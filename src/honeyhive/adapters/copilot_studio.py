"""Convert Microsoft Copilot Studio diagnostic export records to OpenTelemetry spans.

Copilot Studio agents emit telemetry to Azure Application Insights. Customers route that
telemetry through Azure Monitor diagnostic settings, which export records to an Event Hub or
to Blob storage. This module converts those exported records into :class:`ReadableSpan`
objects that can be handed directly to an OTLP exporter and shipped to HoneyHive.

Azure Monitor diagnostic export wire format (confirmed from live records): every record is a
flat object — all Log Analytics columns (``Name``, ``Id``, ``OperationId``, ``UserId``, etc.)
appear at the top level, not nested inside a sub-object. ``Properties`` (capital P) is a dict
of Copilot Studio-specific custom key/value pairs. The type discriminant is ``category`` on
newer exports and ``Type`` on older ones; the adapter accepts both.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Event, ReadableSpan
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.trace import SpanContext, SpanKind, TraceFlags
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.util.types import AttributeValue

_LOG = logging.getLogger(__name__)

_SPAN_TYPES: frozenset[str] = frozenset({"AppEvents", "AppRequests", "AppDependencies"})
# TODO: handle AppExceptions — see HHAI-5791

# Internal Copilot Studio orchestration spans: empty inputs/outputs, no scoreable content.
# Dropped by default; set COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS=1 to retain.
_TOPIC_SPAN_NAMES: frozenset[str] = frozenset(
    {
        "TopicStart",
        "TopicEnd",
        "TopicAction",
        "PowerVirtualAgentRoot",
    }
)

_SCOPE = InstrumentationScope(
    name="honeyhive.adapters.copilot_studio",
    version="0.1.0",
)

_GEN_AI_SYSTEM = "microsoft.copilot_studio"

_TRUTHY: frozenset[str] = frozenset({"1", "true", "yes"})


def copilot_studio_records_to_spans(
    records: list[dict[str, object]],
) -> list[ReadableSpan]:
    """Convert Application Insights diagnostic export records from a Copilot Studio agent to spans.

    Accepts records in the Azure Monitor diagnostic export format — the ``records`` array from
    an Event Hub message already unpacked by the caller. Each record has a flat structure with
    all Log Analytics columns at the top level (``Type`` or ``category``, ``Name``, ``Id``,
    ``OperationId``, etc.).

    Only records with a type of ``AppEvents``, ``AppRequests``, or ``AppDependencies``
    are converted. All other types (``AppExceptions``, ``AppTraces``, etc.) are silently
    skipped — they carry log-signal data, not span data.

    Each valid record is mapped to a single :class:`ReadableSpan`. See the module docstring
    for the full field mapping.

    Records missing a required field (``OperationId``, ``Id``, or ``time``) are skipped with a
    warning.

    Returns an empty list if no records survive filtering and validation.

    Args:
        records: Diagnostic export records, each a JSON object parsed into a dict.

    Returns:
        A list of converted spans, one per valid record. May be empty.
    """
    resource_cache: dict[tuple[str, str], Resource] = {}
    spans: list[ReadableSpan] = []

    for record in records:
        record_type = _get_str(record, "category") or _get_str(record, "Type")
        if record_type not in _SPAN_TYPES:
            _LOG.debug("Skipping record type %r", record_type or "(missing)")
            continue
        name = _get_str(record, "Name")
        if name == "n/a":
            _LOG.debug("Skipping unnamed dependency record")
            continue
        keep_topics = (
            os.environ.get("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "").strip()
            in _TRUTHY
        )
        # Topic/root orchestration spans are noise; drop them unless opted in. Error topics
        # (e.g. "...topic.OnError") are exempt — they may carry error content not otherwise
        # captured, so we never silently discard them.
        is_topic_span = name in _TOPIC_SPAN_NAMES or ".topic." in name
        if not keep_topics and is_topic_span and "error" not in name.lower():
            _LOG.debug(
                "Skipping topic span %r (set COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS=1 to retain)",
                name,
            )
            continue
        try:
            spans.append(_to_readable_span(record, resource_cache))
        except (ValueError, KeyError) as exc:
            _LOG.warning("Skipping malformed record: %s — %.300s", exc, str(record))

    return spans


def _to_readable_span(
    record: dict[str, object],
    resource_cache: dict[tuple[str, str], Resource],
) -> ReadableSpan:
    custom_props = _get_custom_props(record)

    # ── Trace context ──────────────────────────────────────────────────────────
    # Design-mode sessions in the Copilot Studio test canvas don't emit OperationId;
    # fall back to conversationId from Properties, which is stable across the conversation.
    operation_id = _get_str(record, "OperationId") or _get_str(
        custom_props, "conversationId"
    )
    if not operation_id:
        raise ValueError(
            "Missing required field 'OperationId' and no 'conversationId' fallback"
        )
    # AppEvents has no Id column; synthesize a stable span ID from timestamp + event name.
    span_raw_id = (
        _get_str(record, "Id")
        or f"{_get_str(record, 'time')}:{_get_str(record, 'Name')}"
    )
    hh_session_id = str(uuid.uuid5(uuid.NAMESPACE_URL, operation_id))

    trace_id = _to_trace_id(operation_id)
    context = SpanContext(
        trace_id=trace_id,
        span_id=_to_span_id(span_raw_id),
        is_remote=True,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
    )

    parent_context: SpanContext | None = None
    raw_parent = _get_str(record, "ParentId")
    # App Insights sometimes sets ParentId == OperationId on root spans; clear it to avoid
    # making the span its own parent.
    if raw_parent and raw_parent != _get_str(record, "OperationId"):
        parent_context = SpanContext(
            trace_id=trace_id,
            span_id=_to_span_id(raw_parent),
            is_remote=True,
            trace_flags=TraceFlags(TraceFlags.SAMPLED),
        )

    # ── Timestamps ────────────────────────────────────────────────────────────
    start_ns = _iso_to_ns(_require(record, "time"))
    end_ns = start_ns + int(_get_float(record, "DurationMs") * 1_000_000)

    # ── Name and custom properties ────────────────────────────────────────────
    event_name = _get_str(record, "Name") or "Unknown"
    operation = _event_to_operation(event_name)
    # Error status is keyed on the event name only. AppRequests/AppDependencies failure
    # signals (Success == false, ResultCode) are out of scope here — Copilot Studio surfaces
    # turn errors as OnErrorLog AppEvents, and we have no live records of request/dependency
    # failure shapes to map against (see also the AppExceptions follow-up).
    is_error = "error" in event_name.lower()

    # ── Attributes ────────────────────────────────────────────────────────────
    # AppRoleInstance is the actual bot name; AppRoleName is the generic runtime name.
    agent_name = _get_str(record, "AppRoleInstance") or _get_str(record, "AppRoleName")
    raw_attrs: dict[str, AttributeValue] = {
        "gen_ai.system": _GEN_AI_SYSTEM,
        "gen_ai.operation.name": operation,
        "gen_ai.agent.name": agent_name,
        "gen_ai.conversation.id": _get_str(custom_props, "conversationId"),
        # UserId is a top-level column; fromId is the per-message sender in Properties.
        "enduser.id": (
            _get_str(record, "UserId")
            or _get_str(custom_props, "fromId")
            or _get_str(custom_props, "userId")
        ),
        # SessionId is a top-level column, not a Property.
        "session.id": _get_str(record, "SessionId"),
        "messaging.destination": _get_str(custom_props, "channelId"),
        "copilot_studio.topic_name": _normalize_topic_name(
            _get_str(custom_props, "TopicName")
        ),
        "copilot_studio.channel_id": _get_str(custom_props, "channelId"),
        "copilot_studio.design_mode": _get_str(custom_props, "DesignMode"),
        "copilot_studio.user_name": _get_str(custom_props, "fromName"),
        "honeyhive.session_id": hh_session_id,
        "honeyhive.session_auto_create": True,
    }
    if is_error:
        # PascalCase keys confirmed from live records; camelCase as forward-compat fallback.
        raw_attrs["error.type"] = (
            _get_str(custom_props, "ErrorCode")
            or _get_str(custom_props, "errorCode")
            or "unknown"
        )
    # Read at call time so toggling COPILOT_STUDIO_ADAPTER_DEBUG takes effect without restart.
    if os.environ.get("COPILOT_STUDIO_ADAPTER_DEBUG", "").strip() in _TRUTHY:
        raw_attrs["debug.raw_record"] = json.dumps(record, default=str)

    attributes: dict[str, AttributeValue] = {
        k: v for k, v in raw_attrs.items() if v != ""
    }

    # ── Span events (message content) ─────────────────────────────────────────
    events: list[Event] = []
    if text := _get_str(custom_props, "text"):
        if event_name == "BotMessageReceived":
            events.append(
                Event(
                    name="gen_ai.user.message",
                    attributes={"gen_ai.system": _GEN_AI_SYSTEM, "content": text},
                    timestamp=start_ns,
                )
            )
        else:
            events.append(
                Event(
                    name="gen_ai.choice",
                    attributes={
                        "gen_ai.system": _GEN_AI_SYSTEM,
                        "content": text,
                        "finish_reason": "stop",
                        "index": 0,
                    },
                    timestamp=start_ns,
                )
            )

    # ── Resource (deduplicated by agent name + instance) ──────────────────────
    service_name = _get_str(record, "AppRoleName") or "unknown"
    instance_id = _get_str(record, "AppRoleInstance")
    resource_key = (service_name, instance_id)
    if resource_key not in resource_cache:
        resource_cache[resource_key] = Resource(
            {"service.name": service_name, "service.instance.id": instance_id}
        )

    error_message = _get_str(custom_props, "ErrorMessage") or _get_str(
        custom_props, "errorMessage"
    )
    return ReadableSpan(
        name=operation,
        context=context,
        parent=parent_context,
        resource=resource_cache[resource_key],
        attributes=attributes,
        events=events,
        kind=SpanKind.INTERNAL,
        instrumentation_scope=_SCOPE,
        status=Status(
            status_code=StatusCode.ERROR if is_error else StatusCode.OK,
            description=error_message if (is_error and error_message) else None,
        ),
        start_time=start_ns,
        end_time=end_ns,
    )


def _to_trace_id(raw: str) -> int:
    """Map a correlation id to a valid 128-bit OTel trace id (hex passthrough or hashed)."""
    return _to_id(raw, byte_len=16)


def _to_span_id(raw: str) -> int:
    """Map a correlation id to a valid 64-bit OTel span id (hex passthrough or hashed)."""
    return _to_id(raw, byte_len=8)


def _to_id(raw: str, *, byte_len: int) -> int:
    """Return a non-zero ``byte_len``-byte int derived from ``raw``.

    Strips dashes, pipes, and trailing dots before parsing (Application Insights uses
    hierarchical IDs like ``|abc123.1`` that are not valid hex). If the stripped string is
    exactly ``2 * byte_len`` hex chars, it is used directly. Otherwise the value is hashed
    with SHA-256 and the leading ``byte_len`` bytes are used — deterministic across calls so
    parent/child correlation is preserved.  OTel rejects all-zero IDs, so the
    (astronomically unlikely) zero result is bumped to 1.
    """
    stripped = raw.replace("-", "").replace("|", "").rstrip(".")
    stripped = re.sub(r"\.\d+$", "", stripped)
    if re.fullmatch(rf"[0-9a-fA-F]{{{byte_len * 2}}}", stripped):
        value = int(stripped, 16)
    else:
        digest = hashlib.sha256(raw.encode("utf-8")).digest()
        value = int.from_bytes(digest[:byte_len], "big")
    return value or 1


def _iso_to_ns(ts: str) -> int:
    ts = ts.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1_000_000_000)


def _normalize_topic_name(raw: str) -> str:
    """Strip the fully-qualified agent prefix from a Copilot Studio topic name.

    TopicStart records set TopicName to the qualified form (e.g.
    ``cr44e_MyAgent.topic.Greeting``); TopicAction records use the short display
    name (``Greeting``). Normalise both to the short form.
    """
    if not raw:
        return raw
    idx = raw.find(".topic.")
    return raw[idx + len(".topic.") :] if idx != -1 else raw


def _event_to_operation(event_name: str) -> str:
    # Fully-qualified topic events emitted by the Copilot Studio runtime have the form
    # "{agentPrefix}.topic.{TopicName}" (e.g. "cr44e_MyAgent.topic.Greeting"). These are
    # agent-action spans; the topic name is already captured in copilot_studio.topic_name.
    if ".topic." in event_name:
        return "agent_action"
    return {
        "BotMessageReceived": "user_input",
        "BotMessageSend": "agent_output",
        "TopicStart": "agent_action",
        "TopicEnd": "agent_action",
        "TopicAction": "agent_action",
        "PowerVirtualAgentRoot": "agent_action",
        "OnErrorLog": "agent_error",
    }.get(event_name, "agent_action")


def _get_custom_props(record: dict[str, object]) -> dict[str, object]:
    """Return the ``Properties`` custom-dimensions dict from a record.

    The Event Hub diagnostic export emits ``Properties`` as a JSON dict object.
    """
    value = record.get("Properties")
    return value if isinstance(value, dict) else {}


def _require(record: dict[str, object], key: str) -> str:
    """Return ``record[key]`` as a non-empty string or raise ``ValueError``."""
    value = _get_str(record, key)
    if not value:
        raise ValueError(f"Missing required field {key!r}")
    return value


def _get_str(d: dict[str, object], key: str) -> str:
    """Return ``d[key]`` as a string, or ``""`` when missing or not a string."""
    value = d.get(key)
    return value if isinstance(value, str) else ""


def _get_float(d: dict[str, object], key: str) -> float:
    """Return ``d[key]`` coerced to a float, or ``0.0`` when missing or non-numeric."""
    value = d.get(key)
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0

"""HoneyHive OTLP exporter with optimized connection pooling.

This module provides the OTLP exporter for HoneyHive tracers. It's an enhanced
wrapper around the standard OpenTelemetry OTLP exporter that includes:

- Optimized HTTP session with connection pooling for better performance
- Enhanced retry strategies for reliable span delivery
- Session statistics and monitoring capabilities
- Graceful fallback to standard sessions if optimization fails

All span processing should be completed by the HoneyHiveSpanProcessor before
spans reach this exporter, as ReadableSpan objects are immutable.
"""

import json
import math
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

import requests

# Third-party imports
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.trace import StatusCode

# Local imports
from ...utils.logger import safe_log
from .otlp_session import (
    OTLPSessionConfig,
    create_optimized_otlp_session,
    get_default_otlp_config,
    get_session_stats,
)


class OTLPJSONExporter(SpanExporter):
    """OTLP JSON exporter that sends spans in JSON format over HTTP.

    This exporter serializes spans to OTLP JSON format and sends them via HTTP POST
    with Content-Type: application/json. It implements the SpanExporter interface
    and can be used as a drop-in replacement for OTLPSpanExporter when JSON format
    is required.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[requests.Session] = None,
        timeout: Optional[float] = None,
        tracer_instance: Any = None,
    ) -> None:
        """Initialize the OTLP JSON exporter.

        Args:
            endpoint: OTLP endpoint URL
                (e.g., "https://api.dp1.us.honeyhive.ai/opentelemetry/v1/traces")
            headers: Optional HTTP headers to include in requests
            session: Optional requests.Session to use for HTTP requests
            timeout: Optional timeout in seconds for HTTP requests
            tracer_instance: Optional tracer instance for logging context
        """
        self.endpoint = endpoint.rstrip("/")
        # Copy headers to avoid modifying the original dict
        self.headers = dict(headers) if headers else {}
        self.session = session or requests.Session()
        self.timeout = timeout
        self.tracer_instance = tracer_instance
        self._is_shutdown = False

        # Always set Content-Type header for JSON (override any existing value)
        self.headers["Content-Type"] = "application/json"

        safe_log(
            tracer_instance,
            "info",
            "OTLPJSONExporter initialized",
            honeyhive_data={
                "endpoint": self.endpoint,
                "content_type": self.headers.get("Content-Type"),
                "has_session": self.session is not None,
            },
        )

    @classmethod
    def _to_otlp_any_value(cls, value: Any) -> Dict[str, Any]:
        """Convert a Python attribute value to an OTLP AnyValue JSON dict.

        Maps Python types to the corresponding OTLP AnyValue variant so the
        backend deserializes into the proper scalar type (int, float, bool,
        array) instead of coercing everything to a string.

        Note: ``bool`` must be checked before ``int`` because ``bool`` is a
        subclass of ``int`` in Python.
        """
        if isinstance(value, bool):
            return {"boolValue": value}
        if isinstance(value, int):
            # protobuf JSON mapping: int64 must be a JSON string so values above
            # 2^53 survive the server's float64 decode path without precision loss.
            # Matches native opentelemetry-exporter-otlp-proto-http behavior.
            return {"intValue": str(value)}
        if isinstance(value, float):
            # NaN/Inf are not valid JSON — Python's json.dumps emits them as
            # `NaN`/`Infinity` tokens, which Go's encoding/json rejects and
            # would fail the entire export batch. Fall back to stringValue
            # so the batch still lands.
            if not math.isfinite(value):
                return {"stringValue": str(value)}
            return {"doubleValue": value}
        if isinstance(value, str):
            return {"stringValue": value}
        if isinstance(value, (list, tuple)):
            return {
                "arrayValue": {"values": [cls._to_otlp_any_value(v) for v in value]}
            }
        # TODO: serialize JSON to kvlist_value here so it doesnt fall through
        # to stringValue:
        # https://opentelemetry.io/docs/specs/otel/common/attribute-type-mapping/#associative-arrays-with-unique-keys
        return {"stringValue": str(value)}

    @classmethod
    def _to_otlp_key_values(
        cls, attributes: Optional[Mapping[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert a mapping of attributes to an OTLP KeyValue list."""
        if not attributes:
            return []
        return [
            {"key": key, "value": cls._to_otlp_any_value(value)}
            for key, value in attributes.items()
        ]

    def _span_to_otlp_json(self, span: ReadableSpan) -> Dict[str, Any]:
        """Convert a ReadableSpan to OTLP JSON format.

        Args:
            span: ReadableSpan to convert

        Returns:
            Dictionary representing the span in OTLP JSON format
        """
        # Convert trace_id and span_id to hex strings
        trace_id = format(span.context.trace_id, "032x")
        span_id = format(span.context.span_id, "016x")
        parent_span_id = None
        if span.parent and hasattr(span.parent, "span_id") and span.parent.span_id:
            parent_span_id = format(span.parent.span_id, "016x")

        # Preserve native Python types so the backend gets int/float/bool/etc.
        # rather than stringified scalars.
        attributes = self._to_otlp_key_values(span.attributes)

        # Convert events
        events = []
        if span.events:
            for event in span.events:
                event_attrs = self._to_otlp_key_values(event.attributes)
                events.append(
                    {
                        # uint64 - protobuf JSON mapping requires string for uint64
                        "timeUnixNano": str(event.timestamp),
                        "name": event.name,
                        "attributes": event_attrs,
                    }
                )

        # Convert status
        status_code_map = {
            StatusCode.OK: "STATUS_CODE_OK",
            StatusCode.ERROR: "STATUS_CODE_ERROR",
        }
        status = {
            "code": status_code_map.get(span.status.status_code, "STATUS_CODE_UNSET")
        }
        if span.status.description:
            status["message"] = span.status.description

        # Convert kind - use span.kind.name directly (already in correct format)
        span_kind = (
            f"SPAN_KIND_{span.kind.name}"
            if not span.kind.name.startswith("SPAN_KIND_")
            else span.kind.name
        )

        span_json = {
            "traceId": trace_id,
            "spanId": span_id,
            "parentSpanId": parent_span_id,
            "name": span.name,
            "kind": span_kind,
            # uint64 - protobuf JSON mapping requires string for uint64
            "startTimeUnixNano": str(span.start_time),
            "endTimeUnixNano": str(span.end_time),
            "attributes": attributes,
            "events": events,
            "status": status,
        }

        return span_json

    def _spans_to_otlp_json_payload(
        self, spans: Sequence[ReadableSpan]
    ) -> Dict[str, Any]:
        """Convert spans to OTLP JSON payload format.

        Groups spans by their instrumentation scope so the ingestion pipeline
        can correctly identify the instrumentor for each span. Previously all
        spans were placed under a single scope (the first span's), which caused
        misclassification when spans from different instrumentors (e.g.
        pydantic-ai and httpx) were batched together.

        Args:
            spans: Sequence of ReadableSpan objects

        Returns:
            Dictionary in OTLP JSON format ready for HTTP POST
        """
        if not spans:
            return {"resourceSpans": []}

        # Use first span's resource (all spans share the same TracerProvider resource)
        first_span = spans[0]
        resource_attrs: List[Dict[str, Any]] = []
        if first_span.resource and first_span.resource.attributes:
            resource_attrs = self._to_otlp_key_values(first_span.resource.attributes)

        # Group spans by instrumentation scope so each scope's spans are
        # correctly tagged in the OTLP payload. The ingestion pipeline uses
        # the scope name to detect the instrumentor (e.g. "pydantic-ai" →
        # StandardGenAI). Mixing scopes causes misclassification.
        scope_groups: Dict[str, Dict[str, Any]] = {}
        for span in spans:
            scope_name = "unknown"
            scope_version = ""
            if hasattr(span, "instrumentation_scope") and span.instrumentation_scope:
                scope_name = span.instrumentation_scope.name or "unknown"
                scope_version = span.instrumentation_scope.version or ""

            scope_key = f"{scope_name}:{scope_version}"
            if scope_key not in scope_groups:
                scope_info: Dict[str, str] = {"name": scope_name}
                if scope_version:
                    scope_info["version"] = scope_version
                scope_groups[scope_key] = {
                    "scope": scope_info,
                    "spans": [],
                }
            scope_groups[scope_key]["spans"].append(self._span_to_otlp_json(span))

        resource_span = {
            "resource": {"attributes": resource_attrs} if resource_attrs else {},
            "scopeSpans": list(scope_groups.values()),
        }

        return {"resourceSpans": [resource_span]}

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to HoneyHive via OTLP JSON format.

        Args:
            spans: Sequence of ReadableSpan objects to export

        Returns:
            SpanExportResult indicating success or failure
        """
        if self._is_shutdown:
            safe_log(
                self.tracer_instance,
                "debug",
                "JSON exporter already shutdown, skipping export",
            )
            return SpanExportResult.FAILURE

        if not spans:
            return SpanExportResult.SUCCESS

        try:
            # Convert spans to OTLP JSON format
            payload = self._spans_to_otlp_json_payload(spans)
            json_data = json.dumps(payload)

            # Log the JSON payload for debugging
            safe_log(
                self.tracer_instance,
                "debug",
                f"Exporting {len(spans)} spans via OTLP JSON",
                honeyhive_data={
                    "span_count": len(spans),
                    "endpoint": self.endpoint,
                    "payload_size_bytes": len(json_data),
                    "json_payload": json.dumps(
                        payload, indent=2
                    ),  # Pretty-printed for debugging
                },
            )

            # Send HTTP POST request
            response = self.session.post(
                self.endpoint,
                data=json_data,
                headers=self.headers,
                timeout=self.timeout,
            )

            # Check response status
            if response.status_code == 200:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    f"Successfully exported {len(spans)} spans via OTLP JSON",
                    honeyhive_data={
                        "span_count": len(spans),
                        "status_code": response.status_code,
                    },
                )
                return SpanExportResult.SUCCESS

            safe_log(
                self.tracer_instance,
                "error",
                f"OTLP JSON export failed with status {response.status_code}",
                honeyhive_data={
                    "status_code": response.status_code,
                    "response_body": response.text[:500] if response.text else None,
                    "span_count": len(spans),
                },
            )
            return SpanExportResult.FAILURE

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                f"Error in OTLP JSON export: {e}",
                honeyhive_data={
                    "error_type": type(e).__name__,
                    "span_count": len(spans),
                },
            )
            return SpanExportResult.FAILURE

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any buffered spans (no-op for this exporter)."""
        return True

    def shutdown(self) -> None:
        """Shutdown the exporter."""
        if self._is_shutdown:
            return
        self._is_shutdown = True
        if self.session:
            self.session.close()


class HoneyHiveOTLPExporter(SpanExporter):
    """HoneyHive OTLP exporter with optimized connection pooling.

    This exporter is an enhanced wrapper around the standard OpenTelemetry OTLP
    exporter that includes optimized HTTP session with connection pooling for
    better performance and reliability. All span processing should have been
    completed by the HoneyHiveSpanProcessor before spans reach this exporter.

    Features:
    - Optimized HTTP session with connection pooling
    - Enhanced retry strategies for reliable span delivery
    - Session statistics and monitoring capabilities
    - Graceful fallback to standard sessions if optimization fails
    """

    def __init__(
        self,
        tracer_instance: Any = None,
        session_config: Optional[OTLPSessionConfig] = None,
        use_optimized_session: bool = True,
        protocol: str = "http/json",
        **kwargs: Any,
    ) -> None:
        """Initialize the HoneyHive OTLP exporter with optional connection pooling.

        Args:
            tracer_instance: Optional tracer instance for logging context
            session_config: Optional configuration for optimized HTTP session
            use_optimized_session: Whether to use optimized session (default: True)
            protocol: OTLP protocol format
                - "http/json" (default) or "http/protobuf"
            **kwargs: Arguments passed to underlying OTLPSpanExporter or
                OTLPJSONExporter
        """
        self.tracer_instance = tracer_instance
        self.session_config = session_config or get_default_otlp_config(tracer_instance)
        self.use_optimized_session = use_optimized_session
        self.protocol = protocol.lower()
        self._session: Optional[requests.Session] = None
        self._is_shutdown = False
        self._use_json = self.protocol == "http/json"
        self._otlp_exporter: Union[OTLPSpanExporter, OTLPJSONExporter]

        # Create optimized session if requested and not already provided
        if use_optimized_session and "session" not in kwargs:
            try:
                self._session = create_optimized_otlp_session(
                    config=self.session_config, tracer_instance=tracer_instance
                )
                kwargs["session"] = self._session

                safe_log(
                    tracer_instance,
                    "info",
                    "HoneyHiveOTLPExporter initialized with optimized pooling",
                    honeyhive_data=self.session_config.to_dict(),
                )

            except Exception as e:
                safe_log(
                    tracer_instance,
                    "warning",
                    f"Failed to create optimized session, using default: {e}",
                    honeyhive_data={"error_type": type(e).__name__},
                )
                # Continue with default session
        else:
            # Store reference to provided session or None
            self._session = kwargs.get("session")

        # Initialize the appropriate exporter based on protocol
        if self._use_json:
            # Use JSON exporter
            endpoint = kwargs.get("endpoint")
            if not endpoint:
                raise ValueError("endpoint is required for OTLP exporter")
            headers = kwargs.get("headers", {})
            timeout = kwargs.get("timeout")
            self._otlp_exporter = OTLPJSONExporter(
                endpoint=endpoint,
                headers=headers,
                session=self._session,
                timeout=timeout,
                tracer_instance=tracer_instance,
            )
            safe_log(
                tracer_instance,
                "info",
                "HoneyHiveOTLPExporter initialized with JSON format",
                honeyhive_data={"protocol": "http/json", "endpoint": endpoint},
            )
        else:
            # Use standard Protobuf exporter
            self._otlp_exporter = OTLPSpanExporter(**kwargs)

        # Log initialization details
        session_type = (
            "optimized" if self._session and use_optimized_session else "default"
        )
        safe_log(
            tracer_instance,
            "debug",
            f"HoneyHiveOTLPExporter initialized with {session_type} session",
            honeyhive_data={
                "session_type": session_type,
                "use_optimized_session": use_optimized_session,
                "has_custom_session": "session" in kwargs,
            },
        )

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to HoneyHive via OTLP.

        This method exports spans that have already been processed by the
        HoneyHiveSpanProcessor. All attribute processing should have been
        completed before reaching this exporter.

        Args:
            spans: Sequence of ReadableSpan objects to export

        Returns:
            SpanExportResult indicating success or failure
        """
        if self._is_shutdown:
            safe_log(
                self.tracer_instance,
                "debug",
                "Exporter already shutdown, skipping export",
            )
            return SpanExportResult.FAILURE

        safe_log(
            self.tracer_instance,
            "debug",
            f"Exporting {len(spans)} processed spans to HoneyHive",
            honeyhive_data={"span_count": len(spans)},
        )

        try:
            # All span processing completed by HoneyHiveSpanProcessor
            # This exporter simply passes the spans to the underlying OTLP exporter
            return self._otlp_exporter.export(spans)

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                f"Error in OTLP export: {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )
            return SpanExportResult.FAILURE

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any buffered spans."""
        if self._is_shutdown:
            safe_log(
                self.tracer_instance,
                "debug",
                "Exporter already shutdown, skipping force_flush",
            )
            return True
        return self._otlp_exporter.force_flush(timeout_millis)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics from the HTTP session.

        Returns:
            Dictionary containing session and connection pool statistics
        """
        if not self._session:
            return {"error": "No session available", "session_type": "default"}

        try:
            stats = get_session_stats(self._session)
            stats.update(
                {
                    "session_type": (
                        "optimized" if self.use_optimized_session else "custom"
                    ),
                    "session_config": (
                        self.session_config.to_dict() if self.session_config else None
                    ),
                }
            )
            return stats
        except Exception as e:
            return {
                "error": f"Failed to get session stats: {e}",
                "session_type": "optimized" if self.use_optimized_session else "custom",
            }

    def log_session_stats(self) -> None:
        """Log current session statistics for monitoring."""
        stats = self.get_session_stats()
        safe_log(
            self.tracer_instance,
            "debug",
            "OTLP exporter session statistics",
            honeyhive_data={"session_stats": stats},
        )

    def shutdown(self) -> None:
        """Shutdown the exporter and log final statistics."""
        if self._is_shutdown:
            safe_log(
                self.tracer_instance,
                "debug",
                "Exporter already shutdown, ignoring call",
            )
            return

        # Log final session statistics before shutdown
        if self._session and self.tracer_instance:
            try:
                final_stats = self.get_session_stats()
                safe_log(
                    self.tracer_instance,
                    "info",
                    "OTLP exporter final session statistics",
                    honeyhive_data={"final_session_stats": final_stats},
                )
            except Exception as e:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    f"Could not get final session stats: {e}",
                )

        self._is_shutdown = True
        self._otlp_exporter.shutdown()
        safe_log(
            self.tracer_instance, "debug", "HoneyHiveOTLPExporter shutdown completed"
        )

"""Unit tests for honeyhive.adapters.copilot_studio."""

from __future__ import annotations

import hashlib
import json
import uuid

import pytest
from opentelemetry.trace.status import StatusCode

from honeyhive.adapters.copilot_studio import copilot_studio_records_to_spans


def _make_record(
    *,
    type_: str = "AppEvents",
    operation_id: str = "a" * 32,
    id_: str = "b" * 16,
    parent_id: str | None = None,
    time: str = "2024-01-15T10:30:00.0000000Z",
    duration_ms: float = 150.0,
    name: str = "BotMessageSend",
    app_role_name: str = "MyBot",
    app_role_instance: str = "instance-1",
    user_id: str | None = None,
    session_id: str | None = None,
    properties: dict[str, object] | None = None,
) -> dict[str, object]:
    # All Log Analytics columns are at the top level in the Azure Monitor diagnostic
    # export format. "Properties" (capital P) is a JSON dict object in the Event Hub export.
    record: dict[str, object] = {
        "Type": type_,
        "OperationId": operation_id,
        "Id": id_,
        "time": time,
        "DurationMs": duration_ms,
        "Name": name,
        "AppRoleName": app_role_name,
        "AppRoleInstance": app_role_instance,
        "Properties": properties or {},
    }
    if parent_id is not None:
        record["ParentId"] = parent_id
    if user_id is not None:
        record["UserId"] = user_id
    if session_id is not None:
        record["SessionId"] = session_id
    return record


class TestTypeFiltering:
    def test_app_events_passes(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(type_="AppEvents")])
        assert len(spans) == 1

    def test_app_requests_passes(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(type_="AppRequests")])
        assert len(spans) == 1

    def test_app_dependencies_passes(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(type_="AppDependencies")])
        assert len(spans) == 1

    def test_app_exceptions_skipped(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(type_="AppExceptions")])
        assert spans == []

    def test_app_traces_skipped(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(type_="AppTraces")])
        assert spans == []

    def test_missing_type_skipped(self) -> None:
        record = _make_record()
        del record["Type"]
        spans = copilot_studio_records_to_spans([record])
        assert spans == []

    def test_empty_input(self) -> None:
        spans = copilot_studio_records_to_spans([])
        assert spans == []


class TestBasicSpanShape:
    def test_span_name_from_event(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(name="BotMessageSend")])
        assert spans[0].name == "agent_output"

    def test_span_kind_internal(self) -> None:
        from opentelemetry.trace import SpanKind

        spans = copilot_studio_records_to_spans([_make_record()])
        assert spans[0].kind == SpanKind.INTERNAL

    def test_status_ok_by_default(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(name="BotMessageSend")])
        assert spans[0].status.status_code == StatusCode.OK

    def test_status_error_when_name_contains_error(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(name="OnErrorLog")])
        assert spans[0].status.status_code == StatusCode.ERROR

    def test_error_type_attribute_set_on_error_pascalcase(self) -> None:
        # Copilot Studio emits ErrorCode/ErrorMessage in PascalCase.
        spans = copilot_studio_records_to_spans(
            [
                _make_record(
                    name="OnErrorLog",
                    properties={
                        "ErrorCode": "HttpRequestNetworkError",
                        "ErrorMessage": "A network error occurred reaching the target.",
                    },
                )
            ]
        )
        assert spans[0].attributes is not None
        assert spans[0].attributes.get("error.type") == "HttpRequestNetworkError"
        assert (
            spans[0].status.description
            == "A network error occurred reaching the target."
        )

    def test_error_type_attribute_set_on_error_camelcase_fallback(self) -> None:
        spans = copilot_studio_records_to_spans(
            [_make_record(name="OnErrorLog", properties={"errorCode": "BOT_ERR_42"})]
        )
        assert spans[0].attributes is not None
        assert spans[0].attributes.get("error.type") == "BOT_ERR_42"

    def test_error_type_fallback_unknown(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(name="OnErrorLog")])
        assert spans[0].attributes is not None
        assert spans[0].attributes.get("error.type") == "unknown"

    def test_enduser_id_from_top_level_user_id(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(user_id="msteams29:abc")])
        assert spans[0].attributes is not None
        assert spans[0].attributes.get("enduser.id") == "msteams29:abc"

    def test_enduser_id_falls_back_to_from_id(self) -> None:
        spans = copilot_studio_records_to_spans(
            [
                _make_record(
                    name="BotMessageReceived", properties={"fromId": "29:sender"}
                )
            ]
        )
        assert spans[0].attributes is not None
        assert spans[0].attributes.get("enduser.id") == "29:sender"

    def test_session_id_from_top_level_session_id(self) -> None:
        spans = copilot_studio_records_to_spans(
            [_make_record(session_id="sess-hash==")]
        )
        assert spans[0].attributes is not None
        assert spans[0].attributes.get("session.id") == "sess-hash=="

    def test_user_name_from_from_name(self) -> None:
        spans = copilot_studio_records_to_spans(
            [
                _make_record(
                    name="BotMessageReceived", properties={"fromName": "Mike Arndt"}
                )
            ]
        )
        assert spans[0].attributes is not None
        assert spans[0].attributes.get("copilot_studio.user_name") == "Mike Arndt"

    def test_gen_ai_system_attribute(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record()])
        assert spans[0].attributes is not None
        assert spans[0].attributes["gen_ai.system"] == "microsoft.copilot_studio"

    def test_gen_ai_agent_name_uses_instance_over_role(self) -> None:
        # AppRoleInstance is the bot's name; AppRoleName is the generic runtime ("Microsoft Copilot Studio")
        spans = copilot_studio_records_to_spans(
            [
                _make_record(
                    app_role_name="Microsoft Copilot Studio", app_role_instance="My Bot"
                )
            ]
        )
        assert spans[0].attributes is not None
        assert spans[0].attributes["gen_ai.agent.name"] == "My Bot"

    def test_gen_ai_agent_name_falls_back_to_role_when_no_instance(self) -> None:
        record = _make_record(app_role_name="FallbackBot", app_role_instance="")
        spans = copilot_studio_records_to_spans([record])
        assert spans[0].attributes is not None
        assert spans[0].attributes["gen_ai.agent.name"] == "FallbackBot"

    def test_empty_properties_not_included(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(properties={})])
        assert spans[0].attributes is not None
        for val in spans[0].attributes.values():
            assert val != ""

    def test_copilot_properties_mapped(self) -> None:
        spans = copilot_studio_records_to_spans(
            [
                _make_record(
                    properties={
                        "conversationId": "conv-123",
                        "TopicName": "Welcome Topic",
                        "channelId": "msteams",
                        "DesignMode": "False",
                    }
                )
            ]
        )
        attrs = spans[0].attributes
        assert attrs is not None
        assert attrs["gen_ai.conversation.id"] == "conv-123"
        assert attrs["copilot_studio.topic_name"] == "Welcome Topic"
        assert attrs["copilot_studio.channel_id"] == "msteams"
        assert attrs["copilot_studio.design_mode"] == "False"


class TestIdHandling:
    def test_valid_hex_trace_id_passthrough(self) -> None:
        hex_id = "deadbeef" * 4  # 32 hex chars
        spans = copilot_studio_records_to_spans([_make_record(operation_id=hex_id)])
        assert spans[0].context is not None
        assert spans[0].context.trace_id == int(hex_id, 16)

    def test_valid_hex_span_id_passthrough(self) -> None:
        hex_id = "cafebabe" * 2  # 16 hex chars
        spans = copilot_studio_records_to_spans([_make_record(id_=hex_id)])
        assert spans[0].context is not None
        assert spans[0].context.span_id == int(hex_id, 16)

    def test_non_hex_trace_id_derived_deterministically(self) -> None:
        raw = "fCOhCdCnZ9I="  # base64-style, not hex
        spans1 = copilot_studio_records_to_spans([_make_record(operation_id=raw)])
        spans2 = copilot_studio_records_to_spans([_make_record(operation_id=raw)])
        assert spans1[0].context is not None
        assert spans2[0].context is not None
        assert spans1[0].context.trace_id == spans2[0].context.trace_id

    def test_non_hex_span_id_derived_from_sha256(self) -> None:
        raw = "fCOhCdCnZ9I="
        spans = copilot_studio_records_to_spans([_make_record(id_=raw)])
        expected = int.from_bytes(
            hashlib.sha256(raw.encode("utf-8")).digest()[:8], "big"
        )
        assert spans[0].context is not None
        assert spans[0].context.span_id == expected

    def test_parent_child_share_trace_id(self) -> None:
        op_id = "00112233445566778899aabbccddeeff"
        parent_span_id = "aabbccdd11223344"
        child_span_id = "1234567890abcdef"
        records = [
            _make_record(operation_id=op_id, id_=parent_span_id),
            _make_record(
                operation_id=op_id, id_=child_span_id, parent_id=parent_span_id
            ),
        ]
        spans = copilot_studio_records_to_spans(records)
        assert len(spans) == 2
        assert spans[0].context is not None
        assert spans[1].context is not None
        assert spans[0].context.trace_id == spans[1].context.trace_id

    def test_child_parent_id_matches_parent_span_id(self) -> None:
        op_id = "00112233445566778899aabbccddeeff"
        parent_span_id = "aabbccdd11223344"
        records = [
            _make_record(operation_id=op_id, id_=parent_span_id),
            _make_record(
                operation_id=op_id, id_="1234567890abcdef", parent_id=parent_span_id
            ),
        ]
        spans = copilot_studio_records_to_spans(records)
        child = spans[1]
        assert child.parent is not None
        assert child.parent.span_id == int(parent_span_id, 16)

    def test_non_hex_parent_id_derives_to_same_value_as_non_hex_span_id(self) -> None:
        """Non-hex IDs must hash consistently so parent refs resolve."""
        raw_id = "legacyId|abc123"
        records = [
            _make_record(operation_id="a" * 32, id_=raw_id),
            _make_record(operation_id="a" * 32, id_="b" * 16, parent_id=raw_id),
        ]
        spans = copilot_studio_records_to_spans(records)
        parent_span = spans[0]
        child_span = spans[1]
        assert parent_span.context is not None
        assert child_span.parent is not None
        assert child_span.parent.span_id == parent_span.context.span_id

    def test_id_is_never_zero(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(id_="nonhex!!")])
        assert spans[0].context is not None
        assert spans[0].context.span_id != 0

    def test_no_parent_id_produces_root_span(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record()])
        assert spans[0].parent is None

    def test_empty_parent_id_produces_root_span(self) -> None:
        record = _make_record()
        record["ParentId"] = ""
        spans = copilot_studio_records_to_spans([record])
        assert spans[0].parent is None

    def test_parent_id_equal_to_operation_id_produces_root_span(self) -> None:
        # App Insights sets ParentId == OperationId on root spans; clear it to avoid
        # a self-referencing span in OTLP.
        op_id = "a" * 32
        record = _make_record(operation_id=op_id)
        record["ParentId"] = op_id
        spans = copilot_studio_records_to_spans([record])
        assert spans[0].parent is None


class TestTimestamps:
    def test_start_time_from_iso_z(self) -> None:
        from datetime import datetime, timezone

        ts = "2024-01-15T10:30:00.0000000Z"
        spans = copilot_studio_records_to_spans([_make_record(time=ts, duration_ms=0)])
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        expected_ns = int(dt.timestamp() * 1_000_000_000)
        assert spans[0].start_time == expected_ns

    def test_end_time_is_start_plus_duration(self) -> None:
        spans = copilot_studio_records_to_spans(
            [_make_record(time="2024-01-15T10:30:00.000Z", duration_ms=200.0)]
        )
        assert spans[0].end_time is not None
        assert spans[0].start_time is not None
        assert spans[0].end_time - spans[0].start_time == 200_000_000

    def test_duration_ms_string_coerced(self) -> None:
        record = _make_record(duration_ms=0)
        record["DurationMs"] = "250.5"
        spans = copilot_studio_records_to_spans([record])
        assert spans[0].end_time is not None
        assert spans[0].start_time is not None
        assert spans[0].end_time - spans[0].start_time == 250_500_000

    def test_missing_duration_ms_defaults_zero(self) -> None:
        record = _make_record()
        del record["DurationMs"]
        spans = copilot_studio_records_to_spans([record])
        assert spans[0].end_time == spans[0].start_time

    def test_seven_fractional_digits(self) -> None:
        spans = copilot_studio_records_to_spans(
            [_make_record(time="2024-01-15T10:30:00.1234567Z", duration_ms=0)]
        )
        assert spans[0].start_time is not None
        assert spans[0].start_time > 0


class TestSpanEvents:
    def test_bot_message_received_adds_user_event(self) -> None:
        spans = copilot_studio_records_to_spans(
            [_make_record(name="BotMessageReceived", properties={"text": "Hello bot"})]
        )
        events = spans[0].events
        assert len(events) == 1
        assert events[0].name == "gen_ai.user.message"
        assert events[0].attributes is not None
        assert events[0].attributes["content"] == "Hello bot"

    def test_bot_message_send_adds_choice_event(self) -> None:
        # gen_ai.choice → outputs.content in HoneyHive's StandardGenAI normalizer
        spans = copilot_studio_records_to_spans(
            [_make_record(name="BotMessageSend", properties={"text": "Hi there!"})]
        )
        events = spans[0].events
        assert len(events) == 1
        assert events[0].name == "gen_ai.choice"
        assert events[0].attributes is not None
        assert events[0].attributes["content"] == "Hi there!"
        assert events[0].attributes["finish_reason"] == "stop"

    def test_no_text_no_event(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(name="BotMessageSend")])
        assert spans[0].events == ()


class TestEventNameMapping:
    """Verify operation names map correctly to the event names actually emitted by Copilot Studio.

    Event names confirmed from a live test session (June 2025).
    """

    def test_bot_message_received_maps_to_user_input(self) -> None:
        spans = copilot_studio_records_to_spans(
            [_make_record(name="BotMessageReceived")]
        )
        assert spans[0].name == "user_input"

    def test_bot_message_send_maps_to_agent_output(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(name="BotMessageSend")])
        assert spans[0].name == "agent_output"

    def test_topic_start_maps_to_agent_action(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        spans = copilot_studio_records_to_spans([_make_record(name="TopicStart")])
        assert spans[0].name == "agent_action"

    def test_topic_end_maps_to_agent_action(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        spans = copilot_studio_records_to_spans([_make_record(name="TopicEnd")])
        assert spans[0].name == "agent_action"

    def test_topic_action_maps_to_agent_action(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        spans = copilot_studio_records_to_spans([_make_record(name="TopicAction")])
        assert spans[0].name == "agent_action"

    def test_on_error_log_maps_to_agent_error(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(name="OnErrorLog")])
        assert spans[0].name == "agent_error"

    def test_power_virtual_agent_root_maps_to_agent_action(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        spans = copilot_studio_records_to_spans(
            [_make_record(name="PowerVirtualAgentRoot")]
        )
        assert spans[0].name == "agent_action"

    def test_qualified_topic_event_maps_to_agent_action(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        # e.g. "cr44e_HoneyHiveTestAgent.topic.Greeting"
        spans = copilot_studio_records_to_spans(
            [_make_record(name="cr44e_MyAgent.topic.Greeting")]
        )
        assert spans[0].name == "agent_action"

    def test_qualified_on_error_topic_is_error_status(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        # "cr44e_MyAgent.topic.OnError" contains "error" so it should be StatusCode.ERROR
        spans = copilot_studio_records_to_spans(
            [_make_record(name="cr44e_MyAgent.topic.OnError")]
        )
        assert spans[0].status.status_code == StatusCode.ERROR

    def test_unknown_event_name_defaults_to_agent_action(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(name="SomeFutureEvent")])
        assert spans[0].name == "agent_action"


class TestResourceDedup:
    def test_same_role_and_instance_share_resource(self) -> None:
        records = [
            _make_record(app_role_name="Bot", app_role_instance="i1"),
            _make_record(app_role_name="Bot", app_role_instance="i1", id_="c" * 16),
        ]
        spans = copilot_studio_records_to_spans(records)
        assert spans[0].resource is spans[1].resource

    def test_different_instance_different_resource(self) -> None:
        records = [
            _make_record(app_role_name="Bot", app_role_instance="i1"),
            _make_record(app_role_name="Bot", app_role_instance="i2", id_="c" * 16),
        ]
        spans = copilot_studio_records_to_spans(records)
        assert spans[0].resource is not spans[1].resource

    def test_resource_service_name(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record(app_role_name="MyAgent")])
        assert spans[0].resource.attributes["service.name"] == "MyAgent"


class TestPropertiesFormat:
    """Topic-name normalization and span-ID synthesis for the AppEvents schema."""

    def test_qualified_topic_name_is_normalized_to_short_form(self) -> None:
        # TopicStart records emit TopicName as the FQ form; TopicAction uses the short form.
        # Both should resolve to the short name in HoneyHive.
        spans = copilot_studio_records_to_spans(
            [
                _make_record(
                    properties={"TopicName": "cr44e_HoneyHiveTestAgent.topic.Greeting"}
                )
            ]
        )
        assert spans[0].attributes is not None
        assert spans[0].attributes["copilot_studio.topic_name"] == "Greeting"

    def test_short_topic_name_unchanged(self) -> None:
        spans = copilot_studio_records_to_spans(
            [_make_record(properties={"TopicName": "Greeting"})]
        )
        assert spans[0].attributes is not None
        assert spans[0].attributes["copilot_studio.topic_name"] == "Greeting"

    def test_two_app_events_same_time_name_share_span_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        # Deterministic: same time+name → same synthesized span ID
        r1 = _make_record(time="2024-01-15T10:30:00.000Z", name="TopicStart")
        r2 = _make_record(time="2024-01-15T10:30:00.000Z", name="TopicStart")
        del r1["Id"]
        del r2["Id"]
        spans = copilot_studio_records_to_spans([r1, r2])
        assert spans[0].context is not None
        assert spans[1].context is not None
        assert spans[0].context.span_id == spans[1].context.span_id

    def test_different_times_produce_different_span_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        r1 = _make_record(time="2024-01-15T10:30:00.000Z", name="TopicStart")
        r2 = _make_record(time="2024-01-15T10:30:01.000Z", name="TopicStart")
        del r1["Id"]
        del r2["Id"]
        spans = copilot_studio_records_to_spans([r1, r2])
        assert spans[0].context is not None
        assert spans[1].context is not None
        assert spans[0].context.span_id != spans[1].context.span_id


class TestDesignModeFallback:
    """Design-mode test canvas sessions have no OperationId; conversationId is the fallback."""

    def test_missing_operation_id_with_conversation_id_produces_span(self) -> None:
        record = _make_record(properties={"conversationId": "conv-abc-123"})
        record["OperationId"] = ""
        spans = copilot_studio_records_to_spans([record])
        assert len(spans) == 1

    def test_conversation_id_seeds_deterministic_session_id(self) -> None:
        conv_id = "54453b3c-d001-4997-b70e-0c7aa9f0ba29"
        record = _make_record(properties={"conversationId": conv_id})
        record["OperationId"] = ""
        spans = copilot_studio_records_to_spans([record])
        expected_session_id = str(uuid.uuid5(uuid.NAMESPACE_URL, conv_id))
        assert spans[0].attributes is not None
        assert spans[0].attributes["honeyhive.session_id"] == expected_session_id

    def test_two_design_mode_spans_with_same_conversation_share_trace(self) -> None:
        conv_id = "54453b3c-d001-4997-b70e-0c7aa9f0ba29"
        r1 = _make_record(id_="a" * 16, properties={"conversationId": conv_id})
        r2 = _make_record(id_="b" * 16, properties={"conversationId": conv_id})
        r1["OperationId"] = ""
        r2["OperationId"] = ""
        spans = copilot_studio_records_to_spans([r1, r2])
        assert len(spans) == 2
        assert spans[0].context is not None
        assert spans[1].context is not None
        assert spans[0].context.trace_id == spans[1].context.trace_id


class TestTopicFiltering:
    def test_topic_spans_dropped_by_default(self) -> None:
        records = [
            _make_record(name="TopicStart"),
            _make_record(name="TopicEnd"),
            _make_record(name="TopicAction"),
            _make_record(name="PowerVirtualAgentRoot"),
            _make_record(name="BotMessageSend"),
        ]
        spans = copilot_studio_records_to_spans(records)
        assert len(spans) == 1
        assert spans[0].name == "agent_output"

    def test_qualified_topic_name_dropped_by_default(self) -> None:
        spans = copilot_studio_records_to_spans(
            [_make_record(name="cr44e_MyAgent.topic.Greeting")]
        )
        assert spans == []

    def test_error_topic_span_not_dropped_by_default(self) -> None:
        # Error topics may carry error content not otherwise captured, so they are
        # exempt from the default topic drop.
        spans = copilot_studio_records_to_spans(
            [_make_record(name="cr44e_MyAgent.topic.OnError")]
        )
        assert len(spans) == 1
        assert spans[0].status.status_code == StatusCode.ERROR

    def test_topic_spans_retained_when_env_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        records = [
            _make_record(name="TopicStart"),
            _make_record(name="BotMessageSend"),
        ]
        spans = copilot_studio_records_to_spans(records)
        assert len(spans) == 2

    def test_unnamed_dependency_always_dropped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_KEEP_TOPIC_SPANS", "1")
        records = [_make_record(type_="AppDependencies", name="n/a")]
        spans = copilot_studio_records_to_spans(records)
        assert spans == []

    def test_message_spans_never_dropped(self) -> None:
        records = [
            _make_record(name="BotMessageReceived"),
            _make_record(name="BotMessageSend"),
            _make_record(name="OnErrorLog"),
        ]
        spans = copilot_studio_records_to_spans(records)
        assert len(spans) == 3


class TestDebugMode:
    def test_debug_attribute_absent_by_default(self) -> None:
        spans = copilot_studio_records_to_spans([_make_record()])
        assert spans[0].attributes is not None
        assert "debug.raw_record" not in spans[0].attributes

    def test_debug_attribute_present_when_env_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_DEBUG", "1")
        record = _make_record(properties={"conversationId": "conv-debug"})
        spans = copilot_studio_records_to_spans([record])
        assert spans[0].attributes is not None
        raw = spans[0].attributes.get("debug.raw_record")
        assert raw is not None
        parsed = json.loads(str(raw))
        assert parsed["Properties"]["conversationId"] == "conv-debug"

    def test_debug_attribute_is_valid_json(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("COPILOT_STUDIO_ADAPTER_DEBUG", "1")
        spans = copilot_studio_records_to_spans([_make_record()])
        raw = spans[0].attributes.get("debug.raw_record")  # type: ignore[union-attr]
        assert raw is not None
        parsed = json.loads(str(raw))
        assert "Type" in parsed


class TestMalformedRecords:
    def test_missing_operation_id_and_no_conversation_id_skipped(self) -> None:
        record = _make_record()  # Properties is {} (no conversationId)
        record["OperationId"] = ""
        spans = copilot_studio_records_to_spans([record])
        assert spans == []

    def test_missing_id_synthesizes_from_time_and_name(self) -> None:
        # AppEvents has no Id column; the adapter synthesizes a span ID from time+Name.
        record = _make_record()
        del record["Id"]
        spans = copilot_studio_records_to_spans([record])
        assert len(spans) == 1
        assert spans[0].context is not None
        assert spans[0].context.span_id != 0

    def test_missing_time_skipped(self) -> None:
        record = _make_record()
        del record["time"]
        spans = copilot_studio_records_to_spans([record])
        assert spans == []

    def test_malformed_mixed_with_good_yields_good(self) -> None:
        bad = _make_record()
        bad["OperationId"] = ""  # no conversationId fallback either
        good = _make_record(id_="d" * 16)
        spans = copilot_studio_records_to_spans([bad, good])
        assert len(spans) == 1

    def test_all_malformed_returns_empty_list(self) -> None:
        bad1 = _make_record()
        bad1["OperationId"] = ""
        bad2 = _make_record()
        del bad2["time"]
        spans = copilot_studio_records_to_spans([bad1, bad2])
        assert spans == []

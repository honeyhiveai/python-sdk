"""Integration tests for HoneyHive attributes backend verification.

These tests validate that HoneyHive attributes are correctly processed by the
real backend by creating spans and verifying them via backend APIs.

NO MOCKING - All tests use real HoneyHive APIs, real OpenTelemetry components,
and real backend verification.
"""

import time
from typing import Any

import pytest

from honeyhive.api.client import HoneyHive
from honeyhive.models import EventType
from honeyhive.tracer import HoneyHiveTracer, enrich_span, trace
from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_span_export,
    verify_tracer_span,
)


@pytest.mark.integration
@pytest.mark.real_api
class TestHoneyHiveAttributesBackendIntegration:
    """Integration tests for HoneyHive attributes with real backend verification.
    # MIGRATION STATUS: 6 patterns ready for NEW validation_helpers migration


        These tests create real spans and verify that all required HoneyHive
        attributes are properly processed and stored in the backend.
    """

    @pytest.mark.tracer
    def test_decorator_event_type_backend_verification(
        self,
        integration_tracer: Any,
        integration_client: Any,
        real_project: Any,
        real_source: Any,
    ) -> None:
        """Test that @trace decorator EventType enum is properly converted in backend.

        Creates a span using @trace decorator with EventType.tool and verifies
        that backend receives "tool" string, not enum object.
        """
        event_name, test_id = generate_test_id("decorator_event_type_test")

        @trace(  # type: ignore[misc]
            tracer=integration_tracer,
            event_type=EventType.tool.value,
            event_name=event_name,
        )
        def test_function() -> Any:
            with enrich_span(
                inputs={"test_input": "event_type_verification"},
                metadata={
                    "test": {
                        "type": "event_type_backend_verification",
                        "unique_id": test_id,
                    },
                    "expected": {"event_type": "tool"},
                },
                tracer=integration_tracer,
            ):
                time.sleep(0.1)  # Ensure measurable duration
                return {"result": "success", "test_id": test_id}

        # Execute the function
        result = test_function()
        assert result["test_id"] == test_id

        # Force flush to ensure spans are exported immediately
        integration_tracer.force_flush()

        # Create span and verify backend export using centralized helper
        verification_span_name = f"verification_{test_id}"
        event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name=verification_span_name,
            unique_identifier=test_id,
            span_attributes={
                "test.verification_type": "decorator_event_type_test",
                "test.backend_verification": "true",
                "honeyhive.source": real_source,
            },
        )

        # Verify EventType.tool was properly processed (backend returns enum)
        assert (
            event.event_type == EventType.tool
        ), f"Expected EventType.tool, got '{event.event_type}'"
        assert event.session_id == integration_tracer.session_id
        # Note: project_id is the backend ID, not the project name
        assert event.project_id is not None, "Project ID should be set"
        assert event.source == real_source

    @pytest.mark.tracer
    def test_direct_span_event_type_inference(
        self, integration_tracer: Any, integration_client: Any
    ) -> None:
        """Test that direct span creation with instrumentor-style name infers
        correct event_type.

        Creates a span with 'openai.chat.completions.create' name and verifies
        that backend receives 'model' event_type through inference.
        """
        _, test_id = generate_test_id("openai_chat_completions_create")
        # Use unique event name to avoid conflicts with other test runs
        event_name = f"openai.chat.completions.create.{test_id}"

        # Create span directly with instrumentor-style name
        with integration_tracer.start_span(event_name) as span:
            # Add typical LLM attributes
            span.set_attribute("llm.request.model", "gpt-3.5-turbo")
            span.set_attribute("llm.request.temperature", 0.7)

            time.sleep(0.1)

            span.set_attribute("llm.response.model", "gpt-3.5-turbo")

            # Use enrich_span as function (preferred approach) to add metadata
            enrich_span(
                metadata={
                    "test": {
                        "type": "event_type_inference_verification",
                        "unique_id": test_id,
                    },
                    "expected": {"event_type": "model"},
                },
                tracer=integration_tracer,
            )

        # Force flush to ensure spans are exported immediately
        integration_tracer.force_flush()

        # Use retry-based backend verification instead of manual sleep
        event = verify_span_export(
            client=integration_client,
            project=integration_tracer.project,
            unique_identifier=test_id,
            expected_event_name=event_name,
            debug_content=True,
        )

        # Verify span name was inferred as 'model' event_type
        assert (
            event.event_type == EventType.model
        ), f"Expected EventType.model, got '{event.event_type}'"
        assert event.event_name == event_name

    @pytest.mark.tracer
    @pytest.mark.models
    def test_all_event_types_backend_conversion(
        self, integration_tracer: Any, integration_client: Any
    ) -> None:
        """Test that all EventType enum values are properly converted in backend.

        Creates spans with each EventType (model, tool, chain, session) and
        verifies that backend receives correct string values.
        """
        _, test_id = generate_test_id("all_event_types_backend_conversion")
        event_types_to_test = [
            EventType.model,
            EventType.tool,
            EventType.chain,
            EventType.session,
        ]

        created_events = []

        for event_type in event_types_to_test:
            event_name = f"{event_type.value}_test_{test_id}"

            def create_test_function(et: Any, en: Any) -> Any:
                @trace(  # type: ignore[misc]
                    tracer=integration_tracer,
                    event_type=et,
                    event_name=en,
                )
                def test_event_type() -> Any:
                    with enrich_span(
                        inputs={"event_type_test": et.value},
                        metadata={
                            "test": {
                                "type": "all_event_types_verification",
                                "unique_id": f"{test_id}_{et.value}",
                                "event_type": et.value,
                            }
                        },
                        tracer=integration_tracer,
                    ):
                        time.sleep(0.05)
                        return {"event_type": et.value}

                return test_event_type

            test_func = create_test_function(event_type, event_name)
            _ = test_func()  # Execute test but don't need result
            created_events.append(
                (event_name, event_type.value, f"{test_id}_{event_type.value}")
            )

        # Force flush to ensure spans are exported immediately
        integration_tracer.force_flush()

        # Verify all events in backend using retry-based verification
        for event_name, expected_type, unique_id in created_events:
            event = verify_span_export(
                client=integration_client,
                project=integration_tracer.project,
                unique_identifier=unique_id,
                expected_event_name=event_name,
                debug_content=True,
            )

            # Verify the event type matches expected (backend returns enum)
            expected_enum = getattr(EventType, expected_type)
            assert event.event_type == expected_enum, (
                f"Event {event_name}: expected type {expected_enum}, "
                f"got {event.event_type}"
            )

    @pytest.mark.tracer
    @pytest.mark.multi_instance
    def test_multi_instance_attribute_isolation(
        self,
        real_api_credentials: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Test that multiple tracer instances have isolated attributes.

        Creates two independent tracers with different sources and verifies
        that their attributes don't interfere with each other.
        """
        _, test_id = generate_test_id("multi_tracer_attribute_isolation")

        # Create two independent tracers with different sources
        tracer1 = HoneyHiveTracer(
            api_key=real_api_credentials["api_key"],
            project=real_api_credentials["project"],
            source="multi_instance_test_1",
            session_name=f"test-tracer1-{test_id}",
            test_mode=False,
            disable_batch=True,
        )

        tracer2 = HoneyHiveTracer(
            api_key=real_api_credentials["api_key"],
            project=real_api_credentials["project"],
            source="multi_instance_test_2",
            session_name=f"test-tracer2-{test_id}",
            test_mode=False,
            disable_batch=True,
        )

        client = HoneyHive(api_key=real_api_credentials["api_key"], test_mode=False)

        # Create events with each tracer
        @trace(  # type: ignore[misc]
            tracer=tracer1,
            event_type=EventType.tool.value,
            event_name=f"tracer1_event_{test_id}",
        )
        def tracer1_function() -> Any:
            with enrich_span(
                inputs={"tracer": "tracer1"},
                metadata={"test": {"tracer": "1", "unique_id": f"{test_id}_tracer1"}},
                tracer=tracer1,
            ):
                time.sleep(0.05)
                return {"tracer": "1"}

        @trace(  # type: ignore[misc]
            tracer=tracer2,
            event_type=EventType.chain.value,
            event_name=f"tracer2_event_{test_id}",
        )
        def tracer2_function() -> Any:
            with enrich_span(
                inputs={"tracer": "tracer2"},
                metadata={"test": {"tracer": "2", "unique_id": f"{test_id}_tracer2"}},
                tracer=tracer2,
            ):
                time.sleep(0.05)
                return {"tracer": "2"}

        # Execute both functions
        _ = tracer1_function()  # Execute but don't need result
        _ = tracer2_function()  # Execute but don't need result

        # Force flush both tracers to ensure spans are exported immediately
        tracer1.force_flush()
        tracer2.force_flush()

        # Use retry-based backend verification for both events
        event1 = verify_span_export(
            client=client,
            project=tracer1.project,
            unique_identifier=f"{test_id}_tracer1",
            expected_event_name=f"tracer1_event_{test_id}",
            debug_content=True,
        )

        event2 = verify_span_export(
            client=client,
            project=tracer2.project,
            unique_identifier=f"{test_id}_tracer2",
            expected_event_name=f"tracer2_event_{test_id}",
            debug_content=True,
        )

        # Verify proper isolation
        assert event1.session_id == tracer1.session_id
        assert event2.session_id == tracer2.session_id
        assert event1.session_id != event2.session_id

        assert event1.source == "multi_instance_test_1"
        assert event2.source == "multi_instance_test_2"

        assert event1.event_type == EventType.tool
        assert event2.event_type == EventType.chain

        # Cleanup tracers
        try:
            tracer1.force_flush()
            tracer1.shutdown()
            tracer2.force_flush()
            tracer2.shutdown()
        except Exception:
            pass  # Silent cleanup

    @pytest.mark.tracer
    @pytest.mark.end_to_end
    def test_comprehensive_attribute_backend_verification(
        self, integration_tracer: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Comprehensive test that backend receives all required HoneyHive attributes.

        This is the master integration test that creates a span with rich data
        and verifies comprehensive backend attribute storage.
        """
        event_name, test_id = generate_test_id("comprehensive_test")

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation +
        # backend verification
        event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name=event_name,
            unique_identifier=test_id,
            span_attributes={
                "test.type": "comprehensive_backend_verification",
                "test.unique_id": test_id,
                "test.comprehensive": True,
                "honeyhive.inputs.prompt": "Test prompt for comprehensive verification",
                "honeyhive.inputs.model": "test-model",
                "honeyhive.inputs.temperature": 0.7,
                "honeyhive.outputs.response": "Test response",
                "honeyhive.outputs.tokens_used": 100,
                "honeyhive.outputs.cost": 0.001,
                "honeyhive.metadata.model.provider": "test",
                "honeyhive.metadata.model.version": "1.0",
                "honeyhive.config.max_tokens": 150,
                "honeyhive.config.retry_count": 3,
            },
        )

        # Verify all core HoneyHive attributes
        required_attributes = {
            "session_id": integration_tracer.session_id,
            "project_id": None,  # Backend returns project ID, not name -
            # just check it exists
            "source": integration_tracer.source,
            "event_name": event_name,
        }

        for attr_name, expected_value in required_attributes.items():
            actual_value = getattr(event, attr_name)
            if attr_name == "project_id":
                # Just check that project_id exists and is not None
                assert (
                    actual_value is not None
                ), f"Attribute {attr_name} should not be None"
            else:
                assert actual_value == expected_value, (
                    f"Attribute {attr_name}: expected {expected_value}, "
                    f"got {actual_value}"
                )

        # Verify rich data was captured in metadata (new standardized pattern)
        assert event.metadata is not None and len(event.metadata) > 0

        # Verify specific data integrity in metadata (new standardized pattern)
        assert (
            event.metadata.get("honeyhive.inputs.prompt")
            == "Test prompt for comprehensive verification"
        )
        assert event.metadata.get("honeyhive.outputs.response") == "Test response"
        assert event.metadata.get("honeyhive.metadata.model.provider") == "test"
        assert event.metadata.get("honeyhive.config.max_tokens") == 150
        assert event.metadata.get("test.unique_id") == test_id
        assert event.metadata.get("test.comprehensive") is True
        assert event.metadata.get("test.type") == "comprehensive_backend_verification"

        # Verify duration was captured (should be > 0 for 0.15s sleep)
        assert event.duration is not None and event.duration > 0

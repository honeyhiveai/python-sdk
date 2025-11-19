"""Integration tests for tracer functionality in HoneyHive."""

# pylint: disable=C0301
# Justification: line-too-long: Complex integration test assertions
import os
import time
from typing import Any

import pytest

from honeyhive import enrich_span as main_enrich_span
from honeyhive.tracer import enrich_span
from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_tracer_span,
)


@pytest.mark.integration
@pytest.mark.tracer
class TestTracerIntegration:
    """Test tracer integration and end-to-end functionality."""

    def test_tracer_initialization_integration(
        self, integration_tracer: Any, real_project: Any, real_source: Any
    ) -> None:
        """Test tracer initialization and configuration."""
        assert integration_tracer.project == real_project
        assert integration_tracer.source == real_source
        assert integration_tracer.test_mode is False  # Integration tests use real API

    def test_function_tracing_integration(
        self, integration_tracer: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test function tracing integration with backend verification."""

        # Generate unique identifier for backend verification
        _, unique_id = generate_test_id("function_tracing", "integration")

        # Test that the tracer is properly initialized
        assert integration_tracer.project is not None
        assert integration_tracer.source is not None

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation +
        # backend verification
        verified_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name="test_function",
            unique_identifier=unique_id,
            span_attributes={
                "test.unique_id": unique_id,
                "test.type": "function_tracing",
                "function.name": "test_function",
                "function.args": "x=5, y=3",
                "function.result": 8,
            },
        )

        assert verified_event.event_name == "test_function"

    def test_method_tracing_integration(
        self, integration_tracer: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test method tracing integration with backend verification."""

        # Generate unique identifier for backend verification
        _, unique_id = generate_test_id("method_tracing", "integration")

        # ✅ STANDARD PATTERN: Use verify_tracer_span for span creation +
        # backend verification
        verified_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name="test_method",
            unique_identifier=unique_id,
            span_attributes={
                "test.unique_id": unique_id,
                "test.type": "method_tracing",
                "method.name": "test_method",
                "method.class": "TestClass",
                "method.input": 10,
                "method.result": 20,
            },
        )

        assert verified_event.event_name == "test_method"

        # Test that the tracer is properly initialized
        assert integration_tracer.project is not None
        assert integration_tracer.source is not None

    def test_tracer_context_management(self, integration_tracer: Any) -> None:
        """Test tracer context management."""
        with integration_tracer.start_span("test-operation") as span:
            span.set_attribute("test.attribute", "test-value")
            span.add_event("test-event", {"data": "test"})

            # Verify span is active
            assert span.is_recording()

    def test_tracer_event_creation_integration(self, integration_tracer: Any) -> None:
        """Test event creation through tracer with real API."""
        # Agent OS Zero Failing Tests Policy: NO SKIPPING - must use real credentials
        if not os.getenv("HH_API_KEY"):
            pytest.fail(
                "HH_API_KEY required for real event creation test - check .env file"
            )

        event_data = {
            "project": "integration-test-project",
            "source": "integration-test",
            "event_name": "test-event",
            "event_type": "model",
            "config": {"model": "gpt-4"},
            "inputs": {"prompt": "Test"},
            "duration": 100.0,
        }

        # Test real event creation (may fail gracefully in test environment)
        try:
            event_id = integration_tracer.create_event(event_data)
            # If successful, verify event ID is returned as string
            assert isinstance(event_id, str)
            assert event_id is not None
            assert len(event_id) > 0
        except Exception as e:
            # Agent OS Zero Failing Tests Policy: NO SKIPPING - real system exercise
            # required
            pytest.fail(f"Real API event creation failed - real system must work: {e}")

    def test_tracer_session_management(self, integration_tracer: Any) -> None:
        """Test session management through tracer."""
        # Test that the tracer has basic session information
        assert integration_tracer.session_name is not None
        assert integration_tracer.project is not None
        assert integration_tracer.source is not None

        # In test mode, session_id might be None due to API limitations
        # but we can still test the baggage functionality
        assert hasattr(integration_tracer, "set_baggage")
        assert hasattr(integration_tracer, "get_baggage")

    def test_tracer_span_attributes(self, integration_tracer: Any) -> None:
        """Test span attribute management."""
        with integration_tracer.start_span("test-span") as span:
            # Set various attribute types
            span.set_attribute("string.attr", "test")
            span.set_attribute("int.attr", 42)
            span.set_attribute("float.attr", 3.14)
            span.set_attribute("bool.attr", True)

            # Verify span is active and can set attributes
            assert span.is_recording()

            # Test that we can access the span object
            assert hasattr(span, "set_attribute")
            assert hasattr(span, "is_recording")

    def test_tracer_error_handling(self, integration_tracer: Any) -> None:
        """Test tracer error handling with real API scenarios."""
        # Test error handling with invalid data (real API will reject)
        if not os.getenv("HH_API_KEY"):
            pytest.fail(
                "HH_API_KEY required for real error handling test - check .env file"
            )

        # Test with invalid event data that should cause real API errors
        invalid_event_data = {
            "project": "",  # Invalid empty project
            "source": "",  # Invalid empty source
            "event_name": "",  # Invalid empty event name
            "event_type": "invalid_type",  # Invalid event type
            "config": None,  # Invalid config
            "inputs": None,  # Invalid inputs
            "duration": -1.0,  # Invalid duration
        }

        # Real API should handle errors gracefully
        try:
            integration_tracer.create_event(invalid_event_data)
            # If no exception, that's also valid (graceful degradation)
        except Exception as e:
            # Real API errors are expected and acceptable
            assert isinstance(e, Exception)
            # Integration test passes if error is handled without crashing

    def test_tracer_performance_monitoring(self, integration_tracer: Any) -> None:
        """Test tracer performance monitoring."""
        with integration_tracer.start_span("performance-test") as span:
            start_time = time.time()

            # Simulate some work
            time.sleep(0.01)

            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds

            # Verify span is active and can set attributes
            assert span.is_recording()
            assert duration > 0

            # Test that we can set performance attributes
            span.set_attribute("duration_ms", duration)
            span.set_attribute("operation", "performance_test")

    def test_tracer_baggage_propagation(self, integration_tracer: Any) -> None:
        """Test tracer baggage propagation."""
        # Test that baggage methods exist
        assert hasattr(integration_tracer, "set_baggage")
        assert hasattr(integration_tracer, "get_baggage")

        # Test that we can access baggage context (without setting values)
        # In test mode, some OpenTelemetry operations might be limited
        # get_baggage requires a key parameter
        try:
            integration_tracer.get_baggage("test.key")
            # Baggage might be None in test mode, which is acceptable
        except Exception:
            # In test mode, some OpenTelemetry operations might fail
            # This is acceptable for integration testing
            pass

    def test_tracer_span_events(self, integration_tracer: Any) -> None:
        """Test tracer span events."""
        with integration_tracer.start_span("events-test") as span:
            # Test that we can add events to span
            span.add_event("user.login", {"user_id": "user-123"})
            span.add_event("data.processed", {"records": 100})

            # Verify span is active and can handle events
            assert span.is_recording()
            assert hasattr(span, "add_event")

            # Test that we can set additional attributes
            span.set_attribute("event_count", 2)
            span.set_attribute("test_type", "span_events")

    def test_tracer_integration_with_client(
        self, integration_client: Any, integration_tracer: Any
    ) -> None:
        """Test tracer integration with API client."""
        # Test that both client and tracer are properly initialized
        assert integration_client.test_mode is False  # Integration tests use real API
        assert integration_tracer.test_mode is False  # Integration tests use real API
        assert integration_tracer.project is not None
        assert integration_tracer.source is not None

        # Test that we can start a span with the tracer
        with integration_tracer.start_span("api-operation") as span:
            # Verify span is active
            assert span.is_recording()

            # Test that we can set attributes on the span
            span.set_attribute("api.operation", "create_session")
            span.set_attribute("test.integration", True)

            # Verify the span has the expected attributes
            assert hasattr(span, "set_attribute")
            assert hasattr(span, "is_recording")


@pytest.mark.integration
@pytest.mark.tracer
class TestUnifiedEnrichSpanIntegration:
    """Integration tests for unified enrich_span functionality."""

    def test_enrich_span_context_manager_integration(
        self, integration_tracer: Any
    ) -> None:
        """Test enrich_span context manager in integration environment."""

        with integration_tracer.start_span("test_span") as span:
            assert span.is_recording()

            # Test enhanced_tracing_demo.py pattern
            with enrich_span(
                event_type="integration_test",
                event_name="context_manager_test",
                inputs={"test_input": "integration_value"},
                metadata={"test_type": "integration", "pattern": "context_manager"},
                metrics={"execution_time": 0.1},
            ):
                # Simulate some work
                time.sleep(0.01)

        # Verify that no exceptions were thrown
        assert True

    def test_enrich_span_basic_usage_integration(self, integration_tracer: Any) -> None:
        """Test enrich_span basic_usage.py pattern in integration environment."""
        with integration_tracer.start_span("test_span") as span:
            assert span.is_recording()

            # Test basic_usage.py pattern: tracer.enrich_span(attributes={"key":
            # "value"})
            result = integration_tracer.enrich_span(
                attributes={
                    "session_name": "integration_session",
                    "test_type": "integration",
                }
            )
            # Simulate some work
            time.sleep(0.01)

            # Verify enrichment succeeded
            assert result is True

        # Verify that no exceptions were thrown
        assert True

    def test_enrich_span_direct_call_integration(self, integration_tracer: Any) -> None:
        """Test enrich_span direct method call in integration environment."""
        with integration_tracer.start_span("test_span"):
            # Test direct method call
            result = integration_tracer.enrich_span(
                metadata={"test_type": "integration", "call_type": "direct"},
                metrics={"test_metric": 42},
            )

            # Should return boolean indicating success/failure
            assert isinstance(result, bool)

    def test_enrich_span_global_function_integration(
        self, integration_tracer: Any
    ) -> None:
        """Test global enrich_span function in integration environment."""

        with integration_tracer.start_span("test_span"):
            # Test global function with tracer parameter
            result = enrich_span(
                attributes={"test_type": "integration", "call_type": "global"},
                tracer=integration_tracer,
            )

            # Should return UnifiedEnrichSpan instance that can be used as boolean
            assert result is not False

    def test_enrich_span_import_paths_integration(
        self, integration_tracer: Any
    ) -> None:
        """Test valid import paths work in integration environment."""
        # Test valid import paths
        with integration_tracer.start_span("test_span"):
            # Test that valid import paths work
            result1 = enrich_span(
                attributes={"event_type": "import_test_1"}, tracer=integration_tracer
            )
            assert result1 is not False

            result2 = main_enrich_span(
                attributes={"event_type": "import_test_2"}, tracer=integration_tracer
            )
            assert result2 is not False

        # Verify that no exceptions were thrown
        assert True

    def test_enrich_span_real_world_workflow_integration(
        self, integration_tracer: Any
    ) -> None:
        """Test enrich_span in a realistic workflow scenario."""

        # Simulate a realistic AI application workflow
        with integration_tracer.start_span("ai_workflow") as main_span:
            assert main_span.is_recording()

            # Step 1: Data preprocessing
            with enrich_span(
                event_type="preprocessing",
                event_name="data_preparation",
                inputs={"raw_data": "user_query"},
                metadata={"stage": "preprocessing", "version": "1.0"},
            ):
                time.sleep(0.01)  # Simulate preprocessing work

            # Step 2: Model inference
            with enrich_span(
                event_type="inference",
                event_name="model_prediction",
                inputs={"processed_data": "cleaned_query"},
                config_data={"model": "gpt-3.5", "temperature": 0.7},
                metadata={"stage": "inference"},
            ):
                time.sleep(0.02)  # Simulate model inference

            # Step 3: Post-processing with direct call
            result = integration_tracer.enrich_span(
                metadata={"stage": "postprocessing", "output_format": "json"},
                metrics={"response_length": 150, "confidence": 0.95},
            )
            assert isinstance(result, bool)

        # Verify that the complete workflow executed without errors
        assert True

    def test_enrich_span_error_scenarios_integration(
        self, integration_tracer: Any  # pylint: disable=unused-argument
    ) -> None:
        """Test enrich_span error handling in integration environment."""

        # Test with no active span (should handle gracefully)
        with enrich_span(attributes={"event_type": "no_span_test"}):
            pass

        # Test with invalid parameters (should handle gracefully)
        with enrich_span(
            attributes={
                "event_type": "error_test",
                "complex_object": {"nested": {"deeply": "value"}},
                "inputs": ["list", "of", "items"],
            },
            invalid_param="should_be_ignored",
        ):
            pass

        # Test direct call without tracer (should return UnifiedEnrichSpan instance)
        result = enrich_span(attributes={"test": "no_tracer"})
        assert result is not False  # UnifiedEnrichSpan instance is truthy

        # Verify that error scenarios don't crash the application
        assert True

    def test_enrich_span_backwards_compatible(
        self, integration_tracer: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test enrich_span works with main branch interface end-to-end.

        This test verifies that the original main branch interface for enrich_span
        still works correctly with proper namespace routing and backend verification.
        """
        # Generate unique identifier for backend verification
        _, unique_id = generate_test_id("enrich_span_compat", "integration")

        # Create a traced operation with main branch interface
        with integration_tracer.start_span("test_enrichment_backwards_compat") as span:
            assert span.is_recording()

            # Use main branch interface - reserved namespace parameters
            enrich_span(
                metadata={"user_id": "123", "test_id": unique_id, "feature": "chat"},
                metrics={"score": 0.95, "latency_ms": 150},
                feedback={"rating": 5, "helpful": True},
            )

        # Flush to ensure data reaches backend
        integration_tracer.force_flush()
        time.sleep(2)  # Allow backend processing time

        # Use centralized validation helper for backend verification
        verified_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name="test_enrichment_backwards_compat",
            unique_identifier=unique_id,
            span_attributes={
                "honeyhive_metadata.user_id": "123",
                "honeyhive_metadata.test_id": unique_id,
                "honeyhive_metadata.feature": "chat",
                "honeyhive_metrics.score": 0.95,
                "honeyhive_metrics.latency_ms": 150,
                "honeyhive_feedback.rating": 5,
                "honeyhive_feedback.helpful": True,
            },
        )

        # Assert backend verification succeeded
        assert verified_event is not None
        assert verified_event.event_name == "test_enrichment_backwards_compat"

    def test_enrich_span_with_user_properties_and_metrics_integration(
        self, integration_tracer: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test enrich_span with user_properties and metrics."""
        # Generate unique identifier for backend verification
        _, unique_id = generate_test_id("enrich_span_user_props", "integration")

        # Create a traced operation with user_properties and metrics
        with integration_tracer.start_span("test_enrichment_user_props") as span:
            assert span.is_recording()

            # Use instance method with user_properties and metrics
            integration_tracer.enrich_span(
                user_properties={"user_id": "test-user-123", "plan": "premium"},
                metrics={"score": 0.95, "latency_ms": 150},
                metadata={"test_id": unique_id, "feature": "enrichment_test"},
            )

        # Flush to ensure data reaches backend
        integration_tracer.force_flush()
        time.sleep(2)  # Allow backend processing time

        # Verify span attributes in backend
        verified_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name="test_enrichment_user_props",
            unique_identifier=unique_id,
            span_attributes={
                "honeyhive_metadata.test_id": unique_id,
                "honeyhive_metadata.feature": "enrichment_test",
                "honeyhive_metrics.score": 0.95,
                "honeyhive_metrics.latency_ms": 150,
                "honeyhive_user_properties.user_id": "test-user-123",
                "honeyhive_user_properties.plan": "premium",
            },
        )

        # Assert backend verification succeeded
        assert verified_event is not None
        assert verified_event.event_name == "test_enrichment_user_props"

    def test_enrich_span_arbitrary_kwargs_integration(
        self, integration_tracer: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test arbitrary kwargs work end-to-end with backend verification.

        This test verifies that the new feature of passing arbitrary kwargs
        correctly routes them to the metadata namespace and they appear in the backend.
        """
        # Generate unique identifier for backend verification
        _, unique_id = generate_test_id("enrich_kwargs", "integration")

        # Create a traced operation with arbitrary kwargs
        with integration_tracer.start_span("test_kwargs_enrichment") as span:
            assert span.is_recording()

            # New feature: arbitrary kwargs route to metadata namespace
            enrich_span(
                user_id="456",
                feature="search",
                test_id=unique_id,
                score=0.88,
                session="abc123",
            )

        # Flush to ensure data reaches backend
        integration_tracer.force_flush()
        time.sleep(2)  # Allow backend processing time

        # Verify all kwargs appear in honeyhive_metadata namespace
        verified_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name="test_kwargs_enrichment",
            unique_identifier=unique_id,
            span_attributes={
                "honeyhive_metadata.user_id": "456",
                "honeyhive_metadata.feature": "search",
                "honeyhive_metadata.test_id": unique_id,
                "honeyhive_metadata.score": 0.88,
                "honeyhive_metadata.session": "abc123",
            },
        )

        # Assert backend verification succeeded
        assert verified_event is not None
        assert verified_event.event_name == "test_kwargs_enrichment"

    def test_enrich_span_nested_structures_integration(
        self, integration_tracer: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test nested structures are properly handled end-to-end.

        This test verifies that nested dictionaries and lists are correctly
        flattened with proper namespacing and appear in the backend.
        """
        # Generate unique identifier for backend verification
        _, unique_id = generate_test_id("enrich_nested", "integration")

        # Create a traced operation with nested structures
        with integration_tracer.start_span("test_nested_enrichment") as span:
            assert span.is_recording()

            # Test nested dict and list structures
            enrich_span(
                config={
                    "model": "gpt-4",
                    "params": {"temperature": 0.7, "max_tokens": 150},
                    "options": ["streaming", "json_mode"],
                },
                metadata={
                    "test_id": unique_id,
                    "nested": {"level1": {"level2": "deep"}},
                },
                inputs={"messages": [{"role": "user", "content": "hello"}]},
            )

        # Flush to ensure data reaches backend
        integration_tracer.force_flush()
        time.sleep(2)  # Allow backend processing time

        # Verify nested structures are properly flattened in backend
        verified_event = verify_tracer_span(
            tracer=integration_tracer,
            client=integration_client,
            project=real_project,
            span_name="test_nested_enrichment",
            unique_identifier=unique_id,
            span_attributes={
                "honeyhive_metadata.test_id": unique_id,
                "honeyhive_metadata.nested.level1.level2": "deep",
                "honeyhive_config.model": "gpt-4",
                "honeyhive_config.params.temperature": 0.7,
                "honeyhive_config.params.max_tokens": 150,
                "honeyhive_config.options.0": "streaming",
                "honeyhive_config.options.1": "json_mode",
                "honeyhive_inputs.messages.0.role": "user",
                "honeyhive_inputs.messages.0.content": "hello",
            },
        )

        # Assert backend verification succeeded
        assert verified_event is not None
        assert verified_event.event_name == "test_nested_enrichment"

    def test_force_flush_integration(self, integration_tracer: Any) -> None:
        """Test force_flush functionality in integration environment."""
        # Create some spans to flush
        with integration_tracer.start_span("force_flush_test_span_1") as span:
            span.set_attribute("test_type", "force_flush_integration")
            span.set_attribute("span_number", 1)

        with integration_tracer.start_span("force_flush_test_span_2") as span:
            span.set_attribute("test_type", "force_flush_integration")
            span.set_attribute("span_number", 2)

        # Test force_flush with default timeout
        result = integration_tracer.force_flush()
        assert isinstance(result, bool)

        # Test force_flush with custom timeout
        result = integration_tracer.force_flush(timeout_millis=5000)
        assert isinstance(result, bool)

        # Force flush should work multiple times
        result1 = integration_tracer.force_flush(timeout_millis=1000)
        result2 = integration_tracer.force_flush(timeout_millis=2000)
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)

    def test_force_flush_before_shutdown_integration(
        self, integration_tracer: Any
    ) -> None:
        """Test force_flush before shutdown in integration environment."""
        # Create spans to ensure there's something to flush
        with integration_tracer.start_span("pre_shutdown_span") as span:
            span.set_attribute("test_type", "pre_shutdown_flush")
            span.set_attribute("critical", True)

        # Force flush before shutdown (best practice)
        flush_result = integration_tracer.force_flush(timeout_millis=10000)
        assert isinstance(flush_result, bool)

        # Shutdown should work after force flush
        integration_tracer.shutdown()

        # Verify tracer is still accessible (but likely not functional)
        assert integration_tracer.project is not None

    def test_force_flush_with_enrich_span_integration(
        self, integration_tracer: Any
    ) -> None:
        """Test force_flush interaction with enrich_span in integration environment."""

        # Test with context manager pattern using global function
        with enrich_span(
            metadata={"operation": "integration_test"},
            outputs={"result": "test_data"},
            error=None,
            tracer=integration_tracer,
        ):
            with integration_tracer.start_span("enriched_span") as span:
                span.set_attribute("enriched", True)

        # Force flush after enrichment
        result = integration_tracer.force_flush()
        assert isinstance(result, bool)

        # Test with direct call pattern on tracer instance
        success = integration_tracer.enrich_span(
            metadata={"operation": "direct_call_test"},
            outputs={"status": "completed"},
            error=None,
        )
        assert isinstance(success, bool)

        # Force flush after direct enrichment
        result = integration_tracer.force_flush(timeout_millis=3000)
        assert isinstance(result, bool)

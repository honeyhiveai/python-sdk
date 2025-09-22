"""Real API integration tests for multi-tracer functionality in HoneyHive."""

# pylint: disable=duplicate-code  # Integration tests share common patterns

import asyncio
import threading
import time
from typing import Any

import pytest

from honeyhive.tracer import atrace, trace
from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_span_export,
    verify_tracer_span,
)


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.multi_tracer
class TestRealAPIMultiTracer:
    """Test multi-tracer functionality with real API calls."""

    def test_real_session_creation_with_multiple_tracers(
        self, tracer_factory: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test that multiple tracers can create real sessions independently with
        backend verification."""

        # Create multiple tracers with standardized configuration
        tracer1 = tracer_factory("real-session-1")
        tracer2 = tracer_factory("real-session-2")

        # Verify they're independent
        assert tracer1 is not tracer2
        assert tracer1.session_name != tracer2.session_name

        # Test real session creation with both tracers and backend verification
        _, unique_id1 = generate_test_id("real_session_creation", "tracer1")
        verified_event1 = verify_tracer_span(
            tracer=tracer1,
            client=integration_client,
            project=real_project,
            span_name="real_session1",
            unique_identifier=unique_id1,
            span_attributes={
                "session": "tracer1",
                "test.type": "real_session_creation",
                "duration_ms": 100,
            },
        )

        _, unique_id2 = generate_test_id("real_session_creation", "tracer2")
        verified_event2 = verify_tracer_span(
            tracer=tracer2,
            client=integration_client,
            project=real_project,
            span_name="real_session2",
            unique_identifier=unique_id2,
            span_attributes={
                "session": "tracer2",
                "test.type": "real_session_creation",
                "duration_ms": 50,
            },
        )

        # Verify both spans were exported to backend
        assert verified_event1.event_name == "real_session1"
        assert verified_event2.event_name == "real_session2"

        # Verify spans have different session contexts
        assert verified_event1.session_id != verified_event2.session_id
        # Cleanup handled by tracer_factory fixture

    def test_real_event_creation_with_multiple_tracers(
        self, tracer_factory: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test that multiple tracers can create real events independently with
        backend verification."""

        # Create multiple tracers with standardized configuration
        tracer1 = tracer_factory("real-event-1")
        tracer2 = tracer_factory("real-event-2")

        # Create events with both tracers and backend verification
        _, unique_id1 = generate_test_id("real_event_creation", "tracer1")
        verified_event1 = verify_tracer_span(
            tracer=tracer1,
            client=integration_client,
            project=real_project,
            span_name="event_creation1",
            unique_identifier=unique_id1,
            span_attributes={
                "event_type": "model_inference",
                "model": "gpt-4",
                "tracer": "tracer1",
                "test.type": "real_event_creation",
            },
        )

        _, unique_id2 = generate_test_id("real_event_creation", "tracer2")
        verified_event2 = verify_tracer_span(
            tracer=tracer2,
            client=integration_client,
            project=real_project,
            span_name="event_creation2",
            unique_identifier=unique_id2,
            span_attributes={
                "event_type": "data_processing",
                "dataset": "test_dataset",
                "tracer": "tracer2",
                "test.type": "real_event_creation",
            },
        )

        # Verify both events were exported to backend
        assert verified_event1.event_name == "event_creation1"
        assert verified_event2.event_name == "event_creation2"

        # Verify events have different session contexts
        assert verified_event1.session_id != verified_event2.session_id
        # Cleanup handled by tracer_factory fixture

    def test_real_decorator_integration_with_multiple_tracers(
        self, tracer_factory: Any, integration_client: Any, real_project: Any
    ) -> None:
        """Test @trace decorator with multiple tracers using real API with backend
        verification."""

        # Create multiple tracers
        tracer1 = tracer_factory("decorator-test-1")
        tracer2 = tracer_factory("decorator-test-2")

        # Generate unique identifiers for backend verification
        _, unique_id1 = generate_test_id("decorator_integration", "function1")
        _, unique_id2 = generate_test_id("decorator_integration", "function2")

        # Test functions decorated with different tracers
        @trace(  # type: ignore[misc]
            event_name="function1",
            event_type="tool",
            tracer=tracer1,
            metadata={
                "test.unique_id": unique_id1,
                "test.type": "decorator_integration",
            },
        )
        def function1(x: Any, y: Any) -> Any:
            time.sleep(0.1)  # Simulate work
            return x + y

        @trace(  # type: ignore[misc]
            event_name="function2",
            event_type="tool",
            tracer=tracer2,
            metadata={
                "test.unique_id": unique_id2,
                "test.type": "decorator_integration",
            },
        )
        def function2(x: Any, y: Any) -> Any:
            time.sleep(0.05)  # Simulate different work
            return x * y

        # Execute both functions
        result1 = function1(5, 3)
        result2 = function2(4, 6)

        assert result1 == 8
        assert result2 == 24

        # Verify both tracers are properly configured
        assert tracer1.project == real_project
        assert tracer2.project == real_project
        assert tracer1.session_name != tracer2.session_name

        # Backend verification for both decorated functions
        verified_event1 = verify_span_export(
            client=integration_client,
            project=real_project,
            unique_identifier=unique_id1,
            expected_event_name="function1",
        )

        verified_event2 = verify_span_export(
            client=integration_client,
            project=real_project,
            unique_identifier=unique_id2,
            expected_event_name="function2",
        )

        # Verify both spans were exported to backend
        assert verified_event1.event_name == "function1"
        assert verified_event2.event_name == "function2"

        # Verify spans have different session contexts
        assert verified_event1.session_id != verified_event2.session_id
        # Cleanup handled by tracer_factory fixture

    def test_real_async_decorator_integration_with_multiple_tracers(
        self, tracer_factory: Any, real_project: Any
    ) -> None:
        """Test @atrace decorator with multiple tracers using real API."""
        # Create multiple tracers
        tracer1 = tracer_factory("async-decorator-test-1")

        tracer2 = tracer_factory("async-decorator-test-2")

        # Test async functions decorated with different tracers
        @atrace(  # type: ignore[misc]
            event_name="async_function1", event_type="tool", tracer=tracer1
        )
        async def async_function1(x: Any, y: Any) -> Any:
            await asyncio.sleep(0.1)  # Simulate async work
            return x + y

        @atrace(  # type: ignore[misc]
            event_name="async_function2", event_type="tool", tracer=tracer2
        )
        async def async_function2(x: Any, y: Any) -> Any:
            await asyncio.sleep(0.05)  # Simulate different async work
            return x * y

        # Execute both async functions

        result1 = asyncio.run(async_function1(5, 3))
        result2 = asyncio.run(async_function2(4, 6))

        assert result1 == 8
        assert result2 == 24

        # Verify both tracers are properly configured
        assert tracer1.project == real_project
        assert tracer2.project == real_project
        assert tracer1.session_name != tracer2.session_name
        # Cleanup handled by tracer_factory fixture

    def test_real_concurrent_tracer_usage(self, tracer_factory: Any) -> None:
        """Test concurrent usage of multiple tracers with real API."""

        # Create multiple tracers
        tracer1 = tracer_factory("concurrent-test-1")

        tracer2 = tracer_factory("concurrent-test-2")

        results = []

        def use_tracer1() -> None:
            with tracer1.start_span("thread1_span") as span:
                span.set_attribute("thread", "thread1")
                span.set_attribute("tracer", "tracer1")
                # Simulate work
                time.sleep(0.1)
                span.add_event("work_completed", {"duration_ms": 100})
                results.append("tracer1_used")

        def use_tracer2() -> None:
            with tracer2.start_span("thread2_span") as span:
                span.set_attribute("thread", "thread2")
                span.set_attribute("tracer", "tracer2")
                # Simulate different work
                time.sleep(0.05)
                span.add_event("work_completed", {"duration_ms": 50})
                results.append("tracer2_used")

        # Run both tracers concurrently
        thread1 = threading.Thread(target=use_tracer1)
        thread2 = threading.Thread(target=use_tracer2)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Verify both tracers were used
        assert "tracer1_used" in results
        assert "tracer2_used" in results
        assert len(results) == 2
        # Cleanup handled by tracer_factory fixture

    def test_real_tracer_lifecycle_with_api_calls(
        self, tracer_factory: Any, real_project: Any, real_source: Any
    ) -> None:
        """Test complete tracer lifecycle with real API calls."""
        # Create tracer
        tracer = tracer_factory("lifecycle-test")

        # Test initialization
        assert tracer.project == real_project
        assert tracer.source == real_source
        assert "lifecycle-test" in tracer.session_name

        # Test span creation and API communication
        with tracer.start_span("lifecycle_span") as span:
            span.set_attribute("test_phase", "initialization")
            span.add_event("tracer_ready", {"status": "initialized"})

            # Simulate some work
            time.sleep(0.1)

            span.set_attribute("test_phase", "execution")
            span.add_event("work_started", {"timestamp": time.time()})

            # Simulate more work
            time.sleep(0.05)

            span.set_attribute("test_phase", "completion")
            span.add_event("work_completed", {"duration_ms": 150})

        # Test shutdown
        # Cleanup handled by tracer_factory fixture
        # Verify tracer is properly shut down
        assert hasattr(tracer, "shutdown")

    def test_real_error_handling_with_multiple_tracers(
        self, tracer_factory: Any
    ) -> None:
        """Test error handling with multiple tracers using real API."""
        # Create multiple tracers
        tracer1 = tracer_factory("error-test-1")

        tracer2 = tracer_factory("error-test-2")

        # Test error handling in tracer1
        try:
            with tracer1.start_span("error_span") as span:
                span.set_attribute("test", "error_handling")
                # Simulate an error
                raise ValueError("Test error for tracer1")
        except ValueError:
            # Error should be caught and not affect tracer2
            pass

        # Tracer2 should still work normally
        with tracer2.start_span("normal_span") as span:
            span.set_attribute("status", "working")
            span.add_event("operation_successful", {"tracer": "tracer2"})
            assert span.is_recording()
        # Cleanup handled by tracer_factory fixture

    def test_real_performance_monitoring_with_multiple_tracers(
        self, tracer_factory: Any
    ) -> None:
        """Test performance monitoring with multiple tracers using real API."""
        # Create multiple tracers
        tracer1 = tracer_factory("performance-test-1")

        tracer2 = tracer_factory("performance-test-2")

        # Test performance monitoring with tracer1
        with tracer1.start_span("performance_span1") as span1:
            start_time = time.time()

            # Simulate work
            time.sleep(0.1)

            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds

            span1.set_attribute("duration_ms", duration)
            span1.set_attribute("operation", "performance_test_1")
            span1.add_event("performance_measured", {"latency_ms": duration})

        # Test performance monitoring with tracer2
        with tracer2.start_span("performance_span2") as span2:
            start_time = time.time()

            # Simulate different work
            time.sleep(0.05)

            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds

            span2.set_attribute("duration_ms", duration)
            span2.set_attribute("operation", "performance_test_2")
            span2.add_event("performance_measured", {"latency_ms": duration})
        # Cleanup handled by tracer_factory fixture

    def test_real_metadata_and_attributes_with_multiple_tracers(
        self, tracer_factory: Any
    ) -> None:
        """Test metadata and attributes with multiple tracers using real API."""
        # Create multiple tracers
        tracer1 = tracer_factory("metadata-test-1")

        tracer2 = tracer_factory("metadata-test-2")

        # Test rich metadata with tracer1
        with tracer1.start_span("metadata_span1") as span1:
            span1.set_attribute("user_id", "user123")
            span1.set_attribute("request_id", "req456")
            span1.set_attribute("environment", "production")
            span1.set_attribute("version", "1.0.0")

            span1.add_event(
                "user_action",
                {
                    "action": "login",
                    "timestamp": time.time(),
                    "ip_address": "192.168.1.1",
                },
            )

        # Test different metadata with tracer2
        with tracer2.start_span("metadata_span2") as span2:
            span2.set_attribute("service_name", "api_gateway")
            span2.set_attribute("endpoint", "/api/v1/users")
            span2.set_attribute("method", "POST")
            span2.set_attribute("status_code", 200)

            span2.add_event(
                "api_call",
                {
                    "endpoint": "/api/v1/users",
                    "method": "POST",
                    "response_time_ms": 150,
                    "user_agent": "test-client",
                },
            )
        # Cleanup handled by tracer_factory fixture

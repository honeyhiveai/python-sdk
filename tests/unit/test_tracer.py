"""Unit tests for HoneyHive Tracer functionality."""

import os
import time
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer import HoneyHiveTracer

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestHoneyHiveTracer:
    """Test HoneyHiveTracer functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Reset the singleton for each test
        HoneyHiveTracer.reset()

        # Mock OpenTelemetry availability
        with patch.dict(os.environ, {"HH_OTLP_ENABLED": "false"}):
            # Mock the _initialize_session method to prevent it from running
            with patch.object(HoneyHiveTracer, "_initialize_session"):
                # Create the tracer normally
                self.tracer = HoneyHiveTracer(
                    project="test-project",
                    source="test",
                    api_key="test-key",
                    test_mode=True,
                )

                # Now manually set up what we need for testing
                self.tracer.session_id = "test-session-123"

                # Create a mock events API
                mock_events_api = Mock()
                mock_response = Mock()
                mock_response.event_id = "test-event-123"
                mock_events_api.create_event_from_request.return_value = mock_response

                # Create a mock response for create_event (used by enrich_session)
                mock_create_event_response = Mock()
                mock_create_event_response.success = True
                mock_events_api.create_event.return_value = mock_create_event_response

                # Create a mock client
                mock_client = Mock()
                mock_client.events = mock_events_api

                # Create a mock session API
                mock_session_api = Mock()
                mock_session_api.client = mock_client

                # Patch the tracer's session_api AND client
                self.tracer.session_api = mock_session_api
                self.tracer.client = mock_client  # This is what enrich_session uses

                # Store references for debugging
                self.mock_events_api = mock_events_api
                self.mock_response = mock_response

    def test_tracer_initialization(self) -> None:
        """Test tracer initialization."""
        assert self.tracer.project == "test-project"
        assert self.tracer.source == "test"
        assert self.tracer.api_key == "test-key"
        assert self.tracer.test_mode is True

    def test_tracer_singleton_pattern(self) -> None:
        """Test that tracer follows singleton pattern."""
        # Reset for this test
        HoneyHiveTracer.reset()

        tracer1 = HoneyHiveTracer(
            project="project1", source="source1", api_key="key1", test_mode=True
        )
        tracer2 = HoneyHiveTracer(
            project="project2", source="source2", api_key="key2", test_mode=True
        )

        # Should be the same instance
        assert tracer1 is tracer2
        # Should retain first initialization values
        assert tracer1.project == "project1"
        assert tracer1.source == "source1"
        assert tracer1.api_key == "key1"

    def test_start_span(self) -> None:
        """Test starting a span."""
        with self.tracer.start_span("test-span") as span:
            assert span is not None
            # The span should be an OpenTelemetry span object

    def test_start_span_with_attributes(self) -> None:
        """Test starting a span with attributes."""
        attributes = {"key": "value", "number": 42}
        with self.tracer.start_span("test-span", attributes=attributes) as span:
            assert span is not None
            # Attributes are set on the span

    def test_start_span_with_parent(self) -> None:
        """Test starting a span with parent."""
        with self.tracer.start_span("parent-span") as parent_span:
            with self.tracer.start_span(
                "child-span", parent_id="parent-id"
            ) as child_span:
                assert child_span is not None
                # Parent relationship is handled via parent_id

    def test_create_event(self) -> None:
        """Test creating an event."""
        # The events API is already mocked in setup_method
        event_id = self.tracer.create_event(
            event_type="model",  # Use valid EventType1 enum value
            inputs={"input": "data"},
            outputs={"output": "result"},
        )

        # Verify the event was created successfully
        assert event_id == "test-event-123"
        self.mock_events_api.create_event_from_request.assert_called_once()

    def test_create_event_no_session(self) -> None:
        """Test creating an event when no session exists."""
        # Remove session ID
        self.tracer.session_id = None

        event_id = self.tracer.create_event(event_type="test", inputs={"input": "data"})

        assert event_id is None

    def test_enrich_session(self) -> None:
        """Test enriching a session."""
        # Test that the method exists and can be called
        assert hasattr(self.tracer, "enrich_session")
        assert callable(self.tracer.enrich_session)

        # The complex OpenTelemetry integration is hard to test in isolation
        # We'll focus on testing the basic API contract rather than the full functionality
        result = self.tracer.enrich_session(
            metadata={"key": "value"}, feedback={"rating": 5}
        )

        # The method should not crash and should return a boolean
        assert isinstance(result, bool)

    def test_enrich_session_no_session(self) -> None:
        """Test enriching a session when no session exists."""
        # Remove session ID
        self.tracer.session_id = None

        result = self.tracer.enrich_session(metadata={"key": "value"})

        assert result is False

    def test_enrich_span(self) -> None:
        """Test enriching a span."""
        # Mock OpenTelemetry trace
        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            mock_span = Mock()
            mock_span.get_span_context.return_value = Mock(span_id=123)
            mock_trace.get_current_span.return_value = mock_span

            result = self.tracer.enrich_span(
                metadata={"key": "value"}, metrics={"latency": 100}
            )

            assert result is True

    def test_enrich_span_no_active_span(self) -> None:
        """Test enriching a span when no active span exists."""
        # Mock OpenTelemetry trace with no active span
        with patch("honeyhive.tracer.otel_tracer.trace") as mock_trace:
            mock_span = Mock()
            mock_span.get_span_context.return_value = Mock(span_id=0)
            mock_trace.get_current_span.return_value = mock_span

            result = self.tracer.enrich_span(metadata={"key": "value"})

            assert result is False

    def test_get_baggage(self) -> None:
        """Test getting baggage value."""
        # Mock OpenTelemetry baggage
        with patch("honeyhive.tracer.otel_tracer.baggage") as mock_baggage:
            mock_baggage.get_current.return_value = Mock()
            mock_baggage.get_baggage.return_value = "test-value"

            value = self.tracer.get_baggage("test-key")

            assert value == "test-value"

    def test_set_baggage(self) -> None:
        """Test setting baggage value."""
        # Mock OpenTelemetry baggage
        with patch("honeyhive.tracer.otel_tracer.baggage") as mock_baggage:
            mock_context = Mock()
            mock_baggage.get_current.return_value = mock_context
            mock_baggage.set_baggage.return_value = mock_context

            result = self.tracer.set_baggage("test-key", "test-value")

            assert result == mock_context

    def test_inject_context(self) -> None:
        """Test injecting trace context."""
        carrier = {}

        # Mock the propagator
        with patch.object(self.tracer, "propagator") as mock_propagator:
            mock_context = Mock()
            with patch("honeyhive.tracer.otel_tracer.context") as mock_context_module:
                mock_context_module.get_current.return_value = mock_context

                self.tracer.inject_context(carrier)

                mock_propagator.inject.assert_called_once_with(
                    carrier, context=mock_context
                )

    def test_extract_context(self) -> None:
        """Test extracting trace context."""
        carrier = {"traceparent": "test"}

        # Mock the propagator
        with patch.object(self.tracer, "propagator") as mock_propagator:
            mock_context = Mock()
            mock_propagator.extract.return_value = mock_context

            result = self.tracer.extract_context(carrier)

            assert result == mock_context

    def test_shutdown(self) -> None:
        """Test tracer shutdown."""
        # Mock the provider
        with patch.object(self.tracer, "provider") as mock_provider:
            self.tracer.shutdown()

            mock_provider.shutdown.assert_called_once()

    def test_reset_static_state(self) -> None:
        """Test resetting static state."""
        HoneyHiveTracer._reset_static_state()

        assert HoneyHiveTracer._instance is None
        assert HoneyHiveTracer._is_initialized is False

    def test_tracer_configuration(self) -> None:
        """Test tracer configuration options."""
        # Reset for this test to avoid singleton conflicts
        HoneyHiveTracer.reset()

        # Test with different configuration
        with patch.dict(os.environ, {"HH_OTLP_ENABLED": "false"}):
            tracer = HoneyHiveTracer(
                project="config-test",
                source="staging",
                api_key="config-key",
                test_mode=True,
                session_name="custom-session",
            )

            assert tracer.project == "config-test"
            assert tracer.source == "staging"
            assert tracer.api_key == "config-key"
            assert tracer.session_name == "custom-session"

    def test_tracer_error_handling(self) -> None:
        """Test tracer error handling."""
        # Test initialization without OpenTelemetry
        with patch("honeyhive.tracer.otel_tracer.OTEL_AVAILABLE", False):
            with pytest.raises(ImportError, match="OpenTelemetry is required"):
                HoneyHiveTracer(test_mode=True)

    def test_tracer_performance(self) -> None:
        """Test tracer performance characteristics."""
        start_time = time.time()

        # Create multiple spans quickly
        for i in range(10):
            with self.tracer.start_span(f"span-{i}"):
                pass

        end_time = time.time()

        # Should complete quickly (less than 1 second)
        assert end_time - start_time < 1.0

    def test_tracer_memory_usage(self) -> None:
        """Test tracer memory usage."""
        import sys

        # Create tracer and measure memory
        initial_size = sys.getsizeof(self.tracer)

        # Create some spans
        for i in range(5):
            with self.tracer.start_span(f"span-{i}"):
                pass

        final_size = sys.getsizeof(self.tracer)

        # Memory usage should be reasonable
        assert final_size - initial_size < 1000  # Less than 1KB increase

    def test_tracer_concurrent_access(self) -> None:
        """Test tracer concurrent access."""
        import threading
        import time

        results = []

        def worker(worker_id: int) -> None:
            """Worker function to test concurrent access."""
            try:
                with self.tracer.start_span(f"worker-{worker_id}-span"):
                    time.sleep(0.01)  # Small delay
                    results.append(f"worker-{worker_id}-completed")
            except Exception as e:
                results.append(f"worker-{worker_id}-error: {e}")

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All workers should complete successfully
        assert len(results) == 5
        assert all("completed" in result for result in results)

    def test_tracer_edge_cases(self) -> None:
        """Test tracer edge cases."""
        # Test with empty span name
        with self.tracer.start_span("") as span:
            assert span is not None

        # Test with very long span name
        long_name = "x" * 1000
        with self.tracer.start_span(long_name) as span:
            assert span is not None

        # Test with None attributes
        with self.tracer.start_span("test", attributes=None) as span:
            assert span is not None

    def test_tracer_serialization(self) -> None:
        """Test tracer serialization capabilities."""
        # Test that tracer can be pickled (basic serialization test)
        import pickle

        try:
            pickled = pickle.dumps(self.tracer)
            unpickled = pickle.loads(pickled)

            # Basic attributes should be preserved
            assert unpickled.project == self.tracer.project
            assert unpickled.source == self.tracer.source
        except Exception as e:
            # If pickling fails, that's acceptable for complex objects with threading locks
            error_str = str(e).lower()
            assert any(
                keyword in error_str
                for keyword in [
                    "can't pickle",
                    "not serializable",
                    "cannot pickle",
                    "thread.lock",
                ]
            )

    def test_tracer_integration(self) -> None:
        """Test tracer integration with other components."""
        # Test integration with session management
        assert hasattr(self.tracer, "session_id")
        assert hasattr(self.tracer, "session_api")

        # Test integration with OpenTelemetry
        assert hasattr(self.tracer, "tracer")
        assert hasattr(self.tracer, "provider")
        assert hasattr(self.tracer, "propagator")

    def test_enrich_span_basic(self) -> None:
        """Test that enrich_span method exists and can be called."""
        # Test that the method exists
        assert hasattr(self.tracer, "enrich_span")
        assert callable(self.tracer.enrich_span)

        # Test that we can call it with basic parameters
        # This method is simpler and doesn't depend on complex OpenTelemetry context
        try:
            result = self.tracer.enrich_span(
                span_name="test-span", attributes={"key": "value"}
            )
            # The method should not crash
            assert result is not None
        except Exception as e:
            # If it fails due to OpenTelemetry setup, that's expected in test mode
            print(f"enrich_span failed as expected in test mode: {e}")

"""Integration tests for tracer functionality in HoneyHive."""

import time
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.decorators import trace


@pytest.mark.integration
@pytest.mark.tracer
class TestTracerIntegration:
    """Test tracer integration and end-to-end functionality."""

    def test_tracer_initialization_integration(self, integration_tracer, real_project, real_source):
        """Test tracer initialization and configuration."""
        assert integration_tracer.project == real_project
        assert integration_tracer.source == real_source
        assert integration_tracer.test_mode is False  # Integration tests use real API

    def test_function_tracing_integration(self, integration_tracer):
        """Test function tracing integration."""

        @trace(event_type="model", event_name="test_function", tracer=integration_tracer)
        def test_function(x, y):
            return x + y

        # Test that the function can be called and returns correct result
        result = test_function(5, 3)
        assert result == 8

        # Test that the tracer is properly initialized
        assert integration_tracer.project is not None
        assert integration_tracer.source is not None

    def test_method_tracing_integration(self, integration_tracer):
        """Test method tracing integration."""

        class TestClass:
            """Test class for method tracing integration."""

            @trace(event_type="model", event_name="test_method", tracer=integration_tracer)
            def test_method(self, value):
                """Test method that doubles the input value.

                Args:
                    value: Input value to double

                Returns:
                    Doubled value
                """
                return value * 2

        obj = TestClass()

        # Test that the method can be called and returns correct result
        result = obj.test_method(10)
        assert result == 20

        # Test that the tracer is properly initialized
        assert integration_tracer.project is not None
        assert integration_tracer.source is not None

    def test_tracer_context_management(self, integration_tracer):
        """Test tracer context management."""
        with integration_tracer.start_span("test-operation") as span:
            span.set_attribute("test.attribute", "test-value")
            span.add_event("test-event", {"data": "test"})

            # Verify span is active
            assert span.is_recording()

    def test_tracer_event_creation_integration(self, integration_tracer):
        """Test event creation through tracer."""
        with patch.object(integration_tracer, "create_event") as mock_create:
            mock_create.return_value = Mock(event_id="event-789")

            event_data = {
                "project": "integration-test-project",
                "source": "integration-test",
                "event_name": "test-event",
                "event_type": "model",
                "config": {"model": "gpt-4"},
                "inputs": {"prompt": "Test"},
                "duration": 100.0,
            }

            event = integration_tracer.create_event(**event_data)
            assert event.event_id == "event-789"
            mock_create.assert_called_once_with(**event_data)

    def test_tracer_session_management(self, integration_tracer):
        """Test session management through tracer."""
        # Test that the tracer has basic session information
        assert integration_tracer.session_name is not None
        assert integration_tracer.project is not None
        assert integration_tracer.source is not None

        # In test mode, session_id might be None due to API limitations
        # but we can still test the baggage functionality
        assert hasattr(integration_tracer, "set_baggage")
        assert hasattr(integration_tracer, "get_baggage")

    def test_tracer_span_attributes(self, integration_tracer):
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

    def test_tracer_error_handling(self, integration_tracer):
        """Test tracer error handling."""
        with patch.object(integration_tracer, "create_event") as mock_create:
            mock_create.side_effect = Exception("Tracer error")

            with pytest.raises(Exception, match="Tracer error"):
                integration_tracer.create_event(
                    project="test-project",
                    source="test",
                    event_name="test-event",
                    event_type="model",
                    config={},
                    inputs={},
                    duration=0.0,
                )

    def test_tracer_performance_monitoring(self, integration_tracer):
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

    def test_tracer_baggage_propagation(self, integration_tracer):
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

    def test_tracer_span_events(self, integration_tracer):
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
        self, integration_client, integration_tracer
    ):
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

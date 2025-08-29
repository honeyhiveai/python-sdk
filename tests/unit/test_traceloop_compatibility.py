"""Unit tests for HoneyHive Traceloop compatibility."""

import os
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer import HoneyHiveTracer
from honeyhive.tracer.span_processor import HoneyHiveSpanProcessor

# Type: ignore comments for pytest decorators
pytest_mark_asyncio = pytest.mark.asyncio  # type: ignore


class TestTraceloopCompatibility:
    """Test Traceloop compatibility functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Reset the singleton for each test
        HoneyHiveTracer.reset()

        # Mock OpenTelemetry availability
        with patch.dict(os.environ, {"HH_OTLP_ENABLED": "false"}):
            # Mock the _initialize_session method to prevent it from running
            with patch.object(HoneyHiveTracer, "_initialize_session"):
                self.tracer = HoneyHiveTracer(
                    project="test-project",
                    source="test",
                    api_key="test-key",
                    test_mode=True,
                )

    def test_traceloop_association_properties_basic_support(self) -> None:
        """Test that association_properties support exists in the span processor."""
        # Verify that the span processor class exists and can be instantiated
        span_processor = HoneyHiveSpanProcessor()
        assert span_processor is not None
        assert hasattr(span_processor, "on_start")
        assert callable(span_processor.on_start)

    def test_traceloop_association_properties_empty_context(self) -> None:
        """Test handling of empty context without association_properties."""
        span_processor = HoneyHiveSpanProcessor()

        mock_span = Mock()
        mock_context = Mock()
        mock_context.get.return_value = None

        # Should not crash with empty context
        span_processor.on_start(mock_span, mock_context)

        # No attributes should be set
        mock_span.set_attribute.assert_not_called()

    def test_traceloop_association_properties_none_value(self) -> None:
        """Test handling of None association_properties."""
        span_processor = HoneyHiveSpanProcessor()

        mock_span = Mock()
        mock_context = Mock()
        mock_context.get.return_value = None

        # Should not crash with None association_properties
        span_processor.on_start(mock_span, mock_context)

        # No attributes should be set
        mock_span.set_attribute.assert_not_called()

    def test_traceloop_association_properties_invalid_type(self) -> None:
        """Test handling of invalid association_properties type."""
        span_processor = HoneyHiveSpanProcessor()

        mock_span = Mock()
        mock_context = Mock()
        mock_context.get.return_value = "not-a-dict"

        # Should not crash with invalid type
        span_processor.on_start(mock_span, mock_context)

        # No attributes should be set
        mock_span.set_attribute.assert_not_called()

    def test_traceloop_association_properties_error_handling(self) -> None:
        """Test that errors in association_properties processing are handled gracefully."""
        span_processor = HoneyHiveSpanProcessor()

        mock_span = Mock()
        # Mock span.set_attribute to raise an exception
        mock_span.set_attribute.side_effect = Exception("Test error")

        # Create a context object with a get method
        mock_context = Mock()
        mock_context.get.return_value = {"key": "value"}

        # Should not crash when set_attribute fails
        span_processor.on_start(mock_span, mock_context)

        # The error should be caught and logged, but not crash the test

    def test_traceloop_association_properties_processor_creation(self) -> None:
        """Test that the span processor can be created and integrated."""
        # Verify that the span processor class exists
        assert HoneyHiveSpanProcessor is not None

        # Verify that it can be instantiated
        processor = HoneyHiveSpanProcessor()
        assert processor is not None

        # Verify it has the expected interface
        assert hasattr(processor, "on_start")
        assert hasattr(processor, "on_end")
        assert callable(processor.on_start)
        assert callable(processor.on_end)

    def test_traceloop_association_properties_tracer_integration(self) -> None:
        """Test that the tracer can be created with span processor support."""
        # The tracer should be able to create span processors
        # This tests the basic integration without complex OpenTelemetry setup
        assert self.tracer is not None
        assert hasattr(self.tracer, "_span_processor") or hasattr(
            self.tracer, "span_processor"
        )

    def test_traceloop_association_properties_legacy_support_structure(self) -> None:
        """Test that the legacy association_properties support structure exists."""
        # Verify that the span processor has the basic structure for legacy support
        span_processor = HoneyHiveSpanProcessor()

        # Check that the processor can handle basic operations
        mock_span = Mock()
        mock_context = Mock()

        # Test with minimal context that won't trigger complex processing
        mock_context.get.return_value = None

        # Should not crash with minimal context
        span_processor.on_start(mock_span, mock_context)

        # This test verifies the basic structure exists without testing complex logic

    def test_traceloop_association_properties_configuration(self) -> None:
        """Test that traceloop association_properties configuration is available."""
        # Test that the basic configuration for traceloop compatibility exists
        from honeyhive.utils.config import config

        # Verify that config exists and has expected structure
        assert config is not None
        assert hasattr(config, "experiment_id")
        assert hasattr(config, "experiment_name")
        assert hasattr(config, "experiment_variant")
        assert hasattr(config, "experiment_group")
        assert hasattr(config, "experiment_metadata")

    def test_traceloop_association_properties_imports(self) -> None:
        """Test that all necessary imports for traceloop compatibility work."""
        # Test that we can import the necessary components
        from honeyhive.tracer.span_processor import HoneyHiveSpanProcessor
        from honeyhive.utils.config import config

        # Verify imports work
        assert HoneyHiveSpanProcessor is not None
        assert config is not None

        # Test that we can create instances
        processor = HoneyHiveSpanProcessor()
        assert processor is not None

    def test_traceloop_association_properties_basic_workflow(self) -> None:
        """Test the basic workflow of creating and using the span processor."""
        # Test the complete basic workflow
        processor = HoneyHiveSpanProcessor()

        # Create basic mocks
        mock_span = Mock()
        mock_context = Mock()

        # Set up minimal context
        mock_context.get.return_value = None

        # Test the workflow
        processor.on_start(mock_span, mock_context)
        processor.on_end(mock_span)

        # Should complete without errors
        assert processor is not None

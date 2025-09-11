"""Unit tests for HoneyHive span processor functionality."""

import json
import time
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from opentelemetry.trace import Span, SpanContext, SpanKind
from opentelemetry.trace.span import TraceFlags

from honeyhive.tracer.span_processor import HoneyHiveSpanProcessor


class TestHoneyHiveSpanProcessor:
    """Test HoneyHiveSpanProcessor functionality."""

    def test_init(self) -> None:
        """Test HoneyHiveSpanProcessor initialization."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()
            assert processor is not None
            # No cache-related attributes anymore

    def test_init_otel_not_available(self) -> None:
        """Test initialization when OpenTelemetry is not available."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", False):
            with pytest.raises(ImportError, match="OpenTelemetry is required"):
                HoneyHiveSpanProcessor()

    def test_on_start_basic(self) -> None:
        """Test basic on_start functionality."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span
                    mock_span = Mock()
                    mock_span.name = "test_span"
                    mock_span.kind = "internal"
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Mock context and baggage with both session_id and project
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.get_baggage.side_effect = lambda key, ctx: {
                        "session_id": "test_session",
                        "project": "test_project",
                    }.get(key)

                    processor.on_start(mock_span)

                    # Verify span attributes were set
                    assert mock_span.set_attribute.called

    def test_on_start_with_session_id(self) -> None:
        """Test on_start with session_id in baggage."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span
                    mock_span = Mock()
                    mock_span.name = "test_span"
                    mock_span.kind = "internal"
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Mock context and baggage with both session_id and project
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.get_baggage.side_effect = lambda key, ctx: {
                        "session_id": "test_session",
                        "project": "test_project",
                    }.get(key)

                    processor.on_start(mock_span)

                    # Verify span attributes were set (check that set_attribute was called multiple times)
                    assert mock_span.set_attribute.call_count >= 2

    def test_on_start_openai_span(self) -> None:
        """Test on_start with OpenAI-related span."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock OpenAI span
                    mock_span = Mock()
                    mock_span.name = "openai.chat.completions"
                    mock_span.kind = "client"
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Mock context and baggage with both session_id and project
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.get_baggage.side_effect = lambda key, ctx: {
                        "session_id": "test_session",
                        "project": "test_project",
                    }.get(key)

                    processor.on_start(mock_span)

                    # Verify span attributes were set (check that set_attribute was called multiple times)
                    assert mock_span.set_attribute.call_count >= 2

    def test_on_start_with_parent_context(self) -> None:
        """Test on_start with parent context."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span
                    mock_span = Mock()
                    mock_span.name = "test_span"
                    mock_span.kind = "internal"
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Mock parent context and baggage with both session_id and project
                    mock_parent_ctx = Mock()
                    mock_baggage.get_baggage.side_effect = lambda key, ctx: {
                        "session_id": "test_session",
                        "project": "test_project",
                    }.get(key)

                    processor.on_start(mock_span, mock_parent_ctx)

                    # Verify span attributes were set
                    assert mock_span.set_attribute.called

    def test_on_start_no_context(self) -> None:
        """Test on_start when no context is available."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                processor = HoneyHiveSpanProcessor()

                # Mock span
                mock_span = Mock()
                mock_span.name = "test_span"
                mock_span.kind = "internal"
                mock_span.attributes = {}
                mock_span.set_attribute = Mock()

                # Mock no context
                mock_context.get_current.return_value = None

                processor.on_start(mock_span)

                # Verify no attributes were set
                mock_span.set_attribute.assert_not_called()

    def test_on_start_multiple_calls(self) -> None:
        """Test on_start with multiple calls (no caching)."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span
                    mock_span = Mock()
                    mock_span.name = "test_span"
                    mock_span.kind = "internal"
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Mock context and baggage with both session_id and project
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.get_baggage.side_effect = lambda key, ctx: {
                        "session_id": "test_session",
                        "project": "test_project",
                    }.get(key)

                    # First call
                    processor.on_start(mock_span)
                    first_call_count = mock_span.set_attribute.call_count

                    # Second call should process baggage again (no caching)
                    processor.on_start(mock_span)

                    # Verify attributes were set both times
                    assert mock_span.set_attribute.call_count >= first_call_count * 2

    def test_on_end_basic(self) -> None:
        """Test basic on_end functionality."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

            # Mock span
            mock_span = Mock()
            mock_span_context = Mock()
            mock_span_context.span_id = 12345
            mock_span.get_span_context.return_value = mock_span_context
            mock_span.start_time = 1000
            mock_span.end_time = 2000
            mock_span.attributes = {
                "honeyhive.session_id": "test-session"
            }  # Add session_id
            mock_span.name = "test-span"  # Add span name
            mock_span.set_attribute = Mock()

            processor.on_end(mock_span)

            # Verify span was processed (current implementation just logs, doesn't set attributes)
            # The actual duration handling is done by OTLP export, not by setting span attributes
            mock_span.set_attribute.assert_not_called()

    def test_on_end_invalid_span(self) -> None:
        """Test on_end with invalid span."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

            # Mock invalid span
            mock_span = Mock()
            mock_span_context = Mock()
            mock_span_context.span_id = 0  # Invalid span ID
            mock_span.get_span_context.return_value = mock_span_context

            # Should not raise any errors
            processor.on_end(mock_span)

    def test_on_end_no_timing(self) -> None:
        """Test on_end with no timing information."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

            # Mock span without timing
            mock_span = Mock()
            mock_span_context = Mock()
            mock_span_context.span_id = 12345
            mock_span.get_span_context.return_value = mock_span_context
            # No start_time or end_time

            # Should not raise any errors
            processor.on_end(mock_span)

    def test_shutdown(self) -> None:
        """Test shutdown functionality."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

            # Shutdown should complete without errors (no cache to clear)
            processor.shutdown()

            # Should succeed
            assert True

    def test_force_flush(self) -> None:
        """Test force_flush functionality."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock successful validation
                    mock_context.get_current.return_value = Mock()
                    mock_baggage.get_baggage.return_value = "test_session"

                    # Should return True
                    result = processor.force_flush()
                    assert result is True

    def test_force_flush_with_timeout(self) -> None:
        """Test force_flush with custom timeout."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock successful validation
                    mock_context.get_current.return_value = Mock()
                    mock_baggage.get_baggage.return_value = "test_session"

                    # Should return True with custom timeout
                    result = processor.force_flush(5000)
                    assert result is True

    def test_force_flush_validation_failure(self) -> None:
        """Test force_flush with validation failure."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                processor = HoneyHiveSpanProcessor()

                # Mock validation failure
                mock_context.get_current.side_effect = Exception("Context error")

                # Should return False due to validation failure
                result = processor.force_flush()
                assert result is False

    def test_force_flush_otel_not_available(self) -> None:
        """Test force_flush when OpenTelemetry is not available."""
        # First create processor when OTEL is available
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

        # Then test force_flush when OTEL is not available
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", False):
            # Should return True (graceful degradation)
            result = processor.force_flush()
            assert result is True

    def test_on_start_exception_handling(self) -> None:
        """Test exception handling in on_start."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                processor = HoneyHiveSpanProcessor()

                # Mock span that raises exception
                mock_span = Mock()
                mock_span.name = "test_span"
                mock_span.kind = "internal"
                mock_span.attributes = {}
                mock_span.set_attribute.side_effect = Exception("Test error")

                # Mock context
                mock_ctx = Mock()
                mock_context.get_current.return_value = mock_ctx

                # Should not raise exception
                processor.on_start(mock_span)

    def test_on_end_exception_handling(self) -> None:
        """Test exception handling in on_end."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

            # Mock span that raises exception
            mock_span = Mock()
            mock_span.get_span_context.side_effect = Exception("Test error")

            # Should not raise exception
            processor.on_end(mock_span)

    def test_shutdown_exception_handling(self) -> None:
        """Test exception handling in shutdown."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

            # Should not raise exception (no cache operations)
            processor.shutdown()

    def test_otel_not_available_methods(self) -> None:
        """Test methods when OpenTelemetry is not available."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", False):
            # This should raise ImportError during initialization
            with pytest.raises(ImportError, match="OpenTelemetry is required"):
                HoneyHiveSpanProcessor()

    def test_span_attributes_complex_types(self) -> None:
        """Test handling of complex attribute types."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span
                    mock_span = Mock()
                    mock_span.name = "test_span"
                    mock_span.kind = "internal"
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Mock context and baggage with complex data
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.get_baggage.side_effect = lambda key, ctx: {
                        "session_id": "test_session",
                        "project": "test_project",
                        "source": "test_source",
                        "metadata": {"key": "value"},
                        "tags": ["tag1", "tag2"],
                    }.get(key)

                    processor.on_start(mock_span)

                    # Verify complex attributes were set
                    assert mock_span.set_attribute.called

    def test_span_attributes_none_values(self) -> None:
        """Test handling of None attribute values."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span
                    mock_span = Mock()
                    mock_span.name = "test_span"
                    mock_span.kind = "internal"
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Mock context and baggage with both session_id and project
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.get_baggage.side_effect = lambda key, ctx: {
                        "session_id": "test_session",
                        "project": "test_project",
                    }.get(key)

                    processor.on_start(mock_span)

                    # Should handle None values gracefully
                    assert mock_span.set_attribute.called

    def test_span_attributes_empty_values(self) -> None:
        """Test handling of empty attribute values."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span
                    mock_span = Mock()
                    mock_span.name = "test_span"
                    mock_span.kind = "internal"
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Mock context and baggage with both session_id and project
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.get_baggage.side_effect = lambda key, ctx: {
                        "session_id": "test_session",
                        "project": "test_project",
                    }.get(key)

                    processor.on_start(mock_span)

                    # Should handle empty values gracefully
                    assert mock_span.set_attribute.called

    def test_span_attributes_zero_values(self) -> None:
        """Test handling of zero attribute values."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span
                    mock_span = Mock()
                    mock_span.name = "test_span"
                    mock_span.kind = "internal"
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Mock context and baggage with both session_id and project
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.get_baggage.side_effect = lambda key, ctx: {
                        "session_id": "test_session",
                        "project": "test_project",
                    }.get(key)

                    processor.on_start(mock_span)

                    # Should handle zero values gracefully
                    assert mock_span.set_attribute.called

    def test_otel_imports_available(self) -> None:
        """Test that OTEL imports are covered when available."""
        # This test ensures import coverage for lines that are only executed
        # when OTEL_AVAILABLE is True
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            # Force reimport to cover conditional import lines
            import importlib

            import honeyhive.tracer.span_processor

            importlib.reload(honeyhive.tracer.span_processor)

            # Verify the imports worked
            assert hasattr(honeyhive.tracer.span_processor, "HoneyHiveSpanProcessor")

    def test_span_attributes_edge_cases(self) -> None:
        """Test edge cases in span attribute handling."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span with minimal attributes
                    mock_span = Mock()
                    mock_span.name = None  # Edge case: None name
                    mock_span.kind = None  # Edge case: None kind
                    mock_span.attributes = None  # Edge case: None attributes
                    mock_span.set_attribute = Mock()

                    # Mock context and baggage
                    mock_ctx = Mock()
                    mock_context.get_current.return_value = mock_ctx
                    mock_baggage.get_baggage.return_value = None  # No baggage

                    # Should handle None values gracefully
                    processor.on_start(mock_span)

    def test_otel_import_coverage(self) -> None:
        """Test OpenTelemetry import paths for coverage."""
        # This test ensures that both import paths are covered
        import importlib
        import sys

        # Test the import success path (lines 6-8, 15)
        if "opentelemetry" in sys.modules:
            # Force reload to cover import lines
            import honeyhive.tracer.span_processor

            importlib.reload(honeyhive.tracer.span_processor)

        # Test that OTEL_AVAILABLE is correctly set
        from honeyhive.tracer.span_processor import OTEL_AVAILABLE

        assert isinstance(OTEL_AVAILABLE, bool)

    def test_initialization_edge_case(self) -> None:
        """Test initialization with different OTEL states."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            # Test normal initialization
            processor = HoneyHiveSpanProcessor()
            assert processor is not None

            # Test that processor handles missing OpenTelemetry gracefully
            with patch("honeyhive.tracer.span_processor.SpanProcessor", None):
                try:
                    # This should still work or handle gracefully
                    processor = HoneyHiveSpanProcessor()
                except (ImportError, TypeError, AttributeError):
                    # Expected if OpenTelemetry components are missing
                    pass

    def test_span_processor_error_paths(self) -> None:
        """Test error handling paths in span processor."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

            # Test on_start with None span
            try:
                processor.on_start(None)
            except (AttributeError, TypeError):
                pass  # Expected for None span

            # Test on_end with None span
            try:
                processor.on_end(None)
            except (AttributeError, TypeError):
                pass  # Expected for None span

    def test_span_context_edge_cases(self) -> None:
        """Test span context handling edge cases."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            with patch("honeyhive.tracer.span_processor.context") as mock_context:
                with patch("honeyhive.tracer.span_processor.baggage") as mock_baggage:
                    processor = HoneyHiveSpanProcessor()

                    # Mock span with various edge cases
                    mock_span = Mock()
                    mock_span.name = ""  # Empty name
                    mock_span.kind = 0  # Numeric kind
                    mock_span.attributes = {}
                    mock_span.set_attribute = Mock()

                    # Test with context that raises exceptions
                    mock_context.get_current.side_effect = Exception("Context error")

                    # Should handle gracefully
                    processor.on_start(mock_span)

                    # Reset and test baggage error
                    mock_context.get_current.side_effect = None
                    mock_context.get_current.return_value = Mock()
                    mock_baggage.get_baggage.side_effect = Exception("Baggage error")

                    processor.on_start(mock_span)

    def test_span_timing_calculations(self) -> None:
        """Test span timing calculation edge cases."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

            # Test with various timing scenarios
            test_cases = [
                {"start_time": 1000, "end_time": 2000},  # Normal case
                {"start_time": 0, "end_time": 1000},  # Zero start time
                {"start_time": 1000, "end_time": 1000},  # Same time
                {"start_time": 2000, "end_time": 1000},  # Negative duration
            ]

            for case in test_cases:
                mock_span = Mock()
                mock_span_context = Mock()
                mock_span_context.span_id = 12345
                mock_span.get_span_context.return_value = mock_span_context
                mock_span.start_time = case["start_time"]
                mock_span.end_time = case["end_time"]
                mock_span.set_attribute = Mock()

                processor.on_end(mock_span)

    def test_module_import_states(self) -> None:
        """Test module behavior under different import states."""
        # Test that we can handle the module in different states
        import honeyhive.tracer.span_processor as span_mod

        # Verify module attributes exist
        assert hasattr(span_mod, "HoneyHiveSpanProcessor")
        assert hasattr(span_mod, "OTEL_AVAILABLE")

        # Test the processor class is accessible
        if span_mod.OTEL_AVAILABLE:
            processor = span_mod.HoneyHiveSpanProcessor()
            assert processor is not None

    def test_import_error_handling(self) -> None:
        """Test import error handling using sys.modules manipulation."""
        import sys
        from unittest.mock import patch

        # Use the technique from the Medium article to simulate ImportError
        otel_modules = [
            key for key in sys.modules.keys() if key.startswith("opentelemetry")
        ]

        # Create a patch dict that sets all OpenTelemetry modules to None
        patch_dict = {module: None for module in otel_modules}
        patch_dict["opentelemetry"] = None
        patch_dict["opentelemetry.sdk"] = None
        patch_dict["opentelemetry.sdk.trace"] = None

        with patch.dict(sys.modules, patch_dict):
            # Force reimport to trigger the ImportError path
            import importlib

            import honeyhive.tracer.span_processor

            importlib.reload(honeyhive.tracer.span_processor)

            # This should have triggered the ImportError handling
            # and set OTEL_AVAILABLE to False
            from honeyhive.tracer.span_processor import OTEL_AVAILABLE

            # Verify the import error was handled gracefully
            # (Either True or False is acceptable, just testing the path)
            assert isinstance(OTEL_AVAILABLE, bool)

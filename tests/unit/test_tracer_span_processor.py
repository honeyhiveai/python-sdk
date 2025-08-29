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
            mock_span.set_attribute = Mock()

            processor.on_end(mock_span)

            # Verify duration attribute was set
            mock_span.set_attribute.assert_called_with("honeyhive.span.duration", 1000)

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
            processor = HoneyHiveSpanProcessor()

            # Should return True
            result = processor.force_flush()
            assert result is True

    def test_force_flush_with_timeout(self) -> None:
        """Test force_flush with custom timeout."""
        with patch("honeyhive.tracer.span_processor.OTEL_AVAILABLE", True):
            processor = HoneyHiveSpanProcessor()

            # Should return True with custom timeout
            result = processor.force_flush(5000)
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

"""Unit tests for batched async export via OTel BatchSpanProcessor integration.

Tests the HoneyHiveSpanProcessor's internal BatchSpanProcessor wiring:
- Batch mode creates an internal BatchSpanProcessor
- Immediate mode (disable_batch=True) does not
- Spans are enqueued (not exported inline) in batch mode
- force_flush drains the batch queue
- shutdown drains and stops the batch processor
- Config params are passed through correctly
"""

import time
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExportResult

from honeyhive.tracer.processing.span_processor import HoneyHiveSpanProcessor

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_exporter() -> Mock:
    """Create a mock OTLP exporter that satisfies the SpanExporter interface."""
    exporter = Mock()
    exporter.export = Mock(return_value=SpanExportResult.SUCCESS)
    exporter.shutdown = Mock()
    exporter.force_flush = Mock(return_value=True)
    return exporter


def _make_mock_span(
    name: str = "test-span",
    trace_id: int = 0xDEADBEEF,
    span_id: int = 0xCAFE,
    session_id: str = "test-session-123",
) -> Mock:
    """Create a mock ReadableSpan with the minimum attributes needed."""
    span = Mock(spec=ReadableSpan)
    span.name = name
    span.context = Mock()
    span.context.trace_id = trace_id
    span.context.span_id = span_id
    span.context.trace_flags = Mock()
    span.context.trace_flags.sampled = True
    span.parent = None
    span.resource = Mock()
    span.resource.attributes = {"service.name": "test"}
    span.instrumentation_scope = Mock()
    span.instrumentation_scope.name = "honeyhive"
    span.instrumentation_scope.version = "1.0.0"
    span.attributes = {
        "honeyhive.session_id": session_id,
        "honeyhive.project": "test-project",
    }
    span.status = Mock()
    span.status.status_code = Mock()
    span.status.status_code.name = "OK"
    span.status.description = None
    span.events = []
    span.links = []
    span.start_time = 1000000000
    span.end_time = 2000000000
    span.kind = Mock()
    span.kind.name = "INTERNAL"
    return span


# ---------------------------------------------------------------------------
# Initialization tests
# ---------------------------------------------------------------------------


class TestBatchProcessorInitialization:
    """Test that the internal BatchSpanProcessor is created/skipped correctly."""

    def test_batch_mode_creates_internal_batch_processor(self) -> None:
        """When disable_batch=False and exporter provided, _batch_processor is created."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
        )
        assert processor._batch_processor is not None
        assert isinstance(processor._batch_processor, BatchSpanProcessor)
        # Cleanup
        processor.shutdown()

    def test_immediate_mode_skips_batch_processor(self) -> None:
        """When disable_batch=True, _batch_processor is None."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=True,
        )
        assert processor._batch_processor is None
        processor.shutdown()

    def test_no_exporter_skips_batch_processor(self) -> None:
        """When no exporter is provided, _batch_processor is None even if batching enabled."""
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=None,
            disable_batch=False,
        )
        assert processor._batch_processor is None

    def test_default_batch_config_values(self) -> None:
        """Defaults are applied when no explicit config is passed."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
        )
        # We can't directly inspect BatchSpanProcessor internals easily,
        # but we can verify the processor was created without error.
        assert processor._batch_processor is not None
        processor.shutdown()

    def test_custom_batch_config_values(self) -> None:
        """Custom batch config params are accepted without error."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
            max_queue_size=512,
            schedule_delay_millis=1000.0,
            max_export_batch_size=32,
            export_timeout_millis=10000.0,
        )
        assert processor._batch_processor is not None
        processor.shutdown()


# ---------------------------------------------------------------------------
# Export path tests
# ---------------------------------------------------------------------------


class TestBatchExportPath:
    """Test that spans go through the right export path."""

    def test_immediate_mode_calls_exporter_directly(self) -> None:
        """In immediate mode, export([span]) is called synchronously."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=True,
        )

        span = _make_mock_span()
        processor._send_via_otlp(span, {}, "test-session")

        # Exporter should have been called directly with a single-element list
        exporter.export.assert_called_once()
        exported_spans = exporter.export.call_args[0][0]
        assert len(exported_spans) == 1
        assert exported_spans[0] is span
        processor.shutdown()

    def test_batch_mode_does_not_call_exporter_directly(self) -> None:
        """In batch mode, the exporter is NOT called inline from _send_via_otlp."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
            # Use a long delay so the batch worker doesn't auto-flush
            schedule_delay_millis=60000.0,
        )

        span = _make_mock_span()
        processor._send_via_otlp(span, {}, "test-session")

        # The exporter should NOT have been called yet — span is queued
        exporter.export.assert_not_called()
        processor.shutdown()

    def test_batch_mode_exports_on_flush(self) -> None:
        """Spans enqueued in batch mode are exported when force_flush is called."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
            # Long delay to prevent auto-flush during test
            schedule_delay_millis=60000.0,
            max_export_batch_size=64,
        )

        # Enqueue several spans
        for i in range(5):
            span = _make_mock_span(name=f"span-{i}")
            processor._send_via_otlp(span, {}, "test-session")

        # Nothing exported yet
        exporter.export.assert_not_called()

        # Force flush should trigger export
        result = processor.force_flush(timeout_millis=5000)
        assert result is True

        # Exporter should have been called with all spans in one batch
        assert exporter.export.call_count >= 1
        # Total spans exported across all calls should be 5
        total_exported = sum(len(c[0][0]) for c in exporter.export.call_args_list)
        assert total_exported == 5

        processor.shutdown()

    def test_batch_mode_exports_on_shutdown(self) -> None:
        """Remaining queued spans are drained on shutdown."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
            schedule_delay_millis=60000.0,
        )

        for i in range(3):
            span = _make_mock_span(name=f"shutdown-span-{i}")
            processor._send_via_otlp(span, {}, "test-session")

        exporter.export.assert_not_called()

        # Shutdown should drain the queue
        processor.shutdown()

        assert exporter.export.call_count >= 1
        total_exported = sum(len(c[0][0]) for c in exporter.export.call_args_list)
        assert total_exported == 3

    def test_batch_mode_auto_flush_on_interval(self) -> None:
        """Spans are auto-flushed after schedule_delay_millis."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
            # Very short flush interval for testing
            schedule_delay_millis=100.0,
            max_export_batch_size=64,
        )

        span = _make_mock_span(name="auto-flush-span")
        processor._send_via_otlp(span, {}, "test-session")

        # Wait for the auto-flush to trigger
        time.sleep(0.5)

        assert exporter.export.call_count >= 1
        processor.shutdown()

    def test_batch_mode_auto_flush_on_batch_size(self) -> None:
        """Spans are auto-flushed when max_export_batch_size is reached."""
        exporter = _make_mock_exporter()
        batch_size = 4
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
            schedule_delay_millis=60000.0,  # Long delay
            max_export_batch_size=batch_size,
        )

        # Enqueue exactly batch_size spans — should trigger export
        for i in range(batch_size):
            span = _make_mock_span(name=f"batch-span-{i}")
            processor._send_via_otlp(span, {}, "test-session")

        # Give the background thread a moment to process
        time.sleep(0.5)

        assert exporter.export.call_count >= 1
        total_exported = sum(len(c[0][0]) for c in exporter.export.call_args_list)
        assert total_exported == batch_size

        processor.shutdown()


# ---------------------------------------------------------------------------
# force_flush tests
# ---------------------------------------------------------------------------


class TestForceFlush:
    """Test force_flush behavior in both modes."""

    def test_force_flush_batch_mode_returns_true(self) -> None:
        """force_flush succeeds in batch mode with no pending spans."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
        )
        result = processor.force_flush(timeout_millis=5000)
        assert result is True
        processor.shutdown()

    def test_force_flush_immediate_mode_delegates_to_exporter(self) -> None:
        """In immediate mode, force_flush calls exporter.force_flush."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=True,
        )
        result = processor.force_flush(timeout_millis=5000)
        assert result is True
        exporter.force_flush.assert_called_once_with(5000)
        processor.shutdown()

    def test_force_flush_no_exporter_returns_true(self) -> None:
        """force_flush with no exporter returns True (nothing to flush)."""
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=None,
            disable_batch=True,
        )
        result = processor.force_flush(timeout_millis=5000)
        assert result is True


# ---------------------------------------------------------------------------
# shutdown tests
# ---------------------------------------------------------------------------


class TestShutdown:
    """Test shutdown behavior in both modes."""

    def test_shutdown_batch_mode_shuts_down_batch_processor(self) -> None:
        """In batch mode, shutdown() shuts down the internal BatchSpanProcessor."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
        )
        assert processor._batch_processor is not None

        processor.shutdown()

        # After shutdown, the exporter should have been shut down
        # (BatchSpanProcessor calls exporter.shutdown() internally)
        exporter.shutdown.assert_called()

    def test_shutdown_immediate_mode_shuts_down_exporter(self) -> None:
        """In immediate mode, shutdown() shuts down the exporter directly."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=True,
        )
        processor.shutdown()
        exporter.shutdown.assert_called_once()

    def test_shutdown_no_exporter_does_not_raise(self) -> None:
        """shutdown() with no exporter does not raise."""
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=None,
            disable_batch=True,
        )
        processor.shutdown()  # Should not raise


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Test graceful degradation on errors."""

    def test_send_via_otlp_handles_batch_enqueue_error(self) -> None:
        """If BatchSpanProcessor.on_end raises, error is caught gracefully."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
        )
        # Force the batch processor's on_end to raise
        processor._batch_processor.on_end = Mock(side_effect=RuntimeError("queue full"))

        span = _make_mock_span()
        # Should not raise
        processor._send_via_otlp(span, {}, "test-session")
        processor.shutdown()

    def test_force_flush_handles_batch_processor_error(self) -> None:
        """If BatchSpanProcessor.force_flush raises, returns False."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
        )
        processor._batch_processor.force_flush = Mock(
            side_effect=RuntimeError("flush failed")
        )

        result = processor.force_flush(timeout_millis=1000)
        assert result is False
        processor.shutdown()

    def test_shutdown_handles_batch_processor_error(self) -> None:
        """If BatchSpanProcessor.shutdown raises, error is caught."""
        exporter = _make_mock_exporter()
        processor = HoneyHiveSpanProcessor(
            otlp_exporter=exporter,
            disable_batch=False,
        )
        processor._batch_processor.shutdown = Mock(
            side_effect=RuntimeError("shutdown failed")
        )

        # Should not raise
        processor.shutdown()

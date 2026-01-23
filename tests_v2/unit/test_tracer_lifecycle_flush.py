"""Unit tests for tracer lifecycle flush operations.

This module tests the force flush operations for tracer lifecycle management,
including tracer provider flushing, span processor flushing, batch processor
handling, error handling, timeout management, and graceful degradation.

Based on thorough inspection of the actual implementation in:
- src/honeyhive/tracer/lifecycle/flush.py
- src/honeyhive/tracer/lifecycle/core.py
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long,R0917
# Justification: Comprehensive test coverage requires extensive test cases, testing private methods
# requires protected access, pytest fixtures redefine outer names by design, comprehensive test
# classes need many test methods, and mock patch decorators create unavoidable long lines.


from contextlib import contextmanager
from typing import Any, Iterator, List
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.lifecycle.flush import (
    _flush_batch_processors,
    _flush_single_processor,
    _flush_span_processor,
    _flush_tracer_provider,
    _get_batch_processors,
    _log_flush_results,
    force_flush_tracer,
)

# Using standard fixtures from conftest.py


@pytest.fixture
def mock_tracer() -> Mock:
    """Mock tracer instance for flush tests.

    Creates a fresh mock tracer for each test to ensure isolation.
    Uses the standard mock_safe_log fixture pattern.
    """
    tracer = Mock()
    tracer.test_mode = False
    tracer.provider = Mock()
    tracer.span_processor = Mock()
    return tracer


@pytest.fixture
def mock_context_manager() -> Any:
    """Mock context manager for lifecycle lock acquisition."""

    @contextmanager
    def mock_acquire_lock(*_args: Any, **_kwargs: Any) -> Iterator[bool]:
        yield True

    return mock_acquire_lock


class TestForceFlushTracer:
    """Test suite for force_flush_tracer function."""

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    @patch("honeyhive.tracer.lifecycle.flush.acquire_lifecycle_lock_optimized")
    @patch("honeyhive.tracer.lifecycle.flush._flush_tracer_provider")
    @patch("honeyhive.tracer.lifecycle.flush._flush_span_processor")
    @patch("honeyhive.tracer.lifecycle.flush._flush_batch_processors")
    @patch("honeyhive.tracer.lifecycle.flush._log_flush_results")
    def test_force_flush_success_all_components(
        self,
        mock_log_results: Mock,
        mock_flush_batch: Mock,
        mock_flush_span: Mock,
        mock_flush_provider: Mock,
        mock_acquire_lock: Mock,
        _mock_safe_log: Mock,
        mock_tracer: Mock,
        mock_context_manager: Any,
    ) -> None:
        """Test successful force flush of all components."""
        # Setup
        mock_acquire_lock.return_value = mock_context_manager()

        # Mock flush results to simulate successful flushes
        def setup_flush_results(
            _tracer: Any, _timeout: Any, results: List[tuple[str, bool]]
        ) -> None:
            results.extend(
                [
                    ("provider", True),
                    ("span_processor", True),
                    ("batch_processors", True),
                ]
            )

        mock_flush_provider.side_effect = setup_flush_results
        mock_flush_span.side_effect = lambda t, tm, r: r.append(
            ("span_processor", True)
        )
        mock_flush_batch.side_effect = lambda t, tm, r: r.append(
            ("batch_processors", True)
        )

        # Execute
        result = force_flush_tracer(mock_tracer, timeout_millis=5000)

        # Verify
        assert result is True
        mock_acquire_lock.assert_called_once_with("flush", custom_timeout=5.0)
        mock_flush_provider.assert_called_once()
        mock_flush_span.assert_called_once()
        mock_flush_batch.assert_called_once()
        mock_log_results.assert_called_once()

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    @patch("honeyhive.tracer.lifecycle.flush.acquire_lifecycle_lock_optimized")
    def test_force_flush_lock_acquisition_failure(
        self, mock_acquire_lock: Mock, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test force flush when lock acquisition fails."""

        # Setup - lock acquisition fails
        @contextmanager
        def mock_failed_lock(*_args: Any, **_kwargs: Any) -> Iterator[bool]:
            yield False

        mock_acquire_lock.side_effect = mock_failed_lock

        # Execute
        result = force_flush_tracer(mock_tracer, timeout_millis=1000)

        # Verify - this tests lines 74-78
        assert result is False
        mock_safe_log.assert_any_call(
            mock_tracer,
            "warning",
            "Failed to acquire _lifecycle_lock (1.0s)",
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    @patch("honeyhive.tracer.lifecycle.flush.acquire_lifecycle_lock_optimized")
    def test_force_flush_exception_handling(
        self, mock_acquire_lock: Mock, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test force flush exception handling."""
        # Setup - exception during flush operations
        mock_acquire_lock.side_effect = Exception("Lock error")

        # Execute
        result = force_flush_tracer(mock_tracer, timeout_millis=5000)

        # Verify - this tests lines 98-105 with standardized error handling
        assert result is False
        mock_safe_log.assert_any_call(
            mock_tracer,
            "error",
            "Force flush failed",
            honeyhive_data={
                "error": "Lock error",
                "error_type": "Exception",
                "operation": "force_flush_tracer",
            },
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    @patch("honeyhive.tracer.lifecycle.flush.acquire_lifecycle_lock_optimized")
    def test_force_flush_exception_handling_test_mode(
        self, mock_acquire_lock: Mock, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test force flush exception handling with consistent behavior regardless of
        test_mode."""
        # Setup
        mock_tracer.test_mode = True
        mock_acquire_lock.side_effect = Exception("Lock error")

        # Execute
        result = force_flush_tracer(mock_tracer, timeout_millis=5000)

        # Verify - consistent behavior regardless of test_mode (Agent OS standards)
        assert result is False
        # Error logging should occur consistently regardless of test_mode
        mock_safe_log.assert_any_call(
            mock_tracer,
            "error",
            "Force flush failed",
            honeyhive_data={
                "error": "Lock error",
                "error_type": "Exception",
                "operation": "force_flush_tracer",
            },
        )


class TestFlushTracerProvider:
    """Test suite for _flush_tracer_provider function."""

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_provider_success(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test successful provider flush."""
        # Setup
        mock_tracer.provider.force_flush.return_value = True
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_tracer_provider(mock_tracer, 5000, flush_results)

        # Verify
        assert flush_results == [("provider", True)]
        mock_tracer.provider.force_flush.assert_called_once_with(timeout_millis=5000)
        mock_safe_log.assert_any_call(
            mock_tracer,
            "debug",
            "Provider force_flush completed",
            honeyhive_data={"success": True, "operation": "provider_flush"},
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_provider_exception(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test provider flush exception handling."""
        # Setup
        mock_tracer.provider.force_flush.side_effect = Exception("Provider error")
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_tracer_provider(mock_tracer, 5000, flush_results)

        # Verify - this tests lines 128-135
        assert flush_results == [("provider", False)]
        mock_safe_log.assert_any_call(
            mock_tracer,
            "error",
            "Provider force_flush error",
            honeyhive_data={
                "error": "Provider error",
                "error_type": "Exception",
                "operation": "provider_flush",
            },
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_provider_exception_test_mode(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test provider flush exception handling in test mode."""
        # Setup
        mock_tracer.test_mode = True
        mock_tracer.provider.force_flush.side_effect = Exception("Provider error")
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_tracer_provider(mock_tracer, 5000, flush_results)

        # Verify - this tests the test_mode branch in lines 130-134
        assert flush_results == [("provider", False)]
        # Should not log error in test mode
        error_calls = [
            call for call in mock_safe_log.call_args_list if call[0][0] == "error"
        ]
        assert len(error_calls) == 0

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_provider_no_force_flush_method(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test provider without force_flush method."""
        # Setup - provider exists but no force_flush method
        del mock_tracer.provider.force_flush
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_tracer_provider(mock_tracer, 5000, flush_results)

        # Verify - this tests lines 136-139
        assert flush_results == [("provider", True)]
        mock_safe_log.assert_any_call(
            mock_tracer,
            "debug",
            "Provider does not support force_flush",
            honeyhive_data={"operation": "provider_flush"},
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_provider_no_force_flush_method_test_mode(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test provider without force_flush method in test mode."""
        # Setup
        mock_tracer.test_mode = True
        del mock_tracer.provider.force_flush
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_tracer_provider(mock_tracer, 5000, flush_results)

        # Verify - this tests the test_mode branch in lines 137-138
        assert flush_results == [("provider", True)]
        # Should not log debug in test mode
        debug_calls = [
            call for call in mock_safe_log.call_args_list if call[0][0] == "debug"
        ]
        assert len(debug_calls) == 0


class TestFlushSpanProcessor:
    """Test suite for _flush_span_processor function."""

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_span_processor_success(
        self, _mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test successful span processor flush."""
        # Setup
        mock_tracer.span_processor.force_flush.return_value = True
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_span_processor(mock_tracer, 5000, flush_results)

        # Verify
        assert flush_results == [("span_processor", True)]
        mock_tracer.span_processor.force_flush.assert_called_once_with(
            timeout_millis=5000
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_span_processor_exception(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test span processor flush exception handling."""
        # Setup
        mock_tracer.span_processor.force_flush.side_effect = Exception(
            "Processor error"
        )
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_span_processor(mock_tracer, 5000, flush_results)

        # Verify - this tests lines 168-175
        assert flush_results == [("span_processor", False)]
        mock_safe_log.assert_any_call(
            mock_tracer,
            "error",
            "Span processor force_flush error",
            honeyhive_data={
                "error": "Processor error",
                "error_type": "Exception",
                "operation": "span_processor_flush",
            },
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_span_processor_exception_test_mode(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test span processor flush exception handling in test mode."""
        # Setup
        mock_tracer.test_mode = True
        mock_tracer.span_processor.force_flush.side_effect = Exception(
            "Processor error"
        )
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_span_processor(mock_tracer, 5000, flush_results)

        # Verify - this tests the test_mode branch in lines 170-174
        assert flush_results == [("span_processor", False)]
        # Should not log error in test mode
        error_calls = [
            call for call in mock_safe_log.call_args_list if call[0][0] == "error"
        ]
        assert len(error_calls) == 0

    def test_flush_span_processor_no_processor(self, mock_tracer: Mock) -> None:
        """Test when span processor is None."""
        # Setup
        mock_tracer.span_processor = None
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_span_processor(mock_tracer, 5000, flush_results)

        # Verify - this tests lines 176-179
        assert flush_results == [("span_processor", True)]


class TestGetBatchProcessors:
    """Test suite for _get_batch_processors function."""

    def test_get_batch_processors_success(self, mock_tracer: Mock) -> None:
        """Test successful batch processor extraction."""
        # Setup
        mock_processor1 = Mock()
        mock_processor1.force_flush = Mock()
        mock_processor2 = Mock()  # No force_flush method
        # Remove force_flush attribute to ensure it's not detected
        if hasattr(mock_processor2, "force_flush"):
            delattr(mock_processor2, "force_flush")
        mock_processor3 = Mock()
        mock_processor3.force_flush = Mock()

        mock_tracer.provider._span_processors = [
            mock_processor1,
            mock_processor2,
            mock_processor3,
        ]

        # Execute
        result = _get_batch_processors(mock_tracer)

        # Verify
        assert len(result) == 2
        assert mock_processor1 in result
        assert mock_processor3 in result
        assert mock_processor2 not in result

    def test_get_batch_processors_no_provider(self, mock_tracer: Mock) -> None:
        """Test when provider is None."""
        # Setup
        mock_tracer.provider = None

        # Execute
        result = _get_batch_processors(mock_tracer)

        # Verify - this tests line 188
        assert not result

    def test_get_batch_processors_no_span_processors_attr(
        self, mock_tracer: Mock
    ) -> None:
        """Test when provider has no _span_processors attribute."""
        # Setup
        del mock_tracer.provider._span_processors

        # Execute
        result = _get_batch_processors(mock_tracer)

        # Verify - this tests lines 192-194
        assert not result


class TestFlushSingleProcessor:
    """Test suite for _flush_single_processor function."""

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_single_processor_success(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test successful single processor flush."""
        # Setup
        mock_processor = Mock()
        mock_processor.force_flush.return_value = True

        # Execute
        result = _flush_single_processor(mock_processor, 5000, 1, mock_tracer)

        # Verify
        assert result is True
        mock_processor.force_flush.assert_called_once_with(timeout_millis=5000)
        mock_safe_log.assert_any_call(
            mock_tracer,
            "debug",
            "Batch processor force_flush completed",
            honeyhive_data={
                "processor_index": 1,
                "success": True,
                "operation": "batch_processor_flush",
            },
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_single_processor_exception(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test single processor flush exception handling."""
        # Setup
        mock_processor = Mock()
        mock_processor.force_flush.side_effect = Exception("Single processor error")

        # Execute
        result = _flush_single_processor(mock_processor, 5000, 2, mock_tracer)

        # Verify - this tests lines 213-223
        assert result is False
        mock_safe_log.assert_any_call(
            mock_tracer,
            "error",
            "Batch processor force_flush error",
            honeyhive_data={
                "processor_index": 2,
                "error": "Single processor error",
                "error_type": "Exception",
                "operation": "batch_processor_flush",
            },
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_flush_single_processor_exception_test_mode(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test single processor flush exception handling in test mode."""
        # Setup
        mock_tracer.test_mode = True
        mock_processor = Mock()
        mock_processor.force_flush.side_effect = Exception("Single processor error")

        # Execute
        result = _flush_single_processor(mock_processor, 5000, 2, mock_tracer)

        # Verify - this tests the test_mode branch in lines 214-222
        assert result is False
        # Should not log error in test mode
        error_calls = [
            call for call in mock_safe_log.call_args_list if call[0][0] == "error"
        ]
        assert len(error_calls) == 0


class TestFlushBatchProcessors:
    """Test suite for _flush_batch_processors function."""

    @patch("honeyhive.tracer.lifecycle.flush._get_batch_processors")
    @patch("honeyhive.tracer.lifecycle.flush._flush_single_processor")
    def test_flush_batch_processors_success(
        self, mock_flush_single: Mock, mock_get_processors: Mock, mock_tracer: Mock
    ) -> None:
        """Test successful batch processors flush."""
        # Setup
        mock_processor1 = Mock()
        mock_processor2 = Mock()
        mock_get_processors.return_value = [mock_processor1, mock_processor2]
        mock_flush_single.side_effect = [True, True]
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_batch_processors(mock_tracer, 5000, flush_results)

        # Verify - this tests lines 245-252
        assert flush_results == [("batch_processors", True)]
        assert mock_flush_single.call_count == 2
        mock_flush_single.assert_any_call(mock_processor1, 5000, 1, mock_tracer)
        mock_flush_single.assert_any_call(mock_processor2, 5000, 2, mock_tracer)

    @patch("honeyhive.tracer.lifecycle.flush._get_batch_processors")
    def test_flush_batch_processors_no_processors(
        self, mock_get_processors: Mock, mock_tracer: Mock
    ) -> None:
        """Test when no batch processors are found."""
        # Setup
        mock_get_processors.return_value = []
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_batch_processors(mock_tracer, 5000, flush_results)

        # Verify - this tests lines 241-243
        assert flush_results == [("batch_processors", True)]

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    @patch("honeyhive.tracer.lifecycle.flush._get_batch_processors")
    def test_flush_batch_processors_exception(
        self, mock_get_processors: Mock, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test batch processors flush exception handling."""
        # Setup
        mock_get_processors.side_effect = Exception("Batch error")
        flush_results: List[tuple[str, bool]] = []

        # Execute
        _flush_batch_processors(mock_tracer, 5000, flush_results)

        # Verify
        assert flush_results == [("batch_processors", False)]
        mock_safe_log.assert_any_call(
            mock_tracer,
            "error",
            "Batch processors flush error",
            honeyhive_data={
                "error": "Batch error",
                "error_type": "Exception",
                "operation": "batch_processors_flush",
            },
        )


class TestLogFlushResults:
    """Test suite for _log_flush_results function."""

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_log_flush_results_success(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test logging successful flush results."""
        # Setup
        flush_results = [
            ("provider", True),
            ("span_processor", True),
            ("batch_processors", True),
        ]

        # Execute
        _log_flush_results(mock_tracer, True, flush_results)

        # Verify - this tests line 280
        mock_safe_log.assert_any_call(
            mock_tracer,
            "info",
            "Force flush completed successfully",
            honeyhive_data={
                "components_flushed": 3,
                "all_successful": True,
            },
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_log_flush_results_failure(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test logging failed flush results."""
        # Setup
        flush_results = [
            ("provider", True),
            ("span_processor", False),
            ("batch_processors", True),
        ]

        # Execute
        _log_flush_results(mock_tracer, False, flush_results)

        # Verify
        mock_safe_log.assert_any_call(
            mock_tracer,
            "warning",
            "Force flush completed with failures",
            honeyhive_data={
                "failed_components": ["span_processor"],
                "total_components": 3,
                "success_rate": "2/3",
            },
        )

    @patch("honeyhive.tracer.lifecycle.flush.safe_log")
    def test_log_flush_results_test_mode(
        self, mock_safe_log: Mock, mock_tracer: Mock
    ) -> None:
        """Test logging in test mode (should not log)."""
        # Setup
        mock_tracer.test_mode = True
        flush_results = [("provider", True)]

        # Execute
        _log_flush_results(mock_tracer, True, flush_results)

        # Verify - this tests line 277
        mock_safe_log.assert_not_called()

"""
Unit tests for error handling and resilience.
"""

import logging
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from honeyhive.tracer.error_handler import (
    ErrorContext,
    ErrorHandler,
    ErrorSeverity,
    ExportError,
    FallbackMode,
    InitializationError,
    IntegrationError,
    ProviderIncompatibleError,
    RetryStrategy,
    SpanProcessingError,
    handle_export_error,
    handle_initialization_error,
    handle_provider_error,
    handle_span_processing_error,
    with_error_handling,
    with_retry,
)


class TestIntegrationErrors:
    """Test custom exception classes."""

    def test_integration_error_basic(self):
        """Test basic IntegrationError functionality."""
        error = IntegrationError("Test error", "TEST_CODE", {"key": "value"})

        assert str(error) == "Test error"
        assert error.error_code == "TEST_CODE"
        assert error.details == {"key": "value"}
        assert error.timestamp > 0

    def test_provider_incompatible_error(self):
        """Test ProviderIncompatibleError."""
        error = ProviderIncompatibleError("TestProvider", ["operation1", "operation2"])

        assert "TestProvider" in str(error)
        assert "operation1" in str(error)
        assert error.error_code == "PROVIDER_INCOMPATIBLE"
        assert error.details["provider_type"] == "TestProvider"
        assert error.details["required_operations"] == ["operation1", "operation2"]

    def test_initialization_error(self):
        """Test InitializationError."""
        cause = ValueError("Original error")
        error = InitializationError("Init failed", cause)

        assert "Init failed" in str(error)
        assert error.error_code == "INITIALIZATION_ERROR"
        assert "Original error" in error.details["cause"]

    def test_span_processing_error(self):
        """Test SpanProcessingError."""
        cause = RuntimeError("Processing failed")
        error = SpanProcessingError("test_span", cause)

        assert "test_span" in str(error)
        assert error.error_code == "SPAN_PROCESSING_ERROR"
        assert error.details["span_name"] == "test_span"

    def test_export_error(self):
        """Test ExportError."""
        cause = ConnectionError("Network error")
        error = ExportError("OTLP", cause)

        assert "OTLP" in str(error)
        assert error.error_code == "EXPORT_ERROR"
        assert error.details["export_type"] == "OTLP"


class TestRetryStrategy:
    """Test retry strategy functionality."""

    def test_retry_strategy_initialization(self):
        """Test RetryStrategy initialization."""
        strategy = RetryStrategy(max_retries=5, base_delay=2.0, backoff_factor=3.0)

        assert strategy.max_retries == 5
        assert strategy.base_delay == 2.0
        assert strategy.backoff_factor == 3.0

    def test_should_retry_logic(self):
        """Test retry decision logic."""
        strategy = RetryStrategy(max_retries=3)

        # Should retry for generic exceptions
        assert strategy.should_retry(0, RuntimeError("Test"))
        assert strategy.should_retry(1, ValueError("Test"))
        assert strategy.should_retry(2, Exception("Test"))

        # Should not retry after max attempts
        assert not strategy.should_retry(3, RuntimeError("Test"))
        assert not strategy.should_retry(5, ValueError("Test"))

        # Should not retry for certain error types
        assert not strategy.should_retry(0, ProviderIncompatibleError("Test", []))
        assert not strategy.should_retry(1, InitializationError("Test"))

    def test_delay_calculation(self):
        """Test delay calculation with exponential backoff."""
        strategy = RetryStrategy(base_delay=1.0, backoff_factor=2.0, max_delay=10.0)

        assert strategy.get_delay(0) == 1.0
        assert strategy.get_delay(1) == 2.0
        assert strategy.get_delay(2) == 4.0
        assert strategy.get_delay(3) == 8.0
        assert strategy.get_delay(4) == 10.0  # Capped at max_delay

    def test_execute_with_retry_success(self):
        """Test successful execution with retry."""
        strategy = RetryStrategy(max_retries=3)

        mock_func = Mock(return_value="success")
        result = strategy.execute_with_retry(mock_func, "arg1", kwarg1="value1")

        assert result == "success"
        mock_func.assert_called_once_with("arg1", kwarg1="value1")

    def test_execute_with_retry_eventual_success(self):
        """Test eventual success after retries."""
        strategy = RetryStrategy(max_retries=3, base_delay=0.01)  # Fast for testing

        mock_func = Mock(
            side_effect=[RuntimeError("Fail"), RuntimeError("Fail"), "success"]
        )

        with patch("time.sleep"):  # Mock sleep to speed up test
            result = strategy.execute_with_retry(mock_func)

        assert result == "success"
        assert mock_func.call_count == 3

    def test_execute_with_retry_max_retries_exceeded(self):
        """Test failure after max retries."""
        strategy = RetryStrategy(max_retries=2, base_delay=0.01)

        mock_func = Mock(side_effect=RuntimeError("Always fail"))

        with patch("time.sleep"):
            with pytest.raises(RuntimeError, match="Always fail"):
                strategy.execute_with_retry(mock_func)

        assert mock_func.call_count == 3  # Initial + 2 retries

    def test_execute_with_retry_no_retry_error(self):
        """Test no retry for certain error types."""
        strategy = RetryStrategy(max_retries=3)

        mock_func = Mock(side_effect=ProviderIncompatibleError("Test", []))

        with pytest.raises(ProviderIncompatibleError):
            strategy.execute_with_retry(mock_func)

        mock_func.assert_called_once()  # No retries


class TestErrorHandler:
    """Test ErrorHandler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Mock(spec=logging.Logger)
        self.error_handler = ErrorHandler(self.logger)

    def test_error_handler_initialization(self):
        """Test ErrorHandler initialization."""
        handler = ErrorHandler()

        assert handler.logger is not None
        assert isinstance(handler.retry_strategy, RetryStrategy)
        assert handler.error_counts == {}
        assert not handler.fallback_active

    def test_handle_integration_failure_logging(self):
        """Test error logging in handle_integration_failure."""
        context = ErrorContext(
            operation="test_operation",
            component="test_component",
            severity=ErrorSeverity.HIGH,
            fallback_mode=FallbackMode.NO_OP,
        )

        error = IntegrationError("Test error", "TEST_CODE")

        result = self.error_handler.handle_integration_failure(error, context)

        # Check logging
        self.logger.error.assert_called_once()
        call_args = self.logger.error.call_args
        assert "Integration failure" in call_args[0][0]
        assert "test_component.test_operation" in call_args[0][0]

        # Check error counting
        assert self.error_handler.error_counts["test_component.test_operation"] == 1

        # Check result
        assert result["fallback_mode"] == "no_op"

    def test_console_logging_fallback(self):
        """Test console logging fallback."""
        context = ErrorContext(
            operation="test_op",
            component="test_comp",
            severity=ErrorSeverity.MEDIUM,
            fallback_mode=FallbackMode.CONSOLE_LOGGING,
        )

        error = RuntimeError("Test error")
        result = self.error_handler.handle_integration_failure(error, context)

        assert result["fallback_mode"] == "console_logging"
        assert "logger" in result
        assert self.error_handler.fallback_active

    def test_no_op_fallback(self):
        """Test no-op fallback."""
        context = ErrorContext(
            operation="test_op",
            component="test_comp",
            severity=ErrorSeverity.LOW,
            fallback_mode=FallbackMode.NO_OP,
        )

        error = ValueError("Test error")
        result = self.error_handler.handle_integration_failure(error, context)

        assert result["fallback_mode"] == "no_op"
        assert result["operation"] == "disabled"
        assert self.error_handler.fallback_active

    def test_partial_integration_fallback(self):
        """Test partial integration fallback."""
        context = ErrorContext(
            operation="span_processing",
            component="span_processor",
            severity=ErrorSeverity.MEDIUM,
            fallback_mode=FallbackMode.PARTIAL_INTEGRATION,
        )

        error = SpanProcessingError("test_span")
        result = self.error_handler.handle_integration_failure(error, context)

        assert result["fallback_mode"] == "partial_integration"
        assert "disabled_features" in result
        assert "enabled_features" in result
        assert "honeyhive_export" in result["disabled_features"]
        assert "local_logging" in result["enabled_features"]

    def test_graceful_degradation_fallback(self):
        """Test graceful degradation fallback."""
        context = ErrorContext(
            operation="test_op",
            component="test_comp",
            severity=ErrorSeverity.HIGH,
            fallback_mode=FallbackMode.GRACEFUL_DEGRADATION,
        )

        error = ExportError("OTLP")

        with patch.object(
            self.error_handler, "_schedule_background_retry"
        ) as mock_schedule:
            result = self.error_handler.handle_integration_failure(error, context)

        assert result["fallback_mode"] == "graceful_degradation"
        assert result["reduced_functionality"] is True
        assert result["background_retry"] is True
        mock_schedule.assert_called_once_with(context)

    def test_health_check_too_recent(self):
        """Test health check skipped when too recent."""
        self.error_handler.last_health_check = time.time()

        result = self.error_handler.perform_health_check()

        assert result["status"] == "skipped"
        assert result["reason"] == "too_recent"

    def test_health_check_no_fallback(self):
        """Test health check when not in fallback mode."""
        self.error_handler.last_health_check = 0  # Force health check

        result = self.error_handler.perform_health_check()

        assert result["fallback_active"] is False
        assert result["recovery_attempted"] is False

    def test_health_check_with_recovery(self):
        """Test health check with recovery attempt."""
        self.error_handler.last_health_check = 0
        self.error_handler.fallback_active = True

        with patch.object(
            self.error_handler, "_attempt_recovery", return_value=True
        ) as mock_recovery:
            result = self.error_handler.perform_health_check()

        assert result["recovery_attempted"] is True
        assert result["recovery_successful"] is True
        assert not self.error_handler.fallback_active
        mock_recovery.assert_called_once()

    def test_recovery_attempt_success(self):
        """Test successful recovery attempt."""
        with patch("honeyhive.tracer.error_handler.trace") as mock_trace:
            mock_provider = Mock()
            mock_tracer = Mock()
            mock_span = Mock()

            mock_trace.get_tracer_provider.return_value = mock_provider
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
                return_value=mock_span
            )
            mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
                return_value=None
            )

            result = self.error_handler._attempt_recovery()

        assert result is True
        mock_span.set_attribute.assert_called_once_with("recovery.test", True)

    def test_recovery_attempt_failure(self):
        """Test failed recovery attempt."""
        with patch("honeyhive.tracer.error_handler.trace") as mock_trace:
            mock_trace.get_tracer_provider.side_effect = Exception("Recovery failed")

            result = self.error_handler._attempt_recovery()

        assert result is False
        self.logger.warning.assert_called_once()

    def test_error_statistics(self):
        """Test error statistics collection."""
        # Add some errors
        self.error_handler.error_counts = {"comp1.op1": 3, "comp2.op2": 1}
        self.error_handler.fallback_active = True

        stats = self.error_handler.get_error_statistics()

        assert stats["total_errors"] == 4
        assert stats["error_breakdown"] == {"comp1.op1": 3, "comp2.op2": 1}
        assert stats["fallback_active"] is True
        assert "last_health_check" in stats
        assert "health_check_interval" in stats

    def test_reset_error_counts(self):
        """Test resetting error counts."""
        self.error_handler.error_counts = {"test": 5}
        self.error_handler.fallback_active = True

        self.error_handler.reset_error_counts()

        assert self.error_handler.error_counts == {}
        assert not self.error_handler.fallback_active


class TestDecorators:
    """Test error handling decorators."""

    def test_with_error_handling_decorator_success(self):
        """Test error handling decorator with successful function."""
        error_handler = Mock()
        context = ErrorContext(
            operation="test",
            component="test",
            severity=ErrorSeverity.LOW,
            fallback_mode=FallbackMode.NO_OP,
        )

        @with_error_handling(error_handler, context)
        def test_function(x, y):
            return x + y

        result = test_function(2, 3)

        assert result == 5
        error_handler.handle_integration_failure.assert_not_called()

    def test_with_error_handling_decorator_error(self):
        """Test error handling decorator with function error."""
        error_handler = Mock()
        error_handler.handle_integration_failure.return_value = "fallback_result"

        context = ErrorContext(
            operation="test",
            component="test",
            severity=ErrorSeverity.HIGH,
            fallback_mode=FallbackMode.CONSOLE_LOGGING,
        )

        @with_error_handling(error_handler, context)
        def test_function():
            raise ValueError("Test error")

        result = test_function()

        assert result == "fallback_result"
        error_handler.handle_integration_failure.assert_called_once()

        # Check that the error was passed correctly
        call_args = error_handler.handle_integration_failure.call_args
        assert isinstance(call_args[0][0], ValueError)
        assert call_args[0][1] == context

    def test_with_retry_decorator_success(self):
        """Test retry decorator with successful function."""

        @with_retry()
        def test_function(x):
            return x * 2

        result = test_function(5)
        assert result == 10

    def test_with_retry_decorator_with_custom_strategy(self):
        """Test retry decorator with custom strategy."""
        strategy = RetryStrategy(max_retries=1, base_delay=0.01)

        @with_retry(strategy)
        def test_function():
            raise RuntimeError("Always fail")

        with patch("time.sleep"):
            with pytest.raises(RuntimeError):
                test_function()


class TestConvenienceFunctions:
    """Test convenience functions for common error patterns."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset global error handler
        from honeyhive.tracer.error_handler import (
            ErrorHandler,
            set_global_error_handler,
        )

        set_global_error_handler(ErrorHandler(Mock(spec=logging.Logger)))

    def test_handle_provider_error(self):
        """Test provider error handling convenience function."""
        error = ProviderIncompatibleError("TestProvider", ["operation1"])

        with patch(
            "honeyhive.tracer.error_handler.get_global_error_handler"
        ) as mock_get_handler:
            mock_handler = Mock()
            mock_handler.handle_integration_failure.return_value = "handled"
            mock_get_handler.return_value = mock_handler

            result = handle_provider_error(error, "TestProvider")

        assert result == "handled"
        mock_handler.handle_integration_failure.assert_called_once()

        # Check context
        call_args = mock_handler.handle_integration_failure.call_args
        context = call_args[0][1]
        assert context.operation == "provider_integration"
        assert context.component == "provider_detector"
        assert context.severity == ErrorSeverity.HIGH
        assert context.fallback_mode == FallbackMode.GRACEFUL_DEGRADATION

    def test_handle_span_processing_error(self):
        """Test span processing error handling convenience function."""
        error = SpanProcessingError("test_span")

        with patch(
            "honeyhive.tracer.error_handler.get_global_error_handler"
        ) as mock_get_handler:
            mock_handler = Mock()
            mock_handler.handle_integration_failure.return_value = "handled"
            mock_get_handler.return_value = mock_handler

            result = handle_span_processing_error(error, "test_span")

        assert result == "handled"

        # Check context
        call_args = mock_handler.handle_integration_failure.call_args
        context = call_args[0][1]
        assert context.operation == "span_processing"
        assert context.severity == ErrorSeverity.MEDIUM
        assert context.fallback_mode == FallbackMode.PARTIAL_INTEGRATION

    def test_handle_export_error(self):
        """Test export error handling convenience function."""
        error = ExportError("OTLP")

        with patch(
            "honeyhive.tracer.error_handler.get_global_error_handler"
        ) as mock_get_handler:
            mock_handler = Mock()
            mock_handler.handle_integration_failure.return_value = "handled"
            mock_get_handler.return_value = mock_handler

            result = handle_export_error(error, "OTLP")

        assert result == "handled"

        # Check context
        call_args = mock_handler.handle_integration_failure.call_args
        context = call_args[0][1]
        assert context.operation == "span_export"
        assert context.severity == ErrorSeverity.MEDIUM
        assert context.fallback_mode == FallbackMode.CONSOLE_LOGGING

    def test_handle_initialization_error(self):
        """Test initialization error handling convenience function."""
        error = InitializationError("Init failed")

        with patch(
            "honeyhive.tracer.error_handler.get_global_error_handler"
        ) as mock_get_handler:
            mock_handler = Mock()
            mock_handler.handle_integration_failure.return_value = "handled"
            mock_get_handler.return_value = mock_handler

            result = handle_initialization_error(error, "tracer")

        assert result == "handled"

        # Check context
        call_args = mock_handler.handle_integration_failure.call_args
        context = call_args[0][1]
        assert context.operation == "initialization"
        assert context.component == "tracer"
        assert context.severity == ErrorSeverity.CRITICAL
        assert context.fallback_mode == FallbackMode.NO_OP

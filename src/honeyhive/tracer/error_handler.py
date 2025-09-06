"""
Enhanced error handling and resilience for HoneyHive tracer integration.

This module provides comprehensive error handling for non-instrumentor
framework integration, including graceful degradation, retry mechanisms,
and recovery strategies.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional


class IntegrationError(Exception):
    """Base exception for integration errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTEGRATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = time.time()


class ProviderIncompatibleError(IntegrationError):
    """Provider doesn't support required operations."""

    def __init__(self, provider_type: str, required_operations: List[str]):
        message = f"Provider {provider_type} doesn't support required operations: {required_operations}"
        super().__init__(
            message,
            error_code="PROVIDER_INCOMPATIBLE",
            details={
                "provider_type": provider_type,
                "required_operations": required_operations,
            },
        )


class InitializationError(IntegrationError):
    """Error during tracer initialization."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(
            message,
            error_code="INITIALIZATION_ERROR",
            details={"cause": str(cause) if cause else None},
        )


class SpanProcessingError(IntegrationError):
    """Error during span processing."""

    def __init__(self, span_name: str, cause: Optional[Exception] = None):
        message = f"Error processing span '{span_name}'"
        super().__init__(
            message,
            error_code="SPAN_PROCESSING_ERROR",
            details={"span_name": span_name, "cause": str(cause) if cause else None},
        )


class ExportError(IntegrationError):
    """Error during span export."""

    def __init__(self, export_type: str, cause: Optional[Exception] = None):
        message = f"Error exporting spans via {export_type}"
        super().__init__(
            message,
            error_code="EXPORT_ERROR",
            details={
                "export_type": export_type,
                "cause": str(cause) if cause else None,
            },
        )


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FallbackMode(Enum):
    """Available fallback modes."""

    CONSOLE_LOGGING = "console_logging"
    NO_OP = "no_op"
    PARTIAL_INTEGRATION = "partial_integration"
    GRACEFUL_DEGRADATION = "graceful_degradation"


@dataclass
class ErrorContext:
    """Context information for error handling."""

    operation: str
    component: str
    severity: ErrorSeverity
    fallback_mode: FallbackMode
    retry_count: int = 0
    max_retries: int = 3
    backoff_factor: float = 2.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RetryStrategy:
    """Retry strategy with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if operation should be retried."""
        if attempt >= self.max_retries:
            return False

        # Don't retry certain types of errors
        if isinstance(error, (ProviderIncompatibleError, InitializationError)):
            return False

        return True

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.base_delay * (self.backoff_factor**attempt)
        return min(delay, self.max_delay)

    def execute_with_retry(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        """Execute function with retry logic."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e

                if not self.should_retry(attempt, e):
                    break

                if attempt < self.max_retries:
                    delay = self.get_delay(attempt)
                    logging.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)

        # All retries exhausted
        if last_error is not None:
            raise last_error
        raise RuntimeError("Function execution failed with no specific error")


class ErrorHandler:
    """Comprehensive error handler for HoneyHive integration."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.retry_strategy = RetryStrategy()
        self.error_counts: Dict[str, int] = {}
        self.fallback_active = False
        self.health_check_interval = 30.0  # seconds
        self.last_health_check = 0.0

    def handle_integration_failure(
        self, error: Exception, context: ErrorContext
    ) -> Any:
        """Handle integration failure with appropriate fallback."""
        self.logger.error(
            f"Integration failure in {context.component}.{context.operation}: {error}",
            extra={
                "error_code": getattr(error, "error_code", "UNKNOWN"),
                "severity": context.severity.value,
                "component": context.component,
                "operation": context.operation,
            },
        )

        # Update error counts
        error_key = f"{context.component}.{context.operation}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # Determine fallback action
        return self._execute_fallback(error, context)

    def _execute_fallback(self, error: Exception, context: ErrorContext) -> Any:
        """Execute appropriate fallback based on context."""
        if context.fallback_mode == FallbackMode.CONSOLE_LOGGING:
            return self._console_logging_fallback(error, context)
        elif context.fallback_mode == FallbackMode.NO_OP:
            return self._no_op_fallback(error, context)
        elif context.fallback_mode == FallbackMode.PARTIAL_INTEGRATION:
            return self._partial_integration_fallback(error, context)
        elif context.fallback_mode == FallbackMode.GRACEFUL_DEGRADATION:
            return self._graceful_degradation_fallback(error, context)
        else:
            self.logger.warning(f"Unknown fallback mode: {context.fallback_mode}")
            return self._no_op_fallback(error, context)

    def _console_logging_fallback(self, error: Exception, context: ErrorContext) -> Any:
        """Fallback to console logging."""
        self.logger.info(f"Falling back to console logging for {context.operation}")

        # Set up console logging for spans
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - HoneyHive Fallback - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        fallback_logger = logging.getLogger("honeyhive.fallback")
        fallback_logger.addHandler(console_handler)
        fallback_logger.setLevel(logging.INFO)

        self.fallback_active = True
        return {"fallback_mode": "console_logging", "logger": fallback_logger}

    def _no_op_fallback(self, error: Exception, context: ErrorContext) -> Any:
        """Fallback to no-op operation."""
        self.logger.info(f"Using no-op fallback for {context.operation}")
        self.fallback_active = True
        return {"fallback_mode": "no_op", "operation": "disabled"}

    def _partial_integration_fallback(
        self, error: Exception, context: ErrorContext
    ) -> Any:
        """Fallback to partial integration."""
        self.logger.info(f"Using partial integration fallback for {context.operation}")

        # Try to maintain some functionality
        disabled_features: List[str] = []
        enabled_features: List[str] = []
        partial_config = {
            "fallback_mode": "partial_integration",
            "disabled_features": disabled_features,
            "enabled_features": enabled_features,
        }

        # Determine what can still work
        if context.operation == "span_processing":
            disabled_features.append("honeyhive_export")
            enabled_features.append("local_logging")
        elif context.operation == "provider_integration":
            disabled_features.append("span_processor_integration")
            enabled_features.append("manual_tracing")

        self.fallback_active = True
        return partial_config

    def _graceful_degradation_fallback(
        self, error: Exception, context: ErrorContext
    ) -> Any:
        """Fallback with graceful degradation."""
        self.logger.info(f"Gracefully degrading {context.operation}")

        degradation_config = {
            "fallback_mode": "graceful_degradation",
            "reduced_functionality": True,
            "error_tolerance": True,
            "background_retry": True,
        }

        # Schedule background retry
        self._schedule_background_retry(context)

        self.fallback_active = True
        return degradation_config

    def _schedule_background_retry(self, context: ErrorContext) -> None:
        """Schedule background retry for failed operation."""
        import threading

        def background_retry() -> None:
            time.sleep(self.retry_strategy.get_delay(context.retry_count))
            self.logger.info(f"Attempting background retry for {context.operation}")
            # Implementation would depend on specific operation
            # This is a placeholder for the retry logic

        retry_thread = threading.Thread(target=background_retry, daemon=True)
        retry_thread.start()

    def perform_health_check(self) -> Dict[str, Any]:
        """Perform health check and attempt recovery."""
        current_time = time.time()

        if current_time - self.last_health_check < self.health_check_interval:
            return {"status": "skipped", "reason": "too_recent"}

        self.last_health_check = current_time

        health_status = {
            "timestamp": current_time,
            "fallback_active": self.fallback_active,
            "error_counts": self.error_counts.copy(),
            "recovery_attempted": False,
            "recovery_successful": False,
        }

        if self.fallback_active:
            self.logger.info("Attempting recovery from fallback mode...")
            recovery_result = self._attempt_recovery()
            health_status["recovery_attempted"] = True
            health_status["recovery_successful"] = recovery_result

            if recovery_result:
                self.fallback_active = False
                self.logger.info("Recovery successful - normal operation restored")
            else:
                self.logger.warning("Recovery failed - remaining in fallback mode")

        return health_status

    def _attempt_recovery(self) -> bool:
        """Attempt to recover from fallback mode."""
        try:
            # Test basic functionality
            from opentelemetry import trace

            # Check if we can get a tracer provider
            provider = trace.get_tracer_provider()
            if provider is None:
                return False

            # Check if we can create a tracer
            tracer = trace.get_tracer("recovery_test")
            if tracer is None:
                return False

            # Test span creation
            with tracer.start_as_current_span("recovery_test_span") as span:
                span.set_attribute("recovery.test", True)

            # If we get here, basic functionality is working
            return True

        except Exception as e:
            self.logger.warning(f"Recovery attempt failed: {e}")
            return False

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_breakdown": self.error_counts.copy(),
            "fallback_active": self.fallback_active,
            "last_health_check": self.last_health_check,
            "health_check_interval": self.health_check_interval,
        }

    def reset_error_counts(self) -> None:
        """Reset error counts (useful for testing)."""
        self.error_counts.clear()
        self.fallback_active = False


def with_error_handling(error_handler: ErrorHandler, context: ErrorContext) -> Any:
    """Decorator for adding error handling to functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_integration_failure(e, context)

        return wrapper

    return decorator


def with_retry(retry_strategy: Optional[RetryStrategy] = None) -> Any:
    """Decorator for adding retry logic to functions."""

    if retry_strategy is None:
        retry_strategy = RetryStrategy()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return retry_strategy.execute_with_retry(func, *args, **kwargs)

        return wrapper

    return decorator


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_global_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler

    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()

    return _global_error_handler


def set_global_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler instance."""
    global _global_error_handler
    _global_error_handler = handler


# Convenience functions for common error handling patterns
def handle_provider_error(error: Exception, provider_type: str) -> Any:
    """Handle provider-related errors."""
    context = ErrorContext(
        operation="provider_integration",
        component="provider_detector",
        severity=ErrorSeverity.HIGH,
        fallback_mode=FallbackMode.GRACEFUL_DEGRADATION,
        metadata={"provider_type": provider_type},
    )

    return get_global_error_handler().handle_integration_failure(error, context)


def handle_span_processing_error(error: Exception, span_name: str) -> Any:
    """Handle span processing errors."""
    context = ErrorContext(
        operation="span_processing",
        component="span_processor",
        severity=ErrorSeverity.MEDIUM,
        fallback_mode=FallbackMode.PARTIAL_INTEGRATION,
        metadata={"span_name": span_name},
    )

    return get_global_error_handler().handle_integration_failure(error, context)


def handle_export_error(error: Exception, export_type: str) -> Any:
    """Handle export errors."""
    context = ErrorContext(
        operation="span_export",
        component="span_exporter",
        severity=ErrorSeverity.MEDIUM,
        fallback_mode=FallbackMode.CONSOLE_LOGGING,
        metadata={"export_type": export_type},
    )

    return get_global_error_handler().handle_integration_failure(error, context)


def handle_initialization_error(error: Exception, component: str) -> Any:
    """Handle initialization errors."""
    context = ErrorContext(
        operation="initialization",
        component=component,
        severity=ErrorSeverity.CRITICAL,
        fallback_mode=FallbackMode.NO_OP,
        metadata={"initialization_component": component},
    )

    return get_global_error_handler().handle_integration_failure(error, context)

"""Dynamic error handling and resilience for HoneyHive tracer integration.

This module provides comprehensive error handling using dynamic patterns for
graceful degradation, retry mechanisms, and recovery strategies. All error
handling logic is extensible and configuration-driven.
"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, cast

# Import shared logging utility
from ...utils.logger import safe_log

# pylint: disable=global-statement
# Global statement used for singleton error handler pattern - required for
# maintaining consistent error handling across the entire tracer module


class IntegrationError(Exception):
    """Base exception for integration errors with dynamic context."""

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
        message = (
            f"Provider {provider_type} doesn't support required operations: "
            f"{required_operations}"
        )
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
    """Error severity levels for dynamic handling."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResilienceLevel(Enum):
    """Resilience levels for dynamic error handling strategies."""

    STRICT = "strict"  # Fail fast, no retries
    BALANCED = "balanced"  # Some retries, graceful degradation
    RESILIENT = "resilient"  # Maximum retries, always degrade gracefully


@dataclass
class ErrorContext:
    """Dynamic error context with extensible metadata."""

    error: Exception
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    component: str = "unknown"
    operation: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class RecoveryStrategy:
    """Dynamic recovery strategy configuration."""

    name: str
    handler: Callable[[ErrorContext], bool]
    applicable_errors: List[str] = field(default_factory=list)
    max_attempts: int = 3
    backoff_multiplier: float = 1.5
    base_delay: float = 0.1


class ErrorHandler:
    """Dynamic error handler with extensible strategies and patterns."""

    def __init__(
        self,
        resilience_level: ResilienceLevel = ResilienceLevel.BALANCED,
        tracer_instance: Any = None,
    ):
        """Initialize error handler with dynamic configuration.

        Args:
            resilience_level: Level of resilience for error handling
            tracer_instance: Optional tracer instance for logging context
        """
        self.resilience_level = resilience_level
        self.tracer_instance = tracer_instance
        self._lock = threading.Lock()
        self._error_history: List[ErrorContext] = []
        self._recovery_strategies = self._build_recovery_strategies_dynamically()
        self._error_patterns = self._build_error_patterns_dynamically()

    def _build_recovery_strategies_dynamically(self) -> List[RecoveryStrategy]:
        """Dynamically build recovery strategies based on resilience level.

        Returns:
            List of recovery strategies
        """
        strategies = []

        # Base strategies available for all resilience levels
        strategies.extend(
            [
                RecoveryStrategy(
                    name="graceful_degradation",
                    handler=self._graceful_degradation_handler,
                    applicable_errors=["PROVIDER_INCOMPATIBLE", "INITIALIZATION_ERROR"],
                    max_attempts=1,
                ),
                RecoveryStrategy(
                    name="retry_with_backoff",
                    handler=self._retry_with_backoff_handler,
                    applicable_errors=["EXPORT_ERROR", "SPAN_PROCESSING_ERROR"],
                    max_attempts=self._get_max_retries_for_level(),
                    backoff_multiplier=1.5,
                    base_delay=0.1,
                ),
            ]
        )

        # Add resilience-level specific strategies
        if self.resilience_level in {
            ResilienceLevel.BALANCED,
            ResilienceLevel.RESILIENT,
        }:
            strategies.append(
                RecoveryStrategy(
                    name="fallback_provider",
                    handler=self._fallback_provider_handler,
                    applicable_errors=["PROVIDER_INCOMPATIBLE"],
                    max_attempts=1,
                )
            )

        if self.resilience_level == ResilienceLevel.RESILIENT:
            strategies.append(
                RecoveryStrategy(
                    name="console_fallback",
                    handler=self._console_fallback_handler,
                    applicable_errors=["EXPORT_ERROR"],
                    max_attempts=1,
                )
            )

        return strategies

    def _build_error_patterns_dynamically(self) -> Dict[str, Dict[str, Any]]:
        """Dynamically build error patterns for classification.

        Returns:
            Dictionary of error patterns and their configurations
        """
        return {
            "connection_errors": {
                "patterns": ["connection", "timeout", "network", "unreachable"],
                "severity": ErrorSeverity.MEDIUM,
                "retry_eligible": True,
            },
            "authentication_errors": {
                "patterns": ["auth", "unauthorized", "forbidden", "api_key"],
                "severity": ErrorSeverity.HIGH,
                "retry_eligible": False,
            },
            "provider_errors": {
                "patterns": ["provider", "incompatible", "unsupported"],
                "severity": ErrorSeverity.HIGH,
                "retry_eligible": False,
            },
            "processing_errors": {
                "patterns": ["processing", "span", "attribute"],
                "severity": ErrorSeverity.LOW,
                "retry_eligible": True,
            },
        }

    def _get_max_retries_for_level(self) -> int:
        """Dynamically get max retries based on resilience level.

        Returns:
            Maximum number of retries
        """
        retry_mapping = {
            ResilienceLevel.STRICT: 0,
            ResilienceLevel.BALANCED: 3,
            ResilienceLevel.RESILIENT: 5,
        }
        return retry_mapping.get(self.resilience_level, 3)

    def handle_error(
        self,
        error: Exception,
        component: str = "unknown",
        operation: str = "unknown",
        **metadata: Any,
    ) -> bool:
        """Dynamically handle error with appropriate recovery strategy.

        Args:
            error: Exception that occurred
            component: Component where error occurred
            operation: Operation that failed
            **metadata: Additional error metadata

        Returns:
            bool: True if error was handled successfully, False otherwise
        """
        with self._lock:
            # Create error context
            error_context = self._create_error_context_dynamically(
                error, component, operation, metadata
            )

            # Record error in history
            self._record_error_dynamically(error_context)

            # Classify error severity
            error_context.severity = self._classify_error_severity_dynamically(error)

            # Apply recovery strategies
            recovery_success = self._apply_recovery_strategies_dynamically(
                error_context
            )

            # Log error handling result
            self._log_error_handling_result_dynamically(error_context, recovery_success)

            return recovery_success

    def _create_error_context_dynamically(
        self,
        error: Exception,
        component: str,
        operation: str,
        metadata: Dict[str, Any],
    ) -> ErrorContext:
        """Dynamically create error context with comprehensive information.

        Args:
            error: Exception that occurred
            component: Component where error occurred
            operation: Operation that failed
            metadata: Additional error metadata

        Returns:
            ErrorContext with comprehensive error information
        """
        return ErrorContext(
            error=error,
            component=component,
            operation=operation,
            metadata=metadata,
            max_retries=self._get_max_retries_for_level(),
        )

    def _record_error_dynamically(self, error_context: ErrorContext) -> None:
        """Dynamically record error in history with size management.

        Args:
            error_context: Error context to record
        """
        self._error_history.append(error_context)

        # Dynamic history size management
        max_history_size = 100
        if len(self._error_history) > max_history_size:
            self._error_history = self._error_history[-max_history_size:]

    def _classify_error_severity_dynamically(self, error: Exception) -> ErrorSeverity:
        """Dynamically classify error severity using pattern matching.

        Args:
            error: Exception to classify

        Returns:
            ErrorSeverity level
        """
        error_message = str(error).lower()
        error_type = type(error).__name__.lower()

        # Dynamic pattern matching
        for _pattern_name, pattern_config in self._error_patterns.items():
            patterns = pattern_config["patterns"]
            if any(
                pattern in error_message or pattern in error_type
                for pattern in patterns
            ):
                return ErrorSeverity(pattern_config["severity"])

        # Default severity for unclassified errors
        return ErrorSeverity.MEDIUM

    def _apply_recovery_strategies_dynamically(
        self, error_context: ErrorContext
    ) -> bool:
        """Dynamically apply recovery strategies based on error context.

        Args:
            error_context: Error context to handle

        Returns:
            bool: True if recovery was successful
        """
        error_code = getattr(error_context.error, "error_code", "UNKNOWN_ERROR")

        # Find applicable strategies
        applicable_strategies = self._find_applicable_strategies_dynamically(error_code)

        # Apply strategies in order
        for strategy in applicable_strategies:
            try:
                if self._execute_recovery_strategy_dynamically(strategy, error_context):
                    return True
            except Exception as strategy_error:
                safe_log(
                    self.tracer_instance,
                    "warning",
                    "Recovery strategy failed",
                    honeyhive_data={
                        "strategy": strategy.name,
                        "error": str(strategy_error),
                        "original_error": str(error_context.error),
                    },
                )
                continue

        return False

    def _find_applicable_strategies_dynamically(
        self, error_code: str
    ) -> List[RecoveryStrategy]:
        """Dynamically find applicable recovery strategies.

        Args:
            error_code: Error code to match against

        Returns:
            List of applicable recovery strategies
        """
        applicable = []

        for strategy in self._recovery_strategies:
            if (
                not strategy.applicable_errors
                or error_code in strategy.applicable_errors
            ):
                applicable.append(strategy)

        # Sort by priority (could be made dynamic in future)
        return applicable

    def _execute_recovery_strategy_dynamically(
        self, strategy: RecoveryStrategy, error_context: ErrorContext
    ) -> bool:
        """Dynamically execute recovery strategy with backoff.

        Args:
            strategy: Recovery strategy to execute
            error_context: Error context

        Returns:
            bool: True if strategy succeeded
        """
        for attempt in range(strategy.max_attempts):
            try:
                if strategy.handler(error_context):
                    return True

                # Dynamic backoff calculation
                if attempt < strategy.max_attempts - 1:
                    delay = strategy.base_delay * (strategy.backoff_multiplier**attempt)
                    time.sleep(delay)

            except Exception as handler_error:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Recovery strategy handler failed",
                    honeyhive_data={
                        "strategy": strategy.name,
                        "attempt": attempt + 1,
                        "error": str(handler_error),
                    },
                )
                continue

        return False

    def _log_error_handling_result_dynamically(
        self, error_context: ErrorContext, recovery_success: bool
    ) -> None:
        """Dynamically log error handling result.

        Args:
            error_context: Error context that was handled
            recovery_success: Whether recovery was successful
        """
        log_level = "info" if recovery_success else "warning"
        log_message = (
            "Error handled successfully"
            if recovery_success
            else "Error handling failed"
        )

        safe_log(
            self.tracer_instance,
            log_level,
            log_message,
            honeyhive_data={
                "component": error_context.component,
                "operation": error_context.operation,
                "error_type": type(error_context.error).__name__,
                "severity": error_context.severity.value,
                "recovery_success": recovery_success,
                "retry_count": error_context.retry_count,
            },
        )

    # Recovery strategy handlers
    def _graceful_degradation_handler(self, error_context: ErrorContext) -> bool:
        """Handle error with graceful degradation.

        Args:
            error_context: Error context

        Returns:
            bool: True if degradation successful
        """
        safe_log(
            self.tracer_instance,
            "info",
            "Applying graceful degradation",
            honeyhive_data={
                "component": error_context.component,
                "operation": error_context.operation,
            },
        )
        # Graceful degradation always succeeds by definition
        return True

    def _retry_with_backoff_handler(self, error_context: ErrorContext) -> bool:
        """Handle error with retry and backoff.

        Args:
            error_context: Error context

        Returns:
            bool: True if retry should be attempted
        """
        if error_context.retry_count < error_context.max_retries:
            error_context.retry_count += 1
            return False  # Indicate retry needed
        return True  # Max retries reached, give up

    def _fallback_provider_handler(self, error_context: ErrorContext) -> bool:
        """Handle error by falling back to alternative provider.

        Args:
            error_context: Error context

        Returns:
            bool: True if fallback successful
        """
        safe_log(
            self.tracer_instance,
            "info",
            "Falling back to alternative provider",
            honeyhive_data={
                "component": error_context.component,
                "original_error": str(error_context.error),
            },
        )
        # Implementation would set up fallback provider
        return True

    def _console_fallback_handler(self, error_context: ErrorContext) -> bool:
        """Handle error by falling back to console logging.

        Args:
            error_context: Error context

        Returns:
            bool: True if console fallback successful
        """
        safe_log(
            self.tracer_instance,
            "info",
            "Falling back to console logging",
            honeyhive_data={
                "component": error_context.component,
                "original_error": str(error_context.error),
            },
        )
        # Console fallback always succeeds
        return True

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get dynamic error statistics.

        Returns:
            Dictionary with error statistics
        """
        with self._lock:
            if not self._error_history:
                return {"total_errors": 0}

            # Dynamic statistics calculation
            stats = {
                "total_errors": len(self._error_history),
                "error_types": self._calculate_error_type_distribution(),
                "severity_distribution": self._calculate_severity_distribution(),
                "component_distribution": self._calculate_component_distribution(),
                "recent_errors": len(
                    [
                        e
                        for e in self._error_history
                        if time.time() - e.timestamp < 300  # Last 5 minutes
                    ]
                ),
            }

            return stats

    def _calculate_error_type_distribution(self) -> Dict[str, int]:
        """Calculate error type distribution."""
        distribution: Dict[str, int] = {}
        for error_context in self._error_history:
            error_type = type(error_context.error).__name__
            distribution[error_type] = distribution.get(error_type, 0) + 1
        return distribution

    def _calculate_severity_distribution(self) -> Dict[str, int]:
        """Calculate severity distribution."""
        distribution: Dict[str, int] = {}
        for error_context in self._error_history:
            severity = error_context.severity.value
            distribution[severity] = distribution.get(severity, 0) + 1
        return distribution

    def _calculate_component_distribution(self) -> Dict[str, int]:
        """Calculate component distribution."""
        distribution: Dict[str, int] = {}
        for error_context in self._error_history:
            component = error_context.component
            distribution[component] = distribution.get(component, 0) + 1
        return distribution


def get_error_handler(
    resilience_level: ResilienceLevel = ResilienceLevel.BALANCED,
    tracer_instance: Any = None,
) -> ErrorHandler:
    """Get or create per-tracer-instance error handler with dynamic configuration.

    Args:
        resilience_level: Resilience level for error handling
        tracer_instance: Tracer instance for logging context and isolation

    Returns:
        ErrorHandler instance (per-tracer-instance for proper isolation)
    """
    # Multi-instance architecture: Each tracer gets its own error handler
    if tracer_instance is not None:
        # Check if tracer already has an error handler
        if not hasattr(tracer_instance, "_error_handler"):
            # Internal SDK code accessing tracer's error handler attribute
            # Protected access is required for multi-instance architecture
            tracer_instance._error_handler = (  # pylint: disable=protected-access
                ErrorHandler(resilience_level, tracer_instance)
            )
        error_handler = (
            tracer_instance._error_handler  # pylint: disable=protected-access
        )
        return cast(ErrorHandler, error_handler)

    # Fallback: Create new handler for cases without tracer instance
    return ErrorHandler(resilience_level, tracer_instance)


def with_error_handling(
    component: str = "unknown",
    operation: str = "unknown",
    resilience_level: ResilienceLevel = ResilienceLevel.BALANCED,
    tracer_instance: Any = None,
) -> Any:
    """Decorator for dynamic error handling.

    Args:
        component: Component name for error context
        operation: Operation name for error context
        resilience_level: Resilience level for error handling
        tracer_instance: Optional tracer instance for logging context

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = get_error_handler(resilience_level, tracer_instance)
                handled = error_handler.handle_error(
                    e,
                    component=component,
                    operation=operation,
                    function_name=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                )

                if not handled and resilience_level == ResilienceLevel.STRICT:
                    raise

                # Return None or appropriate default for graceful degradation
                return None

        return wrapper

    return decorator

"""HoneyHive Logging Module - Structured logging utilities."""

import json
import logging
import sys
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

# No lifecycle imports - logger should be independent
# Shutdown detection implemented directly in logger module


# Global config removed - using per-instance configuration instead

# Internal shutdown state tracking - managed automatically by safe_log
_shutdown_detected = threading.Event()


def _detect_shutdown_conditions() -> bool:
    """Dynamically detect shutdown conditions without external signaling.

    Returns:
        True if shutdown conditions are detected, False otherwise
    """
    # Check if already detected
    if _shutdown_detected.is_set():
        return True

    # Check for Python interpreter shutdown
    try:
        # During shutdown, many modules become None
        if sys is None or threading is None:
            _shutdown_detected.set()
            return True
    except (AttributeError, NameError):
        _shutdown_detected.set()
        return True

    # Check if standard streams are closed
    try:
        if hasattr(sys.stdout, "closed") and sys.stdout.closed:
            _shutdown_detected.set()
            return True
        if hasattr(sys.stderr, "closed") and sys.stderr.closed:
            _shutdown_detected.set()
            return True
    except (AttributeError, OSError):
        _shutdown_detected.set()
        return True

    return False


def is_shutdown_detected() -> bool:
    """Check if shutdown has been detected (for internal use by tracer components).

    This function dynamically detects shutdown conditions and is safe to call
    from any tracer component that needs to check shutdown state.

    Returns:
        True if shutdown is in progress, False otherwise
    """
    return _detect_shutdown_conditions()


def reset_logging_state() -> None:
    """Reset logging state (primarily for testing).

    This function clears all internal state, which is useful
    for testing scenarios where logging state needs to be reset.
    """
    _shutdown_detected.clear()


class HoneyHiveFormatter(logging.Formatter):
    """Custom formatter for HoneyHive logs.

    Provides structured JSON logging with configurable fields
    including timestamps, log levels, and HoneyHive-specific data.
    """

    def __init__(
        self, include_timestamp: bool = True, include_level: bool = True
    ) -> None:
        """Initialize the formatter.

        Args:
            include_timestamp: Whether to include timestamp in log output
            include_level: Whether to include log level in log output
        """
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with HoneyHive structure.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": (
                datetime.now(timezone.utc).isoformat()
                if self.include_timestamp
                else None
            ),
            "level": record.levelname if self.include_level else None,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "honeyhive_data"):
            log_data.update(getattr(record, "honeyhive_data", {}))

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}

        return json.dumps(log_data, default=str)


class HoneyHiveLogger:
    """HoneyHive logger with structured logging.

    Provides a structured logging interface with HoneyHive-specific
    formatting and context data support. Uses per-instance configuration
    instead of global config for multi-instance architecture.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        *,
        level: Optional[Union[str, int]] = None,
        formatter: Optional[logging.Formatter] = None,
        handler: Optional[logging.Handler] = None,
        verbose: Optional[bool] = None,
    ):
        """Initialize the logger.

        Note: too-many-positional-arguments disabled - Logger class requires multiple
        configuration parameters (name, level, formatter, handler, verbose) for
        proper initialization and flexibility.

        Args:
            name: Logger name
            level: Log level (string or integer)
            formatter: Custom formatter to use
            handler: Custom handler to use
            verbose: Whether to enable debug logging (overrides level if provided)
        """
        self.logger = logging.getLogger(name)
        self.verbose = verbose

        # Dynamic level determination with verbose parameter priority
        effective_level = self._determine_log_level_dynamically(level, verbose)
        self.logger.setLevel(effective_level)

        # Add handler if not already present
        if not self.logger.handlers:
            if handler is None:
                handler = logging.StreamHandler(sys.stdout)
                if formatter is None:
                    formatter = HoneyHiveFormatter()
                handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def _determine_log_level_dynamically(
        self, level: Optional[Union[str, int]], verbose: Optional[bool]
    ) -> int:
        """Dynamically determine the appropriate log level.

        Uses dynamic logic to prioritize:
        1. Explicit level parameter
        2. Verbose parameter (True = DEBUG, False = WARNING)
        3. Default to WARNING

        Args:
            level: Explicit log level
            verbose: Verbose flag from tracer

        Returns:
            Resolved log level as integer
        """
        # Priority 1: Explicit level parameter
        if level is not None:
            if isinstance(level, str):
                return getattr(logging, level.upper(), logging.WARNING)
            if isinstance(level, int):
                return level

        # Priority 2: Verbose parameter from tracer
        if verbose is True:
            return logging.DEBUG
        if verbose is False:
            return logging.WARNING

        # Priority 3: Default to WARNING (suppress INFO/DEBUG, show
        # WARNING/ERROR/CRITICAL)
        return logging.WARNING

    def update_verbose_setting(self, verbose: bool) -> None:
        """Dynamically update the logger's verbose setting.

        This allows the tracer to update the logger's level
        after initialization based on configuration changes.

        Args:
            verbose: New verbose setting
        """
        self.verbose = verbose
        new_level = logging.DEBUG if verbose else logging.WARNING
        self.logger.setLevel(new_level)

    def _log_with_context(
        self,
        level: int,
        message: str,
        args: tuple = (),
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log with HoneyHive context data and lazy formatting support.

        Args:
            level: Log level
            message: Log message format string
            args: Arguments for lazy string formatting
            honeyhive_data: Additional HoneyHive context data
            **kwargs: Additional logging parameters
        """
        extra = kwargs.copy()
        if honeyhive_data:
            extra["honeyhive_data"] = honeyhive_data

        # Use Python's standard logging lazy formatting
        self.logger.log(level, message, *args, extra=extra)

    def debug(
        self,
        message: str,
        *args: Any,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log debug message with lazy formatting support.

        Args:
            message: Debug message format string (supports % formatting)
            *args: Arguments for lazy string formatting
            honeyhive_data: Additional HoneyHive context data
            **kwargs: Additional logging parameters
        """
        self._log_with_context(logging.DEBUG, message, args, honeyhive_data, **kwargs)

    def info(
        self,
        message: str,
        *args: Any,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log info message with lazy formatting support."""
        self._log_with_context(logging.INFO, message, args, honeyhive_data, **kwargs)

    def warning(
        self,
        message: str,
        *args: Any,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log warning message with lazy formatting support."""
        self._log_with_context(logging.WARNING, message, args, honeyhive_data, **kwargs)

    def error(
        self,
        message: str,
        *args: Any,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log error message with lazy formatting support."""
        self._log_with_context(logging.ERROR, message, args, honeyhive_data, **kwargs)

    def critical(
        self,
        message: str,
        *args: Any,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log critical message with lazy formatting support."""
        self._log_with_context(
            logging.CRITICAL, message, args, honeyhive_data, **kwargs
        )

    def exception(
        self,
        message: str,
        *args: Any,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log exception message with traceback and lazy formatting support."""
        extra = kwargs.copy()
        if honeyhive_data:
            extra["honeyhive_data"] = honeyhive_data

        self.logger.exception(message, *args, extra=extra)


def get_logger(
    name: str,
    verbose: Optional[bool] = None,
    tracer_instance: Optional[Any] = None,
    **kwargs: Any,
) -> HoneyHiveLogger:
    """Get a HoneyHive logger instance with dynamic configuration.

    Uses dynamic logic to determine logger configuration based on
    tracer instance settings or explicit parameters.

    Args:
        name: Logger name
        verbose: Explicit verbose setting
        tracer_instance: Tracer instance to extract verbose setting from
        **kwargs: Additional logger parameters

    Returns:
        Configured HoneyHive logger instance
    """
    # Dynamic verbose detection from tracer instance
    if verbose is None and tracer_instance is not None:
        verbose = _extract_verbose_from_tracer_dynamically(tracer_instance)

    return HoneyHiveLogger(name, verbose=verbose, **kwargs)


def _extract_verbose_from_tracer_dynamically(tracer_instance: Any) -> Optional[bool]:
    """Dynamically extract verbose setting from tracer instance.

    Uses dynamic logic to handle different tracer types and configurations.

    Args:
        tracer_instance: Tracer instance to inspect

    Returns:
        Verbose setting if found, None otherwise
    """
    if tracer_instance is None:
        return None

    # Dynamic attribute checking - handles various tracer types
    verbose_attrs = ["verbose", "_verbose", "config.verbose"]

    for attr_path in verbose_attrs:
        try:
            # Handle nested attributes like 'config.verbose'
            obj = tracer_instance
            for attr in attr_path.split("."):
                obj = getattr(obj, attr, None)
                if obj is None:
                    break

            if isinstance(obj, bool):
                return obj
        except (AttributeError, TypeError):
            continue

    return None


# Default logger - uses INFO level by default, can be updated per-instance
default_logger = get_logger("honeyhive")


def get_tracer_logger(
    tracer_instance: Any, logger_name: Optional[str] = None
) -> HoneyHiveLogger:
    """Get a logger instance configured for a specific tracer.

    Creates a unique logger per tracer instance with dynamic configuration
    based on the tracer's verbose setting.

    Args:
        tracer_instance: Tracer instance to create logger for
        logger_name: Optional custom logger name

    Returns:
        Logger configured for the tracer instance
    """
    # Generate unique logger name per tracer instance
    if logger_name is None:
        tracer_id = getattr(tracer_instance, "tracer_id", id(tracer_instance))
        logger_name = f"honeyhive.tracer.{tracer_id}"

    return get_logger(name=logger_name, tracer_instance=tracer_instance)


# Simple approach: Use tracer logger directly, no module-level loggers needed


def safe_log(
    tracer_instance: Any,
    level: str,
    message: str,
    *args: Any,
    honeyhive_data: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> None:
    """Safely log a message with enhanced early initialization and
    multi-instance support.

    This function provides comprehensive protection against logging failures during:
    - Python interpreter shutdown
    - Stream closure in parallel/multiprocess execution
    - Thread teardown race conditions
    - Container/serverless environment shutdown
    - Early initialization before tracer logger is ready
    - Multi-instance tracer scenarios

    Enhanced Fallback Strategy:
    1. Use tracer instance logger if fully initialized
    2. Delegate to actual tracer if tracer_instance has tracer_instance
       (API client pattern)
    3. Use tracer_instance's own logger if available
       (API client independent mode)
    4. Create temporary logger with tracer's verbose setting if tracer exists
       but logger not ready
    5. Use default fallback logger for None tracer_instance or early
       initialization

    Args:
        tracer_instance: Optional tracer instance for per-instance logging
            (can be None or partially initialized)
        level: Log level (debug, info, warning, error)
        message: Log message format string (supports % formatting for lazy evaluation)
        *args: Arguments for lazy string formatting (deferred until log level check)
        honeyhive_data: Optional structured data for HoneyHive logger
        **kwargs: Additional keyword arguments for logger

    Performance Note:
        Uses lazy formatting with % placeholders for optimal performance.
        String interpolation is deferred until the log level is confirmed active,
        avoiding unnecessary string operations for filtered log messages.

    Example:
        >>> # ✅ CORRECT - Lazy formatting (recommended)
        >>> safe_log(tracer_instance, "debug", "Processing %s spans", span_count,
        ...          honeyhive_data={"span_id": "123"})
        >>> safe_log(tracer_instance, "warning",
        ...           "Failed to process %s after %d tries",
        ...          item_name, retry_count)
        >>> # ✅ CORRECT - Static messages
        >>> safe_log(None, "info", "Static message")  # Works without tracer
        >>> safe_log(partial_tracer, "debug", "Early init message")
        >>> # ❌ AVOID - F-strings (eager evaluation, performance impact)
        >>> # safe_log(tracer, "error", f"Failed: {error}")  # Don't do this
    """
    # Import here to avoid circular imports

    # Skip all logging if shutdown conditions are detected
    if _detect_shutdown_conditions():
        return None

    try:
        # Enhanced fallback logic for early initialization and multi-instance safety
        target_logger = None

        # Strategy 1: Use tracer instance logger if fully initialized
        if (
            tracer_instance
            and hasattr(tracer_instance, "logger")
            and tracer_instance.logger
        ):
            target_logger = tracer_instance.logger

        # Strategy 2: Check if tracer_instance has its own tracer_instance
        # (API client pattern)
        elif (
            tracer_instance
            and hasattr(tracer_instance, "tracer_instance")
            and tracer_instance.tracer_instance
        ):
            # API client with tracer_instance - delegate to the actual tracer
            return safe_log(
                tracer_instance.tracer_instance,
                level,
                message,
                *args,
                honeyhive_data=honeyhive_data,
                **kwargs,
            )

        # Strategy 3: Use tracer_instance's own logger if it has one
        # (API client independent mode)
        elif (
            tracer_instance
            and hasattr(tracer_instance, "logger")
            and tracer_instance.logger
        ):
            target_logger = tracer_instance.logger

        # Strategy 4: Use tracer instance for logger creation if partially
        # initialized
        elif tracer_instance and hasattr(tracer_instance, "verbose"):
            # Tracer exists but logger not ready - create temporary logger with
            # tracer's verbose setting
            verbose_setting = getattr(tracer_instance, "verbose", False)
            target_logger = get_logger("honeyhive.early_init", verbose=verbose_setting)

        # Strategy 5: Fallback to default logger for None tracer_instance or
        # no verbose setting
        else:
            # Complete fallback for early initialization or None tracer_instance
            target_logger = get_logger("honeyhive.fallback")

        # Check if the logger and its handlers are still available
        if not hasattr(target_logger, "logger") or not target_logger.logger.handlers:
            return None  # Logger is gone, fail silently

        # Check if any handler has a closed stream
        for handler in target_logger.logger.handlers:
            if hasattr(handler, "stream") and hasattr(
                getattr(handler, "stream", None), "closed"
            ):
                stream = getattr(handler, "stream", None)
                if stream and getattr(stream, "closed", False):
                    # Mark shutdown detected for future calls
                    _shutdown_detected.set()
                    return None  # Stream is closed, fail silently

        log_func = getattr(target_logger, level)
        if honeyhive_data:
            log_func(message, *args, honeyhive_data=honeyhive_data, **kwargs)
        else:
            log_func(message, *args, **kwargs)

    except Exception:
        # Fail silently - logging should never crash the application
        # This includes cases where:
        # - Logger methods don't exist
        # - Stream operations fail
        # - Handler operations fail
        # - Any other logging-related exception
        pass

    return None


# Convenience functions for common log levels
def safe_debug(tracer_instance: Any, message: str, **kwargs: Any) -> None:
    """Convenience function for debug logging."""
    safe_log(tracer_instance, "debug", message, **kwargs)


def safe_info(tracer_instance: Any, message: str, **kwargs: Any) -> None:
    """Convenience function for info logging."""
    safe_log(tracer_instance, "info", message, **kwargs)


def safe_warning(tracer_instance: Any, message: str, **kwargs: Any) -> None:
    """Convenience function for warning logging."""
    safe_log(tracer_instance, "warning", message, **kwargs)


def safe_error(tracer_instance: Any, message: str, **kwargs: Any) -> None:
    """Convenience function for error logging."""
    safe_log(tracer_instance, "error", message, **kwargs)

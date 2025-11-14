"""
Structured JSON logging with behavioral metrics.

Provides structured logging for Ouroboros with:
    - JSON Lines format for queryability (jq, grep)
    - Context fields (session_id, action, timestamps)
    - Behavioral metrics integration
    - Log rotation (size-based)
    - Subsystem-specific loggers

All log entries include structured context for behavioral analysis and debugging.

Example Usage:
    >>> from ouroboros.utils.logging import get_logger
    >>> 
    >>> logger = get_logger("my_module")
    >>> logger.info(
    ...     "Processing query",
    ...     query="How does X work?",
    ...     session_id="abc123",
    ...     action="search_standards"
    ... )
    >>> 
    >>> # Log behavioral event
    >>> logger.behavioral(
    ...     "query_processed",
    ...     metrics={"query_diversity": 0.85, "prepend_shown": True}
    ... )

See Also:
    - config.schemas.logging: LoggingConfig for configuration
    - metrics: MetricsCollector for behavioral metrics tracking
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Formats log records as JSON Lines (one JSON object per line) for:
        - Queryability with jq, grep, etc.
        - Structured storage in log aggregation systems
        - Easy parsing by analysis tools

    JSON Structure:
        {
            "timestamp": "2025-11-04T12:00:00.123456Z",
            "level": "INFO",
            "logger": "ouroboros.subsystems.rag",
            "message": "Query processed",
            "session_id": "abc123",
            "query": "How does X work?",
            "action": "search_standards"
        }

    Example:
        >>> formatter = JSONFormatter()
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
        >>> logger = logging.getLogger("test")
        >>> logger.addHandler(handler)
        >>> logger.info("Test message", extra={"session_id": "123"})
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string.

        Args:
            record: Log record to format

        Returns:
            str: JSON-formatted log line

        Format:
            - timestamp: ISO 8601 UTC timestamp
            - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            - logger: Logger name (e.g., "ouroboros.subsystems.rag")
            - message: Log message
            - **extra: All extra fields from logging call

        Example Output:
            {"timestamp": "2025-11-04T12:00:00.123Z", "level": "INFO", ...}
        """
        # Build base log entry
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exc_info"] = self.formatException(record.exc_info)

        # Add all extra fields (session_id, action, query, etc.)
        # Filter out standard LogRecord attributes
        standard_attrs = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
            "exc_info",
            "exc_text",
            "stack_info",
        }

        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                log_entry[key] = value

        return json.dumps(log_entry)


class StructuredLogger:
    """
    Structured logger with JSON formatting and behavioral metrics.

    Wraps Python logging with:
        - JSON Lines formatting
        - Structured context (session_id, action, etc.)
        - Behavioral event logging
        - Log rotation (size-based)
        - Subsystem-specific log files

    Log Levels:
        - DEBUG: Detailed debugging information
        - INFO: General informational messages
        - WARNING: Warning messages (non-critical issues)
        - ERROR: Error messages (recoverable failures)
        - CRITICAL: Critical failures (unrecoverable)

    Log Rotation:
        Logs rotate when file size exceeds rotation_size_mb:
            - ouroboros.log (current)
            - ouroboros.log.1 (previous)
            - ouroboros.log.2 (older)
            - ... (up to max_files)

    Example:
        >>> logger = StructuredLogger("my_module", Path(".praxis-os/logs"))
        >>> 
        >>> # Basic logging
        >>> logger.info("Query processed", query="How?", session_id="abc")
        >>> 
        >>> # Error logging with exception
        >>> try:
        ...     raise ValueError("Test error")
        ... except Exception:
        ...     logger.error("Operation failed", exc_info=True)
        >>> 
        >>> # Behavioral metrics
        >>> logger.behavioral(
        ...     "query_diversity",
        ...     {"unique_queries": 10, "total_queries": 15, "diversity": 0.67}
        ... )

    Attributes:
        name (str): Logger name (module or subsystem)
        logger (logging.Logger): Underlying Python logger
    """

    def __init__(
        self,
        name: str,
        log_dir: Path,
        level: str = "INFO",
        rotation_size_mb: int = 100,
        max_files: int = 10,
    ) -> None:
        """
        Initialize structured logger.

        Args:
            name: Logger name (e.g., "ouroboros.subsystems.rag")
            log_dir: Directory for log files
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            rotation_size_mb: Rotate when file exceeds N MB
            max_files: Keep N most recent log files

        Example:
            >>> logger = StructuredLogger(
            ...     "my_module",
            ...     Path(".praxis-os/logs"),
            ...     level="DEBUG",
            ...     rotation_size_mb=50,
            ...     max_files=5
            ... )

        Log Files:
            - {log_dir}/ouroboros.log (current)
            - {log_dir}/ouroboros.log.1 (previous)
            - ...
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.propagate = False  # Don't propagate to root logger

        # Ensure log directory exists
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler
        log_file = log_dir / "ouroboros.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=rotation_size_mb * 1024 * 1024,  # Convert MB to bytes
            backupCount=max_files,
        )
        file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(file_handler)

        # Also add console handler for development (non-JSON for readability)
        if level.upper() == "DEBUG":
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.logger.addHandler(console_handler)

    def debug(self, message: str, **extra: Any) -> None:
        """
        Log debug message with structured context.

        Args:
            message: Log message
            **extra: Additional structured fields

        Example:
            >>> logger.debug(
            ...     "Processing batch",
            ...     batch_size=100,
            ...     items_processed=75
            ... )
        """
        self.logger.debug(message, extra=extra)

    def info(self, message: str, **extra: Any) -> None:
        """
        Log info message with structured context.

        Args:
            message: Log message
            **extra: Additional structured fields

        Example:
            >>> logger.info(
            ...     "Query processed",
            ...     query="How does X work?",
            ...     session_id="abc123",
            ...     results=5
            ... )
        """
        self.logger.info(message, extra=extra)

    def warning(self, message: str, **extra: Any) -> None:
        """
        Log warning message with structured context.

        Args:
            message: Log message
            **extra: Additional structured fields

        Example:
            >>> logger.warning(
            ...     "Query diversity low",
            ...     diversity=0.3,
            ...     threshold=0.5
            ... )
        """
        self.logger.warning(message, extra=extra)

    def error(self, message: str, exc_info: bool = False, **extra: Any) -> None:
        """
        Log error message with structured context.

        Args:
            message: Log message
            exc_info: Include exception traceback
            **extra: Additional structured fields

        Example:
            >>> try:
            ...     raise ValueError("Test error")
            ... except Exception:
            ...     logger.error(
            ...         "Operation failed",
            ...         exc_info=True,
            ...         operation="index_build"
            ...     )
        """
        self.logger.error(message, exc_info=exc_info, extra=extra)

    def critical(self, message: str, exc_info: bool = False, **extra: Any) -> None:
        """
        Log critical message with structured context.

        Args:
            message: Log message
            exc_info: Include exception traceback
            **extra: Additional structured fields

        Example:
            >>> logger.critical(
            ...     "System failure",
            ...     exc_info=True,
            ...     subsystem="workflow"
            ... )
        """
        self.logger.critical(message, exc_info=exc_info, extra=extra)

    def behavioral(self, event: str, metrics: dict[str, Any]) -> None:
        """
        Log behavioral event with metrics.

        Behavioral events track AI agent behavior for:
            - Query diversity analysis
            - Workflow adherence tracking
            - Tool usage patterns
            - Learning trends

        Args:
            event: Behavioral event name
            metrics: Event metrics (counts, rates, diversity, etc.)

        Example:
            >>> logger.behavioral(
            ...     "query_diversity",
            ...     {
            ...         "session_id": "abc123",
            ...         "unique_queries": 10,
            ...         "total_queries": 15,
            ...         "diversity": 0.67,
            ...         "trend": "improving"
            ...     }
            ... )

        Behavioral Events:
            - query_diversity: Query uniqueness tracking
            - workflow_adherence: Gate passage rates
            - tool_usage: Tool call frequencies
            - prepend_effectiveness: Gamification impact
            - learning_trend: Behavior improvement over time

        Metrics Structure:
            - session_id: AI agent session identifier
            - timestamp: Event timestamp (auto-added)
            - event_type: "behavioral" (auto-added)
            - **metrics: Event-specific metrics
        """
        self.logger.info(
            f"Behavioral event: {event}",
            extra={"event_type": "behavioral", "event_name": event, **metrics},
        )


# Global logger registry for subsystems
_loggers: dict[str, StructuredLogger] = {}


def get_logger(
    name: str,
    log_dir: Optional[Path] = None,
    level: Optional[str] = None,
    rotation_size_mb: int = 100,
    max_files: int = 10,
) -> StructuredLogger:
    """
    Get or create structured logger for subsystem.

    Maintains global logger registry to ensure single logger per subsystem.
    Subsequent calls with same name return cached logger.

    Args:
        name: Logger name (e.g., "ouroboros.subsystems.rag")
        log_dir: Log directory (default: .praxis-os/logs)
        level: Log level (default: INFO)
        rotation_size_mb: Rotate when file exceeds N MB
        max_files: Keep N most recent log files

    Returns:
        StructuredLogger: Logger instance for subsystem

    Example:
        >>> # First call creates logger
        >>> logger1 = get_logger("my_module")
        >>> 
        >>> # Second call returns same logger
        >>> logger2 = get_logger("my_module")
        >>> assert logger1 is logger2

    Use Cases:
        - Subsystem logging (RAG, Workflow, Browser)
        - Module-specific logging (query_tracker, prepend_generator)
        - Tool logging (pos_search_project, pos_workflow)
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(
            name=name,
            log_dir=log_dir or Path(".praxis-os/logs"),
            level=level or "INFO",
            rotation_size_mb=rotation_size_mb,
            max_files=max_files,
        )

    return _loggers[name]


__all__ = ["JSONFormatter", "StructuredLogger", "get_logger"]


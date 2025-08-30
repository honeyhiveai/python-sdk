"""HoneyHive Logging Module - Structured logging utilities."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from .config import config


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
            log_data.update(record.honeyhive_data)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}

        return json.dumps(log_data, default=str)


class HoneyHiveLogger:
    """HoneyHive logger with structured logging.

    Provides a structured logging interface with HoneyHive-specific
    formatting and context data support.
    """

    def __init__(
        self,
        name: str,
        level: Optional[Union[str, int]] = None,
        formatter: Optional[logging.Formatter] = None,
        handler: Optional[logging.Handler] = None,
    ):
        """Initialize the logger.

        Args:
            name: Logger name
            level: Log level (string or integer)
            formatter: Custom formatter to use
            handler: Custom handler to use
        """
        self.logger = logging.getLogger(name)

        # Set level
        if level is not None:
            if isinstance(level, str):
                level = getattr(logging, level.upper())
            self.logger.setLevel(level)  # type: ignore[arg-type]
        elif config.debug_mode:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

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

    def _log_with_context(
        self,
        level: int,
        message: str,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log with HoneyHive context data.

        Args:
            level: Log level
            message: Log message
            honeyhive_data: Additional HoneyHive context data
            **kwargs: Additional logging parameters
        """
        extra = kwargs.copy()
        if honeyhive_data:
            extra["honeyhive_data"] = honeyhive_data

        self.logger.log(level, message, extra=extra)

    def debug(
        self,
        message: str,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log debug message.

        Args:
            message: Debug message to log
            honeyhive_data: Additional HoneyHive context data
            **kwargs: Additional logging parameters
        """
        self._log_with_context(logging.DEBUG, message, honeyhive_data, **kwargs)

    def info(
        self,
        message: str,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log info message."""
        self._log_with_context(logging.INFO, message, honeyhive_data, **kwargs)

    def warning(
        self,
        message: str,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, honeyhive_data, **kwargs)

    def error(
        self,
        message: str,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log error message."""
        self._log_with_context(logging.ERROR, message, honeyhive_data, **kwargs)

    def critical(
        self,
        message: str,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, honeyhive_data, **kwargs)

    def exception(
        self,
        message: str,
        honeyhive_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Log exception message with traceback."""
        extra = kwargs.copy()
        if honeyhive_data:
            extra["honeyhive_data"] = honeyhive_data

        self.logger.exception(message, extra=extra)


def get_logger(name: str, **kwargs: Any) -> HoneyHiveLogger:
    """Get a HoneyHive logger instance."""
    return HoneyHiveLogger(name, **kwargs)


# Default logger
default_logger = get_logger("honeyhive")

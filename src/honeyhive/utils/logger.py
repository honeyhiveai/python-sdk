"""HoneyHive Logging Module - Structured logging utilities."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from .config import config


class HoneyHiveFormatter(logging.Formatter):
    """Custom formatter for HoneyHive logs."""
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with HoneyHive structure."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat() if self.include_timestamp else None,
            "level": record.levelname if self.include_level else None,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'honeyhive_data'):
            log_data.update(record.honeyhive_data)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        return json.dumps(log_data, default=str)


class HoneyHiveLogger:
    """HoneyHive logger with structured logging."""
    
    def __init__(
        self,
        name: str,
        level: Optional[Union[str, int]] = None,
        formatter: Optional[logging.Formatter] = None,
        handler: Optional[logging.Handler] = None
    ):
        self.logger = logging.getLogger(name)
        
        # Set level
        if level is not None:
            if isinstance(level, str):
                level = getattr(logging, level.upper())
            self.logger.setLevel(level)
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
        **kwargs
    ):
        """Log with HoneyHive context data."""
        extra = kwargs.copy()
        if honeyhive_data:
            extra['honeyhive_data'] = honeyhive_data
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, honeyhive_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, honeyhive_data, **kwargs)
    
    def info(self, message: str, honeyhive_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, honeyhive_data, **kwargs)
    
    def warning(self, message: str, honeyhive_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, honeyhive_data, **kwargs)
    
    def error(self, message: str, honeyhive_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, honeyhive_data, **kwargs)
    
    def critical(self, message: str, honeyhive_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, honeyhive_data, **kwargs)
    
    def exception(self, message: str, honeyhive_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log exception message with traceback."""
        extra = kwargs.copy()
        if honeyhive_data:
            extra['honeyhive_data'] = honeyhive_data
        
        self.logger.exception(message, extra=extra)


def get_logger(name: str, **kwargs) -> HoneyHiveLogger:
    """Get a HoneyHive logger instance."""
    return HoneyHiveLogger(name, **kwargs)


# Default logger
default_logger = get_logger("honeyhive")

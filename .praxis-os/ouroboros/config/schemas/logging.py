"""
Configuration schema for logging subsystem.

Provides Pydantic v2 model for structured logging configuration including:
    - Log directory and rotation
    - Log level and format (JSON vs text)
    - File rotation by size
    - Behavioral metrics logging

Supports JSON Lines format for structured logs and behavioral metrics tracking.

Example Usage:
    >>> from ouroboros.config.schemas.logging import LoggingConfig
    >>> 
    >>> config = LoggingConfig(
    ...     log_dir=Path(".praxis-os/logs"),
    ...     level="INFO",
    ...     format="json",
    ...     rotation_size_mb=100,
    ...     max_files=10,
    ...     behavioral_metrics_enabled=True
    ... )

See Also:
    - base.BaseConfig: Base configuration model
    - Behavioral metrics: Query diversity, trend tracking, prepend effectiveness
"""

from pathlib import Path

from pydantic import Field

from ouroboros.config.schemas.base import BaseConfig


class LoggingConfig(BaseConfig):
    """
    Configuration for structured logging with behavioral metrics.

    Manages structured logging with JSON Lines format, log rotation, and
    behavioral metrics tracking. Behavioral metrics are mission-critical for
    Ouroboros's behavioral engineering goals (query diversity, prepend
    effectiveness, trend analysis).

    Key Settings:
        - log_dir: Directory for log files
        - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - format: Log format (json=JSON Lines, text=human-readable)
        - rotation_size_mb: Rotate logs when file exceeds N MB
        - max_files: Keep N most recent log files
        - behavioral_metrics_enabled: Enable behavioral metrics logging

    Log Formats:
        - json: JSON Lines format (one JSON object per line)
            {
                "timestamp": "2025-11-04T12:00:00Z",
                "level": "INFO",
                "message": "Query processed",
                "query": "How does X work?",
                "session_id": "uuid",
                "metrics": {...}
            }
        - text: Human-readable format
            2025-11-04 12:00:00 INFO Query processed: How does X work?

    Behavioral Metrics:
        When behavioral_metrics_enabled=True, logs include:
            - Query diversity (unique queries per session)
            - Query trends (categories over time)
            - Prepend effectiveness (queries with/without prepends)
            - Search quality (result relevance, chunk utility)
            - Workflow adherence (gate passage rates)

    Log Rotation:
        Logs rotate when file size exceeds rotation_size_mb:
            - ouroboros.log (current)
            - ouroboros.log.1 (previous)
            - ouroboros.log.2 (older)
            - ... (up to max_files)
        Oldest logs are deleted when max_files exceeded.

    Example:
        >>> from ouroboros.config.schemas.logging import LoggingConfig
        >>> 
        >>> # Production config (JSON, INFO level, 100MB rotation)
        >>> config = LoggingConfig(
        ...     log_dir=Path(".praxis-os/logs"),
        ...     level="INFO",
        ...     format="json",
        ...     rotation_size_mb=100,
        ...     max_files=10,
        ...     behavioral_metrics_enabled=True
        ... )
        >>> 
        >>> # Development config (text, DEBUG level, smaller rotation)
        >>> dev_config = LoggingConfig(
        ...     level="DEBUG",
        ...     format="text",
        ...     rotation_size_mb=10,
        ...     max_files=5,
        ...     behavioral_metrics_enabled=True
        ... )
        >>> 
        >>> # Testing config (minimal logging, no metrics)
        >>> test_config = LoggingConfig(
        ...     level="WARNING",
        ...     format="text",
        ...     behavioral_metrics_enabled=False
        ... )

    Validation Rules:
        - level: Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL
        - format: Must be "json" or "text"
        - rotation_size_mb: 10-1000 MB
        - max_files: 1-100 files
        - log_dir: Path for log files

    Behavioral Engineering:
        Behavioral metrics are Ouroboros's primary mission. Logs track:
            - Query-first behavior (agents querying standards)
            - Workflow adherence (gate passage, evidence quality)
            - Tool usage patterns (search → implement → validate)
            - Learning trends (query diversity increasing over time)

    Performance:
        - JSON format: ~1-2ms per log entry (buffered writes)
        - Text format: ~0.5-1ms per log entry
        - Rotation: ~10-50ms (background thread)
        - Behavioral metrics: ~5-10ms overhead per query
    """

    log_dir: Path = Field(
        default=Path(".praxis-os/logs"),
        description="Directory for log files (JSON Lines format)",
    )

    level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Log level (DEBUG|INFO|WARNING|ERROR|CRITICAL)",
    )

    format: str = Field(
        default="json",
        pattern=r"^(json|text)$",
        description="Log format (json=JSON Lines, text=human-readable)",
    )

    rotation_size_mb: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Rotate logs when file size exceeds N MB (10-1000)",
    )

    max_files: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Keep N most recent log files (1-100)",
    )

    behavioral_metrics_enabled: bool = Field(
        default=True,
        description="Enable behavioral metrics logging (query diversity, trends, prepend effectiveness)",
    )


__all__ = ["LoggingConfig"]


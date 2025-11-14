"""
Core utilities for Ouroboros MCP server.

Provides foundational utilities for:
    - Errors: Actionable exceptions with remediation guidance
    - Logging: Structured JSON logging with behavioral metrics
    - Metrics: Behavioral metrics tracking (query diversity, latency)

These utilities are used throughout the Ouroboros codebase to ensure
consistent error handling, logging, and metrics collection.

Example Usage:
    >>> from ouroboros.utils.errors import ActionableError
    >>> from ouroboros.utils.logging import get_logger
    >>> from ouroboros.utils.metrics import MetricsCollector
    >>> 
    >>> # Error handling
    >>> raise ActionableError(
    ...     what_failed="Config validation failed",
    ...     why_failed="chunk_size must be >= 100",
    ...     how_to_fix="Update config: indexes.vector.chunk_size = 500"
    ... )
    >>> 
    >>> # Logging
    >>> logger = get_logger("my_module")
    >>> logger.info("Processing query", query="How does X work?", session_id="abc123")
    >>> 
    >>> # Metrics
    >>> metrics = MetricsCollector()
    >>> metrics.track_query("How does X work?", session_id="abc123")

See Also:
    - errors: Actionable exceptions with remediation
    - logging: Structured JSON logging
    - metrics: Behavioral metrics tracking
"""

__all__ = []


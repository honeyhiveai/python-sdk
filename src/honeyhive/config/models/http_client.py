"""HTTP client configuration models for HoneyHive SDK.

This module provides Pydantic models for HTTP client configuration
including connection pooling, timeouts, retry behavior, proxy settings,
and SSL configuration.
"""

# pylint: disable=duplicate-code
# Note: Environment variable utility functions (_get_env_*) are intentionally
# duplicated across config modules to keep each module self-contained and
# avoid unnecessary coupling. These are simple, stable utility functions.

import logging
import os
from typing import Any, Optional

from pydantic import Field, field_validator

from .base import BaseHoneyHiveConfig, _safe_validate_url


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean value from environment variable."""
    value = os.getenv(key, "").lower()
    if value in ("true", "1", "yes", "on"):
        return True
    if value in ("false", "0", "no", "off"):
        return False
    return default


def _get_env_int(key: str, default: int = 0) -> int:
    """Get integer value from environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


def _get_env_float(key: str, default: float = 0.0) -> float:
    """Get float value from environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


class HTTPClientConfig(BaseHoneyHiveConfig):
    """HTTP client configuration settings.

    This class extends BaseHoneyHiveConfig with HTTP-specific settings
    for connection pooling, timeouts, retry behavior, proxy settings,
    and SSL configuration. Supports both HH_* and standard HTTP_*
    environment variables.

    Example:
        >>> config = HTTPClientConfig(
        ...     timeout=30.0,
        ...     max_connections=50,
        ...     http_proxy="http://proxy.company.com:8080"
        ... )
        >>> # Or load from environment variables:
        >>> # export HH_TIMEOUT=30.0
        >>> # export HH_MAX_CONNECTIONS=50
        >>> config = HTTPClientConfig()
    """

    # Connection settings
    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds",
        examples=[30.0, 60.0, 120.0],
    )

    max_connections: int = Field(
        default=10,
        description="Maximum connections in pool",
        examples=[10, 50, 100],
    )

    max_keepalive_connections: int = Field(
        default=20,
        description="Maximum keepalive connections",
        examples=[20, 50, 100],
    )

    keepalive_expiry: float = Field(
        default=30.0,
        description="Keepalive expiry time in seconds",
        examples=[30.0, 60.0, 300.0],
    )

    pool_timeout: float = Field(
        default=10.0,
        description="Pool timeout in seconds",
        examples=[10.0, 30.0, 60.0],
    )

    # Rate limiting
    rate_limit_calls: int = Field(
        default=100,
        description="Maximum calls per time window",
        examples=[100, 200, 500],
    )

    rate_limit_window: float = Field(
        default=60.0,
        description="Rate limit time window in seconds",
        examples=[60.0, 300.0, 3600.0],
    )

    max_retries: int = Field(
        3,
        description="Maximum retry attempts",
        examples=[3, 5, 10],
    )

    # Proxy settings
    http_proxy: Optional[str] = Field(
        None,
        description="HTTP proxy URL",
        examples=["http://proxy.company.com:8080"],
    )

    https_proxy: Optional[str] = Field(
        None,
        description="HTTPS proxy URL",
        examples=["https://proxy.company.com:8080"],
    )

    no_proxy: Optional[str] = Field(
        None,
        description="Comma-separated list of hosts to bypass proxy",
        examples=["localhost,127.0.0.1,.local"],
    )

    # SSL and redirects
    verify_ssl: bool = Field(
        True,
        description="Verify SSL certificates",
    )

    follow_redirects: bool = Field(
        True,
        description="Follow HTTP redirects",
    )

    def __init__(self, **data: Any) -> None:
        """Load this class's fields from the environment before validation.

        Init kwargs outrank the pydantic-settings environment source, so the
        HH_ names read here are what populate the fields declared on this
        class; the inherited fields still come through env_prefix. Reading
        them here also honours the standard HTTP_*, *_PROXY, VERIFY_SSL and
        FOLLOW_REDIRECTS variables and falls back to the default on a
        malformed value instead of raising.
        """
        # Load from environment variables with fallbacks to standard env vars
        env_data = {
            "timeout": _get_env_float("HH_TIMEOUT", 30.0),
            "max_connections": _get_env_int(
                "HH_MAX_CONNECTIONS", _get_env_int("HTTP_MAX_CONNECTIONS", 10)
            ),
            "max_keepalive_connections": _get_env_int(
                "HH_MAX_KEEPALIVE_CONNECTIONS",
                _get_env_int("HTTP_MAX_KEEPALIVE_CONNECTIONS", 20),
            ),
            "keepalive_expiry": _get_env_float(
                "HH_KEEPALIVE_EXPIRY", _get_env_float("HTTP_KEEPALIVE_EXPIRY", 30.0)
            ),
            "pool_timeout": _get_env_float(
                "HH_POOL_TIMEOUT", _get_env_float("HTTP_POOL_TIMEOUT", 10.0)
            ),
            "rate_limit_calls": _get_env_int(
                "HH_RATE_LIMIT_CALLS", _get_env_int("HTTP_RATE_LIMIT_CALLS", 100)
            ),
            "rate_limit_window": _get_env_float(
                "HH_RATE_LIMIT_WINDOW", _get_env_float("HTTP_RATE_LIMIT_WINDOW", 60.0)
            ),
            "max_retries": _get_env_int("HH_MAX_RETRIES", 3),
            # Proxy settings with fallbacks
            "http_proxy": (
                os.getenv("HH_HTTP_PROXY")
                or os.getenv("HTTP_PROXY")
                or os.getenv("http_proxy")
            ),
            "https_proxy": (
                os.getenv("HH_HTTPS_PROXY")
                or os.getenv("HTTPS_PROXY")
                or os.getenv("https_proxy")
            ),
            "no_proxy": (
                os.getenv("HH_NO_PROXY")
                or os.getenv("NO_PROXY")
                or os.getenv("no_proxy")
            ),
            # SSL and redirects
            "verify_ssl": _get_env_bool(
                "HH_VERIFY_SSL", _get_env_bool("VERIFY_SSL", True)
            ),
            "follow_redirects": _get_env_bool(
                "HH_FOLLOW_REDIRECTS", _get_env_bool("FOLLOW_REDIRECTS", True)
            ),
        }

        # Merge environment data with provided data (provided data takes precedence)
        merged_data = {**env_data, **data}
        super().__init__(**merged_data)

    @field_validator(
        "timeout",
        "keepalive_expiry",
        "pool_timeout",
        "rate_limit_window",
        mode="before",
    )
    @classmethod
    def validate_positive_float(cls, v: Any) -> float:
        """Validate that float values are positive with graceful degradation."""
        # Handle type conversion gracefully
        try:
            if v is None:
                return 30.0  # Default for None
            v = float(v)
        except (ValueError, TypeError):
            logger = logging.getLogger(__name__)
            logger.warning(
                "Invalid float type: expected float, got %s. Using default 30.0.",
                type(v).__name__,
                extra={
                    "honeyhive_data": {"invalid_value": v, "type": type(v).__name__}
                },
            )
            return 30.0  # Safe default

        if v <= 0:
            logger = logging.getLogger(__name__)
            logger.warning(
                "Invalid timeout value: must be positive, got %s. Using default 30.0.",
                v,
                extra={"honeyhive_data": {"invalid_timeout": v}},
            )
            return 30.0  # Safe default
        return v  # type: ignore[no-any-return]

    @field_validator(
        "max_connections",
        "max_keepalive_connections",
        "rate_limit_calls",
        "max_retries",
        mode="before",
    )
    @classmethod
    def validate_positive_int(cls, v: Any) -> int:
        """Validate that integer values are positive with graceful degradation."""
        # Handle type conversion gracefully
        try:
            if v is None:
                return 100  # Default for None
            v = int(v)
        except (ValueError, TypeError):
            logger = logging.getLogger(__name__)
            logger.warning(
                "Invalid int type: expected int, got %s. Using default 100.",
                type(v).__name__,
                extra={
                    "honeyhive_data": {"invalid_value": v, "type": type(v).__name__}
                },
            )
            return 100  # Safe default

        if v <= 0:
            logger = logging.getLogger(__name__)
            logger.warning(
                (
                    "Invalid connection value: must be positive, got %s. "
                    "Using default 100."
                ),
                v,
                extra={"honeyhive_data": {"invalid_value": v}},
            )
            return 100  # Safe default
        return v  # type: ignore[no-any-return]

    @field_validator("http_proxy", "https_proxy", mode="before")
    @classmethod
    def validate_proxy_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate proxy URL format with graceful degradation."""

        return _safe_validate_url(v, "proxy_url", allow_none=True, default=None)

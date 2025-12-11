"""OTLP configuration models for HoneyHive SDK.

This module provides Pydantic models for OTLP (OpenTelemetry Protocol)
configuration including batch processing, export intervals, and performance tuning.
"""

# pylint: disable=duplicate-code
# Note: Environment variable utility functions (_get_env_*) are intentionally
# duplicated across config modules to keep each module self-contained and
# avoid unnecessary coupling. These are simple, stable utility functions.

import json
import logging
import os
from typing import Any, Dict, Optional

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import SettingsConfigDict

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


def _get_env_json(key: str, default: Optional[dict] = None) -> Optional[dict]:
    """Get JSON value from environment variable."""
    value = os.getenv(key)
    if not value:
        return default
    try:
        result = json.loads(value)
        if isinstance(result, dict):
            return result
        return default
    except (json.JSONDecodeError, TypeError):
        return default


class OTLPConfig(BaseHoneyHiveConfig):
    """OTLP (OpenTelemetry Protocol) configuration settings.

    This class extends BaseHoneyHiveConfig with OTLP-specific settings
    for batch processing, export intervals, and performance tuning.

    Example:
        >>> config = OTLPConfig(
        ...     batch_size=200,
        ...     flush_interval=1.0,
        ...     otlp_endpoint="https://custom.otlp.endpoint"
        ... )
        >>> # Or load from environment variables:
        >>> # export HH_BATCH_SIZE=200
        >>> # export HH_FLUSH_INTERVAL=1.0
        >>> config = OTLPConfig()
    """

    # OTLP export settings
    otlp_enabled: bool = Field(  # type: ignore[call-overload,pydantic-alias]
        default=True,
        description="Enable OTLP export",
        validation_alias=AliasChoices("HH_OTLP_ENABLED", "otlp_enabled"),
    )

    otlp_endpoint: Optional[str] = Field(  # type: ignore[call-overload,pydantic-alias]
        default=None,
        description="Custom OTLP endpoint URL",
        validation_alias=AliasChoices("HH_OTLP_ENDPOINT", "otlp_endpoint"),
        examples=["https://api.honeyhive.ai/otlp", "https://custom.otlp.endpoint"],
    )

    otlp_headers: Optional[Dict[str, Any]] = Field(  # type: ignore[call-overload,pydantic-alias]  # pylint: disable=line-too-long
        default=None,
        description="OTLP headers in JSON format",
        validation_alias=AliasChoices("HH_OTLP_HEADERS", "otlp_headers"),
        examples=[{"Authorization": "Bearer token", "X-Custom": "value"}],
    )

    otlp_protocol: str = Field(  # type: ignore[call-overload,pydantic-alias]
        default="http/protobuf",
        description="OTLP protocol format: 'http/protobuf' or 'http/json'",
        validation_alias=AliasChoices(
            "HH_OTLP_PROTOCOL", "OTEL_EXPORTER_OTLP_PROTOCOL", "otlp_protocol"
        ),
        examples=["http/protobuf", "http/json"],
    )

    # Batch processing settings
    batch_size: int = Field(  # type: ignore[call-overload,pydantic-alias]
        default=100,
        description="OTLP batch size for performance optimization",
        validation_alias=AliasChoices("HH_BATCH_SIZE", "batch_size"),
        examples=[50, 100, 200, 500],
    )

    flush_interval: float = Field(  # type: ignore[call-overload,pydantic-alias]
        default=5.0,
        description="OTLP flush interval in seconds",
        validation_alias=AliasChoices("HH_FLUSH_INTERVAL", "flush_interval"),
        examples=[0.5, 1.0, 5.0, 10.0],
    )

    max_export_batch_size: int = Field(  # type: ignore[call-overload,pydantic-alias]
        default=512,
        description="Maximum export batch size",
        validation_alias=AliasChoices(
            "HH_MAX_EXPORT_BATCH_SIZE", "max_export_batch_size"
        ),
        examples=[256, 512, 1024],
    )

    export_timeout: float = Field(  # type: ignore[call-overload,pydantic-alias]
        default=30.0,
        description="Export timeout in seconds",
        validation_alias=AliasChoices("HH_EXPORT_TIMEOUT", "export_timeout"),
        examples=[10.0, 30.0, 60.0],
    )

    model_config = SettingsConfigDict(
        validate_assignment=True,
        extra="forbid",
        case_sensitive=False,
    )

    def __init__(self, **data: Any) -> None:
        """Initialize OTLP config with environment variable loading."""
        # Load from environment variables
        env_data = {
            "otlp_enabled": _get_env_bool("HH_OTLP_ENABLED", True),
            "otlp_endpoint": os.getenv("HH_OTLP_ENDPOINT"),
            "otlp_headers": _get_env_json("HH_OTLP_HEADERS"),
            "otlp_protocol": os.getenv("HH_OTLP_PROTOCOL")
            or os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL")
            or "http/protobuf",
            "batch_size": _get_env_int("HH_BATCH_SIZE", 100),
            "flush_interval": _get_env_float("HH_FLUSH_INTERVAL", 5.0),
            "max_export_batch_size": _get_env_int("HH_MAX_EXPORT_BATCH_SIZE", 512),
            "export_timeout": _get_env_float("HH_EXPORT_TIMEOUT", 30.0),
        }

        # Merge environment data with provided data (provided data takes precedence)
        merged_data = {**env_data, **data}
        super().__init__(**merged_data)

    @field_validator("otlp_endpoint", mode="before")
    @classmethod
    def validate_otlp_endpoint(cls, v: Optional[str]) -> Optional[str]:
        """Validate OTLP endpoint URL format with graceful degradation."""

        # If None is provided, allow it
        if v is None:
            return None

        # Use a default OTLP endpoint for invalid URLs
        default_endpoint = "http://localhost:4318/v1/traces"
        validated = _safe_validate_url(
            v, "otlp_endpoint", allow_none=False, default=default_endpoint
        )
        # Remove trailing slash for consistency
        return validated.rstrip("/") if validated else None

    @field_validator("batch_size", "max_export_batch_size", mode="before")
    @classmethod
    def validate_batch_sizes(cls, v: Any) -> int:
        """Validate batch size values with graceful degradation."""
        # Handle type conversion gracefully
        try:
            if v is None:
                return 100  # Default for None
            v = int(v)
        except (ValueError, TypeError):
            logger = logging.getLogger(__name__)
            logger.warning(
                "Invalid batch size type: expected int, got %s. Using default 100.",
                type(v).__name__,
                extra={
                    "honeyhive_data": {
                        "invalid_batch_size": v,
                        "type": type(v).__name__,
                    }
                },
            )
            return 100  # Safe default

        if v <= 0:
            logger = logging.getLogger(__name__)
            logger.warning(
                "Invalid batch size: must be positive, got %s. Using default 100.",
                v,
                extra={"honeyhive_data": {"invalid_batch_size": v}},
            )
            return 100  # Safe default
        if v > 10000:
            logger = logging.getLogger(__name__)
            logger.warning(
                "Large batch size may impact performance: %s. Using maximum 10000.",
                v,
                extra={"honeyhive_data": {"large_batch_size": v}},
            )
            return 10000  # Performance limit
        return v  # type: ignore[no-any-return]

    @field_validator("flush_interval", "export_timeout", mode="before")
    @classmethod
    def validate_timeouts(cls, v: Any) -> float:
        """Validate timeout values with graceful degradation."""
        # Handle type conversion gracefully
        try:
            if v is None:
                return 5.0  # Default for None
            v = float(v)
        except (ValueError, TypeError):
            logger = logging.getLogger(__name__)
            logger.warning(
                "Invalid timeout type: expected float, got %s. Using default 5.0.",
                type(v).__name__,
                extra={
                    "honeyhive_data": {"invalid_timeout": v, "type": type(v).__name__}
                },
            )
            return 5.0  # Safe default

        if v <= 0:
            logger = logging.getLogger(__name__)
            logger.warning(
                "Invalid timeout: must be positive, got %s. Using default 5.0.",
                v,
                extra={"honeyhive_data": {"invalid_timeout": v}},
            )
            return 5.0  # Safe default
        return v  # type: ignore[no-any-return]

    @field_validator("otlp_headers", mode="before")
    @classmethod
    def validate_otlp_headers(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate OTLP headers format with graceful degradation."""
        if v is not None:
            if not isinstance(v, dict):
                logger = logging.getLogger(__name__)
                logger.warning(
                    "Invalid otlp_headers: expected dict, got %s. Using None.",
                    type(v).__name__,
                    extra={"honeyhive_data": {"headers_type": type(v).__name__}},
                )
                return None

            # Ensure all keys are strings - filter out invalid keys
            valid_headers = {}
            for key, value in v.items():
                if isinstance(key, str):
                    valid_headers[key] = value
                else:
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        (
                            "Invalid OTLP header key: expected string, got %s. "
                            "Skipping key."
                        ),
                        type(key).__name__,
                        extra={
                            "honeyhive_data": {
                                "key_type": type(key).__name__,
                                "key": str(key),
                            }
                        },
                    )
            return valid_headers if valid_headers else None
        return v

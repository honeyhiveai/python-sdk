"""Base configuration models for HoneyHive SDK.

This module provides the base Pydantic models that contain common fields
shared across different domain-specific configurations. This approach
eliminates duplication while maintaining type safety and validation.

The models follow graceful degradation principles - invalid values are logged
as warnings and replaced with safe defaults to prevent crashing the host application.
"""

# pylint: disable=duplicate-code
# Note: Pydantic model configuration patterns are intentionally similar
# across config modules for consistency. These provide standardized
# validation and environment variable handling.

import logging
import os
from typing import Any, Optional

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Module logger for graceful degradation warnings
logger = logging.getLogger(__name__)


class ServerURLMixin:  # pylint: disable=too-few-public-methods
    """Mixin for server URL configuration with HH_API_URL environment variable support.

    This mixin provides the server_url field with proper environment variable loading
    for classes that need to support custom HoneyHive server URLs. It can be used
    by both APIClientConfig and TracerConfig to avoid field duplication.

    Environment Variables:
        HH_API_URL: Custom HoneyHive server URL

    Examples:
        >>> class MyConfig(BaseHoneyHiveConfig, ServerURLMixin):
        ...     pass
        >>> config = MyConfig()  # Loads from HH_API_URL if set
    """

    server_url: str = Field(
        default="https://api.honeyhive.ai",
        description="Custom HoneyHive server URL",
        validation_alias=AliasChoices("HH_API_URL", "server_url"),
        examples=["https://api.honeyhive.ai", "https://custom.honeyhive.com"],
    )

    @field_validator("server_url", mode="before")
    @classmethod
    def validate_server_url(cls, v: Any) -> str:
        """Validate server URL format with graceful degradation.

        Args:
            v: The server URL to validate

        Returns:
            The validated and normalized server URL, or default if invalid
        """
        if v is None:
            return "https://api.honeyhive.ai"

        validated = _safe_validate_url(
            v, "server_url", allow_none=False, default="https://api.honeyhive.ai"
        )
        # Remove trailing slash for consistency
        return validated.rstrip("/") if validated else "https://api.honeyhive.ai"


def _safe_validate_string(
    value: Any, field_name: str, allow_none: bool = True, default: Optional[str] = None
) -> Optional[str]:
    """Safely validate string values with graceful degradation.

    Args:
        value: Value to validate
        field_name: Name of the field for logging
        allow_none: Whether None values are allowed
        default: Default value to return on validation failure

    Returns:
        Validated string or safe default
    """
    if value is None:
        return None if allow_none else default

    if not isinstance(value, str):
        logger.warning(
            "Invalid %s: expected string, got %s. Using default.",
            field_name,
            type(value).__name__,
            extra={
                "honeyhive_data": {
                    "field": field_name,
                    "invalid_type": type(value).__name__,
                }
            },
        )
        return default

    value = value.strip()
    if len(value) == 0:
        logger.warning(
            "Empty %s provided. Using default.",
            field_name,
            extra={"honeyhive_data": {"field": field_name}},
        )
        return default

    return value  # type: ignore[no-any-return]


def _safe_validate_url(
    value: Any, field_name: str, allow_none: bool = True, default: Optional[str] = None
) -> Optional[str]:
    """Safely validate URL values with graceful degradation.

    Args:
        value: Value to validate
        field_name: Name of the field for logging
        allow_none: Whether None values are allowed
        default: Default value to return on validation failure

    Returns:
        Validated URL or safe default
    """
    validated = _safe_validate_string(value, field_name, allow_none, default)
    if validated is None or validated == default:
        return validated

    if not validated.startswith(("http://", "https://")):
        logger.warning(
            "Invalid %s: must be HTTP/HTTPS URL. Using default.",
            field_name,
            extra={"honeyhive_data": {"field": field_name, "invalid_url": validated}},
        )
        return default

    return validated


class BaseHoneyHiveConfig(BaseSettings):
    """Base configuration model with common HoneyHive fields.

    This base class contains fields that are commonly used across different
    parts of the SDK (tracer, API client, evaluation, etc.) to avoid
    duplication and ensure consistent validation.

    Common Fields:
        - api_key: HoneyHive API key for authentication
        - project: Project name (required by backend API)
        - test_mode: Enable test mode (no data sent to backend)
        - verbose: Enable verbose logging

    Example:
        This class is not used directly but inherited by domain-specific configs:

        >>> class TracerConfig(BaseHoneyHiveConfig):
        ...     session_name: Optional[str] = None
        ...     source: str = "dev"
        >>>
        >>> config = TracerConfig(api_key="hh_...", project="my-project")
        >>> print(config.api_key)  # Inherited from base
        hh_...
    """

    api_key: Optional[str] = Field(  # type: ignore[call-overload,pydantic-alias]
        default=None,
        description="HoneyHive API key for authentication",
        validation_alias=AliasChoices("HH_API_KEY", "api_key"),
        examples=["hh_1234567890abcdef"],
    )

    project: Optional[str] = Field(  # type: ignore[call-overload,pydantic-alias]
        default=None,
        description="Project name (required by backend API)",
        validation_alias=AliasChoices("HH_PROJECT", "project"),
        examples=["my-llm-project", "chatbot-v2"],
    )

    test_mode: bool = Field(  # type: ignore[call-overload,pydantic-alias]
        default=False,
        description="Enable test mode (no data sent to backend)",
        validation_alias=AliasChoices("HH_TEST_MODE", "test_mode"),
    )

    verbose: bool = Field(  # type: ignore[call-overload,pydantic-alias]
        default=False,
        description="Enable verbose logging output and debug mode",
        validation_alias=AliasChoices("HH_VERBOSE", "verbose"),
    )

    model_config = SettingsConfigDict(
        validate_assignment=True,
        extra="forbid",  # Prevent accidental typos in field names
        case_sensitive=False,
    )

    def __init__(self, **data: Any) -> None:
        """Initialize base config with unified verbose/debug mode handling."""
        # Handle verbose mode from HH_VERBOSE environment variable
        if "verbose" not in data:
            # Check HH_VERBOSE environment variable
            verbose_env = os.getenv("HH_VERBOSE", "").lower()

            # Set verbose=True if HH_VERBOSE is true
            if verbose_env in ("true", "1", "yes", "on"):
                data["verbose"] = True

        super().__init__(**data)

    @field_validator("api_key", mode="before")
    @classmethod
    def validate_api_key(cls, v: Any) -> Optional[str]:
        """Validate API key format with graceful degradation.

        Args:
            v: The API key value to validate

        Returns:
            The validated and normalized API key, or None if invalid
        """
        validated = _safe_validate_string(v, "api_key", allow_none=True, default=None)
        if validated is not None:
            # Basic format validation - should start with 'hh_' for HoneyHive keys
            if not validated.startswith(("hh_", "sk-")):
                # Warning: not an error to maintain backwards compatibility
                logger.debug(
                    "API key does not follow standard format (hh_* or sk_*): %s...",
                    validated[:8],
                    extra={
                        "honeyhive_data": {
                            "api_key_prefix": validated[:3] if validated else None
                        }
                    },
                )
        return validated

    @field_validator("project", mode="before")
    @classmethod
    def validate_project(cls, v: Any) -> Optional[str]:
        """Validate project name format with graceful degradation.

        Args:
            v: The project name to validate

        Returns:
            The validated and normalized project name, or None if invalid
        """
        validated = _safe_validate_string(v, "project", allow_none=True, default=None)
        if validated is not None:
            # Basic validation - no special characters that could cause issues
            invalid_chars = ["/", "\\", "?", "#", "&"]
            if any(char in validated for char in invalid_chars):
                logger.warning(
                    "Project name contains invalid characters. Using None.",
                    extra={
                        "honeyhive_data": {
                            "project": validated,
                            "invalid_chars": invalid_chars,
                        }
                    },
                )
                return None
        return validated

    @field_validator("test_mode", "verbose", mode="before")
    @classmethod
    def validate_boolean_fields(cls, v: Any) -> bool:
        """Validate boolean fields with graceful degradation.

        Args:
            v: The value to validate as boolean

        Returns:
            The validated boolean value, or False if invalid
        """
        if v is None:
            return False

        if isinstance(v, bool):
            return v

        if isinstance(v, str):
            # Handle common boolean string representations
            lower_v = v.lower().strip()
            if lower_v in ("true", "1", "yes", "on", "enabled"):
                return True
            if lower_v in ("false", "0", "no", "off", "disabled", ""):
                return False
            # Invalid boolean string - log warning and return default
            logger.warning(
                "Invalid boolean value: %s. Using False as default.",
                v,
                extra={"honeyhive_data": {"invalid_boolean": v}},
            )
            return False

        # For non-string, non-bool types, log warning and return default
        logger.warning(
            "Invalid boolean type: %s. Using False as default.",
            type(v).__name__,
            extra={
                "honeyhive_data": {"invalid_type": type(v).__name__, "value": str(v)}
            },
        )
        return False

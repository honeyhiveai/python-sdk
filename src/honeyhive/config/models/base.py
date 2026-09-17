"""Base configuration models for HoneyHive SDK.

This module provides the base Pydantic models that contain common fields
shared across different domain-specific configurations. This approach
eliminates duplication while maintaining type safety and validation.

The models follow graceful degradation principles - invalid values are logged
as warnings and replaced with safe defaults to prevent crashing the host application.
That rule covers values the SDK can do without. Two things raise instead: a
connection argument of the wrong type at an entry point (checked in
``honeyhive.config.resolved``; ``_present`` there says why), and a present
``ingestion_api_key`` of the wrong kind, here and in the resolver alike, because
whoever set it meant to, and dropping it silently would send telemetry with the
wrong key and lose it with no signal.
"""

# pylint: disable=duplicate-code
# Note: Pydantic model configuration patterns are intentionally similar
# across config modules for consistency. These provide standardized
# validation and environment variable handling.

import logging
import os
from typing import Any, FrozenSet, Optional

from pydantic import Field, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from ..resolved import (
    DEFAULT_API_URL,
    check_ingestion_api_key,
    environment_api_key,
    environment_api_url,
    environment_ingestion_api_key,
    normalize_api_url,
    settings_sources,
)

# Module logger for graceful degradation warnings
logger = logging.getLogger(__name__)

# The fields whose values come from honeyhive.config.resolved rather than from
# pydantic-settings' environment source: a constructor argument wins, otherwise
# the field's default_factory asks the resolver. The environment source skips
# these names so the prefix-derived spelling of server_url cannot bypass the
# resolver's precedence.
RESOLVED_FIELDS: FrozenSet[str] = frozenset(
    {"api_key", "ingestion_api_key", "server_url"}
)


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
        - api_key: HoneyHive API key for authentication (from HH_API_KEY)
        - ingestion_api_key: Ingestion API key for sending traces and events
          (from HH_INGESTION_API_KEY; optional, api_key is used for those
          requests when unset)
        - server_url: HoneyHive API URL (from HH_API_URL)
        - project: Deprecated project name (optional; backend infers scope from API key)
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

    api_key: Optional[str] = Field(
        default_factory=environment_api_key,
        description="HoneyHive API key for authentication",
        examples=["hh_1234567890abcdef"],
    )

    ingestion_api_key: Optional[str] = Field(
        default_factory=environment_ingestion_api_key,
        description=(
            "Ingestion API key (begins with hh_ingst_) sent with requests that "
            "create sessions or write events. When unset, api_key is used for "
            "those requests too."
        ),
        examples=["hh_ingst_..."],
    )

    server_url: str = Field(
        default_factory=environment_api_url,
        description="Custom HoneyHive server URL",
        examples=[
            DEFAULT_API_URL,
            "https://custom.honeyhive.com",
        ],
    )

    project: Optional[str] = Field(
        default=None,
        description=(
            "Deprecated. Legacy project name accepted for backwards compatibility "
            "but no longer used — the backend infers project context from the API "
            "key. Will be removed in v2.0."
        ),
        examples=["my-llm-project", "chatbot-v2"],
    )

    test_mode: bool = Field(
        default=False,
        description="Enable test mode (no data sent to backend)",
    )

    verbose: bool = Field(
        default=False,
        description="Enable verbose logging output and debug mode",
    )

    # Fields read the environment variable HH_<FIELD NAME>, so a new field needs
    # no alias. RESOLVED_FIELDS are the exception: their default_factory asks
    # honeyhive.config.resolved, so their variables and alternates are read in
    # exactly one place. The bare field name is not read: the README and the
    # docs site list only HH_ names, so a bare twin was never a documented
    # input and gets no compatibility path. Errors omit the offending value
    # because these fields hold credentials.
    model_config = SettingsConfigDict(
        validate_assignment=True,
        extra="forbid",  # Prevent accidental typos in field names
        case_sensitive=False,
        env_prefix="HH_",
        hide_input_in_errors=True,
    )

    @classmethod
    # pydantic-settings calls this hook with these six arguments, so the count
    # is the library's, not ours.
    # pylint: disable-next=too-many-positional-arguments
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Exclude the resolver's fields from the environment source."""
        del env_settings  # replaced by EnvSettingsSourceWithout
        return settings_sources(
            settings_cls,
            init_settings,
            dotenv_settings,
            file_secret_settings,
            excluded=RESOLVED_FIELDS,
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

    @field_validator("ingestion_api_key", mode="before")
    @classmethod
    def validate_ingestion_api_key(cls, v: Any) -> Optional[str]:
        """Apply the ingestion key's shape rule to an explicitly constructed value.

        Values from the resolver arrive already checked; this covers
        ``Config(ingestion_api_key=...)``. None and a blank string mean unset,
        so api_key is used for ingestion too. Anything else was set on purpose
        and must be an ingestion API key.

        Args:
            v: The ingestion API key value to validate

        Returns:
            The validated key, or None when unset

        Raises:
            ValueError: The value is not a string, or is present and is not an
                ingestion API key.
        """
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(
                f"ingestion_api_key must be a string, got {type(v).__name__}."
            )
        if not v.strip():
            return None
        return check_ingestion_api_key(v, "ingestion_api_key")

    @field_validator("server_url", mode="before")
    @classmethod
    def validate_server_url(cls, v: Any) -> str:
        """Apply the API URL shape rule to an explicitly constructed value.

        Values from the resolver arrive already normalized; this covers
        ``Config(server_url=...)``. Absent or blank means the default.

        Args:
            v: The server URL to validate

        Returns:
            The normalized URL, or the default when absent or malformed
        """
        validated = _safe_validate_string(
            v, "server_url", allow_none=False, default=DEFAULT_API_URL
        )
        if validated is None:
            return DEFAULT_API_URL
        return normalize_api_url(validated, "server_url")

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

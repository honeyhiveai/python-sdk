"""Tracer configuration models for HoneyHive SDK.

This module provides Pydantic models specifically for tracer initialization
and configuration. These models are used to reduce argument count in tracer
constructors while maintaining backwards compatibility.

The hybrid approach allows both old and new usage patterns:

Old Usage (Backwards Compatible):
    tracer = HoneyHiveTracer(api_key="...", project="...", verbose=True)

New Usage (Recommended):
    config = TracerConfig(api_key="...", project="...", verbose=True)
    tracer = HoneyHiveTracer(config=config)

All validation follows graceful degradation principles to prevent crashing
the host application.
"""

# pylint: disable=duplicate-code
# Note: Environment variable utility functions (_get_env_*) are intentionally
# duplicated across config modules to keep each module self-contained and
# avoid unnecessary coupling. These are simple, stable utility functions.

import logging
import uuid
from typing import Any, Dict, Optional

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import SettingsConfigDict

from .base import BaseHoneyHiveConfig, _safe_validate_string, _safe_validate_url

# Module logger for graceful degradation warnings
logger = logging.getLogger(__name__)


class TracerConfig(BaseHoneyHiveConfig):
    """Core tracer configuration with validation.

    This class defines the primary configuration parameters for initializing
    a HoneyHive tracer instance. It inherits common fields from BaseHoneyHiveConfig
    and adds tracer-specific parameters.

    Inherited Fields:
        - api_key: HoneyHive API key for authentication
        - project: Project name (required by backend API)
        - test_mode: Enable test mode (no data sent to backend)
        - verbose: Enable verbose logging output

    Tracer-Specific Fields:
        - session_name: Human-readable session identifier
        - source: Source environment identifier
        - server_url: Custom HoneyHive server URL (from HH_API_URL env var)
        - disable_http_tracing: Disable HTTP request tracing (disabled by default)
        - disable_batch: Disable batch processing of spans

    Example:
        >>> config = TracerConfig(
        ...     api_key="hh_1234567890abcdef",
        ...     project="my-llm-project",
        ...     session_name="user-chat-session",
        ...     source="production",
        ...     verbose=True
        ... )
        >>> tracer = HoneyHiveTracer(config=config)

        # Backwards compatible usage still works:
        >>> tracer = HoneyHiveTracer(
        ...     api_key="hh_1234567890abcdef",
        ...     project="my-llm-project",
        ...     verbose=True
        ... )
    """

    session_name: Optional[str] = Field(  # type: ignore[call-overload]
        None,
        description="Human-readable session identifier",
        examples=["user-chat-session", "batch-processing-job"],
    )

    source: str = Field(  # type: ignore[call-overload,pydantic-alias]
        default="dev",
        description="Source environment identifier",
        validation_alias=AliasChoices("HH_SOURCE", "source"),
        examples=["dev", "staging", "production"],
    )

    server_url: Optional[str] = Field(  # type: ignore[call-overload,pydantic-alias]
        default=None,
        description="Custom HoneyHive server URL",
        validation_alias=AliasChoices("HH_API_URL", "server_url"),
        examples=["https://api.honeyhive.ai", "https://custom.honeyhive.com"],
    )

    disable_http_tracing: bool = Field(  # type: ignore[call-overload,pydantic-alias]
        default=True,
        description="Disable HTTP request tracing (disabled by default)",
        validation_alias=AliasChoices(
            "HH_DISABLE_HTTP_TRACING", "disable_http_tracing"
        ),
    )

    disable_batch: bool = Field(  # type: ignore[call-overload,pydantic-alias]
        default=False,
        description="Disable batch processing of spans",
        validation_alias=AliasChoices("HH_DISABLE_BATCH", "disable_batch"),
    )

    disable_tracing: bool = Field(  # type: ignore[call-overload,pydantic-alias]
        default=False,
        description="Disable all tracing functionality",
        validation_alias=AliasChoices("HH_DISABLE_TRACING", "disable_tracing"),
    )

    # Dynamic Cache Configuration - Uses dynamic logic for performance optimization
    cache_enabled: bool = Field(  # type: ignore[call-overload,pydantic-alias]
        default=True,
        description="Enable dynamic caching for performance optimization",
        validation_alias=AliasChoices("HH_CACHE_ENABLED", "cache_enabled"),
    )

    cache_max_size: Optional[int] = Field(  # type: ignore[call-overload,pydantic-alias]
        None,
        description="Maximum cache size per cache type (dynamic sizing if None)",
        validation_alias=AliasChoices("HH_CACHE_MAX_SIZE", "cache_max_size"),
        examples=[1000, 5000, 10000],
    )

    cache_ttl: Optional[float] = Field(  # type: ignore[call-overload,pydantic-alias]
        None,
        description="Cache TTL in seconds (dynamic TTL based on cache type if None)",
        validation_alias=AliasChoices("HH_CACHE_TTL", "cache_ttl"),
        examples=[300.0, 600.0, 3600.0],
    )

    cache_cleanup_interval: Optional[float] = Field(  # type: ignore[call-overload,pydantic-alias]  # pylint: disable=line-too-long
        None,
        description="Cache cleanup interval in seconds (dynamic interval if None)",
        validation_alias=AliasChoices(
            "HH_CACHE_CLEANUP_INTERVAL", "cache_cleanup_interval"
        ),
        examples=[60.0, 120.0, 300.0],
    )

    # Session-related fields (for hybrid approach)
    session_id: Optional[str] = Field(  # type: ignore[call-overload]
        None,
        description="Existing session ID to attach to (must be valid UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    inputs: Optional[Dict[str, Any]] = Field(  # type: ignore[call-overload]
        None,
        description="Session input data",
        examples=[{"user_id": "123", "query": "Hello world"}],
    )

    link_carrier: Optional[Dict[str, Any]] = Field(  # type: ignore[call-overload]
        None,
        description="Context propagation carrier for distributed tracing",
        examples=[{"traceparent": "00-...", "baggage": "..."}],
    )

    # Evaluation-related fields (for hybrid approach)
    is_evaluation: bool = Field(
        default=False, description="Enable evaluation mode"
    )  # type: ignore[call-overload]

    run_id: Optional[str] = Field(  # type: ignore[call-overload]
        None,
        description="Evaluation run identifier",
        examples=["eval-run-123", "experiment-2024-01-15"],
    )

    dataset_id: Optional[str] = Field(  # type: ignore[call-overload]
        None,
        description="Dataset identifier for evaluation",
        examples=["dataset-456", "qa-dataset-v2"],
    )

    datapoint_id: Optional[str] = Field(  # type: ignore[call-overload]
        None,
        description="Specific datapoint identifier",
        examples=["datapoint-789", "question-42"],
    )

    model_config = SettingsConfigDict(
        validate_assignment=True,
        extra="forbid",
        case_sensitive=False,
    )

    @field_validator("server_url", mode="before")
    @classmethod
    def validate_server_url(cls, v: Any) -> Optional[str]:
        """Validate server URL format with graceful degradation.

        Args:
            v: The server URL to validate

        Returns:
            The validated server URL, or None if invalid
        """
        return _safe_validate_url(v, "server_url", allow_none=True, default=None)

    @field_validator("source", mode="before")
    @classmethod
    def validate_source(cls, v: Any) -> str:
        """Validate source environment with graceful degradation.

        Args:
            v: The source environment to validate

        Returns:
            The validated source environment, or "dev" if invalid
        """
        validated = _safe_validate_string(v, "source", allow_none=False, default="dev")
        return validated or "dev"  # Ensure we always return a non-None value

    @field_validator("session_id", mode="before")
    @classmethod
    def validate_session_id(cls, v: Any) -> Optional[str]:
        """Validate session ID format with graceful degradation.

        Args:
            v: The session ID to validate

        Returns:
            The validated and normalized session ID, or None if invalid
        """
        validated = _safe_validate_string(
            v, "session_id", allow_none=True, default=None
        )
        if validated is not None:
            try:
                # Validate UUID format
                uuid.UUID(validated)
                return validated.lower()  # Normalize to lowercase
            except ValueError:
                logger.warning(
                    "Invalid session_id: must be a valid UUID. Using None.",
                    extra={"honeyhive_data": {"session_id": validated}},
                )
                return None
        return validated

    @field_validator("run_id", "dataset_id", "datapoint_id", mode="before")
    @classmethod
    def validate_ids(cls, v: Any) -> Optional[str]:
        """Validate ID fields with graceful degradation.

        Args:
            v: The ID value to validate

        Returns:
            The validated ID, or None if invalid
        """
        return _safe_validate_string(v, "ID field", allow_none=True, default=None)


class SessionConfig(BaseHoneyHiveConfig):
    """Session-specific configuration parameters.

    This class handles configuration related to session management,
    including session linking and input/output data.

    Example:
        >>> session_config = SessionConfig(
        ...     session_id="550e8400-e29b-41d4-a716-446655440000",
        ...     inputs={"user_id": "123", "query": "Hello world"}
        ... )
        >>> tracer = HoneyHiveTracer(
        ...     config=tracer_config,
        ...     session_config=session_config
        ... )
    """

    session_id: Optional[str] = Field(  # type: ignore[call-overload]
        None,
        description="Existing session ID to attach to (must be valid UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    inputs: Optional[Dict[str, Any]] = Field(  # type: ignore[call-overload]
        None,
        description="Session input data",
        examples=[{"user_id": "123", "query": "Hello world"}],
    )

    link_carrier: Optional[Dict[str, Any]] = Field(  # type: ignore[call-overload]
        None,
        description="Context propagation carrier for distributed tracing",
        examples=[{"traceparent": "00-...", "baggage": "..."}],
    )

    model_config = SettingsConfigDict(
        validate_assignment=True,
        extra="forbid",
        case_sensitive=False,
    )

    @field_validator("session_id", mode="before")
    @classmethod
    def validate_session_id(cls, v: Any) -> Optional[str]:
        """Validate session ID format with graceful degradation.

        Args:
            v: The session ID to validate

        Returns:
            The validated and normalized session ID, or None if invalid
        """
        validated = _safe_validate_string(
            v, "session_id", allow_none=True, default=None
        )
        if validated is not None:
            try:
                # Validate UUID format
                uuid.UUID(validated)
                return validated.lower()  # Normalize to lowercase
            except ValueError:
                logger.warning(
                    "Invalid session_id: must be a valid UUID. Using None.",
                    extra={"honeyhive_data": {"session_id": validated}},
                )
                return None
        return validated


class EvaluationConfig(BaseHoneyHiveConfig):
    """Evaluation-specific configuration parameters.

    This class handles configuration for evaluation scenarios,
    including dataset and run management.

    Example:
        >>> eval_config = EvaluationConfig(
        ...     is_evaluation=True,
        ...     run_id="eval-run-123",
        ...     dataset_id="dataset-456",
        ...     datapoint_id="datapoint-789"
        ... )
        >>> tracer = HoneyHiveTracer(
        ...     config=tracer_config,
        ...     evaluation_config=eval_config
        ... )
    """

    is_evaluation: bool = Field(
        default=False, description="Enable evaluation mode"
    )  # type: ignore[call-overload]

    run_id: Optional[str] = Field(  # type: ignore[call-overload]
        None,
        description="Evaluation run identifier",
        examples=["eval-run-123", "experiment-2024-01-15"],
    )

    dataset_id: Optional[str] = Field(  # type: ignore[call-overload]
        None,
        description="Dataset identifier for evaluation",
        examples=["dataset-456", "qa-dataset-v2"],
    )

    datapoint_id: Optional[str] = Field(  # type: ignore[call-overload]
        None,
        description="Specific datapoint identifier",
        examples=["datapoint-789", "question-42"],
    )

    model_config = SettingsConfigDict(
        validate_assignment=True,
        extra="forbid",
        case_sensitive=False,
    )

    @field_validator("run_id", "dataset_id", "datapoint_id", mode="before")
    @classmethod
    def validate_ids(cls, v: Any) -> Optional[str]:
        """Validate ID fields with graceful degradation.

        Args:
            v: The ID value to validate

        Returns:
            The validated ID, or None if invalid
        """
        return _safe_validate_string(v, "ID field", allow_none=True, default=None)

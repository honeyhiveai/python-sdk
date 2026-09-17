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

Validation degrades gracefully for values the tracer can do without: a missing
or invalid setting is logged and defaulted rather than crashing the host
application. A present ``ingestion_api_key`` of the wrong kind is the one
exception and raises at construction; see ``BaseHoneyHiveConfig``.
"""

# pylint: disable=duplicate-code
# Note: Environment variable utility functions (_get_env_*) are intentionally
# duplicated across config modules to keep each module self-contained and
# avoid unnecessary coupling. These are simple, stable utility functions.

import logging
import uuid
from typing import Any, Dict, List, Literal, Optional

import requests
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
)

from .base import BaseHoneyHiveConfig, _safe_validate_string

# Module logger for graceful degradation warnings
logger = logging.getLogger(__name__)

# A field declared with validation_alias equal to its own name reads the bare
# environment variable it has always read (RUN_ID, not HH_RUN_ID), because
# env_prefix does not apply to an alias. These fields never had an HH_
# variable; only the API key and URL variables changed names, every other
# variable keeps the name it had. Dropping one of these aliases would move the
# field to HH_<NAME> and stop the bare name working.


class SpanNameFilter(BaseModel):
    """A single span name filter entry.

    Uses BaseModel (not BaseSettings) since these are nested data models
    that should not read from environment variables.

    Attributes:
        type: The filter matching strategy. Only "prefix" is currently supported.
        value: The value to match against span names.
    """

    type: Literal["prefix"] = Field(
        description='Filter matching strategy. Only "prefix" is currently supported.',
    )
    value: str = Field(
        description="The value to match against span names.",
        examples=["a2a.client.transports.jsonrpc"],
    )

    model_config = {"validate_assignment": True, "extra": "forbid"}


class SpanNameFilters(BaseModel):
    """Configuration for filtering spans by name.

    Uses BaseModel (not BaseSettings) since these are nested data models
    that should not read from environment variables.

    Supports both include (allow-list) and exclude (block-list) filters.
    If include is specified, only spans matching at least one include filter are kept.
    If exclude is specified, spans matching any exclude filter are dropped.
    If both are specified, a span must match include AND not match exclude.

    Example:
        >>> filters = SpanNameFilters(
        ...     exclude=[SpanNameFilter(type="prefix", value="a2a.client.transports")]
        ... )
    """

    include: Optional[List[SpanNameFilter]] = Field(
        default=None,
        description="Allow-list: only keep spans matching at least one filter.",
    )
    exclude: Optional[List[SpanNameFilter]] = Field(
        default=None,
        description="Block-list: drop spans matching any filter.",
    )

    model_config = {"validate_assignment": True, "extra": "forbid"}


class TracerConfig(BaseHoneyHiveConfig):
    """Core tracer configuration with validation.

    This class defines the primary configuration parameters for initializing
    a HoneyHive tracer instance. It inherits common fields from BaseHoneyHiveConfig
    and adds tracer-specific parameters.

    Inherited Fields:
        - api_key: HoneyHive API key for authentication
        - ingestion_api_key: Ingestion API key for sending traces and events
          (optional; api_key is used when unset)
        - server_url: Custom HoneyHive server URL (from HH_API_URL env var)
        - project: Deprecated project name (optional; backend infers scope from API key)
        - test_mode: Enable test mode (no data sent to backend)
        - verbose: Enable verbose logging output

    Tracer-Specific Fields:
        - session_name: Human-readable session identifier
        - source: Source environment identifier
        - disable_http_tracing: Disable HTTP request tracing (disabled by default)
        - disable_batch: Disable batch processing of spans
        - requests_session: Custom requests.Session for OTLP span export
          (caller-owned; not closed by the SDK on shutdown)

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

    session_name: Optional[str] = Field(
        None,
        validation_alias="session_name",
        description="Human-readable session identifier",
        examples=["user-chat-session", "batch-processing-job"],
    )

    source: str = Field(
        default="dev",
        description="Source environment identifier",
        examples=["dev", "staging", "production"],
    )

    disable_http_tracing: bool = Field(
        default=True,
        description="Disable HTTP request tracing (disabled by default)",
    )

    disable_batch: bool = Field(
        default=False,
        description="Disable batch processing of spans",
    )

    disable_tracing: bool = Field(
        default=False,
        description="Disable all tracing functionality",
    )

    span_name_filters: Optional[SpanNameFilters] = Field(
        default=None,
        validation_alias="span_name_filters",
        description=(
            "Filter spans by name using include/exclude lists. "
            "Each filter entry specifies a type ('prefix') and value to match. "
            "Excluded spans are dropped before enrichment and export."
        ),
        examples=[
            {"exclude": [{"type": "prefix", "value": "a2a.client.transports.jsonrpc"}]}
        ],
    )

    # OpenTelemetry Span Limits Configuration
    max_attributes: int = Field(
        default=1024,
        description=(
            "Maximum number of attributes per span "
            "(OpenTelemetry default: 128, HoneyHive default: 1024)"
        ),
        examples=[128, 256, 500, 1024, 2000],
    )

    max_events: int = Field(
        default=1024,
        description=(
            "Maximum number of events per span (matches max_attributes "
            "because events are flattened to pseudo-attributes)"
        ),
    )

    max_links: int = Field(
        default=128,
        description="Maximum number of links per span",
    )

    max_span_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB default
        description="Maximum total size of span (attributes + events + links) in bytes",
        examples=[1048576, 5242880, 10485760, 20971520],  # 1MB, 5MB, 10MB, 20MB
    )

    # Core Attribute Preservation Configuration
    preserve_core_attributes: bool = Field(
        default=True,
        description=(
            "Enable core attribute preservation to prevent FIFO eviction "
            "of critical attributes (session_id, event_type, etc.). When "
            "enabled, re-sets core attributes before span.end() to ensure "
            "they survive eviction. Disable only for debugging or extreme "
            "performance requirements."
        ),
    )

    # Dynamic Cache Configuration - Uses dynamic logic for performance optimization
    cache_enabled: bool = Field(
        default=True,
        description="Enable dynamic caching for performance optimization",
    )

    cache_max_size: Optional[int] = Field(
        None,
        description="Maximum cache size per cache type (dynamic sizing if None)",
        examples=[1000, 5000, 10000],
    )

    cache_ttl: Optional[float] = Field(
        None,
        description="Cache TTL in seconds (dynamic TTL based on cache type if None)",
        examples=[300.0, 600.0, 3600.0],
    )

    cache_cleanup_interval: Optional[float] = Field(
        None,
        description="Cache cleanup interval in seconds (dynamic interval if None)",
        examples=[60.0, 120.0, 300.0],
    )

    # HTTP session configuration
    requests_session: Optional[requests.Session] = Field(
        None,
        validation_alias="requests_session",
        description=(
            "Custom requests.Session for OTLP span export HTTP connections, "
            "e.g. with custom proxies, retries, or TLS settings. The caller "
            "owns the session; the SDK will not close it on shutdown. When "
            "unset, the SDK creates its own connection-pooled session."
        ),
    )

    # Session-related fields (for hybrid approach)
    session_id: Optional[str] = Field(
        None,
        validation_alias="session_id",
        description="Existing session ID to attach to (must be valid UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    inputs: Optional[Dict[str, Any]] = Field(
        None,
        validation_alias="inputs",
        description="Session input data",
        examples=[{"user_id": "123", "query": "Hello world"}],
    )

    link_carrier: Optional[Dict[str, Any]] = Field(
        None,
        validation_alias="link_carrier",
        description="Context propagation carrier for distributed tracing",
        examples=[{"traceparent": "00-...", "baggage": "..."}],
    )

    # Evaluation-related fields (for hybrid approach)
    is_evaluation: bool = Field(
        default=False,
        validation_alias="is_evaluation",
        description="Enable evaluation mode",
    )

    run_id: Optional[str] = Field(
        None,
        validation_alias="run_id",
        description="Evaluation run identifier",
        examples=["eval-run-123", "experiment-2024-01-15"],
    )

    dataset_id: Optional[str] = Field(
        None,
        validation_alias="dataset_id",
        description="Dataset identifier for evaluation",
        examples=["dataset-456", "qa-dataset-v2"],
    )

    datapoint_id: Optional[str] = Field(
        None,
        validation_alias="datapoint_id",
        description="Specific datapoint identifier",
        examples=["datapoint-789", "question-42"],
    )

    @field_serializer("requests_session", when_used="json")
    def _serialize_requests_session(
        self, value: Optional[requests.Session]
    ) -> Optional[str]:
        """Serialize the session as a placeholder in JSON mode.

        Session objects aren't JSON-serializable and would otherwise raise
        PydanticSerializationError. Python-mode model_dump() is unaffected —
        config merging relies on it to pass the session through by reference.

        Args:
            value: The configured session, if any

        Returns:
            A placeholder string when a session is set, otherwise None
        """
        return "<requests.Session>" if value is not None else None

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

    session_id: Optional[str] = Field(
        None,
        validation_alias="session_id",
        description="Existing session ID to attach to (must be valid UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    skip_backend_session_creation: bool = Field(
        default=False,
        validation_alias="skip_backend_session_creation",
        description=(
            "If True, skip the init-time backend session creation call. "
            "If a valid session_id is also provided, the SDK trusts that the "
            "session already exists on the backend. Otherwise, callers are "
            "expected to manage session_ids via per-request "
            "create_session(session_id=<uuid>, skip_api_call=True) calls. "
            "Note: an invalid session_id (e.g. non-UUID) triggers the "
            "degraded-mode path and still calls the backend."
        ),
    )

    inputs: Optional[Dict[str, Any]] = Field(
        None,
        validation_alias="inputs",
        description="Session input data",
        examples=[{"user_id": "123", "query": "Hello world"}],
    )

    link_carrier: Optional[Dict[str, Any]] = Field(
        None,
        validation_alias="link_carrier",
        description="Context propagation carrier for distributed tracing",
        examples=[{"traceparent": "00-...", "baggage": "..."}],
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
        default=False,
        validation_alias="is_evaluation",
        description="Enable evaluation mode",
    )

    run_id: Optional[str] = Field(
        None,
        validation_alias="run_id",
        description="Evaluation run identifier",
        examples=["eval-run-123", "experiment-2024-01-15"],
    )

    dataset_id: Optional[str] = Field(
        None,
        validation_alias="dataset_id",
        description="Dataset identifier for evaluation",
        examples=["dataset-456", "qa-dataset-v2"],
    )

    datapoint_id: Optional[str] = Field(
        None,
        validation_alias="datapoint_id",
        description="Specific datapoint identifier",
        examples=["datapoint-789", "question-42"],
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

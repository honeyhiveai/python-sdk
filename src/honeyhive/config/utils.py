"""Configuration utilities for HoneyHive SDK.

This module provides utility functions for working with configuration objects,
including merging config objects with individual parameters for backwards
compatibility and creating unified flattened configurations.
"""

# pylint: disable=too-many-branches
# Justification: Config merging logic requires comprehensive validation branches

from typing import Any, Optional, Tuple

from ..utils.dotdict import DotDict
from .models import (
    APIClientConfig,
    EvaluationConfig,
    ExperimentConfig,
    HTTPClientConfig,
    OTLPConfig,
    SessionConfig,
    TracerConfig,
)


def merge_configs_with_params(
    config: Optional[TracerConfig] = None,
    session_config: Optional[SessionConfig] = None,
    evaluation_config: Optional[EvaluationConfig] = None,
    **individual_params: Any,
) -> Tuple[TracerConfig, SessionConfig, EvaluationConfig]:
    """Merge config objects with individual parameters for backwards compatibility.

    This function enables the hybrid approach where both config objects and
    individual parameters can be used. Individual parameters take precedence
    over config object values to maintain backwards compatibility.

    Args:
        config: Core tracer configuration object
        session_config: Session-specific configuration object
        evaluation_config: Evaluation-specific configuration object
        **individual_params: Individual parameter overrides for backwards compatibility

    Returns:
        Tuple of (merged_tracer_config, merged_session_config, merged_evaluation_config)

    Example:
        >>> # Using config objects
        >>> tracer_cfg = TracerConfig(api_key="hh_123", verbose=True)
        >>> session_cfg = SessionConfig(inputs={"user": "123"})
        >>> merged = merge_configs_with_params(
        ...     config=tracer_cfg,
        ...     session_config=session_cfg
        ... )

        >>> # Using individual parameters (backwards compatible)
        >>> merged = merge_configs_with_params(
        ...     api_key="hh_123",
        ...     verbose=True,
        ...     inputs={"user": "123"}
        ... )

        >>> # Mixed usage (individual params override config)
        >>> merged = merge_configs_with_params(
        ...     config=tracer_cfg,  # has verbose=True
        ...     verbose=False       # overrides config
        ... )
    """
    # Start with defaults or provided configs
    tracer_config = config or TracerConfig()
    session_cfg = session_config or SessionConfig()
    eval_cfg = evaluation_config or EvaluationConfig()

    # Override tracer config with individual parameters
    tracer_overrides = {}
    for field in TracerConfig.model_fields.keys():
        if field in individual_params:
            tracer_overrides[field] = individual_params[field]

    if tracer_overrides:
        tracer_config = tracer_config.model_copy(update=tracer_overrides)

    # Override session config with individual parameters
    session_overrides = {}
    for field in SessionConfig.model_fields.keys():
        if field in individual_params:
            session_overrides[field] = individual_params[field]

    if session_overrides:
        session_cfg = session_cfg.model_copy(update=session_overrides)

    # Override evaluation config with individual parameters
    eval_overrides = {}
    for field in EvaluationConfig.model_fields.keys():
        if field in individual_params:
            eval_overrides[field] = individual_params[field]

    if eval_overrides:
        eval_cfg = eval_cfg.model_copy(update=eval_overrides)

    return tracer_config, session_cfg, eval_cfg


def create_unified_config(
    config: Optional[TracerConfig] = None,
    session_config: Optional[SessionConfig] = None,
    evaluation_config: Optional[EvaluationConfig] = None,
    **individual_params: Any,
) -> DotDict:
    """Create a unified nested configuration from all config sources.

    This function merges all configuration types (TracerConfig, SessionConfig,
    EvaluationConfig, HTTPClientConfig, OTLPConfig, APIClientConfig, ExperimentConfig)
    into a nested DotDict structure that eliminates key collisions and provides
    clear namespacing for different config types.

    Structure:
        - TracerConfig fields at root level (most commonly accessed)
        - Specialized configs nested: config.session.*, config.evaluation.*, etc.
        - For colliding fields: More specific configs override base configs at root

    Priority Order (for fields that exist in multiple configs):
        1. individual_params (highest - backwards compatibility)
        2. SessionConfig (session-specific overrides)
        3. EvaluationConfig (evaluation-specific overrides)
        4. TracerConfig (base defaults)

    Args:
        config: Core tracer configuration object
        session_config: Session-specific configuration object
        evaluation_config: Evaluation-specific configuration object
        **individual_params: Individual parameter overrides for backwards compatibility

    Returns:
        DotDict: Unified configuration with nested structure accessible
        via both config.field_name and config['field_name'] patterns.

    Example:
        >>> # Basic usage
        >>> config = TracerConfig(api_key="key", project="proj")
        >>> unified = create_unified_config(config=config)
        >>> unified.api_key  # "key" (TracerConfig at root)
        >>> unified.http.timeout  # 30.0 (HTTPClientConfig nested)

        >>> # Field collision handling (SessionConfig overrides TracerConfig)
        >>> tracer_cfg = TracerConfig(api_key="key1", session_id=None)
        >>> session_cfg = SessionConfig(session_id="550e8400-...")
        >>> unified = create_unified_config(
        ...     config=tracer_cfg, session_config=session_cfg
        ... )
        >>> unified.session_id  # "550e8400-..." (from SessionConfig)
        >>> unified.session.session_id  # Also "550e8400-..."
    """
    # First merge the main configs with individual params
    tracer_config, session_config_merged, evaluation_config_merged = (
        merge_configs_with_params(
            config=config,
            session_config=session_config,
            evaluation_config=evaluation_config,
            **individual_params,
        )
    )

    # Create unified result with nested structure
    unified = DotDict()

    # 1. TracerConfig fields at root level (most commonly accessed)
    if tracer_config:
        unified.update(tracer_config.model_dump())

    # 2. Create nested configs to avoid key collisions
    # HTTP Client Configuration
    default_http_config = HTTPClientConfig()
    unified.http = DotDict(default_http_config.model_dump())

    # OTLP Configuration
    default_otlp_config = OTLPConfig()
    unified.otlp = DotDict(default_otlp_config.model_dump())

    # API Client Configuration
    default_api_config = APIClientConfig()
    unified.api = DotDict(default_api_config.model_dump())

    # Experiment Configuration
    default_experiment_config = ExperimentConfig()
    unified.experiment = DotDict(default_experiment_config.model_dump())

    # Session Configuration (nested to avoid collisions with TracerConfig)
    if session_config_merged:
        unified.session = DotDict(session_config_merged.model_dump())
    else:
        unified.session = DotDict()

    # Evaluation Configuration (nested to avoid collisions with TracerConfig)
    if evaluation_config_merged:
        unified.evaluation = DotDict(evaluation_config_merged.model_dump())
    else:
        unified.evaluation = DotDict()

    # 2.5. Promote specialized config values to root level for colliding fields
    # Priority: SessionConfig/EvaluationConfig > TracerConfig (more specific wins)
    # This fixes the field collision bug where SessionConfig.session_id was hidden
    # Only promote when specialized configs were explicitly provided (not defaults)

    # Helper to determine if a field was explicitly set vs using default
    def was_field_explicitly_set(config_obj: Any, field_name: str) -> bool:
        """Check if a field was explicitly set by user or is just a default."""
        if config_obj is None:
            return False
        # Check if the field exists in the original config object's __dict__
        # or __pydantic_fields_set__ (Pydantic v2 tracks explicitly set fields)
        if hasattr(config_obj, "__pydantic_fields_set__"):
            return field_name in config_obj.__pydantic_fields_set__
        # Fallback: assume explicitly set if value differs from field default
        if hasattr(type(config_obj), "model_fields"):
            field_info = type(config_obj).model_fields.get(field_name)
            if field_info and hasattr(field_info, "default"):
                return bool(getattr(config_obj, field_name, None) != field_info.default)
        return True  # Conservative: promote if we can't determine

    # Promote EvaluationConfig values to root (lower priority)
    # Only if evaluation_config was actually provided by user
    if evaluation_config is not None and evaluation_config_merged:
        for field in EvaluationConfig.model_fields.keys():
            nested_value = unified.evaluation.get(field)
            # Only promote if field was explicitly set and value is not None
            if nested_value is not None and was_field_explicitly_set(
                evaluation_config, field
            ):
                unified[field] = nested_value

    # Promote SessionConfig values to root (higher priority - overrides evaluation)
    # Only if session_config was actually provided by user
    if session_config is not None and session_config_merged:
        for field in SessionConfig.model_fields.keys():
            nested_value = unified.session.get(field)
            # Only promote if field was explicitly set and value is not None
            if nested_value is not None and was_field_explicitly_set(
                session_config, field
            ):
                unified[field] = nested_value

    # 3. Handle individual params - route to appropriate nested config or root
    # AND promote SessionConfig/EvaluationConfig params to root
    # (for field collision handling)
    for param, value in individual_params.items():
        # Route params to appropriate nested config based on known field sets
        # Use try/except for safe field checking
        try:
            if hasattr(SessionConfig, "model_fields") and param in dict(
                SessionConfig.model_fields
            ):
                unified.session[param] = value
                # Also promote to root
                # (SessionConfig has highest priority for colliding fields)
                unified[param] = value
                continue
        except (AttributeError, TypeError):
            pass

        try:
            if hasattr(EvaluationConfig, "model_fields") and param in dict(
                EvaluationConfig.model_fields
            ):
                unified.evaluation[param] = value
                # Also promote to root
                # (EvaluationConfig overrides TracerConfig for colliding fields)
                unified[param] = value
                continue
        except (AttributeError, TypeError):
            pass

        try:
            if hasattr(HTTPClientConfig, "model_fields") and param in dict(
                HTTPClientConfig.model_fields
            ):
                unified.http[param] = value
                continue
        except (AttributeError, TypeError):
            pass

        try:
            if hasattr(OTLPConfig, "model_fields") and param in dict(
                OTLPConfig.model_fields
            ):
                unified.otlp[param] = value
                continue
        except (AttributeError, TypeError):
            pass

        try:
            if hasattr(APIClientConfig, "model_fields") and param in dict(
                APIClientConfig.model_fields
            ):
                unified.api[param] = value
                continue
        except (AttributeError, TypeError):
            pass

        try:
            if hasattr(ExperimentConfig, "model_fields") and param in dict(
                ExperimentConfig.model_fields
            ):
                unified.experiment[param] = value
                continue
        except (AttributeError, TypeError):
            pass

        # TracerConfig fields or unknown params go to root
        unified[param] = value

    return unified

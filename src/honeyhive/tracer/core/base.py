"""Base tracer implementation with initialization and core infrastructure.

This module provides the foundational HoneyHive tracer class with dynamic
initialization, configuration management, and utility classes. It uses
dynamic logic for flexible configuration handling and graceful degradation.
"""

# pylint: disable=too-many-lines
# Justification: Base tracer class requires extensive functionality including
# dynamic configuration, cache management, resource detection, attribute
# normalization, and backward compatibility. Splitting would break cohesion.

# pylint: disable=duplicate-code
# Justification: Legitimate shared patterns with decorator and operations mixins.
# Duplicate code represents common dynamic attribute normalization patterns
# shared across core mixin classes for consistent behavior.

import os
import platform
import threading
from typing import Any, Dict, Optional, Self, Union

from opentelemetry.trace import INVALID_SPAN_CONTEXT, SpanKind

from ...api.client import HoneyHive
from ...api.session import SessionAPI
from ...config import create_unified_config
from ...config.models import EvaluationConfig, SessionConfig, TracerConfig
from ...utils.cache import CacheConfig, CacheManager
from ...utils.dotdict import DotDict
from ...utils.logger import safe_log
from ..infra import build_otel_resources
from ..instrumentation.initialization import initialize_tracer_instance
from ..lifecycle.core import get_lock_config

# Removed TracerConfigInterface - replaced with DotDict config


# Sentinel type for detecting explicitly passed parameters
class _ExplicitType:  # pylint: disable=too-few-public-methods
    """Sentinel type for detecting explicitly passed vs default parameters."""

    def __repr__(self) -> str:
        return "<EXPLICIT>"


_EXPLICIT = _ExplicitType()


class NoOpSpan:
    """No-op span implementation for graceful degradation.

    This class provides a safe default span that implements the same interface
    as a real span but performs no operations. This follows OpenTelemetry best
    practices for error handling - never return None, always return a usable object.
    """

    def __init__(self) -> None:
        """Initialize no-op span with safe defaults."""
        self.kind = SpanKind.INTERNAL
        self._attributes: Dict[str, Any] = {}

    def set_attribute(self, key: str, value: Any) -> None:
        """Set attribute (no-op)."""

    def set_attributes(self, attributes: Dict[str, Any]) -> None:
        """Set multiple attributes (no-op)."""

    def add_event(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        """Add event (no-op)."""

    def record_exception(
        self,
        exception: Exception,
        attributes: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None,
        escaped: bool = False,
    ) -> None:
        """Record exception (no-op)."""

    def set_status(self, status: Any, description: Optional[str] = None) -> None:
        """Set status (no-op)."""

    def update_name(self, name: str) -> None:
        """Update name (no-op)."""

    def end(self, end_time: Optional[int] = None) -> None:
        """End span (no-op)."""

    def is_recording(self) -> bool:
        """Check if span is recording (always False for no-op)."""
        return False

    def get_span_context(self) -> Any:
        """Get span context (returns invalid context)."""
        return INVALID_SPAN_CONTEXT


class HoneyHiveTracerBase:  # pylint: disable=too-many-instance-attributes
    """Base HoneyHive tracer with dynamic initialization and configuration.

    This base class provides the core infrastructure for HoneyHive tracing
    including dynamic configuration handling, initialization logic, and
    foundational properties. It uses dynamic patterns for flexible setup.

    Note: too-many-instance-attributes disabled - Base tracer class requires extensive
    attributes for configuration management, state tracking, API clients, threading
    locks, and backward compatibility support.
    """

    # Type annotations for instance attributes
    config: DotDict
    client: Optional["HoneyHive"]
    session_api: Optional["SessionAPI"]
    _baggage_lock: "threading.Lock"
    _session_id: Optional[str]
    tracer: Any  # OpenTelemetry Tracer instance

    # Sentinel object moved to module level with proper typing

    # pylint: disable=too-many-arguments
    # Justification: This __init__ supports both new Pydantic config approach
    # and backwards compatibility. High argument count necessary for API compatibility.
    def __init__(
        self,
        # New Pydantic config approach (recommended)
        config: Optional["TracerConfig"] = None,
        session_config: Optional["SessionConfig"] = None,
        evaluation_config: Optional["EvaluationConfig"] = None,
        *,  # Force all remaining arguments to be keyword-only
        # Backwards compatibility - all original parameters (keyword-only)
        # Use _EXPLICIT as sentinel to detect explicitly passed vs default values
        api_key: Union[Optional[str], _ExplicitType] = _EXPLICIT,
        project: Union[Optional[str], _ExplicitType] = _EXPLICIT,
        session_name: Union[Optional[str], _ExplicitType] = _EXPLICIT,
        source: Union[str, _ExplicitType] = _EXPLICIT,
        server_url: Union[Optional[str], _ExplicitType] = _EXPLICIT,
        session_id: Union[Optional[str], _ExplicitType] = _EXPLICIT,
        disable_http_tracing: Union[Optional[bool], _ExplicitType] = _EXPLICIT,
        disable_batch: Union[bool, _ExplicitType] = _EXPLICIT,
        verbose: Union[bool, _ExplicitType] = _EXPLICIT,
        inputs: Union[Optional[Dict[str, Any]], _ExplicitType] = _EXPLICIT,
        is_evaluation: Union[bool, _ExplicitType] = _EXPLICIT,
        run_id: Union[Optional[str], _ExplicitType] = _EXPLICIT,
        dataset_id: Union[Optional[str], _ExplicitType] = _EXPLICIT,
        datapoint_id: Union[Optional[str], _ExplicitType] = _EXPLICIT,
        link_carrier: Union[Optional[Dict[str, Any]], _ExplicitType] = _EXPLICIT,
        test_mode: Union[bool, _ExplicitType] = _EXPLICIT,
        **kwargs: Any,
    ) -> None:
        """Initialize the HoneyHive tracer using dynamic configuration merging.

        This constructor uses dynamic logic to merge Pydantic config objects with
        backward-compatible parameters, allowing flexible initialization patterns.

        New Pydantic Config Approach (Recommended):
            config = TracerConfig(api_key="...", project="...", verbose=True)
            tracer = HoneyHiveTracer(config=config)

        Backwards Compatible Approach (Still Supported):
            tracer = HoneyHiveTracer(api_key="...", project="...", verbose=True)

        :param config: Pydantic tracer configuration object (recommended)
        :type config: Optional[TracerConfig]
        :param session_config: Session-specific configuration
        :type session_config: Optional[SessionConfig]
        :param evaluation_config: Evaluation-specific configuration
        :type evaluation_config: Optional[EvaluationConfig]
        """
        # Multi-instance architecture uses safe_log() for all logging
        # No direct logger assignment needed - safe_log handles per-instance logging

        # Dynamic configuration merging - handles both new and legacy patterns
        # Create parameter dict with only explicitly provided parameters
        explicit_params = {}

        # Map of parameter names to their values - only include if not sentinel
        param_mapping = {
            "api_key": api_key,
            "project": project,
            "session_name": session_name,
            "source": source,
            "server_url": server_url,
            "session_id": session_id,
            "disable_http_tracing": disable_http_tracing,
            "disable_batch": disable_batch,
            "verbose": verbose,
            "inputs": inputs,
            "is_evaluation": is_evaluation,
            "run_id": run_id,
            "dataset_id": dataset_id,
            "datapoint_id": datapoint_id,
            "link_carrier": link_carrier,
            "test_mode": test_mode,
        }

        # Only include explicitly provided parameters (not sentinel values)
        for param_name, value in param_mapping.items():
            if value is not _EXPLICIT:
                explicit_params[param_name] = value

        # Use centralized config merging from config module
        self.config = create_unified_config(
            config=config,
            session_config=session_config,
            evaluation_config=evaluation_config,
            **explicit_params,
            **kwargs,
        )

        # Initialize core instance attributes dynamically
        self._initialize_core_attributes()

        # Initialize OpenTelemetry components using dynamic initialization
        self._initialize_otel_components()

        # Set up API clients using dynamic configuration
        self._initialize_api_clients()

    # Configuration merging moved to config module - see create_unified_config()

    def _initialize_core_attributes(self) -> None:
        """Initialize core tracer attributes using dynamic configuration."""
        # Extract configuration values dynamically
        config = self.config

        # Core tracer state
        self._initialized = False
        self._instance_shutdown = (
            False  # Instance-specific shutdown flag for multi-instance architecture
        )
        self.test_mode = config.get("test_mode", False)

        # Core configuration attributes
        self.api_key = config.get("api_key")
        self.server_url = config.get("server_url")
        self.verbose = config.get("verbose", False)

        # Session management attributes (both public and private for compatibility)
        self.session_name = config.get("session_name")
        # session_id is now properly promoted to root by create_unified_config()
        # Fallback to nested location for extra safety
        self.session_id = config.get("session_id") or (
            config.get("session", {}).get("session_id")
            if isinstance(config.get("session"), dict)
            else None
        )

        self._session_name = self.session_name  # Private version for internal use
        self._session_id = self.session_id  # Private version for internal use

        # Evaluation attributes
        self.is_evaluation = config.get("is_evaluation", False)
        self.run_id = config.get("run_id")
        self.dataset_id = config.get("dataset_id")
        self.datapoint_id = config.get("datapoint_id")

        # Legacy compatibility attributes
        self.project = config.get("project")
        self.source = config.get("source")

        # Dynamic Cache Management - Initialize per-instance cache manager
        self._cache_manager = self._initialize_cache_manager(config)

        # Initialize evaluation context
        self._evaluation_context: Dict[str, Any] = {}
        # Dynamic evaluation context setup
        if self.is_evaluation:
            self._setup_evaluation_context_dynamically(config)

        # OpenTelemetry components (initialized later)
        self.provider = None
        self.tracer = None
        self.span_processor = None
        self.propagator = None
        # Provider management for multi-instance architecture
        self.is_main_provider = False
        self._tracer_id = None

        # Per-instance locking for high-concurrency scenarios
        self._baggage_lock = threading.Lock()
        self._instance_lock = threading.RLock()  # Reentrant for same thread
        self._flush_lock = threading.Lock()  # Separate lock for flush operations

    def _initialize_otel_components(self) -> None:
        """Initialize OpenTelemetry components using dynamic initialization."""
        try:
            # Use dynamic initialization helper
            initialize_tracer_instance(self)
            self._initialized = True

            safe_log(
                self,
                "info",
                "HoneyHive tracer initialized successfully",
                honeyhive_data={
                    "architecture": "multi-instance",
                    "test_mode": self.test_mode,
                    "has_session": bool(self._session_id),
                },
            )
        except Exception as e:
            safe_log(
                self,
                "error",
                "Failed to initialize tracer: %s",
                str(e),
                honeyhive_data={"error_type": type(e).__name__},
            )
            # Graceful degradation - tracer remains usable but in no-op mode
            self._initialized = False

    def _initialize_api_clients(self) -> None:
        """Initialize API clients using dynamic configuration."""
        config = self.config

        # Initialize HoneyHive API client dynamically
        api_params = self._extract_api_parameters_dynamically(config)
        if api_params:
            try:
                self.client = HoneyHive(**api_params, tracer_instance=self)
                self.session_api = SessionAPI(self.client)
            except Exception as e:
                safe_log(
                    self,
                    "warning",
                    "Failed to initialize API client: %s",
                    str(e),
                    honeyhive_data={"error_type": type(e).__name__},
                )
                # Graceful degradation
                self.client = None
                self.session_api = None
        else:
            self.client = None
            self.session_api = None

    def _extract_api_parameters_dynamically(
        self, config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Dynamically extract API parameters from configuration."""
        # Required parameters for tracer (api_key for API client, project for tracer)
        api_key = config.get("api_key")
        project = config.get("project")

        # Both api_key and project are required for tracer functionality
        if not api_key or not project:
            return None

        # Build API parameters dynamically (only params accepted by HoneyHive API)
        api_params = {}

        # Map configuration keys to API client parameters (excluding project)
        param_mapping = {
            "api_key": "api_key",
            "server_url": "server_url",
            "timeout": "timeout",
            "test_mode": "test_mode",
            "verbose": "verbose",
        }

        for config_key, api_key_param in param_mapping.items():
            value = config.get(config_key)
            if value is not None:
                api_params[api_key_param] = value

        return api_params

    # Legacy config resolution methods removed - all consumers should use
    # self.config.get() directly. The unified DotDict config object from
    # create_unified_config() handles all resolution

    def _initialize_cache_manager(self, config: Any) -> Optional[CacheManager]:
        """Initialize cache manager with config-driven defaults.

        Args:
            config: Configuration object (dict or Pydantic model)

        Returns:
            CacheManager instance if caching is enabled, None otherwise
        """
        # Check if caching is enabled
        cache_enabled = config.get("cache_enabled", True)
        if not cache_enabled:
            safe_log(self, "debug", "Cache disabled via configuration")
            return None

        # Generate unique instance ID for multi-instance isolation
        instance_id = f"tracer_{id(self)}_{getattr(self, '_tracer_id', 'unknown')}"

        # Use config-driven defaults with sensible fallbacks
        cache_config = CacheConfig(
            max_size=config.get("cache_max_size", 1000),
            default_ttl=config.get("cache_ttl", 300.0),
            cleanup_interval=60.0,  # Static - no need for dynamic calculation
            enable_stats=True,
        )

        try:
            cache_manager = CacheManager(instance_id=instance_id, config=cache_config)
            safe_log(
                self, "debug", "Initialized cache manager for instance %s", instance_id
            )
            return cache_manager
        except Exception as e:
            # Graceful degradation - cache failures should not break tracer
            safe_log(self, "warning", "Failed to initialize cache manager: %s", e)
            return None

    def _setup_evaluation_context_dynamically(self, config: Dict[str, Any]) -> None:
        """Dynamically set up evaluation context from configuration."""
        # Extract evaluation-specific fields dynamically
        evaluation_fields = ["run_id", "dataset_id", "datapoint_id", "is_evaluation"]

        for field in evaluation_fields:
            value = config.get(field)
            if value is not None:
                self._evaluation_context[field] = value

    def _merge_configs_internally(
        self,
        config: Optional[TracerConfig] = None,
        session_config: Optional[SessionConfig] = None,
        evaluation_config: Optional[EvaluationConfig] = None,
        **individual_params: Any,
    ) -> tuple[TracerConfig, SessionConfig, EvaluationConfig]:
        """Internal method to merge config objects with individual parameters.

        This method encapsulates the hybrid assembly logic within the class,
        ensuring that the external interface only exposes the final merged result.
        Individual parameters take precedence over config object values for
        backwards compatibility.
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

    def _acquire_instance_lock_with_timeout(
        self, timeout: Optional[float] = None
    ) -> bool:
        """Acquire per-instance lock with environment-optimized timeout.

        Args:
            timeout: Optional custom timeout. If None, uses environment-optimized value

        Returns:
            bool: True if lock was acquired, False if timeout occurred

        Examples:
            >>> # Auto-optimized timeout
            >>> if tracer._acquire_instance_lock_with_timeout():
            ...     try:
            ...         # Perform instance-specific operation
            ...         pass
            ...     finally:
            ...         tracer._release_instance_lock()
        """
        if timeout is None:
            config = get_lock_config()
            timeout = config.get("lifecycle_timeout", 1.0)

        # Ensure timeout is not None for type safety
        effective_timeout = timeout if timeout is not None else 1.0
        return self._instance_lock.acquire(timeout=effective_timeout)

    def _release_instance_lock(self) -> None:
        """Release per-instance lock."""
        try:
            self._instance_lock.release()
        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host app
            safe_log(
                self,
                "debug",
                "Failed to release instance lock",
                honeyhive_data={"error_type": type(e).__name__},
            )

    @classmethod
    def reset(cls) -> None:
        """Reset static state for testing purposes.

        This method provides backward compatibility for test environments
        that expect a reset capability. In the multi-instance architecture,
        this primarily delegates to the lifecycle management system.
        """
        # In multi-instance architecture, reset is handled by lifecycle management
        # This is a no-op for backward compatibility
        return None

    @classmethod
    def init(
        cls,
        config: Optional["TracerConfig"] = None,
        session_config: Optional["SessionConfig"] = None,
        evaluation_config: Optional["EvaluationConfig"] = None,
        **kwargs: Any,
    ) -> Self:
        """Factory method for creating tracer instances with dynamic configuration.

        This is a simple pass-through to __init__ for backwards compatibility.

        Args:
            config: Pydantic tracer configuration
            session_config: Session-specific configuration
            evaluation_config: Evaluation-specific configuration
            **kwargs: Backward-compatible parameters

        Returns:
            Initialized HoneyHive tracer instance
        """
        # Simple pass-through to constructor
        return cls(
            config=config,
            session_config=session_config,
            evaluation_config=evaluation_config,
            **kwargs,
        )

    def _should_create_session_automatically(self) -> bool:
        """Dynamically determine if session should be created automatically."""
        # Check if we have the necessary components and configuration
        return (
            self.session_api is not None
            and self._session_name is not None
            and self._session_id is None  # Don't create if already have session_id
            and not self.test_mode  # Skip in test mode
        )

    def _create_session_dynamically(self) -> None:
        """Dynamically create a session using available configuration."""
        if not self.session_api or not self._session_name:
            return

        try:
            # Build session creation parameters dynamically
            session_params = self._build_session_parameters_dynamically()

            # Create session via API
            response = self.session_api.create_session_from_dict(session_params)

            if hasattr(response, "session_id"):
                # pylint: disable=attribute-defined-outside-init
                # Justification: _session_id is properly initialized in __init__.
                # This is legitimate reassignment during dynamic session creation,
                # not a first-time attribute definition.
                self._session_id = response.session_id
                safe_log(
                    self,
                    "info",
                    "Created session automatically: %s",
                    str(self._session_id),
                    honeyhive_data={"session_name": self._session_name},
                )

        except Exception as e:
            safe_log(
                self,
                "warning",
                "Failed to create session automatically: %s",
                str(e),
                honeyhive_data={"session_name": self._session_name},
            )

    def _build_session_parameters_dynamically(self) -> Dict[str, Any]:
        """Dynamically build session creation parameters."""
        params = {"session_name": self._session_name}

        # Add evaluation context if available
        if self._evaluation_context:
            params.update(self._evaluation_context)

        # Add other dynamic parameters from configuration
        config = self.config
        optional_params = ["source", "inputs"]

        for param in optional_params:
            value = config.get(param)
            if value is not None:
                params[param] = value

        return params

    # Properties with dynamic access patterns
    @property
    def project_name(self) -> Optional[str]:
        """Get project name from unified configuration."""
        result = self.config.get("project")
        return str(result) if result is not None else None

    @property
    def source_environment(self) -> str:
        """Get source environment from unified configuration."""
        result = self.config.get("source", "dev")
        return str(result)

    @property
    def is_initialized(self) -> bool:
        """Check if tracer is properly initialized."""
        return self._initialized

    @property
    def is_test_mode(self) -> bool:
        """Check if tracer is in test mode."""
        return bool(self.test_mode)

    # Removed config_interface property - replaced with DotDict config
    # Users should now use tracer.config directly for all configuration access

    def _normalize_attribute_key_dynamically(self, key: str) -> str:
        """Dynamically normalize attribute keys with caching for performance.

        This method uses dynamic caching to optimize repeated attribute key
        normalization, which is critical for high-throughput tracing scenarios.
        """
        if not isinstance(key, str):
            key = str(key)

        if not self._is_caching_enabled() or not self._cache_manager:
            return self._perform_key_normalization(key)

        # Use cache manager's domain-specific method
        attr_key = f"key_norm:{hash(key)}"
        result = self._cache_manager.get_cached_attributes(
            attr_key=attr_key,
            normalizer_func=lambda: self._perform_key_normalization(key),
        )
        return str(result)  # Ensure string return type

    def _perform_key_normalization(self, key: str) -> str:
        """Perform the actual key normalization logic."""
        # Replace invalid characters dynamically
        normalized = key.replace(".", "_").replace("-", "_").replace(" ", "_")

        # Ensure valid identifier
        if not normalized or normalized[0].isdigit():
            normalized = f"attr_{normalized}"

        return normalized

    def _normalize_attribute_value_dynamically(self, value: Any) -> Any:
        """Dynamically normalize attribute values with caching for performance.

        This method uses dynamic caching to optimize repeated attribute value
        normalization, especially for complex objects that require string conversion.
        """
        # Handle None values immediately (no caching needed)
        if value is None:
            return None

        # Handle basic types that don't need normalization (no caching needed)
        if isinstance(value, (str, int, float, bool)):
            return value

        # Use caching for complex types only
        if not self._is_caching_enabled() or not self._cache_manager:
            return self._perform_value_normalization(value)

        # Use cache manager's domain-specific method
        try:
            value_type = type(value).__name__
            attr_key = f"val_norm:{hash(str(value))}:{value_type}"
            return self._cache_manager.get_cached_attributes(
                attr_key=attr_key,
                normalizer_func=lambda: self._perform_value_normalization(value),
            )
        except Exception:
            # If hashing fails, skip caching and normalize directly
            return self._perform_value_normalization(value)

    def _perform_value_normalization(self, value: Any) -> Any:
        """Perform the actual value normalization logic."""
        # Handle enum values dynamically
        if hasattr(value, "value"):
            return value.value

        # Convert complex types to strings
        try:
            return str(value)
        except Exception as e:
            # Graceful degradation following Agent OS standards - never crash host app
            safe_log(
                self,
                "debug",
                "Failed to serialize attribute value",
                honeyhive_data={"error_type": type(e).__name__},
            )
            return "<unserializable>"

    # Cache getter methods removed - using CacheManager domain methods directly

    def _is_caching_enabled(self) -> bool:
        """Check if caching is enabled via configuration.

        Returns:
            True if caching is enabled and cache manager is available, False otherwise
        """
        # Check if cache manager exists
        if not hasattr(self, "_cache_manager") or not self._cache_manager:
            return False

        # Direct config resolution (never use caching for this check)
        if hasattr(self, "config") and self.config:
            return bool(self.config.get("cache_enabled", True))

        # No merged config available, default to True
        return True

    def _detect_resources_with_cache(self) -> Dict[str, Any]:
        """Detect system resources with dynamic caching for performance.

        This method performs expensive system resource detection and caches
        the results for improved performance on subsequent calls.

        Returns:
            Dictionary containing detected resource information
        """
        if not self._is_caching_enabled() or not self._cache_manager:
            return self._perform_resource_detection()

        # Use cache manager's domain-specific method
        resource_key = self._build_resource_cache_key()
        return self._cache_manager.get_cached_resources(
            resource_key=resource_key, detector_func=self._perform_resource_detection
        )

    def _build_resource_cache_key(self) -> str:
        """Build cache key for resource detection based on system characteristics.

        Returns:
            Cache key string based on stable system identifiers
        """

        # Dynamic key based on system characteristics that affect resources
        key_components = [
            platform.system(),  # OS type (Linux, Darwin, Windows)
            platform.machine(),  # Architecture (x86_64, arm64)
            str(os.getpid()),  # Process ID (changes per process)
            os.getenv("HOSTNAME", "unknown"),  # Hostname for containerized environments
            os.getenv("KUBERNETES_SERVICE_HOST", ""),  # K8s detection
            os.getenv("AWS_LAMBDA_FUNCTION_NAME", ""),  # Lambda detection
        ]

        # Create stable hash of key components
        key_string = "|".join(str(c) for c in key_components)
        return f"resources:{hash(key_string)}"

    def _perform_resource_detection(self) -> Dict[str, Any]:
        """Perform resource detection using the infra module.

        Returns:
            Dictionary containing detected resource attributes
        """
        return build_otel_resources(self)

    # Resource detection methods moved to infra module

    # Backwards compatibility methods for context propagation
    def link(self, carrier: Dict[str, Any]) -> str:
        """Link context to carrier for backwards compatibility.

        Args:
            carrier: Dictionary to inject context into

        Returns:
            Token for unlinking (tracer ID for backwards compatibility)
        """
        # Inject context into carrier using context mixin functionality
        # The inject_context method is provided by TracerContextMixin
        try:
            # Convert to Dict[str, str] as required by inject_context
            str_carrier = {k: str(v) for k, v in carrier.items()}
            if hasattr(self, "inject_context"):
                self.inject_context(str_carrier)  # type: ignore[attr-defined]
                # Update original carrier with injected values
                carrier.update(str_carrier)
        except Exception as e:
            safe_log(self, "warning", "Failed to inject context in link: %s", e)

        # Return tracer ID as token for backwards compatibility
        return str(id(self))

    def inject(self, carrier: Dict[str, Any]) -> Dict[str, Any]:
        """Inject context into carrier for backwards compatibility.

        Args:
            carrier: Dictionary to inject context into

        Returns:
            The carrier with injected context
        """
        # Use existing context injection if available
        if hasattr(self, "inject_context"):
            self.inject_context(carrier)

        return carrier

    def unlink(self, _token: str) -> None:
        """Unlink context for backwards compatibility.

        Args:
            _token: Token returned from link() method (ignored for compatibility)
        """
        # This is a no-op for backwards compatibility
        # The original implementation may have done cleanup, but with per-instance
        # architecture, no cleanup is needed
        return None  # No-op for backwards compatibility

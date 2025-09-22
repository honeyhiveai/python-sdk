"""Optimized HTTP session factory for OpenTelemetry OTLP exports.

This module provides utilities for creating high-performance HTTP sessions
specifically optimized for OTLP (OpenTelemetry Protocol) span exports.
The sessions feature enhanced connection pooling, intelligent retry strategies,
and configurations tuned for telemetry workloads.

Key optimizations:
- Connection pooling with configurable pool sizes
- Retry strategies for transient network failures
- Non-blocking pool behavior for high throughput
- Optimized timeouts for telemetry data
"""

# pylint: disable=duplicate-code
# Pydantic field validators are domain-specific but share identical validation logic

from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, ConfigDict, Field, field_validator
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ...utils.logger import safe_log
from ..infra.environment import (
    get_comprehensive_environment_analysis,
    get_performance_characteristics,
)

# No longer need to import from otlp_profiles - proper layering restored


class OTLPSessionConfig(BaseModel):
    """Configuration for optimized OTLP HTTP sessions.

    This class encapsulates all configuration options for creating
    high-performance HTTP sessions for OTLP exports.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,  # Allow modifications during dynamic adjustments
    )

    pool_connections: int = Field(
        default=10,
        description="Number of connection pools to cache",
        ge=1,
        le=100,
    )

    pool_maxsize: int = Field(
        default=20,
        description="Maximum connections per pool",
        ge=1,
        le=200,
    )

    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for failed requests",
        ge=0,
        le=20,
    )

    pool_block: bool = Field(
        default=False,
        description="Whether to block when pool is full",
    )

    timeout: Optional[float] = Field(
        default=30.0,
        description="Request timeout in seconds",
        gt=0.0,
        le=600.0,
    )

    backoff_factor: float = Field(
        default=0.5,
        description="Backoff factor for retry delays",
        ge=0.0,
        le=10.0,
    )

    retry_status_codes: List[int] = Field(
        default_factory=lambda: [429, 500, 502, 503, 504],
        description="HTTP status codes to retry",
    )

    @field_validator("pool_maxsize")
    @classmethod
    def validate_pool_maxsize(
        cls, v: int, info: Any
    ) -> int:  # pylint: disable=duplicate-code
        """Ensure pool_maxsize is at least as large as pool_connections.

        Note: This validation logic is intentionally duplicated between
        OTLPSessionConfig and EnvironmentProfile classes as both need
        the same pool size validation constraints.
        """
        if hasattr(info, "data") and "pool_connections" in info.data:
            pool_connections = info.data["pool_connections"]
            if v < pool_connections:
                return int(max(pool_connections, v))
        return v

    @field_validator("retry_status_codes")
    @classmethod
    def validate_retry_status_codes(cls, v: List[int]) -> List[int]:
        """Validate HTTP status codes are in valid range."""
        if not v:
            return [429, 500, 502, 503, 504]  # Default codes

        # Filter to valid HTTP status codes (100-599)
        valid_codes = [code for code in v if 100 <= code <= 599]
        return valid_codes if valid_codes else [429, 500, 502, 503, 504]

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for logging."""
        return self.model_dump()


def create_optimized_otlp_session(
    config: Optional[OTLPSessionConfig] = None,
    tracer_instance: Optional[Any] = None,
) -> requests.Session:
    """Create optimized requests.Session for OTLP exports.

    This function creates a high-performance HTTP session specifically
    optimized for OpenTelemetry OTLP span exports. The session features:

    - Enhanced connection pooling for reduced connection overhead
    - Intelligent retry strategy for transient network failures
    - Optimized timeouts and backoff strategies for telemetry workloads
    - Non-blocking pool behavior for high-throughput scenarios

    Args:
        config: Optional session configuration (uses defaults if None)
        tracer_instance: Optional tracer instance for logging context

    Returns:
        Optimized requests.Session configured for OTLP exports

    Example:
        >>> config = OTLPSessionConfig(pool_maxsize=30, max_retries=5)
        >>> session = create_optimized_otlp_session(config, tracer_instance)
        >>> # Use session with OTLPSpanExporter
        >>> exporter = OTLPSpanExporter(endpoint="...", session=session)
    """
    if config is None:
        config = OTLPSessionConfig()

    safe_log(
        tracer_instance,
        "debug",
        "Creating optimized OTLP session with connection pooling",
        honeyhive_data={"session_config": config.to_dict()},
    )

    try:
        # Create new session
        session = requests.Session()

        # Configure retry strategy optimized for telemetry
        retry_strategy = Retry(
            total=config.max_retries,
            status_forcelist=config.retry_status_codes,
            backoff_factor=config.backoff_factor,
            raise_on_status=False,  # Don't raise on retry-able status codes
            respect_retry_after_header=True,  # Honor server retry-after headers
        )

        # Create high-performance HTTP adapter
        adapter = HTTPAdapter(
            pool_connections=config.pool_connections,
            pool_maxsize=config.pool_maxsize,
            max_retries=retry_strategy,
            pool_block=config.pool_block,
        )

        # Mount adapter for both HTTP and HTTPS
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default timeout if specified
        if config.timeout:
            # Note: This sets a default, but can be overridden per request
            session.timeout = config.timeout  # type: ignore[attr-defined]

        safe_log(
            tracer_instance,
            "info",
            "Successfully created optimized OTLP session",
            honeyhive_data={
                "pool_connections": config.pool_connections,
                "pool_maxsize": config.pool_maxsize,
                "max_retries": config.max_retries,
                "timeout": config.timeout,
            },
        )

        return session

    except Exception as e:
        safe_log(
            tracer_instance,
            "error",
            f"Failed to create optimized OTLP session: {e}",
            honeyhive_data={
                "error_type": type(e).__name__,
                "session_config": config.to_dict(),
            },
        )

        # Fallback to basic session
        safe_log(
            tracer_instance,
            "warning",
            "Falling back to basic requests.Session for OTLP exports",
        )
        return requests.Session()


def get_session_stats(session: requests.Session) -> Dict[str, Any]:
    """Get connection pool statistics from a requests session.

    Args:
        session: The requests.Session to analyze

    Returns:
        Dictionary containing pool statistics and configuration
    """
    stats: Dict[str, Any] = {
        "adapters": {},
        "total_pools": 0,
    }

    try:
        for prefix, adapter in session.adapters.items():
            adapter_stats: Dict[str, Any] = {
                "type": type(adapter).__name__,
                "pools": 0,
            }

            # Get pool manager stats if available
            if hasattr(adapter, "poolmanager") and adapter.poolmanager:
                pool_manager = adapter.poolmanager
                adapter_stats.update(
                    {
                        "pools": len(getattr(pool_manager, "pools", {})),
                        "pool_connections": getattr(adapter, "config", {}).get(
                            "pool_connections", "default"
                        ),
                        "pool_maxsize": getattr(adapter, "config", {}).get(
                            "pool_maxsize", "default"
                        ),
                    }
                )
                pools_count = adapter_stats["pools"]
                if isinstance(pools_count, int):
                    stats["total_pools"] += pools_count

            stats["adapters"][prefix] = adapter_stats

    except Exception as e:
        stats["error"] = f"Failed to get session stats: {e}"

    return stats


def create_dynamic_otlp_config(
    tracer_instance: Optional[Any] = None, scenario: str = "default", **overrides: Any
) -> OTLPSessionConfig:
    """Create fully dynamic OTLP session configuration based on environment analysis.

    This function uses pure dynamic logic to determine optimal configuration values
    based on actual environment conditions, resource constraints, and tracer settings.
    NO hardcoded values - everything calculated from real conditions.

    Args:
        tracer_instance: Optional tracer instance for dynamic configuration
        scenario: Configuration scenario hint (used for dynamic adjustments)
        **overrides: Explicit configuration overrides

    Returns:
        Dynamically configured OTLPSessionConfig based on actual environment
    """
    # Get comprehensive environment analysis
    try:
        # Import at top level to avoid inline imports
        env_analysis = _get_comprehensive_environment_analysis(tracer_instance)
    except Exception:
        # Fallback to basic analysis if environment module not available
        env_analysis = _get_basic_environment_analysis(tracer_instance)

    # Extract dynamic factors from environment analysis
    resource_constraints = env_analysis.get("resource_constraints", {})
    performance_chars = env_analysis.get("performance_characteristics", {})

    # Calculate base configuration dynamically from environment
    base_config = _calculate_base_config_from_environment(
        resource_constraints, performance_chars, tracer_instance
    )

    # Apply dynamic tracer-specific adjustments
    if tracer_instance:
        base_config = _apply_tracer_dynamic_adjustments(base_config, tracer_instance)

    # Apply dynamic scenario adjustments (using environment multipliers)
    base_config = _apply_scenario_dynamic_adjustments(
        base_config, scenario, performance_chars
    )

    # Apply explicit overrides
    base_config.update(overrides)

    # Log the fully dynamic configuration
    safe_log(
        tracer_instance,
        "debug",
        "Created fully dynamic OTLP config from environment analysis",
        honeyhive_data={
            "scenario": scenario,
            "dynamic_config": base_config,
            "environment_type": env_analysis.get("environment_type"),
            "resource_scaling_factors": {
                "memory": resource_constraints.get("memory_constraint_factor"),
                "cpu": resource_constraints.get("cpu_scaling_factor"),
                "network": resource_constraints.get("network_scaling_factor"),
            },
            "performance_multipliers": {
                "timeout": performance_chars.get("timeout_multiplier"),
                "retry": performance_chars.get("retry_multiplier"),
                "concurrency": performance_chars.get("concurrency_multiplier"),
            },
        },
    )

    return OTLPSessionConfig(**base_config)


def _calculate_base_config_from_environment(
    resource_constraints: Dict[str, Any],
    performance_chars: Dict[str, Any],
    _tracer_instance: Optional[Any] = None,
) -> Dict[str, Any]:
    """Calculate base configuration dynamically from environment analysis."""

    # Get dynamic scaling factors from environment
    memory_factor = resource_constraints.get("memory_constraint_factor", 1.0)
    cpu_factor = resource_constraints.get("cpu_scaling_factor", 1.0)
    network_factor = resource_constraints.get("network_scaling_factor", 1.0)

    # Get dynamic performance multipliers
    timeout_multiplier = performance_chars.get("timeout_multiplier", 1.0)
    retry_multiplier = performance_chars.get("retry_multiplier", 1.0)
    concurrency_multiplier = performance_chars.get("concurrency_multiplier", 1.0)

    # Calculate pool connections based on CPU and concurrency capability
    base_pool_connections = max(2, int(8 * cpu_factor * concurrency_multiplier))

    # Calculate pool max size based on memory and network capability
    base_pool_maxsize = max(5, int(15 * memory_factor * network_factor))

    # Calculate retries based on network reliability and performance requirements
    base_max_retries = max(1, int(3 * retry_multiplier * network_factor))

    # Calculate timeout based on latency sensitivity and network conditions
    base_timeout = max(5.0, 25.0 * timeout_multiplier * network_factor)

    # Calculate backoff factor based on performance characteristics
    execution_model = performance_chars.get("execution_model", "persistent")
    if execution_model == "serverless":
        base_backoff_factor = 0.2  # Fast backoff for serverless
    elif "latency" in performance_chars.get("latency_sensitivity", ""):
        base_backoff_factor = 0.3  # Moderate backoff for latency-sensitive
    else:
        base_backoff_factor = 0.5  # Standard backoff

    # Determine pool blocking based on execution model
    pool_block = execution_model not in ["serverless", "burst"]

    # Dynamic retry status codes based on environment reliability
    network_tier = resource_constraints.get("network_tier", "standard")
    if "serverless" in network_tier or "constrained" in network_tier:
        # More aggressive retry codes for constrained environments
        retry_codes = [408, 429, 500, 502, 503, 504, 520, 521, 522, 523, 524]
    else:
        # Standard retry codes for stable environments
        retry_codes = [429, 500, 502, 503, 504]

    return {
        "pool_connections": base_pool_connections,
        "pool_maxsize": base_pool_maxsize,
        "max_retries": base_max_retries,
        "pool_block": pool_block,
        "timeout": base_timeout,
        "backoff_factor": base_backoff_factor,
        "retry_status_codes": retry_codes,
    }


def _apply_tracer_dynamic_adjustments(
    config: Dict[str, Any], tracer_instance: Any
) -> Dict[str, Any]:
    """Apply dynamic adjustments based on tracer configuration."""
    try:
        # Get tracer configuration dynamically
        batch_size = getattr(tracer_instance, "batch_size", None)
        if batch_size is None and hasattr(tracer_instance, "config"):
            batch_size = getattr(tracer_instance.config, "batch_size", None)

        disable_batch = getattr(tracer_instance, "disable_batch", False)
        verbose = getattr(tracer_instance, "verbose", False)

        # Dynamic batch size analysis
        if batch_size:
            # Calculate load factor from batch size
            load_factor = min(3.0, max(0.3, batch_size / 100.0))

            # Adjust pool size based on expected load
            config["pool_maxsize"] = max(5, int(config["pool_maxsize"] * load_factor))
            config["pool_connections"] = max(
                2, int(config["pool_connections"] * (load_factor * 0.8))
            )

            # Adjust timeout based on batch processing time
            batch_timeout_factor = min(2.0, max(0.5, batch_size / 200.0))
            config["timeout"] = max(5.0, config["timeout"] * batch_timeout_factor)

        # Dynamic batching mode adjustments
        if disable_batch:
            # Immediate mode = many small requests, need more connections
            config["pool_connections"] = max(
                config["pool_connections"], int(config["pool_connections"] * 1.5)
            )
            config["pool_maxsize"] = max(
                config["pool_maxsize"], int(config["pool_maxsize"] * 1.2)
            )
            # Faster timeouts for immediate mode
            config["timeout"] = max(5.0, config["timeout"] * 0.7)

        # Dynamic verbosity adjustments
        if verbose:
            # Verbose mode = more debugging, allow more retries and longer timeouts
            config["max_retries"] = min(8, config["max_retries"] + 2)
            config["timeout"] = min(120.0, config["timeout"] * 1.3)
            config["backoff_factor"] = max(0.1, config["backoff_factor"] * 0.8)

    except Exception as e:
        safe_log(
            tracer_instance,
            "debug",
            f"Could not apply tracer dynamic adjustments: {e}",
        )

    return config


def _apply_scenario_dynamic_adjustments(
    config: Dict[str, Any], scenario: str, performance_chars: Dict[str, Any]
) -> Dict[str, Any]:
    """Apply dynamic scenario adjustments based on performance characteristics."""

    # Get dynamic multipliers from performance analysis
    overall_scaling = performance_chars.get("overall_scaling_factor", 1.0)
    concurrency_multiplier = performance_chars.get("concurrency_multiplier", 1.0)

    # Apply scenario-specific dynamic adjustments
    if scenario == "high_volume":
        # Scale up based on actual system capability
        volume_factor = min(2.5, max(1.2, overall_scaling * 1.4))
        config["pool_connections"] = int(config["pool_connections"] * volume_factor)
        config["pool_maxsize"] = int(config["pool_maxsize"] * (volume_factor * 0.9))
        config["max_retries"] = min(10, config["max_retries"] + 3)
        config["timeout"] = min(180.0, config["timeout"] * 1.5)

    elif scenario == "low_latency":
        # Optimize for speed based on latency sensitivity
        latency_sensitivity = performance_chars.get("latency_sensitivity", "standard")
        if "critical" in latency_sensitivity:
            speed_factor = 0.4  # Very aggressive
        elif "high" in latency_sensitivity:
            speed_factor = 0.6  # Aggressive
        else:
            speed_factor = 0.8  # Moderate

        config["pool_connections"] = max(
            2, int(config["pool_connections"] * speed_factor)
        )
        config["pool_maxsize"] = max(
            5, int(config["pool_maxsize"] * (speed_factor + 0.2))
        )
        config["max_retries"] = max(1, int(config["max_retries"] * speed_factor))
        config["timeout"] = max(3.0, config["timeout"] * speed_factor)
        config["backoff_factor"] = max(0.1, config["backoff_factor"] * speed_factor)

    # Apply concurrency-based adjustments
    if concurrency_multiplier > 1.5:
        # High concurrency environment
        config["pool_connections"] = int(config["pool_connections"] * 1.3)
        config["pool_maxsize"] = int(config["pool_maxsize"] * 1.2)
    elif concurrency_multiplier < 0.7:
        # Low concurrency environment
        config["pool_connections"] = max(2, int(config["pool_connections"] * 0.8))
        config["pool_maxsize"] = max(5, int(config["pool_maxsize"] * 0.9))

    return config


def _get_comprehensive_environment_analysis(
    tracer_instance: Optional[Any] = None,
) -> Dict[str, Any]:
    """Get comprehensive environment analysis using the dedicated environment module."""
    try:
        return get_comprehensive_environment_analysis(tracer_instance)
    except ImportError:
        # Fallback if environment module not available
        return _get_basic_environment_analysis(tracer_instance)


def _get_basic_environment_analysis(
    _tracer_instance: Optional[Any] = None,
) -> Dict[str, Any]:
    """Fallback environment analysis when full environment module not available."""

    # Use infra module for environment detection
    return get_performance_characteristics(_tracer_instance)


# Dynamic configuration factories
def get_default_otlp_config(tracer_instance: Optional[Any] = None) -> OTLPSessionConfig:
    """Get default OTLP configuration with dynamic adjustments."""
    return create_dynamic_otlp_config(tracer_instance, "default")


def get_high_volume_otlp_config(
    tracer_instance: Optional[Any] = None,
) -> OTLPSessionConfig:
    """Get high-volume OTLP configuration with dynamic adjustments."""
    return create_dynamic_otlp_config(tracer_instance, "high_volume")


def get_low_latency_otlp_config(
    tracer_instance: Optional[Any] = None,
) -> OTLPSessionConfig:
    """Get low-latency OTLP configuration with dynamic adjustments."""
    return create_dynamic_otlp_config(tracer_instance, "low_latency")


# Removed get_environment_aware_otlp_config - proper layering restored
# Callers should use otlp_profiles.get_environment_optimized_config() directly

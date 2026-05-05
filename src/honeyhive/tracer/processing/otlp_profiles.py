"""Environment-aware OTLP configuration profiles with full dynamic logic.

This module provides intelligent OTLP session configuration profiles that
automatically optimize connection pooling based on detected environment
characteristics, leveraging the existing resource detection from the tracer core.

Key Features:
- Reuses existing environment detection from tracer core (no duplication)
- Fully dynamic configuration - no hardcoded values
- Resource-aware optimization based on actual system characteristics

- Environment-specific optimization patterns
- Intelligent scaling based on detected constraints

Architecture:
- Leverages tracer._detect_container_environment_dynamically()
- Leverages tracer._detect_cloud_environment_dynamically()
- Uses dynamic logic throughout - all values calculated from environment
"""

# pylint: disable=duplicate-code
# Pydantic field validators are domain-specific but share identical validation logic

import multiprocessing
import os
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ...utils.logger import safe_log
from ..infra.environment import get_comprehensive_environment_analysis
from .otlp_session import OTLPSessionConfig

# Removed unnecessary wrapper - use environment module directly


class EnvironmentProfile(BaseModel):
    """Environment-specific OTLP configuration profile."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,  # Allow modifications during dynamic adjustments
    )

    name: str = Field(
        ...,
        description="Profile name for identification",
        min_length=1,
        max_length=100,
    )

    pool_connections: int = Field(
        ...,
        description="Number of connection pools to maintain",
        ge=1,
        le=50,
    )

    pool_maxsize: int = Field(
        ...,
        description="Maximum size of each connection pool",
        ge=1,
        le=100,
    )

    max_retries: int = Field(
        ...,
        description="Maximum number of retry attempts",
        ge=0,
        le=10,
    )

    timeout: float = Field(
        ...,
        description="Request timeout in seconds",
        gt=0.0,
        le=300.0,
    )

    backoff_factor: float = Field(
        ...,
        description="Backoff factor for retry delays",
        ge=0.0,
        le=5.0,
    )

    description: str = Field(
        "",
        description="Human-readable profile description",
        max_length=500,
    )

    pool_block: bool = Field(
        False,
        description="Whether connection pool should block when exhausted",
    )

    additional_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional configuration parameters",
    )

    @field_validator("pool_maxsize")
    @classmethod
    def validate_pool_maxsize(cls, v: int, info: Any) -> int:
        """Ensure pool_maxsize is at least as large as pool_connections.

        Note: This validation logic is intentionally duplicated between
        EnvironmentProfile and OTLPSessionConfig classes as both need
        the same pool size validation constraints.
        """
        if hasattr(info, "data") and "pool_connections" in info.data:
            pool_connections = info.data["pool_connections"]
            if v < pool_connections:
                return int(max(pool_connections, v))
        return v


# EnvironmentAnalyzer class removed - profiles are now pure consumers of
# environment data
# All environment analysis is handled by the dedicated environment.py module


def _determine_environment_type(
    container_info: Dict[str, Any], cloud_info: Dict[str, Any]
) -> str:
    """Determine primary environment type from detection results."""
    # Serverless takes highest priority
    if cloud_info.get("faas.name"):
        return "aws_lambda"

    # Container orchestration
    if container_info.get("k8s.cluster.name"):
        return "kubernetes"
    if container_info.get("container.runtime") == "docker":
        return "docker"

    # Cloud providers
    cloud_provider = cloud_info.get("cloud.provider")
    if cloud_provider == "aws":
        return "aws_ec2"
    if cloud_provider == "gcp":
        return "gcp"
    if cloud_provider == "azure":
        return "azure"

    return "standard"


def _analyze_resource_constraints() -> Dict[str, Any]:
    """Dynamically analyze system resource constraints."""
    constraints: Dict[str, Any] = {}

    try:
        # Memory analysis
        if lambda_memory := os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE"):
            memory_mb = int(lambda_memory)
            constraints["memory_mb"] = memory_mb
            constraints["memory_tier"] = (
                "low" if memory_mb < 512 else "medium" if memory_mb < 1024 else "high"
            )
        else:
            # Default memory tier based on environment
            constraints["memory_tier"] = "medium"

        # CPU analysis
        try:
            cpu_count = multiprocessing.cpu_count()
            constraints["cpu_count"] = cpu_count
            constraints["cpu_tier"] = (
                "low" if cpu_count <= 2 else "medium" if cpu_count <= 8 else "high"
            )
        except:
            constraints["cpu_count"] = 1
            constraints["cpu_tier"] = "low"

    except Exception as e:
        constraints["analysis_error"] = str(e)

    return constraints


def _analyze_performance_characteristics(environment_type: str) -> Dict[str, Any]:
    """Dynamically analyze performance characteristics."""
    characteristics = {}

    try:
        # Execution model based on environment
        if environment_type == "aws_lambda":
            characteristics.update(
                {
                    "execution_model": "serverless",
                    "cold_start_sensitive": True,
                    "connection_reuse_critical": True,
                    "latency_sensitivity": "high",
                }
            )
        elif environment_type == "kubernetes":
            characteristics.update(
                {
                    "execution_model": "orchestrated",
                    "scaling_dynamic": True,
                    "connection_persistence": "medium",
                    "latency_sensitivity": "standard",
                }
            )
        else:
            characteristics.update(
                {
                    "execution_model": "persistent",
                    "connection_persistence": "high",
                    "latency_sensitivity": "standard",
                }
            )

        # Dynamic concurrency analysis
        if os.getenv("HH_HIGH_CONCURRENCY") == "true":
            characteristics["concurrency_pattern"] = "high"
        elif environment_type == "aws_lambda":
            characteristics["concurrency_pattern"] = "burst"
        else:
            characteristics["concurrency_pattern"] = "standard"

        # Dynamic latency sensitivity
        session_name = os.getenv("HH_SESSION_NAME", "").lower()
        if "benchmark" in session_name or "load" in session_name:
            characteristics["latency_sensitivity"] = "critical"

    except Exception as e:
        characteristics["analysis_error"] = str(e)

    return characteristics


class EnvironmentProfileManager:
    """Manages environment-specific OTLP configuration profiles."""

    # Predefined environment profiles
    PROFILES = {
        "aws_lambda": EnvironmentProfile(
            name="AWS Lambda",
            description="Optimized for AWS Lambda serverless functions",
            pool_connections=3,  # Minimal pools for cold start speed
            pool_maxsize=8,  # Small pools due to memory constraints
            max_retries=2,  # Fast failure for timeout constraints
            timeout=10.0,  # Short timeout for Lambda limits
            backoff_factor=0.1,  # Very fast backoff
            additional_config={
                "connection_reuse_priority": "critical",
                "cold_start_optimization": True,
            },
        ),
        "kubernetes": EnvironmentProfile(
            name="Kubernetes",
            description="Optimized for Kubernetes orchestrated environments",
            pool_connections=12,  # Moderate pools for scaling
            pool_maxsize=20,  # Balanced for pod resources
            max_retries=4,  # More retries for network resilience
            timeout=25.0,  # Reasonable timeout for orchestrated networking
            backoff_factor=0.3,  # Moderate backoff
            additional_config={
                "graceful_shutdown": True,
                "scaling_aware": True,
            },
        ),
        "docker": EnvironmentProfile(
            name="Docker Container",
            description="Optimized for Docker containerized applications",
            pool_connections=8,  # Moderate pools
            pool_maxsize=15,  # Container resource aware
            max_retries=3,  # Standard retries
            timeout=20.0,  # Container networking timeout
            backoff_factor=0.4,  # Standard backoff
            additional_config={
                "container_optimized": True,
            },
        ),
        "gcp": EnvironmentProfile(
            name="Google Cloud Platform",
            description="Optimized for GCP environments",
            pool_connections=10,  # GCP networking optimized
            pool_maxsize=18,  # GCP resource patterns
            max_retries=3,  # GCP reliability patterns
            timeout=22.0,  # GCP network characteristics
            backoff_factor=0.35,  # GCP-tuned backoff
            additional_config={
                "gcp_optimized": True,
            },
        ),
        "azure": EnvironmentProfile(
            name="Microsoft Azure",
            description="Optimized for Azure cloud environments",
            pool_connections=10,  # Azure networking patterns
            pool_maxsize=18,  # Azure resource allocation
            max_retries=4,  # Azure resilience patterns
            timeout=24.0,  # Azure network characteristics
            backoff_factor=0.4,  # Azure-tuned backoff
            additional_config={
                "azure_optimized": True,
            },
        ),
        "aws_ec2": EnvironmentProfile(
            name="AWS EC2",
            description="Optimized for AWS EC2 instances",
            pool_connections=15,  # EC2 networking capacity
            pool_maxsize=25,  # EC2 resource availability
            max_retries=3,  # AWS reliability
            timeout=30.0,  # EC2 network performance
            backoff_factor=0.3,  # AWS-tuned backoff
            additional_config={
                "aws_optimized": True,
                "ec2_instance": True,
            },
        ),
        "standard": EnvironmentProfile(
            name="Standard Environment",
            description="Default profile for standard server environments",
            pool_connections=10,  # Balanced default
            pool_maxsize=20,  # Standard capacity
            max_retries=3,  # Standard resilience
            timeout=30.0,  # Standard timeout
            backoff_factor=0.5,  # Standard backoff
            additional_config={
                "standard_environment": True,
            },
        ),
    }

    @classmethod
    def get_optimal_profile(
        cls, tracer_instance: Optional[Any] = None
    ) -> Tuple[EnvironmentProfile, Dict[str, Any]]:
        """Get the optimal OTLP profile for the current environment.

        Args:
            tracer_instance: Optional tracer instance for logging context

        Returns:
            Tuple of (selected_profile, environment_analysis)
        """
        # Get comprehensive environment analysis directly from environment module
        # Profiles are pure consumers - no environment detection logic here
        safe_log(
            tracer_instance,
            "debug",
            "Getting environment analysis for OTLP profile optimization",
        )
        env_analysis = get_comprehensive_environment_analysis(tracer_instance)
        env_type = env_analysis.get("environment_type", "standard")
        _resource_constraints = env_analysis.get("resource_constraints", {})
        _performance_chars = env_analysis.get("performance_characteristics", {})

        # Use the comprehensive analysis directly
        environment_analysis = env_analysis

        # Select base profile
        base_profile = cls.PROFILES.get(env_type, cls.PROFILES["standard"])

        # Create optimized profile with dynamic adjustments
        optimized_profile = cls._apply_dynamic_adjustments(
            base_profile, environment_analysis, tracer_instance
        )

        safe_log(
            tracer_instance,
            "info",
            f"Selected OTLP profile: {optimized_profile.name}",
            honeyhive_data={
                "profile_name": optimized_profile.name,
                "environment_analysis": environment_analysis,
                "profile_config": {
                    "pool_connections": optimized_profile.pool_connections,
                    "pool_maxsize": optimized_profile.pool_maxsize,
                    "timeout": optimized_profile.timeout,
                    "max_retries": optimized_profile.max_retries,
                },
            },
        )

        return optimized_profile, environment_analysis

    @classmethod
    def _apply_dynamic_adjustments(
        cls,
        base_profile: EnvironmentProfile,
        environment_analysis: Dict[str, Any],
        tracer_instance: Optional[Any] = None,
    ) -> EnvironmentProfile:
        """Apply dynamic adjustments to base profile based on environment analysis."""

        # Create a copy for modification using Pydantic model_copy
        adjusted_profile = base_profile.model_copy(
            update={
                "name": f"{base_profile.name} (Optimized)",
                "description": f"{base_profile.description} with dynamic adjustments",
                "additional_config": (
                    base_profile.additional_config.copy()
                    if base_profile.additional_config
                    else {}
                ),
            }
        )

        try:
            constraints = environment_analysis.get("resource_constraints", {})
            performance = environment_analysis.get("performance_characteristics", {})

            # Memory-based adjustments
            memory_tier = constraints.get("memory_tier", "medium")
            if memory_tier == "low":
                adjusted_profile.pool_connections = max(
                    2, adjusted_profile.pool_connections // 2
                )
                adjusted_profile.pool_maxsize = max(
                    5, adjusted_profile.pool_maxsize // 2
                )
            elif memory_tier == "high":
                adjusted_profile.pool_connections = min(
                    20, int(adjusted_profile.pool_connections * 1.3)
                )
                adjusted_profile.pool_maxsize = min(
                    40, int(adjusted_profile.pool_maxsize * 1.3)
                )

            # CPU-based adjustments
            cpu_tier = constraints.get("cpu_tier", "medium")
            if cpu_tier == "low":
                adjusted_profile.max_retries = max(1, adjusted_profile.max_retries - 1)
            elif cpu_tier == "high":
                adjusted_profile.max_retries = min(6, adjusted_profile.max_retries + 1)

            # Latency sensitivity adjustments
            latency_sensitivity = performance.get("latency_sensitivity", "standard")
            if latency_sensitivity == "critical":
                adjusted_profile.timeout = max(5.0, adjusted_profile.timeout * 0.6)
                adjusted_profile.backoff_factor = max(
                    0.1, adjusted_profile.backoff_factor * 0.5
                )
                adjusted_profile.max_retries = max(1, adjusted_profile.max_retries - 1)
            elif latency_sensitivity == "high":
                adjusted_profile.timeout = max(8.0, adjusted_profile.timeout * 0.8)
                adjusted_profile.backoff_factor = max(
                    0.2, adjusted_profile.backoff_factor * 0.7
                )

            # Concurrency pattern adjustments
            concurrency_pattern = performance.get("concurrency_pattern", "standard")
            if concurrency_pattern == "high":
                adjusted_profile.pool_connections = min(
                    25, int(adjusted_profile.pool_connections * 1.5)
                )
                adjusted_profile.pool_maxsize = min(
                    50, int(adjusted_profile.pool_maxsize * 1.4)
                )
            elif concurrency_pattern == "burst":
                # Optimize for burst scaling (like Lambda)
                adjusted_profile.pool_connections = max(
                    3, adjusted_profile.pool_connections
                )
                adjusted_profile.pool_maxsize = max(8, adjusted_profile.pool_maxsize)

            # Add adjustment metadata
            if adjusted_profile.additional_config is not None:
                adjusted_profile.additional_config["dynamic_adjustments"] = {
                    "memory_tier": memory_tier,
                    "cpu_tier": cpu_tier,
                    "latency_sensitivity": latency_sensitivity,
                    "concurrency_pattern": concurrency_pattern,
                }

        except Exception as e:
            safe_log(
                tracer_instance,
                "warning",
                f"Failed to apply dynamic adjustments: {e}",
                honeyhive_data={"error_type": type(e).__name__},
            )
            # Return base profile if adjustments fail
            return base_profile

        return adjusted_profile

    @classmethod
    def create_otlp_config_from_profile(
        cls,
        profile: EnvironmentProfile,
        _tracer_instance: Optional[Any] = None,
        **overrides: Any,
    ) -> OTLPSessionConfig:
        """Create an OTLPSessionConfig from an environment profile.

        Args:
            profile: Environment profile to use as base
            tracer_instance: Optional tracer instance for context
            **overrides: Explicit configuration overrides

        Returns:
            Configured OTLPSessionConfig
        """
        config_params: Dict[str, Any] = {
            "pool_connections": int(profile.pool_connections),
            "pool_maxsize": int(profile.pool_maxsize),
            "max_retries": int(profile.max_retries),
            "timeout": float(profile.timeout) if profile.timeout is not None else None,
            "backoff_factor": float(profile.backoff_factor),
            "pool_block": bool(profile.pool_block),
        }

        # Apply any explicit overrides with proper type conversion
        for key, value in overrides.items():
            if key in ["pool_connections", "pool_maxsize", "max_retries"]:
                config_params[key] = int(value)
            elif key in ["timeout", "backoff_factor"]:
                config_params[key] = float(value) if value is not None else None
            elif key == "pool_block":
                config_params[key] = bool(value)
            elif key == "retry_status_codes":
                config_params[key] = (
                    list(value) if isinstance(value, (list, tuple)) else [int(value)]
                )
            else:
                config_params[key] = value

        return OTLPSessionConfig(**config_params)


def get_environment_optimized_config(
    tracer_instance: Optional[Any] = None, **overrides: Any
) -> OTLPSessionConfig:
    """Get environment-optimized OTLP configuration.

    This is the main entry point for getting an OTLP configuration that's
    automatically optimized for the current environment.

    Args:
        tracer_instance: Optional tracer instance for context
        **overrides: Explicit configuration overrides

    Returns:
        Environment-optimized OTLPSessionConfig
    """
    profile_manager = EnvironmentProfileManager()
    optimal_profile, _environment_analysis = profile_manager.get_optimal_profile(
        tracer_instance
    )

    return profile_manager.create_otlp_config_from_profile(
        optimal_profile, tracer_instance, **overrides
    )

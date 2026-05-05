"""Environment and resource detection utilities.

This module provides comprehensive environment detection capabilities for
optimizing tracer behavior based on deployment context. It detects:

- Cloud providers (AWS, GCP, Azure)
- Container environments (Docker, Kubernetes)
- Serverless platforms (AWS Lambda, etc.)
- System resources (CPU, memory)
- Network characteristics

The detection logic is designed to be:
- Fast and lightweight
- Gracefully degrading on errors
- Cache-friendly for repeated calls
- OpenTelemetry resource convention compliant
"""

import multiprocessing
import os
import platform
from typing import Any, Dict, Optional

from ...utils.logger import safe_log


class EnvironmentDetector:
    """Comprehensive environment and resource detection."""

    def __init__(self, tracer_instance: Optional[Any] = None):
        """Initialize environment detector.

        Args:
            tracer_instance: Optional tracer instance for logging context
        """
        self.tracer_instance = tracer_instance
        self._cache: Dict[str, Any] = {}

    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """Get comprehensive environment analysis with caching.

        Returns:
            Complete environment analysis including all detection results
        """
        if "comprehensive_analysis" in self._cache:
            return dict(self._cache["comprehensive_analysis"])

        analysis = {
            "environment_type": self.detect_primary_environment_type(),
            "container_info": self.detect_container_environment(),
            "cloud_info": self.detect_cloud_environment(),
            "resource_constraints": self.detect_resource_constraints(),
            "performance_characteristics": self.detect_performance_characteristics(),
            "system_info": self.detect_system_info(),
        }

        # Cache the result
        self._cache["comprehensive_analysis"] = analysis

        safe_log(
            self.tracer_instance,
            "debug",
            f"Environment analysis complete: {analysis['environment_type']}",
            honeyhive_data={
                "environment_type": analysis["environment_type"],
                "has_container_info": bool(analysis["container_info"]),
                "has_cloud_info": bool(analysis["cloud_info"]),
                "resource_constraints": analysis["resource_constraints"],
            },
        )

        return analysis

    def detect_primary_environment_type(self) -> str:
        """Detect the primary environment type.

        Returns:
            Primary environment type string
        """
        if "environment_type" in self._cache:
            return str(self._cache["environment_type"])

        # Priority order for environment detection
        env_type = "standard"  # Default

        try:
            # Serverless (highest priority)
            if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
                env_type = "aws_lambda"
            # Container orchestration
            elif os.getenv("KUBERNETES_SERVICE_HOST"):
                env_type = "kubernetes"
            elif os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER"):
                env_type = "docker"
            # Cloud providers (non-serverless)
            elif os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT"):
                env_type = "gcp"
            elif os.getenv("AZURE_RESOURCE_GROUP") or os.getenv(
                "WEBSITE_RESOURCE_GROUP"
            ):
                env_type = "azure"
            elif os.getenv("AWS_REGION"):
                env_type = "aws_ec2"

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "debug",
                f"Error detecting environment type: {e}",
            )

        self._cache["environment_type"] = env_type
        return env_type

    def detect_container_environment(self) -> Dict[str, Any]:
        """Detect container environment characteristics.

        Returns:
            Dictionary with container environment details
        """
        if "container_info" in self._cache:
            return dict(self._cache["container_info"])

        container_info = {}

        try:
            # Docker detection
            if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER"):
                container_info["container.runtime"] = "docker"
                if container_id := os.getenv("HOSTNAME"):
                    container_info["container.id"] = container_id

            # Kubernetes detection
            if os.getenv("KUBERNETES_SERVICE_HOST"):
                container_info.update(
                    {
                        "k8s.cluster.name": os.getenv("K8S_CLUSTER_NAME", "unknown"),
                        "k8s.namespace.name": os.getenv("K8S_NAMESPACE", "default"),
                        "k8s.pod.name": os.getenv(
                            "K8S_POD_NAME", os.getenv("HOSTNAME", "unknown")
                        ),
                        "k8s.deployment.name": os.getenv(
                            "K8S_DEPLOYMENT_NAME", "unknown"
                        ),
                    }
                )

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "debug",
                f"Error detecting container environment: {e}",
            )

        self._cache["container_info"] = container_info
        return container_info

    def detect_cloud_environment(self) -> Dict[str, Any]:
        """Detect cloud provider and environment.

        Returns:
            Dictionary with cloud environment details
        """
        if "cloud_info" in self._cache:
            return dict(self._cache["cloud_info"])

        cloud_info = {}

        try:
            # AWS detection
            if os.getenv("AWS_REGION") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
                cloud_info["cloud.provider"] = "aws"
                cloud_info["cloud.region"] = os.getenv("AWS_REGION", "unknown")

                # Lambda-specific detection
                if lambda_name := os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
                    cloud_info.update(
                        {
                            "faas.name": lambda_name,
                            "faas.version": os.getenv(
                                "AWS_LAMBDA_FUNCTION_VERSION", "unknown"
                            ),
                            "faas.runtime": f"python{platform.python_version()}",
                            "faas.memory_size": os.getenv(
                                "AWS_LAMBDA_FUNCTION_MEMORY_SIZE"
                            )
                            or "unknown",
                            "faas.timeout": (
                                os.getenv("AWS_LAMBDA_FUNCTION_TIMEOUT") or "unknown"
                            ),
                        }
                    )

            # GCP detection
            elif os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT"):
                cloud_info.update(
                    {
                        "cloud.provider": "gcp",
                        "cloud.region": os.getenv("GOOGLE_CLOUD_REGION", "unknown"),
                        "gcp.project.id": os.getenv(
                            "GOOGLE_CLOUD_PROJECT", os.getenv("GCP_PROJECT", "unknown")
                        ),
                    }
                )

            # Azure detection
            elif os.getenv("AZURE_RESOURCE_GROUP") or os.getenv(
                "WEBSITE_RESOURCE_GROUP"
            ):
                cloud_info.update(
                    {
                        "cloud.provider": "azure",
                        "cloud.region": os.getenv("AZURE_REGION", "unknown"),
                        "azure.resource_group": os.getenv(
                            "AZURE_RESOURCE_GROUP",
                            os.getenv("WEBSITE_RESOURCE_GROUP", "unknown"),
                        ),
                    }
                )

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "debug",
                f"Error detecting cloud environment: {e}",
            )

        self._cache["cloud_info"] = cloud_info
        return cloud_info

    def detect_resource_constraints(self) -> Dict[str, Any]:
        """Detect system resource constraints using dynamic analysis.

        Returns:
            Dictionary with resource constraint information
        """
        if "resource_constraints" in self._cache:
            return dict(self._cache["resource_constraints"])

        constraints = {}

        try:
            # Dynamic memory analysis
            constraints.update(self._analyze_memory_constraints_dynamically())

            # Dynamic CPU analysis
            constraints.update(self._analyze_cpu_constraints_dynamically())

            # Dynamic network analysis
            constraints.update(self._analyze_network_constraints_dynamically())

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "debug",
                f"Error detecting resource constraints: {e}",
            )
            # Provide safe defaults using dynamic fallback
            constraints = self._get_fallback_resource_constraints()

        self._cache["resource_constraints"] = constraints
        return constraints

    def _analyze_memory_constraints_dynamically(self) -> Dict[str, Any]:
        """Dynamically analyze memory constraints based on environment signals."""
        memory_info = {}

        # Lambda memory detection
        if lambda_memory := os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE"):
            memory_mb = int(lambda_memory)
            memory_info.update(
                {
                    "memory_mb": memory_mb,
                    "memory_tier": self._calculate_memory_tier_dynamically(memory_mb),
                    "memory_source": "lambda_config",
                    "memory_constraint_factor": (
                        self._calculate_memory_constraint_factor(memory_mb)
                    ),
                }
            )
        # Container memory limits
        elif cgroup_memory := self._detect_container_memory_limit():
            memory_info.update(
                {
                    "memory_mb": cgroup_memory,
                    "memory_tier": self._calculate_memory_tier_dynamically(
                        cgroup_memory
                    ),
                    "memory_source": "container_cgroup",
                    "memory_constraint_factor": (
                        self._calculate_memory_constraint_factor(cgroup_memory)
                    ),
                }
            )
        else:
            # Estimate based on environment type
            env_type = self.detect_primary_environment_type()
            estimated_memory = self._estimate_memory_by_environment(env_type)
            memory_info.update(
                {
                    "memory_tier": self._calculate_memory_tier_dynamically(
                        estimated_memory
                    ),
                    "memory_source": "environment_estimated",
                    "memory_constraint_factor": (
                        self._calculate_memory_constraint_factor(estimated_memory)
                    ),
                }
            )

        return memory_info

    def _analyze_cpu_constraints_dynamically(self) -> Dict[str, Any]:
        """Dynamically analyze CPU constraints based on system characteristics."""
        cpu_info = {}

        try:
            cpu_count = multiprocessing.cpu_count()
            cpu_info.update(
                {
                    "cpu_count": cpu_count,
                    "cpu_tier": self._calculate_cpu_tier_dynamically(cpu_count),
                    "cpu_source": "detected",
                    "cpu_scaling_factor": self._calculate_cpu_scaling_factor(cpu_count),
                }
            )
        except Exception:
            # Fallback based on environment
            env_type = self.detect_primary_environment_type()
            estimated_cpus = self._estimate_cpu_by_environment(env_type)
            cpu_info.update(
                {
                    "cpu_count": estimated_cpus,
                    "cpu_tier": self._calculate_cpu_tier_dynamically(estimated_cpus),
                    "cpu_source": "environment_fallback",
                    "cpu_scaling_factor": self._calculate_cpu_scaling_factor(
                        estimated_cpus
                    ),
                }
            )

        return cpu_info

    def _analyze_network_constraints_dynamically(self) -> Dict[str, Any]:
        """Dynamically analyze network constraints based on environment."""
        network_info = {}

        env_type = self.detect_primary_environment_type()
        cloud_info = self.detect_cloud_environment()
        container_info = self.detect_container_environment()

        # Dynamic network tier calculation
        network_tier = self._calculate_network_tier_dynamically(
            env_type, cloud_info, container_info
        )
        network_scaling = self._calculate_network_scaling_factor(network_tier)

        network_info.update(
            {
                "network_tier": network_tier,
                "network_scaling_factor": network_scaling,
                "connection_limit_factor": self._calculate_connection_limit_factor(
                    env_type
                ),
            }
        )

        return network_info

    def _calculate_memory_tier_dynamically(self, memory_mb: int) -> str:
        """Calculate memory tier using dynamic thresholds based on current standards."""
        # Dynamic thresholds based on modern application requirements
        low_threshold = 256  # Minimal for basic operations
        medium_threshold = 1024  # Standard for most applications
        high_threshold = 2048  # High-performance applications

        if memory_mb < low_threshold:
            return "minimal"
        if memory_mb < medium_threshold:
            return "low"
        if memory_mb < high_threshold:
            return "medium"
        return "high"

    def _calculate_cpu_tier_dynamically(self, cpu_count: int) -> str:
        """Calculate CPU tier using dynamic analysis of processing capacity."""
        # Dynamic CPU tier calculation based on modern multi-core standards
        if cpu_count <= 1:
            return "minimal"
        if cpu_count <= 2:
            return "low"
        if cpu_count <= 4:
            return "medium"
        if cpu_count <= 8:
            return "high"
        return "very_high"

    def _calculate_network_tier_dynamically(
        self, _env_type: str, cloud_info: Dict, container_info: Dict
    ) -> str:
        """Calculate network tier based on environment characteristics."""
        # Serverless environments have the most constraints
        if cloud_info.get("faas.name"):
            return "serverless_constrained"

        # Container orchestration has managed networking
        if container_info.get("k8s.cluster.name"):
            return "orchestrated_managed"
        if container_info.get("container.runtime"):
            return "containerized_isolated"

        # Cloud providers have different network characteristics
        cloud_provider = cloud_info.get("cloud.provider")
        if cloud_provider:
            return f"cloud_{cloud_provider}_optimized"

        return "standard_networking"

    def _calculate_memory_constraint_factor(self, memory_mb: int) -> float:
        """Calculate memory constraint factor for dynamic scaling."""
        # Lower memory = higher constraint factor (more conservative)
        if memory_mb < 256:
            return 0.3  # Very conservative
        if memory_mb < 512:
            return 0.5  # Conservative
        if memory_mb < 1024:
            return 0.7  # Moderate
        if memory_mb < 2048:
            return 1.0  # Standard
        return 1.3  # Aggressive

    def _calculate_cpu_scaling_factor(self, cpu_count: int) -> float:
        """Calculate CPU scaling factor for dynamic optimization."""
        # More CPUs = higher scaling factor
        return min(2.0, max(0.5, cpu_count / 4.0))

    def _calculate_network_scaling_factor(self, network_tier: str) -> float:
        """Calculate network scaling factor based on tier."""
        scaling_map = {
            "serverless_constrained": 0.3,
            "containerized_isolated": 0.6,
            "orchestrated_managed": 0.8,
            "cloud_aws_optimized": 1.2,
            "cloud_gcp_optimized": 1.1,
            "cloud_azure_optimized": 1.0,
            "standard_networking": 1.0,
        }
        return scaling_map.get(network_tier, 1.0)

    def _calculate_connection_limit_factor(self, env_type: str) -> float:
        """Calculate connection limit factor based on environment."""
        # Different environments have different connection limits
        limit_factors = {
            "aws_lambda": 0.2,  # Very limited
            "docker": 0.6,  # Container limited
            "kubernetes": 0.8,  # Orchestration managed
            "gcp": 1.0,  # Standard cloud
            "azure": 1.0,  # Standard cloud
            "aws_ec2": 1.2,  # AWS networking optimized
        }
        return limit_factors.get(env_type, 1.0)

    def _detect_container_memory_limit(self) -> Optional[int]:
        """Detect container memory limit from cgroups."""
        try:
            # Try to read cgroup memory limit
            cgroup_paths = [
                "/sys/fs/cgroup/memory/memory.limit_in_bytes",
                "/sys/fs/cgroup/memory.max",
            ]

            for path in cgroup_paths:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        limit_bytes = int(f.read().strip())
                        # Convert to MB and check if it's a real limit (not max value)
                        if limit_bytes < (1 << 62):  # Not the cgroup max value
                            return limit_bytes // (1024 * 1024)
        except Exception:
            pass

        return None

    def _estimate_memory_by_environment(self, env_type: str) -> int:
        """Estimate memory based on environment type characteristics."""
        # Dynamic estimation based on typical environment characteristics
        estimates = {
            "aws_lambda": 512,  # Lambda default
            "docker": 1024,  # Typical container
            "kubernetes": 2048,  # K8s pod default
            "gcp": 1024,  # GCP instance
            "azure": 1024,  # Azure instance
            "aws_ec2": 2048,  # EC2 instance
        }
        return estimates.get(env_type, 1024)  # Default estimate

    def _estimate_cpu_by_environment(self, env_type: str) -> int:
        """Estimate CPU count based on environment type."""
        estimates = {
            "aws_lambda": 1,  # Lambda vCPU
            "docker": 2,  # Typical container
            "kubernetes": 2,  # K8s pod default
            "gcp": 2,  # GCP instance
            "azure": 2,  # Azure instance
            "aws_ec2": 4,  # EC2 instance
        }
        return estimates.get(env_type, 2)  # Default estimate

    def _get_fallback_resource_constraints(self) -> Dict[str, Any]:
        """Get fallback resource constraints using dynamic defaults."""
        env_type = self.detect_primary_environment_type()

        return {
            "memory_tier": "medium",
            "cpu_tier": "medium",
            "network_tier": f"{env_type}_fallback",
            "memory_constraint_factor": 0.7,
            "cpu_scaling_factor": 1.0,
            "network_scaling_factor": 1.0,
            "connection_limit_factor": 1.0,
            "fallback_reason": "constraint_detection_failed",
        }

    def detect_performance_characteristics(self) -> Dict[str, Any]:
        """Detect performance characteristics using dynamic analysis.

        Returns:
            Dictionary with performance characteristics
        """
        if "performance_characteristics" in self._cache:
            return dict(self._cache["performance_characteristics"])

        characteristics = {}

        try:
            # Dynamic execution model analysis
            characteristics.update(self._analyze_execution_model_dynamically())

            # Dynamic concurrency pattern analysis
            characteristics.update(self._analyze_concurrency_patterns_dynamically())

            # Dynamic latency sensitivity analysis
            characteristics.update(self._analyze_latency_sensitivity_dynamically())

            # Dynamic scaling characteristics
            characteristics.update(self._analyze_scaling_characteristics_dynamically())

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "debug",
                f"Error detecting performance characteristics: {e}",
            )
            # Provide safe defaults using dynamic fallback
            characteristics = self._get_fallback_performance_characteristics()

        self._cache["performance_characteristics"] = characteristics
        return characteristics

    def _analyze_execution_model_dynamically(self) -> Dict[str, Any]:
        """Dynamically analyze execution model based on environment signals."""
        _env_type = self.detect_primary_environment_type()
        cloud_info = self.detect_cloud_environment()
        container_info = self.detect_container_environment()

        execution_info = {}

        # Serverless execution model
        if cloud_info.get("faas.name"):
            execution_info.update(
                {
                    "execution_model": "serverless",
                    "cold_start_sensitive": True,
                    "connection_reuse_critical": True,
                    "execution_time_limited": True,
                    "memory_optimization_critical": True,
                }
            )
        # Container orchestration model
        elif container_info.get("k8s.cluster.name"):
            execution_info.update(
                {
                    "execution_model": "orchestrated",
                    "scaling_dynamic": True,
                    "connection_persistence": "managed",
                    "resource_allocation_dynamic": True,
                    "graceful_shutdown_required": True,
                }
            )
        # Containerized model
        elif container_info.get("container.runtime"):
            execution_info.update(
                {
                    "execution_model": "containerized",
                    "resource_constrained": True,
                    "connection_persistence": "isolated",
                    "resource_allocation_fixed": True,
                    "isolation_boundaries": True,
                }
            )
        # Persistent/traditional model
        else:
            execution_info.update(
                {
                    "execution_model": "persistent",
                    "connection_persistence": "long_lived",
                    "resource_allocation_stable": True,
                    "scaling_manual": True,
                    "full_system_access": True,
                }
            )

        return execution_info

    def _analyze_concurrency_patterns_dynamically(self) -> Dict[str, Any]:
        """Dynamically analyze concurrency patterns from environment signals."""
        concurrency_info = {}

        # Explicit high concurrency signal
        if os.getenv("HH_HIGH_CONCURRENCY") == "true":
            concurrency_info.update(
                {
                    "concurrency_pattern": "high_explicit",
                    "concurrency_multiplier": 2.0,
                    "connection_pool_scaling": "aggressive",
                }
            )
        # Lambda burst concurrency
        elif self.detect_primary_environment_type() == "aws_lambda":
            concurrency_info.update(
                {
                    "concurrency_pattern": "burst_serverless",
                    "concurrency_multiplier": 0.5,  # Conservative for cold starts
                    "connection_pool_scaling": "minimal",
                }
            )
        # Kubernetes dynamic scaling
        elif self.detect_container_environment().get("k8s.cluster.name"):
            concurrency_info.update(
                {
                    "concurrency_pattern": "orchestrated_scaling",
                    "concurrency_multiplier": 1.2,
                    "connection_pool_scaling": "managed",
                }
            )
        # Standard concurrency
        else:
            concurrency_info.update(
                {
                    "concurrency_pattern": "standard_persistent",
                    "concurrency_multiplier": 1.0,
                    "connection_pool_scaling": "balanced",
                }
            )

        return concurrency_info

    def _analyze_latency_sensitivity_dynamically(self) -> Dict[str, Any]:
        """Dynamically analyze latency sensitivity from environment signals."""
        latency_info = {}

        # Check session name for performance indicators
        session_name = os.getenv("HH_SESSION_NAME", "").lower()
        performance_keywords = [
            "benchmark",
            "load",
            "perf",
            "test",
            "stress",
            "latency",
        ]

        if any(keyword in session_name for keyword in performance_keywords):
            latency_info.update(
                {
                    "latency_sensitivity": "critical_performance_testing",
                    "timeout_multiplier": 0.4,  # Very aggressive timeouts
                    "retry_multiplier": 0.5,  # Fewer retries for speed
                }
            )
        # Lambda has inherent latency sensitivity due to timeout constraints
        elif self.detect_primary_environment_type() == "aws_lambda":
            latency_info.update(
                {
                    "latency_sensitivity": "high_serverless_constraints",
                    "timeout_multiplier": 0.6,  # Aggressive timeouts
                    "retry_multiplier": 0.7,  # Fewer retries
                }
            )
        # Production environment indicators
        elif any(env_var in os.environ for env_var in ["PROD", "PRODUCTION", "LIVE"]):
            latency_info.update(
                {
                    "latency_sensitivity": "high_production",
                    "timeout_multiplier": 0.8,  # Moderate timeouts
                    "retry_multiplier": 1.2,  # More retries for reliability
                }
            )
        # Development/testing environment
        elif any(
            env_var in os.environ
            for env_var in ["DEV", "DEVELOPMENT", "TEST", "STAGING"]
        ):
            latency_info.update(
                {
                    "latency_sensitivity": "low_development",
                    "timeout_multiplier": 1.5,  # Relaxed timeouts
                    "retry_multiplier": 1.0,  # Standard retries
                }
            )
        # Standard sensitivity
        else:
            latency_info.update(
                {
                    "latency_sensitivity": "standard_balanced",
                    "timeout_multiplier": 1.0,  # Standard timeouts
                    "retry_multiplier": 1.0,  # Standard retries
                }
            )

        return latency_info

    def _analyze_scaling_characteristics_dynamically(self) -> Dict[str, Any]:
        """Dynamically analyze scaling characteristics from environment."""
        scaling_info = {}

        _env_type = self.detect_primary_environment_type()
        resource_constraints = self.detect_resource_constraints()

        # Calculate scaling factors based on actual resources
        memory_factor = resource_constraints.get("memory_constraint_factor", 1.0)
        cpu_factor = resource_constraints.get("cpu_scaling_factor", 1.0)
        network_factor = resource_constraints.get("network_scaling_factor", 1.0)

        # Overall scaling capability
        overall_scaling = (memory_factor + cpu_factor + network_factor) / 3.0

        if overall_scaling < 0.5:
            scaling_pattern = "constrained_minimal"
        elif overall_scaling < 0.8:
            scaling_pattern = "conservative_scaling"
        elif overall_scaling > 1.3:
            scaling_pattern = "aggressive_scaling"
        else:
            scaling_pattern = "balanced_scaling"

        scaling_info.update(
            {
                "scaling_pattern": scaling_pattern,
                "overall_scaling_factor": overall_scaling,
                "memory_scaling_factor": memory_factor,
                "cpu_scaling_factor": cpu_factor,
                "network_scaling_factor": network_factor,
            }
        )

        return scaling_info

    def _get_fallback_performance_characteristics(self) -> Dict[str, Any]:
        """Get fallback performance characteristics using dynamic defaults."""
        env_type = self.detect_primary_environment_type()

        return {
            "execution_model": "persistent",
            "latency_sensitivity": "standard_fallback",
            "concurrency_pattern": f"{env_type}_fallback",
            "scaling_pattern": "conservative_fallback",
            "timeout_multiplier": 1.0,
            "retry_multiplier": 1.0,
            "concurrency_multiplier": 1.0,
            "overall_scaling_factor": 1.0,
            "fallback_reason": "performance_detection_failed",
        }

    def detect_system_info(self) -> Dict[str, Any]:
        """Detect basic system information.

        Returns:
            Dictionary with system information
        """
        if "system_info" in self._cache:
            return dict(self._cache["system_info"])

        system_info = {}

        try:
            system_info.update(
                {
                    "os.type": platform.system(),
                    "os.description": platform.platform(),
                    "process.runtime.name": "python",
                    "process.runtime.version": platform.python_version(),
                    "process.pid": os.getpid(),
                    "host.arch": platform.machine(),
                }
            )

            # Add hostname if available
            if hostname := os.getenv("HOSTNAME"):
                system_info["host.name"] = hostname

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "debug",
                f"Error detecting system info: {e}",
            )

        self._cache["system_info"] = system_info
        return system_info

    def clear_cache(self) -> None:
        """Clear the detection cache to force re-detection."""
        self._cache.clear()


# Convenience functions for common use cases
def get_environment_type(tracer_instance: Optional[Any] = None) -> str:
    """Get the primary environment type.

    Args:
        tracer_instance: Optional tracer instance for logging context

    Returns:
        Primary environment type string
    """
    detector = EnvironmentDetector(tracer_instance)
    return detector.detect_primary_environment_type()


def get_resource_constraints(tracer_instance: Optional[Any] = None) -> Dict[str, Any]:
    """Get system resource constraints.

    Args:
        tracer_instance: Optional tracer instance for logging context

    Returns:
        Dictionary with resource constraints
    """
    detector = EnvironmentDetector(tracer_instance)
    return detector.detect_resource_constraints()


def get_performance_characteristics(
    tracer_instance: Optional[Any] = None,
) -> Dict[str, Any]:
    """Get performance characteristics.

    Args:
        tracer_instance: Optional tracer instance for logging context

    Returns:
        Dictionary with performance characteristics
    """
    detector = EnvironmentDetector(tracer_instance)
    return detector.detect_performance_characteristics()


def get_comprehensive_environment_analysis(
    tracer_instance: Optional[Any] = None,
) -> Dict[str, Any]:
    """Get comprehensive environment analysis with per-tracer caching.

    Each tracer instance maintains its own environment detector and cache,
    ensuring full isolation in multi-instance architectures.

    Args:
        tracer_instance: Optional tracer instance for logging and cache isolation

    Returns:
        Complete environment analysis
    """
    # Use tracer-specific detector if tracer instance provided
    if tracer_instance is not None:
        # Check if tracer already has an environment detector
        if not hasattr(tracer_instance, "_environment_detector"):
            # Protected access required for multi-instance architecture
            tracer_instance._environment_detector = EnvironmentDetector(
                tracer_instance
            )  # pylint: disable=protected-access

        return dict(
            tracer_instance._environment_detector.get_comprehensive_analysis()  # pylint: disable=protected-access
        )

    # For standalone usage (no tracer), create a temporary detector
    detector = EnvironmentDetector(None)
    return detector.get_comprehensive_analysis()


def clear_environment_cache(tracer_instance: Optional[Any] = None) -> None:
    """Clear environment detection cache for a specific tracer instance.

    Args:
        tracer_instance: Tracer instance whose cache should be cleared.
                        If None, this is a no-op for standalone usage.
    """
    if tracer_instance is not None and hasattr(
        tracer_instance, "_environment_detector"
    ):
        # Protected access required for multi-instance cache management
        tracer_instance._environment_detector._cache.clear()  # pylint: disable=protected-access

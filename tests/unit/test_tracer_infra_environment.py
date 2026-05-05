"""Unit tests for honeyhive.tracer.infra.environment.

This module contains comprehensive unit tests for environment detection and
resource analysis functionality in the HoneyHive tracer infrastructure.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

# pylint: disable=too-few-public-methods
# Justification: Test classes are focused on specific functionality

import os
from unittest.mock import Mock, patch

from honeyhive.tracer.infra.environment import (
    EnvironmentDetector,
    clear_environment_cache,
    get_comprehensive_environment_analysis,
    get_environment_type,
    get_performance_characteristics,
    get_resource_constraints,
)


class TestEnvironmentDetectorInitialization:
    """Test EnvironmentDetector initialization."""

    def test_init_with_tracer_instance(self) -> None:
        """Test initialization with tracer instance."""
        mock_tracer = Mock()
        detector = EnvironmentDetector(mock_tracer)

        assert detector.tracer_instance is mock_tracer
        assert not detector._cache

    def test_init_without_tracer_instance(self) -> None:
        """Test initialization without tracer instance."""
        detector = EnvironmentDetector(None)

        assert detector.tracer_instance is None
        assert not detector._cache

    def test_init_with_optional_tracer(self) -> None:
        """Test initialization with optional tracer parameter."""
        detector = EnvironmentDetector()

        assert detector.tracer_instance is None
        assert not detector._cache


class TestEnvironmentDetectorPrimaryEnvironmentType:
    """Test primary environment type detection."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "test-function"})
    def test_detect_aws_lambda_environment(self, __mock_safe_log: Mock) -> None:
        """Test detection of AWS Lambda environment."""
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "aws_lambda"
        assert detector._cache["environment_type"] == "aws_lambda"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"KUBERNETES_SERVICE_HOST": "10.0.0.1"})
    def test_detect_kubernetes_environment(self, _mock_safe_log: Mock) -> None:
        """Test detection of Kubernetes environment."""
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "kubernetes"
        assert detector._cache["environment_type"] == "kubernetes"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch("os.path.exists")
    def test_detect_docker_environment_with_dockerenv(
        self, mock_exists: Mock, _mock_safe_log: Mock
    ) -> None:
        """Test detection of Docker environment via .dockerenv file."""
        mock_exists.return_value = True
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "docker"
        mock_exists.assert_called_with("/.dockerenv")

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"DOCKER_CONTAINER": "true"})
    def test_detect_docker_environment_with_env_var(self, _mock_safe_log: Mock) -> None:
        """Test detection of Docker environment via environment variable."""
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "docker"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"})
    def test_detect_gcp_environment(self, _mock_safe_log: Mock) -> None:
        """Test detection of GCP environment."""
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "gcp"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"GCP_PROJECT": "test-project"})
    def test_detect_gcp_environment_alternative_var(self, _mock_safe_log: Mock) -> None:
        """Test detection of GCP environment with alternative variable."""
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "gcp"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"AZURE_RESOURCE_GROUP": "test-rg"})
    def test_detect_azure_environment(self, _mock_safe_log: Mock) -> None:
        """Test detection of Azure environment."""
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "azure"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"WEBSITE_RESOURCE_GROUP": "test-rg"})
    def test_detect_azure_environment_alternative_var(
        self, _mock_safe_log: Mock
    ) -> None:
        """Test detection of Azure environment with alternative variable."""
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "azure"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"AWS_REGION": "us-east-1"})
    def test_detect_aws_ec2_environment(self, _mock_safe_log: Mock) -> None:
        """Test detection of AWS EC2 environment."""
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "aws_ec2"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_detect_standard_environment(self, _mock_safe_log: Mock) -> None:
        """Test detection of standard environment when no cloud indicators."""
        detector = EnvironmentDetector()

        result = detector.detect_primary_environment_type()

        assert result == "standard"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_detect_environment_type_caching(self, _mock_safe_log: Mock) -> None:
        """Test that environment type detection uses caching."""
        detector = EnvironmentDetector()
        detector._cache["environment_type"] = "cached_type"

        result = detector.detect_primary_environment_type()

        assert result == "cached_type"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "test"})
    def test_detect_environment_type_exception_handling(
        self, _mock_safe_log: Mock
    ) -> None:
        """Test exception handling in environment type detection."""
        detector = EnvironmentDetector()

        with patch("os.getenv", side_effect=Exception("Test error")):
            result = detector.detect_primary_environment_type()

            assert result == "standard"
            _mock_safe_log.assert_called_with(
                detector.tracer_instance,
                "debug",
                "Error detecting environment type: Test error",
            )


class TestEnvironmentDetectorContainerEnvironment:
    """Test container environment detection."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch("os.path.exists")
    def test_detect_docker_container_with_dockerenv(
        self, mock_exists: Mock, _mock_safe_log: Mock
    ) -> None:
        """Test Docker container detection via .dockerenv file."""
        mock_exists.return_value = True
        detector = EnvironmentDetector()

        result = detector.detect_container_environment()

        assert result["container.runtime"] == "docker"
        mock_exists.assert_called_with("/.dockerenv")

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"DOCKER_CONTAINER": "true", "HOSTNAME": "container-123"})
    def test_detect_docker_container_with_hostname(self, _mock_safe_log: Mock) -> None:
        """Test Docker container detection with hostname."""
        detector = EnvironmentDetector()

        result = detector.detect_container_environment()

        assert result["container.runtime"] == "docker"
        assert result["container.id"] == "container-123"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(
        os.environ,
        {
            "KUBERNETES_SERVICE_HOST": "10.0.0.1",
            "K8S_CLUSTER_NAME": "test-cluster",
            "K8S_NAMESPACE": "test-namespace",
            "K8S_POD_NAME": "test-pod",
            "K8S_DEPLOYMENT_NAME": "test-deployment",
        },
    )
    def test_detect_kubernetes_container_full_info(self, _mock_safe_log: Mock) -> None:
        """Test Kubernetes container detection with full information."""
        detector = EnvironmentDetector()

        result = detector.detect_container_environment()

        assert result["k8s.cluster.name"] == "test-cluster"
        assert result["k8s.namespace.name"] == "test-namespace"
        assert result["k8s.pod.name"] == "test-pod"
        assert result["k8s.deployment.name"] == "test-deployment"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(
        os.environ, {"KUBERNETES_SERVICE_HOST": "10.0.0.1", "HOSTNAME": "fallback-pod"}
    )
    def test_detect_kubernetes_container_with_defaults(
        self, _mock_safe_log: Mock
    ) -> None:
        """Test Kubernetes container detection with default values."""
        detector = EnvironmentDetector()

        result = detector.detect_container_environment()

        assert result["k8s.cluster.name"] == "unknown"
        assert result["k8s.namespace.name"] == "default"
        assert result["k8s.pod.name"] == "fallback-pod"
        assert result["k8s.deployment.name"] == "unknown"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_detect_container_environment_empty(self, _mock_safe_log: Mock) -> None:
        """Test container environment detection with no container indicators."""
        detector = EnvironmentDetector()

        result = detector.detect_container_environment()

        assert not result

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_detect_container_environment_caching(self, _mock_safe_log: Mock) -> None:
        """Test that container environment detection uses caching."""
        detector = EnvironmentDetector()
        detector._cache["container_info"] = {"cached": "info"}

        result = detector.detect_container_environment()

        assert result == {"cached": "info"}

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"KUBERNETES_SERVICE_HOST": "10.0.0.1"})
    def test_detect_container_environment_exception_handling(
        self, _mock_safe_log: Mock
    ) -> None:
        """Test exception handling in container environment detection."""
        detector = EnvironmentDetector()

        with patch("os.getenv", side_effect=Exception("Test error")):
            result = detector.detect_container_environment()

            assert not result
            _mock_safe_log.assert_called_with(
                detector.tracer_instance,
                "debug",
                "Error detecting container environment: Test error",
            )


class TestEnvironmentDetectorCloudEnvironment:
    """Test cloud environment detection."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-east-1",
            "AWS_LAMBDA_FUNCTION_NAME": "test-function",
            "AWS_LAMBDA_FUNCTION_VERSION": "1",
            "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "512",
            "AWS_LAMBDA_FUNCTION_TIMEOUT": "30",
        },
    )
    @patch("platform.python_version")
    def test_detect_aws_lambda_cloud_environment(
        self, mock_python_version: Mock, _mock_safe_log: Mock
    ) -> None:
        """Test AWS Lambda cloud environment detection."""
        mock_python_version.return_value = "3.11.0"
        detector = EnvironmentDetector()

        result = detector.detect_cloud_environment()

        assert result["cloud.provider"] == "aws"
        assert result["cloud.region"] == "us-east-1"
        assert result["faas.name"] == "test-function"
        assert result["faas.version"] == "1"
        assert result["faas.runtime"] == "python3.11.0"
        assert result["faas.memory_size"] == "512"
        assert result["faas.timeout"] == "30"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"AWS_REGION": "us-west-2"})
    def test_detect_aws_ec2_cloud_environment(self, _mock_safe_log: Mock) -> None:
        """Test AWS EC2 cloud environment detection."""
        detector = EnvironmentDetector()

        result = detector.detect_cloud_environment()

        assert result["cloud.provider"] == "aws"
        assert result["cloud.region"] == "us-west-2"
        assert "faas.name" not in result

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(
        os.environ,
        {"GOOGLE_CLOUD_PROJECT": "test-project", "GOOGLE_CLOUD_REGION": "us-central1"},
    )
    def test_detect_gcp_cloud_environment(self, _mock_safe_log: Mock) -> None:
        """Test GCP cloud environment detection."""
        detector = EnvironmentDetector()

        result = detector.detect_cloud_environment()

        assert result["cloud.provider"] == "gcp"
        assert result["cloud.region"] == "us-central1"
        assert result["gcp.project.id"] == "test-project"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"GCP_PROJECT": "alt-project"})
    def test_detect_gcp_cloud_environment_alternative_var(
        self, _mock_safe_log: Mock
    ) -> None:
        """Test GCP cloud environment detection with alternative variable."""
        detector = EnvironmentDetector()

        result = detector.detect_cloud_environment()

        assert result["cloud.provider"] == "gcp"
        assert result["cloud.region"] == "unknown"
        assert result["gcp.project.id"] == "alt-project"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(
        os.environ, {"AZURE_RESOURCE_GROUP": "test-rg", "AZURE_REGION": "eastus"}
    )
    def test_detect_azure_cloud_environment(self, _mock_safe_log: Mock) -> None:
        """Test Azure cloud environment detection."""
        detector = EnvironmentDetector()

        result = detector.detect_cloud_environment()

        assert result["cloud.provider"] == "azure"
        assert result["cloud.region"] == "eastus"
        assert result["azure.resource_group"] == "test-rg"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"WEBSITE_RESOURCE_GROUP": "webapp-rg"})
    def test_detect_azure_cloud_environment_alternative_var(
        self, _mock_safe_log: Mock
    ) -> None:
        """Test Azure cloud environment detection with alternative variable."""
        detector = EnvironmentDetector()

        result = detector.detect_cloud_environment()

        assert result["cloud.provider"] == "azure"
        assert result["cloud.region"] == "unknown"
        assert result["azure.resource_group"] == "webapp-rg"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_detect_cloud_environment_empty(self, _mock_safe_log: Mock) -> None:
        """Test cloud environment detection with no cloud indicators."""
        detector = EnvironmentDetector()

        result = detector.detect_cloud_environment()

        assert not result

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_detect_cloud_environment_caching(self, _mock_safe_log: Mock) -> None:
        """Test that cloud environment detection uses caching."""
        detector = EnvironmentDetector()
        detector._cache["cloud_info"] = {"cached": "cloud"}

        result = detector.detect_cloud_environment()

        assert result == {"cached": "cloud"}

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"AWS_REGION": "us-east-1"})
    def test_detect_cloud_environment_exception_handling(
        self, _mock_safe_log: Mock
    ) -> None:
        """Test exception handling in cloud environment detection."""
        detector = EnvironmentDetector()

        with patch("os.getenv", side_effect=Exception("Test error")):
            result = detector.detect_cloud_environment()

            assert not result
            _mock_safe_log.assert_called_with(
                detector.tracer_instance,
                "debug",
                "Error detecting cloud environment: Test error",
            )


class TestEnvironmentDetectorResourceConstraints:
    """Test resource constraints detection."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.object(EnvironmentDetector, "_analyze_memory_constraints_dynamically")
    @patch.object(EnvironmentDetector, "_analyze_cpu_constraints_dynamically")
    @patch.object(EnvironmentDetector, "_analyze_network_constraints_dynamically")
    def test_detect_resource_constraints_success(
        self,
        mock_network: Mock,
        mock_cpu: Mock,
        mock_memory: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test successful resource constraints detection."""
        mock_memory.return_value = {"memory_tier": "medium"}
        mock_cpu.return_value = {"cpu_tier": "high"}
        mock_network.return_value = {"network_tier": "standard"}

        detector = EnvironmentDetector()
        result = detector.detect_resource_constraints()

        assert result["memory_tier"] == "medium"
        assert result["cpu_tier"] == "high"
        assert result["network_tier"] == "standard"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_detect_resource_constraints_caching(self, _mock_safe_log: Mock) -> None:
        """Test that resource constraints detection uses caching."""
        detector = EnvironmentDetector()
        detector._cache["resource_constraints"] = {"cached": "constraints"}

        result = detector.detect_resource_constraints()

        assert result == {"cached": "constraints"}

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.object(EnvironmentDetector, "_get_fallback_resource_constraints")
    @patch.object(EnvironmentDetector, "_analyze_memory_constraints_dynamically")
    def test_detect_resource_constraints_exception_handling(
        self,
        mock_memory: Mock,
        mock_fallback: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test exception handling in resource constraints detection."""
        mock_memory.side_effect = Exception("Test error")
        mock_fallback.return_value = {"fallback": "constraints"}

        detector = EnvironmentDetector()
        result = detector.detect_resource_constraints()

        assert result == {"fallback": "constraints"}
        _mock_safe_log.assert_called_with(
            detector.tracer_instance,
            "debug",
            "Error detecting resource constraints: Test error",
        )


class TestEnvironmentDetectorMemoryConstraints:
    """Test memory constraints analysis."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "1024"})
    def test_analyze_memory_constraints_lambda(self, _mock_safe_log: Mock) -> None:
        """Test memory constraints analysis for Lambda environment."""
        detector = EnvironmentDetector()

        result = detector._analyze_memory_constraints_dynamically()

        assert result["memory_mb"] == 1024
        assert result["memory_tier"] == "medium"
        assert result["memory_source"] == "lambda_config"
        assert result["memory_constraint_factor"] == 1.0

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.object(EnvironmentDetector, "_detect_container_memory_limit")
    def test_analyze_memory_constraints_container(
        self, mock_container_memory: Mock, _mock_safe_log: Mock
    ) -> None:
        """Test memory constraints analysis for container environment."""
        mock_container_memory.return_value = 2048
        detector = EnvironmentDetector()

        result = detector._analyze_memory_constraints_dynamically()

        assert result["memory_mb"] == 2048
        assert result["memory_tier"] == "high"
        assert result["memory_source"] == "container_cgroup"
        assert result["memory_constraint_factor"] == 1.3

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.object(EnvironmentDetector, "_detect_container_memory_limit")
    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "_estimate_memory_by_environment")
    def test_analyze_memory_constraints_estimated(
        self,
        mock_estimate: Mock,
        mock_env_type: Mock,
        mock_container_memory: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test memory constraints analysis with estimation."""
        mock_container_memory.return_value = None
        mock_env_type.return_value = "docker"
        mock_estimate.return_value = 1024
        detector = EnvironmentDetector()

        result = detector._analyze_memory_constraints_dynamically()

        assert result["memory_tier"] == "medium"
        assert result["memory_source"] == "environment_estimated"
        assert result["memory_constraint_factor"] == 1.0


class TestEnvironmentDetectorCpuConstraints:
    """Test CPU constraints analysis."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch("multiprocessing.cpu_count")
    def test_analyze_cpu_constraints_success(
        self, mock_cpu_count: Mock, _mock_safe_log: Mock
    ) -> None:
        """Test successful CPU constraints analysis."""
        mock_cpu_count.return_value = 4
        detector = EnvironmentDetector()

        result = detector._analyze_cpu_constraints_dynamically()

        assert result["cpu_count"] == 4
        assert result["cpu_tier"] == "medium"
        assert result["cpu_source"] == "detected"
        assert result["cpu_scaling_factor"] == 1.0

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch("multiprocessing.cpu_count")
    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "_estimate_cpu_by_environment")
    def test_analyze_cpu_constraints_fallback(
        self,
        mock_estimate: Mock,
        mock_env_type: Mock,
        mock_cpu_count: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test CPU constraints analysis with fallback."""
        mock_cpu_count.side_effect = Exception("CPU detection failed")
        mock_env_type.return_value = "aws_lambda"
        mock_estimate.return_value = 1
        detector = EnvironmentDetector()

        result = detector._analyze_cpu_constraints_dynamically()

        assert result["cpu_count"] == 1
        assert result["cpu_tier"] == "minimal"
        assert result["cpu_source"] == "environment_fallback"
        assert result["cpu_scaling_factor"] == 0.5


class TestEnvironmentDetectorNetworkConstraints:
    """Test network constraints analysis."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_cloud_environment")
    @patch.object(EnvironmentDetector, "detect_container_environment")
    def test_analyze_network_constraints_serverless(
        self,
        mock_container: Mock,
        mock_cloud: Mock,
        mock_env_type: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test network constraints analysis for serverless environment."""
        mock_env_type.return_value = "aws_lambda"
        mock_cloud.return_value = {"faas.name": "test-function"}
        mock_container.return_value = {}
        detector = EnvironmentDetector()

        result = detector._analyze_network_constraints_dynamically()

        assert result["network_tier"] == "serverless_constrained"
        assert result["network_scaling_factor"] == 0.3
        assert result["connection_limit_factor"] == 0.2

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_cloud_environment")
    @patch.object(EnvironmentDetector, "detect_container_environment")
    def test_analyze_network_constraints_kubernetes(
        self,
        mock_container: Mock,
        mock_cloud: Mock,
        mock_env_type: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test network constraints analysis for Kubernetes environment."""
        mock_env_type.return_value = "kubernetes"
        mock_cloud.return_value = {}
        mock_container.return_value = {"k8s.cluster.name": "test-cluster"}
        detector = EnvironmentDetector()

        result = detector._analyze_network_constraints_dynamically()

        assert result["network_tier"] == "orchestrated_managed"
        assert result["network_scaling_factor"] == 0.8
        assert result["connection_limit_factor"] == 0.8


class TestEnvironmentDetectorCalculationMethods:
    """Test calculation methods for tiers and factors."""

    def test_calculate_memory_tier_dynamically(self) -> None:
        """Test memory tier calculation with various memory sizes."""
        detector = EnvironmentDetector()

        assert detector._calculate_memory_tier_dynamically(128) == "minimal"
        assert detector._calculate_memory_tier_dynamically(512) == "low"
        assert detector._calculate_memory_tier_dynamically(1024) == "medium"
        assert detector._calculate_memory_tier_dynamically(2048) == "high"
        assert detector._calculate_memory_tier_dynamically(4096) == "high"

    def test_calculate_cpu_tier_dynamically(self) -> None:
        """Test CPU tier calculation with various CPU counts."""
        detector = EnvironmentDetector()

        assert detector._calculate_cpu_tier_dynamically(1) == "minimal"
        assert detector._calculate_cpu_tier_dynamically(2) == "low"
        assert detector._calculate_cpu_tier_dynamically(4) == "medium"
        assert detector._calculate_cpu_tier_dynamically(8) == "high"
        assert detector._calculate_cpu_tier_dynamically(16) == "very_high"

    def test_calculate_network_tier_dynamically(self) -> None:
        """Test network tier calculation with various environments."""
        detector = EnvironmentDetector()

        # Serverless environment
        result = detector._calculate_network_tier_dynamically(
            "aws_lambda", {"faas.name": "test"}, {}
        )
        assert result == "serverless_constrained"

        # Kubernetes environment
        result = detector._calculate_network_tier_dynamically(
            "kubernetes", {}, {"k8s.cluster.name": "test"}
        )
        assert result == "orchestrated_managed"

        # Container environment
        result = detector._calculate_network_tier_dynamically(
            "docker", {}, {"container.runtime": "docker"}
        )
        assert result == "containerized_isolated"

        # Cloud environment
        result = detector._calculate_network_tier_dynamically(
            "aws_ec2", {"cloud.provider": "aws"}, {}
        )
        assert result == "cloud_aws_optimized"

        # Standard environment
        result = detector._calculate_network_tier_dynamically("standard", {}, {})
        assert result == "standard_networking"

    def test_calculate_memory_constraint_factor(self) -> None:
        """Test memory constraint factor calculation."""
        detector = EnvironmentDetector()

        assert detector._calculate_memory_constraint_factor(128) == 0.3
        assert detector._calculate_memory_constraint_factor(256) == 0.5
        assert detector._calculate_memory_constraint_factor(512) == 0.7
        assert detector._calculate_memory_constraint_factor(1024) == 1.0
        assert detector._calculate_memory_constraint_factor(2048) == 1.3

    def test_calculate_cpu_scaling_factor(self) -> None:
        """Test CPU scaling factor calculation."""
        detector = EnvironmentDetector()

        assert detector._calculate_cpu_scaling_factor(1) == 0.5
        assert detector._calculate_cpu_scaling_factor(2) == 0.5
        assert detector._calculate_cpu_scaling_factor(4) == 1.0
        assert detector._calculate_cpu_scaling_factor(8) == 2.0
        assert detector._calculate_cpu_scaling_factor(16) == 2.0

    def test_calculate_network_scaling_factor(self) -> None:
        """Test network scaling factor calculation."""
        detector = EnvironmentDetector()

        assert (
            detector._calculate_network_scaling_factor("serverless_constrained") == 0.3
        )
        assert (
            detector._calculate_network_scaling_factor("containerized_isolated") == 0.6
        )
        assert detector._calculate_network_scaling_factor("orchestrated_managed") == 0.8
        assert detector._calculate_network_scaling_factor("cloud_aws_optimized") == 1.2
        assert detector._calculate_network_scaling_factor("cloud_gcp_optimized") == 1.1
        assert (
            detector._calculate_network_scaling_factor("cloud_azure_optimized") == 1.0
        )
        assert detector._calculate_network_scaling_factor("standard_networking") == 1.0
        assert detector._calculate_network_scaling_factor("unknown_tier") == 1.0

    def test_calculate_connection_limit_factor(self) -> None:
        """Test connection limit factor calculation."""
        detector = EnvironmentDetector()

        assert detector._calculate_connection_limit_factor("aws_lambda") == 0.2
        assert detector._calculate_connection_limit_factor("docker") == 0.6
        assert detector._calculate_connection_limit_factor("kubernetes") == 0.8
        assert detector._calculate_connection_limit_factor("gcp") == 1.0
        assert detector._calculate_connection_limit_factor("azure") == 1.0
        assert detector._calculate_connection_limit_factor("aws_ec2") == 1.2
        assert detector._calculate_connection_limit_factor("unknown") == 1.0


class TestEnvironmentDetectorContainerMemoryLimit:
    """Test container memory limit detection."""

    @patch("os.path.exists")
    @patch("builtins.open")
    def test_detect_container_memory_limit_success(
        self, mock_open: Mock, mock_exists: Mock
    ) -> None:
        """Test successful container memory limit detection."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "1073741824"
        detector = EnvironmentDetector()

        result = detector._detect_container_memory_limit()

        assert result == 1024  # 1073741824 bytes = 1024 MB

    @patch("os.path.exists")
    def test_detect_container_memory_limit_no_file(self, mock_exists: Mock) -> None:
        """Test container memory limit detection when no cgroup files exist."""
        mock_exists.return_value = False
        detector = EnvironmentDetector()

        result = detector._detect_container_memory_limit()

        assert result is None

    @patch("os.path.exists")
    @patch("builtins.open")
    def test_detect_container_memory_limit_max_value(
        self, mock_open: Mock, mock_exists: Mock
    ) -> None:
        """Test container memory limit detection with max cgroup value."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = str(1 << 62)
        detector = EnvironmentDetector()

        result = detector._detect_container_memory_limit()

        assert result is None

    @patch("os.path.exists")
    @patch("builtins.open")
    def test_detect_container_memory_limit_exception(
        self, mock_open: Mock, mock_exists: Mock
    ) -> None:
        """Test container memory limit detection with exception."""
        mock_exists.return_value = True
        mock_open.side_effect = Exception("File read error")
        detector = EnvironmentDetector()

        result = detector._detect_container_memory_limit()

        assert result is None


class TestEnvironmentDetectorEstimationMethods:
    """Test environment-based estimation methods."""

    def test_estimate_memory_by_environment(self) -> None:
        """Test memory estimation by environment type."""
        detector = EnvironmentDetector()

        assert detector._estimate_memory_by_environment("aws_lambda") == 512
        assert detector._estimate_memory_by_environment("docker") == 1024
        assert detector._estimate_memory_by_environment("kubernetes") == 2048
        assert detector._estimate_memory_by_environment("gcp") == 1024
        assert detector._estimate_memory_by_environment("azure") == 1024
        assert detector._estimate_memory_by_environment("aws_ec2") == 2048
        assert detector._estimate_memory_by_environment("unknown") == 1024

    def test_estimate_cpu_by_environment(self) -> None:
        """Test CPU estimation by environment type."""
        detector = EnvironmentDetector()

        assert detector._estimate_cpu_by_environment("aws_lambda") == 1
        assert detector._estimate_cpu_by_environment("docker") == 2
        assert detector._estimate_cpu_by_environment("kubernetes") == 2
        assert detector._estimate_cpu_by_environment("gcp") == 2
        assert detector._estimate_cpu_by_environment("azure") == 2
        assert detector._estimate_cpu_by_environment("aws_ec2") == 4
        assert detector._estimate_cpu_by_environment("unknown") == 2


class TestEnvironmentDetectorFallbackMethods:
    """Test fallback methods for error scenarios."""

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    def test_get_fallback_resource_constraints(self, mock_env_type: Mock) -> None:
        """Test fallback resource constraints generation."""
        mock_env_type.return_value = "docker"
        detector = EnvironmentDetector()

        result = detector._get_fallback_resource_constraints()

        assert result["memory_tier"] == "medium"
        assert result["cpu_tier"] == "medium"
        assert result["network_tier"] == "docker_fallback"
        assert result["memory_constraint_factor"] == 0.7
        assert result["cpu_scaling_factor"] == 1.0
        assert result["network_scaling_factor"] == 1.0
        assert result["connection_limit_factor"] == 1.0
        assert result["fallback_reason"] == "constraint_detection_failed"


class TestEnvironmentDetectorPerformanceCharacteristics:
    """Test performance characteristics detection."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.object(EnvironmentDetector, "_analyze_execution_model_dynamically")
    @patch.object(EnvironmentDetector, "_analyze_concurrency_patterns_dynamically")
    @patch.object(EnvironmentDetector, "_analyze_latency_sensitivity_dynamically")
    @patch.object(EnvironmentDetector, "_analyze_scaling_characteristics_dynamically")
    def test_detect_performance_characteristics_success(
        self,
        mock_scaling: Mock,
        mock_latency: Mock,
        mock_concurrency: Mock,
        mock_execution: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test successful performance characteristics detection."""
        mock_execution.return_value = {"execution_model": "serverless"}
        mock_concurrency.return_value = {"concurrency_pattern": "burst"}
        mock_latency.return_value = {"latency_sensitivity": "high"}
        mock_scaling.return_value = {"scaling_pattern": "aggressive"}

        detector = EnvironmentDetector()
        result = detector.detect_performance_characteristics()

        assert result["execution_model"] == "serverless"
        assert result["concurrency_pattern"] == "burst"
        assert result["latency_sensitivity"] == "high"
        assert result["scaling_pattern"] == "aggressive"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_detect_performance_characteristics_caching(
        self, _mock_safe_log: Mock
    ) -> None:
        """Test that performance characteristics detection uses caching."""
        detector = EnvironmentDetector()
        detector._cache["performance_characteristics"] = {"cached": "performance"}

        result = detector.detect_performance_characteristics()

        assert result == {"cached": "performance"}

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.object(EnvironmentDetector, "_get_fallback_performance_characteristics")
    @patch.object(EnvironmentDetector, "_analyze_execution_model_dynamically")
    def test_detect_performance_characteristics_exception_handling(
        self,
        mock_execution: Mock,
        mock_fallback: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test exception handling in performance characteristics detection."""
        mock_execution.side_effect = Exception("Test error")
        mock_fallback.return_value = {"fallback": "performance"}

        detector = EnvironmentDetector()
        result = detector.detect_performance_characteristics()

        assert result == {"fallback": "performance"}
        _mock_safe_log.assert_called_with(
            detector.tracer_instance,
            "debug",
            "Error detecting performance characteristics: Test error",
        )


class TestEnvironmentDetectorExecutionModel:
    """Test execution model analysis."""

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_cloud_environment")
    @patch.object(EnvironmentDetector, "detect_container_environment")
    def test_analyze_execution_model_serverless(
        self, mock_container: Mock, mock_cloud: Mock, mock_env_type: Mock
    ) -> None:
        """Test execution model analysis for serverless environment."""
        mock_env_type.return_value = "aws_lambda"
        mock_cloud.return_value = {"faas.name": "test-function"}
        mock_container.return_value = {}
        detector = EnvironmentDetector()

        result = detector._analyze_execution_model_dynamically()

        assert result["execution_model"] == "serverless"
        assert result["cold_start_sensitive"] is True
        assert result["connection_reuse_critical"] is True
        assert result["execution_time_limited"] is True
        assert result["memory_optimization_critical"] is True

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_cloud_environment")
    @patch.object(EnvironmentDetector, "detect_container_environment")
    def test_analyze_execution_model_orchestrated(
        self, mock_container: Mock, mock_cloud: Mock, mock_env_type: Mock
    ) -> None:
        """Test execution model analysis for orchestrated environment."""
        mock_env_type.return_value = "kubernetes"
        mock_cloud.return_value = {}
        mock_container.return_value = {"k8s.cluster.name": "test-cluster"}
        detector = EnvironmentDetector()

        result = detector._analyze_execution_model_dynamically()

        assert result["execution_model"] == "orchestrated"
        assert result["scaling_dynamic"] is True
        assert result["connection_persistence"] == "managed"
        assert result["resource_allocation_dynamic"] is True
        assert result["graceful_shutdown_required"] is True

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_cloud_environment")
    @patch.object(EnvironmentDetector, "detect_container_environment")
    def test_analyze_execution_model_containerized(
        self, mock_container: Mock, mock_cloud: Mock, mock_env_type: Mock
    ) -> None:
        """Test execution model analysis for containerized environment."""
        mock_env_type.return_value = "docker"
        mock_cloud.return_value = {}
        mock_container.return_value = {"container.runtime": "docker"}
        detector = EnvironmentDetector()

        result = detector._analyze_execution_model_dynamically()

        assert result["execution_model"] == "containerized"
        assert result["resource_constrained"] is True
        assert result["connection_persistence"] == "isolated"
        assert result["resource_allocation_fixed"] is True
        assert result["isolation_boundaries"] is True

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_cloud_environment")
    @patch.object(EnvironmentDetector, "detect_container_environment")
    def test_analyze_execution_model_persistent(
        self, mock_container: Mock, mock_cloud: Mock, mock_env_type: Mock
    ) -> None:
        """Test execution model analysis for persistent environment."""
        mock_env_type.return_value = "standard"
        mock_cloud.return_value = {}
        mock_container.return_value = {}
        detector = EnvironmentDetector()

        result = detector._analyze_execution_model_dynamically()

        assert result["execution_model"] == "persistent"
        assert result["connection_persistence"] == "long_lived"
        assert result["resource_allocation_stable"] is True
        assert result["scaling_manual"] is True
        assert result["full_system_access"] is True


class TestEnvironmentDetectorConcurrencyPatterns:
    """Test concurrency patterns analysis."""

    @patch.dict(os.environ, {"HH_HIGH_CONCURRENCY": "true"})
    def test_analyze_concurrency_patterns_high_explicit(self) -> None:
        """Test concurrency patterns analysis with explicit high concurrency."""
        detector = EnvironmentDetector()

        result = detector._analyze_concurrency_patterns_dynamically()

        assert result["concurrency_pattern"] == "high_explicit"
        assert result["concurrency_multiplier"] == 2.0
        assert result["connection_pool_scaling"] == "aggressive"

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    def test_analyze_concurrency_patterns_lambda(self, mock_env_type: Mock) -> None:
        """Test concurrency patterns analysis for Lambda environment."""
        mock_env_type.return_value = "aws_lambda"
        detector = EnvironmentDetector()

        result = detector._analyze_concurrency_patterns_dynamically()

        assert result["concurrency_pattern"] == "burst_serverless"
        assert result["concurrency_multiplier"] == 0.5
        assert result["connection_pool_scaling"] == "minimal"

    @patch.object(EnvironmentDetector, "detect_container_environment")
    def test_analyze_concurrency_patterns_kubernetes(
        self, mock_container: Mock
    ) -> None:
        """Test concurrency patterns analysis for Kubernetes environment."""
        mock_container.return_value = {"k8s.cluster.name": "test-cluster"}
        detector = EnvironmentDetector()

        result = detector._analyze_concurrency_patterns_dynamically()

        assert result["concurrency_pattern"] == "orchestrated_scaling"
        assert result["concurrency_multiplier"] == 1.2
        assert result["connection_pool_scaling"] == "managed"

    def test_analyze_concurrency_patterns_standard(self) -> None:
        """Test concurrency patterns analysis for standard environment."""
        detector = EnvironmentDetector()

        with patch.object(
            detector, "detect_primary_environment_type", return_value="standard"
        ):
            with patch.object(
                detector, "detect_container_environment", return_value={}
            ):
                result = detector._analyze_concurrency_patterns_dynamically()

        assert result["concurrency_pattern"] == "standard_persistent"
        assert result["concurrency_multiplier"] == 1.0
        assert result["connection_pool_scaling"] == "balanced"


class TestEnvironmentDetectorLatencySensitivity:
    """Test latency sensitivity analysis."""

    @patch.dict(os.environ, {"HH_SESSION_NAME": "benchmark-test"})
    def test_analyze_latency_sensitivity_performance_testing(self) -> None:
        """Test latency sensitivity analysis for performance testing."""
        detector = EnvironmentDetector()

        result = detector._analyze_latency_sensitivity_dynamically()

        assert result["latency_sensitivity"] == "critical_performance_testing"
        assert result["timeout_multiplier"] == 0.4
        assert result["retry_multiplier"] == 0.5

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    def test_analyze_latency_sensitivity_lambda(self, mock_env_type: Mock) -> None:
        """Test latency sensitivity analysis for Lambda environment."""
        mock_env_type.return_value = "aws_lambda"
        detector = EnvironmentDetector()

        result = detector._analyze_latency_sensitivity_dynamically()

        assert result["latency_sensitivity"] == "high_serverless_constraints"
        assert result["timeout_multiplier"] == 0.6
        assert result["retry_multiplier"] == 0.7

    @patch.dict(os.environ, {"PROD": "true"})
    def test_analyze_latency_sensitivity_production(self) -> None:
        """Test latency sensitivity analysis for production environment."""
        detector = EnvironmentDetector()

        result = detector._analyze_latency_sensitivity_dynamically()

        assert result["latency_sensitivity"] == "high_production"
        assert result["timeout_multiplier"] == 0.8
        assert result["retry_multiplier"] == 1.2

    @patch.dict(os.environ, {"DEV": "true"})
    def test_analyze_latency_sensitivity_development(self) -> None:
        """Test latency sensitivity analysis for development environment."""
        detector = EnvironmentDetector()

        result = detector._analyze_latency_sensitivity_dynamically()

        assert result["latency_sensitivity"] == "low_development"
        assert result["timeout_multiplier"] == 1.5
        assert result["retry_multiplier"] == 1.0

    def test_analyze_latency_sensitivity_standard(self) -> None:
        """Test latency sensitivity analysis for standard environment."""
        detector = EnvironmentDetector()

        result = detector._analyze_latency_sensitivity_dynamically()

        assert result["latency_sensitivity"] == "standard_balanced"
        assert result["timeout_multiplier"] == 1.0
        assert result["retry_multiplier"] == 1.0


class TestEnvironmentDetectorScalingCharacteristics:
    """Test scaling characteristics analysis."""

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_resource_constraints")
    def test_analyze_scaling_characteristics_constrained(
        self, mock_constraints: Mock, mock_env_type: Mock
    ) -> None:
        """Test scaling characteristics analysis for constrained environment."""
        mock_env_type.return_value = "aws_lambda"
        mock_constraints.return_value = {
            "memory_constraint_factor": 0.3,
            "cpu_scaling_factor": 0.5,
            "network_scaling_factor": 0.3,
        }
        detector = EnvironmentDetector()

        result = detector._analyze_scaling_characteristics_dynamically()

        assert result["scaling_pattern"] == "constrained_minimal"
        assert result["overall_scaling_factor"] < 0.5

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_resource_constraints")
    def test_analyze_scaling_characteristics_aggressive(
        self, mock_constraints: Mock, mock_env_type: Mock
    ) -> None:
        """Test scaling characteristics analysis for high-resource environment."""
        mock_env_type.return_value = "aws_ec2"
        mock_constraints.return_value = {
            "memory_constraint_factor": 1.3,
            "cpu_scaling_factor": 2.0,
            "network_scaling_factor": 1.2,
        }
        detector = EnvironmentDetector()

        result = detector._analyze_scaling_characteristics_dynamically()

        assert result["scaling_pattern"] == "aggressive_scaling"
        assert result["overall_scaling_factor"] > 1.3

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_resource_constraints")
    def test_analyze_scaling_characteristics_balanced(
        self, mock_constraints: Mock, mock_env_type: Mock
    ) -> None:
        """Test scaling characteristics analysis for balanced environment."""
        mock_env_type.return_value = "docker"
        mock_constraints.return_value = {
            "memory_constraint_factor": 1.0,
            "cpu_scaling_factor": 1.0,
            "network_scaling_factor": 1.0,
        }
        detector = EnvironmentDetector()

        result = detector._analyze_scaling_characteristics_dynamically()

        assert result["scaling_pattern"] == "balanced_scaling"
        assert 0.8 <= result["overall_scaling_factor"] <= 1.3


class TestEnvironmentDetectorFallbackPerformance:
    """Test fallback performance characteristics."""

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    def test_get_fallback_performance_characteristics(
        self, mock_env_type: Mock
    ) -> None:
        """Test fallback performance characteristics generation."""
        mock_env_type.return_value = "kubernetes"
        detector = EnvironmentDetector()

        result = detector._get_fallback_performance_characteristics()

        assert result["execution_model"] == "persistent"
        assert result["latency_sensitivity"] == "standard_fallback"
        assert result["concurrency_pattern"] == "kubernetes_fallback"
        assert result["scaling_pattern"] == "conservative_fallback"
        assert result["timeout_multiplier"] == 1.0
        assert result["retry_multiplier"] == 1.0
        assert result["concurrency_multiplier"] == 1.0
        assert result["overall_scaling_factor"] == 1.0
        assert result["fallback_reason"] == "performance_detection_failed"


class TestEnvironmentDetectorSystemInfo:
    """Test system information detection."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch("platform.system")
    @patch("platform.platform")
    @patch("platform.python_version")
    @patch("os.getpid")
    @patch("platform.machine")
    @patch.dict(os.environ, {"HOSTNAME": "test-host"})
    def test_detect_system_info_complete(  # pylint: disable=R0917 # too-many-positional-arguments
        self,
        mock_machine: Mock,
        mock_getpid: Mock,
        mock_python_version: Mock,
        mock_platform: Mock,
        mock_system: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test complete system information detection."""
        mock_system.return_value = "Linux"
        mock_platform.return_value = "Linux-5.4.0-x86_64"
        mock_python_version.return_value = "3.11.0"
        mock_getpid.return_value = 12345
        mock_machine.return_value = "x86_64"

        detector = EnvironmentDetector()
        result = detector.detect_system_info()

        assert result["os.type"] == "Linux"
        assert result["os.description"] == "Linux-5.4.0-x86_64"
        assert result["process.runtime.name"] == "python"
        assert result["process.runtime.version"] == "3.11.0"
        assert result["process.pid"] == 12345
        assert result["host.arch"] == "x86_64"
        assert result["host.name"] == "test-host"

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch("platform.system")
    @patch("platform.platform")
    @patch("platform.python_version")
    @patch("os.getpid")
    @patch("platform.machine")
    def test_detect_system_info_without_hostname(  # pylint: disable=R0917 # too-many-positional-arguments
        self,
        mock_machine: Mock,
        mock_getpid: Mock,
        mock_python_version: Mock,
        mock_platform: Mock,
        mock_system: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test system information detection without hostname."""
        mock_system.return_value = "Darwin"
        mock_platform.return_value = "Darwin-21.6.0-x86_64"
        mock_python_version.return_value = "3.11.0"
        mock_getpid.return_value = 54321
        mock_machine.return_value = "x86_64"

        detector = EnvironmentDetector()
        result = detector.detect_system_info()

        assert result["os.type"] == "Darwin"
        assert result["os.description"] == "Darwin-21.6.0-x86_64"
        assert result["process.runtime.name"] == "python"
        assert result["process.runtime.version"] == "3.11.0"
        assert result["process.pid"] == 54321
        assert result["host.arch"] == "x86_64"
        assert "host.name" not in result

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_detect_system_info_caching(self, _mock_safe_log: Mock) -> None:
        """Test that system info detection uses caching."""
        detector = EnvironmentDetector()
        detector._cache["system_info"] = {"cached": "system"}

        result = detector.detect_system_info()

        assert result == {"cached": "system"}

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch("platform.system")
    def test_detect_system_info_exception_handling(
        self, mock_system: Mock, _mock_safe_log: Mock
    ) -> None:
        """Test exception handling in system info detection."""
        mock_system.side_effect = Exception("System error")
        detector = EnvironmentDetector()

        result = detector.detect_system_info()

        assert not result
        _mock_safe_log.assert_called_with(
            detector.tracer_instance,
            "debug",
            "Error detecting system info: System error",
        )


class TestEnvironmentDetectorComprehensiveAnalysis:
    """Test comprehensive environment analysis."""

    @patch("honeyhive.tracer.infra.environment.safe_log")
    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    @patch.object(EnvironmentDetector, "detect_container_environment")
    @patch.object(EnvironmentDetector, "detect_cloud_environment")
    @patch.object(EnvironmentDetector, "detect_resource_constraints")
    @patch.object(EnvironmentDetector, "detect_performance_characteristics")
    @patch.object(EnvironmentDetector, "detect_system_info")
    def test_get_comprehensive_analysis_success(  # pylint: disable=R0917 # too-many-positional-arguments
        self,
        mock_system: Mock,
        mock_performance: Mock,
        mock_constraints: Mock,
        mock_cloud: Mock,
        mock_container: Mock,
        mock_env_type: Mock,
        _mock_safe_log: Mock,
    ) -> None:
        """Test successful comprehensive environment analysis."""
        mock_env_type.return_value = "aws_lambda"
        mock_container.return_value = {"container.runtime": "docker"}
        mock_cloud.return_value = {"cloud.provider": "aws"}
        mock_constraints.return_value = {"memory_tier": "medium"}
        mock_performance.return_value = {"execution_model": "serverless"}
        mock_system.return_value = {"os.type": "Linux"}

        detector = EnvironmentDetector()
        result = detector.get_comprehensive_analysis()

        assert result["environment_type"] == "aws_lambda"
        assert result["container_info"]["container.runtime"] == "docker"
        assert result["cloud_info"]["cloud.provider"] == "aws"
        assert result["resource_constraints"]["memory_tier"] == "medium"
        assert result["performance_characteristics"]["execution_model"] == "serverless"
        assert result["system_info"]["os.type"] == "Linux"

        _mock_safe_log.assert_called_with(
            detector.tracer_instance,
            "debug",
            "Environment analysis complete: aws_lambda",
            honeyhive_data={
                "environment_type": "aws_lambda",
                "has_container_info": True,
                "has_cloud_info": True,
                "resource_constraints": {"memory_tier": "medium"},
            },
        )

    @patch("honeyhive.tracer.infra.environment.safe_log")
    def test_get_comprehensive_analysis_caching(self, _mock_safe_log: Mock) -> None:
        """Test that comprehensive analysis uses caching."""
        detector = EnvironmentDetector()
        detector._cache["comprehensive_analysis"] = {"cached": "analysis"}

        result = detector.get_comprehensive_analysis()

        assert result == {"cached": "analysis"}


class TestEnvironmentDetectorCacheManagement:
    """Test cache management functionality."""

    def test_clear_cache(self) -> None:
        """Test cache clearing functionality."""
        detector = EnvironmentDetector()
        detector._cache = {"test": "data", "another": "value"}

        detector.clear_cache()

        assert not detector._cache


class TestModuleLevelFunctions:
    """Test module-level convenience functions."""

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    def test_get_environment_type_with_tracer(self, mock_detect: Mock) -> None:
        """Test get_environment_type function with tracer instance."""
        mock_detect.return_value = "aws_lambda"
        mock_tracer = Mock()

        result = get_environment_type(mock_tracer)

        assert result == "aws_lambda"

    @patch.object(EnvironmentDetector, "detect_primary_environment_type")
    def test_get_environment_type_without_tracer(self, mock_detect: Mock) -> None:
        """Test get_environment_type function without tracer instance."""
        mock_detect.return_value = "docker"

        result = get_environment_type()

        assert result == "docker"

    @patch.object(EnvironmentDetector, "detect_resource_constraints")
    def test_get_resource_constraints_with_tracer(self, mock_detect: Mock) -> None:
        """Test get_resource_constraints function with tracer instance."""
        mock_detect.return_value = {"memory_tier": "high"}
        mock_tracer = Mock()

        result = get_resource_constraints(mock_tracer)

        assert result == {"memory_tier": "high"}

    @patch.object(EnvironmentDetector, "detect_resource_constraints")
    def test_get_resource_constraints_without_tracer(self, mock_detect: Mock) -> None:
        """Test get_resource_constraints function without tracer instance."""
        mock_detect.return_value = {"cpu_tier": "medium"}

        result = get_resource_constraints()

        assert result == {"cpu_tier": "medium"}

    @patch.object(EnvironmentDetector, "detect_performance_characteristics")
    def test_get_performance_characteristics_with_tracer(
        self, mock_detect: Mock
    ) -> None:
        """Test get_performance_characteristics function with tracer instance."""
        mock_detect.return_value = {"execution_model": "orchestrated"}
        mock_tracer = Mock()

        result = get_performance_characteristics(mock_tracer)

        assert result == {"execution_model": "orchestrated"}

    @patch.object(EnvironmentDetector, "detect_performance_characteristics")
    def test_get_performance_characteristics_without_tracer(
        self, mock_detect: Mock
    ) -> None:
        """Test get_performance_characteristics function without tracer instance."""
        mock_detect.return_value = {"latency_sensitivity": "high"}

        result = get_performance_characteristics()

        assert result == {"latency_sensitivity": "high"}

    def test_get_comprehensive_environment_analysis_with_tracer(self) -> None:
        """Test get_comprehensive_environment_analysis with tracer instance."""
        mock_tracer = Mock()
        mock_detector = Mock()
        mock_detector.get_comprehensive_analysis.return_value = {"complete": "analysis"}
        mock_tracer._environment_detector = mock_detector

        with patch("builtins.hasattr", return_value=True):
            result = get_comprehensive_environment_analysis(mock_tracer)

        assert result == {"complete": "analysis"}
        mock_detector.get_comprehensive_analysis.assert_called_once_with()

    @patch.object(EnvironmentDetector, "get_comprehensive_analysis")
    def test_get_comprehensive_environment_analysis_create_detector(
        self, mock_analysis: Mock
    ) -> None:
        """Test get_comprehensive_environment_analysis creating new detector."""
        mock_analysis.return_value = {"new": "analysis"}
        mock_tracer = Mock()

        with patch("builtins.hasattr", return_value=False):
            result = get_comprehensive_environment_analysis(mock_tracer)

        assert result == {"new": "analysis"}
        assert hasattr(mock_tracer, "_environment_detector")

    @patch.object(EnvironmentDetector, "get_comprehensive_analysis")
    def test_get_comprehensive_environment_analysis_without_tracer(
        self, mock_analysis: Mock
    ) -> None:
        """Test get_comprehensive_environment_analysis without tracer instance."""
        mock_analysis.return_value = {"standalone": "analysis"}

        result = get_comprehensive_environment_analysis()

        assert result == {"standalone": "analysis"}

    def test_clear_environment_cache_with_tracer(self) -> None:
        """Test clear_environment_cache with tracer instance."""
        mock_tracer = Mock()
        mock_detector = Mock()
        mock_tracer._environment_detector = mock_detector

        with patch("builtins.hasattr", return_value=True):
            clear_environment_cache(mock_tracer)

        # Function should complete without error

    def test_clear_environment_cache_without_detector(self) -> None:
        """Test clear_environment_cache with tracer but no detector."""
        mock_tracer = Mock()

        with patch("builtins.hasattr", return_value=False):
            clear_environment_cache(mock_tracer)

        # Should not raise exception

    def test_clear_environment_cache_without_tracer(self) -> None:
        """Test clear_environment_cache without tracer instance."""
        clear_environment_cache(None)

        # Should not raise exception

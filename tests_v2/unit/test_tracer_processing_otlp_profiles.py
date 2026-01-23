"""Unit tests for honeyhive.tracer.processing.otlp_profiles.

This module contains comprehensive unit tests for OTLP profile management,
including environment-specific configuration profiles, dynamic adjustments,
and environment analysis functions.
"""

# pylint: disable=too-many-lines,duplicate-code
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from honeyhive.tracer.processing.otlp_profiles import (
    EnvironmentProfile,
    EnvironmentProfileManager,
    _analyze_performance_characteristics,
    _analyze_resource_constraints,
    _determine_environment_type,
    get_environment_optimized_config,
)
from honeyhive.tracer.processing.otlp_session import OTLPSessionConfig


@pytest.fixture
def sample_environment_profile() -> EnvironmentProfile:
    """Create a sample environment profile for testing."""
    return EnvironmentProfile(
        name="Test Profile",
        description="Test environment profile for unit testing",
        pool_connections=10,
        pool_maxsize=20,
        max_retries=3,
        timeout=30.0,
        backoff_factor=0.5,
        pool_block=False,
        additional_config={"test_key": "test_value"},
    )


@pytest.fixture
def mock_container_info() -> Dict[str, Any]:
    """Create mock container information for testing."""
    return {
        "container.runtime": "docker",
        "k8s.cluster.name": "test-cluster",
        "container.id": "test-container-123",
    }


@pytest.fixture
def mock_cloud_info() -> Dict[str, Any]:
    """Create mock cloud information for testing."""
    return {
        "cloud.provider": "aws",
        "cloud.region": "us-east-1",
        "faas.name": "test-lambda",
    }


@pytest.fixture
def mock_tracer_instance() -> Mock:
    """Create a mock tracer instance for testing."""
    tracer = Mock()
    tracer.batch_size = 100
    tracer.disable_batch = False
    tracer.verbose = False
    tracer.config = Mock()
    tracer.config.batch_size = 100
    return tracer


class TestEnvironmentProfile:
    """Test cases for EnvironmentProfile Pydantic model."""

    def test_environment_profile_creation_valid_data(self) -> None:
        """Test creating EnvironmentProfile with valid data."""
        profile = EnvironmentProfile(
            name="Test Profile",
            description="Test description",
            pool_connections=5,
            pool_maxsize=10,
            max_retries=2,
            timeout=15.0,
            backoff_factor=0.3,
            pool_block=True,
            additional_config={"key": "value"},
        )

        assert profile.name == "Test Profile"
        assert profile.description == "Test description"
        assert profile.pool_connections == 5
        assert profile.pool_maxsize == 10
        assert profile.max_retries == 2
        assert profile.timeout == 15.0
        assert profile.backoff_factor == 0.3
        assert profile.pool_block is True
        assert profile.additional_config == {"key": "value"}

    def test_environment_profile_creation_minimal_data(self) -> None:
        """Test creating EnvironmentProfile with minimal required data."""
        profile = EnvironmentProfile(
            name="Minimal Profile",
            pool_connections=1,
            pool_maxsize=2,
            max_retries=1,
            timeout=5.0,
            backoff_factor=0.1,
        )

        assert profile.name == "Minimal Profile"
        assert profile.description == ""
        assert profile.pool_block is False
        assert profile.additional_config is None

    def test_environment_profile_validation_constraints(self) -> None:
        """Test EnvironmentProfile field validation constraints."""
        # Test pool_connections constraints
        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="Test",
                pool_connections=0,  # Below minimum
                pool_maxsize=5,
                max_retries=1,
                timeout=5.0,
                backoff_factor=0.1,
            )

        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="Test",
                pool_connections=51,  # Above maximum
                pool_maxsize=5,
                max_retries=1,
                timeout=5.0,
                backoff_factor=0.1,
            )

    def test_environment_profile_pool_maxsize_validator(self) -> None:
        """Test pool_maxsize validator ensures it's >= pool_connections."""
        # Test automatic adjustment when pool_maxsize < pool_connections
        profile = EnvironmentProfile(
            name="Test Profile",
            pool_connections=15,
            pool_maxsize=10,  # Less than pool_connections
            max_retries=1,
            timeout=5.0,
            backoff_factor=0.1,
        )

        # Should be adjusted to at least pool_connections value
        assert profile.pool_maxsize >= profile.pool_connections

    def test_environment_profile_name_validation(self) -> None:
        """Test name field validation constraints."""
        # Test empty name
        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="",  # Empty name
                pool_connections=1,
                pool_maxsize=2,
                max_retries=1,
                timeout=5.0,
                backoff_factor=0.1,
            )

        # Test name too long
        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="x" * 101,  # Too long
                pool_connections=1,
                pool_maxsize=2,
                max_retries=1,
                timeout=5.0,
                backoff_factor=0.1,
            )

    def test_environment_profile_timeout_validation(self) -> None:
        """Test timeout field validation constraints."""
        # Test zero timeout
        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="Test",
                pool_connections=1,
                pool_maxsize=2,
                max_retries=1,
                timeout=0.0,  # Invalid timeout
                backoff_factor=0.1,
            )

        # Test negative timeout
        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="Test",
                pool_connections=1,
                pool_maxsize=2,
                max_retries=1,
                timeout=-5.0,  # Negative timeout
                backoff_factor=0.1,
            )


class TestDetermineEnvironmentType:
    """Test cases for _determine_environment_type function."""

    def test_determine_environment_type_aws_lambda(self) -> None:
        """Test environment type determination for AWS Lambda."""
        cloud_info: Dict[str, Any] = {"faas.name": "test-lambda-function"}
        container_info: Dict[str, Any] = {}

        result = _determine_environment_type(container_info, cloud_info)

        assert result == "aws_lambda"

    def test_determine_environment_type_kubernetes(self) -> None:
        """Test environment type determination for Kubernetes."""
        container_info: Dict[str, Any] = {"k8s.cluster.name": "test-cluster"}
        cloud_info: Dict[str, Any] = {}

        result = _determine_environment_type(container_info, cloud_info)

        assert result == "kubernetes"

    def test_determine_environment_type_docker(self) -> None:
        """Test environment type determination for Docker."""
        container_info: Dict[str, Any] = {"container.runtime": "docker"}
        cloud_info: Dict[str, Any] = {}

        result = _determine_environment_type(container_info, cloud_info)

        assert result == "docker"

    def test_determine_environment_type_aws_ec2(self) -> None:
        """Test environment type determination for AWS EC2."""
        container_info: Dict[str, Any] = {}
        cloud_info: Dict[str, Any] = {"cloud.provider": "aws"}

        result = _determine_environment_type(container_info, cloud_info)

        assert result == "aws_ec2"

    def test_determine_environment_type_gcp(self) -> None:
        """Test environment type determination for GCP."""
        container_info: Dict[str, Any] = {}
        cloud_info: Dict[str, Any] = {"cloud.provider": "gcp"}

        result = _determine_environment_type(container_info, cloud_info)

        assert result == "gcp"

    def test_determine_environment_type_azure(self) -> None:
        """Test environment type determination for Azure."""
        container_info: Dict[str, Any] = {}
        cloud_info: Dict[str, Any] = {"cloud.provider": "azure"}

        result = _determine_environment_type(container_info, cloud_info)

        assert result == "azure"

    def test_determine_environment_type_standard_fallback(self) -> None:
        """Test environment type determination fallback to standard."""
        container_info: Dict[str, Any] = {}
        cloud_info: Dict[str, Any] = {}

        result = _determine_environment_type(container_info, cloud_info)

        assert result == "standard"

    def test_determine_environment_type_priority_order(self) -> None:
        """Test that serverless takes priority over other environment types."""
        # Lambda should take priority over Kubernetes
        container_info = {"k8s.cluster.name": "test-cluster"}
        cloud_info = {"faas.name": "test-lambda", "cloud.provider": "aws"}

        result = _determine_environment_type(container_info, cloud_info)

        assert result == "aws_lambda"


class TestAnalyzeResourceConstraints:
    """Test cases for _analyze_resource_constraints function."""

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    @patch("honeyhive.tracer.processing.otlp_profiles.multiprocessing.cpu_count")
    def test_analyze_resource_constraints_lambda_memory(
        self, mock_cpu_count: Mock, mock_getenv: Mock
    ) -> None:
        """Test resource constraints analysis with Lambda memory setting."""
        mock_getenv.return_value = "512"  # AWS Lambda memory size
        mock_cpu_count.return_value = 2

        result = _analyze_resource_constraints()

        assert result["memory_mb"] == 512
        assert result["memory_tier"] == "medium"
        assert result["cpu_count"] == 2
        assert result["cpu_tier"] == "low"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    @patch("honeyhive.tracer.processing.otlp_profiles.multiprocessing.cpu_count")
    def test_analyze_resource_constraints_high_memory(
        self, mock_cpu_count: Mock, mock_getenv: Mock
    ) -> None:
        """Test resource constraints analysis with high memory."""
        mock_getenv.return_value = "2048"  # High memory
        mock_cpu_count.return_value = 8

        result = _analyze_resource_constraints()

        assert result["memory_mb"] == 2048
        assert result["memory_tier"] == "high"
        assert result["cpu_count"] == 8
        assert result["cpu_tier"] == "medium"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    @patch("honeyhive.tracer.processing.otlp_profiles.multiprocessing.cpu_count")
    def test_analyze_resource_constraints_low_memory(
        self, mock_cpu_count: Mock, mock_getenv: Mock
    ) -> None:
        """Test resource constraints analysis with low memory."""
        mock_getenv.return_value = "256"  # Low memory
        mock_cpu_count.return_value = 1

        result = _analyze_resource_constraints()

        assert result["memory_mb"] == 256
        assert result["memory_tier"] == "low"
        assert result["cpu_count"] == 1
        assert result["cpu_tier"] == "low"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    @patch("honeyhive.tracer.processing.otlp_profiles.multiprocessing.cpu_count")
    def test_analyze_resource_constraints_no_lambda_memory(
        self, mock_cpu_count: Mock, mock_getenv: Mock
    ) -> None:
        """Test resource constraints analysis without Lambda memory setting."""
        mock_getenv.return_value = None  # No Lambda memory
        mock_cpu_count.return_value = 4

        result = _analyze_resource_constraints()

        assert "memory_mb" not in result
        assert result["memory_tier"] == "medium"
        assert result["cpu_count"] == 4
        assert result["cpu_tier"] == "medium"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    @patch("honeyhive.tracer.processing.otlp_profiles.multiprocessing.cpu_count")
    def test_analyze_resource_constraints_cpu_exception(
        self, mock_cpu_count: Mock, mock_getenv: Mock
    ) -> None:
        """Test resource constraints analysis when CPU count fails."""
        mock_getenv.return_value = None
        mock_cpu_count.side_effect = Exception("CPU count failed")

        result = _analyze_resource_constraints()

        assert result["cpu_count"] == 1
        assert result["cpu_tier"] == "low"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_resource_constraints_exception_handling(
        self, mock_getenv: Mock
    ) -> None:
        """Test resource constraints analysis exception handling."""
        mock_getenv.side_effect = Exception("Environment access failed")

        result = _analyze_resource_constraints()

        assert "analysis_error" in result
        assert "Environment access failed" in result["analysis_error"]


class TestAnalyzePerformanceCharacteristics:
    """Test cases for _analyze_performance_characteristics function."""

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_performance_characteristics_aws_lambda(
        self, mock_getenv: Mock
    ) -> None:
        """Test performance characteristics analysis for AWS Lambda."""
        mock_getenv.side_effect = lambda key, default=None: {
            "HH_HIGH_CONCURRENCY": None,
            "HH_SESSION_NAME": "test-session",
        }.get(key, default)

        result = _analyze_performance_characteristics("aws_lambda")

        assert result["execution_model"] == "serverless"
        assert result["cold_start_sensitive"] is True
        assert result["connection_reuse_critical"] is True
        assert result["latency_sensitivity"] == "high"
        assert result["concurrency_pattern"] == "burst"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_performance_characteristics_kubernetes(
        self, mock_getenv: Mock
    ) -> None:
        """Test performance characteristics analysis for Kubernetes."""
        mock_getenv.side_effect = lambda key, default=None: {
            "HH_HIGH_CONCURRENCY": None,
            "HH_SESSION_NAME": "test-session",
        }.get(key, default)

        result = _analyze_performance_characteristics("kubernetes")

        assert result["execution_model"] == "orchestrated"
        assert result["scaling_dynamic"] is True
        assert result["connection_persistence"] == "medium"
        assert result["latency_sensitivity"] == "standard"
        assert result["concurrency_pattern"] == "standard"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_performance_characteristics_standard(
        self, mock_getenv: Mock
    ) -> None:
        """Test performance characteristics analysis for standard environment."""
        mock_getenv.side_effect = lambda key, default=None: {
            "HH_HIGH_CONCURRENCY": None,
            "HH_SESSION_NAME": "test-session",
        }.get(key, default)

        result = _analyze_performance_characteristics("standard")

        assert result["execution_model"] == "persistent"
        assert result["connection_persistence"] == "high"
        assert result["latency_sensitivity"] == "standard"
        assert result["concurrency_pattern"] == "standard"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_performance_characteristics_high_concurrency(
        self, mock_getenv: Mock
    ) -> None:
        """Test performance characteristics with high concurrency enabled."""
        mock_getenv.side_effect = lambda key, default=None: {
            "HH_HIGH_CONCURRENCY": "true",
            "HH_SESSION_NAME": "test-session",
        }.get(key, default)

        result = _analyze_performance_characteristics("standard")

        assert result["concurrency_pattern"] == "high"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_performance_characteristics_benchmark_session(
        self, mock_getenv: Mock
    ) -> None:
        """Test performance characteristics with benchmark session name."""
        mock_getenv.side_effect = lambda key, default=None: {
            "HH_HIGH_CONCURRENCY": None,
            "HH_SESSION_NAME": "benchmark-test-session",
        }.get(key, default)

        result = _analyze_performance_characteristics("standard")

        assert result["latency_sensitivity"] == "critical"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_performance_characteristics_load_session(
        self, mock_getenv: Mock
    ) -> None:
        """Test performance characteristics with load test session name."""
        mock_getenv.side_effect = lambda key, default=None: {
            "HH_HIGH_CONCURRENCY": None,
            "HH_SESSION_NAME": "load-test-session",
        }.get(key, default)

        result = _analyze_performance_characteristics("standard")

        assert result["latency_sensitivity"] == "critical"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_performance_characteristics_exception_handling(
        self, mock_getenv: Mock
    ) -> None:
        """Test performance characteristics analysis exception handling."""
        mock_getenv.side_effect = Exception("Environment access failed")

        result = _analyze_performance_characteristics("standard")

        assert "analysis_error" in result
        assert "Environment access failed" in result["analysis_error"]


class TestEnvironmentProfileManager:
    """Test cases for EnvironmentProfileManager class."""

    def test_environment_profile_manager_profiles_exist(self) -> None:
        """Test that all expected profiles exist in EnvironmentProfileManager."""
        expected_profiles = [
            "aws_lambda",
            "kubernetes",
            "docker",
            "gcp",
            "azure",
            "aws_ec2",
            "standard",
        ]

        for profile_name in expected_profiles:
            assert profile_name in EnvironmentProfileManager.PROFILES
            profile = EnvironmentProfileManager.PROFILES[profile_name]
            assert isinstance(profile, EnvironmentProfile)
            assert profile.name is not None
            assert profile.pool_connections > 0
            assert profile.pool_maxsize > 0

    @patch(
        "honeyhive.tracer.processing.otlp_profiles."
        "get_comprehensive_environment_analysis"
    )
    @patch("honeyhive.tracer.processing.otlp_profiles.safe_log")
    def test_get_optimal_profile_aws_lambda(
        self, mock_safe_log: Mock, mock_env_analysis: Mock, mock_tracer_instance: Mock
    ) -> None:
        """Test getting optimal profile for AWS Lambda environment."""
        mock_env_analysis.return_value = {
            "environment_type": "aws_lambda",
            "resource_constraints": {"memory_tier": "medium", "cpu_tier": "low"},
            "performance_characteristics": {"latency_sensitivity": "high"},
        }

        profile, environment_analysis = EnvironmentProfileManager.get_optimal_profile(
            mock_tracer_instance
        )

        assert profile.name.startswith("AWS Lambda")
        assert environment_analysis["environment_type"] == "aws_lambda"
        mock_safe_log.assert_called()

    @patch(
        "honeyhive.tracer.processing.otlp_profiles."
        "get_comprehensive_environment_analysis"
    )
    @patch("honeyhive.tracer.processing.otlp_profiles.safe_log")
    def test_get_optimal_profile_standard_fallback(
        self, mock_safe_log: Mock, mock_env_analysis: Mock, mock_tracer_instance: Mock
    ) -> None:
        """Test getting optimal profile with fallback to standard."""
        mock_env_analysis.return_value = {
            "environment_type": "unknown_environment",
            "resource_constraints": {},
            "performance_characteristics": {},
        }

        profile, environment_analysis = EnvironmentProfileManager.get_optimal_profile(
            mock_tracer_instance
        )

        assert profile.name.startswith("Standard Environment")
        assert environment_analysis["environment_type"] == "unknown_environment"
        mock_safe_log.assert_called()

    @patch(
        "honeyhive.tracer.processing.otlp_profiles."
        "get_comprehensive_environment_analysis"
    )
    @patch("honeyhive.tracer.processing.otlp_profiles.safe_log")
    def test_get_optimal_profile_no_tracer_instance(
        self, mock_safe_log: Mock, mock_env_analysis: Mock
    ) -> None:
        """Test getting optimal profile without tracer instance."""
        mock_env_analysis.return_value = {
            "environment_type": "standard",
            "resource_constraints": {},
            "performance_characteristics": {},
        }

        profile, environment_analysis = EnvironmentProfileManager.get_optimal_profile(
            None
        )

        assert isinstance(profile, EnvironmentProfile)
        assert environment_analysis["environment_type"] == "standard"
        mock_safe_log.assert_called()

    def test_apply_dynamic_adjustments_memory_low(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test dynamic adjustments for low memory environment."""
        environment_analysis = {
            "resource_constraints": {"memory_tier": "low", "cpu_tier": "medium"},
            "performance_characteristics": {"latency_sensitivity": "standard"},
        }

        adjusted_profile = EnvironmentProfileManager._apply_dynamic_adjustments(
            sample_environment_profile, environment_analysis, mock_tracer_instance
        )

        # Low memory should reduce pool sizes
        assert (
            adjusted_profile.pool_connections
            <= sample_environment_profile.pool_connections
        )
        assert adjusted_profile.pool_maxsize <= sample_environment_profile.pool_maxsize
        assert adjusted_profile.name.endswith("(Optimized)")

    def test_apply_dynamic_adjustments_memory_high(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test dynamic adjustments for high memory environment."""
        environment_analysis = {
            "resource_constraints": {"memory_tier": "high", "cpu_tier": "high"},
            "performance_characteristics": {"latency_sensitivity": "standard"},
        }

        adjusted_profile = EnvironmentProfileManager._apply_dynamic_adjustments(
            sample_environment_profile, environment_analysis, mock_tracer_instance
        )

        # High memory should increase pool sizes
        assert (
            adjusted_profile.pool_connections
            >= sample_environment_profile.pool_connections
        )
        assert adjusted_profile.pool_maxsize >= sample_environment_profile.pool_maxsize

    def test_apply_dynamic_adjustments_latency_critical(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test dynamic adjustments for critical latency sensitivity."""
        environment_analysis = {
            "resource_constraints": {"memory_tier": "medium", "cpu_tier": "medium"},
            "performance_characteristics": {"latency_sensitivity": "critical"},
        }

        adjusted_profile = EnvironmentProfileManager._apply_dynamic_adjustments(
            sample_environment_profile, environment_analysis, mock_tracer_instance
        )

        # Critical latency should reduce timeout and retries
        assert adjusted_profile.timeout <= sample_environment_profile.timeout
        assert adjusted_profile.max_retries <= sample_environment_profile.max_retries
        assert (
            adjusted_profile.backoff_factor <= sample_environment_profile.backoff_factor
        )

    def test_apply_dynamic_adjustments_high_concurrency(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test dynamic adjustments for high concurrency pattern."""
        environment_analysis = {
            "resource_constraints": {"memory_tier": "medium", "cpu_tier": "medium"},
            "performance_characteristics": {"concurrency_pattern": "high"},
        }

        adjusted_profile = EnvironmentProfileManager._apply_dynamic_adjustments(
            sample_environment_profile, environment_analysis, mock_tracer_instance
        )

        # High concurrency should increase pool sizes
        assert (
            adjusted_profile.pool_connections
            >= sample_environment_profile.pool_connections
        )
        assert adjusted_profile.pool_maxsize >= sample_environment_profile.pool_maxsize

    def test_apply_dynamic_adjustments_exception_handling(
        self,
        sample_environment_profile: EnvironmentProfile,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test dynamic adjustments exception handling."""
        # Create invalid environment analysis that will cause exception
        environment_analysis = {
            "resource_constraints": {"memory_tier": None},  # Invalid data
            "performance_characteristics": {"latency_sensitivity": None},
        }

        result = EnvironmentProfileManager._apply_dynamic_adjustments(
            sample_environment_profile, environment_analysis, mock_tracer_instance
        )

        # Should return base profile on exception, but it will be modified
        # with name change
        assert result.pool_connections == sample_environment_profile.pool_connections
        assert result.pool_maxsize == sample_environment_profile.pool_maxsize
        # The exception doesn't actually trigger safe_log in this case
        # because the environment_analysis has valid structure

    def test_create_otlp_config_from_profile(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test creating OTLP config from environment profile."""
        config = EnvironmentProfileManager.create_otlp_config_from_profile(
            sample_environment_profile, mock_tracer_instance
        )

        assert isinstance(config, OTLPSessionConfig)
        assert config.pool_connections == sample_environment_profile.pool_connections
        assert config.pool_maxsize == sample_environment_profile.pool_maxsize
        assert config.max_retries == sample_environment_profile.max_retries
        assert config.timeout == sample_environment_profile.timeout
        assert config.backoff_factor == sample_environment_profile.backoff_factor
        assert config.pool_block == sample_environment_profile.pool_block

    def test_create_otlp_config_from_profile_with_overrides(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test creating OTLP config from profile with overrides."""
        overrides = {
            "pool_connections": 25,
            "timeout": 60.0,
            "retry_status_codes": [500, 502, 503],
        }

        config = EnvironmentProfileManager.create_otlp_config_from_profile(
            sample_environment_profile, mock_tracer_instance, **overrides
        )

        assert config.pool_connections == 25
        assert config.timeout == 60.0
        assert config.retry_status_codes == [500, 502, 503]
        # Pool maxsize should be adjusted to match pool_connections due to validator
        assert config.pool_maxsize >= config.pool_connections

    def test_create_otlp_config_from_profile_type_conversion(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test type conversion in OTLP config creation."""
        overrides = {
            "pool_connections": "15",  # String should be converted to int
            "timeout": "45.5",  # String should be converted to float
            "pool_block": "true",  # String should be converted to bool
        }

        config = EnvironmentProfileManager.create_otlp_config_from_profile(
            sample_environment_profile, mock_tracer_instance, **overrides
        )

        assert config.pool_connections == 15
        assert config.timeout == 45.5
        assert config.pool_block is True


class TestGetEnvironmentOptimizedConfig:
    """Test cases for get_environment_optimized_config function."""

    @patch(
        "honeyhive.tracer.processing.otlp_profiles."
        "EnvironmentProfileManager.get_optimal_profile"
    )
    @patch(
        "honeyhive.tracer.processing.otlp_profiles."
        "EnvironmentProfileManager.create_otlp_config_from_profile"
    )
    def test_get_environment_optimized_config_success(
        self,
        mock_create_config: Mock,
        mock_get_profile: Mock,
        mock_tracer_instance: Mock,
        sample_environment_profile: EnvironmentProfile,
    ) -> None:
        """Test successful environment optimized config retrieval."""
        mock_get_profile.return_value = (
            sample_environment_profile,
            {"environment_type": "standard"},
        )
        mock_config = Mock(spec=OTLPSessionConfig)
        mock_create_config.return_value = mock_config

        result = get_environment_optimized_config(mock_tracer_instance)

        assert result == mock_config
        mock_get_profile.assert_called_once_with(mock_tracer_instance)
        mock_create_config.assert_called_once_with(
            sample_environment_profile, mock_tracer_instance
        )

    @patch(
        "honeyhive.tracer.processing.otlp_profiles."
        "EnvironmentProfileManager.get_optimal_profile"
    )
    @patch(
        "honeyhive.tracer.processing.otlp_profiles."
        "EnvironmentProfileManager.create_otlp_config_from_profile"
    )
    def test_get_environment_optimized_config_with_overrides(
        self,
        mock_create_config: Mock,
        mock_get_profile: Mock,
        mock_tracer_instance: Mock,
        sample_environment_profile: EnvironmentProfile,
    ) -> None:
        """Test environment optimized config with overrides."""
        mock_get_profile.return_value = (
            sample_environment_profile,
            {"environment_type": "standard"},
        )
        mock_config = Mock(spec=OTLPSessionConfig)
        mock_create_config.return_value = mock_config

        overrides = {"pool_connections": 20, "timeout": 45.0}

        result = get_environment_optimized_config(mock_tracer_instance, **overrides)

        assert result == mock_config
        mock_create_config.assert_called_once_with(
            sample_environment_profile, mock_tracer_instance, **overrides
        )

    @patch(
        "honeyhive.tracer.processing.otlp_profiles."
        "EnvironmentProfileManager.get_optimal_profile"
    )
    @patch(
        "honeyhive.tracer.processing.otlp_profiles."
        "EnvironmentProfileManager.create_otlp_config_from_profile"
    )
    def test_get_environment_optimized_config_no_tracer(
        self,
        mock_create_config: Mock,
        mock_get_profile: Mock,
        sample_environment_profile: EnvironmentProfile,
    ) -> None:
        """Test environment optimized config without tracer instance."""
        mock_get_profile.return_value = (
            sample_environment_profile,
            {"environment_type": "standard"},
        )
        mock_config = Mock(spec=OTLPSessionConfig)
        mock_create_config.return_value = mock_config

        result = get_environment_optimized_config(None)

        assert result == mock_config
        mock_get_profile.assert_called_once_with(None)
        mock_create_config.assert_called_once_with(sample_environment_profile, None)


class TestEdgeCasesAndErrorHandling:
    """Test cases for edge cases and error handling scenarios."""

    def test_environment_profile_with_none_additional_config(self) -> None:
        """Test EnvironmentProfile with None additional_config."""
        profile = EnvironmentProfile(
            name="Test Profile",
            pool_connections=5,
            pool_maxsize=10,
            max_retries=2,
            timeout=15.0,
            backoff_factor=0.3,
            additional_config=None,
        )

        assert profile.additional_config is None

    def test_environment_profile_with_empty_additional_config(self) -> None:
        """Test EnvironmentProfile with empty additional_config."""
        profile = EnvironmentProfile(
            name="Test Profile",
            pool_connections=5,
            pool_maxsize=10,
            max_retries=2,
            timeout=15.0,
            backoff_factor=0.3,
            additional_config={},
        )

        assert profile.additional_config == {}

    def test_determine_environment_type_empty_inputs(self) -> None:
        """Test _determine_environment_type with empty inputs."""
        result = _determine_environment_type({}, {})
        assert result == "standard"

    def test_determine_environment_type_none_values(self) -> None:
        """Test _determine_environment_type with None values in inputs."""
        container_info = {"k8s.cluster.name": None, "container.runtime": None}
        cloud_info = {"cloud.provider": None, "faas.name": None}

        result = _determine_environment_type(container_info, cloud_info)
        assert result == "standard"

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_resource_constraints_invalid_memory_value(
        self, mock_getenv: Mock
    ) -> None:
        """Test resource constraints analysis with invalid memory value."""
        mock_getenv.return_value = "invalid_number"

        # Should not raise exception, should handle gracefully
        result = _analyze_resource_constraints()

        # Should have analysis error instead of memory_tier
        assert "analysis_error" in result

    def test_apply_dynamic_adjustments_empty_analysis(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test dynamic adjustments with empty environment analysis."""
        environment_analysis: Dict[str, Any] = {
            "resource_constraints": {},
            "performance_characteristics": {},
        }

        result = EnvironmentProfileManager._apply_dynamic_adjustments(
            sample_environment_profile, environment_analysis, mock_tracer_instance
        )

        # Should still return a valid profile
        assert isinstance(result, EnvironmentProfile)
        assert result.name.endswith("(Optimized)")

    def test_apply_dynamic_adjustments_missing_keys(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test dynamic adjustments with missing keys in analysis."""
        environment_analysis: Dict[str, Any] = {}  # Missing required keys

        result = EnvironmentProfileManager._apply_dynamic_adjustments(
            sample_environment_profile, environment_analysis, mock_tracer_instance
        )

        # Should still return a valid profile
        assert isinstance(result, EnvironmentProfile)


class TestComprehensiveCoverage:
    """Test cases to ensure comprehensive coverage of all code paths."""

    def test_environment_profile_all_validation_constraints(self) -> None:
        """Test all validation constraints for EnvironmentProfile."""
        # Test max_retries constraints
        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="Test",
                pool_connections=5,
                pool_maxsize=10,
                max_retries=-1,  # Below minimum
                timeout=15.0,
                backoff_factor=0.3,
            )

        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="Test",
                pool_connections=5,
                pool_maxsize=10,
                max_retries=11,  # Above maximum
                timeout=15.0,
                backoff_factor=0.3,
            )

        # Test backoff_factor constraints
        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="Test",
                pool_connections=5,
                pool_maxsize=10,
                max_retries=3,
                timeout=15.0,
                backoff_factor=-0.1,  # Below minimum
            )

        with pytest.raises(ValidationError):
            EnvironmentProfile(
                name="Test",
                pool_connections=5,
                pool_maxsize=10,
                max_retries=3,
                timeout=15.0,
                backoff_factor=5.1,  # Above maximum
            )

    def test_all_predefined_profiles_valid(self) -> None:
        """Test that all predefined profiles in EnvironmentProfileManager are valid."""
        for profile in EnvironmentProfileManager.PROFILES.values():
            # Verify all profiles are valid EnvironmentProfile instances
            assert isinstance(profile, EnvironmentProfile)
            assert profile.name is not None
            assert len(profile.name) > 0
            assert profile.pool_connections >= 1
            assert profile.pool_maxsize >= profile.pool_connections
            assert profile.max_retries >= 0
            assert profile.timeout > 0
            assert profile.backoff_factor >= 0

            # Verify additional_config structure
            if profile.additional_config is not None:
                assert isinstance(profile.additional_config, dict)

    @patch("honeyhive.tracer.processing.otlp_profiles.os.getenv")
    def test_analyze_performance_characteristics_all_branches(
        self, mock_getenv: Mock
    ) -> None:
        """Test all conditional branches in _analyze_performance_characteristics."""
        # Test all environment types
        environment_types = [
            "aws_lambda",
            "kubernetes",
            "docker",
            "standard",
            "unknown",
        ]

        for env_type in environment_types:
            mock_getenv.side_effect = lambda key, default=None: {
                "HH_HIGH_CONCURRENCY": None,
                "HH_SESSION_NAME": "test-session",
            }.get(key, default)

            result = _analyze_performance_characteristics(env_type)

            # Should always return a dict with some characteristics
            assert isinstance(result, dict)
            if env_type in ["aws_lambda", "kubernetes"]:
                assert "execution_model" in result
            else:
                assert "execution_model" in result
                assert result["execution_model"] == "persistent"

    def test_create_otlp_config_all_override_types(
        self, sample_environment_profile: EnvironmentProfile, mock_tracer_instance: Mock
    ) -> None:
        """Test creating OTLP config with all possible override types."""
        overrides = {
            "pool_connections": 25,
            "pool_maxsize": 50,
            "max_retries": 5,
            "timeout": 60.0,
            "backoff_factor": 1.0,
            "pool_block": True,
            "retry_status_codes": [429, 500, 502, 503, 504],
        }

        config = EnvironmentProfileManager.create_otlp_config_from_profile(
            sample_environment_profile, mock_tracer_instance, **overrides
        )

        assert config.pool_connections == 25
        assert config.pool_maxsize == 50
        assert config.max_retries == 5
        assert config.timeout == 60.0
        assert config.backoff_factor == 1.0
        assert config.pool_block is True
        assert config.retry_status_codes == [429, 500, 502, 503, 504]

"""Unit tests for honeyhive.tracer.infra.resources module.

pylint: disable=R0917,line-too-long  # Test fixtures

This module tests OpenTelemetry resource attribute building and management
functionality with comprehensive mocking of all external dependencies.

Test Coverage:
- build_otel_resources() function with all conditional branches
- _detect_service_name() function with priority detection logic
- _detect_service_version() function with version source detection
- _get_python_version() function with exception handling
- All safe_log conditional calls and exception paths
- Graceful degradation scenarios
"""

# pylint: disable=too-many-arguments,too-many-locals,protected-access
# pylint: disable=redefined-outer-name,too-many-statements,R0917
# pylint: disable=too-many-public-methods,duplicate-code

from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

from honeyhive.tracer.infra.resources import (
    _detect_service_name,
    _detect_service_version,
    _get_python_version,
    build_otel_resources,
)


class TestBuildOtelResources:
    """Test suite for build_otel_resources function."""

    @patch("honeyhive.tracer.infra.resources.EnvironmentDetector")
    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getpid")
    @patch("honeyhive.tracer.infra.resources._get_python_version")
    @patch("honeyhive.tracer.infra.resources._detect_service_name")
    @patch("honeyhive.tracer.infra.resources._detect_service_version")
    def test_build_otel_resources_success_with_tracer(
        self,
        mock_detect_service_version: Mock,
        mock_detect_service_name: Mock,
        mock_get_python_version: Mock,
        mock_getpid: Mock,
        mock_safe_log: Mock,
        mock_environment_detector: Mock,
    ) -> None:
        """Test successful resource building with tracer instance.

        Verifies that all resource attributes are properly collected
        and safe_log is called for success logging.
        """
        # Arrange
        mock_tracer: Mock = Mock()
        mock_tracer_id: int = 12345

        # Mock all function returns
        mock_getpid.return_value = 9876
        mock_get_python_version.return_value = "3.11.5"
        mock_detect_service_name.return_value = "test-service"
        mock_detect_service_version.return_value = "1.0.0"

        # Mock EnvironmentDetector
        mock_detector_instance: Mock = Mock()
        mock_environment_detector.return_value = mock_detector_instance

        mock_detector_instance.detect_system_info.return_value = {
            "os.type": "Linux",
            "host.name": "test-host",
        }
        mock_detector_instance.detect_container_environment.return_value = {
            "container.runtime": "docker"
        }
        mock_detector_instance.detect_cloud_environment.return_value = {
            "cloud.provider": "aws"
        }

        # Mock id() function for tracer instance
        with patch("honeyhive.tracer.infra.resources.id", return_value=mock_tracer_id):
            # Act
            result: Dict[str, Any] = build_otel_resources(mock_tracer)

        # Assert - Verify all expected resource attributes
        expected_keys = {
            "process.pid",
            "process.runtime.name",
            "process.runtime.version",
            "service.name",
            "service.version",
            "service.instance.id",
            "os.type",
            "host.name",
            "container.runtime",
            "cloud.provider",
        }
        assert set(result.keys()) == expected_keys

        # Verify specific values
        assert result["process.pid"] == 9876
        assert result["process.runtime.name"] == "python"
        assert result["process.runtime.version"] == "3.11.5"
        assert result["service.name"] == "test-service"
        assert result["service.version"] == "1.0.0"
        assert result["service.instance.id"] == str(mock_tracer_id)
        assert result["os.type"] == "Linux"
        assert result["host.name"] == "test-host"
        assert result["container.runtime"] == "docker"
        assert result["cloud.provider"] == "aws"

        # Verify EnvironmentDetector was called correctly
        mock_environment_detector.assert_called_once_with(mock_tracer)
        mock_detector_instance.detect_system_info.assert_called_once()
        mock_detector_instance.detect_container_environment.assert_called_once()
        mock_detector_instance.detect_cloud_environment.assert_called_once()

        # Verify helper functions were called
        mock_detect_service_name.assert_called_once_with(mock_tracer)
        mock_detect_service_version.assert_called_once()
        mock_get_python_version.assert_called_once()
        mock_getpid.assert_called_once()

        # Verify success logging was called
        mock_safe_log.assert_called_once_with(
            mock_tracer,
            "debug",
            f"Built {len(result)} OpenTelemetry resource attributes",
        )

    @patch("honeyhive.tracer.infra.resources.EnvironmentDetector")
    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getpid")
    @patch("honeyhive.tracer.infra.resources._get_python_version")
    @patch("honeyhive.tracer.infra.resources._detect_service_name")
    @patch("honeyhive.tracer.infra.resources._detect_service_version")
    def test_build_otel_resources_success_without_tracer(
        self,
        mock_detect_service_version: Mock,
        mock_detect_service_name: Mock,
        mock_get_python_version: Mock,
        mock_getpid: Mock,
        mock_safe_log: Mock,
        mock_environment_detector: Mock,
    ) -> None:
        """Test successful resource building without tracer instance.

        Verifies that resources are built correctly when no tracer
        is provided and no logging occurs.
        """
        # Arrange
        mock_getpid.return_value = 5432
        mock_get_python_version.return_value = "3.12.1"
        mock_detect_service_name.return_value = "unknown-service"
        mock_detect_service_version.return_value = "unknown"

        # Mock EnvironmentDetector
        mock_detector_instance: Mock = Mock()
        mock_environment_detector.return_value = mock_detector_instance

        mock_detector_instance.detect_system_info.return_value = {}
        mock_detector_instance.detect_container_environment.return_value = {}
        mock_detector_instance.detect_cloud_environment.return_value = {}

        # Act
        result: Dict[str, Any] = build_otel_resources(None)

        # Assert - Verify basic resource attributes
        assert result["process.pid"] == 5432
        assert result["process.runtime.name"] == "python"
        assert result["process.runtime.version"] == "3.12.1"
        assert result["service.name"] == "unknown-service"
        assert result["service.version"] == "unknown"
        assert result["service.instance.id"] == "unknown"

        # Verify EnvironmentDetector was called with None
        mock_environment_detector.assert_called_once_with(None)

        # Verify helper functions were called
        mock_detect_service_name.assert_called_once_with(None)
        mock_detect_service_version.assert_called_once()

        # Verify no logging occurred (tracer_instance is None)
        mock_safe_log.assert_not_called()

    @patch("honeyhive.tracer.infra.resources.EnvironmentDetector")
    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getpid")
    def test_build_otel_resources_exception_with_tracer(
        self,
        mock_getpid: Mock,
        mock_safe_log: Mock,
        mock_environment_detector: Mock,
    ) -> None:
        """Test exception handling with tracer instance.

        Verifies that exceptions are caught gracefully and warning
        is logged when tracer instance is available.
        """
        # Arrange
        mock_tracer: Mock = Mock()
        mock_tracer_id: int = 67890
        test_exception = RuntimeError("Environment detection failed")

        # Mock EnvironmentDetector to raise exception
        mock_environment_detector.side_effect = test_exception
        mock_getpid.return_value = 1111

        # Mock id() function for tracer instance
        with patch("honeyhive.tracer.infra.resources.id", return_value=mock_tracer_id):
            # Act
            result: Dict[str, Any] = build_otel_resources(mock_tracer)

        # Assert - Verify graceful degradation
        expected_minimal_resources = {
            "service.name": "unknown",
            "service.instance.id": str(mock_tracer_id),
            "process.pid": 1111,
        }
        assert result == expected_minimal_resources

        # Verify warning was logged
        mock_safe_log.assert_called_once_with(
            mock_tracer, "warning", f"Error during resource detection: {test_exception}"
        )

    @patch("honeyhive.tracer.infra.resources.EnvironmentDetector")
    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getpid")
    def test_build_otel_resources_exception_without_tracer(
        self,
        mock_getpid: Mock,
        mock_safe_log: Mock,
        mock_environment_detector: Mock,
    ) -> None:
        """Test exception handling without tracer instance.

        Verifies that exceptions are caught gracefully and no
        logging occurs when no tracer instance is available.
        """
        # Arrange
        test_exception = ValueError("Mock environment error")

        # Mock EnvironmentDetector to raise exception
        mock_environment_detector.side_effect = test_exception
        mock_getpid.return_value = 2222

        # Act
        result: Dict[str, Any] = build_otel_resources(None)

        # Assert - Verify graceful degradation
        expected_minimal_resources = {
            "service.name": "unknown",
            "service.instance.id": "unknown",
            "process.pid": 2222,
        }
        assert result == expected_minimal_resources

        # Verify no logging occurred (tracer_instance is None)
        mock_safe_log.assert_not_called()


class TestDetectServiceName:
    """Test suite for _detect_service_name function."""

    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_name_otel_service_name_with_tracer(
        self,
        mock_getenv: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test service name detection from OTEL_SERVICE_NAME with tracer.

        Verifies that OTEL_SERVICE_NAME has highest priority and
        detection is logged when tracer is available.
        """
        # Arrange
        mock_tracer: Mock = Mock()
        expected_service_name: str = "otel-test-service"

        # Mock environment variables - OTEL_SERVICE_NAME has highest priority
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            env_vars = {
                "OTEL_SERVICE_NAME": expected_service_name,
                "HH_SERVICE_NAME": "hh-service",
                "SERVICE_NAME": "generic-service",
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_name(mock_tracer)

        # Assert
        assert result == expected_service_name

        # Verify logging occurred
        mock_safe_log.assert_called_once_with(
            mock_tracer, "debug", f"Service name detected: {expected_service_name}"
        )

    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_name_hh_service_name_without_tracer(
        self,
        mock_getenv: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test service name detection from HH_SERVICE_NAME without tracer.

        Verifies that HH_SERVICE_NAME is used when OTEL_SERVICE_NAME
        is not available and no logging occurs without tracer.
        """
        # Arrange
        expected_service_name: str = "honeyhive-test-service"

        # Mock environment variables - only HH_SERVICE_NAME available
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            env_vars = {
                "HH_SERVICE_NAME": expected_service_name,
                "SERVICE_NAME": "generic-service",
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_name(None)

        # Assert
        assert result == expected_service_name

        # Verify no logging occurred (tracer_instance is None)
        mock_safe_log.assert_not_called()

    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_name_from_tracer_project_attribute(
        self,
        mock_getenv: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test service name detection from tracer project attribute.

        Verifies that tracer.project attribute is used when
        environment variables are not available.
        """
        # Arrange
        mock_tracer: Mock = Mock()
        expected_project_name: str = "tracer-project-name"
        mock_tracer.project = expected_project_name

        # Mock environment variables - none available
        mock_getenv.return_value = None

        # Act
        result: str = _detect_service_name(mock_tracer)

        # Assert
        assert result == expected_project_name

        # Verify logging occurred
        mock_safe_log.assert_called_once_with(
            mock_tracer, "debug", f"Service name detected: {expected_project_name}"
        )

    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_name_from_lambda_function(
        self,
        mock_getenv: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test service name detection from AWS Lambda function name.

        Verifies that AWS_LAMBDA_FUNCTION_NAME is used when
        higher priority sources are not available.
        """
        # Arrange
        mock_tracer: Mock = Mock()
        expected_lambda_name: str = "my-lambda-function"
        mock_tracer.project = None  # No project attribute

        # Mock environment variables - only Lambda available
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            env_vars = {
                "AWS_LAMBDA_FUNCTION_NAME": expected_lambda_name,
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_name(mock_tracer)

        # Assert
        assert result == expected_lambda_name

        # Verify logging occurred
        mock_safe_log.assert_called_once_with(
            mock_tracer, "debug", f"Service name detected: {expected_lambda_name}"
        )

    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_name_from_k8s_app_name(
        self,
        mock_getenv: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test service name detection from Kubernetes app name.

        Verifies that K8S_APP_NAME is used when other sources
        are not available.
        """
        # Arrange
        mock_tracer: Mock = Mock()
        expected_k8s_name: str = "k8s-app-service"
        mock_tracer.project = None

        # Mock environment variables - only K8S available
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            env_vars = {
                "K8S_APP_NAME": expected_k8s_name,
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_name(mock_tracer)

        # Assert
        assert result == expected_k8s_name

        # Verify logging occurred
        mock_safe_log.assert_called_once_with(
            mock_tracer, "debug", f"Service name detected: {expected_k8s_name}"
        )

    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_name_default_fallback(
        self,
        mock_getenv: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test service name detection falls back to default.

        Verifies that default service name is returned when
        no sources are available and logging occurs for default.
        """
        # Arrange
        mock_tracer: Mock = Mock()
        mock_tracer.project = None

        # Mock environment variables - none available
        mock_getenv.return_value = None

        # Act
        result: str = _detect_service_name(mock_tracer)

        # Assert
        assert result == "honeyhive-service"

        # Verify logging occurred for the default value (the function logs the default)
        mock_safe_log.assert_called_once_with(
            mock_tracer, "debug", "Service name detected: honeyhive-service"
        )

    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_name_exception_handling(
        self,
        mock_getenv: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test service name detection handles exceptions gracefully.

        Verifies that exceptions during detection are caught
        and default value is returned.
        """
        # Arrange
        mock_tracer: Mock = Mock()
        mock_tracer.project = None  # Ensure project attribute doesn't interfere

        # Mock getenv to raise exception for first few calls, then return None
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            if key in ["OTEL_SERVICE_NAME", "HH_SERVICE_NAME", "SERVICE_NAME"]:
                raise OSError("Environment access error")
            return default

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_name(mock_tracer)

        # Assert - Should return default fallback
        assert result == "honeyhive-service"

        # Verify logging occurred for the default value
        # (the function still logs the default)
        mock_safe_log.assert_called_once_with(
            mock_tracer,
            "debug",
            "Service name detected: honeyhive-service",
        )

    @patch("honeyhive.tracer.infra.resources.safe_log")
    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_name_tracer_project_exception(
        self,
        mock_getenv: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test service name detection handles tracer.project exceptions.

        Verifies that exceptions when accessing tracer.project
        are caught and processing continues to default.
        """
        # Arrange
        mock_tracer: Mock = Mock()
        # Mock environment variables - none available
        mock_getenv.return_value = None

        # Make tracer.project return None (no project set)
        mock_tracer.project = None

        # Act
        result: str = _detect_service_name(mock_tracer)

        # Assert - Should return default fallback
        assert result == "honeyhive-service"

        # Verify logging occurred for the default value (the function logs the default)
        mock_safe_log.assert_called_once_with(
            mock_tracer, "debug", "Service name detected: honeyhive-service"
        )


class TestDetectServiceVersion:
    """Test suite for _detect_service_version function."""

    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_version_otel_service_version(
        self,
        mock_getenv: Mock,
    ) -> None:
        """Test service version detection from OTEL_SERVICE_VERSION.

        Verifies that OTEL_SERVICE_VERSION has highest priority
        for version detection.
        """
        # Arrange
        expected_version: str = "2.1.0"

        # Mock environment variables - OTEL_SERVICE_VERSION has highest priority
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            env_vars = {
                "OTEL_SERVICE_VERSION": expected_version,
                "HH_SERVICE_VERSION": "1.5.0",
                "SERVICE_VERSION": "1.0.0",
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_version()

        # Assert
        assert result == expected_version

    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_version_hh_service_version(
        self,
        mock_getenv: Mock,
    ) -> None:
        """Test service version detection from HH_SERVICE_VERSION.

        Verifies that HH_SERVICE_VERSION is used when
        OTEL_SERVICE_VERSION is not available.
        """
        # Arrange
        expected_version: str = "1.8.2"

        # Mock environment variables - only HH_SERVICE_VERSION available
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            env_vars = {
                "HH_SERVICE_VERSION": expected_version,
                "SERVICE_VERSION": "1.0.0",
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_version()

        # Assert
        assert result == expected_version

    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_version_generic_service_version(
        self,
        mock_getenv: Mock,
    ) -> None:
        """Test service version detection from SERVICE_VERSION.

        Verifies that SERVICE_VERSION is used when HoneyHive-specific
        versions are not available.
        """
        # Arrange
        expected_version: str = "3.0.1"

        # Mock environment variables - only SERVICE_VERSION available
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            env_vars = {
                "SERVICE_VERSION": expected_version,
                "GIT_COMMIT": "abcdef123456",
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_version()

        # Assert
        assert result == expected_version

    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_version_git_commit_truncated(
        self,
        mock_getenv: Mock,
    ) -> None:
        """Test service version detection from GIT_COMMIT (truncated).

        Verifies that GIT_COMMIT is truncated to 8 characters
        when used as version source.
        """
        # Arrange
        full_commit: str = "abcdef1234567890abcdef"
        expected_version: str = "abcdef12"  # First 8 characters

        # Mock environment variables - only GIT_COMMIT available
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            if key == "GIT_COMMIT":
                return full_commit
            return env_vars.get(key, default) if key in env_vars else default

        env_vars: Dict[str, str] = {}
        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_version()

        # Assert
        assert result == expected_version

    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_version_build_number(
        self,
        mock_getenv: Mock,
    ) -> None:
        """Test service version detection from BUILD_NUMBER.

        Verifies that BUILD_NUMBER is used when other version
        sources are not available.
        """
        # Arrange
        expected_version: str = "build-456"

        # Mock environment variables - only BUILD_NUMBER available
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            env_vars = {
                "BUILD_NUMBER": expected_version,
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_version()

        # Assert
        assert result == expected_version

    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_version_default_fallback(
        self,
        mock_getenv: Mock,
    ) -> None:
        """Test service version detection falls back to default.

        Verifies that default version is returned when
        no version sources are available.
        """
        # Arrange
        # Mock environment variables - none available
        mock_getenv.return_value = None

        # Act
        result: str = _detect_service_version()

        # Assert
        assert result == "unknown"

    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_version_exception_handling(
        self,
        mock_getenv: Mock,
    ) -> None:
        """Test service version detection handles exceptions gracefully.

        Verifies that exceptions during detection are caught
        and default value is returned.
        """
        # Arrange
        # Mock getenv to raise exception
        mock_getenv.side_effect = PermissionError("Environment access denied")

        # Act
        result: str = _detect_service_version()

        # Assert - Should return default fallback
        assert result == "unknown"

    @patch("honeyhive.tracer.infra.resources.os.getenv")
    def test_detect_service_version_empty_git_commit(
        self,
        mock_getenv: Mock,
    ) -> None:
        """Test service version detection handles empty GIT_COMMIT.

        Verifies that empty GIT_COMMIT is skipped and
        processing continues to next source.
        """
        # Arrange
        expected_version: str = "build-789"

        # Mock environment variables - empty GIT_COMMIT, BUILD_NUMBER available
        def mock_getenv_side_effect(
            key: str, default: Optional[str] = None
        ) -> Optional[str]:
            env_vars = {
                "GIT_COMMIT": "",  # Empty string
                "BUILD_NUMBER": expected_version,
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = mock_getenv_side_effect

        # Act
        result: str = _detect_service_version()

        # Assert
        assert result == expected_version


class TestGetPythonVersion:
    """Test suite for _get_python_version function."""

    @patch("honeyhive.tracer.infra.resources.sys.version_info")
    def test_get_python_version_success(
        self,
        mock_version_info: Mock,
    ) -> None:
        """Test successful Python version detection.

        Verifies that Python version is correctly formatted
        from sys.version_info components.
        """
        # Arrange
        mock_version_info.major = 3
        mock_version_info.minor = 11
        mock_version_info.micro = 5
        expected_version: str = "3.11.5"

        # Act
        result: str = _get_python_version()

        # Assert
        assert result == expected_version

    @patch("honeyhive.tracer.infra.resources.sys.version_info")
    def test_get_python_version_different_version(
        self,
        mock_version_info: Mock,
    ) -> None:
        """Test Python version detection with different version.

        Verifies that version formatting works correctly
        with different version numbers.
        """
        # Arrange
        mock_version_info.major = 3
        mock_version_info.minor = 12
        mock_version_info.micro = 0
        expected_version: str = "3.12.0"

        # Act
        result: str = _get_python_version()

        # Assert
        assert result == expected_version

    @patch("honeyhive.tracer.infra.resources.sys")
    def test_get_python_version_sys_none_exception(
        self,
        mock_sys: Mock,
    ) -> None:
        """Test Python version detection when sys module is None.

        Verifies that exceptions when sys module is None
        (during shutdown) are handled gracefully.
        """
        # Arrange
        mock_sys.version_info = None

        # Act
        result: str = _get_python_version()

        # Assert - Should return default fallback
        assert result == "unknown"

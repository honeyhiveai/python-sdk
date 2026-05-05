"""Unit tests for honeyhive.tracer.integration.http.

This module contains comprehensive unit tests for HTTP instrumentation functionality,
including dynamic library detection, instrumentation configuration, and method wrapping.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

# pylint: disable=too-many-public-methods
# Justification: Comprehensive test coverage requires many test methods

# pylint: disable=unused-argument
# Justification: Test fixtures from @patch decorators may not always be used

import os
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.integration.http import (
    DummyInstrumentation,
    HTTPInstrumentation,
    _create_instrumentation_instance_dynamically,
    get_http_instrumentation_status,
    instrument_http,
    uninstrument_http,
)


class TestHTTPInstrumentation:
    """Test suite for HTTPInstrumentation class."""

    def test_initialization_with_tracer_instance(self, mock_safe_log: Mock) -> None:
        """Test HTTPInstrumentation initialization with tracer instance."""
        # Arrange
        mock_tracer = Mock()

        # Act
        with patch.object(
            HTTPInstrumentation,
            "_detect_libraries_dynamically",
            return_value={"httpx": True, "requests": True},
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {
                        "httpx": {"enabled": True},
                        "requests": {"enabled": True},
                    },
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Assert
        assert instrumentation.tracer_instance == mock_tracer
        assert instrumentation._is_instrumented is False
        assert isinstance(instrumentation._original_methods, dict)
        assert isinstance(instrumentation._library_availability, dict)
        assert isinstance(instrumentation._instrumentation_config, dict)
        # Production code doesn't log during initialization

    def test_initialization_without_tracer_instance(self, mock_safe_log: Mock) -> None:
        """Test HTTPInstrumentation initialization without tracer instance."""
        # Act
        with patch.object(
            HTTPInstrumentation,
            "_detect_libraries_dynamically",
            return_value={"httpx": False, "requests": False},
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={"enabled": False},
            ):
                instrumentation = HTTPInstrumentation()

        # Assert
        assert instrumentation.tracer_instance is None
        assert instrumentation._is_instrumented is False

    def test_detect_libraries_dynamically_all_available(
        self, mock_safe_log: Mock
    ) -> None:
        """Test dynamic library detection when all libraries are available."""
        # Arrange
        mock_tracer = Mock()

        # Act
        with patch("builtins.__import__") as mock_import:
            mock_import.return_value = Mock()  # Simulate successful import
            instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)
            result = instrumentation._detect_libraries_dynamically()

        # Assert
        assert result["httpx"] is True
        assert result["requests"] is True
        assert result["aiohttp"] is True
        assert result["urllib3"] is True
        # Production code doesn't log during library detection

    def test_detect_libraries_dynamically_none_available(
        self, mock_safe_log: Mock
    ) -> None:
        """Test dynamic library detection when no libraries are available."""
        # Arrange
        mock_tracer = Mock()

        # Act
        with patch("builtins.__import__", side_effect=ImportError("No module")):
            instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)
            result = instrumentation._detect_libraries_dynamically()

        # Assert
        assert result["httpx"] is False
        assert result["requests"] is False
        assert result["aiohttp"] is False
        assert result["urllib3"] is False

    def test_detect_libraries_dynamically_partial_availability(
        self, mock_safe_log: Mock
    ) -> None:
        """Test dynamic library detection with partial library availability."""
        # Arrange
        mock_tracer = Mock()

        def mock_import_side_effect(name: str) -> Mock:
            if name in ["httpx", "requests"]:
                return Mock()
            raise ImportError(f"No module named '{name}'")

        # Act
        with patch("builtins.__import__", side_effect=mock_import_side_effect):
            instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)
            result = instrumentation._detect_libraries_dynamically()

        # Assert
        assert result["httpx"] is True
        assert result["requests"] is True
        assert result["aiohttp"] is False
        assert result["urllib3"] is False
        # Production code doesn't log during library detection

    def test_build_instrumentation_config_dynamically_enabled(
        self, mock_safe_log: Mock
    ) -> None:
        """Test building instrumentation configuration when enabled."""
        # Arrange
        mock_tracer = Mock()

        # Act
        with patch.object(
            HTTPInstrumentation,
            "_detect_libraries_dynamically",
            return_value={"httpx": True, "requests": True},
        ):
            with patch.object(
                HTTPInstrumentation,
                "_is_http_tracing_disabled_dynamically",
                return_value=False,
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)
                result = instrumentation._build_instrumentation_config_dynamically()

        # Assert
        assert result["enabled"] is True
        assert result["libraries"]["httpx"]["enabled"] is True
        assert result["libraries"]["requests"]["enabled"] is True
        assert result["span_attributes"]["http.method"] is True
        assert result["span_attributes"]["http.url"] is True
        assert result["span_attributes"]["http.status_code"] is True
        assert result["span_attributes"]["http.user_agent"] is False
        assert result["error_handling"]["graceful_degradation"] is True

    def test_build_instrumentation_config_dynamically_disabled(
        self, mock_safe_log: Mock
    ) -> None:
        """Test building instrumentation configuration when disabled."""
        # Arrange
        mock_tracer = Mock()

        # Act
        with patch.object(
            HTTPInstrumentation,
            "_detect_libraries_dynamically",
            return_value={"httpx": False, "requests": False},
        ):
            with patch.object(
                HTTPInstrumentation,
                "_is_http_tracing_disabled_dynamically",
                return_value=True,
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)
                result = instrumentation._build_instrumentation_config_dynamically()

        # Assert
        assert result["enabled"] is False
        assert result["libraries"]["httpx"]["enabled"] is False
        assert result["libraries"]["requests"]["enabled"] is False

    @pytest.mark.parametrize(
        "env_var,env_value,expected",
        [
            ("HH_DISABLE_HTTP_TRACING", "true", True),
            ("HH_DISABLE_HTTP_TRACING", "1", True),
            ("HH_DISABLE_HTTP_TRACING", "yes", True),
            ("HH_DISABLE_HTTP_TRACING", "on", True),
            ("HH_DISABLE_HTTP_TRACING", "false", False),
            ("HH_DISABLE_HTTP_TRACING", "0", False),
            ("HONEYHIVE_DISABLE_HTTP_TRACING", "true", True),
            ("DISABLE_HTTP_TRACING", "true", True),
            ("NONEXISTENT_VAR", "true", False),
        ],
    )
    def test_is_http_tracing_disabled_dynamically(
        self, env_var: str, env_value: str, expected: bool, mock_safe_log: Mock
    ) -> None:
        """Test dynamic HTTP tracing disable check with various env variables."""
        # Arrange
        mock_tracer = Mock()

        # Act
        with patch.dict(os.environ, {env_var: env_value}, clear=True):
            with patch.object(
                HTTPInstrumentation, "_detect_libraries_dynamically", return_value={}
            ):
                with patch.object(
                    HTTPInstrumentation,
                    "_build_instrumentation_config_dynamically",
                    return_value={
                        "enabled": True,
                        "libraries": {
                            "httpx": {"enabled": True},
                            "requests": {"enabled": True},
                        },
                    },
                ):
                    instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)
                    result = instrumentation._is_http_tracing_disabled_dynamically()

        # Assert
        assert result == expected

    def test_instrument_already_instrumented(self, mock_safe_log: Mock) -> None:
        """Test instrument method when already instrumented."""
        # Arrange
        mock_tracer = Mock()

        with patch.object(
            HTTPInstrumentation, "_detect_libraries_dynamically", return_value={}
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {
                        "httpx": {"enabled": True},
                        "requests": {"enabled": True},
                    },
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)
                instrumentation._is_instrumented = True

        # Act
        instrumentation.instrument()

        # Assert
        # Production code doesn't log when already instrumented

    def test_instrument_disabled_by_configuration(self, mock_safe_log: Mock) -> None:
        """Test instrument method when disabled by configuration."""
        # Arrange
        mock_tracer = Mock()

        with patch.object(
            HTTPInstrumentation, "_detect_libraries_dynamically", return_value={}
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={"enabled": False},
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Act
        instrumentation.instrument()

        # Assert
        # Production code doesn't log when disabled by configuration

    def test_instrument_successful_execution(self, mock_safe_log: Mock) -> None:
        """Test successful instrument execution."""
        # Arrange
        mock_tracer = Mock()
        mock_results = {"httpx": True, "requests": True}

        with patch.object(
            HTTPInstrumentation,
            "_detect_libraries_dynamically",
            return_value={"httpx": True, "requests": True},
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {
                        "httpx": {"enabled": True},
                        "requests": {"enabled": True},
                    },
                },
            ):
                with patch.object(
                    HTTPInstrumentation,
                    "_execute_instrumentation_dynamically",
                    return_value=mock_results,
                ):
                    instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Act
        instrumentation.instrument()

        # Assert
        assert instrumentation._is_instrumented is True
        # Production code doesn't log during successful instrumentation

    def test_should_instrument_library_dynamically_enabled(
        self, mock_safe_log: Mock
    ) -> None:
        """Test library instrumentation decision when enabled."""
        # Arrange
        mock_tracer = Mock()

        with patch.object(
            HTTPInstrumentation,
            "_detect_libraries_dynamically",
            return_value={"httpx": True},
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {"httpx": {"enabled": True}},
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Act
        result = instrumentation._should_instrument_library_dynamically("httpx")

        # Assert
        assert result is True

    def test_should_instrument_library_dynamically_disabled(
        self, mock_safe_log: Mock
    ) -> None:
        """Test library instrumentation decision when disabled."""
        # Arrange
        mock_tracer = Mock()

        with patch.object(
            HTTPInstrumentation,
            "_detect_libraries_dynamically",
            return_value={"httpx": False},
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {"httpx": {"enabled": False}},
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Act
        result = instrumentation._should_instrument_library_dynamically("httpx")

        # Assert
        assert result is False

    def test_store_original_methods_dynamically_success(
        self, mock_safe_log: Mock
    ) -> None:
        """Test successful original methods storage."""
        # Arrange
        mock_tracer = Mock()
        mock_module = Mock()
        mock_class = Mock()
        mock_method = Mock()

        # Setup mock module structure
        mock_class.request = mock_method
        mock_module.Client = mock_class

        with patch.object(
            HTTPInstrumentation, "_detect_libraries_dynamically", return_value={}
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {
                        "httpx": {"enabled": True},
                        "requests": {"enabled": True},
                    },
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Act
        result = instrumentation._store_original_methods_dynamically(
            mock_module, ["Client"], ["request"]
        )

        # Assert
        assert "Client.request" in result
        assert result["Client.request"] == mock_method

    def test_store_original_methods_dynamically_missing_class(
        self, mock_safe_log: Mock
    ) -> None:
        """Test original methods storage with missing class."""
        # Arrange
        mock_tracer = Mock()
        mock_module = Mock(spec=[])  # Empty spec means no attributes

        with patch.object(
            HTTPInstrumentation, "_detect_libraries_dynamically", return_value={}
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {
                        "httpx": {"enabled": True},
                        "requests": {"enabled": True},
                    },
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Act
        result = instrumentation._store_original_methods_dynamically(
            mock_module, ["Client"], ["request"]
        )

        # Assert
        assert not result

    def test_extract_trace_attributes_dynamically_httpx(
        self, mock_safe_log: Mock
    ) -> None:
        """Test trace attributes extraction for httpx."""
        # Arrange
        mock_tracer = Mock()

        with patch.object(
            HTTPInstrumentation, "_detect_libraries_dynamically", return_value={}
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {
                        "httpx": {"enabled": True},
                        "requests": {"enabled": True},
                    },
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Act
        result = instrumentation._extract_trace_attributes_dynamically(
            "httpx", ("GET", "https://api.example.com"), {}
        )

        # Assert
        assert result["http.method"] == "GET"
        assert result["http.url"] == "https://api.example.com"

    def test_extract_trace_attributes_dynamically_requests(
        self, mock_safe_log: Mock
    ) -> None:
        """Test trace attributes extraction for requests."""
        # Arrange
        mock_tracer = Mock()

        with patch.object(
            HTTPInstrumentation, "_detect_libraries_dynamically", return_value={}
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {
                        "httpx": {"enabled": True},
                        "requests": {"enabled": True},
                    },
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Act
        result = instrumentation._extract_trace_attributes_dynamically(
            "requests", ("POST", "https://api.example.com/data"), {}
        )

        # Assert
        assert result["http.method"] == "POST"
        assert result["http.url"] == "https://api.example.com/data"

    def test_extract_trace_attributes_dynamically_unknown_library(
        self, mock_safe_log: Mock
    ) -> None:
        """Test trace attributes extraction for unknown library."""
        # Arrange
        mock_tracer = Mock()

        with patch.object(
            HTTPInstrumentation, "_detect_libraries_dynamically", return_value={}
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {
                        "httpx": {"enabled": True},
                        "requests": {"enabled": True},
                    },
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)

        # Act
        result = instrumentation._extract_trace_attributes_dynamically(
            "unknown", ("GET", "https://api.example.com"), {}
        )

        # Assert
        assert not result

    def test_uninstrument_not_instrumented(self, mock_safe_log: Mock) -> None:
        """Test uninstrument when not instrumented."""
        # Arrange
        mock_tracer = Mock()

        with patch.object(
            HTTPInstrumentation, "_detect_libraries_dynamically", return_value={}
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value={
                    "enabled": True,
                    "libraries": {
                        "httpx": {"enabled": True},
                        "requests": {"enabled": True},
                    },
                },
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)
                instrumentation._is_instrumented = False

        # Act
        instrumentation.uninstrument()

        # Assert
        # Production code doesn't log when not instrumented

    def test_get_instrumentation_status(self, mock_safe_log: Mock) -> None:
        """Test instrumentation status retrieval."""
        # Arrange
        mock_tracer = Mock()
        library_availability = {"httpx": True, "requests": False}
        instrumentation_config = {"enabled": True, "libraries": {}}
        original_methods = {"httpx": {"Client.request": Mock()}}

        with patch.object(
            HTTPInstrumentation,
            "_detect_libraries_dynamically",
            return_value=library_availability,
        ):
            with patch.object(
                HTTPInstrumentation,
                "_build_instrumentation_config_dynamically",
                return_value=instrumentation_config,
            ):
                instrumentation = HTTPInstrumentation(tracer_instance=mock_tracer)
                instrumentation._is_instrumented = True
                instrumentation._original_methods = original_methods

        # Act
        result = instrumentation.get_instrumentation_status()

        # Assert
        assert result["is_instrumented"] is True
        assert result["enabled"] is True
        assert result["library_availability"] == library_availability
        assert result["instrumented_libraries"] == ["httpx"]
        assert result["configuration"] == instrumentation_config


class TestDummyInstrumentation:
    """Test suite for DummyInstrumentation class."""

    def test_initialization(self, mock_safe_log: Mock) -> None:
        """Test DummyInstrumentation initialization."""
        # Arrange
        mock_tracer = Mock()

        # Act
        dummy = DummyInstrumentation(tracer_instance=mock_tracer)

        # Assert
        assert dummy.tracer_instance == mock_tracer

    def test_initialization_without_tracer(self, mock_safe_log: Mock) -> None:
        """Test DummyInstrumentation initialization without tracer."""
        # Act
        dummy = DummyInstrumentation()

        # Assert
        assert dummy.tracer_instance is None

    def test_instrument_no_op(self, mock_safe_log: Mock) -> None:
        """Test dummy instrument method is no-op."""
        # Arrange
        mock_tracer = Mock()
        dummy = DummyInstrumentation(tracer_instance=mock_tracer)

        # Act
        dummy.instrument()

        # Assert
        # Production code doesn't log for dummy implementation

    def test_uninstrument_no_op(self, mock_safe_log: Mock) -> None:
        """Test dummy uninstrument method is no-op."""
        # Arrange
        dummy = DummyInstrumentation()

        # Act
        dummy.uninstrument()

        # Assert - Should not raise any exception

    def test_get_instrumentation_status_dummy(self, mock_safe_log: Mock) -> None:
        """Test dummy instrumentation status."""
        # Arrange
        dummy = DummyInstrumentation()

        # Act
        result = dummy.get_instrumentation_status()

        # Assert
        assert result["is_instrumented"] is False
        assert result["enabled"] is False
        assert not result["library_availability"]
        assert not result["instrumented_libraries"]
        assert result["configuration"] == {"enabled": False}


class TestGlobalFunctions:
    """Test suite for global instrumentation functions."""

    def test_create_instrumentation_instance_dynamically_enabled(
        self, mock_safe_log: Mock
    ) -> None:
        """Test dynamic instrumentation instance creation when enabled."""
        # Act
        with patch.dict(os.environ, {}, clear=True):
            result = _create_instrumentation_instance_dynamically()

        # Assert
        assert isinstance(result, HTTPInstrumentation)

    @pytest.mark.parametrize(
        "env_var,env_value",
        [
            ("HH_DISABLE_HTTP_TRACING", "true"),
            ("HONEYHIVE_DISABLE_HTTP_TRACING", "1"),
            ("DISABLE_HTTP_TRACING", "yes"),
        ],
    )
    def test_create_instrumentation_instance_dynamically_disabled(
        self, env_var: str, env_value: str, mock_safe_log: Mock
    ) -> None:
        """Test dynamic instrumentation instance creation when disabled."""
        # Act
        with patch.dict(os.environ, {env_var: env_value}, clear=True):
            result = _create_instrumentation_instance_dynamically()

        # Assert
        assert isinstance(result, DummyInstrumentation)

    def test_instrument_http_global_function(self, mock_safe_log: Mock) -> None:
        """Test global instrument_http function."""
        # Arrange
        mock_instrumentation = Mock()

        # Act
        with patch(
            "honeyhive.tracer.integration.http._instrumentation", mock_instrumentation
        ):
            instrument_http()

        # Assert
        mock_instrumentation.instrument.assert_called_once()

    def test_uninstrument_http_global_function(self, mock_safe_log: Mock) -> None:
        """Test global uninstrument_http function."""
        # Arrange
        mock_instrumentation = Mock()

        # Act
        with patch(
            "honeyhive.tracer.integration.http._instrumentation", mock_instrumentation
        ):
            uninstrument_http()

        # Assert
        mock_instrumentation.uninstrument.assert_called_once()

    def test_get_http_instrumentation_status_global_function(
        self, mock_safe_log: Mock
    ) -> None:
        """Test global get_http_instrumentation_status function."""
        # Arrange
        mock_instrumentation = Mock()
        expected_status = {"is_instrumented": True, "enabled": True}
        mock_instrumentation.get_instrumentation_status.return_value = expected_status

        # Act
        with patch(
            "honeyhive.tracer.integration.http._instrumentation", mock_instrumentation
        ):
            result = get_http_instrumentation_status()

        # Assert
        assert result == expected_status
        mock_instrumentation.get_instrumentation_status.assert_called_once()

    def test_get_http_instrumentation_status_none_result(
        self, mock_safe_log: Mock
    ) -> None:
        """Test global get_http_instrumentation_status function with None result."""
        # Arrange
        mock_instrumentation = Mock()
        mock_instrumentation.get_instrumentation_status.return_value = None

        # Act
        with patch(
            "honeyhive.tracer.integration.http._instrumentation", mock_instrumentation
        ):
            result = get_http_instrumentation_status()

        # Assert
        assert not result

"""Unit tests for honeyhive.tracer.core.config_interface.

This module contains comprehensive unit tests for TracerConfigInterface,
a clean interface for accessing tracer configuration values with dynamic
resolution from multiple sources including config objects, environment
variables, and tracer defaults.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.core.config_interface import (
    CommonConfigKeys,
    TracerConfigInterface,
)

# pylint: disable=too-many-public-methods
# Justification: Comprehensive unit test coverage requires extensive test methods


class TestTracerConfigInterface:
    """Test suite for TracerConfigInterface class."""

    def test_initialization(self) -> None:
        """Test TracerConfigInterface initialization."""
        # Arrange
        mock_tracer = Mock()

        # Act
        config_interface = TracerConfigInterface(mock_tracer)

        # Assert
        assert config_interface._tracer is mock_tracer

    def test_getattr_with_direct_config_access(self) -> None:
        """Test __getattr__ with direct config access."""
        # Arrange
        mock_tracer = Mock()
        mock_config = Mock()
        mock_config.api_key = "test-api-key"
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_is_default_value", return_value=False):
            # Act
            result = config_interface.api_key

            # Assert
            assert result == "test-api-key"

    def test_getattr_with_attribute_error(self) -> None:
        """Test __getattr__ raises AttributeError when key not found."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_resolve_config_value", return_value=None):
            # Act & Assert
            with pytest.raises(
                AttributeError, match="Configuration key 'nonexistent' not found"
            ):
                _ = config_interface.nonexistent

    def test_resolve_config_value_direct_config_priority(self) -> None:
        """Test _resolve_config_value prioritizes direct config access."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(
            config_interface, "_try_direct_config_access", return_value="direct_value"
        ):
            # Act
            result = config_interface._resolve_config_value("test_key")

            # Assert
            assert result == "direct_value"

    def test_resolve_config_value_nested_config_fallback(self) -> None:
        """Test _resolve_config_value falls back to nested config access."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with (
            patch.object(
                config_interface, "_try_direct_config_access", return_value=None
            ),
            patch.object(
                config_interface,
                "_try_nested_config_access",
                return_value="nested_value",
            ),
        ):
            # Act
            result = config_interface._resolve_config_value("test_key")

            # Assert
            assert result == "nested_value"

    def test_resolve_config_value_environment_variable_fallback(self) -> None:
        """Test _resolve_config_value falls back to environment variables."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with (
            patch.object(
                config_interface, "_try_direct_config_access", return_value=None
            ),
            patch.object(
                config_interface, "_try_nested_config_access", return_value=None
            ),
            patch.object(
                config_interface,
                "_try_environment_variable_access",
                return_value="env_value",
            ),
        ):
            # Act
            result = config_interface._resolve_config_value("test_key")

            # Assert
            assert result == "env_value"

    def test_resolve_config_value_tracer_attribute_fallback(self) -> None:
        """Test _resolve_config_value falls back to tracer attributes."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with (
            patch.object(
                config_interface, "_try_direct_config_access", return_value=None
            ),
            patch.object(
                config_interface, "_try_nested_config_access", return_value=None
            ),
            patch.object(
                config_interface, "_try_environment_variable_access", return_value=None
            ),
            patch.object(
                config_interface,
                "_try_tracer_attribute_access",
                return_value="tracer_value",
            ),
        ):
            # Act
            result = config_interface._resolve_config_value("test_key")

            # Assert
            assert result == "tracer_value"

    def test_resolve_config_value_returns_none_when_not_found(self) -> None:
        """Test _resolve_config_value returns None when value not found."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with (
            patch.object(
                config_interface, "_try_direct_config_access", return_value=None
            ),
            patch.object(
                config_interface, "_try_nested_config_access", return_value=None
            ),
            patch.object(
                config_interface, "_try_environment_variable_access", return_value=None
            ),
            patch.object(
                config_interface, "_try_tracer_attribute_access", return_value=None
            ),
        ):
            # Act
            result = config_interface._resolve_config_value("test_key")

            # Assert
            assert result is None

    def test_try_direct_config_access_no_merged_config(self) -> None:
        """Test _try_direct_config_access returns None when no merged config."""
        # Arrange
        mock_tracer = Mock()
        if hasattr(mock_tracer, "_merged_config"):
            del mock_tracer._merged_config  # Ensure attribute doesn't exist
        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._try_direct_config_access("test_key")

        # Assert
        assert result is None

    def test_try_direct_config_access_with_attribute(self) -> None:
        """Test _try_direct_config_access with config attribute."""
        # Arrange
        mock_tracer = Mock()
        mock_config = Mock()
        mock_config.api_key = "test-api-key"
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_is_default_value", return_value=False):
            # Act
            result = config_interface._try_direct_config_access("api_key")

            # Assert
            assert result == "test-api-key"

    def test_try_direct_config_access_with_dict_key(self) -> None:
        """Test _try_direct_config_access with dictionary key."""
        # Arrange
        mock_tracer = Mock()
        mock_config = {"project": "test-project"}
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_is_default_value", return_value=False):
            # Act
            result = config_interface._try_direct_config_access("project")

            # Assert
            assert result == "test-project"

    def test_try_direct_config_access_skips_default_values(self) -> None:
        """Test _try_direct_config_access skips default values."""
        # Arrange
        mock_tracer = Mock()
        mock_config = Mock()
        mock_config.source = "dev"  # This is a default value
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_is_default_value", return_value=True):
            # Act
            result = config_interface._try_direct_config_access("source")

            # Assert
            assert result is None

    def test_is_default_value_known_defaults(self) -> None:
        """Test _is_default_value identifies known default values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._is_default_value("source", "dev") is True
        assert (
            config_interface._is_default_value("server_url", "https://api.honeyhive.ai")
            is True
        )
        assert config_interface._is_default_value("session_name", "unknown") is True
        assert config_interface._is_default_value("disable_http_tracing", True) is True
        assert config_interface._is_default_value("verbose", False) is True
        assert config_interface._is_default_value("api_key", None) is True

    def test_is_default_value_dynamic_detection(self) -> None:
        """Test _is_default_value dynamic default detection."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._is_default_value("unknown_key", None) is True
        assert config_interface._is_default_value("unknown_flag", False) is True
        assert config_interface._is_default_value("unknown_string", "dev") is True
        assert config_interface._is_default_value("unknown_string", "default") is True
        assert config_interface._is_default_value("unknown_string", "unknown") is True

    def test_is_default_value_non_defaults(self) -> None:
        """Test _is_default_value correctly identifies non-default values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._is_default_value("source", "production") is False
        assert (
            config_interface._is_default_value("server_url", "https://custom.api.com")
            is False
        )
        assert (
            config_interface._is_default_value("session_name", "custom-session")
            is False
        )
        assert (
            config_interface._is_default_value("disable_http_tracing", False) is False
        )
        assert config_interface._is_default_value("verbose", True) is False
        assert config_interface._is_default_value("api_key", "real-api-key") is False

    def test_try_nested_config_access_no_merged_config(self) -> None:
        """Test _try_nested_config_access returns None when no merged config."""
        # Arrange
        mock_tracer = Mock()
        if hasattr(mock_tracer, "_merged_config"):
            del mock_tracer._merged_config  # Ensure attribute doesn't exist
        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._try_nested_config_access("test_key")

        # Assert
        assert result is None

    def test_try_nested_config_access_dict_traversal(self) -> None:
        """Test _try_nested_config_access with dictionary traversal."""
        # Arrange
        mock_tracer = Mock()
        nested_config = Mock()
        nested_config.batch_size = 100
        mock_config = {"otlp": nested_config}
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._try_nested_config_access("batch_size")

        # Assert
        assert result == 100

    def test_try_nested_config_access_nested_dict(self) -> None:
        """Test _try_nested_config_access with nested dictionary."""
        # Arrange
        mock_tracer = Mock()
        mock_config = {"http": {"timeout": 30.0}}
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._try_nested_config_access("timeout")

        # Assert
        assert result == 30.0

    def test_try_nested_config_access_pydantic_model(self) -> None:
        """Test _try_nested_config_access with Pydantic model attributes."""
        # Arrange
        mock_tracer = Mock()
        mock_config = Mock()
        mock_nested = Mock()
        mock_nested.flush_interval = 5.0
        mock_config.otlp_config = mock_nested
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._try_nested_config_access("flush_interval")

        # Assert
        assert result == 5.0

    @patch("os.getenv")
    def test_try_environment_variable_access_hh_prefix(self, mock_getenv: Mock) -> None:
        """Test _try_environment_variable_access with HH_ prefix."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)
        mock_getenv.return_value = "env-api-key"

        with (
            patch.object(
                config_interface, "_convert_env_value", return_value="env-api-key"
            ),
            patch.object(config_interface, "_get_sensible_default", return_value=None),
        ):
            # Act
            result = config_interface._try_environment_variable_access("api_key")

            # Assert
            assert result == "env-api-key"
            mock_getenv.assert_called_with("HH_API_KEY")

    @patch("os.getenv")
    def test_try_environment_variable_access_honeyhive_prefix(
        self, mock_getenv: Mock
    ) -> None:
        """Test _try_environment_variable_access with HONEYHIVE_ prefix."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)
        mock_getenv.side_effect = lambda key: (
            "honeyhive-api-key" if key == "HONEYHIVE_API_KEY" else None
        )

        with (
            patch.object(
                config_interface, "_convert_env_value", return_value="honeyhive-api-key"
            ),
            patch.object(config_interface, "_get_sensible_default", return_value=None),
        ):
            # Act
            result = config_interface._try_environment_variable_access("api_key")

            # Assert
            assert result == "honeyhive-api-key"

    @patch("os.getenv")
    def test_try_environment_variable_access_fallback_to_default(
        self, mock_getenv: Mock
    ) -> None:
        """Test _try_environment_variable_access falls back to sensible default."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)
        mock_getenv.return_value = None

        with patch.object(
            config_interface, "_get_sensible_default", return_value="default-value"
        ):
            # Act
            result = config_interface._try_environment_variable_access("unknown_key")

            # Assert
            assert result == "default-value"

    def test_convert_env_value_boolean_detection(self) -> None:
        """Test _convert_env_value detects boolean values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(
            config_interface, "_convert_boolean_value", return_value=True
        ):
            # Act
            result = config_interface._convert_env_value("enabled", "true")

            # Assert
            assert result is True

    def test_convert_env_value_numeric_detection(self) -> None:
        """Test _convert_env_value detects numeric values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_convert_int_value", return_value=100):
            # Act
            result = config_interface._convert_env_value("batch_size", "100")

            # Assert
            assert result == 100

    def test_convert_env_value_float_detection(self) -> None:
        """Test _convert_env_value detects float values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_convert_float_value", return_value=5.0):
            # Act
            result = config_interface._convert_env_value("timeout", "5.0")

            # Assert
            assert result == 5.0

    def test_convert_env_value_format_based_conversion(self) -> None:
        """Test _convert_env_value uses format-based conversion."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(
            config_interface, "_convert_by_format", return_value="formatted_value"
        ):
            # Act
            result = config_interface._convert_env_value("custom_key", "some_value")

            # Assert
            assert result == "formatted_value"

    def test_convert_boolean_value_valid_true_values(self) -> None:
        """Test _convert_boolean_value handles valid true values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_boolean_value("true") is True
        assert config_interface._convert_boolean_value("1") is True
        assert config_interface._convert_boolean_value("yes") is True
        assert config_interface._convert_boolean_value("on") is True
        assert config_interface._convert_boolean_value("enabled") is True
        assert (
            config_interface._convert_boolean_value("TRUE") is True
        )  # Case insensitive

    def test_convert_boolean_value_valid_false_values(self) -> None:
        """Test _convert_boolean_value handles valid false values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_boolean_value("false") is False
        assert config_interface._convert_boolean_value("0") is False
        assert config_interface._convert_boolean_value("no") is False
        assert config_interface._convert_boolean_value("off") is False
        assert config_interface._convert_boolean_value("disabled") is False
        assert (
            config_interface._convert_boolean_value("FALSE") is False
        )  # Case insensitive

    def test_convert_boolean_value_invalid_values(self) -> None:
        """Test _convert_boolean_value returns None for invalid values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_boolean_value("invalid") is None
        assert config_interface._convert_boolean_value("maybe") is None
        assert config_interface._convert_boolean_value("2") is None

    def test_convert_int_value_valid_integers(self) -> None:
        """Test _convert_int_value handles valid integers."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_int_value("100") == 100
        assert config_interface._convert_int_value("0") == 0
        assert config_interface._convert_int_value("-50") == -50

    def test_convert_int_value_invalid_values(self) -> None:
        """Test _convert_int_value returns None for invalid values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_int_value("not_a_number") is None
        assert config_interface._convert_int_value("12.5") is None
        assert config_interface._convert_int_value("") is None

    def test_convert_float_value_valid_floats(self) -> None:
        """Test _convert_float_value handles valid floats."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_float_value("5.0") == 5.0
        assert config_interface._convert_float_value("0.5") == 0.5
        assert config_interface._convert_float_value("-2.5") == -2.5
        assert config_interface._convert_float_value("100") == 100.0  # Integer as float

    def test_convert_float_value_invalid_values(self) -> None:
        """Test _convert_float_value returns None for invalid values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_float_value("not_a_number") is None
        assert config_interface._convert_float_value("") is None

    def test_convert_by_format_integer_detection(self) -> None:
        """Test _convert_by_format detects integers."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_by_format("123") == 123
        assert config_interface._convert_by_format("-456") == -456

    def test_convert_by_format_float_detection(self) -> None:
        """Test _convert_by_format detects floats."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_by_format("12.5") == 12.5
        assert config_interface._convert_by_format("-3.14") == -3.14

    def test_convert_by_format_boolean_detection(self) -> None:
        """Test _convert_by_format detects booleans."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_by_format("true") is True
        assert config_interface._convert_by_format("false") is False
        # Note: "1" and "0" are detected as integers first, so they return int values
        assert config_interface._convert_by_format("1") == 1  # Integer, not boolean
        assert config_interface._convert_by_format("0") == 0  # Integer, not boolean
        assert config_interface._convert_by_format("yes") is True
        assert config_interface._convert_by_format("no") is False

    def test_convert_by_format_string_fallback(self) -> None:
        """Test _convert_by_format falls back to string."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._convert_by_format("custom_string") == "custom_string"
        assert config_interface._convert_by_format("mixed123text") == "mixed123text"

    def test_get_sensible_default_known_keys(self) -> None:
        """Test _get_sensible_default returns known defaults."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._get_sensible_default("api_key") is None
        assert (
            config_interface._get_sensible_default("server_url")
            == "https://api.honeyhive.ai"
        )
        assert config_interface._get_sensible_default("project") is None
        assert config_interface._get_sensible_default("source") == "dev"
        assert config_interface._get_sensible_default("disable_tracing") is False
        assert config_interface._get_sensible_default("batch_size") == 100
        assert config_interface._get_sensible_default("flush_interval") == 5.0

    def test_get_sensible_default_dynamic_inference(self) -> None:
        """Test _get_sensible_default uses dynamic inference."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        # Boolean flags - "enabled" in name should return True
        assert config_interface._get_sensible_default("custom_enabled") is True
        # "disabled" in name should return False (not enabled)
        assert config_interface._get_sensible_default("custom_disabled") is False
        # "is_" prefix should return False (no "enabled" in name)
        assert config_interface._get_sensible_default("is_custom") is False
        # "has_" prefix should return False (no "enabled" in name)
        assert config_interface._get_sensible_default("has_custom") is False

        # Size/count/limit values
        assert config_interface._get_sensible_default("custom_size") == 100
        assert config_interface._get_sensible_default("custom_count") == 100
        assert config_interface._get_sensible_default("custom_limit") == 100
        assert config_interface._get_sensible_default("custom_max") == 100

        # Time intervals
        assert config_interface._get_sensible_default("custom_interval") == 5.0
        assert config_interface._get_sensible_default("custom_timeout") == 5.0
        assert config_interface._get_sensible_default("custom_delay") == 5.0

        # URLs/endpoints and IDs/names
        assert config_interface._get_sensible_default("custom_url") is None
        assert config_interface._get_sensible_default("custom_endpoint") is None
        assert config_interface._get_sensible_default("custom_id") is None
        assert config_interface._get_sensible_default("custom_name") is None

        # Default fallback
        assert config_interface._get_sensible_default("unknown_key") is None

    def test_try_tracer_attribute_access_existing_attribute(self) -> None:
        """Test _try_tracer_attribute_access with existing attribute."""
        # Arrange
        mock_tracer = Mock()
        mock_tracer.project_name = "test-project"
        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._try_tracer_attribute_access("project_name")

        # Assert
        assert result == "test-project"

    def test_try_tracer_attribute_access_nonexistent_attribute(self) -> None:
        """Test _try_tracer_attribute_access with nonexistent attribute."""
        # Arrange
        mock_tracer = Mock()
        if hasattr(mock_tracer, "nonexistent_attr"):
            del mock_tracer.nonexistent_attr  # Ensure attribute doesn't exist
        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._try_tracer_attribute_access("nonexistent_attr")

        # Assert
        assert result is None

    def test_get_method_success(self) -> None:
        """Test get method returns value successfully."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(
            config_interface, "_resolve_config_value", return_value="test_value"
        ):
            # Act
            result = config_interface.get("test_key")

            # Assert
            assert result == "test_value"

    def test_get_method_with_default(self) -> None:
        """Test get method returns default when key not found."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_resolve_config_value", return_value=None):
            # Act
            result = config_interface.get("nonexistent_key", "default_value")

            # Assert
            assert result == "default_value"

    def test_get_method_no_default(self) -> None:
        """Test get method returns None when key not found and no default."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_resolve_config_value", return_value=None):
            # Act
            result = config_interface.get("nonexistent_key")

            # Assert
            assert result is None

    def test_contains_method_key_exists(self) -> None:
        """Test __contains__ returns True when key exists."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "__getattr__", return_value="test_value"):
            # Act
            result = "test_key" in config_interface

            # Assert
            assert result is True

    def test_contains_method_key_not_exists(self) -> None:
        """Test __contains__ returns False when key doesn't exist."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "__getattr__", side_effect=AttributeError):
            # Act
            result = "nonexistent_key" in config_interface

            # Assert
            assert result is False

    def test_getitem_method_success(self) -> None:
        """Test __getitem__ returns value successfully."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "__getattr__", return_value="test_value"):
            # Act
            result = config_interface["test_key"]

            # Assert
            assert result == "test_value"

    def test_getitem_method_key_error(self) -> None:
        """Test __getitem__ raises KeyError when key not found."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "__getattr__", side_effect=AttributeError):
            # Act & Assert
            with pytest.raises(
                KeyError, match="Configuration key 'nonexistent_key' not found"
            ):
                _ = config_interface["nonexistent_key"]

    def test_to_dict_method(self) -> None:
        """Test to_dict method combines merged config and tracer attributes."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        merged_config_data = {"api_key": "test-key", "project": "test-project"}
        tracer_attributes_data = {"session_id": "test-session", "verbose": True}

        with (
            patch.object(
                config_interface,
                "_extract_merged_config",
                return_value=merged_config_data,
            ),
            patch.object(
                config_interface,
                "_extract_tracer_attributes",
                return_value=tracer_attributes_data,
            ),
        ):
            # Act
            result = config_interface.to_dict()

            # Assert
            expected = {**merged_config_data, **tracer_attributes_data}
            assert result == expected

    def test_extract_merged_config_no_merged_config(self) -> None:
        """Test _extract_merged_config returns empty dict when no merged config."""
        # Arrange
        mock_tracer = Mock()
        if hasattr(mock_tracer, "_merged_config"):
            del mock_tracer._merged_config  # Ensure attribute doesn't exist
        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._extract_merged_config()

        # Assert
        assert not result

    def test_extract_merged_config_pydantic_model(self) -> None:
        """Test _extract_merged_config with Pydantic model."""
        # Arrange
        mock_tracer = Mock()
        mock_config = Mock()
        mock_config.model_dump.return_value = {
            "api_key": "test-key",
            "project": "test-project",
        }
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._extract_merged_config()

        # Assert
        assert result == {"api_key": "test-key", "project": "test-project"}
        mock_config.model_dump.assert_called_once()

    def test_extract_merged_config_object_attributes(self) -> None:
        """Test _extract_merged_config with object attributes."""
        # Arrange
        mock_tracer = Mock()
        mock_config = Mock()
        mock_config.api_key = "test-key"
        mock_config.project = "test-project"
        if hasattr(mock_config, "model_dump"):
            del mock_config.model_dump  # Ensure method doesn't exist
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._extract_merged_config()

        # Assert
        assert "api_key" in result
        assert "project" in result

    def test_extract_merged_config_dictionary(self) -> None:
        """Test _extract_merged_config with dictionary."""
        # Arrange
        mock_tracer = Mock()
        mock_config = {"api_key": "test-key", "project": "test-project"}
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        # Act
        result = config_interface._extract_merged_config()

        # Assert
        assert result == {"api_key": "test-key", "project": "test-project"}

    def test_extract_tracer_attributes(self) -> None:
        """Test _extract_tracer_attributes extracts config-like attributes."""
        # Arrange
        mock_tracer = Mock()
        mock_tracer.api_key = "test-key"
        mock_tracer.project = "test-project"
        mock_tracer.session_id = "test-session"
        mock_tracer.non_config_attr = "should_not_be_included"

        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(
            config_interface,
            "_is_config_like_attribute",
            side_effect=lambda attr: attr in ["api_key", "project", "session_id"],
        ):
            # Act
            result = config_interface._extract_tracer_attributes()

            # Assert
            assert "api_key" in result
            assert "project" in result
            assert "session_id" in result
            assert "non_config_attr" not in result

    def test_is_config_like_attribute_matches_patterns(self) -> None:
        """Test _is_config_like_attribute matches configuration patterns."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._is_config_like_attribute("api_key") is True
        assert config_interface._is_config_like_attribute("project") is True
        assert config_interface._is_config_like_attribute("session_name") is True
        assert config_interface._is_config_like_attribute("endpoint_url") is True
        assert config_interface._is_config_like_attribute("timeout_enabled") is True
        assert config_interface._is_config_like_attribute("batch_size") is True
        assert config_interface._is_config_like_attribute("flush_interval") is True
        assert config_interface._is_config_like_attribute("otlp_config") is True
        assert config_interface._is_config_like_attribute("http_client") is True

    def test_is_config_like_attribute_rejects_non_config(self) -> None:
        """Test _is_config_like_attribute rejects non-configuration attributes."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._is_config_like_attribute("random_method") is False
        assert config_interface._is_config_like_attribute("process_data") is False
        assert config_interface._is_config_like_attribute("calculate_result") is False

    def test_repr_method_success(self) -> None:
        """Test __repr__ method returns formatted string."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        config_dict = {"api_key": "test-key", "project": "test-project"}
        sanitized_dict = {"api_key": "***", "project": "test-project"}

        with (
            patch.object(config_interface, "to_dict", return_value=config_dict),
            patch.object(
                config_interface, "_sanitize_config_dict", return_value=sanitized_dict
            ),
        ):
            # Act
            result = repr(config_interface)

            # Assert
            assert (
                result == "TracerConfig({'api_key': '***', 'project': 'test-project'})"
            )

    def test_repr_method_exception_handling(self) -> None:
        """Test __repr__ method handles exceptions gracefully."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(
            config_interface, "to_dict", side_effect=Exception("Test error")
        ):
            # Act
            result = repr(config_interface)

            # Assert
            assert result == "TracerConfig(<error accessing config>)"

    def test_sanitize_config_dict(self) -> None:
        """Test _sanitize_config_dict sanitizes sensitive values."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        config_dict = {
            "api_key": "secret-key",
            "token": "secret-token",
            "password": "secret-password",
            "project": "test-project",
            "session_id": "test-session",
        }

        with patch.object(
            config_interface,
            "_is_sensitive_key",
            side_effect=lambda key: key in ["api_key", "token", "password"],
        ):
            # Act
            result = config_interface._sanitize_config_dict(config_dict)

            # Assert
            assert result["api_key"] == "***"
            assert result["token"] == "***"
            assert result["password"] == "***"
            assert result["project"] == "test-project"
            assert result["session_id"] == "test-session"

    def test_sanitize_config_dict_none_values(self) -> None:
        """Test _sanitize_config_dict handles None values for sensitive keys."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        config_dict = {"api_key": None, "project": "test-project"}

        with patch.object(
            config_interface,
            "_is_sensitive_key",
            side_effect=lambda key: key == "api_key",
        ):
            # Act
            result = config_interface._sanitize_config_dict(config_dict)

            # Assert
            assert result["api_key"] is None
            assert result["project"] == "test-project"

    def test_is_sensitive_key_detects_sensitive_patterns(self) -> None:
        """Test _is_sensitive_key detects sensitive data patterns."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._is_sensitive_key("api_key") is True
        assert config_interface._is_sensitive_key("access_token") is True
        assert config_interface._is_sensitive_key("secret_value") is True
        assert config_interface._is_sensitive_key("password") is True
        assert config_interface._is_sensitive_key("auth_header") is True
        assert config_interface._is_sensitive_key("credential_data") is True
        assert config_interface._is_sensitive_key("private_key") is True
        assert config_interface._is_sensitive_key("secure_config") is True

    def test_is_sensitive_key_allows_non_sensitive(self) -> None:
        """Test _is_sensitive_key allows non-sensitive keys."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Act & Assert
        assert config_interface._is_sensitive_key("project") is False
        assert config_interface._is_sensitive_key("session_id") is False
        assert config_interface._is_sensitive_key("batch_size") is False
        assert config_interface._is_sensitive_key("timeout") is False
        assert config_interface._is_sensitive_key("endpoint_url") is False


# pylint: disable=too-few-public-methods
# Justification: Test class for constants only needs one test method


class TestCommonConfigKeys:
    """Test suite for CommonConfigKeys class."""

    def test_common_config_keys_constants(self) -> None:
        """Test CommonConfigKeys contains expected constants."""
        # Act & Assert
        assert CommonConfigKeys.API_KEY == "api_key"
        assert CommonConfigKeys.PROJECT == "project"
        assert CommonConfigKeys.SOURCE == "source"
        assert CommonConfigKeys.SESSION_NAME == "session_name"
        assert CommonConfigKeys.BATCH_SIZE == "batch_size"
        assert CommonConfigKeys.FLUSH_INTERVAL == "flush_interval"
        assert CommonConfigKeys.OTLP_ENABLED == "otlp_enabled"
        assert CommonConfigKeys.OTLP_ENDPOINT == "otlp_endpoint"
        assert CommonConfigKeys.RUN_ID == "run_id"
        assert CommonConfigKeys.DATASET_ID == "dataset_id"
        assert CommonConfigKeys.DATAPOINT_ID == "datapoint_id"
        assert CommonConfigKeys.IS_EVALUATION == "is_evaluation"
        assert CommonConfigKeys.HTTP_TRACING_ENABLED == "http_tracing_enabled"
        assert CommonConfigKeys.ASYNC_ENABLED == "async_enabled"


class TestTracerConfigInterfaceIntegration:
    """Integration tests for TracerConfigInterface with realistic scenarios."""

    def test_full_config_resolution_chain(self) -> None:
        """Test complete config resolution chain with realistic tracer."""
        # Arrange
        mock_tracer = Mock()

        # Setup merged config with some values
        mock_config = Mock()
        mock_config.api_key = "config-api-key"
        mock_config.project = "config-project"
        mock_tracer._merged_config = mock_config

        # Setup tracer attributes - ensure they don't conflict with config
        mock_tracer.session_id = "tracer-session-id"
        mock_tracer.verbose = True

        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_is_default_value", return_value=False):
            # Act & Assert - Direct config access (should find in merged config)
            assert config_interface.api_key == "config-api-key"
            assert config_interface.project == "config-project"

        # For attributes not in merged config, should fall back to tracer attributes
        with patch.object(config_interface, "_resolve_config_value") as mock_resolve:
            mock_resolve.return_value = "tracer-session-id"
            assert config_interface.session_id == "tracer-session-id"

            mock_resolve.return_value = True
            assert config_interface.verbose is True

    @patch("os.getenv")
    def test_environment_variable_override(self, mock_getenv: Mock) -> None:
        """Test environment variables override default values."""
        # Arrange
        mock_tracer = Mock()
        mock_config = Mock()
        mock_config.source = "dev"  # Default value
        mock_tracer._merged_config = mock_config

        # Setup environment variable
        mock_getenv.side_effect = lambda key: (
            "production" if key == "HH_SOURCE" else None
        )

        config_interface = TracerConfigInterface(mock_tracer)

        # Mock the resolution chain to simulate env var override
        with patch.object(
            config_interface, "_resolve_config_value", return_value="production"
        ):
            # Act
            result = config_interface.source

            # Assert
            assert result == "production"

    def test_dict_style_access(self) -> None:
        """Test dictionary-style access methods."""
        # Arrange
        mock_tracer = Mock()
        mock_config = {"api_key": "test-key", "project": "test-project"}
        mock_tracer._merged_config = mock_config

        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(config_interface, "_resolve_config_value") as mock_resolve:
            # Setup mock to return values for existing keys, None for nonexistent
            def resolve_side_effect(key: str) -> str | None:
                return mock_config.get(key)

            mock_resolve.side_effect = resolve_side_effect

            # Act & Assert - get method
            assert config_interface.get("api_key") == "test-key"
            assert config_interface.get("nonexistent", "default") == "default"

            # Act & Assert - contains method
            assert "api_key" in config_interface
            assert "nonexistent" not in config_interface

            # Act & Assert - getitem method
            assert config_interface["api_key"] == "test-key"
            assert config_interface["project"] == "test-project"

    def test_to_dict_comprehensive(self) -> None:
        """Test to_dict method with comprehensive configuration."""
        # Arrange
        mock_tracer = Mock()

        # Setup merged config
        mock_config = {
            "api_key": "secret-key",
            "project": "test-project",
            "batch_size": 100,
        }
        mock_tracer._merged_config = mock_config

        # Setup tracer attributes
        mock_tracer.session_id = "test-session"
        mock_tracer.verbose = True
        mock_tracer.timeout = 30.0
        mock_tracer.internal_method = lambda: None  # Should be filtered out

        config_interface = TracerConfigInterface(mock_tracer)

        with patch.object(
            config_interface,
            "_is_config_like_attribute",
            side_effect=lambda attr: attr in ["session_id", "verbose", "timeout"],
        ):
            # Act
            result = config_interface.to_dict()

            # Assert
            assert result["api_key"] == "secret-key"
            assert result["project"] == "test-project"
            assert result["batch_size"] == 100
            assert result["session_id"] == "test-session"
            assert result["verbose"] is True
            assert result["timeout"] == 30.0
            assert "internal_method" not in result

    def test_error_handling_edge_cases(self) -> None:
        """Test error handling for edge cases."""
        # Arrange
        mock_tracer = Mock()
        config_interface = TracerConfigInterface(mock_tracer)

        # Test with no merged config
        if hasattr(mock_tracer, "_merged_config"):
            del mock_tracer._merged_config

        # Act & Assert - Should not raise exceptions
        assert config_interface._try_direct_config_access("test_key") is None
        assert config_interface._try_nested_config_access("test_key") is None
        assert not config_interface._extract_merged_config()

        # Test attribute error handling - mock resolve to return None
        with patch.object(config_interface, "_resolve_config_value", return_value=None):
            with pytest.raises(AttributeError):
                _ = config_interface.nonexistent_key

        # Test KeyError handling - mock __getattr__ to raise AttributeError
        with patch.object(config_interface, "__getattr__", side_effect=AttributeError):
            with pytest.raises(KeyError):
                _ = config_interface["nonexistent_key"]

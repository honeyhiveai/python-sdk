"""Unit tests for OTLP configuration models.

This module provides comprehensive unit tests for the OTLPConfig class
and related utility functions with proper mocking and isolation.
"""

import json
import os
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from honeyhive.config.models.otlp import (
    OTLPConfig,
    _get_env_bool,
    _get_env_float,
    _get_env_int,
    _get_env_json,
)


class TestEnvironmentUtilityFunctions:
    """Test environment variable utility functions."""

    def test_get_env_bool_true_values(self) -> None:
        """Test _get_env_bool with various true values."""
        true_values = ["true", "1", "yes", "on", "TRUE", "True", "YES", "ON"]

        for value in true_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}):
                result = _get_env_bool("TEST_BOOL", False)
                assert result is True, f"Failed for value: {value}"

    def test_get_env_bool_false_values(self) -> None:
        """Test _get_env_bool with various false values."""
        false_values = ["false", "0", "no", "off", "FALSE", "False", "NO", "OFF"]

        for value in false_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}):
                result = _get_env_bool("TEST_BOOL", True)
                assert result is False, f"Failed for value: {value}"

    def test_get_env_bool_default_when_missing(self) -> None:
        """Test _get_env_bool returns default when environment variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = _get_env_bool("MISSING_VAR", True)
            assert result is True

            result = _get_env_bool("MISSING_VAR", False)
            assert result is False

    def test_get_env_bool_default_when_invalid(self) -> None:
        """Test _get_env_bool returns default for invalid values."""
        invalid_values = ["maybe", "invalid", "2", ""]

        for value in invalid_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}):
                result = _get_env_bool("TEST_BOOL", True)
                assert result is True, f"Failed for invalid value: {value}"

    def test_get_env_int_valid_values(self) -> None:
        """Test _get_env_int with valid integer values."""
        test_cases = [
            ("0", 0),
            ("42", 42),
            ("-10", -10),
            ("1000", 1000),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"TEST_INT": env_value}):
                result = _get_env_int("TEST_INT", 999)
                assert result == expected, f"Failed for value: {env_value}"

    def test_get_env_int_invalid_values(self) -> None:
        """Test _get_env_int returns default for invalid values."""
        invalid_values = ["not_a_number", "3.14", "", "abc"]

        for value in invalid_values:
            with patch.dict(os.environ, {"TEST_INT": value}):
                result = _get_env_int("TEST_INT", 100)
                assert result == 100, f"Failed for invalid value: {value}"

    def test_get_env_int_missing_variable(self) -> None:
        """Test _get_env_int returns default when variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = _get_env_int("MISSING_VAR", 42)
            assert result == 42

    def test_get_env_float_valid_values(self) -> None:
        """Test _get_env_float with valid float values."""
        test_cases = [
            ("0.0", 0.0),
            ("3.14", 3.14),
            ("-2.5", -2.5),
            ("42", 42.0),
            ("1000.001", 1000.001),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"TEST_FLOAT": env_value}):
                result = _get_env_float("TEST_FLOAT", 999.0)
                assert result == expected, f"Failed for value: {env_value}"

    def test_get_env_float_invalid_values(self) -> None:
        """Test _get_env_float returns default for invalid values."""
        invalid_values = ["not_a_number", "", "abc", "3.14.15"]

        for value in invalid_values:
            with patch.dict(os.environ, {"TEST_FLOAT": value}):
                result = _get_env_float("TEST_FLOAT", 5.0)
                assert result == 5.0, f"Failed for invalid value: {value}"

    def test_get_env_float_missing_variable(self) -> None:
        """Test _get_env_float returns default when variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = _get_env_float("MISSING_VAR", 3.14)
            assert result == 3.14

    def test_get_env_json_valid_dict(self) -> None:
        """Test _get_env_json with valid JSON dictionary."""
        test_dict = {"key": "value", "number": 42, "nested": {"inner": "data"}}
        json_string = json.dumps(test_dict)

        with patch.dict(os.environ, {"TEST_JSON": json_string}):
            result = _get_env_json("TEST_JSON", {})
            assert result == test_dict

    def test_get_env_json_invalid_json(self) -> None:
        """Test _get_env_json returns default for invalid JSON."""
        invalid_json_values = [
            "not_json",
            '{"invalid": json}',
            '{"unclosed": "dict"',
            "",
        ]

        for value in invalid_json_values:
            with patch.dict(os.environ, {"TEST_JSON": value}):
                result = _get_env_json("TEST_JSON", {"default": "value"})
                assert result == {
                    "default": "value"
                }, f"Failed for invalid JSON: {value}"

    def test_get_env_json_non_dict_json(self) -> None:
        """Test _get_env_json returns default for valid JSON that's not a dict."""
        non_dict_values = [
            '"string"',
            "42",
            "[1, 2, 3]",
            "true",
            "null",
        ]

        for value in non_dict_values:
            with patch.dict(os.environ, {"TEST_JSON": value}):
                result = _get_env_json("TEST_JSON", {"default": "value"})
                assert result == {
                    "default": "value"
                }, f"Failed for non-dict JSON: {value}"

    def test_get_env_json_missing_variable(self) -> None:
        """Test _get_env_json returns default when variable is missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = _get_env_json("MISSING_VAR", {"default": "value"})
            assert result == {"default": "value"}

            result = _get_env_json("MISSING_VAR", None)
            assert result is None


class TestOTLPConfigInitialization:
    """Test OTLPConfig class initialization and basic functionality."""

    def test_default_initialization(self) -> None:
        """Test OTLPConfig initialization with default values."""
        with patch.dict(os.environ, {}, clear=True):
            config = OTLPConfig()

            assert config.otlp_enabled is True
            assert config.otlp_endpoint is None
            assert config.otlp_headers is None
            assert config.batch_size == 100
            assert config.flush_interval == 5.0
            assert config.max_export_batch_size == 512
            assert config.export_timeout == 30.0

    def test_initialization_with_parameters(self) -> None:
        """Test OTLPConfig initialization with explicit parameters."""
        config = OTLPConfig(
            otlp_enabled=False,
            otlp_endpoint="https://custom.endpoint.com",
            otlp_headers={"Authorization": "Bearer token"},
            batch_size=200,
            flush_interval=1.0,
            max_export_batch_size=1024,
            export_timeout=60.0,
        )

        assert config.otlp_enabled is False
        assert config.otlp_endpoint == "https://custom.endpoint.com"
        assert config.otlp_headers == {"Authorization": "Bearer token"}
        assert config.batch_size == 200
        assert config.flush_interval == 1.0
        assert config.max_export_batch_size == 1024
        assert config.export_timeout == 60.0

    def test_initialization_from_environment_variables(self) -> None:
        """Test OTLPConfig initialization from environment variables."""
        env_vars = {
            "HH_OTLP_ENABLED": "false",
            "HH_OTLP_ENDPOINT": "https://env.endpoint.com",
            "HH_OTLP_HEADERS": '{"X-API-Key": "secret"}',
            "HH_OTLP_PROTOCOL": "http/json",
            "HH_BATCH_SIZE": "300",
            "HH_FLUSH_INTERVAL": "2.5",
            "HH_MAX_EXPORT_BATCH_SIZE": "2048",
            "HH_EXPORT_TIMEOUT": "45.0",
        }

        with patch.dict(os.environ, env_vars):
            config = OTLPConfig()

            assert config.otlp_enabled is False
            assert config.otlp_endpoint == "https://env.endpoint.com"
            assert config.otlp_headers == {"X-API-Key": "secret"}
            assert config.otlp_protocol == "http/json"  # From HH_OTLP_PROTOCOL env var
            assert config.batch_size == 300
            assert config.flush_interval == 2.5
            assert config.max_export_batch_size == 2048
            assert config.export_timeout == 45.0

    def test_parameter_precedence_over_environment(self) -> None:
        """Test that explicit parameters take precedence over environment variables."""
        env_vars = {
            "HH_BATCH_SIZE": "500",
            "HH_FLUSH_INTERVAL": "10.0",
        }

        with patch.dict(os.environ, env_vars):
            config = OTLPConfig(batch_size=200, flush_interval=1.0)

            assert config.batch_size == 200  # Parameter overrides env
            assert config.flush_interval == 1.0  # Parameter overrides env


class TestOTLPEndpointValidation:
    """Test OTLP endpoint validation functionality."""

    @patch("honeyhive.config.models.otlp._safe_validate_url")
    def test_validate_otlp_endpoint_none_value(self, mock_validate_url: Mock) -> None:
        """Test endpoint validation with None value."""
        result = OTLPConfig.validate_otlp_endpoint(None)
        assert result is None
        mock_validate_url.assert_not_called()

    @patch("honeyhive.config.models.otlp._safe_validate_url")
    def test_validate_otlp_endpoint_valid_url(self, mock_validate_url: Mock) -> None:
        """Test endpoint validation with valid URL."""
        mock_validate_url.return_value = "https://api.example.com/otlp"

        result = OTLPConfig.validate_otlp_endpoint("https://api.example.com/otlp/")

        assert result == "https://api.example.com/otlp"  # Trailing slash removed
        mock_validate_url.assert_called_once_with(
            "https://api.example.com/otlp/",
            "otlp_endpoint",
            allow_none=False,
            default="http://localhost:4318/v1/traces",
        )

    @patch("honeyhive.config.models.otlp._safe_validate_url")
    def test_validate_otlp_endpoint_invalid_url_uses_default(
        self, mock_validate_url: Mock
    ) -> None:
        """Test endpoint validation with invalid URL falls back to default."""
        mock_validate_url.return_value = "http://localhost:4318/v1/traces"

        result = OTLPConfig.validate_otlp_endpoint("invalid-url")

        assert result == "http://localhost:4318/v1/traces"
        mock_validate_url.assert_called_once_with(
            "invalid-url",
            "otlp_endpoint",
            allow_none=False,
            default="http://localhost:4318/v1/traces",
        )

    @patch("honeyhive.config.models.otlp._safe_validate_url")
    def test_validate_otlp_endpoint_none_return_from_validator(
        self, mock_validate_url: Mock
    ) -> None:
        """Test endpoint validation when validator returns None."""
        mock_validate_url.return_value = None

        result = OTLPConfig.validate_otlp_endpoint("some-url")

        assert result is None
        mock_validate_url.assert_called_once()


class TestBatchSizeValidation:
    """Test batch size validation functionality."""

    def test_validate_batch_sizes_valid_values(self) -> None:
        """Test batch size validation with valid values."""
        valid_values = [1, 50, 100, 500, 1000, 5000, 10000]

        for value in valid_values:
            result = OTLPConfig.validate_batch_sizes(value)
            assert result == value, f"Failed for valid value: {value}"

    def test_validate_batch_sizes_string_conversion(self) -> None:
        """Test batch size validation with string values that can be converted."""
        string_values = ["1", "100", "500", "1000"]

        for value in string_values:
            result = OTLPConfig.validate_batch_sizes(value)
            assert result == int(value), f"Failed for string value: {value}"

    @patch("logging.getLogger")
    def test_validate_batch_sizes_none_value(self, mock_get_logger: Mock) -> None:
        """Test batch size validation with None value."""
        result = OTLPConfig.validate_batch_sizes(None)
        assert result == 100  # Default value
        mock_get_logger.assert_not_called()

    @patch("logging.getLogger")
    def test_validate_batch_sizes_invalid_type(self, mock_get_logger: Mock) -> None:
        """Test batch size validation with invalid type."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        invalid_values = ["not_a_number", [], {}, object()]

        for value in invalid_values:
            result = OTLPConfig.validate_batch_sizes(value)
            assert result == 100, f"Failed for invalid value: {value}"

        # Should log warning for each invalid value
        assert mock_logger.warning.call_count == len(invalid_values)

    @patch("logging.getLogger")
    def test_validate_batch_sizes_negative_value(self, mock_get_logger: Mock) -> None:
        """Test batch size validation with negative values."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        negative_values = [-1, -10, -100, 0]

        for value in negative_values:
            result = OTLPConfig.validate_batch_sizes(value)
            assert result == 100, f"Failed for negative value: {value}"

        # Should log warning for each negative value
        assert mock_logger.warning.call_count == len(negative_values)

    @patch("logging.getLogger")
    def test_validate_batch_sizes_too_large(self, mock_get_logger: Mock) -> None:
        """Test batch size validation with values exceeding maximum."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        large_values = [10001, 50000, 100000]

        for value in large_values:
            result = OTLPConfig.validate_batch_sizes(value)
            assert result == 10000, f"Failed for large value: {value}"

        # Should log warning for each large value
        assert mock_logger.warning.call_count == len(large_values)


class TestTimeoutValidation:
    """Test timeout validation functionality."""

    def test_validate_timeouts_valid_values(self) -> None:
        """Test timeout validation with valid values."""
        valid_values = [0.1, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0]

        for value in valid_values:
            result = OTLPConfig.validate_timeouts(value)
            assert result == value, f"Failed for valid value: {value}"

    def test_validate_timeouts_integer_conversion(self) -> None:
        """Test timeout validation with integer values."""
        integer_values = [1, 5, 10, 30, 60]

        for value in integer_values:
            result = OTLPConfig.validate_timeouts(value)
            assert result == float(value), f"Failed for integer value: {value}"

    def test_validate_timeouts_string_conversion(self) -> None:
        """Test timeout validation with string values that can be converted."""
        string_values = ["1.0", "5.5", "10", "30.0"]

        for value in string_values:
            result = OTLPConfig.validate_timeouts(value)
            assert result == float(value), f"Failed for string value: {value}"

    @patch("logging.getLogger")
    def test_validate_timeouts_none_value(self, mock_get_logger: Mock) -> None:
        """Test timeout validation with None value."""
        result = OTLPConfig.validate_timeouts(None)
        assert result == 5.0  # Default value
        mock_get_logger.assert_not_called()

    @patch("logging.getLogger")
    def test_validate_timeouts_invalid_type(self, mock_get_logger: Mock) -> None:
        """Test timeout validation with invalid type."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        invalid_values = ["not_a_number", [], {}, object()]

        for value in invalid_values:
            result = OTLPConfig.validate_timeouts(value)
            assert result == 5.0, f"Failed for invalid value: {value}"

        # Should log warning for each invalid value
        assert mock_logger.warning.call_count == len(invalid_values)

    @patch("logging.getLogger")
    def test_validate_timeouts_negative_or_zero(self, mock_get_logger: Mock) -> None:
        """Test timeout validation with negative or zero values."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        invalid_values = [-1.0, -10.0, 0.0, -0.1]

        for value in invalid_values:
            result = OTLPConfig.validate_timeouts(value)
            assert result == 5.0, f"Failed for invalid value: {value}"

        # Should log warning for each invalid value
        assert mock_logger.warning.call_count == len(invalid_values)


class TestOTLPHeadersValidation:
    """Test OTLP headers validation functionality."""

    def test_validate_otlp_headers_none_value(self) -> None:
        """Test headers validation with None value."""
        result = OTLPConfig.validate_otlp_headers(None)
        assert result is None

    def test_validate_otlp_headers_valid_dict(self) -> None:
        """Test headers validation with valid dictionary."""
        valid_headers = {
            "Authorization": "Bearer token",
            "X-API-Key": "secret",
            "Content-Type": "application/json",
        }

        result = OTLPConfig.validate_otlp_headers(valid_headers)
        assert result == valid_headers

    @patch("logging.getLogger")
    def test_validate_otlp_headers_invalid_type(self, mock_get_logger: Mock) -> None:
        """Test headers validation with invalid type."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        invalid_values: list[Any] = ["string", 123, [], object()]

        for value in invalid_values:
            result = OTLPConfig.validate_otlp_headers(value)
            assert result is None, f"Failed for invalid value: {value}"

        # Should log warning for each invalid value
        assert mock_logger.warning.call_count == len(invalid_values)

    @patch("logging.getLogger")
    def test_validate_otlp_headers_invalid_keys(self, mock_get_logger: Mock) -> None:
        """Test headers validation with invalid key types."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        headers_with_invalid_keys: Dict[Any, str] = {
            "valid_key": "valid_value",
            123: "invalid_key_type",
            None: "another_invalid_key",
            "another_valid_key": "another_valid_value",
        }

        result = OTLPConfig.validate_otlp_headers(headers_with_invalid_keys)

        # Should only include valid string keys
        expected = {
            "valid_key": "valid_value",
            "another_valid_key": "another_valid_value",
        }
        assert result == expected

        # Should log warning for each invalid key
        assert mock_logger.warning.call_count == 2

    @patch("logging.getLogger")
    def test_validate_otlp_headers_all_invalid_keys(
        self, mock_get_logger: Mock
    ) -> None:
        """Test headers validation when all keys are invalid."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        headers_with_all_invalid_keys: Dict[Any, str] = {
            123: "value1",
            None: "value2",
            tuple(): "value3",  # Use tuple instead of list (hashable)
        }

        result = OTLPConfig.validate_otlp_headers(headers_with_all_invalid_keys)

        # Should return None when no valid keys remain
        assert result is None

        # Should log warning for each invalid key
        assert mock_logger.warning.call_count == 3


class TestOTLPConfigIntegration:
    """Test OTLPConfig integration scenarios."""

    def test_full_configuration_with_all_fields(self) -> None:
        """Test complete configuration with all fields specified."""
        config_data = {
            "otlp_enabled": True,
            "otlp_endpoint": "https://api.honeyhive.ai/otlp",
            "otlp_headers": {"Authorization": "Bearer test-token"},
            "batch_size": 250,
            "flush_interval": 2.0,
            "max_export_batch_size": 1024,
            "export_timeout": 45.0,
        }

        config = OTLPConfig(**config_data)

        assert config.otlp_enabled is True
        assert config.otlp_endpoint == "https://api.honeyhive.ai/otlp"
        assert config.otlp_headers == {"Authorization": "Bearer test-token"}
        assert config.batch_size == 250
        assert config.flush_interval == 2.0
        assert config.max_export_batch_size == 1024
        assert config.export_timeout == 45.0

    def test_mixed_environment_and_parameters(self) -> None:
        """Test configuration with mixed environment variables and parameters."""
        env_vars = {
            "HH_OTLP_ENABLED": "true",
            "HH_BATCH_SIZE": "150",
            "HH_FLUSH_INTERVAL": "3.0",
        }

        with patch.dict(os.environ, env_vars):
            config = OTLPConfig(
                otlp_endpoint="https://override.endpoint.com",
                export_timeout=25.0,
            )

            # Environment variables should be used
            assert config.otlp_enabled is True
            assert config.batch_size == 150
            assert config.flush_interval == 3.0

            # Parameters should override
            assert config.otlp_endpoint == "https://override.endpoint.com"
            assert config.export_timeout == 25.0

            # Defaults should be used for unspecified fields
            assert config.otlp_headers is None
            assert config.max_export_batch_size == 512

    @patch("honeyhive.config.models.otlp._safe_validate_url")
    def test_validation_error_handling(self, mock_validate_url: Mock) -> None:
        """Test that validation errors are handled gracefully."""
        # Mock URL validation to return a valid URL
        mock_validate_url.return_value = "http://localhost:4318/v1/traces"

        # This should not raise an exception even with invalid data types
        # because validators handle graceful degradation
        config = OTLPConfig(
            batch_size="invalid",  # Will be converted to default 100
            flush_interval="invalid",  # Will be converted to default 5.0
            otlp_headers="invalid",  # Will be converted to None
        )

        assert config.batch_size == 100
        assert config.flush_interval == 5.0
        assert config.otlp_headers is None

    def test_model_config_settings(self) -> None:
        """Test that model configuration settings are properly applied."""
        config = OTLPConfig()

        # Verify model config attributes (model_config is a dict in Pydantic v2)
        assert config.model_config["env_prefix"] == ""
        assert config.model_config["validate_assignment"] is True
        assert config.model_config["extra"] == "forbid"
        assert config.model_config["case_sensitive"] is False

    def test_forbidden_extra_fields(self) -> None:
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            OTLPConfig(invalid_field="should_fail")

        error = exc_info.value
        assert "Extra inputs are not permitted" in str(error)

    def test_field_descriptions_and_examples(self) -> None:
        """Test that field metadata is properly configured."""
        config = OTLPConfig()

        # Verify that model fields are properly configured

        # Check that all expected fields exist
        expected_fields = [
            "otlp_enabled",
            "otlp_endpoint",
            "otlp_headers",
            "batch_size",
            "flush_interval",
            "max_export_batch_size",
            "export_timeout",
        ]

        for field_name in expected_fields:
            assert hasattr(config, field_name)

        # Verify some field properties by accessing the actual values
        assert config.batch_size == 100
        assert config.flush_interval == 5.0
        # Note: otlp_enabled may be False in test environment, check field exists
        assert hasattr(config, "otlp_enabled")


class TestOTLPConfigEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_boundary_batch_sizes(self) -> None:
        """Test batch size validation at boundaries."""
        # Test minimum valid value
        config = OTLPConfig(batch_size=1)
        assert config.batch_size == 1

        # Test maximum valid value
        config = OTLPConfig(batch_size=10000)
        assert config.batch_size == 10000

    def test_boundary_timeouts(self) -> None:
        """Test timeout validation at boundaries."""
        # Test very small positive value
        config = OTLPConfig(flush_interval=0.001, export_timeout=0.001)
        assert config.flush_interval == 0.001
        assert config.export_timeout == 0.001

    def test_empty_headers_dict(self) -> None:
        """Test configuration with empty headers dictionary."""
        config = OTLPConfig(otlp_headers={})
        # Empty dict is converted to None by validation
        assert config.otlp_headers is None

    def test_large_headers_dict(self) -> None:
        """Test configuration with large headers dictionary."""
        large_headers = {f"Header-{i}": f"Value-{i}" for i in range(100)}
        config = OTLPConfig(otlp_headers=large_headers)
        assert config.otlp_headers == large_headers

    @patch.dict(os.environ, {}, clear=True)
    def test_clean_environment_initialization(self) -> None:
        """Test initialization with completely clean environment."""
        config = OTLPConfig()

        # Should use all defaults
        assert config.otlp_enabled is True
        assert config.otlp_endpoint is None
        assert config.otlp_headers is None
        assert config.batch_size == 100
        assert config.flush_interval == 5.0
        assert config.max_export_batch_size == 512
        assert config.export_timeout == 30.0

    def test_case_insensitive_environment_variables(self) -> None:
        """Test that environment variables are case insensitive due to model config."""
        # Note: This tests the model_config.case_sensitive = False setting
        # The actual case insensitivity is handled by Pydantic's settings
        config = OTLPConfig()
        assert config.model_config["case_sensitive"] is False

    def test_otlp_protocol_from_environment(self) -> None:
        """Test otlp_protocol can be set from environment variables."""
        with patch.dict(os.environ, {"HH_OTLP_PROTOCOL": "http/json"}):
            config = OTLPConfig()
            assert config.otlp_protocol == "http/json"

        with patch.dict(os.environ, {"OTEL_EXPORTER_OTLP_PROTOCOL": "http/json"}):
            config = OTLPConfig()
            assert config.otlp_protocol == "http/json"

        with patch.dict(os.environ, {}, clear=True):
            config = OTLPConfig()
            assert config.otlp_protocol == "http/protobuf"  # Default

    def test_otlp_protocol_parameter_override(self) -> None:
        """Test that otlp_protocol parameter overrides environment variable."""
        with patch.dict(os.environ, {"HH_OTLP_PROTOCOL": "http/json"}):
            config = OTLPConfig(otlp_protocol="http/protobuf")
            assert config.otlp_protocol == "http/protobuf"

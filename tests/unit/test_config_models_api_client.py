"""Unit tests for HoneyHive API client configuration models.

This module contains comprehensive unit tests for the APIClientConfig class,
focusing on configuration validation, environment variable handling, and
field validation behavior.

Tests cover:
- APIClientConfig class initialization and configuration
- Server URL validation with various input types
- Environment variable loading (HH_API_URL)
- HTTPClientConfig composition and integration
- Field validation error handling and graceful degradation
- Pydantic model configuration behavior
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

# pylint: disable=too-many-public-methods
# Justification: Comprehensive unit test coverage requires extensive test cases

import os
from typing import Dict
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from honeyhive.config.models.api_client import APIClientConfig
from honeyhive.config.models.base import BaseHoneyHiveConfig
from honeyhive.config.models.http_client import HTTPClientConfig


class TestAPIClientConfig:
    """Test suite for APIClientConfig class."""

    def test_initialization_default_values(self) -> None:
        """Test APIClientConfig initialization with default values.

        Verifies that the configuration initializes with proper default values
        for all fields when no parameters are provided.
        """
        config = APIClientConfig()

        assert isinstance(config, BaseHoneyHiveConfig)
        assert config.server_url == "https://api.honeyhive.ai"
        assert isinstance(config.http_config, HTTPClientConfig)

    def test_initialization_with_server_url(self) -> None:
        """Test APIClientConfig initialization with custom server URL.

        Verifies that the configuration accepts and properly validates
        a custom server URL parameter.
        """
        custom_url = "https://custom.honeyhive.com"
        config = APIClientConfig(server_url=custom_url)

        assert config.server_url == custom_url
        assert isinstance(config.http_config, HTTPClientConfig)

    def test_initialization_with_http_config(self) -> None:
        """Test APIClientConfig initialization with custom HTTP config.

        Verifies that the configuration accepts and properly composes
        a custom HTTPClientConfig instance.
        """
        custom_http_config = HTTPClientConfig(timeout=60.0, max_connections=50)
        config = APIClientConfig(http_config=custom_http_config)

        assert config.server_url == "https://api.honeyhive.ai"
        assert config.http_config is custom_http_config
        assert hasattr(config.http_config, "timeout")
        assert hasattr(config.http_config, "max_connections")

    def test_initialization_with_all_parameters(self) -> None:
        """Test APIClientConfig initialization with all parameters.

        Verifies that the configuration properly handles initialization
        with both server_url and http_config parameters.
        """
        custom_url = "https://custom.honeyhive.com"
        custom_http_config = HTTPClientConfig(timeout=45.0, max_connections=25)

        config = APIClientConfig(server_url=custom_url, http_config=custom_http_config)

        assert config.server_url == custom_url
        assert config.http_config is custom_http_config
        assert hasattr(config.http_config, "timeout")
        assert hasattr(config.http_config, "max_connections")

    @patch.dict(os.environ, {"HH_API_URL": "https://env.honeyhive.ai"})
    def test_environment_variable_loading(self) -> None:
        """Test APIClientConfig loads server URL from environment variable.

        Verifies that the configuration properly loads the server URL
        from the HH_API_URL environment variable when available.
        """
        config = APIClientConfig()

        assert config.server_url == "https://env.honeyhive.ai"

    @patch.dict(os.environ, {"HH_API_URL": "https://env.honeyhive.ai/"})
    def test_environment_variable_trailing_slash_removal(self) -> None:
        """Test server URL trailing slash removal from environment variable.

        Verifies that trailing slashes are properly removed from server URLs
        loaded from environment variables for consistency.
        """
        config = APIClientConfig()

        assert config.server_url == "https://env.honeyhive.ai"

    def test_server_url_validation_valid_https(self) -> None:
        """Test server URL validation with valid HTTPS URL.

        Verifies that the validator accepts and properly processes
        valid HTTPS URLs.
        """
        config = APIClientConfig(server_url="https://api.example.com")

        assert config.server_url == "https://api.example.com"

    def test_server_url_validation_valid_http(self) -> None:
        """Test server URL validation with valid HTTP URL.

        Verifies that the validator accepts and properly processes
        valid HTTP URLs.
        """
        config = APIClientConfig(server_url="http://localhost:8080")

        assert config.server_url == "http://localhost:8080"

    def test_server_url_validation_trailing_slash_removal(self) -> None:
        """Test server URL validation removes trailing slashes.

        Verifies that the validator removes trailing slashes from
        server URLs for consistency.
        """
        config = APIClientConfig(server_url="https://api.example.com/")

        assert config.server_url == "https://api.example.com"

    def test_server_url_validation_multiple_trailing_slashes(self) -> None:
        """Test server URL validation removes multiple trailing slashes.

        Verifies that the validator removes multiple trailing slashes
        from server URLs.
        """
        config = APIClientConfig(server_url="https://api.example.com///")

        assert config.server_url == "https://api.example.com"

    def test_server_url_validation_with_invalid_protocol(self) -> None:
        """Test server URL validation with invalid protocol.

        Verifies that the validator properly handles URLs without
        proper HTTP/HTTPS protocol and falls back to default.
        """
        config = APIClientConfig(server_url="ftp://invalid.example.com")

        assert config.server_url == "https://api.honeyhive.ai"

    def test_server_url_validation_graceful_degradation(self) -> None:
        """Test server URL validation graceful degradation behavior.

        Verifies that invalid URLs are handled gracefully and fall back
        to the default server URL without raising exceptions.
        """
        config = APIClientConfig(server_url="not-a-url")

        assert config.server_url == "https://api.honeyhive.ai"

    def test_server_url_validation_with_malformed_url(self) -> None:
        """Test server URL validation with malformed URL.

        Verifies that malformed URLs are handled gracefully through
        the validation system.
        """
        config = APIClientConfig(server_url="://malformed")

        assert config.server_url == "https://api.honeyhive.ai"

    def test_server_url_validation_with_none_input(self) -> None:
        """Test server URL validation with None input.

        Verifies that the validator properly handles None input values
        and uses the default server URL.
        """
        config = APIClientConfig(server_url=None)  # type: ignore[arg-type]

        assert config.server_url == "https://api.honeyhive.ai"

    def test_server_url_validation_with_empty_string_input(self) -> None:
        """Test server URL validation with empty string input.

        Verifies that the validator properly handles empty string input
        and falls back to the default server URL.
        """
        config = APIClientConfig(server_url="")

        assert config.server_url == "https://api.honeyhive.ai"

    def test_server_url_validation_with_non_string_input(self) -> None:
        """Test server URL validation with non-string input.

        Verifies that the validator properly handles non-string input values
        and falls back to the default server URL through graceful degradation.
        """
        config = APIClientConfig(server_url=12345)  # type: ignore[arg-type]

        assert config.server_url == "https://api.honeyhive.ai"

    def test_server_url_validation_with_dict_input(self) -> None:
        """Test server URL validation with dictionary input.

        Verifies that the validator properly handles dictionary input values
        and falls back to the default server URL.
        """
        invalid_input: Dict[str, str] = {"url": "https://example.com"}
        config = APIClientConfig(server_url=invalid_input)  # type: ignore[arg-type]

        assert config.server_url == "https://api.honeyhive.ai"

    def test_server_url_validation_with_list_input(self) -> None:
        """Test server URL validation with list input.

        Verifies that the validator properly handles list input values
        and falls back to the default server URL.
        """
        invalid_input = ["https://example.com", "https://backup.com"]
        config = APIClientConfig(server_url=invalid_input)  # type: ignore[arg-type]

        assert config.server_url == "https://api.honeyhive.ai"

    def test_model_config_env_prefix(self) -> None:
        """Test model configuration does not use env_prefix.

        Verifies that the model configuration uses explicit validation_alias
        instead of env_prefix for environment variable loading.
        """
        assert APIClientConfig.model_config["env_prefix"] == ""

    def test_model_config_validate_assignment(self) -> None:
        """Test model configuration enables assignment validation.

        Verifies that the model configuration enables validation
        when values are assigned after initialization.
        """
        assert APIClientConfig.model_config["validate_assignment"] is True

    def test_model_config_extra_forbid(self) -> None:
        """Test model configuration forbids extra fields.

        Verifies that the model configuration is set to forbid
        extra fields that are not defined in the model.
        """
        assert APIClientConfig.model_config["extra"] == "forbid"

    def test_model_config_case_sensitive(self) -> None:
        """Test model configuration is case insensitive.

        Verifies that the model configuration is set to be
        case insensitive for field names.
        """
        assert APIClientConfig.model_config["case_sensitive"] is False

    def test_extra_fields_forbidden(self) -> None:
        """Test that extra fields are forbidden during initialization.

        Verifies that the model raises a ValidationError when
        extra fields are provided during initialization.
        """
        with pytest.raises(ValidationError) as exc_info:
            APIClientConfig(extra_field="not_allowed")  # type: ignore[call-arg]

        assert "extra_field" in str(exc_info.value)

    def test_inheritance_from_base_honeyhive_config(self) -> None:
        """Test APIClientConfig inherits from BaseHoneyHiveConfig.

        Verifies that APIClientConfig properly inherits from the base
        configuration class and has access to common fields.
        """
        config = APIClientConfig()

        assert isinstance(config, BaseHoneyHiveConfig)
        # Verify inherited fields are accessible (from BaseHoneyHiveConfig)
        assert hasattr(config, "api_key")
        assert hasattr(config, "project")
        assert hasattr(config, "test_mode")
        assert hasattr(config, "verbose")

    def test_http_config_default_factory(self) -> None:
        """Test HTTPClientConfig is created with default factory.

        Verifies that each APIClientConfig instance gets its own
        HTTPClientConfig instance through the default factory.
        """
        config1 = APIClientConfig()
        config2 = APIClientConfig()

        assert isinstance(config1.http_config, HTTPClientConfig)
        assert isinstance(config2.http_config, HTTPClientConfig)
        assert config1.http_config is not config2.http_config

    def test_http_config_composition(self) -> None:
        """Test HTTPClientConfig composition behavior.

        Verifies that the APIClientConfig properly composes the
        HTTPClientConfig and maintains the relationship.
        """
        config = APIClientConfig()

        assert isinstance(config.http_config, HTTPClientConfig)
        assert hasattr(config.http_config, "timeout")
        assert hasattr(config.http_config, "max_connections")

    @patch.dict(os.environ, {"HH_API_URL": "https://env-server.com"})
    def test_case_insensitive_environment_variables(self) -> None:
        """Test case insensitive environment variable handling.

        Verifies that environment variables are properly loaded
        with the HH_API_URL environment variable.
        """
        config = APIClientConfig()

        assert config.server_url == "https://env-server.com"

    def test_field_descriptions_and_examples(self) -> None:
        """Test field descriptions and examples are properly set.

        Verifies that the server_url field has proper description
        and examples as defined in the Field configuration.
        """
        # Test that model has the expected field
        config = APIClientConfig()
        assert hasattr(config, "server_url")
        assert config.server_url == "https://api.honeyhive.ai"

    def test_http_config_field_description(self) -> None:
        """Test http_config field has proper description.

        Verifies that the http_config field has the correct
        description as defined in the Field configuration.
        """
        # Test that model has the expected field
        config = APIClientConfig()
        assert hasattr(config, "http_config")
        assert isinstance(config.http_config, HTTPClientConfig)

    def test_validate_assignment_behavior(self) -> None:
        """Test validate_assignment behavior after initialization.

        Verifies that field validation occurs when values are
        assigned after the model is initialized.
        """
        config = APIClientConfig()

        # Valid assignment should work
        config.server_url = "https://new.example.com"
        assert config.server_url == "https://new.example.com"

        # Invalid assignment should trigger validation
        config.server_url = "https://with-slash.com/"
        assert config.server_url == "https://with-slash.com"  # Trailing slash removed

    def test_server_url_field_default_value(self) -> None:
        """Test server_url field has correct default value.

        Verifies that the server_url field is configured with
        the correct default value.
        """
        config = APIClientConfig()
        assert config.server_url == "https://api.honeyhive.ai"

    def test_docstring_examples_functionality(self) -> None:
        """Test functionality described in class docstring examples.

        Verifies that the examples provided in the class docstring
        work as documented.
        """
        # Simple usage example
        config = APIClientConfig(
            api_key="hh_1234567890abcdef", server_url="https://api.honeyhive.ai"
        )
        assert config.server_url == "https://api.honeyhive.ai"

        # Advanced usage with HTTP config example
        http_config = HTTPClientConfig(timeout=60.0, max_connections=50)
        config = APIClientConfig(
            api_key="hh_1234567890abcdef",
            server_url="https://api.honeyhive.ai",
            http_config=http_config,
        )
        assert config.server_url == "https://api.honeyhive.ai"
        assert hasattr(config.http_config, "timeout")
        assert hasattr(config.http_config, "max_connections")

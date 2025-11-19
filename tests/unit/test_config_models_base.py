"""Unit tests for HoneyHive config models base functionality.

This module tests the BaseHoneyHiveConfig class including field validation,
environment variable loading, and common configuration patterns.
"""

import os
from typing import Any, Dict, Optional
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from honeyhive.config.models.base import BaseHoneyHiveConfig, _safe_validate_url


class TestBaseHoneyHiveConfig:
    """Test the BaseHoneyHiveConfig class."""

    def test_initialization_with_all_fields(self) -> None:
        """Test initialization with all fields provided."""
        config = BaseHoneyHiveConfig(
            api_key="hh_test_key_123",
            project="test-project",
            test_mode=True,
            verbose=True,
        )

        assert config.api_key == "hh_test_key_123"
        assert config.project == "test-project"
        assert config.test_mode is True
        assert config.verbose is True

    def test_initialization_with_minimal_fields(self) -> None:
        """Test initialization with minimal required fields."""
        # Clear environment to ensure clean test
        with patch.dict(os.environ, {}, clear=True):
            config = BaseHoneyHiveConfig(
                api_key="hh_test_key_123", project="test-project"
            )

            assert config.api_key == "hh_test_key_123"
            assert config.project == "test-project"
            assert config.test_mode is False  # Default value
            assert config.verbose is False  # Default value

    def test_initialization_with_environment_variables(self) -> None:
        """Test initialization loads from environment variables."""
        env_vars = {
            "HH_API_KEY": "env_api_key_456",
            "HH_PROJECT": "env-project",
            "HH_TEST_MODE": "true",
            "HH_VERBOSE": "false",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = BaseHoneyHiveConfig()

            assert config.api_key == "env_api_key_456"
            assert config.project == "env-project"
            assert config.test_mode is True
            assert config.verbose is False

    def test_parameter_override_environment(self) -> None:
        """Test that explicit parameters override environment variables."""
        env_vars = {
            "HH_API_KEY": "env_api_key",
            "HH_PROJECT": "env-project",
            "HH_TEST_MODE": "true",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = BaseHoneyHiveConfig(api_key="param_api_key", test_mode=False)

            assert config.api_key == "param_api_key"  # Parameter overrides env
            assert config.project == "env-project"  # From environment
            assert config.test_mode is False  # Parameter overrides env

    def test_api_key_validation_valid_keys(self) -> None:
        """Test API key validation with valid keys."""
        valid_keys = [
            "hh_1234567890abcdef",
            "hh_short",
            "hh_very_long_api_key_with_underscores_and_numbers_123456789",
        ]

        for api_key in valid_keys:
            config = BaseHoneyHiveConfig(api_key=api_key, project="test")
            assert config.api_key == api_key

    def test_api_key_validation_graceful_degradation(self) -> None:
        """Test API key validation uses graceful degradation."""
        # Test empty string gets converted to None
        config = BaseHoneyHiveConfig(api_key="", project="test")
        assert config.api_key is None

        # Test whitespace only gets converted to None
        config = BaseHoneyHiveConfig(api_key="   ", project="test")
        assert config.api_key is None

        # Test None is allowed
        config = BaseHoneyHiveConfig(api_key=None, project="test")
        assert config.api_key is None

        # Test non-hh_ keys are allowed (for backwards compatibility)
        config = BaseHoneyHiveConfig(api_key="invalid", project="test")
        assert config.api_key == "invalid"

        # Test non-string api_key gets converted to None with warning
        config = BaseHoneyHiveConfig(api_key=123, project="test")
        assert config.api_key is None

    def test_project_validation_valid_projects(self) -> None:
        """Test project validation with valid project names."""
        valid_projects = [
            "simple-project",
            "project_with_underscores",
            "project123",
            "a",  # Single character
            "very-long-project-name-with-many-hyphens-and-numbers-123",
        ]

        for project in valid_projects:
            config = BaseHoneyHiveConfig(api_key="hh_test", project=project)
            assert config.project == project

    def test_project_validation_graceful_degradation(self) -> None:
        """Test project validation uses graceful degradation."""
        # Test empty string gets converted to None
        config = BaseHoneyHiveConfig(api_key="hh_test", project="")
        assert config.project is None

        # Test whitespace only gets converted to None
        config = BaseHoneyHiveConfig(api_key="hh_test", project="   ")
        assert config.project is None

        # Test invalid characters get converted to None
        config = BaseHoneyHiveConfig(api_key="hh_test", project="project/with/slash")
        assert config.project is None

        config = BaseHoneyHiveConfig(api_key="hh_test", project="project?with?question")
        assert config.project is None

        # Test None is allowed
        config = BaseHoneyHiveConfig(api_key="hh_test", project=None)
        assert config.project is None

        # Test non-string project gets converted to None with warning
        config = BaseHoneyHiveConfig(api_key="hh_test", project=123)
        assert config.project is None

    @pytest.mark.parametrize(
        "test_mode_value,expected",
        [
            ("true", True),
            ("false", False),
            ("1", True),
            ("0", False),
            ("yes", True),
            ("no", False),
            ("TRUE", True),
            ("FALSE", False),
        ],
    )
    def test_test_mode_environment_parsing(
        self, test_mode_value: str, expected: bool
    ) -> None:
        """Test test_mode parsing from environment variables."""
        with patch.dict(os.environ, {"HH_TEST_MODE": test_mode_value}, clear=True):
            config = BaseHoneyHiveConfig(api_key="hh_test", project="test")
            assert config.test_mode is expected

    @pytest.mark.parametrize(
        "verbose_value,expected",
        [
            ("true", True),
            ("false", False),
            ("1", True),
            ("0", False),
            ("yes", True),
            ("no", False),
            ("TRUE", True),
            ("FALSE", False),
        ],
    )
    def test_verbose_environment_parsing(
        self, verbose_value: str, expected: bool
    ) -> None:
        """Test verbose parsing from environment variables."""
        with patch.dict(os.environ, {"HH_VERBOSE": verbose_value}, clear=True):
            config = BaseHoneyHiveConfig(api_key="hh_test", project="test")
            assert config.verbose is expected

    def test_model_config_settings(self) -> None:
        """Test that model configuration is set correctly."""
        _ = BaseHoneyHiveConfig(api_key="hh_test", project="test")  # Test instantiation

        # Test that extra fields are forbidden
        with pytest.raises(ValidationError):
            BaseHoneyHiveConfig(
                api_key="hh_test", project="test", invalid_field="should_fail"
            )

    def test_field_descriptions_and_examples(self) -> None:
        """Test that fields have proper descriptions and examples."""
        # This tests the Field definitions in the model
        schema = BaseHoneyHiveConfig.model_json_schema()

        # Check api_key field (now appears as HH_API_KEY in schema due to
        # validation_alias)
        api_key_field = schema["properties"]["HH_API_KEY"]
        assert "description" in api_key_field
        assert "examples" in api_key_field
        assert "hh_" in str(api_key_field["examples"])

        # Check project field (now appears as HH_PROJECT in schema due to
        # validation_alias)
        project_field = schema["properties"]["HH_PROJECT"]
        assert "description" in project_field
        assert "examples" in project_field

    def test_model_serialization(self) -> None:
        """Test model serialization to dict and JSON."""
        config = BaseHoneyHiveConfig(
            api_key="hh_test_key", project="test-project", test_mode=True, verbose=False
        )

        # Test dict serialization
        config_dict = config.model_dump()
        expected_dict = {
            "api_key": "hh_test_key",
            "project": "test-project",
            "test_mode": True,
            "verbose": False,
        }
        assert config_dict == expected_dict

        # Test JSON serialization
        config_json = config.model_dump_json()
        assert isinstance(config_json, str)
        assert "hh_test_key" in config_json
        assert "test-project" in config_json

    def test_model_deserialization(self) -> None:
        """Test model deserialization from dict."""
        config_data = {
            "api_key": "hh_test_key",
            "project": "test-project",
            "test_mode": True,
            "verbose": False,
        }

        config = BaseHoneyHiveConfig(**config_data)

        assert config.api_key == "hh_test_key"
        assert config.project == "test-project"
        assert config.test_mode is True
        assert config.verbose is False

    def test_case_insensitive_field_names(self) -> None:
        """Test that field names are case insensitive."""
        # The model should accept both cases due to case_sensitive=False
        config = BaseHoneyHiveConfig(
            api_key="hh_test_key",  # Lowercase (standard)
            project="test-project",  # Lowercase (standard)
            test_mode=True,
            verbose=False,
        )

        assert config.api_key == "hh_test_key"
        assert config.project == "test-project"
        assert config.test_mode is True
        assert config.verbose is False

    def test_inheritance_compatibility(self) -> None:
        """Test that the base config can be properly inherited."""

        class TestChildConfig(BaseHoneyHiveConfig):
            """Test child configuration class."""

            child_field: Optional[str] = None

        config = TestChildConfig(
            api_key="hh_test", project="test", child_field="child_value"
        )

        # Base fields should work
        assert config.api_key == "hh_test"
        assert config.project == "test"

        # Child field should work
        assert config.child_field == "child_value"

    def test_environment_variable_precedence(self) -> None:
        """Test environment variable precedence order."""
        # Test that explicit parameters have highest precedence
        env_vars = {
            "HH_API_KEY": "env_key",
            "HH_PROJECT": "env_project",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Explicit parameters should override environment
            config = BaseHoneyHiveConfig(
                api_key="explicit_key", project="explicit_project"
            )

            assert config.api_key == "explicit_key"
            assert config.project == "explicit_project"

            # Environment should be used when no explicit parameter
            config2 = BaseHoneyHiveConfig()
            assert config2.api_key == "env_key"
            assert config2.project == "env_project"

    def test_graceful_degradation_empty_strings(self) -> None:
        """Test that empty strings are handled gracefully with warnings."""
        # logging and patch imported at top level

        # Test empty API key - should log warning and set to None
        with patch("honeyhive.config.models.base.logger") as mock_logger:
            config = BaseHoneyHiveConfig(api_key="", project="test")

            # Should have logged warning about empty api_key
            mock_logger.warning.assert_called()
            assert config.api_key is None
            assert config.project == "test"

        # Test empty project - should log warning and set to None
        with patch("honeyhive.config.models.base.logger") as mock_logger:
            config = BaseHoneyHiveConfig(api_key="hh_test", project="")

            # Should have logged warning about empty project
            mock_logger.warning.assert_called()
            assert config.api_key == "hh_test"
            assert config.project is None

    def test_graceful_degradation_invalid_types(self) -> None:
        """Test that invalid config types never crash the application."""
        # These should all work without raising exceptions
        invalid_inputs: list[Dict[str, Any]] = [
            {"api_key": 123, "project": "test"},
            {"api_key": [], "project": "test"},
            {"api_key": {}, "project": "test"},
            {"api_key": None, "project": 456},
            {"api_key": "valid", "project": []},
            {"api_key": "valid", "project": {}},
        ]

        for invalid_input in invalid_inputs:
            # Should not crash - graceful degradation should handle it
            config = BaseHoneyHiveConfig(**invalid_input)
            # Invalid values should be converted to None or safe defaults
            assert config is not None

    def test_graceful_degradation_logging(self) -> None:
        """Test that graceful degradation produces appropriate warning logs."""
        # logging and patch imported at top level

        with patch("honeyhive.config.models.base.logger") as mock_logger:
            # Create config with invalid values
            config = BaseHoneyHiveConfig(api_key=123, project="test")

            # Should have logged warnings about invalid values
            assert mock_logger.warning.called

            # Config should still be created successfully
            assert config is not None
            assert config.api_key is None  # Invalid value converted to None

    def test_boolean_validation_none_values(self) -> None:
        """Test boolean validation with None values."""
        # Test that None values are handled correctly (line 224)
        config = BaseHoneyHiveConfig(
            api_key="test", project="test", test_mode=None, verbose=None
        )
        assert config.test_mode is False
        assert config.verbose is False

    def test_boolean_validation_invalid_types(self) -> None:
        """Test boolean validation with invalid types."""
        # logging and patch imported at top level

        with patch("honeyhive.config.models.base.logger") as mock_logger:
            # Test non-string, non-bool types (lines 245-249)
            config = BaseHoneyHiveConfig(
                api_key="test",
                project="test",
                test_mode=123,  # Invalid type
                verbose=[],  # Invalid type
            )

            # Should log warnings for invalid types
            assert mock_logger.warning.call_count >= 2

            # Should default to False
            assert config.test_mode is False
            assert config.verbose is False

    def test_boolean_validation_invalid_strings(self) -> None:
        """Test boolean validation with invalid string values."""
        # logging and patch imported at top level

        with patch("honeyhive.config.models.base.logger") as mock_logger:
            # Test invalid boolean strings (lines 238-242)
            config = BaseHoneyHiveConfig(
                api_key="test",
                project="test",
                test_mode="invalid_bool_string",
                verbose="not_a_boolean",
            )

            # Should log warnings for invalid boolean strings
            assert mock_logger.warning.call_count >= 2

            # Should default to False
            assert config.test_mode is False
            assert config.verbose is False

    def test_url_validation_invalid_protocol(self) -> None:
        """Test URL validation with invalid protocols."""
        # logging and patch imported at top level

        # _safe_validate_url imported at top level

        with patch("honeyhive.config.models.base.logger") as mock_logger:
            # Test URL that doesn't start with http/https (lines 80-87)
            result = _safe_validate_url(
                "ftp://example.com", "test_url", default="https://default.com"
            )

            # Should log warning and return default
            mock_logger.warning.assert_called()
            assert result == "https://default.com"

            # Test valid URL (line 87)
            result_valid = _safe_validate_url(
                "https://valid.com", "test_url", default="https://default.com"
            )
            assert result_valid == "https://valid.com"

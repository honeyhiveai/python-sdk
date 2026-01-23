"""Unit tests for honeyhive.config.models.experiment.

This module contains comprehensive unit tests for experiment configuration models
including ExperimentConfig class and related utility functions.
"""

# pylint: disable=too-many-lines
# Justification: Comprehensive unit test coverage requires extensive test cases

# pylint: disable=redefined-outer-name
# Justification: Pytest fixture pattern requires parameter shadowing

# pylint: disable=protected-access
# Justification: Unit tests need to verify private method behavior

import json
import logging
import os
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

from honeyhive.config.models.experiment import ExperimentConfig, _get_env_json


class TestGetEnvJson:
    """Test suite for _get_env_json utility function."""

    def test_get_env_json_with_valid_json_string(self) -> None:
        """Test _get_env_json with valid JSON string from environment."""
        # Arrange
        test_key: str = "TEST_JSON_KEY"
        test_value: str = '{"model_type": "gpt-4", "temperature": 0.7}'
        expected_result: Dict[str, Any] = {"model_type": "gpt-4", "temperature": 0.7}

        with patch.object(os, "getenv", return_value=test_value):
            # Act
            result: Optional[Dict[str, Any]] = _get_env_json(test_key)

            # Assert
            assert result == expected_result

    def test_get_env_json_with_empty_environment_variable(self) -> None:
        """Test _get_env_json with empty environment variable returns default."""
        # Arrange
        test_key: str = "EMPTY_JSON_KEY"
        default_value: Dict[str, str] = {"default": "value"}

        with patch.object(os, "getenv", return_value=None):
            # Act
            result: Optional[Dict[str, Any]] = _get_env_json(test_key, default_value)

            # Assert
            assert result == default_value

    def test_get_env_json_with_no_default_returns_none(self) -> None:
        """Test _get_env_json with no environment variable and no default."""
        # Arrange
        test_key: str = "MISSING_JSON_KEY"

        with patch.object(os, "getenv", return_value=None):
            # Act
            result: Optional[Dict[str, Any]] = _get_env_json(test_key)

            # Assert
            assert result is None

    def test_get_env_json_with_invalid_json_returns_default(self) -> None:
        """Test _get_env_json with invalid JSON string returns default."""
        # Arrange
        test_key: str = "INVALID_JSON_KEY"
        invalid_json: str = '{"invalid": json}'
        default_value: Dict[str, str] = {"fallback": "value"}

        with patch.object(os, "getenv", return_value=invalid_json):
            # Act
            result: Optional[Dict[str, Any]] = _get_env_json(test_key, default_value)

            # Assert
            assert result == default_value

    def test_get_env_json_with_non_dict_json_returns_default(self) -> None:
        """Test _get_env_json with non-dict JSON (list/string) returns default."""
        # Arrange
        test_key: str = "NON_DICT_JSON_KEY"
        non_dict_json: str = '["item1", "item2", "item3"]'
        default_value: Dict[str, str] = {"type": "dict"}

        with patch.object(os, "getenv", return_value=non_dict_json):
            # Act
            result: Optional[Dict[str, Any]] = _get_env_json(test_key, default_value)

            # Assert
            assert result == default_value

    def test_get_env_json_with_json_decode_error_returns_default(self) -> None:
        """Test _get_env_json handles JSONDecodeError gracefully."""
        # Arrange
        test_key: str = "MALFORMED_JSON_KEY"
        malformed_json: str = '{"key": value}'  # Missing quotes around value

        with patch.object(os, "getenv", return_value=malformed_json):
            # Act
            result: Optional[Dict[str, Any]] = _get_env_json(test_key)

            # Assert
            assert result is None

    def test_get_env_json_with_type_error_returns_default(self) -> None:
        """Test _get_env_json handles TypeError gracefully."""
        # Arrange
        test_key: str = "TYPE_ERROR_KEY"

        with patch.object(os, "getenv", return_value="valid_string"):
            with patch.object(json, "loads", side_effect=TypeError("Type error")):
                # Act
                result: Optional[Dict[str, Any]] = _get_env_json(test_key)

                # Assert
                assert result is None


class TestExperimentConfig:
    """Test suite for ExperimentConfig class."""

    def test_experiment_config_initialization_with_direct_parameters(self) -> None:
        """Test ExperimentConfig initialization with direct parameters."""
        # Arrange
        test_data: Dict[str, Any] = {
            "experiment_id": "exp_12345",
            "experiment_name": "model-comparison",
            "experiment_variant": "baseline",
            "experiment_group": "control",
            "experiment_metadata": {"model_type": "gpt-4", "temperature": 0.7},
        }

        # Act
        config: ExperimentConfig = ExperimentConfig(**test_data)

        # Assert
        assert config.experiment_id == "exp_12345"
        assert config.experiment_name == "model-comparison"
        assert config.experiment_variant == "baseline"
        assert config.experiment_group == "control"
        assert config.experiment_metadata == {"model_type": "gpt-4", "temperature": 0.7}

    def test_experiment_config_initialization_with_environment_variables(self) -> None:
        """Test ExperimentConfig initialization with environment variable fallbacks."""
        # Arrange
        env_vars: Dict[str, str] = {
            "HH_EXPERIMENT_ID": "env_exp_123",
            "HH_EXPERIMENT_NAME": "env_experiment",
            "HH_EXPERIMENT_VARIANT": "env_variant",
            "HH_EXPERIMENT_GROUP": "env_group",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_id == "env_exp_123"
            assert config.experiment_name == "env_experiment"
            assert config.experiment_variant == "env_variant"
            assert config.experiment_group == "env_group"

    def test_experiment_config_initialization_with_mlflow_fallbacks(self) -> None:
        """Test ExperimentConfig initialization with MLflow env fallbacks."""
        # Arrange
        env_vars: Dict[str, str] = {
            "MLFLOW_EXPERIMENT_ID": "mlflow_exp_456",
            "MLFLOW_EXPERIMENT_NAME": "mlflow_experiment",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_id == "mlflow_exp_456"
            assert config.experiment_name == "mlflow_experiment"

    def test_experiment_config_initialization_with_wandb_fallbacks(self) -> None:
        """Test ExperimentConfig initialization with W&B fallbacks."""
        # Arrange
        env_vars: Dict[str, str] = {
            "WANDB_RUN_ID": "wandb_run_789",
            "WANDB_PROJECT": "wandb_project",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_id == "wandb_run_789"
            assert config.experiment_name == "wandb_project"

    def test_experiment_config_initialization_with_comet_fallbacks(self) -> None:
        """Test ExperimentConfig initialization with Comet ML fallbacks."""
        # Arrange
        env_vars: Dict[str, str] = {
            "COMET_EXPERIMENT_KEY": "comet_key_abc",
            "COMET_PROJECT_NAME": "comet_project",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_id == "comet_key_abc"
            assert config.experiment_name == "comet_project"

    def test_experiment_config_initialization_with_generic_fallbacks(self) -> None:
        """Test ExperimentConfig initialization with generic env fallbacks."""
        # Arrange
        env_vars: Dict[str, str] = {
            "EXPERIMENT_ID": "generic_exp_999",
            "EXPERIMENT_NAME": "generic_experiment",
            "VARIANT": "generic_variant",
            "GROUP": "generic_group",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_id == "generic_exp_999"
            assert config.experiment_name == "generic_experiment"
            assert config.experiment_variant == "generic_variant"
            assert config.experiment_group == "generic_group"

    def test_experiment_config_initialization_with_ab_test_fallbacks(self) -> None:
        """Test ExperimentConfig initialization with A/B test env fallbacks."""
        # Arrange
        env_vars: Dict[str, str] = {
            "AB_TEST_VARIANT": "ab_variant_a",
            "AB_TEST_GROUP": "ab_group_1",
            "TREATMENT": "treatment_x",
            "COHORT": "cohort_y",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_variant == "ab_variant_a"
            assert config.experiment_group == "ab_group_1"

    def test_experiment_config_initialization_with_metadata_fallbacks(self) -> None:
        """Test ExperimentConfig initialization with metadata env fallbacks."""
        # Arrange
        test_metadata: Dict[str, Any] = {"model": "gpt-4", "version": "1.0"}

        with patch(
            "honeyhive.config.models.experiment._get_env_json"
        ) as mock_get_env_json:
            mock_get_env_json.return_value = test_metadata

            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_metadata == test_metadata
            mock_get_env_json.assert_called()

    def test_experiment_config_direct_data_overrides_environment(self) -> None:
        """Test that direct parameters override environment variables."""
        # Arrange
        env_vars: Dict[str, str] = {
            "HH_EXPERIMENT_ID": "env_id",
            "HH_EXPERIMENT_NAME": "env_name",
        }
        direct_data: Dict[str, str] = {
            "experiment_id": "direct_id",
            "experiment_name": "direct_name",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Act
            config: ExperimentConfig = ExperimentConfig(**direct_data)

            # Assert
            assert config.experiment_id == "direct_id"
            assert config.experiment_name == "direct_name"

    def test_experiment_config_initialization_with_no_environment_variables(
        self,
    ) -> None:
        """Test ExperimentConfig initialization with no environment variables."""
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_id is None
            assert config.experiment_name is None
            assert config.experiment_variant is None
            assert config.experiment_group is None
            assert config.experiment_metadata is None

    def test_validate_experiment_strings_with_valid_string(self) -> None:
        """Test validate_experiment_strings with valid string input."""
        # Arrange
        test_string: str = "valid_experiment_id"

        # Act
        result: Optional[str] = ExperimentConfig.validate_experiment_strings(
            test_string
        )

        # Assert
        assert result == "valid_experiment_id"

    def test_validate_experiment_strings_with_none_input(self) -> None:
        """Test validate_experiment_strings with None input returns None."""
        # Act
        result: Optional[str] = ExperimentConfig.validate_experiment_strings(None)

        # Assert
        assert result is None

    def test_validate_experiment_strings_with_empty_string(self) -> None:
        """Test validate_experiment_strings with empty string."""
        # Act
        result: Optional[str] = ExperimentConfig.validate_experiment_strings("")

        # Assert
        assert result is None

    def test_validate_experiment_strings_with_whitespace_string(self) -> None:
        """Test validate_experiment_strings with whitespace-only string."""
        # Act
        result: Optional[str] = ExperimentConfig.validate_experiment_strings("   ")

        # Assert
        assert result is None

    def test_validate_experiment_metadata_with_valid_dict(self) -> None:
        """Test validate_experiment_metadata with valid dictionary input."""
        # Arrange
        test_metadata: Dict[str, Any] = {
            "model_type": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 100,
        }

        # Act
        result: Optional[Dict[str, Any]] = (
            ExperimentConfig.validate_experiment_metadata(test_metadata)
        )

        # Assert
        assert result == test_metadata

    def test_validate_experiment_metadata_with_none_input(self) -> None:
        """Test validate_experiment_metadata with None input returns None."""
        # Act
        result: Optional[Dict[str, Any]] = (
            ExperimentConfig.validate_experiment_metadata(None)
        )

        # Assert
        assert result is None

    def test_validate_experiment_metadata_with_invalid_type_logs_warning(self) -> None:
        """Test validate_experiment_metadata with invalid type logs warning."""
        # Arrange
        invalid_metadata: str = "not_a_dict"

        with patch.object(logging, "getLogger") as mock_get_logger:
            mock_logger: Mock = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            result: Optional[
                Dict[str, Any]
            ] = ExperimentConfig.validate_experiment_metadata(
                invalid_metadata  # type: ignore[arg-type]
            )

            # Assert
            assert result is None
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args
            assert (
                "Invalid experiment_metadata: expected dict, got %s. Using None."
                in warning_call[0][0]
            )

    def test_validate_experiment_metadata_with_invalid_keys_filters_them(self) -> None:
        """Test validate_experiment_metadata filters out non-string keys."""
        # Arrange
        metadata_with_invalid_keys: Dict[Any, Any] = {
            "valid_key": "valid_value",
            123: "numeric_key",
            None: "none_key",
            "another_valid": "another_value",
        }
        expected_result: Dict[str, Any] = {
            "valid_key": "valid_value",
            "another_valid": "another_value",
        }

        with patch.object(logging, "getLogger") as mock_get_logger:
            mock_logger: Mock = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            result: Optional[Dict[str, Any]] = (
                ExperimentConfig.validate_experiment_metadata(
                    metadata_with_invalid_keys
                )
            )

            # Assert
            assert result == expected_result
            assert mock_logger.warning.call_count == 2  # Two invalid keys

    def test_validate_experiment_metadata_with_all_invalid_keys_returns_none(
        self,
    ) -> None:
        """Test validate_experiment_metadata returns None when all keys are invalid."""
        # Arrange
        metadata_all_invalid_keys: Dict[Any, Any] = {
            123: "numeric_key",
            None: "none_key",
            45.6: "float_key",
        }

        with patch.object(logging, "getLogger") as mock_get_logger:
            mock_logger: Mock = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            result: Optional[Dict[str, Any]] = (
                ExperimentConfig.validate_experiment_metadata(metadata_all_invalid_keys)
            )

            # Assert
            assert result is None
            assert mock_logger.warning.call_count == 3  # Three invalid keys

    def test_experiment_config_field_validation_integration(self) -> None:
        """Test ExperimentConfig field validation integration with Pydantic."""
        # Arrange
        test_data: Dict[str, Any] = {
            "experiment_id": "  valid_id  ",  # Should be validated
            "experiment_name": "",  # Should become None
            "experiment_variant": None,  # Should remain None
            "experiment_metadata": {"key": "value"},  # Should be validated
        }

        # Act
        config: ExperimentConfig = ExperimentConfig(**test_data)

        # Assert
        assert config.experiment_id == "valid_id"  # Trimmed by _safe_validate_string
        assert config.experiment_name is None  # Empty string converted to None
        assert config.experiment_variant is None
        assert config.experiment_metadata == {"key": "value"}

    def test_experiment_config_model_config_settings(self) -> None:
        """Test ExperimentConfig model configuration settings."""
        # Arrange & Act
        config: ExperimentConfig = ExperimentConfig()

        # Assert
        assert config.model_config["env_prefix"] == ""
        assert config.model_config["validate_assignment"] is True
        assert config.model_config["extra"] == "forbid"
        assert config.model_config["case_sensitive"] is False

    def test_experiment_config_with_mixed_environment_priority(self) -> None:
        """Test ExperimentConfig env variable priority (HH_ > generic > platform)."""
        # Arrange
        env_vars: Dict[str, str] = {
            "HH_EXPERIMENT_ID": "honeyhive_id",
            "EXPERIMENT_ID": "generic_id",
            "MLFLOW_EXPERIMENT_ID": "mlflow_id",
            "WANDB_RUN_ID": "wandb_id",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_id == "honeyhive_id"  # HH_ prefix takes priority

    def test_experiment_config_environment_fallback_chain(self) -> None:
        """Test ExperimentConfig environment variable fallback chain works correctly."""
        # Arrange - Only set lower priority variables
        env_vars: Dict[str, str] = {
            "MLFLOW_EXPERIMENT_ID": "mlflow_fallback",
            "WANDB_PROJECT": "wandb_fallback",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Act
            config: ExperimentConfig = ExperimentConfig()

            # Assert
            assert config.experiment_id == "mlflow_fallback"
            assert config.experiment_name == "wandb_fallback"

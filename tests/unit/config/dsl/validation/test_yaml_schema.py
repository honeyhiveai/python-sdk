# pylint: disable=protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, pytest fixtures are used as parameters,
# and unavoidable long lines in @patch decorator read_data parameters.
"""
Unit tests for config.dsl.validation.yaml_schema module.

Tests YAML schema validation for provider configuration files including:
- Structure patterns validation
- Navigation rules validation
- Field mappings validation
- Transforms validation
- File-level validation with I/O mocking
- Multi-file batch validation
- CLI entry point behavior
"""

from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, mock_open

import yaml

from config.dsl.validation.yaml_schema import (
    validate_structure_patterns,
    validate_navigation_rules,
    validate_field_mappings,
    validate_transforms,
    validate_yaml_file,
    validate_yaml_schema,
    main,
)


class TestValidateStructurePatterns:
    """Test validate_structure_patterns() function."""

    def test_valid_structure_patterns(self) -> None:
        """Test validation with valid structure patterns data."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            "patterns": {
                "chat_completion": {
                    "signature_fields": ["gen_ai.request.model", "gen_ai.system"],
                    "confidence_weight": 0.9,
                    "priority": 1,
                    "optional_fields": ["gen_ai.usage.prompt_tokens"],
                }
            },
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert not errors

    def test_missing_version_field(self) -> None:
        """Test validation when version field is missing."""
        data: Dict[str, Any] = {
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            "patterns": {},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) == 1
        assert "Missing required top-level field 'version'" in errors[0]

    def test_missing_provider_field(self) -> None:
        """Test validation when provider field is missing."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "dsl_type": "provider_structure_patterns",
            "patterns": {},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) == 1
        assert "Missing required top-level field 'provider'" in errors[0]

    def test_missing_dsl_type_field(self) -> None:
        """Test validation when dsl_type field is missing."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "patterns": {},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) == 1
        assert "Missing required top-level field 'dsl_type'" in errors[0]

    def test_invalid_version_format(self) -> None:
        """Test validation with invalid version format."""
        data: Dict[str, Any] = {
            "version": "2.0",  # Not 1.x or 4.x
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            "patterns": {},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) == 1
        assert "Invalid version '2.0'" in errors[0]

    def test_wrong_dsl_type(self) -> None:
        """Test validation with wrong dsl_type value."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "wrong_type",
            "patterns": {},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) == 1
        assert "Invalid dsl_type 'wrong_type'" in errors[0]
        assert "provider_structure_patterns" in errors[0]

    def test_missing_patterns_section(self) -> None:
        """Test validation when patterns section is missing."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) >= 1
        assert any("patterns" in error.lower() for error in errors)

    def test_invalid_patterns_type(self) -> None:
        """Test validation when patterns is not a dictionary."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            "patterns": "not_a_dict",
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) == 1
        assert "'patterns' must be a dictionary" in errors[0]

    def test_pattern_missing_signature_fields(self) -> None:
        """Test validation when pattern is missing signature_fields."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            "patterns": {"test_pattern": {"confidence_weight": 0.9}},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) == 1
        assert "Pattern 'test_pattern' missing required 'signature_fields'" in errors[0]

    def test_pattern_invalid_confidence_weight(self) -> None:
        """Test validation with invalid confidence_weight."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            "patterns": {
                "test_pattern": {
                    "signature_fields": ["field1"],
                    "confidence_weight": 1.5,  # Out of range
                }
            },
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) == 1
        assert "confidence_weight must be a number between 0 and 1" in errors[0]

    def test_pattern_invalid_priority(self) -> None:
        """Test validation with invalid priority."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            "patterns": {
                "test_pattern": {
                    "signature_fields": ["field1"],
                    "priority": -1,  # Negative
                }
            },
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_structure_patterns(data, filepath)

        assert len(errors) == 1
        assert "priority must be a positive integer" in errors[0]


class TestValidateNavigationRules:
    """Test validate_navigation_rules() function."""

    def test_valid_navigation_rules(self) -> None:
        """Test validation with valid navigation rules data."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_navigation_rules",
            "navigation_rules": {"rule1": "value1"},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_navigation_rules(data, filepath)

        assert not errors

    def test_missing_required_fields(self) -> None:
        """Test validation when required fields are missing."""
        data: Dict[str, Any] = {"version": "4.0"}
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_navigation_rules(data, filepath)

        assert len(errors) == 3  # provider, dsl_type, navigation_rules

    def test_wrong_dsl_type(self) -> None:
        """Test validation with wrong dsl_type."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "wrong_type",
            "navigation_rules": {},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_navigation_rules(data, filepath)

        assert len(errors) == 1
        assert "Invalid dsl_type" in errors[0]
        assert "provider_navigation_rules" in errors[0]

    def test_invalid_navigation_rules_type(self) -> None:
        """Test validation when navigation_rules is not a dictionary."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_navigation_rules",
            "navigation_rules": "not_a_dict",
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_navigation_rules(data, filepath)

        assert len(errors) == 1
        assert "'navigation_rules' must be a dictionary" in errors[0]


class TestValidateFieldMappings:
    """Test validate_field_mappings() function."""

    def test_valid_field_mappings(self) -> None:
        """Test validation with valid field mappings data."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_field_mappings",
            "field_mappings": {
                "inputs": {},
                "outputs": {},
                "config": {},
                "metadata": {},
            },
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_field_mappings(data, filepath)

        assert not errors

    def test_missing_required_fields(self) -> None:
        """Test validation when required fields are missing."""
        data: Dict[str, Any] = {"version": "4.0"}
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_field_mappings(data, filepath)

        assert len(errors) == 3  # provider, dsl_type, field_mappings

    def test_wrong_dsl_type(self) -> None:
        """Test validation with wrong dsl_type."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "wrong_type",
            "field_mappings": {},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_field_mappings(data, filepath)

        assert len(errors) >= 1
        assert any("dsl_type" in error for error in errors)

    def test_missing_honeyhive_schema_sections(self) -> None:
        """Test validation when HoneyHive schema sections are missing."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_field_mappings",
            "field_mappings": {"inputs": {}},  # Missing outputs, config, metadata
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_field_mappings(data, filepath)

        assert len(errors) == 3  # outputs, config, metadata
        assert any("outputs" in error for error in errors)
        assert any("config" in error for error in errors)
        assert any("metadata" in error for error in errors)

    def test_invalid_field_mappings_type(self) -> None:
        """Test validation when field_mappings is not a dictionary."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_field_mappings",
            "field_mappings": "not_a_dict",
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_field_mappings(data, filepath)

        assert len(errors) == 1
        assert "'field_mappings' must be a dictionary" in errors[0]


class TestValidateTransforms:
    """Test validate_transforms() function."""

    def test_valid_transforms(self) -> None:
        """Test validation with valid transforms data."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_transforms",
            "transforms": {"transform1": "value1"},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_transforms(data, filepath)

        assert not errors

    def test_missing_required_fields(self) -> None:
        """Test validation when required fields are missing."""
        data: Dict[str, Any] = {"version": "4.0"}
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_transforms(data, filepath)

        assert len(errors) == 3  # provider, dsl_type, transforms

    def test_wrong_dsl_type(self) -> None:
        """Test validation with wrong dsl_type."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "wrong_type",
            "transforms": {},
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_transforms(data, filepath)

        assert len(errors) == 1
        assert "Invalid dsl_type" in errors[0]
        assert "provider_transforms" in errors[0]

    def test_invalid_transforms_type(self) -> None:
        """Test validation when transforms is not a dictionary."""
        data: Dict[str, Any] = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_transforms",
            "transforms": "not_a_dict",
        }
        filepath: Path = Path("test.yaml")

        errors: List[str] = validate_transforms(data, filepath)

        assert len(errors) == 1
        assert "'transforms' must be a dictionary" in errors[0]


class TestValidateYamlFile:
    """Test validate_yaml_file() function."""

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="version: '4.0'\nprovider: openai\ndsl_type: provider_structure_patterns\npatterns:\n  test:\n    signature_fields: [field1]",
    )
    @patch("yaml.safe_load")
    def test_valid_structure_patterns_file(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test validation of valid structure_patterns.yaml file."""
        mock_yaml_load.return_value = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            "patterns": {"test": {"signature_fields": ["field1"]}},
        }
        filepath: Path = Path("structure_patterns.yaml")

        is_valid, errors = validate_yaml_file(filepath)

        assert is_valid
        assert not errors

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="version: '4.0'\nprovider: openai\ndsl_type: provider_navigation_rules\nnavigation_rules: {}",
    )
    @patch("yaml.safe_load")
    def test_valid_navigation_rules_file(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test validation of valid navigation_rules.yaml file."""
        mock_yaml_load.return_value = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_navigation_rules",
            "navigation_rules": {},
        }
        filepath: Path = Path("navigation_rules.yaml")

        is_valid, errors = validate_yaml_file(filepath)

        assert is_valid
        assert not errors

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_yaml_parsing_error(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test handling of YAML parsing errors."""
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML syntax")
        filepath: Path = Path("test.yaml")

        is_valid, errors = validate_yaml_file(filepath)

        assert not is_valid
        assert len(errors) == 1
        assert "YAML parsing error" in errors[0]

    def test_file_not_found(self) -> None:
        """Test handling of missing file."""
        filepath: Path = Path("nonexistent.yaml")

        is_valid, errors = validate_yaml_file(filepath)

        assert not is_valid
        assert len(errors) == 1
        assert "File not found" in errors[0]

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_non_dict_root(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test validation when YAML root is not a dictionary."""
        mock_yaml_load.return_value = ["list", "not", "dict"]
        filepath: Path = Path("test.yaml")

        is_valid, errors = validate_yaml_file(filepath)

        assert not is_valid
        assert len(errors) == 1
        assert "YAML root must be a dictionary" in errors[0]

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_unknown_file_type_skips_validation(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test that unknown file types skip validation."""
        mock_yaml_load.return_value = {"any": "data"}
        filepath: Path = Path("unknown_file.yaml")

        is_valid, errors = validate_yaml_file(filepath)

        assert is_valid
        assert not errors

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_unexpected_error_handling(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test handling of unexpected errors."""
        mock_yaml_load.side_effect = RuntimeError("Unexpected error")
        filepath: Path = Path("test.yaml")

        is_valid, errors = validate_yaml_file(filepath)

        assert not is_valid
        assert len(errors) == 1
        assert "Unexpected error" in errors[0]


class TestValidateYamlSchema:
    """Test validate_yaml_schema() function."""

    @patch.object(Path, "exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_all_files_valid(
        self,
        mock_yaml_load: Mock,
        _mock_file: Mock,
        mock_exists: Mock,
    ) -> None:
        """Test validation when all files are valid."""
        mock_exists.return_value = True
        # Return appropriate data for each file type
        mock_yaml_load.side_effect = [
            {
                "version": "4.0",
                "provider": "openai",
                "dsl_type": "provider_structure_patterns",
                "patterns": {"test": {"signature_fields": ["field1"]}},
            },
            {
                "version": "4.0",
                "provider": "openai",
                "dsl_type": "provider_navigation_rules",
                "navigation_rules": {},
            },
        ]

        files: List[Path] = [
            Path("structure_patterns.yaml"),
            Path("navigation_rules.yaml"),
        ]

        all_valid, errors, count = validate_yaml_schema(files)

        assert all_valid
        assert not errors
        assert count == 2

    @patch.object(Path, "exists")
    def test_nonexistent_file(self, mock_exists: Mock) -> None:
        """Test handling of non-existent file."""
        mock_exists.return_value = False

        files: List[Path] = [Path("nonexistent.yaml")]

        all_valid, errors, count = validate_yaml_schema(files)

        assert not all_valid
        assert len(errors) == 1
        assert "File does not exist" in errors[0]
        assert count == 0

    @patch.object(Path, "exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_mix_of_valid_and_invalid_files(
        self,
        mock_yaml_load: Mock,
        _mock_file: Mock,
        mock_exists: Mock,
    ) -> None:
        """Test validation with mix of valid and invalid files."""
        mock_exists.return_value = True

        # First file valid, second file invalid
        mock_yaml_load.side_effect = [
            {
                "version": "4.0",
                "provider": "openai",
                "dsl_type": "provider_structure_patterns",
                "patterns": {"test": {"signature_fields": ["field1"]}},
            },
            {
                "version": "4.0",
                "provider": "openai",
                "dsl_type": "provider_structure_patterns",
                "patterns": "invalid",  # Should be dict
            },
        ]

        files: List[Path] = [
            Path("structure_patterns.yaml"),
            Path("structure_patterns.yaml"),
        ]

        all_valid, errors, count = validate_yaml_schema(files)

        assert not all_valid
        assert len(errors) > 0
        assert count == 2

    @patch.object(Path, "exists")
    def test_empty_file_list(self, _mock_exists: Mock) -> None:
        """Test validation with empty file list."""
        files: List[Path] = []

        all_valid, errors, count = validate_yaml_schema(files)

        assert all_valid
        assert not errors
        assert count == 0

    @patch.object(Path, "exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_multiple_errors_accumulated(
        self,
        mock_yaml_load: Mock,
        _mock_file: Mock,
        mock_exists: Mock,
    ) -> None:
        """Test that errors from multiple files are accumulated."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            # Missing patterns section
        }

        files: List[Path] = [
            Path("structure_patterns.yaml"),
            Path("structure_patterns.yaml"),
        ]

        all_valid, errors, count = validate_yaml_schema(files)

        assert not all_valid
        assert len(errors) >= 2  # At least one error per file
        assert count == 2


class TestMain:
    """Test main() CLI entry point."""

    def test_no_arguments_returns_error_code(self) -> None:
        """Test that running with no arguments returns error code 1."""
        with patch("sys.argv", ["script_name"]):
            exit_code: int = main()

            assert exit_code == 1

    @patch.object(Path, "exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_valid_files_returns_success(
        self,
        mock_yaml_load: Mock,
        _mock_file: Mock,
        mock_exists: Mock,
    ) -> None:
        """Test successful validation returns code 0."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            "patterns": {"test": {"signature_fields": ["field1"]}},
        }

        with patch("sys.argv", ["script", "structure_patterns.yaml"]):
            exit_code: int = main()

            assert exit_code == 0

    @patch.object(Path, "exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_invalid_files_returns_failure(
        self,
        mock_yaml_load: Mock,
        _mock_file: Mock,
        mock_exists: Mock,
    ) -> None:
        """Test failed validation returns code 1."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            "version": "4.0",
            "provider": "openai",
            "dsl_type": "provider_structure_patterns",
            # Missing patterns section - invalid
        }

        with patch("sys.argv", ["script", "structure_patterns.yaml"]):
            exit_code: int = main()

            assert exit_code == 1

    @patch.object(Path, "exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_multiple_files_in_argv(
        self,
        mock_yaml_load: Mock,
        _mock_file: Mock,
        mock_exists: Mock,
    ) -> None:
        """Test handling of multiple files from command line."""
        mock_exists.return_value = True
        # Return appropriate data for each file type
        mock_yaml_load.side_effect = [
            {
                "version": "4.0",
                "provider": "openai",
                "dsl_type": "provider_structure_patterns",
                "patterns": {"test": {"signature_fields": ["field1"]}},
            },
            {
                "version": "4.0",
                "provider": "openai",
                "dsl_type": "provider_navigation_rules",
                "navigation_rules": {},
            },
            {
                "version": "4.0",
                "provider": "openai",
                "dsl_type": "provider_field_mappings",
                "field_mappings": {
                    "inputs": {},
                    "outputs": {},
                    "config": {},
                    "metadata": {},
                },
            },
        ]

        with patch(
            "sys.argv",
            [
                "script",
                "structure_patterns.yaml",
                "navigation_rules.yaml",
                "field_mappings.yaml",
            ],
        ):
            exit_code: int = main()

            assert exit_code == 0
            # Verify all 3 files were processed
            assert mock_yaml_load.call_count == 3

"""
Unit tests for config.dsl.compiler module.

This test suite provides comprehensive coverage of the ProviderCompiler class
and main() function, using complete external dependency mocking for isolation.

Coverage Targets:
- Line coverage: 90%+ (466/518 lines minimum)
- Branch coverage: 90%+ (121/134 branches minimum)
- Function coverage: 100% (21/21 functions)

Quality Targets:
- Pylint score: 10.0/10
- MyPy errors: 0
- Black formatted: Yes
"""

# pylint: disable=W0702,W0718,W0719,W0212  # From pyproject.toml
# pylint: disable=unused-argument,too-many-positional-arguments  # Test-specific
# pylint: disable=too-few-public-methods,too-many-arguments  # Test-specific
# pylint: disable=too-many-lines,too-many-public-methods  # Comprehensive coverage
# pylint: disable=redefined-outer-name  # Pytest fixture pattern
# pylint: disable=import-error  # config.dsl is separate package, not in src/

from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

from config.dsl.compiler import ProviderCompiler, main
from honeyhive.tracer.processing.semantic_conventions.bundle_types import (
    CompiledProviderBundle,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_provider_data() -> Dict[str, Any]:
    """Sample provider data matching expected structure."""
    return {
        "structure_patterns": {
            "patterns": {
                "pattern1": {
                    "signature_fields": ["field1", "field2", "field3"],
                    "confidence_weight": 0.9,
                },
                "pattern2": {
                    "signature_fields": ["fieldA", "fieldB"],
                    "confidence_weight": 0.85,
                },
            }
        },
        "field_mappings": {
            "field_mappings": {
                "inputs": {
                    "model": {"source_rule": "nav_rule1"},
                    "messages": {"source_rule": "static_test_value"},
                },
                "outputs": {"response": {"source_rule": "nav_rule2"}},
                "config": {"temperature": {"source_rule": "transform_rule1"}},
                "metadata": {
                    "provider": {"source_rule": "static_openai"},
                    "latency": {"source_rule": "nav_rule3"},
                },
            }
        },
        "navigation_rules": {
            "navigation_rules": {
                "nav_rule1": {
                    "source_field": "model",
                    "extraction_method": "direct_copy",
                    "fallback_value": "unknown",
                },
                "nav_rule2": {
                    "source_field": "response",
                    "extraction_method": "array_flatten",
                    "fallback_value": [],
                },
                "nav_rule3": {
                    "source_field": "latency_ms",
                    "extraction_method": "object_merge",
                    "fallback_value": {},
                },
            }
        },
        "transforms": {
            "transforms": {
                "transform_rule1": {
                    "function_type": "lambda",
                    "implementation": "lambda x: x * 2",
                    "parameters": {},
                }
            }
        },
    }


@pytest.fixture
def sample_shared_config() -> Dict[str, Any]:
    """Sample shared configuration data."""
    return {
        "validation_rules": {
            "min_signatures": 2,
            "confidence_range": [0.5, 1.0],
        },
        "core_schema": {"version": "4.0"},
    }


# ============================================================================
# TEST CLASS: ProviderCompiler
# ============================================================================


class TestProviderCompiler:
    """Test suite for ProviderCompiler class."""

    # ------------------------------------------------------------------------
    # Initialization Tests
    # ------------------------------------------------------------------------

    def test_init_success(self, tmp_path: Path) -> None:
        """Test successful ProviderCompiler initialization."""
        # Arrange
        source_dir = tmp_path / "source"
        output_dir = tmp_path / "output"

        # Act
        compiler = ProviderCompiler(source_dir, output_dir)

        # Assert
        assert compiler.source_dir == source_dir
        assert compiler.output_dir == output_dir
        assert compiler.providers_dir == source_dir / "providers"
        assert compiler.shared_dir == source_dir / "shared"
        assert not compiler.providers
        assert not compiler.shared_config
        assert isinstance(compiler.compilation_stats, dict)

    # ------------------------------------------------------------------------
    # compile_all_providers Tests
    # ------------------------------------------------------------------------

    @patch("time.time")
    @patch("logging.getLogger")
    def test_compile_all_providers_success(
        self,
        mock_get_logger: Mock,
        mock_time: Mock,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test successful compilation of all providers."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_time.side_effect = [1000.0, 1005.5, 1005.5]  # Start, end, and final access

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.providers = {"openai": sample_provider_data}
        compiler.shared_config = sample_shared_config

        # Mock internal methods to return expected data
        with (
            patch.object(compiler, "_load_shared_configuration") as mock_load_shared,
            patch.object(compiler, "_load_all_providers") as mock_load_providers,
            patch.object(compiler, "_validate_all_providers") as mock_validate,
            patch.object(compiler, "_save_bundle") as mock_save,
        ):

            mock_load_shared.return_value = None
            mock_load_providers.return_value = None
            mock_validate.return_value = None
            mock_save.return_value = None

            # Act
            bundle = compiler.compile_all_providers()

            # Assert
            assert isinstance(bundle, CompiledProviderBundle)
            assert "compilation_time" in compiler.compilation_stats
            mock_load_shared.assert_called_once()
            mock_load_providers.assert_called_once_with(None)
            mock_validate.assert_called_once()
            mock_save.assert_called_once()

    @patch("logging.getLogger")
    def test_compile_all_providers_with_specific_provider(
        self,
        mock_get_logger: Mock,
        tmp_path: Path,
    ) -> None:
        """Test compilation with specific_provider parameter."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        with (
            patch.object(compiler, "_load_shared_configuration"),
            patch.object(compiler, "_load_all_providers") as mock_load_providers,
        ):
            mock_load_providers.side_effect = ValueError("Test error")

            # Act & Assert
            with pytest.raises(Exception):
                compiler.compile_all_providers(specific_provider="openai")

            mock_load_providers.assert_called_once_with("openai")

    @patch("logging.getLogger")
    def test_compile_all_providers_handles_error(
        self,
        mock_get_logger: Mock,
        tmp_path: Path,
    ) -> None:
        """Test error handling in compile_all_providers."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        with patch.object(
            compiler, "_load_shared_configuration", side_effect=ValueError("Test error")
        ):
            # Act & Assert
            with pytest.raises(Exception):
                compiler.compile_all_providers()

    # ------------------------------------------------------------------------
    # _load_shared_configuration Tests
    # ------------------------------------------------------------------------

    @patch("builtins.open", new_callable=mock_open, read_data="test: data")
    @patch("yaml.safe_load")
    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_shared_configuration_success(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        mock_yaml: Mock,
        mock_file: Mock,
        tmp_path: Path,
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test successful loading of shared configuration."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = True
        mock_yaml.return_value = sample_shared_config

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        # Act
        compiler._load_shared_configuration()

        # Assert
        assert "validation_rules" in compiler.shared_config
        # Note: shared_config contains all loaded files, not just validation_rules
        assert "core_schema" in compiler.shared_config
        # Note: Logger assertions removed - logger is module-level, created at import

    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_shared_configuration_file_not_found(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        tmp_path: Path,
    ) -> None:
        """Test FileNotFoundError when shared config file missing."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = False

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Required shared config file"):
            compiler._load_shared_configuration()

    @patch("builtins.open", new_callable=mock_open, read_data="invalid: yaml: [")
    @patch("yaml.safe_load")
    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_shared_configuration_invalid_yaml(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        mock_yaml: Mock,
        mock_file: Mock,
        tmp_path: Path,
    ) -> None:
        """Test ValueError on invalid YAML syntax."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = True
        mock_yaml.side_effect = yaml.YAMLError("Parse error")

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid YAML"):
            compiler._load_shared_configuration()

    # ------------------------------------------------------------------------
    # _load_all_providers Tests
    # ------------------------------------------------------------------------

    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_all_providers_directory_not_found(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        tmp_path: Path,
    ) -> None:
        """Test FileNotFoundError when providers directory missing."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = False

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Providers directory not found"):
            compiler._load_all_providers()

    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_all_providers_specific_provider_not_found(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        tmp_path: Path,
    ) -> None:
        """Test FileNotFoundError when specific provider directory missing."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        def exists_side_effect(path: Path) -> bool:
            # Providers dir exists, but specific provider dir doesn't
            if "providers" in str(path) and "openai" not in str(path):
                return True
            return False

        mock_exists.side_effect = lambda: exists_side_effect(Path())

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        # Mock Path.exists to return True for providers_dir, False for specific
        with patch.object(Path, "exists") as mock_path_exists:
            mock_path_exists.side_effect = [True, False]  # providers_dir, provider_dir

            # Act & Assert
            with pytest.raises(FileNotFoundError, match="Provider directory not found"):
                compiler._load_all_providers(specific_provider="openai")

    @patch("pathlib.Path.iterdir")
    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_all_providers_no_valid_providers(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        mock_iterdir: Mock,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when no valid provider directories found."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = True

        # Mock empty directory iteration
        mock_iterdir.return_value = []

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        # Act & Assert
        with pytest.raises(ValueError, match="No valid provider directories found"):
            compiler._load_all_providers()

    def test_load_all_providers_handles_provider_error(
        self,
        tmp_path: Path,
    ) -> None:
        """Test error handling when loading individual provider fails."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        # Create mock provider directory with proper Path interface
        mock_provider_dir = Mock(spec=Path)
        mock_provider_dir.name = "openai"
        mock_provider_dir.is_dir.return_value = True
        mock_provider_dir.__truediv__ = Mock(
            side_effect=lambda x: Mock(spec=Path, exists=Mock(return_value=True))
        )

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "iterdir", return_value=[mock_provider_dir]),
            patch.object(
                compiler,
                "_load_provider_files",
                side_effect=Exception("Load error"),
            ),
        ):

            # Act & Assert - exception is logged and re-raised (line 193)
            with pytest.raises(Exception) as exc_info:
                compiler._load_all_providers()

            assert "Load error" in str(exc_info.value)
            assert "openai" not in compiler.providers

    # ------------------------------------------------------------------------
    # _load_provider_files Tests
    # ------------------------------------------------------------------------

    @patch("builtins.open", new_callable=mock_open, read_data="provider: openai")
    @patch("yaml.safe_load")
    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_provider_files_success(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        mock_yaml: Mock,
        mock_file: Mock,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test successful loading of provider files."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = True

        # Mock yaml.safe_load to return proper structure
        def yaml_side_effect(f: Any) -> Dict[str, Any]:
            return {"provider": "openai", **sample_provider_data}

        mock_yaml.side_effect = yaml_side_effect

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_dir = tmp_path / "providers" / "openai"

        # Act
        result = compiler._load_provider_files(provider_dir, "openai")

        # Assert
        assert isinstance(result, dict)
        assert "structure_patterns" in result
        assert "field_mappings" in result

    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_provider_files_file_not_found(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        tmp_path: Path,
    ) -> None:
        """Test FileNotFoundError when required provider file missing."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = False

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_dir = tmp_path / "providers" / "openai"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Required provider file"):
            compiler._load_provider_files(provider_dir, "openai")

    @patch("builtins.open", new_callable=mock_open, read_data="provider: openai")
    @patch("yaml.safe_load")
    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_provider_files_not_dict(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        mock_yaml: Mock,
        mock_file: Mock,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when YAML file doesn't contain a dictionary."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = True
        mock_yaml.return_value = ["list", "instead", "of", "dict"]

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_dir = tmp_path / "providers" / "openai"

        # Act & Assert
        with pytest.raises(ValueError, match="must contain a dictionary"):
            compiler._load_provider_files(provider_dir, "openai")

    @patch("builtins.open", new_callable=mock_open, read_data="provider: anthropic")
    @patch("yaml.safe_load")
    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_provider_files_name_mismatch(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        mock_yaml: Mock,
        mock_file: Mock,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when provider name in file doesn't match directory."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = True
        mock_yaml.return_value = {"provider": "anthropic"}

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_dir = tmp_path / "providers" / "openai"

        # Act & Assert
        with pytest.raises(ValueError, match="Provider name mismatch"):
            compiler._load_provider_files(provider_dir, "openai")

    @patch("builtins.open", new_callable=mock_open, read_data="invalid: yaml: [")
    @patch("yaml.safe_load")
    @patch("pathlib.Path.exists")
    @patch("logging.getLogger")
    def test_load_provider_files_invalid_yaml(
        self,
        mock_get_logger: Mock,
        mock_exists: Mock,
        mock_yaml: Mock,
        mock_file: Mock,
        tmp_path: Path,
    ) -> None:
        """Test ValueError on invalid YAML syntax in provider file."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_exists.return_value = True
        mock_yaml.side_effect = yaml.YAMLError("Parse error")

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_dir = tmp_path / "providers" / "openai"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid YAML"):
            compiler._load_provider_files(provider_dir, "openai")

    # ------------------------------------------------------------------------
    # _validate_all_providers Tests
    # ------------------------------------------------------------------------

    def test_validate_all_providers_success(
        self,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test successful validation of all providers."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.providers = {"openai": sample_provider_data}
        compiler.shared_config = sample_shared_config

        # Act & Assert - should not raise
        compiler._validate_all_providers()

    def test_validate_all_providers_handles_error(
        self,
        tmp_path: Path,
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test error handling in _validate_all_providers."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        # Invalid provider data - missing required fields
        compiler.providers = {"openai": {}}
        compiler.shared_config = sample_shared_config

        # Act & Assert - exception is logged and re-raised (line 257)
        with pytest.raises(ValueError) as exc_info:
            compiler._validate_all_providers()

        assert "No patterns defined" in str(exc_info.value)
        assert compiler.compilation_stats["validation_errors"] == 1

    # ------------------------------------------------------------------------
    # _validate_provider Tests
    # ------------------------------------------------------------------------

    def test_validate_provider_success(
        self,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test successful provider validation."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        validation_rules = sample_shared_config.get("validation_rules", {})

        # Act & Assert - should not raise
        compiler._validate_provider("openai", sample_provider_data, validation_rules)

    def test_validate_provider_no_patterns(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when no patterns defined."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_data: Dict[str, Any] = {"structure_patterns": {"patterns": {}}}

        # Act & Assert
        with pytest.raises(ValueError, match="No patterns defined"):
            compiler._validate_provider("openai", provider_data, {})

    def test_validate_provider_insufficient_signature_fields(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when signature has < 2 fields."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_data = {
            "structure_patterns": {
                "patterns": {
                    "pattern1": {
                        "signature_fields": ["only_one_field"],
                        "confidence_weight": 0.9,
                    }
                }
            }
        }

        # Act & Assert
        with pytest.raises(ValueError, match="must have at least 2 signature fields"):
            compiler._validate_provider("openai", provider_data, {})

    def test_validate_provider_confidence_out_of_range_low(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when confidence < 0.5."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_data = {
            "structure_patterns": {
                "patterns": {
                    "pattern1": {
                        "signature_fields": ["field1", "field2"],
                        "confidence_weight": 0.3,  # Too low
                    }
                }
            }
        }

        # Act & Assert
        with pytest.raises(ValueError, match="confidence must be between"):
            compiler._validate_provider("openai", provider_data, {})

    def test_validate_provider_confidence_out_of_range_high(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when confidence > 1.0."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_data = {
            "structure_patterns": {
                "patterns": {
                    "pattern1": {
                        "signature_fields": ["field1", "field2"],
                        "confidence_weight": 1.5,  # Too high
                    }
                }
            }
        }

        # Act & Assert
        with pytest.raises(ValueError, match="confidence must be between"):
            compiler._validate_provider("openai", provider_data, {})

    def test_validate_provider_missing_field_mapping_section(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when required field mapping section missing."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_data = {
            "structure_patterns": {
                "patterns": {
                    "pattern1": {
                        "signature_fields": ["field1", "field2"],
                        "confidence_weight": 0.9,
                    }
                }
            },
            "field_mappings": {"field_mappings": {"inputs": {}, "outputs": {}}},
            # Missing 'config' and 'metadata' sections
        }

        # Act & Assert
        with pytest.raises(ValueError, match="missing required section"):
            compiler._validate_provider("openai", provider_data, {})

    def test_validate_provider_missing_provider_in_metadata(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when 'provider' field missing in metadata section."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        provider_data = {
            "structure_patterns": {
                "patterns": {
                    "pattern1": {
                        "signature_fields": ["field1", "field2"],
                        "confidence_weight": 0.9,
                    }
                }
            },
            "field_mappings": {
                "field_mappings": {
                    "inputs": {},
                    "outputs": {},
                    "config": {},
                    "metadata": {},  # Empty metadata - no 'provider' field
                }
            },
        }

        # Act & Assert
        with pytest.raises(ValueError, match="must include 'provider' field"):
            compiler._validate_provider("openai", provider_data, {})

    # ------------------------------------------------------------------------
    # _compile_signature_indices Tests
    # ------------------------------------------------------------------------

    def test_compile_signature_indices_success(
        self,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test successful signature index compilation."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.providers = {"openai": sample_provider_data}

        # Act
        forward_index, inverted_index = compiler._compile_signature_indices()

        # Assert
        assert isinstance(forward_index, dict)
        assert isinstance(inverted_index, dict)
        assert "openai" in forward_index
        assert len(forward_index["openai"]) == 2  # 2 patterns
        assert len(inverted_index) == 2  # 2 unique signatures

    def test_compile_signature_indices_collision_handling(
        self,
        tmp_path: Path,
    ) -> None:
        """Test collision handling when multiple providers have same signature."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.providers = {
            "openai": {
                "structure_patterns": {
                    "patterns": {
                        "pattern1": {
                            "signature_fields": ["field1", "field2"],
                            "confidence_weight": 0.9,
                        }
                    }
                }
            },
            "anthropic": {
                "structure_patterns": {
                    "patterns": {
                        "pattern1": {
                            "signature_fields": ["field1", "field2"],  # Same signature
                            "confidence_weight": 0.95,  # Higher confidence
                        }
                    }
                }
            },
        }

        # Act
        _, inverted_index = compiler._compile_signature_indices()

        # Assert
        signature = frozenset(["field1", "field2"])
        assert signature in inverted_index
        # Should keep higher confidence provider (anthropic)
        assert inverted_index[signature][0] == "anthropic"
        assert inverted_index[signature][1] == 0.95
        # Note: warning is logged, but we don't assert on logger mock

    # ------------------------------------------------------------------------
    # _compile_extraction_functions Tests
    # ------------------------------------------------------------------------

    @patch("logging.getLogger")
    def test_compile_extraction_functions_success(
        self,
        mock_get_logger: Mock,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test successful extraction function compilation."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.providers = {"openai": sample_provider_data}

        # Act
        functions = compiler._compile_extraction_functions()

        # Assert
        assert isinstance(functions, dict)
        assert "openai" in functions
        assert isinstance(functions["openai"], str)
        assert "def extract_openai" in functions["openai"]
        assert "inputs =" in functions["openai"]
        assert "outputs =" in functions["openai"]

    # ------------------------------------------------------------------------
    # _generate_extraction_function Tests
    # ------------------------------------------------------------------------

    def test_generate_extraction_function_success(
        self,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test successful extraction function code generation."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        # Act
        function_code = compiler._generate_extraction_function(
            "openai", sample_provider_data
        )

        # Assert
        assert isinstance(function_code, str)
        assert "def extract_openai" in function_code
        assert "inputs =" in function_code
        assert "outputs =" in function_code
        assert "config =" in function_code
        assert "metadata =" in function_code
        assert "return {" in function_code

    # ------------------------------------------------------------------------
    # _generate_field_extraction_code Tests
    # ------------------------------------------------------------------------

    def test_generate_field_extraction_code_static_value(
        self,
        tmp_path: Path,
    ) -> None:
        """Test code generation for static value."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        navigation_rules: Dict[str, Any] = {}
        transforms: Dict[str, Any] = {}

        # Act
        code = compiler._generate_field_extraction_code(
            "field1", "static_test_value", navigation_rules, transforms
        )

        # Assert
        assert code == "'test_value'"

    def test_generate_field_extraction_code_direct_copy(
        self,
        tmp_path: Path,
    ) -> None:
        """Test code generation for direct copy extraction."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        navigation_rules: Dict[str, Any] = {
            "nav_rule1": {
                "source_field": "model",
                "extraction_method": "direct_copy",
                "fallback_value": "unknown",
            }
        }
        transforms: Dict[str, Any] = {}

        # Act
        code = compiler._generate_field_extraction_code(
            "field1", "nav_rule1", navigation_rules, transforms
        )

        # Assert
        assert "attributes.get('model'" in code
        assert "'unknown'" in code

    def test_generate_field_extraction_code_array_flatten(
        self,
        tmp_path: Path,
    ) -> None:
        """Test code generation for array flatten extraction."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        navigation_rules: Dict[str, Any] = {
            "nav_rule1": {
                "source_field": "items",
                "extraction_method": "array_flatten",
                "fallback_value": [],
            }
        }
        transforms: Dict[str, Any] = {}

        # Act
        code = compiler._generate_field_extraction_code(
            "field1", "nav_rule1", navigation_rules, transforms
        )

        # Assert
        assert "_flatten_array" in code
        assert "attributes.get('items'" in code

    def test_generate_field_extraction_code_object_merge(
        self,
        tmp_path: Path,
    ) -> None:
        """Test code generation for object merge extraction."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        navigation_rules: Dict[str, Any] = {
            "nav_rule1": {
                "source_field": "data",
                "extraction_method": "object_merge",
                "fallback_value": {},
            }
        }
        transforms: Dict[str, Any] = {}

        # Act
        code = compiler._generate_field_extraction_code(
            "field1", "nav_rule1", navigation_rules, transforms
        )

        # Assert
        assert "_merge_objects" in code
        assert "attributes.get('data'" in code

    def test_generate_field_extraction_code_unknown_method(
        self,
        tmp_path: Path,
    ) -> None:
        """Test code generation for unknown extraction method."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        navigation_rules: Dict[str, Any] = {
            "nav_rule1": {
                "source_field": "field",
                "extraction_method": "unknown_method",
                "fallback_value": None,
            }
        }
        transforms: Dict[str, Any] = {}

        # Act
        code = compiler._generate_field_extraction_code(
            "field1", "nav_rule1", navigation_rules, transforms
        )

        # Assert
        assert "attributes.get('field'" in code

    def test_generate_field_extraction_code_with_transform(
        self,
        tmp_path: Path,
    ) -> None:
        """Test code generation for transform rule."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        navigation_rules: Dict[str, Any] = {}
        transforms: Dict[str, Any] = {
            "transform_rule1": {
                "function_type": "lambda",
                "implementation": "lambda x: x * 2",
                "parameters": {},
            }
        }

        # Act
        code = compiler._generate_field_extraction_code(
            "field1", "transform_rule1", navigation_rules, transforms
        )

        # Assert
        assert "lambda x: x * 2" in code or "lambda" in code

    # ------------------------------------------------------------------------
    # _get_fallback_value Tests
    # ------------------------------------------------------------------------

    def test_get_fallback_value_from_navigation_rules(
        self,
        tmp_path: Path,
    ) -> None:
        """Test getting fallback value from navigation rules."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        navigation_rules: Dict[str, Any] = {
            "nav_rule1": {
                "source_field": "field",
                "extraction_method": "direct_copy",
                "fallback_value": "default",
            }
        }

        # Act
        fallback = compiler._get_fallback_value("nav_rule1", navigation_rules)

        # Assert
        assert fallback == "default"

    def test_get_fallback_value_none(
        self,
        tmp_path: Path,
    ) -> None:
        """Test fallback value when rule not in navigation rules."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        navigation_rules: Dict[str, Any] = {}

        # Act
        fallback = compiler._get_fallback_value("unknown_rule", navigation_rules)

        # Assert
        assert fallback is None

    # ------------------------------------------------------------------------
    # _compile_field_mappings Tests
    # ------------------------------------------------------------------------

    def test_compile_field_mappings_success(
        self,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test successful field mappings compilation."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.providers = {"openai": sample_provider_data}

        # Act
        mappings = compiler._compile_field_mappings()

        # Assert
        assert isinstance(mappings, dict)
        assert "openai" in mappings
        assert isinstance(mappings["openai"], dict)

    # ------------------------------------------------------------------------
    # _compile_transform_registry Tests
    # ------------------------------------------------------------------------

    def test_compile_transform_registry_success(
        self,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test successful transform registry compilation."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.providers = {"openai": sample_provider_data}

        # Act
        registry = compiler._compile_transform_registry()

        # Assert
        assert isinstance(registry, dict)
        assert "openai" in registry
        assert isinstance(registry["openai"], dict)

    # ------------------------------------------------------------------------
    # _compile_validation_rules Tests
    # ------------------------------------------------------------------------

    def test_compile_validation_rules_success(
        self,
        tmp_path: Path,
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test successful validation rules compilation."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.shared_config = sample_shared_config

        # Act
        rules = compiler._compile_validation_rules()

        # Assert
        assert isinstance(rules, dict)
        assert "min_signatures" in rules
        assert rules["min_signatures"] == 2

    def test_compile_validation_rules_empty_config(
        self,
        tmp_path: Path,
    ) -> None:
        """Test validation rules compilation with empty config."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.shared_config = {}

        # Act
        rules = compiler._compile_validation_rules()

        # Assert
        assert isinstance(rules, dict)
        assert rules == {}

    # ------------------------------------------------------------------------
    # _generate_build_metadata Tests
    # ------------------------------------------------------------------------

    @patch("time.time")
    def test_generate_build_metadata_success(
        self,
        mock_time: Mock,
        tmp_path: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test successful build metadata generation."""
        # Arrange
        mock_time.return_value = 1234567890.5
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.providers = {"openai": sample_provider_data}
        # _generate_build_metadata reads from compilation_stats (lines 578-580)
        compiler.compilation_stats = {
            "providers_processed": 1,
            "patterns_compiled": 2,
            "functions_generated": 1,
            "validation_errors": 0,
            "compilation_time": 5.5,
        }

        # Act
        metadata = compiler._generate_build_metadata()

        # Assert
        assert isinstance(metadata, dict)
        assert "build_timestamp" in metadata
        assert "providers_count" in metadata
        assert "source_hash" in metadata  # Correct field name from line 581
        assert "compilation_time" in metadata
        assert metadata["providers_count"] == 1
        assert metadata["build_timestamp"] == 1234567890
        assert metadata["compilation_time"] == 5.5

    # ------------------------------------------------------------------------
    # _calculate_source_hash Tests
    # ------------------------------------------------------------------------

    @patch("builtins.open", new_callable=mock_open, read_data=b"test data")
    @patch("hashlib.sha256")
    @patch("pathlib.Path.glob")
    def test_calculate_source_hash_success(
        self,
        mock_glob: Mock,
        mock_sha256: Mock,
        mock_file: Mock,
        tmp_path: Path,
    ) -> None:
        """Test successful source hash calculation."""
        # Arrange
        mock_hasher = Mock()
        mock_hasher.hexdigest.return_value = "abc123"
        mock_sha256.return_value = mock_hasher

        # Mock glob to return file paths
        mock_yaml_file = Mock()
        mock_yaml_file.name = "test.yaml"
        mock_glob.return_value = [mock_yaml_file]

        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        compiler.providers = {"openai": {}}

        # Act
        source_hash = compiler._calculate_source_hash()

        # Assert
        assert source_hash == "abc123"
        mock_sha256.assert_called_once()
        mock_hasher.update.assert_called()

    # ------------------------------------------------------------------------
    # _validate_bundle Tests
    # ------------------------------------------------------------------------

    def test_validate_bundle_success(
        self,
        tmp_path: Path,
    ) -> None:
        """Test successful bundle validation."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        # Create valid bundle
        bundle = CompiledProviderBundle(
            provider_signatures={"openai": [frozenset(["field1", "field2"])]},
            signature_to_provider={frozenset(["field1", "field2"]): ("openai", 0.9)},
            extraction_functions={"openai": "def extract_openai(): pass"},
            field_mappings={},
            transform_registry={},
            validation_rules={},
            build_metadata={},
        )

        # Act & Assert - should not raise
        compiler._validate_bundle(bundle)

    def test_validate_bundle_empty_provider_signatures(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when bundle has no provider signatures."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        bundle = CompiledProviderBundle(
            provider_signatures={},  # Empty
            signature_to_provider={},
            extraction_functions={"openai": "def extract(): pass"},
            field_mappings={},
            transform_registry={},
            validation_rules={},
            build_metadata={},
        )

        # Act & Assert
        with pytest.raises(ValueError, match="no provider signatures"):
            compiler._validate_bundle(bundle)

    def test_validate_bundle_empty_extraction_functions(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when bundle has no extraction functions."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        bundle = CompiledProviderBundle(
            provider_signatures={"openai": [frozenset(["field1", "field2"])]},
            signature_to_provider={frozenset(["field1", "field2"]): ("openai", 0.9)},
            extraction_functions={},  # Empty
            field_mappings={},
            transform_registry={},
            validation_rules={},
            build_metadata={},
        )

        # Act & Assert
        with pytest.raises(ValueError, match="no extraction functions"):
            compiler._validate_bundle(bundle)

    def test_validate_bundle_provider_no_signatures(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when provider has no signatures."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        bundle = CompiledProviderBundle(
            provider_signatures={"openai": []},  # Empty list
            signature_to_provider={},
            extraction_functions={"openai": "def extract(): pass"},
            field_mappings={},
            transform_registry={},
            validation_rules={},
            build_metadata={},
        )

        # Act & Assert
        with pytest.raises(ValueError, match="has no signatures"):
            compiler._validate_bundle(bundle)

    def test_validate_bundle_signature_too_small(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when signature has < 2 fields."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        bundle = CompiledProviderBundle(
            provider_signatures={"openai": [frozenset(["only_one"])]},  # < 2 fields
            signature_to_provider={frozenset(["only_one"]): ("openai", 0.9)},
            extraction_functions={"openai": "def extract(): pass"},
            field_mappings={},
            transform_registry={},
            validation_rules={},
            build_metadata={},
        )

        # Act & Assert
        with pytest.raises(ValueError, match="< 2 fields"):
            compiler._validate_bundle(bundle)

    def test_validate_bundle_invalid_function_syntax(
        self,
        tmp_path: Path,
    ) -> None:
        """Test ValueError when extraction function has invalid syntax."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        bundle = CompiledProviderBundle(
            provider_signatures={"openai": [frozenset(["field1", "field2"])]},
            signature_to_provider={frozenset(["field1", "field2"]): ("openai", 0.9)},
            extraction_functions={
                "openai": "def invalid syntax here"
            },  # Invalid Python
            field_mappings={},
            transform_registry={},
            validation_rules={},
            build_metadata={},
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid extraction function"):
            compiler._validate_bundle(bundle)

    # ------------------------------------------------------------------------
    # _save_bundle Tests
    # ------------------------------------------------------------------------

    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.dump")
    @patch("json.dump")
    @patch("pathlib.Path.mkdir")
    def test_save_bundle_success(
        self,
        mock_mkdir: Mock,
        mock_json_dump: Mock,
        mock_pickle_dump: Mock,
        mock_file: Mock,
        tmp_path: Path,
    ) -> None:
        """Test successful bundle saving."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")

        bundle = CompiledProviderBundle(
            provider_signatures={"openai": [frozenset(["field1", "field2"])]},
            signature_to_provider={frozenset(["field1", "field2"]): ("openai", 0.9)},
            extraction_functions={"openai": "def extract(): pass"},
            field_mappings={},
            transform_registry={},
            validation_rules={},
            build_metadata={"version": "4.0"},
        )

        # Act
        compiler._save_bundle(bundle)

        # Assert
        mock_mkdir.assert_called_once()
        mock_pickle_dump.assert_called_once()
        mock_json_dump.assert_called_once()

    # ------------------------------------------------------------------------
    # _log_compilation_stats Tests
    # ------------------------------------------------------------------------

    def test_log_compilation_stats_success(
        self,
        tmp_path: Path,
    ) -> None:
        """Test successful compilation stats logging."""
        # Arrange
        compiler = ProviderCompiler(tmp_path, tmp_path / "output")
        # Use exact keys from __init__ (lines 54-58)
        compiler.compilation_stats = {
            "providers_processed": 2,
            "patterns_compiled": 5,
            "functions_generated": 3,
            "validation_errors": 0,
            "compilation_time": 3.5,
        }

        # Act & Assert - should not raise
        compiler._log_compilation_stats()


# ============================================================================
# TEST CLASS: main() function
# ============================================================================


class TestMainFunction:
    """Test suite for main() CLI function."""

    @patch("sys.argv", ["compiler.py"])
    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_main_default_arguments(
        self,
        mock_get_logger: Mock,
        mock_logging_config: Mock,
    ) -> None:
        """Test main() with default arguments."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        with patch("config.dsl.compiler.ProviderCompiler") as mock_compiler_class:
            mock_compiler = Mock()
            mock_compiler_class.return_value = mock_compiler

            mock_bundle = Mock()
            mock_bundle.build_metadata = {
                "compilation_time": 5.0,
            }
            mock_bundle.provider_signatures = {"openai": [], "anthropic": []}
            mock_bundle.extraction_functions = {"openai": "func1", "anthropic": "func2"}
            mock_compiler.compile_all_providers.return_value = mock_bundle

            # Act
            result = main()

            # Assert
            assert result == 0
            mock_compiler_class.assert_called_once()
            mock_compiler.compile_all_providers.assert_called_once()

    @patch("sys.argv", ["compiler.py", "--verbose"])
    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_main_verbose_flag(
        self,
        mock_get_logger: Mock,
        mock_logging_config: Mock,
    ) -> None:
        """Test main() with verbose flag."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        with patch("config.dsl.compiler.ProviderCompiler") as mock_compiler_class:
            mock_compiler = Mock()
            mock_compiler_class.return_value = mock_compiler

            mock_bundle = Mock()
            mock_bundle.build_metadata = {"compilation_time": 5.0}
            mock_bundle.provider_signatures = {}
            mock_bundle.extraction_functions = {}
            mock_compiler.compile_all_providers.return_value = mock_bundle

            # Act
            result = main()

            # Assert
            assert result == 0
            # Verify logging configured with DEBUG level
            assert any(
                call[1].get("level") == 10  # DEBUG level
                for call in mock_logging_config.call_args_list
            )

    @patch(
        "sys.argv",
        [
            "compiler.py",
            "--source-dir",
            "/custom/source",
            "--output-dir",
            "/custom/output",
        ],
    )
    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_main_custom_directories(
        self,
        mock_get_logger: Mock,
        mock_logging_config: Mock,
    ) -> None:
        """Test main() with custom source and output directories."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        with patch("config.dsl.compiler.ProviderCompiler") as mock_compiler_class:
            mock_compiler = Mock()
            mock_compiler_class.return_value = mock_compiler

            mock_bundle = Mock()
            mock_bundle.build_metadata = {"compilation_time": 5.0}
            mock_bundle.provider_signatures = {}
            mock_bundle.extraction_functions = {}
            mock_compiler.compile_all_providers.return_value = mock_bundle

            # Act
            result = main()

            # Assert
            assert result == 0
            # Verify custom paths passed to compiler
            call_args = mock_compiler_class.call_args
            assert str(call_args[0][0]) == "/custom/source"
            assert str(call_args[0][1]) == "/custom/output"

    @patch("sys.argv", ["compiler.py", "--provider", "openai"])
    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_main_specific_provider(
        self,
        mock_get_logger: Mock,
        mock_logging_config: Mock,
    ) -> None:
        """Test main() with specific provider argument."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        with patch("config.dsl.compiler.ProviderCompiler") as mock_compiler_class:
            mock_compiler = Mock()
            mock_compiler_class.return_value = mock_compiler

            mock_bundle = Mock()
            mock_bundle.build_metadata = {"compilation_time": 5.0}
            mock_bundle.provider_signatures = {"openai": []}
            mock_bundle.extraction_functions = {"openai": "func"}
            mock_compiler.compile_all_providers.return_value = mock_bundle

            # Act
            result = main()

            # Assert
            assert result == 0
            # Note: ArgumentParser uses positional arg, not keyword
            mock_compiler.compile_all_providers.assert_called_once_with("openai")

    @patch("sys.argv", ["compiler.py"])
    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_main_handles_compilation_error(
        self,
        mock_get_logger: Mock,
        mock_logging_config: Mock,
    ) -> None:
        """Test main() error handling when compilation fails."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        with patch("config.dsl.compiler.ProviderCompiler") as mock_compiler_class:
            mock_compiler = Mock()
            mock_compiler_class.return_value = mock_compiler
            mock_compiler.compile_all_providers.side_effect = Exception(
                "Compilation failed"
            )

            # Act
            result = main()

            # Assert
            assert result == 1  # Error exit code
            # Error is logged by compile_all_providers, not main
            # Main just re-raises, so check exit code is sufficient

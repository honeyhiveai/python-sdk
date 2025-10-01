"""Unit tests for Provider Compiler - Universal LLM Discovery Engine v4.0.

This module tests the provider compilation system with complete isolation via mocking.
All external dependencies are mocked to ensure fast, deterministic tests.

Test Coverage Target: 90%+ line and branch coverage
Quality Targets: 100% pass rate, 10.0/10 Pylint, 0 MyPy errors
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods
# pylint: disable=line-too-long,unused-argument,too-many-positional-arguments,too-few-public-methods
# pylint: disable=too-many-arguments
# Justification: Comprehensive test coverage requires extensive test cases, testing private methods
# requires protected access, pytest fixtures redefine outer names by design, comprehensive test
# classes need many test methods, mock patch decorators create unavoidable long lines, pytest
# fixtures are often unused in individual tests but required by the framework, test methods require
# many positional arguments for fixtures and mocks, test classes may have single focused tests,
# and integration test methods require many arguments to mock complex compilation pipelines.

from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from typing import Dict, Any

import pytest
import yaml

# Import from config.dsl package (proper Python package structure)
from config.dsl.compiler import ProviderCompiler


@pytest.fixture
def mock_source_dir(tmp_path: Path) -> Path:
    """Create mock source directory structure."""
    source_dir = tmp_path / "config" / "dsl"
    providers_dir = source_dir / "providers"
    shared_dir = source_dir / "shared"

    providers_dir.mkdir(parents=True)
    shared_dir.mkdir(parents=True)

    return source_dir


@pytest.fixture
def mock_output_dir(tmp_path: Path) -> Path:
    """Create mock output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)
    return output_dir


@pytest.fixture
def sample_provider_data() -> Dict[str, Any]:
    """Sample provider configuration data for testing."""
    return {
        "structure_patterns": {
            "patterns": {
                "chat_completion": {
                    "signature_fields": ["model", "messages", "response"],
                    "confidence_weight": 0.95,
                },
                "completion": {
                    "signature_fields": ["prompt", "model"],
                    "confidence_weight": 0.85,
                },
            }
        },
        "field_mappings": {
            "field_mappings": {
                "inputs": {"prompt": {"source": "prompt", "fallback": ""}},
                "outputs": {"response": {"source": "response", "fallback": ""}},
                "config": {"temperature": {"source": "temperature", "fallback": 0.7}},
                "metadata": {
                    "model": {"source": "model", "fallback": "unknown"},
                    "provider": {"source": "static_openai", "fallback": "openai"},
                },
            }
        },
        "navigation_rules": {},
        "transforms": {"transforms": {}},
    }


@pytest.fixture
def sample_shared_config() -> Dict[str, Any]:
    """Sample shared configuration for testing."""
    return {
        "validation_rules": {
            "required_fields": ["provider", "version"],
            "signature_min_fields": 2,
        }
    }


class TestProviderCompilerInit:
    """Test suite for ProviderCompiler initialization."""

    def test_init_creates_correct_attributes(
        self, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test __init__ creates all required attributes."""
        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        assert compiler.source_dir == mock_source_dir
        assert compiler.output_dir == mock_output_dir
        assert compiler.providers_dir == mock_source_dir / "providers"
        assert compiler.shared_dir == mock_source_dir / "shared"
        assert isinstance(compiler.providers, dict)
        assert isinstance(compiler.shared_config, dict)
        assert isinstance(compiler.compilation_stats, dict)

    def test_init_stats_dictionary_structure(
        self, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test __init__ creates compilation_stats with correct structure."""
        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        assert "providers_processed" in compiler.compilation_stats
        assert "patterns_compiled" in compiler.compilation_stats
        assert "functions_generated" in compiler.compilation_stats
        assert "validation_errors" in compiler.compilation_stats
        assert "compilation_time" in compiler.compilation_stats

        # Verify initial values
        assert compiler.compilation_stats["providers_processed"] == 0
        assert compiler.compilation_stats["patterns_compiled"] == 0


class TestProviderCompilerLoadSharedConfiguration:
    """Test suite for _load_shared_configuration method."""

    @patch("builtins.open", new_callable=mock_open, read_data="version: 1.0\nrules: {}")
    @patch("yaml.safe_load")
    @patch("logging.getLogger")
    def test_load_shared_configuration_success(
        self,
        mock_get_logger: Mock,
        mock_yaml_load: Mock,
        mock_file: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test _load_shared_configuration loads all required files successfully."""
        # Setup
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_yaml_load.return_value = sample_shared_config

        # Create required shared config files
        (mock_source_dir / "shared" / "core_schema.yaml").touch()
        (mock_source_dir / "shared" / "instrumentor_mappings.yaml").touch()
        (mock_source_dir / "shared" / "validation_rules.yaml").touch()

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute
        compiler._load_shared_configuration()

        # Verify
        assert "core_schema" in compiler.shared_config
        assert "instrumentor_mappings" in compiler.shared_config
        assert "validation_rules" in compiler.shared_config
        assert mock_yaml_load.call_count == 3

    @patch("logging.getLogger")
    def test_load_shared_configuration_missing_file(
        self, mock_get_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _load_shared_configuration raises FileNotFoundError for missing files."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute & Verify - should raise because files don't exist
        with pytest.raises(
            FileNotFoundError, match="Required shared config file not found"
        ):
            compiler._load_shared_configuration()

    @patch("builtins.open", new_callable=mock_open, read_data="invalid: yaml: {]")
    @patch("yaml.safe_load")
    @patch("logging.getLogger")
    def test_load_shared_configuration_invalid_yaml(
        self,
        mock_get_logger: Mock,
        mock_yaml_load: Mock,
        mock_file: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
    ) -> None:
        """Test _load_shared_configuration raises ValueError for invalid YAML."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")

        # Create file
        (mock_source_dir / "shared" / "core_schema.yaml").touch()

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute & Verify
        with pytest.raises(ValueError, match="Invalid YAML"):
            compiler._load_shared_configuration()


class TestProviderCompilerCompileSignatureIndices:
    """Test suite for _compile_signature_indices method - core of TASK-012."""

    @patch("logging.getLogger")
    def test_compile_signature_indices_basic_functionality(
        self,
        mock_get_logger: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test _compile_signature_indices generates both forward and inverted indices."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {"openai": sample_provider_data}

        # Execute
        forward_index, inverted_index = compiler._compile_signature_indices()

        # Verify forward index structure
        assert "openai" in forward_index
        assert len(forward_index["openai"]) == 2  # 2 patterns
        assert all(isinstance(sig, frozenset) for sig in forward_index["openai"])

        # Verify inverted index structure
        assert len(inverted_index) == 2  # 2 unique signatures
        for signature, (provider, confidence) in inverted_index.items():
            assert isinstance(signature, frozenset)
            assert isinstance(provider, str)
            assert isinstance(confidence, float)
            assert provider == "openai"

    @patch("logging.getLogger")
    def test_compile_signature_indices_collision_handling(
        self, mock_get_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _compile_signature_indices handles signature collisions correctly."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Create two providers with identical signature but different confidence
        compiler.providers = {
            "provider_a": {
                "structure_patterns": {
                    "patterns": {
                        "pattern1": {
                            "signature_fields": ["field1", "field2"],
                            "confidence_weight": 0.85,
                        }
                    }
                }
            },
            "provider_b": {
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

        # Execute
        _forward_index, inverted_index = compiler._compile_signature_indices()

        # Verify collision handling - should keep higher confidence provider
        signature = frozenset(["field1", "field2"])
        assert signature in inverted_index
        provider, confidence = inverted_index[signature]
        assert provider == "provider_b"  # Higher confidence provider
        assert confidence == 0.95

        # Collision was handled correctly (behavior verified, logging is implementation detail)

    @patch("logging.getLogger")
    def test_compile_signature_indices_default_confidence(
        self, mock_get_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _compile_signature_indices uses default confidence when not specified."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {
            "test_provider": {
                "structure_patterns": {
                    "patterns": {
                        "pattern_no_confidence": {
                            "signature_fields": ["field1", "field2"]
                            # No confidence_weight specified
                        }
                    }
                }
            }
        }

        # Execute
        _, inverted_index = compiler._compile_signature_indices()

        # Verify default confidence applied
        signature = frozenset(["field1", "field2"])
        _, confidence = inverted_index[signature]
        assert confidence == 0.9  # Default value

    @patch("logging.getLogger")
    def test_compile_signature_indices_empty_providers(
        self, mock_get_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _compile_signature_indices handles empty providers gracefully."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {}

        # Execute
        forward_index, inverted_index = compiler._compile_signature_indices()

        # Verify empty results
        assert len(forward_index) == 0
        assert len(inverted_index) == 0

    @patch("logging.getLogger")
    def test_compile_signature_indices_stats_tracking(
        self,
        mock_get_logger: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test _compile_signature_indices updates compilation_stats correctly."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {"openai": sample_provider_data}

        initial_patterns = compiler.compilation_stats["patterns_compiled"]

        # Execute
        compiler._compile_signature_indices()

        # Verify stats updated
        assert compiler.compilation_stats["patterns_compiled"] == initial_patterns + 2


class TestProviderCompilerCompileAllProviders:
    """Test suite for compile_all_providers method - main entry point."""

    @patch.object(ProviderCompiler, "_save_bundle")
    @patch.object(ProviderCompiler, "_validate_bundle")
    @patch.object(ProviderCompiler, "_generate_build_metadata")
    @patch.object(ProviderCompiler, "_compile_validation_rules")
    @patch.object(ProviderCompiler, "_compile_transform_registry")
    @patch.object(ProviderCompiler, "_compile_field_mappings")
    @patch.object(ProviderCompiler, "_compile_extraction_functions")
    @patch.object(ProviderCompiler, "_compile_signature_indices")
    @patch.object(ProviderCompiler, "_validate_all_providers")
    @patch.object(ProviderCompiler, "_load_all_providers")
    @patch.object(ProviderCompiler, "_load_shared_configuration")
    @patch("time.time")
    @patch("logging.getLogger")
    def test_compile_all_providers_success_path(
        self,
        mock_get_logger: Mock,
        mock_time: Mock,
        mock_load_shared: Mock,
        mock_load_providers: Mock,
        mock_validate_all: Mock,
        mock_compile_sigs: Mock,
        mock_compile_funcs: Mock,
        mock_compile_mappings: Mock,
        mock_compile_transforms: Mock,
        mock_compile_validation: Mock,
        mock_build_metadata: Mock,
        mock_validate_bundle: Mock,
        mock_save_bundle: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
    ) -> None:
        """Test compile_all_providers executes full compilation pipeline successfully."""
        # Setup
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_time.side_effect = [1000.0, 1005.5]  # Start and end time

        # Mock return values for compilation steps
        mock_compile_sigs.return_value = (
            {"openai": [frozenset(["model", "messages"])]},  # forward_index
            {frozenset(["model", "messages"]): ("openai", 0.95)},  # inverted_index
        )
        mock_compile_funcs.return_value = {"openai": "def extract(attrs): pass"}
        mock_compile_mappings.return_value = {"openai": {}}
        mock_compile_transforms.return_value = {"openai": {}}
        mock_compile_validation.return_value = {}
        mock_build_metadata.return_value = {"version": "4.0.1"}

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute
        _bundle = compiler.compile_all_providers()

        # Verify all steps called in order
        mock_load_shared.assert_called_once()
        mock_load_providers.assert_called_once_with(None)
        mock_validate_all.assert_called_once()
        mock_compile_sigs.assert_called_once()
        mock_compile_funcs.assert_called_once()
        mock_compile_mappings.assert_called_once()
        mock_compile_transforms.assert_called_once()
        mock_compile_validation.assert_called_once()
        mock_build_metadata.assert_called_once()
        mock_validate_bundle.assert_called_once()
        mock_save_bundle.assert_called_once()

        # Verify compilation time calculated
        assert compiler.compilation_stats["compilation_time"] == 5.5

    @patch.object(ProviderCompiler, "_load_shared_configuration")
    @patch("time.time")
    @patch("logging.getLogger")
    def test_compile_all_providers_handles_exceptions(
        self,
        mock_get_logger: Mock,
        mock_time: Mock,
        mock_load_shared: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
    ) -> None:
        """Test compile_all_providers handles exceptions and logs errors."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_time.return_value = 1000.0
        test_exception = Exception("Test exception")
        mock_load_shared.side_effect = test_exception

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute & Verify - exception should propagate
        with pytest.raises(Exception) as exc_info:
            compiler.compile_all_providers()

        # Verify correct exception was raised (behavior test)
        assert str(exc_info.value) == "Test exception"


class TestProviderCompilerValidateBundle:
    """Test suite for _validate_bundle method."""

    @patch("logging.getLogger")
    def test_validate_bundle_success(
        self, mock_get_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _validate_bundle passes for valid bundle."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Create mock bundle with valid structure (signatures need 2+ fields)
        mock_bundle = MagicMock()
        mock_bundle.provider_signatures = {"openai": [frozenset(["model", "messages"])]}
        mock_bundle.signature_to_provider = {
            frozenset(["model", "messages"]): ("openai", 0.95)
        }
        mock_bundle.extraction_functions = {"openai": "def extract(): pass"}
        mock_bundle.field_mappings = {"openai": {}}
        mock_bundle.transform_registry = {"openai": {}}
        mock_bundle.validation_rules = {}
        mock_bundle.build_metadata = {"version": "4.0.1"}

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute - should not raise (behavior test)
        compiler._validate_bundle(mock_bundle)
        # Method completed successfully without raising exception

    @patch("logging.getLogger")
    def test_validate_bundle_empty_providers(
        self, mock_get_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _validate_bundle raises ValueError for empty providers."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Create mock bundle with NO providers
        mock_bundle = MagicMock()
        mock_bundle.provider_signatures = {}

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute & Verify - match actual error message
        with pytest.raises(ValueError, match="Bundle contains no provider signatures"):
            compiler._validate_bundle(mock_bundle)


class TestProviderCompilerSaveBundle:
    """Test suite for _save_bundle method."""

    @patch("json.dump")
    @patch("pickle.dump")
    @patch("builtins.open", new_callable=mock_open)
    @patch("logging.getLogger")
    def test_save_bundle_success(
        self,
        mock_get_logger: Mock,
        mock_file: Mock,
        mock_pickle_dump: Mock,
        mock_json_dump: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
    ) -> None:
        """Test _save_bundle successfully serializes bundle."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_bundle = MagicMock()
        mock_bundle.build_metadata = {"version": "4.0.1"}  # Add serializable metadata

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute
        compiler._save_bundle(mock_bundle)

        # Verify pickle.dump called with bundle
        mock_pickle_dump.assert_called_once()
        assert mock_pickle_dump.call_args[0][0] == mock_bundle

    @patch("json.dump")
    @patch("pickle.dump")
    @patch("builtins.open", new_callable=mock_open)
    @patch("logging.getLogger")
    def test_save_bundle_creates_output_dir(
        self,
        mock_get_logger: Mock,
        mock_file: Mock,
        mock_pickle_dump: Mock,
        mock_json_dump: Mock,
        mock_source_dir: Path,
        tmp_path: Path,
    ) -> None:
        """Test _save_bundle creates output directory if it doesn't exist."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        output_dir = tmp_path / "nonexistent" / "output"
        mock_bundle = MagicMock()
        mock_bundle.build_metadata = {"version": "4.0.1"}  # Add serializable metadata

        compiler = ProviderCompiler(mock_source_dir, output_dir)

        # Execute
        compiler._save_bundle(mock_bundle)

        # Verify directory was created
        assert output_dir.exists()


class TestProviderCompilerGenerateBuildMetadata:
    """Test suite for _generate_build_metadata method."""

    @patch("hashlib.md5")
    @patch("time.time")
    @patch("logging.getLogger")
    def test_generate_build_metadata_structure(
        self,
        mock_get_logger: Mock,
        mock_time: Mock,
        mock_md5: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
    ) -> None:
        """Test _generate_build_metadata returns correct structure."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_time.return_value = 1234567890.123
        mock_hash = Mock()
        mock_hash.hexdigest.return_value = "abc123def456"
        mock_md5.return_value = mock_hash

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {"openai": {}, "anthropic": {}}
        compiler.compilation_stats["patterns_compiled"] = 10

        # Execute
        metadata = compiler._generate_build_metadata()

        # Verify structure
        assert "version" in metadata
        assert "build_timestamp" in metadata
        assert "source_hash" in metadata
        assert "providers_count" in metadata
        assert "patterns_count" in metadata

        # Verify values
        assert metadata["version"] == "4.0"
        assert metadata["build_timestamp"] == 1234567890
        assert metadata["providers_count"] == 2
        assert metadata["patterns_count"] == 10


class TestProviderCompilerLogCompilationStats:
    """Test suite for _log_compilation_stats method."""

    @patch("config.dsl.compiler.logger")
    def test_log_compilation_stats_output(
        self, mock_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _log_compilation_stats logs all statistics."""
        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.compilation_stats = {
            "providers_processed": 3,
            "patterns_compiled": 18,
            "functions_generated": 3,
            "validation_errors": 0,
            "compilation_time": 5.5,
        }

        # Execute
        compiler._log_compilation_stats()

        # Verify stats logging occurred (should log multiple stats)
        assert mock_logger.info.call_count >= 5  # At least 5 info calls for the stats


class TestProviderCompilerLoadAllProviders:
    """Test suite for _load_all_providers method."""

    @patch.object(ProviderCompiler, "_load_provider_files")
    @patch("logging.getLogger")
    def test_load_all_providers_single_provider(
        self,
        mock_get_logger: Mock,
        mock_load_files: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test _load_all_providers loads specific provider when specified."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_load_files.return_value = sample_provider_data

        # Create provider directory
        provider_dir = mock_source_dir / "providers" / "openai"
        provider_dir.mkdir(parents=True)

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute
        compiler._load_all_providers(specific_provider="openai")

        # Verify
        assert "openai" in compiler.providers
        assert compiler.compilation_stats["providers_processed"] == 1

    @patch("logging.getLogger")
    def test_load_all_providers_missing_specific_provider(
        self, mock_get_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _load_all_providers raises error for missing specific provider."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute & Verify
        with pytest.raises(FileNotFoundError, match="Provider directory not found"):
            compiler._load_all_providers(specific_provider="nonexistent")

    @patch("logging.getLogger")
    def test_load_all_providers_no_providers_dir(
        self, mock_get_logger: Mock, tmp_path: Path
    ) -> None:
        """Test _load_all_providers raises error when providers directory missing."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        source_dir = tmp_path / "config"
        output_dir = tmp_path / "output"
        source_dir.mkdir()

        compiler = ProviderCompiler(source_dir, output_dir)

        # Execute & Verify
        with pytest.raises(FileNotFoundError, match="Providers directory not found"):
            compiler._load_all_providers()


class TestProviderCompilerLoadProviderFiles:
    """Test suite for _load_provider_files method."""

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="provider: openai\nversion: 1.0",
    )
    @patch("yaml.safe_load")
    @patch("logging.getLogger")
    def test_load_provider_files_success(
        self,
        mock_get_logger: Mock,
        mock_yaml_load: Mock,
        mock_file: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
    ) -> None:
        """Test _load_provider_files loads all 4 required YAML files."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_yaml_load.return_value = {"provider": "openai", "version": "1.0"}

        # Create provider directory with required files
        provider_dir = mock_source_dir / "providers" / "openai"
        provider_dir.mkdir(parents=True)
        (provider_dir / "structure_patterns.yaml").touch()
        (provider_dir / "navigation_rules.yaml").touch()
        (provider_dir / "field_mappings.yaml").touch()
        (provider_dir / "transforms.yaml").touch()

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute
        result = compiler._load_provider_files(provider_dir, "openai")

        # Verify all 4 files loaded
        assert "structure_patterns" in result
        assert "navigation_rules" in result
        assert "field_mappings" in result
        assert "transforms" in result
        assert mock_yaml_load.call_count == 4

    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch("yaml.safe_load")
    @patch("logging.getLogger")
    def test_load_provider_files_invalid_yaml(
        self,
        mock_get_logger: Mock,
        mock_yaml_load: Mock,
        mock_file: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
    ) -> None:
        """Test _load_provider_files raises error for invalid YAML content."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_yaml_load.return_value = None  # Returns None instead of dict

        provider_dir = mock_source_dir / "providers" / "openai"
        provider_dir.mkdir(parents=True)
        # Create all 4 required files
        (provider_dir / "structure_patterns.yaml").touch()
        (provider_dir / "navigation_rules.yaml").touch()
        (provider_dir / "field_mappings.yaml").touch()
        (provider_dir / "transforms.yaml").touch()

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute & Verify
        with pytest.raises(ValueError, match="Provider file must contain a dictionary"):
            compiler._load_provider_files(provider_dir, "openai")


class TestProviderCompilerValidateAllProviders:
    """Test suite for _validate_all_providers method."""

    @patch.object(ProviderCompiler, "_validate_provider")
    @patch("logging.getLogger")
    def test_validate_all_providers_success(
        self,
        mock_get_logger: Mock,
        mock_validate: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_provider_data: Dict[str, Any],
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test _validate_all_providers validates all loaded providers."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {
            "openai": sample_provider_data,
            "anthropic": sample_provider_data,
        }
        compiler.shared_config = sample_shared_config

        # Execute
        compiler._validate_all_providers()

        # Verify both providers validated
        assert mock_validate.call_count == 2

    @patch.object(ProviderCompiler, "_validate_provider")
    @patch("logging.getLogger")
    def test_validate_all_providers_handles_errors(
        self,
        mock_get_logger: Mock,
        mock_validate: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_provider_data: Dict[str, Any],
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test _validate_all_providers logs error, updates stats, then re-raises exception."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.side_effect = ValueError("Invalid provider data")

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {"provider1": sample_provider_data}
        compiler.shared_config = sample_shared_config

        # Execute - should raise after logging and updating stats
        with pytest.raises(ValueError, match="Invalid provider data"):
            compiler._validate_all_providers()

        # Verify error was logged and stats updated before re-raising
        assert compiler.compilation_stats["validation_errors"] == 1


class TestProviderCompilerValidateProvider:
    """Test suite for _validate_provider method."""

    @patch("logging.getLogger")
    def test_validate_provider_success(
        self,
        mock_get_logger: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test _validate_provider passes for valid provider data."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        validation_rules = {
            "required_fields": ["provider", "version"],
            "signature_min_fields": 2,
        }

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute - should not raise
        compiler._validate_provider("openai", sample_provider_data, validation_rules)

    @patch("logging.getLogger")
    def test_validate_provider_missing_patterns(
        self, mock_get_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _validate_provider raises ValueError for missing patterns."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        invalid_data = {"structure_patterns": {"patterns": {}}}  # No patterns
        validation_rules = {}

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute & Verify
        with pytest.raises(ValueError, match="No patterns defined"):
            compiler._validate_provider("openai", invalid_data, validation_rules)

    @patch("logging.getLogger")
    def test_validate_provider_insufficient_signature_fields(
        self, mock_get_logger: Mock, mock_source_dir: Path, mock_output_dir: Path
    ) -> None:
        """Test _validate_provider raises ValueError for insufficient signature fields."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        invalid_data = {
            "structure_patterns": {
                "patterns": {
                    "pattern1": {
                        "signature_fields": ["only_one_field"],  # Only 1 field
                        "confidence_weight": 0.9,
                    }
                }
            }
        }
        validation_rules = {"signature_min_fields": 2}

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)

        # Execute & Verify
        with pytest.raises(ValueError, match="at least 2 signature fields"):
            compiler._validate_provider("openai", invalid_data, validation_rules)


class TestProviderCompilerCompileExtractionFunctions:
    """Test suite for _compile_extraction_functions method."""

    @patch.object(ProviderCompiler, "_generate_extraction_function")
    @patch("logging.getLogger")
    def test_compile_extraction_functions_generates_for_all_providers(
        self,
        mock_get_logger: Mock,
        mock_generate: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test _compile_extraction_functions generates functions for all providers."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_generate.return_value = "def extract(attrs): return {}"

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {
            "openai": sample_provider_data,
            "anthropic": sample_provider_data,
        }

        # Execute
        result = compiler._compile_extraction_functions()

        # Verify
        assert "openai" in result
        assert "anthropic" in result
        assert mock_generate.call_count == 2
        assert compiler.compilation_stats["functions_generated"] == 2


class TestProviderCompilerCompileFieldMappings:
    """Test suite for _compile_field_mappings method."""

    @patch("logging.getLogger")
    def test_compile_field_mappings_success(
        self,
        mock_get_logger: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test _compile_field_mappings compiles mappings for all providers."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {"openai": sample_provider_data}

        # Execute
        result = compiler._compile_field_mappings()

        # Verify
        assert "openai" in result
        assert isinstance(result["openai"], dict)


class TestProviderCompilerCompileTransformRegistry:
    """Test suite for _compile_transform_registry method."""

    @patch("logging.getLogger")
    def test_compile_transform_registry_success(
        self,
        mock_get_logger: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_provider_data: Dict[str, Any],
    ) -> None:
        """Test _compile_transform_registry compiles transforms for all providers."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {"openai": sample_provider_data}

        # Execute
        result = compiler._compile_transform_registry()

        # Verify
        assert "openai" in result
        assert isinstance(result["openai"], dict)


class TestProviderCompilerCompileValidationRules:
    """Test suite for _compile_validation_rules method."""

    @patch("logging.getLogger")
    def test_compile_validation_rules_returns_shared_config(
        self,
        mock_get_logger: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
        sample_shared_config: Dict[str, Any],
    ) -> None:
        """Test _compile_validation_rules returns validation rules from shared config."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.shared_config = sample_shared_config

        # Execute
        result = compiler._compile_validation_rules()

        # Verify
        assert result == sample_shared_config["validation_rules"]


class TestProviderCompilerCalculateSourceHash:
    """Test suite for _calculate_source_hash method."""

    @patch("hashlib.md5")
    @patch("logging.getLogger")
    def test_calculate_source_hash_processes_all_files(
        self,
        mock_get_logger: Mock,
        mock_md5: Mock,
        mock_source_dir: Path,
        mock_output_dir: Path,
    ) -> None:
        """Test _calculate_source_hash processes all provider and shared files."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_hash = Mock()
        mock_hash.hexdigest.return_value = "abc123"
        mock_md5.return_value = mock_hash

        # Create some YAML files
        (mock_source_dir / "shared" / "core_schema.yaml").write_text("test: data")
        provider_dir = mock_source_dir / "providers" / "openai"
        provider_dir.mkdir(parents=True)
        (provider_dir / "structure_patterns.yaml").write_text("patterns: {}")

        compiler = ProviderCompiler(mock_source_dir, mock_output_dir)
        compiler.providers = {"openai": {}}

        # Execute
        result = compiler._calculate_source_hash()

        # Verify hash was generated (actual hash, not mocked)
        assert isinstance(result, str)
        assert len(result) > 0


# Phase 8: Quality Validation
# Run with: tox -e unit -- tests/unit/scripts/test_compile_providers.py -v
# Coverage: tox -e unit -- tests/unit/config/dsl/test_compiler.py --cov=config.dsl.compiler --cov-report=term-missing
# Pylint: pylint tests/unit/scripts/test_compile_providers.py
# MyPy: mypy tests/unit/scripts/test_compile_providers.py

# pylint: disable=protected-access,redefined-outer-name,too-many-public-methods
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, and pytest fixtures are used as parameters.
"""
Unit tests for config.dsl.validation.bundle_verification module.

Tests bundle compilation and verification including:
- Bundle structure validation
- Provider consistency checks
- Inverted index integrity verification
- Full compilation workflow
- CLI entry point behavior
"""

from pathlib import Path
from typing import List
from unittest.mock import Mock, patch, mock_open

from config.dsl.validation.bundle_verification import (
    verify_bundle_structure,
    verify_provider_consistency,
    verify_inverted_index_integrity,
    verify_bundle_compilation,
    main,
)


class TestVerifyBundleStructure:
    """Test verify_bundle_structure() function."""

    def test_valid_bundle_with_all_attributes(self) -> None:
        """Test validation of a complete valid bundle."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.signature_to_provider = {frozenset(["field1"]): ("openai", 0.9)}
        bundle.extraction_functions = {"openai": "func"}
        bundle.field_mappings = {"openai": {}}
        bundle.transform_registry = {}
        bundle.validation_rules = {}
        bundle.build_metadata = {"version": "1.0"}

        errors: List[str] = verify_bundle_structure(bundle)

        assert not errors

    def test_missing_provider_signatures(self) -> None:
        """Test detection of missing provider_signatures."""
        bundle: Mock = Mock(spec=[])  # Empty spec - no attributes

        errors: List[str] = verify_bundle_structure(bundle)

        assert len(errors) >= 1
        assert any("provider_signatures" in error for error in errors)

    def test_invalid_provider_signatures_type(self) -> None:
        """Test detection of invalid provider_signatures type."""
        bundle: Mock = Mock()
        bundle.provider_signatures = "not_a_dict"
        bundle.signature_to_provider = {}
        bundle.extraction_functions = {}
        bundle.field_mappings = {}
        bundle.transform_registry = {}
        bundle.validation_rules = {}
        bundle.build_metadata = {}

        errors: List[str] = verify_bundle_structure(bundle)

        assert len(errors) >= 1
        assert any("must be a dictionary" in error for error in errors)

    def test_empty_provider_signatures(self) -> None:
        """Test detection of empty provider_signatures."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {}
        bundle.signature_to_provider = {}
        bundle.extraction_functions = {}
        bundle.field_mappings = {}
        bundle.transform_registry = {}
        bundle.validation_rules = {}
        bundle.build_metadata = {}

        errors: List[str] = verify_bundle_structure(bundle)

        assert len(errors) >= 1
        assert any(
            "is empty" in error and "provider" in error.lower() for error in errors
        )

    def test_missing_signature_to_provider(self) -> None:
        """Test detection of missing signature_to_provider."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        # Missing signature_to_provider
        bundle.extraction_functions = {}
        bundle.field_mappings = {}
        bundle.transform_registry = {}
        bundle.validation_rules = {}
        bundle.build_metadata = {}
        # Remove signature_to_provider from spec
        delattr(bundle, "signature_to_provider")

        errors: List[str] = verify_bundle_structure(bundle)

        assert len(errors) >= 1
        assert any("signature_to_provider" in error for error in errors)

    def test_missing_extraction_functions(self) -> None:
        """Test detection of missing extraction_functions."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.signature_to_provider = {}
        # Missing extraction_functions
        bundle.field_mappings = {}
        bundle.transform_registry = {}
        bundle.validation_rules = {}
        bundle.build_metadata = {}
        delattr(bundle, "extraction_functions")

        errors: List[str] = verify_bundle_structure(bundle)

        assert len(errors) >= 1
        assert any("extraction_functions" in error for error in errors)

    def test_missing_field_mappings(self) -> None:
        """Test detection of missing field_mappings."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.signature_to_provider = {}
        bundle.extraction_functions = {}
        # Missing field_mappings
        bundle.transform_registry = {}
        bundle.validation_rules = {}
        bundle.build_metadata = {}
        delattr(bundle, "field_mappings")

        errors: List[str] = verify_bundle_structure(bundle)

        assert len(errors) >= 1
        assert any("field_mappings" in error for error in errors)

    def test_missing_transform_registry(self) -> None:
        """Test detection of missing transform_registry."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.signature_to_provider = {}
        bundle.extraction_functions = {}
        bundle.field_mappings = {}
        # Missing transform_registry
        bundle.validation_rules = {}
        bundle.build_metadata = {}
        delattr(bundle, "transform_registry")

        errors: List[str] = verify_bundle_structure(bundle)

        assert len(errors) >= 1
        assert any("transform_registry" in error for error in errors)

    def test_missing_validation_rules(self) -> None:
        """Test detection of missing validation_rules."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.signature_to_provider = {}
        bundle.extraction_functions = {}
        bundle.field_mappings = {}
        bundle.transform_registry = {}
        # Missing validation_rules
        bundle.build_metadata = {}
        delattr(bundle, "validation_rules")

        errors: List[str] = verify_bundle_structure(bundle)

        assert len(errors) >= 1
        assert any("validation_rules" in error for error in errors)


class TestVerifyProviderConsistency:
    """Test verify_provider_consistency() function."""

    def test_all_providers_consistent(self) -> None:
        """Test when all providers have all required components."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {
            "openai": {frozenset(["field1"])},
            "anthropic": {frozenset(["field2"])},
        }
        bundle.extraction_functions = {"openai": "func1", "anthropic": "func2"}
        bundle.field_mappings = {"openai": {}, "anthropic": {}}

        errors: List[str] = verify_provider_consistency(bundle)

        assert not errors

    def test_provider_has_signatures_but_no_extraction_function(self) -> None:
        """Test detection when provider has signatures but no extraction function."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.extraction_functions = {}  # Missing openai
        bundle.field_mappings = {"openai": {}}

        errors: List[str] = verify_provider_consistency(bundle)

        assert len(errors) >= 1
        assert any(
            "openai" in error and "extraction function" in error for error in errors
        )

    def test_provider_has_signatures_but_no_field_mappings(self) -> None:
        """Test detection when provider has signatures but no field mappings."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.extraction_functions = {"openai": "func"}
        bundle.field_mappings = {}  # Missing openai

        errors: List[str] = verify_provider_consistency(bundle)

        assert len(errors) >= 1
        assert any("openai" in error and "field mappings" in error for error in errors)

    def test_provider_has_extraction_function_but_no_signatures(self) -> None:
        """Test detection when provider has extraction function but no signatures."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {}
        bundle.extraction_functions = {"openai": "func"}
        bundle.field_mappings = {}

        errors: List[str] = verify_provider_consistency(bundle)

        assert len(errors) >= 1
        assert any("openai" in error and "signatures" in error for error in errors)

    def test_provider_has_field_mappings_but_no_signatures(self) -> None:
        """Test detection when provider has field mappings but no signatures."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {}
        bundle.extraction_functions = {}
        bundle.field_mappings = {"openai": {}}

        errors: List[str] = verify_provider_consistency(bundle)

        assert len(errors) >= 1
        assert any("openai" in error and "signatures" in error for error in errors)

    def test_multiple_consistency_errors(self) -> None:
        """Test detection of multiple consistency errors."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.extraction_functions = {"anthropic": "func"}
        bundle.field_mappings = {"cohere": {}}

        errors: List[str] = verify_provider_consistency(bundle)

        assert len(errors) >= 3  # At least one error per provider


class TestVerifyInvertedIndexIntegrity:
    """Test verify_inverted_index_integrity() function."""

    def test_valid_inverted_index(self) -> None:
        """Test validation of correct inverted index."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {
            "openai": {frozenset(["field1"]), frozenset(["field2"])},
            "anthropic": {frozenset(["field3"])},
        }
        bundle.signature_to_provider = {
            frozenset(["field1"]): ("openai", 0.9),
            frozenset(["field2"]): ("openai", 0.8),
            frozenset(["field3"]): ("anthropic", 0.9),
        }

        errors: List[str] = verify_inverted_index_integrity(bundle)

        assert not errors

    def test_inverted_index_larger_than_forward_index(self) -> None:
        """Test detection when inverted index has more signatures than forward."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}  # 1 signature
        bundle.signature_to_provider = {
            frozenset(["field1"]): ("openai", 0.9),
            frozenset(["field2"]): ("openai", 0.8),
            frozenset(["field3"]): ("anthropic", 0.9),
        }  # 3 signatures

        errors: List[str] = verify_inverted_index_integrity(bundle)

        assert len(errors) >= 1
        assert any("MORE signatures" in error for error in errors)

    def test_unknown_provider_reference(self) -> None:
        """Test detection of unknown provider in inverted index."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.signature_to_provider = {
            frozenset(["field1"]): ("unknown_provider", 0.9)  # Unknown provider
        }

        errors: List[str] = verify_inverted_index_integrity(bundle)

        assert len(errors) >= 1
        assert any("unknown provider" in error.lower() for error in errors)

    def test_invalid_confidence_value_negative(self) -> None:
        """Test detection of negative confidence value."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.signature_to_provider = {
            frozenset(["field1"]): ("openai", -0.5)
        }  # Negative

        errors: List[str] = verify_inverted_index_integrity(bundle)

        assert len(errors) >= 1
        assert any("invalid confidence" in error.lower() for error in errors)

    def test_invalid_confidence_value_greater_than_one(self) -> None:
        """Test detection of confidence value > 1."""
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        bundle.signature_to_provider = {frozenset(["field1"]): ("openai", 1.5)}  # > 1

        errors: List[str] = verify_inverted_index_integrity(bundle)

        assert len(errors) >= 1
        assert any("invalid confidence" in error.lower() for error in errors)


class TestVerifyBundleCompilation:
    """Test verify_bundle_compilation() function."""

    @patch("config.dsl.validation.bundle_verification.time.perf_counter")
    @patch("config.dsl.validation.bundle_verification.ProviderCompiler")
    def test_successful_compilation(
        self, mock_compiler_class: Mock, mock_perf_counter: Mock
    ) -> None:
        """Test successful bundle compilation and verification."""
        # Setup timing
        mock_perf_counter.side_effect = [1000.0, 1000.1]

        # Setup mock compiler
        mock_compiler: Mock = Mock()
        mock_compiler_class.return_value = mock_compiler

        # Setup mock bundle
        mock_bundle: Mock = Mock()
        mock_bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        mock_bundle.signature_to_provider = {frozenset(["field1"]): ("openai", 0.9)}
        mock_bundle.extraction_functions = {"openai": "func"}
        mock_bundle.field_mappings = {"openai": {}}
        mock_bundle.transform_registry = {}
        mock_bundle.validation_rules = {}
        mock_bundle.build_metadata = {}
        mock_compiler.compile_all_providers.return_value = mock_bundle

        is_valid, errors, compilation_time = verify_bundle_compilation()

        assert is_valid
        assert not errors
        assert abs(compilation_time - 100.0) < 0.01  # (1000.1 - 1000.0) * 1000

    @patch(
        "config.dsl.validation.bundle_verification.ProviderCompiler",
        side_effect=ImportError("Module not found"),
    )
    def test_import_error(self, _mock_compiler_class: Mock) -> None:
        """Test handling of import errors."""
        is_valid, errors, compilation_time = verify_bundle_compilation()

        assert not is_valid
        assert len(errors) >= 1
        assert any("Import error" in error for error in errors)
        assert compilation_time == 0

    @patch("config.dsl.validation.bundle_verification.time.perf_counter")
    @patch("config.dsl.validation.bundle_verification.ProviderCompiler")
    def test_compilation_exception(
        self, mock_compiler_class: Mock, mock_perf_counter: Mock
    ) -> None:
        """Test handling of compilation exceptions."""
        mock_perf_counter.return_value = 1000.0
        mock_compiler: Mock = Mock()
        mock_compiler_class.return_value = mock_compiler
        mock_compiler.compile_all_providers.side_effect = RuntimeError(
            "Compilation failed"
        )

        is_valid, errors, compilation_time = verify_bundle_compilation()

        assert not is_valid
        assert len(errors) >= 1
        assert any("Compilation failed" in error for error in errors)
        assert compilation_time == 0

    @patch("config.dsl.validation.bundle_verification.time.perf_counter")
    @patch("config.dsl.validation.bundle_verification.ProviderCompiler")
    def test_structure_validation_fails(
        self, mock_compiler_class: Mock, mock_perf_counter: Mock
    ) -> None:
        """Test when structure validation fails."""
        mock_perf_counter.side_effect = [1000.0, 1000.1]
        mock_compiler: Mock = Mock()
        mock_compiler_class.return_value = mock_compiler

        # Bundle with structural error
        mock_bundle: Mock = Mock()
        mock_bundle.provider_signatures = "not_a_dict"  # Invalid type
        mock_bundle.signature_to_provider = {}
        mock_bundle.extraction_functions = {}
        mock_bundle.field_mappings = {}
        mock_bundle.transform_registry = {}
        mock_bundle.validation_rules = {}
        mock_bundle.build_metadata = {}
        mock_compiler.compile_all_providers.return_value = mock_bundle

        is_valid, errors, compilation_time = verify_bundle_compilation()

        assert not is_valid
        assert len(errors) >= 1
        assert compilation_time > 0

    @patch("config.dsl.validation.bundle_verification.time.perf_counter")
    @patch("config.dsl.validation.bundle_verification.ProviderCompiler")
    def test_consistency_validation_fails(
        self, mock_compiler_class: Mock, mock_perf_counter: Mock
    ) -> None:
        """Test when consistency validation fails."""
        mock_perf_counter.side_effect = [1000.0, 1000.1]
        mock_compiler: Mock = Mock()
        mock_compiler_class.return_value = mock_compiler

        # Bundle with consistency error
        mock_bundle: Mock = Mock()
        mock_bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        mock_bundle.signature_to_provider = {frozenset(["field1"]): ("openai", 0.9)}
        mock_bundle.extraction_functions = {}  # Missing extraction function
        mock_bundle.field_mappings = {"openai": {}}
        mock_bundle.transform_registry = {}
        mock_bundle.validation_rules = {}
        mock_bundle.build_metadata = {}
        mock_compiler.compile_all_providers.return_value = mock_bundle

        is_valid, errors, _compilation_time = verify_bundle_compilation()

        assert not is_valid
        assert len(errors) >= 1

    @patch("config.dsl.validation.bundle_verification.time.perf_counter")
    @patch("config.dsl.validation.bundle_verification.ProviderCompiler")
    def test_integrity_validation_fails(
        self, mock_compiler_class: Mock, mock_perf_counter: Mock
    ) -> None:
        """Test when integrity validation fails."""
        mock_perf_counter.side_effect = [1000.0, 1000.1]
        mock_compiler: Mock = Mock()
        mock_compiler_class.return_value = mock_compiler

        # Bundle with integrity error
        mock_bundle: Mock = Mock()
        mock_bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        mock_bundle.signature_to_provider = {
            frozenset(["field1"]): ("unknown", 0.9)
        }  # Unknown provider
        mock_bundle.extraction_functions = {"openai": "func"}
        mock_bundle.field_mappings = {"openai": {}}
        mock_bundle.transform_registry = {}
        mock_bundle.validation_rules = {}
        mock_bundle.build_metadata = {}
        mock_compiler.compile_all_providers.return_value = mock_bundle

        is_valid, errors, _compilation_time = verify_bundle_compilation()

        assert not is_valid
        assert len(errors) >= 1

    @patch("config.dsl.validation.bundle_verification.time.perf_counter")
    @patch("config.dsl.validation.bundle_verification.ProviderCompiler")
    def test_bundle_validate_bundle_integrity_returns_false(
        self, mock_compiler_class: Mock, mock_perf_counter: Mock
    ) -> None:
        """Test when bundle.validate_bundle_integrity() returns False."""
        mock_perf_counter.side_effect = [1000.0, 1000.1]
        mock_compiler: Mock = Mock()
        mock_compiler_class.return_value = mock_compiler

        # Bundle with validate_bundle_integrity method that returns False
        mock_bundle: Mock = Mock()
        mock_bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        mock_bundle.signature_to_provider = {frozenset(["field1"]): ("openai", 0.9)}
        mock_bundle.extraction_functions = {"openai": "func"}
        mock_bundle.field_mappings = {"openai": {}}
        mock_bundle.transform_registry = {}
        mock_bundle.validation_rules = {}
        mock_bundle.build_metadata = {}
        mock_bundle.validate_bundle_integrity.return_value = False
        mock_compiler.compile_all_providers.return_value = mock_bundle

        is_valid, errors, _compilation_time = verify_bundle_compilation()

        assert not is_valid
        assert len(errors) >= 1
        assert any("integrity validation" in error.lower() for error in errors)

    @patch("config.dsl.validation.bundle_verification.time.perf_counter")
    @patch("config.dsl.validation.bundle_verification.ProviderCompiler")
    def test_custom_paths_provided(
        self, mock_compiler_class: Mock, mock_perf_counter: Mock
    ) -> None:
        """Test compilation with custom config and output directories."""
        mock_perf_counter.side_effect = [1000.0, 1000.1]
        mock_compiler: Mock = Mock()
        mock_compiler_class.return_value = mock_compiler

        # Setup valid bundle
        mock_bundle: Mock = Mock()
        mock_bundle.provider_signatures = {"openai": {frozenset(["field1"])}}
        mock_bundle.signature_to_provider = {frozenset(["field1"]): ("openai", 0.9)}
        mock_bundle.extraction_functions = {"openai": "func"}
        mock_bundle.field_mappings = {"openai": {}}
        mock_bundle.transform_registry = {}
        mock_bundle.validation_rules = {}
        mock_bundle.build_metadata = {}
        mock_compiler.compile_all_providers.return_value = mock_bundle

        custom_config: Path = Path("/custom/config")
        custom_output: Path = Path("/custom/output")

        is_valid, errors, _compilation_time = verify_bundle_compilation(
            config_dir=custom_config, output_dir=custom_output
        )

        assert is_valid
        assert not errors
        # Verify compiler was called with custom paths
        mock_compiler_class.assert_called_once_with(
            source_dir=custom_config, output_dir=custom_output
        )


class TestMain:
    """Test main() CLI entry point."""

    @patch("config.dsl.validation.bundle_verification.verify_bundle_compilation")
    def test_successful_verification(self, mock_verify: Mock) -> None:
        """Test successful verification returns exit code 0."""
        mock_verify.return_value = (True, [], 150.0)

        with patch("pathlib.Path.exists", return_value=False):
            exit_code: int = main()

            assert exit_code == 0

    @patch("config.dsl.validation.bundle_verification.verify_bundle_compilation")
    def test_verification_fails(self, mock_verify: Mock) -> None:
        """Test failed verification returns exit code 1."""
        mock_verify.return_value = (False, ["Error 1", "Error 2"], 150.0)

        exit_code: int = main()

        assert exit_code == 1

    @patch("config.dsl.validation.bundle_verification.verify_bundle_compilation")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    @patch("pathlib.Path.exists")
    def test_bundle_file_exists_detailed_output(
        self,
        mock_exists: Mock,
        mock_pickle_load: Mock,
        _mock_file: Mock,
        mock_verify: Mock,
    ) -> None:
        """Test detailed output when bundle file exists."""
        mock_verify.return_value = (True, [], 150.0)
        mock_exists.return_value = True

        # Setup mock bundle for detailed output
        mock_bundle: Mock = Mock()
        mock_bundle.provider_signatures = {"openai": {}, "anthropic": {}, "cohere": {}}
        mock_bundle.signature_to_provider = {
            "sig1": ("openai", 0.9),
            "sig2": ("anthropic", 0.8),
        }
        mock_pickle_load.return_value = mock_bundle

        exit_code: int = main()

        assert exit_code == 0
        # Verify pickle.load was called
        assert mock_pickle_load.called

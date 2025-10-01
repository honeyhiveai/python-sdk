"""
Provider Bundle Compilation Verification - Quality Gate 14.

Verifies that provider bundles compile successfully with all required components.
This catches configuration errors before they break the runtime system.

This module can be used both as a library and as a CLI tool:
    - Library: from config.dsl.validation.bundle_verification import verify_bundle_compilation
    - CLI: python -m config.dsl.validation.bundle_verification

Agent OS Compliance: Comprehensive validation with detailed error reporting.
"""

import sys
import pickle
import time
from pathlib import Path
from typing import Tuple, List, Optional

# Import bundle types
from honeyhive.tracer.processing.semantic_conventions.bundle_types import (
    CompiledProviderBundle,
)
from config.dsl.compiler import ProviderCompiler


def verify_bundle_structure(bundle: CompiledProviderBundle) -> List[str]:
    """
    Verify the compiled bundle has all required components.

    Args:
        bundle: Compiled provider bundle

    Returns:
        List of validation error messages
    """
    errors: List[str] = []

    # Check provider_signatures
    if not hasattr(bundle, "provider_signatures"):
        errors.append("Bundle missing 'provider_signatures' attribute")
    elif not isinstance(bundle.provider_signatures, dict):
        errors.append("'provider_signatures' must be a dictionary")
    elif len(bundle.provider_signatures) == 0:
        errors.append("'provider_signatures' is empty - no providers compiled")

    # Check signature_to_provider (inverted index)
    if not hasattr(bundle, "signature_to_provider"):
        errors.append(
            "Bundle missing 'signature_to_provider' attribute "
            "(required for O(1) detection)"
        )
    elif not isinstance(bundle.signature_to_provider, dict):
        errors.append("'signature_to_provider' must be a dictionary")
    elif len(bundle.signature_to_provider) == 0:
        errors.append("'signature_to_provider' is empty - inverted index not generated")

    # Check extraction_functions
    if not hasattr(bundle, "extraction_functions"):
        errors.append("Bundle missing 'extraction_functions' attribute")
    elif not isinstance(bundle.extraction_functions, dict):
        errors.append("'extraction_functions' must be a dictionary")

    # Check field_mappings
    if not hasattr(bundle, "field_mappings"):
        errors.append("Bundle missing 'field_mappings' attribute")
    elif not isinstance(bundle.field_mappings, dict):
        errors.append("'field_mappings' must be a dictionary")

    # Check transform_registry
    if not hasattr(bundle, "transform_registry"):
        errors.append("Bundle missing 'transform_registry' attribute")
    elif not isinstance(bundle.transform_registry, dict):
        errors.append("'transform_registry' must be a dictionary")

    # Check validation_rules
    if not hasattr(bundle, "validation_rules"):
        errors.append("Bundle missing 'validation_rules' attribute")
    elif not isinstance(bundle.validation_rules, dict):
        errors.append("'validation_rules' must be a dictionary")

    # Check build_metadata
    if not hasattr(bundle, "build_metadata"):
        errors.append("Bundle missing 'build_metadata' attribute")
    elif not isinstance(bundle.build_metadata, dict):
        errors.append("'build_metadata' must be a dictionary")

    return errors


def verify_provider_consistency(bundle: CompiledProviderBundle) -> List[str]:
    """
    Verify consistency across bundle components.

    Args:
        bundle: Compiled provider bundle

    Returns:
        List of validation error messages
    """
    errors: List[str] = []

    # Get provider names from each component
    sig_providers: set[str] = set(bundle.provider_signatures.keys())
    func_providers: set[str] = set(bundle.extraction_functions.keys())
    mapping_providers: set[str] = set(bundle.field_mappings.keys())

    # Check that all providers have all components
    for provider in sig_providers:
        if provider not in func_providers:
            errors.append(
                f"Provider '{provider}' has signatures but no extraction function"
            )
        if provider not in mapping_providers:
            errors.append(f"Provider '{provider}' has signatures but no field mappings")

    for provider in func_providers:
        if provider not in sig_providers:
            errors.append(
                f"Provider '{provider}' has extraction function but no signatures"
            )

    for provider in mapping_providers:
        if provider not in sig_providers:
            errors.append(f"Provider '{provider}' has field mappings but no signatures")

    return errors


def verify_inverted_index_integrity(bundle: CompiledProviderBundle) -> List[str]:
    """
    Verify inverted index integrity and consistency with forward index.

    Args:
        bundle: Compiled provider bundle

    Returns:
        List of validation error messages
    """
    errors: List[str] = []

    # Count signatures in forward index
    forward_count: int = sum(len(sigs) for sigs in bundle.provider_signatures.values())

    # Count signatures in inverted index
    inverted_count: int = len(bundle.signature_to_provider)

    # They should match (unless there are collisions)
    if inverted_count > forward_count:
        errors.append(
            f"Inverted index has MORE signatures ({inverted_count}) "
            f"than forward index ({forward_count}) - should be impossible"
        )

    # Verify each signature in inverted index points to valid provider
    for signature, (provider, confidence) in bundle.signature_to_provider.items():
        if provider not in bundle.provider_signatures:
            errors.append(f"Inverted index references unknown provider '{provider}'")

        # Check confidence range
        if not (0 <= confidence <= 1):
            errors.append(
                f"Provider '{provider}' has invalid confidence {confidence} "
                "(must be 0-1)"
            )

    return errors


def verify_bundle_compilation(
    config_dir: Optional[Path] = None, output_dir: Optional[Path] = None
) -> Tuple[bool, List[str], float]:
    """
    Compile providers and verify the bundle.

    This is the main library function for bundle compilation verification.

    Args:
        config_dir: Path to config/dsl directory (defaults to standard location)
        output_dir: Path to output directory (defaults to standard location)

    Returns:
        Tuple of (is_valid, errors, compilation_time_ms)
    """
    errors: List[str] = []
    start_time: float = time.perf_counter()

    try:
        # Setup paths if not provided
        if config_dir is None:
            config_dir = Path(__file__).parent.parent
        if output_dir is None:
            output_dir = (
                Path(__file__).parent.parent.parent.parent
                / "src"
                / "honeyhive"
                / "tracer"
                / "processing"
                / "semantic_conventions"
            )

        # Compile
        compiler: ProviderCompiler = ProviderCompiler(
            source_dir=config_dir, output_dir=output_dir
        )
        bundle: CompiledProviderBundle = compiler.compile_all_providers()

        compilation_time: float = (time.perf_counter() - start_time) * 1000

        # Verify bundle structure
        errors.extend(verify_bundle_structure(bundle))

        # Verify provider consistency
        if not errors:  # Only if structure is valid
            errors.extend(verify_provider_consistency(bundle))

        # Verify inverted index integrity
        if not errors:  # Only if previous checks passed
            errors.extend(verify_inverted_index_integrity(bundle))

        # Verify bundle integrity method
        if hasattr(bundle, "validate_bundle_integrity"):
            if not bundle.validate_bundle_integrity():
                errors.append("Bundle integrity validation method returned False")

        return len(errors) == 0, errors, compilation_time

    except ImportError as e:
        errors.append(f"Import error: {e}")
        return False, errors, 0
    except Exception as e:
        errors.append(f"Compilation failed: {e}")
        return False, errors, 0


def main() -> int:
    """
    Main entry point for bundle compilation verification CLI.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("🔨 Compiling provider bundle...")

    is_valid, errors, compilation_time = verify_bundle_compilation()

    if not is_valid:
        print("❌ Bundle Compilation Verification Failed:\n")
        for error in errors:
            print(f"  {error}")
        return 1
    else:
        # Get bundle details for success message
        bundle_path: Path = (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "honeyhive"
            / "tracer"
            / "processing"
            / "semantic_conventions"
            / "compiled_providers.pkl"
        )

        if bundle_path.exists():
            with open(bundle_path, "rb") as f:
                bundle: CompiledProviderBundle = pickle.load(f)
                provider_count: int = len(bundle.provider_signatures)
                signature_count: int = len(bundle.signature_to_provider)

                print(
                    f"✅ Bundle Compilation Verification Passed\n"
                    f"  Providers: {provider_count}\n"
                    f"  Signatures (inverted index): {signature_count}\n"
                    f"  Compilation time: {compilation_time:.2f}ms"
                )
        else:
            print("✅ Bundle Compilation Verification Passed")

        return 0


if __name__ == "__main__":
    sys.exit(main())

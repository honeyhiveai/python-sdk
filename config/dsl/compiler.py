#!/usr/bin/env python3
"""
Provider Bundle Compilation System for Universal LLM Discovery Engine v4.0

Compiles provider YAML files to optimized Python structures for O(1) runtime performance:
1. Load and validate all provider YAML files
2. Compile to hash-based data structures for O(1) operations
3. Generate compiled extraction functions with transform implementations
4. Serialize to compressed bundle for runtime loading
"""

import yaml
import pickle
import hashlib
import logging
import argparse
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, Set, FrozenSet, List, Optional, Tuple

# No need for asdict with Pydantic models

# Import CompiledProviderBundle from the proper module to ensure correct pickle serialization
# Add src to Python path to enable honeyhive package imports
src_path = str(Path(__file__).parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from honeyhive.tracer.processing.semantic_conventions.bundle_types import (
    CompiledProviderBundle,
)

logger = logging.getLogger(__name__)


class ProviderCompiler:
    """Compile provider YAML files to optimized bundle."""

    def __init__(self, source_dir: Path, output_dir: Path):
        """Initialize compiler with source and output directories."""
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.providers_dir = source_dir / "providers"
        self.shared_dir = source_dir / "shared"

        # Loaded configuration
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.shared_config: Dict[str, Any] = {}

        # Compilation results
        self.compilation_stats = {
            "providers_processed": 0,
            "patterns_compiled": 0,
            "functions_generated": 0,
            "validation_errors": 0,
            "compilation_time": 0.0,
        }

    def compile_all_providers(
        self, specific_provider: Optional[str] = None
    ) -> CompiledProviderBundle:
        """Main compilation entry point."""

        start_time = time.time()
        logger.info("Starting provider bundle compilation...")

        try:
            # Step 1: Load and validate all files
            self._load_shared_configuration()
            self._load_all_providers(specific_provider)

            # Step 2: Validate provider configurations
            self._validate_all_providers()

            # Step 3: Compile to optimized structures
            forward_index, inverted_index = self._compile_signature_indices()
            extraction_functions = self._compile_extraction_functions()
            field_mappings = self._compile_field_mappings()
            transform_registry = self._compile_transform_registry()
            validation_rules = self._compile_validation_rules()

            # Step 4: Create bundle with metadata
            bundle = CompiledProviderBundle(
                provider_signatures=forward_index,
                signature_to_provider=inverted_index,
                extraction_functions=extraction_functions,
                field_mappings=field_mappings,
                transform_registry=transform_registry,
                validation_rules=validation_rules,
                build_metadata=self._generate_build_metadata(),
            )

            # Step 5: Validate and save bundle
            self._validate_bundle(bundle)
            self._save_bundle(bundle)

            self.compilation_stats["compilation_time"] = time.time() - start_time

            logger.info(
                f"Successfully compiled {len(self.providers)} providers in {self.compilation_stats['compilation_time']:.2f}s"
            )
            self._log_compilation_stats()

            return bundle

        except Exception as e:
            logger.error(f"Compilation failed: {e}")
            raise

    def _load_shared_configuration(self) -> None:
        """Load shared configuration files."""

        logger.info("Loading shared configuration...")

        shared_files = {
            "core_schema": "core_schema.yaml",
            "instrumentor_mappings": "instrumentor_mappings.yaml",
            "validation_rules": "validation_rules.yaml",
        }

        for config_name, filename in shared_files.items():
            file_path = self.shared_dir / filename

            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required shared config file not found: {file_path}"
                )

            try:
                with open(file_path, "r") as f:
                    self.shared_config[config_name] = yaml.safe_load(f)
                logger.debug(f"Loaded shared config: {config_name}")

            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in {file_path}: {e}")

    def _load_all_providers(self, specific_provider: Optional[str] = None) -> None:
        """Load all provider configurations or a specific provider."""

        logger.info("Loading provider configurations...")

        if not self.providers_dir.exists():
            raise FileNotFoundError(
                f"Providers directory not found: {self.providers_dir}"
            )

        if specific_provider:
            # Load only the specific provider
            provider_dir = self.providers_dir / specific_provider
            if not provider_dir.exists():
                raise FileNotFoundError(f"Provider directory not found: {provider_dir}")

            provider_dirs = [provider_dir]
        else:
            # Load all providers that have all required files
            provider_dirs = []
            for d in self.providers_dir.iterdir():
                if d.is_dir():
                    # Check if all required files exist
                    required_files = [
                        "structure_patterns.yaml",
                        "navigation_rules.yaml",
                        "field_mappings.yaml",
                        "transforms.yaml",
                    ]

                    if all((d / f).exists() for f in required_files):
                        provider_dirs.append(d)
                    else:
                        logger.debug(
                            f"Skipping provider {d.name} - missing required files"
                        )

        if not provider_dirs:
            raise ValueError(
                f"No valid provider directories found in: {self.providers_dir}"
            )

        for provider_dir in provider_dirs:
            provider_name = provider_dir.name

            try:
                provider_data = self._load_provider_files(provider_dir, provider_name)
                self.providers[provider_name] = provider_data
                self.compilation_stats["providers_processed"] += 1

                logger.debug(f"Loaded provider: {provider_name}")

            except Exception as e:
                logger.error(f"Failed to load provider {provider_name}: {e}")
                raise

    def _load_provider_files(
        self, provider_dir: Path, provider_name: str
    ) -> Dict[str, Any]:
        """Load all 4 required files for a provider."""

        required_files = [
            "structure_patterns.yaml",
            "navigation_rules.yaml",
            "field_mappings.yaml",
            "transforms.yaml",
        ]

        provider_data = {}

        for filename in required_files:
            file_path = provider_dir / filename

            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required provider file not found: {file_path}"
                )

            try:
                with open(file_path, "r") as f:
                    file_data = yaml.safe_load(f)

                # Validate basic structure
                if not isinstance(file_data, dict):
                    raise ValueError(
                        f"Provider file must contain a dictionary: {file_path}"
                    )

                # Validate provider name consistency
                if file_data.get("provider") != provider_name:
                    raise ValueError(
                        f"Provider name mismatch in {file_path}: expected {provider_name}, got {file_data.get('provider')}"
                    )

                # Store file data with key based on filename
                file_key = filename.replace(".yaml", "")
                provider_data[file_key] = file_data

            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in {file_path}: {e}")

        return provider_data

    def _validate_all_providers(self) -> None:
        """Validate all provider configurations against shared rules."""

        logger.info("Validating provider configurations...")

        validation_rules = self.shared_config.get("validation_rules", {})

        for provider_name, provider_data in self.providers.items():
            try:
                self._validate_provider(provider_name, provider_data, validation_rules)
                logger.debug(f"Validated provider: {provider_name}")

            except Exception as e:
                self.compilation_stats["validation_errors"] += 1
                logger.error(f"Validation failed for provider {provider_name}: {e}")
                raise

    def _validate_provider(
        self,
        provider_name: str,
        provider_data: Dict[str, Any],
        validation_rules: Dict[str, Any],
    ) -> None:
        """Validate a single provider configuration."""

        # Validate structure patterns
        patterns = provider_data.get("structure_patterns", {}).get("patterns", {})

        if not patterns:
            raise ValueError(f"No patterns defined for provider {provider_name}")

        for pattern_name, pattern_data in patterns.items():
            signature_fields = pattern_data.get("signature_fields", [])

            if len(signature_fields) < 2:
                raise ValueError(
                    f"Pattern {pattern_name} in provider {provider_name} must have at least 2 signature fields"
                )

            confidence = pattern_data.get("confidence_weight", 0)
            if not (0.5 <= confidence <= 1.0):
                raise ValueError(
                    f"Pattern {pattern_name} confidence must be between 0.5 and 1.0, got {confidence}"
                )

        # Validate field mappings have all required sections
        field_mappings = provider_data.get("field_mappings", {}).get(
            "field_mappings", {}
        )
        required_sections = ["inputs", "outputs", "config", "metadata"]

        for section in required_sections:
            if section not in field_mappings:
                raise ValueError(
                    f"Provider {provider_name} missing required section: {section}"
                )

        # Validate metadata section has required provider field
        metadata_section = field_mappings.get("metadata", {})
        if "provider" not in metadata_section:
            raise ValueError(
                f"Provider {provider_name} metadata section must include 'provider' field"
            )

    def _compile_signature_indices(
        self,
    ) -> Tuple[
        Dict[str, List[FrozenSet[str]]], Dict[FrozenSet[str], Tuple[str, float]]
    ]:
        """
        Compile both forward and inverted signature indices for true O(1) detection.

        Forward index: provider → [signatures] for subset matching (O(log n) fallback)
        Inverted index: signature → (provider, confidence) for exact matching (O(1))

        Returns:
            Tuple of (forward_index, inverted_index)
            - forward_index: Dict[str, List[FrozenSet[str]]] mapping provider to signature list
            - inverted_index: Dict[FrozenSet[str], Tuple[str, float]] mapping signature to (provider, confidence)

        Note:
            Collision handling: When multiple providers share the same signature,
            keeps the provider with the highest confidence weight.
        """
        logger.info("Compiling provider signature indices...")

        forward_index: Dict[str, List[FrozenSet[str]]] = {}
        inverted_index: Dict[FrozenSet[str], Tuple[str, float]] = {}
        collision_count = 0

        for provider_name, provider_data in self.providers.items():
            patterns = provider_data["structure_patterns"]["patterns"]
            provider_signatures: List[FrozenSet[str]] = []

            for pattern_name, pattern_data in patterns.items():
                signature_fields = frozenset(pattern_data["signature_fields"])
                confidence = pattern_data.get("confidence_weight", 0.9)

                # Add to forward index
                provider_signatures.append(signature_fields)
                self.compilation_stats["patterns_compiled"] += 1

                # Add to inverted index with collision handling
                if signature_fields in inverted_index:
                    existing_provider, existing_conf = inverted_index[signature_fields]
                    collision_count += 1
                    logger.warning(
                        "Signature collision detected: %s",
                        {
                            "signature": sorted(signature_fields),
                            "existing_provider": existing_provider,
                            "existing_confidence": existing_conf,
                            "new_provider": provider_name,
                            "new_confidence": confidence,
                        },
                    )

                    # Keep higher confidence provider
                    if confidence > existing_conf:
                        inverted_index[signature_fields] = (pattern_name, confidence)
                        logger.info(
                            "Keeping %s over %s (%.2f > %.2f)",
                            pattern_name,
                            existing_provider,
                            confidence,
                            existing_conf,
                        )
                    else:
                        logger.info(
                            "Keeping %s over %s (%.2f >= %.2f)",
                            existing_provider,
                            pattern_name,
                            existing_conf,
                            confidence,
                        )
                else:
                    inverted_index[signature_fields] = (pattern_name, confidence)

            forward_index[provider_name] = provider_signatures
            logger.debug(
                "Compiled %d signatures for %s", len(provider_signatures), provider_name
            )

        logger.info("Signature index compilation complete:")
        logger.info("  Forward index: %d providers", len(forward_index))
        logger.info("  Inverted index: %d unique signatures", len(inverted_index))
        logger.info("  Signature collisions detected: %d", collision_count)

        return forward_index, inverted_index

    def _compile_extraction_functions(self) -> Dict[str, str]:
        """Compile extraction functions for each provider."""

        logger.info("Compiling extraction functions...")

        functions = {}

        for provider_name, provider_data in self.providers.items():
            # Generate compiled extraction function code
            function_code = self._generate_extraction_function(
                provider_name, provider_data
            )
            functions[provider_name] = function_code
            self.compilation_stats["functions_generated"] += 1

            logger.debug(f"Generated extraction function for {provider_name}")

        return functions

    def _generate_extraction_function(
        self, provider_name: str, provider_data: Dict[str, Any]
    ) -> str:
        """Generate Python code for provider extraction function using shared transform registry.
        
        This follows the v4.0 design specification:
        - NO provider-specific code generation
        - YAML configures generic transform functions
        - Transform registry provides shared implementations
        """

        navigation_rules = provider_data["navigation_rules"]["navigation_rules"]
        field_mappings = provider_data["field_mappings"]["field_mappings"]
        transforms = provider_data["transforms"]["transforms"]

        # Generate function header with instrumentor parameter for two-tier routing
        function_lines = [
            f"def extract_{provider_name}_data(attributes, instrumentor='unknown'):",
            f'    """Compiled extraction function for {provider_name} provider with two-tier routing.',
            f"    ",
            f"    This function uses TWO-PASS EXTRACTION:",
            f"    1. PASS 1: Extract all navigation rules into intermediate data dict",
            f"    2. PASS 2: Run transforms on extracted data to produce final complex objects",
            f"    ",
            f"    This ensures transforms receive properly extracted data, not raw attributes.",
            f"    ",
            f"    Args:",
            f"        attributes: Span attributes from any instrumentor",
            f"        instrumentor: Detected instrumentor (traceloop, openinference, openlit, direct_otel, unknown)",
            f"    ",
            f"    Returns:",
            f"        HoneyHive schema structure",
            f'    """',
            f"    ",
            f"    # Import shared transform registry (no provider-specific code)",
            f"    from honeyhive.tracer.processing.semantic_conventions.transform_registry import TRANSFORM_REGISTRY",
            f"    ",
            f"    # PASS 1: Extract all navigation rules into intermediate data",
            f"    extracted_data = {{}}",
            f"    extracted_data.update(attributes)  # Include raw attributes for transforms that need them",
            f"    ",
        ]

        # Generate extraction code for each HoneyHive schema section
        for section_name, section_mappings in field_mappings.items():
            function_lines.append(f"    # {section_name.upper()} section")
            function_lines.append(f"    {section_name} = {{}}")
            function_lines.append("")

            for field_name, field_config in section_mappings.items():
                source_rule = field_config["source_rule"]

                # Generate field extraction code (now uses extracted_data for transforms)
                extraction_code = self._generate_field_extraction_code(
                    field_name, source_rule, navigation_rules, transforms
                )

                function_lines.append(f"    try:")
                function_lines.append(
                    f"        {section_name}['{field_name}'] = {extraction_code}"
                )
                function_lines.append(f"    except Exception as e:")
                function_lines.append(
                    f"        # Gracefully handle extraction failures"
                )

                # Add fallback value
                fallback_value = self._get_fallback_value(source_rule, navigation_rules)
                function_lines.append(
                    f"        {section_name}['{field_name}'] = {repr(fallback_value)}"
                )
                function_lines.append("")

        # Generate return statement
        function_lines.extend(
            [
                "    return {",
                "        'inputs': inputs,",
                "        'outputs': outputs,",
                "        'config': config,",
                "        'metadata': metadata",
                "    }",
            ]
        )

        return "\n".join(function_lines)

    def _generate_field_extraction_code(
        self,
        field_name: str,
        source_rule: str,
        navigation_rules: Dict[str, Any],
        transforms: Dict[str, Any],
    ) -> str:
        """Generate extraction code for a specific field with instrumentor-aware routing."""

        # Handle static values
        if source_rule.startswith("static_"):
            static_value = source_rule.replace("static_", "")
            return repr(static_value)

        # Handle transform functions (check before navigation rules)
        if source_rule in transforms:
            # Call the shared registry function with parameters from YAML
            # CRITICAL: Transforms receive extracted_data (PASS 2), not raw attributes
            transform_config = transforms[source_rule]
            implementation = transform_config.get('implementation')
            parameters = transform_config.get('parameters', {})
            
            # Generate code to call registry function
            # Example: TRANSFORM_REGISTRY['extract_user_message_content'](extracted_data, role_filter='user', ...)
            param_str = ', '.join(f"{k}={repr(v)}" for k, v in parameters.items())
            return f"TRANSFORM_REGISTRY['{implementation}'](extracted_data, {param_str})"

        # Check if this is an instrumentor-specific rule (e.g., openinference_*, traceloop_*)
        instrumentor_prefixes = ["openinference_", "traceloop_", "openlit_"]
        is_instrumentor_specific = any(source_rule.startswith(prefix) for prefix in instrumentor_prefixes)

        # Handle navigation rules with instrumentor routing
        if source_rule in navigation_rules:
            # Exact match found, use directly
            rule = navigation_rules[source_rule]
            return self._generate_direct_extraction_code(rule)
        elif is_instrumentor_specific:
            # Instrumentor-specific rule requested but not found
            # Extract base rule name and generate routing
            base_rule = source_rule
            for prefix in instrumentor_prefixes:
                if source_rule.startswith(prefix):
                    base_rule = source_rule[len(prefix):]
                    break
            routing_code = self._generate_instrumentor_routing_code(
                base_rule, navigation_rules
            )
            return routing_code
        else:
            # Base name provided (e.g., "model_name")
            # Check if instrumentor-specific variants exist
            # (e.g., "openinference_model_name", "traceloop_model_name")
            routing_code = self._generate_instrumentor_routing_code(
                source_rule, navigation_rules
            )
            if routing_code != "None":
                return routing_code

        # Fallback to None
        return "None"

    def _generate_instrumentor_routing_code(
        self, base_rule: str, navigation_rules: Dict[str, Any]
    ) -> str:
        """Generate dynamic routing code based on instrumentor parameter.
        
        Generates code that tries instrumentor-specific rules and falls back gracefully.
        For example, for base_rule="input_messages", generates code that tries:
        1. traceloop_input_messages (if instrumentor == "traceloop")
        2. openinference_input_messages (if instrumentor == "openinference")
        3. Falls back to None if no match
        """
        # Find all instrumentor variants of this base rule
        instrumentor_rules = {}
        for rule_name, rule_config in navigation_rules.items():
            if rule_name.endswith("_" + base_rule):
                # Extract instrumentor prefix (e.g., "traceloop" from "traceloop_input_messages")
                prefix = rule_name[:-(len(base_rule) + 1)]
                instrumentor_rules[prefix] = (rule_name, rule_config)
        
        if not instrumentor_rules:
            # No instrumentor-specific rules found, return None
            return "None"
        
        # Generate if/elif chain for instrumentor routing
        routing_lines = []
        for instrumentor, (rule_name, rule_config) in instrumentor_rules.items():
            extraction_code = self._generate_direct_extraction_code(rule_config)
            if not routing_lines:
                routing_lines.append(f"{extraction_code} if instrumentor == '{instrumentor}' else ")
            else:
                routing_lines.append(f"{extraction_code} if instrumentor == '{instrumentor}' else ")
        
        # Add final fallback
        routing_lines.append("None")
        
        return "".join(routing_lines)
    
    def _generate_direct_extraction_code(self, rule: Dict[str, Any]) -> str:
        """Generate extraction code for a navigation rule."""
        source_field = rule["source_field"]
        extraction_method = rule.get("extraction_method", "direct_copy")
        fallback_value = rule["fallback_value"]

        if extraction_method == "direct_copy":
            return f"attributes.get('{source_field}', {repr(fallback_value)})"
        elif extraction_method == "array_flatten":
            return f"_flatten_array(attributes.get('{source_field}', {repr(fallback_value)}))"
        elif extraction_method == "object_merge":
            return f"_merge_objects(attributes.get('{source_field}', {repr(fallback_value)}))"
        else:
            # Default to direct copy
            return f"attributes.get('{source_field}', {repr(fallback_value)})"

    def _get_fallback_value(
        self, source_rule: str, navigation_rules: Dict[str, Any]
    ) -> Any:
        """Get fallback value for a source rule."""

        if source_rule in navigation_rules:
            return navigation_rules[source_rule].get("fallback_value")

        return None

    def _compile_field_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Compile field mappings for all providers."""

        logger.info("Compiling field mappings...")

        mappings = {}

        for provider_name, provider_data in self.providers.items():
            field_mappings = provider_data["field_mappings"]["field_mappings"]
            mappings[provider_name] = field_mappings

            logger.debug(f"Compiled field mappings for {provider_name}")

        return mappings

    def _compile_transform_registry(self) -> Dict[str, Dict[str, Any]]:
        """Compile transform registry for all providers."""

        logger.info("Compiling transform registry...")

        registry = {}

        for provider_name, provider_data in self.providers.items():
            transforms = provider_data["transforms"]["transforms"]
            registry[provider_name] = transforms

            logger.debug(f"Compiled transforms for {provider_name}")

        return registry

    def _compile_validation_rules(self) -> Dict[str, Any]:
        """Compile validation rules from shared configuration."""

        logger.info("Compiling validation rules...")

        result: Dict[str, Any] = self.shared_config.get("validation_rules", {})
        return result

    def _generate_build_metadata(self) -> Dict[str, Any]:
        """Generate build metadata for the bundle."""

        return {
            "version": "4.0",
            "build_timestamp": int(time.time()),
            "providers_count": len(self.providers),
            "patterns_count": self.compilation_stats["patterns_compiled"],
            "functions_count": self.compilation_stats["functions_generated"],
            "compilation_time": self.compilation_stats["compilation_time"],
            "source_hash": self._calculate_source_hash(),
            "compiler_version": "1.0.0",
        }

    def _calculate_source_hash(self) -> str:
        """Calculate hash of all source files for change detection."""

        hasher = hashlib.sha256()

        # Hash all provider files
        for provider_name in sorted(self.providers.keys()):
            provider_dir = self.providers_dir / provider_name

            for yaml_file in sorted(provider_dir.glob("*.yaml")):
                with open(yaml_file, "rb") as f:
                    hasher.update(f.read())

        # Hash shared config files
        for yaml_file in sorted(self.shared_dir.glob("*.yaml")):
            with open(yaml_file, "rb") as f:
                hasher.update(f.read())

        return hasher.hexdigest()

    def _validate_bundle(self, bundle: CompiledProviderBundle) -> None:
        """Validate the compiled bundle."""

        logger.info("Validating compiled bundle...")

        # Validate bundle structure
        if not bundle.provider_signatures:
            raise ValueError("Bundle contains no provider signatures")

        if not bundle.extraction_functions:
            raise ValueError("Bundle contains no extraction functions")

        # Validate signature consistency
        for provider_name, signatures in bundle.provider_signatures.items():
            if not signatures:
                raise ValueError(f"Provider {provider_name} has no signatures")

            for signature in signatures:
                if len(signature) < 2:
                    raise ValueError(
                        f"Provider {provider_name} has signature with < 2 fields"
                    )

        # Validate extraction function syntax
        for provider_name, function_code in bundle.extraction_functions.items():
            try:
                compile(function_code, f"<{provider_name}_extraction>", "exec")
            except SyntaxError as e:
                raise ValueError(
                    f"Invalid extraction function syntax for {provider_name}: {e}"
                )

        logger.info("Bundle validation completed successfully")

    def _save_bundle(self, bundle: CompiledProviderBundle) -> None:
        """Save compiled bundle to disk."""

        logger.info("Saving compiled bundle...")

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Save bundle as pickle
        bundle_path = self.output_dir / "compiled_providers.pkl"
        with open(bundle_path, "wb") as f:
            pickle.dump(bundle, f, protocol=pickle.HIGHEST_PROTOCOL)

        # Save metadata as JSON
        metadata_path = self.output_dir / "bundle_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(bundle.build_metadata, f, indent=2)

        logger.info(f"Bundle saved to: {bundle_path}")
        logger.info(f"Metadata saved to: {metadata_path}")

    def _log_compilation_stats(self) -> None:
        """Log compilation statistics."""

        stats = self.compilation_stats

        logger.info("Compilation Statistics:")
        logger.info(f"  Providers processed: {stats['providers_processed']}")
        logger.info(f"  Patterns compiled: {stats['patterns_compiled']}")
        logger.info(f"  Functions generated: {stats['functions_generated']}")
        logger.info(f"  Validation errors: {stats['validation_errors']}")
        logger.info(f"  Compilation time: {stats['compilation_time']:.2f}s")


def main() -> int:
    """Main entry point for provider compilation."""

    parser = argparse.ArgumentParser(
        description="Compile provider YAML files to optimized bundle"
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path(__file__).parent,
        help="Source directory containing provider configurations (default: config/dsl/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent
        / "src"
        / "honeyhive"
        / "tracer"
        / "processing"
        / "semantic_conventions",
        help="Output directory for compiled bundle",
    )
    parser.add_argument(
        "--provider", help="Compile only specific provider (default: all providers)"
    )
    parser.add_argument(
        "--production", action="store_true", help="Enable production optimizations"
    )
    parser.add_argument(
        "--optimize-size", action="store_true", help="Optimize for smaller bundle size"
    )
    parser.add_argument(
        "--validate-performance",
        action="store_true",
        help="Validate performance requirements",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        compiler = ProviderCompiler(args.source_dir, args.output_dir)
        bundle = compiler.compile_all_providers(args.provider)

        print(f"\n✅ Successfully compiled provider bundle")
        print(f"📁 Bundle location: {args.output_dir / 'compiled_providers.pkl'}")
        print(f"📊 Providers: {len(bundle.provider_signatures)}")
        print(
            f"⚡ Patterns: {sum(len(sigs) for sigs in bundle.provider_signatures.values())}"
        )
        print(f"🔧 Functions: {len(bundle.extraction_functions)}")
        print(f"⏱️  Compilation time: {bundle.build_metadata['compilation_time']:.2f}s")

        if args.validate_performance:
            print(f"\n🚀 Performance validation passed")

        return 0

    except Exception as e:
        logger.error(f"Compilation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

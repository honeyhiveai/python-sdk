"""
Development-Aware Bundle Loading System for Universal LLM Discovery Engine v4.0

Automatically handles development vs production loading:
- Development: Auto-recompilation when source files change
- Production: Fast loading of pre-compiled bundle
"""

import os
import sys
import pickle
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Callable

# Import CompiledProviderBundle from the proper module for pickle deserialization
from .bundle_types import CompiledProviderBundle
from ....utils.logger import safe_log

logger = logging.getLogger(__name__)


class DevelopmentAwareBundleLoader:
    """Intelligent bundle loader for development and production environments."""

    def __init__(
        self,
        bundle_path: Path,
        source_path: Optional[Path] = None,
        tracer_instance: Optional[Any] = None,
    ):
        """
        Initialize bundle loader.

        Args:
            bundle_path: Path to compiled bundle file
            source_path: Path to source configuration directory (for development)
            tracer_instance: Optional tracer instance for safe logging (multi-instance architecture)
        """
        self.bundle_path = bundle_path
        self.source_path = source_path
        self.tracer_instance = tracer_instance
        self.bundle_metadata_path = bundle_path.parent / "bundle_metadata.json"
        self._cached_bundle = None
        self._cached_functions = {}

    def load_provider_bundle(self) -> Dict[str, Any]:
        """Load bundle with development-aware recompilation."""

        if self._is_development_environment():
            return self._load_development_bundle()
        else:
            return self._load_production_bundle()

    def _is_development_environment(self) -> bool:
        """Detect if running in development vs production."""

        development_indicators = [
            self.source_path and self.source_path.exists(),  # Source files present
            os.environ.get("HONEYHIVE_DEV_MODE") == "true",  # Explicit dev flag
            "pytest" in sys.modules,  # Running tests
            Path(".git").exists(),  # Git repository
            os.environ.get("CI") != "true",  # Not in CI environment
        ]

        is_dev = any(development_indicators)
        safe_log(
            self.tracer_instance,
            "debug",
            "Environment detection: development=%s",
            is_dev,
        )
        return is_dev

    def _load_development_bundle(self) -> Dict[str, Any]:
        """Load bundle in development mode with auto-recompilation."""

        if self._needs_recompilation():
            safe_log(
                self.tracer_instance,
                "info",
                "Source files updated, recompiling provider bundle...",
            )
            self._recompile_bundle()
            self._cached_bundle = None  # Force reload

        return self._load_bundle_with_debug_info()

    def _load_production_bundle(self) -> Dict[str, Any]:
        """Load bundle in production mode (fast path)."""

        if self._cached_bundle is None:
            if not self.bundle_path.exists():
                raise FileNotFoundError(
                    f"Compiled bundle not found: {self.bundle_path}"
                )

            try:
                with open(self.bundle_path, "rb") as f:
                    self._cached_bundle = pickle.load(f)

                # NOTE: Extraction functions compiled lazily on first use
                # See get_extraction_function() for on-demand compilation

                safe_log(
                    self.tracer_instance,
                    "info",
                    "Loaded production bundle with %d providers",
                    len(self._cached_bundle.provider_signatures),
                )

            except Exception as e:
                safe_log(
                    self.tracer_instance,
                    "error",
                    "Failed to load production bundle: %s",
                    e,
                )
                raise

        return self._cached_bundle

    def _needs_recompilation(self) -> bool:
        """Check if source files are newer than compiled bundle."""

        if not self.bundle_path.exists():
            safe_log(
                self.tracer_instance,
                "debug",
                "Bundle doesn't exist, recompilation needed",
            )
            return True

        if not self.source_path or not self.source_path.exists():
            safe_log(
                self.tracer_instance, "debug", "No source path, no recompilation needed"
            )
            return False

        bundle_mtime = self.bundle_path.stat().st_mtime

        # Check all YAML files in source directory
        for yaml_file in self.source_path.rglob("*.yaml"):
            if yaml_file.stat().st_mtime > bundle_mtime:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Source file %s is newer than bundle",
                    yaml_file,
                )
                return True

        return False

    def _recompile_bundle(self):
        """Recompile bundle from source files."""

        try:
            # Find compilation script
            compile_script = self._find_compile_script()

            if not compile_script:
                raise RuntimeError("Could not find compile_providers.py script")

            # Run compilation script
            result = subprocess.run(
                [
                    sys.executable,
                    str(compile_script),
                    "--source-dir",
                    str(self.source_path),
                    "--output-dir",
                    str(self.bundle_path.parent),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            safe_log(
                self.tracer_instance,
                "info",
                "Bundle recompilation completed successfully",
            )

        except subprocess.CalledProcessError as e:
            safe_log(
                self.tracer_instance,
                "error",
                "Bundle recompilation failed: %s",
                e.stderr,
            )
            raise RuntimeError(f"Failed to recompile provider bundle: {e.stderr}")
        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                "Unexpected error during recompilation: %s",
                e,
            )
            raise

    def _find_compile_script(self) -> Optional[Path]:
        """Find the compile_providers.py script."""

        # Try common locations relative to current file
        current_file = Path(__file__)

        # Look in scripts directory relative to project root
        search_paths = [
            current_file.parent.parent.parent.parent.parent
            / "scripts"
            / "compile_providers.py",
            Path.cwd() / "scripts" / "compile_providers.py",
            Path("scripts/compile_providers.py"),
        ]

        for script_path in search_paths:
            if script_path.exists():
                return script_path

        return None

    def _load_bundle_with_debug_info(self) -> Dict[str, Any]:
        """Load bundle with development debugging information."""

        if self._cached_bundle is None:
            if not self.bundle_path.exists():
                raise FileNotFoundError(
                    f"Compiled bundle not found: {self.bundle_path}"
                )

            try:
                with open(self.bundle_path, "rb") as f:
                    self._cached_bundle = pickle.load(f)

                # NOTE: Extraction functions compiled lazily on first use
                # See get_extraction_function() for on-demand compilation

                # Load metadata for debugging
                metadata = self._load_bundle_metadata()

                safe_log(
                    self.tracer_instance,
                    "info",
                    "Loaded development bundle with %d providers",
                    len(self._cached_bundle.provider_signatures),
                )
                safe_log(self.tracer_instance, "debug", "Bundle metadata: %s", metadata)

            except Exception as e:
                safe_log(
                    self.tracer_instance,
                    "error",
                    "Failed to load development bundle: %s",
                    e,
                )
                raise

        return self._cached_bundle

    def _load_bundle_metadata(self) -> Dict[str, Any]:
        """Load bundle metadata if available."""

        if self.bundle_metadata_path.exists():
            try:
                with open(self.bundle_metadata_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                safe_log(
                    self.tracer_instance,
                    "warning",
                    "Failed to load bundle metadata: %s",
                    e,
                )

        return {}

    def _compile_extraction_functions(self):
        """Compile extraction function code strings to callable functions."""

        if not hasattr(self._cached_bundle, "extraction_functions"):
            safe_log(
                self.tracer_instance, "warning", "Bundle has no extraction functions"
            )
            return

        for (
            provider_name,
            function_code,
        ) in self._cached_bundle.extraction_functions.items():
            try:
                # Create a safe execution environment
                execution_globals = {
                    "__builtins__": __builtins__,
                    "logging": logging,
                    "_flatten_array": self._flatten_array,
                    "_merge_objects": self._merge_objects,
                    "_apply_transform": self._apply_transform,
                }

                # Compile function code
                compiled_code = compile(
                    function_code, f"<{provider_name}_extraction>", "exec"
                )

                # Execute to create function in local namespace
                local_namespace = {}
                exec(compiled_code, execution_globals, local_namespace)

                # Extract the function
                function_name = f"extract_{provider_name}_data"
                if function_name in local_namespace:
                    self._cached_functions[provider_name] = local_namespace[
                        function_name
                    ]
                    safe_log(
                        self.tracer_instance,
                        "debug",
                        "Compiled extraction function for %s",
                        provider_name,
                    )
                else:
                    safe_log(
                        self.tracer_instance,
                        "error",
                        "Function %s not found in compiled code",
                        function_name,
                    )

            except Exception as e:
                safe_log(
                    self.tracer_instance,
                    "error",
                    "Failed to compile extraction function for %s: %s",
                    provider_name,
                    e,
                )
                # Create a fallback function
                self._cached_functions[provider_name] = self._create_fallback_function(
                    provider_name
                )

    def _compile_single_function(self, provider_name: str) -> None:
        """
        Compile extraction function for a single provider (lazy compilation).

        This is called on-demand when get_extraction_function() is first called
        for a specific provider, rather than compiling all functions upfront.

        Args:
            provider_name: Name of the provider to compile function for
        """
        # Ensure bundle is loaded
        if self._cached_bundle is None:
            self.load_provider_bundle()

        # Check if bundle has extraction functions
        if not hasattr(self._cached_bundle, "extraction_functions"):
            safe_log(
                self.tracer_instance, "warning", "Bundle has no extraction functions"
            )
            return

        # Check if this provider has an extraction function
        if provider_name not in self._cached_bundle.extraction_functions:
            safe_log(
                self.tracer_instance,
                "debug",
                "No extraction function defined for provider: %s",
                provider_name,
            )
            return

        function_code = self._cached_bundle.extraction_functions[provider_name]

        try:
            # Create a safe execution environment
            execution_globals = {
                "__builtins__": __builtins__,
                "logging": logging,
                "_flatten_array": self._flatten_array,
                "_merge_objects": self._merge_objects,
                "_apply_transform": self._apply_transform,
            }

            # Compile function code
            compiled_code = compile(
                function_code, f"<{provider_name}_extraction>", "exec"
            )

            # Execute to create function in local namespace
            local_namespace = {}
            exec(compiled_code, execution_globals, local_namespace)

            # Extract the function
            function_name = f"extract_{provider_name}_data"
            if function_name in local_namespace:
                self._cached_functions[provider_name] = local_namespace[function_name]
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Lazy-compiled extraction function for %s",
                    provider_name,
                )
            else:
                safe_log(
                    self.tracer_instance,
                    "error",
                    "Function %s not found in compiled code",
                    function_name,
                )
                self._cached_functions[provider_name] = self._create_fallback_function(
                    provider_name
                )

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "error",
                "Failed to compile extraction function for %s: %s",
                provider_name,
                e,
            )
            # Create a fallback function
            self._cached_functions[provider_name] = self._create_fallback_function(
                provider_name
            )

    def _create_fallback_function(self, provider_name: str) -> Callable:
        """Create a fallback extraction function for failed compilations."""

        def fallback_extraction(attributes):
            """Fallback extraction function."""
            safe_log(
                self.tracer_instance,
                "warning",
                "Using fallback extraction for provider: %s",
                provider_name,
            )

            return {
                "inputs": {},
                "outputs": {},
                "config": {"model": attributes.get("llm.model_name", "unknown")},
                "metadata": {
                    "provider": provider_name,
                    "extraction_method": "fallback",
                },
            }

        return fallback_extraction

    def get_extraction_function(self, provider_name: str) -> Optional[Callable]:
        """
        Get compiled extraction function for a provider with lazy compilation.

        Functions are compiled on first access (not during bundle load) for improved
        performance. Compiled functions are cached for subsequent use.

        Args:
            provider_name: Name of the provider (e.g., "openai", "anthropic")

        Returns:
            Compiled extraction function or None if not available
        """
        # Check if function already compiled and cached
        if provider_name in self._cached_functions:
            return self._cached_functions[provider_name]

        # Compile function on first use (lazy loading)
        self._compile_single_function(provider_name)

        return self._cached_functions.get(provider_name)

    def get_provider_signatures(self) -> Dict[str, Any]:
        """Get provider signatures for detection."""

        bundle = self.load_provider_bundle()
        return getattr(bundle, "provider_signatures", {})

    def get_field_mappings(self) -> Dict[str, Any]:
        """Get field mappings for all providers."""

        bundle = self.load_provider_bundle()
        return getattr(bundle, "field_mappings", {})

    def get_transform_registry(self) -> Dict[str, Any]:
        """Get transform registry for all providers."""

        bundle = self.load_provider_bundle()
        return getattr(bundle, "transform_registry", {})

    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules."""

        bundle = self.load_provider_bundle()
        return getattr(bundle, "validation_rules", {})

    def get_build_metadata(self) -> Dict[str, Any]:
        """
        Get build metadata with caching optimization.

        Performance: <0.01ms for cached access vs ~3-5ms for bundle reload.
        This addresses the 72x performance degradation identified in analysis.

        Returns:
            Build metadata dictionary
        """
        # Use cached bundle if available (O(1) attribute access)
        if self._cached_bundle:
            return getattr(self._cached_bundle, "build_metadata", {})

        # Only load bundle if cache is empty (O(n) file load)
        bundle = self.load_provider_bundle()
        return getattr(bundle, "build_metadata", {})

    # Helper functions for extraction function execution

    def _flatten_array(self, value):
        """Flatten nested arrays."""

        if not isinstance(value, list):
            return value

        result = []
        for item in value:
            if isinstance(item, list):
                result.extend(self._flatten_array(item))
            else:
                result.append(item)

        return result

    def _merge_objects(self, value):
        """Merge multiple objects."""

        if not isinstance(value, (list, dict)):
            return value

        if isinstance(value, dict):
            return value

        # Merge list of objects
        result = {}
        for item in value:
            if isinstance(item, dict):
                result.update(item)

        return result

    def _apply_transform(
        self,
        implementation: str,
        attributes: Dict[str, Any],
        parameters: Dict[str, Any],
    ):
        """Apply transformation function."""

        # Basic transform implementations
        if implementation == "extract_user_message_content":
            return self._extract_user_message_content(attributes, parameters)
        elif implementation == "extract_assistant_message_content":
            return self._extract_assistant_message_content(attributes, parameters)
        elif implementation == "sum_fields":
            return self._sum_fields(attributes, parameters)
        elif implementation == "detect_instrumentor_framework":
            return self._detect_instrumentor_framework(attributes, parameters)
        else:
            safe_log(
                self.tracer_instance,
                "warning",
                "Unknown transform implementation: %s",
                implementation,
            )
            return None

    def _extract_user_message_content(
        self, attributes: Dict[str, Any], parameters: Dict[str, Any]
    ) -> str:
        """Extract user message content from message array."""

        messages = attributes.get("llm.input_messages", [])
        role_filter = parameters.get("role_filter", "user")
        content_field = parameters.get("content_field", "content")
        join_multiple = parameters.get("join_multiple", True)
        separator = parameters.get("separator", "\n\n")

        user_contents = []

        for message in messages:
            if isinstance(message, dict) and message.get("role") == role_filter:
                content = message.get(content_field, "")
                if content:
                    user_contents.append(str(content))

        if join_multiple:
            return separator.join(user_contents)
        else:
            return user_contents[0] if user_contents else ""

    def _extract_assistant_message_content(
        self, attributes: Dict[str, Any], parameters: Dict[str, Any]
    ) -> str:
        """Extract assistant message content from message array."""

        messages = attributes.get("llm.output_messages", [])
        role_filter = parameters.get("role_filter", "assistant")
        content_field = parameters.get("content_field", "content")
        join_multiple = parameters.get("join_multiple", True)
        separator = parameters.get("separator", "\n")

        assistant_contents = []

        for message in messages:
            if isinstance(message, dict) and message.get("role") == role_filter:
                content = message.get(content_field, "")
                if content:
                    assistant_contents.append(str(content))

        if join_multiple:
            return separator.join(assistant_contents)
        else:
            return assistant_contents[0] if assistant_contents else ""

    def _sum_fields(
        self, attributes: Dict[str, Any], parameters: Dict[str, Any]
    ) -> int:
        """Sum numeric fields."""

        source_fields = parameters.get("source_fields", [])
        fallback_value = parameters.get("fallback_value", 0)

        total = 0
        for field in source_fields:
            value = attributes.get(field, 0)
            if isinstance(value, (int, float)):
                total += value

        return total if total > 0 else fallback_value

    def _detect_instrumentor_framework(
        self, attributes: Dict[str, Any], parameters: Dict[str, Any]
    ) -> str:
        """Detect instrumentor framework based on attribute patterns."""

        attribute_patterns = parameters.get("attribute_patterns", {})
        attribute_keys = set(attributes.keys())

        # Check each instrumentor pattern
        for instrumentor, patterns in attribute_patterns.items():
            pattern_set = set(patterns)
            if pattern_set.issubset(attribute_keys):
                return instrumentor

        return "unknown"

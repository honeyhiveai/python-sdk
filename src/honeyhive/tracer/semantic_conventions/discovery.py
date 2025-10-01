"""Dynamic discovery system for semantic convention definitions.

This module provides automatic discovery and loading of all semantic convention
definitions from the definitions/ directory. It supports:

- Automatic version detection from filenames
- Dynamic loading of convention attributes
- Cache preloading for performance
- Multi-version support for the same provider

The discovery system scans for files matching the pattern:
{provider}_v{major}_{minor}_{patch}.py

Examples:
- openinference_v0_1_31.py
- traceloop_v0_46_2.py
- honeyhive_v1_0_0.py
"""

import importlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...utils.cache import CacheManager
from ...utils.logger import safe_log


@dataclass
class ConventionDefinition:
    """Represents a semantic convention definition."""

    provider: str
    version: Tuple[int, int, int]  # (major, minor, patch)
    attributes: Dict[str, str]
    source_file: str
    definition_data: Optional[Dict[str, Any]] = (
        None  # Raw definition data from CONVENTION_DEFINITION
    )

    @property
    def version_string(self) -> str:
        """Returns version as string (e.g., '0.1.31')."""
        return f"{self.version[0]}.{self.version[1]}.{self.version[2]}"

    @property
    def cache_key(self) -> str:
        """Returns cache key for this convention."""
        return f"{self.provider}_v{self.version[0]}_{self.version[1]}_{self.version[2]}"


class ConventionDiscovery:
    """Discovers and loads semantic convention definitions dynamically."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """Initialize the discovery system.

        Args:
            cache_manager: Optional cache manager for performance optimization
        """
        self.cache_manager = cache_manager
        self.definitions: Dict[str, ConventionDefinition] = {}
        self.providers: Dict[str, List[ConventionDefinition]] = {}
        self._definitions_dir = Path(__file__).parent / "definitions"

        # Pattern to match convention definition files
        # Format: {provider}_v{major}_{minor}_{patch}.py
        self._filename_pattern = re.compile(r"^([a-zA-Z_]+)_v(\d+)_(\d+)_(\d+)\.py$")

    def discover_all_conventions(self) -> Dict[str, ConventionDefinition]:
        """Discovers all semantic convention definitions.

        Scans the definitions/ directory for convention files and loads them.

        Returns:
            Dictionary mapping cache keys to ConventionDefinition objects
        """
        try:
            if not self._definitions_dir.exists():
                safe_log(
                    None,
                    "warning",
                    f"Definitions directory not found: {self._definitions_dir}",
                )
                return {}

            discovered_count = 0

            for file_path in self._definitions_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue

                definition = self._load_convention_file(file_path)
                if definition:
                    self.definitions[definition.cache_key] = definition

                    # Group by provider
                    if definition.provider not in self.providers:
                        self.providers[definition.provider] = []
                    self.providers[definition.provider].append(definition)

                    discovered_count += 1

            # Sort provider versions (newest first)
            for provider_definitions in self.providers.values():
                provider_definitions.sort(key=lambda d: d.version, reverse=True)

            safe_log(
                None,
                "info",
                f"Discovered {discovered_count} semantic convention definitions",
            )
            safe_log(None, "debug", f"Providers: {list(self.providers.keys())}")

            return self.definitions

        except Exception as e:
            safe_log(None, "error", f"Failed to discover conventions: {e}")
            return {}

    def _load_convention_file(self, file_path: Path) -> Optional[ConventionDefinition]:
        """Loads a single convention definition file.

        Args:
            file_path: Path to the convention definition file

        Returns:
            ConventionDefinition object or None if loading failed
        """
        try:
            # Parse filename to extract provider and version
            match = self._filename_pattern.match(file_path.name)
            if not match:
                safe_log(
                    None,
                    "warning",
                    f"Skipping file with invalid name format: {file_path.name}",
                )
                return None

            provider = match.group(1)
            major = int(match.group(2))
            minor = int(match.group(3))
            patch = int(match.group(4))
            version = (major, minor, patch)

            # Dynamic import of the module
            module_name = (
                f"honeyhive.tracer.semantic_conventions.definitions.{file_path.stem}"
            )
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                # Try relative import
                module_name = f".definitions.{file_path.stem}"
                module = importlib.import_module(
                    module_name, package="src.honeyhive.tracer.semantic_conventions"
                )

            # Look for the convention definition
            # First try the new structured format: CONVENTION_DEFINITION
            convention_def = None
            if hasattr(module, "CONVENTION_DEFINITION"):
                convention_def = getattr(module, "CONVENTION_DEFINITION")
                if isinstance(convention_def, dict):
                    # Extract all attribute names from the structured definition
                    attributes = self._extract_attributes_from_definition(
                        convention_def
                    )
                    if not attributes:
                        safe_log(
                            None,
                            "warning",
                            (
                                f"No attributes found in CONVENTION_DEFINITION "
                                f"in {file_path.name}"
                            ),
                        )
                        return None
                else:
                    safe_log(
                        None,
                        "warning",
                        (
                            f"CONVENTION_DEFINITION in {file_path.name} "
                            "is not a dictionary"
                        ),
                    )
                    return None
            else:
                # Fallback to legacy format:
                # {PROVIDER}_V{MAJOR}_{MINOR}_{PATCH}_ATTRIBUTES
                attr_name = (
                    f"{provider.upper()}_V{major}_{minor}_{patch}_ATTRIBUTES"
                )

                if not hasattr(module, attr_name):
                    safe_log(
                        None,
                        "warning",
                        (
                            f"No convention definition found in {file_path.name} "
                            f"(expected: CONVENTION_DEFINITION or {attr_name})"
                        ),
                    )
                    return None

                attributes = getattr(module, attr_name)
                if not isinstance(attributes, dict):
                    safe_log(
                        None,
                        "warning",
                        f"Attributes in {file_path.name} is not a dictionary",
                    )
                    return None

            definition = ConventionDefinition(
                provider=provider,
                version=version,
                attributes=attributes,
                source_file=str(file_path),
                definition_data=convention_def,  # Store raw definition data
            )

            safe_log(
                None,
                "debug",
                (
                    f"Loaded {provider} v{definition.version_string} "
                    f"with {len(attributes)} attributes"
                ),
            )
            return definition

        except Exception as e:
            safe_log(
                None, "error", f"Failed to load convention file {file_path}: {e}"
            )
            return None

    def _extract_attributes_from_definition(
        self, convention_def: Dict[str, Any]
    ) -> Dict[str, str]:
        """Extract attribute names and descriptions from structured definition.
        
        Args:
            convention_def: The CONVENTION_DEFINITION dictionary

        Returns:
            Dictionary mapping attribute names to descriptions
        """
        attributes = {}

        try:
            # Extract from input_mapping
            if (
                "input_mapping" in convention_def
                and "mappings" in convention_def["input_mapping"]
            ):
                for attr_name, mapping in convention_def["input_mapping"][
                    "mappings"
                ].items():
                    description = mapping.get(
                        "description", f"Input attribute: {attr_name}"
                    )
                    attributes[attr_name] = description

            # Extract from output_mapping
            if (
                "output_mapping" in convention_def
                and "mappings" in convention_def["output_mapping"]
            ):
                for attr_name, mapping in convention_def["output_mapping"][
                    "mappings"
                ].items():
                    description = mapping.get(
                        "description", f"Output attribute: {attr_name}"
                    )
                    attributes[attr_name] = description

            # Extract from config_mapping
            if (
                "config_mapping" in convention_def
                and "mappings" in convention_def["config_mapping"]
            ):
                for attr_name, mapping in convention_def["config_mapping"][
                    "mappings"
                ].items():
                    description = mapping.get(
                        "description", f"Config attribute: {attr_name}"
                    )
                    attributes[attr_name] = description

            # Extract from metadata_mapping
            if (
                "metadata_mapping" in convention_def
                and "mappings" in convention_def["metadata_mapping"]
            ):
                for attr_name, mapping in convention_def["metadata_mapping"][
                    "mappings"
                ].items():
                    description = mapping.get(
                        "description", f"Metadata attribute: {attr_name}"
                    )
                    attributes[attr_name] = description

            # Extract from detection_patterns if available
            if "detection_patterns" in convention_def:
                patterns = convention_def["detection_patterns"]
                if "signature_attributes" in patterns:
                    for attr_name in patterns["signature_attributes"]:
                        if attr_name not in attributes:
                            attributes[attr_name] = f"Signature attribute: {attr_name}"
                if "unique_attributes" in patterns:
                    for attr_name in patterns["unique_attributes"]:
                        if attr_name not in attributes:
                            attributes[attr_name] = f"Unique attribute: {attr_name}"

        except Exception as e:
            safe_log(
                None,
                "warning",
                f"Error extracting attributes from convention definition: {e}",
            )

        return attributes

    def get_latest_version(self, provider: str) -> Optional[ConventionDefinition]:
        """Gets the latest version of a provider's convention.

        Args:
            provider: Name of the provider (e.g., 'openinference', 'traceloop')

        Returns:
            ConventionDefinition for the latest version, or None if not found
        """
        if provider not in self.providers:
            return None

        # Providers are already sorted with newest first
        return self.providers[provider][0]

    def get_specific_version(
        self, provider: str, version: Tuple[int, int, int]
    ) -> Optional[ConventionDefinition]:
        """Gets a specific version of a provider's convention.

        Args:
            provider: Name of the provider
            version: Version tuple (major, minor, patch)

        Returns:
            ConventionDefinition for the specific version, or None if not found
        """
        cache_key = f"{provider}_v{version[0]}_{version[1]}_{version[2]}"
        return self.definitions.get(cache_key)

    def get_all_versions(self, provider: str) -> List[ConventionDefinition]:
        """Gets all versions of a provider's convention.

        Args:
            provider: Name of the provider

        Returns:
            List of ConventionDefinition objects, sorted newest first
        """
        return self.providers.get(provider, [])

    def preload_cache(self) -> bool:
        """Preloads all convention definitions into cache for performance.

        Returns:
            True if successful, False otherwise
        """
        if not self.cache_manager:
            safe_log(None, "debug", "No cache manager available for preloading")
            return False

        try:
            preloaded_count = 0

            for cache_key, definition in self.definitions.items():
                try:
                    # Cache the full definition
                    definitions_cache = self.cache_manager.get_cache(
                        "convention_definitions"
                    )
                    definitions_cache.set(cache_key, definition, ttl=3600)

                    # Cache individual attribute lookups for fast detection
                    attributes_cache = self.cache_manager.get_cache(
                        "convention_attributes"
                    )
                    for attr_name in definition.attributes.keys():
                        attr_cache_key = f"attr_{attr_name}_{definition.provider}"
                        attributes_cache.set(
                            attr_cache_key, definition.provider, ttl=3600
                        )

                    preloaded_count += 1

                except Exception as cache_error:
                    safe_log(
                        None,
                        "warning",
                        f"Failed to cache definition {cache_key}: {cache_error}",
                    )
                    continue

            safe_log(
                None,
                "info",
                f"Preloaded {preloaded_count} convention definitions into cache",
            )
            return preloaded_count > 0

        except Exception as e:
            safe_log(None, "error", f"Failed to preload cache: {e}")
            return False

    def get_provider_for_attribute(self, attribute_name: str) -> Optional[str]:
        """Fast lookup to find which provider defines an attribute.

        Args:
            attribute_name: Name of the attribute to look up

        Returns:
            Provider name or None if not found
        """
        # Try cache first
        if self.cache_manager:
            try:
                attr_cache_key = f"attr_{attribute_name}"
                attributes_cache = self.cache_manager.get_cache("convention_attributes")
                cached_provider = attributes_cache.get(attr_cache_key)
                if cached_provider:
                    return str(cached_provider)
            except Exception:
                pass  # Fall back to direct lookup

        # Direct lookup
        for definition in self.definitions.values():
            if attribute_name in definition.attributes:
                return definition.provider

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Returns statistics about discovered conventions.

        Returns:
            Dictionary with discovery statistics
        """
        stats: Dict[str, Any] = {
            "total_definitions": len(self.definitions),
            "total_providers": len(self.providers),
            "providers": {},
        }

        for provider, definitions in self.providers.items():
            stats["providers"][provider] = {
                "versions": len(definitions),
                "latest_version": (
                    definitions[0].version_string if definitions else None
                ),
                "total_attributes": sum(len(d.attributes) for d in definitions),
            }

        return stats


# Global discovery instance (lazy initialization)
_discovery_instance: Optional[ConventionDiscovery] = None


def get_discovery_instance(
    cache_manager: Optional[CacheManager] = None,
) -> ConventionDiscovery:
    """Gets the global discovery instance (singleton pattern).

    Args:
        cache_manager: Optional cache manager for the first initialization

    Returns:
        ConventionDiscovery instance
    """
    global _discovery_instance  # pylint: disable=global-statement

    if _discovery_instance is None:
        _discovery_instance = ConventionDiscovery(cache_manager)
        # Auto-discover on first access
        _discovery_instance.discover_all_conventions()
        # Preload cache if available
        if cache_manager:
            _discovery_instance.preload_cache()

    return _discovery_instance


def discover_semantic_conventions(
    cache_manager: Optional[CacheManager] = None,
) -> Dict[str, ConventionDefinition]:
    """Convenience function to discover all semantic conventions.

    Args:
        cache_manager: Optional cache manager for performance optimization

    Returns:
        Dictionary mapping cache keys to ConventionDefinition objects
    """
    discovery = get_discovery_instance(cache_manager)
    return discovery.definitions

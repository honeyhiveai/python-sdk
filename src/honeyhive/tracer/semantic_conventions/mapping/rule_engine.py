"""Dynamic rule engine for semantic convention mapping.

This module provides the core rule creation and coordination logic for the
modular semantic convention system. It replaces hardcoded mapping logic
with pure configuration-driven rule generation.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ....utils.logger import safe_log
from ..discovery import ConventionDefinition


@dataclass
class MappingRule:
    """Represents a mapping rule from source attribute to target field."""

    source_pattern: str  # Source attribute pattern (supports wildcards)
    target_field: str  # Target field in HoneyHive schema
    target_path: str  # Dot-separated path
    # (e.g., "inputs.chat_history", "metadata.usage.total_tokens")
    transform: Optional[str] = None  # Optional transformation function name
    condition: Optional[str] = None  # Optional condition for applying the rule


class RuleEngine:
    """Dynamic rule creation and coordination engine.

    This class replaces the monolithic ConfigDrivenMapper with focused
    rule creation logic that reads mapping patterns from definition files.
    """

    def __init__(self) -> None:
        """Initialize the rule engine."""
        self._rule_cache: Dict[str, List[MappingRule]] = {}

    def create_rules(self, definition: ConventionDefinition) -> List[MappingRule]:
        """Creates mapping rules dynamically from definition file structure.

        This replaces the static hardcoded rules with dynamic logic that reads
        from the definition files (input_mapping, output_mapping, config_mapping).

        Args:
            definition: ConventionDefinition to create rules for

        Returns:
            List of MappingRule objects created from definition structure
        """
        # Check cache first
        cache_key = f"{definition.provider}_{definition.version_string}"
        if cache_key in self._rule_cache:
            return self._rule_cache[cache_key]

        rules = []

        try:
            # Get the definition data from the definition file
            definition_data = definition.definition_data
            if not definition_data:
                safe_log(
                    None, "warning", f"No definition data for {definition.provider}"
                )
                return []

            # Create input mapping rules
            input_mapping = definition_data.get("input_mapping", {})
            if input_mapping and "mappings" in input_mapping:
                for source_pattern, mapping_config in input_mapping["mappings"].items():
                    target = mapping_config.get("target", "unknown")
                    transform = mapping_config.get("transform", "direct")

                    # Create rule for input mapping
                    rule = MappingRule(
                        source_pattern=source_pattern,
                        target_field="inputs",
                        target_path=f"inputs.{target}",
                        transform=transform,
                    )
                    rules.append(rule)

                    safe_log(
                        None,
                        "debug",
                        (
                            f"Created input rule: {source_pattern} → inputs.{target} "
                            f"(transform: {transform})"
                        ),
                    )

            # Create output mapping rules
            output_mapping = definition_data.get("output_mapping", {})
            if output_mapping and "mappings" in output_mapping:
                for source_pattern, mapping_config in output_mapping[
                    "mappings"
                ].items():
                    target = mapping_config.get("target", "unknown")
                    transform = mapping_config.get("transform", "direct")

                    # Create rule for output mapping (single target per rule)
                    if isinstance(target, list):
                        # Handle legacy multiple targets by using first target
                        target = target[0] if target else "content"

                    rule = MappingRule(
                        source_pattern=source_pattern,
                        target_field="outputs",
                        target_path=f"outputs.{target}",
                        transform=transform,
                    )
                    rules.append(rule)

                    safe_log(
                        None,
                        "debug",
                        (
                            f"Created output rule: {source_pattern} → outputs.{target} "
                            f"(transform: {transform})"
                        ),
                    )

            # Create config mapping rules
            config_mapping = definition_data.get("config_mapping", {})
            if config_mapping and "mappings" in config_mapping:
                for source_pattern, mapping_config in config_mapping[
                    "mappings"
                ].items():
                    target = mapping_config.get("target", "unknown")
                    transform = mapping_config.get("transform", "direct")

                    # Create rule for config mapping
                    rule = MappingRule(
                        source_pattern=source_pattern,
                        target_field="config",
                        target_path=f"config.{target}",
                        transform=transform,
                    )
                    rules.append(rule)

                    safe_log(
                        None,
                        "debug",
                        (
                            f"Created config rule: {source_pattern} → config.{target} "
                            f"(transform: {transform})"
                        ),
                    )

            # Create metadata mapping rules (optional)
            metadata_mapping = definition_data.get("metadata_mapping", {})
            if metadata_mapping and "mappings" in metadata_mapping:
                for source_pattern, mapping_config in metadata_mapping[
                    "mappings"
                ].items():
                    target = mapping_config.get("target", "unknown")
                    transform = mapping_config.get("transform", "direct")

                    # Create rule for metadata mapping
                    rule = MappingRule(
                        source_pattern=source_pattern,
                        target_field="metadata",
                        target_path=f"metadata.{target}",
                        transform=transform,
                    )
                    rules.append(rule)

                    safe_log(
                        None,
                        "debug",
                        (
                            f"Created metadata rule: {source_pattern} → "
                            f"metadata.{target} (transform: {transform})"
                        ),
                    )

        except Exception as e:
            safe_log(
                None,
                "error",
                f"Failed to create dynamic rules for {definition.provider}: {e}",
            )
            # Fallback to empty rules rather than crashing

        # Cache the results
        self._rule_cache[cache_key] = rules

        safe_log(
            None,
            "debug",
            f"Created {len(rules)} dynamic mapping rules for {definition.provider}",
        )

        return rules

    def clear_cache(self) -> None:
        """Clear the rule cache (useful for testing or reloading definitions)."""
        self._rule_cache.clear()
        safe_log(None, "debug", "Rule engine cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        return {
            "cached_definitions": len(self._rule_cache),
            "total_cached_rules": sum(
                len(rules) for rules in self._rule_cache.values()
            ),
            "cache_keys": list(self._rule_cache.keys()),
        }

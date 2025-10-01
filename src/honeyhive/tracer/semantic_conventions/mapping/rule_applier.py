"""Rule application logic for semantic convention mapping.

This module contains the logic for applying mapping rules to transform
OpenTelemetry attributes into the HoneyHive event schema format.
"""

from typing import Any, Dict, List

from ....utils.logger import safe_log
from .patterns import pattern_matcher
from .rule_engine import MappingRule
from .transforms import TransformRegistry


class RuleApplier:
    """Applies mapping rules to transform attributes to HoneyHive schema.

    This class provides the execution logic for applying mapping rules,
    replacing the hardcoded rule application methods in the monolithic mapper.
    """

    def __init__(self) -> None:
        """Initialize the rule applier with its own transform registry instance."""
        self.transform_registry = TransformRegistry()

    def apply_rules(
        self,
        attributes: Dict[str, Any],
        rules: List[MappingRule],
        event_type: str,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """Apply a list of mapping rules to a set of attributes.

        Args:
            attributes: Source attributes dictionary
            rules: List of mapping rules to apply
            event_type: The detected event type (e.g., "model", "chain")

        Returns:
            A dictionary representing the mapped HoneyHive event schema.
        """
        result: Dict[str, Any] = {
            "inputs": {},
            "outputs": {},
            "config": {},
            "metadata": {},
        }

        for rule in rules:
            try:
                matching_attrs = pattern_matcher.find_matching_attributes(
                    attributes, rule.source_pattern
                )
                if not matching_attrs:
                    continue

                self.apply_rule(result, matching_attrs, rule)

            except Exception as e:
                safe_log(
                    None, "warning", f"Error applying rule {rule.source_pattern}: {e}"
                )

        return result

    def apply_rule(
        self, result: Dict[str, Any], matching_attrs: Dict[str, Any], rule: MappingRule
    ) -> None:
        """Apply a single mapping rule based on its target field.

        Args:
            result: The result dictionary to update
            matching_attrs: Dictionary of matching attributes
            rule: The mapping rule to apply
        """
        try:
            if rule.target_field == "inputs":
                self.apply_input_mapping(result, matching_attrs, rule)
            elif rule.target_field == "outputs":
                self.apply_output_mapping(result, matching_attrs, rule)
            elif rule.target_field == "config":
                self.apply_config_mapping(result, matching_attrs, rule)
            elif rule.target_field == "metadata":
                self.apply_metadata_mapping(result, matching_attrs, rule)
            else:
                # Fallback for unknown target fields
                self.apply_generic_mapping(result, matching_attrs, rule)

        except Exception as e:
            safe_log(None, "warning", f"Error applying rule {rule.source_pattern}: {e}")

    def apply_input_mapping(
        self, result: Dict[str, Any], matching_attrs: Dict[str, Any], rule: MappingRule
    ) -> None:
        """Apply dynamic input mapping based on rule configuration."""
        try:
            # For exact matches, get the specific attribute value
            # For wildcard matches, pass the entire matching_attrs dict
            if len(matching_attrs) == 1 and rule.source_pattern in matching_attrs:
                # Exact match - pass the actual attribute value
                attr_value = matching_attrs[rule.source_pattern]
                transformed_value = self.transform_registry.apply_transform(
                    rule.transform or "direct", attr_value, matching_attrs
                )
            else:
                # Wildcard match - pass the matching attributes dict
                transformed_value = self.transform_registry.apply_transform(
                    rule.transform or "direct", matching_attrs, matching_attrs
                )

            # Extract target name from target_path
            # (e.g., "inputs.chat_history" -> "chat_history")
            target_name = (
                rule.target_path.split(".", 1)[1]
                if "." in rule.target_path
                else rule.target_path
            )

            # Set the value in inputs
            result["inputs"][target_name] = transformed_value

            safe_log(
                None,
                "debug",
                (
                    f"Dynamic input mapping: {rule.source_pattern} -> "
                    f"inputs.{target_name} (transform: {rule.transform or 'direct'})"
                ),
            )

        except Exception as e:
            safe_log(
                None,
                "warning",
                f"Error in dynamic input mapping for {rule.source_pattern}: {e}",
            )

    def apply_output_mapping(
        self, result: Dict[str, Any], matching_attrs: Dict[str, Any], rule: MappingRule
    ) -> None:
        """Apply dynamic output mapping based on rule configuration."""
        try:
            # For exact matches, get the specific attribute value
            # For wildcard matches, pass the entire matching_attrs dict
            if len(matching_attrs) == 1 and rule.source_pattern in matching_attrs:
                # Exact match - pass the actual attribute value
                attr_value = matching_attrs[rule.source_pattern]
                transformed_value = self.transform_registry.apply_transform(
                    rule.transform or "direct", attr_value, matching_attrs
                )
            else:
                # Wildcard match - pass the matching attributes dict
                transformed_value = self.transform_registry.apply_transform(
                    rule.transform or "direct", matching_attrs, matching_attrs
                )

            # Extract target name from target_path
            # (e.g., "outputs.content" -> "content")
            target_name = (
                rule.target_path.split(".", 1)[1]
                if "." in rule.target_path
                else rule.target_path
            )

            # Set the value in outputs
            result["outputs"][target_name] = transformed_value

            safe_log(
                None,
                "debug",
                (
                    f"Dynamic output mapping: {rule.source_pattern} -> "
                    f"outputs.{target_name} (transform: {rule.transform or 'direct'})"
                ),
            )

        except Exception as e:
            safe_log(
                None,
                "warning",
                f"Error in dynamic output mapping for {rule.source_pattern}: {e}",
            )

    def apply_config_mapping(
        self, result: Dict[str, Any], matching_attrs: Dict[str, Any], rule: MappingRule
    ) -> None:
        """Apply dynamic config mapping based on rule configuration."""
        try:
            # For exact matches, get the specific attribute value
            # For wildcard matches, pass the entire matching_attrs dict
            if len(matching_attrs) == 1 and rule.source_pattern in matching_attrs:
                # Exact match - pass the actual attribute value
                attr_value = matching_attrs[rule.source_pattern]
                transformed_value = self.transform_registry.apply_transform(
                    rule.transform or "direct", attr_value, matching_attrs
                )
            else:
                # Wildcard match - pass the matching attributes dict
                transformed_value = self.transform_registry.apply_transform(
                    rule.transform or "direct", matching_attrs, matching_attrs
                )

            # Extract target name from target_path (e.g., "config.model" -> "model")
            target_name = (
                rule.target_path.split(".", 1)[1]
                if "." in rule.target_path
                else rule.target_path
            )

            # For direct transform, extract the actual value from the dictionary
            if (
                rule.transform == "direct"
                and isinstance(transformed_value, dict)
                and len(transformed_value) == 1
            ):
                transformed_value = next(iter(transformed_value.values()))

            # Set the value in config
            result["config"][target_name] = transformed_value

            safe_log(
                None,
                "debug",
                (
                    f"Dynamic config mapping: {rule.source_pattern} -> "
                    f"config.{target_name} (transform: {rule.transform or 'direct'})"
                ),
            )

        except Exception as e:
            safe_log(
                None,
                "warning",
                f"Error in dynamic config mapping for {rule.source_pattern}: {e}",
            )

    def apply_metadata_mapping(
        self, result: Dict[str, Any], matching_attrs: Dict[str, Any], rule: MappingRule
    ) -> None:
        """Apply dynamic metadata mapping based on rule configuration."""
        try:
            # For exact matches, get the specific attribute value
            # For wildcard matches, pass the entire matching_attrs dict
            if len(matching_attrs) == 1 and rule.source_pattern in matching_attrs:
                # Exact match - pass the actual attribute value
                attr_value = matching_attrs[rule.source_pattern]
                transformed_value = self.transform_registry.apply_transform(
                    rule.transform or "direct", attr_value, matching_attrs
                )
            else:
                # Wildcard match - pass the matching attributes dict
                transformed_value = self.transform_registry.apply_transform(
                    rule.transform or "direct", matching_attrs, matching_attrs
                )

            # Extract target name from target_path (e.g., "metadata.tokens" -> "tokens")
            target_name = (
                rule.target_path.split(".", 1)[1]
                if "." in rule.target_path
                else rule.target_path
            )

            # Set the value in metadata
            result["metadata"][target_name] = transformed_value

            safe_log(
                None,
                "debug",
                (
                    f"Dynamic metadata mapping: {rule.source_pattern} -> "
                    f"metadata.{target_name} (transform: {rule.transform or 'direct'})"
                ),
            )

        except Exception as e:
            safe_log(
                None,
                "warning",
                f"Error in dynamic metadata mapping for {rule.source_pattern}: {e}",
            )

    def apply_generic_mapping(
        self, result: Dict[str, Any], matching_attrs: Dict[str, Any], rule: MappingRule
    ) -> None:
        """Apply generic mapping for unknown target fields."""
        try:
            # Apply transform to get the processed value
            transformed_value = self.transform_registry.apply_transform(
                rule.transform or "direct", matching_attrs, {}
            )

            # Use the full target_path for generic mappings
            self._set_nested_value(result, rule.target_path, transformed_value)

            safe_log(
                None,
                "debug",
                (
                    f"Generic mapping: {rule.source_pattern} -> {rule.target_path} "
                    f"(transform: {rule.transform or 'direct'})"
                ),
            )

        except Exception as e:
            safe_log(
                None,
                "warning",
                f"Error in generic mapping for {rule.source_pattern}: {e}",
            )

    def _set_nested_value(self, obj: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested value in a dictionary using dot notation.

        Args:
            obj: The dictionary to modify
            path: Dot-separated path (e.g., "config.model", "metadata.usage.tokens")
            value: The value to set
        """
        parts = path.split(".")
        current = obj

        # Navigate to the parent of the final key
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the final value
        current[parts[-1]] = value

    def apply_single_rule_legacy(
        self, result: Dict[str, Any], matching_attrs: Dict[str, Any], rule: MappingRule
    ) -> None:
        """Apply a single mapping rule to the result (legacy compatibility method).

        This method provides compatibility with the old single rule application logic
        while the migration is in progress.

        Args:
            result: The result dictionary to update
            matching_attrs: Dictionary of matching attributes
            rule: The mapping rule to apply
        """
        try:
            # Apply transform
            transformed_value = self.transform_registry.apply_transform(
                rule.transform or "direct", matching_attrs, matching_attrs
            )
            if transformed_value is not None:
                self._set_nested_value(result, rule.target_path, transformed_value)

        except Exception as e:
            safe_log(
                None,
                "warning",
                f"Error applying single rule {rule.source_pattern}: {e}",
            )


# Create a global instance for easy access
rule_applier = RuleApplier()

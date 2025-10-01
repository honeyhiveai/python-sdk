"""Pattern matching utilities for semantic convention mapping.

This module provides fast, efficient pattern matching for OpenTelemetry attributes
using native Python string operations instead of regex for optimal performance.
"""

from typing import Any, Dict

from ....utils.logger import safe_log


class PatternMatcher:
    """Fast pattern matching utility for semantic convention attributes.

    This class provides efficient wildcard pattern matching using native Python
    string operations (startswith, endswith) instead of regex for better performance.
    """

    def find_matching_attributes(
        self, attributes: Dict[str, Any], pattern: str
    ) -> Dict[str, Any]:
        """Find attributes matching a pattern (supports wildcards).

        Args:
            attributes: Source attributes dictionary
            pattern: Pattern to match (supports * wildcard)

        Returns:
            Dictionary of matching attributes
        """
        if "*" not in pattern:
            # Exact match
            result = {pattern: attributes[pattern]} if pattern in attributes else {}
            safe_log(
                None,
                "debug",
                f"Exact match for '{pattern}': found {len(result)} attributes",
            )
            return result

        # Simple, fast wildcard pattern matching using string operations
        matching = {}

        if pattern.endswith("*"):
            # Pattern like "gen_ai.prompt.*" - use startswith
            prefix = pattern[:-1]  # Remove the *
            for attr_name, attr_value in attributes.items():
                if attr_name.startswith(prefix):
                    matching[attr_name] = attr_value
        elif "*" in pattern:
            # Pattern like "gen_ai.completion.*.role" - split and match parts
            parts = pattern.split("*")
            if len(parts) == 2:
                prefix, suffix = parts
                for attr_name, attr_value in attributes.items():
                    if attr_name.startswith(prefix) and attr_name.endswith(suffix):
                        matching[attr_name] = attr_value
            else:
                # Multiple wildcards - fallback to simple startswith with first part
                prefix = parts[0]
                for attr_name, attr_value in attributes.items():
                    if attr_name.startswith(prefix):
                        matching[attr_name] = attr_value
        else:
            # No wildcard - this shouldn't happen here but handle gracefully
            if pattern in attributes:
                matching[pattern] = attributes[pattern]

        safe_log(
            None,
            "debug",
            f"Smart wildcard match for '{pattern}': found {len(matching)} attributes",
        )
        return matching

    def is_pattern_match(self, attribute_name: str, pattern: str) -> bool:
        """Check if a single attribute name matches a pattern.

        Args:
            attribute_name: The attribute name to test
            pattern: The pattern to match against

        Returns:
            True if the attribute matches the pattern
        """
        if "*" not in pattern:
            return attribute_name == pattern

        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return attribute_name.startswith(prefix)
        if "*" in pattern:
            parts = pattern.split("*")
            if len(parts) == 2:
                prefix, suffix = parts
                return attribute_name.startswith(prefix) and attribute_name.endswith(
                    suffix
                )
            # Multiple wildcards - use first part
            prefix = parts[0]
            return attribute_name.startswith(prefix)

        return False

    def extract_pattern_groups(
        self, attribute_name: str, pattern: str
    ) -> Dict[str, str]:
        """Extract groups from a pattern match (useful for indexed attributes).

        Args:
            attribute_name: The matched attribute name
            pattern: The pattern that was matched

        Returns:
            Dictionary with extracted groups (e.g., {"index": "0", "field": "role"})
        """
        groups: Dict[str, str] = {}

        if "*" not in pattern:
            return groups

        if pattern.endswith("*"):
            # Pattern like "gen_ai.prompt.*"
            prefix = pattern[:-1]
            if attribute_name.startswith(prefix):
                remainder = attribute_name[len(prefix) :]
                # Try to extract index and field if it's a structured remainder
                parts = remainder.split(".")
                if len(parts) >= 2 and parts[0].isdigit():
                    groups["index"] = parts[0]
                    groups["field"] = ".".join(parts[1:])
                else:
                    groups["remainder"] = remainder

        elif "*" in pattern:
            # Pattern like "gen_ai.completion.*.role"
            parts = pattern.split("*")
            if len(parts) == 2:
                prefix, suffix = parts
                if attribute_name.startswith(prefix) and attribute_name.endswith(
                    suffix
                ):
                    # Extract the middle part
                    start_idx = len(prefix)
                    end_idx = (
                        len(attribute_name) - len(suffix)
                        if suffix
                        else len(attribute_name)
                    )
                    middle = attribute_name[start_idx:end_idx]
                    groups["middle"] = middle
                    # If middle looks like an index, extract it
                    if middle.isdigit():
                        groups["index"] = middle

        return groups

    def get_pattern_priority(self, pattern: str) -> int:
        """Get priority score for a pattern (more specific = higher priority).

        Args:
            pattern: The pattern to score

        Returns:
            Priority score (higher = more specific)
        """
        if "*" not in pattern:
            return 1000  # Exact matches have highest priority

        # Count non-wildcard parts
        parts = pattern.split("*")
        total_length = sum(len(part) for part in parts)
        wildcard_count = pattern.count("*")

        # More specific patterns (longer non-wildcard parts, fewer wildcards)
        # get higher priority
        return total_length - (wildcard_count * 10)

    def sort_patterns_by_priority(self, patterns: list) -> list:
        """Sort patterns by priority (most specific first).

        Args:
            patterns: List of pattern strings

        Returns:
            Sorted list with most specific patterns first
        """
        return sorted(patterns, key=self.get_pattern_priority, reverse=True)


# Create a global instance for easy access
pattern_matcher = PatternMatcher()

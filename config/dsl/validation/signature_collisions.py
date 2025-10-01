"""
Provider Signature Uniqueness Check - Quality Gate 13.

Detects signature collisions across providers to prevent ambiguous provider detection.
When multiple providers share the same signature, the inverted index keeps only the
highest confidence provider, which may cause detection issues.

This module can be used both as a library and as a CLI tool:
    - Library: from config.dsl.validation.signature_collisions import check_collisions
    - CLI: python -m config.dsl.validation.signature_collisions <files...>

Agent OS Compliance: Clear error reporting with resolution suggestions.
"""

import sys
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, FrozenSet


def extract_signatures(
    filepath: Path,
) -> List[Tuple[FrozenSet[str], str, float]]:
    """
    Extract signatures from a structure_patterns.yaml file.

    Args:
        filepath: Path to structure_patterns.yaml

    Returns:
        List of (signature_frozenset, pattern_name, confidence) tuples
    """
    signatures: List[Tuple[FrozenSet[str], str, float]] = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data: Dict[str, any] = yaml.safe_load(f)

        if not isinstance(data, dict) or "patterns" not in data:
            return signatures

        provider_name: str = data.get("provider", filepath.parent.name)
        patterns: Dict[str, any] = data["patterns"]

        for pattern_name, pattern_data in patterns.items():
            if "signature_fields" in pattern_data:
                signature_fields: FrozenSet[str] = frozenset(
                    pattern_data["signature_fields"]
                )
                confidence: float = pattern_data.get("confidence_weight", 0.9)
                signatures.append(
                    (signature_fields, f"{provider_name}:{pattern_name}", confidence)
                )

    except Exception as e:
        print(f"Warning: Failed to parse {filepath}: {e}", file=sys.stderr)

    return signatures


def check_collisions(
    yaml_files: List[Path],
) -> Tuple[bool, List[str]]:
    """
    Check for signature collisions across all provider files.

    Args:
        yaml_files: List of structure_patterns.yaml file paths

    Returns:
        Tuple of (has_collisions, collision_messages)
    """
    # Map: signature -> [(provider:pattern, confidence), ...]
    signature_map: Dict[FrozenSet[str], List[Tuple[str, float]]] = defaultdict(list)
    collision_messages: List[str] = []

    # Collect all signatures
    for filepath in yaml_files:
        signatures: List[Tuple[FrozenSet[str], str, float]] = extract_signatures(
            filepath
        )
        for sig_fields, pattern_name, confidence in signatures:
            signature_map[sig_fields].append((pattern_name, confidence))

    # Find collisions (signatures used by multiple providers)
    for signature, patterns in signature_map.items():
        if len(patterns) > 1:
            # Extract provider names (before the colon)
            providers: List[str] = [p.split(":")[0] for p, _ in patterns]
            unique_providers: set[str] = set(providers)

            # Only report if different providers share the signature
            if len(unique_providers) > 1:
                collision_messages.append(
                    f"\n⚠️  Signature Collision Detected:\n"
                    f"  Signature: {sorted(signature)}\n"
                    f"  Used by {len(patterns)} patterns across {len(unique_providers)} providers:"
                )

                # Sort by confidence (highest first)
                sorted_patterns: List[Tuple[str, float]] = sorted(
                    patterns, key=lambda x: x[1], reverse=True
                )

                for pattern_name, conf in sorted_patterns:
                    provider: str = pattern_name.split(":")[0]
                    collision_messages.append(
                        f"    - {pattern_name} (provider: {provider}, confidence: {conf})"
                    )

                # Determine winner (highest confidence)
                winner_pattern, winner_conf = sorted_patterns[0]
                winner_provider: str = winner_pattern.split(":")[0]

                collision_messages.append(
                    f"  Resolution: Inverted index will keep '{winner_provider}' "
                    f"(highest confidence: {winner_conf})"
                )

                # Check if confidence difference is too small
                if len(sorted_patterns) > 1:
                    second_conf: float = sorted_patterns[1][1]
                    conf_diff: float = winner_conf - second_conf

                    if conf_diff < 0.05:
                        collision_messages.append(
                            f"  ⚠️  WARNING: Confidence difference is very small ({conf_diff:.3f}). "
                            "Consider increasing the difference to >0.05 for clear disambiguation."
                        )

    return len(collision_messages) > 0, collision_messages


def check_signature_collisions(yaml_files: List[Path]) -> Tuple[bool, List[str], int]:
    """
    Check for signature collisions across provider YAML files.

    This is the main library function for signature collision detection.

    Args:
        yaml_files: List of structure_patterns.yaml file paths

    Returns:
        Tuple of (has_collisions, collision_messages, providers_checked)
    """
    # Filter to only structure_patterns.yaml files
    structure_files: List[Path] = [
        f for f in yaml_files if f.name == "structure_patterns.yaml"
    ]

    if not structure_files:
        return False, [], 0

    has_collisions, messages = check_collisions(structure_files)
    return has_collisions, messages, len(structure_files)


def main() -> int:
    """
    Main entry point for signature uniqueness check CLI.

    Returns:
        Exit code (0 for no collisions, 1 for collisions detected)
    """
    if len(sys.argv) < 2:
        print(
            "Usage: python -m config.dsl.validation.signature_collisions "
            "<structure_patterns.yaml files...>"
        )
        return 1

    yaml_files: List[Path] = [Path(f) for f in sys.argv[1:]]

    has_collisions, messages, providers_checked = check_signature_collisions(yaml_files)

    if has_collisions:
        print("❌ Signature Uniqueness Check Failed:\n")
        for message in messages:
            print(message)
        print("\n💡 Suggestions:")
        print("  1. Adjust confidence_weight values to clearly differentiate providers")
        print("  2. Add more signature_fields to make patterns more specific")
        print("  3. Review if patterns truly represent different providers")
        return 1
    else:
        print(
            f"✅ Signature Uniqueness Check Passed "
            f"({providers_checked} providers checked, no collisions)"
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())

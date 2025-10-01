"""
Provider YAML Schema Validation - Quality Gate 12.

Validates provider YAML files against the Universal LLM Discovery Engine v4.0 schema.
This ensures all provider configurations follow the correct structure before compilation.

This module can be used both as a library and as a CLI tool:
    - Library: from config.dsl.validation.yaml_schema import validate_yaml_file
    - CLI: python -m config.dsl.validation.yaml_schema <files...>

Agent OS Compliance: Systematic validation with clear error reporting.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple


def validate_structure_patterns(data: Dict[str, Any], filepath: Path) -> List[str]:
    """
    Validate structure_patterns.yaml schema.

    Args:
        data: Parsed YAML data
        filepath: Path to YAML file

    Returns:
        List of validation error messages
    """
    errors: List[str] = []

    # Check required top-level fields
    required_top_level: List[str] = ["version", "provider", "dsl_type", "patterns"]
    for field in required_top_level:
        if field not in data:
            errors.append(f"{filepath}: Missing required top-level field '{field}'")

    # Validate version format (accept 1.x, 4.x formats)
    if "version" in data:
        version: Any = data["version"]
        if not isinstance(version, str) or not (
            version.startswith("1.") or version.startswith("4.")
        ):
            errors.append(
                f"{filepath}: Invalid version '{version}', must be '1.x' or '4.x' format"
            )

    # Validate dsl_type
    if "dsl_type" in data:
        if data["dsl_type"] != "provider_structure_patterns":
            errors.append(
                f"{filepath}: Invalid dsl_type '{data['dsl_type']}', "
                "expected 'provider_structure_patterns'"
            )

    # Validate patterns section
    if "patterns" not in data:
        errors.append(f"{filepath}: Missing required 'patterns' section")
        return errors

    patterns: Any = data["patterns"]
    if not isinstance(patterns, dict):
        errors.append(f"{filepath}: 'patterns' must be a dictionary")
        return errors

    # Validate each pattern
    for pattern_name, pattern_data in patterns.items():
        if not isinstance(pattern_data, dict):
            errors.append(f"{filepath}: Pattern '{pattern_name}' must be a dictionary")
            continue

        # Required pattern fields
        if "signature_fields" not in pattern_data:
            errors.append(
                f"{filepath}: Pattern '{pattern_name}' missing "
                "required 'signature_fields'"
            )
        elif not isinstance(pattern_data["signature_fields"], list):
            errors.append(
                f"{filepath}: Pattern '{pattern_name}' signature_fields "
                "must be a list"
            )
        elif len(pattern_data["signature_fields"]) == 0:
            errors.append(
                f"{filepath}: Pattern '{pattern_name}' signature_fields "
                "cannot be empty"
            )

        # Validate confidence_weight if present
        if "confidence_weight" in pattern_data:
            conf: Any = pattern_data["confidence_weight"]
            if not isinstance(conf, (int, float)) or not (0 <= conf <= 1):
                errors.append(
                    f"{filepath}: Pattern '{pattern_name}' confidence_weight "
                    "must be a number between 0 and 1"
                )

        # Validate priority if present
        if "priority" in pattern_data:
            priority: Any = pattern_data["priority"]
            if not isinstance(priority, int) or priority < 1:
                errors.append(
                    f"{filepath}: Pattern '{pattern_name}' priority "
                    "must be a positive integer"
                )

        # Validate optional_fields if present
        if "optional_fields" in pattern_data:
            if not isinstance(pattern_data["optional_fields"], list):
                errors.append(
                    f"{filepath}: Pattern '{pattern_name}' optional_fields "
                    "must be a list"
                )

    return errors


def validate_navigation_rules(data: Dict[str, Any], filepath: Path) -> List[str]:
    """
    Validate navigation_rules.yaml schema.

    Args:
        data: Parsed YAML data
        filepath: Path to YAML file

    Returns:
        List of validation error messages
    """
    errors: List[str] = []

    # Check required top-level fields
    required_fields: List[str] = ["version", "provider", "dsl_type", "navigation_rules"]
    for field in required_fields:
        if field not in data:
            errors.append(f"{filepath}: Missing required field '{field}'")

    # Validate dsl_type
    if "dsl_type" in data:
        if data["dsl_type"] != "provider_navigation_rules":
            errors.append(
                f"{filepath}: Invalid dsl_type '{data['dsl_type']}', "
                "expected 'provider_navigation_rules'"
            )

    # Validate navigation_rules structure
    if "navigation_rules" in data:
        rules: Any = data["navigation_rules"]
        if not isinstance(rules, dict):
            errors.append(f"{filepath}: 'navigation_rules' must be a dictionary")

    return errors


def validate_field_mappings(data: Dict[str, Any], filepath: Path) -> List[str]:
    """
    Validate field_mappings.yaml schema.

    Args:
        data: Parsed YAML data
        filepath: Path to YAML file

    Returns:
        List of validation error messages
    """
    errors: List[str] = []

    # Check required top-level fields
    required_fields: List[str] = ["version", "provider", "dsl_type", "field_mappings"]
    for field in required_fields:
        if field not in data:
            errors.append(f"{filepath}: Missing required field '{field}'")

    # Validate dsl_type
    if "dsl_type" in data:
        if data["dsl_type"] != "provider_field_mappings":
            errors.append(
                f"{filepath}: Invalid dsl_type '{data['dsl_type']}', "
                "expected 'provider_field_mappings'"
            )

    # Validate field_mappings structure
    if "field_mappings" in data:
        mappings: Any = data["field_mappings"]
        if not isinstance(mappings, dict):
            errors.append(f"{filepath}: 'field_mappings' must be a dictionary")
        else:
            # Check for required HoneyHive schema sections
            required_sections: List[str] = ["inputs", "outputs", "config", "metadata"]
            for section in required_sections:
                if section not in mappings:
                    errors.append(
                        f"{filepath}: Missing required HoneyHive schema "
                        f"section '{section}'"
                    )

    return errors


def validate_transforms(data: Dict[str, Any], filepath: Path) -> List[str]:
    """
    Validate transforms.yaml schema.

    Args:
        data: Parsed YAML data
        filepath: Path to YAML file

    Returns:
        List of validation error messages
    """
    errors: List[str] = []

    # Check required top-level fields
    required_fields: List[str] = ["version", "provider", "dsl_type", "transforms"]
    for field in required_fields:
        if field not in data:
            errors.append(f"{filepath}: Missing required field '{field}'")

    # Validate dsl_type
    if "dsl_type" in data:
        if data["dsl_type"] != "provider_transforms":
            errors.append(
                f"{filepath}: Invalid dsl_type '{data['dsl_type']}', "
                "expected 'provider_transforms'"
            )

    # Validate transforms structure
    if "transforms" in data:
        transforms: Any = data["transforms"]
        if not isinstance(transforms, dict):
            errors.append(f"{filepath}: 'transforms' must be a dictionary")

    return errors


def validate_yaml_file(filepath: Path) -> Tuple[bool, List[str]]:
    """
    Validate a single provider YAML file.

    Args:
        filepath: Path to YAML file

    Returns:
        Tuple of (is_valid, errors)
    """
    errors: List[str] = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data: Any = yaml.safe_load(f)

        if not isinstance(data, dict):
            errors.append(f"{filepath}: YAML root must be a dictionary")
            return False, errors

        # Determine file type and validate accordingly
        filename: str = filepath.name

        if filename == "structure_patterns.yaml":
            errors.extend(validate_structure_patterns(data, filepath))
        elif filename == "navigation_rules.yaml":
            errors.extend(validate_navigation_rules(data, filepath))
        elif filename == "field_mappings.yaml":
            errors.extend(validate_field_mappings(data, filepath))
        elif filename == "transforms.yaml":
            errors.extend(validate_transforms(data, filepath))
        else:
            # Unknown file type, skip validation
            return True, []

    except yaml.YAMLError as e:
        errors.append(f"{filepath}: YAML parsing error: {e}")
    except FileNotFoundError:
        errors.append(f"{filepath}: File not found")
    except Exception as e:
        errors.append(f"{filepath}: Unexpected error: {e}")

    return len(errors) == 0, errors


def validate_yaml_schema(yaml_files: List[Path]) -> Tuple[bool, List[str], int]:
    """
    Validate multiple provider YAML files.

    This is the main library function for YAML schema validation.

    Args:
        yaml_files: List of paths to YAML files to validate

    Returns:
        Tuple of (all_valid, all_errors, files_checked)
    """
    all_errors: List[str] = []
    files_checked: int = 0

    for filepath in yaml_files:
        if not filepath.exists():
            all_errors.append(f"{filepath}: File does not exist")
            continue

        files_checked += 1
        is_valid, errors = validate_yaml_file(filepath)

        if not is_valid:
            all_errors.extend(errors)

    return len(all_errors) == 0, all_errors, files_checked


def main() -> int:
    """
    Main entry point for provider YAML schema validation CLI.

    Returns:
        Exit code (0 for success, 1 for validation failures)
    """
    if len(sys.argv) < 2:
        print("Usage: python -m config.dsl.validation.yaml_schema <yaml_files...>")
        return 1

    yaml_files: List[Path] = [Path(f) for f in sys.argv[1:]]

    all_valid, all_errors, files_checked = validate_yaml_schema(yaml_files)

    if not all_valid:
        print("❌ Provider YAML Schema Validation Failed:\n")
        for error in all_errors:
            print(f"  {error}")
        return 1
    else:
        print(
            f"✅ Provider YAML Schema Validation Passed "
            f"({files_checked} files checked)"
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())

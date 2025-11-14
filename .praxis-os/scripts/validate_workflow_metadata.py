#!/usr/bin/env python3
"""
Validate workflow metadata.json against official standards.

Standards: universal/standards/workflows/workflow-metadata-standards.md

Usage:
    python scripts/validate_workflow_metadata.py <workflow_path>
    python scripts/validate_workflow_metadata.py universal/workflows/test_generation_v3

Exit codes:
    0 - Valid metadata
    1 - Validation errors found
    2 - File not found or invalid JSON
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Required fields from workflow-metadata-standards.md
REQUIRED_ROOT_FIELDS = [
    "workflow_type",
    "version",
    "description",
    "total_phases",
    "estimated_duration",
    "primary_outputs",
    "phases",
]

REQUIRED_PHASE_FIELDS = [
    "phase_number",
    "phase_name",
    "purpose",
    "estimated_effort",
    "key_deliverables",
    "validation_criteria",
]

# Optional but recommended fields
RECOMMENDED_ROOT_FIELDS = ["name", "author"]


def validate_workflow_metadata(
    workflow_path: Path,
) -> Tuple[bool, List[str], List[str]]:
    """
    Validate workflow metadata against standard.

    Args:
        workflow_path: Path to workflow directory

    Returns:
        (is_valid, list_of_errors, list_of_warnings)
    """
    metadata_file = workflow_path / "metadata.json"

    if not metadata_file.exists():
        return False, [f"metadata.json not found in {workflow_path}"], []

    try:
        with open(metadata_file, encoding="utf-8") as f:
            metadata = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"], []

    errors = []
    warnings = []

    # Check required root fields
    for field in REQUIRED_ROOT_FIELDS:
        if field not in metadata:
            errors.append(f"Missing required root field: {field}")

    # Check recommended fields
    for field in RECOMMENDED_ROOT_FIELDS:
        if field not in metadata:
            warnings.append(f"Missing recommended field: {field}")

    # If no phases, can't continue
    if "phases" not in metadata:
        return False, errors, warnings

    phases = metadata.get("phases", [])
    total_phases = metadata.get("total_phases")

    # Handle dynamic workflows
    is_dynamic = metadata.get("dynamic_phases", False)
    if is_dynamic and total_phases == "dynamic":
        # Dynamic workflows: validate only static phases (phase 0 typically)
        # Skip phase count validation
        warnings.append("Dynamic workflow detected - only validating static phases")
    else:
        # Static workflows: validate phase count consistency
        if total_phases != len(phases):
            errors.append(
                f"total_phases ({total_phases}) != phases.length ({len(phases)})"
            )

    # Check phase numbering
    for i, phase in enumerate(phases):
        expected_num = i
        actual_num = phase.get("phase_number")

        # Allow "1-N" for dynamic phase placeholders
        if isinstance(actual_num, str) and "-" in str(actual_num):
            if not is_dynamic:
                errors.append(
                    f"Phase {i}: dynamic phase_number '{actual_num}' "
                    "but dynamic_phases is false"
                )
            continue

        if actual_num != expected_num:
            errors.append(
                f"Phase {i}: phase_number should be {expected_num}, got {actual_num}"
            )

    # Check required phase fields
    for i, phase in enumerate(phases):
        phase_num = phase.get("phase_number", i)
        for field in REQUIRED_PHASE_FIELDS:
            if field not in phase:
                errors.append(f"Phase {phase_num} missing required field: {field}")

    # Quality checks
    if "description" in metadata:
        desc = metadata["description"]
        if len(desc) < 20:
            warnings.append(
                "description is too short (should be detailed and searchable)"
            )
        if not any(char.isspace() for char in desc):
            warnings.append(
                "description should contain multiple words for searchability"
            )

    if "estimated_duration" in metadata:
        duration = metadata["estimated_duration"]
        if not any(
            unit in str(duration).lower() for unit in ["minute", "hour", "day", "week"]
        ):
            errors.append(f"estimated_duration should include units: '{duration}'")

    if "primary_outputs" in metadata:
        outputs = metadata["primary_outputs"]
        if not isinstance(outputs, list):
            errors.append("primary_outputs must be an array")
        elif len(outputs) == 0:
            errors.append("primary_outputs should contain at least one deliverable")

    # Check phases have concrete deliverables and criteria
    for i, phase in enumerate(phases):
        phase_num = phase.get("phase_number", i)

        if "key_deliverables" in phase:
            deliverables = phase["key_deliverables"]
            if not isinstance(deliverables, list) or len(deliverables) == 0:
                errors.append(
                    f"Phase {phase_num}: key_deliverables must be non-empty array"
                )

        if "validation_criteria" in phase:
            criteria = phase["validation_criteria"]
            if not isinstance(criteria, list) or len(criteria) == 0:
                errors.append(
                    f"Phase {phase_num}: validation_criteria must be non-empty array"
                )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def print_results(
    workflow_name: str, is_valid: bool, errors: List[str], warnings: List[str]
) -> None:
    """Print validation results in a human-readable format."""
    print("=" * 80)
    print(f"WORKFLOW METADATA VALIDATION: {workflow_name}")
    print("=" * 80)
    print()

    if is_valid:
        print("✅ VALID - All required fields present and properly structured")
    else:
        print("❌ INVALID - Validation errors found")

    if errors:
        print()
        print(f"ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  ❌ {error}")

    if warnings:
        print()
        print(f"WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  ⚠️  {warning}")

    print()
    print("=" * 80)
    print()

    if not is_valid:
        print("RECOMMENDATION:")
        print("  Review workflow-metadata-standards.md for required fields")
        print("  Update metadata.json to include all required fields")
        print("  Run validation again after fixes")
    else:
        print("COMPLIANCE:")
        print("  ✅ Metadata follows workflow-metadata-standards.md")
        print("  ✅ Ready for workflow engine consumption")
        print("  ✅ Optimized for RAG semantic search")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_workflow_metadata.py <workflow_path>")
        print(
            "Example: python scripts/validate_workflow_metadata.py universal/workflows/test_generation_v3"
        )
        sys.exit(2)

    workflow_path = Path(sys.argv[1])

    if not workflow_path.exists():
        print(f"❌ Error: Workflow path does not exist: {workflow_path}")
        sys.exit(2)

    if not workflow_path.is_dir():
        print(f"❌ Error: Path is not a directory: {workflow_path}")
        sys.exit(2)

    is_valid, errors, warnings = validate_workflow_metadata(workflow_path)
    print_results(workflow_path.name, is_valid, errors, warnings)

    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()

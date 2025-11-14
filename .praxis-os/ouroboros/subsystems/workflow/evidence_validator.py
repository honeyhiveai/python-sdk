"""
Evidence Validator: Multi-layer validation (field → type → custom → cross-field → artifact).

Implements adversarial validation to catch AI agent shortcuts:
Layer 1: Field presence (required fields exist)
Layer 2: Type validation (field types correct)
Layer 3: Custom validators (field-level constraints)
Layer 4: Cross-field rules (inter-field logic)
Layer 5: Artifact validation (files exist and valid)

Architecture:
- Pure validation logic (stateless)
- Clear error messages with field paths
- Explicit pass/fail (no silent failures)
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ouroboros.subsystems.workflow.hidden_schemas import EvidenceSchema, FieldSchema
from ouroboros.utils.errors import EvidenceValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Validation result with pass/fail and errors/warnings.

    Attributes:
        passed: Whether validation passed overall
        errors: List of error messages (block phase completion)
        warnings: List of warning messages (non-blocking)
        field_errors: Errors by field name
    """

    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_errors: Dict[str, List[str]] = field(default_factory=dict)

    def add_error(self, error: str, field_name: Optional[str] = None) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.passed = False
        if field_name:
            if field_name not in self.field_errors:
                self.field_errors[field_name] = []
            self.field_errors[field_name].append(error)

    def add_warning(self, warning: str) -> None:
        """Add validation warning (non-blocking)."""
        self.warnings.append(warning)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "field_errors": self.field_errors,
        }


class EvidenceValidator:
    """
    Multi-layer evidence validator.

    Validates evidence against hidden schemas with 5-layer validation:
    1. Field presence
    2. Type validation
    3. Custom validators
    4. Cross-field rules
    5. Artifact validation
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize evidence validator.

        Args:
            workspace_root: Workspace root for artifact path resolution
        """
        self.workspace_root = workspace_root or Path.cwd()
        logger.info("EvidenceValidator initialized", extra={"workspace_root": str(self.workspace_root)})

    def validate(self, evidence: Dict[str, Any], schema: EvidenceSchema) -> ValidationResult:
        """
        Validate evidence against schema.

        Executes all 5 validation layers in sequence.

        Args:
            evidence: Evidence dictionary to validate
            schema: Evidence schema from HiddenSchemas

        Returns:
            ValidationResult with pass/fail and errors
        """
        result = ValidationResult(passed=True)

        # Layer 1: Field presence
        self._validate_field_presence(evidence, schema, result)

        # Layer 2: Type validation
        self._validate_types(evidence, schema, result)

        # Layer 3: Custom validators
        self._validate_custom(evidence, schema, result)

        # Layer 4: Cross-field rules
        self._validate_cross_field(evidence, schema, result)

        # Layer 5: Artifact validation
        self._validate_artifacts(evidence, schema, result)

        logger.info(
            "Evidence validation complete",
            extra={
                "passed": result.passed,
                "error_count": len(result.errors),
                "warning_count": len(result.warnings),
            },
        )

        return result

    def _validate_field_presence(self, evidence: Dict[str, Any], schema: EvidenceSchema, result: ValidationResult) -> None:
        """
        Layer 1: Validate required fields are present.

        Args:
            evidence: Evidence to validate
            schema: Evidence schema
            result: ValidationResult to populate
        """
        required_fields = schema.get_required_fields()

        for field_name in required_fields:
            if field_name not in evidence:
                result.add_error(
                    f"Field '{field_name}' is required but missing. Provide this field to complete phase.",
                    field_name=field_name,
                )

    def _validate_types(self, evidence: Dict[str, Any], schema: EvidenceSchema, result: ValidationResult) -> None:
        """
        Layer 2: Validate field types.

        Args:
            evidence: Evidence to validate
            schema: Evidence schema
            result: ValidationResult to populate
        """
        type_map = {
            "boolean": bool,
            "integer": int,
            "string": str,
            "object": dict,
            "list": list,
        }

        for field_name, field_schema in schema.evidence_fields.items():
            if field_name not in evidence:
                continue  # Missing fields handled in Layer 1

            value = evidence[field_name]
            expected_type = type_map.get(field_schema.type)

            if expected_type is None:
                result.add_warning(f"Unknown type '{field_schema.type}' for field '{field_name}'")
                continue

            if not isinstance(value, expected_type):
                result.add_error(
                    f"Field '{field_name}' must be {field_schema.type}, got: {type(value).__name__}. "
                    f"Correct the type to proceed.",
                    field_name=field_name,
                )

    def _validate_custom(self, evidence: Dict[str, Any], schema: EvidenceSchema, result: ValidationResult) -> None:
        """
        Layer 3: Validate custom field-level constraints.

        Args:
            evidence: Evidence to validate
            schema: Evidence schema
            result: ValidationResult to populate
        """
        for field_name, field_schema in schema.evidence_fields.items():
            if field_name not in evidence:
                continue

            if field_schema.validator is None:
                continue

            # Get validator lambda
            validator_code = schema.validators.get(field_schema.validator)
            if validator_code is None:
                result.add_warning(f"Validator '{field_schema.validator}' not found for field '{field_name}'")
                continue

            # Execute validator
            try:
                # pylint: disable=eval-used
                # Justification: Controlled eval for validator lambdas with empty builtins
                validator_func = eval(validator_code, {"__builtins__": {}}, {})  # noqa: S307
                value = evidence[field_name]
                params = field_schema.validator_params or {}

                # Call validator (may take params)
                if params:
                    is_valid = validator_func(value, **params)
                else:
                    is_valid = validator_func(value)

                if not is_valid:
                    result.add_error(
                        f"Field '{field_name}' failed validation: {field_schema.validator}. "
                        f"Check constraints and correct the value.",
                        field_name=field_name,
                    )
            except Exception as e:
                result.add_error(
                    f"Validator execution failed for field '{field_name}': {e}. "
                    f"Contact maintainer if this persists.",
                    field_name=field_name,
                )

    def _validate_cross_field(self, evidence: Dict[str, Any], schema: EvidenceSchema, result: ValidationResult) -> None:
        """
        Layer 4: Validate cross-field rules.

        Args:
            evidence: Evidence to validate
            schema: Evidence schema
            result: ValidationResult to populate
        """
        for rule in schema.cross_field_rules:
            try:
                if not rule.evaluate(evidence):
                    result.add_error(f"Cross-field validation failed: {rule.error_message}")
            except Exception as e:
                result.add_error(f"Cross-field rule evaluation error: {e}")

    def _validate_artifacts(self, evidence: Dict[str, Any], schema: EvidenceSchema, result: ValidationResult) -> None:
        """
        Layer 5: Validate artifact files exist and are valid.

        Checks for fields ending in '_path' or '_file' and validates they exist.

        Args:
            evidence: Evidence to validate
            schema: Evidence schema
            result: ValidationResult to populate
        """
        # Identify artifact fields (end with _path, _file, or type is "artifact")
        artifact_fields = []
        for field_name, field_schema in schema.evidence_fields.items():
            if field_name.endswith("_path") or field_name.endswith("_file") or field_schema.type == "artifact":
                artifact_fields.append(field_name)

        for field_name in artifact_fields:
            if field_name not in evidence:
                continue

            artifact_path_str = evidence[field_name]
            if not isinstance(artifact_path_str, str):
                result.add_error(
                    f"Artifact field '{field_name}' must be a string path, got: {type(artifact_path_str).__name__}",
                    field_name=field_name,
                )
                continue

            # Resolve path relative to workspace
            artifact_path = self.workspace_root / artifact_path_str

            if not artifact_path.exists():
                result.add_error(
                    f"Artifact file '{artifact_path_str}' not found. "
                    f"Expected at: {artifact_path}. "
                    f"Create the file or correct the path.",
                    field_name=field_name,
                )


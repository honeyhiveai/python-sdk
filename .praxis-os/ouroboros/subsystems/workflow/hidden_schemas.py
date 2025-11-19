"""
Hidden Schemas: Evidence schema loader (never exposed to AI).

Implements information asymmetry - schemas are loaded from workflow
gate-definition.yaml files but NEVER exposed via MCP tool schemas.

Architecture:
- Pure loader (no validation logic)
- Thread-safe caching
- Graceful fallback to permissive gate
"""

import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class SchemaLoaderError(ActionableError):
    """Schema loading failed."""

    pass


@dataclass
class FieldSchema:
    """
    Schema definition for single evidence field.

    Attributes:
        name: Field name
        type: Field type (boolean, integer, string, object, list)
        required: Whether field is required
        validator: Optional validator name
        validator_params: Optional parameters for validator
        description: Human-readable description
    """

    name: str
    type: str
    required: bool
    validator: Optional[str]
    validator_params: Optional[Dict[str, Any]]
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "validator": self.validator,
            "validator_params": self.validator_params,
            "description": self.description,
        }


@dataclass
class CrossFieldRule:
    """
    Cross-field validation rule.

    Validates relationships between multiple evidence fields using lambda expressions.

    Attributes:
        rule: Lambda expression taking evidence dict (e.g., "lambda e: e['a'] > e['b']")
        error_message: Error message shown if rule fails
    """

    rule: str
    error_message: str

    def evaluate(self, evidence: Dict[str, Any]) -> bool:
        """
        Evaluate rule against evidence.

        Args:
            evidence: Evidence dictionary to validate

        Returns:
            True if rule passes, False otherwise

        Raises:
            ValueError: If rule syntax invalid or evaluation fails
        """
        try:
            # pylint: disable=eval-used
            # Justification: Controlled eval for lambda expressions with empty builtins
            rule_func = eval(self.rule, {"__builtins__": {}}, {})  # noqa: S307
            return bool(rule_func(evidence))
        except Exception as e:
            raise ValueError(f"Cross-field rule evaluation failed: {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {"rule": self.rule, "error_message": self.error_message}


@dataclass
class EvidenceSchema:
    """
    Complete evidence schema for a workflow phase.

    Attributes:
        evidence_fields: Field schemas by field name
        validators: Validator lambda expressions by name
        cross_field_rules: Cross-field validation rules
        strict: Whether strict mode enabled (errors block vs warnings)
        allow_override: Whether manual override allowed
        source: How schema was loaded (yaml, permissive)
    """

    evidence_fields: Dict[str, FieldSchema]
    validators: Dict[str, str]
    cross_field_rules: List[CrossFieldRule]
    strict: bool
    allow_override: bool
    source: str

    def get_required_fields(self) -> List[str]:
        """Get list of required field names."""
        return [name for name, schema in self.evidence_fields.items() if schema.required]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "evidence_fields": {k: v.to_dict() for k, v in self.evidence_fields.items()},
            "validators": self.validators,
            "cross_field_rules": [r.to_dict() for r in self.cross_field_rules],
            "strict": self.strict,
            "allow_override": self.allow_override,
            "source": self.source,
        }


class HiddenSchemas:
    """
    Loads evidence schemas from workflow gate-definition.yaml files.

    Implements information asymmetry:
    - Schemas are NEVER exposed to AI via MCP tool schemas
    - Validation errors only appear AFTER submission
    - Philosophy: Prevents Goodhart's Law (optimizing for validation over work)

    Thread-safe with caching for performance.
    """

    def __init__(self, workflows_dir: Path):
        """
        Initialize schema loader.

        Args:
            workflows_dir: Base directory for workflow definitions
                (e.g., .praxis-os/workflows/)
        """
        self.workflows_dir = workflows_dir
        self._cache: Dict[str, EvidenceSchema] = {}
        self._cache_lock = threading.RLock()

        logger.info("HiddenSchemas initialized", extra={"workflows_dir": str(workflows_dir)})

    def get_schema(self, workflow_type: str, phase: int) -> EvidenceSchema:
        """
        Get evidence schema for workflow/phase.

        Thread-safe with caching (double-checked locking pattern).

        Args:
            workflow_type: Workflow type identifier
            phase: Phase number

        Returns:
            EvidenceSchema (from YAML or permissive fallback)
        """
        cache_key = f"{workflow_type}:{phase}"

        # Fast path: Check cache without lock
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Slow path: Load with lock
        with self._cache_lock:
            # Re-check inside lock (another thread may have loaded)
            if cache_key in self._cache:
                return self._cache[cache_key]

            # Load schema
            schema = self._load_with_fallback(workflow_type, phase)

            # Cache and return
            self._cache[cache_key] = schema
            return schema

    def is_schema_exposed(self) -> bool:
        """
        Check if schemas are exposed to AI.

        Always returns False - this is intentional (information asymmetry).

        Returns:
            False (schemas are NEVER exposed)
        """
        return False

    def _load_with_fallback(self, workflow_type: str, phase: int) -> EvidenceSchema:
        """
        Load schema with fallback to permissive gate.

        Args:
            workflow_type: Workflow type identifier
            phase: Phase number

        Returns:
            EvidenceSchema from YAML or permissive fallback
        """
        # Try loading from YAML
        schema = self._load_from_yaml(workflow_type, phase)
        if schema:
            logger.info("Loaded evidence schema from YAML", extra={"workflow_type": workflow_type, "phase": phase})
            return schema

        # Fallback to permissive gate
        logger.info(
            "Using permissive gate (no gate-definition.yaml)",
            extra={"workflow_type": workflow_type, "phase": phase},
        )
        return self._get_permissive_schema()

    def _load_from_yaml(self, workflow_type: str, phase: int) -> Optional[EvidenceSchema]:
        """
        Load schema from gate-definition.yaml file.

        Path: .praxis-os/workflows/{workflow_type}/phases/{phase}/gate-definition.yaml

        Args:
            workflow_type: Workflow type identifier
            phase: Phase number

        Returns:
            EvidenceSchema if file exists and valid, None otherwise
        """
        gate_path = self.workflows_dir / workflow_type / "phases" / str(phase) / "gate-definition.yaml"

        if not gate_path.exists():
            logger.debug("Gate definition not found", extra={"gate_path": str(gate_path)})
            return None

        try:
            content = yaml.safe_load(gate_path.read_text(encoding="utf-8"))
            return self._parse_gate_content(content, "yaml")
        except yaml.YAMLError as e:
            logger.error("Failed to parse YAML gate", extra={"gate_path": str(gate_path), "error": str(e)})
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Justification: Graceful fallback to permissive gate
            logger.error("Failed to load YAML gate", extra={"gate_path": str(gate_path), "error": str(e)})
            return None

    def _parse_gate_content(self, content: Dict[str, Any], source: str) -> EvidenceSchema:
        """
        Parse gate content into EvidenceSchema.

        Args:
            content: Parsed YAML content
            source: Source indicator (yaml, permissive)

        Returns:
            EvidenceSchema object

        Raises:
            SchemaLoaderError: If content structure invalid
        """
        # Validate required sections
        if "checkpoint" not in content:
            raise SchemaLoaderError(
                what_failed="Schema parsing",
                why_failed="Missing 'checkpoint' section in gate-definition.yaml",
                how_to_fix="Add 'checkpoint' section with 'enabled', 'strict', 'allow_override'",
            )
        if "evidence_schema" not in content:
            raise SchemaLoaderError(
                what_failed="Schema parsing",
                why_failed="Missing 'evidence_schema' section in gate-definition.yaml",
                how_to_fix="Add 'evidence_schema' section with field definitions",
            )

        # Parse checkpoint config
        checkpoint_config = content["checkpoint"]

        # Check if gate is enabled
        if "enabled" not in checkpoint_config:
            raise SchemaLoaderError(
                what_failed="Schema parsing",
                why_failed="Missing 'checkpoint.enabled' field",
                how_to_fix="Add 'checkpoint.enabled: true' or 'enabled: false'",
            )

        enabled = checkpoint_config["enabled"]
        if not isinstance(enabled, bool):
            raise SchemaLoaderError(
                what_failed="Schema parsing",
                why_failed=f"'checkpoint.enabled' must be boolean, got: {type(enabled).__name__}",
                how_to_fix="Set 'checkpoint.enabled' to true or false",
            )

        # If gate is disabled, return permissive schema
        if not enabled:
            logger.info("Evidence gate explicitly disabled (enabled: false), using permissive schema")
            return self._get_permissive_schema()

        strict = checkpoint_config.get("strict", False)
        allow_override = checkpoint_config.get("allow_override", True)

        # Parse evidence schema
        evidence_fields = {}
        for field_name, field_config in content["evidence_schema"].items():
            evidence_fields[field_name] = FieldSchema(
                name=field_name,
                type=field_config.get("type", "string"),
                required=field_config.get("required", False),
                validator=field_config.get("validator"),
                validator_params=field_config.get("validator_params"),
                description=field_config.get("description", ""),
            )

        # Parse validators
        validators = content.get("validators", {})

        # Parse cross-field rules
        cross_field_rules = []
        for rule_config in content.get("cross_field_validation", []):
            cross_field_rules.append(CrossFieldRule(rule=rule_config["rule"], error_message=rule_config["error_message"]))

        return EvidenceSchema(
            evidence_fields=evidence_fields,
            validators=validators,
            cross_field_rules=cross_field_rules,
            strict=strict,
            allow_override=allow_override,
            source=source,
        )

    def _get_permissive_schema(self) -> EvidenceSchema:
        """
        Return permissive schema for backwards compatibility.

        Used when gate-definition.yaml is missing. Accepts any evidence without validation.

        Returns:
            EvidenceSchema in permissive mode
        """
        return EvidenceSchema(
            evidence_fields={}, validators={}, cross_field_rules=[], strict=False, allow_override=True, source="permissive"
        )


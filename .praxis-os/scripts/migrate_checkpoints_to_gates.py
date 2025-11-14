#!/usr/bin/env python3
"""
Migration script to generate gate-definition.yaml files from existing workflows.

Scans workflow directories, parses checkpoint requirements from phase.md files,
and generates gate-definition.yaml files for validation.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.config.checkpoint_loader import (
    CheckpointRequirements,
    FieldSchema,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MigrationScript:
    """
    Migration script to generate validation gates for existing workflows.

    Workflow:
    1. Scan workflows directory
    2. For each workflow, scan phases
    3. Parse checkpoint requirements from phase.md
    4. Generate gate-definition.yaml files
    5. Validate generated gates

    Attributes:
        workflows_path: Path to workflows directory
        dry_run: Whether to run in dry-run mode (no file writes)
        force: Whether to overwrite existing gates

    Example:
        >>> script = MigrationScript(Path(".praxis-os/workflows"))
        >>> results = script.run()
        >>> print(f"Generated {results['gates_created']} gates")
    """

    def __init__(
        self, workflows_path: Path, dry_run: bool = False, force: bool = False
    ):
        """
        Initialize migration script.

        Args:
            workflows_path: Path to workflows directory
            dry_run: If True, don't write files (default: False)
            force: If True, overwrite existing gates (default: False)
        """
        self.workflows_path = workflows_path
        self.dry_run = dry_run
        self.force = force

        # Statistics tracking
        self.stats = {
            "workflows_scanned": 0,
            "phases_scanned": 0,
            "gates_created": 0,
            "gates_skipped": 0,
            "errors": 0,
        }

    def run(self) -> Dict[str, int]:
        """
        Run migration script on all workflows.

        Returns:
            Dictionary with migration statistics

        Example:
            >>> script = MigrationScript(Path(".praxis-os/workflows"))
            >>> results = script.run()
            >>> assert results['gates_created'] >= 0
        """
        logger.info(
            "Starting migration (dry_run=%s, force=%s)", self.dry_run, self.force
        )

        # Scan workflows directory
        workflows = self.scan_workflows()
        logger.info("Found %d workflows", len(workflows))

        # Process each workflow
        for workflow_name in workflows:
            try:
                self.process_workflow(workflow_name)
            except Exception as e:
                logger.error("Failed to process workflow %s: %s", workflow_name, e)
                self.stats["errors"] += 1

        # Log final statistics
        self.log_statistics()

        return self.stats

    def scan_workflows(self) -> List[str]:
        """
        Scan workflows directory and return list of workflow names.

        Returns:
            List of workflow directory names

        Example:
            >>> script = MigrationScript(Path(".praxis-os/workflows"))
            >>> workflows = script.scan_workflows()
            >>> assert "test_generation_v3" in workflows
        """
        if not self.workflows_path.exists():
            logger.error("Workflows path does not exist: %s", self.workflows_path)
            return []

        workflows = []
        for item in self.workflows_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                workflows.append(item.name)

        return sorted(workflows)

    def process_workflow(self, workflow_name: str) -> None:
        """
        Process a single workflow and generate gates for all phases.

        Args:
            workflow_name: Name of workflow directory

        Example:
            >>> script = MigrationScript(Path(".praxis-os/workflows"))
            >>> script.process_workflow("test_generation_v3")
        """
        logger.info("Processing workflow: %s", workflow_name)
        self.stats["workflows_scanned"] += 1

        workflow_path = self.workflows_path / workflow_name
        phases_path = workflow_path / "phases"

        if not phases_path.exists():
            logger.warning("No phases directory for %s", workflow_name)
            return

        # Process each phase
        for phase_dir in sorted(phases_path.iterdir()):
            if phase_dir.is_dir() and phase_dir.name.isdigit():
                phase_num = int(phase_dir.name)
                self.process_phase(workflow_name, phase_num, phase_dir)

    def process_phase(
        self, workflow_name: str, phase_num: int, phase_path: Path
    ) -> None:
        """
        Process a single phase and generate gate if needed.

        Args:
            workflow_name: Workflow name
            phase_num: Phase number
            phase_path: Path to phase directory

        Example:
            >>> script = MigrationScript(Path(".praxis-os/workflows"))
            >>> phase_path = Path(".praxis-os/workflows/test_generation_v3/phases/1")
            >>> script.process_phase("test_generation_v3", 1, phase_path)
        """
        logger.info("Processing phase: %s phase %d", workflow_name, phase_num)
        self.stats["phases_scanned"] += 1

        gate_path = phase_path / "gate-definition.yaml"

        # Check if gate already exists
        if gate_path.exists() and not self.force:
            logger.info("Gate exists, skipping: %s", gate_path)
            self.stats["gates_skipped"] += 1
            return

        # Parse checkpoint from phase.md
        # TODO: Implement in Task 2.3
        requirements = self.parse_checkpoint(phase_path)

        if not requirements:
            logger.warning("No checkpoint requirements found for phase %d", phase_num)
            return

        # Generate gate
        # TODO: Implement in Task 2.4
        gate_content = self.generate_gate(requirements)

        # Write gate file (unless dry-run)
        if self.dry_run:
            logger.info("[DRY RUN] Would create: %s", gate_path)
        else:
            self.write_gate(gate_path, gate_content)
            logger.info("Created gate: %s", gate_path)

        self.stats["gates_created"] += 1

    def parse_checkpoint(self, phase_path: Path) -> Optional[CheckpointRequirements]:
        """
        Parse checkpoint requirements from phase.md file.

        Looks for checkpoint/validation sections in markdown and extracts
        evidence field requirements with types inferred from descriptions.

        Args:
            phase_path: Path to phase directory

        Returns:
            CheckpointRequirements if found, None otherwise

        Example:
            >>> script = MigrationScript(Path(".praxis-os/workflows"))
            >>> phase_path = Path(".praxis-os/workflows/test/phases/1")
            >>> requirements = script.parse_checkpoint(phase_path)
            >>> assert requirements is not None
        """
        phase_md = phase_path / "phase.md"

        if not phase_md.exists():
            logger.debug("No phase.md found in %s", phase_path)
            return None

        try:
            content = phase_md.read_text(encoding="utf-8")

            # Extract checkpoint section
            checkpoint_section = self._extract_checkpoint_section(content)
            if not checkpoint_section:
                logger.debug("No checkpoint section found in %s", phase_md)
                return None

            # Parse evidence fields from checkpoint section
            evidence_schema = self._parse_evidence_fields(checkpoint_section)

            if not evidence_schema:
                logger.debug("No evidence fields found in checkpoint section")
                return None

            # Build requirements with lenient defaults
            requirements = CheckpointRequirements(
                evidence_schema=evidence_schema,
                validators={},
                cross_field_rules=[],
                strict=False,  # Lenient by default
                allow_override=True,
                source="parsed",
            )

            logger.info(
                "Parsed %d evidence fields from %s", len(evidence_schema), phase_md
            )

            return requirements

        except Exception as e:
            logger.error("Failed to parse checkpoint from %s: %s", phase_md, e)
            return None

    def _extract_checkpoint_section(self, content: str) -> Optional[str]:
        """
        Extract checkpoint/validation gate section from markdown.

        Looks for sections with headers like:
        - ## Checkpoint
        - ## Validation Gate
        - ## Phase Checkpoint

        Args:
            content: Markdown content

        Returns:
            Checkpoint section text or None
        """
        import re

        # Pattern to match checkpoint headers
        checkpoint_patterns = [
            r"##\s+(?:Phase\s+)?Checkpoint(?:\s+Validation)?",
            r"##\s+Validation\s+Gate",
            r"##\s+Evidence\s+(?:Required|Submission)",
        ]

        for pattern in checkpoint_patterns:
            match = re.search(
                pattern + r"(.*?)(?=\n##\s+|\Z)", content, re.DOTALL | re.IGNORECASE
            )
            if match:
                return match.group(1).strip()

        return None

    def _parse_evidence_fields(self, checkpoint_section: str) -> Dict[str, FieldSchema]:
        """
        Parse evidence field requirements from checkpoint section.

        Looks for patterns like:
        - **field_name**: description
        - - field_name: description
        - Required: field_name - description

        Args:
            checkpoint_section: Checkpoint section text

        Returns:
            Dictionary of field name to FieldSchema
        """
        import re

        evidence_schema = {}
        lines = checkpoint_section.split("\n")

        # Patterns to detect evidence fields
        field_patterns = [
            # **field_name**: description or - **field_name**: description
            r"^\s*-?\s*\*\*([a-z_]+)\*\*:\s*(.+)",
            # - field_name: description
            r"^\s*-\s+([a-z_]+):\s*(.+)",
            # "field_name" or `field_name` followed by description
            r'^\s*["\']?`?([a-z_]+)`?["\']?\s*[-:]\s*(.+)',
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for pattern in field_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    field_name = match.group(1).lower()
                    description = match.group(2).strip()

                    # Skip if field_name looks like a header or label
                    if len(field_name) > 50 or field_name in [
                        "required",
                        "optional",
                        "evidence",
                        "fields",
                    ]:
                        continue

                    # Infer type from description
                    field_type = self._infer_field_type(description)

                    # Determine if required
                    required = self._is_field_required(description)

                    evidence_schema[field_name] = FieldSchema(
                        name=field_name,
                        type=field_type,
                        required=required,
                        validator=None,
                        validator_params=None,
                        description=description,
                    )

                    logger.debug(
                        "Found field: %s (type=%s, required=%s)",
                        field_name,
                        field_type,
                        required,
                    )

                    break

        return evidence_schema

    def _infer_field_type(self, description: str) -> str:
        """
        Infer field type from description text.

        Args:
            description: Field description

        Returns:
            Type string (integer, boolean, string, list, object)
        """
        desc_lower = description.lower()

        # Integer indicators
        if any(
            word in desc_lower
            for word in ["number", "count", "total", "sum", "quantity"]
        ):
            return "integer"

        # Boolean indicators
        if any(
            word in desc_lower
            for word in ["true/false", "yes/no", "flag", "whether", "if"]
        ):
            return "boolean"

        # List indicators
        if any(
            word in desc_lower
            for word in ["list", "array", "collection", "items", "multiple"]
        ):
            return "list"

        # Object indicators
        if any(
            word in desc_lower
            for word in ["dict", "dictionary", "mapping", "object", "structure"]
        ):
            return "object"

        # Default to string
        return "string"

    def _is_field_required(self, description: str) -> bool:
        """
        Determine if field is required from description.

        Args:
            description: Field description

        Returns:
            True if required, False if optional
        """
        desc_lower = description.lower()

        # Check for optional indicators
        if any(word in desc_lower for word in ["optional", "if applicable", "may"]):
            return False

        # Check for required indicators
        if any(word in desc_lower for word in ["required", "must", "mandatory"]):
            return True

        # Default to required
        return True

    def generate_gate(self, requirements: CheckpointRequirements) -> str:
        """
        Generate gate-definition.yaml content from requirements.

        Converts CheckpointRequirements to properly formatted YAML
        following the gate-definition.yaml standard format.

        Args:
            requirements: Parsed checkpoint requirements

        Returns:
            YAML content string

        Example:
            >>> from mcp_server.config.checkpoint_loader import CheckpointRequirements, FieldSchema
            >>> requirements = CheckpointRequirements(
            ...     evidence_schema={"field": FieldSchema("field", "integer", True, None, None, "desc")},
            ...     validators={},
            ...     cross_field_rules=[],
            ...     strict=False,
            ...     allow_override=True,
            ...     source="parsed"
            ... )
            >>> script = MigrationScript(Path("."))
            >>> yaml_content = script.generate_gate(requirements)
            >>> assert "checkpoint:" in yaml_content
        """
        import yaml

        # Build gate structure
        gate_dict = {
            "checkpoint": {
                "strict": requirements.strict,
                "allow_override": requirements.allow_override,
            },
            "evidence_schema": {},
            "validators": requirements.validators,
        }

        # Add cross-field validation if present
        if requirements.cross_field_rules:
            gate_dict["cross_field_validation"] = [
                {"rule": rule.rule, "error_message": rule.error_message}
                for rule in requirements.cross_field_rules
            ]

        # Convert evidence schema to dict
        for field_name, field_schema in requirements.evidence_schema.items():
            field_dict = {
                "type": field_schema.type,
                "required": field_schema.required,
                "description": field_schema.description,
            }

            # Add validator if present
            if field_schema.validator:
                field_dict["validator"] = field_schema.validator

            # Add validator params if present
            if field_schema.validator_params:
                field_dict["validator_params"] = field_schema.validator_params

            gate_dict["evidence_schema"][field_name] = field_dict

        # Generate YAML with comments
        yaml_content = self._format_yaml_with_comments(gate_dict, requirements)

        return yaml_content

    def _format_yaml_with_comments(
        self, gate_dict: Dict[str, Any], requirements: CheckpointRequirements
    ) -> str:
        """
        Format gate dictionary as YAML with helpful comments.

        Args:
            gate_dict: Gate structure dictionary
            requirements: Original requirements

        Returns:
            Formatted YAML string with comments
        """
        import yaml

        # Header comment
        lines = [
            "# Gate Definition",
            "# Auto-generated from phase.md checkpoint section",
            "#",
            f"# Source: {requirements.source}",
            f"# Fields: {len(requirements.evidence_schema)}",
            "#",
            "",
        ]

        # Generate clean YAML
        yaml_str = yaml.dump(
            gate_dict, default_flow_style=False, sort_keys=False, allow_unicode=True
        )

        lines.append(yaml_str)

        return "\n".join(lines)

    def write_gate(self, gate_path: Path, content: str) -> None:
        """
        Write gate content to file.

        Args:
            gate_path: Path to gate file
            content: YAML content
        """
        gate_path.write_text(content, encoding="utf-8")

    def log_statistics(self) -> None:
        """Log final migration statistics."""
        logger.info("=" * 60)
        logger.info("Migration Complete")
        logger.info("=" * 60)
        logger.info("Workflows scanned: %d", self.stats["workflows_scanned"])
        logger.info("Phases scanned: %d", self.stats["phases_scanned"])
        logger.info("Gates created: %d", self.stats["gates_created"])
        logger.info("Gates skipped: %d", self.stats["gates_skipped"])
        logger.info("Errors: %d", self.stats["errors"])
        logger.info("=" * 60)


def main() -> int:
    """
    Main entry point for migration script.

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    parser = argparse.ArgumentParser(
        description="Generate gate-definition.yaml files for existing workflows"
    )
    parser.add_argument(
        "--workflows-path",
        type=Path,
        default=Path(".praxis-os/workflows"),
        help="Path to workflows directory (default: .praxis-os/workflows)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without creating files"
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing gates")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run migration
    script = MigrationScript(
        workflows_path=args.workflows_path, dry_run=args.dry_run, force=args.force
    )

    results = script.run()

    # Return error code if any errors occurred
    return 1 if results["errors"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Generate gate-definition.yaml files for all workflows.

Part of Evidence Validation System (Phase 2, Task 2.1-2.5).
Creates gate-definition.yaml for each phase in each workflow by parsing
checkpoint sections from phase.md files.

Usage:
    # Dry run (preview only)
    python scripts/generate-gate-definitions.py --dry-run

    # Generate for specific workflow
    python scripts/generate-gate-definitions.py --workflow spec_creation_v1

    # Generate for all workflows (lenient mode)
    python scripts/generate-gate-definitions.py

    # Generate with strict mode
    python scripts/generate-gate-definitions.py --strict
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class CheckpointParser:
    """Parse checkpoint requirements from phase.md files."""

    def parse_checkpoint(self, phase_md_path: Path) -> Dict[str, Any]:
        """
        Parse checkpoint section from phase.md file.

        Args:
            phase_md_path: Path to phase.md file

        Returns:
            Dictionary with parsed checkpoint data:
            - fields: Dict of field_name -> field_info
            - validation_criteria: List of validation rules

        Example:
            >>> parser = CheckpointParser()
            >>> data = parser.parse_checkpoint(Path("phase.md"))
            >>> data["fields"]["tests_passing"]
            {"type": "integer", "description": "Number of passing tests"}
        """
        if not phase_md_path.exists():
            logger.warning(f"Phase file not found: {phase_md_path}")
            return {"fields": {}}

        content = phase_md_path.read_text()

        # Find checkpoint/validation section
        checkpoint_match = re.search(
            r"##\s+.*(?:Checkpoint|Validation Gate|Evidence Requirements).*?\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )

        if not checkpoint_match:
            logger.debug(f"No checkpoint section found in {phase_md_path.name}")
            return {"fields": {}}

        checkpoint_text = checkpoint_match.group(1)

        # Extract evidence fields from checkbox lists
        fields = self._extract_evidence_fields(checkpoint_text)

        return {"fields": fields, "raw_text": checkpoint_text}

    def _extract_evidence_fields(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract evidence fields from checkpoint text.

        Looks for patterns like:
        - [ ] field_name: description
        - [ ] `field_name` - description
        - field_name (type): description

        Args:
            text: Checkpoint section text

        Returns:
            Dict of field_name -> {type, description, required}
        """
        fields = {}

        # Pattern 1: Checkbox with field name
        # - [ ] field_name: description
        # - [ ] `field_name` - description
        checkbox_pattern = (
            r"-\s*\[\s*\]\s*(?:`([^`]+)`|(\w+))(?:\s*[:-]\s*(.+?))?(?=\n|$)"
        )

        for match in re.finditer(checkbox_pattern, text):
            field_name = match.group(1) or match.group(2)
            description = match.group(3) or ""

            if field_name:
                field_name = field_name.strip()
                fields[field_name] = {
                    "type": self._infer_type(field_name, description),
                    "description": description.strip(),
                    "required": True,
                }

        # Pattern 2: Bold field names
        # **field_name**: description
        bold_pattern = r"\*\*([a-z_]+)\*\*\s*[:-]\s*(.+?)(?=\n|$)"

        for match in re.finditer(bold_pattern, text):
            field_name = match.group(1).strip()
            description = match.group(2).strip()

            if field_name not in fields:
                fields[field_name] = {
                    "type": self._infer_type(field_name, description),
                    "description": description,
                    "required": True,
                }

        return fields

    def _infer_type(self, field_name: str, description: str) -> str:
        """
        Infer field type from name and description.

        Args:
            field_name: Field name (e.g., "tests_passing")
            description: Field description

        Returns:
            Type name: "boolean", "integer", "string", "list"
        """
        field_lower = field_name.lower()
        desc_lower = description.lower()

        # Boolean patterns
        if any(word in field_lower for word in ["is_", "has_", "can_", "should_"]):
            return "boolean"
        if any(word in desc_lower for word in ["true/false", "yes/no", "flag"]):
            return "boolean"

        # Integer patterns
        if any(
            word in field_lower
            for word in ["count", "num", "total", "passing", "failing"]
        ):
            return "integer"
        if any(word in desc_lower for word in ["number of", "count of", "total"]):
            return "integer"

        # List patterns
        if field_name.endswith("s") or field_name.endswith("_list"):
            return "list"
        if any(word in desc_lower for word in ["list of", "array of", "collection"]):
            return "list"

        # Default to string
        return "string"


class GateGenerator:
    """Generate gate-definition.yaml files from checkpoint data."""

    def __init__(self, strict: bool = False):
        """
        Initialize gate generator.

        Args:
            strict: Whether to generate strict gates (True) or lenient (False)
        """
        self.strict = strict

    def generate_gate_yaml(
        self, checkpoint_data: Dict[str, Any], phase_number: int
    ) -> str:
        """
        Generate gate-definition.yaml content from checkpoint data.

        Args:
            checkpoint_data: Parsed checkpoint data
            phase_number: Phase number (affects strictness)

        Returns:
            YAML content string

        Example:
            >>> gen = GateGenerator()
            >>> yaml_content = gen.generate_gate_yaml(data, 1)
        """
        fields = checkpoint_data.get("fields", {})

        # Build gate structure
        gate = {
            "checkpoint": {
                "strict": self.strict and phase_number >= 2,  # Phases 0-1 lenient
                "allow_override": True,
            },
            "evidence_schema": {},
            "validators": {},
        }

        # Add common validators
        if any(f.get("type") == "integer" for f in fields.values()):
            gate["validators"]["positive"] = "lambda x: x > 0"

        # Generate schema for each field
        for field_name, field_info in fields.items():
            field_type = field_info.get("type", "string")

            schema = {
                "type": field_type,
                "required": field_info.get("required", True),
                "description": field_info.get("description", ""),
            }

            # Add validator if needed
            if field_type == "integer":
                schema["validator"] = "positive"

            gate["evidence_schema"][field_name] = schema

        # Convert to YAML with nice formatting
        return yaml.dump(gate, sort_keys=False, default_flow_style=False)


class MigrationRunner:
    """Run migration to generate gates for all workflows."""

    def __init__(
        self,
        workflows_dir: str = ".praxis-os/workflows",
        dry_run: bool = False,
        strict: bool = False,
    ):
        """
        Initialize migration runner.

        Args:
            workflows_dir: Path to workflows directory
            dry_run: If True, only preview without writing files
            strict: If True, generate strict gates
        """
        self.workflows_dir = Path(workflows_dir)
        self.dry_run = dry_run
        self.parser = CheckpointParser()
        self.generator = GateGenerator(strict=strict)

        # Statistics
        self.stats = {
            "workflows_scanned": 0,
            "phases_processed": 0,
            "gates_generated": 0,
            "gates_skipped": 0,
            "errors": 0,
        }

    def scan_workflows(self, workflow_filter: Optional[str] = None) -> List[str]:
        """
        Scan workflows directory for all workflows.

        Args:
            workflow_filter: Optional workflow name to process only that workflow

        Returns:
            List of workflow names (sorted)

        Example:
            >>> runner = MigrationRunner()
            >>> workflows = runner.scan_workflows()
            >>> "spec_creation_v1" in workflows
            True
        """
        if not self.workflows_dir.exists():
            logger.error(f"Workflows directory not found: {self.workflows_dir}")
            return []

        workflows = []

        for entry in self.workflows_dir.iterdir():
            if not entry.is_dir():
                continue

            # Check if it has phases directory
            phases_dir = entry / "phases"
            if not phases_dir.exists():
                continue

            # Apply filter if specified
            if workflow_filter and entry.name != workflow_filter:
                continue

            workflows.append(entry.name)

        return sorted(workflows)

    def process_workflow(self, workflow_name: str) -> int:
        """
        Process a single workflow, generating gates for all phases.

        Args:
            workflow_name: Workflow name

        Returns:
            Number of gates generated
        """
        workflow_dir = self.workflows_dir / workflow_name
        phases_dir = workflow_dir / "phases"

        if not phases_dir.exists():
            logger.warning(f"Phases directory not found: {phases_dir}")
            return 0

        logger.info(f"\nProcessing workflow: {workflow_name}")
        self.stats["workflows_scanned"] += 1

        gates_generated = 0

        # Process each phase directory
        for phase_dir in sorted(phases_dir.iterdir()):
            if not phase_dir.is_dir():
                continue

            # Extract phase number from directory name
            try:
                phase_number = int(phase_dir.name)
            except ValueError:
                logger.debug(f"Skipping non-numeric phase directory: {phase_dir.name}")
                continue

            gates_generated += self._process_phase(
                workflow_name, phase_number, phase_dir
            )

        return gates_generated

    def _process_phase(
        self, workflow_name: str, phase_number: int, phase_dir: Path
    ) -> int:
        """
        Process a single phase, generating gate-definition.yaml.

        Args:
            workflow_name: Workflow name
            phase_number: Phase number
            phase_dir: Path to phase directory

        Returns:
            1 if gate generated, 0 otherwise
        """
        self.stats["phases_processed"] += 1

        # Find phase.md file
        phase_md = phase_dir / "phase.md"
        if not phase_md.exists():
            logger.debug(f"No phase.md in {phase_dir}")
            return 0

        # Check if gate already exists
        gate_file = phase_dir / "gate-definition.yaml"
        if gate_file.exists():
            logger.debug(f"Gate already exists: {gate_file}")
            self.stats["gates_skipped"] += 1
            return 0

        # Parse checkpoint
        try:
            checkpoint_data = self.parser.parse_checkpoint(phase_md)

            if not checkpoint_data.get("fields"):
                logger.debug(
                    f"No checkpoint fields found in {workflow_name} Phase {phase_number}"
                )
                return 0

            # Generate gate YAML
            gate_yaml = self.generator.generate_gate_yaml(checkpoint_data, phase_number)

            # Write or preview
            if self.dry_run:
                logger.info(
                    f"[DRY-RUN] Would create: {gate_file}\n"
                    f"Fields: {list(checkpoint_data['fields'].keys())}"
                )
            else:
                gate_file.write_text(gate_yaml)
                logger.info(
                    f"Generated: {gate_file} "
                    f"({len(checkpoint_data['fields'])} fields)"
                )

            self.stats["gates_generated"] += 1
            return 1

        except Exception as e:
            logger.error(f"Error processing {phase_dir}: {e}")
            self.stats["errors"] += 1
            return 0

    def run(self, workflow_filter: Optional[str] = None) -> Dict[str, int]:
        """
        Run migration on all workflows.

        Args:
            workflow_filter: Optional workflow name to process only that workflow

        Returns:
            Statistics dictionary
        """
        logger.info("=" * 70)
        logger.info("Gate Definition Migration")
        logger.info("=" * 70)
        logger.info(f"Workflows directory: {self.workflows_dir}")
        logger.info(f"Dry run: {self.dry_run}")
        logger.info(f"Strict mode: {self.generator.strict}")

        # Scan workflows
        workflows = self.scan_workflows(workflow_filter)
        logger.info(f"\nFound {len(workflows)} workflows")

        if not workflows:
            logger.error("No workflows found!")
            return self.stats

        # Process each workflow
        for workflow_name in workflows:
            self.process_workflow(workflow_name)

        # Print summary
        self._print_summary()

        return self.stats

    def _print_summary(self):
        """Print migration summary statistics."""
        logger.info("\n" + "=" * 70)
        logger.info("Migration Summary")
        logger.info("=" * 70)
        logger.info(f"Workflows scanned:  {self.stats['workflows_scanned']}")
        logger.info(f"Phases processed:   {self.stats['phases_processed']}")
        logger.info(f"Gates generated:    {self.stats['gates_generated']}")
        logger.info(f"Gates skipped:      {self.stats['gates_skipped']}")
        logger.info(f"Errors:             {self.stats['errors']}")

        if self.dry_run:
            logger.info("\n[DRY-RUN] No files were modified.")
            logger.info("Remove --dry-run to generate gates.")


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description="Generate gate-definition.yaml files for all workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without writing files"
    )

    parser.add_argument("--workflow", type=str, help="Process only specified workflow")

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Generate strict gates (errors block advancement)",
    )

    parser.add_argument(
        "--workflows-dir",
        type=str,
        default=".praxis-os/workflows",
        help="Path to workflows directory (default: .praxis-os/workflows)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run migration
    runner = MigrationRunner(
        workflows_dir=args.workflows_dir, dry_run=args.dry_run, strict=args.strict
    )

    stats = runner.run(workflow_filter=args.workflow)

    # Exit with error if any errors occurred
    if stats["errors"] > 0:
        logger.error("\nMigration completed with errors!")
        sys.exit(1)

    logger.info("\nMigration completed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()

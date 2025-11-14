"""
WorkflowDefinitionParser for parsing workflow YAML definitions.

Parses workflow definition files into structured DynamicPhase/Task objects
for iterative workflow generation in workflow_creation_v1.

Extracted from task_parser.py to enable modular parser architecture.
Target: ~150 lines after extraction
"""

from pathlib import Path
from typing import List, Optional

import yaml

from ouroboros.subsystems.workflow.models import DynamicPhase, DynamicTask

from ..base import ParseError, SourceParser


class WorkflowDefinitionParser(SourceParser):
    """
    Parser for workflow definition YAML files.

    Parses workflow definition YAML and extracts phase/task structure
    for iterative workflow generation in workflow_creation_v1.

    Unlike SpecTasksParser (which parses markdown for display),
    this parser extracts structured data for file generation.
    """

    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse workflow definition YAML into DynamicPhase objects.

        Args:
            source_path: Path to workflow definition YAML file

        Returns:
            List of DynamicPhase objects (one per target workflow phase)

        Raises:
            ParseError: If file is invalid or cannot be parsed
        """
        if not source_path.exists():
            raise ParseError(f"Definition file not found: {source_path}")

        try:
            with open(source_path, "r", encoding="utf-8") as f:
                definition = yaml.safe_load(f)
        except Exception as e:
            raise ParseError(f"Failed to read YAML: {e}") from e

        if not definition:
            raise ParseError(f"Definition file is empty: {source_path}")

        # Extract phases array
        phases_data = definition.get("phases", [])
        if not phases_data:
            raise ParseError("No phases found in definition")

        # Convert each target phase into DynamicPhase
        dynamic_phases = []
        for phase_data in phases_data:
            dynamic_phase = self._build_dynamic_phase(phase_data)
            if dynamic_phase:
                dynamic_phases.append(dynamic_phase)

        return dynamic_phases

    def _build_dynamic_phase(self, phase_data: dict) -> Optional[DynamicPhase]:
        """
        Build a DynamicPhase from workflow definition phase data.

        Args:
            phase_data: Phase dictionary from workflow definition

        Returns:
            DynamicPhase object or None if invalid
        """
        phase_number = phase_data.get("number", 0)
        phase_name = phase_data.get("name", f"Phase {phase_number}")
        description = phase_data.get("purpose", "")
        estimated_duration = phase_data.get("estimated_duration", "Variable")

        # Extract tasks
        tasks_data = phase_data.get("tasks", [])
        tasks = []
        for task_data in tasks_data:
            task = self._build_dynamic_task(task_data, phase_number)
            if task:
                tasks.append(task)

        # Extract validation gate
        validation_gate_data = phase_data.get("validation_gate", {})
        validation_gate = self._extract_validation_gate(validation_gate_data)

        return DynamicPhase(
            phase_number=phase_number,
            phase_name=phase_name,
            description=description,
            estimated_duration=estimated_duration,
            tasks=tasks,
            validation_gate=validation_gate,
        )

    def _build_dynamic_task(
        self, task_data: dict, phase_number: int
    ) -> Optional[DynamicTask]:
        """
        Build a DynamicTask from workflow definition task data.

        Args:
            task_data: Task dictionary from workflow definition
            phase_number: Parent phase number

        Returns:
            DynamicTask object or None if invalid
        """
        task_number = task_data.get("number", 1)
        task_name = task_data.get("name", f"task-{task_number}")
        task_purpose = task_data.get("purpose", "")

        # Build task ID (matches phase.task format)
        task_id = f"{phase_number}.{task_number}"

        # Extract optional fields
        estimated_time = task_data.get("estimated_time", "Variable")
        dependencies = task_data.get("dependencies", [])
        acceptance_criteria = task_data.get("validation_criteria", [])

        return DynamicTask(
            task_id=task_id,
            task_name=task_name,
            description=task_purpose,
            estimated_time=estimated_time,
            dependencies=dependencies,
            acceptance_criteria=acceptance_criteria,
        )

    def _extract_validation_gate(self, validation_gate_data: dict) -> List[str]:
        """
        Extract validation gate criteria from definition.

        Args:
            validation_gate_data: Validation gate dictionary

        Returns:
            List of validation criteria strings
        """
        criteria = []

        # Extract evidence_required fields
        evidence_required = validation_gate_data.get("evidence_required", {})
        for field_name, field_data in evidence_required.items():
            if isinstance(field_data, dict):
                description = field_data.get("description", field_name)
                field_type = field_data.get("type", "unknown")
                validator = field_data.get("validator", "")
                criteria.append(
                    f"{field_name} ({field_type}, {validator}): {description}"
                )
            else:
                criteria.append(str(field_data))

        return criteria


__all__ = [
    "WorkflowDefinitionParser",
]

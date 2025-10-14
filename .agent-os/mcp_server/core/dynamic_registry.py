"""
Dynamic content registry for workflow sessions.

Manages template loading, source parsing, and content rendering for dynamic workflows.
Each registry instance is tied to a single workflow session.
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: __init__ requires 6 parameters for complete registry setup
# (workflow_type, parser, source paths, template paths) - all necessary for
# flexible dynamic content management

from pathlib import Path
from typing import Any, Dict

from mcp_server.core.parsers import SourceParser
from mcp_server.models.workflow import DynamicWorkflowContent


class DynamicRegistryError(Exception):
    """Raised when dynamic registry operations fail."""


class DynamicContentRegistry:
    """
    Session-scoped registry for dynamically-generated workflow content.

    Manages the lifecycle of dynamic workflow content:
    1. Load templates from filesystem on initialization
    2. Parse source using provided parser
    3. Cache parsed phases and rendered content
    4. Serve content via get_phase_content() and get_task_content()
    5. Provide metadata for workflow engine responses

    This class is instantiated once per dynamic workflow session and
    lives for the duration of the session.

    Attributes:
        workflow_type: Type of workflow (e.g., "spec_execution_v1")
        content: Parsed and cached DynamicWorkflowContent
    """

    def __init__(
        self,
        workflow_type: str,
        phase_template_path: Path,
        task_template_path: Path,
        source_path: Path,
        parser: SourceParser,
    ):
        """
        Initialize dynamic content registry for a workflow session.

        Loads templates, parses source, and creates cached content structure.

        Args:
            workflow_type: Workflow type identifier
            phase_template_path: Path to phase template file
            task_template_path: Path to task template file
            source_path: Path to source file (e.g., spec's tasks.md)
            parser: SourceParser instance for parsing source

        Raises:
            DynamicRegistryError: If template loading or parsing fails
        """
        self.workflow_type = workflow_type

        # Load templates
        try:
            phase_template = self._load_template(phase_template_path)
            task_template = self._load_template(task_template_path)
        except Exception as e:
            raise DynamicRegistryError(f"Failed to load templates: {e}") from e

        # Parse source into structured phases
        try:
            phases = parser.parse(source_path)
        except Exception as e:
            raise DynamicRegistryError(
                f"Failed to parse source {source_path}: {e}"
            ) from e

        if not phases:
            raise DynamicRegistryError(f"No phases parsed from {source_path}")

        # Create cached content structure
        self.content = DynamicWorkflowContent(
            source_path=str(source_path),
            workflow_type=workflow_type,
            phase_template=phase_template,
            task_template=task_template,
            phases=phases,
        )

    def _load_template(self, template_path: Path) -> str:
        """
        Load template file from filesystem.

        Args:
            template_path: Path to template file

        Returns:
            Template content as string

        Raises:
            DynamicRegistryError: If template file not found or unreadable
        """
        if not template_path.exists():
            raise DynamicRegistryError(f"Template not found: {template_path}")

        try:
            return template_path.read_text(encoding="utf-8")
        except Exception as e:
            raise DynamicRegistryError(
                f"Failed to read template {template_path}: {e}"
            ) from e

    def get_phase_content(self, phase: int) -> str:
        """
        Get rendered phase content with command language.

        Uses lazy rendering and caching for performance.

        Args:
            phase: Phase number to render (matches phase_number field)

        Returns:
            Rendered phase content with enforcement commands

        Raises:
            IndexError: If phase not found
        """
        return self.content.render_phase(phase)

    def get_task_content(self, phase: int, task_number: int) -> str:
        """
        Get rendered task content with command language.

        Uses lazy rendering and caching for performance.

        Args:
            phase: Phase number (matches phase_number field)
            task_number: Task number within phase (1-indexed)

        Returns:
            Rendered task content with enforcement commands

        Raises:
            IndexError: If phase or task not found
        """
        return self.content.render_task(phase, task_number)

    def get_phase_metadata(self, phase: int) -> Dict[str, Any]:
        """
        Get phase metadata for workflow engine responses.

        Returns summary information about phase without full content,
        useful for building workflow engine API responses.

        Args:
            phase: Phase number

        Returns:
            Dictionary with phase metadata:
                - phase_number: int
                - phase_name: str
                - description: str
                - estimated_duration: str
                - task_count: int
                - tasks: List[Dict] with task metadata
                - validation_gate: List[str]

        Raises:
            IndexError: If phase not found
        """
        # Find phase by phase_number
        phase_data = next(
            (p for p in self.content.phases if p.phase_number == phase), None
        )

        if not phase_data:
            raise IndexError(f"Phase {phase} not found")

        # Build task metadata list
        tasks_metadata = [
            {
                "task_number": i + 1,
                "task_id": task.task_id,
                "task_name": task.task_name,
                "estimated_time": task.estimated_time,
                "dependencies": task.dependencies,
            }
            for i, task in enumerate(phase_data.tasks)
        ]

        return {
            "phase_number": phase_data.phase_number,
            "phase_name": phase_data.phase_name,
            "description": phase_data.description,
            "estimated_duration": phase_data.estimated_duration,
            "task_count": len(phase_data.tasks),
            "tasks": tasks_metadata,
            "validation_gate": phase_data.validation_gate,
        }

    def get_total_phases(self) -> int:
        """
        Get total number of phases in this workflow.

        Returns:
            Number of phases
        """
        return len(self.content.phases)

    def has_phase(self, phase: int) -> bool:
        """
        Check if phase exists in this workflow.

        Args:
            phase: Phase number to check

        Returns:
            True if phase exists, False otherwise
        """
        return any(p.phase_number == phase for p in self.content.phases)

    def get_all_phases_metadata(self) -> list[Dict[str, Any]]:
        """
        Get metadata for all phases.

        Useful for workflow overview and planning.

        Returns:
            List of phase metadata dictionaries
        """
        return [
            self.get_phase_metadata(phase.phase_number) for phase in self.content.phases
        ]


__all__ = [
    "DynamicRegistryError",
    "DynamicContentRegistry",
]

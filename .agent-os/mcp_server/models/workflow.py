"""
Workflow state and metadata models.

All workflow-related data structures for phase gating, checkpoints,
and workflow execution tracking.
"""

# pylint: disable=too-many-instance-attributes
# Justification: Data models (dataclasses) require many attributes to represent
# complete workflow state, metadata, and checkpoint information. This is by design
# for comprehensive type-safe data structures.

from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class CheckpointStatus(str, Enum):
    """Status of checkpoint validation."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CommandExecution:
    """
    Record of a command executed during phase.

    Tracks what commands were run and their results for evidence collection.
    """

    command: str  # Command that was run
    output: str  # Command output
    exit_code: int  # Exit code
    executed_at: datetime  # When command was run
    duration_ms: float  # How long it took

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "command": self.command,
            "output": self.output,
            "exit_code": self.exit_code,
            "executed_at": self.executed_at.isoformat(),
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommandExecution":
        """Deserialize from dictionary."""
        return cls(
            command=data["command"],
            output=data["output"],
            exit_code=data["exit_code"],
            executed_at=datetime.fromisoformat(data["executed_at"]),
            duration_ms=data["duration_ms"],
        )


@dataclass
class PhaseArtifact:
    """
    Artifacts produced by completing a phase.

    Contains evidence for checkpoint validation and outputs for next phases.
    """

    phase_number: int  # Which phase produced this
    evidence: Dict[str, Any]  # Required evidence for checkpoint
    outputs: Dict[str, Any]  # Phase outputs (function lists, etc.)
    commands_executed: List[CommandExecution]  # Commands run
    timestamp: datetime  # When artifact created

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "phase_number": self.phase_number,
            "evidence": self.evidence,
            "outputs": self.outputs,
            "commands_executed": [cmd.to_dict() for cmd in self.commands_executed],
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhaseArtifact":
        """Deserialize from dictionary."""
        return cls(
            phase_number=data["phase_number"],
            evidence=data["evidence"],
            outputs=data["outputs"],
            commands_executed=[
                CommandExecution.from_dict(cmd) for cmd in data["commands_executed"]
            ],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


@dataclass
class WorkflowState:
    """
    Represents current state of workflow (e.g., test generation).

    Enforces phase gating - only current phase is accessible.
    """

    session_id: str  # Unique session identifier
    workflow_type: str  # "test_generation_v3", "production_code_v2"
    target_file: str  # File being worked on
    current_phase: int  # Current phase number (1-8)
    completed_phases: List[int]  # Phases completed
    phase_artifacts: Dict[int, PhaseArtifact]  # Outputs from each phase
    checkpoints: Dict[int, CheckpointStatus]  # Checkpoint pass/fail status
    created_at: datetime  # Session start time
    updated_at: datetime  # Last update time
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to JSON for persistence.

        Returns:
            Dictionary representation of workflow state
        """
        return {
            "session_id": self.session_id,
            "workflow_type": self.workflow_type,
            "target_file": self.target_file,
            "current_phase": self.current_phase,
            "completed_phases": self.completed_phases,
            "phase_artifacts": {
                phase: artifact.to_dict()
                for phase, artifact in self.phase_artifacts.items()
            },
            "checkpoints": {
                phase: status.value for phase, status in self.checkpoints.items()
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """
        Deserialize from JSON.

        Args:
            data: Dictionary representation

        Returns:
            WorkflowState instance
        """
        return cls(
            session_id=data["session_id"],
            workflow_type=data["workflow_type"],
            target_file=data["target_file"],
            current_phase=data["current_phase"],
            completed_phases=data["completed_phases"],
            phase_artifacts={
                int(phase): PhaseArtifact.from_dict(artifact)
                for phase, artifact in data["phase_artifacts"].items()
            },
            checkpoints={
                int(phase): CheckpointStatus(status)
                for phase, status in data["checkpoints"].items()
            },
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )

    def can_access_phase(self, phase: int) -> bool:
        """
        Check if phase is accessible given current state.

        Phase gating enforcement: Current phase OR completed phases are accessible.

        Args:
            phase: Phase number to check

        Returns:
            True if phase is accessible, False otherwise
        """
        # Can access current phase
        if phase == self.current_phase:
            return True

        # Can review completed phases
        if phase in self.completed_phases:
            return True

        # Cannot access future phases
        return False

    def complete_phase(
        self, phase: int, artifact: PhaseArtifact, checkpoint_passed: bool = True
    ) -> None:
        """
        Mark phase complete and advance to next.

        Args:
            phase: Phase number being completed
            artifact: Phase artifacts for evidence
            checkpoint_passed: Whether checkpoint validation passed

        Raises:
            ValueError: If trying to complete wrong phase
        """
        if phase != self.current_phase:
            raise ValueError(
                f"Cannot complete phase {phase}, current phase is {self.current_phase}"
            )

        # Store artifacts and checkpoint status
        self.phase_artifacts[phase] = artifact
        self.checkpoints[phase] = (
            CheckpointStatus.PASSED if checkpoint_passed else CheckpointStatus.FAILED
        )

        if checkpoint_passed:
            # Mark phase complete and advance
            self.completed_phases.append(phase)
            self.current_phase = phase + 1

        self.updated_at = datetime.now()

    def get_artifact(self, phase: int) -> Optional[PhaseArtifact]:
        """
        Get artifact from completed phase.

        Args:
            phase: Phase number

        Returns:
            PhaseArtifact if available, None otherwise
        """
        return self.phase_artifacts.get(phase)

    def is_complete(self) -> bool:
        """
        Check if workflow is complete.

        Returns:
            True if all phases completed
        """
        # Assuming 8 phases for test generation
        max_phases = 8 if "test" in self.workflow_type else 6
        return self.current_phase > max_phases


@dataclass
class CheckpointCriteria:
    """
    Criteria for validating phase checkpoint.

    Defines what evidence is required to pass a checkpoint.
    """

    phase_number: int  # Which phase these criteria apply to
    required_evidence: Dict[str, str]  # field_name: field_type
    validators: Dict[str, Any]  # field_name: validation_function
    description: str  # Human-readable description

    def validate(self, evidence: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate evidence against criteria.

        Args:
            evidence: Evidence dictionary from phase artifact

        Returns:
            Tuple of (passed: bool, missing_fields: List[str])
        """
        missing_fields = []

        for field_name, field_type in self.required_evidence.items():
            # Check field exists
            if field_name not in evidence:
                missing_fields.append(field_name)
                continue

            # Check field type
            value = evidence[field_name]
            if field_type == "int" and not isinstance(value, int):
                missing_fields.append(f"{field_name} (wrong type)")
            elif field_type == "str" and not isinstance(value, str):
                missing_fields.append(f"{field_name} (wrong type)")
            elif field_type == "list" and not isinstance(value, list):
                missing_fields.append(f"{field_name} (wrong type)")

            # Run custom validator if exists
            if field_name in self.validators:
                validator = self.validators[field_name]
                if not validator(value):
                    missing_fields.append(f"{field_name} (validation failed)")

        passed = len(missing_fields) == 0
        return passed, missing_fields


@dataclass
class PhaseMetadata:
    """
    Metadata for a single phase in a workflow.

    Provides overview information about phase purpose, effort, and validation.

    For hybrid dynamic workflows (e.g., spec_execution_v1), some phases may have
    static tasks defined in metadata while others are dynamically generated.
    """

    phase_number: int
    phase_name: str
    purpose: str
    estimated_effort: str
    key_deliverables: List[str]
    validation_criteria: List[str]
    tasks: Optional[List[Dict[str, Any]]] = None  # Static tasks for hybrid workflows
    task_execution: Optional[Dict[str, Any]] = None  # Dynamic task execution config

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        result = asdict(self)
        # Remove None values for cleaner output
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhaseMetadata":
        """
        Deserialize from dictionary.

        Filters out unknown fields for forward compatibility.
        """
        # Get known fields from dataclass
        known_fields = {f.name for f in fields(cls)}

        # Filter to only known fields
        filtered_data = {k: v for k, v in data.items() if k in known_fields}

        return cls(**filtered_data)


@dataclass
class WorkflowMetadata:
    """
    Metadata for complete workflow overview.

    Provides upfront information about workflow structure, phases, and expected outputs.
    This allows AI agents to plan effectively without needing separate API calls.

    Extended to support dynamic workflows where phase/task content is generated
    from external sources (e.g., spec tasks.md files) rather than static workflow files.
    """

    workflow_type: str
    version: str
    description: str
    total_phases: Union[int, str]  # int or "dynamic" for dynamic workflows
    estimated_duration: str
    primary_outputs: List[str]
    phases: List[PhaseMetadata]

    # Dynamic workflow support (optional)
    dynamic_phases: bool = False
    dynamic_config: Optional[Dict[str, Any]] = None
    # dynamic_config structure:
    # {
    #     "source_type": "spec_tasks_md",
    #     "source_path_key": "spec_path",
    #     "templates": {
    #         "phase": "phases/dynamic/phase-template.md",
    #         "task": "phases/dynamic/task-template.md"
    #     },
    #     "parser": "spec_tasks_parser"
    # }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        result: Dict[str, Any] = {
            "workflow_type": self.workflow_type,
            "version": self.version,
            "description": self.description,
            "total_phases": self.total_phases,
            "estimated_duration": self.estimated_duration,
            "primary_outputs": self.primary_outputs,
            "phases": [phase.to_dict() for phase in self.phases],
        }

        # Add dynamic workflow fields if present
        if self.dynamic_phases:
            result["dynamic_phases"] = self.dynamic_phases
        if self.dynamic_config:
            result["dynamic_config"] = self.dynamic_config

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowMetadata":
        """
        Deserialize from dictionary.

        Handles dynamic workflows where total_phases may be "dynamic" string.
        """
        # Handle total_phases - can be int or "dynamic" string
        total_phases = data["total_phases"]
        if isinstance(total_phases, str) and total_phases == "dynamic":
            # For dynamic workflows, use the actual phase count from phases array
            total_phases = len(data["phases"])

        return cls(
            workflow_type=data["workflow_type"],
            version=data["version"],
            description=data.get("description", ""),
            total_phases=total_phases,
            estimated_duration=data["estimated_duration"],
            primary_outputs=data["primary_outputs"],
            phases=[PhaseMetadata.from_dict(p) for p in data["phases"]],
            dynamic_phases=data.get("dynamic_phases", False),
            dynamic_config=data.get("dynamic_config"),
        )


@dataclass
class WorkflowConfig:
    """
    Configuration for workflow execution.

    Defines workflow-specific settings and parameters.
    """

    workflow_type: str  # Type identifier
    total_phases: int  # Number of phases
    phase_names: List[str]  # Names of each phase
    strict_gating: bool = True  # Enforce strict phase order
    allow_phase_skip: bool = False  # Allow skipping phases (dangerous!)
    checkpoint_required: bool = True  # Require checkpoint validation
    auto_save: bool = True  # Auto-save state after each phase

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowConfig":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class DynamicTask:
    """
    Task structure parsed from external source (e.g., spec tasks.md).

    Represents a single task within a dynamic workflow phase with all metadata
    needed for template rendering and execution guidance.

    Attributes:
        task_id: Unique task identifier (e.g., "1.1", "2.3")
        task_name: Human-readable task name
        description: Detailed description of what needs to be done
        estimated_time: Estimated completion time (e.g., "2 hours", "30 minutes")
        dependencies: List of task IDs this task depends on (e.g., ["1.1", "1.2"])
        acceptance_criteria: List of criteria that must be met for task completion
    """

    task_id: str
    task_name: str
    description: str
    estimated_time: str
    dependencies: List[str]
    acceptance_criteria: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for rendering."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DynamicTask":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class DynamicPhase:
    """
    Phase structure parsed from external source (e.g., spec tasks.md).

    Represents a complete phase in a dynamic workflow including all tasks,
    metadata, and validation gates needed for execution.

    Attributes:
        phase_number: Sequential phase number (0, 1, 2, ...)
        phase_name: Human-readable phase name
        description: Phase goal or purpose
        estimated_duration: Estimated time to complete entire phase
        tasks: List of DynamicTask objects for this phase
        validation_gate: List of validation criteria that must pass before advancing
    """

    phase_number: int
    phase_name: str
    description: str
    estimated_duration: str
    tasks: List[DynamicTask]
    validation_gate: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for rendering."""
        return {
            "phase_number": self.phase_number,
            "phase_name": self.phase_name,
            "description": self.description,
            "estimated_duration": self.estimated_duration,
            "tasks": [task.to_dict() for task in self.tasks],
            "validation_gate": self.validation_gate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DynamicPhase":
        """Deserialize from dictionary."""
        return cls(
            phase_number=data["phase_number"],
            phase_name=data["phase_name"],
            description=data["description"],
            estimated_duration=data["estimated_duration"],
            tasks=[DynamicTask.from_dict(t) for t in data["tasks"]],
            validation_gate=data["validation_gate"],
        )

    def get_task(self, task_number: int) -> Optional[DynamicTask]:
        """
        Get task by number (1-indexed).

        Args:
            task_number: Task number (1-indexed)

        Returns:
            DynamicTask if found, None otherwise
        """
        if 1 <= task_number <= len(self.tasks):
            return self.tasks[task_number - 1]
        return None


@dataclass
class DynamicWorkflowContent:
    """
    Parsed and cached content for a dynamic workflow session.

    This class holds all parsed phase/task data from an external source,
    loaded templates, and caches rendered content for performance.
    Lifecycle is tied to workflow session.

    Attributes:
        source_path: Path to external source file (e.g., spec's tasks.md)
        workflow_type: Workflow type identifier
        phase_template: Loaded phase template content
        task_template: Loaded task template content
        phases: List of all parsed DynamicPhase objects
        _rendered_phases: Cache of rendered phase content (lazy initialization)
        _rendered_tasks: Cache of rendered task content (lazy initialization)
    """

    source_path: str  # Path as string for JSON serialization
    workflow_type: str
    phase_template: str
    task_template: str
    phases: List[DynamicPhase]
    _rendered_phases: Dict[int, str] = field(default_factory=dict, repr=False)
    _rendered_tasks: Dict[tuple, str] = field(default_factory=dict, repr=False)

    def render_phase(self, phase: int) -> str:
        """
        Render phase template with phase data.

        Uses simple placeholder replacement with cached results.

        Args:
            phase: Phase number to render (matches phase_number field)

        Returns:
            Rendered phase content with command language

        Raises:
            IndexError: If phase number not found
        """
        if phase not in self._rendered_phases:
            # Find phase by phase_number (not list index)
            phase_data = next((p for p in self.phases if p.phase_number == phase), None)
            if not phase_data:
                raise IndexError(f"Phase {phase} not found")

            self._rendered_phases[phase] = self._render_template(
                self.phase_template, phase_data
            )
        return self._rendered_phases[phase]

    def render_task(self, phase: int, task_number: int) -> str:
        """
        Render task template with task data.

        Uses simple placeholder replacement with cached results.

        Args:
            phase: Phase number (matches phase_number field)
            task_number: Task number within phase (1-indexed)

        Returns:
            Rendered task content with command language

        Raises:
            IndexError: If phase or task number not found
        """
        cache_key = (phase, task_number)
        if cache_key not in self._rendered_tasks:
            # Find phase by phase_number (not list index)
            phase_data = next((p for p in self.phases if p.phase_number == phase), None)
            if not phase_data:
                raise IndexError(f"Phase {phase} not found")

            task_data = phase_data.get_task(task_number)
            if not task_data:
                raise IndexError(f"Task {task_number} not found in phase {phase}")

            self._rendered_tasks[cache_key] = self._render_template(
                self.task_template, task_data, phase_data
            )
        return self._rendered_tasks[cache_key]

    def _render_template(
        self,
        template: str,
        task_or_phase_data: Any,
        phase_data: Optional[DynamicPhase] = None,
    ) -> str:
        """
        Simple placeholder replacement renderer.

        Replaces [PLACEHOLDER] markers with values from data objects.

        Args:
            template: Template string with [PLACEHOLDER] markers
            task_or_phase_data: DynamicTask or DynamicPhase object
            phase_data: Optional phase data for task rendering

        Returns:
            Rendered template string
        """
        result = template

        # Handle DynamicPhase rendering
        if isinstance(task_or_phase_data, DynamicPhase):
            phase = task_or_phase_data
            result = result.replace("[PHASE_NUMBER]", str(phase.phase_number))
            result = result.replace("[PHASE_NAME]", phase.phase_name)
            result = result.replace("[PHASE_DESCRIPTION]", phase.description)
            result = result.replace("[ESTIMATED_DURATION]", phase.estimated_duration)
            result = result.replace("[TASK_COUNT]", str(len(phase.tasks)))
            result = result.replace("[NEXT_PHASE_NUMBER]", str(phase.phase_number + 1))

            # Format validation gate as list
            gate_formatted = "\n".join(
                f"- [ ] {criterion}" for criterion in phase.validation_gate
            )
            result = result.replace("[VALIDATION_GATE]", gate_formatted)

        # Handle DynamicTask rendering
        elif isinstance(task_or_phase_data, DynamicTask):
            task = task_or_phase_data
            result = result.replace("[TASK_ID]", task.task_id)
            result = result.replace("[TASK_NAME]", task.task_name)
            result = result.replace("[TASK_DESCRIPTION]", task.description)
            result = result.replace("[ESTIMATED_TIME]", task.estimated_time)

            # Add phase context if available
            if phase_data:
                result = result.replace("[PHASE_NUMBER]", str(phase_data.phase_number))
                result = result.replace("[PHASE_NAME]", phase_data.phase_name)

            # Format dependencies
            deps_formatted = (
                ", ".join(task.dependencies) if task.dependencies else "None"
            )
            result = result.replace("[DEPENDENCIES]", deps_formatted)

            # Format acceptance criteria
            criteria_formatted = "\n".join(
                f"- [ ] {criterion}" for criterion in task.acceptance_criteria
            )
            result = result.replace("[ACCEPTANCE_CRITERIA]", criteria_formatted)

            # Calculate next task number (parse from task_id)
            try:
                task_num = int(task.task_id.split(".")[-1])
                result = result.replace("[NEXT_TASK_NUMBER]", str(task_num + 1))
            except (ValueError, IndexError):
                result = result.replace("[NEXT_TASK_NUMBER]", "?")

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (without render cache)."""
        return {
            "source_path": self.source_path,
            "workflow_type": self.workflow_type,
            "phase_template": self.phase_template,
            "task_template": self.task_template,
            "phases": [phase.to_dict() for phase in self.phases],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DynamicWorkflowContent":
        """Deserialize from dictionary."""
        return cls(
            source_path=data["source_path"],
            workflow_type=data["workflow_type"],
            phase_template=data["phase_template"],
            task_template=data["task_template"],
            phases=[DynamicPhase.from_dict(p) for p in data["phases"]],
        )


__all__ = [
    "CheckpointStatus",
    "CommandExecution",
    "PhaseArtifact",
    "WorkflowState",
    "CheckpointCriteria",
    "PhaseMetadata",
    "WorkflowMetadata",
    "WorkflowConfig",
    "DynamicTask",
    "DynamicPhase",
    "DynamicWorkflowContent",
]

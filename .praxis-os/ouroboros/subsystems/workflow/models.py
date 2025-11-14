"""
Workflow Subsystem Models.

Immutable Pydantic v2 models for workflow state and metadata.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class CheckpointStatus(str, Enum):
    """Checkpoint validation status."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class PhaseTimingInfo(BaseModel):
    """Timing information for a single phase."""

    model_config = {"frozen": True, "extra": "forbid"}

    phase: int = Field(..., ge=0, description="Phase number")
    started_at: datetime = Field(..., description="When phase execution started")
    completed_at: Optional[datetime] = Field(None, description="When phase was completed (None if in progress)")
    duration_seconds: Optional[float] = Field(None, description="Phase duration in seconds (calculated)")

    @property
    def duration(self) -> Optional[float]:
        """Calculate duration in seconds if phase is complete."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class PhaseArtifact(BaseModel):
    """Artifact produced by a phase (e.g., generated tests, spec document)."""

    model_config = {"frozen": True, "extra": "forbid"}

    phase: int = Field(..., ge=0, description="Phase number that produced this artifact")
    artifact_type: str = Field(..., min_length=1, description="Type of artifact (e.g., 'tests', 'spec')")
    file_path: str = Field(..., min_length=1, description="Path to artifact file")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional artifact metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="When artifact was created")


class WorkflowState(BaseModel):
    """
    Immutable workflow state.

    Enforces phase gating - only current phase is accessible.
    State is passed to workflow subsystem, never mutated in place.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    session_id: str = Field(..., min_length=1, description="Unique session identifier")
    workflow_type: str = Field(..., min_length=1, description="Workflow type (e.g., 'spec_execution_v1')")
    target_file: str = Field(..., min_length=1, description="Target file being worked on")
    current_phase: int = Field(..., ge=0, description="Current phase number")
    completed_phases: List[int] = Field(default_factory=list, description="Phases completed")
    phase_artifacts: Dict[int, PhaseArtifact] = Field(default_factory=dict, description="Artifacts from each phase")
    checkpoints: Dict[int, CheckpointStatus] = Field(default_factory=dict, description="Checkpoint status per phase")
    evidence_submitted: Dict[int, Dict[str, Any]] = Field(
        default_factory=dict, description="Evidence submitted for each phase"
    )
    phase_timings: Dict[int, PhaseTimingInfo] = Field(
        default_factory=dict, description="Timing information for each phase"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="Session start time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    completed_at: Optional[datetime] = Field(None, description="When workflow was marked complete")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session metadata")

    def with_phase_completed(
        self, phase: int, evidence: Dict[str, Any], checkpoint_status: CheckpointStatus
    ) -> "WorkflowState":
        """
        Return new state with phase completed.

        This is the ONLY way to advance phases (immutable pattern).
        """
        now = datetime.now()
        
        # Calculate new completed phases
        new_completed = list(self.completed_phases)
        if phase not in new_completed:
            new_completed.append(phase)
            new_completed.sort()

        # Calculate new current phase
        new_current = phase + 1

        # Build new checkpoints dict
        new_checkpoints = dict(self.checkpoints)
        new_checkpoints[phase] = checkpoint_status

        # Build new evidence dict
        new_evidence = dict(self.evidence_submitted)
        new_evidence[phase] = evidence

        # Update phase timing - mark phase as completed
        new_timings = dict(self.phase_timings)
        if phase in new_timings:
            # Phase was already started, mark it complete
            timing = new_timings[phase]
            duration = (now - timing.started_at).total_seconds()
            new_timings[phase] = PhaseTimingInfo(
                phase=phase,
                started_at=timing.started_at,
                completed_at=now,
                duration_seconds=duration
            )
        
        # Start timing for next phase
        new_timings[new_current] = PhaseTimingInfo(
            phase=new_current,
            started_at=now,
            completed_at=None,
            duration_seconds=None
        )

        # Return new state (immutable)
        return self.model_copy(
            update={
                "current_phase": new_current,
                "completed_phases": new_completed,
                "checkpoints": new_checkpoints,
                "evidence_submitted": new_evidence,
                "phase_timings": new_timings,
                "updated_at": now,
            }
        )

    def with_artifact(self, artifact: PhaseArtifact) -> "WorkflowState":
        """Return new state with artifact added."""
        new_artifacts = dict(self.phase_artifacts)
        new_artifacts[artifact.phase] = artifact

        return self.model_copy(update={"phase_artifacts": new_artifacts, "updated_at": datetime.now()})


class WorkflowMetadata(BaseModel):
    """Workflow metadata loaded from workflow definition."""

    model_config = {"frozen": True, "extra": "allow"}  # Allow extra fields for forward compatibility

    # Required core fields
    workflow_type: str = Field(..., min_length=1, description="Workflow type identifier")
    version: str = Field(..., min_length=1, description="Workflow version")
    description: str = Field(..., min_length=1, description="Workflow description")
    
    # Optional descriptive fields
    name: Optional[str] = Field(None, description="Human-readable workflow name")
    author: Optional[str] = Field(None, description="Workflow author")
    
    # Phase configuration
    total_phases: Union[int, str] = Field("dynamic", description="Total phases (int or 'dynamic')")
    max_phase: int = Field(0, ge=0, description="Maximum phase number (for static workflows)")
    start_phase: int = Field(0, description="Starting phase number")
    
    # Dynamic workflow configuration
    dynamic_phases: bool = Field(False, description="Whether workflow has dynamic phases")
    dynamic_config: Optional[Dict[str, Any]] = Field(None, description="Dynamic workflow configuration")
    
    # Workflow invocation requirements
    required_options: List[str] = Field(default_factory=list, description="Required options for start_workflow()")
    
    # Metadata and quality
    strict_mode: bool = Field(True, description="Whether strict validation is enabled")
    estimated_duration: Optional[str] = Field(None, description="Estimated completion time")
    primary_outputs: List[str] = Field(default_factory=list, description="Expected deliverables")
    target_language: List[str] = Field(default_factory=list, description="Target programming languages")
    quality_gates: Optional[Dict[str, Any]] = Field(None, description="Quality gate definitions")
    quality_standards: Optional[Dict[str, Any]] = Field(None, description="Quality standards")
    
    # Phases (if static)
    phases: List[Dict[str, Any]] = Field(default_factory=list, description="Phase definitions")
    
    # Timestamps
    created: Optional[str] = Field(None, description="Creation date")
    updated: Optional[str] = Field(None, description="Last update date")

    def model_post_init(self, __context: Any) -> None:
        """
        Calculate max_phase after initialization if not explicitly set.
        
        For static workflows: max_phase = highest phase_number in phases array
        For dynamic workflows: max_phase stays 0 until runtime calculation
        
        BUG FIX: Prevents premature workflow completion when max_phase defaults to 0.
        Previously: current_phase (3) > max_phase (0) = True (marks complete incorrectly)
        Now: current_phase (3) > max_phase (5) = False (correct for 6-phase workflow)
        """
        # Only calculate if max_phase is still default (0) and workflow is static
        if self.max_phase == 0 and not self.dynamic_phases and self.phases:
            # Calculate from phases array (find highest phase_number)
            phase_numbers = [p.get("phase_number", 0) for p in self.phases if isinstance(p, dict)]
            if phase_numbers:
                calculated_max = max(phase_numbers)
                # Use object.__setattr__ since model is frozen
                object.__setattr__(self, "max_phase", calculated_max)


class DynamicTask(BaseModel):
    """
    Task structure parsed from external source (e.g., spec tasks.md).

    Represents a single task within a dynamic workflow phase with all metadata
    needed for template rendering and execution guidance.

    Used by dynamic workflows (spec_execution_v1, workflow_creation_v1) to parse
    task information from markdown or YAML sources.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    task_id: str = Field(..., min_length=1, description="Unique task identifier (e.g., '1.1', '2.3')")
    task_name: str = Field(..., min_length=1, description="Human-readable task name")
    description: str = Field(..., description="Detailed description of what needs to be done")
    estimated_time: str = Field(default="Variable", description="Estimated completion time")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this task depends on")
    acceptance_criteria: List[str] = Field(
        default_factory=list, description="List of criteria that must be met for completion"
    )


class DynamicPhase(BaseModel):
    """
    Phase structure parsed from external source (e.g., spec tasks.md).

    Represents a complete phase in a dynamic workflow including all tasks,
    metadata, and validation gates needed for execution.

    Used by dynamic workflows to adapt structure based on external specifications
    rather than static workflow definitions.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    phase_number: int = Field(..., ge=0, description="Sequential phase number (0, 1, 2, ...)")
    phase_name: str = Field(..., min_length=1, description="Human-readable phase name")
    description: str = Field(..., description="Phase goal or purpose")
    estimated_duration: str = Field(default="Variable", description="Estimated time to complete entire phase")
    tasks: List[DynamicTask] = Field(default_factory=list, description="List of tasks for this phase")
    validation_gate: List[str] = Field(
        default_factory=list, description="List of validation criteria that must pass before advancing"
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


class DynamicWorkflowContent:
    """
    Parsed and cached content for dynamic workflow session.
    
    Holds parsed phase/task data from spec's tasks.md file,
    loaded templates, and caches rendered content.
    
    This is a RAM-only cache - content is derived from tasks.md
    and can be reconstructed anytime. NOT persisted to disk.
    
    Separate from WorkflowState (which tracks current phase, checkpoints).
    """
    
    def __init__(
        self,
        source_path: str,
        workflow_type: str,
        phase_template: str,
        task_template: str,
        phases: List[DynamicPhase],
    ):
        """Initialize dynamic workflow content."""
        self.source_path = source_path
        self.workflow_type = workflow_type
        self.phase_template = phase_template
        self.task_template = task_template
        self.phases = phases
        self._rendered_phases: Dict[int, str] = {}
        self._rendered_tasks: Dict[tuple, str] = {}
    
    def render_phase(self, phase: int) -> str:
        """
        Render phase template with phase data (cached).
        
        Args:
            phase: Phase number
            
        Returns:
            Rendered phase content
            
        Raises:
            IndexError: If phase not found
        """
        if phase not in self._rendered_phases:
            phase_data = next((p for p in self.phases if p.phase_number == phase), None)
            if not phase_data:
                raise IndexError(f"Phase {phase} not found")
            
            self._rendered_phases[phase] = self._render_template(
                self.phase_template, phase_data
            )
        return self._rendered_phases[phase]
    
    def render_task(self, phase: int, task_number: int) -> str:
        """
        Render task template with task data (cached).
        
        Args:
            phase: Phase number
            task_number: Task number (1-indexed)
            
        Returns:
            Rendered task content
            
        Raises:
            IndexError: If phase or task not found
        """
        cache_key = (phase, task_number)
        if cache_key not in self._rendered_tasks:
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
        Simple placeholder replacement: [PLACEHOLDER] → value.
        
        Args:
            template: Template string with [PLACEHOLDER] markers
            task_or_phase_data: DynamicTask or DynamicPhase
            phase_data: Optional phase context for task rendering
            
        Returns:
            Rendered template
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
            
            # Format validation gate
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
            
            # Add phase context
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
            
            # Calculate next task number
            try:
                task_num = int(task.task_id.split(".")[-1])
                result = result.replace("[NEXT_TASK_NUMBER]", str(task_num + 1))
            except (ValueError, IndexError):
                result = result.replace("[NEXT_TASK_NUMBER]", "?")
        
        return result


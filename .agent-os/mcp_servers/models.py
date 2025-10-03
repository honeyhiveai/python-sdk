"""
Data Models for Agent OS MCP/RAG System.

All workflow state, artifacts, and data structures.
100% AI-authored via human orchestration.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


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


# Export document chunk models from chunker for consistency
# (These are already defined in chunker.py, re-export here for convenience)
from .chunker import DocumentChunk, ChunkMetadata  # noqa: E402

__all__ = [
    "CheckpointStatus",
    "CommandExecution",
    "PhaseArtifact",
    "WorkflowState",
    "CheckpointCriteria",
    "WorkflowConfig",
    "DocumentChunk",  # Re-exported from chunker
    "ChunkMetadata",  # Re-exported from chunker
]


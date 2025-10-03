"""
Unit tests for Data Models.

Tests serialization, deserialization, and validation logic.
100% AI-authored via human orchestration.
"""

# Import from .agent-os package
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / ".agent-os"))

# pylint: disable=wrong-import-position
from mcp_servers.models import (
    CheckpointCriteria,
    CheckpointStatus,
    CommandExecution,
    PhaseArtifact,
    WorkflowConfig,
    WorkflowState,
)


class TestCommandExecution:
    """Test CommandExecution model."""

    def test_create_command_execution(self):
        """Test creating command execution."""
        now = datetime.now()
        cmd = CommandExecution(
            command="grep -rn 'def'",
            output="line 1: def func()\nline 2: def another()",
            exit_code=0,
            executed_at=now,
            duration_ms=150.5,
        )

        assert cmd.command == "grep -rn 'def'"
        assert cmd.exit_code == 0
        assert cmd.duration_ms == 150.5

    def test_command_execution_to_dict(self):
        """Test serialization to dict."""
        now = datetime.now()
        cmd = CommandExecution(
            command="test command",
            output="output",
            exit_code=0,
            executed_at=now,
            duration_ms=100.0,
        )

        data = cmd.to_dict()

        assert data["command"] == "test command"
        assert data["exit_code"] == 0
        assert "executed_at" in data

    def test_command_execution_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "command": "test command",
            "output": "output",
            "exit_code": 0,
            "executed_at": datetime.now().isoformat(),
            "duration_ms": 100.0,
        }

        cmd = CommandExecution.from_dict(data)

        assert cmd.command == "test command"
        assert cmd.exit_code == 0
        assert isinstance(cmd.executed_at, datetime)


class TestPhaseArtifact:
    """Test PhaseArtifact model."""

    def test_create_phase_artifact(self):
        """Test creating phase artifact."""
        now = datetime.now()
        artifact = PhaseArtifact(
            phase_number=1,
            evidence={"function_count": 10, "method_count": 5},
            outputs={"functions": ["func1", "func2"]},
            commands_executed=[],
            timestamp=now,
        )

        assert artifact.phase_number == 1
        assert artifact.evidence["function_count"] == 10
        assert len(artifact.outputs["functions"]) == 2

    def test_phase_artifact_to_dict(self):
        """Test serialization."""
        now = datetime.now()
        artifact = PhaseArtifact(
            phase_number=1,
            evidence={"count": 5},
            outputs={"data": "test"},
            commands_executed=[],
            timestamp=now,
        )

        data = artifact.to_dict()

        assert data["phase_number"] == 1
        assert data["evidence"]["count"] == 5
        assert "timestamp" in data

    def test_phase_artifact_from_dict(self):
        """Test deserialization."""
        data = {
            "phase_number": 2,
            "evidence": {"test": "value"},
            "outputs": {"result": "data"},
            "commands_executed": [],
            "timestamp": datetime.now().isoformat(),
        }

        artifact = PhaseArtifact.from_dict(data)

        assert artifact.phase_number == 2
        assert artifact.evidence["test"] == "value"
        assert isinstance(artifact.timestamp, datetime)


class TestWorkflowState:
    """Test WorkflowState model."""

    def test_create_workflow_state(self):
        """Test creating workflow state."""
        now = datetime.now()
        state = WorkflowState(
            session_id="test-session",
            workflow_type="test_generation_v3",
            target_file="test.py",
            current_phase=1,
            completed_phases=[],
            phase_artifacts={},
            checkpoints={},
            created_at=now,
            updated_at=now,
        )

        assert state.session_id == "test-session"
        assert state.current_phase == 1
        assert len(state.completed_phases) == 0

    def test_can_access_phase(self):
        """Test phase access control."""
        now = datetime.now()
        state = WorkflowState(
            session_id="test",
            workflow_type="test_generation_v3",
            target_file="test.py",
            current_phase=2,
            completed_phases=[1],
            phase_artifacts={},
            checkpoints={},
            created_at=now,
            updated_at=now,
        )

        # Can access current phase
        assert state.can_access_phase(2) is True

        # Can access completed phases
        assert state.can_access_phase(1) is True

        # Cannot access future phases
        assert state.can_access_phase(3) is False

    def test_complete_phase_success(self):
        """Test completing a phase successfully."""
        now = datetime.now()
        state = WorkflowState(
            session_id="test",
            workflow_type="test_generation_v3",
            target_file="test.py",
            current_phase=1,
            completed_phases=[],
            phase_artifacts={},
            checkpoints={},
            created_at=now,
            updated_at=now,
        )

        artifact = PhaseArtifact(
            phase_number=1,
            evidence={"count": 10},
            outputs={},
            commands_executed=[],
            timestamp=now,
        )

        state.complete_phase(1, artifact, checkpoint_passed=True)

        # Should advance to next phase
        assert state.current_phase == 2
        assert 1 in state.completed_phases
        assert state.checkpoints[1] == CheckpointStatus.PASSED
        assert state.phase_artifacts[1] == artifact

    def test_complete_phase_wrong_phase(self):
        """Test completing wrong phase raises error."""
        now = datetime.now()
        state = WorkflowState(
            session_id="test",
            workflow_type="test_generation_v3",
            target_file="test.py",
            current_phase=1,
            completed_phases=[],
            phase_artifacts={},
            checkpoints={},
            created_at=now,
            updated_at=now,
        )

        artifact = PhaseArtifact(
            phase_number=2,
            evidence={},
            outputs={},
            commands_executed=[],
            timestamp=now,
        )

        with pytest.raises(ValueError, match="Cannot complete phase 2"):
            state.complete_phase(2, artifact)

    def test_complete_phase_checkpoint_failed(self):
        """Test completing phase with failed checkpoint."""
        now = datetime.now()
        state = WorkflowState(
            session_id="test",
            workflow_type="test_generation_v3",
            target_file="test.py",
            current_phase=1,
            completed_phases=[],
            phase_artifacts={},
            checkpoints={},
            created_at=now,
            updated_at=now,
        )

        artifact = PhaseArtifact(
            phase_number=1,
            evidence={},
            outputs={},
            commands_executed=[],
            timestamp=now,
        )

        state.complete_phase(1, artifact, checkpoint_passed=False)

        # Should NOT advance
        assert state.current_phase == 1
        assert 1 not in state.completed_phases
        assert state.checkpoints[1] == CheckpointStatus.FAILED

    def test_get_artifact(self):
        """Test retrieving phase artifact."""
        now = datetime.now()
        artifact = PhaseArtifact(
            phase_number=1,
            evidence={"count": 5},
            outputs={},
            commands_executed=[],
            timestamp=now,
        )

        state = WorkflowState(
            session_id="test",
            workflow_type="test_generation_v3",
            target_file="test.py",
            current_phase=2,
            completed_phases=[1],
            phase_artifacts={1: artifact},
            checkpoints={},
            created_at=now,
            updated_at=now,
        )

        retrieved = state.get_artifact(1)
        assert retrieved is not None
        assert retrieved.phase_number == 1

        # Non-existent artifact
        assert state.get_artifact(3) is None

    def test_is_complete(self):
        """Test workflow completion check."""
        now = datetime.now()

        # Not complete
        state = WorkflowState(
            session_id="test",
            workflow_type="test_generation_v3",
            target_file="test.py",
            current_phase=5,
            completed_phases=[1, 2, 3, 4],
            phase_artifacts={},
            checkpoints={},
            created_at=now,
            updated_at=now,
        )
        assert not state.is_complete()

        # Complete (phase > 8)
        state.current_phase = 9
        assert state.is_complete()

    def test_workflow_state_to_dict(self):
        """Test serialization."""
        now = datetime.now()
        state = WorkflowState(
            session_id="test",
            workflow_type="test_generation_v3",
            target_file="test.py",
            current_phase=1,
            completed_phases=[],
            phase_artifacts={},
            checkpoints={},
            created_at=now,
            updated_at=now,
        )

        data = state.to_dict()

        assert data["session_id"] == "test"
        assert data["current_phase"] == 1
        assert "created_at" in data

    def test_workflow_state_from_dict(self):
        """Test deserialization."""
        now = datetime.now()
        data = {
            "session_id": "test",
            "workflow_type": "test_generation_v3",
            "target_file": "test.py",
            "current_phase": 1,
            "completed_phases": [],
            "phase_artifacts": {},
            "checkpoints": {},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "metadata": {},
        }

        state = WorkflowState.from_dict(data)

        assert state.session_id == "test"
        assert state.current_phase == 1
        assert isinstance(state.created_at, datetime)


class TestCheckpointCriteria:
    """Test CheckpointCriteria model."""

    def test_create_checkpoint_criteria(self):
        """Test creating checkpoint criteria."""
        criteria = CheckpointCriteria(
            phase_number=1,
            required_evidence={"function_count": "int", "method_count": "int"},
            validators={"function_count": lambda x: x > 0},
            description="Phase 1 checkpoint",
        )

        assert criteria.phase_number == 1
        assert "function_count" in criteria.required_evidence

    def test_validate_success(self):
        """Test successful validation."""
        criteria = CheckpointCriteria(
            phase_number=1,
            required_evidence={"count": "int"},
            validators={"count": lambda x: x > 0},
            description="Test",
        )

        evidence = {"count": 10}
        passed, missing = criteria.validate(evidence)

        assert passed is True
        assert len(missing) == 0

    def test_validate_missing_field(self):
        """Test validation with missing field."""
        criteria = CheckpointCriteria(
            phase_number=1,
            required_evidence={"count": "int", "name": "str"},
            validators={},
            description="Test",
        )

        evidence = {"count": 10}  # Missing 'name'
        passed, missing = criteria.validate(evidence)

        assert passed is False
        assert "name" in missing

    def test_validate_wrong_type(self):
        """Test validation with wrong type."""
        criteria = CheckpointCriteria(
            phase_number=1,
            required_evidence={"count": "int"},
            validators={},
            description="Test",
        )

        evidence = {"count": "not_an_int"}
        passed, missing = criteria.validate(evidence)

        assert passed is False
        assert any("count" in field for field in missing)

    def test_validate_custom_validator_fails(self):
        """Test validation with failing custom validator."""
        criteria = CheckpointCriteria(
            phase_number=1,
            required_evidence={"count": "int"},
            validators={"count": lambda x: x > 10},  # Must be > 10
            description="Test",
        )

        evidence = {"count": 5}  # Fails validator
        passed, missing = criteria.validate(evidence)

        assert passed is False
        assert any("count" in field for field in missing)


class TestWorkflowConfig:
    """Test WorkflowConfig model."""

    def test_create_workflow_config(self):
        """Test creating workflow config."""
        config = WorkflowConfig(
            workflow_type="test_generation_v3",
            total_phases=8,
            phase_names=["Phase 1", "Phase 2", "Phase 3"],
        )

        assert config.workflow_type == "test_generation_v3"
        assert config.total_phases == 8
        assert config.strict_gating is True  # Default

    def test_workflow_config_to_dict(self):
        """Test serialization."""
        config = WorkflowConfig(
            workflow_type="test_generation_v3",
            total_phases=8,
            phase_names=["Phase 1"],
        )

        data = config.to_dict()

        assert data["workflow_type"] == "test_generation_v3"
        assert data["total_phases"] == 8

    def test_workflow_config_from_dict(self):
        """Test deserialization."""
        data = {
            "workflow_type": "test_generation_v3",
            "total_phases": 8,
            "phase_names": ["Phase 1"],
            "strict_gating": True,
            "allow_phase_skip": False,
            "checkpoint_required": True,
            "auto_save": True,
        }

        config = WorkflowConfig.from_dict(data)

        assert config.workflow_type == "test_generation_v3"
        assert config.total_phases == 8


# Test coverage target: 60%+ per project requirements
# This test suite provides comprehensive coverage of:
# - Model creation
# - Serialization/deserialization
# - Validation logic
# - Phase gating enforcement
# - Checkpoint validation
# - State management

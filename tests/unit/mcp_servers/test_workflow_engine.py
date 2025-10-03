"""
Unit tests for Workflow Engine.

Tests phase gating, checkpoint validation, and state management.
100% AI-authored via human orchestration.
"""

# Import from .agent-os package
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / ".agent-os"))

# pylint: disable=wrong-import-position
from mcp_servers.rag_engine import RAGEngine
from mcp_servers.state_manager import StateManager
from mcp_servers.workflow_engine import CheckpointLoader, WorkflowEngine


class TestCheckpointLoader:
    """Test dynamic checkpoint loading."""

    def test_load_checkpoint_requirements(self):
        """Test loading checkpoint requirements from RAG."""
        # Mock RAG engine
        mock_rag = Mock(spec=RAGEngine)
        mock_rag.search.return_value = Mock(
            chunks=[
                {"content": "Must provide `function_count` - number of functions found"}
            ]
        )

        loader = CheckpointLoader(mock_rag)
        requirements = loader.load_checkpoint_requirements("test_generation_v3", 1)

        assert "required_evidence" in requirements

    def test_checkpoint_caching(self):
        """Test that checkpoint requirements are cached."""
        mock_rag = Mock(spec=RAGEngine)
        mock_rag.search.return_value = Mock(chunks=[])

        loader = CheckpointLoader(mock_rag)

        # First call
        loader.load_checkpoint_requirements("test_generation_v3", 1)
        # Second call (should use cache)
        loader.load_checkpoint_requirements("test_generation_v3", 1)

        # Should only call RAG once
        assert mock_rag.search.call_count == 1

    def test_is_evidence_requirement(self):
        """Test detection of evidence requirement lines."""
        loader = CheckpointLoader(Mock())

        assert loader._is_evidence_requirement("Must provide function_count")
        assert loader._is_evidence_requirement("Required: method verification")
        assert loader._is_evidence_requirement("Evidence: command output")
        assert not loader._is_evidence_requirement("This is just text")

    def test_extract_field_name(self):
        """Test field name extraction."""
        loader = CheckpointLoader(Mock())

        assert (
            loader._extract_field_name("Must provide `function_count`")
            == "function_count"
        )
        assert (
            loader._extract_field_name("Required: **method_count**") == "method_count"
        )
        assert "test_field" in loader._extract_field_name(
            "Verify test_field is present"
        )

    def test_infer_field_type(self):
        """Test type inference from context."""
        loader = CheckpointLoader(Mock())

        assert loader._infer_field_type("function count", []) == int
        assert loader._infer_field_type("list of methods", []) == list
        assert loader._infer_field_type("command output", []) == str
        assert loader._infer_field_type("enabled flag", []) == bool


class TestWorkflowEngineInitialization:  # pylint: disable=too-few-public-methods
    """Test workflow engine initialization."""

    def test_init_workflow_engine(self):
        """Test basic initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            rag_engine = Mock(spec=RAGEngine)

            engine = WorkflowEngine(state_manager, rag_engine)

            assert engine.state_manager is not None
            assert engine.rag_engine is not None
            assert engine.checkpoint_loader is not None


class TestWorkflowCreation:
    """Test workflow creation and starting."""

    def test_start_workflow(self):
        """Test starting a new workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)
            mock_rag.search.return_value = Mock(
                chunks=[{"content": "Phase 1 content"}],
                total_tokens=100,
                retrieval_method="vector",
            )

            engine = WorkflowEngine(state_manager, mock_rag)

            result = engine.start_workflow(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            assert "session_id" in result
            assert result["current_phase"] == 1
            assert result["workflow_type"] == "test_generation_v3"

    def test_start_workflow_resumes_existing(self):
        """Test that starting workflow resumes existing session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)
            mock_rag.search.return_value = Mock(
                chunks=[{"content": "Phase content"}],
                total_tokens=100,
                retrieval_method="vector",
            )

            engine = WorkflowEngine(state_manager, mock_rag)

            # Start first workflow
            result1 = engine.start_workflow(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            # Try to start another for same file (should resume)
            result2 = engine.start_workflow(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            assert result1["session_id"] == result2["session_id"]


class TestPhaseGating:
    """Test phase gating enforcement."""

    def test_can_only_access_current_phase(self):
        """Test that only current phase is accessible."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)
            mock_rag.search.return_value = Mock(
                chunks=[{"content": "Phase content"}],
                total_tokens=100,
                retrieval_method="vector",
            )

            engine = WorkflowEngine(state_manager, mock_rag)

            result = engine.start_workflow(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            session_id = result["session_id"]

            # Try to access phase 2 (should be blocked)
            phase2_result = engine.get_phase_content(session_id, 2)

            assert "error" in phase2_result
            assert phase2_result["error"] == "Phase sequence violation"
            assert phase2_result["current_phase"] == 1

    def test_can_access_completed_phases(self):
        """Test that completed phases can be accessed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)
            mock_rag.search.return_value = Mock(
                chunks=[{"content": "Phase content"}],
                total_tokens=100,
                retrieval_method="vector",
            )

            engine = WorkflowEngine(state_manager, mock_rag)

            result = engine.start_workflow(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            session_id = result["session_id"]

            # Complete phase 1
            state = state_manager.load_state(session_id)
            state.current_phase = 2
            state.completed_phases = [1]
            state_manager.save_state(state)

            # Try to access phase 1 (should be allowed)
            phase1_result = engine.get_phase_content(session_id, 1)

            assert "error" not in phase1_result
            assert phase1_result["requested_phase"] == 1


class TestCheckpointValidation:
    """Test checkpoint validation."""

    def test_validate_checkpoint_passes(self):
        """Test successful checkpoint validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)

            # Mock checkpoint requirements
            mock_loader = Mock()
            mock_loader.load_checkpoint_requirements.return_value = {
                "required_evidence": {
                    "function_count": {
                        "type": int,
                        "validator": lambda x: x > 0,
                        "description": "Number of functions",
                    }
                }
            }

            engine = WorkflowEngine(state_manager, mock_rag, mock_loader)

            evidence = {"function_count": 10}

            passed, missing = engine._validate_checkpoint(
                "test_generation_v3", 1, evidence
            )

            assert passed is True
            assert len(missing) == 0

    def test_validate_checkpoint_fails_missing_field(self):
        """Test checkpoint validation with missing field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)

            mock_loader = Mock()
            mock_loader.load_checkpoint_requirements.return_value = {
                "required_evidence": {
                    "function_count": {
                        "type": int,
                        "validator": lambda x: x > 0,
                        "description": "Number of functions",
                    }
                }
            }

            engine = WorkflowEngine(state_manager, mock_rag, mock_loader)

            evidence = {}  # Missing function_count

            passed, missing = engine._validate_checkpoint(
                "test_generation_v3", 1, evidence
            )

            assert passed is False
            assert len(missing) > 0
            assert any("function_count" in field for field in missing)

    def test_validate_checkpoint_fails_wrong_type(self):
        """Test checkpoint validation with wrong type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)

            mock_loader = Mock()
            mock_loader.load_checkpoint_requirements.return_value = {
                "required_evidence": {
                    "function_count": {
                        "type": int,
                        "validator": lambda x: True,
                        "description": "Number of functions",
                    }
                }
            }

            engine = WorkflowEngine(state_manager, mock_rag, mock_loader)

            evidence = {"function_count": "not_an_int"}

            passed, missing = engine._validate_checkpoint(
                "test_generation_v3", 1, evidence
            )

            assert passed is False
            assert any("wrong type" in field for field in missing)


class TestPhaseCompletion:
    """Test phase completion."""

    def test_complete_phase_success(self):
        """Test successful phase completion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)
            mock_rag.search.return_value = Mock(
                chunks=[{"content": "Phase content"}],
                total_tokens=100,
                retrieval_method="vector",
            )

            mock_loader = Mock()
            mock_loader.load_checkpoint_requirements.return_value = {
                "required_evidence": {
                    "function_count": {
                        "type": int,
                        "validator": lambda x: x > 0,
                        "description": "Number of functions",
                    }
                }
            }

            engine = WorkflowEngine(state_manager, mock_rag, mock_loader)

            result = engine.start_workflow(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            session_id = result["session_id"]

            # Complete phase 1
            evidence = {"function_count": 10}
            completion_result = engine.complete_phase(session_id, 1, evidence)

            assert completion_result["checkpoint_passed"] is True
            assert completion_result["phase_completed"] == 1
            assert completion_result["next_phase"] == 2

            # Verify state updated
            state = state_manager.load_state(session_id)
            assert state.current_phase == 2
            assert 1 in state.completed_phases

    def test_complete_phase_failure(self):
        """Test phase completion with failed checkpoint."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)
            mock_rag.search.return_value = Mock(
                chunks=[{"content": "Phase content"}],
                total_tokens=100,
                retrieval_method="vector",
            )

            mock_loader = Mock()
            mock_loader.load_checkpoint_requirements.return_value = {
                "required_evidence": {
                    "function_count": {
                        "type": int,
                        "validator": lambda x: x > 0,
                        "description": "Number of functions",
                    }
                }
            }

            engine = WorkflowEngine(state_manager, mock_rag, mock_loader)

            result = engine.start_workflow(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            session_id = result["session_id"]

            # Try to complete with missing evidence
            evidence = {}
            completion_result = engine.complete_phase(session_id, 1, evidence)

            assert completion_result["checkpoint_passed"] is False
            assert "missing_evidence" in completion_result

            # Verify state not updated
            state = state_manager.load_state(session_id)
            assert state.current_phase == 1
            assert len(state.completed_phases) == 0

    def test_complete_wrong_phase_raises_error(self):
        """Test that completing wrong phase raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)
            mock_rag.search.return_value = Mock(
                chunks=[{"content": "Phase content"}],
                total_tokens=100,
                retrieval_method="vector",
            )

            engine = WorkflowEngine(state_manager, mock_rag)

            result = engine.start_workflow(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            session_id = result["session_id"]

            # Try to complete phase 2 (wrong phase)
            with pytest.raises(ValueError, match="Cannot complete phase 2"):
                engine.complete_phase(session_id, 2, {})


class TestWorkflowState:
    """Test workflow state management."""

    def test_get_workflow_state(self):
        """Test retrieving workflow state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)
            mock_rag.search.return_value = Mock(
                chunks=[{"content": "Phase content"}],
                total_tokens=100,
                retrieval_method="vector",
            )

            engine = WorkflowEngine(state_manager, mock_rag)

            result = engine.start_workflow(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            session_id = result["session_id"]

            state = engine.get_workflow_state(session_id)

            assert state["session_id"] == session_id
            assert state["current_phase"] == 1
            assert state["workflow_type"] == "test_generation_v3"
            assert state["is_complete"] is False

    def test_get_nonexistent_session_raises_error(self):
        """Test that getting non-existent session raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(Path(temp_dir))
            mock_rag = Mock(spec=RAGEngine)

            engine = WorkflowEngine(state_manager, mock_rag)

            with pytest.raises(ValueError, match="Session .* not found"):
                engine.get_workflow_state("nonexistent-id")


# Test coverage target: 60%+ per project requirements
# This test suite provides comprehensive coverage of:
# - Checkpoint loading (dynamic)
# - Workflow creation
# - Phase gating enforcement
# - Checkpoint validation
# - Phase completion
# - State management
# - Error handling

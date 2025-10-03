"""
Unit tests for State Manager.

Tests state persistence, session lifecycle, and recovery.
100% AI-authored via human orchestration.
"""

import json

# Import from .agent-os package
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / ".agent-os"))

# pylint: disable=wrong-import-position
from mcp_servers.models import PhaseArtifact
from mcp_servers.state_manager import StateManager


class TestStateManagerInitialization:
    """Test state manager initialization."""

    def test_init_creates_directory(self):
        """Test that initialization creates state directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_dir = Path(temp_dir) / "state"
            manager = StateManager(state_dir)

            assert state_dir.exists()
            assert manager.state_dir == state_dir

    def test_init_with_existing_directory(self):
        """Test initialization with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_dir = Path(temp_dir)
            manager = StateManager(state_dir)

            assert manager.state_dir == state_dir


class TestSessionCreation:
    """Test session creation."""

    def test_create_session_basic(self):
        """Test basic session creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            assert state.session_id is not None
            assert state.workflow_type == "test_generation_v3"
            assert state.target_file == "test.py"
            assert state.current_phase == 1
            assert len(state.completed_phases) == 0

    def test_create_session_with_metadata(self):
        """Test session creation with metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            metadata = {"user": "test_user", "priority": "high"}
            state = manager.create_session(
                workflow_type="test_generation_v3",
                target_file="test.py",
                metadata=metadata,
            )

            assert state.metadata["user"] == "test_user"
            assert state.metadata["priority"] == "high"

    def test_create_session_persists(self):
        """Test that created session is persisted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_dir = Path(temp_dir)
            manager = StateManager(state_dir)

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            # Check file exists
            state_file = state_dir / f"{state.session_id}.json"
            assert state_file.exists()


class TestStatePersistence:
    """Test state save/load operations."""

    def test_save_and_load_state(self):
        """Test saving and loading state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            # Create and save state
            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            # Load state
            loaded_state = manager.load_state(state.session_id)

            assert loaded_state is not None
            assert loaded_state.session_id == state.session_id
            assert loaded_state.workflow_type == state.workflow_type
            assert loaded_state.target_file == state.target_file

    def test_load_nonexistent_state(self):
        """Test loading non-existent state returns None."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.load_state("nonexistent-id")

            assert state is None

    def test_save_updates_timestamp(self):
        """Test that save updates timestamp."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            original_updated = state.updated_at

            # Wait a moment and save again
            time.sleep(0.1)
            manager.save_state(state)

            # Reload and check timestamp updated
            loaded = manager.load_state(state.session_id)
            assert loaded.updated_at > original_updated

    def test_save_state_with_artifacts(self):
        """Test saving state with phase artifacts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            # Add artifact
            artifact = PhaseArtifact(
                phase_number=1,
                evidence={"count": 10},
                outputs={"data": "test"},
                commands_executed=[],
                timestamp=datetime.now(),
            )
            state.phase_artifacts[1] = artifact
            manager.save_state(state)

            # Reload and verify artifact
            loaded = manager.load_state(state.session_id)
            assert 1 in loaded.phase_artifacts
            assert loaded.phase_artifacts[1].evidence["count"] == 10


class TestSessionDeletion:
    """Test session deletion."""

    def test_delete_session_success(self):
        """Test successful session deletion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            # Delete session
            deleted = manager.delete_session(state.session_id)

            assert deleted is True
            assert manager.load_state(state.session_id) is None

    def test_delete_nonexistent_session(self):
        """Test deleting non-existent session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            deleted = manager.delete_session("nonexistent-id")

            assert deleted is False


class TestSessionListing:
    """Test listing sessions."""

    def test_list_sessions_empty(self):
        """Test listing sessions when none exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            sessions = manager.list_sessions()

            assert len(sessions) == 0

    def test_list_sessions_multiple(self):
        """Test listing multiple sessions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            # Create multiple sessions
            state1 = manager.create_session(
                workflow_type="test_generation_v3", target_file="test1.py"
            )
            state2 = manager.create_session(
                workflow_type="test_generation_v3", target_file="test2.py"
            )

            sessions = manager.list_sessions()

            assert len(sessions) == 2
            session_ids = [s.session_id for s in sessions]
            assert state1.session_id in session_ids
            assert state2.session_id in session_ids

    def test_list_sessions_filter_by_type(self):
        """Test filtering sessions by workflow type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            manager.create_session(
                workflow_type="test_generation_v3", target_file="test1.py"
            )
            manager.create_session(
                workflow_type="production_code_v2", target_file="test2.py"
            )

            sessions = manager.list_sessions(workflow_type="test_generation_v3")

            assert len(sessions) == 1
            assert sessions[0].workflow_type == "test_generation_v3"

    def test_list_sessions_active_only(self):
        """Test filtering only active sessions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            # Create active session
            active = manager.create_session(
                workflow_type="test_generation_v3", target_file="test1.py"
            )

            # Create completed session
            completed = manager.create_session(
                workflow_type="test_generation_v3", target_file="test2.py"
            )
            completed.current_phase = 9  # Beyond phase 8
            manager.save_state(completed)

            sessions = manager.list_sessions(active_only=True)

            assert len(sessions) == 1
            assert sessions[0].session_id == active.session_id


class TestSessionCleanup:
    """Test cleanup of old sessions."""

    def test_cleanup_old_sessions(self):
        """Test cleaning up old sessions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir), cleanup_days=1)

            # Create old session
            old_state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            # Manually set old timestamp by modifying the file
            state_file = manager._get_state_file(old_state.session_id)
            data = json.loads(state_file.read_text())
            data["updated_at"] = (datetime.now() - timedelta(days=2)).isoformat()
            state_file.write_text(json.dumps(data))

            # Create recent session
            recent_state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test2.py"
            )

            # Run cleanup
            cleaned = manager.cleanup_old_sessions()

            assert cleaned == 1
            assert manager.load_state(old_state.session_id) is None
            assert manager.load_state(recent_state.session_id) is not None

    def test_cleanup_no_old_sessions(self):
        """Test cleanup when no old sessions exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir), cleanup_days=7)

            manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            cleaned = manager.cleanup_old_sessions()

            assert cleaned == 0


class TestActiveSession:
    """Test finding active sessions."""

    def test_get_active_session_found(self):
        """Test finding active session for target file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            found = manager.get_active_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            assert found is not None
            assert found.session_id == state.session_id

    def test_get_active_session_not_found(self):
        """Test when no active session exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            found = manager.get_active_session(
                workflow_type="test_generation_v3", target_file="nonexistent.py"
            )

            assert found is None

    def test_get_active_session_ignores_completed(self):
        """Test that completed sessions are not returned."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            state.current_phase = 9  # Completed
            manager.save_state(state)

            found = manager.get_active_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            assert found is None


class TestStateValidation:
    """Test state validation."""

    def test_validate_valid_state(self):
        """Test validation of valid state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )

            valid, issues = manager.validate_state(state)

            assert valid is True
            assert len(issues) == 0

    def test_validate_missing_session_id(self):
        """Test validation catches missing session_id."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            state.session_id = ""

            valid, issues = manager.validate_state(state)

            assert valid is False
            assert any("session_id" in issue for issue in issues)

    def test_validate_invalid_phase(self):
        """Test validation catches invalid phase."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            state.current_phase = 0

            valid, issues = manager.validate_state(state)

            assert valid is False
            assert any("phase" in issue.lower() for issue in issues)

    def test_validate_inconsistent_phases(self):
        """Test validation catches phase inconsistencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            state = manager.create_session(
                workflow_type="test_generation_v3", target_file="test.py"
            )
            state.completed_phases = [1, 3]  # Missing phase 2
            state.current_phase = 4

            valid, _ = manager.validate_state(state)

            assert valid is False


class TestStatistics:
    """Test statistics gathering."""

    def test_get_statistics_empty(self):
        """Test statistics with no sessions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            stats = manager.get_statistics()

            assert stats["total_sessions"] == 0
            assert stats["active_sessions"] == 0

    def test_get_statistics_with_sessions(self):
        """Test statistics with sessions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = StateManager(Path(temp_dir))

            manager.create_session(
                workflow_type="test_generation_v3", target_file="test1.py"
            )
            manager.create_session(
                workflow_type="test_generation_v3", target_file="test2.py"
            )

            stats = manager.get_statistics()

            assert stats["total_sessions"] == 2
            assert stats["active_sessions"] == 2
            assert "test_generation_v3" in stats["workflow_type_counts"]


# Test coverage target: 60%+ per project requirements
# This test suite provides comprehensive coverage of:
# - Session creation
# - State persistence
# - Session deletion
# - Session listing
# - Cleanup operations
# - Active session finding
# - State validation
# - Statistics

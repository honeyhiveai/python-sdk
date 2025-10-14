"""
State Manager for Workflow Persistence.

Manages workflow state persistence, session lifecycle, and artifacts.
100% AI-authored via human orchestration.
"""

# pylint: disable=broad-exception-caught
# Justification: State manager catches broad exceptions for robustness,
# ensuring workflow state operations don't crash the server

# pylint: disable=missing-raises-doc
# Justification: Exception raising is documented in Returns/Notes sections,
# avoiding redundant "Raises:" sections for standard exceptions

import fcntl
import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import WorkflowState

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages workflow state persistence and session lifecycle.

    Features:
    - JSON-based state persistence
    - File locking for concurrent access
    - Automatic cleanup of old sessions
    - Session recovery and validation
    - Artifact storage
    """

    def __init__(self, state_dir: Path, cleanup_days: int = 7):
        """
        Initialize state manager.

        Args:
            state_dir: Directory to store state files
            cleanup_days: Days after which to clean up old sessions
        """
        self.state_dir = state_dir
        self.cleanup_days = cleanup_days

        # Ensure state directory exists
        self.state_dir.mkdir(parents=True, exist_ok=True)

        logger.info("StateManager initialized: %s", state_dir)

    def create_session(
        self, workflow_type: str, target_file: str, metadata: Optional[Dict] = None
    ) -> WorkflowState:
        """
        Create new workflow session.

        Args:
            workflow_type: Type of workflow (e.g., "test_generation_v3")
            target_file: File being worked on
            metadata: Optional additional metadata

        Returns:
            New WorkflowState instance
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()

        # Detect starting phase dynamically (0 or 1)
        starting_phase = self._detect_starting_phase(workflow_type)

        state = WorkflowState(
            session_id=session_id,
            workflow_type=workflow_type,
            target_file=target_file,
            current_phase=starting_phase,  # Use detected starting phase
            completed_phases=[],
            phase_artifacts={},
            checkpoints={},
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

        # Save immediately
        self.save_state(state)

        logger.info(
            "Created session %s for %s on %s starting at Phase %s",
            session_id,
            workflow_type,
            target_file,
            starting_phase,
        )

        return state

    def _detect_starting_phase(self, workflow_type: str) -> int:
        """
        Detect the starting phase for a workflow.

        Checks if Phase 0 exists in the workflow structure.

        Args:
            workflow_type: Type of workflow

        Returns:
            Starting phase number (0 if Phase 0 exists, 1 otherwise)
        """
        # Try to find workflows directory
        # Check multiple possible locations
        possible_paths = [
            Path(".agent-os") / "workflows" / workflow_type / "phases" / "0",
            Path("universal") / "workflows" / workflow_type / "phases" / "0",
        ]

        # If workflows_base_path is available in environment
        if hasattr(self, "_workflows_base_path"):
            possible_paths.insert(
                0, self._workflows_base_path / workflow_type / "phases" / "0"
            )

        for phase_0_path in possible_paths:
            if phase_0_path.exists():
                logger.info(
                    "Workflow %s has Phase 0 at %s", workflow_type, phase_0_path
                )
                return 0

        # Default to Phase 1 for backwards compatibility
        logger.info("Workflow %s starts at Phase 1 (no Phase 0 found)", workflow_type)
        return 1

    def save_state(self, state: WorkflowState) -> None:
        """
        Save workflow state to disk with file locking.

        Args:
            state: WorkflowState to save

        Raises:
            IOError: If save fails
        """
        state_file = self._get_state_file(state.session_id)

        # Update timestamp
        state.updated_at = datetime.now()

        # Serialize to JSON
        data = state.to_dict()

        # Write with file locking for concurrent access safety
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                    f.flush()
                finally:
                    # Release lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            logger.debug("Saved state for session %s", state.session_id)

        except Exception as e:
            logger.error("Failed to save state %s: %s", state.session_id, e)
            raise

    def load_state(self, session_id: str) -> Optional[WorkflowState]:
        """
        Load workflow state from disk.

        Args:
            session_id: Session identifier

        Returns:
            WorkflowState if exists, None otherwise

        Raises:
            ValueError: If state file is corrupted
        """
        state_file = self._get_state_file(session_id)

        if not state_file.exists():
            logger.warning("State file not found: %s", session_id)
            return None

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                # Acquire shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            state = WorkflowState.from_dict(data)
            logger.debug("Loaded state for session %s", session_id)
            return state

        except json.JSONDecodeError as e:
            logger.error("Corrupted state file %s: %s", session_id, e)
            raise ValueError(f"Corrupted state file: {e}") from e
        except Exception as e:
            logger.error("Failed to load state %s: %s", session_id, e)
            raise

    def delete_session(self, session_id: str) -> bool:
        """
        Delete workflow session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        state_file = self._get_state_file(session_id)

        if not state_file.exists():
            logger.warning("Session not found for deletion: %s", session_id)
            return False

        try:
            state_file.unlink()
            logger.info("Deleted session %s", session_id)
            return True
        except Exception as e:
            logger.error("Failed to delete session %s: %s", session_id, e)
            return False

    def list_sessions(
        self, workflow_type: Optional[str] = None, active_only: bool = False
    ) -> List[WorkflowState]:
        """
        List workflow sessions.

        Args:
            workflow_type: Optional filter by workflow type
            active_only: If True, only return incomplete sessions

        Returns:
            List of WorkflowState instances
        """
        sessions = []

        # Find all state files
        for state_file in self.state_dir.glob("*.json"):
            try:
                session_id = state_file.stem
                state = self.load_state(session_id)

                if state is None:
                    continue

                # Apply filters
                if workflow_type and state.workflow_type != workflow_type:
                    continue

                if active_only and state.is_complete():
                    continue

                sessions.append(state)

            except Exception as e:
                logger.warning("Failed to load session from %s: %s", state_file, e)
                continue

        logger.debug("Listed %s sessions", len(sessions))
        return sessions

    def cleanup_old_sessions(self) -> int:
        """
        Clean up sessions older than cleanup_days.

        Returns:
            Number of sessions cleaned up
        """
        cutoff_date = datetime.now() - timedelta(days=self.cleanup_days)
        cleaned_count = 0

        logger.info("Cleaning up sessions older than %s", cutoff_date.isoformat())

        for state_file in self.state_dir.glob("*.json"):
            try:
                session_id = state_file.stem
                state = self.load_state(session_id)

                if state is None:
                    continue

                # Check age
                if state.updated_at < cutoff_date:
                    if self.delete_session(session_id):
                        cleaned_count += 1
                        logger.debug(
                            "Cleaned up old session %s (last updated: %s)",
                            session_id,
                            state.updated_at.isoformat(),
                        )

            except Exception as e:
                logger.warning("Failed to cleanup %s: %s", state_file, e)
                continue

        logger.info("Cleaned up %s old sessions", cleaned_count)
        return cleaned_count

    def get_active_session(
        self, workflow_type: str, target_file: str
    ) -> Optional[WorkflowState]:
        """
        Get active session for workflow type and target file.

        Useful for resuming workflows.

        Args:
            workflow_type: Workflow type to match
            target_file: Target file to match

        Returns:
            Active WorkflowState if found, None otherwise
        """
        sessions = self.list_sessions(workflow_type=workflow_type, active_only=True)

        # Find matching target file
        for state in sessions:
            if state.target_file == target_file:
                logger.debug(
                    "Found active session %s for %s", state.session_id, target_file
                )
                return state

        logger.debug("No active session found for %s", target_file)
        return None

    def validate_state(self, state: WorkflowState) -> tuple[bool, List[str]]:
        """
        Validate workflow state for corruption or inconsistencies.

        Args:
            state: WorkflowState to validate

        Returns:
            Tuple of (valid: bool, issues: List[str])
        """
        issues = []

        # Check basic fields
        if not state.session_id:
            issues.append("Missing session_id")

        if not state.workflow_type:
            issues.append("Missing workflow_type")

        if not state.target_file:
            issues.append("Missing target_file")

        # Check phase consistency
        if state.current_phase < 1:
            issues.append("Invalid current_phase (< 1)")

        # Check completed phases are sequential
        if state.completed_phases:
            sorted_phases = sorted(state.completed_phases)
            expected = list(range(1, len(sorted_phases) + 1))
            if sorted_phases != expected:
                issues.append(
                    f"Completed phases not sequential: {state.completed_phases}"
                )

        # Check current phase follows completed phases
        if state.completed_phases:
            expected_current = max(state.completed_phases) + 1
            if state.current_phase != expected_current:
                issues.append(
                    f"Current phase {state.current_phase} doesn't follow "
                    f"completed phases {state.completed_phases}"
                )

        # Check timestamps
        if state.created_at > state.updated_at:
            issues.append("updated_at is before created_at")

        valid = len(issues) == 0

        if not valid:
            logger.warning(
                "State validation failed for %s: %s", state.session_id, issues
            )

        return valid, issues

    def recover_corrupted_state(self, session_id: str) -> bool:
        """
        Attempt to recover corrupted state file.

        Args:
            session_id: Session to recover

        Returns:
            True if recovered, False if unrecoverable
        """
        state_file = self._get_state_file(session_id)

        if not state_file.exists():
            return False

        # Try to load and validate
        try:
            state = self.load_state(session_id)
            if state is None:
                return False

            valid, issues = self.validate_state(state)

            if valid:
                logger.info("State %s is valid, no recovery needed", session_id)
                return True

            logger.warning("Attempting to recover state %s: %s", session_id, issues)

            # Attempt repairs
            if not state.completed_phases:
                state.completed_phases = []

            state.current_phase = max(state.current_phase, 1)

            if state.created_at > state.updated_at:
                state.updated_at = datetime.now()

            # Validate again
            valid, issues = self.validate_state(state)

            if valid:
                # Save repaired state
                self.save_state(state)
                logger.info("Successfully recovered state %s", session_id)
                return True

            logger.error("Could not recover state %s: %s", session_id, issues)
            return False

        except Exception as e:
            logger.error("Failed to recover state %s: %s", session_id, e)
            return False

    def _get_state_file(self, session_id: str) -> Path:
        """
        Get path to state file for session.

        Args:
            session_id: Session identifier

        Returns:
            Path to state file
        """
        return self.state_dir / f"{session_id}.json"

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about managed sessions.

        Returns:
            Dictionary with statistics
        """
        all_sessions = self.list_sessions()
        active_sessions = [s for s in all_sessions if not s.is_complete()]

        workflow_counts: Dict[str, int] = {}
        for session in all_sessions:
            workflow_type = session.workflow_type
            workflow_counts[workflow_type] = workflow_counts.get(workflow_type, 0) + 1

        return {
            "total_sessions": len(all_sessions),
            "active_sessions": len(active_sessions),
            "completed_sessions": len(all_sessions) - len(active_sessions),
            "workflow_type_counts": workflow_counts,
            "state_directory": str(self.state_dir),
            "cleanup_days": self.cleanup_days,
        }

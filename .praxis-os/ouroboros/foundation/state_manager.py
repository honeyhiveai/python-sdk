"""
State Manager: Workflow state persistence.

Low-level persistence layer for workflow state.
Uses JSON files with atomic writes and file locking.

Architecture:
- Foundation layer (no workflow logic)
- Serializes/deserializes WorkflowState to/from JSON
- Atomic writes with file locking (fcntl)
- Session listing and cleanup
"""

import fcntl
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ouroboros.subsystems.workflow.models import WorkflowState
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class StateManagerError(ActionableError):
    """State manager operation failed."""

    pass


class StateManager:
    """
    Manages workflow state persistence.

    Features:
    - JSON-based state files (.praxis-os/workflow_states/{session_id}.json)
    - Atomic writes with file locking (fcntl)
    - Session listing and filtering
    - Automatic cleanup of old sessions
    """

    def __init__(self, state_dir: Path, cleanup_days: int = 30):
        """
        Initialize state manager.

        Args:
            state_dir: Directory to store state files
            cleanup_days: Days after which to clean up completed sessions
        """
        self.state_dir = state_dir
        self.cleanup_days = cleanup_days

        # Ensure state directory exists
        self.state_dir.mkdir(parents=True, exist_ok=True)

        logger.info("StateManager initialized", extra={"state_dir": str(state_dir), "cleanup_days": cleanup_days})

    def save_state(self, state: WorkflowState) -> None:
        """
        Save workflow state to disk with atomic write and file locking.

        Args:
            state: WorkflowState to persist

        Raises:
            StateManagerError: If save fails
        """
        state_file = self._get_state_file(state.session_id)

        # Update timestamp (create new state with updated timestamp)
        state = state.model_copy(update={"updated_at": datetime.now()})

        # Serialize to JSON
        try:
            data = state.model_dump(mode="json")  # Pydantic v2 serialization
        except Exception as e:
            raise StateManagerError(
                what_failed="State serialization",
                why_failed=f"Failed to serialize WorkflowState to JSON: {e}",
                how_to_fix="Check WorkflowState model for non-serializable fields",
            ) from e

        # Write with file locking for concurrent access safety
        try:
            # Create parent directories if needed
            state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(state_file, "w", encoding="utf-8") as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2, default=str)  # default=str handles datetime
                    f.flush()
                finally:
                    # Release lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            logger.debug("Saved state", extra={"session_id": state.session_id, "state_file": str(state_file)})

        except Exception as e:
            raise StateManagerError(
                what_failed="State persistence",
                why_failed=f"Failed to write state file {state_file}: {e}",
                how_to_fix=f"Check filesystem permissions for {state_file.parent}",
            ) from e

    def load_state(self, session_id: str) -> Optional[WorkflowState]:
        """
        Load workflow state from disk.

        Args:
            session_id: Session identifier

        Returns:
            WorkflowState if found, None if session doesn't exist

        Raises:
            StateManagerError: If state file is corrupted
        """
        state_file = self._get_state_file(session_id)

        if not state_file.exists():
            logger.debug("State file not found", extra={"session_id": session_id, "state_file": str(state_file)})
            return None

        # Read with file locking
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                # Acquire shared lock (multiple readers OK)
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                finally:
                    # Release lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Deserialize to Pydantic model
            state = WorkflowState(**data)
            logger.debug("Loaded state", extra={"session_id": session_id, "current_phase": state.current_phase})
            return state

        except json.JSONDecodeError as e:
            raise StateManagerError(
                what_failed="State deserialization",
                why_failed=f"State file {state_file} contains invalid JSON: {e}",
                how_to_fix=f"Delete corrupted state file: rm {state_file}",
            ) from e
        except Exception as e:
            raise StateManagerError(
                what_failed="State loading",
                why_failed=f"Failed to load state file {state_file}: {e}",
                how_to_fix=f"Check state file format or delete: rm {state_file}",
            ) from e

    def create_session(
        self, workflow_type: str, target_file: str, session_id: Optional[str] = None, metadata: Optional[Dict] = None
    ) -> WorkflowState:
        """
        Create new workflow session.

        Args:
            workflow_type: Workflow type identifier
            target_file: Target file being worked on
            session_id: Optional custom session ID (generates UUID if None)
            metadata: Optional session metadata

        Returns:
            New WorkflowState with session initialized

        Raises:
            StateManagerError: If session already exists
        """
        import uuid

        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Check if session already exists
        if self._get_state_file(session_id).exists():
            raise StateManagerError(
                what_failed="Session creation",
                why_failed=f"Session {session_id} already exists",
                how_to_fix=f"Use a different session ID or delete existing session",
            )

        # Create initial state
        state = WorkflowState(
            session_id=session_id,
            workflow_type=workflow_type,
            target_file=target_file,
            current_phase=0,
            completed_phases=[],
            metadata=metadata or {},
            completed_at=None,
        )

        # Persist state
        self.save_state(state)

        logger.info(
            "Created workflow session",
            extra={"session_id": session_id, "workflow_type": workflow_type, "target_file": target_file},
        )

        return state

    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all workflow sessions.

        Args:
            status: Optional filter ("active", "completed", "all")

        Returns:
            List of session summaries (session_id, workflow_type, current_phase, updated_at)
        """
        sessions = []

        for state_file in self.state_dir.glob("*.json"):
            try:
                state = self.load_state(state_file.stem)  # stem = filename without extension
                if state is None:
                    continue

                # Determine status
                is_complete = len(state.completed_phases) > 0 and state.current_phase > max(state.completed_phases)

                # Apply filter
                if status == "active" and is_complete:
                    continue
                if status == "completed" and not is_complete:
                    continue

                sessions.append(
                    {
                        "session_id": state.session_id,
                        "workflow_type": state.workflow_type,
                        "target_file": state.target_file,
                        "current_phase": state.current_phase,
                        "completed_phases": state.completed_phases,
                        "updated_at": state.updated_at.isoformat(),
                        "is_complete": is_complete,
                    }
                )
            except Exception as e:
                logger.warning("Failed to load session", extra={"state_file": str(state_file), "error": str(e)})
                continue

        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)  # type: ignore[arg-type,return-value]

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session state file.

        Args:
            session_id: Session to delete

        Returns:
            True if deleted, False if session didn't exist
        """
        state_file = self._get_state_file(session_id)

        if not state_file.exists():
            return False

        try:
            state_file.unlink()
            logger.info("Deleted session", extra={"session_id": session_id})
            return True
        except Exception as e:
            raise StateManagerError(
                what_failed="Session deletion",
                why_failed=f"Failed to delete state file {state_file}: {e}",
                how_to_fix=f"Check filesystem permissions for {state_file}",
            ) from e

    def cleanup_completed(self, older_than_days: Optional[int] = None) -> int:
        """
        Cleanup completed sessions older than threshold.

        Args:
            older_than_days: Days threshold (uses self.cleanup_days if None)

        Returns:
            Number of sessions deleted
        """
        if older_than_days is None:
            older_than_days = self.cleanup_days

        threshold = datetime.now() - timedelta(days=older_than_days)
        deleted_count = 0

        for state_file in self.state_dir.glob("*.json"):
            try:
                state = self.load_state(state_file.stem)
                if state is None:
                    continue

                # Check if completed and old
                is_complete = len(state.completed_phases) > 0 and state.current_phase > max(state.completed_phases)

                if is_complete and state.updated_at < threshold:
                    if self.delete_session(state.session_id):
                        deleted_count += 1
            except Exception as e:
                logger.warning(
                    "Failed to cleanup session", extra={"state_file": str(state_file), "error": str(e)}
                )
                continue

        if deleted_count > 0:
            logger.info("Cleaned up completed sessions", extra={"deleted_count": deleted_count})

        return deleted_count

    def _get_state_file(self, session_id: str) -> Path:
        """Get state file path for session ID."""
        return self.state_dir / f"{session_id}.json"


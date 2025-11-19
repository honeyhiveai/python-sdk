"""
Session Mapper: Generic session state persistence (Middleware Layer).

Provides transparent session management for all subsystems:
- UUID generation and session_id creation
- Generic JSON state persistence (doesn't know subsystem models)
- Directory-based status organization (active/completed/error)
- Auto-move on status change
- Cleanup (timeout for active, age for completed/error)
- File locking (fcntl) for concurrent safety

Architecture:
    Tools → SessionMapper → Disk State (by invoker & status)
    
    state/
    ├── workflow/
    │   ├── active/
    │   ├── completed/
    │   └── error/
    └── browser/
        ├── active/
        ├── completed/
        └── error/

Key Design:
- SessionMapper is GENERIC (doesn't know WorkflowState, BrowserSession models)
- Subsystems serialize/deserialize their own models
- Status in BOTH directory (organization) and JSON (subsystem access)
- Auto-move: save_state() with new status deletes old location
- Transparent: AI agents and humans don't think about state management

Usage:
    >>> mapper = SessionMapper(state_dir=Path(".praxis-os/state"))
    >>> 
    >>> # Create session
    >>> session_id = mapper.create_session_id(ctx, "workflow")
    >>> 
    >>> # Save state (generic dict)
    >>> mapper.save_state("workflow", session_id, {"status": "active", ...}, "active")
    >>> 
    >>> # Load state (generic dict)
    >>> data = mapper.load_state("workflow", session_id)
    >>> 
    >>> # Complete workflow (auto-moves active → completed)
    >>> mapper.save_state("workflow", session_id, {"status": "completed", ...}, "completed")
    >>> 
    >>> # Cleanup
    >>> mapper.cleanup_by_timeout("browser", idle_timeout_minutes=30)
    >>> mapper.cleanup_by_age("workflow", "completed", older_than_days=30)

Traceability:
    FR-021: Isolated Sessions (session isolation)
    NFR-M2: Middleware coverage (100% of stateful tool calls)
    NFR-M4: Auto-maintenance (transparent cleanup)
"""

import fcntl
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class SessionMapper:
    """
    Generic session state persistence for all subsystems.
    
    Responsibilities:
    - UUID generation and session_id creation
    - Generic JSON state persistence (doesn't know subsystem models)
    - Directory-based status organization (active/completed/error)
    - Auto-move on status change
    - Cleanup (timeout for active, age for completed/error)
    - File locking (fcntl) for concurrent safety
    
    Does NOT know about:
    - WorkflowState, BrowserSession models
    - Subsystem business logic
    - What fields are in the state JSON
    
    Example:
        >>> mapper = SessionMapper(state_dir=Path(".praxis-os/state"))
        >>> session_id = mapper.create_session_id(ctx, "workflow")
        >>> mapper.save_state("workflow", session_id, {...}, "active")
        >>> data = mapper.load_state("workflow", session_id)
    """
    
    def __init__(self, state_dir: Path):
        """
        Initialize SessionMapper.
        
        Args:
            state_dir: Base directory for state files
                      Example: .praxis-os/state
        """
        # ALWAYS use absolute path to avoid CWD issues
        self.state_dir = state_dir.resolve()
        
        # Ensure base directory and subdirectories exist
        for invoker in ["workflow", "browser"]:
            for status in ["active", "completed", "error"]:
                (self.state_dir / invoker / status).mkdir(parents=True, exist_ok=True)
        
        logger.info("SessionMapper initialized", extra={"state_dir": str(self.state_dir)})
    
    def create_session_id(self, invoker: str, conversation_id: Optional[str] = None) -> str:
        """
        Create new session ID for subsystem.
        
        Format: {invoker}_{conversation_id}_{uuid}
        Example: "workflow_client_abc_s0_550e8400-e29b-41d4-a716-446655440000"
        
        Args:
            invoker: Subsystem name ("workflow", "browser")
            conversation_id: Optional conversation context
                           If None, uses "default"
        
        Returns:
            str: Unique session ID
        
        Example:
            >>> session_id = mapper.create_session_id("workflow", "client_abc_s0")
            >>> # Returns: "workflow_client_abc_s0_550e8400-..."
        """
        conv_id = conversation_id or "default"
        uuid = str(uuid4())
        session_id = f"{invoker}_{conv_id}_{uuid}"
        
        logger.debug("Created session ID", extra={"invoker": invoker, "session_id": session_id})
        return session_id
    
    def save_state(
        self,
        invoker: str,
        session_id: str,
        state_data: Dict[str, Any],
        status: str = "active"
    ) -> None:
        """
        Save state with auto-move on status change.
        
        Process:
        1. Updates state_data["status"] = status
        2. Writes to state/{invoker}/{status}/{session_id}.json
        3. If file exists in different status dir, deletes old location
        
        Args:
            invoker: Subsystem ("workflow", "browser")
            session_id: Session identifier
            state_data: Generic dict/JSON data (subsystem-specific structure)
            status: "active", "completed", or "error"
        
        Example:
            # First save
            mapper.save_state("workflow", "wf_123", {...}, status="active")
            # → Creates state/workflow/active/wf_123.json
            
            # Later, workflow completes
            mapper.save_state("workflow", "wf_123", {...}, status="completed")
            # → Creates state/workflow/completed/wf_123.json
            # → Deletes state/workflow/active/wf_123.json (auto-move)
        
        Raises:
            ValueError: If status is not one of: active, completed, error
        """
        if status not in ["active", "completed", "error"]:
            raise ValueError(f"Invalid status: {status}. Must be: active, completed, error")
        
        # Ensure status is in the data (both directory and JSON)
        state_data = state_data.copy()  # Don't mutate input
        state_data["status"] = status
        
        # Target path
        target_path = self.state_dir / invoker / status / f"{session_id}.json"
        
        # Write with atomic operation + file locking
        self._write_json_atomic(target_path, state_data)
        
        # Delete from other status directories (auto-move)
        for other_status in ["active", "completed", "error"]:
            if other_status != status:
                old_path = self.state_dir / invoker / other_status / f"{session_id}.json"
                if old_path.exists():
                    old_path.unlink()
                    logger.debug(
                        "Moved session between statuses",
                        extra={
                            "session_id": session_id,
                            "invoker": invoker,
                            "from_status": other_status,
                            "to_status": status
                        }
                    )
        
        logger.debug("Saved state", extra={"invoker": invoker, "session_id": session_id, "status": status})
    
    def load_state(
        self,
        invoker: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load state from any status directory.
        
        Searches: active → completed → error
        
        Args:
            invoker: Subsystem ("workflow", "browser")
            session_id: Session identifier
        
        Returns:
            dict: State data with status field, or None if not found
        
        Example:
            >>> data = mapper.load_state("workflow", "wf_123")
            >>> if data:
            >>>     print(data["status"])  # "active", "completed", or "error"
        """
        for status in ["active", "completed", "error"]:
            path = self.state_dir / invoker / status / f"{session_id}.json"
            if path.exists():
                data = self._read_json_locked(path)
                
                # Verify status matches directory (defensive programming)
                if data.get("status") != status:
                    logger.warning(
                        "Status mismatch between directory and JSON",
                        extra={
                            "session_id": session_id,
                            "dir_status": status,
                            "json_status": data.get("status")
                        }
                    )
                    data["status"] = status  # Trust directory
                
                logger.debug("Loaded state", extra={"invoker": invoker, "session_id": session_id, "status": status})
                return data
        
        logger.debug("State not found", extra={"invoker": invoker, "session_id": session_id})
        return None
    
    def list_sessions(
        self,
        invoker: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List sessions with metadata.
        
        Args:
            invoker: Subsystem ("workflow", "browser")
            status: Optional filter ("active", "completed", "error")
        
        Returns:
            List of dicts with: {
                "session_id": str,
                "status": str,
                "file_path": str,
                "last_modified": datetime
            }
        
        Example:
            >>> # List all workflow sessions
            >>> sessions = mapper.list_sessions("workflow")
            >>> 
            >>> # List only active workflows
            >>> active = mapper.list_sessions("workflow", status="active")
        """
        statuses = [status] if status else ["active", "completed", "error"]
        sessions = []
        
        for stat in statuses:
            status_dir = self.state_dir / invoker / stat
            if not status_dir.exists():
                continue
                
            for json_file in status_dir.glob("*.json"):
                sessions.append({
                    "session_id": json_file.stem,
                    "status": stat,
                    "file_path": str(json_file),
                    "last_modified": datetime.fromtimestamp(json_file.stat().st_mtime)
                })
        
        logger.debug(
            "Listed sessions",
            extra={"invoker": invoker, "status_filter": status, "count": len(sessions)}
        )
        return sessions
    
    def cleanup_by_timeout(
        self,
        invoker: str,
        idle_timeout_minutes: int
    ) -> int:
        """
        Cleanup active sessions by idle timeout.
        
        Use case: Browser sessions with no activity for N minutes
        
        Checks state_data["last_access"] field (subsystem must maintain this!)
        Moves to "error" status (timeout = abnormal termination)
        
        Args:
            invoker: Subsystem ("browser")
            idle_timeout_minutes: Idle time before cleanup
        
        Returns:
            int: Number of sessions cleaned up
        
        Example:
            >>> # Cleanup browsers idle for 30+ minutes
            >>> count = mapper.cleanup_by_timeout("browser", idle_timeout_minutes=30)
            >>> print(f"Cleaned up {count} idle sessions")
        """
        cleaned = 0
        cutoff = datetime.now() - timedelta(minutes=idle_timeout_minutes)
        
        active_dir = self.state_dir / invoker / "active"
        if not active_dir.exists():
            return 0
        
        for json_file in active_dir.glob("*.json"):
            try:
                data = self._read_json_locked(json_file)
                
                # Check last_access (subsystem-specific field)
                last_access_str = data.get("last_access")
                if last_access_str:
                    try:
                        last_access = datetime.fromisoformat(last_access_str)
                        if last_access < cutoff:
                            # Move to error (timeout)
                            data["status"] = "error"
                            data["error_reason"] = f"Idle timeout ({idle_timeout_minutes}m)"
                            self.save_state(invoker, json_file.stem, data, status="error")
                            cleaned += 1
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid last_access format: {e}", extra={"session_id": json_file.stem})
            except Exception as e:
                logger.error(f"Error during timeout cleanup: {e}", extra={"file": str(json_file)})
        
        if cleaned > 0:
            logger.info(
                "Cleaned up idle sessions",
                extra={"invoker": invoker, "count": cleaned, "timeout_minutes": idle_timeout_minutes}
            )
        
        return cleaned
    
    def cleanup_by_age(
        self,
        invoker: str,
        status: str,
        older_than_days: int
    ) -> int:
        """
        Delete sessions older than N days from completed/error.
        
        Use case: Purge old completed workflows after 30 days
        
        Args:
            invoker: Subsystem ("workflow", "browser")
            status: "completed" or "error" (NOT "active"!)
            older_than_days: Age threshold
        
        Returns:
            int: Number of sessions deleted
        
        Example:
            >>> # Delete completed workflows older than 30 days
            >>> count = mapper.cleanup_by_age("workflow", "completed", older_than_days=30)
            >>> print(f"Deleted {count} old sessions")
        
        Raises:
            ValueError: If status is "active" (use cleanup_by_timeout instead)
        """
        if status == "active":
            raise ValueError("Cannot cleanup active sessions by age, use cleanup_by_timeout")
        
        if status not in ["completed", "error"]:
            raise ValueError(f"Invalid status: {status}. Must be: completed, error")
        
        deleted = 0
        cutoff = datetime.now() - timedelta(days=older_than_days)
        
        status_dir = self.state_dir / invoker / status
        if not status_dir.exists():
            return 0
        
        for json_file in status_dir.glob("*.json"):
            try:
                mtime = datetime.fromtimestamp(json_file.stat().st_mtime)
                if mtime < cutoff:
                    json_file.unlink()
                    deleted += 1
                    logger.debug(
                        "Deleted old session",
                        extra={
                            "session_id": json_file.stem,
                            "invoker": invoker,
                            "status": status,
                            "age_days": (datetime.now() - mtime).days
                        }
                    )
            except Exception as e:
                logger.error(f"Error during age cleanup: {e}", extra={"file": str(json_file)})
        
        if deleted > 0:
            logger.info(
                "Cleaned up old sessions",
                extra={"invoker": invoker, "status": status, "count": deleted, "older_than_days": older_than_days}
            )
        
        return deleted
    
    def _write_json_atomic(self, path: Path, data: Dict[str, Any]) -> None:
        """
        Atomic write with fcntl exclusive locking.
        
        Args:
            path: Target file path
            data: Data to serialize as JSON
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2, default=str)
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def _read_json_locked(self, path: Path) -> Dict[str, Any]:
        """
        Read JSON with fcntl shared lock.
        
        Args:
            path: Source file path
        
        Returns:
            dict: Deserialized JSON data
        """
        with open(path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                return json.load(f)  # type: ignore[no-any-return]
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


# Singleton instance for use across subsystems
_session_mapper: Optional[SessionMapper] = None


def get_session_mapper(state_dir: Optional[Path] = None) -> SessionMapper:
    """
    Get singleton SessionMapper instance.
    
    Args:
        state_dir: Optional state directory (used for first initialization)
                  If None and mapper exists, returns existing instance
                  If None and mapper doesn't exist, raises error
    
    Returns:
        SessionMapper: Global session mapper instance
    
    Example:
        >>> # Initialize once
        >>> mapper = get_session_mapper(state_dir=Path(".praxis-os/state"))
        >>> 
        >>> # Later calls don't need state_dir
        >>> mapper = get_session_mapper()
    
    Raises:
        RuntimeError: If mapper not initialized and no state_dir provided
    """
    global _session_mapper
    
    if _session_mapper is None:
        if state_dir is None:
            raise RuntimeError("SessionMapper not initialized. Provide state_dir on first call.")
        _session_mapper = SessionMapper(state_dir)
    
    return _session_mapper


__all__ = [
    "SessionMapper",
    "get_session_mapper",
]


"""
Session State Helper - DRY wrapper for subsystem state persistence.

Provides a clean interface for subsystems to persist/load typed state via SessionMapper
without boilerplate serialization/deserialization logic.

Architecture:
    - Generic over state model (Type[BaseModel])
    - Wraps SessionMapper with subsystem-specific context
    - Handles serialization (Pydantic → JSON) and deserialization (JSON → Pydantic)
    - Provides list_sessions with automatic state enrichment

Example:
    >>> from ouroboros.subsystems.workflow.models import WorkflowState
    >>> 
    >>> helper = SessionStateHelper(
    ...     session_mapper=session_mapper,
    ...     invoker="workflow",
    ...     state_model=WorkflowState
    ... )
    >>> 
    >>> # Save state
    >>> state = WorkflowState(session_id="abc", workflow_type="spec", ...)
    >>> helper.save(state, status="active")
    >>> 
    >>> # Load state (typed!)
    >>> loaded: WorkflowState = helper.load("abc")

Traceability:
    Design Decision: Composition over inheritance for session state management
    Benefits: Testability, extensibility, maintainability, type safety
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

from ouroboros.foundation.session_mapper import SessionMapper

logger = logging.getLogger(__name__)

# Generic type for state models (must be Pydantic BaseModel)
TState = TypeVar("TState", bound=BaseModel)


class SessionStateHelper(Generic[TState]):
    """
    Generic helper for subsystem state persistence.
    
    Wraps SessionMapper with subsystem-specific context (invoker name, state model)
    and provides typed save/load operations with automatic serialization.
    
    Type Parameters:
        TState: The Pydantic model for this subsystem's state
    
    Attributes:
        session_mapper: SessionMapper instance for generic persistence
        invoker: Subsystem identifier ("workflow", "browser", etc.)
        state_model: Pydantic model class for type-safe deserialization
    """
    
    def __init__(
        self,
        session_mapper: SessionMapper,
        invoker: str,
        state_model: Type[TState],
    ):
        """
        Initialize helper for a specific subsystem.
        
        Args:
            session_mapper: SessionMapper instance
            invoker: Subsystem identifier (e.g., "workflow", "browser")
            state_model: Pydantic model class for state
        """
        self.session_mapper = session_mapper
        self.invoker = invoker
        self.state_model = state_model
        
        logger.debug(
            "SessionStateHelper initialized",
            extra={"invoker": invoker, "model": state_model.__name__}
        )
    
    def save(self, state: TState, status: str = "active") -> None:
        """
        Save state with automatic serialization.
        
        Args:
            state: Pydantic state model instance
            status: Session status ("active", "completed", "error")
        
        Example:
            >>> helper.save(workflow_state, status="active")
        """
        # Extract session_id from state (all state models must have it)
        session_id = state.session_id  # type: ignore[attr-defined]
        
        # Serialize Pydantic → JSON-compatible dict
        state_data = state.model_dump(mode="json")
        
        # Persist via SessionMapper
        self.session_mapper.save_state(
            invoker=self.invoker,
            session_id=session_id,
            state_data=state_data,
            status=status
        )
        
        logger.debug(
            "State saved",
            extra={
                "invoker": self.invoker,
                "session_id": session_id,
                "status": status,
            }
        )
    
    def load(self, session_id: str) -> Optional[TState]:
        """
        Load state with automatic deserialization.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Typed state model instance, or None if not found
        
        Example:
            >>> state: WorkflowState = helper.load("workflow_abc_123")
            >>> if state:
            ...     print(state.current_phase)
        """
        # Load generic dict from SessionMapper
        state_data = self.session_mapper.load_state(self.invoker, session_id)
        
        if state_data is None:
            logger.debug(
                "State not found",
                extra={"invoker": self.invoker, "session_id": session_id}
            )
            return None
        
        # Strip SessionMapper's internal "status" field (implementation detail)
        # This field is used for directory organization but not part of subsystem models
        state_data.pop("status", None)
        
        # Deserialize JSON → Pydantic (type-safe!)
        try:
            state = self.state_model.model_validate(state_data)
            logger.debug(
                "State loaded",
                extra={
                    "invoker": self.invoker,
                    "session_id": session_id,
                    "model": self.state_model.__name__,
                }
            )
            return state
        except Exception as e:
            logger.error(
                "State deserialization failed",
                extra={
                    "invoker": self.invoker,
                    "session_id": session_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            return None
    
    def list_sessions(
        self,
        status: Optional[str] = None,
        enrich: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        List sessions with optional state enrichment.
        
        Args:
            status: Optional filter ("active", "completed", "error", or None for all)
            enrich: If True, load full state for each session (slower but detailed)
        
        Returns:
            List of session metadata (minimal) or enriched with full state
        
        Example:
            >>> # Minimal (fast)
            >>> sessions = helper.list_sessions(status="active")
            >>> [{'session_id': '...', 'status': 'active', ...}]
            >>> 
            >>> # Enriched (slower, but includes full state)
            >>> sessions = helper.list_sessions(status="active", enrich=True)
            >>> [{'session_id': '...', 'state': WorkflowState(...), ...}]
        """
        # Get minimal metadata from SessionMapper
        sessions = self.session_mapper.list_sessions(self.invoker, status=status)
        
        if not enrich:
            return sessions
        
        # Enrich with full state
        enriched = []
        for meta in sessions:
            try:
                state = self.load(meta["session_id"])
                if state:
                    enriched.append({
                        **meta,
                        "state": state,  # Typed state model
                    })
            except Exception as e:
                logger.warning(
                    "Failed to enrich session",
                    extra={
                        "invoker": self.invoker,
                        "session_id": meta["session_id"],
                        "error": str(e),
                    }
                )
                continue
        
        return enriched
    
    def delete(self, session_id: str, reason: str = "manually_deleted") -> bool:
        """
        Delete session (mark as error for cleanup).
        
        Args:
            session_id: Session to delete
            reason: Reason for deletion (for logging/debugging)
        
        Returns:
            True if deleted, False if not found
        
        Example:
            >>> helper.delete("workflow_abc_123", reason="user_cancelled")
        """
        # Load current state
        state = self.load(session_id)
        
        if state is None:
            return False
        
        # Mark as error (manually deleted) - will be cleaned up by cleanup task
        state_data = state.model_dump(mode="json")
        state_data["error_reason"] = reason
        
        self.session_mapper.save_state(
            invoker=self.invoker,
            session_id=session_id,
            state_data=state_data,
            status="error"
        )
        
        logger.info(
            "Session deleted (moved to error)",
            extra={
                "invoker": self.invoker,
                "session_id": session_id,
                "reason": reason,
            }
        )
        return True


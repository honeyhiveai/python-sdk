"""
pos_workflow: Unified workflow management tool.

Provides a single consolidated tool for all workflow operations:
- Discovery (1 action): list_workflows
- Execution (5 actions): start, get_phase, get_task, complete_phase, get_state
- Management (3 actions): list_sessions, get_session, delete_session
- Recovery (5 actions): pause, resume, retry_phase, rollback, get_errors

Architecture:
    AI Agent → pos_workflow (Tools Layer)
        ↓
    WorkflowEngine (Workflow Subsystem)
        ↓
    ├─ WorkflowRenderer (content loading)
    ├─ PhaseGates (sequential enforcement)
    ├─ EvidenceValidator (multi-layer validation)
    ├─ HiddenSchemas (evidence schemas)
    └─ StateManager (persistence)

Traceability:
    FR-006: pos_workflow - Workflow Execution Tool
    FR-017: Phase-Gated Execution
    FR-018: Evidence Validation
    FR-019: Hidden Evidence Schemas
    FR-020: Workflow State Persistence
"""

import ast
import json
import logging
from typing import Any, Dict, Literal, Optional, Union

from ouroboros.tools.base import ActionDispatchMixin

logger = logging.getLogger(__name__)


class WorkflowTool(ActionDispatchMixin):
    """
    Unified workflow management tool using ActionDispatchMixin pattern.
    
    Provides comprehensive workflow operations through a single tool interface.
    """
    
    def __init__(self, mcp: Any, workflow_engine: Any):
        """Initialize with workflow engine."""
        super().__init__(mcp)
        self.workflow_engine = workflow_engine
        
        # Define action handlers
        self.handlers = {
            # Discovery
            "list_workflows": self._handle_list_workflows,
            # Execution
            "start": self._handle_start,
            "get_phase": self._handle_get_phase,
            "get_task": self._handle_get_task,
            "complete_phase": self._handle_complete_phase,
            "get_state": self._handle_get_state,
            # Management
            "list_sessions": self._handle_list_sessions,
            "get_session": self._handle_get_session,
            "delete_session": self._handle_delete_session,
            # Recovery (stubs)
            "pause": self._handle_pause,
            "resume": self._handle_resume,
            "retry_phase": self._handle_retry_phase,
            "rollback": self._handle_rollback,
            "get_errors": self._handle_get_errors,
        }
    
    @property
    def tool(self):
        """Return the MCP tool decorator wrapper."""
        @self.mcp.tool()
        async def pos_workflow(
            action: Literal[
                # Discovery (1 action)
                "list_workflows",
                # Execution (5 actions)
                "start",
                "get_phase",
                "get_task",
                "complete_phase",
                "get_state",
                # Management (3 actions)
                "list_sessions",
                "get_session",
                "delete_session",
                # Recovery (5 actions - stubs)
                "pause",
                "resume",
                "retry_phase",
                "rollback",
                "get_errors",
            ],
            # Session context
            session_id: Optional[str] = None,
            # Start workflow parameters
            workflow_type: Optional[str] = None,
            target_file: Optional[str] = None,
            options: Optional[Union[Dict[str, Any], str]] = None,  # Union to handle JSON string serialization
            # Task retrieval parameters (Union to handle JSON number serialization)
            phase: Union[int, float, None] = None,
            task_number: Union[int, float, None] = None,
            # Phase completion parameters
            evidence: Optional[Dict[str, Any]] = None,
            # Discovery parameters
            category: Optional[str] = None,
            # Session management parameters
            status: Optional[str] = None,
            reason: Optional[str] = None,
            checkpoint_note: Optional[str] = None,
            # Recovery parameters
            reset_evidence: Optional[bool] = False,
            to_phase: Union[int, float, None] = None,
        ) -> Dict[str, Any]:
            """
            Unified workflow management tool.
            
            Handles all workflow operations through action-based dispatch:
            - Discovery (1 action): list_workflows
            - Execution (5 actions): start, get_phase, get_task, complete_phase, get_state
            - Management (3 actions): list_sessions, get_session, delete_session
            - Recovery (5 actions): pause, resume, retry_phase, rollback, get_errors
            
            Args:
                action: Operation to perform (required)
                session_id: Session identifier (required for most operations)
                workflow_type: Workflow type identifier (required for start)
                target_file: Target file path (required for start)
                options: Optional workflow configuration (for start)
                phase: Phase number (for get_phase, complete_phase, retry_phase)
                task_number: Task number (for get_task)
                evidence: Evidence dictionary (for complete_phase)
                category: Workflow category filter (for list_workflows)
                status: Session status filter (for list_sessions)
                reason: Pause/resume reason (for pause, resume)
                checkpoint_note: Note for pause checkpoint (for pause)
                reset_evidence: Reset evidence on retry (for retry_phase)
                to_phase: Target phase for rollback (for rollback)
                
            Returns:
                Dictionary with operation results and status
                
            Examples:
                >>> # Start a workflow
                >>> pos_workflow(
                ...     action="start",
                ...     workflow_type="spec_execution_v1",
                ...     target_file="specs/ouroboros.md"
                ... )
                
                >>> # Get current phase
                >>> pos_workflow(
                ...     action="get_phase",
                ...     session_id="550e8400-..."
                ... )
                
                >>> # Complete phase with evidence
                >>> pos_workflow(
                ...     action="complete_phase",
                ...     session_id="550e8400-...",
                ...     phase=1,
                ...     evidence={"tests_passed": 15, "coverage": 95}
                ... )
            
            Raises:
                ValueError: If action is invalid or required parameters missing
                
            Traceability:
                FR-006: pos_workflow - Workflow Execution Tool
                FR-017: Phase-Gated Execution
                FR-018: Evidence Validation
            """
            # Type coercion for numeric parameters (MCP sends JSON numbers)
            if phase is not None:
                phase = int(phase)
            if task_number is not None:
                task_number = int(task_number)
            if to_phase is not None:
                to_phase = int(to_phase)
            
            # Dispatch to handler
            return await self.dispatch(
                action,
                self.handlers,  # type: ignore[arg-type]
                session_id=session_id,
                workflow_type=workflow_type,
                target_file=target_file,
                options=options,
                phase=phase,
                task_number=task_number,
                evidence=evidence,
                category=category,
                status=status,
                reason=reason,
                checkpoint_note=checkpoint_note,
                reset_evidence=reset_evidence,
                to_phase=to_phase,
            )
        
        return pos_workflow
    
    # ========================================================================
    # Discovery Handlers
    # ========================================================================
    
    async def _handle_list_workflows(self, category: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        List available workflows with optional category filtering.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dict with workflows list and count
        """
        # Load workflows from workflows directory
        workflows_dir = self.workflow_engine.workflows_dir
        workflows = []
        
        if workflows_dir.exists():
            # Scan for metadata.json files
            for metadata_file in workflows_dir.glob("*/metadata.json"):
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        # Apply category filter if provided
                        if category is None or metadata.get("category") == category:
                            workflows.append(metadata)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load {metadata_file}: {e}")
                    continue
        
        return {
            "workflows": workflows,
            "count": len(workflows),
        }
    
    # ========================================================================
    # Execution Handlers
    # ========================================================================
    
    async def _handle_start(
        self,
        workflow_type: Optional[str] = None,
        target_file: Optional[str] = None,
        options: Optional[Union[Dict[str, Any], str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Start new workflow session.
        
        Args:
            workflow_type: Workflow identifier (required)
            target_file: Target file path (required)
            options: Optional workflow configuration
            
        Returns:
            Dict with session info and initial phase content
            
        Raises:
            ValueError: If required parameters missing
        """
        if not workflow_type:
            raise ValueError("start action requires workflow_type parameter")
        if not target_file:
            raise ValueError("start action requires target_file parameter")
        
        # Validate target_file for security (no directory traversal)
        if ".." in target_file or target_file.startswith("/"):
            raise ValueError(f"Invalid target_file: {target_file} (contains '..' or starts with '/')")
        
        # Defensive: Handle MCP serializing options dict as JSON string or Python repr
        parsed_options = {}
        if options:
            if isinstance(options, str):
                # Try JSON first (standard format)
                try:
                    parsed_options = json.loads(options)
                    logger.debug("options parameter received as JSON string, parsed successfully")
                except json.JSONDecodeError:
                    # Try Python literal eval (in case FastMCP sends Python dict repr)
                    try:
                        parsed_options = ast.literal_eval(options)
                        if not isinstance(parsed_options, dict):
                            raise ValueError(f"options string evaluated to {type(parsed_options)}, expected dict")
                        logger.debug("options parameter received as Python dict string, parsed successfully")
                    except (ValueError, SyntaxError) as e:
                        logger.error(f"Failed to parse options string: {e}. Received: {options[:200]}")
                        raise ValueError(
                            f"options parameter must be valid JSON or Python dict string. "
                            f"Error: {e}. Received: {options[:200] if len(options) > 200 else options}"
                        )
            elif isinstance(options, dict):
                parsed_options = options
            else:
                raise ValueError(f"options parameter must be dict or string, got {type(options)}")
        
        # Call WorkflowEngine to start session
        result = self.workflow_engine.start_workflow(
            workflow_type=workflow_type,
            target_file=target_file,
            **parsed_options
        )
        
        return result  # type: ignore[no-any-return]
    
    async def _handle_get_phase(
        self,
        session_id: Optional[str] = None,
        phase: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get phase content and guidance.
        
        Args:
            session_id: Session identifier (required)
            phase: Phase number (optional, defaults to current phase)
            
        Returns:
            Dict with phase content and metadata
            
        Raises:
            ValueError: If session_id missing or invalid
        """
        if not session_id:
            raise ValueError("get_phase action requires session_id parameter")
        
        # Validate session ID format
        self._validate_session_id(session_id)
        
        # Load state to get current phase if not specified
        state = self.workflow_engine._state_helper.load(session_id)
        if not state:
            raise ValueError(f"Session not found: {session_id}")
        
        # Use current phase if not specified
        target_phase = phase if phase is not None else state.current_phase
        
        # Get phase content
        result = self.workflow_engine.get_phase(session_id, target_phase)
        
        return result  # type: ignore[no-any-return]
    
    async def _handle_get_task(
        self,
        session_id: Optional[str] = None,
        phase: Optional[int] = None,
        task_number: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get specific task details within a phase.
        
        Args:
            session_id: Session identifier (required)
            phase: Phase number (required)
            task_number: Task number within phase (required)
            
        Returns:
            Dict with task content and acceptance criteria
            
        Raises:
            ValueError: If required parameters missing or invalid
        """
        if not session_id:
            raise ValueError("get_task action requires session_id parameter")
        if phase is None:
            raise ValueError("get_task action requires phase parameter")
        if task_number is None:
            raise ValueError("get_task action requires task_number parameter")
        
        # Validate session ID format
        self._validate_session_id(session_id)
        
        # Validate phase and task_number are valid integers
        if not isinstance(phase, int) or phase < 0:
            raise ValueError(f"phase must be a non-negative integer, got: {phase}")
        if not isinstance(task_number, int) or task_number < 0:
            raise ValueError(f"task_number must be a non-negative integer, got: {task_number}")
        
        # Get task content
        result = self.workflow_engine.get_task(session_id, phase, task_number)
        
        return result  # type: ignore[no-any-return]
    
    async def _handle_complete_phase(
        self,
        session_id: Optional[str] = None,
        phase: Optional[int] = None,
        evidence: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete phase with evidence validation.
        
        Args:
            session_id: Session identifier (required)
            phase: Phase number (required)
            evidence: Evidence dictionary (required)
            
        Returns:
            Dict with completion status and next phase info
            
        Raises:
            ValueError: If required parameters missing or evidence invalid
        """
        if not session_id:
            raise ValueError("complete_phase action requires session_id parameter")
        if phase is None:
            raise ValueError("complete_phase action requires phase parameter")
        if evidence is None:
            raise ValueError("complete_phase action requires evidence parameter")
        
        # Validate session ID format
        self._validate_session_id(session_id)
        
        # Validate evidence size (prevent DoS)
        self._validate_evidence_size(evidence)
        
        # Complete phase with evidence validation
        result = self.workflow_engine.complete_phase(session_id, phase, evidence)
        
        return result  # type: ignore[no-any-return]
    
    async def _handle_get_state(
        self,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get complete workflow state.
        
        Args:
            session_id: Session identifier (required)
            
        Returns:
            Dict with complete workflow state
            
        Raises:
            ValueError: If session_id missing or invalid
        """
        if not session_id:
            raise ValueError("get_state action requires session_id parameter")
        
        # Validate session ID format
        self._validate_session_id(session_id)
        
        # Load state
        state = self.workflow_engine._state_helper.load(session_id)
        if not state:
            raise ValueError(f"Session not found: {session_id}")
        
        # Convert state to dictionary
        return {
            "session_id": session_id,
            "workflow_type": state.workflow_type,
            "current_phase": state.current_phase,
            "target_file": state.target_file,
            "metadata": state.metadata.model_dump() if hasattr(state.metadata, "model_dump") else state.metadata,
            "checkpoints": {
                phase: checkpoint.value for phase, checkpoint in state.checkpoints.items()
            },
            "phase_artifacts": {
                phase: artifact.model_dump() if hasattr(artifact, "model_dump") else artifact
                for phase, artifact in state.phase_artifacts.items()
            },
            "created_at": state.created_at.isoformat() if hasattr(state.created_at, "isoformat") else str(state.created_at),
            "updated_at": state.updated_at.isoformat() if hasattr(state.updated_at, "isoformat") else str(state.updated_at),
        }
    
    # ========================================================================
    # Management Handlers
    # ========================================================================
    
    async def _handle_list_sessions(
        self,
        status: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        List all workflow sessions with optional status filtering.
        
        Args:
            status: Optional status filter ("active", "completed", "error", or None for all)
            
        Returns:
            Dict with sessions list and count
            
        Raises:
            ValueError: If status filter invalid
        """
        # Validate status filter
        valid_statuses = {"active", "completed", "error"}
        if status and status not in valid_statuses:
            raise ValueError(
                f"Invalid status filter: {status}. "
                f"Must be one of: {', '.join(sorted(valid_statuses))}"
            )
        
        # Get sessions via WorkflowEngine (uses SessionStateHelper)
        sessions = self.workflow_engine.list_sessions(status=status)
        
        # Sessions are already in dict format with all fields
        # Just format for API response
        formatted_sessions = []
        for session in sessions:
            formatted_sessions.append({
                "session_id": session["session_id"],
                "workflow_type": session["workflow_type"],
                "session_status": session["status"],
                "current_phase": session["current_phase"],
                "target_file": session["target_file"],
                "created_at": session["updated_at"],  # Using updated_at as proxy for created
                "updated_at": session["updated_at"],
                "is_complete": session["is_complete"],
                "completed_phases": session["completed_phases"],
            })
        
        return {
            "sessions": formatted_sessions,
            "count": len(formatted_sessions),
        }
    
    async def _handle_get_session(
        self,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get detailed session information.
        
        Args:
            session_id: Session identifier (required)
            
        Returns:
            Dict with detailed session info
            
        Raises:
            ValueError: If session_id missing or invalid
        """
        if not session_id:
            raise ValueError("get_session action requires session_id parameter")
        
        # Validate session ID format
        self._validate_session_id(session_id)
        
        # Load session state
        state = self.workflow_engine._state_helper.load(session_id)
        if not state:
            raise ValueError(f"Session not found: {session_id}")
        
        # Compute session status
        # Check if workflow is complete
        is_complete = (
            len(state.completed_phases) > 0 
            and state.current_phase > max(state.completed_phases)
        )
        
        if is_complete:
            computed_status = "completed"
        elif state.metadata.get("paused", False):
            computed_status = "paused"
        elif any(
            checkpoint.value == "failed"
            for checkpoint in state.checkpoints.values()
        ):
            computed_status = "error"
        else:
            computed_status = "active"
        
        return {
            "session_id": state.session_id,
            "workflow_type": state.workflow_type,
            "session_status": computed_status,
            "current_phase": state.current_phase,
            "target_file": state.target_file,
            "created_at": (
                state.created_at.isoformat()
                if hasattr(state.created_at, "isoformat")
                else str(state.created_at)
            ),
            "updated_at": (
                state.updated_at.isoformat()
                if hasattr(state.updated_at, "isoformat")
                else str(state.updated_at)
            ),
            "checkpoints": {
                phase: checkpoint.value for phase, checkpoint in state.checkpoints.items()
            },
            "artifacts": {
                phase: (
                    artifact.model_dump() if hasattr(artifact, "model_dump") else artifact
                )
                for phase, artifact in state.phase_artifacts.items()
            },
        }
    
    async def _handle_delete_session(
        self,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Delete workflow session and cleanup state.
        
        Args:
            session_id: Session identifier (required)
            
        Returns:
            Dict confirming deletion
            
        Raises:
            ValueError: If session_id missing or invalid
        """
        if not session_id:
            raise ValueError("delete_session action requires session_id parameter")
        
        # Validate session ID format
        self._validate_session_id(session_id)
        
        # P0 FIX: Use proper abstraction instead of direct filesystem manipulation
        # WorkflowEngine.delete_session() → SessionStateHelper.delete() → SessionMapper
        deleted = self.workflow_engine.delete_session(session_id)
        
        if not deleted:
            raise ValueError(f"Session {session_id} not found")
        
        return {
            "session_id": session_id,
            "deleted": True,
            "message": "Session marked for deletion (moved to error status)"
        }
    
    # ========================================================================
    # Recovery Handlers (stubs)
    # ========================================================================
    
    async def _handle_pause(
        self,
        session_id: Optional[str] = None,
        reason: Optional[str] = None,
        checkpoint_note: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Pause workflow session (stub)."""
        raise NotImplementedError("pause action not yet implemented - will be added in Phase 7")
    
    async def _handle_resume(
        self,
        session_id: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Resume paused workflow session (stub)."""
        raise NotImplementedError("resume action not yet implemented - will be added in Phase 7")
    
    async def _handle_retry_phase(
        self,
        session_id: Optional[str] = None,
        phase: Optional[int] = None,
        reset_evidence: Optional[bool] = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Retry failed phase (stub)."""
        raise NotImplementedError("retry_phase action not yet implemented - will be added in Phase 7")
    
    async def _handle_rollback(
        self,
        session_id: Optional[str] = None,
        to_phase: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Rollback to previous phase (stub)."""
        raise NotImplementedError("rollback action not yet implemented - will be added in Phase 7")
    
    async def _handle_get_errors(
        self,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get workflow errors (stub)."""
        raise NotImplementedError("get_errors action not yet implemented - will be added in Phase 7")
    
    # ========================================================================
    # Validation Utilities
    # ========================================================================
    
    def _validate_session_id(self, session_id: str) -> None:
        """
        Validate session ID format for security.
        
        Prevents directory traversal and command injection attacks.
        
        Args:
            session_id: Session identifier to validate
            
        Raises:
            ValueError: If session ID format is invalid
        """
        # UUID format: 8-4-4-4-12 hex characters
        # Allow alphanumeric + hyphens only (no path separators or special chars)
        if not session_id or len(session_id) > 64:
            raise ValueError(f"Invalid session_id format: {session_id}")
        
        if ".." in session_id or "/" in session_id or "\\" in session_id:
            raise ValueError(f"Invalid session_id: {session_id} (contains path separators)")
    
    def _validate_evidence_size(self, evidence: Dict[str, Any]) -> None:
        """
        Validate evidence dictionary size to prevent DoS.
        
        Args:
            evidence: Evidence dictionary to validate
            
        Raises:
            ValueError: If evidence exceeds size limits
        """
        evidence_json = json.dumps(evidence)
        evidence_size = len(evidence_json)
        
        # Limit: 1MB (adjust based on requirements)
        max_size = 1024 * 1024
        if evidence_size > max_size:
            raise ValueError(
                f"Evidence too large: {evidence_size} bytes (max: {max_size}). "
                "Consider splitting into smaller chunks or providing file paths instead."
            )


def register_workflow_tool(mcp: Any, workflow_engine: Any) -> int:
    """
    Register pos_workflow tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        workflow_engine: WorkflowEngine instance for workflow operations
        
    Returns:
        int: Number of tools registered (always 1)
        
    Traceability:
        FR-006: pos_workflow tool registration
        FR-010: Tool auto-discovery pattern
    """
    # Create tool instance
    tool_instance = WorkflowTool(mcp=mcp, workflow_engine=workflow_engine)
    
    # Register the tool (accessing the @mcp.tool() decorated function)
    _ = tool_instance.tool
    
    logger.info("✅ Registered pos_workflow tool (14 actions) using ActionDispatchMixin")
    return 1  # One tool registered


__all__ = ["register_workflow_tool", "WorkflowTool"]


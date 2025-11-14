"""
Base classes and mixins for MCP tools.

Provides common patterns for action-based dispatch tools, reducing boilerplate
and ensuring consistent error handling, validation, and response formatting.

Architecture:
    ActionDispatchMixin provides:
    - Action validation
    - Handler dispatch with error wrapping
    - Standard response envelopes (success/error)
    - Logging integration
    - Consistent error formatting

    Tools inherit from ActionDispatchMixin and implement:
    - @mcp.tool() decorated methods
    - Action handler methods (async def _handle_*)
    - Action → handler mapping dict

Example:
    >>> class WorkflowTool(ActionDispatchMixin):
    ...     def __init__(self, mcp, workflow_engine):
    ...         super().__init__(mcp)
    ...         self.workflow_engine = workflow_engine
    ...         self.handlers = {
    ...             "start": self._handle_start,
    ...             "get_phase": self._handle_get_phase,
    ...         }
    ...     
    ...     @mcp.tool()
    ...     async def pos_workflow(self, action: Literal[...], **kwargs):
    ...         return await self.dispatch(action, self.handlers, **kwargs)
    ...     
    ...     async def _handle_start(self, workflow_type, **kwargs):
    ...         # Pure business logic, no boilerplate
    ...         result = self.workflow_engine.start_workflow(...)
    ...         return {"session_id": result["session_id"]}

Benefits:
    - DRY: Dispatch logic in ONE place
    - Testable: Mock subsystems easily
    - Maintainable: Changes to dispatch don't affect handlers
    - Clean: Handlers focus on business logic only
    - Consistent: All tools have same error format

Traceability:
    Design Decision: Mixin pattern for tool action dispatch
    Benefits: Code reduction, consistency, maintainability
"""

import logging
from typing import Any, Callable, Dict, Optional, Set

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class ActionDispatchMixin:
    """
    Mixin providing common action-based dispatch behavior for MCP tools.
    
    Provides:
    - Action validation against allowed set
    - Handler lookup and invocation
    - Error handling with standard envelopes
    - Success/error response formatting
    - Logging integration
    
    Usage:
        1. Inherit from this mixin
        2. Define self.handlers dict (action → handler function)
        3. Call self.dispatch(action, self.handlers, **kwargs) from tool
    
    Attributes:
        mcp: FastMCP server instance (for tool registration)
    """
    
    def __init__(self, mcp: FastMCP, query_tracker: Optional[Any] = None):
        """
        Initialize mixin with MCP server reference and optional QueryTracker.
        
        Args:
            mcp: FastMCP server instance
            query_tracker: Optional QueryTracker for behavioral metrics
        """
        self.mcp = mcp
        self.query_tracker = query_tracker
        logger.debug("ActionDispatchMixin initialized", extra={"class": self.__class__.__name__})
    
    def validate_action(self, action: str, valid_actions: Set[str]) -> None:
        """
        Validate action is in allowed set.
        
        Args:
            action: Action string to validate
            valid_actions: Set of allowed actions
        
        Raises:
            ValueError: If action not in valid_actions
        
        Example:
            >>> self.validate_action("start", {"start", "stop"})
            >>> # OK
            >>> self.validate_action("invalid", {"start", "stop"})
            ValueError: Invalid action: 'invalid'. Must be one of: start, stop
        """
        if action not in valid_actions:
            valid_list = ", ".join(sorted(valid_actions))
            raise ValueError(
                f"Invalid action: '{action}'. Must be one of: {valid_list}"
            )
    
    async def dispatch(
        self,
        action: str,
        handlers: Dict[str, Callable],
        query: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Dispatch action to appropriate handler with error wrapping.
        
        Provides:
        - Handler lookup
        - Async invocation
        - Error catching and formatting
        - Standard response envelopes
        - Logging
        - Query tracking (if QueryTracker available)
        
        Args:
            action: Action to dispatch
            handlers: Dict mapping action strings to handler functions
            query: Optional query string for QueryTracker integration
            session_id: Optional session ID for QueryTracker integration
            **kwargs: Arguments to pass to handler
        
        Returns:
            Standard response dict:
            - Success: {"status": "success", "action": "...", ...handler_result}
            - Error: {"status": "error", "action": "...", "error": "...", "error_type": "..."}
        
        Example:
            >>> handlers = {"start": self._handle_start}
            >>> result = await self.dispatch("start", handlers, workflow_type="spec")
            >>> # Returns: {"status": "success", "action": "start", "session_id": "..."}
        """
        logger.info(
            "Dispatching action",
            extra={
                "action": action,
                "tool_class": self.__class__.__name__,
                "kwargs_keys": list(kwargs.keys()),
            }
        )
        
        # Extract task_session_id once (used for both tracking and prepend generation)
        task_session_id = None
        if self.query_tracker and query:
            try:
                # Extract dynamic session ID for task boundaries (prepend)
                from ouroboros.middleware.session_id_extractor import extract_session_id
                
                # Two session concepts:
                # 1. agent_session_id: Long-lived (entire conversation) - for behavioral metrics
                # 2. task_session_id: Short-lived (per user request with timeout) - for prepend gamification
                agent_session_id = session_id or "default_session"
                task_session_id = extract_session_id(client_id=agent_session_id)
                
                # Record in QueryTracker under BOTH sessions:
                # - agent_session for long-term behavioral tracking
                # - task_session for prepend query counts (resets on timeout)
                self.query_tracker.record_query(agent_session_id, query)
                self.query_tracker.record_query(task_session_id, query)
                
                logger.debug(
                    "Query tracked",
                    extra={
                        "agent_session": agent_session_id,
                        "task_session": task_session_id,
                        "query": query[:50]
                    }
                )
            except Exception as e:
                # Non-critical, don't fail dispatch
                logger.warning("Failed to track query: %s", e)
        
        try:
            # Validate handler exists
            handler = handlers.get(action)
            if not handler:
                raise ValueError(
                    f"No handler registered for action: '{action}'. "
                    f"Available actions: {', '.join(sorted(handlers.keys()))}"
                )
            
            # Reconstruct handler kwargs (include query, session_id, and task_session_id if provided)
            handler_kwargs = dict(kwargs)
            if query is not None:
                handler_kwargs['query'] = query
            if session_id is not None:
                handler_kwargs['session_id'] = session_id
            if task_session_id is not None:
                handler_kwargs['task_session_id'] = task_session_id
            
            # Invoke handler (may be sync or async)
            if callable(handler):
                result = handler(**handler_kwargs)
                # Await if coroutine
                if hasattr(result, "__await__"):
                    result = await result
            else:
                raise TypeError(f"Handler for '{action}' is not callable: {handler}")
            
            # Wrap in success envelope
            response = self.success_response(action, result)
            
            logger.debug(
                "Action dispatched successfully",
                extra={
                    "action": action,
                    "tool_class": self.__class__.__name__,
                }
            )
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                "Action dispatch failed",
                extra={
                    "action": action,
                    "tool_class": self.__class__.__name__,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True
            )
            
            # Return error envelope
            return self.error_response(action, e)
    
    def success_response(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create standard success response envelope.
        
        Args:
            action: Action that succeeded
            data: Handler result data (will be merged into response)
        
        Returns:
            Dict with:
            - status: "success"
            - action: echoed action string
            - **data: handler result merged in
        
        Example:
            >>> self.success_response("start", {"session_id": "abc"})
            {"status": "success", "action": "start", "session_id": "abc"}
        """
        return {
            "status": "success",
            "action": action,
            **data
        }
    
    def error_response(
        self,
        action: str,
        error: Exception,
        remediation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standard error response envelope.
        
        Args:
            action: Action that failed
            error: Exception that was raised
            remediation: Optional remediation hint for user
        
        Returns:
            Dict with:
            - status: "error"
            - action: echoed action string
            - error: error message
            - error_type: exception class name
            - remediation: optional fix hint
        
        Example:
            >>> try:
            ...     raise ValueError("Invalid workflow type")
            ... except Exception as e:
            ...     self.error_response("start", e, "Check workflow exists")
            {
                "status": "error",
                "action": "start",
                "error": "Invalid workflow type",
                "error_type": "ValueError",
                "remediation": "Check workflow exists"
            }
        """
        response = {
            "status": "error",
            "action": action,
            "error": str(error),
            "error_type": type(error).__name__,
        }
        
        # Add remediation if provided or if ActionableError
        if remediation:
            response["remediation"] = remediation
        elif hasattr(error, "how_to_fix") and hasattr(error, "what_failed"):
            # ActionableError has structured remediation
            response["remediation"] = getattr(error, "how_to_fix", "Check server logs")
        else:
            # Generic remediation
            response["remediation"] = "Check server logs for detailed error information"
        
        return response
    
    def validate_required_params(
        self,
        params: Dict[str, Any],
        required: list[str]
    ) -> None:
        """
        Validate required parameters are present and not None.
        
        Args:
            params: Parameters dict to validate
            required: List of required parameter names
        
        Raises:
            ValueError: If any required parameter is missing or None
        
        Example:
            >>> params = {"workflow_type": "spec", "target_file": None}
            >>> self.validate_required_params(params, ["workflow_type", "target_file"])
            ValueError: Missing or empty required parameters: target_file
        """
        missing = [
            param for param in required
            if param not in params or params[param] is None
        ]
        
        if missing:
            raise ValueError(
                f"Missing or empty required parameters: {', '.join(missing)}"
            )


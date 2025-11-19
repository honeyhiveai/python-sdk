"""
pos_search_project: Unified search tool for project knowledge.

Provides a single consolidated tool for all search operations across:
- Standards documentation (hybrid search: vector + FTS + RRF)
- Code semantic search (CodeBERT embeddings)  
- AST structural search (Tree-sitter patterns)
- Call graph traversal (find_callers, find_dependencies, find_call_paths)

Architecture:
    AI Agent → pos_search_project (Tools Layer)
        ↓
    Middleware (query_tracker + prepend_generator)
        ↓
    IndexManager (RAG Subsystem)
        ↓
    ├─ StandardsIndex
    ├─ CodeIndex
    ├─ ASTIndex
    └─ GraphIndex

Traceability:
    FR-005: pos_search_project - Unified Search Tool
    FR-011: Standards Search (hybrid)
    FR-012: Code Semantic Search
    FR-013: Code Graph Traversal
    FR-014: AST Structural Search
"""

# pylint: disable=broad-exception-caught
# Justification: Top-level MCP tool must catch all exceptions to return
# structured error responses to AI agents, preventing tool crashes

import logging
from typing import Any, Dict, List, Literal, Optional

from ouroboros.middleware.prepend_generator import PrependGenerator
from ouroboros.tools.base import ActionDispatchMixin

logger = logging.getLogger(__name__)


class SearchTool(ActionDispatchMixin):
    """
    Unified search tool using ActionDispatchMixin pattern.
    
    Provides search across standards, code, AST, and graph indexes.
    """
    
    def __init__(self, mcp: Any, index_manager: Any, query_tracker: Optional[Any] = None):
        """Initialize with IndexManager and optional QueryTracker."""
        super().__init__(mcp, query_tracker)  # Pass query_tracker to mixin
        self.index_manager = index_manager
        
        # Initialize prepend generator if query_tracker available
        self.prepend_generator = PrependGenerator(query_tracker) if query_tracker else None
        
        # Define action handlers
        self.handlers = {
            "search_standards": self._handle_search_standards,
            "search_code": self._handle_search_code,
            "search_ast": self._handle_search_ast,
            "find_callers": self._handle_find_callers,
            "find_dependencies": self._handle_find_dependencies,
            "find_call_paths": self._handle_find_call_paths,
        }
    
    @property
    def tool(self):
        """Return the MCP tool decorator wrapper."""
        @self.mcp.tool()
        async def pos_search_project(
            action: Literal[
                "search_standards",      # Hybrid search standards docs (vector + FTS + RRF)
                "search_code",           # Semantic code search (CodeBERT embeddings)
                "search_ast",            # Structural AST search (Tree-sitter patterns)
                "find_callers",          # Graph: who calls this symbol?
                "find_dependencies",     # Graph: what does this symbol call?
                "find_call_paths"        # Graph: show call chain symbol_a → symbol_b
            ],
            query: str,
            method: Literal["hybrid", "vector", "fts"] = "hybrid",
            n_results: int = 3,
            max_depth: int = 10,          # For graph traversal actions
            to_symbol: Optional[str] = None,  # For find_call_paths
            filters: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """
            Unified search across all project knowledge.
            
            Routes search queries to the appropriate index based on action:
            - search_standards → StandardsIndex (hybrid: vector + FTS + RRF + rerank)
            - search_code → CodeIndex (semantic: CodeBERT embeddings)
            - search_ast → ASTIndex (structural: Tree-sitter syntax patterns)
            - find_callers → GraphIndex (recursive CTE: who calls this?)
            - find_dependencies → GraphIndex (recursive CTE: what does this call?)
            - find_call_paths → GraphIndex (recursive CTE: call chain A→B)
            
            Middleware Integration:
            - Query tracking: Records all searches for behavioral analysis
            - Prepend generation: Adds progress/suggestions to first result
            - Session extraction: Automatic conversation ID detection
            
            Args:
                action: Search operation to perform (required)
                query: Search query or symbol name (required)
                method: Search method for content actions (hybrid/vector/fts)
                       Default: "hybrid" (combines vector + FTS via RRF)
                n_results: Number of results to return (default: 3)
                max_depth: Maximum traversal depth for graph actions (default: 10)
                to_symbol: Target symbol for find_call_paths (required for that action)
                filters: Optional metadata filters (e.g., {"phase": 2, "tags": ["async"]})
                
            Returns:
                Dictionary with:
                - status: "success" or "error"
                - action: Echoed action parameter
                - results: List of search results
                - count: Number of results returned
                - metadata: Query metadata (tokens, time, method, etc.)
                
            Examples:
                >>> # Search standards docs
                >>> pos_search_project(
                ...     action="search_standards",
                ...     query="How does the workflow system work?",
                ...     n_results=3
                ... )
                
                >>> # Find who calls a function
                >>> pos_search_project(
                ...     action="find_callers",
                ...     query="process_workflow_phase",
                ...     max_depth=5
                ... )
                
                >>> # Find call path between two functions
                >>> pos_search_project(
                ...     action="find_call_paths",
                ...     query="start_workflow",
                ...     to_symbol="execute_phase",
                ...     max_depth=10
                ... )
            
            Raises:
                ValueError: If action is invalid or required parameters missing
                IndexError: If requested index is not available
                
            Traceability:
                FR-005: pos_search_project - Unified Search Tool
                FR-011: Standards Search
                FR-012: Code Semantic Search
                FR-013: Code Graph Traversal
                FR-014: AST Structural Search
            """
            return await self.dispatch(
                action,
                self.handlers,  # type: ignore[arg-type]
                query=query,
                method=method,
                n_results=n_results,
                max_depth=max_depth,
                to_symbol=to_symbol,
                filters=filters
            )
        
        return pos_search_project
    
    # ========================================================================
    # Action Handlers (delegate to IndexManager)
    # ========================================================================
    
    def _handle_search_standards(
        self, query: str, n_results: int = 3, filters: Optional[Dict] = None, session_id: Optional[str] = None, task_session_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Search standards documentation."""
        # Let the index handle graceful degradation - don't block on health checks
        
        params = {"query": query, "n_results": n_results}
        if filters:
            params["filters"] = filters
        result = self.index_manager.route_action("search_standards", **params)
        
        # Add prepend to all results if prepend generator available and results exist
        if self.prepend_generator and result.get("results") and len(result["results"]) > 0:
            try:
                # Use task session ID (short-lived with timeout) for prepend gamification
                # task_session_id is extracted once in base.py dispatch() and passed here
                if task_session_id:
                    prepend = self.prepend_generator.generate(task_session_id, query)
                    # Prepend to all results that have content field
                    for res in result["results"]:
                        if isinstance(res, dict) and "content" in res and res.get("content"):
                            res["content"] = prepend + res["content"]
            except Exception as e:
                logger.warning("Failed to generate prepend: %s", e)
        
        return result  # type: ignore[no-any-return]
    
    def _handle_search_code(
        self, query: str, n_results: int = 3, filters: Optional[Dict] = None, session_id: Optional[str] = None, task_session_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Search code semantically."""
        # Let the index handle graceful degradation - don't block on health checks
        
        params = {"query": query, "n_results": n_results}
        if filters:
            params["filters"] = filters
        result = self.index_manager.route_action("search_code", **params)
        
        # Add prepend to all results if prepend generator available and results exist
        if self.prepend_generator and result.get("results") and len(result["results"]) > 0:
            try:
                # Use task session ID (short-lived with timeout) for prepend gamification
                # task_session_id is extracted once in base.py dispatch() and passed here
                if task_session_id:
                    prepend = self.prepend_generator.generate(task_session_id, query)
                    # Prepend to all results that have content field
                    for res in result["results"]:
                        if isinstance(res, dict) and "content" in res and res.get("content"):
                            res["content"] = prepend + res["content"]
            except Exception as e:
                logger.warning("Failed to generate prepend: %s", e)
        
        return result  # type: ignore[no-any-return]
    
    def _handle_search_ast(
        self, query: str, n_results: int = 3, filters: Optional[Dict] = None, session_id: Optional[str] = None, task_session_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Search AST structures."""
        # Let the index handle graceful degradation - don't block on health checks
        
        params = {"query": query, "n_results": n_results}
        if filters:
            params["filters"] = filters
        result = self.index_manager.route_action("search_ast", **params)
        
        # Add prepend to all results if prepend generator available and results exist
        if self.prepend_generator and result.get("results") and len(result["results"]) > 0:
            try:
                # Use task session ID (short-lived with timeout) for prepend gamification
                # task_session_id is extracted once in base.py dispatch() and passed here
                if task_session_id:
                    prepend = self.prepend_generator.generate(task_session_id, query)
                    # Prepend to all results that have content field
                    for res in result["results"]:
                        if isinstance(res, dict) and "content" in res and res.get("content"):
                            res["content"] = prepend + res["content"]
            except Exception as e:
                logger.warning("Failed to generate prepend: %s", e)
        
        return result  # type: ignore[no-any-return]
    
    def _handle_find_callers(
        self, query: str, max_depth: int = 10, filters: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Find who calls a symbol."""
        # Let the index handle graceful degradation - don't block on health checks
        
        # Extract partition from filters for multi-repo mode
        partition = None
        if filters and isinstance(filters, dict):
            partition = filters.get("partition")
        
        return self.index_manager.route_action(  # type: ignore[no-any-return]
            "find_callers",
            symbol_name=query,
            max_depth=max_depth,
            partition=partition
        )
    
    def _handle_find_dependencies(
        self, query: str, max_depth: int = 10, filters: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Find what a symbol calls."""
        # Let the index handle graceful degradation - don't block on health checks
        
        # Extract partition from filters for multi-repo mode
        partition = None
        if filters and isinstance(filters, dict):
            partition = filters.get("partition")
        
        return self.index_manager.route_action(  # type: ignore[no-any-return]
            "find_dependencies",
            symbol_name=query,
            max_depth=max_depth,
            partition=partition
        )
    
    def _handle_find_call_paths(
        self, query: str, to_symbol: Optional[str], max_depth: int = 10, filters: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Find call path between two symbols."""
        # Let the index handle graceful degradation - don't block on health checks
        
        if not to_symbol:
            raise ValueError(
                "find_call_paths requires 'to_symbol' parameter. "
                "Provide to_symbol parameter: "
                "pos_search_project(action='find_call_paths', query='start', to_symbol='end')"
            )
        
        # Extract partition from filters for multi-repo mode
        partition = None
        if filters and isinstance(filters, dict):
            partition = filters.get("partition")
        
        return self.index_manager.route_action(  # type: ignore[no-any-return]
            "find_call_paths",
            from_symbol=query,
            to_symbol=to_symbol,
            max_depth=max_depth,
            partition=partition
        )


def register_search_tool(
    mcp: Any, index_manager: Any, query_tracker: Optional[Any] = None
) -> int:
    """
    Register pos_search_project tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        index_manager: IndexManager instance for routing search actions
        query_tracker: Optional QueryTracker for behavioral metrics
        
    Returns:
        int: Number of tools registered (always 1)
        
    Traceability:
        FR-005: pos_search_project tool registration
        FR-010: Tool auto-discovery pattern
    """
    # Create tool instance
    tool_instance = SearchTool(
        mcp=mcp, index_manager=index_manager, query_tracker=query_tracker
    )
    
    # Register the tool (accessing the @mcp.tool() decorated function)
    _ = tool_instance.tool
    
    logger.info("✅ Registered pos_search_project tool (6 actions) using ActionDispatchMixin")
    return 1  # One tool registered


__all__ = ["register_search_tool", "SearchTool"]


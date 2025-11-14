"""
Tools Layer: MCP tools exposing subsystems to AI agents.

Provides unified, action-based tools that follow domain abstraction patterns:
- pos_search_project: Unified search (6 actions across 4 indexes)
- pos_workflow: Workflow management (14 actions for lifecycle)
- pos_browser: Browser automation (24 actions for Playwright)
- pos_filesystem: File operations (12 actions for CRUD)
- get_server_info: Server status/health/metrics

Architecture:
    AI Agent (Claude, GPT-4, etc.)
        ↓ MCP Protocol
    ToolRegistry (Auto-Discovery)
        ↓
    Tools Layer (this module)
        ↓ Middleware (query_tracker, prepend_generator, session_mapper)
    Subsystems Layer (RAG, Workflow, Browser)
        ↓
    Foundation Layer (Config, Utils, Errors)

Design Principles:
- **Pluggable Architecture:** Tools auto-discovered via ToolRegistry
- Action-based dispatch (single tool, multiple actions)
- Literal type hints (generates JSON Schema enum for AI)
- Middleware integration (100% of tool calls tracked)
- Subsystem delegation (tools are thin wrappers)
- ActionableError (consistent error handling)

Auto-Discovery Pattern:
    Each tool module exports a `register_*_tool()` function.
    ToolRegistry scans tools/ directory, imports modules,
    and calls registration functions with dependency injection.
    
    New tools can be added by dropping a file in tools/ - no code changes needed!

Example:
    >>> from ouroboros.tools.registry import ToolRegistry
    >>> from pathlib import Path
    >>> from fastmcp import FastMCP
    >>> 
    >>> mcp = FastMCP("praxis-os")
    >>> tools_dir = Path("ouroboros/tools")
    >>> 
    >>> registry = ToolRegistry(
    ...     tools_dir=tools_dir,
    ...     mcp_server=mcp,
    ...     dependencies={
    ...         "index_manager": index_manager,
    ...         "workflow_engine": workflow_engine,
    ...         "browser_manager": browser_manager,
    ...         "session_mapper": session_mapper,
    ...         "query_tracker": query_tracker,
    ...     }
    ... )
    >>> 
    >>> results = registry.register_all()
    >>> print(f"Registered {results['tools_registered']} tools")

Traceability:
    FR-005: pos_search_project
    FR-006: pos_workflow
    FR-007: pos_browser
    FR-008: pos_filesystem
    FR-009: get_server_info
    FR-010: Tool Auto-Discovery (ToolRegistry)
"""

from ouroboros.tools.registry import ToolRegistry

__all__ = [
    "ToolRegistry",
]


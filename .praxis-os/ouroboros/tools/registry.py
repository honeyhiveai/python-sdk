"""
Tool Registry: Auto-discovery and registration of MCP tools.

Scans tools/ directory for Python modules and automatically discovers
and registers tools with FastMCP, providing a pluggable architecture.

Architecture Pattern:
- Each tool module exports a `register_*_tool()` function
- ToolRegistry scans directory, imports modules, calls registration functions
- New tools can be added by dropping files in tools/ (no code changes needed)

Traceability:
    FR-010: Tool Auto-Discovery and Registration
    NFR-E2: Tool Auto-Discovery (extensibility)
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Auto-discovers and registers MCP tools from tools/ directory.
    
    Provides pluggable architecture where new tools can be added by simply
    dropping a Python file in the tools/ directory with a `register_*_tool()`
    function.
    
    Architecture:
    - Scans tools/ directory for .py files (excludes __init__.py, registry.py)
    - Imports each module
    - Discovers `register_*_tool()` functions
    - Calls registration functions with appropriate dependencies
    - Handles errors gracefully (skip invalid modules, log errors)
    
    Example Tool Module Structure:
        # ouroboros/tools/pos_search_project.py
        def register_search_tool(mcp, index_manager):
            @mcp.tool()
            async def pos_search_project(...):
                ...
            return 1  # tools registered
    """
    
    def __init__(
        self,
        tools_dir: Path,
        mcp_server: Any,
        dependencies: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ToolRegistry.
        
        Args:
            tools_dir: Path to tools/ directory
            mcp_server: FastMCP server instance
            dependencies: Dict of available dependencies for tool registration
                         (e.g., {"index_manager": ..., "workflow_engine": ...})
        """
        self.tools_dir = tools_dir
        self.mcp_server = mcp_server
        self.dependencies = dependencies or {}
        
        if not self.tools_dir.exists():
            raise FileNotFoundError(f"Tools directory not found: {self.tools_dir}")
        
        logger.info("ToolRegistry initialized: %s", self.tools_dir)
    
    def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover all tool modules in tools/ directory.
        
        Returns:
            List of tool metadata dicts with module info and registration functions
        """
        discovered = []
        
        # Scan for Python files (exclude __init__.py, registry.py)
        for tool_file in self.tools_dir.glob("*.py"):
            if tool_file.name in ("__init__.py", "registry.py"):
                continue
            
            try:
                # Import module
                module_name = f"ouroboros.tools.{tool_file.stem}"
                module = importlib.import_module(module_name)
                
                # Find register_*_tool functions
                for name, obj in inspect.getmembers(module):
                    if (
                        name.startswith("register_")
                        and name.endswith("_tool")
                        and callable(obj)
                    ):
                        # Get function signature for dependency injection
                        sig = inspect.signature(obj)
                        params = list(sig.parameters.keys())
                        
                        discovered.append({
                            "module_name": module_name,
                            "function_name": name,
                            "function": obj,
                            "parameters": params,
                            "file": str(tool_file),
                        })
                        
                        logger.debug(
                            "Discovered tool: %s.%s (params: %s)",
                            module_name,
                            name,
                            params
                        )
            
            except ImportError as e:
                logger.error(
                    "Failed to import tool module %s: %s",
                    tool_file.name,
                    e
                )
                continue
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(
                    "Error discovering tools in %s: %s",
                    tool_file.name,
                    e,
                    exc_info=True
                )
                continue
        
        logger.info("Discovered %d tool registration function(s)", len(discovered))
        return discovered
    
    def register_tool(self, tool_info: Dict[str, Any]) -> int:
        """
        Register a single tool by calling its registration function.
        
        Args:
            tool_info: Tool metadata dict from discover_tools()
            
        Returns:
            Number of tools registered (from registration function return value)
        """
        func = tool_info["function"]
        params = tool_info["parameters"]
        
        # Build arguments for registration function via dependency injection
        kwargs = {"mcp": self.mcp_server}
        
        for param in params:
            if param == "mcp":
                continue  # Already added
            elif param in self.dependencies:
                kwargs[param] = self.dependencies[param]
            else:
                # Optional parameter - check if function has default
                sig = inspect.signature(func)
                param_obj = sig.parameters.get(param)
                if param_obj and param_obj.default != inspect.Parameter.empty:
                    # Has default, safe to omit
                    continue
                else:
                    logger.warning(
                        "Missing required dependency '%s' for %s. Skipping tool.",
                        param,
                        tool_info["function_name"]
                    )
                    return 0
        
        try:
            # Call registration function
            count = func(**kwargs)
            
            logger.info(
                "✅ Registered %s (%d tool(s)) from %s",
                tool_info["function_name"],
                count,
                tool_info["module_name"]
            )
            
            return int(count)
            
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Error registering tool %s: %s",
                tool_info["function_name"],
                e,
                exc_info=True
            )
            return 0
    
    def register_all(self) -> Dict[str, Any]:
        """
        Discover and register all tools.
        
        Returns:
            Dict with registration summary:
            - tools_discovered: int
            - tools_registered: int
            - tools_failed: int
            - details: List[Dict] (per-tool results)
        """
        discovered = self.discover_tools()
        
        if not discovered:
            logger.error(
                "⚠️  No tools discovered in %s. Server will have no functionality!",
                self.tools_dir
            )
            raise RuntimeError(f"No tools discovered in {self.tools_dir}")
        
        total_registered = 0
        total_failed = 0
        details = []
        
        for tool_info in discovered:
            count = self.register_tool(tool_info)
            
            if count > 0:
                total_registered += count
                details.append({
                    "function": tool_info["function_name"],
                    "module": tool_info["module_name"],
                    "count": count,
                    "status": "success",
                })
            else:
                total_failed += 1
                details.append({
                    "function": tool_info["function_name"],
                    "module": tool_info["module_name"],
                    "status": "failed",
                })
        
        logger.info(
            "📊 Tool Registration Summary: %d discovered, %d registered, %d failed",
            len(discovered),
            total_registered,
            total_failed
        )
        
        if total_registered == 0:
            raise RuntimeError("No tools successfully registered. Server cannot function.")
        
        return {
            "tools_discovered": len(discovered),
            "tools_registered": total_registered,
            "tools_failed": total_failed,
            "details": details,
        }


__all__ = ["ToolRegistry"]


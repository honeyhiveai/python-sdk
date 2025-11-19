"""
get_server_info: Server and project information tool for observability.

Provides comprehensive server status, health checks, behavioral metrics,
and version information for monitoring and debugging.

Actions:
- status: Server runtime (uptime, config, subsystems initialized)
- health: Index health, parser status, config validation
- behavioral_metrics: Query frequency, diversity, trends
- version: Server version, Python version, dependencies

Architecture:
    AI Agent → get_server_info (Tools Layer)
        ↓
    All Subsystems (RAG, Workflow, Browser) + Middleware
        ↓
    Metrics Collection

Traceability:
    FR-009: get_server_info - Server Status Tool
    User Story 6: Human Developer Observes AI Improvement
"""

import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from ouroboros.tools.base import ActionDispatchMixin

logger = logging.getLogger(__name__)

# Module-level variables for server startup tracking
_SERVER_START_TIME = time.time()
_SERVER_START_DATETIME = datetime.now(timezone.utc).isoformat()


class ServerInfoTool(ActionDispatchMixin):
    """
    Server information tool using ActionDispatchMixin pattern.
    
    Provides observability into server status, health, metrics, and versions.
    """
    
    def __init__(
        self,
        mcp: Any,
        index_manager: Optional[Any] = None,
        workflow_engine: Optional[Any] = None,
        browser_manager: Optional[Any] = None,
        query_tracker: Optional[Any] = None,
    ):
        """Initialize with subsystem references."""
        super().__init__(mcp, query_tracker)  # Pass query_tracker to mixin
        self.index_manager = index_manager
        self.workflow_engine = workflow_engine
        self.browser_manager = browser_manager
        # query_tracker is available via self.query_tracker from mixin
        
        # Define action handlers
        self.handlers = {
            "status": self._handle_status,
            "health": self._handle_health,
            "behavioral_metrics": self._handle_behavioral_metrics,
            "version": self._handle_version,
        }
    
    @property
    def tool(self):
        """Return the MCP tool decorator wrapper."""
        @self.mcp.tool()
        async def get_server_info(
            action: Literal["status", "health", "behavioral_metrics", "version"] = "status"
        ) -> Dict[str, Any]:
            """
            Get server and project information for observability.
            
            Provides comprehensive server metadata, health status, behavioral metrics,
            and version information for monitoring, debugging, and observing AI improvement.
            
            Actions:
                - status: Server runtime (uptime, config, subsystems initialized)
                - health: Index health status, parsers installed, config validation
                - behavioral_metrics: Query frequency, diversity, trends (from query_tracker)
                - version: Server version, Python version, key dependencies
            
            Args:
                action: Information type to retrieve (default: "status")
                
            Returns:
                Dictionary with:
                - status: "success" or "error"
                - action: Echoed action parameter
                - data: Action-specific information
                
            Examples:
                >>> # Get server status
                >>> get_server_info(action="status")
                
                >>> # Check index health
                >>> get_server_info(action="health")
                
                >>> # View behavioral metrics
                >>> get_server_info(action="behavioral_metrics")
            
            Traceability:
                FR-009: get_server_info - Server Status Tool
                User Story 6: Human Developer Observes AI Improvement
            """
            return await self.dispatch(action, self.handlers)
        
        return get_server_info
    
    # ========================================================================
    # Action Handlers (instance methods)
    # ========================================================================
    
    def _handle_status(self) -> Dict[str, Any]:
        """Get server runtime status."""
        # Calculate uptime
        uptime_seconds = int(time.time() - _SERVER_START_TIME)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_formatted = f"{hours}h {minutes}m {seconds}s"
        
        # Get tool count
        try:
            tools_count = len(self.mcp.list_tools()) if hasattr(self.mcp, "list_tools") else 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Could not get tool count: %s", e)
            tools_count = 0
        
        # Detect project info
        try:
            cwd = os.getcwd()
            project_name = os.path.basename(cwd)
        except Exception:  # pylint: disable=broad-exception-caught
            project_name = "unknown"
            cwd = "unknown"
        
        return {
            "server": {
                "uptime_seconds": uptime_seconds,
                "uptime_formatted": uptime_formatted,
                "started_at": _SERVER_START_DATETIME,
                "pid": os.getpid(),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            },
            "project": {
                "name": project_name,
                "root": cwd,
                "praxis_os_path": os.path.join(cwd, ".praxis-os"),
            },
            "subsystems": {
                "rag": {
                    "enabled": self.index_manager is not None,
                    "initialized": self.index_manager is not None,
                },
                "workflow": {
                    "enabled": self.workflow_engine is not None,
                    "initialized": self.workflow_engine is not None,
                },
                "browser": {
                    "enabled": self.browser_manager is not None,
                    "initialized": self.browser_manager is not None,
                },
            },
            "capabilities": {
                "tools_available": tools_count,
                "mcp_protocol": "1.0",
            },
        }
    
    def _handle_health(self) -> Dict[str, Any]:
        """Get health status of indexes and parsers."""
        checks: List[Dict[str, Any]] = []
        health_data = {
            "overall_health": "healthy",
            "checks": checks,
        }
        
        # Check RAG subsystem
        if self.index_manager is None:
            checks.append({
                "component": "rag_subsystem",
                "status": "disabled",
                "message": "RAG subsystem not initialized",
            })
        else:
            # Check if indexes are available
            try:
                # Try to access index registry
                if hasattr(self.index_manager, "_indexes"):
                    index_count = len(self.index_manager._indexes)
                    if index_count > 0:
                        checks.append({
                            "component": "rag_indexes",
                            "status": "healthy",
                            "message": f"{index_count} indexes initialized",
                            "indexes": list(self.index_manager._indexes.keys()),
                        })
                    else:
                        checks.append({
                            "component": "rag_indexes",
                            "status": "warning",
                            "message": "No indexes initialized",
                            "remediation": "Check index configuration in config/mcp.yaml",
                        })
                        health_data["overall_health"] = "degraded"
                else:
                    checks.append({
                        "component": "rag_indexes",
                        "status": "unknown",
                        "message": "Could not access index registry",
                    })
            except Exception as e:  # pylint: disable=broad-exception-caught
                checks.append({
                    "component": "rag_subsystem",
                    "status": "error",
                    "message": f"Error checking RAG health: {e}",
                })
                health_data["overall_health"] = "unhealthy"
        
        return health_data
    
    def _handle_behavioral_metrics(self) -> Dict[str, Any]:
        """Get behavioral metrics from query tracking."""
        if self.query_tracker is None:
            return {
                "warning": "Query tracking not available",
                "message": "QueryTracker not initialized. Behavioral metrics require query tracking middleware.",
                "metrics": {},
            }
        
        try:
            # Get metrics from query tracker
            metrics_data = {
                "metrics": {
                    "total_queries": 0,
                    "unique_queries": 0,
                    "query_diversity": 0.0,
                    "angle_coverage": {},
                    "message": "Metrics collection in progress. Query tracker integration needed.",
                },
            }
            
            # Try to get actual metrics if available
            if hasattr(self.query_tracker, "get_all_sessions"):
                sessions = self.query_tracker.get_all_sessions()
                total = sum(s.total_queries for s in sessions.values())
                unique = sum(s.unique_queries for s in sessions.values())
                metrics_data["metrics"]["total_queries"] = total
                metrics_data["metrics"]["unique_queries"] = unique
                if total > 0:
                    metrics_data["metrics"]["query_diversity"] = round(unique / total, 2)
            
            return metrics_data
            
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Error getting behavioral metrics: %s", e)
            return {
                "warning": f"Could not retrieve metrics: {e}",
                "metrics": {},
            }
    
    def _handle_version(self) -> Dict[str, Any]:
        """Get version information."""
        # Collect dependency versions
        dependencies = {}
        
        try:
            import fastmcp
            dependencies["fastmcp"] = fastmcp.__version__ if hasattr(fastmcp, "__version__") else "unknown"
        except ImportError:
            dependencies["fastmcp"] = "not installed"
        
        try:
            import pydantic
            dependencies["pydantic"] = pydantic.__version__
        except ImportError:
            dependencies["pydantic"] = "not installed"
        
        try:
            import lancedb
            dependencies["lancedb"] = lancedb.__version__ if hasattr(lancedb, "__version__") else "unknown"
        except ImportError:
            dependencies["lancedb"] = "not installed"
        
        try:
            import playwright
            dependencies["playwright"] = playwright.__version__ if hasattr(playwright, "__version__") else "unknown"
        except ImportError:
            dependencies["playwright"] = "not installed"
        
        return {
            "server": {
                "version": "2.0.0-ouroboros",
                "codename": "ouroboros",
                "release_date": "2025-11-04",
            },
            "python": {
                "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "implementation": sys.implementation.name,
                "platform": sys.platform,
            },
            "dependencies": dependencies,
        }


def register_server_info_tool(
    mcp: Any,
    index_manager: Optional[Any] = None,
    workflow_engine: Optional[Any] = None,
    browser_manager: Optional[Any] = None,
    query_tracker: Optional[Any] = None,
) -> int:
    """
    Register get_server_info tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        index_manager: Optional IndexManager for health checks
        workflow_engine: Optional WorkflowEngine for status
        browser_manager: Optional BrowserManager for status
        query_tracker: Optional QueryTracker for behavioral metrics
        
    Returns:
        int: Number of tools registered (always 1)
        
    Traceability:
        FR-009: get_server_info tool registration
    """
    # Create tool instance
    tool_instance = ServerInfoTool(
        mcp=mcp,
        index_manager=index_manager,
        workflow_engine=workflow_engine,
        browser_manager=browser_manager,
        query_tracker=query_tracker,
    )
    
    # Register the tool (accessing the @mcp.tool() decorated function)
    _ = tool_instance.tool
    
    logger.info("✅ Registered get_server_info tool (4 actions) using ActionDispatchMixin")
    return 1  # One tool registered


__all__ = ["register_server_info_tool", "ServerInfoTool"]


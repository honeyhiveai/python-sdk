"""
MCP tools module with selective loading and performance monitoring.

Provides tool registration with group-based selective loading to avoid
performance degradation (research shows 85% drop with >20 tools).
"""

import logging
from typing import List, Optional, Any

from .rag_tools import register_rag_tools
from .workflow_tools import register_workflow_tools

logger = logging.getLogger(__name__)


def register_all_tools(
    mcp: Any,
    rag_engine: Any,
    workflow_engine: Any,
    framework_generator: Any,
    base_path: Optional[Any] = None,
    enabled_groups: Optional[List[str]] = None,
    max_tools_warning: int = 20,
) -> int:
    """
    Register MCP tools with selective loading and performance monitoring.
    
    Research shows LLM performance degrades by up to 85% with >20 tools.
    This function monitors tool count and enables selective loading.
    
    :param mcp: FastMCP server instance
    :param rag_engine: RAG engine for search tools
    :param workflow_engine: Workflow engine for workflow tools
    :param framework_generator: Generator for create_workflow tool
    :param base_path: Base path for .agent-os (for create_workflow)
    :param enabled_groups: Tool groups to enable (None = default groups)
    :param max_tools_warning: Warning threshold for tool count (default 20)
    :return: Total number of registered tools
    """
    if enabled_groups is None:
        enabled_groups = ["rag", "workflow"]  # Default: core tools only
    
    tool_count = 0
    
    if "rag" in enabled_groups:
        count = register_rag_tools(mcp, rag_engine)
        tool_count += count
        logger.info(f"✅ Registered {count} RAG tool(s)")
    
    if "workflow" in enabled_groups:
        count = register_workflow_tools(mcp, workflow_engine, framework_generator, base_path)
        tool_count += count
        logger.info(f"✅ Registered {count} workflow tool(s)")
    
    # Future: sub-agent tools
    # if "design_validator" in enabled_groups:
    #     from .sub_agent_tools.design_validator import register_design_validator_tools
    #     count = register_design_validator_tools(mcp, ...)
    #     tool_count += count
    #     logger.info(f"✅ Registered {count} design validator tool(s)")
    
    logger.info(f"📊 Total MCP tools registered: {tool_count}")
    
    if tool_count > max_tools_warning:
        logger.warning(
            f"⚠️  Tool count ({tool_count}) exceeds recommended limit ({max_tools_warning}). "
            "LLM performance may degrade by up to 85%. "
            "Consider selective loading via enabled_tool_groups config."
        )
    
    return tool_count


__all__ = [
    "register_all_tools",
    "register_rag_tools",
    "register_workflow_tools",
]

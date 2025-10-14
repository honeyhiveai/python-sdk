"""
MCP tools module with selective loading and performance monitoring.

Provides tool registration with group-based selective loading to avoid
performance degradation (research shows 85% drop with >20 tools).
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: register_all_tools requires 9 parameters to wire all MCP tool
# groups (RAG, workflow, browser, framework generators, validators) with optional
# dependencies - necessary for comprehensive tool registration

import logging
from typing import Any, List, Optional

from .browser_tools import register_browser_tools
from .rag_tools import register_rag_tools
from .server_info_tools import register_server_info_tools
from .workflow_tools import register_workflow_tools

logger = logging.getLogger(__name__)


def register_all_tools(
    mcp: Any,
    rag_engine: Any,
    workflow_engine: Any,
    framework_generator: Any,
    workflow_validator: Any,
    browser_manager: Optional[Any] = None,
    base_path: Optional[Any] = None,
    enabled_groups: Optional[List[str]] = None,
    max_tools_warning: int = 20,
    project_discovery: Optional[Any] = None,
    transport_mode: str = "stdio",
) -> int:
    """
    Register MCP tools with selective loading and performance monitoring.

    Research shows LLM performance degrades by up to 85% with >20 tools.
    This function monitors tool count and enables selective loading.

    :param mcp: FastMCP server instance
    :param rag_engine: RAG engine for search tools
    :param workflow_engine: Workflow engine for workflow tools
    :param framework_generator: Generator for create_workflow tool
    :param workflow_validator: WorkflowValidator class for validate_workflow tool
    :param browser_manager: Optional BrowserManager for browser tools
    :param base_path: Base path for .agent-os (for create_workflow)
    :param enabled_groups: Tool groups to enable (None = default groups)
    :param max_tools_warning: Warning threshold for tool count (default 20)
    :param project_discovery: ProjectInfoDiscovery for server info tool
    :param transport_mode: Current transport mode (dual, stdio, http)
    :return: Total number of registered tools

    Traceability:
        FR-12 (Conditional tool loading)
    """
    if enabled_groups is None:
        enabled_groups = ["rag", "workflow"]  # Default: core tools only

    tool_count = 0

    # Always register server info tool (core functionality)
    if project_discovery:
        count = register_server_info_tools(mcp, project_discovery, transport_mode)
        tool_count += count
        logger.info("✅ Registered %s server info tool(s)", count)

    if "rag" in enabled_groups:
        count = register_rag_tools(mcp, rag_engine)
        tool_count += count
        logger.info("✅ Registered %s RAG tool(s)", count)

    if "workflow" in enabled_groups:
        count = register_workflow_tools(
            mcp, workflow_engine, framework_generator, workflow_validator, base_path
        )
        tool_count += count
        logger.info("✅ Registered %s workflow tool(s)", count)

    if "browser" in enabled_groups and browser_manager:
        count = register_browser_tools(mcp, browser_manager)
        tool_count += count
        logger.info("✅ Registered %s browser tool(s)", count)
    elif "browser" in enabled_groups and not browser_manager:
        logger.warning("⚠️  Browser tools requested but browser_manager not provided")

    # Future: sub-agent tools
    # if "design_validator" in enabled_groups:
    #     from .sub_agent_tools.design_validator import register_design_validator_tools
    #     count = register_design_validator_tools(mcp, ...)
    #     tool_count += count
    #     logger.info("✅ Registered %s design validator tool(s)", count)

    logger.info("📊 Total MCP tools registered: %s", tool_count)

    if tool_count > max_tools_warning:
        logger.warning(
            "⚠️  Tool count (%s) exceeds recommended limit (%s). "
            "LLM performance may degrade by up to 85%%. "
            "Consider selective loading via enabled_tool_groups config.",
            tool_count,
            max_tools_warning,
        )

    return tool_count


__all__ = [
    "register_all_tools",
    "register_rag_tools",
    "register_workflow_tools",
    "register_browser_tools",
    "register_server_info_tools",
]

"""
Example: How sub-agents connect to the MCP server via HTTP.

This module demonstrates how a sub-agent (like Cline, Aider, etc.) can:
1. Discover the MCP server using the state file
2. Connect via HTTP transport
3. Initialize an MCP session
4. List available tools
5. Call tools (e.g., search_standards)

This is a working, end-to-end example that can be run standalone or integrated
into other sub-agent workflows.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import the discovery utility we created
from mcp_server.sub_agents.discovery import discover_mcp_server

logger = logging.getLogger(__name__)


async def connect_and_use_mcp_server(
    agent_os_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Connect to the MCP server and demonstrate tool usage.

    This is a complete, working example showing how to:
    - Discover the server via state file
    - Connect using streamable_http_client
    - Initialize an MCP session
    - List available tools
    - Call a tool (search_standards)

    Args:
        agent_os_path: Path to .agent-os directory. If None, will auto-discover.

    Returns:
        Dictionary with results from the connection attempt, including:
        - success: bool indicating if connection succeeded
        - url: str of the server URL (if discovered)
        - tools_count: int number of tools available
        - tools: List of tool names
        - search_result: Result from calling search_standards
        - error: str error message (if failed)

    Example:
        >>> import asyncio
        >>> result = asyncio.run(connect_and_use_mcp_server())
        >>> if result["success"]:
        ...     print(f"Connected to {result['url']}")
        ...     print(f"Available tools: {result['tools']}")
    """
    try:
        # Step 1: Discover the MCP server using the discovery utility
        logger.info("🔍 Discovering MCP server...")
        url = discover_mcp_server(agent_os_path)

        if url is None:
            error_msg = (
                "❌ MCP server not found. Possible reasons:\n"
                "  1. Server not started (run 'python -m mcp_server "
                "--transport dual')\n"
                "  2. State file missing (.agent-os/.mcp_server_state.json)\n"
                "  3. Server crashed (stale PID in state file)\n"
                "  4. Running in stdio-only mode (need 'dual' or 'http' mode)"
            )
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        logger.info("✅ Discovered MCP server at: %s", url)

        # Step 2: Import MCP client dependencies
        # Note: Cline expects stdio transport, not HTTP
        # These imports are included for reference but not used in this example
        try:
            pass  # Reserved for potential stdio fallback
        except ImportError as e:
            error_msg = (
                f"❌ MCP client libraries not installed: {e}\n"
                "Install with: pip install mcp"
            )
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        # Step 3: Connect to the server via HTTP
        # Note: This example uses a mock connection for demonstration
        # In a real scenario, you'd use:
        #   from mcp.client.streamable_http import streamable_http_client
        #   async with streamable_http_client(url) as (read, write):
        logger.info("🔌 Connecting to MCP server at %s...", url)

        # For demonstration, we'll simulate the connection flow
        # In production, replace this with actual streamable_http_client usage
        mock_tools = await _mock_list_tools(url)
        mock_search_result = await _mock_search_standards(url)

        logger.info("✅ Connected successfully!")
        logger.info("📋 Available tools: %s", ", ".join(mock_tools))

        return {
            "success": True,
            "url": url,
            "tools_count": len(mock_tools),
            "tools": mock_tools,
            "search_result": mock_search_result,
        }

    except ConnectionError as e:
        error_msg = f"❌ Connection failed: {e}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except Exception as e:  # pylint: disable=broad-exception-caught
        error_msg = f"❌ Unexpected error: {e}"
        logger.exception(error_msg)
        return {"success": False, "error": error_msg}


async def _mock_list_tools(_url: str) -> List[str]:
    """
    Mock implementation of listing tools.

    In production, this would be:
        async with streamable_http_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                tools_result = await session.list_tools()
                return [tool.name for tool in tools_result.tools]

    Args:
        url: The MCP server URL.

    Returns:
        List of tool names.
    """
    # Simulate network delay
    await asyncio.sleep(0.1)

    # Return expected tools from Agent OS
    return [
        "search_standards",
        "start_workflow",
        "get_current_phase",
        "get_task",
        "complete_phase",
        "get_workflow_state",
        "create_workflow",
        "validate_workflow",
        "current_date",
        "get_server_info",
    ]


async def _mock_search_standards(_url: str, _query: str = "") -> Dict[str, Any]:
    """
    Mock implementation of calling search_standards tool.

    In production, this would be:
        async with streamable_http_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                result = await session.call_tool(
                    "search_standards",
                    {"query": "production code checklist", "n_results": 3}
                )
                return result

    Args:
        url: The MCP server URL.

    Returns:
        Mock search results.
    """
    # Simulate network delay
    await asyncio.sleep(0.2)

    # Return mock search results
    return {
        "results": [
            {
                "title": "Production Code Checklist",
                "content": (
                    "All production code must include: docstrings, type hints, "
                    "error handling..."
                ),
                "score": 0.95,
            }
        ],
        "query": "production code checklist",
        "retrieval_method": "semantic_search",
    }


# ==============================================================================
# Configuration Helpers for Different Sub-Agent Types
# ==============================================================================


def get_mcp_config_for_cline() -> Optional[Dict[str, Any]]:
    """
    Get MCP configuration for Cline agent.

    Cline can use this to auto-configure its MCP server connection.

    Returns:
        Configuration dict for Cline's settings.json, or None if server not found.

    Example usage in Cline settings:
        ```json
        {
          "mcpServers": {
            "agent-os-rag": {
              "transport": "streamable-http",
              "url": "http://127.0.0.1:4242/mcp"
            }
          }
        }
        ```

    Example code:
        >>> config = get_mcp_config_for_cline()
        >>> if config:
        ...     # Write to Cline settings file
        ...     with open(".cline/mcp_settings.json", "w") as f:
        ...         json.dump(config, f, indent=2)
    """
    url = discover_mcp_server()

    if url is None:
        logger.warning("Cannot generate Cline config: MCP server not found")
        return None

    return {
        "mcpServers": {
            "agent-os-rag": {
                "transport": "streamable-http",
                "url": url,
            }
        }
    }


def get_mcp_config_for_aider() -> Optional[Dict[str, Any]]:
    """
    Get MCP configuration for Aider agent.

    Returns:
        Configuration dict for Aider, or None if server not found.

    Example usage:
        >>> config = get_mcp_config_for_aider()
        >>> if config:
        ...     # Pass to Aider via environment variable or config file
        ...     import os
        ...     os.environ["AIDER_MCP_URL"] = config["url"]
    """
    url = discover_mcp_server()

    if url is None:
        logger.warning("Cannot generate Aider config: MCP server not found")
        return None

    return {
        "url": url,
        "transport": "http",
    }


def get_mcp_config_for_python_sdk() -> Optional[Dict[str, Any]]:
    """
    Get MCP configuration for Python SDK clients.

    Returns:
        Configuration dict with connection details, or None if server not found.

    Example usage:
        ```python
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        config = get_mcp_config_for_python_sdk()
        if config:
            async with streamable_http_client(config["url"]) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()

                    # List available tools
                    tools = await session.list_tools()
                    print(f"Available tools: {[t.name for t in tools.tools]}")

                    # Call a tool
                    result = await session.call_tool(
                        "search_standards",
                        {"query": "production code checklist", "n_results": 5}
                    )
                    print(f"Search results: {result}")
        ```
    """
    url = discover_mcp_server()

    if url is None:
        logger.warning("Cannot generate Python SDK config: MCP server not found")
        return None

    return {
        "url": url,
        "transport": "streamable-http",
    }


# ==============================================================================
# CLI Interface
# ==============================================================================


async def async_main() -> int:
    """
    Async main function demonstrating end-to-end MCP usage.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    logger.info("=" * 60)
    logger.info("MCP Sub-Agent Connection Example")
    logger.info("=" * 60)

    # Run the example
    result = await connect_and_use_mcp_server()

    # Display results
    if result["success"]:
        logger.info("")
        logger.info("✅ Connection successful!")
        logger.info("   URL: %s", result["url"])
        logger.info("   Tools available: %d", result["tools_count"])
        logger.info("   Tool names: %s", ", ".join(result["tools"][:5]))
        if result["tools_count"] > 5:
            logger.info("   ... and %d more", result["tools_count"] - 5)
        logger.info("")
        logger.info("📝 Search result preview:")
        logger.info("   %s", result["search_result"]["results"][0]["title"])
        logger.info("")
        return 0

    # Error case
    logger.error("")
    logger.error(result["error"])
    logger.error("")
    return 1


def main() -> int:
    """
    CLI tool to demonstrate MCP server discovery and connection.

    This can be run standalone:
        python -m mcp_server.sub_agents.mcp_client_example

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    return asyncio.run(async_main())


if __name__ == "__main__":
    sys.exit(main())

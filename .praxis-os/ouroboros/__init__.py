"""
Tool registry for automatic MCP tool discovery and registration.

Provides dynamic tool discovery from the tools/ directory, extracting:
    - Function signatures with type hints
    - Literal type hints for action enums
    - Docstrings for tool descriptions
    - Parameter schemas for MCP registration

The registry scans tools/ at startup and registers all discovered tools
with FastMCP automatically.

Example Usage:
    >>> from ouroboros.registry.loader import ToolRegistry
    >>> from ouroboros.config.loader import load_config
    >>> 
    >>> config = load_config()
    >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
    >>> tools = registry.discover_tools()
    >>> print(f"Discovered {len(tools)} tools")

See Also:
    - loader: ToolRegistry for tool discovery
    - types: ToolDefinition, ToolMetadata for tool metadata
"""

__all__: list[str] = []


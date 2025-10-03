"""
Entry point for Agent OS MCP server when run as a module.

Allows execution via:
    python -m mcp_servers
"""
from .agent_os_rag import main

if __name__ == "__main__":
    main()



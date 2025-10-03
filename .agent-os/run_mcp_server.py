#!/usr/bin/env python3
"""
Standalone entry point for Agent OS MCP server.

This script adds the mcp_servers directory to the Python path,
loads environment variables from .env file, and starts the MCP server.
"""
import sys
import os
from pathlib import Path

# Load .env file from project root
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"

if env_file.exists():
    # Load .env manually (lightweight, no extra dependency)
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            # Remove 'export ' prefix if present
            if line.startswith('export '):
                line = line[7:]  # Remove 'export '
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), value)

# Add mcp_servers directory to path for imports
mcp_servers_dir = Path(__file__).parent / "mcp_servers"
sys.path.insert(0, str(mcp_servers_dir))

# Now we can import with relative paths working
if __name__ == "__main__":
    from agent_os_rag import main
    main()



#!/usr/bin/env python3
"""
Update Cline MCP configuration with current prAxIs OS MCP server port.

This script reads the dynamically allocated port from .praxis-os/.mcp_server_state.json
and updates the Cline MCP settings to connect via HTTP to that port.

Usage:
    python .praxis-os/bin/update-cline-mcp.py

The script will:
1. Read current MCP server port from state file
2. Locate Cline's cline_mcp_settings.json
3. Update or create agent-os-rag server configuration
4. Preserve other MCP server configurations
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def find_mcp_state_file() -> Optional[Path]:
    """
    Find .praxis-os/.mcp_server_state.json in current project.

    :return: Path to state file or None if not found
    """
    # Try current directory
    state_file = Path.cwd() / ".praxis-os" / ".mcp_server_state.json"
    if state_file.exists():
        return state_file

    # Try parent directories (up to 3 levels)
    for parent in Path.cwd().parents[:3]:
        state_file = parent / ".praxis-os" / ".mcp_server_state.json"
        if state_file.exists():
            return state_file

    return None


def read_mcp_state(state_file: Path) -> Dict[str, Any]:
    """
    Read MCP server state to get current port and project name.

    :param state_file: Path to .mcp_server_state.json
    :return: State dictionary
    :raises: ValueError if file invalid
    """
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Validate required fields
        if "port" not in state:
            raise ValueError("State file missing 'port' field")
        if "url" not in state:
            raise ValueError("State file missing 'url' field")
        if "project" not in state or "name" not in state["project"]:
            raise ValueError("State file missing 'project.name' field")

        return state
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in state file: {e}")


def find_cline_config() -> Optional[Path]:
    """
    Find Cline's cline_mcp_settings.json file.

    Searches in common VSCode/Cursor settings locations.

    :return: Path to config file or None if not found
    """
    # Common locations for VSCode/Cursor settings
    home = Path.home()

    # macOS/Linux locations
    possible_paths = [
        # VSCode
        home
        / "Library"
        / "Application Support"
        / "Code"
        / "User"
        / "globalStorage"
        / "saoudrizwan.claude-dev"
        / "settings"
        / "cline_mcp_settings.json",
        home
        / ".config"
        / "Code"
        / "User"
        / "globalStorage"
        / "saoudrizwan.claude-dev"
        / "settings"
        / "cline_mcp_settings.json",
        # Cursor
        home
        / "Library"
        / "Application Support"
        / "Cursor"
        / "User"
        / "globalStorage"
        / "saoudrizwan.claude-dev"
        / "settings"
        / "cline_mcp_settings.json",
        home
        / ".config"
        / "Cursor"
        / "User"
        / "globalStorage"
        / "saoudrizwan.claude-dev"
        / "settings"
        / "cline_mcp_settings.json",
        # Windows
        home
        / "AppData"
        / "Roaming"
        / "Code"
        / "User"
        / "globalStorage"
        / "saoudrizwan.claude-dev"
        / "settings"
        / "cline_mcp_settings.json",
        home
        / "AppData"
        / "Roaming"
        / "Cursor"
        / "User"
        / "globalStorage"
        / "saoudrizwan.claude-dev"
        / "settings"
        / "cline_mcp_settings.json",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def update_cline_config(
    config_file: Path, server_name: str, url: str, port: int
) -> None:
    """
    Update Cline MCP config with prAxIs OS server settings.

    :param config_file: Path to cline_mcp_settings.json
    :param server_name: Dynamic MCP server name (from project name)
    :param url: MCP server URL
    :param port: MCP server port
    """
    # Read existing config or create new
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {"mcpServers": {}}

    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Update or create configuration with dynamic server name
    # CRITICAL: Must specify "type": "streamableHttp" explicitly!
    # Cline's schema checks in order: stdio, sse, streamableHttp
    # Without type, URL-only configs default to SSE (deprecated)
    config["mcpServers"][server_name] = {
        "type": "streamableHttp",
        "url": url,
        "alwaysAllow": [
            "search_standards",
            "get_current_phase",
            "get_workflow_state",
            "get_server_info",
        ],
        "disabled": False,
        "timeout": 60,
    }

    # Create parent directory if needed
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Write updated config
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Updated Cline MCP config at: {config_file}")
    print(f"   Server name: {server_name}")
    print(f"   Server URL: {url}")
    print(f"   Port: {port}")


def main() -> int:
    """
    Main entry point.

    :return: Exit code (0 = success, 1 = error)
    """
    print("🔍 prAxIs OS MCP - Cline Configuration Updater")
    print("=" * 60)

    # Step 1: Find MCP state file
    print("\n📂 Searching for .praxis-os/.mcp_server_state.json...")
    state_file = find_mcp_state_file()

    if not state_file:
        print("❌ ERROR: Could not find .praxis-os/.mcp_server_state.json")
        print("\nMake sure:")
        print("  1. You're in an prAxIs OS project")
        print("  2. The MCP server is running")
        print("  3. Run from project root or subdirectory")
        return 1

    print(f"✅ Found state file: {state_file}")

    # Step 2: Read current port
    print("\n📖 Reading MCP server state...")
    try:
        state = read_mcp_state(state_file)
        port = state["port"]
        url = state["url"]
        server_name = state["project"]["name"]
        print(f"✅ Current MCP server: {url}")
        print(f"   Project name: {server_name}")
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        return 1

    # Step 3: Find Cline config
    print("\n🔍 Searching for Cline MCP config...")
    config_file = find_cline_config()

    if not config_file:
        print("⚠️  WARNING: Could not find cline_mcp_settings.json")
        print("\nPlease provide the path manually:")
        print("  python update-cline-mcp.py --config-path <path>")
        print("\nOr configure manually in Cline:")
        print("  1. Click MCP Servers icon")
        print("  2. Go to Configure tab")
        print("  3. Click 'Configure MCP Servers'")
        print(f"  4. Add remote server with URL: {url}")
        return 1

    print(f"✅ Found config file: {config_file}")

    # Step 4: Update config
    print("\n✏️  Updating Cline MCP configuration...")
    try:
        update_cline_config(config_file, server_name, url, port)
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Cline is now configured for prAxIs OS")
        print(f"\nServer name: {server_name} (from project)")
        print("\nNext steps:")
        print("  1. Restart Cline (reload VSCode/Cursor window)")
        print(f"  2. Open Cline and verify '{server_name}' server is connected")
        print("  3. Try: 'search standards for orientation'")
        return 0
    except Exception as e:
        print(f"❌ ERROR updating config: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

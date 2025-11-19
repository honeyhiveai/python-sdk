#!/usr/bin/env python3
"""
Configure Claude Code extension with prAxIs OS MCP server.

This script creates/updates .mcp.json in the project root to configure
the Claude Code extension to use the prAxIs OS MCP server via HTTP transport.

Similar to update-cline-mcp.py, this configures HTTP connection to an
EXISTING MCP server (launched by Cursor or another primary IDE).

Usage:
    python .praxis-os/bin/configure-claude-code-mcp.py

The script will:
1. Read current MCP server port from .praxis-os/.mcp_server_state.json
2. Create or update .mcp.json in project root
3. Configure agent-os-rag server with HTTP transport
4. Preserve other MCP server configurations
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def find_project_root() -> Optional[Path]:
    """
    Find project root containing .praxis-os directory.

    :return: Path to project root or None if not found
    """
    # Start from current directory
    current = Path.cwd()

    # Check current directory
    if (current / ".praxis-os").exists():
        return current

    # Check parent directories (up to 5 levels)
    for parent in current.parents[:5]:
        if (parent / ".praxis-os").exists():
            return parent

    return None


def read_mcp_state(project_root: Path) -> Dict[str, Any]:
    """
    Read MCP server state to get current HTTP URL.

    :param project_root: Path to project root
    :return: State dictionary
    :raises: ValueError if file invalid or missing
    """
    state_file = project_root / ".praxis-os" / ".mcp_server_state.json"

    if not state_file.exists():
        raise ValueError(
            "MCP server state file not found. "
            "Make sure Cursor (or primary IDE) is running with prAxIs OS MCP server active."
        )

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Validate required fields
        if "url" not in state:
            raise ValueError("State file missing 'url' field")
        if "port" not in state:
            raise ValueError("State file missing 'port' field")

        return state
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in state file: {e}")


def create_claude_code_config(url: str) -> Dict[str, Any]:
    """
    Create Claude Code MCP configuration for prAxIs OS.

    :param url: HTTP URL of running MCP server
    :return: Configuration dictionary
    """
    # CRITICAL: Must specify "type": "streamableHttp" explicitly!
    # Without type, URL-only configs may default to SSE (deprecated)
    return {"agent-os-rag": {"type": "streamableHttp", "transport": "http", "url": url}}


def update_mcp_json(project_root: Path, url: str, port: int) -> None:
    """
    Update .mcp.json with prAxIs OS server configuration using official CLI.

    Uses 'claude mcp add --scope project' to write project-local config.
    This is the official method per https://docs.claude.com/en/docs/claude-code/mcp.md

    :param project_root: Path to project root
    :param url: HTTP URL of MCP server
    :param port: Port number
    """
    import subprocess

    # Use official 'claude mcp add' with --scope project
    # This writes to .mcp.json (project-local, shareable)
    cmd = [
        "claude",
        "mcp",
        "add",
        "--scope",
        "project",
        "--transport",
        "http",
        "agent-os-rag",
        url,
    ]

    try:
        result = subprocess.run(
            cmd, cwd=str(project_root), capture_output=True, text=True, check=True
        )

        # Parse output to find the modified file path
        output_lines = result.stdout.strip().split("\n")

        print(f"✅ Updated {project_root / '.mcp.json'}")
        print(f"   Server URL: {url}")
        print(f"   Port: {port}")

    except subprocess.CalledProcessError as e:
        # Fall back to manual JSON editing if CLI fails
        print(f"⚠️  'claude mcp add' failed, using manual config...")

        mcp_json = project_root / ".mcp.json"

        # Read existing config or create new
        if mcp_json.exists():
            with open(mcp_json, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {"mcpServers": {}}

        # Ensure mcpServers exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Update or create agent-os-rag configuration
        praxis_os_config = create_claude_code_config(url)
        config["mcpServers"].update(praxis_os_config)

        # Write updated config
        with open(mcp_json, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Updated {mcp_json}")
        print(f"   Server URL: {url}")
        print(f"   Port: {port}")


def ensure_project_mcp_enabled(project_root: Path) -> None:
    """
    Ensure .claude/settings.local.json enables project MCP servers.

    Claude Code requires "enableAllProjectMcpServers": true in
    .claude/settings.local.json to respect project-local .mcp.json files.

    :param project_root: Path to project root
    """
    claude_dir = project_root / ".claude"
    settings_file = claude_dir / "settings.local.json"

    # Ensure .claude directory exists
    claude_dir.mkdir(exist_ok=True)

    # Read existing settings or create new
    if settings_file.exists():
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)
    else:
        settings = {}

    # Enable project MCP servers
    if not settings.get("enableAllProjectMcpServers", False):
        settings["enableAllProjectMcpServers"] = True

        # Write updated settings
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        print(f"✅ Enabled project MCP servers in {settings_file}")
    else:
        print(f"✅ Project MCP servers already enabled")


def ensure_vscode_workspace_settings(project_root: Path) -> None:
    """
    Ensure VS Code workspace settings enable Claude Code project MCP servers.

    The VS Code extension may need "claudeCode.enableProjectMcpServers": true
    in .vscode/settings.json to respect project-local .mcp.json files.

    :param project_root: Path to project root
    """
    vscode_dir = project_root / ".vscode"
    settings_file = vscode_dir / "settings.json"

    # Ensure .vscode directory exists
    vscode_dir.mkdir(exist_ok=True)

    # Read existing settings or create new
    if settings_file.exists():
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)
    else:
        settings = {}

    # Enable Claude Code project MCP servers
    if not settings.get("claudeCode.enableProjectMcpServers", False):
        settings["claudeCode.enableProjectMcpServers"] = True

        # Write updated settings
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        print(f"✅ Enabled Claude Code project MCP in {settings_file}")
    else:
        print(f"✅ Claude Code project MCP already enabled")


def main() -> int:
    """
    Main entry point.

    :return: Exit code (0 = success, 1 = error)
    """
    print("🔍 prAxIs OS MCP - Claude Code Configuration")
    print("=" * 60)

    # Step 1: Find project root
    print("\n📂 Searching for project root with .praxis-os/...")
    project_root = find_project_root()

    if not project_root:
        print("❌ ERROR: Could not find .praxis-os directory")
        print("\nMake sure:")
        print("  1. You're in an prAxIs OS project")
        print("  2. prAxIs OS has been installed")
        print("  3. Run from project root or subdirectory")
        return 1

    print(f"✅ Found project root: {project_root}")

    # Step 2: Read MCP server state
    print("\n📖 Reading MCP server state...")
    try:
        state = read_mcp_state(project_root)
        port = state["port"]
        url = state["url"]
        print(f"✅ Current MCP server: {url}")
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure Cursor (or primary IDE) is running")
        print("  2. Verify MCP server started (check Cursor output)")
        print("  3. Check .praxis-os/.mcp_server_state.json exists")
        return 1

    # Step 3: Enable project MCP servers in .claude/settings.local.json
    print("\n✏️  Enabling project MCP servers...")
    try:
        ensure_project_mcp_enabled(project_root)
    except Exception as e:
        print(f"⚠️  Warning: {e}")

    # Step 3b: Enable project MCP in VS Code workspace settings
    print("\n✏️  Configuring VS Code workspace settings...")
    try:
        ensure_vscode_workspace_settings(project_root)
    except Exception as e:
        print(f"⚠️  Warning: {e}")

    # Step 4: Update .mcp.json using official CLI
    print("\n✏️  Configuring .mcp.json (via 'claude mcp add')...")
    try:
        update_mcp_json(project_root, url, port)

        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Claude Code is now configured for prAxIs OS")
        print("\nConfiguration:")
        print("  - Method: Official 'claude mcp add --scope project'")
        print("  - MCP Config: .mcp.json (project-local, shareable)")
        print("  - CLI Settings: .claude/settings.local.json")
        print("  - VS Code Settings: .vscode/settings.json (extension support)")
        print("  - Transport: HTTP (connects to existing server)")
        print("  - Primary IDE: Cursor (launches server)")
        print("  - Claude Code: Secondary agent (via HTTP)")
        print("\nNext steps:")
        print("  1. Reload VS Code/Cursor window")
        print("  2. Open Claude Code extension")
        print("  3. Verify 'agent-os-rag' server is connected")
        print("  4. Try: 'search standards for orientation'")
        return 0

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

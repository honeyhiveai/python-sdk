"""
MCP server discovery utilities for sub-agents.

This module provides utilities for sub-agents to discover and connect to
a running MCP server instance via its HTTP transport. The discovery mechanism
reads the server's state file and validates that the server is still running.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# pylint: disable=too-many-return-statements
def discover_mcp_server(
    agent_os_path: Optional[Path] = None,
) -> Optional[str]:
    """
    Discover a running MCP server's HTTP endpoint by reading its state file.

    This function enables sub-agents to locate and connect to the MCP server
    without hardcoding URLs or ports. It reads the server's state file,
    validates that the server process is still alive, and returns the HTTP URL.

    The discovery process:
    1. Locates the `.agent-os/.mcp_server_state.json` state file
    2. Reads the server's transport mode, URL, and PID
    3. Validates the PID is still running (checks /proc/{pid} on Unix)
    4. Returns the HTTP URL if server is alive and HTTP-enabled
    5. Returns None if server not found, stale, or stdio-only

    Args:
        agent_os_path: Path to the .agent-os directory. If None, searches
                      for .agent-os in the current directory and parent
                      directories up to the home directory.

    Returns:
        The HTTP URL of the MCP server (e.g., "http://127.0.0.1:4242/mcp"),
        or None if:
        - State file does not exist (server not started)
        - PID is invalid or process not running (stale state)
        - Transport mode is "stdio" (HTTP not enabled)
        - State file is corrupted or missing required fields

    Example:
        >>> from mcp_server.sub_agents import discover_mcp_server
        >>> import requests
        >>>
        >>> # Discover server
        >>> url = discover_mcp_server()
        >>> if url is None:
        ...     print("MCP server not running")
        ... else:
        ...     # Use the URL to make requests
        ...     response = requests.post(
        ...         url,
        ...         json={
        ...             "jsonrpc": "2.0",
        ...             "id": 1,
        ...             "method": "tools/list",
        ...             "params": {}
        ...         }
        ...     )
        ...     print(f"Available tools: {response.json()}")

    Raises:
        No exceptions are raised. All errors are logged and result in
        returning None, making this function safe for use in sub-agent
        initialization logic.

    Notes:
        - This function performs I/O (file read, process check) and should
          be called at connection time, not imported/cached
        - On Windows, PID validation uses psutil if available, otherwise
          assumes PID is valid
        - Thread-safe: reads are atomic, state file is not modified
        - If server crashes without cleanup, stale state will be detected
          via PID check within a few seconds

    See Also:
        - PortManager.write_state(): Creates the state file
        - PortManager.read_state(): Low-level state file reader
    """
    # Locate .agent-os directory
    if agent_os_path is None:
        agent_os_path = _find_agent_os_directory()
        if agent_os_path is None:
            logger.debug("Could not locate .agent-os directory")
            return None

    # Read state file
    state_file = agent_os_path / ".mcp_server_state.json"
    if not state_file.exists():
        logger.debug("State file not found at %s", state_file)
        return None

    try:
        with open(state_file, encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Failed to read state file %s: %s", state_file, e)
        return None

    # Validate required fields
    if not isinstance(state, dict):
        logger.warning("State file %s has invalid format (not a dict)", state_file)
        return None

    transport = state.get("transport")
    url = state.get("url")
    pid = state.get("pid")

    if not all([transport, url, pid]):
        logger.warning(
            "State file %s missing required fields (transport=%s, url=%s, pid=%s)",
            state_file,
            transport,
            url,
            pid,
        )
        return None

    # Check if HTTP is enabled
    if transport not in ["http", "dual"]:
        logger.debug("Server is running in %s mode (HTTP not available)", transport)
        return None

    # Validate PID (check if process is still running)
    pid_int = int(pid) if pid is not None else 0
    if not _is_process_alive(pid_int):
        logger.warning("Server PID %s is not running (stale state file)", pid)
        return None

    logger.info("Discovered MCP server at %s (PID %s)", url, pid)
    return url


def _find_agent_os_directory() -> Optional[Path]:
    """
    Search for the .agent-os directory starting from the current directory.

    Searches upward through parent directories until finding .agent-os or
    reaching the home directory.

    Returns:
        Path to .agent-os directory, or None if not found.
    """
    current = Path.cwd()
    home = Path.home()

    # Search current directory and parents
    while True:
        agent_os = current / ".agent-os"
        if agent_os.exists() and agent_os.is_dir():
            return agent_os

        # Stop at home directory
        if current == home:
            break

        # Move to parent
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    return None


def _is_process_alive(pid: int) -> bool:  # pylint: disable=too-many-return-statements
    """
    Check if a process with the given PID is currently running.

    Uses platform-specific methods:
    - Unix/Linux: Checks /proc/{pid} directory existence
    - macOS: Sends signal 0 to check process existence
    - Windows: Uses psutil if available, otherwise assumes alive

    Args:
        pid: Process ID to check.

    Returns:
        True if the process is running, False otherwise.

    Notes:
        - On Unix systems, this checks /proc first (fastest), then tries
          sending signal 0 as a fallback
        - On Windows, requires psutil for accurate checking
        - False positives (returning True for dead process) are rare but
          possible on Windows without psutil
    """
    if not isinstance(pid, int) or pid <= 0:
        return False

    # Try /proc filesystem first (Unix/Linux)
    proc_path = Path(f"/proc/{pid}")
    if proc_path.exists():
        return True

    # Try sending signal 0 (Unix/macOS)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
    except Exception as e:  # pylint: disable=broad-exception-caught
        # On Windows, os.kill may not work as expected
        logger.debug("Could not check PID %s via signal: %s", pid, e)

    # Try psutil as fallback (cross-platform)
    try:
        import psutil  # pylint: disable=import-outside-toplevel

        result: bool = psutil.pid_exists(pid)
        return result
    except ImportError:
        logger.debug("psutil not available, assuming PID %s is alive", pid)
        # Conservative: assume process is alive if we can't verify
        # Better to attempt connection and fail than miss a valid server
        return True
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.debug("psutil check failed for PID %s: %s", pid, e)
        return True  # Conservative assumption

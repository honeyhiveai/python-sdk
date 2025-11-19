"""
Port allocation and state file management for MCP server dual-transport.

This module provides dynamic port allocation to enable multiple MCP server
instances (across different projects/Cursor windows) to run simultaneously
without conflicts.

Traceability:
    FR-026: Dual-Transport Support
    NFR-O1: Structured Logging (state file management)
"""

import json
import logging
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from ouroboros.foundation.project_info import ProjectInfoDiscovery

logger = logging.getLogger(__name__)


class PortManager:
    """
    Manages dynamic port allocation and server state persistence.

    Responsibilities:
    - Allocate available ports from range 4242-5242
    - Write atomic state files for sub-agent discovery
    - Provide state file cleanup on shutdown
    - Validate port availability via socket binding

    State file format (.praxis-os/.mcp_server_state.json):
    {
      "version": "1.0.0",
      "transport": "dual",
      "port": 4243,
      "host": "127.0.0.1",
      "path": "/mcp",
      "url": "http://127.0.0.1:4243/mcp",
      "pid": 12345,
      "started_at": "2025-10-11T10:30:00Z",
      "project": {"name": "...", "root": "..."}
    }

    Example:
        >>> from pathlib import Path
        >>> manager = PortManager(Path(".praxis-os"), project_discovery)
        >>> port = manager.find_available_port()
        >>> manager.write_state(transport="dual", port=port)
        >>> # ... server runs ...
        >>> manager.cleanup_state()
    """

    STATE_FILE_NAME = ".mcp_server_state.json"
    DEFAULT_PORT_START = 4242
    DEFAULT_PORT_END = 5242

    def __init__(self, base_path: Path, project_discovery: ProjectInfoDiscovery):
        """
        Initialize port manager.

        Args:
            base_path: Path to .praxis-os directory
            project_discovery: ProjectInfoDiscovery instance for metadata
        """
        self.base_path = base_path
        self.state_file = base_path / self.STATE_FILE_NAME
        self.project_discovery = project_discovery

    def find_available_port(self, preferred_port: int = DEFAULT_PORT_START) -> int:
        """
        Find first available port in range.

        Tries preferred port first (typically 4242), then increments
        through range until available port found or range exhausted.

        Args:
            preferred_port: First port to try (default: 4242)

        Returns:
            Available port number

        Raises:
            RuntimeError: If no ports available in range with actionable message

        Example:
            >>> port = manager.find_available_port()
            >>> print(f"Allocated port: {port}")
            Allocated port: 4242
        """
        for port in range(preferred_port, self.DEFAULT_PORT_END + 1):
            if self._is_port_available(port):
                logger.info("Allocated port %d", port)
                return port

        # No ports available - provide actionable error
        raise RuntimeError(
            f"No available ports in range {preferred_port}-{self.DEFAULT_PORT_END}. "
            f"Close some MCP server instances (e.g., other Cursor windows) and retry. "
            f"To see active servers: ps aux | grep ouroboros"
        )

    def write_state(
        self,
        transport: str,
        port: Optional[int],
        host: str = "127.0.0.1",
        path: str = "/mcp",
    ) -> None:
        """
        Write server state to file for sub-agent discovery.

        Uses atomic write (temp file + rename) to prevent corruption
        if process crashes during write. Sets restrictive permissions
        (0o600) for security.

        Args:
            transport: Transport mode ("dual", "stdio", "http")
            port: HTTP port (None for stdio-only)
            host: HTTP host (default: "127.0.0.1")
            path: HTTP path (default: "/mcp")

        Raises:
            OSError: If file write fails (propagated, fatal error)

        Example:
            >>> manager.write_state(
            ...     transport="dual",
            ...     port=4242,
            ...     host="127.0.0.1",
            ...     path="/mcp"
            ... )
        """
        # Discover project info dynamically
        project_info = self.project_discovery.get_project_info()

        # Build complete state document
        state = {
            "version": "1.0.0",
            "transport": transport,
            "port": port,
            "host": host,
            "path": path,
            "url": f"http://{host}:{port}{path}" if port else None,
            "pid": os.getpid(),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "project": {"name": project_info["name"], "root": project_info["root"]},
        }

        # Atomic write: temp file + rename (POSIX atomic operation)
        temp_file = self.state_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        temp_file.rename(self.state_file)

        # Set restrictive permissions (owner read/write only)
        self.state_file.chmod(0o600)

        logger.info("State file written: %s", self.state_file)

    @classmethod
    def read_state(cls, base_path: Path) -> Optional[Dict]:
        """
        Read server state from file (for sub-agents).

        Returns None gracefully for missing or corrupted files
        to enable sub-agents to detect server unavailability.

        Args:
            base_path: Path to .praxis-os directory

        Returns:
            State dictionary if valid, None otherwise

        Example:
            >>> from pathlib import Path
            >>> state = PortManager.read_state(Path(".praxis-os"))
            >>> if state:
            ...     url = state["url"]
            ...     print(f"Server at: {url}")
            ... else:
            ...     print("Server not running")
        """
        state_file = base_path / cls.STATE_FILE_NAME

        if not state_file.exists():
            return None

        try:
            result: Dict = json.loads(state_file.read_text(encoding="utf-8"))
            return result
        except (json.JSONDecodeError, OSError) as e:
            # Corrupted or unreadable - return None for graceful degradation
            logger.warning("Failed to read state file: %s", e)
            return None

    def cleanup_state(self) -> None:
        """
        Remove state file on shutdown.

        Called in finally block to ensure cleanup even on errors.
        Safe to call multiple times or if file doesn't exist.

        Example:
            >>> try:
            ...     # ... run server ...
            ...     pass
            ... finally:
            ...     manager.cleanup_state()
        """
        if self.state_file.exists():
            self.state_file.unlink()
            logger.info("State file removed: %s", self.state_file)

    def _is_port_available(self, port: int) -> bool:
        """
        Check if port is available by attempting socket bind.

        Args:
            port: Port number to check

        Returns:
            True if port is available, False otherwise

        Note:
            Uses SO_REUSEADDR to handle TIME_WAIT state properly.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("127.0.0.1", port))
                return True
        except OSError:
            # Port in use or permission denied
            return False


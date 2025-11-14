"""
Transport mode management for MCP server dual-transport architecture.

This module orchestrates stdio and HTTP transports, supporting:
- Dual mode (stdio + HTTP concurrently)
- stdio-only mode
- HTTP-only mode

Traceability:
    FR-026: Dual-Transport Support
    NFR-O1: Structured Logging (transport lifecycle)
"""

import logging
import socket
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)


class TransportManager:
    """
    Manages transport mode execution and lifecycle.

    Orchestrates different transport modes for the MCP server:
    - Dual mode: stdio (main thread) + HTTP (background thread)
    - stdio-only: IDE communication only
    - HTTP-only: Network communication only

    Provides:
    - Thread-safe transport orchestration
    - HTTP readiness checking with timeout
    - Graceful shutdown handling

    Example:
        >>> from fastmcp import FastMCP
        >>> mcp = FastMCP("my-server")
        >>> manager = TransportManager(mcp)
        >>> # Run dual mode
        >>> manager.run_dual_mode(host="127.0.0.1", port=4242, path="/mcp")
    """

    def __init__(self, mcp_server):
        """
        Initialize transport manager.

        Args:
            mcp_server: Configured FastMCP instance
        """
        self.mcp_server = mcp_server
        self.http_thread: Optional[threading.Thread] = None

    def run_dual_mode(self, http_host: str, http_port: int, http_path: str) -> None:
        """
        Run dual transport mode: stdio (main) + HTTP (background).

        Execution flow:
        1. Start HTTP server in daemon thread
        2. Wait for HTTP server to be ready (health check with timeout)
        3. Run stdio in main thread (blocks until shutdown)
        4. On shutdown, daemon thread automatically dies

        Args:
            http_host: Host for HTTP server (typically "127.0.0.1")
            http_port: Port for HTTP server (from port allocation)
            http_path: Path for MCP endpoint (typically "/mcp")

        Raises:
            RuntimeError: If HTTP server fails to start within timeout

        Example:
            >>> manager.run_dual_mode(
            ...     http_host="127.0.0.1",
            ...     http_port=4242,
            ...     http_path="/mcp"
            ... )
        """
        logger.info("🔄 Starting dual transport mode")
        logger.info("   stdio: for IDE communication")
        logger.info("   HTTP:  http://%s:%d%s", http_host, http_port, http_path)

        # Start HTTP in background daemon thread
        self.http_thread = self._start_http_thread(http_host, http_port, http_path)

        # Wait for HTTP server to be ready (health check)
        if not self._wait_for_http_ready(http_host, http_port, timeout=5):
            raise RuntimeError(
                f"HTTP server failed to start within 5 seconds. "
                f"Port {http_port} may be in use or there's a configuration error. "
                f"Check logs for details."
            )

        logger.info("✅ HTTP transport ready")
        logger.info("🔌 Starting stdio transport (blocking)")

        # Run stdio in main thread (blocks until shutdown)
        self.mcp_server.run(transport="stdio", show_banner=False)

    def run_stdio_mode(self) -> None:
        """
        Run stdio-only mode (IDE communication only).

        No HTTP server is started. Only stdio transport runs for IDE.
        This is the traditional mode for users who don't need sub-agents.

        Example:
            >>> manager.run_stdio_mode()
        """
        logger.info("🔌 Starting stdio-only mode")
        self.mcp_server.run(transport="stdio", show_banner=False)

    def run_http_mode(self, host: str, port: int, path: str) -> None:
        """
        Run HTTP-only mode (network communication only).

        No stdio transport. Only HTTP server runs, useful for:
        - Running as a system service
        - Testing HTTP transport independently
        - Serving only network-based agents

        Args:
            host: Host for HTTP server
            port: Port for HTTP server
            path: Path for MCP endpoint

        Example:
            >>> manager.run_http_mode(
            ...     host="127.0.0.1",
            ...     port=4242,
            ...     path="/mcp"
            ... )
        """
        logger.info("🌐 Starting HTTP-only mode")
        logger.info("   HTTP: http://%s:%d%s", host, port, path)
        self.mcp_server.run(
            transport="streamable-http",
            host=host,
            port=port,
            path=path,
            show_banner=False,
        )

    def shutdown(self) -> None:
        """
        Graceful shutdown of transport manager.

        Called in finally block to ensure cleanup even on errors.
        Safe to call multiple times or if no transports are running.

        Note:
            HTTP thread is daemon, so it will automatically die when
            main thread exits. This method is for explicit cleanup.

        Example:
            >>> try:
            ...     manager.run_dual_mode(...)
            ... finally:
            ...     manager.shutdown()
        """
        if self.http_thread and self.http_thread.is_alive():
            logger.info("Waiting for HTTP thread to finish...")
            # Daemon threads die automatically, but log for visibility
        logger.info("Transport manager shutdown complete")

    def _start_http_thread(self, host: str, port: int, path: str) -> threading.Thread:
        """
        Start HTTP server in background daemon thread.

        Daemon thread ensures it dies when main thread exits,
        preventing orphaned processes.

        Args:
            host: HTTP server host
            port: HTTP server port
            path: MCP endpoint path

        Returns:
            Running daemon thread
        """

        def run_http():
            """Thread target function for HTTP server."""
            try:
                self.mcp_server.run(
                    transport="streamable-http",
                    host=host,
                    port=port,
                    path=path,
                    show_banner=False,
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                # Log but don't crash - main thread handles lifecycle
                logger.error("HTTP transport error: %s", e, exc_info=True)

        thread = threading.Thread(
            target=run_http, daemon=True, name="http-transport"  # Dies with main thread
        )
        thread.start()
        logger.debug("HTTP thread started: %s", thread.name)

        return thread

    def _wait_for_http_ready(self, host: str, port: int, timeout: int = 5) -> bool:
        """
        Poll socket connection until HTTP server ready or timeout.

        Uses socket connection test to verify HTTP server is accepting
        connections before returning control to caller.

        Args:
            host: HTTP server host
            port: HTTP server port
            timeout: Maximum seconds to wait (default: 5)

        Returns:
            True if server ready, False if timeout

        Note:
            Retries every 0.5 seconds with 1 second socket timeout.
        """
        start = time.time()

        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)  # 1 second per connection attempt
                    sock.connect((host, port))
                    # Connection successful
                    logger.debug("HTTP server ready on %s:%d", host, port)
                    return True
            except (ConnectionRefusedError, OSError):
                # Server not ready yet, wait and retry
                time.sleep(0.5)

        # Timeout reached
        logger.error("HTTP server did not become ready after %ds", timeout)
        return False


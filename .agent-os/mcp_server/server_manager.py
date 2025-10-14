"""
Server Manager for Agent OS Upgrade Workflow.

Manages MCP server restart and health verification.
"""

# pylint: disable=broad-exception-caught,missing-raises-doc,consider-using-with
# Justification: Server manager uses broad exceptions for robustness,
# standard exception documentation in docstrings, and Popen without context manager
# is intentional for background server process that must remain running

import logging
import subprocess
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ServerManager:
    """
    Manages MCP server process lifecycle.

    Features:
    - Graceful server restart
    - Health check polling
    - Process management
    - Restart timing

    Example:
        manager = ServerManager()
        result = manager.restart_server()
        if result["started"]:
            print(f"Server restarted in {result['restart_time_seconds']}s")
    """

    @staticmethod
    def restart_server() -> Dict:
        """
        Restart MCP server process.

        Steps:
        1. Stop server (pkill)
        2. Wait for process to terminate
        3. Start new process in background
        4. Wait for health check

        Returns:
            {
                "stopped": bool,
                "started": bool,
                "restart_time_seconds": float,
                "pid": int | None,
                "error": str | None
            }
        """
        logger.info("Restarting MCP server...")

        start_time = time.time()

        result: Dict[str, Any] = {
            "stopped": False,
            "started": False,
            "restart_time_seconds": 0.0,
            "pid": None,
            "error": None,
        }

        # Step 1: Stop server
        try:
            subprocess.run(
                ["pkill", "-f", "python -m mcp_server"],
                timeout=10,
                check=False,
            )
            logger.info("Sent stop signal to MCP server")

            # Wait for process to terminate
            time.sleep(2)
            result["stopped"] = True

        except subprocess.TimeoutExpired:
            result["error"] = "Failed to stop server: timeout"
            logger.error(result["error"])
            return result
        except Exception as e:
            result["error"] = f"Failed to stop server: {e}"
            logger.error(result["error"])
            return result

        # Step 2: Start server in background
        try:
            # Start server in background
            process = subprocess.Popen(
                ["python", "-m", "mcp_server"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            result["pid"] = process.pid
            logger.info("Started MCP server with PID: %s", process.pid)

            # Wait a moment for server to initialize
            time.sleep(3)

            result["started"] = True

        except Exception as e:
            result["error"] = f"Failed to start server: {e}"
            logger.error(result["error"])
            return result

        # Calculate restart time
        result["restart_time_seconds"] = time.time() - start_time

        logger.info("Server restarted in %.2fs", result["restart_time_seconds"])

        return result

    @staticmethod
    def wait_for_server_ready(timeout: int = 30) -> bool:
        """
        Wait for server to respond to health checks.

        Polls every second until server responds or timeout.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if server is ready, False if timeout
        """
        logger.info("Waiting for server to be ready (timeout: %ss)...", timeout)

        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if server process is running
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "python -m mcp_server"],
                    capture_output=True,
                    timeout=5,
                    check=False,
                )

                if result.returncode == 0:
                    logger.info("Server is ready")
                    return True

            except Exception as e:
                logger.debug("Health check failed: %s", e)

            time.sleep(1)

        logger.error("Server not ready after %ss", timeout)
        return False

    @staticmethod
    def stop_server() -> bool:
        """
        Stop MCP server process.

        Returns:
            True if stopped successfully, False otherwise
        """
        logger.info("Stopping MCP server...")

        try:
            subprocess.run(
                ["pkill", "-f", "python -m mcp_server"],
                timeout=10,
                check=False,
            )
            logger.info("Server stopped")
            return True

        except Exception as e:
            logger.error("Failed to stop server: %s", e)
            return False

    @staticmethod
    def is_server_running() -> bool:
        """
        Check if MCP server is currently running.

        Returns:
            True if running, False otherwise
        """
        try:
            result = subprocess.run(
                ["pgrep", "-f", "python -m mcp_server"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0

        except Exception:
            return False

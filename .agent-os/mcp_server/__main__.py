"""
Entry point for Agent OS MCP server when run as a module.

Allows execution via:
    python -m mcp_server --transport dual
    python -m mcp_server --transport stdio
    python -m mcp_server --transport http
"""

# pylint: disable=broad-exception-caught
# Justification: Entry point uses broad exceptions for robustness

import argparse
import logging
import os
import sys
from pathlib import Path

from .config import ConfigLoader, ConfigValidator
from .port_manager import PortManager
from .project_info import ProjectInfoDiscovery
from .server import ServerFactory
from .transport_manager import TransportManager

logger = logging.getLogger(__name__)


def find_agent_os_directory() -> Path:
    """
    Find .agent-os directory in project.

    Search order:
    1. AGENT_OS_BASE_PATH env var (if set)
    2. Current directory / .agent-os
    3. Home directory / .agent-os
    4. Parent of __file__ / .agent-os

    Returns:
        Path to .agent-os directory

    Raises:
        SystemExit: If .agent-os directory not found
    """
    # Priority 1: Check AGENT_OS_BASE_PATH env var (for IDEs with wrong cwd)
    if base_env := os.getenv("AGENT_OS_BASE_PATH"):
        base_path = Path(base_env) / ".agent-os"
        if base_path.exists():
            logger.info("Using AGENT_OS_BASE_PATH: %s", base_path)
            return base_path
        logger.warning(
            "AGENT_OS_BASE_PATH is set to %s but .agent-os not found there",
            base_env,
        )

    # Priority 2: Current directory (for well-behaved IDEs)
    base_path = Path.cwd() / ".agent-os"

    if not base_path.exists():
        # Try common alternative locations
        alternatives = [
            Path.home() / ".agent-os",
            Path(__file__).parent.parent.parent / ".agent-os",
        ]

        for alt in alternatives:
            if alt.exists():
                base_path = alt
                break
        else:
            logger.error(
                "Could not find .agent-os directory. Tried:\n"
                "  - AGENT_OS_BASE_PATH env var: %s\n"
                "  - %s\n"
                "  - %s\n"
                "  - %s\n"
                "Please run from project root, set AGENT_OS_BASE_PATH, "
                "or ensure .agent-os exists.",
                os.getenv("AGENT_OS_BASE_PATH", "not set"),
                Path.cwd() / ".agent-os",
                Path.home() / ".agent-os",
                Path(__file__).parent.parent.parent / ".agent-os",
            )
            sys.exit(1)

    return base_path


def main() -> None:  # pylint: disable=too-many-statements
    """
    Entry point for MCP server with dual-transport support.

    Supports three transport modes:
    - dual: stdio (IDE) + HTTP (sub-agents) concurrently
    - stdio: IDE communication only
    - http: Network communication only

    Uses ConfigLoader, ConfigValidator, and ServerFactory for dependency injection.
    Handles graceful shutdown on KeyboardInterrupt and logs fatal errors.

    CLI Usage:
        python -m mcp_server --transport dual
        python -m mcp_server --transport stdio --log-level DEBUG
        python -m mcp_server --transport http

    :raises SystemExit: Exits with code 1 if server initialization fails
    """
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Agent OS MCP Server with dual-transport support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Transport modes:
  dual    - stdio (for IDE) + HTTP (for sub-agents) concurrently
  stdio   - IDE communication only (traditional mode)
  http    - Network communication only (for testing or services)

Examples:
  python -m mcp_server --transport dual
  python -m mcp_server --transport stdio --log-level DEBUG
        """,
    )
    parser.add_argument(
        "--transport",
        choices=["dual", "stdio", "http"],
        required=True,
        help="Transport mode: dual, stdio, or http",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger.info("=" * 60)
    logger.info("Agent OS MCP Server")
    logger.info("Transport Mode: %s", args.transport)
    logger.info("Log Level: %s", args.log_level)
    logger.info("=" * 60)

    # Initialize components (for cleanup in finally block)
    port_manager = None
    transport_mgr = None

    try:
        # Find and validate .agent-os directory
        base_path = find_agent_os_directory()
        logger.info("Base path: %s", base_path)

        # Load and validate configuration
        config = ConfigLoader.load(base_path)
        logger.info("Configuration loaded successfully")

        errors = ConfigValidator.validate(config)
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error("  %s", error)
            sys.exit(1)

        logger.info("Configuration validated successfully")

        # Initialize project discovery and port manager
        project_discovery = ProjectInfoDiscovery(base_path)
        port_manager = PortManager(base_path, project_discovery)

        # Create MCP server using factory with dependency injection
        factory = ServerFactory(config)
        mcp = factory.create_server(
            project_discovery=project_discovery, transport_mode=args.transport
        )

        # Initialize transport manager
        transport_mgr = TransportManager(mcp, config)

        # Execute based on transport mode
        if args.transport == "dual":
            # Dual mode: stdio + HTTP concurrently
            http_port = port_manager.find_available_port()
            http_host = config.mcp.http_host
            http_path = config.mcp.http_path

            # Write state file with HTTP URL for sub-agent discovery
            port_manager.write_state(
                transport="dual", port=http_port, host=http_host, path=http_path
            )

            logger.info("Port allocated: %d", http_port)
            logger.info("HTTP URL: http://%s:%d%s", http_host, http_port, http_path)

            # Run dual mode (HTTP in background, stdio in foreground)
            transport_mgr.run_dual_mode(http_host, http_port, http_path)

        elif args.transport == "stdio":
            # stdio-only mode (traditional)
            port_manager.write_state(transport="stdio", port=None)

            transport_mgr.run_stdio_mode()

        elif args.transport == "http":
            # HTTP-only mode
            http_port = port_manager.find_available_port()
            http_host = config.mcp.http_host
            http_path = config.mcp.http_path

            port_manager.write_state(
                transport="http", port=http_port, host=http_host, path=http_path
            )

            logger.info("Port allocated: %d", http_port)
            logger.info("HTTP URL: http://%s:%d%s", http_host, http_port, http_path)

            transport_mgr.run_http_mode(http_host, http_port, http_path)

    except KeyboardInterrupt:
        logger.info("Server shutdown requested (Ctrl+C)")
    except Exception as e:
        logger.error("Server failed: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup: Always cleanup state file and shutdown transports
        if port_manager:
            port_manager.cleanup_state()
            logger.info("State file cleaned up")

        if transport_mgr:
            transport_mgr.shutdown()

        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()

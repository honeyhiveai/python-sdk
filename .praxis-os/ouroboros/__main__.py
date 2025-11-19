"""
Entry point for Ouroboros MCP server when run as a module.

Allows execution via:
    python -m ouroboros --transport dual
    python -m ouroboros --transport stdio
    python -m ouroboros --transport http

Architecture:
    1. Load config (Pydantic v2 validation, fail-fast)
    2. Initialize Foundation layer (logging, errors)
    3. Initialize Subsystems (RAG, Workflow, Browser)
    4. Initialize Middleware (query_tracker, session_mapper)
    5. Register Tools (via ToolRegistry auto-discovery)
    6. Start MCP server (FastMCP)

Traceability:
    FR-010: Tool Auto-Discovery via ToolRegistry
    NFR-U2: Fail-fast validation at startup
    NFR-P1: Cold start <30s
"""

# pylint: disable=broad-exception-caught
# Justification: Entry point uses broad exceptions for robustness

import argparse
import logging
import os
import sys
from pathlib import Path

# CRITICAL: Prevent semaphore leaks in Python 3.13
# Must be set BEFORE imports that use joblib/tokenizers (sentence-transformers, etc.)

# 1. Disable tokenizers parallelism (prevents fork-after-parallelism issues)
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# 2. Configure joblib to use threading instead of loky (no semaphores)
try:
    import joblib
    # Register threading backend as default
    joblib.parallel.register_parallel_backend('threading', joblib.parallel.ThreadingBackend, make_default=True)
    
    # AGGRESSIVE: Override Parallel class to force threading backend
    original_parallel_init = joblib.Parallel.__init__
    def patched_parallel_init(self, *args, **kwargs):
        # Force backend to threading, ignore whatever was passed
        kwargs['backend'] = 'threading'
        kwargs['prefer'] = 'threads'
        original_parallel_init(self, *args, **kwargs)
    joblib.Parallel.__init__ = patched_parallel_init
    
    logging.basicConfig(level=logging.INFO)
    logging.info("✅ Aggressively configured joblib to ONLY use threading (Python 3.13 compat)")
except ImportError:
    # joblib not yet installed, will be handled by dependency checks
    pass

from ouroboros.foundation import PortManager, ProjectInfoDiscovery, TransportManager
from ouroboros.foundation.runtime_lock import RuntimeLock

logger = logging.getLogger(__name__)


def find_praxis_os_directory() -> Path:
    """
    Find .praxis-os directory in project.
    
    Search order:
    1. PROJECT_ROOT env var (if set)
    2. Current directory / .praxis-os
    3. Home directory / .praxis-os
    4. Parent of __file__ / .praxis-os
    
    Returns:
        Path to .praxis-os directory
        
    Raises:
        SystemExit: If .praxis-os directory not found
    """
    # Priority 1: Check PROJECT_ROOT env var
    if project_root_env := os.getenv("PROJECT_ROOT"):
        base_path = Path(project_root_env) / ".praxis-os"
        if base_path.exists():
            logger.info("Using PROJECT_ROOT: %s", base_path)
            return base_path
        logger.warning(
            "PROJECT_ROOT is set to %s but .praxis-os not found there",
            project_root_env,
        )
    
    # Priority 2: Current directory
    base_path = Path.cwd() / ".praxis-os"
    
    if not base_path.exists():
        # Try common alternative locations
        alternatives = [
            Path.home() / ".praxis-os",
            Path(__file__).parent.parent / ".praxis-os",
        ]
        
        for alt in alternatives:
            if alt.exists():
                base_path = alt
                break
        else:
            logger.error(
                "Could not find .praxis-os directory. Tried:\n"
                "  - PROJECT_ROOT env var: %s\n"
                "  - %s\n"
                "  - %s\n"
                "  - %s\n"
                "Please run from project root, set PROJECT_ROOT, "
                "or ensure .praxis-os exists.",
                os.getenv("PROJECT_ROOT", "not set"),
                Path.cwd() / ".praxis-os",
                Path.home() / ".praxis-os",
                Path(__file__).parent.parent / ".praxis-os",
            )
            sys.exit(1)
    
    return base_path


def main() -> None:
    """
    Entry point for Ouroboros MCP server.
    
    Supports three transport modes:
    - dual: stdio (IDE) + HTTP (sub-agents) concurrently
    - stdio: IDE communication only  
    - http: Network communication only
    
    CLI Usage:
        python -m ouroboros --transport dual
        python -m ouroboros --transport stdio --log-level DEBUG
        python -m ouroboros --transport http
        
    Raises:
        SystemExit: Exits with code 1 if server initialization fails
    """
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Ouroboros MCP Server - Clean Architecture Rewrite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Transport modes:
  dual    - stdio (for IDE) + HTTP (for sub-agents) concurrently
  stdio   - IDE communication only (traditional mode)
  http    - Network communication only (for testing or services)

Examples:
  python -m ouroboros --transport dual
  python -m ouroboros --transport stdio --log-level DEBUG
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
    logger.info("Ouroboros MCP Server - v2.0.0")
    logger.info("Transport Mode: %s", args.transport)
    logger.info("Log Level: %s", args.log_level)
    logger.info("=" * 60)
    
    # Initialize components (for cleanup in finally block)
    runtime_lock = None
    port_manager = None
    transport_mgr = None
    init_lock = None
    
    try:
        # Find and validate .praxis-os directory
        base_path = find_praxis_os_directory()
        logger.info("Base path: %s", base_path)
        
        # Acquire runtime lock (enforces singleton - one server per project)
        runtime_lock = RuntimeLock(base_path)
        if not runtime_lock.acquire():
            # Another MCP server is already running - exit gracefully
            logger.info(
                "Another MCP server is already running for this project. "
                "Exiting gracefully (singleton enforcement)."
            )
            sys.exit(0)
        
        # Acquire initialization lock (defends against concurrent spawns)
        from ouroboros.foundation.init_lock import InitLock
        
        init_lock = InitLock(base_path, timeout_seconds=10)
        if not init_lock.acquire():
            # Another process is initializing - exit gracefully
            logger.info(
                "Another MCP server instance is initializing. "
                "Exiting gracefully (this is normal with misbehaving MCP clients)."
            )
            sys.exit(0)
        
        # Initialize project discovery and port manager
        project_discovery = ProjectInfoDiscovery(base_path)
        port_manager = PortManager(base_path, project_discovery)
        
        # Create server
        from ouroboros.server import create_server
        
        mcp = create_server(base_path, args.transport)
        
        # Initialize transport manager
        transport_mgr = TransportManager(mcp)
        
        # Execute based on transport mode
        if args.transport == "dual":
            # Dual mode: stdio + HTTP concurrently
            http_port = port_manager.find_available_port()
            http_host = "127.0.0.1"
            http_path = "/mcp"
            
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
            http_host = "127.0.0.1"
            http_path = "/mcp"
            
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
        # Cleanup: Always cleanup state file, shutdown transports, and release lock
        if port_manager:
            port_manager.cleanup_state()
            logger.info("State file cleaned up")
        
        if transport_mgr:
            transport_mgr.shutdown()
        
        if init_lock:
            init_lock.release()
        
        if runtime_lock:
            runtime_lock.release()
        
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()


"""
Entry point for Agent OS MCP server when run as a module.

Allows execution via:
    python -m mcp_server
"""

import sys
import logging
from pathlib import Path

from .config import ConfigLoader, ConfigValidator
from .server import ServerFactory

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Entry point for MCP server with new modular architecture.
    
    Uses ConfigLoader, ConfigValidator, and ServerFactory for dependency injection.
    Handles graceful shutdown on KeyboardInterrupt and logs fatal errors.
    
    :raises SystemExit: Exits with code 1 if server initialization fails
    """
    try:
        # Determine base path (.agent-os/)
        # When run as module: python -m mcp_server
        # Assumes .agent-os/ is in parent directory of project
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
                logger.error(f"Could not find .agent-os directory. Tried: {base_path}")
                sys.exit(1)
        
        logger.info(f"Using base path: {base_path}")
        
        # Load configuration with graceful fallback
        config = ConfigLoader.load(base_path)
        logger.info("Configuration loaded successfully")
        
        # Validate configuration
        errors = ConfigValidator.validate(config)
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  {error}")
            sys.exit(1)
        
        logger.info("Configuration validated successfully")
        
        # Create server using factory with dependency injection
        factory = ServerFactory(config)
        mcp = factory.create_server()
        
        # Run with stdio transport for Cursor integration
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport='stdio')
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
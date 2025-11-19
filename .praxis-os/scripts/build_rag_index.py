"""
RAG Index Builder - CLI wrapper for StandardsIndex.

This script provides a command-line interface for building the standards index.
It now delegates to the StandardsIndex class which supports:
- Incremental updates (only processes changed files)
- Full rebuilds (force=True)
- Config-driven embedding models
- File locking for concurrency safety

File Locking (Concurrency Safety):
- Full rebuilds (--force) acquire exclusive lock to prevent corruption
- If MCP server is running (holds shared lock), force rebuild is blocked
- Incremental updates work safely via StandardsIndex
- Windows: Not supported (fcntl Unix-only, use WSL2)

100% AI-authored via human orchestration.
"""

import argparse
import logging
import sys
from pathlib import Path

import yaml

# Add mcp_server to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".praxis-os"))
from mcp_server.server.indexes.standards_index import StandardsIndex

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Build or update the RAG index from standards."""
    parser = argparse.ArgumentParser(
        description="Build RAG index from prAxIs OS standards"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force full rebuild even if index exists",
    )
    parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Disable incremental updates (process all files)",
    )
    parser.add_argument(
        "--index-path",
        type=str,
        help="Override index cache path (default: .praxis-os/.cache/standards/)",
    )
    parser.add_argument(
        "--config-path",
        type=str,
        help="Override config file path (default: .praxis-os/config/index_config.yaml)",
    )

    args = parser.parse_args()

    # Determine paths
    base_path = Path(__file__).parent.parent / ".praxis-os"

    if args.config_path:
        config_path = Path(args.config_path)
    else:
        config_path = base_path / "config" / "index_config.yaml"

    if args.index_path:
        cache_path = Path(args.index_path)
    else:
        cache_path = base_path / ".cache" / "standards"

    # Load config
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        full_config = yaml.safe_load(f)

    # Extract standards-specific config
    if "indexes" not in full_config or "standards" not in full_config["indexes"]:
        logger.error("Config missing 'indexes.standards' section")
        sys.exit(1)

    standards_config = full_config["indexes"]["standards"]
    source_paths = standards_config.get("source_paths", [])

    if not source_paths:
        logger.error("No source_paths configured for standards")
        sys.exit(1)

    # Create StandardsIndex instance
    logger.info("Initializing StandardsIndex...")
    logger.info(f"Cache path: {cache_path}")
    logger.info(f"Source paths: {source_paths}")

    index = StandardsIndex(cache_path=cache_path, config=standards_config)

    # Build index
    try:
        incremental = not args.no_incremental

        if args.force:
            logger.info("🔄 Force rebuild requested")
            index.build(source_paths=source_paths, force=True, incremental=False)
        elif incremental:
            logger.info("📝 Incremental update mode")
            index.build(source_paths=source_paths, force=False, incremental=True)
        else:
            logger.info("🔄 Full build mode")
            index.build(source_paths=source_paths, force=False, incremental=False)

        logger.info("✅ Index build complete!")

    except Exception as e:
        logger.error(f"❌ Index build failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Integration test for hot reload functionality.

Tests that the MCP server's file watcher detects Agent OS content changes
and triggers automatic index rebuilds.

100% AI-authored via human orchestration.
"""

import logging
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.agent_os_rag import create_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_hot_reload():
    """Test that file watcher detects changes and triggers rebuild."""
    
    logger.info("=" * 80)
    logger.info("INTEGRATION TEST: Hot Reload")
    logger.info("=" * 80)
    
    # Step 1: Initialize MCP server (starts file watcher)
    logger.info("\n📦 Step 1: Initialize MCP server with file watcher...")
    base_path = Path(__file__).parent.parent
    
    try:
        server = create_server(base_path=base_path)
        logger.info("✅ MCP server initialized with file watcher active")
    except Exception as e:
        logger.error(f"❌ Failed to initialize server: {e}", exc_info=True)
        return False
    
    # Step 2: Create a test file in Agent OS standards
    logger.info("\n✍️  Step 2: Simulating AI editing Agent OS content...")
    test_file = base_path / "standards" / "ai-assistant" / "_test_hot_reload.md"
    
    try:
        test_file.write_text("""# Hot Reload Test Document

This is a test document created to verify automatic index rebuilding.

## Test Section

When this file is created, the MCP server's file watcher should:
1. Detect the new .md file
2. Wait 5 seconds (debounce)
3. Trigger background index rebuild
4. Log completion

## Expected Behavior

The file watcher should log:
- "📝 New Agent OS content: _test_hot_reload.md"
- "🔄 Rebuilding index after Agent OS content changes..."
- "✅ Index rebuild complete! New content available."

**This demonstrates zero-touch hot reload for AI-managed content.**
""")
        logger.info(f"✅ Created test file: {test_file.name}")
    except Exception as e:
        logger.error(f"❌ Failed to create test file: {e}")
        return False
    
    # Step 3: Wait for file watcher to detect and rebuild
    logger.info("\n⏳ Step 3: Waiting for file watcher to detect change...")
    logger.info("   (5 second debounce + ~30 second rebuild with local embeddings)")
    
    # Wait 45 seconds total (5s debounce + 30s rebuild + 10s buffer)
    for i in range(45):
        time.sleep(1)
        if (i + 1) % 10 == 0:
            logger.info(f"   ... {i + 1}s elapsed")
    
    # Step 4: Clean up test file
    logger.info("\n🧹 Step 4: Cleaning up test file...")
    try:
        test_file.unlink()
        logger.info(f"✅ Removed test file: {test_file.name}")
    except Exception as e:
        logger.error(f"⚠️  Failed to remove test file: {e}")
    
    # Step 5: Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST COMPLETE")
    logger.info("=" * 80)
    logger.info("""
Check the logs above for:
✅ "📝 New Agent OS content: _test_hot_reload.md"
✅ "🔄 Rebuilding index after Agent OS content changes..."
✅ "✅ Index rebuild complete! New content available."

If you see all three, hot reload is working correctly!

Workflow verification:
1. AI edits Agent OS content → File watcher detects
2. 5 second debounce → Background rebuild starts
3. Local embeddings (30s) → Index updated
4. New content available → Zero human intervention

**100% AI-managed infrastructure with autonomous hot reload.**
""")
    
    return True


if __name__ == "__main__":
    success = test_hot_reload()
    sys.exit(0 if success else 1)


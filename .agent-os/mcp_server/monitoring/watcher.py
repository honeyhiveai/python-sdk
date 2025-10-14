"""
File system monitoring for Agent OS content changes.

Watches standards, usage, and workflows directories for changes and triggers
incremental index rebuilds with debouncing.
"""

# pylint: disable=too-many-instance-attributes
# Justification: File watcher needs 9 attributes for paths, timing, threading,
# callbacks, and state management - essential for robust file monitoring

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: __init__ requires 8 parameters for complete watcher configuration
# (paths, debouncing, callbacks, cache control) - all necessary for flexibility

# pylint: disable=import-outside-toplevel
# Justification: IndexBuilder imported lazily to avoid circular dependencies
# and reduce startup time when file watching is not needed

# pylint: disable=broad-exception-caught
# Justification: File watcher must be robust - catches broad exceptions during
# index rebuilds to prevent file monitoring service interruption

import logging
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class AgentOSFileWatcher(FileSystemEventHandler):
    """Watches Agent OS directories for content changes and triggers index rebuild."""

    def __init__(
        self,
        index_path: Path,
        standards_path: Path,
        usage_path: Optional[Path],
        workflows_path: Optional[Path],
        embedding_provider: str = "local",
        rag_engine: Optional[Any] = None,
        debounce_seconds: int = 5,
    ) -> None:
        """
        Initialize file watcher with configured paths.

        Uses dependency injection - all paths provided by configuration.

        :param index_path: Path to vector index directory
        :param standards_path: Path to standards directory
        :param usage_path: Path to usage directory (optional)
        :param workflows_path: Path to workflows directory (optional)
        :param embedding_provider: Embedding provider ("local" or "openai")
        :param rag_engine: Optional RAG engine instance for hot reload
        :param debounce_seconds: Seconds to wait after last change before rebuilding
        """
        self.index_path = index_path
        self.standards_path = standards_path
        self.usage_path = usage_path
        self.workflows_path = workflows_path
        self.embedding_provider = embedding_provider
        self.rag_engine = rag_engine
        self.rebuild_pending = False
        self.last_rebuild_time = 0.0
        self.debounce_seconds = debounce_seconds

    def on_modified(self, event: Any) -> None:
        """
        Handle file modification events.

        :param event: File system event from watchdog
        """
        if event.is_directory:
            return

        # Rebuild for markdown and JSON files (workflows metadata)
        if not (event.src_path.endswith(".md") or event.src_path.endswith(".json")):
            return

        logger.info("📝 Agent OS content modified: %s", Path(event.src_path).name)
        self._schedule_rebuild()

    def on_created(self, event: Any) -> None:
        """
        Handle file creation events.

        :param event: File system event from watchdog
        """
        if event.is_directory:
            return

        # Handle both markdown and JSON files (workflows metadata)
        if event.src_path.endswith(".md") or event.src_path.endswith(".json"):
            logger.info("📝 New Agent OS content: %s", Path(event.src_path).name)
            self._schedule_rebuild()

    def on_deleted(self, event: Any) -> None:
        """
        Handle file deletion events.

        :param event: File system event from watchdog
        """
        if event.is_directory:
            return

        # Handle both markdown and JSON files (workflows metadata)
        if event.src_path.endswith(".md") or event.src_path.endswith(".json"):
            logger.info("🗑️  Agent OS content deleted: %s", Path(event.src_path).name)
            self._schedule_rebuild()

    def _schedule_rebuild(self) -> None:
        """
        Schedule an index rebuild with debouncing.

        Prevents rapid repeated rebuilds by debouncing changes and running
        rebuild in background thread after quiet period.
        """
        if self.rebuild_pending:
            return  # Already scheduled

        self.rebuild_pending = True

        def rebuild_after_debounce() -> None:
            """
            Wait for debounce period, then incrementally update index.
            """
            time.sleep(self.debounce_seconds)

            logger.info(
                "🔄 Incrementally updating index after Agent OS content changes..."
            )
            try:
                # Import here to avoid circular dependency
                sys.path.insert(0, str(self.index_path.parent.parent))
                from scripts.build_rag_index import IndexBuilder

                builder = IndexBuilder(
                    index_path=self.index_path,
                    standards_path=self.standards_path,
                    usage_path=(
                        self.usage_path
                        if self.usage_path and self.usage_path.exists()
                        else None
                    ),
                    workflows_path=(
                        self.workflows_path
                        if self.workflows_path and self.workflows_path.exists()
                        else None
                    ),
                    embedding_provider=self.embedding_provider,
                )

                result = builder.build_index(force=False, incremental=True)

                # Reload RAG engine with thread-safe locking
                # The reload_index() method acquires write lock automatically
                if self.rag_engine and result["status"] == "success":
                    self.rag_engine.reload_index()
                    build_type = result.get("build_type", "update")
                    logger.info(
                        "✅ Index %s complete. RAG engine reloaded with fresh index.",
                        build_type,
                    )
                elif result["status"] == "success":
                    logger.info(
                        "✅ Index %s complete.", result.get("build_type", "update")
                    )
                else:
                    logger.warning(
                        "⚠️  Index rebuild had issues: %s",
                        result.get("message", "Unknown error"),
                    )

                self.last_rebuild_time = time.time()
            except Exception as e:
                logger.error("❌ Failed to rebuild index: %s", e, exc_info=True)
            finally:
                self.rebuild_pending = False

        # Run rebuild in background thread
        thread = threading.Thread(target=rebuild_after_debounce, daemon=True)
        thread.start()


__all__ = ["AgentOSFileWatcher"]

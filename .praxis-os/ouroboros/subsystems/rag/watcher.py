"""File Watcher for Incremental Index Updates.

Monitors configured paths for file changes and triggers incremental index updates
via the IndexManager. Implements debouncing to prevent rebuild storms during rapid
changes (e.g., bulk file operations, IDE saves).

Architecture:
    File Change → FileWatcher → IndexManager → Index Class → Update ALL sub-indexes

Key Design Principles:
    - Path-to-Index Mapping: Each path maps to one or more indexes
    - Debouncing: Configurable delay (500ms default) prevents excessive rebuilds
    - Background Processing: Non-blocking file monitoring via threading
    - Clean Separation: Watcher only detects/routes, IndexManager owns update logic

Mission: Keep indexes fresh (<5s from file save to searchable) without overwhelming
the system during bulk changes.
"""

import logging
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ouroboros.config.schemas.indexes import FileWatcherConfig
from ouroboros.subsystems.rag.index_manager import IndexManager
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class FileWatcher:
    """File watcher for incremental index updates.
    
    Monitors configured paths and triggers updates via IndexManager.
    
    Path-to-Index Mapping:
        - .praxis-os/standards/ → ["standards"]
        - src/, lib/, app/ → ["code", "graph", "ast"]
    
    Architecture:
        1. Watchdog detects file change
        2. FileWatcher debounces (500ms default)
        3. FileWatcher maps path → index_names
        4. For each index_name: IndexManager.update_from_watcher(index_name, files)
        5. Index class updates ALL its sub-indexes
    
    Debouncing Strategy:
        - Collects changes in a time window (500ms default)
        - Triggers update after quiet period
        - Groups files by affected indexes
    """
    
    def __init__(
        self,
        config: FileWatcherConfig,
        index_manager: IndexManager,
        path_mappings: Dict[str, List[str]],
    ):
        """Initialize file watcher.
        
        Args:
            config: FileWatcherConfig from MCPConfig
            index_manager: IndexManager instance for routing updates
            path_mappings: Path → [index_names] mapping
                Example: {
                    ".praxis-os/standards/": ["standards"],
                    "src/": ["code", "graph", "ast"],
                }
        
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.index_manager = index_manager
        self.path_mappings = path_mappings
        
        # Watchdog components
        self._observer: Any | None = None
        self._handler: _FileChangeHandler | None = None
        
        # Debouncing state
        self._pending_changes: Dict[str, Set[Path]] = defaultdict(set)  # index_name → {files}
        self._debounce_timer: threading.Timer | None = None
        self._lock = threading.Lock()
        
        logger.info(
            "FileWatcher initialized (debounce=%dms, patterns=%s)",
            self.config.debounce_ms,
            self.config.watch_patterns
        )
    
    def start(self) -> None:
        """Start monitoring configured paths.
        
        Creates watchdog Observer and starts monitoring all configured paths.
        
        Raises:
            ActionableError: If start fails (e.g., permission denied)
        """
        if not self.config.enabled:
            logger.info("File watching disabled in config")
            return
        
        if self._observer is not None:
            logger.warning("FileWatcher already started")
            return
        
        try:
            self._observer = Observer()
            self._handler = _FileChangeHandler(
                watcher=self,
                watch_patterns=self.config.watch_patterns
            )
            
            # Schedule monitoring for each configured path
            for path_str in self.path_mappings.keys():
                path = Path(path_str)
                if not path.exists():
                    logger.warning("Watch path does not exist: %s", path)
                    continue
                
                self._observer.schedule(
                    self._handler,
                    str(path),
                    recursive=True  # Watch subdirectories
                )
                logger.info("📁 Watching: %s", path)
            
            self._observer.start()
            logger.info("✅ FileWatcher started")
            
        except Exception as e:
            raise ActionableError(
                what_failed="FileWatcher start",
                why_failed=str(e),
                how_to_fix="Check that watch paths exist and are readable. Ensure watchdog is installed: pip install watchdog"
            ) from e
    
    def stop(self) -> None:
        """Stop monitoring.
        
        Stops the watchdog Observer and cleans up resources.
        """
        if self._observer is None:
            return
        
        try:
            self._observer.stop()
            self._observer.join(timeout=5.0)
            
            # Cancel any pending debounce timer
            with self._lock:
                if self._debounce_timer is not None:
                    self._debounce_timer.cancel()
                    self._debounce_timer = None
            
            logger.info("✅ FileWatcher stopped")
            
        except Exception as e:
            logger.error("Failed to stop FileWatcher: %s", e, exc_info=True)
        finally:
            self._observer = None
            self._handler = None
    
    def _on_file_event(self, event: FileSystemEvent) -> None:
        """Handle file event from watchdog.
        
        Called by _FileChangeHandler when a file changes.
        Debounces changes and schedules index updates.
        
        Args:
            event: FileSystemEvent from watchdog
        """
        if event.is_directory:
            return
        
        file_path = Path(str(event.src_path))
        event_type = event.event_type  # 'created', 'modified', 'deleted'
        
        # Determine which indexes need updating
        affected_indexes = self._get_affected_indexes(file_path)
        
        if not affected_indexes:
            logger.debug("File change ignored (no matching indexes): %s", file_path.name)
            return
        
        logger.info("📝 File %s: %s → indexes: %s", event_type, file_path.name, affected_indexes)
        
        # Add to pending changes for each affected index
        with self._lock:
            for index_name in affected_indexes:
                self._pending_changes[index_name].add(file_path)
            
            # Reset debounce timer
            self._reset_debounce_timer()
    
    def _get_affected_indexes(self, file_path: Path) -> List[str]:
        """Determine which indexes are affected by a file change.
        
        Maps file path to index names using path_mappings.
        
        Args:
            file_path: Changed file path
            
        Returns:
            List of index names that should be updated
        
        Example:
            >>> watcher._get_affected_indexes(Path("src/module.py"))
            ["code", "graph", "ast"]
            
            >>> watcher._get_affected_indexes(Path(".praxis-os/standards/doc.md"))
            ["standards"]
        """
        affected = []
        
        for watch_path_str, index_names in self.path_mappings.items():
            watch_path = Path(watch_path_str)
            
            # Check if file is under this watch path
            try:
                file_path.relative_to(watch_path)
                affected.extend(index_names)
            except ValueError:
                # Not a subpath
                continue
        
        return list(set(affected))  # Remove duplicates
    
    def _reset_debounce_timer(self) -> None:
        """Reset debounce timer.
        
        Cancels existing timer and starts a new one.
        Must be called with self._lock held.
        """
        # Cancel existing timer
        if self._debounce_timer is not None:
            self._debounce_timer.cancel()
        
        # Start new timer
        delay_seconds = self.config.debounce_ms / 1000.0
        self._debounce_timer = threading.Timer(
            delay_seconds,
            self._process_pending_changes
        )
        self._debounce_timer.daemon = True
        self._debounce_timer.start()
    
    def _process_pending_changes(self) -> None:
        """Process pending changes after debounce period.
        
        Called by debounce timer after quiet period.
        Dispatches batched updates to IndexManager.
        """
        # Collect pending changes under lock
        with self._lock:
            changes_to_process = dict(self._pending_changes)
            self._pending_changes.clear()
            self._debounce_timer = None
        
        if not changes_to_process:
            return
        
        logger.info("🔄 Processing %d pending index updates...", len(changes_to_process))
        
        # Dispatch to IndexManager for each affected index
        for index_name, files in changes_to_process.items():
            try:
                logger.info(
                    "Updating %s index (%d files)...",
                    index_name,
                    len(files)
                )
                
                self.index_manager.update_from_watcher(
                    index_name=index_name,
                    changed_files=list(files)
                )
                
                logger.info("✅ %s index updated", index_name)
                
            except Exception as e:
                logger.error(
                    "❌ Failed to update %s index: %s",
                    index_name,
                    e,
                    exc_info=True
                )
                # Continue processing other indexes


class _FileChangeHandler(FileSystemEventHandler):
    """Internal handler for watchdog file system events.
    
    Filters events by file pattern and delegates to FileWatcher.
    """
    
    def __init__(self, watcher: FileWatcher, watch_patterns: List[str]):
        """Initialize handler.
        
        Args:
            watcher: Parent FileWatcher instance
            watch_patterns: File patterns to watch (e.g., ['*.md', '*.py'])
        """
        super().__init__()
        self.watcher = watcher
        self.watch_patterns = watch_patterns
    
    def _should_process(self, file_path: Path) -> bool:
        """Check if file matches watch patterns.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file should be processed
        """
        # Check against patterns
        for pattern in self.watch_patterns:
            if file_path.match(pattern):
                return True
        return False
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation."""
        if not event.is_directory and self._should_process(Path(str(event.src_path))):
            self.watcher._on_file_event(event)
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification."""
        if not event.is_directory and self._should_process(Path(str(event.src_path))):
            self.watcher._on_file_event(event)
    
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion."""
        if not event.is_directory and self._should_process(Path(str(event.src_path))):
            self.watcher._on_file_event(event)


__all__ = ["FileWatcher"]

"""File-based locking manager for index operations.

Prevents concurrent access corruption during index build/update operations.
Uses fcntl-based file locking on Unix systems (POSIX compliance).

Thread Safety:
    - Designed for process-level locking (prevents multiple MCP server instances)
    - File locks are advisory (cooperative locking model)
    - Exclusive locks block all other access (build, update)
    - Shared locks allow concurrent reads (search operations)

Platform Support:
    - Unix/Linux/macOS: Full fcntl-based locking
    - Windows: Stub implementation (logs warning, returns True)

Usage:
    >>> lock_mgr = IndexLockManager("standards", Path("/path/to/.cache/rag"))
    >>> with lock_mgr.exclusive_lock():
    ...     # Build or update index (exclusive access)
    ...     pass
    >>> with lock_mgr.shared_lock():
    ...     # Search index (shared access, blocks during exclusive ops)
    ...     pass

Traceability:
    - FR-003: Locking mechanism prevents corruption
    - NFR-R1: Reliability target (0 corruption incidents per month)
"""

import atexit
import logging
import platform
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

# Platform-specific imports
try:
    import fcntl  # Unix/Linux/macOS only

    FCNTL_AVAILABLE = True
except ImportError:
    FCNTL_AVAILABLE = False

from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class IndexLockManager:
    """File-based lock manager for preventing concurrent index corruption.

    Provides process-level locking using fcntl (Unix/Linux/macOS) or stub
    implementation (Windows). Supports both shared (read) and exclusive (write)
    locks via context managers.

    Attributes:
        index_name: Name of the index (e.g., "standards", "code")
        lock_dir: Directory where lock files are stored
        lock_file_path: Full path to this index's lock file
        _lock_file: Open file handle (kept open during lock lifetime)

    Example:
        >>> manager = IndexLockManager("standards", Path("/tmp/locks"))
        >>> with manager.exclusive_lock():
        ...     rebuild_index()  # Exclusive access guaranteed
        >>> with manager.shared_lock():
        ...     search_index()  # Shared access (multiple readers OK)
    """

    def __init__(self, index_name: str, lock_dir: Path) -> None:
        """Initialize lock manager for an index.

        Args:
            index_name: Identifier for the index (used in lock filename)
            lock_dir: Directory to store lock files (created if missing)

        Raises:
            ActionableError: If lock directory cannot be created
        """
        self.index_name = index_name
        self.lock_dir = lock_dir
        self.lock_file_path = lock_dir / f"{index_name}.lock"
        self._lock_file: Optional[object] = None

        # Create lock directory if it doesn't exist
        try:
            self.lock_dir.mkdir(parents=True, exist_ok=True)
            logger.debug("Lock directory ready: %s", self.lock_dir)
        except Exception as e:
            raise ActionableError(
                what_failed=f"Create lock directory: {lock_dir}",
                why_failed=str(e),
                how_to_fix="Ensure parent directory is writable and accessible",
            ) from e

        # Register cleanup handler (close lock file on exit)
        atexit.register(self._cleanup)

    def acquire_shared(self, blocking: bool = True) -> bool:
        """Acquire shared lock (multiple readers allowed).

        Shared locks allow concurrent read operations (searches) while blocking
        exclusive operations (builds/updates). Multiple processes can hold
        shared locks simultaneously.

        Args:
            blocking: If True, wait for lock. If False, fail immediately if locked.

        Returns:
            True if lock acquired, False if non-blocking and lock unavailable

        Raises:
            ActionableError: If lock acquisition fails (process error)
        """
        return self._acquire_lock(shared=True, blocking=blocking)

    def acquire_exclusive(self, blocking: bool = True) -> bool:
        """Acquire exclusive lock (single writer, blocks all others).

        Exclusive locks provide sole access for build/update operations. Blocks
        all other access (shared and exclusive) until released.

        Args:
            blocking: If True, wait for lock. If False, fail immediately if locked.

        Returns:
            True if lock acquired, False if non-blocking and lock unavailable

        Raises:
            ActionableError: If lock acquisition fails (process error)
        """
        return self._acquire_lock(shared=False, blocking=blocking)

    def release(self) -> None:
        """Release currently held lock.

        Safe to call even if no lock is held (no-op in that case).
        """
        if self._lock_file is not None:
            try:
                # Close file (automatically releases fcntl lock)
                self._lock_file.close()  # type: ignore
                logger.debug("Lock released: %s", self.index_name)
            except Exception as e:
                logger.warning("Error releasing lock for %s: %s", self.index_name, e)
            finally:
                self._lock_file = None

    @contextmanager
    def exclusive_lock(self, blocking: bool = True) -> Generator[None, None, None]:
        """Context manager for exclusive lock (build/update operations).

        Example:
            >>> with lock_mgr.exclusive_lock():
            ...     build_index()  # Exclusive access

        Args:
            blocking: If True, wait for lock. If False, raise if unavailable.

        Yields:
            None (lock held during context)

        Raises:
            ActionableError: If lock cannot be acquired
        """
        acquired = self.acquire_exclusive(blocking=blocking)
        if not acquired:
            raise ActionableError(
                what_failed=f"Acquire exclusive lock for '{self.index_name}'",
                why_failed="Lock already held by another process",
                how_to_fix=(
                    "Options:\n"
                    "1. Wait for other process to finish\n"
                    "2. Close other Cursor/IDE instances\n"
                    "3. Stop MCP server: pkill -f 'ouroboros.server'\n"
                    f"4. Force remove lock: rm {self.lock_file_path}"
                ),
            )
        try:
            yield
        finally:
            self.release()

    @contextmanager
    def shared_lock(self, blocking: bool = True) -> Generator[None, None, None]:
        """Context manager for shared lock (search operations).

        Example:
            >>> with lock_mgr.shared_lock():
            ...     search_index()  # Shared access (concurrent readers OK)

        Args:
            blocking: If True, wait for lock. If False, raise if unavailable.

        Yields:
            None (lock held during context)

        Raises:
            ActionableError: If lock cannot be acquired
        """
        acquired = self.acquire_shared(blocking=blocking)
        if not acquired:
            raise ActionableError(
                what_failed=f"Acquire shared lock for '{self.index_name}'",
                why_failed="Exclusive lock held by another process (rebuild in progress)",
                how_to_fix="Wait for rebuild to complete (usually <60s)",
            )
        try:
            yield
        finally:
            self.release()

    def _acquire_lock(self, shared: bool, blocking: bool) -> bool:
        """Internal: Acquire lock with specified mode.

        Args:
            shared: True for shared lock (LOCK_SH), False for exclusive (LOCK_EX)
            blocking: True to block until acquired, False to fail immediately

        Returns:
            True if acquired, False if non-blocking and unavailable

        Raises:
            ActionableError: If locking fails (IO error, permission denied)
        """
        # Windows stub (fcntl not available)
        if not FCNTL_AVAILABLE:
            logger.warning(
                "File locking not supported on Windows (stub implementation). "
                "Index corruption possible with concurrent access."
            )
            return True  # Stub: Always "succeeds"

        try:
            # Open lock file (create if doesn't exist, mode 600 for security)
            self._lock_file = open(  # noqa: SIM115
                self.lock_file_path,
                mode="a",  # Append mode (create if missing)
            )

            # Set restrictive permissions (owner read/write only)
            self.lock_file_path.chmod(0o600)

            # Acquire lock using fcntl
            lock_mode = fcntl.LOCK_SH if shared else fcntl.LOCK_EX
            if not blocking:
                lock_mode |= fcntl.LOCK_NB  # Non-blocking flag

            fcntl.flock(self._lock_file, lock_mode)

            lock_type = "shared" if shared else "exclusive"
            logger.debug("✅ %s lock acquired: %s", lock_type.capitalize(), self.index_name)
            return True

        except IOError as e:
            # Non-blocking lock unavailable (expected, not an error)
            if not blocking and e.errno in (11, 35):  # EAGAIN or EWOULDBLOCK
                logger.debug("Lock unavailable (non-blocking): %s", self.index_name)
                if self._lock_file is not None:
                    self._lock_file.close()  # type: ignore
                    self._lock_file = None
                return False

            # Actual error (permission denied, disk full, etc.)
            raise ActionableError(
                what_failed=f"Acquire lock for '{self.index_name}'",
                why_failed=str(e),
                how_to_fix=(
                    "Common causes:\n"
                    "1. MCP server already running (check: ps aux | grep ouroboros)\n"
                    "2. Cursor IDE has server running (close and reopen)\n"
                    "3. Stale lock file (safe to delete if no processes running)\n"
                    f"4. Permission issue (check: ls -l {self.lock_file_path})\n"
                    "5. Disk full (check: df -h)"
                ),
            ) from e

    def _cleanup(self) -> None:
        """Cleanup: Release lock and close file on process exit.

        Called automatically by atexit handler. Safe to call multiple times.
        """
        self.release()

        # Remove lock file if it exists (cleanup)
        try:
            if self.lock_file_path.exists():
                self.lock_file_path.unlink()
                logger.debug("Lock file removed: %s", self.lock_file_path)
        except Exception as e:
            logger.debug("Could not remove lock file: %s", e)

    def __repr__(self) -> str:
        """String representation for debugging."""
        locked = "locked" if self._lock_file is not None else "unlocked"
        return f"IndexLockManager(index='{self.index_name}', status={locked})"


"""
Initialization lock for defending against concurrent MCP client spawns.

Handles race conditions where MCP clients (like Cursor) spawn multiple server
instances simultaneously. Uses file-based locking to ensure only one process
completes initialization.

Design Philosophy:
    - Defensive: Handle misbehaving clients gracefully
    - Fast-fail: Don't waste resources on duplicate processes
    - Clean exit: Duplicate processes exit silently (not an error)
    - Cross-platform: Works on Unix and Windows

Usage:
    >>> from pathlib import Path
    >>> from ouroboros.foundation.init_lock import InitLock
    >>> 
    >>> base_path = Path(".praxis-os")
    >>> lock = InitLock(base_path, timeout_seconds=10)
    >>> 
    >>> if lock.acquire():
    ...     try:
    ...         # Initialize server (indexes, subsystems, etc.)
    ...         initialize_server()
    ...     finally:
    ...         lock.release()
    ... else:
    ...     # Another process is initializing, exit gracefully
    ...     sys.exit(0)

Traceability:
    - Addresses Cursor MCP race condition bug (3x CreateClient)
    - Prevents DuckDB lock conflicts during concurrent initialization
    - FR-026: Defensive architecture for misbehaving MCP clients
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class InitLock:
    """
    File-based initialization lock for preventing concurrent server starts.
    
    Defends against MCP clients spawning multiple server instances by ensuring
    only ONE process completes initialization. Other processes detect the lock
    and exit gracefully.
    
    Lock Strategy:
        1. First process creates lock file with its PID
        2. Subsequent processes check lock file:
           - If PID still running → wait (timeout) → exit gracefully
           - If PID dead (stale lock) → claim lock and proceed
        3. On successful init → remove lock file
        4. On crash → lock file becomes stale (detectable via PID)
    
    Attributes:
        lock_file: Path to .init.lock file
        timeout_seconds: Max time to wait for existing init
        pid: Current process PID
        acquired: Whether this process holds the lock
    
    Example:
        >>> lock = InitLock(Path(".praxis-os"), timeout_seconds=10)
        >>> if lock.acquire():
        ...     print("Won the race! Initializing...")
        ...     # ... initialize server ...
        ...     lock.release()
        ... else:
        ...     print("Another process is initializing. Exiting gracefully.")
        ...     sys.exit(0)
    """
    
    LOCK_FILE_NAME = ".init.lock"
    
    def __init__(self, base_path: Path, timeout_seconds: int = 10):
        """
        Initialize lock manager.
        
        Args:
            base_path: Path to .praxis-os directory
            timeout_seconds: Max seconds to wait for existing initialization
                - If another process takes longer, assume it's hung/crashed
                - Default 10s is reasonable for server startup
        """
        self.lock_file = base_path / ".cache" / self.LOCK_FILE_NAME
        self.timeout_seconds = timeout_seconds
        self.pid = os.getpid()
        self.acquired = False
        
        # Ensure cache directory exists
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
    
    def acquire(self) -> bool:
        """
        Attempt to acquire initialization lock.
        
        Returns:
            True if lock acquired (proceed with initialization)
            False if another process is initializing (exit gracefully)
        
        Logic:
            1. If no lock file → create it, acquire lock
            2. If lock file exists:
               a. Read PID from file
               b. Check if PID is still running
               c. If running → wait (timeout) → return False
               d. If dead → claim stale lock, return True
        
        Example:
            >>> if lock.acquire():
            ...     # Won the race, initialize server
            ...     pass
            ... else:
            ...     # Lost the race, exit gracefully
            ...     sys.exit(0)
        """
        start_time = time.time()
        
        while True:
            # Try to claim lock
            if self._try_claim_lock():
                self.acquired = True
                logger.info(
                    "🔒 Init lock acquired (PID %d) - proceeding with initialization",
                    self.pid
                )
                return True
            
            # Lock exists - check if we should wait or give up
            elapsed = time.time() - start_time
            if elapsed >= self.timeout_seconds:
                logger.warning(
                    "⏱️ Init lock timeout (%ds) - another process may be hung. "
                    "Exiting gracefully to avoid resource conflicts.",
                    self.timeout_seconds
                )
                return False
            
            # Check lock holder
            holder_pid = self._read_lock_holder()
            if holder_pid is None:
                # Lock file disappeared, retry
                continue
            
            if not self._is_process_running(holder_pid):
                # Stale lock (holder died), remove it and claim
                logger.info(
                    "🔓 Stale init lock detected (dead PID %d) - removing stale lock",
                    holder_pid
                )
                try:
                    self.lock_file.unlink(missing_ok=True)
                except Exception as e:
                    logger.warning("Failed to remove stale lock: %s", e)
                continue  # Next iteration will claim it
            
            # Holder is alive and initializing, wait briefly
            logger.debug(
                "⏳ Init lock held by PID %d, waiting... (%.1fs elapsed)",
                holder_pid,
                elapsed
            )
            time.sleep(0.5)  # Poll every 500ms
    
    def release(self) -> None:
        """
        Release initialization lock.
        
        Removes lock file to signal initialization complete.
        Safe to call multiple times.
        
        Example:
            >>> try:
            ...     lock.acquire()
            ...     initialize_server()
            ... finally:
            ...     lock.release()
        """
        if not self.acquired:
            return
        
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
                logger.info("🔓 Init lock released (PID %d)", self.pid)
        except Exception as e:
            logger.warning("Failed to release init lock: %s", e)
        finally:
            self.acquired = False
    
    def _try_claim_lock(self) -> bool:
        """
        Atomically try to create lock file with our PID.
        
        Returns:
            True if lock claimed, False if file already exists
        
        Uses:
            O_CREAT | O_EXCL for atomic file creation (POSIX guarantee)
        """
        try:
            # O_CREAT | O_EXCL = atomic "create if not exists"
            fd = os.open(
                str(self.lock_file),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600  # Owner read/write only
            )
            
            # Write our PID
            os.write(fd, str(self.pid).encode('utf-8'))
            os.close(fd)
            
            return True
            
        except FileExistsError:
            # Lock already held by another process
            return False
        except Exception as e:
            logger.warning("Failed to claim init lock: %s", e)
            return False
    
    def _read_lock_holder(self) -> Optional[int]:
        """
        Read PID of lock holder from lock file.
        
        Returns:
            PID as integer, or None if file missing/corrupted
        """
        try:
            content = self.lock_file.read_text(encoding='utf-8').strip()
            return int(content)
        except (FileNotFoundError, ValueError, OSError):
            return None
    
    @staticmethod
    def _is_process_running(pid: int) -> bool:
        """
        Check if process with given PID is still running.
        
        Args:
            pid: Process ID to check
        
        Returns:
            True if process exists, False otherwise
        
        Cross-platform:
            - Unix: os.kill(pid, 0) - signal 0 checks existence
            - Windows: Use tasklist (fallback)
        """
        try:
            # Signal 0 doesn't kill, just checks if process exists
            # Works on Unix/Linux/macOS
            os.kill(pid, 0)
            return True
        except OSError:
            # Process doesn't exist or we don't have permission
            return False
        except AttributeError:
            # Windows doesn't have os.kill(pid, 0)
            # Fallback: check if process exists via tasklist
            import subprocess
            try:
                output = subprocess.check_output(
                    ['tasklist', '/FI', f'PID eq {pid}'],
                    stderr=subprocess.DEVNULL
                )
                return str(pid) in output.decode()
            except Exception:
                # If we can't check, assume it's running (safer)
                return True
    
    def __enter__(self):
        """Context manager entry."""
        if not self.acquire():
            # Another process is initializing, exit gracefully
            import sys
            logger.info("Another process is initializing. Exiting gracefully.")
            sys.exit(0)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False  # Don't suppress exceptions
    
    def __del__(self):
        """Cleanup on garbage collection."""
        self.release()


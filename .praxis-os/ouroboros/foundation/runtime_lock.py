"""
Runtime lock for enforcing singleton MCP server per project.

This module provides the RuntimeLock class which ensures only one ouroboros
MCP server instance runs per project directory by acquiring and holding a
file-based lock for the entire process lifetime.

Traceability:
    FR-001: Singleton Enforcement
    FR-002: Stale Lock Detection
    FR-003: Graceful Degradation
    FR-005: Lock Lifecycle Management
    FR-006: Observability
    FR-007: Lock File Location
"""

import atexit
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class RuntimeLock:
    """
    Runtime lock for enforcing singleton MCP server per project.
    
    Acquired at server startup and held for entire process lifetime.
    Prevents multiple ouroboros instances from running concurrently.
    
    Differences from InitLock:
    - InitLock: Held during initialization only (10s)
    - RuntimeLock: Held for entire server lifetime (hours/days)
    
    Lock Strategy:
    1. Attempt to create lock file atomically (O_CREAT | O_EXCL)
    2. If file exists → check if holder PID is alive
    3. If holder alive → exit gracefully (another server running)
    4. If holder dead → remove stale lock, retry
    5. On successful acquisition → hold until process exits
    
    Cleanup:
    - Lock file removed on graceful shutdown (atexit handler)
    - Lock file left behind on crash (detected as stale by next spawn)
    
    Security Features:
    - PID reuse mitigation via process name verification
    - Timestamp validation (24-hour old lock timeout)
    - Disk full handling (write verification)
    - Directory DoS mitigation
    - Retry limit (prevents infinite loops)
    
    Traceability:
        FR-001: Singleton enforcement via lifetime lock
        FR-002: Stale lock detection via PID checking
        FR-003: Graceful error handling
        FR-005: Lock lifecycle management
        FR-006: Observability via logging
        FR-007: Lock file location (.cache/.runtime.lock)
    """
    
    LOCK_FILE_NAME = ".runtime.lock"
    
    def __init__(self, base_path: Path) -> None:
        """
        Initialize RuntimeLock.
        
        Args:
            base_path: Path to .praxis-os directory
            
        Traceability:
            FR-007: Lock file location
        """
        self.lock_file = base_path / ".cache" / self.LOCK_FILE_NAME
        self.pid = os.getpid()
        self.acquired = False
        self._max_retries = 3
        
        # Create .cache directory if it doesn't exist
        try:
            self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(
                "Failed to create lock directory %s: %s",
                self.lock_file.parent,
                e
            )
            # Continue anyway - will fail later if directory is truly inaccessible
        
        # Register cleanup handler for graceful shutdown
        atexit.register(self._cleanup)
    
    def acquire(self, _retry_count: int = 0) -> bool:
        """
        Attempt to acquire runtime lock.
        
        Implements retry logic with stale lock detection and cleanup.
        Maximum 3 retries to prevent infinite loops.
        
        Args:
            _retry_count: Internal retry counter (do not set manually)
            
        Returns:
            True if lock acquired, False if another server is running
            
        Traceability:
            FR-001: Singleton enforcement
            FR-002: Stale lock detection
            FR-003: Graceful degradation
        """
        # Check retry limit (prevent infinite loops)
        if _retry_count >= self._max_retries:
            logger.error(
                "Failed to acquire RuntimeLock after %d retries: %s",
                self._max_retries,
                self.lock_file
            )
            return False
        
        # Log retry attempts
        if _retry_count > 0:
            logger.debug(
                "Retrying RuntimeLock acquisition (attempt %d/%d)",
                _retry_count + 1,
                self._max_retries
            )
        
        # Try to claim lock atomically
        if self._try_claim_lock():
            self.acquired = True
            logger.info(
                "RuntimeLock acquired successfully: PID=%d, file=%s",
                self.pid,
                self.lock_file
            )
            return True
        
        # Lock file exists - check if holder is alive
        holder_info = self._read_lock_holder()
        
        if holder_info is None:
            # Corrupted lock file - remove and retry
            logger.warning(
                "RuntimeLock file is corrupted, removing: %s",
                self.lock_file
            )
            try:
                self.lock_file.unlink()
            except Exception as e:
                logger.warning(
                    "Failed to remove corrupted lock file: %s",
                    e
                )
            return self.acquire(_retry_count + 1)
        
        holder_pid, holder_timestamp = holder_info
        
        # Check lock age (24-hour timeout for old locks)
        if holder_timestamp > 0:  # Skip for old format (timestamp=0)
            lock_age_seconds = time.time() - holder_timestamp
            lock_age_hours = lock_age_seconds / 3600
            
            if lock_age_hours > 24:
                # Lock is very old - assume stale
                logger.warning(
                    "RuntimeLock is %.1f hours old (holder PID=%d), assuming stale: %s",
                    lock_age_hours,
                    holder_pid,
                    self.lock_file
                )
                try:
                    self.lock_file.unlink()
                except Exception as e:
                    logger.warning(
                        "Failed to remove old lock file: %s",
                        e
                    )
                return self.acquire(_retry_count + 1)
        
        # Check if holder process is alive and is ouroboros
        if not self._is_process_running(holder_pid):
            # Holder is dead or not ouroboros - remove stale lock
            logger.info(
                "RuntimeLock holder (PID=%d) is not running or not ouroboros, removing stale lock: %s",
                holder_pid,
                self.lock_file
            )
            try:
                self.lock_file.unlink()
            except Exception as e:
                logger.warning(
                    "Failed to remove stale lock file: %s",
                    e
                )
            return self.acquire(_retry_count + 1)
        
        # Holder is alive and is ouroboros - another server is running
        logger.info(
            "RuntimeLock is held by another ouroboros server (PID=%d): %s",
            holder_pid,
            self.lock_file
        )
        return False
    
    def release(self) -> None:
        """
        Release runtime lock.
        
        Called on graceful shutdown (finally block + atexit handler).
        Idempotent - safe to call multiple times.
        
        Traceability:
            FR-005: Lock lifecycle management
            FR-006: Observability
        """
        # Check if lock was acquired by this process
        if not self.acquired:
            return  # Not acquired, nothing to do
        
        try:
            # Remove lock file
            self.lock_file.unlink()
            logger.info(
                "RuntimeLock released: PID=%d, file=%s",
                self.pid,
                self.lock_file
            )
        except FileNotFoundError:
            # Lock file already removed (race condition or manual deletion)
            logger.debug(
                "RuntimeLock file already removed: %s",
                self.lock_file
            )
        except Exception as e:
            # Other errors (permission denied, etc.)
            logger.warning(
                "Failed to release RuntimeLock: %s (error: %s)",
                self.lock_file,
                e
            )
        finally:
            # Always mark as not acquired
            self.acquired = False
    
    def _try_claim_lock(self) -> bool:
        """
        Atomically create lock file with PID and timestamp.
        
        Uses O_CREAT | O_EXCL for atomic creation.
        Writes "PID TIMESTAMP" format for PID reuse mitigation.
        Verifies write succeeded (disk full detection).
        Handles directory at lock path (DoS mitigation).
        
        Returns:
            True if lock claimed, False if file already exists
            
        Traceability:
            FR-004: Platform-specific atomic file creation
            FR-006: Observability
            Security: Disk full handling, directory DoS mitigation
        """
        try:
            # Atomic file creation with exclusive access
            fd = os.open(
                str(self.lock_file),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600  # Owner read/write only
            )
            
            try:
                # Write PID and timestamp for PID reuse mitigation
                content = f"{self.pid} {int(time.time())}"
                content_bytes = content.encode('utf-8')
                
                # Write and verify (disk full detection)
                bytes_written = os.write(fd, content_bytes)
                
                if bytes_written != len(content_bytes):
                    # Disk full or write failure
                    logger.warning(
                        "Incomplete write to lock file (expected %d bytes, wrote %d)",
                        len(content_bytes),
                        bytes_written
                    )
                    # Clean up partial file
                    try:
                        self.lock_file.unlink()
                    except Exception as cleanup_error:
                        logger.warning(
                            "Failed to clean up partial lock file: %s",
                            cleanup_error
                        )
                    return False
                
                logger.info(
                    "RuntimeLock acquired: PID=%d, file=%s",
                    self.pid,
                    self.lock_file
                )
                return True
                
            finally:
                # Always close file descriptor
                os.close(fd)
                
        except FileExistsError:
            # Lock file already exists - another server is running
            logger.debug(
                "RuntimeLock file already exists: %s",
                self.lock_file
            )
            return False
            
        except IsADirectoryError:
            # Directory at lock path (DoS mitigation)
            logger.warning(
                "Directory exists at lock path: %s (removing)",
                self.lock_file
            )
            try:
                # Remove directory to allow lock creation
                shutil.rmtree(self.lock_file)
            except Exception as e:
                logger.warning(
                    "Failed to remove directory at lock path: %s",
                    e
                )
            return False
            
        except Exception as e:
            # Unexpected error - log and return False (conservative)
            logger.warning(
                "Failed to claim RuntimeLock: %s",
                e,
                exc_info=True
            )
            # Try to clean up if file was created
            try:
                if self.lock_file.exists():
                    self.lock_file.unlink()
            except Exception:
                pass  # Best effort cleanup
            return False
    
    def _read_lock_holder(self) -> Optional[tuple[int, int]]:
        """
        Read PID and timestamp from lock file.
        
        Lock file format: "PID TIMESTAMP" (space-separated)
        Old format: "PID" (no timestamp, treated as very old)
        
        Returns:
            Tuple of (PID, timestamp) if valid, None if corrupted/missing
            
        Traceability:
            FR-002: Stale lock detection
            FR-003: Graceful degradation
            Security: Timestamp validation for PID reuse mitigation
        """
        try:
            # Read lock file content
            content = self.lock_file.read_text(encoding='utf-8').strip()
            
            # Parse format: "PID TIMESTAMP" or "PID" (old format)
            parts = content.split()
            
            if len(parts) == 2:
                # New format: PID + timestamp
                pid = int(parts[0])
                timestamp = int(parts[1])
                return (pid, timestamp)
            elif len(parts) == 1:
                # Old format: PID only (backward compatibility)
                pid = int(parts[0])
                logger.debug(
                    "Lock file uses old format (PID only): %s",
                    self.lock_file
                )
                return (pid, 0)  # timestamp=0 indicates old format
            else:
                # Invalid format
                logger.warning(
                    "Lock file has invalid format (expected 1-2 parts, got %d): %s",
                    len(parts),
                    self.lock_file
                )
                return None
                
        except FileNotFoundError:
            # Lock file doesn't exist
            logger.debug("Lock file not found: %s", self.lock_file)
            return None
            
        except ValueError as e:
            # Invalid PID or timestamp (not integers)
            logger.warning(
                "Lock file contains invalid data: %s (error: %s)",
                self.lock_file,
                e
            )
            return None
            
        except OSError as e:
            # Other file system errors (permission denied, etc.)
            logger.warning(
                "Failed to read lock file: %s (error: %s)",
                self.lock_file,
                e
            )
            return None
    
    @staticmethod
    def _get_process_cmdline(pid: int) -> Optional[str]:
        """
        Get process command line using stdlib only.
        
        Tries /proc first (Linux, WSL2), falls back to ps command (macOS, Unix).
        
        Args:
            pid: Process ID to check
            
        Returns:
            Command line string if readable, None if process doesn't exist
            or permission denied
            
        Traceability:
            Security: Process name verification for PID reuse mitigation
        """
        # Try /proc first (Linux, WSL2)
        try:
            with open(f"/proc/{pid}/cmdline", 'rb') as f:
                cmdline_bytes = f.read()
                # /proc/pid/cmdline uses null bytes as separators
                cmdline = cmdline_bytes.decode('utf-8', errors='ignore')
                cmdline = cmdline.replace('\x00', ' ').strip()
                if cmdline:
                    return cmdline
        except (FileNotFoundError, PermissionError, OSError):
            # /proc not available or PID doesn't exist
            pass
        
        # Fall back to ps command (macOS, Unix)
        try:
            result = subprocess.run(
                ['ps', '-p', str(pid), '-o', 'command='],
                capture_output=True,
                text=True,
                timeout=0.5
            )
            if result.returncode == 0:
                cmdline = result.stdout.strip()
                if cmdline:
                    return cmdline
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # ps command failed or timed out
            pass
        
        # Could not determine command line
        return None
    
    @staticmethod
    def _is_process_running(pid: int) -> bool:
        """
        Check if process is running AND is ouroboros.
        
        Verifies both PID existence and process name to mitigate PID reuse attacks.
        Conservative: assumes process is running if verification fails.
        
        Args:
            pid: Process ID to check
            
        Returns:
            True if process is running and is ouroboros, False otherwise
            
        Traceability:
            FR-002: Stale lock detection
            NFR-R1: Conservative PID checking (zero false positives)
            Security: Process name verification for PID reuse mitigation
        """
        # Handle invalid PIDs
        if pid <= 0:
            return False
        
        try:
            # Check if PID exists
            os.kill(pid, 0)
            
            # PID exists - verify it's actually ouroboros
            cmdline = RuntimeLock._get_process_cmdline(pid)
            
            if cmdline is None:
                # Can't verify (permission denied, etc.)
                # Conservative: assume valid (NFR-R1)
                logger.debug(
                    "Cannot verify process name for PID %d (permission denied or /proc unavailable)",
                    pid
                )
                return True
            
            # Check if it's ouroboros
            if 'ouroboros' in cmdline.lower():
                logger.debug("PID %d is ouroboros: %s", pid, cmdline[:100])
                return True
            
            # PID exists but is NOT ouroboros → PID reuse!
            logger.warning(
                "PID %d is not ouroboros (cmd='%s') - PID reuse detected!",
                pid,
                cmdline[:100]
            )
            return False
            
        except OSError:
            # PID doesn't exist
            return False
    
    def _cleanup(self) -> None:
        """
        Cleanup on process exit (atexit handler).
        
        Removes lock file if this process holds the lock.
        Best-effort cleanup - logs warnings on failure but doesn't raise.
        
        Traceability:
            FR-005: Lock lifecycle management
            FR-006: Observability
        """
        self.release()


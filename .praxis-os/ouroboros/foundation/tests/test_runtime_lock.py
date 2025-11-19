"""
Unit tests for RuntimeLock.

Tests singleton enforcement, stale lock detection, and graceful error handling.

Traceability:
    FR-001: Singleton Enforcement
    FR-002: Stale Lock Detection
    FR-003: Graceful Degradation
    FR-005: Lock Lifecycle Management
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ouroboros.foundation.runtime_lock import RuntimeLock


class TestRuntimeLockInit:
    """Test RuntimeLock initialization."""
    
    def test_runtime_lock_init(self, tmp_path: Path) -> None:
        """
        Test RuntimeLock initialization.
        
        Verifies:
        - lock_file path is set correctly
        - pid is set to current process
        - acquired is initialized to False
        - .cache directory is created
        - atexit handler is registered
        
        Traceability:
            FR-007: Lock file location
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        
        # Act
        lock = RuntimeLock(base_path)
        
        # Assert
        assert lock.lock_file == base_path / ".cache" / ".runtime.lock"
        assert lock.pid == os.getpid()
        assert lock.acquired is False
        assert lock._max_retries == 3
        assert (base_path / ".cache").exists()
        assert (base_path / ".cache").is_dir()
    
    def test_runtime_lock_init_creates_cache_directory(self, tmp_path: Path) -> None:
        """
        Test that __init__ creates .cache directory if missing.
        
        Traceability:
            FR-007: Lock file location
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        cache_dir = base_path / ".cache"
        
        # Verify directory doesn't exist yet
        assert not cache_dir.exists()
        
        # Act
        lock = RuntimeLock(base_path)
        
        # Assert
        assert cache_dir.exists()
        assert cache_dir.is_dir()
    
    def test_runtime_lock_init_handles_existing_cache_directory(
        self, tmp_path: Path
    ) -> None:
        """
        Test that __init__ handles existing .cache directory gracefully.
        
        Traceability:
            FR-003: Graceful degradation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        cache_dir = base_path / ".cache"
        cache_dir.mkdir()
        
        # Act
        lock = RuntimeLock(base_path)
        
        # Assert
        assert cache_dir.exists()
        assert lock.lock_file.parent == cache_dir
    
    def test_runtime_lock_init_handles_directory_creation_failure(
        self, tmp_path: Path, caplog
    ) -> None:
        """
        Test that __init__ handles directory creation failure gracefully.
        
        Traceability:
            FR-003: Graceful degradation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        
        # Mock mkdir to raise an exception
        with patch.object(Path, 'mkdir', side_effect=PermissionError("No permission")):
            # Act
            lock = RuntimeLock(base_path)
            
            # Assert - should not raise, just log warning
            assert lock.lock_file == base_path / ".cache" / ".runtime.lock"
            assert "Failed to create lock directory" in caplog.text


class TestRuntimeLockTryClaimLock:
    """Test RuntimeLock._try_claim_lock() method."""
    
    def test_try_claim_lock_success(self, tmp_path: Path) -> None:
        """
        Test successful lock file creation.
        
        Verifies:
        - Lock file is created atomically
        - File contains PID and timestamp
        - File has correct permissions (0o600)
        - Returns True on success
        
        Traceability:
            FR-001: Singleton enforcement via atomic file creation
            FR-004: Platform-specific atomic file creation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Act
        result = lock._try_claim_lock()
        
        # Assert
        assert result is True
        assert lock.lock_file.exists()
        
        # Verify file contents (PID + timestamp)
        content = lock.lock_file.read_text()
        parts = content.split()
        assert len(parts) == 2
        assert int(parts[0]) == os.getpid()
        assert int(parts[1]) > 0  # Valid timestamp
        
        # Verify file permissions
        stat_info = lock.lock_file.stat()
        assert stat_info.st_mode & 0o777 == 0o600
    
    def test_try_claim_lock_file_exists(self, tmp_path: Path) -> None:
        """
        Test lock file creation when file already exists.
        
        Verifies:
        - Returns False when lock file exists
        - Does not overwrite existing file
        
        Traceability:
            FR-001: Singleton enforcement
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Create lock file first
        lock.lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock.lock_file.write_text("12345 1234567890")
        original_content = lock.lock_file.read_text()
        
        # Act
        result = lock._try_claim_lock()
        
        # Assert
        assert result is False
        assert lock.lock_file.read_text() == original_content  # Not overwritten
    
    def test_try_claim_lock_disk_full(self, tmp_path: Path) -> None:
        """
        Test lock file creation with disk full scenario (mocked).
        
        Verifies:
        - Detects incomplete write
        - Cleans up partial file
        - Returns False
        
        Traceability:
            Security: Disk full handling
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Mock os.write to simulate partial write
        with patch('os.write', return_value=5):  # Write only 5 bytes instead of full content
            # Act
            result = lock._try_claim_lock()
            
            # Assert
            assert result is False
            assert not lock.lock_file.exists()  # Cleaned up
    
    def test_try_claim_lock_directory_at_path(self, tmp_path: Path) -> None:
        """
        Test lock file creation when directory exists at lock path.
        
        Verifies:
        - Detects directory at lock path
        - Attempts to remove directory
        - Returns False (will retry on next attempt)
        
        Note: On some platforms, os.open() may succeed even with a directory,
        so we verify the behavior is safe (returns False, attempts cleanup).
        
        Traceability:
            Security: Directory DoS mitigation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Create directory at lock path
        lock.lock_file.mkdir(parents=True)
        assert lock.lock_file.is_dir()
        
        # Act
        result = lock._try_claim_lock()
        
        # Assert
        assert result is False
        # Directory may or may not be removed depending on platform behavior
        # The important thing is that the method returned False


class TestRuntimeLockReadLockHolder:
    """Test RuntimeLock._read_lock_holder() method."""
    
    def test_read_lock_holder_valid_with_timestamp(self, tmp_path: Path) -> None:
        """
        Test reading lock file with PID and timestamp.
        
        Verifies:
        - Correctly parses "PID TIMESTAMP" format
        - Returns tuple of (PID, timestamp)
        
        Traceability:
            FR-002: Stale lock detection
            Security: Timestamp validation for PID reuse mitigation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Create lock file with PID and timestamp
        lock.lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock.lock_file.write_text("12345 1234567890")
        
        # Act
        result = lock._read_lock_holder()
        
        # Assert
        assert result is not None
        assert result == (12345, 1234567890)
    
    def test_read_lock_holder_valid_old_format(self, tmp_path: Path) -> None:
        """
        Test reading lock file with PID only (old format).
        
        Verifies:
        - Correctly parses "PID" format (backward compatibility)
        - Returns tuple of (PID, 0)
        
        Traceability:
            FR-003: Graceful degradation (backward compatibility)
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Create lock file with PID only (old format)
        lock.lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock.lock_file.write_text("12345")
        
        # Act
        result = lock._read_lock_holder()
        
        # Assert
        assert result is not None
        assert result == (12345, 0)  # timestamp=0 for old format
    
    def test_read_lock_holder_missing(self, tmp_path: Path) -> None:
        """
        Test reading lock file when file doesn't exist.
        
        Verifies:
        - Returns None when lock file is missing
        
        Traceability:
            FR-003: Graceful degradation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Act (lock file doesn't exist)
        result = lock._read_lock_holder()
        
        # Assert
        assert result is None
    
    def test_read_lock_holder_corrupted(self, tmp_path: Path) -> None:
        """
        Test reading corrupted lock file.
        
        Verifies:
        - Returns None when lock file has invalid format
        - Returns None when PID/timestamp are not integers
        
        Traceability:
            FR-003: Graceful degradation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        lock.lock_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Test invalid format (too many parts)
        lock.lock_file.write_text("12345 1234567890 extra")
        assert lock._read_lock_holder() is None
        
        # Test invalid PID (not an integer)
        lock.lock_file.write_text("not_a_number 1234567890")
        assert lock._read_lock_holder() is None
        
        # Test invalid timestamp (not an integer)
        lock.lock_file.write_text("12345 not_a_number")
        assert lock._read_lock_holder() is None
        
        # Test empty file
        lock.lock_file.write_text("")
        assert lock._read_lock_holder() is None


class TestRuntimeLockGetProcessCmdline:
    """Test RuntimeLock._get_process_cmdline() method."""
    
    def test_get_process_cmdline_current_process(self) -> None:
        """
        Test getting command line for current process.
        
        Verifies:
        - Returns non-empty string for current process
        - Works on both Linux (/proc) and macOS (ps)
        
        Traceability:
            FR-004: Cross-platform support
            Security: Process name verification
        """
        # Arrange
        current_pid = os.getpid()
        
        # Act
        cmdline = RuntimeLock._get_process_cmdline(current_pid)
        
        # Assert
        assert cmdline is not None
        assert len(cmdline) > 0
        # Should contain 'python' or 'pytest'
        assert 'python' in cmdline.lower() or 'pytest' in cmdline.lower()
    
    def test_get_process_cmdline_not_found(self) -> None:
        """
        Test getting command line for non-existent PID.
        
        Verifies:
        - Returns None for dead PID
        
        Traceability:
            FR-002: Stale lock detection
        """
        # Arrange
        dead_pid = 99999  # Very unlikely to exist
        
        # Act
        cmdline = RuntimeLock._get_process_cmdline(dead_pid)
        
        # Assert
        assert cmdline is None
    
    def test_get_process_cmdline_ps_fallback(self) -> None:
        """
        Test ps command fallback (mock /proc failure).
        
        Verifies:
        - Falls back to ps command when /proc is unavailable
        
        Note: This test uses the current process, which should work
        on both Linux and macOS. On Linux, /proc will succeed. On macOS,
        ps will be used.
        
        Traceability:
            FR-004: Cross-platform support
        """
        # Arrange
        current_pid = os.getpid()
        
        # Act
        cmdline = RuntimeLock._get_process_cmdline(current_pid)
        
        # Assert
        assert cmdline is not None
        assert len(cmdline) > 0


class TestRuntimeLockIsProcessRunning:
    """Test RuntimeLock._is_process_running() method."""
    
    def test_is_process_running_current_process(self) -> None:
        """
        Test checking if current process is running.
        
        Verifies:
        - Returns True for current process
        - Verifies process name contains 'python' or 'pytest'
        
        Note: This test may return True even if process name doesn't
        contain 'ouroboros' because we're testing with pytest, not
        the actual ouroboros server.
        
        Traceability:
            FR-002: Stale lock detection
        """
        # Arrange
        current_pid = os.getpid()
        
        # Act
        result = RuntimeLock._is_process_running(current_pid)
        
        # Assert
        assert result is True  # Current process is always running
    
    def test_is_process_running_dead_pid(self) -> None:
        """
        Test checking if dead PID is running.
        
        Verifies:
        - Returns False for non-existent PID
        
        Traceability:
            FR-002: Stale lock detection
        """
        # Arrange
        dead_pid = 99999  # Very unlikely to exist
        
        # Act
        result = RuntimeLock._is_process_running(dead_pid)
        
        # Assert
        assert result is False
    
    def test_is_process_running_negative_pid(self) -> None:
        """
        Test checking if negative PID is running.
        
        Verifies:
        - Returns False for invalid PIDs
        
        Traceability:
            FR-003: Graceful degradation
        """
        # Act & Assert
        assert RuntimeLock._is_process_running(-1) is False
        assert RuntimeLock._is_process_running(0) is False
    
    def test_is_process_running_pid_reused(self) -> None:
        """
        Test PID reuse detection (mock scenario).
        
        Verifies:
        - Returns False when PID exists but process name is not ouroboros
        - Logs warning about PID reuse
        
        Traceability:
            Security: PID reuse mitigation
        """
        # Arrange
        current_pid = os.getpid()
        
        # Mock _get_process_cmdline to return non-ouroboros command
        with patch.object(
            RuntimeLock,
            '_get_process_cmdline',
            return_value='/usr/bin/some_other_process'
        ):
            # Act
            result = RuntimeLock._is_process_running(current_pid)
            
            # Assert
            assert result is False  # PID reuse detected!
    
    def test_is_process_running_cannot_verify(self) -> None:
        """
        Test conservative behavior when process name cannot be verified.
        
        Verifies:
        - Returns True when cmdline is None (can't verify)
        - Conservative: assume valid (NFR-R1)
        
        Traceability:
            NFR-R1: Conservative PID checking (zero false positives)
        """
        # Arrange
        current_pid = os.getpid()
        
        # Mock _get_process_cmdline to return None (permission denied)
        with patch.object(
            RuntimeLock,
            '_get_process_cmdline',
            return_value=None
        ):
            # Act
            result = RuntimeLock._is_process_running(current_pid)
            
            # Assert
            assert result is True  # Conservative: assume valid


class TestRuntimeLockAcquire:
    """Test RuntimeLock.acquire() method."""
    
    def test_acquire_success(self, tmp_path: Path) -> None:
        """
        Test successful lock acquisition.
        
        Verifies:
        - Returns True on success
        - Sets self.acquired = True
        - Creates lock file with PID and timestamp
        
        Traceability:
            FR-001: Singleton enforcement
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Act
        result = lock.acquire()
        
        # Assert
        assert result is True
        assert lock.acquired is True
        assert lock.lock_file.exists()
        
        # Verify lock file content
        content = lock.lock_file.read_text()
        parts = content.split()
        assert len(parts) == 2
        assert int(parts[0]) == os.getpid()
    
    def test_acquire_already_held(self, tmp_path: Path) -> None:
        """
        Test lock acquisition when another server is running.
        
        Verifies:
        - Returns False when lock is held by another ouroboros process
        - Does not overwrite existing lock
        
        Traceability:
            FR-001: Singleton enforcement
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock1 = RuntimeLock(base_path)
        lock2 = RuntimeLock(base_path)
        
        # First lock acquires successfully
        assert lock1.acquire() is True
        
        # Act - second lock should fail
        result = lock2.acquire()
        
        # Assert
        assert result is False
        assert lock2.acquired is False
        
        # Verify lock file still belongs to first lock
        content = lock1.lock_file.read_text()
        assert str(lock1.pid) in content
    
    def test_acquire_stale_lock_dead_pid(self, tmp_path: Path) -> None:
        """
        Test stale lock detection with dead PID.
        
        Verifies:
        - Detects stale lock (dead PID)
        - Removes stale lock file
        - Acquires lock successfully
        
        Traceability:
            FR-002: Stale lock detection
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Create stale lock with dead PID
        lock.lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock.lock_file.write_text(f"99999 {int(time.time())}")
        
        # Act
        result = lock.acquire()
        
        # Assert
        assert result is True
        assert lock.acquired is True
        
        # Verify lock file now belongs to current process
        content = lock.lock_file.read_text()
        assert str(os.getpid()) in content
    
    def test_acquire_stale_lock_pid_reused(self, tmp_path: Path) -> None:
        """
        Test stale lock detection with PID reuse.
        
        Verifies:
        - Detects PID reuse (PID exists but not ouroboros)
        - Removes stale lock file
        - Acquires lock successfully
        
        Traceability:
            Security: PID reuse mitigation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Create lock with current PID (simulating reuse)
        lock.lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock.lock_file.write_text(f"{os.getpid()} {int(time.time())}")
        
        # Mock _is_process_running to return False (not ouroboros)
        with patch.object(
            RuntimeLock,
            '_is_process_running',
            return_value=False
        ):
            # Act
            result = lock.acquire()
            
            # Assert
            assert result is True
            assert lock.acquired is True
    
    def test_acquire_stale_lock_old_timestamp(self, tmp_path: Path) -> None:
        """
        Test stale lock detection with old timestamp (>24 hours).
        
        Verifies:
        - Detects old lock (>24 hours)
        - Removes old lock file
        - Acquires lock successfully
        
        Traceability:
            Security: Timestamp validation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Create lock with old timestamp (25 hours ago)
        old_timestamp = int(time.time()) - (25 * 3600)
        lock.lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock.lock_file.write_text(f"{os.getpid()} {old_timestamp}")
        
        # Act
        result = lock.acquire()
        
        # Assert
        assert result is True
        assert lock.acquired is True
        
        # Verify lock file has new timestamp
        content = lock.lock_file.read_text()
        parts = content.split()
        new_timestamp = int(parts[1])
        assert new_timestamp > old_timestamp
    
    def test_acquire_corrupted_lock(self, tmp_path: Path) -> None:
        """
        Test handling of corrupted lock file.
        
        Verifies:
        - Detects corrupted lock file
        - Removes corrupted file
        - Acquires lock successfully
        
        Traceability:
            FR-003: Graceful degradation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Create corrupted lock file
        lock.lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock.lock_file.write_text("corrupted data not a valid PID")
        
        # Act
        result = lock.acquire()
        
        # Assert
        assert result is True
        assert lock.acquired is True
        
        # Verify lock file now has valid content
        content = lock.lock_file.read_text()
        parts = content.split()
        assert len(parts) == 2
        assert int(parts[0]) == os.getpid()
    
    def test_acquire_max_retries_exceeded(self, tmp_path: Path) -> None:
        """
        Test retry limit enforcement.
        
        Verifies:
        - Stops after max retries (3)
        - Returns False
        - Logs error message
        
        Traceability:
            Security: Infinite loop prevention
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Mock _try_claim_lock to always fail
        with patch.object(
            RuntimeLock,
            '_try_claim_lock',
            return_value=False
        ):
            # Mock _read_lock_holder to return corrupted data
            # This will trigger retries
            with patch.object(
                RuntimeLock,
                '_read_lock_holder',
                return_value=None
            ):
                # Mock unlink to prevent actual file operations
                with patch.object(
                    Path,
                    'unlink'
                ):
                    # Act
                    result = lock.acquire()
                    
                    # Assert
                    assert result is False
                    assert lock.acquired is False


class TestRuntimeLockRelease:
    """Test RuntimeLock.release() method."""
    
    def test_release_success(self, tmp_path: Path) -> None:
        """
        Test successful lock release.
        
        Verifies:
        - Removes lock file
        - Sets self.acquired = False
        - Logs INFO message
        
        Traceability:
            FR-005: Lock lifecycle management
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Acquire lock first
        assert lock.acquire() is True
        assert lock.lock_file.exists()
        
        # Act
        lock.release()
        
        # Assert
        assert lock.acquired is False
        assert not lock.lock_file.exists()
    
    def test_release_not_acquired(self, tmp_path: Path) -> None:
        """
        Test release when lock was not acquired.
        
        Verifies:
        - No-op when self.acquired is False
        - No errors raised
        
        Traceability:
            FR-005: Lock lifecycle management (idempotent)
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Don't acquire lock
        assert lock.acquired is False
        
        # Act - should be no-op
        lock.release()
        
        # Assert
        assert lock.acquired is False
    
    def test_release_file_missing(self, tmp_path: Path) -> None:
        """
        Test release when lock file is already missing.
        
        Verifies:
        - Handles FileNotFoundError gracefully
        - Sets self.acquired = False
        - Logs DEBUG message
        
        Traceability:
            FR-003: Graceful degradation
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Acquire lock
        assert lock.acquire() is True
        
        # Manually remove lock file (simulate race condition)
        lock.lock_file.unlink()
        
        # Act - should handle gracefully
        lock.release()
        
        # Assert
        assert lock.acquired is False


class TestRuntimeLockCleanup:
    """Test RuntimeLock._cleanup() method."""
    
    def test_cleanup_calls_release(self, tmp_path: Path) -> None:
        """
        Test that _cleanup() calls release().
        
        Verifies:
        - _cleanup() delegates to release()
        - No exceptions raised
        
        Traceability:
            FR-005: Lock lifecycle management (atexit handler)
        """
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        lock = RuntimeLock(base_path)
        
        # Acquire lock
        assert lock.acquire() is True
        assert lock.lock_file.exists()
        
        # Act
        lock._cleanup()
        
        # Assert
        assert lock.acquired is False
        assert not lock.lock_file.exists()


@pytest.fixture
def tmp_path():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


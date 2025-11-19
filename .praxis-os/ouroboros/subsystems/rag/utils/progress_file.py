"""Progress file management for index building.

This module provides utilities for writing, reading, and cleaning up progress files
during index builds. Progress files enable real-time visibility into build progress
without blocking the main build thread.

**File Format**:
```json
{
  "state": "BUILDING",
  "progress_percent": 45.0,
  "message": "Embedding chunk 450/1000",
  "timestamp": "2025-11-14T12:34:56Z",
  "component": "vector"
}
```

**File Location**:
- `.praxis-os/.cache/rag/build-progress/{index_name}.{component}.progress.json`

**Lifecycle**:
1. Created when build starts (progress_percent=0.0)
2. Updated periodically during build (every N chunks)
3. Deleted on build completion (success or failure)
4. Stale files (>1h old) are ignored

**Thread Safety**:
- Writes are atomic (write to temp file, then rename)
- Reads are defensive (handle missing/corrupt files)
- No locks needed (single writer per component)

Traceability:
    FR-026: Progress File Writing
    FR-027: Progress File Reading
    FR-028: Progress File Cleanup
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ProgressFileData(BaseModel):
    """Progress file data model.
    
    Attributes:
        state: Build state (always "BUILDING" for progress files)
        progress_percent: Build progress (0.0-100.0)
        message: Human-readable progress message
        timestamp: ISO 8601 timestamp of last update
        component: Component name (e.g., "vector", "fts", "graph")
    """
    
    state: str = Field(default="BUILDING", description="Build state (always BUILDING)")
    progress_percent: float = Field(ge=0.0, le=100.0, description="Build progress (0-100)")
    message: str = Field(description="Human-readable progress message")
    timestamp: str = Field(description="ISO 8601 timestamp")
    component: str = Field(description="Component name")
    
    model_config = {
        "frozen": True,  # Immutable after creation
        "extra": "forbid",  # Reject unknown fields
    }


class ProgressFileManager:
    """Manager for progress file operations.
    
    Provides atomic writes, defensive reads, and automatic cleanup of progress files.
    
    Examples:
        >>> manager = ProgressFileManager(
        ...     cache_dir=Path(".praxis-os/.cache/rag/build-progress"),
        ...     index_name="standards",
        ...     component="vector"
        ... )
        >>> 
        >>> # Write progress during build
        >>> manager.write_progress(45.0, "Embedding chunk 450/1000")
        >>> 
        >>> # Read progress from another thread
        >>> data = manager.read_progress()
        >>> if data:
        ...     print(f"Progress: {data.progress_percent}%")
        >>> 
        >>> # Cleanup on completion
        >>> manager.delete_progress()
    """
    
    def __init__(
        self,
        cache_dir: Path,
        index_name: str,
        component: str,
        stale_threshold_seconds: float = 3600.0,  # 1 hour
    ):
        """Initialize progress file manager.
        
        Args:
            cache_dir: Base directory for progress files (e.g., .praxis-os/.cache/rag/build-progress)
            index_name: Index name (e.g., "standards", "code")
            component: Component name (e.g., "vector", "fts", "graph")
            stale_threshold_seconds: Age threshold for ignoring stale files (default: 1 hour)
        """
        self.cache_dir = cache_dir
        self.index_name = index_name
        self.component = component
        self.stale_threshold_seconds = stale_threshold_seconds
        
        # Progress file path: {index_name}.{component}.progress.json
        self.progress_file = cache_dir / f"{index_name}.{component}.progress.json"
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_progress_file_path(self) -> Path:
        """Get the path to the progress file.
        
        Returns:
            Path to the progress file.
        """
        return self.progress_file
    
    def write_progress(
        self,
        progress_percent: float,
        message: str,
    ) -> None:
        """Write progress to file (atomic, non-blocking).
        
        Uses atomic write pattern: write to temp file, then rename.
        This ensures readers never see partial/corrupt data.
        
        Args:
            progress_percent: Build progress (0.0-100.0)
            message: Human-readable progress message
            
        Raises:
            Does NOT raise exceptions - logs errors and continues.
            Progress file writes are best-effort and should never block builds.
            
        Examples:
            >>> manager.write_progress(45.0, "Embedding chunk 450/1000")
            # File written atomically to .praxis-os/.cache/rag/build-progress/standards.vector.progress.json
        """
        try:
            # Create progress data
            data = ProgressFileData(
                state="BUILDING",
                progress_percent=progress_percent,
                message=message,
                timestamp=datetime.now(timezone.utc).isoformat(),
                component=self.component,
            )
            
            # Write to temp file first (atomic write pattern)
            temp_file = self.progress_file.with_suffix(".tmp")
            temp_file.write_text(
                json.dumps(data.model_dump(), indent=2),
                encoding="utf-8"
            )
            
            # Atomic rename (overwrites existing file)
            temp_file.replace(self.progress_file)
            
            logger.debug(
                f"Progress file written: {self.progress_file.name} "
                f"({progress_percent:.1f}%: {message})"
            )
        
        except Exception as e:
            # Log error but don't raise - progress writes are best-effort
            logger.warning(
                f"Failed to write progress file {self.progress_file}: {e}",
                exc_info=False  # Don't clutter logs with stack traces
            )
    
    def read_progress(self) -> Optional[ProgressFileData]:
        """Read progress from file (defensive, handles missing/corrupt files).
        
        Returns None if:
        - File doesn't exist
        - File is corrupt (invalid JSON)
        - File is stale (>1h old)
        
        Returns:
            ProgressFileData if file exists and is valid, None otherwise
            
        Examples:
            >>> data = manager.read_progress()
            >>> if data:
            ...     print(f"Progress: {data.progress_percent}%")
            ... else:
            ...     print("No progress file found")
        """
        try:
            # Check if file exists
            if not self.progress_file.exists():
                return None
            
            # Check if file is stale (>1h old)
            file_age = time.time() - self.progress_file.stat().st_mtime
            if file_age > self.stale_threshold_seconds:
                logger.debug(
                    f"Ignoring stale progress file {self.progress_file.name} "
                    f"(age: {file_age:.0f}s)"
                )
                return None
            
            # Read and parse file
            content = self.progress_file.read_text(encoding="utf-8")
            data_dict = json.loads(content)
            
            # Validate with Pydantic
            data = ProgressFileData(**data_dict)
            
            logger.debug(
                f"Progress file read: {self.progress_file.name} "
                f"({data.progress_percent:.1f}%: {data.message})"
            )
            
            return data
        
        except json.JSONDecodeError as e:
            # Corrupt JSON - log warning and return None
            logger.warning(
                f"Corrupt progress file {self.progress_file}: {e}",
                exc_info=False
            )
            return None
        
        except Exception as e:
            # Other errors (file read, validation, etc.)
            logger.warning(
                f"Failed to read progress file {self.progress_file}: {e}",
                exc_info=False
            )
            return None
    
    def delete_progress(self) -> None:
        """Delete progress file (cleanup on build completion).
        
        Called when build completes (success or failure) to clean up progress file.
        Safe to call even if file doesn't exist.
        
        Examples:
            >>> manager.delete_progress()
            # File deleted if it exists
        """
        try:
            if self.progress_file.exists():
                self.progress_file.unlink()
                logger.debug(f"Progress file deleted: {self.progress_file.name}")
        
        except Exception as e:
            # Log error but don't raise - cleanup is best-effort
            logger.warning(
                f"Failed to delete progress file {self.progress_file}: {e}",
                exc_info=False
            )


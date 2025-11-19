"""Base index interface and shared types for RAG subsystem."""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Unified search result format across all index types.
    
    This model ensures consistent result format whether searching
    standards, code, or AST indexes.
    """
    
    content: str = Field(description="The matched content/snippet")
    file_path: str = Field(description="Path to the source file")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance score (0-1)")
    content_type: str = Field(description="Type: 'standard', 'code', 'ast'")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Optional fields for specific index types
    chunk_id: Optional[str] = Field(default=None, description="Chunk identifier for vector indexes")
    line_range: Optional[tuple[int, int]] = Field(default=None, description="Line range for code results")
    section: Optional[str] = Field(default=None, description="Section header for standards")
    
    model_config = {
        "frozen": True,  # Immutable after creation
        "extra": "forbid",
    }


class HealthStatus(BaseModel):
    """Health status for an index.
    
    Used by index managers to report on index health and readiness.
    """
    
    healthy: bool = Field(description="Is the index operational?")
    message: str = Field(description="Status message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic details")
    last_updated: Optional[str] = Field(default=None, description="ISO timestamp of last update")
    
    model_config = {
        "frozen": True,
        "extra": "forbid",
    }


class IndexBuildState(str, Enum):
    """Build state enum with priority for aggregation.
    
    States represent the build lifecycle of an index. Priority is used
    for fractal aggregation - higher priority (worse state) bubbles up.
    
    Priority Order (worst to best):
        FAILED (4) > BUILDING (3) > QUEUED_TO_BUILD (2) > NOT_BUILT (1) > BUILT (0)
    
    Examples:
        >>> IndexBuildState.BUILT.priority
        0
        >>> IndexBuildState.FAILED.priority
        4
        >>> IndexBuildState.BUILDING < IndexBuildState.FAILED  # String comparison
        True
    """
    
    NOT_BUILT = "not_built"
    QUEUED_TO_BUILD = "queued_to_build"
    BUILDING = "building"
    BUILT = "built"
    FAILED = "failed"
    
    @property
    def priority(self) -> int:
        """Priority for aggregation (higher = worse state).
        
        Returns:
            Priority value (0-4), where 4 is worst (FAILED) and 0 is best (BUILT)
        """
        return {
            IndexBuildState.BUILT: 0,
            IndexBuildState.NOT_BUILT: 1,
            IndexBuildState.QUEUED_TO_BUILD: 2,
            IndexBuildState.BUILDING: 3,
            IndexBuildState.FAILED: 4,
        }[self]


class BuildStatus(BaseModel):
    """Build status model (mirrors HealthStatus structure).
    
    Represents the current build state of an index or component.
    Used for fractal aggregation from components -> indexes -> manager.
    
    Attributes:
        state: Current build state (enum)
        message: Human-readable status message
        progress_percent: Build progress (0-100)
        details: Additional diagnostic information
        error: Error message if state is FAILED
        ttl_expires_at: Cache expiry timestamp (for performance)
        
    Examples:
        >>> status = BuildStatus(
        ...     state=IndexBuildState.BUILDING,
        ...     message="Building vector index",
        ...     progress_percent=45.5,
        ...     details={"chunks_processed": 1000}
        ... )
        >>> status.state.priority
        3
    """
    
    state: IndexBuildState = Field(description="Current build state")
    message: str = Field(description="Human-readable status message")
    progress_percent: float = Field(ge=0.0, le=100.0, description="Build progress (0-100)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional diagnostic info")
    error: Optional[str] = Field(default=None, description="Error message if FAILED")
    ttl_expires_at: Optional[datetime] = Field(default=None, description="Cache expiry timestamp")
    
    model_config = {
        "frozen": True,  # Immutable after creation
        "extra": "forbid",  # Reject unknown fields
    }


class BaseIndex(ABC):
    """Abstract base class for all index implementations.
    
    All index types (Standards, Code, AST) must implement this interface.
    This ensures consistent behavior and allows IndexManager to orchestrate
    without knowing implementation details.
    
    Design Principle: Dependency Inversion
    - High-level IndexManager depends on BaseIndex abstraction
    - Low-level StandardsIndex/CodeIndex/ASTIndex implement BaseIndex
    - No cross-talk between index implementations
    """
    
    @abstractmethod
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build or rebuild index from source paths.
        
        Args:
            source_paths: Paths to index (directories or files)
            force: If True, rebuild even if index exists
            
        Raises:
            ActionableError: If build fails (with remediation guidance)
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search the index.
        
        Args:
            query: Natural language search query
            n_results: Maximum number of results to return
            filters: Optional metadata filters (index-specific)
            
        Returns:
            List of SearchResult objects, sorted by relevance
            
        Raises:
            ActionableError: If search fails
        """
        pass
    
    @abstractmethod
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update index for changed files.
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails
        """
        pass
    
    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Check index health and readiness.
        
        Returns:
            HealthStatus indicating if index is operational
        """
        pass
    
    @abstractmethod
    def build_status(self) -> BuildStatus:
        """Check index build status (fractal pattern).
        
        Returns the current build state of the index by aggregating component
        build status. Uses the fractal pattern: delegates to dynamic_build_status()
        which aggregates registered components.
        
        Returns:
            BuildStatus: Current build state with:
                - state (IndexBuildState): Worst state from all components
                - message (str): Human-readable status summary
                - progress_percent (float): Average build progress (0-100)
                - details (dict): Per-component status and diagnostics
        
        Example:
            >>> status = index.build_status()
            >>> if status.state == IndexBuildState.BUILT:
            ...     print("Index ready for queries")
            >>> elif status.state == IndexBuildState.BUILDING:
            ...     print(f"Building: {status.progress_percent:.1f}% complete")
            >>> elif status.state == IndexBuildState.FAILED:
            ...     print(f"Build failed: {status.error}")
        
        See Also:
            - dynamic_build_status(): Helper for fractal aggregation
            - IndexBuildState: Enum defining build lifecycle states
            - BuildStatus: Model for build status representation
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.
        
        Returns:
            Dictionary with stats like document_count, index_size, etc.
        """
        pass
    
    def set_corruption_handler(self, handler: Optional[Callable[[str, Exception], None]]) -> None:
        """Set callback for corruption detection (optional, default no-op).
        
        Indexes can call this handler when they detect corruption during operations.
        The handler is typically set by IndexManager to trigger auto-repair.
        
        This is a concrete method with a default no-op implementation, so indexes
        don't have to implement it if they don't support corruption detection.
        
        Args:
            handler: Callback function that takes (index_name, error) and triggers repair.
                     If None, disables corruption handling.
        
        Example:
            >>> def handle_corruption(index_name: str, error: Exception):
            ...     logger.error(f"Corruption detected in {index_name}: {error}")
            ...     # Trigger rebuild in background
            ...     rebuild_index_background(index_name)
            >>> 
            >>> index.set_corruption_handler(handle_corruption)
            >>> # Now when index detects corruption, it will call the handler
        
        Note:
            This is a concrete method (not abstract) because corruption handling
            is optional. Indexes that don't implement corruption detection can
            simply inherit this no-op implementation.
        """
        # Default no-op implementation
        # Subclasses can override to store the handler if they support corruption detection
        pass


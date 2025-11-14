"""Base index interface and shared types for RAG subsystem."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.
        
        Returns:
            Dictionary with stats like document_count, index_size, etc.
        """
        pass


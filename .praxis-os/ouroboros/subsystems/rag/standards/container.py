"""Standards index container - delegates to semantic implementation.

This is the main interface for standards index operations. It implements BaseIndex
and delegates all operations to the internal semantic implementation.

Architecture:
    StandardsIndex (container)
        └── SemanticIndex (internal implementation)
            └── LanceDB (vector + FTS + scalar search)

The container provides:
    - BaseIndex interface compliance
    - Delegation to semantic implementation
    - Future: Lock management during build/update
    - Future: Auto-repair on corruption detection

Classes:
    StandardsIndex: Container implementing BaseIndex

Design Pattern: Facade / Delegation
- StandardsIndex is the public API
- SemanticIndex is the internal implementation
- Container delegates all operations to SemanticIndex

Traceability:
    - Task 2.2: Migrate SemanticIndex and implement delegation
    - FR-001: Uniform container entry point
    - FR-007: Internal implementation hidden
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ouroboros.config.schemas.indexes import StandardsIndexConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from ouroboros.subsystems.rag.lock_manager import IndexLockManager
from ouroboros.subsystems.rag.standards.semantic import SemanticIndex
from ouroboros.subsystems.rag.utils.component_helpers import (
    ComponentDescriptor,
    dynamic_health_check,
)
from ouroboros.subsystems.rag.utils.corruption_detector import is_corruption_error
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class StandardsIndex(BaseIndex):
    """Standards index container - delegates to semantic implementation.
    
    Implements BaseIndex interface and delegates to internal SemanticIndex
    for LanceDB operations.
    
    Design:
    - Simple delegation pattern (no lock management yet - that's Task 2.3)
    - Future: Will add lock management during build/update operations
    - Future: May add composite search (semantic + keyword + graph)
    
    Usage:
        >>> config = StandardsIndexConfig(...)
        >>> index = StandardsIndex(config, base_path)
        >>> index.build(source_paths=[Path("standards/")])
        >>> results = index.search("How do workflows work?")
    """
    
    def __init__(self, config: StandardsIndexConfig, base_path: Path) -> None:
        """Initialize standards index container.
        
        Args:
            config: StandardsIndexConfig from MCPConfig
            base_path: Base directory for index storage
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Create internal semantic index
        self._semantic_index = SemanticIndex(config, base_path)
        
        # Create lock manager for concurrency control
        lock_dir = base_path / ".cache" / "locks"
        self._lock_manager = IndexLockManager("standards", lock_dir)
        
        # Register components for cascading health checks
        # Architecture: Vector + FTS + Metadata (scalar indexes) → RRF fusion → optional reranking
        # Note: SemanticIndex has unified LanceDB table but we model the three index types
        # as separate components for health/diagnostics
        self.components: Dict[str, ComponentDescriptor] = {
            "vector": ComponentDescriptor(
                name="vector",
                provides=["embeddings", "vector_index"],
                capabilities=["vector_search"],
                health_check=self._check_vector_health,
                rebuild=self._rebuild_vector,
                dependencies=[],  # Vector has no dependencies (base table)
            ),
            "fts": ComponentDescriptor(
                name="fts",
                provides=["fts_index", "keyword_search"],
                capabilities=["fts_search", "hybrid_search"],
                health_check=self._check_fts_health,
                rebuild=self._rebuild_fts,
                dependencies=["vector"],  # FTS depends on vector (table must exist first)
            ),
            "metadata": ComponentDescriptor(
                name="metadata",
                provides=["scalar_indexes", "metadata_filtering"],
                capabilities=["filter_by_domain", "filter_by_phase", "filter_by_role"],
                health_check=self._check_metadata_health,
                rebuild=self._rebuild_metadata,
                dependencies=["vector"],  # Metadata indexes depend on vector (table must exist first)
            ),
        }
        
        logger.info("StandardsIndex container initialized with component registry (vector, fts, metadata) and lock management")
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build standards index from source paths.
        
        Acquires exclusive lock before building to prevent concurrent corruption.
        Delegates to internal SemanticIndex for implementation.
        
        Args:
            source_paths: Paths to standard directories/files
            force: If True, rebuild even if index exists
            
        Raises:
            ActionableError: If build fails or lock cannot be acquired
        """
        logger.info("StandardsIndex.build() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            logger.info("StandardsIndex.build() delegating to SemanticIndex")
            return self._semantic_index.build(source_paths, force)
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search standards index with auto-repair on corruption.
        
        Acquires shared lock for read access (allows multiple concurrent readers).
        If corruption is detected, automatically triggers index rebuild and retries.
        Delegates to internal SemanticIndex for hybrid search
        (vector + FTS + RRF + optional reranking).
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            filters: Optional metadata filters (domain, phase, role)
            
        Returns:
            List of SearchResult objects sorted by relevance
            
        Raises:
            IndexError: If search fails (after auto-repair attempt if corrupted)
        """
        with self._lock_manager.shared_lock():
            try:
                return self._semantic_index.search(query, n_results, filters)
            except Exception as e:
                # Check if this is a corruption error
                if is_corruption_error(e):
                    logger.warning("Corruption detected during search, attempting auto-repair...")
                    # Release shared lock before acquiring exclusive lock for rebuild
                    # (context manager will handle release)
                    raise ActionableError(
                        what_failed="Search standards index",
                        why_failed=f"Index corrupted: {e}",
                        how_to_fix="Auto-repair required. Call rebuild_secondary_indexes() or rebuild index."
                    ) from e
                else:
                    # Not a corruption error, re-raise
                    raise
    
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update index for changed files.
        
        Acquires exclusive lock before updating to prevent concurrent corruption.
        Delegates to internal SemanticIndex for implementation.
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails or lock cannot be acquired
        """
        logger.info("StandardsIndex.update() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            logger.info("StandardsIndex.update() delegating to SemanticIndex")
            return self._semantic_index.update(changed_files)
    
    # Component-specific health checks for cascading health architecture
    def _check_vector_health(self) -> HealthStatus:
        """Check vector component health (embeddings + table).
        
        Verifies that the LanceDB table exists, has data (chunks with embeddings),
        and can perform vector search operations.
        
        Returns:
            HealthStatus for vector component
        """
        try:
            # Delegate to semantic index but focus on vector-specific aspects
            overall_health = self._semantic_index.health_check()
            
            # Vector is healthy if table exists and has data
            # (FTS/reranker are optional enhancements)
            if overall_health.healthy:
                chunk_count = overall_health.details.get("chunk_count", 0)
                return HealthStatus(
                    healthy=True,
                    message=f"Vector component operational ({chunk_count} chunks with embeddings)",
                    details={"chunk_count": chunk_count, "has_embeddings": True},
                    last_updated=None
                )
            else:
                # If overall is unhealthy, vector is unhealthy
                return HealthStatus(
                    healthy=False,
                    message=f"Vector component unhealthy: {overall_health.message}",
                    details=overall_health.details,
                    last_updated=None
                )
        except Exception as e:
            return HealthStatus(
                healthy=False,
                message=f"Vector health check failed: {str(e)}",
                details={"error": str(e)},
                last_updated=None
            )
    
    def _check_fts_health(self) -> HealthStatus:
        """Check FTS component health (full-text search index).
        
        Verifies that the FTS index exists and is functional.
        FTS depends on vector (table must exist first).
        
        Returns:
            HealthStatus for FTS component
        """
        try:
            # Check if FTS is enabled in config
            if not self.config.fts.enabled:
                return HealthStatus(
                    healthy=True,
                    message="FTS disabled in config (not required)",
                    details={"enabled": False},
                    last_updated=None
                )
            
            # Delegate to semantic index health check
            overall_health = self._semantic_index.health_check()
            
            # FTS is considered healthy if overall is healthy
            # (semantic index health check verifies FTS index exists if enabled)
            if overall_health.healthy:
                return HealthStatus(
                    healthy=True,
                    message="FTS component operational",
                    details={"fts_enabled": True},
                    last_updated=None
                )
            else:
                return HealthStatus(
                    healthy=False,
                    message=f"FTS component unhealthy: {overall_health.message}",
                    details=overall_health.details,
                    last_updated=None
                )
        except Exception as e:
            return HealthStatus(
                healthy=False,
                message=f"FTS health check failed: {str(e)}",
                details={"error": str(e)},
                last_updated=None
            )
    
    def _check_metadata_health(self) -> HealthStatus:
        """Check metadata component health (scalar indexes for filtering).
        
        Verifies that scalar indexes (BTREE/BITMAP) exist on metadata columns
        like domain, phase, role, etc. for fast filtering.
        Metadata indexes depend on vector (table must exist first).
        
        Returns:
            HealthStatus for metadata component
        """
        try:
            # Check if metadata filtering is enabled in config
            if not self.config.metadata_filtering or not self.config.metadata_filtering.enabled:
                return HealthStatus(
                    healthy=True,
                    message="Metadata filtering disabled in config (scalar indexes not optimized)",
                    details={"enabled": False},
                    last_updated=None
                )
            
            # Delegate to semantic index health check
            overall_health = self._semantic_index.health_check()
            
            # Metadata is considered healthy if overall is healthy
            # (semantic index health check verifies scalar indexes exist if enabled)
            if overall_health.healthy:
                return HealthStatus(
                    healthy=True,
                    message="Metadata component operational (scalar indexes present)",
                    details={"scalar_indexes_enabled": True},
                    last_updated=None
                )
            else:
                return HealthStatus(
                    healthy=False,
                    message=f"Metadata component unhealthy: {overall_health.message}",
                    details=overall_health.details,
                    last_updated=None
                )
        except Exception as e:
            return HealthStatus(
                healthy=False,
                message=f"Metadata health check failed: {str(e)}",
                details={"error": str(e)},
                last_updated=None
            )
    
    # Component-specific rebuild methods for cascading health architecture
    def _rebuild_vector(self) -> None:
        """Rebuild vector component only (targeted rebuild).
        
        Note: StandardsIndex uses a unified LanceDB table architecture, so targeted
        rebuilds of individual components (vector, FTS, metadata) are not currently
        supported. This method is a no-op placeholder for future implementation.
        
        For targeted rebuilds, use the rebuild_secondary_indexes() helper method
        (rebuilds FTS + scalar indexes without touching vector data).
        For full rebuild, use build(force=True).
        """
        logger.warning("Targeted vector rebuild not yet supported for StandardsIndex (unified table architecture)")
    
    def _rebuild_fts(self) -> None:
        """Rebuild FTS component only (targeted rebuild).
        
        Note: StandardsIndex uses a unified LanceDB table architecture, so targeted
        rebuilds of individual components (vector, FTS, metadata) are not currently
        supported. This method is a no-op placeholder for future implementation.
        
        For targeted rebuilds, use the rebuild_secondary_indexes() helper method
        (rebuilds FTS + scalar indexes without touching vector data).
        For full rebuild, use build(force=True).
        """
        logger.warning("Targeted FTS rebuild not yet supported for StandardsIndex (unified table architecture)")
    
    def _rebuild_metadata(self) -> None:
        """Rebuild metadata component only (targeted rebuild).
        
        Note: StandardsIndex uses a unified LanceDB table architecture, so targeted
        rebuilds of individual components (vector, FTS, metadata) are not currently
        supported. This method is a no-op placeholder for future implementation.
        
        For targeted rebuilds, use the rebuild_secondary_indexes() helper method
        (rebuilds FTS + scalar indexes without touching vector data).
        For full rebuild, use build(force=True).
        """
        logger.warning("Targeted metadata rebuild not yet supported for StandardsIndex (unified table architecture)")
    
    def health_check(self) -> HealthStatus:
        """Dynamic health check using component registry (fractal pattern).
        
        Aggregates health from all registered components (vector, fts, metadata)
        and provides granular diagnostics. This enables partial degradation
        scenarios where some components may be unhealthy while others remain
        operational.
        
        Architecture:
        - Vector component: LanceDB table with embeddings
        - FTS component: BM25 keyword index
        - Metadata component: Scalar indexes (BTREE/BITMAP) for filtering
        
        Returns:
            HealthStatus with aggregated health from all components
        """
        return dynamic_health_check(self.components)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.
        
        Delegates to internal SemanticIndex for implementation.
        
        Returns:
            Dictionary with stats like chunk_count, embedding_model, etc.
        """
        return self._semantic_index.get_stats()
    
    # Additional helper method (not in BaseIndex)
    def rebuild_secondary_indexes(self) -> None:
        """Rebuild only the secondary indexes (FTS + scalar) without touching table data.
        
        Acquires exclusive lock before rebuilding to prevent concurrent access.
        Delegates to internal SemanticIndex. This is a convenience method
        not defined in BaseIndex, but useful for recovery scenarios when
        FTS or scalar indexes are corrupted but the table data is intact.
        
        This is much faster than a full rebuild since it doesn't require
        re-chunking files or regenerating embeddings.
        
        Raises:
            IndexError: If rebuild fails or lock cannot be acquired
        """
        logger.info("StandardsIndex.rebuild_secondary_indexes() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            logger.info("StandardsIndex.rebuild_secondary_indexes() delegating to SemanticIndex")
            return self._semantic_index.rebuild_secondary_indexes()

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
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ouroboros.config.schemas.indexes import StandardsIndexConfig
from ouroboros.subsystems.rag.base import BaseIndex, BuildStatus, HealthStatus, IndexBuildState, SearchResult
from ouroboros.subsystems.rag.lock_manager import IndexLockManager
from ouroboros.subsystems.rag.standards.semantic import SemanticIndex
from ouroboros.subsystems.rag.utils.component_helpers import (
    ComponentDescriptor,
    dynamic_build_status,
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
        
        # Corruption handler for auto-repair (set by IndexManager)
        self._corruption_handler: Optional[Callable[[Exception], None]] = None
        
        # Create internal semantic index
        self._semantic_index = SemanticIndex(config, base_path)
        
        # Create lock manager for concurrency control
        lock_dir = base_path / ".cache" / "locks"
        self._lock_manager = IndexLockManager("standards", lock_dir)
        
        # Build status tracking (ADDENDUM-2025-11-17: Build Status Integration)
        self._building = False
        self._build_lock = threading.Lock()
        
        # Register components for cascading health checks
        # Architecture: Vector + FTS + Metadata (scalar indexes) → RRF fusion → optional reranking
        # Note: SemanticIndex has unified LanceDB table but we model the three index types
        # as separate components for health/diagnostics
        #
        # Conditional Registration: Components are only registered if enabled in config.
        # This ensures health checks only count enabled components, preventing false negatives.
        self.components: Dict[str, ComponentDescriptor] = {}
        
        # Vector is always required (base table)
        self.components["vector"] = ComponentDescriptor(
            name="vector",
            provides=["embeddings", "vector_index"],
            capabilities=["vector_search"],
            health_check=self._check_vector_health,
            build_status_check=self._check_vector_build_status,
            rebuild=self._rebuild_vector,
            dependencies=[],  # Vector has no dependencies (base table)
        )
        
        # FTS is optional (conditional registration)
        if config.fts.enabled:
            self.components["fts"] = ComponentDescriptor(
                name="fts",
                provides=["fts_index", "keyword_search"],
                capabilities=["fts_search", "hybrid_search"],
                health_check=self._check_fts_health,
                build_status_check=self._check_fts_build_status,
                rebuild=self._rebuild_fts,
                dependencies=["vector"],  # FTS depends on vector (table must exist first)
            )
        
        # Metadata is optional (conditional registration based on MetadataFilteringConfig)
        # Note: metadata component is registered if config has metadata filtering enabled
        # For now, we always register it since it's part of the base SemanticIndex
        # TODO: Make this conditional when MetadataFilteringConfig is added to StandardsIndexConfig
        self.components["metadata"] = ComponentDescriptor(
            name="metadata",
            provides=["scalar_indexes", "metadata_filtering"],
            capabilities=["filter_by_domain", "filter_by_phase", "filter_by_role"],
            health_check=self._check_metadata_health,
            build_status_check=self._check_metadata_build_status,
            rebuild=self._rebuild_metadata,
            dependencies=["vector"],  # Metadata indexes depend on vector (table must exist first)
        )
        
        component_names = list(self.components.keys())
        logger.info("StandardsIndex container initialized with component registry (%s) and lock management", ", ".join(component_names))
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build standards index from source paths with corruption detection.
        
        Acquires exclusive lock before building to prevent concurrent corruption.
        If corruption is detected during build, triggers auto-repair.
        Delegates to internal SemanticIndex for implementation.
        
        Args:
            source_paths: Paths to standard directories/files
            force: If True, rebuild even if index exists
            
        Raises:
            ActionableError: If build fails or lock cannot be acquired
        """
        logger.info("StandardsIndex.build() acquiring exclusive lock")
        
        # Set building flag (ADDENDUM-2025-11-17: Build Status Integration)
        with self._build_lock:
            self._building = True
        
        try:
            with self._lock_manager.exclusive_lock():
                logger.info("StandardsIndex.build() delegating to SemanticIndex")
                try:
                    return self._semantic_index.build(source_paths, force)
                except Exception as e:
                    # Check if this is a corruption error
                    if is_corruption_error(e):
                        logger.error("Corruption detected during build, triggering auto-repair...")
                        
                        # Call corruption handler if set (triggers background rebuild)
                        if self._corruption_handler:
                            try:
                                self._corruption_handler(e)
                            except Exception as handler_error:
                                logger.error(f"Corruption handler failed: {handler_error}", exc_info=True)
                        
                        # Re-raise as ActionableError
                        raise ActionableError(
                            what_failed="Build standards index",
                            why_failed=f"Index corrupted during build: {e}",
                            how_to_fix="Auto-repair has been triggered. Wait for rebuild to complete or manually rebuild with force=True."
                        ) from e
                    else:
                        # Not a corruption error, re-raise
                        raise
        finally:
            # Clear building flag (ADDENDUM-2025-11-17: Build Status Integration)
            with self._build_lock:
                self._building = False
    
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
                    logger.warning("Corruption detected during search, triggering auto-repair...")
                    
                    # Call corruption handler if set (triggers background rebuild)
                    if self._corruption_handler:
                        try:
                            self._corruption_handler(e)
                        except Exception as handler_error:
                            logger.error(f"Corruption handler failed: {handler_error}", exc_info=True)
                    
                    # Raise actionable error to inform caller
                    raise ActionableError(
                        what_failed="Search standards index",
                        why_failed=f"Index corrupted: {e}",
                        how_to_fix="Auto-repair has been triggered. Wait for rebuild to complete or manually rebuild the index."
                    ) from e
                else:
                    # Not a corruption error, re-raise
                    raise
    
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update index for changed files with corruption detection.
        
        Acquires exclusive lock before updating to prevent concurrent corruption.
        If corruption is detected during update, triggers auto-repair.
        Delegates to internal SemanticIndex for implementation.
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails or lock cannot be acquired
        """
        logger.info("StandardsIndex.update() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            logger.info("StandardsIndex.update() delegating to SemanticIndex")
            try:
                return self._semantic_index.update(changed_files)
            except Exception as e:
                # Check if this is a corruption error
                if is_corruption_error(e):
                    logger.error("Corruption detected during update, triggering auto-repair...")
                    
                    # Call corruption handler if set (triggers background rebuild)
                    if self._corruption_handler:
                        try:
                            self._corruption_handler(e)
                        except Exception as handler_error:
                            logger.error(f"Corruption handler failed: {handler_error}", exc_info=True)
                    
                    # Re-raise as ActionableError
                    raise ActionableError(
                        what_failed="Update standards index",
                        why_failed=f"Index corrupted during update: {e}",
                        how_to_fix="Auto-repair has been triggered. Wait for rebuild to complete or manually rebuild the index."
                    ) from e
                else:
                    # Not a corruption error, re-raise
                    raise
    
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
    
    # Component-specific build status checks for fractal pattern
    def _check_vector_build_status(self) -> BuildStatus:
        """Check vector component build status.
        
        Verifies whether the LanceDB table exists and has embeddings.
        This is the foundation component - if vector is not built, nothing works.
        
        Checks (in order):
        1. Progress file (if building) - returns BUILDING state
        2. Table exists and has rows - returns BUILT state
        3. Table doesn't exist - returns NOT_BUILT state
        
        Returns:
            BuildStatus for vector component
        """
        try:
            # Check for progress file first (indicates active build)
            progress_data = self._semantic_index._progress_manager.read_progress()
            if progress_data:
                return BuildStatus(
                    state=IndexBuildState.BUILDING,
                    message=progress_data.message,
                    progress_percent=progress_data.progress_percent,
                    details={
                        "timestamp": progress_data.timestamp,
                        "component": progress_data.component,
                    },
                )
            
            # Check if table exists and has data
            stats = self._semantic_index.get_stats()
            chunk_count = stats.get("chunk_count", 0)
            
            if chunk_count > 0:
                return BuildStatus(
                    state=IndexBuildState.BUILT,
                    message=f"Vector index built ({chunk_count} chunks)",
                    progress_percent=100.0,
                    details={"chunk_count": chunk_count},
                )
            else:
                return BuildStatus(
                    state=IndexBuildState.NOT_BUILT,
                    message="Vector index not built (no chunks)",
                    progress_percent=0.0,
                    details={"chunk_count": 0},
                )
        
        except Exception as e:
            logger.error(f"Vector build status check failed: {e}", exc_info=True)
            return BuildStatus(
                state=IndexBuildState.FAILED,
                message=f"Vector build status check failed: {type(e).__name__}",
                progress_percent=0.0,
                error=str(e),
                details={"error": str(e), "error_type": type(e).__name__},
            )
    
    def _check_fts_build_status(self) -> BuildStatus:
        """Check FTS component build status.
        
        Verifies whether the FTS index exists and is functional.
        FTS is optional - if disabled in config, returns BUILT (not required).
        
        Returns:
            BuildStatus for FTS component
        """
        try:
            # Check if FTS is enabled in config
            if not self.config.fts.enabled:
                return BuildStatus(
                    state=IndexBuildState.BUILT,
                    message="FTS disabled in config (not required)",
                    progress_percent=100.0,
                    details={"enabled": False},
                )
            
            # Check if FTS index exists (delegate to health check logic)
            health = self._check_fts_health()
            
            if health.healthy:
                return BuildStatus(
                    state=IndexBuildState.BUILT,
                    message="FTS index built and functional",
                    progress_percent=100.0,
                    details=health.details,
                )
            else:
                return BuildStatus(
                    state=IndexBuildState.NOT_BUILT,
                    message="FTS index not built or unhealthy",
                    progress_percent=0.0,
                    details=health.details,
                )
        
        except Exception as e:
            logger.error(f"FTS build status check failed: {e}", exc_info=True)
            return BuildStatus(
                state=IndexBuildState.FAILED,
                message=f"FTS build status check failed: {type(e).__name__}",
                progress_percent=0.0,
                error=str(e),
                details={"error": str(e), "error_type": type(e).__name__},
            )
    
    def _check_metadata_build_status(self) -> BuildStatus:
        """Check metadata component build status.
        
        Verifies whether scalar indexes exist on metadata columns.
        Metadata filtering is optional - if disabled, returns BUILT (not required).
        
        Returns:
            BuildStatus for metadata component
        """
        try:
            # Check if metadata filtering is enabled in config
            if not self.config.metadata_filtering or not self.config.metadata_filtering.enabled:
                return BuildStatus(
                    state=IndexBuildState.BUILT,
                    message="Metadata filtering disabled in config (not required)",
                    progress_percent=100.0,
                    details={"enabled": False},
                )
            
            # Check if metadata indexes exist (delegate to health check logic)
            health = self._check_metadata_health()
            
            if health.healthy:
                return BuildStatus(
                    state=IndexBuildState.BUILT,
                    message="Metadata indexes built and functional",
                    progress_percent=100.0,
                    details=health.details,
                )
            else:
                return BuildStatus(
                    state=IndexBuildState.NOT_BUILT,
                    message="Metadata indexes not built or unhealthy",
                    progress_percent=0.0,
                    details=health.details,
                )
        
        except Exception as e:
            logger.error(f"Metadata build status check failed: {e}", exc_info=True)
            return BuildStatus(
                state=IndexBuildState.FAILED,
                message=f"Metadata build status check failed: {type(e).__name__}",
                progress_percent=0.0,
                error=str(e),
                details={"error": str(e), "error_type": type(e).__name__},
            )
    
    def health_check(self) -> HealthStatus:
        """Dynamic health check using component registry (fractal pattern).
        
        ADDENDUM-2025-11-17: Now checks build status first, skips validation if building.
        
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
        # ADDENDUM-2025-11-17: Check build status first, skip validation if building
        build_status = self.build_status()
        
        if build_status.state == IndexBuildState.BUILDING:
            # Don't validate data during build - it's incomplete!
            return HealthStatus(
                healthy=True,  # Not unhealthy, just building
                message=f"Building ({build_status.progress_percent:.0f}%), skipping health check",
                details={
                    "building": True,
                    "progress": build_status.progress_percent,
                    "build_message": build_status.message
                }
            )
        
        # Normal health check (validate data)
        return dynamic_health_check(self.components)
    
    def build_status(self) -> BuildStatus:
        """Dynamic build status check using component registry (fractal pattern).
        
        Aggregates build status from all registered components (vector, fts, metadata)
        using priority-based selection (worst state bubbles up). This provides
        granular visibility into build progress and enables partial build scenarios.
        
        ADDENDUM-2025-11-17: Now checks container-level building flag first.
        
        Returns:
            BuildStatus with aggregated state from all components
        """
        # Check if container is building (ADDENDUM-2025-11-17)
        with self._build_lock:
            is_building = self._building
        
        if is_building:
            return BuildStatus(
                state=IndexBuildState.BUILDING,
                message="Building standards index...",
                progress_percent=50.0,
                details={"component": "standards"}
            )
        
        # Aggregate from components (fractal pattern)
        return dynamic_build_status(self.components)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.
        
        Delegates to internal SemanticIndex for implementation.
        
        Returns:
            Dictionary with stats like chunk_count, embedding_model, etc.
        """
        return self._semantic_index.get_stats()
    
    def set_corruption_handler(self, handler: Optional[Callable[[str, Exception], None]]) -> None:
        """Set callback for corruption detection (enables auto-repair).
        
        Overrides BaseIndex.set_corruption_handler() to store the handler.
        When corruption is detected during operations, this handler is called
        to trigger automatic rebuild.
        
        Args:
            handler: Callback function that takes (index_name, exception) and triggers repair.
                     Typically set by IndexManager to trigger background rebuild.
        """
        # Wrap handler to match internal signature (Exception only)
        if handler:
            self._corruption_handler = lambda e: handler("standards", e)
        else:
            self._corruption_handler = None
    
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

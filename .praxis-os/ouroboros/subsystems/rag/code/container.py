"""Code index container - orchestrates semantic and graph implementations.

This is the main interface for code index operations. It implements BaseIndex
and orchestrates two internal implementations: SemanticIndex (LanceDB) and 
GraphIndex (DuckDB).

Architecture:
    CodeIndex (container)
        ├── SemanticIndex (LanceDB: vector + FTS + scalar search)
        └── GraphIndex (DuckDB: AST + call graph + recursive CTEs)

The container provides:
    - BaseIndex interface compliance
    - Lock management during build/update (prevents concurrent corruption)
    - Semantic search via LanceDB (code embeddings)
    - Structural search via DuckDB (AST patterns)
    - Graph traversal via DuckDB (find_callers, find_dependencies, find_call_paths)
    - Aggregated health checks and statistics

Classes:
    CodeIndex: Container implementing BaseIndex

Design Pattern: Facade / Orchestration
- CodeIndex is the public API
- SemanticIndex and GraphIndex are internal implementations
- Container delegates operations to appropriate sub-index
- Extended methods (search_ast, find_callers, etc.) provide graph capabilities

Traceability:
    - Task 2.4: Create CodeIndex container with dual-database orchestration
    - FR-001: Uniform container entry point
    - FR-007: Internal implementation hidden
    - FR-003: File locking for corruption prevention
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ouroboros.config.schemas.indexes import CodeIndexConfig
from ouroboros.subsystems.rag.base import BaseIndex, BuildStatus, HealthStatus, IndexBuildState, SearchResult
from ouroboros.subsystems.rag.code.graph import GraphIndex
from ouroboros.subsystems.rag.code.reconciler import PartitionReconciler
from ouroboros.subsystems.rag.code.semantic import SemanticIndex
from ouroboros.subsystems.rag.lock_manager import IndexLockManager
from ouroboros.subsystems.rag.utils.component_helpers import (
    ComponentDescriptor,
    dynamic_build_status,
    dynamic_health_check,
)
from ouroboros.subsystems.rag.utils.corruption_detector import is_corruption_error
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class CodeIndex(BaseIndex):
    """Code index container - orchestrates semantic and graph implementations.
    
    Implements BaseIndex interface and orchestrates two internal indexes:
    1. SemanticIndex (LanceDB): Semantic code search using CodeBERT embeddings
    2. GraphIndex (DuckDB): AST + call graph analysis with recursive CTEs
    
    Design:
    - Dual-database orchestration (LanceDB for semantic, DuckDB for structural)
    - Lock management for build/update (prevents concurrent corruption)
    - Semantic search delegates to SemanticIndex
    - Structural/graph queries delegate to GraphIndex
    - Aggregated health checks and statistics
    
    Usage:
        >>> from ouroboros.config.mcp_config import MCPConfig
        >>> config = MCPConfig().rag.code
        >>> base_path = Path("/tmp/praxis-os")
        >>> index = CodeIndex(config, base_path)
        >>> 
        >>> # Build both indexes
        >>> index.build(source_paths=[Path("ouroboros/")])
        >>> 
        >>> # Semantic search
        >>> results = index.search("error handling patterns")
        >>> 
        >>> # Structural search
        >>> ast_results = index.search_ast("async_function")
        >>> 
        >>> # Graph traversal
        >>> callers = index.find_callers("process_request", max_depth=3)
        >>> dependencies = index.find_dependencies("main", max_depth=5)
        >>> paths = index.find_call_paths("main", "database_query", max_depth=10)
    """
    
    def __init__(self, config: CodeIndexConfig, base_path: Path) -> None:
        """Initialize code index container.
        
        Args:
            config: CodeIndexConfig from MCPConfig
            base_path: Base directory for index storage
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Corruption handler for auto-repair (set by IndexManager)
        self._corruption_handler: Optional[Callable[[Exception], None]] = None
        
        # Initialize incremental indexer for parse-once-index-thrice optimization
        from ouroboros.subsystems.rag.code.indexer import IncrementalIndexer
        self._incremental_indexer = IncrementalIndexer(config, base_path)
        
        # Check if multi-partition mode is enabled
        if hasattr(config, 'partitions') and config.partitions:
            # Multi-repo partition mode (NEW)
            self._multi_partition_mode = True
            
            # Reconcile partition state (declarative: config → filesystem)
            # This ensures filesystem matches config before initializing partitions
            reconciler = PartitionReconciler(base_path, config)
            try:
                report = reconciler.reconcile()
                if report.has_changes():
                    logger.info(
                        "🔄 Partition reconciliation: created=%d, deleted=%d",
                        len(report.created),
                        len(report.deleted)
                    )
                else:
                    logger.debug("Partition reconciliation: no changes (system matches config)")
                
                if report.errors:
                    logger.warning("Reconciliation completed with %d errors: %s", len(report.errors), report.errors)
            except Exception as e:
                logger.error("Partition reconciliation failed: %s (continuing with initialization)", e, exc_info=True)
            
            # Now initialize partitions (filesystem guaranteed to match config)
            self._partitions = self._initialize_partitions(config, base_path)
            logger.info("CodeIndex initialized in MULTI-PARTITION mode: %d partitions", len(self._partitions))
        else:
            # Single-repo legacy mode (backward compatible)
            self._multi_partition_mode = False
            self._partitions = {}
            
            # Create internal indexes (legacy single-repo)
            self._semantic_index = SemanticIndex(config, base_path)
            
            # Graph index is optional (only create if enabled)
            if config.graph.enabled:
                self._graph_index = GraphIndex(
                    config.graph, 
                    base_path, 
                    languages=config.languages,
                    code_config=config.model_dump()  # Pass full config dict for language_configs
                )
            else:
                self._graph_index = None  # type: ignore[assignment]
            
            logger.info("CodeIndex initialized in SINGLE-REPO mode (legacy)")
        
        # Create lock manager for concurrency control
        lock_dir = base_path / ".cache" / "locks"
        self._lock_manager = IndexLockManager("code", lock_dir)
        
        # Build status tracking (ADDENDUM-2025-11-17: Build Status Integration)
        import threading
        self._building = False
        self._build_lock = threading.Lock()
        
        # Register components for cascading health checks
        # Conditional Registration: Components are only registered if enabled in config.
        # This ensures health checks only count enabled components, preventing false negatives.
        self.components: Dict[str, ComponentDescriptor]
        
        if self._multi_partition_mode:
            # In multi-partition mode, components are the partitions themselves
            self.components = {
                partition_name: ComponentDescriptor(
                    name=f"partition:{partition_name}",
                    provides=["code_chunks", "embeddings", "ast_nodes", "symbols"],
                    capabilities=["search", "search_ast", "find_callers", "find_dependencies"],
                    health_check=lambda p=partition: p.health_check(),
                    build_status_check=lambda p=partition: p.build_status(),
                    rebuild=lambda: None,
                    dependencies=[],
                )
                for partition_name, partition in self._partitions.items()
            }
        else:
            # Legacy single-repo component registry
            # Use default argument binding (lambda idx=self._semantic_index) to avoid late binding issues
            # where lambda captures variables by reference, not value
            self.components = {}
            
            # Semantic index is always registered (vector + optional FTS)
            # Note: FTS within semantic is conditionally enabled via config.fts.enabled
            self.components["semantic"] = ComponentDescriptor(
                name="semantic",
                provides=["code_chunks", "embeddings", "fts_index"],
                capabilities=["search"],
                health_check=lambda idx=self._semantic_index: idx.health_check(),
                build_status_check=self._check_semantic_build_status,
                rebuild=lambda: None,  # SemanticIndex doesn't have targeted rebuild yet (full rebuild only)
                dependencies=[],
            )
            
            # Graph index is optional (conditional registration)
            if config.graph.enabled:
                self.components["graph"] = ComponentDescriptor(
                    name="graph",
                    provides=["ast_nodes", "symbols", "relationships"],
                    capabilities=["search_ast", "find_callers", "find_dependencies", "find_call_paths"],
                    health_check=lambda idx=self._graph_index: idx.health_check(),
                    build_status_check=self._check_graph_build_status,
                    rebuild=lambda: None,  # GraphIndex has component-level rebuilds internally, not at container level
                    dependencies=[],
                )
        
        component_names = list(self.components.keys())
        logger.info("CodeIndex container initialized with component registry (%s) and lock management", ", ".join(component_names))
    
    def _initialize_partitions(self, config: CodeIndexConfig, base_path: Path) -> Dict[str, Any]:
        """Initialize partitions from config (multi-repo mode).
        
        Args:
            config: CodeIndexConfig with partitions defined
            base_path: Base path for index storage
            
        Returns:
            Dict mapping partition name to CodePartition instance
        """
        from ouroboros.subsystems.rag.code.partition import CodePartition
        
        partitions: Dict[str, "CodePartition"] = {}
        
        if not config.partitions:
            return partitions
        
        for partition_name, partition_config in config.partitions.items():
            try:
                logger.info("Initializing partition '%s'", partition_name)
                
                # Resolve repository path
                repo_path = (base_path / partition_config.path).resolve()
                logger.info("  Partition '%s' repo_path: %s", partition_name, repo_path)
                
                if not repo_path.exists():
                    logger.warning(
                        "Partition '%s' repository path does not exist: %s (skipping)",
                        partition_name,
                        repo_path
                    )
                    continue
                
                logger.info("  Partition '%s' repo exists, initializing indexes", partition_name)
                
                # Create partition-specific database paths
                # Partitions are stored at: base_path/.cache/indexes/code/{partition_name}/
                partition_base = base_path / ".cache" / "indexes" / "code" / partition_name
                partition_base.mkdir(parents=True, exist_ok=True)
                
                # Define explicit paths for sub-indexes (config-driven, no hardcoding!)
                semantic_index_path = partition_base / "semantic.lance"
                graph_db_path = partition_base / "graph.duckdb"
                
                # Initialize semantic index for this partition with explicit path
                logger.info("  Partition '%s' initializing SemanticIndex", partition_name)
                semantic_index = SemanticIndex(
                    config=config,
                    base_path=base_path,  # For resolving source_paths
                    index_path=semantic_index_path,  # Explicit partition-specific path
                    partition_name=partition_name  # Pass partition name for chunk tagging
                )
                logger.info("  Partition '%s' SemanticIndex initialized successfully", partition_name)
                
                # Initialize graph index for this partition with explicit path
                logger.info("  Partition '%s' initializing GraphIndex with db_path=%s", partition_name, graph_db_path)
                graph_index = GraphIndex(
                    config=config.graph,
                    base_path=base_path,  # For resolving source_paths
                    languages=config.languages,
                    code_config=config.model_dump(),
                    db_path=graph_db_path  # Explicit partition-specific path
                )
                logger.info("  Partition '%s' GraphIndex initialized successfully", partition_name)
                
                # Wrap in CodePartition container
                partition = CodePartition(
                    partition_name=partition_name,
                    partition_config=partition_config,
                    base_path=base_path,
                    semantic_index=semantic_index,
                    graph_index=graph_index
                )
                
                partitions[partition_name] = partition
                
                logger.info(
                    "Partition '%s' initialized: %d domains, path=%s",
                    partition_name,
                    len(partition_config.domains),
                    repo_path
                )
            
            except Exception as e:
                logger.error(
                    "Failed to initialize partition '%s': %s (skipping)",
                    partition_name,
                    str(e),
                    exc_info=True
                )
        
        if not partitions:
            raise ActionableError(
                what_failed="Initialize CodeIndex partitions",
                why_failed="No partitions were successfully initialized",
                how_to_fix="Check partition configs in mcp.yaml and ensure repository paths exist"
            )
        
        return partitions
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build code index (both semantic and graph) from source paths.
        
        Acquires exclusive lock before building to prevent concurrent corruption.
        
        In multi-partition mode, builds all partitions. Each partition's source paths
        are determined by its configured repository path (not the source_paths parameter).
        
        In single-repo mode, builds both indexes from the provided source paths.
        
        Args:
            source_paths: Paths to source directories (used in single-repo mode only)
            force: If True, rebuild even if indexes exist
            
        Raises:
            ActionableError: If build fails or lock cannot be acquired
        """
        logger.info("CodeIndex.build() acquiring exclusive lock")
        
        # Set building flag (ADDENDUM-2025-11-17: Build Status Integration)
        with self._build_lock:
            self._building = True
        
        try:
            with self._lock_manager.exclusive_lock():
                if self._multi_partition_mode:
                    # Multi-partition build: iterate over all partitions
                    logger.info("CodeIndex.build() building %d partitions", len(self._partitions))
                    
                    for partition_name, partition in self._partitions.items():
                        try:
                            logger.info("Building partition '%s' from path: %s", partition_name, partition.path)
                            
                            # Collect source paths from all domains (code, tests, docs, etc.)
                            source_paths = []
                            for domain_name, domain_config in partition.domains.items():
                                if domain_config.include_paths:
                                    # Resolve include_paths relative to partition path
                                    for include_path in domain_config.include_paths:
                                        full_path = partition.path / include_path
                                        source_paths.append(full_path)
                                        logger.info("  Domain '%s' include path: %s", domain_name, full_path)
                            
                            # Fallback to partition root if no include_paths specified
                            if not source_paths:
                                source_paths = [partition.path]
                                logger.info("  No include_paths specified, using partition root: %s", partition.path)
                            
                            # Build semantic index for this partition
                            if partition.semantic:
                                logger.info("  Building semantic index for '%s' with %d source paths", partition_name, len(source_paths))
                                partition.semantic.build(source_paths, force)
                            
                            # Build graph index for this partition
                            if partition.graph:
                                logger.info("  Building graph index for '%s' with %d source paths", partition_name, len(source_paths))
                                partition.graph.build(source_paths, force)
                            
                            logger.info("  ✅ Partition '%s' built successfully", partition_name)
                        
                        except Exception as e:
                            logger.error("Failed to build partition '%s': %s", partition_name, e, exc_info=True)
                            # Continue with other partitions (graceful degradation)
                    
                    logger.info("✅ CodeIndex multi-partition build complete")
                else:
                    # Legacy single-repo build
                    logger.info("CodeIndex.build() building semantic index (LanceDB)")
                    self._semantic_index.build(source_paths, force)
                    
                    logger.info("CodeIndex.build() building graph index (DuckDB)")
                    self._graph_index.build(source_paths, force)
                    
                    logger.info("✅ CodeIndex built successfully (semantic + graph)")
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
        """Search code index using semantic search (CodeBERT embeddings).
        
        Delegates to SemanticIndex for hybrid search (vector + FTS + RRF).
        Acquires shared lock for read access (allows multiple concurrent readers).
        
        In multi-partition mode, searches across all partitions or specific partition
        if 'partition' filter is provided.
        
        For structural queries, use search_ast().
        For graph traversal, use find_callers/find_dependencies/find_call_paths().
        
        Args:
            query: Natural language or code search query
            n_results: Number of results to return
            filters: Optional filters (language, file_path, partition, domain, metadata)
            
        Returns:
            List of SearchResult objects with line ranges
            
        Raises:
            IndexError: If search fails (after auto-repair attempt if corrupted)
        """
        with self._lock_manager.shared_lock():
            try:
                if self._multi_partition_mode:
                    # Multi-partition search routing
                    filters = filters or {}
                    partition_filter = filters.get("partition")
                    
                    if partition_filter:
                        # Search specific partition (FRACTAL DELEGATION - preserve filters dict)
                        if partition_filter not in self._partitions:
                            raise ActionableError(
                                what_failed=f"Search partition '{partition_filter}'",
                                why_failed=f"Partition '{partition_filter}' not found",
                                how_to_fix=f"Available partitions: {list(self._partitions.keys())}"
                            )
                        return self._partitions[partition_filter].search(  # type: ignore[no-any-return]
                            query, "search_code", 
                            filters=filters,
                            n_results=n_results
                        )
                    else:
                        # Search all partitions and aggregate (FRACTAL DELEGATION - preserve filters dict)
                        all_results = []
                        for partition_name, partition in self._partitions.items():
                            try:
                                results = partition.search(query, "search_code", filters=filters, n_results=n_results)
                                # Add partition metadata
                                for result in results:
                                    if hasattr(result, 'metadata'):
                                        result.metadata["_partition"] = partition_name
                                all_results.extend(results)
                            except Exception as e:
                                logger.warning(
                                    "Partition '%s' search failed: %s (continuing)",
                                    partition_name,
                                    str(e)
                                )
                        
                        # Sort by relevance and limit
                        all_results.sort(key=lambda x: getattr(x, 'score', 0), reverse=True)
                        return all_results[:n_results]
                else:
                    # Legacy single-repo mode
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
                        what_failed="Search code index (semantic)",
                        why_failed=f"Index corrupted: {e}",
                        how_to_fix="Auto-repair has been triggered. Wait for rebuild to complete or manually rebuild the index."
                    ) from e
                else:
                    # Not a corruption error, re-raise
                    raise
    
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update code index (both semantic and graph) for changed files.
        
        Acquires exclusive lock before updating to prevent concurrent corruption.
        
        In multi-partition mode, routes changed files to the appropriate partition
        based on file path matching.
        
        In single-repo mode, updates both indexes with all changed files.
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails or lock cannot be acquired
        """
        logger.info("CodeIndex.update() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            if self._multi_partition_mode:
                # Multi-partition update: route files to appropriate partition
                logger.info("CodeIndex.update() routing %d files to partitions", len(changed_files))
                
                # Group files by partition
                partition_files: Dict[str, List[Path]] = {name: [] for name in self._partitions.keys()}
                unmatched_files = []
                
                for file_path in changed_files:
                    matched = False
                    # Check which partition this file belongs to
                    for partition_name, partition in self._partitions.items():
                        try:
                            # Check if file is relative to partition's repo path
                            file_path.resolve().relative_to(partition.path)
                            partition_files[partition_name].append(file_path)
                            matched = True
                            break
                        except ValueError:
                            # File is not in this partition
                            continue
                    
                    if not matched:
                        unmatched_files.append(file_path)
                
                if unmatched_files:
                    logger.warning(
                        "CodeIndex.update() %d files don't match any partition: %s",
                        len(unmatched_files),
                        [str(f) for f in unmatched_files[:5]]  # Show first 5
                    )
                
                # Update each partition with its files (fractal delegation pattern)
                for partition_name, files in partition_files.items():
                    if not files:
                        continue
                    
                    try:
                        partition = self._partitions[partition_name]
                        logger.info("  Updating partition '%s' with %d files (parse-once-index-thrice)", partition_name, len(files))
                        
                        # Domain detection (TODO: enhance with path patterns)
                        domain = "code"
                        
                        # FRACTAL DELEGATION PATTERN:
                        # 1. Prepare parse cache (parse once)
                        parse_stats = self._incremental_indexer.prepare_updates(
                            files=files,
                            partition=partition_name,
                            domain=domain
                        )
                        logger.info(
                            "    Parse cache prepared: %d files parsed in %.2fms",
                            parse_stats.files_processed,
                            parse_stats.total_time_ms
                        )
                        
                        # 2. Activate cache for indexes to use
                        from ouroboros.subsystems.rag.code.indexer import set_active_parse_cache
                        set_active_parse_cache(self._incremental_indexer)
                        
                        try:
                            # 3. Delegate to SemanticIndex (standard interface, uses cache)
                            if partition.semantic:
                                try:
                                    partition.semantic.update(files)
                                    logger.info("    ✅ SemanticIndex updated")
                                except Exception as e:
                                    logger.error("    ❌ SemanticIndex update failed: %s", str(e))
                            
                            # 4. Delegate to GraphIndex (standard interface, uses cache)
                            if partition.graph:
                                try:
                                    partition.graph.update(files)
                                    logger.info("    ✅ GraphIndex updated")
                                except Exception as e:
                                    logger.error("    ❌ GraphIndex update failed: %s", str(e))
                        
                        finally:
                            # 5. Deactivate cache and clear
                            set_active_parse_cache(None)
                            cleared = self._incremental_indexer.clear_cache()
                            logger.info("    Parse cache deactivated and cleared (%d entries)", cleared)
                        
                        # Summary
                        logger.info(
                            "  ✅ Partition '%s' updated: %d files processed, %d errors",
                            partition_name,
                            parse_stats.files_processed,
                            len(parse_stats.errors)
                        )
                    
                    except Exception as e:
                        logger.error("Failed to update partition '%s': %s", partition_name, e, exc_info=True)
                        # Clear cache on error to prevent stale data
                        self._incremental_indexer.clear_cache()
                        # Continue with other partitions (graceful degradation)
                
                logger.info("✅ CodeIndex multi-partition update complete")
            else:
                # Legacy single-repo update (fractal delegation pattern)
                logger.info("CodeIndex.update() updating with parse-once-index-thrice optimization")
                
                try:
                    # FRACTAL DELEGATION PATTERN:
                    # 1. Prepare parse cache (parse once)
                    parse_stats = self._incremental_indexer.prepare_updates(
                        files=changed_files,
                        partition="default",
                        domain="code"
                    )
                    logger.info(
                        "  Parse cache prepared: %d files parsed in %.2fms",
                        parse_stats.files_processed,
                        parse_stats.total_time_ms
                    )
                    
                    # 2. Activate cache for indexes to use
                    from ouroboros.subsystems.rag.code.indexer import set_active_parse_cache
                    set_active_parse_cache(self._incremental_indexer)
                    
                    try:
                        # 3. Delegate to SemanticIndex (standard interface, uses cache)
                        try:
                            self._semantic_index.update(changed_files)
                            logger.info("  ✅ SemanticIndex updated")
                        except Exception as e:
                            logger.error("  ❌ SemanticIndex update failed: %s", str(e))
                        
                        # 4. Delegate to GraphIndex (standard interface, uses cache)
                        try:
                            self._graph_index.update(changed_files)
                            logger.info("  ✅ GraphIndex updated")
                        except Exception as e:
                            logger.error("  ❌ GraphIndex update failed: %s", str(e))
                    
                    finally:
                        # 5. Deactivate cache and clear
                        set_active_parse_cache(None)
                        cleared = self._incremental_indexer.clear_cache()
                        logger.info("  Parse cache deactivated and cleared (%d entries)", cleared)
                    
                    # Summary
                    logger.info(
                        "✅ CodeIndex updated: %d files processed, %d errors",
                        parse_stats.files_processed,
                        len(parse_stats.errors)
                    )
                
                except Exception as e:
                    logger.error("CodeIndex update failed: %s", str(e), exc_info=True)
                    # Ensure cache is cleaned up on error
                    from ouroboros.subsystems.rag.code.indexer import set_active_parse_cache
                    set_active_parse_cache(None)
                    self._incremental_indexer.clear_cache()
                    raise
    
    # Component-specific build status checks for fractal pattern
    def _check_semantic_build_status(self) -> BuildStatus:
        """Check semantic component build status.
        
        Verifies whether the LanceDB table exists and has code embeddings.
        
        Checks (in order):
        1. Progress file (if building) - returns BUILDING state
        2. Table exists and has rows - returns BUILT state
        3. Table doesn't exist - returns NOT_BUILT state
        
        Returns:
            BuildStatus for semantic component
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
                    message=f"Semantic index built ({chunk_count} chunks)",
                    progress_percent=100.0,
                    details={"chunk_count": chunk_count},
                )
            else:
                return BuildStatus(
                    state=IndexBuildState.NOT_BUILT,
                    message="Semantic index not built (no chunks)",
                    progress_percent=0.0,
                    details={"chunk_count": 0},
                )
        
        except Exception as e:
            logger.error(f"Semantic build status check failed: {e}", exc_info=True)
            return BuildStatus(
                state=IndexBuildState.FAILED,
                message=f"Semantic build status check failed: {type(e).__name__}",
                progress_percent=0.0,
                error=str(e),
                details={"error": str(e), "error_type": type(e).__name__},
            )
    
    def _check_graph_build_status(self) -> BuildStatus:
        """Check graph component build status.
        
        Verifies whether the DuckDB tables (AST + graph) exist and have data.
        Graph is optional - if disabled in config, returns BUILT (not required).
        
        Returns:
            BuildStatus for graph component
        """
        try:
            # Check if graph is enabled in config
            if not self.config.graph.enabled:
                return BuildStatus(
                    state=IndexBuildState.BUILT,
                    message="Graph disabled in config (not required)",
                    progress_percent=100.0,
                    details={"enabled": False},
                )
            
            # Check if graph tables exist (delegate to health check logic)
            health = self._graph_index.health_check()
            
            if health.healthy:
                return BuildStatus(
                    state=IndexBuildState.BUILT,
                    message="Graph index built and functional",
                    progress_percent=100.0,
                    details=health.details,
                )
            else:
                return BuildStatus(
                    state=IndexBuildState.NOT_BUILT,
                    message="Graph index not built or unhealthy",
                    progress_percent=0.0,
                    details=health.details,
                )
        
        except Exception as e:
            logger.error(f"Graph build status check failed: {e}", exc_info=True)
            return BuildStatus(
                state=IndexBuildState.FAILED,
                message=f"Graph build status check failed: {type(e).__name__}",
                progress_percent=0.0,
                error=str(e),
                details={"error": str(e), "error_type": type(e).__name__},
            )
    
    def health_check(self) -> HealthStatus:
        """Dynamic health check using component registry (fractal pattern).
        
        ADDENDUM-2025-11-17: Now checks build status first, skips validation if building.
        
        Delegates to dynamic_health_check() which:
        1. Calls each component's health_check() lambda
        2. Aggregates results into nested structure
        3. Determines overall health from component health
        
        The component registry enables:
        - Dynamic health aggregation (no hardcoded component names)
        - Nested health reporting (graph component shows ast + graph sub-components)
        - Partial degradation detection (e.g., semantic broken but graph healthy)
        - Targeted diagnostics (pinpoint which component is unhealthy)
        
        Returns:
            HealthStatus with nested components dict showing health of semantic and graph
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
        
        ADDENDUM-2025-11-17: Now checks container-level building flag first.
        
        Aggregates build status from all registered components (semantic, graph)
        using priority-based selection (worst state bubbles up). This provides
        granular visibility into build progress and enables partial build scenarios.
        
        Returns:
            BuildStatus with aggregated state from all components
        """
        # Check if container is building (ADDENDUM-2025-11-17)
        with self._build_lock:
            is_building = self._building
        
        if is_building:
            return BuildStatus(
                state=IndexBuildState.BUILDING,
                message="Building code index...",
                progress_percent=50.0,
                details={"component": "code"}
            )
        
        # Aggregate from components (fractal pattern)
        return dynamic_build_status(self.components)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get code index statistics (aggregated from semantic + graph).
        
        Returns statistics from both sub-indexes:
        - Semantic: chunk_count, embedding_model, languages, fts_enabled
        - Graph: ast_node_count, symbol_count, relationship_count
        
        In multi-partition mode, aggregates stats across all partitions.
        
        Returns:
            Dictionary with aggregated statistics
        """
        if self._multi_partition_mode:
            # Multi-partition stats aggregation
            partition_stats = {}
            total_chunks = 0
            total_ast_nodes = 0
            total_symbols = 0
            total_relationships = 0
            
            for partition_name, partition in self._partitions.items():
                try:
                    # Get partition-level stats (will aggregate from its sub-indexes)
                    if hasattr(partition, 'semantic') and partition.semantic:
                        semantic_stats = partition.semantic.get_stats()
                        total_chunks += semantic_stats.get("chunk_count", 0)
                    
                    if hasattr(partition, 'graph') and partition.graph:
                        graph_stats = partition.graph.get_stats()
                        total_ast_nodes += graph_stats.get("ast_node_count", 0)
                        total_symbols += graph_stats.get("symbol_count", 0)
                        total_relationships += graph_stats.get("relationship_count", 0)
                    
                    partition_stats[partition_name] = {
                        "domains": list(partition.domains.keys()),
                        "path": str(partition.path)
                    }
                except Exception as e:
                    logger.error("Failed to get stats for partition '%s': %s", partition_name, e)
                    partition_stats[partition_name] = {"error": str(e)}
            
            return {
                "mode": "multi-partition",
                "partition_count": len(self._partitions),
                "partitions": partition_stats,
                "chunk_count": total_chunks,  # For diagnostics compatibility
                "ast_node_count": total_ast_nodes,  # For diagnostics compatibility
                "symbol_count": total_symbols,  # For diagnostics compatibility
                "relationship_count": total_relationships,  # For diagnostics compatibility
            }
        else:
            # Legacy single-repo stats
            semantic_stats = self._semantic_index.get_stats()
            graph_stats = self._graph_index.get_stats()
            
            return {
                "mode": "single-repo",
                "semantic": semantic_stats,
                "graph": graph_stats,
                "total_chunks": semantic_stats.get("chunk_count", 0),
                "total_ast_nodes": graph_stats.get("ast_node_count", 0),
                "total_symbols": graph_stats.get("symbol_count", 0),
                "total_relationships": graph_stats.get("relationship_count", 0),
            }
    
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
            self._corruption_handler = lambda e: handler("code", e)
        else:
            self._corruption_handler = None
    
    # ========================================================================
    # Extended Methods (not in BaseIndex, specific to code index)
    # ========================================================================
    
    def search_ast(
        self,
        pattern: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search AST index by node type or symbol name (structural search).
        
        Delegates to GraphIndex for AST pattern queries.
        Enables finding code by structure, not semantics.
        
        In multi-partition mode, searches across all partitions or specific partition
        if 'partition' filter is provided.
        
        Examples:
            - search_ast("function_definition") → all functions
            - search_ast("async_function") → all async functions
            - search_ast("error_handler") → error handling code
        
        Args:
            pattern: Node type or symbol name pattern to search
            n_results: Max results to return
            filters: Optional filters (language, file_path, node_type, partition)
            
        Returns:
            List of dictionaries with AST node information
            
        Raises:
            IndexError: If query fails
        """
        with self._lock_manager.shared_lock():
            if self._multi_partition_mode:
                # Multi-partition AST search routing
                filters = filters or {}
                partition_filter = filters.get("partition")
                
                if partition_filter:
                    # Search specific partition
                    if partition_filter not in self._partitions:
                        raise ActionableError(
                            what_failed=f"Search AST in partition '{partition_filter}'",
                            why_failed=f"Partition '{partition_filter}' not found",
                            how_to_fix=f"Available partitions: {list(self._partitions.keys())}"
                        )
                    # FRACTAL COMPLIANCE: Pass filters as dict, n_results in kwargs
                    return self._partitions[partition_filter].search(  # type: ignore[no-any-return]
                        query=pattern, 
                        action="search_ast", 
                        filters=filters,
                        n_results=n_results
                    )
                else:
                    # Search all partitions and aggregate
                    all_results = []
                    for partition_name, partition in self._partitions.items():
                        try:
                            # FRACTAL COMPLIANCE: Pass filters as dict, n_results in kwargs
                            results = partition.search(
                                query=pattern, 
                                action="search_ast", 
                                filters=filters,
                                n_results=n_results
                            )
                            # Add partition metadata
                            for result in results:
                                result["_partition"] = partition_name
                            all_results.extend(results)
                        except Exception as e:
                            logger.warning(
                                "Partition '%s' AST search failed: %s (continuing)",
                                partition_name,
                                str(e)
                            )
                    return all_results[:n_results]
            else:
                # Legacy single-repo mode
                if self._graph_index is None:
                    raise ActionableError(
                        what_failed="Search AST",
                        why_failed="Graph index is disabled",
                        how_to_fix="Enable graph index in config: graph.enabled = true"
                    )
                return self._graph_index.search_ast(pattern, n_results, filters)
    
    def find_callers(self, symbol_name: str, max_depth: int = 10, partition: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find who calls the given symbol (reverse lookup).
        
        Delegates to GraphIndex for recursive CTE graph traversal.
        
        In multi-partition mode, searches within a specific partition (required).
        Graph traversal is partition-isolated by default.
        
        Example:
            find_callers("process_request", max_depth=3, partition="praxis-os")
            → Returns: handle_api_call, main, server_loop (chain of callers)
        
        Args:
            symbol_name: Name of the symbol to find callers for
            max_depth: Maximum traversal depth (default: 10)
            partition: Required in multi-partition mode (which repo to search)
            
        Returns:
            List of caller information with paths
            
        Raises:
            IndexError: If query fails
            ActionableError: If partition is required but not provided
        """
        with self._lock_manager.shared_lock():
            if self._multi_partition_mode:
                # Multi-partition mode: require partition specification
                if not partition:
                    raise ActionableError(
                        what_failed="Find callers in multi-partition mode",
                        why_failed="Partition not specified",
                        how_to_fix=f"Provide partition parameter. Available: {list(self._partitions.keys())}"
                    )
                
                if partition not in self._partitions:
                    raise ActionableError(
                        what_failed=f"Find callers in partition '{partition}'",
                        why_failed=f"Partition '{partition}' not found",
                        how_to_fix=f"Available partitions: {list(self._partitions.keys())}"
                    )
                
                return self._partitions[partition].search(symbol_name, "find_callers", max_depth=max_depth)  # type: ignore[no-any-return]
            else:
                # Legacy single-repo mode
                if self._graph_index is None:
                    raise ActionableError(
                        what_failed="Find callers",
                        why_failed="Graph index is disabled",
                        how_to_fix="Enable graph index in config: graph.enabled = true"
                    )
                return self._graph_index.find_callers(symbol_name, max_depth)
    
    def find_dependencies(self, symbol_name: str, max_depth: int = 10, partition: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find what the given symbol calls (forward lookup).
        
        Delegates to GraphIndex for recursive CTE graph traversal.
        
        In multi-partition mode, searches within a specific partition (required).
        Graph traversal is partition-isolated by default.
        
        Example:
            find_dependencies("main", max_depth=3, partition="praxis-os")
            → Returns: init_app, load_config, start_server (chain of calls)
        
        Args:
            symbol_name: Name of the symbol to find dependencies for
            max_depth: Maximum traversal depth (default: 10)
            partition: Required in multi-partition mode (which repo to search)
            
        Returns:
            List of dependency information with paths
            
        Raises:
            IndexError: If query fails
            ActionableError: If partition is required but not provided
        """
        with self._lock_manager.shared_lock():
            if self._multi_partition_mode:
                # Multi-partition mode: require partition specification
                if not partition:
                    raise ActionableError(
                        what_failed="Find dependencies in multi-partition mode",
                        why_failed="Partition not specified",
                        how_to_fix=f"Provide partition parameter. Available: {list(self._partitions.keys())}"
                    )
                
                if partition not in self._partitions:
                    raise ActionableError(
                        what_failed=f"Find dependencies in partition '{partition}'",
                        why_failed=f"Partition '{partition}' not found",
                        how_to_fix=f"Available partitions: {list(self._partitions.keys())}"
                    )
                
                return self._partitions[partition].search(symbol_name, "find_dependencies", max_depth=max_depth)  # type: ignore[no-any-return]
            else:
                # Legacy single-repo mode
                if self._graph_index is None:
                    raise ActionableError(
                        what_failed="Find dependencies",
                        why_failed="Graph index is disabled",
                        how_to_fix="Enable graph index in config: graph.enabled = true"
                    )
                return self._graph_index.find_dependencies(symbol_name, max_depth)
    
    def find_call_paths(
        self,
        from_symbol: str,
        to_symbol: str,
        max_depth: int = 10,
        partition: Optional[str] = None
    ) -> List[List[str]]:
        """Find call paths from one symbol to another.
        
        Delegates to GraphIndex for recursive CTE path finding.
        
        In multi-partition mode, searches within a specific partition (required).
        Graph traversal is partition-isolated by default.
        
        Example:
            find_call_paths("main", "database_query", max_depth=5, partition="praxis-os")
            → Returns: [["main", "init_app", "setup_db", "database_query"],
                       ["main", "process_request", "database_query"]]
        
        Args:
            from_symbol: Starting symbol name
            to_symbol: Target symbol name
            max_depth: Maximum path length (default: 10)
            partition: Required in multi-partition mode (which repo to search)
            
        Returns:
            List of call paths (each path is a list of symbol names)
            
        Raises:
            IndexError: If query fails
            ActionableError: If partition is required but not provided
        """
        with self._lock_manager.shared_lock():
            if self._multi_partition_mode:
                # Multi-partition mode: require partition specification
                if not partition:
                    raise ActionableError(
                        what_failed="Find call paths in multi-partition mode",
                        why_failed="Partition not specified",
                        how_to_fix=f"Provide partition parameter. Available: {list(self._partitions.keys())}"
                    )
                
                if partition not in self._partitions:
                    raise ActionableError(
                        what_failed=f"Find call paths in partition '{partition}'",
                        why_failed=f"Partition '{partition}' not found",
                        how_to_fix=f"Available partitions: {list(self._partitions.keys())}"
                    )
                
                return self._partitions[partition].search(  # type: ignore[no-any-return]
                    from_symbol, 
                    "find_call_paths",
                    to_symbol=to_symbol,
                    max_depth=max_depth
                )
            else:
                # Legacy single-repo mode
                if self._graph_index is None:
                    raise ActionableError(
                        what_failed="Find call paths",
                        why_failed="Graph index is disabled",
                        how_to_fix="Enable graph index in config: graph.enabled = true"
                    )
                return self._graph_index.find_call_paths(from_symbol, to_symbol, max_depth)

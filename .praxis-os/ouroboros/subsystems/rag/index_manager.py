"""Index Manager: Central orchestrator for all RAG indexes.

Responsibilities:
- Route search queries to correct index (standards, code, ast)
- Initialize indexes from config
- Coordinate incremental updates from FileWatcher
- Expose unified search interface to tools layer
- Health checks and auto-repair

Design Principles:
- Config-driven: No hardcoded index initialization
- Fail-fast: Invalid configs crash at startup, not runtime
- Graceful degradation: Missing indexes log errors but don't crash server
- Clean architecture: Subsystem layer, depends only on Foundation + Config
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ouroboros.config.schemas.indexes import IndexesConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from ouroboros.utils.errors import ActionableError, IndexError

logger = logging.getLogger(__name__)


# INDEX_REGISTRY: Maps index name → (module_path, class_name, description)
# This registry enables dynamic index initialization without modifying IndexManager code.
# To add a new index: add entry here + add config schema + implement BaseIndex interface
INDEX_REGISTRY = {
    "standards": (
        "ouroboros.subsystems.rag.standards",  # Submodule path
        "StandardsIndex",  # Container class implementing BaseIndex
        "Standards documentation (hybrid: vector + FTS + RRF)"
    ),
    "code": (
        "ouroboros.subsystems.rag.code",  # Submodule path
        "CodeIndex",  # Container class implementing BaseIndex
        "Code semantic + structural + graph (LanceDB + DuckDB)"
    ),
}


class IndexManager:
    """Central orchestrator for all RAG indexes.
    
    This class routes queries to the appropriate index type (standards, code, ast)
    and coordinates updates from the file watcher.
    
    Architecture:
        Tools Layer (pos_search_project)
            ↓
        IndexManager (this class)
            ↓
        ├─ StandardsIndex (hybrid: vector + FTS + RRF)
        ├─ CodeIndex (semantic: LanceDB + graph: DuckDB)
        └─ ASTIndex (structural: Tree-sitter)
    """
    
    def __init__(self, config: IndexesConfig, base_path: Path):
        """Initialize IndexManager with configuration.
        
        Args:
            config: IndexesConfig from MCPConfig
            base_path: Base path for resolving relative paths (.praxis-os/)
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Index registry: {index_name: BaseIndex}
        self._indexes: Dict[str, BaseIndex] = {}
        
        # Initialize indexes based on config
        try:
            self._init_indexes()
            logger.info("IndexManager initialized with %d indexes", len(self._indexes))
        except Exception as e:
            raise ActionableError(
                what_failed="IndexManager initialization",
                why_failed=str(e),
                how_to_fix="Check index configurations in config/mcp.yaml. Ensure paths are valid and dependencies installed."
            ) from e
    
    def _init_indexes(self) -> None:
        """Initialize all configured indexes dynamically.
        
        Uses INDEX_REGISTRY (module-level constant) to discover and initialize indexes
        based on config. If an index fails to initialize, it logs an error but continues
        with other indexes (graceful degradation).
        
        Registry-based initialization allows adding new index types without modifying
        this method - just add entry to module-level INDEX_REGISTRY.
        
        Note: The registry pattern replaces hardcoded imports, enabling:
        - Easy addition of new indexes (add to INDEX_REGISTRY + config + BaseIndex impl)
        - Graceful degradation (missing indexes log warnings, don't crash server)
        - Clean separation of concerns (IndexManager doesn't know implementation details)
        """
        # Dynamically initialize each configured index from module-level INDEX_REGISTRY
        for index_name, (module_path, class_name, description) in INDEX_REGISTRY.items():
            # Check if this index is configured
            if not hasattr(self.config, index_name):
                logger.debug(f"Index '{index_name}' not in config, skipping")
                continue
            
            index_config = getattr(self.config, index_name)
            if not index_config:
                logger.debug(f"Index '{index_name}' is None/disabled, skipping")
                continue
            
            # Attempt to initialize the index
            try:
                # Dynamic import: loads the submodule's container class
                # Example: "ouroboros.subsystems.rag.standards" → StandardsIndex
                module = __import__(module_path, fromlist=[class_name])
                index_class = getattr(module, class_name)
                
                # Instantiate with standard BaseIndex interface (config + base_path)
                index_instance = index_class(
                    config=index_config,
                    base_path=self.base_path
                )
                
                self._indexes[index_name] = index_instance
                logger.info(f"✅ {class_name} initialized: {description}")
                
            except ImportError as e:
                logger.warning(f"{class_name} not available (module not found): {e}")
            except Exception as e:
                logger.error(f"Failed to initialize {class_name}: {e}", exc_info=True)
        
        # Validate that at least one index initialized successfully
        if not self._indexes:
            raise ActionableError(
                what_failed="IndexManager initialization",
                why_failed="No indexes were successfully initialized",
                how_to_fix="Check that at least one index is enabled in config/mcp.yaml and dependencies are installed."
            )
    
    def route_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """Route action to correct index dynamically.
        
        This is the main entry point for the pos_search_project tool.
        Uses a registry pattern to map actions to indexes and methods,
        allowing new actions without code changes.
        
        Supported actions (dynamically discovered):
        - search_*: Search specific index (e.g., search_standards, search_code, search_ast)
        - find_*: Graph queries (e.g., find_callers, find_dependencies, find_call_paths)
        
        Args:
            action: The action to perform
            **kwargs: Action-specific parameters
            
        Returns:
            Dictionary with action results
            
        Raises:
            ActionableError: If action is invalid or execution fails
        """
        # Action registry: maps action pattern → (index_name, method_name, is_search)
        # This allows adding new actions without modifying this method
        # Note: Graph operations (find_*, search_ast) now route to CodeIndex (dual-database architecture)
        ACTION_REGISTRY = {
            "search_standards": ("standards", "search", True),
            "search_code": ("code", "search", True),
            "search_ast": ("code", "search_ast", False),  # AST search via CodeIndex.search_ast()
            "find_callers": ("code", "find_callers", False),  # Graph via CodeIndex.find_callers()
            "find_dependencies": ("code", "find_dependencies", False),  # Graph via CodeIndex.find_dependencies()
            "find_call_paths": ("code", "find_call_paths", False),  # Graph via CodeIndex.find_call_paths()
        }
        
        # Check if action is in registry
        if action not in ACTION_REGISTRY:
            valid_actions = ", ".join(ACTION_REGISTRY.keys())
            raise ActionableError(
                what_failed=f"route_action({action})",
                why_failed=f"Unknown action: {action}",
                how_to_fix=f"Valid actions: {valid_actions}"
            )
        
        index_name, method_name, is_search = ACTION_REGISTRY[action]
        
        # Check if index is available
        if index_name not in self._indexes:
            raise IndexError(
                what_failed=action,
                why_failed=f"{index_name.capitalize()}Index not available",
                how_to_fix=f"Ensure {index_name} index is configured in config/mcp.yaml and dependencies are installed"
            )
        
        # Execute the action
        try:
            index = self._indexes[index_name]
            
            if is_search:
                # Standard search actions
                results = index.search(**kwargs)
                response = {
                    "status": "success",
                    "results": [result.model_dump() for result in results],
                    "count": len(results)
                }
                
                # Add diagnostics if results are empty
                if len(results) == 0:
                    response["diagnostics"] = self._generate_diagnostics(
                        action, index_name, index, kwargs
                    )
                
                return response
            else:
                # Custom methods (e.g., graph queries, AST search)
                method = getattr(index, method_name)
                
                # Store original query for diagnostics
                original_query = kwargs.get("query")
                
                # Parameter mapping for methods with different signatures
                if method_name == "search_ast" and "query" in kwargs:
                    # search_ast expects 'pattern' not 'query'
                    kwargs["pattern"] = kwargs.pop("query")
                
                results = method(**kwargs)
                result_list = results if isinstance(results, list) else [results]
                
                response = {
                    "status": "success",
                    "results": result_list,
                    "count": len(result_list)
                }
                
                # Add diagnostics if results are empty
                if len(result_list) == 0:
                    # Restore query for diagnostics
                    if original_query:
                        kwargs["query"] = original_query
                    response["diagnostics"] = self._generate_diagnostics(
                        action, index_name, index, kwargs
                    )
                
                return response
                
        except Exception as e:
            logger.error("%s failed: %s", action, e, exc_info=True)
            raise IndexError(
                what_failed=action,
                why_failed=str(e),
                how_to_fix="Check server logs for details. Ensure index is built and dependencies are installed."
            ) from e
    
    def _generate_diagnostics(
        self, action: str, index_name: str, index: Any, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate diagnostic information for empty search results.
        
        Provides helpful context when queries return no results, including:
        - Index health status
        - Total entries in index
        - Query pattern used
        - Suggestions for what to try next
        
        Args:
            action: The action that returned empty results
            index_name: Name of the index that was queried
            index: The index instance
            kwargs: Query parameters
            
        Returns:
            Dictionary with diagnostic information
        """
        diagnostics = {
            "index_name": index_name,
            "index_health": "unknown",
            "total_entries": 0,
        }
        
        # Get index health
        try:
            health = index.health_check()
            diagnostics["index_health"] = "healthy" if health.healthy else "unhealthy"
            if not health.healthy:
                diagnostics["health_message"] = health.message
        except Exception as e:
            logger.warning("Failed to check index health for diagnostics: %s", e)
            diagnostics["index_health"] = "error"
        
        # Get total entries
        try:
            stats = index.get_stats()
            if action == "search_ast":
                diagnostics["total_entries"] = stats.get("ast_node_count", 0)
            elif action in ("find_callers", "find_dependencies", "find_call_paths"):
                diagnostics["total_entries"] = stats.get("symbol_count", 0)
            elif action == "search_code":
                diagnostics["total_entries"] = stats.get("chunk_count", 0)
            elif action == "search_standards":
                diagnostics["total_entries"] = stats.get("chunk_count", 0)
        except Exception as e:
            logger.warning("Failed to get index stats for diagnostics: %s", e)
        
        # Add query pattern
        query_value = kwargs.get("query") or kwargs.get("pattern")
        if query_value:
            diagnostics["query_pattern"] = query_value
        
        # Add action-specific suggestions
        if action == "search_ast":
            diagnostics["suggestion"] = (
                "AST search requires tree-sitter node types (not natural language). "
                "Common patterns: 'function_definition', 'class_definition', 'if_statement', "
                "'for_statement', 'try_statement', 'import_statement'"
            )
            diagnostics["example"] = (
                "pos_search_project(action='search_ast', query='function_definition', n_results=5)"
            )
        elif action == "find_callers":
            symbol = kwargs.get("query") or kwargs.get("symbol_name", "")
            diagnostics["suggestion"] = (
                f"No callers found for symbol '{symbol}'. This could mean: "
                "(1) Symbol is not called anywhere, (2) Symbol doesn't exist in the index, "
                "(3) Symbol name doesn't match exactly (case-sensitive)"
            )
        elif action == "find_dependencies":
            symbol = kwargs.get("query") or kwargs.get("symbol_name", "")
            diagnostics["suggestion"] = (
                f"No dependencies found for symbol '{symbol}'. This could mean: "
                "(1) Symbol doesn't call anything, (2) Symbol doesn't exist in the index, "
                "(3) Symbol name doesn't match exactly (case-sensitive)"
            )
        elif action == "find_call_paths":
            from_sym = kwargs.get("from_symbol", "")
            to_sym = kwargs.get("to_symbol", "")
            diagnostics["suggestion"] = (
                f"No call path found from '{from_sym}' to '{to_sym}'. This could mean: "
                "(1) No direct or indirect path exists, (2) One or both symbols don't exist, "
                "(3) Max depth limit reached (try increasing max_depth)"
            )
        elif action in ("search_code", "search_standards"):
            diagnostics["suggestion"] = (
                "No results found. Try: (1) Broader search terms, (2) Different keywords, "
                "(3) Check spelling and terminology"
            )
        
        return diagnostics
    
    def get_index(self, index_name: str) -> Optional[BaseIndex]:
        """Get index instance by name.
        
        Args:
            index_name: Name of the index ("standards", "code", "ast")
            
        Returns:
            BaseIndex instance or None if not available
        """
        return self._indexes.get(index_name)
    
    def health_check_all(self) -> Dict[str, HealthStatus]:
        """Run health checks on all indexes.
        
        Returns:
            Dictionary mapping index name to HealthStatus
        """
        health_statuses = {}
        
        for name, index in self._indexes.items():
            try:
                health_statuses[name] = index.health_check()
            except Exception as e:
                logger.error("Health check failed for %s: %s", name, e)
                health_statuses[name] = HealthStatus(
                    healthy=False,
                    message=f"Health check failed: {e}",
                    details={}
                )
        
        return health_statuses
    
    def ensure_all_indexes_healthy(self, auto_build: bool = True) -> Dict[str, Any]:
        """Ensure all indexes are healthy, auto-building/repairing if needed.
        
        This is the main orchestration method for startup index validation.
        
        Flow:
        1. Check for .rebuild_index flag file (if present, force rebuild)
        2. Run health checks on all indexes
        3. Categorize unhealthy indexes:
           - Secondary rebuild only (FTS/scalar indexes missing)
           - Full rebuild (table missing or empty)
        4. Rebuild secondary indexes first (faster)
        5. Rebuild full indexes
        6. Re-check health
        7. Return summary report
        
        Args:
            auto_build: If True, automatically rebuild unhealthy indexes
            
        Returns:
            Dictionary with:
            - all_healthy (bool): True if all indexes are now healthy
            - indexes_rebuilt (list): List of indexes that were rebuilt
            - indexes_failed (list): List of indexes that failed to rebuild
            - health_status (dict): Final health status for all indexes
        """
        logger.info("🔍 Checking health of all indexes...")
        
        # Step 0: Check for .rebuild_index flag file
        rebuild_flag_path = self.base_path / "standards" / ".rebuild_index"
        force_rebuild_all = False
        
        if rebuild_flag_path.exists():
            logger.info("📋 Found .rebuild_index flag - forcing full rebuild of all indexes")
            force_rebuild_all = True
            try:
                rebuild_flag_path.unlink()  # Delete flag after reading
                logger.info("✅ Removed .rebuild_index flag")
            except Exception as e:
                logger.warning("⚠️  Failed to remove .rebuild_index flag: %s", e)
        
        # Step 1: Initial health check
        health = self.health_check_all()
        
        # Log health status for all indexes
        for index_name, status in health.items():
            if status.healthy:
                logger.info("  ✅ %s: %s", index_name, status.message)
            else:
                logger.warning("  ⚠️  %s: %s", index_name, status.message)
        
        indexes_rebuilt = []
        indexes_failed = []
        
        # Step 2: Categorize unhealthy indexes
        indexes_secondary_only = []
        indexes_full_rebuild = []
        
        for index_name, status in health.items():
            if not status.healthy:
                
                # Check if only secondary indexes need rebuilding
                if status.details.get("needs_secondary_rebuild"):
                    indexes_secondary_only.append(index_name)
                else:
                    # Full rebuild needed
                    indexes_full_rebuild.append(index_name)
        
        # If force rebuild flag was present, rebuild all indexes
        if force_rebuild_all:
            logger.info("🔄 Force rebuild requested - rebuilding all indexes")
            indexes_full_rebuild = list(health.keys())  # Rebuild all indexes
            indexes_secondary_only = []  # Skip secondary-only rebuilds
        
        # If auto_build is disabled, just report status
        if not auto_build:
            return {
                "all_healthy": all(s.healthy for s in health.values()),
                "indexes_rebuilt": [],
                "indexes_failed": [],
                "health_status": {name: status.model_dump() for name, status in health.items()}
            }
        
        # Step 3: Rebuild secondary indexes first (faster, just FTS + scalar)
        if indexes_secondary_only:
            logger.info("🔧 Rebuilding secondary indexes for %d index(es)...", len(indexes_secondary_only))
            for index_name in indexes_secondary_only:
                try:
                    logger.info("  Rebuilding secondary indexes for %s...", index_name)
                    
                    index = self._indexes[index_name]
                    # Check if index has specialized secondary rebuild method
                    if hasattr(index, 'rebuild_secondary_indexes'):
                        index.rebuild_secondary_indexes()
                        logger.info("  ✅ Rebuilt secondary indexes for %s", index_name)
                    else:
                        # Fallback to full rebuild
                        logger.warning("  Secondary rebuild not available for %s, doing full rebuild", index_name)
                        self.rebuild_index(index_name)
                        logger.info("  ✅ Built %s index", index_name)
                    
                    indexes_rebuilt.append(index_name)
                    
                except Exception as e:
                    logger.error("  ❌ Failed to rebuild %s indexes: %s", index_name, e)
                    indexes_failed.append(index_name)
                    # Continue with other indexes
        
        # Step 4: Full rebuild for indexes that need it
        if indexes_full_rebuild:
            logger.info("🔨 Building %d missing/empty index(es)...", len(indexes_full_rebuild))
            for index_name in indexes_full_rebuild:
                try:
                    logger.info("  Building %s index (full rebuild)...", index_name)
                    self.rebuild_index(index_name, force=True)  # Force clean rebuild for unhealthy indexes
                    logger.info("  ✅ Built %s index", index_name)
                    indexes_rebuilt.append(index_name)
                    
                except Exception as e:
                    logger.error("  ❌ Failed to build %s index: %s", index_name, e)
                    indexes_failed.append(index_name)
                    # Continue with other indexes
        
        # Step 5: Re-check health
        if indexes_rebuilt:
            logger.info("🔍 Re-checking health after rebuilds...")
            health = self.health_check_all()
        
        # Step 6: Summary
        all_healthy = all(s.healthy for s in health.values())
        
        if all_healthy:
            logger.info("✅ All indexes healthy")
        elif indexes_failed:
            logger.warning("⚠️  Some indexes failed to rebuild: %s", indexes_failed)
        
        return {
            "all_healthy": all_healthy,
            "indexes_rebuilt": indexes_rebuilt,
            "indexes_failed": indexes_failed,
            "health_status": {name: status.model_dump() for name, status in health.items()}
        }
    
    def rebuild_index(self, index_name: str, force: bool = False) -> None:
        """Rebuild specified index from source.
        
        Args:
            index_name: Name of the index to rebuild
            force: If True, force rebuild even if index exists
            
        Raises:
            ActionableError: If index not found or rebuild fails
        """
        if index_name not in self._indexes:
            raise ActionableError(
                what_failed=f"rebuild_index({index_name})",
                why_failed=f"Index not found: {index_name}",
                how_to_fix=f"Available indexes: {', '.join(self._indexes.keys())}"
            )
        
        try:
            index = self._indexes[index_name]
            
            # Get source paths from config dynamically
            source_paths = []
            
            # Check if this index has a config with source_paths
            if hasattr(self.config, index_name):
                index_config = getattr(self.config, index_name)
                if index_config and hasattr(index_config, "source_paths"):
                    source_paths = [self.base_path / path for path in index_config.source_paths]
            
            # Handle nested/derived indexes that share source paths with code index
            if not source_paths:
                # Graph and AST indexes use code index source paths
                if index_name in ("graph", "ast") and hasattr(self.config, "code") and self.config.code:
                    if hasattr(self.config.code, "source_paths"):
                        source_paths = [self.base_path / path for path in self.config.code.source_paths]
                        logger.info("%s index using code source paths", index_name)
            
            logger.info("Rebuilding %s index from %d source paths", index_name, len(source_paths))
            index.build(source_paths, force=force)
            logger.info("✅ %s index rebuilt successfully", index_name)
            
        except Exception as e:
            logger.error("Failed to rebuild %s index: %s", index_name, e, exc_info=True)
            raise IndexError(
                what_failed=f"rebuild_index({index_name})",
                why_failed=str(e),
                how_to_fix="Check server logs for details. Ensure source paths are valid and dependencies installed."
            ) from e
    
    def update_from_watcher(self, index_name: str, changed_files: List[Path]) -> None:
        """Update index with changed files from FileWatcher.
        
        Args:
            index_name: Name of the index to update
            changed_files: List of files that changed
            
        Raises:
            ActionableError: If index not found or update fails
        """
        if index_name not in self._indexes:
            logger.warning("Ignoring update for unknown index: %s", index_name)
            return
        
        try:
            self._indexes[index_name].update(changed_files)
            logger.info("✅ Updated %s index with %d files", index_name, len(changed_files))
        except Exception as e:
            logger.error("Failed to update %s index: %s", index_name, e, exc_info=True)
            # Don't raise - file watcher should continue monitoring
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all indexes.
        
        Returns:
            Dictionary mapping index name to stats dictionary
        """
        stats = {}
        
        for name, index in self._indexes.items():
            try:
                stats[name] = index.get_stats()
            except Exception as e:
                logger.error("Failed to get stats for %s: %s", name, e)
                stats[name] = {"error": str(e)}
        
        return stats


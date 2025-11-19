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
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

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
        
        # Build state cache for performance optimization
        # Maps index_name -> BuildStatus with TTL-based invalidation
        self._build_state_cache: Dict[str, Any] = {}  # BuildStatus type imported later
        self._build_state_cache_time: Dict[str, float] = {}
        self._build_state_cache_lock = threading.RLock()
        
        # Cache TTL configuration
        self._build_state_cache_ttl: float = 60.0  # BUILT state (stable)
        self._building_state_cache_ttl: float = 5.0  # BUILDING state (dynamic, will be calculated)
        
        # Thread safety for _indexes dict
        self._indexes_lock = threading.RLock()
        
        # Telemetry callback (optional, disabled by default)
        self._telemetry_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
        
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
                
                # Inject corruption handler for auto-repair
                # This enables indexes to trigger automatic rebuilds when corruption is detected
                try:
                    index_instance.set_corruption_handler(
                        lambda error, idx_name=index_name: self._handle_corruption(idx_name, error)
                    )
                    logger.debug(f"Corruption handler injected for {index_name} index")
                except Exception as e:
                    # Don't fail initialization if handler injection fails
                    logger.warning(f"Failed to inject corruption handler for {index_name}: {e}")
                
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
    
    def _get_required_indexes_for_action(self, action: str) -> List[str]:
        """Get list of required indexes for an action.
        
        Maps actions to the indexes they require. Used for build readiness checks
        before executing actions. This ensures we don't attempt queries on indexes
        that aren't built yet.
        
        Args:
            action: The action to perform (e.g., "search_standards", "find_callers")
            
        Returns:
            List of index names required for this action (e.g., ["standards"], ["code"])
            
        Examples:
            >>> manager._get_required_indexes_for_action("search_standards")
            ["standards"]
            >>> manager._get_required_indexes_for_action("find_callers")
            ["code"]
            >>> manager._get_required_indexes_for_action("search_ast")
            ["code"]
        
        Note:
            This method uses the same ACTION_REGISTRY as route_action() to ensure
            consistency. If the action is not in the registry, returns empty list.
        """
        # Action registry: maps action pattern → (index_name, method_name, is_search)
        # This is the same registry used by route_action() for consistency
        ACTION_REGISTRY = {
            "search_standards": ("standards", "search", True),
            "search_code": ("code", "search", True),
            "search_ast": ("code", "search_ast", False),  # AST search via CodeIndex.search_ast()
            "find_callers": ("code", "find_callers", False),  # Graph via CodeIndex.find_callers()
            "find_dependencies": ("code", "find_dependencies", False),  # Graph via CodeIndex.find_dependencies()
            "find_call_paths": ("code", "find_call_paths", False),  # Graph via CodeIndex.find_call_paths()
        }
        
        if action not in ACTION_REGISTRY:
            return []
        
        index_name, _, _ = ACTION_REGISTRY[action]
        return [index_name]
    
    def _check_build_readiness(self, action: str) -> Optional[Dict[str, Any]]:
        """Check if required indexes for an action are built and ready.
        
        This method checks the build status of all indexes required for the action.
        If any required index is not BUILT, returns an error response with details.
        If all required indexes are BUILT, returns None (ready to proceed).
        
        Args:
            action: The action to perform (e.g., "search_standards", "find_callers")
            
        Returns:
            None if all required indexes are BUILT (ready to proceed)
            Dict with error response if any required index is not BUILT
            
        Examples:
            >>> # All indexes built
            >>> manager._check_build_readiness("search_standards")
            None
            
            >>> # Standards index not built
            >>> manager._check_build_readiness("search_standards")
            {
                "status": "error",
                "error": "Index not built",
                "message": "standards index is not built (state: NOT_BUILT)",
                "build_status": {...}
            }
        
        Note:
            This method uses build_status() from indexes, which delegates to
            dynamic_build_status() for fractal aggregation of component status.
        """
        from ouroboros.subsystems.rag.base import IndexBuildState
        
        # Get required indexes for this action
        required_indexes = self._get_required_indexes_for_action(action)
        
        if not required_indexes:
            # Unknown action or no indexes required
            return None
        
        # Check build status of each required index
        for index_name in required_indexes:
            # Check if index exists
            if index_name not in self._indexes:
                return {
                    "status": "error",
                    "error": "Index not available",
                    "message": f"{index_name} index is not available (not configured or failed to initialize)",
                    "how_to_fix": f"Ensure {index_name} index is configured in config/mcp.yaml and dependencies are installed",
                }
            
            # Get index build status
            index = self._indexes[index_name]
            build_status = index.build_status()
            
            # Check if index is BUILT
            if build_status.state != IndexBuildState.BUILT:
                return {
                    "status": "error",
                    "error": "Index not built",
                    "message": f"{index_name} index is not built (state: {build_status.state.value})",
                    "build_status": {
                        "state": build_status.state.value,
                        "message": build_status.message,
                        "progress_percent": build_status.progress_percent,
                        "details": build_status.details,
                    },
                    "how_to_fix": f"Build the {index_name} index first using the build action or ensure_all_indexes_healthy()",
                }
        
        # All required indexes are BUILT
        return None
    
    def _format_building_response(self, index_name: str, build_status: Any) -> Dict[str, Any]:
        """Format a response when an index is currently building.
        
        Provides informative feedback to the user about build progress,
        including progress percentage, estimated time, and suggestions.
        
        Args:
            index_name: Name of the index that's building
            build_status: BuildStatus object from the index
            
        Returns:
            Dict with status, message, and build progress information
            
        Example:
            >>> status = BuildStatus(
            ...     state=IndexBuildState.BUILDING,
            ...     message="Building vector index",
            ...     progress_percent=45.5,
            ...     details={"chunks_processed": 1000}
            ... )
            >>> manager._format_building_response("standards", status)
            {
                "status": "building",
                "message": "standards index is currently building (45.5% complete)",
                "build_status": {
                    "state": "building",
                    "message": "Building vector index",
                    "progress_percent": 45.5,
                    "details": {"chunks_processed": 1000}
                },
                "suggestion": "Wait for build to complete or try again in a few moments"
            }
        """
        return {
            "status": "building",
            "message": f"{index_name} index is currently building ({build_status.progress_percent:.1f}% complete)",
            "build_status": {
                "state": build_status.state.value,
                "message": build_status.message,
                "progress_percent": build_status.progress_percent,
                "details": build_status.details,
            },
            "suggestion": "Wait for build to complete or try again in a few moments",
        }
    
    def _format_failed_response(self, index_name: str, build_status: Any) -> Dict[str, Any]:
        """Format a response when an index build has failed.
        
        Provides detailed error information and remediation guidance to help
        the user recover from build failures.
        
        Args:
            index_name: Name of the index that failed to build
            build_status: BuildStatus object from the index
            
        Returns:
            Dict with status, error message, and remediation guidance
            
        Example:
            >>> status = BuildStatus(
            ...     state=IndexBuildState.FAILED,
            ...     message="Build failed: Disk space exhausted",
            ...     progress_percent=0.0,
            ...     error="No space left on device",
            ...     details={"error_type": "OSError"}
            ... )
            >>> manager._format_failed_response("standards", status)
            {
                "status": "error",
                "error": "Index build failed",
                "message": "standards index build failed: Disk space exhausted",
                "build_status": {
                    "state": "failed",
                    "message": "Build failed: Disk space exhausted",
                    "progress_percent": 0.0,
                    "error": "No space left on device",
                    "details": {"error_type": "OSError"}
                },
                "how_to_fix": "Check server logs for details. Try rebuilding with force=True..."
            }
        """
        return {
            "status": "error",
            "error": "Index build failed",
            "message": f"{index_name} index build failed: {build_status.message}",
            "build_status": {
                "state": build_status.state.value,
                "message": build_status.message,
                "progress_percent": build_status.progress_percent,
                "error": build_status.error,
                "details": build_status.details,
            },
            "how_to_fix": (
                f"Check server logs for details. Try rebuilding the {index_name} index with force=True. "
                f"If the error persists, check disk space, permissions, and dependencies."
            ),
        }
    
    def _attach_build_metadata(self, response: Dict[str, Any], index_name: str) -> Dict[str, Any]:
        """Attach build status metadata to a successful response.
        
        Adds optional build status information to the response for observability.
        This helps users understand the state of the index that served their query,
        which can be useful for debugging or monitoring.
        
        Args:
            response: The response dict to augment
            index_name: Name of the index that served the query
            
        Returns:
            Response dict with added "_build_metadata" field
            
        Example:
            >>> response = {"status": "success", "results": [...], "count": 5}
            >>> manager._attach_build_metadata(response, "standards")
            {
                "status": "success",
                "results": [...],
                "count": 5,
                "_build_metadata": {
                    "index": "standards",
                    "state": "built",
                    "progress_percent": 100.0
                }
            }
        
        Note:
            The "_build_metadata" field is prefixed with underscore to indicate
            it's optional metadata, not core response data.
        """
        try:
            index = self._indexes.get(index_name)
            if index:
                build_status = index.build_status()
                response["_build_metadata"] = {
                    "index": index_name,
                    "state": build_status.state.value,
                    "progress_percent": build_status.progress_percent,
                }
        except Exception as e:
            # Don't fail the response if metadata attachment fails
            logger.warning(f"Failed to attach build metadata for {index_name}: {e}")
        
        return response
    
    def _handle_corruption(self, index_name: str, error: Exception) -> None:
        """Handle corruption detection from an index (callback pattern).
        
        This method is called by indexes when they detect corruption during operations.
        It triggers auto-repair by scheduling a background rebuild and emits telemetry.
        
        Args:
            index_name: Name of the corrupted index
            error: The exception that indicates corruption
            
        Example:
            >>> # Index detects corruption and calls this handler
            >>> manager._handle_corruption("standards", CorruptionError("Table missing"))
            # Logs error, invalidates cache, schedules rebuild
        
        Note:
            This is a callback method set via set_corruption_handler() on indexes.
            It's designed to be non-blocking - rebuild happens in background thread.
        """
        logger.error(
            f"Corruption detected in {index_name} index: {type(error).__name__}: {error}",
            exc_info=True
        )
        
        # Emit telemetry for corruption detection
        from datetime import datetime, timezone
        self._emit_telemetry("corruption_detected", {
            "index_name": index_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
        })
        
        # Invalidate build cache for this index
        self._invalidate_build_cache(index_name)
        
        # Trigger background rebuild
        # Note: This uses threading to avoid blocking the current operation
        import threading
        rebuild_thread = threading.Thread(
            target=self._rebuild_index_background,
            args=(index_name,),
            name=f"rebuild-{index_name}",
            daemon=True  # Don't prevent shutdown
        )
        rebuild_thread.start()
        
        # Emit telemetry for auto-repair trigger
        self._emit_telemetry("auto_repair_triggered", {
            "index_name": index_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger_reason": "corruption_detected",
        })
        
        logger.info(f"Auto-repair triggered for {index_name} index (background rebuild started)")
    
    def _rebuild_index_background(self, index_name: str) -> None:
        """Rebuild an index in the background (called from corruption handler).
        
        This method runs in a separate thread to avoid blocking the main operation.
        It performs a full rebuild with force=True to clear corruption.
        
        Args:
            index_name: Name of the index to rebuild
            
        Note:
            This method includes error handling to prevent thread crashes.
            Failures are logged but don't propagate to the main thread.
        """
        try:
            logger.info(f"Background rebuild starting for {index_name} index")
            self.rebuild_index(index_name, force=True)
            logger.info(f"Background rebuild completed successfully for {index_name} index")
            
            # Emit telemetry for successful auto-repair
            from datetime import datetime, timezone
            self._emit_telemetry("auto_repair_completed", {
                "index_name": index_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": True,
            })
        except Exception as e:
            logger.error(
                f"Background rebuild failed for {index_name} index: {type(e).__name__}: {e}",
                exc_info=True
            )
            
            # Emit telemetry for failed auto-repair
            from datetime import datetime, timezone
            self._emit_telemetry("auto_repair_completed", {
                "index_name": index_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error_type": type(e).__name__,
                "error_message": str(e),
            })
    
    def set_telemetry_callback(
        self,
        callback: Optional[Callable[[str, Dict[str, Any]], None]]
    ) -> None:
        """Set telemetry callback for event emission (optional).
        
        Telemetry is disabled by default. When enabled, this callback is invoked
        for key events like build progress, corruption detection, and auto-repair.
        
        The callback should be non-blocking and handle errors gracefully, as
        telemetry failures will not propagate (logged only).
        
        Args:
            callback: Function to call on telemetry events.
                     Signature: (event_type: str, event_data: Dict[str, Any]) -> None
                     If None, disables telemetry.
        
        Event Types:
            - "build_started": Index build initiated
            - "build_progress": Build progress update
            - "build_completed": Build finished successfully
            - "build_failed": Build failed
            - "corruption_detected": Corruption detected during operation
            - "auto_repair_triggered": Auto-repair initiated
            - "auto_repair_completed": Auto-repair finished
        
        Event Data (common fields):
            - "index_name": Name of the index (str)
            - "timestamp": ISO 8601 timestamp (str)
            - Additional fields vary by event type
        
        Example:
            >>> def my_telemetry_handler(event_type: str, event_data: Dict[str, Any]):
            ...     print(f"Event: {event_type}, Data: {event_data}")
            >>> 
            >>> manager.set_telemetry_callback(my_telemetry_handler)
            >>> # Now telemetry events will be emitted
            >>> 
            >>> manager.set_telemetry_callback(None)
            >>> # Telemetry disabled
        
        Note:
            Telemetry is controlled by config.build.telemetry_enabled.
            Even with a callback set, events are only emitted if enabled in config.
        """
        self._telemetry_callback = callback
        if callback:
            logger.info("Telemetry callback registered")
        else:
            logger.info("Telemetry callback disabled")
    
    def _emit_telemetry(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Emit telemetry event (internal helper).
        
        Calls the telemetry callback if set and enabled in config.
        Catches and logs errors to prevent telemetry failures from affecting
        core functionality.
        
        Args:
            event_type: Type of event (e.g., "build_started", "corruption_detected")
            event_data: Event-specific data dictionary
        
        Example:
            >>> self._emit_telemetry("build_started", {
            ...     "index_name": "standards",
            ...     "timestamp": datetime.now(timezone.utc).isoformat(),
            ...     "source_paths": ["standards/"],
            ... })
        
        Note:
            This method is defensive - telemetry failures are logged but never
            propagate to the caller. Telemetry is optional and should never
            break core functionality.
        """
        # Check if telemetry is enabled in config
        if not self.config.build.telemetry_enabled:
            return
        
        # Check if callback is set
        if not self._telemetry_callback:
            return
        
        try:
            # Call the callback
            self._telemetry_callback(event_type, event_data)
        except Exception as e:
            # Log error but don't propagate - telemetry is optional
            logger.error(
                f"Telemetry callback failed for event '{event_type}': {type(e).__name__}: {e}",
                exc_info=False  # Don't clutter logs with stack traces
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
        
        # Check build readiness (resilient index building)
        build_error = self._check_build_readiness(action)
        if build_error:
            return build_error
        
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
                
                # Attach build metadata for observability
                response = self._attach_build_metadata(response, index_name)
                
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
                
                # Attach build metadata for observability
                response = self._attach_build_metadata(response, index_name)
                
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
    
    # ========================================================================
    # Build State Cache Methods (Performance Foundation - Phase 0)
    # ========================================================================
    
    def _calculate_building_ttl(self, progress_percent: float) -> float:
        """Calculate dynamic TTL for BUILDING state based on progress.
        
        The TTL adapts to build progress to balance freshness and performance:
        - Early stage (0-10%): 2s TTL - Fast changes, check frequently
        - Mid stage (10-50%): 5s TTL - Steady progress, moderate checks
        - Late stage (50-100%): 10s TTL - Slow near completion, less frequent checks
        
        Args:
            progress_percent: Build progress percentage (0-100)
            
        Returns:
            TTL in seconds (2.0, 5.0, or 10.0)
            
        Examples:
            >>> manager._calculate_building_ttl(5.0)
            2.0
            >>> manager._calculate_building_ttl(30.0)
            5.0
            >>> manager._calculate_building_ttl(75.0)
            10.0
        """
        if progress_percent < 10:
            return 2.0
        elif progress_percent < 50:
            return 5.0
        else:
            return 10.0
    
    def _invalidate_build_cache(self, index_name: str) -> None:
        """Atomically invalidate build state cache for an index.
        
        This method is thread-safe and removes both the cached status and timestamp
        for the specified index. Used when build state changes (e.g., build starts,
        completes, or fails).
        
        Args:
            index_name: Name of the index to invalidate
            
        Thread Safety:
            Uses RLock to ensure atomic removal from both cache dictionaries.
            Safe to call from multiple threads simultaneously.
            
        Examples:
            >>> manager._invalidate_build_cache("standards")
            # Cache entry removed atomically
        """
        with self._build_state_cache_lock:
            self._build_state_cache.pop(index_name, None)
            self._build_state_cache_time.pop(index_name, None)
    
    def _iter_indexes(self) -> List[tuple[str, BaseIndex]]:
        """Safely iterate over indexes with thread safety.
        
        Returns a snapshot of the indexes dictionary to prevent concurrent
        modification errors during iteration. Use this instead of directly
        iterating over self._indexes.items().
        
        Returns:
            List of (index_name, index_instance) tuples
            
        Thread Safety:
            Creates a snapshot under lock, preventing concurrent modification
            errors if indexes are added/removed during iteration.
            
        Examples:
            >>> for name, index in manager._iter_indexes():
            ...     print(f"Index: {name}")
        """
        with self._indexes_lock:
            return list(self._indexes.items())


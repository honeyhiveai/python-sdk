"""
Ouroboros Server: FastMCP server initialization and lifecycle management.

This module creates and configures the complete MCP server with all subsystems:
1. Load config (Pydantic v2 validation)
2. Initialize Foundation layer (StateManager)
3. Initialize Subsystems (RAG, Workflow, Browser)
4. Initialize Middleware (query_tracker, session_mapper)
5. Register Tools (via ToolRegistry auto-discovery)
6. Return FastMCP server

Architecture:
    create_server()
        ↓
    FastMCP("praxis-os")
        ↓
    Initialize Subsystems
        ↓
    Initialize Middleware
        ↓
    ToolRegistry.register_all()
        ↓
    Return configured server

Traceability:
    FR-010: Tool Auto-Discovery
    NFR-U2: Fail-fast validation at startup
    NFR-P1: Cold start <30s
"""

import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ouroboros.config.schemas.mcp import MCPConfig
from ouroboros.tools.registry import ToolRegistry
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


def create_server(base_path: Path, transport_mode: str = "stdio") -> FastMCP:
    """
    Create and configure complete MCP server.
    
    Initializes all subsystems, middleware, and tools in the correct order:
    1. Load and validate config
    2. Create FastMCP server instance
    3. Initialize Foundation layer (StateManager)
    4. Initialize Subsystems (RAG, Workflow, Browser)
    5. Initialize Middleware (query_tracker, session_mapper)
    6. Auto-discover and register tools (via ToolRegistry)
    
    Args:
        base_path: Path to .praxis-os directory
        transport_mode: Transport mode (dual, stdio, http)
        
    Returns:
        FastMCP: Configured server ready to run
        
    Raises:
        ActionableError: If initialization fails with remediation guidance
        
    Example:
        >>> from pathlib import Path
        >>> from ouroboros.server import create_server
        >>> 
        >>> base_path = Path(".praxis-os")
        >>> mcp = create_server(base_path, transport_mode="dual")
        >>> mcp.run()  # Start server
    
    Cold Start Target: <30s
    """
    logger.info("=" * 60)
    logger.info("Initializing Ouroboros MCP Server")
    logger.info("Base path: %s", base_path)
    logger.info("=" * 60)
    
    # ========================================================================
    # 1. Load and Validate Configuration
    # ========================================================================
    logger.info("Loading configuration...")
    
    config_path = base_path / "config" / "mcp.yaml"
    
    try:
        config = MCPConfig.from_yaml(config_path)
        logger.info("✅ Configuration loaded and validated")
    except FileNotFoundError as e:
        raise ActionableError(
            what_failed="Configuration loading",
            why_failed=f"Config file not found: {config_path}",
            how_to_fix=(
                f"Create config file at {config_path}\n"
                "Reference: See documentation for config structure"
            )
        ) from e
    except Exception as e:
        raise ActionableError(
            what_failed="Configuration validation",
            why_failed=str(e),
            how_to_fix=(
                f"Fix configuration errors in {config_path}\n"
                "Check field names, types, and required values"
            )
        ) from e
    
    # Validate paths exist
    path_errors = config.validate_paths()
    if path_errors:
        error_msg = "\n".join(path_errors)
        raise ActionableError(
            what_failed="Configuration path validation",
            why_failed=f"Invalid paths in configuration:\n{error_msg}",
            how_to_fix="Create missing directories or update config paths"
        )
    
    # ========================================================================
    # 2. Create FastMCP Server Instance
    # ========================================================================
    logger.info("Creating FastMCP server instance...")
    
    mcp = FastMCP(
        "praxis-os",
        instructions=(
            "You are an AI assistant with access to the prAxIs OS MCP server. "
            "This server provides tools for searching project knowledge, "
            "managing workflows, browser automation, and file operations."
        )
    )
    
    logger.info("✅ FastMCP server created")
    
    # ========================================================================
    # 3. Initialize Foundation Layer
    # ========================================================================
    logger.info("Initializing Foundation layer...")
    
    # 3a. Initialize SessionMapper (generic state persistence)
    try:
        from ouroboros.foundation.session_mapper import SessionMapper
        
        state_dir = base_path / "state"  # New unified state directory
        state_dir.mkdir(parents=True, exist_ok=True)
        
        session_mapper = SessionMapper(state_dir=state_dir)
        logger.info("✅ SessionMapper initialized", extra={"state_dir": str(state_dir)})
    except Exception as e:
        raise ActionableError(
            what_failed="SessionMapper initialization",
            why_failed=str(e),
            how_to_fix="Check state directory permissions and disk space"
        ) from e
    
    # ========================================================================
    # 4. Initialize Subsystems
    # ========================================================================
    
    # 4a. RAG Subsystem (IndexManager)
    logger.info("Initializing RAG subsystem...")
    
    index_manager: Optional[Any] = None
    try:
        from ouroboros.subsystems.rag.index_manager import IndexManager
        
        index_manager = IndexManager(
            config=config.indexes,
            base_path=base_path
        )
        logger.info("✅ IndexManager initialized with %d indexes", 
                   len(index_manager._indexes))
        
        # Check health status (fast, non-blocking)
        # Note: We do NOT auto-build during init to avoid blocking stdio transport
        # Background thread will build indexes after server starts (Option 2: Eventually Consistent)
        result = index_manager.ensure_all_indexes_healthy(auto_build=False)
        
        # Log summary (just health check, not rebuild)
        if result["all_healthy"]:
            logger.info("✅ All indexes healthy and operational")
        else:
            unhealthy = [name for name in result.get("index_status", {}).keys() 
                        if not result["index_status"][name].get("healthy", False)]
            logger.info("⏳ Some indexes need building: %s (will build in background)", 
                       ", ".join(unhealthy))
        
    except Exception as e:
        logger.warning("⚠️  IndexManager initialization failed: %s", e)
        logger.warning("    RAG tools will not be available")
        index_manager = None
    
    # 4a.1. Background Index Building (Eventually Consistent)
    # Start background thread to build unhealthy indexes after server init completes.
    # This ensures server is responsive immediately while indexes converge to healthy state.
    if index_manager and not result["all_healthy"]:
        def _build_indexes_background():
            """Background thread to build indexes after server starts.
            
            This function runs in a daemon thread and will not block server shutdown.
            It builds all unhealthy indexes to ensure eventually consistent state.
            
            Design:
            - Daemon thread (dies with main process)
            - No inter-thread communication needed (fire-and-forget)
            - Logs progress for observability
            - Graceful error handling (won't crash server)
            """
            try:
                logger.info("🔄 Starting background index building thread...")
                
                # Build all unhealthy indexes (auto_build=True, incremental=True)
                build_result = index_manager.ensure_all_indexes_healthy(auto_build=True)
                
                if build_result["all_healthy"]:
                    logger.info("✅ Background index building complete - all indexes healthy")
                else:
                    failed = build_result.get("indexes_failed", [])
                    if failed:
                        logger.warning(
                            "⚠️  Background index building completed with failures: %s",
                            ", ".join(failed)
                        )
                    else:
                        logger.info("✅ Background index building complete")
                        
            except Exception as e:
                logger.error("❌ Background index building failed: %s", e, exc_info=True)
                logger.error("   Indexes will remain unhealthy until manual rebuild or server restart")
        
        # Start daemon thread (non-blocking, will die with main process)
        build_thread = threading.Thread(
            target=_build_indexes_background,
            name="index-builder",
            daemon=True
        )
        build_thread.start()
        logger.info("📋 Background index building scheduled (non-blocking)")
    
    # 4b. File Watcher (incremental index updates)
    logger.info("Initializing FileWatcher...")
    
    file_watcher: Optional[Any] = None
    try:
        from ouroboros.subsystems.rag.watcher import FileWatcher
        
        if index_manager and config.indexes.file_watcher.enabled:
            # Define path-to-index mappings
            # Map which paths trigger which index updates
            path_mappings = {
                str(base_path / "standards"): ["standards"],  # .praxis-os/standards/ → standards index
            }
            
            # Add code paths from code config
            for source_path in config.indexes.code.source_paths:
                path_mappings[source_path] = ["code", "ast", "graph"]
            
            file_watcher = FileWatcher(
                config=config.indexes.file_watcher,
                index_manager=index_manager,
                path_mappings=path_mappings
            )
            file_watcher.start()
            logger.info("✅ FileWatcher started (hot reload enabled)")
        else:
            if not index_manager:
                logger.info("⚠️  FileWatcher skipped (IndexManager not available)")
            else:
                logger.info("⚠️  FileWatcher disabled in config")
    except Exception as e:
        logger.warning("⚠️  FileWatcher initialization failed: %s", e)
        logger.warning("    Index auto-updates will not be available")
        file_watcher = None
    
    # 4c. Workflow Subsystem (WorkflowEngine)
    logger.info("Initializing Workflow subsystem...")
    
    workflow_engine: Optional[Any] = None
    try:
        from ouroboros.subsystems.workflow.engine import WorkflowEngine
        
        workflow_engine = WorkflowEngine(
            config=config.workflow,
            base_path=base_path,
            session_mapper=session_mapper
        )
        logger.info("✅ WorkflowEngine initialized")
    except Exception as e:
        logger.warning("⚠️  WorkflowEngine initialization failed: %s", e)
        logger.warning("    Workflow tools will not be available")
        workflow_engine = None
    
    # 4d. Browser Subsystem (BrowserManager)
    logger.info("Initializing Browser subsystem...")
    
    browser_manager: Optional[Any] = None
    try:
        from ouroboros.subsystems.browser.manager import BrowserManager

        browser_manager = BrowserManager(
            config=config.browser,
            session_mapper=session_mapper
        )
        logger.info("✅ BrowserManager initialized")
    except Exception as e:
        logger.warning("⚠️  BrowserManager initialization failed: %s", e)
        logger.warning("    Browser tools will not be available")
        browser_manager = None
    
    # ========================================================================
    # 5. Initialize Middleware
    # ========================================================================
    logger.info("Initializing Middleware layer...")
    
    # 5a. QueryTracker (for behavioral metrics)
    query_tracker: Optional[Any] = None
    try:
        from ouroboros.middleware.query_tracker import QueryTracker
        query_tracker = QueryTracker()
        logger.info("✅ QueryTracker initialized (behavioral metrics enabled)")
    except Exception as e:
        logger.warning("⚠️  QueryTracker initialization failed: %s", e)
        # Non-critical, server can function without metrics
    
    # SessionMapper already initialized in Foundation layer (line 148)
    
    # ========================================================================
    # 6. Register Tools via ToolRegistry (Auto-Discovery)
    # ========================================================================
    logger.info("Registering tools via ToolRegistry...")
    
    tools_dir = Path(__file__).parent / "tools"
    
    # Initialize results with safe defaults (P0 fix: prevents crash if registration fails)
    results = {"tools_discovered": 0, "tools_registered": 0, "tools_failed": 0, "details": []}
    
    try:
        registry = ToolRegistry(
            tools_dir=tools_dir,
            mcp_server=mcp,
            dependencies={
                "index_manager": index_manager,
                "workflow_engine": workflow_engine,
                "browser_manager": browser_manager,
                "session_mapper": session_mapper,
                "query_tracker": query_tracker,
                "workspace_root": base_path.parent,  # for pos_filesystem
            }
        )
        
        results = registry.register_all()
        
        logger.info("=" * 60)
        logger.info("Tool Registration Summary:")
        logger.info("  Tools discovered: %d", results["tools_discovered"])
        logger.info("  Tools registered: %d", results["tools_registered"])
        logger.info("  Tools failed: %d", results["tools_failed"])
        logger.info("=" * 60)
        
        tools_failed = results.get("tools_failed", 0)
        if isinstance(tools_failed, (int, str)):
            failed_count = int(tools_failed) if isinstance(tools_failed, str) else tools_failed
            if failed_count > 0:
                logger.warning("⚠️  Some tools failed to register. Check logs above.")
        
        # Log details
        details: Any = results.get("details", [])
        if isinstance(details, list):
            for detail in details:
                if detail.get("status") == "success":
                    logger.info("  ✅ %s (%d tool(s))", 
                               detail.get("function"), detail.get("count"))
                else:
                    logger.warning("  ❌ %s (failed)", detail.get("function"))
        
    except Exception as e:
        raise ActionableError(
            what_failed="Tool registration",
            why_failed=str(e),
            how_to_fix=(
                "Check that tools/ directory exists and contains valid tool modules. "
                "See logs for detailed error information."
            )
        ) from e
    
    # ========================================================================
    # 7. Prepare Background Tasks (lazy start via middleware)
    # ========================================================================
    import asyncio
    
    # Define index building task coroutine
    async def index_building_task():
        """Background task for building/rebuilding indexes.
        
        Runs synchronous index building in a thread pool to avoid blocking
        the event loop. This allows the MCP server to respond to requests
        while indexes are being built.
        """
        logger.info("✅ Background index building task started")
        
        try:
            if index_manager:
                # Build indexes in background thread (non-blocking for event loop)
                logger.info("🔨 Building indexes in background thread...")
                
                # Run sync method in thread pool using asyncio.to_thread()
                # This keeps the event loop responsive during long-running builds
                result = await asyncio.to_thread(
                    index_manager.ensure_all_indexes_healthy,
                    auto_build=True
                )
                
                # Log summary with detailed statistics
                if result["indexes_rebuilt"]:
                    logger.info("📊 Rebuilt %d index(es): %s", 
                              len(result["indexes_rebuilt"]), 
                              ", ".join(result["indexes_rebuilt"]))
                    
                    # Log detailed stats for each rebuilt index
                    health_status = result.get("health_status", {})
                    for index_name in result["indexes_rebuilt"]:
                        # Get stats directly from the index
                        try:
                            index = index_manager.get_index(index_name)
                            stats = index.get_stats() if index else {}
                            stats_msg = []
                            
                            # Code index stats (multi-partition)
                            if "partition_count" in stats:
                                stats_msg.append(f"{stats['partition_count']} partitions")
                            if "chunk_count" in stats:
                                stats_msg.append(f"{stats['chunk_count']} chunks")
                            if "ast_node_count" in stats:
                                stats_msg.append(f"{stats['ast_node_count']} AST nodes")
                            if "symbol_count" in stats:
                                stats_msg.append(f"{stats['symbol_count']} symbols")
                            if "relationship_count" in stats:
                                stats_msg.append(f"{stats['relationship_count']} relationships")
                            
                            # Standards index stats (no partition_count)
                            if "chunk_count" in stats and "partition_count" not in stats:
                                stats_msg.append(f"{stats['chunk_count']} chunks")
                            
                            stats_str = ", ".join(stats_msg) if stats_msg else "no detailed stats"
                        except Exception as e:
                            stats_str = f"stats unavailable ({e})"
                        
                        # Get health status
                        final_health = health_status.get(index_name, {})
                        is_healthy = final_health.get("healthy", False)
                        health_msg = final_health.get("message", "Unknown status")
                        
                        logger.info(
                            "  ✅ %s: %s | Health: %s (%s)",
                            index_name,
                            stats_str,
                            "HEALTHY" if is_healthy else "UNHEALTHY",
                            health_msg
                        )
                        
                        # If multi-partition code index, show per-partition breakdown
                        if index_name == "code" and stats.get("mode") == "multi-partition":
                            # Get the actual index to query partition stats
                            code_index = index_manager._indexes.get("code")
                            if code_index and hasattr(code_index, '_partitions'):
                                for partition_name, partition in code_index._partitions.items():
                                    try:
                                        p_chunks = partition.semantic.get_stats().get("chunk_count", 0) if partition.semantic else 0
                                        p_ast = partition.graph.get_stats().get("ast_node_count", 0) if partition.graph else 0
                                        p_symbols = partition.graph.get_stats().get("symbol_count", 0) if partition.graph else 0
                                        p_rels = partition.graph.get_stats().get("relationship_count", 0) if partition.graph else 0
                                        
                                        logger.info(
                                            "    ├─ %s: %d chunks, %d AST nodes, %d symbols, %d relationships",
                                            partition_name,
                                            p_chunks,
                                            p_ast,
                                            p_symbols,
                                            p_rels
                                        )
                                    except Exception as pe:
                                        logger.warning("    ├─ %s: stats unavailable (%s)", partition_name, pe)
                
                if result["indexes_failed"]:
                    logger.warning("⚠️  Failed to rebuild %d index(es): %s", 
                                  len(result["indexes_failed"]), 
                                  ", ".join(result["indexes_failed"]))
                
                if result["all_healthy"]:
                    logger.info("✅ All indexes built and healthy")
        except Exception as e:
            logger.error("❌ Index building task failed: %s", e, exc_info=True)
    
    # Define cleanup task coroutine
    async def cleanup_task():
        """Background task for automatic session cleanup."""
        logger.info("✅ Background cleanup task started")
        
        while True:
            try:
                # Browser sessions: Cleanup idle ACTIVE sessions (30 min timeout)
                # Browser sessions are short-lived (minutes to hours)
                # If idle for 30+ minutes, likely abandoned → move to error
                browser_cleaned = session_mapper.cleanup_by_timeout("browser", idle_timeout_minutes=30)
                if browser_cleaned > 0:
                    logger.info("Cleaned up %d idle browser sessions", browser_cleaned)
                
                # Workflow sessions: DO NOT cleanup active sessions!
                # Workflows are long-lived (days/weeks) and must survive server restarts
                # Active workflows can wait indefinitely for human approval/review
                # Only cleanup COMPLETED and ERROR workflows by age
                
                # Cleanup old COMPLETED sessions (30 days)
                workflow_completed = session_mapper.cleanup_by_age("workflow", "completed", older_than_days=30)
                browser_completed = session_mapper.cleanup_by_age("browser", "completed", older_than_days=30)
                if workflow_completed > 0 or browser_completed > 0:
                    logger.info("Cleaned up %d old completed sessions", workflow_completed + browser_completed)
                
                # Cleanup old ERROR sessions (7 days)
                workflow_errors = session_mapper.cleanup_by_age("workflow", "error", older_than_days=7)
                browser_errors = session_mapper.cleanup_by_age("browser", "error", older_than_days=7)
                if workflow_errors > 0 or browser_errors > 0:
                    logger.info("Cleaned up %d old error sessions", workflow_errors + browser_errors)
                
                # Wait 1 hour before next cleanup
                await asyncio.sleep(3600)
                    
            except Exception as e:
                logger.error("Error in cleanup task: %s", e, exc_info=True)
                # Wait before retrying on error
                await asyncio.sleep(60)
    
    # Define periodic health check poller coroutine
    async def health_check_poller():
        """Background task for periodic index health monitoring.
        
        Prevents index corruption from going undetected by periodically checking
        index health and triggering rebuilds if corruption is detected.
        
        Features:
        - Grace period on startup (5 min) - no rebuilds during this time
        - Periodic polling (every 1 min) to detect corruption
        - Backoff/cooldown (2 min) to prevent cascading rebuilds
        - Auto-rebuild on corruption detection (after grace period)
        """
        logger.info("✅ Background health check poller started")
        
        # Track server startup time for grace period
        import time
        startup_time = time.time()
        rebuild_grace_period_seconds = 5 * 60  # 5 minutes - no rebuilds during this time
        logger.info("⏳ Health check poller: %d second grace period for rebuilds after startup", rebuild_grace_period_seconds)
        
        # Cooldown tracking: Prevent rebuilding the same index too frequently
        last_rebuild_time: Dict[str, float] = {}  # index_name -> timestamp
        rebuild_cooldown_seconds = 2 * 60  # 2 minutes minimum between rebuilds
        
        while True:
            try:
                if index_manager:
                    logger.info("🏥 Periodic health check: Checking all indexes...")
                    
                    # Run health check in background thread (non-blocking)
                    health_status = await asyncio.to_thread(
                        index_manager.health_check_all
                    )
                    
                    # Check each index
                    current_time = time.time()
                    time_since_startup = current_time - startup_time
                    in_grace_period = time_since_startup < rebuild_grace_period_seconds
                    
                    for index_name, health in health_status.items():
                        is_healthy = health.healthy
                        
                        if not is_healthy:
                            logger.warning("⚠️  Index '%s' is unhealthy: %s", 
                                         index_name, 
                                         health.message)
                            
                            # Check startup grace period: Don't rebuild during initial startup
                            if in_grace_period:
                                remaining = int(rebuild_grace_period_seconds - time_since_startup)
                                logger.info("⏸️  Index '%s' unhealthy but in startup grace period (%d seconds remaining)", 
                                          index_name, remaining)
                                continue
                            
                            # Check cooldown: Has it been long enough since last rebuild?
                            last_rebuild = last_rebuild_time.get(index_name, 0)
                            time_since_rebuild = current_time - last_rebuild
                            
                            if time_since_rebuild < rebuild_cooldown_seconds:
                                remaining = int(rebuild_cooldown_seconds - time_since_rebuild)
                                logger.info("⏸️  Index '%s' rebuild on cooldown (%d seconds remaining)", 
                                          index_name, remaining)
                                continue
                            
                            # Trigger rebuild (in background thread)
                            logger.info("🔨 Triggering rebuild for unhealthy index '%s'...", index_name)
                            try:
                                result = await asyncio.to_thread(
                                    index_manager.ensure_all_indexes_healthy,
                                    auto_build=True
                                )
                                
                                if index_name in result.get("indexes_rebuilt", []):
                                    # Get stats directly from the index
                                    try:
                                        index = index_manager.get_index(index_name)
                                        stats = index.get_stats() if index else {}
                                        stats_msg = []
                                        
                                        # Code index stats (multi-partition)
                                        if "partition_count" in stats:
                                            stats_msg.append(f"{stats['partition_count']} partitions")
                                        if "chunk_count" in stats:
                                            stats_msg.append(f"{stats['chunk_count']} chunks")
                                        if "ast_node_count" in stats:
                                            stats_msg.append(f"{stats['ast_node_count']} AST nodes")
                                        if "symbol_count" in stats:
                                            stats_msg.append(f"{stats['symbol_count']} symbols")
                                        if "relationship_count" in stats:
                                            stats_msg.append(f"{stats['relationship_count']} relationships")
                                        
                                        # Standards index stats (no partition_count)
                                        if "chunk_count" in stats and "partition_count" not in stats:
                                            stats_msg.append(f"{stats['chunk_count']} chunks")
                                        
                                        stats_str = ", ".join(stats_msg) if stats_msg else "no detailed stats"
                                    except Exception as e:
                                        stats_str = f"stats unavailable ({e})"
                                    
                                    # Get health status
                                    final_health = result.get("health_status", {}).get(index_name, {})
                                    is_healthy = final_health.get("healthy", False)
                                    health_msg = final_health.get("message", "Unknown status")
                                    
                                    logger.info(
                                        "✅ Successfully rebuilt index '%s': %s | Health: %s (%s)",
                                        index_name,
                                        stats_str,
                                        "HEALTHY" if is_healthy else "UNHEALTHY",
                                        health_msg
                                    )
                                    
                                    # If multi-partition code index, show per-partition breakdown
                                    if index_name == "code" and stats.get("mode") == "multi-partition":
                                        # Get the actual index to query partition stats
                                        code_index = index_manager._indexes.get("code")
                                        if code_index and hasattr(code_index, '_partitions'):
                                            for partition_name, partition in code_index._partitions.items():
                                                try:
                                                    p_chunks = partition.semantic.get_stats().get("chunk_count", 0) if partition.semantic else 0
                                                    p_ast = partition.graph.get_stats().get("ast_node_count", 0) if partition.graph else 0
                                                    p_symbols = partition.graph.get_stats().get("symbol_count", 0) if partition.graph else 0
                                                    p_rels = partition.graph.get_stats().get("relationship_count", 0) if partition.graph else 0
                                                    
                                                    logger.info(
                                                        "  ├─ %s: %d chunks, %d AST nodes, %d symbols, %d relationships",
                                                        partition_name,
                                                        p_chunks,
                                                        p_ast,
                                                        p_symbols,
                                                        p_rels
                                                    )
                                                except Exception as pe:
                                                    logger.warning("  ├─ %s: stats unavailable (%s)", partition_name, pe)
                                    
                                    last_rebuild_time[index_name] = current_time
                                elif index_name in result.get("indexes_failed", []):
                                    logger.error("❌ Failed to rebuild index '%s'", index_name)
                                    last_rebuild_time[index_name] = current_time  # Still set cooldown to prevent spam
                            except Exception as rebuild_error:
                                logger.error("❌ Error rebuilding index '%s': %s", 
                                           index_name, rebuild_error, exc_info=True)
                                last_rebuild_time[index_name] = current_time  # Set cooldown even on error
                        else:
                            logger.debug("✅ Index '%s' is healthy", index_name)
                    
                    logger.info("🏥 Periodic health check complete")
                
                # Wait 1 minute before next health check
                poll_interval_seconds = 1 * 60  # 1 minute
                await asyncio.sleep(poll_interval_seconds)
                
            except Exception as e:
                logger.error("Error in health check poller: %s", e, exc_info=True)
                # Wait before retrying on error
                await asyncio.sleep(60)
    
    # Store state for lazy startup
    # We can't use asyncio.create_task() during synchronous initialization
    # because FastMCP's event loop hasn't started yet (mcp.run() starts it later)
    tasks_started = False
    
    async def start_background_tasks_once():
        """Start background tasks on first request (lazy init)."""
        nonlocal tasks_started
        if not tasks_started:
            tasks_started = True
            # Start index building task (one-time, exits after build)
            asyncio.create_task(index_building_task())
            # Start cleanup task (continuous, runs forever)
            asyncio.create_task(cleanup_task())
            # Start health check poller (continuous, runs forever)
            asyncio.create_task(health_check_poller())
            logger.info("🚀 Background tasks scheduled (lazy init on first MCP request)")
    
    # Add middleware to start background tasks on first request
    # This ensures the event loop is running before we schedule tasks
    @mcp.add_middleware  # type: ignore[arg-type]
    async def startup_middleware(context, call_next):
        """Middleware to lazily start background tasks on first request."""
        await start_background_tasks_once()
        return await call_next(context)
    
    logger.info("⏳ Background tasks (index building, cleanup, health monitoring) will start on first MCP request")
    
    # ========================================================================
    # 8. Server Ready
    # ========================================================================
    logger.info("=" * 60)
    logger.info("✅ Ouroboros MCP Server initialized successfully!")
    logger.info("   Transport mode: %s", transport_mode)
    logger.info("   Tools available: %d", results["tools_registered"])
    logger.info("=" * 60)
    
    return mcp


__all__ = ["create_server"]


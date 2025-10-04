"""
Agent OS MCP/RAG Server - Main Integration Point.

Exposes 5 MCP tools to Cursor IDE for workflow-aware RAG retrieval.
100% AI-authored via human orchestration.

Tools:
1. search_standards - Semantic search over Agent OS
2. start_workflow - Initialize workflow session
3. get_current_phase - Retrieve current phase content
4. complete_phase - Submit evidence and advance
5. get_workflow_state - Query workflow state

Features:
- Automatic index rebuild when AI edits Agent OS content
- Local-first embeddings (free, offline)
- HoneyHive tracing for dogfooding
"""

import logging
import os
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from mcp.server.fastmcp import FastMCP
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add mcp_servers directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from rag_engine import RAGEngine
from workflow_engine import WorkflowEngine
from state_manager import StateManager

# HoneyHive tracing for dogfooding - singleton pattern
HONEYHIVE_ENABLED = False
tracer = None
_tracer_initialized = False

try:
    from honeyhive import HoneyHiveTracer, trace, enrich_span
    from honeyhive.models import EventType
    HONEYHIVE_ENABLED = os.getenv("HONEYHIVE_ENABLED", "false").lower() == "true"
except ImportError as e:
    import sys as _sys
    _sys.stderr.write(f"DEBUG: ImportError - {e}\n")
    _sys.stderr.flush()
    HONEYHIVE_ENABLED = False


def _init_tracer():
    """Initialize HoneyHive tracer (singleton pattern)."""
    global tracer, _tracer_initialized, HONEYHIVE_ENABLED
    
    if _tracer_initialized:
        return  # Already initialized
    
    _tracer_initialized = True
    
    if not HONEYHIVE_ENABLED:
        return
    
    # Debug: Log what env vars we're seeing
    import sys as _sys
    _sys.stderr.write(f"DEBUG: HONEYHIVE_ENABLED={os.getenv('HONEYHIVE_ENABLED')}\n")
    _sys.stderr.write(f"DEBUG: HH_API_KEY={'SET' if os.getenv('HH_API_KEY') else 'NOT SET'}\n")
    _sys.stderr.write(f"DEBUG: HONEYHIVE_PROJECT={os.getenv('HONEYHIVE_PROJECT')}\n")
    _sys.stderr.write(f"DEBUG: HH_PROJECT={os.getenv('HH_PROJECT')}\n")
    _sys.stderr.flush()
    
    # Initialize tracer with environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HONEYHIVE_PROJECT") or os.getenv("HH_PROJECT")
    
    if api_key and project:
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            source="agent-os-mcp-server",
            verbose=True
        )
        _sys.stderr.write(f"🍯 HoneyHive tracing enabled for dogfooding (project: {project})\n")
        _sys.stderr.write(f"DEBUG: tracer object = {tracer}\n")
        _sys.stderr.write(f"DEBUG: tracer.session_id = {tracer.session_id if tracer else 'None'}\n")
        _sys.stderr.flush()
    else:
        logger = logging.getLogger(__name__)
        logger.warning(
            "HoneyHive enabled but missing HH_API_KEY or HONEYHIVE_PROJECT, "
            "tracing disabled"
        )
        HONEYHIVE_ENABLED = False

# No-op decorators if HoneyHive not enabled or available
if not HONEYHIVE_ENABLED:
    def trace(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def enrich_span(data):
        pass


def tool_trace(func):
    """Helper to apply trace decorator with tracer instance for tools."""
    import sys as _trace_sys
    _trace_sys.stderr.write(f"DEBUG: tool_trace called for {func.__name__}, HONEYHIVE_ENABLED={HONEYHIVE_ENABLED}, tracer={tracer}\n")
    _trace_sys.stderr.flush()
    if HONEYHIVE_ENABLED and tracer:
        _trace_sys.stderr.write(f"DEBUG: Wrapping {func.__name__} with @trace decorator\n")
        _trace_sys.stderr.flush()
        wrapped = trace(tracer=tracer, event_type=EventType.tool)(func)
        _trace_sys.stderr.write(f"DEBUG: Wrapped function: {wrapped}\n")
        _trace_sys.stderr.flush()
        return wrapped
    return func

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG level to see verbose HoneyHive tracer output
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(".agent-os/.cache/mcp_server.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger(__name__)


class AgentOSFileWatcher(FileSystemEventHandler):
    """Watches Agent OS standards directory for AI edits and triggers index rebuild."""
    
    def __init__(
        self,
        index_path: Path,
        standards_path: Path,
        rag_engine: Optional[RAGEngine] = None
    ) -> None:
        """Initialize file watcher for Agent OS content changes.
        
        :param index_path: Path to vector index directory
        :type index_path: Path
        :param standards_path: Path to Agent OS standards directory
        :type standards_path: Path
        :param rag_engine: Optional RAG engine instance for hot reload
        :type rag_engine: Optional[RAGEngine]
        """
        self.index_path: Path = index_path
        self.standards_path: Path = standards_path
        self.rag_engine: Optional[RAGEngine] = rag_engine
        self.rebuild_pending: bool = False
        self.last_rebuild_time: float = 0
        self.debounce_seconds: int = 5  # Wait 5s after last change before rebuilding
        
    def on_modified(self, event: Any) -> None:
        """Handle file modification events.
        
        :param event: File system event from watchdog
        :type event: Any
        """
        if event.is_directory:
            return
        
        # Only rebuild for markdown files
        if not event.src_path.endswith('.md'):
            return
        
        logger.info(f"📝 Agent OS content modified: {Path(event.src_path).name}")
        self._schedule_rebuild()
    
    def on_created(self, event: Any) -> None:
        """Handle file creation events.
        
        :param event: File system event from watchdog
        :type event: Any
        """
        if event.is_directory:
            return
        
        if event.src_path.endswith('.md'):
            logger.info(f"📝 New Agent OS content: {Path(event.src_path).name}")
            self._schedule_rebuild()
    
    def _schedule_rebuild(self) -> None:
        """Schedule an index rebuild with debouncing.
        
        Prevents rapid repeated rebuilds by debouncing changes and running
        rebuild in background thread after quiet period.
        """
        if self.rebuild_pending:
            return  # Already scheduled
        
        self.rebuild_pending = True
        
        def rebuild_after_debounce() -> None:
            """Wait for debounce period, then incrementally update index with locking."""
            time.sleep(self.debounce_seconds)
            
            logger.info(
                "🔄 Incrementally updating index after Agent OS content changes..."
            )
            try:
                # Import here to avoid circular dependency
                sys.path.insert(0, str(self.index_path.parent.parent))
                from scripts.build_rag_index import IndexBuilder
                
                # Use incremental update for fast hot reload!
                builder = IndexBuilder(
                    index_path=self.index_path,
                    standards_path=self.standards_path,
                    embedding_provider="local",
                )
                
                result = builder.build_index(force=False, incremental=True)
                
                # Reload RAG engine with thread-safe locking
                # The reload_index() method acquires write lock automatically
                if self.rag_engine and result["status"] == "success":
                    self.rag_engine.reload_index()
                    build_type = result.get("build_type", "update")
                    files_processed = result.get("files_processed", 0)
                    logger.info(
                        f"✅ {build_type.title()} complete! "
                        f"Processed {files_processed} file(s), "
                        f"{result['chunks']} total chunks available."
                    )
                
                self.last_rebuild_time = time.time()
                
            except Exception as e:
                logger.error(f"❌ Index update failed: {e}", exc_info=True)
            finally:
                self.rebuild_pending = False
        
        # Run rebuild in background thread
        threading.Thread(target=rebuild_after_debounce, daemon=True).start()


def create_server(base_path: Optional[Path] = None) -> FastMCP:
    """Create and configure the Agent OS MCP/RAG server.
    
    Initializes all components (RAG engine, workflow engine, state manager)
    and registers 5 MCP tools for Cursor IDE integration.
    
    :param base_path: Base path for Agent OS (defaults to .agent-os/)
    :type base_path: Optional[Path]
    :return: Configured FastMCP server instance ready for stdio transport
    :rtype: FastMCP
    
    **Example:**
    
    .. code-block:: python
    
        from pathlib import Path
        server = create_server(Path(".agent-os"))
        server.run(transport='stdio')
    """
    # Determine base path
    if base_path is None:
        # Assume server is in .agent-os/mcp_servers/
        base_path = Path(__file__).parent.parent

    base_path = Path(base_path)
    standards_path = base_path / "standards"
    cache_path = base_path / ".cache"
    index_path = cache_path / "vector_index"
    state_path = cache_path / "state"

    # Ensure cache directories exist
    cache_path.mkdir(parents=True, exist_ok=True)
    state_path.mkdir(parents=True, exist_ok=True)

    # Initialize components
    logger.info("Initializing Agent OS MCP/RAG Server")
    
    # Initialize HoneyHive tracer (singleton - only once)
    _init_tracer()
    
    # Check if index exists, build if missing
    _ensure_index_exists(index_path, standards_path)

    # Initialize components
    rag_engine = RAGEngine(index_path=index_path, standards_path=standards_path)
    state_manager = StateManager(state_dir=state_path)
    workflow_engine = WorkflowEngine(
        state_manager=state_manager, rag_engine=rag_engine
    )
    
    logger.info("All components initialized successfully")
    
    # Start file watcher for automatic index rebuild
    logger.info(f"👀 Watching {standards_path} for AI edits...")
    file_watcher = AgentOSFileWatcher(index_path, standards_path, rag_engine)
    observer = Observer()
    observer.schedule(file_watcher, path=str(standards_path), recursive=True)
    observer.start()
    logger.info("✅ File watcher active - index will auto-rebuild on content changes")

    # Create FastMCP server
    mcp = FastMCP(
        name="agent-os-rag",
        instructions="Agent OS RAG/Workflow engine with phase gating"
    )

    # Register Tool 1: search_standards
    @mcp.tool()
    @tool_trace
    async def search_standards(
        query: str,
        n_results: int = 5,
        filter_phase: Optional[int] = None,
        filter_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Semantic search over Agent OS documentation.

        Performs RAG-based semantic search to find relevant Agent OS content.
        Replaces reading entire framework documents with targeted retrieval.

        Args:
            query: Natural language question or topic
            n_results: Number of chunks to return (default 5)
            filter_phase: Optional phase number filter (1-8)
            filter_tags: Optional tags filter (e.g., ["mocking", "ast"])

        Returns:
            Dictionary with results, tokens, retrieval method, and timing
        """
        try:
            # Enrich HoneyHive span with MCP context
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "search_standards",
                    "mcp.query": query,
                    "mcp.n_results": n_results,
                    "mcp.filter_phase": filter_phase,
                    "mcp.filter_tags": filter_tags,
                })

            logger.info(
                f"search_standards: query='{query}', n_results={n_results}, "
                f"filter_phase={filter_phase}"
            )

            filters = {}
            if filter_phase is not None:
                filters["phase"] = filter_phase
            if filter_tags:
                filters["tags"] = filter_tags

            result = rag_engine.search(
                query=query, n_results=n_results, filters=filters
            )

            # Format response
            formatted_results = [
                {
                    "content": chunk.get("content", ""),
                    "file": chunk.get("file_path", ""),
                    "section": chunk.get("section_header", ""),
                    "relevance_score": score,
                    "tokens": chunk.get("tokens", 0),
                }
                for chunk, score in zip(result.chunks, result.relevance_scores)
            ]

            response = {
                "results": formatted_results,
                "total_tokens": result.total_tokens,
                "retrieval_method": result.retrieval_method,
                "query_time_ms": result.query_time_ms,
            }

            # Enrich span with results
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "result.chunks_returned": len(formatted_results),
                    "result.total_tokens": result.total_tokens,
                    "result.retrieval_method": result.retrieval_method,
                    "result.query_time_ms": result.query_time_ms,
                })

            logger.info(
                f"search_standards completed: {len(formatted_results)} results, "
                f"{result.total_tokens} tokens, {result.query_time_ms:.2f}ms"
            )

            return response

        except Exception as e:
            logger.error(f"search_standards failed: {e}", exc_info=True)
            return {"error": str(e), "results": [], "total_tokens": 0}

    # Register Tool 2: start_workflow
    @mcp.tool()
    @tool_trace
    async def start_workflow(
        workflow_type: str,
        target_file: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Start new workflow session with phase gating.

        Initializes a new workflow session, enforcing sequential phase execution.
        Returns Phase 1 content with acknowledgment requirement.

        Args:
            workflow_type: "test_generation_v3" or "production_code_v2"
            target_file: File being worked on (e.g., "config/dsl/compiler.py")
            options: Optional workflow configuration

        Returns:
            Dictionary with session info, Phase 1 content, and acknowledgment
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "start_workflow",
                    "workflow.type": workflow_type,
                    "workflow.target_file": target_file,
                })

            logger.info(
                f"start_workflow: type='{workflow_type}', file='{target_file}'"
            )

            result = workflow_engine.start_workflow(
                workflow_type=workflow_type,
                target_file=target_file,
                metadata=options,
            )

            if HONEYHIVE_ENABLED:
                enrich_span({
                    "workflow.session_id": result.get("session_id"),
                    "workflow.current_phase": result.get("current_phase"),
                })

            logger.info(f"Workflow started: session_id={result['session_id']}")

            return result

        except Exception as e:
            logger.error(f"start_workflow failed: {e}", exc_info=True)
            return {"error": str(e)}

    # Register Tool 3: get_current_phase
    @mcp.tool()
    @tool_trace
    async def get_current_phase(session_id: str) -> Dict[str, Any]:
        """
        Get current phase content and requirements.

        Retrieves the content for the current phase in the workflow,
        including requirements, commands, and artifacts from previous phases.

        Args:
            session_id: Workflow session identifier

        Returns:
            Dictionary with current phase content and artifacts
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "get_current_phase",
                    "workflow.session_id": session_id,
                })

            logger.info(f"get_current_phase: session_id='{session_id}'")

            result = workflow_engine.get_current_phase(session_id)

            if HONEYHIVE_ENABLED:
                enrich_span({
                    "workflow.current_phase": result.get("current_phase"),
                    "workflow.target_file": result.get("target_file"),
                })

            logger.info(
                f"Returned phase {result['current_phase']} content for {session_id}"
            )

            return result

        except ValueError as e:
            logger.warning(f"get_current_phase: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"get_current_phase failed: {e}", exc_info=True)
            return {"error": str(e)}

    # Register Tool 4: complete_phase
    @mcp.tool()
    @tool_trace
    async def complete_phase(
        session_id: str, phase: int, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit evidence and attempt phase completion.

        Validates evidence against checkpoint criteria.
        If passed, advances to next phase and returns content.
        If failed, returns missing evidence and current phase content.

        Args:
            session_id: Workflow session identifier
            phase: Phase number being completed
            evidence: Evidence dictionary matching checkpoint criteria

        Returns:
            Dictionary with checkpoint result and next phase content if passed
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "complete_phase",
                    "workflow.session_id": session_id,
                    "workflow.phase": phase,
                    "workflow.evidence_fields": list(evidence.keys()),
                })

            logger.info(
                f"complete_phase: session_id='{session_id}', phase={phase}, "
                f"evidence_keys={list(evidence.keys())}"
            )

            result = workflow_engine.complete_phase(
                session_id=session_id, phase=phase, evidence=evidence
            )

            if HONEYHIVE_ENABLED:
                enrich_span({
                    "workflow.checkpoint_passed": result.get("checkpoint_passed"),
                    "workflow.next_phase": result.get("next_phase"),
                    "workflow.missing_evidence": result.get("missing_evidence", []),
                })

            if result.get("checkpoint_passed"):
                logger.info(f"Phase {phase} completed for {session_id}")
            else:
                logger.warning(
                    f"Phase {phase} checkpoint failed: {result.get('missing_evidence')}"
                )

            return result

        except ValueError as e:
            logger.warning(f"complete_phase: {e}")
            return {"error": str(e), "checkpoint_passed": False}
        except Exception as e:
            logger.error(f"complete_phase failed: {e}", exc_info=True)
            return {"error": str(e), "checkpoint_passed": False}

    # Register Tool 5: get_workflow_state
    @mcp.tool()
    @tool_trace
    async def get_workflow_state(session_id: str) -> Dict[str, Any]:
        """
        Get complete workflow state for debugging/resume.

        Returns full workflow state including progress, completed phases,
        artifacts, and resume capability.

        Args:
            session_id: Workflow session identifier

        Returns:
            Dictionary with complete workflow state
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span({
                    "mcp.tool": "get_workflow_state",
                    "workflow.session_id": session_id,
                })

            logger.info(f"get_workflow_state: session_id='{session_id}'")

            result = workflow_engine.get_workflow_state(session_id)

            if HONEYHIVE_ENABLED:
                enrich_span({
                    "workflow.current_phase": result.get("current_phase"),
                    "workflow.completed_phases": result.get("completed_phases", []),
                    "workflow.is_complete": result.get("is_complete"),
                })

            logger.info(
                f"Returned state for {session_id}: phase {result['current_phase']}"
            )

            return result

        except ValueError as e:
            logger.warning(f"get_workflow_state: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"get_workflow_state failed: {e}", exc_info=True)
            return {"error": str(e)}

    logger.info("Agent OS MCP/RAG Server ready with 5 tools registered")
    return mcp


def _ensure_index_exists(index_path: Path, standards_path: Path) -> None:
    """Ensure vector index exists, build if missing.
    
    Implements first-run experience by checking for existing LanceDB index
    and automatically building it if not found using local embeddings.
    
    :param index_path: Path to vector index directory
    :type index_path: Path
    :param standards_path: Path to Agent OS standards directory
    :type standards_path: Path
    :raises RuntimeError: If index build fails and cannot be recovered
    
    **Note:**
    
    This function blocks for ~60 seconds on first run while building the index.
    Subsequent runs detect the existing index and return immediately.
    """
    # Check if index exists (LanceDB format)
    index_marker = index_path / "agent_os_standards.lance"

    if index_marker.exists():
        logger.info(f"Vector index found at {index_path}")
        return

    # Index doesn't exist - build it
    logger.warning("Vector index not found - building index for first run")
    logger.info("This will take ~60 seconds, please wait...")

    try:
        # Import here to avoid circular dependency
        import sys
        sys.path.insert(0, str(index_path.parent.parent))
        from scripts.build_rag_index import IndexBuilder

        # Build index with local embeddings (free, offline)
        builder = IndexBuilder(
            index_path=index_path,
            standards_path=standards_path,
            embedding_provider="local",
        )

        logger.info("Building vector index from Agent OS standards...")
        builder.build_index()

        logger.info("✅ Vector index built successfully!")
        logger.info(f"Index location: {index_path}")

    except Exception as e:
        logger.error(f"Failed to build index: {e}", exc_info=True)
        logger.error(
            "Please run manually: python .agent-os/scripts/build_rag_index.py"
        )
        raise RuntimeError(
            f"Vector index is required but could not be built: {e}"
        )


def main() -> None:
    """Entry point for MCP server.
    
    Starts the Agent OS MCP/RAG server with stdio transport for Cursor IDE.
    Handles graceful shutdown on KeyboardInterrupt and logs fatal errors.
    
    :raises SystemExit: Exits with code 1 if server initialization fails
    
    **Example:**
    
    .. code-block:: python
    
        # Run from command line:
        # python .agent-os/run_mcp_server.py
        
        if __name__ == "__main__":
            main()
    """
    try:
        # Create server
        mcp = create_server()
        
        # Run with stdio transport for Cursor integration
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport='stdio')
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

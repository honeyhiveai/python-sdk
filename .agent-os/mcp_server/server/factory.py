"""
ServerFactory for creating MCP server with dependency injection.

Creates and wires all components (RAG engine, workflow engine, file watchers)
with full dependency injection throughout.
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: Factory methods require 6 parameters for complete server
# configuration (config, enable_watch, skip_build, log_level, etc) to support
# flexible initialization patterns

# pylint: disable=import-outside-toplevel
# Justification: IndexBuilder imported lazily to avoid circular dependencies
# and reduce startup time when index building is not needed

import logging
import sys
from typing import Any, List, Optional

from fastmcp import FastMCP
from watchdog.observers import Observer

from ..framework_generator import FrameworkGenerator
from ..models.config import ServerConfig
from ..monitoring.watcher import AgentOSFileWatcher
from ..rag_engine import RAGEngine
from ..state_manager import StateManager
from ..workflow_engine import WorkflowEngine
from ..workflow_validator import WorkflowValidator
from .browser_manager import BrowserManager
from .tools import register_all_tools

logger = logging.getLogger(__name__)


class ServerFactory:
    """Factory for creating MCP server with dependency injection."""

    def __init__(self, config: ServerConfig):
        """
        Initialize factory with validated configuration.

        :param config: Validated ServerConfig
        """
        self.config = config
        self.paths = config.resolved_paths
        self.observers: List[Any] = []  # Track file watchers for cleanup

    def create_server(
        self, project_discovery: Optional[Any] = None, transport_mode: str = "stdio"
    ) -> FastMCP:
        """
        Create fully configured MCP server.

        :param project_discovery: Optional ProjectInfoDiscovery for server info tool
        :param transport_mode: Transport mode for server info (dual, stdio, http)
        :return: FastMCP server ready to run
        :raises ValueError: If component creation fails
        """
        logger.info("🏗️  Creating MCP server with modular architecture")

        # Ensure directories exist
        self._ensure_directories()

        # Ensure RAG index exists
        self._ensure_index()

        # Create core components (dependency injection!)
        rag_engine = self._create_rag_engine()
        state_manager = self._create_state_manager()
        workflow_engine = self._create_workflow_engine(rag_engine, state_manager)
        framework_generator = self._create_framework_generator(rag_engine)
        browser_manager = self._create_browser_manager()

        # Start file watchers
        self._start_file_watchers(rag_engine)

        # Create MCP server and register tools
        mcp = self._create_mcp_server(
            rag_engine=rag_engine,
            workflow_engine=workflow_engine,
            framework_generator=framework_generator,
            workflow_validator=WorkflowValidator,
            browser_manager=browser_manager,
            project_discovery=project_discovery,
            transport_mode=transport_mode,
        )

        logger.info("✅ MCP server created successfully")
        return mcp

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        # Create cache directory if needed
        cache_dir = self.paths["index_path"].parent
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created cache directory: %s", cache_dir)

    def _ensure_index(self) -> None:
        """Ensure RAG index exists, build if missing."""
        index_path = self.paths["index_path"]

        if index_path.exists():
            logger.info("✅ RAG index found at %s", index_path)
            return

        logger.info("⚠️  RAG index not found, building...")

        try:
            # Import IndexBuilder from .agent-os/scripts/
            sys.path.insert(0, str(self.config.base_path))
            from scripts.build_rag_index import IndexBuilder

            builder = IndexBuilder(
                index_path=index_path,
                standards_path=self.paths["standards_path"],
                usage_path=(
                    self.paths["usage_path"]
                    if self.paths["usage_path"].exists()
                    else None
                ),
                workflows_path=(
                    self.paths["workflows_path"]
                    if self.paths["workflows_path"].exists()
                    else None
                ),
                embedding_provider=self.config.rag.embedding_provider,
            )

            result = builder.build_index()

            if result["status"] == "success":
                logger.info("✅ RAG index built: %s chunks", result.get("chunks", 0))
            else:
                logger.warning("⚠️  Index build incomplete: %s", result.get("message"))

        except Exception as e:
            logger.error("❌ Failed to build index: %s", e, exc_info=True)
            raise ValueError(f"Could not build RAG index: {e}") from e

    def _create_rag_engine(self) -> RAGEngine:
        """Create RAG engine with configured paths."""
        logger.info("Creating RAG engine...")
        return RAGEngine(
            index_path=self.paths["index_path"],
            standards_path=self.config.base_path.parent,
        )

    def _create_state_manager(self) -> StateManager:
        """Create state manager with configured path."""
        logger.info("Creating state manager...")
        state_dir = self.paths["index_path"].parent / "state"
        return StateManager(state_dir=state_dir)

    def _create_workflow_engine(
        self, rag_engine: RAGEngine, state_manager: StateManager
    ) -> WorkflowEngine:
        """Create workflow engine with dependencies."""
        logger.info("Creating workflow engine...")
        return WorkflowEngine(
            state_manager=state_manager,
            rag_engine=rag_engine,
            workflows_base_path=self.paths["workflows_path"],
        )

    def _create_framework_generator(self, rag_engine: RAGEngine) -> FrameworkGenerator:
        """Create framework generator with dependencies."""
        logger.info("Creating framework generator...")
        return FrameworkGenerator(rag_engine=rag_engine)

    def _create_browser_manager(self) -> BrowserManager:
        """
        Create browser manager for Playwright automation.

        :return: BrowserManager instance

        Traceability:
            FR-11 (ServerFactory integration)
        """
        logger.info("Creating browser manager...")
        session_timeout = 3600  # 1 hour default
        return BrowserManager(session_timeout=session_timeout)

    def _start_file_watchers(self, rag_engine: RAGEngine) -> None:
        """Start file watchers for hot reload."""
        logger.info("Starting file watchers...")

        # Create watcher with configured paths
        watcher = AgentOSFileWatcher(
            index_path=self.paths["index_path"],
            standards_path=self.paths["standards_path"],
            usage_path=(
                self.paths["usage_path"] if self.paths["usage_path"].exists() else None
            ),
            workflows_path=(
                self.paths["workflows_path"]
                if self.paths["workflows_path"].exists()
                else None
            ),
            embedding_provider=self.config.rag.embedding_provider,
            rag_engine=rag_engine,
            debounce_seconds=5,
        )

        # Watch standards directory
        observer = Observer()
        observer.schedule(watcher, str(self.paths["standards_path"]), recursive=True)

        # Watch usage directory if exists
        if self.paths["usage_path"].exists():
            observer.schedule(watcher, str(self.paths["usage_path"]), recursive=True)

        # Watch workflows directory if exists
        if self.paths["workflows_path"].exists():
            observer.schedule(
                watcher, str(self.paths["workflows_path"]), recursive=True
            )

        observer.start()
        self.observers.append(observer)

        logger.info("✅ File watchers started (hot reload enabled)")

    def _create_mcp_server(
        self,
        rag_engine: RAGEngine,
        workflow_engine: WorkflowEngine,
        framework_generator: FrameworkGenerator,
        workflow_validator: type,
        browser_manager: BrowserManager,
        project_discovery: Optional[Any] = None,
        transport_mode: str = "stdio",
    ) -> FastMCP:
        """Create and configure FastMCP server."""
        logger.info("Creating FastMCP server...")

        # Create FastMCP instance
        mcp = FastMCP("agent-os-rag")

        # Register tools with selective loading
        tool_count = register_all_tools(
            mcp=mcp,
            rag_engine=rag_engine,
            workflow_engine=workflow_engine,
            framework_generator=framework_generator,
            workflow_validator=workflow_validator,
            browser_manager=browser_manager,
            base_path=self.config.base_path,
            enabled_groups=self.config.mcp.enabled_tool_groups,
            max_tools_warning=self.config.mcp.max_tools_warning,
            project_discovery=project_discovery,
            transport_mode=transport_mode,
        )

        logger.info("✅ FastMCP server created with %s tools", tool_count)

        return mcp

    async def shutdown(self, browser_manager: Optional[BrowserManager] = None) -> None:
        """
        Shutdown file watchers and cleanup resources.

        :param browser_manager: Optional BrowserManager to shutdown
        """
        logger.info("Shutting down server factory...")

        # Shutdown browser manager if provided
        if browser_manager:
            await browser_manager.shutdown()

        for observer in self.observers:
            observer.stop()
            observer.join()

        self.observers.clear()
        logger.info("✅ Server factory shutdown complete")


__all__ = ["ServerFactory"]

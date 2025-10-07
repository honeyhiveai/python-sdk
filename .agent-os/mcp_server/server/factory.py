"""
ServerFactory for creating MCP server with dependency injection.

Creates and wires all components (RAG engine, workflow engine, file watchers)
with full dependency injection throughout.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from fastmcp import FastMCP

from ..models.config import ServerConfig
from ..rag_engine import RAGEngine
from ..state_manager import StateManager
from ..workflow_engine import WorkflowEngine
from ..framework_generator import FrameworkGenerator
from ..monitoring.watcher import AgentOSFileWatcher
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
        self.observers = []  # Track file watchers for cleanup
    
    def create_server(self) -> FastMCP:
        """
        Create fully configured MCP server.
        
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
        
        # Start file watchers
        self._start_file_watchers(rag_engine)
        
        # Create MCP server and register tools
        mcp = self._create_mcp_server(
            rag_engine=rag_engine,
            workflow_engine=workflow_engine,
            framework_generator=framework_generator
        )
        
        logger.info("✅ MCP server created successfully")
        return mcp
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        # Create cache directory if needed
        cache_dir = self.paths["index_path"].parent
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created cache directory: {cache_dir}")
    
    def _ensure_index(self) -> None:
        """Ensure RAG index exists, build if missing."""
        index_path = self.paths["index_path"]
        
        if index_path.exists():
            logger.info(f"✅ RAG index found at {index_path}")
            return
        
        logger.info("⚠️  RAG index not found, building...")
        
        try:
            # Import IndexBuilder
            sys.path.insert(0, str(self.config.base_path.parent))
            from scripts.build_rag_index import IndexBuilder
            
            builder = IndexBuilder(
                index_path=index_path,
                standards_path=self.paths["standards_path"],
                usage_path=self.paths["usage_path"] if self.paths["usage_path"].exists() else None,
                workflows_path=self.paths["workflows_path"] if self.paths["workflows_path"].exists() else None,
                embedding_provider=self.config.rag.embedding_provider,
            )
            
            result = builder.build_index()
            
            if result["status"] == "success":
                logger.info(f"✅ RAG index built: {result['chunks_indexed']} chunks")
            else:
                logger.warning(f"⚠️  Index build incomplete: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"❌ Failed to build index: {e}", exc_info=True)
            raise ValueError(f"Could not build RAG index: {e}")
    
    def _create_rag_engine(self) -> RAGEngine:
        """Create RAG engine with configured paths."""
        logger.info("Creating RAG engine...")
        return RAGEngine(
            index_path=self.paths["index_path"],
            standards_path=self.config.base_path.parent
        )
    
    def _create_state_manager(self) -> StateManager:
        """Create state manager with configured path."""
        logger.info("Creating state manager...")
        state_dir = self.paths["index_path"].parent / "state"
        return StateManager(state_dir=state_dir)
    
    def _create_workflow_engine(
        self,
        rag_engine: RAGEngine,
        state_manager: StateManager
    ) -> WorkflowEngine:
        """Create workflow engine with dependencies."""
        logger.info("Creating workflow engine...")
        return WorkflowEngine(
            state_manager=state_manager,
            rag_engine=rag_engine,
            workflows_base_path=self.paths["workflows_path"]
        )
    
    def _create_framework_generator(
        self,
        rag_engine: RAGEngine
    ) -> FrameworkGenerator:
        """Create framework generator with dependencies."""
        logger.info("Creating framework generator...")
        return FrameworkGenerator(rag_engine=rag_engine)
    
    def _start_file_watchers(self, rag_engine: RAGEngine) -> None:
        """Start file watchers for hot reload."""
        logger.info("Starting file watchers...")
        
        # Create watcher with configured paths
        watcher = AgentOSFileWatcher(
            index_path=self.paths["index_path"],
            standards_path=self.paths["standards_path"],
            usage_path=self.paths["usage_path"] if self.paths["usage_path"].exists() else None,
            workflows_path=self.paths["workflows_path"] if self.paths["workflows_path"].exists() else None,
            embedding_provider=self.config.rag.embedding_provider,
            rag_engine=rag_engine,
            debounce_seconds=5
        )
        
        # Watch standards directory
        observer = Observer()
        observer.schedule(watcher, str(self.paths["standards_path"]), recursive=True)
        
        # Watch usage directory if exists
        if self.paths["usage_path"].exists():
            observer.schedule(watcher, str(self.paths["usage_path"]), recursive=True)
        
        # Watch workflows directory if exists
        if self.paths["workflows_path"].exists():
            observer.schedule(watcher, str(self.paths["workflows_path"]), recursive=True)
        
        observer.start()
        self.observers.append(observer)
        
        logger.info("✅ File watchers started (hot reload enabled)")
    
    def _create_mcp_server(
        self,
        rag_engine: RAGEngine,
        workflow_engine: WorkflowEngine,
        framework_generator: FrameworkGenerator
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
            base_path=self.config.base_path,
            enabled_groups=self.config.mcp.enabled_tool_groups,
            max_tools_warning=self.config.mcp.max_tools_warning
        )
        
        logger.info(f"✅ FastMCP server created with {tool_count} tools")
        
        return mcp
    
    def shutdown(self) -> None:
        """Shutdown file watchers and cleanup resources."""
        logger.info("Shutting down server factory...")
        
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers.clear()
        logger.info("✅ Server factory shutdown complete")


__all__ = ["ServerFactory"]

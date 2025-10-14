"""
Data Models for Agent OS MCP/RAG System.

Modular organization by domain:
- config: Configuration models (RAGConfig, ServerConfig)
- workflow: Workflow state and phase models
- rag: RAG search and document chunk models
- sub_agents: Sub-agent models (future)

All models importable via: from mcp_server.models import X
"""

# Configuration models
from .config import MCPConfig, RAGConfig, ServerConfig

# RAG models
from .rag import ChunkMetadata, DocumentChunk, QueryMetrics, SearchResult

# Upgrade workflow models
from .upgrade_models import (
    BackupManifest,
    Phase0Evidence,
    Phase1Evidence,
    Phase2Evidence,
    Phase3Evidence,
    Phase4Evidence,
    Phase5Evidence,
    UpgradeReport,
    UpgradeWorkflowSession,
)

# Workflow models
from .workflow import (
    CheckpointCriteria,
    CheckpointStatus,
    CommandExecution,
    PhaseArtifact,
    PhaseMetadata,
    WorkflowConfig,
    WorkflowMetadata,
    WorkflowState,
)

__all__ = [
    # Config
    "RAGConfig",
    "MCPConfig",
    "ServerConfig",
    # Workflow
    "CheckpointStatus",
    "CommandExecution",
    "PhaseArtifact",
    "WorkflowState",
    "CheckpointCriteria",
    "PhaseMetadata",
    "WorkflowMetadata",
    "WorkflowConfig",
    # RAG
    "ChunkMetadata",
    "DocumentChunk",
    "SearchResult",
    "QueryMetrics",
    # Upgrade
    "Phase0Evidence",
    "Phase1Evidence",
    "Phase2Evidence",
    "Phase3Evidence",
    "Phase4Evidence",
    "Phase5Evidence",
    "BackupManifest",
    "UpgradeReport",
    "UpgradeWorkflowSession",
]

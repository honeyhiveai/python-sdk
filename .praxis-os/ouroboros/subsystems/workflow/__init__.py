"""
Workflow Subsystem: Phase-gated execution with evidence validation.

Components:
- WorkflowEngine: Main orchestrator (session-based interface)
- PhaseGates: Enforce sequential phase completion
- EvidenceValidator: Multi-layer validation (field → type → custom → cross-field → artifact)
- HiddenSchemas: Load evidence schemas (never exposed to AI)
- WorkflowRenderer: Render phase content from workflow definitions
- WorkflowState: Immutable state dataclass (Pydantic)

Architecture:
- StateManager (foundation layer) is the integration point for session persistence
- WorkflowEngine coordinates all workflow components
- Delegates validation to PhaseGates + EvidenceValidator
- Delegates rendering to WorkflowRenderer

Note: WorkflowEngine is not imported here to avoid circular imports.
Import directly: from ouroboros.subsystems.workflow.engine import WorkflowEngine
"""

from ouroboros.subsystems.workflow.evidence_validator import EvidenceValidator
from ouroboros.subsystems.workflow.hidden_schemas import HiddenSchemas
from ouroboros.subsystems.workflow.models import (
    CheckpointStatus,
    DynamicPhase,
    DynamicTask,
    PhaseArtifact,
    WorkflowMetadata,
    WorkflowState,
)
from ouroboros.subsystems.workflow.parsers import (
    ParseError,
    SourceParser,
    SpecTasksParser,
    WorkflowDefinitionParser,
)
from ouroboros.subsystems.workflow.phase_gates import PhaseGates
from ouroboros.subsystems.workflow.workflow_renderer import WorkflowRenderer

# Note: WorkflowEngine not included to avoid circular import with StateManager
__all__ = [
    "PhaseGates",
    "EvidenceValidator",
    "HiddenSchemas",
    "WorkflowRenderer",
    "WorkflowState",
    "WorkflowMetadata",
    "PhaseArtifact",
    "CheckpointStatus",
    "DynamicTask",
    "DynamicPhase",
    "ParseError",
    "SourceParser",
    "SpecTasksParser",
    "WorkflowDefinitionParser",
]


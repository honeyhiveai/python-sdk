"""
Configuration schema for workflow subsystem.

Provides Pydantic v2 model for workflow configuration including:
    - Workflow definitions directory
    - State persistence directory
    - Session timeout management
    - Completed workflow cleanup
    - Evidence schema exposure control (ADVERSARIAL DESIGN)

The WorkflowConfig enforces adversarial design principles by preventing
evidence schema exposure. This ensures AI agents cannot game workflow
validation gates.

Example Usage:
    >>> from ouroboros.config.schemas.workflow import WorkflowConfig
    >>> 
    >>> config = WorkflowConfig(
    ...     workflows_dir=Path(".praxis-os/workflows"),
    ...     state_dir=Path(".praxis-os/workflow_states"),
    ...     session_timeout_minutes=1440,  # 24 hours
    ...     cleanup_completed_after_days=30,
    ...     evidence_schemas_exposed=False  # MUST be False
    ... )

See Also:
    - base.BaseConfig: Base configuration model
    - Adversarial design: standards/development/adversarial-design-for-ai-systems.md
"""

from pathlib import Path

from pydantic import Field, field_validator

from ouroboros.config.schemas.base import BaseConfig


class WorkflowConfig(BaseConfig):
    """
    Configuration for workflow subsystem with adversarial design enforcement.

    Manages phase-gated workflow execution with state persistence, session
    timeouts, and automatic cleanup of completed workflows. Critically enforces
    adversarial design by preventing evidence schema exposure.

    Adversarial Design Principle:
        Evidence schemas MUST remain hidden from AI agents. If schemas are
        exposed, agents can game validation by providing exactly the expected
        fields without doing actual work. This validation enforces that
        evidence_schemas_exposed is always False.

    Key Settings:
        - workflows_dir: Directory containing workflow definitions
        - state_dir: Directory for persisting workflow state (JSON files)
        - session_timeout_minutes: Session timeout (60 min to 7 days)
        - cleanup_completed_after_days: Archive completed workflows after N days
        - evidence_schemas_exposed: MUST be False (adversarial design)

    Session Management:
        - Active sessions persist in state_dir/{session_id}.json
        - Sessions timeout after session_timeout_minutes of inactivity
        - Completed sessions archived after cleanup_completed_after_days

    State Persistence:
        State files are JSON with structure:
            {
                "session_id": "uuid",
                "workflow_type": "spec_execution_v1",
                "current_phase": 2,
                "completed_phases": [0, 1],
                "evidence_submitted": {...},
                "created_at": "2025-11-04T12:00:00Z",
                "updated_at": "2025-11-04T13:30:00Z"
            }

    Example:
        >>> from ouroboros.config.schemas.workflow import WorkflowConfig
        >>> 
        >>> # Valid config (evidence_schemas_exposed=False)
        >>> config = WorkflowConfig(
        ...     workflows_dir=Path(".praxis-os/workflows"),
        ...     state_dir=Path(".praxis-os/workflow_states"),
        ...     session_timeout_minutes=1440,  # 24 hours
        ...     cleanup_completed_after_days=30,
        ...     evidence_schemas_exposed=False
        ... )
        >>> 
        >>> # Invalid config (evidence_schemas_exposed=True) - FAILS
        >>> try:
        ...     bad_config = WorkflowConfig(evidence_schemas_exposed=True)
        ... except ValueError as e:
        ...     print(e)  # "evidence_schemas_exposed MUST be False..."

    Validation Rules:
        - workflows_dir: Path to workflow definitions
        - state_dir: Path for state persistence
        - session_timeout_minutes: 60-10080 minutes (1 hour to 7 days)
        - cleanup_completed_after_days: 1-365 days
        - evidence_schemas_exposed: **MUST be False** (enforced by validator)

    Security:
        Adversarial design validator prevents configuration that would enable
        AI agents to game workflow validation gates.
    """

    workflows_dir: Path = Field(
        default=Path(".praxis-os/workflows"),
        description="Directory containing workflow definitions (metadata.json, phases/, tasks/)",
    )

    state_dir: Path = Field(
        default=Path(".praxis-os/workflow_states"),
        description="Directory for persisting workflow state (JSON files per session)",
    )

    session_timeout_minutes: int = Field(
        default=1440,  # 24 hours
        ge=60,  # 1 hour minimum
        le=10080,  # 7 days maximum
        description="Session timeout in minutes (60-10080, default 24 hours)",
    )

    cleanup_completed_after_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Archive completed workflows after N days (1-365)",
    )

    evidence_schemas_exposed: bool = Field(
        default=False,
        description="Expose evidence schemas to AI agents (MUST be False for adversarial design)",
    )

    @field_validator("evidence_schemas_exposed")
    @classmethod
    def prevent_schema_exposure(cls, v: bool) -> bool:
        """
        Enforce adversarial design by preventing evidence schema exposure.

        Evidence schemas MUST remain hidden from AI agents. If schemas are
        exposed, agents can trivially game validation by providing exactly the
        expected fields without doing actual work. This validator enforces that
        evidence_schemas_exposed is always False.

        Adversarial Design Rationale:
            - AI agents optimize for perceived completion, not thoroughness
            - If evidence schema visible → Agent provides minimal fields
            - If evidence schema hidden → Agent must do real work to pass
            - Information asymmetry is intentional and mission-critical

        Args:
            v: Value of evidence_schemas_exposed field

        Returns:
            bool: Validated value (always False)

        Raises:
            ValueError: If v is True (schema exposure attempted)

        Example:
            >>> # Valid: schemas hidden
            >>> config = WorkflowConfig(evidence_schemas_exposed=False)  # ✅
            >>> 
            >>> # Invalid: schemas exposed
            >>> config = WorkflowConfig(evidence_schemas_exposed=True)  # ❌ ValueError

        See Also:
            - standards/development/adversarial-design-for-ai-systems.md
            - Ouroboros mission: Behavioral engineering through structural enforcement
        """
        if v is True:
            raise ValueError(
                "evidence_schemas_exposed MUST be False\n"
                "Reason: Exposing evidence schemas violates adversarial design principle\n"
                "Impact: AI agents can game validation by providing expected fields without doing work\n"
                "Remediation: Set evidence_schemas_exposed=False (or remove field to use default)\n"
                "Reference: See standards/development/adversarial-design-for-ai-systems.md"
            )
        return v


__all__ = ["WorkflowConfig"]


"""
Phase Gates: Enforce sequential phase completion (no phase skipping).

Architecture:
- Pure logic (state passed in, not mutated)
- Clear pass/fail decisions
- Integrates with HiddenSchemas and EvidenceValidator
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from ouroboros.subsystems.workflow.evidence_validator import EvidenceValidator, ValidationResult
from ouroboros.subsystems.workflow.hidden_schemas import HiddenSchemas
from ouroboros.subsystems.workflow.models import CheckpointStatus, WorkflowState
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class PhaseGateError(ActionableError):
    """Phase gate operation failed."""

    pass


@dataclass
class PhaseAdvanceResult:
    """
    Result of phase advance attempt.

    Attributes:
        allowed: Whether advance is allowed
        reason: Reason for allow/deny
        new_state: New state if advance succeeded (None if denied)
        validation_result: Validation result if evidence was checked
    """

    allowed: bool
    reason: str
    new_state: Optional[WorkflowState] = None
    validation_result: Optional[ValidationResult] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        result = {"allowed": self.allowed, "reason": self.reason}

        if self.validation_result:
            result["validation"] = self.validation_result.to_dict()

        return result


class PhaseGates:
    """
    Phase gates: Enforce sequential phase completion.

    Responsibilities:
    - Validate phase progression (must complete phase N before N+1)
    - Check evidence submission before advancing
    - Return phase access decisions
    """

    def __init__(self, hidden_schemas: HiddenSchemas, evidence_validator: EvidenceValidator, max_phase: Optional[int] = None):
        """
        Initialize phase gates.

        Args:
            hidden_schemas: Schema loader for evidence validation
            evidence_validator: Validator for multi-layer checking
            max_phase: Maximum phase number (None = no limit)
        """
        self.hidden_schemas = hidden_schemas
        self.evidence_validator = evidence_validator
        self.max_phase = max_phase

        logger.info("PhaseGates initialized", extra={"max_phase": max_phase})

    def can_advance(self, state: WorkflowState, to_phase: int) -> Tuple[bool, str]:
        """
        Check if can advance to phase.

        Args:
            state: Current workflow state
            to_phase: Target phase number

        Returns:
            (allowed, reason) tuple
        """
        # Check if trying to skip phases
        if to_phase > state.current_phase + 1:
            return (
                False,
                f"Cannot skip phases. Current phase: {state.current_phase}, requested: {to_phase}. "
                f"Complete phase {state.current_phase} before advancing to {to_phase}.",
            )

        # Check if trying to go backwards
        if to_phase < state.current_phase:
            return (False, f"Cannot go backwards. Current phase: {state.current_phase}, requested: {to_phase}.")

        # Check if already at requested phase
        if to_phase == state.current_phase:
            return (True, f"Already at phase {to_phase}.")

        # Check if previous phase completed
        previous_phase = to_phase - 1
        if previous_phase not in state.completed_phases:
            return (
                False,
                f"Phase {previous_phase} incomplete. Complete phase {previous_phase} before advancing to {to_phase}.",
            )

        # Check if previous phase checkpoint passed
        previous_checkpoint = state.checkpoints.get(previous_phase)
        if previous_checkpoint != CheckpointStatus.PASSED:
            return (
                False,
                f"Phase {previous_phase} checkpoint did not pass. "
                f"Submit valid evidence for phase {previous_phase} before advancing.",
            )

        # Check max phase limit
        if self.max_phase is not None and to_phase > self.max_phase:
            return (False, f"Phase {to_phase} exceeds workflow maximum phase {self.max_phase}.")

        return (True, f"Advance to phase {to_phase} allowed.")

    def complete_phase(self, state: WorkflowState, phase: int, evidence: Dict[str, Any]) -> PhaseAdvanceResult:
        """
        Complete phase with evidence submission.

        Validates evidence and returns new state if validation passes.

        Args:
            state: Current workflow state
            phase: Phase to complete
            evidence: Evidence dictionary

        Returns:
            PhaseAdvanceResult with allowed/denied and new state
        """
        # Check if phase is current phase
        if phase != state.current_phase:
            return PhaseAdvanceResult(
                allowed=False,
                reason=f"Cannot complete phase {phase}. Current phase is {state.current_phase}. "
                f"Complete phase {state.current_phase} first.",
            )

        # Load schema for this phase
        try:
            schema = self.hidden_schemas.get_schema(state.workflow_type, phase)
        except Exception as e:
            logger.error("Failed to load schema", extra={"workflow_type": state.workflow_type, "phase": phase, "error": str(e)})
            return PhaseAdvanceResult(
                allowed=False, reason=f"Failed to load evidence schema for phase {phase}: {e}"
            )

        # Validate evidence
        validation_result = self.evidence_validator.validate(evidence, schema)

        # Check if validation passed
        if not validation_result.passed:
            checkpoint_status = CheckpointStatus.FAILED
            reason = f"Evidence validation failed. Errors:\n" + "\n".join(f"  - {err}" for err in validation_result.errors)

            # In strict mode, block completion
            if schema.strict:
                logger.warning(
                    "Evidence validation failed (strict mode)",
                    extra={
                        "workflow_type": state.workflow_type,
                        "phase": phase,
                        "error_count": len(validation_result.errors),
                    },
                )
                return PhaseAdvanceResult(allowed=False, reason=reason, validation_result=validation_result)

            # In non-strict mode, allow but warn
            logger.warning(
                "Evidence validation failed (non-strict mode, allowing)",
                extra={
                    "workflow_type": state.workflow_type,
                    "phase": phase,
                    "error_count": len(validation_result.errors),
                },
            )
            # Fall through to create new state
        else:
            checkpoint_status = CheckpointStatus.PASSED
            reason = f"Phase {phase} completed successfully."

        # Create new state with phase completed
        new_state = state.with_phase_completed(phase, evidence, checkpoint_status)

        logger.info(
            "Phase completed",
            extra={
                "workflow_type": state.workflow_type,
                "phase": phase,
                "checkpoint_status": checkpoint_status.value,
                "new_phase": new_state.current_phase,
            },
        )

        return PhaseAdvanceResult(allowed=True, reason=reason, new_state=new_state, validation_result=validation_result)

    def get_phase_status(self, state: WorkflowState, phase: int) -> Dict[str, Any]:
        """
        Get status of a specific phase.

        Args:
            state: Current workflow state
            phase: Phase to check

        Returns:
            Dictionary with phase status information
        """
        is_completed = phase in state.completed_phases
        is_current = phase == state.current_phase
        checkpoint_status = state.checkpoints.get(phase, CheckpointStatus.PENDING)

        # Determine accessibility
        accessible = is_current or is_completed

        return {
            "phase": phase,
            "is_completed": is_completed,
            "is_current": is_current,
            "accessible": accessible,
            "checkpoint_status": checkpoint_status.value,
            "evidence_submitted": state.evidence_submitted.get(phase, {}),
        }


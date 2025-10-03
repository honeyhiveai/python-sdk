"""
Workflow Engine for Phase Gating and Checkpoint Validation.

Enforces architectural constraints for sequential workflow execution.
100% AI-authored via human orchestration.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Callable

from models import WorkflowState, PhaseArtifact, CheckpointStatus, CommandExecution
from state_manager import StateManager
from rag_engine import RAGEngine

logger = logging.getLogger(__name__)


class CheckpointLoader:
    """
    Load checkpoint requirements dynamically from Agent OS standards.

    Aligns with project principle: dynamic logic over static patterns.
    Single source of truth: Agent OS docs define checkpoints, not code.
    """

    def __init__(self, rag_engine: RAGEngine):
        """
        Initialize checkpoint loader.

        Args:
            rag_engine: RAG engine for querying Agent OS docs
        """
        self.rag_engine = rag_engine
        self._checkpoint_cache: Dict[str, Dict] = {}

    def load_checkpoint_requirements(
        self, workflow_type: str, phase: int
    ) -> Dict[str, Any]:
        """
        Load checkpoint requirements from Agent OS documents dynamically.

        Args:
            workflow_type: Workflow type (e.g., "test_generation_v3")
            phase: Phase number

        Returns:
            Dictionary with required evidence fields and validators
        """
        cache_key = f"{workflow_type}_phase_{phase}"

        if cache_key in self._checkpoint_cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._checkpoint_cache[cache_key]

        # Query RAG for checkpoint section of this phase
        query = f"{workflow_type} Phase {phase} checkpoint requirements evidence"
        
        try:
            result = self.rag_engine.search(
                query=query, n_results=3, filters={"phase": phase}
            )

            # Parse checkpoint requirements from retrieved content
            requirements = self._parse_checkpoint_requirements(result.chunks)

            # Cache for performance
            self._checkpoint_cache[cache_key] = requirements

            logger.info(
                f"Loaded checkpoint requirements for {workflow_type} Phase {phase}"
            )

            return requirements

        except Exception as e:
            logger.error(f"Failed to load checkpoint requirements: {e}")
            # Return minimal fallback requirements
            return {"required_evidence": {}}

    def _parse_checkpoint_requirements(
        self, chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parse checkpoint requirements from document chunks dynamically.

        Analyzes document structure to extract:
        - Required evidence fields
        - Field types (inferred from examples)
        - Validation rules (extracted from requirements language)

        Args:
            chunks: Document chunks from RAG search

        Returns:
            Dictionary with parsed requirements
        """
        requirements = {}

        for chunk in chunks:
            content = chunk.get("content", "")
            lines = content.split("\n")

            for i, line in enumerate(lines):
                # Detect evidence requirement patterns dynamically
                if self._is_evidence_requirement(line):
                    field_name = self._extract_field_name(line)
                    if field_name and field_name != "unknown_field":
                        context_lines = (
                            lines[i : i + 3] if i + 3 < len(lines) else lines[i:]
                        )
                        field_type = self._infer_field_type(line, context_lines)
                        validator = self._extract_validator(line, context_lines)

                        requirements[field_name] = {
                            "type": field_type,
                            "validator": validator,
                            "description": self._extract_description(line),
                        }

        return {"required_evidence": requirements}

    def _is_evidence_requirement(self, line: str) -> bool:
        """Detect if line describes an evidence requirement.
        
        Analyzes line for requirement indicator keywords like "must provide",
        "required:", "evidence:", etc.
        
        :param line: Line from document to analyze
        :type line: str
        :return: True if line describes evidence requirement
        :rtype: bool
        """
        # Look for requirement indicators in line structure
        indicators = [
            "must provide",
            "required:",
            "evidence:",
            "checkpoint:",
            "verify that",
            "proof of",
        ]
        line_lower = line.lower()
        return any(ind in line_lower for ind in indicators)

    def _extract_field_name(self, line: str) -> str:
        """Extract field name from requirement line.
        
        Looks for field names in common formats like `field_name` or
        **field_name** or snake_case words.
        
        :param line: Line with potential field name
        :type line: str
        :return: Extracted field name or "unknown_field" if not found
        :rtype: str
        """
        # Look for field name patterns (typically in code formatting or bold)
        words = line.split()
        for word in words:
            # Field names often in code format: `field_name`
            if word.startswith("`") and word.endswith("`"):
                return word.strip("`")
            # Or emphasized: **field_name**
            if word.startswith("**") and word.endswith("**"):
                return word.strip("*").lower().replace(" ", "_")

        # Fallback: first snake_case word
        for word in words:
            if "_" in word and word.replace("_", "").replace("-", "").isalnum():
                return word.strip(":`\"'")

        return "unknown_field"

    def _infer_field_type(self, line: str, context: List[str]) -> type:
        """Infer field type from context and examples.
        
        Analyzes keywords and context to determine if field should be
        int, str, list, bool, or dict. Defaults to str if unclear.
        
        :param line: Line with field definition
        :type line: str
        :param context: Surrounding lines for additional context
        :type context: List[str]
        :return: Inferred type (int, str, list, bool, or dict)
        :rtype: type
        """
        line_lower = line.lower()
        context_text = " ".join(context).lower()

        # Look for type hints in context
        if any(
            word in line_lower
            for word in ["count", "number", "quantity", "total", "sum"]
        ):
            return int
        if any(
            word in line_lower or word in context_text
            for word in ["list", "array", "collection", "functions", "methods"]
        ):
            return list
        if any(word in line_lower for word in ["flag", "boolean", "true/false"]):
            return bool
        if any(word in line_lower for word in ["dict", "mapping", "object"]):
            return dict
        if any(
            word in line_lower
            for word in ["output", "text", "command", "path", "file"]
        ):
            return str

        # Default to string
        return str

    def _extract_validator(self, line: str, context: List[str]) -> Callable:
        """Extract validation logic from requirement description.
        
        Analyzes requirement language to create appropriate validator function.
        Handles patterns like "greater than", "non-empty", "optional", etc.
        
        :param line: Line with validation requirements
        :type line: str
        :param context: Surrounding lines for context
        :type context: List[str]
        :return: Validation function that returns True if valid
        :rtype: Callable
        """
        line_lower = line.lower()

        # Analyze requirement language for validation rules
        if any(
            phrase in line_lower
            for phrase in ["greater than", "at least", "non-zero", "minimum"]
        ):
            return lambda x: (x > 0 if isinstance(x, int) else len(x) > 0)

        if any(
            phrase in line_lower
            for phrase in ["non-empty", "must contain", "cannot be empty"]
        ):
            return lambda x: len(x) > 0 if hasattr(x, "__len__") else x is not None

        if "optional" in line_lower or "may be empty" in line_lower:
            return lambda x: True

        # Default: must exist and not be None
        return lambda x: x is not None


    def _extract_description(self, line: str) -> str:
        """Extract human-readable description from line.
        
        Removes formatting characters (*, #, -, :, `, ") and returns
        clean description text.
        
        :param line: Line with description and formatting
        :type line: str
        :return: Cleaned description text
        :rtype: str
        """
        # Remove formatting and extract description text
        cleaned = line.strip("*#-:`\"")
        return cleaned.strip()


class WorkflowEngine:
    """
    Workflow engine with architectural phase gating.

    Features:
    - Phase gating: Can only access current phase
    - Checkpoint validation: Evidence required to advance
    - State persistence: Resume workflows
    - Error handling: Clear feedback on violations
    """

    def __init__(
        self,
        state_manager: StateManager,
        rag_engine: RAGEngine,
        checkpoint_loader: Optional[CheckpointLoader] = None,
    ):
        """
        Initialize workflow engine.

        Args:
            state_manager: State manager for persistence
            rag_engine: RAG engine for content retrieval
            checkpoint_loader: Optional custom checkpoint loader
        """
        self.state_manager = state_manager
        self.rag_engine = rag_engine
        self.checkpoint_loader = checkpoint_loader or CheckpointLoader(rag_engine)

        logger.info("WorkflowEngine initialized")

    def start_workflow(
        self, workflow_type: str, target_file: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Start new workflow session with phase gating.

        Args:
            workflow_type: Workflow type (e.g., "test_generation_v3")
            target_file: File being worked on
            metadata: Optional additional metadata

        Returns:
            Dictionary with session info and Phase 1 content
        """
        # Check for existing active session
        existing = self.state_manager.get_active_session(workflow_type, target_file)
        if existing:
            logger.info(
                f"Resuming existing session {existing.session_id} for {target_file}"
            )
            return self._format_phase_response(existing, existing.current_phase)

        # Create new session
        state = self.state_manager.create_session(workflow_type, target_file, metadata)

        logger.info(
            f"Started workflow {workflow_type} session {state.session_id} "
            f"for {target_file}"
        )

        # Return Phase 1 content
        return self._format_phase_response(state, 1)

    def get_current_phase(self, session_id: str) -> Dict[str, Any]:
        """
        Get current phase content for session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with current phase content

        Raises:
            ValueError: If session not found
        """
        state = self.state_manager.load_state(session_id)
        if state is None:
            raise ValueError(f"Session {session_id} not found")

        return self._format_phase_response(state, state.current_phase)

    def get_phase_content(
        self, session_id: str, requested_phase: int
    ) -> Dict[str, Any]:
        """
        Get content for requested phase with gating enforcement.

        Args:
            session_id: Session identifier
            requested_phase: Phase number requested

        Returns:
            Phase content if allowed, error with current phase if denied
        """
        state = self.state_manager.load_state(session_id)
        if state is None:
            raise ValueError(f"Session {session_id} not found")

        # Check access permission
        if not state.can_access_phase(requested_phase):
            # Phase gating violation
            logger.warning(
                f"Phase sequence violation: Session {session_id} tried to access "
                f"phase {requested_phase}, current phase is {state.current_phase}"
            )

            return {
                "error": "Phase sequence violation",
                "message": f"You must complete Phase {state.current_phase} before "
                f"accessing Phase {requested_phase}",
                "violation_type": "attempted_skip",
                "requested_phase": requested_phase,
                "current_phase": state.current_phase,
                "current_phase_content": self._get_phase_content_from_rag(
                    state.workflow_type, state.current_phase
                ),
                "phase_gating_enforced": True,
            }

        # Access allowed
        return self._format_phase_response(state, requested_phase)

    def complete_phase(
        self, session_id: str, phase: int, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Attempt to complete phase with evidence.

        Args:
            session_id: Session identifier
            phase: Phase to complete
            evidence: Evidence dictionary for checkpoint validation

        Returns:
            Result with pass/fail and next phase content if passed

        Raises:
            ValueError: If session not found or phase mismatch
        """
        state = self.state_manager.load_state(session_id)
        if state is None:
            raise ValueError(f"Session {session_id} not found")

        # Verify this is the current phase
        if phase != state.current_phase:
            raise ValueError(
                f"Cannot complete phase {phase}, current phase is {state.current_phase}"
            )

        # Validate checkpoint
        passed, missing = self._validate_checkpoint(
            state.workflow_type, phase, evidence
        )

        if not passed:
            logger.warning(
                f"Checkpoint failed for session {session_id} phase {phase}: "
                f"{missing}"
            )

            return {
                "checkpoint_passed": False,
                "missing_evidence": missing,
                "current_phase": phase,
                "phase_content": self._get_phase_content_from_rag(
                    state.workflow_type, phase
                ),
                "message": "Complete checkpoint requirements to proceed",
                "evidence_provided": list(evidence.keys()),
            }

        # Checkpoint passed - create artifact and advance
        artifact = PhaseArtifact(
            phase_number=phase,
            evidence=evidence,
            outputs=evidence.get("outputs", {}),
            commands_executed=self._extract_commands_from_evidence(evidence),
            timestamp=datetime.now(),
        )

        state.complete_phase(phase, artifact, checkpoint_passed=True)
        self.state_manager.save_state(state)

        logger.info(
            f"Phase {phase} completed for session {session_id}, "
            f"advanced to phase {state.current_phase}"
        )

        # Return next phase or completion
        if state.is_complete():
            return {
                "checkpoint_passed": True,
                "phase_completed": phase,
                "workflow_complete": True,
                "message": "All phases complete!",
                "session_id": session_id,
            }

        # Return next phase content
        return {
            "checkpoint_passed": True,
            "phase_completed": phase,
            "next_phase": state.current_phase,
            "next_phase_content": self._get_phase_content_from_rag(
                state.workflow_type, state.current_phase
            ),
            "artifacts_available": self._get_artifacts_summary(state),
        }

    def get_workflow_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get complete workflow state.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with complete state information
        """
        state = self.state_manager.load_state(session_id)
        if state is None:
            raise ValueError(f"Session {session_id} not found")

        return {
            "session_id": state.session_id,
            "workflow_type": state.workflow_type,
            "target_file": state.target_file,
            "current_phase": state.current_phase,
            "completed_phases": state.completed_phases,
            "total_phases": 8 if "test" in state.workflow_type else 6,
            "is_complete": state.is_complete(),
            "checkpoints": {
                phase: status.value for phase, status in state.checkpoints.items()
            },
            "created_at": state.created_at.isoformat(),
            "updated_at": state.updated_at.isoformat(),
        }

    def _validate_checkpoint(
        self, workflow_type: str, phase: int, evidence: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate evidence against dynamically loaded checkpoint requirements.

        Args:
            workflow_type: Workflow type
            phase: Phase number
            evidence: Evidence dictionary

        Returns:
            Tuple of (passed: bool, missing_fields: List[str])
        """
        # Load requirements dynamically from Agent OS documents
        checkpoint_def = self.checkpoint_loader.load_checkpoint_requirements(
            workflow_type, phase
        )

        requirements = checkpoint_def.get("required_evidence", {})

        # If no requirements found, pass (permissive fallback)
        if not requirements:
            logger.warning(
                f"No checkpoint requirements found for {workflow_type} phase {phase}, "
                "passing by default"
            )
            return (True, [])

        missing = []

        for field, spec in requirements.items():
            # Check field exists
            if field not in evidence:
                missing.append(
                    f"{field} (required: {spec.get('description', 'no description')})"
                )
                continue

            # Check type
            expected_type = spec.get("type", str)
            if not isinstance(evidence[field], expected_type):
                missing.append(
                    f"{field} (wrong type: expected {expected_type.__name__}, "
                    f"got {type(evidence[field]).__name__})"
                )
                continue

            # Check validator
            try:
                validator = spec.get("validator", lambda x: x is not None)
                if not validator(evidence[field]):
                    missing.append(
                        f"{field} (validation failed: {spec.get('description', '')})"
                    )
                    continue
            except Exception as e:
                missing.append(f"{field} (validation error: {str(e)})")
                continue

        passed = len(missing) == 0
        return (passed, missing)

    def _get_phase_content_from_rag(
        self, workflow_type: str, phase: int
    ) -> Dict[str, Any]:
        """Retrieve phase content from RAG engine.

        Args:
            workflow_type: Workflow type
            phase: Phase number

        Returns:
            Dictionary with phase content
        """
        query = f"{workflow_type} Phase {phase} requirements and instructions"

        try:
            result = self.rag_engine.search(
                query=query, n_results=5, filters={"phase": phase}
            )

            return {
                "phase_number": phase,
                "phase_name": f"Phase {phase}",
                "content_chunks": result.chunks,
                "total_tokens": result.total_tokens,
                "retrieval_method": result.retrieval_method,
            }

        except Exception as e:
            logger.error(f"Failed to retrieve phase content: {e}")
            return {
                "phase_number": phase,
                "phase_name": f"Phase {phase}",
                "error": str(e),
                "content_chunks": [],
            }

    def _format_phase_response(
        self, state: WorkflowState, phase: int
    ) -> Dict[str, Any]:
        """
        Format standard phase response.

        Args:
            state: Workflow state
            phase: Phase number

        Returns:
            Formatted response dictionary
        """
        phase_content = self._get_phase_content_from_rag(state.workflow_type, phase)

        return {
            "session_id": state.session_id,
            "workflow_type": state.workflow_type,
            "target_file": state.target_file,
            "current_phase": state.current_phase,
            "requested_phase": phase,
            "phase_content": phase_content,
            "artifacts_available": self._get_artifacts_summary(state),
            "completed_phases": state.completed_phases,
            "is_complete": state.is_complete(),
        }

    def _get_artifacts_summary(self, state: WorkflowState) -> Dict[int, Dict]:
        """
        Get summary of available artifacts from completed phases.

        Args:
            state: Workflow state

        Returns:
            Dictionary mapping phase to artifact summary
        """
        summary = {}
        for phase, artifact in state.phase_artifacts.items():
            summary[phase] = {
                "phase": artifact.phase_number,
                "evidence_fields": list(artifact.evidence.keys()),
                "outputs": artifact.outputs,
                "timestamp": artifact.timestamp.isoformat(),
            }
        return summary

    def _extract_commands_from_evidence(
        self, evidence: Dict[str, Any]
    ) -> List[CommandExecution]:
        """
        Extract command executions from evidence if present.

        Args:
            evidence: Evidence dictionary

        Returns:
            List of CommandExecution objects
        """
        commands = []

        # Look for command-related fields
        if "commands_executed" in evidence:
            cmd_data = evidence["commands_executed"]
            if isinstance(cmd_data, list):
                for cmd in cmd_data:
                    if isinstance(cmd, dict):
                        commands.append(CommandExecution.from_dict(cmd))

        return commands


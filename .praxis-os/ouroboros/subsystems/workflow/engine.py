"""
Workflow Engine: Orchestrator for phase-gated workflow execution.

Implements the WorkflowEngine interface from the Ouroboros spec, coordinating
all workflow subsystem components to provide session-based workflow execution.

Architecture:
- Accepts session_id parameters (public interface)
- Uses StateManager for session persistence
- Delegates phase gating to PhaseGates
- Delegates validation to EvidenceValidator + HiddenSchemas
- Delegates content rendering to WorkflowRenderer

This is the "glue" that connects all workflow components together.
"""

import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ouroboros.config.schemas.workflow import WorkflowConfig
from ouroboros.foundation.session_mapper import SessionMapper
from ouroboros.foundation.session_state_helper import SessionStateHelper
from ouroboros.subsystems.workflow.dynamic_registry import DynamicContentRegistry, DynamicRegistryError
from ouroboros.subsystems.workflow.evidence_validator import EvidenceValidator
from ouroboros.subsystems.workflow.guidance import add_workflow_guidance
from ouroboros.subsystems.workflow.hidden_schemas import HiddenSchemas
from ouroboros.subsystems.workflow.models import PhaseTimingInfo, WorkflowMetadata, WorkflowState
from ouroboros.subsystems.workflow.parsers import SpecTasksParser
from ouroboros.subsystems.workflow.phase_gates import PhaseAdvanceResult, PhaseGates
from ouroboros.subsystems.workflow.workflow_renderer import WorkflowRenderer
from ouroboros.utils.errors import ActionableError, WorkflowExecutionError

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Orchestrator for workflow execution.

    Implements the WorkflowEngine interface defined in the Ouroboros spec.
    Coordinates all workflow subsystem components to provide complete
    workflow lifecycle management.

    Architecture:
    - Public interface: session_id-based methods
    - Internal: Loads state via StateManager, delegates to components
    - State persistence: Automatic save after phase completion

    Components:
    - StateManager: Session state persistence
    - WorkflowRenderer: Metadata and content loading
    - PhaseGates: Sequential phase enforcement
    - EvidenceValidator: Multi-layer validation
    - HiddenSchemas: Evidence schema loading
    """

    def __init__(
        self,
        config: WorkflowConfig,
        base_path: Path,
        session_mapper: SessionMapper,
    ):
        """
        Initialize WorkflowEngine.

        Args:
            config: Workflow configuration
            base_path: Base path for resolving relative paths
            session_mapper: SessionMapper instance for generic state persistence

        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Session state helper (typed persistence via SessionMapper)
        self._state_helper = SessionStateHelper(
            session_mapper=session_mapper,
            invoker="workflow",
            state_model=WorkflowState
        )

        # Resolve workflows directory
        self.workflows_dir = base_path / config.workflows_dir

        if not self.workflows_dir.exists():
            raise ActionableError(
                what_failed="WorkflowEngine initialization",
                why_failed=f"Workflows directory does not exist: {self.workflows_dir}",
                how_to_fix=f"Create workflows directory at {self.workflows_dir} or update config.workflows_dir",
            )

        # Initialize stateless components
        self._renderer = WorkflowRenderer(self.workflows_dir)
        self._hidden_schemas = HiddenSchemas(self.workflows_dir)
        
        # Dynamic workflow content cache (RAM only, reconstructible from tasks.md)
        # NOT state - just parsed content for convenience
        self._dynamic_sessions: Dict[str, DynamicContentRegistry] = {}
        self._dynamic_lock = threading.RLock()

        logger.info("WorkflowEngine initialized", extra={"workflows_dir": str(self.workflows_dir)})

    # ========================================================================
    # Public Interface (matches Ouroboros spec)
    # ========================================================================

    def start_workflow(
        self, workflow_type: str, target_file: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Start new workflow session.

        Creates new session with initial state, loads workflow metadata,
        and returns session info with overview and first phase content.

        Args:
            workflow_type: Workflow identifier
            target_file: Optional target file being worked on
            **kwargs: Additional workflow options (stored in metadata)

        Returns:
            Dict with session_id, workflow overview, and initial phase content

        Raises:
            WorkflowExecutionError: If workflow not found
        """
        # Load workflow metadata
        try:
            metadata = self._renderer.load_metadata(workflow_type)
        except Exception as e:
            raise WorkflowExecutionError(
                what_failed=f"Starting workflow '{workflow_type}'",
                why_failed=f"Failed to load workflow metadata: {e}",
                how_to_fix=f"Check that workflow exists in {self.workflows_dir}/{workflow_type}/metadata.json",
            ) from e

        # Validate workflow-specific required options
        if metadata.required_options:
            missing = [opt for opt in metadata.required_options if opt not in kwargs]
            if missing:
                raise WorkflowExecutionError(
                    what_failed=f"Starting workflow '{workflow_type}'",
                    why_failed=f"Missing required workflow options: {missing}",
                    how_to_fix=f"Provide required options when starting workflow. "
                               f"Example: workflow_type='{workflow_type}', options={{{', '.join(f'{k}=\"...\"' for k in missing)}}}",
                )

        # Create new session
        target = target_file or "unknown"
        
        # Generate session ID via SessionMapper
        session_id = self._state_helper.session_mapper.create_session_id("workflow", conversation_id=None)
        
        # Initialize phase 0 timing
        now = datetime.now()
        initial_timing = {
            0: PhaseTimingInfo(
                phase=0,
                started_at=now,
                completed_at=None,
                duration_seconds=None
            )
        }
        
        # Create WorkflowState (subsystem-specific model)
        state = WorkflowState(
            session_id=session_id,
            workflow_type=workflow_type,
            target_file=target,
            current_phase=0,  # Start at Phase 0
            phase_timings=initial_timing,
            metadata=kwargs or {},
            completed_at=None,
        )
        
        # Save state via helper (automatic serialization)
        self._state_helper.save(state, status="active")

        # Note: Phase content is NOT included in response (just-in-time disclosure)
        # AI agents must explicitly call get_phase() to receive phase content

        logger.info(
            "Started workflow session",
            extra={
                "session_id": state.session_id,
                "workflow_type": workflow_type,
                "target_file": target,
                "current_phase": state.current_phase,
            },
        )

        response = {
            "session_id": state.session_id,
            "workflow_type": workflow_type,
            "target_file": target,
            "current_phase": state.current_phase,
            "workflow_overview": {
                "workflow_type": metadata.workflow_type,
                "version": metadata.version,
                "description": metadata.description,
                "max_phase": metadata.max_phase,
            },
            # phase_content removed for just-in-time disclosure (FR-001)
            # AI agents must explicitly call get_phase() to receive phase content
        }
        
        # Generate breadcrumb navigation to guide AI to next action
        breadcrumb = {
            "⚡_NEXT_ACTION": "get_phase(phase=0)",
        }
        
        return add_workflow_guidance(response, breadcrumb=breadcrumb)

    def get_phase(self, session_id: str, phase: int) -> Dict[str, Any]:
        """
        Get phase content and guidance.

        Loads session state, checks phase accessibility via phase gates,
        and returns phase content.

        Args:
            session_id: Session identifier
            phase: Phase number to retrieve

        Returns:
            Dict with phase metadata, tasks, guidance, and status

        Raises:
            WorkflowExecutionError: If session not found or phase not accessible
        """
        # Load state
        state = self._load_state(session_id)

        # Check if phase is accessible (phase gating)
        can_access, reason = self._can_advance(state, phase)
        if not can_access and phase != state.current_phase:
            raise WorkflowExecutionError(
                what_failed=f"Accessing phase {phase}",
                why_failed=reason,
                how_to_fix=f"Complete phase {state.current_phase} first.",
            )

        # Get phase content (route via dynamic registry if dynamic workflow)
        # Note: Phase 0 is always static (setup/analysis), even for dynamic workflows
        try:
            is_dynamic = self._is_dynamic(state)
            logger.info(
                f"get_phase: phase={phase}, phase_type={type(phase)}, is_dynamic={is_dynamic}, phase>0={phase > 0}"
            )
            
            if is_dynamic and phase > 0:
                # Dynamic workflow: parse from spec's tasks.md (phases 1+)
                logger.info(f"Using dynamic registry for phase {phase}")
                registry = self._get_or_create_dynamic_registry(session_id, state)
                phase_content = registry.get_phase_content(phase)
            else:
                # Static workflow OR Phase 0 (always static): load from filesystem
                logger.info(f"Using static renderer for phase {phase}")
                phase_content = self._renderer.get_phase_content(state.workflow_type, phase)  # type: ignore[assignment]
        except DynamicRegistryError as e:
            raise WorkflowExecutionError(
                what_failed=f"Getting phase {phase} content (dynamic)",
                why_failed=str(e),
                how_to_fix=e.how_to_fix,
            ) from e
        except Exception as e:
            raise WorkflowExecutionError(
                what_failed=f"Getting phase {phase} content",
                why_failed=f"Failed to load phase content: {e}",
                how_to_fix=f"Check that phase {phase} exists for workflow {state.workflow_type}",
            ) from e

        # Get phase status
        phase_status = self._get_phase_status(state, phase)

        response = {
            "session_id": session_id,
            "workflow_type": state.workflow_type,
            "phase": phase,
            "current_phase": state.current_phase,
            "phase_status": phase_status,
            "phase_content": phase_content,
        }
        
        # Generate task count aware breadcrumb (FR-002)
        task_count = self._get_task_count_for_phase(state, phase)
        
        if task_count is not None and task_count > 0:
            # Phase has tasks: guide to first task
            breadcrumb = {
                "📊_PHASE_INFO": f"Phase {phase} has {task_count} tasks",
                "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number=1)",
            }
        elif task_count == 0:
            # Edge case: Phase has no tasks, go straight to complete_phase
            breadcrumb = {
                "📊_PHASE_INFO": f"Phase {phase} has 0 tasks",
                "⚡_NEXT_ACTION": f"complete_phase(phase={phase}, evidence={{...}})",
            }
        else:
            # Task count retrieval failed (graceful degradation)
            # Provide generic guidance without specific task count
            breadcrumb = {
                "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number=1)",
            }
        
        return add_workflow_guidance(response, breadcrumb=breadcrumb)
    
    def get_task(self, session_id: str, phase: int, task_number: int) -> Dict[str, Any]:
        """
        Get individual task content.

        Loads session state, checks phase accessibility via phase gates,
        and returns specific task content.

        Args:
            session_id: Session identifier
            phase: Phase number
            task_number: Task number within phase

        Returns:
            Dict with task metadata and content

        Raises:
            WorkflowExecutionError: If session not found, phase not accessible, or task not found
        """
        # Load state
        state = self._load_state(session_id)

        # Check if phase is accessible (phase gating)
        can_access, reason = self._can_advance(state, phase)
        if not can_access and phase != state.current_phase:
            raise WorkflowExecutionError(
                what_failed=f"Accessing phase {phase}",
                why_failed=reason,
                how_to_fix=f"Complete phase {state.current_phase} first.",
            )

        # Get task content (route via dynamic registry if dynamic workflow)
        # Note: Phase 0 is always static (setup/analysis), even for dynamic workflows
        try:
            is_dynamic = self._is_dynamic(state)
            logger.info(
                f"get_task: phase={phase}, task_number={task_number}, phase_type={type(phase)}, task_type={type(task_number)}, is_dynamic={is_dynamic}, phase>0={phase > 0}"
            )
            
            if is_dynamic and phase > 0:
                # Dynamic workflow: parse from spec's tasks.md (phases 1+)
                logger.info(f"Using dynamic registry for phase {phase} task {task_number}")
                registry = self._get_or_create_dynamic_registry(session_id, state)
                task_content = registry.get_task_content(phase, task_number)
            else:
                # Static workflow OR Phase 0 (always static): load from filesystem
                logger.info(f"Using static renderer for phase {phase} task {task_number}")
                task_content = self._renderer.get_task_content(state.workflow_type, phase, task_number)  # type: ignore[assignment]
        except DynamicRegistryError as e:
            raise WorkflowExecutionError(
                what_failed=f"Getting task {task_number} in phase {phase} (dynamic)",
                why_failed=str(e),
                how_to_fix=e.how_to_fix,
            ) from e
        except Exception as e:
            raise WorkflowExecutionError(
                what_failed=f"Getting task {task_number} in phase {phase}",
                why_failed=f"Failed to load task content: {e}",
                how_to_fix=f"Check that task {task_number} exists in phase {phase} for workflow {state.workflow_type}",
            ) from e

        # Get phase status
        phase_status = self._get_phase_status(state, phase)

        response = {
            "session_id": session_id,
            "workflow_type": state.workflow_type,
            "phase": phase,
            "task_number": task_number,
            "current_phase": state.current_phase,
            "phase_status": phase_status,
            "task_content": task_content,
        }
        
        # Generate dynamic position-aware breadcrumb (FR-003)
        task_count = self._get_task_count_for_phase(state, phase)
        
        if task_count is not None:
            # Task count available: generate position-aware breadcrumb
            # API is 1-based: task_number ∈ [1, task_count]
            # Final task is when task_number == task_count
            if task_number < task_count:
                # Not the final task: guide to next task
                breadcrumb = {
                    "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count}",
                    "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})",
                }
            else:
                # Final task: guide to complete_phase
                breadcrumb = {
                    "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count} (final)",
                    "⚡_NEXT_ACTION": f"complete_phase(phase={phase}, evidence={{...}})",
                }
        else:
            # Task count retrieval failed (graceful degradation)
            # Provide generic position indicator without specific count
            breadcrumb = {
                "🎯_CURRENT_POSITION": f"Task {task_number}",
                "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})",
            }
        
        return add_workflow_guidance(response, breadcrumb=breadcrumb)

    def complete_phase(self, session_id: str, phase: int, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete phase with evidence submission.

        Validates evidence against hidden schema, advances phase if valid,
        and persists new state.

        Args:
            session_id: Session identifier
            phase: Phase to complete
            evidence: Evidence dictionary

        Returns:
            Dict with validation result and next phase info

        Raises:
            WorkflowExecutionError: If session not found or validation fails
        """
        # Load state
        state = self._load_state(session_id)

        # Get max phase for this workflow
        metadata = self._renderer.load_metadata(state.workflow_type)
        max_phase = metadata.max_phase
        
        # CRITICAL: For dynamic workflows, calculate max_phase from parsed tasks.md
        # Static workflows: max_phase is pre-calculated in metadata.json
        # Dynamic workflows: max_phase defaults to 0 in metadata, MUST calculate at runtime
        if metadata.dynamic_phases:
            try:
                registry = self._get_or_create_dynamic_registry(session_id, state)
                # Find highest phase_number in parsed phases
                if registry.content.phases:
                    max_phase = max(p.phase_number for p in registry.content.phases)
                    logger.debug(
                        "Dynamic workflow max_phase calculated",
                        extra={"session_id": session_id, "max_phase": max_phase}
                    )
            except Exception as e:
                logger.warning(
                    "Failed to calculate dynamic max_phase, using metadata default",
                    extra={"session_id": session_id, "error": str(e)}
                )

        # Create PhaseGates for validation
        evidence_validator = EvidenceValidator()
        phase_gates = PhaseGates(self._hidden_schemas, evidence_validator, max_phase)

        # Attempt to complete phase
        result = phase_gates.complete_phase(state, phase, evidence)

        # If successful, save new state
        if result.allowed and result.new_state:
            # Check if workflow is complete
            workflow_complete = result.new_state.current_phase > max_phase
            
            # Determine status (completed if workflow done, else active)
            new_status = "completed" if workflow_complete else "active"
            
            # If workflow is complete, mark completion timestamp
            final_state = result.new_state
            if workflow_complete:
                final_state = result.new_state.model_copy(update={"completed_at": datetime.now()})
            
            # Save via helper (automatic serialization)
            self._state_helper.save(final_state, status=new_status)
            
            logger.info(
                "Phase completed successfully",
                extra={
                    "session_id": session_id,
                    "completed_phase": phase,
                    "new_phase": result.new_state.current_phase,
                    "status": new_status,
                    "workflow_complete": workflow_complete,
                },
            )

            response = {
                "session_id": session_id,
                "success": True,
                "phase_completed": phase,
                "current_phase": result.new_state.current_phase,
                "workflow_complete": workflow_complete,
                "validation": result.validation_result.to_dict() if result.validation_result else None,
                "message": result.reason,
            }
            
            # Generate next phase or completion breadcrumb (FR-004)
            if workflow_complete:
                # Workflow complete: celebration breadcrumb (no next action)
                breadcrumb = {
                    "🎉_WORKFLOW_COMPLETE": f"All {max_phase + 1} phases completed successfully!",
                }
            else:
                # More phases remaining: guide to next phase
                next_phase = result.new_state.current_phase
                breadcrumb = {
                    "✅_PHASE_COMPLETE": f"Phase {phase} completed. Advanced to Phase {next_phase}.",
                    "⚡_NEXT_ACTION": f"get_phase(phase={next_phase})",
                }
            
            return add_workflow_guidance(response, breadcrumb=breadcrumb)
        else:
            logger.warning(
                "Phase completion failed",
                extra={
                    "session_id": session_id,
                    "phase": phase,
                    "reason": result.reason,
                },
            )
            response = {
                "session_id": session_id,
                "success": False,
                "phase_completed": None,
                "current_phase": state.current_phase,
                "validation": result.validation_result.to_dict() if result.validation_result else None,
                "message": result.reason,
            }
            return add_workflow_guidance(response)

    def validate_evidence(self, workflow_type: str, phase: int, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate evidence against hidden schema (stateless, for pre-validation).

        Useful for checking evidence before submission.

        Args:
            workflow_type: Workflow type
            phase: Phase number
            evidence: Evidence dictionary

        Returns:
            ValidationResult dict with detailed errors/warnings

        Raises:
            WorkflowExecutionError: If schema not found
        """
        try:
            schema = self._hidden_schemas.get_schema(workflow_type, phase)
        except Exception as e:
            raise WorkflowExecutionError(
                what_failed=f"Validating evidence for {workflow_type} phase {phase}",
                why_failed=f"Failed to load evidence schema: {e}",
                how_to_fix=f"Check that workflow {workflow_type} has a schema for phase {phase}",
            ) from e

        evidence_validator = EvidenceValidator()
        validation_result = evidence_validator.validate(evidence, schema)
        return validation_result.to_dict()

    # ========================================================================
    # Additional Utility Methods
    # ========================================================================

    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all available workflows.

        Returns:
            List of workflow info dicts
        """
        workflows = []

        try:
            workflows_dict = self._renderer.list_workflows()
            for workflow_type, metadata in workflows_dict.items():
                workflows.append(
                    {
                        "workflow_type": workflow_type,
                        "version": metadata.version,
                        "description": metadata.description,
                        "max_phase": metadata.max_phase,
                    }
                )

            return workflows

        except Exception as e:
            raise ActionableError(
                what_failed="list_workflows",
                why_failed=str(e),
                how_to_fix="Check that workflows directory is readable and contains valid workflow definitions",
            ) from e

    def get_workflow_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get current workflow state.

        Args:
            session_id: Session identifier

        Returns:
            WorkflowState as dict

        Raises:
            WorkflowExecutionError: If session not found
        """
        state = self._load_state(session_id)
        response = state.model_dump(mode="json")
        return add_workflow_guidance(response)

    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all workflow sessions.

        Args:
            status: Optional filter ("active", "completed", "error", or None for all)

        Returns:
            List of session summaries with workflow details
        """
        # Get enriched sessions via helper (auto load/deserialize)
        enriched_sessions = self._state_helper.list_sessions(status=status, enrich=True)
        
        # Add workflow-specific "is_complete" field
        sessions = []
        for meta in enriched_sessions:
            state: WorkflowState = meta["state"]
            
            # Determine if workflow is complete (same logic as old StateManager)
            # Workflow is complete if current_phase exceeds the highest completed phase
            is_complete = False
            if state.completed_phases:
                is_complete = state.current_phase > max(state.completed_phases)
            
            sessions.append({
                "session_id": state.session_id,
                "workflow_type": state.workflow_type,
                "target_file": state.target_file,
                "current_phase": state.current_phase,
                "completed_phases": state.completed_phases,
                "updated_at": state.updated_at.isoformat(),
                "status": meta["status"],
                "is_complete": is_complete,
            })
        
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete workflow session.
        
        Moves session to "error" status with "manually_deleted" reason.
        Will be cleaned up automatically by background cleanup task.

        Args:
            session_id: Session to delete

        Returns:
            True if deleted (moved to error), False if not found
        """
        # Delete via helper (marks as error for cleanup)
        return self._state_helper.delete(session_id, reason="manually_deleted")

    # ========================================================================
    # Internal Helper Methods
    # ========================================================================
    
    def _is_dynamic(self, state: WorkflowState) -> bool:
        """
        Check if workflow uses dynamic content (parsed from spec's tasks.md).
        
        Args:
            state: Workflow state
            
        Returns:
            True if workflow has dynamic phases
        """
        # Load workflow metadata to check dynamic_phases flag
        try:
            workflow_metadata = self._renderer.load_metadata(state.workflow_type)
            return workflow_metadata.dynamic_phases
        except Exception:
            return False
    
    def _get_or_create_dynamic_registry(
        self, session_id: str, state: WorkflowState
    ) -> DynamicContentRegistry:
        """
        Get or create dynamic content registry for session (RAM cache).
        
        This is a content cache (NOT state) - parsed content from spec's tasks.md
        that stays in RAM for convenience. Can be reconstructed anytime.
        
        Args:
            session_id: Session identifier
            state: Workflow state (contains spec_path in metadata)
            
        Returns:
            DynamicContentRegistry instance
            
        Raises:
            DynamicRegistryError: If parsing or template loading fails
        """
        with self._dynamic_lock:
            # Return cached if exists
            if session_id in self._dynamic_sessions:
                return self._dynamic_sessions[session_id]
            
            # Create new registry
            try:
                # Get spec path from metadata
                spec_path = state.metadata.get("spec_path")
                if not spec_path:
                    raise DynamicRegistryError(
                        "Dynamic workflow missing 'spec_path' in metadata. "
                        "Provide spec_path in options when starting workflow."
                    )
                
                spec_path = Path(spec_path)
                source_path = spec_path / "tasks.md"
                
                if not source_path.exists():
                    raise DynamicRegistryError(
                        f"Spec tasks.md not found: {source_path}. "
                        f"Dynamic workflows require a tasks.md file in the spec directory."
                    )
                
                # Get template paths
                workflow_dir = self.workflows_dir / state.workflow_type
                phase_template_path = workflow_dir / "phases" / "dynamic" / "phase-template.md"
                task_template_path = workflow_dir / "phases" / "dynamic" / "task-template.md"
                
                if not phase_template_path.exists():
                    raise DynamicRegistryError(
                        f"Phase template not found: {phase_template_path}. "
                        f"Dynamic workflows require phase-template.md in phases/dynamic/"
                    )
                
                if not task_template_path.exists():
                    raise DynamicRegistryError(
                        f"Task template not found: {task_template_path}. "
                        f"Dynamic workflows require task-template.md in phases/dynamic/"
                    )
                
                # Create parser
                parser = SpecTasksParser()
                
                # Create and cache registry
                registry = DynamicContentRegistry(
                    workflow_type=state.workflow_type,
                    phase_template_path=phase_template_path,
                    task_template_path=task_template_path,
                    source_path=source_path,
                    parser=parser,
                )
                
                self._dynamic_sessions[session_id] = registry
                logger.info(
                    "Created dynamic content registry",
                    extra={"session_id": session_id, "source": str(source_path)}
                )
                
                return registry
                
            except DynamicRegistryError:
                raise
            except Exception as e:
                raise DynamicRegistryError(
                    f"Failed to create dynamic content registry: {e}"
                ) from e

    def _get_task_count_for_phase(self, state: WorkflowState, phase: int) -> Optional[int]:
        """
        Get the number of tasks in a phase, routing to appropriate backend.

        This helper routes task count retrieval based on workflow type:
        - Static workflows: Count task files via WorkflowRenderer.get_task_count()
        - Dynamic workflows: Get cached count from DynamicContentRegistry.get_phase_metadata()

        **Graceful Degradation:** If task count retrieval fails, returns None and logs error.
        This allows workflows to continue execution without breadcrumb navigation rather than
        failing completely. Breadcrumbs are a UX enhancement, not a critical requirement.

        Args:
            state: Workflow state containing workflow_type and metadata
            phase: Phase number (0-based indexing)

        Returns:
            Number of tasks in the phase, or None if retrieval fails.
            None indicates breadcrumb generation should be skipped for this action.

        Note:
            - Thread-safe (no shared state modification)
            - Never raises exceptions (fail-safe design)
            - Errors logged at ERROR level for monitoring
        """
        try:
            # Check if workflow uses dynamic content
            if self._is_dynamic(state):
                # Dynamic workflow: Get from registry
                # Note: Dynamic registry caches task_count during parsing
                registry = self._get_or_create_dynamic_registry(state.session_id, state)
                phase_metadata = registry.get_phase_metadata(phase)
                task_count = phase_metadata.get("task_count")
                
                logger.debug(
                    "Task count retrieved from dynamic registry",
                    extra={"workflow_type": state.workflow_type, "phase": phase, "task_count": task_count},
                )
                
                return task_count
            else:
                # Static workflow: Count files via renderer
                task_count = self._renderer.get_task_count(state.workflow_type, phase)
                
                logger.debug(
                    "Task count retrieved from static renderer",
                    extra={"workflow_type": state.workflow_type, "phase": phase, "task_count": task_count},
                )
                
                return task_count

        except Exception as e:
            # Graceful degradation: Log error, return None
            # Workflow continues without breadcrumb navigation
            logger.error(
                "Failed to retrieve task count for phase (breadcrumb navigation disabled for this action)",
                extra={
                    "workflow_type": state.workflow_type,
                    "phase": phase,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            return None

    def _load_state(self, session_id: str) -> WorkflowState:
        """Load session state, raise error if not found."""
        # Load via helper (automatic deserialization)
        state = self._state_helper.load(session_id)
        
        if state is None:
            raise WorkflowExecutionError(
                what_failed=f"Loading session '{session_id}'",
                why_failed="Session not found",
                how_to_fix=f"Check session_id. Use list_sessions() to see active sessions.",
            )
        
        return state

    def _can_advance(self, state: WorkflowState, target_phase: int) -> Tuple[bool, str]:
        """Check if phase advancement is allowed."""
        try:
            metadata = self._renderer.load_metadata(state.workflow_type)
            max_phase = metadata.max_phase

            evidence_validator = EvidenceValidator()
            phase_gates = PhaseGates(self._hidden_schemas, evidence_validator, max_phase)

            return phase_gates.can_advance(state, target_phase)

        except Exception as e:
            logger.error("_can_advance failed: %s", e, exc_info=True)
            return (False, f"Internal error: {e}")

    def _get_phase_status(self, state: WorkflowState, phase: int) -> Dict[str, Any]:
        """Get status of a specific phase."""
        try:
            metadata = self._renderer.load_metadata(state.workflow_type)
            max_phase = metadata.max_phase

            evidence_validator = EvidenceValidator()
            phase_gates = PhaseGates(self._hidden_schemas, evidence_validator, max_phase)

            return phase_gates.get_phase_status(state, phase)

        except Exception as e:
            logger.error("_get_phase_status failed: %s", e, exc_info=True)
            return {
                "phase": phase,
                "is_completed": False,
                "is_current": False,
                "accessible": False,
                "checkpoint_status": "unknown",
                "error": str(e),
            }


__all__ = ["WorkflowEngine"]

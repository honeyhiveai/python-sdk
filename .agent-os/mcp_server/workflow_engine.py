"""
Workflow Engine for Phase Gating and Checkpoint Validation.

Enforces architectural constraints for sequential workflow execution.
100% AI-authored via human orchestration.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable

from .models import (
    WorkflowState, 
    PhaseArtifact, 
    CheckpointStatus, 
    CommandExecution,
    WorkflowMetadata,
    PhaseMetadata,
)
from .state_manager import StateManager
from .rag_engine import RAGEngine
from .core.session import WorkflowSession

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
        workflows_base_path: Optional[Path] = None,
    ):
        """
        Initialize workflow engine.

        Args:
            state_manager: State manager for persistence
            rag_engine: RAG engine for content retrieval
            checkpoint_loader: Optional custom checkpoint loader
            workflows_base_path: Base path for workflow metadata files
        """
        self.state_manager = state_manager
        self.rag_engine = rag_engine
        self.checkpoint_loader = checkpoint_loader or CheckpointLoader(rag_engine)
        
        # Determine workflows base path (default to universal/workflows)
        if workflows_base_path is None:
            # Try to find workflows directory relative to this file
            current_dir = Path(__file__).parent
            self.workflows_base_path = current_dir.parent / "universal" / "workflows"
        else:
            self.workflows_base_path = workflows_base_path
        
        # Cache for loaded workflow metadata
        self._metadata_cache: Dict[str, WorkflowMetadata] = {}
        
        # Session cache for session-scoped workflow execution
        self._sessions: Dict[str, WorkflowSession] = {}

        logger.info("WorkflowEngine initialized")

    def load_workflow_metadata(self, workflow_type: str) -> WorkflowMetadata:
        """
        Load workflow metadata from metadata.json file.
        
        Provides upfront overview information including total phases, phase names,
        purposes, and expected outputs. Falls back to generating metadata from
        phase discovery if metadata.json doesn't exist.
        
        Args:
            workflow_type: Workflow type (e.g., "test_generation_v3")
        
        Returns:
            WorkflowMetadata with complete workflow overview
        """
        # Check cache first
        if workflow_type in self._metadata_cache:
            logger.debug(f"Workflow metadata cache hit for {workflow_type}")
            return self._metadata_cache[workflow_type]
        
        # Try to load from metadata.json
        metadata_path = self.workflows_base_path / workflow_type / "metadata.json"
        
        if metadata_path.exists():
            logger.info(f"Loading workflow metadata from {metadata_path}")
            try:
                with open(metadata_path, 'r') as f:
                    metadata_dict = json.load(f)
                metadata = WorkflowMetadata.from_dict(metadata_dict)
                
                # Cache the metadata
                self._metadata_cache[workflow_type] = metadata
                
                logger.info(
                    f"Loaded metadata for {workflow_type}: "
                    f"{metadata.total_phases} phases, {len(metadata.phases)} phase definitions"
                )
                return metadata
            except Exception as e:
                logger.warning(
                    f"Failed to load metadata.json for {workflow_type}: {e}. "
                    "Falling back to generated metadata."
                )
        
        # Fallback: Generate metadata from known workflow types
        logger.info(f"Generating fallback metadata for {workflow_type}")
        metadata = self._generate_fallback_metadata(workflow_type)
        
        # Cache the generated metadata
        self._metadata_cache[workflow_type] = metadata
        
        return metadata
    
    def _generate_fallback_metadata(self, workflow_type: str) -> WorkflowMetadata:
        """
        Generate fallback metadata for workflows without metadata.json.
        
        Uses hardcoded knowledge of standard workflow structures for backward
        compatibility. This ensures existing workflows continue to work.
        
        Args:
            workflow_type: Workflow type
        
        Returns:
            Generated WorkflowMetadata
        """
        # Known workflow structures
        if "test" in workflow_type.lower():
            # Test generation workflow (8 phases)
            return WorkflowMetadata(
                workflow_type=workflow_type,
                version="unknown",
                description="Test generation workflow (auto-generated metadata)",
                total_phases=8,
                estimated_duration="2-3 hours",
                primary_outputs=["test files", "coverage report"],
                phases=[
                    PhaseMetadata(
                        phase_number=i,
                        phase_name=f"Phase {i}",
                        purpose=f"Phase {i} tasks",
                        estimated_effort="Variable",
                        key_deliverables=[],
                        validation_criteria=[],
                    )
                    for i in range(0, 8)
                ],
            )
        else:
            # Production code workflow (6 phases)
            return WorkflowMetadata(
                workflow_type=workflow_type,
                version="unknown",
                description="Production code workflow (auto-generated metadata)",
                total_phases=6,
                estimated_duration="1-2 hours",
                primary_outputs=["production code", "documentation"],
                phases=[
                    PhaseMetadata(
                        phase_number=i,
                        phase_name=f"Phase {i}",
                        purpose=f"Phase {i} tasks",
                        estimated_effort="Variable",
                        key_deliverables=[],
                        validation_criteria=[],
                    )
                    for i in range(0, 6)
                ],
            )
    
    def get_session(self, session_id: str) -> WorkflowSession:
        """
        Get or create WorkflowSession instance.
        
        Implements session factory pattern - caches sessions for performance
        and initializes dynamic content registry if applicable.
        
        Args:
            session_id: Session identifier
            
        Returns:
            WorkflowSession instance
            
        Raises:
            ValueError: If session not found in state manager
        """
        # Check cache first
        if session_id in self._sessions:
            logger.debug(f"Session cache hit for {session_id}")
            return self._sessions[session_id]
        
        # Load state from persistence
        state = self.state_manager.load_state(session_id)
        if state is None:
            raise ValueError(f"Session {session_id} not found")
        
        # Load metadata for this workflow type
        metadata = self.load_workflow_metadata(state.workflow_type)
        
        # Create session with all dependencies
        session = WorkflowSession(
            session_id=session_id,
            workflow_type=state.workflow_type,
            target_file=state.target_file,
            state=state,
            rag_engine=self.rag_engine,
            state_manager=self.state_manager,
            workflows_base_path=self.workflows_base_path,
            metadata=metadata,
            options=state.metadata,  # Pass session metadata as options
        )
        
        # Cache session
        self._sessions[session_id] = session
        
        logger.info(
            f"Created session {session_id} for workflow {state.workflow_type} "
            f"(dynamic={session._is_dynamic()})"
        )
        
        return session

    def start_workflow(
        self, workflow_type: str, target_file: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Start new workflow session with phase gating.
        
        Now creates WorkflowSession immediately for session-scoped execution.
        Initializes dynamic content registry if workflow is dynamic.

        Args:
            workflow_type: Workflow type (e.g., "test_generation_v3")
            target_file: File being worked on
            metadata: Optional additional metadata (may include spec_path for dynamic workflows)

        Returns:
            Dictionary with session info, workflow overview, and Phase 0 content
        """
        # Load workflow metadata for overview
        workflow_metadata = self.load_workflow_metadata(workflow_type)
        
        # Check for existing active session
        existing = self.state_manager.get_active_session(workflow_type, target_file)
        if existing:
            logger.info(
                f"Resuming existing session {existing.session_id} for {target_file}"
            )
            # Get or create session instance
            session = self.get_session(existing.session_id)
            # Delegate to session
            response = session.get_current_phase()
            # Add workflow overview to resumed session
            response["workflow_overview"] = workflow_metadata.to_dict()
            return response

        # Create new session state (state_manager detects starting phase dynamically)
        state = self.state_manager.create_session(workflow_type, target_file, metadata)

        logger.info(
            f"Started workflow {workflow_type} session {state.session_id} "
            f"for {target_file} at Phase {state.current_phase}"
        )

        # Create session instance immediately (handles dynamic registry initialization)
        session = WorkflowSession(
            session_id=state.session_id,
            workflow_type=workflow_type,
            target_file=target_file,
            state=state,
            rag_engine=self.rag_engine,
            state_manager=self.state_manager,
            workflows_base_path=self.workflows_base_path,
            metadata=workflow_metadata,
            options=metadata,
        )
        
        # Cache session
        self._sessions[state.session_id] = session
        
        logger.info(
            f"Created session instance {state.session_id} "
            f"(dynamic={session._is_dynamic()})"
        )

        # Return initial phase content (delegates to session)
        response = session.get_current_phase()
        response["workflow_overview"] = workflow_metadata.to_dict()
        
        return response

    def get_current_phase(self, session_id: str) -> Dict[str, Any]:
        """
        Get current phase content for session.
        
        Now delegates to WorkflowSession for dynamic content support.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with current phase content

        Raises:
            ValueError: If session not found
        """
        # Get or create session instance
        session = self.get_session(session_id)
        
        # Delegate to session (handles dynamic registry if applicable)
        return session.get_current_phase()

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
        
        Now delegates to WorkflowSession and handles cleanup on completion.

        Args:
            session_id: Session identifier
            phase: Phase to complete
            evidence: Evidence dictionary for checkpoint validation

        Returns:
            Result with pass/fail and next phase content if passed

        Raises:
            ValueError: If session not found or phase mismatch
        """
        # Get or create session instance
        session = self.get_session(session_id)
        
        # Delegate to session (handles dynamic registry if applicable)
        result = session.complete_phase(phase, evidence)
        
        # Check if workflow is complete and cleanup session
        if result.get("workflow_complete", False):
            logger.info(f"Workflow complete for session {session_id}, cleaning up")
            session.cleanup()
            # Remove from cache
            if session_id in self._sessions:
                del self._sessions[session_id]
        
        return result

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

    def get_task(
        self, session_id: str, phase: int, task_number: int
    ) -> Dict[str, Any]:
        """
        Get full content for a specific task (horizontal scaling - one task at a time).
        
        Now delegates to WorkflowSession for dynamic content support.

        Args:
            session_id: Session identifier
            phase: Phase number
            task_number: Task number within the phase

        Returns:
            Dictionary with complete task content and execution steps
        """
        # Get or create session instance
        session = self.get_session(session_id)
        
        # Delegate to session (handles dynamic registry if applicable)
        return session.get_task(phase, task_number)

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
        """Retrieve phase overview with task metadata (no full task content).

        Args:
            workflow_type: Workflow type
            phase: Phase number

        Returns:
            Dictionary with phase overview and task metadata list
        """
        try:
            # Query 1: General phase requirements and methodology
            general_query = f"{workflow_type} Phase {phase} requirements instructions methodology"
            general_result = self.rag_engine.search(
                query=general_query, n_results=3, filters={"phase": phase}
            )
            
            # Query 2: Discover available tasks in this phase
            task_query = f"{workflow_type} Phase {phase} task list files"
            task_result = self.rag_engine.search(
                query=task_query, n_results=20, filters={"phase": phase}
            )
            
            # Extract task metadata (no full content)
            tasks_metadata = self._extract_task_metadata_from_chunks(
                task_result.chunks, workflow_type, phase
            )

            return {
                "phase_number": phase,
                "phase_name": f"Phase {phase}",
                "content_chunks": general_result.chunks,  # General guidance only
                "tasks": tasks_metadata,  # Metadata only: task numbers, names, files
                "total_tokens": general_result.total_tokens,
                "retrieval_method": general_result.retrieval_method,
                "message": "Use get_task(session_id, phase, task_number) to retrieve full task content",
            }

        except Exception as e:
            logger.error(f"Failed to retrieve phase content: {e}")
            return {
                "phase_number": phase,
                "phase_name": f"Phase {phase}",
                "error": str(e),
                "content_chunks": [],
                "tasks": [],
            }
    
    def _get_task_content_from_rag(
        self, workflow_type: str, phase: int, task_number: int
    ) -> Dict[str, Any]:
        """
        Retrieve complete content for a specific task from RAG.
        
        Uses targeted query to get ALL chunks for the task file to ensure completeness.
        
        Args:
            workflow_type: Workflow type
            phase: Phase number
            task_number: Task number
        
        Returns:
            Dictionary with complete task content and execution steps
        """
        try:
            # Targeted query for this specific task
            # Use task number in query to find the right task file
            task_query = f"{workflow_type} Phase {phase} task {task_number} task-{task_number}- EXECUTE-NOW commands steps"
            
            # Request many chunks to ensure we get the COMPLETE task
            # A typical task file might be split into 3-8 chunks
            result = self.rag_engine.search(
                query=task_query, 
                n_results=50,  # High number to ensure completeness
                filters={"phase": phase}
            )
            
            # Filter to only chunks from the specific task file
            task_file_pattern = f"task-{task_number}-"
            task_chunks = [
                chunk for chunk in result.chunks 
                if task_file_pattern in chunk.get("file_path", "")
            ]
            
            if not task_chunks:
                return {
                    "phase": phase,
                    "task_number": task_number,
                    "error": f"Task {task_number} not found in Phase {phase}",
                    "content": "",
                    "steps": [],
                }
            
            # Get task file path from first chunk
            task_file = task_chunks[0].get("file_path", "")
            
            # Sort chunks by position in file (if available) to maintain order
            task_chunks.sort(key=lambda c: c.get("start_line", 0))
            
            # Combine ALL chunks to get complete content
            full_content = "\n\n".join(chunk.get("content", "") for chunk in task_chunks)
            
            # Extract task name from first chunk or filename
            task_name = task_chunks[0].get("section_header", "")
            if not task_name:
                first_line = full_content.split("\n")[0].strip("#").strip()
                task_name = first_line if first_line else f"Task {task_number}"
            
            # Extract execution steps from complete content
            steps = self._extract_steps_from_content(full_content)
            
            logger.info(
                f"Retrieved complete task {task_number} for {workflow_type} Phase {phase}: "
                f"{len(task_chunks)} chunks, {len(full_content)} chars, {len(steps)} steps"
            )
            
            return {
                "phase": phase,
                "task_number": task_number,
                "task_name": task_name,
                "task_file": task_file,
                "content": full_content,  # COMPLETE task content
                "steps": steps,  # Extracted commands and decision points
                "chunks_retrieved": len(task_chunks),  # For debugging
                "total_tokens": sum(chunk.get("tokens", 0) for chunk in task_chunks),
                "retrieval_method": result.retrieval_method,
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve task {task_number}: {e}")
            return {
                "phase": phase,
                "task_number": task_number,
                "error": str(e),
                "content": "",
                "steps": [],
            }
    
    def _extract_task_metadata_from_chunks(
        self, chunks: List[Dict[str, Any]], workflow_type: str, phase: int
    ) -> List[Dict[str, Any]]:
        """
        Extract task metadata (no full content) from RAG chunks.
        
        Groups chunks by task file and extracts only metadata.
        
        Args:
            chunks: RAG search result chunks
            workflow_type: Workflow type
            phase: Phase number
        
        Returns:
            List of task metadata dictionaries (no full content)
        """
        import re
        
        # Group chunks by file to identify unique tasks
        tasks_by_file = {}
        
        for chunk in chunks:
            file_path = chunk.get("file_path", "")
            
            # Only process task files (task-1-*.md, task-2-*.md, etc.)
            if "task-" in file_path and file_path.endswith(".md"):
                if file_path not in tasks_by_file:
                    # Extract task number from filename
                    task_match = re.search(r'task-(\d+)-', file_path)
                    task_number = int(task_match.group(1)) if task_match else 0
                    
                    # Extract task name from first chunk's header
                    task_name = chunk.get("section_header", "")
                    if not task_name:
                        content = chunk.get("content", "")
                        first_line = content.split("\n")[0].strip("#").strip() if content else ""
                        task_name = first_line if first_line else f"Task {task_number}"
                    
                    tasks_by_file[file_path] = {
                        "task_number": task_number,
                        "task_name": task_name,
                        "task_file": file_path,
                    }
        
        # Sort by task number
        tasks_metadata = sorted(tasks_by_file.values(), key=lambda t: t["task_number"])
        
        logger.info(f"Found {len(tasks_metadata)} tasks in {workflow_type} Phase {phase}")
        
        return tasks_metadata
    
    def _structure_tasks_from_chunks(
        self, chunks: List[Dict[str, Any]], workflow_type: str, phase: int
    ) -> List[Dict[str, Any]]:
        """
        Structure task information from RAG chunks.
        
        Groups chunks by task file and extracts task information.
        
        Args:
            chunks: RAG search result chunks
            workflow_type: Workflow type
            phase: Phase number
        
        Returns:
            List of structured task dictionaries
        """
        # Group chunks by file (each task file becomes a task)
        tasks_by_file = {}
        
        for chunk in chunks:
            file_path = chunk.get("file_path", "")
            
            # Only process task files (task-1-*.md, task-2-*.md, etc.)
            if "task-" in file_path and file_path.endswith(".md"):
                if file_path not in tasks_by_file:
                    tasks_by_file[file_path] = {
                        "task_file": file_path,
                        "chunks": [],
                    }
                tasks_by_file[file_path]["chunks"].append(chunk)
        
        # Convert to structured tasks
        tasks = []
        for task_file, task_data in sorted(tasks_by_file.items()):
            task = self._extract_task_structure(task_file, task_data["chunks"])
            if task:
                tasks.append(task)
        
        logger.info(f"Structured {len(tasks)} tasks from {len(chunks)} RAG chunks for {workflow_type} Phase {phase}")
        
        return tasks
    
    def _extract_task_structure(
        self, task_file: str, chunks: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract structured task information from RAG chunks.
        
        Args:
            task_file: Path to task file
            chunks: RAG chunks from this task file
        
        Returns:
            Structured task dictionary or None
        """
        if not chunks:
            return None
        
        # Extract task number from filename (task-1-name.md -> 1)
        import re
        task_match = re.search(r'task-(\d+)-', task_file)
        task_number = int(task_match.group(1)) if task_match else 0
        
        # Combine all chunk content
        full_content = "\n\n".join(chunk.get("content", "") for chunk in chunks)
        
        # Extract task name from first chunk's section header or content
        task_name = chunks[0].get("section_header", "")
        if not task_name:
            # Try to extract from first line of content
            first_line = full_content.split("\n")[0].strip("#").strip()
            task_name = first_line if first_line else f"Task {task_number}"
        
        # Extract commands (look for code blocks and EXECUTE-NOW markers)
        steps = self._extract_steps_from_content(full_content)
        
        return {
            "task_number": task_number,
            "task_name": task_name,
            "task_file": task_file,
            "content": full_content,  # Full task content for reference
            "steps": steps,  # Extracted execution steps
            "chunks": [
                {
                    "content": chunk.get("content", ""),
                    "section": chunk.get("section_header", ""),
                    "tokens": chunk.get("tokens", 0),
                }
                for chunk in chunks
            ],
        }
    
    def _extract_steps_from_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract execution steps from task content.
        
        Looks for command patterns like:
        - 🛑 EXECUTE-NOW
        - ```bash code blocks
        - 📊 COUNT-AND-DOCUMENT
        
        Args:
            content: Task content markdown
        
        Returns:
            List of step dictionaries
        """
        steps = []
        import re
        
        # Find all bash code blocks with context
        # Pattern: Finds EXECUTE-NOW markers followed by bash blocks
        execute_pattern = r'🛑\s*EXECUTE-NOW[:\s]*([^\n]*)\n```(?:bash|shell)?\n(.*?)\n```'
        
        for match in re.finditer(execute_pattern, content, re.DOTALL):
            description = match.group(1).strip() or "Execute command"
            command = match.group(2).strip()
            
            # Look for evidence markers after this command
            evidence = None
            after_match = content[match.end():match.end()+500]
            evidence_match = re.search(r'📊\s*COUNT-AND-DOCUMENT[:\s]*([^\n]*)', after_match)
            if evidence_match:
                evidence = evidence_match.group(1).strip()
            
            steps.append({
                "description": description,
                "type": "execute_command",
                "command": command,
                "evidence_required": evidence,
            })
        
        # Also find QUERY-AND-DECIDE sections (branching logic)
        query_pattern = r'🔍\s*QUERY-AND-DECIDE[:\s]*([^\n]*)'
        for match in re.finditer(query_pattern, content):
            steps.append({
                "description": match.group(1).strip(),
                "type": "decision_point",
                "requires_analysis": True,
            })
        
        return steps

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


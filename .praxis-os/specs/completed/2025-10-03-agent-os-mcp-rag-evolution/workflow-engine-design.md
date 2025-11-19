# Workflow Engine Design
# Agent OS MCP/RAG Evolution

**Document Version:** 1.0  
**Date:** October 3, 2025  
**Status:** Draft - Specification Phase

---

## PURPOSE

This document details the **workflow engine design** that implements architectural phase gating, replacing documentary enforcement with structural constraints.

---

## CORE CONCEPT

### Current Problem: Documentary Enforcement

```python
current_approach = {
    "mechanism": "Framework documents say 'complete phases in order'",
    "enforcement": "User catches when AI skips phases",
    "ai_behavior": "AI sees all phases, tempted to skip",
    "corrections_needed": "5 per session (AI Perspective doc)"
}
```

### Solution: Architectural Enforcement

```python
workflow_engine_approach = {
    "mechanism": "Engine controls what AI can access",
    "enforcement": "AI literally cannot see Phase N+1 until Phase N done",
    "ai_behavior": "AI cannot skip (structurally impossible)",
    "corrections_needed": "0 for phase skipping"
}
```

---

## ARCHITECTURE

### Component Structure

```
WorkflowEngine
├── Phase Gating Logic
│   ├── Access Control: can_access_phase(N)
│   ├── Content Delivery: get_phase_content(N)
│   └── Progression: advance_to_next_phase()
│
├── Checkpoint System
│   ├── Evidence Requirements: get_checkpoint_criteria(N)
│   ├── Validation: validate_evidence(evidence, criteria)
│   └── Pass/Fail: checkpoint_passed(N)
│
├── State Management
│   ├── Current State: get_workflow_state(session_id)
│   ├── Persistence: save_state() / load_state()
│   └── Artifact Passing: get_artifacts_for_phase(N)
│
└── Error Handling
    ├── Sequence Violations: phase_sequence_error()
    ├── Missing Evidence: evidence_missing_error()
    └── Graceful Recovery: recover_from_error()
```

---

## PHASE GATING MECHANISM

### Access Control Algorithm

```python
def can_access_phase(session_id: str, requested_phase: int) -> bool:
    """
    Determine if AI can access requested phase.
    
    Rules:
    1. Can ONLY access current_phase
    2. Cannot skip ahead to current_phase + 2 or more
    3. Cannot go backward (but can review completed)
    
    Returns:
        True if requested_phase == current_phase OR requested_phase in completed
        False otherwise
    """
    state = load_state(session_id)
    
    # Can access current phase
    if requested_phase == state.current_phase:
        return True
    
    # Can review completed phases
    if requested_phase in state.completed_phases:
        return True
    
    # Cannot access future phases
    return False
```

### Content Delivery

```python
def get_phase_content(session_id: str, requested_phase: int) -> Dict[str, Any]:
    """
    Get content for requested phase with gating enforcement.
    
    Behavior:
    - If allowed: Return phase content
    - If denied: Return error + current phase content
    """
    if not can_access_phase(session_id, requested_phase):
        return {
            "error": "Phase sequence violation",
            "message": f"Complete Phase {state.current_phase} first",
            "violation_type": "attempted_skip",
            "current_phase_content": load_phase_content(state.current_phase),
            "artifacts_available": get_artifacts(state)
        }
    
    # Allowed - return requested content
    content = load_phase_content(requested_phase)
    artifacts = get_artifacts(state) if requested_phase == state.current_phase else {}
    
    return {
        "phase_number": requested_phase,
        "phase_content": content,
        "artifacts_from_previous": artifacts,
        "checkpoint_criteria": get_checkpoint_criteria(requested_phase)
    }
```

---

## CHECKPOINT SYSTEM

### Evidence Requirements - Dynamic Loading

**Critical:** Checkpoint requirements are **loaded dynamically from Agent OS documents**, not hardcoded.

```python
class CheckpointLoader:
    """
    Load checkpoint requirements dynamically from Agent OS standards.
    
    Aligns with project principle: dynamic logic over static patterns.
    """
    
    def __init__(self, rag_engine: RAGEngine):
        self.rag_engine = rag_engine
        self._checkpoint_cache = {}
    
    def load_checkpoint_requirements(self, workflow_type: str, phase: int) -> Dict[str, Any]:
        """
        Load checkpoint requirements from Agent OS documents dynamically.
        
        Instead of hardcoded CHECKPOINT_DEFINITIONS, parse from actual framework docs.
        """
        cache_key = f"{workflow_type}_phase_{phase}"
        
        if cache_key in self._checkpoint_cache:
            return self._checkpoint_cache[cache_key]
        
        # Query RAG for checkpoint section of this phase
        query = f"{workflow_type} Phase {phase} checkpoint requirements evidence"
        result = self.rag_engine.search(
            query=query,
            filter_phase=phase,
            filter_tags=["checkpoint", "evidence"],
            n_results=3
        )
        
        # Parse checkpoint requirements from retrieved content
        requirements = self._parse_checkpoint_requirements(result.chunks)
        
        # Cache for performance
        self._checkpoint_cache[cache_key] = requirements
        
        return requirements
    
    def _parse_checkpoint_requirements(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Parse checkpoint requirements from document chunks dynamically.
        
        Analyzes document structure to extract:
        - Required evidence fields
        - Field types (inferred from examples)
        - Validation rules (extracted from requirements language)
        """
        requirements = {}
        
        for chunk in chunks:
            # Find checkpoint section
            lines = chunk.content.split('\n')
            
            for i, line in enumerate(lines):
                # Detect evidence requirement patterns dynamically
                if self._is_evidence_requirement(line):
                    field_name = self._extract_field_name(line)
                    field_type = self._infer_field_type(line, lines[i:i+3])
                    validator = self._extract_validator(line, lines[i:i+3])
                    
                    requirements[field_name] = {
                        "type": field_type,
                        "validator": validator,
                        "description": self._extract_description(line)
                    }
        
        return {"required_evidence": requirements}
    
    def _is_evidence_requirement(self, line: str) -> bool:
        """Detect if line describes an evidence requirement."""
        # Look for requirement indicators in line structure
        indicators = ["must provide", "required:", "evidence:", "checkpoint:"]
        line_lower = line.lower()
        return any(ind in line_lower for ind in indicators)
    
    def _extract_field_name(self, line: str) -> str:
        """Extract field name from requirement line."""
        # Look for field name patterns (typically in code formatting or bold)
        words = line.split()
        for word in words:
            # Field names often in code format: `field_name`
            if word.startswith('`') and word.endswith('`'):
                return word.strip('`')
            # Or emphasized: **field_name**
            if word.startswith('**') and word.endswith('**'):
                return word.strip('*').lower().replace(' ', '_')
        
        # Fallback: first snake_case word
        for word in words:
            if '_' in word and word.replace('_', '').isalnum():
                return word
        
        return "unknown_field"
    
    def _infer_field_type(self, line: str, context: List[str]) -> type:
        """Infer field type from context and examples."""
        line_lower = line.lower()
        
        # Look for type hints in context
        if any(word in line_lower for word in ["count", "number", "quantity"]):
            return int
        if any(word in line_lower for word in ["list", "array", "collection"]):
            return list
        if any(word in line_lower for word in ["output", "text", "command"]):
            return str
        if any(word in line_lower for word in ["flag", "boolean", "true/false"]):
            return bool
        
        # Default to string
        return str
    
    def _extract_validator(self, line: str, context: List[str]) -> callable:
        """Extract validation logic from requirement description."""
        line_lower = line.lower()
        
        # Analyze requirement language for validation rules
        if "greater than" in line_lower or "at least" in line_lower or "non-zero" in line_lower:
            return lambda x: x > 0 if isinstance(x, int) else len(x) > 0
        if "non-empty" in line_lower or "must contain" in line_lower:
            return lambda x: len(x) > 0
        if "optional" in line_lower or "may be empty" in line_lower:
            return lambda x: True
        
        # Default: must exist
        return lambda x: x is not None
    
    def _extract_description(self, line: str) -> str:
        """Extract human-readable description."""
        # Remove formatting and extract description text
        cleaned = line.strip('*#-:`"')
        return cleaned.strip()
```

**Why dynamic loading:**
- ✅ **Single source of truth** - Agent OS docs define checkpoints, not code
- ✅ **No drift** - Code always matches current framework version
- ✅ **Extensible** - New phases/fields need no code changes
- ✅ **Validates framework documents** - Parsing forces clear checkpoint definitions
- ✅ **Aligns with project standards** - Dynamic logic over static patterns

### Validation Algorithm

```python
def validate_checkpoint(
    self, 
    workflow_type: str,
    phase: int, 
    evidence: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validate evidence against dynamically loaded checkpoint requirements.
    
    Returns:
        (passed: bool, missing_fields: List[str])
    """
    # Load requirements dynamically from Agent OS documents
    checkpoint_def = self.checkpoint_loader.load_checkpoint_requirements(
        workflow_type, phase
    )
    requirements = checkpoint_def["required_evidence"]
    missing = []
    
    for field, spec in requirements.items():
        # Check field exists
        if field not in evidence:
            missing.append(f"{field} (required: {spec.get('description', 'no description')})")
            continue
        
        # Check type
        if not isinstance(evidence[field], spec["type"]):
            missing.append(
                f"{field} (wrong type: expected {spec['type'].__name__}, "
                f"got {type(evidence[field]).__name__})"
            )
            continue
        
        # Check validator
        try:
            if not spec["validator"](evidence[field]):
                missing.append(f"{field} (validation failed: {spec.get('description', '')})")
                continue
        except Exception as e:
            missing.append(f"{field} (validation error: {str(e)})")
            continue
    
    passed = len(missing) == 0
    return (passed, missing)
```

**Key difference:** Requirements loaded dynamically from Agent OS docs, not hardcoded dict.

### Phase Completion

```python
def complete_phase(
    session_id: str,
    phase: int,
    evidence: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Attempt to complete phase with evidence.
    
    Steps:
    1. Validate checkpoint
    2. If passed: Save artifacts, advance phase
    3. If failed: Return missing evidence, stay on phase
    """
    state = load_state(session_id)
    
    # Validate checkpoint
    passed, missing = validate_checkpoint(phase, evidence)
    
    if not passed:
        return {
            "checkpoint_passed": False,
            "missing_evidence": missing,
            "current_phase": phase,
            "current_phase_content": load_phase_content(phase),
            "message": "Complete checkpoint requirements to proceed"
        }
    
    # Checkpoint passed - save and advance
    artifact = PhaseArtifact(
        phase_number=phase,
        evidence=evidence,
        outputs=extract_outputs(evidence),
        commands_executed=extract_commands(evidence),
        timestamp=datetime.now()
    )
    
    state.completed_phases.append(phase)
    state.phase_artifacts[phase] = artifact
    state.current_phase = phase + 1
    state.checkpoints[phase] = "passed"
    state.updated_at = datetime.now()
    
    save_state(state)
    
    # Return next phase content
    if state.current_phase <= 8:
        return {
            "checkpoint_passed": True,
            "phase_completed": phase,
            "next_phase": state.current_phase,
            "next_phase_content": load_phase_content(state.current_phase),
            "artifacts_available": get_artifacts(state)
        }
    else:
        return {
            "checkpoint_passed": True,
            "phase_completed": phase,
            "workflow_complete": True,
            "message": "All phases complete, ready for test generation"
        }
```

---

## STATE MANAGEMENT

### State Persistence

```python
class StateManager:
    """Manages workflow state persistence."""
    
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.state_path.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, state: WorkflowState) -> None:
        """Save state to disk."""
        state_file = self.state_path / "sessions" / f"{state.session_id}.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Serialize
        data = state.to_dict()
        
        # Write atomically
        temp_file = state_file.with_suffix('.tmp')
        temp_file.write_text(json.dumps(data, indent=2))
        temp_file.replace(state_file)
    
    def load_state(self, session_id: str) -> WorkflowState:
        """Load state from disk."""
        state_file = self.state_path / "sessions" / f"{session_id}.json"
        
        if not state_file.exists():
            raise StateError(f"Session {session_id} not found")
        
        data = json.loads(state_file.read_text())
        return WorkflowState.from_dict(data)
```

### Artifact Management

```python
def get_artifacts(state: WorkflowState) -> Dict[int, Any]:
    """
    Get artifacts from completed phases for current phase.
    
    Example:
    If on Phase 3, return artifacts from Phases 1 and 2:
    {
        1: {
            "function_count": 21,
            "functions": ["compile", "parse", ...],
            "methods": ["_validate", ...]
        },
        2: {
            "logger_call_count": 15,
            "logging_patterns": [...]
        }
    }
    """
    artifacts = {}
    for phase_num in state.completed_phases:
        if phase_num in state.phase_artifacts:
            artifact = state.phase_artifacts[phase_num]
            artifacts[phase_num] = artifact.outputs
    
    return artifacts
```

---

## ERROR HANDLING

### Sequence Violation Handling

```python
def handle_sequence_violation(
    state: WorkflowState,
    requested_phase: int
) -> Dict[str, Any]:
    """
    Handle when AI tries to skip phases.
    
    Returns helpful error with correct phase content.
    """
    return {
        "error": "phase_sequence_violation",
        "message": f"Cannot access Phase {requested_phase}",
        "reason": f"Currently on Phase {state.current_phase}",
        "required_action": f"Complete Phase {state.current_phase} checkpoint first",
        "current_phase_content": load_phase_content(state.current_phase),
        "progress": {
            "completed": state.completed_phases,
            "current": state.current_phase,
            "total": 8
        }
    }
```

### Missing Evidence Handling

```python
def handle_missing_evidence(
    self,
    workflow_type: str,
    phase: int,
    missing_fields: List[str]
) -> Dict[str, Any]:
    """
    Handle incomplete checkpoint evidence.
    
    Returns specific requirements with examples (dynamically loaded).
    """
    # Load requirements dynamically
    checkpoint_def = self.checkpoint_loader.load_checkpoint_requirements(
        workflow_type, phase
    )
    
    # Extract examples from Agent OS documents
    examples = self._extract_evidence_examples(workflow_type, phase)
    
    return {
        "error": "incomplete_checkpoint",
        "phase": phase,
        "missing_evidence": missing_fields,
        "required_format": checkpoint_def["required_evidence"],
        "examples": examples,
        "message": "Provide all required evidence to complete checkpoint"
    }

def _extract_evidence_examples(self, workflow_type: str, phase: int) -> Dict[str, Any]:
    """
    Extract evidence examples from Agent OS documents dynamically.
    
    Searches for example sections in phase documentation.
    """
    query = f"{workflow_type} Phase {phase} evidence examples"
    result = self.rag_engine.search(
        query=query,
        filter_phase=phase,
        filter_tags=["example", "evidence"],
        n_results=2
    )
    
    # Parse examples from retrieved chunks
    examples = {}
    for chunk in result.chunks:
        parsed = self._parse_examples_from_content(chunk.content)
        examples.update(parsed)
    
    return examples
```

---

## INTEGRATION WITH RAG ENGINE

### Loading Phase Content

```python
def load_phase_content(phase: int) -> Dict[str, Any]:
    """
    Load phase content using RAG engine.
    
    Uses semantic search to get phase-specific content only.
    """
    # Query RAG for phase content
    query = f"Phase {phase} requirements commands checkpoint"
    result = rag_engine.search(
        query=query,
        filter_phase=phase,
        n_results=3  # Get 3 most relevant chunks
    )
    
    # Combine chunks into phase content
    content = "\n\n".join([chunk.content for chunk in result.chunks])
    
    return {
        "phase_number": phase,
        "content": content,
        "sources": [chunk.file_path for chunk in result.chunks],
        "total_tokens": result.total_tokens
    }
```

---

## TESTING STRATEGY

### Unit Tests

```python
# tests/unit/mcp_servers/test_workflow_engine.py

def test_phase_gating_enforcement():
    """Test that phase skipping is prevented."""
    engine = WorkflowEngine(...)
    session_id = engine.start_workflow("test_generation_v3", "test.py")["session_id"]
    
    # Try to skip to Phase 3
    result = engine.get_phase_content(session_id, requested_phase=3)
    
    # Should get error
    assert "error" in result
    assert result["error"] == "phase_sequence_violation"
    assert result["current_phase_content"]  # Should return Phase 1 content

def test_checkpoint_validation_pass():
    """Test checkpoint validation when evidence complete."""
    evidence = {
        "function_count": 21,
        "method_count": 15,
        "branch_count": 36,
        "ast_command_output": "def compile()...",
        "functions_list": ["compile", "parse"]
    }
    
    passed, missing = validate_checkpoint(phase=1, evidence=evidence)
    
    assert passed is True
    assert missing == []

def test_checkpoint_validation_fail():
    """Test checkpoint validation when evidence incomplete."""
    evidence = {
        "function_count": 21,
        # Missing other required fields
    }
    
    passed, missing = validate_checkpoint(phase=1, evidence=evidence)
    
    assert passed is False
    assert len(missing) == 4  # 4 missing fields

# Total: 20+ tests covering all scenarios
```

---

## SUCCESS METRICS

**Workflow Engine succeeds when:**

✅ Cannot access Phase N+1 before Phase N (100% prevention)  
✅ Checkpoint validation requires complete evidence  
✅ State persists across Cursor restarts  
✅ Artifacts pass correctly between phases  
✅ Error messages helpful and actionable  
✅ 0 corrections needed for phase sequencing

---

**Document Status:** Complete - Ready for Review  
**Next Document:** rag-architecture.md  
**Purpose:** Architectural phase gating design  
**Key Innovation:** Structural prevention vs. documentary prohibition


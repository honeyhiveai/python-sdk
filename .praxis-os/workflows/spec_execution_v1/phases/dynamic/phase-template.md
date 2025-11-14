# Phase [PHASE_NUMBER]: [PHASE_NAME]

**Phase:** [PHASE_NUMBER]  
**Name:** [PHASE_NAME]  
**Estimated Duration:** [ESTIMATED_DURATION]  
**Total Tasks:** [TASK_COUNT]

---

## 🎯 Phase Objective

[PHASE_DESCRIPTION]

---

## Phase Overview

⚠️ MUST-READ: Review phase description from tasks.md

**This phase includes:**
- Task [N.1]: [Brief description]
- Task [N.2]: [Brief description]
- Task [N.3]: [Brief description]
[... list all tasks]

---

## Execution Approach

### Horizontal Scaling (One Task at a Time)

🛑 EXECUTE-NOW: Use `get_task()` for each task individually

```python
# Get first task
MCP: get_task(session_id, phase=[PHASE_NUMBER], task_number=1)

# Complete task 1, then:
MCP: get_task(session_id, phase=[PHASE_NUMBER], task_number=2)

# Continue until all tasks complete
```

⚠️ WARNING: Do NOT attempt multiple tasks simultaneously

Meta-framework principle: **Horizontal decomposition** means focused, sequential execution. One task at a time ensures optimal attention and quality.

---

## Production Standards

🛑 EXECUTE-NOW: Every task must follow production code checklist

For EACH task in this phase:
- ✅ Query relevant standards via MCP
- ✅ Follow specs.md design
- ✅ Use implementation.md patterns
- ✅ Apply production code checklist
- ✅ Write comprehensive tests
- ✅ Collect evidence

---

## Task Execution Loop

For each task in this phase:

### 1. Get Task

```python
MCP: get_task(session_id, phase=[PHASE_NUMBER], task_number=[N])
```

### 2. Execute Task

Follow task template guidance:
- Verify dependencies
- Query standards
- Implement with quality
- Write tests
- Validate criteria

### 3. Collect Evidence

📊 COUNT-AND-DOCUMENT: Task results

### 4. Next Task

Proceed to next task number or phase checkpoint

---

## Phase Checkpoint

🛑 VALIDATE-GATE: Phase [PHASE_NUMBER] Completion

After ALL tasks complete, validate phase-level criteria:

[VALIDATION_GATE]

Additional mandatory validation:
- [ ] All tasks in phase completed ✅/❌
- [ ] All tests passing ✅/❌
- [ ] No linting errors ✅/❌
- [ ] Production checklist satisfied ✅/❌
- [ ] Documentation updated ✅/❌

🚨 FRAMEWORK-VIOLATION: Advancing with incomplete tasks

Phase gates are MANDATORY. Proceeding with incomplete tasks or failing tests will cause cascading failures in later phases.

---

## Evidence Submission

📊 COUNT-AND-DOCUMENT: Phase [PHASE_NUMBER] Results

**Tasks Completed:**
- Total: [number]/[number]
- Details: [list with status]

**Code Quality:**
- Files modified: [list]
- Tests added: [number]
- Tests passing: [number]/[number]
- Coverage: [percentage]%

**Validation:**
- Phase gate criteria: [number] met
- Production standards: [complete/incomplete]

---

## Complete Phase

🛑 EXECUTE-NOW: Submit evidence to complete phase

```python
MCP: complete_phase(
    session_id=session_id,
    phase=[PHASE_NUMBER],
    evidence={
        "tasks_completed": [list of task IDs],
        "tests_passing": [number],
        "files_modified": [list],
        "validation_gate": {
            [gate criteria with true/false values]
        }
    }
)
```

---

## Next Phase

🎯 NEXT-MANDATORY: Proceed to Phase [NEXT_PHASE_NUMBER]

```python
MCP: get_current_phase(session_id)
# Returns Phase [NEXT_PHASE_NUMBER] overview
```


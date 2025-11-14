# Task [TASK_ID]: [TASK_NAME]

**Phase:** [PHASE_NUMBER] ([PHASE_NAME])  
**Task ID:** [TASK_ID]  
**Estimated Time:** [ESTIMATED_TIME]  
**Dependencies:** [DEPENDENCIES]

---

## 🎯 Objective

[TASK_DESCRIPTION]

---

## Prerequisites

🛑 EXECUTE-NOW: Verify dependencies completed

Dependencies: [DEPENDENCIES or "None"]

⚠️ MUST-READ: Review specs.md section relevant to this task

⚠️ MUST-READ: Review implementation.md patterns for this task

---

## Implementation Standards

🛑 EXECUTE-NOW: Query production code checklist

```python
MCP: search_standards("production code checklist")
```

**Mandatory Quality Requirements:**
- ✅ Comprehensive Sphinx-style docstrings
- ✅ Full type hints (parameters + return types)
- ✅ Explicit error handling with specific exceptions
- ✅ Resource lifecycle management
- ✅ Unit tests (80%+ coverage)
- ✅ Integration tests (if applicable)

🚨 FRAMEWORK-VIOLATION: Skipping quality requirements

Production code checklist is MANDATORY. Code without proper docstrings, type hints, tests, or error handling will fail validation gates.

---

## Execution Steps

🛑 MANDATORY EXECUTION DISCIPLINE: Step-by-Step Validation

**DO NOT rush through all steps then validate at the end. Validate EACH step before proceeding.**

**Correct Execution Pattern:**
1. Complete ONE acceptance criterion (fully, thoroughly)
2. 🛑 VALIDATE-GATE: [Criterion name]
   - [ ] [Specific criterion] ✅/❌
3. If ❌ → Fix it NOW before proceeding
4. If ✅ → Proceed to next criterion
5. Repeat for EACH acceptance criterion

🚨 FRAMEWORK-VIOLATION: Completing multiple steps before validating each one

**Why this matters:** Without step-level gates, you WILL take shortcuts. Validation gates are blocking checkpoints, not post-hoc checklists.

---

Follow specs.md design and implementation.md patterns to complete this task.

### Key Actions

[TASK_STEPS or general guidance based on task type]

**For each key action above:**
- Complete the action thoroughly and systematically
- Validate it meets the acceptance criterion
- Do NOT proceed to next action until current one passes validation

### Testing Requirements

🛑 EXECUTE-NOW: Write tests BEFORE marking complete

- Unit tests for all new functions/classes
- Integration tests for component interactions
- All tests must pass

---

## Acceptance Criteria

🛑 VALIDATE-GATE: Task Completion

**Execute these criteria ONE AT A TIME with validation between each:**

[ACCEPTANCE_CRITERIA]

Additional mandatory criteria:
- [ ] Code follows production checklist ✅/❌
- [ ] Sphinx docstrings complete ✅/❌
- [ ] Type hints on all functions ✅/❌
- [ ] Error handling implemented ✅/❌
- [ ] Tests written and passing ✅/❌
- [ ] No linting errors ✅/❌

---

## Evidence Collection

📊 COUNT-AND-DOCUMENT: Task Results

**Files Modified:**
- [list of files created/modified]

**Code Quality:**
- Functions/classes added: [number]
- Docstrings: [number]
- Type hints: [complete/incomplete]
- Tests written: [number]
- Tests passing: [number]/[number]

**Validation:**
- Acceptance criteria: [number] met
- Production checklist: [complete/incomplete]

🛑 EXECUTE-NOW: Mark task complete in tasks.md

Update the spec's tasks.md file to track completion:

1. Open `.praxis-os/specs/{SPEC_DIR}/tasks.md`
2. Find this task: `- [ ] **Task [TASK_ID]**: [TASK_NAME]`
3. Change to: `- [x] **Task [TASK_ID]**: [TASK_NAME]`
4. Update all acceptance criteria checkboxes to `[x]`
5. Note actual line counts or metrics in criteria (if applicable)

**Why:** Maintains visible progress tracking and provides historical record of completed work.

🚨 FRAMEWORK-VIOLATION: Using generated code summaries, not full files

Do NOT re-read large generated files. Use summaries only to preserve context efficiency.

---

## Next Task

🎯 NEXT-MANDATORY: Use `get_task()` for next task

```python
MCP: get_task(session_id, phase=[PHASE_NUMBER], task_number=[NEXT_TASK_NUMBER])
```

Or if this is the last task in the phase:

🎯 NEXT-MANDATORY: Complete phase checkpoint (see phase template)


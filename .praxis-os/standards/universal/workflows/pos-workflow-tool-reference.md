# pos_workflow Tool Reference

**Keywords for search**: pos_workflow tool, workflow tool usage, how to start workflow, how to execute workflow, workflow tool API, workflow actions, start workflow, get task, complete phase, workflow tool reference, pos_workflow documentation, workflow execution guide, how to use workflows, workflow tool examples, when to use pos_workflow, workflow session management

**This standard provides complete reference documentation for the `pos_workflow` MCP tool, including all 14 actions, parameters, usage patterns, and examples.**

---

## 🎯 TL;DR - pos_workflow Tool Quick Reference

**Core Principle:** `pos_workflow` is the single consolidated tool for ALL workflow operations - discovery, execution, session management, and recovery.

**Common Actions:**
- `list_workflows` - Discover available workflows
- `start` - Initialize a workflow session
- `get_task` - Get specific task details
- `complete_phase` - Submit evidence and advance
- `get_state` - Check workflow progress

**Basic Usage Pattern:**
```python
# 1. Discover workflows
pos_workflow(action="list_workflows")

# 2. Start workflow
result = pos_workflow(
    action="start",
    workflow_type="spec_execution_v1",
    target_file="feature-name",
    options={"spec_path": ".praxis-os/specs/approved/2025-11-04-rag-index-submodule-refactor"}
)
session_id = result["session_id"]  # SAVE THIS!

# 3. Get current phase
pos_workflow(action="get_phase", session_id=session_id)

# 4. Get specific task
pos_workflow(action="get_task", session_id=session_id, phase=1, task_number=1)

# 5. Complete phase with evidence
pos_workflow(
    action="complete_phase",
    session_id=session_id,
    phase=1,
    evidence={"tests_passed": 15, "files_modified": ["src/auth.py"]}
)

# 6. Check state
pos_workflow(action="get_state", session_id=session_id)
```

**14 Available Actions:**
- **Discovery (1)**: list_workflows
- **Execution (5)**: start, get_phase, get_task, complete_phase, get_state
- **Management (3)**: list_sessions, get_session, delete_session
- **Recovery (5)**: pause, resume, retry_phase, rollback, get_errors

**Critical Rules:**
- ✅ **ALWAYS save `session_id`** from start action - you need it for everything else
- ✅ **Phase gating is enforced** - cannot skip phases, must complete in order
- ✅ **Evidence required** - every complete_phase needs evidence dictionary
- ❌ **Don't bypass workflows** - if workflow exists, use it (don't ad-hoc implement)

---

## ❓ Questions This Answers

1. "How do I use the pos_workflow tool?"
2. "How to start a workflow?"
3. "How to execute a specification using workflows?"
4. "What actions does pos_workflow support?"
5. "How to get tasks from a workflow?"
6. "How to complete a workflow phase?"
7. "How to submit evidence for phase completion?"
8. "How to check workflow progress?"
9. "How to list available workflows?"
10. "How to resume a workflow session?"
11. "How to manage workflow sessions?"
12. "What parameters does pos_workflow need?"
13. "How to discover what workflows exist?"
14. "How to get details about a specific workflow?"
15. "What's the difference between get_phase and get_task?"
16. "How to handle workflow errors?"
17. "How to delete a workflow session?"
18. "What evidence format for complete_phase?"
19. "How to execute specs phase by phase?"
20. "What's the workflow execution lifecycle?"

---

## 🎯 Purpose

This standard provides comprehensive reference documentation for the `pos_workflow` MCP tool, the single consolidated interface for all workflow operations in prAxIs OS.

**Core Principle**: One tool, multiple actions. All workflow operations (discovery, execution, management, recovery) use `pos_workflow` with different `action` parameters.

---

## What is pos_workflow?

`pos_workflow` is the consolidated MCP tool that provides **all workflow operations** through action-based dispatch.

**Why one tool instead of many?**
- Research shows 85% LLM performance drop with >20 tools
- Follows proven `pos_browser` pattern
- Single interface is easier to learn and use
- Consistent parameter patterns across actions

**What can it do?**
- Discover available workflows
- Start and execute workflows
- Get phase/task details
- Submit evidence and advance phases
- Manage workflow sessions
- Handle errors and recovery

---

## Complete Action Reference

### Discovery Actions

#### list_workflows

**Purpose:** Discover all available workflows in the system.

**Parameters:**
- `action`: `"list_workflows"` (required)
- `category`: Optional filter (e.g., `"code_generation"`, `"spec_execution"`)

**Returns:**
- `workflows`: List of workflow metadata objects
- `count`: Number of workflows found

**Example:**
```python
# List all workflows
result = pos_workflow(action="list_workflows")

# Filter by category
result = pos_workflow(action="list_workflows", category="spec_execution")
```

**When to use:**
- User asks "what workflows are available?"
- Need to discover workflow for a task
- Exploring workflow capabilities

---

### Execution Actions

#### start

**Purpose:** Initialize a new workflow session.

**Parameters:**
- `action`: `"start"` (required)
- `workflow_type`: Workflow identifier (required) - e.g., `"spec_execution_v1"`, `"test_generation_v3"`
- `target_file`: Target file or identifier (required)
- `options`: Optional configuration dictionary

**Returns:**
- `session_id`: Session identifier (**SAVE THIS - required for all subsequent actions!**)
- `workflow_type`: Echoed workflow type
- `current_phase`: Starting phase (usually 1)
- `workflow_overview`: Complete phase structure

**Example:**
```python
# Start spec execution workflow
result = pos_workflow(
    action="start",
    workflow_type="spec_execution_v1",
    target_file="rag-index-refactor",
    options={"spec_path": ".praxis-os/specs/approved/2025-11-04-rag-index-submodule-refactor"}
)

session_id = result["session_id"]  # CRITICAL: Save this!
```

**Important:**
- `target_file` format depends on workflow type
- Code workflows: Use actual file path (e.g., `"src/auth.py"`)
- Spec workflows: Use simple identifier, provide full path in `options["spec_path"]`
- **Always save the `session_id`** - you need it for everything else

---

#### get_phase

**Purpose:** Get current phase overview and all tasks in that phase.

**Parameters:**
- `action`: `"get_phase"` (required)
- `session_id`: Session identifier (required)

**Returns:**
- `phase_number`: Current phase number
- `phase_title`: Phase name/description
- `tasks`: List of all tasks in current phase (brief summaries)
- `acceptance_criteria`: Phase completion criteria
- `dependencies`: Required dependencies from previous phases

**Example:**
```python
result = pos_workflow(action="get_phase", session_id=session_id)

# Result includes:
# {
#   "phase_number": 1,
#   "phase_title": "Foundation & Parser Base",
#   "tasks": [
#     {"task_id": "1.1", "title": "Create base parser structure"},
#     {"task_id": "1.2", "title": "Implement ParseError class"}
#   ],
#   "acceptance_criteria": ["All base classes defined", "Tests pass"]
# }
```

**When to use:**
- Starting a new phase
- Need overview of all tasks in current phase
- Want to see phase-level requirements

---

#### get_task

**Purpose:** Get detailed content for a specific task.

**Parameters:**
- `action`: `"get_task"` (required)
- `session_id`: Session identifier (required)
- `phase`: Phase number (required)
- `task_number`: Task number within phase (required)

**Returns:**
- `task_id`: Task identifier
- `title`: Task title
- `content`: Full task description and requirements
- `acceptance_criteria`: Task-specific acceptance criteria
- `dependencies`: Task dependencies
- `estimated_time`: Time estimate (if available)

**Example:**
```python
# Get Task 1.2 details
result = pos_workflow(
    action="get_task",
    session_id=session_id,
    phase=1,
    task_number=2
)

# Result includes full task details:
# {
#   "task_id": "1.2",
#   "title": "Implement ParseError class",
#   "content": "Create ActionableError subclass...",
#   "acceptance_criteria": ["Inherits from ActionableError", "Tests pass"],
#   "dependencies": ["1.1"]
# }
```

**When to use:**
- Need full details for implementing a task
- Want to understand task requirements
- Checking acceptance criteria before starting

---

#### complete_phase

**Purpose:** Submit evidence of phase completion and advance to next phase.

**Parameters:**
- `action`: `"complete_phase"` (required)
- `session_id`: Session identifier (required)
- `phase`: Phase number being completed (required)
- `evidence`: Evidence dictionary (required)

**Returns:**
- `validation_passed`: Boolean indicating if evidence met requirements
- `next_phase`: Next phase number (if validation passed)
- `errors`: Validation errors (if any)
- `phase_completed`: Boolean

**Evidence Format:**
```python
evidence = {
    "files_modified": ["path/to/file1.py", "path/to/file2.py"],
    "tests_passed": 15,
    "tests_added": 8,
    "acceptance_criteria_met": ["Criterion 1", "Criterion 2"],
    "notes": "Additional context or observations",
    # Any other relevant metrics
}
```

**Example:**
```python
result = pos_workflow(
    action="complete_phase",
    session_id=session_id,
    phase=1,
    evidence={
        "files_modified": [
            "ouroboros/subsystems/workflow/parsers/base.py",
            "tests/integration/test_parser.py"
        ],
        "tests_passed": 10,
        "tests_added": 10,
        "acceptance_criteria_met": [
            "Base parser classes created",
            "ParseError implemented",
            "All tests passing"
        ],
        "notes": "Modular architecture in place"
    }
)

if result["validation_passed"]:
    print(f"✅ Phase 1 complete! Moving to Phase {result['next_phase']}")
else:
    print(f"❌ Validation failed: {result['errors']}")
```

**Important:**
- Evidence is **required** - empty dict will fail validation
- Include all relevant metrics (files, tests, criteria)
- Validation is enforced - cannot skip phases
- If validation fails, fix issues and retry

---

#### get_state

**Purpose:** Get complete workflow state and progress.

**Parameters:**
- `action`: `"get_state"` (required)
- `session_id`: Session identifier (required)

**Returns:**
- `workflow_type`: Workflow identifier
- `current_phase`: Current phase number
- `total_phases`: Total number of phases
- `progress`: Completion percentage
- `status`: Workflow status ("active", "paused", "completed", "error")
- `history`: Phase completion history

**Example:**
```python
result = pos_workflow(action="get_state", session_id=session_id)

# Result includes:
# {
#   "workflow_type": "spec_execution_v1",
#   "current_phase": 3,
#   "total_phases": 9,
#   "progress": 33.3,
#   "status": "active",
#   "history": [
#     {"phase": 1, "completed_at": "2025-11-06T10:30:00", "evidence": {...}},
#     {"phase": 2, "completed_at": "2025-11-06T11:45:00", "evidence": {...}}
#   ]
# }
```

**When to use:**
- Check overall progress
- Resuming after interruption
- Reporting status to user
- Debugging workflow issues

---

### Management Actions

#### list_sessions

**Purpose:** List all workflow sessions (active and historical).

**Parameters:**
- `action`: `"list_sessions"` (required)
- `status`: Optional filter - `"active"`, `"paused"`, `"completed"`, `"error"`

**Returns:**
- `sessions`: List of session objects
- `count`: Number of sessions found

**Example:**
```python
# List all active sessions
result = pos_workflow(action="list_sessions", status="active")

# List all sessions
result = pos_workflow(action="list_sessions")
```

**When to use:**
- Finding interrupted sessions to resume
- Checking what workflows are running
- Debugging session issues

---

#### get_session

**Purpose:** Get detailed information about a specific session.

**Parameters:**
- `action`: `"get_session"` (required)
- `session_id`: Session identifier (required)

**Returns:**
- Complete session details including state, history, and metadata

**Example:**
```python
result = pos_workflow(action="get_session", session_id=session_id)
```

---

#### delete_session

**Purpose:** Delete a workflow session (cleanup or cancel workflow).

**Parameters:**
- `action`: `"delete_session"` (required)
- `session_id`: Session identifier (required)

**Returns:**
- `deleted`: Boolean indicating success

**Example:**
```python
result = pos_workflow(action="delete_session", session_id=session_id)
```

**When to use:**
- Cleaning up completed workflows
- Canceling workflows that won't be completed
- Resolving session conflicts

---

### Recovery Actions

*Note: Recovery actions (pause, resume, retry_phase, rollback, get_errors) are planned for Phase 3 implementation.*

---

## Common Workflow Patterns

### Pattern 1: Execute a Specification

**Scenario:** User says "implement this spec" or "execute the spec"

```python
# Step 1: Discover spec execution workflow
workflows = pos_workflow(action="list_workflows", category="spec_execution")

# Step 2: Start workflow with spec path
result = pos_workflow(
    action="start",
    workflow_type="spec_execution_v1",
    target_file="feature-name",
    options={"spec_path": ".praxis-os/specs/approved/2025-11-04-rag-index-submodule-refactor"}
)
session_id = result["session_id"]

# Step 3: Get Phase 1 overview
phase = pos_workflow(action="get_phase", session_id=session_id)
print(f"Phase {phase['phase_number']}: {phase['phase_title']}")
print(f"Tasks: {len(phase['tasks'])}")

# Step 4: Get first task details
task = pos_workflow(
    action="get_task",
    session_id=session_id,
    phase=1,
    task_number=1
)
print(f"Task 1.1: {task['title']}")

# Step 5: [Do the actual work - implement, test, validate]

# Step 6: Complete phase with evidence
result = pos_workflow(
    action="complete_phase",
    session_id=session_id,
    phase=1,
    evidence={
        "files_modified": ["list", "of", "files"],
        "tests_passed": 10,
        "acceptance_criteria_met": ["criterion 1", "criterion 2"]
    }
)

# Step 7: Repeat for each phase until workflow_complete
```

---

### Pattern 2: Resume Interrupted Workflow

**Scenario:** Workflow was interrupted, need to resume

```python
# Step 1: List active sessions
sessions = pos_workflow(action="list_sessions", status="active")

# Step 2: Get session details
session = pos_workflow(action="get_session", session_id=session_id)

# Step 3: Get current state
state = pos_workflow(action="get_state", session_id=session_id)
print(f"Resuming at Phase {state['current_phase']}")

# Step 4: Get current phase
phase = pos_workflow(action="get_phase", session_id=session_id)

# Step 5: Continue from where you left off
```

---

### Pattern 3: Check Progress and Report Status

**Scenario:** User asks "how's the workflow going?"

```python
# Get complete state
state = pos_workflow(action="get_state", session_id=session_id)

print(f"Workflow: {state['workflow_type']}")
print(f"Progress: {state['progress']}%")
print(f"Current Phase: {state['current_phase']} of {state['total_phases']}")
print(f"Status: {state['status']}")

# Get current phase details
phase = pos_workflow(action="get_phase", session_id=session_id)
print(f"\nCurrent Phase: {phase['phase_title']}")
print(f"Tasks: {len(phase['tasks'])} tasks to complete")
```

---

## Anti-Patterns (DON'T Do These)

### ❌ Anti-Pattern 1: Forgetting to Save session_id

```python
# BAD: Losing session_id
result = pos_workflow(action="start", workflow_type="...", target_file="...")
# ... do some work ...
# ... uh oh, what was the session_id?
pos_workflow(action="get_phase", session_id=???)  # LOST!
```

**GOOD:**
```python
result = pos_workflow(action="start", workflow_type="...", target_file="...")
session_id = result["session_id"]  # SAVE IT IMMEDIATELY
# Use session_id for everything else
```

---

### ❌ Anti-Pattern 2: Not Providing Evidence

```python
# BAD: Empty evidence
pos_workflow(
    action="complete_phase",
    session_id=session_id,
    phase=1,
    evidence={}  # Will fail validation!
)
```

**GOOD:**
```python
pos_workflow(
    action="complete_phase",
    session_id=session_id,
    phase=1,
    evidence={
        "files_modified": ["actual", "files"],
        "tests_passed": 10,
        "acceptance_criteria_met": ["actual", "criteria"]
    }
)
```

---

### ❌ Anti-Pattern 3: Trying to Skip Phases

```python
# BAD: Trying to jump ahead
pos_workflow(action="complete_phase", session_id=session_id, phase=3, evidence={...})
# ERROR: Phase 2 not completed yet!
```

**GOOD:**
```python
# Complete phases in order
pos_workflow(action="complete_phase", session_id=session_id, phase=1, evidence={...})
pos_workflow(action="complete_phase", session_id=session_id, phase=2, evidence={...})
pos_workflow(action="complete_phase", session_id=session_id, phase=3, evidence={...})
```

---

### ❌ Anti-Pattern 4: Using get_phase When You Need get_task

```python
# BAD: Getting phase when you need task details
phase = pos_workflow(action="get_phase", session_id=session_id)
# Phase gives overview, not full task details!
```

**GOOD:**
```python
# Use get_phase for overview
phase = pos_workflow(action="get_phase", session_id=session_id)

# Use get_task for detailed implementation requirements
task = pos_workflow(
    action="get_task",
    session_id=session_id,
    phase=1,
    task_number=1
)
```

---

### ❌ Anti-Pattern 5: Ad-Hoc Implementation Instead of Using Workflows

```python
# BAD: User says "execute this spec" but you just start coding
# ... implement feature manually without workflow ...
```

**GOOD:**
```python
# User says "execute this spec"
# 1. Query for workflow guidance
pos_search_project(action="search_standards", query="how to execute specification workflow")

# 2. Use the appropriate workflow
pos_workflow(action="start", workflow_type="spec_execution_v1", ...)
```

---

## Checklist for Using pos_workflow

**Before starting a workflow:**
- [ ] Queried standards to understand workflow usage
- [ ] Discovered available workflows with `list_workflows`
- [ ] Identified correct workflow type for the task
- [ ] Have target_file and any required options ready

**When starting a workflow:**
- [ ] Used `start` action with correct parameters
- [ ] **Saved `session_id` immediately**
- [ ] Checked `workflow_overview` to understand structure
- [ ] Noted total_phases and starting phase

**During workflow execution:**
- [ ] Using `get_phase` for phase overviews
- [ ] Using `get_task` for detailed task requirements
- [ ] Actually implementing the tasks (not just calling tools)
- [ ] Validating work against acceptance criteria

**When completing phases:**
- [ ] Collected evidence of completion
- [ ] Used `complete_phase` with comprehensive evidence dict
- [ ] Handled validation errors if they occur
- [ ] Verified phase advancement before continuing

**Throughout workflow:**
- [ ] Using `get_state` to check progress
- [ ] Not trying to skip phases
- [ ] Following phase-gated progression
- [ ] Providing meaningful evidence at each gate

---

## 🔍 When to Query This Standard

| Scenario | Example Query |
|----------|---------------|
| **Starting a workflow** | `pos_search_project(action="search_standards", query="how to start workflow pos_workflow")` |
| **Executing a spec** | `pos_search_project(action="search_standards", query="execute specification workflow")` |
| **Getting task details** | `pos_search_project(action="search_standards", query="pos_workflow get task details")` |
| **Completing a phase** | `pos_search_project(action="search_standards", query="complete phase workflow evidence")` |
| **Workflow progress** | `pos_search_project(action="search_standards", query="check workflow progress state")` |
| **Resume workflow** | `pos_search_project(action="search_standards", query="resume interrupted workflow")` |
| **Tool reference** | `pos_search_project(action="search_standards", query="pos_workflow tool API reference")` |
| **Workflow actions** | `pos_search_project(action="search_standards", query="what actions pos_workflow support")` |
| **Evidence format** | `pos_search_project(action="search_standards", query="workflow evidence format complete_phase")` |
| **Session management** | `pos_search_project(action="search_standards", query="workflow session management list")` |

---

## 🔗 Related Standards

**Query for related standards:**
- `pos_search_project(action="search_standards", query="workflow system overview")` - Overall workflow architecture
- `pos_search_project(action="search_standards", query="workflow discovery patterns")` - How to discover workflows
- `pos_search_project(action="search_standards", query="spec execution workflow")` - Specific guidance for spec execution
- `pos_search_project(action="search_standards", query="workflow metadata standards")` - Understanding workflow definitions
- `pos_search_project(action="search_standards", query="evidence validation system")` - How evidence is validated

---

**Version:** 1.0.0  
**Created:** 2025-11-06  
**Last Updated:** 2025-11-06  
**Next Review:** After first successful dogfooding session with fresh AI


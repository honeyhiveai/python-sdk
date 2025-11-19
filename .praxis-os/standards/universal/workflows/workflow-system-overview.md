# Workflow System Overview

**prAxIs OS Phase-Gated Workflow System Standards**

---

## 🎯 TL;DR - Workflow System Quick Reference

**Keywords for search**: workflow system, phase gating, workflow execution, workflow discovery, start_workflow, get_task, complete_phase, horizontal scaling, workflow state, validation gates

**Core Principle:** Workflows are structured, phase-gated processes that guide AI agents through complex tasks with quality checkpoints.

**Three Components:**
1. **Metadata** (metadata.json) - Workflow definition, indexed by RAG
2. **Engine** (workflow_engine.py) - Enforces gating, validates evidence
3. **MCP Tools** - AI agent interface (start_workflow, get_task, complete_phase)

**Key MCP Tools:**
```python
# Discover and start workflow
start_workflow(workflow_type="test_generation_v3", target_file="src/utils.py")

# Get current phase overview
get_current_phase(session_id)

# Get full task content (v1.3.0: horizontal scaling)
get_task(session_id, phase=1, task_number=2)

# Submit evidence and advance
complete_phase(session_id, phase=1, evidence={...})

# Check status
get_workflow_state(session_id)
```

**Phase Gating:** Sequential execution with validation gates. Cannot skip phases. Must provide evidence of completion.

**Horizontal Scaling (v1.3.0):** Tasks broken into individual files (≤100 lines), loaded on-demand to preserve context.

**Workflow Discovery:** RAG indexes metadata.json → AI queries like "how to generate tests" → Returns relevant workflow overview.

**State Management:** Persistent across sessions, resumable after failures, automatic backups.

**Common Workflows:**
- `test_generation_v3` - Generate comprehensive test suites
- `production_code_v2` - Write production-quality code
- `spec_execution_v1` - Execute design specifications

**Anti-Patterns:**
- ❌ Skipping phases (gating prevents this)
- ❌ Manual task management instead of using workflows
- ❌ Not submitting evidence at checkpoints

---

## ❓ Questions This Answers

1. "What is the prAxIs OS workflow system?"
2. "How do workflows work?"
3. "How do I start a workflow?"
4. "How do I use workflow MCP tools?"
5. "What is phase gating?"
6. "How do I discover workflows?"
7. "What is horizontal scaling in workflows?"
8. "How do I complete a phase?"
9. "How does workflow state management work?"
10. "How do I create a new workflow?"
11. "What are standard prAxIs OS workflows?"
12. "What are workflow best practices?"

---

## 🎯 Purpose

The prAxIs OS workflow system provides structured, phase-gated execution for complex AI-assisted tasks. This document defines standards for understanding, using, and creating workflows.

---

## How Is the Workflow System Architected?

The workflow system uses a three-tier architecture separating metadata, execution engine, and AI agent interface.

### Three-Tier System

1. **Workflow Metadata** (`universal/workflows/{workflow_type}/metadata.json`)
   - Defines workflow structure and phases
   - Provides overview information for AI planning
   - Indexed in RAG for semantic search

2. **Workflow Engine** (`mcp_server/workflow_engine.py`)
   - Enforces phase gating (sequential execution)
   - Validates checkpoint evidence
   - Manages workflow state and persistence

3. **MCP Tools** (Cursor IDE integration)
   - `start_workflow` - Initialize workflow with overview
   - `get_current_phase` - Get phase overview and task metadata
   - `get_task` - Get full content for specific task (v1.3.0: horizontal scaling)
   - `complete_phase` - Submit evidence and advance
   - `get_workflow_state` - Query workflow status

---

## What Is the Workflow Metadata Schema?

Metadata defines workflow structure, phases, and deliverables, enabling RAG discovery and AI planning.

### Structure

```json
{
  "workflow_type": "string",
  "version": "semver",
  "description": "string",
  "total_phases": number,
  "estimated_duration": "string",
  "primary_outputs": ["string"],
  "phases": [
    {
      "phase_number": number,
      "phase_name": "string",
      "purpose": "string",
      "estimated_effort": "string",
      "key_deliverables": ["string"],
      "validation_criteria": ["string"]
    }
  ]
}
```

### Location

Metadata files MUST be stored at:
```
universal/workflows/{workflow_type}/metadata.json
```

Example locations:
- `universal/workflows/test_generation_v3/metadata.json`
- `universal/workflows/production_code_v2/metadata.json`

---

## How to Use Workflows (Step-by-Step)?

Complete workflow usage from discovery through execution to completion.

### Starting a Workflow

```python
# Example 1: Code-based workflow (test generation)
result = await mcp_agent-os-rag_start_workflow(
    workflow_type="test_generation_v3",
    target_file="src/auth.py"  # File path for code workflows
)

# Example 2: Spec-based workflow (spec execution)
result = await mcp_agent-os-rag_start_workflow(
    workflow_type="spec_execution_v1",
    target_file="manifest-upgrade-system",  # Simple identifier, NOT full path
    options={"spec_path": ".praxis-os/specs/2025-10-07-manifest-upgrade-system"}
)

# Response includes workflow overview
overview = result["workflow_overview"]
total_phases = overview["total_phases"]  # e.g., 8
phases = overview["phases"]  # All phase metadata

# Now you know the complete roadmap before starting!
```

**Parameter Usage Note:**
- `target_file` format depends on workflow type
- Code workflows: Use actual file path (e.g., `"src/auth.py"`)
- Spec workflows: Use simple identifier (e.g., `"feature-name"`), provide full path in `options`

### Key Benefits

1. **Single API Call** - No need for separate `get_workflow_state()` call
2. **Complete Overview** - See all phases upfront
3. **Better Planning** - Know time commitment and deliverables
4. **Progress Tracking** - Understand "Phase 2 of 8" immediately

---

## How Does Workflow Discovery via RAG Work?

RAG-based workflow discovery enables AI agents to find relevant workflows through natural language queries.

### How It Works

1. **Indexing** - Workflow metadata is indexed in RAG during build
2. **Search** - Use semantic search to discover workflows
3. **Structure** - Metadata provides complete workflow information

### Example Queries

```python
# Find workflows for specific tasks
result = await mcp_agent-os-rag_search_standards(
    query="How do I generate comprehensive tests for Python code?",
    n_results=5
)
# Returns: test_generation_v3 workflow information

# Discover available workflows
result = await mcp_agent-os-rag_search_standards(
    query="What workflows are available for production code generation?",
    n_results=3
)
# Returns: production_code_v2 workflow metadata
```

---

## What Is Phase Gating and Why Does It Matter?

Phase gating enforces sequential workflow execution with validation checkpoints, preventing premature advancement and ensuring quality.

### Sequential Execution

Workflows enforce **strict phase order**:

1. ✅ Can only access current phase
2. ✅ Must complete current phase to advance
3. ❌ Cannot skip phases
4. ❌ Cannot access future phases

### Checkpoint Validation

Each phase has **checkpoint requirements**:

```python
# Submit evidence to complete phase
await mcp_agent-os-rag_complete_phase(
    session_id="session_123",
    phase=1,
    evidence={
        "functions_analyzed": 12,
        "classes_identified": 3,
        "test_strategy": "unit + integration",
        "coverage_goal": 80
    }
)
```

**Evidence must include:**
- Required fields (defined in metadata)
- Quantifiable metrics
- Validation criteria met

---

## What Is Horizontal Scaling in Workflows? (v1.3.0)

Horizontal scaling breaks large workflows into focused, on-demand task files to preserve AI context efficiency.

### Task-Level Execution

Workflows now enforce **horizontal scaling** - working on one task at a time instead of loading all tasks upfront.

**Meta-Framework Principle:** Break work into small, focused chunks (≤100 lines each)

### The Pattern

```python
# Step 1: Get phase overview (task metadata only)
phase = await mcp_agent-os-rag_get_current_phase(session_id="session_123")

print(f"Phase {phase['current_phase']}: {len(phase['phase_content']['tasks'])} tasks")
for task_meta in phase['phase_content']['tasks']:
    print(f"  {task_meta['task_number']}: {task_meta['task_name']}")

# Step 2: Get FIRST task's full content
task = await mcp_agent-os-rag_get_task(
    session_id="session_123",
    phase=1,
    task_number=1
)

print(f"\n=== {task['task_name']} ===")
print(f"Content: {len(task['content'])} characters")
print(f"Steps: {len(task['steps'])} execution steps")

# Step 3: Execute the task
evidence = {}
for step in task['steps']:
    if step['type'] == 'execute_command':
        # Substitute variables
        cmd = step['command'].replace('[PRODUCTION_FILE]', task['target_file'])
        result = await run_terminal_cmd(cmd)
        
        # Collect evidence
        if step['evidence_required']:
            evidence[step['evidence_required']] = parse(result)

# Step 4: Get NEXT task and repeat
task2 = await mcp_agent-os-rag_get_task(session_id="session_123", phase=1, task_number=2)
# ... execute task 2 ...

# Step 5: Complete phase with evidence
await mcp_agent-os-rag_complete_phase(
    session_id="session_123",
    phase=1,
    evidence=evidence
)
```

### Why This Matters

**Before (v1.2.3):** Returned all tasks at once
- ❌ 10KB+ of content in single response
- ❌ Agent loses focus with too much context
- ❌ Wastes tokens on tasks not yet relevant
- ❌ Violates horizontal scaling principle

**After (v1.3.0):** Get task list, then one task at a time
- ✅ ~200 bytes for task list
- ✅ ~1-2KB per task (focused attention)
- ✅ Load only what's needed now
- ✅ Honors meta-workflow architecture

### Benefits

1. **Focused Attention** - One atomic work unit in context
2. **Token Efficiency** - Only load current task
3. **Clear Progress** - "Working on task 2 of 5"
4. **Sequential Flow** - API enforces task order
5. **Complete Content** - Retrieves ALL chunks for the task

---

## How to Create New Workflows?

Guidelines for designing and implementing new workflows that follow prAxIs OS standards.

### Step 1: Define Metadata

Create `universal/workflows/{workflow_name}/metadata.json`:

```json
{
  "workflow_type": "api_validation",
  "version": "1.0.0",
  "description": "Validate API design and implementation",
  "total_phases": 4,
  "estimated_duration": "45-60 minutes",
  "primary_outputs": [
    "API validation report",
    "Compliance checklist",
    "Recommendations"
  ],
  "phases": [
    {
      "phase_number": 0,
      "phase_name": "API Discovery",
      "purpose": "Identify all API endpoints and contracts",
      "estimated_effort": "10 minutes",
      "key_deliverables": [
        "Endpoint inventory",
        "Contract definitions"
      ],
      "validation_criteria": [
        "All endpoints documented",
        "Contracts validated"
      ]
    }
    // ... more phases
  ]
}
```

### Step 2: Index the Workflow

Metadata is automatically indexed when:
- File is created in `universal/workflows/`
- File watcher detects changes
- Index rebuild includes workflows directory

### Step 3: Test Discovery

```python
# Verify workflow is discoverable
result = await mcp_agent-os-rag_search_standards(
    query="API validation workflow",
    n_results=3
)
# Should return your new workflow metadata
```

---

## What Standard Workflows Are Available?

prAxIs OS includes battle-tested workflows for common development tasks.

### test_generation_v3

**Purpose:** Generate comprehensive test suites with validation gates

**Phases:** 8 (Setup → Analysis → Unit → Integration → Validation → Coverage → Refinement → Documentation)

**Duration:** 2-3 hours

**Outputs:** Unit tests, integration tests, validation tests, coverage report

**Use When:**
- Need comprehensive test coverage
- Working with untested or under-tested code
- Systematic test generation required

### production_code_v2

**Purpose:** Generate production-quality code with architectural validation

**Phases:** 6 (Requirements → Design → Core → Integration → Validation → Documentation)

**Duration:** 1-2 hours

**Outputs:** Production code, API docs, integration guides, architecture diagrams

**Use When:**
- Building new features or modules
- Need production-quality implementation
- Architectural compliance required

---

## How Does Workflow State Management Work?

State management ensures workflows are persistent, resumable, and recoverable across sessions.

### Session Persistence

Workflows maintain **persistent state**:

- Session ID for resume capability
- Current phase tracking
- Completed phases history
- Phase artifacts (evidence + outputs)
- Checkpoint validation results

### Resuming Workflows

```python
# Start workflow (or resume if session exists)
result = await mcp_agent-os-rag_start_workflow(
    workflow_type="test_generation_v3",
    target_file="auth.py"
)

# If session exists for this file:
# - Returns existing session
# - Shows current phase
# - Includes completed phases
# - Workflow overview still included
```

---

## What Common Workflow Mistakes Should I Avoid?

These anti-patterns defeat the purpose of workflows. Recognize and avoid them.

### ❌ DON'T: Skip Phases

```python
# BAD: Trying to complete phase 3 when on phase 1
await complete_phase(session_id="...", phase=3, evidence={...})
# Result: ERROR - Phase sequence violation
```

### ❌ DON'T: Provide Incomplete Evidence

```python
# BAD: Missing required evidence fields
await complete_phase(
    session_id="...",
    phase=1,
    evidence={"some_field": "value"}
)
# Result: Checkpoint validation failed
```

### ❌ DON'T: Read Workflow Files Directly

```python
# BAD: Direct file access
with open("universal/workflows/test_generation_v3/metadata.json") as f:
    metadata = json.load(f)
```

### ✅ DO: Use MCP Tools

```python
# GOOD: Use start_workflow to get metadata
result = await start_workflow("test_generation_v3", "file.py")
metadata = result["workflow_overview"]
```

---

## What Are Workflow System Best Practices?

Proven practices for effective workflow usage and creation.

### 1. Query Before Starting

```python
# Discover workflow capabilities first
discovery = await pos_search_project(
    query="What does test_generation_v3 workflow produce?",
    n_results=3
)
# Understand deliverables before committing

# Then start with full knowledge
session = await start_workflow("test_generation_v3", "auth.py")
```

### 2. Use Overview for Planning

```python
session = await start_workflow("test_generation_v3", "auth.py")
overview = session["workflow_overview"]

# Plan your approach
print(f"Total phases: {overview['total_phases']}")
print(f"Estimated duration: {overview['estimated_duration']}")

for phase in overview["phases"]:
    print(f"Phase {phase['phase_number']}: {phase['phase_name']}")
    print(f"  Effort: {phase['estimated_effort']}")
    print(f"  Deliverables: {phase['key_deliverables']}")
```

### 3. Provide Quantified Evidence

```python
# GOOD: Specific, measurable evidence
evidence = {
    "functions_identified": 15,
    "classes_identified": 3,
    "test_types_determined": ["unit", "integration"],
    "coverage_goal_percent": 85,
    "complexity_analysis": "moderate"
}
```

### 4. Handle Validation Failures

```python
result = await complete_phase(session_id, phase, evidence)

if not result["checkpoint_passed"]:
    missing = result["missing_evidence"]
    print(f"Missing evidence: {missing}")
    # Collect missing evidence and retry
```

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Understanding workflows** | `pos_search_project(content_type="standards", query="workflow system")` |
| **Starting workflow** | `pos_search_project(content_type="standards", query="how to start workflow")` |
| **Phase gating** | `pos_search_project(content_type="standards", query="phase gating")` |
| **Horizontal scaling** | `pos_search_project(content_type="standards", query="workflow horizontal scaling")` |
| **Workflow discovery** | `pos_search_project(content_type="standards", query="workflow discovery")` |
| **Available workflows** | `pos_search_project(content_type="standards", query="standard workflows")` |
| **Creating workflow** | `pos_search_project(content_type="standards", query="create new workflow")` |
| **State management** | `pos_search_project(content_type="standards", query="workflow state")` |
| **MCP tools** | `pos_search_project(content_type="standards", query="workflow MCP tools")` |
| **Best practices** | `pos_search_project(content_type="standards", query="workflow best practices")` |

---

## 🔗 Related Standards

**Query workflow for complete workflow understanding:**

1. **Start with system overview** → `pos_search_project(content_type="standards", query="workflow system")` (this document)
2. **Learn metadata structure** → `pos_search_project(content_type="standards", query="workflow metadata")` → `standards/workflows/workflow-metadata-standards.md`
3. **Understand construction** → `pos_search_project(content_type="standards", query="workflow construction")` → `standards/workflows/workflow-construction-standards.md`
4. **Learn RAG configuration** → `pos_search_project(content_type="standards", query="MCP RAG configuration")` → `standards/workflows/mcp-rag-configuration.md`

**By Category:**

**Workflows:**
- `standards/workflows/workflow-metadata-standards.md` - metadata.json structure → `pos_search_project(content_type="standards", query="workflow metadata")`
- `standards/workflows/workflow-construction-standards.md` - Building workflows → `pos_search_project(content_type="standards", query="workflow construction")`
- `standards/workflows/mcp-rag-configuration.md` - RAG indexing → `pos_search_project(content_type="standards", query="MCP RAG configuration")`

**Meta-Framework:**
- `standards/meta-workflow/validation-gates.md` - Checkpoint validation → `pos_search_project(content_type="standards", query="validation gates")`
- `standards/meta-workflow/command-language.md` - Command symbols → `pos_search_project(content_type="standards", query="command language")`
- `standards/meta-workflow/framework-creation-principles.md` - Framework design → `pos_search_project(content_type="standards", query="framework creation principles")`
- `standards/meta-workflow/horizontal-decomposition.md` - Task breakdown → `pos_search_project(content_type="standards", query="horizontal decomposition")`

**Usage:**
- `usage/mcp-usage-guide.md` - Using MCP tools → `pos_search_project(content_type="standards", query="MCP usage guide")`
- `usage/operating-model.md` - prAxIs OS principles → `pos_search_project(content_type="standards", query="prAxIs OS operating model")`

---

## 📖 Version History

### v1.2.0 (2025-10-06)
- Added workflow overview in `start_workflow` response
- Workflow metadata indexed in RAG for discovery
- Enhanced MCP tool integration

### v1.0.0 (2025-10-05)
- Initial workflow system with phase gating
- Checkpoint validation
- State persistence

---

**Remember:** Workflows provide structured, validated execution paths for complex AI-assisted tasks. Use MCP tools to discover, start, and complete workflows systematically.

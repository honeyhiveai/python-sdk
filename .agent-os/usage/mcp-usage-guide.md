# MCP Tool Usage Guide

**Guide for using Model Context Protocol (MCP) tools in Agent OS projects.**

---

## 🎯 What Is MCP?

**Model Context Protocol (MCP)** allows AI assistants to access tools and information through a standardized interface. In Agent OS, MCP provides:

- 📚 **Semantic search** over standards and docs
- 🔄 **Workflow execution** with phase gating
- 🎯 **Context reduction** (50KB → 5KB per query)
- ✅ **Architectural enforcement** (prevents AI shortcuts)

---

## 🚀 Available MCP Tools

### 1. `search_standards`

**Purpose:** Semantic search over all Agent OS standards and documentation

**When to use:**
- Need guidance on a pattern or practice
- Looking for examples
- Want to understand a concept
- Checking if something already exists

**Example:**
```python
mcp_agent-os-rag_search_standards(
    query="How should I handle race conditions in concurrent code?",
    n_results=5
)
```

**Returns:** Relevant chunks from standards with context

---

### 2. `start_workflow`

**Purpose:** Initialize a phase-gated workflow (e.g., test generation, production code)

**When to use:**
- Generating tests
- Creating production code
- Following a structured process

**NEW in v1.2.0:** Returns complete workflow overview upfront!

**Example:**
```python
session = mcp_agent-os-rag_start_workflow(
    workflow_type="test_generation_v3",
    target_file="auth.py"
)

# NEW: Workflow overview included
overview = session["workflow_overview"]
print(f"Total phases: {overview['total_phases']}")  # 8
print(f"Duration: {overview['estimated_duration']}")  # "2-3 hours"

# See all phases before starting
for phase in overview["phases"]:
    print(f"Phase {phase['phase_number']}: {phase['phase_name']}")
```

**Returns:** Session ID, Phase 0 content, and complete workflow overview

**Discovery Tip:** Use `search_standards` to discover available workflows before starting:
```python
# Find workflows for your task
result = mcp_agent-os-rag_search_standards(
    query="What workflows are available for testing Python code?",
    n_results=5
)
# Returns: Workflow metadata with descriptions and capabilities
```

---

### 3. `get_current_phase`

**Purpose:** Get current phase overview with task metadata (v1.3.0: Now returns task list only)

**When to use:**
- During workflow execution
- Need to see what tasks are in the current phase
- Planning your work sequence

**NEW in v1.3.0:** Returns task metadata only (not full content) - enforces horizontal scaling!

**Example:**
```python
phase = mcp_agent-os-rag_get_current_phase(
    session_id="workflow_session_123"
)

# See what tasks are available
print(f"Phase {phase['current_phase']}: {len(phase['phase_content']['tasks'])} tasks")

for task_meta in phase['phase_content']['tasks']:
    print(f"  Task {task_meta['task_number']}: {task_meta['task_name']}")
    # Note: No full content here - use get_task to retrieve it
```

**Returns:** 
- Phase number and name
- General phase guidance (`content_chunks`)
- Task metadata list: `task_number`, `task_name`, `task_file` (no full content)
- Message: "Use get_task(session_id, phase, task_number) to retrieve full task content"

---

### 4. `get_task` ⭐ NEW in v1.3.0

**Purpose:** Get complete content for a specific task (horizontal scaling)

**When to use:**
- After seeing task list from `get_current_phase`
- Ready to work on a specific task
- Need task execution steps and commands
- Following meta-framework's "one task at a time" principle

**Why this tool?**
- ✅ Focused attention (one task in context at a time)
- ✅ Token efficient (only load what you need now)
- ✅ Complete content (retrieves ALL chunks for the task)
- ✅ Sequential execution (natural workflow progression)

**Example:**
```python
# Step 1: See what tasks exist
phase = mcp_agent-os-rag_get_current_phase(session_id="workflow_123")

# Step 2: Get first task's full content
task = mcp_agent-os-rag_get_task(
    session_id="workflow_123",
    phase=1,
    task_number=1
)

print(f"Task: {task['task_name']}")
print(f"Content: {len(task['content'])} characters")
print(f"Steps: {len(task['steps'])} execution steps")

# Step 3: Execute the task
for step in task['steps']:
    if step['type'] == 'execute_command':
        # Substitute variables
        cmd = step['command'].replace('[PRODUCTION_FILE]', task['target_file'])
        result = run_command(cmd)
        
        # Collect evidence
        if step['evidence_required']:
            evidence[step['evidence_required']] = parse(result)
```

**Parameters:**
- `session_id`: Workflow session ID
- `phase`: Phase number (can reference previous phases)
- `task_number`: Task number within the phase

**Returns:**
- Complete task markdown (`content`)
- Structured execution steps (`steps`)
  - `type`: "execute_command" or "decision_point"
  - `command`: Bash command to execute
  - `description`: What this step does
  - `evidence_required`: What to document
- Task metadata (name, file, number)
- Session context (workflow_type, target_file, current_phase)

**Workflow Pattern:**
```python
# Get phase overview
phase = get_current_phase(session_id)
evidence = {}

# Work through tasks sequentially
for task_meta in phase['phase_content']['tasks']:
    # Get full task content
    task = get_task(session_id, phase['current_phase'], task_meta['task_number'])
    
    # Execute steps
    for step in task['steps']:
        result = execute(step)
        evidence[f"task_{task['task_number']}_{step['evidence_required']}"] = result
    
# Complete phase
complete_phase(session_id, phase['current_phase'], evidence)
```

---

### 5. `complete_phase`

**Purpose:** Submit evidence and advance to next phase

**When to use:**
- Finished current phase
- Have quantified evidence
- Ready to proceed

**Example:**
```python
mcp_agent-os-rag_complete_phase(
    session_id="workflow_session_123",
    phase=0,
    evidence={"functions_identified": 5, "classes_identified": 2}
)
```

**Returns:** Validation result + next phase content (if passed)

---

### 6. `get_workflow_state`

**Purpose:** Query complete workflow state

**When to use:**
- Debugging workflow
- Checking progress
- Resuming interrupted workflow

**Example:**
```python
mcp_agent-os-rag_get_workflow_state(
    session_id="workflow_session_123"
)
```

**Returns:** Full state including phases completed, evidence collected

---

### 7. `create_workflow`

**Purpose:** Generate new workflow framework using meta-framework principles

**When to use:**
- Creating a new structured process
- Need phase-gated workflow for specific task
- Building reusable framework

**Example:**
```python
mcp_agent-os-rag_create_workflow(
    name="api-documentation",
    workflow_type="documentation",
    phases=["Analysis", "Generation", "Validation"],
    target_language="python"
)
```

**Returns:** Generated framework files and compliance report

---

## 🚨 Critical Rules

### 1. **NEVER Bypass MCP**

❌ **DON'T:**
```python
# Reading .agent-os/ directly
with open(".agent-os/standards/testing/test-pyramid.md") as f:
    content = f.read()
```

✅ **DO:**
```python
# Use MCP tool
mcp_agent-os-rag_search_standards(
    query="test pyramid principles"
)
```

**Why:** MCP provides context reduction (90%) and tracks usage

---

### 2. **Use MCP for All Standards Access**

**Exception:** Only when **authoring/maintaining** standards files

- ✅ **Consumption mode**: Use MCP tools
- ✅ **Authorship mode**: Direct file access (when writing standards)

---

### 3. **Follow Workflow Phase Gating**

When in a workflow:
1. ✅ Use `get_current_phase` to get requirements
2. ✅ Complete phase requirements
3. ✅ Use `complete_phase` with evidence
4. ❌ DON'T skip phases
5. ❌ DON'T read future phases directly

---

## 💡 Best Practices

### Semantic Queries

**Good queries (specific, complete questions):**
- ✅ "How should I structure integration tests in Python?"
- ✅ "What are the best practices for handling database migrations?"
- ✅ "Where should I place utility functions in the codebase?"

**Bad queries (too vague or single words):**
- ❌ "tests"
- ❌ "database"
- ❌ "python patterns"

---

### Workflow Usage

1. **Start with binding contract acknowledgment**
2. **Read phase requirements carefully**
3. **Provide quantified evidence** (counts, metrics)
4. **Don't assume - query standards** when unsure
5. **Complete phases systematically** (no skipping)

---

## 📋 Quick Reference

| Task | MCP Tool | Example Query |
|------|----------|---------------|
| Find pattern | `search_standards` | "concurrency race conditions" |
| Generate tests | `start_workflow` | type="test_generation_v3" |
| Check phase | `get_current_phase` | session_id="..." |
| Submit evidence | `complete_phase` | phase=1, evidence={...} |
| Create framework | `create_workflow` | name="...", phases=[...] |

---

## 🔍 Troubleshooting

### "No results found"
- Make query more specific
- Try different wording
- Check spelling
- Broaden search terms

### "Phase validation failed"
- Review evidence requirements
- Ensure quantified metrics provided
- Check evidence format matches expected schema
- Read validation error message carefully

### "Workflow not found"
- Check session_id is correct
- Workflow may have expired
- Start new workflow if needed

---

##📞 Questions?

- **Tool behavior**: Query MCP: `"mcp tool routing guide"`
- **Standards access**: Use `search_standards` with your question
- **Workflow help**: Read workflow entry point (via `get_current_phase`)

---

**Remember:** MCP tools are your primary interface to Agent OS knowledge. Use them instead of direct file access for 90% context reduction and better AI assistance!

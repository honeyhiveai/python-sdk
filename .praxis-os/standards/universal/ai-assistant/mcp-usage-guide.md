# MCP Tool Usage Guide

**Guide for using Model Context Protocol (MCP) tools in prAxIs OS projects.**

**Keywords for search**: MCP tools, Model Context Protocol, how to use MCP tools, search_standards, start_workflow, workflow tools, MCP usage, semantic search, phase gating, tool discovery

---

## 🚨 Quick Reference (TL;DR)

**What is MCP?** Model Context Protocol - standardized interface for AI assistants to access tools and information.

**8 Core MCP Tools:**
1. **`pos_search`** - Semantic search over prAxIs OS docs (use 5-10+ times per task)
2. **`start_workflow`** - Initialize phase-gated workflows
3. **`get_current_phase`** - Retrieve current workflow phase
4. **`get_task`** - Get specific task details (NEW in v1.3.0)
5. **`complete_phase`** - Submit evidence and advance
6. **`get_workflow_state`** - Check workflow progress
7. **`create_workflow`** - Generate new workflow frameworks
8. **`current_date`** - Get current date/time

**Critical Rules:**
- ✅ **NEVER bypass MCP** - Always use `pos_search()`, never `read_file()` for standards
- ✅ **Query liberally** - 5-10+ queries per task, not just once
- ✅ **Follow phase gating** - Use workflows for structured tasks

---

## Questions This Answers

- "How do I use MCP tools in prAxIs OS?"
- "What is the Model Context Protocol?"
- "How do I search for standards using MCP?"
- "How do I start a workflow?"
- "What MCP tools are available?"
- "Should I use read_file or pos_search?"
- "How do I get workflow tasks?"
- "How do I complete a workflow phase?"
- "What is phase gating?"
- "How often should I query standards?"

---

## 🎯 What Is MCP?

**Model Context Protocol (MCP)** allows AI assistants to access tools and information through a standardized interface. In prAxIs OS, MCP provides:

- 📚 **Semantic search** over standards and docs
- 🔄 **Workflow execution** with phase gating
- 🎯 **Context reduction** (50KB → 5KB per query)
- ✅ **Architectural enforcement** (prevents AI shortcuts)

---

## 🚀 Available MCP Tools

**Tool Discovery:** The MCP protocol provides built-in tool introspection via `tools/list`, which returns all available tools with their parameter schemas. Cursor IDE handles this automatically when you invoke MCP tools.

### 1. `pos_search`

**Purpose:** Semantic search over all prAxIs OS standards and documentation

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
# Example 1: Test generation workflow
session = mcp_agent-os-rag_start_workflow(
    workflow_type="test_generation_v3",
    target_file="auth.py"  # File path for code workflows
)

# Example 2: Spec execution workflow (different pattern!)
session = mcp_agent-os-rag_start_workflow(
    workflow_type="spec_execution_v1",
    target_file="my-feature-name",  # Simple identifier, NOT a path
    options={"spec_path": ".praxis-os/specs/2025-10-07-my-feature-name"}  # Full path in options
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

**Important:** The `target_file` parameter usage varies by workflow:
- For code workflows (`test_generation_v3`, `production_code_v2`): Use file path (e.g., `"src/auth.py"`)
- For spec workflows (`spec_execution_v1`): Use simple identifier (e.g., `"my-feature"`), put full path in `options.spec_path`

**Discovery Tip:** Use `pos_search` to discover available workflows before starting:
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
- Following meta-workflow's "one task at a time" principle

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

**Purpose:** Generate new workflow framework using meta-workflow principles

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

### 8. `current_date`

**Purpose:** Get current date/time to prevent AI date errors

**When to use:**
- Creating specs or documentation with dates
- Generating timestamped directories or files
- Any content requiring accurate current date

**Example:**
```python
date_info = mcp_agent-os-rag_current_date()
print(date_info["iso_date"])  # "2025-10-07"
print(date_info["iso_datetime"])  # "2025-10-07T14:30:00-07:00"
```

**Returns:** Dictionary with current date/time in multiple formats

---

## 🔍 Tool Discovery

### MCP Protocol Introspection

The MCP protocol includes built-in tool discovery capabilities:

1. **`tools/list`** - Returns all available MCP tools with:
   - Tool name
   - Description
   - Parameter schema (names, types, required/optional)
   - Return value schema

2. **`resources/list`** - Returns available resources (use `list_mcp_resources` tool)

3. **`prompts/list`** - Returns available prompts (if server exposes any)

**Note:** Cursor IDE automatically handles these protocol-level calls. When you need to know what tools are available or what parameters they take, you can:
- Check this documentation
- Rely on Cursor's autocomplete (uses `tools/list` under the hood)
- Use the MCP inspector in Cursor's dev tools

---

## 🚨 Critical Rules

### 1. **NEVER Bypass MCP**

❌ **DON'T:**
```python
# Reading .praxis-os/ directly
with open(".praxis-os/standards/testing/test-pyramid.md") as f:
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
| Find pattern | `pos_search` | "concurrency race conditions" |
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

## When to Query This Guide

This guide is most valuable when:

1. **Starting to Use MCP Tools**
   - Situation: First time using prAxIs OS MCP tools
   - Query: `pos_search(content_type="standards", query="how to use MCP tools")`

2. **Choosing Between Tools**
   - Situation: Not sure which MCP tool to use
   - Query: `pos_search(content_type="standards", query="MCP tools available")`

3. **Workflow Questions**
   - Situation: Need to understand workflow execution
   - Query: `pos_search(content_type="standards", query="how to start workflow")`

4. **Search vs Read File**
   - Situation: Unsure if I should use `pos_search` or `read_file`
   - Query: `pos_search(content_type="standards", query="pos_search vs read_file")`

5. **Phase Gating Questions**
   - Situation: Understanding workflow phase progression
   - Query: `pos_search(content_type="standards", query="workflow phase gating")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| MCP overview | `pos_search(content_type="standards", query="what is MCP")` |
| Available tools | `pos_search(content_type="standards", query="MCP tools available")` |
| Search standards | `pos_search(content_type="standards", query="how to use pos_search")` |
| Start workflow | `pos_search(content_type="standards", query="how to start workflow")` |
| Complete phase | `pos_search(content_type="standards", query="how to complete workflow phase")` |

---

## Cross-References and Related Guides

**Core Orientation:**
- `usage/ai-agent-quickstart.md` - Practical examples of using MCP tools
  → `pos_search(content_type="standards", query="AI agent quickstart")`
- `standards/universal/ai-assistant/PRAXIS-OS-ORIENTATION.md` - MCP in context of prAxIs OS principles
  → `pos_search(content_type="standards", query="prAxIs OS orientation")`

**Workflows:**
- `workflows/spec_execution_v1/` - Example of phase-gated workflow
  → `pos_search(content_type="standards", query="spec execution workflow")`
- `workflows/test_generation_v3/` - Test generation workflow
  → `pos_search(content_type="standards", query="test generation workflow")`

**Standards:**
- `standards/documentation/rag-content-authoring.md` - How content is optimized for search
  → `pos_search(content_type="standards", query="RAG content authoring")`

**Query workflow:**
1. **First Use**: `pos_search(content_type="standards", query="how to use MCP tools")` → Learn tool basics
2. **During Work**: Use `pos_search()` liberally (5-10+ times per task)
3. **Workflows**: `pos_search(content_type="standards", query="how to start workflow")` → Execute structured tasks
4. **Troubleshooting**: `pos_search(content_type="standards", query="MCP tool usage")` → Resolve issues

---

## 📞 Questions?

- **Tool behavior**: Query MCP: `pos_search(content_type="standards", query="mcp tool routing guide")`
- **Standards access**: Use `pos_search` with your question
- **Workflow help**: Read workflow entry point (via `get_current_phase`)

---

**Remember:** MCP tools are your primary interface to prAxIs OS knowledge. Use them instead of direct file access for 90% context reduction and better AI assistance!

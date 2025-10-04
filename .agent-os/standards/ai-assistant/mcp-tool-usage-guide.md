# MCP Tool Usage Guide
**Complete reference for Agent OS MCP/RAG tools**

100% AI-authored via human orchestration.

---

## 🎯 Quick Decision Tree

**Question about process/workflow?** → `search_standards`  
**Question about SDK API?** → `search_docs` (future)  
**Need to generate tests?** → `start_workflow(type="test_generation_v3")`  
**Need to generate production code?** → `start_workflow(type="production_code_v2")`  
**Uncertain which tool?** → `search_standards(query="[your question]")` (always safe)

---

## 📚 Available MCP Tools

### Core Search Tools

#### `mcp_agent-os-rag_search_standards`
**Corpus:** Agent OS standards (development process, frameworks, rules)  
**Use for:**
- "How do I generate tests?"
- "What are the git safety rules?"
- "Operating model clarification"
- "Credential file protection rules"
- "Import verification rules"
- "Quality gate requirements"

**Parameters:**
```python
search_standards(
    query: str,           # Natural language question
    n_results: int = 5,   # Number of chunks to return
    filter_phase: int = None,      # Optional: filter by phase number
    filter_tags: list[str] = None  # Optional: filter by tags
)
```

**Example Queries:**
- `"git safety rules forbidden operations"`
- `"credential file protection rules for .env files"`
- `"test generation framework phase 1 requirements"`
- `"operating model roles paradigm"`

**Returns:** 5-10 relevant chunks (5KB total) instead of full files (50KB)

---

### Workflow Management Tools

#### `mcp_agent-os-rag_start_workflow`
**Purpose:** Initialize phase-gated workflow for systematic code generation  
**Use for:**
- Test generation (V3 framework with 8 phases)
- Production code generation (V2 framework with complexity-based paths)

**Parameters:**
```python
start_workflow(
    workflow_type: str,  # "test_generation_v3" or "production_code_v2"
    target_file: str     # File being worked on (e.g., "src/honeyhive/tracer.py")
)
```

**Returns:**
- `session_id`: Unique workflow session identifier
- `current_phase`: Phase 1 content and requirements
- `acknowledgment_required`: Must acknowledge before proceeding

**Example:**
```python
result = start_workflow(
    workflow_type="test_generation_v3",
    target_file="src/honeyhive/api/client.py"
)
# Returns Phase 1: Analysis requirements only (not all 8 phases)
```

---

#### `mcp_agent-os-rag_get_current_phase`
**Purpose:** Retrieve current phase requirements  
**Use for:**
- Checking what phase you're currently on
- Getting current phase content and requirements
- Reviewing artifacts from completed phases

**Parameters:**
```python
get_current_phase(
    session_id: str  # From start_workflow response
)
```

**Returns:**
- `current_phase`: Phase number
- `phase_content`: Requirements and guidance for current phase
- `artifacts`: Evidence and outputs from completed phases

---

#### `mcp_agent-os-rag_complete_phase`
**Purpose:** Submit evidence and attempt phase completion  
**Use for:**
- Advancing to next phase after completing requirements
- Validating evidence against checkpoint criteria

**Parameters:**
```python
complete_phase(
    session_id: str,
    phase: int,         # Phase number being completed
    evidence: dict      # Evidence matching checkpoint criteria
)
```

**Returns:**
- `checkpoint_passed`: True if evidence validates
- `missing_evidence`: List of missing criteria (if failed)
- `next_phase_content`: Content for next phase (if passed)

**Example:**
```python
result = complete_phase(
    session_id="abc-123",
    phase=1,
    evidence={
        "test_file_created": True,
        "framework_decision": "pytest",
        "function_count": 12,
        "class_count": 3
    }
)
# If passed: Returns Phase 2 content
# If failed: Returns missing evidence list
```

---

#### `mcp_agent-os-rag_get_workflow_state`
**Purpose:** Query complete workflow state for debugging/resume  
**Use for:**
- Checking overall workflow progress
- Debugging workflow issues
- Resuming interrupted workflows

**Parameters:**
```python
get_workflow_state(
    session_id: str
)
```

**Returns:**
- `workflow_type`: Type of workflow
- `current_phase`: Current phase number
- `completed_phases`: List of completed phases
- `artifacts`: All artifacts from completed phases
- `can_resume`: Whether workflow can be resumed

---

## 🎯 Tool Selection Guidelines

### When to Use `search_standards`

**Always use for:**
- ✅ Process questions: "How do I X?"
- ✅ Rule queries: "What are the rules for Y?"
- ✅ Framework questions: "What's the test generation workflow?"
- ✅ Operating model: "What's my role?"
- ✅ Compliance checks: "Can I write to .env?"
- ✅ Quality requirements: "What's the Pylint target?"

**Examples:**
```python
# Git operation question
search_standards(query="git safety rules forbidden operations")

# Credential file question
search_standards(query="credential file protection rules for .env files")

# Test generation question
search_standards(query="test generation framework V3 overview")

# Import verification
search_standards(query="import path verification rules 2-minute rule")
```

---

### When to Use `start_workflow`

**Always use for:**
- ✅ Generating test files (unit or integration)
- ✅ Generating production code (functions, classes, modules)
- ✅ Any systematic code generation requiring phase gating

**Never use for:**
- ❌ Simple edits to existing files
- ❌ Bug fixes
- ❌ Documentation updates
- ❌ Configuration changes

**Decision criteria:**
```
If generating new code file → start_workflow
If editing existing file → search_standards for guidance, then implement
```

---

### When to Use `get_current_phase`

**Use when:**
- ✅ You're in an active workflow and forgot current phase
- ✅ You need to review completed phase artifacts
- ✅ You want to see current requirements before proceeding

**Example:**
```python
# Check where I am in workflow
state = get_current_phase(session_id="abc-123")
# Returns: Phase 3 requirements + Phase 1-2 artifacts
```

---

### When to Use `complete_phase`

**Use when:**
- ✅ You've completed all requirements for current phase
- ✅ You have evidence ready to submit
- ✅ You want to advance to next phase

**Never use:**
- ❌ Without completing current phase requirements
- ❌ Without evidence to submit
- ❌ To skip phases

**Example:**
```python
# After completing Phase 1 analysis
result = complete_phase(
    session_id="abc-123",
    phase=1,
    evidence={
        "function_count": 8,
        "class_count": 2,
        "complexity_assessment": "medium"
    }
)
```

---

## 🚨 Common Mistakes to Avoid

### Mistake 1: Reading .agent-os/ directly instead of using MCP
```
❌ WRONG:
read_file(".agent-os/standards/ai-assistant/code-generation/tests/v3/phase-1.md")

✅ CORRECT:
search_standards(query="test generation phase 1 requirements")
```

### Mistake 2: Skipping workflow for code generation
```
❌ WRONG:
User: "Generate tests for tracer.py"
AI: [Directly writes test file without workflow]

✅ CORRECT:
result = start_workflow(
    workflow_type="test_generation_v3",
    target_file="src/honeyhive/tracer.py"
)
[Follow phase-by-phase guidance]
```

### Mistake 3: Submitting incomplete evidence
```
❌ WRONG:
complete_phase(session_id="abc", phase=1, evidence={"done": True})

✅ CORRECT:
complete_phase(
    session_id="abc",
    phase=1,
    evidence={
        "function_count": 12,
        "class_count": 3,
        "framework_decision": "pytest",
        "complexity_assessment": "medium"
    }
)
```

---

## 🎯 Advanced Patterns

### Pattern 1: Iterative Refinement
```python
# Initial query
results = search_standards(query="test generation framework")

# Refine based on results
results = search_standards(
    query="test generation phase 1 analysis requirements",
    filter_phase=1
)
```

### Pattern 2: Cross-Referencing
```python
# Get workflow guidance
search_standards(query="test generation V3 workflow overview")

# Start workflow
start_workflow(workflow_type="test_generation_v3", target_file="...")

# Query specific phase details as needed
search_standards(query="phase 3 dependency analysis mocking strategy")
```

---

**Document Status:** Complete - MCP Tool Reference  
**Purpose:** Comprehensive guide for MCP tool selection and usage  
**Related:** `OPERATING-MODEL.md`, `mcp-enforcement-rules.md`

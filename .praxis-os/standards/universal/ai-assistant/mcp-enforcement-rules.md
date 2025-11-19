# MCP Enforcement Rules
**Why MCP exists and how to use it correctly**

100% AI-authored via human orchestration.

---

## 🎯 The Problem MCP/RAG Solves

### Before MCP/RAG
```
User: "What are the Phase 1 requirements for test generation?"

AI Behavior:
├── read_file(".agent-os/standards/ai-assistant/code-generation/tests/v3/framework-core.md")
│   └── Loads: 500 lines (12,000 tokens)
├── Scans entire file looking for Phase 1 content
├── Context window: 12,000 tokens consumed
└── AI sees all 8 phases when should only see Phase 1

Problem: 96% context waste (need 500 tokens, load 12,000 tokens)
```

### After MCP/RAG
```
User: "What are the Phase 1 requirements for test generation?"

AI Behavior:
├── mcp_agent-os-rag_pos_search_project(action="search_standards", query=query="test generation phase 1 requirements")
├── MCP searches vector index semantically
├── Returns: 3 relevant chunks (500 tokens total)
└── AI sees only Phase 1 content

Result: 90% context reduction (12,000 → 500 tokens)
```

**This is why MCP exists:** Context efficiency through semantic search.

---

## 🚨 Forbidden Operations

### NEVER Bypass MCP to Read .agent-os/ Directly

**Forbidden tool calls:**
```python
# ❌ FORBIDDEN
read_file(".agent-os/standards/...")
read_file(".agent-os/specs/...")
codebase_search(target_directories=[".agent-os"])
grep(path=".agent-os/...")
list_dir(".agent-os/standards")
```

**Why forbidden:**
1. **Context waste**: You'll read 50KB when you need 5KB
2. **Wrong scope**: You'll see all 8 phases when you should only see Phase 1
3. **Defeats architecture**: Bypasses the 90% context reduction we built
4. **Demonstrates the problem**: You're doing exactly what MCP/RAG was built to prevent

---

## ✅ The ONLY Exception: Authorship Mode

**Direct file access IS allowed when writing/maintaining standards:**

### Authorship Mode (Direct Access OK)
```python
# ✅ ALLOWED: Writing NEW standards
User: "Create a rule for X"
AI: read_file(".agent-os/standards/...") to check existing structure
AI: write new standard file

# ✅ ALLOWED: Updating EXISTING standards
User: "Update the test framework to include Y"
AI: read_file(".agent-os/standards/ai-assistant/code-generation/tests/...")
AI: Update the standard

# ✅ ALLOWED: Maintaining MCP server code
User: "Add a new tool to the MCP server"
AI: read_file(".agent-os/mcp_servers/agent_os_rag.py")
AI: Implement new tool

# ✅ ALLOWED: Updating specification documents
User: "Update tasks.md to mark Phase 1 complete"
AI: read_file(".agent-os/specs/*/tasks.md")
AI: Update task status

# ✅ ALLOWED: Maintaining RAG infrastructure
User: "Fix the index builder"
AI: read_file(".agent-os/scripts/build_rag_index.py")
AI: Fix the script

# ✅ ALLOWED: User explicitly says
User: "Read the file .agent-os/standards/X.md"
AI: read_file(".agent-os/standards/X.md")
```

### Consumption Mode (MCP REQUIRED)
```python
# ❌ FORBIDDEN: Reading for guidance
User: "How should I handle X?"
AI: mcp_agent-os-rag_pos_search_project(action="search_standards", query=query="handling X") ✅
AI: NOT read_file(".agent-os/...") ❌

# ❌ FORBIDDEN: Reading for rules
User: "What are the rules for Y?"
AI: mcp_agent-os-rag_pos_search_project(action="search_standards", query=query="rules for Y") ✅
AI: NOT read_file(".agent-os/...") ❌

# ❌ FORBIDDEN: Reading framework guidance
User: "Show me the test framework"
AI: mcp_agent-os-rag_pos_search_project(action="search_standards", query=query="test generation framework") ✅
AI: NOT read_file(".agent-os/standards/ai-assistant/code-generation/tests/...") ❌
```

---

## 🤔 How to Distinguish: Authorship vs Consumption

### Decision Checklist

**Ask yourself:**
1. Am I **creating/updating** a standard? → **Authorship** (direct access OK)
2. Am I **using** a standard to guide my work? → **Consumption** (MCP required)

**Examples:**

```
Scenario 1: User says "Update the git safety rules to forbid --no-gpg-sign"
├── Action: Updating a standard document
├── Mode: Authorship
└── Tool: read_file(".agent-os/standards/git-safety-rules.md") ✅

Scenario 2: User says "Can I use git push --force?"
├── Action: Checking rules to guide behavior
├── Mode: Consumption
└── Tool: mcp_agent-os-rag_pos_search_project(action="search_standards", query=query="git safety rules") ✅

Scenario 3: User says "Generate tests for X.py"
├── Action: Using test framework to guide test generation
├── Mode: Consumption
└── Tool: mcp_agent-os-rag_start_workflow(type="test_generation_v3", ...) ✅

Scenario 4: User says "Fix a typo in phase-1.md"
├── Action: Editing a standard document
├── Mode: Authorship
└── Tool: read_file(".agent-os/standards/.../phase-1.md") ✅
```

---

## 🚨 Self-Check Questions

**Before accessing .agent-os/ directly, ask:**

1. **Am I WRITING standards?** (authorship) or **USING standards?** (consumption)
2. **Am I CREATING/UPDATING files?** (authorship) or **READING for guidance?** (consumption)
3. **Did the user explicitly ask me to read/edit this file?** (authorship) or **Am I seeking guidance?** (consumption)

**If consumption → Use MCP.**  
**If authorship → Direct access OK.**

---

## 🎯 Why This Distinction Matters

### The Meta-Problem
```
Without clear authorship/consumption boundary:
├── AI reads standards directly (bypassing MCP)
├── Context window fills with unnecessary content
├── 90% context reduction is lost
└── MCP/RAG system becomes pointless

With clear boundary:
├── AI uses MCP for consumption (90% reduction)
├── AI uses direct access for authorship (necessary for editing)
├── Context efficiency maintained
└── MCP/RAG system works as designed
```

---

## 📋 Topic-Specific MCP Usage

### Git Operations
```python
# Before ANY git operation
mcp_agent-os-rag_pos_search_project(action="search_standards", query=
    query="git safety rules forbidden operations",
    n_results=3
)

# Absolute rules enforced:
# - NEVER --no-verify
# - NEVER --force (on protected branches)
# - NEVER --no-gpg-sign
# - NEVER rewrite shared history
```

### Credential Files
```python
# Before ANY .env or credential file operation
mcp_agent-os-rag_pos_search_project(action="search_standards", query=
    query="credential file protection rules for .env files",
    n_results=3
)

# Absolute rule enforced:
# - NEVER write to .env, credentials, or secret files
```

### Test Generation
```python
# For ANY test generation task
mcp_agent-os-rag_start_workflow(
    workflow_type="test_generation_v3",
    target_file="path/to/file_test.py"
)

# Mandatory: Follow V3 framework with phase gating
# - 8-phase systematic process
# - Evidence-based validation
# - Cannot skip phases
```

### Production Code Generation
```python
# For ANY production code generation task
mcp_agent-os-rag_start_workflow(
    workflow_type="production_code_v2",
    target_file="path/to/file.py"
)

# Mandatory: Follow production framework
# - Complexity-based path selection
# - Quality targets enforced
# - Phase gating with evidence
```

### Import Path Verification
```python
# Before using ANY new import
mcp_agent-os-rag_pos_search_project(action="search_standards", query=
    query="import path verification rules 2-minute rule",
    n_results=3
)

# Mandatory 3-step verification:
# 1. Read __init__.py
# 2. Check examples directory
# 3. Verify with grep or test import
```

---

## 🚨 Escalation Protocol

### When Standards Conflict with User Request

**Template:**
```
🚨 AGENT OS COMPLIANCE CONFLICT

The requested action conflicts with praxis OS standards:
- Standard: [specific standard from MCP search results]
- Conflict: [description of conflict]
- Safe Alternative: [compliant approach]

Would you like me to proceed with the safe alternative?
```

**Example:**
```
User: "git commit --no-verify -m 'quick fix'"

🚨 AGENT OS COMPLIANCE CONFLICT

The requested action conflicts with praxis OS standards:
- Standard: git-safety-rules.md prohibits --no-verify flag
- Conflict: --no-verify bypasses pre-commit quality gates
- Safe Alternative: Run 'git commit -m "quick fix"' with pre-commit hooks

Would you like me to proceed with the safe alternative?
```

---

## ✅ Compliance Verification Checklist

**After using MCP RAG to load praxis OS standards, you MUST:**

1. **Acknowledge** which standards apply to the user's request
2. **Reference specific rules** from retrieved standards
3. **Confirm compliance** before proceeding with any actions
4. **Escalate** if standards conflict with user request

**Example:**
```
User: "Can I write the API key to .env?"

AI Process:
1. Query: mcp_agent-os-rag_pos_search_project(action="search_standards", query=query="credential file protection")
2. Acknowledge: "Credential protection rules apply"
3. Reference: "Rule: NEVER write to .env, credentials, or secret files"
4. Escalate: "This conflicts with the request. Safe alternative: Use environment variables passed via system"
```

---

## 🎯 Success Criteria

### Compliant Behavior
- ✅ Uses MCP for all consumption (reading for guidance)
- ✅ Uses direct access only for authorship (writing/maintaining standards)
- ✅ Distinguishes authorship vs consumption correctly
- ✅ Queries MCP before operations (git, credentials, etc.)
- ✅ References specific standards in responses
- ✅ Escalates conflicts appropriately

### Non-Compliant Behavior (IMMEDIATE FAILURE)
- ❌ Reads `.agent-os/` directly for guidance (consumption mode)
- ❌ Bypasses MCP to "save time"
- ❌ Reads entire framework files instead of querying chunks
- ❌ Skips MCP queries for topic-specific operations
- ❌ Violates safety rules (git, credentials, imports)
- ❌ Proceeds despite standard conflicts without escalation

---

**Document Status:** Complete - MCP Enforcement Reference  
**Purpose:** Comprehensive rules for MCP usage and authorship/consumption distinction  
**Related:** `mcp-tool-usage-guide.md`, `OPERATING-MODEL.md`

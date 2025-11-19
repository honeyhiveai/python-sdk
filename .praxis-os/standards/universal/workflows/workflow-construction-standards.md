# Workflow Construction Standards

**Purpose:** Define standards for creating workflows within the prAxIs OS workflow engine.  
**Audience:** Workflow authors, spec creators  
**Last Updated:** 2025-10-07

---

## 🎯 TL;DR - Workflow Construction Quick Reference

**Keywords for search**: workflow construction, building workflows, workflow structure, phase.md, task files, workflow standards, workflow file sizes, workflow engine, creating workflows, workflow templates

**Core Principle:** Workflows follow meta-workflow principles with specific file naming and size standards: phase.md (~80 lines), task files (100-170 lines), command language, validation gates.

**Directory Structure:**
```
workflows/{workflow_name}/
├── metadata.json           # Workflow definition (required)
├── phases/
│   ├── N/
│   │   ├── phase.md       # Phase overview (~80 lines)
│   │   ├── task-1-name.md # Task files (100-170 lines)
│   │   └── task-2-name.md
└── core/                   # Optional supporting docs
```

**Key Rules:**
1. ✅ **Use `phase.md`** (not README.md)
2. ✅ **Phase files: ~80 lines** (overview only)
3. ✅ **Task files: 100-170 lines** (detailed execution)
4. ✅ **One task = one file** (horizontal decomposition)
5. ✅ **Command language** (🛑, 🎯, 📊)
6. ✅ **Validation gates** after every phase

**Phase File Template:**
```markdown
# Phase N: [Name]
🎯 Phase Objective: [Clear goal]
## Tasks in This Phase
- task-1-name.md
- task-2-name.md
🛑 VALIDATE-GATE: Phase N Checkpoint
- [ ] Criterion ✅/❌
```

**Task File Template:**
```markdown
# Task N: [Name]
🎯 Objective: [What this accomplishes]
## Prerequisites
🛑 EXECUTE-NOW: [Required actions]
## Steps
### Step 1: [Action]
[Detailed instructions]
## Completion Criteria
- [ ] Criterion ✅/❌
🎯 NEXT-MANDATORY: [Next task]
```

**File Size Guidelines:**
- **Phase files:** 60-100 lines (target: 80)
- **Task files:** 100-170 lines (target: 120)
- **Supporting docs:** 200-500 lines

**Command Language:**
- `🛑 EXECUTE-NOW` - Blocking action
- `🎯 NEXT-MANDATORY` - Explicit routing
- `📊 COUNT-AND-DOCUMENT` - Evidence gathering
- `🛑 VALIDATE-GATE` - Quality checkpoint

**Common Mistakes:**
- Using README.md instead of phase.md
- Monolithic task files (>200 lines)
- Missing validation gates
- Vague completion criteria

---

## ❓ Questions This Answers

1. "How do I create a workflow?"
2. "What is the workflow directory structure?"
3. "Should I use README.md or phase.md?"
4. "What size should task files be?"
5. "How do I structure phase files?"
6. "How do I structure task files?"
7. "What command language should I use?"
8. "How do I add validation gates?"
9. "What are workflow construction standards?"
10. "How do workflows relate to meta-workflow?"
11. "What file naming conventions exist?"

---

## 🎯 Overview

This document defines the **structural standards** for building workflows in the prAxIs OS workflow engine. It applies meta-workflow principles specifically to workflow construction.

**Related Standards:**
- [Meta-Framework Principles](../meta-workflow/framework-creation-principles.md) - Foundation principles
- [Three-Tier Architecture](../meta-workflow/three-tier-architecture.md) - Content organization
- [Horizontal Decomposition](../meta-workflow/horizontal-decomposition.md) - File size guidelines
- [Workflow Metadata Standards](workflow-metadata-standards.md) - metadata.json structure

---

## What Is the Standard Workflow Structure?

Every workflow MUST follow this directory structure to ensure compatibility with the workflow engine:

```
workflows/{workflow_name}/
├── metadata.json           # Workflow definition (required)
├── phases/
│   ├── N/
│   │   ├── phase.md                    # Phase overview (~80 lines)
│   │   ├── task-1-name.md              # Task files (100-170 lines each)
│   │   ├── task-2-name.md
│   │   └── task-N-name.md
│   └── dynamic/                        # For dynamic workflows only
│       ├── phase-template.md
│       └── task-template.md
└── core/                               # Optional supporting docs
    ├── glossary.md
    └── helpers.md
```

**Key Rules:**
1. ✅ Phase overview files MUST be named `phase.md` (not README.md)
2. ✅ Task files MUST be named `task-N-descriptive-name.md`
3. ✅ File sizes MUST follow meta-workflow guidelines (see below)

---

## How to Structure Phase Files?

Phase files are navigation hubs that provide overview and route to tasks. They must be concise and focused.

**Filename:** `phase.md`  
**Size:** ~80 lines  
**Purpose:** Phase overview with task links

### Required Sections

```markdown
# Phase N: [Name]

**Phase Number:** N  
**Purpose:** [Brief description]  
**Estimated Time:** [Duration]  
**Total Tasks:** [N]

---

## 🎯 Phase Objective
[1-2 paragraphs explaining what user accomplishes]

---

## Tasks in This Phase

### Task 1: [Name]
**File:** [task-1-name.md](task-1-name.md)  
**Purpose:** [Brief description]  
**Time:** [Duration]

[Repeat for each task]

---

## Execution Approach
🛑 EXECUTE-NOW: Complete tasks sequentially
[Explanation of task order/dependencies]

---

## Phase Deliverables
- ✅ [Deliverable 1]
- ✅ [Deliverable 2]

---

## Validation Gate
🛑 VALIDATE-GATE: Phase N Checkpoint
- [ ] [Phase-level criterion] ✅/❌

---

## Start Phase N
🎯 NEXT-MANDATORY: [task-1-name.md](task-1-name.md)
```

**Rationale:** Phase files are **navigation hubs**, not execution details. Keep them concise.

---

## How to Structure Task Files?

Task files contain detailed execution instructions for a single, focused task. They are the core execution units.

**Filename:** `task-N-descriptive-name.md`  
**Size:** 100-170 lines  
**Purpose:** Detailed execution instructions for single task

### Required Sections

```markdown
# Task N: [Name]

**Phase:** N ([Phase Name])  
**Purpose:** [What this accomplishes]  
**Estimated Time:** [Duration]

---

## 🎯 Objective
[1-2 paragraphs explaining what user creates/does]

---

## Prerequisites
🛑 EXECUTE-NOW: Verify dependencies
[Prerequisites, dependencies, required reading]

---

## Steps

### Step 1: [Action]
[Detailed instructions with commands, examples]

### Step 2: [Action]
[More instructions]

[Continue with steps]

---

## Completion Criteria
🛑 VALIDATE-GATE: Task Completion
- [ ] [Criterion 1] ✅/❌
- [ ] [Criterion 2] ✅/❌

🚨 FRAMEWORK-VIOLATION: [Warning]

---

## Evidence Collection
📊 COUNT-AND-DOCUMENT: Task Results
[What to measure and document]

---

## Next Task
🎯 NEXT-MANDATORY: [task-N+1-name.md](task-N+1-name.md)
```

**Rationale:** Task files contain all execution details. Phase files just link to them.

---

## What Are the File Size Guidelines?

File size directly impacts AI attention quality. Follow these empirically validated targets:

Based on meta-workflow horizontal decomposition principles:

| File Type | Size | Purpose |
|-----------|------|---------|
| `phase.md` | ~80 lines | Overview + navigation |
| `task-N-name.md` | 100-170 lines | Single-task execution |
| `metadata.json` | Varies | Workflow definition |
| Core docs | 200-500 lines | Methodology (Tier 2) |

**Why These Sizes:**
- **Phase files (~80 lines):** Provides overview without overwhelming
- **Task files (100-170 lines):** Enough detail for complete execution without context overflow
- **Validated by:** `spec_execution_v1` workflow (working implementation)

**🚨 Anti-Pattern:** 
- ❌ Inline tasks in phase files (creates 500+ line files)
- ❌ Phase files > 100 lines (defeats navigation purpose)
- ❌ Task files > 200 lines (splits AI attention)

---

## What Command Language Should I Use in Workflows?

Command language creates binding instructions that AI agents cannot ignore. Use these standardized symbols:

All workflow files MUST use command language for enforceability:

**Blocking Commands (MUST execute):**
- `🛑 EXECUTE-NOW:` - Mandatory action
- `🛑 VALIDATE-GATE:` - Checkpoint criteria

**Mandatory Reading:**
- `⚠️ MUST-READ:` - Required documentation

**Evidence Collection:**
- `📊 COUNT-AND-DOCUMENT:` - Metrics to record

**Navigation:**
- `🎯 NEXT-MANDATORY:` - Next file/task

**Violations:**
- `🚨 FRAMEWORK-VIOLATION:` - What NOT to do

See: [Command Language Standard](../meta-workflow/command-language.md)

---

## How to Validate Workflow Quality?

Use this checklist to ensure your workflow meets prAxIs OS standards before deployment:

Before considering a workflow complete:

**Structure:**
- [ ] All phase directories have `phase.md` (not README.md) ✅/❌
- [ ] Task files named `task-N-descriptive-name.md` ✅/❌
- [ ] `metadata.json` exists and validates ✅/❌

**File Sizes:**
- [ ] Phase files ~80 lines (70-90 acceptable) ✅/❌
- [ ] Task files 100-170 lines ✅/❌
- [ ] No execution files > 200 lines ✅/❌

**Content:**
- [ ] Command language used throughout ✅/❌
- [ ] All tasks have validation gates ✅/❌
- [ ] All tasks have evidence collection ✅/❌
- [ ] Task navigation links complete ✅/❌

**Testing:**
- [ ] Workflow tested end-to-end ✅/❌
- [ ] All tasks executable as written ✅/❌
- [ ] Validation gates enforceable ✅/❌

---

## What Working Examples Exist?

These production workflows demonstrate the standards in action:

**Compliant Workflows:**
- `spec_execution_v1` - Hybrid static/dynamic workflow
- `test-generation` - Code generation workflow (needs README→phase.md rename)

**Study These:**
1. `.praxis-os/workflows/spec_execution_v1/phases/0/phase.md` (76 lines)
2. `.praxis-os/workflows/spec_execution_v1/phases/0/task-1-locate-spec.md` (124 lines)

---

## What Common Mistakes Should I Avoid?

These anti-patterns frequently occur in workflow construction. Recognize and eliminate them:

### Mistake 1: Using README.md Instead of phase.md
**Problem:** Inconsistent naming, unclear purpose  
**Fix:** Always use `phase.md` for phase overview files

### Mistake 2: Inline Tasks in Phase Files
**Problem:** Creates 500+ line phase files  
**Fix:** Separate each task into its own `task-N-name.md` file

### Mistake 3: Incorrect File Sizes
**Problem:** Phase files too long, task files too short  
**Fix:** Follow ~80 line phase, 100-170 line task guideline

### Mistake 4: Missing Command Language
**Problem:** Instructions not binding, often skipped  
**Fix:** Use 🛑 EXECUTE-NOW, 🛑 VALIDATE-GATE throughout

---

## How Do Workflows Relate to Meta-Framework?

Workflow construction standards are the specific application of meta-workflow principles:

**Workflow Construction Standards** are a specific application of **Meta-Framework Principles**:

| Meta-Framework Principle | Workflow Application |
|--------------------------|----------------------|
| Three-Tier Architecture | Phase (Tier 1), Core (Tier 2), Outputs (Tier 3) |
| Horizontal Decomposition | Phase files ~80 lines, task files 100-170 lines |
| Command Language | All commands used in phase/task files |
| Validation Gates | Task-level + Phase-level gates |
| Single Responsibility | One task per file |

**Meta-framework** = Universal AI framework principles  
**Workflow Construction Standards** = Specific application for workflow engine

---

## How to Create a New Workflow?

Follow this systematic process to create a workflow from scratch or from specification:

**Step-by-step process:**

1. **Define structure** in `metadata.json`
2. **Create directories** for each phase
3. **Write phase.md** for each phase (~80 lines)
4. **Write task files** for all tasks (100-170 lines each)
5. **Validate** against checklist above
6. **Test end-to-end** with workflow engine
7. **Iterate** based on dogfooding

**Tools:**
- Use `spec_creation_v1` workflow to create spec
- Use `spec_execution_v1` workflow to implement from spec
- Query MCP standards throughout

---

## 🎯 Key Takeaways

1. ✅ **Always use `phase.md`** (not README.md)
2. ✅ **Keep phase files ~80 lines** (overview only)
3. ✅ **Task files 100-170 lines** (detailed execution)
4. ✅ **One task = one file** (horizontal decomposition)
5. ✅ **Command language** enforces compliance
6. ✅ **Based on actual working workflows** (not theoretical)

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Creating workflow** | `pos_search_project(content_type="standards", query="workflow construction")` |
| **Workflow structure** | `pos_search_project(content_type="standards", query="workflow structure")` |
| **Phase files** | `pos_search_project(content_type="standards", query="phase.md")` |
| **Task files** | `pos_search_project(content_type="standards", query="task file structure")` |
| **File sizes** | `pos_search_project(content_type="standards", query="workflow file sizes")` |
| **Validation gates** | `pos_search_project(content_type="standards", query="workflow validation gates")` |
| **Command language** | `pos_search_project(content_type="standards", query="workflow commands")` |
| **Building workflows** | `pos_search_project(content_type="standards", query="building workflows")` |

---

## 🔗 Related Standards

**Query workflow for complete workflow creation:**

1. **Start with construction** → `pos_search_project(content_type="standards", query="workflow construction")` (this document)
2. **Add metadata** → `pos_search_project(content_type="standards", query="workflow metadata")` → `standards/workflows/workflow-metadata-standards.md`
3. **Understand system** → `pos_search_project(content_type="standards", query="workflow system overview")` → `standards/workflows/workflow-system-overview.md`
4. **Learn principles** → `pos_search_project(content_type="standards", query="framework creation principles")` → `standards/meta-workflow/framework-creation-principles.md`
5. **Apply architecture** → `pos_search_project(content_type="standards", query="three-tier architecture")` → `standards/meta-workflow/three-tier-architecture.md`

**By Category:**

**Workflows:**
- `standards/workflows/workflow-metadata-standards.md` - metadata.json structure → `pos_search_project(content_type="standards", query="workflow metadata")`
- `standards/workflows/workflow-system-overview.md` - Workflow engine → `pos_search_project(content_type="standards", query="workflow system overview")`
- `standards/workflows/mcp-rag-configuration.md` - RAG configuration → `pos_search_project(content_type="standards", query="MCP RAG configuration")`

**Meta-Framework (Foundation):**
- `standards/meta-workflow/framework-creation-principles.md` - Core principles → `pos_search_project(content_type="standards", query="framework creation principles")`
- `standards/meta-workflow/three-tier-architecture.md` - Content organization → `pos_search_project(content_type="standards", query="three-tier architecture")`
- `standards/meta-workflow/horizontal-decomposition.md` - File size guidelines → `pos_search_project(content_type="standards", query="horizontal decomposition")`
- `standards/meta-workflow/command-language.md` - Command symbols → `pos_search_project(content_type="standards", query="command language")`
- `standards/meta-workflow/validation-gates.md` - Quality checkpoints → `pos_search_project(content_type="standards", query="validation gates")`

**Usage:**
- `usage/creating-specs.md` - Specification structure → `pos_search_project(content_type="standards", query="how to create specs")`

---

**These standards emerged from dogfooding the workflow engine. They represent validated, working patterns.**

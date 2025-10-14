# Workflow Construction Standards

**Purpose:** Define standards for creating workflows within the Agent OS workflow engine.  
**Audience:** Workflow authors, spec creators  
**Last Updated:** 2025-10-07

---

## 🎯 Overview

This document defines the **structural standards** for building workflows in the Agent OS workflow engine. It applies meta-framework principles specifically to workflow construction.

**Related Standards:**
- [Meta-Framework Principles](../meta-framework/framework-creation-principles.md) - Foundation principles
- [Three-Tier Architecture](../meta-framework/three-tier-architecture.md) - Content organization
- [Horizontal Decomposition](../meta-framework/horizontal-decomposition.md) - File size guidelines
- [Workflow Metadata Standards](workflow-metadata-standards.md) - metadata.json structure

---

## 📁 Standard Workflow Structure

Every workflow MUST follow this directory structure:

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
3. ✅ File sizes MUST follow meta-framework guidelines (see below)

---

## 📄 Phase File Standard

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

## 📄 Task File Standard

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

## 📏 File Size Guidelines

Based on meta-framework horizontal decomposition principles:

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

## 🔧 Command Language

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

See: [Command Language Standard](../meta-framework/command-language.md)

---

## ✅ Validation Checklist

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

## 📚 Examples

**Compliant Workflows:**
- `spec_execution_v1` - Hybrid static/dynamic workflow
- `test-generation` - Code generation workflow (needs README→phase.md rename)

**Study These:**
1. `.agent-os/workflows/spec_execution_v1/phases/0/phase.md` (76 lines)
2. `.agent-os/workflows/spec_execution_v1/phases/0/task-1-locate-spec.md` (124 lines)

---

## 🚨 Common Mistakes

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

## 🔄 Relationship to Meta-Framework

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

## 📝 Creating a New Workflow

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

**These standards emerged from dogfooding the workflow engine. They represent validated, working patterns.**

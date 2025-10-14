# Phase 0: Setup & Path Selection

**Phase Number:** 0  
**Purpose:** Environment validation, target analysis, and CRITICAL path selection (unit OR integration)  
**Estimated Time:** 10-15 minutes  
**Total Tasks:** 4

---

## 🎯 Phase Objective

Establish solid foundation and lock path strategy that determines entire workflow execution. This phase prevents path mixing and ensures all prerequisites are met before deep analysis begins.

---

## 🚨 Critical Importance

**Path selection here is LOCKED for entire workflow**
- Unit path → Mock external dependencies
- Integration path → Real API usage

Cannot change mid-workflow. This decision affects all subsequent phases.

---

## Tasks in This Phase

### Task 1: Environment Validation
**File:** [task-1-environment-validation.md](task-1-environment-validation.md)  
**Purpose:** Verify workspace, git, Python, and all required tools  
**Time:** 3 minutes

### Task 2: Target File Analysis
**File:** [task-2-target-analysis.md](task-2-target-analysis.md)  
**Purpose:** Analyze production file complexity and scope  
**Time:** 3 minutes

### Task 3: Path Selection (CRITICAL)
**File:** [task-3-path-selection.md](task-3-path-selection.md)  
**Purpose:** Choose unit OR integration path - locks strategy  
**Time:** 2 minutes

### Task 4: Baseline Metrics
**File:** [task-4-baseline-metrics.md](task-4-baseline-metrics.md)  
**Purpose:** Collect pre-generation metrics if test exists  
**Time:** 2 minutes

---

## Execution Approach

🛑 EXECUTE-NOW: Complete tasks sequentially

Tasks must be completed in order:
1 → 2 → 3 → 4

Task 3 (Path Selection) is critical - cannot proceed without locked path.

---

## Phase Deliverables

Upon completion, you will have:
- ✅ Environment verified (Python, tools, workspace)
- ✅ Target file analyzed (complexity, functions, classes)
- ✅ Path selected and locked (unit OR integration)
- ✅ Baseline metrics collected
- ✅ Progress table initialized

---

## Validation Gate

🛑 VALIDATE-GATE: Phase 0 Checkpoint

Before advancing to Phase 1:
- [ ] Environment verified and working ✅/❌
- [ ] Target file validated and analyzed ✅/❌
- [ ] Path selected (unit OR integration) and documented ✅/❌
- [ ] Baseline metrics collected ✅/❌
- [ ] Progress table initialized in chat ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without path selection

---

## Start Phase 0

🎯 NEXT-MANDATORY: [task-1-environment-validation.md](task-1-environment-validation.md)

Begin with Task 1 to validate your environment.




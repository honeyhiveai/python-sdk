# Phase 0: Supporting Documents Integration

**Phase Number:** 0  
**Purpose:** Incorporate pre-existing documents into spec structure  
**Estimated Time:** 10-20 minutes  
**Total Tasks:** 4

**Note:** This phase is OPTIONAL and only runs if `supporting_docs` provided in workflow options.

---

## 🎯 Phase Objective

Process existing analysis, research, or design documents to extract insights that will inform requirements, design, and implementation phases. This phase bridges the gap between existing documentation and structured specification creation.

**Spec Lifecycle:** New specs are created in `specs/review/` (awaiting approval status) and later moved to `approved/` or `completed/` as they progress through the lifecycle.

---

## Tasks in This Phase

### Task 0: Create Spec Directory
**File:** [task-0-create-directory.md](task-0-create-directory.md)  
**Purpose:** Create properly-named spec directory in `specs/review/` location  
**Time:** 1 minute

### Task 1: Copy or Reference Documents
**File:** [task-1-copy-documents.md](task-1-copy-documents.md)  
**Purpose:** Make documents accessible in spec directory  
**Time:** 5 minutes

### Task 2: Create Document Index
**File:** [task-2-create-index.md](task-2-create-index.md)  
**Purpose:** Catalog all documents with structured metadata  
**Time:** 5 minutes

### Task 3: Extract Key Insights
**File:** [task-3-extract-insights.md](task-3-extract-insights.md)  
**Purpose:** Extract and categorize insights for later phases  
**Time:** 10 minutes

---

## Execution Approach

🛑 EXECUTE-NOW: Complete tasks sequentially

Tasks must be completed in order: 0 → 1 → 2 → 3

Each task builds on the previous one's output.

---

## Phase Deliverables

Upon completion, you will have:
- ✅ Spec directory created in `specs/review/` with correct naming convention
- ✅ All supporting docs accessible (copied or referenced)
- ✅ INDEX.md with document catalog and metadata
- ✅ Extracted insights categorized by type (requirements/design/implementation)

---

## Validation Gate

🛑 VALIDATE-GATE: Phase 0 Checkpoint

Before advancing to Phase 1:
- [ ] Spec directory created in `specs/review/` location ✅/❌
- [ ] Directory follows `YYYY-MM-DD-descriptive-name` format ✅/❌
- [ ] `supporting-docs/` directory exists ✅/❌
- [ ] All documents processed (embedded or referenced) ✅/❌
- [ ] `INDEX.md` created with all documents listed ✅/❌
- [ ] Each document has extracted insights ✅/❌
- [ ] Mode documented (embed vs reference) ✅/❌
- [ ] Cross-reference summary complete ✅/❌

🚨 FRAMEWORK-VIOLATION: Skipping insight extraction

Extracting insights from supporting documents is MANDATORY. These insights inform requirements, design, and implementation. Skipping this step will result in incomplete specs.

---

## Start Phase 0

🎯 NEXT-MANDATORY: [task-0-create-directory.md](task-0-create-directory.md)

Begin with Task 0 to create the properly-named spec directory.
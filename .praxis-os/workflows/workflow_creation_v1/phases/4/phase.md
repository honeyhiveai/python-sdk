# Phase 4: Phase Content Generation

**Purpose**: Generate all phase.md and task files for target workflow  
**Deliverable**: Complete target workflow with all phase and task files populated

---

## Overview

This phase generates ALL content files for the target workflow by iterating through the workflow definition. We systematically:

1. **Load** the target workflow definition from Phase 1
2. **Loop** through all target phases and generate phase.md files
3. **Loop** through all tasks and generate task-N-name.md files
4. **Verify** all files created successfully

**This is a loop-based generation phase - all files created in one pass.**

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

---

## Tasks

| # | Task | File | Status |
|---|------|------|--------|
| 1 | Load Target Definition | task-1-load-target-definition.md | ⬜ |
| 2 | Generate Phase Files | task-2-generate-phase-files.md | ⬜ |
| 3 | Generate Task Files | task-3-generate-task-files.md | ⬜ |
| 4 | Verify Generation | task-4-verify-generation.md | ⬜ |

---

## Validation Gate

🚨 **CRITICAL**: Phase 3 MUST complete successfully before proceeding to Phase 4.

**Evidence Required**:

| Evidence | Type | Validator | Description |
|----------|------|-----------|-------------|
| `phase_files_created` | integer | greater_than_0 | Number of phase.md files created |
| `task_files_created` | integer | greater_than_0 | Number of task files created |
| `total_files_expected` | integer | greater_than_0 | Total files expected from definition |
| `all_phases_populated` | boolean | is_true | All target phases have complete files |

**Human Approval**: Not required

---

## Navigation

**Start Here**: 🎯 NEXT-MANDATORY: task-1-load-target-definition.md

**After Phase 4 Complete**: 🎯 NEXT-MANDATORY: ../5/phase.md


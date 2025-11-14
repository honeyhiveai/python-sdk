# Phase 2: Workflow Scaffolding

**Purpose**: Create directory structure and metadata.json  
**Deliverable**: Complete workflow directory with all phase folders

---

## Overview

This phase creates the foundational directory structure for the target workflow. We systematically:

1. **Create** the root workflow directory
2. **Create** all phase directories (0, 1, 2, ...)
3. **Create** core/ for supporting files
4. **Create** supporting-docs/ for design archive
5. **Create** dynamic/ if workflow is dynamic
6. **Generate** metadata.json with complete structure
7. **Verify** all directories created correctly

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

---

## Tasks

| # | Task | File | Status |
|---|------|------|--------|
| 1 | Create Workflow Directory | task-1-create-workflow-directory.md | ⬜ |
| 2 | Create Phase Directories | task-2-create-phase-directories.md | ⬜ |
| 3 | Create Core Directory | task-3-create-core-directory.md | ⬜ |
| 4 | Create Supporting Docs | task-4-create-supporting-docs.md | ⬜ |
| 5 | Create Dynamic Directories | task-5-create-dynamic-directories.md | ⬜ |
| 6 | Generate Metadata JSON | task-6-generate-metadata-json.md | ⬜ |
| 7 | Validate Metadata | task-7-validate-metadata.md | ⬜ |
| 8 | Verify Scaffolding | task-8-verify-scaffolding.md | ⬜ |
| 9 | Generate Gate Definitions | task-9-generate-gate-definitions.md | ⬜ |
| 10 | Validate Gate Consistency | task-10-validate-gate-consistency.md | ⬜ |

---

## Validation Gate

🚨 **CRITICAL**: Phase 1 MUST complete successfully before proceeding to Phase 2.

**Evidence Required**:

| Evidence | Type | Validator | Description |
|----------|------|-----------|-------------|
| `workflow_directory_path` | string | directory_exists | Path to created workflow directory |
| `phase_directories_count` | integer | greater_than_0 | Number of phase directories created |
| `metadata_json_created` | boolean | is_true | metadata.json file created and valid |
| `scaffolding_verified` | boolean | is_true | All directory structure verified |

**Human Approval**: Not required

---

## Navigation

**Start Here**: 🎯 NEXT-MANDATORY: task-1-create-workflow-directory.md

**After Phase 2 Complete**: 🎯 NEXT-MANDATORY: ../3/phase.md

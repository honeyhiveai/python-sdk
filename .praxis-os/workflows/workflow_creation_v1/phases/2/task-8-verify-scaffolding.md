# Task 8: Verify Scaffolding

**Phase**: 2 - Workflow Scaffolding  
**Purpose**: Confirm all directories created correctly  
**Depends On**: All previous Phase 1 tasks (especially Task 7 - Validate Metadata)  
**Feeds Into**: Phase 2 (Core Files & Documentation)

---

## Objective

Systematically verify that all directories and the metadata.json file were created correctly and completely.

---

## Context

📊 **CONTEXT**: This is the final checkpoint before moving to content creation. We must confirm the scaffolding is complete and correct, as all subsequent phases depend on this structure.

---

## Instructions

### Step 1: Verify Root Directory

Confirm the workflow root directory exists and is accessible:

```
.praxis-os/workflows/{target_workflow_type}/
```

📖 **DISCOVER-TOOL**: List directory contents

Expected contents:
- `metadata.json` (file)
- `core/` (directory)
- `supporting-docs/` (directory)
- `phases/` (directory)

⚠️ **CONSTRAINT**: All four items MUST be present.

### Step 2: Verify phases/ Structure

List the contents of `phases/` directory:

📖 **DISCOVER-TOOL**: List directory contents

Expected:
- Numbered directories (0/, 1/, 2/, ...)
- `dynamic/` directory (if workflow is dynamic)

Count the directories and confirm:
- Count matches `total_target_phases` from Phase 0
- Phase numbers are sequential
- No gaps in numbering

### Step 3: Verify Each Phase Directory

For each phase directory, confirm it exists and is currently empty (will be populated later):

```
phases/0/
phases/1/
phases/2/
...
```

### Step 4: Verify core/ and supporting-docs/

Confirm both directories exist and are empty:

```
core/
supporting-docs/
```

### Step 5: Verify metadata.json

Confirm the metadata.json file:
- Exists
- Is readable
- Contains valid JSON
- Has all required fields
- References all phases
- References all tasks

Read and parse the file to validate structure.

### Step 6: Generate Verification Report

Create summary with status for:
- Root directory and 4 expected subdirectories (✅ each)
- Phase directories count and list (✅ each)
- Dynamic directory if applicable
- Metadata JSON validation (Valid JSON, all fields/phases/tasks)
- Overall status: READY FOR PHASE 2

### Step 7: Handle Verification Failures

If ANY verification fails:
- 🚨 **CRITICAL**: STOP execution
- Document the specific failure
- Provide corrective action required
- Do not proceed to Phase 2

---

## Expected Output

**Evidence for Validation Gate**:
- `workflow_directory_path`: String (path to workflow root)
- `phase_directories_count`: Integer (number of phase directories)
- `metadata_json_created`: Boolean (true)
- `scaffolding_verified`: Boolean (true if all checks pass)

**Verification Report**:
- `verification_report`: String (formatted report text)

---

## Quality Checks

✅ Root directory verified  
✅ All expected subdirectories present  
✅ Phase directories counted and verified  
✅ metadata.json validated  
✅ Verification report generated  
✅ Ready for Phase 2

---

## Checkpoint Evidence

Submit the following evidence to complete Phase 1:

```yaml
evidence:
  workflow_directory_path: ".praxis-os/workflows/{workflow_type}/"
  phase_directories_count: {N}
  metadata_json_created: true
  scaffolding_verified: true
```

---

## Navigation

🎯 **NEXT-MANDATORY**: ../3/phase.md (begin Phase 3 after checkpoint passes)

↩️ **RETURN-TO**: phase.md (after task complete, before phase submission)


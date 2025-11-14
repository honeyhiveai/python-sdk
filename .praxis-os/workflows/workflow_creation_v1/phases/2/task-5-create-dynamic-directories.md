# Task 5: Create Dynamic Directories

**Phase**: 2 - Workflow Scaffolding  
**Purpose**: If dynamic, create phases/dynamic/  
**Depends On**: Task 2 (phases created), Phase 0 (is_dynamic flag)  
**Feeds Into**: Task 6 (Generate Metadata JSON)

---

## Objective

If the target workflow is dynamic, create the `phases/dynamic/` directory that will house the phase and task templates used for iteration.

---

## Context

📊 **CONTEXT**: Dynamic workflows use template files to generate multiple similar phases. The templates live in `phases/dynamic/` and are processed by the workflow engine during execution. Static workflows do not need this directory.

🔍 **MUST-SEARCH**: "dynamic workflows template iteration"

---

## Instructions

### Step 1: Check if Workflow is Dynamic

Retrieve the `is_dynamic` flag from Phase 0 Task 5 preparation.

If `is_dynamic == false`:
- Skip directory creation
- Document that target workflow is static
- Proceed to Task 6

If `is_dynamic == true`:
- Continue with Steps 2-5

⚠️ **CONSTRAINT**: Only create dynamic/ directory if workflow is actually dynamic.

### Step 2: Create phases/dynamic/ Directory

Create the directory at:

```
{workflow_directory_path}/phases/dynamic/
```

📖 **DISCOVER-TOOL**: Create a directory

### Step 3: Verify Creation

Confirm the directory was created successfully.

📖 **DISCOVER-TOOL**: List directory contents to verify

Expected: `phases/dynamic/` exists and is empty.

### Step 4: Document Dynamic Configuration

From Phase 0 `dynamic_config`, note:
- Template file names needed (phase-template.md, task-template.md)
- Iteration count
- Source type

This information will be used later when creating the template files.

### Step 5: Store Path

Store the dynamic directory path for use in template creation phases.

---

## Expected Output

**Variables to Capture**:
- `dynamic_directory_created`: Boolean (true if created, false if skipped)
- `dynamic_directory_path`: String (path if created, null if skipped)
- `target_workflow_is_dynamic`: Boolean (from Phase 0)

---

## Quality Checks

✅ Dynamic flag checked  
✅ Directory created only if needed  
✅ Creation verified (if created)  
✅ Dynamic configuration documented  
✅ Path stored for later use

---

## Navigation

🎯 **NEXT-MANDATORY**: task-6-generate-metadata-json.md

↩️ **RETURN-TO**: phase.md (after task complete)


# Task 3: Archive Definition

**Phase**: 3 - Core Files & Documentation  
**Purpose**: Copy definition YAML to supporting-docs/workflow-definition.yaml  
**Depends On**: Phase 1 (supporting-docs/ created), Phase 0 (definition_path)  
**Feeds Into**: Task 4 (Generate Design Summary)

---

## Objective

Archive the original workflow definition YAML file in the workflow's supporting-docs directory for future reference.

---

## Context

📊 **CONTEXT**: Preserving the original definition YAML alongside the generated workflow ensures that future maintainers can understand the workflow's design intent, regenerate it if needed, or create variations based on the same definition structure.

---

## Instructions

### Step 1: Retrieve Definition Path

Get the `definition_path` from Phase 0 Task 1, which points to the original workflow definition YAML file.

### Step 2: Read Definition File

Read the complete contents of the original definition file.

📖 **DISCOVER-TOOL**: Read file contents

### Step 3: Determine Archive Path

The archived file should be saved as:

```
{workflow_directory_path}/supporting-docs/workflow-definition.yaml
```

### Step 4: Write Archived Copy

Write the definition contents to the archive location:

📖 **DISCOVER-TOOL**: Write content to a file

⚠️ **CONSTRAINT**: The archived file MUST be an exact copy of the original. Do not modify, reformat, or validate the content during archiving.

### Step 5: Verify Archive Created

Confirm the archived file:
- Exists at the correct path
- Contains the same content as the original
- Is valid YAML

📖 **DISCOVER-TOOL**: Read file to verify contents

Compare file sizes or checksums if available to ensure exact duplication.

### Step 6: Document Archive Location

Record the archive path for reference in the design summary (Task 4).

---

## Expected Output

**Variables to Capture**:
- `definition_archived`: Boolean (true if successful)
- `archived_definition_path`: String (path to archived file)
- `archive_verified`: Boolean (true if verified identical)

---

## Quality Checks

✅ Definition path retrieved  
✅ Original file read successfully  
✅ Archive path determined  
✅ File written to archive location  
✅ Archive verified identical to original  
✅ Path documented for reference

---

## Navigation

🎯 **NEXT-MANDATORY**: task-4-generate-design-summary.md

↩️ **RETURN-TO**: phase.md (after task complete)


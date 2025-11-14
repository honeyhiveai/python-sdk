# Task 3: Create Core Directory

**Phase**: 2 - Workflow Scaffolding  
**Purpose**: Create core/ for supporting files  
**Depends On**: Task 1 (workflow_directory_path)  
**Feeds Into**: Task 4 (Create Supporting Docs)

---

## Objective

Create the `core/` directory that will house workflow supporting files like command glossaries and progress tracking.

---

## Context

📊 **CONTEXT**: The `core/` directory contains files that support workflow execution but aren't part of the phase progression. These typically include command language glossaries, progress tracking templates, and other operational documents.

---

## Instructions

### Step 1: Create core/ Directory

Create the directory at:

```
{workflow_directory_path}/core/
```

📖 **DISCOVER-TOOL**: Create a directory

### Step 2: Verify Creation

Confirm the directory was created successfully.

📖 **DISCOVER-TOOL**: List directory contents

Expected: `core/` exists and is empty.

### Step 3: Document Path

Store the core directory path for use in Phase 2 when we populate it with files.

---

## Expected Output

**Variables to Capture**:
- `core_directory_path`: String (path to core/ directory)
- `core_directory_created`: Boolean (true if successful)

---

## Quality Checks

✅ core/ directory created  
✅ Creation verified  
✅ Path stored for Phase 2

---

## Navigation

🎯 **NEXT-MANDATORY**: task-4-create-supporting-docs.md

↩️ **RETURN-TO**: phase.md (after task complete)


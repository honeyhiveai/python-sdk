# Task 2: Create Phase Directories

**Phase**: 2 - Workflow Scaffolding  
**Purpose**: Create phases/0/, phases/1/, etc.  
**Depends On**: Task 1 (workflow_directory_path)  
**Feeds Into**: Task 3 (Create Core Directory)

---

## Objective

Create a `phases/` directory and individual subdirectories for each phase defined in the target workflow.

---

## Context

📊 **CONTEXT**: Each workflow phase gets its own numbered directory under `phases/`. The directory numbers correspond to the `number` field in each phase definition. Static phases use integers (0, 1, 2), while placeholder phases (N+3, N+4) will be resolved to actual numbers during creation.

---

## Instructions

### Step 1: Create phases/ Parent Directory

First, create the main `phases/` directory:

```
{workflow_directory_path}/phases/
```

📖 **DISCOVER-TOOL**: Create a directory

### Step 2: Determine Phase Numbers

Using the `phases_to_create` array from Phase 0 Task 5, extract all phase numbers.

For each phase:
- If `number` is an integer (0, 1, 2), use it directly
- If `number` is a placeholder (N+3, N+4), calculate the actual number:
  - N = `total_target_phases` from definition
  - N+3 becomes actual number
  - N+4 becomes actual number

Example: If workflow has 5 phases in definition:
- Phase 0, 1, 2 → static phases
- Phase N+3 → becomes Phase 8 (5 base + 3 dynamic)
- Phase N+4 → becomes Phase 9

⚠️ **CONSTRAINT**: Phase numbers must be sequential without gaps.

### Step 3: Create Each Phase Directory

For each phase number, create a directory:

```
{workflow_directory_path}/phases/{phase_number}/
```

Create them in order: 0, 1, 2, 3, ...

📖 **DISCOVER-TOOL**: Create directories (may support creating multiple or need individual commands)

### Step 4: Verify All Directories Created

List the contents of `{workflow_directory_path}/phases/` and confirm:
- All expected phase directories exist
- Directory count matches expected count
- No unexpected directories present

📖 **DISCOVER-TOOL**: List directory contents

---

## Expected Output

**Variables to Capture**:
- `phase_directories_count`: Integer (number of phase directories created)
- `phase_directories_list`: Array of strings (list of directory names)
- `phases_path`: String (path to phases/ parent directory)

---

## Quality Checks

✅ phases/ parent directory created  
✅ All phase directories created  
✅ Phase numbering is sequential  
✅ Directory count matches expected  
✅ All creations verified

---

## Navigation

🎯 **NEXT-MANDATORY**: task-3-create-core-directory.md

↩️ **RETURN-TO**: phase.md (after task complete)


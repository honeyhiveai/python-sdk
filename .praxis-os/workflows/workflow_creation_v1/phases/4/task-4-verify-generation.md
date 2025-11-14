# Task 4: Verify Generation

**Phase**: 4 - Phase Content Generation  
**Purpose**: Verify all phase and task files created successfully  
**Depends On**: Tasks 2-3 (all files generated)  
**Feeds Into**: Phase 4 completion / Phase 5

---

## Objective

Verify that all expected phase and task files were created correctly and prepare evidence for the Phase 4 validation gate.

---

## Context

📊 **CONTEXT**: File generation is complete. We need to verify that every phase has a phase.md file and every task has its corresponding task file. This ensures the target workflow is complete before moving to compliance validation.

---

## Instructions

### Step 1: Count Generated Files

**Phase Files:**

📖 **DISCOVER-TOOL**: List directory contents

```bash
# Count phase.md files
ls {workflow_root_path}/phases/*/phase.md | wc -l
```

Expected: `total_target_phases` (from Task 1)

**Task Files:**

```bash
# Count task files
ls {workflow_root_path}/phases/*/task-*.md | wc -l
```

Expected: `total_target_tasks` (from Task 1)

### Step 2: Verify Each Phase is Complete

For each phase directory, verify:

```python
for phase_num in range(total_target_phases):
    phase_dir = f"{workflow_root_path}/phases/{phase_num}"
    
    # Check phase.md exists
    phase_file = f"{phase_dir}/phase.md"
    assert os.path.exists(phase_file), f"Missing {phase_file}"
    
    # Check all tasks exist for this phase
    phase_data = definition['phases'][phase_num]
    for task in phase_data['tasks']:
        task_file = f"{phase_dir}/task-{task['number']}-{task['name']}.md"
        assert os.path.exists(task_file), f"Missing {task_file}"
```

⚠️ **CONSTRAINT**: If any file is missing, report which ones and STOP

### Step 3: Sample File Content Check

Read a few generated files to ensure they're not empty and have valid content:

```python
# Check first phase file
with open(f"{workflow_root_path}/phases/0/phase.md") as f:
    content = f.read()
    assert len(content) > 100, "Phase file too short"
    assert "# Phase 0:" in content, "Phase file malformed"

# Check first task file  
first_phase = definition['phases'][0]
first_task = first_phase['tasks'][0]
task_file = f"{workflow_root_path}/phases/0/task-1-{first_task['name']}.md"
with open(task_file) as f:
    content = f.read()
    assert len(content) > 50, "Task file too short"
    assert "# Task 1:" in content, "Task file malformed"
```

### Step 4: Verify File Naming Convention

Check that all task files follow the naming pattern:

```
task-{number}-{name}.md
```

No extra characters, correct format, lowercase with hyphens.

### Step 5: Calculate Total Files

```python
total_files_expected = total_target_phases + total_target_tasks
total_files_created = phase_files_created + task_files_created
```

Verify: `total_files_created == total_files_expected`

### Step 6: Prepare Evidence

Gather evidence for Phase 4 validation gate:

```python
evidence = {
    "phase_files_created": phase_files_created,
    "task_files_created": task_files_created,
    "total_files_expected": total_files_expected,
    "all_phases_populated": True  # if all checks passed
}
```

---

## Expected Output

**Verification Results**:
- ✅ All phase files created
- ✅ All task files created
- ✅ File naming correct
- ✅ Content not empty
- ✅ Counts match expected

**Evidence for Validation Gate**:
- `phase_files_created`: {count}
- `task_files_created`: {count}
- `total_files_expected`: {count}
- `all_phases_populated`: true

---

## Quality Checks

✅ Phase file count verified  
✅ Task file count verified  
✅ All phase directories complete  
✅ Sample content checked  
✅ File naming verified  
✅ Total counts match  
✅ Evidence prepared

---

## Checkpoint Evidence

Submit the following evidence to complete Phase 4:

```yaml
evidence:
  phase_files_created: {count}
  task_files_created: {count}
  total_files_expected: {count}
  all_phases_populated: true
```

🚨 **CRITICAL**: All four evidence fields are required to pass the Phase 4 validation gate.

---

## Navigation

🎯 **NEXT-MANDATORY**: ../5/phase.md (after checkpoint passes)

↩️ **RETURN-TO**: phase.md (after task complete, before phase submission)



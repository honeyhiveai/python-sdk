# Task 2: Generate Phase Files

**Phase**: 4 - Phase Content Generation  
**Purpose**: Generate phase.md for each target workflow phase  
**Depends On**: Task 1 (definition loaded)  
**Feeds Into**: Task 3 (Generate Task Files)

---

## Objective

Loop through all phases in the target workflow definition and generate a `phase.md` file for each one using the phase template.

---

## Context

📊 **CONTEXT**: Each phase needs a phase.md file that provides an overview, task list, validation gate, and navigation. We use the phase template from `phases/dynamic/phase-template.md` and substitute variables for each target phase.

🔍 **MUST-SEARCH**: "phase.md structure requirements workflow"

---

## Instructions

### Step 1: Load Phase Template

Read the phase template file:

```
{workflow_root_path}/phases/dynamic/phase-template.md
```

📖 **DISCOVER-TOOL**: Read template file

This template contains placeholders like:
- `{{phase_number}}`
- `{{phase_name}}`
- `{{phase_purpose}}`
- `{{phase_deliverable}}`
- `{{task_count}}`
- `{{task_table}}` (generated from tasks list)
- `{{validation_gate_table}}` (generated from validation gate)

### Step 2: Loop Through Phases

For each phase in `definition['phases']`:

```python
for phase in definition['phases']:
    phase_number = phase['number']
    phase_name = phase['name']
    phase_purpose = phase['purpose']
    phase_deliverable = phase['deliverable']
    tasks = phase['tasks']
    validation_gate = phase.get('validation_gate', {})
    
    # Generate content (see Step 3)
```

### Step 3: Generate Phase Content

For each phase, create the phase.md content:

**A. Build Task Table:**

```markdown
| # | Task | File | Status |
|---|------|------|--------|
| 1 | Task Name | task-1-task-name.md | ⬜ |
| 2 | Another Task | task-2-another-task.md | ⬜ |
...
```

**B. Build Validation Gate Table:**

```markdown
| Evidence | Type | Validator | Description |
|----------|------|-----------|-------------|
| field_name | type | validator | description |
...
```

**C. Substitute Variables in Template:**

Replace all placeholders:
- `{{phase_number}}` → phase number
- `{{phase_name}}` → phase name
- `{{phase_purpose}}` → phase purpose
- `{{phase_deliverable}}` → phase deliverable
- `{{task_count}}` → len(tasks)
- `{{task_table}}` → generated task table
- `{{validation_gate_table}}` → generated validation gate table
- `{{prev_phase}}` → phase_number - 1 (for navigation)
- `{{next_phase}}` → phase_number + 1 (for navigation)

### Step 4: Write Phase File

For each phase, write the generated content:

```
{workflow_root_path}/phases/{phase_number}/phase.md
```

📖 **DISCOVER-TOOL**: Write content to file

⚠️ **CONSTRAINT**: Phase directory must already exist (created in Phase 2)

### Step 5: Track Progress

Keep count of phase files created for validation:

```python
phase_files_created = 0
for phase in definition['phases']:
    # Generate and write phase.md
    phase_files_created += 1
```

---

## Expected Output

**Files Created**:
- `phases/0/phase.md`
- `phases/1/phase.md`
- `phases/2/phase.md`
- ... (one per target phase)

**Variables to Capture**:
- `phase_files_created`: Integer (count of phase.md files written)

---

## Quality Checks

✅ Phase template loaded  
✅ All phases processed  
✅ Task tables generated correctly  
✅ Validation gate tables generated correctly  
✅ All placeholders substituted  
✅ Files written to correct locations  
✅ Count matches expected phases

---

## Navigation

🎯 **NEXT-MANDATORY**: task-3-generate-task-files.md

↩️ **RETURN-TO**: phase.md (after task complete)



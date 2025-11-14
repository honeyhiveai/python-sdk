# Task 1: Load Target Definition

**Phase**: 4 - Phase Content Generation  
**Purpose**: Load workflow definition YAML for iteration  
**Depends On**: Phase 1 (definition validation)  
**Feeds Into**: Task 2 (Generate Phase Files)

---

## Objective

Load the target workflow definition YAML into memory and prepare for iteration over phases and tasks.

---

## Context

📊 **CONTEXT**: The workflow definition was validated in Phase 1 and archived in Phase 3. We need to load it again for file generation. The definition contains all metadata needed to generate phase and task files.

---

## Instructions

### Step 1: Get Definition Path

The definition path was captured in Phase 1 evidence:
- From workflow options: `definition_path`
- Or from Phase 3 archive: `supporting-docs/workflow-definition.yaml`

Use the path from Phase 1 (stored in workflow state/artifacts).

📖 **DISCOVER-TOOL**: Read file contents

### Step 2: Load YAML

Load the workflow definition YAML file:

```python
import yaml

with open(definition_path, 'r') as f:
    definition = yaml.safe_load(f)
```

📖 **DISCOVER-TOOL**: Parse YAML file

### Step 3: Extract Key Data

From the loaded definition, extract:

**Target Workflow Metadata:**
- `name`: Target workflow name
- `version`: Target workflow version
- `workflow_type`: Type of workflow

**Phases Array:**
- `phases`: List of all phase definitions
- Each phase has: `number`, `name`, `purpose`, `deliverable`, `tasks`, `validation_gate`

**Quality Standards** (if present):
- `quality_standards`: Override defaults for task file generation

### Step 4: Calculate Counts

Count what needs to be generated:

```python
total_phases = len(definition['phases'])
total_tasks = sum(len(phase['tasks']) for phase in definition['phases'])
```

Store these for verification in Task 4.

### Step 5: Verify Definition Structure

Quick sanity check:
- ✅ `phases` is a non-empty list
- ✅ Each phase has required fields (`number`, `name`, `tasks`)
- ✅ Each task has required fields (`number`, `name`, `purpose`)

⚠️ **CONSTRAINT**: If validation fails, STOP and report error (should not happen if Phase 1 passed)

---

## Expected Output

**Variables to Capture**:
- `definition`: Complete workflow definition dict
- `target_workflow_name`: String
- `total_target_phases`: Integer
- `total_target_tasks`: Integer
- `phases_to_generate`: List of phase dicts
- `workflow_root_path`: Path to target workflow directory (from Phase 2)

**These variables feed into Tasks 2-3 for file generation.**

---

## Quality Checks

✅ Definition loaded successfully  
✅ YAML parsed without errors  
✅ Phases array extracted  
✅ Counts calculated  
✅ Structure validated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-2-generate-phase-files.md

↩️ **RETURN-TO**: phase.md (after task complete)



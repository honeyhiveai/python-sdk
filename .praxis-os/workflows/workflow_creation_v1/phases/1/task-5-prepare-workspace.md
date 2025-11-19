# Task 5: Prepare Workspace

**Phase**: 1 - Definition Import & Validation  
**Purpose**: Extract metadata, set up iteration variables  
**Depends On**: Task 4 (completeness_valid)  
**Feeds Into**: Phase 2 (Workflow Scaffolding)

---

## Objective

Prepare all necessary variables and metadata for workflow creation, including dynamic iteration configuration if applicable.

---

## Instructions

### Step 1: Extract Core Metadata

From the validated definition, extract:

**Basic Info**:
- `target_workflow_name` (from `name`)
- `target_workflow_version` (from `version`)
- `target_workflow_type` (from `workflow_type`)

**Counts**:
- `total_target_phases` (number of phases)
- `total_target_tasks` (sum of tasks across all phases)

**Flags**:
- `is_dynamic` (from `dynamic` field, default false)

### Step 2: Prepare Dynamic Configuration (if applicable)

If `is_dynamic == true`:

Extract from `dynamic_config`:
- `source_type` (e.g., "workflow_definition")
- `iteration_logic` (e.g., "per_target_phase")
- `variables` (object with variable definitions)
- `templates.phase` (path to phase template)
- `templates.task` (path to task template)

Calculate:
- `dynamic_iteration_count` (number of times to iterate)
- `static_phase_numbers` (list of non-dynamic phase numbers)

### Step 3: Prepare Directory Paths

Calculate all paths needed for creation:

```
workflow_root = .praxis-os/workflows/{target_workflow_type}/
  - metadata.json
  - core/
  - supporting-docs/
  - phases/
    - 0/, 1/, 2/, ... (for each phase)
    - dynamic/ (if is_dynamic)
```

### Step 4: Organize Phase Data

Create an organized structure of all phases and tasks for easy iteration:

```python
phases_to_create = [
  {
    "number": 0,
    "name": "Phase Name",
    "purpose": "...",
    "deliverable": "...",
    "tasks": [
      {"number": 1, "name": "task-name", "purpose": "..."},
      ...
    ],
    "validation_gate": {...}
  },
  ...
]
```

### Step 5: Verify Readiness

Confirm all necessary information is available:
- ✅ Metadata extracted
- ✅ Paths calculated
- ✅ Phase/task data organized
- ✅ Dynamic config prepared (if applicable)

---

## Expected Output

**Evidence for Validation Gate**:
- `definition_path`: String (from Task 1)
- `definition_valid`: Boolean (true if all validation passed)
- `total_target_phases`: Integer
- `total_target_tasks`: Integer

**Additional Variables for Next Phases**:
- `target_workflow_name`: String
- `workflow_root_path`: String
- `phases_to_create`: Array
- `is_dynamic`: Boolean
- `dynamic_config`: Object (if applicable)

---

## Quality Checks

✅ All metadata extracted correctly  
✅ All paths calculated  
✅ Phase data organized  
✅ Ready to begin creation

---

## Checkpoint Evidence

Submit the following evidence to complete Phase 0:

```yaml
evidence:
  definition_path: "path/to/definition.yaml"
  definition_valid: true
  total_target_phases: N
  total_target_tasks: M
```

---

## Navigation

🎯 **NEXT-MANDATORY**: ../2/phase.md (begin Phase 2 after checkpoint passes)

↩️ **RETURN-TO**: phase.md (after task complete, before phase submission)


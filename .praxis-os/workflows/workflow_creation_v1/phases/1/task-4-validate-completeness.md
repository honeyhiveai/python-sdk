# Task 4: Validate Completeness

**Phase**: 1 - Definition Import & Validation  
**Purpose**: Verify all phases have tasks and gates  
**Depends On**: Task 3 (structure_valid)  
**Feeds Into**: Task 5 (Prepare Workspace)

---

## Objective

Ensure every phase in the definition has complete information: tasks, validation gates, and proper structure.

---

## Instructions

### Step 1: Validate Phase Structure

For each phase in `definition.phases`, verify:

**Required Phase Fields**:
- `number` (integer)
- `name` (string)
- `purpose` (string)
- `deliverable` (string)
- `tasks` (array, must contain at least 1 task)
- `validation_gate` (object)

⚠️ **CONSTRAINT**: Every phase MUST have at least 1 task and a validation gate.

### Step 2: Validate Task Structure

For each task in each phase, verify:

**Required Task Fields**:
- `number` (integer)
- `name` (string, kebab-case)
- `purpose` (string)

**Optional Task Fields**:
- `commands_needed` (array)
- `domain_focus` (string)
- `invokes_workflow` (string)
- `invokes_workflow_options` (object)
- `invokes_workflow_required_evidence` (array)

### Step 3: Validate Gate Structure

For each validation gate, verify:

**Required Gate Fields**:
- `evidence_required` (object with at least 1 evidence field)
- `human_approval_required` (boolean)

For each evidence field, verify:
- `type` (string: string|boolean|integer|array|object)
- `description` (string)
- `validator` (string: is_true|file_exists|greater_than_0|etc.)

🔍 **MUST-SEARCH**: "validation gate evidence fields checkpoint loader"

### Step 4: Check Phase Numbering

Verify phases are numbered sequentially (0, 1, 2, ...) or use placeholder format (N+3, N+4).

### Step 5: Count Totals

Calculate:
- Total number of target workflow phases
- Total number of tasks across all phases
- Number of dynamic phases (if applicable)
- Number of static phases

---

## Expected Output

**Variables to Capture**:
- `completeness_valid`: Boolean
- `phase_count`: Integer
- `task_count`: Integer
- `dynamic_phase_count`: Integer (if applicable)
- `validation_errors`: Array (list any errors found)

**If Validation Fails**:
- 🚨 **CRITICAL**: STOP execution
- Report all missing task/gate information
- Report phase numbering issues
- Provide specific fixes needed

---

## Quality Checks

✅ All phases have required fields  
✅ All tasks have required fields  
✅ All gates have evidence requirements  
✅ Phase numbering is sequential  
✅ Totals calculated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-5-prepare-workspace.md

↩️ **RETURN-TO**: phase.md (after task complete)


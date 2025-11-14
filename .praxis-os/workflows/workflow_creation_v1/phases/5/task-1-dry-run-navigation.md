# Task 1: Dry-Run Navigation

**Phase**: 5 - Testing & Delivery  
**Purpose**: Test workflow navigation works (🎯 NEXT-MANDATORY links)  
**Depends On**: Phase 3 (workflow compliant)  
**Feeds Into**: Task 2 (Validate Commands)

---

## Objective

Simulate navigating through the entire workflow to verify all 🎯 NEXT-MANDATORY and ↩️ RETURN-TO links are correct and unbroken.

---

## Context

📊 **CONTEXT**: Navigation is the backbone of workflow execution. Broken links or incorrect sequencing will cause workflow failures. This dry-run tests the navigation without executing the actual task instructions.

---

## Instructions

### Step 1: Start at Workflow Entry Point

Begin at the first file an agent would read:

```
{workflow_directory_path}/phases/0/phase.md
```

📖 **DISCOVER-TOOL**: Read file contents

Identify the first 🎯 NEXT-MANDATORY command.

### Step 2: Follow Navigation Chain

From Phase 0, follow the navigation sequence:

1. Read current file
2. Find 🎯 NEXT-MANDATORY command
3. Extract target file path
4. Verify target file exists
5. Read target file
6. Repeat

Continue until reaching the end of the workflow.

📖 **DISCOVER-TOOL**: Check file exists, read file

### Step 3: Document Navigation Path

Create a navigation map:

```markdown
## Navigation Map

Phase 0:
  phase.md → task-1-locate-definition.md
  task-1 → task-2-parse-definition.md
  task-2 → task-3-validate-structure.md
  task-3 → task-4-validate-completeness.md
  task-4 → task-5-prepare-workspace.md
  task-5 → ../1/phase.md

Phase 1:
  phase.md → task-1-create-workflow-directory.md
  ...
```

### Step 4: Check for Navigation Errors

Look for:
- **Broken links**: File referenced doesn't exist
- **Wrong paths**: Incorrect relative path syntax
- **Missing links**: Task has no 🎯 NEXT-MANDATORY
- **Circular links**: Task points back to itself or creates loop
- **Orphaned tasks**: Tasks not referenced by any navigation

Document each error found.

### Step 5: Verify Phase Transitions

Check that phase-to-phase navigation is correct:
- Last task of Phase N → Phase N phase.md (for checkpoint)
- After checkpoint pass → Next phase (Phase N+1 phase.md)
- Phase boundaries clear and intentional

### Step 6: Test Return-To Links

For each ↩️ RETURN-TO command:
- Verify target file exists
- Verify it makes logical sense (usually phase.md)
- Check consistency across phase

### Step 7: Check Dynamic Phase Navigation

If workflow is dynamic:
- Verify dynamic template includes navigation logic
- Check iteration variables used correctly
- Confirm last iteration points to correct next phase

### Step 8: Generate Navigation Test Report

```markdown
# Navigation Dry-Run Report

**Total Files Tested**: {count}
**Navigation Links Tested**: {count}
**Broken Links**: {count}
**Missing Links**: {count}
**Circular References**: {count}

## Navigation Flow
✅ Phase 0 → Phase 1: Correct
✅ Phase 1 → Phase 2: Correct
...

## Errors Found
[List all navigation issues]

## Status: {PASS/FAIL}
```

---

## Expected Output

**Variables to Capture**:
- `dry_run_successful`: Boolean (true if no broken links)
- `navigation_errors`: Array (list of issues if any)
- `total_links_tested`: Integer
- `navigation_report`: String (report content)

**If Errors Found**:
- 🚨 **CRITICAL**: Document each error with file and line number
- Navigate back to Phase 3 Task 8 to fix
- Do not proceed until navigation is clean

---

## Quality Checks

✅ Started at entry point  
✅ Followed full navigation chain  
✅ Navigation path documented  
✅ All links verified exist  
✅ Phase transitions checked  
✅ Return-to links verified  
✅ Dynamic navigation checked (if applicable)  
✅ Test report generated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-2-validate-commands.md

↩️ **RETURN-TO**: phase.md (after task complete)


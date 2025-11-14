# Task 2: Create Progress Tracking

**Phase**: 3 - Core Files & Documentation  
**Purpose**: Create progress table template in core/progress-tracking.md  
**Depends On**: Task 1 (command glossary created)  
**Feeds Into**: Task 3 (Archive Definition)

---

## Objective

Create a progress tracking template that workflow users can update to monitor their progress through phases and tasks.

---

## Context

📊 **CONTEXT**: The progress tracking file provides a structured way for users to monitor workflow execution, track quality metrics, document issues, and maintain notes throughout the workflow lifecycle.

---

## Instructions

### Step 1: Design Progress Tracking Structure

The tracking file should include the following sections:

**Section 1: Phase Completion Status**
- Table with columns: Phase | Name | Status | Tasks Complete | Gate Passed
- One row per phase
- Status indicators: ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

**Section 2: Target Workflow Information**
- Fields for capturing key metadata about the workflow being created

**Section 3: Quality Metrics**
- File size compliance tracking
- Command coverage tracking
- Validation gate coverage
- Meta-workflow principle checklist

**Section 4: Known Issues**
- Table for tracking issues discovered during execution
- Columns: Issue | Phase | Severity | Status | Resolution

**Section 5: Notes**
- Free-form section for documentation

### Step 2: Build Phase Completion Table

Using the `phases_to_create` data from Phase 0, create a table row for each phase:

```markdown
| Phase | Name | Status | Tasks Complete | Gate Passed |
|-------|------|--------|----------------|-------------|
| 0 | Definition Import & Validation | ⬜ | 0/{task_count} | ⬜ |
| 1 | Workflow Scaffolding | ⬜ | 0/{task_count} | ⬜ |
...
```

### Step 3: Create Quality Metrics Section

Include tracking for all quality standards from the workflow definition:

```markdown
### File Size Compliance
- **Target**: ≥95% of task files ≤100 lines
- **Current**: _____ / _____ files compliant (____%)

### Command Coverage
- **Target**: ≥80% command language usage
- **Current**: _____%

### Validation Gates
- **Target**: 100% of phases have gates
- **Current**: _____ / _____ phases (____%)
```

### Step 4: Create Meta-Workflow Principles Checklist

Include a checklist for the 5 core principles:

```markdown
| Principle | Status | Notes |
|-----------|--------|-------|
| LLM Constraint Awareness | ⬜ | File sizes, context limits |
| Horizontal Task Decomposition | ⬜ | Single responsibility per task |
| Command Language + Binding | ⬜ | ≥80% coverage |
| Validation Gates at Boundaries | ⬜ | Every phase has checkpoint |
| Evidence-Based Progress | ⬜ | Measurable artifacts |
```

### Step 5: Write Progress Tracking File

Write the complete template to:

```
{workflow_directory_path}/core/progress-tracking.md
```

📖 **DISCOVER-TOOL**: Write content to a file

### Step 6: Verify File Created

Confirm the file was created and is readable.

📖 **DISCOVER-TOOL**: Read file to verify contents

Check:
- File exists at correct path
- All sections present
- Tables properly formatted
- Ready for user to update

---

## Expected Output

**Variables to Capture**:
- `progress_tracking_created`: Boolean (true if successful)
- `progress_tracking_path`: String (path to file)

---

## Quality Checks

✅ Progress tracking structure designed  
✅ Phase table includes all phases  
✅ Quality metrics section created  
✅ Principles checklist included  
✅ Issues tracking table added  
✅ File written successfully  
✅ File verified readable

---

## Navigation

🎯 **NEXT-MANDATORY**: task-3-archive-definition.md

↩️ **RETURN-TO**: phase.md (after task complete)


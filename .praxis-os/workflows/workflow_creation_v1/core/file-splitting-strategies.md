# File Splitting Strategies

**Type**: Tier 2 (Methodology - On-Demand Reading)  
**Purpose**: Practical strategies for splitting oversized task files while maintaining workflow integrity  
**Referenced by**: Phase 3, Task 8 (Fix Violations)

---

## Overview

When task files exceed size limits, they must be split horizontally into multiple focused tasks. This document provides proven strategies for identifying split points, executing splits, and maintaining workflow coherence.

---

## When to Split

### Size-Based Triggers

- **Must split**: >170 lines
- **Should split**: >150 lines and complex
- **Consider splitting**: 100-150 lines with multiple responsibilities

### Responsibility-Based Triggers

- Task name includes "and" (multiple actions)
- Purpose statement has multiple verbs
- Instructions switch between unrelated concerns
- More than 8-10 steps
- More than 8-10 expected outputs

---

## Split Strategy Patterns

### Pattern 1: Sequential Step Split

**When to use**: Task has clear sequence of independent steps

**Original** (180 lines):
```
Task 5: Setup and Validate Environment
- Steps 1-6: Install dependencies
- Steps 7-12: Configure settings
- Steps 13-18: Validate installation
```

**Split into**:
- **Task 5a: Setup Environment** (90 lines)
  - Steps 1-6: Install dependencies
  - Steps 7-12: Configure settings
  
- **Task 5b: Validate Environment** (90 lines)
  - Steps 1-6: Run validation checks
  - Depends on: Task 5a

**Navigation updates**:
```markdown
# Task 5a
🎯 NEXT-MANDATORY: task-5b-validate-environment.md

# Task 5b
🎯 NEXT-MANDATORY: task-6-next-task.md  # Original next
```

---

### Pattern 2: Prepare/Execute Split

**When to use**: Task has distinct preparation and execution phases

**Original** (200 lines):
```
Task 3: Generate Compliance Report
- Steps 1-8: Gather all metrics
- Steps 9-15: Format report
- Steps 16-20: Write file
```

**Split into**:
- **Task 3a: Gather Compliance Metrics** (100 lines)
  - Steps 1-8: Collect data from audits
  - Output: metrics object
  
- **Task 3b: Generate Compliance Report** (100 lines)
  - Input: metrics from 3a
  - Steps 1-8: Format and write report
  - Depends on: Task 3a

---

### Pattern 3: Create/Verify Split

**When to use**: Task creates something then validates it

**Original** (190 lines):
```
Task 7: Create and Verify Scaffolding
- Steps 1-12: Create directories
- Steps 13-20: Verify structure
```

**Split into**:
- **Task 7a: Create Scaffolding** (95 lines)
  - Steps 1-12: Create all directories
  
- **Task 7b: Verify Scaffolding** (95 lines)
  - Steps 1-8: Verify each directory
  - Depends on: Task 7a

---

### Pattern 4: Extract Methodology to Core

**When to use**: Task contains extensive how-to guidance

**Original** (250 lines):
```
Task 6: Create Usage Guide
- Step 1: Review structure (40 lines of structure detail)
- Step 2: Extract content (20 lines)
- Step 3: Write sections (150 lines of section templates)
- Step 4: Verify completeness (40 lines)
```

**Refactor**:
- **Create**: `core/usage-guide-structure.md` (200+ lines)
  - All structure templates
  - Section-by-section guidance
  
- **Slim Task 6**: (80 lines)
  ```markdown
  ⚠️ MUST-READ: [../../core/usage-guide-structure.md]
  
  Steps:
  1. Review structure template (in core file)
  2. Extract content from definition
  3. Write using template structure
  4. Verify completeness
  ```

---

### Pattern 5: Multi-Category Split

**When to use**: Task handles multiple categories of similar items

**Original** (220 lines):
```
Task 2: Validate All Commands
- Validate NEXT-MANDATORY (40 lines)
- Validate MUST-SEARCH (40 lines)
- Validate CONSTRAINT (30 lines)
- Validate CRITICAL (30 lines)
- Validate DISCOVER-TOOL (40 lines)
- Validate other commands (40 lines)
```

**Split into**:
- **Task 2a: Validate Navigation Commands** (90 lines)
  - NEXT-MANDATORY
  - RETURN-TO
  
- **Task 2b: Validate Requirement Commands** (90 lines)
  - CONSTRAINT
  - CRITICAL
  - MUST-SEARCH
  
- **Task 2c: Validate Discovery Commands** (70 lines)
  - DISCOVER-TOOL
  - Other commands

---

## Split Execution Process

### Step 1: Identify Split Point

Read oversized file and identify:
- Natural section boundaries
- Logical groupings
- Dependencies between steps
- Output handoffs between sections

**Split point indicators**:
- Section headers (###)
- "After X, proceed to Y"
- Change in focus/topic
- Different outputs

### Step 2: Determine Split Strategy

Choose appropriate pattern from above based on:
- Content structure
- Task purpose
- Dependencies
- Output types

### Step 3: Plan New Task Structure

**For each new task**:
- Task number/letter (5a, 5b or renumber 5, 6)
- Task name (descriptive, single responsibility)
- Purpose (one sentence)
- Depends on (previous task)
- Feeds into (next task)
- Expected outputs

### Step 4: Create New Task Files

**Template for split tasks**:
```markdown
# Task {N}{letter}: {Focused Name}

**Phase**: {phase} - {phase_name}
**Purpose**: {Single focused purpose}
**Depends On**: Task {N-1} or Task {N}{previous_letter}
**Feeds Into**: Task {N}{next_letter} or Task {N+1}

---

## Objective

{Clear, focused objective}

---

## Context

📊 **CONTEXT**: {Explain this task's role in larger process}

{If extracted from methodology, reference}
⚠️ MUST-READ: [../../core/{methodology}.md]

---

## Instructions

### Step 1: {Action}

{Specific instructions}

{Repeat for focused steps}

---

## Expected Output

**Variables to Capture**:
- `{variable}`: {type} ({description})

---

## Quality Checks

✅ {Check 1}
✅ {Check 2}

---

## Navigation

🎯 **NEXT-MANDATORY**: task-{N}{next_letter}-{name}.md

↩️ **RETURN-TO**: phase.md (after task complete)
```

### Step 5: Update Phase Overview

In `phase.md`, update task table:

**Before**:
```markdown
| 5 | Original Task | task-5-original.md | ⬜ |
```

**After**:
```markdown
| 5a | First Part | task-5a-first-part.md | ⬜ |
| 5b | Second Part | task-5b-second-part.md | ⬜ |
```

Or if renumbering:
```markdown
| 5 | First Part | task-5-first-part.md | ⬜ |
| 6 | Second Part | task-6-second-part.md | ⬜ |
| 7 | Next Task | task-7-next-task.md | ⬜ |
```

### Step 6: Update metadata.json

Update tasks array for the phase:

**Before**:
```json
"tasks": [
  {"task_number": 5, "name": "original-task", "file": "task-5-original.md"}
]
```

**After** (with letters):
```json
"tasks": [
  {"task_number": "5a", "name": "first-part", "file": "task-5a-first-part.md"},
  {"task_number": "5b", "name": "second-part", "file": "task-5b-second-part.md"}
]
```

Or (renumbered):
```json
"tasks": [
  {"task_number": 5, "name": "first-part", "file": "task-5-first-part.md"},
  {"task_number": 6, "name": "second-part", "file": "task-6-second-part.md"},
  {"task_number": 7, "name": "next-task", "file": "task-7-next-task.md"}
]
```

### Step 7: Update All Navigation

**Files to update**:
- Previous task's NEXT-MANDATORY
- Phase.md start task (if splitting task 1)
- Any tasks that reference this task in "Depends On"

**Before**:
```markdown
🎯 NEXT-MANDATORY: task-5-original.md
```

**After**:
```markdown
🎯 NEXT-MANDATORY: task-5a-first-part.md
```

### Step 8: Verify Split Integrity

**Checklist**:
- [ ] All original content preserved
- [ ] No duplicated content
- [ ] Dependencies clear
- [ ] Outputs flow correctly (5a output → 5b input)
- [ ] Navigation chain intact
- [ ] Both files ≤150 lines (ideally ≤100)
- [ ] Single responsibility per task
- [ ] phase.md updated
- [ ] metadata.json updated

---

## Naming Conventions

### Using Letters (Preferred for small splits)

- Original: `task-5-setup-and-validate.md`
- Split: `task-5a-setup.md`, `task-5b-validate.md`
- Advantage: Preserves phase numbering
- Use when: Splitting 1-2 tasks

### Renumbering (For major restructures)

- Original: Tasks 5, 6, 7
- After split: Tasks 5, 6, 7, 8, 9
- Task 5 → Tasks 5 + 6
- Old Task 6 → New Task 7
- Advantage: Clean sequential numbering
- Use when: Splitting many tasks, major refactor

---

## Edge Cases

### Splitting Task 1

If splitting the first task of a phase:
- Update phase.md "Start Here" navigation
- Ensure Phase N-1 points to new Task 1a (or new Task 1)

### Splitting Last Task

If splitting the final task of a phase:
- Ensure last split task returns to phase.md
- Ensure last split task has checkpoint evidence instructions

### Splitting Dynamic Templates

If splitting a dynamic template:
- Both splits are templates with variables
- Ensure iteration logic spans both tasks
- Update dynamic phase template navigation

---

## Common Pitfalls

❌ **Arbitrary Split**: Splitting mid-step with no logical boundary  
✅ **Logical Split**: Splitting between complete steps or sections

❌ **Uneven Split**: 30 lines + 170 lines  
✅ **Balanced Split**: 100 lines + 100 lines

❌ **Broken Dependencies**: Task B doesn't receive Task A's output  
✅ **Clear Handoff**: Task A output explicitly feeds Task B input

❌ **Lost Context**: Split tasks missing background  
✅ **Contextual**: Each task has sufficient context section

❌ **Navigation Orphans**: Tasks not linked properly  
✅ **Complete Chain**: Every task has NEXT-MANDATORY and RETURN-TO

---

## Post-Split Validation

After splitting, verify:

1. **File Sizes**: Both files ≤150 lines (ideally ≤100)
2. **Navigation**: Can trace from phase start to end
3. **Dependencies**: All "Depends On" references valid
4. **Outputs**: Variables from Task A available in Task B
5. **Completeness**: All original functionality preserved
6. **Consistency**: Similar structure and formatting
7. **Metadata**: phase.md and metadata.json updated
8. **Quality**: Command coverage maintained

---

**Use these strategies to maintain workflow quality while keeping task files focused and manageable.**


# Phase {{target_phase_number}}: {{target_phase_name}}

**Purpose**: {{target_phase_purpose}}  
**Deliverable**: {{target_phase_deliverable}}

**Iteration**: {{iteration_number}} of {{total_iterations}}

---

## Overview

This phase creates Phase {{target_phase_number}} of the target workflow.

We will:
1. Create the phase.md overview file
2. Create all task files for this phase
3. Ensure proper task sequencing and navigation
4. Verify all files created correctly

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

---

## Context

📊 **CONTEXT**: This is a dynamically generated phase. We are creating Phase {{target_phase_number}} ("{{target_phase_name}}") of the target workflow based on the workflow definition.

**Target Phase Info**:
- **Phase Number**: {{target_phase_number}}
- **Phase Name**: {{target_phase_name}}
- **Purpose**: {{target_phase_purpose}}
- **Deliverable**: {{target_phase_deliverable}}
- **Total Tasks**: {{task_count}}

---

## Tasks

This phase has the following tasks to create:

{{#each target_phase_tasks}}
| {{task_number}} | {{task_name}} | Create task-{{task_number}}-{{task_name}}.md | ⬜ |
{{/each}}

---

## Instructions

### Step 1: Create Phase Overview File

Create `phases/{{target_phase_number}}/phase.md` for the target workflow.

The file should include:
- Phase name, purpose, and deliverable
- Overview of the phase
- Task table listing all tasks
- Validation gate section with evidence requirements
- Navigation (start here, after complete)

🔍 **MUST-SEARCH**: "phase overview file structure format"

**Content Structure**:
```markdown
# Phase {{target_phase_number}}: {{target_phase_name}}

**Purpose**: {{target_phase_purpose}}
**Deliverable**: {{target_phase_deliverable}}

## Overview
[Description of what this phase accomplishes]

## Tasks
[Table with all tasks]

## Validation Gate
[Evidence requirements from definition]

## Navigation
[Start here, after complete links]
```

⚠️ **CONSTRAINT**: The phase overview file should be concise (~80 lines), following three-tier architecture guidance.

### Step 2: Create Each Task File

For each task in `target_phase_tasks`, create a task file:

`phases/{{target_phase_number}}/task-{{number}}-{{name}}.md`

Each task file must include:
- **Header**: Phase, purpose, dependencies, feeds into
- **Objective**: Clear goal statement
- **Context**: Background information (📊 CONTEXT)
- **Instructions**: Step-by-step with command symbols
- **Expected Output**: Variables and artifacts
- **Quality Checks**: Verification checklist
- **Navigation**: Next task and return-to

🔍 **MUST-SEARCH**: "task file structure horizontal decomposition"

**Task File Structure**:
```markdown
# Task {{number}}: {{name}}

**Phase**: {{target_phase_number}} - {{target_phase_name}}
**Purpose**: {{task_purpose}}
**Depends On**: [Dependencies]
**Feeds Into**: [Next tasks]

## Objective
[What this task accomplishes]

## Context
📊 **CONTEXT**: [Helpful background]

## Instructions
### Step 1: [Action]
[Details with commands]

### Step N: [Final action]

## Expected Output
[Variables, artifacts]

## Quality Checks
✅ [Checklist]

## Navigation
🎯 **NEXT-MANDATORY**: task-{{next_number}}-{{next_name}}.md
↩️ **RETURN-TO**: phase.md
```

⚠️ **CONSTRAINT**: Each task file MUST be ≤100 lines. If a task is complex, it must be decomposed further.

### Step 3: Add Domain Expertise via RAG

For tasks that specify a `domain_focus` in the definition, add appropriate 🔍 MUST-SEARCH commands:

Example:
```markdown
## Context

📊 **CONTEXT**: This task requires understanding of validation gate design.

🔍 **MUST-SEARCH**: "validation gate evidence fields checkpoint"
```

This ensures domain knowledge is retrieved when needed without bloating the task file.

### Step 4: Apply Command Language

As you write task instructions, apply the appropriate command symbols:

- 🎯 **NEXT-MANDATORY**: For sequential navigation
- 📖 **DISCOVER-TOOL**: For tool discovery (avoid hardcoding)
- ⚠️ **CONSTRAINT**: For requirements and limits
- 🚨 **CRITICAL**: For hard stops
- 🔍 **MUST-SEARCH**: For RAG queries

Target ≥80% command coverage across the phase.

### Step 5: Implement Task Sequencing

Ensure proper navigation flow:
- First task: phase.md → task-1
- Middle tasks: task-N → task-N+1
- Last task: task-N → phase.md (for checkpoint submission)
- All tasks: ↩️ RETURN-TO: phase.md

### Step 6: Add Validation Gate to Phase Overview

From the workflow definition, extract the validation gate for this phase and add it to the phase.md file.

Format:
```markdown
## Validation Gate

🚨 **CRITICAL**: Phase {{target_phase_number}} MUST complete successfully before proceeding.

**Evidence Required**:

| Evidence | Type | Validator | Description |
|----------|------|-----------|-------------|
{{#each evidence_fields}}
| `{{name}}` | {{type}} | {{validator}} | {{description}} |
{{/each}}

**Human Approval**: {{human_approval_required}}
```

### Step 7: Verify All Files Created

Check that all files for Phase {{target_phase_number}} were created:
- phase.md exists
- All {{task_count}} task files exist
- File names follow pattern
- No missing files

📖 **DISCOVER-TOOL**: List directory contents

---

## Expected Output

**Variables to Capture**:
- `target_phase_{{target_phase_number}}_created`: Boolean
- `target_phase_{{target_phase_number}}_task_count`: Integer
- `target_phase_{{target_phase_number}}_files_verified`: Boolean

---

## Quality Checks

✅ Phase overview file created (~80 lines)  
✅ All task files created (≤100 lines each)  
✅ Domain expertise integrated via MUST-SEARCH  
✅ Command language applied (≥80% coverage)  
✅ Task sequencing implemented  
✅ Validation gate included  
✅ All files verified

---

## Validation Gate

🚨 **CRITICAL**: This dynamic phase iteration MUST complete before proceeding to next iteration.

**Evidence Required**:

| Evidence | Type | Validator | Description |
|----------|------|-----------|-------------|
| `target_phase_{{target_phase_number}}_created` | boolean | is_true | Phase {{target_phase_number}} fully created |
| `target_phase_{{target_phase_number}}_task_count` | integer | equals | Number of task files equals expected count |
| `target_phase_{{target_phase_number}}_files_verified` | boolean | is_true | All phase files verified |

**Human Approval**: Not required

---

## Navigation

{{#if has_next_iteration}}
🎯 **NEXT-MANDATORY**: phase-template.md (next iteration: Phase {{next_phase_number}})
{{else}}
🎯 **NEXT-MANDATORY**: ../4/phase.md (proceed to Meta-Workflow Compliance)
{{/if}}

↩️ **RETURN-TO**: ../2/phase.md (if returning from iteration)


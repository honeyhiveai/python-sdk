# Task Parser - Parsing tasks.md Structure

**Type:** Tier 2 (Methodology - On-Demand Reading)  
**Purpose:** Comprehensive guide for parsing tasks.md structure to extract phases, tasks, dependencies, and validation gates  
**Referenced by:** Phase 0, Task 2

---

## Overview

This document provides a systematic methodology for parsing a specification's `tasks.md` file to extract all phases, individual tasks, dependencies, and validation gates. This parsing is critical for building the execution plan.

---

## tasks.md Structure Standards

### Standard Format

A well-structured tasks.md follows this pattern:

```markdown
# Implementation Task Breakdown

## Phase 1: [Phase Name] ([Timeframe])

**Goal:** [What this phase achieves]

**Tasks:**

- **Task 1.1**: [Task description]
  - **Estimated Time**: [Duration]
  - **Dependencies**: [Task IDs or "None"]
  - **Acceptance Criteria**:
    - [ ] [Criterion 1]
    - [ ] [Criterion 2]

- **Task 1.2**: [Task description]
  - **Estimated Time**: [Duration]
  - **Dependencies**: Task 1.1
  - **Acceptance Criteria**:
    - [ ] [Criterion 1]

**Phase Deliverables:**
- [Deliverable 1]
- [Deliverable 2]

**Validation Gate:**
- [ ] [Gate criterion 1]
- [ ] [Gate criterion 2]

---

## Phase 2: [Phase Name] ([Timeframe])
[... repeat structure]
```

---

## Parsing Steps

### Step 1: Extract Phase Headers

**Pattern to match:** `## Phase N: Name (Timeframe)`

**Regex (conceptual):**
```regex
^## Phase (\d+): (.+?) \((.+?)\)
```

**Extraction:**
- Phase number: `\d+`
- Phase name: `.+?`
- Timeframe: `.+?` (optional)

**Example:**
```markdown
## Phase 1: Foundation (Week 1, Days 1-3)
```

Extracts:
- Number: 1
- Name: "Foundation"
- Timeframe: "Week 1, Days 1-3"

### Step 2: Extract Phase Goal

**Pattern to match:** `**Goal:**` line after phase header

**Example:**
```markdown
**Goal:** Create foundational module structure
```

Extracts:
- Goal: "Create foundational module structure"

### Step 3: Extract Tasks

**Pattern to match:** `- **Task N.M**:` under **Tasks:** section

**Regex (conceptual):**
```regex
^- \*\*Task (\d+)\.(\d+)\*\*: (.+)
```

**Extraction:**
- Phase number: `\d+`
- Task number: `\d+`
- Description: `.+`

**Example:**
```markdown
- **Task 1.1**: Create models/ module structure
  - **Estimated Time**: 4 hours
  - **Dependencies**: None
```

Extracts:
- Task ID: "1.1"
- Description: "Create models/ module structure"

### Step 4: Extract Task Details

For each task, extract sub-fields:

#### Estimated Time
**Pattern:** `- **Estimated Time**: [duration]`

#### Dependencies
**Pattern:** `- **Dependencies**: [value]`

**Values:**
- "None" → No dependencies
- "Task X.Y" → Depends on task X.Y
- "Tasks X.Y, X.Z" → Multiple dependencies

**Parsing logic:**
```python
if dependencies == "None":
    deps = []
elif "," in dependencies:
    deps = [d.strip() for d in dependencies.split(",")]
else:
    deps = [dependencies.strip()]
```

#### Acceptance Criteria
**Pattern:** Lines starting with `- [ ]` under **Acceptance Criteria:**

**Example:**
```markdown
- **Acceptance Criteria**:
  - [ ] models/__init__.py exists
  - [ ] models/config.py with RAGConfig dataclass
  - [ ] All docstrings complete
```

Extracts list of criteria:
- "models/__init__.py exists"
- "models/config.py with RAGConfig dataclass"
- "All docstrings complete"

### Step 5: Extract Phase Deliverables

**Pattern:** Bullet list under `**Phase Deliverables:**`

**Example:**
```markdown
**Phase Deliverables:**
- models/ module structure
- config/ module structure
- monitoring/ module structure
```

Extracts:
- 3 deliverables

### Step 6: Extract Validation Gates

**Pattern:** Checklist under `**Validation Gate:**`

**Example:**
```markdown
**Validation Gate:**
- [ ] All tasks complete
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
```

Extracts gate criteria:
- "All tasks complete"
- "All tests passing"
- "Code reviewed"
- "Documentation updated"

---

## Data Structure

### Parsed Output Format

```python
{
    "spec_name": "mcp-server-modular-redesign",
    "total_phases": 4,
    "total_tasks": 20,
    "phases": [
        {
            "phase_number": 1,
            "phase_name": "Foundation",
            "timeframe": "Week 1, Days 1-3",
            "goal": "Create foundational module structure",
            "tasks": [
                {
                    "task_id": "1.1",
                    "description": "Create models/ module structure",
                    "estimated_time": "4 hours",
                    "dependencies": [],
                    "acceptance_criteria": [
                        "models/__init__.py exists",
                        "models/config.py with RAGConfig"
                    ]
                },
                {
                    "task_id": "1.2",
                    "description": "Create config/ module structure",
                    "estimated_time": "3 hours",
                    "dependencies": ["Task 1.1"],
                    "acceptance_criteria": [...]
                }
            ],
            "deliverables": [
                "models/ module structure",
                "config/ module structure"
            ],
            "validation_gate": [
                "All tasks complete",
                "All tests passing"
            ]
        }
    ]
}
```

---

## Common Variations

### Variation 1: No Timeframe

```markdown
## Phase 1: Foundation
```

Handle: Timeframe = null

### Variation 2: Inline Dependencies

```markdown
- **Task 1.2**: Create config (depends on 1.1)
```

Parse description for "(depends on ...)" pattern

### Variation 3: Missing Acceptance Criteria

If no criteria listed, use phase validation gate as fallback

### Variation 4: Nested Tasks

```markdown
- **Task 2.1**: Update __main__.py
  - Subtask: Implement config loading
  - Subtask: Initialize engines
```

Flatten to single task or note as implementation details

---

## Validation

### Parsed Data Validation

After parsing, validate:

1. **Phase Continuity**: Phases numbered sequentially (1, 2, 3, ...)
2. **Task Continuity**: Tasks within each phase numbered sequentially (N.1, N.2, N.3, ...)
3. **Dependencies Valid**: All referenced task IDs exist
4. **Acceptance Criteria**: At least 1 criterion per task
5. **Validation Gates**: At least 1 gate per phase

---

## Error Handling

### Common Parsing Errors

**Error 1: Missing Phase Number**
```markdown
## Foundation (Week 1)
```
**Recovery**: Infer from sequence

**Error 2: Malformed Task ID**
```markdown
- Task 1-1: Create module
```
**Recovery**: Normalize to "1.1" format

**Error 3: Ambiguous Dependencies**
```markdown
- **Dependencies**: Previous task
```
**Recovery**: Resolve to prior task ID

---

## Usage in Workflow

### In Phase 0, Task 2

1. Read tasks.md file
2. Apply parsing methodology from this document
3. Extract all phases, tasks, dependencies, gates
4. Validate parsed data
5. Store structured data for execution

### During Execution

- Reference parsed data to determine task sequence
- Use dependencies for execution order
- Use acceptance criteria for validation
- Use validation gates for checkpoints

---

## References

- Three-Tier Architecture: This is Tier 2 (methodology)
- Command Language: Use in parsing output
- Horizontal Decomposition: One task at a time execution

---

**This methodology ensures consistent, accurate parsing of any tasks.md structure, enabling reliable spec execution.**


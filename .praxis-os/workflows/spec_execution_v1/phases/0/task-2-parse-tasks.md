# Task 2: Parse Tasks File

**Phase:** 0 (Spec Analysis & Planning)  
**Purpose:** Extract phases, tasks, dependencies, and validation gates from tasks.md  
**Estimated Time:** 3 minutes

---

## 🎯 Objective

Parse the `tasks.md` file to extract all phases, individual tasks with acceptance criteria, task dependencies, and validation gates. Build a structured understanding of the implementation plan.

---

## Prerequisites

🛑 EXECUTE-NOW: Task 1 must be completed (spec validated)

⚠️ MUST-READ: [../../core/task-parser.md](../../core/task-parser.md) for parsing guidance

---

## Steps

### Step 1: Read tasks.md

Read the complete tasks.md file:

```bash
cat .praxis-os/specs/YYYY-MM-DD-name/tasks.md
```

### Step 2: Extract Phase Structure

Identify all phases by markdown headers (## Phase N: Name):

📊 COUNT-AND-DOCUMENT: Phases Identified

Example structure:
```markdown
## Phase 1: Foundation (Week 1)
## Phase 2: Integration (Week 2)  
## Phase 3: Testing (Week 3)
## Phase 4: Deployment (Week 4)
```

- Total phases: [number]
- Phase list: [phase numbers and names]

### Step 3: Extract Tasks Per Phase

For each phase, extract all tasks (format: - Task N.M: Description):

📊 COUNT-AND-DOCUMENT: Tasks Per Phase

- Phase 1: [number] tasks
- Phase 2: [number] tasks
- Phase 3: [number] tasks
- Phase 4: [number] tasks
- **Total tasks**: [number]

### Step 4: Extract Task Details

For each task, identify:
1. **Task ID** (e.g., 1.1, 2.3)
2. **Description** (what needs to be done)
3. **Estimated Time** (if specified)
4. **Dependencies** (e.g., "Depends on Task 1.2")
5. **Acceptance Criteria** (checklist items)

Example:
```markdown
- Task 1.1: Create models/ module
  - Estimated Time: 4 hours
  - Dependencies: None
  - Acceptance Criteria:
    - [ ] models/__init__.py exists
    - [ ] models/config.py created
```

### Step 5: Extract Validation Gates

Find "Validation Gate" sections for each phase:

📊 COUNT-AND-DOCUMENT: Validation Gates

- Phase 1 gate: [criteria count] criteria
- Phase 2 gate: [criteria count] criteria
- Total gates: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Parsing Complete

- [ ] All phases extracted ✅/❌
- [ ] All tasks extracted with IDs ✅/❌
- [ ] Task details captured (time, dependencies, criteria) ✅/❌
- [ ] Validation gates identified ✅/❌
- [ ] Parse results documented ✅/❌

🚨 FRAMEWORK-VIOLATION: Skipping dependency extraction

Dependencies are critical for execution order. If tasks have dependencies (e.g., "Depends on Task 1.2"), they MUST be extracted and documented.

---

## Evidence Collection

📊 COUNT-AND-DOCUMENT: Parse Results

**Phase Summary:**
- Total phases: [number]
- Total tasks: [number]
- Total validation gates: [number]

**Sample Task (first task):**
- ID: [e.g., 1.1]
- Description: [brief description]
- Estimated time: [if specified]
- Dependencies: [list or "None"]
- Acceptance criteria: [count] criteria

---

## Next Step

🎯 NEXT-MANDATORY: [task-3-build-plan.md](task-3-build-plan.md)

With parsing complete, proceed to build the execution plan and query relevant standards.


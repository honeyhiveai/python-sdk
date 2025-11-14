# Task 2: Break Down into Tasks

**Phase:** 3 (Task Breakdown)  
**Purpose:** Define specific tasks for each phase  
**Estimated Time:** 10 minutes

---

## 🎯 Objective

Break each implementation phase into specific, actionable tasks. Tasks should be small enough to complete in reasonable timeframes but complete enough to represent meaningful progress.

---

## Prerequisites

🛑 EXECUTE-NOW: Task 1 must be completed

- Phases must be identified in tasks.md

⚠️ MUST-READ: Reference template

See `core/tasks-template.md` for task format guidelines and good vs bad examples.

---

## Steps

### Step 1: Review Phase Objectives

For each phase in tasks.md, understand what needs to be accomplished. Review specs.md to see what components, APIs, and data models need to be built.

### Step 2: Identify Tasks for Each Phase

For each phase, list specific actions needed. Follow the pattern from `core/tasks-template.md`:

**Good Task Format:**
```markdown
- [ ] **Task 1.1**: {Specific action}
  - {Sub-action item 1}
  - {Sub-action item 2}
  - {Verification step}
```

**Example from `core/tasks-template.md`:**
```markdown
- [ ] **Task 1.1**: Create database schema
  - Define tables for users, resources, tags
  - Add indexes for foreign keys
  - Create migration file with up/down migrations
  - Verify schema matches data models from specs.md
```

### Step 3: Write Tasks for Each Phase

Add tasks under each phase section:

```markdown
### Phase 1 Tasks

- [ ] **Task 1.1**: {Task name}
  - {Action item}
  - {Action item}
  - Verify {verification}

- [ ] **Task 1.2**: {Task name}
  - {Action item}
  - Verify {verification}
```

**Guidelines:**
- Start task names with action verbs (Create, Implement, Test, Deploy)
- Include specific deliverables (not just "setup database" but "create users, resources, tags tables")
- Add verification steps
- Keep tasks focused (if > 8 hours, consider splitting)

### Step 4: Size Tasks

Use T-shirt sizing from `core/tasks-template.md`:
- **Small (S):** 1-2 hours
- **Medium (M):** 2-4 hours
- **Large (L):** 4-8 hours
- **Extra Large (XL):** Consider breaking down

Estimate time for each task and note if uncertain.

### Step 5: Map Tasks to Design

Ensure tasks trace to components/APIs from specs.md:

```markdown
- [ ] **Task 2.1**: Implement UserService
  - {From specs.md section 2.1 Component: UserService}
```

### Step 6: Validate Task Quality

For each task, check:
- [ ] Action-oriented (starts with verb)
- [ ] Specific deliverables listed
- [ ] Verification included
- [ ] Traceable to specs.md
- [ ] Estimable (can size it)
- [ ] Not too large (< 8 hours)

See `core/tasks-template.md` "Good vs Bad Task Format" for examples.

📊 COUNT-AND-DOCUMENT: Tasks defined
- Phase 1 tasks: [number]
- Phase 2 tasks: [number]
- Total tasks: [number]
- Average size: [S/M/L]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] All phases have tasks defined ✅/❌
- [ ] Minimum 3 tasks per phase ✅/❌
- [ ] Tasks are specific and actionable ✅/❌
- [ ] Tasks include action items ✅/❌
- [ ] Verification steps included ✅/❌
- [ ] Tasks traceable to specs.md ✅/❌

🚨 FRAMEWORK-VIOLATION: Vague tasks

Tasks like "Setup system" or "Implement feature" are too vague. See `core/tasks-template.md` for specific examples.

---

## Next Task

🎯 NEXT-MANDATORY: [task-3-acceptance-criteria.md](task-3-acceptance-criteria.md)

Continue to add acceptance criteria to each task.

# Task 4: Map Dependencies

**Phase:** 3 (Task Breakdown)  
**Purpose:** Identify task and phase dependencies  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Document dependencies between tasks and phases. Dependencies determine execution order and prevent attempting tasks before prerequisites are complete.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-3 must be completed

- All tasks must have acceptance criteria

⚠️ MUST-READ: Reference template

See `core/tasks-template.md` for dependency mapping patterns.

---

## Steps

### Step 1: Identify Phase-Level Dependencies

Document dependencies between phases:

```markdown
## Dependencies

### Phase 1 → Phase 2
{Describe why Phase 2 depends on Phase 1}
Cannot {Phase 2 activity} without {Phase 1 deliverable}.

### Phase 2 → Phase 3
{Describe dependency}
```

**Example from `core/tasks-template.md`:**
```markdown
### Phase 1 → Phase 2
Phase 2 (Implementation) depends on Phase 1 (Setup) being complete.
Cannot write business logic without database schema and models.
```

### Step 2: Identify Task-Level Dependencies

For tasks that depend on other tasks:

```markdown
- [ ] **Task 2.3**: Implement API endpoints
  - **Depends on:** Task 2.1 (data models), Task 2.2 (business logic)
  - {Action items}
```

**Dependency Types:**
- **Hard dependency:** Must be completed first
- **Soft dependency:** Helpful but not required
- **Parallel:** Can be done simultaneously

### Step 3: Document Dependency Patterns

Add visual representation using patterns from `core/tasks-template.md`:

**Linear Dependencies:**
```
Phase 1 → Phase 2 → Phase 3
```

**Parallel with Sync Points:**
```
Phase 1
├── Task 1.1 (parallel)
├── Task 1.2 (parallel)
└── Task 1.3 (depends on 1.1 + 1.2)
```

### Step 4: Validate Execution Order

Check that:
- [ ] No circular dependencies
- [ ] Dependencies are necessary (not just convenient)
- [ ] Parallel tasks are truly independent
- [ ] Blocking tasks identified

**Red flags:**
- Task depends on something in a later phase
- Circular dependency (A depends on B depends on A)
- Every task depends on every other task

### Step 5: Estimate Impact

For each dependency, note:
- **If delayed:** What gets blocked?
- **Critical path:** Which dependencies affect total timeline?

📊 COUNT-AND-DOCUMENT: Dependencies mapped
- Phase dependencies: [number]
- Task dependencies: [number]
- Tasks with no dependencies: [number]
- Parallel tasks: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Phase dependencies documented ✅/❌
- [ ] Task dependencies identified ✅/❌
- [ ] No circular dependencies ✅/❌
- [ ] Parallel tasks identified ✅/❌
- [ ] Execution order validated ✅/❌

🚨 FRAMEWORK-VIOLATION: Circular dependencies

If Task A depends on Task B which depends on Task A, the workflow is impossible to execute. Dependencies must be acyclic.

---

## Next Task

🎯 NEXT-MANDATORY: [task-5-validation-gates.md](task-5-validation-gates.md)

Continue to define phase-level validation gates.

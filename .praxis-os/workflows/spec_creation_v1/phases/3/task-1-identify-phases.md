# Task 1: Identify Implementation Phases

**Phase:** 3 (Task Breakdown)  
**Purpose:** Break implementation into logical phases  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Identify logical phases that group related implementation tasks. Phases should represent clear milestones and follow a sensible execution order.

---

## Prerequisites

🛑 EXECUTE-NOW: Phase 2 must be completed

- Review specs.md for technical design

⚠️ MUST-READ: Query MCP and reference template

```python
MCP: search_standards("task breakdown phased implementation")
```

See `core/tasks-template.md` for complete structure and examples.

---

## Steps

### Step 1: Create tasks.md

Initialize from `core/tasks-template.md`:

```bash
cat > .praxis-os/specs/{SPEC_DIR}/tasks.md << 'EOF'
# Implementation Tasks

**Project:** {FEATURE_NAME}  
**Date:** {CURRENT_DATE}  
**Status:** Draft - Pending Approval

---

## Time Estimates

EOF
```

### Step 2: Identify Phase Categories

Common phase patterns (see `core/tasks-template.md` "Common Patterns"):

- **Setup Phase:** Directory structure, config, database setup
- **Implementation Phases:** Core functionality by component
- **Testing Phase:** Unit tests, integration tests
- **Deployment Phase:** Scripts, monitoring, docs

Choose phases that match your architecture from specs.md.

### Step 3: Write Phase Headers

For each phase:

```markdown
## Phase 1: {Phase Name}

**Objective:** {What this phase accomplishes}

**Estimated Duration:** {hours}

### Phase 1 Tasks

[Tasks will be added in Task 2]
```

### Step 4: Add Time Estimates Summary

```markdown
## Time Estimates

- **Phase 1:** {hours} ({description})
- **Phase 2:** {hours} ({description})
- **Total:** {total hours} ({days})
```

### Step 5: Validate Phase Structure

Check each phase:
- [ ] Clear objective
- [ ] Logical grouping
- [ ] Follows execution order
- [ ] Represents meaningful milestone

📊 COUNT-AND-DOCUMENT: Phases identified
- Total phases: [number]
- Estimated total time: [hours]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] tasks.md created ✅/❌
- [ ] At least 1 phase defined ✅/❌
- [ ] Each phase has clear objective ✅/❌
- [ ] Phases follow logical order ✅/❌
- [ ] Time estimates provided ✅/❌

---

## Next Task

🎯 NEXT-MANDATORY: [task-2-break-down-tasks.md](task-2-break-down-tasks.md)

# Task 3: Write Acceptance Criteria

**Phase:** 3 (Task Breakdown)  
**Purpose:** Add testable criteria to each task  
**Estimated Time:** 7 minutes

---

## 🎯 Objective

Add specific, measurable acceptance criteria to each task. Acceptance criteria define "done" and enable objective verification of task completion.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-2 must be completed

- All tasks must be defined in tasks.md

⚠️ MUST-READ: Reference template

See `core/tasks-template.md` for acceptance criteria guidelines and INVEST criteria.

---

## Steps

### Step 1: Understand INVEST Criteria

From `core/tasks-template.md`:

**I**ndependent: Can be completed independently  
**N**egotiable: Details can be refined  
**V**aluable: Delivers clear value  
**E**stimable: Can be sized  
**S**mall: Fits in reasonable timeframe  
**T**estable: Has clear success criteria ← **This task focuses here**

### Step 2: Add Acceptance Criteria to Each Task

For each task in tasks.md, add:

```markdown
- [ ] **Task 1.1**: {Task name}
  - {Action items}
  
  **Acceptance Criteria:**
  - [ ] {Specific, testable criterion 1}
  - [ ] {Specific, testable criterion 2}
  - [ ] {Specific, testable criterion 3}
```

### Step 3: Write Measurable Criteria

Follow patterns from `core/tasks-template.md` "Good Acceptance Criteria":

**Good (Measurable):**
```markdown
**Acceptance Criteria:**
- [ ] All unit tests passing (>80% coverage)
- [ ] API endpoint responds within 200ms (p95)
- [ ] Error handling covers 5 identified edge cases
- [ ] Documentation includes 3 code examples
- [ ] Linter reports zero errors
```

**Bad (Vague):**
```markdown
**Acceptance Criteria:**
- [ ] Code is done
- [ ] Tests exist
- [ ] Works well
```

### Step 4: Cover Different Aspects

For each task, consider criteria for:

**Functionality:**
- [ ] Feature works as specified
- [ ] All edge cases handled
- [ ] Error conditions tested

**Quality:**
- [ ] Tests pass (unit + integration)
- [ ] Code coverage meets minimum
- [ ] Linter has zero errors
- [ ] Code reviewed and approved

**Documentation:**
- [ ] Public APIs have docstrings
- [ ] README updated
- [ ] Examples provided

**Integration:**
- [ ] Works with dependent components
- [ ] Database migrations run successfully
- [ ] Configuration documented

### Step 5: Make Criteria Checkable

Each criterion should be binary (yes/no):

**Good:** "All 15 unit tests passing"  
**Bad:** "Tests mostly working"

**Good:** "API response time < 200ms for 95th percentile"  
**Bad:** "API is fast enough"

**Good:** "Zero linter errors on modified files"  
**Bad:** "Code quality is good"

### Step 6: Validate Criteria Quality

For each task's criteria, check:
- [ ] Specific (clear what to verify)
- [ ] Measurable (can be objectively checked)
- [ ] Relevant (relates to task deliverables)
- [ ] Achievable (realistic to accomplish)
- [ ] Binary (clear yes/no)

📊 COUNT-AND-DOCUMENT: Acceptance criteria
- Total tasks: [number]
- Tasks with criteria: [number]
- Average criteria per task: [number]
- All criteria measurable: [✅/❌]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] All tasks have acceptance criteria ✅/❌
- [ ] Minimum 2 criteria per task ✅/❌
- [ ] All criteria are specific and measurable ✅/❌
- [ ] Criteria are binary (checkable) ✅/❌
- [ ] Cover functionality, quality, documentation ✅/❌

🚨 FRAMEWORK-VIOLATION: Vague acceptance criteria

Criteria like "works well" or "code is good" are not testable. Every criterion must be objectively verifiable.

---

## Next Task

🎯 NEXT-MANDATORY: [task-4-map-dependencies.md](task-4-map-dependencies.md)

Continue to map task and phase dependencies.

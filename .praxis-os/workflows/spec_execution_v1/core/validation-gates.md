# Validation Gates - Quality Checkpoints

**Type:** Tier 2 (Methodology - On-Demand Reading)  
**Purpose:** Extract and validate checkpoint criteria from tasks.md, enforce quality gates  
**Referenced by:** Dynamic task and phase templates

---

## Overview

Validation gates are mandatory checkpoints between phases that prevent advancement until all quality criteria are met. This document defines how to extract gate criteria from tasks.md and how to validate evidence against them.

---

## Gate Levels

### Level 1: Task-Level Gates

**Location:** Task acceptance criteria

**Example:**
```markdown
- **Task 1.1**: Create models/ module
  - **Acceptance Criteria**:
    - [ ] models/__init__.py exists
    - [ ] models/config.py created
    - [ ] All docstrings complete
    - [ ] Tests passing
```

**Purpose:** Validate individual task completion

### Level 2: Phase-Level Gates

**Location:** Phase validation gate section

**Example:**
```markdown
**Validation Gate:**
- [ ] All tasks complete
- [ ] All tests passing  
- [ ] Code reviewed
- [ ] Documentation updated
```

**Purpose:** Validate entire phase before advancing

---

## Extracting Gate Criteria

### From tasks.md

**Pattern 1: Task Acceptance Criteria**

Find checklist under `**Acceptance Criteria:**`

```markdown
- **Acceptance Criteria**:
  - [ ] Criterion 1
  - [ ] Criterion 2
```

Extract all `- [ ]` items.

**Pattern 2: Phase Validation Gate**

Find checklist under `**Validation Gate:**`

```markdown
**Validation Gate:**
- [ ] Gate criterion 1
- [ ] Gate criterion 2
```

Extract all `- [ ]` items.

---

## Mandatory vs Optional Criteria

### Mandatory Criteria

All gates are **mandatory** by default. Tasks or phases cannot be marked complete unless ALL criteria are met.

### Optional Criteria (Not Recommended)

Some specs may mark optional criteria:

```markdown
- [ ] Essential criterion (required)
- [ ] Optional enhancement (nice to have)
```

**Recommendation:** Avoid optional criteria. If it's in the gate, it should be required.

---

## Evidence Collection

### Evidence Types

**Type 1: Boolean Evidence**
```python
{"all_tests_passing": true}
```

**Type 2: Count Evidence**
```python
{"tests_passing": 15, "tests_total": 15}
```

**Type 3: File Evidence**
```python
{"files_created": ["models/__init__.py", "models/config.py"]}
```

**Type 4: Quality Evidence**
```python
{"code_reviewed": true, "linting_passed": true}
```

---

## Validation Logic

### Task-Level Validation

```python
def validate_task_gate(acceptance_criteria, evidence):
    """
    Validate task completion against acceptance criteria.
    
    :param acceptance_criteria: List of criteria from tasks.md
    :param evidence: Dictionary of collected evidence
    :return: (passed: bool, missing: list)
    """
    missing = []
    
    for criterion in acceptance_criteria:
        if not check_criterion(criterion, evidence):
            missing.append(criterion)
    
    passed = len(missing) == 0
    return passed, missing
```

### Phase-Level Validation

```python
def validate_phase_gate(validation_gate, task_evidence, phase_evidence):
    """
    Validate phase completion against validation gate.
    
    :param validation_gate: List of gate criteria from tasks.md
    :param task_evidence: Evidence from all tasks in phase
    :param phase_evidence: Phase-level evidence
    :return: (passed: bool, missing: list)
    """
    missing = []
    
    for criterion in validation_gate:
        if not check_phase_criterion(criterion, task_evidence, phase_evidence):
            missing.append(criterion)
    
    passed = len(missing) == 0
    return passed, missing
```

---

## Common Gate Patterns

### Pattern 1: Completeness Gates

```markdown
- [ ] All tasks in phase completed
- [ ] All files created
- [ ] All functions implemented
```

**Validation:** Check counts match expected totals

### Pattern 2: Quality Gates

```markdown
- [ ] All tests passing
- [ ] No linting errors
- [ ] Code coverage ≥80%
```

**Validation:** Run quality checks, verify passing status

### Pattern 3: Documentation Gates

```markdown
- [ ] API documentation complete
- [ ] README updated
- [ ] Inline comments added
```

**Validation:** Check documentation files exist and are complete

### Pattern 4: Review Gates

```markdown
- [ ] Code reviewed
- [ ] Security review complete
- [ ] Performance validated
```

**Validation:** Check review artifacts exist

---

## Failure Handling

### When Gates Fail

🛑 **STOP execution**

Do NOT advance to next task/phase.

**Actions:**
1. Report which criteria failed
2. Show what evidence is missing
3. Return to incomplete items
4. Re-validate after fixes

### Example Failure Report

```
❌ GATE FAILURE: Phase 1 Validation Gate

Missing criteria:
- [ ] All tests passing (FAILED: 12/15 passing)
- [ ] Code reviewed (FAILED: No review artifact)

Completed criteria:
- [✅] All tasks complete
- [✅] Documentation updated

Action required:
1. Fix 3 failing tests
2. Complete code review
3. Re-submit evidence
```

---

## Integration with Workflow

### Task Completion

1. Execute task
2. Collect evidence
3. Validate against acceptance criteria
4. If passed → Mark complete
5. If failed → Return to task

### Phase Completion

1. Complete all tasks
2. Collect phase-level evidence
3. Validate against validation gate
4. If passed → Advance to next phase
5. If failed → Fix incomplete items

### Using MCP complete_phase()

```python
# Attempt phase completion
result = complete_phase(
    session_id=session_id,
    phase=1,
    evidence={
        "tasks_completed": [1.1, 1.2, 1.3],
        "tests_passing": 15,
        "validation_gate": {
            "all_tasks_complete": true,
            "tests_passing": true,
            "code_reviewed": true
        }
    }
)

# If validation gate fails:
if not result["passed"]:
    print("Missing criteria:", result["missing"])
    # Fix issues and retry
```

---

## Quality Standards Integration

### Mandatory Standards

In addition to gates defined in tasks.md, ALL tasks must meet:

**Production Code Checklist:**
- [ ] Sphinx docstrings
- [ ] Type hints
- [ ] Error handling
- [ ] Resource lifecycle management
- [ ] Tests (unit + integration)

These are **implicit gates** enforced by the workflow, even if not explicitly in tasks.md.

---

## Gate Design Guidelines

### For Spec Authors

When designing gates in tasks.md:

1. **Be Specific**: "Tests passing" better than "Code works"
2. **Be Measurable**: "Coverage ≥80%" better than "Good coverage"
3. **Be Complete**: Include all quality dimensions
4. **Be Realistic**: Don't require perfection

### Anti-Patterns

❌ **Too Vague**: "Code is good"  
✅ **Better**: "All tests passing, no linting errors"

❌ **Unmeasurable**: "Performance is acceptable"  
✅ **Better**: "Response time <100ms for 95th percentile"

❌ **Too Lenient**: "Some tests passing"  
✅ **Better**: "All tests passing"

---

## References

- Task Parser (task-parser.md): Provides gate criteria data
- Command Language: Uses 🛑 VALIDATE-GATE command
- Production Code Checklist: Implicit quality gates

---

**Validation gates are the quality firewall. They prevent bad code from advancing and ensure systematic, high-quality delivery.**


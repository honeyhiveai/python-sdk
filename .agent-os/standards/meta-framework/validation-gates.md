# Validation Gates - Universal Meta-Framework Pattern

**Timeless pattern for ensuring quality at phase boundaries**

## What Is a Validation Gate?

A **validation gate** is an explicit checkpoint with measurable criteria that must be satisfied before proceeding to the next phase.

**Core Insight**: Without explicit gates, AI will claim completion prematurely. Gates force verification.

---

## The Trust Problem

**Without Gates**:
```
Phase 1 → Phase 2 → Phase 3
  ↓         ↓         ↓
Trust AI  Trust AI  Trust AI
```

Result: 60-70% actual completion, work quality varies

**With Gates**:
```
Phase 1 → [Validate ✅/❌] → Phase 2 → [Validate ✅/❌] → Phase 3
            ↑ Explicit                   ↑ Explicit
```

Result: 85-95% actual completion, quality assured

---

## Gate Structure

### Basic Pattern

```markdown
🛑 VALIDATE-GATE: [Phase/Task Name]

**Criteria** (all must be ✅ to proceed):
- [ ] Criterion 1: [specific, measurable] ✅/❌
- [ ] Criterion 2: [specific, measurable] ✅/❌
- [ ] Criterion 3: [specific, measurable] ✅/❌

🚨 FRAMEWORK-VIOLATION: Proceeding with ❌ criteria
```

### Key Elements

1. **Command Symbol** (🛑): Blocking, cannot ignore
2. **Clear Name**: What is being validated
3. **Measurable Criteria**: Specific, verifiable
4. **Checkboxes**: ✅/❌ forcing explicit verification
5. **Violation Warning**: Prevents shortcuts

---

## Gate Types

### Type 1: Completion Gates

Verify phase/task completion:

```markdown
🛑 VALIDATE-GATE: Phase 1 Completion
- [ ] All 6 analysis strategies applied ✅/❌
- [ ] Progress table updated ✅/❌
- [ ] Evidence documented ✅/❌
- [ ] Output files created ✅/❌
```

### Type 2: Quality Gates

Verify output quality:

```markdown
🛑 VALIDATE-GATE: Code Quality
- [ ] Pylint score 10.0/10 ✅/❌
- [ ] All tests passing ✅/❌
- [ ] Coverage ≥80% ✅/❌
- [ ] Documentation complete ✅/❌
```

### Type 3: Prerequisites Gates

Verify readiness to proceed:

```markdown
🛑 VALIDATE-GATE: Phase 2 Prerequisites
- [ ] Phase 1 gate passed ✅/❌
- [ ] Required files exist ✅/❌
- [ ] Dependencies installed ✅/❌
- [ ] Environment configured ✅/❌
```

---

## Measurable Criteria

### ✅ Good Criteria (Specific, Verifiable)

```markdown
- [ ] Exactly 45 test cases written ✅/❌
- [ ] Code coverage is 87% ✅/❌
- [ ] Pylint score is 10.0/10 ✅/❌
- [ ] All 12 functions documented ✅/❌
- [ ] Progress table shows 6/6 complete ✅/❌
```

### ❌ Bad Criteria (Vague, Unverifiable)

```markdown
- [ ] Tests are mostly done ✅/❌
- [ ] Code quality is good ✅/❌
- [ ] Documentation is adequate ✅/❌
- [ ] Most tasks complete ✅/❌
```

---

## Implementation Pattern

### Pattern 1: At Task End

```markdown
## Completion

📊 COUNT-AND-DOCUMENT: Results
- Files created: 3
- Tests written: 12
- Tests passing: 12/12

🛑 VALIDATE-GATE: Task 1 Complete
- [ ] All steps executed ✅/❌
- [ ] Tests passing: 12/12 ✅/❌
- [ ] Files created: 3/3 ✅/❌

🔄 UPDATE-TABLE: Progress

🎯 NEXT-MANDATORY: [next-task.md]
```

### Pattern 2: At Phase Boundary

```markdown
## Phase 2 Completion

🛑 VALIDATE-GATE: Phase 2 Quality
- [ ] Code passes all checks ✅/❌
- [ ] Documentation complete ✅/❌
- [ ] Tests coverage ≥80% ✅/❌
- [ ] Progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: Do NOT proceed with ❌

Upon all ✅:
🎯 NEXT-MANDATORY: [phases/3/entry.md]
```

---

## Enforcement Mechanisms

### Mechanism 1: Violation Warnings

```markdown
🚨 FRAMEWORK-VIOLATION: Skipping Gate

If you proceed without all ✅:
1. Quality cannot be verified
2. Downstream failures likely  
3. Rework required

**STOP. Complete all criteria.**
```

### Mechanism 2: Quantified Evidence

```markdown
🛑 VALIDATE-GATE: Phase Complete
- [ ] 6/6 strategies checked ✅/❌
- [ ] 45/45 tests passing ✅/❌
- [ ] 87% coverage (≥80% required) ✅/❌

📊 Provide actual numbers above.
```

### Mechanism 3: Progress Blocking

```markdown
🛑 VALIDATE-GATE: Prerequisites

Cannot proceed to Phase 2 until:
- [ ] Phase 1 gate passed ✅
- [ ] Files exist ✅
- [ ] Environment ready ✅

🎯 NEXT-MANDATORY: [only when all ✅]
```

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Gate Coverage | 100% phases/tasks | Manual count |
| Criteria Measurability | 100% specific | Review |
| Gate Pass Rate | 85%+ first attempt | Execution log |
| Violation Prevention | 95%+ | Monitor shortcuts |

---

## References

- [Framework Creation Principles](framework-creation-principles.md)
- [Command Language](command-language.md)

---

**Validation gates transform trust-based workflows into verified, high-quality processes.**

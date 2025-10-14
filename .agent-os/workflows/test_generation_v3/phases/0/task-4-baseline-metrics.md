# Task 4: Baseline Metrics Collection

**Phase:** 0 (Setup & Path Selection)  
**Purpose:** Collect pre-generation metrics if test file already exists  
**Estimated Time:** 2 minutes

---

## 🎯 Objective

Check if a test file already exists for the target and collect baseline metrics for comparison.

---

## Prerequisites

- [ ] Task 1 (Environment Validation) complete ✅/❌
- [ ] Task 2 (Target Analysis) complete ✅/❌
- [ ] Task 3 (Path Selection) complete and LOCKED ✅/❌

---

## Steps

### Step 1: Check for Existing Test File

🛑 EXECUTE-NOW: Look for existing tests

```bash
# Check unit tests
ls tests/unit/test_* 2>/dev/null | grep -i [target_module_name] || echo "No existing unit test"

# Check integration tests
ls tests/integration/test_* 2>/dev/null | grep -i [target_module_name] || echo "No existing integration test"
```

🛑 PASTE-OUTPUT: Test file search results

📊 COUNT-AND-DOCUMENT: Existing Tests
- Unit test exists: [yes/no - path if yes]
- Integration test exists: [yes/no - path if yes]

### Step 2: Collect Baseline Metrics (if test exists)

**If NO existing test:**

📊 COUNT-AND-DOCUMENT: Baseline
```markdown
No existing test file - starting from scratch
- Current coverage: N/A
- Current quality: N/A
- Baseline: None
```

Skip to completion criteria.

**If existing test DOES exist:**

🛑 EXECUTE-NOW: Collect current metrics

```bash
# Run existing tests
pytest [existing_test_file] -v

# Check coverage
pytest [existing_test_file] --cov=[module] --cov-report=term

# Check quality
pylint [existing_test_file]
mypy [existing_test_file]
```

🛑 PASTE-OUTPUT: Current test metrics

📊 COUNT-AND-DOCUMENT: Baseline Metrics
- Tests: [X passing, Y failing]
- Coverage: [Z%]
- Pylint: [score/10]
- MyPy: [N errors]

### Step 3: Document Improvement Targets

📊 COUNT-AND-DOCUMENT: Improvement Goals
```markdown
From: [current state]
To: [V3 targets]
- Pass rate: [current%] → 100%
- Coverage: [current%] → 90%+
- Pylint: [current] → 10.0/10
- MyPy: [current errors] → 0
```

---

## Completion Criteria

🛑 VALIDATE-GATE: Baseline Metrics Complete

- [ ] Checked for existing test file ✅/❌
- [ ] Collected baseline metrics (or documented N/A) ✅/❌
- [ ] Improvement targets documented ✅/❌

---

## Evidence Collection

📊 QUANTIFY-RESULTS: Baseline Status
```markdown
Baseline Metrics:
- Existing test: [yes/no]
- Current pass rate: [%] or [N/A]
- Current coverage: [%] or [N/A]
- Current Pylint: [score] or [N/A]
- Target: 100% pass, 90%+ coverage, 10.0/10 Pylint
```

---

## Phase 0 Completion

🔄 UPDATE-TABLE: Progress Tracking
```markdown
| Phase | Status | Evidence | Gate |
|-------|--------|----------|------|
| 0.4: Baseline Metrics | ✅ | [baseline status], ready for Phase 1 | ✅ |
```

🛑 VALIDATE-GATE: Phase 0 Complete

Before proceeding to Phase 1:
- [ ] Environment validated ✅/❌
- [ ] Target analyzed ✅/❌
- [ ] Path selected and LOCKED ✅/❌
- [ ] Baseline collected ✅/❌

📊 QUANTIFY-RESULTS: Phase 0 Summary
```markdown
Phase 0 Complete:
- Environment: ✅ All tools present
- Target: [X lines, Y functions, Z classes]
- Path: [unit | integration] - LOCKED
- Baseline: [status]
- Ready: ✅ Proceed to Phase 1
```

---

## Next Phase

🎯 NEXT-MANDATORY: [../1/phase.md](../1/phase.md)

**Begin Phase 1: Method Verification**
- This is the CRITICAL phase that prevents 22% failure rates
- AST-based deep analysis required
- No shortcuts allowed

---

**Phase 0 Complete** - Foundation established for systematic test generation



# Task 3: Path Selection (CRITICAL)

**Phase:** 0 (Setup & Path Selection)  
**Purpose:** Choose unit OR integration path - LOCKS strategy for entire workflow  
**Estimated Time:** 2 minutes

---

## 🚨 CRITICAL DECISION POINT

**This decision is IRREVERSIBLE and affects all subsequent phases**

Once selected, you CANNOT mix unit and integration strategies.

---

## 🎯 Objective

Select the appropriate test path based on testing goals and lock it for the entire workflow.

---

## Prerequisites

- [ ] Task 1 (Environment Validation) complete ✅/❌
- [ ] Task 2 (Target Analysis) complete ✅/❌
- [ ] Target file complexity understood

---

## Path Options

### Option A: Unit Test Path

**Strategy:** Mock EXTERNAL dependencies (not code under test)

**When to choose:**
- Need 90%+ code coverage
- Testing single module in isolation
- Fast test execution required
- No real API access needed

**What gets mocked:**
- External libraries (requests, os, sys)
- Other internal modules (honeyhive.utils.logger)
- Configuration and environment
- File system operations

**What does NOT get mocked:**
- The code being tested (execute for coverage)
- Test fixtures and helpers

**Quality targets:**
- 100% test pass rate
- 10.0/10 Pylint score
- 0 MyPy errors
- 90%+ line coverage
- 85%+ branch coverage

### Option B: Integration Test Path

**Strategy:** Real API usage with backend verification

**When to choose:**
- Need end-to-end validation
- Testing multi-component integration
- Backend behavior verification required
- Have test API credentials

**What is REAL:**
- API calls to HoneyHive backend
- Configuration from environment
- Logging output
- State changes in backend

**What gets mocked:**
- Only test-specific data
- Nothing in core functionality

**Quality targets:**
- 100% test pass rate
- 10.0/10 Pylint score
- 0 MyPy errors
- Functional flow coverage (no 90% requirement)
- Backend verification with verify_backend_event()

---

## Decision Process

### Step 1: Review Target Analysis

From Task 2, consider:
- File complexity
- Number of external dependencies
- Testing goals (coverage vs integration)

### Step 2: Make Decision

🛑 EXECUTE-NOW: Declare path selection

```markdown
**SELECTED PATH:** [unit | integration]

**Rationale:** [Explain why this path is appropriate for this file]

**Implications Understood:**
- Unit: Will mock all external dependencies, target 90%+ coverage
- Integration: Will use real APIs, verify backend state

**Strategy Locked:** Cannot change path after this point
```

### Step 3: Document Path Lock

📊 COUNT-AND-DOCUMENT: Path Selection
- Path: [unit | integration]
- Rationale: [brief explanation]
- Coverage target: [90%+ for unit | functional for integration]
- Mock strategy: [external deps only | minimal test data only]

---

## Completion Criteria

🛑 VALIDATE-GATE: Path Selection Complete

- [ ] Path selected (unit OR integration) ✅/❌
- [ ] Rationale documented ✅/❌
- [ ] Implications understood ✅/❌
- [ ] Strategy locked and documented ✅/❌

🚨 FRAMEWORK-VIOLATION: Proceeding without path selection
🚨 FRAMEWORK-VIOLATION: Mixing unit and integration strategies later

---

## Evidence Collection

📊 QUANTIFY-RESULTS: Path Lock
```markdown
PATH SELECTION (LOCKED):
- Selected: [unit | integration]
- Rationale: [explanation]
- Coverage target: [90%+ | functional]
- Mock strategy: [external deps | minimal]
- Cannot be changed
```

---

## Next Step

🔄 UPDATE-TABLE: Progress Tracking
```markdown
| Phase | Status | Evidence | Gate |
|-------|--------|----------|------|
| 0.3: Path Selection | ✅ | PATH: [unit/integration] - LOCKED | ✅ |
```

🎯 NEXT-MANDATORY: [task-4-baseline-metrics.md](task-4-baseline-metrics.md)

---

**Critical:** All subsequent phases will reference this path selection



# Test Pyramid - Universal Testing Strategy

**Timeless testing strategy applicable to all software development.**

## The Test Pyramid Concept

```
       /\
      /E2E\       ← Few, slow, expensive, brittle
     /------\
    /Integr.\    ← Some, moderate speed, moderate cost
   /----------\
  /   Unit     \ ← Many, fast, cheap, stable
 /--------------\
```

**Principle:** More unit tests, fewer integration tests, even fewer end-to-end tests.

## Why the Pyramid Shape?

### Bottom: Unit Tests (70-80%)
- **What:** Test individual functions/classes in isolation
- **Speed:** Milliseconds per test
- **Cost:** Low (easy to write and maintain)
- **Stability:** High (no external dependencies)
- **Failure diagnosis:** Pinpoints exact issue

### Middle: Integration Tests (15-25%)
- **What:** Test interactions between components
- **Speed:** Seconds per test
- **Cost:** Moderate (setup complexity)
- **Stability:** Moderate (depends on external systems)
- **Failure diagnosis:** Narrows to component interaction

### Top: End-to-End Tests (5-10%)
- **What:** Test complete user workflows
- **Speed:** Minutes per test
- **Cost:** High (complex setup, maintenance burden)
- **Stability:** Low (many failure points)
- **Failure diagnosis:** Could be anywhere in system

## Anti-Pattern: Ice Cream Cone

```
 /--------------\
/   E2E Tests   \ ← Too many slow, brittle tests
 \--------------/
  \  Integr.  /   ← Some integration tests
   \--------/
    \ Unit /      ← Too few unit tests
     \----/
```

**Problems:**
- Slow feedback loops (hours to run tests)
- High maintenance burden (E2E tests break often)
- Poor failure diagnosis (hard to find root cause)
- Expensive CI/CD infrastructure

## Quantified Ratios (Universal Target)

| Test Type | Percentage | Count Example (1000 tests) | Avg Runtime |
|-----------|-----------|---------------------------|-------------|
| Unit | 70-80% | 700-800 tests | <100ms each |
| Integration | 15-25% | 150-250 tests | 1-10s each |
| E2E | 5-10% | 50-100 tests | 10-60s each |

**Total runtime target:** <10 minutes for full suite

## What to Test at Each Level

### Unit Tests (Most)
Test:
- ✅ Business logic functions
- ✅ Data transformations
- ✅ Edge cases and boundary conditions
- ✅ Error handling paths
- ✅ Utility functions
- ✅ Single class behavior

Don't test:
- ❌ External API calls (mock them)
- ❌ Database queries (mock the database)
- ❌ File system operations (mock them)
- ❌ Network requests (mock them)

### Integration Tests (Some)
Test:
- ✅ Database interactions (real database, test data)
- ✅ API client/server interactions
- ✅ Message queue producers/consumers
- ✅ File system operations (with temp files)
- ✅ Component integration (multiple classes)

Don't test:
- ❌ Third-party service calls (use test doubles)
- ❌ Complete user workflows (that's E2E)
- ❌ UI interactions (that's E2E)

### E2E Tests (Few)
Test:
- ✅ Critical user workflows (login, checkout, etc.)
- ✅ Happy path scenarios
- ✅ Major error scenarios (payment failure, etc.)

Don't test:
- ❌ Every edge case (too expensive)
- ❌ Every error path (unit/integration handle this)
- ❌ Every UI permutation (combinatorial explosion)

## Test Coverage vs Test Type

**Coverage target allocation:**
- Unit tests: Cover 80-90% of code
- Integration tests: Cover critical paths (20-30% additional coverage)
- E2E tests: Cover user workflows (5-10% additional coverage)

**Overlap is OK:** Some code is tested at multiple levels for different purposes.

## Implementation Strategy

### Step 1: Start with Units
Build unit test foundation first:
- Fast feedback during development
- Easy to write
- Stable foundation

### Step 2: Add Integration
Test component interactions:
- Validate integration points
- Catch interface mismatches
- Verify external system interactions

### Step 3: Add E2E Last
Only for critical workflows:
- Verify complete system behavior
- Catch deployment issues
- Smoke tests for production

## Test Speed Targets (Universal)

| Test Type | Individual Test | Full Suite |
|-----------|----------------|------------|
| Unit | <100ms | <2 minutes |
| Integration | 1-10 seconds | <5 minutes |
| E2E | 10-60 seconds | <10 minutes |
| **Total** | | **<10 minutes** |

**Why speed matters:**
- Developers run tests frequently
- Slow tests = less frequent testing = bugs
- Fast feedback = faster iteration

## Language-Specific Implementation

**This document covers universal strategy. For language-specific implementations:**
- See `.agent-os/standards/development/python-testing.md` (pytest, unittest, coverage.py)
- See `.agent-os/standards/development/go-testing.md` (go test, table tests, benchmarks)
- See `.agent-os/standards/development/js-testing.md` (Jest, Mocha, Cypress)
- Etc.

Each language guide will provide:
- Specific testing frameworks
- Code examples
- Project-specific patterns
- Tool configurations

---

**The pyramid shape is universal. The tools and syntax vary by language.**

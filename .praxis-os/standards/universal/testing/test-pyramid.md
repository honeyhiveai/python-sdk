# Test Pyramid - Universal Testing Strategy

**Timeless testing strategy for balanced, maintainable test suites.**

---

## 🚨 Test Pyramid Quick Reference (TL;DR)

**Keywords for search**: test pyramid, testing strategy, unit tests integration tests, e2e testing, test ratios, testing best practices, how to structure tests, test coverage, fast tests, test suite organization, testing levels

**Critical test ratios (Universal Target):**

| Test Type | Percentage | Speed | Purpose |
|-----------|-----------|-------|---------|
| **Unit Tests** | 70-80% | <100ms | Test individual functions/classes in isolation |
| **Integration Tests** | 15-25% | 1-10s | Test component interactions |
| **End-to-End Tests** | 5-10% | 10-60s | Test complete user workflows |

**The pyramid principle:** More unit tests (fast, cheap, stable), fewer integration tests (moderate), even fewer E2E tests (slow, expensive, brittle).

**Target suite runtime:** <10 minutes total

**When to query this standard:**
- Planning test strategy → `pos_search_project(content_type="standards", query="test pyramid ratios")`
- Too many slow tests → `pos_search_project(content_type="standards", query="e2e testing best practices")`
- Deciding what to test → `pos_search_project(content_type="standards", query="unit vs integration testing")`
- Test suite too slow → `pos_search_project(content_type="standards", query="fast test suite")`
- Code coverage targets → `pos_search_project(content_type="standards", query="test coverage strategy")`

**For complete guide with examples, continue reading below.**

---

## Questions This Answers

- "How many unit tests vs integration tests should I have?"
- "What is the test pyramid and why does it matter?"
- "Why is my test suite so slow?"
- "What should I test with unit tests vs integration tests?"
- "How do I structure my testing strategy?"
- "What are good test coverage targets?"
- "When should I write E2E tests vs unit tests?"

---

## What is the Test Pyramid?

The Test Pyramid is a testing strategy that visualizes the ideal distribution of tests across different levels:

```
       /\
      /E2E\       ← Few (5-10%), slow, expensive, brittle
     /------\
    /Integr.\    ← Some (15-25%), moderate speed/cost
   /----------\
  /   Unit     \ ← Many (70-80%), fast, cheap, stable
 /--------------\
```

**Core principle:** More unit tests at the base (fast, cheap, stable), fewer integration tests in the middle (moderate), and even fewer end-to-end tests at the top (slow, expensive, brittle).

**Created by:** Mike Cohn (2009), refined by Martin Fowler  
**Applies to:** All software systems, all languages  
**Purpose:** Fast feedback, reliable tests, maintainable test suites

---

## Why the Pyramid Shape Matters

Understanding each layer's purpose and characteristics helps you structure your test suite correctly.

### How to Structure Unit Tests (Bottom Layer: 70-80%)

**What unit tests are:**
- **What:** Test individual functions/classes in isolation
- **Speed:** Milliseconds per test (<100ms target)
- **Cost:** Low (easy to write and maintain)
- **Stability:** High (no external dependencies)
- **Failure diagnosis:** Pinpoints exact issue immediately
- **When to run:** Every code change, continuous during development

**Why so many:**
- Catch bugs early (at the source)
- Fast feedback loop (seconds, not minutes)
- Easy to debug (test fails = you know exactly what broke)
- Cheap to maintain (no infrastructure needed)
- Run thousands in seconds

### How to Structure Integration Tests (Middle Layer: 15-25%)

**What integration tests are:**
- **What:** Test interactions between components
- **Speed:** Seconds per test (1-10s target)
- **Cost:** Moderate (setup complexity, test data management)
- **Stability:** Moderate (depends on external systems like databases)
- **Failure diagnosis:** Narrows to component interaction
- **When to run:** Before commit, CI pipeline

**Why fewer than unit:**
- Slower to run (need real database, services)
- More expensive to maintain (test data, infrastructure)
- Less precise diagnosis (which component failed?)
- Still valuable (catch integration issues)

### How to Structure E2E Tests (Top Layer: 5-10%)

**What E2E tests are:**
- **What:** Test complete user workflows through UI/API
- **Speed:** Minutes per test (10-60s target)
- **Cost:** High (complex setup, maintenance burden)
- **Stability:** Low (many failure points: UI, API, database, network)
- **Failure diagnosis:** Could be anywhere in system
- **When to run:** Pre-release, nightly builds, smoke tests

**Why so few:**
- Very slow (limits how often you can run them)
- Very brittle (break due to UI changes, timing issues)
- Hard to debug (which layer caused the failure?)
- Expensive infrastructure (browsers, test environments)
- Still critical (verify complete system works)

---

## How to Recognize Test Suite Problems (Anti-Patterns)

### Anti-Pattern 1: Ice Cream Cone (Inverted Pyramid)

```
 /--------------\
/   E2E Tests   \ ← Too many (50%+): slow, brittle tests
 \--------------/
  \  Integr.  /   ← Some (30%): moderate tests
   \--------/
    \ Unit /      ← Too few (20%): fast, stable tests
     \----/
```

**Symptoms:**
- Test suite takes hours to run
- Tests break frequently due to minor UI changes
- Hard to diagnose test failures
- Developers skip running tests locally (too slow)
- High CI/CD infrastructure costs

**Consequences:**
- Slow feedback loops (hours to find bugs)
- High maintenance burden (constantly fixing E2E tests)
- Poor failure diagnosis (hard to find root cause)
- Developers lose trust in tests
- Bugs reach production (tests too slow to run frequently)

**How to fix:**
- Stop writing new E2E tests temporarily
- Convert E2E tests to integration or unit tests where possible
- Focus on building unit test coverage
- Reserve E2E for truly critical workflows only

### Anti-Pattern 2: Manual Testing Hourglass

```
     /E2E\       ← Reasonable E2E
    /------\
   / Manual \    ← Too much manual testing
  /----------\
 /   Unit     \  ← Good unit tests
/--------------\
```

**Problem:** Large middle layer is manual testing (slow, error-prone, expensive).

**Fix:** Convert manual tests to automated integration tests.

---

## How to Calculate Test Ratios (Universal Targets)

### The 70-15-5 Rule Explained

| Test Type | Percentage | Count (if 1000 total) | Individual Runtime | Suite Runtime |
|-----------|-----------|----------------------|-------------------|---------------|
| **Unit** | 70-80% | 700-800 tests | <100ms each | <2 minutes |
| **Integration** | 15-25% | 150-250 tests | 1-10s each | <5 minutes |
| **E2E** | 5-10% | 50-100 tests | 10-60s each | <10 minutes |
| **TOTAL** | 100% | 1000 tests | | **<10 minutes** |

**Flexibility:** These are guidelines, not rigid rules. Adjust based on:
- System complexity (microservices need more integration tests)
- Team size (small teams may use fewer E2E)
- Release frequency (daily deploys need faster suites)
- Criticality (payment systems need more E2E)

**Minimum viable pyramid:** 60% unit, 30% integration, 10% E2E  
**Ideal pyramid:** 75% unit, 20% integration, 5% E2E

---

## What to Test at Each Level

### Unit Tests: What to Test (Most Tests Here)

**✅ DO test with unit tests:**
- Business logic functions (pure functions, calculations)
- Data transformations (parsing, formatting, validation)
- Edge cases and boundary conditions (null, empty, max values)
- Error handling paths (exceptions, error states)
- Utility functions (helpers, formatters)
- Single class behavior (methods, state changes)
- Algorithm correctness (sorting, searching, filtering)

**❌ DON'T test with unit tests:**
- External API calls → Mock them (use test doubles)
- Database queries → Mock the database (use in-memory or mocks)
- File system operations → Mock them (use test filesystem)
- Network requests → Mock them (use test doubles)
- Time-dependent behavior → Mock the clock
- Third-party libraries → Trust their tests

**Example decision:**
```python
# ✅ Unit test: Pure business logic
def calculate_discount(price, customer_tier):
    if customer_tier == "gold":
        return price * 0.20
    elif customer_tier == "silver":
        return price * 0.10
    return 0

# ❌ Don't unit test: Database call (use integration test)
def get_customer_tier(customer_id):
    return database.query("SELECT tier FROM customers WHERE id = ?", customer_id)
```

### Integration Tests: What to Test (Some Tests Here)

**✅ DO test with integration tests:**
- Database interactions (queries, transactions, migrations)
- API client/server interactions (HTTP requests/responses)
- Message queue producers/consumers (Kafka, RabbitMQ)
- File system operations (reading/writing actual files)
- Component integration (multiple classes working together)
- External service interactions (with test instances)

**❌ DON'T test with integration tests:**
- Third-party service calls → Use test doubles or contract tests
- Complete user workflows → That's E2E territory
- UI interactions → That's E2E territory
- Every edge case → Unit tests handle those better (faster)

**Example decision:**
```python
# ✅ Integration test: Real database interaction
def test_user_repository_saves_to_database():
    repo = UserRepository(database=test_database)
    user = User(name="Alice", email="alice@example.com")
    repo.save(user)
    
    retrieved = repo.find_by_email("alice@example.com")
    assert retrieved.name == "Alice"

# ❌ Don't integration test: Pure logic (use unit test)
def test_calculate_discount():  # This should be unit test
    assert calculate_discount(100, "gold") == 20
```

### E2E Tests: What to Test (Few Tests Here)

**✅ DO test with E2E tests:**
- Critical user workflows (login, registration, checkout)
- Happy path scenarios (most common user journey)
- Major error scenarios (payment failure, network timeout)
- Smoke tests (verify deployment succeeded)

**❌ DON'T test with E2E tests:**
- Every edge case → Too expensive (use unit tests)
- Every error path → Too slow (use unit/integration)
- Every UI permutation → Combinatorial explosion (use unit/integration)
- Implementation details → Brittle tests (use lower levels)

**Example decision:**
```python
# ✅ E2E test: Critical workflow
def test_user_can_complete_checkout():
    browser.visit("/products")
    browser.click("Add to Cart")
    browser.click("Checkout")
    browser.fill("card_number", "4111111111111111")
    browser.click("Place Order")
    assert browser.see("Order Confirmed")

# ❌ Don't E2E test: Edge case validation (use unit test)
def test_invalid_credit_card_format():  # This should be unit test
    assert validate_credit_card("123") == False
```

---

## How to Allocate Test Coverage

### Coverage Allocation by Test Level

**Unit tests:** Cover 80-90% of codebase
- Focus on business logic, algorithms, utilities
- High coverage is achievable and maintainable

**Integration tests:** Cover 20-30% additional (critical paths)
- Focus on component interactions, database operations
- Overlap with unit tests is OK

**E2E tests:** Cover 5-10% additional (user workflows)
- Focus on critical user journeys
- Significant overlap with lower levels is expected

**Total unique coverage:** Aim for 90%+ code coverage overall, with most coming from fast unit tests.

### When to Pursue 100% Coverage

✅ **Pursue 100% unit test coverage for:**
- Payment processing logic
- Security/authentication code
- Financial calculations
- Medical/safety-critical systems
- Core business rules

⚠️ **Don't pursue 100% coverage for:**
- Boilerplate code (getters/setters)
- Framework integration code (better as integration tests)
- UI rendering code (better as E2E or visual tests)
- Generated code

---

## How to Implement the Pyramid (Step-by-Step)

### Step 1: Start with Unit Tests

**Build unit test foundation first:**
- Test all business logic functions
- Test all data transformations
- Test all edge cases and error handling
- Mock external dependencies

**Benefits:**
- Fast feedback during development
- Easy to write and maintain
- Stable foundation for refactoring

**Target:** 70-80% code coverage from unit tests alone

### Step 2: Add Integration Tests

**Test component interactions:**
- Database operations (real database, test data)
- API endpoints (real HTTP, test server)
- Message queues (real broker, test topics)
- File operations (real filesystem, temp directories)

**Benefits:**
- Validate integration points work correctly
- Catch interface mismatches early
- Verify external system interactions

**Target:** 15-25% of test suite

### Step 3: Add E2E Tests Last

**Only for critical workflows:**
- User registration and login
- Core product features
- Payment and checkout
- Critical admin operations

**Benefits:**
- Verify complete system behavior
- Catch deployment configuration issues
- Smoke tests for production readiness

**Target:** 5-10% of test suite, <10 tests to start

---

## How Fast Should Tests Run? (Speed Targets)

| Test Type | Individual Test | Full Suite | When to Run |
|-----------|----------------|------------|-------------|
| **Unit** | <100ms | <2 minutes | Every code change |
| **Integration** | 1-10 seconds | <5 minutes | Before commit |
| **E2E** | 10-60 seconds | <10 minutes | Before merge/deploy |
| **Total Suite** | | **<10 minutes** | CI pipeline |

**Why speed matters:**

1. **Fast feedback** → Developers run tests frequently → Bugs caught early
2. **Slow tests** → Developers skip tests → Bugs reach production
3. **10-minute rule** → Maximum acceptable wait time for feedback
4. **Sub-second unit tests** → Enables TDD (test-driven development)

**If your suite is slower:**
- Parallelize tests (run tests concurrently)
- Optimize slow tests (reduce setup, use test doubles)
- Split suites (fast unit tests vs slower integration/E2E)
- Consider test pyramid ratio (too many E2E tests?)

---

## When to Query This Standard

### During Test Planning

```python
# Planning test strategy for new feature
pos_search_project(content_type="standards", query="test pyramid ratios")
pos_search_project(content_type="standards", query="what to test with unit tests")
pos_search_project(content_type="standards", query="test coverage targets")
```

### When Tests Are Too Slow

```python
# Test suite taking too long
pos_search_project(content_type="standards", query="fast test suite optimization")
pos_search_project(content_type="standards", query="test speed targets")
pos_search_project(content_type="standards", query="unit vs integration testing")
```

### When Deciding Test Type

```python
# Deciding where to test specific functionality
pos_search_project(content_type="standards", query="when to write integration tests")
pos_search_project(content_type="standards", query="e2e testing best practices")
pos_search_project(content_type="standards", query="test doubles mocking")
```

### During Code Review

```python
# Reviewing test quality
pos_search_project(content_type="standards", query="test pyramid anti-patterns")
pos_search_project(content_type="standards", query="testing best practices")
```

---

## Cross-References

### Related Testing Standards

Query for comprehensive testing strategy:

```python
# For test implementation details
pos_search_project(content_type="standards", query="test doubles mocking stubs fakes")

# For integration testing patterns
pos_search_project(content_type="standards", query="integration testing database")

# For E2E testing guidance
pos_search_project(content_type="standards", query="end to end testing selenium")

# For test quality checks
pos_search_project(content_type="standards", query="production code checklist testing")
```

**Related Standards:**
- [Test Doubles](test-doubles.md) - Mocks, stubs, spies for unit testing
- [Integration Testing](integration-testing.md) - Database, API, component testing patterns
- [Production Code Checklist](../ai-safety/production-code-checklist.md) - Includes test coverage requirements
- [TDD Practices](test-driven-development.md) - Test-first development approach

### Language-Specific Implementations

This document covers universal strategy. For language-specific tools and patterns:

```python
# Python testing
pos_search_project(content_type="standards", query="pytest unittest python testing")

# Go testing
pos_search_project(content_type="standards", query="go test table tests benchmarks")

# JavaScript testing
pos_search_project(content_type="standards", query="jest mocha cypress javascript testing")

# Java testing
pos_search_project(content_type="standards", query="junit mockito java testing")
```

**Language-Specific Guides:**
- Python: pytest, unittest, coverage.py, mocking patterns
- Go: go test, table tests, benchmark tests, testify
- JavaScript: Jest, Mocha, Chai, Cypress, Playwright
- Java: JUnit, Mockito, TestContainers, Selenium

---

## Common Mistakes and How to Fix Them

### Mistake 1: Writing E2E Tests First

**Problem:** E2E tests are slow and brittle, making early development painful.

**Fix:** Start with unit tests, add integration tests, add E2E tests last.

### Mistake 2: Testing Everything at E2E Level

**Problem:** "If E2E tests catch bugs, more E2E tests = fewer bugs, right?" Wrong!

**Fix:** Test details with unit tests (fast), workflows with E2E tests (slow).

### Mistake 3: No Integration Tests

**Problem:** Unit tests pass, E2E tests pass, but production fails due to integration issues.

**Fix:** Add integration tests for component boundaries (database, APIs, queues).

### Mistake 4: Mocking Everything in Unit Tests

**Problem:** Unit tests pass, but system doesn't work because mocks don't match reality.

**Fix:** Use integration tests to verify mocks match real behavior.

### Mistake 5: Ignoring Test Speed

**Problem:** Test suite takes 2 hours to run, developers stop running tests.

**Fix:** Optimize for speed - parallelize, reduce setup time, check pyramid ratios.

---

**The pyramid shape is universal. The tools and syntax vary by language. Start with unit tests (many, fast, cheap), add integration tests (some, moderate), finish with E2E tests (few, slow, critical). Target: <10 minutes for full suite.**

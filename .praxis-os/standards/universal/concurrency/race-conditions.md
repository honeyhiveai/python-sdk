# Race Conditions - Universal CS Fundamentals

**Timeless pattern applicable to all programming languages and paradigms.**

**Keywords for search**: race condition, race conditions, concurrency bugs, thread safety, shared state, non-deterministic bugs, data races, concurrent access, synchronization, mutex, atomic operations

---

## 🚨 Quick Reference (TL;DR)

**Definition:** Multiple execution contexts access shared state concurrently, at least one modifies it, without synchronization → non-deterministic bug.

**Why Dangerous:**
- Non-deterministic (works 99.9% of time, fails 0.1%)
- Hard to reproduce (timing-dependent)
- Silent data corruption
- Production-only failures

**Four Prevention Strategies:**
1. **Mutual Exclusion (Locks)** - Only one context accesses at a time
2. **Atomic Operations** - Hardware-level indivisible operations
3. **Immutability** - State that never changes can't race
4. **Message Passing** - No shared state, communicate via messages

**Three Common Patterns:**
1. **Check-Then-Act** - Race between check and action
2. **Read-Modify-Write** - Lost updates
3. **Double-Checked Locking** - Partially constructed objects

**Detection:**
- Stress testing (high load)
- Thread sanitizers (TSan, Helgrind)
- Delay injection
- Code review (shared state analysis)

---

## Questions This Answers

- "What is a race condition?"
- "How to detect race conditions in my code?"
- "How to prevent race conditions?"
- "What synchronization mechanisms prevent races?"
- "Why do I have intermittent test failures?"
- "What is check-then-act race condition?"
- "How to test for race conditions?"
- "What tools detect race conditions?"
- "When to use locks vs atomic operations?"
- "What is thread safety?"
- "How to identify shared state?"
- "What causes non-deterministic bugs?"

---

## What is a Race Condition?

A race condition occurs when multiple execution contexts (threads, processes, coroutines, etc.) access shared state concurrently, and at least one modifies it, without proper synchronization.

**The result depends on the timing of execution—a non-deterministic bug.**

## Universal Pattern

```
Context 1: read(x) → compute(x+1) → write(x)
Context 2: read(x) → compute(x+1) → write(x)

Expected result: x increases by 2
Actual result: x increases by 1 (lost update!)
```

## Why Race Conditions Are Dangerous

1. **Non-deterministic**: May work 99.9% of the time, fail 0.1%
2. **Hard to reproduce**: Timing-dependent, load-dependent
3. **Silent corruption**: Data becomes inconsistent without errors
4. **Production failures**: Often only appear under real-world load

## How to Detect Race Conditions?

### 1. How to Analyze Shared State
**Question:** What variables/data structures can be accessed by multiple execution contexts?

- Global variables
- Class instance attributes
- Static/module-level variables
- Database records
- File system
- Network sockets

### 2. How to Analyze Access Patterns
**Question:** For each shared state, what are the access patterns?

- **Read-only**: Safe (no writes = no race)
- **Write-only**: Can have races (ordering matters)
- **Read-write**: Most complex (read-check-modify patterns dangerous)

### 3. How to Recognize Timing-Dependent Behavior
**Symptoms:**
- "Works on my machine, fails in production"
- "Works with 1 user, fails with 100"
- "Intermittent failures"
- "Test passes sometimes, fails other times"

## How to Prevent Race Conditions? (Universal Strategies)

### Strategy 1: How to Use Mutual Exclusion (Locks)
**Concept:** Only one execution context can access the critical section at a time.

**Universal pattern:**
```
acquire_lock()
try:
    # Critical section - access shared state
    read/modify/write shared state
finally:
    release_lock()
```

**When to use:** Simple read-modify-write operations on shared state.

### Strategy 2: How to Use Atomic Operations
**Concept:** Operations that complete in a single, indivisible step.

**Examples:**
- Atomic increment (x++)
- Compare-and-swap (CAS)
- Test-and-set

**When to use:** Simple operations supported by hardware/runtime.

### Strategy 3: How to Use Immutability
**Concept:** State that never changes cannot have race conditions.

**Pattern:**
- Read-only data structures
- Copy-on-write
- Functional programming

**When to use:** When data doesn't need to change frequently.

### Strategy 4: How to Use Message Passing (No Shared State)
**Concept:** Execution contexts communicate via messages, no shared memory.

**Pattern:**
- Actor model
- Channel-based communication
- Event streams

**When to use:** Complex workflows with minimal shared state needs.

## What Are Common Race Condition Patterns?

### Pattern 1: Check-Then-Act
```
if (resource.is_available()):  # Check
    resource.use()              # Act (race between check and act!)
```

**Fix:** Make check-and-act atomic or use locking.

### Pattern 2: Read-Modify-Write
```
x = shared_state.get()  # Read
x = x + 1              # Modify
shared_state.set(x)    # Write (another context may have modified it!)
```

**Fix:** Use atomic operations or locks.

### Pattern 3: Double-Checked Locking (Broken)
```
if (instance is None):       # First check (no lock)
    acquire_lock()
    if (instance is None):   # Second check (with lock)
        instance = create()  # May be partially constructed!
    release_lock()
```

**Fix:** Use proper initialization patterns (language-specific).

## How to Test for Race Conditions?

### Testing Techniques
1. **Stress testing**: High load with many concurrent contexts
2. **Delay injection**: Add sleeps to increase chance of races
3. **Thread sanitizers**: Tools that detect races (TSan, Helgrind)
4. **Code review**: Systematic shared state analysis

### Automated Detection
- Static analysis tools (language-specific)
- Dynamic race detectors (runtime instrumentation)
- Fuzzing with concurrency

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-concurrency.md` (Python)
- See `.praxis-os/standards/development/go-concurrency.md` (Go)
- See `.praxis-os/standards/development/js-concurrency.md` (JavaScript)
- Etc.

Each language-specific guide will map these universal concepts to:
- Language-specific locking primitives
- Language-specific atomic operations
- Language-specific concurrency models
- Language-specific testing tools

---

## When to Query This Standard

This standard is most valuable when:

1. **Debugging Intermittent Failures**
   - Situation: Tests pass sometimes, fail other times
   - Query: `pos_search_project(content_type="standards", query="race condition intermittent failures")`

2. **Implementing Concurrent Code**
   - Situation: Writing multi-threaded or async code
   - Query: `pos_search_project(content_type="standards", query="how to prevent race conditions")`

3. **Code Review for Thread Safety**
   - Situation: Reviewing code that uses shared state
   - Query: `pos_search_project(content_type="standards", query="how to detect race conditions")`

4. **Production Bugs Under Load**
   - Situation: "Works on my machine, fails in production"
   - Query: `pos_search_project(content_type="standards", query="race condition symptoms")`

5. **Choosing Synchronization Strategy**
   - Situation: Deciding between locks, atomics, immutability
   - Query: `pos_search_project(content_type="standards", query="race condition prevention strategies")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Detect races | `pos_search_project(content_type="standards", query="how to detect race conditions")` |
| Prevent races | `pos_search_project(content_type="standards", query="race condition prevention")` |
| Test for races | `pos_search_project(content_type="standards", query="test for race conditions")` |
| Fix check-then-act | `pos_search_project(content_type="standards", query="check-then-act race condition")` |
| Thread safety | `pos_search_project(content_type="standards", query="thread safety patterns")` |

---

## Cross-References and Related Standards

**Concurrency Standards:**
- `standards/concurrency/deadlocks.md` - Deadlock prevention (lock ordering prevents both)
  → `pos_search_project(content_type="standards", query="deadlock prevention")`
- `standards/concurrency/locking-strategies.md` - Choosing the right lock type
  → `pos_search_project(content_type="standards", query="locking strategies")`
- `standards/concurrency/shared-state-analysis.md` - Identifying shared state
  → `pos_search_project(content_type="standards", query="shared state analysis")`

**Testing Standards:**
- `standards/testing/integration-testing.md` - Stress testing concurrent code
  → `pos_search_project(content_type="standards", query="integration testing concurrency")`

**Query workflow for fixing race conditions:**
1. **Detect**: `pos_search_project(content_type="standards", query="how to detect race conditions")` → Identify shared state
2. **Analyze**: `pos_search_project(content_type="standards", query="shared state analysis")` → Determine access patterns
3. **Choose Strategy**: `pos_search_project(content_type="standards", query="race condition prevention")` → Select locks/atomics/immutability
4. **Implement**: `pos_search_project(content_type="standards", query="locking strategies")` → Apply synchronization
5. **Test**: `pos_search_project(content_type="standards", query="test for race conditions")` → Validate with stress tests
6. **Review**: `pos_search_project(content_type="standards", query="deadlock prevention")` → Ensure no new deadlocks

---

**This is a timeless CS fundamental. The concepts apply universally, implementations vary by language. Shared mutable state without synchronization = race condition. Always.**

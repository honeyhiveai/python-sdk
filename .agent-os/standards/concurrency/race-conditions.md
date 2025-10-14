# Race Conditions - Universal CS Fundamentals

**Timeless pattern applicable to all programming languages and paradigms.**

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

## Detection Strategies

### 1. Shared State Analysis
**Question:** What variables/data structures can be accessed by multiple execution contexts?

- Global variables
- Class instance attributes
- Static/module-level variables
- Database records
- File system
- Network sockets

### 2. Access Pattern Analysis
**Question:** For each shared state, what are the access patterns?

- **Read-only**: Safe (no writes = no race)
- **Write-only**: Can have races (ordering matters)
- **Read-write**: Most complex (read-check-modify patterns dangerous)

### 3. Timing-Dependent Behavior
**Symptoms:**
- "Works on my machine, fails in production"
- "Works with 1 user, fails with 100"
- "Intermittent failures"
- "Test passes sometimes, fails other times"

## Prevention Strategies (Universal)

### Strategy 1: Mutual Exclusion (Locks)
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

### Strategy 2: Atomic Operations
**Concept:** Operations that complete in a single, indivisible step.

**Examples:**
- Atomic increment (x++)
- Compare-and-swap (CAS)
- Test-and-set

**When to use:** Simple operations supported by hardware/runtime.

### Strategy 3: Immutability
**Concept:** State that never changes cannot have race conditions.

**Pattern:**
- Read-only data structures
- Copy-on-write
- Functional programming

**When to use:** When data doesn't need to change frequently.

### Strategy 4: Message Passing (No Shared State)
**Concept:** Execution contexts communicate via messages, no shared memory.

**Pattern:**
- Actor model
- Channel-based communication
- Event streams

**When to use:** Complex workflows with minimal shared state needs.

## Common Race Condition Patterns

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

## Testing for Race Conditions

### Techniques
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
- See `.agent-os/standards/development/python-concurrency.md` (Python)
- See `.agent-os/standards/development/go-concurrency.md` (Go)
- See `.agent-os/standards/development/js-concurrency.md` (JavaScript)
- Etc.

Each language-specific guide will map these universal concepts to:
- Language-specific locking primitives
- Language-specific atomic operations
- Language-specific concurrency models
- Language-specific testing tools

---

**This is a timeless CS fundamental. The concepts apply universally, implementations vary by language.**

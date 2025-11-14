# Deadlocks - Universal Concurrency Problem

**Timeless pattern applicable to all concurrent systems.**

**Keywords for search**: deadlock, deadlocks, circular wait, lock ordering, resource starvation, Coffman conditions, mutual exclusion, hold and wait, no preemption, deadlock prevention, deadlock detection, dining philosophers

---

## 🚨 Quick Reference (TL;DR)

**Definition:** Two or more execution contexts permanently blocked, each waiting for the other to release a resource → system hangs indefinitely.

**Four Necessary Conditions (Coffman):**
Deadlock can ONLY occur if ALL four are present:
1. **Mutual Exclusion** - Resources can't be shared
2. **Hold and Wait** - Contexts hold resources while waiting for more
3. **No Preemption** - Resources can't be forcibly taken
4. **Circular Wait** - Circular chain of contexts waiting for each other

**Prevention = Break ANY ONE condition**

**Four Prevention Strategies:**
1. **Lock Ordering** (Break Circular Wait) - Always acquire in same order
2. **Timeout** (Break Hold and Wait) - Release all on timeout, retry
3. **Lock-Free** (Break Mutual Exclusion) - Use atomic operations
4. **All-or-Nothing** (Break Hold and Wait) - Acquire all resources atomically

**Detection & Recovery:**
- **Resource Allocation Graph** - Detect cycles
- **Abort and Restart** - Kill one context to break deadlock
- **Rollback** - Roll back to safe state

**Best Strategy:** Lock ordering (simplest, most effective, no runtime overhead)

---

## Questions This Answers

- "What is a deadlock?"
- "How to prevent deadlocks?"
- "What are the Coffman conditions?"
- "What is lock ordering and why does it work?"
- "How to detect deadlocks?"
- "How to recover from a deadlock?"
- "What is the dining philosophers problem?"
- "When to use timeout vs lock ordering?"
- "What tools detect deadlocks?"
- "How to test for deadlocks?"
- "What is circular wait?"
- "How to avoid nested locking deadlocks?"

---

## What is a Deadlock?

A deadlock occurs when two or more execution contexts are permanently blocked, each waiting for the other to release a resource.

**Result:** System hangs indefinitely, no progress can be made.

## Universal Deadlock Pattern

```
Context 1:              Context 2:
lock(Resource A)        lock(Resource B)
    ↓                       ↓
wait for Resource B     wait for Resource A
    ↓                       ↓
[DEADLOCK - both waiting forever]
```

## What Are the Four Necessary Conditions? (Coffman Conditions)

A deadlock can ONLY occur if ALL four conditions are present:

### 1. Mutual Exclusion
Resources cannot be shared; only one context can hold a resource at a time.

### 2. Hold and Wait
Contexts hold resources while waiting for additional resources.

### 3. No Preemption
Resources cannot be forcibly taken away; they must be voluntarily released.

### 4. Circular Wait
A circular chain of contexts exists where each waits for a resource held by the next.

**Prevention strategy:** Break ANY ONE of these four conditions to prevent deadlocks.

---

## How to Prevent Deadlocks? (Universal Strategies)

### Strategy 1: How to Use Lock Ordering (Break Circular Wait)
**Concept:** Always acquire locks in a consistent global order.

```
// Define global lock order
Resource A = lock_id 1
Resource B = lock_id 2
Resource C = lock_id 3

// ALL contexts must acquire in this order
Context 1:
    acquire(A)  // id 1
    acquire(B)  // id 2
    ...

Context 2:
    acquire(A)  // id 1
    acquire(B)  // id 2
    ...

// No circular wait possible!
```

**Benefits:**
- Simple to implement
- No runtime overhead
- Guaranteed deadlock-free

**Drawbacks:**
- Requires global coordination
- May reduce concurrency (holding locks longer)

---

### Strategy 2: How to Use Timeout (Break Hold and Wait)
**Concept:** Limit how long a context waits for a resource.

```
acquired_locks = []

try:
    acquire(lock_A, timeout=5_seconds)
    acquired_locks.append(lock_A)
    
    acquire(lock_B, timeout=5_seconds)
    acquired_locks.append(lock_B)
    
    # Success - do work
    
except TimeoutError:
    # Release all acquired locks
    for lock in acquired_locks:
        release(lock)
    
    # Back off and retry
    sleep(random_backoff)
    retry()
```

**Benefits:**
- Detects and recovers from deadlocks
- No global coordination needed

**Drawbacks:**
- Wastes work on timeout
- May cause livelock (constant retry without progress)

---

### Strategy 3: How to Use Lock-Free Data Structures (Break Mutual Exclusion)
**Concept:** Use atomic operations instead of locks.

```
// Lock-free increment
old_value = atomic_read(counter)
new_value = old_value + 1
success = atomic_compare_and_swap(counter, old_value, new_value)

if not success:
    retry()  // Another context modified it, try again
```

**Benefits:**
- No locks = no deadlocks
- Better performance under contention

**Drawbacks:**
- Complex to implement
- Limited to simple operations
- ABA problem (value changes, then changes back)

---

### Strategy 4: How to Use All-or-Nothing Resource Acquisition (Break Hold and Wait)
**Concept:** Acquire all resources atomically or none at all.

```
all_resources = [resource_A, resource_B, resource_C]

acquired = try_acquire_all(all_resources)

if acquired:
    # Do work with all resources
    ...
    release_all(all_resources)
else:
    # Couldn't get all resources, retry
    sleep(backoff)
    retry()
```

**Benefits:**
- Prevents holding partial resources
- Clear success/failure

**Drawbacks:**
- Reduces concurrency (must wait for all)
- May cause resource starvation

---

## How to Detect Deadlocks?

### How to Use Resource Allocation Graph
**Concept:** Model resources and contexts as a graph, detect cycles.

```
Graph:
- Nodes: Contexts and Resources
- Edges:
  - Context → Resource: Context waiting for resource
  - Resource → Context: Resource held by context

Cycle detection:
    if cycle exists in graph:
        DEADLOCK DETECTED
```

**Use cases:**
- Operating systems
- Database transaction managers
- Distributed systems

---

## How to Recover from Deadlocks?

### 1. Abort and Restart
**Concept:** Kill one or more contexts to break the deadlock.

```
if deadlock_detected():
    victim = select_victim(contexts)  // Least work done, etc.
    abort(victim)
    restart(victim)
```

**Considerations:**
- Which context to kill? (fairness)
- How to prevent starvation? (killed repeatedly)

### 2. Rollback
**Concept:** Roll context back to a safe state before the deadlock.

```
if deadlock_detected():
    victim = select_victim(contexts)
    rollback_to_checkpoint(victim)
    release_resources(victim)
```

**Use cases:**
- Database transactions (ACID guarantees)
- Distributed systems with checkpointing

---

## What Are Real-World Deadlock Examples?

### Example 1: Dining Philosophers
**Problem:** 5 philosophers, 5 forks, each needs 2 forks to eat.

```
Philosopher 1: fork_1, fork_2
Philosopher 2: fork_2, fork_3
Philosopher 3: fork_3, fork_4
Philosopher 4: fork_4, fork_5
Philosopher 5: fork_5, fork_1  // Circular dependency!
```

**Solution:** Lock ordering (philosophers 1-4 acquire left-then-right, philosopher 5 acquires right-then-left).

### Example 2: Database Transactions
**Problem:** Transaction A locks row 1, waits for row 2. Transaction B locks row 2, waits for row 1.

**Solution:** Database uses deadlock detection (timeout or graph analysis) and aborts one transaction.

### Example 3: Nested Function Calls
**Problem:** Function A acquires lock X, calls function B. Function B tries to acquire lock Y, then lock X (already held by A from another context).

**Solution:** Use reentrant locks (allow same context to re-acquire) or redesign to avoid nested locking.

---

## What Deadlock Anti-Patterns Should I Avoid?

### Anti-Pattern 1: Ignoring Lock Order
❌ Different contexts acquire locks in different orders.

```
Context 1:      Context 2:
lock(A)         lock(B)
lock(B)         lock(A)  // DEADLOCK!
```

### Anti-Pattern 2: No Timeout
❌ Blocking indefinitely without timeout.

```
lock(resource)  // Blocks forever if deadlock occurs
```

### Anti-Pattern 3: Nested Locks Without Reentrant Support
❌ Trying to re-acquire a non-reentrant lock.

```
lock(X)
    function_that_also_locks(X)  // DEADLOCK with self!
```

---

## How to Test for Deadlocks?

### Testing Techniques
1. **Stress testing:** High load with many concurrent contexts
2. **Deadlock detectors:** Tools that analyze lock acquisition patterns
3. **Static analysis:** Detect potential deadlock cycles in code
4. **Fuzzing:** Random execution orders to expose race conditions

### Automated Detection Tools
- **Thread Sanitizer (TSan):** Detects data races and deadlocks (C/C++)
- **Helgrind:** Valgrind tool for threading bugs
- **Language-specific:** Python threading debug, Go race detector, etc.

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-concurrency.md` (Python: `threading.Lock`, deadlock detection)
- See `.praxis-os/standards/development/go-concurrency.md` (Go: `sync.Mutex`, `select` with timeout)
- See `.praxis-os/standards/development/rust-concurrency.md` (Rust: `Mutex<T>`, lock poisoning)
- Etc.

Each language guide will provide:
- Language-specific lock types
- Timeout mechanisms
- Deadlock detection tools
- Code examples

---

## When to Query This Standard

This standard is most valuable when:

1. **System Hangs Indefinitely**
   - Situation: Application freezes, no progress
   - Query: `pos_search_project(content_type="standards", query="deadlock system hangs")`

2. **Implementing Multi-Lock Code**
   - Situation: Need to acquire multiple locks
   - Query: `pos_search_project(content_type="standards", query="how to prevent deadlocks")`

3. **Code Review for Lock Safety**
   - Situation: Reviewing code with multiple locks
   - Query: `pos_search_project(content_type="standards", query="deadlock prevention lock ordering")`

4. **Choosing Deadlock Prevention Strategy**
   - Situation: Deciding between lock ordering, timeout, lock-free
   - Query: `pos_search_project(content_type="standards", query="deadlock prevention strategies")`

5. **Debugging Concurrent System Freeze**
   - Situation: Production system hangs under load
   - Query: `pos_search_project(content_type="standards", query="how to detect deadlocks")`

6. **Understanding Coffman Conditions**
   - Situation: Learning deadlock theory
   - Query: `pos_search_project(content_type="standards", query="Coffman conditions deadlock")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Prevent deadlocks | `pos_search_project(content_type="standards", query="deadlock prevention")` |
| Lock ordering | `pos_search_project(content_type="standards", query="lock ordering prevent deadlock")` |
| Detect deadlocks | `pos_search_project(content_type="standards", query="how to detect deadlocks")` |
| Timeout strategy | `pos_search_project(content_type="standards", query="timeout deadlock prevention")` |
| Dining philosophers | `pos_search_project(content_type="standards", query="dining philosophers deadlock")` |

---

## Cross-References and Related Standards

**Concurrency Standards:**
- `standards/concurrency/race-conditions.md` - Preventing data races (complementary to deadlock prevention)
  → `pos_search_project(content_type="standards", query="race condition prevention")`
- `standards/concurrency/locking-strategies.md` - Choosing lock types (reentrant locks help with nested calls)
  → `pos_search_project(content_type="standards", query="locking strategies")`
- `standards/concurrency/shared-state-analysis.md` - Identifying shared resources that need locks
  → `pos_search_project(content_type="standards", query="shared state analysis")`

**Testing Standards:**
- `standards/testing/integration-testing.md` - Stress testing for deadlocks
  → `pos_search_project(content_type="standards", query="stress testing concurrency")`

**Query workflow for preventing deadlocks:**
1. **Learn Theory**: `pos_search_project(content_type="standards", query="Coffman conditions")` → Understand 4 conditions
2. **Identify Resources**: `pos_search_project(content_type="standards", query="shared state analysis")` → Find what needs locking
3. **Choose Strategy**: `pos_search_project(content_type="standards", query="deadlock prevention strategies")` → Select lock ordering (best)
4. **Implement**: Define global lock order, apply consistently
5. **Test**: `pos_search_project(content_type="standards", query="how to test for deadlocks")` → Stress test with many threads
6. **Review**: Check all lock acquisitions follow order

---

**Deadlocks are a universal problem in concurrent systems. Prevention is better than detection. Lock ordering is the simplest and most effective strategy. Break ANY ONE of the four Coffman conditions to prevent deadlocks.**

# Deadlocks - Universal Concurrency Problem

**Timeless pattern applicable to all concurrent systems.**

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

## The Four Necessary Conditions (Coffman Conditions)

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

## Prevention Strategies (Universal)

### Strategy 1: Lock Ordering (Break Circular Wait)
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

### Strategy 2: Timeout (Break Hold and Wait)
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

### Strategy 3: Lock-Free Data Structures (Break Mutual Exclusion)
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

### Strategy 4: Single-Resource Acquisition (Break Hold and Wait)
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

## Detection Strategies

### Resource Allocation Graph
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

## Recovery Strategies

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

## Real-World Examples

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

## Anti-Patterns

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

## Testing for Deadlocks

### Techniques
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
- See `.agent-os/standards/development/python-concurrency.md` (Python: `threading.Lock`, deadlock detection)
- See `.agent-os/standards/development/go-concurrency.md` (Go: `sync.Mutex`, `select` with timeout)
- See `.agent-os/standards/development/rust-concurrency.md` (Rust: `Mutex<T>`, lock poisoning)
- Etc.

Each language guide will provide:
- Language-specific lock types
- Timeout mechanisms
- Deadlock detection tools
- Code examples

---

**Deadlocks are a universal problem in concurrent systems. Prevention is better than detection. Lock ordering is the simplest and most effective strategy.**

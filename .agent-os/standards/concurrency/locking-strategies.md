# Locking Strategies - Universal Concurrency Patterns

**Timeless patterns for synchronizing access to shared resources.**

## What are Locking Strategies?

Locking strategies are systematic approaches to controlling concurrent access to shared resources, preventing race conditions and ensuring data consistency.

**Key principle:** Only one execution context should access shared mutable state at a time.

---

## Strategy 1: Mutex (Mutual Exclusion Lock)

**Definition:** Basic lock that allows only one execution context to hold it at a time.

**Concept:**
```
Context A:              Context B:
lock(mutex)            try to lock(mutex)
    ↓                      ↓
critical section       [BLOCKED - waiting]
    ↓                      ↓
unlock(mutex)          lock acquired!
                       critical section
```

### Characteristics
- **Mutual exclusion:** Only one holder at a time
- **Blocking:** Other contexts wait until unlocked
- **Simple:** Easy to understand and use

### Example

```
class BankAccount:
    def __init__(self):
        self.balance = 0
        self.lock = Mutex()
    
    def deposit(self, amount):
        self.lock.acquire()
        try:
            current = self.balance
            # Simulate processing time
            sleep(0.001)
            self.balance = current + amount
        finally:
            self.lock.release()
    
    def withdraw(self, amount):
        self.lock.acquire()
        try:
            if self.balance >= amount:
                current = self.balance
                sleep(0.001)
                self.balance = current - amount
                return True
            return False
        finally:
            self.lock.release()
```

**When to use:** Default choice for simple mutual exclusion.

---

## Strategy 2: Reentrant Lock (Recursive Lock)

**Definition:** Lock that can be acquired multiple times by the same execution context.

**Concept:**
```
Context A:
lock(reentrant_lock)     // Count = 1
    ↓
    call function_that_also_locks()
        ↓
        lock(reentrant_lock)  // Count = 2 (same context, allowed!)
            ↓
        unlock(reentrant_lock)  // Count = 1
    ↓
unlock(reentrant_lock)   // Count = 0 (fully released)
```

### Characteristics
- **Reentrant:** Same context can acquire multiple times
- **Count-based:** Tracks acquisition count
- **Prevents self-deadlock:** Avoids deadlock when calling nested functions

### Example

```
class ThreadSafeCache:
    def __init__(self):
        self.cache = {}
        self.lock = ReentrantLock()
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                return self.cache[key]
            
            # This calls set(), which also acquires the lock!
            # Would deadlock with regular mutex
            value = self.compute_value(key)
            self.set(key, value)  // Reentrant lock allows this
            return value
    
    def set(self, key, value):
        with self.lock:  // Can acquire again (same thread)
            self.cache[key] = value
```

**When to use:** Nested function calls that need same lock.

---

## Strategy 3: Read-Write Lock (RWLock)

**Definition:** Lock with two modes - multiple readers OR single writer.

**Concept:**
```
Read mode:
- Multiple readers can hold lock simultaneously
- No writers allowed

Write mode:
- Only one writer can hold lock
- No readers or other writers allowed
```

### Characteristics
- **Read concurrency:** Multiple readers don't block each other
- **Write exclusivity:** Writers block everyone
- **Performance:** Better for read-heavy workloads

### Example

```
class CachedDatabase:
    def __init__(self):
        self.cache = {}
        self.rwlock = ReadWriteLock()
    
    def read(self, key):
        with self.rwlock.read_lock():  // Multiple readers OK
            return self.cache.get(key)
    
    def write(self, key, value):
        with self.rwlock.write_lock():  // Exclusive access
            self.cache[key] = value
    
    def bulk_read(self, keys):
        with self.rwlock.read_lock():  // Concurrent with other reads
            return [self.cache.get(k) for k in keys]
```

**Performance:**
- Read-heavy (90% reads): 5-10x faster than mutex
- Write-heavy (90% writes): Similar to mutex
- Balanced (50/50): 2-3x faster than mutex

**When to use:** Read-heavy workloads (caches, configuration, shared state).

---

## Strategy 4: Spinlock

**Definition:** Lock that busy-waits (spins) instead of blocking.

**Concept:**
```
// Blocking lock (mutex)
while lock is held:
    context switches to another thread  // OS scheduler involvement

// Spinlock
while lock is held:
    check again  // Busy-wait, no context switch
    check again
    check again  // Burns CPU!
```

### Characteristics
- **No context switch:** Avoids OS scheduler overhead
- **Burns CPU:** Wastes CPU cycles while waiting
- **Fast for short waits:** Better than mutex if lock held briefly

### Example

```
class HighFrequencyCounter:
    def __init__(self):
        self.count = 0
        self.spinlock = Spinlock()
    
    def increment(self):
        self.spinlock.acquire()  // Spin if locked
        self.count += 1
        self.spinlock.release()
```

**When to use:**
- ✅ Lock held for very short time (<1 microsecond)
- ✅ High contention expected
- ✅ Real-time or low-latency requirements
- ❌ Don't use for long critical sections (wastes CPU)

**Typical use cases:** Kernel code, device drivers, high-frequency trading.

---

## Strategy 5: Semaphore

**Definition:** Lock with a count, allowing N simultaneous holders.

**Concept:**
```
Semaphore(count=3)  // Up to 3 holders

Context A: acquire()  // count = 2
Context B: acquire()  // count = 1
Context C: acquire()  // count = 0
Context D: acquire()  // [BLOCKED - count is 0]

Context A: release()  // count = 1
Context D: acquire()  // count = 0 (unblocked!)
```

### Characteristics
- **Counted:** Allows N simultaneous access
- **Resource pooling:** Limit concurrent access to limited resources
- **Flexible:** Can be binary (count=1, like mutex) or counting (count>1)

### Example

```
class ConnectionPool:
    def __init__(self, max_connections=10):
        self.connections = [create_connection() for _ in range(max_connections)]
        self.semaphore = Semaphore(max_connections)
    
    def execute_query(self, query):
        self.semaphore.acquire()  // Wait if all 10 connections in use
        try:
            connection = self.get_connection()
            result = connection.query(query)
            return result
        finally:
            self.semaphore.release()  // Free up slot
```

**When to use:** Resource pooling (database connections, thread pools, API rate limiting).

---

## Strategy 6: Lock-Free Algorithms (Compare-and-Swap)

**Definition:** Algorithms that use atomic operations instead of locks.

**Concept:**
```
// Lock-based increment
lock.acquire()
value = counter
counter = value + 1
lock.release()

// Lock-free increment (CAS)
loop:
    old_value = counter
    new_value = old_value + 1
    if compare_and_swap(counter, old_value, new_value):
        break  // Success!
    // Else: Another context modified it, try again
```

### Characteristics
- **No locks:** Uses atomic CPU instructions
- **Non-blocking:** Always makes progress (no deadlocks)
- **Complex:** Hard to implement correctly
- **Performance:** Better under high contention

### Example

```
class LockFreeStack:
    def __init__(self):
        self.head = None
    
    def push(self, value):
        node = Node(value)
        loop:
            old_head = atomic_read(self.head)
            node.next = old_head
            if atomic_compare_and_swap(self.head, old_head, node):
                return  // Success!
            // Else: Retry with new head value
    
    def pop(self):
        loop:
            old_head = atomic_read(self.head)
            if old_head is None:
                return None
            new_head = old_head.next
            if atomic_compare_and_swap(self.head, old_head, new_head):
                return old_head.value  // Success!
            // Else: Retry
```

**When to use:**
- ✅ High contention scenarios
- ✅ Simple data structures (stack, queue, counter)
- ❌ Avoid for complex logic (hard to get right)

---

## Comparison Matrix

| Strategy | Concurrent Readers | Concurrent Writers | Complexity | Performance | Use Case |
|----------|-------------------|-------------------|------------|-------------|----------|
| **Mutex** | ❌ (1 at a time) | ❌ (1 at a time) | Low | Good | General purpose |
| **Reentrant Lock** | ❌ | ❌ | Low | Good | Nested calls |
| **Read-Write Lock** | ✅ (unlimited) | ❌ (1 at a time) | Medium | Excellent (read-heavy) | Caches, config |
| **Spinlock** | ❌ | ❌ | Low | Excellent (short waits) | Kernel, real-time |
| **Semaphore** | ✅ (limited) | ✅ (limited) | Medium | Good | Resource pools |
| **Lock-Free** | ✅ | ✅ | Very High | Excellent (high contention) | Counters, queues |

---

## Choosing the Right Strategy

### Decision Tree

```
Need to protect shared state?
    ↓
Is it read-heavy (>80% reads)?
    YES → Read-Write Lock
    NO ↓
    
Will nested functions use same lock?
    YES → Reentrant Lock
    NO ↓
    
Need to limit concurrent access (e.g., pool)?
    YES → Semaphore
    NO ↓
    
Is critical section very short (<1μs)?
    YES → Spinlock (if kernel/real-time)
    NO ↓
    
High contention + simple operation?
    YES → Lock-Free (if you can implement it correctly)
    NO ↓
    
Default → Mutex
```

---

## Advanced Patterns

### Pattern 1: Lock Ordering (Prevent Deadlocks)

```
// Always acquire locks in same order
LOCK_ORDER = [lock_A, lock_B, lock_C]

def transfer(from_account, to_account, amount):
    locks = sorted([from_account.lock, to_account.lock], key=id)
    
    with locks[0]:
        with locks[1]:
            from_account.balance -= amount
            to_account.balance += amount
```

### Pattern 2: Try-Lock with Timeout

```
def safe_operation():
    if lock.try_acquire(timeout=5_seconds):
        try:
            # Critical section
            pass
        finally:
            lock.release()
    else:
        # Couldn't acquire lock, handle gracefully
        return fallback_result
```

### Pattern 3: Lock Granularity

```
// Fine-grained locking (better concurrency)
class ShardedCache:
    def __init__(self, num_shards=16):
        self.shards = [
            {"data": {}, "lock": Mutex()}
            for _ in range(num_shards)
        ]
    
    def get(self, key):
        shard = self.shards[hash(key) % len(self.shards)]
        with shard["lock"]:  // Only locks one shard
            return shard["data"].get(key)
```

---

## Anti-Patterns

### Anti-Pattern 1: Holding Lock Too Long
❌ Performing I/O or heavy computation while holding lock.

```
// BAD
with lock:
    data = database.query()  // Network I/O!
    process(data)            // Heavy computation!
```

**Fix:** Minimize critical section.
```
// GOOD
data = database.query()  // No lock needed
processed = process(data)  // No lock needed
with lock:
    self.cache = processed  // Only lock for write
```

### Anti-Pattern 2: Nested Locks Without Order
❌ Acquiring locks in different orders (deadlock risk).

### Anti-Pattern 3: Using Mutex for Read-Heavy Workload
❌ Blocking all readers when they could read concurrently.

**Fix:** Use Read-Write Lock instead.

---

## Performance Guidelines

### Lock Acquisition Cost

| Strategy | Overhead | When Fast | When Slow |
|----------|----------|-----------|-----------|
| Mutex | ~20-100ns | Uncontended | High contention |
| Reentrant Lock | ~30-150ns | Uncontended | High contention + reacquisition |
| RWLock (read) | ~30-100ns | Uncontended | Write-heavy |
| RWLock (write) | ~50-200ns | Uncontended | Many readers |
| Spinlock | ~10-50ns | Short wait | Long wait (wastes CPU) |
| Semaphore | ~50-150ns | Available | All permits taken |
| Lock-Free (CAS) | ~10-50ns | Low contention | High contention (many retries) |

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-concurrency.md` (Python: `threading.Lock`, `RLock`, `Semaphore`)
- See `.agent-os/standards/development/go-concurrency.md` (Go: `sync.Mutex`, `sync.RWMutex`, channels)
- See `.agent-os/standards/development/rust-concurrency.md` (Rust: `Mutex<T>`, `RwLock<T>`, `Arc<T>`)
- See `.agent-os/standards/development/java-concurrency.md` (Java: `synchronized`, `ReentrantLock`, `ReadWriteLock`)
- Etc.

---

**Locking is fundamental to concurrent programming. Choose the right strategy for your use case: Mutex for general purpose, RWLock for read-heavy, Semaphore for resource pools, and Lock-Free for high contention simple operations.**

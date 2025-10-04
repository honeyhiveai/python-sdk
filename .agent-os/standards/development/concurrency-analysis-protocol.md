# Concurrency Analysis Protocol
**Systematic approach to analyzing and handling concurrent access patterns**

**Date**: October 4, 2025  
**Status**: Active  
**Scope**: All code touching shared state

---

## 🎯 Purpose

This protocol provides a systematic approach for AI assistants to analyze and handle concurrency correctly when writing code that accesses shared state.

**Key Insight**: AI can evaluate 100+ concurrent scenarios instantly. There is NO excuse for race conditions.

---

## 📋 Step 1: Identify Shared State

**Question**: What state is accessed by this code?

**Shared state types:**

### **Class-Level (Shared Across Instances)**
```python
class Counter:
    total = 0  # ⚠️ SHARED - all instances see this
    
    def __init__(self):
        self.count = 0  # ✅ NOT SHARED - per-instance
```

### **Module-Level (Shared Across Imports)**
```python
# config.py
_connection_pool = {}  # ⚠️ SHARED - all imports see this
```

### **File System (Shared Across Processes)**
```python
with open("data.txt", "w") as f:  # ⚠️ SHARED - other processes can access
    f.write(data)
```

### **External Systems (Shared Across Everything)**
```python
db.execute("UPDATE users SET ...")  # ⚠️ SHARED - database state
cache.set("key", value)              # ⚠️ SHARED - cache state
vector_store.search(query)           # ⚠️ SHARED - index state
```

**If ANY shared state identified → Continue to Step 2**  
**If NO shared state → Concurrency analysis complete (thread-safe by design)**

---

## 📋 Step 2: Research Library Thread-Safety

**NEVER assume a library is thread-safe. ALWAYS research.**

### **Research Checklist:**

1. **Read official documentation**
   - Search for: "thread-safe", "concurrent", "multithread"
   - Look for: Concurrency section, Thread Safety section

2. **Check GitHub issues**
   - Search issues for: "race condition", "thread", "concurrent"
   - Recent issues about corruption or data loss?

3. **Examine examples**
   - Do official examples use locks?
   - Do they warn about concurrency?

4. **Test if uncertain**
   - Write concurrent access test
   - Run with multiple threads
   - Check for errors or corruption

### **Common Library Patterns:**

**Thread-Safe Internally (No External Lock Needed):**
```python
# Examples:
import queue
import threading
from collections.abc import deque  # (with maxlen)

# These handle locking internally
q = queue.Queue()
q.put(item)  # Thread-safe
```

**NOT Thread-Safe (External Lock Required):**
```python
# Examples:
import sqlite3
import lancedb
from sentence_transformers import SentenceTransformer

# These require external locking
db = lancedb.connect("path")
table = db.open_table("name")
table.search(query)  # NOT thread-safe for concurrent read+write
```

**Partially Thread-Safe (Read the Docs!):**
```python
# Examples:
import redis
import boto3

# redis: Thread-safe for connections from connection pool
# boto3: Thread-safe at resource level, not client level
# ALWAYS verify specifics in documentation
```

---

## 📋 Step 3: Choose Locking Strategy

### **Strategy 1: No Shared State (Best)**
Redesign to avoid shared state entirely.

```python
# Bad: Shared state
class APIClient:
    _cache = {}  # Shared across all instances!
    
    def get(self, key):
        if key in self._cache:
            return self._cache[key]

# Good: No shared state
class APIClient:
    def __init__(self):
        self._cache = {}  # Per-instance, no sharing
    
    def get(self, key):
        if key in self._cache:
            return self._cache[key]
```

### **Strategy 2: Read-Only Shared State (Safe)**
If shared state is never modified, no locking needed.

```python
# Safe: Read-only after initialization
class Config:
    SETTINGS = {
        "timeout": 30,
        "retries": 3
    }  # Never modified → thread-safe
```

### **Strategy 3: Simple Lock (Mutual Exclusion)**
Use `threading.Lock()` when only one thread should access at a time.

```python
import threading

class Cache:
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()
    
    def get(self, key):
        with self._lock:  # Only one thread in this block
            return self._data.get(key)
    
    def set(self, key, value):
        with self._lock:  # Only one thread in this block
            self._data[key] = value
```

**When to use:** Simple shared state with short critical sections.

### **Strategy 4: Reentrant Lock (Nested Calls)**
Use `threading.RLock()` when lock may be acquired multiple times by same thread.

```python
import threading

class RAGEngine:
    def __init__(self):
        self._lock = threading.RLock()  # Reentrant!
    
    def search(self, query):
        with self._lock:
            result = self._vector_search(query)
            self._cache_result(result)  # May also acquire lock!
            return result
    
    def _cache_result(self, result):
        with self._lock:  # Same thread can reacquire
            self._cache[key] = result
```

**When to use:** Methods call each other and both need the lock.

### **Strategy 5: Read-Write Lock (Multiple Readers)**
Allow multiple concurrent readers, but exclusive writer.

```python
import threading

class RAGEngine:
    def __init__(self):
        self._lock = threading.RLock()
        self._rebuilding = threading.Event()
    
    def search(self, query):
        # Wait if rebuild in progress
        if self._rebuilding.is_set():
            self._rebuilding.wait(timeout=30)
        
        with self._lock:  # Read lock (multiple threads can hold)
            return self._vector_search(query)
    
    def reload_index(self):
        with self._lock:  # Write lock (exclusive, blocks all reads)
            self._rebuilding.set()
            try:
                # Rebuild logic
                self._rebuild()
            finally:
                self._rebuilding.clear()
```

**When to use:** Frequent reads, infrequent writes (like hot reload).

### **Strategy 6: Lock-Free Data Structures**
Use built-in thread-safe structures.

```python
import queue
from collections import deque

# Thread-safe queue
q = queue.Queue()
q.put(item)      # Thread-safe
item = q.get()   # Thread-safe

# Atomic append (GIL protection)
items = []
items.append(x)  # Atomic due to GIL
# But NOT thread-safe: items = items + [x]  (creates new list)
```

**When to use:** Queue/stack patterns with producer-consumer.

---

## 📋 Step 4: Identify Critical Sections

**Critical section**: Code that MUST NOT be interrupted by another thread.

### **Example Analysis:**

```python
class Cache:
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()
    
    def get_or_compute(self, key, compute_fn):
        # CRITICAL SECTION START
        with self._lock:
            if key in self._data:        # Read shared state
                return self._data[key]   # Return cached value
            
            # Compute is expensive, should we release lock?
            # Answer: Depends on compute_fn duration
            
            value = compute_fn()         # Compute new value
            self._data[key] = value      # Write shared state
            return value
        # CRITICAL SECTION END
```

**Optimization (if compute is slow):**
```python
def get_or_compute(self, key, compute_fn):
    # Fast path: Check cache with lock
    with self._lock:
        if key in self._data:
            return self._data[key]
    
    # Slow path: Compute without lock (multiple threads may compute same key)
    value = compute_fn()
    
    # Store result with lock
    with self._lock:
        self._data[key] = value
    
    return value
```

**Rule**: Keep critical sections as SHORT as possible. Long operations (I/O, computation) should happen outside locks when safe.

---

## 📋 Step 5: Write Concurrent Access Tests

**MANDATORY**: Every concurrent code path must have a test validating safety.

### **Test Template:**

```python
import threading
import time

def test_concurrent_access():
    """Test that concurrent access doesn't cause race conditions."""
    shared_object = MyClass()
    errors = []
    
    def worker(worker_id, iterations):
        """Worker thread performing operations."""
        try:
            for i in range(iterations):
                result = shared_object.operation()
                # Validate result integrity
                assert result is not None
        except Exception as e:
            errors.append(f"Worker {worker_id}: {e}")
    
    # Launch multiple worker threads
    threads = []
    for i in range(10):  # 10 concurrent workers
        t = threading.Thread(target=worker, args=(i, 100))
        t.start()
        threads.append(t)
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    # Assert no errors
    assert len(errors) == 0, f"Concurrent access errors: {errors}"
    
    # Validate final state integrity
    assert shared_object.is_consistent()
```

### **Real-World Example (From Agent OS MCP Fix):**

```python
# .agent-os/scripts/test_concurrent_access.py
def query_worker(engine, worker_id, duration):
    """Continuously query the RAG engine."""
    query_count = 0
    error_count = 0
    
    while time.time() - start_time < duration:
        try:
            result = engine.search("query", n_results=3)
            query_count += 1
        except Exception as e:
            error_count += 1
            print(f"Worker {worker_id} ERROR: {e}")
    
    return query_count, error_count

def reload_worker(engine, reload_count, delay):
    """Trigger index reloads."""
    for i in range(reload_count):
        time.sleep(delay)
        engine.reload_index()

# Test: 3 query workers + 3 reloads = should have 0 errors
```

**Result: 268 queries + 3 reloads = 0 errors = Thread-safe ✅**

---

## 📋 Step 6: Document Concurrency Guarantees

**Every concurrent code path must document:**

1. **What's protected**: What shared state exists
2. **How it's protected**: Lock type and strategy
3. **Why it's safe**: Brief reasoning
4. **How it's tested**: Test name or validation approach

### **Documentation Template:**

```python
class RAGEngine:
    """
    Semantic search engine with thread-safe concurrent access.
    
    **Concurrency Guarantees:**
    - Shared state: LanceDB table, query cache
    - Protection: threading.RLock for read operations, Event for rebuild signaling
    - Safety: Write lock blocks all reads during reload, reads wait for rebuild completion
    - Validation: test_concurrent_access.py - 268 queries + 3 reloads = 0 errors
    
    **Thread Safety:**
    - search(): Safe for concurrent calls (shared read lock)
    - reload_index(): Safe for concurrent calls (exclusive write lock)
    - Multiple searches during reload: Queries wait gracefully (30s timeout)
    """
    
    def __init__(self):
        self._lock = threading.RLock()        # Protects index access
        self._rebuilding = threading.Event()  # Signals rebuild state
```

---

## 🚨 Common Concurrency Mistakes (To Avoid)

### **1. Assuming Python's GIL Protects You**
```python
# Bad: Assumes GIL makes this safe (IT DOESN'T)
self.counter += 1  # NOT atomic! (read, add, write = 3 operations)

# Good: Use lock
with self._lock:
    self.counter += 1
```

### **2. Locking at Wrong Granularity**
```python
# Bad: Lock too coarse (blocks everything)
def process_batch(self, items):
    with self._lock:  # Lock held for entire batch!
        for item in items:
            self.slow_operation(item)  # Minutes of blocking!

# Good: Lock only critical sections
def process_batch(self, items):
    for item in items:
        result = self.slow_operation(item)  # No lock needed
        with self._lock:  # Lock only for shared state update
            self._results.append(result)
```

### **3. Deadlock from Lock Ordering**
```python
# Bad: Inconsistent lock ordering
def transfer(from_account, to_account, amount):
    with from_account.lock:
        with to_account.lock:  # Deadlock if another thread locks in reverse order!
            from_account.balance -= amount
            to_account.balance += amount

# Good: Consistent lock ordering (by ID)
def transfer(from_account, to_account, amount):
    first, second = sorted([from_account, to_account], key=lambda a: a.id)
    with first.lock:
        with second.lock:  # Always lock in same order
            from_account.balance -= amount
            to_account.balance += amount
```

### **4. Forgetting to Release Lock**
```python
# Bad: Lock not released on exception
def update(self, key, value):
    self._lock.acquire()
    if not self.validate(value):
        raise ValueError("Invalid")  # Lock never released!
    self._data[key] = value
    self._lock.release()

# Good: Use context manager (automatic release)
def update(self, key, value):
    with self._lock:  # Released even on exception
        if not self.validate(value):
            raise ValueError("Invalid")
        self._data[key] = value
```

---

## ✅ Checklist Summary

**Before writing concurrent code:**

- [ ] Identified all shared state
- [ ] Researched library thread-safety (not assumed!)
- [ ] Chosen appropriate locking strategy
- [ ] Identified critical sections (kept minimal)
- [ ] Written concurrent access test
- [ ] Documented concurrency guarantees
- [ ] Avoided common mistakes (GIL assumption, wrong granularity, deadlocks)

**If all checked → Code is thread-safe**  
**If any unchecked → DO NOT COMMIT**

---

## 📚 Related Standards

- **[Production Code Universal Checklist](production-code-universal-checklist.md)** - Tier 1 and Tier 2 requirements
- **[Failure Mode Analysis Template](failure-mode-analysis-template.md)** - How concurrent failures happen

**Remember: AI can evaluate 100+ scenarios instantly. There is NO excuse for race conditions.**

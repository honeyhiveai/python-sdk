# Shared State Analysis - Universal Concurrency Practice

**Timeless approach to identifying and managing shared state in concurrent systems.**

**Keywords for search**: shared state, shared mutable state, concurrent access, thread safety, state classification, local state, immutable state, shared state analysis, concurrency bugs, data flow analysis, escape analysis

---

## 🚨 Quick Reference (TL;DR)

**Core Principle:** Shared mutable state is the root of most concurrency bugs.

**Three Categories of State:**
1. **Local State** (Safe) - Owned by single context, never shared
2. **Shared Immutable State** (Safe) - Shared but read-only
3. **Shared Mutable State** (DANGER!) - Shared AND can be modified

**Three Key Questions:**
1. **Is it shared?** Can multiple contexts access it?
2. **Is it mutable?** Can it be modified after creation?
3. **Is access synchronized?** Is there proper synchronization?

**Four Refactoring Strategies:**
1. **Eliminate Sharing** - Make state local
2. **Make Immutable** - Copy-on-write, frozen data structures
3. **Add Synchronization** - Locks, atomics, channels
4. **Use Message Passing** - No shared state, communicate via messages

**Common Patterns:**
- **Read-Heavy State** → Read-write lock or immutable copy-on-write
- **Accumulator (Counter)** → Atomic operations or thread-local aggregation
- **Lazy Initialization** → Double-checked locking or Once/Call-Once
- **Producer-Consumer** → Thread-safe queue

**Analysis Techniques:**
- Data flow analysis (where created, modified, accessed)
- Happens-before analysis (guaranteed ordering)
- Escape analysis (does local data become shared)

---

## Questions This Answers

- "What is shared state?"
- "How to identify shared state in my code?"
- "What's the difference between local, shared immutable, and shared mutable state?"
- "How to analyze if state is thread-safe?"
- "What patterns indicate shared mutable state?"
- "How to refactor to eliminate shared state?"
- "When to use locks vs immutability vs message passing?"
- "What is escape analysis?"
- "How to test for shared state issues?"
- "What is happens-before analysis?"
- "How to identify race conditions from shared state?"
- "What are best practices for managing shared state?"

---

## What is Shared State?

Shared state is data that can be accessed or modified by multiple execution contexts (threads, processes, goroutines, async tasks) concurrently.

**Key principle:** Shared mutable state is the root of most concurrency bugs.

---

## How to Classify State? (Three Categories)

```
State Classification:
    ├── Local State (Safe)
    ├── Shared Immutable State (Safe)
    └── Shared Mutable State (DANGER!)
```

### 1. Local State (Safe)

**Definition:** Data owned by single execution context, never shared.

```
def process_data(input):
    // Local variables - safe
    result = 0
    temp = input * 2
    items = []
    
    for i in range(temp):
        items.append(i)  // Local list, no sharing
    
    return sum(items)
```

**Characteristics:**
- ✅ No synchronization needed
- ✅ No race conditions possible
- ✅ Fast (no locking overhead)

**Guideline:** Prefer local state whenever possible.

---

### 2. Shared Immutable State (Safe)

**Definition:** Data shared across contexts but never modified.

```
// Configuration loaded at startup
CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "api_url": "https://api.example.com"
}

def make_request():
    // Reading shared config - safe (immutable)
    timeout = CONFIG["timeout"]
    url = CONFIG["api_url"]
    return http.get(url, timeout=timeout)
```

**Characteristics:**
- ✅ No synchronization needed
- ✅ No race conditions (read-only)
- ✅ Fast (no locking)

**Guideline:** Make shared data immutable when possible.

---

### 3. Shared Mutable State (DANGER!)

**Definition:** Data shared across contexts AND can be modified.

```
// Global counter - SHARED MUTABLE STATE
counter = 0

def increment():
    global counter
    counter += 1  // RACE CONDITION!
```

**Characteristics:**
- ❌ Requires synchronization
- ❌ Race conditions likely
- ❌ Slower (locking overhead)
- ❌ Complex reasoning

**Guideline:** Minimize shared mutable state. Synchronize when unavoidable.

---

## How to Identify Shared State?

### Question 1: Is it Shared?

**Ask:** Can multiple execution contexts access this data?

```
// NOT shared (local variable)
def process():
    local_var = 0
    return local_var

// SHARED (class attribute)
class Service:
    shared_counter = 0  // All instances share this!

// SHARED (global variable)
global_cache = {}

// SHARED (instance variable accessed by multiple threads)
class ThreadSafeService:
    def __init__(self):
        self.cache = {}  // Shared if multiple threads call methods
```

---

### Question 2: Is it Mutable?

**Ask:** Can this data be modified after creation?

```
// Immutable (safe to share)
CONFIG = ("production", 443, True)  // Tuple - immutable
API_KEY = "secret123"                // String - immutable

// Mutable (dangerous to share)
users = []            // List - mutable
cache = {}            // Dict - mutable
counter = 0           // Integer - mutable (via reassignment)
```

---

### Question 3: Is Access Synchronized?

**Ask:** Is there proper synchronization protecting this shared mutable state?

```
// UNSAFE (no synchronization)
class UnsafeCounter:
    def __init__(self):
        self.count = 0  // Shared mutable
    
    def increment(self):
        self.count += 1  // Race condition!

// SAFE (synchronized)
class SafeCounter:
    def __init__(self):
        self.count = 0
        self.lock = Lock()
    
    def increment(self):
        with self.lock:
            self.count += 1  // Protected
```

---

## What Common Shared State Patterns Exist?

### Pattern 1: Read-Heavy Shared State

**Scenario:** Data read frequently, written rarely.

**Problem:**
```
// Lock on every read is expensive
cache = {}
lock = Lock()

def get(key):
    with lock:  // Blocks all readers!
        return cache.get(key)

def set(key, value):
    with lock:
        cache[key] = value
```

**Solution 1: Read-Write Lock**
```
cache = {}
rwlock = ReadWriteLock()

def get(key):
    with rwlock.read_lock():  // Multiple readers OK
        return cache.get(key)

def set(key, value):
    with rwlock.write_lock():  // Exclusive write
        cache[key] = value
```

**Solution 2: Immutable Copy-on-Write**
```
cache = ImmutableDict()

def get(key):
    return cache.get(key)  // No lock needed!

def set(key, value):
    with lock:
        // Create new immutable dict with updated value
        cache = cache.set(key, value)
```

---

### Pattern 2: Accumulator (Shared Counter)

**Scenario:** Multiple contexts incrementing a counter.

**Problem:**
```
total_requests = 0

def handle_request():
    global total_requests
    total_requests += 1  // Race condition!
```

**Solution 1: Lock**
```
total_requests = 0
lock = Lock()

def handle_request():
    global total_requests
    with lock:
        total_requests += 1
```

**Solution 2: Atomic Operations**
```
total_requests = AtomicInteger(0)

def handle_request():
    total_requests.increment()  // Atomic, no lock needed
```

**Solution 3: Thread-Local Aggregation**
```
thread_local_counts = ThreadLocal(initial=0)

def handle_request():
    thread_local_counts.value += 1  // No sharing, no lock

def get_total():
    return sum(thread_local_counts.all_values())
```

---

### Pattern 3: Lazy Initialization

**Scenario:** Initialize expensive resource on first use.

**Problem:**
```
database_connection = None

def get_connection():
    global database_connection
    if database_connection is None:  // Race condition!
        database_connection = create_connection()
    return database_connection
```

**Solution 1: Double-Checked Locking**
```
database_connection = None
lock = Lock()

def get_connection():
    global database_connection
    if database_connection is None:  // Fast path (no lock)
        with lock:
            if database_connection is None:  // Recheck inside lock
                database_connection = create_connection()
    return database_connection
```

**Solution 2: Once/Call-Once**
```
database_connection = None
once = Once()

def get_connection():
    global database_connection
    once.do(lambda: initialize_connection())
    return database_connection

def initialize_connection():
    global database_connection
    database_connection = create_connection()
```

---

### Pattern 4: Producer-Consumer Queue

**Scenario:** One context produces data, another consumes.

**Problem:**
```
queue = []  // Shared mutable list

def producer():
    while True:
        item = produce()
        queue.append(item)  // Race condition!

def consumer():
    while True:
        if len(queue) > 0:  // Race condition!
            item = queue.pop(0)
            process(item)
```

**Solution: Thread-Safe Queue**
```
queue = ThreadSafeQueue()

def producer():
    while True:
        item = produce()
        queue.put(item)  // Thread-safe

def consumer():
    while True:
        item = queue.get()  // Blocks if empty, thread-safe
        process(item)
```

---

## What Analysis Techniques Should I Use?

### Technique 1: Data Flow Analysis

**Ask:** Where is data created? Where is it modified? Who accesses it?

```
// Trace data flow
user_data = fetch_from_database()  // Created (local)
    ↓
cache[user_id] = user_data         // Stored in shared cache (SHARED)
    ↓
def other_thread():
    data = cache[user_id]          // Accessed from shared cache (SHARED)
    data.update({"status": "active"})  // MUTATION! (DANGER)
```

**Finding:** `user_data` becomes shared when stored in cache. Mutation creates race condition.

---

### Technique 2: Happens-Before Analysis

**Ask:** Is there a guaranteed ordering between operations?

```
Thread A:                 Thread B:
x = 1                     print(x)
    ↓                         ↓
    ?                         ?

Question: What does Thread B print?
Answer: UNDEFINED! (race condition)

With synchronization:
Thread A:                 Thread B:
x = 1                     lock.acquire()
lock.release()            print(x)  // Guaranteed to see x = 1
    ↓                     lock.release()
happens-before
```

**Happens-Before Rules:**
1. Sequential execution within a thread
2. Lock release happens-before lock acquire (by another thread)
3. Thread creation happens-before thread execution
4. Write to volatile/atomic happens-before read

---

### Technique 3: Escape Analysis

**Ask:** Does this local data escape the current context?

```
// No escape - safe
def process():
    data = [1, 2, 3]
    return sum(data)  // data never escapes

// Escapes via return - check if receiver shares it
def process():
    data = [1, 2, 3]
    return data  // Caller might share this!

// Escapes via global - SHARED
global_list = []

def process():
    data = [1, 2, 3]
    global_list.append(data)  // Escaped! Now shared

// Escapes via callback - check if callback shares it
def process(callback):
    data = [1, 2, 3]
    callback(data)  // Callback might share this!
```

---

## How to Refactor Shared State?

### Strategy 1: Eliminate Sharing

**Before:**
```
class UserService:
    def __init__(self):
        self.temp_users = []  // Shared mutable
    
    def process_batch(self, users):
        self.temp_users = users  // Multiple threads might call this!
        for user in self.temp_users:
            self.save(user)
```

**After:**
```
class UserService:
    def process_batch(self, users):
        temp_users = list(users)  // Local copy
        for user in temp_users:
            self.save(user)
```

---

### Strategy 2: Make Immutable

**Before:**
```
class Config:
    def __init__(self):
        self.settings = {}  // Shared mutable
    
    def update(self, key, value):
        self.settings[key] = value  // Race condition!
```

**After:**
```
class Config:
    def __init__(self, settings):
        self._settings = frozendict(settings)  // Immutable
    
    def with_update(self, key, value):
        new_settings = dict(self._settings)
        new_settings[key] = value
        return Config(new_settings)  // Return new instance
```

---

### Strategy 3: Add Synchronization

**Before:**
```
class Cache:
    def __init__(self):
        self.data = {}  // Shared mutable, no lock
    
    def get(self, key):
        return self.data.get(key)  // Race condition!
    
    def set(self, key, value):
        self.data[key] = value  // Race condition!
```

**After:**
```
class Cache:
    def __init__(self):
        self.data = {}
        self.lock = Lock()
    
    def get(self, key):
        with self.lock:
            return self.data.get(key)
    
    def set(self, key, value):
        with self.lock:
            self.data[key] = value
```

---

### Strategy 4: Use Message Passing

**Before (Shared State):**
```
class Counter:
    def __init__(self):
        self.count = 0
        self.lock = Lock()
    
    def increment(self):
        with self.lock:
            self.count += 1
```

**After (Message Passing):**
```
class Counter:
    def __init__(self):
        self.count = 0
        self.queue = Queue()
        self.start_worker()
    
    def start_worker(self):
        def worker():
            while True:
                msg = self.queue.get()
                if msg == "increment":
                    self.count += 1
        
        thread = Thread(target=worker)
        thread.start()
    
    def increment(self):
        self.queue.put("increment")  // Send message, no shared state!
```

---

## How to Test for Shared State Issues?

### Test 1: Stress Test

```
def test_concurrent_increment():
    counter = Counter()
    threads = []
    
    def increment_many():
        for _ in range(1000):
            counter.increment()
    
    // Start 10 threads
    for _ in range(10):
        t = Thread(target=increment_many)
        threads.append(t)
        t.start()
    
    // Wait for all
    for t in threads:
        t.join()
    
    // Should be 10,000
    assert counter.value == 10_000  // Fails if race condition!
```

### Test 2: Thread Sanitizer

```
// Compile with thread sanitizer
// gcc -fsanitize=thread program.c

// Run program
// ./program

// Thread sanitizer will detect:
// - Data races
// - Use of uninitialized memory
// - Lock order violations
```

---

## What Are Shared State Best Practices?

### 1. Minimize Shared State
- Prefer local variables
- Pass data as function arguments
- Return new data instead of mutating

### 2. Make Shared Data Immutable
- Use immutable data structures
- Copy-on-write for updates
- Freeze/finalize after initialization

### 3. Synchronize Access
- Identify all shared mutable state
- Protect with locks, atomics, or channels
- Document synchronization requirements

### 4. Use Higher-Level Abstractions
- Thread-safe queues
- Concurrent collections
- Actor model / message passing

### 5. Test Concurrency
- Stress tests with many threads
- Thread sanitizer tools
- Property-based testing

---

## What Should I Check in Code Review?

When reviewing code for shared state issues:

- [ ] Identify all shared data (global, class attributes, closures)
- [ ] Check if shared data is mutable
- [ ] Verify proper synchronization for shared mutable data
- [ ] Look for data races (multiple threads, no happens-before)
- [ ] Check for missing locks or wrong lock granularity
- [ ] Verify lock ordering to prevent deadlocks
- [ ] Ensure thread-safe use of collections (lists, dicts, sets)
- [ ] Check for escaped local data becoming shared
- [ ] Review lazy initialization for race conditions
- [ ] Test with thread sanitizer or equivalent tool

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-concurrency.md` (Python: threading, global state, GIL)
- See `.praxis-os/standards/development/go-concurrency.md` (Go: goroutines, channels, sync package)
- See `.praxis-os/standards/development/rust-concurrency.md` (Rust: ownership, Send/Sync traits)
- See `.praxis-os/standards/development/java-concurrency.md` (Java: synchronized, volatile, concurrent collections)
- Etc.

---

## When to Query This Standard

This standard is most valuable when:

1. **Starting Concurrent Code Design**
   - Situation: Planning multi-threaded architecture
   - Query: `pos_search_project(content_type="standards", query="how to identify shared state")`

2. **Code Review for Concurrency**
   - Situation: Reviewing code that uses threads/async
   - Query: `pos_search_project(content_type="standards", query="shared state analysis checklist")`

3. **Debugging Concurrency Bugs**
   - Situation: Intermittent failures, race conditions suspected
   - Query: `pos_search_project(content_type="standards", query="shared mutable state patterns")`

4. **Refactoring to Improve Thread Safety**
   - Situation: Have shared state, want to eliminate or protect it
   - Query: `pos_search_project(content_type="standards", query="how to refactor shared state")`

5. **Choosing Synchronization Approach**
   - Situation: Deciding between locks, immutability, message passing
   - Query: `pos_search_project(content_type="standards", query="shared state refactoring strategies")`

6. **Understanding Concurrency Failures**
   - Situation: "Why is my concurrent code breaking?"
   - Query: `pos_search_project(content_type="standards", query="shared mutable state root cause")`

### Query by Use Case

| Use Case | Example Query |
|----------|---------------|
| Identify shared state | `pos_search_project(content_type="standards", query="how to identify shared state")` |
| Classify state safety | `pos_search_project(content_type="standards", query="local vs shared state")` |
| Refactor away sharing | `pos_search_project(content_type="standards", query="eliminate shared state")` |
| Add synchronization | `pos_search_project(content_type="standards", query="synchronize shared state")` |
| Test concurrency | `pos_search_project(content_type="standards", query="test shared state issues")` |
| Code review checklist | `pos_search_project(content_type="standards", query="shared state code review")` |

---

## Cross-References and Related Standards

**Concurrency Standards:**
- `standards/concurrency/race-conditions.md` - Race conditions from unsynchronized shared state
  → `pos_search_project(content_type="standards", query="race condition prevention")`
- `standards/concurrency/deadlocks.md` - Deadlocks from improper lock ordering
  → `pos_search_project(content_type="standards", query="deadlock prevention")`
- `standards/concurrency/locking-strategies.md` - Choosing locks to protect shared state
  → `pos_search_project(content_type="standards", query="locking strategies")`

**Testing Standards:**
- `standards/testing/integration-testing.md` - Testing concurrent code with shared state
  → `pos_search_project(content_type="standards", query="integration testing concurrency")`

**Query workflow for managing shared state:**
1. **Identify**: `pos_search_project(content_type="standards", query="how to identify shared state")` → Find all shared data
2. **Classify**: Determine if local, shared immutable, or shared mutable
3. **Analyze**: `pos_search_project(content_type="standards", query="escape analysis")` → Check if local data escapes
4. **Choose Strategy**: `pos_search_project(content_type="standards", query="how to refactor shared state")` → Eliminate, immutabilize, or synchronize
5. **Implement**: Apply chosen strategy (locks, atomics, immutable structures)
6. **Test**: `pos_search_project(content_type="standards", query="test shared state issues")` → Stress test with concurrency
7. **Review**: `pos_search_project(content_type="standards", query="shared state code review")` → Validate with checklist

---

**Shared mutable state is the enemy of concurrent programming. Minimize it. Make it immutable when possible. Synchronize it carefully when unavoidable. Test thoroughly. Your future self will thank you.**

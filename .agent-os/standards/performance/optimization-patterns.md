# Performance Optimization Patterns - Universal Performance Practice

**Timeless patterns for writing efficient code without premature optimization.**

## Core Principle

**"Make it work, make it right, make it fast - in that order."**

- **Make it work:** Correct functionality first
- **Make it right:** Clean, maintainable code
- **Make it fast:** Optimize after measuring

**Key principle:** Measure before optimizing. Don't guess.

---

## The Performance Optimization Process

### Step 1: Measure (MANDATORY)

**Before ANY optimization:**

```
1. Profile the code
2. Identify the bottleneck
3. Measure current performance
4. Set performance target
5. Optimize the bottleneck
6. Measure again
7. Verify improvement
```

**Without measurement:** You're guessing, not optimizing.

---

### Step 2: Identify the Bottleneck

**The 80/20 Rule:** 80% of time is spent in 20% of code.

**Tools for profiling (language-specific):**
- **CPU profiling:** Find hot loops, expensive functions
- **Memory profiling:** Find allocations, memory leaks
- **I/O profiling:** Find slow database queries, network calls

**Look for:**
- Functions with high cumulative time
- Functions called many times (even if individually fast)
- Memory allocations in hot paths
- Blocking I/O operations

---

### Step 3: Optimize

**Only optimize the measured bottleneck.**

Don't optimize code that takes <1% of total runtime.

---

## Universal Optimization Patterns

### Pattern 1: Reduce Algorithmic Complexity

**Problem:** Using wrong algorithm for the job.

```
// ❌ BAD: O(n²) - nested loops
function find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

// ✅ GOOD: O(n) - using set
function find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

**Improvement:** O(n²) → O(n)  
**Speedup:** 100x for 1000 items, 10,000x for 10,000 items

---

### Pattern 2: Cache Expensive Computations

**Problem:** Recomputing same result multiple times.

```
// ❌ BAD: Recomputes every time
function fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  // Exponential time!

// ✅ GOOD: Memoization
cache = {}
function fibonacci(n):
    if n in cache:
        return cache[n]
    if n <= 1:
        return n
    result = fibonacci(n-1) + fibonacci(n-2)
    cache[n] = result
    return result
```

**Improvement:** O(2ⁿ) → O(n)  
**Speedup:** Minutes → milliseconds for n=40

---

### Pattern 3: Batch Operations

**Problem:** Making many small operations instead of one large operation.

```
// ❌ BAD: N database queries
for user_id in user_ids:
    user = database.query("SELECT * FROM users WHERE id = ?", user_id)
    process(user)

// ✅ GOOD: 1 database query
users = database.query("SELECT * FROM users WHERE id IN (?)", user_ids)
for user in users:
    process(user)
```

**Improvement:** N queries → 1 query  
**Speedup:** 10x-100x depending on network latency

---

### Pattern 4: Avoid Premature Allocation

**Problem:** Allocating memory unnecessarily.

```
// ❌ BAD: Creates intermediate lists
function process_data(items):
    filtered = [item for item in items if item > 0]
    doubled = [item * 2 for item in filtered]
    summed = sum(doubled)
    return summed

// ✅ GOOD: Single pass, no intermediate allocation
function process_data(items):
    total = 0
    for item in items:
        if item > 0:
            total += item * 2
    return total
```

**Improvement:** 3 allocations → 0 allocations  
**Speedup:** 2x-3x for large datasets

---

### Pattern 5: Lazy Evaluation

**Problem:** Computing values that might not be needed.

```
// ❌ BAD: Always computes expensive_operation
function get_value(use_expensive):
    expensive_result = expensive_operation()  // Always runs
    if use_expensive:
        return expensive_result
    return cheap_default()

// ✅ GOOD: Only computes if needed
function get_value(use_expensive):
    if use_expensive:
        return expensive_operation()  // Only runs if needed
    return cheap_default()
```

---

### Pattern 6: Parallelization

**Problem:** Doing sequential work that could be parallel.

```
// ❌ BAD: Sequential processing
results = []
for url in urls:
    response = fetch(url)  // Blocks until complete
    results.append(process(response))

// ✅ GOOD: Parallel processing
async function process_urls(urls):
    tasks = [fetch_and_process(url) for url in urls]
    results = await gather_all(tasks)  // Parallel execution
    return results
```

**Improvement:** Sequential → Parallel  
**Speedup:** Nx where N = number of parallel tasks

**Caution:** Only parallelize CPU-bound or I/O-bound work. Measure to confirm benefit.

---

## Common Performance Anti-Patterns

### Anti-Pattern 1: Premature Optimization

❌ Optimizing code before profiling.

```
// ❌ BAD: Premature micro-optimization
// "I'll use bit manipulation because it's faster"
function is_even(n):
    return (n & 1) == 0  // Harder to read

// ✅ GOOD: Clear code first
function is_even(n):
    return n % 2 == 0  // Clear and fast enough
```

**Rule:** Don't optimize until profiling shows it's necessary.

---

### Anti-Pattern 2: Trading Readability for Micro-Optimizations

❌ Making code unreadable for negligible gains.

```
// ❌ BAD: Unreadable for 5% speedup
x=(a:=b+c)*(d:=e-f)+a*d

// ✅ GOOD: Readable, 95% as fast
sum_value = b + c
diff_value = e - f
x = sum_value * diff_value + sum_value * diff_value
```

**Rule:** Only sacrifice readability for significant gains (>2x).

---

### Anti-Pattern 3: Optimizing Non-Bottlenecks

❌ Optimizing code that takes <1% of runtime.

```
// ❌ BAD: Optimizing startup code
function initialize():
    config = load_config()  // Runs once, takes 10ms
    // Spending hours optimizing this to 5ms
```

**Rule:** Only optimize code in hot paths (>10% of runtime).

---

### Anti-Pattern 4: Ignoring I/O Bottlenecks

❌ Optimizing CPU code when I/O is the bottleneck.

```
// ❌ BAD: Optimizing computation, but...
function process_users():
    for user in users:
        compute_fast(user)  // 1ms (optimized!)
        database.save(user)  // 50ms (ignored!)
```

**Rule:** Profile I/O separately. It's usually the bottleneck.

---

## Performance Measurement

### Benchmarking Best Practices

```
function benchmark(operation, iterations=1000):
    // Warmup (JIT compilation, caching)
    for i in range(10):
        operation()
    
    // Measure
    start = high_precision_timer()
    for i in range(iterations):
        operation()
    end = high_precision_timer()
    
    // Report
    total_time = end - start
    avg_time = total_time / iterations
    ops_per_second = iterations / total_time
    
    print(f"Average: {avg_time}ms")
    print(f"Throughput: {ops_per_second} ops/sec")
```

---

### Profiling Checklist

- [ ] **CPU profiling:** Identify hot functions
- [ ] **Memory profiling:** Find allocations and leaks
- [ ] **I/O profiling:** Measure database queries, API calls
- [ ] **Benchmark:** Before and after optimization
- [ ] **Real workload:** Use production-like data

---

## Specific Optimization Techniques

### Technique 1: Database Query Optimization

**N+1 Query Problem:**

```
// ❌ BAD: N+1 queries
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)
    user.orders = orders

// ✅ GOOD: 2 queries with JOIN or eager loading
users = db.query("""
    SELECT users.*, orders.*
    FROM users
    LEFT JOIN orders ON users.id = orders.user_id
""")
```

---

### Technique 2: Index Usage

```
// ❌ BAD: No index on frequently queried column
CREATE TABLE users (
    id INTEGER,
    email TEXT,
    name TEXT
)
// Query: SELECT * FROM users WHERE email = ? → Full table scan

// ✅ GOOD: Index on email
CREATE TABLE users (
    id INTEGER,
    email TEXT,
    name TEXT
)
CREATE INDEX idx_users_email ON users(email)
// Query: SELECT * FROM users WHERE email = ? → Index lookup
```

**Speedup:** 100x-1000x for large tables

---

### Technique 3: Compression

```
// For network transfers or large data storage
compressed_data = compress(large_data)
send_over_network(compressed_data)

// Receiver
large_data = decompress(compressed_data)
```

**Trade-off:** CPU time (compression) vs network/disk time (transfer)  
**When beneficial:** Network/disk is bottleneck

---

### Technique 4: Connection Pooling

```
// ❌ BAD: New connection per request
for request in requests:
    connection = create_connection()  // Expensive!
    result = connection.query()
    connection.close()

// ✅ GOOD: Reuse connections from pool
pool = ConnectionPool(size=10)
for request in requests:
    with pool.get_connection() as connection:
        result = connection.query()
    // Connection returned to pool, not closed
```

---

## Performance Targets

### Latency Guidelines (User-Facing)

```
< 100ms  - Feels instant
< 300ms  - Feels fast
< 1000ms - Acceptable
> 1000ms - Feels slow
> 5000ms - User will abandon
```

---

### Throughput Guidelines

```
Database queries: < 100ms per query
API calls: < 200ms per call
Background jobs: < 5 seconds per job
Batch processing: > 1000 items/second
```

---

## Trade-offs

### Memory vs Speed

**Cache:** Uses memory to save computation time.

```
// More memory, faster
cache = {}  // Stores all results

// Less memory, slower
cache = LRUCache(max_size=1000)  // Stores recent results only
```

---

### Accuracy vs Speed

**Approximation:** Faster but less accurate.

```
// Slow but exact
exact_result = compute_exact_value(data)

// Fast but approximate
approx_result = compute_approximate_value(data)
```

---

### Simplicity vs Performance

**Complex optimization:** Faster but harder to maintain.

```
// Simple but slower
result = sorted(items)

// Complex but faster (if already mostly sorted)
result = insertion_sort(items)  // O(n) for nearly sorted
```

**Rule:** Choose simplicity unless profiling proves optimization necessary.

---

## Testing Performance

### Performance Regression Tests

```
function test_performance_regression():
    start = timer()
    result = expensive_operation(large_dataset)
    elapsed = timer() - start
    
    // Assert performance hasn't regressed
    assert elapsed < 1.0, f"Operation took {elapsed}s, expected < 1.0s"
```

---

### Load Testing

```
// Simulate concurrent load
function load_test():
    concurrent_requests = 100
    requests_per_user = 10
    
    async function simulate_user():
        for i in range(requests_per_user):
            await make_request()
    
    // Run 100 concurrent users
    await gather_all([simulate_user() for _ in range(concurrent_requests)])
```

---

## Best Practices Summary

### 1. Always Measure First

**Before optimizing:**
- [ ] Profile to find bottleneck
- [ ] Measure current performance
- [ ] Set target performance

---

### 2. Optimize in Order

```
1. Algorithm (O(n²) → O(n))
2. I/O (N queries → 1 query)
3. Memory (allocations → reuse)
4. CPU (expensive operations → cheaper)
5. Micro-optimizations (last resort)
```

---

### 3. Maintain Readability

```
// ✅ GOOD: Clear and fast enough
function calculate_total(items):
    return sum(item.price for item in items)

// ❌ BAD: Micro-optimized but unreadable
function calculate_total(items):
    t=0;[t:=t+i.p for i in items];return t
```

**Rule:** Readable code is maintainable code.

---

### 4. Document Optimizations

```
// Performance-critical path: runs 10M times/sec
// Profiled: 40% of total CPU time
// Optimized: O(n²) → O(n) using hash set
// Benchmark: 100ms → 5ms for 1000 items
function find_duplicates(items):
    # Implementation
```

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-performance.md`
- See `.agent-os/standards/development/go-performance.md`
- See `.agent-os/standards/development/rust-performance.md`
- Etc.

---

**Premature optimization is the root of all evil. Measure first, optimize bottlenecks, maintain readability. Make it work, make it right, make it fast - in that order.**

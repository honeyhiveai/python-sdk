# Production Code Universal Checklist
**CRITICAL: ALL code written by AI must meet these standards - NO EXCEPTIONS**

**Date**: October 4, 2025  
**Status**: Active  
**Scope**: Every code change, regardless of size or perceived complexity

---

## 🎯 Core Principle

**"AI has no excuse for shortcuts."**

Unlike human developers:
- AI doesn't get tired (no fatigue-induced errors)
- AI doesn't have time pressure (microseconds vs hours)
- AI doesn't have cognitive load limits (can evaluate 100+ scenarios instantly)
- Quality checks add negligible latency (~5 seconds) vs debugging time (hours/days)

**Therefore: Every line of AI-written code must be production-grade from the start.**

---

## 📋 Universal Checks (Tier 1 - MANDATORY FOR ALL CODE)

These checks apply to EVERY code change, no matter how small.

### 1. **Shared State Analysis**
**Question**: Does this code access any shared state?

**Shared state includes:**
- Class attributes (not instance-specific)
- Module-level variables
- File system (reading/writing files)
- Databases, caches, vector stores
- Network connections
- Environment variables (reading is usually safe, but be aware)

**If YES → Concurrency analysis REQUIRED:**
- [ ] What happens if 2+ threads/processes access this simultaneously?
- [ ] Does the library handle locking internally? (Research required - NEVER assume)
- [ ] Do I need external locking? (threading.Lock, RLock, asyncio.Lock)
- [ ] How do I test concurrent access? (Write concurrent test like test_concurrent_access.py)

**Documentation Required:**
```python
# CONCURRENCY: Thread-safe via [RLock/library internal/no shared state]
# Validated with: [test name or reasoning]
```

### 2. **Dependency Analysis**
**Question**: Does this code add or modify an external dependency?

**If YES → Version justification REQUIRED:**
- [ ] Why this specific version or version range?
- [ ] What changed between versions that matters to us?
- [ ] What's the stability/maturity level? (alpha, beta, stable)
- [ ] Are there known issues in this version?

**Version Specification Standards:**
- `package~=1.2.0` - Patch-level compatibility (1.2.x) - **PREFERRED** for stable dependencies
- `package>=1.2.0,<2.0.0` - Explicit upper bound when breaking changes expected
- `package==1.2.0` - Exact pin (rare, only for critical stability or known incompatibility)
- `package>=1.2.0` - **FORBIDDEN** (too broad, non-deterministic builds)

**Documentation Required:**
```python
# requirements.txt
package~=1.2.0  # Justification: Latest stable, fixes concurrency bug in 1.1.x
```

### 3. **Failure Mode Analysis**
**Question**: How does this code fail?

**EVERY code block must answer:**
- [ ] What happens if the external service is down?
- [ ] What happens if the network times out?
- [ ] What happens if input is malformed/invalid?
- [ ] What happens if resources are exhausted (memory, disk, connections)?
- [ ] What's the graceful degradation path?

**Required Pattern:**
```python
try:
    # Primary operation
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    # Graceful degradation (fallback, cached result, None)
    result = fallback_strategy()
```

**Anti-Pattern (FORBIDDEN):**
```python
# Bad: Bare except, no logging, no degradation
try:
    result = risky_operation()
except:
    pass
```

### 4. **Resource Lifecycle**
**Question**: Does this code manage resources (connections, files, locks)?

**If YES → Lifecycle management REQUIRED:**
- [ ] How are resources acquired? (open, connect, acquire)
- [ ] How are resources released? (close, disconnect, release)
- [ ] What happens during reload/restart?
- [ ] What happens if cleanup fails?
- [ ] Memory leak potential?

**Required Pattern:**
```python
# Good: Context manager ensures cleanup
with resource_manager() as resource:
    resource.do_work()

# Or explicit cleanup with try/finally
resource = None
try:
    resource = acquire_resource()
    resource.do_work()
finally:
    if resource:
        resource.cleanup()
```

### 5. **Test Coverage**
**Question**: How do I validate this works?

**EVERY code change must have:**
- [ ] Unit test for happy path
- [ ] Unit test for failure modes
- [ ] Integration test if touching external systems
- [ ] Concurrent access test if touching shared state

**Minimum Acceptable:**
```python
def test_happy_path():
    result = my_function(valid_input)
    assert result == expected_output

def test_failure_mode():
    with pytest.raises(SpecificException):
        my_function(invalid_input)
```

---

## 🏗️ Infrastructure Code Checks (Tier 2 - When Code Involves)

Apply Tier 1 + Tier 2 when code involves:
- Datastores (SQL, NoSQL, vector stores, caches)
- Background threads or async operations
- File I/O with hot reload or watching
- Network connections with pooling
- External APIs with rate limits

### 6. **Datastore Concurrency (Mandatory)**

**Questions:**
- [ ] Does the datastore library handle concurrent access internally?
- [ ] Do I need external locking (read-write locks, mutexes)?
- [ ] What happens during index rebuild/schema migration?
- [ ] How do I test concurrent read/write scenarios?

**Research Protocol:**
1. Read library documentation section on concurrency
2. Search for "thread-safe" or "concurrent" in library docs
3. Check GitHub issues for concurrency-related bugs
4. When in doubt: Add external locking

**Example (LanceDB):**
```python
# LanceDB 0.25.x does NOT handle concurrent writes internally
# External locking required for hot reload scenarios
class RAGEngine:
    def __init__(self):
        self._lock = threading.RLock()  # Reentrant for nested calls
        self._rebuilding = threading.Event()  # Signal rebuild state
    
    def search(self, query):
        if self._rebuilding.is_set():
            self._rebuilding.wait(timeout=30)  # Wait for rebuild
        with self._lock:  # Acquire read lock
            return self._vector_search(query)
    
    def reload_index(self):
        with self._lock:  # Acquire write lock (blocks reads)
            self._rebuilding.set()
            try:
                # Rebuild logic
                pass
            finally:
                self._rebuilding.clear()
```

### 7. **Connection Lifecycle (Mandatory)**

**Questions:**
- [ ] Are connections pooled or per-request?
- [ ] What's the connection timeout strategy?
- [ ] How are stale connections detected and cleaned?
- [ ] What happens during service restart?

**Required Pattern:**
```python
# Good: Explicit cleanup before reconnect
def reload_connection(self):
    with self._lock:
        # Close old connections cleanly
        if hasattr(self, 'connection'):
            del self.connection
        if hasattr(self, 'pool'):
            del self.pool
        
        # Reconnect
        self.connection = create_connection()
```

### 8. **Async/Threading (Mandatory)**

**Questions:**
- [ ] Are there any race conditions between threads?
- [ ] Are there any deadlock scenarios?
- [ ] How do I gracefully shut down background threads?
- [ ] Are daemon threads appropriate or do I need proper cleanup?

**Required Pattern:**
```python
# Good: Background thread with proper cleanup signal
class Worker:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._work, daemon=True)
        self._thread.start()
    
    def _work(self):
        while not self._stop_event.is_set():
            # Do work
            time.sleep(interval)
    
    def shutdown(self):
        self._stop_event.set()
        self._thread.join(timeout=5)
```

---

## 🔬 Complex Systems Checks (Tier 3 - When Code Involves)

Apply Tier 1 + Tier 2 + Tier 3 when code involves:
- New architectural patterns (not yet in codebase)
- Distributed systems (multiple processes/machines)
- Performance-critical paths (hot loops, high throughput)
- Security-sensitive operations (auth, credentials, encryption)

### 9. **Architecture Review (Use Workflow)**

**When to use production_code_v2 workflow:**
- Introducing new design patterns
- Adding new infrastructure components
- Modifying critical paths
- Refactoring > 200 lines

**Workflow phases ensure:**
- Phase 1: Complexity assessment + failure mode analysis
- Phase 2: Design review with alternatives considered
- Phase 3: Implementation with quality gates

### 10. **Performance Analysis**

**Questions:**
- [ ] What's the Big O complexity?
- [ ] Are there any N+1 query problems?
- [ ] What's the memory footprint with large inputs?
- [ ] How does this scale with concurrent requests?

**Validation:**
- [ ] Benchmark with realistic data sizes
- [ ] Profile memory usage
- [ ] Stress test with concurrent load

### 11. **Security Analysis**

**Questions:**
- [ ] Are credentials ever logged or committed?
- [ ] Is user input sanitized?
- [ ] Are secrets properly encrypted at rest?
- [ ] Are there any injection vulnerabilities (SQL, command)?

**Required:**
- [ ] Use environment variables for secrets (NEVER hardcode)
- [ ] Use parameterized queries (NEVER string concatenation)
- [ ] Validate and sanitize all external input
- [ ] Audit logging for security events

---

## ✅ Commit Message Requirements

**Every commit must document checklist completion:**

```
type(scope): brief description

**Tier 1 Checks:**
- Concurrency: [Thread-safe via RLock | No shared state]
- Dependencies: [Added package~=X.Y.Z because reason | No changes]
- Failure Modes: [Graceful degradation via fallback | N/A]
- Resources: [Proper cleanup via context manager | N/A]
- Tests: [Added test_feature_happy_path + test_feature_failure]

**Tier 2 Checks (if applicable):**
- Datastore Concurrency: [External locking added | N/A]
- Connection Lifecycle: [Cleanup before reload | N/A]
- Async/Threading: [No race conditions, validated with concurrent test | N/A]

**Tier 3 Checks (if applicable):**
- Workflow: [production_code_v2 Phase 3 complete | N/A]
- Performance: [O(n) complexity, benchmarked with 10K items | N/A]
- Security: [Credentials from env vars, input sanitized | N/A]
```

---

## 🚨 Anti-Patterns (FORBIDDEN)

### **1. "Prototype Mode" Thinking**
```python
# Bad: "This is just a quick prototype"
def connect_db():
    return sqlite3.connect("db.sqlite")  # No error handling, no cleanup
```

**Why forbidden:** AI has no time pressure. There is no "quick prototype" - only production code.

### **2. Assuming Thread-Safety**
```python
# Bad: "The library probably handles this"
class Cache:
    def __init__(self):
        self._data = {}  # Assumes dict is thread-safe (IT'S NOT)
```

**Why forbidden:** NEVER assume. Research or add locking.

### **3. Broad Version Ranges**
```python
# Bad: requirements.txt
lancedb>=0.3.0  # Allows 22 different versions!
```

**Why forbidden:** Non-deterministic builds. Use `~=` for patch-level compatibility.

### **4. Silent Failures**
```python
# Bad: Fails silently
try:
    result = api_call()
except:
    pass  # User has no idea what went wrong
```

**Why forbidden:** Debugging nightmare. Log errors, degrade gracefully.

### **5. Resource Leaks**
```python
# Bad: No cleanup
file = open("data.txt")
data = file.read()
# file never closed!
```

**Why forbidden:** Use context managers or explicit try/finally cleanup.

---

## 📚 Related Standards

- **[Concurrency Analysis Protocol](concurrency-analysis-protocol.md)** - Detailed guide for analyzing concurrent access patterns
- **[Version Pinning Standards](version-pinning-standards.md)** - Comprehensive dependency versioning rules
- **[Failure Mode Analysis Template](failure-mode-analysis-template.md)** - Structured approach to failure mode thinking

---

## 🎯 Summary: The 5-Second Rule

**Before writing ANY code, spend 5 seconds asking:**

1. **Shared state?** → Concurrency check
2. **Dependency?** → Version justification
3. **How does this fail?** → Failure modes
4. **Resources?** → Lifecycle management
5. **Tests?** → Coverage plan

**5 seconds of AI thinking > Hours of human debugging.**

**This is not optional. This is the baseline for all AI-authored code.**

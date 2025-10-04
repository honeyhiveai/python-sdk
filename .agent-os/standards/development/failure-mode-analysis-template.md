# Failure Mode Analysis Template
**Systematic approach to thinking about how code fails**

**Date**: October 4, 2025  
**Status**: Active  
**Scope**: All production code

---

## 🎯 Core Principle

**"Hope is not a strategy. Plan for failure."**

**The Reality:**
- Networks fail
- Services go down
- Inputs are malformed
- Resources get exhausted
- Bugs exist in dependencies
- Hardware fails

**The Question:** How does your code behave when things go wrong?

**AI Advantage:** Can evaluate 100+ failure scenarios in seconds. No excuse for unhandled edge cases.

---

## 📋 The 5 Failure Mode Questions

**Ask these for EVERY code block:**

### **1. What external dependencies does this code have?**

**Categories:**
- Network (APIs, databases, external services)
- File system (local files, mounted volumes)
- Environment (env vars, system resources)
- External libraries (third-party code)
- Hardware (CPU, memory, disk)

**For each dependency → Next 4 questions**

---

### **2. How can this dependency fail?**

**Common failure modes:**

**Network failures:**
- Service is down (503, connection refused)
- Timeout (slow response, no response)
- Intermittent connectivity (packets dropped)
- DNS resolution failure
- SSL/TLS handshake failure
- Rate limiting (429 Too Many Requests)

**File system failures:**
- File doesn't exist (FileNotFoundError)
- Permission denied (PermissionError)
- Disk full (OSError: No space left)
- File is locked by another process
- Corrupted data
- Wrong format/encoding

**Resource exhaustion:**
- Out of memory (MemoryError)
- Too many open files (OS limit)
- Connection pool exhausted
- Thread pool exhausted
- CPU throttling

**Data failures:**
- Malformed input (JSON syntax error, invalid UTF-8)
- Schema mismatch (missing fields, wrong types)
- Constraint violation (value out of range)
- Null/None when value expected
- Empty collection when items expected

**Dependency failures:**
- Library throws unexpected exception
- Library has bug (returns None instead of value)
- Library deprecated API
- Version incompatibility

---

### **3. What happens if this failure occurs?**

**Trace the impact:**

```python
# Example: API call failure
def get_user(user_id):
    response = api.get(f"/users/{user_id}")  # What if this fails?
    # If fails → exception raised
    user = parse_response(response)  # Never reached
    # If fails → downstream code breaks
    return user  # Never reached

# Downstream impact:
def process_user_request(user_id):
    user = get_user(user_id)  # Crashes here
    # Everything after crashes too
    send_email(user.email)
    log_activity(user.id)
    return success_response()
```

**Impact levels:**
- **Critical**: Data loss, corruption, security breach
- **High**: Request fails, user sees error
- **Medium**: Degraded functionality, fallback works
- **Low**: Logged warning, no user impact

---

### **4. What's the graceful degradation path?**

**Strategies (in order of preference):**

#### **Strategy 1: Retry with Exponential Backoff**
Use for: Transient failures (network blips, temporary service unavailability)

```python
import time

def api_call_with_retry(url, max_retries=3):
    """Retry transient failures with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise  # Final attempt failed
            
            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
```

#### **Strategy 2: Fallback to Cache/Default**
Use for: Read operations where stale data is better than no data

```python
def get_config(key):
    """Get config with fallback to cached value."""
    try:
        # Try primary source
        value = config_service.get(key)
        cache.set(key, value)  # Update cache on success
        return value
    except ServiceUnavailable:
        # Fallback to cache
        cached_value = cache.get(key)
        if cached_value is not None:
            logger.warning(f"Config service down, using cached value for {key}")
            return cached_value
        
        # Fallback to default
        default = DEFAULT_CONFIG.get(key)
        if default is not None:
            logger.warning(f"Config service down, no cache, using default for {key}")
            return default
        
        # No fallback possible
        logger.error(f"Config service down, no cache or default for {key}")
        raise ConfigurationError(f"Cannot get config for {key}")
```

#### **Strategy 3: Circuit Breaker**
Use for: Failing services (stop hitting a dead service)

```python
class CircuitBreaker:
    """Stop calling failing service after threshold."""
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            # Check if timeout expired
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpen("Service is unavailable")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"  # Service recovered
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"  # Stop calling service
            raise
```

#### **Strategy 4: Graceful Feature Degradation**
Use for: Non-critical features

```python
def render_dashboard(user_id):
    """Render dashboard with graceful degradation."""
    dashboard = {
        "user": get_user(user_id),  # Critical - must succeed
        "stats": None,
        "recommendations": None,
        "social_feed": None,
    }
    
    # Try to load optional features
    try:
        dashboard["stats"] = get_user_stats(user_id)
    except Exception as e:
        logger.warning(f"Stats unavailable: {e}")
        # Show dashboard without stats
    
    try:
        dashboard["recommendations"] = get_recommendations(user_id)
    except Exception as e:
        logger.warning(f"Recommendations unavailable: {e}")
        # Show dashboard without recommendations
    
    try:
        dashboard["social_feed"] = get_social_feed(user_id)
    except Exception as e:
        logger.warning(f"Social feed unavailable: {e}")
        # Show dashboard without social feed
    
    return dashboard
```

#### **Strategy 5: Fail Fast (When Appropriate)**
Use for: Critical operations where failure is unacceptable

```python
def charge_payment(user_id, amount):
    """Charge payment - must succeed or fail clearly."""
    try:
        transaction = payment_gateway.charge(user_id, amount)
        if not transaction.success:
            raise PaymentFailed(transaction.error)
        return transaction
    except Exception as e:
        # Log error with full context
        logger.error(f"Payment failed for user {user_id}, amount {amount}: {e}")
        # Do NOT silently fail
        # Do NOT fallback to "free"
        # Fail explicitly so user knows to retry
        raise
```

---

### **5. How do I log/monitor this failure?**

**Every failure path must have:**

#### **1. Structured Logging**
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = api_call(url)
except requests.exceptions.Timeout as e:
    logger.error(
        "API call timeout",
        extra={
            "url": url,
            "timeout": 5,
            "error": str(e),
            "user_id": user_id,  # Context
            "request_id": request_id,  # Correlation
        }
    )
```

**Log levels:**
- `ERROR`: Operation failed, user impacted
- `WARNING`: Degraded, using fallback
- `INFO`: Normal operation with fallback used
- `DEBUG`: Detailed troubleshooting

#### **2. Metrics/Observability**
```python
# Count failures
metrics.increment("api.call.failure", tags=["service:user-api", "error:timeout"])

# Track latency (including failures)
with metrics.timer("api.call.duration"):
    result = api_call(url)

# Alert on thresholds
if failure_rate > 0.05:  # 5% failure rate
    alert.trigger("api_failure_rate_high")
```

#### **3. User-Facing Errors**
```python
# Bad: Expose internal error
return {"error": "ConnectionError: Failed to connect to db-prod-01.internal:5432"}

# Good: User-friendly message, log details
logger.error(f"Database connection failed: {e}", exc_info=True)
return {
    "error": "Service temporarily unavailable. Please try again.",
    "error_code": "SERVICE_UNAVAILABLE",
    "request_id": request_id  # For support to trace
}
```

---

## 📋 Failure Mode Checklist Template

**Use this for every code block with external dependencies:**

```markdown
## Failure Mode Analysis: [Function/Class Name]

### External Dependencies
- [ ] Network: [API endpoint, database, service]
- [ ] File System: [Files read/written]
- [ ] Environment: [Env vars, system resources]
- [ ] Libraries: [Third-party code]

### Failure Scenarios

**Scenario 1: [Dependency] fails due to [reason]**
- **Failure Mode**: [How it fails - exception type, error code]
- **Impact**: [Critical/High/Medium/Low] - [What breaks downstream]
- **Degradation**: [Retry/Fallback/Circuit breaker/Fail fast]
- **Logging**: [What gets logged, at what level]
- **Test**: [How to test this failure mode]

**Scenario 2: [Next failure mode]**
... repeat ...

### Validation
- [ ] All failure modes have degradation strategy
- [ ] All failure modes have logging
- [ ] All failure modes have tests
- [ ] User experience is acceptable for each failure mode
```

---

## 📋 Example: RAG Engine Failure Analysis

```markdown
## Failure Mode Analysis: RAGEngine.search()

### External Dependencies
- [x] LanceDB vector database (file-based)
- [x] SentenceTransformer model (embedding generation)
- [x] File system (standards markdown files for grep fallback)

### Failure Scenarios

**Scenario 1: LanceDB index corrupted/missing**
- **Failure Mode**: FileNotFoundError or lancedb.exceptions.Error
- **Impact**: High - Vector search unavailable
- **Degradation**: Fallback to grep search over raw markdown files
- **Logging**: logger.warning("Vector search unavailable, using grep fallback")
- **Test**: test_grep_fallback_when_index_missing()

**Scenario 2: Embedding model fails to load**
- **Failure Mode**: OSError (model files missing/corrupted)
- **Impact**: High - Cannot generate query embeddings
- **Degradation**: Fallback to grep search (no embeddings needed)
- **Logging**: logger.error("Embedding model load failed", exc_info=True)
- **Test**: test_search_without_embedding_model()

**Scenario 3: LanceDB query timeout**
- **Failure Mode**: TimeoutError after 30s
- **Impact**: High - Query hangs
- **Degradation**: Log warning, fallback to grep
- **Logging**: logger.warning("Vector search timeout, falling back to grep")
- **Test**: test_vector_search_timeout()

**Scenario 4: Concurrent access corruption (race condition)**
- **Failure Mode**: lancedb file path error during hot reload
- **Impact**: Critical - Index corruption
- **Degradation**: Prevention via locking (no degradation needed)
- **Logging**: logger.error("Index corruption detected", exc_info=True)
- **Test**: test_concurrent_access() - 268 queries + 3 reloads = 0 errors

**Scenario 5: Invalid query (empty string, None)**
- **Failure Mode**: ValueError or empty results
- **Impact**: Low - Single query fails
- **Degradation**: Return empty SearchResult with error message
- **Logging**: logger.debug("Invalid query received")
- **Test**: test_search_with_invalid_query()

### Validation
- [x] All failure modes have degradation strategy (grep fallback or prevention)
- [x] All failure modes have logging (INFO, WARNING, or ERROR)
- [x] All failure modes have tests (unit + concurrent access)
- [x] User experience: Queries still work even if vector search fails
```

---

## 🚨 Common Failure Analysis Mistakes

### **1. Assuming Happy Path**
```python
# Bad: Assumes API always succeeds
def get_user(user_id):
    response = api.get(f"/users/{user_id}")
    return response.json()  # What if API is down? Network timeout?

# Good: Handle failures
def get_user(user_id):
    try:
        response = api.get(f"/users/{user_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise UserServiceUnavailable() from e
```

### **2. Silent Failures**
```python
# Bad: Fail silently
try:
    send_notification(user_id)
except:
    pass  # User never knows notification failed!

# Good: Log and alert
try:
    send_notification(user_id)
except Exception as e:
    logger.error(f"Notification failed for user {user_id}: {e}")
    metrics.increment("notification.failure")
    # Decide: Retry? Queue for later? Alert user?
```

### **3. Overly Broad Exception Handling**
```python
# Bad: Catch everything
try:
    result = complex_operation()
except:  # Catches KeyboardInterrupt, SystemExit, everything!
    return None

# Good: Catch specific exceptions
try:
    result = complex_operation()
except (ValueError, KeyError) as e:
    logger.error(f"Operation failed: {e}")
    return default_value()
# Let other exceptions propagate (KeyboardInterrupt, etc.)
```

### **4. No Graceful Degradation**
```python
# Bad: All-or-nothing
def render_page(user_id):
    user = get_user(user_id)  # If fails, whole page fails
    stats = get_stats(user_id)  # If fails, whole page fails
    return render(user, stats)

# Good: Graceful degradation
def render_page(user_id):
    user = get_user(user_id)  # Critical - must succeed
    
    stats = None
    try:
        stats = get_stats(user_id)  # Optional
    except Exception as e:
        logger.warning(f"Stats unavailable: {e}")
    
    return render(user, stats)  # Page works without stats
```

### **5. No Testing of Failure Modes**
```python
# Bad: Only test happy path
def test_get_user():
    user = get_user(123)
    assert user.name == "Alice"

# Good: Test failure modes too
def test_get_user_timeout():
    with patch("requests.get", side_effect=Timeout()):
        with pytest.raises(UserServiceUnavailable):
            get_user(123)

def test_get_user_fallback_to_cache():
    with patch("api.get", side_effect=ServiceUnavailable()):
        user = get_user_with_cache(123)
        assert user is not None  # Got cached user
```

---

## ✅ Checklist Summary

**Before committing code with external dependencies:**

- [ ] Identified all external dependencies
- [ ] Listed all ways each dependency can fail
- [ ] Determined impact level for each failure
- [ ] Chose degradation strategy for each failure
- [ ] Added logging for each failure path
- [ ] Wrote tests for failure modes
- [ ] Validated user experience during failures

**If all checked → Failure modes handled**  
**If any unchecked → DO NOT COMMIT**

---

## 📚 Related Standards

- **[Production Code Universal Checklist](production-code-universal-checklist.md)** - Tier 1 failure mode requirements
- **[Concurrency Analysis Protocol](concurrency-analysis-protocol.md)** - Concurrent failure modes

**Remember: AI can evaluate 100+ failure scenarios in seconds. There is NO excuse for unhandled edge cases.**

# Timeout Patterns - Universal Failure Handling

**Timeless patterns for preventing operations from hanging indefinitely.**

## What are Timeouts?

Timeouts are limits on how long an operation can take before being forcibly terminated or considered failed.

**Key principle:** Don't wait forever. Fail fast when operations take too long.

## Why Timeouts Matter

### Without Timeouts
```
User: "Load my profile"
App: Calls API...
    ↓
API is slow/hung...
    ↓
[30 seconds pass]
    ↓
[User frustrated, closes app]
    ↓
[Request still waiting...]
```

### With Timeouts
```
User: "Load my profile"
App: Calls API with 5s timeout...
    ↓
API is slow/hung...
    ↓
[5 seconds pass]
    ↓
Timeout! Return cached data
    ↓
User sees profile (slightly stale, but fast)
```

---

## Timeout Types

### 1. Connection Timeout

**What it controls:** Time to establish a connection.

**Example:**
```
try:
    connection = connect_to_server(
        host="api.example.com",
        connection_timeout=3_seconds  // Max time to connect
    )
except ConnectionTimeout:
    return "Service unavailable"
```

**Typical values:**
- **Fast services:** 1-3 seconds
- **Slow services:** 5-10 seconds
- **Never:** Infinite (will hang if DNS/network issues)

**When it fires:**
- DNS resolution fails/slow
- Network unreachable
- Server not responding to SYN packets
- Firewall dropping packets

---

### 2. Request Timeout (Read Timeout)

**What it controls:** Time to receive response after connection established.

**Example:**
```
try:
    connection = connect_to_server(host="api.example.com")
    response = connection.request(
        "/api/users",
        request_timeout=10_seconds  // Max time to get response
    )
except RequestTimeout:
    return "Request took too long"
```

**Typical values:**
- **Fast APIs:** 5-15 seconds
- **Slow APIs:** 30-60 seconds
- **Long-running:** 300 seconds (5 minutes)

**When it fires:**
- Server processing slowly
- Large response payload
- Network congestion
- Server hung mid-request

---

### 3. Total Timeout (Deadline)

**What it controls:** Total time for entire operation (connection + request + retries).

**Example:**
```
start_time = current_time()
deadline = start_time + 30_seconds

while current_time() < deadline:
    try:
        result = operation()
        return result
    except TransientError:
        if current_time() >= deadline:
            raise DeadlineExceeded("Operation exceeded 30s deadline")
        sleep(backoff)
```

**Typical values:**
- **User-facing:** 30 seconds (user won't wait longer)
- **Background jobs:** 300-600 seconds (5-10 minutes)
- **Batch processing:** 3600+ seconds (1+ hour)

**When to use:** Prevent operations from running indefinitely across retries.

---

### 4. Idle Timeout (Keep-Alive)

**What it controls:** Time connection can remain idle before being closed.

**Example:**
```
connection_pool = ConnectionPool(
    idle_timeout=60_seconds  // Close idle connections after 60s
)

connection = pool.get_connection()
connection.execute_query(query)
pool.return_connection(connection)

// If no activity for 60s, connection is closed
```

**Typical values:**
- **HTTP connections:** 60-120 seconds
- **Database connections:** 300-600 seconds (5-10 minutes)
- **WebSockets:** 3600+ seconds (or infinite with heartbeat)

**When to use:** Resource management (don't hold connections forever).

---

## Timeout Strategies

### Strategy 1: Aggressive Timeouts with Fallback

**Concept:** Short timeouts, fast failure, good fallback.

```
def get_recommendations(user_id):
    try:
        return api.get_recommendations(
            user_id,
            timeout=2_seconds  // Aggressive!
        )
    except Timeout:
        return get_popular_items()  // Fallback
```

**Benefits:**
- Fast user experience (max 2s wait)
- Always returns result (fallback)

**Drawbacks:**
- May timeout on valid slow responses
- Higher fallback usage

**When to use:** User-facing features where speed > accuracy.

---

### Strategy 2: Conservative Timeouts with Retry

**Concept:** Longer timeouts, retry on failure.

```
max_retries = 3
timeout = 30_seconds

for attempt in range(max_retries):
    try:
        return api.call(timeout=timeout)
    except Timeout:
        if attempt < max_retries - 1:
            continue
        raise
```

**Benefits:**
- Gives operations time to complete
- Retries handle transient slowness

**Drawbacks:**
- Slower failure (30s * 3 = 90s worst case)
- Poor user experience if all timeout

**When to use:** Background jobs, critical operations where accuracy matters.

---

### Strategy 3: Cascading Timeouts

**Concept:** Nested operations have progressively shorter timeouts.

```
def handle_request(total_timeout=10_seconds):
    start = current_time()
    remaining = total_timeout
    
    # Database query gets 3s
    remaining -= 3
    data = database.query(timeout=3_seconds)
    
    # API call gets remaining time (7s)
    remaining = total_timeout - (current_time() - start)
    result = api.call(timeout=remaining)
    
    return result
```

**Benefits:**
- Respects overall deadline
- Prevents one slow operation from consuming all time

**Drawbacks:**
- More complex
- Requires careful time accounting

**When to use:** Multi-step workflows with total deadline.

---

### Strategy 4: Adaptive Timeouts

**Concept:** Adjust timeouts based on historical performance.

```
class AdaptiveTimeout:
    def __init__(self, initial=5_seconds):
        self.history = []
        self.current = initial
    
    def get_timeout(self):
        if len(self.history) < 10:
            return self.current
        
        # p95 latency + buffer
        p95 = percentile(self.history, 95)
        self.current = p95 * 1.5  // 50% buffer
        return self.current
    
    def record(self, duration):
        self.history.append(duration)
        if len(self.history) > 100:
            self.history.pop(0)

adaptive = AdaptiveTimeout()

def call_api():
    timeout = adaptive.get_timeout()
    start = time()
    try:
        result = api.call(timeout=timeout)
        adaptive.record(time() - start)
        return result
    except Timeout:
        adaptive.record(timeout)
        raise
```

**Benefits:**
- Self-tuning
- Adapts to service performance changes

**Drawbacks:**
- Complex implementation
- Requires historical data

**When to use:** Long-running systems with variable service performance.

---

## Timeout Configuration Matrix

| Operation Type | Connection | Request | Total | Idle |
|----------------|------------|---------|-------|------|
| **REST API (fast)** | 3s | 10s | 30s | 60s |
| **REST API (slow)** | 5s | 30s | 60s | 120s |
| **Database query** | 2s | 10s | 30s | 300s |
| **Database connection** | 5s | - | - | 600s |
| **Microservice call** | 2s | 5s | 15s | 60s |
| **File upload** | 5s | 300s | 600s | - |
| **Streaming API** | 5s | Infinite | - | 30s (heartbeat) |
| **Batch job** | 10s | 3600s | 7200s | - |

---

## Integration with Retry and Circuit Breaker

### Timeout + Retry
```
def resilient_call():
    for attempt in range(3):
        try:
            return api.call(timeout=5_seconds)
        except Timeout:
            if attempt < 2:
                sleep(exponential_backoff(attempt))
            else:
                raise
```

### Timeout + Circuit Breaker
```
circuit_breaker = CircuitBreaker()

def protected_call():
    try:
        return circuit_breaker.call(
            lambda: api.call(timeout=5_seconds)
        )
    except Timeout:
        # Circuit breaker tracks timeout as failure
        # Opens circuit after threshold
        raise
```

### All Three Together
```
def fully_resilient_call():
    for attempt in range(3):
        try:
            return circuit_breaker.call(
                lambda: api.call(timeout=5_seconds)
            )
        except CircuitOpenError:
            return fallback_value  // Circuit open, use fallback
        except Timeout:
            if attempt < 2:
                sleep(exponential_backoff(attempt))
            else:
                raise
```

---

## Anti-Patterns

### Anti-Pattern 1: No Timeouts
❌ Operations that can hang forever.

```
// BAD
response = api.call()  // Waits forever if service hangs
```

**Impact:** Application hangs, resources exhausted, poor UX.

### Anti-Pattern 2: Timeout Longer Than User Will Wait
❌ 5-minute timeout for user-facing request.

```
// BAD
def load_profile():
    return api.get_profile(timeout=300_seconds)  // User left after 10s!
```

**Fix:** Use timeout appropriate for user expectations (5-15s).

### Anti-Pattern 3: Timeout Shorter Than Normal Response Time
❌ 1-second timeout when API typically takes 2 seconds.

```
// BAD
return api.call(timeout=1_second)  // Always times out!
```

**Fix:** Set timeout to p95/p99 latency + buffer (not average).

### Anti-Pattern 4: Same Timeout for All Operations
❌ Using global 10-second timeout for everything.

**Fix:** Configure timeouts per operation based on expected latency.

### Anti-Pattern 5: Silent Timeout Handling
❌ Catching timeout exception and doing nothing.

```
// BAD
try:
    return api.call(timeout=5_seconds)
except Timeout:
    pass  // Silent failure!
```

**Fix:** Log timeout, increment metric, provide fallback or error.

---

## Observability

### What to Log
```
logger.warning(
    f"Operation '{operation_name}' timed out "
    f"after {timeout}s. "
    f"Attempt {attempt}/{max_retries}. "
    f"Will retry in {backoff}s."
)
```

### Metrics to Track
```
metrics = {
    "timeout_rate": percentage of requests that timeout,
    "p50_latency": median response time,
    "p95_latency": 95th percentile response time,
    "p99_latency": 99th percentile response time,
    "timeout_threshold": current timeout value
}

// Alert if timeout_rate > 1%
// Alert if p95_latency approaching timeout
```

### Alerts
- Alert if timeout rate exceeds threshold (e.g., >1%)
- Alert if timeouts correlate with service degradation
- Alert if p95 latency consistently close to timeout

---

## Testing Timeouts

### Unit Tests
```
def test_timeout_handling():
    mock_api = MockAPI(delay=10_seconds)
    
    start = time()
    try:
        call_api(mock_api, timeout=1_second)
        assert False, "Should have timed out"
    except Timeout:
        elapsed = time() - start
        assert elapsed < 1.5  // Timed out quickly
```

### Integration Tests
```
def test_cascading_timeouts():
    # Simulate slow downstream service
    slow_service = deploy_slow_service()
    
    result = handle_request(total_timeout=5_seconds)
    
    assert result is not None  // Got fallback
    assert response_time < 5_seconds  // Respected deadline
```

---

## Best Practices

### 1. Always Set Timeouts
Every network operation should have a timeout. No exceptions.

### 2. Use Different Timeouts for Different Stages
- Connection timeout: Short (1-3s)
- Request timeout: Medium (5-30s)
- Total timeout: Long (30-300s)

### 3. Set Timeout Based on p95/p99, Not Average
```
// BAD
timeout = average_latency  // 50% will timeout!

// GOOD
timeout = p95_latency * 1.5  // Only 5% timeout, 50% buffer
```

### 4. Provide Fallback for User-Facing Operations
Don't let user see "Request timeout" error. Show cached/default data.

### 5. Log and Monitor All Timeouts
Timeouts are service degradation signals. Track and alert on them.

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-failure-modes.md` (Python: `timeout` parameter, `signal.alarm()`)
- See `.agent-os/standards/development/go-failure-modes.md` (Go: `context.WithTimeout`, `time.After`)
- See `.agent-os/standards/development/js-failure-modes.md` (JavaScript: `Promise.race`, `AbortController`)
- Etc.

---

**Timeouts are essential for resilient systems. Always set them. Use aggressive timeouts with fallbacks for user-facing operations, conservative timeouts for background jobs. Monitor timeout rates as service health indicators.**

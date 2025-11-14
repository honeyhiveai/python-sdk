# Circuit Breakers - Universal Resilience Pattern

**Timeless pattern for preventing cascade failures in distributed systems.**

---

## 🎯 TL;DR - Circuit Breakers Quick Reference

**Keywords for search**: circuit breaker, circuit breaker pattern, fail fast, cascade failure, distributed systems resilience, circuit breaker states, half-open state, fallback strategy, resilience pattern

**Three Circuit States:**
1. **CLOSED** (Normal) - All requests pass through, monitor failures
2. **OPEN** (Failing) - Block all requests, fail fast, return fallback
3. **HALF-OPEN** (Testing) - Allow limited test requests to check recovery

**State Transitions:**
```
CLOSED → (failures exceed threshold) → OPEN
OPEN → (timeout expires) → HALF-OPEN
HALF-OPEN → (success) → CLOSED
HALF-OPEN → (failure) → OPEN
```

**Key Configuration:**
- **Failure Threshold:** 50% failure rate over 10 requests (typical)
- **Timeout:** 30-60 seconds before testing recovery
- **Test Requests:** 1-5 requests in half-open state

**When to Use:**
- **External API calls** (network unreliability)
- **Database connections** (prevent connection pool exhaustion)
- **Microservice calls** (prevent cascade failures)
- **Any remote dependency** (protect your system from their failures)

**Fallback Strategies:**
- Return cached data
- Return default value
- Degrade to simplified functionality
- Return informative error

**Key Benefit:** Fail fast instead of wasting resources on doomed operations, allowing system to recover.

---

## ❓ Questions This Answers

1. "What is a circuit breaker?"
2. "How do circuit breakers prevent cascade failures?"
3. "When should I use a circuit breaker?"
4. "What are the three circuit breaker states?"
5. "What's the difference between open, closed, and half-open states?"
6. "How do I configure circuit breaker thresholds?"
7. "What's a fallback strategy?"
8. "How do circuit breakers work with retry logic?"
9. "How do I test circuit breaker behavior?"
10. "What circuit breaker anti-patterns should I avoid?"

---

## What is a Circuit Breaker?

A circuit breaker is a design pattern that prevents an application from repeatedly attempting operations that are likely to fail, allowing it to "fail fast" and recover gracefully.

**Inspired by:** Electrical circuit breakers that protect electrical circuits from damage.

**Key principle:** Don't waste resources on operations that will fail. Fail fast, then periodically retry.

## What are the Three Circuit Breaker States?

Circuit breakers operate as a state machine with three distinct states. Understanding state transitions is essential for correct implementation.

```
     CLOSED                    OPEN                   HALF-OPEN
(Normal operation)      (Failing, block calls)    (Testing recovery)
       │                         │                        │
       │ Failures exceed         │ Timeout               │ Success
       │ threshold               │ expires               │
       ↓                         ↓                        ↓
     OPEN ───────────────→ HALF-OPEN ──────────────→ CLOSED
       ↑                         │                        │
       │                         │ Failure                │
       └─────────────────────────┴────────────────────────┘
```

### State 1: CLOSED (Normal Operation)
- All requests pass through
- Monitor failure rate
- If failures exceed threshold → Open circuit

### State 2: OPEN (Blocking)
- All requests fail immediately (no actual call)
- Return cached data or error
- After timeout → Half-Open

### State 3: HALF-OPEN (Testing)
- Allow limited requests through (1-5 test requests)
- If success → Close circuit
- If failure → Open circuit again

---

## How to Implement a Circuit Breaker (Universal Pattern)

This universal implementation pattern applies across all languages and frameworks, providing the core logic for circuit breaker behavior.

```
class CircuitBreaker:
    state = CLOSED
    failure_count = 0
    success_count = 0
    last_failure_time = None
    
    # Thresholds
    failure_threshold = 5        // Open after 5 failures
    success_threshold = 2        // Close after 2 successes
    timeout = 60_seconds         // Try recovery after 60s
    
    def call(operation):
        if state == OPEN:
            if current_time() - last_failure_time > timeout:
                state = HALF_OPEN  // Time to test
            else:
                raise CircuitOpenError("Circuit is open, failing fast")
        
        if state == HALF_OPEN:
            # Only allow limited test requests
            if success_count >= success_threshold:
                state = CLOSED
                failure_count = 0
                return operation()
            else:
                return try_recovery(operation)
        
        # State is CLOSED
        try:
            result = operation()
            failure_count = 0  // Reset on success
            return result
        except Error:
            failure_count += 1
            last_failure_time = current_time()
            
            if failure_count >= failure_threshold:
                state = OPEN
                log("Circuit opened after {failure_count} failures")
            
            raise
    
    def try_recovery(operation):
        try:
            result = operation()
            success_count += 1
            return result
        except Error:
            state = OPEN
            success_count = 0
            raise
```

---

## When Should I Use Circuit Breakers?

Circuit breakers protect your system from wasting resources on failing dependencies. Use them for any remote or unreliable operation.

### ✅ Good Use Cases

**1. External Service Calls**
```
// Protect against failing API
api_breaker = CircuitBreaker()

def fetch_recommendations():
    return api_breaker.call(
        lambda: external_api.get_recommendations()
    )
```

**2. Database Operations**
```
// Protect against database downtime
db_breaker = CircuitBreaker()

def query_users():
    return db_breaker.call(
        lambda: database.query("SELECT * FROM users")
    )
```

**3. Microservice Communication**
```
// Protect calling service from downstream failures
order_service_breaker = CircuitBreaker()

def create_order(order_data):
    return order_service_breaker.call(
        lambda: order_service.create(order_data)
    )
```

### ❌ Bad Use Cases

**1. Local Operations**
- No need for circuit breaker on in-memory operations
- Overhead without benefit

**2. User Input Validation**
- User errors are not transient failures
- Circuit breaker won't help

**3. Operations Without Fallback**
- If you can't provide a fallback, circuit breaker just adds delay
- Better to retry or return error immediately

---

## What Fallback Strategies Should I Use?

When the circuit breaker is open, your system must provide a fallback response. Choose the strategy that best maintains user experience while protecting system resources.

When circuit is open, provide alternative behavior:

### Strategy 1: Cached Data
```
def fetch_user_profile(user_id):
    try:
        return circuit_breaker.call(
            lambda: api.get_profile(user_id)
        )
    except CircuitOpenError:
        cached = cache.get(f"profile:{user_id}")
        if cached:
            return cached  // Stale data better than no data
        raise
```

### Strategy 2: Default Value
```
def get_recommendations():
    try:
        return circuit_breaker.call(
            lambda: api.get_recommendations()
        )
    except CircuitOpenError:
        return get_popular_items()  // Fallback to popular items
```

### Strategy 3: Degraded Functionality
```
def search_products(query):
    try:
        return circuit_breaker.call(
            lambda: advanced_search(query)
        )
    except CircuitOpenError:
        return basic_search(query)  // Simpler search without advanced features
```

### Strategy 4: Queue for Later
```
def send_notification(message):
    try:
        return circuit_breaker.call(
            lambda: notification_service.send(message)
        )
    except CircuitOpenError:
        queue.enqueue(message)  // Send when service recovers
        return {"status": "queued"}
```

---

## How to Configure Circuit Breaker Parameters

Proper configuration is critical for effective circuit breaker behavior. These parameters control when the breaker opens, how long it stays open, and when it tests recovery.

### Failure Threshold
**What:** Number of consecutive failures before opening circuit.

**Typical values:**
- Low-traffic: 3-5 failures
- High-traffic: 10-50 failures (percentage-based)

**Tuning:**
- Too low: False positives (opens on transient blips)
- Too high: Slow to detect real outages

### Timeout (Open → Half-Open)
**What:** How long to wait before testing recovery.

**Typical values:**
- Fast recovery services: 10-30 seconds
- Slow recovery services: 60-300 seconds

**Tuning:**
- Too short: Hammers failing service
- Too long: Delays recovery detection

### Success Threshold (Half-Open → Closed)
**What:** Number of successful tests before closing circuit.

**Typical values:**
- Conservative: 3-5 successes
- Aggressive: 1-2 successes

**Tuning:**
- Too low: May close prematurely (flaky service)
- Too high: Delays full recovery

---

## What Advanced Circuit Breaker Patterns Exist?

These advanced patterns extend basic circuit breaker functionality for complex distributed systems scenarios.

### Pattern 1: Percentage-Based Threshold
**Concept:** Open circuit if failure rate exceeds percentage (not absolute count).

```
failure_rate_threshold = 0.5  // 50% failure rate

if failure_count / total_requests > failure_rate_threshold:
    state = OPEN
```

**Benefits:**
- Scales with traffic
- Handles low-traffic edge cases

### Pattern 2: Time-Window-Based
**Concept:** Track failures in a sliding time window.

```
failure_window = 60_seconds
failures = []  // List of (timestamp, error)

def record_failure(error):
    now = current_time()
    failures.append((now, error))
    
    # Remove old failures outside window
    failures = [(t, e) for t, e in failures if now - t < failure_window]
    
    if len(failures) >= failure_threshold:
        state = OPEN
```

**Benefits:**
- More accurate failure detection
- Handles bursts gracefully

### Pattern 3: Half-Open Request Limit
**Concept:** Allow only N requests through in half-open state.

```
half_open_request_limit = 5
half_open_requests_made = 0

if state == HALF_OPEN:
    if half_open_requests_made >= half_open_request_limit:
        raise CircuitOpenError("Half-open request limit reached")
    
    half_open_requests_made += 1
    # Try operation
```

**Benefits:**
- Limits load on recovering service
- Prevents thundering herd

---

## How Do Circuit Breakers Integrate with Retry Strategies?

Circuit breakers and retry strategies are complementary resilience patterns. Use them together for optimal failure handling.

Circuit breakers complement retry strategies:

```
max_retries = 3
circuit_breaker = CircuitBreaker()

for attempt in range(max_retries):
    try:
        result = circuit_breaker.call(
            lambda: external_api.call()
        )
        return result
    except CircuitOpenError:
        # Don't retry if circuit is open
        return fallback_value
    except TransientError:
        # Retry transient errors
        if attempt < max_retries - 1:
            sleep(exponential_backoff(attempt))
        else:
            raise
```

**Key principle:**
- Circuit breaker = System-level protection (many requests)
- Retry = Request-level resilience (single request)

---

## How to Monitor Circuit Breaker Behavior

Effective observability helps you tune circuit breaker parameters, diagnose issues, and understand system health.

### Metrics to Track
```
circuit_breaker.metrics = {
    "state": "closed|open|half_open",
    "failure_count": 0,
    "success_count": 0,
    "requests_blocked": 0,  // Count of fast-fail requests
    "last_state_change": timestamp,
    "state_durations": {
        "closed": total_seconds,
        "open": total_seconds,
        "half_open": total_seconds
    }
}
```

### Logging
```
// State transitions
logger.warning(
    f"Circuit breaker '{name}' state changed: "
    f"{old_state} → {new_state}. "
    f"Failure count: {failure_count}, "
    f"Last error: {last_error}"
)

// Fast-fail events
logger.info(
    f"Circuit breaker '{name}' is OPEN. "
    f"Request blocked (fast-fail). "
    f"Will retry in {timeout - elapsed}s"
)
```

### Alerts
- Alert when circuit opens (service degraded)
- Alert if circuit stays open for extended time (service down)
- Alert if circuit flaps (open/close rapidly, configuration issue)

---

## What Circuit Breaker Anti-Patterns Should I Avoid?

These common mistakes undermine circuit breaker effectiveness or create new problems.

### Anti-Pattern 1: No Fallback
❌ Circuit opens, but no alternative behavior.

**Result:** User gets error, no better than just failing.

### Anti-Pattern 2: Too Aggressive Threshold
❌ Opens circuit after 1-2 failures.

**Result:** Opens on transient blips, false positives.

### Anti-Pattern 3: Too Long Timeout
❌ Waits 30 minutes before testing recovery.

**Result:** Service recovers but circuit stays open unnecessarily.

### Anti-Pattern 4: Blocking Requests in HALF-OPEN Without Limit
❌ All requests flow through in half-open state.

**Result:** Thundering herd on recovering service.

---

## How to Test Circuit Breakers

Circuit breaker testing ensures correct state transitions and fallback behavior under failure conditions.

### Unit Tests
```
def test_circuit_opens_after_failures():
    breaker = CircuitBreaker(failure_threshold=3)
    
    # Simulate 3 failures
    for i in range(3):
        try:
            breaker.call(lambda: raise_error())
        except:
            pass
    
    assert breaker.state == OPEN

def test_circuit_closes_after_successes():
    breaker = CircuitBreaker(success_threshold=2)
    breaker.state = HALF_OPEN
    
    # Simulate 2 successes
    breaker.call(lambda: "success")
    breaker.call(lambda: "success")
    
    assert breaker.state == CLOSED
```

### Integration Tests
- Simulate service failures
- Verify circuit opens
- Verify fallback behavior
- Simulate recovery
- Verify circuit closes

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **External API integration** | `pos_search_project(content_type="standards", query="circuit breaker")` |
| **Cascade failure prevention** | `pos_search_project(content_type="standards", query="prevent cascade failure")` |
| **Microservices communication** | `pos_search_project(content_type="standards", query="circuit breaker pattern")` |
| **Service degradation** | `pos_search_project(content_type="standards", query="fallback strategy")` |
| **Half-open state confusion** | `pos_search_project(content_type="standards", query="circuit breaker states")` |
| **Parameter tuning** | `pos_search_project(content_type="standards", query="circuit breaker configuration")` |
| **Resilience patterns** | `pos_search_project(content_type="standards", query="fail fast")` |

---

## 🔗 Related Standards

**Query workflow for resilient systems:**

1. **Start with retries** → `pos_search_project(content_type="standards", query="retry strategies")` → `standards/failure-modes/retry-strategies.md`
2. **Add circuit breaker** → `pos_search_project(content_type="standards", query="circuit breaker")` (this document)
3. **Add graceful degradation** → `pos_search_project(content_type="standards", query="graceful degradation")` → `standards/failure-modes/graceful-degradation.md`
4. **Add timeouts** → `pos_search_project(content_type="standards", query="timeout patterns")` → `standards/failure-modes/timeout-patterns.md`

**By Category:**

**Failure Modes:**
- `standards/failure-modes/retry-strategies.md` - Retry logic (use inside circuit breaker) → `pos_search_project(content_type="standards", query="retry strategies")`
- `standards/failure-modes/graceful-degradation.md` - Degrading functionality → `pos_search_project(content_type="standards", query="graceful degradation")`
- `standards/failure-modes/timeout-patterns.md` - Timeout configuration → `pos_search_project(content_type="standards", query="timeout patterns")`

**Testing:**
- `standards/testing/integration-testing.md` - Testing circuit breaker behavior → `pos_search_project(content_type="standards", query="integration testing")`

**Architecture:**
- `standards/architecture/dependency-injection.md` - Injecting circuit breakers → `pos_search_project(content_type="standards", query="dependency injection")`

**AI Safety:**
- `standards/ai-safety/production-code-checklist.md` - Production code checklist (includes failure handling) → `pos_search_project(content_type="standards", query="production code checklist")`

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-failure-modes.md` (Python: `pybreaker` library)
- See `.praxis-os/standards/development/go-failure-modes.md` (Go: `github.com/sony/gobreaker`)
- See `.praxis-os/standards/development/js-failure-modes.md` (JavaScript: `opossum` library)
- Etc.

---

**Circuit breakers are essential for resilient distributed systems. Use them to protect your service from cascade failures and fail fast when dependencies are down.**

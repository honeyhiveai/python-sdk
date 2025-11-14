# Retry Strategies - Universal Failure Handling Pattern

**Timeless patterns for handling transient failures.**

---

## 🎯 TL;DR - Retry Strategies Quick Reference

**Keywords for search**: retry strategies, retry patterns, exponential backoff, jitter, transient failures, idempotency, circuit breaker, failure handling, retry logic, backoff algorithm

**Core Retry Strategies:**
1. **Simple Retry (Fixed Delay)** - Retry N times with fixed delay (use for low-traffic)
2. **Exponential Backoff** - Double delay each attempt (1s → 2s → 4s)
3. **Exponential Backoff + Jitter** - Add randomness to prevent thundering herd (**recommended for production**)
4. **Retry with Timeout** - Give up after max time, not just max attempts
5. **Adaptive Retry** - Integrate with circuit breaker for system-wide protection

**Key Principles:**
- **Retry transient failures only** (503, timeout, rate limit)
- **Don't retry permanent failures** (401, 404, 400)
- **Make operations idempotent** - Retrying must be safe
- **Use exponential backoff + jitter** - Prevents thundering herd
- **Set max retries AND timeout** - Avoid infinite loops

**Quick Decision:**
- **Network/API calls** → Exponential backoff + jitter
- **Database operations** → Simple retry (fast recovery)
- **File operations** → Retry with timeout
- **High-traffic systems** → Adaptive retry + circuit breaker

**Retry Decision:**
```
503/504/429/timeout → RETRY
401/403/404/400 → FAIL IMMEDIATELY
```

---

## ❓ Questions This Answers

1. "How do I implement retry logic?"
2. "When should I retry a failed operation?"
3. "What's exponential backoff?"
4. "What's jitter and why do I need it?"
5. "Should I retry a 404 error?"
6. "How many times should I retry?"
7. "What's the difference between transient and permanent failures?"
8. "How do I prevent thundering herd during retries?"
9. "What does idempotency mean for retries?"
10. "How do I combine retries with circuit breakers?"

---

## What are Retry Strategies?

Retry strategies are systematic approaches to re-attempting failed operations when failures are transient (temporary) rather than permanent.

**Key principle:** Not all failures are permanent. Network blips, temporary overload, and brief outages should be retried.

## How to Distinguish Transient vs Permanent Failures

The first step in retry logic is classifying failures. Retrying permanent failures wastes resources and delays error reporting to users.

### Transient Failures (Retry-able)
- ✅ Network timeout
- ✅ Service temporarily unavailable (503)
- ✅ Database connection pool exhausted
- ✅ Rate limit exceeded (429)
- ✅ Temporary file lock

**Characteristic:** Will succeed if retried after a delay.

### Permanent Failures (Don't Retry)
- ❌ Invalid credentials (401)
- ❌ Resource not found (404)
- ❌ Bad request format (400)
- ❌ Insufficient permissions (403)
- ❌ Resource deleted

**Characteristic:** Will never succeed, retrying wastes resources.

---

## How to Implement Simple Retry (Fixed Delay) - Strategy 1

Simple retry with fixed delay is the easiest retry strategy to implement. Use it for low-traffic systems or when failures recover quickly.

**Concept:** Retry N times with fixed delay between attempts.

```
max_retries = 3
delay = 1_second

for attempt in range(max_retries):
    try:
        result = operation()
        return result  // Success
    except TransientError:
        if attempt < max_retries - 1:
            sleep(delay)
        else:
            raise  // Failed after all retries
```

**Benefits:**
- Simple to implement
- Predictable behavior

**Drawbacks:**
- May retry too fast (thundering herd)
- Wastes time if service is down for extended period

**When to use:** Low-traffic systems, quick recovery expected.

---

## How to Implement Exponential Backoff - Strategy 2

Exponential backoff increases delay exponentially with each retry, reducing load on failing services and allowing time for recovery.

**Concept:** Increase delay exponentially after each failure.

```
max_retries = 5
base_delay = 1_second

for attempt in range(max_retries):
    try:
        result = operation()
        return result  // Success
    except TransientError:
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)  // 1s, 2s, 4s, 8s, 16s
            sleep(delay)
        else:
            raise
```

**Benefits:**
- Backs off under sustained failure
- Reduces load on failing service
- Industry standard (AWS, Google, etc.)

**Drawbacks:**
- Delays grow quickly
- May wait too long if service recovers quickly

**When to use:** Most scenarios, especially with external services.

---

## How to Implement Exponential Backoff with Jitter - Strategy 3 (Recommended)

Jitter adds randomness to backoff delays, preventing all clients from retrying simultaneously. This is the recommended production strategy.

**Concept:** Add randomness to exponential backoff to prevent thundering herd.

```
max_retries = 5
base_delay = 1_second

for attempt in range(max_retries):
    try:
        result = operation()
        return result
    except TransientError:
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)
            jitter = random_uniform(0, delay * 0.3)  // Up to 30% jitter
            final_delay = delay + jitter
            sleep(final_delay)
        else:
            raise
```

**Benefits:**
- Prevents synchronized retries from many clients
- Spreads load over time
- Industry best practice

**Drawbacks:**
- Slightly more complex
- Non-deterministic delay

**When to use:** High-traffic distributed systems (recommended).

---

## How to Implement Retry with Timeout - Strategy 4

Timeout-based retries set a maximum total time for all retry attempts, preventing operations from hanging indefinitely even with exponential backoff.

**Concept:** Limit total time spent retrying, not just number of attempts.

```
max_total_time = 30_seconds
start_time = current_time()

while current_time() - start_time < max_total_time:
    try:
        result = operation()
        return result
    except TransientError:
        elapsed = current_time() - start_time
        if elapsed < max_total_time:
            delay = calculate_backoff(elapsed)
            sleep(delay)
        else:
            raise TimeoutError("Exceeded max retry time")
```

**Benefits:**
- Bounds total latency
- Prevents indefinite retries
- User-friendly (predictable timeout)

**Drawbacks:**
- May retry fewer times if delays are long
- Requires time tracking

**When to use:** User-facing requests with latency requirements.

---

## How to Implement Adaptive Retry (Circuit Breaker Integration) - Strategy 5

Adaptive retry dynamically adjusts retry behavior based on system health, integrating with circuit breakers for system-wide failure protection.

**Concept:** Adjust retry behavior based on system health.

```
circuit_state = get_circuit_state(service)

if circuit_state == OPEN:
    raise ServiceUnavailable("Circuit open, skipping retry")

if circuit_state == HALF_OPEN:
    max_retries = 1  // Limited retries in half-open state
else:
    max_retries = 5  // Normal retries in closed state

for attempt in range(max_retries):
    try:
        result = operation()
        circuit_breaker.record_success()
        return result
    except TransientError:
        circuit_breaker.record_failure()
        if attempt < max_retries - 1:
            sleep(exponential_backoff(attempt))
        else:
            raise
```

**Benefits:**
- Fails fast when service is known to be down
- Reduces unnecessary retries
- Integrates with broader resilience patterns

**Drawbacks:**
- More complex
- Requires circuit breaker state

**When to use:** Microservices, distributed systems with circuit breakers.

---

## How to Choose the Right Retry Strategy (Decision Matrix)

Use this matrix to quickly select the appropriate retry strategy based on failure type and context.

| Failure Type | Retry? | Strategy | Max Retries | Max Time |
|--------------|--------|----------|-------------|----------|
| Network timeout | ✅ Yes | Exponential backoff + jitter | 5 | 30s |
| 503 Service Unavailable | ✅ Yes | Exponential backoff + jitter | 5 | 30s |
| 429 Rate Limit | ✅ Yes | Backoff based on Retry-After header | 3 | 60s |
| 500 Internal Server Error | ⚠️ Maybe | Exponential backoff | 3 | 15s |
| 404 Not Found | ❌ No | - | 0 | - |
| 400 Bad Request | ❌ No | - | 0 | - |
| 401 Unauthorized | ❌ No | - | 0 | - |
| Database deadlock | ✅ Yes | Exponential backoff | 3 | 10s |
| Connection refused | ✅ Yes | Exponential backoff + jitter | 5 | 30s |

---

## Why Idempotency is Critical for Retries

Retrying non-idempotent operations can cause duplicate side effects (double charges, duplicate records). Operations must be idempotent before implementing retries.

**Critical:** Retries are only safe if operations are idempotent.

### What is Idempotency?
An operation is idempotent if performing it multiple times has the same effect as performing it once.

**Idempotent operations (safe to retry):**
- ✅ GET requests (reading data)
- ✅ PUT requests (full resource replacement)
- ✅ DELETE requests (deleting same resource multiple times)
- ✅ Database queries (SELECT)

**Non-idempotent operations (dangerous to retry):**
- ❌ POST requests without idempotency keys
- ❌ Charging a credit card
- ❌ Sending an email
- ❌ Incrementing a counter (without proper locking)

### Making Operations Idempotent

**Pattern: Idempotency Keys**
```
request_id = generate_unique_id()

for attempt in range(max_retries):
    try:
        result = api.create_payment(
            amount=100,
            idempotency_key=request_id  // Same key for all retries
        )
        return result
    except TransientError:
        sleep(backoff)
        continue  // Safe to retry with same key
```

**Server-side:**
```
def create_payment(amount, idempotency_key):
    # Check if already processed
    existing = db.get_payment(idempotency_key)
    if existing:
        return existing  // Return previous result
    
    # Process new payment
    payment = process_payment(amount)
    db.store_payment(idempotency_key, payment)
    return payment
```

---

## What Retry Anti-Patterns Should I Avoid?

These common retry mistakes can make outages worse, waste resources, or cause data corruption. Recognize and avoid them.

### Anti-Pattern 1: Immediate Retry Without Delay
❌ Retrying instantly on failure (amplifies load).

```
// BAD
for attempt in range(10):
    try:
        result = operation()
        return result
    except Error:
        continue  // No delay, hammers service!
```

### Anti-Pattern 2: Infinite Retries
❌ Retrying forever without bounds.

```
// BAD
while True:
    try:
        return operation()
    except Error:
        sleep(1)  // Retries forever!
```

### Anti-Pattern 3: Retrying Non-Transient Errors
❌ Retrying 404 Not Found or 401 Unauthorized.

```
// BAD
for attempt in range(5):
    try:
        return fetch_user(user_id)
    except NotFoundError:
        sleep(1)  // Will never succeed!
```

### Anti-Pattern 4: No Logging
❌ Retrying silently without logging.

```
// BAD
try:
    return operation()
except TransientError:
    # Silent retry, no visibility
    return operation()
```

**Good pattern:** Log every retry with attempt number, error, and delay.

---

## How to Monitor and Observe Retry Behavior

Effective retry observability helps diagnose issues, tune retry parameters, and detect when services need attention.

### What to Log
```
logger.warning(
    f"Retry attempt {attempt + 1}/{max_retries} "
    f"for operation '{operation_name}' "
    f"after {error_type}: {error_message}. "
    f"Retrying in {delay}s..."
)
```

### Metrics to Track
- **Retry rate:** % of operations that required retries
- **Retry attempts:** Average number of retries per operation
- **Final failure rate:** % of operations that failed after all retries
- **Latency impact:** Added latency from retries

### Alerts
- Alert if retry rate exceeds threshold (e.g., >10%)
- Alert if final failure rate is high (e.g., >1%)
- Alert if retry delays are consistently long (service degraded)

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Network call failures** | `pos_search_project(content_type="standards", query="retry strategies")` |
| **API integration** | `pos_search_project(content_type="standards", query="exponential backoff")` |
| **Transient errors** | `pos_search_project(content_type="standards", query="when to retry failures")` |
| **Distributed systems** | `pos_search_project(content_type="standards", query="retry with jitter")` |
| **Duplicate operations concern** | `pos_search_project(content_type="standards", query="idempotency retries")` |
| **Retry tuning** | `pos_search_project(content_type="standards", query="retry decision matrix")` |
| **Thundering herd** | `pos_search_project(content_type="standards", query="jitter retry")` |

---

## 🔗 Related Standards

**Query workflow for resilient failure handling:**

1. **Start here** → `pos_search_project(content_type="standards", query="retry strategies")`
2. **Then protect** → `pos_search_project(content_type="standards", query="circuit breaker")` → `standards/failure-modes/circuit-breakers.md`
3. **Then degrade** → `pos_search_project(content_type="standards", query="graceful degradation")` → `standards/failure-modes/graceful-degradation.md`
4. **Then timeout** → `pos_search_project(content_type="standards", query="timeout patterns")` → `standards/failure-modes/timeout-patterns.md`

**By Category:**

**Failure Modes:**
- `standards/failure-modes/circuit-breakers.md` - System-wide failure protection → `pos_search_project(content_type="standards", query="circuit breaker")`
- `standards/failure-modes/graceful-degradation.md` - Degrade functionality when services fail → `pos_search_project(content_type="standards", query="graceful degradation")`
- `standards/failure-modes/timeout-patterns.md` - Timeout configuration → `pos_search_project(content_type="standards", query="timeout patterns")`

**Testing:**
- `standards/testing/integration-testing.md` - Testing retry logic → `pos_search_project(content_type="standards", query="integration testing")`

**Database:**
- `standards/database/database-patterns.md` - Database retry strategies → `pos_search_project(content_type="standards", query="database retry")` 

**AI Safety:**
- `standards/ai-safety/production-code-checklist.md` - Production code checklist (includes failure handling) → `pos_search_project(content_type="standards", query="production code checklist")`

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-failure-modes.md` (Python: `retrying`, `tenacity` libraries)
- See `.praxis-os/standards/development/go-failure-modes.md` (Go: `github.com/cenkalti/backoff`)
- See `.praxis-os/standards/development/js-failure-modes.md` (JavaScript: `retry`, `async-retry` libraries)
- Etc.

---

**Retry strategies are essential for resilient systems. Use exponential backoff with jitter for most scenarios. Always ensure operations are idempotent before retrying.**

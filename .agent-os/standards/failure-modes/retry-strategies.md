# Retry Strategies - Universal Failure Handling Pattern

**Timeless patterns for handling transient failures.**

## What are Retry Strategies?

Retry strategies are systematic approaches to re-attempting failed operations when failures are transient (temporary) rather than permanent.

**Key principle:** Not all failures are permanent. Network blips, temporary overload, and brief outages should be retried.

## Transient vs Permanent Failures

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

## Strategy 1: Simple Retry (Fixed Delay)

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

## Strategy 2: Exponential Backoff

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

## Strategy 3: Exponential Backoff with Jitter

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

## Strategy 4: Retry with Timeout

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

## Strategy 5: Adaptive Retry (Circuit Breaker Integration)

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

## Retry Decision Matrix

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

## Idempotency Requirements

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

## Anti-Patterns

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

## Observability

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

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-failure-modes.md` (Python: `retrying`, `tenacity` libraries)
- See `.agent-os/standards/development/go-failure-modes.md` (Go: `github.com/cenkalti/backoff`)
- See `.agent-os/standards/development/js-failure-modes.md` (JavaScript: `retry`, `async-retry` libraries)
- Etc.

---

**Retry strategies are essential for resilient systems. Use exponential backoff with jitter for most scenarios. Always ensure operations are idempotent before retrying.**

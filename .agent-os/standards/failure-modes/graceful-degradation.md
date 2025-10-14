# Graceful Degradation - Universal Failure Handling Pattern

**Timeless pattern for handling failures without complete system collapse.**

## What is Graceful Degradation?

Graceful degradation is the practice of designing systems to continue operating (at reduced functionality) when components fail, rather than failing completely.

**Principle:** It's better to provide partial service than no service at all.

## Universal Pattern

```
Normal Operation:
  Request → Service A → Service B → Service C → Response (full features)

Service B Fails:
  Request → Service A → [Service B FAILED] → Service C → Response (reduced features)
  
System stays operational, just with degraded capability.
```

## Why Graceful Degradation Matters

### Real-World Example: E-Commerce Site

**Without Graceful Degradation:**
- Recommendation service fails → Entire site crashes
- User gets error page → Lost sale

**With Graceful Degradation:**
- Recommendation service fails → Site continues
- Recommendations section shows "Popular Items" fallback
- User can still browse and purchase → Sale preserved

## Degradation Strategies (Universal)

### Strategy 1: Fallback to Cached Data
**Pattern:** Use stale data when fresh data unavailable.

```
try:
    data = fetch_from_api()
    cache.set(data)
except APIError:
    data = cache.get()  # Use cached data
    if data is None:
        data = default_data  # Final fallback
```

**Use cases:**
- Product recommendations (show popular items)
- Pricing data (use last known prices)
- User profiles (use cached profile)

### Strategy 2: Feature Degradation
**Pattern:** Disable non-critical features, keep core functional.

```
features = {
    "core": ["browse", "purchase", "checkout"],  # Always available
    "enhanced": ["recommendations", "reviews", "personalization"]  # Can degrade
}

if service_health["recommendations"] == "down":
    disable_feature("recommendations")
    # Core features still work
```

**Use cases:**
- Disable recommendations, keep shopping
- Disable real-time updates, show refresh button
- Disable analytics tracking, keep functionality

### Strategy 3: Timeout and Circuit Breaker
**Pattern:** Fail fast with fallback rather than waiting indefinitely.

```
try:
    result = slow_service.call(timeout=2_seconds)
except TimeoutError:
    result = fallback_value
    circuit_breaker.open("slow_service")
```

**Benefits:**
- Faster response (2s timeout vs 30s hang)
- Circuit breaker prevents cascade failures
- User gets response, even if degraded

### Strategy 4: Partial Results
**Pattern:** Return incomplete results rather than nothing.

```
results = []
for service in [serviceA, serviceB, serviceC]:
    try:
        results.append(service.fetch())
    except ServiceError:
        continue  # Skip failed service, collect from others

return results  # Return whatever we got
```

**Use cases:**
- Search across multiple data sources
- Aggregating data from multiple services
- Federated queries

### Strategy 5: Read-Only Mode
**Pattern:** Allow reads when writes are unavailable.

```
if database.is_writable():
    process_write_request()
else:
    return "Service in read-only mode, try again later"
    # Reads still work
```

**Use cases:**
- Database maintenance
- Storage system issues
- Replication lag

## Failure Mode Decision Tree

```
Service fails
    ↓
Is there cached data?
    YES → Use cached data (Strategy 1)
    NO ↓
Is the feature critical?
    NO → Disable feature, continue (Strategy 2)
    YES ↓
Can we provide partial results?
    YES → Return what we have (Strategy 4)
    NO ↓
Can we operate read-only?
    YES → Enable read-only mode (Strategy 5)
    NO ↓
Fail fast with clear error message
```

## User Experience Considerations

### Good Degradation (User-Aware)
```
┌─────────────────────────────────────┐
│ Shopping Cart                        │
│                                      │
│ [Item 1] $10                        │
│ [Item 2] $15                        │
│                                      │
│ ⚠️  Recommendations temporarily     │
│    unavailable. Showing popular     │
│    items instead.                   │
│                                      │
│ [Popular Item 1] $20                │
│ [Popular Item 2] $25                │
│                                      │
│ [Checkout] ← Still works            │
└─────────────────────────────────────┘
```

### Bad Degradation (Silent or Confusing)
```
┌─────────────────────────────────────┐
│ Shopping Cart                        │
│                                      │
│ [Item 1] $10                        │
│ [Item 2] $15                        │
│                                      │
│ (Empty recommendations section)     │
│ (User thinks: "No recommendations   │
│  for me? Is something wrong?")      │
│                                      │
│ [Checkout] ← Still works but user  │
│            is confused              │
└─────────────────────────────────────┘
```

**Best practice:** Communicate degradation to users when appropriate.

## Testing Graceful Degradation

### Chaos Engineering
Intentionally inject failures to test degradation:

1. **Kill services randomly**: Does system survive?
2. **Introduce latency**: Do timeouts work?
3. **Fill up disk/memory**: Does system degrade cleanly?
4. **Partition network**: Does system handle split-brain?

### Automated Tests
```
def test_recommendation_service_failure():
    # Simulate service failure
    mock_recommendation_service.fail()
    
    # System should fall back to popular items
    response = get_recommendations()
    assert response.fallback_used == True
    assert len(response.items) > 0
    assert response.items == popular_items
```

## Anti-Patterns

### Anti-Pattern 1: Silent Failures
❌ Service fails, system continues without fallback, user gets broken experience.

### Anti-Pattern 2: Cascade Failures
❌ One service fails, takes down entire system because no circuit breakers.

### Anti-Pattern 3: Infinite Retries
❌ Service fails, system retries forever, never degrades, user waits indefinitely.

### Anti-Pattern 4: Data Loss Degradation
❌ Write operation fails, system silently drops data without user knowing.

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-failure-modes.md` (Python exceptions, try/except)
- See `.agent-os/standards/development/go-failure-modes.md` (Go errors, error handling)
- See `.agent-os/standards/development/js-failure-modes.md` (JavaScript promises, async/await)
- Etc.

---

**Graceful degradation is universal. The implementation details vary by language and architecture.**

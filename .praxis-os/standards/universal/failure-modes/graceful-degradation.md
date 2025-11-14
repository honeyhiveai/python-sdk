# Graceful Degradation - Universal Failure Handling Pattern

**Timeless pattern for handling failures without complete system collapse.**

---

## 🎯 TL;DR - Graceful Degradation Quick Reference

**Keywords for search**: graceful degradation, partial service, system degradation, feature degradation, fallback data, reduced functionality, service degradation, resilience pattern, failure handling

**Core Principle:** Better to provide partial service than no service at all.

**Degradation Strategies:**
1. **Fallback to Cached Data** - Use stale data when fresh data unavailable
2. **Feature Degradation** - Disable non-critical features, keep core functional
3. **Simplified Response** - Return basic data instead of enriched data
4. **Queue for Later** - Accept request, process asynchronously when service recovers
5. **Read-Only Mode** - Allow reads, disable writes

**Decision Tree:**
```
Dependency Failed?
├─ Critical (payment, auth) → Return Error (fail fast)
├─ Important (search) → Simplified fallback
└─ Nice-to-have (recommendations) → Disable feature
```

**User Experience Guidelines:**
- **Communicate degradation** - Tell users what's limited
- **Set expectations** - "Recommendations temporarily unavailable"
- **Preserve core functionality** - Always protect critical user flows
- **Log degradation events** - Track for monitoring and alerting

**Key Benefit:** System stays operational during partial failures, preserving user experience and business value.

---

## ❓ Questions This Answers

1. "What is graceful degradation?"
2. "How do I keep my system running when a dependency fails?"
3. "What's the difference between critical and non-critical failures?"
4. "How do I provide fallback data when a service is down?"
5. "Should I cache data for graceful degradation?"
6. "How do I communicate degraded service to users?"
7. "When should I disable features vs. show cached data?"
8. "How do I test graceful degradation?"
9. "What features should degrade first?"
10. "How does graceful degradation work with circuit breakers?"

---

## What is Graceful Degradation?

Graceful degradation is the practice of designing systems to continue operating (at reduced functionality) when components fail, rather than failing completely.

**Principle:** It's better to provide partial service than no service at all.

## How Does Graceful Degradation Work? (Universal Pattern)

Graceful degradation allows systems to maintain partial functionality when dependencies fail, rather than cascading to complete failure.

```
Normal Operation:
  Request → Service A → Service B → Service C → Response (full features)

Service B Fails:
  Request → Service A → [Service B FAILED] → Service C → Response (reduced features)
  
System stays operational, just with degraded capability.
```

## Why Does Graceful Degradation Matter?

Understanding the business impact of graceful degradation helps prioritize its implementation. Partial service often means the difference between lost revenue and preserved user experience.

### Real-World Example: E-Commerce Site

**Without Graceful Degradation:**
- Recommendation service fails → Entire site crashes
- User gets error page → Lost sale

**With Graceful Degradation:**
- Recommendation service fails → Site continues
- Recommendations section shows "Popular Items" fallback
- User can still browse and purchase → Sale preserved

## What Degradation Strategies Should I Use?

Choose the appropriate degradation strategy based on the type of dependency failure and the importance of the feature to user experience.

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

## How to Decide What to Degrade (Decision Tree)

Not all features are equal. Use this decision tree to determine the appropriate response when a dependency fails.

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

## How to Communicate Degraded Service to Users

Transparent communication about degraded service maintains user trust and sets appropriate expectations.

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

## How to Test Graceful Degradation

Testing graceful degradation ensures your fallback strategies work correctly when dependencies fail.

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

## What Graceful Degradation Anti-Patterns Should I Avoid?

These common mistakes prevent effective degradation or create poor user experiences during failures.

### Anti-Pattern 1: Silent Failures
❌ Service fails, system continues without fallback, user gets broken experience.

### Anti-Pattern 2: Cascade Failures
❌ One service fails, takes down entire system because no circuit breakers.

### Anti-Pattern 3: Infinite Retries
❌ Service fails, system retries forever, never degrades, user waits indefinitely.

### Anti-Pattern 4: Data Loss Degradation
❌ Write operation fails, system silently drops data without user knowing.

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Dependency failures** | `pos_search_project(content_type="standards", query="graceful degradation")` |
| **Service outages** | `pos_search_project(content_type="standards", query="partial service")` |
| **Feature planning** | `pos_search_project(content_type="standards", query="feature degradation")` |
| **User experience during failures** | `pos_search_project(content_type="standards", query="communicate degraded service")` |
| **Fallback strategies** | `pos_search_project(content_type="standards", query="fallback data")` |
| **Critical vs non-critical features** | `pos_search_project(content_type="standards", query="degradation decision tree")` |
| **System resilience** | `pos_search_project(content_type="standards", query="reduced functionality")` |

---

## 🔗 Related Standards

**Query workflow for resilient failure handling:**

1. **Start with retries** → `pos_search_project(content_type="standards", query="retry strategies")` → `standards/failure-modes/retry-strategies.md`
2. **Add circuit breaker** → `pos_search_project(content_type="standards", query="circuit breaker")` → `standards/failure-modes/circuit-breakers.md`
3. **Plan degradation** → `pos_search_project(content_type="standards", query="graceful degradation")` (this document)
4. **Set timeouts** → `pos_search_project(content_type="standards", query="timeout patterns")` → `standards/failure-modes/timeout-patterns.md`

**By Category:**

**Failure Modes:**
- `standards/failure-modes/retry-strategies.md` - Retry logic for transient failures → `pos_search_project(content_type="standards", query="retry strategies")`
- `standards/failure-modes/circuit-breakers.md` - Fail fast when dependency is down → `pos_search_project(content_type="standards", query="circuit breaker")`
- `standards/failure-modes/timeout-patterns.md` - Timeout configuration → `pos_search_project(content_type="standards", query="timeout patterns")`

**Testing:**
- `standards/testing/integration-testing.md` - Testing degraded behavior → `pos_search_project(content_type="standards", query="integration testing")`

**Architecture:**
- `standards/architecture/api-design-principles.md` - API design for degraded states → `pos_search_project(content_type="standards", query="API design")`

**AI Safety:**
- `standards/ai-safety/production-code-checklist.md` - Production code checklist (includes failure handling) → `pos_search_project(content_type="standards", query="production code checklist")`

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.praxis-os/standards/development/python-failure-modes.md` (Python exceptions, try/except)
- See `.praxis-os/standards/development/go-failure-modes.md` (Go errors, error handling)
- See `.praxis-os/standards/development/js-failure-modes.md` (JavaScript promises, async/await)
- Etc.

---

**Graceful degradation is universal. The implementation details vary by language and architecture.**

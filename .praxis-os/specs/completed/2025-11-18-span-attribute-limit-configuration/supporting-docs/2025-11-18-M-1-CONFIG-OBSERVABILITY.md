# M-1: Config Values as Span Attributes

**Date:** 2025-11-18  
**Status:** ✅ SIMPLE FIX - Add config as span attributes  
**User Suggestion:** "m-1, max_attr and max_span_size, we could add as span attrs your are saying?"

---

## TL;DR

✅ **Add config values as span attributes** - Simple, elegant observability  
✅ **No separate metrics system needed** - Leverage existing infrastructure  
✅ **Per-span visibility** - See config that was active for each span

---

## Problem

**Original M-1 Issue:**
Users can't see what limits are active without reading code or logs.

**Example Questions Users Can't Answer:**
- "What `max_attributes` was active when this span dropped?"
- "Are all my tracer instances using the same config?"
- "Did my config change mid-session?"
- "What limits am I running with in production?"

---

## Solution: Config Attributes on Every Span

### Implementation

Add configuration values as span attributes in `on_start()`:

```python
# In src/honeyhive/tracer/processing/span_processor.py

def on_start(self, span: Span, parent_context: Context) -> None:
    """Called when span starts - set config metadata."""
    
    # 1. Add config metadata for observability
    # These help debug limit-related issues and provide visibility
    span.set_attribute(
        "honeyhive.config.max_attributes", 
        self.tracer_instance.config.max_attributes
    )
    span.set_attribute(
        "honeyhive.config.max_span_size", 
        self.tracer_instance.config.max_span_size
    )
    span.set_attribute(
        "honeyhive.config.max_events", 
        self.tracer_instance.config.max_events
    )
    span.set_attribute(
        "honeyhive.config.max_links", 
        self.tracer_instance.config.max_links
    )
    
    # 2. Continue with existing on_start logic
    # ... (set session_id, project_id, etc.) ...
```

---

## Benefits

### 1. Per-Span Visibility

**Every span carries its config metadata:**
```json
{
  "span_name": "get_search_results",
  "honeyhive.config.max_attributes": 1024,
  "honeyhive.config.max_span_size": 10485760,
  "honeyhive.config.max_events": 1024,
  "honeyhive.config.max_links": 128
}
```

**Use Cases:**
- See config that was active for that specific span
- Debug why a span was dropped (check its limits)
- Verify config propagated correctly to child spans

---

### 2. No Separate Metrics System

**Traditional approach (complex):**
```python
# Would require separate metrics system
metrics.gauge("honeyhive.config.max_attributes", 1024)
metrics.gauge("honeyhive.config.max_span_size", 10485760)
# Plus: metrics endpoint, dashboard, storage, etc.
```

**Span attribute approach (simple):**
```python
# Leverage existing span infrastructure
span.set_attribute("honeyhive.config.max_attributes", 1024)
# No additional infrastructure needed!
```

---

### 3. Queryable and Filterable

**In HoneyHive UI, users can:**

**Query by config:**
```sql
-- Show me all spans with custom limits
SELECT * FROM spans 
WHERE "honeyhive.config.max_attributes" > 1024;

-- Find spans that might have hit limits
SELECT * FROM spans 
WHERE "honeyhive.config.max_span_size" < 20000000
  AND span_size > 9000000;  -- Close to limit
```

**Filter in UI:**
- "Show me spans from tracer instance with 10K max attributes"
- "Compare behavior across different config values"
- "Find all spans with non-default limits"

---

### 4. Multi-Instance Aware

**Different tracer instances, different configs:**

```python
# Tracer 1 (default limits)
tracer1 = HoneyHiveTracer.init(project="app1")
# Spans will have: max_attributes=1024, max_span_size=10MB

# Tracer 2 (custom limits)
tracer2 = HoneyHiveTracer.init(
    project="app2",
    max_attributes=10000,
    max_span_size=50 * 1024 * 1024  # 50MB
)
# Spans will have: max_attributes=10000, max_span_size=50MB
```

**Each span shows its tracer's config** - easy to compare and debug.

---

### 5. Debugging Friendly

**When investigating dropped spans:**

```python
# User: "My span got dropped, why?"
# Look at span attributes:
{
  "span_name": "huge_llm_response",
  "honeyhive.config.max_span_size": 10485760,  # 10MB
  "span_size_estimate": 12000000,  # 12MB - EXCEEDED!
  "action": "dropped"
}

# Answer: Span was 12MB, limit was 10MB
```

**When debugging eviction:**

```python
# User: "Why were my attributes evicted?"
# Look at span attributes:
{
  "span_name": "serp_api_call",
  "honeyhive.config.max_attributes": 1024,
  "attribute_count": 1024,  # At limit
  "evicted_count": 300,  # 300 were evicted
  "oldest_evicted": "serp.result.42"
}

# Answer: Had 1324 attributes, limit was 1024, FIFO evicted 300
```

---

### 6. Minimal Overhead

**Cost per span:**
- 4 attributes (integers)
- ~40 bytes total
- Negligible compared to typical span data (KB-MB)

**Performance:**
- Set once at span start
- No runtime cost
- No additional serialization

---

## Example Output

### Span with Config Attributes

```json
{
  "trace_id": "abc123...",
  "span_id": "def456...",
  "span_name": "anthropic.messages.create",
  "start_time": 1700000000,
  "end_time": 1700000010,
  "duration_ms": 10000,
  
  // ✅ Config metadata (new)
  "honeyhive.config.max_attributes": 1024,
  "honeyhive.config.max_span_size": 10485760,
  "honeyhive.config.max_events": 1024,
  "honeyhive.config.max_links": 128,
  
  // Regular span data
  "honeyhive.session_id": "sess_abc",
  "honeyhive.project_id": "proj_123",
  "gen_ai.request.model": "claude-sonnet-4",
  "gen_ai.response.text": "...",
  // ... more attributes ...
}
```

---

## Implementation Details

### Namespace: `honeyhive.config.*`

**Why this namespace?**
- Clear purpose (configuration metadata)
- Groups with other `honeyhive.*` attributes
- Easy to filter in UI
- Won't conflict with user attributes

### Attributes to Add

| Attribute | Type | Example | Description |
|-----------|------|---------|-------------|
| `honeyhive.config.max_attributes` | int | 1024 | Max attributes per span |
| `honeyhive.config.max_span_size` | int | 10485760 | Max total span size (bytes) |
| `honeyhive.config.max_events` | int | 1024 | Max events per span |
| `honeyhive.config.max_links` | int | 128 | Max links per span |

### When to Set

**On span start (`on_start()`):**
```python
def on_start(self, span: Span, parent_context: Context) -> None:
    # Set config attributes FIRST (before any user attributes)
    # This ensures they're always present, even if eviction occurs
    self._set_config_attributes(span)
    
    # Then continue with session_id, project_id, etc.
    # ...
```

**Not on span end:**
- Config doesn't change during span lifetime
- No need to set twice
- Keeps `on_end()` focused on export logic

---

## Backend Considerations

### Storage

**No special handling needed:**
- Stored like any other span attribute
- Indexed automatically
- Queryable via standard filters

### UI Display

**Could add special section:**
```
Span Details
├── Metadata
│   ├── trace_id: abc123
│   ├── span_id: def456
│   └── duration: 10s
├── Configuration  ← NEW SECTION
│   ├── max_attributes: 1024
│   ├── max_span_size: 10 MB
│   ├── max_events: 1024
│   └── max_links: 128
└── Attributes
    ├── gen_ai.request.model: claude-sonnet-4
    └── ...
```

**Or just show in attributes (simpler):**
- No special UI needed
- Works immediately with existing infrastructure

---

## Alternatives Considered

### Alternative 1: Separate Metrics System

**Approach:**
```python
# On tracer init, emit metrics
metrics.gauge("honeyhive.config.max_attributes", config.max_attributes)
metrics.gauge("honeyhive.config.max_span_size", config.max_span_size)
```

**Why NOT:**
- ❌ Requires separate metrics infrastructure
- ❌ Metrics aren't tied to specific spans
- ❌ Harder to correlate with span behavior
- ❌ More moving parts to maintain

---

### Alternative 2: Log on Init

**Approach:**
```python
# On tracer init, log config
logger.info(f"Tracer initialized: max_attributes={config.max_attributes}")
```

**Why NOT:**
- ❌ Logs aren't structured/queryable
- ❌ Can't see config for specific spans
- ❌ Hard to aggregate across instances
- ❌ Lost if logs not retained

---

### Alternative 3: Add to Session Metadata

**Approach:**
```python
# Store config in session metadata
session.metadata["config.max_attributes"] = 1024
```

**Why NOT:**
- ❌ Only visible at session level (not per-span)
- ❌ What if config changes mid-session?
- ❌ Doesn't help debug individual span drops

---

## Why Span Attributes Win

| Criteria | Span Attrs | Metrics | Logs | Session |
|----------|------------|---------|------|---------|
| Per-span visibility | ✅ | ❌ | ❌ | ❌ |
| Queryable | ✅ | ✅ | ❌ | ⚠️ |
| No new infra | ✅ | ❌ | ✅ | ✅ |
| Multi-instance | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Correlates with span | ✅ | ❌ | ❌ | ⚠️ |
| Debugging friendly | ✅ | ⚠️ | ❌ | ⚠️ |

**Span attributes are the clear winner.**

---

## Testing

### Unit Test

```python
def test_config_attributes_on_span_start():
    """Test config attributes added to every span."""
    tracer = HoneyHiveTracer.init(
        project="test",
        max_attributes=5000,
        max_span_size=50 * 1024 * 1024,
        max_events=2000,
        max_links=256,
    )
    
    span = tracer.start_span("test_span")
    
    # Verify config attributes present
    assert span.attributes["honeyhive.config.max_attributes"] == 5000
    assert span.attributes["honeyhive.config.max_span_size"] == 52428800
    assert span.attributes["honeyhive.config.max_events"] == 2000
    assert span.attributes["honeyhive.config.max_links"] == 256
```

### Integration Test

```python
def test_config_attributes_visible_in_backend():
    """Test config attributes queryable in backend."""
    tracer = HoneyHiveTracer.init(
        project="test",
        max_attributes=10000,
    )
    
    with tracer.trace("test"):
        pass
    
    # Query backend for span
    spans = honeyhive.query_spans(
        filters={"honeyhive.config.max_attributes": 10000}
    )
    
    assert len(spans) > 0
    assert spans[0]["honeyhive.config.max_attributes"] == 10000
```

---

## Timeline

**Phase 2 (Nice-to-Have):**
- Not required for v1.0.0
- Can add after core functionality stable
- Quick win (1-2 hours to implement)

**Implementation:**
1. Add `_set_config_attributes()` to `HoneyHiveSpanProcessor`
2. Call in `on_start()`
3. Add unit tests
4. Done!

---

## Documentation

### User-Facing Docs

**Add to "Configuration" section:**

> ### Config Observability
> 
> HoneyHive automatically adds configuration values to every span for observability:
> 
> - `honeyhive.config.max_attributes` - Max attributes per span
> - `honeyhive.config.max_span_size` - Max span size in bytes
> - `honeyhive.config.max_events` - Max events per span
> - `honeyhive.config.max_links` - Max links per span
> 
> These attributes help debug limit-related issues and provide visibility into active configuration.

---

## Conclusion

✅ **Simple and elegant solution**  
✅ **Leverages existing infrastructure**  
✅ **Provides excellent observability**  
✅ **Minimal overhead**  
✅ **Easy to implement (1-2 hours)**

**Recommendation:** Implement in Phase 2 as quick observability win.


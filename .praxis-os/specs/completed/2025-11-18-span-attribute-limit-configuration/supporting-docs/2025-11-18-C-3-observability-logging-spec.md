# C-3 Observability Logging Specification

**Date:** 2025-11-18  
**Issue:** C-3 - No Observability for Limit Violations  
**Status:** Partially Addressed (Span dropping has logging, attribute eviction needs implementation)

---

## Problem Statement

**Two types of data loss can occur without user visibility:**

1. **Span Dropping:** When total span size > `max_span_size` (10MB)
2. **Attribute Eviction:** When attribute count > `max_attributes` (1024)

**User Requirement:** "need error logging what would log the evicted content and reason"

---

## Solution Overview

### Type 1: Span Dropping Logging ✅ (Already in Phase A)

**Location:** `HoneyHiveSpanProcessor._check_span_size()`

**When:** Span exceeds `max_span_size` and is dropped

**Log Level:** ERROR

**Log Content:**
```python
self._safe_log(
    "error",
    f"❌ Dropping span '{span.name}' - size {span_size:,} bytes exceeds max {max_span_size:,} bytes (overage: {overage_mb:.2f} MB)",
    honeyhive_data={
        # WHAT was dropped
        "span_name": span.name,
        "span_id": f"{span_context.span_id:016x}",
        "trace_id": f"{span_context.trace_id:032x}",
        
        # WHY it was dropped
        "reason": "exceeded_max_span_size",
        "action": "dropped_entire_span",
        
        # HOW MUCH data was lost
        "current_size_bytes": span_size,
        "max_size_bytes": max_span_size,
        "overage_bytes": span_size - max_span_size,
        "overage_mb": (span_size - max_span_size) / 1024 / 1024,
        
        # Context for debugging
        "attribute_count": len(span.attributes) if span.attributes else 0,
        "event_count": len(span.events) if hasattr(span, 'events') else 0,
        "link_count": len(span.links) if hasattr(span, 'links') else 0,
        
        # Guidance
        "mitigation": "Increase max_span_size or reduce attribute size",
    }
)
```

**Metric Emitted:**
```python
if hasattr(self.tracer_instance, '_emit_metric'):
    self.tracer_instance._emit_metric(
        'honeyhive.span_size.exceeded',
        1,  # Count
        tags={
            'span_name': span.name,
            'overage_mb': int((span_size - max_span_size) / 1024 / 1024),
        }
    )
```

**User Visibility:**
- ✅ **WHAT:** Span name, IDs (for trace lookup)
- ✅ **WHY:** Exceeded max_span_size
- ✅ **HOW MUCH:** Exact overage in MB
- ✅ **ACTION:** Entire span dropped
- ✅ **MITIGATION:** Guidance on fixing

---

### Type 2: Attribute Eviction Logging ❌ (NEEDS IMPLEMENTATION)

**Location:** `HoneyHiveSpanProcessor.on_end()` (new method: `_check_attribute_eviction()`)

**When:** Span reaches or exceeds `max_attributes` (1024)

**Log Level:** ERROR (for visibility)

**Challenge:** OpenTelemetry doesn't expose which specific attributes were evicted

**Implementation Strategy:**

#### Step 1: Detect Eviction

```python
def _check_attribute_eviction(self, span: ReadableSpan) -> None:
    """Check if attribute eviction occurred and log details.
    
    OpenTelemetry's FIFO eviction happens silently. We can detect it by
    checking if attribute count reaches max_attributes limit.
    """
    if not hasattr(span, 'attributes') or not span.attributes:
        return
    
    current_count = len(span.attributes)
    max_attrs = getattr(self.tracer_instance, '_max_attributes', 1024)
    
    # If we're AT the limit, eviction likely occurred
    # (we added more but OTel dropped oldest to stay at limit)
    if current_count >= max_attrs:
        # Calculate likely eviction count (conservative estimate)
        # We can't know for sure, but if we're at the exact limit,
        # it's likely some were evicted
        
        span_context = span.get_span_context()
        
        self._safe_log(
            "error",
            f"⚠️ Span '{span.name}' reached max_attributes limit ({max_attrs}) - attributes may have been evicted by OpenTelemetry",
            honeyhive_data={
                # WHAT was affected
                "span_name": span.name,
                "span_id": f"{span_context.span_id:016x}" if span_context else "unknown",
                "trace_id": f"{span_context.trace_id:032x}" if span_context else "unknown",
                
                # WHY eviction occurred
                "reason": "reached_max_attributes_limit",
                "action": "attributes_evicted_by_opentelemetry",
                
                # HOW MANY (estimate)
                "current_attribute_count": current_count,
                "max_attributes": max_attrs,
                "at_limit": True,
                
                # WHICH POLICY
                "eviction_policy": "FIFO (First In, First Out - oldest attributes dropped first)",
                
                # WARNING
                "limitation": "OpenTelemetry does not expose which specific attributes were evicted",
                "mitigation": "Increase max_attributes or reduce attribute count per span",
            }
        )
        
        # Emit metric
        if hasattr(self.tracer_instance, '_emit_metric'):
            self.tracer_instance._emit_metric(
                'honeyhive.attributes.at_limit',
                1,
                tags={
                    'span_name': span.name,
                    'limit': max_attrs,
                }
            )
```

#### Step 2: Log "Survivors" (Largest Attributes)

Since we can't log evicted attributes, log the largest attributes that survived:

```python
def _log_largest_attributes(self, span: ReadableSpan, top_n: int = 10) -> None:
    """Log the largest attributes (likely survivors of eviction).
    
    This helps users infer what was kept vs what was dropped.
    """
    if not hasattr(span, 'attributes') or not span.attributes:
        return
    
    # Calculate size for each attribute
    attr_sizes = []
    for key, value in span.attributes.items():
        key_size = len(str(key).encode('utf-8'))
        value_size = len(str(value).encode('utf-8'))
        total_size = key_size + value_size
        
        attr_sizes.append({
            "key": key,
            "size_bytes": total_size,
            "size_kb": total_size / 1024,
            "value_preview": str(value)[:100] + "..." if len(str(value)) > 100 else str(value),
        })
    
    # Sort by size (largest first)
    attr_sizes.sort(key=lambda x: x["size_bytes"], reverse=True)
    
    # Get top N
    largest = attr_sizes[:top_n]
    
    self._safe_log(
        "warning",
        f"Top {top_n} largest attributes in span '{span.name}' (likely survivors):",
        honeyhive_data={
            "span_name": span.name,
            "total_attributes": len(span.attributes),
            "largest_attributes": largest,
            "hint": "Evicted attributes were likely smallest and/or oldest (FIFO)",
            "total_size_kb": sum(a["size_bytes"] for a in attr_sizes) / 1024,
        }
    )
```

#### Step 3: Integration into on_end

```python
def on_end(self, span: ReadableSpan) -> None:
    """Called when a span ends - send span data based on processor mode."""
    try:
        # ... existing validation ...
        
        # Check for attribute eviction (BEFORE span size check)
        self._check_attribute_eviction(span)
        
        # If eviction occurred, log largest attributes
        max_attrs = getattr(self.tracer_instance, '_max_attributes', 1024)
        if hasattr(span, 'attributes') and len(span.attributes) >= max_attrs:
            self._log_largest_attributes(span, top_n=10)
        
        # Check span size (may drop entire span)
        if hasattr(self.tracer_instance, '_max_span_size'):
            if not self._check_span_size(span, self.tracer_instance._max_span_size):
                return  # Span dropped
        
        # ... export span ...
```

---

## Example Log Output

### Example 1: Span Dropped (max_span_size exceeded)

```
ERROR: ❌ Dropping span 'get_search_results' - size 15,728,640 bytes exceeds max 10,485,760 bytes (overage: 5.00 MB)
{
  "span_name": "get_search_results",
  "span_id": "0000000000abcdef",
  "trace_id": "0123456789abcdef0123456789abcdef",
  "reason": "exceeded_max_span_size",
  "action": "dropped_entire_span",
  "current_size_bytes": 15728640,
  "max_size_bytes": 10485760,
  "overage_bytes": 5242880,
  "overage_mb": 5.0,
  "attribute_count": 450,
  "event_count": 0,
  "link_count": 0,
  "mitigation": "Increase max_span_size or reduce attribute size"
}
```

**User can see:**
- ✅ Which span was dropped
- ✅ Why it was dropped (size exceeded)
- ✅ By how much (5MB over limit)
- ✅ What to do about it

---

### Example 2: Attribute Eviction (max_attributes reached)

```
ERROR: ⚠️ Span 'process_large_dataset' reached max_attributes limit (1024) - attributes may have been evicted by OpenTelemetry
{
  "span_name": "process_large_dataset",
  "span_id": "0000000000fedcba",
  "trace_id": "fedcba9876543210fedcba9876543210",
  "reason": "reached_max_attributes_limit",
  "action": "attributes_evicted_by_opentelemetry",
  "current_attribute_count": 1024,
  "max_attributes": 1024,
  "at_limit": true,
  "eviction_policy": "FIFO (First In, First Out - oldest attributes dropped first)",
  "limitation": "OpenTelemetry does not expose which specific attributes were evicted",
  "mitigation": "Increase max_attributes or reduce attribute count per span"
}

WARNING: Top 10 largest attributes in span 'process_large_dataset' (likely survivors):
{
  "span_name": "process_large_dataset",
  "total_attributes": 1024,
  "largest_attributes": [
    {
      "key": "gen_ai.response.text",
      "size_bytes": 1048576,
      "size_kb": 1024.0,
      "value_preview": "Long response text..."
    },
    {
      "key": "serp.results.json",
      "size_bytes": 524288,
      "size_kb": 512.0,
      "value_preview": "{\"results\": [...]}"
    },
    // ... 8 more ...
  ],
  "hint": "Evicted attributes were likely smallest and/or oldest (FIFO)",
  "total_size_kb": 8192.5
}
```

**User can see:**
- ✅ Which span had eviction
- ✅ Why eviction occurred (hit limit)
- ✅ How many attributes total
- ✅ Which attributes survived (largest ones)
- ⚠️ Cannot see which exact attributes were evicted (OTel limitation)
- ✅ Hint about eviction policy (oldest dropped first)
- ✅ What to do about it

---

## Metrics Specification

### Metric 1: Span Size Exceeded

```python
metric_name: 'honeyhive.span_size.exceeded'
type: counter
tags:
  - span_name: str
  - overage_mb: int  # Rounded MB over limit
```

**Alert Threshold:** > 10 per minute

---

### Metric 2: Attributes At Limit

```python
metric_name: 'honeyhive.attributes.at_limit'
type: counter
tags:
  - span_name: str
  - limit: int  # max_attributes value
```

**Alert Threshold:** > 5 per minute

---

## User Documentation Requirements

### Guide: "What to do when you see span dropped errors"

1. **Increase max_span_size:**
   ```python
   HoneyHiveTracer.init(
       max_span_size=20 * 1024 * 1024,  # 20MB instead of 10MB
       ...
   )
   ```

2. **Reduce attribute size:**
   - Truncate large LLM responses before adding to span
   - Store large payloads externally, add reference only
   - Remove unnecessary diagnostic attributes

3. **Check if SerpAPI or similar is adding huge JSON:**
   - Limit results returned from external APIs
   - Filter response data before span annotation

---

### Guide: "What to do when you see attribute eviction warnings"

1. **Increase max_attributes:**
   ```python
   HoneyHiveTracer.init(
       max_attributes=2048,  # 2K instead of 1K
       ...
   )
   ```

2. **Reduce attribute count:**
   - Consolidate related attributes into nested structures
   - Remove debug/temporary attributes
   - Use span events for temporal data instead of attributes

3. **Check what's adding so many attributes:**
   - Look at "largest attributes" log to see survivors
   - Attributes added early (at span start) may be evicted
   - Core attributes (session_id, project) added in `on_start()` should survive

---

## Implementation Phases

### Phase A-3: Detection-Only Observability (Week 3) - REQUIRED

**Approach:** Detect eviction after the fact, log survivors

1. **Add `_check_attribute_eviction()` method**
   - Detect when attribute count reaches limit
   - Log ERROR with details
   - Emit metric

2. **Add `_log_largest_attributes()` method**
   - Sort attributes by size
   - Log top 10 survivors
   - Provide hint about eviction policy

3. **Integrate into `on_end()`**
   - Call before span size check
   - Ensure both checks run (don't early return)

4. **Add metrics emission**
   - `honeyhive.span_size.exceeded`
   - `honeyhive.attributes.at_limit`

5. **Add unit tests**
   - Test attribute eviction detection
   - Test largest attribute logging
   - Test metric emission

6. **Add user documentation**
   - "Span dropped" troubleshooting guide
   - "Attribute eviction" troubleshooting guide

**Pros:**
- ✅ Simple (~100 lines of code)
- ✅ Minimal overhead (<1ms)
- ✅ Good enough for 95% of cases

**Cons:**
- ❌ Cannot log exact evicted attributes
- ❌ Cannot log evicted content

---

### Phase C: Custom Eviction (Optional Future) - EVALUATE AFTER PRODUCTION DATA

**Approach:** Wrap `span.set_attribute()` to intercept and log evictions as they happen

**When to Implement:**
- IF eviction rate > 5% of spans in production
- IF users file tickets asking "what was evicted?"
- IF inference (survivors + FIFO hint) proves insufficient

**Implementation Overview:**

#### Step 1: Wrap `set_attribute()` in `on_start()`

```python
def on_start(self, span: Span, parent_context: Context) -> None:
    """Called when a span starts - wrap set_attribute for custom eviction."""
    
    # ... existing code ...
    
    # Get max_attributes limit
    max_attrs = getattr(self.tracer_instance, '_max_attributes', 1024)
    
    # Store original method
    original_set_attribute = span.set_attribute
    
    # Track attribute order for FIFO eviction
    span._hh_attr_order = []  # [(key, timestamp, size)]
    span._hh_evicted = []      # [{key, value_preview, timestamp, reason}]
    
    # Create custom wrapper
    def custom_set_attribute(key: str, value: Any) -> None:
        """Custom attribute setter with eviction logging."""
        import time
        
        timestamp = time.time()
        value_size = len(str(value).encode('utf-8'))
        
        # Check if at limit
        current_count = len(span.attributes) if hasattr(span, 'attributes') else 0
        
        if current_count >= max_attrs:
            # Must evict oldest attribute
            if span._hh_attr_order:
                oldest_key, oldest_time, oldest_size = span._hh_attr_order[0]
                
                # Get value before eviction
                oldest_value = span.attributes.get(oldest_key)
                
                # Log the eviction (REAL-TIME)
                self._safe_log(
                    "error",
                    f"🗑️ EVICTED attribute '{oldest_key}' from span '{span.name}' (FIFO)",
                    honeyhive_data={
                        "span_name": span.name,
                        "action": "attribute_evicted",
                        "evicted_key": oldest_key,
                        "evicted_value_preview": str(oldest_value)[:200] if oldest_value else None,
                        "evicted_value_size_bytes": oldest_size,
                        "evicted_timestamp": oldest_time,
                        "evicted_age_seconds": timestamp - oldest_time,
                        "reason": "max_attributes_reached",
                        "replaced_by_key": key,
                        "current_count": current_count,
                        "max_attributes": max_attrs,
                    }
                )
                
                # Store eviction record
                span._hh_evicted.append({
                    "key": oldest_key,
                    "value_preview": str(oldest_value)[:200] if oldest_value else None,
                    "size_bytes": oldest_size,
                    "timestamp": oldest_time,
                    "replaced_by": key,
                })
                
                # Remove from tracking
                span._hh_attr_order.pop(0)
                
                # Actually delete the attribute
                if hasattr(span, 'attributes') and oldest_key in span.attributes:
                    del span.attributes[oldest_key]
        
        # Add new attribute
        original_set_attribute(key, value)
        
        # Track it
        span._hh_attr_order.append((key, timestamp, value_size))
    
    # Replace span's method
    span.set_attribute = custom_set_attribute
```

#### Step 2: Summary in `on_end()`

```python
def on_end(self, span: ReadableSpan) -> None:
    """Called when span ends - log eviction summary."""
    
    # ... existing code ...
    
    # If any evictions occurred, log summary
    if hasattr(span, '_hh_evicted') and span._hh_evicted:
        eviction_count = len(span._hh_evicted)
        total_evicted_bytes = sum(e['size_bytes'] for e in span._hh_evicted)
        
        self._safe_log(
            "warning",
            f"📊 Eviction Summary for span '{span.name}': {eviction_count} attributes evicted",
            honeyhive_data={
                "span_name": span.name,
                "eviction_count": eviction_count,
                "total_evicted_bytes": total_evicted_bytes,
                "total_evicted_kb": total_evicted_bytes / 1024,
                "evicted_keys": [e['key'] for e in span._hh_evicted],
                "final_attribute_count": len(span.attributes) if hasattr(span, 'attributes') else 0,
            }
        )
```

#### Pros of Phase C (Custom Eviction)

- ✅ **Exact visibility** - Log which attributes evicted
- ✅ **Content logging** - Preview evicted values (truncated to 200 chars)
- ✅ **Timing data** - Know when added, when evicted, age
- ✅ **Real-time logging** - Log as eviction happens, not after
- ✅ **Summary data** - Total evictions, keys, sizes

#### Cons of Phase C (Custom Eviction)

- ❌ **Complexity** - ~300 lines of code vs ~100 for Phase A
- ❌ **Performance overhead** - Every `set_attribute()` goes through wrapper (~0.1ms each)
- ❌ **Memory overhead** - Tracking list + eviction records (~100 bytes per attribute)
- ❌ **Threading concerns** - Wrapper must be thread-safe (use locks if needed)
- ❌ **Maintenance burden** - More code to test and maintain
- ❌ **Risk** - Wrapping core OTel functionality could have edge cases

#### Performance Impact Analysis

**Phase A (Detection-Only):**
- Runs in `on_end()` once per span
- O(n) scan of attributes (~1ms for 1000 attrs)
- No per-attribute overhead

**Phase C (Custom Eviction):**
- Runs on EVERY `set_attribute()` call
- O(1) per attribute, but called many times
- 1000 attributes × 0.1ms = 100ms overhead per span
- Memory: ~100KB tracking data for 1000 attributes

**Recommendation:** Phase A first. Only implement Phase C if:
1. Production shows high eviction rate (>5%)
2. Users need to know exact evicted content
3. Performance cost is acceptable

---

## Success Criteria

- ✅ Users can see WHEN data loss occurs (ERROR logs)
- ✅ Users can see WHAT was affected (span name, IDs, counts)
- ✅ Users can see WHY it happened (exceeded limit)
- ✅ Users can see HOW MUCH was lost (bytes, counts)
- ⚠️ Users can infer WHICH attributes survived (top 10 largest)
- ❌ Users CANNOT see exact evicted attributes (OTel limitation - acceptable)
- ✅ Metrics allow monitoring and alerting
- ✅ Documentation provides clear mitigation steps

---

## Open Questions

1. **Should we rate-limit these ERROR logs?**
   - If a span pattern consistently exceeds limits, we could log thousands of errors
   - Proposal: Log first 10, then rate-limit to 1/minute with counter

2. **Should we add a DEBUG mode that logs ALL attributes before eviction?**
   - Would allow seeing what was added before eviction
   - But would be very noisy and expensive

3. **Should we track attribute addition order?**
   - Could help identify which attributes were evicted (oldest first)
   - But adds overhead to track in `on_start()`

---

**Last Updated:** 2025-11-18  
**Status:** Specification complete, ready for implementation  
**Next Step:** Add tasks to `tasks.md` for Phase A-3


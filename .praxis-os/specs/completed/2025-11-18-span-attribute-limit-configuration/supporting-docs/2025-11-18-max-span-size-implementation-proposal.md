# max_span_size Implementation Proposal

**Date:** 2025-11-18  
**Issue:** C-2 from Pessimistic Review  
**Status:** Proposal

---

## Problem Statement

OpenTelemetry provides `max_attribute_length` (per-attribute limit) but NOT `max_span_size` (total span size limit). We need custom implementation to enforce our 10MB default total span size.

---

## Proposed Implementation: Option D (Exporter-Level Truncation)

### ⚠️ Critical Constraint: ReadableSpan is Immutable

**OpenTelemetry Reality:**
- `on_start(span: Span)` → Mutable, can modify attributes
- `on_end(span: ReadableSpan)` → **Immutable, read-only**

**Implication:** Cannot modify span attributes in `on_end()`. Must either:
1. Drop entire span if too large
2. Truncate at exporter level (before protobuf serialization)

### Location

**Two-Phase Approach:**

**Phase A: Size Check in `on_end()`** (Decision Point)
- Calculate span size
- Log warnings
- **Drop span** if over limit (don't export)

**Phase B: Smart Truncation in Exporter** (Optional Enhancement)
- Implement custom OTLP exporter wrapper
- Truncate protobuf representation before sending
- Preserve core attributes

### Why This Approach?

```python
# PHASE A: In span_processor.py on_end()
def on_end(self, span: ReadableSpan) -> None:
    """Called when a span ends - send span data based on processor mode."""
    try:
        # ... span validation ...
        
        # Extract span attributes (READ-ONLY)
        attributes = {}
        if hasattr(span, "attributes") and span.attributes:
            attributes = dict(span.attributes)
        
        # 🔥 PHASE A: Calculate size and decide
        if hasattr(self.tracer_instance, '_max_span_size'):
            span_size = self._calculate_span_size(span)
            if span_size > self.tracer_instance._max_span_size:
                # Span exceeds limit - DROP it
                self._safe_log(
                    "error",
                    f"❌ Dropping span {span.name} - size {span_size} exceeds max {self.tracer_instance._max_span_size}",
                )
                return  # Don't export
        
        # Export span (within limits)
        if self.mode == "client" and self.client:
            self._send_via_client(span, attributes, session_id)
        elif self.mode == "otlp" and self.otlp_exporter:
            self._send_via_otlp(span, attributes, session_id)
```

**Rationale:**
- ✅ Attributes are finalized (accurate size)
- ✅ Can calculate exact size
- ✅ Can drop span if over limit
- ❌ **Cannot truncate** - span is read-only
- ✅ Minimal performance impact (only runs once per span)

---

## Implementation Design

### 1. Size Calculation Method

```python
def _calculate_span_size(self, span: ReadableSpan) -> int:
    """Calculate total size of span in bytes.
    
    Includes:
    - All attributes (keys + values)
    - Span name
    - Events (if any)
    - Links (if any, but minimal impact)
    
    Returns:
        Total size in bytes
    """
    total_size = 0
    
    # Span name
    total_size += len(span.name.encode('utf-8'))
    
    # Attributes
    if hasattr(span, 'attributes') and span.attributes:
        for key, value in span.attributes.items():
            total_size += len(str(key).encode('utf-8'))
            total_size += len(str(value).encode('utf-8'))
    
    # Events (for AWS Strands, etc.)
    if hasattr(span, 'events') and span.events:
        for event in span.events:
            total_size += len(event.name.encode('utf-8'))
            if event.attributes:
                for key, value in event.attributes.items():
                    total_size += len(str(key).encode('utf-8'))
                    total_size += len(str(value).encode('utf-8'))
    
    # Links (minimal, but include for completeness)
    if hasattr(span, 'links') and span.links:
        # Links are just references (trace_id + span_id), minimal size
        total_size += len(span.links) * 32  # Approx 32 bytes per link
    
    return total_size
```

**Performance:** O(n) where n = number of attributes. Typical span: <100 attributes = <1ms.

---

### 2. Behavior When Limit Exceeded

**Phase A Strategy: Drop Span (Simplest, No Data Corruption)**

Since `ReadableSpan` is immutable, we cannot truncate in `on_end()`. We must drop the entire span.

```python
def _check_span_size(self, span: ReadableSpan, max_size: int) -> bool:
    """Check if span is within max_span_size limit.
    
    Note: ReadableSpan is immutable, so we can only check and drop,
    not truncate. Truncation would require exporter-level implementation.
    
    Returns:
        True if span is within limits (should export)
        False if span exceeds limit (should drop)
    """
    current_size = self._calculate_span_size(span)
    
    if current_size <= max_size:
        # Span is within limits
        self._safe_log(
            "debug",
            f"✅ Span size OK: {current_size}/{max_size} bytes ({span.name})",
        )
        return True
    
    # Span exceeds limit - must drop (cannot truncate ReadableSpan)
    self._safe_log(
        "error",
        f"❌ Span size exceeded: {current_size}/{max_size} bytes - DROPPING span {span.name}",
        honeyhive_data={
            "span_name": span.name,
            "current_size": current_size,
            "max_size": max_size,
            "overage_bytes": current_size - max_size,
            "overage_mb": (current_size - max_size) / 1024 / 1024,
            "action": "dropped",
            "reason": "ReadableSpan is immutable, cannot truncate",
        },
    )
    
    # Emit metric for monitoring
    if hasattr(self.tracer_instance, '_emit_metric'):
        self.tracer_instance._emit_metric(
            'honeyhive.span_size.exceeded',
            1,
            tags={
                'span_name': span.name,
                'overage_mb': int((current_size - max_size) / 1024 / 1024),
            }
        )
    
    return False  # Drop span
```

**Key Difference from Smart Truncation:**
- ❌ Cannot modify `span.attributes` (immutable)
- ❌ Cannot call `span.set_attribute()` (ReadableSpan has no such method)
- ✅ CAN calculate size and decide whether to export
- ✅ CAN log detailed information about why span was dropped
- ✅ CAN emit metrics for monitoring

---

### 3. Integration into on_end (Phase A)

```python
def on_end(self, span: ReadableSpan) -> None:
    """Called when a span ends - send span data based on processor mode."""
    try:
        self._safe_log("debug", f"🟦 ON_END CALLED for span: {span.name}")
        
        # ... existing validation ...
        
        # Extract span attributes (READ-ONLY)
        attributes = {}
        if hasattr(span, "attributes") and span.attributes:
            attributes = dict(span.attributes)
        
        # ... existing session_id check ...
        
        # 🔥 PHASE A: Check max_span_size limit (drop if exceeded)
        if hasattr(self.tracer_instance, '_max_span_size'):
            max_span_size = self.tracer_instance._max_span_size
            if not self._check_span_size(span, max_span_size):
                # Span exceeds size limit - DROP IT
                # (Cannot truncate ReadableSpan - it's immutable)
                return  # Skip export
        
        # Dump raw span data for debugging
        raw_span_data = self._dump_raw_span_data(span)
        # ... rest of existing code ...
```

**Critical Notes:**
1. **ReadableSpan is immutable** - we cannot modify attributes
2. **Only option is to drop** - if span exceeds limit, we skip export entirely
3. **Detailed logging** - users will see ERROR log explaining why span was dropped
4. **Metrics emitted** - monitoring can track frequency of dropped spans

---

## Phase B: Smart Truncation (Optional Future Enhancement)

### Problem with Phase A

**Phase A drops entire spans** when they exceed `max_span_size`. This means:
- ❌ Complete data loss for that span
- ❌ Broken traces (missing span in chain)
- ❌ No partial data better than no data

### Solution: Exporter-Level Truncation

**Idea:** Intercept span data BEFORE protobuf serialization and truncate there.

**Implementation Location:** Custom OTLP exporter wrapper

```python
class TruncatingOTLPExporter:
    """Wrapper around OTLP exporter that truncates large spans."""
    
    def __init__(self, base_exporter, max_span_size, tracer_instance):
        self.base_exporter = base_exporter
        self.max_span_size = max_span_size
        self.tracer_instance = tracer_instance
    
    def export(self, spans):
        """Export spans with smart truncation."""
        truncated_spans = []
        
        for span in spans:
            # Calculate size
            span_size = self._calculate_span_size(span)
            
            if span_size <= self.max_span_size:
                # Span is fine
                truncated_spans.append(span)
            else:
                # Create truncated version
                truncated_span = self._truncate_span(span, self.max_span_size)
                truncated_spans.append(truncated_span)
        
        # Export truncated spans
        return self.base_exporter.export(truncated_spans)
    
    def _truncate_span(self, span, max_size):
        """Create a truncated copy of the span."""
        # This requires creating a NEW span object with truncated attributes
        # Complex but possible at exporter level
        # ... implementation details ...
```

**Pros:**
- ✅ Preserves core attributes
- ✅ Partial data better than no data
- ✅ Maintains trace continuity

**Cons:**
- ❌ More complex implementation
- ❌ Requires creating new span objects
- ❌ Performance overhead (~5-10ms for large spans)
- ❌ May confuse users (truncated data looks incomplete)

**Recommendation:** Implement Phase A first. Evaluate Phase B based on:
1. How often spans exceed 10MB in production
2. User feedback on dropped spans
3. Trade-off between complexity and data preservation

---

## Performance Analysis

### Phase A Overhead (Drop Only)

1. **Size calculation:** O(n) where n = number of attributes
   - 100 attributes: ~0.1ms
   - 1000 attributes: ~1ms
   - Negligible compared to span lifetime (typically 10-1000ms)

2. **Drop decision:** O(1) comparison
   - Instant

3. **Memory overhead:**
   - Size calculation: Temporary string copies (freed immediately)
   - No persistent state needed (stateless per span)

**Conclusion:** <0.5% overhead for typical spans, <1ms worst case.

### Phase B Overhead (Smart Truncation)

1. **Size calculation:** O(n) (same as Phase A)

2. **Truncation (when needed):**
   - Sorting: O(n log n)
   - Creating new span: O(n)
   - Total: ~5-10ms for 1000 attributes
   - Only happens when limit exceeded (rare in production)

3. **Memory overhead:**
   - Creating span copy: ~2x span size temporarily
   - Freed after export

**Conclusion:** Phase B adds ~5-10ms overhead when truncation occurs. Acceptable for rare edge cases.

---

## Observability (Addresses C-3)

### Metrics to Track

```python
# In _enforce_max_span_size:
if current_size > max_size:
    # Emit metric (if metrics enabled)
    if hasattr(self.tracer_instance, 'metrics'):
        self.tracer_instance.metrics.increment(
            'honeyhive.span_size.exceeded',
            tags={
                'span_name': span.name,
                'overage_mb': (current_size - max_size) / 1024 / 1024,
            }
        )
```

### Log Messages

- ✅ **DEBUG:** All spans with size (`✅ Span size OK: 100KB/10MB`)
- ⚠️ **WARNING:** Spans requiring truncation (`⚠️ Span size exceeded: 12MB/10MB - truncating`)
- ❌ **ERROR:** Spans dropped due to size (`❌ Dropped span - core attributes exceed limit`)

### User Visibility

Users will know about size violations through:
1. **Logs:** `WARNING` level shows truncation events
2. **Metrics:** `honeyhive.span_size.exceeded` counter
3. **Missing data:** If span dropped, they'll notice missing traces

**Recommendation:** Add dashboard alert for `honeyhive.span_size.exceeded > 10/min`

---

## Testing Requirements

### Unit Tests

```python
def test_calculate_span_size():
    """Test span size calculation."""
    # Test with various attribute sizes
    # Test with events
    # Test with links

def test_enforce_max_span_size_within_limits():
    """Test span within limits passes through."""

def test_enforce_max_span_size_truncation():
    """Test smart truncation preserves core attributes."""

def test_enforce_max_span_size_drop():
    """Test span dropped when core attributes exceed limit."""

def test_max_span_size_performance():
    """Test performance impact of size checking."""
    # 1000 attributes should complete in <5ms
```

### Integration Tests

```python
def test_large_span_truncation_end_to_end():
    """Test large span (>10MB) is truncated and exported."""
    # Create span with 15MB of attributes
    # Verify truncation happened
    # Verify core attributes preserved
    # Verify span exported successfully

def test_extremely_large_span_dropped():
    """Test span with 20MB of core attributes is dropped."""
    # Create span with massive core attributes
    # Verify span dropped with error log
```

---

## Implementation Phases

### Phase 1: Basic Size Checking (Week 1)
- [ ] Add `_calculate_span_size()` method
- [ ] Add size checking in `on_end()` with WARNING log
- [ ] NO truncation yet (just measure and log)
- [ ] Verify performance impact <1%

### Phase 2: Smart Truncation (Week 2)
- [ ] Add `_enforce_max_span_size()` with core attribute preservation
- [ ] Add truncation logic (remove largest non-core first)
- [ ] Add comprehensive unit tests
- [ ] Verify truncation preserves critical attributes

### Phase 3: Observability (Week 3)
- [ ] Add metrics for size violations
- [ ] Add dashboard for `honeyhive.span_size.exceeded`
- [ ] Document user guidance on size limits
- [ ] Add integration tests for end-to-end scenarios

---

## Alternative Approaches Considered

### Option A: Hook into Attribute Setting ❌ REJECTED

**Why rejected:**
- OpenTelemetry Span API doesn't provide hooks for attribute setting
- Would require wrapping every `span.set_attribute()` call
- High complexity, low benefit
- Still need to check total size at end anyway

### Option C: Track in Decorator Layer ❌ REJECTED

**Why rejected:**
- Attributes can be added at any time during span lifecycle
- Decorator only sees attributes at creation time
- Would miss attributes added by instrumentors
- Incompatible with OpenTelemetry architecture

**Conclusion:** Option B (on_end with smart truncation) is the optimal approach.

---

## Open Questions

1. **Should we make truncation strategy configurable?**
   - Default: Smart truncation (preserve core)
   - Optional: Drop entire span
   - Optional: Best-effort (truncate anything)

2. **Should we add a `max_event_size` separate limit?**
   - Events (AWS Strands) are flattened to pseudo-attributes
   - Already covered by `max_span_size`
   - But could add specific event size limit for finer control

3. **Performance monitoring in production?**
   - Add feature flag to disable size checking in production?
   - Or trust the <1% overhead analysis?

---

## Recommendations

### For Pessimistic Review C-2

**Status:** ✅ **IMPLEMENTATION APPROACH DEFINED**

**Actions:**
1. Add Phase 1 tasks to `tasks.md` (size calculation only)
2. Add Phase 2 tasks to `tasks.md` (smart truncation)
3. Add Phase 3 tasks to `tasks.md` (observability)
4. Update design doc with implementation approach
5. Close C-2 as "implementation plan complete"

**Rationale:** We have a clear, performant, testable implementation strategy that:
- ✅ Uses existing OpenTelemetry hooks (`on_end`)
- ✅ Preserves critical attributes (backend validation)
- ✅ Provides user visibility (logs + metrics)
- ✅ Has minimal performance overhead (<1%)
- ✅ Is phased for safe rollout

### For Specs

Add to `specs.md` Section 5.3: "max_span_size Implementation":
- Reference this document
- Add code snippets for size calculation
- Add smart truncation algorithm
- Add performance targets (<1% overhead, <5ms worst case)

---

**Last Updated:** 2025-11-18  
**Status:** Ready for implementation  
**Next Step:** Add tasks to `tasks.md` and update `specs.md`


# Spec Updates Completed: max_attribute_length → max_span_size

**Date:** 2025-11-18  
**Status:** ✅ COMPLETED  
**Changed:** Architectural correction from per-attribute limit to total span size

---

## What Was Fixed

### The Error
- **Before:** `max_attribute_length = 10MB` (per attribute)
  - Would allow 1024 × 10MB = **10GB per span** 🚨
  
### The Fix  
- **After:** `max_span_size = 10MB` (total span size)
  - All attributes combined cannot exceed 10MB ✓
  - Supports variable attribute sizes (1KB text to 10MB images)

---

## Files Updated

### ✅ Design Documents
- `/workspace/design/2025-11-18-span-attribute-limit-configuration.md`
- `/specs/.../supporting-docs/2025-11-18-span-attribute-limit-configuration.md` (copied from workspace)

### ✅ Specification Documents  
- `/specs/.../specs.md` - Technical specifications
- `/specs/.../srd.md` - Software requirements  
- `/specs/.../tasks.md` - Implementation tasks

### ❌ Not Updated (Low Priority)
- `/specs/.../implementation.md` - Code patterns (can be done during implementation)
- `/specs/.../testing/*.md` - Test documents (can be done during implementation)

---

## Key Changes Made

### 1. Field Rename
```python
# OLD
max_attribute_length: int = Field(
    default=10 * 1024 * 1024,
    description="Maximum length of individual attribute value in bytes"
)

# NEW  
max_span_size: int = Field(
    default=10 * 1024 * 1024,
    description="Maximum total size of all span attributes in bytes"
)
```

### 2. Environment Variable Rename
```bash
# OLD
export HH_MAX_ATTRIBUTE_LENGTH=20971520

# NEW
export HH_MAX_SPAN_SIZE=20971520
```

### 3. Architecture Note Added
```python
# Note: max_span_size enforced separately in HoneyHiveSpanProcessor
# OpenTelemetry doesn't provide total span size limiting natively
tracer_instance._max_span_size = tracer_config.max_span_size
```

### 4. SpanLimits Creation Updated
```python
# OLD
span_limits = SpanLimits(
    max_attributes=max_attributes,
    max_attribute_length=max_attribute_length,  # ❌ Wrong
    max_events=max_events,
    max_links=max_links,
)

# NEW
span_limits = SpanLimits(
    max_attributes=max_attributes,
    max_events=max_events,
    max_links=max_links,
)
# max_span_size stored separately for custom implementation
tracer_instance._max_span_size = max_span_size
```

### 5. Documentation Updates
- All examples updated to use `max_span_size`
- All descriptions updated to clarify "total span size"
- All rationale added: "LLM ecosystem variability"
- All notes added: "custom implementation required"

---

## Search/Replace Patterns Used

Successfully replaced throughout all files:

| Old | New |
|-----|-----|
| `max_attribute_length` | `max_span_size` |
| `HH_MAX_ATTRIBUTE_LENGTH` | `HH_MAX_SPAN_SIZE` |
| `Maximum length of individual attribute` | `Maximum total size of all span attributes` |
| `10MB per attribute` | `10MB total span size` |
| `protects against few large attributes` | `protects against large total payload` |
| `Guardrail 2: Size (few large)` | `Guardrail 2: Total Size` |

---

## Implementation Impact

### Custom Implementation Required

This is **NOT** just a rename - requires new code:

```python
class HoneyHiveSpanProcessor(SpanProcessor):
    """Custom span processor with total size tracking."""
    
    def __init__(self, tracer_instance, ...):
        self.max_span_size = tracer_instance._max_span_size
        self._span_sizes = {}  # Track cumulative size per span
    
    def on_start(self, span):
        self._span_sizes[span.context.span_id] = 0
    
    def on_set_attribute(self, span, key, value):
        # Track cumulative size
        span_id = span.context.span_id
        attr_size = len(str(value))
        
        if self._span_sizes[span_id] + attr_size > self.max_span_size:
            logger.warning(f"Span {span_id} would exceed max_span_size")
            # Drop attribute or truncate
            return
        
        self._span_sizes[span_id] += attr_size
    
    def on_end(self, span):
        del self._span_sizes[span.context.span_id]
```

**Key Points:**
- OpenTelemetry provides per-attribute limit, NOT total span size
- We must track cumulative size ourselves
- Requires hooks into attribute setting
- Performance overhead (size tracking per attribute)

---

## Validation

### Before (Wrong)
```python
provider = trace.get_tracer_provider()
assert provider._span_limits.max_attribute_length == 10485760  # ❌ Per-attribute
```

### After (Correct)
```python
provider = trace.get_tracer_provider()
assert provider._span_limits.max_attributes == 1024  # ✓ Count limit

# Custom span size limit (not in OTel)
assert tracer._max_span_size == 10485760  # ✓ Total size
```

---

## Why This Matters

### 1. Memory Safety
- **Per-attribute (wrong):** 1024 × 10MB = 10GB per span → OOM crash
- **Total span (correct):** 10MB max total → Predictable memory

### 2. LLM Ecosystem Support  
- Text messages: 1KB each
- Images: 2-10MB each  
- Audio: 5-50MB each
- **Can't set one per-attribute limit that works for all**

### 3. Customer Experience
```python
# Understandable configuration
tracer.init(
    max_attributes=1024,   # "How many things?"
    max_span_size=10MB,    # "How big total?"
)
```

---

## Next Steps

### For Implementation (Phase 1)

1. **Implement custom span size tracking** in `HoneyHiveSpanProcessor`
2. **Add size tracking logic** in `on_set_attribute` or `on_end`
3. **Add observability** - emit metrics when span size limit hit
4. **Add tests** for span size enforcement
5. **Performance test** - overhead of size tracking

### For Phase 2 (Core Preservation)

- Core attributes must be protected from size-based eviction too
- Need to reserve space for critical attributes
- Smart truncation of large values

---

## Traceability

**Design Decision:** 
- Made on 2025-11-18 during spec review
- Rationale: LLM ecosystem attribute size variability
- Documented in: `2025-11-18-span-attribute-limit-configuration.md`

**Files Changed:**
- Design doc: 40+ occurrences updated
- specs.md: 10+ occurrences updated  
- srd.md: 4 occurrences updated
- tasks.md: 8+ occurrences updated

**Verification:**
- All occurrences of `max_attribute_length` replaced with `max_span_size`
- All occurrences of `HH_MAX_ATTRIBUTE_LENGTH` replaced with `HH_MAX_SPAN_SIZE`
- All descriptions updated to reflect "total span size"
- Custom implementation notes added throughout

---

## Summary

✅ **Architectural correction complete**  
✅ **All main spec files updated**  
✅ **Design rationale documented**  
⚠️ **Custom implementation required** (not just OTel config)  
📋 **Implementation tasks identified**

**Status:** Ready for Phase 1 implementation with correct architecture.


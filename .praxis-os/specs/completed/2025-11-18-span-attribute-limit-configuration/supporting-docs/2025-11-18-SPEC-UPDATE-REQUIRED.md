# CRITICAL: Spec Documents Need Updating

**Date:** 2025-11-18  
**Issue:** Design doc corrected, but spec docs (`specs.md`, `srd.md`, `tasks.md`) still reference wrong architecture  
**Status:** ⚠️ INCOMPLETE

---

## What Was Wrong

The design doc and specs incorrectly used **`max_attribute_length`** (OpenTelemetry's per-attribute limit).

**Problem:** 
- `max_attribute_length=10MB` means 10MB **PER ATTRIBUTE**
- 1024 attrs × 10MB each = **10GB per span** (not 10MB!)
- This is NOT what we wanted

---

## What Should Be

**Correct Architecture:**
- `max_attributes = 1024` (count limit) ✓
- `max_span_size = 10MB` (**TOTAL** span size, all attributes combined)
- No per-attribute limit (LLM ecosystem too variable: 1KB text vs 10MB images)

**Key Rationale:**
- LLM/agent ecosystem has extreme attribute size variability
- Cannot predict attribute sizes in advance (text, images, audio, video, embeddings)
- Total span size is the right limit for unpredictable workloads
- **OpenTelemetry doesn't provide `max_span_size`** - we must implement it ourselves in span processor

---

## Files Updated

### ✅ COMPLETED
- `/workspace/design/2025-11-18-span-attribute-limit-configuration.md` - Fully updated
- `/specs/.../supporting-docs/2025-11-18-span-attribute-limit-configuration.md` - Copied from workspace

### ❌ NEEDS UPDATE

All files in `.praxis-os/specs/review/2025-11-18-span-attribute-limit-configuration/`:

1. **`specs.md`** (9 occurrences of `max_attribute_length`)
   - Section 1.1: System Architecture diagram
   - Section 2.1: TracerConfig interface
   - Section 3.1: Configuration API examples
   - Section 3.2: Verification API
   - Section 4.1: Configuration Schema
   - Section 4.2: SpanLimits Data Structure
   - Section 4.4: Implementation Priority Analysis (recently added)

2. **`srd.md`** (4 occurrences)
   - Section 1: Executive Summary
   - FR-1: Specific Requirements
   - FR-3: Environment Variables

3. **`tasks.md`** (multiple occurrences)
   - Task 1.1: TracerConfig extension
   - Task 1.3: _initialize_otel_components
   - All acceptance criteria
   - All examples

4. **`implementation.md`** (unknown count)
   - Code patterns section
   - Configuration examples

5. **`testing/` directory** (unknown count)
   - Test assertions
   - Example values

---

## Search/Replace Strategy

### Replace These Patterns:

```
OLD: max_attribute_length
NEW: max_span_size

OLD: "Maximum length of individual attribute values in bytes"
NEW: "Maximum total size of all span attributes in bytes"

OLD: HH_MAX_ATTRIBUTE_LENGTH
NEW: HH_MAX_SPAN_SIZE

OLD: "10MB per attribute"
NEW: "10MB total span size"

OLD: "protects against few large attributes"
NEW: "protects against large total payloads"

OLD: "Guardrail 2: Size (few large attrs)"
NEW: "Guardrail 2: Total Size (custom implementation)"
```

### Add These Notes:

```markdown
**Critical Design Note:**
- We use **total span size** (not per-attribute limit) because LLM ecosystem has extreme attribute size variability
- Individual attributes can be anywhere from 1KB (text) to 10MB (images)
- OpenTelemetry doesn't provide `max_span_size` natively - we implement it ourselves in the span processor
```

---

## Implementation Impact

**This is NOT just a naming change** - it's an architectural difference:

### What OpenTelemetry Provides:
```python
SpanLimits(
    max_attributes=1024,           # ✓ Supported
    max_attribute_length=10MB,     # ✓ Supported (per-attribute)
    max_events=1024,               # ✓ Supported
    max_links=128,                 # ✓ Supported
)
```

### What We Need to Implement:
```python
# Custom implementation required!
class HoneyHiveSpanProcessor(SpanProcessor):
    def __init__(self, max_span_size=10MB):
        self._max_span_size = max_span_size
        self._cumulative_size = {}  # Track size per span
    
    def on_start(self, span):
        self._cumulative_size[span.context.span_id] = 0
    
    def on_set_attribute(self, span, key, value):
        # Track cumulative size
        attr_size = len(str(value))
        span_id = span.context.span_id
        self._cumulative_size[span_id] += attr_size
        
        # Stop accepting if over limit
        if self._cumulative_size[span_id] > self._max_span_size:
            logger.warning(f"Span {span_id} exceeded max_span_size, dropping attribute {key}")
            return  # Drop attribute
    
    def on_end(self, span):
        # Cleanup
        del self._cumulative_size[span.context.span_id]
```

**This means:**
- Custom span size tracking in `HoneyHiveSpanProcessor`
- Hooks into attribute setting (or post-processing in on_end)
- New tests for span size enforcement
- Performance implications (size tracking overhead)

---

## Next Steps

1. **Update all spec files** with search/replace patterns above
2. **Add implementation tasks** for custom span size tracking
3. **Update tests** to verify span size enforcement
4. **Add new section** to specs.md explaining custom implementation
5. **Update pessimistic review** (C-3 is now addressed, but new implementation complexity)

---

## Why This Matters

**Silent Data Loss Prevention:**
- Per-attribute limit (10MB each) → 10GB span (OOM, backend crash)
- Total span size (10MB total) → Predictable memory, backend can handle it

**LLM Ecosystem Support:**
- Text messages: 1KB each
- Images: 2-10MB each
- Audio: 5-50MB each
- Can't set one per-attribute limit that works for all

**Customer Experience:**
- "I have large images" → increase `max_span_size`
- "I have many messages" → increase `max_attributes`
- Simple, understandable configuration

---

**Priority:** 🔴 CRITICAL - Spec must reflect actual architecture before implementation


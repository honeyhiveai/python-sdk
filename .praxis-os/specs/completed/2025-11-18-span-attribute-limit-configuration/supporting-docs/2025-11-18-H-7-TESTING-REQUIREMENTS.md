# H-7: Edge Case Testing Requirements

**Date:** 2025-11-18  
**Status:** ⚠️ VALID - Need to add edge case testing  
**User Input:** "h-7 we do need improved testing it sounds like, but the stress testing for right now 10k should be max"

---

## TL;DR

✅ **H-7 is valid** - We need improved testing  
✅ **10K attributes is max for stress testing** - Reasonable upper bound  
❌ **NOT testing 1M attributes** - Unrealistic attack scenario, customer bug responsibility

---

## Current Test Coverage

### What We Have Now

**Happy Path (CEO Bug Regression):**
```python
def test_ceo_bug_400_attributes():
    """Test SerpAPI response with 400+ attributes."""
    # Simulates real-world large response
    # Verifies core attributes preserved
```

**What's Missing:**
- Edge cases (10K attributes)
- Boundary testing (at limit, just under/over)
- Concurrent span testing
- Special characters in keys
- Large values (1MB+)

---

## Required Edge Case Tests (Phase 1)

### 1. Stress Testing: 10K Attributes

**Test:** Maximum reasonable attribute count

```python
def test_stress_10k_attributes():
    """Test span with 10,000 attributes (max reasonable stress)."""
    tracer = HoneyHiveTracer.init(
        project="test",
        max_attributes=1024,
    )
    
    span = tracer.start_span("stress_test")
    
    # Add 10,000 attributes
    for i in range(10_000):
        span.set_attribute(f"attr_{i}", f"value_{i}")
    
    span.end()
    
    # Verify:
    assert span is not None
    # Core attributes should still be present (Phase 2)
    # Memory should be bounded to ~1024 attributes
    # No crashes or exceptions
```

**Why 10K?**
- Reasonable upper bound for real workloads
- Tests eviction logic thoroughly (9,000+ evictions)
- Validates memory is bounded correctly

**Why NOT 1M?**
- Unrealistic attack scenario
- Customer bug (infinite loop), not SDK concern
- Same philosophy as C-4/H-3: customer responsibility

---

### 2. Boundary Testing

**Test:** Behavior at limit boundaries

```python
def test_boundary_exactly_at_limit():
    """Test exactly 1024 attributes (at limit)."""
    span = tracer.start_span("boundary_test")
    
    # Add exactly 1024 attributes
    for i in range(1024):
        span.set_attribute(f"attr_{i}", f"value_{i}")
    
    # Should not trigger eviction yet
    # Verify all 1024 present
    
    # One more should trigger eviction
    span.set_attribute("attr_1024", "value_1024")
    
    # Verify attr_0 was evicted (FIFO)
    # Verify 1024 attributes still present (not 1025)


def test_boundary_just_under_limit():
    """Test 1023 attributes (just under limit)."""
    span = tracer.start_span("under_limit_test")
    
    for i in range(1023):
        span.set_attribute(f"attr_{i}", f"value_{i}")
    
    # Should NOT trigger eviction
    # All 1023 should be present
    span.end()


def test_boundary_just_over_limit():
    """Test 1025 attributes (just over limit)."""
    span = tracer.start_span("over_limit_test")
    
    for i in range(1025):
        span.set_attribute(f"attr_{i}", f"value_{i}")
    
    # Should trigger eviction once
    # Oldest (attr_0) should be evicted
    # 1024 attributes present (attr_1 through attr_1024)
    span.end()
```

---

### 3. Concurrent Span Testing

**Test:** Multiple spans hitting limit simultaneously

```python
from concurrent.futures import ThreadPoolExecutor

def test_concurrent_spans_at_limit():
    """Test 100 concurrent spans, each with 1500 attributes."""
    
    def create_large_span(span_id):
        span = tracer.start_span(f"concurrent_span_{span_id}")
        for i in range(1500):  # Over limit
            span.set_attribute(f"attr_{i}", f"value_{i}")
        span.end()
        return span
    
    # Create 100 concurrent spans
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(create_large_span, i) 
            for i in range(100)
        ]
        results = [f.result() for f in futures]
    
    # Verify:
    # - All spans completed successfully
    # - No race conditions
    # - Memory bounded (100 * 1024 attributes max)
    # - No crashes
```

---

### 4. Special Characters in Keys

**Test:** Attribute keys with special characters

```python
def test_special_characters_in_keys():
    """Test attributes with various special characters."""
    span = tracer.start_span("special_chars_test")
    
    # Dots (common in nested structures)
    span.set_attribute("key.with.dots", "value")
    
    # Dashes
    span.set_attribute("key-with-dashes", "value")
    
    # Underscores
    span.set_attribute("key_with_underscores", "value")
    
    # Unicode
    span.set_attribute("key_with_unicode_🎉", "value")
    
    # Numbers
    span.set_attribute("key123", "value")
    span.set_attribute("123key", "value")
    
    # Mixed
    span.set_attribute("key.with-mixed_chars123", "value")
    
    span.end()
    
    # Verify all attributes set successfully
    # Verify backend accepts them
```

---

### 5. Large Values

**Test:** Attributes with large values

```python
def test_large_attribute_values():
    """Test attributes with large values (1MB+)."""
    span = tracer.start_span("large_value_test")
    
    # 1MB text
    large_text = "x" * (1024 * 1024)
    span.set_attribute("large_text", large_text)
    
    # Large JSON
    large_dict = {f"key_{i}": f"value_{i}" for i in range(10_000)}
    span.set_attribute("large_json", json.dumps(large_dict))
    
    # Large nested structure
    nested = {"level1": {"level2": {"level3": {"data": ["x"] * 10_000}}}}
    span.set_attribute("large_nested", json.dumps(nested))
    
    span.end()
    
    # Verify:
    # - Max span size limit enforced (10MB)
    # - Large values don't crash serialization
    # - Backend accepts or rejects appropriately
```

---

### 6. Core Attribute Preservation (Phase 2)

**Test:** Core attributes preserved during stress

```python
def test_core_attributes_preserved_under_stress():
    """Test core attributes survive 10K attribute flood."""
    tracer = HoneyHiveTracer.init(
        project="test_project",
        max_attributes=1024,
    )
    
    span = tracer.start_span("stress_test")
    
    # Core attributes set (should be preserved)
    # These are set by tracer automatically:
    # - honeyhive.session_id
    # - honeyhive.project_id
    # - honeyhive.event_type
    # - honeyhive.event_name
    # - honeyhive.source
    
    # Flood with 10K regular attributes
    for i in range(10_000):
        span.set_attribute(f"regular_attr_{i}", f"value_{i}")
    
    span.end()
    
    # Verify:
    # - honeyhive.session_id still present
    # - honeyhive.project_id still present
    # - All core attributes present
    # - Backend accepts span (not dropped)
    
    # NOTE: This requires Phase 2 core attribute preservation
```

---

## What We're NOT Testing (Out of Scope)

### 1. Attack Scenarios

**NOT Testing:**
```python
# ❌ 1,000,000 attributes (attack/bug)
def test_attack_1m_attributes():  # DON'T ADD THIS
    for i in range(1_000_000):
        span.set_attribute(...)
```

**Why NOT:**
- Unrealistic scenario
- Customer bug (infinite loop)
- Same philosophy as H-3: customer responsibility
- 10K is sufficient to test eviction logic

---

### 2. Binary Data

**NOT Testing:**
```python
# ❌ Binary data in attributes
def test_binary_data():  # DON'T ADD THIS
    span.set_attribute("binary", b"\x00\x01\x02...")
```

**Why NOT:**
- Not a real use case for span attributes
- Attributes are string-based in OpenTelemetry
- JSON serialization would fail anyway

---

### 3. Malicious Patterns

**NOT Testing:**
```python
# ❌ SQL injection, XSS, etc.
def test_malicious_attributes():  # DON'T ADD THIS
    span.set_attribute("key", "'; DROP TABLE users; --")
```

**Why NOT:**
- Backend validation responsibility
- SDK shouldn't try to sanitize (trust backend)
- Not a limit configuration concern

---

## Implementation Plan

### File Structure

```
tests/
├── integration/
│   ├── test_span_limits_happy_path.py  # Existing (CEO bug)
│   └── test_span_limits_stress.py      # NEW - Edge cases
└── unit/
    └── test_span_limits_unit.py        # Existing
```

### New File: `test_span_limits_stress.py`

```python
"""
Integration tests for span attribute limits - edge cases.

Tests:
- Stress: 10K attributes (max reasonable)
- Boundary: at/under/over limit
- Concurrent: multiple spans simultaneously
- Special chars: dots, dashes, unicode
- Large values: 1MB+ attributes
- Phase 2: Core attribute preservation
"""

import pytest
from concurrent.futures import ThreadPoolExecutor
from honeyhive import HoneyHiveTracer

class TestSpanLimitsStress:
    """Stress testing for span attribute limits."""
    
    def test_stress_10k_attributes(self):
        """Test 10,000 attributes (max reasonable stress)."""
        # Implementation...
    
    def test_boundary_at_limit(self):
        """Test exactly 1024 attributes."""
        # Implementation...
    
    # ... rest of tests ...
```

---

## Test Execution

### Run Edge Case Tests

```bash
# Run all stress tests
tox -e integration-parallel -- tests/integration/test_span_limits_stress.py

# Run specific test
tox -e integration-parallel -- tests/integration/test_span_limits_stress.py::TestSpanLimitsStress::test_stress_10k_attributes

# Run with verbose output
tox -e integration-parallel -- tests/integration/test_span_limits_stress.py -v
```

### CI Integration

Add to CI pipeline:
```yaml
- name: Run Stress Tests
  run: |
    tox -e integration-parallel -- tests/integration/test_span_limits_stress.py
```

---

## Success Criteria

### Phase 1 (v1.0.0) - Must Have

- [ ] `test_stress_10k_attributes` passes
- [ ] `test_boundary_at_limit` passes
- [ ] `test_boundary_just_under_limit` passes
- [ ] `test_boundary_just_over_limit` passes
- [ ] `test_concurrent_spans_at_limit` passes
- [ ] `test_special_characters_in_keys` passes
- [ ] `test_large_attribute_values` passes

### Phase 2 - Nice to Have

- [ ] `test_core_attributes_preserved_under_stress` passes
- [ ] `test_attribute_order_preserved` passes
- [ ] `test_eviction_patterns` passes

---

## Timeline

**Week 2 (Phase 1):** Add edge case tests  
**Week 3 (Phase 1):** Validate all tests pass  
**Phase 2:** Add core attribute preservation tests

---

## Related Documents

- **Pessimistic Review:** `.praxis-os/workspace/review/2025-11-18-span-limits-pessimistic-review.md` (H-7 section)
- **Test Strategy:** `.praxis-os/specs/review/.../testing/test-strategy.md`

---

## Conclusion

✅ **H-7 is valid** - We need improved edge case testing

**Scope:** 10K attributes max for stress testing (not 1M)

**Approach:** Add `test_span_limits_stress.py` with 7 edge case tests

**Timeline:** Week 2-3 (Phase 1 implementation)

**Philosophy:** Test realistic edge cases, not attack scenarios (customer responsibility)


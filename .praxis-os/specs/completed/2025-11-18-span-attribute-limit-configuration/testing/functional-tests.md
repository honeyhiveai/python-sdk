# Functional Test Plan

**Feature:** Span Attribute Limit Configuration & Core Attribute Preservation  
**Date:** 2025-11-18  
**Test Type:** Functional Requirements Verification

---

## Overview

This document defines functional test cases to verify all functional requirements (FR-1 through FR-7). Each test case includes:
- Test ID and name
- Requirement traceability
- Preconditions
- Test steps
- Expected results
- Pass/fail criteria

---

## FR-1: Configurable Span Attribute Limits

### FT-1.1: Custom Max Attributes Configuration

**Requirement:** FR-1  
**Type:** Unit Test  
**Priority:** P0 (CRITICAL)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed
- Test environment configured

**Test Steps:**
1. Create `TracerConfig` with `max_attributes=2000`
2. Verify config instance has `max_attributes == 2000`
3. Initialize `HoneyHiveTracer` with this config
4. Get `TracerProvider` from OpenTelemetry
5. Verify provider's `_span_limits.max_attributes == 2000`

**Expected Results:**
- TracerConfig accepts custom value
- TracerProvider reflects custom limit

**Pass/Fail Criteria:**
- PASS: Provider limit == 2000
- FAIL: Provider limit != 2000 OR error raised

**Test Implementation:**
```python
def test_custom_max_attributes_configuration():
    """Verify custom max_attributes is applied to TracerProvider."""
    config = TracerConfig(
        api_key="test",
        project="test",
        max_attributes=2000,
    )
    assert config.max_attributes == 2000
    
    tracer = HoneyHiveTracer.init(config=config, test_mode=True)
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attributes == 2000
```

---

### FT-1.2: Custom Max Attribute Length Configuration

**Requirement:** FR-1  
**Type:** Unit Test  
**Priority:** P0 (CRITICAL)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed

**Test Steps:**
1. Create `TracerConfig` with `max_attribute_length=20971520` (20MB)
2. Verify config has correct value
3. Initialize tracer
4. Verify provider's `_span_limits.max_attribute_length == 20971520`

**Expected Results:**
- Custom size limit applied

**Pass/Fail Criteria:**
- PASS: Provider limit == 20MB
- FAIL: Provider limit != 20MB

**Test Implementation:**
```python
def test_custom_max_attribute_length_configuration():
    """Verify custom max_attribute_length is applied."""
    config = TracerConfig(
        api_key="test",
        project="test",
        max_attribute_length=20 * 1024 * 1024,  # 20MB
    )
    assert config.max_attribute_length == 20971520
    
    tracer = HoneyHiveTracer.init(config=config, test_mode=True)
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attribute_length == 20971520
```

---

## FR-2: Increased Default Limits

### FT-2.1: Default Max Attributes is 1024

**Requirement:** FR-2  
**Type:** Unit Test  
**Priority:** P0 (CRITICAL)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed

**Test Steps:**
1. Create `TracerConfig` without specifying `max_attributes`
2. Verify `config.max_attributes == 1024`
3. Initialize tracer with default config
4. Verify provider `max_attributes == 1024`

**Expected Results:**
- Default is 1024 (not OpenTelemetry's 128)

**Pass/Fail Criteria:**
- PASS: Default == 1024
- FAIL: Default != 1024

**Test Implementation:**
```python
def test_default_max_attributes_is_1024():
    """Verify default max_attributes is 1024 (8x OTel default)."""
    config = TracerConfig(api_key="test", project="test")
    assert config.max_attributes == 1024
    
    tracer = HoneyHiveTracer.init(config=config, test_mode=True)
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attributes == 1024
```

---

### FT-2.2: Default Max Attribute Length is 10MB

**Requirement:** FR-2  
**Type:** Unit Test  
**Priority:** P0 (CRITICAL)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed

**Test Steps:**
1. Create `TracerConfig` without specifying `max_attribute_length`
2. Verify `config.max_attribute_length == 10485760` (10MB)
3. Initialize tracer
4. Verify provider reflects 10MB

**Expected Results:**
- Default is 10MB

**Pass/Fail Criteria:**
- PASS: Default == 10MB
- FAIL: Default != 10MB

**Test Implementation:**
```python
def test_default_max_attribute_length_is_10mb():
    """Verify default max_attribute_length is 10MB."""
    config = TracerConfig(api_key="test", project="test")
    assert config.max_attribute_length == 10 * 1024 * 1024
    
    tracer = HoneyHiveTracer.init(config=config, test_mode=True)
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attribute_length == 10485760
```

---

### FT-2.3: CEO Bug Regression Test (SerpAPI Large Response)

**Requirement:** FR-2, BG-1 (Eliminate silent data loss)  
**Type:** Integration Test  
**Priority:** P0 (CRITICAL)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed
- SerpAPI integration configured
- HoneyHive test project created

**Test Steps:**
1. Initialize tracer with default config
2. Create span with 400+ attributes (simulate SerpAPI response)
3. Wait for span export
4. Query HoneyHive API for span
5. Verify span exists in backend
6. Verify `honeyhive.session_id` attribute present
7. Verify parent-child relationship maintained

**Expected Results:**
- Span exported successfully
- Core attributes NOT evicted
- No backend rejection

**Pass/Fail Criteria:**
- PASS: Span found in backend WITH session_id
- FAIL: Span missing OR session_id missing

**Test Implementation:**
```python
def test_ceo_bug_regression_serpapi_large_response():
    """Regression test: SerpAPI with 400+ attrs doesn't drop session_id."""
    tracer = HoneyHiveTracer.init(
        project="test",
        test_mode=False,  # Real export
    )
    
    with tracer.start_span("serpapi_search") as span:
        # Simulate SerpAPI response: 50 results × 8 attributes each = 400 attrs
        for i in range(50):
            span.set_attribute(f"results.{i}.title", f"Title {i}")
            span.set_attribute(f"results.{i}.url", f"https://example.com/{i}")
            span.set_attribute(f"results.{i}.snippet", f"Snippet {i}" * 100)
            span.set_attribute(f"results.{i}.position", i)
            span.set_attribute(f"results.{i}.source", "google")
            span.set_attribute(f"results.{i}.date", "2025-11-18")
            span.set_attribute(f"results.{i}.rating", 4.5)
            span.set_attribute(f"results.{i}.reviews", 42)
    
    # Wait for export
    time.sleep(2)
    
    # Query HoneyHive API
    span_data = query_honeyhive_api_for_span(span_id=span.context.span_id)
    
    # Verify
    assert span_data is not None, "Span not found in backend (REJECTED)"
    assert "session_id" in span_data["attributes"], "session_id was evicted"
    assert span_data["attributes"]["session_id"] is not None
```

---

## FR-3: Environment Variable Support

### FT-3.1: Environment Variable for Max Attributes

**Requirement:** FR-3  
**Type:** Unit Test  
**Priority:** P1 (HIGH)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed

**Test Steps:**
1. Set `os.environ["HH_MAX_ATTRIBUTES"] = "3000"`
2. Create `TracerConfig` without constructor param
3. Verify `config.max_attributes == 3000`
4. Verify provider reflects 3000

**Expected Results:**
- Env var sets config value

**Pass/Fail Criteria:**
- PASS: Config reads env var correctly
- FAIL: Env var ignored

**Test Implementation:**
```python
def test_env_var_for_max_attributes():
    """Verify HH_MAX_ATTRIBUTES env var sets config value."""
    os.environ["HH_MAX_ATTRIBUTES"] = "3000"
    
    config = TracerConfig(api_key="test", project="test")
    assert config.max_attributes == 3000
    
    del os.environ["HH_MAX_ATTRIBUTES"]
```

---

### FT-3.2: Constructor Overrides Environment Variable

**Requirement:** FR-3  
**Type:** Unit Test  
**Priority:** P1 (HIGH)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed

**Test Steps:**
1. Set `os.environ["HH_MAX_ATTRIBUTES"] = "2000"`
2. Create `TracerConfig` with `max_attributes=5000` (constructor)
3. Verify `config.max_attributes == 5000` (constructor wins)

**Expected Results:**
- Constructor param overrides env var

**Pass/Fail Criteria:**
- PASS: Constructor value used (5000)
- FAIL: Env var value used (2000)

**Test Implementation:**
```python
def test_constructor_overrides_env_var():
    """Verify constructor params override env vars."""
    os.environ["HH_MAX_ATTRIBUTES"] = "2000"
    
    config = TracerConfig(
        api_key="test",
        project="test",
        max_attributes=5000,  # Override
    )
    assert config.max_attributes == 5000  # Constructor wins
    
    del os.environ["HH_MAX_ATTRIBUTES"]
```

---

## FR-4: Apply Limits During TracerProvider Creation

### FT-4.1: Limits Applied to New TracerProvider

**Requirement:** FR-4  
**Type:** Integration Test  
**Priority:** P0 (CRITICAL)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- No existing TracerProvider
- Python SDK installed

**Test Steps:**
1. Verify no existing provider (NoOp provider)
2. Initialize tracer with `max_attributes=1500`
3. Verify `atomic_provider_detection_and_setup` created new provider
4. Verify provider has `max_attributes == 1500`
5. Verify provider has `max_attribute_length == 10MB` (default)

**Expected Results:**
- New provider created with custom limits

**Pass/Fail Criteria:**
- PASS: Provider has correct limits
- FAIL: Limits not applied

**Test Implementation:**
```python
def test_limits_applied_to_new_provider():
    """Verify limits are applied when creating new TracerProvider."""
    # Reset provider to NoOp
    trace._TRACER_PROVIDER = None
    trace._TRACER_PROVIDER_INITIALIZED = False
    
    config = TracerConfig(
        api_key="test",
        project="test",
        max_attributes=1500,
    )
    tracer = HoneyHiveTracer.init(config=config, test_mode=True)
    
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attributes == 1500
    assert provider._span_limits.max_attribute_length == 10485760
```

---

### FT-4.2: Existing Provider Retains Its Limits

**Requirement:** FR-4, C-1 (Constraint)  
**Type:** Integration Test  
**Priority:** P1 (HIGH)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Existing TracerProvider with max_attributes=200

**Test Steps:**
1. Create TracerProvider with `max_attributes=200`
2. Set as global provider
3. Initialize HoneyHive tracer with `max_attributes=1024`
4. Verify warning logged: "Existing TracerProvider detected"
5. Verify provider STILL has `max_attributes == 200` (unchanged)

**Expected Results:**
- Existing provider unchanged
- Warning logged

**Pass/Fail Criteria:**
- PASS: Provider limit unchanged, warning logged
- FAIL: Provider limit changed OR no warning

**Test Implementation:**
```python
def test_existing_provider_retains_limits():
    """Verify existing provider's limits cannot be overridden."""
    # Create provider with custom limits
    existing_provider = TracerProvider(
        span_limits=SpanLimits(max_attributes=200)
    )
    trace.set_tracer_provider(existing_provider)
    
    # Try to initialize with different limits
    with patch("honeyhive.utils.logger.safe_log") as mock_log:
        config = TracerConfig(
            api_key="test",
            project="test",
            max_attributes=1024,  # Try to override
        )
        tracer = HoneyHiveTracer.init(config=config, test_mode=True)
        
        # Verify warning logged
        mock_log.assert_any_call(
            tracer,
            "warning",
            "Existing TracerProvider detected. Span limits cannot be changed.",
        )
    
    # Verify limits unchanged
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attributes == 200  # Still 200!
```

---

## FR-5: Configuration Validation

### FT-5.1: Reject Negative Max Attributes

**Requirement:** FR-5  
**Type:** Unit Test  
**Priority:** P1 (HIGH)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed

**Test Steps:**
1. Attempt to create `TracerConfig` with `max_attributes=-1`
2. Expect `ValueError` raised
3. Verify error message contains "must be positive"

**Expected Results:**
- `ValueError` raised with actionable message

**Pass/Fail Criteria:**
- PASS: ValueError raised with correct message
- FAIL: No error raised OR wrong error type

**Test Implementation:**
```python
def test_reject_negative_max_attributes():
    """Verify negative max_attributes raises ValueError."""
    with pytest.raises(ValueError, match="must be positive"):
        TracerConfig(
            api_key="test",
            project="test",
            max_attributes=-1,
        )
```

---

### FT-5.2: Reject Max Attributes Below Minimum (128)

**Requirement:** FR-5  
**Type:** Unit Test  
**Priority:** P1 (HIGH)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed

**Test Steps:**
1. Attempt to create `TracerConfig` with `max_attributes=100`
2. Expect `ValueError` raised
3. Verify error message contains "must be >= 128"

**Expected Results:**
- ValueError raised

**Pass/Fail Criteria:**
- PASS: ValueError raised
- FAIL: No error raised

**Test Implementation:**
```python
def test_reject_max_attributes_below_minimum():
    """Verify max_attributes < 128 raises ValueError."""
    with pytest.raises(ValueError, match="must be >= 128"):
        TracerConfig(
            api_key="test",
            project="test",
            max_attributes=100,
        )
```

---

### FT-5.3: Reject Max Attributes Above Maximum (10000)

**Requirement:** FR-5, NFR-5 (Memory safety)  
**Type:** Unit Test  
**Priority:** P1 (HIGH)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed

**Test Steps:**
1. Attempt to create `TracerConfig` with `max_attributes=20000`
2. Expect `ValueError` raised
3. Verify error message contains "must be <= 10000"

**Expected Results:**
- ValueError raised (sanity check)

**Pass/Fail Criteria:**
- PASS: ValueError raised
- FAIL: No error raised

**Test Implementation:**
```python
def test_reject_max_attributes_above_maximum():
    """Verify max_attributes > 10000 raises ValueError (sanity check)."""
    with pytest.raises(ValueError, match="must be <= 10000"):
        TracerConfig(
            api_key="test",
            project="test",
            max_attributes=20000,
        )
```

---

### FT-5.4: Reject Max Attribute Length Below 1KB

**Requirement:** FR-5  
**Type:** Unit Test  
**Priority:** P1 (HIGH)  
**Status:** ✅ IMPLEMENTED

**Preconditions:**
- Python SDK installed

**Test Steps:**
1. Attempt to create `TracerConfig` with `max_attribute_length=500` (500 bytes)
2. Expect `ValueError` raised
3. Verify error message contains "must be >= 1KB"

**Expected Results:**
- ValueError raised

**Pass/Fail Criteria:**
- PASS: ValueError raised
- FAIL: No error raised

**Test Implementation:**
```python
def test_reject_max_attribute_length_below_minimum():
    """Verify max_attribute_length < 1KB raises ValueError."""
    with pytest.raises(ValueError, match="must be >= 1KB"):
        TracerConfig(
            api_key="test",
            project="test",
            max_attribute_length=500,  # 500 bytes
        )
```

---

## FR-6: Core Attribute Preservation (Phase 2)

### FT-6.1: Core Attributes Cached on Span Start

**Requirement:** FR-6  
**Type:** Unit Test  
**Priority:** P0 (CRITICAL)  
**Status:** 📅 PLANNED (Phase 2)

**Preconditions:**
- Phase 2 implemented
- `CoreAttributeSpanProcessor` created

**Test Steps:**
1. Initialize tracer with core preservation enabled
2. Create span with core attributes set
3. Verify `CoreAttributeSpanProcessor.on_start()` called
4. Verify core attrs cached in processor's internal cache
5. Verify cache contains: `session_id`, `project_id`, `event_type`

**Expected Results:**
- Core attributes cached at span start

**Pass/Fail Criteria:**
- PASS: Cache contains all core attrs
- FAIL: Cache empty OR missing core attrs

**Test Implementation (Pseudocode):**
```python
def test_core_attributes_cached_on_start():
    """Verify CoreAttributeSpanProcessor caches core attrs on_start."""
    tracer = HoneyHiveTracer.init(
        project="test",
        preserve_core_attributes=True,
    )
    
    processor = get_core_attribute_processor(tracer)
    
    with tracer.start_span("test") as span:
        span_id = id(span)
        
        # Verify cache populated
        assert span_id in processor._core_attr_cache
        cached_attrs = processor._core_attr_cache[span_id]
        assert "honeyhive.session_id" in cached_attrs
        assert "honeyhive.project_id" in cached_attrs
        assert "honeyhive.event_type" in cached_attrs
```

---

### FT-6.2: Missing Core Attributes Re-injected on Span End

**Requirement:** FR-6  
**Type:** Integration Test  
**Priority:** P0 (CRITICAL)  
**Status:** 📅 PLANNED (Phase 2)

**Preconditions:**
- Phase 2 implemented

**Test Steps:**
1. Initialize tracer with core preservation enabled
2. Create span with 2000 attributes (exceeds 1024 limit)
3. Verify core attrs evicted during span lifetime
4. Call `span.end()`
5. Verify `CoreAttributeSpanProcessor.on_end()` called
6. Verify missing core attrs re-injected into span
7. Verify re-injection logged

**Expected Results:**
- Core attrs restored before export

**Pass/Fail Criteria:**
- PASS: Core attrs present in final span
- FAIL: Core attrs missing after re-injection

**Test Implementation (Pseudocode):**
```python
def test_missing_core_attributes_reinjected():
    """Verify evicted core attrs are re-injected on span end."""
    tracer = HoneyHiveTracer.init(
        project="test",
        preserve_core_attributes=True,
    )
    
    with patch("honeyhive.utils.logger.safe_log") as mock_log:
        with tracer.start_span("test") as span:
            # Add 2000 attributes (exceeds 1024 limit)
            for i in range(2000):
                span.set_attribute(f"attr_{i}", f"value_{i}")
            
            # Verify core attrs evicted during lifetime
            assert "honeyhive.session_id" not in span.attributes
        
        # Verify re-injection logged
        mock_log.assert_any_call(
            tracer,
            "warning",
            match="Re-injected .* evicted core attributes",
        )
    
    # Verify core attrs present in exported span
    exported_span = get_exported_span()
    assert "honeyhive.session_id" in exported_span.attributes
    assert "honeyhive.project_id" in exported_span.attributes
```

---

### FT-6.3: Extreme Payload Does Not Cause Backend Rejection

**Requirement:** FR-6, BG-1  
**Type:** Integration Test  
**Priority:** P0 (CRITICAL)  
**Status:** 📅 PLANNED (Phase 2)

**Preconditions:**
- Phase 2 implemented
- HoneyHive backend access

**Test Steps:**
1. Initialize tracer with core preservation enabled
2. Create span with 10,000 attributes (10x limit)
3. Wait for span export
4. Query HoneyHive backend for span
5. Verify span exists (not rejected)
6. Verify core attributes present

**Expected Results:**
- Span exported successfully despite extreme payload
- Core attrs preserved

**Pass/Fail Criteria:**
- PASS: Span found in backend with core attrs
- FAIL: Span rejected OR core attrs missing

**Test Implementation (Pseudocode):**
```python
@pytest.mark.integration
def test_extreme_payload_no_backend_rejection():
    """Verify 10K+ attributes doesn't cause backend rejection."""
    tracer = HoneyHiveTracer.init(
        project="test",
        preserve_core_attributes=True,
        test_mode=False,  # Real export
    )
    
    with tracer.start_span("extreme_payload") as span:
        # Add 10,000 attributes
        for i in range(10000):
            span.set_attribute(f"large_attr_{i}", f"value_{i}" * 100)
    
    time.sleep(2)  # Wait for export
    
    # Query backend
    span_data = query_honeyhive_api_for_span(span.context.span_id)
    
    # Verify
    assert span_data is not None, "Span was REJECTED"
    assert "session_id" in span_data["attributes"]
    assert "project_id" in span_data["attributes"]
    assert "event_type" in span_data["attributes"]
```

---

## FR-7: Smart Truncation (Phase 3)

### FT-7.1: Large Attributes Automatically Truncated

**Requirement:** FR-7  
**Type:** Unit Test  
**Priority:** P2 (MEDIUM)  
**Status:** 📅 PLANNED (Phase 3)

**Preconditions:**
- Phase 3 implemented

**Test Steps:**
1. Initialize tracer with truncation enabled
2. Set attribute with 500KB value (exceeds 100KB threshold)
3. Verify truncation strategy applied
4. Verify truncated attribute has `_truncated` suffix
5. Verify truncation logged

**Expected Results:**
- Large attribute truncated
- Truncation transparent

**Pass/Fail Criteria:**
- PASS: Attribute truncated, suffix added
- FAIL: No truncation OR no suffix

**Test Implementation (Pseudocode):**
```python
def test_large_attributes_truncated():
    """Verify attributes >100KB are automatically truncated."""
    tracer = HoneyHiveTracer.init(
        project="test",
        enable_truncation=True,
        truncation_threshold=100 * 1024,  # 100KB
    )
    
    with tracer.start_span("test") as span:
        large_value = "x" * 500 * 1024  # 500KB
        span.set_attribute("large_response", large_value)
        
        # Verify truncated
        assert "large_response_truncated" in span.attributes
        assert len(span.attributes["large_response_truncated"]) < 100 * 1024
        assert "..." in span.attributes["large_response_truncated"]  # Head-tail strategy
```

---

## Test Summary

| Test ID | Requirement | Type | Priority | Status | Phase |
|---------|-------------|------|----------|--------|-------|
| FT-1.1 | FR-1 | Unit | P0 | ✅ DONE | 1 |
| FT-1.2 | FR-1 | Unit | P0 | ✅ DONE | 1 |
| FT-2.1 | FR-2 | Unit | P0 | ✅ DONE | 1 |
| FT-2.2 | FR-2 | Unit | P0 | ✅ DONE | 1 |
| FT-2.3 | FR-2, BG-1 | Integration | P0 | ✅ DONE | 1 |
| FT-3.1 | FR-3 | Unit | P1 | ✅ DONE | 1 |
| FT-3.2 | FR-3 | Unit | P1 | ✅ DONE | 1 |
| FT-4.1 | FR-4 | Integration | P0 | ✅ DONE | 1 |
| FT-4.2 | FR-4, C-1 | Integration | P1 | ✅ DONE | 1 |
| FT-5.1 | FR-5 | Unit | P1 | ✅ DONE | 1 |
| FT-5.2 | FR-5 | Unit | P1 | ✅ DONE | 1 |
| FT-5.3 | FR-5, NFR-5 | Unit | P1 | ✅ DONE | 1 |
| FT-5.4 | FR-5 | Unit | P1 | ✅ DONE | 1 |
| FT-6.1 | FR-6 | Unit | P0 | 📅 PLANNED | 2 |
| FT-6.2 | FR-6 | Integration | P0 | 📅 PLANNED | 2 |
| FT-6.3 | FR-6, BG-1 | Integration | P0 | 📅 PLANNED | 2 |
| FT-7.1 | FR-7 | Unit | P2 | 📅 PLANNED | 3 |

**Total Tests:** 17  
**Implemented:** 13 (Phase 1)  
**Planned:** 4 (Phase 2-3)  
**Coverage:** All 7 functional requirements covered

---

**Document Status:** Complete  
**Last Updated:** 2025-11-18  
**Next Review:** After Phase 2 implementation


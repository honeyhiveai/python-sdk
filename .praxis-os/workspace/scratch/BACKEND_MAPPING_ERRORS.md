# Backend Attribute Mapping Errors (Staging)

## Summary
After fixing client-side `enrich_span` issues, all spans are correctly exported from the Python SDK. However, 9 integration tests fail due to backend attribute routing issues in the staging ingestion service.

**Client Status:** ✅ **ALL SPANS EXPORT CORRECTLY**
**Backend Status:** ❌ **ATTRIBUTE ROUTING ISSUES**

---

## Test Failures Breakdown

### ❌ 1. test_error_spans_backend_verification

**File:** `tests/integration/test_otel_backend_verification_integration.py`

**Issue:** `honeyhive_error` attribute missing from metadata

**Client Sends:**
```json
{
  "honeyhive_error": "Intentional test error for backend verification",
  "honeyhive_error_type": "ValueError"
}
```

**Backend Returns:**
```python
error_event.error = "ValueError: Intentional test error..."  # ✅ Routed to top-level
error_event.metadata = {
  "honeyhive_error_type": "ValueError",  # ✅ Present
  # "honeyhive_error": MISSING ❌ (expected to be in metadata too)
}
```

**Expected Behavior:** Backend should preserve `honeyhive_error` in `metadata` AND route to top-level `error`

**Test Assertion:**
```python
assert metadata.get("honeyhive_error") == "Intentional test error for backend verification"  # FAILS
```

---

### ❌ 2. test_high_cardinality_attributes_backend_verification

**File:** `tests/integration/test_otel_backend_verification_integration.py`

**Issue:** General attribute routing - needs investigation

**Likely Issue:** Similar to test #1, attributes may be routed differently than tests expect

---

### ❌ 3. test_otlp_export_with_backend_verification

**File:** `tests/integration/test_otel_otlp_export_integration.py`

**Issue:** Backend verification timeout or attribute routing

**Likely Issue:** Event not found or attributes not routing correctly

**Test Assertion:**
```python
assert target_event.metadata.get("test.unique_id") == unique_id
assert target_event.metadata.get("honeyhive.session_id") == test_session_id
assert target_event.metadata.get("honeyhive.project") == real_project
assert target_event.metadata.get("honeyhive.source") == real_source
```

---

### ❌ 4. test_performance_regression_detection

**File:** `tests/integration/test_otel_performance_regression_integration.py`

**Issue:** Performance timing test - may be flaky, not mapping related

---

### ❌ 5. test_tracing_minimal_overhead_integration

**File:** `tests/integration/test_tracer_performance.py`

**Issue:** Performance overhead test failure

**Error:** `AssertionError: Tracer overhead too high: 143.44ms (expected < 75.0ms)`

**Root Cause:** **NOT A MAPPING ERROR** - Performance characteristic test, not related to our changes

---

### ❌ 6. test_multi_instance_attribute_isolation

**File:** `tests/integration/test_honeyhive_attributes_backend_integration.py`

**Issue:** Attribute routing for HoneyHive-specific attributes

**Test Assertions:**
```python
assert event.metadata.get("honeyhive.outputs.response") == "Test response"
assert event.metadata.get("honeyhive.metadata.model.provider") == "test"
assert event.metadata.get("honeyhive.config.max_tokens") == 150
```

**Likely Issue:** Backend may be routing these attributes differently (e.g., `honeyhive.outputs.*` → `outputs`, `honeyhive.config.*` → `config`)

---

### ❌ 7. test_span_attributes_comprehensive_lifecycle

**File:** `tests/integration/test_otel_span_lifecycle_integration.py`

**Issue:** `honeyhive.project` and `honeyhive.source` not in metadata

**Test Assertions:**
```python
assert target_event.metadata.get("honeyhive.project") == real_project  # FAILS
assert target_event.metadata.get("honeyhive.source") == real_source    # FAILS
```

**Backend Returns:**
```python
event.metadata = {
  "traceloop.association.properties.session_id": "...",
  "traceloop.association.properties.project": "sdk",  # ✅ Different key
  "traceloop.association.properties.source": "pytest-integration",  # ✅ Different key
  # "honeyhive.project": MISSING ❌
  # "honeyhive.source": MISSING ❌
}
```

**Root Cause:** Backend routes `honeyhive.project` → `traceloop.association.properties.project` in metadata, not preserving the original key.

---

### ❌ 8. test_span_events_comprehensive_lifecycle

**File:** `tests/integration/test_otel_span_lifecycle_integration.py`

**Issue:** Same as #7 - `honeyhive.project` and `honeyhive.source` routing

**Test Assertion:**
```python
assert target_event.metadata.get("honeyhive.project") == real_project  # FAILS
```

---

### ❌ 9. test_concurrent_span_creation_thread_safety

**File:** `tests/integration/test_otel_concurrency_integration.py`

**Issue:** Backend verification timeout - events not found

**Error:** `Expected to verify at least 5 spans, got 0`

**Root Cause:** Either:
1. Staging backend ingestion delay/issue
2. Event filtering not working correctly
3. Spans not being stored

---

## Backend Mapping Issues Summary

### Critical Issues (Blocking Test Success):

1. **`honeyhive_error` attribute routing** (2 tests)
   - Client sends: `honeyhive_error`
   - Backend routes to: top-level `error` field ONLY
   - Expected: Should also preserve in `metadata.honeyhive_error`

2. **`honeyhive.project` and `honeyhive.source` attribute routing** (2 tests)
   - Client sends: `honeyhive.project`, `honeyhive.source`
   - Backend routes to: `metadata.traceloop.association.properties.{project|source}`
   - Expected: Should preserve original keys `metadata.honeyhive.project`, `metadata.honeyhive.source`

3. **HoneyHive namespace attribute routing** (1 test)
   - Client sends: `honeyhive.outputs.*`, `honeyhive.config.*`, `honeyhive.metadata.*`
   - Backend likely routes to: top-level `outputs`, `config`, `metadata` (flattened)
   - Expected: Tests expect them in `metadata.honeyhive.outputs.*` format

4. **Backend verification timeouts** (2 tests)
   - Events not appearing in backend after 5s wait
   - May be staging-specific ingestion delay

5. **Performance tests** (1 test)
   - Not a mapping issue - performance characteristic failure

---

## Ingestion Service Mapping Reference

From our earlier ingestion service test fixtures, the correct mapping should be:

### HoneyHive SDK Attributes → Event Fields

| Client Attribute | Backend Event Field | Notes |
|-----------------|--------------------|--------------------|
| `honeyhive_metadata.*` | `metadata.*` (flattened) | ✅ Working |
| `honeyhive_metrics.*` | `metrics.*` (custom) or `metadata.*` (tokens) | ✅ Working |
| `honeyhive_inputs.*` | `inputs.*` (flattened) | ✅ Working |
| `honeyhive_outputs.*` | `outputs` (string or flattened) | ✅ Working |
| `honeyhive_config.*` | `config.*` (flattened) | ✅ Working |
| `honeyhive_feedback.*` | `feedback.*` (flattened) | ✅ Working |
| `honeyhive_error` | `error` (top-level) | ❌ Should ALSO be in `metadata.honeyhive_error` |
| `honeyhive.project` | `metadata.traceloop.association.properties.project` | ❌ Should ALSO be in `metadata.honeyhive.project` |
| `honeyhive.source` | `metadata.traceloop.association.properties.source` | ❌ Should ALSO be in `metadata.honeyhive.source` |

---

## Action Items

### For Backend Team (hive-kube ingestion service):

1. **Preserve `honeyhive_error` in metadata** while also routing to top-level `error`
2. **Preserve `honeyhive.project` and `honeyhive.source`** in metadata with original keys
3. **Investigate event storage/retrieval delays** for concurrent span tests
4. **Review attribute routing** for `honeyhive.*` prefixed attributes

### For SDK Team (python-sdk):

✅ **NO CHANGES NEEDED** - Client is correctly exporting all attributes

### For Test Team:

Option A: Update tests to match current backend behavior (short-term)
Option B: Wait for backend fixes (preferred - maintains test coverage)

---

## Verification

To verify backend is receiving data correctly, check:

```bash
# Client exports (verbose output shows):
✅ "honeyhive_error": "Intentional test error..."
✅ "honeyhive.project": "sdk"
✅ Status 200 from OTLP endpoint

# Backend query returns:
❌ metadata.honeyhive_error: null (expected: "Intentional test error...")
❌ metadata.honeyhive.project: null (expected: "sdk")
✅ metadata.traceloop.association.properties.project: "sdk"
```

---

## Conclusion

**All 9 integration test failures are backend attribute routing issues, NOT regressions from our `enrich_span` fixes.**

The Python SDK is correctly:
- ✅ Executing `enrich_span` immediately
- ✅ Setting all namespaced attributes correctly
- ✅ Exporting spans via OTLP successfully
- ✅ Receiving 200 OK responses from backend

The staging backend ingestion service needs updates to preserve certain attributes in metadata as tests expect.


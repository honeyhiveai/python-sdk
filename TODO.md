# TODO - Test Failures to Fix

This document tracks test failures and implementation issues discovered during v1.x development.

**Last Updated:** 2025-12-12  
**Test Command:** `direnv exec . pytest tests/tracer/ -v`  
**Current Status:** 35 passed, 6 failed (after test API fixes)

---

## RESOLVED: Test API Fixes (Commits 3a8d052, 3b99361)

The following test issues have been **fixed** by updating tests to match the v0 API:

### Fixed: `tracer_id` → `_tracer_id` attribute access
Tests were using `tracer.tracer_id` but v0 API only has private `_tracer_id`. Tests updated to use `_tracer_id`.

### Fixed: `name` → `event_name` parameter  
Tests were using `@trace(name="...")` but v0 API only accepts `event_name`. Tests updated.

### Fixed: Arbitrary kwargs → `metadata={}` dict
Tests were passing arbitrary kwargs like `key="value"` but v0 API only accepts structured `metadata={}` dict. Tests updated.

---

## REMAINING: Implementation Issues (6 failures)

These are **implementation bugs** that the tests are correctly catching, not test bugs.

### Issue 1: SAFE_PROPAGATION_KEYS Missing Keys

**File:** `src/honeyhive/tracer/processing/context.py`

**Problem:** `SAFE_PROPAGATION_KEYS` is missing `project` and `source` keys.

**Expected:** `{'project', 'source', 'run_id', 'dataset_id', 'datapoint_id', 'honeyhive_tracer_id'}`  
**Actual:** `{'run_id', 'dataset_id', 'datapoint_id', 'honeyhive_tracer_id'}`

**Affected Test:**
- `tests/tracer/test_baggage_isolation.py::TestSelectiveBaggagePropagation::test_safe_keys_constant_complete`

### Issue 2: enrich_span Metadata Not Being Set

**Problem:** `tracer.enrich_span(metadata={"key": "value"})` is not setting `honeyhive.metadata.key` on span attributes.

**Example:** After calling `tracer.enrich_span(metadata={"env": "production"})`, the span attributes don't contain `honeyhive.metadata.env`.

**Affected Tests:**
- `tests/tracer/test_multi_instance.py::TestMultiInstanceIntegration::test_two_projects_same_process`
- `tests/tracer/test_multi_instance.py::TestMultiInstanceSafety::test_no_cross_contamination`
- `tests/tracer/test_baggage_isolation.py::TestBaggagePropagationIntegration::test_evaluate_pattern_simulation`

### Issue 3: Baggage Isolation Between Nested Tracers

**Problem:** When tracer2 starts a span inside tracer1's span context, the baggage shows tracer2's ID instead of maintaining proper isolation. The test expects each tracer to see its own ID in baggage within its own span context.

**Affected Tests:**
- `tests/tracer/test_baggage_isolation.py::TestBaggageIsolation::test_two_tracers_isolated_baggage`
- `tests/tracer/test_baggage_isolation.py::TestBaggagePropagationIntegration::test_multi_instance_no_interference`

---

## DEPRECATED: Previous Categories (Now Resolved or Reclassified)

### Category 1: Missing `tracer_id` Property - RESOLVED
Tests updated to use `_tracer_id` instead of expecting public `tracer_id` property.

### Category 2: `trace` Decorator Kwargs Handling - RESOLVED  
Tests updated to use `event_name=` instead of `name=` and `metadata={}` instead of arbitrary kwargs

---

## Category 3: Backwards Compatibility - Missing Imports (3 failures)

**Issue:** Tests expect certain modules/functions to exist that are no longer available or moved.

### 3a. Missing `honeyhive.utils.config` module

**Affected Test:**
- `tests/compatibility/test_backward_compatibility.py::TestBackwardCompatibility::test_environment_variable_compatibility`

**Example Error:**
```
ModuleNotFoundError: No module named 'honeyhive.utils.config'
```

**Investigation Needed:**
- Check if `honeyhive.utils.config` was removed or renamed
- Verify if this is intentional API change or if module needs to be restored

### 3b. Missing `evaluate_batch` function

**Affected Test:**
- `tests/compatibility/test_backward_compatibility.py::TestBackwardCompatibility::test_new_features_availability`

**Example Error:**
```
Failed: New features should be importable: cannot import name 'evaluate_batch' from 'honeyhive'
```

**Investigation Needed:**
- Check if `evaluate_batch` was removed or renamed
- Verify if it should be exported from main `honeyhive` package

### 3c. Config access compatibility

**Affected Test:**
- `tests/compatibility/test_backward_compatibility.py::TestBackwardCompatibility::test_config_access_compatibility`

**Example Error:**
```
AssertionError: assert (False or False)
```

**Investigation Needed:**
- Test is checking config access patterns
- Likely related to missing `honeyhive.utils.config` module

---

## Category 4: Model/Data Issues (3 failures)

### 4a. UUIDType repr format (2 failures) - **FIXED IN CURRENT COMMIT**

**Status:** ✅ **RESOLVED** - Fixed by adding `__repr__` method in post-processing

**Affected Tests:**
- `tests/unit/test_models_generated.py::TestGeneratedModels::test_uuid_type`
- `tests/unit/test_models_integration.py::TestUUIDType::test_uuid_type_repr_method`

**Previous Error:**
```
assert "UUIDType(root=UUID('...'))" == 'UUIDType(...)'
```

**Fix Applied:** Updated `scripts/generate_v0_models.py` to add both `__str__` and `__repr__` methods to `UUIDType` during post-processing.

### 4b. External dataset evaluation

**Affected Test:**
- `tests/unit/test_experiments_core.py::TestEvaluate::test_evaluate_with_external_dataset`

**Example Error:**
```
AssertionError: expected call not found.
```

**Investigation Needed:**
- Mock expectations don't match actual calls
- May be related to API changes in evaluation functions

---

## Category 5: Baggage Propagation Issues (2 failures)

### 5a. SAFE_PROPAGATION_KEYS mismatch

**Affected Test:**
- `tests/tracer/test_baggage_isolation.py::TestSelectiveBaggagePropagation::test_safe_keys_constant_complete`

**Example Error:**
```
AssertionError: SAFE_PROPAGATION_KEYS mismatch. 
Expected: {'source', 'dataset_id', 'datapoint_id', 'run_id', 'project', 'honeyhive_tracer_id'}
```

**Investigation Needed:**
- Check if `SAFE_PROPAGATION_KEYS` constant changed
- Verify if test expectations need updating

### 5b. Evaluate pattern simulation

**Affected Test:**
- `tests/tracer/test_baggage_isolation.py::TestBaggagePropagationIntegration::test_evaluate_pattern_simulation`

**Example Error:**
```
AssertionError: assert 'honeyhive.metadata.datapoint' in {'honeyhive.project': 'test-project', ...}
```

**Investigation Needed:**
- Baggage key format or propagation logic may have changed
- Test expectations may need updating to match new baggage schema

---

## Summary Statistics

| Category | Count | Priority | Status |
|----------|-------|----------|--------|
| Missing tracer_id property | 8 | High | To Do |
| trace decorator kwargs | 21 | High | To Do |
| Backwards compat imports | 3 | Medium | To Do |
| Model/Data issues | 3 | Medium | 2 Fixed, 1 To Do |
| Baggage propagation | 2 | Medium | To Do |
| **Total** | **37** | - | **2 Fixed, 35 To Do** |

---

## Action Items

### Immediate (High Priority)
1. [ ] Add `tracer_id` property to `HoneyHiveTracer` class
2. [ ] Investigate and fix `trace` decorator kwargs handling
   - Determine intended API design
   - Update either implementation or tests accordingly

### Short Term (Medium Priority)
3. [ ] Restore or document removal of `honeyhive.utils.config`
4. [ ] Restore or document removal of `evaluate_batch`
5. [ ] Fix baggage propagation key mismatches
6. [ ] Fix external dataset evaluation mock expectations

### Verification
- [ ] Run `make test` and verify all tests pass
- [ ] Run `make test-all` (requires .env) for full integration test suite
- [ ] Update this TODO.md as issues are resolved

---

## Notes

- These failures were discovered after fixing model generation (Pydantic v2 compatibility)
- The UUIDType `__str__` and `__repr__` issues have been resolved
- Most failures appear to be from API evolution without corresponding test updates
- No CI changes needed - CI uses tox environments which handle integration tests separately

---

## Related Commits

- `f6c6199` - Fixed test infrastructure and import paths for Pydantic v2 compatibility
- `cf2ca51` - Fixed formatting tool version mismatch and expanded make format scope
- `08b0bd4` - Consolidated pip dependencies: removed requests, beautifulsoup4, pyyaml from Nix
- `755133a` - feat(dev): add v0 model generation and fix environment isolation

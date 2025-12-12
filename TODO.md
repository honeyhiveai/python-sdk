# TODO - Test Failures to Fix

This document tracks the 37 test failures discovered after fixing the model generation and test infrastructure. These appear to be pre-existing issues where the codebase evolved but tests weren't updated to match the new APIs.

**Last Updated:** 2025-12-12  
**Test Command:** `make test` (runs `pytest tests/unit/ tests/tracer/ tests/compatibility/ -n auto`)  
**Total Failures:** 35 out of 3014 tests (2 fixed: UUIDType repr issues)

---

## Category 1: Missing `tracer_id` Property (8 failures)

**Issue:** Tests expect `.tracer_id` as a public property, but the implementation only has `._tracer_id` (private attribute).

**Root Cause:** The `HoneyHiveTracer` class needs a public `@property` for `tracer_id` to expose the private `._tracer_id` attribute.

**Affected Tests:**
- `tests/tracer/test_baggage_isolation.py::TestBaggagePropagationIntegration::test_multi_instance_no_interference`
- `tests/tracer/test_baggage_isolation.py::TestTracerDiscoveryViaBaggage::test_discover_tracer_from_baggage`
- `tests/tracer/test_baggage_isolation.py::TestBaggageIsolation::test_two_tracers_isolated_baggage`
- `tests/tracer/test_baggage_isolation.py::TestTracerDiscoveryViaBaggage::test_discovery_with_evaluation_context`
- `tests/tracer/test_multi_instance.py::TestMultiInstanceSafety::test_discovery_in_threads`
- `tests/tracer/test_multi_instance.py::TestMultiInstanceSafety::test_registry_concurrent_access`
- `tests/tracer/test_multi_instance.py::TestMultiInstanceIntegration::test_two_projects_same_process`
- `tests/tracer/test_multi_instance.py::TestMultiInstanceSafety::test_no_cross_contamination`

**Example Error:**
```
AttributeError: 'HoneyHiveTracer' object has no attribute 'tracer_id'. Did you mean: '_tracer_id'?
```

**Suggested Fix:**
Add to `src/honeyhive/tracer/core/tracer.py` or `base.py`:
```python
@property
def tracer_id(self) -> str:
    """Public accessor for tracer ID."""
    return self._tracer_id
```

---

## Category 2: `trace` Decorator Kwargs Handling (21 failures)

**Issue:** The `_create_tracing_params()` function rejects kwargs that tests are passing to the `@trace` decorator (e.g., `name=`, `key=`, arbitrary attributes).

**Root Cause:** The decorator API may have changed to be more strict about accepted parameters, but tests still use the old flexible kwargs approach.

**Affected Tests:**
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_basic`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_attributes`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_return_value`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_exception`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_complex_attributes`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_error_recovery`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_performance`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_arguments`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_none_attributes`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_dynamic_attributes`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_concurrent_usage`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_async_function`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_context_manager`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_generator_function`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_nested_calls`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_keyword_arguments`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_class_method`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_memory_usage`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_large_data`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_empty_attributes`
- `tests/tracer/test_trace.py::TestTraceDecorator::test_trace_with_static_method`

**Example Error:**
```
TypeError: _create_tracing_params() got an unexpected keyword argument 'name'
TypeError: _create_tracing_params() got an unexpected keyword argument 'key'
```

**Example Test Usage:**
```python
@trace(name="test-function", tracer=self.mock_tracer)
@trace(event_name="test-function", key="value", tracer=self.mock_tracer)
```

**Investigation Needed:**
1. Check `src/honeyhive/tracer/instrumentation/decorators.py` to see what params are accepted
2. Determine if the decorator API intentionally changed or if tests need updating
3. Either:
   - Update `_create_tracing_params()` to accept/ignore arbitrary kwargs, OR
   - Update all test cases to use the new strict API

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

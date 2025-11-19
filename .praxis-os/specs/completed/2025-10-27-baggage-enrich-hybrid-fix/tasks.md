# Implementation Tasks

**Project:** Baggage Context + Enrich Functions Hybrid API Fix  
**Date:** 2025-10-27  
**Status:** Draft - Pending Approval  
**Ship Date:** 2025-10-31 (Friday)

---

## Time Estimates

- **Phase 1: Core Baggage Fix** - 4 hours (Monday)
- **Phase 2: Documentation Updates** - 4 hours (Tuesday)
- **Phase 3: Example Updates** - 4 hours (Wednesday)
- **Phase 4: Comprehensive Testing** - 6 hours (Thursday)
- **Phase 5: Release Preparation** - 2 hours (Friday AM)

**Total:** 20 hours (5 days, half-days)

---

## Phase 1: Core Baggage Fix

**Objective:** Fix the root cause of tracer discovery failure in evaluate() by re-enabling selective baggage propagation.

**Estimated Duration:** 4 hours

**Priority:** CRITICAL (blocks all evaluate() + enrich patterns)

### Phase 1 Tasks

#### Task 1.1: Implement Selective Baggage Propagation

**File:** `src/honeyhive/tracer/processing/context.py`

**Description:** Modify `_apply_baggage_context()` to filter baggage items to safe keys only and re-enable `context.attach()`.

**Changes:**
1. Add `SAFE_PROPAGATION_KEYS` constant
2. Filter `baggage_items` to safe keys
3. Uncomment `context.attach(ctx)` call
4. Add logging for filtered keys

**Acceptance Criteria:**
- Only safe keys propagated (run_id, dataset_id, datapoint_id, honeyhive_tracer_id, project, source)
- Session-specific keys excluded (session_id, session_name)
- Context attached successfully
- No errors in logs

**Estimated Time:** 1 hour

**Code Location:** Lines 270-295 (approx)

**Testing:** Unit test for key filtering

---

#### Task 1.2: Verify discover_tracer() Integration

**File:** `src/honeyhive/tracer/registry.py`

**Description:** Ensure `discover_tracer()` correctly reads `honeyhive_tracer_id` from baggage after propagation fix.

**Changes:**
1. Review baggage lookup logic
2. Verify priority order (explicit > baggage > default)
3. Add debug logging if needed

**Acceptance Criteria:**
- Baggage lookup works after propagation fix
- Priority order respected
- Returns correct tracer instance
- Graceful None return if not found

**Estimated Time:** 1 hour

**Testing:** Unit test for baggage-based discovery

---

#### Task 1.3: Unit Tests for Baggage Propagation

**File:** `tests/tracer/processing/test_context.py` (new)

**Description:** Add comprehensive unit tests for selective baggage propagation.

**Test Cases:**
1. `test_safe_keys_propagated()` - Verify safe keys in context
2. `test_unsafe_keys_filtered()` - Verify session_id not propagated
3. `test_context_attached()` - Verify context.attach() called
4. `test_empty_baggage()` - Handle empty dict gracefully
5. `test_thread_isolation()` - Verify thread-local context

**Acceptance Criteria:**
- All tests pass
- Code coverage ≥ 90% for modified code
- Tests run in CI

**Estimated Time:** 1.5 hours

---

#### Task 1.4: Integration Test for evaluate() + enrich_span()

**File:** `tests/integration/test_evaluate_enrich.py` (new)

**Description:** Add integration test that validates the full evaluate() + enrich_span() pattern works end-to-end.

**Test Scenario:**
```python
@trace(event_type="tool")
def user_function(datapoint):
    result = process(datapoint)
    enrich_span(metadata={"result": result})
    return result

result = evaluate(
    function=user_function,
    dataset=[{"inputs": {...}}],
    api_key=os.environ["HH_API_KEY"],
    project="test"
)

assert result["status"] == "completed"
assert "enrich_span successful" in logs
```

**Acceptance Criteria:**
- Test passes with real API call
- Tracer discovery works via baggage
- Enrichment succeeds
- Evaluation context propagated (run_id, datapoint_id)

**Estimated Time:** 0.5 hours

---

## Phase 2: Documentation Updates

**Objective:** Update all documentation to feature instance methods as primary API, document both patterns clearly.

**Estimated Duration:** 4 hours

**Priority:** HIGH (user-facing change)

### Phase 2 Tasks

#### Task 2.1: Update README.md

**File:** `README.md`

**Description:** Add prominent section showing instance method pattern as primary, legacy pattern as secondary.

**Changes:**
1. Add "Quick Start" with instance method pattern
2. Add "enrich_span & enrich_session" section
3. Show both patterns with clear labels (PRIMARY vs LEGACY)
4. Add note about v2.0 deprecation

**Example:**
```markdown
### Enriching Spans (PRIMARY - Recommended)

```python
tracer = HoneyHiveTracer(api_key="...", project="...")

@tracer.trace(event_type="tool")
def my_function():
    result = ...
    tracer.enrich_span(metadata={"result": result})  # ← Instance method
    return result
```

### Enriching Spans (Legacy Pattern)

For backward compatibility, the free function pattern still works:

```python
from honeyhive import enrich_span

@trace(event_type="tool")  
def my_function():
    result = ...
    enrich_span(metadata={"result": result})  # ← Free function (auto-discovery)
    return result
```

**Note:** Free functions will be deprecated in v2.0. Migrate to instance methods.
```

**Acceptance Criteria:**
- Instance methods shown first
- Both patterns documented clearly
- Migration note included
- Code examples correct

**Estimated Time:** 1.5 hours

---

#### Task 2.2: Update API Reference Documentation

**Files:**
- `docs/api/tracer.md` (or equivalent Sphinx docs)
- Docstrings in `src/honeyhive/tracer/core/context.py`

**Description:** Ensure API reference prominently features instance methods.

**Changes:**
1. Update `HoneyHiveTracer.enrich_span()` docstring
2. Update `HoneyHiveTracer.enrich_session()` docstring
3. Mark free functions as "Legacy" in API docs
4. Add cross-references between patterns

**Acceptance Criteria:**
- Docstrings comprehensive
- Instance methods documented fully
- Free functions marked as legacy
- Sphinx builds without errors

**Estimated Time:** 1.5 hours

---

#### Task 2.3: Create Migration Guide

**File:** `docs/migration/v0.2-to-v1.0.md` (new)

**Description:** Write migration guide for users upgrading from v0.2.x to v1.0.

**Sections:**
1. **What's New in v1.0**
2. **Breaking Changes** (none for v1.0)
3. **Recommended Pattern Changes** (instance methods)
4. **Migration Steps** (step-by-step)
5. **FAQ**

**Example Migration:**
```markdown
### Before (v0.2.x)

```python
from honeyhive import enrich_span

@trace(event_type="tool")
def my_function():
    enrich_span(metadata={...})
```

### After (v1.0 - Recommended)

```python
tracer = HoneyHiveTracer(...)

@tracer.trace(event_type="tool")
def my_function():
    tracer.enrich_span(metadata={...})
```

### Compatibility Note

The v0.2.x pattern still works in v1.0 with no changes required. Migration is optional but recommended.
```

**Acceptance Criteria:**
- Clear migration steps
- Code examples accurate
- FAQ addresses common questions
- Markdown renders correctly

**Estimated Time:** 1 hour

---

## Phase 3: Example Updates

**Objective:** Update 5-10 key examples to demonstrate instance method pattern as best practice.

**Estimated Duration:** 4 hours

**Priority:** MEDIUM (user education)

### Phase 3 Tasks

#### Task 3.1: Update Core Examples

**Files:**
- `examples/basic_tracing.py`
- `examples/openai_integration.py`
- `examples/anthropic_integration.py`
- `examples/custom_spans.py`
- `examples/evaluation_example.py`

**Description:** Update examples to use instance method pattern.

**Changes for Each Example:**
1. Initialize tracer explicitly
2. Use `tracer.enrich_span()` instead of `enrich_span()`
3. Use `@tracer.trace()` decorator
4. Add comments explaining pattern

**Example:**
```python
# Before
from honeyhive import trace, enrich_span

@trace(event_type="tool")
def process():
    result = ...
    enrich_span(metadata={"result": result})

# After
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer(
    api_key=os.environ["HH_API_KEY"],
    project="my-project"
)

@tracer.trace(event_type="tool")  # ← Use tracer instance
def process():
    result = ...
    tracer.enrich_span(metadata={"result": result})  # ← Instance method
```

**Acceptance Criteria:**
- All examples run without errors
- Instance methods used consistently
- Comments explain pattern
- README in examples/ updated

**Estimated Time:** 3 hours (30 min per example)

---

#### Task 3.2: Create evaluate() + Instance Method Example

**File:** `examples/evaluate_with_enrichment.py` (new)

**Description:** Create comprehensive example showing evaluate() with instance method enrichment.

**Example:**
```python
from honeyhive import HoneyHiveTracer, evaluate
import os

def process_datapoint(datapoint, tracer):
    """User function with explicit tracer."""
    inputs = datapoint["inputs"]
    
    @tracer.trace(event_type="tool")
    def llm_call():
        result = {"output": "test"}
        tracer.enrich_span(
            metadata={"model": "gpt-4"},
            metrics={"latency_ms": 150}
        )
        return result
    
    return llm_call()

# Run evaluation
result = evaluate(
    function=lambda dp: process_datapoint(dp, None),  # Tracer auto-discovered
    dataset=[{"inputs": {"text": "test"}}],
    api_key=os.environ["HH_API_KEY"],
    project="evals"
)

print(f"Status: {result['status']}")
```

**Acceptance Criteria:**
- Example runs successfully
- Shows both explicit and auto-discovery patterns
- Well-commented
- README updated

**Estimated Time:** 1 hour

---

## Phase 4: Comprehensive Testing

**Objective:** Validate all patterns work correctly with comprehensive test coverage.

**Estimated Duration:** 6 hours

**Priority:** CRITICAL (quality gate for v1.0)

### Phase 4 Tasks

#### Task 4.1: Multi-Instance Safety Tests

**File:** `tests/tracer/test_multi_instance.py` (new)

**Description:** Verify multiple concurrent tracer instances don't interfere with each other.

**Test Cases:**
1. `test_concurrent_tracers_isolated()` - 10 threads, unique tracers
2. `test_baggage_isolation()` - Each thread sees own baggage
3. `test_registry_concurrent_access()` - Registry thread-safe
4. `test_discovery_in_threads()` - Discovery works per-thread
5. `test_no_cross_contamination()` - Span attributes isolated

**Test Pattern:**
```python
def test_concurrent_tracers_isolated():
    """Test 10 concurrent tracers are isolated."""
    def thread_func(thread_id):
        tracer = HoneyHiveTracer(
            api_key="test",
            project=f"p{thread_id}",
            session_name=f"s{thread_id}"
        )
        
        with tracer.start_span(f"span-{thread_id}") as span:
            tracer.enrich_span(metadata={"tid": thread_id})
            
            # Verify own metadata
            attrs = span.attributes
            assert attrs["metadata.tid"] == thread_id
        
        return tracer.tracer_id
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(thread_func, range(10)))
    
    # All unique tracer IDs
    assert len(set(results)) == 10
```

**Acceptance Criteria:**
- All concurrency tests pass
- No race conditions
- No data leakage
- Memory stable

**Estimated Time:** 2 hours

---

#### Task 4.2: Backward Compatibility Test Suite

**File:** `tests/tracer/test_backward_compat.py` (new)

**Description:** Validate all v0.2.x patterns work unchanged.

**Test Cases:**
1. `test_v0_2_free_function_enrich_span()` - Free function pattern
2. `test_v0_2_free_function_enrich_session()` - Free function session
3. `test_v0_2_global_decorator()` - @trace decorator (global)
4. `test_v0_2_evaluate_pattern()` - evaluate() with free functions
5. `test_v0_2_discovery()` - Tracer discovery via baggage

**Acceptance Criteria:**
- All v0.2.x patterns work
- No modifications required
- Same behavior as v0.2.x
- Tests pass

**Estimated Time:** 1.5 hours

---

#### Task 4.3: End-to-End Integration Tests

**File:** `tests/integration/test_e2e_patterns.py` (new)

**Description:** Test complete workflows with real API calls.

**Test Scenarios:**
1. **OpenAI + Enrichment**: Trace OpenAI call, enrich span, verify in HoneyHive
2. **Anthropic + Enrichment**: Trace Anthropic call, enrich span, verify
3. **evaluate() + Instance Method**: Full evaluation with enrichment
4. **evaluate() + Free Function**: Legacy evaluation pattern
5. **Multi-Model Evaluation**: Multiple models in one evaluate() call

**Acceptance Criteria:**
- All integrations work
- Data appears in HoneyHive
- Evaluation context propagated
- No errors

**Estimated Time:** 2 hours

---

#### Task 4.4: Performance Benchmarks

**File:** `tests/performance/test_benchmarks.py` (new)

**Description:** Measure performance impact of changes.

**Benchmarks:**
1. **Baggage Propagation**: < 1ms overhead
2. **Tracer Discovery**: < 1ms overhead
3. **Instance Method Call**: ~0.1ms (baseline)
4. **Free Function Call**: ~0.2ms (with discovery)
5. **evaluate() Throughput**: No regression (1000 datapoints)

**Acceptance Criteria:**
- All benchmarks meet targets
- No performance regression vs v0.2.x
- Memory stable
- Results documented

**Estimated Time:** 0.5 hours

---

## Phase 5: Release Preparation

**Objective:** Prepare v1.0 release for Friday deployment.

**Estimated Duration:** 2 hours

**Priority:** CRITICAL (ship date)

### Phase 5 Tasks

#### Task 5.1: Update CHANGELOG

**File:** `CHANGELOG.md`

**Description:** Document all changes in v1.0 release.

**Format:**
```markdown
## [1.0.0] - 2025-10-31

### Added
- Instance methods `HoneyHiveTracer.enrich_span()` and `HoneyHiveTracer.enrich_session()` as primary API
- Selective baggage propagation for evaluation context
- Multi-instance tracer support with isolated context
- Migration guide for v0.2.x users

### Fixed
- Tracer discovery in `evaluate()` pattern with `enrich_span()` calls
- Baggage context propagation with safe key filtering
- Thread isolation for concurrent tracer instances

### Changed
- Instance methods now recommended over free functions
- Free functions marked as legacy (no deprecation warning in v1.0)

### Deprecated
- Free functions `enrich_span()` and `enrich_session()` (removal planned for v2.0)

### Documentation
- README updated with instance method examples
- API reference updated
- Migration guide added
- 10 examples updated to demonstrate best practices
```

**Acceptance Criteria:**
- All changes documented
- Semantic versioning followed
- Clear deprecation notice
- Links to migration guide

**Estimated Time:** 0.5 hours

---

#### Task 5.2: Version Bump and Build

**Files:**
- `pyproject.toml` or `setup.py`
- `src/honeyhive/__init__.py`

**Description:** Bump version to 1.0.0 and build package.

**Steps:**
1. Update version to `1.0.0`
2. Run linters: `pylint src/honeyhive` (≥ 9.5)
3. Run type checker: `mypy src/honeyhive` (0 errors)
4. Run tests: `pytest tests/` (all pass)
5. Build package: `python -m build`
6. Verify package: `twine check dist/*`

**Acceptance Criteria:**
- Version updated
- Linters pass
- Type checker passes
- All tests pass
- Package builds
- Twine check passes

**Estimated Time:** 1 hour

---

#### Task 5.3: Pre-Release Checklist

**Description:** Final validation before PyPI deployment.

**Checklist:**
- [ ] All tests pass (unit, integration, performance)
- [ ] Documentation updated (README, API, migration guide)
- [ ] Examples updated and tested
- [ ] CHANGELOG complete
- [ ] Version bumped to 1.0.0
- [ ] Code quality checks pass (Pylint ≥ 9.5, MyPy 0 errors)
- [ ] Package builds successfully
- [ ] No linter errors
- [ ] Git branch up-to-date
- [ ] PR reviewed (if applicable)
- [ ] Customer onboarding plan ready

**Acceptance Criteria:**
- All checklist items marked ✅
- Ready to deploy to PyPI

**Estimated Time:** 0.5 hours

---

## Dependencies & Ordering

### Critical Path

```
Phase 1 (Baggage Fix)
    ↓
Phase 4 (Testing - depends on Phase 1)
    ↓
Phase 2 (Documentation) ← Can overlap with Phase 4
    ↓
Phase 3 (Examples - depends on Phase 2 docs)
    ↓
Phase 5 (Release)
```

### Parallelization Opportunities

- **Phase 2 + Phase 4**: Documentation can be written while tests run
- **Phase 3 tasks**: Example updates can be parallelized (independent files)

### Blockers

- **Phase 1 → Phase 4**: Testing requires core fix complete
- **Phase 2 → Phase 3**: Examples depend on documentation patterns
- **Phase 1-4 → Phase 5**: Release requires all prior phases complete

---

## Risk Mitigation

### High-Risk Items

1. **Task 1.1 (Baggage Fix)**: Most critical, blocks everything
   - **Mitigation**: Complete Monday AM, test immediately
   
2. **Task 4.1 (Multi-Instance Tests)**: Complex concurrency testing
   - **Mitigation**: Allocate extra time, test thoroughly

3. **Task 5.2 (Build)**: Must pass all quality gates
   - **Mitigation**: Run linters/tests continuously during development

### Contingency Plans

- **If Phase 1 slips**: Cut Phase 3 (examples) → v1.0.1 follow-up
- **If Phase 4 finds bugs**: Friday becomes bug-fix day, ship Monday
- **If documentation slips**: Ship with minimal docs, update post-release

---

## Testing Strategy by Phase

### Phase 1: Unit Tests Required

- Selective baggage propagation
- Tracer discovery with baggage
- Thread-local context isolation

### Phase 4: Integration Tests Required

- End-to-end evaluate() + enrich patterns
- Multi-instance safety
- Backward compatibility
- Performance benchmarks

### Phase 5: Smoke Tests Required

- Package installs cleanly
- Quick start example runs
- No import errors

---

## Success Metrics

### Technical

- ✅ Pylint score ≥ 9.5
- ✅ MyPy 0 errors
- ✅ Test coverage ≥ 90% (changed code)
- ✅ All tests pass (unit + integration)
- ✅ No performance regression (< 5% overhead)

### User-Facing

- ✅ Zero breaking changes in v1.0
- ✅ Instance methods documented as primary
- ✅ Migration guide available
- ✅ 10+ examples updated

### Business

- ✅ Ships Friday (2025-10-31)
- ✅ Two customers onboard successfully
- ✅ No major bugs in first week

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-27  
**Status:** Draft - Pending Approval  
**Estimated Total Time:** 20 hours (5 days, half-days)


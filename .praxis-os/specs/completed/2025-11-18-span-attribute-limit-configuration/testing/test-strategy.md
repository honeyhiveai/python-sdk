# Test Strategy

**Feature:** Span Attribute Limit Configuration & Core Attribute Preservation  
**Date:** 2025-11-18  
**Version:** 1.0

---

## Overview

This document defines the comprehensive testing strategy for span attribute limit configuration and core attribute preservation, covering unit tests, integration tests, performance benchmarks, and end-to-end validation.

---

## Test Pyramid

```
              /\
             /E2E\           End-to-End (5%)
            /------\          - CEO bug regression
           /  Integ \         - Backend validation
          /----------\
         / Perf Bench \     Performance (10%)
        /--------------\     - Initialization overhead
       / Integration    \    - Per-span overhead
      /------------------\
     /     Unit Tests     \ Unit Tests (85%)
    /----------------------\ - Config validation
   /                        \ - Component behavior
  /__________________________ - API contracts
```

**Distribution:**
- Unit Tests: 85% (~26 tests)
- Integration Tests: 10% (~3 tests)
- Performance Benchmarks: 5% (~2 tests)

**Total Estimated Tests:** ~30-35 tests across all phases

---

## Testing Levels

### Level 1: Unit Tests (85%)

**Purpose:** Validate individual components in isolation  
**Scope:** TracerConfig, atomic_provider_detection_and_setup, CoreAttributeSpanProcessor  
**Framework:** pytest  
**Execution:** `tox -e unit`

**Coverage Targets:**
- TracerConfig: 100% line coverage
- atomic_provider_detection_and_setup: 95% line coverage
- Core attribute preservation logic: 95% line coverage

**Key Test Categories:**
1. **Configuration Validation** (8 tests)
   - Default values
   - Custom values
   - Environment variables
   - Validation ranges (negative, min, max)

2. **Provider Integration** (4 tests)
   - New provider creation with limits
   - Existing provider detection
   - Limit application verification
   - Warning logging

3. **Core Preservation** (6 tests - Phase 2)
   - Cache population on start
   - Re-injection on end
   - Memory cleanup
   - Thread safety

4. **Truncation Logic** (4 tests - Phase 3)
   - Strategy selection
   - Truncation application
   - Suffix addition
   - Logging

---

### Level 2: Integration Tests (10%)

**Purpose:** Validate end-to-end workflows across components  
**Scope:** Tracer initialization → Span creation → Export → Backend validation  
**Framework:** pytest + HoneyHive test API  
**Execution:** `tox -e integration-parallel`

**Key Scenarios:**

1. **CEO Bug Regression** (FT-2.3)
   - Simulate SerpAPI response (400+ attributes)
   - Verify no backend rejection
   - Verify session continuity maintained

2. **Edge Case & Stress Testing** (H-7 Requirements - Phase 1B)
   
   **Purpose:** Validate behavior under stress and boundary conditions (From Pessimistic Review H-7)
   
   **2.1 Stress Test: 10K Attributes**
   - Create span with 10,000 attributes (max reasonable stress)
   - Verify memory bounded (~1024 attributes retained)
   - Verify FIFO eviction works correctly (9,000+ evicted)
   - Verify no crashes or exceptions
   - Performance: test completes in <5 seconds
   
   **2.2 Boundary Tests**
   - Test at exact limit (1024 attributes)
   - Test just under limit (1023 attributes)
   - Test just over limit (1025 attributes)
   - Verify oldest attributes evicted first (FIFO)
   
   **2.3 Concurrent Span Test**
   - Create 100 concurrent spans, each with 1500 attributes
   - Verify all spans complete successfully
   - Verify no race conditions
   - Verify memory bounded (100 × 1024 attributes max)
   
   **2.4 Special Characters Test**
   - Keys with dots: `key.with.dots`
   - Keys with dashes: `key-with-dashes`
   - Keys with unicode: `key_with_unicode_🎉`
   - Keys with numbers: `123key`, `key123`
   
   **2.5 Large Value Test**
   - 1MB text attribute
   - 5MB JSON attribute
   - 10MB nested structure
   - Verify `max_span_size` enforcement
   
   **NOT Testing (Out of Scope):**
   - ❌ 1M attributes (unrealistic attack, customer bug responsibility)
   - ❌ Binary data (not real use case)
   - ❌ Malicious patterns (backend/customer responsibility)

3. **Multi-Instrumentor Compatibility** (Phase 2)
   - Initialize OpenAI, Anthropic, AWS instrumentors
   - Verify span limits apply globally
   - Verify no instrumentor conflicts

---

### Level 3: Performance Benchmarks (5%)

**Purpose:** Verify performance targets (<1% overhead)  
**Scope:** Initialization, span creation, core preservation, truncation  
**Framework:** pytest-benchmark  
**Execution:** `pytest tests/performance/ --benchmark-only`

**Benchmark Suite:**

1. **Initialization Overhead** (NFT-4.1)
   - Target: <11ms
   - Measurement: Average of 100 initializations
   - Status: ✅ ~5ms (Phase 1)

2. **Per-Span Overhead** (NFT-4.2)
   - Target: <1ms for 50 attributes
   - Measurement: 1000 spans, average time
   - Status: ✅ ~0.5ms (Phase 1)

3. **Core Preservation Overhead** (NFT-4.3 - Phase 2)
   - Target: <1ms additional overhead
   - Measurement: With vs without preservation
   - Status: 📅 Planned

4. **Truncation Overhead** (NFT-4.4 - Phase 3)
   - Target: <0.1ms per attribute
   - Measurement: Truncation time for 100KB values
   - Status: 📅 Planned

---

## Test Execution Strategy

### Phase 1: Configurable Limits (COMPLETED)

**Test Count:** 13 unit + 2 integration + 2 performance = 17 tests  
**Status:** ✅ ALL PASSING

**Execution:**
```bash
# Unit tests
tox -e unit tests/unit/test_config_models_tracer.py

# Integration tests
tox -e integration-parallel tests/integration/test_span_limits.py

# Performance benchmarks
pytest tests/performance/test_span_overhead.py --benchmark-only
```

**Coverage Achieved:**
- TracerConfig: 100%
- atomic_provider_detection_and_setup: 98%
- _initialize_otel_components: 95%

**Performance Results:**
- Initialization: ~5ms (✅ <11ms target)
- Per-span (50 attrs): ~0.5ms (✅ <1ms target)
- Memory (1K spans): ~5MB (✅ <10MB target)

---

### Phase 2: Core Attribute Preservation (PLANNED)

**Test Count:** 6 unit + 2 integration + 1 performance = 9 tests  
**Status:** 📅 NOT STARTED

**Execution Plan:**
```bash
# Unit tests (new file)
tox -e unit tests/unit/test_core_attribute_processor.py

# Integration tests
tox -e integration-parallel tests/integration/test_core_preservation.py

# Performance benchmark
pytest tests/performance/test_preservation_overhead.py --benchmark-only
```

**Coverage Targets:**
- CoreAttributeSpanProcessor: 95%
- Core attribute priority system: 100%

**Performance Targets:**
- Preservation overhead: <1ms per span
- Memory growth: <1MB per 1K spans (cache overhead)

---

### Phase 3: Smart Truncation (PLANNED)

**Test Count:** 4 unit + 1 integration + 1 performance = 6 tests  
**Status:** 📅 FUTURE

**Execution Plan:**
```bash
# Unit tests (new file)
tox -e unit tests/unit/test_truncation_strategy.py

# Integration test
tox -e integration-parallel tests/integration/test_truncation.py

# Performance benchmark
pytest tests/performance/test_truncation_overhead.py --benchmark-only
```

**Coverage Targets:**
- TruncationStrategy classes: 90%
- _set_span_attributes truncation logic: 95%

**Performance Targets:**
- Truncation overhead: <0.1ms per attribute
- Memory savings: 50% for large payloads

---

## Test Data Management

### Mock Data

**Unit Tests:**
- Use in-memory test mode (`test_mode=True`)
- Mock OTLP exporter to avoid network calls
- Mock HoneyHive API responses

**Integration Tests:**
- Use dedicated HoneyHive test project
- Real OTLP export to backend
- Clean up test spans after execution

### Test Fixtures

**Common Fixtures:**
```python
@pytest.fixture
def tracer_config():
    """Standard TracerConfig for tests."""
    return TracerConfig(
        api_key="test_key",
        project="test_project",
        max_attributes=1024,
        max_attribute_length=10485760,
    )

@pytest.fixture
def reset_tracer_provider():
    """Reset global TracerProvider before each test."""
    trace._TRACER_PROVIDER = None
    trace._TRACER_PROVIDER_INITIALIZED = False
    yield
    # Cleanup after test

@pytest.fixture
def mock_honeyhive_api():
    """Mock HoneyHive API for unit tests."""
    with patch("honeyhive.api.client.HoneyHive") as mock:
        yield mock
```

---

## Continuous Integration

### Pre-Commit Checks

**Run Before Every Commit:**
```bash
# Code formatting
black src/ tests/

# Type checking
mypy src/

# Linting
ruff check src/ tests/

# Fast unit tests (subset)
tox -e unit -- -m "not slow"
```

### Pull Request Checks

**Run on Every PR:**
```bash
# Full unit test suite
tox -e unit

# Integration tests (parallel)
tox -e integration-parallel

# Coverage report
tox -e coverage

# Performance regression check
pytest tests/performance/ --benchmark-compare
```

**Required Criteria:**
- Unit tests: 100% pass rate
- Integration tests: 100% pass rate
- Code coverage: >80% for new code
- Performance: No regression >5%

---

### Nightly Builds

**Run Daily:**
```bash
# Full test suite (all phases)
tox

# Long-running integration tests
pytest tests/integration/ --run-slow

# Memory leak detection
pytest tests/performance/ --memray

# Stress tests
pytest tests/stress/ --workers=10
```

---

## Test Environments

### Local Development

**Setup:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dev dependencies
pip install -e ".[dev,test]"

# Run tests
tox -e unit
```

**Requirements:**
- Python 3.8+
- pytest >=7.0
- OpenTelemetry SDK >=1.20
- HoneyHive Python SDK (current branch)

---

### CI/CD Pipeline (GitHub Actions)

**Test Matrix:**
- Python versions: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- OS: Ubuntu (Linux), macOS, Windows
- OpenTelemetry SDK: 1.20, 1.21, latest

**Parallel Execution:**
- Unit tests: Parallelized across 4 workers
- Integration tests: Parallelized across 2 workers
- Performance benchmarks: Sequential (avoid contention)

---

### Staging Environment

**Purpose:** Pre-production validation  
**Setup:** HoneyHive staging backend  
**Tests:** Full integration suite + CEO regression tests

---

## Regression Testing

### CEO Bug Regression Test

**Frequency:** Every commit  
**Test ID:** FT-2.3, NFT-1.2  
**Purpose:** Ensure SerpAPI large response bug never reoccurs

**Execution:**
```bash
# Run CEO's original script
python sample-tests/openinference-anthropic.py

# Verify spans exported
pytest tests/integration/test_ceo_bug_regression.py
```

**Success Criteria:**
- `get_search_results` span exported
- `honeyhive.session_id` attribute present
- Parent-child relationship maintained
- No "missing session_id" warnings

---

### Backward Compatibility Tests

**Frequency:** Every PR  
**Purpose:** Ensure no breaking changes to existing API

**Test Suite:**
```bash
# Run full existing test suite (unmodified)
tox -e unit -- tests/unit/legacy/
tox -e integration-parallel -- tests/integration/legacy/
```

**Success Criteria:**
- 100% pass rate for all existing tests
- No new deprecation warnings
- API contracts unchanged

---

## Performance Regression Detection

### Benchmark Comparison

**Tool:** pytest-benchmark  
**Baseline:** Phase 1 performance (commit: <SHA>)

**Process:**
1. Run benchmarks on current branch
2. Compare to baseline (stored in `.benchmarks/`)
3. Fail if regression >5%
4. Update baseline after review

**Command:**
```bash
pytest tests/performance/ --benchmark-only --benchmark-compare=0001
```

---

## Test Metrics & Reporting

### Coverage Reports

**Tool:** coverage.py + pytest-cov  
**Target:** >80% line coverage for new code

**Generate Report:**
```bash
tox -e coverage
open htmlcov/index.html
```

**Track by Component:**
- TracerConfig: 100%
- atomic_provider_detection_and_setup: 95%
- CoreAttributeSpanProcessor: 95% (Phase 2)
- TruncationStrategy: 90% (Phase 3)

---

### Test Execution Dashboard

**Track:**
- Total tests: 30 (Phase 1) → 39 (Phase 2) → 45 (Phase 3)
- Pass rate: 100% target
- Average execution time: <5 minutes (unit), <10 minutes (integration)
- Flaky tests: 0 tolerance

---

## Test Maintenance

### Test Review Cadence

- **Weekly:** Review flaky tests, update fixtures
- **Per Phase:** Review test coverage, add missing tests
- **Per Release:** Update regression suite, archive obsolete tests

### Test Documentation

- Inline docstrings for all test functions
- README in tests/ directory with setup instructions
- Test IDs in functional-tests.md and nonfunctional-tests.md

---

## Risk Mitigation

### Flaky Test Prevention

**Strategies:**
- Reset global state before each test (`reset_tracer_provider` fixture)
- Use deterministic test data (no random values)
- Avoid time-based assertions (use retries with timeout)
- Isolate tests (no shared mutable state)

**Detection:**
- Run tests 10x to detect flakiness
- Track flaky tests in CI dashboard
- Fix or quarantine flaky tests immediately

---

### Test Coverage Gaps

**Phase 1 Gaps:**
- ✅ None identified (13/13 FRs covered)

**Phase 2 Risks:**
- Thread safety of CoreAttributeSpanProcessor
- Memory leak detection in long-running applications
- Race conditions in concurrent span creation

**Mitigation:**
- Add thread safety tests with concurrent span creation
- Add memory profiling tests with 10K+ spans
- Use threading.Lock or thread-local storage

---

## Traceability Matrix

| Requirement | Unit Tests | Integration Tests | Performance Tests | Total Coverage |
|-------------|------------|-------------------|-------------------|----------------|
| FR-1 | 2 | 1 | 0 | 3 |
| FR-2 | 2 | 1 | 0 | 3 |
| FR-3 | 2 | 0 | 0 | 2 |
| FR-4 | 2 | 2 | 0 | 4 |
| FR-5 | 4 | 0 | 0 | 4 |
| FR-6 (Phase 2) | 3 | 2 | 1 | 6 |
| FR-7 (Phase 3) | 3 | 1 | 1 | 5 |
| NFR-1 | 1 | 1 | 0 | 2 |
| NFR-2 | 1 | 0 | 0 | 1 |
| NFR-3 | 1 (suite) | 0 | 0 | 1 |
| NFR-4 | 0 | 0 | 4 | 4 |
| NFR-5 | 1 | 1 | 0 | 2 |
| NFR-6 | 1 (review) | 0 | 0 | 1 |

**Total:** 23 unit + 9 integration + 6 performance = 38 tests

---

## Test Execution Timeline

| Phase | Unit Tests | Integration Tests | Performance | Total Time |
|-------|------------|-------------------|-------------|------------|
| Phase 1 | ~2 min | ~5 min | ~1 min | ~8 min |
| Phase 2 | ~3 min | ~7 min | ~2 min | ~12 min |
| Phase 3 | ~3.5 min | ~8 min | ~2.5 min | ~14 min |

**CI Pipeline Total:** ~15 minutes (parallelized)

---

**Document Status:** Complete  
**Last Updated:** 2025-11-18  
**Next Review:** After Phase 2 implementation


# Integration Test Analysis: Documentation to Test Mapping

## Executive Summary

**Total Integration Tests:** 226 tests across 34 files (legacy) + 30 new tests in `tests_v2/integrations/`  
**Primary Issue:** Most tests hit real backend APIs, causing slow execution (>5 min for full suite)

### NEW: Provider Integration Test Suite (`tests_v2/integrations/`)

| Test File | Provider | Tests | Docs Coverage |
|-----------|----------|-------|---------------|
| `test_openai_integration.py` | OpenAI | 6 | `/integrations/openai.mdx` |
| `test_anthropic_integration.py` | Anthropic | 4 | `/integrations/anthropic.mdx` |
| `test_langchain_integration.py` | LangChain/LangGraph | 5 | `/integrations/langchain.mdx`, `/integrations/langgraph.mdx` |
| `test_evaluate_integration.py` | evaluate() | 5 | `/evaluation/running-experiments.mdx` |
| `test_tracing_integration.py` | Core Tracing | 10 | `/tracing/introduction.mdx`, `/tracing/custom-spans.mdx` |

**Run with:**
```bash
tox -e integrations              # All providers
tox -e integrations-openai       # OpenAI only
tox -e integrations-anthropic    # Anthropic only
tox -e integrations-langchain    # LangChain only
tox -e integrations-evaluate     # evaluate() only
tox -e integrations-tracing      # Core tracing only
```

---

---

## Documentation Page to Test Mapping

### CRITICAL DOCUMENTATION PAGES (Customer-Facing Features)

| Documentation Page | Test File(s) | Coverage Status | Priority |
|-------------------|--------------|-----------------|----------|
| **Tracing Introduction** (`/tracing/introduction.mdx`) | `test_tracer_integration.py` (26 tests) | ✅ Good | P0 |
| **Custom Spans / @trace** (`/tracing/custom-spans.mdx`, `/sdk-reference/python/api/decorators.mdx`) | `test_tracer_integration.py`, `tests_v2/unit/test_tracer_instrumentation_decorators.py` | ✅ Good | P0 |
| **Enriching Traces** (`/tracing/enrich-traces.mdx`) | `test_tracer_integration.py::TestUnifiedEnrichSpanIntegration` | ✅ Good | P0 |
| **Distributed Tracing** (`/tracing/distributed-tracing.mdx`) | `test_multi_instance_tracer_integration.py` (12 tests) | ✅ Good | P0 |
| **Running Experiments / evaluate()** (`/evaluation/running-experiments.mdx`, `/sdk-reference/python-experiments-ref.mdx`) | `test_experiments_integration.py` (8 tests), `test_evaluate_enrich.py` (5 tests) | ✅ Good | P0 |

### API DOCUMENTATION PAGES

| Documentation Page | Test File(s) | Coverage Status | Priority |
|-------------------|--------------|-----------------|----------|
| **Datasets API** (`/api-reference/datasets/`) | `api/test_datasets_api.py` (7 tests) | ✅ Good | P1 |
| **Datapoints API** (`/api-reference/datapoints/`) | `api/test_datapoints_api.py` (6 tests) | ✅ Good | P1 |
| **Configurations API** (`/api-reference/configurations/`) | `api/test_configurations_api.py` (5 tests) | ✅ Good | P1 |
| **Projects API** (`/api-reference/projects/`) | `api/test_projects_api.py` (4 tests) | ✅ Good | P1 |
| **Metrics API** (`/api-reference/metrics/`) | `api/test_metrics_api.py` (4 tests) | ✅ Good | P1 |
| **Experiments API** (`/api-reference/experiments/`) | `api/test_experiments_api.py` (4 tests) | ✅ Good | P1 |
| **Tools API** (`/api-reference/tools/`) | `api/test_tools_api.py` (6 tests) | ✅ Good | P1 |

### INTEGRATION DOCUMENTATION PAGES

| Documentation Page | Test File(s) | Coverage Status | Priority |
|-------------------|--------------|-----------------|----------|
| **OpenAI Integration** (`/integrations/openai.mdx`) | `test_real_instrumentor_integration.py` (4 tests), `test_real_instrumentor_integration_comprehensive.py` (10 tests) | ⚠️ Partial (tests exist but flaky) | P1 |
| **LangChain Integration** (`/integrations/langchain.mdx`) | None specific | ❌ Missing | P2 |
| **LiteLLM Integration** (`/integrations/litellm.mdx`) | None specific | ❌ Missing | P2 |

### ADVANCED DOCUMENTATION PAGES

| Documentation Page | Test File(s) | Coverage Status | Priority |
|-------------------|--------------|-----------------|----------|
| **OpenTelemetry Concepts** (`/concepts/opentelemetry.mdx`) | `test_otel_*.py` (50+ tests) | ✅ Good | P2 |
| **Multi-Instance Tracers** (`/concepts/multi-instance.mdx`) | `test_multi_instance_tracer_integration.py` (12 tests), `test_real_api_multi_tracer.py` (9 tests) | ✅ Good | P2 |
| **Multithreading** (`/tracing/multithreading.mdx`) | `test_otel_concurrency_integration.py` (4 tests) | ✅ Good | P2 |

---

## DOCUMENTATION PAGES WITHOUT INTEGRATION TESTS

### HIGH PRIORITY GAPS (P1)

| Documentation Page | Gap Description | Recommended Action |
|-------------------|-----------------|-------------------|
| `/tracing/client-side-evals.mdx` | No tests for client-side evaluation patterns | Create `test_client_side_evals_integration.py` |
| `/tracing/setting-user-feedback.mdx` | User feedback enrichment not specifically tested | Add tests to `test_tracer_integration.py` |
| `/tracing/setting-user-properties.mdx` | User properties enrichment not specifically tested | Add tests to `test_tracer_integration.py` |
| `/evaluation/creating-evaluators.mdx` | `@evaluator` decorator not integration-tested | Add to `test_experiments_integration.py` |

### MEDIUM PRIORITY GAPS (P2)

| Documentation Page | Gap Description | Recommended Action |
|-------------------|-----------------|-------------------|
| `/integrations/langchain.mdx` | No LangChain-specific integration tests | Create `test_langchain_integration.py` |
| `/integrations/litellm.mdx` | No LiteLLM-specific integration tests | Create `test_litellm_integration.py` |
| `/integrations/anthropic.mdx` | No Anthropic-specific integration tests | Create `test_anthropic_integration.py` |
| `/tracing/mcp-tracing.mdx` | No MCP tracing tests | Create `test_mcp_tracing_integration.py` |

### LOW PRIORITY GAPS (P3)

| Documentation Page | Gap Description |
|-------------------|-----------------|
| `/prompts/overview.mdx` | Prompt management not tested |
| `/monitoring/overview.mdx` | Monitoring/alerts not tested (UI feature) |
| `/workspace/*.mdx` | Workspace features not SDK-testable |

---

## Test Categorization by Speed

### FAST TESTS (< 5s, no real API calls)
- Unit tests in `tests_v2/unit/` - **1738 tests** across 37 files ✅

**Unit Test Coverage by Documentation Topic:**

| Documentation Topic | Unit Test File(s) | Test Count |
|--------------------|-------------------|------------|
| @trace, @atrace decorators | `test_tracer_instrumentation_decorators.py` | 67 |
| HoneyHiveTracer init | `test_tracer_instrumentation_initialization.py` | 63 |
| evaluate() function | `test_experiments_core.py` | 45+ |
| Tracer configuration | `test_tracer_core_config_interface.py`, `test_config_models_*.py` | 100+ |
| Distributed tracing/context | `test_tracer_processing_context_distributed.py` | 50+ |
| OTLP export | `test_tracer_processing_otlp_*.py` | 80+ |
| Flush/shutdown lifecycle | `test_tracer_lifecycle_flush.py`, `test_tracer_lifecycle_shutdown.py` | 60+ |
| Git info capture | `test_tracer_utils_git.py` | 30+ |
| enrich_span/session | `test_tracer_processing_context.py` | 100+ |

### MEDIUM TESTS (5-30s, mock API or local only)  
- `test_model_integration.py` - 6 tests (some pass, 4 fail due to schema changes)
- `test_simple_integration.py` - 7 tests (some pass, 4 fail due to schema changes)

### SLOW TESTS (30s+, require real API backend)
- `test_tracer_integration.py` - 26 tests (hits backend for validation)
- `test_experiments_integration.py` - 8 tests (creates real experiment runs)
- `test_otel_backend_verification_integration.py` - 19 tests
- `tests/integration/api/*.py` - 36 tests (CRUD operations)
- All `test_*_backend_*.py` files

---

## Known Failures

### API Schema Changes (4 tests)
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for CreateConfigurationRequest
parameters.call_type
  Field required
```
**Files affected:**
- `test_simple_integration.py`
- `test_model_integration.py`

### Backend Verification Failures (ongoing)
```
ValidationError: Span export validation failed: Backend verification failed after 10 attempts: 
EventsAPI.get_by_session_id() missing 1 required positional argument: 'project'
```
**Files affected:**
- `test_batch_configuration.py`
- Various `test_otel_backend_verification_*.py`

---

## Recommendations

### Immediate (This PR)
1. Add `@pytest.mark.slow` to all backend-hitting tests
2. Create tox environment `integration-fast` that excludes slow tests
3. Run slow tests only in nightly CI, not on every PR

### Short-term
1. Fix `call_type` schema validation errors (4 tests)
2. Fix `EventsAPI.get_by_session_id` signature (backend API change)
3. Add missing `@pytest.mark.real_api` markers

### Long-term
1. Create integration tests for LangChain, LiteLLM, Anthropic integrations
2. Add client-side evaluation tests
3. Add user feedback/properties enrichment tests

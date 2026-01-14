# Skipped Integration Tests Summary

This document summarizes all skipped integration tests and the reasons for each skip.

## Table of Contents
- [End-to-End Validation Tests](#end-to-end-validation-tests)
- [HoneyHive Attributes Backend Integration](#honeyhive-attributes-backend-integration)
- [Experiments Integration](#experiments-integration)
- [Evaluate Enrich Integration](#evaluate-enrich-integration)
- [V1 Immediate Ship Requirements](#v1-immediate-ship-requirements)
- [Real Instrumentor Integration](#real-instrumentor-integration)
- [E2E Patterns](#e2e-patterns)
- [OpenTelemetry Tests](#opentelemetry-tests)
- [API Tests](#api-tests)

---

## End-to-End Validation Tests

**File:** `tests/integration/test_end_to_end_validation.py`

### 1. `test_session_event_relationship_validation`
- **Reason:** GET /v1/sessions/{session_id} endpoint not deployed on testing backend (returns 404 Route not found)
- **Impact:** Cannot validate session-event relationships with full data validation

### 2. `test_configuration_workflow_validation`
- **Reason:** Configuration list endpoint not returning newly created configurations - backend data propagation issue
- **Impact:** Cannot validate configuration creation and retrieval workflow

### 3. `test_cross_entity_data_consistency`
- **Reason:** GET /v1/sessions/{session_id} endpoint not deployed on testing backend (returns 404 Route not found)
- **Impact:** Cannot test data consistency across multiple entity types (configurations, sessions, datapoints)

---

## HoneyHive Attributes Backend Integration

**File:** `tests/integration/test_honeyhive_attributes_backend_integration.py`

All 5 tests in this file are skipped with the same reason:

### 1. `test_decorator_event_type_backend_verification`
### 2. `test_direct_span_event_type_inference`
### 3. `test_all_event_types_backend_conversion`
### 4. `test_multi_instance_attribute_isolation`
### 5. `test_comprehensive_attribute_backend_verification`
- **Reason:** GET /v1/events/{session_id} endpoint not deployed on testing backend (returns 'Route not found')
- **Impact:** Cannot verify that HoneyHive attributes are properly processed and stored in the backend until this endpoint is deployed

---

## Experiments Integration

**File:** `tests/integration/test_experiments_integration.py`

### Entire test class skipped conditionally
- **Condition:** `os.environ.get("HH_SOURCE", "").startswith("github-actions")`
- **Reason:** Requires write permissions not available in CI
- **Impact:** All experiment integration tests are skipped in CI environments

---

## Evaluate Enrich Integration

**File:** `tests/integration/test_evaluate_enrich.py`

### Entire module skipped
- **Reason:** Skipped pending v1 evaluation API migration - evaluate() function no longer exists in v1
- **Impact:** All tests in this module are skipped as they test v0 evaluate() functionality

### Additional conditional skip
- **Condition:** `not os.environ.get("HH_API_KEY")`
- **Reason:** Requires HH_API_KEY environment variable
- **Impact:** Tests require API credentials to run

---

## V1 Immediate Ship Requirements

**File:** `tests/integration/test_v1_immediate_ship_requirements.py`

### Entire test class skipped conditionally
- **Condition:** `os.environ.get("HH_SOURCE", "").startswith("github-actions")`
- **Reason:** Requires write permissions not available in CI
- **Impact:** All v1.0 immediate ship requirement tests are skipped in CI environments

---

## Real Instrumentor Integration

**File:** `tests/integration/test_real_instrumentor_integration.py`

### 1. `test_real_openai_instrumentor_integration`
- **Condition:** `not os.getenv("OPENAI_API_KEY")`
- **Reason:** Requires OPENAI_API_KEY for real instrumentor test
- **Impact:** Cannot test with real OpenAI instrumentor to catch integration bugs

---

## E2E Patterns

**File:** `tests/integration/test_e2e_patterns.py`

### Entire module skipped conditionally
- **Condition:** `not os.environ.get("HH_API_KEY")`
- **Reason:** Requires HH_API_KEY environment variable
- **Impact:** All end-to-end pattern tests require API credentials

---

## OpenTelemetry Tests

Multiple files have OpenTelemetry tests skipped conditionally:

### Files affected:
- `tests/integration/test_otel_otlp_export_integration.py`
- `tests/integration/test_otel_edge_cases_integration.py`
- `tests/integration/test_otel_performance_integration.py`
- `tests/integration/test_otel_backend_verification_integration.py`
- `tests/integration/test_otel_resource_management_integration.py`
- `tests/integration/test_otel_concurrency_integration.py`
- `tests/integration/test_otel_span_lifecycle_integration.py`
- `tests/integration/test_otel_context_propagation_integration.py`
- `tests/integration/test_otel_performance_regression_integration.py`

### Skip condition:
- **Condition:** `not OTEL_AVAILABLE`
- **Reason:** OpenTelemetry not available
- **Impact:** All OpenTelemetry integration tests are skipped if OpenTelemetry dependencies are not installed

---

## API Tests

### Tools API

**File:** `tests/integration/api/test_tools_api.py`

#### 1. `test_get_tool`
- **Reason:** Client Bug: tools.delete() passes tool_id but service expects function_id - cleanup would fail
- **Impact:** Cannot test tool retrieval by ID due to cleanup bug

#### 2. `test_get_tool_404`
- **Reason:** v1 API doesn't have get_tool method, only list
- **Impact:** Cannot test 404 for missing tool

#### 3. `test_list_tools`
- **Reason:** Client Bug: tools.delete() passes tool_id but service expects function_id - cleanup would fail
- **Impact:** Cannot test tool listing due to cleanup bug

#### 4. `test_update_tool`
- **Reason:** Backend returns 400 error for updateTool endpoint
- **Impact:** Cannot test tool schema updates

#### 5. `test_delete_tool`
- **Reason:** Client Bug: tools.delete() passes tool_id but generated service expects function_id parameter
- **Impact:** Cannot test tool deletion

---

### Datapoints API

**File:** `tests/integration/api/test_datapoints_api.py`

#### 1. `test_bulk_operations`
- **Reason:** DatapointsAPI bulk operations may not be implemented yet
- **Impact:** Cannot test bulk create/update/delete operations

---

### Datasets API

**File:** `tests/integration/api/test_datasets_api.py`

#### 1. `test_list_datasets_include_datapoints`
- **Reason:** Backend issue with include_datapoints parameter
- **Impact:** Cannot test dataset listing with datapoints included

#### 2. `test_update_dataset`
- **Reason:** UpdateDatasetRequest requires dataset_id field - needs investigation
- **Impact:** Cannot test dataset metadata updates

---

### Configurations API

**File:** `tests/integration/api/test_configurations_api.py`

#### 1. `test_get_configuration`
- **Reason:** v1 API: no get_configuration method, must use list() to retrieve
- **Impact:** Cannot test configuration retrieval by ID

---

### Metrics API

**File:** `tests/integration/api/test_metrics_api.py`

#### 1. `test_create_metric`
- **Reason:** Backend Issue: createMetric endpoint returns 400 Bad Request error
- **Impact:** Cannot test custom metric creation

#### 2. `test_get_metric`
- **Reason:** Backend Issue: createMetric endpoint returns 400 Bad Request error (blocks retrieval test)
- **Impact:** Cannot test metric retrieval (depends on create working)

#### 3. `test_list_metrics`
- **Reason:** Backend Issue: createMetric endpoint returns 400 Bad Request error (blocks list test)
- **Impact:** Cannot test metric listing (depends on create working)

#### 4. `test_compute_metric`
- **Reason:** MetricsAPI.compute_metric() requires event_id and may not be fully implemented
- **Impact:** Cannot test metric computation on events

---

### Projects API

**File:** `tests/integration/api/test_projects_api.py`

#### 1. `test_create_project`
- **Reason:** Backend Issue: create_project returns 'Forbidden route' error
- **Impact:** Cannot test project creation

#### 2. `test_get_project`
- **Reason:** Backend Issue: getProjects endpoint returns 404 Not Found error
- **Impact:** Cannot test project retrieval

#### 3. `test_list_projects`
- **Reason:** Backend Issue: getProjects endpoint returns 404 Not Found error
- **Impact:** Cannot test project listing

#### 4. `test_update_project`
- **Reason:** Backend Issue: create_project returns 'Forbidden route' error
- **Impact:** Cannot test project updates (depends on create working)

---

### Experiments API

**File:** `tests/integration/api/test_experiments_api.py`

#### 1. `test_create_run`
- **Reason:** Spec Drift: CreateRunRequest requires event_ids (mandatory field)
- **Impact:** Cannot test run creation without pre-existing events

#### 2. `test_get_run`
- **Reason:** Spec Drift: CreateRunRequest requires event_ids (mandatory field)
- **Impact:** Cannot test run retrieval (depends on create working)

#### 3. `test_list_runs`
- **Reason:** Spec Drift: CreateRunRequest requires event_ids (mandatory field)
- **Impact:** Cannot test run listing (depends on create working)

#### 4. `test_run_experiment`
- **Reason:** ExperimentsAPI.run_experiment() requires complex setup with dataset and metrics
- **Impact:** Cannot test async experiment execution

---

## Summary Statistics

### By Skip Reason Category

1. **Backend Endpoint Not Deployed (8 tests)**
   - GET /v1/sessions/{session_id} endpoint (3 tests)
   - GET /v1/events/{session_id} endpoint (5 tests)

2. **Backend Issues/Errors (11 tests)**
   - 400 Bad Request errors (4 tests)
   - 404 Not Found errors (2 tests)
   - Forbidden route errors (2 tests)
   - Data propagation issues (1 test)
   - Parameter issues (2 tests)

3. **Client/API Bugs (6 tests)**
   - tools.delete() parameter mismatch (4 tests)
   - Spec drift issues (2 tests)

4. **Missing API Methods (4 tests)**
   - v1 API doesn't have get_tool method (1 test)
   - v1 API doesn't have get_configuration method (1 test)
   - Bulk operations not implemented (1 test)
   - compute_metric may not be implemented (1 test)

5. **Environment/Conditional Skips (5 test classes/modules)**
   - CI environment restrictions (2 test classes)
   - Missing API keys (2 modules)
   - Missing dependencies (1 test)

6. **Migration/Deprecation (1 module)**
   - v0 evaluate() function no longer exists in v1 (entire module)

7. **Complex Setup Required (1 test)**
   - Requires complex setup with dataset and metrics

### Total Skipped Tests
- **Individual test methods:** 21 API tests + 8 backend endpoint tests + 1 real instrumentor test = **30 individual tests**
- **Entire modules/classes:** 5 (conditionally skipped)
  - Experiments Integration (conditional on CI)
  - Evaluate Enrich Integration (entire module)
  - V1 Immediate Ship Requirements (conditional on CI)
  - E2E Patterns (conditional on HH_API_KEY)
  - Real Instrumentor Integration (1 test conditional on OPENAI_API_KEY)
- **OpenTelemetry tests:** 9 files (conditionally skipped if OTEL not available)

**Note:** The GET /v1/events endpoint mentioned in previous versions of this document was removed from the API as it never existed in production. Event verification now uses getEventsBySessionId, which requires a valid session.

---

## Recommendations

1. **Backend Endpoints:** Deploy GET /v1/sessions/{session_id} and GET /v1/events/{session_id} endpoints
2. **Backend Bugs:** Fix 400/404/Forbidden errors in Metrics, Projects, and Tools APIs
4. **Client Bugs:** Fix tools.delete() parameter mismatch (tool_id vs function_id)
5. **API Spec:** Update OpenAPI spec to match actual backend requirements (event_ids in CreateRunRequest)
6. **Documentation:** Document which endpoints require write permissions vs read-only access
7. **Migration:** Complete v1 evaluation API migration to enable evaluate_enrich tests

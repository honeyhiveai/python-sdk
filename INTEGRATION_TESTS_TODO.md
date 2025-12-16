# Integration Tests TODO

Tracking issues blocking integration tests from passing.

## API Endpoints Not Yet Deployed

| Endpoint | Used By | Status |
|----------|---------|--------|
| `POST /v1/session/start` | `test_simple_integration.py::test_session_event_workflow_with_validation` | ❌ Missing |
| `GET /v1/events` | `test_honeyhive_attributes_backend_integration.py` (all 5 tests), `test_simple_integration.py::test_session_event_workflow_with_validation` | ❌ Missing |
| `POST /v1/events` | `test_simple_integration.py::test_session_event_workflow_with_validation` | ⚠️ Untested (blocked by session) |
| `GET /v1/session/{id}` | `test_simple_integration.py::test_session_event_workflow_with_validation` | ⚠️ Untested (blocked by session) |

## API Endpoints Returning Errors

| Endpoint | Error | Used By | Status |
|----------|-------|---------|--------|
| `POST /v1/metrics` (createMetric) | 400 Bad Request | `test_metrics_api.py::test_create_metric`, `test_get_metric`, `test_list_metrics` | ❌ Broken |
| `GET /v1/projects` (getProjects) | 404 Not Found | `test_projects_api.py::test_get_project`, `test_list_projects` | ❌ Broken |
| `GET /v1/experiments/{run_id}/result` (getExperimentResult) | TODOSchema validation error - missing 'message' field | All `test_experiments_integration.py` tests (7 tests) | ❌ Broken |

## Tests Passing

- `test_simple_integration.py::test_basic_datapoint_creation_and_retrieval` ✅
- `test_simple_integration.py::test_basic_configuration_creation_and_retrieval` ✅
- `test_simple_integration.py::test_model_serialization_workflow` ✅
- `test_simple_integration.py::test_error_handling` ✅
- `test_simple_integration.py::test_environment_configuration` ✅
- `test_simple_integration.py::test_fixture_availability` ✅

## Tests Failing (Blocked)

- `test_simple_integration.py::test_session_event_workflow_with_validation` - blocked by missing `/v1/session/start`

## Generated Client Issues

Several auto-generated API endpoints return `Dict[str, Any]` instead of properly typed Pydantic models due to incomplete OpenAPI specifications:

- **Events Service**: All endpoints (createEvent, getEvents, createModelEvent, etc.)
- **Session Service**: startSession endpoint
- **Datapoints Service**: getDatapoint endpoint (others are properly typed)
- **Projects Service**: Uses TODOSchema placeholder models

**Details:** See [UNTYPED_ENDPOINTS.md](./UNTYPED_ENDPOINTS.md) for full analysis and long-term fix plan.

**Impact:** Workarounds like `_get_field()` helper needed to handle both dict and object responses. Will be resolved when OpenAPI spec is fixed and client is regenerated.

## Notes

- Staging server: `https://api.testing-dp-1.honeyhive.ai`
- v1 API endpoints use `/v1/` prefix
- Sessions and Events APIs use dict-based requests (no typed Pydantic models) - see UNTYPED_ENDPOINTS.md

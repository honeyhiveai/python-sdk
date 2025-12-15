# Integration Tests TODO

Tracking issues blocking integration tests from passing.

## API Endpoints Not Yet Deployed

| Endpoint | Used By | Status |
|----------|---------|--------|
| `POST /v1/session/start` | `test_simple_integration.py::test_session_event_workflow_with_validation` | ❌ Missing |
| `POST /v1/events` | `test_simple_integration.py::test_session_event_workflow_with_validation` | ⚠️ Untested (blocked by session) |
| `GET /v1/session/{id}` | `test_simple_integration.py::test_session_event_workflow_with_validation` | ⚠️ Untested (blocked by session) |
| `GET /v1/events` | `test_simple_integration.py::test_session_event_workflow_with_validation` | ⚠️ Untested (blocked by session) |

## API Endpoints Returning Errors

| Endpoint | Error | Used By | Status |
|----------|-------|---------|--------|
| `POST /v1/metrics` (createMetric) | 400 Bad Request | `test_metrics_api.py::test_create_metric`, `test_get_metric`, `test_list_metrics` | ❌ Broken |
| `GET /v1/projects` (getProjects) | 404 Not Found | `test_projects_api.py::test_get_project`, `test_list_projects` | ❌ Broken |

## Tests Passing

- `test_simple_integration.py::test_basic_datapoint_creation_and_retrieval` ✅
- `test_simple_integration.py::test_basic_configuration_creation_and_retrieval` ✅
- `test_simple_integration.py::test_model_serialization_workflow` ✅
- `test_simple_integration.py::test_error_handling` ✅
- `test_simple_integration.py::test_environment_configuration` ✅
- `test_simple_integration.py::test_fixture_availability` ✅

## Tests Failing (Blocked)

- `test_simple_integration.py::test_session_event_workflow_with_validation` - blocked by missing `/v1/session/start`

## Notes

- Staging server: `https://api.testing-dp-1.honeyhive.ai`
- v1 API endpoints use `/v1/` prefix
- Sessions and Events APIs use dict-based requests (no typed Pydantic models)

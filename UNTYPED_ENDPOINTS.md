# Untyped Endpoints - Generated Client Incomplete Models

## Overview

Several endpoints in the auto-generated API client return `Dict[str, Any]` instead of properly typed Pydantic models. This is due to incomplete or ambiguous OpenAPI specification definitions that the code generator cannot handle.

This causes the need for workarounds like `_get_field()` helper functions that handle both dict and object-based responses.

## Affected Endpoints

### Events Service (5 untyped endpoints)
- `Events_service.createEvent()` → `Dict[str, Any]`
- `Events_service.getEvents()` → `Dict[str, Any]`
- `Events_service.createModelEvent()` → `Dict[str, Any]`
- `Events_service.createEventBatch()` → `Dict[str, Any]`
- `Events_service.createModelEventBatch()` → `Dict[str, Any]`

**Root Cause:** OpenAPI spec likely uses `anyOf` or generic response schemas that the generator can't translate to typed models.

**Impact:**
- Backend verification code uses `_get_field()` helper to handle dict responses
- Tests must use dict access patterns (`event["field"]`) instead of attribute access
- No IDE autocomplete support for response fields

### Session Service (1 untyped endpoint)
- `Session_service.startSession()` → `Dict[str, Any]`

**Root Cause:** No proper `SessionStartResponse` model defined in OpenAPI spec.

**Impact:**
- Session start responses accessed as dicts
- Tests use `session["session_id"]` instead of `session.session_id`
- No validation of response structure

### Datapoints Service (1 partially untyped endpoint)
- `Datapoints_service.getDatapoint()` → `Dict[str, Any]`
- **Note:** Other datapoint methods (`getDatapoints`, `createDatapoint`, etc.) are properly typed

**Root Cause:** Inconsistent OpenAPI spec definitions - some endpoints have response models, others don't.

**Impact:**
- Single datapoint retrieval returns untyped dict
- List/create operations return proper types
- Inconsistent handling in client code

### Projects Service (Placeholder models)
- `Projects_service.*` endpoints use `TODOSchema` placeholder class
- Indicates these endpoints were auto-generated but specs are incomplete

**Root Cause:** OpenAPI spec not finalized for project management endpoints.

**Impact:**
- No real type safety for project operations
- Placeholder models likely don't match actual API responses

## Workarounds in Current Code

### `_get_field()` Helper Function
Located in: `tests/utils/backend_verification.py`

```python
def _get_field(obj: Any, field: str, default: Any = None) -> Any:
    """Get field from object or dict, supporting both attribute and dict access."""
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)
```

**Why it exists:** Some response objects are dicts while others are typed models. This helper abstracts that difference.

**Better approach:** Once specs are fixed and regenerated, this will no longer be needed.

## Long-term Fix

### Phase 1: OpenAPI Spec Updates
1. Define response models for all Events endpoints:
   - `CreateEventResponse` for `createEvent()`
   - `GetEventsResponse` for `getEvents()`
   - etc.

2. Define `SessionStartResponse` model for session start endpoint

3. Define proper `GetDatapointResponse` model (ensure consistency with `GetDatapointsResponse`)

4. Replace `TODOSchema` placeholders with real project models

### Phase 2: Client Regeneration
1. Update OpenAPI spec in `openapi.yaml` or source
2. Run: `python scripts/generate_client.py --use-orjson`
3. Remove workarounds like `_get_field()` helper
4. Update tests to use proper attribute access

### Phase 3: Testing
1. Run integration tests to verify all endpoints work with typed responses
2. Remove dict-based response handling code
3. Add type checking validation to CI/CD

## Files Currently Working Around This

- `tests/utils/backend_verification.py` - Uses `_get_field()` helper
- `tests/utils/validation_helpers.py` - Uses `_get_field()` helper
- `tests/integration/test_end_to_end_validation.py` - Uses dict key access for session responses
- `src/honeyhive/api/client.py` - EventsAPI and sessions methods return Dict

## Status

**Current:** Documented workaround, functional but not type-safe
**Target:** All endpoints return proper Pydantic models with full type safety
**Priority:** Medium - functionality works, but developer experience could be better

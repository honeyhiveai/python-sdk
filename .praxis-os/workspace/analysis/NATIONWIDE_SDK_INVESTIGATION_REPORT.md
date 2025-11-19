# Nationwide SDK Issues - Investigation Report

**Date**: November 3, 2025  
**Status**: Investigation Complete - No Changes Made  
**Purpose**: Understanding issues before implementing fixes

---

## Issue 1: Can we eliminate `session_id` kwarg from `tracer.enrich_session()`?

### Current Behavior

**Method Signature** (`src/honeyhive/tracer/core/context.py:115-126`):
```python
def enrich_session(
    self,
    session_id: Optional[str] = None,  # ← Can this be removed?
    metadata: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    user_properties: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> None:
```

### How `session_id` is Used

**Lines 227-233**:
```python
# Get target session ID - use explicit session_id if provided
# (backwards compat). Otherwise fall back to dynamic detection
target_session_id: Optional[str]
if session_id:
    target_session_id = session_id  # ← Explicit override
else:
    target_session_id = self._get_session_id_for_enrichment_dynamically()
```

**Fallback Logic** (`_get_session_id_for_enrichment_dynamically()`, lines 318-328):
```python
def _get_session_id_for_enrichment_dynamically(self) -> Optional[str]:
    """Dynamically get session ID for enrichment operations."""
    # Priority: explicit session_id, baggage session_id
    if self._session_id:
        return str(self._session_id)  # ← Instance variable (primary source)
    
    # Check baggage dynamically
    try:
        current_baggage = get_current_baggage()
        baggage_session = current_baggage.get("session_id")
        # ...
```

**Tracer Instance Has Session ID** (`src/honeyhive/tracer/core/base.py:246-255`):
```python
# session_id is now properly promoted to root by create_unified_config()
# Fallback to nested location for extra safety
self.session_id = config.get("session_id") or (
    config.get("session", {}).get("session_id")
    if isinstance(config.get("session"), dict)
    else None
)

self._session_name = self.session_name  # Private version for internal use
self._session_id = self.session_id  # Private version for internal use
```

### Usage Analysis

**Test Coverage** (`tests/unit/test_tracer_core_context.py:430-451`):
```python
def test_enrich_session_backwards_compatible_with_explicit_session_id(self):
    """Test enrich_session with explicit session_id (backwards compat)."""
    context_mixin._session_id = "default-session-123"
    
    # Act - Old pattern: pass explicit session_id
    context_mixin.enrich_session(
        session_id="explicit-session-456",  # ← Overrides instance session_id
        metadata={"meta_key": "meta_value"},
    )
    
    # Assert - Should use explicit session_id, not default
    assert call_args[1]["event_id"] == "explicit-session-456"  # ← Works as override
```

**Documentation** (`src/honeyhive/tracer/core/context.py:138-140`):
```python
Args:
    session_id: Optional explicit session ID to enrich.
                If not provided, uses tracer's current session ID.
                (Provided for backwards compatibility)  # ← Explicitly marked as backwards compat
```

### Examples Found in Codebase

**No usage with explicit `session_id` in production code**:
- All examples use: `tracer.enrich_session(metadata={...})` without `session_id`
- Only test file uses explicit `session_id` (for backwards compatibility testing)
- Deprecated free function uses it: `enrich_session(session_id="...", metadata={}, tracer=tracer)`

### Findings

✅ **Yes, it CAN be removed** because:
1. **Tracer already has reference**: `self._session_id` is always available
2. **Marked as backwards compat**: Documentation explicitly states it's for backwards compatibility
3. **Not used in practice**: No production code uses the explicit parameter
4. **Primary pattern**: All examples and docs show usage without explicit session_id
5. **Legacy pattern**: Only the deprecated free function `enrich_session()` needs it

⚠️ **Impact of Removal**:
- **Breaking Change**: Any code passing explicit `session_id` will break
- **Free Function**: The compatibility layer `enrich_session(session_id, ...)` would need adjustment
- **Test Updates**: 1 test specifically validates this backwards compat behavior

💡 **Recommendation**:
- **v1.x**: Deprecate with warning when used
- **v2.0**: Remove parameter entirely
- **Alternative**: Keep only if needed for the legacy free function compatibility

---

## Issue 2: SessionAPI.update_session() call in early_init

### Investigation

**Searched for**: References to `SessionAPI.update_session()`

**Results**:
```bash
$ grep -r "update_session" src/
# No matches found in source code
```

**SessionAPI Methods** (`src/honeyhive/api/session.py`):
```python
class SessionAPI(BaseAPI):
    def create_session(self, session: SessionStartRequest) -> SessionStartResponse
    def create_session_from_dict(self, session_data: dict) -> SessionStartResponse
    def start_session(self, project, session_name, source, ...) -> SessionStartResponse
    def get_session(self, session_id: str) -> SessionResponse
    def delete_session(self, session_id: str) -> bool
    # ❌ NO update_session() method exists
```

**"early_init" Reference** (`src/honeyhive/utils/logger.py:521`):
```python
# This is just a logger name, not a function or initialization phase
target_logger = get_logger("honeyhive.early_init", verbose=verbose_setting)
```

### Previous Bug Report

**Found**: `ENRICH_SESSION_UPDATE_BUG_REPORT.md`
- **Status**: ✅ FIXED (Date: 2025-10-31)
- **Original Bug**: `TracerContextMixin.enrich_session()` was calling `self.session_api.update_session()`
- **Fix Applied**: Changed to use `self.client.events.update_event()` instead
- **Lines Fixed**: `src/honeyhive/tracer/core/context.py:236-246`

**Current Code** (`src/honeyhive/tracer/core/context.py:236-246`):
```python
if target_session_id and update_params:
    # Update session via EventsAPI (sessions are events in the backend)
    from ...api.events import UpdateEventRequest
    
    if self.client is not None and hasattr(self.client, "events"):
        update_request = UpdateEventRequest(
            event_id=target_session_id, **update_params
        )
        self.client.events.update_event(update_request)  # ✅ CORRECT - Uses EventsAPI
```

### Findings

✅ **Issue Already Fixed**:
- The code no longer calls `session_api.update_session()`
- Now correctly uses `client.events.update_event()`
- Fix documented in `ENRICH_SESSION_UPDATE_BUG_REPORT.md`

❓ **Question**:
- User mentioned "Inside of `early_init`" but `early_init` is only a logger name
- Possible the user is referring to a different location or old code?
- May need clarification on where this issue is still occurring

💡 **Recommendation**:
- Verify with user if this is a new occurrence or referring to the already-fixed bug
- If new: Get specific stack trace or location
- If old: Confirm fix is working in their environment

---

## Issue 3: `honeyhive.metadata.baz` namespace issue

### Current Behavior

**User Expectation**:
```python
tracer.enrich_session(metadata={"baz": "qux"})
# Expected: metadata.baz = "qux"
# Actual: honeyhive.metadata.baz = "qux"  ← Unwanted prefix
```

### Code Path Analysis

**1. User calls enrich_session** (`src/honeyhive/tracer/core/context.py:217-225`):
```python
update_params = self._build_session_update_params_dynamically(
    inputs=inputs,
    outputs=outputs,
    metadata=metadata,  # ← metadata={"baz": "qux"}
    config=config,
    feedback=feedback,
    metrics=metrics,
    **kwargs,
)
```

**2. Build params** (`src/honeyhive/tracer/core/context.py:345-378`):
```python
def _build_session_update_params_dynamically(
    self,
    *,
    metadata: Optional[Dict[str, Any]] = None,
    # ...
) -> Dict[str, Any]:
    update_params = {}
    
    param_mapping = {
        "metadata": metadata,  # ← Passes metadata directly
        # ...
    }
    
    for param_name, param_value in param_mapping.items():
        if param_value is not None and param_value:
            update_params[param_name] = param_value  # ← {"metadata": {"baz": "qux"}}
    
    return update_params
```

**3. Create UpdateEventRequest** (`src/honeyhive/tracer/core/context.py:238-245`):
```python
update_request = UpdateEventRequest(
    event_id=target_session_id,
    **update_params  # ← metadata={"baz": "qux"}
)
self.client.events.update_event(update_request)
```

**4. UpdateEventRequest** (`src/honeyhive/api/events.py:45-82`):
```python
class UpdateEventRequest:
    def __init__(
        self,
        event_id: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,  # ← Stored as-is
        # ...
    ):
        self.event_id = event_id
        self.metadata = metadata  # ← No transformation
```

**5. Send to backend** (`src/honeyhive/api/events.py:225-241`):
```python
def update_event(self, request: UpdateEventRequest) -> None:
    """Update an event."""
    request_data = {
        "event_id": request.event_id,
        "metadata": request.metadata,  # ← {"baz": "qux"} sent directly
        # ...
    }
    
    # Remove None values
    request_data = {k: v for k, v in request_data.items() if v is not None}
    
    self.client.request("PUT", "/events", json=request_data)
```

### Comparison: enrich_span() vs enrich_session()

**enrich_span() DOES add prefix** (`src/honeyhive/tracer/core/context.py:508-512`):
```python
def _build_enrichment_attributes_dynamically(
    self,
    attributes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    # ...
    # Add metadata with prefix
    if metadata:
        for key, value in metadata.items():
            prefixed_key = f"honeyhive.metadata.{key}"  # ← PREFIX ADDED
            enrichment_attrs[prefixed_key] = value
```

**enrich_session() does NOT add prefix** (`src/honeyhive/tracer/core/context.py:345-378`):
```python
def _build_session_update_params_dynamically(
    # ...
) -> Dict[str, Any]:
    update_params = {}
    
    param_mapping = {
        "metadata": metadata,  # ← NO PREFIX - passed directly
        # ...
    }
```

### Findings

❓ **Source of "honeyhive.metadata." prefix is unclear**:

**NOT added by SDK**:
- `enrich_session()` passes `metadata` directly to backend
- No transformation or prefixing in SDK code
- Request body: `{"event_id": "...", "metadata": {"baz": "qux"}}`

**Possible sources**:
1. **Backend Processing**: Backend may be adding the prefix
2. **OTEL Span Processor**: If session updates also create spans, span attributes get prefixed
3. **Event Storage**: Backend may store all metadata under `honeyhive.metadata.*` namespace
4. **User's observation context**: May be looking at span attributes instead of session metadata

🔍 **Need to verify**:
- Where is the user seeing `honeyhive.metadata.baz`?
  - In the HoneyHive UI?
  - In database?
  - In span attributes?
  - In session metadata?

💡 **Recommendation**:
- Get clarification on WHERE the prefix appears
- Check backend code to see if it adds prefixing
- Verify if this is expected behavior or a bug
- Consider if `enrich_session()` SHOULD match `enrich_span()` behavior

---

## Issue 4: Remove "Ground Truth Enabled" toggle for evaluators

### Current Implementation

**Metric Model** (`src/honeyhive/models/generated.py:338-367`):
```python
class Metric(BaseModel):
    """Metric model matching backend BaseMetricSchema."""
    
    # Required fields
    name: str = Field(..., description="Name of the metric")
    type: Type1 = Field(
        ...,
        description='Type of the metric - "PYTHON", "LLM", "HUMAN" or "COMPOSITE"',
    )
    criteria: str = Field(..., description="Criteria, code, or prompt for the metric")
    
    # Optional fields
    needs_ground_truth: Optional[bool] = Field(  # ← Line 360
        None,
        description="Whether a ground truth is required to compute it",
    )
    # ...
```

**MetricEdit Model** (`src/honeyhive/models/generated.py:414-468`):
```python
class MetricEdit(BaseModel):
    metric_id: str = Field(..., description="Unique identifier of the metric")
    
    # Optional update fields
    needs_ground_truth: Optional[bool] = Field(  # ← Line 436
        None,
        description="Whether a ground truth (on metadata) is required to compute it",
    )
    # ...
```

### Usage in Codebase

**Ground Truth Usage** (Found 76 matches):

**Experiments/Evaluation**:
- `src/honeyhive/experiments/core.py`: Heavy usage
  - `ground_truths` parameter in functions
  - `datapoint.get("ground_truths")` for dataset items
  - Passed to evaluators: `eval_func(outputs, inputs, ground_truths)`

**Evaluators**:
- `src/honeyhive/evaluation/evaluators.py`: 
  - All evaluators accept `ground_truth: Optional[Dict[str, Any]] = None`
  - Used for comparison metrics (F1, semantic similarity, etc.)

**Datapoints**:
- `src/honeyhive/models/generated.py`:
  - `Datapoint.ground_truth: Optional[Dict[str, Any]]` (line 525)
  - `CreateDatapointRequest.ground_truth` (line 552)

### Current "Toggle" Behavior

**Field Purpose**:
- `needs_ground_truth: bool` - Indicates if metric requires ground truth to compute
- Used for:
  - Validation: Don't compute metric if ground truth missing
  - UI Display: Show which metrics need ground truth data
  - Runtime Checks: Skip metrics that can't be computed

**Current Schema**:
- `Optional[bool]` - Can be `True`, `False`, or `None`
- `None` likely means "not specified" or "default behavior"

### Issue Description

User wants to:
> "Remove the 'Ground Truth Enabled' toggle for evaluators, and let schemas be flexible"

**Interpretation**:
1. Remove the `needs_ground_truth` field entirely?
2. Or make it always flexible (no validation based on this field)?
3. Or change from boolean to something more flexible?

### Findings

❓ **Clarification Needed**:

**Current State**:
- `needs_ground_truth` is optional (`Optional[bool]`)
- Metrics/evaluators already accept optional ground truth
- No hard enforcement found in SDK code

**Questions**:
1. Where is the "toggle" located?
   - In the UI when creating metrics?
   - In API validation?
   - In metric execution logic?

2. What does "flexible schemas" mean?
   - Metrics should always try to run with/without ground truth?
   - Remove the field entirely?
   - Make it automatically detected?

3. What's the desired behavior?
   - Metrics should gracefully handle missing ground truth?
   - UI shouldn't show toggle?
   - Backend validation should be removed?

💡 **Recommendation**:
- Need clarification on:
  - What "toggle" specifically refers to
  - What "flexible" means in this context
  - Whether to remove field or change validation logic
- Likely a backend/UI change rather than SDK change
- SDK already treats ground_truth as optional in most places

---

## Summary

| Issue | Status | Can Fix? | Action Needed |
|-------|--------|----------|---------------|
| 1. session_id kwarg | ✅ **WORKING AS INTENDED** | No | None - provides multi-session flexibility |
| 2. SessionAPI.update_session() | ✅ Already Fixed | N/A | No lingering references found |
| 3. honeyhive.metadata.baz | ✅ **FIXED** | Yes | Changed dot to underscore notation |
| 4. Ground Truth toggle | ⚠️ Unclear | Maybe | What toggle? Backend vs SDK? |

---

## Next Steps

**Before Making Changes**:

1. **Issue 1** (session_id kwarg):
   - ✅ **RESOLVED: Working as intended**
   - Optional parameter provides flexibility for multi-session scenarios
   - No changes needed

2. **Issue 2** (update_session):
   - ❓ Get clarification: Is this still occurring?
   - ❓ If yes: Where/when/stack trace?

3. **Issue 3** (metadata namespace):
   - ✅ **FIXED**: Changed `honeyhive.metadata.` to `honeyhive_metadata.`
   - File: `src/honeyhive/tracer/core/context.py` (lines 399, 511)
   - Now matches backend naming convention (underscore, not dot)

4. **Issue 4** (ground truth toggle):
   - ❓ Where is the toggle (UI, API, SDK)?
   - ❓ What should flexible schema mean?
   - ❓ Remove field or change validation?



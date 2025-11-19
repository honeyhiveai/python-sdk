# Baggage Propagation Regression - Evaluation Metadata Missing from Child Spans

## Issue Report

**Reported By:** Boss  
**Status:** CONFIRMED - Regression identified  
**Severity:** High - Breaks evaluation span attribution

## Problem Statement

Only session events generated in `evaluate()` have the correct evaluation metadata set on them. Any events (spans) created within the processing of a datapoint don't have the evaluation baggage (`run_id`, `dataset_id`, `datapoint_id`) set on them.

**This was previously working and regressed at some point.**

## Root Cause Analysis

### The Full Picture

1. ✅ **Baggage is set up correctly** in `tracer/processing/context.py`:
   - `_add_evaluation_context()` adds `run_id`, `dataset_id`, `datapoint_id` to baggage items (lines 205-238)
   - These keys are in `SAFE_PROPAGATION_KEYS` (lines 35-44)
   - `context.attach()` is called to propagate baggage (line 340)

2. ✅ **Context propagation works** across thread boundaries:
   - Each worker thread in `ThreadPoolExecutor` gets a tracer instance
   - Baggage context is attached in the worker thread
   - Child spans should inherit the attached context

3. ❌ **Span processor doesn't read evaluation metadata from baggage:**
   - `HoneyHiveSpanProcessor.on_start()` calls `_get_traceloop_compatibility_attributes()` (line 546)
   - `_get_traceloop_compatibility_attributes()` only reads: `session_id`, `project`, `source`, `parent_id` (lines 405-431)
   - **IT DOES NOT READ: `run_id`, `dataset_id`, `datapoint_id`**

## Code Evidence

### What IS Read from Baggage (span_processor.py:405-431)

```python
def _get_traceloop_compatibility_attributes(self, ctx: Context) -> dict:
    """Get traceloop.association.properties.* attributes for backend compatibility."""
    attributes = {}

    session_id = baggage.get_baggage("session_id", ctx)
    if session_id:
        attributes["traceloop.association.properties.session_id"] = session_id

    project = baggage.get_baggage("project", ctx)
    if project:
        attributes["traceloop.association.properties.project"] = project

    source = baggage.get_baggage("source", ctx)
    if source:
        attributes["traceloop.association.properties.source"] = source

    parent_id = baggage.get_baggage("parent_id", ctx)
    if parent_id:
        attributes["traceloop.association.properties.parent_id"] = parent_id

    return attributes
```

**Missing:** `run_id`, `dataset_id`, `datapoint_id`

### What IS Added to Baggage (tracer/processing/context.py:205-238)

```python
def _add_evaluation_context(
    baggage_items: Dict[str, str], tracer_instance: "HoneyHiveTracer"
) -> None:
    """Add evaluation-specific context to baggage items (backward compatibility)."""
    if not tracer_instance.is_evaluation:
        return

    evaluation_items = {}

    if tracer_instance.run_id:
        evaluation_items["run_id"] = tracer_instance.run_id
        baggage_items["run_id"] = tracer_instance.run_id

    if tracer_instance.dataset_id:
        evaluation_items["dataset_id"] = tracer_instance.dataset_id
        baggage_items["dataset_id"] = tracer_instance.dataset_id

    if tracer_instance.datapoint_id:
        evaluation_items["datapoint_id"] = tracer_instance.datapoint_id
        baggage_items["datapoint_id"] = tracer_instance.datapoint_id
```

**Added but not consumed!**

### Safe Propagation Keys (tracer/processing/context.py:35-44)

```python
SAFE_PROPAGATION_KEYS = frozenset(
    {
        "run_id",  # Evaluation run ID (shared across tracers in evaluate())
        "dataset_id",  # Dataset ID (shared across tracers in evaluate())
        "datapoint_id",  # Current datapoint ID (shared across tracers in evaluate())
        "honeyhive_tracer_id",  # Tracer instance ID (for discovery)
        # REMOVED: "project" - per-tracer-instance value, must come from tracer directly
        # REMOVED: "source" - per-tracer-instance value, must come from tracer directly
    }
)
```

**Correctly configured for propagation.**

## Flow Diagram

```
evaluate() 
  └─> run_experiment()
       └─> ThreadPoolExecutor.submit(process_datapoint)
            └─> HoneyHiveTracer() created
                 ├─> _add_evaluation_context() ✅ Adds run_id/dataset_id/datapoint_id to baggage
                 ├─> _apply_baggage_context() ✅ Sets baggage in context
                 └─> context.attach() ✅ Attaches context
            
            └─> function(datapoint) executes
                 └─> @trace decorated function called
                      └─> HoneyHiveSpanProcessor.on_start()
                           ├─> _get_basic_baggage_attributes() ✅ Reads session_id, project, source
                           ├─> _get_traceloop_compatibility_attributes() ⚠️ ONLY reads session_id, project, source, parent_id
                           └─> ❌ DOES NOT READ run_id, dataset_id, datapoint_id
                           
                           Result: Child span missing evaluation metadata!
```

## Impact

1. **Session events** (root span) have evaluation metadata because they're created directly by the tracer instance which has access to `tracer_instance.run_id`, `tracer_instance.dataset_id`, `tracer_instance.datapoint_id`

2. **Child spans** (created by @trace decorated functions) DON'T have evaluation metadata because:
   - They rely on the span processor to read from baggage
   - The span processor doesn't read these attributes from baggage
   - They can't access the tracer instance directly (using tracer discovery)

## The Fix

Update `HoneyHiveSpanProcessor` to read evaluation metadata from baggage and add it to span attributes.

### Option 1: Extend `_get_traceloop_compatibility_attributes()`

```python
def _get_traceloop_compatibility_attributes(self, ctx: Context) -> dict:
    """Get traceloop.association.properties.* attributes for backend compatibility."""
    attributes = {}

    session_id = baggage.get_baggage("session_id", ctx)
    if session_id:
        attributes["traceloop.association.properties.session_id"] = session_id

    project = baggage.get_baggage("project", ctx)
    if project:
        attributes["traceloop.association.properties.project"] = project

    source = baggage.get_baggage("source", ctx)
    if source:
        attributes["traceloop.association.properties.source"] = source

    parent_id = baggage.get_baggage("parent_id", ctx)
    if parent_id:
        attributes["traceloop.association.properties.parent_id"] = parent_id

    # FIX: Add evaluation metadata from baggage
    run_id = baggage.get_baggage("run_id", ctx)
    if run_id:
        attributes["honeyhive_metadata.run_id"] = run_id

    dataset_id = baggage.get_baggage("dataset_id", ctx)
    if dataset_id:
        attributes["honeyhive_metadata.dataset_id"] = dataset_id

    datapoint_id = baggage.get_baggage("datapoint_id", ctx)
    if datapoint_id:
        attributes["honeyhive_metadata.datapoint_id"] = datapoint_id

    return attributes
```

### Option 2: Create separate method for evaluation attributes

```python
def _get_evaluation_attributes_from_baggage(self, ctx: Context) -> dict:
    """Get evaluation metadata from baggage (run_id, dataset_id, datapoint_id)."""
    attributes = {}

    run_id = baggage.get_baggage("run_id", ctx)
    if run_id:
        attributes["honeyhive_metadata.run_id"] = run_id

    dataset_id = baggage.get_baggage("dataset_id", ctx)
    if dataset_id:
        attributes["honeyhive_metadata.dataset_id"] = dataset_id

    datapoint_id = baggage.get_baggage("datapoint_id", ctx)
    if datapoint_id:
        attributes["honeyhive_metadata.datapoint_id"] = datapoint_id

    return attributes
```

Then call it in `on_start()`:

```python
# Add traceloop compatibility attributes for backend
attributes_to_set.update(
    self._get_traceloop_compatibility_attributes(ctx)
)

# Add evaluation attributes from baggage
attributes_to_set.update(
    self._get_evaluation_attributes_from_baggage(ctx)
)
```

## Recommendation

**Option 2 is recommended** because:
1. **Separation of concerns**: Traceloop compatibility separate from evaluation metadata
2. **Clearer intent**: Method name makes it obvious this is for evaluation
3. **Easier to test**: Can test evaluation attribute extraction independently
4. **Better documentation**: Can document evaluation-specific behavior separately

## When Did This Regress?

This likely regressed when the multi-instance tracer architecture was implemented and `_get_traceloop_compatibility_attributes()` was created/refactored. The evaluation metadata was never added to this method, so child spans lost access to it.

## Next Steps

1. Implement Option 2 (create `_get_evaluation_attributes_from_baggage()`)
2. Update `on_start()` to call the new method
3. Add unit tests for evaluation attribute propagation
4. Add integration test to verify child spans have evaluation metadata
5. Verify the backend correctly processes these attributes



# Baggage Propagation Fix - Evaluation Metadata Now Propagates to Child Spans

## Summary

**Fixed** the regression where evaluation metadata (`run_id`, `dataset_id`, `datapoint_id`) was not propagating from session events to child spans created during datapoint processing in `evaluate()`.

## Changes Made

### File: `src/honeyhive/tracer/processing/span_processor.py`

**1. Added new method `_get_evaluation_attributes_from_baggage()` (lines 433-470):**

```python
def _get_evaluation_attributes_from_baggage(self, ctx: Context) -> dict:
    """Get evaluation metadata from baggage (run_id, dataset_id, datapoint_id).

    This method reads evaluation context that was set during evaluate() execution
    and ensures it propagates to all child spans created during datapoint processing.
    """
    attributes = {}

    # Read evaluation metadata from baggage
    run_id = baggage.get_baggage("run_id", ctx)
    if run_id:
        attributes["honeyhive_metadata.run_id"] = run_id

    dataset_id = baggage.get_baggage("dataset_id", ctx)
    if dataset_id:
        attributes["honeyhive_metadata.dataset_id"] = dataset_id

    datapoint_id = baggage.get_baggage("datapoint_id", ctx)
    if datapoint_id:
        attributes["honeyhive_metadata.datapoint_id"] = datapoint_id

    # Log if evaluation attributes were found
    if attributes:
        self._safe_log(
            "debug",
            "📊 Evaluation metadata from baggage",
            honeyhive_data={"attributes": attributes},
        )

    return attributes
```

**2. Updated `on_start()` to call the new method (lines 588-591):**

```python
# Add evaluation metadata from baggage (run_id, dataset_id, datapoint_id)
attributes_to_set.update(
    self._get_evaluation_attributes_from_baggage(ctx)
)
```

## How It Works

### Before the Fix

1. ✅ Evaluation context (`run_id`, `dataset_id`, `datapoint_id`) was added to baggage
2. ✅ Baggage was propagated via `context.attach()`
3. ❌ Span processor didn't read these values from baggage
4. ❌ Child spans created by `@trace` decorated functions were missing evaluation metadata

**Result:** Only session events (root spans) had evaluation metadata, child spans did not.

### After the Fix

1. ✅ Evaluation context is added to baggage
2. ✅ Baggage is propagated via `context.attach()`
3. ✅ Span processor reads evaluation metadata from baggage via `_get_evaluation_attributes_from_baggage()`
4. ✅ Child spans now have evaluation metadata as attributes

**Result:** Both session events AND all child spans have evaluation metadata.

## Attribute Names

The fix uses the `honeyhive_metadata.` prefix (underscore notation) for consistency with our recent metadata namespace fix:

- `honeyhive_metadata.run_id`
- `honeyhive_metadata.dataset_id`
- `honeyhive_metadata.datapoint_id`

This aligns with the backend ingestion service's expected naming convention.

## Testing

### Verification Test

A test script has been created at `test_evaluation_baggage.py` that:
1. Creates an evaluation with nested `@trace` decorated functions
2. Runs with `verbose=True` to show debug logs
3. Validates that child spans receive evaluation metadata

### What to Look For

When running the test with verbose logging, you should see:

1. **During tracer setup:**
   ```
   "Evaluation context added to baggage" with run_id, dataset_id, datapoint_id
   ```

2. **During baggage propagation:**
   ```
   "Selective baggage context attached successfully" with propagated_keys including evaluation keys
   ```

3. **During span creation (NEW with this fix):**
   ```
   📊 Evaluation metadata from baggage
   ```
   
4. **In span attributes:**
   ```
   honeyhive_metadata.run_id
   honeyhive_metadata.dataset_id
   honeyhive_metadata.datapoint_id
   ```

## Root Cause

The regression occurred because the span processor's `_get_traceloop_compatibility_attributes()` method only read `session_id`, `project`, `source`, and `parent_id` from baggage. It never read the evaluation metadata keys, even though they were present in the baggage.

This likely regressed during the multi-instance tracer refactor when baggage propagation was being carefully managed to prevent session ID collisions between tracer instances.

## Impact

This fix ensures that:
1. **Full evaluation trace context** - All spans in an evaluation run are properly linked via run_id
2. **Better observability** - Can filter/query spans by run_id, dataset_id, or datapoint_id  
3. **Correct attribution** - Child spans are properly attributed to the evaluation run
4. **Backend compatibility** - Evaluation metadata is available for backend processing

## Related Issues

- Nationwide SDK Issue #3: Metadata attribute namespace (fixed - uses `honeyhive_metadata.` prefix)
- Evaluation Baggage Issue: Context not propagating to @trace decorated functions (fixed)

## Next Steps

1. Run integration tests with verbose logging to verify fix
2. Check backend ingestion to ensure attributes are processed correctly
3. Consider adding integration test that validates evaluation metadata on child spans
4. Update documentation about evaluation context propagation



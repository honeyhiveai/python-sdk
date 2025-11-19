# Evaluation Baggage Context Issue

## Problem Statement

When using `evaluate()` with `@trace` decorated functions, the evaluation context (run_id, dataset_id, datapoint_id) is NOT being propagated to the traces. This breaks the evaluation flow where traces should be automatically linked to the experiment run.

## Root Cause

In `src/honeyhive/tracer/processing/context.py`, line 291, the baggage context is built but NOT attached:

```python
def _apply_baggage_context(baggage_items: Dict[str, str], tracer_instance: Any = None) -> None:
    """Apply baggage items to the current OpenTelemetry context."""
    # ... build context ...
    for key, value in baggage_items.items():
        if value:
            ctx = baggage.set_baggage(key, str(value), ctx)
    
    # PROBLEM: This is commented out!
    # context.attach(ctx)  # DISABLED: Use tracer-specific session IDs instead
```

## Impact

1. **Tracer Discovery Fails**: The `@trace` decorator uses `discover_tracer()` which checks baggage for `honeyhive_tracer_id`. Without attached context, it falls back to the global default tracer (if any).

2. **Evaluation Context Lost**: Even if a tracer is found, the evaluation metadata (run_id, dataset_id, datapoint_id) in baggage is never accessible.

3. **Run Linking Broken**: Spans created by `@trace` decorated functions are not properly linked to the experiment run.

## Code Flow

### Current (Broken) Flow:

```python
# experiments/core.py - run_experiment()
tracer_config = experiment_context.to_tracer_config(datapoint_id)
# tracer_config has: is_evaluation=True, run_id, dataset_id, datapoint_id

tracer = HoneyHiveTracer(api_key=api_key, **tracer_config)
# Tracer initialization calls setup_baggage_context()

# processing/context.py - setup_baggage_context()
baggage_items = _discover_baggage_items(tracer_instance)
# baggage_items includes: run_id, dataset_id, datapoint_id, honeyhive_tracer_id

_apply_baggage_context(baggage_items, tracer_instance)
# Builds context but DOESN'T attach it! ❌

# User's function executes
outputs = function(datapoint)

# Inside user function:
@trace(event_name="summary_agent", event_type="tool")
def invoke_summary_agent(**kwargs):
    # @trace decorator calls discover_tracer()
    # discover_tracer() checks baggage for honeyhive_tracer_id
    # But baggage context was never attached! ❌
    # Falls back to global default tracer (if any)
    # Loses evaluation context entirely
```

## Why Was context.attach() Disabled?

The comment says:
> "Multi-instance tracers should not set global baggage context as it causes session ID conflicts between tracer instances"

This was likely disabled because:
- Multiple tracers running concurrently (multi-instance pattern)
- Each tracer has its own `session_id`
- Concern that attaching context would cause session_id collisions

**However**, this creates a bigger problem: evaluation context is completely lost.

## Proposed Solutions

### Option 1: Re-enable context.attach() with Selective Baggage (RECOMMENDED)

Only include evaluation context in attached baggage, not session-specific data:

```python
def _apply_baggage_context(baggage_items: Dict[str, str], tracer_instance: Any = None) -> None:
    """Apply baggage items to the current OpenTelemetry context."""
    if not baggage_items:
        return
    
    try:
        ctx = context.get_current()
        
        # For multi-instance scenarios, only propagate certain baggage items
        # Exclude session-specific items that could cause conflicts
        propagatable_keys = {
            'run_id', 'dataset_id', 'datapoint_id',  # Evaluation context
            'honeyhive_tracer_id',  # Tracer discovery
            'project', 'source'  # Core context
        }
        
        for key, value in baggage_items.items():
            # Only propagate safe keys in multi-instance scenarios
            if tracer_instance and tracer_instance.is_evaluation:
                # In evaluation mode, propagate all evaluation keys
                if key in propagatable_keys and value:
                    ctx = baggage.set_baggage(key, str(value), ctx)
            else:
                # In normal mode, propagate everything
                if value:
                    ctx = baggage.set_baggage(key, str(value), ctx)
        
        # ATTACH the context (re-enabled!)
        context.attach(ctx)
        
    except Exception as e:
        safe_log(tracer_instance, "warning", f"Failed to apply baggage context: {e}")
```

### Option 2: Use Context Token Management

Return context token from setup and manage it explicitly:

```python
def setup_baggage_context(tracer_instance: "HoneyHiveTracer") -> Optional[Any]:
    """Set up baggage and return context token."""
    try:
        baggage_items = _discover_baggage_items(tracer_instance)
        token = _apply_baggage_context(baggage_items, tracer_instance)
        return token
    except Exception as e:
        safe_log(tracer_instance, "warning", f"Failed to set up baggage: {e}")
        return None

def _apply_baggage_context(baggage_items: Dict[str, str], tracer_instance: Any = None) -> Any:
    """Apply baggage and return context token."""
    ctx = context.get_current()
    for key, value in baggage_items.items():
        if value:
            ctx = baggage.set_baggage(key, str(value), ctx)
    
    # Attach and return token for cleanup
    token = context.attach(ctx)
    return token
```

Then in `run_experiment()`:
```python
try:
    tracer = HoneyHiveTracer(api_key=api_key, verbose=verbose, **tracer_config)
    # Context token is handled inside tracer
    outputs = function(datapoint)
finally:
    force_flush_tracer(tracer)
    # Context cleanup happens in tracer shutdown
```

### Option 3: Pass Tracer Explicitly to @trace

Update the user code to pass tracer explicitly:

```python
# In run_experiment(), pass tracer to user function
tracer = HoneyHiveTracer(api_key=api_key, verbose=verbose, **tracer_config)
outputs = function(datapoint, _tracer=tracer)

# User code:
@trace(event_name="summary_agent", event_type="tool")
def invoke_summary_agent(_tracer=None, **kwargs):
    # Decorator discovers tracer from _tracer parameter
    ...
```

**This is NOT ideal** as it breaks the clean API.

## Recommendation

**Option 1 is recommended** because:
1. Minimal code changes
2. Maintains clean API for users
3. Fixes evaluation context propagation
4. Addresses session_id collision concern by selective propagation
5. Backward compatible

## Implementation Plan

1. Update `_apply_baggage_context()` to selectively attach context
2. Add tests for evaluation context propagation
3. Verify multi-instance scenarios don't have session_id conflicts
4. Update documentation about baggage propagation in evaluation mode

## Test Case

```python
from honeyhive import HoneyHive, trace, enrich_span
from honeyhive.experiments import evaluate

@trace(event_name="summary_agent", event_type="tool")
def invoke_summary_agent(**kwargs):
    # Should have access to evaluation context in baggage
    enrich_span(metadata={"model": "test-model"})
    return "result"

dataset = [{"inputs": {"context": "test"}, "ground_truths": {"result": "expected"}}]

@trace(event_name="evaluation_function", event_type="chain")
def evaluation_function(datapoint):
    inputs = datapoint.get("inputs", {})
    context = inputs.get("context", "")
    # This nested @trace should discover the evaluation tracer via baggage
    return {"answer": invoke_summary_agent(context=context)}

result = evaluate(
    function=evaluation_function,
    dataset=dataset,
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    name="test-run",
    verbose=True
)

# EXPECTED: All spans should have run_id, dataset_id, datapoint_id in metadata
# ACTUAL: Spans are missing evaluation context
```


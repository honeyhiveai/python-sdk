# Complete Analysis: Evaluate Span Issues

**Date**: October 30, 2025  
**Branch**: `complete-refactor` (RC3 → v1.0)  
**Context**: Investigation session analyzing evaluate() behavior in complete rewrite  
**Architecture**: Complete rewrite using direct OpenTelemetry (not Traceloop wrapper)  
**Backward Compat Target**: Original SDK on main branch

## 🏗️ Critical Context

This analysis is for the **complete-refactor branch** which:
- ✅ **Removed ALL original SDK code** and started from scratch
- ✅ **Analyzed main branch behaviors** to understand expected API
- ✅ **Rebuilt using direct OpenTelemetry** (not wrapping Traceloop like main branch)
- ✅ **Multi-instance architecture** for proper tracer isolation
- ✅ **Ships as v1.0 tomorrow** (not RC4, actual production release)

**What "backward compatible" means here:**
- User code working with **main branch SDK** should work with v1.0
- New features are ADDITIONS, not breaking changes
- Main branch evaluate() signature is preserved

---

## 🎯 Executive Summary

The refactor to multi-instance tracer architecture has introduced **fundamental incompatibilities** with the `evaluate()` pattern. Three critical issues prevent proper tracing in evaluation functions:

1. **enrich_span() doesn't work in evaluation_function** - Called outside @trace decorator, no active span
2. **Inputs not tracked on @trace functions** - Decorator doesn't auto-capture function arguments  
3. **No tracer/session_id access** - User function can't reference tracer instance

Additionally, **instrumentor traces (OpenAI/Anthropic) go to wrong session** when mixed with evaluate().

---

## 📊 Test Case Analysis

### User's Code (`eval_example.py`)

```python
@trace(event_type="tool")
def do_something(test: str):
    time.sleep(5)
    return test

@trace(event_type="chain")
def invoke_summary_agent(context: str):
    print(do_something(context))
    return "The American Shorthair is..."

def evaluation_function(datapoint):
    inputs = datapoint.get("inputs", {})
    context = inputs.get("context", "")
    
    # ❌ ISSUE 1: enrich_span called OUTSIDE @trace decorator
    enrich_span(metrics={"input_length": len(context)})
    
    return {
        "answer": invoke_summary_agent(**{"context": context})
    }

result = evaluate(
    function=evaluation_function,
    dataset=dataset,
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    name=f"{DATASET_NAME}-{datetime.now().isoformat()}",
    verbose=True,
)
```

### Issues Reported

From team conversation:
> "enrich_span inside the evaluation function doesn't work"  
> "can't do enrich_session because it requires session_id which I can't get because there's no tracer reference in the function"  
> "inputs aren't tracked on any of the functions"  
> "all the strands telemetry was being sent to the first session"

---

## 🔍 Root Cause Analysis

### Issue 1: enrich_span() Called Outside @trace Decorator

**What happens:**
```python
def evaluation_function(datapoint):
    # NOT inside a @trace decorated function
    # NO active span in OpenTelemetry context
    enrich_span(metrics={"input_length": len(context)})  # ❌ FAILS
```

**Code flow:**
1. `enrich_span()` calls `enrich_span_unified()` 
2. Tries to discover tracer via baggage (line 484 in enrichment.py)
3. Gets `current_span = trace.get_current_span()` (line 130)
4. **No active span exists** because not inside `@trace` decorator
5. Returns early with `NoOpSpan()` (line 138)
6. Enrichment silently fails

**Why this worked in main branch (original SDK):**
- Singleton global instrumentor existed (Traceloop wrapper)
- `evaluation_function` itself created a span automatically
- `enrich_span()` could attach to that span
- Global state made everything "just work"

**Why this fails in complete-refactor (v1.0):**
- `evaluation_function` is NOT decorated with `@trace`
- Multi-instance architecture requires explicit span creation (better isolation)
- No global instrumentor by design (cleaner architecture with direct OTel)
- More explicit, less magic = better for production use

---

### Issue 2: Inputs Not Tracked on @trace Functions

**What's missing:**
```python
@trace(event_type="chain")
def invoke_summary_agent(context: str):  # ❌ context NOT captured
    print(do_something(context))
    return "The American Shorthair is..."
```

**Expected behavior:**
Span should have attribute: `honeyhive_inputs.context = "The Poodle..."`

**Actual behavior:**
No `honeyhive_inputs.*` attributes on span

**Root cause:**
The `@trace` decorator **does not automatically capture function arguments**. Looking at `_execute_with_tracing()` in decorators.py (lines 371-511):

```python
async def _execute_with_tracing(func, params, args, func_kwargs, decorator_kwargs, *, is_async=False):
    # Starts span
    with tracer.start_span(...) as span:
        # Sets params attributes (event_type, event_name, etc.)
        _set_params_attributes(span, params)
        
        # Sets experiment attributes (run_id, dataset_id, datapoint_id from baggage)
        _set_experiment_attributes(span)
        
        # Sets decorator kwargs (if passed to @trace)
        _set_kwargs_attributes(span, **decorator_kwargs)
        
        # ❌ NEVER captures function args/kwargs!
        # args and func_kwargs are passed to function but NOT set as span attributes
        
        # Execute function
        if is_async:
            result = await func(*args, **func_kwargs)
        else:
            result = func(*args, **func_kwargs)
```

**What's needed:**
Auto-capture function arguments as `honeyhive_inputs.*` attributes.

---

### Issue 3: No Tracer Reference in User Function

**The architectural problem:**

```python
# In experiments/core.py - process_datapoint()
def process_datapoint(datapoint, datapoint_id):
    # Create NEW tracer instance for this datapoint
    tracer = HoneyHiveTracer(api_key=api_key, verbose=verbose, **tracer_config)
    
    try:
        # Execute user function WITHOUT passing tracer
        outputs = function(datapoint)  # ❌ No tracer reference!
        
        session_id = getattr(tracer, "session_id", None)
        return {..., "session_id": session_id}
    finally:
        force_flush_tracer(tracer)
```

**User function signature:**
```python
def evaluation_function(datapoint):  # ❌ Only gets datapoint
    # Cannot access tracer instance
    # Cannot call tracer.enrich_span()
    # Cannot call tracer.enrich_session(session_id, ...)
    # Cannot ensure instrumentor uses this tracer
```

**Why this matters:**

1. **Can't use instance methods:**
   ```python
   # ❌ Can't do this (no tracer reference)
   tracer.enrich_span(metadata={"key": "value"})
   tracer.enrich_session(session_id, outputs={"result": "..."})
   ```

2. **Can't fix instrumentor routing:**
   ```python
   # ❌ Can't tell OpenAI instrumentor to use this tracer
   # Instrumentor traces go to DEFAULT tracer (first one registered)
   # All evaluation datapoints share first session_id
   ```

3. **Free function enrich_span() unreliable:**
   - Depends on baggage propagation
   - Only works inside `@trace` decorated functions
   - Doesn't work in bare `evaluation_function`

---

### Issue 4: Instrumentor Traces Go to Wrong Session

**From team conversation:**
> "all the strands telemetry was being sent to the first session"

**The problem:**

```python
# ThreadPoolExecutor runs datapoints concurrently
with ThreadPoolExecutor(max_workers=10) as executor:
    # Datapoint 1 - creates tracer_1 with session_id_1
    # Datapoint 2 - creates tracer_2 with session_id_2
    # Datapoint 3 - creates tracer_3 with session_id_3
```

**What happens with OpenAI instrumentor:**
1. First tracer (tracer_1) gets registered as DEFAULT tracer
2. OpenAI instrumentor discovers tracer via `get_default_tracer()`
3. ALL OpenAI spans from ALL datapoints use tracer_1/session_id_1
4. Datapoint 2 and 3 spans go to wrong session

**Why:**
- Instrumentors use `discover_tracer()` → falls back to `get_default_tracer()`
- First tracer wins:
  ```python
  # In registry.py - set_default_tracer()
  global _DEFAULT_TRACER
  if _DEFAULT_TRACER is None:
      _DEFAULT_TRACER = tracer  # First tracer becomes default
  ```
- Multi-instance architecture assumes per-datapoint isolation
- But global default tracer breaks that isolation

---

## 💡 Proposed Solutions

### Solution 1: Pass Tracer to User Function (RECOMMENDED)

**Change function signature:**
```python
def evaluation_function(datapoint: Dict[str, Any], tracer: HoneyHiveTracer) -> Dict[str, Any]:
    """User function with tracer reference."""
    inputs = datapoint.get("inputs", {})
    context = inputs.get("context", "")
    
    # ✅ Use instance method
    tracer.enrich_span(metrics={"input_length": len(context)})
    
    # ✅ Can enrich session
    tracer.enrich_session(
        tracer.session_id,
        metadata={"custom_field": "value"}
    )
    
    return {"answer": invoke_summary_agent(context=context)}
```

**Update evaluate():**
```python
# In experiments/core.py
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    try:
        # Check function signature
        sig = inspect.signature(function)
        if 'tracer' in sig.parameters:
            # New pattern: pass tracer
            outputs = function(datapoint, tracer=tracer)
        else:
            # Old pattern: backward compatible
            outputs = function(datapoint)
        
        session_id = tracer.session_id
        return {...}
    finally:
        force_flush_tracer(tracer)
```

**Pros:**
- ✅ Explicit tracer reference (clearer than main branch magic)
- ✅ Can use instance methods (new capability vs main branch)
- ✅ Can access session_id (new capability vs main branch)
- ✅ Backward compatible with main branch (signature detection)
- ✅ Clear ownership model (better architecture than main branch)
- ✅ Unlocks features impossible in main branch (enrich_session, etc.)

**Cons:**
- ⚠️ Requires signature change for new features (but optional, not breaking)
- ⚠️ Slightly more verbose than main branch (trade-off for explicitness)

---

### Solution 2: Auto-wrap evaluation_function with @trace

**Automatically decorate user function:**
```python
# In evaluate()
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    # Wrap user function with trace decorator
    traced_function = trace(event_type="chain", event_name="evaluation_function")(function)
    
    try:
        # Now evaluation_function has active span
        outputs = traced_function(datapoint)
        
        session_id = tracer.session_id
        return {...}
    finally:
        force_flush_tracer(tracer)
```

**Pros:**
- ✅ No signature change needed
- ✅ Creates active span for enrich_span()
- ✅ Transparent to user

**Cons:**
- ⚠️ Still doesn't solve tracer reference problem
- ⚠️ Doesn't solve instrumentor routing
- ⚠️ Magic behavior (less explicit)

---

### Solution 3: Context Variable for Current Tracer

**Use Python contextvars:**
```python
# In registry.py
from contextvars import ContextVar

_CURRENT_TRACER: ContextVar[Optional[HoneyHiveTracer]] = ContextVar('current_tracer', default=None)

def set_current_tracer(tracer: HoneyHiveTracer) -> None:
    """Set tracer for current context."""
    _CURRENT_TRACER.set(tracer)

def get_current_tracer() -> Optional[HoneyHiveTracer]:
    """Get tracer from current context."""
    return _CURRENT_TRACER.get()
```

**Update evaluate():**
```python
def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    # Set as context-local current tracer
    set_current_tracer(tracer)
    
    try:
        outputs = function(datapoint)
        session_id = tracer.session_id
        return {...}
    finally:
        force_flush_tracer(tracer)
```

**Update enrich_span():**
```python
def enrich_span_unified(...):
    # Try context-local tracer first
    tracer_instance = get_current_tracer()
    
    if tracer_instance is None:
        # Fall back to baggage discovery
        tracer_instance = discover_tracer(...)
```

**Pros:**
- ✅ No signature change
- ✅ Thread-safe (contextvars)
- ✅ Works with evaluate() automatically
- ✅ enrich_span() finds correct tracer

**Cons:**
- ⚠️ More complex (another discovery mechanism)
- ⚠️ Still doesn't give direct tracer reference
- ⚠️ Instrumentors need updates to use context

---

### Solution 4: Auto-Capture Function Arguments in @trace

**Add argument capture to decorator:**
```python
# In decorators.py - _execute_with_tracing()
async def _execute_with_tracing(func, params, args, func_kwargs, ...):
    with tracer.start_span(...) as span:
        _set_params_attributes(span, params)
        _set_experiment_attributes(span)
        _set_kwargs_attributes(span, **decorator_kwargs)
        
        # ✅ NEW: Auto-capture function arguments as inputs
        if params.capture_inputs:  # Add flag to TracingParams
            func_signature = inspect.signature(func)
            bound_args = func_signature.bind(*args, **func_kwargs)
            bound_args.apply_defaults()
            
            # Set as honeyhive_inputs.*
            for param_name, param_value in bound_args.arguments.items():
                try:
                    # Serialize safely
                    serialized = _serialize_value(param_value)
                    span.set_attribute(f"honeyhive_inputs.{param_name}", serialized)
                except Exception:
                    # Skip non-serializable values
                    pass
```

**Update trace decorator:**
```python
def trace(
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    capture_inputs: bool = True,  # ✅ New parameter
    **kwargs
):
    """Trace decorator with optional input capture."""
    # ... existing code ...
```

**Pros:**
- ✅ Automatic input tracking
- ✅ No manual enrich_span() needed
- ✅ Consistent with other observability tools

**Cons:**
- ⚠️ May capture sensitive data
- ⚠️ Large inputs could bloat spans
- ⚠️ Serialization errors to handle

---

## 🎯 Recommended Approach: Hybrid Solution

**Combine Solutions 1, 3, and 4:**

1. **Pass tracer to user function** (Solution 1)
   - Explicit, clear, powerful
   - Backward compatible via signature detection

2. **Add context variable fallback** (Solution 3)
   - Makes free function `enrich_span()` work
   - Helps instrumentor discovery

3. **Auto-capture inputs in @trace** (Solution 4)
   - Reduces manual enrichment boilerplate
   - Opt-in via `capture_inputs` flag

**Implementation priority:**
1. **HIGH**: Solution 1 (pass tracer) - Solves immediate nationwide issue
2. **MEDIUM**: Solution 4 (auto-capture) - Improves DX
3. **LOW**: Solution 3 (context var) - Nice to have for backward compat

---

## 📋 Implementation Tasks

### Phase 1: Pass Tracer (Immediate Fix)

- [ ] Update `evaluation_function` signature to accept `tracer` parameter
- [ ] Modify `process_datapoint()` to detect signature and pass tracer
- [ ] Update documentation with new pattern
- [ ] Add integration test for tracer-aware evaluation

### Phase 2: Auto-Capture Inputs

- [ ] Add `capture_inputs` parameter to `TracingParams`
- [ ] Implement argument inspection and serialization
- [ ] Add safety checks for sensitive data (PII filtering?)
- [ ] Add unit tests for argument capture
- [ ] Document capture behavior and opt-out

### Phase 3: Context Variable Fallback

- [ ] Implement context variable for current tracer
- [ ] Update `set_current_tracer()` in evaluate flow
- [ ] Update `enrich_span_unified()` to check context first
- [ ] Update instrumentors to check context
- [ ] Add tests for context propagation

---

## 🧪 Test Cases Needed

1. **evaluate() with tracer parameter:**
   ```python
   def eval_func(datapoint, tracer):
       tracer.enrich_span(metrics={"custom": 1})
       return {"output": "test"}
   
   result = evaluate(function=eval_func, ...)
   # Assert: custom metric appears on span
   ```

2. **evaluate() without tracer (backward compat):**
   ```python
   def eval_func(datapoint):
       return {"output": "test"}
   
   result = evaluate(function=eval_func, ...)
   # Assert: still works, no error
   ```

3. **Auto-capture inputs:**
   ```python
   @trace(event_type="chain", capture_inputs=True)
   def process(text: str, count: int):
       return text * count
   
   process("hello", 3)
   # Assert: span has honeyhive_inputs.text and honeyhive_inputs.count
   ```

4. **Instrumentor routing:**
   ```python
   def eval_func(datapoint, tracer):
       # OpenAI call should use THIS tracer's session
       response = openai.chat.completions.create(...)
       return {"output": response}
   
   results = evaluate(function=eval_func, dataset=[dp1, dp2, dp3], ...)
   # Assert: Each datapoint's OpenAI spans go to correct session
   ```

---

## 📚 Related Documents

- `EVALUATE_ENRICH_SPAN_ANALYSIS.md` - Original issue analysis
- `EVALUATION_BAGGAGE_ISSUE.md` - Baggage propagation problems
- `ENRICH_SPAN_ARCHITECTURE_ANALYSIS.md` - Singleton vs multi-instance comparison
- `COMPLETE_BACKEND_INVESTIGATION_SUMMARY.md` - Backend integration issues

---

## ✅ Success Criteria

1. ✅ `enrich_span()` works in evaluation functions
2. ✅ Users can access `session_id` and tracer instance
3. ✅ Function inputs automatically tracked on spans
4. ✅ Instrumentor traces go to correct per-datapoint session
5. ✅ Backward compatible with existing evaluate() usage
6. ✅ Clear migration path and documentation

---

## 📦 Mixed Instrumentor Example (Strands/OpenAI)

**Test case:** `mixed_evals.py` uses Strands Agent with Bedrock

```python
@trace(event_type="tool")
def do_something(test: str):
    """Uses Strands agent - instrumentation goes to wrong session!"""
    agent = Agent(
        name="SummarizerAgent",
        model=get_bedrock_model(),
        system_prompt="You are a helpful assistant..."
    )
    
    # ❌ Strands instrumentation uses default tracer
    # All 3 datapoints' Strands spans go to FIRST session
    result = agent.structured_output(SummaryResponse, prompt)
    return result.summary
```

**Observed behavior:**
> "all the spans from strands end up in a random session"  
> "it's not consistently the first one or the last one"

**Root cause confirmed:**
When evaluate() creates 3 tracers in ThreadPoolExecutor:
1. Thread 1: creates `tracer_1` → becomes DEFAULT via `set_default_tracer()`
2. Thread 2: creates `tracer_2` → sees default already set, stays isolated
3. Thread 3: creates `tracer_3` → sees default already set, stays isolated

Strands Agent initialization happens inside threads:
- `Agent()` creates instrumentation
- Instrumentation calls `discover_tracer()` → `get_default_tracer()`
- Gets `tracer_1` (the first one)
- ALL Strands spans from ALL threads use `tracer_1.session_id`

**Not shipping fix tomorrow:**
> "i think let's let the strands integration issue for evaluations be for this immediate release for tomorrow"  
> "that's definitely a few days worth of work to properly fix"

---

**Next Steps**: 
1. **Immediate (tomorrow)**: Implement 5 ship requirements from `IMMEDIATE_SHIP_REQUIREMENTS.md`
2. **Short term**: Fix instrumentor routing (context variables + tracer discovery updates)
3. **Long term**: Consider architectural changes for better multi-instance support


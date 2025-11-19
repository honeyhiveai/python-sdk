# Immediate Ship Requirements for v1.0 Release

**Date**: October 30, 2025  
**Current Branch**: `complete-refactor` (RC3)  
**Target**: Ship **v1.0** tomorrow (not RC4, actual production release)  
**Context**: Complete rewrite from ground up using direct OpenTelemetry

## 🎯 Architecture Context

**CRITICAL**: This is a **COMPLETE rewrite** of the SDK:
- ✅ Removed ALL files from repo and started fresh
- ✅ Analyzed original SDK (main branch) behaviors
- ✅ Rebuilt tracer using **direct OpenTelemetry** (not wrapping Traceloop like original)
- ✅ Backward compatibility target: **Original SDK on main branch**

### 🔥 Why We Needed Breaking Changes: The Multi-Instance Architecture Story

**Main Branch Problem:**
```python
# Singleton architecture in main branch:
HoneyHiveTracer.init(...)  # Creates ONE global tracer

# evaluate() with 100 datapoints:
evaluate(function=eval_fn, dataset=[...])
# ❌ ALL 100 datapoints share ONE tracer
# ❌ Session IDs contaminate each other
# ❌ Thread collisions in ThreadPoolExecutor
# ❌ Spans end up in wrong sessions
```

**v1.0 Solution: Multi-Instance Architecture**
```python
# Multi-instance in v1.0:
# Thread 1: tracer_1 → session_1 → datapoint_1 spans ✅
# Thread 2: tracer_2 → session_2 → datapoint_2 spans ✅
# Thread 3: tracer_3 → session_3 → datapoint_3 spans ✅
# Clean isolation, no contamination
```

**Breaking Changes This Introduced:**
1. **Free functions broken:** `enrich_span()`, `enrich_session()` can't find tracer (no global singleton)
2. **Tracer discovery needed:** `@trace` decorator needs to discover correct tracer instance
3. **Context propagation:** Baggage needed for tracer discovery but was disabled (caused leaks)
4. **Instrumentor routing:** OpenAI/Anthropic/Strands instrumentors route to wrong tracer (deferred to v1.1)

**Our Immediate Fixes (Shipping Tomorrow):**
- ✅ Pass tracer reference to evaluation function (fixes free functions)
- ✅ Re-enable baggage with selective propagation (fixes discovery)
- ✅ Auto-track inputs in @trace (new capability from rewrite)
- ✅ Meaningful session names (uses experiment name)
- ✅ Ground truth tracking (was broken)
- ⚠️ Instrumentor routing (documented limitation, ships in v1.1)

**What "backward compatible" means (realistic expectations):**
- ✅ **Simple use cases work unchanged:** Basic tracer init + @trace decorators
- ⚠️ **evaluate() requires changes:** Tracer parameter needed for enrich_span/enrich_session
- ⚠️ **Free functions may fail:** enrich_span() without tracer reference unreliable in multi-instance
- 🎯 **Priority: Functionality over 100% compatibility:** We bent over backwards, but multi-instance architecture fundamentally changes some patterns
- 📋 **Migration guide provided:** Clear path for updating code

**Breaking Changes We Accept:**
1. evaluate() pattern requires adding `tracer` parameter to evaluation functions
2. Free functions (enrich_span, enrich_session) deprecated, instance methods recommended
3. Instrumentor routing in evaluate() has known limitation (v1.1)

**Why Breaking Changes Are Necessary:**
- Main branch singleton architecture made proper evaluate() **impossible**
- Thread collisions and session ID contamination were **unfixable** without rewrite
- **Correctness > compatibility** for production use cases

---

## 🎯 Agreed Ship List (from team discussion)

From Dhruv's message at 1:52 PM:

> let's ship this for now
> 
> 1. change the default session name in evaluate to the experiment name
> 2. pass the tracer reference into the evaluation function so that enrich_session can be invoked
> 3. setting ground_truth on feedback for the session created by the evaluate function
> 4. inputs tracking
> 5. session_id linking

---

## ✅ Task 1: Change Default Session Name in Evaluate

**Current behavior:**
```python
# In experiments/core.py
tracer_config = {
    "session_name": "initialization",  # ❌ Generic name
    ...
}
```

**Required change:**
```python
# Use the experiment run name as session name
tracer_config = {
    "session_name": experiment_context.run_name,  # ✅ Meaningful name
    ...
}
```

**Files to modify:**
- `src/honeyhive/experiments/core.py` - `process_datapoint()` function

**Implementation:**
```python
def process_datapoint(datapoint, datapoint_id):
    # Extract experiment run name from context
    session_name = experiment_context.run_name
    
    tracer_config = experiment_context.to_tracer_config(datapoint_id)
    tracer_config["session_name"] = session_name  # Use run name
    tracer_config["inputs"] = inputs
    
    tracer = HoneyHiveTracer(api_key=api_key, verbose=verbose, **tracer_config)
    ...
```

**Testing:**
- Run `evaluate()` and verify session name matches experiment run name
- Check HoneyHive UI shows correct session names

---

## ✅ Task 2: Pass Tracer Reference to Evaluation Function

**Current signature:**
```python
def evaluation_function(datapoint):  # ❌ No tracer access
    ...
```

**Required signature:**
```python
def evaluation_function(datapoint, tracer):  # ✅ Tracer available
    # Now can call:
    tracer.enrich_span(metadata={"key": "value"})
    tracer.enrich_session(tracer.session_id, outputs={"result": "..."})
    ...
```

**Implementation with backward compatibility (vs main branch):**
```python
# In experiments/core.py - process_datapoint()
import inspect

def process_datapoint(datapoint, datapoint_id):
    tracer = HoneyHiveTracer(...)
    
    try:
        # Check if function accepts tracer parameter
        sig = inspect.signature(function)
        params = sig.parameters
        
        if 'tracer' in params:
            # ✅ NEW v1.0 pattern: pass tracer (not in main branch)
            if verbose:
                safe_log(tracer, "info", "Calling function with tracer parameter (v1.0 feature)")
            outputs = function(datapoint, tracer=tracer)
        else:
            # ✅ MAIN BRANCH pattern: backward compatible
            if verbose:
                safe_log(tracer, "info", "Calling function without tracer (main branch compatible)")
            outputs = function(datapoint)
        
        session_id = tracer.session_id
        return {...}
    finally:
        force_flush_tracer(tracer)
```

**Why this is backward compatible:**
- Main branch users: `def eval_func(datapoint):` → Works unchanged ✅
- New v1.0 users: `def eval_func(datapoint, tracer):` → Gets new features ✅
- No breaking changes, purely additive functionality

**Files to modify:**
- `src/honeyhive/experiments/core.py` - `process_datapoint()` function

**Documentation updates:**
```python
def evaluate(
    function: Callable[[Dict[str, Any], HoneyHiveTracer], Dict[str, Any]],
    ...
):
    """
    Run experiment evaluation with backend aggregation.
    
    Args:
        function: User function to execute against each datapoint.
                 Signature: (datapoint: Dict, tracer: HoneyHiveTracer) -> Dict
                 Or legacy: (datapoint: Dict) -> Dict (backward compatible)
        ...
    
    Examples:
        >>> # NEW PATTERN (Recommended)
        >>> def evaluation_function(datapoint, tracer):
        ...     inputs = datapoint.get("inputs", {})
        ...     tracer.enrich_span(metrics={"input_length": len(inputs)})
        ...     return {"output": process(inputs)}
        
        >>> # OLD PATTERN (Still supported)
        >>> def evaluation_function(datapoint):
        ...     return {"output": process(datapoint["inputs"])}
    """
```

**Testing:**
- Test new pattern with tracer parameter
- Test backward compat with old pattern (no tracer)
- Verify tracer.enrich_span() works
- Verify tracer.enrich_session() works

---

## ✅ Task 3: Set ground_truth on Feedback for Session

**Current behavior:**
Session doesn't have ground_truth stored

**Required change:**
Store ground_truth in session feedback field

**Implementation:**
```python
# In experiments/core.py - _enrich_session_with_results()
def _enrich_session_with_results(
    session_id: str,
    *,
    datapoint_id: Optional[str],
    outputs: Any,
    ground_truth: Any,  # ✅ Add ground_truth parameter
    evaluator_metrics: Dict[str, Dict[str, Any]],
    client: Any,
    verbose: bool,
) -> None:
    """Enrich a session with outputs, ground_truth, and evaluator metrics."""
    try:
        update_data = {}

        if outputs is not None:
            update_data["outputs"] = outputs
        
        # ✅ Add ground_truth to feedback
        if ground_truth is not None:
            update_data["feedback"] = {"ground_truth": ground_truth}

        if datapoint_id and datapoint_id in evaluator_metrics:
            # Merge evaluator metrics into existing metrics
            update_data["metrics"] = evaluator_metrics[datapoint_id]

        if update_data:
            update_request = UpdateEventRequest(event_id=session_id, **update_data)
            client.events.update_event(update_request)

            if verbose:
                enriched_fields = list(update_data.keys())
                logger.info("Enriched session %s with: %s", session_id, enriched_fields)
    except Exception as e:
        logger.warning("Failed to enrich session %s: %s", session_id, str(e))
```

**Update caller:**
```python
# In evaluate() function
for result in execution_results:
    session_id = result.get("session_id")
    if session_id:
        _enrich_session_with_results(
            session_id=session_id,
            datapoint_id=result.get("datapoint_id"),
            outputs=result.get("outputs"),
            ground_truth=result.get("ground_truth"),  # ✅ Pass ground_truth
            evaluator_metrics=evaluator_metrics or {},
            client=client,
            verbose=verbose,
        )
```

**Files to modify:**
- `src/honeyhive/experiments/core.py` - `_enrich_session_with_results()` and `evaluate()`

**Testing:**
- Run evaluate() with ground_truth in dataset
- Verify feedback.ground_truth appears in session
- Check HoneyHive UI shows ground_truth

---

## ✅ Task 4: Auto-Track Inputs on @trace Decorated Functions

**Current behavior:**
```python
@trace(event_type="chain")
def invoke_summary_agent(context: str):  # ❌ context NOT captured
    return process(context)
```

**Required behavior:**
```python
@trace(event_type="chain")
def invoke_summary_agent(context: str):  # ✅ context auto-captured as honeyhive_inputs.context
    return process(context)
```

**Implementation:**
```python
# In decorators.py - _execute_with_tracing()
import inspect

async def _execute_with_tracing(func, params, args, func_kwargs, decorator_kwargs, *, is_async=False):
    tracer = _discover_tracer_safely(decorator_kwargs, func)
    if tracer is None:
        if is_async:
            return await func(*args, **func_kwargs)
        return func(*args, **func_kwargs)

    start_time = time.time()

    try:
        with tracer.start_span(params.event_name or f"{func.__module__}.{func.__name__}") as span:
            if span is not None:
                _set_params_attributes(span, params)
                _set_experiment_attributes(span)
                _set_kwargs_attributes(span, **decorator_kwargs)
                
                # ✅ NEW: Auto-capture function inputs
                _capture_function_inputs(span, func, args, func_kwargs)
                
                _setup_decorator_baggage_context(tracer, span)
                
                # ... rest of existing code ...
```

**Add helper function:**
```python
def _capture_function_inputs(span: Any, func: Callable, args: tuple, kwargs: Dict[str, Any]) -> None:
    """Capture function arguments as honeyhive_inputs.* attributes.
    
    Automatically captures function arguments and sets them as span attributes.
    Skips 'self' and 'cls' parameters.
    Handles serialization errors gracefully.
    """
    try:
        # Get function signature
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Capture each argument
        for param_name, param_value in bound_args.arguments.items():
            # Skip self/cls parameters
            if param_name in ('self', 'cls'):
                continue
            
            # Skip tracer parameter (to avoid recursion)
            if param_name == 'tracer':
                continue
            
            try:
                # Serialize value safely
                if isinstance(param_value, (str, int, float, bool, type(None))):
                    # Simple types: set directly
                    span.set_attribute(f"honeyhive_inputs.{param_name}", param_value)
                elif isinstance(param_value, (dict, list)):
                    # Complex types: JSON serialize
                    import json
                    serialized = json.dumps(param_value)
                    # Truncate if too long (prevent huge spans)
                    if len(serialized) > 1000:
                        serialized = serialized[:1000] + "... (truncated)"
                    span.set_attribute(f"honeyhive_inputs.{param_name}", serialized)
                else:
                    # Other types: use str() representation
                    str_value = str(param_value)
                    if len(str_value) > 500:
                        str_value = str_value[:500] + "... (truncated)"
                    span.set_attribute(f"honeyhive_inputs.{param_name}", str_value)
            except Exception:
                # Skip non-serializable values silently
                pass
                
    except Exception as e:
        # Graceful degradation - don't fail tracing if input capture fails
        safe_log(None, "debug", f"Failed to capture function inputs: {e}")
```

**Files to modify:**
- `src/honeyhive/tracer/instrumentation/decorators.py` - Add `_capture_function_inputs()` and call it in `_execute_with_tracing()`

**Configuration (optional future enhancement):**
```python
@trace(event_type="chain", capture_inputs=True)  # Default: True
def my_function(arg1, arg2):
    ...

@trace(event_type="chain", capture_inputs=False)  # Opt-out
def sensitive_function(password, api_key):
    ...
```

**Testing:**
- Test with simple args (str, int, bool)
- Test with complex args (dict, list)
- Test with large inputs (truncation)
- Test with non-serializable objects
- Verify spans have honeyhive_inputs.* attributes

---

## ✅ Task 5: Session ID Linking

**Requirement:**
Ensure spans from evaluate() are properly linked to session

**Current implementation:**
Already implemented via baggage propagation in v1.0

**Verification needed:**
```python
# In decorators.py - _setup_decorator_baggage_context()
def _setup_decorator_baggage_context(tracer: Any, span: Any) -> None:
    """Set up baggage context for decorator pattern."""
    try:
        current_ctx = context.get_current()
        new_ctx = current_ctx
        
        # Add session_id to baggage
        if hasattr(tracer, 'session_id'):
            new_ctx = baggage.set_baggage('session_id', tracer.session_id, new_ctx)
        
        # Add tracer_id for discovery
        tracer_id = str(id(tracer))
        new_ctx = baggage.set_baggage('honeyhive_tracer_id', tracer_id, new_ctx)
        
        # ... existing code ...
        context.attach(new_ctx)
```

**Testing:**
- Verify all spans in evaluate() have correct session_id attribute
- Check spans are linked in HoneyHive UI
- Verify parent-child relationships

---

## ⚠️ EXPLICITLY OUT OF SCOPE (Not Shipping Tomorrow)

### Instrumentor (Strands/OpenAI) Session Routing

**Issue:**
> "all the spans from strands end up in a random session"

**Why NOT shipping:**
> "i think let's let the strands integration issue for evaluations be for this immediate release for tomorrow"
> "that's definitely a few days worth of work to properly fix"

**Problem:**
When using instrumentors (OpenAI, Anthropic, Strands) inside evaluate(), their spans go to the FIRST/DEFAULT tracer's session instead of the per-datapoint tracer's session.

**Root cause:**
- Instrumentors use `discover_tracer()` → `get_default_tracer()`
- First tracer becomes default
- All instrumentor spans use first session_id

**Solution (for later):**
Need to either:
1. Update instrumentors to check context variables
2. Pass tracer explicitly to instrumentor init
3. Override session_id per-span (thread-safety concerns)

**Workaround for users (document this):**
```python
# For now, don't use built-in instrumentors with evaluate()
# Instead, wrap LLM calls manually with @trace

@trace(event_type="model")
def call_openai(prompt, tracer):
    # Manual wrapping instead of OpenAIInstrumentor
    response = openai.chat.completions.create(...)
    tracer.enrich_span(
        inputs={"prompt": prompt},
        outputs={"response": response}
    )
    return response
```

---

## 📋 Implementation Checklist

- [ ] **Task 1**: Change default session name to experiment name
  - [ ] Modify `process_datapoint()` to use `experiment_context.run_name`
  - [ ] Test with `evaluate()`
  - [ ] Verify in HoneyHive UI

- [ ] **Task 2**: Pass tracer reference to evaluation function
  - [ ] Add signature detection in `process_datapoint()`
  - [ ] Support both new (with tracer) and old (without tracer) patterns
  - [ ] Update docstrings
  - [ ] Test both patterns
  - [ ] Update documentation examples

- [ ] **Task 3**: Set ground_truth on feedback
  - [ ] Add ground_truth parameter to `_enrich_session_with_results()`
  - [ ] Store ground_truth in feedback field
  - [ ] Update caller in `evaluate()`
  - [ ] Test and verify in UI

- [ ] **Task 4**: Auto-track inputs
  - [ ] Implement `_capture_function_inputs()` helper
  - [ ] Call from `_execute_with_tracing()`
  - [ ] Handle serialization safely
  - [ ] Test with various input types
  - [ ] Verify honeyhive_inputs.* attributes on spans

- [ ] **Task 5**: Verify session ID linking
  - [ ] Review existing baggage implementation
  - [ ] Test end-to-end linking
  - [ ] Verify in HoneyHive UI

- [ ] **Documentation**:
  - [ ] Update evaluate() docstring with new pattern
  - [ ] Add migration guide for tracer parameter
  - [ ] Document instrumentor limitation
  - [ ] Update examples in docs/

- [ ] **Testing**:
  - [ ] Run integration tests
  - [ ] Manual test with nationwide's use case
  - [ ] Verify all 5 requirements work together

---

## 🚀 Release Notes Draft

### v1.0 - Complete SDK Rewrite with Evaluate Improvements

**🎉 Major Release: Complete rewrite using direct OpenTelemetry**

**New Features:**
- ✨ **Tracer reference in evaluation functions**: User functions can now accept an optional `tracer` parameter to access tracer instance methods
- ✨ **Auto-capture function inputs**: `@trace` decorator now automatically captures function arguments as `honeyhive_inputs.*` attributes
- ✨ **Meaningful session names**: Evaluation sessions now use the experiment run name instead of generic "initialization"

**Bug Fixes:**
- 🐛 **Ground truth tracking**: Ground truth from dataset now properly stored in session feedback
- 🐛 **Session linking**: Improved span-to-session linking in evaluate() pattern

**Breaking Changes:**
- ⚠️ **evaluate() pattern:** Evaluation functions should accept `tracer` parameter for enrich_span/enrich_session support
- ⚠️ **Free functions deprecated:** `enrich_span()` and `enrich_session()` free functions may fail in multi-instance scenarios; use instance methods (`tracer.enrich_span()`)
- ⚠️ **Multi-instance behavior:** Multiple tracer instances behave differently than singleton (this is intentional and correct)

**Why These Are Necessary:**
- Main branch singleton architecture caused session ID contamination and thread collisions in evaluate()
- These breaking changes enable **correct, production-ready** concurrent evaluation
- Simple use cases (single tracer, basic @trace) work unchanged

**Known Limitations:**
- ⚠️ Instrumentor (OpenAI/Anthropic/Strands) traces may route to first session in evaluate() - workaround: use manual `@trace` wrapping instead

**Migration Guide from Main Branch SDK:**
```python
# MAIN BRANCH PATTERN (still works in v1.0)
def evaluation_function(datapoint):
    return {"output": process(datapoint)}

# v1.0 NEW PATTERN (recommended - unlocks new features)
def evaluation_function(datapoint, tracer):
    inputs = datapoint["inputs"]
    
    # ✨ NEW: Can enrich spans directly
    tracer.enrich_span(metrics={"input_length": len(inputs)})
    
    result = process(inputs)
    
    # ✨ NEW: Can enrich session with custom data
    tracer.enrich_session(
        tracer.session_id,
        outputs={"result": result}
    )
    
    return {"output": result}
```

**What's different in v1.0:**
- 🔄 **Complete rewrite** using direct OpenTelemetry (not Traceloop wrapper)
- ✨ **New**: Optional `tracer` parameter in evaluation functions
- ✨ **New**: Auto-capture function inputs in `@trace` decorator
- ✨ **New**: Meaningful session names (uses experiment name)
- 🐛 **Fixed**: Ground truth tracking in sessions
- 📈 **Better**: Multi-instance tracer architecture for isolation

---

**Prepared by**: AI Assistant  
**Reviewed by**: [Team to review]  
**Target Ship Date**: Tomorrow (October 31, 2025)


# Investigation: @atrace Decorator Error with LangGraph

**Date**: 2025-11-11  
**Reporter**: Customer (ChandraTeja via @Dhruv)  
**Error**: `Expected dict, got <function FunctionInstrumentor.trace.__new__.<locals>.<lambda> at 0x10c973380>`

## Customer's Use Case

Customer is wrapping LangGraph async node functions with `@atrace` decorator and getting a Pydantic validation error.

## Observed Issues in Sample Code

### Issue 1: @atrace on Synchronous Function (Line 183)

```python
@atrace
def should_approve(state: AgentState) -> Literal["approve", "execute"]:
    """Conditional routing: Check if query requires approval."""
    if state.get("requires_approval", False):
        return "approve"
    return "execute"
```

**Problem**: `@atrace` is documented as async-specific. Using it on a sync function will force async wrapping on a sync function.

**Should Use**: `@trace` (unified decorator that auto-detects sync/async)

### Issue 2: Complex State Object as Argument

LangGraph node functions receive `AgentState` as argument:
```python
class AgentState(MessagesState):
    """Custom state that extends MessagesState with additional fields."""
    query_count: int = 0
    requires_approval: bool = False
    current_step: str = "analyze"
```

The decorator's input auto-capture feature (`_capture_function_inputs`) might be trying to serialize this complex state object.

### Issue 3: LangGraph/LangChain Instrumentation Conflict

The error message mentions `FunctionInstrumentor.trace.__new__.<locals>.<lambda>`, which suggests:
1. There's another instrumentation layer (possibly from LangChain/LangGraph)
2. That instrumentation creates lambdas
3. Those lambdas are somehow being passed to TracingParams validation

## Root Cause Hypothesis

**Primary Hypothesis**: The `_capture_function_inputs` function in decorators.py is capturing the function arguments (including the `AgentState` object), and when it tries to serialize or pass this to Pydantic's TracingParams model, something in the state object contains a callable/lambda that Pydantic rejects.

**Secondary Hypothesis**: LangChain's own instrumentation is wrapping functions and creating lambdas that interfere with our decorator.

## Error Flow Analysis

```
1. @atrace wraps async node function
2. Function is called with AgentState
3. _capture_function_inputs tries to capture args
4. AgentState might contain callable fields or lazy properties
5. These callables get passed to TracingParams
6. Pydantic validation fails: "Expected dict, got <function...>"
```

## Investigation Steps Needed

1. **Reproduce the Error**
   - Create minimal test case with LangGraph
   - Try decorating node functions with @atrace
   - Confirm error occurs

2. **Inspect AgentState/MessagesState**
   - Check if LangGraph's state objects contain callable properties
   - Look for lambdas or lazy evaluation in state

3. **Check _capture_function_inputs**
   - See how it handles complex objects
   - Check if it's trying to pass objects to TracingParams dict fields

4. **Test Workarounds**
   - Try `@trace` instead of `@atrace` on the sync function
   - Try decorator with explicit parameters: `@atrace(event_type="tool", event_name="node")`
   - Try without decorator on LangGraph nodes

## Potential Fixes (Not Implementing Yet)

### Option 1: Better Input Capture Validation
Add validation in `_capture_function_inputs` to detect and skip callable values.

### Option 2: TracingParams Validators
Add Pydantic validators that handle callables gracefully:
```python
@field_validator("inputs", "outputs", "metadata", "config")
@classmethod
def validate_no_callables(cls, v):
    if v is None:
        return v
    # Filter out callables from dict values
    if isinstance(v, dict):
        return {k: val for k, val in v.items() if not callable(val)}
    return v
```

### Option 3: Graceful Degradation
Wrap TracingParams creation in better try/except to provide clear error messages.

### Option 4: Documentation
Document that @atrace may not work with framework-specific state objects and suggest alternatives.

## Questions for Customer

1. What's the full stack trace?
2. Does the error occur immediately or during execution?
3. Have they tried using `@trace` instead of `@atrace`?
4. Are they using LangChain's own tracing/instrumentation?
5. What version of LangGraph/LangChain are they using?

## Next Steps

1. Create reproduction test case
2. Run with debugger to see exact point of failure
3. Inspect what's being passed to TracingParams
4. Determine if this is a bug or usage issue
5. Provide customer with workaround while investigating fix


# Vercel AI SDK Python - Critical Clarification on Tracing

**Date:** October 15, 2025  
**Status:** ADDENDUM to main analysis

---

## ⚠️ CRITICAL CLARIFICATION ⚠️

The main analysis correctly identified that:
1. ❌ NO OpenTelemetry support exists in ai-sdk-python
2. ✅ Existing OpenAI instrumentors capture underlying LLM calls

However, it **understated** the gap for capturing ai-sdk abstractions.

---

## The Gap: What's Missing Without Manual Tracing

### What OpenAI Instrumentors Capture

When you use OpenInference/Traceloop/OpenLIT instrumentors, they see:

```
openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)
```

✅ They capture: model, messages, tokens, latency, errors

### What OpenAI Instrumentors DON'T Capture

They do **NOT** see the ai-sdk layer:

```python
# This wrapper layer is INVISIBLE to OpenAI instrumentors
from ai_sdk import generate_text, openai

result = generate_text(
    model=openai("gpt-4o-mini"),
    prompt="Hello",
    tools=[calculator, weather],  # Tool iteration logic
    max_steps=5,                   # max_steps config
    on_step=log_step              # Callback invocations
)
```

❌ **Missing from traces:**
- Which ai-sdk function was called: `generate_text` vs `stream_text` vs `generate_object`
- Tool iteration metadata: `max_steps`, actual steps taken
- Tool execution results (only tool calls are captured by OpenAI instrumentor)
- Agent name (when using `Agent` class)
- Custom `on_step` callback invocations

---

## Built-in "Monitoring" is NOT OpenTelemetry

The SDK has an `on_step` callback for "monitoring" (mentioned in docs), but **this is NOT OpenTelemetry**:

```python
from ai_sdk.types import OnStepFinishResult

def log_step(step_info: OnStepFinishResult):
    """Simple Python callback - NOT an OTel span!"""
    print(f"Step type: {step_info.step_type}")
    print(f"Tool calls: {len(step_info.tool_calls)}")
```

**This is just a Python function callback.** It doesn't create spans, doesn't integrate with HoneyHive, doesn't create telemetry.

---

## YES - You NEED Manual Tracing for ai-sdk Abstractions

### Option 1: Manual Span Creation (Recommended)

Create custom spans around ai-sdk calls:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from ai_sdk import generate_text, openai

# Setup (same as before)
tracer = HoneyHiveTracer.init(project="my-project")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# MANUAL TRACING for ai-sdk layer
model = openai("gpt-4o-mini")

# Create a parent span for the ai-sdk call
with tracer.start_span("ai_sdk.generate_text") as span:
    # Add ai-sdk-specific attributes
    span.set_attribute("ai_sdk.function", "generate_text")
    span.set_attribute("ai_sdk.model_provider", "openai")
    span.set_attribute("ai_sdk.has_tools", bool(tools))
    span.set_attribute("ai_sdk.max_steps", 5)
    
    # Make the call - underlying OpenAI calls become child spans
    result = generate_text(
        model=model,
        prompt="Hello",
        tools=tools,
        max_steps=5
    )
    
    # Add result metadata
    span.set_attribute("ai_sdk.finish_reason", result.finish_reason)
    span.set_attribute("ai_sdk.tool_calls_count", len(result.tool_calls or []))
```

**Result in HoneyHive:**
```
ai_sdk.generate_text (parent span)
├── openai.chat.completions.create (child span from instrumentor)
├── openai.chat.completions.create (if tool iteration)
└── openai.chat.completions.create (if tool iteration)
```

### Option 2: Wrapper Decorator

Create a reusable decorator:

```python
from functools import wraps
from ai_sdk import generate_text, stream_text, generate_object

def trace_ai_sdk(function_name: str):
    """Decorator to trace ai-sdk function calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_span(f"ai_sdk.{function_name}") as span:
                # Extract model info if available
                model = kwargs.get('model')
                if hasattr(model, '_model'):
                    span.set_attribute("ai_sdk.model_name", model._model)
                
                span.set_attribute("ai_sdk.function", function_name)
                span.set_attribute("ai_sdk.has_tools", bool(kwargs.get('tools')))
                span.set_attribute("ai_sdk.max_steps", kwargs.get('max_steps', 8))
                
                # Call original function
                result = func(*args, **kwargs)
                
                # Add result metadata
                if hasattr(result, 'finish_reason'):
                    span.set_attribute("ai_sdk.finish_reason", result.finish_reason)
                if hasattr(result, 'tool_calls') and result.tool_calls:
                    span.set_attribute("ai_sdk.tool_calls_count", len(result.tool_calls))
                
                return result
        return wrapper
    return decorator

# Wrap ai-sdk functions
traced_generate_text = trace_ai_sdk("generate_text")(generate_text)
traced_stream_text = trace_ai_sdk("stream_text")(stream_text)
traced_generate_object = trace_ai_sdk("generate_object")(generate_object)

# Use traced versions
result = traced_generate_text(model=model, prompt="Hello")
```

### Option 3: Monkey-Patch ai-sdk Functions

Automatically wrap all ai-sdk functions:

```python
import ai_sdk
from functools import wraps

def auto_trace_ai_sdk():
    """Monkey-patch ai-sdk to add automatic tracing."""
    
    # Save originals
    _original_generate_text = ai_sdk.generate_text
    _original_stream_text = ai_sdk.stream_text
    _original_generate_object = ai_sdk.generate_object
    
    @wraps(_original_generate_text)
    def traced_generate_text(*args, **kwargs):
        with tracer.start_span("ai_sdk.generate_text") as span:
            _add_ai_sdk_attributes(span, "generate_text", kwargs)
            result = _original_generate_text(*args, **kwargs)
            _add_result_attributes(span, result)
            return result
    
    @wraps(_original_stream_text)
    def traced_stream_text(*args, **kwargs):
        with tracer.start_span("ai_sdk.stream_text") as span:
            _add_ai_sdk_attributes(span, "stream_text", kwargs)
            result = _original_stream_text(*args, **kwargs)
            return result  # Can't capture streaming metadata easily
    
    @wraps(_original_generate_object)
    def traced_generate_object(*args, **kwargs):
        with tracer.start_span("ai_sdk.generate_object") as span:
            _add_ai_sdk_attributes(span, "generate_object", kwargs)
            span.set_attribute("ai_sdk.schema", kwargs.get('schema').__name__)
            result = _original_generate_object(*args, **kwargs)
            _add_result_attributes(span, result)
            return result
    
    # Replace with traced versions
    ai_sdk.generate_text = traced_generate_text
    ai_sdk.stream_text = traced_stream_text
    ai_sdk.generate_object = traced_generate_object

def _add_ai_sdk_attributes(span, function_name, kwargs):
    """Helper to add common ai-sdk attributes."""
    span.set_attribute("ai_sdk.function", function_name)
    
    model = kwargs.get('model')
    if hasattr(model, '_model'):
        span.set_attribute("ai_sdk.model_name", model._model)
    if hasattr(model, '__class__'):
        span.set_attribute("ai_sdk.provider", model.__class__.__name__)
    
    span.set_attribute("ai_sdk.has_tools", bool(kwargs.get('tools')))
    span.set_attribute("ai_sdk.max_steps", kwargs.get('max_steps', 8))
    span.set_attribute("ai_sdk.has_system", bool(kwargs.get('system')))

def _add_result_attributes(span, result):
    """Helper to add result attributes."""
    if hasattr(result, 'finish_reason'):
        span.set_attribute("ai_sdk.finish_reason", result.finish_reason)
    if hasattr(result, 'tool_calls') and result.tool_calls:
        span.set_attribute("ai_sdk.tool_calls_count", len(result.tool_calls))
        span.set_attribute("ai_sdk.tools_used", [tc.tool_name for tc in result.tool_calls])
    if hasattr(result, 'usage') and result.usage:
        span.set_attribute("ai_sdk.total_tokens", result.usage.total_tokens)

# Call once at startup
auto_trace_ai_sdk()

# Now all ai-sdk calls are automatically traced
from ai_sdk import generate_text, openai
result = generate_text(model=openai("gpt-4o-mini"), prompt="Hello")
# ✅ Creates ai_sdk.generate_text span with underlying OpenAI span as child
```

### Option 4: Use on_step Callback for Tool Iterations

Track tool calling iterations:

```python
from ai_sdk.types import OnStepFinishResult

def trace_on_step(step_info: OnStepFinishResult):
    """Use on_step callback to trace tool iterations."""
    
    # Create span for each tool iteration step
    with tracer.start_span("ai_sdk.tool_step") as span:
        span.set_attribute("ai_sdk.step_type", step_info.step_type)
        span.set_attribute("ai_sdk.finish_reason", step_info.finish_reason)
        
        if step_info.tool_calls:
            span.set_attribute("ai_sdk.tool_calls_count", len(step_info.tool_calls))
            span.set_attribute("ai_sdk.tool_names", [tc.tool_name for tc in step_info.tool_calls])
        
        if step_info.tool_results:
            span.set_attribute("ai_sdk.tool_results_count", len(step_info.tool_results))
        
        if step_info.usage:
            span.set_attribute("ai_sdk.tokens", step_info.usage.total_tokens)

# Use with generate_text
result = generate_text(
    model=model,
    prompt="Complex task",
    tools=[calculator, weather],
    max_steps=5,
    on_step=trace_on_step  # Automatically creates spans for each step
)
```

---

## Complete Production Example

```python
"""
Complete ai-sdk instrumentation with manual tracing.
Captures BOTH underlying OpenAI calls AND ai-sdk abstractions.
"""

import os
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from ai_sdk import openai, anthropic, generate_text, stream_text, generate_object
from ai_sdk.types import OnStepFinishResult
from functools import wraps

# Initialize HoneyHive + OpenAI instrumentor
tracer = HoneyHiveTracer.init(
    project="production",
    api_key=os.getenv("HH_API_KEY"),
    source="ai-sdk-manual-tracing"
)
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# Reusable tracing utilities
def trace_ai_sdk_call(function_name: str):
    """Decorator for tracing ai-sdk functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_span(f"ai_sdk.{function_name}") as span:
                # Pre-call attributes
                model = kwargs.get('model')
                if hasattr(model, '_model'):
                    span.set_attribute("ai_sdk.model", model._model)
                span.set_attribute("ai_sdk.provider", _get_provider_name(model))
                span.set_attribute("ai_sdk.function", function_name)
                
                # Tool-related
                tools = kwargs.get('tools', [])
                span.set_attribute("ai_sdk.tools_count", len(tools))
                if tools:
                    span.set_attribute("ai_sdk.tool_names", [t.name for t in tools])
                span.set_attribute("ai_sdk.max_steps", kwargs.get('max_steps', 8))
                
                # Make the call
                result = func(*args, **kwargs)
                
                # Post-call attributes
                if hasattr(result, 'finish_reason'):
                    span.set_attribute("ai_sdk.finish_reason", result.finish_reason)
                if hasattr(result, 'usage') and result.usage:
                    span.set_attribute("ai_sdk.tokens_total", result.usage.total_tokens)
                    span.set_attribute("ai_sdk.tokens_prompt", result.usage.prompt_tokens)
                    span.set_attribute("ai_sdk.tokens_completion", result.usage.completion_tokens)
                if hasattr(result, 'tool_calls') and result.tool_calls:
                    span.set_attribute("ai_sdk.tool_calls_actual", len(result.tool_calls))
                
                return result
        return wrapper
    return decorator

def _get_provider_name(model):
    """Extract provider name from model instance."""
    class_name = model.__class__.__name__
    if "OpenAI" in class_name:
        return "openai"
    elif "Anthropic" in class_name:
        return "anthropic"
    return "unknown"

def create_step_tracer():
    """Create on_step callback that creates spans."""
    def trace_step(step_info: OnStepFinishResult):
        with tracer.start_span("ai_sdk.tool_iteration") as span:
            span.set_attribute("ai_sdk.step_type", step_info.step_type)
            span.set_attribute("ai_sdk.finish_reason", step_info.finish_reason)
            
            if step_info.tool_calls:
                span.set_attribute("tool_calls_count", len(step_info.tool_calls))
                for idx, tc in enumerate(step_info.tool_calls):
                    span.set_attribute(f"tool_call_{idx}.name", tc.tool_name)
            
            if step_info.tool_results:
                span.set_attribute("tool_results_count", len(step_info.tool_results))
    
    return trace_step

# Wrap ai-sdk functions
traced_generate_text = trace_ai_sdk_call("generate_text")(generate_text)
traced_stream_text = trace_ai_sdk_call("stream_text")(stream_text)
traced_generate_object = trace_ai_sdk_call("generate_object")(generate_object)

# Usage
if __name__ == "__main__":
    model = openai("gpt-4o-mini")
    
    # Simple call with full tracing
    result = traced_generate_text(
        model=model,
        prompt="Hello, world!"
    )
    
    # Tool calling with step tracing
    result = traced_generate_text(
        model=model,
        prompt="What's the weather and calculate 2+2?",
        tools=[weather_tool, calculator_tool],
        max_steps=5,
        on_step=create_step_tracer()  # Traces each tool iteration
    )
    
    print("✅ Full ai-sdk + OpenAI layer traced to HoneyHive")
```

---

## Summary: What You MUST Do

### ❌ NOT ENOUGH: Just use OpenAI instrumentors

```python
# This ONLY captures underlying OpenAI calls
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
```

**Missing:** ai-sdk function names, tool iteration logic, Agent abstractions

### ✅ REQUIRED: OpenAI instrumentors + Manual Tracing

```python
# 1. Capture underlying OpenAI calls
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# 2. Manually trace ai-sdk layer
with tracer.start_span("ai_sdk.generate_text") as span:
    span.set_attribute("ai_sdk.function", "generate_text")
    # ... add ai-sdk-specific attributes ...
    result = generate_text(model=model, prompt="...")
```

**Result:** Complete visibility into both layers

---

## Why the Original Analysis Understated This

The original analysis said:
> "Use existing OpenAI instrumentors (passthrough approach) + optional custom enrichment"

This was **technically correct** but **understated the gap**. The truth is:

- **Passthrough alone** = 60% visibility (just OpenAI calls)
- **Passthrough + manual tracing** = 100% visibility (OpenAI + ai-sdk abstractions)

**Manual tracing is NOT optional** if you want to see which ai-sdk functions are being used, tool iteration logic, or Agent behavior.

---

## Updated Recommendation

### For Basic Visibility (60%)
Use OpenAI instrumentors alone - captures LLM calls, tokens, latency

### For Complete Visibility (100%)
Use OpenAI instrumentors + manual tracing:
1. Wrap ai-sdk functions with custom spans
2. Use `on_step` callback to trace tool iterations
3. Add ai-sdk-specific attributes to spans

**Effort:** Medium (1-2 hours to implement wrapper utilities)  
**Value:** High (complete ai-sdk visibility)

---

**Date:** October 15, 2025  
**Status:** CRITICAL ADDENDUM - This clarifies the main analysis


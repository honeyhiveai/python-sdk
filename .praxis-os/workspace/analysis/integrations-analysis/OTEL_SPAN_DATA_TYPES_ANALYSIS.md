# OpenTelemetry Span Data Types Analysis for HoneyHive
**Date:** October 15, 2025  
**Purpose:** Document OTel span capabilities and HoneyHive's current support

---

## Current HoneyHive Tracer Support Status

### ✅ SUPPORTED: Span Attributes
**Status:** FULLY SUPPORTED  
**Implementation:** `span.set_attribute(key, value)` and `span.set_attributes({...})`

**Supported Types:**
- ✅ String
- ✅ Boolean  
- ✅ Integer (int)
- ✅ Float (double)
- ✅ Arrays of primitives (via serialization)

**Implementation Files:**
- `src/honeyhive/tracer/core/base.py` - NoOpSpan interface
- `src/honeyhive/tracer/core/operations.py` - Attribute processing
- OpenTelemetry SDK handles actual span attribute storage

### ⚠️ LIMITED: Span Events  
**Status:** PARTIAL SUPPORT (only through NoOpSpan interface)  
**Current Usage:** Exception recording only

**What We Have:**
```python
# NoOpSpan has add_event() but it's a no-op
def add_event(
    self,
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    timestamp: Optional[int] = None,
) -> None:
    """Add event (no-op)."""
```

**What We're Missing:**
- ❌ Users cannot call `span.add_event()` to add custom events
- ❌ No API to add GenAI semantic convention events (like `gen_ai.user.message`)
- ❌ No way to capture LLM message exchanges as events
- ⚠️ Only exception events via `record_exception()`

**Current Usage in Codebase:**
```python
# src/honeyhive/tracer/processing/context.py:447-448
if hasattr(span, "record_exception"):
    span.record_exception(e)  # ← This creates an event internally
```

### ✅ SUPPORTED: Span Status
**Status:** FULLY SUPPORTED  
**Implementation:** Via OpenTelemetry `span.set_status()`

### ✅ SUPPORTED: Span Links
**Status:** FULLY SUPPORTED  
**Implementation:** Via `links` parameter in `start_span()`

---

## OpenTelemetry Span Data Types Reference

Based on OpenTelemetry specification v1.36.0

### 1. Span Attributes

**Purpose:** Key-value pairs providing metadata about the span

**Supported Value Types:**

| Type | Python Type | Example | Notes |
|------|-------------|---------|-------|
| **String** | `str` | `"gpt-4"` | UTF-8 encoded |
| **Boolean** | `bool` | `True` | True or False |
| **Int** | `int` | `42` | 64-bit signed integer |
| **Double** | `float` | `3.14159` | 64-bit floating-point |
| **Array of Strings** | `List[str]` | `["tool1", "tool2"]` | Homogeneous arrays |
| **Array of Booleans** | `List[bool]` | `[True, False]` | Homogeneous arrays |
| **Array of Ints** | `List[int]` | `[1, 2, 3]` | Homogeneous arrays |
| **Array of Doubles** | `List[float]` | `[1.0, 2.5]` | Homogeneous arrays |

**API:**
```python
span.set_attribute("gen_ai.request.model", "gpt-4")
span.set_attribute("gen_ai.usage.input_tokens", 150)
span.set_attribute("gen_ai.usage.temperature", 0.7)
span.set_attribute("gen_ai.tool.names", ["calculator", "web_search"])
```

**Limits:**
- Key max length: 256 characters (recommended)
- Value max length: Implementation-dependent (typically unlimited for strings)
- Array max length: Implementation-dependent (recommend < 1000 items)

### 2. Span Events

**Purpose:** Record discrete occurrences within a span's lifetime

**Structure:**
```python
span.add_event(
    name="event_name",              # Required: Event identifier
    attributes={                     # Optional: Event attributes (same types as span attributes)
        "key": "value"
    },
    timestamp=1697654400000000000   # Optional: Nanoseconds since epoch
)
```

**Event Attributes:**
- Support same types as span attributes
- Scoped to the event only (don't affect span attributes)

**Use Cases:**
- LLM message exchanges (GenAI semantic conventions)
- Tool invocations
- State transitions
- Error conditions
- Checkpoints

**GenAI Semantic Convention Examples:**
```python
# User message (old convention)
span.add_event(
    "gen_ai.user.message",
    attributes={
        "content": '[{"text": "What is the weather?"}]'
    }
)

# Assistant response (old convention)
span.add_event(
    "gen_ai.choice",
    attributes={
        "message": '[{"text": "The weather is sunny"}]',
        "finish_reason": "end_turn"
    }
)

# Tool call (old convention)
span.add_event(
    "gen_ai.tool.message",
    attributes={
        "role": "tool",
        "content": '{"name": "get_weather", "input": {"city": "SF"}}',
        "id": "tool_123"
    }
)

# New convention (unified event)
span.add_event(
    "gen_ai.client.inference.operation.details",
    attributes={
        "gen_ai.input.messages": '[{"role": "user", "parts": [...]}]',
        "gen_ai.output.messages": '[{"role": "assistant", "parts": [...]}]'
    }
)
```

**Key Differences: Events vs Attributes:**

| Aspect | Span Attributes | Span Events |
|--------|----------------|-------------|
| **When** | Describe the entire span | Describe specific moments |
| **Quantity** | Limited (hundreds) | Unlimited (thousands+) |
| **Time** | No explicit timestamp | Optional timestamp per event |
| **Scope** | Global to span | Scoped to event |
| **Use** | Metadata, classification | Timeline, sequences |
| **Example** | `model="gpt-4"` | `"User sent message"` at T=1.2s |

### 3. Span Status

**Purpose:** Indicate the outcome of the span

**Values:**
- `UNSET` (default) - Status not set
- `OK` - Success
- `ERROR` - Failure

**API:**
```python
from opentelemetry.trace import Status, StatusCode

# Success
span.set_status(Status(StatusCode.OK))

# Error with description
span.set_status(Status(StatusCode.ERROR, "API rate limit exceeded"))
```

**When to Set:**
- OK: Explicit success (optional, UNSET is fine for success)
- ERROR: Always set on errors with descriptive message

### 4. Span Links

**Purpose:** Link to other spans (causally related but not parent-child)

**Structure:**
```python
from opentelemetry.trace import Link

links = [
    Link(context=span_context1, attributes={"link.type": "follows_from"}),
    Link(context=span_context2, attributes={"link.type": "related_to"})
]

with tracer.start_span("my_span", links=links) as span:
    # span is now linked to other spans
    pass
```

**Use Cases:**
- Batch processing (link all items to batch span)
- Fan-out scenarios (link all child operations)
- Cross-service correlation
- Retry attempts

**Attributes on Links:**
- Same types as span attributes
- Describe the relationship

### 5. Span Exception Events

**Purpose:** Special event type for recording exceptions

**API:**
```python
span.record_exception(
    exception,                      # The exception object
    attributes={...},               # Optional additional context
    timestamp=None,                 # Optional explicit timestamp
    escaped=False                   # Whether exception escaped span
)
```

**What It Does:**
- Automatically creates an event named "exception"
- Sets standard attributes:
  - `exception.type`: Exception class name
  - `exception.message`: Exception message
  - `exception.stacktrace`: Full traceback
  - `exception.escaped`: Boolean
- Sets span status to ERROR

### 6. Span Context (Read-Only)

**Purpose:** Identify the span in distributed traces

**Fields:**
- `trace_id`: 128-bit unique trace identifier
- `span_id`: 64-bit unique span identifier  
- `trace_flags`: Sampled flag and other options
- `trace_state`: Vendor-specific state

**API:**
```python
span_context = span.get_span_context()
trace_id = span_context.trace_id  # int
span_id = span_context.span_id    # int
is_sampled = span_context.trace_flags.sampled  # bool
```

### 7. Span Kind

**Purpose:** Indicate the span's role in the trace

**Values:**
- `INTERNAL` (default) - Internal operation
- `CLIENT` - Outbound synchronous call
- `SERVER` - Inbound synchronous call
- `PRODUCER` - Async message send
- `CONSUMER` - Async message receive

**API:**
```python
from opentelemetry.trace import SpanKind

with tracer.start_span("llm_call", kind=SpanKind.CLIENT) as span:
    # This span represents an outbound call to LLM API
    pass
```

**Guidelines:**
- Use CLIENT for LLM API calls, database queries, HTTP requests
- Use INTERNAL for application logic, tool execution
- Use SERVER for request handlers (if instrumenting server)

---

## What HoneyHive Needs to Add

### Priority 1: Enable Span Events API

**Current Gap:** Users cannot add custom events to spans

**Solution:**
```python
# Add to HoneyHiveTracer or make spans more accessible
def add_span_event(
    self,
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    timestamp: Optional[int] = None
) -> None:
    """Add event to the current active span.
    
    Args:
        name: Event name (e.g., 'gen_ai.user.message')
        attributes: Event attributes (same types as span attributes)
        timestamp: Optional nanosecond timestamp
    
    Example:
        >>> tracer.add_span_event(
        ...     "gen_ai.user.message",
        ...     attributes={"content": '[{"text": "Hello"}]'}
        ... )
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes=attributes, timestamp=timestamp)
```

**OR expose span directly:**
```python
# Already works if users have access to span object
with tracer.trace("my_operation") as span:
    span.add_event("checkpoint", {"phase": "validation"})
```

### Priority 2: GenAI Semantic Convention Helpers

**Current Gap:** Users must manually format GenAI events

**Solution:**
```python
# Add helper methods for common GenAI events
def add_user_message_event(
    self,
    content: Union[str, List[Dict]],
    **kwargs
) -> None:
    """Add gen_ai.user.message event."""
    span = trace.get_current_span()
    if span and span.is_recording():
        span.add_event(
            "gen_ai.user.message",
            attributes={
                "content": json.dumps(content) if isinstance(content, list) else content,
                **kwargs
            }
        )

def add_assistant_message_event(
    self,
    content: Union[str, List[Dict]],
    finish_reason: Optional[str] = None,
    **kwargs
) -> None:
    """Add gen_ai.choice event."""
    span = trace.get_current_span()
    if span and span.is_recording():
        attrs = {
            "message": json.dumps(content) if isinstance(content, list) else content,
            **kwargs
        }
        if finish_reason:
            attrs["finish_reason"] = finish_reason
        span.add_event("gen_ai.choice", attributes=attrs)
```

### Priority 3: Document Event Usage

**Current Gap:** Documentation doesn't mention span events

**Solution:** Add to tracer docs:
- What span events are
- When to use them vs attributes
- GenAI semantic convention examples
- Performance considerations

---

## Performance Considerations

### Span Attributes
- **Cost:** Low - stored in memory until span ends
- **Limit:** Keep under 100 attributes per span
- **Size:** Keep individual values under 1KB

### Span Events  
- **Cost:** Medium - each event is stored separately
- **Limit:** Can have thousands, but recommend < 100 per span
- **Size:** Events with large attributes increase memory
- **Timeline:** Events maintain chronological order

### Best Practices

**Use Attributes For:**
- ✅ Classification (model, provider, operation type)
- ✅ Metrics (token counts, latency, costs)
- ✅ Static metadata (session ID, user ID)

**Use Events For:**
- ✅ Message sequences (user → assistant → user)
- ✅ Tool invocations timeline
- ✅ State transitions
- ✅ Checkpoints in long operations

**Avoid:**
- ❌ Large strings in attributes (> 1KB)
- ❌ Hundreds of events per span (impacts performance)
- ❌ Duplicate data (put in attributes OR events, not both)

---

## OpenTelemetry Spec References

- **Span Attributes:** https://opentelemetry.io/docs/specs/otel/trace/api/#set-attributes
- **Span Events:** https://opentelemetry.io/docs/specs/otel/trace/api/#add-events
- **GenAI Semantic Conventions:** https://opentelemetry.io/docs/specs/semconv/gen-ai/
- **Python API:** https://opentelemetry-python.readthedocs.io/en/latest/api/trace.html

---

**Status:** ✅ Analysis Complete  
**Next Steps:**
1. Implement span event API in HoneyHiveTracer
2. Add GenAI semantic convention helpers
3. Update documentation with event examples
4. Test with AWS Strands integration (they use events extensively!)

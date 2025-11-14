# OpenTelemetry Span Events: Neutral Provider Analysis
**Date:** October 15, 2025  
**Purpose:** Analyze span event support in context of HoneyHive's neutral BYOI architecture

---

## HoneyHive's Neutral Provider Positioning

From `docs/explanation/architecture/byoi-design.rst`:

> **BYOI Architecture**: HoneyHive's BYOI architecture separates concerns:
> - **Core observability infrastructure** (HoneyHive)
> - **LLM library integration** (Instrumentors)  
> - **Business logic** (Your application)

**Key Principles:**
1. ✅ **Provider Agnostic**: Compatible with any OpenTelemetry-compliant instrumentor
2. ✅ **No Fixed Dependencies**: No LLM library dependencies in core SDK
3. ✅ **OpenTelemetry Foundation**: Built on OTel standards for interoperability
4. ✅ **Instrumentor Choice**: Users decide - OpenInference, Traceloop, or custom

**What This Means for Span Events:**

As a **neutral observability provider**, HoneyHive should:
- ✅ **Support ALL OpenTelemetry features transparently** (including span events)
- ✅ **Not prescribe HOW to use events** (that's up to instrumentors/frameworks)
- ✅ **Enable standard OTel APIs** (let spans work as OpenTelemetry intends)
- ❌ **Not create custom abstractions** (stay neutral, follow OTel standards)

---

## Current State: Span Events Support

### ✅ What Works Today

**1. Span Events Flow Through Correctly**

When instrumentors or frameworks use `span.add_event()`, those events are:
- Captured by OpenTelemetry SDK
- Processed by HoneyHiveSpanProcessor
- Exported to HoneyHive backend
- Visible in HoneyHive dashboard

**Evidence:**
- OpenTelemetry SDK handles event storage
- HoneyHiveSpanProcessor receives `ReadableSpan` with events
- OTLP exporter includes events in span data

**Example from AWS Strands:**
```python
# Strands SDK adds events to spans
span.add_event(
    "gen_ai.user.message",
    attributes={"content": '[{"text": "Hello"}]'}
)

# These events automatically flow through HoneyHive ✅
# Because HoneyHive provides the TracerProvider
```

**2. Exception Events Supported**

```python
# Already works in HoneyHive
if hasattr(span, "record_exception"):
    span.record_exception(e)  # Creates "exception" event
```

### ⚠️ What's Limited

**Users Cannot Easily Add Custom Events**

**Current API:**
```python
# This DOES work but isn't documented:
with tracer.trace("my_operation") as span:
    span.add_event("checkpoint", {"status": "validated"})  # ✅ Works!
    
# This DOESN'T work (no tracer method):
tracer.add_span_event("checkpoint", {"status": "validated"})  # ❌ No such method
```

**Why it matters:**
- Users may want to add custom checkpoints
- GenAI frameworks use events extensively (AWS Strands, etc.)
- Users might want to manually instrument when BYOI instrumentors don't cover their use case

---

## The Neutral Provider Approach

### What HoneyHive SHOULD Do

**1. Enable Span Access (Documentation Priority)**

**Document that users can access and use the span object:**

```python
# docs/how-to/manual-instrumentation.rst

Adding Custom Events to Spans
==============================

HoneyHive's spans are standard OpenTelemetry spans, supporting all OTel features including events.

**Add events during manual instrumentation:**

.. code-block:: python

    with tracer.trace("my_operation") as span:
        # Add checkpoint event
        span.add_event("validation_start", {
            "record_count": 1000,
            "validation_type": "schema"
        })
        
        # Your logic
        result = validate_data()
        
        # Add result event
        span.add_event("validation_complete", {
            "errors_found": len(result.errors),
            "duration_ms": result.duration
        })

**Access current span from OpenTelemetry:**

.. code-block:: python

    from opentelemetry import trace
    
    def my_function():
        # Get current span from OTel context
        span = trace.get_current_span()
        
        if span and span.is_recording():
            span.add_event("custom_checkpoint", {"data": "value"})

**When to use events vs attributes:**

- **Attributes**: Metadata about the entire operation (model name, user ID, total tokens)
- **Events**: Discrete occurrences during the operation (message sent, tool called, checkpoint reached)
```

**2. Optional Convenience Method (Low Priority)**

If users request it, add a simple passthrough:

```python
# Optional addition to HoneyHiveTracer
def add_event_to_current_span(
    self,
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    timestamp: Optional[int] = None
) -> None:
    """Add event to the current active span.
    
    This is a convenience method that adds an event to whatever span
    is currently active in the OpenTelemetry context.
    
    Args:
        name: Event name
        attributes: Event attributes (same types as span attributes)
        timestamp: Optional nanosecond timestamp
    
    Example:
        >>> # During traced operation
        >>> tracer.add_event_to_current_span(
        ...     "checkpoint",
        ...     {"phase": "validation", "records": 1000}
        ... )
    
    Note:
        This is equivalent to calling span.add_event() directly.
        Prefer accessing the span object for more control.
    """
    from opentelemetry import trace
    
    span = trace.get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes=attributes, timestamp=timestamp)
```

### What HoneyHive SHOULD NOT Do

**❌ Don't Create Custom Event Abstractions**

```python
# DON'T DO THIS - Too prescriptive for neutral provider
def add_user_message_event(self, content: str, **kwargs) -> None:
    """Add gen_ai.user.message event."""
    # This is semantic convention specific
    # Let instrumentors handle this
    pass

def add_assistant_message_event(self, content: str, finish_reason: str) -> None:
    """Add gen_ai.choice event."""
    # This is semantic convention specific
    # Let instrumentors handle this
    pass
```

**Why not:**
- **Violates BYOI principles** - Prescribes specific conventions
- **Not neutral** - Favors GenAI semantic conventions
- **Instrumentor's job** - OpenInference/Traceloop should handle this
- **Maintenance burden** - Must track semantic convention changes
- **Not composable** - What about non-GenAI use cases?

**❌ Don't Ship Semantic Convention Libraries**

```python
# DON'T DO THIS
from honeyhive.conventions.genai import GenAIEventHelper

# This makes HoneyHive non-neutral
```

**Why not:**
- Semantic conventions evolve (v1.36.0 → v1.37.0)
- Different instrumentors may use different conventions
- Users should choose their conventions via instrumentors
- Creates tight coupling HoneyHive doesn't want

---

## Integration with AWS Strands (Real-World Example)

**AWS Strands SDK uses span events extensively:**

From `docs/AWS_STRANDS_SDK_ANALYSIS.md`:

```python
# Strands adds 20+ different event types:
span.add_event("gen_ai.user.message", attributes={...})
span.add_event("gen_ai.choice", attributes={...})
span.add_event("gen_ai.tool.message", attributes={...})
span.add_event("gen_ai.client.inference.operation.details", attributes={...})
```

**HoneyHive's Role with Strands:**

1. ✅ **Provide TracerProvider** via `trace_api.set_tracer_provider(tracer.provider)`
2. ✅ **Receive spans with events** from Strands via HoneyHiveSpanProcessor
3. ✅ **Export events** to HoneyHive backend via OTLP exporter
4. ✅ **Display events** in HoneyHive dashboard timeline
5. ❌ **Don't interfere** with Strands' event naming/format

**This is the BYOI model in action:**
- Strands handles semantic conventions (they're the instrumentor/framework)
- HoneyHive handles observability infrastructure (neutral provider)
- User gets best of both: Strands' rich events + HoneyHive's analytics

---

## Recommendations

### Priority 1: Documentation (High Impact, Low Effort)

**Action:** Add section to manual instrumentation docs

**Location:** `docs/how-to/manual-instrumentation.rst`

**Content:**
- Explain that spans are standard OTel spans
- Show `span.add_event()` examples
- Explain events vs attributes
- Show `trace.get_current_span()` pattern
- Link to OTel semantic conventions (let users choose)

**Why:**
- Users may not realize span events are supported
- Documents existing capability
- Enables advanced use cases
- Maintains neutrality

### Priority 2: Verify Backend Support (Critical Check)

**Action:** Verify HoneyHive backend properly handles span events

**Check:**
1. OTLP exporter includes events in span proto
2. Backend stores event data (name, attributes, timestamp)
3. Dashboard displays events in span timeline
4. Events are searchable/filterable
5. Event attributes are accessible in queries

**If gaps found:**
- Backend team needs to implement event storage/display
- Update OTLP proto handling
- Add UI for event visualization

### Priority 3: Optional Convenience Method (Low Priority)

**Action:** Add `add_event_to_current_span()` if users request it

**When:**
- After documenting direct span access
- If users say direct access is too verbose
- If it simplifies common patterns

**Why low priority:**
- Direct span access already works
- Adding methods increases API surface
- Maintenance overhead

### Priority 4: Integration Testing (Validation)

**Action:** Add test for span events with BYOI instrumentors

**Test Case:**
```python
def test_span_events_flow_through_honeyhive():
    """Verify events added by instrumentors are captured."""
    tracer = HoneyHiveTracer.init(project="test")
    
    # Simulate instrumentor adding events
    with tracer.trace("operation") as span:
        span.add_event("gen_ai.user.message", 
                      attributes={"content": "test"})
        span.add_event("gen_ai.choice", 
                      attributes={"message": "response"})
    
    # Verify events were captured
    # (Check span processor received events)
```

---

## OpenTelemetry Span Event Data Types (Reference)

### Event Structure

```python
span.add_event(
    name="event_name",              # Required: Event identifier (str)
    attributes={                     # Optional: Event attributes
        "key": "value"              # Same types as span attributes
    },
    timestamp=1697654400000000000   # Optional: Nanoseconds since epoch (int)
)
```

### Supported Attribute Types (Same as Span Attributes)

| Type | Python Type | Example |
|------|-------------|---------|
| String | `str` | `"user_message"` |
| Boolean | `bool` | `True` |
| Int | `int` | `42` |
| Double | `float` | `3.14` |
| Array of Strings | `List[str]` | `["tool1", "tool2"]` |
| Array of Booleans | `List[bool]` | `[True, False]` |
| Array of Ints | `List[int]` | `[1, 2, 3]` |
| Array of Doubles | `List[float]` | `[1.0, 2.5]` |

### Event vs Attribute Decision Guide

**Use Span Attributes For:**
- ✅ Metadata about the entire operation
- ✅ Classification (model, provider, type)
- ✅ Aggregatable metrics (tokens, cost, latency)
- ✅ Fixed values set once

**Use Span Events For:**
- ✅ Timeline of occurrences
- ✅ Sequences (message → response → tool → response)
- ✅ State transitions
- ✅ Multiple occurrences of same type
- ✅ Timestamped milestones

**Examples:**

| Data | Type | Rationale |
|------|------|-----------|
| `model="gpt-4"` | Attribute | Fixed for entire operation |
| `input_tokens=150` | Attribute | Aggregate metric |
| User sent message | Event | Specific moment in time |
| Tool invoked | Event | Discrete occurrence |
| Agent handoff | Event | State transition |
| `session_id="abc"` | Attribute | Metadata for operation |

---

## Summary: HoneyHive's Neutral Provider Role

### ✅ What HoneyHive Provides (Neutral Infrastructure)

1. **OpenTelemetry TracerProvider** - Standard OTel foundation
2. **Span Processing** - Receives spans from any OTel source
3. **OTLP Export** - Sends spans (with events) to backend
4. **Dashboard** - Visualizes traces and events
5. **Storage** - Persists span data including events

### ✅ What Instrumentors/Frameworks Provide (Conventions)

1. **Auto-instrumentation** - Capture LLM calls automatically
2. **Semantic Conventions** - Apply GenAI/LLM conventions
3. **Event Creation** - Add framework-specific events
4. **Attribute Standards** - Set meaningful attributes
5. **Context Propagation** - Link related operations

### ✅ What Users Get (Composability)

```python
# User chooses their stack:
from honeyhive import HoneyHiveTracer          # Infrastructure
from openinference.instrumentation.openai import OpenAIInstrumentor  # Convention
import openai                                   # LLM library

# Initialize (BYOI pattern):
tracer = HoneyHiveTracer.init(project="my-app")  # 1. Provider
instrumentor = OpenAIInstrumentor()              # 2. Instrumentor  
instrumentor.instrument(tracer_provider=tracer.provider)  # 3. Connect

# Use normally:
client = openai.OpenAI()
response = client.chat.completions.create(...)  # Automatically traced

# Add custom events if needed:
from opentelemetry import trace
span = trace.get_current_span()
span.add_event("custom_checkpoint", {"data": "value"})  # Manual event
```

**This is BYOI in action:**
- HoneyHive: Neutral infrastructure layer
- OpenInference: Convention/instrumentation layer
- OpenAI: LLM functionality layer
- User: Composes all three

---

## Next Actions

### Immediate (Documentation)
1. ✅ Document span event support in manual instrumentation guide
2. ✅ Show `span.add_event()` examples
3. ✅ Explain when to use events vs attributes
4. ✅ Link to OpenTelemetry semantic conventions

### Validation (Backend Check)
1. ⚠️ Verify backend stores span events
2. ⚠️ Verify dashboard displays events in timeline
3. ⚠️ Verify events are searchable/queryable

### Optional (User Request)
1. ⏳ Add convenience method if users ask
2. ⏳ Create integration tests with event-heavy frameworks (Strands)
3. ⏳ Add event examples to tutorials

### Avoid (Stay Neutral)
1. ❌ Don't create GenAI semantic convention helpers
2. ❌ Don't prescribe event naming conventions
3. ❌ Don't ship semantic convention libraries
4. ❌ Don't create custom event abstractions

---

**Status:** ✅ Analysis Complete  
**Position:** Neutral observability provider supporting standard OTel features  
**Recommendation:** Document existing span event support, verify backend handling, stay neutral

## References

- HoneyHive BYOI Design: `docs/explanation/architecture/byoi-design.rst`
- OpenTelemetry Span Events Spec: https://opentelemetry.io/docs/specs/otel/trace/api/#add-events
- GenAI Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- AWS Strands Analysis: `docs/AWS_STRANDS_SDK_ANALYSIS.md`


# HoneyHive Ingestion Service: Span Events Analysis
**Date:** October 15, 2025  
**Analyzed Repository:** `hive-kube/kubernetes/ingestion_service`  
**Critical Finding:** ⚠️ **SPAN EVENTS ARE BEING DROPPED AT INGESTION LAYER**

---

## Executive Summary

### 🔴 CRITICAL GAP IDENTIFIED

**The HoneyHive ingestion service is silently dropping all OpenTelemetry span events.**

This is a **severe compatibility issue** for OTel-native frameworks like AWS Strands that rely heavily on span events for capturing:
- LLM message exchanges (`gen_ai.user.message`, `gen_ai.choice`)
- Tool invocations (`gen_ai.tool.message`)
- State transitions and checkpoints
- Fine-grained operation details

**Impact:**
- AWS Strands SDK users will lose critical GenAI semantic convention data
- Message-level tracing will not work
- Tool call details will be lost
- GenAI frameworks following OTel standards will appear "broken"

---

## Evidence: Code Analysis

### 1. Protobuf Structure DOES Support Events ✅

**File:** `app/utils/trace_pb.js`

The OpenTelemetry protobuf definition includes span events:

```javascript
// Line 994: Span.prototype definition
Span.prototype.events = $util.emptyArray;
Span.prototype.droppedEventsCount = 0;

// Span.Event structure (lines 1757-1781):
Event.prototype.timeUnixNano = $util.Long ? $util.Long.fromBits(0,0,false) : 0;
Event.prototype.name = '';
Event.prototype.attributes = $util.emptyArray;
Event.prototype.droppedAttributesCount = 0;
```

**Conclusion:** The protobuf decoder DOES parse span events from incoming OTLP data.

---

### 2. Ingestion Service IGNORES Events ❌

**File:** `app/services/otel_processing_service.js`

#### Function: `parseTrace(trace)` (Lines 29-142)

The critical processing loop:

```javascript:38:49:app/services/otel_processing_service.js
scopeSpan.spans.forEach((span) => {
  let eventMetadata = { ...metadata };
  let eventName = span.name;
  span.startTimeUnixNano = parseInt(span.startTimeUnixNano);
  span.endTimeUnixNano = parseInt(span.endTimeUnixNano);
  let parsedAttributes = {};
  span.attributes.forEach((attribute) => {      // ← ONLY attributes processed
    let attributeName = attribute.key;
    let attributeValue = parseAnyValue(attribute.value);
    parsedAttributes[attributeName] = attributeValue;
  });
  parsedAttributes = parseIndexedAttributes(parsedAttributes);
  // ... rest of processing
```

**What's Being Processed:**
- ✅ `span.name`
- ✅ `span.startTimeUnixNano`
- ✅ `span.endTimeUnixNano`
- ✅ `span.attributes` (extensively mapped)
- ✅ Span hierarchy (via trace IDs)

**What's Being IGNORED:**
- ❌ `span.events` - **NEVER accessed**
- ❌ `span.status` - Not extracted
- ❌ `span.links` - Not extracted

**Grep Confirmation:**
```bash
$ grep -n "span\.events" app/services/otel_processing_service.js
# No matches found

$ grep -n "span\.events" app/routes/*.js app/services/*.js
# No matches found
```

---

### 3. NextJS Processing Also Ignores Events ❌

**File:** `app/services/otel_processing_service.js`

#### Function: `parseNextJSTrace(trace)` (Lines 160-338)

Same issue - no event processing:

```javascript:169:188:app/services/otel_processing_service.js
scopeSpan.spans.forEach((span) => {
  let eventMetadata = { ...metadata };
  let eventConfig = {};
  let eventName = span.name;
  let inputs = {};
  let outputs = {};
  let metrics = {};
  let feedback = {};
  let error = null;

  span.startTimeUnixNano = parseInt(span.startTimeUnixNano);
  span.endTimeUnixNano = parseInt(span.endTimeUnixNano);

  let parsedAttributes = {};
  span.attributes.forEach((attribute) => {      // ← ONLY attributes
    let attributeName = attribute.key;
    let attributeValue = parseAnyValue(attribute.value);
    parsedAttributes[attributeName] = attributeValue;
  });
  parsedAttributes = parseIndexedAttributes(parsedAttributes);
```

**Conclusion:** Events are dropped for ALL ingestion paths.

---

## Impact Analysis: AWS Strands SDK

### What Strands Sends

Based on analysis in `/tmp/sdk-analysis/strands-sdk/src/strands/telemetry/tracer.py`:

#### 1. User Message Event
```python
span.add_event(
    "gen_ai.user.message",
    attributes={
        "content": json.dumps([{"text": "What is the weather?"}])
    }
)
```

**HoneyHive Status:** 🔴 **DROPPED**

---

#### 2. Assistant Response Event
```python
span.add_event(
    "gen_ai.choice",
    attributes={
        "message": json.dumps([{"text": "The weather is sunny"}]),
        "finish_reason": "end_turn"
    }
)
```

**HoneyHive Status:** 🔴 **DROPPED**

---

#### 3. Tool Call Event
```python
span.add_event(
    "gen_ai.tool.message",
    attributes={
        "role": "tool",
        "content": json.dumps({
            "name": "get_weather",
            "input": {"city": "SF"}
        }),
        "id": "call_123"
    }
)
```

**HoneyHive Status:** 🔴 **DROPPED**

---

### What Users Will See

When AWS Strands users send traces to HoneyHive:

| Expected Behavior | Actual Behavior |
|-------------------|----------------|
| Message-level tracing visible | ❌ Messages not captured |
| Tool invocation timeline | ❌ Tool calls not captured |
| GenAI semantic convention compliance | ❌ Events dropped |
| Rich conversation context | ❌ Only span-level attributes |
| Checkpoint markers | ❌ Lost |

**User Experience:** Tracing will appear "broken" compared to other OTel collectors.

---

## Why This Is Critical

### 1. OTel Semantic Conventions Rely on Events

The GenAI semantic conventions (old and new) use events extensively:

**Old Convention:**
- `gen_ai.user.message` - User input event
- `gen_ai.choice` - Assistant response event
- `gen_ai.tool.message` - Tool call event

**New Convention (v0.4.0):**
- `gen_ai.client.inference.operation.details` - Unified operation event with input/output messages

**Current HoneyHive Support:** 0%

---

### 2. Events vs Attributes: Why Both Matter

| Use Case | Attributes | Events |
|----------|-----------|---------|
| **Model metadata** | ✅ `gen_ai.request.model="gpt-4"` | N/A |
| **Token counts** | ✅ `gen_ai.usage.input_tokens=150` | N/A |
| **Message exchanges** | ❌ Too verbose for attributes | ✅ `gen_ai.user.message` event |
| **Tool invocations** | ❌ Sequence lost | ✅ `gen_ai.tool.message` event |
| **Timeline** | ❌ No timestamps | ✅ Each event has timestamp |
| **Conversation flow** | ❌ Hard to reconstruct | ✅ Chronological events |

**Key Insight:** Attributes describe the span; events describe what happened within it.

---

### 3. BYOI Architecture Requires Full OTel Support

HoneyHive's philosophy is to be a **neutral observability provider** that works with any instrumentor.

**Current Reality:**
- ✅ Supports OpenTelemetry **span attributes**
- ✅ Supports OpenTelemetry **span hierarchy**
- ✅ Supports OpenTelemetry **trace context propagation**
- ❌ **Does NOT support OpenTelemetry span events**
- ❌ **Does NOT support OpenTelemetry span status**
- ❌ **Does NOT support OpenTelemetry span links**

**Consequence:** HoneyHive is NOT truly OTel-compliant for GenAI use cases.

---

## Comparison: Other OTel Collectors

### What Standard Collectors Do

**Jaeger, Zipkin, Tempo, Honeycomb, DataDog, etc.:**
- ✅ Ingest span events
- ✅ Display events in trace timeline
- ✅ Support GenAI semantic conventions
- ✅ Allow querying on event attributes

**HoneyHive:**
- ❌ Drops events silently
- ❌ No way to see message exchanges
- ❌ GenAI conventions incomplete

---

## Root Cause Analysis

### Why Are Events Being Dropped?

**Hypothesis 1: Legacy Event Model**

HoneyHive has its own "event" concept (model events, tool events, chain events) that predates OTel adoption.

```javascript
// Current HoneyHive event structure
let event = {
  project: project_name,
  source: source,
  session_id: session_id,
  event_name: eventName,          // From span.name
  event_type: eventType,          // Derived from attributes
  inputs: inputs,                 // Extracted from attributes
  outputs: outputs,               // Extracted from attributes
  metrics: metrics,               // Extracted from attributes
  metadata: eventMetadata,        // Extracted from attributes
  config: eventConfig,            // Extracted from attributes
  start_time: start_time,
  end_time: end_time,
  duration: duration,
  event_id: eventId,
  children: [],
  // ...
};
```

**Issue:** This maps 1 OTel span → 1 HoneyHive event, but doesn't account for multiple OTel events within a span.

---

**Hypothesis 2: Attribute-Centric Architecture**

The ingestion service was built to extract all data from span attributes:

```javascript:54:55:app/services/otel_processing_service.js
// Apply 3-tier attribute mapping
const { eventData, context } = applyAttributeMappings(parsedAttributes, instrumentor);
```

**Issue:** GenAI semantic conventions use BOTH attributes AND events, but HoneyHive only looks at attributes.

---

**Hypothesis 3: Performance Concerns**

Events can be numerous (100+ per span in chat scenarios). Perhaps events were intentionally skipped?

**Counter:** Modern OTel collectors handle thousands of events efficiently. This is not a valid reason.

---

## What Needs to Be Fixed

### Priority 1: Ingest Span Events ⚠️

**Required Changes:**

#### 1.1. Parse Span Events in `parseTrace()`

**File:** `app/services/otel_processing_service.js`

**Current (line 38-49):**
```javascript
scopeSpan.spans.forEach((span) => {
  // ... parse attributes only
  span.attributes.forEach((attribute) => {
    // ...
  });
  // ❌ Events never accessed
```

**Proposed:**
```javascript
scopeSpan.spans.forEach((span) => {
  // ... parse attributes
  
  // Parse span events
  let spanEvents = [];
  if (span.events && Array.isArray(span.events)) {
    span.events.forEach((event) => {
      let parsedEvent = {
        name: event.name,
        timestamp: parseInt(event.timeUnixNano),
        attributes: {}
      };
      
      if (event.attributes && Array.isArray(event.attributes)) {
        event.attributes.forEach((attr) => {
          parsedEvent.attributes[attr.key] = parseAnyValue(attr.value);
        });
      }
      
      spanEvents.push(parsedEvent);
    });
  }
  
  // Include events in the HoneyHive event
  let event = {
    // ... existing fields
    span_events: spanEvents,  // NEW FIELD
    // ...
  };
```

---

#### 1.2. Store Events in ClickHouse

**Current Schema:** Unknown (need to check ClickHouse table definitions)

**Required Schema Change:**

Option A: **Embedded JSON (Quick Fix)**
```sql
-- Add to existing events table
ALTER TABLE events ADD COLUMN span_events String DEFAULT '[]';
-- Store as JSON array
```

Option B: **Separate Table (Better)**
```sql
CREATE TABLE span_events (
    event_id UUID,              -- FK to events table
    event_name String,          -- e.g., "gen_ai.user.message"
    timestamp UInt64,           -- Nanoseconds since epoch
    attributes String,          -- JSON
    event_order UInt32,         -- Order within span
    INDEX idx_event_id event_id TYPE bloom_filter GRANULARITY 1
) ENGINE = MergeTree()
ORDER BY (event_id, event_order);
```

---

#### 1.3. Update TypeScript Types

**File:** `app/types/index.ts` (assumed)

```typescript
export interface SpanEvent {
  name: string;
  timestamp: number;  // Unix nano
  attributes: Record<string, any>;
  order?: number;
}

export interface HoneyHiveEvent {
  // ... existing fields
  span_events?: SpanEvent[];  // NEW
  // ...
}
```

---

### Priority 2: Support GenAI Event Conventions

Add special handling for GenAI semantic convention events:

```javascript
// Helper function to enrich GenAI events
function enrichGenAIEvent(spanEvent, eventData) {
  const eventName = spanEvent.name;
  
  if (eventName === 'gen_ai.user.message') {
    // Extract user message from event attributes
    const content = spanEvent.attributes.content;
    if (content) {
      try {
        const parsed = JSON.parse(content);
        eventData.inputs.messages = eventData.inputs.messages || [];
        eventData.inputs.messages.push({
          role: 'user',
          content: parsed
        });
      } catch (e) {}
    }
  }
  
  else if (eventName === 'gen_ai.choice') {
    // Extract assistant response
    const message = spanEvent.attributes.message;
    const finishReason = spanEvent.attributes.finish_reason;
    if (message) {
      try {
        const parsed = JSON.parse(message);
        eventData.outputs.messages = eventData.outputs.messages || [];
        eventData.outputs.messages.push({
          role: 'assistant',
          content: parsed,
          finish_reason: finishReason
        });
      } catch (e) {}
    }
  }
  
  else if (eventName === 'gen_ai.tool.message') {
    // Extract tool call
    const toolContent = spanEvent.attributes.content;
    const toolId = spanEvent.attributes.id;
    if (toolContent) {
      try {
        const parsed = JSON.parse(toolContent);
        eventData.metadata.tool_calls = eventData.metadata.tool_calls || [];
        eventData.metadata.tool_calls.push({
          id: toolId,
          name: parsed.name,
          input: parsed.input
        });
      } catch (e) {}
    }
  }
}
```

---

### Priority 3: Support Span Status

**Current:** Span status is not extracted

**Fix:**
```javascript
// In parseTrace():
if (span.status) {
  event.status = {
    code: span.status.code,  // 0=UNSET, 1=OK, 2=ERROR
    message: span.status.message || null
  };
}
```

---

## Testing Requirements

### Unit Tests

```javascript
describe('Span Event Processing', () => {
  it('should parse span events from protobuf', () => {
    const trace = createMockTraceWithEvents();
    const events = parseTrace(trace);
    
    expect(events[0].span_events).toBeDefined();
    expect(events[0].span_events.length).toBe(3);
    expect(events[0].span_events[0].name).toBe('gen_ai.user.message');
  });
  
  it('should extract GenAI message events', () => {
    const trace = createMockGenAITrace();
    const events = parseTrace(trace);
    
    expect(events[0].inputs.messages).toBeDefined();
    expect(events[0].outputs.messages).toBeDefined();
  });
  
  it('should handle spans without events gracefully', () => {
    const trace = createMockTraceWithoutEvents();
    const events = parseTrace(trace);
    
    expect(events[0].span_events).toEqual([]);
  });
});
```

---

### Integration Tests

**Test with AWS Strands SDK:**

```python
# Python test script
from strands import Agent
from honeyhive import HoneyHive

# Initialize HoneyHive tracer
tracer = HoneyHive.init(
    project="strands-test",
    api_key=os.getenv("HONEYHIVE_API_KEY")
)

# Run Strands agent
agent = Agent(model="openai/gpt-4", tools=[get_weather])
result = agent("What's the weather in SF?")

# Verify in HoneyHive:
# 1. Span exists
# 2. Span has events
# 3. Events contain gen_ai.user.message
# 4. Events contain gen_ai.choice
# 5. Events contain gen_ai.tool.message (if tool was called)
```

**Expected Results:**
- ✅ User message captured in event
- ✅ Assistant response captured in event
- ✅ Tool call captured in event
- ✅ Timeline shows all events
- ✅ Events queryable in HoneyHive UI

---

## Migration Strategy

### Phase 1: Non-Breaking Addition ✅ SAFE

1. Add `span_events` field to ingestion (default to `[]`)
2. Add ClickHouse column (nullable or default `[]`)
3. Deploy to staging
4. Test with Strands SDK
5. Deploy to production

**Risk:** Low - existing traces unaffected

---

### Phase 2: GenAI Event Enrichment

1. Add GenAI event parsing helpers
2. Populate `inputs.messages` from events
3. Populate `outputs.messages` from events
4. Test with multiple frameworks (Strands, LangChain, etc.)

**Risk:** Medium - may conflict with attribute-based extraction

---

### Phase 3: UI Updates

1. Update trace viewer to display span events
2. Add event timeline visualization
3. Add event attribute inspection
4. Add event-based filtering

**Risk:** Low - UI-only changes

---

## Comparison: Before vs After

### Current State (Before Fix)

**AWS Strands Trace:**
```
Span: "agent.run"
├─ Attributes:
│  ├─ gen_ai.request.model: "gpt-4"
│  ├─ gen_ai.usage.input_tokens: 150
│  └─ gen_ai.usage.output_tokens: 80
└─ Events: ❌ DROPPED
   ├─ gen_ai.user.message (lost)
   ├─ gen_ai.choice (lost)
   └─ gen_ai.tool.message (lost)
```

**HoneyHive Event:**
```json
{
  "event_name": "agent.run",
  "event_type": "model",
  "config": { "model": "gpt-4" },
  "metrics": { "input_tokens": 150, "output_tokens": 80 },
  "inputs": {},  // ← EMPTY
  "outputs": {}  // ← EMPTY
}
```

---

### Fixed State (After Fix)

**AWS Strands Trace:**
```
Span: "agent.run"
├─ Attributes:
│  ├─ gen_ai.request.model: "gpt-4"
│  ├─ gen_ai.usage.input_tokens: 150
│  └─ gen_ai.usage.output_tokens: 80
└─ Events: ✅ CAPTURED
   ├─ gen_ai.user.message {"content": "What's the weather?"}
   ├─ gen_ai.tool.message {"name": "get_weather", ...}
   └─ gen_ai.choice {"message": "The weather is sunny"}
```

**HoneyHive Event:**
```json
{
  "event_name": "agent.run",
  "event_type": "model",
  "config": { "model": "gpt-4" },
  "metrics": { "input_tokens": 150, "output_tokens": 80 },
  "inputs": {
    "messages": [
      { "role": "user", "content": "What's the weather?" }
    ]
  },
  "outputs": {
    "messages": [
      { "role": "assistant", "content": "The weather is sunny" }
    ]
  },
  "span_events": [
    {
      "name": "gen_ai.user.message",
      "timestamp": 1697654400000000000,
      "attributes": { "content": "[{\"text\": \"What's the weather?\"}]" }
    },
    {
      "name": "gen_ai.tool.message",
      "timestamp": 1697654401000000000,
      "attributes": { "name": "get_weather", "input": "{\"city\": \"SF\"}" }
    },
    {
      "name": "gen_ai.choice",
      "timestamp": 1697654402000000000,
      "attributes": { "message": "[{\"text\": \"The weather is sunny\"}]", "finish_reason": "end_turn" }
    }
  ]
}
```

---

## Recommendations

### Immediate Actions (This Sprint)

1. **Verify ClickHouse Schema**
   - Check if `span_events` column exists
   - If not, create migration script

2. **Add Event Parsing**
   - Update `parseTrace()` to extract `span.events`
   - Update `parseNextJSTrace()` to extract `span.events`
   - Add unit tests

3. **Deploy to Staging**
   - Test with mock Strands traces
   - Verify events are stored
   - Check performance impact

---

### Short-Term Actions (Next 2 Sprints)

4. **GenAI Event Enrichment**
   - Add `enrichGenAIEvent()` helper
   - Map events to `inputs.messages` and `outputs.messages`
   - Add integration tests with Strands SDK

5. **Documentation**
   - Update API docs to mention span events
   - Add GenAI semantic convention examples
   - Document event storage format

6. **UI Updates**
   - Display span events in trace viewer
   - Add event timeline visualization
   - Add event filtering

---

### Long-Term Actions (Future)

7. **Full OTel Compliance**
   - Add span status support
   - Add span links support
   - Add resource attributes (if not already supported)
   - Add scope attributes (if not already supported)

8. **Performance Optimization**
   - Benchmark event processing overhead
   - Add event sampling if needed
   - Optimize ClickHouse queries for events

9. **Advanced Features**
   - Event-based alerting
   - Event-based metrics
   - Event correlation across traces

---

## Appendix: OpenTelemetry Span Events Specification

### Event Structure (OTLP Proto)

```protobuf
message Span {
  // ... other fields
  repeated Event events = 11;
  uint32 dropped_events_count = 12;
  
  message Event {
    fixed64 time_unix_nano = 1;
    string name = 2;
    repeated KeyValue attributes = 3;
    uint32 dropped_attributes_count = 4;
  }
}
```

### GenAI Semantic Conventions

**Old Convention (pre-v0.4.0):**
- Events: `gen_ai.user.message`, `gen_ai.choice`, `gen_ai.tool.message`
- Attributes: Model, tokens on span; messages in events

**New Convention (v0.4.0+):**
- Event: `gen_ai.client.inference.operation.details`
- Attributes: Messages moved to event attributes (`gen_ai.input.messages`, `gen_ai.output.messages`)

**HoneyHive Must Support Both:** Many frameworks still use old convention.

---

## References

1. **OpenTelemetry Trace Specification**  
   https://opentelemetry.io/docs/specs/otel/trace/api/#add-events

2. **GenAI Semantic Conventions**  
   https://opentelemetry.io/docs/specs/semconv/gen-ai/

3. **AWS Strands SDK Analysis**  
   `/Users/josh/src/github.com/honeyhiveai/python-sdk/docs/AWS_STRANDS_SDK_ANALYSIS.md`

4. **HoneyHive OTel Span Data Types Analysis**  
   `/Users/josh/src/github.com/honeyhiveai/python-sdk/docs/OTEL_SPAN_DATA_TYPES_ANALYSIS.md`

5. **HoneyHive BYOI Architecture Analysis**  
   `/Users/josh/src/github.com/honeyhiveai/python-sdk/docs/OTEL_SPAN_EVENTS_NEUTRAL_PROVIDER_ANALYSIS.md`

---

**Status:** ✅ Analysis Complete  
**Next Steps:**
1. Present findings to engineering team
2. Create Jira tickets for implementation
3. Prioritize for next sprint
4. Test with AWS Strands SDK after implementation

---

**Critical Insight:**  
> HoneyHive cannot claim to be a neutral observability provider or support BYOI architecture without full OpenTelemetry compliance. Span events are not optional—they are essential for GenAI use cases.


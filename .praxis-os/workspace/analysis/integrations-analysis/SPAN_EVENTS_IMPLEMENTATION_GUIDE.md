# Span Events Implementation Guide
**Quick reference for engineering team**  
**Date:** October 15, 2025

---

## Code Changes Required

### 1. Update `parseTrace()` - Add Event Parsing

**File:** `hive-kube/kubernetes/ingestion_service/app/services/otel_processing_service.js`

**Location:** After line 49 (after `parsedAttributes = parseIndexedAttributes(parsedAttributes);`)

```javascript
// ============ ADD THIS CODE ============

// Parse span events (NEW)
let spanEvents = [];
if (span.events && Array.isArray(span.events)) {
  span.events.forEach((event) => {
    let parsedEvent = {
      name: event.name,
      timestamp: parseInt(event.timeUnixNano),
      attributes: {}
    };
    
    // Parse event attributes
    if (event.attributes && Array.isArray(event.attributes)) {
      event.attributes.forEach((attr) => {
        parsedEvent.attributes[attr.key] = parseAnyValue(attr.value);
      });
    }
    
    spanEvents.push(parsedEvent);
  });
}

// ============ END NEW CODE ============
```

**Location:** Inside event object construction (around line 114)

```javascript
let event = {
  project: project_name,
  source: source,
  session_id: session_id,
  event_name: eventName,
  event_type: eventType,
  inputs: inputs,
  outputs: outputs,
  error: error ? error.toString() : null,
  parent_id: session_id,
  metrics: metrics,
  metadata: eventMetadata,
  config: eventConfig,
  start_time: start_time,
  end_time: end_time,
  duration: (end_time - start_time) / 1000,
  event_id: eventId,
  children: [],
  children_ids: [],
  user_properties: {},
  feedback: feedback,
  span_events: spanEvents,  // ← ADD THIS LINE
};
```

---

### 2. Update `parseNextJSTrace()` - Add Event Parsing

**File:** Same file as above

**Location:** After line 188 (after `parsedAttributes = parseIndexedAttributes(parsedAttributes);`)

```javascript
// ============ ADD THIS CODE ============

// Parse span events (NEW)
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

// ============ END NEW CODE ============
```

**Location:** Inside event object construction (around line 308)

```javascript
let event = {
  event_name: eventName,
  event_type: eventType,
  inputs: inputs,
  outputs: outputs,
  error: error,
  metrics: metrics,
  metadata: eventMetadata,
  config: eventConfig,
  start_time: start_time,
  end_time: end_time,
  duration: (end_time - start_time) / 1000,
  event_id: uuidv4(),
  parent_id: null,
  children: [],
  children_ids: [],
  user_properties: {},
  feedback: feedback,
  span_events: spanEvents,  // ← ADD THIS LINE
  otelLineage: {
    traceId: safeBufferToHex(span.traceId),
    spanId: safeBufferToHex(span.spanId),
    parentSpanId: span.parentSpanId ? safeBufferToHex(span.parentSpanId) : null,
  },
};
```

---

### 3. (Optional) Add GenAI Event Enrichment

**File:** Same file as above

**Location:** Create new function after `parseAnyValue()`

```javascript
/**
 * Enrich inputs/outputs from GenAI semantic convention events
 * @param {Array} spanEvents - Parsed span events
 * @param {Object} inputs - Inputs object to enrich
 * @param {Object} outputs - Outputs object to enrich
 */
function enrichFromGenAIEvents(spanEvents, inputs, outputs) {
  spanEvents.forEach((event) => {
    // User message (old convention)
    if (event.name === 'gen_ai.user.message') {
      inputs.messages = inputs.messages || [];
      try {
        const content = event.attributes.content;
        const parsed = typeof content === 'string' ? JSON.parse(content) : content;
        inputs.messages.push({
          role: 'user',
          content: parsed,
          timestamp: event.timestamp
        });
      } catch (e) {
        console.debug('Failed to parse gen_ai.user.message content:', e);
      }
    }
    
    // Assistant response (old convention)
    else if (event.name === 'gen_ai.choice') {
      outputs.messages = outputs.messages || [];
      try {
        const message = event.attributes.message;
        const parsed = typeof message === 'string' ? JSON.parse(message) : message;
        outputs.messages.push({
          role: 'assistant',
          content: parsed,
          finish_reason: event.attributes.finish_reason || null,
          timestamp: event.timestamp
        });
      } catch (e) {
        console.debug('Failed to parse gen_ai.choice message:', e);
      }
    }
    
    // Tool call (old convention)
    else if (event.name === 'gen_ai.tool.message') {
      metadata.tool_calls = metadata.tool_calls || [];
      try {
        const content = event.attributes.content;
        const parsed = typeof content === 'string' ? JSON.parse(content) : content;
        metadata.tool_calls.push({
          id: event.attributes.id || null,
          name: parsed.name || null,
          input: parsed.input || null,
          timestamp: event.timestamp
        });
      } catch (e) {
        console.debug('Failed to parse gen_ai.tool.message content:', e);
      }
    }
    
    // New convention (v0.4.0+)
    else if (event.name === 'gen_ai.client.inference.operation.details') {
      // Extract input messages
      if (event.attributes['gen_ai.input.messages']) {
        try {
          const inputMsgs = event.attributes['gen_ai.input.messages'];
          const parsed = typeof inputMsgs === 'string' ? JSON.parse(inputMsgs) : inputMsgs;
          inputs.messages = parsed;
        } catch (e) {
          console.debug('Failed to parse gen_ai.input.messages:', e);
        }
      }
      
      // Extract output messages
      if (event.attributes['gen_ai.output.messages']) {
        try {
          const outputMsgs = event.attributes['gen_ai.output.messages'];
          const parsed = typeof outputMsgs === 'string' ? JSON.parse(outputMsgs) : outputMsgs;
          outputs.messages = parsed;
        } catch (e) {
          console.debug('Failed to parse gen_ai.output.messages:', e);
        }
      }
    }
  });
}
```

**Usage in `parseTrace()`:**

```javascript
// After parsing spanEvents and before creating event object:
enrichFromGenAIEvents(spanEvents, inputs, outputs);
```

---

## Unit Tests Required

**File:** `hive-kube/kubernetes/ingestion_service/tests/unit/services/otel_processing_service.test.js` (create if doesn't exist)

```javascript
const { parseTrace, parseNextJSTrace } = require('../../../app/services/otel_processing_service');

describe('Span Events Processing', () => {
  describe('parseTrace', () => {
    it('should parse span events from protobuf', () => {
      const trace = createMockTraceWithEvents([
        { name: 'gen_ai.user.message', attributes: { content: '{"text": "Hello"}' } },
        { name: 'gen_ai.choice', attributes: { message: '{"text": "Hi"}' } }
      ]);
      
      const events = parseTrace(trace);
      
      expect(events[0].span_events).toBeDefined();
      expect(events[0].span_events.length).toBe(2);
      expect(events[0].span_events[0].name).toBe('gen_ai.user.message');
      expect(events[0].span_events[1].name).toBe('gen_ai.choice');
    });
    
    it('should handle spans without events', () => {
      const trace = createMockTraceWithoutEvents();
      
      const events = parseTrace(trace);
      
      expect(events[0].span_events).toEqual([]);
    });
    
    it('should parse event timestamps', () => {
      const trace = createMockTraceWithEvents([
        { name: 'test.event', timeUnixNano: '1697654400000000000' }
      ]);
      
      const events = parseTrace(trace);
      
      expect(events[0].span_events[0].timestamp).toBe(1697654400000000000);
    });
    
    it('should parse event attributes', () => {
      const trace = createMockTraceWithEvents([
        {
          name: 'test.event',
          attributes: [
            { key: 'key1', value: { stringValue: 'value1' } },
            { key: 'key2', value: { intValue: 42 } }
          ]
        }
      ]);
      
      const events = parseTrace(trace);
      
      expect(events[0].span_events[0].attributes.key1).toBe('value1');
      expect(events[0].span_events[0].attributes.key2).toBe(42);
    });
  });
  
  describe('GenAI Event Enrichment', () => {
    it('should extract user messages from gen_ai.user.message events', () => {
      const trace = createMockTraceWithEvents([
        {
          name: 'gen_ai.user.message',
          attributes: { content: JSON.stringify([{ text: 'What is the weather?' }]) }
        }
      ]);
      
      const events = parseTrace(trace);
      
      expect(events[0].inputs.messages).toBeDefined();
      expect(events[0].inputs.messages.length).toBe(1);
      expect(events[0].inputs.messages[0].role).toBe('user');
    });
    
    it('should extract assistant messages from gen_ai.choice events', () => {
      const trace = createMockTraceWithEvents([
        {
          name: 'gen_ai.choice',
          attributes: {
            message: JSON.stringify([{ text: 'The weather is sunny' }]),
            finish_reason: 'end_turn'
          }
        }
      ]);
      
      const events = parseTrace(trace);
      
      expect(events[0].outputs.messages).toBeDefined();
      expect(events[0].outputs.messages.length).toBe(1);
      expect(events[0].outputs.messages[0].role).toBe('assistant');
      expect(events[0].outputs.messages[0].finish_reason).toBe('end_turn');
    });
    
    it('should extract tool calls from gen_ai.tool.message events', () => {
      const trace = createMockTraceWithEvents([
        {
          name: 'gen_ai.tool.message',
          attributes: {
            content: JSON.stringify({ name: 'get_weather', input: { city: 'SF' } }),
            id: 'call_123'
          }
        }
      ]);
      
      const events = parseTrace(trace);
      
      expect(events[0].metadata.tool_calls).toBeDefined();
      expect(events[0].metadata.tool_calls.length).toBe(1);
      expect(events[0].metadata.tool_calls[0].name).toBe('get_weather');
    });
  });
});

// Helper functions
function createMockTraceWithEvents(events) {
  return {
    resourceSpans: [{
      scopeSpans: [{
        scope: { name: 'test.scope' },
        spans: [{
          name: 'test.span',
          startTimeUnixNano: '1697654400000000000',
          endTimeUnixNano: '1697654402000000000',
          attributes: [
            { key: 'honeyhive.session_id', value: { stringValue: 'test-session' } }
          ],
          events: events.map((e, idx) => ({
            name: e.name,
            timeUnixNano: e.timeUnixNano || `169765440${idx}000000000`,
            attributes: e.attributes ? e.attributes.map(attr => 
              typeof attr === 'object' && attr.key ? attr : { key: attr, value: { stringValue: e.attributes[attr] } }
            ) : []
          }))
        }]
      }]
    }]
  };
}

function createMockTraceWithoutEvents() {
  return {
    resourceSpans: [{
      scopeSpans: [{
        scope: { name: 'test.scope' },
        spans: [{
          name: 'test.span',
          startTimeUnixNano: '1697654400000000000',
          endTimeUnixNano: '1697654402000000000',
          attributes: [
            { key: 'honeyhive.session_id', value: { stringValue: 'test-session' } }
          ],
          events: []  // No events
        }]
      }]
    }]
  };
}
```

---

## Integration Test

**File:** `tests/integration/span_events.test.js` (create new)

```javascript
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

describe('Span Events Integration', () => {
  it('should ingest and store span events from OTLP', async () => {
    const sessionId = uuidv4();
    const eventId = uuidv4();
    
    // Send OTLP trace with events
    const otlpPayload = createOTLPTraceWithEvents(sessionId, eventId);
    
    const response = await axios.post(
      'http://localhost:3000/opentelemetry/v1/traces',
      otlpPayload,
      {
        headers: {
          'Content-Type': 'application/x-protobuf',
          'Authorization': `Bearer ${process.env.TEST_API_KEY}`,
          'x-honeyhive': 'project:test-project'
        }
      }
    );
    
    expect(response.status).toBe(200);
    
    // Wait for processing
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Query ClickHouse to verify events stored
    const storedEvent = await getEventFromClickHouse(eventId);
    
    expect(storedEvent).toBeDefined();
    expect(storedEvent.span_events).toBeDefined();
    expect(storedEvent.span_events.length).toBeGreaterThan(0);
    expect(storedEvent.span_events[0].name).toBe('gen_ai.user.message');
  });
});
```

---

## Database Schema (No changes needed!)

**Good news:** The events table already stores `request_json` as a JSON blob, so `span_events` can be added without schema migration.

**Verification:**
```javascript
// In app/utils/clickhouse_queries.js:
const query = `SELECT request_json FROM ${clickHouseEventTableName} WHERE ...`;
```

The `request_json` column contains the entire event object, so adding `span_events` is just adding a new field to that JSON.

---

## Rollout Plan

### Phase 1: Backend Only (Safe)
1. Deploy code changes to staging
2. Test with mock traces
3. Verify `span_events` appears in ClickHouse
4. Deploy to production
5. Monitor performance

**Risk:** Low - purely additive

---

### Phase 2: Strands Integration Test
1. Set up test Strands agent
2. Send traces to HoneyHive staging
3. Verify events captured
4. Verify inputs/outputs populated
5. Document any issues

**Risk:** Medium - may reveal edge cases

---

### Phase 3: UI Updates (Future)
1. Update trace viewer to display events
2. Add event timeline visualization
3. Add event filtering
4. Deploy incrementally

**Risk:** Low - UI only

---

## Performance Considerations

### Expected Impact
- **Event parsing:** +5-10ms per span with events
- **Storage:** +10-50% per trace (depends on event count)
- **Query performance:** Minimal (JSON field)

### Monitoring
- Track `parseTrace()` latency
- Track ClickHouse write latency
- Track `request_json` size growth
- Alert if >100 events per span

### Optimization (if needed)
- Add event sampling (keep first/last N events)
- Add event size limits (max 1KB per event)
- Add event filtering (skip noisy events)

---

## Success Metrics

### Must Track
- [ ] Percentage of spans with events
- [ ] Average events per span
- [ ] Parse latency p50/p95/p99
- [ ] Storage growth rate

### Must Validate
- [ ] AWS Strands traces complete
- [ ] GenAI message events captured
- [ ] No increase in errors
- [ ] Latency within acceptable range (<10% increase)

---

## Troubleshooting

### Issue: Events not appearing in stored data

**Check:**
1. Is `span.events` defined in protobuf payload?
2. Is `span.events` being accessed in `parseTrace()`?
3. Is `spanEvents` added to event object?
4. Is `request_json` being stringified correctly?

**Debug:**
```javascript
// Add logging in parseTrace()
console.log('Span events count:', span.events?.length || 0);
console.log('Parsed span events:', spanEvents);
```

---

### Issue: Performance degradation

**Check:**
1. How many events per span?
2. How large are event attributes?
3. Is parsing blocking the main thread?

**Fix:**
```javascript
// Add event sampling
const MAX_EVENTS_PER_SPAN = 100;
if (span.events.length > MAX_EVENTS_PER_SPAN) {
  console.warn(`Span has ${span.events.length} events, sampling to ${MAX_EVENTS_PER_SPAN}`);
  span.events = span.events.slice(0, MAX_EVENTS_PER_SPAN);
}
```

---

### Issue: GenAI enrichment conflicts with existing data

**Check:**
1. Are inputs/outputs already populated from attributes?
2. Do events and attributes both contain message data?

**Fix:**
```javascript
// Make enrichment conditional
if (!inputs.messages || inputs.messages.length === 0) {
  enrichFromGenAIEvents(spanEvents, inputs, outputs);
}
```

---

## Quick Reference: Event Structure

### Span.Event (Protobuf)
```typescript
interface SpanEvent {
  timeUnixNano: number;      // Nanoseconds since epoch
  name: string;              // Event name (e.g., "gen_ai.user.message")
  attributes: KeyValue[];    // Event-specific attributes
  droppedAttributesCount: number;
}
```

### Parsed Event (HoneyHive)
```typescript
interface ParsedSpanEvent {
  name: string;
  timestamp: number;
  attributes: Record<string, any>;
}
```

### GenAI Event Names (Old Convention)
- `gen_ai.user.message` - User input
- `gen_ai.choice` - Assistant response
- `gen_ai.tool.message` - Tool call

### GenAI Event Names (New Convention)
- `gen_ai.client.inference.operation.details` - Unified operation event

---

## Contacts

- **Code Owner:** TBD
- **Reviewer:** TBD
- **Integration Testing:** TBD
- **Documentation:** TBD

---

**Last Updated:** October 15, 2025  
**Status:** Ready for implementation  
**Estimated Effort:** 1-2 days (backend only)


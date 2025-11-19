# HoneyHive Span Events Gap: Executive Summary
**Date:** October 15, 2025  
**Severity:** 🔴 **CRITICAL**

---

## The Problem in One Sentence

**HoneyHive drops all OpenTelemetry span events at the ingestion layer, making it incompatible with OTel-native GenAI frameworks like AWS Strands that rely on events for message-level tracing.**

---

## Visual: What's Being Lost

```
┌─────────────────────────────────────────────────────────────┐
│ AWS Strands SDK Sends                                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Span: "agent.run"                                           │
│  ├─ Attributes: ✅ CAPTURED                                  │
│  │  ├─ gen_ai.request.model: "gpt-4"                        │
│  │  ├─ gen_ai.usage.input_tokens: 150                       │
│  │  └─ gen_ai.usage.output_tokens: 80                       │
│  │                                                            │
│  └─ Events: ❌ DROPPED BY HONEYHIVE                          │
│     ├─ T+0ms: gen_ai.user.message                           │
│     │   └─ content: "What's the weather in SF?"             │
│     ├─ T+1200ms: gen_ai.tool.message                        │
│     │   └─ tool: get_weather(city="SF")                     │
│     └─ T+2400ms: gen_ai.choice                              │
│         └─ message: "The weather is sunny"                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ HoneyHive Stores                                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  {                                                            │
│    "event_name": "agent.run",                                │
│    "event_type": "model",                                    │
│    "config": { "model": "gpt-4" },                           │
│    "metrics": {                                              │
│      "input_tokens": 150,                                    │
│      "output_tokens": 80                                     │
│    },                                                         │
│    "inputs": {},        ← EMPTY! Message lost                │
│    "outputs": {}        ← EMPTY! Response lost               │
│  }                                                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Impact

### For AWS Strands Users
- ❌ Cannot see conversation messages
- ❌ Cannot see tool invocations
- ❌ Cannot reconstruct agent reasoning
- ❌ GenAI semantic conventions incomplete
- ⚠️ Tracing appears "broken"

### For HoneyHive
- ❌ Not truly OTel-compliant
- ❌ BYOI architecture compromised
- ❌ Incompatible with modern GenAI frameworks
- ⚠️ Competitive disadvantage vs DataDog, Honeycomb, etc.

---

## Root Cause

### Evidence from Code

**File:** `hive-kube/kubernetes/ingestion_service/app/services/otel_processing_service.js`

```javascript
// Line 38-49: The parseTrace() function
scopeSpan.spans.forEach((span) => {
  // ✅ Attributes processed
  span.attributes.forEach((attribute) => {
    parsedAttributes[attribute.key] = parseAnyValue(attribute.value);
  });
  
  // ❌ Events NEVER accessed (span.events is ignored)
  
  // Map span → HoneyHive event
  let event = {
    event_name: span.name,
    inputs: inputs,      // Extracted from attributes only
    outputs: outputs,    // Extracted from attributes only
    // ...
  };
});
```

**Grep Proof:**
```bash
$ grep -rn "span\.events" kubernetes/ingestion_service/
# No results found - events are never accessed!
```

**Protobuf Proof:**
```javascript
// File: app/utils/trace_pb.js, Line 994
Span.prototype.events = $util.emptyArray;  // ← Field exists in proto
Event.prototype.name = '';                  // ← Events are decoded
Event.prototype.attributes = $util.emptyArray;

// But never used in processing!
```

---

## The Fix (High-Level)

### 3 Layers Need Updates

```
┌────────────────────────────────────────────────────┐
│ Layer 1: Ingestion Service (Node.js)              │
├────────────────────────────────────────────────────┤
│ ✅ Parse span.events from protobuf                │
│ ✅ Extract GenAI message events                   │
│ ✅ Include in HoneyHive event object              │
└────────────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────┐
│ Layer 2: Storage (ClickHouse)                     │
├────────────────────────────────────────────────────┤
│ ✅ Add span_events column (JSON or separate table)│
│ ✅ Store event name, timestamp, attributes        │
└────────────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────┐
│ Layer 3: UI (Future)                              │
├────────────────────────────────────────────────────┤
│ ✅ Display events in trace timeline               │
│ ✅ Show message exchanges                         │
│ ✅ Enable event-based filtering                   │
└────────────────────────────────────────────────────┘
```

---

## Priority Actions

### Immediate (This Week)
1. ✅ **Confirm the gap** (DONE - this analysis)
2. ⏳ Review findings with engineering team
3. ⏳ Create implementation tickets
4. ⏳ Prioritize for next sprint

### Short-Term (Next Sprint)
5. ⏳ Update `parseTrace()` to extract `span.events`
6. ⏳ Add `span_events` field to HoneyHive event schema
7. ⏳ Store events in ClickHouse (add column to `request_json`)
8. ⏳ Test with AWS Strands SDK

### Medium-Term (2-3 Sprints)
9. ⏳ Add GenAI event enrichment (populate inputs/outputs from events)
10. ⏳ Update UI to display events
11. ⏳ Add span status support
12. ⏳ Add span links support

---

## Technical Specifications

### Minimal Code Change (Layer 1)

**File:** `app/services/otel_processing_service.js`

**Add after line 49:**
```javascript
// Parse span events
let spanEvents = [];
if (span.events && Array.isArray(span.events)) {
  span.events.forEach((event) => {
    let parsedEvent = {
      name: event.name,
      timestamp: parseInt(event.timeUnixNano),
      attributes: {}
    };
    
    if (event.attributes) {
      event.attributes.forEach((attr) => {
        parsedEvent.attributes[attr.key] = parseAnyValue(attr.value);
      });
    }
    
    spanEvents.push(parsedEvent);
  });
}

// Enrich with GenAI events
spanEvents.forEach((evt) => {
  if (evt.name === 'gen_ai.user.message') {
    inputs.messages = inputs.messages || [];
    inputs.messages.push({
      role: 'user',
      content: evt.attributes.content
    });
  } else if (evt.name === 'gen_ai.choice') {
    outputs.messages = outputs.messages || [];
    outputs.messages.push({
      role: 'assistant',
      content: evt.attributes.message,
      finish_reason: evt.attributes.finish_reason
    });
  }
});
```

**Add to event object (line 114):**
```javascript
let event = {
  // ... existing fields
  span_events: spanEvents,  // NEW
  // ...
};
```

### Storage Change (Layer 2)

**Option A: Embedded in request_json (Quick)**
```javascript
// No schema change needed!
// span_events is just added to the JSON blob
```

**Option B: Separate Table (Better)**
```sql
CREATE TABLE span_events (
    event_id UUID,
    event_name String,
    timestamp UInt64,
    attributes String,  -- JSON
    event_order UInt32,
    tenant String,
    INDEX idx_event_id event_id TYPE bloom_filter
) ENGINE = MergeTree()
ORDER BY (tenant, event_id, event_order);
```

---

## Testing Checklist

### Unit Tests
- [ ] Parse spans with events
- [ ] Parse spans without events
- [ ] Parse GenAI message events
- [ ] Parse GenAI tool events
- [ ] Parse GenAI choice events
- [ ] Handle malformed events gracefully

### Integration Tests
- [ ] Send Strands trace to HoneyHive
- [ ] Verify events stored in ClickHouse
- [ ] Verify inputs.messages populated
- [ ] Verify outputs.messages populated
- [ ] Verify event timeline correct

### Regression Tests
- [ ] Spans without events still work
- [ ] Existing traces unaffected
- [ ] Performance impact acceptable (<10% overhead)

---

## Success Criteria

### Must Have
- ✅ Span events ingested and stored
- ✅ GenAI message events extracted
- ✅ AWS Strands traces fully captured
- ✅ No breaking changes to existing traces

### Should Have
- ✅ Events displayed in UI
- ✅ Event-based filtering
- ✅ Documentation updated

### Nice to Have
- ✅ Event-based alerting
- ✅ Event-based metrics
- ✅ Event timeline visualization

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Schema migration fails | Low | High | Use additive-only changes (default `[]`) |
| Performance degradation | Medium | Medium | Benchmark with high event counts; add sampling |
| Breaking existing traces | Low | Critical | Extensive testing; gradual rollout |
| UI changes required | High | Low | Decouple backend from frontend changes |
| GenAI event conflicts | Medium | Medium | Make event enrichment optional initially |

**Overall Risk:** Low-Medium (mostly additive changes)

---

## Related Documents

1. **Detailed Analysis**  
   [`INGESTION_SERVICE_SPAN_EVENTS_ANALYSIS.md`](./INGESTION_SERVICE_SPAN_EVENTS_ANALYSIS.md)  
   Full technical analysis with code examples, schema proposals, and migration strategy.

2. **AWS Strands SDK Analysis**  
   [`AWS_STRANDS_SDK_ANALYSIS.md`](./AWS_STRANDS_SDK_ANALYSIS.md)  
   How Strands uses span events and what HoneyHive needs to support.

3. **OTel Span Data Types**  
   [`OTEL_SPAN_DATA_TYPES_ANALYSIS.md`](./OTEL_SPAN_DATA_TYPES_ANALYSIS.md)  
   Complete reference of OTel span capabilities (attributes, events, status, links).

4. **BYOI Architecture Context**  
   [`OTEL_SPAN_EVENTS_NEUTRAL_PROVIDER_ANALYSIS.md`](./OTEL_SPAN_EVENTS_NEUTRAL_PROVIDER_ANALYSIS.md)  
   Why span events are critical for HoneyHive's neutral provider positioning.

---

## Key Takeaways

### For Engineering
> **"We're dropping critical data from modern GenAI frameworks. The fix is straightforward: parse `span.events` the same way we parse `span.attributes`."**

### For Product
> **"AWS Strands users will see incomplete traces. We need this to support OTel-native frameworks and maintain our BYOI promise."**

### For Leadership
> **"This is a competitive gap. DataDog, Honeycomb, and others support span events. We need to catch up to remain relevant for GenAI observability."**

---

**Status:** 🔴 **BLOCKER for AWS Strands support**  
**Effort Estimate:** 2-3 sprints (backend + storage + UI)  
**Priority:** **P0** (blocks major customer segment)

---

**Next Step:** Present to engineering team and create implementation plan.


# Span Events Implementation - Final Approach
**Reusing Existing Attribute Mapper**  
**Date:** October 15, 2025

---

## Strategy: Flatten Events → Existing Attribute Mapper

Instead of duplicating semantic pattern logic, we **flatten span events into pseudo-attributes** and pass them through the existing `applyAttributeMappings()` function.

### Why This Is Better
- ✅ Zero code duplication
- ✅ Reuses all existing semantic patterns
- ✅ Consistent handling of attributes and events
- ✅ Automatic support for new patterns
- ✅ Simple ~50 line implementation

---

## Implementation

### Step 1: Add Event Flattening Function

**File:** `hive-kube/kubernetes/ingestion_service/app/utils/event_flattener.js` (new file)

```javascript
/**
 * Flatten span events into pseudo-attributes for processing by attribute mapper
 * 
 * Strategy:
 * - GenAI semantic convention events → transform to known attribute patterns
 * - Generic events → prefix with _event. and let semantic inference handle them
 * - Unknown events → fallback to metadata via semantic patterns
 */

const { parseAnyValue } = require('../services/otel_processing_service');

/**
 * Flatten span events into parsedAttributes object
 * @param {Array} events - Array of span events from protobuf
 * @param {Object} attributes - Existing parsed attributes object (mutated)
 */
function flattenEventsToAttributes(events, attributes) {
  if (!events || !Array.isArray(events) || events.length === 0) {
    return;
  }

  events.forEach((event, idx) => {
    const eventName = event.name;
    const timestamp = parseInt(event.timeUnixNano);
    
    // Parse event attributes
    const eventAttrs = {};
    if (event.attributes && Array.isArray(event.attributes)) {
      event.attributes.forEach((attr) => {
        eventAttrs[attr.key] = parseAnyValue(attr.value);
      });
    }

    // ========================================================================
    // TIER 1: GenAI Semantic Convention Events (Transform to Known Patterns)
    // ========================================================================
    
    if (eventName === 'gen_ai.user.message') {
      // Transform to llm.prompts format (Traceloop pattern)
      // Existing mapper knows: llm.prompts.N.role, llm.prompts.N.content
      
      const content = eventAttrs.content;
      if (content) {
        // Find next available prompt index
        const existingPrompts = Object.keys(attributes).filter(k => 
          k.match(/^llm\.prompts\.\d+\./)
        );
        const maxIndex = existingPrompts.reduce((max, key) => {
          const match = key.match(/^llm\.prompts\.(\d+)\./);
          return match ? Math.max(max, parseInt(match[1])) : max;
        }, -1);
        
        const promptIndex = maxIndex + 1;
        attributes[`llm.prompts.${promptIndex}.role`] = 'user';
        attributes[`llm.prompts.${promptIndex}.content`] = content;
        attributes[`llm.prompts.${promptIndex}._timestamp`] = timestamp;
        attributes[`llm.prompts.${promptIndex}._source`] = 'span_event';
      }
    }
    
    else if (eventName === 'gen_ai.choice') {
      // Transform to llm.completions format (Traceloop pattern)
      // Existing mapper knows: llm.completions.N.role, llm.completions.N.content, etc.
      
      const message = eventAttrs.message;
      const finishReason = eventAttrs.finish_reason;
      
      if (message) {
        const existingCompletions = Object.keys(attributes).filter(k => 
          k.match(/^llm\.completions\.\d+\./)
        );
        const maxIndex = existingCompletions.reduce((max, key) => {
          const match = key.match(/^llm\.completions\.(\d+)\./);
          return match ? Math.max(max, parseInt(match[1])) : max;
        }, -1);
        
        const completionIndex = maxIndex + 1;
        attributes[`llm.completions.${completionIndex}.role`] = 'assistant';
        attributes[`llm.completions.${completionIndex}.content`] = message;
        if (finishReason) {
          attributes[`llm.completions.${completionIndex}.finish_reason`] = finishReason;
        }
        attributes[`llm.completions.${completionIndex}._timestamp`] = timestamp;
        attributes[`llm.completions.${completionIndex}._source`] = 'span_event';
      }
    }
    
    else if (eventName === 'gen_ai.tool.message') {
      // Store tool calls with _event prefix
      // Semantic patterns will route to metadata.tool_calls
      
      const content = eventAttrs.content;
      const toolId = eventAttrs.id;
      const role = eventAttrs.role;
      
      if (content) {
        attributes[`_event.tool_call.${idx}.content`] = content;
        if (toolId) {
          attributes[`_event.tool_call.${idx}.id`] = toolId;
        }
        if (role) {
          attributes[`_event.tool_call.${idx}.role`] = role;
        }
        attributes[`_event.tool_call.${idx}._timestamp`] = timestamp;
      }
    }
    
    else if (eventName === 'gen_ai.client.inference.operation.details') {
      // New GenAI convention (v0.4.0+)
      // Extract input/output messages directly
      
      const inputMessages = eventAttrs['gen_ai.input.messages'];
      const outputMessages = eventAttrs['gen_ai.output.messages'];
      
      if (inputMessages) {
        attributes['_event.gen_ai.input.messages'] = inputMessages;
      }
      if (outputMessages) {
        attributes['_event.gen_ai.output.messages'] = outputMessages;
      }
    }
    
    // ========================================================================
    // TIER 2: OTel Standard Events
    // ========================================================================
    
    else if (eventName === 'exception') {
      // OTel exception events
      const exceptionType = eventAttrs['exception.type'];
      const exceptionMessage = eventAttrs['exception.message'];
      const stacktrace = eventAttrs['exception.stacktrace'];
      
      if (exceptionMessage) {
        attributes['_event.exception.message'] = exceptionMessage;
      }
      if (exceptionType) {
        attributes['_event.exception.type'] = exceptionType;
      }
      if (stacktrace) {
        attributes['_event.exception.stacktrace'] = stacktrace;
      }
      attributes['_event.exception._timestamp'] = timestamp;
    }
    
    // ========================================================================
    // TIER 3: Generic Events (Flatten with _event prefix)
    // ========================================================================
    
    else {
      // Flatten all event attributes with event name as prefix
      // Semantic inference in attribute mapper will route appropriately
      
      Object.entries(eventAttrs).forEach(([key, value]) => {
        // Use event name as prefix to maintain context
        const flattenedKey = `_event.${eventName}.${key}`;
        attributes[flattenedKey] = value;
      });
      
      // Store event metadata for debugging
      attributes[`_event.${eventName}._timestamp`] = timestamp;
      attributes[`_event.${eventName}._name`] = eventName;
    }
  });
  
  // Store event count for debugging
  if (events.length > 0) {
    attributes['_meta.event_count'] = events.length;
  }
}

module.exports = { flattenEventsToAttributes };
```

---

### Step 2: Integrate into `otel_processing_service.js`

**File:** `app/services/otel_processing_service.js`

**Add import at top:**
```javascript
const { flattenEventsToAttributes } = require('../utils/event_flattener.js');
```

**Modify `parseTrace()` function (around line 38-55):**

```javascript
scopeSpan.spans.forEach((span) => {
  let eventMetadata = { ...metadata };
  let eventName = span.name;
  span.startTimeUnixNano = parseInt(span.startTimeUnixNano);
  span.endTimeUnixNano = parseInt(span.endTimeUnixNano);
  
  let parsedAttributes = {};
  
  // EXISTING: Parse span attributes
  span.attributes.forEach((attribute) => {
    let attributeName = attribute.key;
    let attributeValue = parseAnyValue(attribute.value);
    parsedAttributes[attributeName] = attributeValue;
  });
  parsedAttributes = parseIndexedAttributes(parsedAttributes);

  // NEW: Flatten span events into pseudo-attributes
  if (span.events && Array.isArray(span.events)) {
    flattenEventsToAttributes(span.events, parsedAttributes);
  }

  // EXISTING: Detect instrumentor from attributes (now includes event data)
  const instrumentor = detectInstrumentorFromAttributes(parsedAttributes);

  // EXISTING: Apply 3-tier attribute mapping (now handles both attributes AND events)
  const { eventData, context } = applyAttributeMappings(parsedAttributes, instrumentor);
  
  // ... rest of existing code
});
```

**Modify `parseNextJSTrace()` function (around line 169-188):**

```javascript
scopeSpan.spans.forEach((span) => {
  // ... existing code ...
  
  let parsedAttributes = {};
  span.attributes.forEach((attribute) => {
    let attributeName = attribute.key;
    let attributeValue = parseAnyValue(attribute.value);
    parsedAttributes[attributeName] = attributeValue;
  });
  parsedAttributes = parseIndexedAttributes(parsedAttributes);

  // NEW: Flatten span events
  if (span.events && Array.isArray(span.events)) {
    flattenEventsToAttributes(span.events, parsedAttributes);
  }

  // ... rest of existing code (attribute processing)
});
```

---

### Step 3: Extend Semantic Patterns (Optional but Recommended)

**File:** `app/config/semantic_patterns.ts`

**Add to `SEMANTIC_PATTERNS` array (around line 398, before broad fallback patterns):**

```typescript
// ========================================================================
// SPAN EVENT PATTERNS (Medium-High Priority)
// ========================================================================

{
  pattern: /^_event\..*\.(user_message|user_input|user_query|prompt|input)\b/i,
  target: 'inputs',
  priority: 92,
  description: 'User input from span events (semantic inference)'
},
{
  pattern: /^_event\..*\.(assistant_message|assistant_response|completion|response|output)\b/i,
  target: 'outputs',
  priority: 92,
  description: 'Assistant response from span events (semantic inference)'
},
{
  pattern: /^_event\.tool_call\./i,
  target: 'metadata',
  priority: 95,
  description: 'Tool calls from span events'
},
{
  pattern: /^_event\.exception\./i,
  target: 'metadata',
  priority: 98,
  description: 'Exception events from OTel'
},
{
  pattern: /^_event\.gen_ai\.input\.messages/i,
  target: 'inputs',
  priority: 98,
  description: 'GenAI input messages from unified event (new convention)'
},
{
  pattern: /^_event\.gen_ai\.output\.messages/i,
  target: 'outputs',
  priority: 98,
  description: 'GenAI output messages from unified event (new convention)'
},
{
  pattern: /^_event\./i,
  target: 'metadata',
  priority: 50,
  description: 'Generic span events (fallback to metadata)'
},
{
  pattern: /^_meta\./i,
  target: 'metadata',
  priority: 40,
  description: 'Event metadata (counts, etc.)'
}
```

---

### Step 4: Export `parseAnyValue` for Reuse

**File:** `app/services/otel_processing_service.js`

**Add to module.exports (at bottom):**

```javascript
module.exports = {
  processNextJSTrace,
  processOTELTraces,
  parseAnyValue,  // NEW: Export for use in event_flattener
};
```

---

## How It Works

### Example 1: AWS Strands GenAI Events

**Input (OTel Span):**
```javascript
{
  name: "agent.run",
  attributes: [
    { key: "gen_ai.request.model", value: "gpt-4" },
    { key: "gen_ai.usage.input_tokens", value: 150 }
  ],
  events: [
    {
      name: "gen_ai.user.message",
      attributes: [{ key: "content", value: '{"text": "What is the weather?"}' }]
    },
    {
      name: "gen_ai.choice",
      attributes: [
        { key: "message", value: '{"text": "The weather is sunny"}' },
        { key: "finish_reason", value: "stop" }
      ]
    }
  ]
}
```

**After Flattening:**
```javascript
parsedAttributes = {
  "gen_ai.request.model": "gpt-4",
  "gen_ai.usage.input_tokens": 150,
  
  // Events flattened to Traceloop format
  "llm.prompts.0.role": "user",
  "llm.prompts.0.content": '{"text": "What is the weather?"}',
  "llm.prompts.0._source": "span_event",
  
  "llm.completions.0.role": "assistant",
  "llm.completions.0.content": '{"text": "The weather is sunny"}',
  "llm.completions.0.finish_reason": "stop",
  "llm.completions.0._source": "span_event"
}
```

**After Attribute Mapping:**
```javascript
eventData = {
  config: { model: "gpt-4" },
  inputs: {
    chat_history: [
      { role: "user", content: {"text": "What is the weather?"} }
    ]
  },
  outputs: {
    role: "assistant",
    content: {"text": "The weather is sunny"},
    finish_reason: "stop"
  },
  metrics: { input_tokens: 150 },
  metadata: {}
}
```

**✅ Works perfectly with existing Traceloop handler!**

---

### Example 2: Custom Framework Events

**Input (Unknown Framework):**
```javascript
{
  name: "my_agent.execute",
  attributes: [
    { key: "agent.name", value: "weather_bot" }
  ],
  events: [
    {
      name: "my_agent.user_input",
      attributes: [{ key: "text", value: "What's the weather?" }]
    },
    {
      name: "my_agent.bot_response",
      attributes: [{ key: "text", value: "It's sunny!" }]
    }
  ]
}
```

**After Flattening:**
```javascript
parsedAttributes = {
  "agent.name": "weather_bot",
  
  // Events with _event prefix
  "_event.my_agent.user_input.text": "What's the weather?",
  "_event.my_agent.user_input._timestamp": 1697654400000000000,
  "_event.my_agent.user_input._name": "my_agent.user_input",
  
  "_event.my_agent.bot_response.text": "It's sunny!",
  "_event.my_agent.bot_response._timestamp": 1697654401000000000,
  "_event.my_agent.bot_response._name": "my_agent.bot_response"
}
```

**After Semantic Inference:**
```javascript
// Pattern: /^_event\..*\.(user_input|input)\b/i → inputs
// Pattern: /^_event\..*\.(bot_response|response)\b/i → outputs

eventData = {
  config: { name: "weather_bot" },
  inputs: {
    "my_agent.user_input.text": "What's the weather?"
  },
  outputs: {
    "my_agent.bot_response.text": "It's sunny!"
  },
  metadata: {
    "_event.my_agent.user_input._timestamp": 1697654400000000000,
    "_event.my_agent.bot_response._timestamp": 1697654401000000000
  }
}
```

**✅ Semantic inference routes to correct buckets!**

---

### Example 3: Unknown Events (Fallback)

**Input:**
```javascript
{
  events: [
    {
      name: "custom.checkpoint.validation_complete",
      attributes: [
        { key: "status", value: "passed" },
        { key: "duration_ms", value: 123 }
      ]
    }
  ]
}
```

**After Flattening:**
```javascript
parsedAttributes = {
  "_event.custom.checkpoint.validation_complete.status": "passed",
  "_event.custom.checkpoint.validation_complete.duration_ms": 123,
  "_event.custom.checkpoint.validation_complete._timestamp": 1697654400000000000
}
```

**After Semantic Inference:**
```javascript
// Pattern: /^_event\./i → metadata (fallback pattern)

eventData = {
  metadata: {
    "_event.custom.checkpoint.validation_complete.status": "passed",
    "_event.custom.checkpoint.validation_complete.duration_ms": 123,
    "_event.custom.checkpoint.validation_complete._timestamp": 1697654400000000000
  }
}
```

**✅ Unknown events preserved in metadata!**

---

## Testing Strategy

### Unit Tests

**File:** `tests/unit/utils/event_flattener.test.js` (new)

```javascript
const { flattenEventsToAttributes } = require('../../../app/utils/event_flattener');

describe('Event Flattener', () => {
  describe('GenAI Events', () => {
    it('should flatten gen_ai.user.message to llm.prompts format', () => {
      const events = [{
        name: 'gen_ai.user.message',
        timeUnixNano: '1697654400000000000',
        attributes: [
          { key: 'content', value: { stringValue: '{"text": "Hello"}' } }
        ]
      }];
      
      const attributes = {};
      flattenEventsToAttributes(events, attributes);
      
      expect(attributes['llm.prompts.0.role']).toBe('user');
      expect(attributes['llm.prompts.0.content']).toBe('{"text": "Hello"}');
      expect(attributes['llm.prompts.0._source']).toBe('span_event');
    });
    
    it('should flatten gen_ai.choice to llm.completions format', () => {
      const events = [{
        name: 'gen_ai.choice',
        timeUnixNano: '1697654401000000000',
        attributes: [
          { key: 'message', value: { stringValue: '{"text": "Hi"}' } },
          { key: 'finish_reason', value: { stringValue: 'stop' } }
        ]
      }];
      
      const attributes = {};
      flattenEventsToAttributes(events, attributes);
      
      expect(attributes['llm.completions.0.role']).toBe('assistant');
      expect(attributes['llm.completions.0.content']).toBe('{"text": "Hi"}');
      expect(attributes['llm.completions.0.finish_reason']).toBe('stop');
    });
    
    it('should handle multiple messages in sequence', () => {
      const events = [
        {
          name: 'gen_ai.user.message',
          timeUnixNano: '1697654400000000000',
          attributes: [{ key: 'content', value: { stringValue: 'Message 1' } }]
        },
        {
          name: 'gen_ai.choice',
          timeUnixNano: '1697654401000000000',
          attributes: [{ key: 'message', value: { stringValue: 'Response 1' } }]
        },
        {
          name: 'gen_ai.user.message',
          timeUnixNano: '1697654402000000000',
          attributes: [{ key: 'content', value: { stringValue: 'Message 2' } }]
        }
      ];
      
      const attributes = {};
      flattenEventsToAttributes(events, attributes);
      
      expect(attributes['llm.prompts.0.content']).toBe('Message 1');
      expect(attributes['llm.prompts.1.content']).toBe('Message 2');
      expect(attributes['llm.completions.0.content']).toBe('Response 1');
    });
  });
  
  describe('Generic Events', () => {
    it('should flatten unknown events with _event prefix', () => {
      const events = [{
        name: 'custom.checkpoint',
        timeUnixNano: '1697654400000000000',
        attributes: [
          { key: 'status', value: { stringValue: 'passed' } },
          { key: 'duration', value: { intValue: 123 } }
        ]
      }];
      
      const attributes = {};
      flattenEventsToAttributes(events, attributes);
      
      expect(attributes['_event.custom.checkpoint.status']).toBe('passed');
      expect(attributes['_event.custom.checkpoint.duration']).toBe(123);
      expect(attributes['_event.custom.checkpoint._timestamp']).toBe(1697654400000000000);
    });
  });
  
  describe('Exception Events', () => {
    it('should flatten exception events', () => {
      const events = [{
        name: 'exception',
        timeUnixNano: '1697654400000000000',
        attributes: [
          { key: 'exception.type', value: { stringValue: 'ValueError' } },
          { key: 'exception.message', value: { stringValue: 'Invalid input' } }
        ]
      }];
      
      const attributes = {};
      flattenEventsToAttributes(events, attributes);
      
      expect(attributes['_event.exception.type']).toBe('ValueError');
      expect(attributes['_event.exception.message']).toBe('Invalid input');
    });
  });
});
```

### Integration Test

**File:** `tests/integration/span_events.test.js`

```javascript
const { parseTrace } = require('../../app/services/otel_processing_service');

describe('Span Events Integration', () => {
  it('should process AWS Strands trace with GenAI events', () => {
    const trace = {
      resourceSpans: [{
        scopeSpans: [{
          scope: { name: 'strands.telemetry' },
          spans: [{
            name: 'agent.run',
            startTimeUnixNano: '1697654400000000000',
            endTimeUnixNano: '1697654402000000000',
            attributes: [
              { key: 'honeyhive.session_id', value: { stringValue: 'test-session' } },
              { key: 'gen_ai.request.model', value: { stringValue: 'gpt-4' } },
              { key: 'gen_ai.usage.input_tokens', value: { intValue: 150 } }
            ],
            events: [
              {
                name: 'gen_ai.user.message',
                timeUnixNano: '1697654400500000000',
                attributes: [
                  { key: 'content', value: { stringValue: '[{"text": "What is the weather?"}]' } }
                ]
              },
              {
                name: 'gen_ai.choice',
                timeUnixNano: '1697654401500000000',
                attributes: [
                  { key: 'message', value: { stringValue: '[{"text": "The weather is sunny"}]' } },
                  { key: 'finish_reason', value: { stringValue: 'stop' } }
                ]
              }
            ]
          }]
        }]
      }]
    };
    
    const events = parseTrace(trace);
    
    expect(events).toHaveLength(1);
    expect(events[0].event_name).toBe('agent.run');
    expect(events[0].config.model).toBe('gpt-4');
    
    // Check that events were processed
    expect(events[0].inputs.chat_history).toBeDefined();
    expect(events[0].inputs.chat_history.length).toBeGreaterThan(0);
    
    expect(events[0].outputs.content).toBeDefined();
    expect(events[0].outputs.finish_reason).toBe('stop');
  });
});
```

---

## Migration & Rollout

### Phase 1: Deploy Event Flattening (Non-Breaking)
1. Add `event_flattener.js`
2. Integrate into `otel_processing_service.js`
3. Deploy to staging
4. Test with Strands SDK
5. Deploy to production

**Risk:** Very low - purely additive, existing traces unaffected

### Phase 2: Add Semantic Patterns (Enhancement)
1. Add `_event.*` patterns to `semantic_patterns.ts`
2. Test with custom framework events
3. Deploy incrementally

**Risk:** Low - improves handling of unknown events

### Phase 3: Monitor & Iterate
1. Track event processing metrics
2. Add patterns for common frameworks
3. Optimize performance if needed

---

## Benefits Summary

| Aspect | This Approach | Duplicate Logic Approach |
|--------|---------------|--------------------------|
| **Code Size** | +50 lines | +500 lines |
| **Maintenance** | Single mapping system | Two systems to maintain |
| **Consistency** | Attributes = Events | Potential divergence |
| **Extensibility** | Automatic (add patterns once) | Manual (update both) |
| **Testing** | Reuse attribute tests | Duplicate tests needed |
| **Risk** | Very low (reuses proven code) | Medium (new logic paths) |

---

## Next Steps

1. ✅ Review this approach with team
2. ⏳ Implement `event_flattener.js`
3. ⏳ Integrate into `otel_processing_service.js`
4. ⏳ Add semantic patterns for `_event.*`
5. ⏳ Write unit tests
6. ⏳ Test with AWS Strands SDK
7. ⏳ Deploy to staging
8. ⏳ Deploy to production

---

**Key Insight:** By treating events as "just more attributes with special names," we leverage all existing infrastructure while maintaining flexibility for any OTel-compliant framework. This is the elegant, maintainable solution.


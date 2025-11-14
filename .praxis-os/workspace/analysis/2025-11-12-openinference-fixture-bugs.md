# OpenInference Fixture Bugs - Customer Report Analysis

**Date:** 2025-11-12
**Status:** 🔴 **CRITICAL** - Input/Output mapping broken for OpenInference spans

---

## Customer Report

"input/output is not working correctly" for OpenInference Google ADK traces.

---

## Root Cause Analysis

### Issue 1: Output Parsing Not Implemented ❌

**What OpenInference Sends:**
```json
"output.value": "{\"content\":{\"parts\":[{\"text\":\"AI is...\"}],\"role\":\"model\"},\"finish_reason\":\"STOP\",...}"
```

**What Ingestion Needs To Do:**
1. Parse JSON string
2. Extract `content.parts[0].text` 
3. Map `role: "model"` → `role: "assistant"`  
4. Return structured output

**What Current Fixtures Expect:**
```json
"outputs": {
  "role": "assistant",
  "content": "AI is..."
}
```

**The Problem:** Ingestion service doesn't parse Google ADK's Gemini response format!

---

### Issue 2: Input Parsing For Agent/Tool Spans ❌

#### Agent Spans
**Actual Data:**
- NO `input.value` attribute
- Only has `gen_ai.agent.name`, `gen_ai.operation.name`, `output.value`

**Current Fixture:** `"inputs": {}`  ✅ **CORRECT** (agents don't have explicit inputs in ADK)

#### Tool Spans  
**Actual Data:**
```json
"input.value": "{\"city\": \"New York\"}"
"output.value": "{\"id\":\"...\",\"name\":\"get_weather\",\"response\":{...}}"
```

**Current Fixture:**
```json
"inputs": {
  "chat_history": [           // ❌ WRONG! Not a chat message!
    {
      "role": "user",
      "content": "{\"city\": \"New York\"}"
    }
  ]
}
```

**Should Be:**
```json
"inputs": {
  "city": "New York"  // ✅ Direct tool arguments
}
```

---

### Issue 3: LLM Input Message Parsing Complexity ⚠️

**What OpenInference Sends:**
```json
"llm.input_messages.0.message.role": "system",
"llm.input_messages.0.message.content": "You are...",
"llm.input_messages.1.message.role": "user",
"llm.input_messages.1.message.contents.0.message_content.text": "Tell me...",
"llm.input_messages.1.message.contents.0.message_content.type": "text"
```

**Complexity:**
- System message: Simple `content` field
- User message: Nested `contents[].message_content.text` structure
- Multiple content parts per message

**Current Parsing:** May not handle the nested `contents[]` array correctly.

---

## What Ingestion Service Needs

### 1. Parse `output.value` for Gemini Responses

**Gemini Response Structure:**
```json
{
  "content": {
    "parts": [{"text": "..."}],
    "role": "model"
  },
  "finish_reason": "STOP",
  "usage_metadata": {
    "candidates_token_count": 43,
    "prompt_token_count": 63,
    "total_token_count": 106
  },
  "avg_logprobs": -0.046
}
```

**Required Mapping:**
```typescript
// Parse output.value JSON
const parsed = JSON.parse(attributes['output.value']);

// Extract text content
outputs.content = parsed.content?.parts?.[0]?.text || '';
outputs.role = parsed.content?.role === 'model' ? 'assistant' : parsed.content?.role;

// Extract metrics from usage_metadata
metrics.prompt_tokens = parsed.usage_metadata?.prompt_token_count;
metrics.completion_tokens = parsed.usage_metadata?.candidates_token_count;
metrics.total_tokens = parsed.usage_metadata?.total_token_count;

// Extract metadata
metadata.finish_reason = parsed.finish_reason;
metadata.avg_logprobs = parsed.avg_logprobs;
```

---

### 2. Parse `llm.input_messages.*` Correctly

**Handle Two Content Formats:**

**Format A: Simple Content (system messages)**
```json
"llm.input_messages.0.message.role": "system",
"llm.input_messages.0.message.content": "You are..."
```

**Format B: Contents Array (user messages)**
```json
"llm.input_messages.1.message.role": "user",
"llm.input_messages.1.message.contents.0.message_content.text": "Tell me...",
"llm.input_messages.1.message.contents.0.message_content.type": "text"
```

**Required Logic:**
```typescript
function parseLLMInputMessages(attributes) {
  const messages = [];
  let i = 0;
  
  while (attributes[`llm.input_messages.${i}.message.role`]) {
    const role = attributes[`llm.input_messages.${i}.message.role`];
    
    // Try simple content first
    let content = attributes[`llm.input_messages.${i}.message.content`];
    
    // If not found, parse contents array
    if (!content) {
      const contentParts = [];
      let j = 0;
      while (attributes[`llm.input_messages.${i}.message.contents.${j}.message_content.text`]) {
        contentParts.push(
          attributes[`llm.input_messages.${i}.message.contents.${j}.message_content.text`]
        );
        j++;
      }
      content = contentParts.join(' ');
    }
    
    messages.push({ role, content });
    i++;
  }
  
  return messages;
}
```

---

### 3. Fix Tool Input Parsing

**Current:** Wraps tool args in chat_history ❌
**Should:** Parse `input.value` JSON directly as inputs ✅

```typescript
// For TOOL spans
if (spanKind === 'TOOL' && attributes['input.value']) {
  try {
    const parsed = JSON.parse(attributes['input.value']);
    inputs = parsed;  // Direct assignment, not wrapped!
  } catch (e) {
    inputs = { raw: attributes['input.value'] };
  }
}
```

---

## Fixture Corrections Needed

### Fix 1: Agent Fixture Output Parsing
**File:** `openinference_google_adk_unknown_agent_001.json`

**Current (WRONG):**
```json
"outputs": {
  "role": "assistant",
  "content": "Artificial intelligence (AI) is..."
}
```

**Should Be (matches parsed output.value):**
```json
"outputs": {
  "role": "assistant",  // parsed from content.role="model"
  "content": "Artificial intelligence (AI) is..."  // parsed from content.parts[0].text
}
```

**Also Add Metrics (from usage_metadata):**
```json
"metadata": {
  ...
  "prompt_tokens": 63,
  "completion_tokens": 45,
  "total_tokens": 108,
  "avg_logprobs": -0.11237772835625542
}
```

---

### Fix 2: Tool Fixture Input Format
**File:** `openinference_google_adk_unknown_tool_001.json`

**Current (WRONG):**
```json
"inputs": {
  "chat_history": [
    {
      "role": "user",
      "content": "{\"city\": \"New York\"}"
    }
  ]
}
```

**Should Be:**
```json
"inputs": {
  "city": "New York"  // Direct tool arguments!
}
```

---

### Fix 3: LLM Fixture Message Parsing
**File:** `openinference_google_adk_gemini_chat_007.json`

**Verify** that chat_history correctly handles:
1. System message with simple `content`
2. User messages with `contents[].message_content.text`  
3. Multiple content parts per message

---

## Action Plan

### Phase 1: Hive-Kube Ingestion Service Changes ⚠️

**Priority:** HIGH - Customer-blocking issue

**Required Changes:**
1. Add Gemini response parser for `output.value`
2. Fix `llm.input_messages.*` parser to handle `contents[]` array
3. Fix tool input parsing (don't wrap in chat_history)
4. Add unit tests for each parser

**Estimated Effort:** 2-3 hours

---

### Phase 2: Fixture Updates ✅

**Priority:** HIGH - Must match ingestion reality

**Required Changes:**
1. Update all 7 OpenInference fixtures
2. Add metrics extraction from `usage_metadata`
3. Fix tool input format
4. Add test cases for edge cases

**Estimated Effort:** 1 hour

---

### Phase 3: Validation ✅

1. Run fixture tests against updated ingestion service
2. Test with actual Google ADK spans from customer
3. Verify all span types (agent, tool, chain, LLM)

---

## Files Affected

### Hive-Kube (Ingestion Service)
- `kubernetes/ingestion_service/app/utils/attribute_router.ts`
- `kubernetes/ingestion_service/app/services/otel_processing_service.js`

### Python-SDK (Fixtures)
- `tests/fixtures/instrumentor_spans/openinference_google_adk_*.json` (7 files)

---

## Customer Impact

**Current State:** ❌
- Inputs/outputs are empty or incorrect
- Metrics missing
- Tool calls not working
- Agent responses malformed

**After Fix:** ✅
- All inputs/outputs correctly parsed
- Token counts and metrics present
- Tool execution visible
- Agent traces complete

---

## Next Steps

1. **Hive-kube team**: Implement parsing logic
2. **Python-SDK team**: Update fixtures to match
3. **QA**: Test with customer's actual traces
4. **Deploy**: Roll out fix to production

**ETA:** Can be fixed in 1 day if prioritized.


# 🔴 CRITICAL: Google ADK Input Parsing Bug

**Date:** 2025-11-12
**Status:** Root cause identified - Ingestion service missing Google ADK format handler

---

## Root Cause

**The ingestion service does NOT parse Google ADK's `input.value` format for CHAIN spans!**

### Actual Google ADK Span Hierarchy

From customer span dump `google_adk_20251021_102126.json`:

**1. CHAIN Span** (`openinference.span.kind: "CHAIN"`):
```json
"input.value": "{
  \"user_id\": \"test_user\",
  \"session_id\": \"test_basic\",
  \"new_message\": {
    \"parts\": [{\"text\": \"Explain the concept...\"}],
    \"role\": \"user\"
  },
  \"state_delta\": null,
  \"run_config\": null
}"
```

**2. AGENT Span** (`openinference.span.kind: "AGENT"`):
- NO `input.value`
- Only has `output.value` with response

**3. LLM Span** (`openinference.span.kind: "LLM"`):
- Has indexed `llm.input_messages.*.message.*` attributes ✓
- Has indexed `llm.output_messages.*.message.*` attributes ✓

---

## The Bug

**File:** `/Users/josh/src/github.com/honeyhiveai/hive-kube/kubernetes/ingestion_service/app/utils/attribute_router.ts`
**Lines:** 1030-1070 (OpenInference `input.value` parsing)

### Current Parsing Logic

```typescript
case 'openinference':
  // Try 1: Look for inputData.messages array
  if (inputData.messages && Array.isArray(inputData.messages)) {
    // ❌ Google ADK has `new_message`, not `messages`
    consumedKeys.add('input.value');
    inputs.chat_history = inputData.messages.map(...);
  }
  
  // Try 2: Look for indexed llm.input_messages.*
  if (!inputs.chat_history) {
    const indexedResult = extractFromIndexedMessages(attributes);
    // ✓ Works for LLM spans
    // ❌ CHAIN/AGENT spans don't have this
  }
  
  // Try 3: Plain string fallback
  if (!inputs.chat_history && attributes['input.value']) {
    if (typeof inputValue === 'string' && inputValue.trim()) {
      // ❌ Google ADK sends structured JSON, not plain string
      inputs.chat_history = [{role: 'user', content: inputValue}];
    }
  }
```

**Result:** Google ADK CHAIN span inputs are silently ignored!

---

## Required Fix

Add Google ADK format handler after line 1042:

```typescript
// NEW: Google ADK format: {new_message: {parts: [...], role: "user"}}
if (!inputs.chat_history && inputData.new_message && inputData.new_message.parts) {
  consumedKeys.add('input.value');
  const parts = inputData.new_message.parts;
  const text = parts.map((p: any) => p.text || '').filter(Boolean).join('');
  inputs.chat_history = [{
    role: inputData.new_message.role || 'user',
    content: text
  }];
}
```

---

## Impact

### Before Fix ❌
- **CHAIN spans**: No inputs extracted → user queries lost
- **AGENT spans**: Correctly empty (no inputs expected)
- **LLM spans**: Correctly parsed via indexed messages

### After Fix ✅
- **CHAIN spans**: User query extracted from `new_message.parts[].text`
- **AGENT spans**: Still correctly empty
- **LLM spans**: Still correctly parsed

---

## Fixture Status

### Agent Fixture ✅ CORRECT
**File:** `openinference_google_adk_unknown_agent_001.json`
- `expected.inputs: {}` matches reality (agent spans have no inputs)

### Tool Fixture ❌ WRONG
**File:** `openinference_google_adk_unknown_tool_001.json`
- Has `chat_history` with tool args
- Should have direct tool arguments in `inputs`

### LLM Fixture ✅ CORRECT
**File:** `openinference_google_adk_gemini_chat_007.json`
- Uses indexed messages properly

---

## Action Items

### 1. Hive-Kube Ingestion Service (CRITICAL)
**File:** `attribute_router.ts` line ~1043
**Change:** Add Google ADK `new_message` format handler
**Test:** Verify CHAIN span inputs are extracted

### 2. Python-SDK Fixtures (HIGH)
**File:** `openinference_google_adk_unknown_tool_001.json`
**Change:** Remove fake `chat_history`, use direct tool arguments
**Test:** Verify fixture passes after ingestion fix

### 3. Add CHAIN Span Fixture (MEDIUM)
**New file:** `openinference_google_adk_chain_invocation_001.json`
**Purpose:** Test the new Google ADK `new_message` parsing
**Data:** Use actual CHAIN span from customer dump

---

## Testing

```bash
# 1. Update ingestion service
cd ~/src/github.com/honeyhiveai/hive-kube/kubernetes/ingestion_service
# Edit app/utils/attribute_router.ts (add Google ADK handler)

# 2. Run ingestion tests
npm test

# 3. Validate with customer span
node scripts/test-span.js < ../../python-sdk/examples/integrations/span_dumps/google_adk_20251021_102126.json
```

---

## Timeline

- **Discovery:** 2025-11-12 (today)
- **Fix Complexity:** LOW (10-line change)
- **Testing:** MEDIUM (need to verify all span types)
- **ETA:** Can ship same day if prioritized

---

## Why This Wasn't Caught Earlier

1. **Fixtures were created manually** without running against real ingestion service
2. **No CHAIN span fixture** to test top-level invocation inputs
3. **LLM spans worked** (they use different attribute format), masking the bug
4. **Agent spans have no inputs** (expected behavior), didn't reveal the issue


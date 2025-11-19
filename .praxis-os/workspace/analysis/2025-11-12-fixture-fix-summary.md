# OpenInference Google ADK Fixture Fix Summary

**Date:** 2025-11-12  
**Status:** ✅ Tool fixture corrected

---

## What Was Fixed

### Tool Fixture - `openinference_google_adk_unknown_tool_001.json`

**Before (WRONG):**
```json
"inputs": {
  "chat_history": [    // ❌ Tool arguments wrapped as fake chat message
    {
      "role": "user",
      "content": "{\"city\": \"New York\"}"
    }
  ]
}
```

**After (CORRECT):**
```json
"inputs": {
  "city": "New York"  // ✅ Direct tool arguments
}
```

**Output format also fixed:**
- Changed from `role/content` to `message` (tool outputs don't have roles)

---

## Critical Finding: Ingestion Service Gap

### Current State ❌

The ingestion service **does NOT extract tool inputs** from OpenInference spans!

**What happens to these attributes:**
```json
"input.value": "{\"city\": \"New York\"}",
"tool.parameters": "{\"city\": \"New York\"}",
"gcp.vertex.agent.tool_call_args": "{\"city\": \"New York\"}"
```

**Current routing:** All fall through to `result.metadata[key] = value` (line 2700-2701 in `attribute_router.ts`)

**Result:** Tool inputs are LOST - they go to metadata as JSON strings, not parsed into `inputs`!

---

## Why The Customer Reported "Input/Output Not Working"

### OpenInference Google ADK Span Coverage

| Span Type | Input Status | Output Status | Overall |
|-----------|--------------|---------------|---------|
| **LLM** | ✅ Indexed messages parsed correctly | ✅ Parsed from `output.value` | ✅ **WORKS** |
| **AGENT** | ✅ Correctly empty (no inputs expected) | ✅ Parsed from `output.value` | ✅ **WORKS** |
| **TOOL** | ❌ `input.value` NOT parsed | ❌ `output.value` goes to metadata | ❌ **BROKEN** |
| **CHAIN** | ❌ `input.value` (Google ADK `new_message`) NOT parsed | ❌ `output.value` goes to metadata | ❌ **BROKEN** |

---

## Root Causes

### 1. Tool Input Parsing Missing
**File:** `attribute_router.ts` line ~2700  
**Issue:** No special handler for `input.value` when `eventType === 'tool'`  
**Impact:** Tool arguments (`{"city": "New York"}`) go to metadata instead of inputs

### 2. Tool Output Routing Incomplete  
**File:** `attribute_router.ts` line 2463-2474  
**Current:** Only handles **string** `output.value` for tool/chain events  
**Issue:** Google ADK sends **JSON** objects, which don't match `typeof value === 'string'` check  
**Impact:** JSON tool outputs go to metadata instead of `outputs.message`

### 3. Google ADK CHAIN Input Format Not Supported
**File:** `attribute_router.ts` line 1030-1070 (OpenInference normalization)  
**Issue:** Looks for `inputData.messages` array, but Google ADK uses `inputData.new_message`  
**Impact:** User queries in CHAIN spans are lost

---

## Required Ingestion Service Fixes

### Fix 1: Parse Tool Inputs from `input.value`
**Location:** `applyUniversalRouting`, before line 2700

```typescript
// NEW: Parse input.value for TOOL spans
else if (key === 'input.value' && (eventType === 'tool' || attributes['openinference.span.kind'] === 'TOOL')) {
  try {
    const parsed = parseJSONSafe(value);
    if (parsed && typeof parsed === 'object') {
      // Merge parsed tool arguments directly into inputs
      Object.assign(result.inputs, parsed);
      consumedKeys.add(key);
      continue;
    }
  } catch {
    // Fall through to metadata if parse fails
  }
}
```

### Fix 2: Handle JSON `output.value` for Tools
**Location:** Line 2463-2474

```typescript
// UPDATED: Handle both string AND JSON output.value for tool/chain events
else if (
  key === 'output.value' &&
  (eventType === 'tool' || eventType === 'chain' || attributes['honeyhive_event_type'] === 'tool') &&
  !result.outputs.message
) {
  // Try parsing as JSON first (Google ADK format)
  const parsed = parseJSONSafe(value);
  if (parsed && typeof parsed === 'object') {
    // Keep full JSON structure for tool outputs
    result.outputs.message = typeof value === 'string' ? value : JSON.stringify(value);
  } else if (typeof value === 'string') {
    // Handle plain string outputs
    result.outputs.message = value;
  }
  consumedKeys.add(key);
  continue;
}
```

### Fix 3: Add Google ADK CHAIN Input Format Support
**Location:** `normalizeModelInputs`, after line 1043

```typescript
// NEW: Google ADK format: {new_message: {parts: [{text: "..."}], role: "user"}}
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

## Fixture Philosophy

**The fixtures document DESIRED behavior, not broken current behavior.**

This means:
- ✅ Fixtures show what SHOULD work after ingestion service is fixed
- ✅ Fixtures serve as regression test expectations
- ❌ Fixtures do NOT match current broken behavior

**Why:** The customer reported inputs/outputs not working. The fixtures document how they SHOULD work once fixed.

---

## Summary: Fixture Correctness

| Fixture | Pre-Processing (Input Attrs) | Post-Processing (Expected) | Matches Current? | Matches Desired? |
|---------|------------------------------|----------------------------|------------------|------------------|
| **LLM** | ✅ Actual OpenInference | ✅ Current ingestion output | ✅ YES | ✅ YES |
| **Agent** | ✅ Actual OpenInference | ✅ Current ingestion output | ✅ YES | ✅ YES |
| **Tool** | ✅ Actual OpenInference | ⚠️ Desired ingestion output | ❌ NO | ✅ YES |

**Tool fixture is now correct** - it documents how tool inputs SHOULD be parsed after implementing Fix #1 and #2 above.

---

## Next Steps

1. ✅ **DONE:** Fixed tool fixture to match desired behavior
2. **HIVE-KUBE:** Implement 3 ingestion service fixes above
3. **PYTHON-SDK:** Run fixture tests after hive-kube deployment
4. **VALIDATION:** Test with customer's actual Google ADK spans


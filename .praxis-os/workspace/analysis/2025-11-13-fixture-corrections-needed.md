# Fixture Corrections Needed

**Date:** 2025-11-13  
**Context:** Fixing fixtures before hive-kube implements ingestion support

---

## 🔴 **Critical: Pydantic AI Agent Fixture Has Wrong Event Type**

**File:** `pydantic_ai_anthropic_agent_001.json`

### Problem

**Line 25:** `"eventType": "tool"` ❌ **WRONG!**

**This is an AGENT RUN, not a tool execution!**

**Evidence:**
- Line 6: `"agent_name": "agent"`
- Line 7: `"gen_ai.agent.name": "agent"`
- Line 8: `"logfire.msg": "agent run"`
- Line 15: `"honeyhive_event_type": "model"` ← **Attributes say MODEL!**
- Line 19: `"pydantic_ai.all_messages"` ← Full conversation history
- Has chat_history (lines 29-38)
- Has role/content outputs (lines 41-42)

**This is clearly a MODEL/CHAIN event, not a TOOL event!**

---

### Confusion Source

**The fixture mixes MODEL semantics with TOOL eventType:**

```json
{
  "input": {
    "attributes": {
      "honeyhive_event_type": "model",  // ← Says MODEL
      ...
    },
    "eventType": "tool"  // ← Says TOOL ❌ CONTRADICTION!
  },
  "expected": {
    "inputs": {
      "chat_history": [...]  // ← MODEL pattern
    },
    "outputs": {
      "role": "assistant",   // ← MODEL pattern
      "content": "..."
    }
  }
}
```

---

### Correct Event Type

**This should be:**
- `eventType: "model"` (for Pydantic AI agent invocations)
- OR `eventType: "chain"` (if treating agents as orchestration)

**From my Pydantic AI analysis:**
- Pydantic AI agent runs create INTERNAL spans
- These are agent invocations (high-level LLM calls)
- Should map to `event_type: "model"` or `event_type: "chain"`

---

### Why This Matters

**If we leave it as `eventType: "tool"`:**
1. ❌ Ingestion will expect tool parameters (not chat_history)
2. ❌ Ingestion will expect outputs.message (not role/content)
3. ❌ Frontend will render as tool execution (wrong icon, wrong semantics)
4. ❌ Dynamic columns will be wrong

**With correct `eventType: "model"`:**
1. ✅ Ingestion expects chat_history
2. ✅ Ingestion expects role/content
3. ✅ Frontend renders as LLM call (correct icon, correct semantics)
4. ✅ Dynamic columns correct

---

## ✅ **Test Fixture is Intentional (Not a Mistake)**

**File:** `test_honeyhive_event_type_override.json`

This fixture INTENTIONALLY has:
- `eventType: "tool"` but attributes that indicate MODEL
- Purpose: Test that `honeyhive_event_type` attribute overrides automatic detection

**Lines 47-52:**
```json
"notes": [
  "CRITICAL: Tests that honeyhive_event_type overrides automatic event type detection",
  "Expected: event.event_type = 'tool' (from honeyhive_event_type)",
  "NOT: event.event_type = 'model' (from automatic detection based on gen_ai.prompt)"
]
```

**This is a TEST fixture - do NOT "fix" it!**

---

## 🔧 **Required Fix**

### File: `pydantic_ai_anthropic_agent_001.json`

**Change Line 25:**
```diff
- "eventType": "tool"
+ "eventType": "model"
```

**Rationale:**
- Pydantic AI agent invocations are LLM calls, not tool executions
- Fixture already has MODEL patterns (chat_history, role/content)
- Attributes already say `"honeyhive_event_type": "model"`
- Frontend expects MODEL semantics for this data

---

## 📊 **Validation After Fix**

**Run these checks:**

```bash
# 1. Verify fixture has correct event type
jq '.input.eventType' pydantic_ai_anthropic_agent_001.json
# Expected: "model"

# 2. Verify honeyhive_event_type matches
jq '.input.attributes.honeyhive_event_type' pydantic_ai_anthropic_agent_001.json
# Expected: "model"

# 3. Verify expected patterns match MODEL
jq '.expected.inputs | has("chat_history")' pydantic_ai_anthropic_agent_001.json
# Expected: true

jq '.expected.outputs | has("role") and has("content")' pydantic_ai_anthropic_agent_001.json
# Expected: true
```

---

## 🎯 **Impact on Hive-Kube**

**Before Fix:**
- Hive-kube sees `eventType: "tool"`
- Implements tool parsing (expects parameters, outputs.message)
- Test fails because fixture has chat_history and role/content

**After Fix:**
- Hive-kube sees `eventType: "model"`
- Implements model parsing (expects chat_history, role/content)
- Test passes ✅

---

## 📝 **Lesson for Integration Workflow**

**Add Validation Step:**

```python
def validate_fixture_consistency(fixture):
    """Ensure event type matches expected patterns"""
    
    event_type = fixture["input"]["eventType"]
    expected_inputs = fixture["expected"]["inputs"]
    expected_outputs = fixture["expected"]["outputs"]
    
    # Check MODEL event consistency
    if event_type == "model":
        if "chat_history" not in expected_inputs:
            warnings.warn(f"MODEL event should have chat_history: {fixture['name']}")
        
        if "role" not in expected_outputs or "content" not in expected_outputs:
            warnings.warn(f"MODEL event should have role/content: {fixture['name']}")
    
    # Check TOOL event consistency
    elif event_type == "tool":
        if "chat_history" in expected_inputs:
            raise FixtureError(f"TOOL event should NOT have chat_history: {fixture['name']}")
        
        if "role" in expected_outputs and "content" in expected_outputs:
            raise FixtureError(f"TOOL event should NOT have role/content: {fixture['name']}")
        
        if "message" not in expected_outputs:
            warnings.warn(f"TOOL event should have message: {fixture['name']}")
```

**This would have caught the Pydantic AI fixture error immediately!**


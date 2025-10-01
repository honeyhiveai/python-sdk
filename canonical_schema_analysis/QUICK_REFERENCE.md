# HoneyHive Canonical Schema - Quick Reference

**Source**: 385 production events from Deep Research Prod (Financial Research Agent Eval)  
**Date**: 2025-10-01

---

## 🎯 The Canonical Schema Structure

Every HoneyHive event follows this structure:

```json
{
  // Core fields
  "event_id": "uuid",
  "event_name": "string", 
  "event_type": "model|chain|tool|session",
  "source": "string",
  
  // Hierarchy
  "session_id": "uuid",
  "parent_id": "uuid|null",
  "children_ids": ["uuid"],
  
  // THE 4 TARGET SECTIONS (what DSL maps to)
  "inputs": {},      // ← DSL populates this
  "outputs": {},     // ← DSL populates this  
  "config": {},      // ← DSL populates this
  "metadata": {},    // ← DSL populates this
  
  // Timing & observability
  "start_time": "ms", "end_time": "ms", "duration": "ms",
  "error": "string|null",
  "metrics": {}, "feedback": {}, "user_properties": {}
}
```

---

## ⚡ Key Insights for DSL Development

### 1. **It's FLAT, Not Nested**

❌ **Raw OpenAI Response**:
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "id": "call_abc",
        "function": {"name": "search", "arguments": "{...}"}
      }]
    }
  }]
}
```

✅ **Canonical HoneyHive**:
```json
{
  "outputs": {
    "role": "assistant",
    "tool_calls.0.id": "call_abc",
    "tool_calls.0.name": "search",
    "tool_calls.0.arguments": "{...}"
  }
}
```

### 2. **Dot Notation for Arrays**

- `tool_calls.0.id` (HoneyHive)
- NOT `tool_calls[0].id` (Python/JS syntax)
- NOT `tool_calls.id` (loses index)

### 3. **JSON Strings Stay as Strings**

- `tool_calls.*.arguments` is **always a JSON string**
- DSL should **NOT parse it** to an object
- This matches what instrumentors do

### 4. **Chat History is an Array**

```json
{
  "inputs": {
    "chat_history": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "...", "tool_calls.0.id": "..."},
      {"role": "tool", "content": "...", "tool_call_id": "..."}
    ]
  }
}
```

---

## 📋 Common Field Patterns

### MODEL Events (LLM calls)

**inputs**:
- `chat_history` (List[Dict]) - Always present

**outputs**:
- `role` (str) - Always present
- `content` (str|None) - Can be null if tool_calls
- `finish_reason` (str) - Always present
- `tool_calls.*.id`, `tool_calls.*.name`, `tool_calls.*.arguments` - When tool calls

**config**:
- `provider`, `model`, `headers`, `is_streaming`

**metadata**:
- `scope.name`, `scope.version` - Instrumentor info
- `total_tokens`, `prompt_tokens`, `completion_tokens`
- `gen_ai.openai.api_base`, `response_model`, `system_fingerprint`

---

## 🔄 DSL Translation Flow

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: DETECT SOURCE                                   │
│ - OpenInference? (llm.*)                                │
│ - Traceloop? (gen_ai.*)                                 │
│ - OpenLit? (gen_ai.*)                                   │
│ - HoneyHive Direct? (honeyhive_*)                       │
│ - Framework? (custom attributes)                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: EXTRACT RAW DATA                                │
│ - Navigate to attributes using source-specific rules    │
│ - Example: llm.output_messages.0.message.content → val  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: TRANSFORM                                       │
│ - Reconstruct arrays from flattened keys               │
│ - Parse JSON strings IF needed (not for tool args)     │
│ - Normalize message formats                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: MAP TO 4 SECTIONS                               │
│ - inputs ← messages, parameters                         │
│ - outputs ← response, tool_calls, finish_reason         │
│ - config ← provider, model, settings                    │
│ - metadata ← tokens, instrumentor, tracking             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: FLATTEN WITHIN SECTIONS                         │
│ - {tool_calls: [{id: "x"}]} → {tool_calls.0.id: "x"}   │
│ - Preserve JSON strings (don't parse tool args)        │
└─────────────────────────────────────────────────────────┘
```

---

## 🚨 Critical DSL Rules

### ✅ DO:
1. Flatten nested objects to dot notation
2. Use array indices in keys (`.0`, `.1`, etc.)
3. Keep `tool_calls.*.arguments` as JSON string
4. Normalize all message formats to canonical
5. Map every field to one of the 4 sections

### ❌ DON'T:
1. Create nested objects in outputs/inputs/config/metadata
2. Parse JSON strings that should stay as strings
3. Use array bracket notation (`[0]`)
4. Lose data when flattening
5. Add extra wrapper structures

---

## 🎓 Production Examples

### Example 1: Simple Chat Response

**Input Span Attributes** (Traceloop):
```
gen_ai.completion.0.role = "assistant"
gen_ai.completion.0.content = "Hello, how can I help?"
gen_ai.completion.0.finish_reason = "stop"
gen_ai.system = "openai"
gen_ai.request.model = "gpt-4o"
```

**DSL Output** (Canonical):
```json
{
  "outputs": {
    "role": "assistant",
    "content": "Hello, how can I help?",
    "finish_reason": "stop"
  },
  "config": {
    "provider": "openai",
    "model": "gpt-4o"
  }
}
```

### Example 2: Tool Call Response

**Input Span Attributes** (OpenInference):
```
llm.output_messages.0.message.role = "assistant"
llm.output_messages.0.message.content = null
llm.output_messages.0.message.tool_calls.0.tool_call.id = "call_abc"
llm.output_messages.0.message.tool_calls.0.tool_call.function.name = "search_web"
llm.output_messages.0.message.tool_calls.0.tool_call.function.arguments = '{"query":"NVDA"}'
```

**DSL Output** (Canonical):
```json
{
  "outputs": {
    "role": "assistant",
    "content": null,
    "tool_calls.0.id": "call_abc",
    "tool_calls.0.name": "search_web",
    "tool_calls.0.arguments": "{\"query\":\"NVDA\"}"
  }
}
```

**Note**: `arguments` stays as JSON string!

### Example 3: HoneyHive Direct SDK

**Input Span Attributes** (HoneyHive Direct):
```
honeyhive_outputs.role = "assistant"
honeyhive_outputs.content = "Result text"
honeyhive_outputs.finish_reason = "stop"
honeyhive_config.model = "gpt-4o"
honeyhive_config.provider = "OpenAI"
```

**DSL Output** (Canonical):
```json
{
  "outputs": {
    "role": "assistant",
    "content": "Result text",
    "finish_reason": "stop"
  },
  "config": {
    "model": "gpt-4o",
    "provider": "OpenAI"
  }
}
```

---

## 📊 Data Distribution (from 385 events)

- **MODEL**: 100 events (26%)
- **CHAIN**: 100 events (26%)  
- **TOOL**: 100 events (26%)
- **SESSION**: 85 events (22%)

All events 100% conform to the 4-section structure.

---

## 🔗 Related Documents

- [Full Analysis](./CANONICAL_SCHEMA_ANALYSIS.md) - Comprehensive schema analysis
- [DSL Flow](../.agent-os/standards/architecture/DSL_TO_HONEYHIVE_SCHEMA_FLOW.md) - DSL architecture
- [SDK Serialization](../.agent-os/standards/architecture/HONEYHIVE_SDK_SERIALIZATION_PATTERN.md) - How SDK sets attributes

---

**Last Updated**: 2025-10-01  
**Validated Against**: 385 production events


# HoneyHive Canonical Schema Analysis

**Date**: 2025-10-01  
**Data Source**: Deep Research Prod - Financial Research Agent Eval  
**Sample Size**: 385 production events (100 model, 100 chain, 100 tool, 85 session)

---

## 🎯 Executive Summary

This analysis examines the canonical HoneyHive event schema from real production data across all event types. The schema follows a consistent 4-section structure (`inputs`, `outputs`, `config`, `metadata`) with event-type-specific variations.

**Key Finding**: The canonical schema uses **flat, simple key-value pairs** within each section, NOT deeply nested JSON structures matching raw provider responses.

---

## 📊 Schema Structure

### Top-Level Fields (100% consistent across all events)

```json
{
  // Core identification
  "event_id": "uuid",
  "event_name": "string",
  "event_type": "model|chain|tool|session",
  "source": "string",
  
  // Hierarchy
  "project_id": "uuid",
  "session_id": "uuid",
  "parent_id": "uuid|null",
  "children_ids": ["uuid"],
  
  // The 4-Section Target Schema
  "inputs": {},      // Event inputs
  "outputs": {},     // Event outputs
  "config": {},      // Event configuration
  "metadata": {},    // Event metadata
  
  // Timing
  "start_time": "timestamp_ms",
  "end_time": "timestamp_ms",
  "duration": "float_ms",
  
  // Observability
  "error": "string|null",
  "metrics": {},
  "feedback": {},
  "user_properties": {}
}
```

---

## 🔍 Event Type Deep Dive

### 1. MODEL Events (LLM API calls)

**Sample Size**: 100 events

#### Inputs Structure

```json
{
  "inputs": {
    "chat_history": [
      {
        "role": "system",
        "content": "You are a helpful assistant..."
      },
      {
        "role": "user",
        "content": "Task description..."
      },
      {
        "role": "assistant",
        "content": "Response...",
        "tool_calls.0.id": "call_abc",
        "tool_calls.0.name": "search_web",
        "tool_calls.0.arguments": "{\"query\":\"...\"}"
      },
      {
        "role": "tool",
        "content": "Tool output...",
        "tool_call_id": "call_abc"
      }
    ]
  }
}
```

**Key Observations**:
- `chat_history` is an **array of message objects**
- Tool calls are **flattened** within message objects using dot notation (`tool_calls.0.id`, `tool_calls.0.name`, `tool_calls.0.arguments`)
- Tool call `arguments` is a **JSON string**, not a parsed object
- Multi-turn conversations are represented as sequential messages in the array

#### Outputs Structure

```json
{
  "outputs": {
    "finish_reason": "stop",
    "role": "assistant",
    "content": "The response text..."
  }
}
```

OR for tool calls:

```json
{
  "outputs": {
    "finish_reason": "tool_calls",
    "role": "assistant",
    "content": null,
    "tool_calls.0.id": "call_abc",
    "tool_calls.0.name": "function_name",
    "tool_calls.0.arguments": "{\"param\":\"value\"}"
  }
}
```

**Key Observations**:
- **Flat structure** - no nested objects
- `content` can be null when tool_calls are present
- Tool calls use **dot notation** for array elements
- `arguments` is a **JSON string**
- Only the **final response** is captured, not the full raw provider response

#### Config Structure

```json
{
  "config": {
    "provider": "OpenAI",
    "model": "gpt-4o",
    "headers": "None",
    "is_streaming": false
  }
}
```

**Key Observations**:
- Simple key-value pairs
- Provider and model identification
- No nested configuration objects

#### Metadata Structure

```json
{
  "metadata": {
    "scope": {
      "name": "opentelemetry.instrumentation.openai.v1",
      "version": "0.30.0"
    },
    "llm.request.type": "chat",
    "disable_http_tracing": false,
    "run_id": "uuid",
    "dataset_id": "uuid",
    "datapoint_id": "uuid",
    "gen_ai.openai.api_base": "https://api.openai.com/v1/",
    "response_model": "gpt-4o-2024-08-06",
    "system_fingerprint": "fp_...",
    "total_tokens": 306,
    "completion_tokens": 152,
    "prompt_tokens": 154
  }
}
```

**Key Observations**:
- Mix of semantic convention attributes (from instrumentor)
- Token usage statistics
- Instrumentor identification (`scope.name`, `scope.version`)
- Run/dataset tracking for evaluations

---

### 2. CHAIN Events (Orchestration/Agent steps)

**Sample Size**: 100 events

#### Typical Structure

```json
{
  "event_name": "agent_step",
  "event_type": "chain",
  "inputs": {
    "task": "Research topic X",
    "context": "Previous findings..."
  },
  "outputs": {
    "decision": "Use tool Y",
    "reasoning": "Because..."
  },
  "config": {
    "agent_type": "react",
    "max_iterations": 10
  },
  "metadata": {
    "iteration": 5,
    "tools_available": ["search", "file_ops"]
  }
}
```

**Key Observations**:
- Highly variable structure based on framework/use case
- Typically represents agent reasoning or workflow steps
- Parent to MODEL and TOOL events

---

### 3. TOOL Events (Tool/Function executions)

**Sample Size**: 100 events

#### Typical Structure

```json
{
  "event_name": "search_web",
  "event_type": "tool",
  "inputs": {
    "query": "Nvidia insider trading"
  },
  "outputs": {
    "results": [
      {
        "title": "...",
        "url": "...",
        "snippet": "..."
      }
    ]
  },
  "config": {
    "tool_name": "search_web",
    "timeout": 30
  },
  "metadata": {
    "latency_ms": 1234,
    "status_code": 200
  }
}
```

**Key Observations**:
- Structure varies by tool implementation
- Inputs/outputs reflect tool-specific parameters
- Child events of CHAIN or MODEL events

---

### 4. SESSION Events (Top-level traces)

**Sample Size**: 85 events

#### Typical Structure

```json
{
  "event_name": "Financial Research Agent Eval",
  "event_type": "session",
  "inputs": {
    "task_description": "Find insider trading for NVDA",
    "dataset_id": "uuid"
  },
  "outputs": {
    "final_result": "Completed successfully",
    "output_file": "research_notes.txt"
  },
  "config": {
    "eval_name": "Financial Research Agent Eval",
    "agent_version": "v1.0"
  },
  "metadata": {
    "total_llm_calls": 15,
    "total_tool_calls": 8,
    "total_cost": 0.045
  }
}
```

**Key Observations**:
- Root of the event hierarchy
- Aggregated metadata (costs, counts)
- No parent_id

---

## 🔑 Critical Schema Insights

### 1. **Flattening Pattern**

The canonical schema **does NOT preserve raw API response structures**. Instead:

- **Raw OpenAI Response**:
  ```json
  {
    "choices": [{
      "message": {
        "role": "assistant",
        "content": "...",
        "tool_calls": [{
          "id": "call_abc",
          "function": {
            "name": "search",
            "arguments": "{...}"
          }
        }]
      }
    }]
  }
  ```

- **Canonical HoneyHive Schema**:
  ```json
  {
    "outputs": {
      "role": "assistant",
      "content": "...",
      "tool_calls.0.id": "call_abc",
      "tool_calls.0.name": "search",
      "tool_calls.0.arguments": "{...}"
    }
  }
  ```

**Transformation Rules**:
1. Nested objects → Flat key-value pairs
2. Arrays → Dot-notation indices (`.0`, `.1`, etc.)
3. Deep nesting (`.choices[0].message.tool_calls[0].function.name`) → Simplified (`.tool_calls.0.name`)

### 2. **The 4-Section Contract**

Every event MUST populate these sections:

| Section | Purpose | Structure | Required |
|---------|---------|-----------|----------|
| `inputs` | Event inputs/parameters | Dict[str, Any] | Yes (can be {}) |
| `outputs` | Event results/responses | Dict[str, Any] | Yes (can be {}) |
| `config` | Event configuration | Dict[str, Any] | Yes (can be {}) |
| `metadata` | Observability/tracking | Dict[str, Any] | Yes (can be {}) |

**DSL Implication**: The DSL's job is to **map from various trace source formats** (instrumentor attributes, raw responses, framework data) **into this 4-section flat structure**.

### 3. **JSON String Pattern**

Certain fields are **JSON strings**, not parsed objects:

- `tool_calls.*.arguments` - Always a JSON string
- Sometimes `inputs` or `outputs` may contain JSON strings for complex nested data

**DSL Implication**: The DSL must handle:
- Parsing JSON strings when needed
- Leaving them as strings when that's the canonical format (like `tool_calls.*.arguments`)

### 4. **Message History Normalization**

The `inputs.chat_history` array shows a **canonical message format**:

```python
class CanonicalMessage:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str | None
    
    # Optional fields (tool calls)
    tool_calls.0.id: str
    tool_calls.0.name: str
    tool_calls.0.arguments: str  # JSON string
    
    # Optional fields (tool responses)
    tool_call_id: str
```

This is **different from**:
- OpenAI's raw `ChatCompletionMessage` structure
- Anthropic's `content` blocks
- Other provider-specific formats

**DSL Implication**: The DSL must normalize diverse message formats into this canonical structure.

---

## 📋 Common Field Patterns

### Observed in `inputs`:

| Field | Type | Description | Frequency |
|-------|------|-------------|-----------|
| `chat_history` | List[Dict] | Message array for LLM calls | MODEL: 100% |
| `messages` | List[Dict] | Alternative name for chat_history | Rare |
| `query` | str | Single input query | TOOL: Common |
| `task` | str | Task description | CHAIN: Common |
| `context` | str/Dict | Additional context | CHAIN: Common |

### Observed in `outputs`:

| Field | Type | Description | Frequency |
|-------|------|-------------|-----------|
| `role` | str | Message role | MODEL: 100% |
| `content` | str/None | Message content | MODEL: 100% |
| `finish_reason` | str | Completion reason | MODEL: 100% |
| `tool_calls.*.id` | str | Tool call ID | MODEL: When tool calls |
| `tool_calls.*.name` | str | Function name | MODEL: When tool calls |
| `tool_calls.*.arguments` | str | JSON args string | MODEL: When tool calls |

### Observed in `config`:

| Field | Type | Description | Frequency |
|-------|------|-------------|-----------|
| `provider` | str | LLM provider | MODEL: 100% |
| `model` | str | Model name | MODEL: 100% |
| `headers` | str | Request headers | MODEL: Common |
| `is_streaming` | bool | Streaming mode | MODEL: 100% |

### Observed in `metadata`:

| Field | Type | Description | Frequency |
|-------|------|-------------|-----------|
| `scope.name` | str | Instrumentor name | All: 100% |
| `scope.version` | str | Instrumentor version | All: 100% |
| `total_tokens` | int | Total tokens | MODEL: 100% |
| `prompt_tokens` | int | Prompt tokens | MODEL: 100% |
| `completion_tokens` | int | Completion tokens | MODEL: 100% |
| `llm.request.type` | str | Request type | MODEL: 100% |
| `gen_ai.openai.api_base` | str | API endpoint | MODEL: 100% |
| `response_model` | str | Actual model used | MODEL: 100% |
| `system_fingerprint` | str | Model fingerprint | MODEL: 100% |

---

## 🎯 DSL Translation Strategy

Based on this analysis, the DSL must perform these transformations:

### Phase 1: Detection
- Identify trace source (OpenInference, Traceloop, OpenLit, HoneyHive Direct, Framework)
- Identify provider (OpenAI, Anthropic, etc.)
- Identify event type (model, chain, tool, session)

### Phase 2: Extraction
- Extract raw data from span attributes using navigation rules
  - Example: `llm.output_messages.0.message.content` → `content`
  - Example: `gen_ai.completion.0.message.tool_calls.0.id` → `tool_calls.0.id`

### Phase 3: Transformation
- Apply transforms to normalize data
  - Reconstruct arrays from flattened attributes
  - Parse JSON strings when needed
  - Normalize message formats

### Phase 4: Mapping to Canonical Schema
- Map extracted fields to the 4 sections:
  - `inputs` ← Input messages, parameters
  - `outputs` ← Response content, tool calls, finish reason
  - `config` ← Provider, model, configuration
  - `metadata` ← Token usage, instrumentor info, tracking IDs

### Phase 5: Flattening
- Flatten nested structures within each section
  - `{tool_calls: [{id: "x"}]}` → `{tool_calls.0.id: "x"}`
  - Keep JSON strings as strings (don't parse `tool_calls.*.arguments`)

---

## 🚨 Critical DSL Requirements

### 1. **Handle Multiple Message Formats**

The DSL must convert these diverse formats:

**OpenInference** (`llm.output_messages.*`):
```
llm.output_messages.0.message.role = "assistant"
llm.output_messages.0.message.content = "text"
llm.output_messages.0.message.tool_calls.0.tool_call.id = "call_abc"
llm.output_messages.0.message.tool_calls.0.tool_call.function.name = "search"
llm.output_messages.0.message.tool_calls.0.tool_call.function.arguments = "{...}"
```

**Traceloop** (`gen_ai.completion.*`):
```
gen_ai.completion.0.message.role = "assistant"
gen_ai.completion.0.message.content = "text"
gen_ai.completion.0.message.tool_calls.0.id = "call_abc"
gen_ai.completion.0.message.tool_calls.0.function.name = "search"
gen_ai.completion.0.message.tool_calls.0.function.arguments = "{...}"
```

**HoneyHive Direct** (`honeyhive_outputs.*`):
```
honeyhive_outputs.role = "assistant"
honeyhive_outputs.content = "text"
honeyhive_outputs.tool_calls.0.id = "call_abc"
honeyhive_outputs.tool_calls.0.name = "search"
honeyhive_outputs.tool_calls.0.arguments = "{...}"
```

**Into Canonical**:
```json
{
  "outputs": {
    "role": "assistant",
    "content": "text",
    "tool_calls.0.id": "call_abc",
    "tool_calls.0.name": "search",
    "tool_calls.0.arguments": "{...}"
  }
}
```

### 2. **Preserve JSON String Fields**

The DSL must **NOT parse** these fields:
- `tool_calls.*.arguments` - Keep as JSON string
- Any field that the canonical schema expects as a JSON string

### 3. **Handle Chat History Arrays**

For `inputs.chat_history`, the DSL must:
1. Reconstruct the array from flattened attributes
2. Normalize each message to canonical format
3. Preserve the chronological order
4. Handle mixed message types (system, user, assistant, tool)

---

## 📈 Next Steps

### Immediate Actions

1. **Update DSL Field Mappings** - Ensure all `field_mappings.yaml` files map to these flat canonical structures
2. **Add HoneyHive Direct Support** - Add navigation rules for `honeyhive_*` attributes
3. **Validate Flattening Logic** - Ensure transforms correctly flatten nested structures
4. **Test JSON String Handling** - Verify `tool_calls.*.arguments` remains as JSON string

### Validation Strategy

1. Run DSL on these 385 production events
2. Compare DSL output to actual canonical schema
3. Calculate field-by-field accuracy
4. Identify gaps and fix

### Documentation Updates

1. Update `DSL_TO_HONEYHIVE_SCHEMA_FLOW.md` with these findings
2. Create schema validation tests using these examples
3. Document the flattening rules explicitly

---

## 🎓 Key Takeaways

1. **Canonical schema is FLAT** - Not nested like raw API responses
2. **4-Section structure is universal** - All events follow this pattern
3. **Dot notation for arrays** - `tool_calls.0.id`, not `tool_calls[0].id`
4. **JSON strings are preserved** - Some fields stay as JSON strings
5. **Message normalization is critical** - Diverse formats must map to one canonical format
6. **DSL is a translation layer** - From instrumentor/provider formats TO canonical schema

---

**Analysis Complete**: 2025-10-01
**Data Source**: 385 production events from Deep Research Prod
**Quality**: Production-validated canonical schema patterns


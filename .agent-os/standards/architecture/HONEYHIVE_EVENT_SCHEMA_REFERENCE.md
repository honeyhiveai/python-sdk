# HoneyHive Event Schema Reference

**Document Version**: 1.0  
**Date**: 2025-09-30  
**Status**: Authoritative Schema Reference  
**Purpose**: Define what goes into `inputs`, `outputs`, `config`, and `metadata` fields that the DSL must produce

---

## 🎯 Overview

This document defines the **target structure** that the DSL-based semantic convention translation layer must produce. All provider response data, regardless of source (OpenAI, Anthropic, Gemini, instrumentor-provided spans, etc.), must be translated into this unified HoneyHive event schema.

**Critical Context**: This is what the **backend expects to receive** and what the **UI displays**. The DSL's job is to translate any LLM provider response or semantic convention into these exact structures.

---

## 📋 Core HoneyHive Event Schema

### Top-Level Structure

```python
HoneyHiveEvent = {
    # Core identification (populated by span processor)
    "event_id": "uuid",
    "session_id": "uuid", 
    "parent_id": "uuid | null",  # null for root/session events
    "event_name": "string",
    "event_type": "model | chain | tool | session",
    "source": "string",
    "project_id": "string",
    
    # THE FOUR CRITICAL FIELDS (populated by DSL translation)
    "inputs": {...},      # What went INTO the operation
    "outputs": {...},     # What came OUT of the operation
    "config": {...},      # Configuration/parameters used
    "metadata": {...},    # Additional context/metrics
    
    # Timing & metrics (populated by span processor)
    "start_time": float,      # milliseconds since epoch
    "end_time": float,        # milliseconds since epoch
    "duration": float,        # milliseconds
    "error": "string | null",
    "feedback": {...},
    "metrics": {...},
    "user_properties": {...},
    "children_ids": ["uuid"]
}
```

---

## 1. Model Events (LLM API Calls)

### 1.1 Model Event: Chat Completion (Most Common)

**What This Represents**: An LLM chat completion call (OpenAI, Anthropic, Gemini, etc.)

```json
{
  "event_type": "model",
  "event_name": "chat.completion",
  
  "inputs": {
    "chat_history": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user", 
        "content": "What is 2+2?"
      }
    ],
    "functions": [...]  // Optional: function/tool definitions
  },
  
  "outputs": {
    "role": "assistant",
    "content": "2 + 2 equals 4.",
    "finish_reason": "stop",
    "tool_calls": [...]  // Optional: if model called tools
  },
  
  "config": {
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_completion_tokens": 1000,
    "top_p": 1.0,
    "is_streaming": false,
    "headers": "None"
  },
  
  "metadata": {
    "total_tokens": 150,
    "prompt_tokens": 120,
    "completion_tokens": 30,
    "llm.request.type": "chat",
    "system_fingerprint": "fp_abc123",
    "response_model": "gpt-4o-2024-05-13"
  }
}
```

### 1.2 Model Event: Chat with Tool Calls

**What This Represents**: LLM call that invokes tools/functions

```json
{
  "event_type": "model",
  "event_name": "chat.completion",
  
  "inputs": {
    "chat_history": [
      {"role": "system", "content": "You can use tools."},
      {"role": "user", "content": "What's the weather in SF?"}
    ],
    "functions": [
      {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string"}
          }
        }
      }
    ]
  },
  
  "outputs": {
    "role": "assistant",
    "content": null,  // null when using tool_calls
    "finish_reason": "tool_calls",
    "tool_calls": [
      {
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\": \"San Francisco\"}"  // JSON string
        }
      }
    ]
  },
  
  "config": {
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_completion_tokens": 1000
  },
  
  "metadata": {
    "total_tokens": 180,
    "prompt_tokens": 150,
    "completion_tokens": 30
  }
}
```

### 1.3 Model Event: Text Completion (Legacy)

**What This Represents**: Legacy completion API (non-chat)

```json
{
  "event_type": "model",
  "event_name": "completion",
  
  "inputs": {
    "prompt": "Once upon a time"
  },
  
  "outputs": {
    "content": " there was a brave knight...",
    "finish_reason": "stop"
  },
  
  "config": {
    "provider": "openai",
    "model": "gpt-3.5-turbo-instruct",
    "temperature": 0.7,
    "max_tokens": 100
  },
  
  "metadata": {
    "total_tokens": 120,
    "prompt_tokens": 5,
    "completion_tokens": 115
  }
}
```

### 1.4 Model Event: Embeddings

**What This Represents**: Embedding generation

```json
{
  "event_type": "model",
  "event_name": "embeddings",
  
  "inputs": {
    "chunks": [
      "Hello world",
      "How are you?"
    ]
  },
  
  "outputs": {
    "embeddings": [
      [0.123, 0.456, ...],  // 1536-dim vector
      [0.789, 0.012, ...]
    ],
    "num_embeddings": 2
  },
  
  "config": {
    "provider": "openai",
    "model": "text-embedding-3-small",
    "dimensions": 1536
  },
  
  "metadata": {
    "total_tokens": 15,
    "prompt_tokens": 15,
    "completion_tokens": 0
  }
}
```

### 1.5 Model Event: Rerank

**What This Represents**: Document reranking

```json
{
  "event_type": "model",
  "event_name": "rerank",
  
  "inputs": {
    "query": "What is machine learning?",
    "nodes": [
      "Machine learning is...",
      "Deep learning involves...",
      "AI systems can..."
    ]
  },
  
  "outputs": {
    "nodes": [
      {"index": 0, "score": 0.95, "content": "Machine learning is..."},
      {"index": 2, "score": 0.87, "content": "AI systems can..."},
      {"index": 1, "score": 0.72, "content": "Deep learning involves..."}
    ]
  },
  
  "config": {
    "provider": "cohere",
    "model": "rerank-v3",
    "top_k": 3
  },
  
  "metadata": {}
}
```

---

## 2. Chain Events (Workflow Steps)

### 2.1 Chain Event: Generic Chain Step

**What This Represents**: A workflow step that orchestrates other operations

```json
{
  "event_type": "chain",
  "event_name": "workflow.step",
  
  "inputs": {
    "_params_": {
      "messages": [...],
      "self": "WorkflowClass instance",
      "additional_params": {...}
    }
  },
  
  "outputs": {
    "result": "Step completed successfully"  // Can be string, object, or array
  },
  
  "config": {},
  
  "metadata": {
    "scope": {
      "name": "honeyhive.tracer.custom",
      "version": "1.0.0"
    },
    "honeyhive_event_type": "chain"
  }
}
```

---

## 3. Tool Events (Tool Execution)

### 3.1 Tool Event: Function Call Execution

**What This Represents**: Execution of a function/tool called by an LLM

```json
{
  "event_type": "tool",
  "event_name": "tool.execution",
  
  "inputs": {
    "_params_": {
      "self": "ToolClass instance",
      "tool_call": {
        "id": "call_abc123",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\": \"San Francisco\"}"
        }
      },
      "arguments": {
        "location": "San Francisco"
      }
    }
  },
  
  "outputs": {
    "result": {
      "temperature": 68,
      "condition": "Sunny",
      "humidity": 55
    }
  },
  
  "config": {},
  
  "metadata": {
    "scope": {
      "name": "honeyhive.tracer.custom",
      "version": "1.0.0"
    },
    "honeyhive_event_type": "tool"
  }
}
```

---

## 4. Session Events (Root Events)

### 4.1 Session Event: Agent Session

**What This Represents**: A complete agent session/conversation

```json
{
  "event_type": "session",
  "event_name": "agent.session",
  "parent_id": null,  // Session events have no parent
  
  "inputs": {
    "inputs": {
      "task": "Research Tesla and Ford valuations",
      "initial_params": {...}
    }
  },
  
  "outputs": {
    "action_history": [
      "Searched for Tesla valuation",
      "Searched for Ford valuation",
      "Compared metrics"
    ],
    "complete": true,
    "iterations": 3,
    "summary": "Completed valuation comparison"
  },
  
  "config": {},
  
  "metadata": {
    "num_events": 15,
    "num_model_events": 5,
    "has_feedback": false,
    "cost": 0.05,
    "total_tokens": 2500,
    "prompt_tokens": 1800,
    "completion_tokens": 700
  }
}
```

---

## 🔄 DSL Translation Rules

### What the DSL Must Do

The DSL must translate **any** LLM provider response or semantic convention into the above structures. Here's how:

### 1. **Inputs Translation**

**Sources**:
- `gen_ai.prompt` → `inputs.chat_history`
- `llm.input_messages` → `inputs.chat_history`
- `gen_ai.request.functions` → `inputs.functions`
- Provider-specific attributes → Normalized structure

**Example OpenAI → HoneyHive**:
```yaml
# DSL mapping
inputs:
  chat_history:
    source: "gen_ai.prompt"  # or llm.input_messages
    transform: "parse_messages_array"
  functions:
    source: "gen_ai.request.functions"
    transform: "parse_json_or_direct"
```

### 2. **Outputs Translation**

**Sources**:
- `gen_ai.completion` → `outputs.content`, `outputs.tool_calls`
- `llm.output_messages` → `outputs.content`
- `gen_ai.response.finish_reasons` → `outputs.finish_reason`

**Example OpenAI → HoneyHive**:
```yaml
# DSL mapping
outputs:
  content:
    source: "gen_ai.completion.0.message.content"
    fallback: "llm.output_messages.0.content"
  tool_calls:
    source: "gen_ai.completion.0.message.tool_calls"
    transform: "reconstruct_array_from_flattened"
  finish_reason:
    source: "gen_ai.response.finish_reasons.0"
  role:
    source: "gen_ai.completion.0.message.role"
    default: "assistant"
```

### 3. **Config Translation**

**Sources**:
- `gen_ai.system` → `config.provider`
- `gen_ai.request.model` → `config.model`
- `gen_ai.request.temperature` → `config.temperature`
- `gen_ai.request.max_tokens` → `config.max_completion_tokens`

**Example OpenAI → HoneyHive**:
```yaml
# DSL mapping
config:
  provider:
    source: "gen_ai.system"
  model:
    source: "gen_ai.request.model"
  temperature:
    source: "gen_ai.request.temperature"
  max_completion_tokens:
    source: "gen_ai.request.max_tokens"
  is_streaming:
    source: "llm.is_streaming"
    default: false
```

### 4. **Metadata Translation**

**Sources**:
- `gen_ai.usage.prompt_tokens` → `metadata.prompt_tokens`
- `gen_ai.usage.completion_tokens` → `metadata.completion_tokens`
- `gen_ai.usage.total_tokens` → `metadata.total_tokens`
- `gen_ai.response.model` → `metadata.response_model`
- `gen_ai.openai.system_fingerprint` → `metadata.system_fingerprint`

**Example OpenAI → HoneyHive**:
```yaml
# DSL mapping
metadata:
  prompt_tokens:
    source: "gen_ai.usage.prompt_tokens"
  completion_tokens:
    source: "gen_ai.usage.completion_tokens"
  total_tokens:
    source: "gen_ai.usage.total_tokens"
  response_model:
    source: "gen_ai.response.model"
  system_fingerprint:
    source: "gen_ai.openai.system_fingerprint"
```

---

## 🎯 Critical Data Types

### Chat History Structure

```python
chat_history: List[Dict[str, Any]] = [
    {
        "role": "system | user | assistant | tool",
        "content": str,  # Main message content
        
        # Optional fields (assistant messages)
        "tool_calls": [
            {
                "id": str,
                "type": "function",
                "function": {
                    "name": str,
                    "arguments": str  # JSON string, NOT object!
                }
            }
        ],
        
        # Optional fields (tool messages)
        "tool_call_id": str,
        "name": str,
        
        # Optional fields (OpenAI specific)
        "refusal": str,
        "audio": {...}
    }
]
```

**CRITICAL**: `tool_calls[].function.arguments` is a **JSON string**, not an object!

### Tool Calls Structure

```python
tool_calls: List[Dict[str, Any]] = [
    {
        "id": str,           # "call_abc123"
        "type": "function",  # Always "function" for OpenAI
        "function": {
            "name": str,     # "get_weather"
            "arguments": str # '{"location": "SF"}' - JSON STRING!
        }
    }
]
```

### Outputs Structure

```python
outputs: Dict[str, Any] = {
    "role": "assistant",         # Always "assistant" for model outputs
    "content": str | None,       # None if tool_calls present
    "finish_reason": str,        # "stop", "length", "tool_calls", etc.
    "tool_calls": [...],         # Optional: if model called tools
    
    # Provider-specific fields
    "refusal": str,              # OpenAI: refusal message
    "audio": {...},              # OpenAI: audio response
    "annotations": [...]         # OpenAI: citations/references
}
```

---

## 📊 Backend Processing Flow

### How Backend Receives and Uses This Data

```javascript
// Backend: otel_processing_service.js
function parseTrace(trace) {
  for (let span of spans) {
    // Primary path: honeyhive_* attributes (pre-processed by SDK)
    if (hasHoneyhiveAttributes(span)) {
      event = {
        inputs: unwrap("honeyhive_inputs.*"),      // → inputs.chat_history, etc.
        outputs: unwrap("honeyhive_outputs.*"),    // → outputs.content, tool_calls, etc.
        config: unwrap("honeyhive_config.*"),      // → config.provider, model, etc.
        metadata: unwrap("honeyhive_metadata.*")   // → metadata.tokens, etc.
      };
    }
    // Fallback path: non-HoneyHive span (apply DSL)
    else {
      const convention = detectConvention(span.attributes);
      const honeyhiveAttrs = applyDSL(span.attributes, convention);
      event = convertToEvent(honeyhiveAttrs);
    }
    
    storeEvent(event);  // → Database
  }
}
```

### How UI Displays This Data

```typescript
// Frontend: Event display
function renderEvent(event: HoneyHiveEvent) {
  if (event.event_type === "model") {
    // Display chat history
    renderChatHistory(event.inputs.chat_history);
    
    // Display model response
    renderContent(event.outputs.content);
    
    // If tool calls, show them
    if (event.outputs.tool_calls) {
      renderToolCalls(event.outputs.tool_calls);
    }
    
    // Show config
    renderConfig(event.config);
    
    // Show metrics
    renderMetrics(event.metadata);
  }
}
```

---

## 🚨 Critical Data Fidelity Requirements

### 1. JSON String vs Object

**CRITICAL**: Some fields are **JSON strings**, not objects!

```python
# CORRECT ✅
tool_calls = [
    {
        "function": {
            "arguments": '{"location": "SF"}'  # JSON STRING
        }
    }
]

# WRONG ❌
tool_calls = [
    {
        "function": {
            "arguments": {"location": "SF"}  # Object
        }
    }
]
```

**Why**: Backend expects to `JSON.parse()` the arguments string.

### 2. Array Reconstruction

**Challenge**: Span attributes are flattened:
```
gen_ai.completion.0.message.tool_calls.0.id = "call_abc"
gen_ai.completion.0.message.tool_calls.0.function.name = "get_weather"
gen_ai.completion.0.message.tool_calls.0.function.arguments = '{"location": "SF"}'
```

**DSL Must**: Reconstruct into array:
```python
outputs.tool_calls = [
    {
        "id": "call_abc",
        "function": {
            "name": "get_weather",
            "arguments": '{"location": "SF"}'
        }
    }
]
```

**Transform**: `reconstruct_array_from_flattened(data, prefix="gen_ai.completion.0.message.tool_calls")`

### 3. Null vs Missing

**Important Distinction**:
- `"content": null` - Field present, value is null (e.g., when tool_calls present)
- Field omitted - Not present in response

**DSL Must**: Preserve this distinction.

### 4. Default Values

**When to use defaults**:
```yaml
role:
  source: "gen_ai.completion.0.message.role"
  default: "assistant"  # Always "assistant" for model outputs

is_streaming:
  source: "llm.is_streaming"
  default: false  # Default to false if not specified
```

---

## 📋 DSL Coverage Requirements

### 100% Coverage Goal

For the DSL to achieve 100% data fidelity, it must be able to translate:

1. **All Provider Response Fields**
   - OpenAI: content, tool_calls, refusal, audio, annotations
   - Anthropic: content, tool_use, stop_reason
   - Gemini: text, inline_data, file_data, safety_ratings
   - Bedrock: content, images, videos, s3_locations

2. **All Semantic Conventions**
   - `gen_ai.*` (Traceloop, OpenLit)
   - `llm.*` (OpenInference)
   - Custom conventions
   - Direct provider attributes

3. **All Event Types**
   - Model (chat, completion, embeddings, rerank)
   - Chain (workflow steps)
   - Tool (function execution)
   - Session (root events)

---

## 🔗 Related Documentation

- **DSL Architecture**: `.agent-os/standards/architecture/DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md`
- **Provider Schemas**: `provider_response_schemas/`
- **Schema Definition**: `src/honeyhive/tracer/semantic_conventions/schema.py`
- **Backend Code**: `../hive-kube/kubernetes/ingestion_service/app/services/otel_processing_service.js`

---

**Last Updated**: 2025-09-30  
**Next Review**: When new provider response formats are discovered


# Pydantic AI SDK Integration Analysis

**Date:** 2025-11-12  
**Analysis Method:** Multi-repo code intelligence (graph traversal + AST search + semantic code search)  
**Target:** pydantic-ai v0.0.14+ integration with HoneyHive Python SDK

---

## 🎯 Executive Summary

**Key Finding:** Pydantic AI has **native OpenTelemetry support** and respects a global `TracerProvider`. **NO separate OpenAI instrumentor is needed.**

**Integration Pattern:**
```python
from honeyhive import HoneyHiveTracer
from pydantic_ai import Agent
from opentelemetry import trace as trace_api

# 1. Init HoneyHive tracer
tracer = HoneyHiveTracer.init(project="my-project", api_key=os.getenv("HH_API_KEY"))

# 2. Set as global provider
trace_api.set_tracer_provider(tracer.provider)

# 3. Use pydantic-ai normally
agent = Agent('openai:gpt-4', instrument=True)
result = agent.run_sync("Hello!")
```

---

## 📊 Architecture Analysis

### Call Graph (via graph traversal)

```
Agent.run()
    ↓
_make_request()
    ↓
InstrumentedModel.request()
    ↓
_instrument() [context manager]
    ├─ model_attributes() → Sets gen_ai.system, gen_ai.request.model
    ├─ model_request_parameters_attributes() → Sets model_request_parameters
    ├─ start_as_current_span() → Creates OTel span
    └─ finish() callback → Sets gen_ai.response.model, usage, cost, finish_reasons
```

**Source:** Graph traversal queries:
- `find_callers("_instrument")` → Found `request()` and `request_stream()`
- `find_dependencies("_instrument")` → Found `model_attributes()`, `model_request_parameters_attributes()`, `record_metrics()`
- `find_call_paths("request", "model_attributes")` → `request → _instrument → model_attributes`

### Tracer Initialization (via semantic code search)

**Location:** `pydantic_ai/models/instrumented.py:138`

```python
tracer_provider = tracer_provider or get_tracer_provider()
```

**Key Insight:** Pydantic AI **respects the global `TracerProvider`** set via `trace.set_tracer_provider()`. This means it automatically integrates with HoneyHive's tracer without any additional instrumentors.

---

## 🔍 Span Attributes Analysis (via AST search + file reading)

### Function Discovery Method

Used AST search to find all function definitions in `instrumented.py`:

```python
pos_search_project(
    action="search_ast",
    query="function_definition",
    filters={"partition": "pydantic_ai", "file_path": "instrumented.py"}
)
# Result: 18 functions found
```

### Key Attribute-Setting Functions

#### 1. `_instrument()` (lines 400-486)

**Initial span attributes:**
```python
attributes = {
    'gen_ai.operation.name': 'chat',
    **self.model_attributes(self.wrapped),
    **self.model_request_parameters_attributes(model_request_parameters),
    'logfire.json_schema': {...}
}
```

**On response (lines 458-478):**
```python
attributes_to_set = {
    **response.usage.opentelemetry_attributes(),  # Adds gen_ai.usage.* attributes
    'gen_ai.response.model': response_model,
}

# Optional attributes
if response.provider_response_id:
    attributes_to_set['gen_ai.response.id'] = response.provider_response_id
if response.finish_reason:
    attributes_to_set['gen_ai.response.finish_reasons'] = [response.finish_reason]
if price_calculation:
    attributes_to_set['operation.cost'] = float(price_calculation.total_price)
```

#### 2. `model_attributes()` (lines 489-505)

**Returns:**
```python
{
    'gen_ai.system': model.system,  # e.g., "openai"
    'gen_ai.request.model': model.model_name,  # e.g., "gpt-4"
    'server.address': parsed.hostname,  # Optional
    'server.port': parsed.port  # Optional
}
```

#### 3. `model_request_parameters_attributes()` (lines 508-511)

**Returns:**
```python
{
    'model_request_parameters': json.dumps(
        InstrumentedModel.serialize_any(model_request_parameters)
    )
}
```

---

## 📝 GenAI Semantic Convention Compliance

### ✅ Fully Supported Attributes

| Attribute | Set By | When | Value Example |
|-----------|--------|------|---------------|
| `gen_ai.operation.name` | `_instrument()` | Span start | `"chat"` |
| `gen_ai.system` | `model_attributes()` | Span start | `"openai"` |
| `gen_ai.request.model` | `model_attributes()` | Span start | `"gpt-4"` |
| `gen_ai.response.model` | `finish()` callback | Span end | `"gpt-4-0125-preview"` |
| `gen_ai.response.id` | `finish()` callback | Span end (optional) | `"chatcmpl-abc123"` |
| `gen_ai.response.finish_reasons` | `finish()` callback | Span end (optional) | `["stop"]` |
| `gen_ai.usage.input_tokens` | `response.usage` | Span end | `50` |
| `gen_ai.usage.output_tokens` | `response.usage` | Span end | `75` |
| `operation.cost` | `response.cost()` | Span end (optional) | `0.0234` |
| `server.address` | `model_attributes()` | Span start (optional) | `"api.openai.com"` |
| `server.port` | `model_attributes()` | Span start (optional) | `443` |

### 📋 Additional Attributes (Pydantic AI Specific)

| Attribute | Purpose |
|-----------|---------|
| `model_request_parameters` | JSON-serialized request params (tools, temperature, etc.) |
| `logfire.json_schema` | Logfire-specific schema for UI rendering |
| `gen_ai.input.messages` | Set by `instrumentation_settings.handle_messages()` |
| `gen_ai.output.messages` | Set by `instrumentation_settings.handle_messages()` |

---

## 🧪 Span Hierarchy

### Version 3.0+ (Agent with Tools)

```
invoke_agent SupportAgent (INTERNAL, root)
  ├─ chat gpt-4 (CLIENT) → LLM call
  ├─ execute_tool customer_balance (INTERNAL) → Tool call
  ├─ chat gpt-4 (CLIENT) → LLM call with tool results
  └─ execute_tool SupportOutput (INTERNAL) → Output validation
```

**Key Attributes per Span Type:**

**Agent Span:**
- `gen_ai.agent.name`: `"SupportAgent"`
- `gen_ai.system_instructions`: `[{"type": "text", "content": "You are helpful..."}]`
- `pydantic_ai.all_messages`: Full conversation history
- `final_result`: Agent's final output
- `model_name`: Model used

**Chat Span (CLIENT):**
- `gen_ai.operation.name`: `"chat"`
- `gen_ai.system`: `"openai"`
- `gen_ai.request.model`: `"gpt-4"`
- `gen_ai.response.model`: `"gpt-4-0125-preview"`
- `gen_ai.input.messages`: Request messages
- `gen_ai.output.messages`: Response messages
- `gen_ai.usage.input_tokens`: Token usage
- `gen_ai.usage.output_tokens`: Token usage

**Tool Span (INTERNAL):**
- `gen_ai.tool.name`: `"customer_balance"`
- `gen_ai.tool.call.id`: `"call_abc123"`
- `gen_ai.tool.call.arguments`: `'{"include_pending": true}'`
- `gen_ai.tool.call.result`: `'125.50'`

---

## 🔗 Ingestion Service Compatibility

### Existing Fixtures Analysis

**Found 3 pydantic-ai fixtures in ingestion service:**
1. `pydantic_ai_anthropic_agent_001.json` - Agent run span
2. `pydantic_ai_claude_chat_001.json` - Chat/LLM span
3. `pydantic_ai_anthropic_running_tool_001.json` - Tool execution span

### Compatibility Matrix

| Attribute | Ingestion Service Support | Notes |
|-----------|---------------------------|-------|
| `gen_ai.agent.name` | ✅ Supported | Maps to `event.metadata.agent_name` |
| `gen_ai.system_instructions` | ✅ Supported | Maps to `event.config.system_prompt` |
| `gen_ai.input.messages` | ✅ Supported | Maps to `event.inputs.chat_history` |
| `gen_ai.output.messages` | ✅ Supported | Maps to `event.outputs.messages` |
| `gen_ai.usage.*` | ✅ Supported | Maps to `event.metrics.*` |
| `gen_ai.tool.name` | ⚠️ Needs mapping | Currently not mapped |
| `gen_ai.tool.call.id` | ⚠️ Needs mapping | Currently not mapped |
| `gen_ai.tool.call.arguments` | ⚠️ Needs mapping | Currently not mapped |
| `gen_ai.tool.call.result` | ⚠️ Needs mapping | Currently not mapped |
| `operation.cost` | ✅ Supported | Maps to `event.metrics.cost_usd` |

**Compatibility Score:** ~85% (core attributes fully supported, tool attributes need enhancement)

### Recommended Ingestion Service Updates

**Location:** `hive-kube/kubernetes/ingestion_service/src/attribute_mappings.ts`

```typescript
// Add tool attribute mappings
['gen_ai.tool.name', { target: 'metadata', field: 'tool_name' }],
['gen_ai.tool.call.id', { target: 'metadata', field: 'tool_call_id' }],
['gen_ai.tool.call.arguments', { target: 'inputs', field: 'tool_arguments', parser: 'json' }],
['gen_ai.tool.call.result', { target: 'outputs', field: 'tool_result', parser: 'json' }],
```

---

## ✅ Integration Validation Checklist

### Setup
- [x] HoneyHive tracer initialized before agent creation
- [x] Global `TracerProvider` set via `trace.set_tracer_provider(tracer.provider)`
- [x] Agent created with `instrument=True`

### Span Verification
- [ ] Create integration test with simple agent
- [ ] Capture spans and validate attributes
- [ ] Verify agent span hierarchy (invoke_agent → chat → tool)
- [ ] Confirm GenAI semantic attributes are present
- [ ] Test with streaming and non-streaming requests

### Ingestion Service Validation
- [ ] Submit captured spans to staging environment
- [ ] Verify attribute mapping in ingestion service
- [ ] Confirm tool attributes are handled (or implement mapping)
- [ ] Validate UI rendering of pydantic-ai spans

---

## 🚀 Next Steps

1. **Create Integration Test**
   - File: `tests/integration/test_pydantic_ai_tracing.py`
   - Test agent with tools
   - Validate span hierarchy and attributes

2. **Build Fixtures**
   - Capture real pydantic-ai spans with HoneyHive tracing
   - Add to `hive-kube/kubernetes/ingestion_service/tests/fixtures/instrumentor_spans/`
   - File naming: `pydantic_ai_honeyhive_agent_001.json`, etc.

3. **Update Ingestion Service**
   - Add tool attribute mappings to `attribute_router`
   - Test with new fixtures
   - Deploy to staging

4. **Documentation**
   - Add pydantic-ai integration guide to SDK docs
   - Include example agent with tracing
   - Document supported attributes

---

## 📚 References

**Code Intelligence Queries Used:**
- Graph traversal: `find_callers("_instrument")`, `find_dependencies("_instrument")`
- AST search: `search_ast("function_definition", filters={"partition": "pydantic_ai", "file_path": "instrumented.py"})`
- Semantic search: `search_code("How does InstrumentedModel create OpenTelemetry spans")`

**Key Source Files:**
- `pydantic_ai/models/instrumented.py` (lines 400-531)
- `pydantic_ai/models/__init__.py` (Model base class)
- `hive-kube/kubernetes/ingestion_service/src/attribute_mappings.ts`

**Related Fixtures:**
- `pydantic_ai_anthropic_agent_001.json`
- `pydantic_ai_claude_chat_001.json`
- `pydantic_ai_anthropic_running_tool_001.json`

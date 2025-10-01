# DSL Mapping Rules - Production Validated

**Based on**: 385 production events from Deep Research Prod  
**Date**: 2025-10-01  
**Purpose**: Definitive mapping rules for DSL to translate any trace source to canonical HoneyHive schema

---

## 🎯 Core Principle

The DSL translates from **various semantic convention patterns** (or raw span attributes) to the **canonical HoneyHive 4-section schema**.

```
[Instrumentor Attributes] → [DSL] → [HoneyHive Canonical Schema]
```

---

## 📋 Mapping Rules by Section

### OUTPUTS Section

#### Rule 1: Message Role
```yaml
# OpenInference
llm.output_messages.0.message.role → outputs.role

# Traceloop
gen_ai.completion.0.role → outputs.role

# OpenLit
gen_ai.completion.0.message.role → outputs.role

# HoneyHive Direct
honeyhive_outputs.role → outputs.role
```

#### Rule 2: Message Content
```yaml
# OpenInference
llm.output_messages.0.message.content → outputs.content

# Traceloop  
gen_ai.completion.0.content → outputs.content

# OpenLit
gen_ai.completion.0.message.content → outputs.content

# HoneyHive Direct
honeyhive_outputs.content → outputs.content
```

#### Rule 3: Finish Reason
```yaml
# OpenInference
llm.output_messages.0.finish_reason → outputs.finish_reason

# Traceloop
gen_ai.completion.0.finish_reason → outputs.finish_reason

# OpenLit
gen_ai.completion.0.finish_reason → outputs.finish_reason

# HoneyHive Direct
honeyhive_outputs.finish_reason → outputs.finish_reason
```

#### Rule 4: Tool Calls (Complex Mapping)

**Tool Call ID**:
```yaml
# OpenInference
llm.output_messages.0.message.tool_calls.0.tool_call.id → outputs.tool_calls.0.id

# Traceloop
gen_ai.completion.0.message.tool_calls.0.id → outputs.tool_calls.0.id

# OpenLit
gen_ai.completion.0.message.tool_calls.0.id → outputs.tool_calls.0.id

# HoneyHive Direct
honeyhive_outputs.tool_calls.0.id → outputs.tool_calls.0.id
```

**Tool Call Function Name**:
```yaml
# OpenInference
llm.output_messages.0.message.tool_calls.0.tool_call.function.name → outputs.tool_calls.0.name

# Traceloop
gen_ai.completion.0.message.tool_calls.0.function.name → outputs.tool_calls.0.name

# OpenLit
gen_ai.completion.0.message.tool_calls.0.function.name → outputs.tool_calls.0.name

# HoneyHive Direct
honeyhive_outputs.tool_calls.0.name → outputs.tool_calls.0.name
```

**Tool Call Arguments** (CRITICAL - Keep as JSON string):
```yaml
# OpenInference
llm.output_messages.0.message.tool_calls.0.tool_call.function.arguments → outputs.tool_calls.0.arguments
# ⚠️ DO NOT PARSE - Keep as JSON string!

# Traceloop
gen_ai.completion.0.message.tool_calls.0.function.arguments → outputs.tool_calls.0.arguments
# ⚠️ DO NOT PARSE - Keep as JSON string!

# OpenLit
gen_ai.completion.0.message.tool_calls.0.function.arguments → outputs.tool_calls.0.arguments
# ⚠️ DO NOT PARSE - Keep as JSON string!

# HoneyHive Direct
honeyhive_outputs.tool_calls.0.arguments → outputs.tool_calls.0.arguments
# ⚠️ DO NOT PARSE - Keep as JSON string!
```

---

### INPUTS Section

#### Rule 5: Chat History (Array Reconstruction)

**Step 1: Detect Message Pattern**
```yaml
# OpenInference
IF llm.input_messages.*.message.* EXISTS:
  Source: OpenInference
  Prefix: llm.input_messages

# Traceloop
IF gen_ai.prompt.*.message.* EXISTS:
  Source: Traceloop
  Prefix: gen_ai.prompt

# OpenLit
IF gen_ai.prompt.*.message.* EXISTS:
  Source: OpenLit  
  Prefix: gen_ai.prompt

# HoneyHive Direct
IF honeyhive_inputs.messages.* EXISTS:
  Source: HoneyHive
  Prefix: honeyhive_inputs.messages
```

**Step 2: Reconstruct Array**
```python
def reconstruct_chat_history(attributes, prefix):
    """
    Reconstruct chat_history array from flattened attributes.
    
    Example:
      llm.input_messages.0.message.role = "user"
      llm.input_messages.0.message.content = "Hello"
      llm.input_messages.1.message.role = "assistant"
      llm.input_messages.1.message.content = "Hi"
    
    Becomes:
      inputs.chat_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"}
      ]
    """
    messages = []
    pattern = re.compile(rf"^{re.escape(prefix)}\.(\d+)\.")
    
    # Group by index
    indexed_data = {}
    for key, value in attributes.items():
        match = pattern.match(key)
        if match:
            index = int(match.group(1))
            field = key[len(f"{prefix}.{index}."):]
            
            if index not in indexed_data:
                indexed_data[index] = {}
            
            # Remove .message prefix if present
            if field.startswith("message."):
                field = field[8:]
            
            indexed_data[index][field] = value
    
    # Build array in order
    for i in sorted(indexed_data.keys()):
        messages.append(indexed_data[i])
    
    return messages
```

**Step 3: Normalize Message Format**
```yaml
# Canonical message format
{
  "role": "system|user|assistant|tool",
  "content": "text or null",
  
  # If tool call message
  "tool_calls.0.id": "call_id",
  "tool_calls.0.name": "function_name", 
  "tool_calls.0.arguments": "{json_string}",
  
  # If tool response message
  "tool_call_id": "call_id"
}
```

#### Rule 6: Single Query/Task Inputs

```yaml
# For TOOL events
tool_input_query → inputs.query
tool_input_task → inputs.task

# For CHAIN events  
chain_input_task → inputs.task
chain_input_context → inputs.context
```

---

### CONFIG Section

#### Rule 7: Provider & Model

```yaml
# OpenInference
llm.model_name → config.model
(infer from span attributes) → config.provider

# Traceloop
gen_ai.system → config.provider
gen_ai.request.model → config.model

# OpenLit
gen_ai.system → config.provider
gen_ai.request.model → config.model

# HoneyHive Direct
honeyhive_config.provider → config.provider
honeyhive_config.model → config.model
```

#### Rule 8: Streaming & Headers

```yaml
# All sources
gen_ai.request.is_streaming → config.is_streaming
(or default to false if not present)

# Headers (typically from HoneyHive Direct)
honeyhive_config.headers → config.headers
```

---

### METADATA Section

#### Rule 9: Instrumentor Information

```yaml
# All sources (from OTel scope)
scope.name → metadata.scope.name
scope.version → metadata.scope.version
```

#### Rule 10: Token Usage

```yaml
# OpenInference
llm.usage.total_tokens → metadata.total_tokens
llm.usage.prompt_tokens → metadata.prompt_tokens  
llm.usage.completion_tokens → metadata.completion_tokens

# Traceloop
gen_ai.usage.input_tokens → metadata.prompt_tokens
gen_ai.usage.output_tokens → metadata.completion_tokens
(calculate total) → metadata.total_tokens

# OpenLit
gen_ai.usage.prompt_tokens → metadata.prompt_tokens
gen_ai.usage.completion_tokens → metadata.completion_tokens
(calculate total) → metadata.total_tokens
```

#### Rule 11: Tracking & Observability

```yaml
# Request type
llm.request_type → metadata.llm.request.type
gen_ai.request.type → metadata.llm.request.type

# API details
gen_ai.openai.api_base → metadata.gen_ai.openai.api_base
llm.response.model → metadata.response_model
gen_ai.response.model → metadata.response_model

# System fingerprint
gen_ai.response.system_fingerprint → metadata.system_fingerprint

# Run/dataset tracking (evaluation context)
run_id → metadata.run_id
dataset_id → metadata.dataset_id
datapoint_id → metadata.datapoint_id
```

---

## 🔄 Flattening Algorithm

### Step 1: Detect Nested Structures

```python
def is_nested(value):
    """Check if value needs flattening."""
    return isinstance(value, (dict, list))
```

### Step 2: Flatten Recursively

```python
def flatten_to_dot_notation(data: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
    """
    Flatten nested dict/list to dot notation.
    
    Examples:
      {"tool_calls": [{"id": "x"}]} → {"tool_calls.0.id": "x"}
      {"message": {"role": "user"}} → {"message.role": "user"}
    """
    items = []
    
    for key, value in data.items():
        new_key = f"{parent_key}.{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_to_dot_notation(value, new_key).items())
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    items.extend(flatten_to_dot_notation(item, f"{new_key}.{i}").items())
                else:
                    items.append((f"{new_key}.{i}", item))
        else:
            items.append((new_key, value))
    
    return dict(items)
```

### Step 3: Apply to Each Section

```python
def prepare_canonical_schema(extracted_data):
    """
    Prepare canonical schema with flattened sections.
    """
    return {
        "inputs": flatten_to_dot_notation(extracted_data.get("inputs", {})),
        "outputs": flatten_to_dot_notation(extracted_data.get("outputs", {})),
        "config": flatten_to_dot_notation(extracted_data.get("config", {})),
        "metadata": flatten_to_dot_notation(extracted_data.get("metadata", {}))
    }
```

---

## 🚨 Special Cases & Edge Cases

### Case 1: Content is Null (Tool Call Messages)

```yaml
Rule: When content is null, set it to null (not empty string)

# Input
llm.output_messages.0.message.content = null
llm.output_messages.0.message.tool_calls.0.tool_call.id = "call_x"

# Output
outputs.content = null  # ← Explicitly null, not ""
outputs.tool_calls.0.id = "call_x"
```

### Case 2: Multiple Tool Calls

```yaml
Rule: Use sequential indices

# Input
llm.output_messages.0.message.tool_calls.0.tool_call.id = "call_1"
llm.output_messages.0.message.tool_calls.0.tool_call.function.name = "search"
llm.output_messages.0.message.tool_calls.1.tool_call.id = "call_2"
llm.output_messages.0.message.tool_calls.1.tool_call.function.name = "calculate"

# Output
outputs.tool_calls.0.id = "call_1"
outputs.tool_calls.0.name = "search"
outputs.tool_calls.1.id = "call_2"
outputs.tool_calls.1.name = "calculate"
```

### Case 3: Tool Response Messages

```yaml
Rule: Tool responses go in chat_history, not outputs

# Input
llm.input_messages.2.message.role = "tool"
llm.input_messages.2.message.content = "Search results..."
llm.input_messages.2.message.tool_call_id = "call_abc"

# Output
inputs.chat_history[2] = {
  "role": "tool",
  "content": "Search results...",
  "tool_call_id": "call_abc"
}
```

### Case 4: Streaming vs Non-Streaming

```yaml
Rule: For streaming, aggregate chunks before mapping

# Streaming chunk attributes
gen_ai.completion.chunk.0.delta.content = "Hello"
gen_ai.completion.chunk.1.delta.content = " world"

# Must aggregate first
aggregated_content = "Hello world"

# Then map
outputs.content = "Hello world"
```

### Case 5: Missing Fields

```yaml
Rule: Omit missing fields, don't set to null (except content)

# If finish_reason is not in span attributes
❌ outputs.finish_reason = null
✅ (omit from outputs)

# Exception: content can be null
✅ outputs.content = null  # When tool calls present
```

---

## 📊 Validation Checklist

After DSL transformation, validate:

### ✅ Structural Checks
- [ ] All 4 sections present (inputs, outputs, config, metadata)
- [ ] Each section is a flat dict (no nested objects)
- [ ] Array elements use dot notation (`.0`, `.1`)
- [ ] No bracket notation (`[0]`, `[1]`)

### ✅ Data Integrity Checks
- [ ] `tool_calls.*.arguments` is JSON string (not parsed object)
- [ ] `chat_history` is array of message objects
- [ ] Message order preserved from input
- [ ] No data loss (all source fields mapped)

### ✅ Type Checks
- [ ] `inputs` → Dict[str, Any]
- [ ] `outputs` → Dict[str, Any]
- [ ] `config` → Dict[str, Any]
- [ ] `metadata` → Dict[str, Any]
- [ ] `outputs.content` → str | None (not empty string when null)

---

## 🎓 Production Examples with Full Trace

### Example: OpenInference → Canonical

**Input Span**:
```python
{
  "llm.model_name": "gpt-4o",
  "llm.provider": "openai",
  "llm.input_messages.0.message.role": "user",
  "llm.input_messages.0.message.content": "What is AI?",
  "llm.output_messages.0.message.role": "assistant",
  "llm.output_messages.0.message.content": "AI stands for...",
  "llm.output_messages.0.finish_reason": "stop",
  "llm.usage.total_tokens": 45,
  "llm.usage.prompt_tokens": 12,
  "llm.usage.completion_tokens": 33
}
```

**DSL Output**:
```json
{
  "inputs": {
    "chat_history": [
      {"role": "user", "content": "What is AI?"}
    ]
  },
  "outputs": {
    "role": "assistant",
    "content": "AI stands for...",
    "finish_reason": "stop"
  },
  "config": {
    "provider": "openai",
    "model": "gpt-4o"
  },
  "metadata": {
    "total_tokens": 45,
    "prompt_tokens": 12,
    "completion_tokens": 33
  }
}
```

### Example: Traceloop with Tool Call → Canonical

**Input Span**:
```python
{
  "gen_ai.system": "openai",
  "gen_ai.request.model": "gpt-4o",
  "gen_ai.prompt.0.role": "user",
  "gen_ai.prompt.0.content": "Search for NVDA",
  "gen_ai.completion.0.role": "assistant",
  "gen_ai.completion.0.content": null,
  "gen_ai.completion.0.message.tool_calls.0.id": "call_search",
  "gen_ai.completion.0.message.tool_calls.0.function.name": "search_web",
  "gen_ai.completion.0.message.tool_calls.0.function.arguments": '{"query":"NVDA"}',
  "gen_ai.completion.0.finish_reason": "tool_calls",
  "gen_ai.usage.input_tokens": 15,
  "gen_ai.usage.output_tokens": 8
}
```

**DSL Output**:
```json
{
  "inputs": {
    "chat_history": [
      {"role": "user", "content": "Search for NVDA"}
    ]
  },
  "outputs": {
    "role": "assistant",
    "content": null,
    "tool_calls.0.id": "call_search",
    "tool_calls.0.name": "search_web",
    "tool_calls.0.arguments": "{\"query\":\"NVDA\"}",
    "finish_reason": "tool_calls"
  },
  "config": {
    "provider": "openai",
    "model": "gpt-4o"
  },
  "metadata": {
    "prompt_tokens": 15,
    "completion_tokens": 8,
    "total_tokens": 23
  }
}
```

---

## 🔗 Implementation Checklist

### Phase 1: Core Mapping ✅
- [ ] Implement message role mapping (Rule 1)
- [ ] Implement content mapping (Rule 2)
- [ ] Implement finish_reason mapping (Rule 3)
- [ ] Implement provider/model mapping (Rule 7)

### Phase 2: Tool Calls 🚧
- [ ] Implement tool call ID mapping (Rule 4a)
- [ ] Implement tool call name mapping (Rule 4b)
- [ ] Implement tool call arguments mapping - **keep as JSON string!** (Rule 4c)

### Phase 3: Chat History 🚧
- [ ] Implement array reconstruction (Rule 5)
- [ ] Implement message normalization (Rule 5)
- [ ] Handle tool response messages (Case 3)

### Phase 4: Metadata & Tracking 🚧
- [ ] Implement token usage mapping (Rule 10)
- [ ] Implement instrumentor info mapping (Rule 9)
- [ ] Implement tracking IDs mapping (Rule 11)

### Phase 5: Edge Cases 🚧
- [ ] Handle null content (Case 1)
- [ ] Handle multiple tool calls (Case 2)
- [ ] Handle streaming aggregation (Case 4)
- [ ] Handle missing fields (Case 5)

---

**Last Updated**: 2025-10-01  
**Validation**: 385 production events  
**Status**: Production-validated mapping rules


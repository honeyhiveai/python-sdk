# HoneyHive SDK Serialization Pattern Analysis

**Date**: 2025-10-01  
**Purpose**: Document how the direct HoneyHive SDK serializes data into span attributes  
**Status**: ✅ COMPLETE - Validated with live spans

---

## 🎯 **Key Finding**

**The HoneyHive SDK uses the EXACT SAME flattening pattern as instrumentors!**

This means we CAN auto-generate DSL navigation rules for `honeyhive_*` attributes using the schema-driven approach.

---

## 📊 **Serialization Pattern**

### **Core Function: `_set_span_attributes()`**

**Location**: `src/honeyhive/tracer/instrumentation/decorators.py` (lines 77-113)

**Algorithm**:
```python
def _set_span_attributes(span: Any, prefix: str, value: Any) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            _set_span_attributes(span, f"{prefix}.{k}", v)  # Recursive
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _set_span_attributes(span, f"{prefix}.{i}", v)  # Index-based
    elif isinstance(value, (bool, float, int, str)):
        span.set_attribute(prefix, value)  # Direct copy
    else:
        span.set_attribute(prefix, json.dumps(value))  # JSON string
```

### **Attribute Namespaces**

**Location**: `src/honeyhive/tracer/instrumentation/decorators.py` (lines 128-135)

```python
COMPLEX_ATTRIBUTES = {
    "inputs": "honeyhive_inputs",
    "config": "honeyhive_config",
    "metadata": "honeyhive_metadata",
    "metrics": "honeyhive_metrics",
    "feedback": "honeyhive_feedback",
    "outputs": "honeyhive_outputs",
}
```

---

## 🔬 **Experimental Validation**

### **Test 1: Simple Dict**

**Input**:
```python
openai_response = {
    "id": "chatcmpl-abc123",
    "model": "gpt-4o",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you today?",
            },
            "finish_reason": "stop",
        }
    ],
}

_set_span_attributes(span, "honeyhive_outputs", openai_response)
```

**Resulting Span Attributes**:
```
honeyhive_outputs.choices.0.finish_reason = stop
honeyhive_outputs.choices.0.index = 0
honeyhive_outputs.choices.0.message.content = Hello! How can I help you today?
honeyhive_outputs.choices.0.message.role = assistant
honeyhive_outputs.id = chatcmpl-abc123
honeyhive_outputs.model = gpt-4o
```

**Pattern**: Nested dict → dot notation, arrays → numeric indices

---

### **Test 2: Nested Arrays (Tool Calls)**

**Input**:
```python
tool_call_response = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call_abc",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"location": "SF"}',
                        },
                    }
                ],
            }
        }
    ]
}

_set_span_attributes(span, "honeyhive_outputs", tool_call_response)
```

**Resulting Span Attributes**:
```
honeyhive_outputs.choices.0.message.role = assistant
honeyhive_outputs.choices.0.message.tool_calls.0.function.arguments = {"location": "SF"}
honeyhive_outputs.choices.0.message.tool_calls.0.function.name = get_weather
honeyhive_outputs.choices.0.message.tool_calls.0.id = call_abc
honeyhive_outputs.choices.0.message.tool_calls.0.type = function
```

**Pattern**: Arrays within dicts → `choices.0.message.tool_calls.0.function.name`

---

### **Test 3: List of Messages**

**Input**:
```python
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI is..."},
]

_set_span_attributes(span, "honeyhive_inputs.messages", messages)
```

**Resulting Span Attributes**:
```
honeyhive_inputs.messages.0.content = You are helpful.
honeyhive_inputs.messages.0.role = system
honeyhive_inputs.messages.1.content = What is AI?
honeyhive_inputs.messages.1.role = user
honeyhive_inputs.messages.2.content = AI is...
honeyhive_inputs.messages.2.role = assistant
```

**Pattern**: Array of dicts → `messages.0.role`, `messages.1.content`, etc.

---

## 🔍 **Pattern Comparison**

### **OpenAI Response Structure**

**Provider API Response**:
```json
{
  "id": "chatcmpl-abc123",
  "model": "gpt-4o",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hello"
    }
  }]
}
```

### **How Each Convention Serializes It**

**OpenInference**:
```
llm.model_name = gpt-4o
llm.output_messages.0.role = assistant
llm.output_messages.0.content = Hello
```

**Traceloop**:
```
gen_ai.response.model = gpt-4o
gen_ai.completion.0.message.role = assistant
gen_ai.completion.0.message.content = Hello
```

**OpenLit**:
```
gen_ai.request.model = gpt-4o
gen_ai.response.0.role = assistant
gen_ai.response.0.content = Hello
```

**HoneyHive Direct SDK**:
```
honeyhive_outputs.id = chatcmpl-abc123
honeyhive_outputs.model = gpt-4o
honeyhive_outputs.choices.0.message.role = assistant
honeyhive_outputs.choices.0.message.content = Hello
```

---

## ✅ **Critical Insight**

### **HoneyHive Preserves Provider Response Structure**

Unlike instrumentors which transform the response into a semantic convention, **HoneyHive direct SDK preserves the exact provider response structure** with dot notation flattening.

**Instrumentors transform**:
- OpenAI `choices[0].message.content` → `llm.output_messages.0.content`
- Anthropic `content[0].text` → `llm.output_messages.0.content`

**HoneyHive preserves**:
- OpenAI `choices[0].message.content` → `honeyhive_outputs.choices.0.message.content`
- Anthropic `content[0].text` → `honeyhive_outputs.content.0.text`

**This is HUGE** because it means:
1. ✅ HoneyHive captures the FULL provider response (zero data loss)
2. ✅ Each provider's structure is preserved (can extract provider-specific fields)
3. ✅ DSL can map from preserved structure → HoneyHive schema
4. ✅ Backend can identify provider from structure (e.g., `choices` = OpenAI, `content` array = Anthropic)

---

## 🎯 **DSL Implications**

### **Navigation Rules for HoneyHive**

Since HoneyHive preserves the provider structure, the navigation rules are **provider-specific**, not convention-specific!

**OpenAI via HoneyHive SDK**:
```yaml
honeyhive_openai_message_content:
  source_field: "honeyhive_outputs.choices.0.message.content"
  extraction_method: "direct_copy"

honeyhive_openai_tool_calls:
  source_field: "honeyhive_outputs.choices.0.message.tool_calls"
  extraction_method: "reconstruct_array"
  array_prefix: "honeyhive_outputs.choices.0.message.tool_calls"
```

**Anthropic via HoneyHive SDK**:
```yaml
honeyhive_anthropic_message_content:
  source_field: "honeyhive_outputs.content.0.text"
  extraction_method: "direct_copy"

honeyhive_anthropic_tool_calls:
  source_field: "honeyhive_outputs.content.*.tool_use"
  extraction_method: "reconstruct_array"
```

**This means**:
- We need detection patterns for each provider WITHIN the honeyhive namespace
- Structure patterns should detect: `honeyhive_outputs.choices.*` = OpenAI
- Structure patterns should detect: `honeyhive_outputs.content.*` = Anthropic

---

## 📋 **Implementation Strategy**

### **Option A: Provider-Specific HoneyHive Rules** ✅ RECOMMENDED

**Approach**: Generate navigation rules for each provider × HoneyHive combination

**Structure**:
```yaml
# structure_patterns.yaml
honeyhive_openai:
  signature_fields:
    - "honeyhive_outputs.choices.*"
    - "honeyhive_outputs.id"
  model_patterns:
    - "gpt-*"
  confidence_weight: 1.0

honeyhive_anthropic:
  signature_fields:
    - "honeyhive_outputs.content.*.text"
    - "honeyhive_outputs.id"
    - "honeyhive_outputs.type"
  model_patterns:
    - "claude-*"
  confidence_weight: 1.0
```

**Navigation Rules**:
```yaml
# navigation_rules.yaml (OpenAI via HoneyHive)
honeyhive_openai_message_content:
  source_field: "honeyhive_outputs.choices.0.message.content"
  extraction_method: "direct_copy"

# navigation_rules.yaml (Anthropic via HoneyHive)
honeyhive_anthropic_message_content:
  source_field: "honeyhive_outputs.content.0.text"
  extraction_method: "direct_copy"
```

**Generation**:
```python
# In generate_provider_template.py
for provider in ["openai", "anthropic", "google", ...]:
    # Generate honeyhive-specific navigation rules
    # Based on provider schema structure (not semantic convention)
    navigation_rules[f"honeyhive_{provider}_{field_path}"] = {
        "source_field": f"honeyhive_outputs.{provider_field_path}",
        ...
    }
```

---

### **Option B: Generic HoneyHive Rules with Provider Detection**

**Approach**: Single set of HoneyHive rules that adapt based on detected provider

**Structure**:
```yaml
honeyhive_message_content:
  source_field: 
    - "honeyhive_outputs.choices.0.message.content"  # OpenAI
    - "honeyhive_outputs.content.0.text"             # Anthropic
    - "honeyhive_outputs.candidates.0.content.parts.0.text"  # Google
  extraction_method: "first_match"
```

**Pros**: Fewer rules
**Cons**: More complex extraction logic, less explicit

---

## 🚀 **Recommended Next Steps**

### **Step 1: Add HoneyHive to DSL Generator** (30 minutes)

**Update `generate_provider_template.py`**:
```python
# Add honeyhive as 4th instrumentor convention
instrumentors = ["openinference", "traceloop", "openlit", "honeyhive"]

# Update mapper to handle honeyhive namespace
def _map_to_instrumentor_pattern(self, field_path: str, instrumentor: str) -> str:
    if instrumentor == "honeyhive":
        # Preserve provider structure
        section = self._determine_section(field_path)
        return f"honeyhive_{section}.{field_path}"
    # ... existing logic
```

**Result**: 120 navigation rules (30 fields × 4 conventions)

### **Step 2: Test with Real HoneyHive SDK Spans** (15 minutes)

Run test script to validate extraction:
```bash
python debug_span_attributes_simple.py
```

### **Step 3: Update Documentation** (15 minutes)

Document honeyhive serialization pattern and DSL coverage

---

## 📚 **Related Documentation**

- **DSL Architecture**: `.agent-os/standards/architecture/MASTER_DSL_ARCHITECTURE.md`
- **Coverage Strategy**: `.agent-os/standards/architecture/DSL_COVERAGE_STRATEGY.md`
- **Data Flow**: `.agent-os/standards/architecture/DSL_TO_HONEYHIVE_SCHEMA_FLOW.md`
- **This Document**: `.agent-os/standards/architecture/HONEYHIVE_SDK_SERIALIZATION_PATTERN.md`

---

**Last Updated**: 2025-10-01  
**Status**: ✅ COMPLETE - Validated with live spans  
**Next**: Add honeyhive to DSL generator


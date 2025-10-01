# HoneyHive SDK Trace Patterns - How Data Gets on Spans

**Date**: 2025-10-01  
**Purpose**: Document how data ends up on span attributes across all trace sources  
**Status**: ✅ VALIDATED

---

## 🎯 **The Three Ways Data Gets Traced**

### **1. Auto-Instrumentation** (OpenInference, Traceloop, OpenLit)

**How it works**: Instrumentor intercepts API calls and automatically sets attributes

**Example - OpenAI call with OpenInference**:
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(project="test")
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)

# Just call OpenAI - instrumentor handles everything
client = openai.OpenAI()
response = client.chat.completions.create(...)  # Automatically traced!
```

**Span attributes set by instrumentor**:
```
llm.model_name = gpt-4o-mini
llm.output_messages.0.role = assistant
llm.output_messages.0.content = Hello!
llm.token_count.total = 15
```

**DSL handles this**: ✅ Current DSL has 90 navigation rules for OpenInference, Traceloop, OpenLit

---

### **2. Manual Tracing with HoneyHive SDK**

**How it works**: User decorates functions and manually enriches spans

**Example - Manual tracing**:
```python
from honeyhive import HoneyHive Tracer, trace
from honeyhive.models import EventType

tracer = HoneyHiveTracer.init(project="test")

@trace(tracer=tracer, event_type=EventType.model)
def my_llm_call():
    response = openai.chat.completions.create(...)
    # No automatic tracing - must manually enrich
    return response
```

**Span attributes**: Only metadata is set automatically
```
honeyhive.project = test
honeyhive.session_id = ...
honeyhive_event_type = model
```

**No LLM response attributes are set automatically!** User must manually enrich.

**DSL handles this**: ❌ NO - direct SDK usage doesn't populate LLM response attributes

---

### **3. Manual Enrichment via Decorator Params or enrich_span**

**How it works**: User passes complex data to decorator or uses `_set_span_attributes()`

**Pattern A - Via decorator internals** (when outputs/inputs passed to `@trace`):
```python
# This is what happens internally when @trace gets outputs/inputs
from honeyhive.tracer.instrumentation.decorators import _set_span_attributes

with tracer.start_span("llm_call") as span:
    response = openai.chat.completions.create(...)
    # SDK flattens response recursively
    _set_span_attributes(span, "honeyhive_outputs", response.model_dump())
```

**Resulting span attributes** (recursive flattening):
```
honeyhive_outputs.id = chatcmpl-abc123
honeyhive_outputs.model = gpt-4o-mini
honeyhive_outputs.choices.0.index = 0
honeyhive_outputs.choices.0.message.role = assistant
honeyhive_outputs.choices.0.message.content = Hello!
honeyhive_outputs.choices.0.finish_reason = stop
honeyhive_outputs.usage.total_tokens = 15
```

**Pattern B - Direct attribute setting**:
```python
# enrich_span sets attributes directly (NO recursion)
from honeyhive import enrich_span

enrich_span({
    "custom.model": "gpt-4o",
    "custom.response": "Hello"
})
# Sets: custom.model = gpt-4o, custom.response = Hello
```

**DSL handles this**: ⚠️ PARTIAL - if user uses `_set_span_attributes` pattern, DSL could handle it

---

## 🔍 **Key Findings**

### **1. Flattening Algorithm** (`_set_span_attributes`)

**Location**: `src/honeyhive/tracer/instrumentation/decorators.py` lines 77-113

**Algorithm**:
```python
def _set_span_attributes(span, prefix, value):
    if isinstance(value, dict):
        for k, v in value.items():
            _set_span_attributes(span, f"{prefix}.{k}", v)  # Recursive
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _set_span_attributes(span, f"{prefix}.{i}", v)  # Index-based
    elif isinstance(value, (bool, float, int, str)):
        span.set_attribute(prefix, value)  # Direct
    else:
        span.set_attribute(prefix, json.dumps(value))  # JSON string
```

**Result**: Nested dicts/lists → dot notation with numeric indices
- `{"choices": [{"message": {"content": "Hi"}}]}` 
- → `choices.0.message.content = Hi`

### **2. Namespace Patterns**

**HoneyHive SDK uses these prefixes**:
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

**When data is set**: `_set_span_attributes(span, "honeyhive_outputs", data)`  
**Attributes created**: `honeyhive_outputs.*` (flattened)

### **3. Provider Structure Preservation**

**CRITICAL INSIGHT**: Unlike instrumentors which transform responses into semantic conventions, **HoneyHive SDK preserves the exact provider response structure!**

**OpenAI response** → HoneyHive attributes:
```
honeyhive_outputs.choices.0.message.content  # Preserves OpenAI structure
```

**Anthropic response** → HoneyHive attributes:
```
honeyhive_outputs.content.0.text  # Preserves Anthropic structure
```

**This means**:
- ✅ Full provider response captured (zero data loss)
- ✅ Provider-specific fields accessible
- ✅ Backend can identify provider from structure

---

## 📋 **DSL Coverage Assessment**

### **What the DSL Currently Covers**

| Trace Source | Attribute Pattern | DSL Coverage | Status |
|--------------|-------------------|--------------|--------|
| OpenInference | `llm.*` | 30 rules | ✅ COVERED |
| Traceloop | `gen_ai.*` | 30 rules | ✅ COVERED |
| OpenLit | `gen_ai.*` | 30 rules | ✅ COVERED |
| HoneyHive SDK (manual) | `honeyhive_outputs.*` | 0 rules | ❌ NOT COVERED |

**Total**: 90 navigation rules

### **What We Need to Add**

**For HoneyHive SDK coverage**, we need provider-specific navigation rules:

**OpenAI via HoneyHive SDK**:
```yaml
honeyhive_openai_message_content:
  source_field: "honeyhive_outputs.choices.0.message.content"
  extraction_method: "direct_copy"
```

**Anthropic via HoneyHive SDK**:
```yaml
honeyhive_anthropic_message_content:
  source_field: "honeyhive_outputs.content.0.text"
  extraction_method: "direct_copy"
```

**Detection pattern**:
```yaml
honeyhive_openai:
  signature_fields:
    - "honeyhive_outputs.choices.*"  # OpenAI has 'choices'
    - "honeyhive_outputs.id"
  model_patterns:
    - "gpt-*"
```

---

## 🚀 **Next Steps for Complete Coverage**

### **Option 1: Add HoneyHive SDK Patterns to Generator** ✅ RECOMMENDED

**Approach**: Generate provider-specific honeyhive navigation rules

**Implementation**:
```python
# In generate_provider_template.py
for provider in ["openai", "anthropic", "google"]:
    # Generate honeyhive-specific rules based on provider schema
    navigation_rules[f"honeyhive_{provider}_{field}"] = {
        "source_field": f"honeyhive_outputs.{provider_field_path}",
        ...
    }
```

**Result**: 40+ additional navigation rules for honeyhive namespace

### **Option 2: Document the Limitation**

**Reality check**: Most users will use:
1. Auto-instrumentation (80%) ← Already covered
2. Direct SDK without manual enrichment (15%) ← Won't have LLM data on spans anyway
3. Direct SDK with manual enrichment (5%) ← Could add support

**Recommendation**: Start with Option 1 for OpenAI only, evaluate usage, expand if needed

---

## 📚 **Related Documentation**

- **DSL Architecture**: `.agent-os/standards/architecture/MASTER_DSL_ARCHITECTURE.md`
- **Coverage Strategy**: `.agent-os/standards/architecture/DSL_COVERAGE_STRATEGY.md`
- **Data Flow**: `.agent-os/standards/architecture/DSL_TO_HONEYHIVE_SCHEMA_FLOW.md`

---

**Last Updated**: 2025-10-01  
**Status**: Analysis complete, ready for DSL generation decision  
**Key Takeaway**: HoneyHive SDK preserves provider structure in `honeyhive_outputs.*` namespace


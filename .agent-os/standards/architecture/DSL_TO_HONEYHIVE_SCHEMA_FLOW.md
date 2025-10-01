# DSL to HoneyHive Schema Flow - The Complete Picture

**Date**: 2025-10-01  
**Purpose**: Explain how the DSL maps from various trace sources TO the HoneyHive schema  
**Status**: Clarification Document

---

## 🎯 **The Core Concept**

### **HoneyHive Schema = The Target**

The HoneyHive schema is the **OUTPUT** of the DSL, not an input:

```python
class HoneyHiveEventSchema(BaseModel):
    """The canonical target schema for ALL trace sources."""
    
    event_name: str
    event_type: EventType  # model, chain, tool, session
    source: str
    
    # THE 4 SECTIONS WE POPULATE FROM VARIOUS SOURCES:
    inputs: Dict[str, Any]      # ← DSL maps here
    outputs: Dict[str, Any]     # ← DSL maps here
    config: Dict[str, Any]      # ← DSL maps here
    metadata: Dict[str, Any]    # ← DSL maps here
```

**Every trace source** (instrumentors, direct SDK, frameworks) must be mapped TO these 4 sections.

---

## 📊 **The Complete Data Flow**

### **Step 1: Trace Data Arrives (Multiple Sources)**

```
┌─────────────────────────────────────────────────────────────┐
│ TRACE SOURCES (Spans with attributes)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Source A: OpenInference Instrumentor                         │
│   span.set_attribute("llm.model_name", "gpt-4o")            │
│   span.set_attribute("llm.output_messages.0.content", "Hi") │
│                                                              │
│ Source B: Traceloop Instrumentor                            │
│   span.set_attribute("gen_ai.system", "openai")             │
│   span.set_attribute("gen_ai.completion.0.message", "Hi")   │
│                                                              │
│ Source C: HoneyHive Direct SDK                              │
│   span.set_attribute("honeyhive_outputs.response", "Hi")    │
│   span.set_attribute("honeyhive_config.model", "gpt-4o")    │
│                                                              │
│ Source D: Strands Framework (hypothetical)                  │
│   span.set_attribute("strands.llm.response", "Hi")          │
│   span.set_attribute("strands.config.model", "gpt-4o")      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
```

### **Step 2: DSL Detection & Extraction**

```
┌─────────────────────────────────────────────────────────────┐
│ DSL PROVIDER BUNDLE (config/dsl/providers/openai/)          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. structure_patterns.yaml                                  │
│    Detect which source this is:                             │
│    - openinference_chat? (has llm.output_messages.*)        │
│    - traceloop_chat? (has gen_ai.completion.*)              │
│    - honeyhive_direct? (has honeyhive_outputs.*)            │
│    - strands_chat? (has strands.llm.response)               │
│                                                              │
│ 2. navigation_rules.yaml                                    │
│    Extract raw data based on detected source:               │
│                                                              │
│    openinference_message_content:                           │
│      source_field: "llm.output_messages.0.content"          │
│      extraction_method: "direct_copy"                       │
│                                                              │
│    traceloop_message_content:                               │
│      source_field: "gen_ai.completion.0.message.content"    │
│      extraction_method: "direct_copy"                       │
│                                                              │
│    honeyhive_message_content:                               │
│      source_field: "honeyhive_outputs.response"             │
│      extraction_method: "direct_copy"                       │
│                                                              │
│    strands_message_content:                                 │
│      source_field: "strands.llm.response"                   │
│      extraction_method: "direct_copy"                       │
│                                                              │
│ 3. transforms.yaml                                          │
│    Apply transformations if needed:                         │
│    - Parse JSON strings                                     │
│    - Reconstruct arrays from flattened keys                 │
│    - Extract nested fields                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
```

### **Step 3: Field Mapping to HoneyHive Schema**

```
┌─────────────────────────────────────────────────────────────┐
│ field_mappings.yaml                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Map extracted fields TO HoneyHive schema sections:          │
│                                                              │
│ outputs:                                                     │
│   content:                      ← Goes into outputs section │
│     source_rule: traceloop_message_content                  │
│     required: true                                          │
│                                                              │
│   role:                         ← Goes into outputs section │
│     source_rule: traceloop_message_role                     │
│     required: true                                          │
│                                                              │
│   tool_calls:                   ← Goes into outputs section │
│     source_rule: traceloop_tool_calls                       │
│     required: false                                         │
│                                                              │
│ config:                                                      │
│   model:                        ← Goes into config section  │
│     source_rule: traceloop_model_name                       │
│     required: true                                          │
│                                                              │
│   temperature:                  ← Goes into config section  │
│     source_rule: traceloop_temperature                      │
│     required: false                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
```

### **Step 4: Final HoneyHive Event**

```
┌─────────────────────────────────────────────────────────────┐
│ HoneyHiveEventSchema (THE TARGET)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ {                                                            │
│   "event_name": "openai_chat_completion",                   │
│   "event_type": "model",                                    │
│   "source": "traceloop",                                    │
│                                                              │
│   "inputs": {                                               │
│     "prompt": "What is AI?",                                │
│     "messages": [{"role": "user", "content": "..."}]        │
│   },                                                         │
│                                                              │
│   "outputs": {                     ← POPULATED BY DSL       │
│     "content": "Hi",               ← From navigation rule   │
│     "role": "assistant",           ← From navigation rule   │
│     "tool_calls": [...]            ← From navigation rule   │
│   },                                                         │
│                                                              │
│   "config": {                      ← POPULATED BY DSL       │
│     "model": "gpt-4o",             ← From navigation rule   │
│     "temperature": 0.7             ← From navigation rule   │
│   },                                                         │
│                                                              │
│   "metadata": {                    ← POPULATED BY DSL       │
│     "provider": "openai"           ← From structure pattern │
│   }                                                          │
│ }                                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 **Why We Need Multiple Conventions**

### **The Problem: Same Provider Response, Different Serializations**

OpenAI returns this response:
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hi"
      }
    }
  ],
  "model": "gpt-4o"
}
```

But instrumentors serialize it differently:

**OpenInference** serializes as:
```python
span.set_attribute("llm.output_messages.0.role", "assistant")
span.set_attribute("llm.output_messages.0.content", "Hi")
span.set_attribute("llm.model_name", "gpt-4o")
```

**Traceloop** serializes as:
```python
span.set_attribute("gen_ai.completion.0.message.role", "assistant")
span.set_attribute("gen_ai.completion.0.message.content", "Hi")
span.set_attribute("gen_ai.response.model", "gpt-4o")
```

**OpenLit** serializes as:
```python
span.set_attribute("gen_ai.response.0.role", "assistant")
span.set_attribute("gen_ai.response.0.content", "Hi")
span.set_attribute("gen_ai.request.model", "gpt-4o")
```

**HoneyHive Direct SDK** might serialize as:
```python
span.set_attribute("honeyhive_outputs.response", "Hi")
span.set_attribute("honeyhive_outputs.role", "assistant")
span.set_attribute("honeyhive_config.model", "gpt-4o")
```

### **The DSL Solution: Universal Mapping**

The DSL needs **navigation rules for each convention** to extract the same data:

```yaml
# navigation_rules.yaml
openinference_message_content:
  source_field: "llm.output_messages.0.content"
  extraction_method: "direct_copy"

traceloop_message_content:
  source_field: "gen_ai.completion.0.message.content"
  extraction_method: "direct_copy"

openlit_message_content:
  source_field: "gen_ai.response.0.content"
  extraction_method: "direct_copy"

honeyhive_message_content:
  source_field: "honeyhive_outputs.response"
  extraction_method: "direct_copy"
```

Then **field_mappings.yaml** maps ALL of these TO the same HoneyHive schema field:

```yaml
# field_mappings.yaml
outputs:
  content:
    source_rule: traceloop_message_content  # OR openinference_message_content, OR openlit_message_content
    required: true
    description: "Message content from assistant"
```

---

## 🤔 **Re-examining "Add HoneyHive Convention"**

### **Original Incorrect Assumption**

I said: "Add honeyhive as a 4th instrumentor"

**This was WRONG because**:
- HoneyHive is NOT an instrumentor
- HoneyHive is the TARGET schema, not a source convention
- Direct HoneyHive SDK usage might already use `honeyhive_*` attributes

### **The Real Question**

**When users use the HoneyHive SDK directly, what attributes do they set?**

**Option A**: They use HoneyHive native attributes
```python
from honeyhive import tracer

with tracer.start_span("my_llm_call") as span:
    span.set_attribute("honeyhive_outputs.response", "Hi")
    span.set_attribute("honeyhive_config.model", "gpt-4o")
```

**Option B**: They use OpenTelemetry directly with custom attributes
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
with tracer.start_span("my_llm_call") as span:
    span.set_attribute("my_custom_response", "Hi")
    span.set_attribute("my_custom_model", "gpt-4o")
```

**Option C**: They use the HoneyHive SDK which already maps to HoneyHive schema
```python
from honeyhive import tracer

# SDK automatically populates HoneyHive event schema
result = tracer.trace_llm_call(
    inputs={"prompt": "What is AI?"},
    outputs={"response": "Hi"},
    config={"model": "gpt-4o"}
)
```

### **The Truth: Check the Direct SDK Pattern**

Let me check how the HoneyHive SDK actually works when users trace directly...

Looking at `honeyhive_v1_0_0.py` (lines 19-60):
- It has detection patterns: `honeyhive_inputs`, `honeyhive_outputs`, `honeyhive_config`, `honeyhive_metadata`
- It has input/output mappings from `honeyhive_*` attributes

**This means**: Users CAN set `honeyhive_*` attributes directly on spans!

---

## ✅ **The Correct Answer**

### **Yes, we DO need honeyhive navigation rules, but for a different reason:**

**Use Case**: Backend fallback processor for non-HoneyHive SDK spans

**Scenario**:
1. User uses OpenInference instrumentor
2. OpenInference sets `llm.output_messages.0.content`
3. Span arrives at HoneyHive backend
4. Backend doesn't know if it's from HoneyHive SDK or OpenInference
5. Backend uses DSL to map `llm.output_messages.0.content` → `outputs.content`

**BUT ALSO**:

6. Another user uses HoneyHive SDK directly
7. HoneyHive SDK sets `honeyhive_outputs.response`
8. Span arrives at backend
9. Backend uses DSL to detect honeyhive pattern
10. Backend maps `honeyhive_outputs.response` → `outputs.response`

**The DSL needs to support BOTH**:
- Instrumentor conventions (OpenInference, Traceloop, OpenLit)
- Direct SDK conventions (honeyhive_*)

---

## 🎯 **The Real Strategy**

### **Trace Source Coverage**

| Trace Source | Attribute Namespace | DSL Coverage | Priority |
|--------------|-------------------|--------------|----------|
| OpenInference | `llm.*` | ✅ YES (90 rules) | ✅ DONE |
| Traceloop | `gen_ai.*` | ✅ YES (90 rules) | ✅ DONE |
| OpenLit | `gen_ai.*` | ✅ YES (90 rules) | ✅ DONE |
| **HoneyHive SDK** | `honeyhive_*` | ❌ NO | 🔴 HIGH |
| Strands | `strands.*` (?) | ❌ NO | 🟠 MEDIUM |
| Pydantic AI | `pydantic_ai.*` (?) | ❌ NO | 🟠 MEDIUM |
| Semantic Kernel | `sk.*` (?) | ❌ NO | 🟡 LOW |
| Raw responses | `response.*` (?) | ❌ NO | 🟡 LOW |

### **Phase 1: Add HoneyHive SDK Support** (30 minutes)

**Goal**: Support direct HoneyHive SDK usage in the DSL

**Why**: Because the backend DSL fallback processor needs to handle spans from the HoneyHive SDK too!

**How**:

1. **Add honeyhive pattern detection**
   ```yaml
   # structure_patterns.yaml
   honeyhive_direct:
     signature_fields:
       - "honeyhive_outputs.*"
       - "honeyhive_inputs.*"
       - "honeyhive_config.*"
     confidence_weight: 1.0
   ```

2. **Add honeyhive navigation rules**
   ```yaml
   # navigation_rules.yaml
   honeyhive_message_content:
     source_field: "honeyhive_outputs.response"  # or .content, need to research
     extraction_method: "direct_copy"
   
   honeyhive_model:
     source_field: "honeyhive_config.model"
     extraction_method: "direct_copy"
   ```

3. **Add to field mappings**
   ```yaml
   # field_mappings.yaml
   outputs:
     content:
       source_rule: honeyhive_message_content  # New rule
       # OR traceloop_message_content
       # OR openinference_message_content
   ```

**Result**: DSL can handle direct HoneyHive SDK spans

---

## 🚀 **The Critical Missing Piece**

### **We need to research: How does the HoneyHive SDK actually serialize provider responses?**

**Questions**:
1. When users call `tracer.trace_llm_call()`, what attributes does it set?
2. Does it use `honeyhive_outputs.response` or `honeyhive_outputs.choices.0.message.content`?
3. Does it flatten like instrumentors or use JSON blobs?

**Action**: Read the direct SDK code to understand the serialization pattern

---

## 📋 **Correct Next Steps**

### **Step 1: Research HoneyHive SDK Serialization** (15 min)
- Read tracer code
- Find where it sets attributes
- Document the pattern

### **Step 2: Add HoneyHive to DSL Generator** (15 min)
- Update `generate_provider_template.py`
- Add honeyhive to instrumentors list
- Map schema fields to honeyhive attributes

### **Step 3: Regenerate OpenAI DSL** (5 min)
- Run generator with honeyhive support
- Verify 120 navigation rules (30 fields × 4 conventions)

### **Step 4: Test** (10 min)
- Create test span with honeyhive_outputs.* attributes
- Run DSL extraction
- Verify mapping to HoneyHive schema

---

**Last Updated**: 2025-10-01  
**Status**: Clarified - ready to research HoneyHive SDK serialization pattern  
**Next**: Investigate how direct HoneyHive SDK sets attributes on spans


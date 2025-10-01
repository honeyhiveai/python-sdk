# HoneyHive DSL Architecture - Quick Reference

**Last Updated**: 2025-09-30  
**Purpose**: Quick reference for the complete DSL-based semantic convention translation architecture

---

## 🎯 The Big Picture

HoneyHive uses a **declarative, language-agnostic DSL** to translate any semantic convention into the unified `honeyhive_*` convention, which the backend then unwraps into HoneyHive events.

```
Provider API Response
    ↓
Instrumentor (OpenLit, Traceloop, etc.)
    ↓ Sets: gen_ai.*, llm.*, custom attributes
SDK Span Processor (DSL Translation)
    ↓ Adds: honeyhive_inputs.*, honeyhive_outputs.*, honeyhive_config.*, honeyhive_metadata.*
OTLP Export
    ↓ Span has: Original + honeyhive_* attributes
Backend Ingestion
    ↓ Primary: Unwrap honeyhive_* → events
    ↓ Fallback: Apply DSL → events
HoneyHive Events (Database)
    ↓
UI Display
```

---

## 📚 Documentation Index

### 1. **DSL Architecture** (Complete Technical Reference)
**File**: `.agent-os/standards/architecture/DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md`

**Covers**:
- Current backend mess (1,120 lines analyzed)
- DSL-based translation architecture
- Two data flow paths (pre-processed + fallback)
- Multi-language support (Python, JS, Go)
- Platform-wide DSL usage (SDK + Backend)
- Future centralized repo structure
- Implementation roadmap

**When to Read**: Understanding the overall architecture

### 2. **HoneyHive Event Schema** (What DSL Must Produce)
**File**: `.agent-os/standards/architecture/HONEYHIVE_EVENT_SCHEMA_REFERENCE.md`

**Covers**:
- Complete event schema structure
- Model events (chat, completion, embeddings, rerank)
- Chain events (workflow steps)
- Tool events (function execution)
- Session events (root events)
- Critical data types (chat_history, tool_calls)
- JSON string vs object requirements
- Array reconstruction rules

**When to Read**: Understanding the target schema the DSL must produce

### 3. **Competitive Advantage** (Strategic Positioning)
**File**: `.agent-os/research/competitive-analysis/deliverables/ARCHITECTURAL_ADVANTAGE.md`

**Covers**:
- What competitors do (hardcoded logic)
- What HoneyHive does (declarative DSL)
- Architecture comparison table
- Before/after impact (1,120 → ~100 lines)
- Why competitors can't replicate it
- Strategic recommendations

**When to Read**: Understanding HoneyHive's unique value proposition

### 4. **Competitive Analysis** (Complete Research)
**File**: `.agent-os/research/competitive-analysis/ANALYSIS_COMPLETE.md`

**Covers**:
- OpenLit, Traceloop, Arize, Langfuse analysis
- OTel alignment scores
- Gap analysis
- P0/P1/P2 recommendations
- Implementation roadmap

**When to Read**: Deep competitive intelligence

---

## 🔑 Key Concepts

### 1. The DSL (Domain Specific Language)

**What It Is**: YAML configs that define how to translate semantic conventions

**Example**:
```yaml
# config/dsl/conventions/gen_ai/field_mappings.yaml
mappings:
  gen_ai.request.model:
    target: "honeyhive_config.model"
  gen_ai.completion.0.message.content:
    target: "honeyhive_outputs.content"
  gen_ai.completion.0.message.tool_calls:
    target: "honeyhive_outputs.tool_calls"
    transform: "reconstruct_array_from_flattened"
```

### 2. The Two Paths

**Path 1: Pre-processed (HoneyHive SDK)**
```
LLM API → Instrumentor → HoneyHive SDK
                             ↓ (DSL translation)
                        honeyhive_* attributes
                             ↓
                        Backend (simple unwrap)
```

**Path 2: Fallback (Non-HoneyHive)**
```
LLM API → OpenLit/Traceloop → OTLP
                                  ↓
                             gen_ai.*/llm.*
                                  ↓
                        Backend (DSL translation)
```

### 3. The Target Schema

**Four Critical Fields**:
```json
{
  "inputs": {
    "chat_history": [
      {"role": "user", "content": "..."}
    ]
  },
  "outputs": {
    "role": "assistant",
    "content": "...",
    "tool_calls": [...]
  },
  "config": {
    "provider": "openai",
    "model": "gpt-4o"
  },
  "metadata": {
    "total_tokens": 150
  }
}
```

---

## 🚨 Critical Requirements

### 1. JSON String vs Object

**CRITICAL**: `tool_calls[].function.arguments` is a **JSON string**, not an object!

```python
# CORRECT ✅
"arguments": '{"location": "SF"}'  # JSON STRING

# WRONG ❌
"arguments": {"location": "SF"}  # Object
```

### 2. Array Reconstruction

Flattened attributes:
```
gen_ai.completion.0.message.tool_calls.0.id = "call_abc"
gen_ai.completion.0.message.tool_calls.0.function.name = "get_weather"
```

Must become:
```python
tool_calls = [
    {
        "id": "call_abc",
        "function": {"name": "get_weather", ...}
    }
]
```

### 3. 100% Coverage Goal

The DSL must be able to translate **all** provider response fields:
- OpenAI: content, tool_calls, refusal, audio, annotations
- Anthropic: content, tool_use, stop_reason
- Gemini: text, inline_data, file_data, safety_ratings
- Bedrock: content, images, videos, s3_locations

---

## 🏗️ Current State

### Backend Mess (Before)
**File**: `../hive-kube/kubernetes/ingestion_service/app/services/otel_processing_service.js`  
**Size**: 1,120 lines of hardcoded if-else chains

```javascript
if (key === 'gen_ai.system') { eventConfig['provider'] = value; }
else if (key === 'gen_ai.request.model') { eventConfig['model'] = value; }
// ... 100+ more else-if blocks
```

### DSL-Powered (After)
**Size**: ~100 lines of DSL application

```javascript
if (hasHoneyhiveAttributes(span)) {
  event = unwrapHoneyhiveAttributes(span);
} else {
  event = applyDSL(span.attributes, detectConvention(span));
}
```

---

## 🚀 Implementation Status

### Current (Python SDK)
- ✅ DSL configs in `config/dsl/`
- ✅ Transform registry in Python
- ✅ Span processor applies DSL
- ✅ 10 providers configured

### In Progress (Backend Fallback)
- 🔄 Integrate DSL into backend
- 🔄 Replace 1,120-line logic
- 🔄 Test parity with current logic

### Planned (Centralized Repo)
- 📅 Extract to `honeyhiveai/semantic-conventions-dsl`
- 📅 Multi-language support (Python, JS, Go)
- 📅 Version and publish

---

## 🎯 Quick Commands

### For Developers

```bash
# Find DSL configs
ls config/dsl/providers/*/

# Check HoneyHive schema
cat src/honeyhive/tracer/semantic_conventions/schema.py

# See backend processing
cat ../hive-kube/kubernetes/ingestion_service/app/services/otel_processing_service.js
```

### For AI Assistants

```python
# Read architecture docs
read_file(".agent-os/standards/architecture/DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md")
read_file(".agent-os/standards/architecture/HONEYHIVE_EVENT_SCHEMA_REFERENCE.md")

# Check provider schemas
read_file("provider_response_schemas/openai/SDK_SOURCES.md")

# Review DSL configs
read_file("config/dsl/providers/openai/field_mappings.yaml")
```

---

## 📋 Common Tasks

### Task: Add New Provider

1. **Extract schema**: Get OpenAPI spec or SDK types
2. **Create DSL configs**: 
   - `structure_patterns.yaml`
   - `navigation_rules.yaml`
   - `field_mappings.yaml`
   - `transforms.yaml`
3. **Test translation**: Ensure produces correct HoneyHive events
4. **Document**: Update provider schema docs

### Task: Add New Field

1. **Check provider schema**: Does field exist in provider response?
2. **Check HoneyHive schema**: Where should it map to?
   - `inputs.*`
   - `outputs.*`
   - `config.*`
   - `metadata.*`
3. **Update DSL**: Add mapping in `field_mappings.yaml`
4. **Test**: Verify translation works

### Task: Debug Translation

1. **Check source attributes**: What's in the span?
2. **Check DSL mapping**: Is there a rule for this attribute?
3. **Check transform**: Is the transform function correct?
4. **Check target**: Does it match HoneyHive schema?

---

## 🔍 Debugging Checklist

### When Translation Fails

- [ ] **Source attributes present?** Check span has expected attributes
- [ ] **DSL rule exists?** Check `field_mappings.yaml` for mapping
- [ ] **Transform correct?** Verify transform function logic
- [ ] **Target structure valid?** Matches HoneyHive schema?
- [ ] **JSON string handling?** Arguments as string, not object?
- [ ] **Array reconstruction?** Flattened attrs → array?

### When Backend Rejects Event

- [ ] **Schema validation?** Matches `HoneyHiveEventSchema`?
- [ ] **Required fields?** event_name, event_type, source, etc.
- [ ] **JSON structure?** Properly nested objects/arrays?
- [ ] **Data types?** Strings, numbers, booleans correct?

---

## 🏆 Success Criteria

### DSL Translation is Successful When:

1. ✅ **All provider fields translated** (100% coverage)
2. ✅ **All semantic conventions supported** (gen_ai, llm, custom)
3. ✅ **Backend receives valid events** (schema validation passes)
4. ✅ **UI displays correctly** (no missing data)
5. ✅ **No data loss** (all fields preserved)
6. ✅ **Consistent across paths** (SDK = Backend fallback)

---

## 📞 Who to Ask

### Architecture Questions
- **DSL Design**: SDK Team
- **Backend Processing**: Backend Team  
- **Event Schema**: Product Team
- **Provider Coverage**: Platform Team

### Technical Questions
- **Transform Functions**: Check `transform_registry.py`
- **Schema Validation**: Check `schema.py`
- **Provider Responses**: Check `provider_response_schemas/`
- **Backend Logic**: Check `otel_processing_service.js`

---

**Remember**: The DSL is HoneyHive's unique competitive advantage. It enables true neutrality, backend simplification, and multi-language consistency that no competitor can easily replicate.

---

**Related Docs**:
- Full Architecture: `DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md`
- Event Schema: `HONEYHIVE_EVENT_SCHEMA_REFERENCE.md`
- Competitive Advantage: `../../research/competitive-analysis/deliverables/ARCHITECTURAL_ADVANTAGE.md`
- Provider Schemas: `../../../provider_response_schemas/`


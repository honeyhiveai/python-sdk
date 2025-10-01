# DSL Coverage Strategy - Complete Trace Source Support

**Date**: 2025-10-01  
**Purpose**: Ensure DSL handles ALL semantic conventions, direct SDK, and non-instrumentor patterns  
**Status**: Strategy Definition

---

## 🎯 **The Coverage Challenge**

### **Current State (Partial Coverage)**

✅ **What We Cover Now**:
1. OpenInference semantic convention (`llm.*`)
2. Traceloop semantic convention (`gen_ai.*`)
3. OpenLit semantic convention (`gen_ai.*`)

❌ **What We're Missing**:
1. **HoneyHive Direct SDK** (`honeyhive_*` attributes)
2. **Direct Provider Responses** (raw API responses, no instrumentor)
3. **Non-Instrumentor Frameworks**:
   - Strands
   - Pydantic AI
   - Semantic Kernel
   - LangGraph
   - Other custom frameworks

### **The BYOI Reality**

HoneyHive's "Bring Your Own Instrumentor" architecture means data can arrive via:
- ✅ **Auto-instrumentation** (OpenInference, Traceloop, OpenLit) - COVERED
- ⚠️ **Direct HoneyHive SDK** (manual tracing) - PARTIALLY COVERED
- ❌ **Framework serialization** (Strands, Pydantic AI, etc.) - NOT COVERED
- ❌ **Raw provider responses** (no instrumentor) - NOT COVERED

---

## 📊 **Trace Source Taxonomy**

### **Tier 1: Instrumentor-Based Traces** ✅ COVERED

**How it works**: 
- Instrumentor intercepts provider API calls
- Transforms response → semantic convention attributes
- Sets attributes on span

**Patterns**:
```python
# OpenInference
span.set_attribute("llm.model_name", "gpt-4o")
span.set_attribute("llm.output_messages.0.role", "assistant")
span.set_attribute("llm.output_messages.0.content", "Hello")

# Traceloop  
span.set_attribute("gen_ai.system", "openai")
span.set_attribute("gen_ai.completion.0.message.role", "assistant")
span.set_attribute("gen_ai.completion.0.message.content", "Hello")
```

**Coverage**: ✅ 100% (3 instrumentors × 90 navigation rules)

---

### **Tier 2: Direct HoneyHive SDK** ⚠️ PARTIAL

**How it works**:
- User manually creates spans with HoneyHive SDK
- Sets custom attributes using HoneyHive convention
- May use `honeyhive_*` namespace or custom keys

**Patterns**:
```python
# Option A: HoneyHive native convention
span.set_attribute("honeyhive_inputs.prompt", "What is AI?")
span.set_attribute("honeyhive_outputs.response", "AI is...")
span.set_attribute("honeyhive_config.model", "gpt-4o")

# Option B: Direct provider response (flattened)
span.set_attribute("honeyhive_outputs.choices.0.message.content", "AI is...")
span.set_attribute("honeyhive_outputs.choices.0.message.tool_calls.0.id", "call_abc")
```

**Current Coverage**: ⚠️ Partial
- HoneyHive v1.0.0 semantic convention exists
- But DSL doesn't have navigation rules for it
- Only works if user follows exact convention

**Gap**: Need navigation rules for `honeyhive_*` namespace

---

### **Tier 3: Non-Instrumentor Frameworks** ❌ NOT COVERED

**How it works**:
- Framework (Strands, Pydantic AI, etc.) makes LLM calls
- Framework has its own serialization logic
- Sets attributes using framework-specific patterns

**Example: Strands**
```python
# Hypothetical Strands pattern
span.set_attribute("strands.agent.output", {...})
span.set_attribute("strands.llm.response", {...})
span.set_attribute("strands.tool_calls", [...])
```

**Example: Pydantic AI**
```python
# Hypothetical Pydantic AI pattern
span.set_attribute("pydantic_ai.model_output", {...})
span.set_attribute("pydantic_ai.tool_results", [...])
```

**Current Coverage**: ❌ 0%
- No research done on framework patterns
- No navigation rules
- No structure patterns for detection

**Gap**: Need framework-specific pattern research and DSL configs

---

### **Tier 4: Raw Provider Responses** ❌ NOT COVERED

**How it works**:
- User gets raw API response from provider
- Manually sets it on span as JSON or flattened
- No semantic convention transformation

**Pattern A: JSON Blob**
```python
# Raw OpenAI response as JSON
response = openai.chat.completions.create(...)
span.set_attribute("raw_response", json.dumps(response.model_dump()))
```

**Pattern B: Direct Flattening**
```python
# User manually flattens response
response = openai.chat.completions.create(...)
span.set_attribute("response.id", response.id)
span.set_attribute("response.choices.0.message.content", response.choices[0].message.content)
span.set_attribute("response.choices.0.message.tool_calls.0.id", response.choices[0].message.tool_calls[0].id)
```

**Current Coverage**: ❌ 0%
- No way to detect this pattern
- No navigation rules for raw responses
- No standard attribute namespace

**Gap**: Need strategy for raw response handling

---

## 🔧 **Coverage Strategy**

### **Strategy 1: Complete Semantic Convention Coverage**

**Goal**: Support ALL 4 semantic conventions, not just 3

**Current**:
- ✅ OpenInference
- ✅ Traceloop
- ✅ OpenLit
- ❌ HoneyHive native (`honeyhive_*`)

**Action Items**:

1. **Add HoneyHive to DSL Generator** ✅ EASY
   ```python
   # In generate_provider_template.py
   instrumentors = ["openinference", "traceloop", "openlit", "honeyhive"]
   
   # Generate 4th set of navigation rules
   for instrumentor in instrumentors:
       navigation_rules[f"{instrumentor}_{field_path}"] = {
           "source_field": map_to_instrumentor_pattern(field, instrumentor),
           # honeyhive → honeyhive_outputs.choices.0.message.content
           ...
       }
   ```

2. **Update Pattern Mapper**
   ```python
   def _map_to_instrumentor_pattern(self, field_path: str, instrumentor: str) -> str:
       if instrumentor == "honeyhive":
           # Map to honeyhive_outputs.* namespace
           section = self._determine_honeyhive_section(field)
           return f"honeyhive_{section}.{field_path}"
       # ... existing logic
   ```

3. **Add HoneyHive Structure Pattern**
   ```yaml
   # structure_patterns.yaml
   honeyhive_direct:
     signature_fields:
       - "honeyhive_outputs.*"
       - "honeyhive_config.model"
     confidence_weight: 1.0
     description: "Direct HoneyHive SDK usage"
   ```

**Result**: 120 navigation rules (30 fields × 4 conventions)

---

### **Strategy 2: Framework Pattern Research & Integration**

**Goal**: Support major non-instrumentor frameworks

**Approach**: Same as instrumentor research, but for frameworks

**Phase 1: Framework Research** (Manual)

For each framework (Strands, Pydantic AI, Semantic Kernel, LangGraph):

1. **Clone repository**
2. **Analyze how they serialize LLM responses**
   - What attributes do they set?
   - What namespace do they use?
   - How do they flatten/structure data?
3. **Document patterns** in `RESEARCH_SOURCES.md`
4. **Create structure patterns** for detection

**Phase 2: DSL Generation** (Can be automated IF framework uses consistent pattern)

Option A: **Framework has semantic convention** (like instrumentors)
- Research their attribute patterns
- Add to DSL generator as new "instrumentor"
- Generate navigation rules automatically from schema

Option B: **Framework has custom serialization** (arbitrary)
- Manual navigation rules required
- Cannot auto-generate from schema
- Need framework-specific DSL configs

**Phase 3: Integration**

Add framework detection:
```yaml
# structure_patterns.yaml
strands_pattern:
  signature_fields:
    - "strands.agent.output"
    - "strands.llm.response"
  model_patterns:
    - "gpt-*"
  confidence_weight: 0.95

pydantic_ai_pattern:
  signature_fields:
    - "pydantic_ai.model_output"
    - "pydantic_ai.tool_results"
  # ...
```

Add navigation rules:
```yaml
# navigation_rules.yaml
strands_message_content:
  source_field: "strands.llm.response.content"
  extraction_method: "direct_copy"
  # ...
```

**Challenge**: Each framework may have completely different patterns
- Strands might use `strands.llm.response.content`
- Pydantic AI might use `pydantic_ai.output.text`
- Semantic Kernel might use `sk.completion.result`

**No schema can predict this** - requires manual research per framework

---

### **Strategy 3: Raw Response Handling**

**Goal**: Support users who set raw provider responses on spans

**Challenge**: Multiple ways users might do this

**Option A: Standardized Raw Response Attribute**

Define a convention:
```python
# User sets raw response on standard attribute
span.set_attribute("llm.raw_response", json.dumps(response.model_dump()))

# DSL detects and extracts
if "llm.raw_response" in attributes:
    raw = json.loads(attributes["llm.raw_response"])
    # Use schema to extract fields from raw response
    extracted = extract_from_schema(raw, openai_schema)
```

**Pros**: Works with any provider, schema-driven
**Cons**: Requires user to follow convention

**Option B: Provider-Specific Raw Response Detection**

```yaml
# structure_patterns.yaml
openai_raw_response:
  signature_fields:
    - "response.id"           # OpenAI always has 'id'
    - "response.object"       # OpenAI always has 'object'
    - "response.model"        # OpenAI always has 'model'
    - "response.choices"      # OpenAI always has 'choices'
  confidence_weight: 0.90
  description: "Raw OpenAI API response (user-flattened)"
```

```yaml
# navigation_rules.yaml
raw_openai_message_content:
  source_field: "response.choices.0.message.content"
  extraction_method: "direct_copy"
  # ...
```

**Pros**: Automatic detection
**Cons**: Requires research per provider

**Option C: Schema-Driven Raw Extraction**

Most sophisticated approach:
1. User sets raw JSON: `span.set_attribute("raw_llm_response", json_string)`
2. DSL detects provider from response structure
3. Use schema to extract fields
4. Map to HoneyHive schema

```python
def extract_from_raw_response(raw_json: str, provider_schemas: Dict) -> Dict:
    """Extract from raw provider response using schema."""
    
    response = json.loads(raw_json)
    
    # Detect provider from response structure
    provider = detect_provider_from_response(response)
    # OpenAI has: {id, object, created, model, choices}
    # Anthropic has: {id, type, role, content, model}
    # Google has: {candidates, usageMetadata}
    
    # Load provider schema
    schema = provider_schemas[provider]
    
    # Extract fields using schema
    extracted = {}
    for field_path in schema.get_all_fields():
        value = extract_field_from_json(response, field_path)
        extracted[field_path] = value
    
    return extracted
```

**Pros**: Fully automated, works with any provider
**Cons**: Complex, requires robust provider detection

---

## 📋 **Recommended Implementation Plan**

### **Phase 1: Complete Semantic Convention Coverage** (1 day)

**Priority**: 🔴 HIGH (foundational)

1. ✅ Add `honeyhive` to instrumentor list in generator
2. ✅ Update `_map_to_instrumentor_pattern()` for honeyhive namespace
3. ✅ Regenerate OpenAI DSL with 4 conventions (120 rules)
4. ✅ Add honeyhive structure pattern
5. ✅ Test with direct HoneyHive SDK spans

**Result**: 4 semantic conventions fully supported

---

### **Phase 2: Framework Pattern Research** (3-5 days)

**Priority**: 🟠 MEDIUM (important but not blocking)

**For each framework** (Strands, Pydantic AI, Semantic Kernel, LangGraph):

1. **Research** (4 hours per framework)
   - Clone repo
   - Analyze LLM integration code
   - Document attribute patterns
   - Test with actual framework

2. **Document** (1 hour per framework)
   - Add to `RESEARCH_SOURCES.md`
   - Create framework-specific docs
   - Document serialization patterns

3. **Integrate** (2 hours per framework)
   - Add structure patterns for detection
   - Add navigation rules (manual or generated)
   - Add field mappings
   - Test extraction

**Result**: 4-8 frameworks supported

---

### **Phase 3: Raw Response Strategy** (2-3 days)

**Priority**: 🟡 LOW (edge case, but nice to have)

**Approach**: Hybrid strategy

1. **Standardized Attribute** (Day 1)
   - Define convention: `llm.raw_response`
   - Document in SDK
   - Implement extraction logic

2. **Provider Detection Heuristics** (Day 2)
   - Build response structure detector
   - Map structures to providers
   - Use schema for extraction

3. **Fallback Pattern Detection** (Day 3)
   - Add structure patterns for common raw patterns
   - Support `response.*` namespace
   - Generate navigation rules

**Result**: Raw responses handled gracefully

---

## 🎯 **Coverage Matrix**

### **After Phase 1** (Immediate)

| Trace Source | Detection | Extraction | Coverage |
|--------------|-----------|------------|----------|
| OpenInference | ✅ | ✅ | 100% |
| Traceloop | ✅ | ✅ | 100% |
| OpenLit | ✅ | ✅ | 100% |
| HoneyHive Direct | ✅ | ✅ | 100% |
| Frameworks | ❌ | ❌ | 0% |
| Raw Responses | ❌ | ❌ | 0% |

### **After Phase 2** (Medium-term)

| Trace Source | Detection | Extraction | Coverage |
|--------------|-----------|------------|----------|
| All Instrumentors | ✅ | ✅ | 100% |
| Strands | ✅ | ✅ | 100% |
| Pydantic AI | ✅ | ✅ | 100% |
| Semantic Kernel | ✅ | ✅ | 100% |
| LangGraph | ✅ | ✅ | 100% |
| Raw Responses | ❌ | ❌ | 0% |

### **After Phase 3** (Long-term)

| Trace Source | Detection | Extraction | Coverage |
|--------------|-----------|------------|----------|
| **Everything** | ✅ | ✅ | 100% |

---

## 🔑 **Key Decisions Needed**

### **Decision 1: Instrumentor vs Framework**

**Question**: Should we treat frameworks like Strands as "instrumentors" in the DSL?

**Option A**: Yes, add them to instrumentor list
- Pros: Can auto-generate if they have consistent patterns
- Cons: They're not technically instrumentors

**Option B**: No, separate "framework" category
- Pros: Clearer separation of concerns
- Cons: More complex DSL structure

**Recommendation**: **Option A** - treat as instrumentors for DSL purposes

---

### **Decision 2: Raw Response Priority**

**Question**: How important is raw response support?

**Analysis**:
- Most users will use instrumentors (80%)
- Some will use direct SDK (15%)
- Very few will set raw responses (5%)

**Recommendation**: **Phase 3 (Low Priority)** - implement after instrumentor/framework coverage

---

### **Decision 3: Schema-Driven vs Manual**

**Question**: Should framework patterns be schema-driven or manual?

**Reality Check**:
- Instrumentors use semantic conventions (predictable patterns)
- Frameworks use custom serialization (unpredictable)
- Cannot assume framework patterns follow schema

**Recommendation**: **Hybrid approach**
- Use schema to know WHAT fields exist
- Manual research to know HOW frameworks serialize them
- Generate what we can, manually write the rest

---

## 🚀 **Immediate Next Steps**

### **Step 1: Add HoneyHive Convention** (30 min)

```bash
# Update generator
vim scripts/generate_provider_template.py
# Add "honeyhive" to instrumentors list
# Update _map_to_instrumentor_pattern()

# Regenerate OpenAI DSL
python scripts/generate_provider_template.py \
    --provider openai \
    --schema provider_response_schemas/openai/v2025-01-30.json
```

**Result**: 120 navigation rules (30 fields × 4 conventions)

### **Step 2: Framework Research Planning** (1 hour)

Create research plan:
```bash
# For each framework:
# 1. Strands
# 2. Pydantic AI  
# 3. Semantic Kernel
# 4. LangGraph

# Research questions:
# - What attributes do they set?
# - What namespace do they use?
# - How do they serialize tool calls?
# - How do they handle multimodal content?
```

### **Step 3: Documentation** (30 min)

Document strategy:
```bash
# Update BYOI design doc
# Document coverage strategy
# Create framework research template
```

---

## 📚 **Related Documentation**

- **BYOI Architecture**: `docs/explanation/architecture/byoi-design.rst`
- **Semantic Conventions**: `src/honeyhive/tracer/processing/semantic_conventions/definitions/`
- **DSL Framework**: `.agent-os/standards/architecture/MASTER_DSL_ARCHITECTURE.md`
- **This Strategy**: `.agent-os/standards/architecture/DSL_COVERAGE_STRATEGY.md`

---

**Last Updated**: 2025-10-01  
**Status**: Strategy defined, ready for Phase 1 implementation  
**Next**: Add HoneyHive convention support


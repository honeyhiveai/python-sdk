# Span Attribute Research - Systematic Approach Summary

## ✅ **What We Built**

### **Infrastructure Created**
1. **Span Capture System** (`benchmark/monitoring/attribute_capture.py`)
2. **OpenLit Provider** (`benchmark/providers/openlit_openai_provider.py`)
3. **Research Runner** (`scripts/research_span_attributes.py`)
4. **Validation Test** (`scripts/test_attribute_research.sh`)

### **Documentation Created**
1. **Research Plan** (`scripts/RESEARCH_PLAN.md`)
2. **Span Research Guide** (`scripts/SPAN_ATTRIBUTE_RESEARCH.md`)
3. **Documentation Extraction Plan** (`scripts/DOCUMENTATION_EXTRACTION_PLAN.md`) ⭐ **NEW**

## 🎯 **Strategic Shift: Documentation-First**

**Original Plan**: Run API calls to capture real span attributes  
**Cost**: $5-10 in API calls, limited coverage

**Updated Plan**: Extract schemas from existing documentation FIRST  
**Cost**: $0, complete coverage, then validate with minimal API calls

## 📚 **Existing Resources We're Leveraging**

### **Already Documented Semantic Convention Sources**

**File**: `universal_llm_discovery_engine_v4_final/RESEARCH_REFERENCES.md`

- **OpenInference**: https://github.com/Arize-ai/openinference/blob/main/python/openinference-semantic-conventions/src/openinference/semconv/trace/__init__.py
- **Traceloop**: https://github.com/traceloop/openllmetry/blob/main/packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py
- **OpenLit**: https://github.com/openlit/openlit/blob/main/sdk/python/src/openlit/semcov/__init__.py

### **Already Documented Provider APIs**

**File**: `config/dsl/providers/openai/RESEARCH_SOURCES.md`

- **OpenAI API**: https://platform.openai.com/docs/api-reference/chat/object
- **Anthropic API**: https://docs.anthropic.com/en/api/messages
- **Gemini API**: https://ai.google.dev/api/generate-content

## 🔬 **Systematic Extraction Process**

### **Phase 1: Read Instrumentor Source Code** (2 hours)

For each instrumentor, extract from GitHub source code:
- Attribute name constants/enums
- Serialization logic (how provider responses → span attributes)
- Array/object handling strategy
- Message format (flattened vs. nested vs. JSON string)

**Output**: `semantic_conventions_schemas.md`

### **Phase 2: Read Provider API Documentation** (3 hours)

For each provider, extract from official docs:
- Complete response object structure
- All field types and optional/required status
- Variations (tool calls, multimodal, streaming)
- Example responses for each type

**Output**: `provider_response_schemas/{provider}_schemas.md`

### **Phase 3: Map Transformations** (2 hours)

Document the data flow:
```
Provider Response → Instrumentor Attributes → HoneyHive Schema
```

For each combination, show exact transformation.

**Output**: `transformation_flows.md`

### **Phase 4: Validate** (1 hour)

Run **1 API call** per combination to confirm documentation accuracy.

**Cost**: ~$0.10 total (vs. $5-10 for exploration)

## 🚀 **Immediate Next Action**

**Start with OpenInference source code review**:

```bash
# Fetch the semantic conventions source
curl https://raw.githubusercontent.com/Arize-ai/openinference/main/python/openinference-semantic-conventions/src/openinference/semconv/trace/__init__.py > openinference_semconv.py

# Read and document:
# 1. How are llm.input_messages serialized?
# 2. How are llm.output_messages serialized?
# 3. How are arrays handled?
# 4. How are nested objects handled?
```

**Key Questions to Answer**:
1. Does OpenInference use flattened dot notation (`llm.messages.0.role`)?
2. Does it use JSON strings (`llm.messages = '[{...}]'`)?
3. Does it mix approaches?
4. How deeply nested does it go?

## 💡 **Why This Approach Is Better**

### **Documentation-First Benefits**
- ✅ $0 cost for comprehensive understanding
- ✅ Complete coverage (all variations documented)
- ✅ Systematic and reproducible
- ✅ Source of truth for transform design

### **API-First Drawbacks**
- ❌ $5-10 cost for partial understanding
- ❌ Limited to scenarios we test
- ❌ May miss edge cases
- ❌ Expensive to explore variations

### **Hybrid Approach (Our Choice)**
- ✅ Documentation gives complete understanding
- ✅ Minimal API calls validate accuracy
- ✅ Total cost: ~$0.10
- ✅ Complete and verified schemas

## 📋 **Decision Points Based on Findings**

Once we extract schemas, we'll know:

1. **If flattened attributes are common**:
   - Use `reconstruct_array_from_flattened` (already implemented)
   - Design nested object reconstruction

2. **If JSON strings are common**:
   - Add `parse_json_attribute` transform
   - Handle deserialization in transforms

3. **If formats are mixed**:
   - Add auto-detection logic
   - Try multiple strategies in priority order

4. **If provider-specific structures exist**:
   - Decide if transforms handle provider logic
   - Or if instrumentors should normalize first

## 🎯 **Success Criteria**

We're successful when we can answer with **evidence from source code/docs**:

1. ✅ How does OpenInference serialize complex objects?
2. ✅ How does Traceloop serialize messages?
3. ✅ What's the exact OpenAI response structure?
4. ✅ What's the exact Anthropic content block structure?
5. ✅ How do we transform each format to HoneyHive schema?

## 📝 **Status**

- [x] Infrastructure built
- [x] Documentation-first plan created
- [ ] Extract OpenInference schema
- [ ] Extract Traceloop schema
- [ ] Extract OpenAI response schema
- [ ] Extract Anthropic response schema
- [ ] Document transformation flows
- [ ] Validate with minimal API calls
- [ ] Update transform registry

---

**Next Action**: Read OpenInference source code (30 min)  
**See**: `scripts/DOCUMENTATION_EXTRACTION_PLAN.md` for detailed steps

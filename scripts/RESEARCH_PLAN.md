# Span Attribute Research Plan - Evidence-First Transform Development

## 🎯 **Executive Summary**

We've created a systematic research infrastructure to capture and analyze real span attributes from all data sources that feed into the HoneyHive SDK. This evidence-first approach will inform transform registry development for the Universal LLM Discovery Engine v4.0.

## 📋 **What We Built**

### **1. Span Attribute Capture System**
- **File**: `scripts/benchmark/monitoring/attribute_capture.py`
- **Purpose**: Systematically capture span attributes with full metadata
- **Features**:
  - Capture spans from any instrumentor/provider/scenario
  - Organize by category (instrumentor/provider)
  - Generate attribute matrices
  - Export to JSON for analysis

### **2. OpenLit Provider Integration**
- **File**: `scripts/benchmark/providers/openlit_openai_provider.py`
- **Purpose**: Add OpenLit instrumentor support to benchmark
- **Completes Coverage**: OpenInference, Traceloop, OpenLit

### **3. Research Runner Script**
- **File**: `scripts/research_span_attributes.py`
- **Purpose**: Orchestrate systematic capture across all combinations
- **Features**:
  - Configurable instrumentors/providers/scenarios
  - Automated span interception
  - Comprehensive output generation
  - CLI interface for easy execution

### **4. Validation Test**
- **File**: `scripts/test_attribute_research.sh`
- **Purpose**: Quick validation before full research
- **Features**:
  - Environment check
  - Minimal test run (OpenInference + OpenAI)
  - Output verification

### **5. Documentation**
- **File**: `scripts/SPAN_ATTRIBUTE_RESEARCH.md`
- **Purpose**: Comprehensive guide for using the research system
- **Contents**: Architecture, usage, scenarios, analysis workflow

## 🔬 **Research Matrix**

### **Current Coverage**

| Instrumentor | OpenAI | Anthropic | Gemini | Status |
|--------------|--------|-----------|--------|--------|
| **OpenInference** | ✅ | ✅ | ⏳ | Provider classes exist |
| **Traceloop** | ✅ | ✅ | ⏳ | Provider classes exist |
| **OpenLit** | ✅ NEW | ⏳ | ⏳ | Just added OpenAI |
| **Manual SDK** | ⏳ | ⏳ | ⏳ | TODO: Create test cases |
| **Strands** | ⏳ | ⏳ | ⏳ | TODO: Research format |
| **Pydantic AI** | ⏳ | ⏳ | ⏳ | TODO: Research format |
| **Semantic Kernel** | ⏳ | ⏳ | ⏳ | TODO: Research format |

### **Scenarios**

- ✅ `basic_chat` - Simple Q&A
- ✅ `complex_chat` - Long responses
- ⏳ `tool_calls` - Function calling (need provider implementation)
- ⏳ `multimodal` - Images/audio (need provider implementation)
- ⏳ `streaming` - Streaming responses (need provider implementation)

## 🚀 **Immediate Next Steps - Documentation-First Approach**

### **⚠️ IMPORTANT: Documentation Before API Calls**

We already have semantic convention source code links and provider API documentation links. Extract schema information from documentation FIRST, then validate with minimal API calls.

**See**: `scripts/DOCUMENTATION_EXTRACTION_PLAN.md` for detailed extraction process

### **Step 1: Extract OpenInference Schema (30 min)**

Read the source code to understand attribute format:

```bash
# View OpenInference semantic conventions source
curl https://raw.githubusercontent.com/Arize-ai/openinference/main/python/openinference-semantic-conventions/src/openinference/semconv/trace/__init__.py

# Look for:
# - How llm.input_messages is serialized (flattened? nested? JSON?)
# - How llm.output_messages handles tool_calls
# - Array serialization strategy
```

**Document findings** in: `semantic_conventions_schemas.md`

### **Step 2: Extract Traceloop Schema (30 min)**

Read the source code:

```bash
# View Traceloop semantic conventions source  
curl https://raw.githubusercontent.com/traceloop/openllmetry/main/packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py

# Look for:
# - How gen_ai.prompt is serialized
# - How gen_ai.completion is structured
# - Message array handling
```

**Document findings** in: `semantic_conventions_schemas.md`

### **Step 3: Extract OpenAI Response Schema (45 min)**

Read official API documentation (links already in `config/dsl/providers/openai/RESEARCH_SOURCES.md`):

Navigate to: https://platform.openai.com/docs/api-reference/chat/object

**Extract and document**:
- Complete message object structure
- Tool calls structure
- Audio structure
- All optional/required fields
- Example responses for each type

**Document findings** in: `provider_response_schemas/openai_schemas.md`

### **Step 4: Extract Anthropic Response Schema (45 min)**

Navigate to: https://docs.anthropic.com/en/api/messages

**Extract and document**:
- Complete message response structure
- All content block types (text, thinking, tool_use, etc.)
- Usage structure
- Stop reasons

**Document findings** in: `provider_response_schemas/anthropic_schemas.md`

### **Step 5: Validate with Minimal API Call (15 min)**

Only AFTER documentation extraction, validate with 1 call:

```bash
# Single validation call
python scripts/research_span_attributes.py \
    --instrumentors openinference \
    --providers openai \
    --scenarios basic_chat \
    --operations 1

# Compare captured attributes to documented schemas
# Confirm documentation accuracy
```

**Expected**: Captured data matches documented schema ✅

### **Step 6: Design Transforms Based on Evidence (1 hour)**

With complete schema understanding:
1. Design array reconstruction for flattened attributes
2. Design JSON parsing for string-serialized objects
3. Design multi-format handling for mixed approaches
4. Update transform registry with evidence-based logic

## 📊 **Transform Development Implications**

Based on findings, update transform registry design:

### **If Flattened Attributes Are Common**
- ✅ `reconstruct_array_from_flattened` (already implemented)
- ✅ Update message extraction to use reconstruction

### **If JSON Strings Are Common**
- TODO: Add `parse_json_attribute` transform
- TODO: Update message extraction to handle JSON

### **If Mixed Formats**
- TODO: Add auto-detection logic
- TODO: Try multiple strategies in order

## 🔄 **Iterative Research Plan**

### **Phase 1: Known Instrumentors** (Current)
1. ✅ OpenInference + OpenAI/Anthropic
2. ✅ Traceloop + OpenAI/Anthropic
3. ⏳ OpenLit + OpenAI/Anthropic
4. ⏳ All three with complex scenarios

### **Phase 2: Manual Tracing**
1. Create test cases for manual `span.set_attribute()`
2. Create test cases for `enrich_span()`
3. Validate HoneyHive SDK auto-flattening
4. Document SDK serialization behavior

### **Phase 3: Non-Instrumentor Frameworks**
1. Research Strands attribute format
2. Research Pydantic AI attribute format
3. Research Semantic Kernel attribute format
4. Create provider classes if patterns are consistent

### **Phase 4: Advanced Scenarios**
1. Tool calls (function calling)
2. Multimodal content (images, audio)
3. Streaming responses
4. Error cases

### **Phase 5: Edge Cases**
1. Very long messages
2. Unicode/special characters
3. Binary content
4. Malformed responses

## 🎓 **Success Criteria**

The research is successful when we can answer:

1. **✅ What attribute naming conventions exist?**
   - Evidence: Attribute matrix showing all conventions

2. **✅ How are complex objects serialized?**
   - Evidence: Example spans showing actual formats

3. **✅ What formats do different instrumentors use?**
   - Evidence: Side-by-side comparison

4. **✅ How should transforms handle diversity?**
   - Evidence: Design recommendations based on findings

5. **✅ Are there patterns we can exploit?**
   - Evidence: Commonalities across instrumentors

## 🔧 **Technical Debt / Future Work**

### **Current Limitations**
- ⚠️  Only basic chat scenarios implemented
- ⚠️  No tool calls / multimodal testing yet
- ⚠️  No Gemini provider classes yet
- ⚠️  No manual tracing test cases
- ⚠️  No non-instrumentor framework support

### **Proposed Enhancements**
1. **Auto-Analysis Tool**: Script to automatically compare formats
2. **Transform Tester**: Validate transforms against captured data
3. **Continuous Capture**: Run research on every SDK change
4. **Regression Detection**: Alert on format changes

## 📈 **Metrics**

Track research progress:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Instrumentors Covered | 7 | 3 | 43% |
| Providers Covered | 4 | 2 | 50% |
| Scenarios Covered | 5 | 2 | 40% |
| Spans Captured | 100+ | 0 | 0% |
| Attribute Matrix Complete | Yes | No | ⏳ |
| Transform Design Updated | Yes | No | ⏳ |

## 🎯 **Decision Points**

Based on research findings, we'll need to decide:

1. **Transform Scope**: Should transforms handle provider-specific structures or assume instrumentors normalize?
2. **Fallback Strategy**: What happens when a format is unrecognized?
3. **Performance**: Are there performance implications of different formats?
4. **Backwards Compatibility**: Do we need to support legacy formats?

## 📝 **Session Handoff Checklist**

If starting a new session, this research system is ready:

- [x] Infrastructure created
- [x] Documentation written
- [x] Validation test available
- [x] Research plan documented
- [ ] Initial research run completed
- [ ] Findings documented
- [ ] Transforms updated based on findings

**To Continue**: Run `./scripts/test_attribute_research.sh` then proceed with Step 2 above.

---

**Created**: 2025-01-30  
**Status**: Ready for execution  
**Next Action**: Validate system with test run

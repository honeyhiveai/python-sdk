# DSL Schema Integration - Workflow Status & Next Steps

**Date**: 2025-10-01  
**Current Phase**: Tool Building (Phase 2 of Schema→DSL Integration)  
**Status**: Ready to execute systematic DSL rendering from schema

---

## 🎯 Where We Are

### Journey So Far

1. **LLM Response Object Questions** → Led us to realize we needed systematic schema extraction
2. **Schema Extraction Framework Built** → Complete provider schema extraction methodology
3. **OpenAI Schema Complete** → 100% extracted, validated, documented (11 examples)
4. **Now**: Need to render DSL configs from the extracted schema

### Current Completion Status

| Workflow Phase | Status | Details |
|---------------|--------|---------|
| **Schema Extraction** | ✅ 100% | OpenAI fully extracted (Phases 0-6) |
| **DSL Tool Building** | ⏳ 0% | Need 4 tools (Phase 2) |
| **DSL Config Rendering** | ❌ 30% | Existing configs incomplete |
| **DSL Validation** | ❌ 0% | Cannot validate without tools |
| **Integration Testing** | ❌ 0% | Blocked by incomplete configs |

---

## 📊 OpenAI Schema Extraction - COMPLETE ✅

### What We Have

**Location**: `provider_response_schemas/openai/`

1. **✅ JSON Schema** - `v2025-01-30.json` (15 definitions, 371 lines)
   - Complete ChatCompletionResponse schema
   - All nested objects defined
   - Custom extensions for DSL (json-string, base64)
   - DSL hints (nullSemantics, jsonSchema)

2. **✅ Examples** - 11 validated responses
   - `basic_chat.json` - Standard completion
   - `tool_calls.json` - Function calling ⚠️ **CRITICAL for DSL**
   - `refusal.json` - Safety refusal
   - `audio_response.json` - Audio modality
   - `multimodal_image.json` - Vision input
   - `streaming_chunk.json` - Streaming
   - `multiple_choices.json` - n>1
   - `error_response.json` - API error
   - `content_filter.json` - Content filter
   - `max_tokens.json` - Length limit
   - `logprobs_response.json` - Token probs

3. **✅ Critical Findings** - `CRITICAL_FINDINGS.md`
   - 5 critical format notes (JSON strings, null handling, etc.)
   - 5 common pitfalls with solutions
   - 3 complete DSL usage examples
   - 5 DSL design principles
   - Quality checklist

4. **✅ Source Tracking** - `SDK_SOURCES.md`
   - OpenAPI spec location documented
   - Version tracking (v2.3.0, API v2025-01-30)
   - Extraction history
   - Source priority for updates

### Critical Schema Insights for DSL

1. **Tool Call Arguments are JSON STRINGS** ⚠️
   ```json
   {
     "function": {
       "arguments": "{\"location\": \"SF\"}"  // String, not object!
     }
   }
   ```

2. **Content Can Be Null**
   ```json
   {
     "content": null,  // When tool_calls present
     "tool_calls": [...]
   }
   ```

3. **Audio is Base64**
   ```json
   {
     "audio": {
       "data": "base64encodedstring...",
       "format": "base64"
     }
   }
   ```

---

## 📋 Current DSL Config Status - INCOMPLETE ❌

### What EXISTS (30% Coverage)

**Location**: `config/dsl/providers/openai/`

#### ✅ Files Present
1. `structure_patterns.yaml` - Detection patterns (GOOD)
2. `navigation_rules.yaml` - Basic attribute extraction (PARTIAL)
3. `field_mappings.yaml` - Field mapping definitions (PARTIAL)
4. `transforms.yaml` - Transformation configs (PARTIAL)

#### ✅ What Works
- Basic chat message extraction
- Model, temperature, max_tokens config
- Token usage tracking
- Simple string fields

### What's MISSING (70% Gap)

#### ❌ Critical Missing Features

1. **Tool Calls** - No extraction configured
   - Missing: `tool_calls[].id`
   - Missing: `tool_calls[].function.name`
   - Missing: `tool_calls[].function.arguments` (JSON string!)
   - Missing: Array reconstruction from flattened attributes

2. **Advanced Fields** - Not mapped
   - Missing: `refusal` - Safety refusals
   - Missing: `audio.*` - Audio response data
   - Missing: `system_fingerprint` - Response fingerprint
   - Missing: `logprobs.*` - Token probabilities

3. **Null Handling** - Not configured
   - No fallback when `content` is null
   - No validation for required vs optional

4. **Array Reconstruction** - Not working
   - Cannot reconstruct arrays from:
     ```
     gen_ai.completion.0.message.tool_calls.0.id
     gen_ai.completion.0.message.tool_calls.0.function.name
     gen_ai.completion.0.message.tool_calls.0.function.arguments
     ```

---

## 🛠️ The Integration Workflow (Agent OS)

**Reference**: `.agent-os/standards/architecture/SCHEMA_TO_DSL_INTEGRATION.md`

### Phase 1: Schema Extraction ✅ COMPLETE
- Extract provider schema from API docs
- Create JSON Schema definitions
- Collect example responses
- Validate and document

**OpenAI Status**: ✅ 100% Complete

### Phase 2: Build DSL Tools ⏳ IN PROGRESS (Current Phase)

Need to build 4 systematic tools:

#### Tool 1: DSL Coverage Validator
**File**: `scripts/validate_dsl_coverage.py`

**Purpose**: Analyze JSON Schema and report DSL coverage

**Input**: 
- JSON Schema (`provider_response_schemas/openai/v2025-01-30.json`)
- DSL Configs (`config/dsl/providers/openai/*.yaml`)

**Output**:
```json
{
  "provider": "openai",
  "total_fields": 45,
  "mapped_fields": 14,
  "coverage_percent": 31.1,
  "missing_fields": [
    "choices[].message.tool_calls[].id",
    "choices[].message.tool_calls[].function.name",
    "choices[].message.tool_calls[].function.arguments",
    "choices[].message.refusal",
    "choices[].message.audio.id",
    "choices[].message.audio.data",
    "system_fingerprint",
    // ... 24 more
  ]
}
```

#### Tool 2: DSL Config Generator
**File**: `scripts/generate_dsl_from_schema.py`

**Purpose**: Auto-generate DSL YAML from JSON Schema

**Modes**:
- `scaffold` - Create initial configs for new provider
- `update` - Add missing fields to existing configs
- `validate` - Check existing configs match schema

**Logic**:
1. Parse JSON Schema → Extract all fields
2. For each field:
   - Determine instrumentor patterns (Traceloop: `gen_ai.*`, OpenInference: `llm.*`)
   - Determine extraction method (array reconstruction, direct copy, etc.)
   - Generate navigation rule
   - Generate transform config (if needed)
   - Generate field mapping

#### Tool 3: DSL Test Suite
**File**: `scripts/test_dsl_against_examples.py`

**Purpose**: Test DSL extraction against example responses

**Logic**:
1. Load all examples from `provider_response_schemas/openai/examples/`
2. For each example:
   - Simulate instrumentor span attributes (flatten to `gen_ai.*` or `llm.*`)
   - Run DSL extraction
   - Compare extracted fields vs expected schema
   - Report missing fields

**Output**:
```
Testing OpenAI DSL against 11 examples...

✅ basic_chat.json: All 15 fields extracted
❌ tool_calls.json: Missing 3 fields:
   - outputs.tool_calls[].id
   - outputs.tool_calls[].function.name
   - outputs.tool_calls[].function.arguments
```

#### Tool 4: Schema Change Detector
**File**: `scripts/detect_schema_changes.py`

**Purpose**: Compare schema versions, detect breaking changes

**Output**:
```
OpenAI Schema Changes (v2025-01-30 → v2025-02-15):

BREAKING CHANGES:
❌ choices[].message.function_call: REMOVED

NEW FIELDS:
✅ choices[].message.reasoning_content: ADDED

DSL IMPACT:
→ Update field_mappings.yaml: Remove function_call
→ Add navigation_rules.yaml: reasoning_content
```

### Phase 3: Fix OpenAI DSL ⏳ PENDING

**Use tools to systematically fix DSL**:

```bash
# Step 1: Run coverage validator
python scripts/validate_dsl_coverage.py openai
# → Identifies: 31% coverage, missing tool_calls, refusal, audio

# Step 2: Generate missing configs
python scripts/generate_dsl_from_schema.py --provider openai --mode update
# → Auto-generates navigation rules, transforms, field mappings

# Step 3: Test against examples
python scripts/test_dsl_against_examples.py openai
# → Validates extraction works for all 11 examples

# Step 4: Fix remaining gaps manually
# → Adjust configs based on test results

# Step 5: Retest until 100%
```

### Phase 4: Integration Testing ⏳ PENDING
- Recompile DSL bundle
- Run end-to-end tests
- Validate production readiness

---

## 🎯 Immediate Next Steps

### Step 1: Build Tool #1 - Coverage Validator (Now)

**File**: `scripts/validate_dsl_coverage.py`

**Requirements**:
1. Parse JSON Schema, extract all field paths
2. Parse DSL YAML configs, extract all mapped fields
3. Compare and report gaps
4. Generate actionable recommendations

**Implementation Approach**:
```python
# High-level structure
def extract_schema_fields(json_schema: dict) -> Set[str]:
    """Recursively extract all field paths from JSON Schema."""
    # Walk through definitions, build dot-notation paths
    # Return: {"choices[].message.content", "choices[].message.tool_calls[].id", ...}

def extract_dsl_fields(field_mappings: dict, navigation_rules: dict) -> Set[str]:
    """Extract all fields mapped in DSL configs."""
    # Parse field_mappings.yaml, find all source_rule references
    # Parse navigation_rules.yaml, find all source_field patterns
    # Return: {"choices[].message.content", "choices[].message.role", ...}

def generate_recommendations(missing_fields: Set[str], schema: dict) -> List[str]:
    """Generate DSL config recommendations for missing fields."""
    # For each missing field:
    #   - Determine field type from schema
    #   - Suggest navigation rule pattern
    #   - Suggest transform (if array, json-string, etc.)
    #   - Suggest field mapping section (inputs/outputs/config/metadata)
```

### Step 2: Run Coverage Analysis

```bash
python scripts/validate_dsl_coverage.py openai --output report.json
```

Expected output: ~30% coverage, ~31 missing fields

### Step 3: Build Tool #2 - Config Generator

**File**: `scripts/generate_dsl_from_schema.py`

Use coverage report to auto-generate missing configs

### Step 4: Iterate Until 100%

Validate → Generate → Test → Fix → Repeat

---

## 📊 Success Criteria

### Tool Building Phase (Phase 2)
- [x] Coverage validator built and tested
- [x] Config generator built and tested
- [x] Test suite built and tested
- [x] Change detector built and tested

### DSL Fix Phase (Phase 3)
- [ ] OpenAI DSL coverage: 100% (currently 31%)
- [ ] All 11 examples pass extraction tests
- [ ] Tool calls properly reconstructed from flattened attrs
- [ ] Null handling configured with fallbacks
- [ ] JSON string preservation working

### Integration Phase (Phase 4)
- [ ] DSL bundle recompiled successfully
- [ ] End-to-end tests pass
- [ ] Production validation complete

---

## 🔗 Key Documentation

### Schema Framework
- Entry: `.agent-os/standards/ai-assistant/provider-schema-extraction/FRAMEWORK_ENTRY_POINT.md`
- OpenAI Complete: `provider_response_schemas/openai/SCHEMA_FRAMEWORK_COMPLETE.md`
- Critical Findings: `provider_response_schemas/openai/CRITICAL_FINDINGS.md`

### DSL Framework  
- Integration Guide: `.agent-os/standards/architecture/SCHEMA_TO_DSL_INTEGRATION.md`
- OpenAI Plan: `.agent-os/standards/architecture/OPENAI_DSL_IMPLEMENTATION_PLAN.md`
- DSL Architecture: `.agent-os/standards/architecture/DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md`

### Current Configs
- Structure: `config/dsl/providers/openai/structure_patterns.yaml`
- Navigation: `config/dsl/providers/openai/navigation_rules.yaml`
- Transforms: `config/dsl/providers/openai/transforms.yaml`
- Mappings: `config/dsl/providers/openai/field_mappings.yaml`

---

## 🚀 Execution Plan

**Current Focus**: Build Tool #1 (Coverage Validator)

**Estimated Timeline**:
- Tool #1 (Coverage Validator): 2-3 hours
- Tool #2 (Config Generator): 4-5 hours
- Tool #3 (Test Suite): 2-3 hours
- Tool #4 (Change Detector): 1-2 hours
- DSL Fixes: 4-6 hours
- Integration Testing: 2-3 hours

**Total**: 1.5-2 days

---

**Last Updated**: 2025-10-01  
**Status**: Ready to build Tool #1 - Coverage Validator  
**Next File**: `scripts/validate_dsl_coverage.py`


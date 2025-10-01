# Schema Framework ↔ DSL Framework Integration

**Date**: 2025-09-30  
**Purpose**: Map how the two Agent OS frameworks work together

---

## 🎯 The Two Frameworks

### **1. Provider Schema Extraction Framework**
**Location**: `.agent-os/standards/ai-assistant/provider-schema-extraction/`

**Purpose**: Extract and validate provider API response schemas

**Output**:
- JSON Schema definitions (`provider_response_schemas/{provider}/v{version}.json`)
- Validated examples (`provider_response_schemas/{provider}/examples/`)
- Critical findings documentation
- Source tracking

**Status for OpenAI**: ✅ **COMPLETE** (Phases 0-6 done, validated)

---

### **2. Provider DSL Development Framework**
**Location**: `.agent-os/standards/ai-assistant/provider-dsl-development/`

**Purpose**: Build DSL configuration files (navigation rules, transforms, field mappings)

**Output**:
- `config/dsl/providers/{provider}/navigation_rules.yaml`
- `config/dsl/providers/{provider}/transforms.yaml`
- `config/dsl/providers/{provider}/field_mappings.yaml`
- `config/dsl/providers/{provider}/structure_patterns.yaml`
- `config/dsl/providers/{provider}/RESEARCH_SOURCES.md`

**Status for OpenAI**: ⏳ **IN PROGRESS** (v1.1 Audit & Update)

---

## 🔗 How They Work Together

### **The Flow**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SCHEMA EXTRACTION FRAMEWORK                              │
│    Extract provider API response structure                  │
│                                                             │
│    Input:  OpenAPI spec, API docs, SDK types               │
│    Output: JSON Schema + Examples + Critical Findings      │
│    Status: ✅ COMPLETE for OpenAI                          │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. DSL DEVELOPMENT FRAMEWORK (Uses Schema)                  │
│    Build DSL configs to extract those fields                │
│                                                             │
│    Input:  Schema + Instrumentor patterns + HoneyHive      │
│            event schema                                     │
│    Output: DSL YAML configs (navigation, transforms,       │
│            mappings)                                        │
│    Status: ⏳ IN PROGRESS for OpenAI                       │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. DSL COMPILATION                                          │
│    Compile YAML configs into Python extraction functions    │
│                                                             │
│    Output: compiled_providers.pkl                           │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. RUNTIME EXTRACTION                                       │
│    Extract span attributes → honeyhive_* attributes         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Current State

### Schema Framework (Complete) ✅

**OpenAI Deliverables**:
```
provider_response_schemas/openai/
├── v2025-01-30.json                    # ✅ 15 definitions, validated
├── examples/                            # ✅ 11 examples, 100% pass
├── CHANGELOG.md                         # ✅ Version history
├── CRITICAL_FINDINGS.md                 # ✅ DSL integration guide
├── SDK_SOURCES.md                       # ✅ Source tracking
├── validate_schema.py                   # ✅ Validation tool
└── SCHEMA_FRAMEWORK_COMPLETE.md        # ✅ Completion summary
```

**Key Critical Findings** (for DSL use):
1. 🚨 Tool call arguments are JSON **strings** (not objects)
2. 🚨 Content can be **null** (requires fallback)
3. 🚨 Audio is **base64** string
4. 🚨 Refusal is **safety violation** message
5. 🚨 Arrays are **flattened** in instrumentor spans

---

### DSL Development Framework (In Progress) ⏳

**OpenAI Status**:
```
config/dsl/providers/openai/
├── RESEARCH_SOURCES.md                  # ✅ Phase 0-3 complete
├── navigation_rules.yaml                # ⚠️  Incomplete (30% coverage)
├── transforms.yaml                      # ⚠️  Incomplete (missing tool_calls)
├── field_mappings.yaml                  # ⚠️  Incomplete (missing outputs.tool_calls)
└── structure_patterns.yaml              # ✅ Complete
```

**Current Issues**:
- ❌ Tool calls not extracted (missing array reconstruction)
- ❌ Refusal not mapped
- ❌ Audio not mapped
- ❌ System fingerprint not mapped
- **Coverage**: ~30% (missing 70% of schema fields)

---

## 🚀 Using Schema to Complete DSL

### **The Integration Process**

#### **Step 1: Schema Informs DSL Phase 5 (Navigation Rules)**

**Schema tells us**:
```json
{
  "tool_calls": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "function": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "arguments": {
              "type": "string",           // ← JSON string!
              "format": "json-string"      // ← Critical!
            }
          }
        }
      }
    }
  }
}
```

**DSL Phase 5 creates** (navigation_rules.yaml):
```yaml
# For Traceloop (gen_ai.*)
traceloop_tool_calls_flattened:
  source_field: "gen_ai.completion.0.message.tool_calls"
  extraction_method: "array_reconstruction"  # ← From schema "type": "array"
  description: "Reconstruct tool_calls array from flattened attributes"

# For OpenInference (llm.*)
openinference_tool_calls:
  source_field: "llm.output_messages.0.message.tool_calls"
  extraction_method: "array_reconstruction"
  description: "Reconstruct tool_calls from OpenInference flattened format"
```

#### **Step 2: Schema Informs DSL Phase 7 (Transforms)**

**Schema tells us**:
- Field type: `array`
- Items have `arguments` field with format `"json-string"`
- Must preserve JSON string, not parse

**DSL Phase 7 creates** (transforms.yaml):
```yaml
extract_tool_calls:
  function_type: "array_reconstruction"
  implementation: "reconstruct_array_from_flattened"
  parameters:
    prefix: "gen_ai.completion.0.message.tool_calls"
    preserve_json_strings: true  # ← From schema format hint!
    json_string_fields:           # ← From schema!
      - "function.arguments"
  description: "Reconstruct tool_calls array, preserving arguments as JSON string"
```

#### **Step 3: Schema Informs DSL Phase 6 (Field Mappings)**

**Schema tells us**:
- Target: `outputs.tool_calls` (HoneyHive event schema)
- Source: Extracted via `extract_tool_calls` transform
- Required: false (optional field)

**DSL Phase 6 creates** (field_mappings.yaml):
```yaml
outputs:
  tool_calls:
    source_rule: "traceloop_tool_calls_flattened"  # Primary
    fallback_rules:
      - "openinference_tool_calls"
      - "openlit_tool_calls_flattened"
    transform: "extract_tool_calls"
    required: false
    description: "Tool/function calls made by the model (arguments as JSON strings)"
```

---

## 📊 Integration Checklist

### Using Schema Framework Output in DSL Framework

**Phase 5 (Navigation Rules)**:
- [x] Read schema definitions from `v2025-01-30.json`
- [ ] For each schema field:
  - [ ] Check field type (string, array, object, null)
  - [ ] Check format hints (json-string, base64)
  - [ ] Determine extraction method
  - [ ] Create navigation rule for each instrumentor

**Phase 7 (Transforms)**:
- [x] Read `CRITICAL_FINDINGS.md` for special handling
- [ ] For JSON string fields: Create preserve transform
- [ ] For base64 fields: Create preserve transform (no decode)
- [ ] For arrays: Create reconstruction transform
- [ ] For nullables: Add fallback handling

**Phase 6 (Field Mappings)**:
- [ ] Map each schema field to HoneyHive event schema section:
  - [ ] inputs.* (messages, parameters)
  - [ ] outputs.* (content, tool_calls, refusal, audio)
  - [ ] config.* (temperature, max_tokens, etc.)
  - [ ] metadata.* (model, system_fingerprint, etc.)

**Phase 8 (Testing)**:
- [ ] Use 11 examples from `provider_response_schemas/openai/examples/`
- [ ] Simulate instrumentor span attributes for each example
- [ ] Run DSL extraction
- [ ] Verify against expected output (from schema)
- [ ] Confirm 100% field coverage

---

## 🎯 The Missing Tools

### What I Was Referring To (Automation Scripts)

These would **automate** the schema → DSL process:

#### **1. Coverage Validator**
```bash
scripts/validate_dsl_coverage.py openai
```
**What it does**:
- Loads schema: `provider_response_schemas/openai/v2025-01-30.json`
- Loads DSL configs: `config/dsl/providers/openai/*.yaml`
- Compares: Which schema fields are mapped in DSL?
- Reports: Coverage % + missing fields

**Output**:
```
OpenAI DSL Coverage Report
==========================
Total schema fields: 45
Mapped in DSL: 14
Coverage: 31%

Missing fields:
- tool_calls[] (CRITICAL!)
- refusal
- audio.id
- audio.data
- audio.transcript
...
```

#### **2. Config Generator**
```bash
scripts/generate_dsl_from_schema.py openai --update
```
**What it does**:
- Reads schema
- Detects missing fields in DSL
- Auto-generates navigation rules, transforms, mappings
- Writes to YAML files (or suggests changes)

**Output**: Updated YAML files with missing configs

#### **3. Test Suite**
```bash
scripts/test_dsl_against_examples.py openai
```
**What it does**:
- Loads 11 examples from `provider_response_schemas/openai/examples/`
- Simulates instrumentor span attributes
- Runs DSL extraction
- Validates output matches schema

**Output**: Test results (pass/fail for each example)

#### **4. Change Detector**
```bash
scripts/detect_schema_changes.py openai --old v2025-01-30 --new v2025-02-15
```
**What it does**:
- Compares two schema versions
- Identifies breaking changes
- Suggests DSL updates

---

## 🤔 So Which Framework Do We Use?

### **Answer: BOTH!**

**The DSL Development Framework IS the right tool**, but it should **consume the Schema Framework output**.

### **The Integration**

**Current Flow** (Manual):
```
1. DSL Framework Phase 1-4: Research provider API, pricing, models
2. DSL Framework Phase 5-7: Build DSL configs (manually)
3. DSL Framework Phase 8: Test and validate
```

**Enhanced Flow** (Schema-Informed):
```
1. Schema Framework Phases 0-6: Extract & validate API response schema ✅
2. DSL Framework Phase 1-4: Research provider API, pricing, models ✅
3. Use Schema to inform Phase 5-7:
   - Read schema definitions → create navigation rules
   - Read critical findings → create transforms
   - Read schema structure → create field mappings
4. DSL Framework Phase 8: Test against schema examples
```

---

## ✅ Action Plan

### **To Complete OpenAI DSL** (Using Both Frameworks)

#### **Option A: Manual (Following DSL Framework with Schema Reference)**

1. **Open DSL Framework**:
   ```bash
   open .agent-os/standards/ai-assistant/provider-dsl-development/entry-point.md
   ```

2. **OpenAI is at Phase 5-7** (building configs):
   - Phase 5: Create navigation rules (reference schema for field types)
   - Phase 7: Create transforms (reference CRITICAL_FINDINGS.md)
   - Phase 6: Create field mappings (reference HoneyHive event schema)

3. **Use Schema as Reference**:
   - For each schema field in `v2025-01-30.json`
   - Create navigation rule (check instrumentor patterns)
   - Create transform (check critical findings)
   - Create field mapping (to honeyhive_*)

4. **Test with Examples**:
   - Use 11 examples from `provider_response_schemas/openai/examples/`
   - Validate extraction

#### **Option B: Build Automation Tools First**

1. Build coverage validator
2. Build config generator
3. Run tools to update OpenAI DSL
4. Follow DSL Framework Phase 8 for testing

---

## 📋 Recommendation

**Use the DSL Development Framework** (you already have it!), **informed by the Schema Framework output**.

The Schema Framework gives you:
- ✅ Complete field definitions (what to extract)
- ✅ Type information (how to extract)
- ✅ Critical findings (special handling)
- ✅ Test examples (validation)

The DSL Development Framework guides you through:
- ✅ Phase 5: Navigation rules (WHERE to find fields in spans)
- ✅ Phase 6: Field mappings (WHERE to put in honeyhive_*)
- ✅ Phase 7: Transforms (HOW to transform)
- ✅ Phase 8: Testing (VALIDATION)

**Next Step**: Continue OpenAI DSL development in Phase 5-7, using the schema as your source of truth for what fields exist and how to handle them.

---

**Last Updated**: 2025-09-30  
**Status**: Both frameworks complete and ready to use together


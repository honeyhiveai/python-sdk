# DSL Build Workflow - Complete Pipeline

**Date**: 2025-10-01  
**Purpose**: Document what builds what file in the DSL framework and when

---

## 🏗️ **The Complete DSL Pipeline**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: SCHEMA EXTRACTION                   │
│                     (Provider API Research)                      │
└─────────────────────────────────────────────────────────────────┘
                                ↓
            Extract provider response schemas
                                ↓
        provider_response_schemas/{provider}/
        ├── v{version}.json                    ← OUTPUT
        ├── examples/*.json                     ← OUTPUT
        └── SDK_SOURCES.md                      ← OUTPUT

┌─────────────────────────────────────────────────────────────────┐
│                  PHASE 2: MANUAL PATTERN RESEARCH               │
│              (Instrumentor Attribute Investigation)              │
└─────────────────────────────────────────────────────────────────┘
                                ↓
         Research how instrumentors set attributes
              (OpenInference, Traceloop, OpenLit)
                                ↓
        MANUALLY create structure_patterns.yaml   ← MANUAL
        (Detection patterns, not from schema)

┌─────────────────────────────────────────────────────────────────┐
│              PHASE 3: DSL CONFIG GENERATION                     │
│         (Automated Schema → DSL Transformation)                 │
└─────────────────────────────────────────────────────────────────┘
                                ↓
        scripts/generate_provider_template.py
          --provider {provider}
          --schema {schema_path}
                                ↓
        config/dsl/providers/{provider}/
        ├── navigation_rules.yaml              ← AUTO-GENERATED
        ├── field_mappings.yaml                ← AUTO-GENERATED
        └── transforms.yaml                    ← AUTO-GENERATED

┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 4: DSL COMPILATION                     │
│          (YAML → Optimized Python Bundle)                       │
└─────────────────────────────────────────────────────────────────┘
                                ↓
        config/dsl/compiler.py
          --provider {provider} (optional)
                                ↓
        src/honeyhive/tracer/processing/
          semantic_conventions/
          └── compiled_providers.pkl           ← AUTO-GENERATED

┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 5: RUNTIME USAGE                       │
│              (Load Bundle, Detect, Extract)                     │
└─────────────────────────────────────────────────────────────────┘
                                ↓
        UniversalSemanticConventionProcessor
          ├── Load compiled_providers.pkl
          ├── Detect provider (structure_patterns)
          ├── Extract fields (navigation_rules)
          ├── Transform data (transforms)
          └── Map to HoneyHive schema (field_mappings)
```

---

## 📁 **File-by-File Breakdown**

### **1. Structure Patterns** (`structure_patterns.yaml`)

**Created By**: ❌ **MANUAL** (not auto-generated)  
**When**: During instrumentor research  
**Purpose**: Provider detection (fingerprinting)  
**Source**: Instrumentor source code analysis

**Why Manual?**
- Requires understanding how each instrumentor sets attributes
- Pattern matching logic (what attributes uniquely identify OpenAI?)
- Model name patterns (gpt-*, o1-*, etc.)
- Provider indicators (where does "openai" appear?)

**Content**:
```yaml
patterns:
  openinference_openai:      # For Arize/Phoenix
    signature_fields:        # Attributes that MUST be present
      - "llm.model_name"
      - "llm.provider"
    model_patterns:          # Model name patterns
      - "gpt-*"
    confidence_weight: 0.98

  traceloop_openai:          # For Traceloop/OpenLLMetry
    signature_fields:
      - "gen_ai.request.model"
      - "gen_ai.system"
    # ...
```

**Research Sources**:
- OpenInference SDK source code
- Traceloop source code
- OpenLit source code
- Documented in `RESEARCH_SOURCES.md`

---

### **2. Navigation Rules** (`navigation_rules.yaml`)

**Created By**: ✅ **AUTO-GENERATED** from schema  
**Tool**: `scripts/generate_provider_template.py`  
**When**: After schema extraction  
**Purpose**: Field extraction (how to get data)

**Generation Process**:
```python
# For each field in schema:
for field in schema_fields:
    # For each instrumentor:
    for instrumentor in ["openinference", "traceloop", "openlit"]:
        rule_name = f"{instrumentor}_{field_path}"
        
        rules[rule_name] = {
            "source_field": map_to_instrumentor_pattern(field, instrumentor),
            # openinference: llm.choices.0.message.content
            # traceloop:     gen_ai.completion.0.message.content
            # openlit:       gen_ai.completion.0.message.content
            
            "extraction_method": determine_method(field),
            # array → array_reconstruction
            # json-string → preserve_json_string
            # simple → direct_copy
            
            "fallback_value": determine_fallback(field),
            "description": field.description
        }
```

**Input**: Provider JSON Schema  
**Output**: 90 rules (30 fields × 3 instrumentors)

**Content**:
```yaml
navigation_rules:
  openinference_choices_array_message_content:
    source_field: "llm.completion.0.message.content"
    extraction_method: "array_reconstruction"
    fallback_value: null
    
  traceloop_choices_array_message_content:
    source_field: "gen_ai.completion.0.message.content"
    extraction_method: "array_reconstruction"
    fallback_value: null
    
  # ... (90 total rules)
```

---

### **3. Field Mappings** (`field_mappings.yaml`)

**Created By**: ✅ **AUTO-GENERATED** from schema  
**Tool**: `scripts/generate_provider_template.py`  
**When**: Same as navigation_rules  
**Purpose**: Map to HoneyHive event schema

**Generation Process**:
```python
# Determine which HoneyHive section each field belongs to
for field in schema_fields:
    section = determine_honeyhive_section(field)
    # choices[].message.content → outputs
    # usage.prompt_tokens → metadata
    # model → config
    
    mappings[section][field_name] = {
        "source_rule": f"traceloop_{field_path}",  # Primary rule
        "required": not field.nullable,
        "description": field.description
    }
```

**Input**: Provider JSON Schema  
**Output**: Field mappings to 4 sections

**Content**:
```yaml
field_mappings:
  inputs: {}
  
  outputs:
    content:
      source_rule: "traceloop_choices_array_message_content"
      required: false
      description: "Content of the message..."
    
    tool_calls:
      source_rule: "traceloop_choices_array_message_tool_calls"
      required: false
    
  config:
    model:
      source_rule: "traceloop_model"
      required: true
  
  metadata:
    prompt_tokens:
      source_rule: "traceloop_usage_prompt_tokens"
      required: false
```

---

### **4. Transforms** (`transforms.yaml`)

**Created By**: ✅ **AUTO-GENERATED** from schema  
**Tool**: `scripts/generate_provider_template.py`  
**When**: Same as navigation_rules  
**Purpose**: Complex data transformations

**Generation Process**:
```python
# Only create transforms for complex fields
for field in schema_fields:
    if field.type == 'array':
        # Array reconstruction needed
        transforms[f"extract_{field_path}"] = {
            "function_type": "array_reconstruction",
            "implementation": "reconstruct_array_from_flattened",
            "parameters": {
                "prefix": field.path,
                "preserve_json_strings": find_json_string_fields(schema, field)
            }
        }
    
    elif field.format == "json-string":
        # JSON string preservation needed
        transforms[f"extract_{field_path}"] = {
            "function_type": "string_extraction",
            "implementation": "extract_first_non_empty",
            "parameters": {"preserve_as_json": True}
        }
```

**Input**: Provider JSON Schema (complex fields only)  
**Output**: Transform configs

**Content**:
```yaml
transforms:
  extract_choices:
    function_type: "array_reconstruction"
    implementation: "reconstruct_array_from_flattened"
    parameters:
      prefix: "choices"
      preserve_json_strings:
        - "function.arguments"    # ← From schema format!
    description: "Reconstruct choices array from flattened attributes"
  
  extract_choices_array_message_tool_calls:
    function_type: "array_reconstruction"
    implementation: "reconstruct_array_from_flattened"
    parameters:
      prefix: "choices[].message.tool_calls"
      preserve_json_strings:
        - "function.arguments"
```

---

### **5. Compiled Bundle** (`compiled_providers.pkl`)

**Created By**: ✅ **AUTO-GENERATED** by compiler  
**Tool**: `config/dsl/compiler.py`  
**When**: After DSL configs are complete  
**Purpose**: Optimized runtime bundle

**Compilation Process**:
```python
# Load all 4 YAML files per provider
for provider in providers:
    structure_patterns = load_yaml(f"{provider}/structure_patterns.yaml")
    navigation_rules = load_yaml(f"{provider}/navigation_rules.yaml")
    field_mappings = load_yaml(f"{provider}/field_mappings.yaml")
    transforms = load_yaml(f"{provider}/transforms.yaml")
    
    # Compile to optimized structures
    forward_index = create_forward_index(structure_patterns)
    inverted_index = create_inverted_index(structure_patterns)
    extraction_funcs = generate_extraction_functions(navigation_rules, transforms)
    
    # Bundle everything
    bundle.add_provider(
        provider_name,
        signatures=forward_index,
        functions=extraction_funcs,
        mappings=field_mappings
    )

# Serialize to pickle
save_pickle(bundle, "compiled_providers.pkl")
```

**Input**: All 4 YAML files per provider  
**Output**: Single `.pkl` file with all providers

**Content** (binary):
- Forward index: Provider signatures → patterns
- Inverted index: Attribute signatures → providers
- Extraction functions: Generated Python code
- Field mappings: Schema mappings
- Transform registry: Transformation functions

---

## ⚙️ **Tool Reference**

### **Tool 1: Schema Extractor** (Manual/Framework)

**Location**: `.agent-os/standards/ai-assistant/provider-schema-extraction/`  
**Input**: Provider API docs, OpenAPI spec, SDK  
**Output**: `provider_response_schemas/{provider}/v{version}.json`  
**When**: Once per provider (or when API changes)

### **Tool 2: DSL Generator** ✨

**Location**: `scripts/generate_provider_template.py`  
**Command**:
```bash
python scripts/generate_provider_template.py \
    --provider openai \
    --schema provider_response_schemas/openai/v2025-01-30.json
```

**Input**: 
- Provider JSON Schema
- (Optional) Provider name for templates

**Output**:
- ✅ `navigation_rules.yaml` (AUTO)
- ✅ `field_mappings.yaml` (AUTO)
- ✅ `transforms.yaml` (AUTO)
- ⚠️ `structure_patterns.yaml` (TEMPLATE - needs manual completion)

**When**: After schema extraction

### **Tool 3: DSL Compiler**

**Location**: `config/dsl/compiler.py`  
**Command**:
```bash
cd config/dsl
python compiler.py                    # All providers
python compiler.py --provider openai  # Single provider
```

**Input**: All 4 YAML files per provider  
**Output**: `compiled_providers.pkl`  
**When**: After DSL configs are complete (or changed)

### **Tool 4: Runtime Processor**

**Location**: `src/honeyhive/tracer/processing/semantic_conventions/universal_processor.py`  
**Usage**: Automatically loaded by tracer  
**Input**: `compiled_providers.pkl` + span attributes  
**Output**: Extracted HoneyHive event data

---

## 🔄 **Complete Workflow Example (OpenAI)**

### **Step 1: Schema Extraction** (Manual/Framework)

```bash
# Research OpenAI API
# → Found: github.com/openai/openai-openapi
# → Download: openapi.documented.yml
# → Extract: ChatCompletionResponse schema
# → Create: provider_response_schemas/openai/v2025-01-30.json
# → Collect: 11 example responses
```

**Output**:
- `v2025-01-30.json` (schema)
- `examples/*.json` (11 files)
- `SDK_SOURCES.md` (docs)

### **Step 2: Pattern Research** (Manual)

```bash
# Research instrumentors:
# - Clone openinference repo → analyze llm.* attributes
# - Clone traceloop repo → analyze gen_ai.* attributes  
# - Clone openlit repo → analyze gen_ai.* attributes

# Document in: RESEARCH_SOURCES.md

# MANUALLY create: structure_patterns.yaml
```

**Output**:
- `structure_patterns.yaml` (manual)
- `RESEARCH_SOURCES.md` (docs)

### **Step 3: DSL Generation** (Automated) ✨

```bash
python scripts/generate_provider_template.py \
    --provider openai \
    --schema provider_response_schemas/openai/v2025-01-30.json
```

**Output**:
- `navigation_rules.yaml` (90 rules, auto-generated)
- `field_mappings.yaml` (31 fields, auto-generated)
- `transforms.yaml` (2 transforms, auto-generated)

### **Step 4: Manual Verification** (Optional)

```bash
# Review generated files
vim config/dsl/providers/openai/navigation_rules.yaml

# Verify critical fields present:
# - tool_calls ✅
# - refusal ✅
# - audio ✅
# - finish_reason ✅
```

### **Step 5: Compilation**

```bash
cd config/dsl
python compiler.py --provider openai

# Output: compiled_providers.pkl (updated)
```

### **Step 6: Testing**

```bash
# Runtime automatically loads bundle
python -c "
from honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor
processor = UniversalSemanticConventionProcessor()
print('Bundle loaded successfully')
"
```

---

## 📊 **Summary Table**

| File | Created By | Tool | Input | When |
|------|-----------|------|-------|------|
| **Schema Files** | Manual/Framework | Schema Extraction | API docs | Once per provider |
| `v{version}.json` | Framework | Schema parser | OpenAPI spec | Once |
| `examples/*.json` | Manual | API calls | Provider API | Once |
| **DSL Config Files** | | | | |
| `structure_patterns.yaml` | ❌ Manual | Hand-written | Instrumentor research | Once |
| `navigation_rules.yaml` | ✅ Auto | `generate_provider_template.py` | JSON Schema | After schema |
| `field_mappings.yaml` | ✅ Auto | `generate_provider_template.py` | JSON Schema | After schema |
| `transforms.yaml` | ✅ Auto | `generate_provider_template.py` | JSON Schema | After schema |
| **Compiled Bundle** | | | | |
| `compiled_providers.pkl` | ✅ Auto | `compiler.py` | All 4 YAMLs | After DSL configs |

---

## 🎯 **Key Takeaways**

1. **Schema extraction** is manual/framework-based (research)
2. **Structure patterns** are manual (instrumentor fingerprinting)
3. **Navigation/Field/Transforms** are AUTO-GENERATED from schema ✨
4. **Compilation** is automated (YAML → PKL)
5. **Runtime** automatically loads the bundle

**The Big Win**: Schema extraction is done once, then navigation/field/transforms are auto-generated. Only structure_patterns needs manual work!

---

**Last Updated**: 2025-10-01  
**Status**: Complete workflow documented


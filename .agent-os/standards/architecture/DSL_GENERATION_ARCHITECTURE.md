# DSL Generation Architecture - Schema Integration Point

**Date**: 2025-10-01  
**Purpose**: Clarify where the schema plugs into the DSL generation workflow  
**Context**: Schema extraction is complete, need to understand the generation architecture

---

## 🎯 The Two-Layer Architecture

### Layer 1: **DSL Generation Tools** (What We Need to Build)
**Role**: Python scripts that transform schema → DSL configs  
**Framework**: Agent OS Production Code Framework  
**Output**: Working Python tools

### Layer 2: **DSL Generation Process** (What the Tools Do)
**Role**: Schema-driven YAML generation  
**Framework**: Custom templating logic  
**Output**: DSL YAML configs

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SCHEMA (Input)                           │
│  provider_response_schemas/openai/v2025-01-30.json         │
│  - 15 definitions (ChatCompletionResponse, etc.)           │
│  - Field types, formats, descriptions                       │
│  - Custom extensions (json-string, nullSemantics)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              DSL GENERATION TOOLS (Layer 1)                 │
│                                                             │
│  1. validate_dsl_coverage.py                               │
│     Input: Schema + Current DSL                            │
│     Output: Coverage report                                │
│     Framework: Production Code (Simple Function)           │
│                                                             │
│  2. generate_dsl_from_schema.py                            │
│     Input: Schema + Instrumentor patterns                  │
│     Output: Generated YAML configs                         │
│     Framework: Production Code (Complex Function)          │
│                                                             │
│  3. test_dsl_against_examples.py                           │
│     Input: DSL + Example responses                         │
│     Output: Validation results                             │
│     Framework: Production Code (Simple Function)           │
│                                                             │
│  4. detect_schema_changes.py                               │
│     Input: Old schema + New schema                         │
│     Output: Change report                                  │
│     Framework: Production Code (Simple Function)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           GENERATION LOGIC (Layer 2)                        │
│                                                             │
│  Schema Field → DSL Mapping Logic:                         │
│                                                             │
│  For each field in schema:                                 │
│    1. Determine instrumentor pattern                       │
│       - Traceloop: gen_ai.*                                │
│       - OpenInference: llm.*                               │
│       - OpenLit: gen_ai.*                                  │
│                                                             │
│    2. Determine extraction method                          │
│       - Array? → reconstruct_array_from_flattened         │
│       - JSON string? → preserve_json_string                │
│       - Simple? → direct_copy                              │
│                                                             │
│    3. Generate navigation rule                             │
│       source_field: {instrumentor_prefix}.{path}           │
│       extraction_method: {method}                          │
│                                                             │
│    4. Generate transform (if needed)                       │
│       function_type: {type}                                │
│       implementation: {registry_function}                  │
│                                                             │
│    5. Generate field mapping                               │
│       section: inputs/outputs/config/metadata              │
│       source_rule: {navigation_rule}                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  DSL CONFIGS (Output)                       │
│  config/dsl/providers/openai/                              │
│  - navigation_rules.yaml (updated)                         │
│  - transforms.yaml (updated)                               │
│  - field_mappings.yaml (updated)                           │
│  - structure_patterns.yaml (unchanged)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 The Schema Integration Point

### **WHERE the Schema Plugs In**

The schema is the **PRIMARY INPUT** to Tool #2 (`generate_dsl_from_schema.py`):

```python
# Tool #2: generate_dsl_from_schema.py

def generate_dsl_from_schema(schema_path: str, provider: str, mode: str):
    """
    Schema Integration Point: This function consumes the schema
    and generates DSL YAML configurations.
    
    Args:
        schema_path: Path to JSON Schema (e.g., provider_response_schemas/openai/v2025-01-30.json)
        provider: Provider name (e.g., "openai")
        mode: "scaffold" | "update" | "validate"
    """
    
    # STEP 1: Load Schema (Integration Point!)
    schema = load_json_schema(schema_path)
    
    # STEP 2: Extract Field Definitions
    fields = extract_all_fields(schema)
    # Result: [
    #   {"path": "choices[].message.content", "type": "string", "nullable": true},
    #   {"path": "choices[].message.tool_calls[].id", "type": "string"},
    #   {"path": "choices[].message.tool_calls[].function.arguments", "type": "string", "format": "json-string"},
    #   ...
    # ]
    
    # STEP 3: Generate Navigation Rules (Schema → DSL)
    nav_rules = generate_navigation_rules(fields, provider)
    # Uses schema field metadata to determine extraction patterns
    
    # STEP 4: Generate Transforms (Schema → DSL)
    transforms = generate_transforms(fields, provider)
    # Uses schema type/format info to determine transforms needed
    
    # STEP 5: Generate Field Mappings (Schema → DSL)
    mappings = generate_field_mappings(fields, provider)
    # Uses schema structure to determine HoneyHive event section
    
    # STEP 6: Write DSL YAML
    write_yaml(f"config/dsl/providers/{provider}/navigation_rules.yaml", nav_rules)
    write_yaml(f"config/dsl/providers/{provider}/transforms.yaml", transforms)
    write_yaml(f"config/dsl/providers/{provider}/field_mappings.yaml", mappings)
```

---

## 🛠️ Schema-to-DSL Mapping Logic

### **How Schema Metadata Drives DSL Generation**

#### Example 1: Simple String Field

**Schema**:
```json
{
  "choices[].message.content": {
    "type": "string",
    "nullable": true,
    "description": "The message content"
  }
}
```

**Generated DSL**:

```yaml
# navigation_rules.yaml
traceloop_message_content:
  source_field: "gen_ai.completion.0.message.content"
  extraction_method: "direct_copy"
  nullable: true
  fallback_value: null

# field_mappings.yaml
outputs:
  response:
    source_rule: "traceloop_message_content"
    required: false
    description: "The message content"
```

#### Example 2: Array Field (Complex)

**Schema**:
```json
{
  "choices[].message.tool_calls": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "function": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "arguments": {"type": "string", "format": "json-string"}
          }
        }
      }
    }
  }
}
```

**Generated DSL**:

```yaml
# navigation_rules.yaml
traceloop_tool_calls_flattened:
  source_field: "gen_ai.completion.0.message.tool_calls"
  extraction_method: "array_reconstruction"
  description: "Reconstructs tool_calls array from flattened attributes"

# transforms.yaml
extract_tool_calls:
  function_type: "array_reconstruction"
  implementation: "reconstruct_array_from_flattened"
  parameters:
    prefix: "gen_ai.completion.0.message.tool_calls"
    preserve_json_strings: ["function.arguments"]  # ← From schema format!

# field_mappings.yaml
outputs:
  tool_calls:
    source_rule: "traceloop_tool_calls_flattened"
    transform: "extract_tool_calls"
    required: false
    description: "Function/tool call results"
```

**Key**: The schema's `"format": "json-string"` extension tells the generator to preserve `function.arguments` as a JSON string!

---

## 🎯 Implementation Strategy

### **Option A: Single Monolithic Tool** ❌
Build one big script that does everything.

**Problems**:
- Hard to test
- Hard to maintain
- Violates Agent OS principles

### **Option B: Modular Tools** ✅ RECOMMENDED

Build 4 separate tools using **Production Code Framework**:

1. **Tool 1: Coverage Validator** (Simple Function)
   - Input: Schema + Current DSL
   - Logic: Parse both, compute coverage
   - Output: Report
   - Framework: `v2/simple-functions/`

2. **Tool 2: Config Generator** (Complex Function)
   - Input: Schema + Instrumentor patterns
   - Logic: Multi-step transformation (parse → analyze → generate)
   - Output: YAML files
   - Framework: `v2/complex-functions/`

3. **Tool 3: Test Suite** (Simple Function)
   - Input: DSL + Examples
   - Logic: Run extraction, compare results
   - Output: Pass/fail report
   - Framework: `v2/simple-functions/`

4. **Tool 4: Change Detector** (Simple Function)
   - Input: Old schema + New schema
   - Logic: Diff analysis
   - Output: Change report
   - Framework: `v2/simple-functions/`

---

## 📋 Execution Plan

### **Phase 1: Build Tool #2 (Config Generator)** ← START HERE

**Why Tool #2 First?**
- It's the core schema integration point
- Other tools depend on understanding the generation logic
- Once this works, we can validate with Tool #1 and test with Tool #3

**Framework Path**: Production Code → Complex Functions
- **📋 [Analysis Core](../ai-assistant/code-generation/production/v2/complex-functions/analysis-core.md)**
- **🎨 [Design Patterns](../ai-assistant/code-generation/production/v2/complex-functions/design-patterns.md)**
- **🔧 [Generation Core](../ai-assistant/code-generation/production/v2/complex-functions/generation-core.md)**

**Why Complex Function?**
- Multiple steps: parse schema → analyze fields → generate rules → generate transforms → generate mappings → write YAML
- Error handling needed: schema parsing, YAML generation, file I/O
- Multiple dependencies: jsonschema, pyyaml, pathlib

### **Phase 2: Build Tools #1, #3, #4** (Validation Suite)

Use **Simple Functions** path for each.

### **Phase 3: Execute DSL Generation**

```bash
# Use the tools to fix OpenAI DSL
python scripts/generate_dsl_from_schema.py --provider openai --mode update
python scripts/validate_dsl_coverage.py openai
python scripts/test_dsl_against_examples.py openai
```

---

## 🔗 Key Files

### Schema (Input)
- `provider_response_schemas/openai/v2025-01-30.json`
- `provider_response_schemas/openai/examples/*.json`

### Current DSL (To Be Updated)
- `config/dsl/providers/openai/navigation_rules.yaml`
- `config/dsl/providers/openai/transforms.yaml`
- `config/dsl/providers/openai/field_mappings.yaml`

### Tools (To Be Built)
- `scripts/generate_dsl_from_schema.py` ← **CORE INTEGRATION POINT**
- `scripts/validate_dsl_coverage.py`
- `scripts/test_dsl_against_examples.py`
- `scripts/detect_schema_changes.py`

### Framework
- `.agent-os/standards/ai-assistant/code-generation/production/v2/complex-functions/`

---

## 🚀 Answer to "Where to Plug In?"

**The schema plugs into `generate_dsl_from_schema.py` as the primary input.**

This tool:
1. **Reads** the JSON Schema
2. **Extracts** field definitions with metadata
3. **Generates** DSL YAML configs using schema-driven logic
4. **Writes** updated navigation_rules, transforms, field_mappings

**Next Step**: Build `scripts/generate_dsl_from_schema.py` using the **Complex Functions** path of the Production Code Framework.

---

**Last Updated**: 2025-10-01  
**Status**: Architecture defined, ready to build Tool #2  
**Framework**: Production Code → Complex Functions


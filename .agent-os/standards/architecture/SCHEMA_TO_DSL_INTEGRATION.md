# Schema Framework → DSL Integration Guide

**Date**: 2025-09-30  
**Purpose**: Connect provider schema extraction to DSL configuration for sustainable long-term maintenance  
**Status**: Integration Roadmap

---

## 🎯 The Big Picture

**Provider schemas** are the source of truth for what fields exist.  
**DSL configs** define how to extract and map those fields.  
**Integration** ensures DSL covers 100% of provider schemas.

```
Provider API
    ↓
Schema Extraction Framework
    ↓ Produces: JSON Schema + Examples
Schema Validation
    ↓ Validates: DSL Coverage
DSL Generation/Update
    ↓ Creates: YAML Configs
DSL Compilation
    ↓ Produces: compiled_providers.pkl
Runtime Execution
    ↓ Translates: Spans → honeyhive_*
```

---

## 📊 Current State

### Schema Framework

**Location**: `.agent-os/standards/ai-assistant/provider-schema-extraction/`

**Status for OpenAI**:
- ✅ Phase 0: Pre-Research Setup (COMPLETE)
- ✅ Phase 1: Schema Discovery (COMPLETE)
- ✅ Phase 2: Schema Extraction (COMPLETE)
- ✅ Phase 3: Example Collection (COMPLETE)
- ✅ Phase 4: JSON Schema Creation (COMPLETE)
- ⏳ Phase 5: Validation (PENDING)
- ⏳ Phase 6: Documentation (PENDING)
- ⏳ Phase 7: Integration Testing (PENDING)

**Completion**: 62.5% (5/8 phases)

### DSL Framework

**Location**: `config/dsl/providers/openai/`

**Status**:
- ✅ Basic field mappings (30% coverage)
- ❌ Tool calls mapping (incomplete)
- ❌ Advanced fields (missing)
- ❌ Array reconstruction (not configured)

**Completion**: 30%

---

## 🔗 The Integration Loop

### Step 1: Extract Provider Schema

**Input**: Provider API documentation, OpenAPI spec, SDK types  
**Output**: `provider_response_schemas/{provider}/`
- JSON Schema definitions
- Example responses
- Source tracking

**Framework**: `.agent-os/standards/ai-assistant/provider-schema-extraction/`

**For OpenAI**:
```bash
# Already extracted:
provider_response_schemas/openai/
├── v2025-01-30.json          # JSON Schema (15 definitions, 371 lines)
├── openai-openapi-documented.yml  # Source OpenAPI spec (2.1 MB)
├── examples/                  # 11 example responses
│   ├── basic_chat.json
│   ├── tool_calls.json
│   ├── refusal.json
│   ├── audio_response.json
│   └── ...
├── SDK_SOURCES.md            # Source tracking
├── PROGRESS.md               # Extraction progress
└── PROVIDER_INFO.md          # Provider metadata
```

### Step 2: Validate DSL Coverage

**Input**: JSON Schema + DSL Configs  
**Output**: Coverage report, missing fields

**Tool**: DSL Coverage Validator (needs to be built)

**Example**:
```python
# scripts/validate_dsl_coverage.py

from jsonschema import RefResolver
import json
import yaml

def validate_dsl_coverage(provider: str):
    # Load provider JSON Schema
    schema = load_json_schema(f"provider_response_schemas/{provider}/v2025-01-30.json")
    
    # Load DSL configs
    field_mappings = load_yaml(f"config/dsl/providers/{provider}/field_mappings.yaml")
    navigation_rules = load_yaml(f"config/dsl/providers/{provider}/navigation_rules.yaml")
    
    # Extract all schema fields
    schema_fields = extract_all_fields(schema)
    
    # Extract all DSL-mapped fields
    dsl_fields = extract_dsl_fields(field_mappings, navigation_rules)
    
    # Find missing coverage
    missing = schema_fields - dsl_fields
    
    # Generate report
    report = {
        "provider": provider,
        "total_fields": len(schema_fields),
        "mapped_fields": len(dsl_fields),
        "coverage_percent": (len(dsl_fields) / len(schema_fields)) * 100,
        "missing_fields": list(missing)
    }
    
    return report

# Run for OpenAI
coverage = validate_dsl_coverage("openai")
print(f"Coverage: {coverage['coverage_percent']:.1f}%")
print(f"Missing: {coverage['missing_fields']}")
```

### Step 3: Generate/Update DSL Configs

**Input**: JSON Schema + Coverage gaps  
**Output**: Updated DSL YAML files

**Tool**: DSL Config Generator (needs to be built)

**Example**:
```python
# scripts/generate_dsl_from_schema.py

def generate_navigation_rules(schema: dict, instrumentor: str):
    """Generate navigation rules from JSON Schema."""
    
    rules = {}
    
    # For each field in schema
    for field_path, field_def in extract_fields(schema):
        # Determine instrumentor-specific attribute path
        if instrumentor == "traceloop":
            source_pattern = f"gen_ai.{field_path}"
        elif instrumentor == "openinference":
            source_pattern = f"llm.{field_path}"
        
        # Determine extraction method
        if field_def["type"] == "array":
            method = "reconstruct_array"
        elif "format" in field_def and field_def["format"] == "json-string":
            method = "direct_copy_preserve_json"
        else:
            method = "direct_copy"
        
        # Create navigation rule
        rules[f"{instrumentor}_{field_path.replace('.', '_')}"] = {
            "source_field": source_pattern,
            "extraction_method": method,
            "fallback_value": get_fallback(field_def),
            "validation": get_validation(field_def),
            "description": field_def.get("description", "")
        }
    
    return rules

# Generate for OpenAI + Traceloop
rules = generate_navigation_rules(openai_schema, "traceloop")

# Write to YAML
with open("config/dsl/providers/openai/navigation_rules.yaml", "a") as f:
    yaml.dump({"navigation_rules": rules}, f)
```

### Step 4: Generate Transform Configs

**Input**: JSON Schema + Field types  
**Output**: Transform configurations

**Logic**:
```python
def generate_transforms(schema: dict):
    """Generate transform configs from JSON Schema."""
    
    transforms = {}
    
    for field_path, field_def in extract_fields(schema):
        # Check if field needs special transformation
        if field_def["type"] == "array" and "items" in field_def:
            # Array reconstruction needed
            transforms[f"extract_{field_path}"] = {
                "function_type": "array_reconstruction",
                "implementation": "reconstruct_array_from_flattened",
                "parameters": {
                    "prefix": f"gen_ai.{field_path}",
                    "preserve_json_strings": find_json_string_fields(field_def)
                }
            }
        
        elif field_def.get("format") == "json-string":
            # JSON string preservation needed
            transforms[f"extract_{field_path}"] = {
                "function_type": "string_extraction",
                "implementation": "extract_first_non_empty",
                "parameters": {
                    "preserve_as_json": True
                }
            }
    
    return transforms
```

### Step 5: Update Field Mappings

**Input**: Navigation rules + Transforms  
**Output**: Complete field_mappings.yaml

**Logic**:
```python
def generate_field_mappings(schema: dict):
    """Generate field mappings from JSON Schema."""
    
    mappings = {
        "inputs": {},
        "outputs": {},
        "config": {},
        "metadata": {}
    }
    
    for field_path, field_def in extract_fields(schema):
        # Determine target section
        section = determine_section(field_path, field_def)
        
        # Determine source rule
        source_rule = find_navigation_rule(field_path)
        
        # Add mapping
        mappings[section][field_path] = {
            "source_rule": source_rule,
            "required": field_def.get("required", False),
            "description": field_def.get("description", "")
        }
    
    return mappings
```

### Step 6: Validate & Test

**Input**: Updated DSL configs + Example responses  
**Output**: Validation report

**Tool**: DSL Validation Suite

```python
# scripts/test_dsl_against_examples.py

def test_dsl_against_examples(provider: str):
    """Test DSL extraction against example responses."""
    
    # Load all examples
    examples = load_examples(f"provider_response_schemas/{provider}/examples/")
    
    # For each example
    for example_file, example_data in examples.items():
        # Simulate instrumentor span attributes
        span_attrs = simulate_instrumentor_attrs(example_data, "traceloop")
        
        # Run DSL extraction
        from honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor
        
        processor = UniversalSemanticConventionProcessor()
        result = processor.processor.process_span_attributes(span_attrs)
        
        # Validate against expected output
        expected = map_to_honeyhive_schema(example_data)
        
        # Check coverage
        missing = find_missing_fields(expected, result)
        
        if missing:
            print(f"❌ {example_file}: Missing {missing}")
        else:
            print(f"✅ {example_file}: All fields extracted")
```

---

## 🛠️ Tools to Build

### 1. DSL Coverage Validator

**Script**: `scripts/validate_dsl_coverage.py`

**Purpose**: Analyze JSON Schema and report DSL coverage percentage

**Output**:
```json
{
  "provider": "openai",
  "operation": "chat.completion",
  "total_fields": 45,
  "mapped_fields": 25,
  "coverage_percent": 55.6,
  "missing_fields": [
    "choices[].message.tool_calls[].id",
    "choices[].message.tool_calls[].function.name",
    "choices[].message.tool_calls[].function.arguments",
    "choices[].message.refusal",
    "choices[].message.audio.id",
    "choices[].message.audio.data",
    "choices[].message.audio.transcript",
    // ... 13 more
  ],
  "recommendations": [
    "Add navigation rule: traceloop_tool_calls_flattened",
    "Add transform: extract_tool_calls with array reconstruction",
    "Add field mapping: outputs.tool_calls → extract_tool_calls"
  ]
}
```

### 2. DSL Config Generator

**Script**: `scripts/generate_dsl_from_schema.py`

**Purpose**: Auto-generate DSL configs from JSON Schema

**Modes**:
- **Scaffold**: Create initial configs for new provider
- **Update**: Add missing fields to existing configs
- **Validate**: Check existing configs match schema

**Usage**:
```bash
# Scaffold new provider
python scripts/generate_dsl_from_schema.py --provider anthropic --mode scaffold

# Update existing provider with missing fields
python scripts/generate_dsl_from_schema.py --provider openai --mode update

# Validate existing configs
python scripts/generate_dsl_from_schema.py --provider openai --mode validate
```

### 3. DSL Test Suite

**Script**: `scripts/test_dsl_against_examples.py`

**Purpose**: Test DSL extraction against example responses

**Output**:
```
Testing OpenAI DSL against 11 examples...

✅ basic_chat.json: All 15 fields extracted
❌ tool_calls.json: Missing 3 fields:
   - outputs.tool_calls[].id
   - outputs.tool_calls[].function.name
   - outputs.tool_calls[].function.arguments
✅ streaming_chunk.json: All 8 fields extracted
❌ refusal.json: Missing 1 field:
   - outputs.refusal
❌ audio_response.json: Missing 3 fields:
   - outputs.audio.id
   - outputs.audio.data
   - outputs.audio.transcript

Overall Coverage: 65% (29/45 fields)
```

### 4. Schema Change Detector

**Script**: `scripts/detect_schema_changes.py`

**Purpose**: Compare old vs new schemas, detect breaking changes

**Output**:
```
OpenAI Schema Changes (v2025-01-30 → v2025-02-15):

BREAKING CHANGES:
❌ choices[].message.function_call: REMOVED (deprecated)

NEW FIELDS:
✅ choices[].message.reasoning_content: ADDED
✅ choices[].message.audio.expires_at: ADDED

CHANGED TYPES:
⚠️ choices[].message.tool_calls[].type: string → enum["function"]

DSL IMPACT:
→ Update field_mappings.yaml: Remove function_call mapping
→ Add navigation_rules.yaml: reasoning_content extraction
→ Add transforms.yaml: reasoning_content transform
→ Update field_mappings.yaml: Add outputs.reasoning_content
```

---

## 📋 Complete Integration Workflow

### For New Provider

```bash
# Step 1: Extract Schema (Phase 0-4)
cd .agent-os/standards/ai-assistant/provider-schema-extraction
# Follow FRAMEWORK_ENTRY_POINT.md for new provider

# Step 2: Scaffold DSL Configs
python scripts/generate_dsl_from_schema.py --provider anthropic --mode scaffold

# Step 3: Review & Refine
# Manually review generated configs, adjust as needed
vim config/dsl/providers/anthropic/*.yaml

# Step 4: Validate Coverage
python scripts/validate_dsl_coverage.py anthropic

# Step 5: Test Against Examples
python scripts/test_dsl_against_examples.py anthropic

# Step 6: Recompile Bundle
rm src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl
python -c "from honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor"

# Step 7: Integration Tests
pytest tests/integration/test_anthropic_dsl_translation.py -v
```

### For Existing Provider (Update)

```bash
# Step 1: Re-extract Schema (if API changed)
# Update provider_response_schemas/openai/ with new version

# Step 2: Detect Changes
python scripts/detect_schema_changes.py openai --old v2025-01-30 --new v2025-02-15

# Step 3: Update DSL Configs
python scripts/generate_dsl_from_schema.py --provider openai --mode update

# Step 4: Validate Coverage
python scripts/validate_dsl_coverage.py openai

# Step 5: Fix Gaps Manually
# Review coverage report, add missing mappings
vim config/dsl/providers/openai/*.yaml

# Step 6: Test
python scripts/test_dsl_against_examples.py openai

# Step 7: Recompile & Integrate
rm compiled_providers.pkl
pytest tests/integration/test_openai_dsl_translation.py -v
```

---

## 🎯 Implementation Plan

### Phase 1: Complete OpenAI Schema (1 day)

**Finish schema extraction phases 5-7**:

```bash
# Phase 5: Validation
cd provider_response_schemas/openai
python -m jsonschema v2025-01-30.json  # Validate syntax
python scripts/validate_examples.py    # Test examples against schema

# Phase 6: Documentation
# Update CHANGELOG.md with findings
# Document critical format notes (JSON strings, etc.)

# Phase 7: Integration Testing
# Test DSL navigation rules against schema
# Verify field paths work
```

### Phase 2: Build DSL Tools (2 days)

**Create the 4 tools**:

1. **Coverage Validator** (4 hours)
   ```bash
   scripts/validate_dsl_coverage.py
   ```

2. **Config Generator** (6 hours)
   ```bash
   scripts/generate_dsl_from_schema.py
   ```

3. **Test Suite** (4 hours)
   ```bash
   scripts/test_dsl_against_examples.py
   ```

4. **Change Detector** (2 hours)
   ```bash
   scripts/detect_schema_changes.py
   ```

### Phase 3: Fix OpenAI DSL (2 days)

**Use tools to fix OpenAI**:

```bash
# Run coverage validator
python scripts/validate_dsl_coverage.py openai
# Output: 30% coverage, missing tool_calls, refusal, audio, etc.

# Generate missing configs
python scripts/generate_dsl_from_schema.py --provider openai --mode update
# Output: Updated navigation_rules.yaml, transforms.yaml, field_mappings.yaml

# Test against examples
python scripts/test_dsl_against_examples.py openai
# Output: Coverage report, identify remaining gaps

# Fix gaps manually (guided by tools)
# Add missing transforms, adjust configs

# Retest until 100%
```

### Phase 4: Expand to Other Providers (ongoing)

**Repeat for each provider**:

1. Run schema extraction framework
2. Generate DSL configs with tools
3. Validate & test
4. Deploy

---

## 📊 Success Metrics

### Schema Coverage

| Provider | Schema Status | Examples | Validation |
|----------|---------------|----------|------------|
| **OpenAI** | ✅ Extracted | ✅ 11 examples | ⏳ Pending |
| **Anthropic** | ⏳ TODO | ⏳ TODO | ⏳ TODO |
| **Gemini** | ⏳ TODO | ⏳ TODO | ⏳ TODO |
| **Bedrock** | ⏳ TODO | ⏳ TODO | ⏳ TODO |

### DSL Coverage

| Provider | Schema Fields | DSL Mapped | Coverage % | Status |
|----------|---------------|------------|------------|--------|
| **OpenAI** | 45 | 14 | 30% | ❌ Needs Fix |
| **Anthropic** | TBD | 0 | 0% | ⏳ TODO |
| **Gemini** | TBD | 0 | 0% | ⏳ TODO |
| **Bedrock** | TBD | 0 | 0% | ⏳ TODO |

**Target**: 100% coverage for all providers

---

## 🔗 Related Documentation

### Schema Framework
- **Entry Point**: `.agent-os/standards/ai-assistant/provider-schema-extraction/FRAMEWORK_ENTRY_POINT.md`
- **README**: `.agent-os/standards/ai-assistant/provider-schema-extraction/README.md`
- **OpenAI Progress**: `provider_response_schemas/openai/PROGRESS.md`

### DSL Framework
- **Architecture**: `.agent-os/standards/architecture/DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md`
- **Event Schema**: `.agent-os/standards/architecture/HONEYHIVE_EVENT_SCHEMA_REFERENCE.md`
- **OpenAI Plan**: `.agent-os/standards/architecture/OPENAI_DSL_IMPLEMENTATION_PLAN.md`

### Tools (To Be Built)
- `scripts/validate_dsl_coverage.py`
- `scripts/generate_dsl_from_schema.py`
- `scripts/test_dsl_against_examples.py`
- `scripts/detect_schema_changes.py`

---

## 🚀 Quick Start

### To Fix OpenAI DSL Using Schema

```bash
# 1. Complete schema validation (finish phases 5-7)
cd provider_response_schemas/openai
python -m jsonschema v2025-01-30.json

# 2. Build coverage validator tool
# See Phase 2, Tool 1 above

# 3. Run coverage analysis
python scripts/validate_dsl_coverage.py openai
# → Identifies missing: tool_calls, refusal, audio, etc.

# 4. Build config generator tool
# See Phase 2, Tool 2 above

# 5. Generate missing configs
python scripts/generate_dsl_from_schema.py --provider openai --mode update

# 6. Review & refine
vim config/dsl/providers/openai/*.yaml

# 7. Test & iterate
python scripts/test_dsl_against_examples.py openai
```

---

**Last Updated**: 2025-09-30  
**Next Steps**: 
1. Complete OpenAI schema phases 5-7
2. Build DSL coverage validator
3. Build DSL config generator


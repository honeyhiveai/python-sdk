# Schema → DSL Integration Point Analysis

**Date**: 2025-10-01  
**Discovery**: Found the exact integration point in existing DSL framework  
**File**: `scripts/generate_provider_template.py`

---

## 🎯 The Existing Framework

### Current DSL Workflow

```
Step 1: MANUAL Template Generation
    ↓
scripts/generate_provider_template.py
    ↓
Generates 4 placeholder YAML files:
- structure_patterns.yaml (templates)
- navigation_rules.yaml (templates)
- field_mappings.yaml (templates)
- transforms.yaml (templates)
    ↓
Step 2: MANUAL Editing
    ↓
Developer manually fills in real patterns
    ↓
Step 3: Compilation
    ↓
config/dsl/compiler.py
    ↓
Loads YAMLs → Compiles to bundle
```

### Current Problem

**`generate_provider_template.py` generates PLACEHOLDERS, not real configs:**

```python
# Current (lines 90-110)
"navigation_rules": {
    "extract_input_messages": {
        "source_field": "llm.input_messages",  # ← PLACEHOLDER
        "extraction_method": "direct_copy",     # ← GENERIC
        ...
    },
    ...
}
```

**This requires manual work to:**
1. Research the provider API response structure
2. Figure out how instrumentors flatten it
3. Write navigation rules
4. Write transforms
5. Write field mappings

---

## 🔌 The Integration Point

### WHERE to Inject Schema

**File**: `scripts/generate_provider_template.py`

**Functions to Modify**:
1. `_generate_navigation_rules()` - Line 82
2. `_generate_field_mappings()` - Line 148
3. `_generate_transforms()` - Line 261

### HOW to Integrate

**Current** (Template-Based):
```python
def _generate_navigation_rules(self, provider_dir: Path, provider_name: str):
    """Generate navigation_rules.yaml template."""
    
    template = {
        # Hardcoded placeholder rules
        "extract_input_messages": {...},
        "extract_output_messages": {...},
        ...
    }
```

**ENHANCED** (Schema-Driven):
```python
def _generate_navigation_rules(
    self, 
    provider_dir: Path, 
    provider_name: str,
    schema_path: Path = None  # ← NEW: Accept schema path
):
    """Generate navigation_rules.yaml from provider schema."""
    
    if schema_path and schema_path.exists():
        # SCHEMA-DRIVEN GENERATION
        schema = self._load_provider_schema(schema_path)
        navigation_rules = self._generate_rules_from_schema(
            schema, 
            provider_name
        )
    else:
        # Fallback to template for backward compatibility
        navigation_rules = self._generate_template_rules(provider_name)
    
    template = {
        "version": "1.0",
        "provider": provider_name,
        "dsl_type": "provider_navigation_rules",
        "navigation_rules": navigation_rules
    }
```

---

## 📊 Schema → DSL Mapping Logic

### New Methods to Add

#### 1. Load Provider Schema
```python
def _load_provider_schema(self, schema_path: Path) -> Dict[str, Any]:
    """Load JSON Schema from provider_response_schemas."""
    import json
    
    with open(schema_path) as f:
        return json.load(f)
```

#### 2. Extract Fields from Schema
```python
def _extract_schema_fields(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Recursively extract all fields from JSON Schema.
    
    Returns:
        [
            {
                "path": "choices[].message.content",
                "type": "string",
                "nullable": true,
                "description": "..."
            },
            {
                "path": "choices[].message.tool_calls[].id",
                "type": "string",
                "description": "..."
            },
            ...
        ]
    """
    fields = []
    
    # Walk through schema definitions
    for def_name, definition in schema.get("definitions", {}).items():
        fields.extend(self._walk_schema_object(definition, path_prefix=""))
    
    return fields

def _walk_schema_object(
    self, 
    obj: Dict[str, Any], 
    path_prefix: str
) -> List[Dict[str, Any]]:
    """Recursively walk schema object to extract fields."""
    fields = []
    
    if obj.get("type") == "object":
        for prop_name, prop_def in obj.get("properties", {}).items():
            field_path = f"{path_prefix}.{prop_name}" if path_prefix else prop_name
            
            # Add this field
            fields.append({
                "path": field_path,
                "type": prop_def.get("type"),
                "format": prop_def.get("format"),
                "nullable": prop_def.get("nullable", False),
                "description": prop_def.get("description", "")
            })
            
            # Recurse into nested objects
            if prop_def.get("type") == "object":
                fields.extend(self._walk_schema_object(prop_def, field_path))
            
            # Handle arrays
            elif prop_def.get("type") == "array":
                items = prop_def.get("items", {})
                array_path = f"{field_path}[]"
                fields.extend(self._walk_schema_object(items, array_path))
    
    return fields
```

#### 3. Generate Navigation Rules from Schema
```python
def _generate_rules_from_schema(
    self, 
    schema: Dict[str, Any], 
    provider_name: str
) -> Dict[str, Any]:
    """Generate navigation rules from schema fields."""
    
    # Extract all fields from schema
    fields = self._extract_schema_fields(schema)
    
    navigation_rules = {}
    
    for field in fields:
        # Generate rules for each instrumentor
        for instrumentor in ["openinference", "traceloop", "openlit"]:
            rule_name = f"{instrumentor}_{field['path'].replace('.', '_').replace('[]', '_array')}"
            
            navigation_rules[rule_name] = {
                "source_field": self._map_to_instrumentor_pattern(
                    field['path'], 
                    instrumentor
                ),
                "extraction_method": self._determine_extraction_method(field),
                "nullable": field.get("nullable", False),
                "fallback_value": self._determine_fallback(field),
                "description": field.get("description", "")
            }
    
    return navigation_rules

def _map_to_instrumentor_pattern(self, field_path: str, instrumentor: str) -> str:
    """Map schema field path to instrumentor attribute pattern."""
    
    if instrumentor == "openinference":
        # Map to llm.* namespace
        return f"llm.{field_path}"
    
    elif instrumentor in ["traceloop", "openlit"]:
        # Map to gen_ai.* namespace
        return f"gen_ai.{field_path}"
    
    else:
        # Direct pattern
        return field_path

def _determine_extraction_method(self, field: Dict[str, Any]) -> str:
    """Determine extraction method based on field type."""
    
    # Array reconstruction needed
    if "[]" in field['path']:
        return "array_reconstruction"
    
    # JSON string preservation
    elif field.get("format") == "json-string":
        return "preserve_json_string"
    
    # Direct copy
    else:
        return "direct_copy"

def _determine_fallback(self, field: Dict[str, Any]) -> Any:
    """Determine fallback value based on field type."""
    
    if field.get("nullable"):
        return None
    
    field_type = field.get("type")
    
    if field_type == "string":
        return ""
    elif field_type in ["integer", "number"]:
        return 0
    elif field_type == "boolean":
        return False
    elif field_type == "array":
        return []
    elif field_type == "object":
        return {}
    else:
        return None
```

#### 4. Generate Transforms from Schema
```python
def _generate_transforms_from_schema(
    self, 
    schema: Dict[str, Any], 
    provider_name: str
) -> Dict[str, Any]:
    """Generate transform configs from schema."""
    
    fields = self._extract_schema_fields(schema)
    transforms = {}
    
    for field in fields:
        # Only create transforms for complex fields
        if "[]" in field['path']:
            # Array reconstruction transform
            transform_name = f"extract_{field['path'].replace('.', '_').replace('[]', '_array')}"
            
            transforms[transform_name] = {
                "function_type": "array_reconstruction",
                "implementation": "reconstruct_array_from_flattened",
                "parameters": {
                    "prefix": field['path'].replace("[]", ""),
                    "preserve_json_strings": self._find_json_string_fields(schema, field['path'])
                },
                "description": f"Reconstruct {field['path']} from flattened attributes"
            }
        
        elif field.get("format") == "json-string":
            # JSON string preservation transform
            transform_name = f"extract_{field['path'].replace('.', '_')}"
            
            transforms[transform_name] = {
                "function_type": "string_extraction",
                "implementation": "extract_first_non_empty",
                "parameters": {
                    "preserve_as_json": True
                },
                "description": f"Extract {field['path']} as JSON string"
            }
    
    return transforms
```

#### 5. Generate Field Mappings from Schema
```python
def _generate_mappings_from_schema(
    self, 
    schema: Dict[str, Any], 
    provider_name: str
) -> Dict[str, Any]:
    """Generate field mappings from schema."""
    
    fields = self._extract_schema_fields(schema)
    
    mappings = {
        "inputs": {},
        "outputs": {},
        "config": {},
        "metadata": {}
    }
    
    for field in fields:
        # Determine target section based on field path/type
        section = self._determine_honeyhive_section(field)
        field_name = self._extract_field_name(field['path'])
        
        mappings[section][field_name] = {
            "source_rule": f"extract_{field['path'].replace('.', '_').replace('[]', '_array')}",
            "required": not field.get("nullable", False),
            "description": field.get("description", "")
        }
    
    return mappings

def _determine_honeyhive_section(self, field: Dict[str, Any]) -> str:
    """Determine which HoneyHive section a field belongs to."""
    
    path = field['path']
    
    # Input patterns
    if any(x in path for x in ["input", "prompt", "message", "context"]):
        return "inputs"
    
    # Output patterns
    elif any(x in path for x in ["output", "completion", "response", "tool_call", "refusal", "audio"]):
        return "outputs"
    
    # Config patterns
    elif any(x in path for x in ["temperature", "max_tokens", "top_p", "model"]):
        return "config"
    
    # Metadata patterns (everything else)
    else:
        return "metadata"
```

---

## 🔧 Modified Workflow

### New Schema-Driven Workflow

```
Step 0: Schema Extraction (DONE)
    ↓
provider_response_schemas/openai/v2025-01-30.json
    ↓
Step 1: AUTOMATED Generation from Schema
    ↓
scripts/generate_provider_template.py --provider openai --schema provider_response_schemas/openai/v2025-01-30.json
    ↓
Generates 4 REAL YAML files:
- structure_patterns.yaml (from template, same as before)
- navigation_rules.yaml (FROM SCHEMA ✨)
- field_mappings.yaml (FROM SCHEMA ✨)
- transforms.yaml (FROM SCHEMA ✨)
    ↓
Step 2: OPTIONAL Manual Refinement
    ↓
Developer tweaks if needed (but mostly automated!)
    ↓
Step 3: Compilation
    ↓
config/dsl/compiler.py
    ↓
Loads YAMLs → Compiles to bundle
```

---

## 📋 Implementation Plan

### Phase 1: Enhance generate_provider_template.py

**Add to `ProviderTemplateGenerator` class**:

1. ✅ `_load_provider_schema()` - Load JSON Schema
2. ✅ `_extract_schema_fields()` - Walk schema, extract all fields
3. ✅ `_walk_schema_object()` - Recursive field extraction
4. ✅ `_generate_rules_from_schema()` - Schema → navigation rules
5. ✅ `_map_to_instrumentor_pattern()` - Field → instrumentor attribute
6. ✅ `_determine_extraction_method()` - Field type → extraction method
7. ✅ `_determine_fallback()` - Field type → fallback value
8. ✅ `_generate_transforms_from_schema()` - Schema → transforms
9. ✅ `_find_json_string_fields()` - Find json-string format fields
10. ✅ `_generate_mappings_from_schema()` - Schema → field mappings
11. ✅ `_determine_honeyhive_section()` - Field → inputs/outputs/config/metadata
12. ✅ `_extract_field_name()` - Path → simple field name

**Modify existing methods**:
1. ✅ `_generate_navigation_rules()` - Add schema path parameter, use schema if provided
2. ✅ `_generate_field_mappings()` - Add schema path parameter, use schema if provided
3. ✅ `_generate_transforms()` - Add schema path parameter, use schema if provided
4. ✅ `generate_provider_files()` - Add schema path parameter, pass to methods

**Update CLI**:
```python
parser.add_argument(
    "--schema",
    type=Path,
    help="Path to provider JSON Schema (e.g., provider_response_schemas/openai/v2025-01-30.json)"
)
```

### Phase 2: Test Schema-Driven Generation

```bash
# Generate OpenAI configs from schema
python scripts/generate_provider_template.py \
    --provider openai \
    --schema provider_response_schemas/openai/v2025-01-30.json

# Verify generated YAMLs
ls -lh config/dsl/providers/openai/

# Compile bundle
cd config/dsl
python compiler.py --provider openai

# Test extraction
python -c "from honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor; print('OK')"
```

### Phase 3: Validate Coverage

**Expected Results**:
- ✅ All schema fields mapped to navigation rules
- ✅ All complex fields have transforms
- ✅ All fields mapped to HoneyHive sections
- ✅ 100% coverage (vs current ~30%)

---

## 🎯 Answer to "Where to Plug In?"

**The schema plugs into `scripts/generate_provider_template.py`:**

1. **Add `--schema` CLI argument** to accept schema path
2. **Enhance 3 methods** to consume schema instead of generating templates:
   - `_generate_navigation_rules()` 
   - `_generate_field_mappings()`
   - `_generate_transforms()`
3. **Add 12 new helper methods** for schema processing
4. **Run enhanced script** to auto-generate REAL configs from schema
5. **Compile as usual** with `compiler.py`

**This transforms the DSL generation from:**
- ❌ Manual template → Manual editing → Compilation
- ✅ **Schema → Automated generation → Compilation**

---

## 🚀 Next Steps

1. **Enhance `generate_provider_template.py`** with schema consumption logic
2. **Run for OpenAI** to generate real configs from extracted schema
3. **Validate** generated YAMLs are correct
4. **Compile and test** the updated DSL bundle

---

**Last Updated**: 2025-10-01  
**Status**: Integration point identified, ready to enhance  
**File to Modify**: `scripts/generate_provider_template.py`  
**Lines to Change**: 82-366 (all 3 generation methods)


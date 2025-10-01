# Provider Response Schema Specification

**Version**: 1.0  
**Date**: 2025-01-30  
**Purpose**: Define the standard format for documenting LLM provider API response schemas

---

## 🎯 **Overview**

This specification defines how to document LLM provider API response structures in a machine-readable, versioned format that can be:
- **Validated**: Ensure DSL configs reference valid fields
- **Versioned**: Track API changes over time
- **Compared**: Identify differences between providers
- **Tested**: Validate real API responses against schemas

## 📋 **Schema Format**

### **Directory Structure**

```
provider_response_schemas/
├── version.json                    # Registry metadata
├── README.md                       # Usage guide
├── SCHEMA_SPEC.md                  # This file
├── {provider}/
│   ├── v{YYYY-MM-DD}.json         # Versioned schema
│   ├── CHANGELOG.md               # Version history
│   └── examples/
│       ├── {scenario}.json        # Real response examples
│       └── ...
└── validation/
    ├── validate_schema.py         # Schema validator
    └── test_responses.py          # Response validator
```

### **Schema File Format**

Each provider schema file (`v{YYYY-MM-DD}.json`) must follow this structure:

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "version": "YYYY-MM-DD",
  "provider": "provider_name",
  "last_verified": "YYYY-MM-DD",
  "api_version": "provider_api_version",
  "documentation_url": "https://...",
  "schemas": {
    "ResponseTypeName": {
      // JSON Schema definition
    }
  },
  "metadata": {
    "models": ["model-1", "model-2"],
    "endpoints": ["/v1/chat/completions"],
    "notes": "Additional context"
  }
}
```

## 🔧 **JSON Schema Extensions**

We use standard JSON Schema (Draft 7) with custom extensions for LLM-specific patterns:

### **1. JSON String Fields**

Fields that contain JSON-encoded strings (not objects):

```json
{
  "type": "string",
  "format": "json-string",
  "description": "JSON-encoded object as string",
  "jsonSchema": {
    // Schema of the parsed content
    "type": "object",
    "properties": {
      "location": {"type": "string"}
    }
  }
}
```

**Example**: OpenAI's `function.arguments`:
```json
"arguments": "{\"location\": \"SF\"}"  // ← String, not object
```

### **2. Base64 Encoded Fields**

Fields containing base64-encoded data:

```json
{
  "type": "string",
  "format": "base64",
  "contentType": "audio/wav",
  "description": "Base64-encoded audio data"
}
```

### **3. Discriminated Unions**

Fields whose structure depends on a discriminator:

```json
{
  "type": "array",
  "items": {
    "discriminator": {
      "propertyName": "type",
      "mapping": {
        "text": {"$ref": "#/schemas/TextBlock"},
        "tool_use": {"$ref": "#/schemas/ToolUseBlock"}
      }
    }
  }
}
```

**Example**: Anthropic's `content` blocks where `type` determines structure.

### **4. Nullable with Meaning**

Fields where `null` has semantic meaning:

```json
{
  "oneOf": [
    {"type": "string"},
    {"type": "null"}
  ],
  "nullSemantics": "When null, indicates only tool_calls are present"
}
```

**Example**: OpenAI's `content` field can be `null` when only tool calls.

### **5. Conditional Fields**

Fields that only appear under certain conditions:

```json
{
  "type": "object",
  "properties": {
    "refusal": {
      "type": "string",
      "conditional": {
        "when": "finish_reason == 'refused'",
        "description": "Only present when model refuses"
      }
    }
  }
}
```

## 📝 **Schema Definition Guidelines**

### **1. Naming Conventions**

- **Schema Names**: PascalCase (e.g., `ChatCompletionResponse`)
- **Properties**: snake_case (match provider's actual field names)
- **Types**: Use exact provider terminology

### **2. Required vs. Optional**

- **Required**: Always present in API response
- **Optional**: May be absent (use JSON Schema `required` array)
- **Conditional**: Present only under specific conditions (use custom `conditional`)

### **3. Documentation**

Every schema and field must have:
- **description**: What it represents
- **example**: Real value from API
- **notes**: Edge cases, gotchas, version differences

### **4. References**

Use `$ref` for:
- Reusable schema components
- Nested objects
- Common patterns across responses

### **5. Examples**

Include real API response examples in `examples/` directory:
- One file per scenario
- Actual responses from provider API
- Annotated with comments explaining key fields

## 🔍 **Validation Rules**

### **Schema File Validation**

Each schema file must:
1. ✅ Be valid JSON
2. ✅ Follow JSON Schema Draft 7 spec
3. ✅ Include all required top-level fields
4. ✅ Have matching version in filename and content
5. ✅ Reference documented API endpoint

### **Schema Content Validation**

Each schema definition must:
1. ✅ Define all known response fields
2. ✅ Mark required fields correctly
3. ✅ Use appropriate JSON Schema types
4. ✅ Include descriptions for all fields
5. ✅ Provide examples for complex fields

### **Example File Validation**

Each example response must:
1. ✅ Be valid JSON
2. ✅ Validate against the schema
3. ✅ Represent real API response
4. ✅ Include comments explaining context

## 📊 **Versioning Strategy**

### **Version Format**

Use **date-based versioning**: `v{YYYY-MM-DD}`

**Rationale**: Provider APIs evolve continuously, dates are unambiguous.

### **When to Create New Version**

Create new version when:
- ✅ Provider adds new fields
- ✅ Provider removes/deprecates fields
- ✅ Provider changes field types
- ✅ Provider changes field semantics
- ⚠️  Provider fixes documentation (update existing if no API change)

### **Changelog Requirements**

Each `CHANGELOG.md` must document:
```markdown
# YYYY-MM-DD

## Added
- New field `refusal` for model refusals
- New field `audio` for audio responses

## Changed
- `tool_calls` now supports multiple calls

## Deprecated
- `function_call` (use `tool_calls` instead)

## Removed
- Legacy `prompt` field
```

## 🎯 **DSL Integration**

### **Schema References in DSL**

DSL configs should reference schema versions:

```yaml
# config/dsl/providers/openai/metadata.yaml
provider: openai
schema_version: "2025-01-30"
schema_registry: "provider_response_schemas"
```

### **Field Path Validation**

DSL compiler validates field paths against schema:

```python
# Pseudo-code
def validate_field_mapping(mapping, schema):
    field_path = mapping['source_path']
    
    # Check if path exists in schema
    if not schema.has_path(field_path):
        raise ValidationError(f"Invalid path: {field_path}")
    
    # Check if transform matches field type
    field_type = schema.get_type(field_path)
    if field_type == "json-string" and "parse_json" not in mapping['transforms']:
        raise ValidationError(f"Field {field_path} requires JSON parsing")
```

### **Transform Auto-Detection**

Schema metadata can suggest required transforms:

```json
{
  "type": "string",
  "format": "json-string",
  "suggestedTransforms": ["parse_json"]
}
```

## 🔄 **Maintenance Process**

### **Regular Updates**

1. **Monthly Review**: Check provider documentation for changes
2. **Automated Monitoring**: Track provider changelog/release notes
3. **Community Contributions**: Accept schema updates via PRs

### **Validation Pipeline**

```bash
# On schema update
1. Validate JSON syntax
2. Validate against JSON Schema spec
3. Run example responses through schema
4. Check DSL configs still validate
5. Update version.json registry
```

### **Testing**

```python
# tests/test_provider_schemas.py
def test_openai_schema_validates():
    schema = load_schema("openai/v2025-01-30.json")
    examples = load_examples("openai/examples/")
    
    for example in examples:
        assert validate(example, schema)
```

## 📚 **Complete Example**

See `openai/v2025-01-30.json` for a complete reference implementation.

## ✅ **Compliance Checklist**

Before committing a new schema:

- [ ] Valid JSON syntax
- [ ] Follows naming conventions
- [ ] All fields documented
- [ ] Examples included
- [ ] Changelog updated
- [ ] Passes validation tests
- [ ] DSL configs still validate
- [ ] Version number in filename matches content

---

**Next Steps**: 
1. Create first schema: `openai/v2025-01-30.json`
2. Create validation tools
3. Document additional providers

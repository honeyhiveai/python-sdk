# Provider Response Schema Registry

**Version**: 1.0  
**Purpose**: Machine-readable, versioned documentation of LLM provider API response structures

---

## 🎯 **What Is This?**

This registry contains comprehensive, validated schemas for LLM provider API responses. These schemas:

- **Document**: Exact structure of API responses from each provider
- **Validate**: Enable DSL field path validation
- **Version**: Track API changes over time
- **Compare**: Identify structural differences between providers
- **Inform**: Guide DSL design and transform development

## 📁 **Registry Structure**

```
provider_response_schemas/
├── README.md                          # This file
├── SCHEMA_SPEC.md                     # Schema format specification
├── version.json                       # Registry metadata
├── openai/
│   ├── v2025-01-30.json              # Current schema
│   ├── CHANGELOG.md                  # Version history
│   └── examples/
│       ├── basic_chat.json           # Example responses
│       ├── tool_calls.json
│       ├── refusal.json
│       └── ...
├── anthropic/                         # Coming soon
├── gemini/                            # Coming soon
└── validation/
    ├── validate_schema.py            # Schema validator
    └── test_responses.py             # Response validator
```

## 🚀 **Quick Start**

### **View a Provider Schema**

```bash
# View OpenAI schema
cat provider_response_schemas/openai/v2025-01-30.json | jq .

# View specific field
cat provider_response_schemas/openai/v2025-01-30.json | \
    jq '.schemas.ToolCall'
```

### **Validate an API Response**

```python
import json
import jsonschema

# Load schema
with open('provider_response_schemas/openai/v2025-01-30.json') as f:
    schema_doc = json.load(f)
    
# Load example response
with open('provider_response_schemas/openai/examples/basic_chat.json') as f:
    response = json.load(f)

# Validate
schema = schema_doc['schemas']['ChatCompletionResponse']
jsonschema.validate(response, schema)  # Raises if invalid
```

### **Use in DSL Design**

```yaml
# config/dsl/providers/openai/metadata.yaml
provider: openai
schema_version: "2025-01-30"
schema_registry: "provider_response_schemas"

# Field mappings can reference schema paths
field_mappings:
  tool_calls:
    # Schema ensures this path exists
    source_path: "choices[0].message.tool_calls"
    
    # Schema indicates arguments is JSON string
    transforms:
      - type: "parse_json"
        field: "[].function.arguments"  # Required per schema
```

## 📋 **Current Coverage**

| Provider | Latest Version | Status | Validation | Examples | Scope |
|----------|----------------|--------|------------|----------|-------|
| **OpenAI** | v2025-01-30 | ✅ Complete | ✅ Phase 5 | 11 | Chat completions (standard + streaming) |
| **Anthropic** | - | ⏳ Planned | - | - | Content blocks, thinking |
| **Gemini** | - | ⏳ Planned | - | - | Parts array, multimodal |
| **Cohere** | - | ⏳ Planned | - | - | - |
| **Mistral** | - | ⏳ Planned | - | - | - |
| **AWS Bedrock** | - | ⏳ Planned | - | - | - |

**OpenAI Details**:
- Schema definitions: 15
- Examples: 11 (basic chat, tool calls, refusal, audio, multimodal, streaming, multiple choices, errors, content filter, max tokens, logprobs)
- Validation: All examples pass schema validation
- Critical findings documented: JSON string arguments, null handling, base64 audio, array flattening
- **DSL Ready**: ✅ Ready for consumption by DSL framework

## 🔍 **Key Features**

### **1. JSON Schema Extensions**

We extend standard JSON Schema for LLM-specific patterns:

```json
{
  "type": "string",
  "format": "json-string",  // ← Custom: JSON-encoded string
  "jsonSchema": {           // ← Schema of parsed content
    "type": "object"
  }
}
```

See `SCHEMA_SPEC.md` for all extensions.

### **2. Semantic Annotations**

Schemas include semantic meaning:

```json
{
  "content": {
    "oneOf": [{"type": "string"}, {"type": "null"}],
    "nullSemantics": "Null means only tool_calls, no text"  // ← Meaning!
  }
}
```

### **3. Real Examples**

Every schema includes real API responses:

```json
// examples/tool_calls.json
{
  "_comment": "Real response from OpenAI API",
  "_critical_note": "arguments is a JSON STRING!",
  "tool_calls": [...]
}
```

## 🔧 **For DSL Developers**

### **Field Path Validation**

```python
# Validate DSL field mappings against schema
def validate_dsl_mapping(mapping, provider_schema):
    # Check path exists
    assert provider_schema.has_path(mapping['source_path'])
    
    # Check transform requirements
    field_type = provider_schema.get_type(mapping['source_path'])
    if field_type == 'json-string':
        assert 'parse_json' in mapping['transforms']
```

### **Transform Auto-Detection**

```python
# Auto-detect required transforms from schema
def detect_required_transforms(field_path, schema):
    field_def = schema.get_field(field_path)
    
    transforms = []
    if field_def.get('format') == 'json-string':
        transforms.append('parse_json')
    if field_def.get('format') == 'base64':
        transforms.append('decode_base64')
    
    return transforms
```

## 📊 **Critical Findings**

### **OpenAI**

**🔥 Tool Call Arguments are JSON Strings**:
```json
"arguments": "{\"location\": \"SF\"}"  // ← STRING, not object!
```
**DSL Must**: Parse JSON string to get actual arguments

**🔥 Nullable Content with Meaning**:
```json
"content": null  // ← Means "only tool_calls, no text"
```
**DSL Must**: Handle null semantics correctly

**🔥 New Optional Fields**:
```json
"refusal": "I cannot help..."  // ← New safety field
"audio": {...}                  // ← New audio field
```
**DSL Must**: Support optional fields

## 🔄 **Maintenance**

### **Adding a New Provider**

1. Create `{provider}/` directory
2. Research provider API documentation
3. Create `v{YYYY-MM-DD}.json` schema
4. Add example responses in `examples/`
5. Create `CHANGELOG.md`
6. Validate schema
7. Update this README

### **Updating Existing Schema**

1. Check provider changelog/docs
2. Create new `v{YYYY-MM-DD}.json`
3. Update `CHANGELOG.md`
4. Add new examples if needed
5. Test DSL configs still validate

## ✅ **Quality Standards**

All schemas must:
- ✅ Follow `SCHEMA_SPEC.md` format
- ✅ Be valid JSON Schema Draft 7
- ✅ Include real example responses
- ✅ Document all known fields
- ✅ Mark required vs optional correctly
- ✅ Include descriptions for all fields
- ✅ Pass validation tests

## 📚 **Related Documentation**

- [Schema Specification](./SCHEMA_SPEC.md) - Schema format details
- [DSL Design](../config/dsl/README.md) - How DSL uses schemas
- [Transform Registry](../src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py) - Transform implementations

## 🎯 **Future Enhancements**

- [ ] Automated schema extraction from provider APIs
- [ ] Diff tool to compare schema versions
- [ ] Migration tool for DSL configs when schemas change
- [ ] Schema coverage metrics
- [ ] Automated validation against live APIs
- [ ] Community contribution workflow

---

**Status**: 🚧 Active Development  
**Next**: Extract Anthropic schemas  
**Questions**: Open an issue or see [Contributing Guidelines](../CONTRIBUTING.md)

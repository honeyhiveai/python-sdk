# OpenAI - Schema Source Documentation

**Provider**: OpenAI  
**Framework Version**: 1.0 (SDK-First)  
**Last Updated**: 2025-09-30

---

## Strategy 1: Dedicated OpenAPI Repository

**Status**: ✅ FOUND  
**Repository**: https://github.com/openai/openai-openapi  
**Verified**: 2025-09-30

### Primary Source (Stainless-hosted)
- **URL**: https://app.stainless.com/api/spec/documented/openai/openapi.documented.yml
- **Type**: OpenAPI YAML (documented)
- **Status**: Most recent version
- **Maintained By**: OpenAI via Stainless

### Alternate Source (Manual Branch)
- **Branch**: https://github.com/openai/openai-openapi/tree/manual_spec
- **Type**: OpenAPI YAML (manually updated)
- **Status**: Manually maintained version

### Direct Download
```bash
# Download most recent documented spec (recommended)
curl -o openai-openapi-documented.yml \
  https://app.stainless.com/api/spec/documented/openai/openapi.documented.yml

# Or download manual spec from GitHub
curl -o openai-openapi-manual.yml \
  https://raw.githubusercontent.com/openai/openai-openapi/manual_spec/openapi.yaml
```

### Notes
- **BEST SOURCE** for complete API schema
- Machine-readable, versioned specification
- Regularly updated with API changes
- MIT License

---

## Strategy 2: OpenAPI in SDK Repository

**Status**: ⏩ SKIPPED (Strategy 1 succeeded)

---

## Strategy 3: Published OpenAPI URL

**Status**: ❌ NOT FOUND  
**Checked**: OpenAI documentation, platform.openai.com  
**Verified**: 2025-09-30

### Search Results
- No publicly downloadable OpenAPI specification URL
- Moving to next strategy

---

## Strategy 4: Protobuf Definitions

**Status**: ⏩ SKIPPED (Strategy 1 succeeded)

---

## Strategy 5: SDK Type Definitions

**Status**: 📋 SUPPLEMENTARY (for validation)

**Python SDK**: https://github.com/openai/openai-python  
**TypeScript SDK**: https://github.com/openai/openai-node  

### Python SDK Type Definitions
- **File**: `src/openai/types/chat/chat_completion.py`
- **Framework**: Pydantic v2
- **Purpose**: Validate OpenAPI schema accuracy

### TypeScript SDK Type Definitions  
- **File**: `src/resources/chat/completions.ts`
- **Framework**: TypeScript interfaces
- **Purpose**: Cross-validation

---

## Strategy 6: Manual Documentation

**Status**: ⏳ SKIPPED (Strategy 1 succeeded)

---

## Extraction History

### 2025-09-30: Initial Schema Extraction (COMPLETED)
- **Method**: Strategy 1 (Dedicated OpenAPI Repository)
- **Source**: https://github.com/openai/openai-openapi
- **Primary File**: https://app.stainless.com/api/spec/documented/openai/openapi.documented.yml
- **OpenAPI Version**: 3.1.0
- **API Version**: 2.3.0
- **File Size**: 2.1 MB
- **Download Date**: 2025-09-30
- **Extracted By**: AI Assistant (Framework v1.0)

#### Key Schema Locations in OpenAPI Spec
- **CreateChatCompletionResponse**: Line 31698
- **ChatCompletionResponseMessage**: Line 30046
- **ChatCompletionMessageToolCalls**: Line 29526
- **ChatCompletionMessageToolCall**: Line 29463

#### Critical Findings
1. **Tool Call Arguments Format**: `function.arguments` is `type: string` (JSON-serialized), NOT an object
2. **Content Field**: Can be `string` or `null` (anyOf)
3. **Refusal Support**: Dedicated `refusal` field for safety refusals
4. **Audio Support**: Optional `audio` object with base64 data
5. **Annotations**: Array of URL citations (web search tool)

---

## Source Priority for Updates

When updating schemas, check sources in this order:

1. **OpenAPI Repository** (primary)
   - URL: https://github.com/openai/openai-openapi
   - Check: Weekly (if API changes suspected)

2. **Python SDK Types** (validation)
   - URL: https://github.com/openai/openai-python
   - Check: After OpenAPI update

3. **Official Documentation** (fallback)
   - URL: https://platform.openai.com/docs/api-reference
   - Check: If discrepancies found

---

## Verification Checklist

- [x] Strategy 1 executed and documented
- [ ] OpenAPI spec downloaded
- [ ] Schema extracted
- [ ] Examples validated
- [ ] Integration tested

---

**Next Phase**: Phase 2 - Schema Extraction  
**Next Task**: Download and extract OpenAPI specification

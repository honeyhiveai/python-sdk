# Phase 0.1: Verify Provider

## 🎯 **Objective**

Verify the LLM provider exists, is actively maintained, and has an official API with response objects that need schema documentation.

---

## 📋 **Tasks**

### **Task 1.1: Confirm Official Provider Name**

**Action**: Verify the exact official name of the provider.

**How**:
1. Search for provider's official website
2. Find "About" or "Company" page
3. Document official company/product name
4. Note any branding variations

**Evidence Required**:
- Official website URL
- Official product name
- Screenshot or quote showing official name

**Example**:
```markdown
Provider: OpenAI
Official Name: OpenAI
Product: OpenAI API
Website: https://openai.com
Verified: 2025-09-30
```

---

### **Task 1.2: Verify Provider Has Public API**

**Action**: Confirm the provider offers a public API with programmatic access.

**How**:
1. Search for "{provider} API documentation"
2. Locate API reference page
3. Verify API is publicly accessible (not private/enterprise only)
4. Check if API requires paid access or has free tier

**Evidence Required**:
- API documentation URL
- Access model (free tier, paid, etc.)
- API authentication method

**Example**:
```markdown
API Available: Yes
API Docs: https://platform.openai.com/docs/api-reference
Access Model: Free tier + paid tiers
Authentication: API key
Verified: 2025-09-30
```

**⚠️ WARNING**: If provider does NOT have a public API, STOP. This framework is for public API providers only.

---

### **Task 1.3: Verify Provider Returns JSON Responses**

**Action**: Confirm the provider's API returns structured JSON responses (not plain text, HTML, etc.).

**How**:
1. Find API documentation for "Response Format" or "Response Structure"
2. Locate example responses
3. Verify responses are JSON-structured
4. Note if responses use OpenAPI/Swagger specs

**Evidence Required**:
- Link to response format documentation
- Example JSON response (from docs)
- Response content-type

**Example**:
```markdown
Response Format: JSON
Content-Type: application/json
Example Found: https://platform.openai.com/docs/api-reference/chat/create#chat-create-response
Verified: 2025-09-30
```

**⚠️ WARNING**: If provider does NOT return JSON, STOP. This framework is for JSON-based APIs only.

---

### **Task 1.4: Identify Provider Category**

**Action**: Categorize the provider by type.

**Categories**:
- **LLM Provider**: Provides large language model inference (OpenAI, Anthropic, Google, etc.)
- **Embedding Provider**: Provides text embedding services
- **Multimodal Provider**: Provides image/video/audio + text models
- **Other**: Specialized AI services

**Evidence Required**:
- Primary service category
- List of capabilities (chat, completion, embedding, etc.)

**Example**:
```markdown
Category: LLM Provider (Multimodal)
Capabilities:
- Chat completions
- Text completions
- Embeddings
- Image generation
- Audio transcription
Verified: 2025-09-30
```

---

## ✅ **Quality Gate: Provider Verification**

Before proceeding to Task 2, verify:

- ✅ Official provider name documented
- ✅ Provider has public API
- ✅ API returns JSON responses
- ✅ Provider category identified
- ✅ All URLs documented with dates

---

## 📊 **Output**

Create or update: `provider_response_schemas/{provider}/PROVIDER_INFO.md`

**Template**:
```markdown
# {Provider} - Provider Information

## Official Details
- **Official Name**: {name}
- **Website**: {url}
- **Verified**: {YYYY-MM-DD}

## API Details
- **API Docs**: {url}
- **Access Model**: {free/paid/enterprise}
- **Authentication**: {method}
- **Response Format**: JSON
- **Content-Type**: application/json

## Provider Category
- **Primary Category**: {category}
- **Capabilities**:
  - {capability 1}
  - {capability 2}
  - ...

## Verification
- **Verified By**: {AI Assistant / Human}
- **Verification Date**: {YYYY-MM-DD}
- **Last Updated**: {YYYY-MM-DD}

## Notes
{Any important notes about provider}
```

---

## 🎯 **Navigation**

### **Current Phase**: 0 - Pre-Research Setup
### **Current Task**: 1 - Verify Provider

### **Next Step**:
```
🎯 NEXT-MANDATORY: task-2-check-existing-schema.md
```

---

**Phase**: 0  
**Task**: 1  
**Status**: Active

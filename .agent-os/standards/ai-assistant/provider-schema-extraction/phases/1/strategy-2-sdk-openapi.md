# Phase 1: Strategy 2 - OpenAPI in SDK Repository

**🎯 Check if SDKs contain OpenAPI specs**

---

## 🛑 **EXECUTION**

### **Step 1: Locate Official SDKs**

🛑 EXECUTE-NOW: Search for official Python SDK
```bash
# GitHub search: "{provider} official python sdk"
# GitHub search: "org:{provider} python"
```

📊 COUNT-AND-DOCUMENT: Python SDK repos found: [NUMBER]
⚠️ EVIDENCE-REQUIRED: Python SDK URL: [URL or NONE]

🛑 EXECUTE-NOW: Search for official TypeScript SDK
```bash
# GitHub search: "{provider} official typescript sdk"  
# GitHub search: "{provider} node sdk"
```

📊 COUNT-AND-DOCUMENT: TypeScript SDK repos found: [NUMBER]
⚠️ EVIDENCE-REQUIRED: TypeScript SDK URL: [URL or NONE]

### **Step 2: Check SDKs for OpenAPI Files**

🛑 EXECUTE-NOW: Browse SDK repositories for OpenAPI files
```bash
# Check these locations in each SDK:
# - /openapi.yaml
# - /swagger.json  
# - /spec/openapi.yaml
# - /docs/openapi.yaml
```

📊 QUANTIFY-RESULTS: OpenAPI file in Python SDK: [YES/NO]
📊 QUANTIFY-RESULTS: OpenAPI file in TypeScript SDK: [YES/NO]

### **Step 3: Document Findings**

🛑 EXECUTE-NOW: Update SDK_SOURCES.md
```markdown
## Strategy 2: OpenAPI in SDK Repository

**Status**: [✅ FOUND | ❌ NOT FOUND]
**SDK**: [Python | TypeScript]
**Repository**: [URL]
**File Path**: [path/to/openapi.yaml]
**Verified**: [YYYY-MM-DD]
```

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Strategy 2 Complete
- [ ] Python SDK searched ✅/❌
- [ ] TypeScript SDK searched ✅/❌
- [ ] Results documented ✅/❌

---

## 🎯 **NAVIGATION**

### **If FOUND ✅**:
📊 QUANTIFY-RESULTS: OpenAPI in SDK: YES
🛑 UPDATE-TABLE: Phase 1 → OpenAPI found in SDK
🎯 NEXT-MANDATORY: ../2/extract-openapi-spec.md

### **If NOT FOUND ❌**:
📊 QUANTIFY-RESULTS: OpenAPI in SDK: NO
🛑 UPDATE-TABLE: Phase 1.2 → Strategy 2 failed, trying Strategy 3
🎯 NEXT-MANDATORY: [strategy-3-published-url.md](strategy-3-published-url.md)

---

**Phase**: 1  
**Strategy**: 2  
**Lines**: ~80

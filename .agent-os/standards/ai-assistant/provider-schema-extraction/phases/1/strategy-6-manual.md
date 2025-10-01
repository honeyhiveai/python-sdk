# Phase 1: Strategy 6 - Manual Documentation Extraction

**🎯 Last resort: manual schema extraction from docs**

---

## 🚨 **WARNING**

⚠️ This is the LAST RESORT strategy when:
- No OpenAPI spec available
- No SDK repositories found
- No protobuf definitions
- No type definitions

🚨 FRAMEWORK-VIOLATION: Only use if Strategies 1-5 all failed

---

## 🛑 **EXECUTION**

### **Step 1: Locate API Documentation**

🛑 EXECUTE-NOW: Find official API reference
```bash
# Search for:
# - https://{provider}.com/docs/api
# - https://docs.{provider}.com/api-reference
# - https://developer.{provider}.com/reference
```

📊 COUNT-AND-DOCUMENT: API documentation URLs found: [NUMBER]
⚠️ EVIDENCE-REQUIRED: Primary docs URL: [URL]

### **Step 2: Document Manual Approach**

🛑 EXECUTE-NOW: Update SDK_SOURCES.md
```markdown
## Strategy 6: Manual Documentation Extraction

**Status**: ⚠️ MANUAL REQUIRED

### Documentation
- **API Reference**: [URL]
- **Method**: Manual schema extraction
- **Verified**: [YYYY-MM-DD]

### Extraction Plan
1. Read API reference documentation
2. Manually document response structures
3. Create JSON Schema by hand
4. Validate with real API calls (if possible)

**Note**: This is time-consuming and error-prone.
Provider should be encouraged to publish OpenAPI spec.
```

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Strategy 6 Complete
- [ ] API documentation located ✅/❌
- [ ] Manual extraction plan documented ✅/❌
- [ ] SDK_SOURCES.md updated ✅/❌

---

## 🎯 **NAVIGATION**

### **Next Step (Manual Extraction)**:
📊 QUANTIFY-RESULTS: Automated extraction possible: NO
🛑 UPDATE-TABLE: Phase 1 → Manual extraction required
🎯 NEXT-MANDATORY: ../2/manual-schema-extraction.md

---

**Phase**: 1  
**Strategy**: 6  
**Lines**: ~73

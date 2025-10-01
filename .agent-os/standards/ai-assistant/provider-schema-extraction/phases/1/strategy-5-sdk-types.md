# Phase 1: Strategy 5 - SDK Type Definitions

**🎯 Extract schemas from SDK type definitions (fallback)**

---

## 🛑 **EXECUTION**

### **Step 1: Locate Python Type Files**

🛑 EXECUTE-NOW: Find Python type definition files
```bash
# Search Python SDK for:
# - **/types/**/*.py
# - **/models/**/*.py
# - Files with Pydantic BaseModel classes
```

📊 COUNT-AND-DOCUMENT: Python type files found: [NUMBER]
⚠️ EVIDENCE-REQUIRED: Key type files (top 5):
- [file 1 path]
- [file 2 path]
- [file 3 path]

### **Step 2: Locate TypeScript Type Files**

🛑 EXECUTE-NOW: Find TypeScript interface files
```bash
# Search TypeScript SDK for:
# - **/*.d.ts
# - **/types/**/*.ts
# - Files with interface definitions
```

📊 COUNT-AND-DOCUMENT: TypeScript type files found: [NUMBER]
⚠️ EVIDENCE-REQUIRED: Key type files (top 5):
- [file 1 path]
- [file 2 path]
- [file 3 path]

### **Step 3: Document Type Source**

🛑 EXECUTE-NOW: Update SDK_SOURCES.md
```markdown
## Strategy 5: SDK Type Definitions

**Status**: ✅ FOUND (fallback)

### Python SDK Types
- **Repository**: [URL]
- **Version**: [version]
- **Type Files**: [NUMBER] files
- **Key Files**: [list top 5]

### TypeScript SDK Types
- **Repository**: [URL]
- **Version**: [version]
- **Type Files**: [NUMBER] files
- **Key Files**: [list top 5]

**Note**: Requires manual parsing and schema generation
```

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Strategy 5 Complete
- [ ] Python type files located ✅/❌
- [ ] TypeScript type files located ✅/❌
- [ ] SDK_SOURCES.md updated ✅/❌

---

## 🎯 **NAVIGATION**

### **Next Step (Type Extraction Required)**:
📊 QUANTIFY-RESULTS: SDK type definitions found: YES
🛑 UPDATE-TABLE: Phase 1 → SDK types located (requires parsing)
🎯 NEXT-MANDATORY: ../2/parse-sdk-type-definitions.md

---

**Phase**: 1  
**Strategy**: 5  
**Lines**: ~77

# Phase 2: Schema Extraction

**🎯 Extract or convert schema based on Phase 1 discovery**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Phase 1 Complete
- [ ] Phase 1 discovery complete ✅/❌
- [ ] Schema source identified ✅/❌
- [ ] SDK_SOURCES.md updated ✅/❌
- [ ] Strategy documented (1-6) ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without Phase 1 completion

---

## 🛤️ **PATH SELECTION**

**Route based on Phase 1 strategy:**

### **Path A: OpenAPI Spec Extraction**
**Use if**: Strategy 1, 2, or 3 succeeded (OpenAPI found)
- ✅ No conversion needed
- ✅ Already in JSON Schema format
- 🎯 NEXT-MANDATORY: [path-a-extract-openapi.md](path-a-extract-openapi.md)

---

### **Path B: Protobuf Conversion**
**Use if**: Strategy 4 succeeded (Protobuf found)
- ⚠️ Requires conversion to JSON Schema
- ⚠️ May need custom tooling
- 🎯 NEXT-MANDATORY: [path-b-convert-protobuf.md](path-b-convert-protobuf.md)

---

### **Path C: SDK Type Parsing**
**Use if**: Strategy 5 succeeded (SDK types found)
- ⚠️ Requires parsing Pydantic/TypeScript
- ⚠️ Requires schema generation
- 🎯 NEXT-MANDATORY: [path-c-parse-sdk-types.md](path-c-parse-sdk-types.md)

---

### **Path D: Manual Extraction**
**Use if**: Strategy 6 (manual required)
- ❌ Time-consuming manual process
- ❌ Error-prone
- 🎯 NEXT-MANDATORY: [path-d-manual-extraction.md](path-d-manual-extraction.md)

---

## 🛑 **EXECUTION**

⚠️ MUST-COMPLETE: Select path based on Phase 1 strategy

🚨 FRAMEWORK-VIOLATION: If path doesn't match Phase 1 strategy

---

**Phase**: 2  
**Type**: Path Router  
**Lines**: ~65

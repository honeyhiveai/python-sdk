# Phase 1: Strategy 4 - Protobuf Definitions

**🎯 Check for gRPC/Protobuf schema definitions**

---

## 🛑 **EXECUTION**

### **Step 1: Search SDKs for Protobuf Files**

🛑 EXECUTE-NOW: Search SDK repositories for .proto files
```bash
# In Python SDK repository:
# Search for: "*.proto" files
# Common locations: /proto/, /protos/, /grpc/

# In TypeScript SDK repository:
# Same search pattern
```

📊 COUNT-AND-DOCUMENT: .proto files found in Python SDK: [NUMBER]
📊 COUNT-AND-DOCUMENT: .proto files found in TypeScript SDK: [NUMBER]

### **Step 2: Identify Service Definitions**

⚠️ EVIDENCE-REQUIRED: If .proto files found:
- File paths: [list paths]
- Service names: [list service names]
- Contains response messages: [YES/NO]

### **Step 3: Document Source**

🛑 EXECUTE-NOW: Update SDK_SOURCES.md
```markdown
## Strategy 4: Protobuf Definitions

**Status**: [✅ FOUND | ❌ NOT FOUND]
**SDK**: [Python | TypeScript]
**Repository**: [URL]
**Proto Files**: [NUMBER] files
**Service**: [service name]
**Verified**: [YYYY-MM-DD]

### Proto Files
- [path/to/file1.proto]
- [path/to/file2.proto]
```

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Strategy 4 Complete
- [ ] SDK repositories searched ✅/❌
- [ ] Proto files catalogued ✅/❌
- [ ] SDK_SOURCES.md updated ✅/❌

---

## 🎯 **NAVIGATION**

### **If FOUND ✅**:
📊 QUANTIFY-RESULTS: Protobuf definitions found: YES
🛑 UPDATE-TABLE: Phase 1 → Protobuf files located
🎯 NEXT-MANDATORY: ../2/convert-protobuf-to-schema.md

### **If NOT FOUND ❌**:
📊 QUANTIFY-RESULTS: Protobuf definitions found: NO
🛑 UPDATE-TABLE: Phase 1.4 → Strategy 4 failed, trying Strategy 5
🎯 NEXT-MANDATORY: [strategy-5-sdk-types.md](strategy-5-sdk-types.md)

---

**Phase**: 1  
**Strategy**: 4  
**Lines**: ~75

# Phase 2: Path A - Extract OpenAPI Spec

**🎯 Download and extract OpenAPI specification**

---

## 🛑 **EXECUTION**

### **Step 1: Download OpenAPI Spec**

🛑 EXECUTE-NOW: Download spec from source identified in Phase 1
```bash
# Use URL from SDK_SOURCES.md
curl -o /tmp/{provider}-openapi.yaml {URL}
```

🛑 PASTE-OUTPUT: Download confirmation
📊 QUANTIFY-RESULTS: Download successful: [YES/NO]
📊 COUNT-AND-DOCUMENT: File size: [KB]

### **Step 2: Verify OpenAPI Format**

🛑 EXECUTE-NOW: Check OpenAPI version
```bash
# For YAML
head -n 5 /tmp/{provider}-openapi.yaml | grep "openapi:"

# For JSON
jq '.openapi' /tmp/{provider}-openapi.json
```

🛑 PASTE-OUTPUT: Version check result
⚠️ EVIDENCE-REQUIRED: OpenAPI version: [version]

### **Step 3: Extract Response Schemas**

🛑 EXECUTE-NOW: List all response schemas
```bash
# For YAML
yq '.components.schemas | keys' /tmp/{provider}-openapi.yaml

# For JSON
jq '.components.schemas | keys' /tmp/{provider}-openapi.json
```

🛑 PASTE-OUTPUT: Schema list
📊 COUNT-AND-DOCUMENT: Response schemas found: [NUMBER]

### **Step 4: Save to Project**

🛑 EXECUTE-NOW: Copy to extraction directory
```bash
cp /tmp/{provider}-openapi.yaml \
   provider_response_schemas/{provider}/openapi-{version}.yaml
```

📊 QUANTIFY-RESULTS: File saved: YES

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: OpenAPI Extraction Complete
- [ ] Spec downloaded ✅/❌
- [ ] OpenAPI version verified ✅/❌
- [ ] Schemas catalogued ✅/❌
- [ ] File saved to project ✅/❌

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 2 → OpenAPI spec extracted
🎯 NEXT-MANDATORY: ../3/shared-analysis.md

---

**Phase**: 2  
**Path**: A  
**Lines**: ~75

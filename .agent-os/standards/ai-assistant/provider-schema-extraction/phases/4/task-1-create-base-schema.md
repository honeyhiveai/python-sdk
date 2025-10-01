# Phase 4.1: Create Base JSON Schema

**🎯 Convert extracted data to formal JSON Schema**

---

## 🛑 **EXECUTION**

### **Step 1: Initialize Schema Structure**

🛑 EXECUTE-NOW: Create base schema file
```bash
cat > provider_response_schemas/{provider}/v{YYYY-MM-DD}.json << 'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://honeyhive.ai/schemas/{provider}/v{YYYY-MM-DD}",
  "title": "{Provider} API Response Schema",
  "description": "Response schema for {Provider} API",
  "type": "object",
  "properties": {},
  "required": []
}
EOF
```

📊 QUANTIFY-RESULTS: Base schema created: YES

### **Step 2: Extract Schema from OpenAPI/Examples**

⚠️ EVIDENCE-REQUIRED: Main response types identified:
- Response type 1: [name] - [description]
- Response type 2: [name] - [description]

📊 COUNT-AND-DOCUMENT: Response types: [NUMBER]

### **Step 3: Add Field Definitions**

🛑 EXECUTE-NOW: Add properties from examples
```json
{
  "properties": {
    "id": {"type": "string"},
    "object": {"type": "string", "const": "..."},
    "created": {"type": "integer"},
    // ... add all fields
  }
}
```

📊 COUNT-AND-DOCUMENT: Fields defined: [NUMBER]

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Base Schema Created
- [ ] Valid JSON Schema syntax ✅/❌
- [ ] All major fields included ✅/❌
- [ ] Types properly defined ✅/❌

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 4.1 → Base schema created
🎯 NEXT-MANDATORY: [task-2-add-extensions.md](task-2-add-extensions.md)

---

**Phase**: 4  
**Task**: 1  
**Lines**: ~70

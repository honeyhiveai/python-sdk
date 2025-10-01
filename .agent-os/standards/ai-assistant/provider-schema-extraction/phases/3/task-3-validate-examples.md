# Phase 3.3: Validate Examples

**🎯 Verify examples are valid and complete**

---

## 🛑 **EXECUTION**

### **Step 1: Validate JSON Syntax**

🛑 EXECUTE-NOW: Check all examples are valid JSON
```bash
cd provider_response_schemas/{provider}/examples/
for file in *.json; do
    echo "Validating: $file"
    jq empty "$file" && echo "✅ Valid" || echo "❌ Invalid"
done
```

🛑 PASTE-OUTPUT: Validation results
📊 COUNT-AND-DOCUMENT: Valid examples: [X/Y]

### **Step 2: Check Completeness**

⚠️ EVIDENCE-REQUIRED: Verify each example has:
- [ ] Complete response structure
- [ ] All required fields present
- [ ] Realistic values (not placeholders)
- [ ] Source URL documented

📊 QUANTIFY-RESULTS: All examples complete: [YES/NO]

### **Step 3: Document Example Inventory**

🛑 EXECUTE-NOW: Create examples README
```markdown
# {Provider} Response Examples

## Basic Examples
- `basic_chat.json` - [description] ([source URL])
- `{example2}.json` - [description] ([source URL])

## Edge Cases
- `tool_calls.json` - [description] ([source URL])
- `{edge2}.json` - [description] ([source URL])

Total Examples: [NUMBER]
```

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Examples Validated
- [ ] All examples valid JSON ✅/❌
- [ ] All examples complete ✅/❌
- [ ] At least 5 total examples ✅/❌
- [ ] Examples documented ✅/❌

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 3 → COMPLETE (examples validated)
🎯 NEXT-MANDATORY: ../4/shared-analysis.md

---

**Phase**: 3  
**Task**: 3  
**Lines**: ~70

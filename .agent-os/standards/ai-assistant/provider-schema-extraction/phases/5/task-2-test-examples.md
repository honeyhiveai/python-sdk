# Phase 5.2: Test Schema Against Examples

**🎯 Validate all examples against schema**

---

## 🛑 **EXECUTION**

### **Step 1: Install Validation Tool**

🛑 EXECUTE-NOW: Ensure jsonschema is available
```bash
python -m pip show jsonschema || python -m pip install jsonschema
```

📊 QUANTIFY-RESULTS: Validation tool ready: YES

### **Step 2: Test Each Example**

🛑 EXECUTE-NOW: Validate all examples
```bash
cd provider_response_schemas/{provider}

for example in examples/*.json; do
    echo "Testing: $example"
    python -m jsonschema -i "$example" v{YYYY-MM-DD}.json
done
```

🛑 PASTE-OUTPUT: Validation results

📊 COUNT-AND-DOCUMENT: Examples tested: [NUMBER]
📊 COUNT-AND-DOCUMENT: Examples passing: [NUMBER]
📊 QUANTIFY-RESULTS: All examples pass: [YES/NO]

### **Step 3: Fix Validation Failures**

⚠️ EVIDENCE-REQUIRED: If failures exist:
- Failed example: [filename]
- Error: [error message]
- Fix applied: [description]

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Example Testing Complete
- [ ] All examples tested ✅/❌
- [ ] All examples pass validation ✅/❌
- [ ] Failures documented and fixed ✅/❌

🚨 FRAMEWORK-VIOLATION: If examples don't validate

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 5.2 → Examples validated
🎯 NEXT-MANDATORY: [task-3-check-completeness.md](task-3-check-completeness.md)

---

**Phase**: 5  
**Task**: 2  
**Lines**: ~70

# Task 7.4: Transform Validation

**🎯 Validate all transforms complete and ready for compilation**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 7.3 complete (Cost calculation defined) ✅/❌
- [ ] transforms.yaml exists with 3+ transforms ✅/❌
- [ ] YAML compiles ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Count Total Transforms**

🛑 EXECUTE-NOW: Count transforms in transforms.yaml

```bash
grep -c "^[a-z_]*:" config/dsl/providers/{provider}/transforms.yaml
```

🛑 PASTE-OUTPUT: Total transform count

📊 COUNT-AND-DOCUMENT: Total transforms: [NUMBER]

### **Step 2: Validate Required Transforms Present**

🛑 EXECUTE-NOW: Verify minimum required transforms

Required transforms present:
- [ ] extract_message_content_by_role ✅/❌
- [ ] normalize_finish_reason ✅/❌
- [ ] calculate_cost ✅/❌

📊 QUANTIFY-RESULTS: Minimum 3 transforms present: YES/NO

### **Step 3: Validate Transform Completeness**

🛑 EXECUTE-NOW: Check each transform has required fields

For each transform, verify:
- [ ] type field present ✅/❌
- [ ] description present ✅/❌
- [ ] parameters defined ✅/❌
- [ ] implementation = "python" ✅/❌

📊 QUANTIFY-RESULTS: All transforms complete: YES/NO

### **Step 4: Validate Data Sources**

🛑 EXECUTE-NOW: Confirm transforms use verified data

Data source validation:
- Message extraction: Uses Phase 2 message structure: YES/NO
- Finish reason: Uses Phase 3.3 finish values: YES/NO
- Cost calculation: Uses Phase 3.2 pricing (2025-09-30+): YES/NO

📊 QUANTIFY-RESULTS: All transforms use verified data: YES/NO

### **Step 5: Cross-Check with Field Mappings**

🛑 EXECUTE-NOW: Verify field_mappings.yaml references these transforms

From field_mappings.yaml:
- finish_reason field has `transform: normalize_finish_reason`: YES/NO
- cost field has `transform: calculate_cost`: YES/NO

📊 QUANTIFY-RESULTS: Field mappings reference transforms: YES/NO

### **Step 6: Final YAML Compilation Test**

🛑 EXECUTE-NOW: Test complete transforms.yaml compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/transforms.yaml'))"
```

🛑 PASTE-OUTPUT: Final compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 7: Document Complete Transforms**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Transforms - Complete**

**Total Transforms**: [NUMBER]

**Transform Summary**:
1. **extract_message_content_by_role**: Organize messages by role
2. **normalize_finish_reason**: Map provider values to standard ([X] mappings)
3. **calculate_cost**: Calculate cost for [X] models

**Data Sources**:
- Message structure: Phase 2 verification
- Finish reason values: Phase 3.3
- Pricing data: Phase 3.2 (verified 2025-09-30)

**File Status**: ✅ COMPLETE and compiles successfully
```

📊 QUANTIFY-RESULTS: Transforms documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Transform Validation Complete
- [ ] Minimum 3 transforms present ✅/❌
- [ ] All transforms have required fields ✅/❌
- [ ] All data from verified sources (Phase 2, 3) ✅/❌
- [ ] Field mappings reference transforms ✅/❌
- [ ] YAML compiles without errors ✅/❌
- [ ] Transforms documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If using unverified data or transforms incomplete

---

## 🛤️ **PHASE 7 COMPLETION GATE**

🛑 UPDATE-TABLE: Phase 7 → COMPLETE with transforms validated

### **Phase 7 Summary**
📊 QUANTIFY-RESULTS: Total transforms: [NUMBER]
📊 QUANTIFY-RESULTS: Message extraction: ✅
📊 QUANTIFY-RESULTS: Finish reason normalization: ✅ ([X] mappings)
📊 QUANTIFY-RESULTS: Cost calculation: ✅ ([X] models)
📊 QUANTIFY-RESULTS: YAML compilation: ✅ SUCCESS

**Transform Quality**:
- All from verified research (Phase 2, 3): ✅
- Current pricing (2025-09-30+): ✅
- Complete field definitions: ✅
- YAML compiles: ✅

### **Handoff to Phase 8 Validated**
✅ **Complete Transforms**: Message, finish reason, cost
✅ **Verified Data**: All from Phase 2, 3 research
✅ **Field Integration**: Referenced in field_mappings.yaml
✅ **YAML Valid**: File compiles without errors

### **Phase 8 Inputs Ready**
✅ All 4 DSL files complete (structure, navigation, mappings, transforms)
✅ Ready for compilation test
✅ Detection patterns for testing
✅ Extraction rules for validation

---

## 🎯 **CROSS-PHASE NAVIGATION**

🎯 NEXT-MANDATORY: Phase 8 Compilation & Validation (only after all validation gates pass)
🚨 FRAMEWORK-VIOLATION: If advancing to Phase 8 without complete transforms

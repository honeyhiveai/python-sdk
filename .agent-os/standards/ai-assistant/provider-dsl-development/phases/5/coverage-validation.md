# Task 5.5: Navigation Rules Coverage Validation

**🎯 Validate complete coverage for all verified instrumentors**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] All verified instrumentor rules created ✅/❌
- [ ] navigation_rules.yaml exists ✅/❌
- [ ] YAML compiles without errors ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Count Total Rules Created**

🛑 EXECUTE-NOW: Count rules in navigation_rules.yaml

```bash
grep -c "^[a-z_]*:" config/dsl/providers/{provider}/navigation_rules.yaml
```

🛑 PASTE-OUTPUT: Total rule count

📊 COUNT-AND-DOCUMENT: Total rules: [NUMBER]

### **Step 2: Validate Minimum Coverage**

🛑 EXECUTE-NOW: Verify minimum 7 rules per verified instrumentor

From Phase 2:
- Verified instrumentors: [X/3]
- Expected minimum rules: [X × 7] = [NUMBER]
- Actual rules created: [NUMBER from Step 1]
- Coverage adequate: YES/NO

📊 QUANTIFY-RESULTS: Minimum coverage met: YES/NO

### **Step 3: Validate Rule Consistency**

🛑 EXECUTE-NOW: Check all rules have required fields

For each rule in navigation_rules.yaml, verify:
- [ ] source_field present ✅/❌
- [ ] extraction_method present ✅/❌
- [ ] fallback_value present ✅/❌
- [ ] validation present ✅/❌
- [ ] description present ✅/❌

📊 QUANTIFY-RESULTS: All rules complete: YES/NO

### **Step 4: Verify Base Rule Names**

🛑 EXECUTE-NOW: Ensure rules use instrumentor prefixes

Check that all rules follow pattern:
- `{instrumentor}_{field_name}` (e.g., `traceloop_model_name`)
- NO base rule names yet (those come in Phase 6)

📊 QUANTIFY-RESULTS: All rules properly prefixed: YES/NO

### **Step 5: Cross-Check with Phase 2 Evidence**

🛑 EXECUTE-NOW: Confirm all source_field values from Phase 2

For each rule:
- Traceloop rules use `gen_ai.*` attributes from Phase 2: YES/NO
- OpenInference rules use `llm.*` attributes from Phase 2: YES/NO
- OpenLit rules use `openlit.*` attributes from Phase 2: YES/NO

📊 QUANTIFY-RESULTS: All attributes verified from Phase 2: YES/NO

### **Step 6: Document Coverage**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Navigation Rules**
- **File**: `config/dsl/providers/{provider}/navigation_rules.yaml`
- **Total rules**: [NUMBER]
- **Rules per instrumentor**:
  - Traceloop: [X] rules (if verified)
  - OpenInference: [X] rules (if verified)
  - OpenLit: [X] rules (if verified)

**Coverage Status**: ✅ COMPLETE

**Required Fields Covered** (per instrumentor):
- Model name: ✅
- Input messages: ✅
- Output messages: ✅
- Prompt tokens: ✅
- Completion tokens: ✅
- Temperature: ✅
- Max tokens: ✅

**Additional Fields**:
- Top-p: [✅/❌]
- Finish reason: [✅/❌]
- Provider-specific parameters: [COUNT]

**Validation**: All source_field values from Phase 2 verification
```

📊 QUANTIFY-RESULTS: Coverage documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Coverage Validation Complete
- [ ] Total rule count ≥ (verified instrumentors × 7) ✅/❌
- [ ] All rules have required YAML fields ✅/❌
- [ ] All rules properly prefixed ✅/❌
- [ ] All source_field values from Phase 2 ✅/❌
- [ ] Coverage documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If insufficient coverage or unverified attributes used

---

## 🛤️ **PHASE 5 COMPLETION GATE**

🛑 UPDATE-TABLE: Phase 5 → COMPLETE with navigation rules validated

### **Phase 5 Summary**
📊 QUANTIFY-RESULTS: Total rules created: [NUMBER]
📊 QUANTIFY-RESULTS: Instrumentors covered: [X/3]
📊 QUANTIFY-RESULTS: Minimum coverage: [✅ MET / ❌ INSUFFICIENT]
📊 QUANTIFY-RESULTS: YAML compilation: ✅ SUCCESS

**Rule Quality**:
- All from Phase 2 verified attributes: ✅
- Proper fallback values: ✅
- Validation rules present: ✅
- YAML compiles: ✅

### **Handoff to Phase 6 Validated**
✅ **Navigation Rules**: [X] rules ready for field mapping
✅ **Coverage Complete**: All verified instrumentors have rules
✅ **Attribute Verified**: All source_field values from Phase 2
✅ **YAML Valid**: File compiles without errors

### **Phase 6 Inputs Ready**
✅ Complete navigation rules for all instrumentors
✅ Rule names for field mapping references
✅ Extraction methods defined
✅ Validation rules for data quality

---

## 🎯 **CROSS-PHASE NAVIGATION**

🎯 NEXT-MANDATORY: Phase 6 Field Mappings Development (only after all validation gates pass)
🚨 FRAMEWORK-VIOLATION: If advancing to Phase 6 without complete navigation rules

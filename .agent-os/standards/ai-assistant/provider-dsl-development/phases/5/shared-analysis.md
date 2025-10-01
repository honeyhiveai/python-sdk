# Phase 5: Navigation Rules Development

**🎯 Create extraction rules for ALL verified instrumentors**

---

## 🚨 **ENTRY CHECKPOINT**

🛑 VALIDATE-GATE: Phase 5 Prerequisites
- [ ] Phase 4 complete with structure patterns ✅/❌
- [ ] Verified instrumentors list available ✅/❌
- [ ] Provider attributes documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without patterns

---

## 🛑 **MANDATORY EXECUTION SEQUENCE**

⚠️ **CRITICAL**: Complete ONE instrumentor at a time with blocking checkpoints

### **Task 5.1: Rule Planning**
⚠️ MUST-READ: [rule-planning.md](rule-planning.md)
📊 COUNT-AND-DOCUMENT: Required fields mapped for all instrumentors

---

### **Task 5.2: Traceloop Rules** (if Traceloop verified)
⚠️ MUST-READ: [traceloop-rules.md](traceloop-rules.md)
🛑 VALIDATE-GATE: Traceloop rules complete before proceeding
📊 COUNT-AND-DOCUMENT: Traceloop rules created

### ⚠️ **BLOCKING CHECKPOINT: TRACELOOP VALIDATION**

🛑 EXECUTE-NOW: Validate Traceloop rules before proceeding to OpenInference

```bash
# Test YAML compiles with Traceloop rules
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/navigation_rules.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: Traceloop section compiles: YES/NO

🚨 FRAMEWORK-VIOLATION: If proceeding to OpenInference without Traceloop validation

---

### **Task 5.3: OpenInference Rules** (if OpenInference verified)
⚠️ MUST-READ: [openinference-rules.md](openinference-rules.md)
🛑 VALIDATE-GATE: OpenInference rules complete before proceeding
📊 COUNT-AND-DOCUMENT: OpenInference rules created

### ⚠️ **BLOCKING CHECKPOINT: OPENINFERENCE VALIDATION**

🛑 EXECUTE-NOW: Validate OpenInference rules before proceeding to OpenLit

```bash
# Test YAML compiles with both Traceloop + OpenInference rules
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/navigation_rules.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: OpenInference section compiles: YES/NO

🚨 FRAMEWORK-VIOLATION: If proceeding to OpenLit without OpenInference validation

---

### **Task 5.4: OpenLit Rules** (if OpenLit verified)
⚠️ MUST-READ: [openlit-rules.md](openlit-rules.md)
🛑 VALIDATE-GATE: OpenLit rules complete
📊 COUNT-AND-DOCUMENT: OpenLit rules created

### ⚠️ **BLOCKING CHECKPOINT: OPENLIT VALIDATION**

🛑 EXECUTE-NOW: Validate all navigation rules (Traceloop + OpenInference + OpenLit)

```bash
# Test complete navigation_rules.yaml compiles
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/navigation_rules.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: Complete navigation_rules.yaml compiles: YES/NO

🚨 FRAMEWORK-VIOLATION: If proceeding to coverage validation without complete file validation

---

### **Task 5.FINAL: Coverage Validation**
⚠️ MUST-READ: [coverage-validation.md](coverage-validation.md)
📊 QUANTIFY-RESULTS: 7+ rules per instrumentor

🎯 NEXT-MANDATORY: [rule-planning.md](rule-planning.md)

---

## 📋 **PHASE 5 OVERVIEW**

**Purpose**: Create extraction paths for ALL verified instrumentors

**Tasks**: Planning + instrumentor-specific rules + validation

**Expected Duration**: 45-60 minutes

**⚠️ CRITICAL**: Minimum 7 rules per instrumentor required

**Required Rules** (per instrumentor):
- model_name, input_messages, output_messages
- prompt_tokens, completion_tokens
- temperature, max_tokens

---

**Create complete navigation rules for each instrumentor!**

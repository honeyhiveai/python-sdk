# Task 5.2: Traceloop Navigation Rules

**🎯 Create extraction rules for Traceloop instrumentation**

**⚠️ CONDITIONAL**: Only execute if Traceloop was verified in Phase 2

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 5.1 complete (Planning done) ✅/❌
- [ ] Traceloop verified as SUPPORTED in Phase 2 ✅/❌
- [ ] Traceloop attributes from Phase 2 available ✅/❌

🚨 **SKIP THIS FILE** if Traceloop NOT SUPPORTED - proceed to [openinference-rules.md](openinference-rules.md)

---

## 🛑 **EXECUTION**

### **Step 1: Create navigation_rules.yaml File**

🛑 EXECUTE-NOW: Open/create the YAML file (if not exists)

```bash
# File path
config/dsl/providers/{provider}/navigation_rules.yaml
```

📊 QUANTIFY-RESULTS: File opened/created: YES/NO

### **Step 2: Create Minimum Required Traceloop Rules**

🛑 EXECUTE-NOW: Add 7+ required rules using Phase 2 verified attributes

```yaml
# Traceloop Navigation Rules
# Based on Phase 2 verification evidence

traceloop_model_name:
  source_field: "gen_ai.request.model"  # From Phase 2 verification
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "non_empty_string"
  description: "Extract model name from Traceloop gen_ai attributes"

traceloop_input_messages:
  source_field: "gen_ai.prompt"  # Or message array field from Phase 2
  extraction_method: "direct_copy"  # Or array_flatten if array
  fallback_value: null
  validation: "non_empty"
  description: "Extract input prompt/messages from Traceloop"

traceloop_output_messages:
  source_field: "gen_ai.completion"  # Or response field from Phase 2
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "non_empty"
  description: "Extract output completion/messages from Traceloop"

traceloop_prompt_tokens:
  source_field: "gen_ai.usage.prompt_tokens"
  extraction_method: "direct_copy"
  fallback_value: 0
  validation: "positive_number"
  description: "Extract input token count from Traceloop"

traceloop_completion_tokens:
  source_field: "gen_ai.usage.completion_tokens"
  extraction_method: "direct_copy"
  fallback_value: 0
  validation: "positive_number"
  description: "Extract output token count from Traceloop"

traceloop_temperature:
  source_field: "gen_ai.request.temperature"
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "number"
  description: "Extract temperature parameter from Traceloop"

traceloop_max_tokens:
  source_field: "gen_ai.request.max_tokens"
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "positive_number"
  description: "Extract max tokens parameter from Traceloop"

# Additional rules based on Phase 2 verification
traceloop_top_p:
  source_field: "gen_ai.request.top_p"
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "number"
  description: "Extract top_p parameter from Traceloop"

traceloop_finish_reason:
  source_field: "gen_ai.response.finish_reasons"
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "non_empty_string"
  description: "Extract finish reason from Traceloop"
```

**⚠️ CRITICAL**: Use ONLY attributes verified in Phase 2! Adjust field paths based on actual verification evidence.

📊 COUNT-AND-DOCUMENT: Traceloop rules created: [NUMBER]

### **Step 3: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test YAML compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/navigation_rules.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 4: Validate Rule Coverage**

🛑 EXECUTE-NOW: Confirm minimum 7 rules present

Required rules present:
- [ ] traceloop_model_name ✅/❌
- [ ] traceloop_input_messages ✅/❌
- [ ] traceloop_output_messages ✅/❌
- [ ] traceloop_prompt_tokens ✅/❌
- [ ] traceloop_completion_tokens ✅/❌
- [ ] traceloop_temperature ✅/❌
- [ ] traceloop_max_tokens ✅/❌

📊 QUANTIFY-RESULTS: Minimum 7 rules: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Traceloop Rules Complete
- [ ] navigation_rules.yaml exists ✅/❌
- [ ] Minimum 7 Traceloop rules created ✅/❌
- [ ] All source_field values from Phase 2 verification ✅/❌
- [ ] YAML compiles without errors ✅/❌
- [ ] Safe fallback values for all rules ✅/❌

🚨 FRAMEWORK-VIOLATION: If using attributes not verified in Phase 2

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 5.2 → Traceloop rules created ([X] rules)
🎯 NEXT-MANDATORY: [openinference-rules.md](openinference-rules.md) (if OpenInference verified, else skip to next)

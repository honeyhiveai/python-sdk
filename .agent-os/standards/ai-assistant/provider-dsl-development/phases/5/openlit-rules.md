# Task 5.4: OpenLit Navigation Rules

**🎯 Create extraction rules for OpenLit instrumentation**

**⚠️ CONDITIONAL**: Only execute if OpenLit was verified in Phase 2

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Previous task complete (OpenInference rules or earlier) ✅/❌
- [ ] OpenLit verified as SUPPORTED in Phase 2 ✅/❌
- [ ] OpenLit attributes from Phase 2 available ✅/❌

🚨 **SKIP THIS FILE** if OpenLit NOT SUPPORTED - proceed to [coverage-validation.md](coverage-validation.md)

---

## 🛑 **EXECUTION**

### **Step 1: Add OpenLit Rules to navigation_rules.yaml**

🛑 EXECUTE-NOW: Append OpenLit rules using Phase 2 verified attributes

```yaml
# OpenLit Navigation Rules
# Based on Phase 2 verification evidence

openlit_model_name:
  source_field: "openlit.model"  # From Phase 2 verification
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "non_empty_string"
  description: "Extract model name from OpenLit attributes"

openlit_input_messages:
  source_field: "openlit.request.messages"  # Adjust based on Phase 2 code
  extraction_method: "array_flatten"  # Or direct_copy based on structure
  fallback_value: null
  validation: "non_empty"
  description: "Extract input messages from OpenLit"

openlit_output_messages:
  source_field: "openlit.response.messages"  # Adjust based on Phase 2 code
  extraction_method: "array_flatten"  # Or direct_copy based on structure
  fallback_value: null
  validation: "non_empty"
  description: "Extract output messages from OpenLit"

openlit_prompt_tokens:
  source_field: "openlit.usage.prompt_tokens"  # From Phase 2 verification
  extraction_method: "direct_copy"
  fallback_value: 0
  validation: "positive_number"
  description: "Extract prompt token count from OpenLit"

openlit_completion_tokens:
  source_field: "openlit.usage.completion_tokens"  # From Phase 2 verification
  extraction_method: "direct_copy"
  fallback_value: 0
  validation: "positive_number"
  description: "Extract completion token count from OpenLit"

openlit_temperature:
  source_field: "openlit.request.temperature"  # Adjust based on Phase 2 code
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "number"
  description: "Extract temperature parameter from OpenLit"

openlit_max_tokens:
  source_field: "openlit.request.max_tokens"  # Adjust based on Phase 2 code
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "positive_number"
  description: "Extract max tokens from OpenLit"

# Additional rules based on Phase 2 verification
openlit_top_p:
  source_field: "openlit.request.top_p"
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "number"
  description: "Extract top_p parameter from OpenLit"

openlit_finish_reason:
  source_field: "openlit.response.finish_reason"
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "non_empty_string"
  description: "Extract finish reason from OpenLit"
```

**⚠️ CRITICAL**: Adjust field paths based on Phase 2 code verification

📊 COUNT-AND-DOCUMENT: OpenLit rules created: [NUMBER]

### **Step 2: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test YAML compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/navigation_rules.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 3: Validate Rule Coverage**

🛑 EXECUTE-NOW: Confirm minimum 7 rules present

Required rules present:
- [ ] openlit_model_name ✅/❌
- [ ] openlit_input_messages ✅/❌
- [ ] openlit_output_messages ✅/❌
- [ ] openlit_prompt_tokens ✅/❌
- [ ] openlit_completion_tokens ✅/❌
- [ ] openlit_temperature ✅/❌
- [ ] openlit_max_tokens ✅/❌

📊 QUANTIFY-RESULTS: Minimum 7 rules: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: OpenLit Rules Complete
- [ ] navigation_rules.yaml updated ✅/❌
- [ ] Minimum 7 OpenLit rules created ✅/❌
- [ ] All source_field values from Phase 2 verification ✅/❌
- [ ] YAML compiles without errors ✅/❌
- [ ] Safe fallback values for all rules ✅/❌

🚨 FRAMEWORK-VIOLATION: If using attributes not verified in Phase 2

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 5.4 → OpenLit rules created ([X] rules)
🎯 NEXT-MANDATORY: [coverage-validation.md](coverage-validation.md)

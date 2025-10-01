# Task 5.3: OpenInference Navigation Rules

**🎯 Create extraction rules for OpenInference instrumentation**

**⚠️ CONDITIONAL**: Only execute if OpenInference was verified in Phase 2

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Previous task complete (Traceloop rules or planning) ✅/❌
- [ ] OpenInference verified as SUPPORTED in Phase 2 ✅/❌
- [ ] OpenInference attributes from Phase 2 available ✅/❌

🚨 **SKIP THIS FILE** if OpenInference NOT SUPPORTED - proceed to [openlit-rules.md](openlit-rules.md)

---

## 🛑 **EXECUTION**

### **Step 1: Add OpenInference Rules to navigation_rules.yaml**

🛑 EXECUTE-NOW: Append OpenInference rules using Phase 2 verified attributes

```yaml
# OpenInference Navigation Rules
# Based on Phase 2 verification evidence

openinference_model_name:
  source_field: "llm.model_name"  # From Phase 2 verification
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "non_empty_string"
  description: "Extract model name from OpenInference llm attributes"

openinference_input_messages:
  source_field: "llm.input_messages"  # From Phase 2 spec
  extraction_method: "array_flatten"  # Or direct_copy based on structure
  fallback_value: null
  validation: "non_empty"
  description: "Extract input messages from OpenInference"

openinference_output_messages:
  source_field: "llm.output_messages"  # From Phase 2 spec
  extraction_method: "array_flatten"  # Or direct_copy based on structure
  fallback_value: null
  validation: "non_empty"
  description: "Extract output messages from OpenInference"

openinference_prompt_tokens:
  source_field: "llm.token_count.prompt"  # From Phase 2 spec
  extraction_method: "direct_copy"
  fallback_value: 0
  validation: "positive_number"
  description: "Extract prompt token count from OpenInference"

openinference_completion_tokens:
  source_field: "llm.token_count.completion"  # From Phase 2 spec
  extraction_method: "direct_copy"
  fallback_value: 0
  validation: "positive_number"
  description: "Extract completion token count from OpenInference"

openinference_temperature:
  source_field: "llm.temperature"  # Or llm.request.temperature from Phase 2
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "number"
  description: "Extract temperature parameter from OpenInference"

openinference_max_tokens:
  source_field: "llm.max_tokens"  # Or llm.request.max_tokens from Phase 2
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "positive_number"
  description: "Extract max tokens from OpenInference"

# Additional rules based on Phase 2 spec
openinference_top_p:
  source_field: "llm.top_p"
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "number"
  description: "Extract top_p parameter from OpenInference"

openinference_finish_reason:
  source_field: "llm.finish_reason"
  extraction_method: "direct_copy"
  fallback_value: null
  validation: "non_empty_string"
  description: "Extract finish reason from OpenInference"
```

**⚠️ CRITICAL**: Adjust field paths based on Phase 2 spec verification

📊 COUNT-AND-DOCUMENT: OpenInference rules created: [NUMBER]

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
- [ ] openinference_model_name ✅/❌
- [ ] openinference_input_messages ✅/❌
- [ ] openinference_output_messages ✅/❌
- [ ] openinference_prompt_tokens ✅/❌
- [ ] openinference_completion_tokens ✅/❌
- [ ] openinference_temperature ✅/❌
- [ ] openinference_max_tokens ✅/❌

📊 QUANTIFY-RESULTS: Minimum 7 rules: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: OpenInference Rules Complete
- [ ] navigation_rules.yaml updated ✅/❌
- [ ] Minimum 7 OpenInference rules created ✅/❌
- [ ] All source_field values from Phase 2 spec ✅/❌
- [ ] YAML compiles without errors ✅/❌
- [ ] Safe fallback values for all rules ✅/❌

🚨 FRAMEWORK-VIOLATION: If using attributes not verified in Phase 2

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 5.3 → OpenInference rules created ([X] rules)
🎯 NEXT-MANDATORY: [openlit-rules.md](openlit-rules.md) (if OpenLit verified, else skip to coverage-validation.md)

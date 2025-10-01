# Task 7.2: Finish Reason Normalization Transform

**🎯 Define finish reason normalization using Phase 3 values**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 7.1 complete (Message extraction defined) ✅/❌
- [ ] transforms.yaml exists ✅/❌
- [ ] Finish reason values from Phase 3.3 available ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Review Provider Finish Reason Values**

🛑 EXECUTE-NOW: Load finish reason mapping from Phase 3.3

From RESEARCH_SOURCES.md Phase 3.3:
- Provider finish reason values: [LIST]
- Standard mappings needed: [PROVIDER_VALUE → STANDARD_VALUE]

📊 COUNT-AND-DOCUMENT: Finish reason values to map: [NUMBER]

### **Step 2: Define Normalization Transform**

🛑 EXECUTE-NOW: Add normalize_finish_reason to transforms.yaml

```yaml
normalize_finish_reason:
  type: "value_normalization"
  description: "Normalize provider-specific finish reasons to standard values"
  parameters:
    source_field: "finish_reason"
  mappings:
    # Map provider values → standard values
    # Standard values: complete, max_tokens, function_call, content_filter, error
    
    # Based on Phase 3.3 research:
    "{provider_value_1}": "complete"  # e.g., "stop" → "complete"
    "{provider_value_2}": "max_tokens"  # e.g., "length" → "max_tokens"
    "{provider_value_3}": "function_call"  # e.g., "tool_calls" → "function_call"
    "{provider_value_4}": "content_filter"  # If provider has moderation
    # Add all provider-specific values from Phase 3.3
    
  default: "complete"  # Safe default if value not in mappings
  implementation: "python"
```

**⚠️ CRITICAL**: Use ACTUAL provider values from Phase 3.3, not examples

📊 COUNT-AND-DOCUMENT: Finish reason mappings: [NUMBER]

### **Step 3: Verify All Provider Values Mapped**

🛑 EXECUTE-NOW: Cross-check with Phase 3.3

From Phase 3.3 finish reason values:
- Provider value 1: [VALUE] → Mapped: YES/NO
- Provider value 2: [VALUE] → Mapped: YES/NO
- Provider value 3: [VALUE] → Mapped: YES/NO
- ...

📊 QUANTIFY-RESULTS: All provider values mapped: YES/NO

### **Step 4: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test YAML compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/transforms.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 5: Document Finish Reason Transform**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Transforms - Finish Reason Normalization**

**Transform**: `normalize_finish_reason`

**Provider → Standard Mappings**:
| Provider Value | Standard Value | Description |
|----------------|----------------|-------------|
| {provider_val} | complete | Normal completion |
| {provider_val} | max_tokens | Token limit reached |
| {provider_val} | function_call | Tool/function called |
| ... | ... | ... |

**Total Mappings**: [NUMBER]
**Default**: complete (for unknown values)

**Source**: Phase 3.3 finish reason analysis
```

📊 QUANTIFY-RESULTS: Normalization documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Finish Reason Normalization Complete
- [ ] normalize_finish_reason added to transforms.yaml ✅/❌
- [ ] All Phase 3.3 finish values mapped ✅/❌
- [ ] Safe default defined ✅/❌
- [ ] YAML compiles ✅/❌
- [ ] Mappings documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If using example values instead of Phase 3.3 research

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 7.2 → Finish reason normalization defined ([X] mappings)
🎯 NEXT-MANDATORY: [cost-calculation.md](cost-calculation.md)

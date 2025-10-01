# Task 6.2: Outputs Section Mapping

**🎯 Map navigation rules to 'outputs' section of HoneyHive schema**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 6.1 complete (Inputs mapped) ✅/❌
- [ ] field_mappings.yaml exists with inputs section ✅/❌
- [ ] YAML compiles ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Add Outputs Section to field_mappings.yaml**

🛑 EXECUTE-NOW: Append outputs section with base rule names

```yaml
outputs:
  # Output messages/completions
  messages:
    source_rule: "output_messages"  # Base name, compiler routes to {instrumentor}_output_messages
    description: "Generated output messages or completion"
    required: true
    
  # Model used (may differ from requested)
  model:
    source_rule: "model_name"  # Base name
    description: "Actual model used for generation"
    required: true
    
  # Finish reason
  finish_reason:
    source_rule: "finish_reason"  # Base name
    description: "Reason generation stopped"
    required: false
    transform: "normalize_finish_reason"  # Transform function from Phase 7
    
  # Tool calls / Function calls (if applicable)
  tool_calls:
    source_rule: "tool_calls"  # Base name, if rule exists from Phase 5
    description: "Function or tool calls made by the model"
    required: false
```

**⚠️ CRITICAL**: Use BASE rule names, not instrumentor-prefixed

📊 COUNT-AND-DOCUMENT: Output fields mapped: [NUMBER]

### **Step 2: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test YAML compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/field_mappings.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 3: Validate Output Coverage**

🛑 EXECUTE-NOW: Ensure all critical output fields mapped

Required output fields present:
- [ ] messages (generated content) ✅/❌
- [ ] model (actual model used) ✅/❌
- [ ] finish_reason ✅/❌

📊 QUANTIFY-RESULTS: Minimum output coverage: YES/NO

### **Step 4: Check for Transform Requirements**

🛑 EXECUTE-NOW: Note which fields need transforms

Fields requiring transforms (for Phase 7):
- finish_reason: `normalize_finish_reason` (to standardize values)
- messages: May need `extract_message_content_by_role` (for structured extraction)

📊 COUNT-AND-DOCUMENT: Fields needing transforms: [NUMBER]

### **Step 5: Document Outputs Mapping**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Field Mappings - Outputs Section**

**Total output fields**: [NUMBER]

**Standard Output Fields**:
- messages (required) - Generated content
- model (required) - Actual model used
- finish_reason - Completion reason (needs transform)
- tool_calls - Function calls (if supported)

**Transform Requirements**:
- finish_reason: normalize_finish_reason (Phase 7)
- messages: May need role-based extraction (Phase 7)

**Mapping Strategy**: Base rule names with dynamic instrumentor routing
```

📊 QUANTIFY-RESULTS: Outputs mapping documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Outputs Mapping Complete
- [ ] outputs section added to field_mappings.yaml ✅/❌
- [ ] All source_rule use BASE names ✅/❌
- [ ] Minimum 3 output fields mapped ✅/❌
- [ ] Transform requirements noted ✅/❌
- [ ] YAML compiles ✅/❌

🚨 FRAMEWORK-VIOLATION: If using instrumentor-prefixed rule names

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 6.2 → Outputs section mapped ([X] fields)
🎯 NEXT-MANDATORY: [config-mapping.md](config-mapping.md)

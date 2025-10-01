# Task 6.1: Inputs Section Mapping

**🎯 Map navigation rules to 'inputs' section of HoneyHive schema**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Phase 5 complete with navigation rules validated ✅/❌
- [ ] navigation_rules.yaml exists with [X] rules ✅/❌
- [ ] All verified instrumentors have rules ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Create field_mappings.yaml File**

🛑 EXECUTE-NOW: Create/open the YAML file

```bash
# File path
config/dsl/providers/{provider}/field_mappings.yaml
```

📊 QUANTIFY-RESULTS: File created/opened: YES/NO

### **Step 2: Define Inputs Section Structure**

🛑 EXECUTE-NOW: Add inputs section with base rule names

```yaml
# Field Mappings - HoneyHive 4-Section Schema
# Uses base rule names (no instrumentor prefix)
# Dynamic routing handled by compiler

inputs:
  # Input messages/prompts
  messages:
    source_rule: "input_messages"  # Base name, compiler routes to {instrumentor}_input_messages
    description: "Input messages or prompt sent to the model"
    required: true
    
  # Model configuration parameters
  temperature:
    source_rule: "temperature"
    description: "Sampling temperature parameter"
    required: false
    
  max_tokens:
    source_rule: "max_tokens"
    description: "Maximum tokens to generate"
    required: false
    
  top_p:
    source_rule: "top_p"
    description: "Nucleus sampling parameter"
    required: false
    
  # Provider-specific parameters from Phase 3
  # Add any unique parameters identified in Phase 3.3
```

**⚠️ CRITICAL**: Use BASE rule names (e.g., `input_messages`) NOT instrumentor-prefixed (e.g., `traceloop_input_messages`)

📊 COUNT-AND-DOCUMENT: Input fields mapped: [NUMBER]

### **Step 3: Add Provider-Specific Input Parameters**

🛑 EXECUTE-NOW: Reference Phase 3.3 for unique parameters

From RESEARCH_SOURCES.md Phase 3.3:
- Unique parameters: [LIST]

Add each unique parameter to inputs section:
```yaml
  {unique_param_name}:
    source_rule: "{param_name}"  # Base rule name
    description: "{Description from Phase 3}"
    required: false
```

📊 COUNT-AND-DOCUMENT: Provider-specific inputs: [NUMBER]

### **Step 4: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test YAML compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/field_mappings.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 5: Validate Input Coverage**

🛑 EXECUTE-NOW: Ensure all critical input fields mapped

Required input fields present:
- [ ] messages (input data) ✅/❌
- [ ] temperature ✅/❌
- [ ] max_tokens ✅/❌
- [ ] top_p ✅/❌

📊 QUANTIFY-RESULTS: Minimum input coverage: YES/NO

### **Step 6: Document Inputs Mapping**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Field Mappings - Inputs Section**

**Total input fields**: [NUMBER]

**Standard LLM Parameters**:
- messages (required)
- temperature
- max_tokens
- top_p

**Provider-Specific Parameters**:
[List from Phase 3.3]

**Mapping Strategy**: Base rule names with dynamic instrumentor routing via compiler
```

📊 QUANTIFY-RESULTS: Inputs mapping documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Inputs Mapping Complete
- [ ] field_mappings.yaml created ✅/❌
- [ ] inputs section defined ✅/❌
- [ ] All source_rule use BASE names (no prefixes) ✅/❌
- [ ] Minimum 4 input fields mapped ✅/❌
- [ ] Provider-specific params from Phase 3 included ✅/❌
- [ ] YAML compiles ✅/❌

🚨 FRAMEWORK-VIOLATION: If using instrumentor-prefixed rule names

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 6.1 → Inputs section mapped ([X] fields)
🎯 NEXT-MANDATORY: [outputs-mapping.md](outputs-mapping.md)

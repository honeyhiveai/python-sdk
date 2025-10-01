# Task 6.3: Config Section Mapping

**🎯 Map navigation rules to 'config' section of HoneyHive schema**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 6.2 complete (Outputs mapped) ✅/❌
- [ ] field_mappings.yaml exists with inputs and outputs ✅/❌
- [ ] YAML compiles ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Add Config Section to field_mappings.yaml**

🛑 EXECUTE-NOW: Append config section with token usage data

```yaml
config:
  # Token usage information
  prompt_tokens:
    source_rule: "prompt_tokens"  # Base name
    description: "Number of input tokens used"
    required: true
    
  completion_tokens:
    source_rule: "completion_tokens"  # Base name
    description: "Number of output tokens generated"
    required: true
    
  total_tokens:
    source_rule: "total_tokens"  # May not exist in rules, can compute
    description: "Total tokens used (prompt + completion)"
    required: false
    computed: true  # Computed from prompt + completion if not available
    
  # Cost calculation (requires transform from Phase 7)
  cost:
    source_rule: "cost"  # Will be computed via transform
    description: "Estimated cost of the API call"
    required: false
    transform: "calculate_cost"  # Transform function from Phase 7
```

**⚠️ CRITICAL**: Use BASE rule names

📊 COUNT-AND-DOCUMENT: Config fields mapped: [NUMBER]

### **Step 2: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test YAML compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/field_mappings.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 3: Validate Config Coverage**

🛑 EXECUTE-NOW: Ensure all critical config fields mapped

Required config fields present:
- [ ] prompt_tokens ✅/❌
- [ ] completion_tokens ✅/❌
- [ ] total_tokens (or computable) ✅/❌
- [ ] cost (with transform) ✅/❌

📊 QUANTIFY-RESULTS: Minimum config coverage: YES/NO

### **Step 4: Note Transform Requirements**

🛑 EXECUTE-NOW: Identify transforms needed

Transforms for Phase 7:
- `calculate_cost`: Use pricing from Phase 3.2 to compute cost based on tokens
- May need token computation if total_tokens not available

📊 COUNT-AND-DOCUMENT: Config transforms needed: [NUMBER]

### **Step 5: Document Config Mapping**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Field Mappings - Config Section**

**Total config fields**: [NUMBER]

**Token Usage Fields**:
- prompt_tokens (required)
- completion_tokens (required)
- total_tokens (computed if needed)

**Cost Calculation**:
- cost: Requires calculate_cost transform (Phase 7)
- Pricing data source: Phase 3.2

**Transform Requirements**:
- calculate_cost: Use pricing table from Phase 3 (Phase 7)
```

📊 QUANTIFY-RESULTS: Config mapping documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Config Mapping Complete
- [ ] config section added to field_mappings.yaml ✅/❌
- [ ] All source_rule use BASE names ✅/❌
- [ ] Minimum 4 config fields mapped ✅/❌
- [ ] Cost transform planned ✅/❌
- [ ] YAML compiles ✅/❌

🚨 FRAMEWORK-VIOLATION: If using instrumentor-prefixed rule names

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 6.3 → Config section mapped ([X] fields)
🎯 NEXT-MANDATORY: [metadata-mapping.md](metadata-mapping.md)

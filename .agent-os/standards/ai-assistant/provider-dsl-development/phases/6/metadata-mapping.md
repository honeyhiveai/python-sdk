# Task 6.4: Metadata Section Mapping

**🎯 Map provider and instrumentor metadata to HoneyHive schema**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 6.3 complete (Config mapped) ✅/❌
- [ ] field_mappings.yaml exists with inputs, outputs, config ✅/❌
- [ ] YAML compiles ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Add Metadata Section to field_mappings.yaml**

🛑 EXECUTE-NOW: Append metadata section

```yaml
metadata:
  # Provider identification (set by detection, not extracted)
  provider:
    source_rule: null  # Set by provider_processor detection
    description: "LLM provider name (e.g., openai, anthropic, gemini)"
    required: true
    injected: true  # Not extracted from attributes, injected by processor
    
  # Instrumentor identification (set by detection)
  instrumentor:
    source_rule: null  # Set by provider_processor detection
    description: "Instrumentor framework (traceloop, openinference, openlit)"
    required: true
    injected: true
    
  # Provider-specific metadata
  provider_metadata:
    description: "Additional provider-specific metadata"
    required: false
    fields:
      # Add provider-specific metadata from Phase 3 if applicable
      # Example: regional endpoint, model version, etc.
```

**⚠️ NOTE**: Metadata fields are typically injected by the processor, not extracted from attributes

📊 COUNT-AND-DOCUMENT: Metadata fields defined: [NUMBER]

### **Step 2: Add Provider-Specific Metadata**

🛑 EXECUTE-NOW: Review Phase 3.3 for additional metadata

From RESEARCH_SOURCES.md Phase 3.3:
- Provider features that should be in metadata: [LIST if any]
- Regional/compliance information: [LIST if applicable]

Add to provider_metadata section if applicable

📊 COUNT-AND-DOCUMENT: Provider-specific metadata: [NUMBER]

### **Step 3: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test complete file compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/field_mappings.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 4: Validate Complete Field Mappings**

🛑 EXECUTE-NOW: Verify all 4 sections present

Required sections present:
- [ ] inputs (with messages, temperature, max_tokens, top_p) ✅/❌
- [ ] outputs (with messages, model, finish_reason) ✅/❌
- [ ] config (with prompt_tokens, completion_tokens, cost) ✅/❌
- [ ] metadata (with provider, instrumentor) ✅/❌

📊 QUANTIFY-RESULTS: All 4 sections complete: YES/NO

### **Step 5: Document Complete Field Mappings**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Field Mappings - Complete Schema**

**Total sections**: 4
**Total fields**: [SUM of all fields]

**Section Summary**:
- **inputs**: [X] fields (messages, parameters)
- **outputs**: [X] fields (messages, model, finish_reason)
- **config**: [X] fields (tokens, cost)
- **metadata**: [X] fields (provider, instrumentor)

**Mapping Strategy**:
- Base rule names (no instrumentor prefixes)
- Dynamic routing via compiler based on detected instrumentor
- Transforms for finish_reason normalization and cost calculation

**File Status**: ✅ COMPLETE and compiles successfully
```

📊 QUANTIFY-RESULTS: Complete mappings documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Metadata Mapping Complete
- [ ] metadata section added ✅/❌
- [ ] provider and instrumentor fields defined ✅/❌
- [ ] All 4 sections present (inputs, outputs, config, metadata) ✅/❌
- [ ] YAML compiles without errors ✅/❌
- [ ] Complete mappings documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If any section incomplete

---

## 🛤️ **PHASE 6 COMPLETION GATE**

🛑 UPDATE-TABLE: Phase 6 → COMPLETE with field mappings validated

### **Phase 6 Summary**
📊 QUANTIFY-RESULTS: Total sections: 4/4
📊 QUANTIFY-RESULTS: Total fields mapped: [NUMBER]
📊 QUANTIFY-RESULTS: YAML compilation: ✅ SUCCESS

**Section Breakdown**:
- Inputs: [X] fields (standard + provider-specific)
- Outputs: [X] fields (including transform requirements)
- Config: [X] fields (tokens + cost)
- Metadata: [X] fields (injected by processor)

### **Handoff to Phase 7 Validated**
✅ **Complete 4-Section Schema**: All sections defined
✅ **Base Rule Names**: Ready for dynamic routing
✅ **Transform Requirements**: Identified for Phase 7
✅ **YAML Valid**: File compiles without errors

### **Phase 7 Inputs Ready**
✅ Field mappings complete for transform planning
✅ Transform requirements identified (finish_reason, cost)
✅ Pricing data from Phase 3 for cost calculation
✅ Finish reason values from Phase 3 for normalization

---

## 🎯 **CROSS-PHASE NAVIGATION**

🎯 NEXT-MANDATORY: Phase 7 Transforms Development (only after all validation gates pass)
🚨 FRAMEWORK-VIOLATION: If advancing to Phase 7 without complete field mappings

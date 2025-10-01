# Task 3.3: Provider-Specific Features

**🎯 Identify unique parameters and capabilities of this provider**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 3.2 complete (Pricing collected) ✅/❌
- [ ] Model list and pricing both documented ✅/❌
- [ ] API documentation from Phase 1 available ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Review API Documentation for Unique Parameters**

🛑 EXECUTE-NOW: Check API docs for provider-specific parameters

Compare to OpenAI baseline to identify unique parameters:
- OpenAI standard: `temperature`, `max_tokens`, `top_p`, `frequency_penalty`, `presence_penalty`
- Provider-specific: Any additional or different parameters

📊 COUNT-AND-DOCUMENT: Unique parameters found: [NUMBER]

### **Step 2: Document Unique Parameters**

🛑 EXECUTE-NOW: Create parameter reference

**Format**:
```markdown
### Provider-Specific Features

**Unique Parameters**:
- `{parameter-name}`: {Description}
  - Type: {string/number/boolean/array}
  - Default: {value}
  - Available in models: {which models support this}
  - Example values: {examples}
  - Appears in traces as: {attribute name if known}

**Standard Parameters with Variations**:
- `{parameter}`: {How this provider's implementation differs from OpenAI}
```

📊 QUANTIFY-RESULTS: Parameters documented: [NUMBER]

### **Step 3: Identify Unique Capabilities**

🛑 EXECUTE-NOW: Note any unique features

Check for:
- **Function calling**: How it works, any unique aspects
- **JSON mode**: Structured outputs implementation
- **Streaming**: Any special streaming features
- **Multimodal**: Vision, audio, or other modalities
- **Safety/Moderation**: Built-in safety features
- **Regional/Compliance**: EU data residency, GDPR compliance
- **Tool use**: Unique tool/agent capabilities

📊 COUNT-AND-DOCUMENT: Unique capabilities: [NUMBER]

### **Step 4: Note Finish Reason Values**

🛑 EXECUTE-NOW: Identify provider-specific finish reasons

Compare to OpenAI (`stop`, `length`, `tool_calls`, `content_filter`):
- Provider uses same values: YES/NO
- Provider-specific values: [LIST]

**Example**:
```markdown
**Finish Reason Mapping** (for Phase 7):
- `{provider-value-1}` → should map to `complete`
- `{provider-value-2}` → should map to `max_tokens`
- `{provider-value-3}` → should map to `function_call`
```

📊 COUNT-AND-DOCUMENT: Finish reason values: [NUMBER]

### **Step 5: Document in RESEARCH_SOURCES**

🛑 EXECUTE-NOW: Add features to RESEARCH_SOURCES.md

```markdown
### **3.3 Provider-Specific Features**

[PASTE UNIQUE PARAMETERS FROM STEP 2]

[PASTE UNIQUE CAPABILITIES FROM STEP 3]

**Finish Reason Values**:
[PASTE FINISH REASON MAPPING FROM STEP 4]

**Comparison to OpenAI**:
- Standard compatible parameters: [LIST]
- Unique parameters: [COUNT]
- Unique capabilities: [COUNT]
- API compatibility level: [High/Medium/Low]

**Source**: [API docs URL]
**Verified**: 2025-09-30
```

📊 QUANTIFY-RESULTS: Features documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Provider Features Complete
- [ ] Unique parameters identified ✅/❌
- [ ] Unique capabilities documented ✅/❌
- [ ] Finish reason values noted (critical for Phase 7) ✅/❌
- [ ] Comparison to OpenAI baseline done ✅/❌
- [ ] Added to RESEARCH_SOURCES.md ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without feature analysis

---

## 🛤️ **PHASE 3 COMPLETION GATE**

🛑 UPDATE-TABLE: Phase 3 → COMPLETE with model/pricing data

### **Phase 3 Summary**
📊 QUANTIFY-RESULTS: Total models documented: [NUMBER]
📊 QUANTIFY-RESULTS: Models with pricing: [X/TOTAL]
📊 QUANTIFY-RESULTS: Unique parameters: [NUMBER]
📊 QUANTIFY-RESULTS: Unique capabilities: [NUMBER]

**Data Currency**: All data verified as of 2025-09-30

### **Handoff to Phase 4 Validated**
✅ **Complete Model List**: [X] models across all tiers
✅ **Current Pricing**: Verified for all models with currency and units
✅ **Provider Features**: Unique parameters and capabilities documented
✅ **Finish Reason Mapping**: Values identified for transform development

### **Phase 4 Inputs Ready**
✅ Model identifiers for signature patterns
✅ Provider-specific attributes for detection
✅ Feature set for navigation rules
✅ Comprehensive documentation for DSL development

---

## 🎯 **CROSS-PHASE NAVIGATION**

🎯 NEXT-MANDATORY: Phase 4 Structure Patterns Development (only after all validation gates pass)
🚨 FRAMEWORK-VIOLATION: If advancing to Phase 4 without complete model/pricing data

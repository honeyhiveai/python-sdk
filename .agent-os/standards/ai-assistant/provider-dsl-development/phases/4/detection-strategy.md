# Task 4.1: Detection Strategy Design

**🎯 Design O(1) detection strategy using verified instrumentor data**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Phase 3 complete with model/pricing data ✅/❌
- [ ] Phase 2 instrumentor verification complete ✅/❌
- [ ] List of verified instrumentors available ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Review Verified Instrumentors**

🛑 EXECUTE-NOW: List verified instrumentors from Phase 2

From RESEARCH_SOURCES.md Instrumentor Support Matrix:
- Traceloop: ✅ VERIFIED / ❌ NOT SUPPORTED
- OpenInference: ✅ VERIFIED / ❌ NOT SUPPORTED
- OpenLit: ✅ VERIFIED / ❌ NOT SUPPORTED

📊 COUNT-AND-DOCUMENT: Verified instrumentors: [X/3]

### **Step 2: Identify Unique Signature Fields**

🛑 EXECUTE-NOW: For EACH verified instrumentor, identify provider-specific fields

**For Traceloop** (if verified):
- Required fields: `gen_ai.system`, `gen_ai.request.model`
- Provider-specific value: `gen_ai.system = "{provider-specific-value}"`
- Optional unique fields: [any provider-specific gen_ai.* attributes]

**For OpenInference** (if verified):
- Required fields: `llm.provider`, `llm.model_name`
- Provider-specific value: `llm.provider = "{provider-specific-value}"`
- Optional unique fields: [any provider-specific llm.* attributes]

**For OpenLit** (if verified):
- Required fields: `openlit.provider`, `openlit.model`
- Provider-specific value: `openlit.provider = "{provider-specific-value}"`
- Optional unique fields: [any provider-specific openlit.* attributes]

📊 COUNT-AND-DOCUMENT: Unique signature fields per instrumentor: [NUMBER]

### **Step 3: Analyze Uniqueness**

🛑 EXECUTE-NOW: Compare to existing providers (OpenAI, Anthropic, Gemini)

For each verified instrumentor, ask:
- Are required fields ONLY for this provider? (HIGH uniqueness)
- Are required fields shared but values different? (MEDIUM uniqueness)
- Are we relying on generic fields? (LOW uniqueness)

**Uniqueness Assessment**:
- Traceloop: HIGH / MEDIUM / LOW
- OpenInference: HIGH / MEDIUM / LOW
- OpenLit: HIGH / MEDIUM / LOW

📊 QUANTIFY-RESULTS: Overall uniqueness: HIGH/MEDIUM/LOW

### **Step 4: Plan Confidence Weights**

🛑 EXECUTE-NOW: Assign confidence weights based on uniqueness

**Confidence Weight Guidelines**:
- **0.95-0.98**: Provider name in attribute values (e.g., `gen_ai.system = "mistral"`)
- **0.90-0.94**: Unique field combination with clear provider indicators
- **0.85-0.89**: Less unique, relies on multiple fields
- **0.80-0.84**: Generic pattern, may overlap

**Planned Weights**:
- `{instrumentor}_{provider}` pattern: 0.XX (based on uniqueness)

📊 QUANTIFY-RESULTS: Confidence weights planned: YES/NO

### **Step 5: Document Strategy**

🛑 EXECUTE-NOW: Add strategy to RESEARCH_SOURCES.md

```markdown
## 4. **Detection Strategy**

### **Verified Instrumentors for Patterns**
[X/3] instrumentors will have detection patterns:
- Traceloop: [✅/❌] - Confidence: 0.XX
- OpenInference: [✅/❌] - Confidence: 0.XX
- OpenLit: [✅/❌] - Confidence: 0.XX

### **Signature Fields by Instrumentor**

**Traceloop Pattern**:
- Required: [`gen_ai.system`, `gen_ai.request.model`]
- Optional: [provider-specific fields]
- Unique value: `gen_ai.system = "{value}"`

**OpenInference Pattern**:
- Required: [`llm.provider`, `llm.model_name`]
- Optional: [provider-specific fields]
- Unique value: `llm.provider = "{value}"`

**OpenLit Pattern**:
- Required: [`openlit.provider`, `openlit.model`]
- Optional: [provider-specific fields]
- Unique value: `openlit.provider = "{value}"`

### **Uniqueness Analysis**
Overall detection uniqueness: [HIGH/MEDIUM/LOW]
Collision risk with existing providers: [LOW/MEDIUM/HIGH]

**Source**: Phase 2 instrumentor verification
**Planned Patterns**: [X] (one per verified instrumentor)
```

📊 QUANTIFY-RESULTS: Strategy documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Detection Strategy Complete
- [ ] Verified instrumentors reviewed ✅/❌
- [ ] Signature fields identified for each ✅/❌
- [ ] Uniqueness assessed ✅/❌
- [ ] Confidence weights planned ✅/❌
- [ ] Strategy documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without strategy

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 4.1 → Detection strategy designed for [X] instrumentors
🎯 NEXT-MANDATORY: [pattern-definitions.md](pattern-definitions.md)

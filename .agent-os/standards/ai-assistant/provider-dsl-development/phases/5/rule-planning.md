# Task 5.1: Navigation Rules Planning

**🎯 Plan extraction rules for ALL verified instrumentors**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Phase 4 complete with structure patterns validated ✅/❌
- [ ] List of verified instrumentors from Phase 2 ✅/❌
- [ ] Provider attributes from Phase 2 verification ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Review Verified Instrumentors**

🛑 EXECUTE-NOW: List instrumentors that need navigation rules

From Phase 2 RESEARCH_SOURCES.md:
- Traceloop: ✅ VERIFIED / ❌ NOT SUPPORTED
- OpenInference: ✅ VERIFIED / ❌ NOT SUPPORTED  
- OpenLit: ✅ VERIFIED / ❌ NOT SUPPORTED

📊 COUNT-AND-DOCUMENT: Instrumentors needing rules: [X/3]

### **Step 2: Define Required Rules Per Instrumentor**

🛑 EXECUTE-NOW: Plan minimum required rules (7 per instrumentor)

**Minimum Required Rules**:
1. `{instrumentor}_model_name` - Model identifier extraction
2. `{instrumentor}_input_messages` - Input data extraction
3. `{instrumentor}_output_messages` - Output data extraction
4. `{instrumentor}_prompt_tokens` - Input token count
5. `{instrumentor}_completion_tokens` - Output token count
6. `{instrumentor}_temperature` - Temperature parameter
7. `{instrumentor}_max_tokens` - Max tokens parameter

**Additional Rules** (as applicable from Phase 2 verification):
- `{instrumentor}_top_p` - Top-p sampling
- `{instrumentor}_finish_reason` - Completion reason
- `{instrumentor}_tool_calls` - Function calls (if supported)
- Provider-specific parameters from Phase 3

📊 COUNT-AND-DOCUMENT: Total rules to create: [X instrumentors × 7+ rules] = [TOTAL]

### **Step 3: Map to Provider Attributes**

🛑 EXECUTE-NOW: For EACH verified instrumentor, map required rules to actual attributes

**Use Phase 2 verification evidence** to map:

**Example - Traceloop** (if verified):
```markdown
### Traceloop Rules Mapping

1. model_name → `gen_ai.request.model` or `gen_ai.response.model`
2. input_messages → `gen_ai.prompt` or message array field
3. output_messages → `gen_ai.completion` or response array field
4. prompt_tokens → `gen_ai.usage.prompt_tokens`
5. completion_tokens → `gen_ai.usage.completion_tokens`
6. temperature → `gen_ai.request.temperature`
7. max_tokens → `gen_ai.request.max_tokens`
```

Repeat for OpenInference and OpenLit if verified

📊 QUANTIFY-RESULTS: Attribute mappings complete for all verified instrumentors: YES/NO

### **Step 4: Determine Extraction Methods**

🛑 EXECUTE-NOW: Choose extraction method for each rule

**Extraction Methods**:
- `direct_copy`: Simple field copy
- `array_flatten`: Extract from array (e.g., messages)
- `object_merge`: Merge nested objects
- `conditional_extract`: Extract based on condition

**Plan extraction methods** for each rule:
```markdown
### Extraction Methods

**Traceloop**:
- model_name: direct_copy
- input_messages: array_flatten (if array) or direct_copy
- prompt_tokens: direct_copy
- ...

**OpenInference**:
- model_name: direct_copy
- ...
```

📊 COUNT-AND-DOCUMENT: Extraction methods planned: [X] rules

### **Step 5: Define Fallback Values**

🛑 EXECUTE-NOW: Plan safe fallback values

For each rule type:
- model_name: `null` (required field, no safe fallback)
- tokens: `0` (safe numeric default)
- messages: `null` or `[]` (empty array)
- parameters: `null` (optional)

📊 QUANTIFY-RESULTS: Fallback values planned: YES/NO

### **Step 6: Document Planning**

🛑 EXECUTE-NOW: Add rule plan to RESEARCH_SOURCES.md

```markdown
### **Navigation Rules Planning**

**Total Rules to Create**: [NUMBER]

**Rules Per Instrumentor**:
- Traceloop: 7+ rules (if verified)
- OpenInference: 7+ rules (if verified)
- OpenLit: 7+ rules (if verified)

**Minimum Coverage** (per instrumentor):
✅ Model name extraction
✅ Input/output message extraction
✅ Token count extraction
✅ Parameter extraction (temperature, max_tokens)

**Next Steps**:
1. Create rules for each verified instrumentor
2. Use base rule naming (no instrumentor prefix in field_mappings)
3. Implement dynamic routing via compiler
```

📊 QUANTIFY-RESULTS: Rule planning documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Rule Planning Complete
- [ ] Verified instrumentors reviewed ✅/❌
- [ ] Minimum 7 rules per instrumentor planned ✅/❌
- [ ] Attributes mapped from Phase 2 evidence ✅/❌
- [ ] Extraction methods chosen ✅/❌
- [ ] Fallback values defined ✅/❌
- [ ] Planning documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without complete planning

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 5.1 → Navigation rules planned for [X] instrumentors
🎯 NEXT-MANDATORY: [traceloop-rules.md](traceloop-rules.md) (if Traceloop verified, else skip to next verified instrumentor)

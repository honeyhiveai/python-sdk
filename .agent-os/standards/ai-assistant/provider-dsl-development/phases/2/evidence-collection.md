# Task 2.4: Instrumentor Support Evidence Collection

**🎯 Aggregate and validate all instrumentor verification evidence**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 2.3 complete (OpenLit verified) ✅/❌
- [ ] All 3 instrumentors checked ✅/❌
- [ ] Evidence documented in RESEARCH_SOURCES.md ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Create Support Matrix**

🛑 EXECUTE-NOW: Summarize all instrumentor support findings

Create summary table in RESEARCH_SOURCES.md:

```markdown
## 📊 **Instrumentor Support Matrix**

| Instrumentor | Support Status | Evidence Type | Package/Directory |
|--------------|----------------|---------------|-------------------|
| Traceloop | ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC | Code review | `opentelemetry-instrumentation-{provider}` or N/A |
| OpenInference | ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC | Spec review | Provider-specific or Generic LLM |
| OpenLit | ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC | Code review | `{provider}/` or N/A |

**Total Verified**: [X/3]
**Sufficient for DSL**: [YES if ≥1 verified, NO if 0]
```

📊 COUNT-AND-DOCUMENT: Instrumentors verified: [X/3]

### **Step 2: Validate Minimum Support**

🛑 EXECUTE-NOW: Ensure at least 1 instrumentor supports provider

🛑 VALIDATE-GATE: Minimum Support Check
- [ ] At least 1 instrumentor supports provider ✅/❌

🚨 **CRITICAL**: If NO instrumentor support found:
- Document as "No current instrumentor support"
- Provider may require custom implementation
- Consider aborting DSL development or documenting for future support

📊 QUANTIFY-RESULTS: DSL development viable: YES/NO

### **Step 3: Identify Attribute Patterns**

🛑 EXECUTE-NOW: Compare attribute namespaces across verified instrumentors

For each VERIFIED instrumentor, note:
- Traceloop: `gen_ai.*`
- OpenInference: `llm.*`
- OpenLit: `openlit.*`

📊 COUNT-AND-DOCUMENT: Distinct attribute namespaces: [NUMBER]

### **Step 4: Note Critical Attributes**

🛑 EXECUTE-NOW: Identify common required attributes

Across all VERIFIED instrumentors, ensure you captured:
- Provider/system identifier (e.g., `gen_ai.system`, `llm.provider`)
- Model name field
- Input tokens field
- Output tokens field
- Message/prompt fields

📊 QUANTIFY-RESULTS: Critical attributes identified for all verified instrumentors: YES/NO

### **Step 5: Update Evidence Table**

🛑 EXECUTE-NOW: Mark all instrumentor verifications complete

Update evidence tracking table:
```markdown
| Instrumentor | Traceloop | ✅ COMPLETE | 2025-09-30 | [GitHub URL] |
| Instrumentor | OpenInference | ✅ COMPLETE | 2025-09-30 | [GitHub URL] |
| Instrumentor | OpenLit | ✅ COMPLETE | 2025-09-30 | [GitHub URL or N/A] |
```

📊 QUANTIFY-RESULTS: Evidence table updated: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Evidence Collection Complete
- [ ] All 3 instrumentors verified ✅/❌
- [ ] Support matrix created ✅/❌
- [ ] At least 1 instrumentor supports provider ✅/❌
- [ ] Critical attributes identified ✅/❌
- [ ] Evidence table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without verified instrumentor support

---

## 🛤️ **PHASE 2 COMPLETION GATE**

🛑 UPDATE-TABLE: Phase 2 → COMPLETE with instrumentor verification

### **Phase 2 Summary**
📊 QUANTIFY-RESULTS: Instrumentors checked: 3/3
📊 QUANTIFY-RESULTS: Instrumentors verified as supporting provider: [X/3]
📊 QUANTIFY-RESULTS: Verification method: Source code review for all

**Support Status**:
- Traceloop: ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC
- OpenInference: ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC
- OpenLit: ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC

### **Handoff to Phase 3 Validated**
✅ **Instrumentor Support**: [X/3] instrumentors verified from code
✅ **No Assumptions Made**: All findings from actual GitHub repositories
✅ **Attribute Patterns**: Documented for all verified instrumentors
✅ **Critical Attributes**: Identified for navigation rules

### **Phase 3 Inputs Ready**
✅ List of verified instrumentors for DSL development
✅ Attribute patterns for structure patterns
✅ Namespace information for navigation rules
✅ Sufficient support to proceed (≥1 instrumentor verified)

---

## 🎯 **CROSS-PHASE NAVIGATION**

🎯 NEXT-MANDATORY: Phase 3 Model & Pricing Data Collection (only after all validation gates pass)
🚨 FRAMEWORK-VIOLATION: If advancing to Phase 3 without instrumentor verification complete

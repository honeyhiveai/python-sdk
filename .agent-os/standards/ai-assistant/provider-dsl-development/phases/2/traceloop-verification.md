# Task 2.1: Traceloop/OpenLLMetry Support Verification

**🎯 Verify (NOT assume!) Traceloop support from actual code**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Phase 1 complete with official docs verified ✅/❌
- [ ] Provider name known ✅/❌

🚨 **CRITICAL**: NO ASSUMPTIONS - verify from actual GitHub repository code!

---

## 🛑 **EXECUTION**

### **Step 1: Check Traceloop Packages Directory**

🛑 EXECUTE-NOW: Navigate to Traceloop instrumentations

**Primary check**:
```
URL: https://github.com/traceloop/openllmetry/tree/main/packages
```

Look for: `opentelemetry-instrumentation-{provider}`

📊 QUANTIFY-RESULTS: Provider-specific package found: YES/NO

### **Step 2: If Dedicated Package Found**

🛑 EXECUTE-NOW: Verify package contents

If package exists, check:
```
URL: https://github.com/traceloop/openllmetry/tree/main/packages/opentelemetry-instrumentation-{provider}
```

Look in `__init__.py` or instrumentor source for:
- Attribute namespace (e.g., `gen_ai.*`)
- Key attributes (`gen_ai.system = "{provider}"`)
- Patch targets (which SDK it instruments)

🛑 PASTE-OUTPUT: Key attributes found (copy 3-5 examples)

📊 COUNT-AND-DOCUMENT: Attributes documented: [NUMBER]

### **Step 3: If No Dedicated Package**

🛑 EXECUTE-NOW: Check for generic support

If no dedicated package, check:
- Traceloop README for supported providers list
- Generic OpenAI-compatible support
- `gen_ai.*` namespace usage

📊 QUANTIFY-RESULTS: Generic support: YES/NO

### **Step 4: Document Verification Evidence**

🛑 EXECUTE-NOW: Record actual findings in RESEARCH_SOURCES.md

```markdown
## 2. **Instrumentor Support Verification**

### **2.1 Traceloop / OpenLLMetry**

**Support Status**: ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC

**Evidence**:
- **Package**: `opentelemetry-instrumentation-{provider}` (if dedicated)
- **Source URL**: [GitHub URL to actual code]
- **Attribute Namespace**: `gen_ai.*` / other
- **Key Attributes Verified**:
  - `gen_ai.system = "{value}"`
  - `gen_ai.request.model = "{field_path}"`
  - `gen_ai.usage.prompt_tokens = "{field_path}"`
  - [Add 2-3 more key attributes from actual code]
- **Verification Method**: Source code review
- **Last Verified**: 2025-09-30

**Notes**: [Dedicated instrumentor / Generic support / Not supported]
```

📊 QUANTIFY-RESULTS: Evidence documented with source URLs: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Traceloop Verification Complete
- [ ] GitHub repository checked ✅/❌
- [ ] Support status determined from code (not documentation) ✅/❌
- [ ] If supported, attributes extracted from actual code ✅/❌
- [ ] Source URL documented ✅/❌
- [ ] Evidence added to RESEARCH_SOURCES.md ✅/❌
- [ ] Evidence table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If assumptions made without code verification

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 2.1 → Traceloop verified from code
🎯 NEXT-MANDATORY: [openinference-verification.md](openinference-verification.md)

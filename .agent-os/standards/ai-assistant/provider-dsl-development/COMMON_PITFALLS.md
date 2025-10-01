# Common Pitfalls in Provider DSL Development

**Version**: 1.0  
**Date**: 2025-09-30  
**Purpose**: Document common errors and how to avoid them

---

## 🚨 **CRITICAL PITFALLS** (Will Cause Compilation Failure)

### **PITFALL 1: Using `required_fields` Instead of `signature_fields`**

**❌ INCORRECT**:
```yaml
traceloop_mistral:
  required_fields:  # ❌ WRONG - compiler expects "signature_fields"
    - "gen_ai.system"
    - "gen_ai.request.model"
```

**✅ CORRECT**:
```yaml
traceloop_mistral:
  signature_fields:  # ✅ CORRECT - matches compiler schema
    - "gen_ai.system"
    - "gen_ai.request.model"
```

**How to Detect**:
```bash
# Check for incorrect field names
grep -n "required_fields:" config/dsl/providers/{provider}/structure_patterns.yaml
```

**Expected**: No matches (if file is correct)

**Fix**: Replace all `required_fields:` with `signature_fields:`

**Prevention**: Always reference Phase 4 compiler schema documentation

---

### **PITFALL 2: Missing `instrumentor_framework` Field**

**❌ INCORRECT**:
```yaml
traceloop_mistral:
  signature_fields:
    - "gen_ai.system"
  confidence_weight: 0.95
  # ❌ Missing instrumentor_framework
```

**✅ CORRECT**:
```yaml
traceloop_mistral:
  signature_fields:
    - "gen_ai.system"
  confidence_weight: 0.95
  instrumentor_framework: "traceloop"  # ✅ Required field
```

**Error Message**: Compilation will fail with schema validation error

**Prevention**: Use Phase 4.2 template exactly as written

---

### **PITFALL 3: Using Instrumentor Prefixes in field_mappings.yaml**

**❌ INCORRECT**:
```yaml
config:
  model:
    source_rule: "traceloop_model_name"  # ❌ Has instrumentor prefix
```

**✅ CORRECT**:
```yaml
config:
  model:
    source_rule: "model_name"  # ✅ Base name (compiler routes dynamically)
```

**Why**: The compiler routes base names to instrumentor-specific rules at runtime

**How to Detect**:
```bash
# Check for instrumentor prefixes in field mappings
grep -E "(traceloop_|openinference_|openlit_)" config/dsl/providers/{provider}/field_mappings.yaml
```

**Expected**: No matches in source_rule values

**Prevention**: Phase 6 explicitly requires base names only

---

### **PITFALL 4: Fewer Than 2 Signature Fields**

**❌ INCORRECT**:
```yaml
traceloop_mistral:
  signature_fields:
    - "gen_ai.system"  # ❌ Only 1 field (minimum is 2)
```

**✅ CORRECT**:
```yaml
traceloop_mistral:
  signature_fields:
    - "gen_ai.system"
    - "gen_ai.request.model"  # ✅ At least 2 fields
```

**Error Message**: "Pattern must have at least 2 signature fields"

**Prevention**: Phase 4 requires minimum 2 fields per pattern

---

## ⚠️ **WARNING PITFALLS** (Will Cause Unexpected Behavior)

### **PITFALL 5: Assuming Instrumentor Support Without Code Verification**

**❌ INCORRECT Process**:
1. "Provider X exists, so instrumentors probably support it"
2. Create patterns without checking actual code
3. DSL compiles but never detects correctly

**✅ CORRECT Process** (Phase 2):
1. Check Traceloop GitHub: `github.com/traceloop/openllmetry/tree/main/packages/`
2. Verify provider-specific package exists
3. Extract actual attributes from source code
4. Document source URLs

**Example Verification**:
```bash
# Verify Traceloop support for Mistral
curl -s https://api.github.com/repos/traceloop/openllmetry/contents/packages | \
  grep "opentelemetry-instrumentation-mistralai"
```

**Prevention**: Phase 2 requires code repository verification, not assumptions

---

### **PITFALL 6: Using Estimated Pricing Without Flagging**

**❌ INCORRECT**:
```yaml
pricing_table:
  "mistral-small-latest": {"input": 0.20, "output": 0.60}
  # No indication this is estimated
```

**✅ CORRECT**:
```yaml
pricing_table:
  "mistral-small-latest": {"input": 0.20, "output": 0.60}  # Estimated based on tier

metadata:
  models_with_verified_pricing: 3
  models_with_estimated_pricing: 8  # Document estimated pricing
```

**Why**: Future maintainers need to know which prices need verification

**Prevention**: Phase 3 requires flagging verified vs. estimated pricing

---

### **PITFALL 7: Outdated Pricing Data**

**❌ INCORRECT**:
```yaml
# Pricing from 2024-01-01 (outdated)
pricing_table:
  "mistral-large-latest": {"input": 1.50, "output": 5.00}  # Old pricing
```

**✅ CORRECT**:
```yaml
# Pricing verified 2025-09-30
pricing_table:
  "mistral-large-latest": {"input": 2.00, "output": 6.00}  # Current pricing

metadata:
  pricing_date: "2025-09-30"  # Document verification date
  pricing_source: "https://mistral.ai/pricing"
```

**How to Detect**: Phase 7.5 validates pricing_date >= 2025-09-30

**Prevention**: Phase 3 requires current pricing (2025-09-30 or later)

---

### **PITFALL 8: Signature Collision Without Value Differentiation**

**❌ PROBLEM**:
```yaml
# Both patterns have IDENTICAL signatures AND values
traceloop_provider:
  signature_fields: ["gen_ai.system", "gen_ai.request.model"]
  # gen_ai.system value: "provider"

openlit_provider:
  signature_fields: ["gen_ai.system", "gen_ai.request.model"]
  # gen_ai.system value: "provider"  # ❌ Same value as traceloop!
```

**✅ ACCEPTABLE**:
```yaml
# Identical signatures but DIFFERENT values
traceloop_mistral:
  signature_fields: ["gen_ai.system", "gen_ai.request.model"]
  # gen_ai.system value: "MistralAI"  # Different value

openlit_mistral:
  signature_fields: ["gen_ai.system", "gen_ai.request.model"]
  # gen_ai.system value: "mistral"  # Different value (lowercase)
```

**Why Acceptable**: Compiler keeps first pattern, but value-based detection differentiates at runtime

**How to Detect**: Phase 4.3 Step 2B (intra-provider collision check)

**Prevention**: Document expected collisions and verify different values

---

## 📊 **QUALITY PITFALLS** (Will Reduce Coverage)

### **PITFALL 9: Missing Provider-Specific Features**

**❌ INCOMPLETE**:
```yaml
# Generic rules only (temperature, max_tokens)
# Missing Mistral-specific reasoning_tokens
```

**✅ COMPLETE**:
```yaml
# Include provider-specific features
mistral_reasoning_tokens:
  source_field: "gen_ai.usage.reasoning_tokens"  # Mistral-specific
  description: "Reasoning token count (Mistral advanced models)"
```

**Prevention**: Phase 3.3 identifies unique provider features to include

---

### **PITFALL 10: Fewer Than 7 Rules Per Instrumentor**

**❌ INSUFFICIENT**:
```yaml
# Only 4 rules for Traceloop (model_name, input, output, tokens)
# Missing temperature, max_tokens, top_p
```

**✅ SUFFICIENT**:
```yaml
# Minimum 7 rules per instrumentor
# model_name, input_messages, output_messages, prompt_tokens, 
# completion_tokens, temperature, max_tokens
```

**How to Detect**: Phase 5 coverage validation requires 7+ per instrumentor

**Prevention**: Use Phase 5.1 planning to ensure all required fields mapped

---

## 🔧 **PROCESS PITFALLS**

### **PITFALL 11: Batching All Instrumentors Together**

**❌ INCORRECT Process**:
1. Create all 42 rules for all 3 instrumentors at once
2. Skip incremental validation
3. Errors only caught at final compilation

**✅ CORRECT Process** (Phase 5):
1. Create Traceloop rules → validate YAML compiles
2. Create OpenInference rules → validate YAML compiles
3. Create OpenLit rules → validate YAML compiles
4. Final coverage validation

**Prevention**: Phase 5 now has blocking checkpoints between instrumentors

---

### **PITFALL 12: Skipping Pre-Compilation Validation**

**❌ INCORRECT Process**:
1. Complete Phases 0-7
2. Jump directly to Phase 8 compilation
3. Discover field naming errors at compilation

**✅ CORRECT Process** (Phase 7.5 - NEW):
1. Complete Phases 0-7
2. Run Phase 7.5 pre-compilation validation
3. Fix any errors detected
4. Proceed to Phase 8 with confidence

**Prevention**: Always run Phase 7.5 before Phase 8

---

## 📚 **DOCUMENTATION PITFALLS**

### **PITFALL 13: Missing Source URLs**

**❌ INCORRECT**:
```markdown
Traceloop supports Mistral AI
(No source URL provided)
```

**✅ CORRECT**:
```markdown
Traceloop supports Mistral AI

**Source**: https://github.com/traceloop/openllmetry/tree/main/packages/opentelemetry-instrumentation-mistralai
**Verified**: 2025-09-30
```

**Why**: Provides audit trail and enables future verification

**Prevention**: Every claim in RESEARCH_SOURCES.md must have source URL

---

### **PITFALL 14: Not Documenting "Why" Decisions**

**❌ UNCLEAR**:
```yaml
confidence_weight: 0.95  # No explanation why
```

**✅ CLEAR**:
```yaml
confidence_weight: 0.95  
# High confidence: Explicit provider name in gen_ai.system value
# Phase 4.1 uniqueness analysis: HIGH uniqueness, LOW collision risk
```

**Prevention**: Phase 4 requires documenting uniqueness rationale

---

## 🎓 **LESSONS FROM MISTRAL AI IMPLEMENTATION**

### **What Worked Well**

1. ✅ **Systematic phase execution** prevented major errors
2. ✅ **Evidence-based verification** caught instrumentor support early
3. ✅ **Current pricing** ensures production readiness
4. ✅ **Documentation-first** created clear audit trail

### **What Needs Improvement**

1. ⚠️ **Field naming** caused compilation failure (now fixed in Phase 4)
2. ⚠️ **Batching instrumentors** deviated from systematic approach (now fixed in Phase 5)
3. ⚠️ **Intra-provider collisions** not detected early (now added to Phase 4.3)

---

## 🔍 **DETECTION CHECKLIST**

Before final compilation, verify:

- [ ] All signature_fields use `signature_fields:` not `required_fields:`
- [ ] All patterns have `instrumentor_framework` field
- [ ] Field mappings use base names (no instrumentor prefixes)
- [ ] All patterns have 2+ signature fields
- [ ] Instrumentor support verified from code (not assumed)
- [ ] Pricing flagged as verified or estimated
- [ ] Pricing date is 2025-09-30 or later
- [ ] Intra-provider collisions documented
- [ ] Provider-specific features included
- [ ] 7+ rules per verified instrumentor
- [ ] Source URLs provided for all claims
- [ ] Pre-compilation validation run (Phase 7.5)

---

## 📖 **QUICK REFERENCE**

**When you see this error**: "Pattern must have at least 2 signature fields"  
**Fix**: Add more fields to signature_fields list

**When you see this error**: "Validation failed for provider X"  
**Fix**: Check Phase 7.5 validation steps

**When compilation succeeds but detection fails**:  
**Fix**: Verify instrumentor support from code (Phase 2)

**When pricing seems wrong**:  
**Fix**: Re-verify from official pricing page (Phase 3)

---

## 🎯 **BEST PRACTICES**

1. **Always** use Phase 4 compiler schema template
2. **Always** verify instrumentor support from code
3. **Always** document source URLs
4. **Always** run Phase 7.5 before compilation
5. **Always** flag estimated pricing
6. **Never** assume instrumentor support
7. **Never** use instrumentor prefixes in field_mappings.yaml
8. **Never** skip blocking checkpoints

---

**Updated**: 2025-09-30  
**Based On**: Mistral AI implementation retrospective  
**Framework Version**: v1.1

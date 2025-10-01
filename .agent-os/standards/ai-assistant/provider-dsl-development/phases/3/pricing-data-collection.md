# Task 3.2: Pricing Data Collection

**🎯 Collect CURRENT pricing for ALL models (2025-09-30 or later)**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 3.1 complete (Model list collected) ✅/❌
- [ ] Pricing documentation URL from Phase 1 available ✅/❌
- [ ] Model list has [X] models documented ✅/❌

🚨 **CRITICAL**: Pricing MUST be current (2025-09-30 or later) - no outdated data!

---

## 🛑 **EXECUTION**

### **Step 1: Open Pricing Documentation**

🛑 EXECUTE-NOW: Navigate to pricing documentation URL from Phase 1

URL: [From RESEARCH_SOURCES.md section 1.3]

📊 QUANTIFY-RESULTS: Pricing page loads: YES/NO

### **Step 2: Verify Pricing Currency**

🛑 EXECUTE-NOW: Confirm pricing currency and structure

Verify:
- Currency: USD / EUR / Other
- Pricing unit: per 1M tokens / per 1K tokens / per request / other
- Input vs Output separation: YES/NO
- Date/version of pricing (if shown)

📊 QUANTIFY-RESULTS: Currency = [CURRENCY], Unit = [UNIT], Date = [YYYY-MM-DD or N/A]

### **Step 3: Extract Pricing for ALL Models**

🛑 EXECUTE-NOW: Create pricing table for all models from Phase 3.1

**⚠️ CRITICAL**: Must include ALL models, including legacy/deprecated

**Format**:
```markdown
### Pricing Information (as of 2025-09-30)

**Pricing Structure**: ☑️ Per million tokens / Per request / Tiered / Other

**Currency**: [USD/EUR/etc.]

| Model | Input Cost | Output Cost | Unit | Notes |
|-------|------------|-------------|------|-------|
| `{model-1}` | ${X.XX} | ${Y.YY} | per 1M tokens | {special notes if any} |
| `{model-2}` | ${X.XX} | ${Y.YY} | per 1M tokens | |
| ... | ... | ... | ... | |

**Special Pricing Cases**:
- Batch API: {Discount if applicable}
- Cached prompts: {Discount if applicable}
- Fine-tuned models: {Pricing structure if different}
- Enterprise tiers: {Different pricing if applicable}
```

📊 COUNT-AND-DOCUMENT: Models with pricing: [X/TOTAL]

### **Step 4: Handle Missing Pricing**

🛑 EXECUTE-NOW: Document any models without pricing

If ANY model lacks pricing:
- Mark as "Pricing not publicly available"
- Note in "Notes" column
- Flag for manual investigation

📊 QUANTIFY-RESULTS: All models have pricing: YES/NO

### **Step 5: Verify Pricing Currency**

🛑 EXECUTE-NOW: Confirm pricing is current

Check:
- Pricing page shows recent update date: [DATE]
- Pricing matches current models from 3.1
- No outdated model pricing included

📊 QUANTIFY-RESULTS: Pricing is current (2025-09-30+): YES/NO

🚨 **CRITICAL**: If pricing appears outdated, flag for verification

### **Step 6: Document in RESEARCH_SOURCES**

🛑 EXECUTE-NOW: Add complete pricing table to RESEARCH_SOURCES.md

```markdown
### **3.2 Pricing Data**

[PASTE COMPLETE PRICING TABLE FROM STEP 3]

**Pricing Summary**:
- Total models priced: [X/TOTAL]
- Currency: [USD/EUR/etc.]
- Unit: [per 1M tokens/per request/etc.]
- Input/Output separated: [YES/NO]

**Special Cases**:
- Batch discounts: [YES/NO - description]
- Caching: [YES/NO - description]
- Fine-tuning: [Different pricing - description]
- Enterprise: [Custom pricing available]

**Source**: [URL from Phase 1]
**Verified**: 2025-09-30
**Pricing Date**: [Date from pricing page if shown, or "2025-09-30"]
```

📊 QUANTIFY-RESULTS: Pricing documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Pricing Data Complete
- [ ] Pricing for ALL models collected ✅/❌
- [ ] Currency clearly documented ✅/❌
- [ ] Pricing unit specified ✅/❌
- [ ] Input/Output costs separated (if applicable) ✅/❌
- [ ] Pricing is current (2025-09-30+) ✅/❌
- [ ] Special cases documented ✅/❌
- [ ] Added to RESEARCH_SOURCES.md ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding with outdated or incomplete pricing

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 3.2 → Pricing collected for [X] models
🎯 NEXT-MANDATORY: [provider-features.md](provider-features.md)

# Task 1.3: Pricing Documentation Discovery

**🎯 Locate and verify pricing documentation**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 1.2 complete (Models docs verified) ✅/❌
- [ ] Model count estimated ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Search for Pricing Documentation**

🛑 EXECUTE-NOW: Search for provider pricing information

**Common URL patterns to check:**
- `https://{provider}.com/pricing`
- `https://pricing.{provider}.com`
- `https://platform.{provider}.com/pricing`
- `https://docs.{provider}.com/pricing`
- API docs pricing section

**Blog/announcement approach:**
- Check blog for model launch announcements (often include pricing)
- Look for "Introducing [Model]" posts

📊 COUNT-AND-DOCUMENT: URLs checked: [NUMBER]

### **Step 2: Verify Pricing Information Present**

🛑 EXECUTE-NOW: Confirm URL contains pricing data

Look for:
- Per-token costs (input/output separated)
- Per-request costs
- Currency clearly stated (USD/EUR/etc.)
- Pricing for multiple models

📊 QUANTIFY-RESULTS: Pricing found: YES/NO

### **Step 3: Verify Pricing Structure**

🛑 EXECUTE-NOW: Identify pricing model

Determine structure:
- ☑️ Per million tokens (most common)
- ☑️ Per request/API call
- ☑️ Tiered pricing (volume discounts)
- ☑️ Subscription-based
- ☑️ Other

📊 QUANTIFY-RESULTS: Pricing structure: [TYPE]

### **Step 4: Verify Currency and Units**

🛑 EXECUTE-NOW: Document pricing details

Note:
- Currency: USD / EUR / Other
- Unit: per 1M tokens / per 1K tokens / per request
- Input vs Output pricing separated: YES/NO

📊 COUNT-AND-DOCUMENT: Currency: [CURRENCY], Unit: [UNIT]

### **Step 5: Verify Coverage**

🛑 EXECUTE-NOW: Check pricing completeness

Estimate:
- Models with pricing: [NUMBER]
- Models without pricing: [NUMBER]
- Pricing is current (dated if available)

📊 QUANTIFY-RESULTS: Covers all models: YES/NO/PARTIAL

### **Step 6: Document in RESEARCH_SOURCES**

🛑 EXECUTE-NOW: Add to RESEARCH_SOURCES.md

```markdown
### **1.3 Pricing**
- **URL**: [VERIFIED_URL]
- **Last verified**: 2025-09-30
- **Status**: ✅ VERIFIED
- **Currency**: [USD/EUR/etc.]
- **Pricing structure**: [per-token/per-request/tiered/other]
- **Coverage**: [Covers X/Y models or "all current models"]
- **Notes**: [Special pricing cases - batch discounts, caching, enterprise tiers]
```

📊 QUANTIFY-RESULTS: Documented in RESEARCH_SOURCES: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Pricing Documentation Verified
- [ ] URL found and documented ✅/❌
- [ ] Pricing data present ✅/❌
- [ ] Currency clearly stated ✅/❌
- [ ] Pricing structure identified ✅/❌
- [ ] Coverage assessed ✅/❌
- [ ] Added to RESEARCH_SOURCES.md ✅/❌
- [ ] Evidence table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without pricing documentation

**Note**: If pricing not publicly available, document as "Not Publicly Available" and mark for manual collection

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 1.3 → Pricing docs discovered and verified
🎯 NEXT-MANDATORY: [changelog-discovery.md](changelog-discovery.md)

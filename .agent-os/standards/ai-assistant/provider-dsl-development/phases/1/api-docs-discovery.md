# Task 1.1: API Documentation Discovery

**🎯 Locate and verify official API documentation**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] RESEARCH_SOURCES.md exists ✅/❌
- [ ] Provider name known ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Search for API Documentation**

🛑 EXECUTE-NOW: Search for provider API documentation

**Common URL patterns to check:**
- `https://docs.{provider}.com/api`
- `https://api.{provider}.com/docs`
- `https://platform.{provider}.com/docs`
- `https://{provider}.com/documentation`
- `https://developers.{provider}.com`

**For GitHub-first providers:**
- `https://github.com/{provider}/{provider}/blob/main/README.md`
- Look for docs links in README

📊 COUNT-AND-DOCUMENT: URLs checked: [NUMBER]

### **Step 2: Verify URL Loads**

🛑 EXECUTE-NOW: Confirm URL loads successfully

```bash
curl -I https://[DISCOVERED_URL] | head -5
```

🛑 PASTE-OUTPUT: HTTP status code

📊 QUANTIFY-RESULTS: URL loads (200 OK): YES/NO

### **Step 3: Verify Content Currency**

🛑 EXECUTE-NOW: Check for date indicators

Look for:
- Copyright year (should be 2024 or 2025)
- "Last updated" dates
- Recent API versions

📊 QUANTIFY-RESULTS: Dated 2024+: YES/NO

### **Step 4: Document in RESEARCH_SOURCES**

🛑 EXECUTE-NOW: Add to RESEARCH_SOURCES.md

```markdown
## 1. **Official Documentation**

### **1.1 API Documentation**
- **URL**: [VERIFIED_URL]
- **Last verified**: 2025-09-30
- **Status**: ✅ VERIFIED
- **Notes**: [What sections are available - endpoints, reference, guides, etc.]
```

📊 QUANTIFY-RESULTS: Documented in RESEARCH_SOURCES: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: API Documentation Verified
- [ ] URL found and documented ✅/❌
- [ ] URL loads successfully (HTTP 200) ✅/❌
- [ ] Content is current (2024+) ✅/❌
- [ ] Added to RESEARCH_SOURCES.md ✅/❌
- [ ] Evidence table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without verified URL

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 1.1 → API docs discovered and verified
🎯 NEXT-MANDATORY: [models-docs-discovery.md](models-docs-discovery.md)

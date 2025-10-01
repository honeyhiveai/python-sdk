# Phase 1: Strategy 3 - Published OpenAPI URL

**🎯 Try common OpenAPI URL patterns**

---

## 🛑 **EXECUTION**

### **Step 1: Try Standard URL Patterns**

🛑 EXECUTE-NOW: Test OpenAPI URL patterns
```bash
# Pattern 1: API subdomain
curl -I https://api.{provider}.com/openapi.json
curl -I https://api.{provider}.com/v1/openapi.json
curl -I https://api.{provider}.com/swagger.json

# Pattern 2: Main domain
curl -I https://{provider}.com/api/openapi.json
curl -I https://{provider}.com/openapi.json

# Pattern 3: Docs subdomain  
curl -I https://docs.{provider}.com/openapi.json
curl -I https://developer.{provider}.com/openapi.json

# Pattern 4: Well-known
curl -I https://api.{provider}.com/.well-known/openapi.json
```

📊 COUNT-AND-DOCUMENT: URLs tested: [NUMBER]
📊 QUANTIFY-RESULTS: Working URL found: [YES/NO]

### **Step 2: Verify Response**

⚠️ EVIDENCE-REQUIRED: If URL found:
- Working URL: [URL]
- Content-Type: [value]
- File size: [KB]
- OpenAPI version: [version from content]

### **Step 3: Document Source**

🛑 EXECUTE-NOW: Update SDK_SOURCES.md
```markdown
## Strategy 3: Published OpenAPI URL

**Status**: [✅ FOUND | ❌ NOT FOUND]
**URL**: [URL]
**Format**: [JSON | YAML]
**Size**: [KB]
**Verified**: [YYYY-MM-DD]

### Download Command
```bash
curl -o {provider}-openapi.json {URL}
```
```

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Strategy 3 Complete
- [ ] All URL patterns tested ✅/❌
- [ ] Response verified (if found) ✅/❌
- [ ] SDK_SOURCES.md updated ✅/❌

---

## 🎯 **NAVIGATION**

### **If FOUND ✅**:
📊 QUANTIFY-RESULTS: Published OpenAPI URL: YES
🛑 UPDATE-TABLE: Phase 1 → OpenAPI URL located
🎯 NEXT-MANDATORY: ../2/extract-openapi-spec.md

### **If NOT FOUND ❌**:
📊 QUANTIFY-RESULTS: Published OpenAPI URL: NO
🛑 UPDATE-TABLE: Phase 1.3 → Strategy 3 failed, trying Strategy 4
🎯 NEXT-MANDATORY: [strategy-4-protobuf.md](strategy-4-protobuf.md)

---

**Phase**: 1  
**Strategy**: 3  
**Lines**: ~78

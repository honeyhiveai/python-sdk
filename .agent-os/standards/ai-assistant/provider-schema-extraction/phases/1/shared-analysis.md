# Phase 1: Schema Source Discovery

**🎯 Identify the best available source for provider response schemas**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Phase 0 Complete
- [ ] Provider verified and documented ✅/❌
- [ ] Directory structure created ✅/❌
- [ ] SDK_SOURCES.md initialized ✅/❌
- [ ] PROGRESS.md ready ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without Phase 0 completion

---

## 📋 **PHASE 1 STRATEGY**

### **Priority Cascade** (Try in Order)

**Strategy 1**: Dedicated OpenAPI Repository (BEST)
- ✅ Official, versioned, machine-readable
- 🎯 NEXT-MANDATORY: [strategy-1-openapi-repo.md](strategy-1-openapi-repo.md)

**Strategy 2**: OpenAPI in SDK Repository
- ✅ Bundled with SDK, easy to fetch
- Skip to: [strategy-2-sdk-openapi.md](strategy-2-sdk-openapi.md)

**Strategy 3**: Published OpenAPI URL
- ✅ Direct download, no clone needed
- Skip to: [strategy-3-published-url.md](strategy-3-published-url.md)

**Strategy 4**: Protobuf Definitions
- ⚠️ Requires conversion to JSON Schema
- Skip to: [strategy-4-protobuf.md](strategy-4-protobuf.md)

**Strategy 5**: SDK Type Definitions
- ⚠️ Requires parsing and extraction
- Skip to: [strategy-5-sdk-types.md](strategy-5-sdk-types.md)

**Strategy 6**: Manual Documentation
- ❌ Last resort, manual extraction
- Skip to: [strategy-6-manual.md](strategy-6-manual.md)

---

## 🛑 **EXECUTION**

⚠️ MUST-COMPLETE: Strategy 1 first (always start here)

🎯 NEXT-MANDATORY: [strategy-1-openapi-repo.md](strategy-1-openapi-repo.md)

---

**Phase**: 1  
**Type**: Orchestrator  
**Lines**: ~65

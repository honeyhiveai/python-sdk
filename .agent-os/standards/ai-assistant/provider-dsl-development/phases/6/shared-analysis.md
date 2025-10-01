# Phase 6: Field Mappings Development

**🎯 Map extracted data to HoneyHive 4-section schema**

---

## 🚨 **ENTRY CHECKPOINT**

🛑 VALIDATE-GATE: Phase 6 Prerequisites
- [ ] Phase 5 complete with navigation rules ✅/❌
- [ ] All verified instrumentors have rules ✅/❌
- [ ] Base rule names defined ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without navigation rules

---

## 🛑 **MANDATORY EXECUTION SEQUENCE**

### **Task 6.1: Inputs Section**
⚠️ MUST-READ: [inputs-section.md](inputs-section.md)
📊 COUNT-AND-DOCUMENT: Input fields mapped

### **Task 6.2: Outputs Section**
⚠️ MUST-READ: [outputs-section.md](outputs-section.md)
📊 COUNT-AND-DOCUMENT: Output fields mapped

### **Task 6.3: Config Section**
⚠️ MUST-READ: [config-section.md](config-section.md)
📊 QUANTIFY-RESULTS: model field marked required

### **Task 6.4: Metadata Section**
⚠️ MUST-READ: [metadata-section.md](metadata-section.md)
📊 QUANTIFY-RESULTS: provider field marked required

🎯 NEXT-MANDATORY: [inputs-section.md](inputs-section.md)

---

## 📋 **PHASE 6 OVERVIEW**

**Purpose**: Map to HoneyHive 4-section schema

**Tasks**: 4 section mapping tasks

**Expected Duration**: 30-45 minutes

**⚠️ CRITICAL**: 
- Use BASE rule names (no instrumentor prefixes!)
- model and provider MUST be required: true

**Schema Sections**:
1. **inputs**: prompts, messages, chat history
2. **outputs**: responses, completions, tool calls
3. **config**: model, temperature, max_tokens, parameters
4. **metadata**: provider, instrumentor, tokens, cost

---

**Map using base names for dynamic routing!**

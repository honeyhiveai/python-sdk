# Phase 7: Transforms Development

**🎯 Create transformation functions with CURRENT pricing**

---

## 🚨 **ENTRY CHECKPOINT**

🛑 VALIDATE-GATE: Phase 7 Prerequisites
- [ ] Phase 6 complete with field mappings ✅/❌
- [ ] Pricing data from Phase 3 available ✅/❌
- [ ] Pricing verified as current (2025-09-30+) ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without current pricing

---

## 🛑 **MANDATORY EXECUTION SEQUENCE**

### **Task 7.1: Message Extraction Transforms**
⚠️ MUST-READ: [message-extraction.md](message-extraction.md)
📊 COUNT-AND-DOCUMENT: Extract user, system, assistant

### **Task 7.2: Finish Reason Normalization**
⚠️ MUST-READ: [finish-reason-normalization.md](finish-reason-normalization.md)
📊 QUANTIFY-RESULTS: Provider values mapped

### **Task 7.3: Cost Calculation**
⚠️ MUST-READ: [cost-calculation.md](cost-calculation.md)
📊 QUANTIFY-RESULTS: Pricing matches Phase 3 exactly

### **Task 7.4: Instrumentor Detection**
⚠️ MUST-READ: [instrumentor-detection.md](instrumentor-detection.md)
📊 COUNT-AND-DOCUMENT: Detection patterns defined

🎯 NEXT-MANDATORY: [message-extraction.md](message-extraction.md)

---

## 📋 **PHASE 7 OVERVIEW**

**Purpose**: Create build-time transform functions

**Tasks**: 4 transform development tasks

**Expected Duration**: 45-60 minutes

**⚠️ MOST CRITICAL TASK**: Cost calculation with verified pricing

**Required Transforms**:
1. extract_user_prompt
2. extract_system_prompt
3. extract_completion_text
4. extract_finish_reason_normalized
5. calculate_{provider}_cost
6. detect_instrumentor

---

**Use EXACT pricing from Phase 3!**

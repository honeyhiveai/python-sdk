# Phase 2: Logging Analysis - Shared Analysis

**🎯 Execute all components systematically. Shared analysis provides foundation for path-specific strategies.**

🛑 VALIDATE-GATE: Phase 2 Entry Requirements
- [ ] Phase 1 completed with comprehensive evidence ✅/❌
- [ ] Framework contract acknowledged and binding ✅/❌
- [ ] Test path selected and locked (unit OR integration) ✅/❌
- [ ] Phase 1 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without Phase 1 completion

## 🚨 **ENTRY CHECKPOINT**
- [ ] Phase 1 completed and validated
- [ ] Framework contract acknowledged: [../../core/binding-contract.md](../../core/binding-contract.md)
- [ ] Test path selected: Unit or Integration (determines next steps)
- [ ] Production file confirmed: `src/honeyhive/tracer/instrumentation/initialization.py`

## 🛑 **MANDATORY EXECUTION SEQUENCE**

### **Task 2.1: Logging Call Detection**
⚠️ MUST-READ: [logging-call-detection.md](logging-call-detection.md)
🛑 EXECUTE-NOW: All logging detection commands
🛑 PASTE-OUTPUT: Complete logging analysis results
📊 COUNT-AND-DOCUMENT: Logging calls found: [NUMBER]

### **Task 2.2: Safe_log Pattern Analysis**
⚠️ MUST-READ: [safelog-pattern-analysis.md](safelog-pattern-analysis.md)
🛑 EXECUTE-NOW: All safe_log pattern commands
📊 QUANTIFY-RESULTS: Safe_log usage patterns: [NUMBER]

### **Task 2.3: Level Classification**
⚠️ MUST-READ: [level-classification.md](level-classification.md)
🛑 EXECUTE-NOW: All level classification commands
📊 COUNT-AND-DOCUMENT: Log levels identified: [NUMBER]

### **Task 2.4-2.5: Path-Specific Strategy**
🛑 VALIDATE-GATE: Execute based on selected path only
- **Unit Path**: ⚠️ MUST-READ [unit-logging-strategy.md](unit-logging-strategy.md)
- **Integration Path**: ⚠️ MUST-READ [integration-logging-strategy.md](integration-logging-strategy.md)
🚨 FRAMEWORK-VIOLATION: If executing both strategies

### **Task 2.6: Evidence Collection**
⚠️ MUST-READ: [evidence-collection-framework.md](evidence-collection-framework.md)
🛑 UPDATE-TABLE: Phase 2 evidence consolidated
🛑 VALIDATE-GATE: All Phase 2 tasks complete with evidence

## 🚨 **EXECUTION GUARDRAILS**

### **Sequential Requirements**
🚨 FRAMEWORK-VIOLATION: If skipping components or jumping ahead
-   **Cannot skip components** - each builds on previous
-   **Shared analysis first** (2.1-2.3) before path selection
-   **Path-specific strategy** (2.4 OR 2.5) based on test type
🛑 EXECUTE-NOW: All tasks in exact sequence

### **Evidence Requirements**
📊 QUANTIFY-RESULTS: All results must be measurable
-   **Quantified results**: "X log calls found" not "analysis complete"
-   **Command outputs**: Actual grep/Python results pasted
-   **Validation proof**: Quality gates passed with evidence
-   **Progress tracking**: Updated tables with real numbers
⚠️ EVIDENCE-REQUIRED: Complete command output for all tasks

## 🛑 **PHASE 2 COMPLETION GATE**

🛑 VALIDATE-GATE: Phase 2 Complete Evidence
- [ ] All logging calls detected and documented ✅/❌
- [ ] Safe_log patterns analyzed with counts ✅/❌
- [ ] Log levels classified with evidence ✅/❌
- [ ] Path-specific strategy executed (unit OR integration) ✅/❌
- [ ] Evidence framework completed with consolidated results ✅/❌
- [ ] Progress table updated with Phase 2 completion ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding to Phase 3 without all validation gates passed
🛑 UPDATE-TABLE: Phase 2 → COMPLETE with comprehensive evidence
🎯 NEXT-MANDATORY: Phase 3 Dependency Analysis (only after validation)

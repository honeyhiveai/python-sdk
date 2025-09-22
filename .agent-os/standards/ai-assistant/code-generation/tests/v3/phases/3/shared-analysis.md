# Phase 3: Dependency Analysis - Shared Analysis

**🎯 Execute all components systematically. Shared analysis provides foundation for path-specific strategies.**

## 🚨 **ENTRY CHECKPOINT**
- [ ] Phase 2 completed and validated
- [ ] Framework contract acknowledged: [../../core/binding-contract.md](../../core/binding-contract.md)
- [ ] Test path selected: Unit or Integration (determines next steps)
- [ ] Production file confirmed: `src/honeyhive/tracer/instrumentation/initialization.py`

## 📋 **COMPONENTS**

1.  **Dependency Mapping**: [dependency-mapping.md](dependency-mapping.md)
2.  **External Library Analysis**: [external-library-analysis.md](external-library-analysis.md)
3.  **Internal Module Analysis**: [internal-module-analysis.md](internal-module-analysis.md)
4.  **Configuration Dependencies**: [configuration-dependencies.md](configuration-dependencies.md)
5.  **Unit Mock Strategy**: [unit-dependency-strategy.md](unit-dependency-strategy.md) (Unit path only)
6.  **Integration Real Strategy**: [integration-dependency-strategy.md](integration-dependency-strategy.md) (Integration path only)
7.  **Evidence Framework**: [evidence-collection-framework.md](evidence-collection-framework.md)

## 🚨 **EXECUTION GUARDRAILS**

### **Sequential Requirements**
🚨 FRAMEWORK-VIOLATION: If skipping components or jumping ahead
-   **Cannot skip components** - each builds on previous
-   **Shared analysis first** (3.1-3.4) before path selection
-   **Path-specific strategy** (3.5 OR 3.6) based on test type
🛑 EXECUTE-NOW: All tasks in exact sequence

### **Evidence Requirements**
📊 QUANTIFY-RESULTS: All results must be measurable
-   **Quantified results**: "X dependencies found" not "analysis complete"
-   **Command outputs**: Actual grep/Python results pasted
-   **Validation proof**: Quality gates passed with evidence
-   **Progress tracking**: Updated tables with real numbers
⚠️ EVIDENCE-REQUIRED: Complete command output for all tasks

## 🛑 **PHASE 3 COMPLETION GATE**

🛑 VALIDATE-GATE: Phase 3 Complete Evidence
- [ ] All dependencies mapped and documented ✅/❌
- [ ] External libraries analyzed with counts ✅/❌
- [ ] Internal modules analyzed with evidence ✅/❌
- [ ] Configuration dependencies identified ✅/❌
- [ ] Path-specific strategy executed (unit OR integration) ✅/❌
- [ ] Evidence framework completed with consolidated results ✅/❌
- [ ] Progress table updated with Phase 3 completion ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding to Phase 4 without all validation gates passed
🛑 UPDATE-TABLE: Phase 3 → COMPLETE with comprehensive evidence
🎯 NEXT-MANDATORY: Phase 4 Usage Pattern Analysis (only after validation)

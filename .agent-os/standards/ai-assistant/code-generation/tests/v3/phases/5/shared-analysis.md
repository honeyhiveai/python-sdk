# Phase 5: Coverage Analysis - Shared Analysis

**🎯 Execute all components systematically. Shared analysis provides foundation for path-specific strategies.**

🛑 VALIDATE-GATE: Phase 5 Entry Requirements
- [ ] Phase 4 completed with comprehensive evidence ✅/❌
- [ ] Framework contract acknowledged and binding ✅/❌
- [ ] Test path selected and locked (unit OR integration) ✅/❌
- [ ] Phase 4 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without Phase 4 completion

## 🚨 **ENTRY CHECKPOINT**
- [ ] Phase 4 completed and validated
- [ ] Framework contract acknowledged: [../../core/binding-contract.md](../../core/binding-contract.md)
- [ ] Test path selected: Unit or Integration (determines coverage targets)
- [ ] Production file confirmed: `src/honeyhive/tracer/instrumentation/initialization.py`

## 📋 **COMPONENTS**

1.  **Line Coverage Analysis**: [line-coverage-analysis.md](line-coverage-analysis.md)
2.  **Branch Coverage Analysis**: [branch-coverage-analysis.md](branch-coverage-analysis.md)
3.  **Function Coverage Analysis**: [function-coverage-analysis.md](function-coverage-analysis.md)
4.  **Unit Coverage Strategy**: [unit-coverage-strategy.md](unit-coverage-strategy.md) (Unit path only)
5.  **Integration Coverage Strategy**: [integration-coverage-strategy.md](integration-coverage-strategy.md) (Integration path only)
6.  **Evidence Framework**: [evidence-collection-framework.md](evidence-collection-framework.md)

## 🚨 **EXECUTION GUARDRAILS**

### **Sequential Requirements**
-   **Cannot skip components** - each builds on previous
-   **Shared analysis first** (1-3) before path selection
-   **Path-specific strategy** (4 OR 5) based on test type

### **Evidence Requirements**
-   **Quantified results**: "X lines to cover" not "analysis complete"
-   **Command outputs**: Actual analysis results pasted
-   **Validation proof**: Quality gates passed with evidence
-   **Progress tracking**: Updated tables with real numbers

## 🛤️ **PATH SELECTION**
-   **Unit**: Execute [unit-coverage-strategy.md](unit-coverage-strategy.md) (90%+ coverage target)
-   **Integration**: Execute [integration-coverage-strategy.md](integration-coverage-strategy.md) (functionality focus)

**Execute all tasks 5.1-5.6 systematically.**

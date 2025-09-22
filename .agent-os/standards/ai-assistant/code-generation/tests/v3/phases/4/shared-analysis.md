# Phase 4: Usage Pattern Analysis - Shared Analysis

**🎯 Execute all components systematically. Shared analysis provides foundation for path-specific strategies.**

🛑 VALIDATE-GATE: Phase 4 Entry Requirements
- [ ] Phase 3 completed with comprehensive evidence ✅/❌
- [ ] Framework contract acknowledged and binding ✅/❌
- [ ] Test path selected and locked (unit OR integration) ✅/❌
- [ ] Phase 3 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without Phase 3 completion

## 🚨 **ENTRY CHECKPOINT**
- [ ] Phase 3 completed and validated
- [ ] Framework contract acknowledged: [../../core/binding-contract.md](../../core/binding-contract.md)
- [ ] Test path selected: Unit or Integration (determines next steps)
- [ ] Production file confirmed: `src/honeyhive/tracer/instrumentation/initialization.py`

## 📋 **COMPONENTS**

1.  **Function Call Patterns**: [function-call-patterns.md](function-call-patterns.md)
2.  **Control Flow Analysis**: [control-flow-analysis.md](control-flow-analysis.md)
3.  **Error Handling Patterns**: [error-handling-patterns.md](error-handling-patterns.md)
4.  **State Management Analysis**: [state-management-analysis.md](state-management-analysis.md)
5.  **Unit Usage Strategy**: [unit-usage-strategy.md](unit-usage-strategy.md) (Unit path only)
6.  **Integration Usage Strategy**: [integration-usage-strategy.md](integration-usage-strategy.md) (Integration path only)
7.  **Evidence Framework**: [evidence-collection-framework.md](evidence-collection-framework.md)

## 🚨 **EXECUTION GUARDRAILS**

### **Sequential Requirements**
-   **Cannot skip components** - each builds on previous
-   **Shared analysis first** (1-4) before path selection
-   **Path-specific strategy** (5 OR 6) based on test type

### **Evidence Requirements**
-   **Quantified results**: "X patterns found" not "analysis complete"
-   **Command outputs**: Actual grep/Python results pasted
-   **Validation proof**: Quality gates passed with evidence
-   **Progress tracking**: Updated tables with real numbers

## 🛤️ **PATH SELECTION**
-   **Unit**: Execute [unit-usage-strategy.md](unit-usage-strategy.md) (mock usage patterns)
-   **Integration**: Execute [integration-usage-strategy.md](integration-usage-strategy.md) (real usage validation)

**Execute all tasks 4.1-4.7 systematically.**

# Phase 6: Pre-Generation Validation - Shared Analysis

**🎯 Execute all components systematically. Shared analysis provides foundation for path-specific strategies.**

🛑 VALIDATE-GATE: Phase 6 Entry Requirements
- [ ] Phase 5 completed with comprehensive evidence ✅/❌
- [ ] Framework contract acknowledged and binding ✅/❌
- [ ] Test path selected and locked (unit OR integration) ✅/❌
- [ ] Phase 5 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without Phase 5 completion

## 🚨 **ENTRY CHECKPOINT**
- [ ] Phase 5 completed and validated
- [ ] Framework contract acknowledged: [../../core/binding-contract.md](../../core/binding-contract.md)
- [ ] Test path selected: Unit or Integration (determines validation focus)
- [ ] Production file confirmed: `src/honeyhive/tracer/instrumentation/initialization.py`

## 📋 **COMPONENTS**

1.  **Test Generation Readiness**: [test-generation-readiness.md](test-generation-readiness.md)
2.  **Quality Standards Preparation**: [quality-standards-preparation.md](quality-standards-preparation.md)
3.  **Template Syntax Validation**: [template-syntax-validation.md](template-syntax-validation.md)
4.  **Unit Pre-Generation**: [unit-pre-generation.md](unit-pre-generation.md) (Unit path only)
5.  **Integration Pre-Generation**: [integration-pre-generation.md](integration-pre-generation.md) (Integration path only)
6.  **Evidence Framework**: [evidence-collection-framework.md](evidence-collection-framework.md)

## 🚨 **EXECUTION GUARDRAILS**

### **Sequential Requirements**
-   **Cannot skip components** - each validates readiness
-   **Shared validation first** (1-3) before path selection
-   **Path-specific validation** (4 OR 5) based on test type

### **Evidence Requirements**
-   **Validation results**: "PASS/FAIL" with specific issues
-   **Readiness confirmation**: All prerequisites met
-   **Quality gate proof**: Standards validated
-   **Template validation**: Syntax and patterns verified

## 🛤️ **PATH SELECTION**
-   **Unit**: Execute [unit-pre-generation.md](unit-pre-generation.md) (mock readiness)
-   **Integration**: Execute [integration-pre-generation.md](integration-pre-generation.md) (real API readiness)

**Execute all tasks 6.1-6.6 systematically.**

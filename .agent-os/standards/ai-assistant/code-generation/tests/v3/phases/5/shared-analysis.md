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

## 🛑 **BLOCKING VALIDATION GATE: PHASE 5 COMPLETION**

⛔ **MANDATORY EVIDENCE BEFORE PROCEEDING TO PHASE 6**

Answer these questions with **quantified evidence**. Cannot proceed without YES to all.

### **Coverage Completeness Check**

**Q1: Are ALL methods in production file included in coverage analysis?**
- [ ] YES - [NUMBER] methods identified, [NUMBER] test scenarios planned
- [ ] NO - List missing methods:

🚨 **FRAMEWORK-VIOLATION**: If any production methods are missing from analysis

**Q2: Does planned test count support 90%+ coverage target?**
- [ ] YES - [NUMBER] tests planned for [NUMBER] lines = estimated [XX]% coverage
- [ ] NO - Coverage estimate: [XX]% (explain gap)

⛔ **FRAMEWORK-HALT**: If coverage estimate <85%, must add more test scenarios

**Q3: Are complex internal methods covered (not just public API)?**
- [ ] YES - Internal methods have dedicated tests: [list method names]
- [ ] NO - Only public API tested

🚨 **FRAMEWORK-VIOLATION**: Unit tests must cover internal methods for full coverage

### **Method-Level Coverage Table (MANDATORY)**

📊 **REQUIRED**: Complete this table for EVERY method before Phase 6

| Method Name | Lines | Complexity | Test Scenarios | Tests Planned | Est. Coverage |
|-------------|-------|------------|----------------|---------------|---------------|
| method_1 | 25 | Medium | 4 (success, error, edge, invalid) | 4 | ~90% |
| method_2 | 15 | Low | 2 (success, empty input) | 2 | ~85% |
| ... | ... | ... | ... | ... | ... |

**Table Requirements**:
- [ ] ALL methods from Phase 1 analysis listed
- [ ] Test scenario count ≥ 2 for every method
- [ ] Total tests planned = sum of "Tests Planned" column
- [ ] No method shows 0% estimated coverage

⛔ **CANNOT PROCEED**: Missing methods in table = incomplete Phase 5

### **Validation Checklist**

- [ ] Total tests planned: [NUMBER] (if [NUMBER] < methods * 2, explain why)
- [ ] Estimated overall coverage: [XX]% (must be ≥85%)
- [ ] All internal methods included: YES/NO
- [ ] Complex methods have ≥3 test scenarios: YES/NO

🛑 **BLOCKING**: Must show this validation before proceeding to Phase 6

---

### **🚨 CRITICAL: Multi-Module Testing Warning**

**If testing multiple modules for a single task (e.g., TASK-015 with 4 validation modules)**:

#### **Self-Check Question: Module Combining Prevention**

**Question**: "Am I about to suggest combining multiple modules or generating multiple test files at once to save time or tokens?"

**Required Response**: **"NO - Each module must be tested individually using the full 8-phase framework"**

**If YES (attempting to combine)**:
- 🚨 **STOP IMMEDIATELY**
- This violates "Accuracy Over Speed" principle
- Each module requires complete phase execution for quality
- Token savings are NOT worth coverage/quality loss

**Evidence from TASK-015**:
- AI attempted to combine all 4 modules after Module 1
- User corrected: "no, do this the right way per standards"
- **Result if combined**: Estimated 70-80% coverage, lower quality
- **Result systematic**: Achieved 96.82% average coverage, perfect quality

#### **Mandatory Multi-Module Approach**

When testing N modules:
1. ✅ Complete ALL 8 phases for Module 1
2. ✅ Validate Module 1 achieves quality gates (100% pass, 90%+ coverage, 10.0/10 Pylint, 0 MyPy)
3. ✅ Complete ALL 8 phases for Module 2
4. ✅ Repeat until all N modules tested

❌ **NEVER**:
- Generate tests for multiple modules in one Phase 7 execution
- Combine analysis phases across modules
- Skip phases because "previous module was similar"
- Offer to "accelerate" by testing multiple modules together

**Why Systematic Approach Is Required**:
- Each module has unique complexity and edge cases
- Phase 6.5 Pre-Write Validation must review each module's specific patterns
- Production code quality issues are module-specific
- Coverage gaps are easier to identify and fix per-module

**Framework Principle**: **Accuracy Over Speed** - Always

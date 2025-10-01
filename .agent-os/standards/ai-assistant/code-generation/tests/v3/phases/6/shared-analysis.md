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
6.  **String Processing Standards Review**: [Inline task - see TASK 6.6 below]
7.  **MyPy Type Annotation Standards Review**: [Inline task - see TASK 6.7 below]
8.  **Evidence Framework**: [evidence-collection-framework.md](evidence-collection-framework.md)

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

## 📋 **INLINE TASKS**

### **TASK 6.6: Load String Processing Standards**
🛑 EXECUTE-NOW: Read string processing best practices
⚠️ MUST-READ: [../../../../best-practices.md](../../../../best-practices.md) (lines 119-247)

**What to Learn**:
- ✅ Prefer native Python string operations (`in`, `startswith`, `split`)
- ❌ Avoid regex for simple substring matching or parsing
- ✅ Use regex ONLY for complex pattern matching (version strings, log parsing)

**Examples**:
```python
# ✅ PREFERRED in test assertions
with pytest.raises(ValueError) as exc_info:
    function()
assert "expected text" in str(exc_info.value)

# ⚠️ ACCEPTABLE in tests (but less preferred)
with pytest.raises(ValueError, match=r"expected text"):
    function()
```

📊 COUNT-AND-DOCUMENT: String processing standards reviewed: [YES/NO]
🛑 UPDATE-TABLE: Task 6.6 complete → String processing patterns understood

### **TASK 6.7: Load MyPy Type Annotation Standards**
🛑 EXECUTE-NOW: Read MyPy compliance guidelines
⚠️ MUST-READ: [../../../linters/mypy/type-annotations.md](../../../linters/mypy/type-annotations.md)

**Critical Requirements for Test Generation**:
- ✅ All local variables: `variable: Type = value`
- ✅ All function parameters: `param: Type`
- ✅ All return types: `-> ReturnType` (use `-> None` for test methods)
- ✅ Mock annotations: `mock_param: Mock`

**Common MyPy Test Errors to Prevent**:
```python
# ❌ FAILS MyPy
def test_function(self):
    provider_data = {...}  # Need type annotation
    
# ✅ PASSES MyPy
def test_function(self):
    provider_data: Dict[str, Any] = {...}
```

📊 COUNT-AND-DOCUMENT: MyPy standards reviewed: [YES/NO]
🛑 UPDATE-TABLE: Task 6.7 complete → Type annotation patterns memorized

## 🛤️ **PATH SELECTION**
-   **Unit**: Execute [unit-pre-generation.md](unit-pre-generation.md) (mock readiness)
-   **Integration**: Execute [integration-pre-generation.md](integration-pre-generation.md) (real API readiness)

**Execute all tasks 6.1-6.8 systematically.**

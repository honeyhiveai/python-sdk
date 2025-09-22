# Phase 4: Unit Usage Strategy

**🎯 Mock Usage Patterns for Complete Test Coverage in Unit Tests**

## 🚨 **ENTRY REQUIREMENTS**
🛑 VALIDATE-GATE: Unit Usage Strategy Prerequisites
- [ ] All shared analysis completed (Tasks 4.1-4.4) with evidence ✅/❌
- [ ] Unit test path selected and locked (no integration mixing) ✅/❌
- [ ] Usage patterns inventory complete ✅/❌
- [ ] Phase 4.4 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If integration path selected - cannot proceed with unit strategy

## 📋 **UNIT USAGE MOCK STRATEGY**

### **Function Call Mocking**
```python
# Mock chained method calls (from analysis)
@patch.object(SomeClass, 'method_chain')
def test_chained_calls(mock_chain):
    mock_chain.return_value.next_method.return_value = "expected_result"
    result = function_under_test()
    mock_chain.assert_called_once()

# Mock constructor calls (from analysis)
@patch('module.ClassName')
def test_constructor_calls(mock_class):
    mock_instance = Mock()
    mock_class.return_value = mock_instance
    mock_instance.method.return_value = "test_value"
```

### **Control Flow Testing**
```python
# Test all branches (from control flow analysis)
def test_conditional_branches(mock_tracer_base):
    mock_tracer_base.config.api_key = "valid-key"
    assert function_under_test(mock_tracer_base) is True
    
    mock_tracer_base.config.api_key = None
    assert function_under_test(mock_tracer_base) is False

# Test exception handling paths
@patch('module.risky_function')
def test_exception_handling(mock_risky):
    mock_risky.return_value = "success"
    assert function_under_test() == "success"
    
    mock_risky.side_effect = ValueError("test error")
    assert function_under_test() is None
```

### **State Change Verification**
```python
# Verify all state changes (from state management analysis)
def test_state_changes(mock_tracer_base):
    assert mock_tracer_base.initialized is False
    function_under_test(mock_tracer_base)
    assert mock_tracer_base.initialized is True
    assert mock_tracer_base.session_id is not None

# Test attribute assignments
def test_attribute_assignments(mock_tracer_base):
    mock_tracer_base.project_name = None
    function_under_test(mock_tracer_base, project="test-project")
    assert mock_tracer_base.project_name == "test-project"
```

## 📊 **MANDATORY EVIDENCE DOCUMENTATION**
📊 QUANTIFY-RESULTS: Function call mocking strategy: [DEFINED with strategy details]
📊 QUANTIFY-RESULTS: Control flow testing strategy: [DEFINED with strategy details]
📊 QUANTIFY-RESULTS: State verification strategy: [DEFINED with strategy details]
📊 QUANTIFY-RESULTS: Error path testing strategy: [DEFINED with strategy details]
⚠️ EVIDENCE-REQUIRED: Unit usage strategy documented with specific mock patterns

## 🛑 **VALIDATION GATE: UNIT USAGE STRATEGY COMPLETE**
🛑 VALIDATE-GATE: Unit Usage Strategy Evidence
- [ ] All usage patterns have mock strategy (count matches analysis) ✅/❌
- [ ] All branches covered in test design (mock configuration ready) ✅/❌
- [ ] All state changes verified (mock assertions planned) ✅/❌
- [ ] All error paths tested (exception mocking configured) ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without complete unit usage strategy
🛑 UPDATE-TABLE: Phase 4.5 → Unit usage strategy complete with evidence
🎯 NEXT-MANDATORY: [evidence-collection-framework.md](evidence-collection-framework.md)

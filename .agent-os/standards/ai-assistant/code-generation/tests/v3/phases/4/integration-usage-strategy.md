# Phase 4: Integration Usage Strategy

**🎯 Real Usage Validation for End-to-End Functionality Testing**

## 🚨 **ENTRY REQUIREMENTS**
🛑 VALIDATE-GATE: Integration Usage Strategy Prerequisites
- [ ] All shared analysis completed (Tasks 4.1-4.4) with evidence ✅/❌
- [ ] Integration test path selected and locked (no unit mixing) ✅/❌
- [ ] Usage patterns inventory complete ✅/❌
- [ ] Phase 4.4 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If unit path selected - cannot proceed with integration strategy

## 📋 **INTEGRATION USAGE STRATEGY**

### **Real Function Call Validation**
```python
# Use real function calls (no mocking)
def test_real_function_calls(
    honeyhive_tracer: HoneyHiveTracer,
    verify_backend_event
):
    tracer_instance = honeyhive_tracer.get_tracer("test-service")
    span = tracer_instance.start_span("test-operation")
    span.set_attribute("test.key", "test.value")
    span.end()
    
    verify_backend_event(
        tracer=honeyhive_tracer,
        expected_event_type="span",
        expected_data={
            "service_name": "test-service",
            "operation_name": "test-operation"
        }
    )
```

### **Real Control Flow Validation**
```python
# Test real branching behavior
def test_real_conditional_logic(honeyhive_tracer, verify_backend_event):
    if honeyhive_tracer.config.api_key:
        result = honeyhive_tracer.initialize()
        assert result is True
        
        verify_backend_event(
            tracer=honeyhive_tracer,
            expected_event_type="auth",
            expected_data={"authenticated": True}
        )
```

### **Real State Change Validation**
```python
# Verify real state changes
def test_real_state_management(honeyhive_tracer, verify_backend_event):
    assert honeyhive_tracer.initialized is False
    honeyhive_tracer.start_session("integration-test-session")
    assert honeyhive_tracer.initialized is True
    
    verify_backend_event(
        tracer=honeyhive_tracer,
        expected_event_type="session",
        expected_data={"session_id": honeyhive_tracer.session_id}
    )
```

## 📊 **MANDATORY EVIDENCE DOCUMENTATION**
📊 QUANTIFY-RESULTS: Real function validation strategy: [DEFINED with strategy details]
📊 QUANTIFY-RESULTS: Real control flow testing strategy: [DEFINED with strategy details]
📊 QUANTIFY-RESULTS: Real state verification strategy: [DEFINED with strategy details]
📊 QUANTIFY-RESULTS: Real error scenario testing: [DEFINED with strategy details]
⚠️ EVIDENCE-REQUIRED: Integration usage strategy documented with specific validation points

## 🛑 **VALIDATION GATE: INTEGRATION USAGE STRATEGY COMPLETE**
🛑 VALIDATE-GATE: Integration Usage Strategy Evidence
- [ ] All usage patterns use real implementations (no mocks - count matches analysis) ✅/❌
- [ ] All branches tested with real conditions (backend verification ready) ✅/❌
- [ ] All state changes verified with real data (real state validation planned) ✅/❌
- [ ] All error scenarios use real exceptions (real error handling tested) ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without complete integration usage strategy
🛑 UPDATE-TABLE: Phase 4.6 → Integration usage strategy complete with evidence
🎯 NEXT-MANDATORY: [evidence-collection-framework.md](evidence-collection-framework.md)
# Phase 2: Unit Logging Strategy

**🎯 Mock Configuration for Logging Verification in Unit Tests**

## 🚨 **ENTRY REQUIREMENTS**
🛑 VALIDATE-GATE: Unit Logging Strategy Prerequisites
- [ ] Level classification completed with evidence ✅/❌
- [ ] All logging patterns analyzed from Tasks 2.1-2.3 ✅/❌
- [ ] Unit test path selected and locked (no integration mixing) ✅/❌
- [ ] Phase 2.3 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If integration path selected - cannot proceed with unit strategy

## 🛑 **UNIT LOGGING MOCK STRATEGY DEFINITION**

⚠️ MUST-COMPLETE: Define complete logging mock strategy based on analysis
📊 COUNT-AND-DOCUMENT: Logging calls requiring mocks: [NUMBER from analysis]
📊 COUNT-AND-DOCUMENT: Log levels requiring verification: [NUMBER from classification]
📊 COUNT-AND-DOCUMENT: Safe_log patterns requiring mocks: [NUMBER from patterns]

## 📋 **UNIT LOGGING MOCK STRATEGY**

### **Using Analysis Results**
```python
# Based on logging analysis: Mock all logging calls
# Based on safe_log analysis: Use mock_safe_log fixture
# Based on level analysis: Verify correct levels called

def test_function(
    self,
    mock_tracer_base: Mock,
    mock_safe_log: Mock
) -> None:
    # Configure tracer for logging test
    mock_tracer_base.config.api_key = "test-key"
    
    # Execute function that logs
    result = function_under_test(mock_tracer_base)
    
    # Verify logging calls (based on level analysis)
    mock_safe_log.assert_any_call(
        mock_tracer_base,
        "info",  # From level classification
        "Expected message pattern"
    )
    
    # Verify call count matches analysis
    assert mock_safe_log.call_count == expected_count
```

### **Level-Specific Verification**
```python
# Verify debug logging
mock_safe_log.assert_any_call(mock_tracer, "debug", "Debug message")

# Verify info logging  
mock_safe_log.assert_any_call(mock_tracer, "info", "Info message")

# Verify error logging
mock_safe_log.assert_any_call(mock_tracer, "error", "Error message")

# Verify conditional logging paths
if error_condition:
    mock_safe_log.assert_any_call(mock_tracer, "error", "Error occurred")
else:
    mock_safe_log.assert_any_call(mock_tracer, "info", "Success message")
```

### **Mock Configuration**
```python
# Standard fixture usage (from Phase 1 fixture integration)
mock_safe_log: Mock  # From tests/unit/conftest.py

# Verification patterns
mock_safe_log.assert_called()  # At least one call
mock_safe_log.assert_not_called()  # No calls expected
mock_safe_log.call_count == expected_number  # Exact count
```

## 📊 **MANDATORY EVIDENCE DOCUMENTATION**
📊 QUANTIFY-RESULTS: Mock strategy defined: [YES/NO with strategy details]
📊 QUANTIFY-RESULTS: Level verification patterns: [YES/NO with pattern count]
📊 QUANTIFY-RESULTS: Standard fixtures integrated: [YES/NO with fixture list]
⚠️ EVIDENCE-REQUIRED: Unit logging strategy documented with specific verification counts

## 🛑 **VALIDATION GATE: UNIT LOGGING STRATEGY COMPLETE**
🛑 VALIDATE-GATE: Unit Logging Strategy Evidence
- [ ] Mock configuration strategy complete (count matches analysis) ✅/❌
- [ ] Level-specific verification patterns ready (all levels covered) ✅/❌
- [ ] Standard fixture integration confirmed (mock_safe_log usage) ✅/❌
- [ ] Complete isolation achieved (no real logging calls) ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without complete unit logging strategy
🛑 UPDATE-TABLE: Phase 2.4 → Unit logging strategy complete with evidence
🎯 NEXT-MANDATORY: [evidence-collection-framework.md](evidence-collection-framework.md)

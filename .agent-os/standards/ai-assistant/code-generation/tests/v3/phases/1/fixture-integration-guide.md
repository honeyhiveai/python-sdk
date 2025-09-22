# Phase 1: Fixture Integration Guide

**🎯 Standard Fixture Usage from conftest.py**

## 🚨 **ENTRY REQUIREMENTS**
🛑 VALIDATE-GATE: Fixture Integration Prerequisites
- [ ] Import mapping completed with evidence ✅/❌
- [ ] Dependency classification available with counts ✅/❌
- [ ] Phase 1.3 progress table updated ✅/❌

## 🛑 **FIXTURE DISCOVERY AND VALIDATION**

🛑 EXECUTE-NOW: Verify standard fixtures exist in conftest.py files
```bash
# MANDATORY: Execute all fixture verification commands
echo "=== UNIT FIXTURE VERIFICATION ==="
grep -n -E "(mock_tracer_base|mock_safe_log|mock_client|standard_mock_responses)" tests/unit/conftest.py

echo "--- Integration Fixture Verification ---"
grep -n -E "(honeyhive_tracer|verify_backend_event|cleanup_session)" tests/integration/conftest.py

echo "=== FIXTURE SUMMARY ==="
echo "Unit fixtures: $(grep -c -E '(mock_tracer_base|mock_safe_log|mock_client|standard_mock_responses)' tests/unit/conftest.py)"
echo "Integration fixtures: $(grep -c -E '(honeyhive_tracer|verify_backend_event|cleanup_session)' tests/integration/conftest.py)"
```

🛑 PASTE-OUTPUT: Complete fixture verification results below

## 📋 **STANDARD FIXTURES**

### **Unit Test Fixtures** (tests/unit/conftest.py)
```python
# Core unit fixtures
mock_tracer_base: Mock           # Complete mock tracer with attributes
mock_safe_log: Mock             # Standard logging mock
mock_client: Mock               # API client mock
standard_mock_responses: Dict    # Predefined response patterns

# Configuration fixtures
api_key: str                    # Test API key
project: str                    # Test project name
source: str                     # Test source identifier
```

### **Integration Test Fixtures** (tests/integration/conftest.py)
```python
# Core integration fixtures
honeyhive_tracer: HoneyHiveTracer    # Real tracer instance
verify_backend_event                 # Backend verification utility
cleanup_session                      # Session cleanup
```

## 🔧 **USAGE PATTERNS**

### **Unit Test Pattern**
```python
def test_function(
    self,
    mock_tracer_base: Mock,
    mock_safe_log: Mock,
    standard_mock_responses: Dict
) -> None:
    # Configure mocks
    mock_tracer_base.config.api_key = "test-key"
    mock_tracer_base._initialized = False
    
    # Execute test
    result = function_under_test(mock_tracer_base)
    
    # Verify behavior
    assert result is not None
    mock_safe_log.assert_called()
```

### **Integration Test Pattern**
```python
def test_function(
    self,
    honeyhive_tracer: HoneyHiveTracer,
    verify_backend_event
) -> None:
    # Execute with real tracer
    result = function_under_test(honeyhive_tracer)
    
    # Verify backend
    verify_backend_event(
        tracer=honeyhive_tracer,
        expected_event_type="model"
    )
```

## 📊 **MANDATORY EVIDENCE DOCUMENTATION**
📊 COUNT-AND-DOCUMENT: Unit fixtures available: [EXACT NUMBER]
📊 COUNT-AND-DOCUMENT: Integration fixtures available: [EXACT NUMBER]
📊 QUANTIFY-RESULTS: Standard patterns verified: [YES/NO with evidence]
⚠️ EVIDENCE-REQUIRED: Complete fixture verification output pasted above

## 🛑 **VALIDATION GATE: FIXTURE INTEGRATION COMPLETE**
🛑 VALIDATE-GATE: Fixture Integration Evidence
- [ ] Standard fixtures identified and documented with line numbers ✅/❌
- [ ] Usage patterns provided with complete examples ✅/❌
- [ ] Mock configuration examples ready for both paths ✅/❌
- [ ] Fixture availability verified with command output ✅/❌
- [ ] Exact counts documented for all fixture types ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without complete fixture evidence
🛑 UPDATE-TABLE: Phase 1.4 → Fixture integration complete with evidence
🎯 NEXT-MANDATORY: [unit-mock-strategy.md](unit-mock-strategy.md)

# Fixture Patterns - conftest.py Integration Guide

**🎯 AI Guide for Using Standard Fixtures from conftest.py Files**

⚠️ MUST-READ: Complete fixture patterns before test generation
🛑 VALIDATE-GATE: Fixture Pattern Understanding
- [ ] Unit test fixtures identified and understood ✅/❌
- [ ] Integration test fixtures identified and understood ✅/❌
- [ ] Fixture selection strategy comprehended ✅/❌
- [ ] Path-specific fixture usage accepted ✅/❌

🚨 FRAMEWORK-VIOLATION: If mixing unit and integration fixtures

## 🛑 **FIXTURE DISCOVERY AND VERIFICATION**

🛑 EXECUTE-NOW: Verify all standard fixtures exist
```bash
# MANDATORY: Verify fixture availability
echo "=== UNIT FIXTURE VERIFICATION ==="
grep -n -E "(mock_tracer_base|mock_safe_log|mock_client|standard_mock_responses)" tests/unit/conftest.py

echo "--- Integration Fixture Verification ---"
grep -n -E "(honeyhive_tracer|verify_backend_event|cleanup_session)" tests/integration/conftest.py

echo "=== FIXTURE SUMMARY ==="
echo "Unit fixtures: $(grep -c -E '(mock_tracer_base|mock_safe_log|mock_client|standard_mock_responses)' tests/unit/conftest.py)"
echo "Integration fixtures: $(grep -c -E '(honeyhive_tracer|verify_backend_event|cleanup_session)' tests/integration/conftest.py)"
```

🛑 PASTE-OUTPUT: Complete fixture verification results below

## 📋 **FIXTURE DISCOVERY**

### **Unit Test Fixtures** (tests/unit/conftest.py)
```python
# Core fixtures for unit testing
mock_tracer_base: Mock           # Complete mock tracer with all attributes
mock_safe_log: Mock             # Standard logging mock for safe_log utility  
mock_client: Mock               # API client mock with standard responses
standard_mock_responses: Dict    # Predefined response patterns

# Configuration fixtures
api_key: str                    # Test API key
project: str                    # Test project name
source: str                     # Test source identifier
```

### **Integration Test Fixtures** (tests/integration/conftest.py)
```python
# Core fixtures for integration testing
honeyhive_tracer: HoneyHiveTracer    # Real tracer instance for end-to-end testing
verify_backend_event                 # Backend verification utility
cleanup_session                      # Session cleanup and teardown
```

## 🔧 **UNIT TEST FIXTURE USAGE**

### **mock_tracer_base Pattern**
```python
def test_function(self, mock_tracer_base: Mock, mock_safe_log: Mock) -> None:
    """Test using complete mock tracer with all required attributes."""
    # Setup mock tracer state
    mock_tracer_base.project_name = "test-project"
    mock_tracer_base.source_environment = "test"
    mock_tracer_base.test_mode = True
    mock_tracer_base._initialized = False
    mock_tracer_base.session_id = "test-session-123"
    mock_tracer_base.is_main_provider = False
    
    # Configure nested mock objects
    mock_tracer_base.config.server_url = "https://api.honeyhive.ai"
    mock_tracer_base.config.api_key = "test-api-key"
    
    # Execute function under test
    result = function_under_test(mock_tracer_base)
    
    # Verify behavior
    assert result is not None
    mock_safe_log.assert_any_call(mock_tracer_base, "info", "Expected message")
```

### **standard_mock_responses Pattern**
```python
def test_api_integration(
    self, 
    mock_client: Mock, 
    standard_mock_responses: Dict
) -> None:
    """Test API integration using standard response patterns."""
    # Configure mock client with standard responses
    mock_client.post.return_value = standard_mock_responses["session"]
    mock_client.get.return_value = standard_mock_responses["event"]
    
    # Execute function
    result = api_function(mock_client)
    
    # Verify API interactions
    mock_client.post.assert_called_once()
    assert result["session_id"] == "session-test-123"
```

### **Configuration Fixture Pattern**
```python
def test_with_configuration(
    self,
    api_key: str,
    project: str, 
    source: str,
    mock_tracer_base: Mock
) -> None:
    """Test using standard configuration fixtures."""
    # Use standard configuration values
    mock_tracer_base.config.api_key = api_key
    mock_tracer_base.project_name = project
    mock_tracer_base.source_environment = source
    
    # Test configuration handling
    result = configure_tracer(mock_tracer_base)
    assert result.api_key == "test-api-key-12345"
    assert result.project == "test-project"
```

## 🔗 **INTEGRATION TEST FIXTURE USAGE**

### **honeyhive_tracer Pattern**
```python
def test_real_functionality(
    self,
    honeyhive_tracer: HoneyHiveTracer,
    verify_backend_event
) -> None:
    """Test with real tracer instance and backend verification."""
    # Use real tracer (no mocking)
    result = real_function(honeyhive_tracer)
    
    # Verify real behavior
    assert honeyhive_tracer._initialized is True
    assert honeyhive_tracer.session_id is not None
    
    # Verify backend state
    verify_backend_event(
        tracer=honeyhive_tracer,
        expected_event_type="model",
        expected_data={"project": honeyhive_tracer.project_name}
    )
```

### **verify_backend_event Pattern**
```python
def test_backend_integration(
    self,
    honeyhive_tracer: HoneyHiveTracer,
    verify_backend_event
) -> None:
    """Test backend integration with event verification."""
    # Execute function that creates events
    with honeyhive_tracer.start_span("test_operation") as span:
        span.set_attribute("test_key", "test_value")
        result = process_data("test input")
    
    # Verify event appears in backend
    verify_backend_event(
        tracer=honeyhive_tracer,
        expected_event_type="model",
        expected_data={
            "inputs": {"data": "test input"},
            "outputs": {"result": result},
            "metadata": {"test_key": "test_value"}
        },
        timeout=30
    )
```

## 🛑 **MANDATORY FIXTURE SELECTION**

🛑 VALIDATE-GATE: Fixture Selection Based on Test Path
- [ ] Test path confirmed (unit OR integration) ✅/❌
- [ ] Appropriate fixtures selected for path ✅/❌
- [ ] No fixture mixing between paths ✅/❌

### **Unit Tests (Mock Everything)**
🛑 EXECUTE-NOW: Use these fixtures for unit tests ONLY
```python
# MANDATORY: Always use these fixtures for unit tests
@pytest.fixture
def test_unit_function(
    self,
    mock_tracer_base: Mock,      # ✅ Complete mock tracer
    mock_safe_log: Mock,         # ✅ Logging mock
    mock_client: Mock,           # ✅ API client mock
    standard_mock_responses: Dict # ✅ Standard responses
) -> None:
```
🚨 FRAMEWORK-VIOLATION: If using real fixtures in unit tests

### **Integration Tests (Real APIs)**
🛑 EXECUTE-NOW: Use these fixtures for integration tests ONLY
```python
# MANDATORY: Always use these fixtures for integration tests  
@pytest.fixture
def test_integration_function(
    self,
    honeyhive_tracer: HoneyHiveTracer, # ✅ Real tracer
    verify_backend_event,              # ✅ Backend verification
    cleanup_session                    # ✅ Cleanup handling
) -> None:
```
🚨 FRAMEWORK-VIOLATION: If using mock fixtures in integration tests

## 🛑 **MANDATORY FIXTURE COMPLIANCE**

🛑 VALIDATE-GATE: Fixture Usage Compliance
- [ ] Standard fixtures used (no custom mocks created) ✅/❌
- [ ] Path strategy followed (no fixture mixing) ✅/❌
- [ ] Proper configuration applied ✅/❌
- [ ] Cleanup handling implemented ✅/❌

### **Must Use Standard Fixtures**
📊 COUNT-AND-DOCUMENT: Standard fixtures used: [NUMBER]
- ✅ **Never create custom mocks** when standard fixtures exist
- ✅ **Use mock_tracer_base** instead of Mock() for tracers
- ✅ **Use standard_mock_responses** for API responses
- ✅ **Use honeyhive_tracer** for real integration tests
⚠️ EVIDENCE-REQUIRED: All fixtures must be from conftest.py

### **Must Follow Path Strategy**
🛑 VALIDATE-GATE: Path Strategy Adherence
- ✅ **Unit tests**: Use mock fixtures only (complete isolation)
- ✅ **Integration tests**: Use real fixtures only (end-to-end validation)
- ❌ **Never mix**: Don't use real fixtures in unit tests or mocks in integration
🚨 FRAMEWORK-VIOLATION: If path strategy violated

### **Must Configure Properly**
📊 QUANTIFY-RESULTS: Fixture configuration completeness: [PERCENTAGE]
- ✅ **Set required attributes** on mock fixtures before use
- ✅ **Configure return values** for mock methods appropriately
- ✅ **Use test_mode=True** for real fixtures in integration tests
- ✅ **Handle cleanup** with provided cleanup fixtures

🛑 UPDATE-TABLE: Fixture patterns applied with compliance validation
🎯 NEXT-MANDATORY: Apply fixture patterns in test generation

---

**🎯 This guide ensures generated tests use appropriate standard fixtures and follow established patterns with mandatory compliance validation.**

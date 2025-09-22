# Unit Test Path - MOCK EXTERNAL DEPENDENCIES Strategy

## 🎯 **UNIT TEST PHILOSOPHY: COMPLETE ISOLATION**

🛑 VALIDATE-GATE: Unit Path Entry Requirements
- [ ] Mock external dependencies strategy commitment confirmed ✅/❌
- [ ] Complete isolation objective understood ✅/❌
- [ ] V2 mocking failure lessons reviewed (22% pass rate) ✅/❌

🚨 FRAMEWORK-VIOLATION: If using real APIs/services in unit tests or mixing with integration strategies

**Core Principle**: Mock ALL external dependencies while executing production code for coverage  
**Success Metric**: 80%+ pass rate + 90%+ coverage through systematic mocking  
**V2 Failure**: Incomplete mocking caused 22% pass rate  
**V3 Solution**: Systematic "mock external dependencies" approach (Archive-based)  

---

## 🛑 **MANDATORY MOCKING STRATEGY EXECUTION**

⚠️ MUST-READ: Unit tests MUST mock external dependencies - execute production code for coverage

### **🔒 MOCK EXTERNAL DEPENDENCIES CHECKLIST**

**✅ EXTERNAL LIBRARIES (100% Mock Rate)**
```python
# ALL external library calls MUST be mocked
@patch('requests.post')
@patch('requests.get')
@patch('os.getenv')
@patch('sys.exit')
@patch('time.sleep')
@patch('json.loads')
@patch('uuid.uuid4')
# ... EVERY external library call
```

**✅ OTHER INTERNAL MODULES (Selective Mock Rate)**
```python
# Mock OTHER internal modules (NOT the module under test)
@patch('honeyhive.api.client.HoneyHive')
@patch('honeyhive.api.session.SessionAPI')
@patch('honeyhive.utils.logger.safe_log')  # Only if NOT testing utils.logger
@patch('honeyhive.utils.logger.get_tracer_logger')  # Only if NOT testing utils.logger
@patch('honeyhive.tracer.processing.otlp_exporter.HoneyHiveOTLPExporter')  # Only if NOT testing this module
# Mock dependencies, NOT the code under test
```

**🚨 CRITICAL: DO NOT MOCK THE CODE UNDER TEST**
```python
# ❌ WRONG - This kills coverage and violates unit test principles
@patch('honeyhive.tracer.instrumentation.initialization.initialize_tracer_instance')
def test_initialize_tracer_instance(mock_init):
    # This mocks the function we're trying to test - 0% coverage!
    
# ✅ CORRECT - Mock dependencies, test the real function
@patch('honeyhive.tracer.instrumentation.initialization.safe_log')
@patch('honeyhive.tracer.instrumentation.initialization.HoneyHiveOTLPExporter')
def test_initialize_tracer_instance(mock_exporter, mock_log):
    # This tests the REAL function with mocked dependencies - achieves coverage!
    from honeyhive.tracer.instrumentation.initialization import initialize_tracer_instance
    result = initialize_tracer_instance(mock_tracer_base)  # Real function execution
```

**✅ CONFIGURATION & ENVIRONMENT (100% Mock Rate)**
```python
# ALL configuration access MUST be mocked
@patch.dict('os.environ', {'HH_API_KEY': 'test-key'})
@patch('honeyhive.config.get_config')
# Mock tracer.config object completely
mock_tracer.config = Mock()
mock_tracer.config.api_key = "test-key"
mock_tracer.config.server_url = "https://test.api.com"
```

**✅ LOGGING & OUTPUT (100% Mock Rate)**
```python
# ALL logging MUST be mocked and verified
@patch('honeyhive.tracer.instrumentation.initialization.safe_log')
def test_function(mock_safe_log):
    # Test function
    function_under_test()
    
    # Verify logging calls
    mock_safe_log.assert_called_with(
        mock_tracer, 'info', 'Expected message', {'key': 'value'}
    )
```

---

## 🧪 **UNIT TEST MOCK PATTERNS**

### **🎭 Complete Mock Object Pattern**
```python
class MockHoneyHiveTracer:
    """Complete mock with ALL attributes from Phase 1 analysis."""
    
    def __init__(self):
        # CRITICAL: Include ALL attributes found in Phase 1
        self.config = Mock()
        self.config.api_key = "test-key"
        self.config.server_url = "https://test.api.com"
        self.config.otlp_enabled = True
        
        self.is_main_provider = False
        self.project_name = "test-project"
        self.api_key = "test-key"
        self.verbose = False
        self.session_id = "test-session-id"
        self.test_mode = True
        
        # Internal state attributes
        self._initialized = False
        self._tracer_id = None
        self._tracer_provider = None
        self._tracer = None
        self._span_processor = None
        self._otlp_exporter = None
        self._session_config = None
        self._client = None
        self._session_api = None
        
        # Mock methods
        self.start_span = Mock()
        self.create_event = Mock()
        self.flush = Mock()
```

### **🔧 Function Signature Mocking**
```python
# CRITICAL: Mock with correct signatures from Phase 1 analysis
@patch('honeyhive.tracer.instrumentation.initialization.get_tracer_logger')
def test_logger_function(mock_get_logger):
    # V2 FAILED: Expected 1 parameter, actual needs 2
    # V3 SUCCESS: Correct signature from Phase 1 analysis
    mock_get_logger.return_value = Mock()
    
    result = _get_logger_for_tracer(mock_tracer)
    
    # CORRECT: Two parameters as discovered in Phase 1
    mock_get_logger.assert_called_once_with(
        mock_tracer, 
        "honeyhive.tracer.initialization"
    )
```

### **🏗️ Provider Info Mock Pattern**
```python
@pytest.fixture
def mock_provider_info():
    """Complete provider info with ALL required keys from Phase 1."""
    return {
        'provider': Mock(),
        'provider_class_name': 'TracerProvider',
        'provider_instance': Mock(),
        'detection_method': 'atomic',
        'is_global': True,
        'provider_id': 'test-provider-id',
        # Add ALL keys discovered in Phase 1 analysis
    }
```

---

## 🚨 **UNIT TEST ISOLATION REQUIREMENTS**

### **🔒 NO REAL EXTERNAL CALLS**
```python
# ❌ FORBIDDEN in unit tests
requests.post("https://api.honeyhive.ai/events")  # Real API call
os.getenv("HH_API_KEY")  # Real environment access
open("/path/to/file")  # Real file system access

# ✅ REQUIRED in unit tests  
@patch('requests.post')
@patch.dict('os.environ', {'HH_API_KEY': 'test'})
@patch('builtins.open', mock_open(read_data="test"))
```

### **🧹 Clean Test Isolation**
```python
def test_isolated_function():
    """Each test completely independent."""
    # Fresh mock objects for each test
    mock_tracer = MockHoneyHiveTracer()
    
    # Test function in isolation
    result = function_under_test(mock_tracer)
    
    # Verify behavior without side effects
    assert result.expected_value == "expected"
    
    # No cleanup needed - mocks auto-cleanup
```

---

## 📊 **UNIT TEST COVERAGE REQUIREMENTS**

### **🎯 Coverage Targets**
- **Line Coverage**: 90%+ (non-negotiable)
- **Branch Coverage**: 85%+ (all if/else paths)
- **Function Coverage**: 100% (every function tested)
- **Mock Coverage**: 100% (every external dependency mocked)

### **🚨 CRITICAL: How Coverage Works with Mocking**
```python
# ✅ CORRECT - Achieves 90%+ coverage
@patch('honeyhive.tracer.instrumentation.initialization.safe_log')
def test_initialize_tracer_instance(mock_log):
    # Import and execute the REAL production code
    from honeyhive.tracer.instrumentation.initialization import initialize_tracer_instance
    
    # This executes the actual production code lines → Coverage!
    result = initialize_tracer_instance(mock_tracer_base)
    
    # The production code runs with mocked dependencies
    # Coverage tool sees the real code execution
    assert result is not None

# ❌ WRONG - Achieves 0% coverage  
@patch('honeyhive.tracer.instrumentation.initialization.initialize_tracer_instance')
def test_initialize_tracer_instance(mock_init):
    # This mocks the function itself → No real code execution → 0% coverage!
    mock_init.return_value = Mock()
    result = mock_init(mock_tracer_base)
```

**Key Insight**: Mock the dependencies, execute the production code!

### **🌟 Edge Case Testing**
```python
def test_edge_cases():
    """Test boundary conditions and error paths."""
    # None inputs
    result = function_under_test(None)
    assert result is None
    
    # Empty collections
    result = function_under_test([])
    assert result == []
    
    # Exception scenarios
    with patch('external_call', side_effect=Exception("Test error")):
        result = function_under_test(mock_tracer)
        assert result is None  # Graceful degradation
```

---

## 🛡️ **UNIT TEST QUALITY GATES**

### **🚨 Pre-Generation Validation**
Before generating unit tests, verify:
- [ ] All external dependencies identified for mocking
- [ ] All function signatures extracted with parameter counts
- [ ] All attribute access patterns documented
- [ ] Mock object completeness requirements defined
- [ ] No real API calls planned

### **📋 Post-Generation Validation**
After generating unit tests, verify:
- [ ] 90%+ line coverage achieved
- [ ] All external calls are mocked
- [ ] No real API endpoints contacted
- [ ] All mock assertions include expected parameters
- [ ] Edge cases and error paths tested

---

## 🔄 **UNIT PATH PHASE INTEGRATION**

### **Phase 1: Method Verification → Unit Mocking**
- Use AST analysis to identify ALL functions requiring mocks
- Extract exact signatures for mock configuration
- Document ALL attributes for complete mock objects

### **Phase 2: Logging Analysis → Mock Logging**
- Mock ALL safe_log calls with verification
- Mock ALL logger instances
- Verify log messages and levels in tests

### **Phase 3: Dependency Analysis → Mock Dependencies**
- Mock ALL external libraries (requests, os, sys, etc.)
- Mock ALL internal modules (honeyhive.*)
- Mock ALL configuration access

### **Phase 4: Usage Patterns → Mock Patterns**
- Use call patterns to configure mock return values
- Mock ALL function calls with correct signatures
- Verify ALL mock interactions

---

## ✅ **UNIT TEST SUCCESS CRITERIA**

**Unit tests are successful when:**
1. ✅ 90%+ line coverage achieved
2. ✅ All external dependencies mocked
3. ✅ No real API calls made
4. ✅ All function signatures correctly mocked
5. ✅ Complete mock objects with all required attributes
6. ✅ Edge cases and error paths tested
7. ✅ Tests run in complete isolation

**Unit test failure indicators:**
- Real API calls detected
- Missing mock attributes causing AttributeError
- Wrong function signatures causing parameter mismatches
- Low coverage due to incomplete mocking

---

## 🎯 **UNIT PATH ENFORCEMENT**

**When unit path is chosen:**
- ALL external dependencies MUST be mocked
- NO real API calls allowed
- Complete isolation required
- Mock completeness validated
- 90%+ coverage target enforced

**Path violation detection:**
- Real HTTP requests detected → VIOLATION
- Real file system access → VIOLATION  
- Real environment variable access → VIOLATION
- Incomplete mock objects → VIOLATION

**Success metric**: 80%+ first-run pass rate through comprehensive mocking strategy.

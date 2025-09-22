# Phase 3: Dependency Analysis - Complete Mocking Strategy Restoration

## 🎯 **CRITICAL PHASE: DEPENDENCY MAPPING FOR TEST ISOLATION**

**Purpose**: Comprehensive dependency analysis to prevent test failures through complete mocking/real API strategy  
**Archive Success**: Detailed dependency mapping enabled complete test isolation  
**V2 Failure**: Generic import listing missed critical mocking requirements  
**V3 Restoration**: Archive depth + path-specific dependency strategies  

---

## 🚨 **MANDATORY DEPENDENCY ANALYSIS COMMANDS**

### **1. Complete Import Inventory**
```bash
# Extract ALL imports (everything to potentially mock)
grep -E "^import |^from " [PRODUCTION_FILE]
# Expected: Complete list of all dependencies

# Alternative comprehensive import detection
grep -E "^[[:space:]]*import |^[[:space:]]*from " [PRODUCTION_FILE]
# Catches indented imports in functions/classes
```

### **2. External Library Usage Detection**
```bash
# Find external library method calls (primary mock targets)
grep -E "requests\.|urllib\.|json\.|os\.|sys\.|time\.|uuid\.|platform\." [PRODUCTION_FILE]
# Expected: All external library method calls

# OpenTelemetry specific patterns (common in tracing code)
grep -E "opentelemetry\.|TracerProvider\.|SpanProcessor\.|Resource\." [PRODUCTION_FILE]

# Python standard library patterns
grep -E "threading\.|weakref\.|inspect\.|ast\." [PRODUCTION_FILE]
```

### **3. Internal Project Dependencies**
```bash
# Identify internal project imports (mock for isolation)
grep -E "from honeyhive|import honeyhive" [PRODUCTION_FILE]
# Expected: Internal dependencies that need mocking

# Find relative imports within project
grep -E "from \.|from \.\." [PRODUCTION_FILE]

# Find specific internal module usage
grep -E "\.api\.|\.utils\.|\.tracer\.|\.config\." [PRODUCTION_FILE]
```

### **4. Configuration and Environment Dependencies**
```bash
# Find configuration dependencies (mock for test control)
grep -E "config\.|settings\.|env\.|getenv|environ" [PRODUCTION_FILE]
# Expected: Configuration and environment dependencies

# Find environment variable access
grep -E "os\.getenv|os\.environ|getenv" [PRODUCTION_FILE]

# Find configuration object access
grep -E "\.config\.|Config\(|TracerConfig" [PRODUCTION_FILE]
```

---

## 📊 **COMPREHENSIVE DEPENDENCY REQUIREMENTS**

### **🔍 MUST DOCUMENT FOR TEST STRATEGY**

**DEPENDENCY INVENTORY:**
- **Standard Library Modules** (os, sys, json, uuid, threading, etc.)
- **Third-Party Libraries** (requests, opentelemetry, pydantic, etc.)
- **Internal Project Modules** (honeyhive.api, honeyhive.utils, etc.)
- **Configuration Dependencies** (config objects, environment variables)
- **Dynamic Imports** (importlib usage, getattr patterns)

**DEPENDENCY USAGE ANALYSIS:**
- **Method Calls** (requests.post, os.getenv, etc.)
- **Class Instantiation** (TracerProvider(), HoneyHive(), etc.)
- **Attribute Access** (config.api_key, os.environ, etc.)
- **Context Managers** (with statements using dependencies)

---

## 🛤️ **PATH-SPECIFIC DEPENDENCY STRATEGIES**

### **🧪 UNIT TEST PATH: COMPREHENSIVE DEPENDENCY MOCKING**

**Mock Strategy Requirements:**
```python
# Mock ALL external dependencies for complete isolation
@patch('honeyhive.tracer.instrumentation.initialization.HoneyHive')
@patch('honeyhive.tracer.instrumentation.initialization.SessionAPI')
@patch('honeyhive.tracer.instrumentation.initialization.TracerProvider')
@patch('honeyhive.tracer.instrumentation.initialization.Resource')
@patch('honeyhive.tracer.instrumentation.initialization.safe_log')
@patch('honeyhive.tracer.instrumentation.initialization.get_tracer_logger')
@patch('os.getenv')
@patch('uuid.uuid4')
def test_function_with_complete_mocking(
    mock_uuid, mock_getenv, mock_get_logger, mock_safe_log,
    mock_resource, mock_tracer_provider, mock_session_api, mock_honeyhive
):
    """Test with comprehensive dependency mocking."""
    
    # Configure all mocks with expected return values
    mock_getenv.return_value = "test-api-key"
    mock_uuid.return_value.hex = "test-session-id"
    mock_honeyhive.return_value = Mock()
    mock_session_api.return_value = Mock()
    
    # Execute function in complete isolation
    result = function_under_test(mock_tracer)
    
    # Verify all dependencies were called correctly
    mock_honeyhive.assert_called_once_with(api_key="test-api-key")
    mock_session_api.assert_called_once_with(mock_honeyhive.return_value)
```

**Internal Module Mocking Patterns:**
```python
# Mock internal honeyhive modules for isolation
@patch('honeyhive.api.client.HoneyHive')
@patch('honeyhive.api.session.SessionAPI')
@patch('honeyhive.utils.logger.safe_log')
@patch('honeyhive.tracer.processing.otlp_exporter.HoneyHiveOTLPExporter')
@patch('honeyhive.tracer.processing.span_processor.HoneyHiveSpanProcessor')
def test_internal_module_isolation(
    mock_span_processor, mock_otlp_exporter, mock_safe_log, 
    mock_session_api, mock_honeyhive
):
    """Test with all internal modules mocked."""
    
    # Configure internal module mocks
    mock_otlp_exporter.return_value = Mock()
    mock_span_processor.return_value = Mock()
    
    # Test function with complete internal isolation
    result = function_under_test(mock_tracer)
    
    # Verify internal module interactions
    mock_otlp_exporter.assert_called_once()
    mock_span_processor.assert_called_once()
```

**Configuration Mocking Patterns:**
```python
# Mock configuration dependencies for test control
@patch.dict('os.environ', {
    'HH_API_KEY': 'test-key',
    'HH_PROJECT': 'test-project',
    'HH_VERBOSE': 'true'
})
@patch('honeyhive.config.get_config')
def test_configuration_mocking(mock_get_config):
    """Test with configuration dependencies mocked."""
    
    # Mock configuration object
    mock_config = Mock()
    mock_config.api_key = "test-key"
    mock_config.project = "test-project"
    mock_config.verbose = True
    mock_get_config.return_value = mock_config
    
    # Test with controlled configuration
    result = function_under_test(mock_tracer)
    
    # Verify configuration usage
    mock_get_config.assert_called_once()
```

### **🔗 INTEGRATION TEST PATH: REAL DEPENDENCY USAGE**

**Real Dependency Strategy Requirements:**
```python
import os
import tempfile
from honeyhive import HoneyHive
from honeyhive.api.session import SessionAPI

class TestRealDependencies(TestCase):
    """Integration tests with real dependency usage."""
    
    def setUp(self):
        """Setup real test environment."""
        # Use real environment variables
        self.api_key = os.getenv("HH_TEST_API_KEY")
        if not self.api_key:
            self.skipTest("HH_TEST_API_KEY required for integration tests")
        
        # Use real HoneyHive client
        self.client = HoneyHive(api_key=self.api_key)
        self.session_api = SessionAPI(self.client)
    
    def test_real_dependency_integration(self):
        """Test with real external dependencies."""
        # Real tracer initialization
        tracer = HoneyHiveTracer(
            api_key=self.api_key,
            project="integration-test-project"
        )
        
        # Real initialization process
        initialize_tracer_instance(tracer)
        
        # Verify real initialization succeeded
        self.assertTrue(tracer._initialized)
        self.assertIsNotNone(tracer._client)
        self.assertIsNotNone(tracer._session_api)
    
    def test_real_configuration_loading(self):
        """Test real configuration with environment."""
        # Real environment configuration
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            
            # Real file operations
            with open(config_file, 'w') as f:
                json.dump({
                    "api_key": self.api_key,
                    "project": "integration-test",
                    "verbose": True
                }, f)
            
            # Real configuration loading
            config = load_config_from_file(config_file)
            
            # Verify real configuration
            self.assertEqual(config.api_key, self.api_key)
            self.assertEqual(config.project, "integration-test")
```

---

## 🚨 **CRITICAL DEPENDENCY FAILURE PREVENTION**

### **V2 Failures That V3 MUST Prevent:**

1. **Incomplete Dependency Mocking** (caused AttributeError):
   ```python
   # V2 FAILED: Missed mocking internal dependencies
   # Result: AttributeError when accessing unmocked modules
   
   # V3 PREVENTS: Comprehensive dependency inventory and mocking
   @patch('honeyhive.api.client.HoneyHive')  # All internal deps mocked
   @patch('honeyhive.utils.logger.safe_log')
   ```

2. **Missing Configuration Mocking** (caused environment errors):
   ```python
   # V2 FAILED: Didn't mock environment variable access
   # Result: Tests failed when HH_API_KEY not set
   
   # V3 PREVENTS: Complete configuration mocking strategy
   @patch.dict('os.environ', {'HH_API_KEY': 'test-key'})
   ```

3. **Wrong Mock Configurations** (caused unexpected behavior):
   ```python
   # V2 FAILED: Mocks returned None instead of expected objects
   # Result: Tests failed with "NoneType has no attribute" errors
   
   # V3 PREVENTS: Proper mock return value configuration
   mock_client.return_value = Mock()  # Proper mock objects
   mock_session_api.return_value = Mock()
   ```

---

## 📋 **MANDATORY PHASE 3 COMPLETION EVIDENCE**

### **🛑 CRITICAL: Progress Table Update Required**

**You MUST update the progress table in chat window before proceeding to Phase 4.**

**Required Evidence Format:**
```
| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 3: Dependency Analysis | ✅ | Analyzed X external deps (requests, os, uuid), Y internal imports (honeyhive.api, honeyhive.utils), Z config deps identified | 4/4 | Manual | ✅ |
```

### **🚨 ENFORCEMENT PATTERNS**

**❌ VIOLATION INDICATORS:**
- "Phase 3 complete" without showing updated table
- "Moving to Phase 4" without table update
- "Dependencies analyzed" without specific counts and names
- "Mocking strategy complete" without evidence

**🛑 VIOLATION RESPONSE:**
"STOP - You completed Phase 3 but didn't update the progress table. Show me the updated table in the chat window with Phase 3 marked as ✅ and evidence documented (external deps count, internal imports list, config dependencies) before proceeding to Phase 4."

---

## 🎯 **DEPENDENCY ANALYSIS SUCCESS CRITERIA**

**Phase 3 is complete ONLY when:**
1. ✅ All external dependencies identified and categorized
2. ✅ All internal project imports documented
3. ✅ All configuration dependencies mapped
4. ✅ Complete mocking strategy planned (unit) OR real dependency strategy (integration)
5. ✅ Mock return values and configurations specified
6. ✅ Path-specific strategy determined
7. ✅ Progress table updated with specific evidence

**Failure to complete Phase 3 properly WILL cause dependency-related test failures.**

---

## 🔄 **INTEGRATION WITH OTHER PHASES**

### **Phase 2 → Phase 3 Integration**
- Logging dependencies (safe_log, get_tracer_logger) become part of mocking strategy
- Logging configuration dependencies identified

### **Phase 3 → Phase 4 Integration**
- Dependency usage patterns inform how to mock function calls
- Mock configurations determine expected parameters and return values

### **Phase 3 → Test Generation Integration**
- Unit tests: All dependencies mocked with proper configurations
- Integration tests: Real dependencies with proper setup and cleanup
- Mock strategies applied consistently across all test methods

---

## ✅ **PHASE 3 SUCCESS VALIDATION**

**Dependency analysis is successful when:**
1. ✅ Complete inventory of all dependencies (external, internal, config)
2. ✅ Path-specific strategy determined (mock all vs real APIs)
3. ✅ Mock configurations planned with proper return values
4. ✅ Dependency isolation strategy documented
5. ✅ Integration requirements identified (real API setup)
6. ✅ Progress table shows Phase 3 ✅ with evidence

**Next Phase**: Only proceed to [Phase 4: Usage Patterns](phase-4-usage-patterns.md) after progress table update with evidence.

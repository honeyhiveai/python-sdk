# Phase 4: Usage Patterns - Deep Call Pattern Analysis Restoration

## 🎯 **CRITICAL PHASE: USAGE PATTERN UNDERSTANDING FOR REALISTIC TESTS**

**Purpose**: Deep usage pattern analysis to create realistic test scenarios and proper mock configurations  
**Archive Success**: Understanding real usage patterns enabled realistic isolated testing  
**V2 Failure**: Shallow usage analysis missed critical call patterns and parameter combinations  
**V3 Restoration**: Archive depth + path-specific usage analysis  

---

## 🚨 **MANDATORY USAGE PATTERN ANALYSIS COMMANDS**

### **1. Module Usage Discovery**
```bash
# Find how this module is imported and used elsewhere
grep -r "from.*initialization\|import.*initialization" src/ --include="*.py"
# Expected: How this module is imported and used elsewhere

# Find specific function imports
grep -r "from.*initialization import" src/ --include="*.py"

# Find wildcard imports (potential issues)
grep -r "from.*initialization import \*" src/ --include="*.py"
```

### **2. Function Call Pattern Analysis**
```bash
# Find instantiation patterns (for constructor testing)
grep -r "initialize_tracer_instance(" src/ --include="*.py" | head -10
# Expected: How main functions are called in practice

# Find method call patterns with context
grep -B2 -A2 "initialize_tracer_instance\|_setup_main_provider\|_create_otlp_exporter" src/ --include="*.py"
# Expected: How methods are called with surrounding context

# Find parameter passing patterns
grep -r "tracer_instance\." src/ --include="*.py" | head -20
# Expected: How tracer instances are used and what attributes are accessed
```

### **3. Error Handling Pattern Discovery**
```bash
# Find try/except patterns around function calls
grep -B3 -A3 "try:" [PRODUCTION_FILE] | grep -A6 -B6 "initialize_tracer_instance\|_setup_main_provider"
# Expected: Error handling patterns in real usage

# Find exception handling patterns
grep -B2 -A2 "except.*Exception\|except.*Error" [PRODUCTION_FILE]
# Expected: How exceptions are handled in practice

# Find graceful degradation patterns
grep -B2 -A2 "return None\|return False\|pass" [PRODUCTION_FILE]
# Expected: Graceful failure patterns
```

### **4. Configuration Usage Patterns**
```bash
# Find configuration access patterns
grep -B2 -A2 "config\." [PRODUCTION_FILE]
# Expected: How configuration is accessed and used

# Find conditional configuration usage
grep -B3 -A3 "if.*config\|config.*if" [PRODUCTION_FILE]
# Expected: Conditional configuration patterns

# Find default value patterns
grep -B2 -A2 "getattr.*config\|config.*or\|config.*default" [PRODUCTION_FILE]
# Expected: Default value and fallback patterns
```

---

## 📊 **COMPREHENSIVE USAGE PATTERN REQUIREMENTS**

### **🔍 MUST DOCUMENT FOR TEST STRATEGY**

**FUNCTION CALL PATTERNS:**
- **Parameter Combinations** (common ways functions are called)
- **Return Value Usage** (how return values are used by callers)
- **Error Handling** (how exceptions are caught and handled)
- **Conditional Calls** (when functions are called vs skipped)
- **Sequence Patterns** (order of function calls)

**OBJECT USAGE PATTERNS:**
- **Attribute Access** (which attributes are accessed when)
- **Method Chaining** (sequences of method calls)
- **State Dependencies** (how object state affects behavior)
- **Lifecycle Patterns** (initialization → usage → cleanup)

---

## 🛤️ **PATH-SPECIFIC USAGE ANALYSIS**

### **🧪 UNIT TEST PATH: ISOLATED USAGE PATTERNS**

**Mock Configuration Based on Real Usage:**
```python
def test_realistic_initialization_pattern():
    """Test based on real usage patterns from codebase analysis."""
    
    # Pattern 1: Standard initialization (most common usage)
    mock_tracer = MockHoneyHiveTracer()
    mock_tracer.project_name = "production-project"
    mock_tracer.api_key = "prod-api-key"
    mock_tracer.verbose = False  # Default in production
    
    # Mock dependencies based on real call patterns
    with patch('honeyhive.tracer.instrumentation.initialization._initialize_otel_components') as mock_otel:
        with patch('honeyhive.tracer.instrumentation.initialization._initialize_session_management') as mock_session:
            
            initialize_tracer_instance(mock_tracer)
            
            # Verify real usage patterns
            mock_otel.assert_called_once_with(mock_tracer)
            mock_session.assert_called_once_with(mock_tracer)
            assert mock_tracer._initialized is True

def test_verbose_initialization_pattern():
    """Test verbose initialization pattern found in usage analysis."""
    
    # Pattern 2: Verbose mode (found in debug scenarios)
    mock_tracer = MockHoneyHiveTracer()
    mock_tracer.verbose = True  # Verbose pattern from analysis
    
    with patch('honeyhive.tracer.instrumentation.initialization.safe_log') as mock_log:
        initialize_tracer_instance(mock_tracer)
        
        # Verify verbose logging pattern (found in usage analysis)
        debug_calls = [call for call in mock_log.call_args_list 
                      if call[0][1] == 'debug']
        assert len(debug_calls) >= 2  # Verbose pattern expectation

def test_error_handling_pattern():
    """Test error handling pattern found in usage analysis."""
    
    # Pattern 3: Error handling (found in production error scenarios)
    mock_tracer = MockHoneyHiveTracer()
    
    # Simulate error pattern found in usage analysis
    with patch('honeyhive.tracer.instrumentation.initialization._initialize_otel_components', 
               side_effect=Exception("OTEL initialization failed")):
        
        # Should handle error gracefully (pattern from analysis)
        result = initialize_tracer_instance(mock_tracer)
        
        # Verify graceful degradation pattern
        assert mock_tracer._initialized is False  # Expected failure state
```

**Configuration Usage Pattern Testing:**
```python
def test_configuration_access_patterns():
    """Test configuration access patterns found in usage analysis."""
    
    # Pattern: Configuration attribute access (from usage analysis)
    mock_tracer = MockHoneyHiveTracer()
    mock_tracer.config = Mock()
    mock_tracer.config.api_key = "test-key"
    mock_tracer.config.server_url = "https://api.honeyhive.ai"
    mock_tracer.config.otlp_enabled = True
    
    # Test configuration access pattern found in analysis
    with patch('honeyhive.tracer.instrumentation.initialization._create_otlp_exporter') as mock_create:
        _create_otlp_exporter(mock_tracer)
        
        # Verify configuration access pattern
        mock_create.assert_called_once_with(mock_tracer)

def test_provider_info_usage_pattern():
    """Test provider_info usage pattern found in analysis."""
    
    # Pattern: provider_info structure (from _setup_main_provider_components analysis)
    mock_tracer = MockHoneyHiveTracer()
    mock_provider_info = {
        'provider': Mock(),
        'provider_class_name': 'TracerProvider',
        'provider_instance': Mock(),
        'detection_method': 'atomic',
        'is_global': True,
        'provider_id': 'test-provider-id'
    }
    
    # Test usage pattern found in analysis
    with patch('honeyhive.tracer.instrumentation.initialization._create_otlp_exporter') as mock_create:
        _setup_main_provider_components(mock_tracer, mock_provider_info)
        
        # Verify provider_info usage pattern
        mock_create.assert_called_once_with(mock_tracer)
```

### **🔗 INTEGRATION TEST PATH: REAL USAGE VALIDATION**

**End-to-End Usage Pattern Testing:**
```python
class TestRealUsagePatterns(TestCase):
    """Integration tests validating real usage patterns."""
    
    def test_production_initialization_pattern(self):
        """Test production initialization pattern with real APIs."""
        
        # Real usage pattern: Production-like initialization
        tracer = HoneyHiveTracer(
            api_key=os.getenv("HH_TEST_API_KEY"),
            project="integration-test-project",
            verbose=False  # Production default
        )
        
        # Real initialization pattern
        initialize_tracer_instance(tracer)
        
        # Verify real usage pattern results
        self.assertTrue(tracer._initialized)
        self.assertIsNotNone(tracer._client)
        self.assertIsNotNone(tracer._session_api)
        self.assertIsNotNone(tracer.session_id)
    
    def test_multi_instance_usage_pattern(self):
        """Test multi-instance usage pattern found in production."""
        
        # Real pattern: Multiple tracer instances (found in analysis)
        tracer1 = HoneyHiveTracer(
            api_key=os.getenv("HH_TEST_API_KEY"),
            project="project-1"
        )
        tracer2 = HoneyHiveTracer(
            api_key=os.getenv("HH_TEST_API_KEY"),
            project="project-2"
        )
        
        # Real multi-instance initialization pattern
        initialize_tracer_instance(tracer1)
        initialize_tracer_instance(tracer2)
        
        # Verify isolation pattern (found in usage analysis)
        self.assertNotEqual(tracer1.session_id, tracer2.session_id)
        self.assertEqual(tracer1.project_name, "project-1")
        self.assertEqual(tracer2.project_name, "project-2")
```

---

## 🚨 **CRITICAL USAGE PATTERN FAILURE PREVENTION**

### **V2 Failures That V3 MUST Prevent:**

1. **Unrealistic Mock Configurations** (caused test failures):
   ```python
   # V2 FAILED: Mock configurations didn't match real usage
   mock_provider_info = {}  # Missing required keys from real usage
   
   # V3 PREVENTS: Mock configurations based on usage analysis
   mock_provider_info = {
       'provider': Mock(),
       'provider_class_name': 'TracerProvider',  # Found in usage analysis
       'provider_instance': Mock(),              # Required by real usage
       # ... all keys from usage pattern analysis
   }
   ```

2. **Wrong Parameter Combinations** (caused parameter errors):
   ```python
   # V2 FAILED: Function calls didn't match real usage patterns
   _setup_main_provider_components(mock_tracer)  # Missing provider_info
   
   # V3 PREVENTS: Function calls match usage analysis
   _setup_main_provider_components(mock_tracer, mock_provider_info)  # Correct pattern
   ```

3. **Missing Error Scenarios** (incomplete test coverage):
   ```python
   # V2 FAILED: Didn't test error patterns found in real usage
   # V3 PREVENTS: Test error patterns discovered in usage analysis
   with patch('external_call', side_effect=Exception("Real error pattern")):
       result = function_under_test(mock_tracer)
       # Test graceful degradation pattern from analysis
   ```

---

## 📋 **MANDATORY PHASE 4 COMPLETION EVIDENCE**

### **🛑 CRITICAL: Progress Table Update Required**

**You MUST update the progress table in chat window before proceeding to Phase 5.**

**Required Evidence Format:**
```
| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 4: Usage Patterns | ✅ | Found X usage patterns: initialization in Y locations, error handling in Z methods, config access patterns in A functions | 4/4 | Manual | ✅ |
```

### **🚨 ENFORCEMENT PATTERNS**

**❌ VIOLATION INDICATORS:**
- "Phase 4 complete" without showing updated table
- "Moving to Phase 5" without table update
- "Usage patterns found" without specific counts and details
- "Pattern analysis finished" without evidence

**🛑 VIOLATION RESPONSE:**
"STOP - You completed Phase 4 but didn't update the progress table. Show me the updated table in the chat window with Phase 4 marked as ✅ and evidence documented (usage pattern counts, locations, specific patterns found) before proceeding to Phase 5."

---

## 🎯 **USAGE PATTERN ANALYSIS SUCCESS CRITERIA**

**Phase 4 is complete ONLY when:**
1. ✅ All function call patterns identified and documented
2. ✅ Configuration usage patterns analyzed
3. ✅ Error handling patterns discovered
4. ✅ Parameter combination patterns documented
5. ✅ Real usage scenarios identified for test design
6. ✅ Path-specific usage strategies determined
7. ✅ Progress table updated with specific evidence

**Failure to complete Phase 4 properly WILL cause unrealistic test scenarios and mock configuration errors.**

---

## 🔄 **INTEGRATION WITH OTHER PHASES**

### **Phase 3 → Phase 4 Integration**
- Dependency usage patterns inform how dependencies are actually used
- Mock configurations based on real parameter passing patterns

### **Phase 4 → Phase 5 Integration**
- Usage patterns inform coverage requirements (which scenarios to test)
- Error patterns identify edge cases for comprehensive coverage

### **Phase 4 → Test Generation Integration**
- Unit tests: Mock configurations match real usage patterns
- Integration tests: Test scenarios match production usage patterns
- Error tests: Exception scenarios match real error handling patterns

---

## ✅ **PHASE 4 SUCCESS VALIDATION**

**Usage pattern analysis is successful when:**
1. ✅ Complete inventory of function call patterns
2. ✅ Configuration access patterns documented
3. ✅ Error handling patterns identified
4. ✅ Parameter combination patterns analyzed
5. ✅ Mock configurations planned based on real usage
6. ✅ Integration test scenarios based on production patterns
7. ✅ Progress table shows Phase 4 ✅ with evidence

**Next Phase**: Only proceed to [Phase 5: Coverage Analysis](phase-5-coverage-analysis.md) after progress table update with evidence.

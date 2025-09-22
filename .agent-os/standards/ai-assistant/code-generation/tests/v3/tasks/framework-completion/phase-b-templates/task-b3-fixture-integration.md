# Task B3: Fixture Integration System

**🎯 Seamless Integration with Existing conftest.py Fixtures**

## 📋 **TASK DEFINITION**

### **Objective**
Create automatic detection and integration of existing project fixtures from `conftest.py` files, ensuring generated tests use standard fixtures correctly.

### **Requirements**
- **Fixture Discovery**: Automatically find available fixtures
- **Path-Specific Usage**: Unit vs integration fixture selection
- **Type Safety**: Proper fixture type annotations
- **Documentation**: Clear fixture usage patterns

## 🎯 **DELIVERABLES**

### **Fixture Integration Engine**
- **File**: `v3/ai-optimized/fixture-integration-engine.md`
- **Size**: <100 lines
- **Function**: Automatic fixture discovery and integration

### **Fixture Discovery Logic**
```python
# Required fixture discovery functions
def discover_available_fixtures(conftest_paths):
    """Scan conftest.py files for available fixtures"""
    
def categorize_fixtures_by_path(fixtures):
    """Separate unit vs integration fixtures"""
    
def validate_fixture_compatibility(fixture_name, test_path):
    """Ensure fixture matches test path requirements"""
    
def generate_fixture_usage_code(selected_fixtures, test_path):
    """Generate proper fixture usage in test functions"""
```

### **Unit Test Fixtures**
```python
# Standard unit test fixtures (from existing conftest.py)
unit_fixtures = {
    "mock_tracer_base": {
        "type": "Mock",
        "purpose": "Mocked HoneyHiveTracer instance",
        "usage": "Primary tracer mock for unit tests",
        "required_for": "all_unit_tests"
    },
    "mock_safe_log": {
        "type": "Mock", 
        "purpose": "Mocked logging function",
        "usage": "Verify logging calls without real logging",
        "required_for": "tests_with_logging"
    },
    "disable_tracing_for_unit_tests": {
        "type": "None",
        "purpose": "Disable real tracing in unit tests",
        "usage": "Automatic isolation setup",
        "required_for": "all_unit_tests"
    }
}
```

### **Integration Test Fixtures**
```python
# Standard integration test fixtures (from existing conftest.py)
integration_fixtures = {
    "honeyhive_tracer": {
        "type": "HoneyHiveTracer",
        "purpose": "Real HoneyHive tracer instance",
        "usage": "End-to-end functionality testing",
        "required_for": "all_integration_tests"
    },
    "honeyhive_client": {
        "type": "HoneyHiveClient",
        "purpose": "Real HoneyHive API client",
        "usage": "Backend API interactions",
        "required_for": "api_integration_tests"
    },
    "verify_backend_event": {
        "type": "Callable",
        "purpose": "Backend event verification utility",
        "usage": "Assert events appear in HoneyHive backend",
        "required_for": "backend_verification_tests"
    }
}
```

### **Fixture Usage Generation**
```python
# Generate proper test function signatures
def generate_test_signature(test_name, test_path, required_fixtures):
    if test_path == "unit":
        return f"""
def {test_name}(
    self,
    mock_tracer_base: Mock,
    mock_safe_log: Mock,
    disable_tracing_for_unit_tests: None
) -> None:
"""
    elif test_path == "integration":
        return f"""
def {test_name}(
    self,
    honeyhive_tracer: HoneyHiveTracer,
    verify_backend_event: Callable
) -> None:
"""
```

## 🚨 **ACCEPTANCE CRITERIA**

- [ ] Fixture integration engine implemented and <100 lines
- [ ] Automatic fixture discovery from conftest.py
- [ ] Path-specific fixture categorization
- [ ] Proper fixture type annotations
- [ ] Generated test signatures use correct fixtures
- [ ] Integration with existing project fixtures validated

## 🔗 **DEPENDENCIES**

- **Requires**: Task B1 (Template Validation) completed
- **Requires**: Task B2 (Path Generation) for path-specific logic
- **Requires**: Existing `tests/unit/conftest.py` and `tests/integration/conftest.py`

**Priority: HIGH - Essential for generating tests that actually work with existing infrastructure**

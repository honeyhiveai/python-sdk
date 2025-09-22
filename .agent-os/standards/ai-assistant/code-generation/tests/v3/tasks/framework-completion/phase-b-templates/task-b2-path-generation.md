# Task B2: Path-Specific Code Generation

**🎯 Implement Automated Unit vs Integration Code Generation Logic**

## 📋 **TASK DEFINITION**

### **Objective**
Create the logic that automatically selects and applies the correct templates based on test path (unit vs integration) with no possibility of path mixing.

### **Requirements**
- **Path Lock**: Once path selected, no deviation possible
- **Template Selection**: Automatic template choice based on path
- **Code Generation**: Produce path-appropriate test code
- **Quality Enforcement**: Ensure generated code meets path-specific standards

## 🎯 **DELIVERABLES**

### **Path Generation Engine**
- **File**: `v3/ai-optimized/path-generation-engine.md`
- **Size**: <100 lines
- **Function**: Orchestrate path-specific code generation

### **Path Selection Logic**
```python
# Required path selection functions
def select_test_path(user_input):
    """Lock in unit or integration path - no changes allowed"""
    
def validate_path_consistency(selected_path, analysis_results):
    """Ensure all analysis aligns with selected path"""
    
def apply_path_templates(path, analysis_data):
    """Generate code using path-specific templates only"""
    
def enforce_path_quality_standards(path, generated_code):
    """Apply path-specific quality requirements"""
```

### **Unit Path Generation**
```python
# Unit path specifications
unit_path_config = {
    "strategy": "mock_everything",
    "templates": ["unit-test-template.md", "fixture-patterns.md"],
    "quality_targets": {
        "pylint_score": 10.0,
        "mypy_errors": 0,
        "coverage_target": 90.0,
        "mock_isolation": "complete"
    },
    "fixtures_required": ["mock_tracer_base", "mock_safe_log"],
    "no_real_apis": True
}
```

### **Integration Path Generation**
```python
# Integration path specifications  
integration_path_config = {
    "strategy": "real_api_usage",
    "templates": ["integration-template.md", "backend-verification.md"],
    "quality_targets": {
        "pylint_score": 10.0,
        "mypy_errors": 0,
        "coverage_focus": "functionality_not_metrics",
        "backend_verification": "required"
    },
    "fixtures_required": ["honeyhive_tracer", "verify_backend_event"],
    "no_mocking": True
}
```

### **Path Enforcement**
```python
# Prevent path mixing (critical for framework reliability)
class PathViolationError(Exception):
    """Raised when path mixing is attempted"""
    pass

def enforce_path_purity(selected_path, generated_code):
    if selected_path == "unit":
        if "honeyhive_tracer:" in generated_code:
            raise PathViolationError("Unit test using real fixture")
        if "verify_backend_event" in generated_code:
            raise PathViolationError("Unit test attempting backend verification")
    
    elif selected_path == "integration":
        if "mock_tracer_base" in generated_code:
            raise PathViolationError("Integration test using mock fixture")
        if "@patch" in generated_code:
            raise PathViolationError("Integration test using mocks")
```

## 🚨 **ACCEPTANCE CRITERIA**

- [ ] Path selection engine implemented and <100 lines
- [ ] Unit and integration path configs defined
- [ ] Path enforcement prevents mixing
- [ ] Template selection automated by path
- [ ] Quality standards applied per path
- [ ] Path violation detection working

## 🔗 **DEPENDENCIES**

- **Requires**: Task B1 (Template Validation) completed
- **Requires**: Phase A automation for testing
- **Enables**: Task B3 (Fixture Integration)

**Priority: HIGH - Core logic for preventing path mixing failures**

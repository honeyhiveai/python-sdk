# V3 Test Paths - Path Selection and Strategy Guide

**🎯 Comprehensive Guide for Selecting and Executing Unit vs Integration Test Paths**

*This directory contains path-specific strategies for the V3 framework. Each path has distinct requirements, fixtures, and success criteria optimized for different testing objectives.*

🛑 VALIDATE-GATE: Path Selection Entry Requirements
- [ ] Unit vs integration path differences understood ✅/❌
- [ ] Path selection criteria reviewed ✅/❌
- [ ] Path commitment requirement acknowledged ✅/❌

🚨 FRAMEWORK-VIOLATION: If mixing unit and integration strategies or changing paths mid-execution

---

## 🛑 **PATH SELECTION DECISION TREE EXECUTION**

⚠️ MUST-READ: Path selection is binding - no switching allowed after commitment

### **Quick Path Selection**
```python
def select_test_path(production_file, testing_objective):
    """AI-friendly path selection logic."""
    
    # Unit Path Criteria
    if (
        testing_objective == "isolation" or
        testing_objective == "code_coverage" or
        production_file.has_complex_business_logic() or
        production_file.has_many_external_dependencies()
    ):
        return "unit"
    
    # Integration Path Criteria  
    elif (
        testing_objective == "end_to_end" or
        testing_objective == "api_validation" or
        production_file.is_api_integration_layer() or
        production_file.manages_external_resources()
    ):
        return "integration"
    
    # Default: Unit (safer choice)
    else:
        return "unit"
```

### **Decision Matrix**
| Testing Goal | Recommended Path | Rationale |
|--------------|------------------|-----------|
| **Code Coverage** | Unit | Systematic mocking achieves 90%+ coverage |
| **Business Logic** | Unit | Isolated testing of algorithms and logic |
| **API Validation** | Integration | Real API calls verify actual functionality |
| **End-to-End Flows** | Integration | Complete user journey validation |
| **Error Handling** | Both | Unit for logic errors, Integration for API errors |
| **Performance** | Integration | Real system performance characteristics |

---

## 🧪 **UNIT PATH: MOCK EVERYTHING STRATEGY**

### **When to Choose Unit Path**
- **Single Module Testing**: Focus on one module's business logic
- **High Coverage Requirements**: Need 90%+ line and branch coverage
- **Complex Business Logic**: Algorithms, calculations, data processing
- **Many External Dependencies**: Lots of APIs, databases, file systems
- **Fast Execution**: Need rapid test feedback cycles

### **Unit Path Characteristics**
```python
unit_path_profile = {
    "strategy": "Mock everything external - complete isolation",
    "fixtures": ["mock_tracer_base", "mock_safe_log", "disable_tracing_for_unit_tests"],
    "coverage_target": "90%+ line and branch coverage",
    "execution_speed": "Fast (no real API calls)",
    "validation_focus": "Business logic correctness",
    "mocking_requirement": "100% - ALL external dependencies mocked"
}
```

### **Unit Path Success Criteria**
- ✅ **100% Pass Rate**: All tests pass immediately
- ✅ **90%+ Coverage**: Line and branch coverage targets met
- ✅ **Complete Isolation**: No real external calls
- ✅ **Mock Completeness**: All dependencies properly mocked
- ✅ **Fast Execution**: Tests complete in seconds

### **Unit Path Templates**
- **Primary**: [unit-path.md](unit-path.md) - Complete unit strategy
- **Template**: [../ai-optimized/templates/unit-test-template.md](../ai-optimized/templates/unit-test-template.md)
- **Fixtures**: [../ai-optimized/templates/fixture-patterns.md](../ai-optimized/templates/fixture-patterns.md) (unit section)

---

## 🌐 **INTEGRATION PATH: REAL API STRATEGY**

### **When to Choose Integration Path**
- **End-to-End Testing**: Complete user workflows and scenarios
- **API Integration**: Testing actual API endpoints and responses
- **System Validation**: Verifying real system interactions
- **Backend Verification**: Ensuring data appears correctly in backend
- **Multi-Component**: Testing interactions between multiple services

### **Integration Path Characteristics**
```python
integration_path_profile = {
    "strategy": "Real API usage - end-to-end validation",
    "fixtures": ["honeyhive_tracer", "honeyhive_client", "verify_backend_event"],
    "coverage_target": "Complete functional flow coverage (not line %)",
    "execution_speed": "Slower (real API calls and network)",
    "validation_focus": "End-to-end functionality and backend verification",
    "mocking_requirement": "0% - NO mocks for core functionality"
}
```

### **Integration Path Success Criteria**
- ✅ **100% Pass Rate**: All tests pass with real systems
- ✅ **Functional Coverage**: All critical user flows validated
- ✅ **Backend Verification**: All events verified with `verify_backend_event`
- ✅ **Real API Usage**: Actual API calls and responses
- ✅ **Error Handling**: Real error scenarios tested

### **Integration Path Templates**
- **Primary**: [integration-path.md](integration-path.md) - Complete integration strategy
- **Template**: [../ai-optimized/templates/integration-template.md](../ai-optimized/templates/integration-template.md)
- **Fixtures**: [../ai-optimized/templates/fixture-patterns.md](../ai-optimized/templates/fixture-patterns.md) (integration section)

---

## ⚖️ **PATH COMPARISON**

### **Side-by-Side Comparison**
| Aspect | Unit Path | Integration Path |
|--------|-----------|------------------|
| **Mocking** | Mock everything | No mocks for core functionality |
| **Speed** | Fast (milliseconds) | Slower (seconds to minutes) |
| **Coverage** | 90%+ line/branch | Functional flow coverage |
| **Dependencies** | All mocked | Real APIs and services |
| **Environment** | Isolated test env | Real/test backend systems |
| **Validation** | Logic correctness | End-to-end functionality |
| **Fixtures** | `mock_tracer_base` | `honeyhive_tracer` |
| **Backend** | No backend calls | `verify_backend_event` required |

### **Complementary Nature**
```python
# Unit and Integration tests are complementary, not competing
testing_strategy = {
    "unit_tests": {
        "purpose": "Verify business logic correctness in isolation",
        "coverage": "Comprehensive code coverage (90%+)",
        "speed": "Fast feedback for development"
    },
    "integration_tests": {
        "purpose": "Verify end-to-end functionality with real systems", 
        "coverage": "Critical user journey validation",
        "confidence": "High confidence in production behavior"
    }
}
```

---

## 🚨 **PATH ENFORCEMENT MECHANISMS**

### **Path Selection Lock**
```python
# Once path is selected, framework enforces adherence
class PathEnforcement:
    def __init__(self, selected_path):
        self.selected_path = selected_path
        self.violations = []
    
    def validate_unit_path(self, test_code):
        """Enforce unit path requirements."""
        if "requests.post(" in test_code and "@patch" not in test_code:
            self.violations.append("UNIT VIOLATION: Real API call without mock")
        
        if "honeyhive_tracer" in test_code and "mock_tracer_base" not in test_code:
            self.violations.append("UNIT VIOLATION: Real tracer instead of mock")
    
    def validate_integration_path(self, test_code):
        """Enforce integration path requirements."""
        if "@patch('requests" in test_code:
            self.violations.append("INTEGRATION VIOLATION: Core API mocked")
        
        if "verify_backend_event" not in test_code:
            self.violations.append("INTEGRATION VIOLATION: Missing backend verification")
```

### **Quality Gates by Path**
```python
# Path-specific quality requirements
quality_gates = {
    "unit": {
        "pass_rate": "100%",
        "line_coverage": "90%+", 
        "branch_coverage": "90%+",
        "mock_completeness": "100%",
        "real_api_calls": "0 (forbidden)"
    },
    "integration": {
        "pass_rate": "100%",
        "functional_coverage": "All critical flows",
        "backend_verification": "100% of events verified",
        "real_api_usage": "Required for core functionality",
        "error_scenarios": "Real error conditions tested"
    }
}
```

---

## 🔄 **PATH EXECUTION WORKFLOW**

### **Phase 6: Path-Specific Preparation**
```markdown
1. **Path Confirmation**: Verify selected path (unit or integration)
2. **Template Loading**: Load path-specific templates and patterns
3. **Fixture Selection**: Choose appropriate fixtures for selected path
4. **Strategy Application**: Apply path-specific mocking/real API strategy
5. **Validation Setup**: Configure path-specific quality gates
```

### **Phase 7: Path-Specific Generation**
```markdown
1. **Template Application**: Use path-specific code generation templates
2. **Pattern Integration**: Apply path-appropriate assertion and fixture patterns
3. **Strategy Enforcement**: Ensure mocking (unit) or real API (integration) compliance
4. **Quality Integration**: Apply path-specific quality requirements
5. **Completeness Validation**: Verify all requirements for selected path met
```

### **Phase 8: Path-Specific Validation**
```markdown
1. **Quality Gate Execution**: Run path-specific automated validation
2. **Coverage Verification**: Check appropriate coverage type (line % vs functional)
3. **Strategy Compliance**: Verify no path mixing or violations
4. **Success Confirmation**: Ensure all path-specific criteria met
5. **Framework Completion**: Confirm deterministic, high-quality output
```

---

## 📚 **PATH-SPECIFIC RESOURCES**

### **Unit Path Resources**
- **Strategy Guide**: [unit-path.md](unit-path.md) - Complete unit testing strategy
- **Mock Patterns**: Mock everything approach with comprehensive examples
- **Fixtures**: Standard unit fixtures and usage patterns
- **Coverage**: 90%+ line and branch coverage techniques

### **Integration Path Resources**
- **Strategy Guide**: [integration-path.md](integration-path.md) - Complete integration strategy
- **Real API Patterns**: End-to-end testing with actual backend verification
- **Fixtures**: Real system fixtures and backend verification utilities
- **Validation**: `verify_backend_event` and functional flow verification

### **Shared Resources**
- **Templates**: [../ai-optimized/templates/](../ai-optimized/templates/) - Code generation templates
- **Fixtures**: [../ai-optimized/templates/fixture-patterns.md](../ai-optimized/templates/fixture-patterns.md) - All fixture patterns
- **Quality**: [../enforcement/](../enforcement/) - Quality gates and validation

---

## 🎯 **PATH SELECTION BEST PRACTICES**

### **For AI Assistants**
1. **Read Path Requirements**: Understand both unit and integration strategies
2. **Select Path Early**: Choose path in Phase 1 and stick to it
3. **Follow Path Templates**: Use path-specific templates and patterns
4. **Enforce Path Rules**: Never mix unit and integration strategies
5. **Validate Path Compliance**: Ensure generated tests follow selected path

### **For Human Developers**
1. **Understand Complementary Nature**: Unit and integration tests serve different purposes
2. **Choose Based on Goals**: Coverage (unit) vs End-to-End validation (integration)
3. **Maintain Path Separation**: Keep unit and integration tests in separate files/directories
4. **Use Appropriate Tools**: Different fixtures and validation for each path
5. **Validate Both Paths**: Ensure comprehensive testing strategy

---

**🎯 This path system provides clear, enforced separation between unit (mock external dependencies) and integration (real API) testing strategies. Select the appropriate path based on testing objectives and follow the path-specific templates and requirements for deterministic, high-quality results.**

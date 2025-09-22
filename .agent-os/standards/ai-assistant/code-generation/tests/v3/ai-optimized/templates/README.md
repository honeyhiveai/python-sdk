# V3 Template System - Code Generation Templates

**🎯 Comprehensive Template System for Deterministic Test Generation**

*This directory contains all templates, patterns, and code generation guidance for the V3 framework. Templates are optimized for AI consumption and systematic code generation.*

---

## 📋 **TEMPLATE OVERVIEW**

### **Core Templates**
```markdown
Template Structure:
├── unit-test-template.md      # Complete unit test template (mock everything)
├── integration-template.md    # Complete integration test template (real APIs)
├── fixture-patterns.md        # Standard fixture usage patterns
├── assertion-patterns.md      # Assertion and verification patterns
└── README.md                  # This overview (template system guide)
```

### **Specialized Components**
```markdown
Specialized Templates:
├── unit/
│   └── overview.md           # Unit-specific guidance
├── integration/              # Integration-specific templates
├── fixtures/
│   └── unit-fixtures.md      # Unit fixture patterns
└── assertions/               # Assertion pattern library
```

---

## 🎯 **TEMPLATE SELECTION GUIDE**

### **For Unit Tests (Mock Everything)**
```python
template_selection = {
    "primary_template": "unit-test-template.md",
    "fixtures": "fixture-patterns.md (unit section)",
    "assertions": "assertion-patterns.md (mock verification)",
    "strategy": "Complete isolation with comprehensive mocking"
}
```

### **For Integration Tests (Real APIs)**
```python
template_selection = {
    "primary_template": "integration-template.md", 
    "fixtures": "fixture-patterns.md (integration section)",
    "assertions": "assertion-patterns.md (backend verification)",
    "strategy": "End-to-end validation with real backend verification"
}
```

---

## 🏗️ **TEMPLATE USAGE WORKFLOW**

### **Phase 6: Template Selection**
```markdown
1. **Path Determination**: Unit or Integration (from Phase 1-5 analysis)
2. **Template Loading**: Load appropriate primary template
3. **Pattern Integration**: Apply fixture and assertion patterns
4. **Customization**: Adapt templates to specific production code
5. **Validation**: Ensure template compliance with framework requirements
```

### **Phase 7: Code Generation**
```markdown
1. **Template Application**: Use selected templates systematically
2. **Pattern Substitution**: Replace placeholders with actual code elements
3. **Quality Integration**: Apply Pylint disables and formatting
4. **Completeness Check**: Ensure all identified functions/methods covered
5. **Framework Compliance**: Verify generated code follows all patterns
```

---

## 📊 **TEMPLATE COMPONENTS**

### **Unit Test Template Components**
```python
unit_template_components = {
    "file_header": "Module docstring + Pylint disables with justification",
    "imports": "Standard imports (typing, unittest.mock, pytest)",
    "test_class": "Class-based test organization with descriptive names",
    "fixtures": "Standard conftest.py fixtures (mock_tracer_base, mock_safe_log)",
    "mocking": "Comprehensive @patch decorators for all external dependencies",
    "assertions": "Behavior verification (not implementation testing)",
    "error_handling": "Exception testing and graceful degradation verification"
}
```

### **Integration Template Components**
```python
integration_template_components = {
    "file_header": "Module docstring focused on end-to-end validation",
    "imports": "Real HoneyHive imports (no mocks)",
    "test_class": "Integration-focused test organization",
    "fixtures": "Real fixtures (honeyhive_tracer, verify_backend_event)",
    "api_calls": "Actual API interactions with real backend",
    "verification": "Backend state verification with verify_backend_event",
    "cleanup": "Resource cleanup and session management"
}
```

---

## 🎯 **PATTERN LIBRARIES**

### **Fixture Patterns**
**Source**: [fixture-patterns.md](fixture-patterns.md)
```python
fixture_categories = {
    "unit_fixtures": ["mock_tracer_base", "mock_safe_log", "disable_tracing_for_unit_tests"],
    "integration_fixtures": ["honeyhive_tracer", "honeyhive_client", "verify_backend_event"],
    "utility_fixtures": ["standard_mock_responses", "cleanup_session"]
}
```

### **Assertion Patterns**
**Source**: [assertion-patterns.md](assertion-patterns.md)
```python
assertion_categories = {
    "behavior_verification": "Return values, state changes, interface testing",
    "mock_verification": "Call verification, argument checking, call counts",
    "error_handling": "Exception testing, graceful degradation",
    "backend_verification": "verify_backend_event patterns for integration tests"
}
```

---

## 🚨 **TEMPLATE REQUIREMENTS**

### **Mandatory Elements (All Templates)**
```python
mandatory_elements = {
    "file_header": {
        "docstring": "Clear module purpose and testing strategy",
        "pylint_disables": "Pre-approved disables with justification",
        "imports": "Proper typing and framework imports"
    },
    "test_organization": {
        "class_structure": "Descriptive class names with clear purpose",
        "method_naming": "test_[scenario]_[expected_outcome] pattern",
        "documentation": "Docstrings for all test methods"
    },
    "quality_compliance": {
        "type_hints": "Complete type annotations for all methods",
        "error_handling": "Comprehensive exception testing",
        "coverage": "All identified functions/methods tested"
    }
}
```

### **Path-Specific Requirements**
```python
# Unit Test Requirements
unit_requirements = {
    "mocking": "ALL external dependencies mocked",
    "isolation": "Complete test isolation, no real API calls",
    "fixtures": "Standard unit fixtures from conftest.py",
    "coverage": "90%+ line and branch coverage target"
}

# Integration Test Requirements  
integration_requirements = {
    "real_apis": "NO mocking, real API calls only",
    "verification": "verify_backend_event for all critical interactions",
    "fixtures": "Real integration fixtures from conftest.py", 
    "coverage": "Complete functional flow coverage"
}
```

---

## 🔧 **TEMPLATE CUSTOMIZATION**

### **Production Code Adaptation**
```python
# Templates provide placeholders for customization
customization_points = {
    "[MODULE_NAME]": "Actual module being tested",
    "[MODULE_PURPOSE]": "Description of module functionality", 
    "[FunctionName]": "Actual function/class names from production code",
    "[scenario]": "Specific test scenarios based on code analysis",
    "function_to_test": "Actual function imports and calls"
}
```

### **Framework Integration**
```python
# Templates integrate with framework phases
framework_integration = {
    "phase_1_ast": "Function/class names from AST analysis",
    "phase_2_logging": "Logging patterns and safe_log usage",
    "phase_3_dependencies": "Import mocking and dependency handling",
    "phase_4_usage": "Function call patterns and control flow",
    "phase_5_coverage": "Coverage targets and test completeness"
}
```

---

## 📚 **TEMPLATE REFERENCE**

### **Quick Template Selection**
```bash
# AI Assistant Quick Reference
if test_path == "unit":
    primary_template = "unit-test-template.md"
    fixtures = "fixture-patterns.md (unit section)"
    
elif test_path == "integration":
    primary_template = "integration-template.md"
    fixtures = "fixture-patterns.md (integration section)"
```

### **Template Validation**
```python
# Ensure generated code follows templates
template_validation = {
    "structure_compliance": "Matches template organization and patterns",
    "fixture_usage": "Uses correct fixtures for selected path",
    "assertion_patterns": "Follows established assertion patterns",
    "quality_standards": "Meets all Pylint, MyPy, and formatting requirements"
}
```

---

## 🎯 **SUCCESS CRITERIA**

### **Template System Goals**
```python
success_criteria = {
    "deterministic_generation": "Same input produces consistent output",
    "quality_compliance": "Generated code meets all quality targets",
    "framework_adherence": "Code follows established patterns and conventions",
    "maintainability": "Generated tests are readable and maintainable"
}
```

### **Quality Targets**
- **100% Pass Rate**: All generated tests must pass immediately
- **Coverage Targets**: 90%+ (unit) / functional flow (integration)
- **Static Analysis**: 10.0/10 Pylint, 0 MyPy errors
- **Formatting**: 100% Black compliance

---

**🎯 This template system provides comprehensive, AI-optimized templates for generating high-quality unit and integration tests. Use the templates systematically during Phase 7 (Test Generation) to ensure consistent, deterministic results.**

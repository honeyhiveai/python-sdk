# Unit Test Path - Quick Start

**🎯 AI Quick Start for Unit Tests with Mock Everything Strategy**

🛑 VALIDATE-GATE: Unit Quick Start Entry Requirements
- [ ] Unit test path commitment confirmed ✅/❌
- [ ] Mock everything strategy understood ✅/❌
- [ ] Quick start execution readiness confirmed ✅/❌

🚨 FRAMEWORK-VIOLATION: If mixing unit and integration strategies or using real dependencies

## 🛑 **UNIT TEST STRATEGY EXECUTION**

⚠️ MUST-READ: Unit tests require complete isolation through comprehensive mocking

### **Core Principle: MOCK EVERYTHING**
- ✅ **Mock all external dependencies** (APIs, databases, files)
- ✅ **Mock all internal dependencies** (other modules, classes)
- ✅ **Test interfaces and behavior** not implementation details
- ✅ **Achieve complete isolation** for fast, deterministic tests

## 📋 **EXECUTION CHECKLIST**

### **1. Framework Preparation**
- [ ] Acknowledge binding contract: [../../core/binding-contract.md](../../core/binding-contract.md)
- [ ] Confirm unit test path selection
- [ ] Initialize progress tracking table

### **2. Template Selection**
- [ ] Use unit test template: [../../ai-optimized/templates/unit/overview.md](../../ai-optimized/templates/unit/overview.md)
- [ ] Review fixture patterns: [../../ai-optimized/templates/fixtures/unit-fixtures.md](../../ai-optimized/templates/fixtures/unit-fixtures.md)
- [ ] Study assertion patterns: [../../ai-optimized/templates/assertions/unit-assertions.md](../../ai-optimized/templates/assertions/unit-assertions.md)

### **3. Phase Execution**
- [ ] Follow phase checklist: [../../navigation/phase-checklist.md](../../navigation/phase-checklist.md)
- [ ] Execute all phases systematically
- [ ] Update progress table after each phase

### **4. Quality Validation**
- [ ] Run validate-test-quality.py
- [ ] Achieve exit code 0
- [ ] Verify all quality targets met

## 🔧 **UNIT TEST REQUIREMENTS**

### **Standard Fixtures (Required)**
```python
def test_function(
    self,
    mock_tracer_base: Mock,      # Complete mock tracer
    mock_safe_log: Mock,         # Standard logging mock
    mock_client: Mock,           # API client mock
    standard_mock_responses: Dict # Predefined responses
) -> None:
```

### **Quality Targets**
- ✅ **100% pass rate** on first run
- ✅ **90%+ code coverage** for unit tests
- ✅ **10.0/10 Pylint score** with justified disables
- ✅ **0 MyPy errors** with complete type annotations
- ✅ **Black formatting** applied automatically

### **Pylint Disables (Pre-approved)**
```python
# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Comprehensive test coverage requires extensive test cases, testing private methods
# requires protected access, pytest fixtures redefine outer names by design, comprehensive test
# classes need many test methods, and mock patch decorators create unavoidable long lines.
```

## 🚨 **CRITICAL SUCCESS FACTORS**

### **Must Use Mock Everything**
- ❌ **Never call real APIs** in unit tests
- ❌ **Never access real databases** or external services
- ❌ **Never use real file system** operations
- ✅ **Mock all dependencies** completely

### **Must Use Standard Fixtures**
- ✅ **Use mock_tracer_base** instead of creating Mock()
- ✅ **Use mock_safe_log** for logging verification
- ✅ **Use standard_mock_responses** for API patterns
- ❌ **Never create custom mocks** when standards exist

### **Must Follow Templates**
- ✅ **Use provided unit test templates** consistently
- ✅ **Follow fixture integration patterns** exactly
- ✅ **Apply assertion patterns** appropriately
- ❌ **Never deviate from template structure**

---

**🎯 Execute systematically following the phase checklist for 80%+ success rate.**

# AI Assistant Code Generation Standards

**🎯 Goal**: Generate perfect code (10.0/10 Pylint, 0 MyPy errors, 90%+ coverage) without post-generation fixes.

## **🚨 CRITICAL: MANDATORY FRAMEWORKS**

### **🧪 TEST GENERATION FRAMEWORK (MANDATORY)**
**📋 [tests/README.md](tests/README.md)** - **START HERE FOR ALL TEST GENERATION**
- **🚨 MANDATORY Acknowledgment Contract** - Required before proceeding
- **🛡️ Enforcement Patterns** - Violation detection and prevention mechanisms
- **⚡ Natural Discovery Flow**: Framework → Setup → Choose Path (Unit/Integration) → Analysis → Generation → Quality
- **🎯 Quality Targets**: 100% pass rate + 90%+ coverage + 10.0/10 Pylint + 0 MyPy errors
- **📊 Proven Results**: Grade A effectiveness across 10+ experiments

### **🏗️ PRODUCTION CODE FRAMEWORK (MANDATORY)**
**📋 [production/README.md](production/README.md)** - **START HERE FOR ALL PRODUCTION CODE**
- **🔀 Complexity-Based Paths**: Simple Functions → Complex Functions → Classes
- **📋 Template-Driven Generation** with checkpoint gates and quality enforcement
- **⚡ Natural Discovery Flow**: Framework → Complexity Assessment → Choose Path → Analysis → Generation → Quality
- **🎯 Quality Targets**: 10.0/10 Pylint + 0 MyPy errors + Complete type annotations + Comprehensive docstrings
- **🛡️ Quality Gates**: Cannot bypass quality enforcement

## **🚨 FRAMEWORK SELECTION DECISION TREE**

### **Step 1: Identify Generation Type**
```
Are you generating TESTS or PRODUCTION CODE?
├── 🧪 TESTS → Use Test Generation Framework (MANDATORY acknowledgment required)
└── 🏗️ PRODUCTION CODE → Use Production Code Framework (complexity assessment required)
```

### **Step 2: Follow Appropriate Framework**

| Generation Type | Framework Hub | MANDATORY Requirements |
|----------------|---------------|----------------------|
| **🧪 Tests** | **[Test Generation Framework](tests/README.md)** | Acknowledgment contract + Natural discovery flow |
| **🏗️ Production Code** | **[Production Code Framework](production/README.md)** | Complexity assessment + Template-driven approach |

## **🧪 TEST GENERATION QUICK ACCESS**

### **Framework Components (All MANDATORY)**
- **[Framework Hub](tests/README.md)** - Complete framework with acknowledgment contract
- **⚡ NEW: [Modular Framework v2](tests/v2/framework-core.md)** - **OPTIMIZED FOR AI CONSUMPTION (68% smaller)**
- **[Framework Execution Guide](tests/archive/framework-execution-guide.md)** - Execution rules and enforcement (ARCHIVED)
- **[Phase 0 Setup](tests/archive/phase-0-setup.md)** - Pre-generation validation (ARCHIVED)
- **[Unit Test Path](tests/archive/unit-test-generation.md)** - Single module testing with comprehensive mocks (ARCHIVED)
- **[Integration Test Path](tests/archive/integration-test-generation.md)** - Real API testing (ARCHIVED)

### **Quality Enforcement**
- **[Unit Test Quality](tests/archive/unit-test-quality.md)** - 90%+ coverage requirements (ARCHIVED)
- **[Integration Test Quality](tests/archive/integration-test-quality.md)** - Functional validation requirements (ARCHIVED)

### **⚡ NEW MODULAR PATHS (RECOMMENDED)**
- **[Unit Test Path v2](tests/v2/paths/unit-path.md)** - Optimized unit test guidance
- **[Integration Test Path v2](tests/v2/paths/integration-path.md)** - Optimized integration test guidance

## **🏗️ PRODUCTION CODE QUICK ACCESS**

### **Complexity-Based Paths (v2 API)**
- **[Simple Functions v2](production/v2/simple-functions-legacy/)** - Utility functions, validators, formatters
- **[Complex Functions v2](production/v2/complex-functions/)** - Business logic, API handlers, processing functions
- **[Classes v2](production/v2/classes/)** - Pydantic models, service classes, configuration classes

### **Framework Components (v2 API)**
- **[Complexity Assessment v2](production/v2/complexity-assessment.md)** - Determine appropriate path
- **[Framework Execution Guide v2](production/v2/framework-execution-guide.md)** - Production code execution rules

## **🚨 Why This Process Prevents Issues**

| Issue Type | Prevention Method | Evidence |
|------------|------------------|----------|
| Unused imports | Step 1: Import planning | Caught 6 unused imports |
| Line length violations | Step 1: Length strategy | Caught 15+ violations |
| Missing type annotations | Step 1: Type planning | Caught 95 MyPy errors |
| Environment issues | Step 1: Environment check | Caught wrong Python path |

## **📚 Supporting Documentation**

- **Linter-Specific**: `linters/` directory
- **Framework Validation**: `test-generation-framework-check.py`
- **Quality Framework**: `../quality-framework.md`

---

**Remember**: The pre-generation checklist is the lightweight prevention layer that stops issues before they start!
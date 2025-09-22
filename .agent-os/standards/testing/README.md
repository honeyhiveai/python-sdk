# Testing Standards - HoneyHive Python SDK

**🎯 AI-Optimized Documentation for Consistent Quality**

This directory contains focused, comprehensive testing standards designed to ensure AI assistants and human developers consistently deliver high-quality code that meets project requirements.

## 🔒 **MANDATORY: Test Generation Framework**

**⛔ BEFORE writing ANY tests, AI assistants MUST follow the comprehensive framework:**

- **📋 Framework Hub**: [Test Generation Framework](../ai-assistant/code-generation/tests/README.md)
- **🚀 Natural Discovery**: Framework → Setup → Choose Path (Unit/Integration) → Analysis → Generation → Quality
- **🎯 Targets**: 100% pass rate + 90%+ coverage (unit) / functional validation (integration) + 10.0/10 Pylint + 0 MyPy errors

**🚨 RULE**: Follow natural discovery flow with embedded standards for consistent quality

## 📋 **Quick Reference for AI Assistants**

### **Mandatory Requirements for ALL Test Code**
- **Framework Compliance**: MUST follow natural discovery flow with embedded standards
- **Type Annotations**: Every function, method, and variable MUST have type hints
- **Pylint Score**: 10.0/10 (no exceptions without approval)
- **Mypy Errors**: 0 (complete type safety)
- **Docstrings**: All classes and methods must have comprehensive docstrings
- **Test Commands**: ALWAYS use `tox` - NEVER run `pytest` directly

### **Quality Standards Checklist**
- [ ] All imports have type annotations (`Mock`, `Dict[str, str]`, etc.)
- [ ] All test methods have return type annotations (`-> None`)
- [ ] All fixture parameters are typed
- [ ] Protected access uses approved disables (`# pylint: disable=protected-access`)
- [ ] Line length handled by Black formatter
- [ ] No unused imports or variables

## 📚 **Documentation Structure**

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [Unit Testing Standards](unit-testing-standards.md) | Advanced unit test examples and edge cases | Complex unit testing scenarios |
| [Integration Testing Standards](integration-testing-standards.md) | Real-world integration scenarios and patterns | Production-like integration testing |
| [Debugging Methodology](debugging-methodology.md) | 6-step systematic debugging process | When tests fail or need troubleshooting |
| [Test Execution Commands](test-execution-commands.md) | All tox/pytest commands with examples | Running tests, CI/CD setup |
| [Fixture and Patterns](fixture-and-patterns.md) | Advanced testing patterns and custom assertions | Complex testing scenarios |

## 🚨 **Critical AI Assistant Guidelines**

### **When Writing New Tests**
1. **Complete skip-proof framework** - ALL 5 checkpoint gates with evidence
2. **Start with type annotations** - never generate untyped code
3. **Follow fixture patterns** from `fixture-and-patterns.md`
4. **Use debugging methodology** when tests fail
5. **Apply quality standards** from the start (embedded in framework)

### **When Fixing Existing Tests**
1. **Read debugging methodology** for systematic approach
2. **Apply unit testing standards** for structure
3. **Ensure quality standards** are met (embedded in framework)
4. **Use approved patterns** from fixture documentation

### **Common AI Assistant Queries**
- "What type annotations are required for test methods?" → [Unit Testing Standards](unit-testing-standards.md#type-annotations)
- "How do I debug failing tests systematically?" → [Debugging Methodology](debugging-methodology.md#5-step-process)
- "What pylint disables are approved for tests?" → [Unit Testing Standards](unit-testing-standards.md#pylint-requirements)
- "How should I structure mock fixtures?" → [Fixture and Patterns](fixture-and-patterns.md#mock-patterns)

## 🎯 **Success Metrics**

Every test file should achieve:
- **Pylint**: 10.00/10
- **Mypy**: 0 errors
- **Coverage**: ≥80% (project minimum)
- **Tests**: All passing
- **Documentation**: Complete docstrings

---

**💡 Remember**: These standards exist to ensure consistent, high-quality code across all sessions. AI assistants should reference these documents frequently to maintain project standards.

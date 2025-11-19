# AI Assistant Quality Framework

**🎯 MISSION: Enable AI assistants to autonomously ship production-quality solutions**

This framework ensures AI assistants can independently deliver code that meets all quality standards without human intervention, while maintaining safety and reliability.

## 🚨 CRITICAL: Pre-Generation Validation Protocol

**MANDATORY: Execute BEFORE generating ANY code**

```bash
# 1. Get Current Date (MANDATORY for all dated content)
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"

# 2. Validate Current Codebase State
read_file src/honeyhive/__init__.py     # Check current API exports
grep -r "from honeyhive import" examples/  # Verify import patterns  
grep -r "class.*:" src/honeyhive/       # Validate class names
git status --porcelain                  # Ensure clean working directory
git branch --show-current              # Verify correct branch
```

**Purpose**: Prevent common AI assistant errors like hardcoded dates, incorrect imports, and working on wrong branches.

## 🤖 **AI Assistant Command Templates**

**MANDATORY: Use these exact command blocks for consistent execution**

### Pre-Work Validation Template (Copy-Paste Ready)
```bash
# MANDATORY: Run this exact block before any code generation
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"
python --version  # Verify Python 3.11+
which python      # Verify virtual environment active
git status --porcelain  # Must be clean
git branch --show-current  # Verify correct branch
```

### Quality Gate Execution Template (Sequential - ALL Must Pass)
```bash
# Run these commands in sequence - STOP if any fail
tox -e format    # Black formatting check
tox -e lint      # Pylint + mypy analysis  
tox -e unit      # Unit tests (fast, isolated)
tox -e integration  # Integration tests (real APIs)
cd docs && make html  # Documentation build (zero warnings)
cd ..  # Return to project root
```

### Test Debugging Template (For Failing Tests)
```bash
# Isolate and debug specific failing test
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate
python -m pytest tests/unit/test_specific_file.py::TestClass::test_method -v -s
# Add --pdb for interactive debugging if needed
```

### Production Code Analysis Template (Before Test Fixes)
```bash
# MANDATORY: Understand production code before fixing tests
read_file src/honeyhive/path/to/module.py  # Read code being tested
grep -r "class ClassName" src/honeyhive/   # Find class definitions
grep -r "def method_name" src/honeyhive/   # Find method signatures
grep -r "from honeyhive" tests/           # Verify test imports
```

## ✅ Autonomous Quality Gates (ALL MUST PASS)

**MANDATORY: Every code change must pass ALL quality gates**

### Code Quality Gates
```bash
tox -e format           # Black formatting (MUST pass)
tox -e lint            # Pylint analysis ≥8.0/10.0 (MUST pass)
tox -e unit            # Unit tests 100% (MUST pass)
tox -e integration     # Integration tests 100% (MUST pass)
tox -e py311 -e py312 -e py313  # Python compatibility (MUST pass)
```

### Documentation Gates  
```bash
cd docs && make html   # Sphinx build, zero warnings (MUST pass)
cd .. && python -m doctest examples/*.py  # Examples work (MUST pass)
```

### Enhanced Pre-Commit Quality Gates
**These run automatically via pre-commit hooks for ALL significant changes:**
- CHANGELOG update validation for documentation, configuration, and code changes
- Mandatory documentation updates for new features and large changesets
- Comprehensive file pattern matching (docs, scripts, config, praxis OS files)
- AI assistant compliance checking with automatic enforcement

## 🚫 Zero Failing Tests Policy

**❌ NEVER COMMIT** if ANY test fails
**❌ NEVER PUSH** failing tests to ANY branch
**❌ NEVER USE** `git commit --no-verify` without immediate fix
**❌ NEVER USE** hardcoded dates - always use `date +"%Y-%m-%d"`
**❌ NEVER SKIP TESTS** - AI assistants MUST fix failing tests, never skip them
**❌ NEVER USE** `@pytest.mark.skip` or commenting out failing tests

## 🤖 Autonomous Decision Framework

**AI Assistants MUST autonomously:**

### 1. Handle Test Failures
**MANDATORY: Use 5-Step Systematic Debugging Methodology**
1. **Read Production Code**: Understand current implementation and API signatures
2. **Ensure Standard Fixture Usage**: Verify correct fixture selection and setup
3. **Develop Hypothesis**: Analyze failure patterns and identify root cause
4. **Detail Fix Plan**: Create comprehensive plan with validation approach
5. **Implement and Test**: Apply fix systematically with quality gate validation

**Common Fix Patterns:**
- **Import errors**: Fix missing imports and module references
- **Type annotations**: Add complete type hints for mypy compliance
- **Coverage gaps**: Write tests for uncovered code paths
- **Integration failures**: Debug real API issues and fix root causes

### 2. Maintain Quality Standards
- **Apply formatting**: Run Black and isort automatically
- **Resolve linting**: Fix pylint violations to achieve ≥8.0/10.0
- **Update documentation**: Add docstrings and update examples
- **Cross-reference validation**: Ensure all internal links work

### 3. Ensure Compatibility
- **Test across Python versions**: Validate 3.11, 3.12, 3.13 compatibility
- **Validate examples**: Ensure all documentation examples execute correctly
- **Check dependencies**: Verify all imports and requirements are correct

### 4. Prevent Regressions
- **Run full test suite**: Execute both unit and integration tests
- **Verify existing functionality**: Ensure changes don't break existing features
- **Validate API compatibility**: Maintain backward compatibility

### 5. Apply Dynamic Logic Principles
- **Prefer dynamic over static**: Use configuration-driven, discoverable systems instead of hardcoded mappings
- **Enable extensibility**: Design code that adapts to new requirements without modification
- **Implement pattern-based processing**: Use dynamic discovery and pattern matching for attribute processing, provider detection, and configuration handling
- **Reference**: See [Dynamic Logic Pattern](../coding/python-standards.md#dynamic-logic-pattern) in Python Standards

## 📅 Date Usage Requirements - MANDATORY

**🚨 CRITICAL: AI Assistants consistently make date errors. Follow these rules:**

### Correct Date Handling
```bash
# 1. ALWAYS get current date first
CURRENT_DATE=$(date +"%Y-%m-%d")

# 2. Use ISO 8601 format: YYYY-MM-DD
echo "Today is: $CURRENT_DATE"  # e.g., 2025-09-13

# 3. For new specs
mkdir ".agent-os/specs/${CURRENT_DATE}-spec-name/"

# 4. In file headers
echo "**Date**: $CURRENT_DATE" >> spec.md

# 5. NEVER hardcode dates
# ❌ WRONG: "2025-01-30" when today is 2025-09-13
# ✅ CORRECT: Use $CURRENT_DATE variable
```

### Common Date Errors to Prevent
- ❌ Using random past dates (2025-01-30 when today is 2025-09-13)
- ❌ Wrong formats (09/13/2025, Sep 13, 2025)
- ❌ Hardcoded dates instead of system date
- ❌ Inconsistent dates across files

## 💬 Commit Message Standards - MANDATORY

**🚨 CRITICAL: AI Assistants consistently make commit message formatting errors**

### Correct Commit Format
```bash
# Use Conventional Commits: <type>: <description> (max 50 chars)
git commit -m "feat: add dynamic baggage management"
git commit -m "fix: resolve span processor race condition"
git commit -m "docs: update API reference examples"

# Body lines: Maximum 72 characters each
git commit -m "feat: add provider detection

Implements dynamic pattern matching for OpenTelemetry providers
with extensible configuration and multi-instance support."
```

### Commit Message Types
- **feat**: New features
- **fix**: Bug fixes
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Test additions or modifications
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Maintenance tasks

### Common Commit Errors to Prevent
- ❌ Missing closing quotes: `git commit -m "feat: Add feature`
- ❌ Unnecessary quotes: `git commit -m "\"feat: Add feature\""`
- ❌ Too long: `feat: Add comprehensive documentation quality control system validation` (71 chars)
- ❌ Wrong format: Missing type prefix or colon
- ❌ Periods at end: `feat: Add feature.`

## 📚 Documentation Quality Prevention

**MANDATORY: Follow test-first documentation approach**

### Documentation Standards
1. ✅ **RST Structure**: Title underlines, blank lines, proper indentation
2. ✅ **Type Safety**: EventType enums only, complete imports
3. ✅ **Code Examples**: Valid syntax, working imports, tested execution
4. ✅ **Cross-References**: Working internal links, toctree inclusion

### Test-First Documentation Process
1. **Implement Code First**: Write and test the actual implementation
2. **Verify Functionality**: Ensure code works in real environment
3. **Write Documentation**: Create examples based on working code
4. **Test Examples**: Validate all code examples execute correctly
5. **Update Standards**: Only after verifying the approach works

## 🎯 **AI Assistant Self-Validation Checklist**

**MANDATORY: Complete this checklist before submitting ANY code change**

### Code Generation Checklist (ALL Must Be ✅)
- [ ] **Type Annotations**: Every function has complete type hints (`param: Type`, `-> ReturnType`)
- [ ] **Docstrings**: Sphinx format with `:param:`, `:type:`, `:return:`, `:rtype:`, examples for all public functions
- [ ] **Error Handling**: Graceful degradation patterns implemented (try/except with safe_log)
- [ ] **Import Validation**: Verified against current `src/honeyhive/__init__.py` exports
- [ ] **Test Coverage**: Unit tests written for all new functions and methods
- [ ] **Logging**: Used `safe_log()` utility instead of print statements
- [ ] **Configuration**: Used nested config access (e.g., `tracer.config.session.inputs`)
- [ ] **Pylint Compliance**: Generated code achieves 10/10 pylint score without post-generation fixes
- [ ] **Descriptive Names**: All variables and functions have clear, descriptive names
- [ ] **Parameter Limits**: Functions use keyword-only arguments (`*,`) when >3 parameters
- [ ] **No Unused Code**: All variables and parameters are used or prefixed with underscore

### Test Fixing Checklist (ALL Must Be ✅)
- [ ] **Production Code Analysis**: Read and understood the code being tested (Step 3 of debugging methodology)
- [ ] **Mock Signature Verification**: Verified @patch decorators match method signatures (mocks as positional args)
- [ ] **Type Safety**: All test variables have type annotations (`baggage_items: Dict[str, str]`)
- [ ] **Assertion Logic**: Verified expected vs actual values make logical sense
- [ ] **Import Correctness**: All imports match current production code structure
- [ ] **Fixture Usage**: Used appropriate fixtures and mock objects correctly
- [ ] **Error Pattern Recognition**: Applied known patterns for common test failures

### Documentation Checklist (ALL Must Be ✅)
- [ ] **Code Examples**: All examples tested and working (copy-paste executable)
- [ ] **Type Safety**: EventType enums used, no string literals (`EventType.model` not `"model"`)
- [ ] **Complete Imports**: All necessary imports included in examples
- [ ] **Cross-References**: All internal links verified and working
- [ ] **Sphinx Compliance**: RST format, proper directives, zero build warnings

### Quality Gate Verification (ALL Must Pass)
- [ ] **Formatting**: `tox -e format` passes (Black + isort)
- [ ] **Linting**: `tox -e lint` passes (Pylint ≥8.0/10.0 + mypy zero errors)
- [ ] **Unit Tests**: `tox -e unit` passes (100% pass rate)
- [ ] **Integration Tests**: `tox -e integration` passes (100% pass rate)
- [ ] **Documentation**: `cd docs && make html` passes (zero warnings)

### Pre-Submission Final Check (ALL Must Be ✅)
- [ ] **Environment**: Verified virtual environment active (`which python`)
- [ ] **Branch**: Confirmed on correct branch (`git branch --show-current`)
- [ ] **Clean State**: No uncommitted changes (`git status --porcelain`)
- [ ] **Date Usage**: Used `$(date +"%Y-%m-%d")` for any dated content
- [ ] **Command Templates**: Used exact command blocks from this framework

**🚨 CRITICAL**: If ANY checkbox is unchecked, DO NOT proceed. Fix the issue first.

## 🚨 Escalation Protocol

**Hand off to human when:**

### Technical Limitations
- **Repeated Failures**: Cannot resolve test failures after 3 attempts
- **Architecture Changes**: Major structural modifications needed
- **Security Issues**: Authentication or data protection concerns
- **Performance Problems**: Significant latency or resource issues

### Complex Decisions
- **Breaking Changes**: API modifications that affect backward compatibility
- **Design Patterns**: Fundamental architectural decisions
- **External Dependencies**: New library or service integrations
- **Business Logic**: Domain-specific requirements or constraints

## 📊 Success Metrics

**Framework succeeds when:**

### Quality Metrics
- **100% of commits** pass all tests on first attempt
- **90%+ of development tasks** handled autonomously
- **Zero production bugs** from AI-generated code
- **Code quality metrics** consistently improve over time

### Efficiency Metrics
- **Reduced review cycles**: Fewer back-and-forth iterations
- **Faster delivery**: Autonomous completion of routine tasks
- **Higher consistency**: Uniform code quality across all contributions
- **Better documentation**: Complete, tested examples in all docs

## 🔧 Implementation References

### Related Standards
- **[Git Safety Rules](git-safety-rules.md)** - Forbidden operations and data loss prevention
- **[Commit Protocols](commit-protocols.md)** - Review checkpoints and CHANGELOG requirements
- **[Logging Patterns](logging-patterns.md)** - Structured logging and debug output standards

### praxis OS Specifications
- `.agent-os/specs/2025-09-03-ai-assistant-quality-framework/` - Complete framework specification
- `.agent-os/specs/2025-09-03-zero-failing-tests-policy/` - Testing requirements and enforcement
- `.agent-os/specs/2025-09-03-date-usage-standards/` - Date handling requirements and validation
- `.agent-os/specs/2025-09-03-commit-message-standards/` - Commit format requirements and examples

### Quality Standards References
- **[Code Quality](../development/code-quality.md)** - Quality gates and tool configuration
- **[Testing Standards](../development/testing-standards.md)** - Test requirements and coverage
- **[Python Standards](../coding/python-standards.md)** - Language-specific guidelines

---

**📝 Next Steps**: Review [Git Safety Rules](git-safety-rules.md) and [Commit Protocols](commit-protocols.md) for complete AI assistant guidelines.

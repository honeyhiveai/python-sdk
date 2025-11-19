# Python SDK Test Execution Commands

**Comprehensive guide to running tests in the HoneyHive Python SDK.**

---

## 🚨 TL;DR - Test Execution Quick Reference

**Keywords for search**: Python SDK test commands, HoneyHive SDK tox commands, how to run tests Python SDK, pytest tox execution, unit tests integration tests, tox parallel execution, test coverage Python SDK, debugging tests, test-specific commands, Python SDK tox environments, HH_API_KEY testing, pytest markers patterns, coverage report htmlcov, CI/CD test commands, release validation testing, tox -e unit integration format lint

**Core Principle:** ALWAYS use tox for running tests - NEVER run pytest directly. Tox ensures environment isolation, dependency management, and CI/CD compatibility.

**Essential Commands:**
```bash
tox -e unit          # Run unit tests (fast, isolated)
tox -e integration   # Run integration tests (real APIs)
tox -e format        # Format code with Black
tox -e lint          # Run pylint + mypy
tox -e coverage      # Generate coverage report
```

**Why Tox is Required:**
- Environment isolation (clean test environments)
- Dependency management (correct package versions)
- Consistency (same commands everywhere)
- CI/CD compatibility (matches production pipeline)

**Quick Development Cycle:**
```bash
# 1. Format code
tox -e format

# 2. Run tests on specific file
tox -e unit -- tests/unit/test_file.py -v

# 3. Check coverage
tox -e coverage
```

**Parallel Execution (Faster):**
```bash
tox -p auto -e unit,integration  # Auto-detect CPU cores
tox -e integration-parallel       # pytest -n auto
```

---

## ❓ Questions This Answers

1. "How do I run tests for Python SDK?"
2. "What is the test command for Python SDK?"
3. "How do I run unit tests for HoneyHive SDK?"
4. "How do I run integration tests for Python SDK?"
5. "Why use tox instead of pytest?"
6. "How do I run tests in parallel?"
7. "How do I test specific files or functions?"
8. "How do I generate coverage reports?"
9. "How do I debug failing tests?"
10. "What tox environments are available?"
11. "How do I run tests for specific Python versions?"
12. "How do I format code before testing?"
13. "What commands does CI/CD use?"
14. "How do I run tests with environment variables?"
15. "How do I stop on first test failure?"
16. "How do I see print statements in tests?"
17. "How do I run only failed tests?"
18. "What is the pre-commit test workflow?"
19. "How do I validate before release?"
20. "How do I test across multiple Python versions?"

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Running tests** | `pos_search_project(action="search_standards", query="how to run Python SDK tests")` |
| **Unit tests** | `pos_search_project(action="search_standards", query="Python SDK unit test commands")` |
| **Integration tests** | `pos_search_project(action="search_standards", query="Python SDK integration test commands")` |
| **Coverage** | `pos_search_project(action="search_standards", query="Python SDK coverage report")` |
| **Debugging tests** | `pos_search_project(action="search_standards", query="Python SDK debug failing tests")` |
| **Parallel execution** | `pos_search_project(action="search_standards", query="Python SDK parallel test execution")` |
| **Tox environments** | `pos_search_project(action="search_standards", query="Python SDK tox environments list")` |
| **CI/CD commands** | `pos_search_project(action="search_standards", query="Python SDK CI/CD test commands")` |

---

## 🎯 Purpose

Define the exact test execution commands for the HoneyHive Python SDK to ensure consistent, reliable test execution across all development environments and CI/CD pipelines.

**Without this standard**: Inconsistent test execution, environment-specific failures, unclear testing workflow, and broken CI/CD compatibility.

---

## MANDATORY: Use Tox - Never Pytest Directly

**ALWAYS use tox for running tests - NEVER run pytest directly**

### Why Tox is Required

1. **Environment Isolation**: Tests run in clean, isolated environments
2. **Dependency Management**: Ensures correct package versions
3. **Consistency**: Same commands work across all development environments
4. **CI/CD Compatibility**: Matches production testing pipeline

**❌ Wrong:**
```bash
pytest tests/  # DON'T DO THIS
```

**✅ Correct:**
```bash
tox -e unit  # ALWAYS USE TOX
```

---

## Core Test Commands

### Unit Tests (Fast, Isolated)

```bash
# Run all unit tests
tox -e unit

# Run specific unit test file
tox -e unit -- tests/unit/test_specific_file.py

# Run specific test class
tox -e unit -- tests/unit/test_file.py::TestClassName

# Run specific test method
tox -e unit -- tests/unit/test_file.py::TestClassName::test_method_name
```

### Integration Tests (Real APIs, End-to-End)

```bash
# Run all integration tests
tox -e integration

# Run specific integration test
tox -e integration -- tests/integration/test_specific.py
```

### Quality Checks

```bash
# Format code with Black
tox -e format

# Run pylint and mypy analysis
tox -e lint

# Combined format and lint
tox -e format && tox -e lint
```

### Python Version Testing

```bash
# Test with specific Python versions
tox -e py311           # Python 3.11 specific tests
tox -e py312           # Python 3.12 specific tests  
tox -e py313           # Python 3.13 specific tests

# Test across all supported versions
tox -e py311,py312,py313
```

---

## Parallel Execution (Faster)

### Parallel Test Execution

```bash
# Run multiple environments in parallel
tox -p auto -e unit,integration    # Auto-detect CPU cores
tox -p 4 -e unit,integration       # Use 4 parallel processes

# Integration tests with pytest-xdist
tox -e integration-parallel        # Uses pytest -n auto --dist=worksteal
```

**Performance Gain**: 2-4x faster on multi-core machines

### Parallel Configuration

```bash
# Manual parallel execution (if needed)
pytest tests/integration/ -n auto --dist=worksteal  # Auto worker count
pytest tests/integration/ -n 4 --dist=each         # 4 workers, load balancing
```

---

## Targeted Testing Commands

### File-Specific Testing

```bash
# Test single file with full output
tox -e unit -- tests/unit/test_tracer_processing_context.py -v

# Test single file with short output
tox -e unit -- tests/unit/test_tracer_processing_context.py -q

# Test single file with maximum verbosity
tox -e unit -- tests/unit/test_tracer_processing_context.py -vvv
```

### Pattern-Based Testing

```bash
# Test files matching pattern
tox -e unit -- tests/unit/test_tracer_*.py

# Test methods matching pattern
tox -e unit -- -k "test_process"

# Test specific markers
tox -e unit -- -m "not slow"
```

### Debugging Commands

```bash
# Run with full traceback information
tox -e unit -- tests/unit/test_file.py --tb=long

# Show local variables in tracebacks
tox -e unit -- tests/unit/test_file.py --tb=long --showlocals

# Stop on first failure
tox -e unit -- tests/unit/test_file.py -x

# Run with print statements visible
tox -e unit -- tests/unit/test_file.py -s
```

---

## Coverage Commands

### Coverage Generation

```bash
# Generate coverage report
tox -e coverage

# Generate HTML coverage report
tox -e coverage-html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Analysis

```bash
# Show coverage for specific file
coverage report --include="tests/unit/test_file.py"

# Show missing lines
coverage report --show-missing

# Generate coverage data only
coverage run -m pytest tests/unit/
```

---

## Development Workflow Commands

### Pre-Commit Workflow

```bash
# Standard development workflow
tox -e format          # Format code
tox -e lint            # Check quality
tox -e unit            # Run unit tests
tox -e integration     # Run integration tests (if needed)
```

### Quick Development Cycle

```bash
# Fast feedback loop for active development
tox -e unit -- tests/unit/test_current_file.py -v

# Format and test specific file
tox -e format && tox -e unit -- tests/unit/test_file.py
```

### Full Validation

```bash
# Complete validation before commit
tox -e format,lint,unit,integration

# Parallel full validation (faster)
tox -p auto -e format,lint,unit,integration
```

---

## CI/CD Commands

### Continuous Integration

```bash
# Commands used in CI/CD pipeline
tox -e format          # Code formatting check
tox -e lint            # Quality analysis
tox -e unit            # Unit test execution
tox -e integration     # Integration test execution
tox -e coverage        # Coverage reporting
```

### Release Validation

```bash
# Full release validation
tox -e py311,py312,py313,format,lint,coverage

# Parallel release validation (faster)
tox -p auto -e py311,py312,py313,format,lint,coverage
```

---

## Advanced Options

### Environment Variables

```bash
# Set test environment variables
HH_TEST_MODE=true tox -e unit
HH_API_KEY=test-key tox -e integration

# Use .env file for local development
cp env.integration.example .env
tox -e integration
```

### Verbose Output Control

```bash
# Minimal output
tox -e unit -q

# Standard output
tox -e unit

# Verbose output
tox -e unit -v

# Maximum verbosity
tox -e unit -vv
```

### Test Selection

```bash
# Run only failed tests from last run
tox -e unit -- --lf

# Run failed tests first, then others
tox -e unit -- --ff

# Run tests that changed since last commit
tox -e unit -- --testmon
```

---

## Command Reference Tables

### Essential Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `tox -e unit` | Run unit tests | Development, quick feedback |
| `tox -e integration` | Run integration tests | Feature validation |
| `tox -e format` | Format code | Before committing |
| `tox -e lint` | Quality checks | Before committing |
| `tox -e coverage` | Coverage report | Quality assessment |

### Development Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `tox -e unit -- file.py` | Test specific file | Active development |
| `tox -e unit -- -k pattern` | Test by pattern | Feature-specific testing |
| `tox -e unit -- -x` | Stop on first failure | Debugging |
| `tox -e unit -- -s` | Show print output | Debugging |

### Quality Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `tox -e format,lint` | Format and check quality | Pre-commit |
| `tox -p auto -e unit,integration` | Parallel testing | Full validation |
| `tox -e py311,py312,py313` | Multi-version testing | Release preparation |

---

## Best Practices

### Development Workflow

1. **Start with unit tests** - fast feedback loop
2. **Format regularly** - maintain code quality
3. **Run integration tests** - validate end-to-end functionality
4. **Check coverage** - ensure adequate test coverage

### Debugging Workflow

1. **Run specific test** - isolate the issue
2. **Use verbose output** - understand what's happening
3. **Add debugging flags** - get detailed information
4. **Test incrementally** - verify fixes step by step

### Performance Optimization

1. **Use parallel execution** - faster test runs
2. **Target specific tests** - avoid running unnecessary tests
3. **Use test patterns** - run related tests together
4. **Optimize test data** - reduce setup/teardown time

---

## 🔗 Related Standards

**Query workflow for testing:**

1. **Start with this standard** → `pos_search_project(action="search_standards", query="Python SDK test commands")`
2. **Learn testing standards** → `pos_search_project(action="search_standards", query="Python SDK testing standards")` → (to be ported)
3. **Understand environment setup** → `pos_search_project(action="search_standards", query="Python SDK environment setup")` → `standards/development/environment/setup.md`
4. **Learn quality standards** → `pos_search_project(action="search_standards", query="Python SDK code quality")` → (to be ported)

**Universal Testing Standards:**
- `standards/universal/testing/integration-testing.md` → `pos_search_project(action="search_standards", query="integration testing best practices")`
- `standards/universal/testing/test-doubles.md` → `pos_search_project(action="search_standards", query="test doubles mocking")`
- `standards/universal/testing/test-pyramid.md` → `pos_search_project(action="search_standards", query="test pyramid strategy")`

---

## Validation Checklist

Before marking test execution as complete:

- [ ] Tests run using `tox` (not pytest directly)
- [ ] Unit tests passing (`tox -e unit`)
- [ ] Integration tests passing (if applicable)
- [ ] Code formatted (`tox -e format`)
- [ ] Linting passes (`tox -e lint`)
- [ ] Coverage meets threshold (≥80%)
- [ ] All Python versions tested (if release)
- [ ] Environment variables configured (if needed)

---

**💡 Key Principle**: Consistent test execution through tox ensures reliable, reproducible results across all environments.


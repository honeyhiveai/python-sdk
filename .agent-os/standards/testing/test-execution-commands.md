# Test Execution Commands

**🎯 Comprehensive guide to running tests in the HoneyHive Python SDK**

## 🚨 **MANDATORY: Use Tox - Never Pytest Directly**

**ALWAYS use tox for running tests - NEVER run pytest directly**

### **Why Tox is Required**
- **Environment Isolation**: Tests run in clean, isolated environments
- **Dependency Management**: Ensures correct package versions
- **Consistency**: Same commands work across all development environments
- **CI/CD Compatibility**: Matches production testing pipeline

## 🚀 **Core Test Commands**

### **Unit Tests**
```bash
# Run all unit tests (fast, isolated)
tox -e unit

# Run specific unit test file
tox -e unit -- tests/unit/test_specific_file.py

# Run specific test class
tox -e unit -- tests/unit/test_file.py::TestClassName

# Run specific test method
tox -e unit -- tests/unit/test_file.py::TestClassName::test_method_name
```

### **Integration Tests**
```bash
# Run all integration tests (real APIs, end-to-end)
tox -e integration

# Run specific integration test
tox -e integration -- tests/integration/test_specific.py
```

### **Quality Checks**
```bash
# Format code with Black
tox -e format

# Run pylint and mypy analysis
tox -e lint

# Combined format and lint
tox -e format && tox -e lint
```

### **Python Version Testing**
```bash
# Test with specific Python versions
tox -e py311           # Python 3.11 specific tests
tox -e py312           # Python 3.12 specific tests  
tox -e py313           # Python 3.13 specific tests

# Test across all supported versions
tox -e py311,py312,py313
```

## ⚡ **Parallel Execution**

### **Parallel Test Execution**
```bash
# Run multiple environments in parallel
tox -p auto -e unit,integration    # Auto-detect CPU cores
tox -p 4 -e unit,integration       # Use 4 parallel processes

# Integration tests with pytest-xdist
tox -e integration-parallel        # Uses pytest -n auto --dist=worksteal
```

### **Parallel Configuration**
```bash
# Manual parallel execution (if needed)
pytest tests/integration/ -n auto --dist=worksteal  # Auto worker count
pytest tests/integration/ -n 4 --dist=each         # 4 workers, load balancing
```

## 🎯 **Targeted Testing Commands**

### **File-Specific Testing**
```bash
# Test single file with full output
tox -e unit -- tests/unit/test_tracer_processing_context.py -v

# Test single file with short output
tox -e unit -- tests/unit/test_tracer_processing_context.py -q

# Test single file with maximum verbosity
tox -e unit -- tests/unit/test_tracer_processing_context.py -vvv
```

### **Pattern-Based Testing**
```bash
# Test files matching pattern
tox -e unit -- tests/unit/test_tracer_*.py

# Test methods matching pattern
tox -e unit -- -k "test_process"

# Test specific markers
tox -e unit -- -m "not slow"
```

### **Debugging Commands**
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

## 📊 **Coverage Commands**

### **Coverage Generation**
```bash
# Generate coverage report
tox -e coverage

# Generate HTML coverage report
tox -e coverage-html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### **Coverage Analysis**
```bash
# Show coverage for specific file
coverage report --include="tests/unit/test_file.py"

# Show missing lines
coverage report --show-missing

# Generate coverage data only
coverage run -m pytest tests/unit/
```

## 🔧 **Development Workflow Commands**

### **Pre-Commit Workflow**
```bash
# Standard development workflow
tox -e format          # Format code
tox -e lint            # Check quality
tox -e unit            # Run unit tests
tox -e integration     # Run integration tests (if needed)
```

### **Quick Development Cycle**
```bash
# Fast feedback loop for active development
tox -e unit -- tests/unit/test_current_file.py -v

# Format and test specific file
tox -e format && tox -e unit -- tests/unit/test_file.py
```

### **Full Validation**
```bash
# Complete validation before commit
tox -e format,lint,unit,integration

# Parallel full validation (faster)
tox -p auto -e format,lint,unit,integration
```

## 🚨 **CI/CD Commands**

### **Continuous Integration**
```bash
# Commands used in CI/CD pipeline
tox -e format          # Code formatting check
tox -e lint            # Quality analysis
tox -e unit            # Unit test execution
tox -e integration     # Integration test execution
tox -e coverage        # Coverage reporting
```

### **Release Validation**
```bash
# Full release validation
tox -e py311,py312,py313,format,lint,coverage

# Parallel release validation
tox -p auto -e py311,py312,py313,format,lint,coverage
```

## 🎛️ **Advanced Options**

### **Environment Variables**
```bash
# Set test environment variables
HH_TEST_MODE=true tox -e unit
HH_API_KEY=test-key tox -e integration

# Use .env file for local development
cp env.integration.example .env
tox -e integration
```

### **Verbose Output Control**
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

### **Test Selection**
```bash
# Run only failed tests from last run
tox -e unit -- --lf

# Run failed tests first, then others
tox -e unit -- --ff

# Run tests that changed since last commit
tox -e unit -- --testmon
```

## 📋 **Command Reference**

### **Essential Commands**
| Command | Purpose | When to Use |
|---------|---------|-------------|
| `tox -e unit` | Run unit tests | Development, quick feedback |
| `tox -e integration` | Run integration tests | Feature validation |
| `tox -e format` | Format code | Before committing |
| `tox -e lint` | Quality checks | Before committing |
| `tox -e coverage` | Coverage report | Quality assessment |

### **Development Commands**
| Command | Purpose | When to Use |
|---------|---------|-------------|
| `tox -e unit -- file.py` | Test specific file | Active development |
| `tox -e unit -- -k pattern` | Test by pattern | Feature-specific testing |
| `tox -e unit -- -x` | Stop on first failure | Debugging |
| `tox -e unit -- -s` | Show print output | Debugging |

### **Quality Commands**
| Command | Purpose | When to Use |
|---------|---------|-------------|
| `tox -e format,lint` | Format and check quality | Pre-commit |
| `tox -p auto -e unit,integration` | Parallel testing | Full validation |
| `tox -e py311,py312,py313` | Multi-version testing | Release preparation |

## 💡 **Best Practices**

### **Development Workflow**
1. **Start with unit tests** - fast feedback loop
2. **Format regularly** - maintain code quality
3. **Run integration tests** - validate end-to-end functionality
4. **Check coverage** - ensure adequate test coverage

### **Debugging Workflow**
1. **Run specific test** - isolate the issue
2. **Use verbose output** - understand what's happening
3. **Add debugging flags** - get detailed information
4. **Test incrementally** - verify fixes step by step

### **Performance Optimization**
1. **Use parallel execution** - faster test runs
2. **Target specific tests** - avoid running unnecessary tests
3. **Use test patterns** - run related tests together
4. **Optimize test data** - reduce setup/teardown time

---

**💡 Key Principle**: Consistent test execution through tox ensures reliable, reproducible results across all environments.

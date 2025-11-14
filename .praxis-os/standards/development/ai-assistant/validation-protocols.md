# AI Assistant Validation Protocols

**🎯 Comprehensive validation protocols for AI assistants to ensure consistent, high-quality output**

This document defines the mandatory validation steps that AI assistants must execute before generating any code, fixing tests, or making changes to the HoneyHive Python SDK.

## 🚨 **CRITICAL: Pre-Generation Validation Protocol**

**MANDATORY: Execute ALL steps before generating ANY code**

### **Step 1: Environment Validation**
```bash
# MUST run this exact block before any work
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"
python --version  # Verify Python 3.11+
which python      # Verify virtual environment active
```

**Validation Checklist:**
- [ ] **Working directory**: Confirmed in project root
- [ ] **Virtual environment**: Active and correct (`python-sdk`)
- [ ] **Python version**: 3.11 or higher
- [ ] **Current date**: Retrieved and available as `$CURRENT_DATE`

### **Step 2: Codebase State Validation**
```bash
# Verify current codebase state
git status --porcelain                    # Must be clean working directory
git branch --show-current                # Verify correct branch
git log --oneline -5                     # Check recent commits
```

**Validation Checklist:**
- [ ] **Clean state**: No uncommitted changes (`git status --porcelain` empty)
- [ ] **Correct branch**: On intended branch (usually `main` or feature branch)
- [ ] **Recent history**: Aware of recent changes

### **Step 3: API and Import Validation**
```bash
# Verify current API structure and imports
read_file src/honeyhive/__init__.py      # Check current API exports
grep -r "class.*Tracer" src/honeyhive/   # Verify tracer class names
grep -r "from honeyhive import" examples/ # Check import patterns
grep -r "EventType\." src/honeyhive/     # Verify enum usage patterns
```

**Validation Checklist:**
- [ ] **API exports**: Current `__init__.py` structure understood
- [ ] **Class names**: Verified current class and method names
- [ ] **Import patterns**: Confirmed correct import syntax
- [ ] **Enum usage**: Verified EventType patterns

### **Step 4: Configuration Structure Validation**
```bash
# Understand current config architecture
read_file src/honeyhive/config/utils.py  # Check config creation logic
grep -r "config\." src/honeyhive/        # Verify config access patterns
grep -r "tracer\.config" tests/          # Check test config usage
```

**Validation Checklist:**
- [ ] **Config structure**: Understood nested vs flat config access
- [ ] **Access patterns**: Verified correct config attribute access
- [ ] **Test patterns**: Confirmed how tests access config values

## 🔍 **Context-Specific Validation Protocols**

### **For Test Fixing Tasks**

#### **Production Code Analysis Protocol**
```bash
# MANDATORY: Understand production code before fixing tests
read_file src/honeyhive/path/to/module.py  # Read code being tested
grep -r "def method_name" src/honeyhive/   # Find method signatures
grep -r "class ClassName" src/honeyhive/   # Find class definitions
grep -A10 -B5 "method_name" src/honeyhive/path/to/module.py  # Context around method
```

**Analysis Checklist:**
- [ ] **Function signatures**: Understood parameters, types, return values
- [ ] **Dependencies**: Identified imports and external calls
- [ ] **Error handling**: Noted exception types and patterns
- [ ] **Configuration usage**: Verified config access patterns
- [ ] **Business logic**: Understood core functionality

#### **Test Structure Analysis Protocol**
```bash
# Understand current test structure and patterns
read_file tests/unit/test_target_file.py  # Read failing test file
grep -r "@patch" tests/unit/test_target_file.py  # Find mock decorators
grep -r "Mock" tests/unit/test_target_file.py    # Find mock usage
grep -r "fixture" tests/conftest.py              # Check available fixtures
```

**Test Analysis Checklist:**
- [ ] **Mock patterns**: Understood @patch decorator usage and injection
- [ ] **Fixture usage**: Verified available fixtures and their structure
- [ ] **Assertion patterns**: Confirmed expected vs actual value logic
- [ ] **Type annotations**: Checked current test type annotation patterns

### **For Code Generation Tasks**

#### **Architecture Pattern Validation**
```bash
# Verify current architectural patterns
grep -r "graceful" src/honeyhive/        # Check error handling patterns
grep -r "safe_log" src/honeyhive/        # Verify logging utility usage
grep -r "keyword.*only" src/honeyhive/   # Check keyword-only argument usage
grep -r "Optional\[" src/honeyhive/      # Verify type annotation patterns
```

**Architecture Checklist:**
- [ ] **Error handling**: Confirmed graceful degradation patterns
- [ ] **Logging**: Verified safe_log utility usage
- [ ] **Function signatures**: Understood keyword-only argument patterns
- [ ] **Type safety**: Confirmed current type annotation standards

#### **Documentation Pattern Validation**
```bash
# Verify current documentation patterns
grep -A20 '""".*\.' src/honeyhive/      # Check docstring patterns
grep -r ":param:" src/honeyhive/        # Verify Sphinx parameter format
grep -r ".. code-block::" docs/         # Check example formatting
```

**Documentation Checklist:**
- [ ] **Docstring format**: Confirmed Sphinx compatibility requirements
- [ ] **Parameter documentation**: Verified `:param:` and `:type:` usage
- [ ] **Examples**: Understood code block formatting requirements

## ⚡ **Quality Gate Pre-Validation**

### **Pre-Change Quality Check**
```bash
# Verify current quality state before making changes
tox -e format --check    # Check current formatting state
tox -e lint --quiet      # Check current linting state (may have existing issues)
python -m mypy src/ --show-error-codes  # Check current type checking state
```

**Quality State Checklist:**
- [ ] **Formatting baseline**: Understood current formatting state
- [ ] **Linting baseline**: Aware of existing linting issues
- [ ] **Type checking baseline**: Confirmed current mypy state
- [ ] **Test baseline**: Verified current test pass/fail state

### **Dependency and Import Verification**
```bash
# Verify all necessary imports and dependencies
grep -r "from typing import" src/honeyhive/  # Check typing imports
grep -r "from unittest.mock import" tests/   # Check mock imports
pip list | grep -E "(pytest|mypy|pylint|black)"  # Verify tool availability
```

**Dependency Checklist:**
- [ ] **Typing imports**: Confirmed available typing constructs
- [ ] **Test dependencies**: Verified pytest and mock availability
- [ ] **Quality tools**: Confirmed pylint, mypy, black availability

## 🎯 **Task-Specific Validation Workflows**

### **Workflow 1: Test Debugging and Fixing**
```bash
# Complete validation workflow for test fixing
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate

# 1. Environment validation
CURRENT_DATE=$(date +"%Y-%m-%d")
python --version && which python

# 2. Identify failing test
python -m pytest tests/unit/test_specific_file.py::TestClass::test_method -v

# 3. Analyze production code
read_file src/honeyhive/path/to/module.py

# 4. Analyze test structure
read_file tests/unit/test_specific_file.py

# 5. Verify config patterns
grep -r "config\." src/honeyhive/path/to/module.py

# 6. Check mock patterns
grep -A5 -B5 "@patch" tests/unit/test_specific_file.py
```

### **Workflow 2: New Code Generation**
```bash
# Complete validation workflow for code generation
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate

# 1. Environment validation
CURRENT_DATE=$(date +"%Y-%m-%d")
git status --porcelain

# 2. API structure validation
read_file src/honeyhive/__init__.py

# 3. Pattern validation
grep -r "def.*\*," src/honeyhive/  # Keyword-only patterns
grep -r "safe_log" src/honeyhive/  # Logging patterns

# 4. Type annotation validation
grep -r "-> " src/honeyhive/ | head -10  # Return type patterns

# 5. Documentation validation
grep -A10 '"""' src/honeyhive/ | head -20  # Docstring patterns
```

### **Workflow 3: Documentation Updates**
```bash
# Complete validation workflow for documentation
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate

# 1. Current documentation state
cd docs && make html 2>&1 | tail -20  # Check build warnings
cd ..

# 2. Example validation
grep -r "EventType\." docs/  # Verify enum usage in examples
grep -r "from honeyhive import" docs/  # Check import patterns

# 3. Cross-reference validation
grep -r "\.rst" docs/ | grep -v "_build"  # Find internal references
```

## 🚨 **Validation Failure Protocols**

### **When Validation Fails**

#### **Environment Issues**
```bash
# If environment validation fails:
deactivate  # Exit current environment
rm -rf python-sdk/  # Remove corrupted environment
python -m venv python-sdk  # Recreate environment
source python-sdk/bin/activate
pip install -e .  # Reinstall in development mode
```

#### **Codebase State Issues**
```bash
# If codebase state validation fails:
git stash  # Stash uncommitted changes
git status --porcelain  # Verify clean state
git checkout main  # Switch to stable branch
git pull origin main  # Get latest changes
```

#### **Import/API Issues**
```bash
# If import validation fails:
python -c "import honeyhive; print(dir(honeyhive))"  # Test imports
python -c "from honeyhive import HoneyHiveTracer"    # Test specific imports
grep -r "HoneyHiveTracer" src/honeyhive/__init__.py  # Verify exports
```

## 📋 **Validation Completion Checklist**

**Before proceeding with ANY task, ALL items must be ✅:**

### **Environment Validation Complete**
- [ ] **Working directory**: Confirmed in project root
- [ ] **Virtual environment**: Active and functional
- [ ] **Python version**: 3.11+ verified
- [ ] **Current date**: Available as `$CURRENT_DATE`

### **Codebase Validation Complete**
- [ ] **Clean state**: No uncommitted changes
- [ ] **Correct branch**: On intended branch
- [ ] **API structure**: Current exports understood
- [ ] **Import patterns**: Verified and confirmed

### **Context Validation Complete**
- [ ] **Production code**: Read and understood (for test fixes)
- [ ] **Architecture patterns**: Current patterns identified
- [ ] **Configuration structure**: Nested config access confirmed
- [ ] **Quality baseline**: Current state assessed

### **Task-Specific Validation Complete**
- [ ] **Specific workflow**: Appropriate workflow executed
- [ ] **Dependencies**: All required tools available
- [ ] **Patterns**: Relevant patterns identified and understood
- [ ] **Examples**: Current example patterns confirmed

## 🔗 **Related Protocols**

- **[Quality Framework](quality-framework.md)** - Overall quality requirements and gates
- **[Code Generation Patterns](code-generation-patterns.md)** - Specific code templates and patterns
- **[Debugging Methodology](../testing/debugging-methodology.md)** - Systematic test debugging process
- **[Git Safety Rules](git-safety-rules.md)** - Safe git operations and forbidden commands

---

**📝 Next Steps**: After completing validation, proceed with [Code Generation Patterns](code-generation-patterns.md) or [Debugging Methodology](../testing/debugging-methodology.md) as appropriate.

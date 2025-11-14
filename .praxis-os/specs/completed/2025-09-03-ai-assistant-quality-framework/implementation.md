# AI Assistant Quality Framework - Implementation Guide

**Date**: 2025-09-03
**Target**: AI Assistants working on HoneyHive Python SDK
**Purpose**: Autonomous quality assurance and testing

## Pre-Code Generation Checklist

**MANDATORY**: Execute these commands before writing ANY code:

### 1. Environment Validation
```bash
# Verify clean state
git status --porcelain
git branch --show-current

# Check current directory
pwd  # Should be /path/to/honeyhive-python-sdk
ls -la  # Verify project structure exists
```

### 2. API State Validation
```bash
# Validate current API exports
read_file src/honeyhive/__init__.py

# Check import patterns in examples
grep -r "from honeyhive import" examples/ | head -10

# Verify class definitions
grep -r "class.*:" src/honeyhive/ | head -10

# Check test patterns
grep -r "import.*honeyhive" tests/ | head -5
```

### 3. Testing Environment Check
```bash
# Verify tox is available
tox --version

# Check Python versions
python --version
python3.11 --version || echo "Python 3.11 not available"
python3.12 --version || echo "Python 3.12 not available"
python3.13 --version || echo "Python 3.13 not available"
```

## Code Generation Protocol

### Phase 1: Implementation
1. **Write Feature Code**: Implement the requested functionality
2. **Follow Patterns**: Use existing codebase patterns and conventions
3. **Type Safety**: Include proper type annotations
4. **Documentation**: Add docstrings and inline comments

### Phase 2: Test Generation
1. **Unit Tests**: Create comprehensive unit tests
2. **Integration Tests**: Add integration tests if needed
3. **Edge Cases**: Test error conditions and edge cases
4. **Backward Compatibility**: Ensure existing functionality still works

### Phase 3: Documentation Updates
1. **API Documentation**: Update docstrings and type hints
2. **Examples**: Create or update usage examples
3. **Changelog**: Add entry to CHANGELOG.md
4. **Feature Documentation**: Update relevant .md files

## Quality Validation Sequence

**MANDATORY**: Run in this exact order, ALL must pass:

### 1. Code Quality Checks
```bash
# Format code
tox -e format
echo "Exit code: $?"  # Must be 0

# Lint code
tox -e lint  
echo "Exit code: $?"  # Must be 0
```

### 2. Testing Validation
```bash
# Unit tests
tox -e unit
echo "Exit code: $?"  # Must be 0

# Integration tests  
tox -e integration
echo "Exit code: $?"  # Must be 0

# Python version compatibility
tox -e py311
echo "Exit code: $?"  # Must be 0

tox -e py312  
echo "Exit code: $?"  # Must be 0

tox -e py313
echo "Exit code: $?"  # Must be 0
```

### 3. Documentation Validation
```bash
# Build documentation
cd docs
make html 2>&1 | tee build.log
echo "Exit code: $?"  # Must be 0

# Check for warnings
grep -i "warning\|error" build.log
# Should return empty or acceptable warnings only

cd ..
```

### 4. Example Validation
```bash
# Test examples work
python examples/basic_usage.py || echo "Basic example failed"
python examples/advanced_usage.py || echo "Advanced example failed"

# Test doctest examples
python -m doctest examples/*.py
echo "Exit code: $?"  # Must be 0
```

## Failure Resolution Protocol

### When Tests Fail

**NEVER commit failing tests. Fix them immediately.**

#### Common Failure Types and Solutions:

1. **Import Errors**
   ```python
   # Fix: Update import statements
   # Check current exports in __init__.py
   # Use correct class/function names
   ```

2. **Type Errors**
   ```python
   # Fix: Add missing type annotations
   # Use proper EventType enums
   # Import required types
   ```

3. **Formatting Errors**
   ```bash
   # Fix: Apply automatic formatting
   tox -e format
   ```

4. **Lint Errors**
   ```python
   # Fix common issues:
   # - Add docstrings
   # - Fix unused imports
   # - Resolve naming conventions
   # - Fix line length issues
   ```

5. **Test Coverage Issues**
   ```python
   # Fix: Add missing tests for uncovered lines
   # Check coverage report
   # Write tests for edge cases
   ```

### When Documentation Fails

1. **Sphinx Warnings**
   ```rst
   # Fix common RST issues:
   # - Title underline length
   # - Missing blank lines  
   # - Broken cross-references
   # - Malformed tables
   ```

2. **Example Failures**
   ```python
   # Fix: Ensure examples use current API
   # Update import statements
   # Use correct EventType enums
   # Test examples locally
   ```

## Autonomous Decision Matrix

### Fix Automatically
- **Formatting issues**: Apply black/isort
- **Simple import errors**: Update import statements
- **Missing docstrings**: Add basic docstrings
- **Type annotation gaps**: Add simple type hints

### Fix with Validation
- **Test failures**: Write additional tests, verify coverage
- **Lint issues**: Refactor code, improve structure
- **Documentation errors**: Update RST, fix cross-references
- **Example failures**: Update to use current API

### Escalate to Human
- **Architecture changes**: Major structural modifications
- **Complex failures**: Cannot resolve after 3 attempts  
- **Security issues**: Authentication or data protection
- **Performance problems**: Significant resource impact

## Commit and Push Protocol

### Pre-Commit Validation
```bash
# Final validation before commit
tox -e format && echo "Format: PASS" || echo "Format: FAIL"
tox -e lint && echo "Lint: PASS" || echo "Lint: FAIL"  
tox -e unit && echo "Unit Tests: PASS" || echo "Unit Tests: FAIL"
tox -e integration && echo "Integration: PASS" || echo "Integration: FAIL"

# All must show "PASS" before proceeding
```

### Commit Message Format
```
type: brief description

- Detailed change 1
- Detailed change 2  
- Detailed change 3

Tests: All passing (unit, integration, py311-313)
Coverage: Maintained/Improved
Docs: Updated/Built successfully
```

### Push Validation
```bash
# Only push if all validations pass
git add -A
git commit -m "descriptive message"
git push origin branch-name
```

## Success Metrics

### Quality Gates
- [ ] 100% of tests passing
- [ ] Code coverage ≥70% (≥80% for new code)  
- [ ] Pylint score ≥8.0/10.0
- [ ] Zero Sphinx warnings
- [ ] All examples execute successfully

### Development Efficiency
- [ ] First-pass success rate >90%
- [ ] Fix time <30 minutes per failure
- [ ] Zero regressions introduced
- [ ] Documentation always up-to-date

### User Experience
- [ ] API consistency maintained
- [ ] Backward compatibility preserved
- [ ] Clear error messages
- [ ] Complete usage examples

## Continuous Improvement

### After Each Session
1. **Review Failures**: Document what went wrong
2. **Update Patterns**: Improve prevention mechanisms
3. **Optimize Process**: Reduce validation time
4. **Share Learnings**: Update documentation

### Weekly Assessment
1. **Analyze Metrics**: Success rates, failure types
2. **Update Framework**: Improve automation
3. **Refine Standards**: Adjust quality thresholds
4. **Train Models**: Update AI assistant capabilities

## Framework Evolution

This framework should continuously evolve based on:
- **Performance Data**: Success/failure rates, timing metrics
- **Developer Feedback**: Human oversight insights
- **Technology Changes**: New tools, updated standards
- **Project Growth**: Scaling requirements, complexity increases

**Next Review**: Weekly during initial implementation, monthly thereafter
**Update Frequency**: As needed based on failure patterns
**Success Threshold**: >95% autonomous success rate for routine tasks

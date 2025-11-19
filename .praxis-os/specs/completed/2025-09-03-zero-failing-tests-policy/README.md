# Zero Failing Tests Policy - HoneyHive Python SDK

**Date**: 2025-09-03
**Status**: Active
**Scope**: All AI Assistant interactions with HoneyHive Python SDK

## Overview

This specification establishes a **Zero Failing Tests Policy** for the HoneyHive Python SDK project to ensure AI assistants ship production-quality code without human intervention.

## Problem Statement

Recent development on the `complete-refactor` branch revealed that failing tests were committed and pushed, creating workflow failures and potentially unstable code. This violates software engineering best practices and creates technical debt.

## Solution

Implement a **Zero Failing Tests Policy** that requires ALL commits to have 100% passing tests before they can be committed to ANY branch.

## Key Principles

1. **Zero Tolerance**: No failing tests are allowed in any commit
2. **No Exceptions**: This applies to ALL branches, including development branches
3. **Immediate Fix**: Any failing tests must be fixed before new work begins
4. **Comprehensive Coverage**: All test types must pass (unit, integration, linting, formatting)
5. **❌ NO SKIPPING TESTS**: AI assistants MUST fix failing tests, never skip them
6. **Fix Root Cause**: Address the underlying issue, not just the symptom

## Implementation

### Mandatory Testing Process

**Before EVERY commit:**
```bash
# All of these MUST pass 100%
tox -e unit           # Unit tests
tox -e integration    # Integration tests  
tox -e lint          # Code quality checks
tox -e format        # Code formatting checks
tox -e py311 -e py312 -e py313  # Python version compatibility
```

### Enforcement Mechanisms

1. **Pre-commit Hooks**: Automated test execution
2. **CI/CD Blocking**: GitHub Actions will block merges
3. **Documentation**: Clear standards in Agent OS specs
4. **Training**: Developer education on testing practices

### Development Workflow

#### For New Features
1. Write feature code
2. Write comprehensive tests
3. Verify all tests pass locally
4. Commit only after 100% test success
5. Push to branch

#### For Bug Fixes
1. Write test that reproduces bug
2. Verify test fails (confirms bug exists)
3. Fix the bug
4. Verify test now passes
5. Verify no regression (all other tests pass)
6. Commit

#### For Refactoring
1. Ensure all existing tests pass
2. Perform refactoring
3. Verify all tests still pass
4. Update tests if needed (but don't remove coverage)
5. Commit

### Emergency Procedures

#### If Tests Fail After Commit
1. **Stop all new work immediately**
2. **Revert the failing commit**
3. **Fix tests locally**
4. **Re-commit only after all tests pass**
5. **Conduct post-mortem to prevent recurrence**

#### For Critical Hotfixes
- All testing requirements still apply
- No exceptions for "urgent" fixes
- Use expedited review process, not skipped testing

### ❌ PROHIBITED: Test Skipping Policy

**AI assistants are STRICTLY FORBIDDEN from skipping failing tests.**

#### What is NOT Allowed
```python
# ❌ FORBIDDEN - Do not add skip decorators
@pytest.mark.skip(reason="Temporarily skipped - will fix later")
def test_failing_function():
    pass

# ❌ FORBIDDEN - Do not disable tests in tox.ini
# -e unit-skip-broken

# ❌ FORBIDDEN - Do not comment out test functions
# def test_broken():
#     assert something_that_fails()
```

#### What IS Required
```python
# ✅ REQUIRED - Fix the underlying issue
def test_failing_function():
    # Proper mock setup that works
    with patch("module.Class", MagicMock()) as mock_class:
        mock_class.return_value = Mock()
        result = function_under_test()
        assert result == expected_value
```

#### When Tests Fail: Mandatory Process
1. **Investigate Root Cause**: Understand WHY the test is failing
2. **Fix the Implementation**: Address the underlying bug or mock setup
3. **Validate the Fix**: Ensure test passes and doesn't break others
4. **Never Skip**: Skipping tests hides problems and creates technical debt

#### Escalation Protocol
**If AI assistant cannot fix failing tests after 3 attempts:**
- Document the specific error and investigation attempts
- Escalate to human developer for guidance
- Do NOT skip the tests as a workaround

## Impact Assessment

### Benefits
- **Higher Code Quality**: Prevents broken code from entering codebase
- **Faster Development**: Reduces debugging time and rework
- **Better User Experience**: More stable and reliable SDK
- **Improved Developer Confidence**: Trust in codebase stability
- **Reduced Technical Debt**: Prevents accumulation of broken functionality

### Implementation Cost
- **Initial Setup**: Update documentation and processes (1-2 days)
- **Developer Training**: Education on new requirements (ongoing)
- **Slight Workflow Overhead**: Additional testing time per commit
- **Tool Updates**: Enhanced pre-commit hooks and CI/CD

## Success Metrics

- **Zero failing tests** in any commit across all branches
- **Reduced bug reports** from users
- **Faster feature development** due to fewer debugging cycles
- **Improved test coverage** across codebase
- **Higher developer satisfaction** with code quality

## References

- `.praxis-os/standards/best-practices.md` - Updated testing standards
- `.praxis-os/standards/tech-stack.md` - Testing framework requirements
- `tox.ini` - Testing environment configuration
- `.github/workflows/` - CI/CD testing automation

## Enforcement Date

**Effective Immediately**: All new commits must comply with Zero Failing Tests Policy

## Review and Updates

This policy will be reviewed quarterly and updated as needed based on:
- Developer feedback
- Tool improvements
- Process optimization opportunities
- Project evolution needs

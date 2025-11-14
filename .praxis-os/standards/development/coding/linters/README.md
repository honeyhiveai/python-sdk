# Linter-Specific Standards

**🎯 Detailed, tool-specific linting standards for AI assistants**

## 📁 **Directory Structure**

```
linters/
├── README.md                 # This file - overview
├── pylint/
│   ├── common-violations.md  # Most frequent Pylint errors
│   ├── function-rules.md     # Function-specific Pylint rules
│   ├── class-rules.md        # Class-specific Pylint rules
│   ├── import-rules.md       # Import-specific Pylint rules
│   └── test-rules.md         # Test-specific Pylint rules
├── mypy/
│   ├── type-annotations.md   # Type annotation requirements
│   ├── method-mocking.md     # Method mocking patterns
│   ├── generic-types.md      # Generic type usage
│   └── error-recovery.md     # Common MyPy error fixes
├── black/
│   ├── formatting-rules.md   # Black formatting requirements
│   └── line-length.md        # Line length management
└── isort/
    ├── import-sorting.md     # Import organization with isort
    └── import-groups.md      # Import grouping standards
```

## 🚨 **Critical Usage Pattern**

**AI assistants MUST:**

1. **Read the specific linter docs** before generating code
2. **Follow tool-specific patterns** exactly as documented
3. **Run validation immediately** after code generation
4. **Fix errors systematically** using the error recovery guides

**🔗 INTEGRATION WITH FRAMEWORK:**
- **Called from**: [../pre-generation-checklist.md](../pre-generation-checklist.md) - Step 1 of code generation
- **Called from**: [../tests/README.md](../tests/README.md) - Phase 0 validation
- **Next step**: Return to comprehensive analysis framework after reading linter docs

## 📋 **Linter Priority Order**

**Follow this order when addressing linting issues:**

1. **Black** - Formatting first (auto-fixes most issues)
2. **isort** - Import sorting and organization
3. **MyPy** - Type safety (CRITICAL for correctness - catch early!)
4. **Pylint** - Code quality and style (cosmetic issues last)

## 🎯 **Quick Reference**

### **Most Critical Rules**
- **Pylint**: ≤5 positional args, no unused imports, proper docstrings, `assert not result` not `assert result == {}`
- **MyPy**: Complete type annotations, use `patch.object` for method mocking, check return types (`-> None` vs actual returns)
- **Black**: ≤88 char lines, consistent formatting, no trailing whitespace
- **isort**: Sorted imports, proper import grouping

### **Emergency Fixes**
- **Line too long**: Break into multiple lines or use Black (especially docstrings)
- **Cannot assign to method**: Use `patch.object` context manager
- **Unused import**: Remove unused imports (uuid, pytest if not used)
- **Missing docstring**: Add proper Sphinx-style docstring
- **Unused mock argument**: Either use mock or prefix with `_`
- **Need type annotation**: Add `attributes: Dict[str, Any] = {}` for empty containers
- **Method returns None**: Don't assign return value, just call method
- **Unnecessary lambda**: Use direct function reference for `side_effect`

---

**🎯 Remember**: Each linter subdirectory contains focused, actionable guidance for preventing specific errors.

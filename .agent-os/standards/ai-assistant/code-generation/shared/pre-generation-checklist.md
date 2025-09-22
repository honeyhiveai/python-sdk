# Pre-Generation Checklist

**🚨 MANDATORY: Complete this checklist BEFORE writing ANY code**

## ⚡ **30-Second Pre-Generation Validation**

**AI assistants MUST complete ALL items before proceeding:**

### **📋 Environment Validation**
- [ ] **Virtual environment active**: `which python` shows project venv
- [ ] **Current date obtained**: `CURRENT_DATE=$(date +"%Y-%m-%d")`
- [ ] **Working directory correct**: In project root
- [ ] **Git status clean**: No uncommitted changes that would interfere

### **📖 Production Code Analysis**
- [ ] **Read target production code**: Understand what you're testing/implementing
- [ ] **Identify dependencies**: Note all imports and function calls needed
- [ ] **Understand error patterns**: Note exception types and handling
- [ ] **Check configuration usage**: Understand config access patterns

### **📦 Import Planning (WRITE DOWN EXACT LIST)** 
- [ ] **List EXACT imports needed**: Write the actual import statements you'll use
- [ ] **Verify import paths**: Check current module structure
- [ ] **NO unused imports**: Every import MUST be used in the code
- [ ] **Typing imports**: Only import types you'll actually use (List, Dict, etc.)

**MANDATORY: Write your import list here before coding:**
```python
# Standard library imports I will use:
# from typing import [ONLY WHAT I NEED]
# from unittest.mock import [ONLY WHAT I NEED]

# Third-party imports I will use:
# import pytest

# Local imports I will use:
# from honeyhive.module import [ONLY WHAT I NEED]
```

### **🔧 Function Signature Planning**
- [ ] **Count parameters**: Ensure ≤5 positional arguments
- [ ] **Plan keyword-only**: Use `*,` if >3 parameters
- [ ] **Plan return types**: Complete type annotations for returns
- [ ] **Plan variable types**: Type annotations for ALL variables

### **📏 Formatting Planning (PREVENT VIOLATIONS)**
- [ ] **Line length strategy**: Plan to break long lines BEFORE writing them
- [ ] **NO trailing whitespace**: Be conscious of spaces at line ends
- [ ] **Function signature planning**: Long signatures will be multi-line with proper indentation
- [ ] **Docstring planning**: Plan Sphinx-compatible docstrings

**MANDATORY: Plan long line breaks before writing:**
```python
# If function signature will be >88 chars, plan multi-line format:
def long_function_name(
    param1: Type1,
    param2: Type2,
    *,
    param3: Type3 = default,
) -> ReturnType:
    """Docstring here."""
```

### **🧪 MyPy Compliance Planning (CRITICAL FOR TESTS)**
- [ ] **Method mocking strategy**: Will use patch.object, NOT direct assignment
- [ ] **Type annotation completeness**: All variables will have type annotations
- [ ] **Mock specifications**: Will use spec= for type safety
- [ ] **Import requirements**: Know exactly which types needed for annotations

## 🚨 **STOP: Do Not Proceed Until ALL Items Are Checked**

**If ANY item is unchecked, you are not ready to generate code.**

### **Quick Validation Commands**
```bash
# Run these to verify readiness
echo "Environment: $(which python)"
echo "Date: $(date +"%Y-%m-%d")"
echo "Directory: $(pwd)"
echo "Git status: $(git status --porcelain | wc -l) uncommitted files"
```

### **Production Code Analysis Template**
```bash
# MANDATORY: Read and understand production code first
read_file src/honeyhive/path/to/module.py
grep -r "class ClassName" src/honeyhive/
grep -r "def method_name" src/honeyhive/
grep -r "from honeyhive" tests/
```

## ✅ **Ready to Proceed**

**Once ALL items are checked, proceed to:**
- **🚨 MANDATORY FIRST: [linters/README.md](linters/README.md)** - Read linter documentation overview
- **🔧 [linters/pylint/](linters/pylint/)** - **EXPLORE ALL** Pylint docs (5 total) - prevent violations
- **⚫ [linters/black/](linters/black/)** - **EXPLORE ALL** Black docs (2 total) - prevent formatting issues  
- **🔍 [linters/mypy/](linters/mypy/)** - **EXPLORE ALL** MyPy docs (4 total) - prevent type errors
- **📊 MANDATORY METRICS COLLECTION** - Run pre-generation metrics BEFORE analysis
- **📋 [tests/README.md](tests/README.md)** - Then comprehensive analysis

### **🚨 MANDATORY: Pre-Generation Metrics Collection**

**BEFORE starting comprehensive analysis, MUST run:**
```bash
python scripts/test-generation-metrics.py \
  --test-file tests/unit/test_[TARGET_MODULE].py \
  --production-file src/[PRODUCTION_MODULE].py \
  --pre-generation \
  --output pre_generation_metrics_$(date +%Y%m%d_%H%M%S).json \
  --summary
```

**This creates baseline metrics for comparison and framework effectiveness measurement.**

---

**🎯 Goal**: Generate code that achieves 10/10 pylint and 0 mypy errors without post-generation fixes.

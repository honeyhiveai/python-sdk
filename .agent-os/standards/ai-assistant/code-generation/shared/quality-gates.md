# Quality Gates

**🎯 Mandatory validation after code generation**

## 🚨 **MANDATORY: Post-Generation Quality Gates**

**AI assistants MUST run ALL quality gates after generating code:**

### **Gate 1: Pylint Compliance (MUST be 10.00/10)**
```bash
# Check pylint score
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate
python -m pylint tests/unit/test_file.py --score=yes

# REQUIREMENT: Must show "Your code has been rated at 10.00/10"
# If not 10.00/10, code generation is INCOMPLETE
```

### **Gate 2: MyPy Type Checking (MUST be 0 errors)**
```bash
# Check mypy errors
python -m mypy tests/unit/test_file.py

# REQUIREMENT: Must show "Success: no issues found"
# If any errors, code generation is INCOMPLETE

# COMMON MYPY ERRORS TO WATCH FOR:
# - "Cannot assign to a method" → Use patch.object instead
# - "Missing type annotation" → Add type hints to all variables
# - "Incompatible return value type" → Fix fixture return types
```

### **Gate 3: Test Execution (MUST pass 100%)**
```bash
# Run the specific test file
python -m pytest tests/unit/test_file.py -v

# REQUIREMENT: All tests must pass
# If any failures, code generation is INCOMPLETE
```

### **Gate 4: Black Formatting (MUST be clean)**
```bash
# Check if Black would make changes
black --check tests/unit/test_file.py

# REQUIREMENT: Must show "would reformat 0 files"
# If reformatting needed, apply: black tests/unit/test_file.py
```

## 📋 **Quality Gate Execution Template**

**Copy-paste this exact sequence after generating ANY code:**

```bash
#!/bin/bash
# Quality Gate Validation Script
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source python-sdk/bin/activate

FILE="tests/unit/test_file.py"  # Replace with actual file

echo "🎯 Running Quality Gates for $FILE"

# Gate 1: Pylint
echo "Gate 1: Pylint Compliance..."
PYLINT_SCORE=$(python -m pylint "$FILE" --score=yes 2>&1 | grep "rated at" | grep -o "[0-9]\+\.[0-9]\+")
if [[ "$PYLINT_SCORE" == "10.00" ]]; then
    echo "✅ Pylint: $PYLINT_SCORE/10"
else
    echo "❌ Pylint: $PYLINT_SCORE/10 (MUST be 10.00)"
    exit 1
fi

# Gate 2: MyPy
echo "Gate 2: MyPy Type Checking..."
if python -m mypy "$FILE" > /dev/null 2>&1; then
    echo "✅ MyPy: 0 errors"
else
    echo "❌ MyPy: Has errors (MUST be 0)"
    python -m mypy "$FILE"
    exit 1
fi

# Gate 3: Tests
echo "Gate 3: Test Execution..."
if python -m pytest "$FILE" --tb=no -q > /dev/null 2>&1; then
    echo "✅ Tests: All passing"
else
    echo "❌ Tests: Some failing (MUST be 100%)"
    python -m pytest "$FILE" -v
    exit 1
fi

# Gate 4: Black
echo "Gate 4: Black Formatting..."
if black --check "$FILE" > /dev/null 2>&1; then
    echo "✅ Black: No formatting needed"
else
    echo "⚠️  Black: Applying formatting..."
    black "$FILE"
    echo "✅ Black: Formatting applied"
fi

echo "🏆 All Quality Gates PASSED!"
```

## 🚨 **Quality Gate Failure Protocol**

### **When Pylint Score < 10.00**
1. **Read pylint output** to identify specific violations
2. **Consult violation prevention guides**:
   - [pylint-violation-prevention.md](pylint-violation-prevention.md)
   - [parameter-planning.md](parameter-planning.md)
   - [import-planning.md](import-planning.md)
3. **Fix violations systematically** one by one
4. **Re-run pylint** until 10.00/10 achieved

### **When MyPy Has Errors**
1. **Read mypy output** to identify missing type annotations
2. **Consult type annotation guide**: [type-annotations.md](type-annotations.md)
3. **Add missing type annotations** for all variables and functions
4. **Re-run mypy** until 0 errors achieved

### **When Tests Fail**
1. **Read test output** to identify failure reasons
2. **Check production code** being tested for changes
3. **Update test logic** to match current production behavior
4. **Re-run tests** until 100% pass rate achieved

### **When Black Formatting Needed**
1. **Apply Black formatting**: `black file.py`
2. **Re-run quality gates** to ensure no new issues
3. **Verify formatting** doesn't break functionality

## 📊 **Quality Metrics Tracking**

### **Success Criteria**
- **Pylint**: Exactly 10.00/10 (no exceptions)
- **MyPy**: Exactly 0 errors (no exceptions)
- **Tests**: 100% pass rate (no exceptions)
- **Black**: No formatting changes needed

### **Quality Gate Report Template**
```
🎯 QUALITY GATE REPORT
File: tests/unit/test_file.py
Date: $(date +"%Y-%m-%d %H:%M:%S")

✅ Pylint: 10.00/10
✅ MyPy: 0 errors  
✅ Tests: 28/28 passing (100%)
✅ Black: No changes needed

🏆 STATUS: ALL GATES PASSED
```

## 🚨 **CRITICAL: No Exceptions Policy**

**AI assistants are FORBIDDEN from:**
- Accepting pylint scores < 10.00
- Accepting any mypy errors
- Accepting any test failures
- Skipping quality gate validation
- Using `# pylint: disable` without justification

**Quality gates are MANDATORY and MUST ALL PASS before code is considered complete.**

---

**📝 Next**: [failure-recovery.md](failure-recovery.md) - What to do when quality gates fail

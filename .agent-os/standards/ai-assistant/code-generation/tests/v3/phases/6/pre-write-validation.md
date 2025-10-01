# Phase 6.5: Pre-Write Standards Validation

**🎯 CRITICAL: Validate generated code against loaded standards BEFORE writing file**

⚠️ **MANDATORY CHECKPOINT**: This phase executes AFTER Phase 6 test planning, BEFORE Phase 7 file write

🚨 **FRAMEWORK-VIOLATION**: Writing test file without completing this validation

---

## ⛔ **ABSOLUTELY BLOCKING: CANNOT PROCEED WITHOUT POSTING VALIDATION**

### **🛑 MANDATORY REQUIREMENT: Post This In Chat Before Phase 7**

You **MUST** post the following validation results in chat before writing the test file:

```markdown
✅ PRE-WRITE VALIDATION COMPLETE - TASK-XXX

Validation 1 (Imports): PASS/FAIL - All imports at top of file using honeyhive.*
Validation 2 (Type Annotations): PASS/FAIL - All variables have type annotations
Validation 3 (Boolean Comparisons): PASS/FAIL - Using implicit booleanness (not ==)
Validation 4 (Pylint Disables): PASS/FAIL - Only approved disables used
Validation 5 (Mocking Boundaries): PASS/FAIL - Only external dependencies mocked
Validation 6 (Test Structure): PASS/FAIL - Organized with docstrings

Total Violations Detected: [N]
Total Violations Fixed: [N]

Ready to write: tests/unit/path/to/test_file.py
```

🚨 **IF VIOLATIONS > 0**: You MUST fix all violations BEFORE writing the file

🚨 **IF YOU DO NOT POST THIS**: You are violating the framework and bypassing critical quality gates

⛔ **NO EXCEPTIONS**: Even if you think the code is perfect, you MUST post the validation

---

## 🛑 **WHY THIS PHASE EXISTS**

**Problem Identified**: AI assistants consistently load standards in Phase 0, then violate them during generation.

**Evidence from TASK-013**:
- 8 standards files loaded in Phase 0 ✅
- ~180 violations of those standards in generated code ❌
- Pattern: Reading standards ≠ Applying standards

**Evidence from TASK-014**:
- Phase 6.5 checkpoint created from TASK-013 learnings ✅
- AI skipped Phase 6.5 entirely ❌
- 2 inline import violations occurred (same pattern as TASK-013) ❌
- Pattern: Checkpoints without enforcement = ignored checkpoints

**Solution**: Mandatory validation checkpoint that BLOCKS file write AND requires posting results in chat to make it truly enforceable.

---

## ⛔ **BLOCKING VALIDATION: CANNOT WRITE FILE WITHOUT PASSING**

### **Validation 1: Import Compliance**

🛑 **MANDATORY CHECK**: Review planned test file structure

**Question**: Where are imports located in your planned test file?

- [ ] ✅ **All imports at top of file** (lines 1-30)
- [ ] ❌ **Imports inside test methods** → VIOLATION

**If imports in methods detected**:
```
🚨 FRAMEWORK-VIOLATION: python-standards.md Section "Import Organization"
Fix: Move all imports to file top before writing
```

**Project Convention Check**:

- [ ] ✅ **Using `honeyhive.*` import paths** (e.g., `from honeyhive.tracer.X import Y`)
- [ ] ❌ **Using `src.honeyhive.*` import paths** → VIOLATION

**If `src.honeyhive.*` detected**:
```
🚨 PROJECT-CONVENTION-VIOLATION: Project uses honeyhive.* imports
Fix: Change all imports from src.honeyhive.* to honeyhive.*
```

---

### **Validation 2: Type Annotation Compliance**

🛑 **MANDATORY CHECK**: Review type annotations in test code

**Question**: Do ALL local variables in test methods have type annotations?

Example review:
```python
# ✅ CORRECT
def test_something(self):
    data: Dict[str, Any] = {...}
    result: str = function()

# ❌ VIOLATION
def test_something(self):
    data = {...}  # Missing type annotation
    result = function()  # Missing type annotation
```

**Checklist**:
- [ ] All local variables have type annotations
- [ ] All function parameters have type annotations
- [ ] All test methods have `-> None` return type
- [ ] Mock parameters annotated as `Mock`

**If missing annotations detected**:
```
🚨 FRAMEWORK-VIOLATION: type-annotations.md
Fix: Add type annotations to ALL variables before writing
```

---

### **Validation 3: Boolean Comparison Compliance**

🛑 **MANDATORY CHECK**: Review empty collection checks

**Question**: How are you checking for empty dicts/lists?

Example review:
```python
# ❌ VIOLATION
assert processor.stats == {}
assert processor.items == []
assert len(processor.stats) == 0

# ✅ CORRECT
assert not processor.stats
assert not processor.items
```

**Checklist**:
- [ ] Empty dict checks use `not dict_var` (not `== {}`)
- [ ] Empty list checks use `not list_var` (not `== []`)
- [ ] Length checks use appropriate patterns

**If `== {}` or `== []` detected**:
```
🚨 STYLE-VIOLATION: best-practices.md "Implicit Booleanness"
Fix: Change to implicit booleanness checks
```

---

### **Validation 4: Pylint Disable Compliance**

🛑 **MANDATORY CHECK**: Review planned Pylint disables

**Question**: What Pylint disables are you planning to use?

**File-Level Disables (Standard Header)**:
```python
# ✅ ALWAYS APPROVED
# pylint: disable=protected-access,too-many-lines,redefined-outer-name,too-many-public-methods,line-too-long,too-many-positional-arguments
# Justification: [proper justification text]
```

**Inline Disables (As Needed)**:
```python
# ✅ APPROVED AS NEEDED
mock_param: Mock,  # pylint: disable=unused-argument
```

**Never Approved**:
- ❌ `wrong-import-position` - Fix import order instead
- ❌ `missing-module-docstring` - Add docstring instead
- ❌ `import-outside-toplevel` - Move imports to top instead

**Checklist**:
- [ ] File-level disables match approved standard header
- [ ] No "never approved" disables used
- [ ] Inline disables only for approved patterns
- [ ] All disables have justification comments

**If unapproved disables detected**:
```
🚨 FRAMEWORK-VIOLATION: pre-approved-test-disables.md
Fix: Remove unapproved disables, fix underlying issues
```

---

### **Validation 5: Mocking Boundaries Compliance**

🛑 **MANDATORY CHECK**: Review what you're planning to mock

**Question**: List all items you plan to mock with `@patch` or `Mock()`:

**External Dependencies (MUST MOCK)**:
- [ ] Third-party libraries (time, Path, etc.)
- [ ] Cross-module imports (safe_log, bundle_loader, etc.)
- [ ] I/O operations

**Internal Code (NEVER MOCK)**:
- [ ] ❌ Methods of class under test
- [ ] ❌ Functions in same file
- [ ] ❌ Instance attributes

**Checklist**:
- [ ] No `@patch.object(ClassUnderTest, '_internal_method')` patterns
- [ ] All internal methods will execute naturally
- [ ] Only external dependencies are mocked

**If internal mocking detected**:
```
🚨 FRAMEWORK-VIOLATION: mocking-boundaries-reference.md
Fix: Remove internal method mocks, let code execute for coverage
```

---

### **Validation 6: Test Structure Compliance**

🛑 **MANDATORY CHECK**: Review test file organization

**Question**: How many test classes and tests are you generating?

**Expected Structure**:
```python
# ✅ CORRECT
class TestClassInit:
    """Test initialization methods."""
    def test_init_with_defaults(self): ...
    def test_init_with_custom(self): ...

class TestClassProcessing:
    """Test processing methods."""
    def test_process_valid_input(self): ...
```

**Checklist**:
- [ ] Tests organized into logical classes
- [ ] Each test class has docstring
- [ ] Each test method has docstring
- [ ] Test names use `test_methodname_scenario` pattern
- [ ] Module docstring at file top

**If structure violations detected**:
```
🚨 STYLE-VIOLATION: python-standards.md
Fix: Add missing docstrings, organize into classes
```

---

## 🛑 **SELF-CHECK: VALIDATE AGAINST PHASE 0 LOADED STANDARDS**

**Before proceeding to the final checklist, answer this question:**

**Q: "Did I validate this planned test code against ALL standards loaded in Phase 0?"**

Go through each standard file you loaded in Phase 0 and explicitly check:

- [ ] **Import organization standards** - Are ALL imports at the top of the file? (No inline imports)
- [ ] **Type annotation standards** - Do ALL variables have type annotations?
- [ ] **Boolean comparison standards** - Am I using implicit booleanness (not `== {}` or `== []`)?
- [ ] **Pylint disable standards** - Am I only using pre-approved disables?
- [ ] **Mocking boundaries standards** - Am I only mocking external dependencies?
- [ ] **Test structure standards** - Are tests organized in classes with docstrings?
- [ ] **String processing standards** - Am I using native Python operations instead of regex where appropriate?
- [ ] **MyPy type standards** - Have I avoided common type errors (empty containers, Mock types)?

⛔ **IF ANY ANSWER IS "NO" OR "I'M NOT SURE"**:
1. Stop immediately
2. Re-read the relevant Phase 0 standard
3. Fix the violation in your planned code
4. Return to this checklist

🚨 **COMMON AI FAILURE PATTERN**: Saying "yes, I checked" without actually reviewing the code against each standard

💡 **CORRECT APPROACH**: Actually scan through your planned code line-by-line for each standard

---

## 📋 **FINAL PRE-WRITE CHECKLIST**

⛔ **MUST COMPLETE BEFORE WRITING FILE**

```markdown
## Pre-Write Validation Complete

- [ ] ✅ Validation 1: Imports - All at top, using honeyhive.*
- [ ] ✅ Validation 2: Type Annotations - ALL variables annotated
- [ ] ✅ Validation 3: Boolean Comparisons - Using implicit booleanness
- [ ] ✅ Validation 4: Pylint Disables - Only approved disables
- [ ] ✅ Validation 5: Mocking Boundaries - Only external mocked
- [ ] ✅ Validation 6: Test Structure - Organized with docstrings

Total violations detected: [NUMBER]
Total violations fixed: [NUMBER]

🛑 BLOCKING: If violations > 0, MUST fix before file write.
```

---

## 🎯 **PASTE THIS IN CHAT BEFORE WRITING FILE**

⚠️ **MANDATORY**: Copy and paste this validation result in chat:

```
✅ PRE-WRITE VALIDATION COMPLETE - TASK-XXX

Validation 1 (Imports): PASS - All imports at top using honeyhive.*
Validation 2 (Type Annotations): PASS - All variables annotated
Validation 3 (Boolean Comparisons): PASS - Using implicit booleanness
Validation 4 (Pylint Disables): PASS - Only approved disables
Validation 5 (Mocking Boundaries): PASS - Only external dependencies mocked
Validation 6 (Test Structure): PASS - Organized with docstrings

Total Violations: 0
Ready to write: tests/unit/path/to/test_file.py
```

🚨 **FRAMEWORK-VIOLATION**: If you write file without posting validation above

---

## 💡 **WHY THIS WORKS**

**Problem**: Loading standards in Phase 0 doesn't prevent violations during generation.

**Solution**: This checkpoint forces **explicit validation** against each standard **before** committing to file.

**Mechanism**:
1. Standards loaded in Phase 0 (reference material)
2. Code planned in Phase 6 (generation)
3. **Validation in Phase 6.5** (enforcement) ← NEW
4. File written in Phase 7 (execution)

**Result**: Violations caught **before** they enter codebase, not after.

---

## 🔄 **INTEGRATION WITH FRAMEWORK**

**Phase 6 Output**: Test plan complete, ready to generate
**Phase 6.5 Input**: Review planned code against standards (THIS PHASE)
**Phase 6.5 Output**: Validated plan, zero violations
**Phase 7 Input**: Write validated code to file

⛔ **CRITICAL**: Cannot skip from Phase 6 → Phase 7. Must pass through Phase 6.5.

---

🛑 UPDATE-TABLE: Phase 6.5 validation complete
🎯 NEXT-MANDATORY: Proceed to Phase 7 file write

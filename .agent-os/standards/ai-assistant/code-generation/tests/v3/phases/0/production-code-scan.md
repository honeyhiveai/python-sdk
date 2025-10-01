# Phase 0.5: Production Code Standards Scan

**Purpose**: Scan target production file for standards violations BEFORE test generation begins

**When to Execute**: After Phase 0 (Context Loading), before Phase 1 (Method Verification)

**Why This Exists**: Testing often reveals production code quality issues. By scanning production code first, we can fix violations proactively, saving rework cycles and improving overall code quality.

---

## 🛑 BLOCKING CHECKPOINT

**This phase is MANDATORY and BLOCKING**

If violations are found, production code MUST be fixed before proceeding to test generation.

**Evidence**: TASK-015 Module 3 (`bundle_verification.py`) had inline import discovered during test generation, requiring production code fix and test update rework.

---

## Production Code Standards Checklist

Execute these checks on the target production file:

### ✅ Check 1: Inline Imports (CRITICAL)

**Scan For**: Import statements inside functions/methods instead of at top of file

**How to Check**:
```bash
grep -n "^[[:space:]]\+from\|^[[:space:]]\+import" <production_file.py>
```

**Expected**: No output (all imports at top of file)

**If Violations Found**:
1. **STOP test generation**
2. Move inline imports to top of file
3. Verify imports don't create circular dependency issues
4. Re-run this scan to confirm fix

**Example Violation**:
```python
def verify_bundle_compilation() -> Tuple[bool, Dict[str, Any]]:
    from config.dsl.compiler import ProviderCompiler  # ❌ INLINE IMPORT
    ...
```

**Correct**:
```python
from config.dsl.compiler import ProviderCompiler  # ✅ TOP OF FILE

def verify_bundle_compilation() -> Tuple[bool, Dict[str, Any]]:
    ...
```

---

### ✅ Check 2: Type Annotations

**Scan For**: Missing type annotations on function parameters, return types, or class attributes

**How to Check**:
```bash
mypy <production_file.py> --config-file=pyproject.toml
```

**Expected**: 0 errors

**If Violations Found**:
1. **STOP test generation**
2. Add missing type annotations to production code
3. Re-run MyPy to confirm fix

**Why**: Type annotations are required for:
- MyPy compliance in test file
- Mock object type hints
- Test assertion correctness

---

### ✅ Check 3: Logging Pattern (Multi-Instance Components)

**Scan For**: Usage of standard `logging.getLogger()` in multi-instance tracer components

**How to Check**: Review production file's position in architecture

**Multi-Instance Components** (must use `safe_log`):
- Files in `src/honeyhive/tracer/processing/`
- Files that are direct components of tracer
- Files with `tracer_instance` parameter

**Standard Components** (use `logging.getLogger()`):
- CLI tools
- Standalone utilities
- Config/validation modules

**If Violation Found**:
1. **STOP test generation**
2. Replace `logger.*` calls with `safe_log(self.tracer_instance, ...)`
3. Add `tracer_instance` parameter if missing
4. Update caller to pass `tracer_instance`

**Example**: See TASK-014 `bundle_loader.py` fix

---

### ✅ Check 4: Pylint Production Code Scan

**How to Check**:
```bash
pylint <production_file.py> --rcfile=pyproject.toml
```

**Target**: 10.0/10 or document exceptions

**Common Issues to Fix**:
- `import-outside-toplevel` (inline imports)
- `missing-docstring`
- `line-too-long` (run `black` to fix)
- `unused-import`

**If Score < 10.0**:
1. Review violations
2. Fix issues where possible
3. Document any exceptions (e.g., legacy code)
4. Re-scan to confirm

---

### ✅ Check 5: MyPy Production Code Scan

**How to Check**:
```bash
mypy <production_file.py> --config-file=pyproject.toml
```

**Expected**: 0 errors

**Common Issues**:
- Missing type annotations
- `Any` type usage without justification
- Incompatible return types

**If Errors Found**:
1. **STOP test generation** if errors relate to public API
2. Fix type errors in production code
3. Re-run MyPy to confirm

---

### ✅ Check 6: Docstring Coverage

**Scan For**: Missing or incomplete docstrings

**How to Check**: Manually review or use `pydocstyle`

**Required Docstrings**:
- Module docstring at top of file
- All public functions
- All public classes
- All public methods

**Format**: Sphinx-style (Google or NumPy format acceptable)

**Why**: Tests will reference production docstrings, and incomplete docs make test intent unclear

---

## Phase 0.5 Completion Checklist

Before proceeding to Phase 1, confirm:

- [ ] ✅ Check 1: No inline imports found (or all fixed)
- [ ] ✅ Check 2: MyPy reports 0 type errors
- [ ] ✅ Check 3: Logging pattern appropriate for component type
- [ ] ✅ Check 4: Pylint score 10.0/10 (or exceptions documented)
- [ ] ✅ Check 5: MyPy production scan clean
- [ ] ✅ Check 6: All public functions/classes have docstrings

**If ALL checks pass**: Proceed to Phase 1 (Method Verification)

**If ANY check fails**: Fix production code first, then re-run Phase 0.5

---

## Progress Table Update

Update the framework progress table to include Phase 0.5:

| Phase | Status | Evidence | Commands |
|-------|--------|----------|----------|
| 0. Context Loading | ✅ COMPLETE | ... | ... |
| **0.5 Production Code Scan** | **🔄 IN PROGRESS** | **Scanning...** | **0/6** |
| 1. Method Verification | ⏳ PENDING | ... | ... |

---

## Evidence & Rationale

**From TASK-015 Retrospective**:

> **Event**: `bundle_verification.py` had inline import that wasn't caught until test generation
> 
> **Root Cause**: Production code wasn't scanned during Phase 6.5. Assumed production code was standards-compliant.
> 
> **User Feedback**: "inline imports again?!"
> 
> **Fix**: Moved import to top of production file
> 
> **Prevention**: Add Phase 0.5: Production Code Standards Scan before test generation

**Impact**:
- Prevents rework cycles (test → discover prod issue → fix prod → update test)
- Improves production code quality proactively
- Reduces user frustration from recurring violations

---

## Related Standards

- **Inline Imports**: `.agent-os/standards/ai-assistant/code-generation/production/README.md`
- **Type Annotations**: `.agent-os/standards/ai-assistant/code-generation/type-safety.md`
- **safe_log Pattern**: `docs/architecture/multi-instance-logging.md`
- **Pylint Standards**: `.agent-os/standards/ai-assistant/code-generation/linters/pylint/`

---

**Phase Created**: 2025-09-30  
**Evidence Source**: TASK-015 Retrospective  
**Status**: ✅ **APPROVED - INTEGRATE INTO FRAMEWORK**

# Phase 0 Setup - Common Pre-Generation

## 🎯 **PURPOSE**

Complete all pre-generation setup phases and determine test type path.

**Previous**: [Framework Execution Guide](framework-execution-guide.md)  
**Next**: Choose path based on test type decision below

---

# 🚨 **PHASE 0: PRE-GENERATION CHECKLIST**

## 🚨 **MANDATORY FIRST STEP - 30 SECOND VALIDATION**

### ✅ **MANDATORY CHECKLIST (ALL REQUIRED)**

#### **🔧 Environment Validation**
- [ ] **Python virtual environment active** (`python-sdk` venv)
- [ ] **Tox available** (use `tox -e lint`, never direct pylint)
- [ ] **Git status clean** (no uncommitted changes that could interfere)

#### **📦 Import Planning** 
- [ ] **All imports at top level** (never inside functions/methods)
- [ ] **Mock imports planned** (use `patch.object`, avoid `Mock(spec=Class)`)
- [ ] **Production imports identified** (what needs to be imported for testing)

#### **📏 Line Length Strategy**
- [ ] **Black formatting planned** (will auto-fix to 88 chars)
- [ ] **Long test names acceptable** (descriptive over brevity)
- [ ] **Docstring line breaks planned** (use triple quotes with breaks)

#### **🎯 Type Annotation Strategy**
- [ ] **Test function signatures planned** (minimal annotations for tests)
- [ ] **Mock return types identified** (what mocks should return)
- [ ] **Fixture type hints planned** (pytest fixture return types)

#### **📊 Success Metrics Strategy**
- [ ] **Target success metrics identified** (90%+ coverage for unit, functional validation for integration)
- [ ] **Edge cases planned** (error conditions, boundary values)
- [ ] **Integration points mapped** (how this code connects to others)

### 🚨 **MANDATORY: Read Linter Documentation FIRST**

```bash
# MANDATORY COMMANDS - MUST EXECUTE ALL:
find .agent-os/standards/ai-assistant/code-generation/linters/ -name "*.md"
# Expected: All linter-specific documentation files (read ALL for complete context)
```

### 📋 **EMBEDDED CORE LINTER STANDARDS**

#### **🎨 Black Formatting (Auto-Applied)**
- **Line Length**: 88 characters (auto-fixed by Black)
- **Import Organization**: All imports at top level, never inside functions
- **String Quotes**: Consistent quote usage (Black handles)
- **Trailing Whitespace**: Auto-removed by Black

#### **🔍 MyPy Type Checking (Critical for Tests)**
- **Test Functions**: `def test_method() -> None:` (always return None)
- **Mock Patterns**: Use `patch.object(target, 'method')` NOT `Mock(spec=Class)`
- **Fixture Types**: Type all pytest fixtures with return type hints
- **Import Strategy**: `from unittest.mock import patch, MagicMock, PropertyMock`

#### **🛡️ Pylint Quality (10.0/10 Target)**
- **Import Rules**: Standard library → Third party → Local imports
- **Approved Disables**: Only `too-many-lines`, `redefined-outer-name` for tests
- **Test-Specific**: Use `# pylint: disable=protected-access` for `._private` access
- **Documentation**: All classes and methods need docstrings

### 📋 **EMBEDDED CORE TESTING STANDARDS**

#### **📁 File Naming Conventions**
- **Unit Tests**: `test_[module]_[file].py` (e.g., `test_tracer_core_operations.py`)
- **Integration Tests**: `test_[feature]_integration.py` (e.g., `test_tracer_instrumentor_integration.py`)
- **Location**: Unit tests in `tests/unit/`, integration tests in `tests/integration/`

#### **⚡ Command Standards (MANDATORY)**
- **Unit Tests**: `tox -e unit` (NEVER direct pytest)
- **Integration Tests**: `tox -e integration` (NEVER direct pytest)
- **Linting**: `tox -e lint` (NEVER direct pylint)
- **Formatting**: `black [file]` (always run before commit)

#### **🎯 Quality Targets (NON-NEGOTIABLE)**
- **Pylint Score**: 10.0/10 (perfect score required)
- **MyPy Errors**: 0 (complete type safety)
- **Test Pass Rate**: 100% (all tests must pass)
- **Coverage**: 90%+ (unit tests) / Functional validation (integration tests)

**📚 Detailed Standards**: [Testing Standards](../../testing/README.md) for complex scenarios and advanced patterns

**🚨 CHECKPOINT GATE: Cannot proceed until ALL checklist items completed and linter docs read.**

---

# 🚨 **PHASE 0B: PRE-GENERATION METRICS**

## 📊 **MANDATORY BASELINE MEASUREMENT**

### 🚨 **MANDATORY METRICS COMMANDS**

```bash
# 1. Collect comprehensive pre-generation metrics
python scripts/test-generation-metrics.py --production-file [PRODUCTION_FILE] --test-file [TARGET_TEST_FILE] --pre-generation --summary
# Expected: JSON file with baseline coverage, lint scores, complexity metrics
```

**🚨 CHECKPOINT GATE: Cannot proceed without baseline metrics collection.**

**ENFORCEMENT**: AI must copy-paste the actual JSON output from the metrics command. Saying "metrics collected" without showing output is a **SKIP INDICATOR** and must be stopped immediately.

---

# 🚨 **PHASE 0C: TARGET VALIDATION**

## 🚨 **STOP: CANNOT PROCEED WITH INAPPROPRIATE TEST TARGETS**

### 🎯 **FORBIDDEN TEST TARGETS (MUST REJECT)**

#### **❌ NEVER TEST THESE FILES:**
- **`__init__.py`** - Only imports and `__all__` declarations (no business logic)
- **`conftest.py`** - Pytest configuration and fixture controller (never test targets)
- **`setup.py`** - Package installation scripts (not application logic)
- **`__main__.py`** - Entry point scripts (minimal logic, not core functionality)
- **Migration scripts** - One-time database/config changes (not ongoing functionality)

### 🚨 **MANDATORY VALIDATION COMMANDS**

```bash
# 1. Verify target is not a forbidden file type
basename [PRODUCTION_FILE]
# Expected: NOT __init__.py, conftest.py, setup.py, __main__.py

# 2. Verify substantial business logic exists (>50 lines non-import code)
grep -v "^import\|^from\|^#\|^$" [PRODUCTION_FILE] | wc -l
# Expected: >50 lines of actual code

# 3. Verify classes/functions exist (not just imports)
grep -E "^class |^def " [PRODUCTION_FILE] | head -5
# Expected: At least 1 class or function definition

# 4. Validate test file naming follows standards
echo "tests/unit/test_[MODULE_PATH_UNDERSCORED].py" | grep -E "test_[a-z_]+\.py$"
# Expected: Proper test_module_file.py pattern

# 5. Ensure single module focus (not aggregated testing)
echo "[PRODUCTION_MODULE]" | grep -v "models/__init__.py\|__init__.py"
# Expected: Specific module file, not module aggregation
```

### 🚨 **VALIDATION GATE REQUIREMENTS**

**PASS CRITERIA:**
- ✅ Target file is NOT in forbidden list
- ✅ Target has >50 lines of non-import code  
- ✅ Target contains at least 1 class or function
- ✅ Test file follows naming pattern: `test_[module]_[file].py`
- ✅ Single module focus (not testing entire directories)

**ENFORCEMENT RULE:** If ANY validation fails → **REJECT TARGET** and suggest appropriate alternatives.

**🚨 CHECKPOINT GATE: Cannot proceed with invalid targets.**

---

# 🔀 **CRITICAL: TEST TYPE DECISION**

## 🎯 **DETERMINE YOUR PATH**

### **Decision Logic:**

```bash
# Analyze the production file to determine test type
grep -E "class |def " [PRODUCTION_FILE] | wc -l
# If 1-3 classes/functions → Likely UNIT TEST
# If >3 classes or complex workflows → Check integration patterns

grep -E "requests\.|http|api|client" [PRODUCTION_FILE]
# If API calls found → Likely INTEGRATION TEST

grep -E "import.*honeyhive" [PRODUCTION_FILE] | wc -l  
# If many internal imports → Likely INTEGRATION TEST
```

### **🧪 UNIT TEST PATH** 
**Choose if:**
- Single module with 1-3 classes/functions
- Minimal external dependencies
- Focus on isolated component testing
- Can mock all external dependencies

**Next Steps:**
1. **[Unit Test Analysis](unit-test-analysis.md)** - Phases 1-6 with mocking focus
2. **[Unit Test Generation](unit-test-generation.md)** - Unit-specific patterns
3. **[Unit Test Quality](unit-test-quality.md)** - Phases 7-8 with coverage targets

### **🌐 INTEGRATION TEST PATH**
**Choose if:**
- Multi-component workflows
- Real API interactions required
- End-to-end functionality testing
- Cannot meaningfully mock dependencies

**Next Steps:**
1. **[Integration Test Analysis](integration-test-analysis.md)** - Phases 1-6 with real API focus
2. **[Integration Test Generation](integration-test-generation.md)** - Integration-specific patterns  
3. **[Integration Test Quality](integration-test-quality.md)** - Phases 7-8 with functional validation

---

## 🚨 **PHASE 0 COMPLETION CHECKPOINT**

### **Before proceeding to your chosen path, verify:**

**✅ Phase 0 Checklist Complete:**
- Environment validated
- Imports planned
- Line length strategy set
- Type annotations planned
- Success metrics identified
- Linter documentation read

**✅ Phase 0B Metrics Complete:**
- Pre-generation metrics collected
- Baseline JSON file created

**✅ Phase 0C Validation Complete:**
- Target validated as appropriate
- Test file naming confirmed
- Single module focus verified

**✅ Test Type Decision Made:**
- Analysis commands executed
- Path chosen (Unit or Integration)
- Next steps identified

**🎯 UPDATE PROGRESS TABLE:** Mark Phases 0, 0B, and 0C as complete (✅) in chat window before proceeding to chosen path.

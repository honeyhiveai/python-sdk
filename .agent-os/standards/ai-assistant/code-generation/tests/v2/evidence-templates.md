# Required Evidence Templates

## 📊 **PROGRESS TABLE FORMATS**

### **Phase 1: Method Verification Evidence**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 1: Method Verification | ✅ | Found X methods (Y public, Z private), A imports (B external, C internal), D classes verified with __init__ methods | 3/3 | ✅ |
```

### **Phase 2: Logging Analysis Evidence**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 2: Logging Analysis | ✅ | Found X safe_log calls (Y debug, Z info, A error), B conditional branches analyzed in error paths | 3/3 | ✅ |
```

### **Phase 3: Dependency Analysis Evidence**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 3: Dependency Analysis | ✅ | Analyzed X external deps (requests, json, os), Y internal imports mapped (tracer.core, utils.logger) | 4/4 | ✅ |
```

### **Phase 4: Usage Patterns Evidence**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 4: Usage Patterns | ✅ | Found X usage patterns: error handling in Y locations, validation in Z methods, API calls use retry logic | 3/3 | ✅ |
```

### **Phase 5: Coverage Analysis Evidence**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 5: Coverage Analysis | ✅ | Target: 90%+ coverage, X methods (Y public, Z private), A branches planned (B error paths, C validation branches, D business logic) | 2/2 | ✅ |
```

### **Quality Phase Evidence Templates**
```
| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 7: Post-Generation Metrics | ✅ | Tests pass: 100%, Coverage: 92%, Pylint: 10.0/10, MyPy: 0 errors | 1/1 | ✅ |
| 8: Quality Enforcement | ✅ | All targets met: Pass ✅, Coverage ✅, Pylint ✅, MyPy ✅ | 5/5 | ✅ |
```

---

## 📋 **COMMAND OUTPUT FORMATS**

### **Metrics Collection Output Format**

**Pre-Generation Metrics (Phase 0B):**
```bash
python scripts/test-generation-metrics.py --production-file [FILE] --test-file [TARGET] --pre-generation --summary
```

**Required Output to Copy-Paste:**
```
=== TEST GENERATION METRICS SUMMARY ===
Timestamp: 2025-09-20_220600
Production File: src/honeyhive/tracer/core.py
Test File: tests/unit/test_tracer_core.py
Metrics File: test_generation_metrics_20250920_220600.json

BASELINE METRICS:
- Production File Lines: 450
- Existing Test Coverage: 0%
- Pylint Score: 9.2/10
- MyPy Errors: 2
```

**Post-Generation Metrics (Phase 7):**
```
=== TEST GENERATION METRICS SUMMARY ===
Timestamp: 2025-09-20_221500
Production File: src/honeyhive/tracer/core.py
Test File: tests/unit/test_tracer_core.py
Metrics File: test_generation_metrics_20250920_221500.json

QUALITY METRICS:
- Test Pass Rate: 100% (45/45 tests)
- Test Coverage: 92%
- Pylint Score: 10.0/10
- MyPy Errors: 0
- Black Formatting: Clean
```

### **Analysis Command Output Format**

**Method Verification Commands:**
```bash
grep -n "^class\|^def\|^    def" [PRODUCTION_FILE]
# Copy exact output with line numbers

python -c "import ast; [print(f'{node.name}: {ast.get_docstring(node)}') for node in ast.walk(ast.parse(open('[PRODUCTION_FILE]').read())) if isinstance(node, (ast.FunctionDef, ast.ClassDef))]"
# Copy method signatures and docstrings
```

**Logging Analysis Commands:**
```bash
grep -n "log\." [PRODUCTION_FILE]
grep -n "safe_log" [PRODUCTION_FILE]
# Copy exact matches with line numbers
```

**Dependency Analysis Commands:**
```bash
grep -E "^import |^from " [PRODUCTION_FILE]
grep -E "requests\.|urllib\.|json\.|os\.|sys\.|time\." [PRODUCTION_FILE]
# Copy complete import lists and usage patterns
```

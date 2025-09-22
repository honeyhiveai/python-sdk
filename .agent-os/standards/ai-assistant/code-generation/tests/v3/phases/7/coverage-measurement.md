# Phase 7: Coverage Measurement

**🎯 Measure Actual Coverage Achieved by Generated Tests**

## 🚨 **ENTRY REQUIREMENTS**
🛑 VALIDATE-GATE: Coverage Measurement Prerequisites
- [ ] Test execution metrics completed with evidence ✅/❌
- [ ] Coverage tools validated in Phase 6 ✅/❌
- [ ] Phase 7.1 progress table updated ✅/❌

## 📋 **COVERAGE MEASUREMENT COMMANDS**

### **Line Coverage Measurement**
```bash
echo "=== COVERAGE MEASUREMENT ==="

# Run tests with coverage
echo "--- Line Coverage ---"
pytest tests/unit/test_tracer_instrumentation_initialization.py --cov=src/honeyhive/tracer/instrumentation/initialization --cov-report=term-missing

# Generate detailed coverage report
pytest tests/unit/test_tracer_instrumentation_initialization.py --cov=src/honeyhive/tracer/instrumentation/initialization --cov-report=html

# Coverage percentage only
coverage report --include="src/honeyhive/tracer/instrumentation/initialization.py" | grep "TOTAL"
```

### **Branch Coverage Measurement**
```bash
# Branch coverage analysis
echo "--- Branch Coverage ---"
pytest tests/unit/test_tracer_instrumentation_initialization.py --cov=src/honeyhive/tracer/instrumentation/initialization --cov-branch --cov-report=term-missing

# Missing branches identification
coverage report --show-missing --include="src/honeyhive/tracer/instrumentation/initialization.py"
```

### **Function Coverage Analysis**
```python
# Analyze function coverage
import coverage
import ast

def analyze_function_coverage():
    # Load coverage data
    cov = coverage.Coverage()
    cov.load()
    
    # Get covered lines
    covered_lines = cov.get_data().lines('src/honeyhive/tracer/instrumentation/initialization.py')
    
    # Parse AST to find function definitions
    with open('src/honeyhive/tracer/instrumentation/initialization.py', 'r') as f:
        tree = ast.parse(f.read())
    
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'line': node.lineno,
                'covered': node.lineno in covered_lines
            })
    
    covered_functions = sum(1 for f in functions if f['covered'])
    total_functions = len(functions)
    function_coverage = (covered_functions / total_functions * 100) if total_functions > 0 else 0
    
    print(f"FUNCTION COVERAGE: {covered_functions}/{total_functions} ({function_coverage:.1f}%)")
    return function_coverage, covered_functions, total_functions

function_coverage, covered_funcs, total_funcs = analyze_function_coverage()
```

## 📊 **EVIDENCE REQUIRED**
- **Line coverage**: [PERCENTAGE]
- **Branch coverage**: [PERCENTAGE]
- **Function coverage**: [PERCENTAGE]
- **Missing lines**: [LINE NUMBERS]
- **Missing branches**: [BRANCH DETAILS]
- **Command output**: Paste actual coverage results

## 🚨 **VALIDATION GATE**
- [ ] Line coverage measured and documented
- [ ] Branch coverage analyzed
- [ ] Function coverage calculated
- [ ] Missing coverage identified

**Next**: Task 7.3 Quality Assessment

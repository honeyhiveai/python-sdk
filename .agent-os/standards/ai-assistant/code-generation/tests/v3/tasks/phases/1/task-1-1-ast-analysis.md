# Task 1.1: AST Method Analysis

**🎯 Create Deep AST Parsing Component for Method Signature Extraction**

## 📋 **TASK DEFINITION**

### **Scope**
Create a focused component for deep AST parsing that extracts complete method signatures, matching archive capabilities.

### **Archive Reference**
- **Source**: `archive/unit-test-analysis.md` Lines 16-30
- **Capability**: Complete function signature extraction with parameters and defaults

### **Deliverable**
Single file: `phases/1/ast-method-analysis.md` (<100 lines)

## 🎯 **REQUIREMENTS**

### **Must Include**
- **Deep AST parsing command** (Python script for complete analysis)
- **Method signature extraction** with parameters and defaults
- **Class and function inventory** with line numbers
- **Public/private classification** for test targeting
- **Evidence collection template** for quantified results

### **Must Exclude**
- Attribute detection (separate task)
- Import analysis (separate task)  
- Mock configuration (separate task)
- Path-specific strategy (separate task)

## 📊 **SUCCESS CRITERIA**

### **Functionality**
- [ ] **Complete AST parsing** matching archive depth
- [ ] **All method signatures** extracted with parameters
- [ ] **Class inventory** with method counts
- [ ] **Public/private classification** completed
- [ ] **Evidence template** for result documentation

### **Size Constraint**
- [ ] **File size <100 lines** (strict AI consumption limit)
- [ ] **Single responsibility** (AST analysis only)
- [ ] **Clear navigation** to next component

### **Archive Parity**
- [ ] **Matches archive capability** for method extraction
- [ ] **Exceeds archive** with better organization
- [ ] **Preserves quality** while improving consumability

## 🔧 **IMPLEMENTATION NOTES**

### **Archive Command Pattern** (to preserve)
```python
# Extract method signatures and docstrings
python -c "import ast, inspect; [print(f'{node.name}: {ast.get_docstring(node)}') for node in ast.walk(ast.parse(open('[PRODUCTION_FILE]').read())) if isinstance(node, (ast.FunctionDef, ast.ClassDef))]"
```

### **Enhancement Opportunities**
- Better output formatting
- More comprehensive parameter analysis
- Clearer evidence collection

## 🚨 **EXECUTION**
**Create**: `phases/1/ast-method-analysis.md` with complete AST parsing capability in <100 lines

---

**🎯 This task creates the foundation component for all subsequent Phase 1 analysis.**

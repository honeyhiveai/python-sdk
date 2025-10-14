# Task 1: AST Method Analysis

**Phase:** 1 (Method Verification)  
**Purpose:** Deep AST parsing for complete method signature extraction  
**Estimated Time:** 3 minutes

---

## 🎯 Objective

Use AST parsing to extract all function signatures, parameter counts, and privacy levels from the production file. This prevents V2's signature mismatch failures.

---

## Prerequisites

- [ ] Phase 0 complete (environment validated, path selected) ✅/❌
- [ ] Production file path confirmed

---

## 🛑 Step 1: AST Analysis Execution

🛑 EXECUTE-NOW: Complete AST method analysis command

```python
python -c "
import ast

def analyze_methods(file_path):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    print('=== METHOD SIGNATURE ANALYSIS ===')
    
    classes = []
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            cls_info = {'name': node.name, 'line': node.lineno, 'methods': []}
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = [arg.arg for arg in item.args.args]
                    defaults = len(item.args.defaults)
                    required = len(args) - defaults
                    
                    cls_info['methods'].append({
                        'name': item.name,
                        'line': item.lineno,
                        'args': args,
                        'required': required,
                        'total': len(args),
                        'private': item.name.startswith('_')
                    })
            classes.append(cls_info)
        
        elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
            args = [arg.arg for arg in node.args.args]
            defaults = len(node.args.defaults)
            required = len(args) - defaults
            
            functions.append({
                'name': node.name,
                'line': node.lineno,
                'args': args,
                'required': required,
                'total': len(args),
                'private': node.name.startswith('_')
            })
    
    # Report results
    for cls in classes:
        print(f'CLASS: {cls[\"name\"]} (Line {cls[\"line\"]}) - {len(cls[\"methods\"])} methods')
        for method in cls['methods']:
            privacy = 'PRIVATE' if method['private'] else 'PUBLIC'
            print(f'  {method[\"name\"]}({\"', '\".join(method[\"args\"])}) - Line {method[\"line\"]} - {privacy} - Required: {method[\"required\"]}')
    
    for func in functions:
        privacy = 'PRIVATE' if func['private'] else 'PUBLIC'
        print(f'FUNCTION: {func[\"name\"]}({\"', '\".join(func[\"args\"])}) - Line {func[\"line\"]} - {privacy} - Required: {func[\"required\"]}')
    
    total_methods = sum(len(cls['methods']) for cls in classes)
    print(f'\\nSUMMARY: {len(classes)} classes, {total_methods} methods, {len(functions)} functions')

analyze_methods('[PRODUCTION_FILE]')
"
```

🛑 PASTE-OUTPUT: Complete AST analysis results below (no summaries allowed)

---

## 📊 Evidence Documentation

📊 COUNT-AND-DOCUMENT: AST Analysis Results
- Classes found: [EXACT NUMBER]
- Total methods: [EXACT NUMBER]
- Module functions: [EXACT NUMBER]
- Key signatures identified: [list 3-5 most important]

⚠️ EVIDENCE-REQUIRED: Complete command output pasted above

---

## Completion Criteria

🛑 VALIDATE-GATE: AST Analysis Complete

- [ ] AST command executed with full output documented ✅/❌
- [ ] All classes/functions catalogued with exact counts ✅/❌
- [ ] Method signatures extracted with parameters ✅/❌
- [ ] Privacy levels identified (public/private) ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without complete AST evidence

---

## Next Step

🔄 UPDATE-TABLE: Phase 1 Progress
```markdown
| Phase | Status | Evidence | Gate |
|-------|--------|----------|------|
| 1.1: AST Analysis | ✅ | [X classes, Y methods, Z functions] | ✅ |
```

🎯 NEXT-MANDATORY: [task-2-attribute-detection.md](task-2-attribute-detection.md)

---

**Critical:** These signatures must match exactly in generated tests



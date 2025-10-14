# Task 2: Attribute Pattern Detection

**Phase:** 1 (Method Verification)  
**Purpose:** Find ALL attribute access patterns for mock completeness  
**Estimated Time:** 2 minutes

---

## 🎯 Objective

Identify all object.attribute access patterns to ensure mocks have all required attributes. Missing attributes = AttributeError = test failure.

---

## Prerequisites

- [ ] Task 1 (AST Analysis) complete ✅/❌
- [ ] Method inventory available with counts

---

## 🛑 Step 1: Attribute Detection Execution

🛑 EXECUTE-NOW: All attribute detection commands

```bash
echo "=== ATTRIBUTE PATTERNS ==="
grep -n -E "[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*" [PRODUCTION_FILE]

# Nested chains
echo "--- Nested Chains ---"
grep -n -E "[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*" [PRODUCTION_FILE]

# Method calls  
echo "--- Method Calls ---"
grep -n -E "[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\(" [PRODUCTION_FILE]

# Assignments
echo "--- Assignments ---"
grep -n -E "[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\s*=" [PRODUCTION_FILE]

echo "=== SUMMARY ==="
echo "Direct: $(grep -c -E '[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*' [PRODUCTION_FILE])"
echo "Nested: $(grep -c -E '[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*' [PRODUCTION_FILE])"
echo "Methods: $(grep -c -E '[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\(' [PRODUCTION_FILE])"
```

🛑 PASTE-OUTPUT: Complete attribute detection results

---

## 📊 Evidence Documentation

📊 COUNT-AND-DOCUMENT: Attribute Patterns
- Direct attributes: [EXACT NUMBER]
- Nested chains: [EXACT NUMBER] (e.g., tracer.config.api_key)
- Method calls: [EXACT NUMBER]
- Assignments: [EXACT NUMBER]
- Critical attributes: [list key ones like config, is_main_provider]

⚠️ EVIDENCE-REQUIRED: Complete command output pasted above

---

## Completion Criteria

🛑 VALIDATE-GATE: Attribute Detection Complete

- [ ] All attribute patterns identified with line numbers ✅/❌
- [ ] Nested chains documented for complex mock setup ✅/❌
- [ ] Method calls catalogued for return value mocking ✅/❌
- [ ] Assignment patterns captured for state testing ✅/❌
- [ ] Exact counts documented ✅/❌

🚨 FRAMEWORK-VIOLATION: Missing attributes = 22% V2 failure

---

## Next Step

🔄 UPDATE-TABLE: Phase 1 Progress
```markdown
| Phase | Status | Evidence | Gate |
|-------|--------|----------|------|
| 1.2: Attribute Detection | ✅ | [X attributes, Y nested, Z critical] | ✅ |
```

🎯 NEXT-MANDATORY: [task-3-import-mapping.md](task-3-import-mapping.md)

---

**Critical:** Every attribute found MUST be in mocks (unit path)



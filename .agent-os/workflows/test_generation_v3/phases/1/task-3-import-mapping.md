# Task 3: Import Dependency Mapping

**Phase:** 1 (Method Verification)  
**Purpose:** Map all imports to identify external vs internal dependencies  
**Estimated Time:** 2 minutes

---

## 🎯 Objective

Classify all imports as external (require mocking) or internal (path-specific handling) to build complete dependency strategy.

---

## Prerequisites

- [ ] Task 2 (Attribute Detection) complete ✅/❌
- [ ] Method and attribute patterns available

---

## 🛑 Step 1: Import Analysis Execution

🛑 EXECUTE-NOW: All import dependency mapping commands

```bash
echo "=== IMPORT ANALYSIS ==="
grep -n -E "^(import|from.*import)" [PRODUCTION_FILE]

# External dependencies (require mocking)
echo "--- External Dependencies ---"
grep -n -E "^(import|from)\s+(os|sys|time|json|requests|urllib|opentelemetry|typing)" [PRODUCTION_FILE]

# Internal dependencies (path-specific)
echo "--- Internal Dependencies ---"
grep -n -E "^(import|from)\s+.*honeyhive" [PRODUCTION_FILE]

# Conditional imports
echo "--- Conditional Imports ---"
grep -A 3 -B 1 -n "try:" [PRODUCTION_FILE] | grep -E "(import|from.*import)"

echo "=== SUMMARY ==="
echo "Total: $(grep -c -E '^(import|from.*import)' [PRODUCTION_FILE])"
echo "External: $(grep -c -E '^(import|from)\s+(os|sys|time|json|requests|urllib|opentelemetry|typing)' [PRODUCTION_FILE])"
echo "Internal: $(grep -c -E '^(import|from)\s+.*honeyhive' [PRODUCTION_FILE])"
```

🛑 PASTE-OUTPUT: Complete import analysis results

---

## 📊 Evidence Documentation

📊 COUNT-AND-DOCUMENT: Import Classification
- Total imports: [EXACT NUMBER]
- External dependencies: [EXACT NUMBER] (must mock for unit)
- Internal dependencies: [EXACT NUMBER] (path-specific)
- Conditional imports: [EXACT NUMBER]
- Key external: [list major ones like requests, opentelemetry]

⚠️ EVIDENCE-REQUIRED: Complete command output pasted above

---

## Completion Criteria

🛑 VALIDATE-GATE: Import Mapping Complete

- [ ] All imports catalogued with line numbers ✅/❌
- [ ] External dependencies identified for mocking ✅/❌
- [ ] Internal dependencies mapped for path handling ✅/❌
- [ ] Conditional imports documented for edge cases ✅/❌
- [ ] Exact counts documented ✅/❌

---

## Next Step

🔄 UPDATE-TABLE: Phase 1 Progress
```markdown
| Phase | Status | Evidence | Gate |
|-------|--------|----------|------|
| 1.3: Import Mapping | ✅ | [X total, Y external, Z internal] | ✅ |
```

🎯 NEXT-MANDATORY: [task-4-function-calls.md](task-4-function-calls.md)

---

**Critical:** External deps MUST be mocked (unit), Internal handled by path



# Task 1: Validate Source Repository

**Phase:** 0 (Pre-Flight Checks)  
**Purpose:** Verify source repository is valid and clean  
**Estimated Time:** 10 seconds

---

## Objective

Verify the source repository is valid, is an praxis-os repository, has a clean Git state, and contains the required structure.

---

## Steps

### Step 1: Validate Source Repository

```python
from mcp_server.validation_module import ValidationModule

validator = ValidationModule()
source_result = validator.validate_source_repo(source_path)

if not source_result["valid"]:
    raise Exception(f"Source validation failed: {source_result['errors']}")
```

**Required checks:**
- [ ] Path exists
- [ ] Is praxis-os repository (has mcp_server/, universal/)
- [ ] Git status is clean (no uncommitted changes)
- [ ] Version extracted from VERSION.txt
- [ ] Commit hash extracted

---

## Completion Criteria

🛑 VALIDATE-GATE: Source Validated

- [ ] Source path exists ✅/❌
- [ ] Is agent-os repository ✅/❌
- [ ] Git is clean ✅/❌
- [ ] Version extracted ✅/❌
- [ ] Commit hash extracted ✅/❌

---

## Evidence Collection

📊 COUNT-AND-DOCUMENT: Validation Results

**Source Path:** `[path]`  
**Version:** `[version]`  
**Commit:** `[hash]`  
**Git Clean:** `[yes/no]`  
**Validation:** `[PASS/FAIL]`

---

## Next Step

🎯 NEXT-MANDATORY: [task-2-validate-target.md](task-2-validate-target.md)

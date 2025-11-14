# Task 8: Fix Violations

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Address any compliance failures (split files, add commands, etc.)  
**Depends On**: Task 7 (compliance report with fix list)  
**Feeds Into**: Task 9 (Re-validate)

---

## Objective

Systematically fix all critical and high-priority violations identified in the compliance report.

---

## Context

📊 **CONTEXT**: This task requires careful editing of workflow files to bring them into compliance while preserving their functionality and intent. Work from the prioritized fix list in Task 7.

⚠️ **MUST-READ**: [../../core/file-splitting-strategies.md](../../core/file-splitting-strategies.md) for splitting oversized files and [../../core/compliance-audit-methodology.md](../../core/compliance-audit-methodology.md) for fix strategies

⚠️ **CONSTRAINT**: Do not skip critical fixes. Medium and low priority fixes can be deferred if time/complexity is an issue.

---

## Instructions

### Step 1: Review Fix Priority List

From Task 7's compliance report, review prioritized fixes:
- Critical violations (must fix)
- High priority violations (should fix)
- Focus on critical/high first

### Step 2: Fix File Size Violations

For files >170 lines, use splitting strategies from core/file-splitting-strategies.md:
- **Sequential Step Split**: Independent steps → separate tasks
- **Prepare/Execute Split**: Setup vs execution phases
- **Extract Methodology**: Move detailed content to core/

Update phase.md, metadata.json, and navigation after splits.

### Step 3: Fix Command Coverage Violations

For files <80% command coverage:
- Replace natural language with command symbols
- "Check if..." → 📖 **DISCOVER-TOOL**
- "You must..." → ⚠️ **CONSTRAINT**
- "Before proceeding..." → 🚨 **CRITICAL**

### Step 4: Fix Validation Gate Issues

Use gate fixing strategies from core/compliance-audit-methodology.md:
- **Missing gates**: Add complete section with evidence fields
- **Non-parseable**: Fix field names (backticks, snake_case), types, validators
- **Missing evidence**: Add 2-3 key fields per gate

### Step 5: Fix Three-Tier and Decomposition Issues

- **Phase overviews >150 lines**: Extract details to tasks, target ~80 lines
- **Reference content in tasks**: Move to supporting-docs/ or use 🔍 MUST-SEARCH
- **God tasks**: Split using strategies from core/file-splitting-strategies.md

### Step 7: Track Fixes Applied

Maintain a fix log:

```markdown
## Fix Log

### Critical Fixes
- [ ] Split task-3-complex-operation.md (145 lines) → task-3a + task-3b
- [ ] Add validation gate to Phase 2
- [ ] Fix evidence types in Phase 3 gate

### High Priority Fixes
- [ ] Add command symbols to 4 low-coverage tasks
- [ ] Fix gate parseability in Phase 1
...
```

Check off each fix as completed.

### Step 8: Update Affected Files

After making fixes, ensure consistency:
- If tasks split: update phase.md task table
- If tasks renumbered: update all navigation links
- If gates changed: verify evidence fields match task outputs
- If files moved: update any references

📖 **DISCOVER-TOOL**: Search for references to updated files

### Step 9: Verify Fixes Don't Break Navigation

After all fixes, trace navigation flow:
1. Start at Phase 0, task 1
2. Follow all 🎯 NEXT-MANDATORY links
3. Confirm no broken links
4. Confirm ↩️ RETURN-TO links correct
5. Confirm phase progression intact

---

## Expected Output

**Variables to Capture**:
- `violations_fixed`: Boolean (true when all critical/high fixed)
- `fixes_applied_count`: Integer
- `remaining_violations`: Integer (medium/low priority)
- `fix_log`: String (record of changes)

---

## Quality Checks

✅ Fix priority list reviewed  
✅ File size violations addressed  
✅ Command coverage improved  
✅ Validation gates fixed  
✅ Three-tier violations resolved  
✅ Horizontal decomposition improved  
✅ Fix log maintained  
✅ Affected files updated  
✅ Navigation verified intact

---

## Navigation

🎯 **NEXT-MANDATORY**: task-9-re-validate.md

↩️ **RETURN-TO**: phase.md (after task complete)


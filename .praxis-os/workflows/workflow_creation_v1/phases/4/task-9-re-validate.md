# Task 9: Re-validate

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Re-run all checks after fixes  
**Depends On**: Task 8 (violations fixed)  
**Feeds Into**: Task 10 (Final Compliance Check)

---

## Objective

Re-run all compliance audits from Tasks 1-6 to verify that fixes resolved the violations and didn't introduce new issues.

---

## Context

📊 **CONTEXT**: After making fixes, we must validate that the workflow now meets all compliance requirements. This is a full re-audit, not a spot check.

⚠️ **MUST-READ**: [../../core/compliance-audit-methodology.md](../../core/compliance-audit-methodology.md) section on "Re-Validation Process" for systematic re-audit procedures

---

## Instructions

### Step 1: Re-run File Size Audit

Repeat Task 1 process using methodology from core/:
- Find all task files, count lines
- Calculate compliance percentage
- Compare to original (before fixes)

**Expected**: ≥95% ≤100 lines (acceptable ≤150)

### Step 2: Re-run Command Coverage Audit

Repeat Task 2 process:
- Count command usage per file
- Calculate coverage percentages
- Compare to original

**Expected**: ≥80% command coverage

### Step 3: Re-verify Three-Tier, Gates, Contract, Decomposition

Quickly re-run Tasks 3-6:
- Three-tier: All tiers compliant
- Gates: 100% coverage, all parseable
- Contract: Present and complete
- Decomposition: No god tasks

Document any remaining violations.

### Step 4: Compare Before/After Metrics

Use comparison table format from core/compliance-audit-methodology.md:

| Metric | Before | After | Change | Status |
|--------|--------|-------|--------|--------|
| File Size | {%} | {%} | {delta}% | ✅/🟡/❌ |
| Command Coverage | {%} | {%} | {delta}% | ✅/🟡/❌ |
| Gates | {%} | {%} | {delta}% | ✅/❌ |

### Step 5: Document Remaining Issues

If violations remain:
- Critical issues still present
- High priority issues
- Newly introduced issues

### Step 6: Determine Pass/Fail

Calculate compliance score using formula from Task 7.

**Pass**: ALL criteria met → Proceed to Task 10  
**Fail**: ANY criterion fails → Return to Task 8

---

## Expected Output

**Variables to Capture**:
- `revalidation_complete`: Boolean
- `file_size_compliance_percent`: Integer (updated)
- `command_coverage_percent`: Integer (updated)
- `all_metrics_passing`: Boolean
- `remaining_violations`: Array (if any)
- `comparison_report`: String (before/after metrics)

---

## Quality Checks

✅ File size re-audited  
✅ Command coverage re-audited  
✅ Three-tier re-verified  
✅ Validation gates re-verified  
✅ Binding contract confirmed  
✅ Horizontal decomposition re-verified  
✅ Before/after comparison created  
✅ Remaining issues documented  
✅ Pass/fail determination made

---

## Decision Point

**If all metrics passing**:
- ✅ Proceed to Task 10

**If violations remain**:
- ⚠️ Return to Task 8 for additional fixes
- Document what still needs work

---

## Navigation

🎯 **NEXT-MANDATORY**: task-10-final-compliance-check.md (if passing) OR task-8-fix-violations.md (if violations remain)

↩️ **RETURN-TO**: phase.md (after task complete)


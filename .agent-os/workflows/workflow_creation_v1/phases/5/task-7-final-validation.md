# Task 7: Final Validation

**Phase**: 5 - Testing & Delivery  
**Purpose**: Re-run Phase 3 compliance checks  
**Depends On**: Task 6 (usage guide created), Task 5 (refinements applied)  
**Feeds Into**: Task 8 (Human Review)

---

## Objective

Run a final pass of all compliance checks from Phase 3 to ensure that refinements in Task 5 didn't introduce any regressions or new violations.

---

## Context

📊 **CONTEXT**: After usability refinements, we must confirm the workflow still meets all technical compliance requirements. This is a quick re-validation, not a full audit.

⚠️ **MUST-READ**: [../../core/compliance-audit-methodology.md](../../core/compliance-audit-methodology.md) for quick re-validation procedures

🚨 **CRITICAL**: Do not proceed to human review if any compliance regressions are found.

---

## Instructions

### Step 1: Quick File Size Check

Count lines in all task files:

📖 **DISCOVER-TOOL**: Count lines in files

Verify: ≥95% still ≤100 lines (acceptable ≤150, compress ≤170)

If files grew during refinements, assess severity and need for fixes.

### Step 2: Spot Check Command Coverage

Sample 10 random task files, verify command usage still ≥80%.

If coverage dropped, identify cause and restore if needed.

### Step 3: Verify Navigation Intact

Quick navigation trace:
- Start at Phase 0, phase.md
- Follow 3-4 🎯 NEXT-MANDATORY links
- Verify no broken links

### Step 4: Verify Gates and Structure

Quick checks:
- All validation gates still present
- Spot check 3 gates for parseability
- Three-tier still compliant
- Supporting docs present
- metadata.json valid

### Step 5: Compare to Phase 3 Report

Read original compliance report, compare key metrics:

| Metric | Phase 3 | Now | Status |
|--------|---------|-----|--------|
| File Size | {%} | {%} | ✅/⚠️/❌ |
| Command Coverage | {%} | {%} | ✅/⚠️/❌ |
| Gate Coverage | 100% | {%} | ✅/❌ |

### Step 6: Generate Final Validation Report

Use format from core/compliance-audit-methodology.md:
- Compliance status for each metric
- Changes since Phase 3
- Regressions found (if any)
- Overall PASS/FAIL
- Ready for human review (YES/NO)

### Step 7: Make Go/No-Go Decision

**GO**: All metrics passing, no critical regressions → Proceed to Task 8  
**NO-GO**: Any failing metric or critical regression → Return to Task 5

---

## Expected Output

**Variables to Capture**:
- `final_compliance_passed`: Boolean
- `regressions_found`: Array (list if any)
- `ready_for_human_review`: Boolean
- `final_validation_report`: String

---

## Quality Checks

✅ File sizes checked  
✅ Command coverage spot checked  
✅ Navigation verified  
✅ Validation gates confirmed  
✅ Three-tier compliance checked  
✅ Supporting docs verified  
✅ Metadata.json validated  
✅ Comparison to Phase 3 performed  
✅ Final validation report generated  
✅ Go/no-go decision made

---

## Decision Point

**If final_compliance_passed == true**:
- ✅ Proceed to Task 8 (Human Review)

**If final_compliance_passed == false**:
- ⚠️ Return to Task 5 (Implement Refinements)
- Fix regressions
- Re-run this validation

---

## Navigation

🎯 **NEXT-MANDATORY**: task-8-human-review.md (if passing) OR task-5-implement-refinements.md (if regressions)

↩️ **RETURN-TO**: phase.md (after task complete)


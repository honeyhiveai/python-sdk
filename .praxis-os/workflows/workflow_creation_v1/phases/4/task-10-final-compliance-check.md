# Task 10: Final Compliance Check

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Confirm 100% compliance achieved  
**Depends On**: Task 9 (re-validation passing)  
**Feeds Into**: Phase 4 (Testing & Delivery)

---

## Objective

Perform a final verification that the workflow meets all meta-workflow compliance requirements and is ready for testing.

---

## Context

📊 **CONTEXT**: This is the final checkpoint before moving to workflow testing and delivery. All metrics must be passing and all violations resolved.

⚠️ **MUST-READ**: [../../core/compliance-audit-methodology.md](../../core/compliance-audit-methodology.md) for compliance scoring and pass criteria

🚨 **CRITICAL**: Do not proceed to Phase 4 unless this task confirms full compliance.

---

## Instructions

### Step 1: Verify All Metrics Meet Targets

Confirm each metric meets or exceeds target (from Task 9 re-validation):

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| File Size | ≥95% | {%} | ✅/❌ |
| Command Coverage | ≥80% | {%} | ✅/❌ |
| Three-Tier | Pass | {status} | ✅/❌ |
| Gates | 100% | {%} | ✅/❌ |
| Contract | Present | {status} | ✅/❌ |
| Decomposition | Pass | {status} | ✅/❌ |

⚠️ **CONSTRAINT**: ALL must show ✅ to pass.

### Step 2: Confirm Zero Critical Violations

From Task 9 re-validation:
- Critical violations: {count}
- **Expected**: 0 critical

If any remain: 🚨 STOP, return to Task 8.

### Step 3: Review Final Compliance Report

Read updated compliance report (from Task 9), confirm:
- All 5 principles passing
- Compliance score ≥95%
- No blocking issues
- All critical fixes applied

### Step 4: Spot Check Workflow Integrity

Quick spot checks:
- **Navigation**: Pick 3 phases, verify links work
- **Gates**: Pick 3 phases, verify gates parseable
- **Tasks**: Pick 5 tasks, verify size, commands, quality

### Step 5: Calculate Final Score

Use formula from core/compliance-audit-methodology.md.

**Required**: ≥95%

### Step 6: Generate Certification & Prepare Evidence

Create certification with:
- Workflow name/version/date
- All 5 principles certified (✅ for each)
- Final compliance score
- Violation counts (0 critical)
- Status: READY FOR TESTING

Add to compliance report.

Gather evidence for Phase 3 gate:
- All 6 metrics meeting requirements
- Verify values meet gate criteria

---

## Expected Output

**Evidence for Validation Gate**:
- `file_size_compliance_percent`: Integer (≥95)
- `command_coverage_percent`: Integer (≥80)
- `three_tier_validated`: Boolean (true)
- `gate_coverage_percent`: Integer (100)
- `binding_contract_present`: Boolean (true)
- `violations_fixed`: Boolean (true)

**Additional Outputs**:
- `final_compliance_score`: Integer (≥95)
- `certification_issued`: Boolean (true)
- `ready_for_testing`: Boolean (true)

---

---

## Checkpoint Evidence

Submit the following evidence to complete Phase 3:

```yaml
evidence:
  file_size_compliance_percent: {value}
  command_coverage_percent: {value}
  three_tier_validated: true
  gate_coverage_percent: 100
  binding_contract_present: true
  violations_fixed: true
```

---

## Navigation

🎯 **NEXT-MANDATORY**: ../5/phase.md (begin Phase 5 after checkpoint passes)

↩️ **RETURN-TO**: phase.md (after task complete, before phase submission)


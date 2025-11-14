# Task 7: Generate Compliance Report

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Document all metrics and findings  
**Depends On**: Tasks 1-6 (all audits complete)  
**Feeds Into**: Task 8 (Fix Violations)

---

## Objective

Consolidate all audit results from Tasks 1-6 into a comprehensive meta-workflow compliance report.

---

## Context

📊 **CONTEXT**: This report provides a complete picture of workflow quality, combining metrics from all 5 meta-workflow principles. It will guide the fix process in Task 8 and serve as evidence for phase completion.

⚠️ **MUST-READ**: [../../core/compliance-audit-methodology.md](../../core/compliance-audit-methodology.md) section on "Compliance Scoring" and "Compliance Report Structure" for scoring formulas and report format

---

## Instructions

### Step 1: Gather All Audit Results

Collect reports and metrics from Tasks 1-6:
- File size audit, command coverage audit
- Three-tier verification, validation gates verification
- Binding contract verification, horizontal decomposition verification

### Step 2: Create Executive Summary

Use executive summary template from core/compliance-audit-methodology.md.

Summarize:
- Overall compliance status (PASS/FAIL)
- Each of 5 principles (PASS/FAIL + summary)
- Critical issues count
- Total fixes needed

### Step 3: Detail Each Principle

For each of 5 principles, use detailed assessment format from core/:

**Include for each**:
- Compliance percentage
- Status (PASS/FAIL)
- Key metrics from Tasks 1-6
- Issues found
- Recommendations

### Step 4: Create Violations Summary

Use violations table format from core/ to consolidate:
- All violations across principles
- Severity classification (Critical/High/Medium/Low)
- Specific files/locations
- Required fixes

### Step 5: Calculate Compliance Score

Use scoring formula from core/compliance-audit-methodology.md:
- Weight each component appropriately
- Calculate overall score (0-100)
- Determine PASS/FAIL (threshold ≥95%)

### Step 6: Document Strengths

Balance report with positive observations:
- What workflow does well
- Effective patterns used
- Quality achievements

### Step 7: Create Fix Priority List

Order fixes by urgency using format from core/:
- Must Fix (blocking)
- Should Fix (important)
- Nice to Fix (optional)

### Step 8: Write Compliance Report File

Write the complete report to:

```
{workflow_directory_path}/supporting-docs/compliance-report.md
```

📖 **DISCOVER-TOOL**: Write content to a file

### Step 9: Verify Report Completeness

Read the report back and confirm:
- All principles assessed
- All metrics included
- Violations clearly documented
- Fixes prioritized
- Compliance score calculated

---

## Expected Output

**Variables to Capture**:
- `compliance_score`: Integer (0-100)
- `total_violations`: Integer
- `critical_violations`: Integer
- `compliance_report_path`: String
- `compliance_report_complete`: Boolean

---

## Quality Checks

✅ All audit results gathered  
✅ Executive summary created  
✅ Each principle assessed  
✅ Violations consolidated  
✅ Compliance score calculated  
✅ Strengths documented  
✅ Fix priorities established  
✅ Report written and verified

---

## Navigation

🎯 **NEXT-MANDATORY**: task-8-fix-violations.md

↩️ **RETURN-TO**: phase.md (after task complete)


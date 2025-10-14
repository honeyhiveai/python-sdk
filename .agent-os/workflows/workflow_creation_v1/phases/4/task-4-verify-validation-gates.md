# Task 4: Verify Validation Gates

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Check every phase has gate with parseable evidence  
**Depends On**: All phases created  
**Feeds Into**: Task 5 (Verify Binding Contract)

---

## Objective

Verify that every phase has a complete, parseable validation gate with proper evidence fields that the CheckpointLoader can process.

---

## Context

📊 **CONTEXT**: Validation gates are the programmatic checkpoints that enforce quality at phase boundaries. The workflow_engine.py uses CheckpointLoader to parse gates and validate evidence.

⚠️ **MUST-READ**: [../../core/compliance-audit-methodology.md](../../core/compliance-audit-methodology.md) section on "Validation Gate Compliance" for gate requirements, parseability patterns, and verification procedures

🔍 **MUST-SEARCH**: "validation gates checkpoint loader evidence fields"

**Target**: 100% of phases have compliant validation gates

---

## Instructions

### Step 1: Locate All Phase Files

Find all phase.md files:

```
{workflow_directory_path}/phases/*/phase.md
```

📖 **DISCOVER-TOOL**: List all phase directories

Count total phases.

### Step 2: Check Each Phase for Validation Gate

For each phase.md, verify:
- "## Validation Gate" header present
- "Evidence Required" section present
- At least 1 evidence field defined

⚠️ **CONSTRAINT**: EVERY phase must have a validation gate. No exceptions.

If any missing: 🚨 **CRITICAL** fatal violation

### Step 3: Verify Gate Structure and Parseability

For each gate, verify using patterns from core/compliance-audit-methodology.md:

**Required Elements**:
- 🚨 CRITICAL marker
- Evidence Required section
- Minimum 1 evidence field
- Human approval flag

**Evidence Field Format** (table or prose):
- Field names: Backticks, snake_case
- Types: Valid (string, boolean, integer, array, object)
- Validators: Valid names (is_true, file_exists, etc.)
- Descriptions: Present and clear

### Step 4: Check Evidence Fields Match Task Outputs

For each phase, verify evidence fields correspond to actual task outputs:
- Read phase's task files
- Identify what each task produces
- Confirm gate requests evidence for key outputs

Missing fields or orphaned fields indicate misalignment.

### Step 5: Calculate Gate Coverage

Calculate metrics:

```
gate_coverage = (phases_with_gates / total_phases) * 100
parseable_gate_percentage = (parseable_gates / total_gates) * 100
```

**Target**: 
- Gate coverage: 100%
- Parse able: 100%

### Step 6: Generate Validation Gate Report

Use report format from core/compliance-audit-methodology.md:

```markdown
# Validation Gate Verification Report

**Total Phases**: {count}
**Phases with Gates**: {count} ({percent}%)
**Parseable Gates**: {count} ({percent}%)

## Gate Coverage: {PASS/FAIL}

## Issues Found
[List phases with missing or non-parseable gates]

## Status: {PASS/FAIL}
```

Write to temporary analysis file or include in Task 7's compliance report.

---

## Expected Output

**Metrics**:
- `total_phases`: Integer
- `phases_with_gates`: Integer
- `gate_coverage_percent`: Integer (0-100)
- `parseable_gates_count`: Integer
- `parseable_gate_percent`: Integer (0-100)

**Issues**:
- `missing_gates`: Array of phase numbers
- `non_parseable_gates`: Array of phase numbers with issues
- `gate_issues`: Array of specific problems

**Report**:
- `validation_gate_report`: String (formatted report)

**Evidence for Task 7**:
- `gate_coverage_percent`: Must be 100
- `gate_parseability_percent`: Must be 100

---

## Quality Checks

✅ All phases located  
✅ Gate presence verified for each  
✅ Gate structure validated  
✅ Evidence parseability confirmed  
✅ Evidence fields match outputs  
✅ Coverage calculated  
✅ Report generated

---

## Checkpoint Evidence

This task feeds into Phase 3 final checkpoint (Task 10).

Metrics feed into Task 7 (Generate Compliance Report).

---

## Navigation

🎯 **NEXT-MANDATORY**: task-5-verify-binding-contract.md

↩️ **RETURN-TO**: phase.md


# Task 3: Validate Gates Parseable

**Phase**: 5 - Testing & Delivery  
**Purpose**: Confirm gates use indicator keywords CheckpointLoader can parse  
**Depends On**: Task 2 (commands validated), Phase 3 (gates verified)  
**Feeds Into**: Task 4 (Identify Usability Issues)

---

## Objective

Test that validation gates use the specific indicator keywords and format patterns that the CheckpointLoader can reliably parse during workflow execution.

---

## Context

📊 **CONTEXT**: The workflow_engine.py uses CheckpointLoader to dynamically parse validation gates from markdown. Gates must follow specific patterns with indicator keywords for successful parsing.

⚠️ **MUST-READ**: [../../core/compliance-audit-methodology.md](../../core/compliance-audit-methodology.md) section on "Validation Gate Parsing" for parseability requirements, common errors, and fix strategies

🔍 **MUST-SEARCH**: "checkpoint loader parsing patterns indicator keywords"

---

## Instructions

### Step 1: Review Parseability Requirements

From core/compliance-audit-methodology.md, understand:
- Required indicator keywords
- Format patterns (table vs prose)
- Field name format (backticks, snake_case)
- Valid types and validators
- Common parse errors

### Step 2: Locate All Validation Gates

Find all phase.md files:

```
{workflow_directory_path}/phases/*/phase.md
```

📖 **DISCOVER-TOOL**: List phase directories

### Step 3: Check Indicator Keywords

For each validation gate, verify presence of:
- "Validation Gate" header
- "Evidence Required" section
- At least one evidence field
- Human approval flag

⚠️ **CONSTRAINT**: Missing ANY indicator keyword may cause parse failure.

### Step 4: Validate Evidence Field Format

For each gate, check evidence fields follow patterns from core methodology:
- **Field names**: Backticks, snake_case, no spaces/special chars
- **Types**: Valid types (string, boolean, integer, array, object)
- **Validators**: Valid validators (is_true, file_exists, percent_gte_X, etc.)
- **Format**: Consistent table or prose format

### Step 5: Test Parse Simulation

For 3-5 sample gates, manually parse:
1. Extract "Evidence Required" section
2. Parse field definitions
3. Verify no ambiguity

Document any gates where parsing is unclear.

### Step 6: Generate Parseability Report

Use format from core/compliance-audit-methodology.md with:
- Total gates tested
- Parseable vs non-parseable count
- Indicator keyword check results
- Evidence field format issues
- Parse simulation results
- Issues found with specific fixes
- Overall status (PASS/FAIL)

---

## Expected Output

**Variables to Capture**:
- `gates_parseable`: Boolean (true if all can be parsed)
- `parse_issues`: Array (list of issues if any)
- `parseable_gates_count`: Integer
- `parseability_report`: String

**If Parse Issues Found**:
- Document specific formatting problems
- May need to return to Phase 3 Task 8 for fixes

---

## Quality Checks

✅ CheckpointLoader requirements understood  
✅ All gates located  
✅ Indicator keywords verified  
✅ Evidence field format validated  
✅ Field names properly formatted  
✅ Types validated  
✅ Validators verified  
✅ Parse simulation performed  
✅ Parseability report generated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-4-identify-usability-issues.md

↩️ **RETURN-TO**: phase.md (after task complete)


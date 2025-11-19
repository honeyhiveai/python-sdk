# Compliance Audit Methodology

**Type**: Tier 2 (Methodology - On-Demand Reading)  
**Purpose**: Systematic approach for auditing workflow compliance with meta-workflow principles  
**Referenced by**: Phase 3, Tasks 1-10

---

## Overview

This document provides comprehensive methodology for auditing workflows against all meta-workflow compliance requirements. It covers file size auditing, command coverage calculation, validation gate parsing, and compliance reporting.

---

## File Size Auditing

### Line Counting Standards

**Compliant**: ≤100 lines  
**Acceptable**: 101-150 lines (critical content)  
**Compress Needed**: 151-170 lines (really try to scrunch)  
**Must Split**: >170 lines (should be 2 tasks)

### Audit Process

**Step 1: Locate All Task Files**

Pattern: `{workflow_dir}/phases/*/task-*.md`

**Step 2: Count Lines Accurately**

Use actual line count, not estimated:
```bash
wc -l file.md
```

Count includes:
- All content lines
- Blank lines
- Comment lines
- Headers
- Code blocks

**Step 3: Categorize Files**

```
if lines <= 100:
    category = "compliant"
elif lines <= 150:
    category = "acceptable"
elif lines <= 170:
    category = "compress_needed"
else:
    category = "must_split"
```

**Step 4: Calculate Compliance Percentage**

```
compliance_percent = (compliant_count / total_files) * 100
```

Target: ≥95%

**Step 5: Calculate Excess Lines**

For non-compliant files:
```
excess = current_lines - 100
```

### Violation Documentation Format

```markdown
## File Size Violations

### Must Split (>170 lines)
- **{filename}**: {lines} lines (+{excess} over)
  - **Suggested split**: {strategy}
  
### Compress Needed (151-170)
- **{filename}**: {lines} lines (+{excess} over)
  - **Compression strategy**: {approach}

### Acceptable (101-150)
- **{filename}**: {lines} lines (+{excess} over)
  - **Reason critical**: {justification}
```

### Split Strategies

**Strategy 1: Logical Breakpoint Split**
- Identify natural section boundaries
- Split between major steps
- Example: Steps 1-5 → Task A, Steps 6-10 → Task B

**Strategy 2: Before/After Split**
- Preparation vs. execution
- Setup vs. validation
- Example: "prepare-data" + "validate-data"

**Strategy 3: Generate/Review Split**
- Generation task
- Review/refinement task
- Example: "generate-report" + "review-report"

**Strategy 4: Extract Methodology**
- Move detailed methodology to core/
- Keep task file with steps + reference
- Example: Move parsing logic to core/, keep task slim

---

## Command Coverage Auditing

### Command Symbol Inventory

Standard commands to count:
- 🎯 NEXT-MANDATORY
- ↩️ RETURN-TO
- 📊 CONTEXT
- ⚠️ CONSTRAINT
- 🚨 CRITICAL
- 🔍 MUST-SEARCH
- 📖 DISCOVER-TOOL
- 🔄 LOOP-START / LOOP-END

### Coverage Calculation

**Step 1: Count Command Instances**

Per file:
```bash
grep -o "🎯\|🔍\|⚠️\|🚨\|📖\|📊\|↩️\|🔄" file.md | wc -l
```

Count unique command instances, not repeated symbols on same line.

**Step 2: Count Instructional Lines**

Instructional lines include:
- Step headers and descriptions
- Commands (with symbols)
- Tool usage descriptions
- Conditional logic
- Requirement statements

Exclude:
- Headers (# ## ###)
- Blank lines
- Pure context paragraphs (prose without directives)
- Navigation sections
- Metadata fields

**Step 3: Calculate Coverage**

```
file_coverage = (command_lines / instructional_lines) * 100
overall_coverage = (total_command_lines / total_instructional_lines) * 100
```

**Step 4: Categorize Files**

- **Excellent**: ≥90%
- **Good**: 80-89%
- **Needs Improvement**: 70-79%
- **Non-compliant**: <70%

Target: ≥80% overall

### Low Coverage Improvement

**Common Patterns to Fix**:

❌ **Natural language**: "Check if the file exists"  
✅ **Command**: `📖 DISCOVER-TOOL: Check if file exists`

❌ **Soft requirement**: "You should verify..."  
✅ **Binding**: `⚠️ CONSTRAINT: Must verify before proceeding`

❌ **Unclear next step**: "Then proceed to next task"  
✅ **Explicit**: `🎯 NEXT-MANDATORY: task-2-name.md`

❌ **Missing context**: Jumps into instructions  
✅ **With context**: `📊 CONTEXT: This validates...`

---

## Three-Tier Architecture Validation

### Tier Definitions

**Tier 1 (Execution)**: Task files
- Read every execution
- **Limit**: ≤100 lines (≤150 acceptable, ≤170 compress, >170 split)
- **Focus**: Actionable steps
- **Pattern**: Imperative instructions with command symbols

**Tier 2 (Methodology)**: Phase overviews, core/ files
- Read once per phase or on-demand
- **Target**: ~80-120 lines for phase.md, 200-400 for core/ files
- **Focus**: Context, structure, methodology
- **Pattern**: Declarative explanations

**Tier 3 (Outputs)**: Supporting docs, generated artifacts
- Rarely re-read
- **Limit**: Unlimited
- **Focus**: Reference materials
- **Pattern**: Generated reports, archives

### Tier Boundary Validation

**Check 1: No Tier 3 in Tier 1**

Task files should NOT contain:
- Long reference tables
- Complete templates (link to them)
- Extensive examples (summarize, link to full)
- Historical documentation

**Fix**: Move to supporting-docs/, reference with 🔍 MUST-SEARCH

**Check 2: No Tier 1 in Tier 2**

Phase overviews should NOT contain:
- Step-by-step instructions (those go in tasks)
- Detailed command sequences
- Specific file paths

**Fix**: Move to appropriate task files

**Check 3: Tier 2 Appropriate Size**

Phase overviews:
- Target: ~80 lines
- Acceptable: ≤150 lines
- Issue if: >150 lines

**Fix**: Extract detailed content to tasks or core/ files

---

## Validation Gate Parsing

### ParseabilityChecklist

For each validation gate, verify:

**Element 1: Header Present**
```markdown
## Validation Gate
```

**Element 2: Indicator Keywords**
- "Evidence Required" or "Required Evidence"
- "Human Approval" or "Human Approval Required"

**Element 3: Evidence Fields**

Table format:
```markdown
| Evidence | Type | Validator | Description |
|----------|------|-----------|-------------|
| `field_name` | string | is_true | Description |
```

Or prose format:
```markdown
- `field_name` (string): Description [validator: is_true]
```

**Element 4: Field Name Format**
- Backtick-enclosed: `` `field_name` ``
- Snake_case: `field_size_compliance`
- No spaces or special chars

**Element 5: Valid Types**
- string, boolean, integer, array, object

**Element 6: Valid Validators**
- is_true, is_false
- file_exists, directory_exists
- greater_than_0
- percent_gte_95, percent_gte_80, percent_gte_100
- equals

### Common Parse Errors

**Error**: Missing backticks  
**Pattern**: `field_name` vs field_name  
**Fix**: Always use backticks

**Error**: Wrong type name  
**Pattern**: `bool` vs `boolean`, `int` vs `integer`  
**Fix**: Use full type names

**Error**: Misspelled validator  
**Pattern**: `is_True` vs `is_true`  
**Fix**: Lowercase, underscores

**Error**: Inconsistent formatting  
**Pattern**: Mix of table and prose  
**Fix**: Choose one format per gate

---

## Compliance Scoring

### Score Calculation

```
compliance_score = (
  (file_size_compliance * 0.20) +      # 20% weight
  (command_coverage * 0.20) +          # 20% weight
  (three_tier_compliance * 0.15) +     # 15% weight
  (gate_coverage * 0.25) +             # 25% weight
  (binding_contract * 0.10) +          # 10% weight
  (horizontal_decomposition * 0.10)    # 10% weight
)
```

**Passing Threshold**: ≥95%

### Component Scoring

**File Size Compliance** (0-100):
```
score = (compliant_files / total_files) * 100
```

**Command Coverage** (0-100):
```
score = (total_commands / total_instructions) * 100
```

**Three-Tier Compliance** (0 or 100):
```
score = 100 if all_tiers_compliant else 0
```

**Gate Coverage** (0-100):
```
score = (phases_with_gates / total_phases) * 100
```

**Binding Contract** (0 or 100):
```
score = 100 if contract_present else 0
```

**Horizontal Decomposition** (0-100):
```
score = 100 - (god_tasks_count * 10)  # Penalize god tasks
```

---

## Compliance Report Structure

```markdown
# Meta-Workflow Compliance Report

**Workflow**: {name} v{version}
**Generated**: {date}
**Overall Score**: {score}% {PASS/FAIL}

## Executive Summary

[One paragraph overview]

## Detailed Assessments

### 1. LLM Constraint Awareness: {score}% {PASS/FAIL}

**File Size Compliance**: {percent}%
- Target: ≥95%
- Compliant: {count}/{total}
- Violations: {count}

**Findings**:
- {Finding 1}
- {Finding 2}

**Recommendations**:
- {Recommendation 1}

---

[Repeat for each principle]

## Violations Summary

| Severity | Principle | Issue | File | Fix |
|----------|-----------|-------|------|-----|
| Critical | {principle} | {issue} | {file} | {fix} |
| High | {principle} | {issue} | {file} | {fix} |

## Fix Priority List

### Must Fix (Blocking)
1. {Issue with specific fix}
2. {Issue with specific fix}

### Should Fix (Important)
3. {Issue with specific fix}

### Nice to Fix (Optional)
10. {Issue with specific fix}

## Strengths

- {What workflow does well}
- {What workflow does well}

## Overall Compliance: {PASS/FAIL}
```

---

## Re-Validation Process

After fixes applied:

1. **Re-run all audits**
2. **Compare metrics**: Before vs After
3. **Check for regressions**: New issues introduced?
4. **Verify fixes effective**: Issues resolved?
5. **Update compliance score**
6. **Generate comparison table**

```markdown
## Metrics Comparison

| Metric | Before | After | Change | Status |
|--------|--------|-------|--------|--------|
| File Size | {%} | {%} | +{delta}% | ✅/⚠️/❌ |
| Command Coverage | {%} | {%} | +{delta}% | ✅/⚠️/❌ |
```

---

**Use this methodology to conduct thorough, consistent compliance audits for any workflow.**


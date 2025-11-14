# Task 3: Verify Three-Tier

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Validate tier separation (task ≤100, entry 200-500, outputs unrestricted)  
**Depends On**: Task 1 (file sizes known)  
**Feeds Into**: Task 4 (Verify Validation Gates)

---

## Objective

Verify the workflow follows the three-tier architecture pattern for organizing content by AI consumption model.

---

## Context

📊 **CONTEXT**: The three-tier architecture separates workflow content into tiers based on how AI agents consume them during execution.

🔍 **MUST-SEARCH**: "three-tier architecture workflow organization"

**Tier Structure**:
- **Tier 1 (Execution)**: Task files, read every time, ≤100 lines
- **Tier 2 (Methodology)**: Phase overviews, read once per phase, 200-500 lines
- **Tier 3 (Outputs)**: Generated artifacts, rarely re-read, unlimited size

---

## Instructions

### Step 1: Verify Tier 1 (Execution Files)

**Files**: All task-*.md files

**Requirements**:
- ≤100 lines (covered in Task 1)
- Focused, single-purpose instructions
- Read every execution
- High command coverage

From Task 1 results, confirm ≥95% of task files meet size requirement.

### Step 2: Verify Tier 2 (Methodology Files)

**Files**: phase.md files

**Requirements**:
- Approximately 80-120 lines (concise overviews)
- Read once at phase start
- Provide context and navigation
- Not step-by-step instructions

For each phase.md file:

📖 **DISCOVER-TOOL**: Count lines in file

Check line count is reasonable (target ~80 lines, acceptable up to 150).

If any phase.md >200 lines:
- Document as violation
- Suggest moving detailed content to task files or supporting docs

### Step 3: Verify Tier 3 (Output Files)

**Files**: Supporting docs, compliance reports, generated artifacts

**Requirements**:
- Can be any length
- Rarely re-read by AI
- Reference materials
- Not part of execution flow

Check that Tier 3 files are properly located:
- `supporting-docs/` directory
- `core/` directory
- Generated during workflow (not read during execution)

### Step 4: Check for Tier Violations

Common violations:
- Task files >100 lines (Tier 1 violation)
- Phase overviews with step-by-step instructions (Tier 2 → Tier 1 bleed)
- Large reference content in task files (Tier 3 → Tier 1 bleed)
- Execution instructions in supporting docs (Tier 1 → Tier 3 bleed)

Document any violations found.

### Step 5: Verify Proper Tier References

Check that:
- Tier 1 (tasks) reference Tier 3 (docs) via 🔍 MUST-SEARCH, not inline duplication
- Tier 2 (phases) summarize without duplicating Tier 1 content
- Tier 3 (docs) stand alone and don't require reading other tiers

### Step 6: Generate Three-Tier Compliance Report

```markdown
# Three-Tier Architecture Compliance Report

## Tier 1: Execution Files (Task Files)
**Total Files**: {count}
**Size Compliance**: {percent}% ≤100 lines
**Status**: {PASS/FAIL}

## Tier 2: Methodology Files (Phase Overviews)
**Total Files**: {count}
**Average Size**: {lines} lines
**Target**: ~80 lines (acceptable ≤150)
**Status**: {PASS/FAIL}

## Tier 3: Output Files (Supporting Docs)
**Total Files**: {count}
**Properly Located**: {yes/no}
**Status**: {PASS/FAIL}

## Violations
[List any tier boundary violations]

## Overall Compliance
{PASS/FAIL}
```

---

## Expected Output

**Variables to Capture**:
- `three_tier_validated`: Boolean (true if compliant)
- `tier_violations`: Array (list of violations if any)
- `tier_compliance_report`: String (report content)

---

## Quality Checks

✅ Tier 1 files verified (≤100 lines)  
✅ Tier 2 files verified (~80 lines)  
✅ Tier 3 files properly located  
✅ Tier boundaries respected  
✅ Proper tier references used  
✅ Violations documented  
✅ Compliance report generated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-4-verify-validation-gates.md

↩️ **RETURN-TO**: phase.md (after task complete)


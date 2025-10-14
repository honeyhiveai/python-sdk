# Task 1: Audit File Sizes

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Check all task files across all phases  
**Depends On**: All target workflow phases created  
**Feeds Into**: Task 2 (Audit Command Coverage)

---

## Objective

Audit all task files in the created workflow to ensure ≥95% comply with the ≤100 line constraint for horizontal decomposition.

---

## Context

📊 **CONTEXT**: The 100-line limit per task file is a core principle of LLM Constraint Awareness. It ensures tasks fit comfortably in AI context windows and forces proper decomposition.

Target: **≥95% of task files ≤100 lines**

---

## Instructions

### Step 1: Locate All Task Files

Find all task files in the created workflow:

```
{workflow_directory_path}/phases/*/task-*.md
```

📖 **DISCOVER-TOOL**: Find files matching a pattern or list all files recursively

Count total task files found.

### Step 2: Count Lines in Each File

For each task file, count the number of lines.

📖 **DISCOVER-TOOL**: Count lines in a file

Example command pattern:
```bash
wc -l {file_path}
```

⚠️ **CONSTRAINT**: Use actual line count, not estimated. Blank lines and comments count toward the total.

### Step 3: Categorize Files

Categorize each file:
- **Compliant**: ≤100 lines
- **Acceptable**: 101-120 lines (minor overflow)
- **Non-compliant**: >120 lines (needs decomposition)

### Step 4: Calculate Compliance Percentage

```
compliance_percent = (compliant_files / total_files) * 100
```

Target: ≥95%

### Step 5: Document Violations

For any non-compliant files (>120 lines), document:
- File path
- Current line count
- Excess lines (current - 100)
- Suggested split strategy

Example:
```
File: phases/2/task-3-complex-operation.md
Lines: 145
Excess: 45 lines
Suggestion: Split into task-3-complex-operation-part-1.md and task-3-complex-operation-part-2.md
```

### Step 6: Store Results

Create a file size audit report:

```markdown
# File Size Audit Report

**Total Task Files**: {count}
**Compliant (≤100)**: {count} ({percent}%)
**Acceptable (101-120)**: {count} ({percent}%)
**Non-compliant (>120)**: {count} ({percent}%)

**Compliance**: {overall_percent}% {PASS/FAIL}

## Non-Compliant Files
[List with details]

## Acceptable Files (Minor Overflow)
[List]
```

---

## Expected Output

**Variables to Capture**:
- `total_task_files`: Integer
- `compliant_files`: Integer
- `file_size_compliance_percent`: Integer
- `non_compliant_files`: Array of objects with file details
- `file_size_audit_report`: String (report content)

---

## Quality Checks

✅ All task files located  
✅ Line counts accurate  
✅ Files categorized correctly  
✅ Compliance percentage calculated  
✅ Violations documented  
✅ Audit report created

---

## Navigation

🎯 **NEXT-MANDATORY**: task-2-audit-command-coverage.md

↩️ **RETURN-TO**: phase.md (after task complete)


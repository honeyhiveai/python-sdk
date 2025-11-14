# Task 2: Audit Command Coverage

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Count command vs natural language usage  
**Depends On**: Task 1 (file size audit complete)  
**Feeds Into**: Task 3 (Verify Three-Tier)

---

## Objective

Measure command language coverage across all task files to ensure ≥80% of instructions use command symbols for binding AI behavior.

---

## Context

📊 **CONTEXT**: The Command Language + Binding Contract principle requires that most instructions use standardized command symbols (🎯, 🔍, ⚠️, etc.) rather than natural language requests. This creates a reliable API for AI agents.

Target: **≥80% command coverage**

---

## Instructions

### Step 1: Identify Command Symbols to Count

From the command glossary, list all command symbols used:

Common commands:
- 🎯 NEXT-MANDATORY
- ↩️ RETURN-TO
- 📊 CONTEXT
- ⚠️ CONSTRAINT
- 🚨 CRITICAL
- 🔍 MUST-SEARCH
- 📖 DISCOVER-TOOL
- 🔄 LOOP-START / LOOP-END

### Step 2: Count Command Usage Per File

For each task file, count occurrences of command symbols.

📖 **DISCOVER-TOOL**: Search for pattern in files

Example command pattern:
```bash
grep -c "🎯\|🔍\|⚠️\|🚨\|📖\|📊\|↩️\|🔄" {file_path}
```

⚠️ **CONSTRAINT**: Count unique command instances, not repeated uses of same command on same line.

### Step 3: Count Total Instructional Lines

For each task file, count lines that contain instructions (not headers, blank lines, or pure prose).

Instructional content includes:
- Steps and substeps
- Commands (with symbols)
- Tool usage descriptions
- Conditional logic
- Examples with directives

Skip:
- Headers (# ## ###)
- Blank lines
- Pure context paragraphs
- Navigation sections
- Metadata (Phase:, Purpose:, etc.)

### Step 4: Calculate Coverage Per File

```
file_coverage = (command_lines / instructional_lines) * 100
```

Categorize:
- **Excellent**: ≥90%
- **Good**: 80-89%
- **Needs Improvement**: 70-79%
- **Non-compliant**: <70%

### Step 5: Calculate Overall Coverage

```
overall_coverage = (total_command_lines / total_instructional_lines) * 100
```

Target: ≥80%

### Step 6: Identify Low-Coverage Files

For files with <80% coverage, document:
- File path
- Current coverage
- Missing command opportunities
- Suggested improvements

Example:
```
File: phases/1/task-4-verify-setup.md
Coverage: 65%
Issue: Steps 2-4 use natural language ("Check if...", "Confirm that...")
Suggestion: Replace with 📖 DISCOVER-TOOL or ⚠️ CONSTRAINT
```

### Step 7: Generate Command Coverage Report

```markdown
# Command Coverage Audit Report

**Total Task Files**: {count}
**Average Coverage**: {percent}%
**Target**: ≥80%
**Status**: {PASS/FAIL}

## Coverage Distribution
- Excellent (≥90%): {count} files
- Good (80-89%): {count} files
- Needs Improvement (70-79%): {count} files
- Non-compliant (<70%): {count} files

## Low-Coverage Files
[List with improvement suggestions]
```

---

## Expected Output

**Variables to Capture**:
- `command_coverage_percent`: Integer (overall average)
- `low_coverage_files`: Array of files <80%
- `command_coverage_report`: String (report content)

---

## Quality Checks

✅ Command symbols identified  
✅ Usage counted per file  
✅ Instructional lines counted  
✅ Coverage calculated per file  
✅ Overall coverage calculated  
✅ Low-coverage files identified  
✅ Audit report generated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-3-verify-three-tier.md

↩️ **RETURN-TO**: phase.md (after task complete)


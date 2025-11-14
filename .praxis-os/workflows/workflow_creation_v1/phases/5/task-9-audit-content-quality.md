# Task 9: Audit Content Quality

**Phase**: 5 - Meta-Workflow Compliance  
**Purpose**: Verify task files contain actionable, detailed instructions (not generic stubs)  
**Depends On**: All previous validation tasks complete  
**Feeds Into**: Task 8 (Human Review)

---

## Objective

Audit all task files to ensure they contain detailed, actionable instructions rather than generic placeholders. Detect and flag stub content that would prevent AI agents from executing the workflow.

---

## Context

📊 **CONTEXT**: A workflow passes structural validation but may still contain generic placeholder content like "Execute the required actions for this task" or "Document outputs here". This validation ensures content is actionable and task files have sufficient detail for AI agent execution.

🎯 **TARGET**: **0 task files with generic placeholders**  
🎯 **TARGET**: Task files average 100-170 lines with 8+ detailed steps

🔍 **MUST-SEARCH**: "task file quality standards actionable instructions"

---

## Instructions

### Step 1: Define Generic Placeholder Patterns

Create a list of patterns that indicate stub content:

```python
generic_patterns = [
    "Execute the required actions",
    "Complete this task",
    "Document outputs here",
    "Task completed successfully",  # As sole quality check
    "Perform the necessary steps",
    "Follow standard procedures",
    "Apply best practices",  # Without specifics
    "Continue with implementation",
    "Do the required work",
    "Implement as needed"
]
```

📖 **DISCOVER-TOOL**: Pattern matching or text search

### Step 2: Scan All Task Files

For each task file in the generated workflow:

```
{workflow_directory_path}/phases/*/task-*.md
```

Search for generic patterns in the Instructions and Quality Checks sections.

📖 **DISCOVER-TOOL**: Read all task files

🔍 **MUST-SEARCH**: "how to detect generic placeholder content"

### Step 3: Validate Step Detail

For each task file, check the Instructions section:

**A. Steps Section Has Detail:**
- ❌ FAIL: Single generic step like `### Step 1: task-name\n\nExecute the required actions`
- ❌ FAIL: Steps with no actionable content
- ✅ PASS: Multiple specific steps (minimum 3, target 5-8+)
- ✅ PASS: Steps include tool markers (📖, 🔍, ⚠️, 🚨)

**B. Steps Include Tool Discovery:**
- ❌ FAIL: No tool markers (📖 DISCOVER-TOOL, 🔍 MUST-SEARCH)
- ✅ PASS: At least 1 tool marker per 3 steps

**C. Steps Are Actionable:**
- ❌ FAIL: Vague instructions like "Do the task" or "Complete the work"
- ✅ PASS: Specific actions like "Read file at {path}", "Search for pattern X", "Validate field Y"

**D. Steps Have Context:**
- ❌ FAIL: Steps without explanation or guidance
- ✅ PASS: Steps include why/how context or constraints

### Step 4: Validate Examples Present

Check Examples section exists and has concrete content:

**Requirements:**
- ❌ FAIL: No examples section present
- ❌ FAIL: Empty examples section
- ❌ FAIL: Generic "Add example here" placeholders
- ❌ FAIL: Examples section mentioned but not populated
- ✅ PASS: At least 1 concrete example with code/output/scenario
- ✅ PASS: Examples are realistic and instructive

**Example Quality Check:**
- Good: Shows actual code, configuration, or specific scenarios
- Bad: Placeholder text or generic "insert example" comments

### Step 5: Validate Quality Checks Specific

Check Quality Checks section has measurable criteria:

**Requirements:**
- ❌ FAIL: Single generic check like "Task completed successfully"
- ❌ FAIL: Fewer than 3 quality checks
- ❌ FAIL: Vague checks like "Output is good" or "Works correctly"
- ✅ PASS: Specific, measurable criteria (minimum 3, target 5+)
- ✅ PASS: Checks include what to verify and how

**Quality Check Examples:**
- Good: "Token count between 200-400", "All required fields present", "File size under 170 lines"
- Bad: "Task complete", "Looks good", "Finished"

### Step 6: Validate RAG Integration

For tasks with domain_focus specified:

**Requirements:**
- ❌ FAIL: No 🔍 **MUST-SEARCH** markers present
- ❌ FAIL: Domain mentioned but no guidance on querying
- ✅ PASS: At least 1 RAG query for domain knowledge
- ✅ PASS: Search queries are specific to domain

### Step 7: Validate File Size Indicators

Check file sizes as proxy for content richness:

**File Size Assessment:**
- ❌ CONCERN: < 60 lines (likely stub or minimal content)
- ⚠️ ACCEPTABLE: 60-99 lines (may lack detail)
- ✅ GOOD: 100-170 lines (target range)
- ⚠️ REVIEW: > 170 lines (may need decomposition)

📖 **DISCOVER-TOOL**: Count lines in files

### Step 8: Generate Content Quality Report

Create comprehensive report:

```markdown
# Content Quality Audit Report

**Generated**: {current_date}  
**Workflow**: {workflow_name}

## Summary

**Total Task Files**: {count}  
**Fully Actionable**: {count} ({percent}%)  
**Contains Generic Content**: {count} ({percent}%)  
**Missing Examples**: {count} ({percent}%)  
**Weak Quality Checks**: {count} ({percent}%)

**Overall Compliance**: {overall_percent}% {PASS/FAIL}

---

## Files with Generic Content

{For each flagged file:}

### {phase_number}/task-{task_number}-{task_name}.md

**Issues Found:**
- Generic patterns detected: {list patterns with line numbers}
- Missing elements: {examples, tool markers, specific checks}
- Line count: {count} (target: 100-170)
- Steps count: {count} (target: 5-8+)

**Recommendation**: Regenerate with properly extracted steps_outline and examples_needed from design document.

---

## Files with Missing Examples

{List files with no concrete examples}

---

## Files with Weak Quality Checks

{List files with generic or insufficient quality checks}

---

## File Size Distribution

- < 60 lines: {count} files
- 60-99 lines: {count} files
- 100-170 lines: {count} files (TARGET)
- > 170 lines: {count} files

---

## Command Language Coverage

**Tool Markers per Task (average)**: {average}
- 📖 DISCOVER-TOOL: {count} occurrences
- 🔍 MUST-SEARCH: {count} occurrences
- ⚠️ CONSTRAINT: {count} occurrences
- 🚨 CRITICAL: {count} occurrences

**Target**: Minimum 2-3 markers per task

---

## Recommendations

{If failures found:}

🚨 **CRITICAL ISSUES DETECTED**

The following must be fixed before workflow is production-ready:

1. {List specific fixes needed}
2. {Recommend re-running Phase 0 extraction with enhanced logic}
3. {Recommend regenerating flagged task files}

{If passed:}

✅ **CONTENT QUALITY VALIDATED**

All task files contain actionable, detailed instructions suitable for AI agent execution.
```

### Step 9: Determine Pass/Fail Status

Apply validation criteria:

**PASS Criteria** (ALL must be met):
- ✅ 0 files with generic placeholder patterns
- ✅ ≥ 95% of files have concrete examples
- ✅ ≥ 95% of files have specific quality checks (≥3 per task)
- ✅ ≥ 80% of files in 100-170 line range
- ✅ Average ≥ 5 steps per task
- ✅ Average ≥ 2 tool markers per task

**FAIL if**:
- ❌ Any file contains "Execute the required actions" as primary instruction
- ❌ > 5% of files missing examples
- ❌ > 5% of files have generic quality checks only
- ❌ Average task file < 80 lines

### Step 10: Fail Validation if Generic Content Found

If validation fails:

```
🚨 **CRITICAL**: Content quality validation FAILED

Workflow cannot proceed to human review until task files are regenerated with proper detail.

Root Cause: Phase 0 extraction likely did not capture steps_outline, examples_needed, or validation_criteria from design document.

Required Action: 
1. Review Phase 0 extraction output
2. Ensure design document has sufficient detail
3. Re-run Phase 0 with enhanced extraction
4. Regenerate task files in Phase 4
5. Re-run this validation
```

⚠️ **CONSTRAINT**: Workflow cannot be marked complete with failing content quality audit

---

## Expected Output

**Variables to Capture**:
- `content_quality_compliant_files`: Integer (count of fully compliant files)
- `content_quality_compliance_percent`: Integer (percentage)
- `generic_content_detected`: Boolean (True if any generic patterns found)
- `files_with_generic_content`: Array (list of file paths)
- `files_missing_examples`: Array
- `files_weak_quality_checks`: Array
- `average_file_size`: Integer (lines)
- `average_steps_per_task`: Integer
- `average_tool_markers_per_task`: Float
- `content_quality_report`: String (full report markdown)
- `validation_passed`: Boolean

---

## Quality Checks

✅ All task files scanned  
✅ Generic patterns detected and flagged  
✅ Step detail validated (minimum 3 per task)  
✅ Examples presence validated  
✅ Quality checks validated (minimum 3 per task)  
✅ RAG integration validated for domain tasks  
✅ File sizes assessed  
✅ Command language coverage measured  
✅ Comprehensive report generated  
✅ Pass/fail determination made  
✅ Validation criteria applied consistently

---

## Navigation

🎯 **NEXT-MANDATORY**: task-8-human-review.md (if validation passed)

⚠️ **IF-FAILED**: Return to Phase 0 or Phase 4 for regeneration

↩️ **RETURN-TO**: phase.md (after task complete)


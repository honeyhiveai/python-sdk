# Task 2: Validate Commands

**Phase**: 5 - Testing & Delivery  
**Purpose**: Confirm command language consistent and effective  
**Depends On**: Task 1 (dry run passing)  
**Feeds Into**: Task 3 (Validate Gates Parseable)

---

## Objective

Verify that command symbols are used consistently throughout the workflow and that command language patterns are clear and unambiguous.

---

## Context

📊 **CONTEXT**: The command language is the binding contract between workflow author and AI executor. Consistent, proper usage is critical for reliable execution.

⚠️ **MUST-READ**: [../../core/command-language-glossary.md](../../core/command-language-glossary.md) for complete command reference, usage patterns, and anti-patterns

🔍 **MUST-SEARCH**: "command language symbols binding contract"

---

## Instructions

### Step 1: Review Command Language Reference

From core/command-language-glossary.md, understand all command types:
- Discovery (📖 DISCOVER-TOOL)
- Navigation (🎯 NEXT-MANDATORY, ↩️ RETURN-TO)
- Constraints (⚠️ CONSTRAINT, 🚨 CRITICAL)
- Knowledge (🔍 MUST-SEARCH)
- Context (📊 CONTEXT)

### Step 2: Audit Command Usage Across Workflow

For each task file:
- Count command instances by type
- Calculate command presence
- Identify inconsistent usage
- Find missing commands

📖 **DISCOVER-TOOL**: Search for command symbols in all task files

Generate usage report with:
- Total commands, breakdown by type
- Files with no/low command usage
- Inconsistencies found

### Step 3: Verify Navigation Commands

Check all navigation:
- **🎯 NEXT-MANDATORY**: Every task except last in phase, correct target, consistent format
- **↩️ RETURN-TO**: Every task at end, points to phase.md

📖 **DISCOVER-TOOL**: Search and verify navigation commands

Document missing or broken navigation.

### Step 4: Verify Discovery Commands

Check all 📖 **DISCOVER-TOOL** usage:
- Used instead of hardcoded tool names
- Proper format and clarity
- Appropriate use cases

Common errors:
- Direct tool names ("use grep")
- Hardcoded tools ("run read_file")

### Step 5: Verify Constraints and Critical Markers

Check ⚠️ **CONSTRAINT** and 🚨 **CRITICAL** usage:
- Appropriate severity
- Clear and actionable
- No overuse or underuse

### Step 6: Verify Knowledge Retrieval Commands

Check 🔍 **MUST-SEARCH** usage:
- Queries are specific and discoverable
- Used for complex methodology
- Used instead of inline duplication

### Step 7: Check for Anti-Patterns

Identify issues from core/command-language-glossary.md:
- Mixed usage (inconsistent)
- Command redundancy
- Incorrect command selection
- Missing commands where needed

### Step 8: Generate Command Validation Report

Use report format:

```markdown
# Command Language Validation Report

**Total Tasks**: {count}
**Command Usage**: {total_commands} instances

## Usage Breakdown
- 📖 DISCOVER-TOOL: {count}
- 🎯 NEXT-MANDATORY: {count}
- ↩️ RETURN-TO: {count}
- ⚠️ CONSTRAINT: {count}
- 🚨 CRITICAL: {count}
- 🔍 MUST-SEARCH: {count}
- 📊 CONTEXT: {count}

## Issues Found
[List inconsistencies, missing commands, anti-patterns]

## Navigation Integrity: {✅/❌}
## Command Consistency: {✅/❌}

## Overall Status: {PASS/FAIL}
```

---

## Expected Output

**Metrics**:
- `total_commands`: Integer
- `command_breakdown`: Object with counts by type
- `tasks_with_low_commands`: Array
- `navigation_issues`: Array

**Report**:
- `command_validation_report`: String

**Evidence**:
- `navigation_intact`: Boolean (true if all navigation works)
- `command_usage_consistent`: Boolean (true if no major issues)

---

## Quality Checks

✅ Command reference reviewed  
✅ All tasks audited  
✅ Navigation verified  
✅ Discovery commands checked  
✅ Constraints/Critical validated  
✅ Knowledge retrieval verified  
✅ Anti-patterns identified  
✅ Report generated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-3-validate-gates-parseable.md

↩️ **RETURN-TO**: phase.md


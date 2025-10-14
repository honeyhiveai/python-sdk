# Task 6: Verify Horizontal Decomposition

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Confirm tasks follow single responsibility principle  
**Depends On**: All tasks created  
**Feeds Into**: Task 7 (Generate Compliance Report)

---

## Objective

Verify that the workflow demonstrates good horizontal decomposition: tasks are focused, have single responsibilities, and dependencies are clear.

---

## Context

📊 **CONTEXT**: Horizontal decomposition is a core meta-workflow principle. Tasks should be decomposed by single responsibility, not arbitrary grouping. This keeps tasks focused, maintainable, and easy to execute.

⚠️ **MUST-READ**: [../../core/compliance-audit-methodology.md](../../core/compliance-audit-methodology.md) section on "Horizontal Decomposition Assessment" for evaluation criteria and patterns

🔍 **MUST-SEARCH**: "horizontal decomposition single responsibility principle workflow tasks"

---

## Instructions

### Step 1: Review Decomposition Principles

From core/compliance-audit-methodology.md, understand:
- Single Responsibility Principle (one clear purpose per task)
- God Task anti-pattern (multiple responsibilities)
- Clear dependency chains
- Appropriate task granularity

### Step 2: Sample Tasks for Review

Select representative sample (~30% of tasks):
- Simple tasks (early phases)
- Complex tasks (middle/late phases)
- First and last tasks of phases
- Tasks with multiple dependencies

📖 **DISCOVER-TOOL**: List and read task files

### Step 3: Evaluate Each Sampled Task

For each task, assess:

**Single Responsibility**:
- Can purpose be stated in one sentence?
- Does task do one thing well?
- Could it be split further logically?

**Appropriate Scope**:
- Not too narrow (trivial sub-step)
- Not too broad (multiple responsibilities)
- Right level of granularity

**Clear Dependencies**:
- "Depends On" clearly stated?
- "Feeds Into" clearly stated?
- Dependencies logical and minimal?

**God Task Pattern** (anti-pattern):
- Does task have 2+ distinct responsibilities?
- Could it be split without losing coherence?
- Is it trying to do too much?

### Step 4: Check Phase-Level Decomposition

For each phase, verify:
- Tasks follow logical sequence
- No obvious gaps in workflow
- No unnecessary duplication
- Clear progression toward phase goal

### Step 5: Assess Overall Decomposition Quality

Rate decomposition quality:

**Excellent**: 
- All tasks single responsibility
- Clear dependencies
- Appropriate granularity
- No god tasks

**Good**:
- Most tasks well-decomposed
- 1-2 tasks could be split
- Dependencies mostly clear

**Fair**:
- Several tasks with multiple responsibilities
- Some unclear dependencies
- Inconsistent granularity

**Poor**:
- Many god tasks
- Unclear dependencies
- Poor granularity

### Step 6: Generate Decomposition Report

Use report format from core/compliance-audit-methodology.md:

```markdown
# Horizontal Decomposition Verification Report

**Tasks Reviewed**: {count} ({percent}% sample)

## Assessment

**Single Responsibility**: {Excellent/Good/Fair/Poor}
**Dependency Clarity**: {Excellent/Good/Fair/Poor}
**Task Granularity**: {Excellent/Good/Fair/Poor}
**Overall Quality**: {Excellent/Good/Fair/Poor}

## God Tasks Found
[List tasks with multiple responsibilities]

## Decomposition Issues
[List specific problems]

## Recommendations
[Suggestions for improvement]

## Status: {PASS/FAIL}
```

**Pass Criteria**: Overall quality "Good" or better, no critical god tasks

---

## Expected Output

**Assessment**: ratings for single_responsibility, dependency_clarity, granularity, overall  
**Issues**: god_tasks array, decomposition_issues array  
**Report**: decomposition_report string  
**Evidence for Task 7**: horizontal_decomposition_quality (must be "Good" or "Excellent")

---

## Quality Checks

✅ Decomposition principles reviewed  
✅ Task sample selected  
✅ Each task evaluated  
✅ Phase-level assessed  
✅ Overall quality rated  
✅ Report generated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-7-generate-compliance-report.md

↩️ **RETURN-TO**: phase.md


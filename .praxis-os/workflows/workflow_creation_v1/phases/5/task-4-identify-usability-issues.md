# Task 4: Identify Usability Issues

**Phase**: 5 - Testing & Delivery  
**Purpose**: Document friction points, unclear instructions  
**Depends On**: Tasks 1-3 (technical validation complete)  
**Feeds Into**: Task 5 (Implement Refinements)

---

## Objective

Review the workflow from a user experience perspective to identify areas where instructions are unclear, confusing, or create unnecessary friction.

---

## Context

📊 **CONTEXT**: Technical compliance doesn't guarantee usability. This task evaluates whether the workflow will be easy and intuitive for AI agents and human reviewers to use.

⚠️ **MUST-READ**: [../../core/usability-review-patterns.md](../../core/usability-review-patterns.md) for usability criteria framework, common friction patterns, evaluation rubric, and issue classification

---

## Instructions

### Step 1: Review Usability Framework

From core/usability-review-patterns.md, understand:
- 6 usability criteria (Clarity, Consistency, Efficiency, Context, Feedback, Error Handling)
- Common friction patterns (Missing Context, Ambiguous Instructions, Poor Error Handling, etc.)
- Severity classification (Critical/High/Medium/Low)
- Evaluation rubric

### Step 2: Sample Task Files

Select diverse sample (~30% coverage):
- Simple tasks (early phases)
- Complex tasks (later phases)
- Domain-specific tasks
- First-time vs repeated patterns

### Step 3: Evaluate Using Rubric

For each sampled task, apply evaluation rubric from core/:
- **Clarity** (1-5): Objective, instructions, terminology
- **Completeness** (1-5): Context, error handling, examples
- **Usability** (1-5): Flow, commands, tool discovery

Document score and specific issues.

### Step 4: Identify Friction Patterns

Using common patterns from core/, identify:
- Unclear objectives
- Missing context
- Ambiguous instructions
- Poor error handling
- Inconsistent terminology
- Navigation confusion
- Overwhelming complexity

### Step 5: Test Review Scenarios

Walk through scenarios from core/:
- **New user first time**: What confuses? Where stuck?
- **Experienced user returning**: Can resume? Progress clear?
- **Error recovery**: Recovery path clear? Can restart?

### Step 6: Classify and Document Issues

For each issue found, use format from core/:
- Issue title and location
- Severity (Critical/High/Medium/Low)
- Problem description
- User impact
- Suggested fix with example

### Step 7: Generate Usability Report

Use report structure from core/usability-review-patterns.md with:
- Tasks reviewed count
- Issue summary by severity
- Critical/High/Medium/Low issues with details
- Positive observations
- Overall usability rating
- Priority-ordered recommendations

---

## Expected Output

**Variables to Capture**:
- `usability_issues_count`: Integer (total issues found)
- `critical_usability_issues`: Integer
- `usability_issues`: Array (detailed list)
- `usability_report`: String (report content)

⚠️ **CONSTRAINT**: `usability_issues_count` must be > 0 for validation gate. Even excellent workflows have room for improvement.

---

## Quality Checks

✅ Usability criteria defined  
✅ Representative sample reviewed  
✅ Task clarity evaluated  
✅ Context sufficiency checked  
✅ Error handling assessed  
✅ Consistency verified  
✅ Navigation usability tested  
✅ Example scenarios walked through  
✅ Specific suggestions provided  
✅ Usability report generated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-5-implement-refinements.md

↩️ **RETURN-TO**: phase.md (after task complete)


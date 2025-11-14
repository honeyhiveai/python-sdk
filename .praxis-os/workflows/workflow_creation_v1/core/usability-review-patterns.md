# Usability Review Patterns

**Type**: Tier 2 (Methodology - On-Demand Reading)  
**Purpose**: Frameworks and patterns for conducting usability reviews of workflows  
**Referenced by**: Phase 4, Task 4

---

## Overview

This document provides systematic frameworks for evaluating workflow usability from a user experience perspective, including criteria, common friction patterns, and improvement strategies.

---

## Usability Criteria Framework

### Clarity
Instructions are unambiguous and easy to understand
- Single interpretation possible
- Technical terms explained
- Examples provided where helpful

### Consistency
Similar tasks use similar patterns
- Naming conventions followed
- Command usage consistent
- Structure predictable

### Efficiency
No unnecessary steps or redundancy
- Minimal overhead
- Direct paths to goals
- No duplicated work

### Context
Sufficient background provided
- Why before what
- Connections explained
- Prerequisites clear

### Feedback
Clear success/failure indicators
- Progress visible
- Results measurable
- Completion obvious

### Error Handling
Guidance for common problems
- Specific error scenarios
- Corrective actions
- Recovery paths clear

---

## Common Friction Patterns

### Pattern: Unclear Objective
**Symptoms**:
- Purpose statement vague
- Success criteria missing
- Multiple possible interpretations

**Assessment Questions**:
- Can you state the goal in one sentence?
- Is success measurable?
- Are there edge cases not addressed?

**Fix Strategies**:
- Rewrite objective with specific verb
- Add concrete success criteria
- Provide examples of outcomes

---

### Pattern: Missing Context
**Symptoms**:
- Jumps directly into steps
- No explanation of "why"
- Prerequisites unclear

**Assessment Questions**:
- Why is this task necessary?
- What happens if skipped?
- What should user know first?

**Fix Strategies**:
- Add 📊 CONTEXT section
- Explain role in larger process
- Link to prerequisites

---

### Pattern: Ambiguous Instructions
**Symptoms**:
- Multiple ways to interpret
- Conditional logic unclear
- Tools not specified

**Assessment Questions**:
- Could this be done wrong?
- Are conditionals clear (if/then)?
- Is tool discovery adequate?

**Fix Strategies**:
- Use command symbols (🎯, ⚠️, 📖)
- Break ambiguous steps into substeps
- Add concrete examples

---

### Pattern: Poor Error Handling
**Symptoms**:
- No guidance on failures
- Generic "if error" statements
- Missing recovery paths

**Assessment Questions**:
- What are common failure modes?
- How does user recover?
- When to escalate?

**Fix Strategies**:
- Document specific error scenarios
- Provide corrective actions
- Add 🚨 CRITICAL for fatal errors

---

### Pattern: Inconsistent Terminology
**Symptoms**:
- Same concept, different names
- Field names inconsistent
- Command usage varies

**Assessment Questions**:
- Are terms defined consistently?
- Do similar tasks use same patterns?
- Is glossary referenced?

**Fix Strategies**:
- Standardize terminology across workflow
- Reference command glossary
- Update all instances

---

### Pattern: Navigation Confusion
**Symptoms**:
- Unclear where in workflow
- Hard to find next task
- No progress indicators

**Assessment Questions**:
- Can user determine progress?
- Are phase transitions clear?
- Is return path obvious?

**Fix Strategies**:
- Add phase/task indicators to headers
- Use consistent 🎯 NEXT-MANDATORY
- Reference progress tracking

---

### Pattern: Overwhelming Complexity
**Symptoms**:
- Too many steps (>10)
- Multiple responsibilities
- Long file (>150 lines)

**Assessment Questions**:
- Can task be split?
- Is there a single responsibility?
- What's the core action?

**Fix Strategies**:
- Apply horizontal decomposition
- Extract methodology to core/
- Split into focused tasks

---

## Review Scenarios

### Scenario 1: New User First Time

**Perspective**: Complete novice to this workflow

**Questions to Ask**:
- What would confuse them?
- Where would they get stuck?
- Is quick start truly quick?
- Are prerequisites obvious?

**Focus Areas**:
- Phase 0 clarity
- First task accessibility
- Example quality
- Error recovery

---

### Scenario 2: Experienced User Returning

**Perspective**: Used workflow before, returning after time

**Questions to Ask**:
- Can they easily resume?
- Is progress tracking helpful?
- Are reference docs findable?
- Can they skip familiar parts?

**Focus Areas**:
- Progress tracking usability
- Navigation efficiency
- Reference documentation
- Resumption points

---

### Scenario 3: Error Recovery

**Perspective**: Something went wrong mid-workflow

**Questions to Ask**:
- Is error message clear?
- Can they determine cause?
- Is recovery path obvious?
- Can they restart from failure point?

**Focus Areas**:
- Error handling in tasks
- Validation gate clarity
- Checkpoint evidence
- Rollback procedures

---

## Evaluation Rubric

### Task-Level Assessment

For each sampled task, rate 1-5:

**Clarity** (1=Confusing, 5=Crystal Clear):
- Objective clarity
- Instruction clarity
- Terminology clarity

**Completeness** (1=Missing Key Info, 5=Comprehensive):
- Context provided
- Error handling
- Examples included

**Usability** (1=Difficult, 5=Easy):
- Step-by-step flow
- Command usage
- Tool discovery

**Overall Score**: Average of three ratings

**Interpretation**:
- 4.5-5.0: Excellent
- 3.5-4.4: Good
- 2.5-3.4: Needs improvement
- <2.5: Major revision needed

---

## Issue Severity Classification

### Critical (Blocking)
- Incorrect or impossible instructions
- Missing required information
- Navigation breaks workflow
- Fatal ambiguity

**Impact**: User cannot proceed  
**Priority**: Must fix immediately

### High (Major Friction)
- Unclear instructions causing confusion
- Missing context requiring guessing
- Inconsistent patterns
- Poor error handling

**Impact**: User struggles but can proceed  
**Priority**: Should fix before release

### Medium (Minor Friction)
- Verbose or inefficient wording
- Missing helpful examples
- Inconsistent formatting
- Minor terminology issues

**Impact**: User proceeds but experience degraded  
**Priority**: Good to fix if time permits

### Low (Polish)
- Cosmetic improvements
- Additional examples desired
- Enhanced explanations
- Nice-to-have features

**Impact**: Minimal  
**Priority**: Future enhancement

---

## Improvement Suggestions Format

For each issue identified, document:

```markdown
### Issue: [Short Title]

**Location**: [Phase N, Task M, Step X]
**Severity**: [Critical/High/Medium/Low]

**Problem**:
[Specific description of usability issue]

**User Impact**:
[How this affects workflow execution]

**Suggested Fix**:
[Concrete improvement to implement]

**Example** (if helpful):
[Show current vs improved version]
```

---

## Review Report Structure

```markdown
# Usability Review Report

**Tasks Reviewed**: {count} ({percent}% sample)
**Issues Found**: {count}

## Issue Summary
- Critical: {count}
- High: {count}
- Medium: {count}
- Low: {count}

## Critical Issues
[List with location, problem, fix]

## High Priority Issues
[List with location, problem, fix]

## Positive Observations
- [What works well]
- [Effective patterns]

## Overall Usability Rating
{Excellent/Good/Fair/Poor}

## Recommendations
[Priority-ordered list of improvements]
```

---

## Best Practices

### DO:
- Sample diverse tasks (early, middle, late phases)
- Think from user perspective
- Test actual scenarios
- Document specific issues
- Suggest concrete fixes

### DON'T:
- Review only one phase
- Assume expert knowledge
- Make vague criticisms
- Focus only on negatives
- Suggest unrealistic fixes

---

**Use this framework to conduct thorough, systematic usability reviews that improve workflow quality and user experience.**


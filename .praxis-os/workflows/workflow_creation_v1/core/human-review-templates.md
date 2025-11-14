# Human Review Templates & Procedures

**Type**: Tier 2 (Methodology - On-Demand Reading)  
**Purpose**: Templates and procedures for presenting workflows for human approval  
**Referenced by**: Phase 4, Task 8

---

## Overview

This document provides templates for presenting completed workflows to human reviewers for final approval, including review checklists, decision handling procedures, and approval documentation formats.

---

## Executive Summary Template

```markdown
# Workflow Review: {workflow_name} v{version}

## Summary
**Purpose**: {one-line purpose}
**Type**: {workflow_type}
**Complexity**: {count} phases, {count} tasks
**Status**: Ready for approval

## Key Metrics
- File Size Compliance: {percent}%
- Command Coverage: {percent}%
- Validation Gates: 100%
- Meta-Workflow Compliance: {percent}%

## Highlights
- [Key strength 1]
- [Key strength 2]
- [Key strength 3]

## Known Limitations
- [Limitation 1 if any]
- [Limitation 2 if any]

## Recommendation
✅ APPROVE for production use
```

---

## Presentation Format Template

```
=============================================================
WORKFLOW READY FOR HUMAN REVIEW
=============================================================

Workflow: {workflow_name} v{version}
Created: {date}
Location: {workflow_directory_path}

EXECUTIVE SUMMARY:
[Executive summary from above template]

REVIEW CHECKLIST:
□ Design aligns with stated problem
□ Phases and tasks make logical sense
□ Instructions are clear and actionable
□ Quality standards are appropriate
□ Workflow is likely to achieve its purpose
□ No major concerns or risks identified

APPROVAL REQUIRED:
Do you approve this workflow for production use?

[ ] APPROVE - Workflow is ready for production
[ ] APPROVE WITH MINOR CHANGES - Specify changes needed
[ ] REQUEST REVISIONS - Specify major issues to address
[ ] REJECT - Workflow needs significant rework

=============================================================
```

---

## Review Guidance for Human Reviewer

### Quick Review (~15 minutes)
1. Read design summary
2. Review phase structure (phase.md files)
3. Sample 5-10 task files
4. Check compliance report highlights
5. Review usage guide introduction

### Thorough Review (~45 minutes)
1. Read complete design summary and usage guide
2. Review all phase overviews
3. Sample 30% of task files
4. Verify validation gates make sense
5. Check command language usage
6. Assess overall coherence and quality

### Deep Review (~2 hours)
1. Read every phase and task file
2. Trace navigation paths
3. Validate all validation gates
4. Check supporting documentation
5. Assess production readiness thoroughly

**Recommendation**: Minimum Quick Review, preferably Thorough

---

## Decision Handling Procedures

### APPROVED

**Feedback Capture Format**:
```yaml
review:
  decision: APPROVED
  reviewer: {name}
  date: {date}
  comments: |
    {any feedback or notes}
```

**Next Steps**:
1. Create approval.md in supporting-docs/
2. Update metadata.json with approval fields
3. Create CHANGELOG.md
4. Prepare for distribution

---

### APPROVED WITH MINOR CHANGES

**Feedback Capture Format**:
```yaml
review:
  decision: APPROVED_WITH_CHANGES
  reviewer: {name}
  date: {date}
  changes_requested:
    - {change 1}
    - {change 2}
  comments: |
    {additional feedback}
```

**Next Steps**:
1. Document requested changes
2. Implement minor changes
3. Re-present modified sections
4. Obtain final approval
5. Proceed to APPROVED steps

---

### REQUEST REVISIONS

**Feedback Capture Format**:
```yaml
review:
  decision: REVISIONS_REQUESTED
  reviewer: {name}
  date: {date}
  issues:
    - {issue 1}
    - {issue 2}
  comments: |
    {detailed feedback}
```

**Next Steps**:
1. Document all issues to address
2. Return to appropriate phase (likely Phase 4 Task 5)
3. Make revisions
4. Re-run validation (Task 7)
5. Re-present for review (Task 8)

---

### REJECTED

**Feedback Capture Format**:
```yaml
review:
  decision: REJECTED
  reviewer: {name}
  date: {date}
  reasons:
    - {reason 1}
    - {reason 2}
  recommendations: |
    {guidance for rework}
```

**Next Steps**:
1. Document rejection reasons
2. Assess if workflow concept is viable
3. Consider returning to design phase
4. Re-work significantly

---

## Approval Documentation Template

### approval.md

Create in `supporting-docs/approval.md`:

```markdown
# Workflow Approval

**Workflow**: {name} v{version}
**Reviewer**: {reviewer_name}
**Date**: {approval_date}
**Decision**: APPROVED

## Review Notes
{comments from reviewer}

## Review Type Conducted
{Quick / Thorough / Deep}

## Key Observations
- {observation 1}
- {observation 2}

## Recommendations for Future Versions
- {recommendation 1}
- {recommendation 2}

---

This workflow is approved for production use.

**Approval Signature**: {reviewer_name}
**Date**: {date}
```

---

## metadata.json Approval Fields

Add to metadata.json after approval:

```json
{
  ...
  "approved": true,
  "approved_by": "{reviewer}",
  "approved_date": "{date}",
  "approval_type": "{quick/thorough/deep}",
  "status": "production"
}
```

---

## CHANGELOG.md Template

Create in workflow root:

```markdown
# Changelog

All notable changes to this workflow will be documented in this file.

## [v{version}] - {date}

### Added
- Initial release
- {count} phases with {count} total tasks
- {key feature 1}
- {key feature 2}

### Quality Metrics
- File Size Compliance: {percent}%
- Command Coverage: {percent}%
- Meta-Workflow Compliance: {percent}%

### Approved By
- **Reviewer**: {name}
- **Date**: {date}
- **Type**: {review_type}

### Known Limitations
- {limitation 1 if any}

---

## Versioning

This workflow follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible workflow structure changes
- **MINOR**: Backward-compatible additions
- **PATCH**: Backward-compatible bug fixes
```

---

## Distribution Preparation

### For Core Workflows (prAxIs OS)

1. **Notify Maintainers**
   - Create announcement
   - Document in main README
   - Update workflow index

2. **Prepare Documentation**
   - Ensure usage guide is complete
   - Add workflow to documentation site
   - Create example usage

3. **Version Control**
   - Tag release in git
   - Document in CHANGELOG
   - Update version references

### For Project-Specific Workflows

1. **Share with Team**
   - Notify team members
   - Provide usage guide link
   - Schedule walkthrough if needed

2. **Add to Project Documentation**
   - Update project README
   - Link from relevant docs
   - Add to workflow index

3. **Training**
   - Conduct training session if needed
   - Create quick reference card
   - Set up support channel

---

## Common Review Outcomes

### Outcome: Minor Wording Improvements

**Typical Changes**:
- Clarify ambiguous instructions
- Fix typos
- Improve examples

**Resolution Time**: 15-30 minutes

### Outcome: Task Reorganization

**Typical Changes**:
- Reorder tasks for better flow
- Split/merge tasks
- Adjust navigation

**Resolution Time**: 1-2 hours

### Outcome: Missing Validation

**Typical Changes**:
- Add missing validation gates
- Strengthen evidence requirements
- Add quality checks

**Resolution Time**: 2-4 hours

### Outcome: Scope Issues

**Typical Changes**:
- Clarify workflow boundaries
- Adjust success criteria
- Revise phase structure

**Resolution Time**: 4-8 hours (may require design revisit)

---

**Use these templates to conduct systematic, professional human reviews for workflow approval.**


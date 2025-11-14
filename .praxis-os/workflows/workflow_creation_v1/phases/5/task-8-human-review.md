# Task 8: Human Review

**Phase**: 5 - Testing & Delivery  
**Purpose**: Present to human for final approval  
**Depends On**: Task 7 (final validation passing)  
**Feeds Into**: Workflow completion

---

## Objective

Present the completed workflow to a human reviewer for final approval before production release.

---

## Context

📊 **CONTEXT**: This is the final gate before the workflow is considered production-ready. Human judgment is essential for assessing overall quality, coherence, and fitness for purpose that automated checks cannot evaluate.

🚨 **CRITICAL**: This task REQUIRES human approval. AI agents cannot self-approve workflows.

⚠️ **MUST-READ**: [../../core/human-review-templates.md](../../core/human-review-templates.md) for presentation templates, decision handling procedures, and approval documentation formats

---

## Instructions

### Step 1: Prepare Review Package

Compile all materials for human review:

**Core Workflow**:
- Workflow directory path
- Total phases and tasks count

**Documentation**:
- `supporting-docs/design-summary.md`
- `supporting-docs/usage-guide.md`
- `supporting-docs/compliance-report.md`
- Final validation report (from Task 7)

**Metadata**:
- `metadata.json`
- `supporting-docs/workflow-definition.yaml`

### Step 2: Generate Executive Summary

Use the executive summary template from core/human-review-templates.md.

Populate with:
- Workflow name, version, type
- Phase/task counts
- Key metrics from Task 7 (compliance percentages)
- Top 3 strengths from workflow
- Known limitations if any

### Step 3: Present to Human Reviewer

Use the presentation format template from core/human-review-templates.md.

Present with:
- Executive summary
- Review checklist
- Decision options (APPROVE / APPROVE WITH CHANGES / REQUEST REVISIONS / REJECT)

Recommend review type based on workflow criticality:
- Quick Review (~15 min) for minor workflows
- Thorough Review (~45 min) for standard workflows  
- Deep Review (~2 hours) for critical workflows

### Step 4: Capture Human Feedback

Document the reviewer's decision using appropriate format from core/human-review-templates.md:
- APPROVED
- APPROVED WITH MINOR CHANGES
- REQUEST REVISIONS
- REJECTED

Record:
- Decision type
- Reviewer name
- Review date
- Comments/feedback
- Changes requested (if applicable)
- Issues to address (if applicable)

### Step 5: Handle Approval Decision

Follow decision handling procedures from core/human-review-templates.md for:
- **APPROVED**: Create approval docs, proceed to Step 6
- **APPROVED WITH MINOR CHANGES**: Implement, re-present, then APPROVED steps
- **REQUEST REVISIONS**: Return to Task 5, revise, re-validate, re-present
- **REJECTED**: Document reasons, assess viability, escalate

### Step 6: Finalize Workflow (If Approved)

Use templates from core/human-review-templates.md to create:

1. **approval.md** in supporting-docs/
2. **Update metadata.json** with approval fields
3. **CHANGELOG.md** in workflow root

📖 **DISCOVER-TOOL**: Write approval documents

### Step 7: Prepare for Distribution

**Core workflows**: Notify maintainers, update docs, tag release  
**Project workflows**: Share with team, add to docs, train if needed

---

## Expected Output

**Evidence for Validation Gate** (all from previous tasks + this task):
- `dry_run_successful`, `usability_issues_count`, `refinements_applied`, `usage_guide_created`, `final_compliance_passed` (from Tasks 1-7)
- `human_approved`: Boolean (**MUST BE TRUE** - from this task)

**Additional Outputs**:
- `supporting-docs/approval.md`, `CHANGELOG.md` created
- `metadata.json` updated with approval fields
- `reviewer_name`, `approval_date`: String

---

## Checkpoint Evidence

Submit the following evidence to complete Phase 4:

```yaml
evidence:
  dry_run_successful: true
  usability_issues_count: {count}
  refinements_applied: true
  usage_guide_created: true
  final_compliance_passed: true
  human_approved: true
```

🚨 **CRITICAL**: `human_approved` MUST be true to pass this gate.

---

## Workflow Complete!

🎉 **Congratulations!** The workflow has been created, validated, tested, and approved.

**Next Steps**:
- Use the workflow to create other workflows
- Share with team or community
- Monitor usage and gather feedback
- Iterate and improve in future versions

---

## Navigation

**Workflow Complete** - No next task. Return to workflow engine.

↩️ **RETURN-TO**: phase.md (after task complete, for final checkpoint submission)

# Usage Guide Structure - Complete Template

**Type**: Tier 2 (Methodology - On-Demand Reading)  
**Purpose**: Comprehensive template and guidance for creating workflow usage guides  
**Referenced by**: Phase 4, Task 6

---

## Overview

This document provides the complete structure, templates, and examples for creating a comprehensive usage guide for any workflow. The usage guide is the primary user-facing documentation that helps workflow consumers understand when and how to use a workflow.

---

## Standard Usage Guide Structure

```markdown
# {Workflow Name} - Usage Guide

## Overview
- What this workflow does
- Who should use it
- When to use it

## Prerequisites
- Required inputs
- Required tools/environment
- Required knowledge

## Quick Start
- Minimal steps to begin
- Basic example

## Detailed Usage
- Step-by-step walkthrough
- Phase-by-phase guidance
- Key decision points

## Common Issues
- Troubleshooting guide
- Known limitations
- Workarounds

## Examples
- Real-world scenarios
- Sample inputs/outputs

## Advanced Topics
- Customization options
- Integration with other workflows
- Best practices

## Reference
- Related documentation
- Support resources
```

---

## Section-by-Section Guidance

### Section 1: Overview

**Purpose**: Help readers quickly determine if this workflow meets their needs

**Template**:
```markdown
## Overview

### What This Workflow Does

{Workflow} systematically {primary action} by {approach}. It produces:
- {Deliverable 1}
- {Deliverable 2}
- {Deliverable 3}

### Who Should Use This

**Ideal Users**:
- {User type 1} who need to {use case 1}
- {User type 2} working on {context 2}

**Required Skills**:
- {Skill 1} (basic/intermediate/advanced)
- {Skill 2} (basic/intermediate/advanced)

### When to Use This

**Use this workflow when**:
- ✅ {Scenario 1}
- ✅ {Scenario 2}

**Don't use this workflow when**:
- ❌ {Scenario where not appropriate}
- ❌ {Better alternative exists}
```

**Content Sources**:
- Extract from workflow definition: `problem.statement`, `problem.why_workflow`
- Infer user types from workflow complexity and domain
- Base "when to use" on success criteria

---

### Section 2: Prerequisites

**Purpose**: Ensure users have everything needed before starting

**Template**:
```markdown
## Prerequisites

### Required Inputs

Before starting, you must have:

1. **{Input 1}**
   - Format: {file format/data structure}
   - Location: {where to create/find it}
   - Validation: {how to verify it's correct}

2. **{Input 2}**
   - Format: {format}
   - Example: `{example path or content}`

### Required Tools/Environment

This workflow requires access to:

- **{Tool 1}**: {Purpose and how to verify access}
- **{Tool 2}**: {Purpose and how to verify access}

Verify tool access:
```bash
# Commands to verify tools are available
{verification commands}
```

### Required Knowledge

You should be familiar with:

- **{Concept 1}**: {Brief explanation or link to learn more}
- **{Concept 2}**: {Brief explanation or link to learn more}

**Recommended reading**:
- 🔍 Search: "{search query for related standards}"
```

**Content Sources**:
- Required inputs from workflow definition phases (Phase 0 typically validates inputs)
- Tools from workflow's command language usage (DISCOVER-TOOL commands)
- Knowledge from domain_focus fields in tasks

---

### Section 3: Quick Start

**Purpose**: Get users running immediately with minimal explanation

**Template**:
```markdown
## Quick Start

Get started in 5 minutes:

### Step 1: Prepare Your Input

{One-sentence instruction}

Example:
```yaml
# or bash or language-specific
{minimal example}
```

### Step 2: Start the Workflow

```
start_workflow("{workflow_name}", "{target}", 
               {required_options})
```

### Step 3: Follow Phase Progression

The workflow will guide you through:
- **Phase 0**: {One-line summary}
- **Phase 1**: {One-line summary}
- **Phase 2**: {One-line summary}

### Step 4: Complete Validation Gates

At each phase boundary, submit evidence when prompted.

### Step 5: {Final step specific to workflow}

{Final action like approval, deployment, etc.}
```

**Content Sources**:
- Minimal example of workflow's primary input
- Workflow name from metadata
- Phase summaries from phase.md purpose fields
- Required options from Phase 0 validation gate evidence

---

### Section 4: Detailed Usage

**Purpose**: Comprehensive walkthrough with context and guidance

**Template**:
```markdown
## Detailed Usage

### Execution Overview

This workflow operates in {X} phases over approximately {timeframe}:

{Table of phases}
| Phase | Name | Purpose | Key Tasks | Duration |
|-------|------|---------|-----------|----------|
| 0 | {name} | {purpose} | {count} tasks | ~{time} |
| 1 | {name} | {purpose} | {count} tasks | ~{time} |

### Phase-by-Phase Guide

#### Phase 0: {Name}

**Purpose**: {Purpose from phase.md}

**What You'll Do**:
1. {Task 1 summary}
2. {Task 2 summary}
3. {Task 3 summary}

**Key Decisions**:
- {Decision point 1 if any}

**Common Challenges**:
- {Challenge 1}: {Solution}

**Validation Gate**:
The phase gate requires evidence of:
- {Evidence field 1}
- {Evidence field 2}

**Tips**:
- {Helpful tip specific to this phase}

---

[Repeat for each phase]

### Progress Tracking

The workflow includes a progress tracking file at `core/progress-tracking.md`. 
Update this file to monitor:
- Phase completion status
- Task completion within phases
- Quality metrics
- Known issues

### Key Decision Points

Throughout the workflow, you'll make important decisions:

**Decision 1: {Decision Name}** (Phase {N}, Task {M})
- **Question**: {What needs to be decided}
- **Options**: {Option A, Option B}
- **Guidance**: {How to choose}

[Repeat for each major decision point]
```

**Content Sources**:
- Phase data from metadata.json
- Task summaries from task file purposes
- Decision points from conditional logic in tasks
- Common challenges inferred from validation gates and constraints

---

### Section 5: Common Issues & Troubleshooting

**Purpose**: Help users resolve problems without external support

**Template**:
```markdown
## Common Issues

### Issue: {Issue Name}

**Symptoms**:
- {Observable symptom 1}
- {Observable symptom 2}

**Causes**:
- {Common cause 1}
- {Common cause 2}

**Solution**:
1. {Step 1 to resolve}
2. {Step 2 to resolve}
3. If still failing, {escalation path}

**Prevention**:
- {How to avoid this issue}

---

[Template for 5-10 most likely issues]

### Known Limitations

This workflow has the following limitations:

- **{Limitation 1}**: {Description and workaround if any}
- **{Limitation 2}**: {Description and workaround if any}

### When to Seek Help

Escalate to human review if:
- {Escalation scenario 1}
- {Escalation scenario 2}
```

**Content Sources**:
- Common issues from 🚨 CRITICAL and ⚠️ CONSTRAINT markers in tasks
- Validation failures mentioned in tasks
- Error handling sections in complex tasks
- Known limitations from workflow design decisions

---

### Section 6: Examples

**Purpose**: Provide concrete, relatable scenarios

**Template**:
```markdown
## Examples

### Example 1: {Simple Scenario Name}

**Context**: {Brief setup}

**Input**:
```yaml
{example input file or configuration}
```

**Execution**:
```
start_workflow("{workflow_name}", "{target}", {...})
```

**Key Steps**:
1. Phase 0 validated the {input}
2. Phase 1 created {output}
3. Phase 2 generated {artifacts}

**Output**:
{Description of what was produced}

**Time**: ~{duration}

---

### Example 2: {Complex Scenario Name}

[Similar structure but more complex]

---

### Example 3: {Edge Case Scenario}

[Example showing how workflow handles unusual case]
```

**Content Sources**:
- Derive from workflow definition's problem statement
- Use workflow's own definition YAML as Example 1 if self-referential
- Create realistic scenarios based on workflow type
- Include at least one simple, one complex, and one edge case

---

### Section 7: Advanced Topics

**Purpose**: Help experienced users customize and extend

**Template**:
```markdown
## Advanced Topics

### Customization Options

#### Custom Quality Standards

The workflow's quality standards can be adjusted in the definition:

```yaml
quality_standards:
  {standard_1}: {adjustable value}
  {standard_2}: {adjustable value}
```

**When to adjust**: {Guidance on customization}

#### Custom Validators

{If applicable, how to add custom validation logic}

### Integration with Other Workflows

#### Calling This Workflow from Another Workflow

A task in another workflow can invoke this workflow:

```yaml
tasks:
  - number: X
    name: {task-name}
    invokes_workflow: "{this_workflow_name}"
    invokes_workflow_options:
      {required_option}: "{value}"
    invokes_workflow_required_evidence:
      - {evidence_field_1}
      - {evidence_field_2}
```

#### Using Output Workflows

{If this workflow produces other workflows, how to use them}

### Best Practices

#### Design Session Approach

Before starting, conduct a design session:
1. {Step 1 of best practice design process}
2. {Step 2}
3. Document decisions in {location}

#### Quality-First Approach

Prioritize quality over speed:
- {Best practice 1}
- {Best practice 2}

#### Iterative Refinement

{Guidance on iterating after first use}
```

**Content Sources**:
- Quality standards from metadata.json
- Nested workflow support from workflow definition schema
- Best practices inferred from meta-workflow principles
- Domain-specific patterns from workflow type

---

### Section 8: Reference

**Purpose**: Link to related resources

**Template**:
```markdown
## Reference

### Related Documentation

- [Workflow Definition Template](../templates/workflow-definition-template.yaml)
- [Command Language Glossary](./core/command-language-glossary.md)
- [Progress Tracking Template](./core/progress-tracking.md)

### Standards to Read

Relevant prAxIs OS standards:

- 🔍 Search: "{primary standard topic}"
- 🔍 Search: "{secondary standard topic}"
- 🔍 Search: "{domain-specific topic}"

### Example Workflows

- **{this_workflow}**: Self-reference for structure
- **{related_workflow_1}**: {Why it's related}
- **{related_workflow_2}**: {Why it's related}

### Workflow Metadata

- **Name**: {workflow_name}
- **Version**: {version}
- **Type**: {workflow_type}
- **Total Phases**: {count}
- **Total Tasks**: {count}
- **Created**: {date}

### Support

For questions or issues:
1. Review this usage guide thoroughly
2. Check troubleshooting section
3. Search prAxIs OS standards for related topics
4. Consult with workflow maintainers
```

**Content Sources**:
- Links from actual workflow structure
- Standards topics from MUST-SEARCH commands in workflow
- Related workflows from same workflow_type
- Metadata from metadata.json

---

## Usage Guide Quality Checklist

After creating usage guide, verify:

✅ **Completeness**:
- [ ] All 8 sections present
- [ ] Prerequisites clearly documented
- [ ] Quick start is truly quick (≤5 steps)
- [ ] Common issues section has 5+ issues
- [ ] At least 2 examples provided

✅ **Clarity**:
- [ ] Technical jargon explained
- [ ] Examples are concrete
- [ ] Instructions are actionable
- [ ] Success criteria clear

✅ **Accuracy**:
- [ ] Matches actual workflow structure
- [ ] Phase counts correct
- [ ] Evidence fields match gates
- [ ] Links work

✅ **Usefulness**:
- [ ] New user can start quickly
- [ ] Experienced user finds depth
- [ ] Troubleshooting helps common issues
- [ ] Examples are realistic

---

## File Size Guidance

Target usage guide length: 300-500 lines

**Too short** (<200 lines): Likely missing key information  
**Too long** (>600 lines): Consider splitting advanced topics to separate doc

---

**Use this structure to create consistent, comprehensive, helpful usage guides for all workflows.**


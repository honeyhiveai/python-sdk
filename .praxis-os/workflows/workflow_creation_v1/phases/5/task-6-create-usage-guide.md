# Task 6: Create Usage Guide

**Phase**: 5 - Testing & Delivery  
**Purpose**: Write documentation on when/how to use workflow  
**Depends On**: Task 5 (refinements applied)  
**Feeds Into**: Task 7 (Final Validation)

---

## Objective

Create a comprehensive usage guide that explains when to use this workflow, how to prepare for it, how to execute it, and how to troubleshoot common issues.

---

## Context

📊 **CONTEXT**: The usage guide is the user-facing documentation that helps workflow consumers understand if this workflow is right for their needs and how to use it successfully.

⚠️ **MUST-READ**: [../../core/usage-guide-structure.md](../../core/usage-guide-structure.md) for complete structure template and section-by-section guidance

---

## Instructions

### Step 1: Review Structure Template

Read the usage guide structure document (in core/) which provides:
- Complete 8-section template
- Section-by-section guidance with examples
- Content source recommendations
- Quality checklist

### Step 2: Gather Source Content

From Phase 0 preparation and workflow definition, gather:

**From Definition**:
- `problem.statement` → Overview section
- `problem.why_workflow` → When to use section
- `problem.success_criteria` → Success examples
- Phase data → Detailed usage section

**From Workflow Structure**:
- metadata.json → Phase/task counts
- Phase.md files → Phase purposes and deliverables
- Validation gates → Evidence requirements

**From Created Files**:
- core/command-language-glossary.md → Reference section
- supporting-docs/design-summary.md → Advanced topics

### Step 3: Populate Each Section Using Template

Follow the 8-section structure from core/usage-guide-structure.md:

1. **Overview** (extract from problem statement)
2. **Prerequisites** (from Phase 0 validation requirements)
3. **Quick Start** (5-step minimal path)
4. **Detailed Usage** (phase-by-phase walkthrough)
5. **Common Issues** (5-10 troubleshooting scenarios)
6. **Examples** (2-3 concrete scenarios)
7. **Advanced Topics** (customization and integration)
8. **Reference** (links and search queries)

📖 **DISCOVER-TOOL**: Read files to extract content

⚠️ **CONSTRAINT**: Target 300-500 lines total for usage guide

### Step 4: Create Troubleshooting Section

Based on validation gates and 🚨 CRITICAL markers in tasks, document:
- 5-10 most likely issues
- Symptoms, causes, solutions for each
- Prevention strategies
- When to escalate

Reference common failure patterns from Phase 3 compliance issues.

### Step 5: Add Concrete Examples

Create 2-3 examples:
- **Simple scenario**: Basic workflow execution
- **Complex scenario**: Dynamic workflow or edge case
- **Integration scenario**: Calling from another workflow (if applicable)

Use actual workflow definition YAML as example input.

### Step 6: Write Usage Guide File

Write the populated guide to:

```
{workflow_directory_path}/supporting-docs/usage-guide.md
```

📖 **DISCOVER-TOOL**: Write content to a file

### Step 7: Verify Against Quality Checklist

Use the quality checklist from core/usage-guide-structure.md:

✅ All 8 sections present  
✅ Prerequisites clearly documented  
✅ Quick start ≤5 steps  
✅ 5+ common issues documented  
✅ 2+ examples provided  
✅ Instructions actionable  
✅ Examples concrete  
✅ Links work

---

## Expected Output

**Variables to Capture**:
- `usage_guide_created`: Boolean (true if successful)
- `usage_guide_path`: String (file path)
- `usage_guide_sections`: Integer (number of sections)

---

## Quality Checks

✅ Structure defined  
✅ Overview section written  
✅ Prerequisites documented  
✅ Quick start guide created  
✅ Detailed usage written  
✅ Troubleshooting guide added  
✅ Examples provided  
✅ Advanced topics documented  
✅ Reference section added  
✅ Usage guide file written and verified

---

## Navigation

🎯 **NEXT-MANDATORY**: task-7-final-validation.md

↩️ **RETURN-TO**: phase.md (after task complete)


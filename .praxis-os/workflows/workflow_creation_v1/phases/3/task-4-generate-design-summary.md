# Task 4: Generate Design Summary

**Phase**: 3 - Core Files & Documentation  
**Purpose**: Create human-readable supporting-docs/design-summary.md  
**Depends On**: Tasks 1-3 (all core files created), Phase 0 (definition data)  
**Feeds Into**: Phase 3 (Target Phase Creation)

---

## Objective

Generate a comprehensive, human-readable design summary document that explains the workflow's purpose, architecture, design decisions, and usage patterns.

---

## Context

📊 **CONTEXT**: The design summary translates the technical YAML definition into a narrative format that helps human maintainers understand the workflow's rationale, structure, and intended usage without needing to parse YAML or read every task file.

⚠️ **CONSTRAINT**: Design summary should be comprehensive (300-600 lines) as it's a Tier 3 (Output) document, not a Tier 1 task file.

---

## Instructions

### Step 1: Extract Information from Definition

From Phase 0 workflow definition, extract:
- Problem context (statement, why workflow, success criteria)
- Architecture (phase structure, static vs dynamic)
- Configuration (dynamic config if applicable, quality standards)
- Metadata (version, type, target languages)

### Step 2: Use Standard Structure

Create document with these sections (similar to usage guide but design-focused):
1. **Header** (Version, date, type, purpose)
2. **Problem Statement** (Why this workflow exists)
3. **Why a Workflow?** (Justification vs tool/standard)
4. **Success Criteria** (Measurable outcomes)
5. **Architecture** (Static/dynamic phases explained)
6. **Input/Output** (What it consumes/produces)
7. **Key Design Decisions** (Important choices made)
8. **Quality Standards** (Metrics table)
9. **Usage Pattern** (Execution example)
10. **Meta-Workflow Compliance** (How it embodies 5 principles)
11. **Future Enhancements** (Potential improvements)

### Step 3: Populate Each Section

For each section, write clear prose extracting from definition:
- **Problem sections**: Use definition's `problem` object
- **Architecture**: Detail phase structure, counts, dynamic logic if applicable
- **Design Decisions**: Extract from definition or infer logically (don't invent)
- **Quality Standards**: From definition's `quality_standards` or defaults
- **Usage Pattern**: Step-by-step execution example
- **Meta-Workflow Compliance**: How workflow embodies each of 5 principles

### Step 7: Write Design Summary File

Write the complete summary to:

```
{workflow_directory_path}/supporting-docs/design-summary.md
```

📖 **DISCOVER-TOOL**: Write content to a file

### Step 8: Verify File Created

Confirm the file was created and is readable.

📖 **DISCOVER-TOOL**: Read file to verify contents

Check:
- File exists at correct path
- All sections present
- Clear and comprehensive
- Proper markdown formatting

---

## Expected Output

**Evidence for Validation Gate**:
- `design_summary_created`: Boolean (true if successful)

**Additional Variables**:
- `design_summary_path`: String (path to file)
- `summary_word_count`: Integer (approximate length)

---

## Quality Checks

✅ Key information extracted from definition  
✅ Document structure created  
✅ All sections populated  
✅ Design decisions documented  
✅ Usage example provided  
✅ Meta-workflow compliance explained  
✅ File written successfully  
✅ File verified readable and complete

---

## Checkpoint Evidence

Submit the following evidence to complete Phase 2:

```yaml
evidence:
  command_glossary_created: true
  progress_tracking_created: true
  definition_archived: true
  design_summary_created: true
```

---

## Navigation

🎯 **NEXT-MANDATORY**: ../dynamic/phase-template.md (if dynamic workflow) OR ../4/phase.md (if static, to begin target phase creation)

↩️ **RETURN-TO**: phase.md (after task complete, before phase submission)


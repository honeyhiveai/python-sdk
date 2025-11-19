# Task 4: Generate YAML Definition

**Phase**: 0 - Input Conversion & Preprocessing  
**Purpose**: Build YAML definition file from extracted data  
**Depends On**: Task 3 (extracted_data)  
**Feeds Into**: Task 5 (Validate Generated Definition)

---

## Objective

If input was a design document, generate a properly formatted YAML definition file following the workflow-definition-template.yaml structure using the extracted data from Task 3.

---

## Context

📊 **CONTEXT**: The YAML definition follows a strict structure defined in universal/templates/workflow-definition-template.yaml. This task transforms extracted markdown data into that YAML format.

⚠️ **CONDITIONAL EXECUTION**: This task only executes if `input_type == "design_document"`. If input_type is "yaml_definition", skip to Task 5.

🔍 **MUST-SEARCH**: "workflow definition template structure required fields"

---

## Instructions

### Step 1: Check Input Type

```python
if input_type == "yaml_definition":
    # Skip YAML generation
    # standard_definition_path = input_path (from Task 1)
    # Proceed to Task 5
    return
```

### Step 2: Load Template Structure

Reference the workflow definition template structure:

📖 **DISCOVER-TOOL**: Read template file for structure

Template location: `universal/templates/workflow-definition-template.yaml`

Understand required sections:
- Basic Identification (name, version, workflow_type)
- Problem Definition (statement, why_workflow, success_criteria)
- Phase Definitions (phases array)
- Optional sections (dynamic, target_language, tags, quality_standards)

### Step 3: Build YAML Content

Using extracted_data from Task 3, construct YAML content:

```yaml
---
# Generated from design document
# Date: {current_date}
# Source: {design_document_path}

name: "{extracted_data.name}"
version: "{extracted_data.version}"
workflow_type: "{extracted_data.workflow_type}"

problem:
  statement: |
    {extracted_data.problem.statement}
  
  why_workflow: "{extracted_data.problem.why_workflow}"
  
  success_criteria:
    {for criterion in extracted_data.problem.success_criteria}
    - "{criterion}"
    {end}

phases:
  {for phase in extracted_data.phases}
  - number: {phase.number}
    name: "{phase.name}"
    purpose: "{phase.purpose}"
    deliverable: "{phase.deliverable}"
    
    tasks:
      {for task in phase.tasks}
      - number: {task.number}
        name: "{task.name}"
        purpose: "{task.purpose}"
        {if task.domain_focus}
        domain_focus: "{task.domain_focus}"
        {end}
        {if task.commands_needed}
        commands_needed:
          {for cmd in task.commands_needed}
          - "{cmd}"
          {end}
        {end}
      {end}
    
    validation_gate:
      evidence_required:
        {for field_name, field_def in phase.validation_gate.evidence_required}
        {field_name}:
          type: "{field_def.type}"
          description: "{field_def.description}"
          validator: "{field_def.validator}"
        {end}
      human_approval_required: {phase.validation_gate.human_approval_required}
  {end}

dynamic: {extracted_data.dynamic}
target_language: "{extracted_data.target_language}"
created: "{extracted_data.created}"
tags: {extracted_data.tags}
```

### Step 4: Write YAML to File

📖 **DISCOVER-TOOL**: Write file contents

Write generated YAML to temporary location:

```
Path: .praxis-os/specs/generated-{workflow_name}-definition.yaml
```

⚠️ **CONSTRAINT**: Ensure proper YAML formatting:
- Correct indentation (2 spaces)
- Proper quoting of strings with special characters
- Valid YAML syntax

### Step 5: Record Generated Path

Store the path to generated YAML file for Phase 1:
- `standard_definition_path`: Path to generated YAML file
- `yaml_generated`: True

---

## Expected Output

**Variables to Capture**:
- `standard_definition_path`: String (path to YAML file)
- `yaml_generated`: Boolean (True if generated)
- `yaml_content`: String (full YAML content, for logging)

**If YAML Input (Skipped)**:
- `standard_definition_path`: String (original input_path)
- `yaml_generated`: Boolean (False)

---

## Quality Checks

✅ YAML file generated  
✅ File written successfully  
✅ Path recorded for Phase 1  
✅ Content follows template structure

---

## Navigation

🎯 **NEXT-MANDATORY**: task-5-validate-generated-definition.md

↩️ **RETURN-TO**: phase.md (after task complete)


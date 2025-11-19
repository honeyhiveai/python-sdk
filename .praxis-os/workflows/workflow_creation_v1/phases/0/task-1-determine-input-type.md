# Task 1: Determine Input Type

**Phase**: 0 - Input Conversion & Preprocessing  
**Purpose**: Identify input format and validate input options provided  
**Depends On**: None  
**Feeds Into**: Task 2 (Read Input Document)

---

## Objective

Check workflow options to determine if user provided a design document path or YAML definition path, and validate that at least one input is provided.

---

## Context

📊 **CONTEXT**: workflow_creation_v1 supports two input modes: design documents (primary, 90% usage) and YAML definitions (expert mode, 10% usage). This task determines which path to take.

⚠️ **CONSTRAINT**: User MUST provide either `design_document_path` OR `definition_path` in workflow options. If neither provided, this is a fatal error.

---

## Instructions

### Step 1: Check for Design Document Path

Check if workflow options contain `design_document_path`:

```python
if "design_document_path" in options:
    input_type = "design_document"
    input_path = options["design_document_path"]
```

This is the **primary path** - most users will provide a design document from spec creation.

### Step 2: Check for YAML Definition Path

If design document not provided, check for `definition_path`:

```python
elif "definition_path" in options:
    input_type = "yaml_definition"
    input_path = options["definition_path"]
```

This is the **expert path** - for programmatic use or pre-built YAML files.

### Step 3: Error if Neither Provided

🚨 **CRITICAL**: If neither path provided, STOP execution with clear error:

```
Error: No input provided to workflow_creation_v1

workflow_creation_v1 requires EITHER:
  • design_document_path: Path to design document (markdown)
  • definition_path: Path to workflow definition (YAML)

Example (Design Document):
  start_workflow("workflow_creation_v1", "my-workflow-v1", {
      "design_document_path": ".praxis-os/specs/design-spec.md"
  })

Example (YAML Definition):
  start_workflow("workflow_creation_v1", "my-workflow-v1", {
      "definition_path": "my-workflow-definition.yaml"
  })
```

Do not proceed. Workflow cannot continue without input.

### Step 4: Record Input Type

Store the determined input type and path for use in subsequent tasks:
- `input_type`: "design_document" or "yaml_definition"
- `input_path`: Path to the input file

---

## Expected Output

**Variables to Capture**:
- `input_type`: String ("design_document" or "yaml_definition")
- `input_path`: String (path to input file)

---

## Quality Checks

✅ Input type determined  
✅ Input path captured  
✅ Error handling for missing input

---

## Navigation

🎯 **NEXT-MANDATORY**: task-2-read-input-document.md

↩️ **RETURN-TO**: phase.md (after task complete)


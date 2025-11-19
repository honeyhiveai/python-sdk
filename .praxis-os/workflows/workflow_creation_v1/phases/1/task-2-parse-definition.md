# Task 2: Parse Definition

**Phase**: 1 - Definition Import & Validation  
**Purpose**: Read YAML and parse structure  
**Depends On**: Task 1 (definition_path)  
**Feeds Into**: Task 3 (Validate Structure)

---

## Objective

Read the workflow definition YAML file and parse it into a structured object for validation and processing.

---

## Instructions

### Step 1: Read Definition File

Use the `definition_path` from Task 1 to read the complete file contents.

📖 **DISCOVER-TOOL**: Read contents of a file

### Step 2: Parse YAML Structure

Parse the file contents as YAML. The expected top-level structure:

```yaml
name: string
version: string
workflow_type: string
problem: object
phases: array
dynamic: boolean (optional)
dynamic_config: object (optional)
target_language: string (optional)
created: string (optional)
tags: array (optional)
quality_standards: object (optional)
```

⚠️ **CONSTRAINT**: The file MUST be valid YAML. If parsing fails, this is a fatal error.

### Step 3: Store Parsed Definition

Store the parsed definition object in memory for use in validation and creation tasks.

---

## Context

📊 **CONTEXT**: The workflow definition uses the structure defined in `universal/templates/workflow-definition-template.yaml`. All definitions should follow this schema.

🔍 **MUST-SEARCH**: "workflow definition template structure required fields"

---

## Expected Output

**Variables to Capture**:
- `definition_raw`: String (raw YAML content)
- `definition_parsed`: Object (parsed YAML structure)
- `parse_successful`: Boolean

**If Parse Fails**:
- 🚨 **CRITICAL**: STOP execution
- Report parse error with line number if available
- Suggest checking YAML syntax

---

## Quality Checks

✅ File read successfully  
✅ YAML parsed without errors  
✅ Top-level keys identified  
✅ Definition object stored

---

## Navigation

🎯 **NEXT-MANDATORY**: task-3-validate-structure.md

↩️ **RETURN-TO**: phase.md (after task complete)


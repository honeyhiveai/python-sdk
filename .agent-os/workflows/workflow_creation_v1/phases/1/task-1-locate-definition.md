# Task 1: Locate Definition

**Phase**: 1 - Definition Import & Validation  
**Purpose**: Find the workflow definition file via options.definition_path  
**Depends On**: None  
**Feeds Into**: Task 2 (Parse Definition)

---

## Objective

Retrieve the path to the workflow definition YAML file from the workflow session options and verify the file exists.

---

## Context

📊 **CONTEXT**: This workflow was started with `start_workflow()` which accepts an `options` parameter. The `definition_path` key should contain the absolute or relative path to the workflow definition YAML file.

---

## Instructions

### Step 1: Retrieve Definition Path

The workflow session was initialized with options. Check the `options` dictionary for the `definition_path` key:

```python
# The path was passed during workflow start:
# start_workflow("workflow_creation_v1", "target-workflow", 
#                {definition_path: "path/to/workflow-def.yaml"})
```

⚠️ **CONSTRAINT**: The `definition_path` must be provided in the workflow options. If not present, this is a fatal error.

### Step 2: Verify File Exists

Use the appropriate tool to verify the file exists at the specified path.

📖 **DISCOVER-TOOL**: Check if a file exists at a given path

If the file does not exist:
- 🚨 **CRITICAL**: STOP execution
- Report the error with the expected path
- Suggest checking the path and trying again

### Step 3: Document Path

Record the validated definition path for use in subsequent tasks.

---

## Expected Output

**Variables to Capture**:
- `definition_path`: String (absolute or relative path)
- `definition_exists`: Boolean (True if file exists)

---

## Quality Checks

✅ File path retrieved from workflow options  
✅ File existence confirmed  
✅ Path stored for next task

---

## Navigation

🎯 **NEXT-MANDATORY**: task-2-parse-definition.md

↩️ **RETURN-TO**: phase.md (after task complete)


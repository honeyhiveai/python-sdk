# Task 3: Validate Structure

**Phase**: 1 - Definition Import & Validation  
**Purpose**: Check all required sections present  
**Depends On**: Task 2 (definition_parsed)  
**Feeds Into**: Task 4 (Validate Completeness)

---

## Objective

Verify the parsed definition contains all required top-level sections and follows the workflow definition schema.

---

## Instructions

### Step 1: Check Required Fields

Verify the following REQUIRED fields are present:

**Basic Identification**:
- `name` (string, snake_case-v1 format)
- `version` (string, semantic version)
- `workflow_type` (string, category)

**Problem Definition**:
- `problem` (object)
  - `statement` (string)
  - `why_workflow` (string)
  - `success_criteria` (array)

**Phase Definitions**:
- `phases` (array, must contain at least 1 phase)

⚠️ **CONSTRAINT**: If ANY required field is missing, validation MUST fail.

### Step 2: Check Field Types

Verify each field has the correct type:
- Strings are strings
- Arrays are arrays
- Objects are objects
- Booleans are booleans
- Integers are integers

### Step 3: Validate Name Format

Check `name` follows the pattern: `[a-z0-9-]+_v[0-9]+`

Examples:
- ✅ `workflow-creation-v1`
- ✅ `test-generation-v2`
- ❌ `WorkflowCreation`
- ❌ `workflow_creation` (no version)

### Step 4: Check Optional Sections

Document which optional sections are present:
- `dynamic` / `dynamic_config`
- `target_language`
- `created`
- `tags`
- `quality_standards`

---

## Context

🔍 **MUST-SEARCH**: "workflow definition required fields validation"

---

## Expected Output

**Variables to Capture**:
- `structure_valid`: Boolean
- `missing_fields`: Array (list any missing required fields)
- `type_errors`: Array (list any type mismatches)
- `has_dynamic_config`: Boolean

**If Validation Fails**:
- 🚨 **CRITICAL**: STOP execution
- Report all missing fields
- Report all type errors
- Provide corrective guidance

---

## Quality Checks

✅ All required fields present  
✅ All field types correct  
✅ Name format valid  
✅ Optional sections documented

---

## Navigation

🎯 **NEXT-MANDATORY**: task-4-validate-completeness.md

↩️ **RETURN-TO**: phase.md (after task complete)


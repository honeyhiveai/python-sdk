# Task 3: Extract from Design Document

**Phase**: 0 - Input Conversion & Preprocessing  
**Purpose**: Parse design document and extract structured information  
**Depends On**: Task 2 (input_document_content, input_type)  
**Feeds Into**: Task 4 (Generate YAML Definition)

---

## Objective

If input type is "design_document", parse the markdown content and extract problem statement, phases, tasks, and validation gates into structured data for YAML generation.

---

## Context

📊 **CONTEXT**: Design documents from spec_creation_v1 follow a predictable structure with sections for problem statement, success criteria, phase breakdown, and validation framework.

⚠️ **CONDITIONAL EXECUTION**: This task only executes if `input_type == "design_document"`. If input_type is "yaml_definition", skip directly to Task 5 (validation).

🔍 **MUST-SEARCH**: "workflow definition structure phases tasks validation gates"

---

## Instructions

### Step 1: Check Input Type

```python
if input_type == "yaml_definition":
    # Skip this task and Task 4
    # Set design_document_converted = False
    # Proceed to Task 5 for validation
    return
```

### Step 2: Extract Problem Statement

📊 **CONTEXT**: Problem statement typically in section titled "Problem Statement", "Current State", or "Overview".

Extract:
- **problem.statement**: Multi-paragraph description of what workflow solves
- **problem.why_workflow**: Why this needs to be a workflow (vs tool/standard)

Look for sections:
- "Problem Statement"
- "Current State" / "Desired State"
- "Why a Workflow?"

### Step 3: Extract Success Criteria

Look for section titled "Success Criteria", "Success Metrics", or numbered list of outcomes.

Extract as array:
```python
success_criteria = [
    "Criterion 1 extracted from doc",
    "Criterion 2 extracted from doc",
    ...
]
```

Target: 3-7 criteria typically.

### Step 4: Extract Workflow Metadata

From document headers and content, infer:
- **name**: Extract from title (convert to snake_case-v1 format)
- **version**: Default "1.0.0" unless specified
- **workflow_type**: Infer from content keywords:
  - "test" / "testing" → "testing"
  - "document" / "documentation" → "documentation"  
  - "implement" / "build" → "implementation"
  - "validate" / "check" → "validation"
  - Default → "implementation"

### Step 5: Extract Phases

📊 **CONTEXT**: Phases typically in section "Phase Breakdown", "Architecture", or "Phases".

For each phase section (look for "## Phase 0:", "### Phase 1:", etc.):

Extract:
```python
phase = {
    "number": extract_number(section_title),
    "name": extract_name(section_title),
    "purpose": extract_field("Goal:" or "Purpose:"),
    "deliverable": extract_field("Deliverable:" or "Output:"),
    "tasks": [],  # Extracted in Step 6
    "validation_gate": {}  # Extracted in Step 7
}
```

### Step 6: Extract Tasks per Phase

Within each phase section, look for "Tasks:" subsection or numbered lists.

For each task:
```python
task = {
    "number": task_number,
    "name": convert_to_kebab_case(task_title),
    "purpose": task_description,
    "domain_focus": extract_if_mentioned(),  # Optional
    "commands_needed": [],  # Infer from description
    "estimated_lines": 100  # Default
}
```

**Kebab Case Conversion**:
- "Validate Structure" → "validate-structure"
- "Create Workflow Directory" → "create-workflow-directory"

**Infer Commands Needed**:
- Mentions "read", "parse" → ["read_file"]
- Mentions "write", "create" → ["write"]
- Mentions "search", "find" → ["grep", "glob_file_search"]
- Mentions "RAG", "query" → ["search_standards"]
- Mentions "run", "execute" → ["run_terminal_cmd"]

### Step 7: Extract Validation Gates

Look for "Validation Gate", "Checkpoint Validation", "Evidence Required" sections.

Extract evidence fields:
```python
validation_gate = {
    "evidence_required": {
        field_name: {
            "type": field_type,  # string, boolean, integer
            "description": field_description,
            "validator": infer_validator(field_type, field_name)
        }
    },
    "human_approval_required": check_if_mentioned()
}
```

**Validator Inference**:
- boolean type → "is_true"
- integer type + "count" → "greater_than_0"
- integer type + "percent" → "percent_gte_80" (or 95/100)
- string type + "path" → "file_exists" or "directory_exists"
- string type → "non_empty"

### Step 8: Store Extracted Data

Store all extracted information in structured format:
```python
extracted_data = {
    "name": workflow_name,
    "version": "1.0.0",
    "workflow_type": workflow_type,
    "problem": {
        "statement": problem_statement,
        "why_workflow": why_workflow,
        "success_criteria": success_criteria_array
    },
    "phases": phases_array,
    "dynamic": False,  # Default, can be updated if detected
    "target_language": "any",  # Default
    "created": today_date,
    "tags": [],  # Can be inferred from content
    "quality_standards": {}  # Use defaults
}
```

---

## Expected Output

**Variables to Capture**:
- `extracted_data`: Object (structured workflow definition)
- `extraction_successful`: Boolean (True if completed)
- `phases_extracted`: Integer (count of phases)
- `tasks_extracted`: Integer (total tasks across all phases)

**If YAML Input (Skipped)**:
- `design_document_converted`: Boolean (False)

---

## Quality Checks

✅ All required sections extracted (problem, phases, tasks)  
✅ Phase structure validated (each phase has tasks)  
✅ Validation gates extracted for each phase  
✅ Structured data ready for YAML generation

---

## Navigation

🎯 **NEXT-MANDATORY**: task-4-generate-yaml-definition.md

↩️ **RETURN-TO**: phase.md (after task complete)


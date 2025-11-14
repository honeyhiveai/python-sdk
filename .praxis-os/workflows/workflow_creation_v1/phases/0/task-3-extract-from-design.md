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

### Step 6B: Extract Detailed Task Information

🚨 **CRITICAL**: This step extracts the rich detail needed for quality task file generation. Without this, Phase 4 will generate generic stubs.

For each task identified in Step 6, perform deep extraction to populate optional fields that enable rich task generation.

#### A. Extract Step-by-Step Outline

Within the task description or following subsections, look for:
- Numbered steps: "1. X, 2. Y, 3. Z"
- Bulleted sub-items under the task
- Sequential phrases: "First... then... finally..."
- Instructional sequences with action verbs
- Parenthetical details: "(include X, ensure Y, validate Z)"

**Parsing Strategy**:
1. If task has nested numbered/bulleted items, extract each as a step
2. If task description contains sequential phrases, split into logical steps
3. If task description includes parenthetical details, extract as separate steps
4. If no explicit steps found, analyze task purpose and infer 3-5 logical steps

Extract as: `steps_outline: ["Step 1 description", "Step 2 description", ...]`

**Example**:
- Task description: "Write Quick Reference section (front-load critical info, 200-400 tokens, high keyword density)"
- Extracted steps_outline:
  - "Front-load critical info in first 2 sentences"
  - "Use high keyword density (3-5 mentions of core topic)"
  - "Write 200-400 tokens total"
  - "Optimize for RAG discoverability"

#### B. Identify Required Examples

Scan task description and phase context for mentions of:
- "with examples"
- "concrete scenarios"
- "working code"
- ">= N examples"
- Specific example types: "success case", "failure case", "edge case"
- "demonstrate", "show", "illustrate"

**Parsing Strategy**:
1. Extract explicit example requirements from task description
2. If phase mentions examples generally, apply to relevant tasks
3. For implementation/coding tasks, default to ["Success example", "Failure/edge case example"]
4. For validation tasks, include ["Valid input example", "Invalid input example"]
5. For writing tasks, include ["Good example", "Bad example comparison"]

Extract as: `examples_needed: ["Example type 1", "Example type 2", ...]`

**Example**:
- Task description: "Add concrete examples (working code/scenarios)"
- Extracted examples_needed:
  - "Working code example showing correct implementation"
  - "Scenario demonstrating common use case"
  - "Edge case example with error handling"

#### C. Extract Task-Level Validation Criteria

From the phase's "Checkpoint Validation" or "Evidence Required" section:
- Identify which validation fields apply to THIS specific task
- Look for task-specific success criteria
- Convert phase-level checks into task-level quality checks
- Look for measurable outcomes in task description

**Parsing Strategy**:
1. Map phase validation fields to contributing tasks
2. For each task, identify what evidence it produces
3. Create measurable criteria for task completion
4. Extract quantitative requirements (percentages, counts, sizes)
5. Extract qualitative requirements (presence of elements, format compliance)

Extract as: `validation_criteria: ["Criterion 1", "Criterion 2", ...]`

**Example**:
- Phase validation requires: `token_count: integer (200-400)`
- Task: "Write Quick Reference section"
- Extracted validation_criteria:
  - "Token count between 200-400"
  - "Core keyword appears 3-5 times"
  - "Front-loaded critical information in first 2 sentences"
  - "Natural language phrasing for RAG"

#### D. Extract Task Context

Capture rich contextual information from:
- Phase purpose statement (why this phase matters)
- Task description elaborations (details beyond the title)
- Domain-specific terminology mentioned
- Dependency information (what this task builds on)
- Constraint mentions (what must be avoided)
- "Why" statements explaining rationale

**Parsing Strategy**:
1. Combine phase purpose + task description context
2. Extract any "why" explanations or rationale
3. Include domain considerations mentioned
4. Note constraints or anti-patterns
5. Explain how this task contributes to overall workflow goal

Extract as: `task_context: "Rich paragraph explaining why this task matters, constraints, and domain considerations"`

**Example**:
- Extracted task_context: "Quick Reference is the most important section for RAG discovery. Must be optimized for semantic search with natural language phrasing that matches common agent queries. High keyword density (3-5 mentions) ensures retrieval but must remain readable. The 200-400 token limit forces conciseness while the front-loading requirement (critical info in first 2 sentences) maximizes value even when truncated by chunking."

#### E. Update Task Object with Extracted Information

Append all extracted information to task object:
```python
task = {
    "number": task_number,
    "name": convert_to_kebab_case(task_title),
    "purpose": task_description,
    "domain_focus": extract_if_mentioned(),
    "commands_needed": infer_commands(task_description),
    "estimated_lines": 100,
    # NEW FIELDS FROM DEEP EXTRACTION:
    "steps_outline": extracted_steps,  # Array of step descriptions
    "examples_needed": extracted_examples,  # Array of example types
    "validation_criteria": extracted_criteria,  # Array of quality checks
    "task_context": extracted_context  # Rich paragraph
}
```

⚠️ **FALLBACK**: If deep extraction finds nothing:
- `steps_outline`: Default to empty array `[]` (Phase 4 will use intelligent fallback)
- `examples_needed`: Default to `["Success case example", "Failure/edge case example"]`
- `validation_criteria`: Default to `["Task output is complete", "Task output meets requirements"]`
- `task_context`: Default to phase purpose or generic `"Complete this task systematically"`

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


# Task 3: Generate Task Files

**Phase**: 4 - Phase Content Generation  
**Purpose**: Generate all task-N-name.md files for target workflow  
**Depends On**: Task 2 (phase files created)  
**Feeds Into**: Task 4 (Verify Generation)

---

## Objective

Loop through all tasks across all phases and generate individual task markdown files using the task template.

---

## Context

📊 **CONTEXT**: Each task needs its own task-N-name.md file with instructions, examples, validation criteria, and navigation. We use the task template from `phases/dynamic/task-template.md` and substitute variables for each task.

🔍 **MUST-SEARCH**: "task file structure requirements command language"

---

## Instructions

### Step 1: Load Task Template

Read the task template file:

```
{workflow_root_path}/phases/dynamic/task-template.md
```

📖 **DISCOVER-TOOL**: Read template file

This template contains placeholders like:
- `{{phase_number}}`
- `{{task_number}}`
- `{{task_name}}`
- `{{task_purpose}}`
- `{{task_domain_focus}}` (optional)
- `{{commands_needed}}` (list)
- `{{task_steps}}` (generated from steps_outline)
- `{{examples}}` (generated or default)
- `{{validation_criteria}}` (checklist)

### Step 2: Nested Loop Through All Tasks

```python
task_files_created = 0

for phase in definition['phases']:
    phase_number = phase['number']
    
    for task in phase['tasks']:
        task_number = task['number']
        task_name = task['name']
        task_purpose = task['purpose']
        
        # Optional fields
        domain_focus = task.get('domain_focus', '')
        commands_needed = task.get('commands_needed', [])
        steps_outline = task.get('steps_outline', [])
        examples_needed = task.get('examples_needed', [])
        validation_criteria = task.get('validation_criteria', [])
        
        # Generate task content (see Step 3)
```

### Step 3: Generate Task Content

For each task, build the complete task file content:

**A. Build Commands Section (if commands_needed present):**

```markdown
**Commands/Tools Needed:**
- 📖 **DISCOVER-TOOL**: {command description}
- 🔍 **MUST-SEARCH**: {search query}
...
```

**B. Build Steps Section:**

If `steps_outline` provided, expand into detailed steps:

```markdown
### Step 1: {step outline 1}

{Elaborate on step with context from task_context if available}

📖 **DISCOVER-TOOL**: {Infer tool needed for this step from commands_needed}

### Step 2: {step outline 2}

{Elaborate on step}

🔍 **MUST-SEARCH**: {Infer domain query if domain_focus present}

### Step 3: {step outline 3}

...
```

**If NOT provided (FALLBACK LOGIC - CRITICAL):**

⚠️ **DO NOT** use generic placeholders like "Execute the required actions for this task"

Instead, apply **intelligent inference** based on task characteristics:

1. **Analyze task_purpose for action verbs and infer logical steps:**
   - "write" / "create" → Generate steps: "Draft content", "Review against criteria", "Finalize and format"
   - "validate" / "verify" → Generate steps: "Load input", "Run validation checks", "Document results"
   - "generate" / "build" → Generate steps: "Gather inputs", "Apply templates/logic", "Generate output", "Verify correctness"
   - "parse" / "extract" → Generate steps: "Read input file", "Parse structure", "Extract data", "Validate extracted data"
   - "analyze" / "review" → Generate steps: "Load files to analyze", "Apply criteria", "Document findings"

2. **Consider commands_needed to add tool-specific steps:**
   - If includes `"read_file"` → Add step: "Load and read input file(s)"
   - If includes `"write"` → Add step: "Write output to target file"
   - If includes `"grep"` or `"glob_file_search"` → Add step: "Search for relevant files/patterns"
   - If includes `"search_standards"` → Add step: "Query standards for domain guidance"
   - If includes `"run_terminal_cmd"` → Add step: "Execute required command"

3. **Add domain expertise retrieval if domain_focus present:**
   - Always include: 🔍 **MUST-SEARCH**: "{domain_focus} best practices" or "{domain_focus} implementation patterns"

4. **Generate minimum 3-5 reasonable steps with command language markers:**

**Example Fallback Generation:**

Task: "validate-structure", purpose: "Validate YAML follows template structure"

Generated steps (when steps_outline is empty):
```markdown
### Step 1: Load YAML Definition

Read the generated YAML file from the previous phase.

📖 **DISCOVER-TOOL**: Read file contents

### Step 2: Load Template Schema

Read the template structure to understand required fields.

🔍 **MUST-SEARCH**: "YAML schema validation best practices"

### Step 3: Validate Required Fields

Check that all required fields are present and correctly typed.

⚠️ **CONSTRAINT**: All required fields must be non-empty

### Step 4: Validate Field Structure

Ensure phases array, tasks array, and validation_gate structure are correct.

### Step 5: Document Validation Results

Record validation status and any errors found.
```

**C. Build Examples Section:**

If `examples_needed` provided, generate concrete examples:

```markdown
## Examples

### Example 1: {examples_needed[0]}

{Generate example based on type and task_purpose}

{For code examples, include working code snippet}
{For scenarios, include realistic situation}
{For comparisons, show good vs bad side-by-side}

### Example 2: {examples_needed[1]}

...
```

**If NOT provided (FALLBACK LOGIC - CRITICAL):**

⚠️ **DO NOT** leave empty or use "Add example here" placeholders

Instead, generate **2 default examples** based on task type:

1. **Success case example** - Show what correct execution looks like
2. **Failure/edge case example** - Show what to avoid or handle

**Use task_purpose and commands_needed to infer example content:**

- **For validation tasks**: Valid input example + Invalid input example
- **For writing tasks**: Good output example + Bad output example comparison
- **For implementation tasks**: Working code + Common mistake
- **For parsing tasks**: Clean input + Malformed input handling

**Example Fallback Generation:**

Task: "parse-definition", purpose: "Read and parse YAML definition"

Generated examples (when examples_needed is empty):
```markdown
## Examples

### Example 1: Valid YAML Structure

```yaml
name: "example_workflow_v1"
version: "1.0.0"
phases:
  - number: 0
    name: "Setup"
    tasks:
      - number: 1
        name: "initialize"
```

This structure parses correctly with all required fields present.

### Example 2: Invalid YAML - Missing Required Fields

```yaml
name: "broken_workflow"
# Missing version field - will fail validation
phases:
  - name: "Setup"
    # Missing phase number - will fail validation
```

This example shows common parsing errors to handle gracefully.
```

**D. Build Validation Criteria:**

```markdown
## Quality Checks

✅ {criterion 1}  
✅ {criterion 2}  
...
```

**E. Add Domain Expertise (if domain_focus present):**

```markdown
## Context

🔍 **MUST-SEARCH**: "{domain_focus} best practices"

📊 **CONTEXT**: This task requires expertise in {domain_focus}.
```

**F. Substitute All Variables in Template**

### Step 4: Write Task File

For each task, write to the correct location:

```
{workflow_root_path}/phases/{phase_number}/task-{task_number}-{task_name}.md
```

⚠️ **CONSTRAINT**: File name MUST match pattern `task-{number}-{name}.md`

📖 **DISCOVER-TOOL**: Write file contents

### Step 5: Track Progress

```python
task_files_created += 1
```

---

## Expected Output

**Files Created**:
- `phases/0/task-1-first-task.md`
- `phases/0/task-2-second-task.md`
- `phases/1/task-1-another-task.md`
- ... (one per task across all phases)

**Variables to Capture**:
- `task_files_created`: Integer (total task files written)

---

## Quality Checks

✅ Task template loaded  
✅ All phases processed  
✅ All tasks processed  
✅ Command language applied (🔍, 📖, ⚠️, 🚨)  
✅ Domain expertise integrated where specified  
✅ Examples added  
✅ Validation criteria included  
✅ Files named correctly  
✅ All placeholders substituted  
✅ Count matches expected tasks

---

## Navigation

🎯 **NEXT-MANDATORY**: task-4-verify-generation.md

↩️ **RETURN-TO**: phase.md (after task complete)



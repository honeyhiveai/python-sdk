# Task {{task_number}}: {{task_name}}

**Phase**: {{phase_number}} - {{phase_name}}  
**Purpose**: {{task_purpose}}  
**Depends On**: {{task_dependencies}}  
**Feeds Into**: {{task_feeds_into}}

---

## Objective

{{task_objective}}

---

## Context

📊 **CONTEXT**: {{task_context}}

{{#if task_domain_focus}}
🔍 **MUST-SEARCH**: "{{task_domain_focus_query}}"
{{/if}}

---

## Instructions

{{#each task_steps}}
### Step {{step_number}}: {{step_name}}

{{step_description}}

{{#if step_needs_tool}}
📖 **DISCOVER-TOOL**: {{step_tool_description}}
{{/if}}

{{#if step_has_constraint}}
⚠️ **CONSTRAINT**: {{step_constraint}}
{{/if}}

{{#if step_is_critical}}
🚨 **CRITICAL**: {{step_critical_requirement}}
{{/if}}

{{/each}}

---

## Expected Output

**Variables to Capture**:
{{#each expected_variables}}
- `{{variable_name}}`: {{variable_type}} ({{variable_description}})
{{/each}}

{{#if task_creates_artifacts}}
**Artifacts Created**:
{{#each artifacts}}
- {{artifact_name}}: {{artifact_description}}
{{/each}}
{{/if}}

---

## Quality Checks

{{#each quality_checks}}
✅ {{check_description}}
{{/each}}

---

## Navigation

{{#if is_last_task}}
🎯 **NEXT-MANDATORY**: ../{{next_phase_number}}/phase.md (begin next phase after checkpoint passes)
{{else}}
🎯 **NEXT-MANDATORY**: task-{{next_task_number}}-{{next_task_name}}.md
{{/if}}

↩️ **RETURN-TO**: phase.md (after task complete{{#if is_last_task}}, before phase submission{{/if}})


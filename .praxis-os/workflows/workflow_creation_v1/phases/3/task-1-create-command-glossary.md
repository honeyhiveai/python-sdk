# Task 1: Create Command Glossary

**Phase**: 3 - Core Files & Documentation  
**Purpose**: Document all command symbols in core/command-language-glossary.md  
**Depends On**: Phase 1 (core/ directory created)  
**Feeds Into**: Task 2 (Create Progress Tracking)

---

## Objective

Create a comprehensive command language glossary that documents all command symbols used in the target workflow.

---

## Context

📊 **CONTEXT**: The command glossary serves as a reference for both AI agents and human maintainers, explaining each command symbol's binding nature, format, purpose, and usage examples.

🔍 **MUST-SEARCH**: "command language symbols binding contract"

---

## Instructions

### Step 1: Identify Commands Used in Target Workflow

Review the workflow definition to identify which command symbols will be used:

**Common Commands**:
- 🎯 NEXT-MANDATORY (navigation)
- ↩️ RETURN-TO (subroutines)
- 📊 CONTEXT (informational)
- ⚠️ CONSTRAINT (boundaries)
- 🚨 CRITICAL (hard stops)
- 🔍 MUST-SEARCH (RAG queries)
- 📖 DISCOVER-TOOL (tool discovery)
- 🔄 LOOP-START / LOOP-END (iteration, if dynamic)

⚠️ **CONSTRAINT**: Only document commands that are actually used in the workflow. Don't include unused commands.

### Step 2: Retrieve Command Definitions

For each command to be documented, retrieve its standard definition:

🔍 **MUST-SEARCH**: "command language glossary standard definitions"

Each command entry should include:
- **Symbol and Name**
- **Binding**: Whether it's mandatory or informational
- **Format**: Syntax pattern
- **Purpose**: What it achieves
- **Example**: Real usage from standards

### Step 3: Structure the Glossary

Organize commands by category:

```markdown
# Command Language Glossary

## Navigation Commands
[🎯 NEXT-MANDATORY, ↩️ RETURN-TO]

## Informational Commands
[📊 CONTEXT, 🔄 LOOP-START/END]

## Warning Commands
[⚠️ CONSTRAINT, 🚨 CRITICAL]

## Discovery Commands
[🔍 MUST-SEARCH, 📖 DISCOVER-TOOL]

## Usage Notes
[Best practices, placement, precedence]

## Meta-Workflow Compliance
[How glossary supports principles]
```

### Step 4: Generate File Content

Create clear, consistent documentation for each command.

Format per command:
```markdown
### 🎯 NEXT-MANDATORY
**Binding**: MUST read specified file next
**Format**: `🎯 NEXT-MANDATORY: path/to/file.md`
**Purpose**: Enforce sequential execution
**Example**: `🎯 NEXT-MANDATORY: phases/1/task-1-name.md`
```

### Step 5: Write Glossary File

Write the complete glossary to:

```
{workflow_directory_path}/core/command-language-glossary.md
```

📖 **DISCOVER-TOOL**: Write content to a file

### Step 6: Verify File Created

Confirm the file was created and is readable.

📖 **DISCOVER-TOOL**: Read file to verify contents

Check:
- File exists at correct path
- All commands documented
- Proper markdown formatting
- Examples are clear

---

## Expected Output

**Variables to Capture**:
- `command_glossary_created`: Boolean (true if successful)
- `command_glossary_path`: String (path to file)
- `commands_documented_count`: Integer (number of commands)

---

## Quality Checks

✅ All workflow commands identified  
✅ Standard definitions retrieved  
✅ Glossary properly structured  
✅ All commands documented with examples  
✅ File written successfully  
✅ File verified readable

---

## Navigation

🎯 **NEXT-MANDATORY**: task-2-create-progress-tracking.md

↩️ **RETURN-TO**: phase.md (after task complete)


# Task 5: Verify Binding Contract

**Phase**: 4 - Meta-Workflow Compliance  
**Purpose**: Confirm contract in entry point with acknowledgment  
**Depends On**: Task 4 (gates verified)  
**Feeds Into**: Task 6 (Verify Horizontal Decomposition)

---

## Objective

Verify the workflow includes a clear binding contract that establishes the agreement between the AI agent and the workflow system.

---

## Context

📊 **CONTEXT**: The binding contract is typically presented at workflow entry (Phase 0) and requires explicit acknowledgment. It establishes that command symbols are mandatory, not optional suggestions.

---

## Instructions

### Step 1: Locate Entry Point

The workflow entry point is typically:

```
{workflow_directory_path}/phases/0/phase.md
```

This is the first file an agent reads when starting the workflow.

📖 **DISCOVER-TOOL**: Read file contents

### Step 2: Search for Binding Contract Language

Look for binding contract indicators:

📖 **DISCOVER-TOOL**: Search for text patterns

**Key phrases to find**:
- "binding contract"
- "mandatory"
- "MUST" (in command context)
- "acknowledgment" or "acknowledge"
- Explicit statement about command enforcement

Example contract language:
```markdown
## Binding Contract

By proceeding with this workflow, you acknowledge:
- All 🎯 NEXT-MANDATORY commands are binding
- All 🚨 CRITICAL conditions must be met
- All ⚠️ CONSTRAINTS must be respected
- Navigation sequence must be followed

**Do you acknowledge this binding contract?**
```

### Step 3: Verify Contract Completeness

The binding contract should cover:

1. **Command Enforcement**: Commands are mandatory, not suggestions
2. **Validation Gates**: Checkpoints must be passed
3. **Navigation**: Sequence must be followed
4. **Quality Standards**: Metrics must be met

Check that the contract addresses these areas.

### Step 4: Check for Acknowledgment Mechanism

The contract should require acknowledgment, such as:
- Explicit question: "Do you acknowledge?"
- Stop point before proceeding
- First task verifies acknowledgment

⚠️ **CONSTRAINT**: Simply stating rules is not enough. There should be a mechanism for the agent to explicitly acknowledge before proceeding.

### Step 5: Verify Command Language Reference

Check that Phase 0 or a prominent location references the command glossary:

```markdown
📖 See: core/command-language-glossary.md for complete command definitions
```

Or:
```markdown
🔍 **MUST-SEARCH**: "command language binding contract"
```

### Step 6: Check for Contract Throughout Workflow

While the main contract is at entry, verify that binding language is reinforced:

- 🚨 CRITICAL markers on validation gates
- ⚠️ CONSTRAINT markers on requirements
- 🎯 NEXT-MANDATORY for forced navigation

This reinforces the binding nature throughout execution.

### Step 7: Generate Binding Contract Report

```markdown
# Binding Contract Compliance Report

## Contract Location
**Found**: {yes/no}
**Location**: {file_path}

## Contract Elements
- Command Enforcement Stated: {yes/no}
- Validation Gates Mentioned: {yes/no}
- Navigation Requirements: {yes/no}
- Quality Standards Referenced: {yes/no}

## Acknowledgment Mechanism
**Present**: {yes/no}
**Type**: {explicit question/implicit/none}

## Command Glossary Reference
**Present**: {yes/no}

## Contract Reinforcement
**Critical Markers**: {count}
**Constraint Markers**: {count}
**Next-Mandatory Usage**: {count}

## Overall Compliance
{PASS/FAIL}

## Recommendations
[Any improvements needed]
```

---

## Expected Output

**Variables to Capture**:
- `binding_contract_present`: Boolean (true if found and complete)
- `contract_location`: String (file path)
- `acknowledgment_mechanism`: Boolean (true if present)
- `contract_report`: String (report content)

---

## Quality Checks

✅ Entry point located  
✅ Binding contract language found  
✅ Contract completeness verified  
✅ Acknowledgment mechanism present  
✅ Command glossary referenced  
✅ Contract reinforced throughout  
✅ Compliance report generated

---

## Navigation

🎯 **NEXT-MANDATORY**: task-6-verify-horizontal-decomposition.md

↩️ **RETURN-TO**: phase.md (after task complete)


# Command Language Glossary

This workflow uses standardized command symbols for binding AI agent behavior.

## Navigation Commands

### 🎯 NEXT-MANDATORY
**Binding**: MUST read specified file next  
**Format**: `🎯 NEXT-MANDATORY: path/to/file.md`  
**Purpose**: Enforce sequential execution  
**Example**: `🎯 NEXT-MANDATORY: phases/1/task-1-create-workflow-directory.md`

### ↩️ RETURN-TO
**Binding**: MUST return to specified location after completion  
**Format**: `↩️ RETURN-TO: path/to/file.md`  
**Purpose**: Handle subroutines and nested navigation  
**Example**: `↩️ RETURN-TO: phases/0/phase.md`

## Informational Commands

### 📊 CONTEXT
**Binding**: NON-binding context for better decision-making  
**Format**: `📊 CONTEXT: [description]`  
**Purpose**: Provide helpful background without forcing actions  
**Example**: `📊 CONTEXT: This task integrates with the RAG system`

### 🔄 LOOP-START / LOOP-END
**Binding**: MUST iterate through specified items  
**Format**: 
```
🔄 LOOP-START: [variable] in [collection]
  ...tasks...
🔄 LOOP-END
```
**Purpose**: Dynamic iteration  
**Example**: `🔄 LOOP-START: phase in target_phases`

## Warning Commands

### ⚠️ CONSTRAINT
**Binding**: MUST respect specified limitation  
**Format**: `⚠️ CONSTRAINT: [requirement]`  
**Purpose**: Enforce boundaries and requirements  
**Example**: `⚠️ CONSTRAINT: Task file MUST be ≤100 lines`

### 🚨 CRITICAL
**Binding**: MUST NOT proceed without satisfying condition  
**Format**: `🚨 CRITICAL: [condition]`  
**Purpose**: Hard stops for critical requirements  
**Example**: `🚨 CRITICAL: Validation MUST pass before Phase 1`

## Discovery Commands

### 🔍 MUST-SEARCH
**Binding**: MUST execute `search_standards()` with specified query  
**Format**: `🔍 MUST-SEARCH: "query text"`  
**Purpose**: Trigger RAG-based knowledge retrieval  
**Example**: `🔍 MUST-SEARCH: "how to write validation gates"`

### 📖 DISCOVER-TOOL
**Binding**: MUST discover tool via natural language or search  
**Format**: `📖 DISCOVER-TOOL: [tool purpose description]`  
**Purpose**: Avoid hardcoding tool names, use discovery  
**Example**: `📖 DISCOVER-TOOL: list directory contents`

## Usage Notes

1. **Command Placement**: Place commands on their own lines for visibility
2. **Command Stacking**: Multiple commands can apply to same section
3. **Precedence**: 🚨 CRITICAL > ⚠️ CONSTRAINT > 🎯 NEXT-MANDATORY
4. **Readability**: Commands enhance, not replace, clear prose

## Meta-Workflow Compliance

This glossary supports:
- **Binding Contract**: Clear agent-tool API
- **Validation Gates**: 🚨 CRITICAL for checkpoints  
- **Horizontal Decomposition**: 🎯 NEXT-MANDATORY for sequencing
- **RAG Integration**: 🔍 MUST-SEARCH for knowledge retrieval


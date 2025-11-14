# Workflow Creation v1 - Design Summary

**Version**: 1.0.0  
**Created**: 2025-10-13  
**Type**: Dynamic Workflow  
**Purpose**: Systematic creation of meta-workflow-compliant workflows

## Problem Statement

Creating high-quality workflows manually is:
- **Time-consuming**: 50-100+ task files to write
- **Inconsistent**: Easy to miss meta-workflow principles
- **Error-prone**: Validation gates might not be parseable
- **Tedious**: Repetitive command application
- **Incomplete**: Domain expertise not systematically integrated

This workflow solves these problems by providing a systematic, validated approach to workflow creation.

## Why a Workflow?

This is a workflow (not a tool or standard) because:
- **Multi-phase process**: Requires setup, iteration, validation, and testing
- **Validation gates**: Quality checkpoints at phase boundaries
- **Domain expertise integration**: RAG queries for specialized knowledge
- **Human review**: Final approval required before deployment
- **Systematic execution**: Not just guidance, but enforced sequencing

## Success Criteria

✅ All target workflow phases fully populated (phase.md + all task files)  
✅ 95%+ task files ≤100 lines (horizontal decomposition)  
✅ 80%+ command language coverage (binding contract)  
✅ 100% phases have validation gates  
✅ 100% meta-workflow compliance  
✅ Human approval obtained for final workflow

## Architecture

### Static Phases (6 Total)

**Phase 0: Input Conversion & Preprocessing** (5 tasks)
- Determine input type (design document or YAML)
- Read input document
- Extract from design document (if applicable)
- Generate YAML definition (if applicable)
- Validate generated definition

**Phase 1: Definition Import & Validation** (5 tasks)
- Load workflow definition YAML
- Validate structure and completeness
- Prepare for creation

**Phase 2: Workflow Scaffolding** (8 tasks)
- Create directory structure
- Generate metadata.json
- Set up core and supporting-docs

**Phase 3: Core Files & Documentation** (4 tasks)
- Create command glossary
- Create progress tracking
- Archive definition
- Generate design summary

**Phase N+4: Meta-Workflow Compliance** (10 tasks)
- Audit file sizes
- Audit command coverage
- Verify three-tier architecture
- Verify validation gates
- Verify binding contract
- Verify horizontal decomposition
- Generate compliance report
- Fix violations
- Re-validate
- Final compliance check

**Phase N+5: Testing & Delivery** (8 tasks)
- Dry-run navigation
- Validate commands
- Validate gates are parseable
- Identify usability issues
- Implement refinements
- Create usage guide
- Final validation
- Human review (APPROVAL REQUIRED)

### Dynamic Phases (4 to N+3)

The workflow dynamically creates phases for each target workflow phase:
- Iterates N times (once per target phase)
- Uses templates from `phases/dynamic/`
- Creates phase.md and all task files
- Each iteration includes validation

## Input: Workflow Definition YAML

The workflow consumes a structured YAML file with:
- **Metadata**: Name, version, type, language
- **Problem Statement**: What it solves and why
- **Success Criteria**: Measurable outcomes
- **Phases**: Array of phase objects with tasks
- **Validation Gates**: Evidence requirements per phase
- **Quality Standards**: File size, command coverage targets
- **Dynamic Config**: If dynamic, iteration logic and variables

Template: `universal/templates/workflow-definition-template.yaml`

## Output: Complete Workflow

The workflow produces:
- Complete directory structure
- metadata.json with all phase/task references
- All phase.md files with overview and navigation
- All task-N-name.md files with instructions
- Command language glossary
- Progress tracking template
- Archived definition and design summary
- Compliance report
- Usage guide

## Key Design Decisions

### 1. YAML-Driven, Not Interactive
- Design session creates YAML definition
- Workflow reads YAML, not prompting user
- Enables reproducibility and version control

### 2. Dynamic Iteration for Scalability
- Static phases for setup/validation
- Dynamic middle for target phase creation
- Scales to any number of target phases

### 3. RAG Integration via MUST-SEARCH
- Task files stay lightweight (≤100 lines)
- Domain knowledge retrieved on-demand
- No duplication of standards content

### 4. Validation Gates at Every Boundary
- Phase 0: Input converted
- Phase 1: Definition validated
- Phase 2: Scaffolding verified
- Phase 3: Core files created
- Each dynamic iteration: Target phase complete
- Phase N+4: Compliance confirmed
- Phase N+5: Human approval obtained

### 5. Embedded Compliance Auditing
- Self-validates against meta-workflow principles
- Generates compliance report
- Fixes violations automatically
- Re-validates after fixes

## Quality Standards

| Metric | Target | Enforced |
|--------|--------|----------|
| Task file size | ≤100 lines | Phase N+4, Task 1 |
| Command coverage | ≥80% | Phase N+4, Task 2 |
| Validation gates | 100% | Phase N+4, Task 4 |
| Three-tier architecture | 100% | Phase N+4, Task 3 |
| Horizontal decomposition | 100% | Phase N+4, Task 6 |
| Meta-workflow compliance | 100% | Phase N+4, Task 10 |

## Usage Pattern

```
1. Design Session
   └─> Create workflow-name-definition.yaml

2. Start Workflow
   └─> start_workflow("workflow_creation_v1", "workflow-name-definition.yaml", 
                       {definition_path: "path/to/definition.yaml"})

3. Execute Phases
   ├─> Phase 0: Convert input (design doc → YAML)
   ├─> Phase 1: Import & validate definition
   ├─> Phase 2: Create scaffolding
   ├─> Phase 3: Create core files
   ├─> Phases 4-N+3: Create each target phase (dynamic)
   ├─> Phase N+4: Validate compliance
   └─> Phase N+5: Test & deliver (human approval)

4. Output
   └─> .praxis-os/workflows/workflow_name_v1/ (complete workflow)
```

## Meta-Workflow Compliance

This workflow embodies all 5 meta-workflow principles:

1. **LLM Constraint Awareness**
   - All task files ≤100 lines
   - RAG queries instead of long context
   - Horizontal decomposition

2. **Horizontal Task Decomposition**
   - Single responsibility per task
   - 34 static tasks across 5 phases
   - Clear, focused objectives

3. **Command Language + Binding Contract**
   - 80%+ command usage
   - 🎯 NEXT-MANDATORY for sequencing
   - 🔍 MUST-SEARCH for RAG
   - 🚨 CRITICAL for gates

4. **Validation Gates at Boundaries**
   - Every phase has evidence-based checkpoint
   - Human approval for final delivery
   - Programmatic validation in workflow_engine.py

5. **Evidence-Based Progress**
   - Measurable artifacts at each gate
   - Compliance metrics tracked
   - Quality standards enforced

## Future Enhancements

- **Self-Improvement**: Use workflow_creation_v1 to upgrade itself
- **Templates Library**: Pre-built definitions for common workflow types
- **Compliance CI/CD**: Automated validation on workflow changes
- **Multi-Language Support**: Language-specific task templates
- **Nested Workflow Support**: Task can invoke other workflows

---

**Full Design Document**: `working-docs/workflow-creation-v1-design.md`  
**Definition YAML**: `supporting-docs/workflow-definition.yaml`


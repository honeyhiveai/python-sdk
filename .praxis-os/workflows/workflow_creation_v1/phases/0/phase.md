# Phase 0: Input Conversion & Preprocessing

**Purpose:** Accept multiple input formats, normalize to YAML definition  
**Deliverable:** Validated YAML definition ready for Phase 1

---

## Overview

This phase accepts either design documents (markdown) or YAML definitions, converts design docs to standard YAML format if needed, and outputs a validated definition path for Phase 1.

We systematically:

1. **Determine** input type (design document or YAML definition)
2. **Read** input document from provided path
3. **Extract** structured information (if design document)
4. **Generate** YAML definition following template (if design document)
5. **Validate** generated definition is well-formed

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

---

## Tasks

| # | Task | File | Status |
|---|------|------|--------|
| 1 | Determine Input Type | task-1-determine-input-type.md | ⬜ |
| 2 | Read Input Document | task-2-read-input-document.md | ⬜ |
| 3 | Extract from Design Document | task-3-extract-from-design.md | ⬜ |
| 4 | Generate YAML Definition | task-4-generate-yaml-definition.md | ⬜ |
| 5 | Validate Generated Definition | task-5-validate-generated-definition.md | ⬜ |

---

## Context

📊 **CONTEXT**: This is the entry phase for workflow_creation_v1. In the prAxIs OS operating model, Phase 2 (Spec Creation) outputs design documents in markdown format. This phase bridges that output to the YAML format expected by the rest of the workflow.

**Primary Use Case (90%):** Design document input  
**Expert Use Case (10%):** Pre-built YAML definition input

---

## Validation Gate

🚨 **CRITICAL**: Phase 0 MUST complete successfully before proceeding to Phase 1.

**Evidence Required**:

| Evidence | Type | Validator | Description |
|----------|------|-----------|-------------|
| `input_type` | string | non_empty | Type of input provided (design_document or yaml_definition) |
| `input_document_read` | boolean | is_true | Input document successfully read |
| `design_document_converted` | boolean | is_true | Design document converted to YAML (if applicable) |
| `standard_definition_path` | string | file_exists | Path to YAML definition file for Phase 1 |
| `yaml_syntax_valid` | boolean | is_true | YAML syntax validated successfully |

**Human Approval**: Not required

---

## Navigation

**Start Here**: 🎯 NEXT-MANDATORY: task-1-determine-input-type.md

**After Phase 0 Complete**: 🎯 NEXT-MANDATORY: ../1/phase.md


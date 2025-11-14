# Standards Creation Workflow v1

**Purpose**: Automated standards creation with programmatic quality validation

## Overview

This workflow codifies and validates the standards creation process, ensuring AI-authored content is RAG-optimized, semantically complete, and immediately discoverable.

## Key Features

- **Phase-Gated Validation**: 6 phases with quality checkpoints
- **RAG Optimization**: Programmatic keyword density and query hook validation
- **Discoverability Testing**: Multi-angle query testing (>= 80% threshold)
- **Semantic Validation**: Chunk size, completeness, and link validation
- **Automated Integration**: Commit, index rebuild, and immediate discoverability verification

## Success Criteria

- 95%+ standards pass validation on first attempt (after AI learns)
- 85%+ discoverability rate (queries find standard in top 3)
- 0 standards committed without validation passing
- Validation completes in < 60 seconds

## Usage

```python
# Start workflow
session = start_workflow(
    workflow_type="standards_creation_v1",
    target_file="my-standard-name"
)

# Follow phase-gated execution
get_current_phase(session_id)
get_task(session_id, phase, task_number)
complete_phase(session_id, phase, evidence)
```

## Phases

1. **Phase 0**: Discovery & Context (5 tasks)
2. **Phase 1**: Content Creation (6 tasks)
3. **Phase 2**: RAG Optimization (4 tasks)
4. **Phase 3**: Discoverability Testing (5 tasks)
5. **Phase 4**: Semantic Validation (5 tasks)
6. **Phase 5**: Integration & Commit (6 tasks)

## Quality Standards

- Structure compliance: 100%
- RAG optimization: Required for all standards
- Discoverability: >= 80% (4/5 queries in top 3)
- Semantic quality: Chunks 100-500 tokens, all links valid
- No content duplication: Links to source of truth

## Generated

Date: 2025-10-13  
Version: 1.0.0  
Type: standards_creation


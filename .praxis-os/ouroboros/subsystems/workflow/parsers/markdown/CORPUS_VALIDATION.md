# Tasks.md Parser Validation Corpus

**Generated:** 2025-11-05  
**Purpose:** Validation dataset for dynamic pattern discovery parser  
**Source:** 39 tasks.md files from `.praxis-os/specs` and `../python-sdk/.agent-os/specs`

---

## Corpus Statistics

- **Total files analyzed:** 39
- **Files with Phase 0:** 3 (7.7%)
- **Total phase headers:** 141
- **Total metadata headers:** 481
- **Average phases per file:** 3.6
- **Average metadata headers per file:** 12.3

---

## Phase Header Patterns

### Level Distribution
- **Level 2 (##):** 141 (100%) - All phase headers are level 2

### Pattern Distribution
- **"Phase N:" pattern:** 141 (100%) - All follow "Phase N: Name" format

### Phase 0 Files
Files that start with Phase 0 (require phase shift):
1. `.praxis-os/specs/approved/2025-11-04-rag-index-submodule-refactor/tasks.md`
2. `.praxis-os/specs/completed/2025-11-05-parser-submodule-refactor/tasks.md`
3. `../python-sdk/.agent-os/specs/2025-10-03-agent-os-mcp-rag-evolution/tasks.md`

### Phase Header Examples
1. `Phase 1: Core Infrastructure`
2. `Phase 2: Tool Integration and File System`
3. `Phase 0: Foundation & Utilities`
4. `Phase 1: Standards Creation`
5. `Phase 3: Base Personas and Testing`

---

## Metadata Header Patterns

### Top Metadata Keywords (Frequency)
1. **tasks:** 124 occurrences
2. **validation:** 121 occurrences
3. **gate:** 59 occurrences
4. **dependencies:** 50 occurrences
5. **criteria:** 42 occurrences
6. **risk:** 38 occurrences
7. **acceptance:** 35 occurrences
8. **success:** 31 occurrences
9. **execution:** 3 occurrences
10. **estimated:** 2 occurrences

### Common Metadata Header Patterns

**Phase-specific metadata:**
- `Phase N Tasks` (124 occurrences)
- `Phase N Validation Gate` (59 occurrences)
- `Phase N Acceptance Criteria` (35 occurrences)

**General metadata sections:**
- `Dependencies`
- `Linear Phase Dependencies`
- `Task-Level Dependencies`
- `Risk Mitigation`
- `Risk: [description]`
- `Acceptance Criteria Summary`
- `Success Metrics`
- `Implementation Tasks`
- `Time Estimates`

### Metadata Header Examples
1. `Implementation Tasks`
2. `Phase 1 Tasks`
3. `Phase 1 Validation Gate`
4. `Phase 2 Tasks`
5. `Phase 2 Validation Gate`
6. `Phase 3 Tasks`
7. `Phase 3 Validation Gate`
8. `Phase 4 Tasks`
9. `Phase 4 Validation Gate`
10. `Dependencies`
11. `Linear Phase Dependencies`
12. `Task-Level Dependencies`
13. `Risk Mitigation`
14. `Risk: LLM API costs exceed budget`
15. `Acceptance Criteria Summary`
16. `Success Metrics (From SRD)`
17. `Phase Execution Order`
18. `Phase 0 Tasks (Detailed)`
19. `Phase 0 Acceptance Criteria`
20. `Phase 0 Validation Gate`

---

## Parser Validation Requirements

### Must Correctly Identify

1. **Phase Headers:**
   - Level 2 headers (##)
   - Pattern: `Phase N: Name` where N is a number
   - Must NOT identify metadata sections as phases

2. **Metadata Sections (Must Reject):**
   - `Phase N Tasks` - NOT a phase header
   - `Phase N Validation Gate` - NOT a phase header
   - `Phase N Acceptance Criteria` - NOT a phase header
   - `Phase Execution Order` - NOT a phase header
   - `Dependencies` - NOT a phase header
   - `Risk Mitigation` - NOT a phase header

3. **Phase 0 Detection:**
   - Must detect when Phase 0 exists
   - Must apply +1 shift for workflow harness
   - Phase 0 in tasks.md → Phase 1 in workflow

### Expected Behavior

1. **Pattern Discovery:**
   - Should discover that all phase headers are level 2
   - Should discover "Phase N:" pattern
   - Should identify metadata keywords from document

2. **Scoring:**
   - Phase headers matching discovered pattern → high score (≥0.7)
   - Metadata headers → low score (<0.7)
   - Level 3+ headers → penalized

3. **Validation:**
   - Phase sequence must be sequential (no gaps)
   - Phase sequence must have no duplicates
   - Must handle Phase 0 correctly

---

## Test Cases

### Critical Test Cases

1. **Phase 0 Detection:**
   - File: `2025-11-04-rag-index-submodule-refactor/tasks.md`
   - Expected: Detects Phase 0, applies +1 shift
   - Validation: Phase 0 → workflow Phase 1

2. **Metadata Rejection:**
   - Header: `### Phase 0 Tasks (Detailed)`
   - Expected: Score < 0.7, NOT classified as phase
   - Validation: Should NOT create duplicate Phase 0

3. **Phase Execution Order:**
   - Header: `## Phase Execution Order`
   - Expected: Score < 0.7, NOT classified as phase
   - Validation: Should NOT be extracted as phase

4. **Standard Phase Detection:**
   - Header: `## Phase 1: Core Infrastructure`
   - Expected: Score ≥ 0.7, classified as phase
   - Validation: Extracted as Phase 1

---

## Files by Status

### Files with 0 Phases (Need Investigation)
These files may have different formats or be incomplete:
- `2025-10-07-dynamic-workflow-session-refactor` (9 headers)
- `2025-10-07-mcp-server-modular-redesign` (14 headers)
- `2025-09-06-integration-testing-consolidation` (39 headers)
- `2025-09-03-documentation-quality-prevention` (25 headers)
- `2025-09-05-compatibility-matrix-framework` (67 headers)
- `2025-09-03-drop-project-from-tracer-init` (41 headers)
- `2025-09-04-pyproject-integration-titles` (65 headers)
- `2025-09-05-non-instrumentor-integrations` (63 headers)
- `2025-09-03-openinference-mcp-instrumentor` (32 headers)
- `2025-09-17-compatibility-matrix-enhancement` (46 headers)
- `2025-09-02-performance-optimization` (20 headers)

### Files with Phases (Successfully Parsed)
36 files with valid phase structure

---

## Validation Script

Run validation script:
```bash
cd /path/to/praxis-os
PYTHONPATH=.praxis-os/ouroboros:. python3 .praxis-os/ouroboros/subsystems/workflow/parsers/markdown/validate_corpus.py
```

This will:
1. Analyze all 39 tasks.md files
2. Extract patterns
3. Test parser on each file
4. Report success/failure rates
5. Validate phase count accuracy

---

## Key Insights

1. **Consistency:** All phase headers follow same pattern (Level 2, "Phase N:")
2. **Metadata Variety:** Many metadata header patterns exist
3. **Phase 0 Rare:** Only 3 files (7.7%) use Phase 0
4. **High Metadata Density:** Average 12.3 metadata headers per file
5. **Pattern Discovery Critical:** Need to discover metadata keywords dynamically

---

## Recommendations

1. **Pattern Discovery:**
   - Analyze document structure first
   - Identify metadata sections by keywords
   - Build adaptive scoring rules

2. **Validation:**
   - Test on all 39 files
   - Validate Phase 0 detection
   - Ensure metadata rejection

3. **Robustness:**
   - Handle format variations gracefully
   - Provide clear error messages
   - Fallback to heuristics if discovery fails


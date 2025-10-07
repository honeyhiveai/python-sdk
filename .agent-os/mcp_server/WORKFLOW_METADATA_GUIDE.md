# Workflow Metadata Guide

## Overview

Workflow metadata provides upfront overview information about workflow structure, phases, and expected outputs. This enhancement allows AI agents to see the complete workflow roadmap immediately when starting a workflow, eliminating the need for separate API calls.

## What's New

### Enhanced `start_workflow` Response

The `start_workflow` MCP tool now returns a `workflow_overview` field containing:

- **Total number of phases** - Know how many phases exist upfront
- **Phase names and purposes** - Understand what each phase does
- **Estimated effort** - Plan time allocation for each phase
- **Key deliverables** - Know what artifacts to expect
- **Validation criteria** - Understand checkpoint requirements

### Backward Compatibility

The enhancement is **fully backward compatible**:
- Workflows with `metadata.json` files get rich overview information
- Workflows without metadata files get auto-generated fallback metadata
- All existing workflows continue to work without modification

## Metadata File Structure

### Location

Workflow metadata files are stored at:
```
universal/workflows/{workflow_type}/metadata.json
```

Examples:
- `universal/workflows/test_generation_v3/metadata.json`
- `universal/workflows/production_code_v2/metadata.json`

### Schema

```json
{
  "workflow_type": "string",           // Workflow identifier
  "version": "string",                 // Workflow version (semver)
  "description": "string",             // Human-readable description
  "total_phases": number,              // Total number of phases
  "estimated_duration": "string",      // Expected duration (e.g., "2-3 hours")
  "primary_outputs": ["string"],       // List of key outputs
  "phases": [                          // Array of phase metadata
    {
      "phase_number": number,          // Phase number (0-based)
      "phase_name": "string",          // Human-readable phase name
      "purpose": "string",             // What this phase accomplishes
      "estimated_effort": "string",    // Expected time for this phase
      "key_deliverables": ["string"],  // What this phase produces
      "validation_criteria": ["string"] // Checkpoint requirements
    }
  ]
}
```

## Example: Test Generation Workflow

```json
{
  "workflow_type": "test_generation_v3",
  "version": "3.0.0",
  "description": "Generate comprehensive test suites with validation gates",
  "total_phases": 8,
  "estimated_duration": "2-3 hours",
  "primary_outputs": [
    "Unit test files",
    "Integration test files",
    "Validation test files",
    "Coverage report",
    "Test documentation"
  ],
  "phases": [
    {
      "phase_number": 0,
      "phase_name": "Setup",
      "purpose": "Initialize test environment and dependencies",
      "estimated_effort": "10 minutes",
      "key_deliverables": [
        "Test framework configured",
        "Dependencies installed",
        "Test directory structure created"
      ],
      "validation_criteria": [
        "Test runner executes successfully",
        "All dependencies resolved"
      ]
    },
    {
      "phase_number": 1,
      "phase_name": "Analysis",
      "purpose": "Analyze target code and plan test strategy",
      "estimated_effort": "15-20 minutes",
      "key_deliverables": [
        "Code structure analysis",
        "Function/method inventory",
        "Test path determination"
      ],
      "validation_criteria": [
        "All public functions identified",
        "Test types determined",
        "Coverage goals set"
      ]
    }
    // ... additional phases
  ]
}
```

## API Response Format

### `start_workflow` Response

```python
{
  "session_id": "uuid",
  "workflow_type": "test_generation_v3",
  "target_file": "path/to/file.py",
  "current_phase": 1,
  "requested_phase": 1,
  
  # NEW: Workflow overview
  "workflow_overview": {
    "workflow_type": "test_generation_v3",
    "version": "3.0.0",
    "description": "Generate comprehensive test suites with validation gates",
    "total_phases": 8,
    "estimated_duration": "2-3 hours",
    "primary_outputs": ["test files", "coverage report", ...],
    "phases": [
      {
        "phase_number": 0,
        "phase_name": "Setup",
        "purpose": "Initialize test environment and dependencies",
        "estimated_effort": "10 minutes",
        "key_deliverables": [...],
        "validation_criteria": [...]
      },
      // ... all phases
    ]
  },
  
  # Existing fields
  "phase_content": {...},
  "artifacts_available": {},
  "completed_phases": [],
  "is_complete": false
}
```

## Benefits for AI Agents

### Before Enhancement
```python
# Agent had to make 2 calls to understand workflow structure
session = start_workflow("test_generation_v3", "file.ts")  # No phase count!
state = get_workflow_state(session_id)  # Only now sees total_phases: 8
```

### After Enhancement
```python
# Agent gets everything in one call
session = start_workflow("test_generation_v3", "file.ts")
total_phases = session["workflow_overview"]["total_phases"]  # 8
phases = session["workflow_overview"]["phases"]  # All phase info

# Can now plan effectively:
print(f"Starting {total_phases}-phase workflow")
for phase in phases:
    print(f"Phase {phase['phase_number']}: {phase['phase_name']}")
    print(f"  Purpose: {phase['purpose']}")
    print(f"  Effort: {phase['estimated_effort']}")
```

## Implementation Details

### Loading Strategy

The `WorkflowEngine` uses a three-tier loading strategy:

1. **Cache Check** - Check in-memory cache for already-loaded metadata
2. **File Load** - Try to load `metadata.json` from workflow directory
3. **Fallback Generation** - Generate minimal metadata based on workflow type

### Fallback Metadata

For workflows without `metadata.json` files, the engine generates basic metadata:

- **Test workflows** - 8 phases, generic names
- **Production workflows** - 6 phases, generic names

This ensures all existing workflows continue working without modification.

### Caching

Loaded metadata is cached in memory to avoid repeated file I/O:

```python
# First call loads from disk
metadata1 = engine.load_workflow_metadata("test_generation_v3")

# Subsequent calls use cache
metadata2 = engine.load_workflow_metadata("test_generation_v3")  # Cache hit!
```

## Creating Metadata for New Workflows

### Step 1: Create Workflow Directory

```bash
mkdir -p universal/workflows/{workflow_name}
```

### Step 2: Create metadata.json

```bash
touch universal/workflows/{workflow_name}/metadata.json
```

### Step 3: Populate Metadata

Use the schema above and examples from existing workflows. Key considerations:

- **Accurate phase count** - Must match actual workflow phases
- **Clear phase names** - Use descriptive, action-oriented names
- **Realistic time estimates** - Base on actual execution experience
- **Specific deliverables** - List concrete outputs, not vague goals
- **Testable criteria** - Make validation criteria measurable

### Step 4: Validate

The metadata is automatically validated when loaded. Check logs for:

```
INFO - Loaded metadata for test_generation_v3: 8 phases, 8 phase definitions
```

## Migration Path

### Phase 1: Enhancement (Complete) ✅
- Added `WorkflowMetadata` and `PhaseMetadata` models
- Implemented metadata loading with fallback
- Updated `start_workflow()` to include overview
- Backward compatible design

### Phase 2: Metadata Creation (Complete) ✅
- Created metadata for `test_generation_v3`
- Created metadata for `production_code_v2`

### Phase 3: Future Enhancements
- Add metadata validation schema
- Create CI checks for metadata consistency
- Add metadata to workflow creation templates
- Generate metadata from existing workflow documentation

## Troubleshooting

### Metadata Not Loading

**Symptom:** Workflow shows generic phase names ("Phase 0", "Phase 1", etc.)

**Solutions:**
1. Check file exists: `universal/workflows/{workflow_type}/metadata.json`
2. Validate JSON syntax: `python -m json.tool metadata.json`
3. Check logs for errors: `.agent-os/.cache/mcp_server.log`

### Phase Count Mismatch

**Symptom:** Metadata shows different phase count than actual workflow

**Solutions:**
1. Update `total_phases` in metadata.json
2. Ensure `phases` array has correct length
3. Clear metadata cache by restarting MCP server

### Invalid JSON

**Symptom:** Log shows "Failed to load metadata.json"

**Solutions:**
1. Validate JSON: `python -m json.tool metadata.json`
2. Check for trailing commas, missing quotes, etc.
3. Compare against working examples

## Data Models

### Python Models

```python
@dataclass
class PhaseMetadata:
    phase_number: int
    phase_name: str
    purpose: str
    estimated_effort: str
    key_deliverables: List[str]
    validation_criteria: List[str]

@dataclass
class WorkflowMetadata:
    workflow_type: str
    version: str
    description: str
    total_phases: int
    estimated_duration: str
    primary_outputs: List[str]
    phases: List[PhaseMetadata]
```

### TypeScript Types (for MCP clients)

```typescript
interface PhaseMetadata {
  phase_number: number;
  phase_name: string;
  purpose: string;
  estimated_effort: string;
  key_deliverables: string[];
  validation_criteria: string[];
}

interface WorkflowMetadata {
  workflow_type: string;
  version: string;
  description: string;
  total_phases: number;
  estimated_duration: string;
  primary_outputs: string[];
  phases: PhaseMetadata[];
}

interface StartWorkflowResponse {
  session_id: string;
  workflow_type: string;
  workflow_overview: WorkflowMetadata;  // NEW
  current_phase: number;
  phase_content: any;
  completed_phases: number[];
  is_complete: boolean;
}
```

## Version History

### v1.0.0 (2025-10-06)
- Initial implementation of workflow metadata system
- Added `workflow_overview` to `start_workflow` response
- Created metadata for `test_generation_v3` and `production_code_v2`
- Implemented backward-compatible fallback system
- Added comprehensive documentation

## References

- [Original Bug Report](../bug-reports/workflow-overview-enhancement.md)
- [Workflow Engine Implementation](workflow_engine.py)
- [Data Models](models.py)
- [Example Metadata: Test Generation](../universal/workflows/test_generation_v3/metadata.json)
- [Example Metadata: Production Code](../universal/workflows/production_code_v2/metadata.json)

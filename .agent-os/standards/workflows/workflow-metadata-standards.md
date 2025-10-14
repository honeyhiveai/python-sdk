# Workflow Metadata Standards

**Standards for creating and maintaining workflow metadata files**

---

## 🎯 Purpose

This document defines standards for workflow metadata files that enable semantic discovery, AI planning, and proper workflow execution.

---

## 📋 Metadata Schema (Required Fields)

### Complete Schema

```json
{
  "workflow_type": "string (required)",
  "version": "semver (required)",
  "description": "string (required)",
  "total_phases": "number (required)",
  "estimated_duration": "string (required)",
  "primary_outputs": ["string (required)"],
  "phases": [
    {
      "phase_number": "number (required)",
      "phase_name": "string (required)",
      "purpose": "string (required)",
      "estimated_effort": "string (required)",
      "key_deliverables": ["string (required)"],
      "validation_criteria": ["string (required)"]
    }
  ]
}
```

### Field Descriptions

#### Root Level

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `workflow_type` | string | Yes | Unique workflow identifier | `"test_generation_v3"` |
| `version` | string | Yes | Semantic version | `"3.0.0"` |
| `description` | string | Yes | Human-readable description | `"Generate comprehensive test suites"` |
| `total_phases` | number | Yes | Total number of phases | `8` |
| `estimated_duration` | string | Yes | Expected total time | `"2-3 hours"` |
| `primary_outputs` | array | Yes | Key deliverables | `["test files", "coverage report"]` |
| `phases` | array | Yes | Phase definitions | See phase schema |

#### Phase Level

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `phase_number` | number | Yes | Phase identifier (0-based) | `0` |
| `phase_name` | string | Yes | Human-readable name | `"Analysis"` |
| `purpose` | string | Yes | What phase accomplishes | `"Analyze code structure"` |
| `estimated_effort` | string | Yes | Expected phase duration | `"15-20 minutes"` |
| `key_deliverables` | array | Yes | Phase outputs | `["Code analysis", "Test strategy"]` |
| `validation_criteria` | array | Yes | Checkpoint requirements | `["Functions identified"]` |

---

## 📍 File Location

### Standard Location

```
universal/workflows/{workflow_type}/metadata.json
```

### Examples

```
universal/workflows/
├── test_generation_v3/
│   └── metadata.json
├── production_code_v2/
│   └── metadata.json
└── api_validation/
    └── metadata.json
```

### ❌ Invalid Locations

```
# DON'T put metadata here:
.agent-os/workflows/                    # Wrong directory level
universal/standards/workflows/          # Not in standards
mcp_server/workflows/                   # Not in workflows directory
```

---

## ✅ Metadata Quality Standards

### 1. Phase Numbering

**Rule:** Phases MUST be numbered sequentially starting from 0

```json
// ✅ CORRECT
"phases": [
  {"phase_number": 0, "phase_name": "Setup"},
  {"phase_number": 1, "phase_name": "Analysis"},
  {"phase_number": 2, "phase_name": "Generation"}
]

// ❌ WRONG
"phases": [
  {"phase_number": 1, "phase_name": "Setup"},     // Should start at 0
  {"phase_number": 2, "phase_name": "Analysis"},
  {"phase_number": 4, "phase_name": "Generation"} // Skipped 3
]
```

### 2. Phase Count Consistency

**Rule:** `total_phases` MUST equal length of `phases` array

```json
// ✅ CORRECT
{
  "total_phases": 3,
  "phases": [
    {"phase_number": 0, ...},
    {"phase_number": 1, ...},
    {"phase_number": 2, ...}
  ]
}

// ❌ WRONG
{
  "total_phases": 5,    // Says 5 phases
  "phases": [
    {"phase_number": 0, ...},
    {"phase_number": 1, ...},
    {"phase_number": 2, ...}
  ]  // Only 3 phases defined
}
```

### 3. Duration Format

**Rule:** Use ranges with units for estimation

```json
// ✅ CORRECT
"estimated_duration": "2-3 hours"
"estimated_effort": "15-20 minutes"
"estimated_effort": "30-45 minutes"

// ❌ WRONG  
"estimated_duration": "long"
"estimated_effort": "quick"
"estimated_effort": "120"  // No units
```

### 4. Specific Deliverables

**Rule:** Deliverables should be concrete, not vague

```json
// ✅ CORRECT
"key_deliverables": [
  "Unit test files with 80% coverage",
  "Integration test suite",
  "Test documentation README"
]

// ❌ WRONG
"key_deliverables": [
  "Tests",
  "Documentation",
  "Some files"
]
```

### 5. Measurable Criteria

**Rule:** Validation criteria should be testable

```json
// ✅ CORRECT
"validation_criteria": [
  "All public functions have tests",
  "Test suite executes without errors",
  "Coverage ≥80%"
]

// ❌ WRONG
"validation_criteria": [
  "Tests are good",
  "Everything works",
  "Done properly"
]
```

---

## 🎨 Naming Conventions

### Workflow Type

**Format:** `{domain}_{action}_{version}`

```
Examples:
✅ test_generation_v3
✅ production_code_v2
✅ api_validation_v1
✅ security_review_v2

❌ TestGen3
❌ prod-code
❌ API_Validation
```

### Phase Names

**Format:** Action-oriented, capitalize first letter

```
Examples:
✅ Setup
✅ Analysis
✅ Code Generation
✅ Integration Testing
✅ Documentation & Finalization

❌ phase1
❌ ANALYSIS
❌ doing_tests
```

---

## 🔍 Searchability Standards

### Keywords to Include

Metadata should be written to match common queries:

```json
{
  "description": "Generate comprehensive test suites with automated validation gates for Python, TypeScript, and JavaScript projects",
  // Includes: generate, test, automated, validation, Python, TypeScript, JavaScript
  
  "phases": [
    {
      "phase_name": "Unit Test Generation",
      "purpose": "Create unit tests for all functions and classes with mocking and fixtures",
      // Includes: unit test, functions, classes, mocking, fixtures
    }
  ]
}
```

### Test Your Searchability

```python
# Queries that SHOULD find your workflow:
await search_standards("How do I generate tests for Python?")
await search_standards("What workflows create unit tests?")
await search_standards("Automated test generation with validation")

# If these don't return your workflow, improve keywords in description and purposes
```

---

## 📊 Example: Complete Metadata File

```json
{
  "workflow_type": "test_generation_v3",
  "version": "3.0.0",
  "description": "Generate comprehensive test suites with validation gates for Python, TypeScript, and JavaScript projects. Produces unit tests, integration tests, and validation tests with automated coverage reporting.",
  "total_phases": 8,
  "estimated_duration": "2-3 hours",
  "primary_outputs": [
    "Unit test files",
    "Integration test files",
    "Validation test files",
    "Coverage report (HTML and JSON)",
    "Test documentation README"
  ],
  "phases": [
    {
      "phase_number": 0,
      "phase_name": "Setup",
      "purpose": "Initialize test environment, install dependencies, and create directory structure",
      "estimated_effort": "10 minutes",
      "key_deliverables": [
        "Test framework configured (pytest/jest/mocha)",
        "All dependencies installed",
        "Test directory structure created"
      ],
      "validation_criteria": [
        "Test runner executes successfully",
        "All dependencies resolved without errors",
        "Directory structure follows conventions"
      ]
    },
    {
      "phase_number": 1,
      "phase_name": "Analysis",
      "purpose": "Analyze target code structure and determine comprehensive test strategy",
      "estimated_effort": "15-20 minutes",
      "key_deliverables": [
        "Complete code structure analysis",
        "Function and method inventory",
        "Test path determination (unit/integration/validation)",
        "Coverage goals defined"
      ],
      "validation_criteria": [
        "All public functions identified and catalogued",
        "Test types determined for each component",
        "Coverage goal set (minimum 80%)",
        "Complex functions flagged for extra test cases"
      ]
    }
    // ... more phases
  ]
}
```

---

## ⚠️ Common Mistakes

### Mistake 1: Incomplete Phase Definitions

```json
// ❌ WRONG
{
  "phase_number": 1,
  "phase_name": "Analysis"
  // Missing purpose, effort, deliverables, criteria
}

// ✅ CORRECT  
{
  "phase_number": 1,
  "phase_name": "Analysis",
  "purpose": "Analyze code structure and plan tests",
  "estimated_effort": "15-20 minutes",
  "key_deliverables": ["Code analysis", "Test plan"],
  "validation_criteria": ["All functions identified"]
}
```

### Mistake 2: Vague Descriptions

```json
// ❌ WRONG
{
  "description": "A workflow for tests",
  "purpose": "Do analysis"
}

// ✅ CORRECT
{
  "description": "Generate comprehensive test suites with automated validation gates",
  "purpose": "Analyze code structure, identify testable units, and create test strategy"
}
```

### Mistake 3: Missing Version

```json
// ❌ WRONG
{
  "workflow_type": "test_generation"
  // No version field
}

// ✅ CORRECT
{
  "workflow_type": "test_generation_v3",
  "version": "3.0.0"
}
```

---

## 🧪 Validation Checklist

Before committing metadata.json:

- [ ] All required fields present
- [ ] Phases numbered sequentially from 0
- [ ] `total_phases` matches `phases.length`
- [ ] All phases have all 6 required fields
- [ ] Duration estimates use ranges with units
- [ ] Deliverables are specific and concrete
- [ ] Validation criteria are measurable
- [ ] Description includes searchable keywords
- [ ] JSON is valid (no syntax errors)
- [ ] File is in correct location
- [ ] Workflow type follows naming convention

### Automated Validation

```python
import json
from pathlib import Path

def validate_workflow_metadata(metadata_path: Path) -> bool:
    """Validate workflow metadata file."""
    with open(metadata_path) as f:
        metadata = json.load(f)
    
    # Required root fields
    required_root = ["workflow_type", "version", "description", 
                     "total_phases", "estimated_duration", 
                     "primary_outputs", "phases"]
    for field in required_root:
        assert field in metadata, f"Missing required field: {field}"
    
    # Phase count consistency
    assert len(metadata["phases"]) == metadata["total_phases"], \
        "total_phases doesn't match phases array length"
    
    # Phase numbering
    for i, phase in enumerate(metadata["phases"]):
        assert phase["phase_number"] == i, \
            f"Phase {i} has wrong phase_number: {phase['phase_number']}"
    
    # Required phase fields
    required_phase = ["phase_number", "phase_name", "purpose",
                      "estimated_effort", "key_deliverables",
                      "validation_criteria"]
    for phase in metadata["phases"]:
        for field in required_phase:
            assert field in phase, \
                f"Phase {phase['phase_number']} missing field: {field}"
    
    return True
```

---

## 📚 Related Standards

- [Workflow System Overview](workflow-system-overview.md) - Complete workflow system
- [MCP RAG Configuration](mcp-rag-configuration.md) - How metadata is indexed
- [Workflow Metadata Guide](../../../mcp_server/WORKFLOW_METADATA_GUIDE.md) - Technical implementation

---

## 🔍 Querying This Document

```python
# Metadata creation questions
await search_standards("How do I create workflow metadata?")

# Schema questions
await search_standards("What fields are required in workflow metadata?")

# Quality standards
await search_standards("How should I write validation criteria?")
```

---

**Remember:** High-quality metadata enables effective AI discovery, planning, and execution. Follow these standards to ensure your workflows are discoverable and usable!

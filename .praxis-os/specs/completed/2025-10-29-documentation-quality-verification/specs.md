# Technical Specifications

**Project:** Documentation Quality Verification Initiative  
**Date:** 2025-10-29  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 Architectural Pattern: Layered Validation Pipeline

The system uses a **Layered Validation Pipeline** architecture with five defense-in-depth layers, each progressively more comprehensive but also progressively later in the development lifecycle. The architecture is optimized for the "shift left" principle: catch errors as early and cheaply as possible.

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEVELOPER WORKSTATION                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Layer 1: PRE-COMMIT HOOKS (Primary Defense - 95% catch rate)││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     ││
│  │  │ RST Syntax   │  │ Pydantic     │  │ Python Code  │     ││
│  │  │ Validator    │  │ Field        │  │ Syntax       │     ││
│  │  │              │  │ Validator    │  │ Validator    │     ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘     ││
│  │                                                              ││
│  │  Input: git diff --cached (changed RST files)               ││
│  │  Output: BLOCK commit if P0 issues | ALLOW if valid         ││
│  │  Speed: <5 seconds (critical for UX)                        ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Layer 2: LOCAL VALIDATION SCRIPTS (Developer Tools)        ││
│  │  ┌──────────────────────────────────────────────────────┐ ││
│  │  │ validate_all_examples.py  (comprehensive check)      │ ││
│  │  │ validate_config_fields.py  (Pydantic fields only)    │ ││
│  │  │ validate_imports.py        (import resolution)       │ ││
│  │  │ validate_rst_syntax.py     (RST structure)           │ ││
│  │  │ validate_changed_docs.py   (incremental check)       │ ││
│  │  └──────────────────────────────────────────────────────┘ ││
│  │                                                              ││
│  │  Optional: Run before commit for deep validation            ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

                            │ git push
                            ▼

┌─────────────────────────────────────────────────────────────────┐
│                       GITHUB CI/CD                               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Layer 3: GITHUB ACTIONS (Backup Defense - 4% catch rate)   ││
│  │  ┌──────────────────────────────────────────────────────┐ ││
│  │  │ Re-run all pre-commit validations                    │ ││
│  │  │ + Cross-file consistency checks                      │ ││
│  │  │ + Link validation (internal + external)             │ ││
│  │  │ + Full Sphinx build (treat warnings as errors)       │ ││
│  │  │ + Pytest test suite (tests/documentation/)           │ ││
│  │  └──────────────────────────────────────────────────────┘ ││
│  │                                                              ││
│  │  Trigger: Pull Request                                       ││
│  │  Output: Block PR merge if P0 issues | Quality report        ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

                            │ merge to main
                            ▼

┌─────────────────────────────────────────────────────────────────┐
│                     MAIN BRANCH (POST-MERGE)                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Layer 4: POST-MERGE VALIDATION (Last Resort - 1% catch)    ││
│  │  ┌──────────────────────────────────────────────────────┐ ││
│  │  │ Full validation + metrics collection                 │ ││
│  │  │ Alert if issues found (indicates pre-commit bypass)  │ ││
│  │  │ Generate quality trend reports                       │ ││
│  │  └──────────────────────────────────────────────────────┘ ││
│  │                                                              ││
│  │  Purpose: Catch edge cases, track metrics                    ││
│  │  Should: Almost never find issues (success indicator)        ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

                            │ deploy docs
                            ▼

┌─────────────────────────────────────────────────────────────────┐
│                  PRODUCTION (USER-FACING)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Layer 5: USER DISCOVERY (<0.1% escape rate - FAILURE)      ││
│  │                                                              ││
│  │  If a user discovers a documentation error, the entire      ││
│  │  defense-in-depth system has failed. This should be         ││
│  │  statistically near-impossible.                              ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Architectural Decisions

#### Decision 1: Pre-commit Hooks as Primary Defense

**Decision:** Use pre-commit hooks as the PRIMARY validation mechanism, with all other layers serving as backup.

**Rationale:**
- **Cost optimization**: Fixes at commit time cost $1 vs $1000 at production discovery (1000x ROI)
- **Speed optimization**: Fixes in seconds at commit vs days at production
- **Developer experience**: Immediate feedback in local environment, no workflow disruption
- **Prevention over detection**: Impossible to commit bad docs vs catching them later

**Alternatives Considered:**
- **CI/CD only**: Cost $10 per fix (10x more expensive), slower feedback (minutes vs seconds), workflow disruption
- **Post-merge validation**: Cost $100 per fix (100x more expensive), impacts entire team
- **Manual review**: Human error-prone, doesn't scale, slow

**Trade-offs:**
- **Pros:** 95% error catch rate at lowest cost point, immediate feedback, prevents errors from entering git history
- **Cons:** Requires developer setup (one-time `pre-commit install`), could slow commits if validation is slow (mitigated by <5s performance requirement)

#### Decision 2: Dynamic Source of Truth Pattern

**Decision:** All validators MUST dynamically read model definitions from source code at runtime (no hardcoded field lists).

**Rationale:**
- **Root cause fix**: SessionConfig bug was caused by documentation drift from source code
- **Maintenance**: Zero-maintenance validation - automatically stays current as SDK evolves
- **Reliability**: Single source of truth (source code) prevents documentation-validator drift

**Alternatives Considered:**
- **Hardcoded field lists**: Would require manual updates, prone to same drift problem we're solving
- **Separate schema files**: Extra maintenance burden, another drift point

**Trade-offs:**
- **Pros:** Zero-maintenance, impossible for validators to drift from SDK, catches schema changes immediately
- **Cons:** Slight performance overhead (import models at validation time), validators depend on SDK being importable

#### Decision 3: Fail-Fast Validation

**Decision:** Validation stops on first P0 (critical) error and reports immediately.

**Rationale:**
- **Developer experience**: Fast feedback (don't wait for full scan if first file has error)
- **Iterative fixing**: Fix one error, re-run, fix next (natural workflow)
- **Performance**: Minimal time spent on broken commits

**Alternatives Considered:**
- **Collect all errors first**: Slower, overwhelming error lists
- **Continue despite errors**: Wastes time validating files that won't be committed anyway

**Trade-offs:**
- **Pros:** Fast feedback, focused fixes, minimal wasted work
- **Cons:** Developers may need multiple commit attempts (acceptable - errors should be rare with pre-commit)

#### Decision 4: Modular Validator Architecture

**Decision:** Separate validators for each concern (RST syntax, Pydantic fields, imports, code syntax), composable via orchestrator.

**Rationale:**
- **Single Responsibility Principle**: Each validator has one job
- **Testability**: Easy to test each validator independently
- **Extensibility**: Easy to add new validators (e.g., API signature validator)
- **Reusability**: Local scripts, pre-commit, CI/CD all use same validators

**Alternatives Considered:**
- **Monolithic validator**: Harder to test, maintain, extend
- **Sphinx-only validation**: Too late (build-time), doesn't catch all error types

**Trade-offs:**
- **Pros:** Clean separation, testable, maintainable, reusable
- **Cons:** More files to manage (mitigated by clear structure)

### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-1 (Code Validation) | CodeExampleValidator module | Extracts Python code blocks, validates with ast.parse(), sandboxed execution |
| FR-2 (Pydantic Fields) | PydanticFieldValidator module | Dynamically loads models from source, compares doc usage to model.model_fields |
| FR-3 (Imports) | ImportValidator module | Extracts imports, attempts resolution in clean environment |
| FR-4 (API Signatures) | SignatureValidator module (Phase 2) | Introspects SDK functions, compares to documented usage |
| FR-5 (Pre-commit Blocking) | .pre-commit-config.yaml + validate_changed_docs.py | Git hook calls validator, exits 1 to block commit |
| FR-6 (Incremental) | validate_changed_docs.py | Uses git diff --cached to identify changed files only |
| FR-7 (Local Scripts) | docs/utils/ directory with 5 scripts | On-demand validation for developers |
| FR-8 (CI/CD) | .github/workflows/documentation-quality.yml | GitHub Actions workflow, runs on PR |
| FR-9 (Post-merge) | .github/workflows/post-merge-validation.yml | GitHub Actions on main branch |
| FR-10 (Issue Reports) | IssueReporter module | Structured output to discovered-issues.md |
| FR-11 (Correction Workflow) | CorrectionOrchestrator module | Priority-driven fix loop with re-validation |
| NFR-1 (Speed <5s) | Incremental validation + caching | Only validate changed files, cache AST/model schema |
| NFR-2 (Full <2min) | Parallel processing | Multiprocessing for independent file validation |
| NFR-4 (False positives <5%) | High-confidence checks first | Start with syntax/import checks, iterate based on results |
| NFR-5 (Escape rate <0.1%) | Defense in depth (5 layers) | 95% + 4% + 1% = >99.9% catch rate |
| NFR-6 (Clear errors) | Structured error format | File, line, error, suggestion in every message |
| NFR-8 (Source of truth) | Dynamic model loading | Import TracerConfig/SessionConfig at runtime |
| NFR-10 (Safe execution) | Sandboxed environment | restricted exec with no network/filesystem access |

### 1.4 Technology Stack

**Validation Scripts (Python 3.11+):**
- `ast` module: Python syntax validation
- `pydantic`: Model field introspection (`model.model_fields`)
- `importlib`: Dynamic import testing
- `inspect`: Function signature introspection
- `re`: Regular expressions for RST parsing
- `multiprocessing`: Parallel validation for performance

**Pre-commit Hooks:**
- `pre-commit` framework (v3.x): Industry-standard git hook manager
- `.pre-commit-config.yaml`: Hook configuration

**CI/CD:**
- GitHub Actions: Workflow automation
- `pytest` (v7.x): Test framework for validation test suite
- `pytest-cov`: Test coverage measurement
- `sphinx` (v7.x): Documentation build system

**Development Tools:**
- `ruff`: Fast Python linter (for validator code quality)
- `mypy`: Type checking (for validator code)
- `black`: Code formatting (for validator code)

**Infrastructure:**
- Git: Version control, hooks interface
- GitHub: CI/CD platform, PR gating

### 1.5 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ REPOSITORY ROOT                                                  │
│                                                                  │
│  .pre-commit-config.yaml ───────────────┐                       │
│                                          │                       │
│  docs/                                   │                       │
│  ├── *.rst (documentation files)        │                       │
│  └── utils/ (validation scripts)        │                       │
│      ├── validate_all_examples.py ◄─────┼───────┐              │
│      ├── validate_config_fields.py ◄────┤       │              │
│      ├── validate_imports.py ◄──────────┤       │              │
│      ├── validate_rst_syntax.py ◄───────┤       │              │
│      ├── validate_changed_docs.py ◄─────┘       │              │
│      └── validators/ (shared modules)            │              │
│          ├── code_validator.py                   │              │
│          ├── pydantic_validator.py               │              │
│          ├── import_validator.py                 │              │
│          ├── rst_validator.py                    │              │
│          └── issue_reporter.py                   │              │
│                                                   │              │
│  tests/documentation/                            │              │
│  ├── test_doc_examples.py ◄─────────────────────┤              │
│  ├── test_config_examples.py ◄──────────────────┤              │
│  ├── test_imports.py ◄──────────────────────────┤              │
│  └── test_full_build.py ◄───────────────────────┤              │
│                                                   │              │
│  .github/workflows/                              │              │
│  ├── documentation-quality.yml ◄─────────────────┤              │
│  └── post-merge-validation.yml ◄─────────────────┘              │
│                                                                  │
│  src/honeyhive/config/models/                                   │
│  └── tracer.py (source of truth for Pydantic models)            │
│      ├── TracerConfig                                           │
│      ├── SessionConfig                                          │
│      └── EvaluationConfig                                       │
└─────────────────────────────────────────────────────────────────┘

INSTALLATION:
1. Developer runs: pre-commit install (one-time setup)
2. Git automatically runs hooks on commit
3. CI/CD workflows automatically trigger on PR/push
```

**Key Deployment Characteristics:**
- **Zero external dependencies**: All validators run in-repo, no external services
- **Developer-friendly**: One command install (`pre-commit install`)
- **CI-ready**: GitHub Actions workflows committed to repo
- **Portable**: Works on any platform with Python 3.11+ and Git

---

## 2. Component Design

### 2.1 Core Validator Modules

#### Component: CodeExampleValidator
**Purpose:** Extract and validate Python code blocks from RST files

**Responsibilities:**
- Parse RST files for `.. code-block:: python` directives
- Extract code content from indented blocks
- Validate syntax using `ast.parse()`
- Execute code in sandboxed environment (optional, for runtime validation)
- Report syntax errors with file name and line number

**Interface:**
```python
class CodeExampleValidator:
    def extract_code_blocks(self, rst_content: str) -> List[CodeBlock]:
        """Extract all Python code blocks from RST content."""
        
    def validate_syntax(self, code_block: CodeBlock) -> Optional[ValidationError]:
        """Validate code block syntax using ast.parse()."""
        
    def execute_safe(self, code_block: CodeBlock) -> Optional[RuntimeError]:
        """Execute code in sandboxed environment (restricted globals/locals)."""
```

**Dependencies:**
- `ast` (stdlib): Syntax validation
- `re` (stdlib): RST parsing
- Custom `CodeBlock` dataclass

**Error Handling:**
- Syntax errors → ValidationError with line number and error message
- Runtime errors → RuntimeError with exception details
- Malformed RST → Parse warning, skip block

---

#### Component: PydanticFieldValidator
**Purpose:** Validate Pydantic model field usage in documentation

**Responsibilities:**
- Dynamically import Pydantic models from `src/honeyhive/config/models/tracer.py`
- Extract field names from model usage in RST (e.g., `TracerConfig(session_name=...)`)
- Compare extracted fields to `model.model_fields`
- Suggest correct model if field belongs to different model
- Report invalid fields with suggestions

**Interface:**
```python
class PydanticFieldValidator:
    def __init__(self):
        self.models = self._load_models()  # TracerConfig, SessionConfig, EvaluationConfig
        
    def _load_models(self) -> Dict[str, Type[BaseModel]]:
        """Dynamically import models from source code."""
        
    def extract_model_usage(self, rst_content: str) -> List[ModelUsage]:
        """Extract TracerConfig/SessionConfig/EvaluationConfig usage."""
        
    def validate_fields(self, model_usage: ModelUsage) -> List[ValidationError]:
        """Check if fields exist in model.model_fields."""
        
    def suggest_correct_model(self, field_name: str, used_model: str) -> Optional[str]:
        """If field exists in different model, suggest it."""
```

**Key Algorithm:**
```python
# Critical: Dynamic loading prevents validator drift
from honeyhive.config.models.tracer import TracerConfig, SessionConfig, EvaluationConfig

valid_fields = set(SessionConfig.model_fields.keys())
# Result: {"session_id", "inputs", "link_carrier"} - directly from source code!

if "session_name" in documentation_example and "session_name" not in valid_fields:
    # Check if it's in a different model
    for model_name, model_class in models.items():
        if "session_name" in model_class.model_fields:
            return f"Field 'session_name' is not valid for SessionConfig. Did you mean to use {model_name}?"
```

**Dependencies:**
- `pydantic`: Model introspection
- `importlib`: Dynamic model loading
- `re`: Field extraction from RST

---

#### Component: ImportValidator
**Purpose:** Validate that import statements in documentation resolve successfully

**Responsibilities:**
- Extract all `import` and `from ... import` statements from RST
- Attempt imports in clean environment
- Report ImportError with suggestions
- Verify imports match current SDK structure

**Interface:**
```python
class ImportValidator:
    def extract_imports(self, rst_content: str) -> List[ImportStatement]:
        """Extract import statements from code blocks."""
        
    def validate_import(self, import_stmt: ImportStatement) -> Optional[ValidationError]:
        """Attempt import, catch ImportError."""
        
    def suggest_fix(self, failed_import: str) -> Optional[str]:
        """Suggest correct import path if module was moved."""
```

**Dependencies:**
- `importlib`: Dynamic import testing
- `sys`: Module path management

---

#### Component: RSTSyntaxValidator
**Purpose:** Validate RST structure and formatting

**Responsibilities:**
- Validate title underline lengths match title lengths
- Check consistent hierarchy (===, ---, ~~~, ^^^, """)
- Verify code block directives are properly formatted
- Check list formatting (proper markers)

**Interface:**
```python
class RSTSyntaxValidator:
    def validate_title_underlines(self, rst_file: Path) -> List[ValidationError]:
        """Check all title underlines match title length."""
        
    def validate_hierarchy(self, rst_file: Path) -> List[ValidationError]:
        """Verify consistent section hierarchy."""
        
    def validate_code_blocks(self, rst_file: Path) -> List[ValidationError]:
        """Check code block directive syntax."""
```

**Key Algorithm:**
```python
lines = rst_content.split('\n')
underline_chars = {'=', '-', '~', '^', '"'}

for i, line in enumerate(lines):
    if i > 0 and is_underline(line):
        title = lines[i-1].strip()
        underline = line.strip()
        
        if len(title) != len(underline):
            errors.append(ValidationError(
                line=i+1,
                message=f"Title underline mismatch: title={len(title)} chars, underline={len(underline)} chars",
                suggestion=f"Use: {underline[0] * len(title)}"
            ))
```

---

#### Component: IssueReporter
**Purpose:** Generate structured issue reports with prioritization

**Responsibilities:**
- Collect validation errors from all validators
- Categorize by type (syntax, Pydantic, import, RST structure)
- Prioritize by severity (P0-P3)
- Format output as Markdown (`discovered-issues.md`)
- Generate statistics

**Interface:**
```python
class IssueReporter:
    def add_issue(self, issue: ValidationError):
        """Add issue to report."""
        
    def categorize(self) -> Dict[str, List[ValidationError]]:
        """Group issues by category."""
        
    def prioritize(self) -> Dict[str, List[ValidationError]]:
        """Group issues by priority (P0-P3)."""
        
    def generate_report(self, output_path: Path):
        """Write discovered-issues.md."""
```

**Output Format:**
```markdown
# Documentation Issues Discovered

**Date:** 2025-10-29
**Files Scanned:** 43
**Total Issues:** 5

## P0 (Critical - Causes Execution Errors)

### docs/tutorials/advanced-configuration.rst

**Line 286:** Invalid field 'session_name' for SessionConfig
- **Category:** Pydantic field error
- **Suggestion:** Field 'session_name' belongs to TracerConfig, not SessionConfig. Update to:
  ```python
  tracer_config = TracerConfig(session_name="...")
  session_config = SessionConfig(inputs={...})
  ```
```

---

### 2.2 Orchestration Components

#### Component: ValidationOrchestrator
**Purpose:** Coordinate multiple validators and aggregate results

**Responsibilities:**
- Run validators in sequence (or parallel for independent files)
- Collect results from all validators
- Implement fail-fast for P0 errors (if configured)
- Pass results to IssueReporter

**Interface:**
```python
class ValidationOrchestrator:
    def __init__(self, validators: List[Validator]):
        self.validators = validators
        
    def validate_file(self, rst_file: Path) -> List[ValidationError]:
        """Run all validators on single file."""
        
    def validate_files(self, rst_files: List[Path], parallel: bool = True) -> List[ValidationError]:
        """Run validators on multiple files (optionally in parallel)."""
```

---

#### Component: PreCommitHook
**Purpose:** Git hook integration for pre-commit validation

**Responsibilities:**
- Detect changed RST files using `git diff --cached`
- Call ValidationOrchestrator on changed files only
- Exit with code 1 (block commit) if P0 issues found
- Exit with code 0 (allow commit) if validation passes
- Print clear error messages with file/line/suggestion

**Interface:**
```bash
# Called by .pre-commit-config.yaml
python docs/utils/validate_changed_docs.py

# Exit codes:
# 0 = validation passed, allow commit
# 1 = validation failed, block commit
```

**Implementation:**
```python
def main() -> int:
    changed_files = get_changed_rst_files()  # git diff --cached
    
    if not changed_files:
        return 0  # No RST files changed
        
    orchestrator = ValidationOrchestrator(validators=[
        RSTSyntaxValidator(),
        CodeExampleValidator(),
        PydanticFieldValidator(),
        ImportValidator()
    ])
    
    issues = orchestrator.validate_files(changed_files)
    p0_issues = [i for i in issues if i.priority == "P0"]
    
    if p0_issues:
        print_errors(p0_issues)
        return 1  # Block commit
    
    return 0  # Allow commit
```

---

### 2.3 Component Interaction Diagram

```
Developer commits code
       │
       ▼
┌─────────────────┐
│ Git Pre-commit  │
│ Hook            │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ PreCommitHook Component │
│ (validate_changed_docs) │
└────────┬────────────────┘
         │
         │ Get changed RST files
         │ via git diff --cached
         │
         ▼
┌───────────────────────────┐
│ ValidationOrchestrator    │
└────────┬──────────────────┘
         │
         │ For each file, run:
         ├────────────────────────┐
         │                        │
         ▼                        ▼
┌──────────────────┐    ┌──────────────────────┐
│ RSTSyntaxValidator│    │ CodeExampleValidator │
└────────┬──────────┘    └───────┬──────────────┘
         │                       │
         ▼                       ▼
┌──────────────────────┐  ┌────────────────────┐
│ PydanticFieldValidator│ │ ImportValidator    │
└────────┬──────────────┘ └──────┬─────────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ IssueReporter   │
            └────────┬─────────┘
                     │
                     ▼
              Print errors to terminal
              Return exit code (0/1)
```

---

## 3. API Contracts

### 3.1 Internal APIs (Validator Interface)

**BaseValidator Protocol:**
All validators implement this interface for composability:

```python
from typing import Protocol, List
from pathlib import Path

class Validator(Protocol):
    """Protocol that all validators must implement."""
    
    def validate(self, rst_file: Path) -> List[ValidationError]:
        """
        Validate a single RST file.
        
        Args:
            rst_file: Path to RST file to validate
            
        Returns:
            List of ValidationError objects (empty list if valid)
            
        Raises:
            FileNotFoundError: If rst_file doesn't exist
            ValidationException: If validation itself fails (not the content)
        """
        ...
```

**ValidationError Data Model:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ValidationError:
    """Structured validation error."""
    file: Path
    line_number: int
    priority: str  # "P0" | "P1" | "P2" | "P3"
    category: str  # "syntax" | "pydantic_field" | "import" | "rst_structure"
    error_message: str
    suggestion: Optional[str] = None
    code_context: Optional[str] = None
    
    def __str__(self) -> str:
        """Format for terminal output."""
        return f"{self.file}:{self.line_number}: [{self.priority}] {self.error_message}\n  Suggestion: {self.suggestion}"
```

### 3.2 CLI Interface

**validate_changed_docs.py** (Pre-commit hook script):
```bash
# Usage
python docs/utils/validate_changed_docs.py [--verbose] [--fail-fast]

# Flags
--verbose: Print detailed validation progress
--fail-fast: Stop on first P0 error (default: True)

# Exit codes
0: Validation passed
1: Validation failed (P0 errors found)
```

**validate_all_examples.py** (Comprehensive validation):
```bash
# Usage
python docs/utils/validate_all_examples.py [--fix] [--report OUTPUT]

# Flags
--fix: Attempt to auto-fix simple issues (e.g., title underlines)
--report: Output path for discovered-issues.md (default: ./discovered-issues.md)

# Exit codes
0: No issues found
1: Issues found (see report)
```

### 3.3 GitHub Actions Integration API

**Workflow Inputs:**
```yaml
# .github/workflows/documentation-quality.yml
on:
  pull_request:
    paths:
      - 'docs/**/*.rst'

inputs:
  fail-on-warning:
    description: 'Treat warnings as errors'
    required: false
    default: 'true'
```

**Workflow Outputs:**
- PR comment with quality report
- Workflow status (pass/fail)
- Artifact: `discovered-issues.md` (if issues found)

---

## 4. Data Models

### 4.1 Configuration Models (Input)

**Pre-commit Configuration** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: local
    hooks:
      - id: validate-doc-syntax
        name: Validate Python Code in Docs
        entry: python docs/utils/validate_changed_docs.py
        language: system
        files: \.rst$
        pass_filenames: true
        fail_fast: true
        verbose: false
```

### 4.2 Runtime Data Models

**CodeBlock:**
```python
@dataclass
class CodeBlock:
    """Represents a Python code block extracted from RST."""
    file: Path
    start_line: int
    end_line: int
    code: str
    language: str  # "python" | "bash" | etc.
```

**ModelUsage:**
```python
@dataclass
class ModelUsage:
    """Represents Pydantic model usage in documentation."""
    file: Path
    line_number: int
    model_name: str  # "TracerConfig" | "SessionConfig" | "EvaluationConfig"
    fields: List[str]  # Field names used in example
    code_context: str  # Surrounding code for context
```

**ImportStatement:**
```python
@dataclass
class ImportStatement:
    """Represents an import statement from documentation."""
    file: Path
    line_number: int
    import_type: str  # "import" | "from_import"
    module: str
    names: List[str]  # For "from X import A, B"
    code: str  # Original import line
```

### 4.3 Output Data Models

**IssueReport:**
```python
@dataclass
class IssueReport:
    """Aggregated validation report."""
    date: str
    files_scanned: int
    total_issues: int
    issues_by_priority: Dict[str, List[ValidationError]]
    issues_by_category: Dict[str, List[ValidationError]]
    
    def to_markdown(self) -> str:
        """Generate discovered-issues.md content."""
```

---

## 5. Security Design

### 5.1 Code Execution Sandbox

**Threat:** Malicious or buggy code in documentation could harm validator environment.

**Mitigation:**
```python
# Sandboxed execution with restricted globals/locals
def execute_safe(code: str) -> Optional[Exception]:
    """Execute code in sandboxed environment."""
    
    # Restricted globals - no dangerous builtins
    safe_globals = {
        '__builtins__': {
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            # ... safe builtins only
        }
    }
    
    # Empty locals
    safe_locals = {}
    
    try:
        exec(code, safe_globals, safe_locals)
        return None
    except Exception as e:
        return e
```

**Additional Protections:**
- No network access (no `socket`, `urllib`, `requests`)
- No filesystem access (no `open`, `os`, `pathlib` write operations)
- Timeout enforcement (kill execution after 5 seconds)

### 5.2 Input Validation

**RST Content:**
- Treat all RST content as untrusted input
- Parse defensively (catch malformed RST gracefully)
- No `eval()` or `exec()` on RST content directly

**Model Loading:**
- Only import from known, controlled paths (`src/honeyhive/config/models/`)
- Validate module paths before import

### 5.3 Secret Protection

**Documentation Examples:**
- Validators should flag hardcoded API keys/secrets in examples
- Pattern: `api_key="hh_[a-f0-9]{16}"` → should use environment variables
- Warning (not blocking): "Example contains hardcoded API key. Use environment variable."

---

## 6. Performance Design

### 6.1 Performance Requirements (Recap from NFRs)

- **Pre-commit**: <5 seconds for typical commit (1-3 RST files)
- **Full validation**: <2 minutes for entire docs directory (~100 RST files)
- **CI/CD**: <5 minutes total (including validation + Sphinx build + tests)

### 6.2 Performance Optimization Strategies

#### Strategy 1: Incremental Validation

**Implementation:**
```python
# Only validate changed files, not entire docs directory
def get_changed_rst_files() -> List[Path]:
    """Use git to identify changed RST files."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )
    files = [Path(f) for f in result.stdout.strip().split('\n') if f.endswith('.rst')]
    return files
```

**Benefit:**
- Typical commit: 1-3 files → <5s validation
- Full repo: 100 files → would take 2min, but pre-commit only validates changed files

#### Strategy 2: Parallel File Validation

**Implementation:**
```python
from multiprocessing import Pool

def validate_files_parallel(files: List[Path]) -> List[ValidationError]:
    """Validate files in parallel using multiprocessing."""
    with Pool(processes=min(8, len(files))) as pool:
        results = pool.map(validate_single_file, files)
    
    # Flatten results
    return [error for file_errors in results for error in file_errors]
```

**Benefit:**
- 8-core machine: 8x speedup for independent file validation
- Full validation: 100 files → ~15 seconds instead of 2 minutes

#### Strategy 3: Caching

**Implementation:**
```python
import functools
from datetime import datetime, timedelta

@functools.lru_cache(maxsize=128)
def load_pydantic_models() -> Dict[str, Type[BaseModel]]:
    """Load Pydantic models once, cache result."""
    from honeyhive.config.models.tracer import TracerConfig, SessionConfig, EvaluationConfig
    return {
        "TracerConfig": TracerConfig,
        "SessionConfig": SessionConfig,
        "EvaluationConfig": EvaluationConfig
    }
```

**Benefit:**
- Models loaded once per validation run, not per file
- AST trees cached per file (if file unchanged)

#### Strategy 4: Fail-Fast for P0 Errors

**Implementation:**
```python
def validate_with_fail_fast(files: List[Path]) -> List[ValidationError]:
    """Stop validation on first P0 error."""
    for file in files:
        errors = validate_file(file)
        p0_errors = [e for e in errors if e.priority == "P0"]
        if p0_errors:
            return p0_errors  # Stop immediately, return only P0 errors
    return []  # No P0 errors found
```

**Benefit:**
- Developer gets immediate feedback on first broken file
- Don't waste time validating files that won't be committed

### 6.3 Performance Monitoring

**Instrumentation:**
```python
import time

def validate_with_timing(files: List[Path]) -> Tuple[List[ValidationError], float]:
    """Validate files and measure duration."""
    start = time.time()
    errors = validate_files(files)
    duration = time.time() - start
    
    # Log performance metrics
    logger.info(f"Validated {len(files)} files in {duration:.2f}s")
    
    return errors, duration
```

**Performance Regression Testing:**
```python
# tests/documentation/test_performance.py
def test_pre_commit_performance():
    """Ensure pre-commit validation completes in <5s."""
    files = [Path("docs/tutorials/advanced-configuration.rst")]  # Typical size
    
    start = time.time()
    validate_files(files)
    duration = time.time() - start
    
    assert duration < 5.0, f"Pre-commit validation too slow: {duration:.2f}s"
```

---



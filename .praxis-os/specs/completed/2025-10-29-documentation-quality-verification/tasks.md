# Implementation Tasks

**Project:** Documentation Quality Verification Initiative  
**Date:** 2025-10-29  
**Based on:** srd.md (requirements) + specs.md (technical design)

---

## Implementation Phases

This initiative follows the three-phased execution model defined in the DESIGN.md:

1. **Phase 1: Automated Discovery** (Day 1, 4-6 hours) - Build validation tools and discover issues
2. **Phase 2: Systematic Correction** (Day 2, 8-12 hours) - Fix discovered issues in priority order
3. **Phase 3: Prevention Mechanisms** (Day 3, 4-6 hours) - Install pre-commit hooks and CI/CD

---

## Phase 1: Automated Discovery

**Goal:** Build validation tooling and discover all documentation issues  
**Duration:** 4-6 hours  
**Success Criteria:** All validators implemented, `discovered-issues.md` generated with categorized issues

### Task 1.1: Project Structure Setup
**Estimated Time:** 15 minutes  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Create `docs/utils/` directory for validation scripts
- [ ] Create `docs/utils/validators/` directory for shared modules
- [ ] Create `tests/documentation/` directory for test suite
- [ ] Create `.github/workflows/` directory (if not exists)
- [ ] Add `__init__.py` files for Python package structure

**Dependencies:** None

**Validation:**
```bash
# Directory structure created
ls -la docs/utils/
ls -la docs/utils/validators/
ls -la tests/documentation/
```

---

### Task 1.2: Implement ValidationError Data Model
**Estimated Time:** 20 minutes  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Create `docs/utils/validators/models.py`
- [ ] Implement `ValidationError` dataclass with all required fields
- [ ] Implement `CodeBlock` dataclass
- [ ] Implement `ModelUsage` dataclass
- [ ] Implement `ImportStatement` dataclass
- [ ] Add `__str__` methods for terminal-friendly output

**Dependencies:** Task 1.1

**Implementation Pattern:**
```python
# docs/utils/validators/models.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

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
        return f"{self.file}:{self.line_number}: [{self.priority}] {self.error_message}\n  Suggestion: {self.suggestion}"
```

**Validation:**
```python
# Test instantiation
error = ValidationError(
    file=Path("test.rst"),
    line_number=42,
    priority="P0",
    category="pydantic_field",
    error_message="Invalid field",
    suggestion="Use field_x instead"
)
print(error)  # Should format correctly
```

---

### Task 1.3: Implement RSTSyntaxValidator
**Estimated Time:** 45 minutes  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Create `docs/utils/validators/rst_validator.py`
- [ ] Implement `RSTSyntaxValidator` class
- [ ] Implement `validate_title_underlines()` method
- [ ] Implement `validate_hierarchy()` method
- [ ] Implement `validate_code_blocks()` method
- [ ] Handle edge cases (empty files, malformed RST)
- [ ] Return List[ValidationError]

**Dependencies:** Task 1.2

**Key Algorithm:**
```python
def validate_title_underlines(self, rst_file: Path) -> List[ValidationError]:
    """Check all title underlines match title length."""
    errors = []
    content = rst_file.read_text()
    lines = content.split('\n')
    
    underline_chars = {'=', '-', '~', '^', '"'}
    
    for i, line in enumerate(lines):
        if i > 0 and line.strip() and len(set(line.strip())) == 1:
            if line.strip()[0] in underline_chars:
                title = lines[i-1].strip()
                underline = line.strip()
                
                if len(title) != len(underline):
                    errors.append(ValidationError(
                        file=rst_file,
                        line_number=i+1,
                        priority="P0",
                        category="rst_structure",
                        error_message=f"Title underline mismatch: title={len(title)} chars, underline={len(underline)} chars",
                        suggestion=f"Use: {underline[0] * len(title)}"
                    ))
    
    return errors
```

**Validation:**
```bash
# Test on known-bad file
python -c "from docs.utils.validators.rst_validator import RSTSyntaxValidator; v = RSTSyntaxValidator(); print(v.validate_title_underlines(Path('test_bad_underline.rst')))"
```

---

### Task 1.4: Implement CodeExampleValidator
**Estimated Time:** 60 minutes  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Create `docs/utils/validators/code_validator.py`
- [ ] Implement `CodeExampleValidator` class
- [ ] Implement `extract_code_blocks()` method (parse RST for `.. code-block:: python`)
- [ ] Implement `validate_syntax()` method (use `ast.parse()`)
- [ ] Implement `execute_safe()` method (sandboxed execution - optional)
- [ ] Handle syntax errors gracefully
- [ ] Return List[ValidationError]

**Dependencies:** Task 1.2

**Key Algorithm:**
```python
import ast
import re
from pathlib import Path

def extract_code_blocks(self, rst_content: str) -> List[CodeBlock]:
    """Extract Python code blocks from RST content."""
    blocks = []
    lines = rst_content.split('\n')
    
    i = 0
    while i < len(lines):
        if '.. code-block:: python' in lines[i]:
            start_line = i + 1
            i += 1
            
            # Skip blank lines after directive
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            # Collect indented code
            code_lines = []
            indent = len(lines[i]) - len(lines[i].lstrip()) if i < len(lines) else 0
            
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith(' ' * indent)):
                code_lines.append(lines[i][indent:])
                i += 1
            
            blocks.append(CodeBlock(
                file=Path(rst_file),
                start_line=start_line,
                end_line=i,
                code='\n'.join(code_lines),
                language="python"
            ))
        else:
            i += 1
    
    return blocks

def validate_syntax(self, code_block: CodeBlock) -> Optional[ValidationError]:
    """Validate code block syntax using ast.parse()."""
    try:
        ast.parse(code_block.code)
        return None
    except SyntaxError as e:
        return ValidationError(
            file=code_block.file,
            line_number=code_block.start_line + (e.lineno or 1),
            priority="P0",
            category="syntax",
            error_message=f"Python syntax error: {e.msg}",
            suggestion="Fix syntax error in code example"
        )
```

**Validation:**
```bash
# Test on file with known syntax error
python -m docs.utils.validators.code_validator test_syntax_error.rst
```

---

### Task 1.5: Implement PydanticFieldValidator
**Estimated Time:** 90 minutes  
**Priority:** P0 (CRITICAL - prevents SessionConfig-like bugs)

**Acceptance Criteria:**
- [ ] Create `docs/utils/validators/pydantic_validator.py`
- [ ] Implement `PydanticFieldValidator` class
- [ ] Implement `_load_models()` method (dynamically import TracerConfig, SessionConfig, EvaluationConfig)
- [ ] Implement `extract_model_usage()` method (parse RST for model instantiation)
- [ ] Implement `validate_fields()` method (compare to `model.model_fields`)
- [ ] Implement `suggest_correct_model()` method (suggest if field exists in different model)
- [ ] Handle import errors gracefully
- [ ] Return List[ValidationError]

**Dependencies:** Task 1.2

**Key Algorithm:**
```python
from typing import Dict, Type
from pydantic import BaseModel
import re

class PydanticFieldValidator:
    def __init__(self):
        self.models = self._load_models()
        
    def _load_models(self) -> Dict[str, Type[BaseModel]]:
        """Dynamically import models from source code (source of truth)."""
        from honeyhive.config.models.tracer import TracerConfig, SessionConfig, EvaluationConfig
        return {
            "TracerConfig": TracerConfig,
            "SessionConfig": SessionConfig,
            "EvaluationConfig": EvaluationConfig
        }
    
    def extract_model_usage(self, rst_content: str) -> List[ModelUsage]:
        """Extract TracerConfig/SessionConfig/EvaluationConfig usage."""
        usages = []
        pattern = r'(TracerConfig|SessionConfig|EvaluationConfig)\((.*?)\)'
        matches = re.findall(pattern, rst_content, re.DOTALL)
        
        for model_name, fields_str in matches:
            # Parse field names from "field1=value1, field2=value2"
            field_pattern = r'(\w+)='
            fields = re.findall(field_pattern, fields_str)
            usages.append(ModelUsage(
                model_name=model_name,
                fields=fields,
                code_context=f"{model_name}({fields_str[:50]}...)"
            ))
        
        return usages
    
    def validate_fields(self, model_usage: ModelUsage) -> List[ValidationError]:
        """Check if fields exist in model.model_fields."""
        errors = []
        model_class = self.models[model_usage.model_name]
        valid_fields = set(model_class.model_fields.keys())
        
        for field in model_usage.fields:
            if field not in valid_fields:
                # Check if it's in a different model
                suggestion = self.suggest_correct_model(field, model_usage.model_name)
                
                errors.append(ValidationError(
                    file=model_usage.file,
                    line_number=model_usage.line_number,
                    priority="P0",
                    category="pydantic_field",
                    error_message=f"Invalid field '{field}' for {model_usage.model_name}",
                    suggestion=suggestion
                ))
        
        return errors
    
    def suggest_correct_model(self, field_name: str, used_model: str) -> Optional[str]:
        """If field exists in different model, suggest it."""
        for model_name, model_class in self.models.items():
            if model_name != used_model and field_name in model_class.model_fields:
                return f"Field '{field_name}' belongs to {model_name}, not {used_model}. Did you mean to use {model_name}?"
        
        # List valid fields if no suggestion
        model_class = self.models[used_model]
        valid_fields = ', '.join(model_class.model_fields.keys())
        return f"Valid fields for {used_model}: {valid_fields}"
```

**Validation:**
```bash
# Test on advanced-configuration.rst (known to have SessionConfig bug)
python -m docs.utils.validators.pydantic_validator docs/tutorials/advanced-configuration.rst
# Should detect: "session_name is not valid for SessionConfig"
```

**CRITICAL TEST:**
```python
# Regression test for SessionConfig bug
def test_sessionconfig_field_validation():
    """Ensure SessionConfig(session_name=...) is caught."""
    validator = PydanticFieldValidator()
    
    rst_content = """
    .. code-block:: python
    
       session_config = SessionConfig(
           session_name="test",  # INVALID!
           inputs={"user_id": "123"}
       )
    """
    
    usages = validator.extract_model_usage(rst_content)
    errors = []
    for usage in usages:
        errors.extend(validator.validate_fields(usage))
    
    assert len(errors) > 0, "Should detect session_name in SessionConfig"
    assert "TracerConfig" in errors[0].suggestion, "Should suggest TracerConfig"
```

---

### Task 1.6: Implement ImportValidator
**Estimated Time:** 45 minutes  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Create `docs/utils/validators/import_validator.py`
- [ ] Implement `ImportValidator` class
- [ ] Implement `extract_imports()` method
- [ ] Implement `validate_import()` method (attempt import in clean environment)
- [ ] Handle ImportError gracefully
- [ ] Return List[ValidationError]

**Dependencies:** Task 1.2

**Key Algorithm:**
```python
import importlib
import sys

def validate_import(self, import_stmt: ImportStatement) -> Optional[ValidationError]:
    """Attempt import, catch ImportError."""
    try:
        if import_stmt.import_type == "import":
            importlib.import_module(import_stmt.module)
        else:  # from_import
            module = importlib.import_module(import_stmt.module)
            for name in import_stmt.names:
                if not hasattr(module, name):
                    return ValidationError(
                        file=import_stmt.file,
                        line_number=import_stmt.line_number,
                        priority="P0",
                        category="import",
                        error_message=f"Cannot import '{name}' from '{import_stmt.module}'",
                        suggestion=f"Check if '{name}' exists in module or was renamed"
                    )
        return None
    except ImportError as e:
        return ValidationError(
            file=import_stmt.file,
            line_number=import_stmt.line_number,
            priority="P0",
            category="import",
            error_message=f"Import error: {str(e)}",
            suggestion="Check module path and ensure package is installed"
        )
```

---

### Task 1.7: Implement IssueReporter
**Estimated Time:** 30 minutes  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Create `docs/utils/validators/issue_reporter.py`
- [ ] Implement `IssueReporter` class
- [ ] Implement `add_issue()` method
- [ ] Implement `categorize()` method (group by category)
- [ ] Implement `prioritize()` method (group by priority)
- [ ] Implement `generate_report()` method (write to `discovered-issues.md`)
- [ ] Format report as Markdown with statistics

**Dependencies:** Task 1.2

**Output Format:**
```markdown
# Documentation Issues Discovered

**Date:** 2025-10-29
**Files Scanned:** 43
**Total Issues:** 5

## Summary

| Priority | Count | Category | Count |
|----------|-------|----------|-------|
| P0 | 3 | pydantic_field | 2 |
| P1 | 2 | rst_structure | 2 |
| | | syntax | 1 |

## P0 (Critical - Causes Execution Errors)

### docs/tutorials/advanced-configuration.rst

**Line 286:** Invalid field 'session_name' for SessionConfig
- **Category:** pydantic_field
- **Suggestion:** Field 'session_name' belongs to TracerConfig, not SessionConfig
```

---

### Task 1.8: Implement ValidationOrchestrator
**Estimated Time:** 45 minutes  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Create `docs/utils/validators/orchestrator.py`
- [ ] Implement `ValidationOrchestrator` class
- [ ] Implement `validate_file()` method (run all validators on single file)
- [ ] Implement `validate_files()` method (optionally parallel)
- [ ] Implement fail-fast logic for P0 errors
- [ ] Aggregate results from all validators

**Dependencies:** Tasks 1.3, 1.4, 1.5, 1.6

**Implementation:**
```python
from typing import List
from pathlib import Path
from multiprocessing import Pool

class ValidationOrchestrator:
    def __init__(self, validators: List[Validator]):
        self.validators = validators
        
    def validate_file(self, rst_file: Path) -> List[ValidationError]:
        """Run all validators on single file."""
        errors = []
        for validator in self.validators:
            errors.extend(validator.validate(rst_file))
        return errors
        
    def validate_files(self, rst_files: List[Path], parallel: bool = True) -> List[ValidationError]:
        """Run validators on multiple files (optionally in parallel)."""
        if parallel and len(rst_files) > 1:
            with Pool(processes=min(8, len(rst_files))) as pool:
                results = pool.map(self.validate_file, rst_files)
            return [error for file_errors in results for error in file_errors]
        else:
            return [error for file in rst_files for error in self.validate_file(file)]
```

---

### Task 1.9: Implement validate_all_examples.py Script
**Estimated Time:** 30 minutes  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Create `docs/utils/validate_all_examples.py`
- [ ] Accept CLI arguments: `--fix`, `--report`
- [ ] Discover all `.rst` files in `docs/` directory
- [ ] Instantiate all validators
- [ ] Run ValidationOrchestrator on all files
- [ ] Generate `discovered-issues.md` via IssueReporter
- [ ] Print summary to terminal
- [ ] Exit with code 0 (no issues) or 1 (issues found)

**Dependencies:** Tasks 1.3-1.8

**Usage:**
```bash
python docs/utils/validate_all_examples.py --report discovered-issues.md
```

---

### Task 1.10: Run Discovery and Generate Issue Report
**Estimated Time:** 15 minutes  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Execute `validate_all_examples.py` on entire `docs/` directory
- [ ] Review generated `discovered-issues.md`
- [ ] Categorize issues by priority (P0/P1/P2/P3)
- [ ] Document total issues found
- [ ] Identify highest-priority issues for Phase 2

**Command:**
```bash
cd /path/to/repo
python docs/utils/validate_all_examples.py --report discovered-issues.md
cat discovered-issues.md
```

**Success Criteria:**
- [ ] Report generated successfully
- [ ] All P0 issues documented
- [ ] Ready to proceed to Phase 2 (Systematic Correction)

---

## Phase 2: Systematic Correction

**Goal:** Fix all discovered issues in priority order  
**Duration:** 8-12 hours  
**Success Criteria:** Zero P0 issues, 80%+ P1 issues fixed, all fixes validated

### Task 2.1: Fix P0 Issues - Pydantic Field Errors
**Estimated Time:** 2-3 hours  
**Priority:** P0 (CRITICAL)

**Acceptance Criteria:**
- [ ] Review all Pydantic field errors from `discovered-issues.md`
- [ ] For each error, identify correct model (TracerConfig vs SessionConfig vs EvaluationConfig)
- [ ] Update documentation examples to use correct models/fields
- [ ] Re-validate each fix with PydanticFieldValidator
- [ ] Document corrections in `corrections.md`

**Process:**
```bash
# For each Pydantic field error:
1. Open file at reported line number
2. Read validator suggestion (e.g., "Use TracerConfig instead")
3. Update code example
4. Re-validate: python -m docs.utils.validators.pydantic_validator {file}
5. Log in corrections.md
```

**Example Correction:**
```python
# BEFORE (docs/tutorials/advanced-configuration.rst:286)
session_config = SessionConfig(
    session_name="test",  # INVALID FIELD!
    inputs={"user_id": "123"}
)

# AFTER
tracer_config = TracerConfig(session_name="test")
session_config = SessionConfig(inputs={"user_id": "123"})
```

---

### Task 2.2: Fix P0 Issues - RST Syntax Errors
**Estimated Time:** 1-2 hours  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Review all RST syntax errors from `discovered-issues.md`
- [ ] Fix title underline mismatches
- [ ] Fix list formatting issues
- [ ] Fix code block directive errors
- [ ] Re-validate each fix with RSTSyntaxValidator
- [ ] Document corrections in `corrections.md`

**Process:**
```bash
# For each RST syntax error:
1. Open file at reported line number
2. Count title characters vs underline characters
3. Adjust underline to match title length
4. Re-validate: python -m docs.utils.validators.rst_validator {file}
5. Log in corrections.md
```

---

### Task 2.3: Fix P0 Issues - Import Errors
**Estimated Time:** 1 hour  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Review all import errors from `discovered-issues.md`
- [ ] Fix incorrect import paths
- [ ] Update moved module references
- [ ] Re-validate each fix with ImportValidator
- [ ] Document corrections in `corrections.md`

---

### Task 2.4: Fix P0 Issues - Code Syntax Errors
**Estimated Time:** 1 hour  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Review all code syntax errors from `discovered-issues.md`
- [ ] Fix Python syntax errors in code examples
- [ ] Ensure code is complete and runnable
- [ ] Re-validate each fix with CodeExampleValidator
- [ ] Document corrections in `corrections.md`

---

### Task 2.5: Validate P0 Corrections
**Estimated Time:** 30 minutes  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Re-run `validate_all_examples.py` on entire docs directory
- [ ] Verify ZERO P0 issues remaining
- [ ] Generate updated `discovered-issues.md`
- [ ] Proceed to P1 fixes

**Validation:**
```bash
python docs/utils/validate_all_examples.py --report discovered-issues-after-p0-fixes.md
# Verify: 0 P0 issues
```

---

### Task 2.6: Fix P1 Issues (High Priority)
**Estimated Time:** 2-4 hours  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Fix 80%+ of P1 issues
- [ ] Focus on: Deprecated patterns, incomplete examples, missing features
- [ ] Re-validate fixes
- [ ] Document corrections

---

### Task 2.7: Generate Corrections Report
**Estimated Time:** 15 minutes  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Create `corrections.md` with all fixes applied
- [ ] Include before/after examples
- [ ] Document fix categories and counts
- [ ] Calculate time spent per issue type

**Format:**
```markdown
# Documentation Corrections Applied

**Date:** 2025-10-29
**Total Corrections:** 23
**Time Spent:** 6 hours

## P0 Corrections (Critical)

### Pydantic Field Errors (8 corrections)

#### docs/tutorials/advanced-configuration.rst:286

**Before:**
```python
session_config = SessionConfig(session_name="test")
```

**After:**
```python
tracer_config = TracerConfig(session_name="test")
session_config = SessionConfig(inputs={...})
```

**Issue:** `session_name` is TracerConfig field, not SessionConfig  
**Time:** 15 minutes
```

---

## Phase 3: Prevention Mechanisms

**Goal:** Install pre-commit hooks and CI/CD to prevent future errors  
**Duration:** 4-6 hours  
**Success Criteria:** Pre-commit hooks block invalid docs, CI/CD validates on PR, docs updated in CHANGELOG

### Task 3.1: Create .pre-commit-config.yaml
**Estimated Time:** 30 minutes  
**Priority:** P0 (PRIMARY DEFENSE)

**Acceptance Criteria:**
- [ ] Create `.pre-commit-config.yaml` in repository root
- [ ] Configure hooks for: validate_changed_docs.py
- [ ] Set `fail_fast: true` to block commits
- [ ] Test hook blocks invalid documentation

**Implementation:**
```yaml
# .pre-commit-config.yaml
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
        
      - id: validate-pydantic-fields
        name: Validate Pydantic Model Fields
        entry: python docs/utils/validate_config_fields.py
        language: system
        files: \.rst$
        pass_filenames: true
        fail_fast: true
```

**Validation:**
```bash
# Install hooks
pre-commit install

# Test: Attempt to commit file with invalid SessionConfig
echo "SessionConfig(session_name='test')" >> test.rst
git add test.rst
git commit -m "test"  # Should FAIL with validation error
```

---

### Task 3.2: Implement validate_changed_docs.py (Pre-commit Script)
**Estimated Time:** 45 minutes  
**Priority:** P0

**Acceptance Criteria:**
- [ ] Create `docs/utils/validate_changed_docs.py`
- [ ] Detect changed RST files using `git diff --cached`
- [ ] Run ValidationOrchestrator on changed files only
- [ ] Exit 1 if P0 issues found (block commit)
- [ ] Exit 0 if validation passes (allow commit)
- [ ] Print clear error messages

**Implementation:**
```python
#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

def get_changed_rst_files() -> List[Path]:
    """Get RST files changed in git staging area."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )
    files = [Path(f) for f in result.stdout.strip().split('\n') if f.endswith('.rst')]
    return files

def main() -> int:
    """Run validation on changed files only."""
    changed_files = get_changed_rst_files()
    
    if not changed_files:
        print("✅ No RST files changed")
        return 0
    
    print(f"Validating {len(changed_files)} RST files...")
    
    orchestrator = ValidationOrchestrator(validators=[
        RSTSyntaxValidator(),
        CodeExampleValidator(),
        PydanticFieldValidator(),
        ImportValidator()
    ])
    
    issues = orchestrator.validate_files(changed_files)
    p0_issues = [i for i in issues if i.priority == "P0"]
    
    if p0_issues:
        print(f"\n❌ COMMIT BLOCKED: {len(p0_issues)} documentation issues found\n")
        for issue in p0_issues:
            print(f"{issue}")
        print("\nFix these issues before committing:")
        print("Run: python docs/utils/validate_all_examples.py --fix")
        return 1
    
    print(f"\n✅ All {len(changed_files)} RST files valid")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

### Task 3.3: Create GitHub Actions Workflow
**Estimated Time:** 60 minutes  
**Priority:** P1 (BACKUP DEFENSE)

**Acceptance Criteria:**
- [ ] Create `.github/workflows/documentation-quality.yml`
- [ ] Trigger on pull_request for `docs/**/*.rst` changes
- [ ] Run all validation scripts
- [ ] Run Sphinx build with `-W` (warnings as errors)
- [ ] Generate quality report as PR comment
- [ ] Fail PR if P0 issues found

**Implementation:**
```yaml
# .github/workflows/documentation-quality.yml
name: Documentation Quality

on:
  pull_request:
    paths:
      - 'docs/**/*.rst'
      - 'docs/utils/**'
      - '.github/workflows/documentation-quality.yml'

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r docs/requirements.txt
          pip install -e .
      
      - name: Run documentation validation
        run: |
          python docs/utils/validate_all_examples.py --report discovered-issues.md
      
      - name: Build documentation
        run: |
          cd docs
          make clean html SPHINXOPTS="-W"  # Treat warnings as errors
      
      - name: Run documentation tests
        run: |
          pytest tests/documentation/ -v
      
      - name: Upload issues report (if any)
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: discovered-issues
          path: discovered-issues.md
```

---

### Task 3.4: Create Post-Merge Validation Workflow
**Estimated Time:** 30 minutes  
**Priority:** P2 (LAST RESORT)

**Acceptance Criteria:**
- [ ] Create `.github/workflows/post-merge-validation.yml`
- [ ] Trigger on push to main branch
- [ ] Run full validation
- [ ] Generate metrics (error count, types, trends)
- [ ] Alert if issues found (indicates pre-commit bypass)

---

### Task 3.5: Create Documentation Test Suite
**Estimated Time:** 90 minutes  
**Priority:** P1

**Acceptance Criteria:**
- [ ] Create `tests/documentation/test_doc_examples.py`
- [ ] Create `tests/documentation/test_config_examples.py`
- [ ] Create `tests/documentation/test_imports.py`
- [ ] Create `tests/documentation/test_full_build.py`
- [ ] All tests pass with pytest
- [ ] Test coverage ≥90%

**Key Tests:**
```python
# tests/documentation/test_config_examples.py
def test_sessionconfig_has_only_three_fields():
    """Regression test for SessionConfig field bug."""
    from honeyhive.config.models.tracer import SessionConfig
    
    valid_fields = set(SessionConfig.model_fields.keys())
    expected_fields = {"session_id", "inputs", "link_carrier"}
    
    assert valid_fields == expected_fields, \
        f"SessionConfig fields changed! Expected {expected_fields}, got {valid_fields}"

def test_session_name_belongs_to_tracerconfig():
    """Ensure session_name is TracerConfig field, not SessionConfig."""
    from honeyhive.config.models.tracer import TracerConfig, SessionConfig
    
    assert "session_name" in TracerConfig.model_fields
    assert "session_name" not in SessionConfig.model_fields

def test_advanced_configuration_examples_valid():
    """Validate all examples in advanced-configuration.rst."""
    validator = PydanticFieldValidator()
    issues = validator.validate(Path("docs/tutorials/advanced-configuration.rst"))
    
    p0_issues = [i for i in issues if i.priority == "P0"]
    
    assert len(p0_issues) == 0, \
        f"Found {len(p0_issues)} P0 issues:\n" + "\n".join([
            f"  - Line {i.line_number}: {i.error_message}"
            for i in p0_issues
        ])
```

---

### Task 3.6: Update CHANGELOG.md
**Estimated Time:** 15 minutes  
**Priority:** P2

**Acceptance Criteria:**
- [ ] Add entry to CHANGELOG.md under "Documentation"
- [ ] Document improvements made
- [ ] Note prevention mechanisms installed

**Entry:**
```markdown
## [Unreleased]

### Documentation
- Fixed Pydantic model field usage in all tutorials (SessionConfig bug fix)
- Fixed RST formatting issues (title underlines, list formatting)
- Added pre-commit hooks for documentation validation
- Added CI/CD validation for all documentation changes
- Implemented automated validation for code examples, Pydantic fields, and imports
```

---

### Task 3.7: Create Update Checklist Standard
**Estimated Time:** 30 minutes  
**Priority:** P2 (PROCESS ENFORCEMENT)

**Acceptance Criteria:**
- [ ] Create `.praxis-os/standards/documentation/update-checklist.md`
- [ ] Define process for updating docs when SDK changes
- [ ] Reference pre-commit hooks as enforcement
- [ ] Provide examples

**Content:**
```markdown
# Documentation Update Checklist

## When Changing Pydantic Models

REQUIRED when modifying TracerConfig, SessionConfig, or EvaluationConfig:

- [ ] Run: `python docs/utils/validate_config_fields.py`
- [ ] Fix any field mismatches in documentation
- [ ] Pre-commit hooks will enforce on commit
- [ ] Update relevant tutorials/examples

## When Adding New SDK Features

- [ ] Add examples to appropriate tutorial
- [ ] Validate examples: `python docs/utils/validate_all_examples.py`
- [ ] Build docs: `cd docs && make html`
- [ ] Preview locally before committing

## Pre-commit Hook Bypass (NEVER DO THIS)

❌ DO NOT use `git commit --no-verify` to bypass validation  
✅ Fix the documentation issues instead
```

---

### Task 3.8: Generate Post-Mortem Document
**Estimated Time:** 30 minutes  
**Priority:** P2

**Acceptance Criteria:**
- [ ] Create `post-mortem.md` documenting the initiative
- [ ] Include metrics: issues found, time spent, fixes applied
- [ ] Document lessons learned
- [ ] Identify any remaining risks

**Format:**
```markdown
# Documentation Quality Verification - Post-Mortem

## Summary

Systematic verification of SDK documentation to prevent SessionConfig-like bugs.

## Metrics

- **Issues Discovered:** 23 total (8 P0, 12 P1, 3 P2)
- **Issues Fixed:** 20 (100% P0, 80% P1)
- **Time Spent:** 18 hours (Discovery: 5h, Correction: 10h, Prevention: 3h)
- **Files Updated:** 12 RST files

## Root Cause

Documentation examples used invalid Pydantic model fields due to:
1. No validation between documentation and source code
2. Manual synchronization between docs and SDK (prone to drift)
3. No automated testing of documentation code examples

## Preventions Installed

1. Pre-commit hooks (PRIMARY - blocks invalid commits)
2. GitHub Actions (BACKUP - validates all PRs)
3. Automated test suite (REGRESSION - prevents recurrence)
4. Update checklist (PROCESS - enforces systematic updates)

## Success Metrics

- **Error escape rate:** Target <0.1% (pre-launch: >1%)
- **Pre-commit catch rate:** 95%+ (measured via CI bypass rate)
- **False positive rate:** <5% (measured via developer feedback)

## Lessons Learned

1. **Shift left works:** Pre-commit validation is 1000x cheaper than production bugs
2. **Dynamic validation:** Loading models from source prevents validator drift
3. **Defense in depth:** Multiple layers catch different edge cases
```

---

## Dependencies Between Tasks

### Phase 1 Dependencies
```
1.1 (Structure) → 1.2 (Models) → [1.3, 1.4, 1.5, 1.6] (Validators)
[1.3, 1.4, 1.5, 1.6] → 1.7 (Reporter)
[1.3, 1.4, 1.5, 1.6] → 1.8 (Orchestrator)
[1.7, 1.8] → 1.9 (Script)
1.9 → 1.10 (Discovery Run)
```

### Phase 2 Dependencies
```
1.10 (Discovery) → [2.1, 2.2, 2.3, 2.4] (P0 Fixes)
[2.1, 2.2, 2.3, 2.4] → 2.5 (Validation)
2.5 → 2.6 (P1 Fixes)
2.6 → 2.7 (Report)
```

### Phase 3 Dependencies
```
1.8 (Orchestrator) → 3.2 (Pre-commit Script)
3.2 → 3.1 (Pre-commit Config)
[3.1, 3.3, 3.4, 3.5] (Can be parallel)
[All Phase 3] → 3.6 (CHANGELOG)
[All Phase 3] → 3.7 (Checklist)
[All Phase 3] → 3.8 (Post-Mortem)
```

---

## Estimated Timeline

| Phase | Duration | Calendar Days |
|-------|----------|---------------|
| Phase 1: Discovery | 4-6 hours | Day 1 |
| Phase 2: Correction | 8-12 hours | Day 2 |
| Phase 3: Prevention | 4-6 hours | Day 3 |
| **Total** | **16-24 hours** | **3 days** |

---



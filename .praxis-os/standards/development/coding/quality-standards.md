# Python SDK Code Quality Standards

**Comprehensive code quality requirements for the HoneyHive Python SDK.**

---

## 🚨 TL;DR - Code Quality Quick Reference

**Keywords for search**: Python SDK code quality, HoneyHive SDK quality gates, pylint score minimum, mypy type checking, black formatting, isort imports, tox quality commands, code coverage requirements, pre-commit hooks mandatory, quality metrics pylint mypy coverage, documentation build zero warnings, formatting 100% compliance, linting 8.0 score required, test coverage 60% minimum, quality troubleshooting pylint mypy, CI/CD quality validation

**Core Principle:** All code MUST pass mandatory quality gates before commit: formatting (100%), linting (≥8.0/10.0), tests (100% pass), documentation (zero warnings).

**Mandatory Quality Gates:**
```bash
tox -e format        # Must pass 100% (Black + isort)
tox -e lint          # Must achieve ≥8.0/10.0 pylint + 0 mypy errors
tox -e unit          # All unit tests must pass
tox -e integration   # All integration tests must pass
cd docs && make html # Must build with zero warnings
```

**Quality Requirements:**
- **Formatting**: Black (88 chars), isort (black profile)
- **Linting**: Pylint ≥8.0/10.0, MyPy zero errors
- **Coverage**: ≥60% overall, ≥80% for new features
- **Documentation**: Sphinx builds with zero warnings

**Pre-Commit Workflow:**
```bash
tox -e format && tox -e lint && tox -e unit
```

---

## ❓ Questions This Answers

1. "What are the Python SDK code quality standards?"
2. "What quality gates must pass before commit?"
3. "What is the minimum pylint score for Python SDK?"
4. "How do I format code for Python SDK?"
5. "What test coverage is required?"
6. "How do I run quality checks?"
7. "What tools are used for code quality?"
8. "How do I fix pylint errors?"
9. "How do I fix mypy type errors?"
10. "What is the pre-commit workflow?"
11. "What causes CI/CD quality failures?"
12. "How do I check code coverage?"
13. "What documentation requirements exist?"
14. "How do I troubleshoot quality issues?"
15. "What are the quality metrics targets?"
16. "How do I configure quality tools?"
17. "What are common quality violations?"
18. "How do I improve pylint score?"
19. "What type annotations are required?"
20. "What are the quality gate decision trees?"

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Quality gates** | `pos_search_project(action="search_standards", query="Python SDK quality gates requirements")` |
| **Formatting** | `pos_search_project(action="search_standards", query="Python SDK formatting black isort")` |
| **Linting** | `pos_search_project(action="search_standards", query="Python SDK pylint mypy requirements")` |
| **Coverage** | `pos_search_project(action="search_standards", query="Python SDK test coverage minimum")` |
| **Troubleshooting** | `pos_search_project(action="search_standards", query="Python SDK quality troubleshooting pylint mypy")` |
| **Pre-commit** | `pos_search_project(action="search_standards", query="Python SDK pre-commit workflow quality")` |
| **CI/CD** | `pos_search_project(action="search_standards", query="Python SDK CI/CD quality validation")` |

---

## 🎯 Purpose

Define the mandatory code quality standards, tools, and processes that ensure consistent, maintainable, and reliable code across the HoneyHive Python SDK.

**Without this standard**: Inconsistent code quality, failing CI/CD builds, poor maintainability, and production issues.

---

## MANDATORY Quality Gates

**All code MUST pass these quality gates before commit:**

### 1. Formatting (100% Compliance Required)

```bash
tox -e format        # Must pass 100%
```

**Tools and Configuration:**
- **Black**: 88-character line length, automatic formatting
- **isort**: Black profile, automatic import sorting
- **Configuration**: Defined in `pyproject.toml`

**What it checks:**
- Line length (88 characters max)
- Import ordering (black profile)
- Trailing whitespace
- Consistent code style

### 2. Static Analysis (≥8.0/10.0 Required)

```bash
tox -e lint          # Must achieve ≥8.0/10.0 pylint score
```

**Tools and Requirements:**
- **pylint**: Minimum 8.0/10.0 score required
- **mypy**: Zero type checking errors allowed
- **Configuration**: Defined in `pyproject.toml` and `pyrightconfig.json`

**What it checks:**
- Code complexity
- Type annotations
- Docstring completeness
- Code patterns and best practices

### 3. Testing (100% Pass Rate Required)

```bash
tox -e unit          # All unit tests must pass
tox -e integration   # All integration tests must pass
```

**Testing Requirements:**
- **Unit Tests**: Fast, isolated, mocked dependencies
- **Integration Tests**: Real API calls, end-to-end validation
- **Coverage**: Minimum 60% overall, 80% for new features

### 4. Documentation Build (Zero Warnings)

```bash
cd docs && make html # Must build with zero warnings
```

**Documentation Quality:**
- **Sphinx build**: Must complete without warnings
- **Code examples**: All examples must be tested and executable
- **Cross-references**: All internal links must be valid

---

## Development Workflow

### Pre-commit Hook Integration

**Automatic enforcement on relevant file changes:**

```yaml
# .pre-commit-config.yaml structure
repos:
  - repo: local
    hooks:
      - id: black-format      # Python files only
      - id: isort-imports     # Python files only  
      - id: pylint-analysis   # Python files only
      - id: mypy-typing       # Python files only
      - id: yamllint-yaml     # YAML files only
      - id: tox-verification  # Scoped by file type
```

**Pre-commit hooks run automatically on `git commit` - DO NOT bypass with `--no-verify`**

### Manual Quality Verification

**Before every commit, run:**

```bash
# Format check (must pass 100%)
tox -e format

# Lint check (must achieve ≥8.0/10.0)
tox -e lint

# Test verification (must pass 100%)
tox -e unit
tox -e integration

# Documentation build (zero warnings)
cd docs && make html
```

---

## Code Quality Metrics

### Pylint Scoring Requirements

**Minimum scores by component:**

- **Core modules** (`src/honeyhive/`): ≥10.0/10.0
- **API modules** (`src/honeyhive/api/`): ≥10.0/10.0  
- **Utility modules** (`src/honeyhive/utils/`): ≥10.0/10.0
- **Test modules** (`tests/`): ≥10.0/10.0
- **Examples** (`examples/`): ≥10.0/10.0

**Overall project target**: ≥8.0/10.0 (enforced in CI/CD)

### Type Coverage Requirements

**MyPy compliance:**
- **Zero errors** in production code
- **Complete type annotations** for all public APIs
- **Type hints** for all function parameters and return values
- **Generic types** properly specified where applicable

### Test Coverage Requirements

**Coverage targets by test type:**

- **Unit Tests**: ≥80% line coverage for new code
- **Integration Tests**: ≥60% line coverage overall
- **Combined Coverage**: ≥60% overall
- **Critical Paths**: 100% coverage for error handling and edge cases

---

## Quality Tools Configuration

### Black Configuration

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
```

### isort Configuration  

```toml
# pyproject.toml
[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
```

### Pylint Configuration

```toml
# pyproject.toml
[tool.pylint.main]
load-plugins = ["pylint.extensions.docparams"]
min-similarity-lines = 10

[tool.pylint.messages_control]
disable = ["too-few-public-methods", "import-error"]

[tool.pylint.format]
max-line-length = 88
```

### MyPy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

---

## Quality Violations

### Automatic Failures

**These violations cause immediate CI/CD failure:**

- **Formatting**: Any Black or isort violations
- **Linting**: Pylint score below 8.0/10.0
- **Type Checking**: Any mypy errors in production code
- **Test Failures**: Any failing unit or integration tests
- **Documentation**: Sphinx build warnings or errors

### Code Review Blockers

**These issues block code review approval:**

- **Missing docstrings** on public functions/classes
- **Incomplete type annotations** on public APIs
- **Hardcoded values** without configuration
- **Missing error handling** in critical paths
- **Untested code paths** in new features

---

## Quality Validation Commands

### Local Development

```bash
# Quick quality check
tox -e format && tox -e lint

# Full quality validation
tox -e format && tox -e lint && tox -e unit && tox -e integration

# Documentation quality
cd docs && make html
```

### CI/CD Pipeline

```bash
# Parallel execution for speed
tox -p auto -e format,lint,unit,integration

# Python version compatibility
tox -e py311,py312,py313
```

---

## Quality Troubleshooting

### Common Issues and Solutions

**Pylint score too low:**

```bash
# Get detailed pylint report
pylint src/honeyhive/ --output-format=text

# Focus on high-impact violations first
pylint src/honeyhive/ --disable=all --enable=error,fatal
```

**MyPy type errors:**

```bash
# Get detailed type error report
mypy src/honeyhive/ --show-error-codes

# Check specific module
mypy src/honeyhive/tracer/otel_tracer.py --show-traceback
```

**Test coverage gaps:**

```bash
# Generate coverage report
coverage run -m pytest tests/unit/
coverage html
# Open htmlcov/index.html to identify gaps
```

### Quality Gate Decision Tree

```
Quality Gate Failed?
├── Formatting Failed (tox -e format)?
│   ├── Line too long? → Run black file.py → Auto-fix
│   ├── Import order? → Run isort file.py → Auto-fix
│   └── Trailing whitespace? → Run black file.py → Auto-fix
├── Linting Failed (tox -e lint)?
│   ├── Pylint < 8.0/10.0?
│   │   ├── Too many args? → Use keyword-only args (*, param)
│   │   ├── Unused variable? → Rename to _ or _variable
│   │   ├── Missing docstring? → Add Sphinx docstring
│   │   └── Protected access? → Add disable for test files only
│   └── Mypy errors?
│       ├── Missing annotations? → Add type hints to all functions
│       ├── Import untyped? → Add py.typed or # type: ignore
│       └── Type mismatch? → Fix type annotations
├── Tests Failed?
│   ├── Unit tests? → Use debugging methodology
│   └── Integration tests? → Check API connectivity
└── Documentation Failed?
    ├── Sphinx warnings? → Fix RST syntax
    └── Example errors? → Test code examples
```

---

## 🔗 Related Standards

**Query workflow for code quality:**

1. **Start with this standard** → `pos_search_project(action="search_standards", query="Python SDK code quality")`
2. **Learn test commands** → `pos_search_project(action="search_standards", query="Python SDK test commands")` → `standards/development/testing/test-execution-commands.md`
3. **Understand environment setup** → `pos_search_project(action="search_standards", query="Python SDK environment setup")` → `standards/development/environment/setup.md`
4. **Learn production checklist** → `pos_search_project(action="search_standards", query="Python SDK production checklist")` → `standards/development/coding/production-checklist.md`

**By Category:**

**Testing:**
- `standards/development/testing/test-execution-commands.md` → `pos_search_project(action="search_standards", query="Python SDK test commands")`

**Environment:**
- `standards/development/environment/setup.md` → `pos_search_project(action="search_standards", query="Python SDK environment setup")`

**Universal Standards:**
- `standards/universal/testing/test-pyramid.md` → `pos_search_project(action="search_standards", query="test pyramid strategy")`

---

## Validation Checklist

Before marking code quality as complete:

- [ ] `tox -e format` passes 100%
- [ ] `tox -e lint` achieves ≥8.0/10.0 pylint score
- [ ] `mypy` reports zero errors
- [ ] `tox -e unit` passes 100%
- [ ] `tox -e integration` passes (if applicable)
- [ ] Test coverage ≥60% overall
- [ ] Documentation builds with zero warnings
- [ ] All docstrings present on public APIs
- [ ] All type annotations complete
- [ ] Pre-commit hooks installed and passing

---

**💡 Key Principle**: Consistent code quality through automated gates ensures reliable, maintainable, and production-ready code.


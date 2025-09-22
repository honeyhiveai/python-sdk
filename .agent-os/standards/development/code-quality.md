# Code Quality Standards

**🎯 Comprehensive code quality requirements for the HoneyHive Python SDK**

This document defines the mandatory code quality standards, tools, and processes that ensure consistent, maintainable, and reliable code across the project.

## 🚨 MANDATORY Quality Gates

**All code MUST pass these quality gates before commit:**

### 1. Formatting (100% Compliance Required)
```bash
tox -e format        # Must pass 100%
```

**Tools and Configuration:**
- **Black**: 88-character line length, automatic formatting
- **isort**: Black profile, automatic import sorting
- **Configuration**: Defined in `pyproject.toml`

### 2. Static Analysis (≥8.0/10.0 Required)
```bash
tox -e lint          # Must achieve ≥8.0/10.0 pylint score
```

**Tools and Requirements:**
- **pylint**: Minimum 8.0/10.0 score required
- **mypy**: Zero type checking errors allowed
- **Configuration**: Defined in `pyproject.toml` and `pyrightconfig.json`

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

## 🔧 Development Workflow

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

## 📊 Code Quality Metrics

### Pylint Scoring Requirements

**Minimum scores by component:**

- **Core modules** (`src/honeyhive/`): ≥10.0/10.0
- **API modules** (`src/honeyhive/api/`): ≥10.0/10.0  
- **Utility modules** (`src/honeyhive/utils/`): ≥10.0/10.0
- **Test modules** (`tests/`): ≥10.0/10.0
- **Examples** (`examples/`): ≥10.0/10.0

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
- **Combined Coverage**: ≥60% overall (currently achieving 73.22%)
- **Critical Paths**: 100% coverage for error handling and edge cases

## 🛠️ Quality Tools Configuration

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

## 🚫 Quality Violations

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

## 📈 Quality Improvement Process

### Continuous Improvement

**Regular quality assessments:**

1. **Weekly**: Review pylint scores and address declining metrics
2. **Monthly**: Analyze test coverage reports and identify gaps
3. **Quarterly**: Review and update quality standards based on learnings

### Technical Debt Management

**Systematic debt reduction:**

- **Prioritize**: Address quality violations in order of impact
- **Track**: Maintain technical debt backlog with clear priorities
- **Measure**: Monitor quality metrics trends over time
- **Prevent**: Establish quality gates to prevent new debt

### Quality Metrics Dashboard

**Key metrics to monitor:**

- **Pylint Score Trend**: Track score changes over time
- **Test Coverage**: Monitor coverage percentage and gaps
- **Build Success Rate**: Track CI/CD pipeline success
- **Documentation Coverage**: Monitor docstring completeness

## 🔍 Quality Validation Commands

### Local Development
```bash
# Quick quality check
tox -e format && tox -e lint

# Full quality validation
tox -e format && tox -e lint && tox -e unit && tox -e integration

# Documentation quality
cd docs && make html && python utils/validate_navigation.py
```

### CI/CD Pipeline
```bash
# Parallel execution for speed
tox -p auto -e format,lint,unit,integration

# Python version compatibility
tox -e py311,py312,py313
```

## 🆘 Quality Troubleshooting

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

### Performance Optimization

**Quality tool performance:**
- **Parallel execution**: Use `tox -p auto` for parallel testing
- **Incremental checks**: Pre-commit hooks only check changed files
- **Caching**: Leverage tox and pre-commit caching for speed

## 🌳 **Quality Gate Decision Trees**

### **Code Quality Troubleshooting**
```
Quality Gate Failed?
├── Formatting Failed (tox -e format)?
│   ├── Line too long? → Run black file.py → Auto-fix
│   ├── Import order? → Run isort file.py → Auto-fix
│   └── Trailing whitespace? → Run black file.py → Auto-fix
├── Linting Failed (tox -e lint)?
│   ├── Pylint < 10.0/10.0?
│   │   ├── Too many args? → Use keyword-only args (*, param)
│   │   ├── Unused variable? → Rename to _ or _variable
│   │   ├── Missing docstring? → Add Sphinx docstring
│   │   └── Protected access? → Add disable for test files only
│   └── Mypy errors?
│       ├── Missing annotations? → Add type hints to all functions
│       ├── Import untyped? → Add py.typed file or # type: ignore
│       └── Type mismatch? → Fix type annotations or filter values
├── Tests Failed?
│   ├── Unit tests? → Use debugging methodology → Fix systematically
│   └── Integration tests? → Check real API connectivity → Fix auth/config
└── Documentation Failed?
    ├── Sphinx warnings? → Fix RST syntax → Check cross-references
    └── Example errors? → Test code examples → Fix imports/syntax
```

### **AI Assistant Quality Decision Tree**
```
Ready to Submit Code?
├── Pre-Generation Validation Complete?
│   ├── Environment validated? → cd project && source venv && python --version
│   ├── Codebase state clean? → git status --porcelain (empty)
│   └── API structure understood? → read_file src/honeyhive/__init__.py
├── Code Generation Standards Met?
│   ├── Type annotations complete? → All params, returns, variables
│   ├── Docstrings complete? → Sphinx format with examples
│   ├── Error handling implemented? → Graceful degradation patterns
│   └── Quality patterns followed? → Keyword args, safe_log usage
├── All Quality Gates Pass?
│   ├── tox -e format → 100% pass required
│   ├── tox -e lint → ≥8.0/10.0 pylint + 0 mypy errors
│   ├── tox -e unit → 100% pass required
│   ├── tox -e integration → 100% pass required
│   └── cd docs && make html → 0 warnings required
└── Self-Validation Checklist Complete?
    ├── All checkboxes marked ✅ in quality-framework.md
    ├── Command templates used exactly as specified
    └── No shortcuts or assumptions made
```

---

**📝 Next Steps**: After mastering code quality, review [Testing Standards](testing-standards.md) and [Python Standards](../coding/python-standards.md).

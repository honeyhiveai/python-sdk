# Python SDK Development Environment Setup

**Project-specific environment configuration for the HoneyHive Python SDK.**

---

## 🚨 TL;DR - Environment Setup Quick Reference

**Keywords for search**: Python SDK environment, HoneyHive SDK setup, development environment configuration, pre-commit hooks, virtual environment python-sdk, tox testing, black formatting, pylint mypy, yamllint GitHub CLI, HH_API_KEY environment variables, pip install development mode, quality gates mandatory

**Core Principle:** Consistent, reproducible development environments across all contributors ensure code quality and prevent "works on my machine" issues.

**One-Command Setup:**
```bash
./scripts/setup-dev.sh  # Installs pre-commit hooks and validates tools
```

**Critical Requirements:**
1. **Virtual environment named "python-sdk"** (project convention)
2. **Pre-commit hooks installed** (mandatory, cannot bypass)
3. **Required tools**: yamllint >=1.37.0, GitHub CLI (gh), Docker
4. **Environment variables**: Use `.env` file for local development (HH_API_KEY, etc.)
5. **Python 3.11+** (respects pyproject.toml requires-python constraint)

**Quality Gate Checklist:**
- [ ] Virtual environment "python-sdk" activated
- [ ] Pre-commit hooks installed (`./scripts/setup-dev.sh`)
- [ ] Tools verified: `yamllint --version`, `gh --version`
- [ ] Development install: `pip install -e .`
- [ ] Pre-commit runs: `pre-commit run --all-files`
- [ ] Tests pass: `tox -e unit && tox -e integration`

**Common Mistakes:**
- ❌ Installing packages globally (pollutes system Python)
- ❌ Bypassing pre-commit hooks (`--no-verify`)
- ❌ Using wrong virtual environment name (breaks IDE configs)
- ❌ Skipping development mode install (`pip install -e .`)

---

## ❓ Questions This Answers

1. "How do I set up the Python SDK development environment?"
2. "What virtual environment name should I use for Python SDK?"
3. "How to install pre-commit hooks for Python SDK?"
4. "What tools are required for Python SDK development?"
5. "How to configure IDE for Python SDK?"
6. "What environment variables does Python SDK use?"
7. "How to run tests for Python SDK?"
8. "What Python versions are supported by Python SDK?"
9. "How to troubleshoot virtual environment issues?"
10. "What is the Python SDK quality gate process?"
11. "How to configure Black formatter for Python SDK?"
12. "What is the Python SDK pre-commit hook workflow?"
13. "How to install development dependencies for Python SDK?"
14. "What is the environment variable precedence for Python SDK?"
15. "How to validate Python SDK environment setup?"
16. "What tox environments are available for Python SDK?"
17. "How to run parallel tests for Python SDK?"
18. "What is the Python SDK CI/CD environment compatibility?"
19. "How to resolve dependency conflicts in Python SDK?"
20. "What is the Python SDK documentation build process?"
21. "How to use `.env` file for local Python SDK development?"
22. "What is HH_API_KEY and where do I get it?"

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Initial setup** | `pos_search_project(action="search_standards", query="Python SDK environment setup")` |
| **Pre-commit issues** | `pos_search_project(action="search_standards", query="Python SDK pre-commit hooks")` |
| **Virtual env problems** | `pos_search_project(action="search_standards", query="Python SDK virtual environment")` |
| **Tool installation** | `pos_search_project(action="search_standards", query="Python SDK required tools")` |
| **IDE configuration** | `pos_search_project(action="search_standards", query="configure IDE for Python SDK")` |
| **Environment variables** | `pos_search_project(action="search_standards", query="Python SDK environment variables")` |
| **Quality gates** | `pos_search_project(action="search_standards", query="Python SDK quality gates")` |
| **Test execution** | `pos_search_project(action="search_standards", query="how to run Python SDK tests")` |
| **Dependency issues** | `pos_search_project(action="search_standards", query="Python SDK dependency management")` |
| **CI/CD compatibility** | `pos_search_project(action="search_standards", query="Python SDK CI environment")` |

---

## 🎯 Purpose

This standard ensures **consistent, high-quality development environments** across all Python SDK contributors by defining:
- Required tools and versions
- Virtual environment conventions
- Pre-commit hook configuration
- Quality gate processes
- IDE setup patterns
- Environment variable standards

**Without this standard**: Developers experience "works on my machine" issues, quality gates fail unpredictably, and code quality degrades.

---

## Mandatory Quality Process

### ⚠️ CRITICAL: Install Pre-commit Hooks

```bash
# One-time setup (required for all developers)
./scripts/setup-dev.sh
```

**Automatic Quality Enforcement** (only runs when relevant files change):
- **Black formatting**: 88-character lines, applied when Python files change
- **Import sorting**: isort with black profile, applied when Python files change
- **Static analysis**: pylint + mypy type checking when Python files change
- **YAML validation**: yamllint with 120-character lines when YAML files change
- **Documentation checks**: Only when docs/praxis OS files change
- **Tox verification**: Scoped to relevant file types for efficiency

### Before Every Commit (AI Assistants)

1. Pre-commit hooks run automatically (DO NOT bypass with `--no-verify`)
2. Manual verification: `tox -e format && tox -e lint`
3. **MANDATORY**: All tests must pass - `tox -e unit && tox -e integration`
4. **MANDATORY**: Update documentation before committing
5. **MANDATORY**: Use correct dates - `date +"%Y-%m-%d"` command

---

## Required Tools

### Core Development Tools

```bash
# YAML validation for GitHub Actions
pip install yamllint>=1.37.0

# GitHub CLI for workflow investigation
brew install gh

# Verify installation
yamllint --version  # Should show 1.37.0 or higher
gh --version        # Should show 2.78.0 or higher
```

### Tool Usage Patterns

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **yamllint** | Validate GitHub Actions YAML syntax | Before committing workflow changes |
| **GitHub CLI (gh)** | Investigate workflow failures, view run logs, manage releases | When debugging CI/CD issues |
| **Docker** | Lambda testing and container validation | When testing AWS Lambda functions |
| **tox** | Test orchestration and environment management | Running tests, linting, formatting |

---

## Virtual Environment Setup

### ALWAYS Use Virtual Environments

**Never install packages globally.** Always use project-specific virtual environments.

**Use virtual environment named "python-sdk"** (project convention):

```bash
# Create virtual environment
python -m venv python-sdk

# Activate (macOS/Linux)
source python-sdk/bin/activate

# Activate (Windows)
python-sdk\Scripts\activate

# Install in development mode (editable install)
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### Why "python-sdk" Name?

- **IDE Configuration**: All IDE settings reference `./python-sdk/bin/python`
- **Consistency**: Every contributor uses same path
- **Tooling**: Scripts and configs expect this name
- **Documentation**: Examples reference this specific path

---

## Environment Variables

### Standard Environment Variable Patterns

```python
# Support multiple prefixes for compatibility
api_key = (
    os.getenv("HH_API_KEY") or           # HoneyHive prefix (preferred)
    os.getenv("HONEYHIVE_API_KEY") or    # Full name prefix
    os.getenv("API_KEY")                 # Generic fallback
)
```

### Configuration Precedence

1. **Constructor parameters** (highest priority)
2. **HH_* environment variables** (HoneyHive-specific)
3. **Standard environment variables** (generic)
4. **Default values** (lowest priority)

### Local Development: Use `.env` File

**For local development, use `.env` file for credentials** (project convention):

```bash
# .env (in project root, gitignored)
HH_API_KEY=your_api_key_here
HH_TIMEOUT=30.0
HH_PROJECT=your_project_name
```

**Never commit credentials to git.** The `.env` file is automatically ignored.

### Configuration Validation Example

```python
class Config:
    def __init__(self):
        self.api_key = self._validate_api_key()
        self.timeout = self._validate_timeout()
        
    def _validate_timeout(self) -> float:
        """Validate and parse timeout value."""
        timeout = os.getenv("HH_TIMEOUT", "30.0")
        try:
            value = float(timeout)
            if value <= 0:
                raise ValueError("Timeout must be positive")
            return value
        except (ValueError, TypeError):
            logger.warning(f"Invalid timeout: {timeout}, using default")
            return 30.0
```

---

## IDE Configuration

### VS Code Settings

```json
{
    "python.defaultInterpreterPath": "./python-sdk/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm Settings

- Enable Black formatter (88 character line length)
- Configure isort integration (black profile)
- Enable MyPy type checking
- Enable auto-import optimization on save

---

## Quality Validation Workflow

### Local Development Workflow

```bash
# Before starting work
git pull origin main
source python-sdk/bin/activate
pip install -e .

# During development (run frequently)
tox -e format  # Auto-format code with Black
tox -e lint    # Check code quality (pylint + mypy)
tox -e unit    # Run unit tests with pytest

# Before committing
tox -e integration  # Run integration tests
cd docs && make html  # Build Sphinx documentation
```

### Test Execution Patterns

```bash
# Run tests in parallel (faster)
tox -e unit -- -n auto

# Run specific test file
tox -e unit -- tests/unit/test_specific.py

# Skip slow tests during development
tox -e unit -- -m "not slow"

# Run integration tests in parallel
tox -e integration-parallel
```

---

## Continuous Integration Compatibility

### CI/CD Environment Requirements

All development environments must be compatible with CI/CD:

- **Python versions**: 3.11, 3.12, 3.13
- **Operating systems**: Ubuntu (primary), macOS, Windows
- **Dependencies**: Must install cleanly from pyproject.toml
- **Tests**: Must pass in parallel execution environment
- **Pre-commit hooks**: Must pass all checks

---

## Troubleshooting

### Virtual Environment Issues

**Problem**: Activation fails or environment corrupted

```bash
# Solution: Recreate environment
deactivate                    # Exit current environment
rm -rf python-sdk            # Remove corrupted environment
python -m venv python-sdk    # Recreate
source python-sdk/bin/activate
pip install -e .
```

### Dependency Conflicts

**Problem**: Conflicting package versions

```bash
# Solution: Clean install
pip freeze | xargs pip uninstall -y  # Remove all packages
pip install -e .                      # Reinstall from pyproject.toml
```

### Pre-commit Hook Issues

**Problem**: Hooks not running or failing unexpectedly

```bash
# Solution: Reinstall hooks
pre-commit uninstall
pre-commit install
pre-commit run --all-files  # Validate on all files
```

### Environment Variable Not Found

**Problem**: `HH_API_KEY` not recognized

```bash
# Solution: Check .env file and precedence
cat .env                    # Verify .env exists
echo $HH_API_KEY           # Check if loaded
source .env                # Manually load if needed (not recommended)
# Better: Use python-dotenv in code
```

---

## 🔗 Related Standards

**Query workflow for environment setup:**

1. **Start with this standard** → `pos_search_project(action="search_standards", query="Python SDK environment setup")`
2. **Configure Git workflow** → `pos_search_project(action="search_standards", query="Python SDK git workflow")` → `standards/development/workflow/git-workflow.md`
3. **Learn testing standards** → `pos_search_project(action="search_standards", query="Python SDK testing standards")` → `standards/development/testing/testing-standards.md`
4. **Understand quality gates** → `pos_search_project(action="search_standards", query="Python SDK code quality")` → `standards/development/coding/quality-standards.md`

**By Category:**

**Development Workflow:**
- `standards/development/workflow/git-workflow.md` → `pos_search_project(action="search_standards", query="Python SDK git workflow")`
- `standards/development/workflow/release-process.md` → `pos_search_project(action="search_standards", query="Python SDK release process")`

**Code Quality:**
- `standards/development/coding/quality-standards.md` → `pos_search_project(action="search_standards", query="Python SDK code quality")`
- `standards/development/coding/production-checklist.md` → `pos_search_project(action="search_standards", query="Python SDK production checklist")`

**Testing:**
- `standards/development/testing/testing-standards.md` → `pos_search_project(action="search_standards", query="Python SDK testing")`
- `standards/development/testing/performance-guidelines.md` → `pos_search_project(action="search_standards", query="Python SDK performance")`

**Universal Standards:**
- `standards/universal/testing/integration-testing.md` → `pos_search_project(action="search_standards", query="integration testing best practices")`
- `standards/universal/ai-safety/credential-file-protection.md` → `pos_search_project(action="search_standards", query="credential safety")`

---

## Validation Checklist

Before marking environment setup as complete:

- [ ] Virtual environment "python-sdk" created and activated
- [ ] `pip install -e .` executed successfully
- [ ] Pre-commit hooks installed via `./scripts/setup-dev.sh`
- [ ] `yamllint --version` shows 1.37.0 or higher
- [ ] `gh --version` shows 2.78.0 or higher
- [ ] `pre-commit run --all-files` passes
- [ ] `tox -e unit` passes
- [ ] `tox -e lint` passes
- [ ] IDE configured with correct interpreter path
- [ ] `.env` file created with HH_API_KEY (not committed)

---

**📝 Next Steps**: 
- Review [Git Workflow](../workflow/git-workflow.md) for branching and commit standards
- Review [Testing Standards](../testing/testing-standards.md) for test execution requirements
- Review [Code Quality](../coding/quality-standards.md) for quality gates


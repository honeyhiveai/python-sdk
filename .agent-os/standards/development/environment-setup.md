# Development Environment Setup - HoneyHive Python SDK

**🎯 MISSION: Ensure consistent, high-quality development environments across all contributors**

## Mandatory Code Quality Process

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
- **Documentation checks**: Only when docs/Agent OS files change
- **Tox verification**: Scoped to relevant file types for efficiency

### Before Every Commit

1. Pre-commit hooks run automatically (DO NOT bypass)
2. Manual verification: `tox -e format && tox -e lint`
3. **MANDATORY**: All tests must pass - `tox -e unit && tox -e integration`
4. **MANDATORY for AI Assistants**: Update documentation before committing
5. **MANDATORY for AI Assistants**: Use correct dates - `date +"%Y-%m-%d"` command

## Required Tools

```bash
# Core development tools
pip install yamllint>=1.37.0  # YAML validation for workflows
brew install gh               # GitHub CLI for workflow investigation

# Verify installation
yamllint --version
gh --version
```

### Tool Usage Patterns
- **yamllint**: Validate GitHub Actions YAML syntax before commits
- **GitHub CLI**: Investigate workflow failures, view run logs, manage releases
- **Docker**: Required for Lambda testing and container validation

## Virtual Environment & Dependencies

### ALWAYS use virtual environments - Never install packages globally

**Use a virtual environment named "python-sdk"** for this project:

```bash
# Create and activate virtual environment
python -m venv python-sdk
source python-sdk/bin/activate  # On macOS/Linux
# python-sdk\Scripts\activate   # On Windows

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### Dependency Management
- Use the project's pyproject.toml for dependency management
- Respect the requires-python = ">=3.11" constraint
- Pin versions for reproducible builds
- Use pip-tools for dependency resolution

## Configuration Standards

### Environment Variable Patterns

```python
# Support multiple prefixes for compatibility
api_key = (
    os.getenv("HH_API_KEY") or
    os.getenv("HONEYHIVE_API_KEY") or
    os.getenv("API_KEY")
)

# Configuration precedence
# 1. Constructor parameters (highest)
# 2. HH_* environment variables
# 3. Standard environment variables
# 4. Default values (lowest)
```

### Configuration Validation

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

- Enable Black formatter
- Configure isort integration
- Enable MyPy type checking
- Set line length to 88 characters
- Enable auto-import optimization

## Quality Validation

### Local Development Workflow

```bash
# Before starting work
git pull origin main
source python-sdk/bin/activate
pip install -e .

# During development (run frequently)
tox -e format  # Auto-format code
tox -e lint    # Check code quality
tox -e unit    # Run unit tests

# Before committing
tox -e integration  # Run integration tests
cd docs && make html  # Build documentation
```

### Continuous Integration Setup

All development environments must be compatible with CI/CD requirements:

- **Python versions**: 3.11, 3.12, 3.13
- **Operating systems**: Ubuntu (primary), macOS, Windows
- **Dependencies**: Must install cleanly from pyproject.toml
- **Tests**: Must pass in parallel execution environment

## Troubleshooting

### Common Setup Issues

**Virtual Environment Issues**:
```bash
# If activation fails
deactivate  # Exit current environment
rm -rf python-sdk  # Remove corrupted environment
python -m venv python-sdk  # Recreate
source python-sdk/bin/activate
```

**Dependency Conflicts**:
```bash
# Clean install
pip freeze | xargs pip uninstall -y
pip install -e .
```

**Pre-commit Hook Issues**:
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
pre-commit run --all-files
```

### Performance Optimization

**Faster Test Execution**:
```bash
# Run tests in parallel
tox -e unit -- -n auto

# Run specific test files
tox -e unit -- tests/unit/test_specific.py

# Skip slow tests during development
tox -e unit -- -m "not slow"
```

## References

- **[Git Workflow](git-workflow.md)** - Branching and commit standards
- **[Testing Standards](testing-standards.md)** - Test execution requirements
- **[Code Quality](code-quality.md)** - Quality gates and tool configuration

---

**📝 Next Steps**: Review [Git Workflow](git-workflow.md) for branching and commit standards.
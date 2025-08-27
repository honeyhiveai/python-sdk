# Tox Testing Setup Summary

This document summarizes the tox testing configuration that has been set up for the HoneyHive Python SDK.

## What Was Configured

### 1. Tox Configuration (`tox.ini`)
- **Python Versions**: 3.10, 3.11, 3.12
- **Test Environment**: Uses pytest with coverage reporting
- **Additional Environments**: lint, format, docs
- **Dependencies**: Automatically installs all required packages from pyproject.toml

### 2. Project Configuration Updates (`pyproject.toml`)
- **Python Version Support**: Maintained at 3.10+
- **Classifiers**: Python 3.10+ support
- **Dependencies**: Maintained compatibility across all Python versions

### 3. Helper Scripts**
- **`scripts/run_tox.py`**: Python script for running tox commands
- **`scripts/install_python_versions.sh`**: Bash script for installing required Python versions
- **Both scripts are executable and provide user-friendly interfaces**

### 4. Makefile Integration
- **`make tox`**: Run all tests across all Python versions

- **`make tox-py310`**: Run tests for Python 3.10
- **`make tox-py311`**: Run tests for Python 3.11
- **`make tox-py312`**: Run tests for Python 3.12
- **`make tox-lint`**: Run linting checks
- **`make tox-format`**: Run code formatting checks
- **`make tox-install`**: Install tox

### 5. Documentation
- **`TOX_README.md`**: Comprehensive guide for using tox
- **`README.md`**: Updated with testing section
- **`requirements-tox.txt`**: Additional dependencies for tox

## Available Commands

### Direct tox usage
```bash
# List environments
tox -l

# Run all tests
tox

# Run specific Python version
tox -e py311

# Run with additional pytest arguments
tox -- -v --tb=short
```

### Using helper script
```bash
# List environments
python scripts/run_tox.py list

# Run tests
python scripts/run_tox.py test

# Run specific version
python scripts/run_tox.py test -e py311

# Run linting
python scripts/run_tox.py lint
```

### Using make
```bash
# Run all tests
make tox

# Run specific version
make tox-py311

# Run linting
make tox-lint
```

## Test Environments

| Environment | Description | Python Version |
|-------------|-------------|----------------|

| `py310` | Python 3.10 tests | 3.10.13 |
| `py311` | Python 3.11 tests | 3.11.7 |
| `py312` | Python 3.12 tests | 3.12.1 |
| `lint` | Code linting | Current Python |
| `format` | Code formatting | Current Python |
| `docs` | Documentation build | Current Python |

## Coverage and Reporting

- **HTML Coverage**: Generated in `htmlcov/` directory
- **XML Coverage**: Generated for CI/CD integration
- **Terminal Output**: Shows coverage summary and missing lines
- **Source**: Covers `src/honeyhive` directory

## Dependencies

The tox configuration automatically installs:
- All project dependencies from `pyproject.toml`
- Testing dependencies (pytest, pytest-cov, pytest-asyncio)
- Linting tools (pylint, mypy, black, isort)
- Documentation tools (sphinx, sphinx-rtd-theme)

## Python Version Requirements

To run all test environments, you need:
- Python 3.10.13+
- Python 3.11.7+
- Python 3.12.1+

**Note**: Tox will skip environments for unavailable Python versions gracefully.

## Installation Help

If you don't have all required Python versions:

```bash
# Install tox
pip install tox>=4.0

# Install Python versions (macOS/Linux)
./scripts/install_python_versions.sh

# Or use pyenv (recommended)
pyenv install 3.10.13 3.11.7 3.12.1
```

## Next Steps

1. **Install tox**: `pip install tox>=4.0`
2. **Install Python versions**: Use the helper script or pyenv
3. **Run tests**: `tox` or `make tox`
4. **Check coverage**: Coverage reports are generated automatically
5. **Run linting**: `tox -e lint` or `make tox-lint`

## Troubleshooting

- **Python version not found**: Use `./scripts/install_python_versions.sh`
- **Dependency conflicts**: Run `tox --recreate`
- **Test failures**: Use `tox -e py311 -- -v` for verbose output
- **Environment issues**: Check `tox -l` for available environments

## Benefits

This setup provides:
- **Multi-version testing**: Ensures compatibility across Python 3.10-3.12
- **Isolated environments**: Each Python version runs in its own virtual environment
- **Automated dependency management**: No manual environment setup required
- **CI/CD ready**: Easy integration with GitHub Actions, GitLab CI, etc.
- **Developer friendly**: Multiple ways to run tests (tox, script, make)
- **Comprehensive coverage**: Tests, linting, formatting, and documentation

# Tox Testing Configuration for HoneyHive Python SDK

This document explains how to use tox to run tests across multiple Python versions (3.10, 3.11, 3.12) for the HoneyHive Python SDK.

## Overview

Tox is a generic virtual environment management and test command line tool that provides:
- Testing across multiple Python versions
- Isolated test environments
- Automated dependency management
- Consistent test execution across different environments

## Prerequisites

- Python 3.10+ installed on your system
- Access to Python 3.10, 3.11, and 3.12 (tox will use the available versions)

## Installation

### Install tox

```bash
# Using pip
pip install tox>=4.0

# Or using the helper script
python scripts/run_tox.py install

# Or using make
make tox-install
```

### Install Python versions

You'll need Python 3.9, 3.10, 3.11, and 3.12 available on your system. You can use pyenv or your system's package manager:

```bash
# Using pyenv (recommended)
pyenv install 3.10.13
pyenv install 3.11.7
pyenv install 3.12.1

# Or using Homebrew on macOS
brew install python@3.10 python@3.11 python@3.12
```

## Usage

### Basic Commands

#### Run all tests across all Python versions
```bash
# Using tox directly
tox

# Using the helper script
python scripts/run_tox.py test

# Using make
make tox
```

#### Run tests for a specific Python version
```bash
# Python 3.9
tox -e py39
python scripts/run_tox.py test -e py39
make tox-py39

# Python 3.10
tox -e py310
python scripts/run_tox.py test -e py310
make tox-py310

# Python 3.11
tox -e py311
python scripts/run_tox.py test -e py311
make tox-py311

# Python 3.12
tox -e py312
python scripts/run_tox.py test -e py312
make tox-py312
```

#### Run linting checks
```bash
tox -e lint
python scripts/run_tox.py lint
make tox-lint
```

#### Run code formatting checks
```bash
tox -e format
python scripts/run_tox.py format
make tox-format
```

#### Build documentation
```bash
tox -e docs
python scripts/run_tox.py docs
```

### Advanced Usage

#### Pass additional arguments to pytest
```bash
# Run specific test files
tox -- tests/test_openai.py

# Run with verbose output
tox -- -v

# Run with coverage
tox -- --cov=src/honeyhive --cov-report=html

# Run specific test markers
tox -- -m "not slow"
```

#### Parallel execution
```bash
# Run tests in parallel (requires pytest-xdist)
tox -- --numprocesses=auto
```

#### Environment variables
```bash
# Set environment variables for tests
HH_API_KEY=your_key tox -e py311
```

## Configuration

The tox configuration is in `tox.ini` and includes:

### Test Environments
- `py310`: Python 3.10 tests  
- `py311`: Python 3.11 tests
- `py312`: Python 3.12 tests

### Additional Environments
- `lint`: Code linting with pylint and mypy
- `format`: Code formatting checks with black and isort
- `docs`: Documentation building with Sphinx

### Dependencies
Each environment automatically installs the required dependencies from the project's `pyproject.toml` and additional testing dependencies.

## Test Structure

Tests are organized in the `tests/` directory:
- `tests/api/`: API endpoint tests
- `tests/integration/`: Integration tests
- `tests/tracers/`: Tracer-specific tests
- `tests/utils/`: Utility function tests

## Coverage

Test coverage is automatically generated and includes:
- HTML coverage report in `htmlcov/`
- XML coverage report for CI/CD integration
- Terminal coverage summary

## Troubleshooting

### Common Issues

#### Python version not found
```bash
# Check available Python versions
python --version
python3.10 --version
python3.11 --version
python3.12 --version

# Install missing versions or update PATH
```

#### Dependency conflicts
```bash
# Clean tox environments
tox --recreate

# Or remove specific environment
rm -rf .tox/py310
```

#### Test failures
```bash
# Run with verbose output
tox -e py311 -- -v

# Run specific failing test
tox -e py311 -- tests/test_specific.py::test_function
```

### Environment Setup

If you encounter issues with specific Python versions, ensure:
1. The Python version is properly installed and accessible
2. Virtual environments can be created for that version
3. Dependencies are compatible with the Python version

## CI/CD Integration

The tox configuration is designed to work with CI/CD systems:

```yaml
# GitHub Actions example
- name: Run tests with tox
  run: |
    pip install tox
    tox --parallel
```

## Contributing

When adding new tests:
1. Ensure tests work across all Python versions
2. Add any new dependencies to the tox configuration
3. Update this documentation if needed

## Additional Resources

- [Tox Documentation](https://tox.wiki/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Version Support](https://devguide.python.org/versions/)

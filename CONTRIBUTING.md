# Contributing to This Repository

Thank you for your interest in contributing to this repository. Please note that this repository contains generated code. As such, we do not accept direct changes or pull requests. Instead, we encourage you to follow the guidelines below to report issues and suggest improvements.

## How to Report Issues

If you encounter any bugs or have suggestions for improvements, please open an issue on GitHub. When reporting an issue, please provide as much detail as possible to help us reproduce the problem. This includes:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected and actual behavior
- Any relevant logs, screenshots, or error messages
- Information about your environment (e.g., operating system, software versions)
    - For example can be collected using the `npx envinfo` command from your terminal if you have Node.js installed

## Issue Triage and Upstream Fixes

We will review and triage issues as quickly as possible. Our goal is to address bugs and incorporate improvements in the upstream source code. Fixes will be included in the next generation of the generated code.

## Contact

If you have any questions or need further assistance, please feel free to reach out by opening an issue.

Thank you for your understanding and cooperation!

The Maintainers

---

## For HoneyHive Developers

### Development Setup

**Option A: Nix Flakes (Recommended)**

```bash
cd python-sdk
direnv allow  # One-time setup - automatically configures environment
```

**Option B: Traditional Setup**

```bash
cd python-sdk
python -m venv python-sdk
source python-sdk/bin/activate
pip install -e ".[dev,docs]"
./scripts/setup-dev.sh
```

### Common Development Tasks

We provide a Makefile for common development tasks:

```bash
make help              # Show all available commands

# Testing
make test              # Run all tests
make test-fast         # Run tests in parallel
make test-unit         # Unit tests only
make test-integration  # Integration tests only

# Code Quality
make format            # Format code with black and isort
make lint              # Run linting checks
make typecheck         # Run mypy type checking
make check             # Run ALL checks (everything that was in pre-commit)

# Individual Checks (for granular control)
make check-format            # Check code formatting only
make check-lint              # Check linting only
make check-integration       # Integration test validation
make check-docs              # Build and validate documentation
make check-docs-compliance   # Check documentation compliance
make check-feature-sync      # Check feature documentation sync
make check-tracer-patterns   # Check for invalid tracer patterns
make check-no-mocks          # Verify no mocks in integration tests

# Documentation
make docs              # Build documentation
make docs-serve        # Build and serve docs locally
make docs-clean        # Clean doc build artifacts

# SDK Generation
make generate-sdk      # Generate SDK from openapi.yaml
make compare-sdk       # Compare generated SDK with current

# Maintenance
make clean             # Remove build artifacts
make clean-all         # Deep clean (includes .venv)
```

### Pre-commit Hooks

Pre-commit hooks are **fast** (runs in seconds) and automatically enforce:
- ✅ Black formatting
- ✅ Import sorting (isort)
- ✅ Static analysis (pylint + mypy)
- ✅ YAML validation
- ✅ Unit tests (fast, mocked)

**Heavy checks moved to Makefile**: Integration tests, documentation builds, and compliance checks are now run via `make check-all` instead of on every commit. This makes commits fast while still allowing comprehensive validation when needed.
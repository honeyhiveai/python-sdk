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
git clone https://github.com/honeyhiveai/python-sdk.git
cd python-sdk

# Allow direnv (one-time setup)
direnv allow

# That's it! Environment automatically configured with:
# - Python 3.12
# - All dev dependencies
# - Tox environments
```

See [NIX_SETUP.md](NIX_SETUP.md) for full details on the Nix development environment.

**Option B: Traditional Setup**

```bash
git clone https://github.com/honeyhiveai/python-sdk.git
cd python-sdk

# Create and activate virtual environment named 'python-sdk' (required)
python -m venv python-sdk
source python-sdk/bin/activate  # On Windows: python-sdk\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev,docs]"

# Set up development environment (installs tools, runs verification)
./scripts/setup-dev.sh
```

### Common Development Tasks

We provide a Makefile for common development tasks. Run:

```bash
make help
```

Key commands:
- `make check` - Run all comprehensive checks (format, lint, tests, docs, validation)
- `make test` - Run all tests
- `make format` - Format code with Black and isort
- `make lint` - Run linting checks
- `make generate-sdk` - Generate SDK from OpenAPI spec

### Code Quality Checks

Before pushing code, run:
```bash
make check
```

This runs all quality checks:
- ✅ Black formatting
- ✅ Import sorting (isort)
- ✅ Static analysis (pylint + mypy)
- ✅ Unit tests (fast, mocked)
- ✅ Integration test validation
- ✅ Documentation builds
- ✅ Tracer pattern validation
- ✅ Feature documentation sync

All these checks also run automatically in CI when you push or create a pull request.
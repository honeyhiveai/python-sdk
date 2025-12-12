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

We provide a Makefile for common development tasks. Run:

```bash
make help
```

Key commands:
- `make check` - Run all comprehensive checks (everything that was in pre-commit)
- `make test` - Run all tests
- `make format` - Format code
- `make generate-sdk` - Generate SDK from OpenAPI spec

### Pre-commit Hooks

Pre-commit hooks are **fast** (runs in seconds) and automatically enforce:
- ✅ Black formatting
- ✅ Import sorting (isort)
- ✅ Static analysis (pylint + mypy)
- ✅ YAML validation
- ✅ Unit tests (fast, mocked)

**Heavy checks moved to Makefile**: Integration tests, documentation builds, and compliance checks are now run via `make check-all` instead of on every commit. This makes commits fast while still allowing comprehensive validation when needed.
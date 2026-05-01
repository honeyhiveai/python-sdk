.PHONY: help install install-dev test test-all test-unit test-integration check-integration lint format check check-format check-lint typecheck check-tracer-patterns check-no-mocks generate generate-sdk compare-sdk docs-serve docs-build clean clean-all build publish

# Use uv run to automatically resolve the workspace venv and dependencies.
# --extra dev ensures SDK dev optional-dependencies (black, isort, tox, etc.) are installed.
# Override with: UV_RUN="python3" make build
UV_RUN ?= uv run --extra dev
PYTHON ?= $(UV_RUN) python

# Default target
help:
	@echo "HoneyHive Python SDK - Available Commands"
	@echo "=========================================="
	@echo ""
	@echo "Development:"
	@echo "  make install         - Install package in editable mode"
	@echo "  make install-dev     - Install with dev dependencies"
	@echo "  make setup           - Run initial development setup"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run tests in parallel (unit, tracer, compatibility - no external deps)"
	@echo "  make test-all        - Run ALL tests in parallel (requires .env with API credentials)"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration - Run integration tests only (requires .env)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format          - Format code with black and isort"
	@echo "  make lint            - Run linting checks"
	@echo "  make typecheck       - Run mypy type checking"
	@echo "  make check           - Run ALL checks"
	@echo ""
	@echo "Individual Checks (for granular control):"
	@echo "  make check-format    - Check code formatting only"
	@echo "  make check-lint      - Check linting only"
	@echo "  make check-integration - Integration test validation"
	@echo "  make check-tracer-patterns - Check for invalid tracer patterns"
	@echo "  make check-no-mocks  - Verify no mocks in integration tests"
	@echo ""
	@echo "SDK Generation:"
	@echo "  make generate        - Generate v1 client from full OpenAPI spec"
	@echo "  make generate-minimal - Generate v1 client from minimal spec (testing)"
	@echo "  make generate-sdk    - Generate full SDK to comparison_output/ (for analysis)"
	@echo "  make compare-sdk     - Compare generated SDK with current implementation"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-serve      - Serve API reference docs locally (http://127.0.0.1:8000)"
	@echo "  make docs-build      - Build API reference docs to site/"
	@echo ""
	@echo "Build:"
	@echo "  make build           - Build honeyhive package"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           - Remove build artifacts"
	@echo "  make clean-all       - Deep clean (includes venv)"

# Installation
install:
	$(UV_RUN) pip install -e .

install-dev:
	$(UV_RUN) pip install -e ".[dev]"

setup:
	./scripts/setup-dev.sh

# Testing
# Default test target runs tests that don't require external dependencies
# (no .env file, no Docker, no real API credentials needed)
# Uses parallel execution (-n auto) for speed
test:
	$(UV_RUN) pytest tests/unit/ tests/tracer/ tests/compatibility/ -n auto

test-all:
	$(UV_RUN) pytest -n auto

test-integration:
	$(UV_RUN) pytest tests/integration/

test-unit:
	$(UV_RUN) pytest tests/unit/ -n auto

check-integration:
	@echo "Running comprehensive integration test checks..."
	scripts/run-basic-integration-tests.sh

# Code Quality
format:
	$(UV_RUN) black src tests examples scripts
	$(UV_RUN) isort src tests examples scripts

lint:
	$(UV_RUN) tox -e lint

typecheck:
	$(UV_RUN) mypy src

check-format:
	$(UV_RUN) tox -e format

check-lint:
	$(UV_RUN) tox -e lint

# Comprehensive check - runs all quality checks
check: check-format check-lint test-unit check-no-mocks check-integration check-tracer-patterns
	@echo ""
	@echo "✅ All checks passed!"

check-tracer-patterns:
	scripts/validate-tracer-patterns.sh

check-no-mocks:
	scripts/validate-no-mocks-integration.sh

# SDK Generation
# Generate v1 client from full OpenAPI spec
generate:
	$(PYTHON) scripts/generate_client.py
	$(MAKE) format

# Generate v1 client from minimal spec (for testing pipeline)
generate-minimal:
	$(PYTHON) scripts/generate_client.py --minimal
	$(MAKE) format

# Generate full SDK to comparison_output/ (for analysis)
generate-sdk:
	$(PYTHON) scripts/generate_models_and_client.py

compare-sdk:
	@if [ ! -d "comparison_output/full_sdk" ]; then \
		echo "❌ No generated SDK found. Run 'make generate-sdk' first."; \
		exit 1; \
	fi
	$(PYTHON) comparison_output/full_sdk/compare_with_current.py

# Documentation (properdocs + mkdocstrings, AST-based — no SDK runtime deps required)
# Uses the `docs` optional-dependency group from pyproject.toml.
#
# We build with ProperDocs (a drop-in MkDocs 1.6 fork; see the comment above the
# `docs` group in pyproject.toml for rationale). The `properdocs` CLI accepts the
# same flags as `mkdocs` and reads properdocs.yml as its default config file.
#
# Note: --strict is intentionally omitted for now. There are pre-existing
# docstring/signature mismatches and a few malformed cross-refs in the source
# that surface as griffe warnings; cleaning them up is an explicit follow-up.
# Re-add --strict to docs-build once those are resolved so doc rot can't
# accumulate silently.
docs-serve:
	uv run --extra docs properdocs serve

docs-build:
	uv run --extra docs properdocs build

# Build
build:
	$(PYTHON) -m build

# Maintenance
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".tox" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ comparison_output/

clean-all: clean
	rm -rf .venv/ python-sdk/ .direnv/ .tox/

publish: build
	@echo "Publishing honeyhive to PyPI..."
	$(PYTHON) -m twine upload dist/*

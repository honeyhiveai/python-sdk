.PHONY: help install install-dev test test-all test-unit test-integration check-integration lint format check check-format check-lint typecheck check-docs check-docs-compliance check-feature-sync check-tracer-patterns check-no-mocks docs docs-serve docs-clean generate generate-sdk compare-sdk clean clean-all build build-bundled publish publish-bundled

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
	@echo "  make check-docs      - Build and validate documentation"
	@echo "  make check-docs-compliance - Check documentation compliance"
	@echo "  make check-feature-sync - Check feature documentation sync"
	@echo "  make check-tracer-patterns - Check for invalid tracer patterns"
	@echo "  make check-no-mocks  - Verify no mocks in integration tests"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs            - Build documentation"
	@echo "  make docs-serve      - Build and serve documentation"
	@echo "  make docs-clean      - Clean documentation build"
	@echo ""
	@echo "SDK Generation:"
	@echo "  make generate        - Generate v1 client from full OpenAPI spec"
	@echo "  make generate-minimal - Generate v1 client from minimal spec (testing)"
	@echo "  make generate-sdk    - Generate full SDK to comparison_output/ (for analysis)"
	@echo "  make compare-sdk     - Compare generated SDK with current implementation"
	@echo ""
	@echo "Build & Publish:"
	@echo "  make build           - Build honeyhive package"
	@echo "  make build-bundled   - Build honeyhive-bundled package"
	@echo "  make publish         - Publish honeyhive to PyPI"
	@echo "  make publish-bundled - Publish honeyhive-bundled to PyPI"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           - Remove build artifacts"
	@echo "  make clean-all       - Deep clean (includes venv)"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs]"

setup:
	./scripts/setup-dev.sh

# Testing
# Default test target runs tests that don't require external dependencies
# (no .env file, no Docker, no real API credentials needed)
# Uses parallel execution (-n auto) for speed
test:
	pytest tests/unit/ tests/tracer/ tests/compatibility/ -n auto

test-all:
	pytest -n auto

test-integration:
	pytest tests/integration/

test-unit:
	pytest tests/unit/ -n auto

check-integration:
	@echo "Running comprehensive integration test checks..."
	scripts/run-basic-integration-tests.sh

# Code Quality
format:
	black src tests examples scripts
	isort src tests examples scripts

lint:
	tox -e lint

typecheck:
	mypy src

check-format:
	tox -e format

check-lint:
	tox -e lint

# Comprehensive check - runs all quality checks
check: check-format check-lint test-unit check-no-mocks check-integration check-docs check-docs-compliance check-feature-sync check-tracer-patterns
	@echo ""
	@echo "✅ All checks passed!"

check-docs-compliance:
	python scripts/check-documentation-compliance.py

check-feature-sync:
	python scripts/check-feature-sync.py

check-tracer-patterns:
	scripts/validate-tracer-patterns.sh

check-no-mocks:
	scripts/validate-no-mocks-integration.sh

check-docs: docs
	@echo "Building and validating documentation..."
	scripts/validate-docs-navigation.sh

# Documentation
docs:
	cd docs && $(MAKE) html

docs-serve:
	cd docs && python serve.py

docs-clean:
	cd docs && $(MAKE) clean

# SDK Generation
# Generate v1 client from full OpenAPI spec
generate:
	python scripts/generate_client.py
	$(MAKE) format

# Generate v1 client from minimal spec (for testing pipeline)
generate-minimal:
	python scripts/generate_client.py --minimal
	$(MAKE) format

# Generate full SDK to comparison_output/ (for analysis)
generate-sdk:
	python scripts/generate_models_and_client.py

compare-sdk:
	@if [ ! -d "comparison_output/full_sdk" ]; then \
		echo "❌ No generated SDK found. Run 'make generate-sdk' first."; \
		exit 1; \
	fi
	python comparison_output/full_sdk/compare_with_current.py

# Build & Publish
build:
	python -m build

build-bundled:
	@echo "Building honeyhive-bundled package..."
	cp pyproject.toml pyproject.toml.backup
	cp pyproject.bundled.toml pyproject.toml
	python -m build
	mv pyproject.toml.backup pyproject.toml
	@echo "✅ Built honeyhive-bundled package in dist/"

publish:
	@echo "Publishing honeyhive to PyPI..."
	python -m twine upload dist/*

publish-bundled:
	@echo "Publishing honeyhive-bundled to PyPI..."
	cp pyproject.toml pyproject.toml.backup
	cp pyproject.bundled.toml pyproject.toml
	python -m build
	python -m twine upload dist/*
	mv pyproject.toml.backup pyproject.toml
	@echo "✅ Published honeyhive-bundled to PyPI"

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

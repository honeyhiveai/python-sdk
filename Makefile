.PHONY: help install install-dev test test-fast test-unit test-integration check-integration check-all lint format check typecheck check-docs check-docs-compliance check-feature-sync check-tracer-patterns check-no-mocks docs docs-serve docs-clean generate-sdk compare-sdk clean clean-all

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
	@echo "  make test            - Run all tests"
	@echo "  make test-fast       - Run tests in parallel"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make check-integration - Run comprehensive integration test checks"
	@echo "  make check-all       - Run ALL checks (tests + docs + compliance)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run linting checks"
	@echo "  make format          - Format code with black and isort"
	@echo "  make check           - Run format and lint checks"
	@echo "  make typecheck       - Run mypy type checking"
	@echo ""
	@echo "Comprehensive Checks (not in pre-commit):"
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
	@echo "  make generate-sdk    - Generate SDK from OpenAPI spec"
	@echo "  make compare-sdk     - Compare generated SDK with current implementation"
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
test:
	pytest

test-fast:
	pytest -n auto

test-integration:
	pytest tests/integration/

test-unit:
	pytest tests/unit/

check-integration:
	@echo "Running comprehensive integration test checks..."
	scripts/validate-no-mocks-integration.sh
	scripts/run-basic-integration-tests.sh

check-all: check check-docs check-integration
	@echo "✅ All checks passed!"

# Code Quality
lint:
	tox -e lint

format:
	black src tests
	isort src tests

check:
	tox -e format
	tox -e lint

typecheck:
	mypy src

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
generate-sdk:
	python scripts/generate_models_and_client.py

compare-sdk:
	@if [ ! -d "comparison_output/full_sdk" ]; then \
		echo "❌ No generated SDK found. Run 'make generate-sdk' first."; \
		exit 1; \
	fi
	python comparison_output/full_sdk/compare_with_current.py

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
	rm -rf .venv/ python-sdk/ .direnv/

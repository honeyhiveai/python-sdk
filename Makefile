.PHONY: help install install-dev test test-fast test-integration lint format check check-docs-compliance docs docs-serve generate-sdk compare-sdk clean

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
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-unit       - Run unit tests only"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run linting checks"
	@echo "  make format          - Format code with black and isort"
	@echo "  make check           - Run format and lint checks"
	@echo "  make typecheck       - Run mypy type checking"
	@echo "  make check-docs-compliance - Check documentation compliance (heavy)"
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

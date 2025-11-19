#!/bin/bash
# Basic Integration Tests for Pre-commit Hook
# Runs a minimal subset of integration tests with credential validation
# Part of the HoneyHive Python SDK Agent OS Zero Failing Tests Policy

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Basic Integration Tests (Pre-commit)${NC}"
echo "========================================"

# Check for required credentials
echo -e "${BLUE}🔑 Checking API credentials...${NC}"

if [[ -z "${HH_API_KEY:-}" ]]; then
    echo -e "${YELLOW}⚠️  HH_API_KEY not set - skipping integration tests${NC}"
    echo "   Integration tests require valid HoneyHive API credentials"
    echo "   Set HH_API_KEY environment variable to run integration tests"
    echo -e "${GREEN}✅ Pre-commit check passed (credentials not available)${NC}"
    exit 0
fi

if [[ -z "${HH_PROJECT:-}" ]]; then
    echo -e "${YELLOW}⚠️  HH_PROJECT not set - skipping integration tests${NC}"
    echo "   Integration tests require HH_PROJECT environment variable"
    echo "   Set HH_PROJECT environment variable to run integration tests"
    echo -e "${GREEN}✅ Pre-commit check passed (credentials not available)${NC}"
    exit 0
fi

echo -e "${GREEN}✅ API credentials found${NC}"

# Run basic integration tests (fast subset)
echo -e "${BLUE}🚀 Running basic integration tests...${NC}"

# Select a minimal set of fast integration tests
BASIC_TESTS=(
    "tests/integration/test_simple_integration.py::TestSimpleIntegration::test_environment_configuration"
    "tests/integration/test_simple_integration.py::TestSimpleIntegration::test_fixture_availability"
    "tests/integration/test_tracer_integration.py::TestTracerIntegration::test_tracer_initialization_integration"
)

echo "   Selected tests: ${#BASIC_TESTS[@]} fast integration tests"

# Run the basic tests with timeout
timeout 120s tox -e integration -- "${BASIC_TESTS[@]}" --tb=short -q || {
    echo -e "${RED}❌ Basic integration tests failed${NC}"
    echo ""
    echo "Integration tests are failing. This indicates:"
    echo "1. API credentials may be invalid or expired"
    echo "2. Core SDK functionality may be broken"
    echo "3. Environment configuration issues"
    echo ""
    echo "To fix:"
    echo "1. Verify HH_API_KEY and HH_PROJECT are valid"
    echo "2. Run 'tox -e integration' to see detailed errors"
    echo "3. Fix any failing tests before committing"
    echo ""
    echo "Or skip integration tests with: git commit --no-verify"
    echo "(Not recommended - violates Agent OS Zero Failing Tests Policy)"
    exit 1
}

echo -e "${GREEN}✅ Basic integration tests passed${NC}"
echo -e "${GREEN}🎉 Pre-commit integration test check complete${NC}"

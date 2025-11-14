#!/usr/bin/env bash
# Validate that integration tests don't use mocks
# Integration tests should use real dependencies, not mocks

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Checking for mocks in integration tests..."

# Find all integration test files
integration_files=$(find tests/integration -name "test_*.py" 2>/dev/null || true)

if [[ -z "$integration_files" ]]; then
    echo -e "${GREEN}✅ No integration tests found (or directory doesn't exist)${NC}"
    exit 0
fi

# Check for mock usage
violations=()

for file in $integration_files; do
    # Check for common mock patterns
    if grep -qE "(from unittest.mock import|from unittest import mock|@mock\.|@patch|Mock\(|MagicMock)" "$file"; then
        violations+=("$file")
    fi
done

if [[ ${#violations[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ No mocks found in integration tests${NC}"
    exit 0
else
    echo -e "${RED}❌ Integration tests should NOT use mocks (use real dependencies)${NC}"
    echo ""
    for file in "${violations[@]}"; do
        echo -e "  ${RED}✗${NC} $file"
        # Show the offending lines
        grep -n -E "(from unittest.mock import|from unittest import mock|@mock\.|@patch|Mock\(|MagicMock)" "$file" | head -3
    done
    echo ""
    echo -e "${YELLOW}Integration tests validate real system behavior.${NC}"
    echo -e "${YELLOW}Use unit tests for mocked testing.${NC}"
    exit 1
fi


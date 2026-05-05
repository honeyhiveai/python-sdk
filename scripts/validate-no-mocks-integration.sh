#!/bin/bash
# No Mocks in Integration Tests Validation Script
# Part of Integration Testing Consolidation
#
# This script ensures that integration tests use real systems and real APIs,
# preventing mock creep that can hide critical bugs like the ProxyTracerProvider issue.

set -e

echo "🔍 Checking for mocks in integration tests..."

# Use the comprehensive Python validation script
if python3 scripts/validate-no-mocks-integration.py; then
    echo "✅ No mocks found in integration tests"
    exit 0
else
    echo "❌ CRITICAL: Mock violations found in integration tests!"
    echo ""
    echo "🚨 NO MOCKS ALLOWED IN INTEGRATION TESTS"
    echo "Integration tests must use real systems and real APIs."
    echo ""
    echo "💡 Solutions:"
    echo "  1. Move mocked tests to tests/unit/ directory"
    echo "  2. Replace mocks with real API calls using test_mode=False"
    echo "  3. Use real credentials and skip tests if not available"
    echo ""
    echo "📋 Run 'python3 scripts/validate-no-mocks-integration.py --fix' to auto-move heavily mocked files"
    exit 1
fi

#!/bin/bash
# Documentation Navigation Validation Script
# Required by Agent OS standards: .agent-os/standards/best-practices.md
#
# This script validates that all documentation navigation links work correctly
# and that the toctree structure is complete and accurate.

set -e

echo "🔍 Validating documentation navigation (Agent OS requirement)..."

# Build documentation first
echo "📚 Building documentation..."
cd docs
if ! make html >/dev/null 2>&1; then
    echo "❌ Failed to build documentation"
    exit 1
fi

# Check if server is already running on port 8000
if curl -s http://localhost:8000 >/dev/null 2>&1; then
    echo "📡 Using existing documentation server on port 8000"
    cd ..
    if python docs/utils/validate_navigation.py --local; then
        echo "✅ Documentation navigation validation passed"
        exit 0
    else
        echo "❌ Documentation navigation validation failed"
        exit 1
    fi
else
    echo "🚀 Starting temporary documentation server..."
    if python serve.py &>/dev/null & SERVER_PID=$!; then
        # Give server time to start
        sleep 3
        cd ..
        
        # Run validation
        if python docs/utils/validate_navigation.py --local; then
            echo "✅ Documentation navigation validation passed"
            kill $SERVER_PID 2>/dev/null || true
            exit 0
        else
            echo "❌ Documentation navigation validation failed"
            kill $SERVER_PID 2>/dev/null || true
            exit 1
        fi
    else
        echo "❌ Failed to start documentation server"
        exit 1
    fi
fi

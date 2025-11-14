#!/bin/bash
# Documentation Navigation Validation Script
# Required by praxis OS standards: .praxis-os/standards/universal/best-practices.md
#
# This script validates that all documentation navigation links work correctly
# and that the toctree structure is complete and accurate.

set -e

echo "🔍 Validating documentation navigation (praxis OS requirement)..."

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Build documentation first
echo "📚 Building documentation..."
if ! tox -e docs >/dev/null 2>&1; then
    echo "❌ Failed to build documentation"
    exit 1
fi

# Check if server is already running on port 8000
if curl -s http://localhost:8000 >/dev/null 2>&1; then
    echo "📡 Using existing documentation server on port 8000"
    if python3 docs/utils/validate_navigation.py --local; then
        echo "✅ Documentation navigation validation passed"
        exit 0
    else
        echo "❌ Documentation navigation validation failed"
        exit 1
    fi
else
    echo "🚀 Starting temporary documentation server..."
    if python3 docs/serve.py &>/dev/null & SERVER_PID=$!; then
        # Give server time to start
        sleep 3
        
        # Run validation
        if python3 docs/utils/validate_navigation.py --local; then
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

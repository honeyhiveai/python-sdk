#!/bin/bash
# AWS Strands + HoneyHive Integration Test Runner
# 
# This script demonstrates how to run the AWS Strands integration tests
# in different configurations to verify HoneyHive's automatic instrumentation.

set -e  # Exit on any error

echo "🧪 AWS Strands + HoneyHive Integration Test Runner"
echo "=================================================="

# Check if HoneyHive API key is set
if [ -z "$HONEYHIVE_API_KEY" ]; then
    echo "❌ HONEYHIVE_API_KEY environment variable is required"
    echo "   Set it with: export HONEYHIVE_API_KEY='your-api-key'"
    exit 1
fi

echo "✅ HONEYHIVE_API_KEY is set"

# Check AWS credentials (optional but recommended)
echo ""
echo "🔑 Checking AWS Credentials..."
if aws sts get-caller-identity >/dev/null 2>&1; then
    echo "✅ AWS credentials are working"
    IDENTITY=$(aws sts get-caller-identity 2>/dev/null)
    ACCOUNT=$(echo "$IDENTITY" | grep -o '"Account": "[^"]*"' | cut -d'"' -f4)
    echo "   Account: $ACCOUNT"
    
    # Check region
    if [ -n "$AWS_REGION" ] || [ -n "$AWS_DEFAULT_REGION" ]; then
        REGION=${AWS_REGION:-$AWS_DEFAULT_REGION}
        echo "   Region: $REGION"
    else
        echo "   ⚠️  No AWS region set, using us-east-1"
        export AWS_REGION="us-east-1"
    fi
else
    echo "⚠️  AWS credentials not configured or not working"
    echo "   Tests will run in mock mode only"
    echo "   For full testing, configure AWS credentials:"
    echo "     - AWS SSO: aws configure sso && aws sso login"
    echo "     - Environment: export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=..."
    echo "     - AWS CLI: aws configure"
fi

# Check Python environment
echo ""
echo "🐍 Checking Python Environment..."
python --version
echo "   Python path: $(which python)"

# Check if we're in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "   Virtual environment: $VIRTUAL_ENV"
else
    echo "   ⚠️  Not in a virtual environment (recommended to use venv)"
fi

# Install test dependencies if needed
echo ""
echo "📦 Checking Dependencies..."

# Check for required packages
MISSING_PACKAGES=""

if ! python -c "import honeyhive" 2>/dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES honeyhive"
fi

if ! python -c "import opentelemetry" 2>/dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES opentelemetry-api opentelemetry-sdk"
fi

if [ -n "$MISSING_PACKAGES" ]; then
    echo "   📥 Installing missing packages:$MISSING_PACKAGES"
    pip install $MISSING_PACKAGES
else
    echo "   ✅ All required packages are installed"
fi

# Check for AWS Strands package (verified working pattern)
if python -c "from strands import Agent" 2>/dev/null; then
    echo "   ✅ AWS Strands package available"
    STRANDS_MODE="real"
else
    echo "   ⚠️  AWS Strands package not available - will use mock mode"
    echo "      Install with: pip install strands-agents"
    STRANDS_MODE="mock"
fi

# Run the comprehensive integration test
echo ""
echo "🔬 Running Comprehensive Integration Test..."
echo "----------------------------------------"
echo "Mode: $STRANDS_MODE"
echo ""

python test_strands_integration.py

TEST_EXIT_CODE=$?

# Run the basic example if test passed
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "📝 Running Basic Integration Example..."
    echo "------------------------------------"
    
    python examples/strands_integration.py
    EXAMPLE_EXIT_CODE=$?
else
    echo ""
    echo "❌ Comprehensive test failed, skipping example"
    EXAMPLE_EXIT_CODE=1
fi

# Summary
echo ""
echo "📊 Test Summary"
echo "=============="
echo "Comprehensive Test: $([ $TEST_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "Basic Example: $([ $EXAMPLE_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "Strands Mode: $STRANDS_MODE"

if [ $TEST_EXIT_CODE -eq 0 ] && [ $EXAMPLE_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! HoneyHive integration with AWS Strands is working correctly."
    echo ""
    echo "🔗 Next Steps:"
    echo "   1. View traces in HoneyHive dashboard: https://app.honeyhive.ai/"
    echo "   2. Check projects: 'strands-test-*' and 'strands-integration-example'"
    echo "   3. Install AWS Strands for full testing: pip install strands-agents[otel]"
    echo "   4. Set up AWS credentials for real Bedrock model testing"
    exit 0
else
    echo ""
    echo "❌ Some tests failed. Check the output above for details."
    exit 1
fi

#!/bin/bash
# Development environment setup script for HoneyHive Python SDK
# This ensures all developers have consistent tooling and pre-commit hooks

set -e

echo "🔧 Setting up HoneyHive Python SDK development environment..."

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Please activate your 'python-sdk' virtual environment first:"
    echo "   source python-sdk/bin/activate"
    exit 1
fi

# Verify virtual environment name
if [[ "$VIRTUAL_ENV" != *"python-sdk"* ]]; then
    echo "⚠️  Warning: Expected virtual environment named 'python-sdk', got: $VIRTUAL_ENV"
    echo "   Continue anyway? (y/N)"
    read -r response
    if [[ "$response" != "y" && "$response" != "Y" ]]; then
        exit 1
    fi
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -e .
pip install pre-commit>=3.6.0

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Verify tools are working
echo "🔍 Verifying development tools..."

echo "  - Black formatting..."
if ! black --check --quiet src tests 2>/dev/null; then
    echo "    ⚠️  Code needs formatting. Running black..."
    black src tests
fi

echo "  - Import sorting..."
if ! isort --check-only --quiet src tests 2>/dev/null; then
    echo "    ⚠️  Imports need sorting. Running isort..."
    isort src tests
fi

echo "  - Linting..."
tox -e lint -q

echo "  - Format check..."
tox -e format -q

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. All commits will now automatically run quality checks"
echo "  2. To manually run checks: tox -e lint && tox -e format"
echo "  3. To skip pre-commit hooks (emergency only): git commit --no-verify"
echo ""
echo "📚 More info:"
echo "  - praxis OS standards: .praxis-os/standards/"
echo "  - Testing guide: docs/TESTING.rst"
echo "  - Feature list: docs/FEATURE_LIST.rst"

#!/bin/bash
# Development environment setup script for HoneyHive Python SDK
# This ensures all developers have consistent tooling

set -e

# Skip setup if running in Nix shell (Nix handles everything automatically)
if [[ -n "$IN_NIX_SHELL" ]]; then
    echo "✨ Detected Nix shell environment - setup is handled automatically by flake.nix"
    echo "   No manual setup needed!"
    exit 0
fi

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

# Verify tools are working
echo "🔍 Verifying development tools..."

echo "  - Ruff formatting..."
if ! ruff format --check --quiet src tests 2>/dev/null; then
    echo "    ⚠️  Code needs formatting. Running ruff format..."
    ruff format src tests
fi

echo "  - Import sorting..."
if ! ruff check --select I --quiet src tests 2>/dev/null; then
    echo "    ⚠️  Imports need sorting. Running ruff isort fix..."
    ruff check --select I --fix src tests
fi

echo "  - Linting..."
tox -e lint -q

echo "  - Format check..."
tox -e format -q

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Run 'make check' to validate your changes before committing"
echo "  2. All checks will run in CI when you push"
echo "  3. Use 'make help' to see all available commands"

#!/bin/bash

echo "📦 Building Linux-compatible Lambda deployment package..."

# Create a clean bundle directory
rm -rf lambda-bundle
mkdir -p lambda-bundle

# Copy the HoneyHive SDK source
echo "📂 Copying HoneyHive SDK source..."
cp -r ../../src/honeyhive lambda-bundle/

# Copy Lambda functions
echo "📂 Copying Lambda functions..."
cp lambda_functions/*.py lambda-bundle/

# Install dependencies with Linux platform specification
echo "📦 Installing Linux-compatible dependencies to bundle..."
pip install --target lambda-bundle \
    --platform linux_x86_64 \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: \
    httpx \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-otlp-proto-http \
    wrapt \
    pydantic \
    python-dotenv \
    click \
    pyyaml

# Remove unnecessary files to reduce size
echo "🧹 Cleaning up bundle..."
find lambda-bundle -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find lambda-bundle -type f -name "*.pyc" -delete 2>/dev/null || true
find lambda-bundle -type f -name "*.pyo" -delete 2>/dev/null || true

# Show bundle structure
echo "📋 Bundle structure:"
ls -la lambda-bundle/ | head -20
echo ""
echo "📊 Bundle size:"
du -sh lambda-bundle/

echo "✅ Linux-compatible Lambda bundle created successfully!"

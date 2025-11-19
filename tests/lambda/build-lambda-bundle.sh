#!/bin/bash

echo "📦 Building Lambda deployment package..."

# Create a clean bundle directory
rm -rf lambda-bundle
mkdir -p lambda-bundle

# Copy the HoneyHive SDK source
echo "📂 Copying HoneyHive SDK source..."
cp -r ../../src/honeyhive lambda-bundle/

# Copy Lambda functions
echo "📂 Copying Lambda functions..."
cp lambda_functions/*.py lambda-bundle/

# Install dependencies to the bundle directory
echo "📦 Installing dependencies to bundle..."
pip install --target lambda-bundle \
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
ls -la lambda-bundle/
echo ""
echo "📊 Bundle size:"
du -sh lambda-bundle/

echo "✅ Lambda bundle created successfully!"

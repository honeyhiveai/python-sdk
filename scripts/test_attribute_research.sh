#!/bin/bash
# Quick validation test for span attribute research system

set -e  # Exit on error

echo "🧪 Testing Span Attribute Research System"
echo "=========================================="
echo ""

# Check environment variables
echo "📋 Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set"
    exit 1
fi
echo "✅ OPENAI_API_KEY set"

if [ -z "$HH_API_KEY" ]; then
    echo "⚠️  HH_API_KEY not set - using test key"
    export HH_API_KEY="test-key"
fi
echo "✅ HH_API_KEY set"

if [ -z "$HH_PROJECT" ]; then
    echo "⚠️  HH_PROJECT not set - using default"
    export HH_PROJECT="span-research-test"
fi
echo "✅ HH_PROJECT set: $HH_PROJECT"

echo ""
echo "🔬 Running minimal test: OpenInference + OpenAI + basic_chat"
echo "=============================================================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Run minimal research
python scripts/research_span_attributes.py \
    --instrumentors openinference \
    --providers openai \
    --scenarios basic_chat \
    --operations 2 \
    --output-dir span_attribute_captures_test

echo ""
echo "✅ Test complete! Check outputs:"
echo "   span_attribute_captures_test/"
echo ""

# Show summary
if [ -f span_attribute_captures_test/span_captures_*.json ]; then
    echo "📊 Capture files created:"
    ls -lh span_attribute_captures_test/*.json
    echo ""
    
    echo "📈 Quick stats:"
    python3 -c "
import json, glob
files = glob.glob('span_attribute_captures_test/span_captures_*.json')
if files:
    with open(files[0]) as f:
        data = json.load(f)
    print(f\"  Total spans: {data['capture_count']}\")
    if data['spans']:
        first_span = data['spans'][0]
        print(f\"  Instrumentor: {first_span['instrumentor']}\")
        print(f\"  Provider: {first_span['provider']}\")
        print(f\"  Scenario: {first_span['scenario']}\")
        print(f\"  Attributes captured: {len(first_span['attributes'])}\")
        print(f\"  Sample attributes: {list(first_span['attributes'].keys())[:5]}\")
"
else
    echo "⚠️  No capture files found"
fi

echo ""
echo "🎉 Validation successful! Ready for full research."

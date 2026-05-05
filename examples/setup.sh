#!/bin/bash

echo "🚀 Setting up HoneyHive SDK + Mock LLM Examples"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python and pip are available"

# Install HoneyHive SDK in development mode
echo "📦 Installing HoneyHive SDK in development mode..."
cd "$(dirname "$0")/.."
pip3 install -e .

if [ $? -eq 0 ]; then
    echo "✅ HoneyHive SDK installed successfully"
else
    echo "❌ Failed to install HoneyHive SDK"
    exit 1
fi

# Install OpenInference OpenAI instrumentation
echo "📦 Installing OpenInference OpenAI instrumentation..."
pip3 install openinference-instrumentation-openai

if [ $? -eq 0 ]; then
    echo "✅ OpenInference OpenAI instrumentation installed successfully"
else
    echo "❌ Failed to install OpenInference OpenAI instrumentation"
    echo "   This is optional but recommended for enhanced observability"
fi

# Check environment variables
echo "🔍 Checking environment variables..."

if [ -z "$HH_API_KEY" ]; then
    echo "⚠️  HH_API_KEY is not set"
    echo "   Set it with: export HH_API_KEY='your_honeyhive_api_key'"
else
    echo "✅ HH_API_KEY is set"
fi

if [ -z "$HH_SOURCE" ]; then
    echo "⚠️  HH_SOURCE is not set, will use 'production'"
    echo "   Set it with: export HH_SOURCE='your_source_name'"
else
    echo "✅ HH_SOURCE is set to: $HH_SOURCE"
fi

# Test basic import
echo "🧪 Testing basic imports..."
python3 -c "
try:
    from honeyhive.tracer import HoneyHiveTracer
    from honeyhive.api.client import HoneyHive
    print('✅ HoneyHive imports successful')
except ImportError as e:
    print(f'❌ HoneyHive import error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Basic import test failed"
    exit 1
fi

# Test OpenInference import
echo "🧪 Testing OpenInference imports..."
python3 -c "
try:
    from openinference.instrumentation.openai import OpenAIInstrumentor
    print('✅ OpenInference imports successful')
except ImportError as e:
    print(f'⚠️  OpenInference import error: {e}')
    print('   OpenInference is optional but recommended')
fi
"

# Test example files
echo "🧪 Testing example files..."
cd examples

# Test basic tracing example
echo "Testing basic tracing example..."
python3 -c "
import os
os.environ.setdefault('HH_API_KEY', 'test-key')
os.environ.setdefault('HH_SOURCE', 'test')

try:
    from basic_usage import main
    print('✅ Basic usage example test successful')
except Exception as e:
    print(f'❌ Basic usage example test failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Basic usage example test failed"
    exit 1
fi

# Test enhanced tracing demo
echo "Testing enhanced tracing demo..."
python3 -c "
import os
os.environ.setdefault('HH_API_KEY', 'test-key')
os.environ.setdefault('HH_SOURCE', 'test')

try:
    from enhanced_tracing_demo import main
    print('✅ Enhanced tracing demo test successful')
except Exception as e:
    print(f'❌ Enhanced tracing demo test failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Enhanced tracing demo test failed"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Set your HoneyHive API key:"
echo "   export HH_API_KEY='your_honeyhive_api_key'"
echo ""
echo "2. Set your source name:"
echo "   export HH_SOURCE='your_source_name'"
echo ""
echo "3. Run the examples:"
echo "   python3 basic_usage.py"
echo "   python3 enhanced_tracing_demo.py"
echo "   python3 openinference_openai_example.py"
echo ""
echo "📚 Check the README.md file for more details about the examples."

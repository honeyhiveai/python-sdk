# Google AI OpenInference Integration Example

This example demonstrates how to integrate OpenInference with Google AI SDK and our HoneyHive tracer instance, following the same pattern as the OpenAI example.

## 🚀 Features

- **Automatic OpenInference Integration**: Uses our enhanced HoneyHiveTracer with automatic instrumentor integration
- **Google AI SDK Support**: Demonstrates integration with `google.generativeai` library
- **Session-Aware Tracing**: Automatically creates HoneyHive sessions and includes session context in all spans
- **Comprehensive Demos**: Shows basic integration, vanilla tracer usage, advanced span management, and chat conversations
- **Zero Code Changes**: No modifications required to our SDK

## 📋 Prerequisites

1. **Google AI API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **HoneyHive Credentials**: Set up your `.env` file with HoneyHive credentials
3. **Python Dependencies**: Install required packages

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_google_ai.txt
   ```

2. **Set Environment Variables**:
   ```bash
   # Google AI API Key
   export GOOGLE_API_KEY="your-google-ai-api-key"
   
   # HoneyHive Credentials
   export HH_API_KEY="your-honeyhive-api-key"
   export HH_PROJECT="your-project-name"
   export HH_SOURCE="production"
   ```

## 🎯 Usage

### Basic Example

```python
from honeyhive.tracer import HoneyHiveTracer
from openinference.instrumentation.google import GoogleAIInstrumentor

# Initialize tracer with automatic Google AI instrumentation
tracer = HoneyHiveTracer(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT"),
    source=os.getenv("HH_SOURCE"),
    instrumentors=[GoogleAIInstrumentor()]  # Automatic integration
)

# Use Google AI normally - all calls automatically traced
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello, world!")
```

### Run the Full Example

```bash
cd examples
python openinference_google_ai_integration.py
```

## 🔍 What You Get

### Automatic Tracing
- All Google AI API calls automatically traced through OpenInference
- Spans enriched with HoneyHive session context
- No manual instrumentation required

### Session Management
- Automatic HoneyHive session creation during tracer initialization
- Session ID automatically included in all spans
- Session enrichment capabilities

### Comprehensive Observability
- Hierarchical span structure for complex workflows
- Events created for each AI interaction
- Business-specific attributes and metadata
- Complete trace visibility in HoneyHive

## 📊 Demo Scenarios

1. **Basic Integration**: Simple Google AI API call with automatic tracing
2. **Vanilla Tracer**: Custom spans with OpenInference enrichment
3. **Advanced Workflows**: Multi-step AI processing with hierarchical spans
4. **Chat Conversations**: Multi-turn conversations with context tracking
5. **Session Enrichment**: Adding metadata and user properties

## 🔧 Configuration

The example automatically handles:
- OpenInference instrumentation setup
- HoneyHive tracer configuration
- Session creation and management
- Span attribute enrichment
- Event creation and tracking

## 🌟 Key Benefits

- **Zero Code Changes**: Uses only vanilla tracer and spans
- **Automatic Integration**: OpenInference integration happens during tracer initialization
- **Session Awareness**: All spans automatically include session context
- **Provider Agnostic**: No Google AI specific code in our SDK
- **Complete Observability**: Full trace visibility and event tracking

## 📚 Related Examples

- [OpenAI Integration](openinference_integration_simple.py) - Similar pattern with OpenAI
- [Basic Usage](basic_usage.py) - Core SDK functionality
- [Enhanced Tracing](enhanced_tracing_demo.py) - Advanced tracing features

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Key Issues**: Verify `GOOGLE_API_KEY` is set correctly
3. **HoneyHive Connection**: Check `HH_API_KEY` and network connectivity

### Debug Mode

Enable debug logging by setting:
```bash
export HH_DEBUG_MODE=true
```

## 📖 Learn More

- [Google AI SDK Documentation](https://ai.google.dev/docs)
- [OpenInference Documentation](https://github.com/Arize-ai/openinference)
- [HoneyHive Documentation](https://docs.honeyhive.ai)

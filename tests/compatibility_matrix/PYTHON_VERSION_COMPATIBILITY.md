# HoneyHive Python Version Compatibility Matrix

*Generated on: 2025-09-05 04:07:48*

This document provides comprehensive compatibility information for the HoneyHive Python SDK
and various instrumentors across supported Python versions.

## HoneyHive SDK Python Version Support

The **HoneyHive Python SDK** officially supports the following Python versions:

**Supported Versions**: Python 3.11, 3.12, 3.13
**Minimum Version**: Python 3.11 (as defined in pyproject.toml)
**Recommended Version**: Python 3.12 (optimal compatibility and performance)
**Latest Tested**: Python 3.13 (cutting-edge features)

### HoneyHive SDK Compatibility

| Python Version | HoneyHive SDK Support | Notes | End of Life |
|----------------|----------------------|-------|-------------|
| Python 3.11 | ✅ Fully Supported | Minimum supported version | 2027-10 |
| Python 3.12 | ✅ Fully Supported | Recommended version | 2028-10 |
| Python 3.13 | ✅ Fully Supported | Latest supported version | 2029-10 |

*Note: HoneyHive SDK requires Python >=3.11 as specified in `pyproject.toml`*

## Instrumentor Compatibility Matrix

The following table shows **individual instrumentor** compatibility with different Python versions.
Each instrumentor may have its own Python version requirements separate from the HoneyHive SDK.

**Status Legend:**
- **✅ Compatible**: Works out of the box
- **✅ Compatible (Requires Workaround)**: Works with documented workaround
- **⚠️ Unknown**: Compatibility not verified

| Instrumentor | Python 3.11 | Python 3.12 | Python 3.13 | Notes |
|--------------|--------------|--------------|--------------|-------|
| `openinference-instrumentation-anthropic` | ✅ Compatible | ✅ Compatible | ✅ Compatible | OpenInference packages typically support Python 3.8+ |
| `openinference-instrumentation-bedrock` | ✅ Compatible | ✅ Compatible | ✅ Compatible | OpenInference packages typically support Python 3.8+ |
| `openinference-instrumentation-google-adk` | ✅ Compatible | ✅ Compatible | ✅ Compatible | OpenInference packages typically support Python 3.8+ |
| `openinference-instrumentation-google-generativeai` | ✅ Compatible | ✅ Compatible | ✅ Compatible | OpenInference packages typically support Python 3.8+ |
| `openinference-instrumentation-mcp` | ✅ Compatible | ✅ Compatible | ✅ Compatible | Verified compatible (installed and importable) |
| `openinference-instrumentation-openai` | ✅ Compatible | ✅ Compatible | ✅ Compatible | OpenInference packages typically support Python 3.8+ |
| `opentelemetry-instrumentation-anthropic` | ✅ Compatible | ✅ Compatible | ✅ Compatible | Verified compatible (installed and importable) |
| `opentelemetry-instrumentation-bedrock` | ✅ Compatible | ✅ Compatible | ✅ Compatible | Verified compatible (installed and importable) |
| `opentelemetry-instrumentation-google-generativeai` | ✅ Compatible (Requires Workaround) | ✅ Compatible (Requires Workaround) | ✅ Compatible (Requires Workaround) | Requires documented workaround for upstream import bug |
| `opentelemetry-instrumentation-mcp` | ✅ Compatible | ✅ Compatible | ✅ Compatible | Verified compatible (installed and importable) |
| `opentelemetry-instrumentation-openai` | ✅ Compatible | ✅ Compatible | ✅ Compatible | Verified compatible (installed and importable) |

### Instrumentors Requiring Workarounds

Some instrumentors require workarounds due to upstream bugs or compatibility issues:

**OpenTelemetry Google AI (`opentelemetry-instrumentation-google-generativeai`)**:
- **Issue**: Upstream bug with incorrect import path (`google.genai.types` vs `google.generativeai.types`)
- **Workaround**: See `examples/traceloop_google_ai_example_with_workaround.py`
- **Status**: Fully functional with workaround applied

## Test Results by Python Version

*Test results will be populated after running compatibility tests.*

To generate test results, run:
```bash
tox -e compatibility-all
```

## Compatibility Recommendations

### For Production Use
- **Recommended**: Python 3.12 for optimal compatibility and performance
- **Minimum**: Python 3.11 for basic functionality
- **Latest**: Python 3.13 for cutting-edge features (test thoroughly)

### Instrumentor Selection by Python Version

#### Python 3.11+
**OpenInference Instrumentors:**
- `openinference-instrumentation-anthropic` - Anthropic models
- `openinference-instrumentation-bedrock` - AWS Bedrock models
- `openinference-instrumentation-google-adk` - Google Agent Development Kit models
- `openinference-instrumentation-google-generativeai` - Google Generative AI models
- `openinference-instrumentation-mcp` - Model Context Protocol models
- `openinference-instrumentation-openai` - OpenAI models

**OpenTelemetry Instrumentors (via Traceloop):**
- `opentelemetry-instrumentation-anthropic` - Enhanced Anthropic tracing
- `opentelemetry-instrumentation-bedrock` - Enhanced AWS Bedrock tracing
- `opentelemetry-instrumentation-google-generativeai` - Enhanced Google AI tracing
- `opentelemetry-instrumentation-mcp` - Enhanced Model Context Protocol tracing
- `opentelemetry-instrumentation-openai` - Enhanced OpenAI tracing

#### Python 3.12+
**Recommended Setup:**
```python
# Core instrumentors that work reliably
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor
from openinference.instrumentation.bedrock import BedrockInstrumentor
from honeyhive import HoneyHiveTracer

# Initialize with multiple instrumentors
tracer = HoneyHiveTracer.init(
    api_key='your-key',
    instrumentors=[
        OpenAIInstrumentor(),
        AnthropicInstrumentor(),
        BedrockInstrumentor(),
    ]
)
```

## Migration Guide

### Upgrading from Python 3.10 or Earlier
1. **Upgrade Python**: Install Python 3.11 or later
2. **Update Dependencies**: Some packages may need newer versions
3. **Test Thoroughly**: Run full compatibility test suite
4. **Update CI/CD**: Ensure build systems use supported Python versions

### Provider-Specific Notes

#### Multi-Provider Setup
- **Recommendation**: Use both OpenInference and OpenTelemetry instrumentors for comprehensive coverage
- **Best Practice**: Initialize all needed instrumentors during tracer setup
- **Performance**: OpenInference instrumentors are optimized for observability

## Testing Compatibility

### Test Specific Python Version
```bash
# Test on Python 3.11
tox -e compatibility-py311

# Test on Python 3.12
tox -e compatibility-py312

# Test on Python 3.13
tox -e compatibility-py313
```

### Test All Versions
```bash
# Run comprehensive compatibility testing
tox -e compatibility-all

# This will:
# 1. Test each Python version separately
# 2. Generate version-specific reports
# 3. Create this consolidated matrix
```

## Troubleshooting

### Common Issues

#### Package Not Available for Python Version
```
ERROR: Could not find a version that satisfies the requirement
```
**Solution**: Check the compatibility matrix above and use alternative instrumentors.

#### Import Errors
```python
ImportError: cannot import name 'X' from 'Y'
```
**Solution**: Ensure you're using compatible package versions for your Python version.

### Getting Help
- **Documentation**: Check [HoneyHive Docs](https://docs.honeyhive.ai)
- **Issues**: Report compatibility issues on [GitHub](https://github.com/honeyhiveai/python-sdk)
- **Community**: Join our [Discord](https://discord.gg/honeyhive) for support

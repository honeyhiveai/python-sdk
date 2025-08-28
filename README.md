# HoneyHive Python SDK

A comprehensive Python SDK for HoneyHive, providing LLM observability, evaluation, and tracing capabilities with OpenTelemetry integration.

## 🚀 Features

- **OpenTelemetry Integration** - Full OTEL compliance with custom span processor and exporter
- **Automatic Session Management** - Seamless session creation and management
- **Decorator Support** - Easy-to-use `@trace`, `@atrace`, and `@trace_class` decorators
- **Context Managers** - `start_span` and `enrich_span` for manual span management
- **HTTP Instrumentation** - Automatic HTTP request tracing
- **Baggage Support** - Context propagation across service boundaries
- **Real-time API Integration** - Direct integration with HoneyHive backend services
- **Comprehensive Testing** - Full test suite with 203 passing tests

## 📦 Installation

```bash
pip install honeyhive
```

### Development Installation

```bash
git clone https://github.com/honeyhiveai/sample.git
cd sample
pip install -e .
```

## 🔧 Quick Start

### Basic Usage

```python
from honeyhive import HoneyHiveTracer, trace

# Initialize tracer (automatically creates session)
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="your-project",
    source="production"
)

# Use decorator for automatic tracing
@trace
def my_function():
    return "Hello, World!"

# Manual span management
with tracer.start_span("custom-operation"):
    # Your code here
    pass
```

### OpenInference Integration

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Initialize tracer with OpenInference instrumentor
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="your-project",
    source="production",
    instrumentors=[OpenAIInstrumentor()]
)

# OpenInference automatically traces OpenAI calls
import openai
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## 🏗️ Architecture

### Core Components

```
src/honeyhive/
├── api/                    # API client implementations
│   ├── client.py          # Main API client
│   ├── configurations.py  # Configuration management
│   ├── datapoints.py      # Data point operations
│   ├── datasets.py        # Dataset operations
│   ├── events.py          # Event management
│   ├── evaluations.py     # Evaluation operations
│   ├── metrics.py         # Metrics operations
│   ├── projects.py        # Project management
│   ├── session.py         # Session operations
│   └── tools.py           # Tool operations
├── tracer/                 # OpenTelemetry integration
│   ├── otel_tracer.py     # Main tracer implementation
│   ├── span_processor.py  # Custom span processor
│   ├── span_exporter.py   # Custom span exporter
│   ├── decorators.py      # Tracing decorators
│   └── http_instrumentation.py # HTTP request tracing
├── evaluation/             # Evaluation framework
│   └── evaluators.py      # Evaluation decorators
├── models/                 # Pydantic models
│   └── generated.py       # Auto-generated from OpenAPI
└── utils/                  # Utility functions
    ├── config.py          # Configuration management
    ├── connection_pool.py # HTTP connection pooling
    ├── retry.py           # Retry mechanisms
    └── logger.py          # Logging utilities
```

### Key Design Principles

1. **Singleton Pattern** - Single tracer instance per application
2. **Environment Configuration** - Flexible configuration via environment variables
3. **Graceful Degradation** - Fallback mechanisms for missing dependencies
4. **Test Isolation** - Comprehensive test suite with proper isolation
5. **OpenTelemetry Compliance** - Full OTEL standard compliance

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HH_API_KEY` | HoneyHive API key | Required |
| `HH_API_URL` | API base URL | `https://api.honeyhive.ai` |
| `HH_PROJECT` | Project name | `default` |
| `HH_SOURCE` | Source environment | `production` |
| `HH_TEST_MODE` | Enable test mode | `false` |
| `HH_DISABLE_TRACING` | Disable tracing | `false` |
| `HH_DISABLE_HTTP_TRACING` | Disable HTTP instrumentation | `false` |
| `HH_OTLP_ENABLED` | Enable OTLP export | `true` |

### Configuration File

```python
from honeyhive.utils.config import get_config

config = get_config()
print(f"API Key: {config.api_key}")
print(f"Project: {config.project}")
print(f"Source: {config.source}")
```

## 🔍 Tracing Features

### Automatic Session Creation

The tracer automatically creates a HoneyHive session during initialization:

```python
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="your-project",
    source="production"
)
# Session is automatically created and managed
```

### Decorator Support

#### Function Tracing

```python
from honeyhive import trace, atrace

@trace
def sync_function():
    return "synchronous result"

@atrace
async def async_function():
    return "asynchronous result"
```

#### Class Tracing

```python
from honeyhive import trace_class

@trace_class
class MyClass:
    def method1(self):
        return "method 1"
    
    def method2(self):
        return "method 2"
```

### Manual Span Management

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer()

# Create spans manually
with tracer.start_span("operation-name", attributes={"key": "value"}):
    # Your code here
    pass

# Enrich existing spans
with tracer.enrich_span("enrichment", {"additional": "data"}):
    # Your code here
    pass
```

### Context Managers

```python
# Start a new span
with tracer.start_span("database-query") as span:
    span.set_attribute("db.system", "postgresql")
    span.set_attribute("db.statement", "SELECT * FROM users")
    # Execute database query

# Enrich current span
with tracer.enrich_span("data-processing", {"batch_size": 1000}):
    # Process data
    pass
```

## 🌐 HTTP Instrumentation

### Automatic HTTP Tracing

HTTP requests are automatically traced when enabled:

```python
import httpx
import requests

# These requests are automatically traced
response = httpx.get("https://api.example.com/data")
response = requests.get("https://api.example.com/data")
```

### Disabling HTTP Instrumentation

```bash
export HH_DISABLE_HTTP_TRACING=true
```

## 📊 Span Attributes

### Standard Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `honeyhive.session_id` | Session identifier | `"sess_123456"` |
| `honeyhive.project` | Project name | `"my-project"` |
| `honeyhive.source` | Source environment | `"production"` |
| `honeyhive.parent_id` | Parent span ID | `"span_789"` |
| `honeyhive_event_type` | Event type | `"model_inference"` |
| `honeyhive_inputs` | Input data | `{"prompt": "Hello"}` |
| `honeyhive_outputs` | Output data | `{"response": "Hi!"}` |
| `honeyhive_error` | Error information | `"Connection failed"` |

### Legacy Compatibility

For backend compatibility, the following attributes are also set:

| Attribute | Description |
|-----------|-------------|
| `traceloop.association.properties.session_id` | Session ID (legacy format) |
| `traceloop.association.properties.project` | Project (legacy format) |
| `traceloop.association.properties.source` | Source (legacy format) |
| `traceloop.association.properties.parent_id` | Parent ID (legacy format) |

## 🔌 OpenTelemetry Integration

### Custom Span Processor

The `HoneyHiveSpanProcessor` automatically enriches spans with:

- Session context from baggage
- Project and source information
- Legacy attribute compatibility
- Error handling and validation

### OTLP Export

Spans are exported to your backend service via OTLP:

```python
# Configure OTLP endpoint
otlp_endpoint = f"{config.api_url}/opentelemetry/v1/traces"

# Headers include authentication and context
headers = {
    "Authorization": f"Bearer {api_key}",
    "X-Project": project,
    "X-Source": source
}
```

### Disabling OTLP During Tests

```bash
export HH_OTLP_ENABLED=false
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with tox (recommended)
tox
```

### Test Categories

- **Unit Tests** (203 tests) - Core functionality testing
- **Integration Tests** (8 tests) - API integration testing
- **Tracer Tests** - OpenTelemetry integration testing
- **CLI Tests** - Command-line interface testing
- **API Tests** - API client testing

### Test Environment

Tests automatically configure:
- Test mode enabled
- HTTP instrumentation disabled
- OTLP export disabled
- Mocked external dependencies

## 📚 Documentation

For comprehensive documentation, please refer to the [docs/](docs/) directory:

- **[Documentation Index](docs/index.md)** - Quick navigation to all docs
- **[API Reference](docs/API_REFERENCE.md)** - Complete API reference with examples
- **[Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)** - Technical implementation details
- **[OpenInference Integration](docs/OPENINFERENCE_INTEGRATION.md)** - Using SDK with OpenInference instrumentors
- **[Documentation Overview](docs/README.md)** - Detailed documentation guide

## 🚀 Performance Considerations

### Span Processing

- **Efficient Attribute Setting** - Batch attribute operations
- **Context Caching** - Minimize context lookups
- **Early Exit Logic** - Skip processing when not needed
- **Memory Management** - Proper cleanup of resources

### HTTP Instrumentation

- **Conditional Application** - Only when enabled
- **Graceful Fallbacks** - Handle missing dependencies
- **Performance Monitoring** - Built-in performance metrics

## 🔒 Security

### API Key Management

- **Environment Variables** - Secure key storage
- **Test Mode** - Safe testing without real credentials
- **Header Authentication** - Bearer token authentication
- **Secure Transmission** - HTTPS-only communication

### Data Privacy

- **Local Processing** - Sensitive data stays local
- **Configurable Sampling** - Control data volume
- **Audit Logging** - Track data access

## 🛠️ Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/honeyhiveai/sample.git
cd sample

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
tox
```

### Code Quality

- **Type Hints** - Full type annotation support
- **Linting** - Pylint configuration included
- **Formatting** - Black code formatting
- **Testing** - Comprehensive test coverage

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📖 Examples

For comprehensive examples and use cases, please refer to:

- **[Examples Guide](docs/examples/README.md)** - Practical usage patterns and examples
- **[API Reference](docs/API_REFERENCE.md)** - Detailed examples with each API component

## 🐛 Troubleshooting

### Common Issues

#### HTTP Instrumentation Errors

```bash
# Disable HTTP instrumentation
export HH_DISABLE_HTTP_TRACING=true
```

#### OTLP Export Errors

```bash
# Disable OTLP export
export HH_OTLP_ENABLED=false
```

#### Session Creation Failures

```python
# Check API key and project configuration
tracer = HoneyHiveTracer(
    api_key="valid-api-key",
    project="valid-project",
    source="production"
)
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Initialize tracer with debug output
tracer = HoneyHiveTracer(debug=True)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: [https://docs.honeyhive.ai](https://docs.honeyhive.ai)
- **Issues**: [GitHub Issues](https://github.com/honeyhiveai/sample/issues)
- **Discussions**: [GitHub Discussions](https://github.com/honeyhiveai/sample/discussions)
- **Email**: support@honeyhive.ai

## 🙏 Acknowledgments

- OpenTelemetry community for the excellent tracing framework
- OpenInference for seamless instrumentation integration
- Pydantic for robust data validation
- Pytest for comprehensive testing framework

---

**Built with ❤️ by the HoneyHive team**

# HoneyHive Python SDK

A comprehensive Python SDK for HoneyHive, providing LLM observability, evaluation, and tracing capabilities with OpenTelemetry integration.

## 🚀 Features

- **OpenTelemetry Integration** - Full OTEL compliance with custom span processor and exporter
- **Automatic Session Management** - Seamless session creation and management
- **Decorator Support** - Easy-to-use `@trace` (unified sync/async), `@atrace`, and `@trace_class` decorators
- **Context Managers** - `start_span` and `enrich_span` for manual span management
- **HTTP Instrumentation** - Automatic HTTP request tracing
- **Baggage Support** - Context propagation across service boundaries
- **Experiment Harness Integration** - Automatic experiment tracking with MLflow, Weights & Biases, and Comet support
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
from honeyhive import HoneyHiveTracer
from honeyhive.tracer.decorators import trace

# Initialize tracer using the recommended init method
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="production"
)

# Use unified decorator for automatic tracing (works with both sync and async)
@trace(event_type="demo", event_name="my_function")
def my_function():
    return "Hello, World!"

@trace(event_type="demo", event_name="my_async_function")
async def my_async_function():
    await asyncio.sleep(0.1)
    return "Hello, Async World!"

# Manual span management
with tracer.start_span("custom-operation"):
    # Your code here
    pass

# With HTTP tracing enabled
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="production",
    disable_http_tracing=False
)
```

### Initialization

**The `HoneyHiveTracer.init()` method is the recommended way to initialize the tracer:**

```python
from honeyhive import HoneyHiveTracer

# Standard initialization
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="production"
)

# With custom server URL for self-hosted deployments
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="production",
    server_url="https://custom-server.com"
)
```

#### **Enhanced Features Available**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# All features are available in the init method
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="production",
    test_mode=True,  # Test mode support
    instrumentors=[OpenAIInstrumentor()],  # Auto-integration
    disable_http_tracing=True  # Performance control
)
```

**✅ The init method now supports ALL constructor features!**

### OpenInference Integration

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Initialize tracer with OpenInference instrumentor (recommended pattern)
tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="production",
    instrumentors=[OpenAIInstrumentor()]  # Auto-integration
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
| `HH_DISABLE_TRACING` | Disable tracing completely | `false` |
| `HH_DISABLE_HTTP_TRACING` | Disable HTTP request tracing | `false` |
| `HH_TEST_MODE` | Enable test mode | `false` |
| `HH_DEBUG_MODE` | Enable debug mode | `false` |
| `HH_VERBOSE` | Enable verbose API logging | `false` |
| `HH_OTLP_ENABLED` | Enable OTLP export | `true` |

#### Experiment Harness Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HH_EXPERIMENT_ID` | Unique experiment identifier | `None` |
| `HH_EXPERIMENT_NAME` | Human-readable experiment name | `None` |
| `HH_EXPERIMENT_VARIANT` | Experiment variant/treatment | `None` |
| `HH_EXPERIMENT_GROUP` | Experiment group/cohort | `None` |
| `HH_EXPERIMENT_METADATA` | JSON experiment metadata | `None` |

#### HTTP Client Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `HH_MAX_CONNECTIONS` | Maximum HTTP connections | `100` |
| `HH_MAX_KEEPALIVE_CONNECTIONS` | Keepalive connections | `20` |
| `HH_KEEPALIVE_EXPIRY` | Keepalive expiry (seconds) | `30.0` |
| `HH_POOL_TIMEOUT` | Connection pool timeout | `30.0` |
| `HH_RATE_LIMIT_CALLS` | Rate limit calls per window | `1000` |
| `HH_RATE_LIMIT_WINDOW` | Rate limit window (seconds) | `60.0` |
| `HH_HTTP_PROXY` | HTTP proxy URL | `None` |
| `HH_HTTPS_PROXY` | HTTPS proxy URL | `None` |
| `HH_NO_PROXY` | Proxy bypass list | `None` |
| `HH_VERIFY_SSL` | SSL verification | `true`
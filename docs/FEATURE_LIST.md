# HoneyHive Python SDK Feature List

A comprehensive overview of all features available in the HoneyHive Python SDK.

## 🚀 **Core Features**

### **Primary Initialization Pattern**
- **`HoneyHiveTracer.init()`** - Official SDK pattern (recommended)
  - Matches docs.honeyhive.ai exactly
  - Supports self-hosted deployments with `server_url` parameter
  - Environment variable integration
  - Automatic singleton management

### **Alternative Initialization Pattern**
- **Constructor-based initialization** - Enhanced pattern with additional options
  - `test_mode` for development and testing
  - `instrumentors` for OpenInference integration
  - Additional configuration options

### **Tracing Decorators**
- **`@trace`** - Primary decorator for all functions (recommended)
  - Automatically handles both sync and async functions
  - Unified API for all tracing needs
  - Full attribute and metadata support
- **`@atrace`** - Alternative async decorator
- **`@trace_class`** - Automatic method tracing for classes

### **Manual Span Management**
- **`start_span()`** - Create custom spans
- **`enrich_span()`** - Add attributes to existing spans
- **`enrich_session()`** - Session-level enrichment

### **API Client**
- **HTTP Client**: Async-capable HTTP client with connection pooling
- **Authentication**: API key-based authentication
- **Rate Limiting**: Built-in rate limiting and retry logic
- **Error Handling**: Comprehensive error handling and logging
- **Session Management**: Create, manage, and track sessions
- **Event Logging**: Log events with rich metadata

### **Tracing & Observability**
- **OpenTelemetry Integration**: Full OpenTelemetry compliance
- **Span Management**: Create, manage, and track spans
- **Context Propagation**: Automatic context propagation across operations
- **Baggage Support**: Custom metadata propagation
- **HTTP Instrumentation**: Automatic HTTP request tracing
- **Decorators**: 
  - `@dynamic_trace` - **NEW**: Unified decorator for both sync and async functions
  - `@trace` - Legacy decorator for synchronous functions
  - `@atrace` - Legacy decorator for asynchronous functions
  - `@trace_class` - Class-level tracing decorator
- **Context Managers**: Span context management
- **Experiment Tracking**: Automatic experiment context injection into all spans
- **Span Enrichment**: Automatic addition of experiment ID, name, variant, group, and metadata

### **Configuration Management**
- **Environment Variables**: Support for `HH_*` environment variables
- **Dynamic Reloading**: Runtime configuration updates
- **Project Management**: Multi-project support
- **Source Tracking**: Environment and source identification
- **HTTP Client Configuration**: Configurable connection pooling, rate limiting, and proxy settings
- **Experiment Harness Integration**: Support for MLflow, Weights & Biases, Comet, and standard experiment variables

## **Provider Integrations**

### **LLM Providers**
- **OpenAI**: OpenAI API integration with automatic tracing
- **Anthropic**: Anthropic Claude API integration with tracing
- **Custom Providers**: Framework for wrapping any LLM provider

### **Experiment Harness Integration**
- **MLflow**: Automatic detection of `MLFLOW_EXPERIMENT_ID` and `MLFLOW_EXPERIMENT_NAME`
- **Weights & Biases**: Automatic detection of `WANDB_RUN_ID` and `WANDB_PROJECT`
- **Comet**: Automatic detection of `COMET_EXPERIMENT_KEY` and `COMET_PROJECT_NAME`
- **Standard Variables**: Support for `EXPERIMENT_ID`, `EXPERIMENT_NAME`, `EXPERIMENT_VARIANT`, `EXPERIMENT_GROUP`
- **Metadata Parsing**: Support for JSON, key-value, and comma-separated metadata formats
- **Automatic Span Enrichment**: All spans automatically include experiment context

### **Framework Integrations**
- **FastAPI**: Middleware and utilities for FastAPI applications
- **Flask**: Middleware and utilities for Flask applications
- **Django**: Middleware and utilities for Django applications
- **LangChain**: Callback handlers and decorators for LangChain
- **LlamaIndex**: Callback handlers and decorators for LlamaIndex

## **Advanced Features**

### **Connection Management**
- **Connection Pooling**: Efficient HTTP connection reuse
- **Keep-Alive**: Connection keep-alive management
- **Timeout Handling**: Configurable timeouts and retries
- **Cleanup**: Automatic connection cleanup and resource management

### **Caching**
- **In-Memory Cache**: Fast in-memory caching with TTL
- **LRU Eviction**: Least-recently-used cache eviction
- **Size Limits**: Configurable cache size limits
- **Function Caching**: `@cache` and `@acache` decorators

### **Utilities**
- **Logging**: Structured logging with custom formatters
- **Retry Logic**: Exponential backoff and retry strategies
- **Validation**: Data validation and type checking
- **Serialization**: JSON serialization and deserialization

## **Development & Testing**

### **Testing Support**
- **Tox Integration**: Multi-Python version testing
- **Pytest Support**: Full pytest integration with fixtures
- **Mock Support**: Comprehensive mocking and testing utilities
- **Integration Tests**: Real API integration testing

### **Development Tools**
- **CLI Interface**: Command-line interface for common operations
- **Code Quality**: Black, isort, flake8, mypy integration
- **Documentation**: Comprehensive docstrings and examples
- **Type Hints**: Full type annotation support

## **Performance & Reliability**

### **Performance Features**
- **Async Support**: Full async/await support
- **Connection Reuse**: Efficient HTTP connection management
- **Batch Operations**: Support for batch API operations
- **Streaming**: Support for streaming responses

### **Reliability Features**
- **Error Recovery**: Automatic error recovery and retry
- **Circuit Breaker**: Protection against cascading failures
- **Health Checks**: Built-in health check endpoints
- **Monitoring**: Comprehensive metrics and monitoring

## **Deployment & Operations**

### **Configuration**
- **Environment-Based**: Environment-specific configuration
- **Secrets Management**: Secure API key management
- **Validation**: Configuration validation and error checking
- **Defaults**: Sensible defaults with override capability

### **Monitoring**
- **Metrics Collection**: Built-in metrics collection
- **Health Monitoring**: Application health monitoring
- **Alerting**: Configurable alerting and notifications
- **Dashboard Integration**: HoneyHive dashboard integration

## **Security Features**

### **Authentication & Authorization**
- **API Key Security**: Secure API key handling
- **Request Signing**: Request signature validation
- **Rate Limiting**: Protection against abuse
- **Audit Logging**: Comprehensive audit trail

### **Data Protection**
- **PII Handling**: Personal identifiable information protection
- **Encryption**: Data encryption in transit and at rest
- **Access Control**: Fine-grained access control
- **Compliance**: GDPR and privacy compliance support

## **Extensibility**

### **Plugin System**
- **Custom Providers**: Easy integration of new LLM providers
- **Custom Tracers**: Extensible tracing and observability
- **Custom Formatters**: Customizable logging and output formats
- **Middleware Support**: Custom middleware integration

### **Integration Points**
- **Webhook Support**: Webhook integration capabilities
- **API Extensions**: Extensible API client architecture
- **Event System**: Custom event handling and processing
- **Plugin Architecture**: Modular plugin system

## **Documentation & Support**

### **Documentation**
- **API Reference**: Comprehensive API documentation
- **Examples**: Practical usage examples and tutorials
- **Best Practices**: Development and deployment best practices
- **Troubleshooting**: Common issues and solutions

### **Support**
- **Community**: Active community support and discussions
- **Issues**: GitHub issue tracking and resolution
- **Contributing**: Contribution guidelines and development setup
- **Roadmap**: Feature roadmap and development plans

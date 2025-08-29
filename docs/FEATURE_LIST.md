# HoneyHive Python SDK Feature List

A comprehensive overview of all **actually implemented** features available in the HoneyHive Python SDK.

## 🚀 **Core Features**

### **Tracing & Observability**
- **OpenTelemetry Integration**: Full OpenTelemetry compliance with OTLP export
- **Singleton Tracer Pattern**: `HoneyHiveTracer` with automatic singleton management
- **Dual Initialization Patterns**:
  - **`HoneyHiveTracer.init()`** - Official SDK pattern (recommended)
  - **Constructor-based initialization** - Enhanced pattern with additional options
- **Session Management**: Automatic session creation and management
- **Context Propagation**: Automatic context propagation across operations
- **Baggage Support**: Custom metadata propagation with experiment harness integration

### **Tracing Decorators**
- **`@trace`** - Primary decorator for synchronous functions (recommended)
  - Automatically handles function inputs, outputs, and metadata
  - Full attribute and metadata support
  - Experiment harness integration
- **`@atrace`** - Async decorator for asynchronous functions
- **`@trace_class`** - Automatic method tracing for entire classes
- **`enrich_span`** - Context manager for enriching existing spans

### **Manual Span Management**
- **`start_span()`** - Create custom spans with context manager
- **`enrich_span()`** - Add attributes to existing spans
- **`enrich_session()`** - Session-level enrichment with metadata, feedback, and metrics

### **API Client**
- **HTTP Client**: Async-capable HTTP client with connection pooling
- **Authentication**: API key-based authentication
- **Rate Limiting**: Built-in rate limiting with configurable limits
- **Error Handling**: Comprehensive error handling and logging
- **Session Management**: Create, manage, and track sessions
- **Event Logging**: Log events with rich metadata
- **Connection Pooling**: Efficient HTTP connection reuse with keep-alive

### **Configuration Management**
- **Environment Variables**: Support for `HH_*` environment variables
- **Dynamic Reloading**: Runtime configuration updates with `reload_config()`
- **Project Management**: Multi-project support
- **Source Tracking**: Environment and source identification
- **HTTP Client Configuration**: Configurable connection pooling, rate limiting, and proxy settings
- **Experiment Harness Integration**: Support for MLflow, Weights & Biases, Comet, and standard experiment variables

## **Experiment Harness Integration**

### **Automatic Detection**
- **MLflow**: Automatic detection of `MLFLOW_EXPERIMENT_ID` and `MLFLOW_EXPERIMENT_NAME`
- **Weights & Biases**: Automatic detection of `WANDB_RUN_ID` and `WANDB_PROJECT`
- **Comet**: Automatic detection of `COMET_EXPERIMENT_KEY` and `COMET_PROJECT_NAME`
- **Standard Variables**: Support for `EXPERIMENT_ID`, `EXPERIMENT_NAME`, `EXPERIMENT_VARIANT`, `EXPERIMENT_GROUP`
- **Metadata Parsing**: Support for JSON, key-value, and comma-separated metadata formats
- **Automatic Span Enrichment**: All spans automatically include experiment context

### **Span Attributes**
- **Experiment ID**: `honeyhive.experiment_id`
- **Experiment Name**: `honeyhive.experiment_name`
- **Experiment Variant**: `honeyhive.experiment_variant`
- **Experiment Group**: `honeyhive.experiment_group`
- **Experiment Metadata**: Individual attributes for each metadata key

## **Advanced Features**

### **Connection Management**
- **Connection Pooling**: Efficient HTTP connection reuse with configurable limits
- **Keep-Alive**: Connection keep-alive management with expiry settings
- **Timeout Handling**: Configurable timeouts and retries
- **Cleanup**: Automatic connection cleanup and resource management
- **Pool Configuration**: Configurable pool sizes and connection limits

### **Caching System**
- **In-Memory Cache**: Fast in-memory caching with TTL
- **LRU Eviction**: Least-recently-used cache eviction
- **Size Limits**: Configurable cache size limits
- **Function Caching**: `@cache` and `@acache` decorators for function results
- **Async Support**: Full async/await support for caching operations
- **Statistics**: Cache hit/miss statistics and performance metrics

### **Retry & Resilience**
- **Exponential Backoff**: Configurable exponential backoff strategies
- **Jitter Support**: Random jitter to prevent thundering herd
- **Multiple Strategies**: Exponential, linear, and constant backoff
- **Status Code Handling**: Configurable retry on specific HTTP status codes
- **Timeout Management**: Configurable timeouts for retry operations

### **Utilities**
- **Logging**: Structured logging with custom formatters (`HoneyHiveLogger`)
- **Data Structures**: `DotDict` for dot-notation access to dictionaries
- **Baggage Management**: `BaggageDict` for OpenTelemetry baggage operations
- **Validation**: Data validation and type checking with Pydantic models
- **Serialization**: JSON serialization and deserialization with error handling

## **Development & Testing**

### **Testing Support**
- **Tox Integration**: Multi-Python version testing (3.11, 3.12, 3.13)
- **Pytest Support**: Full pytest integration with fixtures and async support
- **Mock Support**: Comprehensive mocking and testing utilities
- **Integration Tests**: Real API integration testing
- **Unit Tests**: Comprehensive unit test coverage
- **Test Mode**: Built-in test mode for development and testing

### **Development Tools**
- **CLI Interface**: Command-line interface for common operations
- **Code Quality**: Black, isort, flake8, mypy integration
- **Documentation**: Comprehensive docstrings and examples
- **Type Hints**: Full type annotation support with mypy strict mode
- **Configuration Management**: CLI commands for viewing and managing configuration

## **Performance & Reliability**

### **Performance Features**
- **Async Support**: Full async/await support throughout the codebase
- **Connection Reuse**: Efficient HTTP connection management
- **Batch Operations**: Support for batch API operations
- **Streaming**: Support for streaming responses
- **Lazy Initialization**: HTTP clients initialized only when needed

### **Reliability Features**
- **Error Recovery**: Automatic error recovery and retry
- **Rate Limiting**: Protection against API rate limit violations
- **Health Monitoring**: Built-in health check capabilities
- **Resource Management**: Automatic cleanup and resource management

## **Deployment & Operations**

### **Configuration**
- **Environment-Based**: Environment-specific configuration
- **Secrets Management**: Secure API key management via environment variables
- **Validation**: Configuration validation and error checking
- **Defaults**: Sensible defaults with override capability
- **Server URL Support**: Self-hosted deployment support with `server_url` parameter

### **Monitoring**
- **OTLP Export**: OpenTelemetry Protocol (OTLP) export to HoneyHive backend
- **Span Processing**: Custom span processor for HoneyHive-specific attributes
- **Console Export**: Console export for debugging and development
- **Metrics Collection**: Built-in metrics collection via span attributes

## **Security Features**

### **Authentication & Authorization**
- **API Key Security**: Secure API key handling via environment variables
- **Bearer Token**: Bearer token authentication for API requests
- **Rate Limiting**: Protection against abuse with configurable limits
- **Audit Logging**: Comprehensive audit trail via event logging

### **Data Protection**
- **HTTPS Only**: All API communication over HTTPS
- **SSL Verification**: Configurable SSL certificate verification
- **Proxy Support**: HTTP/HTTPS proxy support for enterprise environments
- **Access Control**: Project-based access control

## **Extensibility**

### **Integration Points**
- **OpenInference Support**: Automatic integration with OpenInference instrumentors
- **Custom Instrumentors**: Support for custom OpenTelemetry instrumentors
- **Middleware Support**: Custom middleware integration capabilities
- **Plugin Architecture**: Modular architecture for extensions

### **Customization**
- **Custom Attributes**: Full support for custom span attributes
- **Custom Metadata**: Flexible metadata handling for all operations
- **Custom Metrics**: Support for custom performance metrics
- **Custom Feedback**: User feedback integration for evaluation

## **Documentation & Support**

### **Documentation**
- **API Reference**: Comprehensive API documentation
- **Examples**: Practical usage examples and tutorials
- **Best Practices**: Development and deployment best practices
- **Configuration Guide**: Detailed configuration documentation

### **Examples**
- **Basic Usage**: Simple tracing and API usage examples
- **Enhanced Tracing**: Advanced tracing features demonstration
- **Evaluation**: Model evaluation and metrics examples
- **Integration**: OpenInference and experiment harness integration
- **CLI Usage**: Command-line interface examples

## **Technical Specifications**

### **Requirements**
- **Python**: 3.11+ (with support for 3.11, 3.12, 3.13)
- **Dependencies**: OpenTelemetry, httpx, pydantic, click, pyyaml
- **Platform**: Cross-platform (Windows, macOS, Linux)

### **Performance**
- **Memory**: Efficient memory usage with connection pooling
- **CPU**: Minimal CPU overhead for tracing operations
- **Network**: Optimized network usage with keep-alive and connection reuse
- **Scalability**: Designed for high-throughput production environments

## **Notable Limitations**

### **Features Not Currently Implemented**
- **LLM Provider Integrations**: No direct OpenAI, Anthropic, or other LLM provider integrations
- **Framework Middleware**: No FastAPI, Flask, or Django middleware
- **LangChain/LlamaIndex**: No direct callback handlers for these frameworks
- **Webhook Support**: No webhook integration capabilities
- **Metrics Endpoint**: No metrics endpoint (meter_provider not configured)
- **Circuit Breaker**: No circuit breaker pattern implementation
- **Health Check Endpoints**: No built-in health check endpoints

### **Planned Features**
- **Enhanced LLM Integration**: Future support for direct LLM provider integration
- **Framework Middleware**: Planned middleware for popular web frameworks
- **Advanced Metrics**: Enhanced metrics collection and visualization
- **Real-time Monitoring**: Real-time monitoring and alerting capabilities

---

*This feature list reflects the actual implemented capabilities of the HoneyHive Python SDK as of version 0.1.0. Features are based on source code analysis and may differ from marketing materials or planned features.*

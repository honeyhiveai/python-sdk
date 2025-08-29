# HoneyHive Python SDK Documentation

Welcome to the comprehensive documentation for the HoneyHive Python SDK. This SDK provides LLM observability, evaluation, and tracing capabilities with OpenTelemetry integration.

## 🚀 **Quick Start**

### **Primary Initialization Pattern (Recommended)**

```python
from honeyhive import HoneyHiveTracer

# Initialize tracer using the official SDK pattern
HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="production"
)

# Access the tracer instance
tracer = HoneyHiveTracer._instance

# Use tracing decorators
from honeyhive import trace, atrace

@trace(event_type="demo", event_name="my_function")
def my_function():
    return "Hello, World!"

@atrace
async def async_function():
    return "Hello, Async World!"
```

**✅ This pattern matches the official HoneyHive documentation at [docs.honeyhive.ai](https://docs.honeyhive.ai)!**

## 📚 **Documentation Sections**

### **Core Concepts**
- **[API Reference](API_REFERENCE.md)** - Complete API reference with examples
- **[Implementation Guide](IMPLEMENTATION_GUIDE.md)** - Technical implementation details
- **[Feature List](FEATURE_LIST.md)** - Comprehensive feature overview

### **Usage Patterns**
- **[Basic Usage Patterns](examples/BASIC_USAGE_PATTERNS.md)** - Getting started and common patterns
- **[Advanced Patterns](examples/ADVANCED_PATTERNS.md)** - Complex use cases and best practices
- **[Practical Examples](examples/PRACTICAL_EXAMPLES.md)** - Real-world implementation examples

### **Integration Guides**
- **[OpenInference Integration](OPENINFERENCE_INTEGRATION.md)** - Using SDK with OpenInference instrumentors
- **[Examples Directory](examples/README.md)** - Complete examples with code samples

### **Tracing with @trace (Recommended)**

The `@trace` decorator is the **primary tracing method** and automatically handles both synchronous and asynchronous functions:

```python
from honeyhive import trace

# Works with sync functions
@trace(event_type="demo", event_name="sync_function")
def sync_function():
    return "sync result"

# Works with async functions
@trace(event_type="demo", event_name="async_function")
async def async_function():
    return "async result"
```

**Benefits of @trace:**
- ✅ **Unified API** - Same decorator for sync and async
- ✅ **Automatic Detection** - No need to choose between decorators
- ✅ **Cleaner Code** - Simpler, more intuitive syntax
- ✅ **Full Compatibility** - Works with all existing features

## 🔄 **Alternative Initialization Pattern**

For advanced use cases with additional options:

```python
# Enhanced constructor with additional options
tracer = HoneyHiveTracer(
    api_key="your-key",
    project="your-project",
    source="production",
    test_mode=True,  # Additional option
    instrumentors=[OpenAIInstrumentor()]  # Additional option
)
```

**Both patterns are fully supported and work together seamlessly!**

## 🎯 **Key Features**

### **OpenTelemetry Integration**
- Full OTEL compliance with custom span processor and exporter
- Automatic session creation and management
- Seamless integration with existing OpenTelemetry setups

### **Tracing Decorators**
- **`@trace`** - Primary decorator for all functions (recommended)
- **`@atrace`** - Alternative async decorator
- **`@trace_class`** - Automatic method tracing for classes

### **API Client**
- Comprehensive HTTP client with retry support
- Session and event management
- Evaluation framework integration

### **Environment Configuration**
- Flexible configuration via environment variables
- Support for self-hosted deployments
- Test mode for development and CI/CD

## 🚀 **Why Use the Primary Pattern?**

1. **✅ Official SDK Compliance** - Matches docs.honeyhive.ai exactly
2. **✅ Production Ready** - Used in real-world deployments
3. **✅ Self-Hosted Support** - Built-in `server_url` parameter
4. **✅ Environment Integration** - Seamless environment variable support
5. **✅ Singleton Management** - Automatic instance management
6. **✅ Backwards Compatible** - Your existing code continues to work

## 📖 **Getting Started**

1. **Install the SDK:**
   ```bash
   pip install honeyhive
   ```

2. **Set Environment Variables:**
   ```bash
   export HH_API_KEY="your-api-key"
   export HH_PROJECT="your-project"
   export HH_SOURCE="development"
   ```

3. **Initialize Tracer:**
   ```python
   from honeyhive import HoneyHiveTracer
   
   HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project",
       source="production"
   )
   ```

4. **Start Tracing:**
   ```python
   from honeyhive import trace
   
   @trace(event_type="demo", event_name="my_function")
   def my_function():
       return "Hello, World!"
   ```

## 🔗 **External Resources**

- **[Official HoneyHive Documentation](https://docs.honeyhive.ai)** - Primary source for API patterns
- **[GitHub Repository](https://github.com/honeyhiveai/python-sdk)** - Source code and issues
- **[OpenTelemetry Documentation](https://opentelemetry.io/docs/)** - Tracing framework details

## 🆘 **Support**

- **Documentation Issues**: Open an issue in the GitHub repository
- **API Questions**: Check the [API Reference](API_REFERENCE.md)
- **Integration Help**: See [OpenInference Integration](OPENINFERENCE_INTEGRATION.md)

---

**Start with `HoneyHiveTracer.init()` for the best experience!** 🎯

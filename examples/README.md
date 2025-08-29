# HoneyHive Python SDK Examples

This directory contains comprehensive examples demonstrating how to use the HoneyHive Python SDK with the **recommended initialization pattern**.

## 🚀 **Primary Initialization Pattern (Recommended)**

All examples now use the official SDK pattern for maximum compatibility:

```python
from honeyhive import HoneyHiveTracer

# Initialize tracer using the recommended pattern
HoneyHiveTracer.init(
    api_key="your-api-key",
    project="your-project",
    source="production"
)

# Access the tracer instance
tracer = HoneyHiveTracer._instance
```

## 📚 **Available Examples**

### **Core Functionality**
- **[`basic_usage.py`](basic_usage.py)** - Basic SDK usage with `HoneyHiveTracer.init()`
- **[`tracing_decorators.py`](tracing_decorators.py)** - Using `@trace`, `@atrace`, and `@trace_class` decorators
- **[`enhanced_tracing_demo.py`](enhanced_tracing_demo.py)** - Advanced tracing features and manual span management

### **Integration Examples**
- **[`openinference_integration.py`](openinference_integration.py)** - OpenInference integration with HoneyHive
- **[`openinference_integration_simple.py`](openinference_integration_simple.py)** - Simplified OpenInference setup
- **[`openinference_google_ai_integration.py`](openinference_google_ai_integration.py)** - Google AI integration

### **Evaluation Framework**
- **[`evaluation_example.py`](evaluation_example.py)** - Using the evaluation framework with `@evaluator` decorators

### **Advanced Patterns**
- **[`pydantic_validation_demo.py`](pydantic_validation_demo.py)** - Pydantic validation with tracing
- **[`verbose_demo.py`](verbose_demo.py)** - Verbose logging and debugging
- **[`verbose_debugging_example.py`](verbose_debugging_example.py)** - Advanced debugging techniques

### **Backwards Compatibility**
- **[`backwards_compatibility_demo.py`](backwards_compatibility_demo.py)** - Demonstrating both initialization patterns

## 🔧 **Key Features Demonstrated**

### **1. Primary Initialization**
```python
# Recommended pattern (matches docs.honeyhive.ai)
HoneyHiveTracer.init(
    api_key="your-key",
    project="your-project",
    source="production",
    server_url="https://custom-server.com"  # For self-hosted deployments
)
```

### **2. Tracer Access**
```python
# Get tracer instance after initialization
tracer = HoneyHiveTracer._instance

# Use tracer for manual operations
with tracer.start_span("operation"):
    # Your code here
    pass
```

### **3. Decorator Usage**
```python
from honeyhive import trace, atrace, trace_class

@trace(event_type="demo", event_name="my_function")
def my_function():
    return "Hello, World!"

@atrace
async def async_function():
    return "Hello, Async World!"

@trace_class
class MyClass:
    def method(self):
        return "Traced method"
```

## ⚠️ **Important: Use @trace for Tracing**

**Avoid using `@dynamic_trace`** - it's available for backward compatibility but `@trace` is preferred.

The `@trace` decorator automatically handles both synchronous and asynchronous functions, providing the same functionality as `@dynamic_trace` but with a cleaner, more intuitive API.

## 🎯 **Getting Started**

1. **Install Dependencies:**
   ```bash
   pip install honeyhive
   ```

2. **Set Environment Variables:**
   ```bash
   export HH_API_KEY="your-api-key"
   export HH_PROJECT="your-project"
   export HH_SOURCE="development"
   ```

3. **Run Examples:**
   ```bash
   # Basic usage
   python examples/basic_usage.py
   
   # Tracing decorators
   python examples/tracing_decorators.py
   
   # OpenInference integration
   python examples/openinference_integration.py
   ```

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

## 📖 **Documentation**

For comprehensive documentation, see:
- **[API Reference](../docs/API_REFERENCE.md)** - Complete API reference
- **[Basic Usage Patterns](../docs/examples/BASIC_USAGE_PATTERNS.md)** - Detailed usage patterns
- **[Implementation Guide](../docs/IMPLEMENTATION_GUIDE.md)** - Technical implementation details

## 🚀 **Why Use the Primary Pattern?**

1. **✅ Official SDK Compliance** - Matches docs.honeyhive.ai exactly
2. **✅ Production Ready** - Used in real-world deployments
3. **✅ Self-Hosted Support** - Built-in `server_url` parameter
4. **✅ Environment Integration** - Seamless environment variable support
5. **✅ Singleton Management** - Automatic instance management
6. **✅ Backwards Compatible** - Your existing code continues to work

**Start with `HoneyHiveTracer.init()` for the best experience!** 🎯

# Examples Directory

Practical examples and usage patterns for the HoneyHive SDK.

## 🚀 **What's New: Comprehensive Evaluation Framework**

The SDK now includes a **production-ready evaluation framework** with threading support, built-in evaluators, and seamless API integration.

**Key Features:**
- **🔄 Threading Support**: Parallel evaluation processing with `ThreadPoolExecutor`
- **🎯 Built-in Evaluators**: Exact match, F1 score, length, and semantic similarity
- **🔧 Custom Evaluators**: Extensible framework for domain-specific evaluation
- **✨ Decorator Pattern**: Seamless integration with `@evaluate_decorator`
- **📊 API Integration**: Store evaluation results in HoneyHive
- **⚡ Batch Processing**: Efficient evaluation of large datasets

**Quick Start:**
```python
from honeyhive.evaluation.evaluators import evaluate_decorator

@evaluate_decorator(evaluators=["exact_match", "length"])
def generate_response(prompt: str) -> str:
    return "Generated response"

# Function is automatically evaluated when called
result = generate_response("Hello, world!")
```

## 📚 Available Examples

### [Basic Usage Patterns](BASIC_USAGE_PATTERNS.md)
Common usage patterns including:
- Initialization patterns
- **Tracing patterns** - **Use `@trace` decorator (recommended)**
- Session management
- Error handling
- Configuration patterns
- Performance optimization
- Testing patterns

### [Advanced Patterns](ADVANCED_PATTERNS.md)
Advanced usage techniques including:
- Custom instrumentors
- Advanced span management
- Performance optimization
- Framework integration
- Custom metrics collection

### [Practical Examples](PRACTICAL_EXAMPLES.md)
Real-world use cases including:
- Web application integration
- Data processing pipeline
- AI service with multiple providers
- Microservice architecture

### **🆕 [Evaluation Framework Examples](../evaluation/examples.rst)**
Comprehensive evaluation examples including:
- **Threading & Parallel Processing**: Parallel evaluation with `ThreadPoolExecutor`
- **Custom Evaluators**: Creating domain-specific evaluation logic
- **Decorator Pattern**: Automatic evaluation with `@evaluate_decorator`
- **Batch Processing**: Efficient evaluation of large datasets
- **Performance Optimization**: Memory management and worker configuration
- **API Integration**: Storing evaluation results in HoneyHive
- **Error Handling**: Robust error handling and resilience patterns

## 🚀 Quick Start

1. **New to HoneyHive?** Start with [Basic Usage Patterns](BASIC_USAGE_PATTERNS.md)
2. **Building an app?** Check [Practical Examples](PRACTICAL_EXAMPLES.md)
3. **Need advanced features?** Read [Advanced Patterns](ADVANCED_PATTERNS.md)
4. **🆕 Evaluating LLM outputs?** See [Evaluation Framework Examples](../evaluation/examples.rst)

## 💡 How to Use These Examples

### **Important: Use @trace for Tracing**
The examples demonstrate the **recommended `@trace` decorator** which automatically handles both sync and async functions:

```python
from honeyhive.tracer.decorators import trace  # ← Preferred

@trace(event_type="model", event_name="text_generation")
def generate_text(prompt: str) -> str:
    return "Generated text"

@trace(event_type="model", event_name="async_generation")
async def generate_text_async(prompt: str) -> str:
    return "Generated text async"
```

**Use `@trace` for most tracing needs** - it automatically handles both synchronous and asynchronous functions with a clean, intuitive API.

### **🆕 Important: Use @evaluate_decorator for Evaluation**
For evaluation needs, use the **recommended `@evaluate_decorator`** which provides automatic evaluation:

```python
from honeyhive.evaluation.evaluators import evaluate_decorator  # ← Preferred

@evaluate_decorator(evaluators=["exact_match", "length"])
def generate_response(prompt: str) -> str:
    return "Generated response"

# Function is automatically evaluated when called
result = generate_response("Hello, world!")
```

### Copy and Adapt
- Copy the example code that matches your use case
- Adapt the configuration and attributes to your needs
- Modify error handling and business logic as required

### Learn the Patterns
- Study the span naming conventions
- Understand attribute organization
- Learn error handling strategies
- **🆕 Master evaluation patterns and threading**

### Build Incrementally
- Start with basic tracing
- Add custom attributes gradually
- Implement advanced features as needed
- **🆕 Add evaluation capabilities step by step**

## 🔧 Prerequisites

Before running these examples, ensure you have:

1. **HoneyHive SDK installed**
   ```bash
   pip install honeyhive
   ```

2. **API credentials configured**
   ```bash
   export HH_API_KEY="your-api-key"
   export HH_PROJECT="your-project"
   export HH_SOURCE="production"
   ```

3. **Required dependencies** (for specific examples)
   ```bash
   pip install fastapi httpx pandas openai anthropic
   ```

4. **🆕 Evaluation dependencies** (for evaluation examples)
   ```bash
   pip install numpy scikit-learn  # For advanced evaluators
   ```

## 📖 Related Documentation

For comprehensive documentation, see:
- **[API Reference](../API_REFERENCE.md)** - Complete API reference
- **[Basic Usage Patterns](BASIC_USAGE_PATTERNS.md)** - Detailed usage patterns
- **[Implementation Guide](../IMPLEMENTATION_GUIDE.md)** - Technical implementation details
- **🆕 [Evaluation Framework](../evaluation/index.rst)** - Comprehensive evaluation documentation
- **🆕 [Evaluation Examples](../evaluation/examples.rst)** - Detailed evaluation examples

## 🤝 Contributing Examples

We welcome contributions! To add new examples:

1. Create a new markdown file in this directory
2. Follow the existing format and structure
3. Include clear code examples and explanations
4. Add the example to this README index
5. Submit a pull request

## 🐛 Getting Help

If you encounter issues with the examples:

1. Check the [API reference](../API_REFERENCE.md) for details
2. Verify your configuration and credentials
3. Open an issue with specific error details

---

**Last Updated**: January 2025  
**Examples Version**: 2.0  
**🆕 Evaluation Framework**: Production-ready with threading support

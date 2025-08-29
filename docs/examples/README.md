# Examples Directory

Practical examples and usage patterns for the HoneyHive SDK.

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

## 🚀 Quick Start

1. **New to HoneyHive?** Start with [Basic Usage Patterns](BASIC_USAGE_PATTERNS.md)
2. **Building an app?** Check [Practical Examples](PRACTICAL_EXAMPLES.md)
3. **Need advanced features?** Read [Advanced Patterns](ADVANCED_PATTERNS.md)

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

**Avoid using `@dynamic_trace`** - it's available for backward compatibility but `@trace` is preferred.

### Copy and Adapt
- Copy the example code that matches your use case
- Adapt the configuration and attributes to your needs
- Modify error handling and business logic as required

### Learn the Patterns
- Study the span naming conventions
- Understand attribute organization
- Learn error handling strategies

### Build Incrementally
- Start with basic tracing
- Add custom attributes gradually
- Implement advanced features as needed

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

## 📖 Related Documentation

For comprehensive documentation, see:
- **[API Reference](../API_REFERENCE.md)** - Complete API reference
- **[Basic Usage Patterns](BASIC_USAGE_PATTERNS.md)** - Detailed usage patterns
- **[Implementation Guide](../IMPLEMENTATION_GUIDE.md)** - Technical implementation details

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

**Last Updated**: December 2024  
**Examples Version**: 1.0

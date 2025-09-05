# Documentation Templates

This directory contains the formal template system for generating consistent multi-instrumentor integration documentation.

## 🎯 **Quick Start**

Generate provider documentation using the formal template:

```bash
# Generate Anthropic integration docs
./docs/_templates/generate_provider_docs.py --provider anthropic

# Generate Google AI integration docs  
./docs/_templates/generate_provider_docs.py --provider google-ai

# List available providers
./docs/_templates/generate_provider_docs.py --list
```

## 📁 **Template Files**

### Core Templates
- **`multi_instrumentor_integration_formal_template.rst`** - Main template with {{VARIABLE}} placeholders
- **`template_variables.md`** - Documentation of all template variables and their usage
- **`generate_provider_docs.py`** - Script to generate provider docs from template

### Legacy Templates (Reference Only)
- `multi_instrumentor_integration_template.rst` - Earlier version
- `openllmetry_integration_template.rst` - OpenLLMetry-only template
- `openai_multi_instrumentor_example.rst` - OpenAI example implementation

## 🔧 **Template System Features**

### ✅ **What This Provides**
- **Consistent UI**: Same tabbed interface across all providers
- **Complete Examples**: Copy-paste ready code for both instrumentors
- **Quality Assurance**: All templates follow Agent OS documentation standards
- **Easy Maintenance**: Single template file generates all provider docs
- **Type Safety**: Proper imports and EventType enum usage

### 🎨 **Visual Structure**
```
┌─ Instrumentor Selector ──────────────────────────┐
│  ┌─ OpenInference ─┐  ┌─ OpenLLMetry ──┐         │
│  │ 📦 Installation │  │ 📦 Installation │         │
│  │ ⚙️  Basic Setup │  │ ⚙️  Basic Setup │         │  
│  │ 🚀 Advanced    │  │ 🚀 Advanced    │         │
│  │ 🔧 Troubleshoot│  │ 🔧 Troubleshoot│         │
│  └─────────────────┘  └─────────────────┘         │
└───────────────────────────────────────────────────┘

┌─ General Content (always visible) ───────────────┐
│  📊 Comparison Table                             │
│  🔧 Environment Configuration                    │  
│  🔄 Migration Guide                              │
│  📚 See Also                                     │
└───────────────────────────────────────────────────┘
```

## 📝 **Creating New Provider Documentation**

### Method 1: Use Generation Script (Recommended)

```bash
# 1. Add provider config to generate_provider_docs.py
# 2. Run the generator
./docs/_templates/generate_provider_docs.py --provider your-provider

# 3. Customize generated output if needed
# 4. Test the tabbed interface
cd docs && make html && python serve.py
```

### Method 2: Manual Template Replacement

```bash
# 1. Copy the formal template
cp docs/_templates/multi_instrumentor_integration_formal_template.rst \
   docs/how-to/integrations/your-provider.rst

# 2. Replace all {{VARIABLE}} placeholders
# 3. Customize code examples
# 4. Validate and test
```

## 🔍 **Template Variables**

Key variables you need to define for each provider:

### Required Provider Info
```yaml
PROVIDER_NAME: "Your Provider"        # Human-readable name
PROVIDER_KEY: "your-provider"         # URL/filename key  
PROVIDER_MODULE: "your_provider"      # Python import module
PROVIDER_SDK: "your-provider>=1.0.0"  # SDK package requirement
```

### Instrumentor Packages
```yaml
OPENINFERENCE_PACKAGE: "openinference-instrumentation-your-provider"
TRACELOOP_PACKAGE: "opentelemetry-instrumentation-your-provider"
```

### Code Examples
```yaml
BASIC_USAGE_EXAMPLE: |
  client = your_provider.Client()
  response = client.generate("Hello!")
  print(response.text)

ADVANCED_FUNCTION_NAME: "your_use_case"
ADVANCED_IMPLEMENTATION: |
  # Your multi-step example here
```

See `template_variables.md` for complete variable reference.

## ✅ **Quality Standards**

Every generated template must meet:

- **📋 Functional Code**: All examples copy-paste ready and tested
- **🔗 Correct Imports**: Proper package imports with version compatibility
- **🎨 UI Consistency**: Same tabbed interface and styling
- **📚 Documentation Standards**: Follows Divio system and Agent OS rules
- **🔧 Error Handling**: Proper exception handling in all examples
- **🎯 Type Safety**: EventType enums, proper type annotations

## 🧪 **Testing Your Template**

```bash
# 1. Generate the documentation
./docs/_templates/generate_provider_docs.py --provider your-provider

# 2. Build and serve docs locally
cd docs
make html
python serve.py

# 3. Navigate to: http://localhost:8000/how-to/integrations/your-provider.html
# 4. Test all tabs work properly
# 5. Verify all code examples are correct
```

## 🚀 **Integration with Agent OS**

This template system is formally defined in Agent OS standards:

- **📋 Complete Guide**: `.agent-os/standards/documentation-generation.md` - Comprehensive usage documentation
- **🔧 Best Practices**: `.agent-os/standards/best-practices.md` - Integration requirements checklist
- **⚙️ Tech Stack**: `.agent-os/standards/tech-stack.md` - Documentation tools and commands
- **🚨 Quality Requirements**: All new integrations MUST use this template system

## 📖 **Examples**

- **OpenAI**: `docs/how-to/integrations/openai.rst` - Live example using this template
- **Generation Script**: Run with `--help` for usage examples
- **Variable Configs**: See `PROVIDER_CONFIGS` in `generate_provider_docs.py`

This template system ensures every provider integration delivers a consistent, high-quality user experience while maintaining the flexibility to showcase provider-specific features and capabilities.

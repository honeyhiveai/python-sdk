# Multi-Instrumentor Integration Template Variables

This document defines the template variables used in `multi_instrumentor_integration_formal_template.rst` for generating provider-specific integration documentation.

## Template Variables Reference

### Basic Provider Information
- `{{PROVIDER_NAME}}` - Human-readable provider name (e.g., "OpenAI", "Anthropic", "Google AI")
- `{{PROVIDER_KEY}}` - Lowercase key for the provider (e.g., "openai", "anthropic", "google-ai")
- `{{PROVIDER_MODULE}}` - Python module name (e.g., "openai", "anthropic", "google.generativeai")
- `{{PROVIDER_SDK}}` - SDK package name (e.g., "openai>=1.0.0", "anthropic>=0.17.0")
- `{{PROVIDER_EXCEPTION}}` - Main exception class (e.g., "openai.APIError", "anthropic.APIError")
- `{{PROVIDER_API_KEY_NAME}}` - Environment variable name (e.g., "OPENAI_API_KEY", "ANTHROPIC_API_KEY")

### OpenInference Configuration
- `{{OPENINFERENCE_PACKAGE}}` - Package name (e.g., "openinference-instrumentation-openai")
- `{{OPENINFERENCE_IMPORT}}` - Import path (e.g., "openinference.instrumentation.openai")
- `{{OPENINFERENCE_CLASS}}` - Instrumentor class name (e.g., "OpenAIInstrumentor")

### OpenLLMetry Configuration  
- `{{OPENLLMETRY_PACKAGE}}` - Package name (e.g., "opentelemetry-instrumentation-openai")
- `{{OPENLLMETRY_IMPORT}}` - Import path (e.g., "opentelemetry.instrumentation.openai")
- `{{OPENLLMETRY_CLASS}}` - Instrumentor class name (e.g., "OpenAIInstrumentor")

### Code Examples
- `{{BASIC_USAGE_EXAMPLE}}` - Simple usage example
- `{{ADVANCED_FUNCTION_NAME}}` - Name for advanced example function
- `{{ADVANCED_FUNCTION_PARAMS}}` - Parameters for advanced function
- `{{ADVANCED_USAGE_EXAMPLE}}` - Setup code for advanced example
- `{{ADVANCED_IMPLEMENTATION}}` - Main implementation code
- `{{USE_CASE_NAME}}` - Business use case name
- `{{STRATEGY_NAME}}` - Technical strategy name
- `{{MODELS_USED}}` - List of models used
- `{{RETURN_VALUE}}` - Return value structure
- `{{FIRST_PARAM}}` - First parameter name for type checking

### Additional Configuration
- `{{ADDITIONAL_ENV_CONFIG}}` - Provider-specific environment configuration
- `{{MULTIPLE_INSTRUMENTORS_EXAMPLE}}` - Example of combining instrumentors
- `{{MULTIPLE_OPENLLMETRY_INSTRUMENTORS_EXAMPLE}}` - Example of multiple OpenLLMetry instrumentors
- `{{SEE_ALSO_LINKS}}` - Related documentation links

## Provider-Specific Variable Sets

### OpenAI Variables
```yaml
PROVIDER_NAME: "OpenAI"
PROVIDER_KEY: "openai"
PROVIDER_MODULE: "openai"
PROVIDER_SDK: "openai>=1.0.0"
PROVIDER_EXCEPTION: "openai.APIError"
PROVIDER_API_KEY_NAME: "OPENAI_API_KEY"

OPENINFERENCE_PACKAGE: "openinference-instrumentation-openai"
OPENINFERENCE_IMPORT: "openinference.instrumentation.openai"
OPENINFERENCE_CLASS: "OpenAIInstrumentor"

OPENLLMETRY_PACKAGE: "opentelemetry-instrumentation-openai"
OPENLLMETRY_IMPORT: "opentelemetry.instrumentation.openai"
OPENLLMETRY_CLASS: "OpenAIInstrumentor"

BASIC_USAGE_EXAMPLE: |
  client = openai.OpenAI()  # Uses OPENAI_API_KEY automatically
  response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "user", "content": "Hello!"}]
  )
  print(response.choices[0].message.content)

ADVANCED_FUNCTION_NAME: "analyze_sentiment"
ADVANCED_FUNCTION_PARAMS: "text: str"
USE_CASE_NAME: "sentiment_analysis"
STRATEGY_NAME: "multi_model_comparison"
MODELS_USED: '["gpt-3.5-turbo", "gpt-4"]'
FIRST_PARAM: "text"

ADDITIONAL_ENV_CONFIG: ""

SEE_ALSO_LINKS: |
  - :doc:`multi-provider` - Use OpenAI with other providers
  - :doc:`../troubleshooting` - Common integration issues  
  - :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
  - :doc:`anthropic` - Similar integration for Anthropic Claude
```

### Anthropic Variables
```yaml
PROVIDER_NAME: "Anthropic"
PROVIDER_KEY: "anthropic" 
PROVIDER_MODULE: "anthropic"
PROVIDER_SDK: "anthropic>=0.17.0"
PROVIDER_EXCEPTION: "anthropic.APIError"
PROVIDER_API_KEY_NAME: "ANTHROPIC_API_KEY"

OPENINFERENCE_PACKAGE: "openinference-instrumentation-anthropic"
OPENINFERENCE_IMPORT: "openinference.instrumentation.anthropic"
OPENINFERENCE_CLASS: "AnthropicInstrumentor"

OPENLLMETRY_PACKAGE: "opentelemetry-instrumentation-anthropic"
OPENLLMETRY_IMPORT: "opentelemetry.instrumentation.anthropic"
OPENLLMETRY_CLASS: "AnthropicInstrumentor"

BASIC_USAGE_EXAMPLE: |
  client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY automatically
  response = client.messages.create(
      model="claude-3-sonnet-20240229",
      max_tokens=1000,
      messages=[{"role": "user", "content": "Hello!"}]
  )
  print(response.content[0].text)

ADVANCED_FUNCTION_NAME: "analyze_document"
ADVANCED_FUNCTION_PARAMS: "document: str"
USE_CASE_NAME: "document_analysis"
STRATEGY_NAME: "claude_reasoning"
MODELS_USED: '["claude-3-sonnet-20240229", "claude-3-opus-20240229"]'
FIRST_PARAM: "document"

SEE_ALSO_LINKS: |
  - :doc:`multi-provider` - Use Anthropic with other providers
  - :doc:`../troubleshooting` - Common integration issues
  - :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
  - :doc:`openai` - Similar integration for OpenAI GPT
```

## Usage Instructions

1. **Copy the formal template**: `multi_instrumentor_integration_formal_template.rst`
2. **Replace all variables**: Use the provider-specific variable set
3. **Customize examples**: Adapt code examples to provider-specific patterns
4. **Validate**: Ensure all imports and code examples work correctly
5. **Test**: Verify the tabbed interface renders properly

## Template Generation Script

```python
# Example script for generating provider documentation
import yaml
from pathlib import Path

def generate_provider_docs(provider_name: str, variables: dict):
    """Generate provider documentation from template."""
    template_path = Path("docs/_templates/multi_instrumentor_integration_formal_template.rst")
    template_content = template_path.read_text()
    
    # Replace all template variables
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        template_content = template_content.replace(placeholder, str(value))
    
    # Write generated documentation
    output_path = Path(f"docs/how-to/integrations/{variables['PROVIDER_KEY']}.rst")
    output_path.write_text(template_content)
    print(f"Generated: {output_path}")

# Usage
openai_vars = yaml.safe_load("""
PROVIDER_NAME: "OpenAI"
PROVIDER_KEY: "openai"
# ... rest of variables
""")

generate_provider_docs("OpenAI", openai_vars)
```

This template system ensures consistency across all provider integrations while maintaining the flexible tabbed interface pattern.

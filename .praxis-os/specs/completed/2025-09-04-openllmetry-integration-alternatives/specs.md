# OpenLLMetry Integration Alternatives - Technical Specifications

**Date**: 2025-09-04  
**Version**: 1.0  
**Status**: Draft  

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Provider Specifications](#provider-specifications)
3. [Documentation Requirements](#documentation-requirements)
4. [Testing Strategy](#testing-strategy)
5. [Implementation Details](#implementation-details)
6. [Migration Guide](#migration-guide)
7. [Quality Assurance](#quality-assurance)

## Architecture Overview

### Current OpenInference Pattern

The HoneyHive SDK currently supports OpenInference instrumentors through the BYOI (Bring Your Own Instrumentor) architecture:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(
    api_key="your-honeyhive-api-key",
    project="your-project",
    instrumentors=[OpenAIInstrumentor()]
)
```

### Target OpenLLMetry Pattern

The new OpenLLMetry alternatives will follow the same BYOI pattern with different import paths:

```python
from honeyhive import HoneyHiveTracer
from openllmetry.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(
    api_key="your-honeyhive-api-key", 
    project="your-project",
    instrumentors=[OpenAIInstrumentor()]
)
```

### Integration Architecture

```mermaid
graph TD
    A[HoneyHive SDK] --> B[BYOI Architecture]
    B --> C[OpenInference Instrumentors]
    B --> D[OpenLLMetry Instrumentors]
    B --> E[Custom Instrumentors]
    
    C --> F[openinference-instrumentation-openai]
    C --> G[openinference-instrumentation-anthropic]
    C --> H[openinference-instrumentation-google-generativeai]
    
    D --> I[openllmetry[openai]]
    D --> J[openllmetry[anthropic]]
    D --> K[openllmetry[google]]
    
    F --> L[OpenAI API]
    G --> M[Anthropic API]
    H --> N[Google AI API]
    I --> L
    J --> M
    K --> N
```

## Provider Specifications

### 1. OpenAI Integration

#### Current OpenInference Implementation
- **Package**: `openinference-instrumentation-openai`
- **Instrumentor**: `openinference.instrumentation.openai.OpenAIInstrumentor`
- **Install**: `pip install honeyhive[openinference-openai]`

#### New OpenLLMetry Alternative
- **Package**: `openllmetry[openai]`
- **Instrumentor**: `openllmetry.instrumentation.openai.OpenAIInstrumentor`
- **Install**: `pip install honeyhive[openllmetry-openai]`

#### Implementation Requirements
```python
# Compatibility Matrix Test (Primary Testing Approach)
# tests/compatibility_matrix/test_openllmetry_openai.py
def test_openllmetry_openai_integration():
    """Test complete OpenAI integration with OpenLLMetry following existing pattern."""
    from honeyhive import HoneyHiveTracer
    from openllmetry.instrumentation.openai import OpenAIInstrumentor
    import openai
    
    # Follow exact pattern from tests/compatibility_matrix/test_openai.py
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"), 
        instrumentors=[OpenAIInstrumentor()],
        source="compatibility_test"
    )
    
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    
    # Verify tracing and flush
    tracer.force_flush(timeout=10.0)
```

### 2. Anthropic Integration

#### Current OpenInference Implementation
- **Package**: `openinference-instrumentation-anthropic`
- **Instrumentor**: `openinference.instrumentation.anthropic.AnthropicInstrumentor`
- **Install**: `pip install honeyhive[openinference-anthropic]`

#### New OpenLLMetry Alternative  
- **Package**: `openllmetry[anthropic]`
- **Instrumentor**: `openllmetry.instrumentation.anthropic.AnthropicInstrumentor`
- **Install**: `pip install honeyhive[openllmetry-anthropic]`

#### Implementation Requirements
```python
def test_openllmetry_anthropic_integration():
    """Test complete Anthropic integration with OpenLLMetry."""
    from honeyhive import HoneyHiveTracer
    from openllmetry.instrumentation.anthropic import AnthropicInstrumentor
    import anthropic
    
    tracer = HoneyHiveTracer.init(
        api_key="test-key",
        instrumentors=[AnthropicInstrumentor()]
    )
    
    client = anthropic.Anthropic(api_key="test-key")
    # Verify tracing functionality
```

### 3. Google AI (Generative AI) Integration

#### Current OpenInference Implementation
- **Package**: `openinference-instrumentation-google-generativeai`
- **Instrumentor**: `openinference.instrumentation.google_generativeai.GoogleGenerativeAIInstrumentor`
- **Install**: `pip install honeyhive[openinference-google-ai]`

#### New OpenLLMetry Alternative
- **Package**: `openllmetry[google]`
- **Instrumentor**: `openllmetry.instrumentation.google.GoogleInstrumentor`
- **Install**: `pip install honeyhive[openllmetry-google-ai]`

#### Implementation Requirements
```python
def test_openllmetry_google_ai_integration():
    """Test complete Google AI integration with OpenLLMetry."""
    from honeyhive import HoneyHiveTracer
    from openllmetry.instrumentation.google import GoogleInstrumentor
    import google.generativeai as genai
    
    tracer = HoneyHiveTracer.init(
        api_key="test-key",
        instrumentors=[GoogleInstrumentor()]
    )
    
    # Configure and test Google AI
    genai.configure(api_key="test-key")
    model = genai.GenerativeModel('gemini-pro')
```

### 4. Google ADK Integration

#### Current OpenInference Implementation
- **Package**: `openinference-instrumentation-google-adk`
- **Instrumentor**: `openinference.instrumentation.google_adk.GoogleADKInstrumentor`
- **Install**: `pip install honeyhive[openinference-google-adk]`

#### New OpenLLMetry Alternative
- **Package**: `openllmetry[google-adk]` 
- **Instrumentor**: `openllmetry.instrumentation.google_adk.GoogleADKInstrumentor`
- **Install**: `pip install honeyhive[openllmetry-google-adk]`

#### Implementation Requirements
```python
def test_openllmetry_google_adk_integration():
    """Test complete Google ADK integration with OpenLLMetry."""
    from honeyhive import HoneyHiveTracer
    from openllmetry.instrumentation.google_adk import GoogleADKInstrumentor
    import google.adk as adk
    
    tracer = HoneyHiveTracer.init(
        api_key="test-key", 
        instrumentors=[GoogleADKInstrumentor()]
    )
    
    # Test agent workflow tracing
    agent = adk.Agent(name="test_agent", model="gemini-pro")
```

### 5. AWS Bedrock Integration

#### Current OpenInference Implementation
- **Package**: `openinference-instrumentation-bedrock`
- **Instrumentor**: `openinference.instrumentation.bedrock.BedrockInstrumentor`
- **Install**: `pip install honeyhive[openinference-bedrock]`

#### New OpenLLMetry Alternative
- **Package**: `openllmetry[bedrock]`
- **Instrumentor**: `openllmetry.instrumentation.bedrock.BedrockInstrumentor`
- **Install**: `pip install honeyhive[openllmetry-bedrock]`

#### Implementation Requirements
```python
def test_openllmetry_bedrock_integration():
    """Test complete AWS Bedrock integration with OpenLLMetry."""
    from honeyhive import HoneyHiveTracer
    from openllmetry.instrumentation.bedrock import BedrockInstrumentor
    import boto3
    
    tracer = HoneyHiveTracer.init(
        api_key="test-key",
        instrumentors=[BedrockInstrumentor()]
    )
    
    # Test Bedrock client initialization and tracing
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
```

### 6. Azure OpenAI Integration

#### Current OpenInference Implementation
- **Package**: `openinference-instrumentation-openai` (with Azure configuration)
- **Instrumentor**: `openinference.instrumentation.openai.OpenAIInstrumentor`
- **Install**: `pip install honeyhive[openinference-openai]`

#### New OpenLLMetry Alternative
- **Package**: `openllmetry[azure-openai]`
- **Instrumentor**: `openllmetry.instrumentation.azure_openai.AzureOpenAIInstrumentor`
- **Install**: `pip install honeyhive[openllmetry-azure-openai]`

#### Implementation Requirements
```python
def test_openllmetry_azure_openai_integration():
    """Test complete Azure OpenAI integration with OpenLLMetry."""
    from honeyhive import HoneyHiveTracer
    from openllmetry.instrumentation.azure_openai import AzureOpenAIInstrumentor
    import openai
    
    tracer = HoneyHiveTracer.init(
        api_key="test-key",
        instrumentors=[AzureOpenAIInstrumentor()]
    )
    
    # Test Azure OpenAI client configuration
    client = openai.AzureOpenAI(
        azure_endpoint="https://your-resource.openai.azure.com/",
        api_key="test-key",
        api_version="2024-02-01"
    )
```

### 7. MCP (Model Context Protocol) Integration

#### Current OpenInference Implementation
- **Package**: `openinference-instrumentation-mcp`
- **Instrumentor**: `openinference.instrumentation.mcp.MCPInstrumentor`
- **Install**: `pip install honeyhive[openinference-mcp]`

#### New OpenLLMetry Alternative
- **Package**: `openllmetry[mcp]`
- **Instrumentor**: `openllmetry.instrumentation.mcp.MCPInstrumentor`
- **Install**: `pip install honeyhive[openllmetry-mcp]`

#### Implementation Requirements
```python
def test_openllmetry_mcp_integration():
    """Test complete MCP integration with OpenLLMetry."""
    from honeyhive import HoneyHiveTracer
    from openllmetry.instrumentation.mcp import MCPInstrumentor
    import mcp
    
    tracer = HoneyHiveTracer.init(
        api_key="test-key",
        instrumentors=[MCPInstrumentor()]
    )
    
    # Test MCP client and server tracing
```

## Documentation Requirements

### Tabbed Interface Standard

All integration documentation must follow the tabbed interface pattern defined in `.praxis-os/standards/documentation-templates.md`:

```html
.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, 'provider-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'provider-openinference')">OpenInference</button>
     <button class="tab-button" onclick="showTab(event, 'provider-openllmetry')">OpenLLMetry</button>
   </div>

   <div id="provider-install" class="tab-content active">
```

### Documentation Structure for Each Provider

1. **Installation Tab**: Both OpenInference and OpenLLMetry installation options
2. **OpenInference Tab**: Current implementation (unchanged)
3. **OpenLLMetry Tab**: New alternative implementation

### Example: Updated OpenAI Documentation

```rst
Integrate with OpenAI
=====================

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, 'openai-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'openai-openinference')">OpenInference</button>
     <button class="tab-button" onclick="showTab(event, 'openai-openllmetry')">OpenLLMetry</button>
   </div>

   <div id="openai-install" class="tab-content active">

Installation Options
--------------------

Choose your preferred instrumentor provider:

**OpenInference (Recommended)**

.. code-block:: bash

   pip install honeyhive[openinference-openai]

**OpenLLMetry Alternative**  

.. code-block:: bash

   pip install honeyhive[openllmetry-openai]

.. raw:: html

   </div>
   <div id="openai-openinference" class="tab-content">

OpenInference Integration
-------------------------

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai

   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       instrumentors=[OpenAIInstrumentor()]
   )

   client = openai.OpenAI()
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )

.. raw:: html

   </div>
   <div id="openai-openllmetry" class="tab-content">

OpenLLMetry Integration  
-----------------------

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openllmetry.instrumentation.openai import OpenAIInstrumentor
   import openai

   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       instrumentors=[OpenAIInstrumentor()]
   )

   client = openai.OpenAI()
   response = client.chat.completions.create(
       model="gpt-3.5-turbo", 
       messages=[{"role": "user", "content": "Hello!"}]
   )

.. raw:: html

   </div>
   </div>
```

### Documentation Files to Update

1. `docs/how-to/integrations/openai.rst`
2. `docs/how-to/integrations/anthropic.rst`
3. `docs/how-to/integrations/google-ai.rst`
4. `docs/how-to/integrations/google-adk.rst`
5. `docs/how-to/integrations/aws-bedrock.rst`
6. `docs/how-to/integrations/azure-openai.rst`
7. `docs/how-to/integrations/mcp.rst`
8. `docs/how-to/integrations/multi-provider.rst`
9. `docs/how-to/integrations/index.rst`

## Testing Strategy

### Test Categories

#### 1. Primary Testing: Compatibility Matrix Tests
**Main testing approach following existing OpenInference pattern**

```python
# tests/compatibility_matrix/test_openllmetry_openai.py
def test_openllmetry_openai_integration():
    """Test complete OpenAI integration with OpenLLMetry (matches test_openai.py pattern)."""
    import os
    from honeyhive import HoneyHiveTracer
    from openllmetry.instrumentation.openai import OpenAIInstrumentor
    from openai import OpenAI
    
    # Check environment variables (same as existing tests)
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not all([api_key, project, openai_key]):
        return False
    
    # Initialize instrumentor and tracer
    tracer = HoneyHiveTracer.init(
        api_key=api_key,
        project=project,
        instrumentors=[OpenAIInstrumentor()],
        source="openllmetry_compatibility_test"
    )
    
    # Test API calls with automatic tracing
    client = OpenAI(api_key=openai_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "OpenLLMetry test"}],
        max_tokens=50
    )
    
    # Force flush and validate
    tracer.force_flush(timeout=10.0)
    return True
```



### Test Organization

```
tests/
├── compatibility_matrix/                     # PRIMARY AND ONLY TESTING LOCATION
│   ├── test_openllmetry_openai.py           # OpenLLMetry OpenAI integration
│   ├── test_openllmetry_anthropic.py        # OpenLLMetry Anthropic integration
│   ├── test_openllmetry_google_ai.py        # OpenLLMetry Google AI integration
│   ├── test_openllmetry_google_adk.py       # OpenLLMetry Google ADK integration
│   ├── test_openllmetry_bedrock.py          # OpenLLMetry Bedrock integration
│   ├── test_openllmetry_azure_openai.py     # OpenLLMetry Azure OpenAI integration
│   └── test_openllmetry_mcp.py              # OpenLLMetry MCP integration
├── unit/                                     # Existing SDK unit tests (unchanged)
└── integration/                              # Existing SDK integration tests (unchanged)
```

**Note**: Import validation and multi-instrumentor compatibility happen automatically in compatibility matrix tests. OpenTelemetry standard ensures instrumentors from different providers work together without conflicts.

## Implementation Details

### Package Naming Clarification

**Important**: Traceloop (OpenLLMetry) publishes their instrumentors using the standard OpenTelemetry naming convention:
- Package names: `opentelemetry-instrumentation-<provider>`
- Publisher: Traceloop Inc.
- Version range: `0.46.0,<1.0.0`

These are **NOT** the official OpenTelemetry instrumentors, but Traceloop's enhanced versions with additional LLM-specific features.

### PyProject.toml Updates

Add OpenLLMetry alternative dependencies to `pyproject.toml`:

```toml
[project.optional-dependencies]
# Existing OpenInference dependencies (unchanged)
openinference-openai = [
    "openinference-instrumentation-openai>=0.1.0",
    "openai>=1.0.0"
]
openinference-anthropic = [
    "openinference-instrumentation-anthropic>=0.1.0", 
    "anthropic>=0.18.0"
]
openinference-google-ai = [
    "openinference-instrumentation-google-generativeai>=0.1.0",
    "google-generativeai>=0.3.0"
]
openinference-google-adk = [
    "openinference-instrumentation-google-adk>=0.1.0",
    "google-adk>=0.1.0"
]
openinference-bedrock = [
    "openinference-instrumentation-bedrock>=0.1.0",
    "boto3>=1.26.0"
]
openinference-mcp = [
    "openinference-instrumentation-mcp>=0.1.0",
    "mcp>=0.1.0"
]

# New OpenLLMetry (Traceloop) alternatives - using individual instrumentor packages
# Note: These packages are named "opentelemetry-instrumentation-*" but are provided by Traceloop
traceloop-openai = [
    "opentelemetry-instrumentation-openai>=0.46.0,<1.0.0",  # Provided by Traceloop
    "openai>=1.0.0"
]
traceloop-anthropic = [
    "opentelemetry-instrumentation-anthropic>=0.46.0,<1.0.0",  # Provided by Traceloop
    "anthropic>=0.17.0"
]
traceloop-google-ai = [
    "opentelemetry-instrumentation-google-generativeai>=0.46.0,<1.0.0",  # Provided by Traceloop
    "google-generativeai>=0.3.0"
]
traceloop-aws-bedrock = [
    "opentelemetry-instrumentation-bedrock>=0.46.0,<1.0.0",  # Provided by Traceloop
    "boto3>=1.26.0"
]
traceloop-azure-openai = [
    "opentelemetry-instrumentation-openai>=0.46.0,<1.0.0",  # Provided by Traceloop (same package as OpenAI)
    "openai>=1.0.0",
    "azure-identity>=1.12.0"
]
traceloop-mcp = [
    "opentelemetry-instrumentation-mcp>=0.46.0,<1.0.0"  # Provided by Traceloop
]

# Convenience meta-packages
openinference-all = [
    "honeyhive[openinference-openai]",
    "honeyhive[openinference-anthropic]",
    "honeyhive[openinference-google-ai]",
    "honeyhive[openinference-google-adk]",
    "honeyhive[openinference-bedrock]",
    "honeyhive[openinference-mcp]"
]
all-traceloop = [
    "honeyhive[traceloop-openai]",
    "honeyhive[traceloop-anthropic]",
    "honeyhive[traceloop-google-ai]",
    "honeyhive[traceloop-aws-bedrock]",
    "honeyhive[traceloop-azure-openai]", 
    "honeyhive[traceloop-mcp]"
]
```

### Tox Configuration Updates

Update `tox.ini` to test OpenLLMetry integrations:

```ini
[testenv:traceloop-integration]
description = run Traceloop (OpenLLMetry) compatibility matrix tests
deps = 
    {[testenv]deps}
    opentelemetry-instrumentation-anthropic>=0.46.0,<1.0.0
    opentelemetry-instrumentation-openai>=0.46.0,<1.0.0
    anthropic>=0.17.0
    openai>=1.0.0
commands = 
    pytest {posargs:tests/compatibility_matrix} -k "traceloop" -v --asyncio-mode=auto --no-cov
```

### Examples Updates

Create new example files demonstrating OpenLLMetry usage:

```python
# examples/openllmetry_usage_example.py
"""
Example demonstrating HoneyHive integration with OpenLLMetry instrumentors.
"""
from honeyhive import HoneyHiveTracer
from openllmetry.instrumentation.openai import OpenAIInstrumentor
from openllmetry.instrumentation.anthropic import AnthropicInstrumentor
import openai
import anthropic

def main():
    """Demonstrate multi-provider tracing with OpenLLMetry."""
    
    # Initialize HoneyHive with OpenLLMetry instrumentors
    tracer = HoneyHiveTracer.init(
        api_key="your-honeyhive-api-key",
        project="openllmetry-demo",
        instrumentors=[
            OpenAIInstrumentor(),
            AnthropicInstrumentor()
        ]
    )
    
    print("🔧 HoneyHive initialized with OpenLLMetry instrumentors")
    
    # OpenAI usage (automatically traced)
    openai_client = openai.OpenAI()
    openai_response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "What is OpenLLMetry?"}]
    )
    print(f"✅ OpenAI response: {openai_response.choices[0].message.content[:50]}...")
    
    # Anthropic usage (automatically traced)
    anthropic_client = anthropic.Anthropic()
    anthropic_response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[{"role": "user", "content": "What is OpenLLMetry?"}]
    )
    print(f"✅ Anthropic response: {anthropic_response.content[0].text[:50]}...")
    
    print("🎉 All LLM calls automatically traced to HoneyHive!")

if __name__ == "__main__":
    main()
```

## Migration Guide

### For Existing OpenInference Users

Users currently using OpenInference instrumentors can optionally migrate to OpenLLMetry alternatives without changing their core HoneyHive integration:

#### Before (OpenInference)
```bash
pip install honeyhive[openinference-openai]
```

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    instrumentors=[OpenAIInstrumentor()]
)
```

#### After (OpenLLMetry Alternative)
```bash
pip uninstall openinference-instrumentation-openai
pip install honeyhive[openllmetry-openai]
```

```python
from honeyhive import HoneyHiveTracer
from openllmetry.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    instrumentors=[OpenAIInstrumentor()]
)
```

### Mixed Usage (Advanced)

Advanced users can mix OpenInference and OpenLLMetry instrumentors:

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor as OI_OpenAI
from openllmetry.instrumentation.anthropic import AnthropicInstrumentor as OLM_Anthropic

tracer = HoneyHiveTracer.init(
    api_key="your-api-key",
    instrumentors=[
        OI_OpenAI(),       # OpenInference for OpenAI
        OLM_Anthropic()    # OpenLLMetry for Anthropic
    ]
)
```

## Quality Assurance

### Code Quality Standards

1. **Type Annotations**: All OpenLLMetry integration code must have complete type annotations
2. **Docstrings**: Every function and class must have comprehensive docstrings
3. **Error Handling**: Graceful degradation when OpenLLMetry packages are not available
4. **Backwards Compatibility**: No breaking changes to existing OpenInference integrations

### Documentation Quality Standards

1. **Sphinx Warnings**: Zero Sphinx build warnings
2. **Code Examples**: All code examples must be tested and working
3. **Cross-References**: Proper linking between related documentation sections
4. **Accessibility**: WCAG 2.1 AA compliance for tabbed interfaces

### Test Coverage Requirements

1. **Unit Tests**: ≥ 90% code coverage for OpenLLMetry integration code
2. **Integration Tests**: Complete end-to-end testing for each provider
3. **Compatibility Tests**: Verification of mixed instrumentor usage
4. **Installation Tests**: Automated testing of package installation

### Performance Requirements

1. **Initialization Time**: OpenLLMetry instrumentors must initialize in < 100ms
2. **Memory Overhead**: < 5MB additional memory usage per instrumentor
3. **Tracing Overhead**: < 1ms latency impact per traced LLM call
4. **Documentation Build**: Sphinx documentation must build in < 60 seconds

### Success Metrics

1. **Functional Completeness**: 100% of OpenInference providers have OpenLLMetry alternatives
2. **Documentation Coverage**: All providers documented with tabbed interface
3. **Test Coverage**: ≥ 90% test coverage for all OpenLLMetry integration code
4. **Performance Parity**: OpenLLMetry performance within 10% of OpenInference
5. **User Experience**: Clear installation and usage instructions for all providers

## Conclusion

This specification provides a comprehensive plan for adding OpenLLMetry alternatives to all existing OpenInference integrations in the HoneyHive Python SDK. The implementation maintains backward compatibility while providing users with choice in their instrumentation provider, fulfilling the promise of the BYOI (Bring Your Own Instrumentor) architecture.

The tabbed documentation interface ensures users can easily compare options and choose the instrumentor provider that best meets their needs, while comprehensive testing ensures reliability across all provider combinations.

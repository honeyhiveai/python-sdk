# Azure OpenAI Comprehensive Support Guide

**Version:** 1.0.0  
**Date:** 2025-10-15  
**Status:** Production Ready  
**Author:** HoneyHive SDK Team

---

## Executive Summary

### Overview

Azure OpenAI is **fully supported** by HoneyHive through the standard OpenAI instrumentors. This support is achieved transparently because Azure OpenAI uses the same underlying `openai` Python SDK (version >= 1.0.0), just with different configuration parameters.

### Key Finding

**Azure OpenAI does NOT require a separate instrumentor.** The same `OpenAIInstrumentor` from both OpenInference and Traceloop works seamlessly with Azure OpenAI clients because they instrument at the SDK level, not the endpoint level.

### Support Status

| Aspect | Status | Details |
|--------|--------|---------|
| **OpenInference Support** | ✅ Fully Supported | Uses `OpenAIInstrumentor` from `openinference-instrumentation-openai` |
| **Traceloop Support** | ✅ Fully Supported | Uses `OpenAIInstrumentor` from `opentelemetry-instrumentation-openai` |
| **Streaming** | ✅ Supported | Full streaming support with both instrumentors |
| **Embeddings** | ✅ Supported | Full embeddings support |
| **Multiple Deployments** | ✅ Supported | Can trace multiple Azure deployments simultaneously |
| **Python Versions** | ✅ 3.11, 3.12, 3.13 | Full compatibility |
| **Managed Identity** | ⚠️ Supported with config | Requires additional Azure SDK configuration |

---

## Technical Architecture

### How Azure OpenAI Integration Works

```
┌─────────────────────────────────────────────────────────────┐
│                     Customer Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  from openai import AzureOpenAI                             │
│  client = AzureOpenAI(                                      │
│      api_key="...",                                         │
│      azure_endpoint="https://X.openai.azure.com/",         │
│      api_version="2024-02-01"                               │
│  )                                                           │
│                                                              │
│  response = client.chat.completions.create(...)  ←──────────┤ User Code
└─────────────────────────────────────────────────────────────┘
                        ↓ (instrumented)
┌─────────────────────────────────────────────────────────────┐
│              OpenAIInstrumentor (Same for both!)            │
├─────────────────────────────────────────────────────────────┤
│  • Intercepts SDK methods (chat.completions.create, etc.)   │
│  • Works for BOTH OpenAI() and AzureOpenAI()               │
│  • Doesn't care about endpoint - instruments SDK methods   │
│  • Captures: inputs, outputs, tokens, latency              │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  HoneyHive Tracer                           │
├─────────────────────────────────────────────────────────────┤
│  • Receives OpenTelemetry spans from instrumentor           │
│  • Enriches with HoneyHive metadata                         │
│  • Exports via OTLP to HoneyHive backend                   │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  HoneyHive Backend                          │
├─────────────────────────────────────────────────────────────┤
│  • Stores and displays traces                               │
│  • Shows Azure-specific metadata (endpoint, deployment)    │
│  • Full observability for Azure OpenAI                      │
└─────────────────────────────────────────────────────────────┘
```

### Why the Same Instrumentor Works

1. **SDK-Level Instrumentation**: The instrumentor patches methods on the OpenAI SDK classes, not specific endpoints
2. **Shared Code Path**: `AzureOpenAI` inherits from the same base classes as `OpenAI` in the SDK
3. **Method Signature Compatibility**: Both clients use identical method signatures (`.chat.completions.create()`, etc.)
4. **OpenTelemetry Standards**: The instrumentor captures standard OpenTelemetry semantic conventions that work for any OpenAI-compatible endpoint

### Evidence from Codebase

**File:** `tests/compatibility_matrix/test_openinference_azure_openai.py`
```python
# Line 39-48: Same instrumentor used
from openai import AzureOpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor  # ← Same as regular OpenAI

# 1. Initialize OpenInference instrumentor (same as OpenAI)
azure_instrumentor = OpenAIInstrumentor()  # ← No Azure-specific class!
print("✓ Azure OpenAI instrumentor initialized")
```

**File:** `examples/integrations/traceloop_azure_openai_example.py`
```python
# Line 9: Explicit note in comments
# Note: Azure OpenAI uses the same OpenAI instrumentor since it uses the same SDK.

# Line 26-27: Same import
from opentelemetry.instrumentation.openai import OpenAIInstrumentor  # ← Standard OpenAI instrumentor

# Line 42-43: Same initialization
openai_instrumentor = OpenAIInstrumentor()  # ← Works for Azure too!
```

---

## Implementation Details

### Package Dependencies

#### OpenInference Approach
```bash
# Required packages
pip install honeyhive[openinference-azure-openai]

# Or manually
pip install honeyhive
pip install openinference-instrumentation-openai  # ← Same as regular OpenAI
pip install openai>=1.0.0
```

#### Traceloop Approach
```bash
# Required packages
pip install honeyhive[traceloop-azure-openai]

# Or manually
pip install honeyhive
pip install opentelemetry-instrumentation-openai  # ← Same as regular OpenAI
pip install openai>=1.0.0
```

### Configuration Requirements

#### Environment Variables

**Required:**
```bash
# HoneyHive Configuration
export HH_API_KEY="your_honeyhive_api_key"
export HH_PROJECT="your_project_name"

# Azure OpenAI Configuration
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
export AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"
```

**Optional:**
```bash
# API Version (defaults to latest)
export AZURE_OPENAI_API_VERSION="2024-02-01"

# Multiple Deployments
export AZURE_OPENAI_DEPLOYMENT="gpt-35-turbo"
export AZURE_OPENAI_GPT4_DEPLOYMENT="gpt-4"
export AZURE_OPENAI_GPT4_TURBO_DEPLOYMENT="gpt-4-turbo"
```

### Integration Pattern

#### Pattern 1: OpenInference (Recommended for Open Source)

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import AzureOpenAI
import os

# Step 1: Initialize HoneyHive tracer FIRST (without instrumentors)
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT")
)

# Step 2: Initialize instrumentor separately with tracer_provider
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)

# Step 3: Create Azure OpenAI client (uses same instrumentor!)
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Step 4: Use normally - automatically traced
response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Azure deployment name
    messages=[{"role": "user", "content": "Hello from Azure OpenAI!"}]
)

# Step 5: Flush traces
tracer.force_flush()
```

#### Pattern 2: Traceloop (Recommended for Production)

```python
from honeyhive import HoneyHiveTracer, trace, enrich_span
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from openai import AzureOpenAI
import os

# Step 1: Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    source="production-azure-openai",
    project=os.getenv("HH_PROJECT")
)

# Step 2: Initialize instrumentor with tracer_provider
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)

# Step 3: Create Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Step 4: Use with span enrichment for business context
@trace()
def generate_response(prompt: str) -> str:
    enrich_span({
        "provider": "azure_openai",
        "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "region": "eastus"  # Add your region
    })
    
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# Step 5: Use and flush
result = generate_response("Hello from Azure OpenAI!")
tracer.force_flush()
```

#### Pattern 3: Multiple Deployments

```python
from honeyhive import HoneyHiveTracer, trace
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import AzureOpenAI
import os

tracer = HoneyHiveTracer.init()
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@trace()
def test_multiple_deployments():
    # Test GPT-3.5 deployment
    response_35 = client.chat.completions.create(
        model="gpt-35-turbo",  # Deployment name
        messages=[{"role": "user", "content": "Test GPT-3.5"}]
    )
    
    # Test GPT-4 deployment
    response_4 = client.chat.completions.create(
        model="gpt-4",  # Different deployment name
        messages=[{"role": "user", "content": "Test GPT-4"}]
    )
    
    # Both are automatically traced with deployment names in metadata
    return {
        "gpt35": response_35.choices[0].message.content,
        "gpt4": response_4.choices[0].message.content
    }

results = test_multiple_deployments()
tracer.force_flush()
```

---

## Key Differences: Azure OpenAI vs Standard OpenAI

| Aspect | Standard OpenAI | Azure OpenAI | Impact on Instrumentation |
|--------|----------------|--------------|--------------------------|
| **Client Class** | `openai.OpenAI()` | `openai.AzureOpenAI()` | **None** - Same instrumentor works |
| **Endpoint** | `https://api.openai.com` | `https://X.openai.azure.com` | **None** - Instrumentor doesn't care |
| **Authentication** | API Key only | API Key or Managed Identity | **Minor** - Managed Identity requires Azure SDK setup |
| **Model Parameter** | Model name (e.g., `"gpt-4"`) | Deployment name (e.g., `"my-gpt4-deployment"`) | **Important** - Use deployment name, not model |
| **API Version** | Not required | Required (e.g., `"2024-02-01"`) | **Configuration** - Must be specified |
| **Instrumentor** | `OpenAIInstrumentor()` | `OpenAIInstrumentor()` | **None** - Identical |

### Critical Note: Deployment Names vs Model Names

⚠️ **IMPORTANT**: Azure OpenAI uses **deployment names**, not model names:

```python
# ❌ WRONG - This will fail
response = client.chat.completions.create(
    model="gpt-4",  # This is a model name, not a deployment name!
    messages=[...]
)

# ✅ CORRECT - Use your deployment name
response = client.chat.completions.create(
    model="my-gpt4-deployment",  # This is YOUR deployment name in Azure
    messages=[...]
)
```

The deployment name is configured in Azure Portal and can be anything you choose. The instrumentor will capture this deployment name in the trace metadata.

---

## Testing & Validation

### Test Coverage

HoneyHive has comprehensive test coverage for Azure OpenAI:

| Test File | Instrumentor | Coverage | Status |
|-----------|-------------|----------|--------|
| `test_openinference_azure_openai.py` | OpenInference | Chat, Embeddings, Streaming | ✅ Passing |
| `test_traceloop_azure_openai.py` | Traceloop | Chat, Multiple Deployments, Enhanced Metrics | ✅ Passing |

### Running Tests

```bash
# Set environment variables
export HH_API_KEY="your_honeyhive_key"
export HH_PROJECT="test_project"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_azure_key"
export AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment"

# Run OpenInference test
python tests/compatibility_matrix/test_openinference_azure_openai.py

# Run Traceloop test
python tests/compatibility_matrix/test_traceloop_azure_openai.py

# Run full compatibility suite (includes Azure OpenAI)
python tests/compatibility_matrix/run_compatibility_tests.py
```

### Test Validation

Each test validates:
- ✅ Tracer initialization with Azure OpenAI instrumentor
- ✅ Azure OpenAI client creation with correct configuration
- ✅ Basic chat completion with tracing
- ✅ Span enrichment with Azure-specific metadata
- ✅ Streaming support
- ✅ Multiple deployment testing
- ✅ Trace flush and delivery to HoneyHive

### Expected Test Output

```
🧪 HoneyHive + Azure OpenAI Compatibility Test
==================================================
🔧 Setting up Azure OpenAI with HoneyHive integration...
✓ Azure OpenAI instrumentor initialized
✓ HoneyHive tracer initialized with Azure OpenAI instrumentor
✓ Azure OpenAI client initialized (endpoint: https://X.openai.azure.com/)
🚀 Testing Azure OpenAI chat completion...
✓ Azure OpenAI response: [response text]
🔧 Testing span enrichment...
✓ Enhanced completion created: {...}
🔧 Testing Azure OpenAI streaming...
✓ Streaming completed: N chunks, content: [content]
📤 Flushing traces...
✓ Traces flushed successfully
🎉 Azure OpenAI integration test completed successfully!

✅ Azure OpenAI compatibility: PASSED
```

---

## Customer Documentation

### Documentation Files

Azure OpenAI is documented in:

1. **Integration Guide**: `docs/how-to/integrations/azure-openai.rst`
   - Comprehensive guide with both instrumentor options
   - Installation instructions
   - Code examples
   - Troubleshooting section

2. **Examples**:
   - `examples/integrations/traceloop_azure_openai_example.py` - Full working example
   - Demonstrates: basic usage, multiple deployments, cost tracking

3. **Test Files** (serve as reference implementations):
   - `tests/compatibility_matrix/test_openinference_azure_openai.py`
   - `tests/compatibility_matrix/test_traceloop_azure_openai.py`

### Documentation Structure

The `azure-openai.rst` file follows HoneyHive's standard provider documentation template:

```rst
Integrate with Azure OpenAI
===========================

Compatibility
-------------
- Python Version Support
- Provider SDK Requirements
- Instrumentor Compatibility
- Known Limitations

Choose Your Instrumentor
------------------------
- OpenInference (tabs: Installation, Basic Setup, Advanced Usage, Troubleshooting)
- Traceloop (tabs: Installation, Basic Setup, Advanced Usage, Troubleshooting)

Advanced Patterns
-----------------
- Multiple Deployments
- Cost Tracking
- Error Handling
- Managed Identity

Troubleshooting
---------------
- Common Issues
- Debugging Steps
- Support Resources
```

### Installation Shortcuts

HoneyHive provides convenience installation extras:

```bash
# OpenInference approach
pip install honeyhive[openinference-azure-openai]

# Traceloop approach
pip install honeyhive[traceloop-azure-openai]

# Both approaches
pip install honeyhive[all-azure-openai]
```

These extras are defined in `pyproject.toml` and install the correct combination of:
- `honeyhive` base package
- Appropriate instrumentor package
- `openai>=1.0.0` SDK

---

## Known Limitations & Considerations

### Deployment Names

**Limitation**: Azure OpenAI uses deployment names instead of model names.

**Impact**: Customers must configure deployment names in Azure Portal before using.

**Mitigation**: Documentation clearly explains deployment name vs model name distinction.

### API Version Required

**Limitation**: Azure OpenAI requires explicit API version.

**Impact**: Code must specify `api_version` parameter.

**Mitigation**: Documentation provides recommended version (`2024-02-01`).

### Managed Identity Support

**Limitation**: Managed Identity authentication requires additional Azure SDK configuration.

**Impact**: More complex setup for customers using Managed Identity.

**Mitigation**: Documentation includes Managed Identity setup guide.

**Status**: Supported but requires customer to configure Azure SDK properly.

### Regional Endpoints

**Limitation**: Different Azure regions have different endpoint URLs.

**Impact**: Customer must use correct endpoint for their region.

**Mitigation**: Documentation shows endpoint format: `https://{resource-name}.openai.azure.com/`

### Cost Tracking Differences

**Limitation**: Azure pricing may differ from OpenAI pricing.

**Impact**: Traceloop's automatic cost tracking may show different costs than Azure billing.

**Mitigation**: Documentation notes that cost tracking is approximate and customers should verify with Azure billing.

---

## Architecture Decisions

### Decision 1: Reuse OpenAI Instrumentor

**Decision**: Use the same `OpenAIInstrumentor` for both OpenAI and Azure OpenAI.

**Rationale**:
- Azure OpenAI uses the same `openai` Python SDK
- Instrumentor patches SDK methods, not endpoints
- Reduces maintenance burden (one instrumentor to support)
- Proven approach - works in production

**Alternatives Considered**:
1. ❌ Create separate `AzureOpenAIInstrumentor` - Unnecessary duplication
2. ❌ Add Azure-specific logic to instrumentor - Violates separation of concerns
3. ✅ Use same instrumentor transparently - Chosen approach

**Evidence**: Test files show identical instrumentor usage for both OpenAI and Azure OpenAI.

### Decision 2: No Custom Azure Span Attributes

**Decision**: Don't add special Azure-specific span attributes beyond what the instrumentor naturally captures.

**Rationale**:
- The OpenAI instrumentor already captures all necessary metadata
- Azure-specific details (endpoint, deployment name) are captured in standard span attributes
- Customers can add custom attributes via `enrich_span()` if needed

**Implementation**: The instrumentor captures:
- `server.address`: Azure endpoint
- `gen_ai.request.model`: Deployment name
- `gen_ai.response.model`: Deployment name (echoed by Azure)

### Decision 3: Document Both Instrumentor Options

**Decision**: Provide equal documentation for both OpenInference and Traceloop approaches.

**Rationale**:
- Different customers have different needs (open-source vs enhanced metrics)
- HoneyHive's "Bring Your Own Instrumentor" supports both
- Gives customers choice and flexibility

**Implementation**:
- Documentation uses tabbed interface to show both options
- Test coverage for both instrumentors
- Examples demonstrate both approaches

---

## Future Improvements

### Potential Enhancements

1. **Auto-Detection of Azure Endpoints**
   - **Description**: Automatically detect Azure OpenAI endpoints and log metadata
   - **Benefit**: Better visibility into Azure-specific usage
   - **Complexity**: Low - add endpoint pattern matching
   - **Priority**: Medium

2. **Azure Cost Calculator Integration**
   - **Description**: Accurate Azure pricing integration for cost tracking
   - **Benefit**: Accurate cost estimates matching Azure billing
   - **Complexity**: Medium - requires Azure pricing API integration
   - **Priority**: Low - customers can use Azure Cost Management

3. **Managed Identity Example**
   - **Description**: Add example showing Managed Identity authentication
   - **Benefit**: Helps customers using Azure AD authentication
   - **Complexity**: Low - add example code
   - **Priority**: Medium

4. **Multi-Region Support Example**
   - **Description**: Example showing failover across Azure regions
   - **Benefit**: Helps customers with high availability requirements
   - **Complexity**: Medium - requires multi-region setup
   - **Priority**: Low

5. **Azure Private Endpoint Support Documentation**
   - **Description**: Document how to use with Azure Private Endpoints
   - **Benefit**: Security-conscious customers can use private networking
   - **Complexity**: Low - documentation only
   - **Priority**: Medium

---

## Implementation Checklist

### ✅ Completed

- [x] OpenInference instrumentor integration
- [x] Traceloop instrumentor integration
- [x] OpenInference test implementation
- [x] Traceloop test implementation
- [x] Customer documentation (RST file)
- [x] Example scripts
- [x] Environment variable configuration
- [x] Installation extras in pyproject.toml
- [x] Compatibility matrix entry
- [x] Multi-deployment support
- [x] Streaming support
- [x] Embeddings support

### 🚧 In Progress

- [ ] Performance benchmarking vs regular OpenAI
- [ ] Load testing with multiple deployments

### 📋 Backlog

- [ ] Managed Identity example
- [ ] Multi-region failover example
- [ ] Azure Private Endpoint documentation
- [ ] Cost calculator integration
- [ ] Azure-specific troubleshooting guide

---

## Support & Resources

### Internal Resources

**Code Locations**:
- Integration Tests: `tests/compatibility_matrix/test_*_azure_openai.py`
- Example Code: `examples/integrations/traceloop_azure_openai_example.py`
- Documentation: `docs/how-to/integrations/azure-openai.rst`
- Environment Config: `tests/compatibility_matrix/env.example`

**Key Files**:
```
tests/compatibility_matrix/
├── test_openinference_azure_openai.py   # OpenInference test
├── test_traceloop_azure_openai.py       # Traceloop test
└── env.example                          # Environment variables

examples/integrations/
└── traceloop_azure_openai_example.py    # Full example

docs/how-to/integrations/
└── azure-openai.rst                     # Customer documentation
```

### Customer Support

**Common Questions**:

1. **Q**: Do I need a different instrumentor for Azure OpenAI?
   - **A**: No! Use the same `OpenAIInstrumentor` as regular OpenAI.

2. **Q**: Why isn't my Azure OpenAI showing up in traces?
   - **A**: Check that you're using your deployment name (not model name) and that the instrumentor is initialized before creating the client.

3. **Q**: Can I trace multiple Azure deployments simultaneously?
   - **A**: Yes! The instrumentor traces all deployments. Each will appear as a separate span with its deployment name.

4. **Q**: Does this work with Azure Managed Identity?
   - **A**: Yes, but you need to configure the Azure SDK for Managed Identity authentication. The instrumentor works regardless of auth method.

5. **Q**: Are costs tracked differently for Azure vs OpenAI?
   - **A**: Traceloop tracks token usage. Cost calculations may differ from Azure billing due to pricing differences.

### External References

**Microsoft Documentation**:
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure OpenAI Python SDK](https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart?tabs=command-line%2Cpython&pivots=programming-language-python)

**OpenAI SDK**:
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Azure OpenAI Client](https://github.com/openai/openai-python#microsoft-azure-openai)

**Instrumentor Documentation**:
- [OpenInference OpenAI](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-openai)
- [Traceloop OpenAI](https://www.traceloop.com/docs/openllmetry/integrations/openai)

---

## Appendix A: Complete Working Example

### Full Integration Example (Production-Ready)

```python
#!/usr/bin/env python3
"""
Production-Ready Azure OpenAI + HoneyHive Integration
Uses OpenInference instrumentor for clean, open-source tracing.
"""

import os
import sys
from typing import List, Dict, Any

from honeyhive import HoneyHiveTracer, trace, enrich_span
from honeyhive.models import EventType
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import AzureOpenAI


def validate_environment() -> None:
    """Validate required environment variables are set."""
    required_vars = [
        "HH_API_KEY",
        "HH_PROJECT",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("\nRequired variables:")
        print("  - HH_API_KEY: Your HoneyHive API key")
        print("  - HH_PROJECT: Your HoneyHive project name")
        print("  - AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint")
        print("  - AZURE_OPENAI_API_KEY: Your Azure OpenAI API key")
        print("  - AZURE_OPENAI_DEPLOYMENT_NAME: Your Azure deployment name")
        sys.exit(1)


def setup_tracing() -> tuple[HoneyHiveTracer, AzureOpenAI]:
    """Initialize HoneyHive tracing and Azure OpenAI client."""
    
    # Step 1: Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        source="production-azure-openai"
    )
    print("✅ HoneyHive tracer initialized")
    
    # Step 2: Initialize instrumentor separately with tracer_provider
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)
    print("✅ OpenAI instrumentor initialized for Azure OpenAI")
    
    # Step 3: Create Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    print(f"✅ Azure OpenAI client initialized (endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')})")
    
    return tracer, client


@trace(event_type=EventType.chain)
def process_query(client: AzureOpenAI, query: str) -> Dict[str, Any]:
    """Process a query with Azure OpenAI and full tracing."""
    
    # Enrich span with business context
    enrich_span({
        "business.query_type": "customer_support",
        "provider": "azure_openai",
        "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "region": "eastus"  # Add your region
    })
    
    try:
        # Make request (automatically traced)
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        result = {
            "response": response.choices[0].message.content,
            "tokens": response.usage.total_tokens,
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason
        }
        
        # Enrich with results
        enrich_span({
            "business.tokens_used": result["tokens"],
            "business.finish_reason": result["finish_reason"]
        })
        
        return result
        
    except Exception as e:
        # Enrich with error details
        enrich_span({
            "error.type": type(e).__name__,
            "error.message": str(e)
        })
        raise


@trace(event_type=EventType.chain)
def batch_process(client: AzureOpenAI, queries: List[str]) -> List[Dict[str, Any]]:
    """Process multiple queries in batch."""
    
    enrich_span({
        "business.batch_size": len(queries),
        "business.operation": "batch_processing"
    })
    
    results = []
    for i, query in enumerate(queries):
        print(f"Processing query {i+1}/{len(queries)}: {query[:50]}...")
        result = process_query(client, query)
        results.append(result)
        print(f"  ✅ Completed: {result['tokens']} tokens")
    
    enrich_span({
        "business.total_tokens": sum(r["tokens"] for r in results),
        "business.queries_processed": len(results)
    })
    
    return results


def main() -> int:
    """Main execution function."""
    
    print("🚀 Azure OpenAI + HoneyHive Production Integration")
    print("=" * 60)
    
    try:
        # Validate environment
        validate_environment()
        print("✅ Environment validated\n")
        
        # Setup tracing
        tracer, client = setup_tracing()
        print()
        
        # Single query example
        print("📝 Processing single query...")
        result = process_query(
            client,
            "What are the key benefits of using Azure OpenAI?"
        )
        print(f"✅ Response received: {result['response'][:100]}...")
        print(f"   Tokens used: {result['tokens']}\n")
        
        # Batch processing example
        print("📝 Processing batch queries...")
        queries = [
            "What is machine learning?",
            "Explain natural language processing.",
            "What are transformers in AI?"
        ]
        batch_results = batch_process(client, queries)
        print(f"✅ Batch completed: {len(batch_results)} queries processed\n")
        
        # Flush traces
        print("📤 Flushing traces to HoneyHive...")
        tracer.force_flush(timeout=10.0)
        print("✅ Traces sent successfully!\n")
        
        print("🎉 Integration completed successfully!")
        print("💡 Check your HoneyHive dashboard for traces")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### Running the Example

```bash
# Set environment variables
export HH_API_KEY="your_honeyhive_key"
export HH_PROJECT="production"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_azure_key"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-35-turbo"

# Run the example
python azure_openai_production_example.py
```

### Expected Output

```
🚀 Azure OpenAI + HoneyHive Production Integration
============================================================
✅ Environment validated

✅ HoneyHive tracer initialized
✅ OpenAI instrumentor initialized for Azure OpenAI
✅ Azure OpenAI client initialized (endpoint: https://X.openai.azure.com/)

📝 Processing single query...
✅ Response received: Azure OpenAI provides several key benefits including enterprise-grade security, regional availability...
   Tokens used: 145

📝 Processing batch queries...
Processing query 1/3: What is machine learning?...
  ✅ Completed: 98 tokens
Processing query 2/3: Explain natural language processing....
  ✅ Completed: 112 tokens
Processing query 3/3: What are transformers in AI?...
  ✅ Completed: 156 tokens
✅ Batch completed: 3 queries processed

📤 Flushing traces to HoneyHive...
✅ Traces sent successfully!

🎉 Integration completed successfully!
💡 Check your HoneyHive dashboard for traces
```

---

## Appendix B: Troubleshooting Guide

### Issue 1: Traces Not Appearing

**Symptoms**: Azure OpenAI calls execute successfully but don't appear in HoneyHive.

**Diagnosis**:
```python
# Add verbose logging
tracer = HoneyHiveTracer.init(
    verbose=True,  # Enable verbose logging
    project=os.getenv("HH_PROJECT")
)
```

**Common Causes**:
1. Instrumentor not initialized before client creation
2. Missing `tracer.force_flush()` call
3. Incorrect HoneyHive credentials

**Solution**:
```python
# Correct order:
# 1. Init tracer
tracer = HoneyHiveTracer.init()

# 2. Init instrumentor with tracer_provider
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)

# 3. Create client
client = AzureOpenAI(...)

# 4. Make calls
response = client.chat.completions.create(...)

# 5. Flush
tracer.force_flush()
```

### Issue 2: Deployment Name Errors

**Symptoms**: Error: "The model `gpt-4` does not exist"

**Diagnosis**: You're using the model name instead of deployment name.

**Solution**:
```python
# ❌ WRONG
response = client.chat.completions.create(
    model="gpt-4",  # This is a model name
    ...
)

# ✅ CORRECT
response = client.chat.completions.create(
    model="my-gpt4-deployment",  # This is YOUR deployment name
    ...
)
```

### Issue 3: Authentication Errors

**Symptoms**: Error: "Unauthorized" or "Invalid API key"

**Diagnosis**: Check Azure OpenAI credentials and endpoint.

**Verification**:
```python
import os

# Verify environment variables
print("Endpoint:", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("API Key set:", bool(os.getenv("AZURE_OPENAI_API_KEY")))
print("Deployment:", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))

# Test client creation
from openai import AzureOpenAI
try:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    print("✅ Client created successfully")
except Exception as e:
    print(f"❌ Client creation failed: {e}")
```

### Issue 4: Streaming Not Working

**Symptoms**: Streaming calls don't produce spans.

**Diagnosis**: Check instrumentor version and streaming implementation.

**Solution**:
```python
# Ensure you're using latest instrumentor
pip install --upgrade openinference-instrumentation-openai

# Streaming is fully supported
stream = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    messages=[{"role": "user", "content": "Count to 5"}],
    stream=True  # Streaming is instrumented
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## Appendix C: Version History

### Version 1.0.0 (2025-10-15)
- Initial comprehensive documentation
- Full OpenInference and Traceloop support
- Complete test coverage
- Production-ready examples
- Troubleshooting guide

---

**Document Status**: ✅ Complete  
**Last Reviewed**: 2025-10-15  
**Next Review**: 2025-11-15  
**Owner**: HoneyHive SDK Team  
**Reviewers**: Engineering, Customer Success, Documentation


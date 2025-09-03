# Documentation Templates Standards

**Date**: 2025-01-24  
**Status**: Active  
**Scope**: All integration documentation  

## Overview

This document defines standard templates and patterns for creating consistent, user-friendly documentation across all HoneyHive integrations.

## Instrumentor Documentation Standard

### 🎯 **MANDATORY: Tabbed Interface Pattern**

All new instrumentor integration documentation **MUST** use the interactive tabbed interface pattern. This provides progressive disclosure and consistent user experience.

#### Required Tab Structure

Every instrumentor doc must include exactly **3 tabs**:

1. **Installation Tab** - Package installation instructions
2. **Basic Setup Tab** - Simple working example
3. **Advanced Usage Tab** - Real-world patterns with @trace decorator

#### Implementation Template

```rst
Integration with [Provider Name]
===============================

Learn how to integrate HoneyHive with [Provider] using the BYOI (Bring Your Own Instrumentor) approach.

Quick Start
-----------

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, '[provider]-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, '[provider]-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, '[provider]-advanced')">Advanced Usage</button>
   </div>

   <div id="[provider]-install" class="tab-content active">

.. code-block:: bash

   # Recommended: Install with [Provider] integration
   pip install honeyhive[[provider]]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-[provider] [provider-sdk]

.. raw:: html

   </div>
   <div id="[provider]-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.[provider] import [Provider]Instrumentor
   import [provider_sdk]
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # [PROVIDER]_API_KEY=your-[provider]-key

   # Initialize with environment variables (secure)
   tracer = HoneyHiveTracer.init(
       instrumentors=[[Provider]Instrumentor()]  # Uses HH_API_KEY automatically
   )

   # Basic usage with error handling
   try:
       client = [provider_sdk].[ClientClass]()  # Uses [PROVIDER]_API_KEY automatically
       # [Provider-specific API call example]
       # Automatically traced! ✨
   except [provider_sdk].[ProviderAPIError] as e:
       print(f"[Provider] API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="[provider]-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.[provider] import [Provider]Instrumentor
   import [provider_sdk]

   # Initialize with custom configuration
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       source="production",
       instrumentors=[[Provider]Instrumentor()]
   )

   @trace(tracer=tracer, event_type="chain")
   def [advanced_function_name](input_param: str) -> dict:
       """Advanced example with business context and multiple [provider] calls."""
       client = [provider_sdk].[ClientClass]()
       
       # Add business context to the trace
       enrich_span({
           "[business_context].input_type": type(input_param).__name__,
           "[business_context].use_case": "[specific_use_case]",
           "[provider].strategy": "[model_selection_strategy]"
       })
       
       try:
           # [First API call with specific model/configuration]
           # [Second API call with different model/configuration]
           
           # Add result metadata
           enrich_span({
               "[business_context].successful": True,
               "[provider].models_used": ["[model1]", "[model2]"],
               "[business_context].result_metrics": "[relevant_metrics]"
           })
           
           return results
           
       except [provider_sdk].[ProviderAPIError] as e:
           enrich_span({"error.type": "api_error", "error.message": str(e)})
           raise

.. raw:: html

   </div>
   </div>

[Rest of documentation content...]

.. raw:: html

   <script>
   function showTab(evt, tabName) {
     var i, tabcontent, tablinks;
     tabcontent = document.getElementsByClassName("tab-content");
     for (i = 0; i < tabcontent.length; i++) {
       tabcontent[i].classList.remove("active");
     }
     tablinks = document.getElementsByClassName("tab-button");
     for (i = 0; i < tablinks.length; i++) {
       tablinks[i].classList.remove("active");
     }
     document.getElementById(tabName).classList.add("active");
     evt.currentTarget.classList.add("active");
   }
   </script>
   
   <style>
   .code-example {
     margin: 1.5rem 0;
     border: 1px solid #ddd;
     border-radius: 8px;
     overflow: hidden;
   }
   .code-tabs {
     display: flex;
     background: #f8f9fa;
     border-bottom: 1px solid #ddd;
   }
   .tab-button {
     background: none;
     border: none;
     padding: 12px 20px;
     cursor: pointer;
     font-weight: 500;
     color: #666;
     transition: all 0.2s ease;
   }
   .tab-button:hover {
     background: #e9ecef;
     color: #2980b9;
   }
   .tab-button.active {
     background: #2980b9;
     color: white;
     border-bottom: 2px solid #2980b9;
   }
   .tab-content {
     display: none;
     padding: 0;
   }
   .tab-content.active {
     display: block;
   }
   .tab-content .highlight {
     margin: 0;
     border-radius: 0;
   }
   </style>
```

### Content Requirements

#### Installation Tab Content
- **MUST** show `pip install honeyhive[[provider]]` first
- **MUST** include alternative manual installation
- **MUST** be copy-paste ready

#### Basic Setup Tab Content
- **MUST** be a complete, working example
- **MUST** show instrumentor initialization
- **MUST** demonstrate automatic tracing
- **MUST** include environment variables setup (.env file example)
- **MUST** include basic error handling (try/except with provider-specific exceptions)
- **MUST** show secure API key usage (environment variables, not hardcoded)
- **SHOULD** be copy-paste ready for immediate use

#### Advanced Usage Tab Content
- **MUST** use `@trace` decorator with `event_type` parameter
- **MUST** use `enrich_span()` to add business context metadata
- **MUST** show multiple API calls in one function
- **MUST** include comprehensive error handling with span enrichment
- **MUST** demonstrate real-world patterns (business context, multiple models, result metadata)
- **MUST** show provider-specific optimization strategies
- **SHOULD** include provider-specific best practices
- **SHOULD** demonstrate different model usage patterns where applicable

### Naming Conventions

#### Tab IDs
- Installation: `[provider]-install`
- Basic Setup: `[provider]-basic`  
- Advanced Usage: `[provider]-advanced`

#### Function Names (Advanced Tab)
Choose descriptive names that reflect the provider's strength:
- OpenAI: `analyze_sentiment`, `content_generator`
- Anthropic: `research_assistant`, `document_analyzer`
- Google AI: `content_pipeline`, `multi_modal_analysis`
- AWS Bedrock: `multi_model_comparison`, `enterprise_workflow`

### File Structure

```
docs/how-to/integrations/
├── [provider].rst           # Main integration doc with tabs
├── index.rst               # Updated to include new provider
└── multi-provider.rst      # Updated with new provider example
```

### Validation Checklist

Before merging any new instrumentor documentation:

- [ ] **Tab Structure**: All 3 tabs present and functional
- [ ] **Installation**: Both recommended (`pip install honeyhive[provider]`) and manual installation shown
- [ ] **Basic Example**: Complete, working, copy-paste ready with environment variables and error handling
- [ ] **Environment Variables**: .env file example included in Basic Setup tab
- [ ] **Error Handling**: Provider-specific exceptions handled in both Basic and Advanced tabs
- [ ] **Advanced Example**: Uses @trace decorator with enrich_span() for business context
- [ ] **Business Context**: Advanced tab demonstrates real-world metadata and multiple model usage
- [ ] **Security**: No hardcoded API keys, environment variables used throughout
- [ ] **CSS/JS**: Styling and script blocks included at end
- [ ] **Naming**: Consistent tab IDs and descriptive function names
- [ ] **Optional Dependencies**: Provider added to pyproject.toml
- [ ] **Index Update**: Provider listed in integrations index
- [ ] **Documentation Build**: Sphinx builds without warnings
- [ ] **Content Consolidation**: Redundant sections removed (environment variables, basic business context moved to tabs)

### Benefits

This standardized approach provides:

1. **Consistent UX**: Same pattern across all providers
2. **Progressive Disclosure**: Users start simple, advance gradually
3. **Professional Appearance**: Matches landing page quality
4. **Faster Onboarding**: Clear learning path for developers
5. **Maintainable Code**: Reusable template reduces effort

## Legacy Documentation

Existing integration docs without tabs should be gradually updated to use this pattern during routine maintenance or major updates.

## Reference Examples

See these fully implemented examples:
- `docs/how-to/integrations/openai.rst`
- `docs/how-to/integrations/anthropic.rst`
- `docs/how-to/integrations/google-ai.rst`
- `docs/how-to/integrations/aws-bedrock.rst`
- `docs/how-to/integrations/azure-openai.rst`

## Related Standards

- **Optional Dependencies**: `.agent-os/standards/pyproject-dependencies.md`
- **Code Style**: `.agent-os/standards/code-style.md`
- **Documentation Quality**: `.agent-os/specs/2025-09-03-documentation-quality-control/`

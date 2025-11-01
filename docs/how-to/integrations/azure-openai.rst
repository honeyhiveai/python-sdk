Integrate with Azure OpenAI
===========================

.. note::
   **Problem-solving guide for Azure OpenAI integration**
   
   This guide helps you solve specific problems when integrating HoneyHive with Azure OpenAI, with support for multiple instrumentor options.

This guide covers Azure OpenAI integration with HoneyHive's BYOI architecture, supporting both OpenInference and Traceloop instrumentors.

Compatibility
-------------

**Problem**: I need to know if my Python version and Azure OpenAI SDK version are compatible with HoneyHive.

**Solution**: Check the compatibility information below before installation.

Python Version Support
^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Support Level
     - Python Versions
   * - Fully Supported
     - 3.11, 3.12, 3.13
   * - Not Supported
     - 3.10 and below

Provider SDK Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^

- **Minimum**: openai >= 1.0.0
- **Recommended**: openai >= 1.10.0
- **Tested Versions**: 1.10.0, 1.11.0, 1.12.0

Instrumentor Compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Instrumentor
     - Status
     - Notes
   * - OpenInference
     - Fully Supported
     - Full Azure OpenAI support with deployment-specific tracing
   * - Traceloop
     - Fully Supported
     - Enhanced metrics with Azure-specific cost tracking and quotas

Known Limitations
^^^^^^^^^^^^^^^^^

- **Deployment Names**: Must configure Azure deployment names separately from model names
- **API Versions**: Requires Azure API version in configuration, traced in metadata
- **Managed Identity**: Supported but requires additional Azure SDK configuration
- **Streaming**: Fully supported with both instrumentors

.. note::
   For the complete compatibility matrix across all providers, see :doc:`/how-to/integrations/multi-provider`.

Choose Your Instrumentor
------------------------

**Problem**: I need to choose between OpenInference and Traceloop for Azure OpenAI integration.

**Solution**: Choose the instrumentor that best fits your needs:

- **OpenInference**: Open-source, lightweight, great for getting started
- **Traceloop**: Enhanced LLM metrics, cost tracking, production optimizations

.. raw:: html

   <div class="instrumentor-selector">
   <div class="instrumentor-tabs">
     <button class="instrumentor-button active" onclick="showInstrumentor(event, 'openinference-section')">OpenInference</button>
     <button class="instrumentor-button" onclick="showInstrumentor(event, 'openllmetry-section')">Traceloop</button>
   </div>

   <div id="openinference-section" class="instrumentor-content active">

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, 'azure-openai-openinference-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'azure-openai-openinference-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, 'azure-openai-openinference-advanced')">Advanced Usage</button>
     <button class="tab-button" onclick="showTab(event, 'azure-openai-openinference-troubleshoot')">Troubleshooting</button>
   </div>

   <div id="azure-openai-openinference-install" class="tab-content active">

**Best for**: Open-source projects, simple tracing needs, getting started quickly

.. code-block:: bash

   # Recommended: Install with Azure OpenAI integration
   pip install honeyhive[openinference-azure-openai]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-openai openai>=1.0.0

.. raw:: html

   </div>
   <div id="azure-openai-openinference-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # AZURE_OPENAI_API_KEY=your-azure-openai-key

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )  # Uses HH_API_KEY from environment
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   # Basic usage with error handling
   try:
       from openai import AzureOpenAI
       
       # Create Azure OpenAI client
       client = AzureOpenAI(
           api_key=os.getenv("AZURE_OPENAI_API_KEY"),
           api_version="2024-02-01",
           azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
       )
       
       # Chat completion
       response = client.chat.completions.create(
           model="gpt-35-turbo",  # Your deployment name
           messages=[{"role": "user", "content": "Hello from Azure OpenAI!"}]
       )
       # Automatically traced! ✨
   except openai.APIError as e:
       print(f"Azure OpenAI API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="azure-openai-openinference-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai

   # Initialize with custom configuration
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project",        # Or set HH_PROJECT environment variable
       source="production"            # Or set HH_SOURCE environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   @trace(tracer=tracer, event_type=EventType.chain)
   def multi_deployment_azure_workflow(prompts: List[str]) -> dict:
       """Advanced example with business context and multiple Azure OpenAI calls."""
       from openai import AzureOpenAI
       
       # Configure Azure OpenAI client
       client = AzureOpenAI(
           api_key=os.getenv("AZURE_OPENAI_API_KEY"),
           api_version="2024-02-01",
           azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
       )
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type(prompts).__name__,
           "business.use_case": "multi_deployment_analysis",
           "azure-openai.strategy": "azure_deployment_comparison",
           "instrumentor.type": "openinference"
       })
       
       try:
           # Test multiple Azure OpenAI deployments
       deployments = [
           "gpt-35-turbo",      # Your GPT-3.5 deployment
           "gpt-4",             # Your GPT-4 deployment
           "gpt-4-turbo"        # Your GPT-4 Turbo deployment
       ]
       
       results = []
       for prompt in prompts:
           deployment_results = {}
           
           for deployment in deployments:
               try:
                   # Test each deployment
                   response = client.chat.completions.create(
                       model=deployment,
                       messages=[
                           {"role": "user", "content": prompt}
                       ],
                       max_tokens=150,
                       temperature=0.7
                   )
                   
                   deployment_results[deployment] = {
                       "content": response.choices[0].message.content,
                       "tokens": response.usage.total_tokens,
                       "prompt_tokens": response.usage.prompt_tokens,
                       "completion_tokens": response.usage.completion_tokens
                   }
                   
               except Exception as e:
                   deployment_results[deployment] = {"error": str(e)}
           
           results.append({
               "prompt": prompt,
               "deployment_responses": deployment_results
           })
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "azure-openai.models_used": ["gpt-35-turbo", "gpt-4", "gpt-4-turbo"],
               "business.result_confidence": "high"
           })
           
           return {{RETURN_VALUE}}
           
       except openai.APIError as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.source": "openinference"
           })
           raise

.. raw:: html

   </div>
   <div id="azure-openai-openinference-troubleshoot" class="tab-content">

**Common OpenInference Issues**:

1. **Missing Traces**
   
   .. code-block:: python
   
      # Use correct initialization pattern
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = OpenAIInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

2. **Performance for High Volume**
   
   .. code-block:: python
   
      # OpenInference uses efficient span processors automatically
      # No additional configuration needed

3. **Multiple Instrumentors**
   
   .. code-block:: python
   
      # You can combine OpenInference with other instrumentors
      from openinference.instrumentation.openai import OpenAIInstrumentor
       from openinference.instrumentation.anthropic import AnthropicInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               OpenAIInstrumentor(),      # Works for both OpenAI and Azure OpenAI
              AnthropicInstrumentor()
          ]
      )

4. **Environment Configuration**
   
   .. code-block:: bash
   
      # HoneyHive configuration
      export HH_API_KEY="your-honeyhive-api-key"
      export HH_SOURCE="production"
      
      # Azure OpenAI configuration
      export AZURE_OPENAI_API_KEY="your-azure-openai-key"
      export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
      export AZURE_OPENAI_API_VERSION="2024-02-01"

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>

   <div id="openllmetry-section" class="instrumentor-content">

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, 'azure-openai-openllmetry-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'azure-openai-openllmetry-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, 'azure-openai-openllmetry-advanced')">Advanced Usage</button>
     <button class="tab-button" onclick="showTab(event, 'azure-openai-openllmetry-troubleshoot')">Troubleshooting</button>
   </div>

   <div id="azure-openai-openllmetry-install" class="tab-content active">

**Best for**: Production deployments, cost tracking, enhanced LLM observability

.. code-block:: bash

   # Recommended: Install with Traceloop Azure OpenAI integration
   pip install honeyhive[traceloop-azure-openai]
   
   # Alternative: Manual installation
   pip install honeyhive opentelemetry-instrumentation-openai openai>=1.0.0

.. raw:: html

   </div>
   <div id="azure-openai-openllmetry-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   import openai
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # AZURE_OPENAI_API_KEY=your-azure-openai-key

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )  # Uses HH_API_KEY from environment
   
   # Step 2: Initialize Traceloop instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   # Basic usage with automatic tracing
   try:
       from openai import AzureOpenAI
       
       # Create Azure OpenAI client
       client = AzureOpenAI(
           api_key=os.getenv("AZURE_OPENAI_API_KEY"),
           api_version="2024-02-01",
           azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
       )
       
       # Chat completion
       response = client.chat.completions.create(
           model="gpt-35-turbo",  # Your deployment name
           messages=[{"role": "user", "content": "Hello from Azure OpenAI!"}]
       )
       # Automatically traced by Traceloop with enhanced metrics! ✨
   except openai.APIError as e:
       print(f"Azure OpenAI API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="azure-openai-openllmetry-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   import openai

   # Initialize HoneyHive with Traceloop instrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project",        # Or set HH_PROJECT environment variable
       source="production"            # Or set HH_SOURCE environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   @trace(tracer=tracer, event_type=EventType.chain)
   def multi_deployment_azure_workflow(prompts: List[str]) -> dict:
       """Advanced example with business context and enhanced LLM metrics."""
       from openai import AzureOpenAI
       
       # Configure Azure OpenAI client
       client = AzureOpenAI(
           api_key=os.getenv("AZURE_OPENAI_API_KEY"),
           api_version="2024-02-01",
           azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
       )
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type(prompts).__name__,
           "business.use_case": "multi_deployment_analysis",
           "azure-openai.strategy": "cost_optimized_azure_deployment_comparison",
           "instrumentor.type": "openllmetry",
           "observability.enhanced": True
       })
       
       try:
           # Test multiple Azure OpenAI deployments
       deployments = [
           "gpt-35-turbo",      # Your GPT-3.5 deployment
           "gpt-4",             # Your GPT-4 deployment
           "gpt-4-turbo"        # Your GPT-4 Turbo deployment
       ]
       
       results = []
       for prompt in prompts:
           deployment_results = {}
           
           for deployment in deployments:
               try:
                   # Test each deployment
                   response = client.chat.completions.create(
                       model=deployment,
                       messages=[
                           {"role": "user", "content": prompt}
                       ],
                       max_tokens=150,
                       temperature=0.7
                   )
                   
                   deployment_results[deployment] = {
                       "content": response.choices[0].message.content,
                       "tokens": response.usage.total_tokens,
                       "prompt_tokens": response.usage.prompt_tokens,
                       "completion_tokens": response.usage.completion_tokens
                   }
                   
               except Exception as e:
                   deployment_results[deployment] = {"error": str(e)}
           
           results.append({
               "prompt": prompt,
               "deployment_responses": deployment_results
           })
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "azure-openai.models_used": ["gpt-35-turbo", "gpt-4", "gpt-4-turbo"],
               "business.result_confidence": "high",
               "openllmetry.cost_tracking": "enabled",
               "openllmetry.token_metrics": "captured"
           })
           
           return {{RETURN_VALUE}}
           
       except openai.APIError as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.error_handling": "openllmetry"
           })
           raise

.. raw:: html

   </div>
   <div id="azure-openai-openllmetry-troubleshoot" class="tab-content">

**Common Traceloop Issues**:

1. **Missing Traces**
   
   .. code-block:: python
   
      # Ensure Traceloop instrumentor is passed to tracer
      from opentelemetry.instrumentation.openai import OpenAIInstrumentor
      
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = OpenAIInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

2. **Enhanced Metrics Not Showing**
   
   .. code-block:: python
   
      # Ensure you're using the latest version
      # pip install --upgrade opentelemetry-instrumentation-openai
      
      # The instrumentor automatically captures enhanced metrics
      from opentelemetry.instrumentation.openai import OpenAIInstrumentor
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = OpenAIInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

3. **Multiple Traceloop Instrumentors**
   
   .. code-block:: python
   
      # You can combine multiple Traceloop instrumentors
      from opentelemetry.instrumentation.openai import OpenAIInstrumentor
       from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               OpenAIInstrumentor(),      # Works for both OpenAI and Azure OpenAI
               AnthropicInstrumentor()    # Traceloop Anthropic
           ]
       )

4. **Performance Optimization**
   
   .. code-block:: python
   
      # Traceloop instrumentors handle batching automatically
      # No additional configuration needed for performance

5. **Environment Configuration**
   
   .. code-block:: bash
   
      # HoneyHive configuration
      export HH_API_KEY="your-honeyhive-api-key"
      export HH_SOURCE="production"
      
      # Azure OpenAI configuration
      export AZURE_OPENAI_API_KEY="your-azure-openai-key"
      export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
      export AZURE_OPENAI_API_VERSION="2024-02-01"
      
      # Optional: Traceloop cloud features
      export TRACELOOP_API_KEY="your-traceloop-key"
      export TRACELOOP_BASE_URL="https://api.traceloop.com"

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>
   </div>

Comparison: OpenInference vs Traceloop for Azure OpenAI
-------------------------------------------------------

.. list-table:: Feature Comparison
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - OpenInference
     - Traceloop
   * - **Setup Complexity**
     - Simple, single instrumentor
     - Single instrumentor setup
   * - **Token Tracking**
     - Basic span attributes
     - Detailed token metrics + costs
   * - **Model Metrics**
     - Model name, basic timing
     - Cost per model, latency analysis
   * - **Performance**
     - Lightweight, fast
     - Optimized with smart batching
   * - **Cost Analysis**
     - Manual calculation needed
     - Automatic cost per request
   * - **Production Ready**
     - ✅ Yes
     - ✅ Yes, with cost insights
   * - **Debugging**
     - Standard OpenTelemetry
     - Enhanced LLM-specific debug
   * - **Best For**
     - Simple integrations, dev
     - Production, cost optimization

Migration Between Instrumentors
-------------------------------

**From OpenInference to Traceloop**:

.. code-block:: python

   # Before (OpenInference)
   from openinference.instrumentation.openai import OpenAIInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # After (Traceloop) - different instrumentor package
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

**From Traceloop to OpenInference**:

.. code-block:: python

   # Before (Traceloop)
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # After (OpenInference)
   from openinference.instrumentation.openai import OpenAIInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

See Also
--------

- :doc:`multi-provider` - Use Azure OpenAI with other providers
- :doc:`../llm-application-patterns` - Common integration patterns
- :doc:`../../tutorials/02-add-llm-tracing-5min` - LLM integration tutorial
- :doc:`openai` - Similar integration for OpenAI

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
   
   function showInstrumentor(evt, instrumentorName) {
     var i, instrumentorContent, instrumentorLinks;
     instrumentorContent = document.getElementsByClassName("instrumentor-content");
     for (i = 0; i < instrumentorContent.length; i++) {
       instrumentorContent[i].classList.remove("active");
     }
     instrumentorLinks = document.getElementsByClassName("instrumentor-button");
     for (i = 0; i < instrumentorLinks.length; i++) {
       instrumentorLinks[i].classList.remove("active");
     }
     document.getElementById(instrumentorName).classList.add("active");
     evt.currentTarget.classList.add("active");
   }
   </script>
   
   <style>
   .instrumentor-selector {
     margin: 2rem 0;
     border: 2px solid #2980b9;
     border-radius: 12px;
     overflow: hidden;
     box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
   }
   .instrumentor-tabs {
     display: flex;
     background: linear-gradient(135deg, #3498db, #2980b9);
     border-bottom: 1px solid #2980b9;
   }
   .instrumentor-button {
     background: none;
     border: none;
     padding: 15px 25px;
     cursor: pointer;
     font-weight: 600;
     font-size: 16px;
     color: white;
     transition: all 0.3s ease;
     flex: 1;
     text-align: center;
   }
   .instrumentor-button:hover {
     background: rgba(255, 255, 255, 0.1);
     transform: translateY(-1px);
   }
   .instrumentor-button.active {
     background: rgba(255, 255, 255, 0.2);
     border-bottom: 3px solid #f39c12;
   }
   .instrumentor-content {
     display: none;
     padding: 1.5rem;
     background: #f8f9fa;
   }
   .instrumentor-content.active {
     display: block;
   }
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

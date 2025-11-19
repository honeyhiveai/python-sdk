Integrate with [Provider Name]
==============================

.. note::
   **Problem-solving guide for [Provider] integration**
   
   This guide helps you solve specific problems when integrating HoneyHive with [Provider], with support for multiple instrumentor options.

This guide covers [Provider] integration with HoneyHive's BYOI architecture, supporting both OpenInference and Traceloop instrumentors.

Choose Your Instrumentor
------------------------

**Problem**: I need to choose between OpenInference and Traceloop for [Provider] integration.

**Solution**: Both instrumentors work with HoneyHive. Choose based on your needs:

- **OpenInference**: Open-source, lightweight, great for getting started
- **Traceloop**: Enhanced LLM metrics, cost tracking, production optimizations

.. raw:: html

   <div class="instrumentor-selector">
   <div class="instrumentor-tabs">
     <button class="instrumentor-button active" onclick="showInstrumentor(event, 'openinference-section')">OpenInference</button>
     <button class="instrumentor-button" onclick="showInstrumentor(event, 'openllmetry-section')">Traceloop</button>
   </div>

   <div id="openinference-section" class="instrumentor-content active">

OpenInference Integration
-------------------------

**Best for**: Open-source projects, simple tracing needs, getting started quickly

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, '[provider]-openinference-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, '[provider]-openinference-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, '[provider]-openinference-advanced')">Advanced Usage</button>
   </div>

   <div id="[provider]-openinference-install" class="tab-content active">

.. code-block:: bash

   # Recommended: Install with [Provider] integration
   pip install honeyhive[openinference-[provider]]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-[provider] [provider-sdk]

.. raw:: html

   </div>
   <div id="[provider]-openinference-basic" class="tab-content">

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
       # FIXED: Use separate initialization insteadInstrumentor()]  # Uses HH_API_KEY automatically
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
   <div id="[provider]-openinference-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from openinference.instrumentation.[provider] import [Provider]Instrumentor
   import [provider_sdk]

   # Initialize with custom configuration
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       source="production",
       # FIXED: Use separate initialization insteadInstrumentor()]
   )

   @trace(tracer=tracer, event_type=EventType.chain)
   def [advanced_function_name](input_param: str) -> dict:
       """Advanced example with business context and multiple [provider] calls."""
       client = [provider_sdk].[ClientClass]()
       
       # Add business context to the trace
       enrich_span({
           "[business_context].input_type": type(input_param).__name__,
           "[business_context].use_case": "[specific_use_case]",
           "[provider].strategy": "[model_selection_strategy]",
           "instrumentor.type": "openinference"
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
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.source": "openinference"
           })
           raise

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>

   <div id="openllmetry-section" class="instrumentor-content">

Traceloop Integration
---------------------

**Best for**: Production deployments, cost tracking, enhanced LLM observability

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, '[provider]-openllmetry-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, '[provider]-openllmetry-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, '[provider]-openllmetry-advanced')">Advanced Usage</button>
   </div>

   <div id="[provider]-openllmetry-install" class="tab-content active">

.. code-block:: bash

   # Recommended: Install with Traceloop [Provider] integration
   pip install honeyhive[traceloop-[provider]]
   
   # Alternative: Manual installation
   pip install honeyhive opentelemetry-instrumentation-[provider] [provider-sdk]

.. raw:: html

   </div>
   <div id="[provider]-openllmetry-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from traceloop.sdk import Traceloop
   import [provider_sdk]
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # [PROVIDER]_API_KEY=your-[provider]-key

   # Initialize Traceloop first
   Traceloop.init()
   
   # Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init()  # Uses HH_API_KEY automatically

   # Basic usage with automatic tracing
   try:
       client = [provider_sdk].[ClientClass]()  # Uses [PROVIDER]_API_KEY automatically
       # [Provider-specific API call example]
       # Automatically traced by Traceloop with enhanced metrics! ✨
   except [provider_sdk].[ProviderAPIError] as e:
       print(f"[Provider] API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="[provider]-openllmetry-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from traceloop.sdk import Traceloop
   import [provider_sdk]

   # Initialize Traceloop with custom settings
   Traceloop.init(
       app_name="[your-app-name]",
       disable_batch=False,  # Enable batching for performance
       api_endpoint="https://api.traceloop.com"
   )
   
   # Initialize HoneyHive with custom configuration
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       source="production"
   )

   @trace(tracer=tracer, event_type=EventType.chain)
   def [advanced_function_name](input_param: str) -> dict:
       """Advanced example with business context and enhanced LLM metrics."""
       client = [provider_sdk].[ClientClass]()
       
       # Add business context to the trace
       enrich_span({
           "[business_context].input_type": type(input_param).__name__,
           "[business_context].use_case": "[specific_use_case]",
           "[provider].strategy": "[model_selection_strategy]",
           "instrumentor.type": "openllmetry",
           "observability.enhanced": True
       })
       
       try:
           # [First API call - Traceloop captures cost and token metrics]
           # [Second API call - Automatic latency and performance tracking]
           
           # Add result metadata
           enrich_span({
               "[business_context].successful": True,
               "[provider].models_used": ["[model1]", "[model2]"],
               "[business_context].result_metrics": "[relevant_metrics]",
               "openllmetry.cost_tracking": "enabled",
               "openllmetry.token_metrics": "captured"
           })
           
           return results
           
       except [provider_sdk].[ProviderAPIError] as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.error_handling": "openllmetry"
           })
           raise

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>
   </div>

Comparison: OpenInference vs Traceloop
--------------------------------------

.. list-table:: Feature Comparison
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - OpenInference
     - Traceloop
   * - **Setup Complexity**
     - Simple, minimal config
     - Slightly more setup steps
   * - **LLM Metrics**
     - Basic span data
     - Enhanced: cost, tokens, latency
   * - **Performance**
     - Lightweight
     - Optimized with batching
   * - **Cost Tracking**
     - Manual calculation
     - Automatic cost tracking
   * - **Production Ready**
     - ✅ Yes
     - ✅ Yes, with extras
   * - **Open Source**
     - ✅ Fully open
     - ✅ Core is open
   * - **Learning Curve**
     - Minimal
     - Moderate
   * - **Best For**
     - Getting started, simple needs
     - Production, cost analysis

Environment Configuration
-------------------------

**Required Environment Variables** (both instrumentors):

.. code-block:: bash

   # HoneyHive configuration
   export HH_API_KEY="your-honeyhive-api-key"
   export HH_SOURCE="production"
   
   # [Provider] configuration
   export [PROVIDER]_API_KEY="your-[provider]-api-key"

**Additional for Traceloop**:

.. code-block:: bash

   # Optional: Traceloop cloud features
   export TRACELOOP_API_KEY="your-traceloop-key"
   export TRACELOOP_BASE_URL="https://api.traceloop.com"

Migration Between Instrumentors
-------------------------------

**From OpenInference to Traceloop**:

.. code-block:: python

   # Before (OpenInference)
   from openinference.instrumentation.[provider] import [Provider]Instrumentor
   tracer = HoneyHiveTracer.init(# FIXED: Use separate initialization insteadInstrumentor()])
   
   # After (Traceloop)
   from traceloop.sdk import Traceloop
   Traceloop.init()
   tracer = HoneyHiveTracer.init()  # No instrumentors needed

**From Traceloop to OpenInference**:

.. code-block:: python

   # Before (Traceloop)
   from traceloop.sdk import Traceloop
   Traceloop.init()
   tracer = HoneyHiveTracer.init()
   
   # After (OpenInference)
   from openinference.instrumentation.[provider] import [Provider]Instrumentor
   tracer = HoneyHiveTracer.init(# FIXED: Use separate initialization insteadInstrumentor()])

Troubleshooting
---------------

**Common Issues**:

1. **OpenInference: Missing Traces**
   
   .. code-block:: python
   
      # Ensure instrumentor is passed to tracer
      tracer = HoneyHiveTracer.init(
          # FIXED: Use separate initialization insteadInstrumentor()]  # Don't forget this!
      )

2. **Traceloop: Import Conflicts**
   
   .. code-block:: python
   
      # Initialize Traceloop before HoneyHive
      from traceloop.sdk import Traceloop
      Traceloop.init()  # Must come first
      
      from honeyhive import HoneyHiveTracer
      tracer = HoneyHiveTracer.init()

3. **Performance Issues**
   
   .. code-block:: python
   
      # Traceloop: Enable batching
      Traceloop.init(disable_batch=False, batch_size=100)
      
      # OpenInference: Use efficient span processors
      # (automatic with HoneyHiveTracer.init())

See Also
--------

- :doc:`multi-provider` - Use [Provider] with other providers
- :doc:`../troubleshooting` - Common integration issues  
- :doc:`../../tutorials/02-add-llm-tracing-5min` - LLM integration tutorial

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

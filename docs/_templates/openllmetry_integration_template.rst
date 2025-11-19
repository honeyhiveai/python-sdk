Integration with [Provider Name] (OpenLLMetry)
==============================================

.. note::
   **OpenLLMetry alternative for [Provider] integration**
   
   This guide shows how to use OpenLLMetry (Traceloop) instrumentors as an alternative to OpenInference for [Provider] integration.

This guide demonstrates [Provider] integration using OpenLLMetry instrumentation with HoneyHive's BYOI architecture.

Quick Setup
-----------

**Problem**: I want to use OpenLLMetry instrumentation instead of OpenInference for [Provider] tracing.

**Solution**:

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, '[provider]-openllmetry-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, '[provider]-openllmetry-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, '[provider]-openllmetry-advanced')">Advanced Usage</button>
   </div>

   <div id="[provider]-openllmetry-install" class="tab-content active">

.. code-block:: bash

   # Recommended: Install with OpenLLMetry [Provider] integration
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

   # Initialize OpenLLMetry
   Traceloop.init()
   
   # Initialize HoneyHive tracer 
   tracer = HoneyHiveTracer.init()  # Uses HH_API_KEY automatically

   # Basic usage with automatic tracing
   try:
       client = [provider_sdk].[ClientClass]()  # Uses [PROVIDER]_API_KEY automatically
       # [Provider-specific API call example]
       # Automatically traced by OpenLLMetry! ✨
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

   # Initialize OpenLLMetry with custom settings
   Traceloop.init(
       app_name="[your-app-name]",
       disable_batch=False,  # Enable batching for performance
       api_endpoint="https://api.traceloop.com"  # Default endpoint
   )
   
   # Initialize HoneyHive with custom configuration
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       source="production"
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
           "instrumentor.type": "openllmetry"
       })
       
       try:
           # [First API call with specific model/configuration]
           # OpenLLMetry automatically captures LLM-specific metrics
           
           # [Second API call with different model/configuration]
           
           # Add result metadata
           enrich_span({
               "[business_context].successful": True,
               "[provider].models_used": ["[model1]", "[model2]"],
               "[business_context].result_metrics": "[relevant_metrics]",
               "openllmetry.features": "enhanced_llm_observability"
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

Key Differences from OpenInference
----------------------------------

**OpenLLMetry Advantages**:

- **Enhanced LLM Metrics**: Automatic cost tracking, token usage, and latency metrics
- **Production Ready**: Built-in performance optimizations and batching
- **Rich Context**: Captures additional LLM-specific span attributes
- **Cost Analysis**: Automatic cost calculation for major LLM providers

**Integration Patterns**:

.. code-block:: python

   # OpenLLMetry handles instrumentation automatically
   # No need to pass instrumentors to HoneyHiveTracer.init()
   
   # 1. Initialize OpenLLMetry first
   Traceloop.init()
   
   # 2. Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init()
   
   # 3. Use your [Provider] client normally - automatically traced!

Environment Configuration
-------------------------

**Required Environment Variables**:

.. code-block:: bash

   # HoneyHive configuration
   export HH_API_KEY="your-honeyhive-api-key"
   export HH_SOURCE="production"
   
   # [Provider] configuration
   export [PROVIDER]_API_KEY="your-[provider]-api-key"
   
   # Optional: OpenLLMetry configuration
   export TRACELOOP_API_KEY="your-traceloop-key"  # For Traceloop cloud features
   export TRACELOOP_BASE_URL="https://api.traceloop.com"

**Verification**:

.. code-block:: python

   # Test that both instrumentations are working
   import os
   from honeyhive import HoneyHiveTracer
   from traceloop.sdk import Traceloop
   
   # Verify environment
   assert os.getenv("HH_API_KEY"), "HH_API_KEY required"
   assert os.getenv("[PROVIDER]_API_KEY"), "[PROVIDER]_API_KEY required"
   
   # Initialize
   Traceloop.init()
   tracer = HoneyHiveTracer.init()
   
   print("✅ OpenLLMetry + HoneyHive integration ready!")

Troubleshooting
---------------

**Common Issues**:

1. **Import Conflicts**: 
   
   .. code-block:: python
   
      # Ensure OpenLLMetry is initialized before HoneyHive
      from traceloop.sdk import Traceloop
      Traceloop.init()  # Must come first
      
      from honeyhive import HoneyHiveTracer
      tracer = HoneyHiveTracer.init()

2. **Missing Traces**: Check that OpenLLMetry auto-instrumentation is enabled

   .. code-block:: python
   
      # Verify OpenLLMetry is active
      from opentelemetry import trace
      tracer = trace.get_tracer(__name__)
      
      with tracer.start_span("test_span") as span:
          print(f"Span ID: {span.get_span_context().span_id}")

3. **Performance Issues**: Enable batching for high-volume applications

   .. code-block:: python
   
      Traceloop.init(
          disable_batch=False,  # Enable batching
          batch_size=100,       # Adjust batch size
          flush_interval=5000   # Flush every 5 seconds
      )

See Also
--------

- :doc:`multi-provider` - Use [Provider] with other providers
- :doc:`../troubleshooting` - Common integration issues  
- :doc:`../../tutorials/02-add-llm-tracing-5min` - LLM integration tutorial
- :doc:`[provider]` - OpenInference alternative for [Provider]

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

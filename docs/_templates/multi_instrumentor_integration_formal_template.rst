Integrate with {{PROVIDER_NAME}}
===================================

.. note::
   **Problem-solving guide for {{PROVIDER_NAME}} integration**
   
   This guide helps you solve specific problems when integrating HoneyHive with {{PROVIDER_NAME}}, with support for multiple instrumentor options.

This guide covers {{PROVIDER_NAME}} integration with HoneyHive's BYOI architecture, supporting both OpenInference and OpenLLMetry instrumentors.

Choose Your Instrumentor
------------------------

**Problem**: I need to choose between OpenInference and OpenLLMetry for {{PROVIDER_NAME}} integration.

**Solution**: Choose the instrumentor that best fits your needs:

- **OpenInference**: Open-source, lightweight, great for getting started
- **OpenLLMetry**: {{OPENLLMETRY_NOTE if OPENLLMETRY_AVAILABLE == False else "Enhanced LLM metrics, cost tracking, production optimizations"}}

.. raw:: html

   <div class="instrumentor-selector">
   <div class="instrumentor-tabs">
     <button class="instrumentor-button active" onclick="showInstrumentor(event, 'openinference-section')">OpenInference</button>
     <button class="instrumentor-button" onclick="showInstrumentor(event, 'openllmetry-section')">OpenLLMetry</button>
   </div>

   <div id="openinference-section" class="instrumentor-content active">

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, '{{PROVIDER_KEY}}-openinference-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, '{{PROVIDER_KEY}}-openinference-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, '{{PROVIDER_KEY}}-openinference-advanced')">Advanced Usage</button>
     <button class="tab-button" onclick="showTab(event, '{{PROVIDER_KEY}}-openinference-troubleshoot')">Troubleshooting</button>
   </div>

   <div id="{{PROVIDER_KEY}}-openinference-install" class="tab-content active">

**Best for**: Open-source projects, simple tracing needs, getting started quickly

.. code-block:: bash

   # Recommended: Install with {{PROVIDER_NAME}} integration
   pip install honeyhive[openinference-{{PROVIDER_KEY}}]
   
   # Alternative: Manual installation
   pip install honeyhive {{OPENINFERENCE_PACKAGE}} {{PROVIDER_SDK}}

.. raw:: html

   </div>
   <div id="{{PROVIDER_KEY}}-openinference-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from {{OPENINFERENCE_IMPORT}} import {{OPENINFERENCE_CLASS}}
   import {{PROVIDER_MODULE}}
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # {{PROVIDER_API_KEY_NAME}}=your-{{PROVIDER_KEY}}-key

   # Initialize with environment variables (secure)
   tracer = HoneyHiveTracer.init(
       instrumentors=[{{OPENINFERENCE_CLASS}}()]  # Uses HH_API_KEY automatically
   )

   # Basic usage with error handling
   try:
       {{BASIC_USAGE_EXAMPLE}}
       # Automatically traced! ✨
   except {{PROVIDER_EXCEPTION}} as e:
       print(f"{{PROVIDER_NAME}} API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="{{PROVIDER_KEY}}-openinference-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from {{OPENINFERENCE_IMPORT}} import {{OPENINFERENCE_CLASS}}
   import {{PROVIDER_MODULE}}

   # Initialize with custom configuration
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       source="production",
       instrumentors=[{{OPENINFERENCE_CLASS}}()]
   )

   @trace(tracer=tracer, event_type=EventType.chain)
   def {{ADVANCED_FUNCTION_NAME}}({{ADVANCED_FUNCTION_PARAMS}}) -> dict:
       """Advanced example with business context and multiple {{PROVIDER_NAME}} calls."""
       {{ADVANCED_USAGE_EXAMPLE}}
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type({{FIRST_PARAM}}).__name__,
           "business.use_case": "{{USE_CASE_NAME}}",
           "{{PROVIDER_KEY}}.strategy": "{{STRATEGY_NAME}}",
           "instrumentor.type": "openinference"
       })
       
       try:
           {{ADVANCED_IMPLEMENTATION}}
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "{{PROVIDER_KEY}}.models_used": {{MODELS_USED}},
               "business.result_confidence": "high"
           })
           
           return {{RETURN_VALUE}}
           
       except {{PROVIDER_EXCEPTION}} as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.source": "openinference"
           })
           raise

.. raw:: html

   </div>
   <div id="{{PROVIDER_KEY}}-openinference-troubleshoot" class="tab-content">

**Common OpenInference Issues**:

1. **Missing Traces**
   
   .. code-block:: python
   
      # Ensure instrumentor is passed to tracer
      tracer = HoneyHiveTracer.init(
          instrumentors=[{{OPENINFERENCE_CLASS}}()]  # Don't forget this!
      )

2. **Performance for High Volume**
   
   .. code-block:: python
   
      # OpenInference uses efficient span processors automatically
      # No additional configuration needed

3. **Multiple Instrumentors**
   
   .. code-block:: python
   
      # You can combine OpenInference with other instrumentors
      {{MULTIPLE_INSTRUMENTORS_EXAMPLE}}

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>

   <div id="openllmetry-section" class="instrumentor-content">

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, '{{PROVIDER_KEY}}-openllmetry-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, '{{PROVIDER_KEY}}-openllmetry-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, '{{PROVIDER_KEY}}-openllmetry-advanced')">Advanced Usage</button>
     <button class="tab-button" onclick="showTab(event, '{{PROVIDER_KEY}}-openllmetry-troubleshoot')">Troubleshooting</button>
   </div>

   <div id="{{PROVIDER_KEY}}-openllmetry-install" class="tab-content active">

**Best for**: Production deployments, cost tracking, enhanced LLM observability

.. code-block:: bash

   # Recommended: Install with OpenLLMetry {{PROVIDER_NAME}} integration
   pip install honeyhive[traceloop-{{PROVIDER_KEY}}]
   
   # Alternative: Manual installation
   pip install honeyhive {{OPENLLMETRY_PACKAGE}} {{PROVIDER_SDK}}

.. raw:: html

   </div>
   <div id="{{PROVIDER_KEY}}-openllmetry-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from {{OPENLLMETRY_IMPORT}} import {{OPENLLMETRY_CLASS}}
   import {{PROVIDER_MODULE}}
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # {{PROVIDER_API_KEY_NAME}}=your-{{PROVIDER_KEY}}-key

   # Initialize with OpenLLMetry instrumentor
   tracer = HoneyHiveTracer.init(
       instrumentors=[{{OPENLLMETRY_CLASS}}()]  # Uses HH_API_KEY automatically
   )

   # Basic usage with automatic tracing
   try:
       {{BASIC_USAGE_EXAMPLE}}
       # Automatically traced by OpenLLMetry with enhanced metrics! ✨
   except {{PROVIDER_EXCEPTION}} as e:
       print(f"{{PROVIDER_NAME}} API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="{{PROVIDER_KEY}}-openllmetry-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from {{OPENLLMETRY_IMPORT}} import {{OPENLLMETRY_CLASS}}
   import {{PROVIDER_MODULE}}

   # Initialize HoneyHive with OpenLLMetry instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       source="production",
       instrumentors=[{{OPENLLMETRY_CLASS}}()]
   )

   @trace(tracer=tracer, event_type=EventType.chain)
   def {{ADVANCED_FUNCTION_NAME}}({{ADVANCED_FUNCTION_PARAMS}}) -> dict:
       """Advanced example with business context and enhanced LLM metrics."""
       {{ADVANCED_USAGE_EXAMPLE}}
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type({{FIRST_PARAM}}).__name__,
           "business.use_case": "{{USE_CASE_NAME}}",
           "{{PROVIDER_KEY}}.strategy": "cost_optimized_{{STRATEGY_NAME}}",
           "instrumentor.type": "openllmetry",
           "observability.enhanced": True
       })
       
       try:
           {{ADVANCED_IMPLEMENTATION}}
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "{{PROVIDER_KEY}}.models_used": {{MODELS_USED}},
               "business.result_confidence": "high",
               "openllmetry.cost_tracking": "enabled",
               "openllmetry.token_metrics": "captured"
           })
           
           return {{RETURN_VALUE}}
           
       except {{PROVIDER_EXCEPTION}} as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.error_handling": "openllmetry"
           })
           raise

.. raw:: html

   </div>
   <div id="{{PROVIDER_KEY}}-openllmetry-troubleshoot" class="tab-content">

**Common OpenLLMetry Issues**:

1. **Missing Traces**
   
   .. code-block:: python
   
      # Ensure OpenLLMetry instrumentor is passed to tracer
      from {{OPENLLMETRY_IMPORT}} import {{OPENLLMETRY_CLASS}}
      
      tracer = HoneyHiveTracer.init(
          instrumentors=[{{OPENLLMETRY_CLASS}}()]  # Don't forget this!
      )

2. **Enhanced Metrics Not Showing**
   
   .. code-block:: python
   
      # Ensure you're using the latest version
      # pip install --upgrade {{OPENLLMETRY_PACKAGE}}
      
      # The instrumentor automatically captures enhanced metrics
      from {{OPENLLMETRY_IMPORT}} import {{OPENLLMETRY_CLASS}}
      tracer = HoneyHiveTracer.init(instrumentors=[{{OPENLLMETRY_CLASS}}()])

3. **Multiple OpenLLMetry Instrumentors**
   
   .. code-block:: python
   
      # You can combine multiple OpenLLMetry instrumentors
      {{MULTIPLE_OPENLLMETRY_INSTRUMENTORS_EXAMPLE}}

4. **Performance Optimization**
   
   .. code-block:: python
   
      # OpenLLMetry instrumentors handle batching automatically
      # No additional configuration needed for performance

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>
   </div>

Comparison: OpenInference vs OpenLLMetry for {{PROVIDER_NAME}}
---------------------------------------------------------------

.. list-table:: Feature Comparison
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - OpenInference
     - OpenLLMetry
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

Environment Configuration
--------------------------

**Required Environment Variables** (both instrumentors):

.. code-block:: bash

   # HoneyHive configuration
   export HH_API_KEY="your-honeyhive-api-key"
   export HH_PROJECT="{{PROVIDER_KEY}}-integration"
   export HH_SOURCE="production"
   
   # {{PROVIDER_NAME}} configuration
   export {{PROVIDER_API_KEY_NAME}}="your-{{PROVIDER_KEY}}-api-key"

{{ADDITIONAL_ENV_CONFIG}}

Migration Between Instrumentors
-------------------------------

**From OpenInference to OpenLLMetry**:

.. code-block:: python

   # Before (OpenInference)
   from {{OPENINFERENCE_IMPORT}} import {{OPENINFERENCE_CLASS}}
   tracer = HoneyHiveTracer.init(instrumentors=[{{OPENINFERENCE_CLASS}}()])
   
   # After (OpenLLMetry) - different instrumentor package
   from {{OPENLLMETRY_IMPORT}} import {{OPENLLMETRY_CLASS}}
   tracer = HoneyHiveTracer.init(instrumentors=[{{OPENLLMETRY_CLASS}}()])

**From OpenLLMetry to OpenInference**:

.. code-block:: python

   # Before (OpenLLMetry)
   from {{OPENLLMETRY_IMPORT}} import {{OPENLLMETRY_CLASS}}
   tracer = HoneyHiveTracer.init(instrumentors=[{{OPENLLMETRY_CLASS}}()])
   
   # After (OpenInference)
   from {{OPENINFERENCE_IMPORT}} import {{OPENINFERENCE_CLASS}}
   tracer = HoneyHiveTracer.init(instrumentors=[{{OPENINFERENCE_CLASS}}()])

See Also
--------

{{SEE_ALSO_LINKS}}

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

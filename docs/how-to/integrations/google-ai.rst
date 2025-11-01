Integrate with Google AI
========================

.. note::
   **Problem-solving guide for Google AI integration**
   
   This guide helps you solve specific problems when integrating HoneyHive with Google AI, with support for multiple instrumentor options.

This guide covers Google AI integration with HoneyHive's BYOI architecture, supporting both OpenInference and Traceloop instrumentors.

Compatibility
-------------

**Problem**: I need to know if my Python version and Google AI SDK version are compatible with HoneyHive.

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

- **Minimum**: google-generativeai >= 0.3.0
- **Recommended**: google-generativeai >= 0.4.0
- **Tested Versions**: 0.4.0, 0.5.0, 0.6.0

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
     - Gemini Pro and Pro Vision support with multimodal tracing
   * - Traceloop
     - Experimental
     - Basic support available, some Gemini-specific features in development

Known Limitations
^^^^^^^^^^^^^^^^^

- **Streaming**: Supported with manual span management required
- **Multimodal Input**: Vision features traced but media content not captured
- **Function Calling**: Supported in Gemini Pro models
- **Safety Settings**: Not captured in traces by default

.. note::
   For the complete compatibility matrix across all providers, see :doc:`/how-to/integrations/multi-provider`.

Choose Your Instrumentor
------------------------

**Problem**: I need to choose between OpenInference and Traceloop for Google AI integration.

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
     <button class="tab-button active" onclick="showTab(event, 'google-ai-openinference-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'google-ai-openinference-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, 'google-ai-openinference-advanced')">Advanced Usage</button>
     <button class="tab-button" onclick="showTab(event, 'google-ai-openinference-troubleshoot')">Troubleshooting</button>
   </div>

   <div id="google-ai-openinference-install" class="tab-content active">

**Best for**: Open-source projects, simple tracing needs, getting started quickly

.. code-block:: bash

   # Recommended: Install with Google AI integration
   pip install honeyhive[openinference-google-ai]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-google-generativeai google-generativeai>=0.3.0

.. raw:: html

   </div>
   <div id="google-ai-openinference-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   import google.generativeai
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # GOOGLE_API_KEY=your-google-ai-key

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )  # Uses HH_API_KEY from environment
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = GoogleGenerativeAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   # Basic usage with error handling
   try:
       import google.generativeai as genai
       genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
       model = genai.GenerativeModel('gemini-pro')
       response = model.generate_content("Hello!")
       print(response.text)
       # Automatically traced! ✨
   except google.generativeai.types.GoogleGenerativeAIError as e:
       print(f"Google AI API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="google-ai-openinference-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   import google.generativeai

   # Initialize with custom configuration
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project",        # Or set HH_PROJECT environment variable
       source="production"            # Or set HH_SOURCE environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = GoogleGenerativeAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   @trace(tracer=tracer, event_type=EventType.chain)
   def generate_content_comparison(prompt: str) -> dict:
       """Advanced example with business context and multiple Google AI calls."""
       {{ADVANCED_USAGE_EXAMPLE}}
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type(prompt).__name__,
           "business.use_case": "content_generation",
           "google-ai.strategy": "multi_model_gemini",
           "instrumentor.type": "openinference"
       })
       
       try:
           {{ADVANCED_IMPLEMENTATION}}
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "google-ai.models_used": ["gemini-pro", "gemini-pro-vision"],
               "business.result_confidence": "high"
           })
           
           return {{RETURN_VALUE}}
           
       except google.generativeai.types.GoogleGenerativeAIError as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.source": "openinference"
           })
           raise

.. raw:: html

   </div>
   <div id="google-ai-openinference-troubleshoot" class="tab-content">

**Common OpenInference Issues**:

1. **Missing Traces**
   
   .. code-block:: python
   
      # Use correct initialization pattern
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = GoogleGenerativeAIInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

2. **Performance for High Volume**
   
   .. code-block:: python
   
      # OpenInference uses efficient span processors automatically
      # No additional configuration needed

3. **Multiple Instrumentors**
   
   .. code-block:: python
   
      # You can combine OpenInference with other instrumentors
      {{MULTIPLE_INSTRUMENTORS_EXAMPLE}}

4. **Environment Configuration**
   
   .. code-block:: bash
   
      # HoneyHive configuration
      export HH_API_KEY="your-honeyhive-api-key"
      export HH_SOURCE="production"
      
      # Google AI configuration
      export GOOGLE_API_KEY="your-google-ai-api-key"

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>

   <div id="openllmetry-section" class="instrumentor-content">

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, 'google-ai-openllmetry-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'google-ai-openllmetry-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, 'google-ai-openllmetry-advanced')">Advanced Usage</button>
     <button class="tab-button" onclick="showTab(event, 'google-ai-openllmetry-troubleshoot')">Troubleshooting</button>
   </div>

   <div id="google-ai-openllmetry-install" class="tab-content active">

**Best for**: Production deployments, cost tracking, enhanced LLM observability

.. code-block:: bash

   # Recommended: Install with Traceloop Google AI integration
   pip install honeyhive[traceloop-google-ai]
   
   # Alternative: Manual installation
   pip install honeyhive opentelemetry-instrumentation-google-generativeai google-generativeai>=0.3.0

.. raw:: html

   </div>
   <div id="google-ai-openllmetry-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   import google.generativeai
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # GOOGLE_API_KEY=your-google-ai-key

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )  # Uses HH_API_KEY from environment
   
   # Step 2: Initialize Traceloop instrumentor separately with tracer_provider
   instrumentor = GoogleGenerativeAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   # Basic usage with automatic tracing
   try:
       import google.generativeai as genai
       genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
       model = genai.GenerativeModel('gemini-pro')
       response = model.generate_content("Hello!")
       print(response.text)
       # Automatically traced by Traceloop with enhanced metrics! ✨
   except google.generativeai.types.GoogleGenerativeAIError as e:
       print(f"Google AI API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="google-ai-openllmetry-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   import google.generativeai

   # Initialize HoneyHive with Traceloop instrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project",        # Or set HH_PROJECT environment variable
       source="production"            # Or set HH_SOURCE environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = GoogleGenerativeAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   @trace(tracer=tracer, event_type=EventType.chain)
   def generate_content_comparison(prompt: str) -> dict:
       """Advanced example with business context and enhanced LLM metrics."""
       {{ADVANCED_USAGE_EXAMPLE}}
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type(prompt).__name__,
           "business.use_case": "content_generation",
           "google-ai.strategy": "cost_optimized_multi_model_gemini",
           "instrumentor.type": "openllmetry",
           "observability.enhanced": True
       })
       
       try:
           {{ADVANCED_IMPLEMENTATION}}
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "google-ai.models_used": ["gemini-pro", "gemini-pro-vision"],
               "business.result_confidence": "high",
               "openllmetry.cost_tracking": "enabled",
               "openllmetry.token_metrics": "captured"
           })
           
           return {{RETURN_VALUE}}
           
       except google.generativeai.types.GoogleGenerativeAIError as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.error_handling": "openllmetry"
           })
           raise

.. raw:: html

   </div>
   <div id="google-ai-openllmetry-troubleshoot" class="tab-content">

**Common Traceloop Issues**:

1. **Missing Traces**
   
   .. code-block:: python
   
      # Ensure Traceloop instrumentor is passed to tracer
      from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
      
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = GoogleGenerativeAIInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

2. **Enhanced Metrics Not Showing**
   
   .. code-block:: python
   
      # Ensure you're using the latest version
      # pip install --upgrade opentelemetry-instrumentation-google-generativeai
      
      # The instrumentor automatically captures enhanced metrics
      from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = GoogleGenerativeAIInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

3. **Multiple Traceloop Instrumentors**
   
   .. code-block:: python
   
      # You can combine multiple Traceloop instrumentors
      {{MULTIPLE_TRACELOOP_INSTRUMENTORS_EXAMPLE}}

4. **Performance Optimization**
   
   .. code-block:: python
   
      # Traceloop instrumentors handle batching automatically
      # No additional configuration needed for performance

5. **Environment Configuration**
   
   .. code-block:: bash
   
      # HoneyHive configuration
      export HH_API_KEY="your-honeyhive-api-key"
      export HH_SOURCE="production"
      
      # Google AI configuration
      export GOOGLE_API_KEY="your-google-ai-api-key"
      
      # Optional: Traceloop cloud features
      export TRACELOOP_API_KEY="your-traceloop-key"
      export TRACELOOP_BASE_URL="https://api.traceloop.com"

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>
   </div>

Comparison: OpenInference vs Traceloop for Google AI
----------------------------------------------------

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
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = GoogleGenerativeAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # After (Traceloop) - different instrumentor package
   from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = GoogleGenerativeAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

**From Traceloop to OpenInference**:

.. code-block:: python

   # Before (Traceloop)
   from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = GoogleGenerativeAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # After (OpenInference)
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = GoogleGenerativeAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

See Also
--------

- :doc:`multi-provider` - Use Google AI with other providers
- :doc:`../llm-application-patterns` - Common integration patterns
- :doc:`../../tutorials/02-add-llm-tracing-5min` - LLM integration tutorial
- :doc:`openai` - Similar integration for OpenAI GPT

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

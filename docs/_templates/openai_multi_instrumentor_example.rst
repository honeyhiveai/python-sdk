Integrate with OpenAI
=====================

.. note::
   **Problem-solving guide for OpenAI integration**
   
   This guide helps you solve specific problems when integrating HoneyHive with OpenAI, with support for multiple instrumentor options.

This guide covers OpenAI integration with HoneyHive's BYOI architecture, supporting both OpenInference and OpenLLMetry instrumentors.

Choose Your Instrumentor
------------------------

**Problem**: I need to choose between OpenInference and OpenLLMetry for OpenAI integration.

**Solution**: Both instrumentors work excellently with HoneyHive. Choose based on your needs:

- **OpenInference**: Open-source, lightweight, great for getting started
- **OpenLLMetry**: Enhanced LLM metrics, cost tracking, production optimizations

.. raw:: html

   <div class="instrumentor-selector">
   <div class="instrumentor-tabs">
     <button class="instrumentor-button active" onclick="showInstrumentor(event, 'openinference-section')">OpenInference</button>
     <button class="instrumentor-button" onclick="showInstrumentor(event, 'openllmetry-section')">OpenLLMetry</button>
   </div>

   <div id="openinference-section" class="instrumentor-content active">

OpenInference Integration
-------------------------

**Best for**: Open-source projects, simple tracing needs, getting started quickly

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, 'openai-openinference-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'openai-openinference-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, 'openai-openinference-advanced')">Advanced Usage</button>
   </div>

   <div id="openai-openinference-install" class="tab-content active">

.. code-block:: bash

   # Recommended: Install with OpenAI integration
   pip install honeyhive[openinference-openai]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-openai openai

.. raw:: html

   </div>
   <div id="openai-openinference-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # OPENAI_API_KEY=your-openai-key

   # Initialize with environment variables (secure)
   tracer = HoneyHiveTracer.init(
       # FIXED: Use separate initialization instead  # Uses HH_API_KEY automatically
   )

   # Basic usage with error handling
   try:
       client = openai.OpenAI()  # Uses OPENAI_API_KEY automatically
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": "Hello!"}]
       )
       print(response.choices[0].message.content)
       # Automatically traced! ✨
   except openai.APIError as e:
       print(f"OpenAI API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="openai-openinference-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai

   # Initialize with custom configuration
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       source="production"
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   @trace(tracer=tracer, event_type=EventType.chain)
   def analyze_sentiment(text: str) -> dict:
       """Advanced example with business context and multiple OpenAI calls."""
       client = openai.OpenAI()
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type(text).__name__,
           "business.use_case": "sentiment_analysis",
           "openai.strategy": "multi_model_comparison",
           "instrumentor.type": "openinference"
       })
       
       try:
           # First call: Quick sentiment with GPT-3.5
           quick_response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{
                   "role": "user", 
                   "content": f"Analyze sentiment (positive/negative/neutral): {text}"
               }]
           )
           
           # Second call: Detailed analysis with GPT-4
           detailed_response = client.chat.completions.create(
               model="gpt-4",
               messages=[{
                   "role": "user",
                   "content": f"Provide detailed sentiment analysis with confidence score: {text}"
               }]
           )
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "openai.models_used": ["gpt-3.5-turbo", "gpt-4"],
               "business.result_confidence": "high"
           })
           
           return {
               "quick_sentiment": quick_response.choices[0].message.content,
               "detailed_analysis": detailed_response.choices[0].message.content
           }
           
       except openai.APIError as e:
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

OpenLLMetry Integration
-----------------------

**Best for**: Production deployments, cost tracking, enhanced LLM observability

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, 'openai-openllmetry-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'openai-openllmetry-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, 'openai-openllmetry-advanced')">Advanced Usage</button>
   </div>

   <div id="openai-openllmetry-install" class="tab-content active">

.. code-block:: bash

   # Recommended: Install with OpenLLMetry OpenAI integration
   pip install honeyhive[traceloop-openai]
   
   # Alternative: Manual installation
   pip install honeyhive opentelemetry-instrumentation-openai openai

.. raw:: html

   </div>
   <div id="openai-openllmetry-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from traceloop.sdk import Traceloop
   import openai
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # OPENAI_API_KEY=your-openai-key

   # Initialize OpenLLMetry first
   Traceloop.init()
   
   # Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init()  # Uses HH_API_KEY automatically

   # Basic usage with automatic tracing
   try:
       client = openai.OpenAI()  # Uses OPENAI_API_KEY automatically
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": "Hello!"}]
       )
       print(response.choices[0].message.content)
       # Automatically traced by OpenLLMetry with enhanced metrics! ✨
   except openai.APIError as e:
       print(f"OpenAI API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="openai-openllmetry-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from traceloop.sdk import Traceloop
   import openai

   # Initialize OpenLLMetry with custom settings
   Traceloop.init(
       app_name="sentiment-analyzer",
       disable_batch=False,  # Enable batching for performance
       api_endpoint="https://api.traceloop.com"
   )
   
   # Initialize HoneyHive with custom configuration
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       source="production"
   )

   @trace(tracer=tracer, event_type=EventType.chain)
   def analyze_sentiment(text: str) -> dict:
       """Advanced example with business context and enhanced LLM metrics."""
       client = openai.OpenAI()
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type(text).__name__,
           "business.use_case": "sentiment_analysis",
           "openai.strategy": "cost_optimized_multi_model",
           "instrumentor.type": "openllmetry",
           "observability.enhanced": True
       })
       
       try:
           # First call - OpenLLMetry captures cost and token metrics automatically
           quick_response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{
                   "role": "user", 
                   "content": f"Analyze sentiment (positive/negative/neutral): {text}"
               }]
           )
           
           # Second call - Automatic latency and performance tracking
           detailed_response = client.chat.completions.create(
               model="gpt-4",
               messages=[{
                   "role": "user",
                   "content": f"Provide detailed sentiment analysis with confidence score: {text}"
               }]
           )
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "openai.models_used": ["gpt-3.5-turbo", "gpt-4"],
               "business.result_confidence": "high",
               "openllmetry.cost_tracking": "enabled",
               "openllmetry.token_metrics": "captured"
           })
           
           return {
               "quick_sentiment": quick_response.choices[0].message.content,
               "detailed_analysis": detailed_response.choices[0].message.content
           }
           
       except openai.APIError as e:
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

Comparison: OpenInference vs OpenLLMetry for OpenAI
---------------------------------------------------

.. list-table:: Feature Comparison
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - OpenInference
     - OpenLLMetry
   * - **Setup Complexity**
     - Simple, single instrumentor
     - Two-step initialization
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

Real-World Usage Examples
-------------------------

**Content Generation Pipeline**:

.. code-block:: python

   # Works with both instrumentors - just change initialization!
   
   @trace(event_type=EventType.chain)
   def content_pipeline(topic: str) -> str:
       """Generate and refine content using multiple OpenAI models."""
       client = openai.OpenAI()
       
       # Draft with GPT-3.5 (cost-effective)
       draft = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": f"Write a blog post about {topic}"}]
       )
       
       # Polish with GPT-4 (higher quality)
       final = client.chat.completions.create(
           model="gpt-4",
           messages=[{
               "role": "user", 
               "content": f"Improve this blog post: {draft.choices[0].message.content}"
           }]
       )
       
       # OpenLLMetry automatically tracks: 
       # - Cost difference between models
       # - Token usage optimization opportunities
       # - Latency for each step
       
       return final.choices[0].message.content

Environment Configuration
-------------------------

**Required Environment Variables** (both instrumentors):

.. code-block:: bash

   # HoneyHive configuration
   export HH_API_KEY="your-honeyhive-api-key"
   export HH_SOURCE="production"
   
   # OpenAI configuration
   export OPENAI_API_KEY="your-openai-api-key"

**Additional for OpenLLMetry**:

.. code-block:: bash

   # Optional: OpenLLMetry cloud features
   export TRACELOOP_API_KEY="your-traceloop-key"
   export TRACELOOP_BASE_URL="https://api.traceloop.com"

Migration Between Instrumentors
-------------------------------

**From OpenInference to OpenLLMetry**:

.. code-block:: python

   # Before (OpenInference)
   from openinference.instrumentation.openai import OpenAIInstrumentor
   tracer = HoneyHiveTracer.init(# FIXED: Use separate initialization instead)
   
   # After (OpenLLMetry) - easier setup!
   from traceloop.sdk import Traceloop
   Traceloop.init()
   tracer = HoneyHiveTracer.init()  # No instrumentors parameter needed

**From OpenLLMetry to OpenInference**:

.. code-block:: python

   # Before (OpenLLMetry)
   from traceloop.sdk import Traceloop
   Traceloop.init()
   tracer = HoneyHiveTracer.init()
   
   # After (OpenInference)
   from openinference.instrumentation.openai import OpenAIInstrumentor
   tracer = HoneyHiveTracer.init(# FIXED: Use separate initialization instead)

Troubleshooting
---------------

**Common Issues**:

1. **OpenInference: Missing Traces**
   
   .. code-block:: python
   
      # Ensure instrumentor is passed to tracer
      tracer = HoneyHiveTracer.init(
          # FIXED: Use separate initialization instead  # Don't forget this!
      )

2. **OpenLLMetry: Import Order Matters**
   
   .. code-block:: python
   
      # Initialize Traceloop BEFORE HoneyHive
      from traceloop.sdk import Traceloop
      Traceloop.init()  # Must come first
      
      from honeyhive import HoneyHiveTracer
      tracer = HoneyHiveTracer.init()

3. **High Volume Applications**
   
   .. code-block:: python
   
      # OpenLLMetry: Enable batching for performance
      Traceloop.init(
          disable_batch=False, 
          batch_size=100,
          flush_interval=5000  # 5 seconds
      )
      
      # OpenInference: Uses efficient span processors automatically

4. **Cost Tracking Not Working (OpenLLMetry)**
   
   .. code-block:: python
   
      # Ensure you're using the latest version
      # pip install --upgrade opentelemetry-instrumentation-openai
      
      # Verify Traceloop is initialized properly
      Traceloop.init()  # Must be called before making OpenAI calls

See Also
--------

- :doc:`multi-provider` - Use OpenAI with other providers
- :doc:`../troubleshooting` - Common integration issues  
- :doc:`../../tutorials/02-add-llm-tracing-5min` - LLM integration tutorial
- :doc:`anthropic` - Similar integration for Anthropic Claude

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

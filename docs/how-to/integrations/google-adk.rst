Integrate with Google Agent Development Kit (ADK)
=================================================

.. note::
   **Problem-solving guide for Google Agent Development Kit (ADK) integration**
   
   This guide helps you solve specific problems when integrating HoneyHive with Google Agent Development Kit (ADK), with support for multiple instrumentor options.

This guide covers Google Agent Development Kit (ADK) integration with HoneyHive's BYOI architecture, supporting both OpenInference and Traceloop instrumentors.

Compatibility
-------------

**Problem**: I need to know if my Python version and Google Agent Development Kit (ADK) SDK version are compatible with HoneyHive.

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

- **Minimum**: google-adk >= 1.0.0
- **Recommended**: google-adk >= 1.2.0
- **Tested Versions**: 1.2.0, 1.3.0

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
     - Multi-agent workflows and tool calling fully traced
   * - Traceloop
     - Not Supported
     - Traceloop instrumentor not available for Google ADK - use OpenInference

Known Limitations
^^^^^^^^^^^^^^^^^

- **Traceloop**: Not available for Google ADK, OpenInference only
- **Multi-Agent Workflows**: Requires nested span management for proper trace hierarchy
- **Tool Calling**: Fully supported with automatic tool execution tracing
- **Streaming Responses**: Partial support, manual span finalization needed

.. note::
   For the complete compatibility matrix across all providers, see :doc:`/how-to/integrations/multi-provider`.

Choose Your Instrumentor
------------------------

**Problem**: I need to choose between OpenInference and Traceloop for Google Agent Development Kit (ADK) integration.

**Solution**: Choose the instrumentor that best fits your needs:

- **OpenInference**: Open-source, lightweight, great for getting started
- **Traceloop**: Traceloop does not currently provide a Google ADK instrumentor. Only OpenInference instrumentation is available for this provider.

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
     <button class="tab-button active" onclick="showTab(event, 'google-adk-openinference-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'google-adk-openinference-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, 'google-adk-openinference-advanced')">Advanced Usage</button>
     <button class="tab-button" onclick="showTab(event, 'google-adk-openinference-troubleshoot')">Troubleshooting</button>
   </div>

   <div id="google-adk-openinference-install" class="tab-content active">

**Best for**: Open-source projects, simple tracing needs, getting started quickly

.. code-block:: bash

   # Recommended: Install with Google Agent Development Kit (ADK) integration
   pip install honeyhive[openinference-google-adk]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-google-adk google-adk>=1.0.0

.. raw:: html

   </div>
   <div id="google-adk-openinference-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   import google.adk
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # GOOGLE_API_KEY=your-google-adk-key

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )  # Uses HH_API_KEY from environment
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = GoogleADKInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   # Basic usage with error handling
   try:
       agent = adk.Agent(
           name="document_processor",
           model="gemini-pro"
       )
       
       result = agent.run(
           task="Analyze this document",
           input_data={"document": document_content}
       )
       # Automatically traced! ✨
   except google.adk.ADKError as e:
       print(f"Google Agent Development Kit (ADK) API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="google-adk-openinference-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   import google.adk

   # Initialize with custom configuration
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project",        # Or set HH_PROJECT environment variable
       source="production"            # Or set HH_SOURCE environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = GoogleADKInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   @trace(tracer=tracer, event_type=EventType.chain)
   def multi_agent_workflow(documents: List[str]) -> dict:
       """Advanced example with business context and multiple Google Agent Development Kit (ADK) calls."""
       import google.adk as adk
       
       # Configure Google ADK
       adk.configure(api_key=os.getenv("GOOGLE_API_KEY"))
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type(documents).__name__,
           "business.use_case": "multi_agent_analysis",
           "google-adk.strategy": "parallel_processing",
           "instrumentor.type": "openinference"
       })
       
       try:
           # Create specialized agents
       analyzer = adk.Agent(
           name="document_analyzer", 
           model="gemini-pro",
           tools=["text_analysis", "summarization"]
       )
       
       reviewer = adk.Agent(
           name="quality_reviewer",
           model="gemini-ultra", 
           tools=["quality_check", "fact_verification"]
       )
       
       results = []
       for doc in documents:
           # Agent 1: Analyze document
           analysis = analyzer.run(
               task="Analyze document structure and content",
               input_data={"document": doc}
           )
           
           # Agent 2: Review analysis quality
           review = reviewer.run(
               task="Review analysis for accuracy and completeness", 
               input_data={"analysis": analysis.output}
           )
           
           results.append({
               "document": doc,
               "analysis": analysis.output,
               "review": review.output
           })
           
       # Add result metadata
       enrich_span({
           "business.successful": True,
           "google-adk.models_used": ["gemini-pro", "gemini-ultra"],
           "business.result_confidence": "high"
       })
       
       return {
           "processed_documents": len(results),
           "analysis_results": results,
           "workflow_completed": True
       }
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "google-adk.models_used": ["gemini-pro", "gemini-ultra"],
               "business.result_confidence": "high"
           })
           
           return {"processed_documents": len(results), "analysis_results": results, "workflow_completed": True}
           
       except google.adk.ADKError as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.source": "openinference"
           })
           raise

.. raw:: html

   </div>
   <div id="google-adk-openinference-troubleshoot" class="tab-content">

**Common OpenInference Issues**:

1. **Missing Traces**
   
   .. code-block:: python
   
      # Use correct initialization pattern
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = GoogleADKInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

2. **Performance for High Volume**
   
   .. code-block:: python
   
      # OpenInference uses efficient span processors automatically
      # No additional configuration needed

3. **Multiple Instrumentors**
   
   .. code-block:: python
   
      # You can combine OpenInference with other instrumentors
      from openinference.instrumentation.google_adk import GoogleADKInstrumentor
       from openinference.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               GoogleADKInstrumentor(),
               OpenAIInstrumentor()
           ]
       )

4. **Environment Configuration**
   
   .. code-block:: bash
   
      # HoneyHive configuration
      export HH_API_KEY="your-honeyhive-api-key"
      export HH_SOURCE="production"
      
      # Google Agent Development Kit (ADK) configuration
      export GOOGLE_API_KEY="your-google-adk-api-key"

.. raw:: html

   </div>
   </div>

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

Integrate with Model Context Protocol (MCP)
===========================================

.. note::
   **Problem-solving guide for Model Context Protocol (MCP) integration**
   
   This guide helps you solve specific problems when integrating HoneyHive with Model Context Protocol (MCP), with support for multiple instrumentor options.

This guide covers Model Context Protocol (MCP) integration with HoneyHive's BYOI architecture, supporting both OpenInference and Traceloop instrumentors.

Compatibility
-------------

**Problem**: I need to know if my Python version and Model Context Protocol (MCP) SDK version are compatible with HoneyHive.

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

- **Minimum**: mcp-sdk >= 0.1.0
- **Recommended**: mcp-sdk >= 0.2.0
- **Tested Versions**: 0.2.0, 0.3.0

Instrumentor Compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Instrumentor
     - Status
     - Notes
   * - OpenInference
     - Experimental
     - Basic MCP protocol tracing, tool execution captured
   * - Traceloop
     - Not Supported
     - Traceloop instrumentor not available for MCP - use OpenInference

Known Limitations
^^^^^^^^^^^^^^^^^

- **Protocol Version**: MCP 1.0 protocol required, earlier versions not supported
- **Tool Discovery**: Automatic tool discovery traced, manual tools require enrichment
- **Streaming Tools**: Partial support for streaming tool responses
- **Multi-Server**: Multiple MCP server connections require manual span management

.. note::
   For the complete compatibility matrix across all providers, see :doc:`/how-to/integrations/multi-provider`.

Choose Your Instrumentor
------------------------

**Problem**: I need to choose between OpenInference and Traceloop for Model Context Protocol (MCP) integration.

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
     <button class="tab-button active" onclick="showTab(event, 'mcp-openinference-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'mcp-openinference-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, 'mcp-openinference-advanced')">Advanced Usage</button>
     <button class="tab-button" onclick="showTab(event, 'mcp-openinference-troubleshoot')">Troubleshooting</button>
   </div>

   <div id="mcp-openinference-install" class="tab-content active">

**Best for**: Open-source projects, simple tracing needs, getting started quickly

.. code-block:: bash

   # Recommended: Install with Model Context Protocol (MCP) integration
   pip install honeyhive[openinference-mcp]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-mcp mcp>=1.0.0

.. raw:: html

   </div>
   <div id="mcp-openinference-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.mcp import MCPInstrumentor
   import mcp
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # MCP_API_KEY=your-mcp-key

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )  # Uses HH_API_KEY from environment
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = MCPInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   # Basic usage with error handling
   try:
       import mcp
       
       # Create MCP client
       client = mcp.Client(
           server_url="http://localhost:8000",
           api_key=os.getenv("MCP_API_KEY")
       )
       
       # Execute tool via MCP
       result = client.call_tool(
           name="web_search",
           arguments={"query": "Traceloop MCP integration"}
       )
       # Automatically traced! ✨
   except mcp.MCPError as e:
       print(f"Model Context Protocol (MCP) API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="mcp-openinference-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from openinference.instrumentation.mcp import MCPInstrumentor
   import mcp

   # Initialize with custom configuration
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project",        # Or set HH_PROJECT environment variable
       source="production"            # Or set HH_SOURCE environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = MCPInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   @trace(tracer=tracer, event_type=EventType.chain)
   def multi_tool_mcp_workflow(tasks: List[Dict[str, Any]]) -> dict:
       """Advanced example with business context and multiple Model Context Protocol (MCP) calls."""
       import mcp
       
       # Configure MCP client
       client = mcp.Client(
           server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000"),
           api_key=os.getenv("MCP_API_KEY")
       )
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type(tasks).__name__,
           "business.use_case": "tool_orchestration",
           "mcp.strategy": "mcp_multi_tool",
           "instrumentor.type": "openinference"
       })
       
       try:
           # Execute multiple MCP tools in workflow
       available_tools = [
           "web_search",
           "file_processor", 
           "data_analyzer",
           "content_generator"
       ]
       
       results = []
       for task in tasks:
           task_results = {}
           tool_name = task.get("tool")
           arguments = task.get("arguments", {})
           
           if tool_name in available_tools:
               try:
                   # Execute MCP tool
                   result = client.call_tool(
                       name=tool_name,
                       arguments=arguments
                   )
                   
                   task_results[tool_name] = {
                       "success": True,
                       "result": result.content,
                       "metadata": result.metadata
                   }
                   
               except Exception as tool_error:
                   task_results[tool_name] = {
                       "success": False,
                       "error": str(tool_error)
                   }
           else:
               task_results[tool_name] = {
                   "success": False,
                   "error": f"Tool {tool_name} not available"
               }
           
           results.append({
               "task": task,
               "tool_results": task_results
           })
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "mcp.models_used": ["web_search", "file_processor", "data_analyzer"],
               "business.result_confidence": "high"
           })
           
           return {{RETURN_VALUE}}
           
       except mcp.MCPError as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.source": "openinference"
           })
           raise

.. raw:: html

   </div>
   <div id="mcp-openinference-troubleshoot" class="tab-content">

**Common OpenInference Issues**:

1. **Missing Traces**
   
   .. code-block:: python
   
      # Use correct initialization pattern
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = MCPInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

2. **Performance for High Volume**
   
   .. code-block:: python
   
      # OpenInference uses efficient span processors automatically
      # No additional configuration needed

3. **Multiple Instrumentors**
   
   .. code-block:: python
   
      # You can combine OpenInference with other instrumentors
      from openinference.instrumentation.mcp import MCPInstrumentor
       from openinference.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               MCPInstrumentor(),
              OpenAIInstrumentor()
          ]
      )

4. **Environment Configuration**
   
   .. code-block:: bash
   
      # HoneyHive configuration
      export HH_API_KEY="your-honeyhive-api-key"
      export HH_SOURCE="production"
      
      # MCP configuration
      export MCP_SERVER_URL="http://localhost:8000"
      export MCP_API_KEY="your-mcp-api-key"  # Optional

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>

   <div id="openllmetry-section" class="instrumentor-content">

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, 'mcp-openllmetry-install')">Installation</button>
     <button class="tab-button" onclick="showTab(event, 'mcp-openllmetry-basic')">Basic Setup</button>
     <button class="tab-button" onclick="showTab(event, 'mcp-openllmetry-advanced')">Advanced Usage</button>
     <button class="tab-button" onclick="showTab(event, 'mcp-openllmetry-troubleshoot')">Troubleshooting</button>
   </div>

   <div id="mcp-openllmetry-install" class="tab-content active">

**Best for**: Production deployments, cost tracking, enhanced LLM observability

.. code-block:: bash

   # Recommended: Install with Traceloop Model Context Protocol (MCP) integration
   pip install honeyhive[traceloop-mcp]
   
   # Alternative: Manual installation
   pip install honeyhive opentelemetry-instrumentation-mcp mcp>=1.0.0

.. raw:: html

   </div>
   <div id="mcp-openllmetry-basic" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from opentelemetry.instrumentation.mcp import MCPInstrumentor
   import mcp
   import os

   # Environment variables (recommended for production)
   # .env file:
   # HH_API_KEY=your-honeyhive-key
   # MCP_API_KEY=your-mcp-key

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )  # Uses HH_API_KEY from environment
   
   # Step 2: Initialize Traceloop instrumentor separately with tracer_provider
   instrumentor = MCPInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   # Basic usage with automatic tracing
   try:
       import mcp
       
       # Create MCP client
       client = mcp.Client(
           server_url="http://localhost:8000",
           api_key=os.getenv("MCP_API_KEY")
       )
       
       # Execute tool via MCP
       result = client.call_tool(
           name="web_search",
           arguments={"query": "Traceloop MCP integration"}
       )
       # Automatically traced by Traceloop with enhanced metrics! ✨
   except mcp.MCPError as e:
       print(f"Model Context Protocol (MCP) API error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. raw:: html

   </div>
   <div id="mcp-openllmetry-advanced" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from opentelemetry.instrumentation.mcp import MCPInstrumentor
   import mcp

   # Initialize HoneyHive with Traceloop instrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project",        # Or set HH_PROJECT environment variable
       source="production"            # Or set HH_SOURCE environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = MCPInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   @trace(tracer=tracer, event_type=EventType.chain)
   def multi_tool_mcp_workflow(tasks: List[Dict[str, Any]]) -> dict:
       """Advanced example with business context and enhanced LLM metrics."""
       import mcp
       
       # Configure MCP client
       client = mcp.Client(
           server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000"),
           api_key=os.getenv("MCP_API_KEY")
       )
       
       # Add business context to the trace
       enrich_span({
           "business.input_type": type(tasks).__name__,
           "business.use_case": "tool_orchestration",
           "mcp.strategy": "cost_optimized_mcp_multi_tool",
           "instrumentor.type": "openllmetry",
           "observability.enhanced": True
       })
       
       try:
           # Execute multiple MCP tools in workflow
       available_tools = [
           "web_search",
           "file_processor", 
           "data_analyzer",
           "content_generator"
       ]
       
       results = []
       for task in tasks:
           task_results = {}
           tool_name = task.get("tool")
           arguments = task.get("arguments", {})
           
           if tool_name in available_tools:
               try:
                   # Execute MCP tool
                   result = client.call_tool(
                       name=tool_name,
                       arguments=arguments
                   )
                   
                   task_results[tool_name] = {
                       "success": True,
                       "result": result.content,
                       "metadata": result.metadata
                   }
                   
               except Exception as tool_error:
                   task_results[tool_name] = {
                       "success": False,
                       "error": str(tool_error)
                   }
           else:
               task_results[tool_name] = {
                   "success": False,
                   "error": f"Tool {tool_name} not available"
               }
           
           results.append({
               "task": task,
               "tool_results": task_results
           })
           
           # Add result metadata
           enrich_span({
               "business.successful": True,
               "mcp.models_used": ["web_search", "file_processor", "data_analyzer"],
               "business.result_confidence": "high",
               "openllmetry.cost_tracking": "enabled",
               "openllmetry.token_metrics": "captured"
           })
           
           return {{RETURN_VALUE}}
           
       except mcp.MCPError as e:
           enrich_span({
               "error.type": "api_error", 
               "error.message": str(e),
               "instrumentor.error_handling": "openllmetry"
           })
           raise

.. raw:: html

   </div>
   <div id="mcp-openllmetry-troubleshoot" class="tab-content">

**Common Traceloop Issues**:

1. **Missing Traces**
   
   .. code-block:: python
   
      # Ensure Traceloop instrumentor is passed to tracer
      from opentelemetry.instrumentation.mcp import MCPInstrumentor
      
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = MCPInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

2. **Enhanced Metrics Not Showing**
   
   .. code-block:: python
   
      # Ensure you're using the latest version
      # pip install --upgrade opentelemetry-instrumentation-mcp
      
      # The instrumentor automatically captures enhanced metrics
      from opentelemetry.instrumentation.mcp import MCPInstrumentor
      # Step 1: Initialize HoneyHive tracer first (without instrumentors)
      tracer = HoneyHiveTracer.init(
          project="your-project"  # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentor separately with tracer_provider
      instrumentor = MCPInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

3. **Multiple Traceloop Instrumentors**
   
   .. code-block:: python
   
      # You can combine multiple Traceloop instrumentors
      from opentelemetry.instrumentation.mcp import MCPInstrumentor
       from opentelemetry.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               MCPInstrumentor(),         # Traceloop MCP
               OpenAIInstrumentor()       # Traceloop OpenAI
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
      
      # MCP configuration
      export MCP_SERVER_URL="http://localhost:8000"
      export MCP_API_KEY="your-mcp-api-key"  # Optional

.. raw:: html

   </div>
   </div>

.. raw:: html

   </div>
   </div>

Comparison: OpenInference vs Traceloop for Model Context Protocol (MCP)
-----------------------------------------------------------------------

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
   from openinference.instrumentation.mcp import MCPInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = MCPInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # After (Traceloop) - different instrumentor package
   from opentelemetry.instrumentation.mcp import MCPInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = MCPInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

**From Traceloop to OpenInference**:

.. code-block:: python

   # Before (Traceloop)
   from opentelemetry.instrumentation.mcp import MCPInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = MCPInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # After (OpenInference)
   from openinference.instrumentation.mcp import MCPInstrumentor
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       project="your-project"  # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = MCPInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

See Also
--------

- :doc:`multi-provider` - Use MCP with other providers
- :doc:`../llm-application-patterns` - Common integration patterns
- :doc:`../../tutorials/02-add-llm-tracing-5min` - LLM integration tutorial
- :doc:`../advanced-tracing/index` - Advanced tracing patterns

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

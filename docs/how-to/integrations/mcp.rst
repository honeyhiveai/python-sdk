Model Context Protocol (MCP) Integration
=========================================

Learn how to integrate HoneyHive with MCP (Model Context Protocol) clients and servers for comprehensive agent observability.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The Model Context Protocol (MCP) is a standardized protocol that enables AI agents to securely connect to data sources and tools. HoneyHive's MCP integration provides automatic tracing of MCP client-server communications, giving you complete visibility into your agent workflows.

**Key Benefits:**

- **Zero-Code Tracing**: Existing MCP applications work unchanged
- **End-to-End Visibility**: Complete trace propagation across client-server boundaries
- **Rich Context**: MCP-specific span attributes and metadata
- **Multi-Provider Support**: Works alongside other LLM provider instrumentors

Prerequisites
-------------

**Required:**

- Python 3.11 or higher
- HoneyHive Python SDK installed
- MCP instrumentor package

**Optional:**

- Running MCP server for real testing
- Other OpenInference instrumentors for multi-provider setups

Installation
------------

Install MCP support for HoneyHive:

.. code-block:: bash

   pip install honeyhive[mcp]

This installs the OpenInference MCP instrumentor (version 1.3.0+) alongside the HoneyHive SDK.

Quick Start
-----------

**Step 1: Basic MCP Integration**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.mcp import MCPInstrumentor

   # Initialize tracer with MCP instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       instrumentors=[MCPInstrumentor()]
   )

**Step 2: Use MCP Client Normally**

.. code-block:: python

   import asyncio
   from mcp import MCPServerStdio
   from agents import Agent, Runner

   async def main():
       # MCP client-server communication is automatically traced
       async with MCPServerStdio(
           name="Financial Analysis Server",
           params={
               "command": "fastmcp",
               "args": ["run", "./server.py"],
           }
       ) as server:
           
           agent = Agent(
               name="Financial Assistant",
               instructions="Use financial tools to answer questions.",
               mcp_servers=[server]
           )
           
           # This entire workflow is traced end-to-end
           result = await Runner.run(
               starting_agent=agent,
               input="What's the P/E ratio for AAPL?"
           )
           
           print(f"Result: {result.final_output}")

   asyncio.run(main())

**Step 3: Verify Tracing**

Your MCP operations will appear in the HoneyHive dashboard with:

- Client-server communication spans
- Tool execution traces
- Context propagation across boundaries
- MCP-specific metadata and attributes

Multi-Provider Integration
--------------------------

Combine MCP with other LLM providers for complete observability:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.mcp import MCPInstrumentor
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Multi-provider setup
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       instrumentors=[
           MCPInstrumentor(),      # Trace MCP operations
           OpenAIInstrumentor()    # Trace OpenAI calls within tools
       ]
   )

   # Now both MCP and OpenAI operations are traced
   import openai

   async def analyze_with_llm(mcp_data):
       """Function that uses both MCP tools and LLM calls."""
       
       # MCP tool call (automatically traced)
       tool_result = await call_mcp_tool("analyze_data", mcp_data)
       
       # OpenAI call (automatically traced)
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{
               "role": "user", 
               "content": f"Summarize this analysis: {tool_result}"
           }]
       )
       
       return response.choices[0].message.content

Advanced Configuration
----------------------

**Environment Variables**

Configure MCP tracing using environment variables:

.. code-block:: bash

   # HoneyHive configuration
   export HH_API_KEY="your-api-key"
   export HH_PROJECT="mcp-project"
   export HH_SOURCE="production"
   
   # Optional: MCP-specific settings
   export MCP_SERVER_TIMEOUT="30"
   export MCP_TRACE_LEVEL="INFO"

**Custom Span Enrichment**

Enrich MCP spans with additional context:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.models import EventType

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[MCPInstrumentor()]
   )

   @trace(event_type=EventType.tool)
   def enhanced_mcp_tool(tool_name: str, params: dict):
       """MCP tool with custom enrichment."""
       
       # Add custom metadata
       tracer.enrich_span(
           metadata={"mcp_tool_version": "2.1.0"},
           metrics={"input_size": len(str(params))}
       )
       
       # Your MCP tool logic here
       return call_mcp_server(tool_name, params)

**Performance Optimization**

Optimize MCP tracing for production:

.. code-block:: python

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[MCPInstrumentor()],
       disable_http_tracing=True,  # Reduce overhead
   )

Error Handling
--------------

Handle MCP integration errors gracefully:

**Installation Issues**

.. code-block:: python

   def setup_mcp_tracer():
       """Set up MCP tracer with error handling."""
       try:
           from openinference.instrumentation.mcp import MCPInstrumentor
           instrumentor = MCPInstrumentor()
       except ImportError:
           print("MCP instrumentor not available.")
           print("Install with: pip install honeyhive[mcp]")
           return None
       
       try:
           tracer = HoneyHiveTracer.init(
               api_key="your-api-key",
               instrumentors=[instrumentor]
           )
           return tracer
       except Exception as e:
           print(f"Failed to initialize MCP tracer: {e}")
           return None

**Runtime Errors**

.. code-block:: python

   async def robust_mcp_operation(tool_name: str, params: dict):
       """MCP operation with comprehensive error handling."""
       try:
           # MCP operation
           result = await call_mcp_tool(tool_name, params)
           return {"status": "success", "result": result}
           
       except ConnectionError as e:
           # MCP server connection issues
           print(f"MCP server connection failed: {e}")
           return {"status": "connection_error", "error": str(e)}
           
       except TimeoutError as e:
           # MCP operation timeout
           print(f"MCP operation timed out: {e}")
           return {"status": "timeout", "error": str(e)}
           
       except Exception as e:
           # Other MCP errors
           print(f"MCP operation failed: {e}")
           return {"status": "error", "error": str(e)}

Debugging and Monitoring
------------------------

**Trace Validation**

Verify MCP traces are being captured:

.. code-block:: python

   import logging

   # Enable debug logging
   logging.basicConfig(level=logging.DEBUG)

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[MCPInstrumentor()]
   )

   # Check tracer status
   print(f"Tracer initialized: {tracer is not None}")
   print(f"Project: {tracer.project}")

**Performance Monitoring**

Monitor MCP integration performance:

.. code-block:: python

   import time
   from honeyhive import trace
   from honeyhive.models import EventType

   @trace(event_type=EventType.tool)
   def monitored_mcp_tool(tool_name: str, params: dict):
       """MCP tool with performance monitoring."""
       start_time = time.time()
       
       try:
           result = call_mcp_server(tool_name, params)
           
           # Record performance metrics
           duration = time.time() - start_time
           tracer.enrich_span(
               metrics={
                   "duration_seconds": duration,
                   "tool_name": tool_name,
                   "param_count": len(params)
               }
           )
           
           return result
           
       except Exception as e:
           # Record error metrics
           duration = time.time() - start_time
           tracer.enrich_span(
               metrics={
                   "duration_seconds": duration,
                   "error": str(e),
                   "tool_name": tool_name
               }
           )
           raise

Production Deployment
---------------------

**Best Practices for Production**

1. **Environment Configuration**:

   .. code-block:: bash

      # Production environment
      export HH_API_KEY="prod-api-key"
      export HH_PROJECT="production-mcp"
      export HH_SOURCE="production"
      export HH_DISABLE_HTTP_TRACING="true"

2. **Resource Management**:

   .. code-block:: python

      tracer = HoneyHiveTracer.init(
          api_key=os.getenv("HH_API_KEY"),          source=os.getenv("HH_SOURCE", "production"),
          instrumentors=[MCPInstrumentor()],
          disable_http_tracing=True  # Optimize for production
      )

3. **Graceful Shutdown**:

   .. code-block:: python

      import atexit

      def cleanup_tracer():
          """Ensure traces are flushed on shutdown."""
          if hasattr(tracer, 'force_flush'):
              tracer.force_flush()

      atexit.register(cleanup_tracer)

**Health Checks**

Implement health checks for MCP integration:

.. code-block:: python

   def check_mcp_health():
       """Check MCP integration health."""
       health_status = {
           "mcp_instrumentor": False,
           "honeyhive_tracer": False,
           "mcp_server_connection": False
       }
       
       try:
           from openinference.instrumentation.mcp import MCPInstrumentor
           health_status["mcp_instrumentor"] = True
       except ImportError:
           pass
       
       try:
           tracer = HoneyHiveTracer.init(
               api_key="health-check",
               test_mode=True,
               instrumentors=[MCPInstrumentor()]
           )
           health_status["honeyhive_tracer"] = tracer is not None
       except Exception:
           pass
       
       return health_status

Troubleshooting
---------------

**Common Issues and Solutions**

**Issue: MCP instrumentor not found**

.. code-block:: text

   ImportError: No module named 'openinference.instrumentation.mcp'

**Solution:**

.. code-block:: bash

   pip install honeyhive[mcp]

**Issue: Traces not appearing in dashboard**

**Possible causes:**

1. **API key not set**: Verify ``HH_API_KEY`` environment variable
2. **Wrong project name**: Check ``HH_PROJECT`` matches your HoneyHive project
3. **Test mode enabled**: Disable test mode for production tracing

**Solution:**

.. code-block:: python

   # Verify configuration
   tracer = HoneyHiveTracer.init(
       api_key="your-real-api-key",  # Not test-key

       test_mode=False,               # Disable for real tracing
       instrumentors=[MCPInstrumentor()]
   )

**Issue: Poor performance with MCP tracing**

**Solutions:**

1. **Enable HTTP tracing optimization**:

   .. code-block:: python

      tracer = HoneyHiveTracer.init(
          api_key="your-api-key",
          disable_http_tracing=True,  # Default, but explicit
          instrumentors=[MCPInstrumentor()]
      )

2. **Reduce trace frequency** for high-volume operations
3. **Use async operations** where possible

**Issue: MCP server connection problems**

**Debugging steps:**

1. **Check server availability**:

   .. code-block:: bash

      # Test MCP server directly
      curl -X POST http://localhost:8080/health

2. **Verify network configuration**:

   .. code-block:: python

      # Test with timeout settings
      async with MCPServerStdio(
          name="Test Server",
          params={"command": "your-server"},
          client_session_timeout_seconds=30  # Adjust timeout
      ) as server:
          # Your MCP operations

3. **Check logs** for detailed error messages

**Getting Help**

If you continue to experience issues:

1. **Check the logs** for detailed error messages
2. **Verify your environment** matches the prerequisites  
3. **Test with the example code** provided in this guide
4. **Contact support** with your configuration and error details

See Also
--------

- :doc:`multi-provider` - Use MCP with other LLM providers
- :doc:`../troubleshooting` - Common integration issues  
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial

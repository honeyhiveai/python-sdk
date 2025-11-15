End-to-End Distributed Tracing
==============================

**Problem:** You have a multi-service AI agent application and need to trace requests as they flow across service boundaries to understand performance, errors, and dependencies.

**Solution:** Use HoneyHive's distributed tracing with context propagation to create unified traces across multiple services in under 15 minutes.

This tutorial walks you through building a distributed AI agent system using Google ADK, demonstrating how traces flow seamlessly across service boundaries.

What You'll Build
-----------------

A distributed AI agent architecture with mixed invocation patterns:

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph LR
       Client[Client App<br/>Process A]
       Principal[Principal Agent<br/>Process A]
       RemoteAgent[Research Agent<br/>Process B - Remote]
       LocalAgent[Analysis Agent<br/>Process A - Local]
       
       Client -->|user_call| Principal
       Principal -->|HTTP + Context| RemoteAgent
       Principal -->|Direct Call| LocalAgent
       
       classDef client fill:#7b1fa2,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef principal fill:#1565c0,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef remote fill:#ef6c00,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef local fill:#2e7d32,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class Client client
       class Principal principal
       class RemoteAgent remote
       class LocalAgent local

**Architecture:**

- **Client Application**: Initiates multi-turn conversation with agents
- **Principal Agent**: Orchestrates calls to research and analysis agents
- **Research Agent** (Remote): Runs in separate process, receives context via HTTP
- **Analysis Agent** (Local): Runs in same process, directly inherits context

**Key Learning:**

- How to propagate trace context to remote services using HTTP headers
- How to use ``with_distributed_trace_context()`` for simplified server-side tracing
- How to create unified traces spanning both local and distributed agents
- How to see complete request flows in HoneyHive across service boundaries

Prerequisites
-------------

- Python 3.11+ installed
- HoneyHive API key from https://app.honeyhive.ai
- Google Gemini API key (get one at https://aistudio.google.com/apikey)
- 15 minutes of time

Installation
------------

Install required packages:

.. code-block:: bash

   pip install honeyhive google-adk openinference-instrumentation-google-adk flask requests

Step 1: Set Environment Variables
----------------------------------

Create a ``.env`` file with your API keys:

.. code-block:: bash

   # Required
   HH_API_KEY=your_honeyhive_api_key_here
   HH_PROJECT=distributed-tracing-tutorial
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   
   # Optional
   AGENT_SERVER_URL=http://localhost:5003

Load environment variables:

.. code-block:: bash

   source .env

Step 2: Create the Agent Server (Remote Service)
-------------------------------------------------

The remote service that runs a Google ADK research agent.

Create ``agent_server.py``:

.. code-block:: python

   """Google ADK Agent Server - Demonstrates with_distributed_trace_context() helper."""
   
   from flask import Flask, request, jsonify
   from honeyhive import HoneyHiveTracer
   from honeyhive.tracer.processing.context import with_distributed_trace_context
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   from google.adk.agents import LlmAgent
   from google.adk.runners import Runner
   from google.adk.sessions import InMemorySessionService
   from google.genai import types
   import os
   
   # Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project=os.getenv("HH_PROJECT", "distributed-tracing-tutorial"),
       source="agent-server"
   )
   
   # Initialize Google ADK instrumentor
   instrumentor = GoogleADKInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   app = Flask(__name__)
   session_service = InMemorySessionService()
   
   async def run_agent(user_id: str, query: str, agent_name: str) -> str:
       """Run Google ADK agent - automatically part of distributed trace."""
       # Your Agent Code here 
       return final_response or ""
   
   @app.route("/agent/invoke", methods=["POST"])
   async def invoke_agent():
       """Invoke agent with distributed tracing - ONE LINE setup!"""
       
       # 🎯 Single line replaces ~65 lines of context management boilerplate
       with with_distributed_trace_context(dict(request.headers), tracer):
           # All Google ADK spans created here automatically:
           # 1. Link to the client's trace (same trace_id)
           # 2. Use the client's session_id, project, source
           # 3. Appear as children of the client's call_agent_1 span
           
           try:
               data = request.get_json()
               result = await run_agent(
                   data.get("user_id", "default_user"),
                   data.get("query", ""),
                   data.get("agent_name", "research_agent")
               )
               return jsonify({
                   "response": result,
                   "agent": data.get("agent_name", "research_agent")
               })
           except Exception as e:
               return jsonify({"error": str(e)}), 500
   
   if __name__ == "__main__":
       print("🤖 Agent Server starting on port 5003...")
       app.run(port=5003, debug=True, use_reloader=False)

**What's happening:**

1. ``with_distributed_trace_context()`` automatically:
   - Extracts trace context from HTTP headers
   - Parses ``session_id``, ``project``, ``source`` from baggage
   - Attaches context so all spans link to client's trace
   - Handles cleanup (even on exceptions)
   
2. Google ADK instrumentor automatically creates child spans for agent operations

3. **Result**: All agent spans appear in the same unified trace as the client

**Key benefit**: ONE LINE (``with_distributed_trace_context``) replaces ~65 lines of manual context extraction, baggage parsing, context attachment, and cleanup code.

Step 3: Create the Client Application
--------------------------------------

The client orchestrates both remote and local agent calls.

Create ``client_app.py``:

.. code-block:: python

   """Client Application - Orchestrates remote and local agent calls."""
   
   import asyncio
   import os
   from typing import Any
   import requests
   
   from google.adk.sessions import InMemorySessionService
   from google.adk.agents import LlmAgent
   from google.adk.runners import Runner
   from google.genai import types
   
   from honeyhive import HoneyHiveTracer, trace
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   from honeyhive.tracer.processing.context import (
       enrich_span_context,
       inject_context_into_carrier
   )
   
   # Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project=os.getenv("HH_PROJECT", "distributed-tracing-tutorial"),
       source="client-app"
   )
   
   # Initialize Google ADK instrumentor (for local agent calls)
   instrumentor = GoogleADKInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   async def main():
       """Main entry point - demonstrates multi-turn conversation."""
       session_service = InMemorySessionService()
       app_name = "distributed_agent_demo"
       user_id = "demo_user"
       
       # Execute two user calls (multi-turn conversation)
       await user_call(session_service, app_name, user_id,
                      "Explain the benefits of renewable energy")
       await user_call(session_service, app_name, user_id,
                      "What are the main challenges?")
   
   @trace(event_type="chain", event_name="user_call")
   async def user_call(
       session_service: Any,
       app_name: str,
       user_id: str,
       user_query: str
   ) -> str:
       """User entry point - initiates the agent workflow."""
       result = await call_principal(
           session_service,
           app_name,
           user_id,
           user_query,
           os.getenv("AGENT_SERVER_URL", "http://localhost:5003")
       )
       return result
   
   @trace(event_type="chain", event_name="call_principal")
   async def call_principal(
       session_service: Any,
       app_name: str,
       user_id: str,
       query: str,
       agent_server_url: str
   ) -> str:
       """Principal agent - orchestrates remote and local agents."""
       
       # Agent 1: Research (REMOTE - distributed tracing)
       agent_1_result = await call_agent(
           session_service, app_name, user_id, query,
           use_research_agent=True, agent_server_url=agent_server_url
       )
       
       # Agent 2: Analysis (LOCAL - same process)
       agent_2_result = await call_agent(
           session_service, app_name, user_id, agent_1_result,
           use_research_agent=False, agent_server_url=agent_server_url
       )
       
       return f"Research: {agent_1_result}\n\nAnalysis: {agent_2_result}"
   
   async def call_agent(
       session_service: Any,
       app_name: str,
       user_id: str,
       query: str,
       use_research_agent: bool,
       agent_server_url: str
   ) -> str:
       """Call agent - demonstrates mixed invocation patterns."""
       
       if use_research_agent:
           # REMOTE invocation: Call agent server via HTTP
           with enrich_span_context(
               event_name="call_agent_1",
               inputs={"query": query}
           ):
               # Inject trace context into HTTP headers
               headers = {}
               inject_context_into_carrier(headers, tracer)
               
               # HTTP call to remote agent server
               response = requests.post(
                   f"{agent_server_url}/agent/invoke",
                   json={
                       "user_id": user_id,
                       "query": query,
                       "agent_name": "research_agent"
                   },
                   headers=headers,  # Trace context propagates here!
                   timeout=60
               )
               response.raise_for_status()
               result = response.json().get("response", "")
               
               tracer.enrich_span(
                   outputs={"response": result},
                   metadata={"mode": "remote"}
               )
               return result
       
       else:
           # LOCAL invocation: Run agent in same process
           with enrich_span_context(
               event_name="call_agent_2",
               inputs={"research": query}
           ):
               # You can run your local analysis agent here
               
               tracer.enrich_span(
                   outputs={"response": result},
                   metadata={"mode": "local"}
               )
               return result
   
   if __name__ == "__main__":
       asyncio.run(main())

**What's happening:**

**Client Side** (Context Injection):

1. ``@trace`` decorators create traced functions
2. ``enrich_span_context()`` creates explicit spans for each agent call
3. ``inject_context_into_carrier()`` adds trace context to HTTP headers
4. Headers are sent with the HTTP request to the agent server

**Server Side** (Context Extraction):

5. Agent server uses ``with_distributed_trace_context()`` to extract context
6. All Google ADK spans on server inherit the client's context
7. Spans from both client and server appear in same unified trace

**Mixed Invocation**:

- **Agent 1 (Remote)**: Calls agent server via HTTP, demonstrating distributed tracing
- **Agent 2 (Local)**: Runs in same process, demonstrating local span nesting

Step 4: Run and Test
--------------------

**Terminal 1** - Start the Agent Server:

.. code-block:: bash

   source .env
   python agent_server.py

You should see:

.. code-block:: text

   🤖 Agent Server starting on port 5003...
   * Running on http://127.0.0.1:5003

**Terminal 2** - Run the Client Application:

.. code-block:: bash

   source .env
   python client_app.py

You should see the client making two user calls (multi-turn conversation):

.. code-block:: text

   Research: Renewable energy sources, such as solar, wind, and hydropower...
   
   Analysis: The transition to renewable energy requires addressing...

**What's Happening:**

1. Client makes first ``user_call`` asking about benefits of renewable energy
2. ``call_principal`` orchestrates two agents:
   - **Agent 1** (Remote): HTTP call to agent server → research findings
   - **Agent 2** (Local): Runs in same process → analyzes research
3. Client makes second ``user_call`` asking about challenges
4. Same flow repeats for the second question
5. **All spans** from both calls appear in same HoneyHive session

Step 5: View in HoneyHive
--------------------------

1. Go to https://app.honeyhive.ai
2. Navigate to project: ``distributed-tracing-tutorial``
3. Click "Sessions" in the left sidebar
4. Find your session - you'll see:

**Unified Trace Hierarchy (First User Call):**

.. code-block:: text

   📊 user_call [ROOT]
   └── 🔗 call_principal
       ├── 🌐 call_agent_1 (Remote - Process B)
       │   └── 🤖 agent_run [research_agent] (on server)
       │       └── 💬 gemini_chat_completion (Google ADK instrumentation)
       └── 📍 call_agent_2 (Local - Process A)
           └── 🤖 agent_run [analysis_agent] (same process)
               └── 💬 gemini_chat_completion (Google ADK instrumentation)

**Key observations:**

- **Single session across all operations** (both user calls in same session)
- **Parent-child relationships preserved** across service boundaries
- **call_agent_1** (remote) shows HTTP call to agent server
- **call_agent_2** (local) shows in-process agent execution
- **Google ADK spans** (``agent_run``, ``gemini_chat_completion``) automatically captured
- **Source attribution**: 
  - ``client-app`` for client-side spans
  - ``agent-server`` for server-side spans
- **All metadata enriched**: inputs, outputs, mode (remote/local)

What You Learned
----------------

✅ **Simplified Distributed Tracing (v1.0+)**

- **Server-side**: ``with_distributed_trace_context()`` - ONE LINE replaces ~65 lines of boilerplate
- **Client-side**: ``inject_context_into_carrier()`` - Add trace context to HTTP headers
- Automatic baggage extraction (``session_id``, ``project``, ``source``)
- Thread-safe context isolation per request

✅ **Mixed Invocation Patterns**

- **Remote agents**: HTTP calls with context propagation
- **Local agents**: In-process execution with automatic context inheritance
- Both patterns unified in same trace
- Google ADK instrumentor automatically captures agent operations

✅ **Key HoneyHive APIs Used**

- ``inject_context_into_carrier(headers, tracer)`` - Client-side: inject context into HTTP headers
- ``with_distributed_trace_context(headers, tracer)`` - Server-side: extract and attach context (RECOMMENDED)
- ``enrich_span_context(event_name, inputs, outputs)`` - Create enriched spans with explicit names
- ``tracer.enrich_span(outputs, metadata)`` - Add attributes to current span
- ``@trace`` decorator - Automatic function tracing (preserves distributed baggage v1.0+)

✅ **Practical Skills**

- Tracing multi-service AI agent systems
- Debugging distributed agent workflows
- Finding performance bottlenecks across services
- Understanding agent interaction patterns end-to-end

Troubleshooting
---------------

**Problem: Remote agent spans don't appear in the trace**

**Solution**: Check that context is being properly injected and extracted:

.. code-block:: python

   # Client side: Must inject context into headers
   headers = {}
   inject_context_into_carrier(headers, tracer)
   response = requests.post(url, json=data, headers=headers)  # headers required!
   
   # Server side: Use with_distributed_trace_context() helper
   with with_distributed_trace_context(dict(request.headers), tracer):
       # All spans created here will link to client's trace
       result = await run_agent(...)

**Problem: Agent server shows "Connection refused"**

**Solution**: Ensure the agent server is running:

.. code-block:: bash

   # Terminal 1
   source .env
   python agent_server.py
   
   # Wait for: "🤖 Agent Server starting on port 5003..."

**Problem: Missing GOOGLE_API_KEY error**

**Solution**: Set your Google Gemini API key:

.. code-block:: bash

   # In .env file
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Reload
   source .env

**Problem: Server and client show different projects in HoneyHive**

**Solution**: Both must use the same project name:

.. code-block:: python

   # In both agent_server.py and client_app.py
   tracer = HoneyHiveTracer.init(
       project="distributed-tracing-tutorial",  # Must match!
       source="agent-server"  # Can differ per service
   )

Next Steps
----------

**Explore more Google ADK integrations:**

- Try different Google ADK agents (planning, execution, tool-using agents)
- Add more remote services to the distributed trace
- Experiment with different agent orchestration patterns

**Production considerations:**

- Add error handling and retry logic for remote calls
- Implement timeouts for agent invocations
- Add monitoring and health checks for agent servers
- Consider using async HTTP clients (``httpx``, ``aiohttp``) for better performance
- Implement sampling for high-traffic production systems

**Key resources:**

- :doc:`../reference/api/utilities` - Full API reference for distributed tracing utilities
- :doc:`../how-to/advanced-tracing/custom-spans` - Learn about ``enrich_span_context()`` and span enrichment
- `Google ADK Documentation <https://github.com/google/genkit>`_ - Learn more about Google ADK

**Key Takeaway:** With ``with_distributed_trace_context()``, distributed tracing is now a ONE LINE operation on the server side. You can trace complex multi-agent systems across process boundaries with minimal code. 🎉


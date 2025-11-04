End-to-End Distributed Tracing
==============================

**Problem:** You have a multi-service LLM application and need to trace requests as they flow across service boundaries to understand performance, errors, and dependencies.

**Solution:** Use HoneyHive's distributed tracing with context propagation to create unified traces across multiple services in under 20 minutes.

This tutorial walks you through building a complete distributed system with three services that share trace context, giving you end-to-end visibility into request flows.

What You'll Build
-----------------

A microservices architecture with distributed tracing:

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph LR
       Client[Client Request]
       Gateway[API Gateway<br/>Port 5000]
       UserSvc[User Service<br/>Port 5001]
       LLMSvc[LLM Service<br/>Port 5002]
       
       Client -->|HTTP POST| Gateway
       Gateway -->|Propagate Context| UserSvc
       UserSvc -->|Propagate Context| LLMSvc
       
       classDef client fill:#7b1fa2,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef gateway fill:#1565c0,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef service fill:#2e7d32,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef llm fill:#ef6c00,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class Client client
       class Gateway gateway
       class UserSvc service
       class LLMSvc llm

**Architecture:**

- **API Gateway**: Entry point, routes requests
- **User Service**: Validates users, enriches context
- **LLM Service**: Generates AI responses

**Key Learning:**

- How to propagate trace context across services
- How to inject context into HTTP headers
- How to extract context from incoming requests
- How to see unified traces in HoneyHive

Prerequisites
-------------

- Python 3.11+ installed
- HoneyHive API key from https://app.honeyhive.ai
- OpenAI API key (or any LLM provider)
- 20 minutes of time

Installation
------------

Install required packages:

.. code-block:: bash

   pip install honeyhive[openinference-openai] flask requests

Step 1: Create the LLM Service
-------------------------------

The downstream service that makes LLM calls.

Create ``llm_service.py``:

.. code-block:: python

   from flask import Flask, request, jsonify
   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.tracer.processing.context import extract_context_from_carrier
   from honeyhive.models import EventType
   from opentelemetry import context
   import openai
   
   # Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init(
       project="distributed-tracing-tutorial",
       source="llm-service"
   )
   
   app = Flask(__name__)
   
   @app.route('/generate', methods=['POST'])
   def generate():
       """Generate LLM response with distributed trace context."""
       
       # Step 1: Extract trace context from incoming headers
       incoming_context = extract_context_from_carrier(dict(request.headers), tracer)
       
       # Step 2: Attach context so our spans are children of parent trace
       if incoming_context:
           token = context.attach(incoming_context)
       
       # Step 3: Create traced operation
       @trace(tracer=tracer, event_type=EventType.model)
       def generate_response(user_id: str, prompt: str) -> str:
           """Generate LLM response - automatically part of distributed trace."""
           
           tracer.enrich_span({
               "service": "llm-service",
               "user_id": user_id,
               "prompt_length": len(prompt)
           })
           
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{"role": "user", "content": prompt}]
           )
           
           result = response.choices[0].message.content
           tracer.enrich_span({"response_length": len(result)})
           
           return result
       
       # Execute traced function
       data = request.get_json()
       result = generate_response(data['user_id'], data['prompt'])
       
       # Detach context
       if incoming_context:
           context.detach(token)
       
       return jsonify({"response": result})
   
   if __name__ == '__main__':
       print("🔥 LLM Service starting on port 5002...")
       app.run(port=5002, debug=True)

**What's happening:**

1. ``extract_context_from_carrier()`` extracts trace context from HTTP headers
2. ``context.attach()`` makes our spans children of the parent trace
3. The ``@trace`` decorator automatically uses the attached context
4. All operations appear in a single unified trace

Step 2: Create the User Service
--------------------------------

The middle service that validates users and calls the LLM service.

Create ``user_service.py``:

.. code-block:: python

   from flask import Flask, request, jsonify
   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.tracer.processing.context import (
       extract_context_from_carrier,
       inject_context_into_carrier
   )
   from honeyhive.models import EventType
   from opentelemetry import context
   import requests
   
   # Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init(
       project="distributed-tracing-tutorial",
       source="user-service"
   )
   
   app = Flask(__name__)
   
   @app.route('/process', methods=['POST'])
   def process():
       """Process user request with distributed tracing."""
       
       # Extract context from incoming request
       incoming_context = extract_context_from_carrier(dict(request.headers), tracer)
       
       if incoming_context:
           token = context.attach(incoming_context)
       
       @trace(tracer=tracer, event_type=EventType.chain)
       def process_user_request(user_id: str, query: str) -> dict:
           """Validate user and call LLM service."""
           
           tracer.enrich_span({
               "service": "user-service",
               "user_id": user_id,
               "operation": "process_request"
           })
           
           # Step 1: Validate user
           is_valid = validate_user(user_id)
           
           if not is_valid:
               tracer.enrich_span({"validation": "failed"})
               return {"error": "Invalid user"}
           
           tracer.enrich_span({"validation": "passed"})
           
           # Step 2: Inject context for downstream service
           headers = {}
           inject_context_into_carrier(headers, tracer)
           
           # Step 3: Call LLM service with propagated context
           response = requests.post(
               "http://localhost:5002/generate",
               json={"user_id": user_id, "prompt": query},
               headers=headers  # Trace context in headers
           )
           
           tracer.enrich_span({"downstream_status": response.status_code})
           
           return response.json()
       
       @trace(tracer=tracer, event_type=EventType.tool)
       def validate_user(user_id: str) -> bool:
           """Validate user - appears as child span."""
           
           tracer.enrich_span({"operation": "validate_user", "user_id": user_id})
           
           # Simulate validation logic
           valid = user_id.startswith("user_")
           tracer.enrich_span({"is_valid": valid})
           
           return valid
       
       # Execute
       data = request.get_json()
       result = process_user_request(data['user_id'], data['query'])
       
       if incoming_context:
           context.detach(token)
       
       return jsonify(result)
   
   if __name__ == '__main__':
       print("👤 User Service starting on port 5001...")
       app.run(port=5001, debug=True)

**What's happening:**

1. Extracts context from incoming request (from API Gateway)
2. Creates traced operations that are children of parent span
3. Injects context into headers for downstream call
4. LLM Service receives the same trace context

Step 3: Create the API Gateway
-------------------------------

The entry point that initiates the distributed trace.

Create ``api_gateway.py``:

.. code-block:: python

   from flask import Flask, request, jsonify
   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.tracer.processing.context import inject_context_into_carrier
   from honeyhive.models import EventType
   import requests
   
   # Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init(
       project="distributed-tracing-tutorial",
       source="api-gateway"
   )
   
   app = Flask(__name__)
   
   @app.route('/api/query', methods=['POST'])
   @trace(tracer=tracer, event_type=EventType.session)
   def handle_query():
       """API Gateway - initiates distributed trace."""
       
       data = request.get_json()
       
       tracer.enrich_span({
           "service": "api-gateway",
           "endpoint": "/api/query",
           "user_id": data.get('user_id'),
           "client_ip": request.remote_addr
       })
       
       # Inject context into headers for downstream service
       headers = {}
       inject_context_into_carrier(headers, tracer)
       
       tracer.enrich_span({"propagated_headers": list(headers.keys())})
       
       # Call user service with trace context
       response = requests.post(
           "http://localhost:5001/process",
           json=data,
           headers=headers  # Trace context propagates here
       )
       
       tracer.enrich_span({
           "user_service_status": response.status_code,
           "response_size": len(response.content)
       })
       
       return jsonify(response.json())
   
   if __name__ == '__main__':
       print("🌐 API Gateway starting on port 5000...")
       app.run(port=5000, debug=True)

**What's happening:**

1. ``@trace`` decorator creates the root span
2. ``inject_context_into_carrier()`` adds trace context to headers
3. User Service receives these headers and continues the trace
4. Entire request flow appears as single unified trace

Step 4: Run and Test
--------------------

**Terminal 1** - Start LLM Service:

.. code-block:: bash

   python llm_service.py

**Terminal 2** - Start User Service:

.. code-block:: bash

   python user_service.py

**Terminal 3** - Start API Gateway:

.. code-block:: bash

   python api_gateway.py

**Terminal 4** - Test the distributed trace:

.. code-block:: bash

   curl -X POST http://localhost:5000/api/query \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user_123", "query": "Explain distributed tracing"}'

**Expected response:**

.. code-block:: json

   {
     "response": "Distributed tracing is a method..."
   }

Step 5: View in HoneyHive
--------------------------

1. Go to https://app.honeyhive.ai
2. Navigate to project: ``distributed-tracing-tutorial``
3. Click "Traces" in the left sidebar
4. Find your trace - you'll see:

**Unified Trace Hierarchy:**

.. code-block:: text

   📊 handle_query (api-gateway) [ROOT]
   ├── 👤 process_user_request (user-service)
   │   ├── ✓ validate_user (user-service)
   │   └── 🤖 generate_response (llm-service)
   │       └── 💬 openai.chat.completions.create

**Key observations:**

- Single trace ID across all three services
- Parent-child relationships preserved
- Service names show where each span originated
- Timing shows bottlenecks (LLM call is slowest)
- All metadata enriched at each step

What You Learned
----------------

✅ **Context Propagation**

- How to inject trace context into HTTP headers
- How to extract context from incoming requests
- How to attach context so spans become children

✅ **Distributed Architecture**

- Multi-service tracing with Flask
- Propagating context through service mesh
- Maintaining trace hierarchy across services

✅ **HoneyHive APIs**

- ``inject_context_into_carrier(headers, tracer)`` - Add context to headers
- ``extract_context_from_carrier(headers, tracer)`` - Extract context from headers
- ``context.attach(ctx)`` - Make spans children of parent trace
- ``tracer.enrich_span()`` - Instance method for explicit tracer enrichment (v1.0 primary API)

✅ **Practical Skills**

- Debugging multi-service flows
- Finding performance bottlenecks across services
- Understanding request journeys end-to-end

Troubleshooting
---------------

**Problem: Traces appear as separate traces, not unified**

**Solution:** Check that:

.. code-block:: python

   # In calling service: inject context
   headers = {}
   inject_context_into_carrier(headers, tracer)
   requests.post(url, headers=headers)  # Must pass headers!
   
   # In receiving service: extract and attach
   incoming_context = extract_context_from_carrier(request.headers, tracer)
   if incoming_context:
       token = context.attach(incoming_context)

**Problem: Headers not propagating**

**Solution:** Verify Flask passes headers correctly:

.. code-block:: python

   # Convert Flask headers to dict
   headers_dict = dict(request.headers)
   incoming_context = extract_context_from_carrier(headers_dict, tracer)

**Problem: Services show different projects**

**Solution:** All services should use the same project:

.. code-block:: python

   # Same project name in all three services
   tracer = HoneyHiveTracer.init(
       project="distributed-tracing-tutorial",  # Must match!
       source="service-name"  # Can differ per service
   )

Next Steps
----------

**Expand your distributed tracing:**

- :doc:`../how-to/advanced-tracing/advanced-patterns` - Additional patterns
- :doc:`../how-to/advanced-tracing/span-enrichment` - Enrich traces with metadata
- :doc:`../explanation/concepts/tracing-fundamentals` - Deep dive into concepts

**Production considerations:**

- :doc:`../how-to/deployment/production` - Production deployment patterns
- Add service mesh (Istio, Linkerd) for automatic propagation
- Implement sampling for high-traffic services
- Add health checks and monitoring

**Key Takeaway:** Distributed tracing unifies your view across services, making debugging and optimization dramatically easier. You can now trace requests from entry point to LLM call and back. 🎉


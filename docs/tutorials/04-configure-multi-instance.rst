Configure Multi-Instance Tracers
================================

**Problem:** You need different tracer configurations for different parts of your application - like separate tracers for production vs experiments, or different projects for different features.

**Solution:** Create multiple HoneyHiveTracer instances with different configurations, and route traces to the appropriate project based on your needs.

This guide shows you how to set up and manage multiple tracers in a single application.

Why Multiple Tracers?
---------------------

Common scenarios where you need multiple tracers:

**1. Separate Projects:**

- Production traffic → ``production`` project
- Experimental features → ``experiments`` project
- Internal tools → ``internal-tools`` project

**2. Different Environments:**

- Development → ``my-app-dev``
- Staging → ``my-app-staging``
- Production → ``my-app-prod``

**3. Different Teams/Features:**

- Customer-facing API → ``customer-api`` project
- Admin dashboard → ``admin-dashboard`` project
- Background jobs → ``background-jobs`` project

**4. A/B Testing:**

- Control group → ``ab-test-control``
- Variant A → ``ab-test-variant-a``
- Variant B → ``ab-test-variant-b``

Basic Multi-Instance Setup
--------------------------

Create multiple tracer instances:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   # Production tracer
   production_tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="production-app",
       source="production"
   )
   
   # Experiments tracer
   experiments_tracer = HoneyHiveTracer.init(
       api_key="your-key",
       project="experiments",
       source="experimental"
   )
   
   # Note: Both use the same instrumentor, but you specify
   # which tracer to use with the @trace decorator

Pattern 1: Environment-Based Routing
------------------------------------

Route to different projects based on environment:

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.models import EventType
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   # Determine environment
   env = os.getenv("ENVIRONMENT", "development")
   
   # Create environment-specific tracer
   if env == "production":
       tracer = HoneyHiveTracer.init(
           project="myapp-production",
           source="production"
       )
   elif env == "staging":
       tracer = HoneyHiveTracer.init(
           project="myapp-staging",
           source="staging"
       )
   else:
       tracer = HoneyHiveTracer.init(
           project="myapp-development",
           source="development"
       )
   
   # Initialize instrumentor
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # Use the tracer in your functions
   @trace(tracer=tracer, event_type=EventType.chain)
   def generate_response(prompt: str) -> str:
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": prompt}]
       )
       return response.choices[0].message.content

Pattern 2: Feature-Based Routing
--------------------------------

Different features route to different projects:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.models import EventType
   import openai
   
   # Create tracers for different features
   customer_tracer = HoneyHiveTracer.init(
       project="customer-facing-api",
       source="production"
   )
   
   internal_tracer = HoneyHiveTracer.init(
       project="internal-tools",
       source="production"
   )
   
   experimental_tracer = HoneyHiveTracer.init(
       project="experiments",
       source="experimental"
   )
   
   # Customer-facing function
   @trace(tracer=customer_tracer, event_type=EventType.chain)
   def handle_customer_query(query: str) -> str:
       """Customer support queries - traced to customer-facing-api project."""
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "You are a customer support agent."},
               {"role": "user", "content": query}
           ]
       )
       return response.choices[0].message.content
   
   # Internal tool function
   @trace(tracer=internal_tracer, event_type=EventType.tool)
   def generate_internal_report(data: dict) -> str:
       """Internal reporting - traced to internal-tools project."""
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": "Generate an internal report."},
               {"role": "user", "content": str(data)}
           ]
       )
       return response.choices[0].message.content
   
   # Experimental feature
   @trace(tracer=experimental_tracer, event_type=EventType.chain)
   def test_new_prompt_strategy(input_text: str) -> str:
       """Experimental features - traced to experiments project."""
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4-turbo-preview",
           messages=[
               {"role": "system", "content": "Use new experimental prompt format."},
               {"role": "user", "content": input_text}
           ]
       )
       return response.choices[0].message.content

Pattern 3: Dynamic Tracer Selection
-----------------------------------

Select tracer at runtime based on request context:

.. code-block:: python

   from typing import Dict
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   import openai
   
   # Create tracer registry
   TRACERS: Dict[str, HoneyHiveTracer] = {
       "production": HoneyHiveTracer.init(
           project="production",
           source="production"
       ),
       "canary": HoneyHiveTracer.init(
           project="canary-deployment",
           source="canary"
       ),
       "shadow": HoneyHiveTracer.init(
           project="shadow-traffic",
           source="shadow"
       )
   }
   
   def get_tracer_for_request(request_headers: dict) -> HoneyHiveTracer:
       """Select tracer based on request routing."""
       # Check for canary header
       if request_headers.get("X-Canary-User") == "true":
           return TRACERS["canary"]
       
       # Check for shadow traffic
       if request_headers.get("X-Shadow-Traffic") == "true":
           return TRACERS["shadow"]
       
       # Default to production
       return TRACERS["production"]
   
   def process_request(user_input: str, request_headers: dict) -> str:
       """Process request with dynamic tracer selection."""
       # Select appropriate tracer
       selected_tracer = get_tracer_for_request(request_headers)
       
       # Use @trace with selected tracer
       @trace(tracer=selected_tracer, event_type=EventType.chain)
       def _process():
           enrich_span({
               "routing_decision": "canary" if selected_tracer == TRACERS["canary"] else "production",
               "user_input_length": len(user_input)
           })
           
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{"role": "user", "content": user_input}]
           )
           return response.choices[0].message.content
       
       return _process()

Pattern 4: A/B Testing with Multiple Tracers
--------------------------------------------

Track different experiment variants in separate projects:

.. code-block:: python

   import random
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   import openai
   
   # Create tracers for each variant
   control_tracer = HoneyHiveTracer.init(
       project="ab-test-control",
       source="experiment"
   )
   
   variant_a_tracer = HoneyHiveTracer.init(
       project="ab-test-variant-a",
       source="experiment"
   )
   
   variant_b_tracer = HoneyHiveTracer.init(
       project="ab-test-variant-b",
       source="experiment"
   )
   
   def assign_variant(user_id: str) -> str:
       """Assign user to experiment variant."""
       # Simple hash-based assignment (use your actual assignment logic)
       hash_val = hash(user_id) % 100
       
       if hash_val < 33:
           return "control"
       elif hash_val < 66:
           return "variant_a"
       else:
           return "variant_b"
   
   def generate_with_ab_test(user_id: str, prompt: str) -> str:
       """Generate response using A/B test variant."""
       variant = assign_variant(user_id)
       
       # Select tracer based on variant
       if variant == "control":
           tracer = control_tracer
           system_prompt = "You are a helpful assistant."  # Control
       elif variant == "variant_a":
           tracer = variant_a_tracer
           system_prompt = "You are a friendly and enthusiastic assistant!"  # Variant A
       else:
           tracer = variant_b_tracer
           system_prompt = "You are a professional and concise assistant."  # Variant B
       
       @trace(tracer=tracer, event_type=EventType.chain)
       def _generate():
           enrich_span({
               "user_id": user_id,
               "ab_variant": variant,
               "experiment": "prompt_tone_test"
           })
           
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[
                   {"role": "system", "content": system_prompt},
                   {"role": "user", "content": prompt}
               ]
           )
           return response.choices[0].message.content
       
       return _generate()

Configuration Management
------------------------

Centralize tracer configuration in a config file:

**config.yaml:**

.. code-block:: yaml

   tracers:
     production:
       project: "myapp-production"
       source: "production"
       api_key: "${HH_API_KEY}"
     
     staging:
       project: "myapp-staging"
       source: "staging"
       api_key: "${HH_API_KEY}"
     
     experiments:
       project: "experiments"
       source: "experimental"
       api_key: "${HH_API_KEY}"

**Load configuration:**

.. code-block:: python

   import yaml
   import os
   from honeyhive import HoneyHiveTracer
   
   def load_tracers(config_path: str) -> dict:
       """Load tracers from config file."""
       with open(config_path) as f:
           config = yaml.safe_load(f)
       
       tracers = {}
       for name, tracer_config in config["tracers"].items():
           tracers[name] = HoneyHiveTracer.init(
               api_key=os.getenv("HH_API_KEY"),
               project=tracer_config["project"],
               source=tracer_config["source"]
           )
       
       return tracers
   
   # Usage
   tracers = load_tracers("config.yaml")
   prod_tracer = tracers["production"]
   exp_tracer = tracers["experiments"]

Best Practices
--------------

**DO:**

- Use consistent naming conventions (``{app}-{environment}``)
- Document which tracer is used where
- Use environment variables for API keys
- Keep tracer instances in a central registry
- Use the ``@trace`` decorator to specify tracers

**DON'T:**

- Create too many tracers (it's OK to use metadata to differentiate)
- Hard-code API keys
- Mix tracer instances randomly without clear routing logic
- Create new tracers per request (create once, reuse many times)

Performance Considerations
--------------------------

Multiple tracers have minimal overhead:

- Each tracer has its own span processor
- Traces are batched independently per tracer
- Memory overhead: ~100KB per tracer instance
- Network overhead: Batched, async export per tracer

**Recommendation:** 2-5 tracers per application is typical and performant.

Complete Example Application
----------------------------

Here's a complete Flask application with multiple tracers:

.. code-block:: python

   """
   multi_tracer_app.py - Flask app with multi-instance tracers
   """
   
   from flask import Flask, request, jsonify
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import os
   
   app = Flask(__name__)
   
   # Initialize tracers
   API_TRACER = HoneyHiveTracer.init(
       project="customer-api",
       source=os.getenv("ENVIRONMENT", "production")
   )
   
   ADMIN_TRACER = HoneyHiveTracer.init(
       project="admin-tools",
       source=os.getenv("ENVIRONMENT", "production")
   )
   
   # Initialize instrumentor (works with both tracers)
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=API_TRACER.provider)
   
   @app.route("/api/chat", methods=["POST"])
   def chat_endpoint():
       """Customer API endpoint - uses API_TRACER."""
       @trace(tracer=API_TRACER, event_type=EventType.chain)
       def _handle_chat():
           data = request.json
           message = data.get("message")
           user_id = data.get("user_id")
           
           enrich_span({
               "endpoint": "/api/chat",
               "user_id": user_id,
               "request_id": request.headers.get("X-Request-ID")
           })
           
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[{"role": "user", "content": message}]
           )
           
           return response.choices[0].message.content
       
       result = _handle_chat()
       return jsonify({"response": result})
   
   @app.route("/admin/analyze", methods=["POST"])
   def admin_analyze():
       """Admin endpoint - uses ADMIN_TRACER."""
       @trace(tracer=ADMIN_TRACER, event_type=EventType.tool)
       def _handle_analyze():
           data = request.json
           
           enrich_span({
               "endpoint": "/admin/analyze",
               "admin_user": request.headers.get("X-Admin-User"),
               "request_id": request.headers.get("X-Request-ID")
           })
           
           client = openai.OpenAI()
           response = client.chat.completions.create(
               model="gpt-4",
               messages=[{"role": "user", "content": f"Analyze: {data}"}]
           )
           
           return response.choices[0].message.content
       
       result = _handle_analyze()
       return jsonify({"analysis": result})
   
   if __name__ == "__main__":
       app.run(debug=True)

Viewing Traces by Project
-------------------------

In HoneyHive dashboard:

1. Use the project selector to switch between projects
2. Each project shows only its traces
3. Compare metrics across projects to evaluate experiments
4. Export data per-project for analysis

Next Steps
----------

- :doc:`/how-to/advanced-tracing/custom-spans` - Create custom spans with tracers
- :doc:`/how-to/deployment/production` - Production deployment patterns
- :doc:`/how-to/llm-application-patterns` - Application architecture patterns
- :doc:`03-enable-span-enrichment` - Add metadata to traces

**Key Takeaway:** Multiple tracers let you organize traces logically by project, environment, or experiment variant while keeping your codebase clean and maintainable. ✨

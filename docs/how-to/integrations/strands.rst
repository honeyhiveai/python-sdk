AWS Strands Integration
=======================

AWS Strands is Amazon's model-driven AI agent framework for building conversational assistants and autonomous workflows. This guide shows how to integrate HoneyHive with AWS Strands to capture comprehensive traces of your agent executions.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

What is AWS Strands?
~~~~~~~~~~~~~~~~~~~~

AWS Strands is an AI agent framework that:

- **Works with AWS Bedrock models** - Supports Claude, Titan, Nova, and other Bedrock models
- **Built-in OpenTelemetry** - Native tracing support with GenAI semantic conventions
- **Autonomous workflows** - Multi-agent orchestration with Swarms and Graphs
- **Tool execution** - Function calling with automatic tracing
- **Streaming support** - Token-by-token response streaming

Integration Approach
~~~~~~~~~~~~~~~~~~~~

HoneyHive integrates with AWS Strands using **automatic OpenTelemetry provider setup**.

**Key Difference from Other Integrations:**

Unlike OpenAI or Anthropic (which require instrumentors like OpenInference or Traceloop), **AWS Strands has built-in OpenTelemetry tracing**. This means:

- ✅ **NO instrumentor needed** - Strands instruments its own LLM calls
- ✅ **NO manual provider setup** - ``HoneyHiveTracer.init()`` handles it automatically
- ✅ **Built-in GenAI conventions** - All model calls automatically traced
- ✅ **Don't use OpenInference/Traceloop** - Would create duplicate spans
- ✅ **Zero modifications to Strands code** - Works with Strands as-is
- ✅ **Automatic tracing** - All agent activity captured automatically
- ✅ **Comprehensive data** - Token usage, latency, tool calls, message history
- ✅ **Multi-agent support** - Swarms and Graphs fully traced
- ✅ **Standard OTel** - Uses OpenTelemetry best practices

**How It Works:**

1. Call ``HoneyHiveTracer.init()`` - automatically sets up global TracerProvider
2. Strands automatically uses it for all its built-in tracing
3. All LLM calls, agent actions, and tool executions are traced

Complete Example
~~~~~~~~~~~~~~~~

**See the full code:** `strands_integration.py <https://github.com/honeyhiveai/python-sdk/blob/main/examples/integrations/strands_integration.py>`_

A comprehensive working example is available in the repository at ``examples/integrations/strands_integration.py``:

- ✅ All 8 integration patterns shown below
- ✅ Basic agent invocation, tool execution, streaming responses
- ✅ Custom trace attributes, structured outputs with Pydantic
- ✅ Swarm multi-agent collaboration, graph workflows with parallel processing
- ✅ Copy-paste ready code for quick start

What Gets Traced
~~~~~~~~~~~~~~~~

HoneyHive automatically captures:

1. **Span Hierarchy:**

   - Root: ``invoke_agent {agent_name}``
   - Children: Event loop cycles
   - Grandchildren: Model calls and tool executions

2. **Attributes:**

   - Agent name, model ID, tools list
   - Token usage (prompt, completion, cache hits)
   - Latency metrics (TTFT, total duration)
   - Tool names, IDs, status

3. **Events:**

   - Complete message history (user, assistant, tool)
   - Finish reasons
   - Content blocks (text, tool_use, tool_result)

4. **Metadata:**

   - Event loop cycle IDs
   - Parent-child relationships
   - Timestamps

Prerequisites
-------------

Install Dependencies
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install honeyhive strands boto3

AWS Credentials Setup
~~~~~~~~~~~~~~~~~~~~~

AWS Strands uses AWS Bedrock, so you need valid AWS credentials:

**Option 1: Environment Variables**

.. code-block:: bash

   export AWS_ACCESS_KEY_ID=your-access-key
   export AWS_SECRET_ACCESS_KEY=your-secret-key
   export AWS_REGION=us-west-2

**Option 2: AWS SSO / CLI Profile**

.. code-block:: bash

   # Configure AWS CLI profile
   aws configure sso
   
   # Use profile
   export AWS_PROFILE=your-profile
   export AWS_DEFAULT_REGION=us-west-2

**Option 3: IAM Role (EC2, Lambda, ECS)**

If running on AWS infrastructure, use IAM roles - no credentials needed!

Model Access
~~~~~~~~~~~~

AWS Bedrock models are available by default in your AWS account. For Anthropic Claude models, first-time customers must submit use case details (done automatically in the AWS Console when you first select a model) and agree to the EULA when first invoking the model.

**No manual access request needed** - simply start using the models!

Common model IDs:

- ``anthropic.claude-haiku-4-5-20251001-v1:0`` - Claude Haiku 4.5 (latest, fastest)
- ``anthropic.claude-sonnet-4-5-20250929-v1:0`` - Claude Sonnet 4.5 (latest, balanced)
- ``us.amazon.nova-pro-v1:0`` - Amazon Nova Pro
- ``us.amazon.nova-lite-v1:0`` - Amazon Nova Lite

**Note:** Older Claude 3 models from early 2024 are being deprecated. Use Claude 4.5 series for the latest features and long-term support.

Basic Integration
-----------------

Minimal Setup (3 Lines of Code)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ============= HONEYHIVE INTEGRATION =============
   from honeyhive import HoneyHiveTracer
   import os
   
   # Initialize HoneyHive tracer - automatic global provider setup
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project="strands-demo",
   )
   # ==================================================
   
   # ============= YOUR STRANDS CODE ==================
   from strands import Agent
   from strands.models import BedrockModel
   
   # Use Strands normally - tracing is automatic!
   agent = Agent(
       name="BasicAgent",
       model=BedrockModel(model_id="anthropic.claude-haiku-4-5-20251001-v1:0"),
       system_prompt="You are a helpful assistant."
   )
   
   result = agent("What is 2+2?")
   print(result)  # "2+2 equals 4"
   # ==================================================

**That's it!** All agent activity is now automatically traced to HoneyHive.


Basic Agent Example
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ============= HONEYHIVE INTEGRATION =============
   from honeyhive import HoneyHiveTracer
   import os
   
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project="strands-agents",
       session_name="basic-agent-demo"
   )
   # ==================================================
   
   # ============= YOUR STRANDS CODE ==================
   from strands import Agent
   from strands.models import BedrockModel
   
   # Create agent
   agent = Agent(
       name="ResearchAgent",
       model=BedrockModel(model_id="anthropic.claude-haiku-4-5-20251001-v1:0"),
       system_prompt="You are a research assistant that provides concise, factual answers."
   )
   
   # Use agent
   result = agent("What is the capital of France?")
   print(f"Answer: {result}")
   
   # Check HoneyHive dashboard for traces!

Tool Execution
--------------

Agents with Tools
~~~~~~~~~~~~~~~~~

AWS Strands automatically traces tool execution:

.. code-block:: python

   from strands import Agent, tool
   from strands.models import BedrockModel
   
   # Define a tool
   @tool
   def calculator(operation: str, a: float, b: float) -> float:
       """Perform basic math operations: add, subtract, multiply, divide."""
       if operation == "add":
           return a + b
       elif operation == "multiply":
           return a * b
       # ... other operations
   
   # Create agent with tool
   agent = Agent(
       name="MathAgent",
       model=BedrockModel(model_id="anthropic.claude-haiku-4-5-20251001-v1:0"),
       tools=[calculator],
       system_prompt="You are a math assistant. Use the calculator tool."
   )
   
   # Tool execution is automatically traced
   result = agent("What is 15 times 23?")
   print(result)  # "345"

**What Gets Traced:**

- Tool definition and parameters
- Tool invocation with input values
- Tool execution time
- Tool output/result
- Agent's use of tool results

Advanced Features
-----------------

Streaming Responses
~~~~~~~~~~~~~~~~~~~

Stream agent responses token-by-token:

.. code-block:: python

   import asyncio
   
   async def stream_agent():
       agent = Agent(
           name="StreamingAgent",
           model=BedrockModel(
               model_id="anthropic.claude-haiku-4-5-20251001-v1:0",
               streaming=True
           ),
           system_prompt="You are a storyteller."
       )
       
       # Stream response
       async for chunk in agent.stream_async("Tell me a short story"):
           print(chunk, end="", flush=True)
       print()
   
   asyncio.run(stream_agent())

**Tracing with Streaming:**

- Spans still captured normally
- TTFT (Time To First Token) metrics included
- Full response captured in span events

Structured Outputs
~~~~~~~~~~~~~~~~~~

Get type-safe responses with Pydantic:

.. code-block:: python

   from pydantic import BaseModel
   
   class Summary(BaseModel):
       """Summary response model."""
       text: str
       key_points: list[str]
   
   agent = Agent(
       name="SummarizerAgent",
       model=BedrockModel(model_id="anthropic.claude-haiku-4-5-20251001-v1:0"),
       system_prompt="You are a summarization assistant."
   )
   
   # Request structured output
   result = agent.structured_output(
       Summary,
       "Summarize this text: [your text here]"
   )
   
   print(result.text)
   print(result.key_points)

Custom Trace Attributes
~~~~~~~~~~~~~~~~~~~~~~~

Add custom attributes to agent spans:

.. code-block:: python

   agent = Agent(
       name="CustomAgent",
       model=BedrockModel(model_id="anthropic.claude-haiku-4-5-20251001-v1:0"),
       trace_attributes={
           "user_id": "user_123",
           "environment": "production",
           "version": "1.2.0"
       },
       system_prompt="You are a helpful assistant."
   )
   
   # Custom attributes appear on all agent spans
   result = agent("Hello!")

Multi-Agent Workflows
---------------------

Swarm Collaboration
~~~~~~~~~~~~~~~~~~~

Multiple agents working together with handoffs:

.. code-block:: python

   from strands.multiagent import Swarm
   
   # Create specialized agents
   researcher = Agent(
       name="researcher",
       model=BedrockModel(model_id="anthropic.claude-haiku-4-5-20251001-v1:0"),
       system_prompt="You are a research specialist. Gather info and hand off to coder."
   )
   
   coder = Agent(
       name="coder",
       model=BedrockModel(model_id="anthropic.claude-haiku-4-5-20251001-v1:0"),
       tools=[calculator],
       system_prompt="You are a coding specialist. Implement solutions."
   )
   
   reviewer = Agent(
       name="reviewer",
       model=BedrockModel(model_id="anthropic.claude-haiku-4-5-20251001-v1:0"),
       system_prompt="You are a review specialist. Review and provide feedback."
   )
   
   # Create swarm
   swarm = Swarm(
       [researcher, coder, reviewer],
       entry_point=researcher,
       max_handoffs=10
   )
   
   # Execute task
   result = swarm("Calculate compound interest for $1000 at 5% over 3 years")
   
   print(f"Status: {result.status}")
   print(f"Iterations: {result.execution_count}")
   print(f"Time: {result.execution_time}ms")

**What Gets Traced:**

- Each agent invocation in the swarm
- Handoff messages between agents
- Execution order and timing
- Tool calls by each agent
- Final results from each agent

Graph Workflows
~~~~~~~~~~~~~~~

Complex workflows with parallel processing:

.. code-block:: python

   from strands.multiagent import GraphBuilder
   
   # Create specialized agents
   researcher = Agent(name="researcher", ...)
   analyst = Agent(name="analyst", ...)
   fact_checker = Agent(name="fact_checker", ...)
   writer = Agent(name="writer", ...)
   
   # Build graph
   builder = GraphBuilder()
   
   # Add nodes
   builder.add_node(researcher, "research")
   builder.add_node(analyst, "analysis")
   builder.add_node(fact_checker, "fact_check")
   builder.add_node(writer, "write")
   
   # Define dependencies (parallel processing)
   builder.add_edge("research", "analysis")      # research → analysis
   builder.add_edge("research", "fact_check")    # research → fact_check
   builder.add_edge("analysis", "write")         # analysis → write
   builder.add_edge("fact_check", "write")       # fact_check → write
   
   builder.set_entry_point("research")
   
   # Build and execute
   graph = builder.build()
   result = graph("Research renewable energy and write a report")
   
   print(f"Status: {result.status}")
   print(f"Completed Nodes: {result.completed_nodes}/{result.total_nodes}")

**What Gets Traced:**

- Graph structure and dependencies
- Parallel execution paths
- Node execution order
- Each agent's contribution
- Aggregation at convergence points

Integration with evaluate()
---------------------------

Using Strands with HoneyHive's evaluation framework:

Basic Evaluation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.experiments import evaluate
   from strands import Agent
   from strands.models import BedrockModel
   import os
   
   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project=os.getenv("HH_PROJECT")
   )
   
   # Define your agent function
   @trace(event_name="summary_agent", event_type="tool", tracer=tracer)
   def invoke_summary_agent(**kwargs):
       """Agent function for evaluation."""
       agent = Agent(
           name="SummarizerAgent",
           model=BedrockModel(
               model_id="anthropic.claude-haiku-4-5-20251001-v1:0"
           ),
           system_prompt="You are a summarization assistant."
       )
       
       context = kwargs.get("context", "")
       
       # Enrich span with metadata using instance method
       tracer.enrich_span(metadata={
           "model": "claude-haiku-4.5",
           "context_length": len(context)
       })
       
       result = agent(f"Summarize this: {context}")
       return {"answer": result}
   
   # Create dataset
   dataset = [
       {
           "inputs": {
               "context": "Machine learning is a subset of AI..."
           },
           "ground_truth": {
               "result": "Expected summary here"
           }
       },
       # ... more examples
   ]
   
   # Run evaluation
   @trace(event_name="evaluation_function", event_type="chain", tracer=tracer)
   def evaluation_function(datapoint):
       inputs = datapoint.get("inputs", {})
       return invoke_summary_agent(**inputs)
   
   result = evaluate(
       function=evaluation_function,
       dataset=dataset,
       api_key=os.getenv("HH_API_KEY"),
       project=os.getenv("HH_PROJECT"),
       name="strands-evaluation-run",
       verbose=True
   )
   
   print(f"Run ID: {result.run_id}")
   print(f"Status: {result.status}")

With Custom Evaluators
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive.experiments import evaluator
   
   @evaluator
   def summary_quality(outputs, inputs, ground_truth):
       """Evaluate summary quality."""
       answer = outputs.get("answer", "")
       expected = ground_truth.get("result", "")
       
       # Simple length-based quality check
       length_ratio = len(answer) / len(expected) if expected else 0
       quality_score = 1.0 if 0.8 <= length_ratio <= 1.2 else 0.5
       
       return {
           "summary_quality": quality_score,
           "length_ratio": length_ratio
       }
   
   # Run with evaluator
   result = evaluate(
       function=evaluation_function,
       dataset=dataset,
       evaluators=[summary_quality],
       api_key=os.environ["HH_API_KEY"],
       project=os.environ["HH_PROJECT"],
       name="strands-with-evaluators"
   )

Multi-Turn Conversations
~~~~~~~~~~~~~~~~~~~~~~~~

Evaluate agents across multiple conversation turns:

.. code-block:: python

   tracer = HoneyHiveTracer.init(api_key=os.getenv("HH_API_KEY"), project="my-project")
   
   @trace(event_name="multi_turn_agent", event_type="tool", tracer=tracer)
   def multi_turn_conversation(**kwargs):
       """Agent that maintains conversation context."""
       agent = Agent(
           name="ConversationAgent",
           model=BedrockModel(
               model_id="anthropic.claude-haiku-4-5-20251001-v1:0"
           ),
           system_prompt="You are a helpful conversational assistant."
       )
       
       messages = kwargs.get("messages", [])
       results = []
       
       for msg in messages:
           result = agent(msg)
           results.append(result)
           
           # Enrich with per-turn metrics using instance method
           tracer.enrich_span(metrics={
               "turn_number": len(results),
               "response_length": len(result)
           })
       
       return {"answers": results}
   
   # Dataset with conversation flows
   dataset = [
       {
           "inputs": {
               "messages": [
                   "What is Python?",
                   "What are its main uses?",
                   "Is it good for beginners?"
               ]
           },
           "ground_truth": {
               "answer_count": 3,
               "covers_basics": True
           }
       }
   ]

Span Enrichment
---------------

Adding Custom Metadata
~~~~~~~~~~~~~~~~~~~~~~

Enrich spans with additional context:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(api_key=os.getenv("HH_API_KEY"), project="my-project")
   
   @trace(event_name="enriched_agent", event_type="tool", tracer=tracer)
   def enriched_agent_call(**kwargs):
       agent = Agent(
           name="EnrichedAgent",
           model=BedrockModel(
               model_id="anthropic.claude-haiku-4-5-20251001-v1:0"
           )
       )
       
       query = kwargs.get("query", "")
       
       # Add metadata before execution (instance method pattern)
       tracer.enrich_span(metadata={
           "query_type": "factual",
           "user_id": kwargs.get("user_id"),
           "priority": "high"
       })
       
       result = agent(query)
       
       # Add metrics after execution (instance method pattern)
       tracer.enrich_span(metrics={
           "response_length": len(result),
           "query_length": len(query)
       })
       
       return result

Custom Metrics
~~~~~~~~~~~~~~

Track custom performance metrics:

.. code-block:: python

   import time
   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(api_key=os.getenv("HH_API_KEY"), project="my-project")
   
   @trace(event_name="timed_agent", event_type="tool", tracer=tracer)
   def timed_agent_call(**kwargs):
       agent = Agent(...)
       
       start_time = time.time()
       result = agent(kwargs["query"])
       duration = time.time() - start_time
       
       # Add custom timing metrics (instance method pattern)
       tracer.enrich_span(metrics={
           "custom_duration_ms": duration * 1000,
           "tokens_per_second": len(result.split()) / duration
       })
       
       return result

What Gets Traced
----------------

Automatic Span Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~

HoneyHive automatically captures these attributes from Strands:

**Agent-Level:**

- ``gen_ai.agent.name`` - Agent name
- ``gen_ai.request.model`` - Bedrock model ID
- ``gen_ai.agent.tools`` - List of available tools

**Model Calls:**

- ``gen_ai.usage.prompt_tokens`` - Input tokens
- ``gen_ai.usage.completion_tokens`` - Output tokens
- ``gen_ai.usage.total_tokens`` - Total tokens
- ``gen_ai.usage.cached_tokens`` - Cache hits (if supported)
- ``gen_ai.server.time_to_first_token`` - TTFT in milliseconds

**Tool Execution:**

- ``gen_ai.tool.name`` - Tool function name
- ``gen_ai.tool.id`` - Tool invocation ID
- ``gen_ai.tool.status`` - Success/failure status

**Event Loop:**

- ``gen_ai.event_loop.cycle_id`` - Cycle number
- ``gen_ai.event_loop.status`` - Cycle status

Span Events
~~~~~~~~~~~

Complete message history captured as span events:

- User messages with content
- Assistant responses with reasoning
- Tool calls with parameters
- Tool results with outputs
- Finish reasons (stop, tool_use, etc.)

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Issue: "No module named 'strands'"**

.. code-block:: bash

   pip install strands

**Issue: "Duplicate spans in HoneyHive"**

This happens if you accidentally enable LLM instrumentors (OpenInference/Traceloop):

.. code-block:: python

   # ❌ DON'T DO THIS - Strands has built-in tracing
   from openinference.instrumentation.openai import OpenAIInstrumentor
   OpenAIInstrumentor().instrument()  # Will create duplicate spans!
   
   # ✅ DO THIS - Just initialize HoneyHive
   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(...)
   # That's it - automatic provider setup, Strands handles the rest!

**Issue: "Unable to locate credentials"**

Check AWS credentials are configured:

.. code-block:: bash

   aws configure list
   # or
   echo $AWS_ACCESS_KEY_ID

**Issue: "Access Denied" when calling Bedrock**

1. Verify your AWS credentials have Bedrock permissions
2. Check model access in AWS Console → Bedrock → Model access
3. Ensure you're in a supported region

**Issue: "Model not found"**

Use correct Bedrock model IDs (not OpenAI model names):

.. code-block:: python

   # ✅ Correct - Bedrock model ID
   model = BedrockModel(model_id="anthropic.claude-haiku-4-5-20251001-v1:0")
   
   # ❌ Wrong - OpenAI model name
   model = BedrockModel(model_id="gpt-4")

**Issue: Traces not appearing in HoneyHive**

1. Verify ``HH_API_KEY`` is set correctly
2. Check project name matches your HoneyHive project
3. Ensure ``HoneyHiveTracer.init()`` is called BEFORE creating agents
4. Look for error messages in console output

Debugging Traces
~~~~~~~~~~~~~~~~

Enable verbose logging:

.. code-block:: python

   import logging
   
   # Enable HoneyHive debug logging
   logging.basicConfig(level=logging.DEBUG)
   
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project="strands-debug",
       verbose=True  # Enable verbose mode
   )

Check Session ID
~~~~~~~~~~~~~~~~

Print session ID for manual verification:

.. code-block:: python

   tracer = HoneyHiveTracer.init(...)
   
   print(f"Session ID: {tracer.session_id}")
   print(f"Project: {tracer.project}")
   
   # Use agents...
   
   # Check this session in HoneyHive dashboard

Best Practices
--------------

1. **Initialize Tracer Early**

   Always call ``HoneyHiveTracer.init()`` before creating agents (automatic provider setup):

   .. code-block:: python

      # ✅ Correct order
      tracer = HoneyHiveTracer.init(...)  # Automatic global provider setup
      agent = Agent(...)  # Now traced
      
      # ❌ Wrong order
      agent = Agent(...)  # Not traced
      tracer = HoneyHiveTracer.init(...)  # Too late!

2. **Don't Use LLM Instrumentors**

   AWS Strands has built-in tracing - don't add instrumentors:

   .. code-block:: python

      # ❌ DON'T DO THIS
      from openinference.instrumentation.openai import OpenAIInstrumentor
      OpenAIInstrumentor().instrument()  # Creates duplicate spans!
      
      # ✅ DO THIS - Strands instruments itself
      tracer = HoneyHiveTracer.init(...)
      # Strands' built-in tracing handles everything (no manual provider setup needed)

3. **Use Meaningful Agent Names**

   Agent names appear in traces - make them descriptive:

   .. code-block:: python

      # ✅ Good - clear purpose
      agent = Agent(name="customer_support_bot", ...)
      agent = Agent(name="code_reviewer", ...)
      
      # ❌ Bad - unclear
      agent = Agent(name="agent1", ...)
      agent = Agent(name="a", ...)

4. **Add Custom Metadata**

   Enrich spans with business context:

   .. code-block:: python

      tracer.enrich_span(metadata={
          "user_id": user_id,
          "conversation_id": conv_id,
          "intent": detected_intent
      })

5. **Use Structured Outputs**

   Type-safe responses are easier to trace and debug:

   .. code-block:: python

      from pydantic import BaseModel
      
      class Response(BaseModel):
          answer: str
          confidence: float
      
      result = agent.structured_output(Response, query)

6. **Monitor Token Usage**

   Track costs by checking token metrics:

   .. code-block:: python

      # Token usage automatically captured in:
      # - gen_ai.usage.prompt_tokens
      # - gen_ai.usage.completion_tokens
      # 
      # View in HoneyHive dashboard under metrics

Next Steps
----------

- :doc:`/how-to/evaluation/running-experiments` - Run evaluations on your agents
- :doc:`/how-to/advanced-tracing/span-enrichment` - Add custom metadata
- :doc:`/reference/api/tracer` - Full tracer API reference
- `AWS Strands Documentation <https://github.com/strands-agents/sdk-python>`_ - Learn more about Strands



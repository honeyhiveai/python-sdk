Integrate with OpenAI
=====================

.. note::
   **Problem-solving guide for OpenAI integration**
   
   This guide helps you solve specific problems when integrating HoneyHive with OpenAI, from basic setup to advanced patterns.

This guide covers common patterns and solutions for OpenAI integration with HoneyHive's BYOI architecture.

Quick Setup
-----------

**Problem**: I want to add HoneyHive tracing to my existing OpenAI code without changes.

**Solution**:

.. code-block:: bash

   # Install required packages
   pip install honeyhive openinference-instrumentation-openai openai

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   # Initialize HoneyHive with OpenAI instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       project="openai-integration",
       instrumentors=[OpenAIInstrumentor()]
   )
   
   # Use OpenAI exactly as before - automatic tracing!
   client = openai.OpenAI(api_key="your-openai-key")
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )

Environment Variables
---------------------

**Problem**: I need to manage API keys securely across environments.

**Solution**:

.. code-block:: bash

   # .env file
   HH_API_KEY=hh_your_honeyhive_key_here
   HH_PROJECT=openai-production
   HH_SOURCE=production
   OPENAI_API_KEY=sk-your_openai_key_here

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   # Automatic environment variable usage
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )
   
   # OpenAI client uses OPENAI_API_KEY automatically
   client = openai.OpenAI()

Adding Business Context
-----------------------

**Problem**: I want to add custom metadata to my OpenAI traces.

**Solution**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type=EventType.model)
   def handle_customer_query(customer_id: str, query: str, priority: str = "normal"):
       """Handle customer support query with business context."""
       
       # Add business context to the trace
       enrich_span({
           "customer.id": customer_id,
           "support.priority": priority,
           "support.category": classify_query(query),
           "support.agent": "ai_assistant"
       })
       
       client = openai.OpenAI()
       
       # This OpenAI call inherits the business context
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": f"You are a {priority} priority support agent."},
               {"role": "user", "content": query}
           ]
       )
       
       answer = response.choices[0].message.content
       
       # Add response metadata
       enrich_span({
           "support.response_length": len(answer),
           "support.tokens_used": response.usage.total_tokens,
           "support.model": "gpt-4"
       })
       
       return answer
   
   def classify_query(query: str) -> str:
       """Simple query classification."""
       if any(word in query.lower() for word in ["refund", "money", "payment"]):
           return "billing"
       elif any(word in query.lower() for word in ["bug", "error", "broken"]):
           return "technical"
       return "general"

Error Handling
--------------

**Problem**: I need to handle OpenAI API errors gracefully while maintaining tracing.

**Solution**:

.. code-block:: python

   import openai
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import time
   import random
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type="openai_with_retry")
   def robust_openai_call(prompt: str, max_retries: int = 3) -> str:
       """OpenAI call with retry logic and error handling."""
       
       client = openai.OpenAI()
       last_error = None
       
       for attempt in range(max_retries):
           try:
               enrich_span({
                   "retry.attempt": attempt + 1,
                   "retry.max_attempts": max_retries
               })
               
               response = client.chat.completions.create(
                   model="gpt-3.5-turbo",
                   messages=[{"role": "user", "content": prompt}],
                   timeout=30.0
               )
               
               # Success - add metrics
               enrich_span({
                   "success": True,
                   "attempts_needed": attempt + 1,
                   "final_tokens": response.usage.total_tokens
               })
               
               return response.choices[0].message.content
               
           except openai.RateLimitError as e:
               last_error = e
               wait_time = (2 ** attempt) + random.uniform(0, 1)
               
               enrich_span({
                   "error.type": "rate_limit",
                   "error.attempt": attempt + 1,
                   "retry.wait_time": wait_time
               })
               
               if attempt < max_retries - 1:
                   time.sleep(wait_time)
               
           except openai.APIError as e:
               last_error = e
               enrich_span({
                   "error.type": "api_error",
                   "error.message": str(e),
                   "error.attempt": attempt + 1
               })
               
               # Don't retry on API errors
               break
               
           except Exception as e:
               last_error = e
               enrich_span({
                   "error.type": "unexpected",
                   "error.message": str(e),
                   "error.attempt": attempt + 1
               })
       
       # All retries failed
       enrich_span({
           "success": False,
           "total_attempts": max_retries,
           "final_error": str(last_error)
       })
       
       raise last_error

Streaming Responses
-------------------

**Problem**: I need to trace OpenAI streaming responses.

**Solution**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import time
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type="openai_streaming")
   def stream_openai_response(prompt: str) -> str:
       """Handle OpenAI streaming responses with tracing."""
       
       client = openai.OpenAI()
       start_time = time.time()
       
       enrich_span({
           "streaming.enabled": True,
           "prompt.length": len(prompt)
       })
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": prompt}],
           stream=True
       )
       
       chunks = []
       chunk_count = 0
       first_chunk_time = None
       
       for chunk in response:
           chunk_count += 1
           
           if chunk.choices[0].delta.content:
               content = chunk.choices[0].delta.content
               chunks.append(content)
               
               if first_chunk_time is None:
                   first_chunk_time = time.time()
                   enrich_span({
                       "streaming.time_to_first_chunk": first_chunk_time - start_time
                   })
       
       full_response = ''.join(chunks)
       total_time = time.time() - start_time
       
       enrich_span({
           "streaming.chunk_count": chunk_count,
           "streaming.total_time": total_time,
           "response.length": len(full_response),
           "streaming.chars_per_second": len(full_response) / total_time if total_time > 0 else 0
       })
       
       return full_response

Function Calling
----------------

**Problem**: I want to trace OpenAI function calling with proper metadata.

**Solution**:

.. code-block:: python

   import json
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )
   
   def get_weather(location: str) -> str:
       """Mock weather function."""
       return f"The weather in {location} is sunny and 72°F"
   
   def send_email(to: str, subject: str, body: str) -> str:
       """Mock email function."""
       return f"Email sent to {to} with subject '{subject}'"
   
   # Define available functions
   functions = [
       {
           "name": "get_weather",
           "description": "Get current weather for a location",
           "parameters": {
               "type": "object",
               "properties": {
                   "location": {"type": "string", "description": "City name"}
               },
               "required": ["location"]
           }
       },
       {
           "name": "send_email",
           "description": "Send an email",
           "parameters": {
               "type": "object",
               "properties": {
                   "to": {"type": "string"},
                   "subject": {"type": "string"},
                   "body": {"type": "string"}
               },
               "required": ["to", "subject", "body"]
           }
       }
   ]
   
   @trace(tracer=tracer, event_type="openai_function_calling")
   def handle_user_request(user_message: str) -> str:
       """Handle user request with function calling capability."""
       
       client = openai.OpenAI()
       
       enrich_span({
           "functions.available_count": len(functions),
           "functions.names": [f["name"] for f in functions]
       })
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": user_message}],
           functions=functions,
           function_call="auto"
       )
       
       message = response.choices[0].message
       
       if message.function_call:
           # Function was called
           function_name = message.function_call.name
           function_args = json.loads(message.function_call.arguments)
           
           enrich_span({
               "function_call.name": function_name,
               "function_call.arguments": function_args,
               "function_call.triggered": True
           })
           
           # Execute the function
           if function_name == "get_weather":
               function_result = get_weather(**function_args)
           elif function_name == "send_email":
               function_result = send_email(**function_args)
           else:
               function_result = f"Unknown function: {function_name}"
           
           enrich_span({
               "function_call.result": function_result
           })
           
           # Get final response with function result
           final_response = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=[
                   {"role": "user", "content": user_message},
                   {"role": "assistant", "content": None, "function_call": message.function_call},
                   {"role": "function", "name": function_name, "content": function_result}
               ]
           )
           
           return final_response.choices[0].message.content
       else:
           # No function call needed
           enrich_span({
               "function_call.triggered": False
           })
           return message.content

Embeddings Integration
----------------------

**Problem**: I want to trace OpenAI embeddings creation and usage.

**Solution**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import numpy as np
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type="create_embeddings")
   def create_document_embeddings(documents: list[str]) -> list[list[float]]:
       """Create embeddings for a list of documents."""
       
       client = openai.OpenAI()
       
       enrich_span({
           "embeddings.document_count": len(documents),
           "embeddings.total_characters": sum(len(doc) for doc in documents),
           "embeddings.model": "text-embedding-3-small"
       })
       
       response = client.embeddings.create(
           model="text-embedding-3-small",
           input=documents
       )
       
       embeddings = [embedding.embedding for embedding in response.data]
       
       enrich_span({
           "embeddings.dimension": len(embeddings[0]) if embeddings else 0,
           "embeddings.tokens_used": response.usage.total_tokens
       })
       
       return embeddings
   
   @trace(tracer=tracer, event_type="similarity_search")
   def find_similar_documents(query: str, document_embeddings: list, documents: list[str], top_k: int = 5) -> list[tuple]:
       """Find most similar documents to a query."""
       
       client = openai.OpenAI()
       
       # Get query embedding
       query_response = client.embeddings.create(
           model="text-embedding-3-small",
           input=[query]
       )
       
       query_embedding = query_response.data[0].embedding
       
       enrich_span({
           "similarity.query_length": len(query),
           "similarity.corpus_size": len(documents),
           "similarity.top_k": top_k
       })
       
       # Calculate similarities
       similarities = []
       for i, doc_embedding in enumerate(document_embeddings):
           similarity = np.dot(query_embedding, doc_embedding)
           similarities.append((similarity, i, documents[i]))
       
       # Sort by similarity
       similarities.sort(reverse=True, key=lambda x: x[0])
       top_results = similarities[:top_k]
       
       enrich_span({
           "similarity.best_score": top_results[0][0] if top_results else 0,
           "similarity.worst_score": top_results[-1][0] if top_results else 0,
           "similarity.results_count": len(top_results)
       })
       
       return top_results

Cost Tracking
-------------

**Problem**: I need to track and optimize OpenAI API costs.

**Solution**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )
   
   # OpenAI pricing (as of 2024 - check current pricing)
   PRICING = {
       "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
       "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
       "text-embedding-3-small": {"input": 0.00002, "output": 0}
   }
   
   def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
       """Calculate API call cost."""
       if model not in PRICING:
           return 0.0
       
       pricing = PRICING[model]
       input_cost = (prompt_tokens / 1000) * pricing["input"]
       output_cost = (completion_tokens / 1000) * pricing["output"]
       
       return input_cost + output_cost
   
   @trace(tracer=tracer, event_type="cost_tracked_call")
   def cost_aware_completion(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 150) -> dict:
       """OpenAI completion with detailed cost tracking."""
       
       client = openai.OpenAI()
       
       enrich_span({
           "cost.model": model,
           "cost.max_tokens": max_tokens,
           "cost.prompt_length": len(prompt)
       })
       
       response = client.chat.completions.create(
           model=model,
           messages=[{"role": "user", "content": prompt}],
           max_tokens=max_tokens
       )
       
       # Calculate costs
       prompt_tokens = response.usage.prompt_tokens
       completion_tokens = response.usage.completion_tokens
       total_tokens = response.usage.total_tokens
       
       estimated_cost = calculate_cost(model, prompt_tokens, completion_tokens)
       
       enrich_span({
           "cost.prompt_tokens": prompt_tokens,
           "cost.completion_tokens": completion_tokens,
           "cost.total_tokens": total_tokens,
           "cost.estimated_usd": estimated_cost,
           "cost.tokens_per_dollar": total_tokens / estimated_cost if estimated_cost > 0 else 0
       })
       
       return {
           "response": response.choices[0].message.content,
           "cost": estimated_cost,
           "tokens": total_tokens,
           "efficiency": len(response.choices[0].message.content) / total_tokens
       }

Batch Processing
----------------

**Problem**: I need to process many OpenAI requests efficiently while tracking each one.

**Solution**:

.. code-block:: python

   import asyncio
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type=EventType.tool)
   async def process_batch_requests(prompts: list[str], concurrency: int = 5) -> list[str]:
       """Process multiple OpenAI requests concurrently."""
       
       enrich_span({
           "batch.total_requests": len(prompts),
           "batch.concurrency": concurrency,
           "batch.avg_prompt_length": sum(len(p) for p in prompts) / len(prompts)
       })
       
       # Create semaphore to limit concurrency
       semaphore = asyncio.Semaphore(concurrency)
       
       async def process_single_request(prompt: str, index: int) -> str:
           async with semaphore:
               with tracer.trace(f"batch_item_{index}") as span:
                   span.set_attribute("batch.item_index", index)
                   span.set_attribute("batch.prompt_length", len(prompt))
                   
                   client = openai.AsyncOpenAI()
                   
                   response = await client.chat.completions.create(
                       model="gpt-3.5-turbo",
                       messages=[{"role": "user", "content": prompt}]
                   )
                   
                   result = response.choices[0].message.content
                   
                   span.set_attribute("batch.response_length", len(result))
                   span.set_attribute("batch.tokens_used", response.usage.total_tokens)
                   
                   return result
       
       # Process all requests concurrently
       tasks = [process_single_request(prompt, i) for i, prompt in enumerate(prompts)]
       results = await asyncio.gather(*tasks, return_exceptions=True)
       
       # Count successes and failures
       successes = sum(1 for r in results if not isinstance(r, Exception))
       failures = len(results) - successes
       
       enrich_span({
           "batch.successes": successes,
           "batch.failures": failures,
           "batch.success_rate": successes / len(results)
       })
       
       # Convert exceptions to error messages
       processed_results = []
       for result in results:
           if isinstance(result, Exception):
               processed_results.append(f"Error: {str(result)}")
           else:
               processed_results.append(result)
       
       return processed_results

Model Comparison
----------------

**Problem**: I want to compare different OpenAI models for the same task.

**Solution**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import time
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type=EventType.chain)
   def compare_models(prompt: str, models: list[str] = None) -> dict:
       """Compare different OpenAI models for the same prompt."""
       
       if models is None:
           models = ["gpt-3.5-turbo", "gpt-4"]
       
       client = openai.OpenAI()
       results = {}
       
       enrich_span({
           "comparison.models": models,
           "comparison.prompt_length": len(prompt)
       })
       
       for model in models:
           with tracer.trace(f"model_test_{model}") as span:
               span.set_attribute("model.name", model)
               start_time = time.time()
               
               try:
                   response = client.chat.completions.create(
                       model=model,
                       messages=[{"role": "user", "content": prompt}],
                       max_tokens=150
                   )
                   
                   duration = time.time() - start_time
                   content = response.choices[0].message.content
                   
                   span.set_attribute("model.success", True)
                   span.set_attribute("model.duration", duration)
                   span.set_attribute("model.tokens", response.usage.total_tokens)
                   span.set_attribute("model.response_length", len(content))
                   
                   results[model] = {
                       "response": content,
                       "duration": duration,
                       "tokens": response.usage.total_tokens,
                       "cost": calculate_cost(model, response.usage.prompt_tokens, response.usage.completion_tokens),
                       "success": True
                   }
                   
               except Exception as e:
                   duration = time.time() - start_time
                   
                   span.set_attribute("model.success", False)
                   span.set_attribute("model.error", str(e))
                   span.set_attribute("model.duration", duration)
                   
                   results[model] = {
                       "response": f"Error: {str(e)}",
                       "duration": duration,
                       "tokens": 0,
                       "cost": 0,
                       "success": False
                   }
       
       # Add comparison metrics
       successful_models = [m for m in models if results[m]["success"]]
       if successful_models:
           avg_duration = sum(results[m]["duration"] for m in successful_models) / len(successful_models)
           avg_tokens = sum(results[m]["tokens"] for m in successful_models) / len(successful_models)
           
           enrich_span({
               "comparison.successful_models": len(successful_models),
               "comparison.avg_duration": avg_duration,
               "comparison.avg_tokens": avg_tokens
           })
       
       return results

Troubleshooting
---------------

**Common Issues and Solutions:**

**Issue: Traces not appearing**

.. code-block:: python

   # Debug: Check if instrumentor is working
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   # Verify instrumentor is initialized
   from openinference.instrumentation.openai import OpenAIInstrumentor
   instrumentor = OpenAIInstrumentor()
   print(f"Instrumentor initialized: {instrumentor}")

**Issue: Missing token information**

.. code-block:: python

   # Ensure you're using the latest openai library version
   import openai
   print(f"OpenAI version: {openai.__version__}")
   
   # Make sure response.usage is available
   response = client.chat.completions.create(...)
   if hasattr(response, 'usage'):
       print(f"Tokens: {response.usage.total_tokens}")

**Issue: High latency from tracing**

.. code-block:: python

   # Use async client for better performance
   import openai
   client = openai.AsyncOpenAI()
   
   # Or reduce trace detail
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()],
       disable_http_tracing=True  # Reduce overhead
   )

See Also
--------

- :doc:`anthropic` - Anthropic integration patterns
- :doc:`google-ai` - Google AI (Gemini) integration patterns
- :doc:`aws-bedrock` - AWS Bedrock integration patterns
- :doc:`azure-openai` - Azure OpenAI integration patterns
- :doc:`multi-provider` - Using multiple providers together
- :doc:`../troubleshooting` - General troubleshooting guide
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
- :doc:`../../explanation/architecture/byoi-design` - BYOI architecture explanation

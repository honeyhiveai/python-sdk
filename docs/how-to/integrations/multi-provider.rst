Multi-Provider Integration
==========================

Learn how to integrate multiple LLM providers in a single application using HoneyHive's BYOI (Bring Your Own Instrumentor) architecture.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The HoneyHive SDK allows you to trace multiple LLM providers simultaneously using either OpenInference or Traceloop instrumentors. This approach provides:

- **Provider Flexibility**: Use any combination of OpenAI, Anthropic, Google AI, Google ADK, AWS Bedrock, Azure OpenAI, MCP
- **Instrumentor Choice**: Choose between OpenInference (lightweight) or Traceloop (enhanced metrics)
- **Zero Code Changes**: Existing LLM calls are automatically traced
- **Unified Observability**: All providers appear in the same HoneyHive dashboard
- **Independent Configuration**: Each provider can have different settings
- **Intelligent Integration**: Automatic provider strategy selection prevents span loss and enables coexistence

Choose Your Instrumentor Strategy
---------------------------------

**Problem**: I need to choose between OpenInference and Traceloop for multi-provider setups.

**Solution**: You can mix and match instrumentors based on your needs:

**Option 1: All OpenInference (Lightweight)**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.bedrock import BedrockInstrumentor

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project"         # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize each instrumentor separately with tracer_provider
   openai_instrumentor = OpenAIInstrumentor()
   openai_instrumentor.instrument(tracer_provider=tracer.provider)
   
   anthropic_instrumentor = AnthropicInstrumentor()
   anthropic_instrumentor.instrument(tracer_provider=tracer.provider)
   
   google_instrumentor = GoogleGenerativeAIInstrumentor()
   google_instrumentor.instrument(tracer_provider=tracer.provider)
   
   bedrock_instrumentor = BedrockInstrumentor()
   bedrock_instrumentor.instrument(tracer_provider=tracer.provider)

**Option 2: All Traceloop (Enhanced Metrics)**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
   from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   from opentelemetry.instrumentation.bedrock import BedrockInstrumentor

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project"         # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider  
   instrumentor = OpenAIInstrumentor(),           # Traceloop
           AnthropicInstrumentor(),        # Traceloop
           GoogleGenerativeAIInstrumentor(), # Traceloop
           BedrockInstrumentor()           # Traceloop
   instrumentor.instrument(tracer_provider=tracer.provider)

**Option 3: Mixed Instrumentors (Strategic)**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   # OpenInference imports
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   # Traceloop imports  
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project"         # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider  
   instrumentor = OpenAIInstrumentor(),           # Traceloop (enhanced metrics)
           AnthropicInstrumentor(),        # Traceloop (enhanced metrics)
           GoogleADKInstrumentor()         # OpenInference (only option available)
   instrumentor.instrument(tracer_provider=tracer.provider)

**When to Use Each:**

- **OpenInference**: Lightweight, open-source, good for development and simple production setups
- **Traceloop**: Enhanced LLM metrics, cost tracking, production optimizations, detailed token analysis
- **Mixed**: Use Traceloop for high-volume providers (cost tracking) and OpenInference for others

Quick Start
-----------

Initialize HoneyHive with multiple instrumentors:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   from openinference.instrumentation.mcp import MCPInstrumentor
   from openinference.instrumentation.openai import OpenAIInstrumentor

   # Initialize with multiple instrumentors
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",  # Or set HH_API_KEY environment variable
       project="your-project"         # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider  
   instrumentor = AnthropicInstrumentor(),
           GoogleGenerativeAIInstrumentor(),
           GoogleADKInstrumentor(),
           MCPInstrumentor(),          # Agent tool orchestration
           OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

   # Now all providers are automatically traced
   import anthropic
   import google.generativeai as genai
   import google.adk as adk
   import openai

   # Each call is automatically traced with provider-specific context
   anthropic_client = anthropic.Anthropic()
   google_model = genai.GenerativeModel('gemini-pro')
   google_agent = adk.Agent(name="multi_provider_agent", model="gemini-pro")
   openai_client = openai.OpenAI()

Multi-Provider Agent Workflow
-----------------------------

**Problem**: Build an AI agent that uses different providers for different tasks.

**Solution**: Use provider strengths for specific operations:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import openai
   import anthropic

   # Initialize with multiple instrumentors
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",        # Or set HH_API_KEY environment variable
       project="your-project"         # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentors separately with tracer_provider  
   openai_instrumentor = OpenAIInstrumentor()
   anthropic_instrumentor = AnthropicInstrumentor()
   
   openai_instrumentor.instrument(tracer_provider=tracer.provider)
   anthropic_instrumentor.instrument(tracer_provider=tracer.provider)

   # Initialize clients
   openai_client = openai.OpenAI()
   anthropic_client = anthropic.Anthropic()

   from honeyhive import trace, enrich_span, set_default_tracer
   from honeyhive.models import EventType
   
   # Set up default tracer for cleaner code
   set_default_tracer(tracer)
   
   @trace(event_type=EventType.model)
   def classify_task(user_query: str) -> str:
       """Classify user query using OpenAI - automatically traced."""
       enrich_span({
           "llm.provider": "openai",
           "llm.task": "classification",
           "query.length": len(user_query)
       })
       
       classification = openai_client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{
               "role": "system", 
               "content": "Classify this query as: creative, analytical, or factual"
           }, {
               "role": "user", 
               "content": user_query
           }]
       )
       
       task_type = classification.choices[0].message.content.lower()
       enrich_span({"classification.result": task_type})
       return task_type
   
   @trace(event_type=EventType.model)
   def generate_creative_response(user_query: str) -> str:
       """Generate creative response using Anthropic - automatically traced."""
       enrich_span({
           "llm.provider": "anthropic",
           "llm.task": "creative_writing",
           "llm.model": "claude-3-sonnet-20240229"
       })
       
       response = anthropic_client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=1000,
           messages=[{
               "role": "user",
               "content": f"Be creative and engaging: {user_query}"
           }]
       )
       
       final_response = response.content[0].text
       enrich_span({"response.length": len(final_response)})
       return final_response
   
   @trace(event_type=EventType.model)
   def generate_analytical_response(user_query: str) -> str:
       """Generate analytical response using OpenAI GPT-4 - automatically traced."""
       enrich_span({
           "llm.provider": "openai",
           "llm.task": "analysis",
           "llm.model": "gpt-4"
       })
       
       response = openai_client.chat.completions.create(
           model="gpt-4",
           messages=[{
               "role": "system",
               "content": "Provide a thorough analytical response with reasoning."
           }, {
               "role": "user",
               "content": user_query
           }]
       )
       
       final_response = response.choices[0].message.content
       enrich_span({"response.length": len(final_response)})
       return final_response
   
   @trace(event_type=EventType.model)
   def generate_factual_response(user_query: str) -> str:
       """Generate factual response using OpenAI - automatically traced."""
       enrich_span({
           "llm.provider": "openai",
           "llm.task": "factual_qa",
           "llm.model": "gpt-3.5-turbo"
       })
       
       response = openai_client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{
               "role": "system",
               "content": "Provide accurate, factual information."
           }, {
               "role": "user",
               "content": user_query
           }]
       )
       
       final_response = response.choices[0].message.content
       enrich_span({"response.length": len(final_response)})
       return final_response
   
   @trace(event_type=EventType.chain)
   def intelligent_agent(user_query: str) -> str:
       """Agent that routes to different providers based on task type - automatically traced."""
       enrich_span({
           "agent.query": user_query,
           "agent.strategy": "multi_provider",
           "agent.query_length": len(user_query)
       })
       
       # Step 1: Classify the task (automatically traced)
       task_type = classify_task(user_query)
       
       # Step 2: Route to appropriate provider (each function automatically traced)
       if "creative" in task_type:
           final_response = generate_creative_response(user_query)
           provider_used = "anthropic"
       elif "analytical" in task_type:
           final_response = generate_analytical_response(user_query)
           provider_used = "openai_gpt4"
       else:  # factual
           final_response = generate_factual_response(user_query)
           provider_used = "openai_gpt35"
       
       enrich_span({
           "agent.task_classification": task_type,
           "agent.provider_used": provider_used,
           "agent.response_length": len(final_response)
       })
       
       return final_response

**Benefits of the Decorator-First Approach:**

- **Clean Separation**: Each provider function is independently traceable
- **Automatic Tracing**: No manual span management in business logic
- **Better Testing**: Individual functions can be tested in isolation
- **Clearer Code**: Function purposes are immediately obvious
- **Easier Debugging**: Each step has its own trace with specific context

Usage Example
~~~~~~~~~~~~~

.. code-block:: python

   # Clean, straightforward usage
   query = "Write a creative story about AI"
   response = intelligent_agent(query)
   print(response)

Cost Optimization Strategy
--------------------------

**Problem**: Optimize costs by using different models for different complexity levels.

**Solution**: Route based on complexity and cost considerations:

.. code-block:: python

   def cost_optimized_agent(query: str, complexity_threshold: float = 0.7):
       """Route to cost-effective models based on query complexity."""
       
       with tracer.start_span("agent.cost_optimization") as cost_span:
           cost_span.set_attribute("optimization.strategy", "cost_based_routing")
           
           # Step 1: Analyze query complexity (using cheaper model)
           complexity_analysis = openai_client.chat.completions.create(
               model="gpt-3.5-turbo",  # Cheaper for analysis
               messages=[{
                   "role": "system",
                   "content": "Rate the complexity of this query from 0.0 to 1.0. Respond with just the number."
               }, {
                   "role": "user",
                   "content": query
               }]
           )
           
           try:
               complexity = float(complexity_analysis.choices[0].message.content.strip())
           except:
               complexity = 0.5  # Default to medium complexity
           
           cost_span.set_attribute("query.complexity_score", complexity)
           
           # Step 2: Route based on complexity
           if complexity < complexity_threshold:
               # Use cheaper model for simple queries
               cost_span.set_attribute("routing.decision", "cost_optimized")
               cost_span.set_attribute("routing.model", "gpt-3.5-turbo")
               
               response = openai_client.chat.completions.create(
                   model="gpt-3.5-turbo",
                   messages=[{"role": "user", "content": query}]
               )
               result = response.choices[0].message.content
               estimated_cost = 0.002  # Approximate cost
               
           else:
               # Use premium model for complex queries
               cost_span.set_attribute("routing.decision", "quality_optimized")
               cost_span.set_attribute("routing.model", "claude-3-sonnet")
               
               response = anthropic_client.messages.create(
                   model="claude-3-sonnet-20240229",
                   max_tokens=1000,
                   messages=[{"role": "user", "content": query}]
               )
               result = response.content[0].text
               estimated_cost = 0.015  # Approximate cost
           
           cost_span.set_attribute("cost.estimated_usd", estimated_cost)
           cost_span.set_attribute("cost.efficiency_ratio", len(result) / estimated_cost)
           
           return {
               "response": result,
               "complexity": complexity,
               "estimated_cost": estimated_cost,
               "model_used": "gpt-3.5-turbo" if complexity < complexity_threshold else "claude-3-sonnet"
           }

A/B Testing Across Providers
----------------------------

**Problem**: Compare performance across different LLM providers.

**Solution**: Implement A/B testing with automatic metrics collection:

.. code-block:: python

   import random
   from datetime import datetime

   def ab_test_providers(query: str, test_split: float = 0.5):
       """A/B test between providers with automatic metrics collection."""
       
       # Determine which provider to use
       use_provider_a = random.random() < test_split
       provider_name = "openai" if use_provider_a else "anthropic"
       
       with tracer.start_span("ab_test.provider_comparison") as ab_span:
           ab_span.set_attribute("ab_test.provider", provider_name)
           ab_span.set_attribute("ab_test.split_ratio", test_split)
           ab_span.set_attribute("ab_test.query_hash", hash(query) % 10000)
           
           start_time = datetime.now()
           
           if use_provider_a:
               # Provider A: OpenAI
               ab_span.set_attribute("ab_test.variant", "A_openai")
               
               response = openai_client.chat.completions.create(
                   model="gpt-4",
                   messages=[{"role": "user", "content": query}]
               )
               result = response.choices[0].message.content
               tokens_used = response.usage.total_tokens if response.usage else 0
               
           else:
               # Provider B: Anthropic
               ab_span.set_attribute("ab_test.variant", "B_anthropic")
               
               response = anthropic_client.messages.create(
                   model="claude-3-sonnet-20240229",
                   max_tokens=1000,
                   messages=[{"role": "user", "content": query}]
               )
               result = response.content[0].text
               tokens_used = response.usage.input_tokens + response.usage.output_tokens if hasattr(response, 'usage') else 0
           
           end_time = datetime.now()
           latency_ms = (end_time - start_time).total_seconds() * 1000
           
           # Record A/B test metrics
           ab_span.set_attribute("ab_test.latency_ms", latency_ms)
           ab_span.set_attribute("ab_test.tokens_used", tokens_used)
           ab_span.set_attribute("ab_test.response_length", len(result))
           ab_span.set_attribute("ab_test.chars_per_token", len(result) / max(tokens_used, 1))
           
           return {
               "response": result,
               "provider": provider_name,
               "variant": "A" if use_provider_a else "B",
               "metrics": {
                   "latency_ms": latency_ms,
                   "tokens_used": tokens_used,
                   "response_length": len(result)
               }
           }

Environment-Based Provider Selection
------------------------------------

**Problem**: Use different providers in different environments (dev/staging/prod).

**Solution**: Configure providers based on environment variables:

.. code-block:: python

   import os
   from typing import List

   def create_environment_tracer():
       """Create tracer with environment-appropriate instrumentors."""
       
       instrumentors = []
       environment = os.getenv("ENVIRONMENT", "development")
       
       # Production: Use all providers for redundancy
       if environment == "production":
           instrumentors.extend([
               OpenAIInstrumentor(),
               AnthropicInstrumentor(),
               GoogleGenerativeAIInstrumentor()
           ])
       
       # Staging: Use primary and backup
       elif environment == "staging":
           instrumentors.extend([
               OpenAIInstrumentor(),
               AnthropicInstrumentor()
           ])
       
       # Development: Use only OpenAI for cost savings
       else:
           instrumentors.append(OpenAIInstrumentor())
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           api_key=os.getenv("HH_API_KEY"),     # Or set HH_API_KEY environment variable
           project="your-project",             # Or set HH_PROJECT environment variable
           source=environment                  # Or set HH_SOURCE environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       for instrumentor in instrumentors:
           instrumentor.instrument(tracer_provider=tracer.provider)
       
       return tracer, environment

   def environment_aware_agent(query: str):
       """Agent that adapts behavior based on environment."""
       
       tracer, environment = create_environment_tracer()
       
       with tracer.start_span("agent.environment_aware") as env_span:
           env_span.set_attribute("environment", environment)
           
           if environment == "production":
               # Production: Use redundancy and fallbacks
               try:
                   # Primary: OpenAI
                   response = openai_client.chat.completions.create(
                       model="gpt-4",
                       messages=[{"role": "user", "content": query}]
                   )
                   result = response.choices[0].message.content
                   env_span.set_attribute("provider.used", "openai_primary")
                   
               except Exception as e:
                   env_span.set_attribute("provider.openai_error", str(e))
                   
                   # Fallback: Anthropic
                   response = anthropic_client.messages.create(
                       model="claude-3-sonnet-20240229",
                       max_tokens=1000,
                       messages=[{"role": "user", "content": query}]
                   )
                   result = response.content[0].text
                   env_span.set_attribute("provider.used", "anthropic_fallback")
           
           elif environment == "staging":
               # Staging: A/B test between providers
               result = ab_test_providers(query)["response"]
               env_span.set_attribute("provider.used", "ab_test")
           
           else:
               # Development: Use cheap provider
               response = openai_client.chat.completions.create(
                   model="gpt-3.5-turbo",
                   messages=[{"role": "user", "content": query}]
               )
               result = response.choices[0].message.content
               env_span.set_attribute("provider.used", "openai_dev")
           
           return {
               "response": result,
               "environment": environment
           }

Error Handling and Fallbacks
----------------------------

**Problem**: Ensure reliability when one provider fails.

**Solution**: Implement graceful fallbacks between providers:

.. code-block:: python

   def resilient_multi_provider_agent(query: str, max_retries: int = 3):
       """Agent with automatic failover between providers."""
       
       # Define provider priority order
       providers = [
           {
               "name": "openai",
               "client": openai_client,
               "model": "gpt-4",
               "call": lambda q: openai_client.chat.completions.create(
                   model="gpt-4",
                   messages=[{"role": "user", "content": q}]
               ).choices[0].message.content
           },
           {
               "name": "anthropic", 
               "client": anthropic_client,
               "model": "claude-3-sonnet",
               "call": lambda q: anthropic_client.messages.create(
                   model="claude-3-sonnet-20240229",
                   max_tokens=1000,
                   messages=[{"role": "user", "content": q}]
               ).content[0].text
           }
       ]
       
       with tracer.start_span("agent.resilient_multi_provider") as resilient_span:
           resilient_span.set_attribute("resilience.max_retries", max_retries)
           resilient_span.set_attribute("resilience.providers_available", len(providers))
           
           last_error = None
           
           for attempt in range(max_retries):
               for i, provider in enumerate(providers):
                   provider_span_name = f"attempt_{attempt+1}.provider_{provider['name']}"
                   
                   with tracer.start_span(provider_span_name) as provider_span:
                       provider_span.set_attribute("provider.name", provider["name"])
                       provider_span.set_attribute("provider.model", provider["model"])
                       provider_span.set_attribute("attempt.number", attempt + 1)
                       provider_span.set_attribute("provider.priority", i + 1)
                       
                       try:
                           result = provider["call"](query)
                           
                           # Success!
                           provider_span.set_attribute("provider.success", True)
                           resilient_span.set_attribute("success.provider", provider["name"])
                           resilient_span.set_attribute("success.attempt", attempt + 1)
                           resilient_span.set_attribute("success.total_attempts", attempt + 1)
                           
                           return {
                               "response": result,
                               "provider_used": provider["name"],
                               "attempt": attempt + 1,
                               "fallback_occurred": attempt > 0 or i > 0
                           }
                       
                       except Exception as e:
                           last_error = e
                           provider_span.set_attribute("provider.success", False)
                           provider_span.set_attribute("provider.error", str(e))
                           provider_span.set_status("ERROR", str(e))
                           
                           # Log the error but continue to next provider
                           print(f"Provider {provider['name']} failed (attempt {attempt+1}): {e}")
           
           # All providers failed
           resilient_span.set_attribute("success.provider", "none")
           resilient_span.set_attribute("success.total_attempts", max_retries * len(providers))
           resilient_span.set_status("ERROR", f"All providers failed. Last error: {last_error}")
           
           raise Exception(f"All {len(providers)} providers failed after {max_retries} attempts. Last error: {last_error}")

Monitoring Multi-Provider Performance
-------------------------------------

**Problem**: Track performance metrics across multiple providers.

**Solution**: Implement comprehensive monitoring with provider-specific metrics:

.. code-block:: python

   from collections import defaultdict
   import time

   class MultiProviderMonitor:
       def __init__(self, tracer):
           self.tracer = tracer
           self.metrics = defaultdict(lambda: defaultdict(list))
       
       def track_request(self, provider: str, model: str, query: str):
           """Context manager to track provider performance."""
           
           return self._ProviderTracker(self, provider, model, query)
       
       class _ProviderTracker:
           def __init__(self, monitor, provider: str, model: str, query: str):
               self.monitor = monitor
               self.provider = provider
               self.model = model
               self.query = query
               self.start_time = None
               self.span = None
           
           def __enter__(self):
               self.start_time = time.time()
               self.span = self.monitor.tracer.start_span(f"monitor.{self.provider}")
               self.span.set_attribute("monitor.provider", self.provider)
               self.span.set_attribute("monitor.model", self.model)
               self.span.set_attribute("monitor.query_length", len(self.query))
               return self
           
           def __exit__(self, exc_type, exc_val, exc_tb):
               duration = time.time() - self.start_time
               
               if exc_type is None:
                   # Success
                   self.span.set_attribute("monitor.success", True)
                   self.span.set_attribute("monitor.duration_ms", duration * 1000)
                   
                   # Record metrics
                   key = f"{self.provider}_{self.model}"
                   self.monitor.metrics[key]["durations"].append(duration)
                   self.monitor.metrics[key]["successes"].append(1)
               else:
                   # Error
                   self.span.set_attribute("monitor.success", False)
                   self.span.set_attribute("monitor.error", str(exc_val))
                   self.span.set_status("ERROR", str(exc_val))
                   
                   # Record error
                   key = f"{self.provider}_{self.model}"
                   self.monitor.metrics[key]["successes"].append(0)
               
               self.span.end()
       
       def get_performance_report(self):
           """Generate performance report across all providers."""
           
           report = {}
           
           for provider_model, metrics in self.metrics.items():
               if not metrics["durations"]:
                   continue
               
               durations = metrics["durations"]
               successes = metrics["successes"]
               
               report[provider_model] = {
                   "avg_duration_ms": sum(durations) / len(durations) * 1000,
                   "min_duration_ms": min(durations) * 1000,
                   "max_duration_ms": max(durations) * 1000,
                   "success_rate": sum(successes) / len(successes),
                   "total_requests": len(successes),
                   "total_errors": len(successes) - sum(successes)
               }
           
           return report

   # Usage example
   def monitored_multi_provider_agent(query: str):
       """Agent with comprehensive performance monitoring."""
       
       monitor = MultiProviderMonitor(tracer)
       
       with tracer.start_span("agent.monitored_multi_provider") as agent_span:
           
           # Try OpenAI first
           try:
               with monitor.track_request("openai", "gpt-4", query):
                   response = openai_client.chat.completions.create(
                       model="gpt-4",
                       messages=[{"role": "user", "content": query}]
                   )
                   result = response.choices[0].message.content
                   agent_span.set_attribute("final_provider", "openai")
                   return {"response": result, "provider": "openai"}
           
           except Exception as e:
               agent_span.set_attribute("openai_error", str(e))
           
           # Fallback to Anthropic
           try:
               with monitor.track_request("anthropic", "claude-3-sonnet", query):
                   response = anthropic_client.messages.create(
                       model="claude-3-sonnet-20240229",
                       max_tokens=1000,
                       messages=[{"role": "user", "content": query}]
                   )
                   result = response.content[0].text
                   agent_span.set_attribute("final_provider", "anthropic")
                   return {"response": result, "provider": "anthropic"}
           
           except Exception as e:
               agent_span.set_attribute("anthropic_error", str(e))
               raise Exception("All providers failed")

Best Practices
--------------

**1. Provider Selection Strategy**

.. code-block:: python

   # Good: Strategic provider selection
   def choose_provider(task_type: str, budget_limit: float):
       if task_type == "creative" and budget_limit > 0.01:
           return "anthropic"  # Best for creative tasks
       elif task_type == "code" and budget_limit > 0.015:
           return "openai"     # Best for coding
       elif task_type == "factual":
           return "openai"     # Good balance of cost/quality
       else:
           return "openai"     # Fallback

**2. Error Handling**

.. code-block:: python

   # Good: Graceful degradation
   try:
       result = primary_provider_call(query)
   except RateLimitError:
       result = secondary_provider_call(query)
   except Exception as e:
       logger.error(f"Provider failed: {e}")
       result = fallback_response(query)

**3. Cost Management**

.. code-block:: python

   # Good: Cost-aware routing
   def cost_aware_routing(query: str, user_tier: str):
       if user_tier == "premium":
           return use_best_model(query)
       elif estimate_complexity(query) > 0.8:
           return use_good_model(query)
       else:
           return use_cheap_model(query)

**4. Performance Monitoring**

.. code-block:: python

   # Good: Track all relevant metrics
   with tracer.start_span("provider_call") as span:
       span.set_attribute("provider", provider_name)
       span.set_attribute("model", model_name)
       span.set_attribute("estimated_cost", estimated_cost)
       span.set_attribute("user_tier", user_tier)
       
       result = make_llm_call()
       
       span.set_attribute("actual_tokens", result.usage.total_tokens)
       span.set_attribute("success", True)

See Also
--------

- :doc:`../index` - Common integration issues (see Troubleshooting section)
- :doc:`../../tutorials/02-add-llm-tracing-5min` - LLM integration tutorial
- :doc:`../../explanation/architecture/byoi-design` - BYOI architecture explanation
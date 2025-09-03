Integrate with Anthropic
========================

.. note::
   **Problem-solving guide for Anthropic (Claude) integration**
   
   This guide helps you solve specific problems when integrating HoneyHive with Anthropic's Claude models using the BYOI architecture.

This guide covers common patterns and solutions for Anthropic Claude integration with HoneyHive.

Quick Setup
-----------

**Problem**: I want to add HoneyHive tracing to my existing Anthropic Claude code.

**Solution**:

.. code-block:: bash

   # Install required packages
   pip install honeyhive openinference-instrumentation-anthropic anthropic

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import anthropic
   
   # Initialize HoneyHive with Anthropic instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-key",
       instrumentors=[AnthropicInstrumentor()]
   )
   
   # Use Anthropic exactly as before - automatic tracing!
   client = anthropic.Anthropic(api_key="your-anthropic-key")
   response = client.messages.create(
       model="claude-3-sonnet-20240229",
       max_tokens=100,
       messages=[{"role": "user", "content": "Hello, Claude!"}]
   )

Environment Variables
---------------------

**Problem**: I need to manage Anthropic API keys securely across environments.

**Solution**:

.. code-block:: bash

   # .env file
   HH_API_KEY=hh_your_honeyhive_key_here
   HH_PROJECT=anthropic-production
   HH_SOURCE=production
   ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import anthropic
   
   # Automatic environment variable usage
   tracer = HoneyHiveTracer.init(
       instrumentors=[AnthropicInstrumentor()]
   )
   
   # Anthropic client uses ANTHROPIC_API_KEY automatically
   client = anthropic.Anthropic()

Claude-Specific Features
-------------------------

**Problem**: I want to leverage Claude's unique capabilities while maintaining observability.

**Working with Claude's Conversation Format**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import anthropic
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[AnthropicInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type=EventType.model)
   def conduct_claude_conversation(conversation_history: list, new_message: str) -> str:
       """Conduct a conversation with Claude while tracking context."""
       
       client = anthropic.Anthropic()
       
       # Add new message to conversation
       messages = conversation_history + [{"role": "user", "content": new_message}]
       
       enrich_span({
           "conversation.message_count": len(messages),
           "conversation.total_length": sum(len(msg["content"]) for msg in messages),
           "conversation.turns": len([m for m in messages if m["role"] == "user"])
       })
       
       response = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=500,
           messages=messages
       )
       
       assistant_message = response.content[0].text
       
       enrich_span({
           "response.length": len(assistant_message),
           "response.finish_reason": response.stop_reason,
           "model.used": "claude-3-sonnet"
       })
       
       return assistant_message

**Using Claude's System Messages**:

.. code-block:: python

   @trace(tracer=tracer, event_type="claude_system_prompt")
   def claude_with_system_prompt(system_prompt: str, user_message: str) -> str:
       """Use Claude with a system prompt for role-playing or specific behavior."""
       
       client = anthropic.Anthropic()
       
       enrich_span({
           "system_prompt.length": len(system_prompt),
           "system_prompt.type": classify_system_prompt(system_prompt),
           "user_message.length": len(user_message)
       })
       
       response = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=300,
           system=system_prompt,
           messages=[{"role": "user", "content": user_message}]
       )
       
       return response.content[0].text
   
   def classify_system_prompt(prompt: str) -> str:
       """Classify the type of system prompt."""
       if "expert" in prompt.lower():
           return "expert_role"
       elif "assistant" in prompt.lower():
           return "assistant_role"
       elif "analyze" in prompt.lower():
           return "analysis_task"
       return "custom"

Document Analysis with Claude
------------------------------

**Problem**: I need to analyze documents with Claude while tracking performance and quality.

**Solution**:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import anthropic
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[AnthropicInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type="document_analysis")
   def analyze_document_with_claude(document: str, analysis_type: str = "summary") -> dict:
       """Analyze documents using Claude with different analysis types."""
       
       client = anthropic.Anthropic()
       
       # Document preprocessing
       doc_stats = {
           "length": len(document),
           "word_count": len(document.split()),
           "estimated_tokens": len(document) // 4  # Rough estimate
       }
       
       enrich_span({
           "document.length": doc_stats["length"],
           "document.word_count": doc_stats["word_count"],
           "document.estimated_tokens": doc_stats["estimated_tokens"],
           "analysis.type": analysis_type
       })
       
       # Choose prompt based on analysis type
       prompts = {
           "summary": "Please provide a concise summary of this document:",
           "key_points": "Extract the key points from this document:",
           "sentiment": "Analyze the sentiment and tone of this document:",
           "action_items": "Identify any action items or next steps mentioned:",
           "questions": "Generate thoughtful questions about this document:"
       }
       
       prompt = prompts.get(analysis_type, prompts["summary"])
       
       response = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=500,
           messages=[{
               "role": "user", 
               "content": f"{prompt}\n\n{document}"
           }]
       )
       
       analysis_result = response.content[0].text
       
       enrich_span({
           "analysis.result_length": len(analysis_result),
           "analysis.token_efficiency": len(analysis_result) / doc_stats["estimated_tokens"],
           "model.stop_reason": response.stop_reason
       })
       
       return {
           "analysis": analysis_result,
           "type": analysis_type,
           "document_stats": doc_stats,
           "model_info": {
               "model": "claude-3-sonnet",
               "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
               "stop_reason": response.stop_reason
           }
       }

Claude Model Comparison
------------------------

**Problem**: I want to compare different Claude models for my use case.

**Solution**:

.. code-block:: python

   @trace(tracer=tracer, event_type="claude_model_comparison")
   def compare_claude_models(prompt: str, models: list = None) -> dict:
       """Compare different Claude models for the same prompt."""
       
       if models is None:
           models = ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"]
       
       client = anthropic.Anthropic()
       results = {}
       
       enrich_span({
           "comparison.models": models,
           "comparison.prompt_length": len(prompt)
       })
       
       for model in models:
           with tracer.trace(f"claude_model_{model}") as span:
               span.set_attribute("model.name", model)
               start_time = time.time()
               
               try:
                   response = client.messages.create(
                       model=model,
                       max_tokens=200,
                       messages=[{"role": "user", "content": prompt}]
                   )
                   
                   duration = time.time() - start_time
                   content = response.content[0].text
                   
                   span.set_attribute("model.success", True)
                   span.set_attribute("model.duration", duration)
                   span.set_attribute("model.input_tokens", response.usage.input_tokens)
                   span.set_attribute("model.output_tokens", response.usage.output_tokens)
                   span.set_attribute("model.response_length", len(content))
                   
                   results[model] = {
                       "response": content,
                       "duration": duration,
                       "tokens": {
                           "input": response.usage.input_tokens,
                           "output": response.usage.output_tokens,
                           "total": response.usage.input_tokens + response.usage.output_tokens
                       },
                       "success": True,
                       "model_tier": get_model_tier(model)
                   }
                   
               except Exception as e:
                   duration = time.time() - start_time
                   
                   span.set_attribute("model.success", False)
                   span.set_attribute("model.error", str(e))
                   span.set_attribute("model.duration", duration)
                   
                   results[model] = {
                       "response": f"Error: {str(e)}",
                       "duration": duration,
                       "tokens": {"input": 0, "output": 0, "total": 0},
                       "success": False,
                       "error": str(e)
                   }
       
       return results
   
   def get_model_tier(model: str) -> str:
       """Classify Claude model by performance tier."""
       if "haiku" in model:
           return "fast"
       elif "sonnet" in model:
           return "balanced"
       elif "opus" in model:
           return "powerful"
       return "unknown"

Streaming with Claude
---------------------

**Problem**: I need to implement streaming responses with Claude while maintaining tracing.

**Solution**:

.. code-block:: python

   import time
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import anthropic
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[AnthropicInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type="claude_streaming")
   def stream_claude_response(prompt: str) -> str:
       """Handle Claude streaming responses with detailed tracking."""
       
       client = anthropic.Anthropic()
       start_time = time.time()
       
       enrich_span({
           "streaming.enabled": True,
           "prompt.length": len(prompt)
       })
       
       stream = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=500,
           messages=[{"role": "user", "content": prompt}],
           stream=True
       )
       
       chunks = []
       first_chunk_time = None
       chunk_count = 0
       
       for event in stream:
           if event.type == "content_block_delta" and event.delta.type == "text_delta":
               chunk_count += 1
               content = event.delta.text
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

Error Handling and Retry Logic
------------------------------

**Problem**: I need robust error handling for Anthropic API calls.

**Solution**:

.. code-block:: python

   import anthropic
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   import time
   import random
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[AnthropicInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type="anthropic_with_retry")
   def robust_claude_call(prompt: str, max_retries: int = 3) -> str:
       """Claude call with comprehensive error handling and retry logic."""
       
       client = anthropic.Anthropic()
       last_error = None
       
       for attempt in range(max_retries):
           try:
               enrich_span({
                   "retry.attempt": attempt + 1,
                   "retry.max_attempts": max_retries
               })
               
               response = client.messages.create(
                   model="claude-3-sonnet-20240229",
                   max_tokens=300,
                   messages=[{"role": "user", "content": prompt}]
               )
               
               # Success - add metrics
               enrich_span({
                   "success": True,
                   "attempts_needed": attempt + 1,
                   "final_tokens": response.usage.input_tokens + response.usage.output_tokens
               })
               
               return response.content[0].text
               
           except anthropic.RateLimitError as e:
               last_error = e
               wait_time = (2 ** attempt) + random.uniform(0, 1)
               
               enrich_span({
                   "error.type": "rate_limit",
                   "error.attempt": attempt + 1,
                   "retry.wait_time": wait_time
               })
               
               if attempt < max_retries - 1:
                   time.sleep(wait_time)
               
           except anthropic.APIError as e:
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

Advanced Claude Techniques
---------------------------

**Working with Claude's Reasoning Capabilities**:

.. code-block:: python

   @trace(tracer=tracer, event_type="claude_reasoning")
   def claude_step_by_step_reasoning(problem: str) -> dict:
       """Use Claude's reasoning capabilities with step-by-step thinking."""
       
       client = anthropic.Anthropic()
       
       reasoning_prompt = f"""
       Please solve this problem step by step. Show your reasoning process clearly:
       
       Problem: {problem}
       
       Please structure your response as:
       1. Understanding the problem
       2. Approach/methodology
       3. Step-by-step solution
       4. Final answer
       5. Verification/check
       """
       
       enrich_span({
           "reasoning.problem_length": len(problem),
           "reasoning.prompt_type": "step_by_step"
       })
       
       response = client.messages.create(
           model="claude-3-opus-20240229",  # Use most capable model for reasoning
           max_tokens=1000,
           messages=[{"role": "user", "content": reasoning_prompt}]
       )
       
       reasoning_response = response.content[0].text
       
       # Analyze the structure of the response
       sections = reasoning_response.split('\n')
       numbered_sections = [s for s in sections if s.strip() and s.strip()[0].isdigit()]
       
       enrich_span({
           "reasoning.response_length": len(reasoning_response),
           "reasoning.structured_sections": len(numbered_sections),
           "reasoning.tokens_used": response.usage.input_tokens + response.usage.output_tokens
       })
       
       return {
           "problem": problem,
           "reasoning": reasoning_response,
           "structured_sections": len(numbered_sections),
           "model": "claude-3-opus",
           "tokens_used": response.usage.input_tokens + response.usage.output_tokens
       }

Cost Optimization
-----------------

**Problem**: I need to optimize costs when using Claude models.

**Solution**:

.. code-block:: python

   # Claude pricing (check current pricing)
   CLAUDE_PRICING = {
       "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},  # per 1M tokens
       "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
       "claude-3-opus-20240229": {"input": 15.00, "output": 75.00}
   }
   
   def calculate_claude_cost(model: str, input_tokens: int, output_tokens: int) -> float:
       """Calculate Claude API call cost."""
       if model not in CLAUDE_PRICING:
           return 0.0
       
       pricing = CLAUDE_PRICING[model]
       input_cost = (input_tokens / 1_000_000) * pricing["input"]
       output_cost = (output_tokens / 1_000_000) * pricing["output"]
       
       return input_cost + output_cost
   
   @trace(tracer=tracer, event_type="cost_optimized_claude")
   def cost_optimized_claude_call(prompt: str, max_budget_usd: float = 0.01) -> dict:
       """Claude call with cost optimization and budget limits."""
       
       client = anthropic.Anthropic()
       
       # Estimate input tokens and costs for different models
       estimated_input_tokens = len(prompt) // 4  # Rough estimate
       
       model_options = []
       for model, pricing in CLAUDE_PRICING.items():
           estimated_cost = calculate_claude_cost(model, estimated_input_tokens, 100)  # Assume 100 output tokens
           model_options.append((model, estimated_cost))
       
       # Sort by cost (cheapest first)
       model_options.sort(key=lambda x: x[1])
       
       enrich_span({
           "cost.max_budget": max_budget_usd,
           "cost.estimated_input_tokens": estimated_input_tokens,
           "cost.model_options": [f"{m}:${c:.4f}" for m, c in model_options]
       })
       
       # Try models starting with cheapest
       for model, estimated_cost in model_options:
           if estimated_cost > max_budget_usd:
               continue
               
           try:
               response = client.messages.create(
                   model=model,
                   max_tokens=100,  # Conservative limit
                   messages=[{"role": "user", "content": prompt}]
               )
               
               actual_cost = calculate_claude_cost(
                   model, 
                   response.usage.input_tokens, 
                   response.usage.output_tokens
               )
               
               enrich_span({
                   "cost.chosen_model": model,
                   "cost.actual_cost": actual_cost,
                   "cost.under_budget": actual_cost <= max_budget_usd,
                   "cost.efficiency": len(response.content[0].text) / actual_cost if actual_cost > 0 else 0
               })
               
               return {
                   "response": response.content[0].text,
                   "model": model,
                   "cost": actual_cost,
                   "tokens": {
                       "input": response.usage.input_tokens,
                       "output": response.usage.output_tokens
                   },
                   "under_budget": actual_cost <= max_budget_usd
               }
               
           except Exception as e:
               enrich_span({f"error.{model}": str(e)})
               continue
       
       # No model worked within budget
       enrich_span({
           "cost.result": "no_model_within_budget",
           "cost.min_required": model_options[0][1] if model_options else 0
       })
       
       raise ValueError(f"No Claude model available within budget of ${max_budget_usd}")

Integration with Other Services
--------------------------------

**Problem**: I need to integrate Claude with other services while maintaining observability.

**Solution**:

.. code-block:: python

   @trace(tracer=tracer, event_type="claude_service_integration")
   def claude_with_database_lookup(user_query: str, user_id: str) -> str:
       """Integrate Claude with database lookup for personalized responses."""
       
       # Database lookup (traced separately)
       with tracer.trace("database_lookup") as span:
           user_context = fetch_user_context(user_id)
           span.set_attribute("user.tier", user_context.get("tier"))
           span.set_attribute("user.history_length", len(user_context.get("history", [])))
       
       # Prepare context-aware prompt
       context_prompt = f"""
       User Context:
       - User ID: {user_id}
       - Tier: {user_context.get('tier', 'standard')}
       - Previous interactions: {len(user_context.get('history', []))}
       - Preferences: {user_context.get('preferences', {})}
       
       User Query: {user_query}
       
       Please provide a personalized response based on this context.
       """
       
       enrich_span({
           "integration.user_id": user_id,
           "integration.user_tier": user_context.get("tier"),
           "integration.context_available": bool(user_context),
           "integration.personalized": True
       })
       
       client = anthropic.Anthropic()
       response = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=300,
           messages=[{"role": "user", "content": context_prompt}]
       )
       
       # Store interaction for future context
       with tracer.trace("store_interaction") as span:
           store_user_interaction(user_id, user_query, response.content[0].text)
           span.set_attribute("storage.success", True)
       
       return response.content[0].text
   
   def fetch_user_context(user_id: str) -> dict:
       """Mock function to fetch user context from database."""
       # In real implementation, this would query your database
       return {
           "tier": "premium",
           "history": ["previous", "interactions"],
           "preferences": {"style": "detailed", "language": "english"}
       }
   
   def store_user_interaction(user_id: str, query: str, response: str):
       """Mock function to store interaction in database."""
       # In real implementation, this would save to your database
       pass

See Also
--------

- :doc:`multi-provider` - Use Anthropic with other providers
- :doc:`../troubleshooting` - Common integration issues
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
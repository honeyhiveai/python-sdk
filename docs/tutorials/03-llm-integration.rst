LLM Provider Integration Tutorial
==================================

.. note::
   **Tutorial Goal**: Learn to trace LLM calls from OpenAI, Anthropic, and other providers with zero code changes.

This **hands-on tutorial** walks you through integrating HoneyHive with popular LLM providers. You'll build a complete example that demonstrates the "Bring Your Own Instrumentor" architecture.

.. tip::
   **Looking for quick integration guides?** See :doc:`../how-to/index` for problem-specific solutions.

What You'll Learn
-----------------

- How to use the "Bring Your Own Instrumentor" (BYOI) architecture
- Tracing OpenAI calls automatically
- Adding Anthropic, Google AI, and Google ADK tracing
- Combining multiple LLM providers and agent frameworks
- Understanding what data gets captured
- Best practices for LLM observability

Prerequisites
-------------

- Complete :doc:`02-basic-tracing` tutorial
- An LLM provider API key (OpenAI, Anthropic, Google AI, or Google ADK)
- Basic familiarity with your chosen LLM provider

The Magic of BYOI Architecture
-------------------------------

HoneyHive's "Bring Your Own Instrumentor" approach means:

- **Zero code changes** to your existing LLM calls
- **Use any OpenTelemetry-compatible instrumentor**
- **No dependency conflicts** with your existing setup
- **Mix and match** multiple LLM providers seamlessly

Think of instrumentors as plugins that automatically capture LLM interactions.

Choosing Your Instrumentor Type
-------------------------------

You have two main options for LLM instrumentation:

**OpenInference (Recommended for Beginners)**
- Lightweight and easy to set up
- Open-source with active community
- Good for development and simple production setups
- Consistent API across all providers

**OpenLLMetry (Advanced Metrics)**
- Enhanced LLM-specific metrics and cost tracking
- Production-optimized with detailed token analysis
- Better performance monitoring capabilities
- Provided by Traceloop (``opentelemetry-instrumentation-*`` packages)

**When to Use Each:**
- **Start with OpenInference** if you're new to LLM observability
- **Upgrade to OpenLLMetry** when you need detailed cost tracking and production metrics
- **Mix both** strategically based on your provider usage patterns

.. note::
   Both instrumentor types work identically with HoneyHive's BYOI architecture. You can switch between them or use both in the same application.

OpenAI Integration
------------------

You can trace OpenAI calls using either OpenInference or OpenLLMetry instrumentors.

**Step 1: Choose and Install Your Instrumentor**

**Option A: OpenInference (Recommended for Beginners)**

.. code-block:: bash

   # Recommended: Install with OpenAI integration
   pip install honeyhive[openinference-openai]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-openai openai

**Option B: OpenLLMetry (Enhanced Metrics)**

.. code-block:: bash

   # Recommended: Install with OpenLLMetry integration
   pip install honeyhive[traceloop-openai]
   
   # Alternative: Manual installation
   pip install honeyhive opentelemetry-instrumentation-openai openai

**Step 2: Set Up Automatic Tracing**

**Using OpenInference:**

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   # Initialize HoneyHive with OpenInference OpenAI instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       source="development",
       instrumentors=[OpenAIInstrumentor()]  # OpenInference version
   )

**Using OpenLLMetry:**

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   # Initialize HoneyHive with OpenLLMetry OpenAI instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       source="development",
       instrumentors=[OpenAIInstrumentor()]  # OpenLLMetry version
   )

**The rest is identical regardless of instrumentor choice:**

.. code-block:: python

   # Use OpenAI exactly as you normally would - no changes needed!
   client = openai.OpenAI(api_key="your-openai-api-key")
   
   def ask_ai(question: str) -> str:
       """Ask AI a question - this will be automatically traced!"""
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "You are a helpful assistant."},
               {"role": "user", "content": question}
           ],
           max_tokens=150
       )
       return response.choices[0].message.content
   
   # This call is automatically traced with full context
   answer = ask_ai("What is the capital of France?")
   print(f"AI Response: {answer}")

**What Gets Captured Automatically:**

- **Model used** (``gpt-3.5-turbo``)
- **Full conversation** (system prompt + user message)
- **Response content** and metadata
- **Token usage** (prompt tokens, completion tokens, total)
- **Timing** (latency, time to first token)
- **Error handling** (rate limits, API errors)

**Step 3: Add Business Context**

Enhance automatic tracing with business context:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[OpenAIInstrumentor()]
   )
   
   @trace(tracer=tracer, event_type="customer_query")
   def handle_customer_question(customer_id: str, question: str, priority: str = "normal"):
       """Handle a customer support question with full context."""
       
       # Add business context to the trace
       enrich_span({
           "customer.id": customer_id,
           "support.priority": priority,
           "support.category": classify_question(question),
           "support.agent": "ai_assistant"
       })
       
       client = openai.OpenAI()
       
       # This OpenAI call is automatically traced AND includes your business context
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": f"You are a helpful customer support agent. Priority: {priority}"},
               {"role": "user", "content": question}
           ]
       )
       
       answer = response.choices[0].message.content
       
       # Add response context
       enrich_span({
           "support.response_length": len(answer),
           "support.tokens_used": response.usage.total_tokens,
           "support.resolved": True
       })
       
       return answer
   
   def classify_question(question: str) -> str:
       """Simple question classification."""
       if any(word in question.lower() for word in ["refund", "money", "payment"]):
           return "billing"
       elif any(word in question.lower() for word in ["bug", "error", "broken"]):
           return "technical"
       else:
           return "general"

Anthropic Integration
---------------------

Add Anthropic Claude tracing with the same BYOI pattern.

**Step 1: Choose and Install Your Instrumentor**

**Option A: OpenInference**

.. code-block:: bash

   # Recommended: Install with Anthropic integration
   pip install honeyhive[openinference-anthropic]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-anthropic

**Option B: OpenLLMetry**

.. code-block:: bash

   # Recommended: Install with OpenLLMetry integration
   pip install honeyhive[traceloop-anthropic]
   
   # Alternative: Manual installation
   pip install honeyhive opentelemetry-instrumentation-anthropic

**Step 2: Set Up Anthropic Tracing**

**Using OpenInference:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import anthropic
   
   # Initialize with OpenInference Anthropic instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[AnthropicInstrumentor()]
   )

**Using OpenLLMetry:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
   import anthropic
   
   # Initialize with OpenLLMetry Anthropic instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[AnthropicInstrumentor()]
   )

**The rest is identical regardless of instrumentor choice:**

.. code-block:: python

   # Use Anthropic normally - automatic tracing!
   client = anthropic.Anthropic(api_key="your-anthropic-api-key")
   
   def analyze_document(document: str) -> dict:
       """Analyze a document using Claude."""
       
       response = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=500,
           messages=[
               {
                   "role": "user", 
                   "content": f"Analyze this document and provide a summary, key points, and sentiment:\\n\\n{document}"
               }
           ]
       )
       
       # Parse Claude's response (simplified)
       analysis_text = response.content[0].text
       
       return {
           "model": "claude-3-sonnet",
           "analysis": analysis_text,
           "input_length": len(document),
           "response_length": len(analysis_text)
       }
   
   # Automatically traced with full context
   doc = "This is a sample business document about our Q3 results..."
   analysis = analyze_document(doc)

Google AI Integration
---------------------

Add Google AI (Gemini) tracing.

**Step 1: Install Google AI Instrumentor**

.. code-block:: bash

   # Recommended: Install with Google AI integration
   pip install honeyhive[openinference-google-ai]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-google-generativeai

**Step 2: Set Up Google AI Tracing**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   import google.generativeai as genai
   
   # Initialize with Google AI instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[GoogleGenerativeAIInstrumentor()]
   )
   
   # Configure Google AI
   genai.configure(api_key="your-google-api-key")
   
   def generate_creative_content(prompt: str, style: str = "professional") -> str:
       """Generate creative content using Gemini."""
       
       model = genai.GenerativeModel('gemini-pro')
       
       full_prompt = f"Write in a {style} style: {prompt}"
       
       # This is automatically traced!
       response = model.generate_content(full_prompt)
       
       return response.text
   
   # Traced automatically with all context
   content = generate_creative_content(
       "A blog post about AI in healthcare", 
       style="engaging"
   )

Multi-Provider Setup
--------------------

Use multiple LLM providers in the same application. You can mix instrumentor types:

**Option A: All OpenInference**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import openai
   import anthropic
   
   # Initialize with multiple OpenInference instrumentors
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[
           OpenAIInstrumentor(),    # OpenInference OpenAI
           AnthropicInstrumentor()  # OpenInference Anthropic
       ]
   )

**Option B: All OpenLLMetry**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
   import openai
   import anthropic
   
   # Initialize with multiple OpenLLMetry instrumentors
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[
           OpenAIInstrumentor(),    # OpenLLMetry OpenAI
           AnthropicInstrumentor()  # OpenLLMetry Anthropic
       ]
   )

**Option C: Mixed Instrumentors (Strategic)**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   # Mix OpenInference and OpenLLMetry
   from openinference.instrumentation.anthropic import AnthropicInstrumentor as OIAnthropic
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor as OLOpenAI
   import openai
   import anthropic
   
   # Initialize with mixed instrumentors
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[
           OLOpenAI(),     # OpenLLMetry for high-volume OpenAI (enhanced metrics)
           OIAnthropic()   # OpenInference for Anthropic (lightweight)
       ]
   )

**The rest of your code remains identical:**

.. code-block:: python

   @trace(tracer=tracer, event_type="llm_comparison")
   def compare_llm_responses(question: str) -> dict:
       """Compare responses from multiple LLM providers."""
       
       enrich_span({
           "comparison.question_length": len(question),
           "comparison.providers": ["openai", "anthropic"]
       })
       
       # Both of these calls are automatically traced
       openai_client = openai.OpenAI()
       anthropic_client = anthropic.Anthropic()
       
       # OpenAI response
       openai_response = openai_client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": question}]
       )
       
       # Anthropic response  
       anthropic_response = anthropic_client.messages.create(
           model="claude-3-haiku-20240307",
           max_tokens=200,
           messages=[{"role": "user", "content": question}]
       )
       
       results = {
           "openai": {
               "response": openai_response.choices[0].message.content,
               "tokens": openai_response.usage.total_tokens,
               "model": "gpt-3.5-turbo"
           },
           "anthropic": {
               "response": anthropic_response.content[0].text,
               "model": "claude-3-haiku"
           }
       }
       
       enrich_span({
           "comparison.openai_tokens": results["openai"]["tokens"],
           "comparison.responses_received": 2
       })
       
       return results
   
   # Compare responses - both calls traced separately
   comparison = compare_llm_responses("What are the benefits of renewable energy?")

Google ADK Integration
----------------------

Add Google Agent Development Kit (ADK) tracing for sophisticated agent workflows.

**Step 1: Install Google ADK Instrumentor**

.. code-block:: bash

   # Recommended: Install with Google ADK integration
   pip install honeyhive[openinference-google-adk]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-google-adk

**Step 2: Set Up Google ADK Tracing**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   import google.adk as adk
   
   # Initialize with Google ADK instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[GoogleADKInstrumentor()]
   )
   
   # Configure Google ADK
   adk.configure(api_key="your-google-adk-api-key")
   
   def create_research_agent(topic: str) -> str:
       """Create an agent that performs research and analysis."""
       
       # Create an agent with research tools
       agent = adk.Agent(
           name="research_agent",
           model="gemini-pro",
           tools=["web_search", "data_analyzer", "summarizer"],
           temperature=0.3
       )
       
       # Agent workflow is automatically traced!
       result = agent.execute(f"Research and analyze: {topic}")
       
       return result.content

**Step 3: Test Your Agent Integration**

.. code-block:: python

   # Example call that demonstrates agent tracing
   research = create_research_agent("impact of AI on education")
   print(f"Research Results: {research}")

**What Gets Captured for Agents:**

- **Agent workflow steps** (tool calls, reasoning, decisions)
- **Tool interactions** (web searches, data processing)
- **Multi-step reasoning chains**
- **State transitions** and decision points
- **Performance metrics** (execution time, tool latency)

MCP (Model Context Protocol) Integration
-----------------------------------------

MCP enables agents to securely connect to data sources and tools through a standardized protocol.

**Step 1: Install MCP Instrumentor**

.. code-block:: bash

   pip install honeyhive[openinference-mcp]

**Step 2: Set Up MCP Tracing**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.models import EventType
   from openinference.instrumentation.mcp import MCPInstrumentor
   
   # Initialize with MCP instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[MCPInstrumentor()]
   )

**Step 3: Use MCP Client Normally**

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
           },
       ) as server:
           
           agent = Agent(
               name="Financial Assistant", 
               instructions="Use financial tools to answer questions.",
               mcp_servers=[server],
           )
           
           # This entire workflow is traced end-to-end
           result = await Runner.run(
               starting_agent=agent,
               input="What's the P/E ratio for AAPL?"
           )
           
           print(f"Result: {result.final_output}")

   # Run the async function
   asyncio.run(main())

**Step 4: Add Custom MCP Tool Tracing**

.. code-block:: python

   @trace(event_type=EventType.tool)
   def mcp_financial_tool(ticker: str, analysis_type: str) -> dict:
       """Example MCP tool with custom tracing."""
       
       # Your MCP tool logic here
       result = {
           "ticker": ticker,
           "analysis": analysis_type,
           "recommendation": "buy",
           "confidence": 0.85
       }
       
       return result

**What Gets Captured for MCP:**

- **Client-server communication** (requests, responses, protocols)
- **Tool executions** (function calls, parameters, results)  
- **Context propagation** across MCP boundaries
- **Session management** (connections, authentication)
- **Error handling** (timeouts, connection failures)
- **Performance metrics** (latency, throughput)

Advanced: Custom Instrumentor Integration
------------------------------------------

You can also integrate custom or community instrumentors:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from your_custom_instrumentor import CustomLLMInstrumentor
   
   # Use any OpenTelemetry-compatible instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[
           CustomLLMInstrumentor(),
           # Mix with standard instrumentors
           # OpenAIInstrumentor(),
       ]
   )

Understanding Trace Data
-------------------------

When you view traces in your HoneyHive dashboard, you'll see:

**LLM Call Details:**
- Model name and version
- Input prompt and system messages
- Full response content
- Token usage breakdown
- Timing information

**Business Context:**
- Custom attributes you added with ``enrich_span()``
- Function-level tracing from ``@trace`` decorators
- Error handling and exceptions

**Performance Metrics:**
- Latency per call
- Tokens per second
- Cost tracking (if configured)

Best Practices for LLM Tracing
-------------------------------

**1. Use Descriptive Event Types**

.. code-block:: python

   @trace(tracer=tracer, event_type="content_generation")
   def generate_blog_post():
       pass
   
   @trace(tracer=tracer, event_type="document_analysis")
   def analyze_contract():
       pass

**2. Add Business Context**

.. code-block:: python

   enrich_span({
       "user.id": user_id,
       "content.type": "blog_post",
       "generation.purpose": "marketing",
       "model.temperature": 0.7
   })

**3. Handle Rate Limits and Errors**

.. code-block:: python

   @trace(tracer=tracer)
   def safe_llm_call(prompt: str, max_retries: int = 3):
       for attempt in range(max_retries):
           try:
               return llm_call(prompt)
           except RateLimitError:
               enrich_span({"retry.attempt": attempt + 1})
               time.sleep(2 ** attempt)  # Exponential backoff
           except Exception as e:
               enrich_span({"error.type": type(e).__name__})
               raise

**4. Monitor Token Usage**

.. code-block:: python

   @trace(tracer=tracer)
   def cost_aware_llm_call(prompt: str):
       response = client.chat.completions.create(...)
       
       enrich_span({
           "tokens.prompt": response.usage.prompt_tokens,
           "tokens.completion": response.usage.completion_tokens,
           "tokens.total": response.usage.total_tokens,
           "cost.estimated_usd": calculate_cost(response.usage)
       })

Environment Variables for Multiple Providers
---------------------------------------------

Use environment variables to manage multiple API keys:

.. code-block:: bash

   # .env file
   HH_API_KEY=your-honeyhive-key
   HH_PROJECT=multi-llm-app
   
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   GOOGLE_API_KEY=your-google-key

Complete Example: Multi-LLM Content Pipeline
---------------------------------------------

Here's a complete example using multiple providers with both instrumentor options:

**Using OpenInference (Lightweight):**

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import openai
   import anthropic
   
   # Initialize with OpenInference instrumentors
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       instrumentors=[OpenAIInstrumentor(), AnthropicInstrumentor()]
   )

**Using OpenLLMetry (Enhanced Metrics):**

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
   import openai
   import anthropic
   
   # Initialize with OpenLLMetry instrumentors
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       instrumentors=[OpenAIInstrumentor(), AnthropicInstrumentor()]
   )

**The pipeline functions are identical regardless of instrumentor choice:**

.. code-block:: python

   @trace(tracer=tracer, event_type="content_outline")
   def generate_outline(topic: str) -> str:
       """Generate content outline using GPT-4."""
       client = openai.OpenAI()
       
       enrich_span({"content.topic": topic, "step": "outline"})
       
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": "Create a detailed outline for a blog post."},
               {"role": "user", "content": f"Topic: {topic}"}
           ]
       )
       
       return response.choices[0].message.content
   
   @trace(tracer=tracer, event_type="content_writing")
   def write_content(outline: str) -> str:
       """Write content using Claude."""
       client = anthropic.Anthropic()
       
       enrich_span({"step": "writing", "outline_length": len(outline)})
       
       response = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=2000,
           messages=[
               {"role": "user", "content": f"Write a blog post based on this outline:\\n{outline}"}
           ]
       )
       
       return response.content[0].text
   
   @trace(tracer=tracer, event_type="content_review")
   def review_content(content: str) -> dict:
       """Review content quality using GPT-3.5."""
       client = openai.OpenAI()
       
       enrich_span({"step": "review", "content_length": len(content)})
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "Review this content for quality, clarity, and engagement. Provide a score and suggestions."},
               {"role": "user", "content": content}
           ]
       )
       
       review = response.choices[0].message.content
       
       return {
           "review": review,
           "content_score": extract_score(review),  # Custom function
           "review_length": len(review)
       }
   
   @trace(tracer=tracer, event_type="content_pipeline")
   def create_blog_post(topic: str) -> dict:
       """Complete content creation pipeline."""
       
       enrich_span({
           "pipeline.topic": topic,
           "pipeline.steps": ["outline", "write", "review"],
           "pipeline.providers": ["openai", "anthropic"]
       })
       
       # Step 1: Generate outline with GPT-4
       outline = generate_outline(topic)
       
       # Step 2: Write content with Claude
       content = write_content(outline)
       
       # Step 3: Review with GPT-3.5
       review_result = review_content(content)
       
       result = {
           "topic": topic,
           "outline": outline,
           "content": content,
           "review": review_result,
           "pipeline_status": "completed"
       }
       
       enrich_span({
           "pipeline.final_score": review_result["content_score"],
           "pipeline.total_length": len(content),
           "pipeline.success": True
       })
       
       return result
   
   def extract_score(review_text: str) -> float:
       """Extract numeric score from review text (simplified)."""
       # This would use regex or LLM to extract the actual score
       return 8.5  # Placeholder
   
   # Usage - all LLM calls automatically traced!
   if __name__ == "__main__":
       result = create_blog_post("The Future of AI in Healthcare")
       print(f"Content pipeline completed with score: {result['review']['content_score']}")

What's Next?
------------

You now have comprehensive LLM tracing set up! Next steps:

- :doc:`04-evaluation-basics` - Start evaluating your LLM outputs
- :doc:`../how-to/index` - Advanced integration patterns
- :doc:`../explanation/concepts/llm-observability` - Understand LLM observability concepts

Key Takeaways
-------------

- **BYOI Architecture**: Use any OpenTelemetry-compatible instrumentor
- **Zero Code Changes**: Existing LLM calls work without modification
- **Multiple Providers**: Mix OpenAI, Anthropic, Google AI, Google ADK, and others
- **Rich Context**: Automatic capture of prompts, responses, and metadata
- **Business Context**: Add custom attributes with ``enrich_span()``
- **Error Handling**: Automatic capture of rate limits and API errors

.. tip::
   Start with one LLM provider and the basic instrumentor, then add business context and additional providers as needed. The goal is comprehensive observability with minimal development overhead!

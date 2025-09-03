Integrate with Google AI
========================

Learn how to integrate HoneyHive with Google AI's Gemini models using the BYOI (Bring Your Own Instrumentor) approach.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

Google AI offers powerful Gemini models through the `google-generativeai` library. HoneyHive provides automatic tracing through OpenInference instrumentors with zero code changes to your existing Google AI implementations.

**Benefits**:
- **Automatic Tracing**: All Gemini API calls traced automatically
- **Rich Context**: Model parameters, token usage, and performance metrics
- **Multi-Modal Support**: Text, image, and code generation tracing
- **Zero Code Changes**: Works with existing Google AI code

Quick Start
-----------

**1. Install Required Packages**

.. code-block:: bash

   pip install honeyhive google-generativeai openinference-instrumentation-google-generativeai

**2. Initialize HoneyHive with Google AI Instrumentor**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor
   import google.generativeai as genai

   # Initialize HoneyHive tracer with Google AI instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       ,
       instrumentors=[GoogleGenerativeAIInstrumentor()]
   )

   # Configure Google AI
   genai.configure(api_key="your-google-ai-api-key")

**3. Use Google AI Normally - Automatically Traced**

.. code-block:: python

   # All Google AI calls are now automatically traced
   model = genai.GenerativeModel('gemini-pro')
   response = model.generate_content("What is machine learning?")
   print(response.text)

Basic Text Generation
---------------------

**Problem**: Trace basic text generation with Gemini Pro.

**Solution**:

.. code-block:: python

   import google.generativeai as genai
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.google_generativeai import GoogleGenerativeAIInstrumentor

   # Setup (do once at application startup)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       ,
       instrumentors=[GoogleGenerativeAIInstrumentor()]
   )

   genai.configure(api_key="your-google-ai-api-key")

   def generate_text(prompt: str, model_name: str = "gemini-pro") -> str:
       """Generate text with automatic tracing."""
       
       model = genai.GenerativeModel(model_name)
       
       # This call is automatically traced with:
       # - Model name and parameters
       # - Input prompt and token count
       # - Output text and token count
       # - Latency and performance metrics
       response = model.generate_content(prompt)
       
       return response.text

   # Usage examples
   result = generate_text("Explain quantum computing in simple terms")
   print(result)

   result = generate_text("Write a Python function to sort a list", "gemini-pro")
   print(result)

Chat Conversations
------------------

**Problem**: Trace multi-turn conversations with context.

**Solution**:

.. code-block:: python

   def chat_conversation():
       """Multi-turn chat conversation with automatic tracing."""
       
       model = genai.GenerativeModel('gemini-pro')
       chat = model.start_chat(history=[])
       
       # Each message is automatically traced
       response1 = chat.send_message("Hello! I'm learning about AI.")
       print("AI:", response1.text)
       
       response2 = chat.send_message("What should I learn first?")
       print("AI:", response2.text)
       
       response3 = chat.send_message("Can you give me a learning plan?")
       print("AI:", response3.text)
       
       return chat.history

   # Usage
   conversation_history = chat_conversation()

**Enhanced Chat with Custom Context**:

.. code-block:: python

   def enhanced_chat_session(user_id: str, topic: str):
       """Chat session with custom tracing context."""
       
       # Add custom context to the trace
       with tracer.start_span("chat_session") as span:
           span.set_attribute("user.id", user_id)
           span.set_attribute("chat.topic", topic)
           span.set_attribute("chat.model", "gemini-pro")
           
           model = genai.GenerativeModel('gemini-pro')
           chat = model.start_chat(history=[])
           
           # System prompt
           system_prompt = f"You are helping a user learn about {topic}. Be encouraging and provide practical advice."
           
           response = chat.send_message(system_prompt)
           span.set_attribute("chat.system_prompt_tokens", len(system_prompt.split()))
           
           return chat

   # Usage
   chat = enhanced_chat_session("user123", "machine learning")

Multi-Modal Generation
----------------------

**Problem**: Trace image and text multi-modal generation.

**Solution**:

.. code-block:: python

   import PIL.Image

   def analyze_image_with_text(image_path: str, question: str):
       """Analyze image with text prompt - automatically traced."""
       
       # Load image
       image = PIL.Image.open(image_path)
       
       # Use Gemini Pro Vision for multi-modal
       model = genai.GenerativeModel('gemini-pro-vision')
       
       # This multi-modal call is automatically traced with:
       # - Image metadata (size, format)
       # - Text prompt
       # - Model parameters
       # - Response content
       response = model.generate_content([question, image])
       
       return response.text

   def generate_content_from_description(description: str):
       """Generate detailed content from image description."""
       
       with tracer.start_span("content_generation") as span:
           span.set_attribute("content.type", "image_description")
           span.set_attribute("content.description_length", len(description))
           
           model = genai.GenerativeModel('gemini-pro')
           
           prompt = f"""
           Based on this image description: "{description}"
           
           Generate:
           1. A detailed scene analysis
           2. Possible context or story
           3. Key visual elements to notice
           """
           
           response = model.generate_content(prompt)
           span.set_attribute("content.generated_length", len(response.text))
           
           return response.text

   # Usage examples
   result = analyze_image_with_text("photo.jpg", "What's happening in this image?")
   content = generate_content_from_description("A busy street market with colorful fruits")

Advanced Configuration
----------------------

**Problem**: Configure Gemini models with specific parameters and trace the configurations.

**Solution**:

.. code-block:: python

   def advanced_generation(prompt: str, **config):
       """Advanced generation with custom configuration tracing."""
       
       # Configuration options
       generation_config = genai.types.GenerationConfig(
           candidate_count=config.get('candidate_count', 1),
           stop_sequences=config.get('stop_sequences', []),
           max_output_tokens=config.get('max_output_tokens', 1024),
           temperature=config.get('temperature', 0.7),
           top_p=config.get('top_p', 0.8),
           top_k=config.get('top_k', 40)
       )
       
       safety_settings = config.get('safety_settings', [])
       
       with tracer.start_span("advanced_generation") as span:
           # Log configuration for observability
           span.set_attribute("config.temperature", generation_config.temperature)
           span.set_attribute("config.max_tokens", generation_config.max_output_tokens)
           span.set_attribute("config.top_p", generation_config.top_p)
           span.set_attribute("config.top_k", generation_config.top_k)
           span.set_attribute("config.safety_settings_count", len(safety_settings))
           
           model = genai.GenerativeModel('gemini-pro')
           
           # Generate with custom configuration
           response = model.generate_content(
               prompt,
               generation_config=generation_config,
               safety_settings=safety_settings
           )
           
           span.set_attribute("response.finish_reason", getattr(response, 'finish_reason', 'unknown'))
           
           return response.text

   # Usage with different configurations
   creative_config = {
       'temperature': 0.9,
       'top_p': 0.95,
       'max_output_tokens': 2048
   }

   factual_config = {
       'temperature': 0.1,
       'top_p': 0.1,
       'max_output_tokens': 512
   }

   creative_result = advanced_generation("Write a creative story about AI", **creative_config)
   factual_result = advanced_generation("What is the capital of France?", **factual_config)

Error Handling and Reliability
------------------------------

**Problem**: Handle Google AI API errors gracefully while maintaining tracing.

**Solution**:

.. code-block:: python

   import google.generativeai as genai
   from google.api_core import exceptions as google_exceptions

   def reliable_generation(prompt: str, max_retries: int = 3):
       """Reliable generation with error handling and tracing."""
       
       model = genai.GenerativeModel('gemini-pro')
       
       for attempt in range(max_retries):
           try:
               with tracer.start_span(f"generation_attempt_{attempt + 1}") as span:
                   span.set_attribute("attempt.number", attempt + 1)
                   span.set_attribute("attempt.max_retries", max_retries)
                   
                   # This will be traced automatically, including errors
                   response = model.generate_content(prompt)
                   
                   span.set_attribute("attempt.success", True)
                   return response.text
                   
           except google_exceptions.ResourceExhausted as e:
               # Rate limit error
               span.set_attribute("attempt.success", False)
               span.set_attribute("error.type", "rate_limit")
               span.set_attribute("error.message", str(e))
               
               if attempt < max_retries - 1:
                   wait_time = 2 ** attempt  # Exponential backoff
                   span.set_attribute("retry.wait_seconds", wait_time)
                   time.sleep(wait_time)
               else:
                   raise
                   
           except google_exceptions.InvalidArgument as e:
               # Invalid input error
               span.set_attribute("attempt.success", False)
               span.set_attribute("error.type", "invalid_argument")
               span.set_attribute("error.message", str(e))
               raise  # Don't retry invalid arguments
               
           except Exception as e:
               # Other errors
               span.set_attribute("attempt.success", False)
               span.set_attribute("error.type", type(e).__name__)
               span.set_attribute("error.message", str(e))
               
               if attempt < max_retries - 1:
                   time.sleep(1)
               else:
                   raise

   # Usage
   try:
       result = reliable_generation("Explain machine learning")
       print(result)
   except Exception as e:
       print(f"Generation failed: {e}")

Performance Monitoring
----------------------

**Problem**: Monitor and optimize Google AI performance across different models.

**Solution**:

.. code-block:: python

   import time
   from typing import Dict, Any

   def benchmark_models(prompt: str, models: list = None) -> Dict[str, Any]:
       """Benchmark different Gemini models with detailed tracing."""
       
       if models is None:
           models = ["gemini-pro", "gemini-pro-vision"]
       
       results = {}
       
       with tracer.start_span("model_benchmark") as benchmark_span:
           benchmark_span.set_attribute("benchmark.prompt", prompt)
           benchmark_span.set_attribute("benchmark.models_count", len(models))
           
           for model_name in models:
               with tracer.start_span(f"benchmark_{model_name}") as model_span:
                   model_span.set_attribute("model.name", model_name)
                   
                   start_time = time.time()
                   
                   try:
                       model = genai.GenerativeModel(model_name)
                       response = model.generate_content(prompt)
                       
                       end_time = time.time()
                       latency = end_time - start_time
                       
                       # Record performance metrics
                       model_span.set_attribute("performance.latency_ms", latency * 1000)
                       model_span.set_attribute("performance.response_length", len(response.text))
                       model_span.set_attribute("performance.chars_per_second", len(response.text) / latency)
                       model_span.set_attribute("benchmark.success", True)
                       
                       results[model_name] = {
                           "response": response.text,
                           "latency_ms": latency * 1000,
                           "chars_per_second": len(response.text) / latency,
                           "success": True
                       }
                       
                   except Exception as e:
                       end_time = time.time()
                       latency = end_time - start_time
                       
                       model_span.set_attribute("performance.latency_ms", latency * 1000)
                       model_span.set_attribute("benchmark.success", False)
                       model_span.set_attribute("benchmark.error", str(e))
                       
                       results[model_name] = {
                           "error": str(e),
                           "latency_ms": latency * 1000,
                           "success": False
                       }
           
           # Summary metrics
           successful_models = [k for k, v in results.items() if v.get("success")]
           benchmark_span.set_attribute("benchmark.successful_models", len(successful_models))
           benchmark_span.set_attribute("benchmark.success_rate", len(successful_models) / len(models))
           
           return results

   # Usage
   benchmark_results = benchmark_models("Explain quantum computing briefly")
   for model, result in benchmark_results.items():
       if result.get("success"):
           print(f"{model}: {result['latency_ms']:.0f}ms, {result['chars_per_second']:.0f} chars/sec")
       else:
           print(f"{model}: Failed - {result['error']}")

Environment Configuration
-------------------------

**Problem**: Manage Google AI credentials and settings across environments.

**Solution**:

.. code-block:: python

   import os
   from typing import Optional

   def setup_google_ai_environment(
       honeyhive_api_key: Optional[str] = None,
       google_api_key: Optional[str] = None,
       project_name: Optional[str] = None,
       environment: str = "development"
   ):
       """Setup Google AI with HoneyHive for different environments."""
       
       # Use environment variables if not provided
       honeyhive_key = honeyhive_api_key or os.getenv("HH_API_KEY")
       google_key = google_api_key or os.getenv("GOOGLE_API_KEY")
       project = project_name or os.getenv("HH_PROJECT", f"google-ai-{environment}")
       
       if not honeyhive_key:
           raise ValueError("HoneyHive API key required (HH_API_KEY)")
       if not google_key:
           raise ValueError("Google API key required (GOOGLE_API_KEY)")
       
       # Initialize HoneyHive with environment-specific settings
       tracer_config = {
           "api_key": honeyhive_key,
           "project": project,
           "source": environment,
           "instrumentors": [GoogleGenerativeAIInstrumentor()]
       }
       
       # Environment-specific configuration
       if environment == "production":
           tracer_config["disable_http_tracing"] = False  # Enable full tracing
       elif environment == "development":
           tracer_config["test_mode"] = True  # Enable debug mode
       
       tracer = HoneyHiveTracer.init(**tracer_config)
       
       # Configure Google AI
       genai.configure(api_key=google_key)
       
       with tracer.start_span("environment_setup") as span:
           span.set_attribute("environment", environment)
           span.set_attribute("project", project)
           span.set_attribute("google_ai.configured", True)
       
       return tracer

   # Usage for different environments
   
   # Development
   dev_tracer = setup_google_ai_environment(environment="development")
   
   # Production
   prod_tracer = setup_google_ai_environment(environment="production")

Best Practices
--------------

**1. Model Selection**

.. code-block:: python

   # Choose the right model for your use case
   def choose_model(task_type: str) -> str:
       model_mapping = {
           "text_generation": "gemini-pro",
           "image_analysis": "gemini-pro-vision",
           "code_generation": "gemini-pro",
           "conversation": "gemini-pro"
       }
       return model_mapping.get(task_type, "gemini-pro")

**2. Prompt Engineering**

.. code-block:: python

   # Structure prompts for better tracing and results
   def structured_prompt(task: str, context: str, constraints: str = "") -> str:
       prompt = f"""
       Task: {task}
       
       Context: {context}
       
       {f"Constraints: {constraints}" if constraints else ""}
       
       Response:
       """
       return prompt.strip()

**3. Error Recovery**

.. code-block:: python

   # Always implement graceful error handling
   def safe_generation(prompt: str, fallback_response: str = "Unable to generate response"):
       try:
           model = genai.GenerativeModel('gemini-pro')
           response = model.generate_content(prompt)
           return response.text
       except Exception as e:
           # Error is automatically traced
           return fallback_response

**4. Resource Management**

.. code-block:: python

   # Reuse model instances for better performance
   class GoogleAIManager:
       def __init__(self):
           self.models = {}
       
       def get_model(self, model_name: str):
           if model_name not in self.models:
               self.models[model_name] = genai.GenerativeModel(model_name)
           return self.models[model_name]

Common Issues & Solutions
-------------------------

**Issue 1: Authentication Errors**

.. code-block:: python

   # Verify API key setup
   try:
       genai.configure(api_key="your-api-key")
       model = genai.GenerativeModel('gemini-pro')
       test_response = model.generate_content("Hello")
       print("✅ Google AI configured successfully")
   except Exception as e:
       print(f"❌ Configuration failed: {e}")

**Issue 2: Rate Limiting**

.. code-block:: python

   # Implement exponential backoff
   import time
   from random import uniform

   def rate_limited_call(func, *args, **kwargs):
       max_retries = 3
       base_delay = 1
       
       for attempt in range(max_retries):
           try:
               return func(*args, **kwargs)
           except google_exceptions.ResourceExhausted:
               if attempt < max_retries - 1:
                   delay = base_delay * (2 ** attempt) + uniform(0, 1)
                   time.sleep(delay)
               else:
                   raise

**Issue 3: Large Response Handling**

.. code-block:: python

   # Handle potentially large responses
   def generate_with_limits(prompt: str, max_tokens: int = 1024):
       generation_config = genai.types.GenerationConfig(
           max_output_tokens=max_tokens
       )
       
       model = genai.GenerativeModel('gemini-pro')
       response = model.generate_content(
           prompt, 
           generation_config=generation_config
       )
       
       return response.text

See Also
--------

- :doc:`multi-provider` - Use Google AI with other providers
- :doc:`../troubleshooting` - Common integration issues
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
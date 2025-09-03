Integrate with AWS Bedrock
==========================

Learn how to integrate HoneyHive with AWS Bedrock's diverse model ecosystem using the BYOI (Bring Your Own Instrumentor) approach.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

AWS Bedrock provides access to multiple foundation models through a unified API, including Claude (Anthropic), Titan (Amazon), Jurassic (AI21), and others. HoneyHive provides automatic tracing through OpenInference instrumentors with zero code changes to your existing Bedrock implementations.

**Benefits**:
- **Multi-Model Support**: Trace all Bedrock models consistently
- **Automatic Tracing**: All Bedrock API calls traced automatically
- **AWS Integration**: Native integration with AWS infrastructure
- **Rich Context**: Model parameters, costs, and performance metrics
- **Enterprise Ready**: Built for enterprise security and compliance

Supported Models
----------------

AWS Bedrock supports multiple model providers:

**Available Providers:**

- **Anthropic**: Claude 3 (Haiku, Sonnet, Opus) - Conversation, analysis, coding
- **Amazon**: Titan Text/Embeddings - Content generation, search  
- **AI21 Labs**: Jurassic-2 - Text generation, summarization
- **Cohere**: Command/Embed - Generation, embeddings
- **Meta**: Llama 2 - Open-source text generation
- **Stability AI**: Stable Diffusion - Image generation

Quick Start
-----------

**1. Install Required Packages**

.. code-block:: bash

   pip install honeyhive boto3 openinference-instrumentation-bedrock

**2. Configure AWS Credentials**

.. code-block:: bash

   # Option 1: AWS CLI
   aws configure
   
   # Option 2: Environment variables
   export AWS_ACCESS_KEY_ID=your-access-key
   export AWS_SECRET_ACCESS_KEY=your-secret-key
   export AWS_DEFAULT_REGION=us-east-1

**3. Initialize HoneyHive with Bedrock Instrumentor**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.bedrock import BedrockInstrumentor
   import boto3
   import json

   # Initialize HoneyHive tracer with Bedrock instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       instrumentors=[BedrockInstrumentor()]
   )

   # Create Bedrock client
   bedrock_runtime = boto3.client(
       "bedrock-runtime",
       region_name="us-east-1"
   )

**4. Use Bedrock Normally - Automatically Traced**

.. code-block:: python

   # All Bedrock calls are now automatically traced
   request = {
       "prompt": "\n\nHuman: What is machine learning?\n\nAssistant:",
       "max_tokens_to_sample": 100,
       "temperature": 0.1
   }

   response = bedrock_runtime.invoke_model(
       modelId="anthropic.claude-v2",
       body=json.dumps(request),
       contentType="application/json"
   )

   result = json.loads(response["body"].read())
   print(result["completion"])

Claude Integration
------------------

**Problem**: Use Claude models through Bedrock with automatic tracing.

**Solution**:

.. code-block:: python

   import boto3
   import json
   from typing import List, Dict, Any

   def claude_bedrock_chat(
       messages: List[Dict[str, str]], 
       model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
       max_tokens: int = 1000,
       temperature: float = 0.7
   ) -> str:
       """Chat with Claude through Bedrock with automatic tracing."""
       
       bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
       
       # Format for Claude 3
       request = {
           "anthropic_version": "bedrock-2023-05-31",
           "max_tokens": max_tokens,
           "temperature": temperature,
           "messages": messages
       }
       
       # This call is automatically traced with:
       # - Model ID and parameters
       # - Input messages and token estimates
       # - Output text and actual token usage
       # - Latency and cost information
       response = bedrock_runtime.invoke_model(
           modelId=model_id,
           body=json.dumps(request),
           contentType="application/json"
       )
       
       result = json.loads(response["body"].read())
       return result["content"][0]["text"]

   def claude_conversation_example():
       """Example conversation with automatic tracing."""
       
       # Single-turn
       messages = [
           {"role": "user", "content": "Explain quantum computing simply"}
       ]
       response = claude_bedrock_chat(messages)
       print("Claude:", response)
       
       # Multi-turn conversation
       messages = [
           {"role": "user", "content": "What is machine learning?"},
           {"role": "assistant", "content": "Machine learning is a subset of AI..."},
           {"role": "user", "content": "What are the main types?"}
       ]
       response = claude_bedrock_chat(messages, temperature=0.3)
       print("Claude:", response)

   # Usage
   claude_conversation_example()

Amazon Titan Integration
------------------------

**Problem**: Use Amazon Titan models for text generation and embeddings.

**Solution**:

.. code-block:: python

   def titan_text_generation(
       prompt: str,
       model_id: str = "amazon.titan-text-express-v1",
       max_tokens: int = 200,
       temperature: float = 0.7
   ) -> str:
       """Generate text with Amazon Titan."""
       
       bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
       
       request = {
           "inputText": prompt,
           "textGenerationConfig": {
               "maxTokenCount": max_tokens,
               "temperature": temperature,
               "topP": 0.9,
               "stopSequences": []
           }
       }
       
       # Automatically traced
       response = bedrock_runtime.invoke_model(
           modelId=model_id,
           body=json.dumps(request),
           contentType="application/json"
       )
       
       result = json.loads(response["body"].read())
       return result["results"][0]["outputText"]

   def titan_embeddings(
       text: str,
       model_id: str = "amazon.titan-embed-text-v1"
   ) -> List[float]:
       """Generate embeddings with Amazon Titan."""
       
       bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
       
       request = {
           "inputText": text
       }
       
       # Automatically traced
       response = bedrock_runtime.invoke_model(
           modelId=model_id,
           body=json.dumps(request),
           contentType="application/json"
       )
       
       result = json.loads(response["body"].read())
       return result["embedding"]

   # Usage examples
   text_result = titan_text_generation("Explain the benefits of cloud computing")
   embeddings = titan_embeddings("This is a sample text for embedding")
   print(f"Generated text: {text_result}")
   print(f"Embedding dimensions: {len(embeddings)}")

Multi-Model Comparison
----------------------

**Problem**: Compare different models on the same task with performance tracking.

**Solution**:

.. code-block:: python

   import time
   from typing import Dict, Any

   def compare_bedrock_models(prompt: str) -> Dict[str, Any]:
       """Compare multiple Bedrock models with automatic tracing."""
       
       bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
       
       models = [
           {
               "id": "anthropic.claude-3-haiku-20240307-v1:0",
               "name": "Claude 3 Haiku",
               "type": "claude",
               "cost_per_1k_tokens": 0.00025
           },
           {
               "id": "anthropic.claude-3-sonnet-20240229-v1:0", 
               "name": "Claude 3 Sonnet",
               "type": "claude",
               "cost_per_1k_tokens": 0.003
           },
           {
               "id": "amazon.titan-text-express-v1",
               "name": "Titan Text Express",
               "type": "titan",
               "cost_per_1k_tokens": 0.0013
           }
       ]
       
       from honeyhive import trace, enrich_span, set_default_tracer
       
       set_default_tracer(tracer)
       
       @trace(event_type=EventType.model)
       def test_single_model(model: dict, prompt: str) -> dict:
           """Test a single model - automatically traced."""
           enrich_span({
               "model.id": model["id"],
               "model.name": model["name"],
               "model.type": model["type"],
               "prompt.length": len(prompt)
           })
           
           # Model testing logic here
           result = {"model": model["name"], "response": f"Response for {prompt[:50]}..."}
           
           enrich_span({
               "response.length": len(result["response"]),
               "test.success": True
           })
           
           return result
       
       @trace(event_type=EventType.chain)
       def compare_models(models: list, prompt: str) -> dict:
           """Compare multiple models - automatically traced with individual model calls."""
           enrich_span({
               "comparison.prompt": prompt,
               "comparison.models_count": len(models)
           })
           
           results = {}
           
           # Each model test is automatically traced
           for model in models:
               result = test_single_model(model, prompt)
               results[model["name"]] = result
           
           enrich_span({
               "comparison.completed_tests": len(results),
               "comparison.success": True
           })
           
           return results
       
               # Usage
        comparison_results = compare_models(models, "Explain quantum computing")

Streaming Support
-----------------

AWS Bedrock supports streaming responses for real-time applications:

.. code-block:: python

   import boto3
   from honeyhive import trace
   from honeyhive.models import EventType
   
   @trace(event_type=EventType.model)
   def stream_bedrock_response(prompt: str):
       """Stream response from AWS Bedrock."""
       bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
       
       request = {
           "anthropic_version": "bedrock-2023-05-31",
           "max_tokens": 200,
           "temperature": 0.7,
           "messages": [{"role": "user", "content": prompt}]
       }
       
       response = bedrock_runtime.invoke_model_with_response_stream(
           modelId="anthropic.claude-3-sonnet-20240229-v1:0",
           body=json.dumps(request),
           contentType="application/json"
       )
       
       # Process streaming response
       for event in response.get('body'):
           chunk = json.loads(event['chunk']['bytes'].decode())
           if chunk.get('type') == 'content_block_delta':
               yield chunk['delta']['text']

Production Considerations
-------------------------

**1. Error Handling**

.. code-block:: python

   @trace(event_type=EventType.model)
   def robust_bedrock_call(prompt: str, max_retries: int = 3):
       """Robust Bedrock call with retry logic."""
       for attempt in range(max_retries):
           try:
               return bedrock_generate(prompt)
           except Exception as e:
               if attempt == max_retries - 1:
                   raise
               time.sleep(2 ** attempt)  # Exponential backoff

**2. Cost Optimization**

.. code-block:: python

   @trace(event_type=EventType.model)
   def cost_optimized_call(prompt: str):
       """Optimize costs by choosing appropriate model."""
       # Use cheaper model for simple tasks
       if len(prompt) < 100:
           model_id = "amazon.titan-text-lite-v1"
       else:
           model_id = "anthropic.claude-3-haiku-20240307-v1:0"
       
       return bedrock_runtime.invoke_model(
           modelId=model_id,
           body=json.dumps({"inputText": prompt})
       )

See Also
--------

- :doc:`multi-provider` - Use AWS Bedrock with other providers
- :doc:`../troubleshooting` - Common integration issues
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
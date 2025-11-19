#!/usr/bin/env python3
"""
Template generation script for multi-instrumentor provider integration documentation.

This script generates provider-specific integration documentation using the formal
template system defined in multi_instrumentor_integration_formal_template.rst.

Compatibility data is loaded from provider_compatibility.yaml to separate data from code.

Usage:
    python generate_provider_docs.py --provider anthropic
    python generate_provider_docs.py --provider google-ai --output custom_output.rst
    python generate_provider_docs.py --all  # Regenerate all providers
    python generate_provider_docs.py --validate  # Validate compatibility data
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, List


# Provider-specific variable definitions
PROVIDER_CONFIGS = {
    "openai": {
        "PROVIDER_NAME": "OpenAI",
        "PROVIDER_KEY": "openai",
        "PROVIDER_MODULE": "openai",
        "PROVIDER_SDK": "openai>=1.0.0",
        "PROVIDER_EXCEPTION": "openai.OpenAIError",
        "PROVIDER_API_KEY_NAME": "OPENAI_API_KEY",
        "OPENINFERENCE_PACKAGE": "openinference-instrumentation-openai",
        "OPENINFERENCE_IMPORT": "openinference.instrumentation.openai",
        "OPENINFERENCE_CLASS": "OpenAIInstrumentor",
        "TRACELOOP_PACKAGE": "opentelemetry-instrumentation-openai",
        "TRACELOOP_IMPORT": "opentelemetry.instrumentation.openai",
        "TRACELOOP_CLASS": "OpenAIInstrumentor",
        "BASIC_USAGE_EXAMPLE": """client = openai.OpenAI()  # Uses OPENAI_API_KEY automatically
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": "Hello!"}]
       )
       print(response.choices[0].message.content)""",
        "ADVANCED_FUNCTION_NAME": "multi_model_comparison",
        "ADVANCED_FUNCTION_PARAMS": "prompt: str",
        "ADVANCED_USAGE_EXAMPLE": "client = openai.OpenAI()",
        "ADVANCED_IMPLEMENTATION": """# Test multiple OpenAI models
       models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
       
       results = []
       for model in models:
           try:
               # Generate response with current model
               response = client.chat.completions.create(
                   model=model,
                   messages=[{"role": "user", "content": prompt}],
                   max_tokens=150
               )
               
               results.append({
                   "model": model,
                   "response": response.choices[0].message.content,
                   "usage": response.usage.dict() if response.usage else None
               })
               
           except Exception as model_error:
               results.append({
                   "model": model,
                   "error": str(model_error)
               })
       
       # Add result metadata
       enrich_span({
           "business.successful": True,
           "openai.models_used": models,
           "business.result_confidence": "high"
       })
       
       return {
           "prompt": prompt,
           "model_results": results,
           "comparison_completed": True
       }""",
        "RETURN_VALUE": """{
           "prompt": prompt,
           "model_results": results,
           "comparison_completed": True
       }""",
        "ADDITIONAL_ENV_CONFIG": """# OPENAI_API_KEY=your-openai-api-key
# OPENAI_ORG_ID=your-org-id  # Optional""",
        "MULTIPLE_INSTRUMENTORS_EXAMPLE": """from openinference.instrumentation.openai import OpenAIInstrumentor
       from openinference.instrumentation.anthropic import AnthropicInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       openai_instrumentor = OpenAIInstrumentor()
       anthropic_instrumentor = AnthropicInstrumentor()
       
       openai_instrumentor.instrument(tracer_provider=tracer.provider)
       anthropic_instrumentor.instrument(tracer_provider=tracer.provider)""",
        "MULTIPLE_TRACELOOP_INSTRUMENTORS_EXAMPLE": """from opentelemetry.instrumentation.openai import OpenAIInstrumentor
       from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       openai_instrumentor = OpenAIInstrumentor()      # Traceloop OpenAI
       anthropic_instrumentor = AnthropicInstrumentor() # Traceloop Anthropic
       
       openai_instrumentor.instrument(tracer_provider=tracer.provider)
       anthropic_instrumentor.instrument(tracer_provider=tracer.provider)""",
        "USE_CASE_NAME": "model_comparison",
        "STRATEGY_NAME": "multi_model_analysis",
        "MODELS_USED": '["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]',
        "FIRST_PARAM": "prompt",
        "SEE_ALSO_LINKS": """- :doc:`multi-provider` - Use OpenAI with other providers
- :doc:`../llm-application-patterns` - LLM agent architectures and patterns
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
- :doc:`anthropic` - Similar integration for Anthropic Claude""",
    },
    "anthropic": {
        "PROVIDER_NAME": "Anthropic",
        "PROVIDER_KEY": "anthropic",
        "PROVIDER_MODULE": "anthropic",
        "PROVIDER_SDK": "anthropic>=0.17.0",
        "PROVIDER_EXCEPTION": "anthropic.APIError",
        "PROVIDER_API_KEY_NAME": "ANTHROPIC_API_KEY",
        "OPENINFERENCE_PACKAGE": "openinference-instrumentation-anthropic",
        "OPENINFERENCE_IMPORT": "openinference.instrumentation.anthropic",
        "OPENINFERENCE_CLASS": "AnthropicInstrumentor",
        "TRACELOOP_PACKAGE": "opentelemetry-instrumentation-anthropic",
        "TRACELOOP_IMPORT": "opentelemetry.instrumentation.anthropic",
        "TRACELOOP_CLASS": "AnthropicInstrumentor",
        "BASIC_USAGE_EXAMPLE": """client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY automatically
       response = client.messages.create(
           model="claude-3-sonnet-20240229",
           max_tokens=1000,
           messages=[{"role": "user", "content": "Hello!"}]
       )
       print(response.content[0].text)""",
        "ADVANCED_FUNCTION_NAME": "analyze_document",
        "ADVANCED_FUNCTION_PARAMS": "document: str",
        "ADVANCED_USAGE_EXAMPLE": "client = anthropic.Anthropic()",
        "USE_CASE_NAME": "document_analysis",
        "STRATEGY_NAME": "claude_reasoning",
        "MODELS_USED": '["claude-3-sonnet-20240229", "claude-3-opus-20240229"]',
        "FIRST_PARAM": "document",
        "RETURN_VALUE": '{"summary": summary_response.content[0].text, "analysis": analysis_response.content[0].text}',
        "ADVANCED_IMPLEMENTATION": """# First call: Quick summary with Claude Sonnet
           summary_response = client.messages.create(
               model="claude-3-sonnet-20240229",
               max_tokens=500,
               messages=[{
                   "role": "user", 
                   "content": f"Provide a brief summary of this document: {document}"
               }]
           )
           
           # Second call: Detailed analysis with Claude Opus
           analysis_response = client.messages.create(
               model="claude-3-opus-20240229",
               max_tokens=1000,
               messages=[{
                   "role": "user",
                   "content": f"Provide detailed analysis with insights: {document}"
               }]
           )""",
        "ADDITIONAL_ENV_CONFIG": "",
        "MULTIPLE_INSTRUMENTORS_EXAMPLE": """from openinference.instrumentation.anthropic import AnthropicInstrumentor
       from openinference.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       anthropic_instrumentor = AnthropicInstrumentor()
       openai_instrumentor = OpenAIInstrumentor()
       
       anthropic_instrumentor.instrument(tracer_provider=tracer.provider)
       openai_instrumentor.instrument(tracer_provider=tracer.provider)""",
        "MULTIPLE_TRACELOOP_INSTRUMENTORS_EXAMPLE": """from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
       from opentelemetry.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       anthropic_instrumentor = AnthropicInstrumentor()      # Traceloop Anthropic
       openai_instrumentor = OpenAIInstrumentor()          # Traceloop OpenAI
       
       anthropic_instrumentor.instrument(tracer_provider=tracer.provider)
       openai_instrumentor.instrument(tracer_provider=tracer.provider)""",
        "SEE_ALSO_LINKS": """- :doc:`multi-provider` - Use Anthropic with other providers
- :doc:`../llm-application-patterns` - LLM agent architectures and patterns
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
- :doc:`openai` - Similar integration for OpenAI GPT""",
    },
    "google-ai": {
        "PROVIDER_NAME": "Google AI",
        "PROVIDER_KEY": "google-ai",
        "PROVIDER_MODULE": "google.generativeai",
        "PROVIDER_SDK": "google-generativeai>=0.3.0",
        "PROVIDER_EXCEPTION": "google.generativeai.types.GoogleGenerativeAIError",
        "PROVIDER_API_KEY_NAME": "GOOGLE_API_KEY",
        "OPENINFERENCE_PACKAGE": "openinference-instrumentation-google-generativeai",
        "OPENINFERENCE_IMPORT": "openinference.instrumentation.google_generativeai",
        "OPENINFERENCE_CLASS": "GoogleGenerativeAIInstrumentor",
        "TRACELOOP_PACKAGE": "opentelemetry-instrumentation-google-generativeai",
        "TRACELOOP_IMPORT": "opentelemetry.instrumentation.google_generativeai",
        "TRACELOOP_CLASS": "GoogleGenerativeAIInstrumentor",
        "BASIC_USAGE_EXAMPLE": """import google.generativeai as genai
       genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
       model = genai.GenerativeModel('gemini-pro')
       response = model.generate_content("Hello!")
       print(response.text)""",
        "ADVANCED_FUNCTION_NAME": "generate_content_comparison",
        "ADVANCED_FUNCTION_PARAMS": "prompt: str",
        "USE_CASE_NAME": "content_generation",
        "STRATEGY_NAME": "multi_model_gemini",
        "MODELS_USED": '["gemini-pro", "gemini-pro-vision"]',
        "FIRST_PARAM": "prompt",
        "SEE_ALSO_LINKS": """- :doc:`multi-provider` - Use Google AI with other providers
- :doc:`../llm-application-patterns` - LLM agent architectures and patterns
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
- :doc:`openai` - Similar integration for OpenAI GPT""",
    },
    "google-adk": {
        "PROVIDER_NAME": "Google Agent Development Kit (ADK)",
        "PROVIDER_KEY": "google-adk",
        "PROVIDER_MODULE": "google.adk",
        "PROVIDER_SDK": "google-adk>=1.0.0",
        "PROVIDER_EXCEPTION": "google.adk.ADKError",
        "PROVIDER_API_KEY_NAME": "GOOGLE_API_KEY",
        "OPENINFERENCE_PACKAGE": "openinference-instrumentation-google-adk",
        "OPENINFERENCE_IMPORT": "openinference.instrumentation.google_adk",
        "OPENINFERENCE_CLASS": "GoogleADKInstrumentor",
        "TRACELOOP_PACKAGE": "opentelemetry-instrumentation-google-adk",
        "TRACELOOP_IMPORT": "opentelemetry.instrumentation.google_adk",
        "TRACELOOP_CLASS": "GoogleADKInstrumentor",
        "TRACELOOP_AVAILABLE": False,
        "TRACELOOP_NOTE": "Traceloop does not currently provide a Google ADK instrumentor. Only OpenInference instrumentation is available for this provider.",
        "BASIC_USAGE_EXAMPLE": """agent = adk.Agent(
           name="document_processor",
           model="gemini-pro"
       )
       
       result = agent.run(
           task="Analyze this document",
           input_data={"document": document_content}
       )""",
        "ADVANCED_FUNCTION_NAME": "multi_agent_workflow",
        "ADVANCED_FUNCTION_PARAMS": "documents: List[str]",
        "ADVANCED_USAGE_EXAMPLE": """import google.adk as adk
       
       # Configure Google ADK
       adk.configure(api_key=os.getenv("GOOGLE_API_KEY"))""",
        "USE_CASE_NAME": "multi_agent_analysis",
        "STRATEGY_NAME": "parallel_processing",
        "MODELS_USED": '["gemini-pro", "gemini-ultra"]',
        "FIRST_PARAM": "documents",
        "RETURN_VALUE": """{"processed_documents": len(results), "analysis_results": results, "workflow_completed": True}""",
        "ADVANCED_IMPLEMENTATION": """# Create specialized agents
       analyzer = adk.Agent(
           name="document_analyzer", 
           model="gemini-pro",
           tools=["text_analysis", "summarization"]
       )
       
       reviewer = adk.Agent(
           name="quality_reviewer",
           model="gemini-ultra", 
           tools=["quality_check", "fact_verification"]
       )
       
       results = []
       for doc in documents:
           # Agent 1: Analyze document
           analysis = analyzer.run(
               task="Analyze document structure and content",
               input_data={"document": doc}
           )
           
           # Agent 2: Review analysis quality
           review = reviewer.run(
               task="Review analysis for accuracy and completeness", 
               input_data={"analysis": analysis.output}
           )
           
           results.append({
               "document": doc,
               "analysis": analysis.output,
               "review": review.output
           })
           
       # Add result metadata
       enrich_span({
           "business.successful": True,
           "google-adk.models_used": ["gemini-pro", "gemini-ultra"],
           "business.result_confidence": "high"
       })
       
       return {
           "processed_documents": len(results),
           "analysis_results": results,
           "workflow_completed": True
       }""",
        "ADDITIONAL_ENV_CONFIG": "",
        "MULTIPLE_INSTRUMENTORS_EXAMPLE": """from openinference.instrumentation.google_adk import GoogleADKInstrumentor
       from openinference.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               GoogleADKInstrumentor(),
               OpenAIInstrumentor()
           ]
       )""",
        "MULTIPLE_TRACELOOP_INSTRUMENTORS_EXAMPLE": """# Traceloop Google ADK instrumentor not available
       # Use OpenInference for Google ADK + Traceloop for other providers
       from openinference.instrumentation.google_adk import GoogleADKInstrumentor
       from opentelemetry.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               GoogleADKInstrumentor(),      # OpenInference (only option)
               OpenAIInstrumentor()          # Traceloop
           ]
       )""",
        "SEE_ALSO_LINKS": """- :doc:`multi-provider` - Use Google ADK with other providers
- :doc:`../llm-application-patterns` - LLM agent architectures and patterns
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
- :doc:`google-ai` - Similar integration for Google AI""",
    },
    "bedrock": {
        "PROVIDER_NAME": "AWS Bedrock",
        "PROVIDER_KEY": "bedrock",
        "PROVIDER_MODULE": "boto3",
        "PROVIDER_SDK": "boto3>=1.26.0",
        "PROVIDER_EXCEPTION": "botocore.exceptions.ClientError",
        "PROVIDER_API_KEY_NAME": "AWS_ACCESS_KEY_ID",
        "OPENINFERENCE_PACKAGE": "openinference-instrumentation-bedrock",
        "OPENINFERENCE_IMPORT": "openinference.instrumentation.bedrock",
        "OPENINFERENCE_CLASS": "BedrockInstrumentor",
        "TRACELOOP_PACKAGE": "opentelemetry-instrumentation-bedrock",
        "TRACELOOP_IMPORT": "opentelemetry.instrumentation.bedrock",
        "TRACELOOP_CLASS": "BedrockInstrumentor",
        "TRACELOOP_AVAILABLE": True,
        "BASIC_USAGE_EXAMPLE": """import boto3
       
       # Create Bedrock client
       bedrock = boto3.client(
           "bedrock-runtime",
           region_name="us-east-1"
       )
       
       # Invoke model
       response = bedrock.invoke_model(
           modelId="anthropic.claude-3-sonnet-20240229-v1:0",
           body=json.dumps({
               "anthropic_version": "bedrock-2023-05-31",
               "max_tokens": 1000,
               "messages": [{"role": "user", "content": "Hello from Bedrock!"}]
           })
       )""",
        "ADVANCED_FUNCTION_NAME": "multi_model_bedrock_workflow",
        "ADVANCED_FUNCTION_PARAMS": "prompts: List[str]",
        "ADVANCED_USAGE_EXAMPLE": """import boto3
       import json
       
       # Configure AWS Bedrock
       bedrock = boto3.client(
           "bedrock-runtime",
           region_name=os.getenv("AWS_REGION", "us-east-1")
       )""",
        "ADVANCED_IMPLEMENTATION": """# Test multiple Bedrock models
       models = [
           "anthropic.claude-3-sonnet-20240229-v1:0",
           "anthropic.claude-3-haiku-20240307-v1:0",
           "amazon.titan-text-express-v1"
       ]
       
       results = []
       for prompt in prompts:
           model_results = {}
           
           for model_id in models:
               try:
                   # Prepare request based on model type
                   if "anthropic" in model_id:
                       body = {
                           "anthropic_version": "bedrock-2023-05-31",
                           "max_tokens": 1000,
                           "messages": [{"role": "user", "content": prompt}]
                       }
                   elif "titan" in model_id:
                       body = {
                           "inputText": prompt,
                           "textGenerationConfig": {
                               "maxTokenCount": 1000,
                               "temperature": 0.7
                           }
                       }
                   
                   # Invoke model
                   response = bedrock.invoke_model(
                       modelId=model_id,
                       body=json.dumps(body)
                   )
                   
                   response_body = json.loads(response["body"].read())
                   model_results[model_id] = response_body
                   
               except Exception as e:
                   model_results[model_id] = {"error": str(e)}
           
           results.append({
               "prompt": prompt,
               "model_responses": model_results
           })""",
        "ADDITIONAL_ENV_CONFIG": """# AWS_ACCESS_KEY_ID=your-aws-access-key
# AWS_SECRET_ACCESS_KEY=your-aws-secret-key
# AWS_REGION=us-east-1""",
        "MULTIPLE_INSTRUMENTORS_EXAMPLE": """from openinference.instrumentation.bedrock import BedrockInstrumentor
       from openinference.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               BedrockInstrumentor(),
               OpenAIInstrumentor()
           ]
       )""",
        "MULTIPLE_TRACELOOP_INSTRUMENTORS_EXAMPLE": """from opentelemetry.instrumentation.bedrock import BedrockInstrumentor
       from opentelemetry.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               BedrockInstrumentor(),       # Traceloop Bedrock
               OpenAIInstrumentor()         # Traceloop OpenAI
           ]
       )""",
        "USE_CASE_NAME": "multi_model_analysis",
        "STRATEGY_NAME": "bedrock_model_comparison",
        "MODELS_USED": '["claude-3-sonnet", "claude-3-haiku", "titan-text"]',
        "FIRST_PARAM": "prompts",
        "SEE_ALSO_LINKS": """- :doc:`multi-provider` - Use Bedrock with other providers
- :doc:`../llm-application-patterns` - LLM agent architectures and patterns
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
- :doc:`anthropic` - Similar integration for Anthropic Claude""",
    },
    "azure-openai": {
        "PROVIDER_NAME": "Azure OpenAI",
        "PROVIDER_KEY": "azure-openai",
        "PROVIDER_MODULE": "openai",
        "PROVIDER_SDK": "openai>=1.0.0",
        "PROVIDER_EXCEPTION": "openai.APIError",
        "PROVIDER_API_KEY_NAME": "AZURE_OPENAI_API_KEY",
        "OPENINFERENCE_PACKAGE": "openinference-instrumentation-openai",
        "OPENINFERENCE_IMPORT": "openinference.instrumentation.openai",
        "OPENINFERENCE_CLASS": "OpenAIInstrumentor",
        "TRACELOOP_PACKAGE": "opentelemetry-instrumentation-openai",
        "TRACELOOP_IMPORT": "opentelemetry.instrumentation.openai",
        "TRACELOOP_CLASS": "OpenAIInstrumentor",
        "TRACELOOP_AVAILABLE": True,
        "BASIC_USAGE_EXAMPLE": """from openai import AzureOpenAI
       
       # Create Azure OpenAI client
       client = AzureOpenAI(
           api_key=os.getenv("AZURE_OPENAI_API_KEY"),
           api_version="2024-02-01",
           azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
       )
       
       # Chat completion
       response = client.chat.completions.create(
           model="gpt-35-turbo",  # Your deployment name
           messages=[{"role": "user", "content": "Hello from Azure OpenAI!"}]
       )""",
        "ADVANCED_FUNCTION_NAME": "multi_deployment_azure_workflow",
        "ADVANCED_FUNCTION_PARAMS": "prompts: List[str]",
        "ADVANCED_USAGE_EXAMPLE": """from openai import AzureOpenAI
       
       # Configure Azure OpenAI client
       client = AzureOpenAI(
           api_key=os.getenv("AZURE_OPENAI_API_KEY"),
           api_version="2024-02-01",
           azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
       )""",
        "ADVANCED_IMPLEMENTATION": """# Test multiple Azure OpenAI deployments
       deployments = [
           "gpt-35-turbo",      # Your GPT-3.5 deployment
           "gpt-4",             # Your GPT-4 deployment
           "gpt-4-turbo"        # Your GPT-4 Turbo deployment
       ]
       
       results = []
       for prompt in prompts:
           deployment_results = {}
           
           for deployment in deployments:
               try:
                   # Test each deployment
                   response = client.chat.completions.create(
                       model=deployment,
                       messages=[
                           {"role": "user", "content": prompt}
                       ],
                       max_tokens=150,
                       temperature=0.7
                   )
                   
                   deployment_results[deployment] = {
                       "content": response.choices[0].message.content,
                       "tokens": response.usage.total_tokens,
                       "prompt_tokens": response.usage.prompt_tokens,
                       "completion_tokens": response.usage.completion_tokens
                   }
                   
               except Exception as e:
                   deployment_results[deployment] = {"error": str(e)}
           
           results.append({
               "prompt": prompt,
               "deployment_responses": deployment_results
           })""",
        "ADDITIONAL_ENV_CONFIG": """# AZURE_OPENAI_API_KEY=your-azure-openai-key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_VERSION=2024-02-01""",
        "MULTIPLE_INSTRUMENTORS_EXAMPLE": """from openinference.instrumentation.openai import OpenAIInstrumentor
       from openinference.instrumentation.anthropic import AnthropicInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               OpenAIInstrumentor(),      # Works for both OpenAI and Azure OpenAI
               AnthropicInstrumentor()
           ]
       )""",
        "MULTIPLE_TRACELOOP_INSTRUMENTORS_EXAMPLE": """from opentelemetry.instrumentation.openai import OpenAIInstrumentor
       from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               OpenAIInstrumentor(),      # Works for both OpenAI and Azure OpenAI
               AnthropicInstrumentor()    # Traceloop Anthropic
           ]
       )""",
        "USE_CASE_NAME": "multi_deployment_analysis",
        "STRATEGY_NAME": "azure_deployment_comparison",
        "MODELS_USED": '["gpt-35-turbo", "gpt-4", "gpt-4-turbo"]',
        "FIRST_PARAM": "prompts",
        "SEE_ALSO_LINKS": """- :doc:`multi-provider` - Use Azure OpenAI with other providers
- :doc:`../llm-application-patterns` - LLM agent architectures and patterns
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
- :doc:`openai` - Similar integration for OpenAI""",
    },
    "mcp": {
        "PROVIDER_NAME": "Model Context Protocol (MCP)",
        "PROVIDER_KEY": "mcp",
        "PROVIDER_MODULE": "mcp",
        "PROVIDER_SDK": "mcp>=1.0.0",
        "PROVIDER_EXCEPTION": "mcp.MCPError",
        "PROVIDER_API_KEY_NAME": "MCP_API_KEY",
        "OPENINFERENCE_PACKAGE": "openinference-instrumentation-mcp",
        "OPENINFERENCE_IMPORT": "openinference.instrumentation.mcp",
        "OPENINFERENCE_CLASS": "MCPInstrumentor",
        "TRACELOOP_PACKAGE": "opentelemetry-instrumentation-mcp",
        "TRACELOOP_IMPORT": "opentelemetry.instrumentation.mcp",
        "TRACELOOP_CLASS": "MCPInstrumentor",
        "TRACELOOP_AVAILABLE": True,
        "BASIC_USAGE_EXAMPLE": """import mcp
       
       # Create MCP client
       client = mcp.Client(
           server_url="http://localhost:8000",
           api_key=os.getenv("MCP_API_KEY")
       )
       
       # Execute tool via MCP
       result = client.call_tool(
           name="web_search",
           arguments={"query": "Traceloop MCP integration"}
       )""",
        "ADVANCED_FUNCTION_NAME": "multi_tool_mcp_workflow",
        "ADVANCED_FUNCTION_PARAMS": "tasks: List[Dict[str, Any]]",
        "ADVANCED_USAGE_EXAMPLE": """import mcp
       
       # Configure MCP client
       client = mcp.Client(
           server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000"),
           api_key=os.getenv("MCP_API_KEY")
       )""",
        "ADVANCED_IMPLEMENTATION": """# Execute multiple MCP tools in workflow
       available_tools = [
           "web_search",
           "file_processor", 
           "data_analyzer",
           "content_generator"
       ]
       
       results = []
       for task in tasks:
           task_results = {}
           tool_name = task.get("tool")
           arguments = task.get("arguments", {})
           
           if tool_name in available_tools:
               try:
                   # Execute MCP tool
                   result = client.call_tool(
                       name=tool_name,
                       arguments=arguments
                   )
                   
                   task_results[tool_name] = {
                       "success": True,
                       "result": result.content,
                       "metadata": result.metadata
                   }
                   
               except Exception as tool_error:
                   task_results[tool_name] = {
                       "success": False,
                       "error": str(tool_error)
                   }
           else:
               task_results[tool_name] = {
                   "success": False,
                   "error": f"Tool {tool_name} not available"
               }
           
           results.append({
               "task": task,
               "tool_results": task_results
           })""",
        "ADDITIONAL_ENV_CONFIG": """# MCP_API_KEY=your-mcp-api-key
# MCP_SERVER_URL=http://localhost:8000
# MCP_CLIENT_ID=your-client-id""",
        "MULTIPLE_INSTRUMENTORS_EXAMPLE": """from openinference.instrumentation.mcp import MCPInstrumentor
       from openinference.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               MCPInstrumentor(),
               OpenAIInstrumentor()
           ]
       )""",
        "MULTIPLE_TRACELOOP_INSTRUMENTORS_EXAMPLE": """from opentelemetry.instrumentation.mcp import MCPInstrumentor
       from opentelemetry.instrumentation.openai import OpenAIInstrumentor
       
       # Step 1: Initialize HoneyHive tracer first (without instrumentors)
       tracer = HoneyHiveTracer.init(
           project="your-project"  # Or set HH_PROJECT environment variable
       )
       
       # Step 2: Initialize instrumentors separately with tracer_provider
       # REPLACE_WITH_INSTRUMENTOR_SETUP
               MCPInstrumentor(),         # Traceloop MCP
               OpenAIInstrumentor()       # Traceloop OpenAI
           ]
       )""",
        "USE_CASE_NAME": "tool_orchestration",
        "STRATEGY_NAME": "mcp_multi_tool",
        "MODELS_USED": '["web_search", "file_processor", "data_analyzer"]',
        "FIRST_PARAM": "tasks",
        "SEE_ALSO_LINKS": """- :doc:`multi-provider` - Use MCP with other providers
- :doc:`../llm-application-patterns` - LLM agent architectures and patterns
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
- :doc:`../advanced-tracing/index` - Advanced tracing patterns""",
    },
}


def load_compatibility_data() -> Dict[str, Any]:
    """Load provider compatibility data from YAML file."""
    compatibility_file = Path(__file__).parent / "provider_compatibility.yaml"
    
    if not compatibility_file.exists():
        raise FileNotFoundError(
            f"Compatibility data file not found: {compatibility_file}\n"
            "Please ensure provider_compatibility.yaml exists in the templates directory."
        )
    
    with open(compatibility_file, 'r') as f:
        return yaml.safe_load(f)


def format_python_version_support(data: Dict[str, List[str]]) -> str:
    """Format Python version support as RST list-table."""
    lines = []
    lines.append(".. list-table::")
    lines.append("   :header-rows: 1")
    lines.append("   :widths: 30 70")
    lines.append("")
    lines.append("   * - Support Level")
    lines.append("     - Python Versions")
    
    if data.get("supported"):
        versions_str = ", ".join(data["supported"])
        lines.append("   * - Fully Supported")
        lines.append(f"     - {versions_str}")
    
    if data.get("partial"):
        versions_str = ", ".join(data["partial"])
        lines.append("   * - Partial Support")
        lines.append(f"     - {versions_str}")
    
    if data.get("unsupported"):
        versions_str = ", ".join(data["unsupported"])
        lines.append("   * - Not Supported")
        lines.append(f"     - {versions_str}")
    
    return "\n".join(lines)


def format_sdk_version_range(data: Dict[str, Any]) -> str:
    """Format SDK version requirements as RST bullet list."""
    lines = []
    
    if data.get("minimum"):
        lines.append(f"- **Minimum**: {data['minimum']}")
    
    if data.get("recommended"):
        lines.append(f"- **Recommended**: {data['recommended']}")
    
    if data.get("tested_versions"):
        versions_str = ", ".join(data["tested_versions"])
        lines.append(f"- **Tested Versions**: {versions_str}")
    
    return "\n".join(lines)


def format_instrumentor_compatibility(data: Dict[str, Dict[str, str]]) -> str:
    """Format instrumentor compatibility as RST list-table."""
    lines = []
    lines.append(".. list-table::")
    lines.append("   :header-rows: 1")
    lines.append("   :widths: 30 20 50")
    lines.append("")
    lines.append("   * - Instrumentor")
    lines.append("     - Status")
    lines.append("     - Notes")
    
    status_labels = {
        "fully_supported": "Fully Supported",
        "partial": "Partial Support",
        "experimental": "Experimental",
        "not_supported": "Not Supported"
    }
    
    if "openinference" in data:
        status = data["openinference"].get("status", "unknown")
        status_label = status_labels.get(status, status.replace("_", " ").title())
        notes = data["openinference"].get("notes", "")
        lines.append("   * - OpenInference")
        lines.append(f"     - {status_label}")
        lines.append(f"     - {notes}")
    
    if "traceloop" in data:
        status = data["traceloop"].get("status", "unknown")
        status_label = status_labels.get(status, status.replace("_", " ").title())
        notes = data["traceloop"].get("notes", "")
        lines.append("   * - Traceloop")
        lines.append(f"     - {status_label}")
        lines.append(f"     - {notes}")
    
    return "\n".join(lines)


def format_known_limitations(limitations: List[str]) -> str:
    """Format known limitations as RST bullet list."""
    if not limitations:
        return "No known limitations."
    
    lines = []
    for limitation in limitations:
        lines.append(f"- {limitation}")
    
    return "\n".join(lines)


def validate_compatibility_data() -> bool:
    """Validate compatibility data structure and completeness."""
    try:
        compat_data = load_compatibility_data()
        
        required_fields = [
            "python_version_support",
            "sdk_version_range", 
            "instrumentor_compatibility",
            "known_limitations"
        ]
        
        all_valid = True
        for provider_key in PROVIDER_CONFIGS.keys():
            if provider_key not in compat_data:
                print(f"❌ Missing compatibility data for provider: {provider_key}")
                all_valid = False
                continue
            
            provider_compat = compat_data[provider_key]
            
            for field in required_fields:
                if field not in provider_compat:
                    print(f"❌ {provider_key}: Missing required field '{field}'")
                    all_valid = False
            
            # Validate python_version_support structure
            if "python_version_support" in provider_compat:
                pvs = provider_compat["python_version_support"]
                if not isinstance(pvs, dict):
                    print(f"❌ {provider_key}: python_version_support must be a dict")
                    all_valid = False
                elif not any(k in pvs for k in ["supported", "partial", "unsupported"]):
                    print(f"❌ {provider_key}: python_version_support missing version categories")
                    all_valid = False
            
            # Validate instrumentor_compatibility has at least 3 limitations
            if "known_limitations" in provider_compat:
                limitations = provider_compat["known_limitations"]
                if not isinstance(limitations, list):
                    print(f"❌ {provider_key}: known_limitations must be a list")
                    all_valid = False
                elif len(limitations) < 3:
                    print(f"⚠️  {provider_key}: known_limitations has only {len(limitations)} entries (recommended: ≥3)")
        
        if all_valid:
            print(f"✅ All compatibility data validated successfully ({len(compat_data)} providers)")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


def generate_provider_docs(provider_key: str, output_path: Path = None) -> None:
    """Generate provider documentation from template."""

    if provider_key not in PROVIDER_CONFIGS:
        raise ValueError(
            f"Unknown provider: {provider_key}. Available: {list(PROVIDER_CONFIGS.keys())}"
        )

    # Load template
    template_path = (
        Path(__file__).parent / "multi_instrumentor_integration_formal_template.rst"
    )
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    template_content = template_path.read_text()

    # Get provider configuration
    variables = PROVIDER_CONFIGS[provider_key].copy()
    
    # Load and merge compatibility data from YAML
    compatibility_data = load_compatibility_data()
    if provider_key in compatibility_data:
        provider_compat = compatibility_data[provider_key]
        
        # Format compatibility data as RST and add to variables
        variables["PYTHON_VERSION_SUPPORT"] = format_python_version_support(
            provider_compat.get("python_version_support", {})
        )
        variables["SDK_VERSION_RANGE"] = format_sdk_version_range(
            provider_compat.get("sdk_version_range", {})
        )
        variables["INSTRUMENTOR_COMPATIBILITY"] = format_instrumentor_compatibility(
            provider_compat.get("instrumentor_compatibility", {})
        )
        variables["KNOWN_LIMITATIONS"] = format_known_limitations(
            provider_compat.get("known_limitations", [])
        )
    else:
        # Fallback if compatibility data is missing
        print(f"⚠️  Warning: No compatibility data found for {provider_key}")
        variables["PYTHON_VERSION_SUPPORT"] = "No compatibility data available."
        variables["SDK_VERSION_RANGE"] = "No compatibility data available."
        variables["INSTRUMENTOR_COMPATIBILITY"] = "No compatibility data available."
        variables["KNOWN_LIMITATIONS"] = "No compatibility data available."

    # Handle Traceloop availability
    if variables.get("TRACELOOP_AVAILABLE") == False:
        # Replace Traceloop description with unavailability note
        openllmetry_desc = variables.get(
            "TRACELOOP_NOTE", "Traceloop instrumentor not available for this provider."
        )
        template_content = template_content.replace(
            '{{TRACELOOP_NOTE if TRACELOOP_AVAILABLE == False else "Enhanced LLM metrics, cost tracking, production optimizations"}}',
            openllmetry_desc,
        )

        # Replace the instrumentor selection description
        template_content = template_content.replace(
            "- **Traceloop**: Enhanced LLM metrics, cost tracking, production optimizations",
            f"- **Traceloop**: {openllmetry_desc}",
        )

        # Replace Traceloop section content with unavailability message
        openllmetry_section_replacement = f"""
.. note::
   **Traceloop Not Available**
   
   {openllmetry_desc}
   
   Please use the OpenInference instrumentor above for {variables.get("PROVIDER_NAME", "this provider")} integration.

.. raw:: html

   </div>
   </div>"""

        # Find and replace the Traceloop section content
        import re

        # Replace everything between openllmetry-section div and its closing
        pattern = r'(<div id="openllmetry-section"[^>]*>)(.*?)(<div class="instrumentor-content">|</div>\s*</div>)'
        replacement = r"\1" + openllmetry_section_replacement
        template_content = re.sub(
            pattern, replacement, template_content, flags=re.DOTALL
        )

        # Remove comparison table and migration sections when Traceloop is not available
        # Remove comparison section
        comparison_pattern = r"Comparison: OpenInference vs Traceloop.*?(?=\n[A-Z][^\n]*\n-+|\nSee Also\n-+|\Z)"
        template_content = re.sub(
            comparison_pattern, "", template_content, flags=re.DOTALL
        )

        # Remove migration section
        migration_pattern = (
            r"Migration Between Instrumentors\n-+.*?(?=\nSee Also\n-+|\Z)"
        )
        template_content = re.sub(
            migration_pattern, "", template_content, flags=re.DOTALL
        )

        # Remove any standalone content after the Traceloop section since all config goes in troubleshooting tabs
        after_openllmetry_pattern = r"(.. raw:: html\n\n   </div>\n   </div>\n\n)(.*?)(?=.. raw:: html\n\n   <script>)"
        template_content = re.sub(
            after_openllmetry_pattern, r"\1", template_content, flags=re.DOTALL
        )

    else:
        template_content = template_content.replace(
            '{{TRACELOOP_NOTE if TRACELOOP_AVAILABLE == False else "Enhanced LLM metrics, cost tracking, production optimizations"}}',
            "Enhanced LLM metrics, cost tracking, production optimizations",
        )

    # Handle Environment Configuration
    provider_env_configs = {
        "openai": {
            "HAS_SPECIFIC_ENV_VARS": True,
            "ENV_VARS": [
                "# HoneyHive configuration",
                'export HH_API_KEY="your-honeyhive-api-key"',
                'export HH_SOURCE="production"',
                "",
                "# OpenAI configuration",
                'export OPENAI_API_KEY="your-openai-api-key"',
            ],
            "TRACELOOP_ADDITIONAL_ENV_VARS": [
                "",
                "# Optional: Traceloop cloud features",
                'export TRACELOOP_API_KEY="your-traceloop-key"',
                'export TRACELOOP_BASE_URL="https://api.traceloop.com"',
            ],
        },
        "anthropic": {
            "HAS_SPECIFIC_ENV_VARS": True,
            "ENV_VARS": [
                "# HoneyHive configuration",
                'export HH_API_KEY="your-honeyhive-api-key"',
                'export HH_SOURCE="production"',
                "",
                "# Anthropic configuration",
                'export ANTHROPIC_API_KEY="your-anthropic-api-key"',
            ],
            "TRACELOOP_ADDITIONAL_ENV_VARS": [
                "",
                "# Optional: Traceloop cloud features",
                'export TRACELOOP_API_KEY="your-traceloop-key"',
                'export TRACELOOP_BASE_URL="https://api.traceloop.com"',
            ],
        },
        "google-ai": {
            "HAS_SPECIFIC_ENV_VARS": True,
            "ENV_VARS": [
                "# HoneyHive configuration",
                'export HH_API_KEY="your-honeyhive-api-key"',
                'export HH_SOURCE="production"',
                "",
                "# Google AI configuration",
                'export GOOGLE_API_KEY="your-google-ai-api-key"',
            ],
            "TRACELOOP_ADDITIONAL_ENV_VARS": [
                "",
                "# Optional: Traceloop cloud features",
                'export TRACELOOP_API_KEY="your-traceloop-key"',
                'export TRACELOOP_BASE_URL="https://api.traceloop.com"',
            ],
        },
        "google-adk": {
            "HAS_SPECIFIC_ENV_VARS": True,
            "ENV_VARS": [
                "# HoneyHive configuration",
                'export HH_API_KEY="your-honeyhive-api-key"',
                'export HH_SOURCE="production"',
                "",
                "# Google Agent Development Kit (ADK) configuration",
                'export GOOGLE_API_KEY="your-google-adk-api-key"',
            ],
        },
        "bedrock": {
            "HAS_SPECIFIC_ENV_VARS": True,
            "ENV_VARS": [
                "# HoneyHive configuration",
                'export HH_API_KEY="your-honeyhive-api-key"',
                'export HH_SOURCE="production"',
                "",
                "# AWS Bedrock configuration",
                'export AWS_ACCESS_KEY_ID="your-aws-access-key"',
                'export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"',
                'export AWS_DEFAULT_REGION="us-east-1"',
            ],
            "TRACELOOP_ADDITIONAL_ENV_VARS": [
                "",
                "# Optional: Traceloop cloud features",
                'export TRACELOOP_API_KEY="your-traceloop-key"',
                'export TRACELOOP_BASE_URL="https://api.traceloop.com"',
            ],
        },
        "azure-openai": {
            "HAS_SPECIFIC_ENV_VARS": True,
            "ENV_VARS": [
                "# HoneyHive configuration",
                'export HH_API_KEY="your-honeyhive-api-key"',
                'export HH_SOURCE="production"',
                "",
                "# Azure OpenAI configuration",
                'export AZURE_OPENAI_API_KEY="your-azure-openai-key"',
                'export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"',
                'export AZURE_OPENAI_API_VERSION="2024-02-01"',
            ],
            "TRACELOOP_ADDITIONAL_ENV_VARS": [
                "",
                "# Optional: Traceloop cloud features",
                'export TRACELOOP_API_KEY="your-traceloop-key"',
                'export TRACELOOP_BASE_URL="https://api.traceloop.com"',
            ],
        },
        "mcp": {
            "HAS_SPECIFIC_ENV_VARS": True,
            "ENV_VARS": [
                "# HoneyHive configuration",
                'export HH_API_KEY="your-honeyhive-api-key"',
                'export HH_SOURCE="production"',
                "",
                "# MCP configuration",
                'export MCP_SERVER_URL="http://localhost:8000"',
                'export MCP_API_KEY="your-mcp-api-key"  # Optional',
            ],
        },
    }

    # Add title underline variable
    title = f"Integrate with {variables['PROVIDER_NAME']}"
    variables["TITLE_UNDERLINE"] = "=" * len(title)

    # Replace all template variables first
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        template_content = template_content.replace(placeholder, str(value))

    # Add environment configuration to troubleshooting sections if provider has specific env vars
    if (
        provider_key in provider_env_configs
        and provider_env_configs[provider_key]["HAS_SPECIFIC_ENV_VARS"]
    ):
        import re

        env_vars = provider_env_configs[provider_key]["ENV_VARS"]
        env_vars_block = "\n      ".join(env_vars)

        # Add to OpenInference troubleshooting (item 4)
        openinference_env_section = f"""
4. **Environment Configuration**
   
   .. code-block:: bash
   
      {env_vars_block}"""

        # Find OpenInference troubleshooting section end (after variable substitution)
        openinference_pattern = rf'(<div id="{provider_key}-openinference-troubleshoot".*?)(.. raw:: html\n\n   </div>\n   </div>)'
        openinference_match = re.search(
            openinference_pattern, template_content, re.DOTALL
        )

        if openinference_match:
            replacement = (
                openinference_match.group(1)
                + openinference_env_section
                + "\n\n"
                + openinference_match.group(2)
            )
            template_content = template_content.replace(
                openinference_match.group(0), replacement
            )

        # Add to Traceloop troubleshooting (item 5) if available
        if variables.get("TRACELOOP_AVAILABLE", True):
            openllmetry_env_vars = env_vars.copy()
            if "TRACELOOP_ADDITIONAL_ENV_VARS" in provider_env_configs[provider_key]:
                openllmetry_env_vars.extend(
                    provider_env_configs[provider_key]["TRACELOOP_ADDITIONAL_ENV_VARS"]
                )

            openllmetry_env_vars_block = "\n      ".join(openllmetry_env_vars)
            openllmetry_env_section = f"""
5. **Environment Configuration**
   
   .. code-block:: bash
   
      {openllmetry_env_vars_block}"""

            # Find Traceloop troubleshooting section end (after variable substitution)
            openllmetry_pattern = rf'(<div id="{provider_key}-openllmetry-troubleshoot".*?)(.. raw:: html\n\n   </div>\n   </div>)'
            openllmetry_match = re.search(
                openllmetry_pattern, template_content, re.DOTALL
            )

            if openllmetry_match:
                replacement = (
                    openllmetry_match.group(1)
                    + openllmetry_env_section
                    + "\n\n"
                    + openllmetry_match.group(2)
                )
                template_content = template_content.replace(
                    openllmetry_match.group(0), replacement
                )

    # Determine output path
    if output_path is None:
        output_path = (
            template_path.parent.parent
            / "how-to"
            / "integrations"
            / f"{provider_key}.rst"
        )

    # Write generated documentation
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template_content)

    print(f"✅ Generated: {output_path}")
    print(f"🔧 Provider: {variables['PROVIDER_NAME']}")
    print(f"📦 OpenInference: {variables['OPENINFERENCE_PACKAGE']}")
    print(f"📦 Traceloop: {variables['TRACELOOP_PACKAGE']}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Generate provider integration documentation from template"
    )
    parser.add_argument(
        "--provider",
        choices=list(PROVIDER_CONFIGS.keys()),
        help="Provider to generate documentation for",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: docs/how-to/integrations/{provider}.rst)",
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Regenerate documentation for all providers"
    )
    parser.add_argument(
        "--validate", 
        action="store_true", 
        help="Validate compatibility data structure and completeness"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )
    parser.add_argument("--list", action="store_true", help="List available providers")

    args = parser.parse_args()

    if args.list:
        print("Available providers:")
        for key, config in PROVIDER_CONFIGS.items():
            print(f"  {key} - {config['PROVIDER_NAME']}")
        return

    if args.validate:
        success = validate_compatibility_data()
        return 0 if success else 1
    
    if args.all:
        print(f"Regenerating documentation for all {len(PROVIDER_CONFIGS)} providers...")
        for provider_key in PROVIDER_CONFIGS.keys():
            try:
                if args.dry_run:
                    print(f"  [DRY RUN] Would generate: {provider_key}.rst")
                else:
                    generate_provider_docs(provider_key, None)
                    print(f"  ✅ Generated: {provider_key}.rst")
            except Exception as e:
                print(f"  ❌ Failed {provider_key}: {e}")
        return 0
    
    if not args.provider:
        parser.error("--provider is required (unless --all, --validate, or --list is specified)")

    if args.dry_run:
        print(f"[DRY RUN] Would generate documentation for: {args.provider}")
        return 0

    try:
        generate_provider_docs(args.provider, args.output)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

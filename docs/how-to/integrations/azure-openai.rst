Azure OpenAI Integration
=========================

Learn how to integrate HoneyHive with Azure OpenAI Service using the BYOI (Bring Your Own Instrumentor) approach for enterprise OpenAI deployments.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

Azure OpenAI Service provides enterprise-grade access to OpenAI models with enhanced security, compliance, and regional availability. HoneyHive provides automatic tracing through OpenInference instrumentors with zero code changes to your existing Azure OpenAI implementations.

**Benefits**:
- **Enterprise Security**: Private endpoints, VNet integration, managed identity
- **Compliance**: Built for enterprise compliance requirements
- **Regional Deployment**: Deploy models in your preferred Azure regions
- **Automatic Tracing**: All Azure OpenAI calls traced automatically
- **Cost Management**: Detailed usage and cost tracking

Key Differences from OpenAI
---------------------------

Azure OpenAI differs from standard OpenAI in several ways:

================= ========================= =================================
Aspect            OpenAI                    Azure OpenAI
================= ========================= =================================
Authentication    API Keys                  API Keys + Azure AD + Managed Identity
Endpoints         api.openai.com            Custom Azure endpoints
Model Names       gpt-3.5-turbo             Custom deployment names
Pricing           Per-token                 Provisioned + per-token options
Security          Standard                  Enterprise-grade with VNet
Compliance        Limited                   SOC 2, HIPAA, FedRAMP options
================= ========================= =================================

Quick Start
-----------

**1. Install Required Packages**

.. code-block:: bash

   pip install honeyhive openai openinference-instrumentation-openai azure-identity

**2. Configure Azure OpenAI Access**

.. code-block:: bash

   # Option 1: API Key authentication
   export AZURE_OPENAI_API_KEY=your-azure-openai-key
   export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   
   # Option 2: Azure AD authentication
   az login

**3. Initialize HoneyHive with OpenAI Instrumentor**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   import os

   # Initialize HoneyHive tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       ,
       instrumentors=[OpenAIInstrumentor()]
   )

   # Configure Azure OpenAI client
   client = openai.AzureOpenAI(
       api_key=os.getenv("AZURE_OPENAI_API_KEY"),
       api_version="2024-02-01",
       azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
   )

**4. Use Azure OpenAI Normally - Automatically Traced**

.. code-block:: python

   # All Azure OpenAI calls are now automatically traced
   response = client.chat.completions.create(
       model="gpt-35-turbo",  # Your deployment name
       messages=[{"role": "user", "content": "Hello from Azure!"}]
   )
   print(response.choices[0].message.content)

Basic Chat Completion
---------------------

**Problem**: Trace Azure OpenAI chat completions with deployment-specific tracking.

**Solution**:

.. code-block:: python

   import openai
   import os
   from typing import List, Dict, Any

   def azure_chat_completion(
       messages: List[Dict[str, str]],
       deployment_name: str = "gpt-35-turbo",
       temperature: float = 0.7,
       max_tokens: int = 1000
   ) -> str:
       """Chat completion with Azure OpenAI and automatic tracing."""
       
       client = openai.AzureOpenAI(
           api_key=os.getenv("AZURE_OPENAI_API_KEY"),
           api_version="2024-02-01",
           azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
       )
       
       # This call is automatically traced with:
       # - Azure-specific endpoint and deployment info
       # - Model parameters and token usage
       # - Latency and performance metrics
       # - Azure-specific error codes if any
       response = client.chat.completions.create(
           model=deployment_name,  # Azure deployment name
           messages=messages,
           temperature=temperature,
           max_tokens=max_tokens
       )
       
       return response.choices[0].message.content

   def enhanced_azure_chat(user_message: str, context: Dict[str, Any] = None):
       """Enhanced chat with custom tracing context."""
       
       with tracer.start_span("azure_enhanced_chat") as span:
           span.set_attribute("azure.endpoint", os.getenv("AZURE_OPENAI_ENDPOINT"))
           span.set_attribute("azure.api_version", "2024-02-01")
           span.set_attribute("chat.user_message_length", len(user_message))
           
           if context:
               for key, value in context.items():
                   span.set_attribute(f"context.{key}", str(value))
           
           messages = [
               {"role": "system", "content": "You are a helpful assistant deployed on Azure."},
               {"role": "user", "content": user_message}
           ]
           
           response = azure_chat_completion(messages, deployment_name="gpt-35-turbo")
           
           span.set_attribute("chat.response_length", len(response))
           span.set_attribute("azure.deployment_used", "gpt-35-turbo")
           
           return response

   # Usage examples
   response = azure_chat_completion([
       {"role": "user", "content": "Explain Azure OpenAI benefits"}
   ])

   enhanced_response = enhanced_azure_chat(
       "What are the advantages of Azure OpenAI?",
       context={"user_type": "enterprise", "region": "eastus"}
   )

Multi-Deployment Strategy
-------------------------

**Problem**: Use multiple Azure OpenAI deployments for different purposes with tracking.

**Solution**:

.. code-block:: python

   class AzureOpenAIManager:
       """Manage multiple Azure OpenAI deployments with tracing."""
       
       def __init__(self):
           self.client = openai.AzureOpenAI(
               api_key=os.getenv("AZURE_OPENAI_API_KEY"),
               api_version="2024-02-01", 
               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
           )
           
           # Define deployment mappings
           self.deployments = {
               "fast_chat": {
                   "model": "gpt-35-turbo",
                   "use_case": "quick responses",
                   "max_tokens": 500,
                   "temperature": 0.7
               },
               "analytical": {
                   "model": "gpt-4",
                   "use_case": "detailed analysis", 
                   "max_tokens": 2000,
                   "temperature": 0.3
               },
               "creative": {
                   "model": "gpt-4",
                   "use_case": "creative writing",
                   "max_tokens": 1500,
                   "temperature": 0.9
               },
               "embeddings": {
                   "model": "text-embedding-ada-002",
                   "use_case": "text embeddings",
                   "dimensions": 1536
               }
           }
       
       def route_request(self, message: str, task_type: str = "fast_chat") -> Dict[str, Any]:
           """Route request to appropriate deployment with tracing."""
           
           if task_type not in self.deployments:
               raise ValueError(f"Unknown task type: {task_type}")
           
           deployment = self.deployments[task_type]
           
           with tracer.start_span("azure_deployment_routing") as span:
               span.set_attribute("azure.task_type", task_type)
               span.set_attribute("azure.deployment_model", deployment["model"])
               span.set_attribute("azure.use_case", deployment["use_case"])
               span.set_attribute("routing.message_length", len(message))
               
               if task_type == "embeddings":
                   # Handle embeddings differently
                   response = self.client.embeddings.create(
                       model=deployment["model"],
                       input=message
                   )
                   
                   embedding = response.data[0].embedding
                   span.set_attribute("embeddings.dimensions", len(embedding))
                   span.set_attribute("embeddings.model", deployment["model"])
                   
                   return {
                       "type": "embedding",
                       "embedding": embedding,
                       "model": deployment["model"],
                       "dimensions": len(embedding)
                   }
               else:
                   # Handle chat completions
                   messages = [{"role": "user", "content": message}]
                   
                   response = self.client.chat.completions.create(
                       model=deployment["model"],
                       messages=messages,
                       max_tokens=deployment["max_tokens"],
                       temperature=deployment["temperature"]
                   )
                   
                   content = response.choices[0].message.content
                   
                   span.set_attribute("chat.response_length", len(content))
                   span.set_attribute("chat.temperature", deployment["temperature"])
                   span.set_attribute("chat.max_tokens", deployment["max_tokens"])
                   
                   return {
                       "type": "chat",
                       "response": content,
                       "model": deployment["model"],
                       "task_type": task_type,
                       "tokens_used": response.usage.total_tokens if response.usage else 0
                   }

   def intelligent_routing_example():
       """Example of intelligent request routing."""
       
       manager = AzureOpenAIManager()
       
       # Different types of requests
       requests = [
           ("What's the weather like?", "fast_chat"),
           ("Analyze the economic impact of renewable energy adoption", "analytical"),
           ("Write a creative story about space exploration", "creative"),
           ("Convert this text to embeddings", "embeddings")
       ]
       
       results = []
       for message, task_type in requests:
           result = manager.route_request(message, task_type)
           results.append({
               "message": message,
               "task_type": task_type,
               "result": result
           })
           
           print(f"Task: {task_type}")
           print(f"Message: {message}")
           print(f"Result type: {result['type']}")
           if result['type'] == 'chat':
               print(f"Response: {result['response'][:100]}...")
           print()
       
       return results

   # Usage
   manager = AzureOpenAIManager()
   routing_results = intelligent_routing_example()

Azure AD Authentication
-----------------------

**Problem**: Use Azure AD authentication instead of API keys for enhanced security.

**Solution**:

.. code-block:: python

   from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
   from azure.core.exceptions import ClientAuthenticationError

   def setup_azure_ad_authentication(use_managed_identity: bool = False):
       """Setup Azure OpenAI with Azure AD authentication."""
       
       try:
           if use_managed_identity:
               # For Azure services with managed identity
               credential = ManagedIdentityCredential()
           else:
               # For local development or service principal
               credential = DefaultAzureCredential()
           
           # Get token for OpenAI scope
           token = credential.get_token("https://cognitiveservices.azure.com/.default")
           
           # Create client with token authentication
           client = openai.AzureOpenAI(
               azure_ad_token=token.token,
               api_version="2024-02-01",
               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
           )
           
           with tracer.start_span("azure_ad_auth_setup") as span:
               span.set_attribute("auth.type", "azure_ad")
               span.set_attribute("auth.managed_identity", use_managed_identity)
               span.set_attribute("azure.endpoint", os.getenv("AZURE_OPENAI_ENDPOINT"))
               span.set_attribute("auth.token_expires", token.expires_on)
           
           return client
           
       except ClientAuthenticationError as e:
           with tracer.start_span("azure_ad_auth_error") as span:
               span.set_attribute("auth.error", str(e))
               span.set_attribute("auth.type", "azure_ad")
               span.set_status("ERROR", str(e))
           raise

   def azure_ad_chat_example():
       """Example using Azure AD authentication."""
       
       try:
           # Setup client with Azure AD
           client = setup_azure_ad_authentication()
           
           with tracer.start_span("azure_ad_chat") as span:
               span.set_attribute("auth.method", "azure_ad")
               
               response = client.chat.completions.create(
                   model="gpt-35-turbo",
                   messages=[{
                       "role": "user", 
                       "content": "Hello from Azure AD authenticated session!"
                   }]
               )
               
               span.set_attribute("chat.success", True)
               return response.choices[0].message.content
               
       except Exception as e:
           with tracer.start_span("azure_ad_chat_error") as span:
               span.set_attribute("auth.method", "azure_ad")
               span.set_attribute("error.message", str(e))
               span.set_status("ERROR", str(e))
           raise

   # Usage
   try:
       response = azure_ad_chat_example()
       print("Response:", response)
   except Exception as e:
       print(f"Authentication failed: {e}")

Regional Deployment Monitoring
------------------------------

**Problem**: Monitor performance across different Azure regions and deployments.

**Solution**:

.. code-block:: python

   import time
   from typing import Dict, List
   import statistics

   class AzureRegionMonitor:
       """Monitor Azure OpenAI performance across regions."""
       
       def __init__(self):
           self.regional_endpoints = {
               "east_us": {
                   "endpoint": "https://eastus-openai.openai.azure.com/",
                   "region": "East US",
                   "deployments": ["gpt-35-turbo", "gpt-4"]
               },
               "west_europe": {
                   "endpoint": "https://westeurope-openai.openai.azure.com/", 
                   "region": "West Europe",
                   "deployments": ["gpt-35-turbo", "gpt-4"]
               },
               "canada_central": {
                   "endpoint": "https://canadacentral-openai.openai.azure.com/",
                   "region": "Canada Central", 
                   "deployments": ["gpt-35-turbo"]
               }
           }
       
       def benchmark_regions(self, test_message: str, iterations: int = 3) -> Dict[str, Any]:
           """Benchmark performance across Azure regions."""
           
           results = {}
           
           with tracer.start_span("regional_benchmark") as benchmark_span:
               benchmark_span.set_attribute("benchmark.test_message", test_message)
               benchmark_span.set_attribute("benchmark.iterations", iterations)
               benchmark_span.set_attribute("benchmark.regions_count", len(self.regional_endpoints))
               
               for region_key, region_config in self.regional_endpoints.items():
                   region_results = []
                   
                   with tracer.start_span(f"region_{region_key}") as region_span:
                       region_span.set_attribute("region.name", region_config["region"])
                       region_span.set_attribute("region.endpoint", region_config["endpoint"])
                       region_span.set_attribute("region.deployments_count", len(region_config["deployments"]))
                       
                       for deployment in region_config["deployments"]:
                           deployment_latencies = []
                           
                           with tracer.start_span(f"deployment_{deployment}") as deployment_span:
                               deployment_span.set_attribute("deployment.model", deployment)
                               deployment_span.set_attribute("deployment.region", region_config["region"])
                               
                               for i in range(iterations):
                                   try:
                                       # Create client for this region
                                       client = openai.AzureOpenAI(
                                           api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                           api_version="2024-02-01",
                                           azure_endpoint=region_config["endpoint"]
                                       )
                                       
                                       start_time = time.time()
                                       
                                       response = client.chat.completions.create(
                                           model=deployment,
                                           messages=[{"role": "user", "content": test_message}],
                                           max_tokens=100
                                       )
                                       
                                       end_time = time.time()
                                       latency = (end_time - start_time) * 1000  # ms
                                       
                                       deployment_latencies.append(latency)
                                       
                                       # Record individual call metrics
                                       with tracer.start_span(f"call_{i+1}") as call_span:
                                           call_span.set_attribute("call.iteration", i + 1)
                                           call_span.set_attribute("call.latency_ms", latency)
                                           call_span.set_attribute("call.tokens_used", 
                                                                  response.usage.total_tokens if response.usage else 0)
                                           call_span.set_attribute("call.success", True)
                                   
                                   except Exception as e:
                                       with tracer.start_span(f"call_{i+1}_error") as error_span:
                                           error_span.set_attribute("call.iteration", i + 1)
                                           error_span.set_attribute("call.error", str(e))
                                           error_span.set_attribute("call.success", False)
                               
                               # Calculate deployment statistics
                               if deployment_latencies:
                                   avg_latency = statistics.mean(deployment_latencies)
                                   min_latency = min(deployment_latencies)
                                   max_latency = max(deployment_latencies)
                                   std_latency = statistics.stdev(deployment_latencies) if len(deployment_latencies) > 1 else 0
                                   
                                   deployment_span.set_attribute("performance.avg_latency_ms", avg_latency)
                                   deployment_span.set_attribute("performance.min_latency_ms", min_latency)
                                   deployment_span.set_attribute("performance.max_latency_ms", max_latency)
                                   deployment_span.set_attribute("performance.std_latency_ms", std_latency)
                                   deployment_span.set_attribute("performance.success_rate", len(deployment_latencies) / iterations)
                                   
                                   region_results.append({
                                       "deployment": deployment,
                                       "avg_latency_ms": avg_latency,
                                       "min_latency_ms": min_latency,
                                       "max_latency_ms": max_latency,
                                       "std_latency_ms": std_latency,
                                       "success_rate": len(deployment_latencies) / iterations
                                   })
                       
                       # Calculate region averages
                       if region_results:
                           region_avg_latency = statistics.mean([r["avg_latency_ms"] for r in region_results])
                           region_span.set_attribute("region.avg_latency_ms", region_avg_latency)
                           region_span.set_attribute("region.deployments_tested", len(region_results))
                   
                   results[region_key] = {
                       "region": region_config["region"],
                       "endpoint": region_config["endpoint"],
                       "deployments": region_results,
                       "region_avg_latency": statistics.mean([r["avg_latency_ms"] for r in region_results]) if region_results else 0
                   }
               
               # Overall benchmark summary
               all_latencies = []
               for region_data in results.values():
                   for deployment in region_data["deployments"]:
                       all_latencies.append(deployment["avg_latency_ms"])
               
               if all_latencies:
                   benchmark_span.set_attribute("benchmark.overall_avg_latency", statistics.mean(all_latencies))
                   benchmark_span.set_attribute("benchmark.best_latency", min(all_latencies))
                   benchmark_span.set_attribute("benchmark.worst_latency", max(all_latencies))
               
               return results

   def analyze_regional_performance():
       """Analyze and compare regional performance."""
       
       monitor = AzureRegionMonitor()
       
       results = monitor.benchmark_regions(
           "What are the benefits of cloud computing?",
           iterations=5
       )
       
       print("=== Azure OpenAI Regional Performance Analysis ===\n")
       
       for region_key, region_data in results.items():
           print(f"Region: {region_data['region']}")
           print(f"Endpoint: {region_data['endpoint']}")
           print(f"Average Latency: {region_data['region_avg_latency']:.1f}ms")
           
           for deployment in region_data['deployments']:
               print(f"  {deployment['deployment']}: {deployment['avg_latency_ms']:.1f}ms (±{deployment['std_latency_ms']:.1f}ms)")
           print()
       
       # Find best performing region
       best_region = min(results.items(), key=lambda x: x[1]['region_avg_latency'])
       print(f"🏆 Best performing region: {best_region[1]['region']} ({best_region[1]['region_avg_latency']:.1f}ms)")
       
       return results

   # Usage
   performance_results = analyze_regional_performance()

Cost Optimization for Azure
---------------------------

**Problem**: Optimize costs with Azure OpenAI's unique pricing models.

**Solution**:

.. code-block:: python

   class AzureCostOptimizer:
       """Optimize Azure OpenAI costs across deployments and pricing models."""
       
       def __init__(self):
           # Azure OpenAI pricing (example rates - check current pricing)
           self.pricing = {
               "gpt-35-turbo": {
                   "pay_as_you_go": {"input": 0.0015, "output": 0.002},  # per 1K tokens
                   "provisioned": {"hourly": 42.50}  # per hour for 100K PTU
               },
               "gpt-4": {
                   "pay_as_you_go": {"input": 0.03, "output": 0.06},
                   "provisioned": {"hourly": 630.00}  # per hour for 100K PTU
               },
               "gpt-4-32k": {
                   "pay_as_you_go": {"input": 0.06, "output": 0.12},
                   "provisioned": {"hourly": 1260.00}
               }
           }
       
       def calculate_costs(
           self,
           model: str,
           monthly_tokens: int,
           peak_concurrent_requests: int = 10
       ) -> Dict[str, float]:
           """Calculate costs for pay-as-you-go vs provisioned throughput."""
           
           if model not in self.pricing:
               raise ValueError(f"Unknown model: {model}")
           
           pricing = self.pricing[model]
           
           with tracer.start_span("cost_calculation") as span:
               span.set_attribute("cost.model", model)
               span.set_attribute("cost.monthly_tokens", monthly_tokens)
               span.set_attribute("cost.peak_concurrent_requests", peak_concurrent_requests)
               
               # Pay-as-you-go calculation (assuming 50/50 input/output split)
               input_tokens = monthly_tokens * 0.5
               output_tokens = monthly_tokens * 0.5
               
               payg_cost = (
                   (input_tokens / 1000) * pricing["pay_as_you_go"]["input"] +
                   (output_tokens / 1000) * pricing["pay_as_you_go"]["output"]
               )
               
               # Provisioned throughput calculation
               # Estimate PTU needed based on concurrent requests and tokens per request
               avg_tokens_per_request = 500  # Rough estimate
               ptu_needed = peak_concurrent_requests * (avg_tokens_per_request / 1000) * 100  # PTU scaling factor
               
               hours_per_month = 24 * 30  # 720 hours
               provisioned_cost = (ptu_needed / 100000) * pricing["provisioned"]["hourly"] * hours_per_month
               
               span.set_attribute("cost.payg_monthly", payg_cost)
               span.set_attribute("cost.provisioned_monthly", provisioned_cost)
               span.set_attribute("cost.ptu_needed", ptu_needed)
               span.set_attribute("cost.recommended_model", "pay_as_you_go" if payg_cost < provisioned_cost else "provisioned")
               
               return {
                   "pay_as_you_go": payg_cost,
                   "provisioned": provisioned_cost,
                   "ptu_needed": ptu_needed,
                   "savings": abs(payg_cost - provisioned_cost),
                   "recommended": "pay_as_you_go" if payg_cost < provisioned_cost else "provisioned"
               }
       
       def cost_optimization_report(self, usage_scenarios: List[Dict]) -> Dict[str, Any]:
           """Generate cost optimization report for multiple scenarios."""
           
           report = {"scenarios": [], "recommendations": []}
           
           with tracer.start_span("cost_optimization_report") as span:
               span.set_attribute("optimization.scenarios_count", len(usage_scenarios))
               
               total_payg_cost = 0
               total_provisioned_cost = 0
               
               for i, scenario in enumerate(usage_scenarios):
                   costs = self.calculate_costs(
                       scenario["model"],
                       scenario["monthly_tokens"], 
                       scenario.get("peak_concurrent_requests", 10)
                   )
                   
                   scenario_result = {
                       "name": scenario.get("name", f"Scenario {i+1}"),
                       "model": scenario["model"],
                       "monthly_tokens": scenario["monthly_tokens"],
                       "costs": costs
                   }
                   
                   report["scenarios"].append(scenario_result)
                   total_payg_cost += costs["pay_as_you_go"]
                   total_provisioned_cost += costs["provisioned"]
               
               # Overall recommendations
               total_savings = abs(total_payg_cost - total_provisioned_cost)
               overall_recommendation = "pay_as_you_go" if total_payg_cost < total_provisioned_cost else "provisioned"
               
               report["summary"] = {
                   "total_payg_cost": total_payg_cost,
                   "total_provisioned_cost": total_provisioned_cost,
                   "total_savings": total_savings,
                   "overall_recommendation": overall_recommendation
               }
               
               span.set_attribute("optimization.total_payg_cost", total_payg_cost)
               span.set_attribute("optimization.total_provisioned_cost", total_provisioned_cost)
               span.set_attribute("optimization.total_savings", total_savings)
               span.set_attribute("optimization.recommendation", overall_recommendation)
               
               return report

   def cost_optimization_example():
       """Example cost optimization analysis."""
       
       optimizer = AzureCostOptimizer()
       
       # Define usage scenarios
       scenarios = [
           {
               "name": "Customer Support Chatbot",
               "model": "gpt-35-turbo",
               "monthly_tokens": 5000000,  # 5M tokens/month
               "peak_concurrent_requests": 50
           },
           {
               "name": "Content Generation",
               "model": "gpt-4",
               "monthly_tokens": 1000000,  # 1M tokens/month
               "peak_concurrent_requests": 10
           },
           {
               "name": "Code Assistant",
               "model": "gpt-4-32k",
               "monthly_tokens": 500000,   # 500K tokens/month
               "peak_concurrent_requests": 5
           }
       ]
       
       report = optimizer.cost_optimization_report(scenarios)
       
       print("=== Azure OpenAI Cost Optimization Report ===\n")
       
       for scenario in report["scenarios"]:
           print(f"Scenario: {scenario['name']}")
           print(f"Model: {scenario['model']}")
           print(f"Monthly Tokens: {scenario['monthly_tokens']:,}")
           print(f"Pay-as-you-go: ${scenario['costs']['pay_as_you_go']:.2f}")
           print(f"Provisioned: ${scenario['costs']['provisioned']:.2f}")
           print(f"Recommended: {scenario['costs']['recommended']}")
           print(f"Potential Savings: ${scenario['costs']['savings']:.2f}")
           print()
       
       print("=== Summary ===")
       print(f"Total Pay-as-you-go: ${report['summary']['total_payg_cost']:.2f}")
       print(f"Total Provisioned: ${report['summary']['total_provisioned_cost']:.2f}")
       print(f"Overall Recommendation: {report['summary']['overall_recommendation']}")
       print(f"Potential Monthly Savings: ${report['summary']['total_savings']:.2f}")
       
       return report

   # Usage
   cost_report = cost_optimization_example()

Environment Configuration
-------------------------

**Problem**: Manage Azure OpenAI configurations across environments securely.

**Solution**:

.. code-block:: python

   import os
   from azure.keyvault.secrets import SecretClient
   from azure.identity import DefaultAzureCredential

   def setup_azure_environment(
       environment: str = "development",
       use_key_vault: bool = False,
       key_vault_url: Optional[str] = None
   ):
       """Setup Azure OpenAI environment with proper security."""
       
       with tracer.start_span("azure_environment_setup") as span:
           span.set_attribute("environment", environment)
           span.set_attribute("azure.use_key_vault", use_key_vault)
           
           if use_key_vault and key_vault_url:
               # Retrieve secrets from Azure Key Vault
               credential = DefaultAzureCredential()
               secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
               
               try:
                   api_key = secret_client.get_secret("azure-openai-api-key").value
                   endpoint = secret_client.get_secret("azure-openai-endpoint").value
                   hh_api_key = secret_client.get_secret("honeyhive-api-key").value
                   
                   span.set_attribute("azure.secrets_retrieved", True)
               except Exception as e:
                   span.set_attribute("azure.secrets_error", str(e))
                   raise
           else:
               # Use environment variables
               api_key = os.getenv("AZURE_OPENAI_API_KEY")
               endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
               hh_api_key = os.getenv("HH_API_KEY")
           
           if not all([api_key, endpoint, hh_api_key]):
               raise ValueError("Missing required configuration")
           
           # Environment-specific configuration
           tracer_config = {
               "api_key": hh_api_key,
               "project": f"azure-openai-{environment}",
               "source": environment,
               "instrumentors": [OpenAIInstrumentor()]
           }
           
           if environment == "production":
               tracer_config["disable_http_tracing"] = False
           elif environment == "development":
               tracer_config["test_mode"] = True
           
           # Initialize HoneyHive tracer
           tracer = HoneyHiveTracer.init(**tracer_config)
           
           # Create Azure OpenAI client
           client = openai.AzureOpenAI(
               api_key=api_key,
               api_version="2024-02-01",
               azure_endpoint=endpoint
           )
           
           span.set_attribute("azure.endpoint", endpoint)
           span.set_attribute("azure.api_version", "2024-02-01")
           span.set_attribute("setup.success", True)
           
           return tracer, client

   # Usage for different environments
   dev_tracer, dev_client = setup_azure_environment("development")
   prod_tracer, prod_client = setup_azure_environment(
       "production", 
       use_key_vault=True,
       key_vault_url="https://your-keyvault.vault.azure.net/"
   )

Best Practices
--------------

**1. Deployment Strategy**

.. code-block:: python

   # Use descriptive deployment names
   deployment_mapping = {
       "fast-chat": "gpt-35-turbo-fast",     # For quick responses
       "analysis": "gpt-4-analysis",         # For detailed analysis
       "creative": "gpt-4-creative",         # For creative tasks
       "embeddings": "text-embedding-ada-002" # For embeddings
   }

**2. Error Handling**

.. code-block:: python

   # Handle Azure-specific errors
   from openai import AzureOpenAI
   import openai

   def robust_azure_call(client: AzureOpenAI, **kwargs):
       try:
           return client.chat.completions.create(**kwargs)
       except openai.RateLimitError as e:
           # Handle Azure rate limiting
           print(f"Rate limited: {e}")
           raise
       except openai.APIConnectionError as e:
           # Handle Azure connectivity issues
           print(f"Connection error: {e}")
           raise

**3. Security Best Practices**

.. code-block:: python

   # Always use secure credential management
   def secure_client_setup():
       # Never hardcode credentials
       api_key = os.getenv("AZURE_OPENAI_API_KEY")
       endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
       
       if not api_key or not endpoint:
           raise ValueError("Azure OpenAI credentials not configured")
       
       return openai.AzureOpenAI(
           api_key=api_key,
           api_version="2024-02-01",
           azure_endpoint=endpoint
       )

**4. Monitoring and Logging**

.. code-block:: python

   # Add comprehensive logging for Azure-specific metrics
   def enhanced_azure_monitoring(client, deployment, messages):
       with tracer.start_span("azure_monitored_call") as span:
           span.set_attribute("azure.deployment", deployment)
           span.set_attribute("azure.message_count", len(messages))
           
           start_time = time.time()
           response = client.chat.completions.create(
               model=deployment,
               messages=messages
           )
           end_time = time.time()
           
           span.set_attribute("azure.latency_ms", (end_time - start_time) * 1000)
           span.set_attribute("azure.tokens_used", response.usage.total_tokens if response.usage else 0)
           
           return response

See Also
--------

- :doc:`multi-provider` - Use Azure OpenAI with other providers
- :doc:`../troubleshooting` - Common integration issues
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
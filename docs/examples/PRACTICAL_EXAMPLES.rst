Practical Examples
==================

Real-world implementation examples for the HoneyHive Python SDK.

.. contents:: Table of Contents
   :local:
   :depth: 2

Web Application
---------------

FastAPI Integration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI, HTTPException
   from honeyhive import HoneyHiveTracer, trace
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import httpx

   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="web-app",
       source="production",
       instrumentors=[OpenAIInstrumentor()]
   )

   app = FastAPI()

   @app.middleware("http")
   async def tracing_middleware(request, call_next):
       """Add tracing to all HTTP requests."""
       
       with tracer.start_span("http-request") as span:
           # Set request attributes
           span.set_attribute("http.method", request.method)
           span.set_attribute("http.url", str(request.url))
           span.set_attribute("http.user_agent", request.headers.get("user-agent", ""))
           
           try:
               response = await call_next(request)
               span.set_attribute("http.status_code", response.status_code)
               return response
           except Exception as e:
               span.set_attribute("http.error", str(e))
               span.set_attribute("http.error_type", type(e).__name__)
               raise

   @app.get("/users/{user_id}")
   @trace
   async def get_user(user_id: str):
       """Get user information with automatic tracing."""
       
       # Simulate database query
       user = await fetch_user_from_db(user_id)
       
       if not user:
           raise HTTPException(status_code=404, detail="User not found")
       
       return user

   @app.post("/chat")
   async def chat_endpoint(request: dict):
       """Chat endpoint with AI integration."""
       
       with tracer.start_span("chat-request") as span:
           span.set_attribute("chat.user_id", request.get("user_id"))
           span.set_attribute("chat.message_length", len(request.get("message", "")))
           
           try:
               # AI response generation
               response = await generate_ai_response(request["message"])
               
               span.set_attribute("chat.response_length", len(response))
               span.set_attribute("chat.success", True)
               
               return {"response": response}
               
           except Exception as e:
               span.set_attribute("chat.success", False)
               span.set_attribute("chat.error", str(e))
               raise HTTPException(status_code=500, detail="Chat failed")

   async def fetch_user_from_db(user_id: str):
       """Fetch user from database."""
       # Simulate database call
       return {"id": user_id, "name": f"User {user_id}"}

   async def generate_ai_response(message: str):
       """Generate AI response using OpenAI."""
       import openai
       
       response = openai.ChatCompletion.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": message}],
           max_tokens=150
       )
       
       return response.choices[0].message.content

Data Processing Pipeline
------------------------

ETL Pipeline with Tracing
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   import pandas as pd
   import asyncio

   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="data-pipeline",
       source="production"
   )

   class DataPipeline:
       def __init__(self):
           self.tracer = tracer
       
       @trace
       async def extract_data(self, source_path: str) -> pd.DataFrame:
           """Extract data from source with tracing."""
           
           with self.tracer.start_span("data-extraction") as span:
               span.set_attribute("pipeline.stage", "extract")
               span.set_attribute("pipeline.source", source_path)
               
               try:
                   # Read data
                   if source_path.endswith('.csv'):
                       data = pd.read_csv(source_path)
                   elif source_path.endswith('.json'):
                       data = pd.read_json(source_path)
                   else:
                       raise ValueError(f"Unsupported format: {source_path}")
                   
                   span.set_attribute("pipeline.rows", len(data))
                   span.set_attribute("pipeline.columns", len(data.columns))
                   
                   return data
                   
               except Exception as e:
                   span.set_attribute("pipeline.error", str(e))
                   span.record_exception(e)
                   raise
       
       @trace
       async def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
           """Transform data with tracing."""
           
           with self.tracer.start_span("data-transformation") as span:
               span.set_attribute("pipeline.stage", "transform")
               span.set_attribute("pipeline.input_rows", len(data))
               
               try:
                   # Data cleaning
                   cleaned = data.dropna()
                   span.set_attribute("pipeline.cleaned_rows", len(cleaned))
                   
                   # Data transformation
                   transformed = cleaned.copy()
                   transformed['processed'] = cleaned['value'] * 2
                   
                   span.set_attribute("pipeline.output_rows", len(transformed))
                   span.set_attribute("pipeline.success", True)
                   
                   return transformed
                   
               except Exception as e:
                   span.set_attribute("pipeline.success", False)
                   span.set_attribute("pipeline.error", str(e))
                   span.record_exception(e)
                   raise
       
       @trace
       async def load_data(self, data: pd.DataFrame, target_path: str):
           """Load data to target with tracing."""
           
           with self.tracer.start_span("data-loading") as span:
               span.set_attribute("pipeline.stage", "load")
               span.set_attribute("pipeline.target", target_path)
               span.set_attribute("pipeline.rows", len(data))
               
               try:
                   # Save data
                   if target_path.endswith('.csv'):
                       data.to_csv(target_path, index=False)
                   elif target_path.endswith('.parquet'):
                       data.to_parquet(target_path, index=False)
                   else:
                       raise ValueError(f"Unsupported format: {target_path}")
                   
                   span.set_attribute("pipeline.success", True)
                   
               except Exception as e:
                   span.set_attribute("pipeline.success", False)
                   span.set_attribute("pipeline.error", str(e))
                   span.record_exception(e)
                   raise
       
       @trace
       async def run_pipeline(self, source_path: str, target_path: str):
           """Run complete ETL pipeline with tracing."""
           
           with self.tracer.start_span("etl-pipeline") as span:
               span.set_attribute("pipeline.source", source_path)
               span.set_attribute("pipeline.target", target_path)
               
               try:
                   # Extract
                   data = await self.extract_data(source_path)
                   
                   # Transform
                   transformed = await self.transform_data(data)
                   
                   # Load
                   await self.load_data(transformed, target_path)
                   
                   span.set_attribute("pipeline.success", True)
                   span.set_attribute("pipeline.total_rows", len(transformed))
                   
                   return transformed
                   
               except Exception as e:
                   span.set_attribute("pipeline.success", False)
                   span.set_attribute("pipeline.error", str(e))
                   span.record_exception(e)
                   raise

   # Usage
   async def main():
       pipeline = DataPipeline()
       
       try:
           result = await pipeline.run_pipeline(
               "input_data.csv",
               "output_data.parquet"
           )
           print(f"Pipeline completed: {len(result)} rows processed")
       except Exception as e:
           print(f"Pipeline failed: {e}")

   if __name__ == "__main__":
       asyncio.run(main())

AI Service
----------

Multi-Provider AI Service
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import asyncio
   from typing import Dict, Any

   # Initialize tracer with multiple instrumentors
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="ai-service",
       source="production",
       instrumentors=[
           OpenAIInstrumentor(),
           AnthropicInstrumentor()
       ]
   )

   class AIService:
       def __init__(self):
           self.tracer = tracer
       
       @trace
       async def generate_with_openai(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
           """Generate using OpenAI with automatic tracing."""
           
           import openai
           
           try:
               response = openai.ChatCompletion.create(
                   model=model,
                   messages=[{"role": "user", "content": prompt}],
                   max_tokens=1000
               )
               
               return response.choices[0].message.content
               
           except Exception as e:
               # Error is automatically recorded by OpenInference
               raise
       
       @trace
       async def generate_with_anthropic(self, prompt: str, model: str = "claude-3-sonnet-20240229") -> str:
           """Generate using Anthropic with automatic tracing."""
           
           import anthropic
           
           client = anthropic.Anthropic(api_key="your-anthropic-key")
           
           try:
               response = client.messages.create(
                   model=model,
                   max_tokens=1000,
                   messages=[{"role": "user", "content": prompt}]
               )
               
               return response.content[0].text
               
           except Exception as e:
               # Error is automatically recorded by OpenInference
               raise
       
       @trace
       async def generate_with_fallback(self, prompt: str, primary_model: str = "openai") -> str:
           """Generate with fallback to alternative provider."""
           
           with self.tracer.start_span("ai-generation-with-fallback") as span:
               span.set_attribute("ai.primary_model", primary_model)
               span.set_attribute("ai.prompt_length", len(prompt))
               
               try:
                   if primary_model == "openai":
                       try:
                           result = await self.generate_with_openai(prompt)
                           span.set_attribute("ai.provider_used", "openai")
                           return result
                       except Exception as e:
                           span.set_attribute("ai.fallback_triggered", True)
                           span.set_attribute("ai.fallback_reason", str(e))
                           
                           # Fallback to Anthropic
                           result = await self.generate_with_anthropic(prompt)
                           span.set_attribute("ai.provider_used", "anthropic")
                           return result
                   
                   else:  # primary_model == "anthropic"
                       try:
                           result = await self.generate_with_anthropic(prompt)
                           span.set_attribute("ai.provider_used", "anthropic")
                           return result
                       except Exception as e:
                           span.set_attribute("ai.fallback_triggered", True)
                           span.set_attribute("ai.fallback_reason", str(e))
                           
                           # Fallback to OpenAI
                           result = await self.generate_with_openai(prompt)
                           span.set_attribute("ai.provider_used", "openai")
                           return result
               
               except Exception as e:
                   span.set_attribute("ai.success", False)
                   span.set_attribute("ai.error", str(e))
                   span.record_exception(e)
                   raise

   # Usage
   async def main():
       service = AIService()
       
       prompt = "Explain quantum computing in simple terms"
       
       try:
           # Try OpenAI first, fallback to Anthropic
           result = await service.generate_with_fallback(prompt, "openai")
           print(f"Generated: {result}")
       except Exception as e:
           print(f"Generation failed: {e}")

   if __name__ == "__main__":
       asyncio.run(main())

Microservice
------------

User Service with Tracing
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from fastapi import FastAPI, HTTPException
   import httpx
   import asyncio

   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="user-service",
       source="production"
   )

   app = FastAPI()

   class UserService:
       def __init__(self):
           self.tracer = tracer
           self.http_client = httpx.AsyncClient()
       
       @trace
       async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
           """Get user profile with tracing."""
           
           with self.tracer.start_span("user-profile-lookup") as span:
               span.set_attribute("user.id", user_id)
               
               try:
                   # Call external user service
                   response = await self.http_client.get(
                       f"https://external-user-service.com/users/{user_id}"
                   )
                   
                   if response.status_code == 200:
                       user_data = response.json()
                       span.set_attribute("user.found", True)
                       span.set_attribute("user.email", user_data.get("email", ""))
                       return user_data
                   else:
                       span.set_attribute("user.found", False)
                       span.set_attribute("http.status_code", response.status_code)
                       raise HTTPException(status_code=404, detail="User not found")
               
               except Exception as e:
                   span.set_attribute("user.lookup_error", str(e))
                   span.record_exception(e)
                   raise
       
       @trace
       async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
           """Update user preferences with tracing."""
           
           with self.tracer.start_span("user-preferences-update") as span:
               span.set_attribute("user.id", user_id)
               span.set_attribute("preferences.count", len(preferences))
               
               try:
                   # Update preferences
                   response = await self.http_client.put(
                       f"https://external-user-service.com/users/{user_id}/preferences",
                       json=preferences
                   )
                   
                   if response.status_code == 200:
                       updated_data = response.json()
                       span.set_attribute("update.success", True)
                       return updated_data
                   else:
                       span.set_attribute("update.success", False)
                       span.set_attribute("http.status_code", response.status_code)
                       raise HTTPException(status_code=response.status_code, detail="Update failed")
               
               except Exception as e:
                   span.set_attribute("update.error", str(e))
                   span.record_exception(e)
                   raise

   # Initialize service
   user_service = UserService()

   @app.get("/users/{user_id}")
   @trace
   async def get_user(user_id: str):
       """Get user endpoint with tracing."""
       return await user_service.get_user_profile(user_id)

   @app.put("/users/{user_id}/preferences")
   @trace
   async def update_preferences(user_id: str, preferences: Dict[str, Any]):
       """Update preferences endpoint with tracing."""
       return await user_service.update_user_preferences(user_id, preferences)

   @app.on_event("shutdown")
   async def shutdown_event():
       """Cleanup on shutdown."""
       await user_service.http_client.aclose()

Experiment Tracking
-------------------

MLflow Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   import mlflow
   import os
   from typing import Dict, Any

   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="ml-experiments",
       source="production"
   )

   class ExperimentTracker:
       def __init__(self):
           self.tracer = tracer
           mlflow.set_tracking_uri("http://localhost:5000")
       
       @trace
       def start_experiment(self, experiment_name: str, run_name: str = None) -> str:
           """Start MLflow experiment with tracing."""
           
           with self.tracer.start_span("experiment-start") as span:
               span.set_attribute("experiment.name", experiment_name)
               span.set_attribute("experiment.run_name", run_name or "default")
               
               try:
                   # Set experiment
                   mlflow.set_experiment(experiment_name)
                   
                   # Start run
                   run = mlflow.start_run(run_name=run_name)
                   
                   span.set_attribute("experiment.run_id", run.info.run_id)
                   span.set_attribute("experiment.success", True)
                   
                   return run.info.run_id
               
               except Exception as e:
                   span.set_attribute("experiment.success", False)
                   span.set_attribute("experiment.error", str(e))
                   span.record_exception(e)
                   raise
       
       @trace
       def log_parameters(self, run_id: str, params: Dict[str, Any]):
           """Log experiment parameters with tracing."""
           
           with self.tracer.start_span("parameter-logging") as span:
               span.set_attribute("experiment.run_id", run_id)
               span.set_attribute("parameters.count", len(params))
               
               try:
                   with mlflow.start_run(run_id=run_id):
                       mlflow.log_params(params)
                   
                   span.set_attribute("logging.success", True)
               
               except Exception as e:
                   span.set_attribute("logging.success", False)
                   span.set_attribute("logging.error", str(e))
                   span.record_exception(e)
                   raise
       
       @trace
       def log_metrics(self, run_id: str, metrics: Dict[str, float]):
           """Log experiment metrics with tracing."""
           
           with self.tracer.start_span("metric-logging") as span:
               span.set_attribute("experiment.run_id", run_id)
               span.set_attribute("metrics.count", len(metrics))
               
               try:
                   with mlflow.start_run(run_id=run_id):
                       mlflow.log_metrics(metrics)
                   
                   span.set_attribute("logging.success", True)
               
               except Exception as e:
                   span.set_attribute("logging.success", False)
                   span.set_attribute("logging.error", str(e))
                   span.record_exception(e)
                   raise
       
       @trace
       def end_experiment(self, run_id: str):
           """End MLflow experiment with tracing."""
           
           with self.tracer.start_span("experiment-end") as span:
               span.set_attribute("experiment.run_id", run_id)
               
               try:
                   mlflow.end_run()
                   span.set_attribute("experiment.ended", True)
               
               except Exception as e:
                   span.set_attribute("experiment.ended", False)
                   span.set_attribute("experiment.error", str(e))
                   span.record_exception(e)
                   raise

   # Usage example
   def run_experiment():
       tracker = ExperimentTracker()
       
       try:
           # Start experiment
           run_id = tracker.start_experiment("hyperparameter-tuning", "run-001")
           
           # Log parameters
           params = {
               "learning_rate": 0.001,
               "batch_size": 32,
               "epochs": 100
           }
           tracker.log_parameters(run_id, params)
           
           # Simulate training
           # ... training code here ...
           
           # Log metrics
           metrics = {
               "accuracy": 0.95,
               "loss": 0.05,
               "training_time": 120.5
           }
           tracker.log_metrics(run_id, metrics)
           
           # End experiment
           tracker.end_experiment(run_id)
           
           print(f"Experiment completed: {run_id}")
       
       except Exception as e:
           print(f"Experiment failed: {e}")

   if __name__ == "__main__":
       run_experiment()

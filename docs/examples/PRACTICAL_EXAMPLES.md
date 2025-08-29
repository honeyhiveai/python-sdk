# Practical Examples

Real-world implementation examples for the HoneyHive Python SDK.

## Table of Contents

- [Web Application](#web-application)
- [Data Processing Pipeline](#data-processing-pipeline)
- [AI Service](#ai-service)
- [Microservice](#microservice)
- [Experiment Tracking](#experiment-tracking)

---

## Web Application

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from honeyhive import HoneyHiveTracer, trace
from openinference.instrumentation.openai import OpenAIInstrumentor
import httpx

# Initialize tracer
tracer = HoneyHiveTracer(
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
        max_tokens=100
    )
    
    return response.choices[0].message.content
```

---

## Data Processing Pipeline

### ETL Pipeline with Tracing

```python
from honeyhive import HoneyHiveTracer, trace
import pandas as pd
import time

# Initialize tracer
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="data-pipeline",
    source="production"
)

class DataPipeline:
    def __init__(self):
        self.tracer = tracer
    
    @trace
    def extract_data(self, source_path: str):
        """Extract data from source."""
        
        with self.tracer.start_span("data-extraction") as span:
            span.set_attribute("source.path", source_path)
            span.set_attribute("source.type", "csv")
            
            start_time = time.time()
            
            try:
                # Read data
                data = pd.read_csv(source_path)
                
                duration = time.time() - start_time
                span.set_attribute("extraction.duration", duration)
                span.set_attribute("extraction.rows", len(data))
                span.set_attribute("extraction.columns", len(data.columns))
                
                return data
                
            except Exception as e:
                span.set_attribute("extraction.error", str(e))
                span.set_attribute("extraction.success", False)
                raise
    
    @trace
    def transform_data(self, data: pd.DataFrame):
        """Transform extracted data."""
        
        with self.tracer.start_span("data-transformation") as span:
            span.set_attribute("transformation.input_rows", len(data))
            span.set_attribute("transformation.input_columns", len(data.columns))
            
            start_time = time.time()
            
            try:
                # Data cleaning
                cleaned_data = self._clean_data(data)
                
                # Data validation
                validated_data = self._validate_data(cleaned_data)
                
                # Feature engineering
                final_data = self._engineer_features(validated_data)
                
                duration = time.time() - start_time
                span.set_attribute("transformation.duration", duration)
                span.set_attribute("transformation.output_rows", len(final_data))
                span.set_attribute("transformation.output_columns", len(final_data.columns))
                span.set_attribute("transformation.success", True)
                
                return final_data
                
            except Exception as e:
                span.set_attribute("transformation.error", str(e))
                span.set_attribute("transformation.success", False)
                raise
    
    @trace
    def load_data(self, data: pd.DataFrame, target_path: str):
        """Load transformed data to target."""
        
        with self.tracer.start_span("data-loading") as span:
            span.set_attribute("target.path", target_path)
            span.set_attribute("target.rows", len(data))
            span.set_attribute("target.columns", len(data.columns))
            
            start_time = time.time()
            
            try:
                # Save data
                data.to_csv(target_path, index=False)
                
                duration = time.time() - start_time
                span.set_attribute("loading.duration", duration)
                span.set_attribute("loading.success", True)
                
                return target_path
                
            except Exception as e:
                span.set_attribute("loading.error", str(e))
                span.set_attribute("loading.success", False)
                raise
    
    def _clean_data(self, data: pd.DataFrame):
        """Clean the data."""
        with self.tracer.enrich_span("data-cleaning", {"step": "cleaning"}):
            # Remove duplicates
            data = data.drop_duplicates()
            
            # Handle missing values
            data = data.fillna(0)
            
            return data
    
    def _validate_data(self, data: pd.DataFrame):
        """Validate the data."""
        with self.tracer.enrich_span("data-validation", {"step": "validation"}):
            # Check for required columns
            required_columns = ["id", "name", "value"]
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            return data
    
    def _engineer_features(self, data: pd.DataFrame):
        """Engineer new features."""
        with self.tracer.enrich_span("feature-engineering", {"step": "engineering"}):
            # Add timestamp
            data["processed_at"] = pd.Timestamp.now()
            
            # Add derived features
            if "value" in data.columns:
                data["value_squared"] = data["value"] ** 2
                data["value_log"] = np.log(data["value"] + 1)
            
            return data
    
    def run_pipeline(self, source_path: str, target_path: str):
        """Run the complete ETL pipeline."""
        
        with self.tracer.start_span("etl-pipeline") as span:
            span.set_attribute("pipeline.source", source_path)
            span.set_attribute("pipeline.target", target_path)
            
            try:
                # Extract
                data = self.extract_data(source_path)
                
                # Transform
                transformed_data = self.transform_data(data)
                
                # Load
                result_path = self.load_data(transformed_data, target_path)
                
                span.set_attribute("pipeline.success", True)
                span.set_attribute("pipeline.result_path", result_path)
                
                return result_path
                
            except Exception as e:
                span.set_attribute("pipeline.success", False)
                span.set_attribute("pipeline.error", str(e))
                raise

# Usage
pipeline = DataPipeline()
result = pipeline.run_pipeline("input.csv", "output.csv")
```

---

## AI Service

### Multi-Provider AI Service

```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor
import openai
import anthropic
import asyncio

# Initialize tracer with multiple instrumentors
tracer = HoneyHiveTracer(
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
        self.openai_client = openai
        self.anthropic_client = anthropic.Anthropic(api_key="your-anthropic-key")
    
    async def generate_response(self, prompt: str, provider: str = "openai"):
        """Generate AI response from specified provider."""
        
        with self.tracer.start_span("ai-generation") as span:
            span.set_attribute("ai.provider", provider)
            span.set_attribute("ai.prompt_length", len(prompt))
            span.set_attribute("ai.prompt_tokens", self._estimate_tokens(prompt))
            
            start_time = time.time()
            
            try:
                if provider == "openai":
                    response = await self._generate_openai(prompt)
                elif provider == "anthropic":
                    response = await self._generate_anthropic(prompt)
                else:
                    raise ValueError(f"Unsupported provider: {provider}")
                
                duration = time.time() - start_time
                span.set_attribute("ai.duration", duration)
                span.set_attribute("ai.response_length", len(response))
                span.set_attribute("ai.success", True)
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                span.set_attribute("ai.duration", duration)
                span.set_attribute("ai.error", str(e))
                span.set_attribute("ai.success", False)
                raise
    
    async def _generate_openai(self, prompt: str):
        """Generate response using OpenAI."""
        
        with self.tracer.start_span("openai-generation") as span:
            span.set_attribute("openai.model", "gpt-3.5-turbo")
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            
            span.set_attribute("openai.response_tokens", response.usage.total_tokens)
            span.set_attribute("openai.prompt_tokens", response.usage.prompt_tokens)
            span.set_attribute("openai.completion_tokens", response.usage.completion_tokens)
            
            return result
    
    async def _generate_anthropic(self, prompt: str):
        """Generate response using Anthropic."""
        
        with self.tracer.start_span("anthropic-generation") as span:
            span.set_attribute("anthropic.model", "claude-3-sonnet-20240229")
            
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            
            span.set_attribute("anthropic.input_tokens", response.usage.input_tokens)
            span.set_attribute("anthropic.output_tokens", response.usage.output_tokens)
            
            return result
    
    def _estimate_tokens(self, text: str):
        """Estimate token count for text."""
        # Simple estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    async def compare_providers(self, prompt: str):
        """Compare responses from multiple providers."""
        
        with self.tracer.start_span("provider-comparison") as span:
            span.set_attribute("comparison.prompt", prompt)
            
            # Generate responses from both providers
            tasks = [
                self.generate_response(prompt, "openai"),
                self.generate_response(prompt, "anthropic")
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            results = {}
            for i, (provider, response) in enumerate([("openai", "anthropic")]):
                if isinstance(responses[i], Exception):
                    results[provider] = {"error": str(responses[i])}
                else:
                    results[provider] = {"response": responses[i]}
            
            span.set_attribute("comparison.results", str(results))
            return results

# Usage
ai_service = AIService()

# Single provider
response = await ai_service.generate_response("Explain quantum computing", "openai")

# Compare providers
comparison = await ai_service.compare_providers("Write a haiku about AI")
```

---

## Microservice

### User Service with Tracing

```python
from honeyhive import HoneyHiveTracer, trace
import httpx
import json
import time

# Initialize tracer
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="user-service",
    source="production"
)

class UserService:
    def __init__(self):
        self.tracer = tracer
        self.base_url = "https://api.example.com"
    
    @trace
    async def get_user(self, user_id: str):
        """Get user by ID."""
        
        with self.tracer.start_span("user-lookup") as span:
            span.set_attribute("user.id", user_id)
            span.set_attribute("service.name", "user-service")
            
            try:
                # Make HTTP request
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}/users/{user_id}")
                    
                    span.set_attribute("http.status_code", response.status_code)
                    span.set_attribute("http.response_size", len(response.content))
                    
                    if response.status_code == 200:
                        user_data = response.json()
                        span.set_attribute("user.found", True)
                        span.set_attribute("user.email", user_data.get("email", ""))
                        return user_data
                    else:
                        span.set_attribute("user.found", False)
                        span.set_attribute("http.error", response.text)
                        return None
                        
            except Exception as e:
                span.set_attribute("user.error", str(e))
                span.set_attribute("user.success", False)
                raise
    
    @trace
    async def create_user(self, user_data: dict):
        """Create a new user."""
        
        with self.tracer.start_span("user-creation") as span:
            span.set_attribute("user.email", user_data.get("email", ""))
            span.set_attribute("user.role", user_data.get("role", "user"))
            
            try:
                # Validate user data
                self._validate_user_data(user_data)
                
                # Make HTTP request
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/users",
                        json=user_data
                    )
                    
                    span.set_attribute("http.status_code", response.status_code)
                    
                    if response.status_code == 201:
                        created_user = response.json()
                        span.set_attribute("user.created", True)
                        span.set_attribute("user.id", created_user.get("id"))
                        return created_user
                    else:
                        span.set_attribute("user.created", False)
                        span.set_attribute("http.error", response.text)
                        raise HTTPException(response.status_code, response.text)
                        
            except Exception as e:
                span.set_attribute("user.error", str(e))
                span.set_attribute("user.success", False)
                raise
    
    def _validate_user_data(self, user_data: dict):
        """Validate user data before creation."""
        
        with self.tracer.enrich_span("user-validation", {"step": "validation"}):
            required_fields = ["email", "name"]
            missing_fields = [field for field in required_fields if field not in user_data]
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            # Validate email format
            if not self._is_valid_email(user_data["email"]):
                raise ValueError("Invalid email format")
    
    def _is_valid_email(self, email: str):
        """Check if email format is valid."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    async def batch_get_users(self, user_ids: list):
        """Get multiple users in batch."""
        
        with self.tracer.start_span("batch-user-lookup") as span:
            span.set_attribute("batch.size", len(user_ids))
            span.set_attribute("batch.user_ids", str(user_ids))
            
            results = {}
            errors = []
            
            for user_id in user_ids:
                try:
                    user = await self.get_user(user_id)
                    if user:
                        results[user_id] = user
                    else:
                        errors.append(f"User {user_id} not found")
                except Exception as e:
                    errors.append(f"Error fetching user {user_id}: {str(e)}")
            
            span.set_attribute("batch.success_count", len(results))
            span.set_attribute("batch.error_count", len(errors))
            span.set_attribute("batch.errors", str(errors))
            
            return {
                "results": results,
                "errors": errors,
                "total_requested": len(user_ids),
                "total_found": len(results)
            }

# Usage
user_service = UserService()

# Get single user
user = await user_service.get_user("123")

# Create user
new_user = await user_service.create_user({
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
})

# Batch get users
batch_results = await user_service.batch_get_users(["123", "456", "789"])
```

---

## Experiment Tracking

### MLflow Integration

Automatically track experiments with MLflow:

```python
import os
from honeyhive import HoneyHiveTracer, trace
import mlflow

# MLflow automatically sets environment variables
# MLFLOW_EXPERIMENT_ID and MLFLOW_EXPERIMENT_NAME

# Initialize tracer (automatically detects MLflow variables)
tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="ml-experiments",
    source="research"
)

@trace(event_type="model_training", event_name="train_model")
def train_model(model_config: dict):
    """Train a machine learning model with experiment tracking."""
    
    # MLflow experiment context automatically available in all spans
    with tracer.start_span("model_training") as span:
        span.set_attribute("model.type", model_config["type"])
        span.set_attribute("model.parameters", str(model_config["parameters"]))
        
        # Your training code here
        model = create_model(model_config)
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=model_config["epochs"]
        )
        
        # Log metrics
        span.set_attribute("training.epochs", model_config["epochs"])
        span.set_attribute("training.final_loss", float(history.history["loss"][-1]))
        span.set_attribute("training.final_val_loss", float(history.history["val_loss"][-1]))
        
        return model

# Usage
mlflow.set_experiment("my_experiment")
with mlflow.start_run():
    # MLflow automatically sets MLFLOW_EXPERIMENT_ID and MLFLOW_EXPERIMENT_NAME
    model = train_model({
        "type": "neural_network",
        "parameters": {"layers": [64, 32], "dropout": 0.2},
        "epochs": 100
    })
```

### A/B Testing with Experiment Variants

Track different experiment variants:

```python
import os
from honeyhive import HoneyHiveTracer, trace

# Set experiment variant for A/B testing
os.environ["HH_EXPERIMENT_ID"] = "ab_test_001"
os.environ["HH_EXPERIMENT_NAME"] = "recommendation_algorithm"
os.environ["HH_EXPERIMENT_VARIANT"] = "collaborative_filtering"
os.environ["HH_EXPERIMENT_GROUP"] = "treatment"

tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="recommendation_system",
    source="production"
)

@trace(event_type="recommendation", event_name="generate_recommendations")
def generate_recommendations(user_id: str, algorithm: str):
    """Generate recommendations with experiment tracking."""
    
    with tracer.start_span("recommendation_generation") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("algorithm.type", algorithm)
        
        # Your recommendation logic here
        if algorithm == "collaborative_filtering":
            recommendations = collaborative_filtering_recommend(user_id)
        else:
            recommendations = content_based_recommend(user_id)
        
        span.set_attribute("recommendations.count", len(recommendations))
        span.set_attribute("recommendations.algorithm", algorithm)
        
        return recommendations

# Usage
recommendations = generate_recommendations("user_123", "collaborative_filtering")
```

### Hyperparameter Optimization

Track hyperparameter experiments:

```python
import os
from honeyhive import HoneyHiveTracer, trace
import optuna

# Set experiment metadata for hyperparameter optimization
os.environ["HH_EXPERIMENT_ID"] = "hyperopt_001"
os.environ["HH_EXPERIMENT_NAME"] = "transformer_optimization"
os.environ["HH_EXPERIMENT_METADATA"] = '{"optimization_type": "hyperopt", "search_space": "transformer"}'

tracer = HoneyHiveTracer(
    api_key="your-api-key",
    project="nlp_optimization",
    source="research"
)

@trace(event_type="hyperparameter_optimization", event_name="optimize_model")
def optimize_hyperparameters(trial: optuna.Trial):
    """Optimize model hyperparameters with experiment tracking."""
    
    with tracer.start_span("hyperparameter_trial") as span:
        # Suggest hyperparameters
        learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-2, log=True)
        batch_size = trial.suggest_categorical("batch_size", [16, 32, 64, 128])
        num_layers = trial.suggest_int("num_layers", 2, 6)
        
        # Set trial attributes
        span.set_attribute("trial.number", trial.number)
        span.set_attribute("hyperparameters.learning_rate", learning_rate)
        span.set_attribute("hyperparameters.batch_size", batch_size)
        span.set_attribute("hyperparameters.num_layers", num_layers)
        
        # Train model with suggested hyperparameters
        model = create_model(learning_rate=learning_rate, num_layers=num_layers)
        history = train_model(model, batch_size=batch_size)
        
        # Log performance metrics
        final_accuracy = history.history["accuracy"][-1]
        span.set_attribute("performance.final_accuracy", final_accuracy)
        
        return final_accuracy

# Usage
study = optuna.create_study(direction="maximize")
study.optimize(optimize_hyperparameters, n_trials=100)
```

### Multi-Environment Experiment Tracking

Track experiments across different environments:

```python
import os
from honeyhive import HoneyHiveTracer, trace

def setup_experiment_tracking(environment: str, experiment_name: str):
    """Setup experiment tracking for different environments."""
    
    # Common experiment variables
    os.environ["HH_EXPERIMENT_NAME"] = experiment_name
    
    if environment == "development":
        os.environ["HH_EXPERIMENT_ID"] = f"dev_{experiment_name}_001"
        os.environ["HH_EXPERIMENT_GROUP"] = "development"
        os.environ["HH_EXPERIMENT_METADATA"] = '{"environment": "dev", "debug": true}'
        
    elif environment == "staging":
        os.environ["HH_EXPERIMENT_ID"] = f"staging_{experiment_name}_001"
        os.environ["HH_EXPERIMENT_GROUP"] = "staging"
        os.environ["HH_EXPERIMENT_METADATA"] = '{"environment": "staging", "debug": false}'
        
    elif environment == "production":
        os.environ["HH_EXPERIMENT_ID"] = f"prod_{experiment_name}_001"
        os.environ["HH_EXPERIMENT_GROUP"] = "production"
        os.environ["HH_EXPERIMENT_METADATA"] = '{"environment": "prod", "debug": false}'
    
    # Initialize tracer
    return HoneyHiveTracer(
        api_key=os.getenv("HH_API_KEY"),
        project=f"{environment}-experiments",
        source=environment
    )

# Usage
tracer = setup_experiment_tracking("staging", "model_evaluation")

with tracer.start_span("model_evaluation") as span:
    # All spans automatically include experiment context
    # - honeyhive.experiment_id: "staging_model_evaluation_001"
    # - honeyhive.experiment_name: "model_evaluation"
    # - honeyhive.experiment_group: "staging"
    # - honeyhive.experiment_metadata.environment: "staging"
    # - honeyhive.experiment_metadata.debug: "false"
    pass
```

---

## Best Practices

### 1. Span Naming
- Use descriptive, hierarchical names
- Include service and operation context
- Be consistent across your application

### 2. Attribute Management
- Set relevant business attributes
- Include performance metrics
- Avoid sensitive information

### 3. Error Handling
- Always capture error details in spans
- Set success/failure flags
- Include error context and stack traces

### 4. Performance Monitoring
- Track operation durations
- Monitor resource usage
- Set performance thresholds

---

These examples demonstrate real-world usage patterns for the HoneyHive SDK. Adapt them to your specific use case and requirements.

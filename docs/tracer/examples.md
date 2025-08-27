# HoneyHive Tracer Examples & Tutorials

This document provides practical examples and tutorials for using the HoneyHive tracer in various scenarios.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Web Application Examples](#web-application-examples)
- [API Service Examples](#api-service-examples)
- [Background Job Examples](#background-job-examples)
- [Performance Optimization Examples](#performance-optimization-examples)
- [Testing Examples](#testing-examples]
- [Integration Examples](#integration-examples)
- [Error Handling Examples](#error-handling-examples)

## Basic Examples

### Simple Function Tracing

```python
from honeyhive.tracer import trace

@trace
def calculate_fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)

# Usage
result = calculate_fibonacci(10)
```

### Async Function Tracing

```python
import asyncio
from honeyhive.tracer import trace

@trace
async def fetch_data(url: str) -> str:
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

# Usage
async def main():
    data = await fetch_data("https://api.example.com/data")
    print(data)

asyncio.run(main())
```

### Class Method Tracing

```python
from honeyhive.tracer import trace_class

@trace_class
class UserService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_user(self, user_data):
        # This method will be automatically traced
        user_id = self.db.insert_user(user_data)
        return user_id
    
    def get_user(self, user_id):
        # This method will be automatically traced
        return self.db.get_user(user_id)
    
    def _validate_user_data(self, user_data):
        # Private methods are not traced by default
        return user_data is not None

# Usage
service = UserService(db_connection)
user_id = service.create_user({"name": "John", "email": "john@example.com"})
user = service.get_user(user_id)
```

### Selective Class Tracing

```python
from honeyhive.tracer import trace_class

@trace_class(include_list=["public_method", "async_method"])
class SelectiveService:
    def public_method(self):
        # This will be traced
        return "public"
    
    def async_method(self):
        # This will be traced
        return "async"
    
    def internal_method(self):
        # This will NOT be traced
        return "internal"
    
    def _private_method(self):
        # This will NOT be traced (dunder methods excluded)
        return "private"
```

### Legacy Async Tracing

```python
from honeyhive.tracer import atrace

@atrace
async def legacy_async_function():
    # This uses the legacy @atrace decorator
    await asyncio.sleep(0.1)
    return "legacy async result"

# Note: @atrace only works with async functions
# Using it on sync functions will raise ValueError
```

## Web Application Examples

### Flask Application

```python
from flask import Flask, request, jsonify
from honeyhive.tracer import trace, HoneyHiveOTelTracer
from honeyhive.tracer.http_instrumentation import instrument_http

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="web-app",
    source="production"
)

# Enable HTTP instrumentation
instrument_http()

app = Flask(__name__)

@app.route('/users', methods=['POST'])
@trace
def create_user():
    user_data = request.get_json()
    
    # Add custom metadata to the span
    from honeyhive.tracer import enrich_span
    enrich_span(
        config={"endpoint": "/users", "method": "POST"},
        metadata={"user_email": user_data.get("email")}
    )
    
    # User creation logic
    user_id = create_user_in_db(user_data)
    
    return jsonify({"user_id": user_id, "status": "created"}), 201

@app.route('/users/<int:user_id>', methods=['GET'])
@trace
def get_user(user_id):
    user = get_user_from_db(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user)

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Application

```python
from fastapi import FastAPI, HTTPException
from honeyhive.tracer import trace, HoneyHiveOTelTracer
from honeyhive.tracer.http_instrumentation import instrument_http
from honeyhive.tracer.asyncio_tracer import instrument_asyncio

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="fastapi-app",
    source="production"
)

# Enable HTTP and asyncio instrumentation
instrument_http()
instrument_asyncio()

app = FastAPI()

@app.post("/items")
@trace
async def create_item(item_data: dict):
    # Add custom metadata
    from honeyhive.tracer import enrich_span
    enrich_span(
        config={"endpoint": "/items", "method": "POST"},
        metadata={"item_type": item_data.get("type")}
    )
    
    # Item creation logic
    item_id = await create_item_in_db(item_data)
    
    return {"item_id": item_id, "status": "created"}

@app.get("/items/{item_id}")
@trace
async def get_item(item_id: int):
    item = await get_item_from_db(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item

@app.get("/items")
@trace
async def list_items(skip: int = 0, limit: int = 100):
    items = await get_items_from_db(skip, limit)
    return {"items": items, "skip": skip, "limit": limit}
```

### Django Application

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from honeyhive.tracer import trace, HoneyHiveOTelTracer
from honeyhive.tracer.http_instrumentation import instrument_http

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="django-app",
    source="production"
)

# Enable HTTP instrumentation
instrument_http()

@csrf_exempt
@require_http_methods(["POST"])
@trace
def create_user_view(request):
    import json
    
    # Add custom metadata
    from honeyhive.tracer import enrich_span
    enrich_span(
        config={"endpoint": "/users", "method": "POST"},
        metadata={"view": "create_user_view"}
    )
    
    try:
        user_data = json.loads(request.body)
        user_id = create_user_in_db(user_data)
        return JsonResponse({"user_id": user_id, "status": "created"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@trace
def get_user_view(request, user_id):
    user = get_user_from_db(user_id)
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    return JsonResponse(user)
```

## API Service Examples

### REST API Service

```python
import httpx
from honeyhive.tracer import trace, HoneyHiveOTelTracer
from honeyhive.tracer.http_instrumentation import instrument_http

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="rest-api",
    source="production"
)

# Enable HTTP instrumentation
instrument_http()

class UserAPIService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client()
    
    @trace
    def create_user(self, user_data: dict) -> dict:
        # Add custom metadata
        from honeyhive.tracer import enrich_span
        enrich_span(
            config={"service": "user-api", "operation": "create"},
            metadata={"user_email": user_data.get("email")}
        )
        
        response = self.client.post(f"{self.base_url}/users", json=user_data)
        response.raise_for_status()
        return response.json()
    
    @trace
    def get_user(self, user_id: int) -> dict:
        response = self.client.get(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    @trace
    def update_user(self, user_id: int, user_data: dict) -> dict:
        response = self.client.put(f"{self.base_url}/users/{user_id}", json=user_data)
        response.raise_for_status()
        return response.json()
    
    @trace
    def delete_user(self, user_id: int) -> bool:
        response = self.client.delete(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return True

# Usage
user_service = UserAPIService("https://api.example.com")
new_user = user_service.create_user({"name": "John", "email": "john@example.com"})
user = user_service.get_user(new_user["id"])
```

### GraphQL Service

```python
import asyncio
from honeyhive.tracer import trace, HoneyHiveOTelTracer
from honeyhive.tracer.asyncio_tracer import instrument_asyncio

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="graphql-api",
    source="production"
)

# Enable asyncio instrumentation
instrument_asyncio()

class GraphQLService:
    def __init__(self):
        self.schema = self._load_schema()
    
    @trace
    async def execute_query(self, query: str, variables: dict = None) -> dict:
        # Add custom metadata
        from honeyhive.tracer import enrich_span
        enrich_span(
            config={"service": "graphql", "operation": "query"},
            metadata={"query": query[:100]}  # Truncate long queries
        )
        
        # GraphQL execution logic
        result = await self._execute_graphql(query, variables)
        return result
    
    @trace
    async def execute_mutation(self, mutation: str, variables: dict = None) -> dict:
        from honeyhive.tracer import enrich_span
        enrich_span(
            config={"service": "graphql", "operation": "mutation"},
            metadata={"mutation": mutation[:100]}
        )
        
        result = await self._execute_graphql(mutation, variables)
        return result
    
    async def _execute_graphql(self, operation: str, variables: dict = None) -> dict:
        # Simulated GraphQL execution
        await asyncio.sleep(0.1)
        return {"data": {"result": "success"}, "errors": []}

# Usage
async def main():
    service = GraphQLService()
    
    query = """
    query GetUser($id: ID!) {
        user(id: $id) {
            id
            name
            email
        }
    }
    """
    
    result = await service.execute_query(query, {"id": "123"})
    print(result)

asyncio.run(main())
```

## Background Job Examples

### Celery Tasks

```python
from celery import Celery
from honeyhive.tracer import trace, HoneyHiveOTelTracer

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="background-jobs",
    source="production"
)

# Initialize Celery
celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
@trace
def process_user_data(user_id: int, data: dict):
    # Add custom metadata
    from honeyhive.tracer import enrich_span
    enrich_span(
        config={"task": "process_user_data", "queue": "user_processing"},
        metadata={"user_id": user_id, "data_size": len(str(data))}
    )
    
    # Process user data
    result = process_data(data)
    
    # Update user record
    update_user_record(user_id, result)
    
    return {"status": "completed", "user_id": user_id}

@celery_app.task
@trace
def send_notification(user_id: int, message: str):
    from honeyhive.tracer import enrich_span
    enrich_span(
        config={"task": "send_notification", "queue": "notifications"},
        metadata={"user_id": user_id, "message_length": len(message)}
    )
    
    # Send notification logic
    send_email(user_id, message)
    
    return {"status": "sent", "user_id": user_id}

# Usage
def trigger_background_jobs(user_id: int, data: dict):
    # Process data
    process_user_data.delay(user_id, data)
    
    # Send notification
    send_notification.delay(user_id, "Your data has been processed!")
```

### Scheduled Jobs

```python
import schedule
import time
from honeyhive.tracer import trace, HoneyHiveOTelTracer

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="scheduled-jobs",
    source="production"
)

@trace
def daily_cleanup():
    """Daily cleanup job that runs at 2 AM"""
    from honeyhive.tracer import enrich_span
    enrich_span(
        config={"job": "daily_cleanup", "schedule": "daily_2am"},
        metadata={"job_type": "cleanup", "frequency": "daily"}
    )
    
    # Cleanup logic
    cleanup_old_logs()
    cleanup_temp_files()
    cleanup_database_cache()
    
    print("Daily cleanup completed")

@trace
def hourly_health_check():
    """Hourly health check job"""
    from honeyhive.tracer import enrich_span
    enrich_span(
        config={"job": "hourly_health_check", "schedule": "hourly"},
        metadata={"job_type": "health_check", "frequency": "hourly"}
    )
    
    # Health check logic
    check_database_connection()
    check_external_services()
    check_system_resources()
    
    print("Hourly health check completed")

# Schedule jobs
schedule.every().day.at("02:00").do(daily_cleanup)
schedule.every().hour.do(hourly_health_check)

# Run scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
```

## Performance Optimization Examples

### Conditional Tracing

```python
from honeyhive.tracer import trace, enable_tracing, HoneyHiveOTelTracer

# Initialize tracer with performance optimizations
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="performance-app",
    source="production"
)

# Enable conditional tracing
enable_tracing(
    enabled=True,
    min_duration_ms=10.0,      # Only trace operations > 10ms
    max_spans_per_second=100   # Rate limit to 100 spans/second
)

@trace
def fast_operation():
    """This operation is fast and won't be traced"""
    return "fast result"

@trace
def slow_operation():
    """This operation is slow and will be traced"""
    import time
    time.sleep(0.1)  # 100ms - above threshold
    return "slow result"

@trace
def very_slow_operation():
    """This operation is very slow and will be traced"""
    import time
    time.sleep(0.5)  # 500ms - well above threshold
    return "very slow result"
```

### Rate Limiting

```python
from honeyhive.tracer import trace, enable_tracing

# Enable rate limiting
enable_tracing(
    enabled=True,
    min_duration_ms=1.0,
    max_spans_per_second=10  # Very low rate limit for testing
)

@trace
def high_volume_function():
    """This function is called frequently but tracing is rate limited"""
    return "high volume result"

# Simulate high volume calls
for i in range(100):
    result = high_volume_function()
    # Only ~10 calls will be traced due to rate limiting
```

### Span Filtering

```python
from honeyhive.tracer import trace, should_trace_span

def conditional_function():
    """Function with conditional tracing logic"""
    if should_trace_span(estimated_duration_ms=50):
        # Only trace if we expect it to take > 50ms
        with trace("conditional_operation"):
            import time
            time.sleep(0.1)
            return "traced result"
    else:
        return "untraced result"

# Usage
result1 = conditional_function()  # Won't be traced (fast)
result2 = conditional_function()  # Will be traced (slow)
```

## Testing Examples

### Test Mode Initialization

```python
import pytest
from honeyhive.tracer import HoneyHiveOTelTracer

def test_tracer_initialization():
    """Test tracer initialization in test mode"""
    # Test mode provides simplified initialization
    tracer = HoneyHiveOTelTracer(
        test_mode=True,
        project="test-project"
    )
    
    # Verify test mode behavior
    assert tracer._test_mode == True
    assert tracer.project == "test-project"
    assert tracer.source == "dev"  # Default source
    
    # Test mode doesn't make external API calls
    # All operations are mocked for testing

def test_tracer_with_session_id():
    """Test tracer with existing session ID"""
    session_id = "12345678-1234-1234-1234-123456789012"
    
    tracer = HoneyHiveOTelTracer(
        session_id=session_id,
        test_mode=True,
        project="test-project"
    )
    
    assert tracer.session_id == session_id.lower()

def test_invalid_session_id():
    """Test that invalid session ID is handled gracefully"""
    # The tracer catches validation errors and continues
    tracer = HoneyHiveOTelTracer(
        session_id="invalid-uuid",
        test_mode=True,
        project="test-project"
    )
    
    # Tracer still initializes, but session_id validation error is logged
    assert tracer.project == "test-project"
```

### Mocking and Patching

```python
import pytest
from unittest.mock import patch, Mock
from honeyhive.tracer import HoneyHiveOTelTracer

def test_tracer_with_mocked_api():
    """Test tracer with mocked HoneyHive API"""
    with patch('honeyhive.sdk.HoneyHive') as mock_honeyhive:
        # Mock API responses
        mock_honeyhive.return_value.create_session.return_value = {"id": "test-session"}
        
        tracer = HoneyHiveOTelTracer(
            test_mode=True,
            project="test-project"
        )
        
        # Verify API was called with mocked response
        mock_honeyhive.assert_called_once()

def test_span_processor_mocking():
    """Test span processor with mocked spans"""
    from honeyhive.tracer import HoneyHiveSpanProcessor
    
    processor = HoneyHiveSpanProcessor()
    
    # Create mock span
    mock_span = Mock()
    mock_span.name = "test_span"
    mock_span.set_attribute = Mock()
    
    # Test span processing
    processor.on_start(mock_span)
    processor.on_end(mock_span)
    
    # Verify span attributes were set
    assert mock_span.set_attribute.called
```

### Integration Testing

```python
import pytest
import asyncio
from honeyhive.tracer import trace, HoneyHiveOTelTracer
from honeyhive.tracer.http_instrumentation import instrument_http

@pytest.fixture
def tracer():
    """Fixture for tracer in test mode"""
    return HoneyHiveOTelTracer(
        test_mode=True,
        project="test-project"
    )

@pytest.fixture
def http_instrumentation():
    """Fixture for HTTP instrumentation"""
    instrument_http()
    yield
    # Cleanup is automatic

def test_http_instrumentation_integration(tracer, http_instrumentation):
    """Test HTTP instrumentation integration"""
    import requests
    
    # Make HTTP request - should be automatically traced
    response = requests.get("https://httpbin.org/get")
    
    # Verify response
    assert response.status_code == 200
    
    # In a real test, you would verify that spans were created
    # This requires more complex OpenTelemetry testing setup

@pytest.mark.asyncio
async def test_async_instrumentation_integration(tracer):
    """Test asyncio instrumentation integration"""
    from honeyhive.tracer.asyncio_tracer import instrument_asyncio
    
    instrument_asyncio()
    
    @trace
    async def test_coroutine():
        await asyncio.sleep(0.1)
        return "async result"
    
    # Execute coroutine
    result = await test_coroutine()
    assert result == "async result"
```

## Integration Examples

### SQLAlchemy Integration

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from honeyhive.tracer import trace, HoneyHiveOTelTracer

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="database-app",
    source="production"
)

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///test.db')
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

Base.metadata.create_all(engine)

@trace
def create_user(name: str, email: str) -> int:
    """Create a new user in the database"""
    from honeyhive.tracer import enrich_span
    enrich_span(
        config={"operation": "create_user", "table": "users"},
        metadata={"user_name": name, "user_email": email}
    )
    
    session = Session()
    try:
        user = User(name=name, email=email)
        session.add(user)
        session.commit()
        return user.id
    finally:
        session.close()

@trace
def get_user(user_id: int) -> dict:
    """Get user from database"""
    session = Session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return {"id": user.id, "name": user.name, "email": user.email}
        return None
    finally:
        session.close()

# Usage
user_id = create_user("John Doe", "john@example.com")
user = get_user(user_id)
print(f"Created user: {user}")
```

### Redis Integration

```python
import redis
from honeyhive.tracer import trace, HoneyHiveOTelTracer

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="cache-app",
    source="production"
)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@trace
def cache_user_data(user_id: str, user_data: dict) -> bool:
    """Cache user data in Redis"""
    from honeyhive.tracer import enrich_span
    enrich_span(
        config={"operation": "cache_user", "cache": "redis"},
        metadata={"user_id": user_id, "data_size": len(str(user_data))}
    )
    
    try:
        # Set cache with expiration
        redis_client.setex(f"user:{user_id}", 3600, str(user_data))
        return True
    except Exception as e:
        # Log error but continue operation
        print(f"Cache error: {e}")
        return False

@trace
def get_cached_user(user_id: str) -> dict:
    """Get cached user data from Redis"""
    try:
        cached_data = redis_client.get(f"user:{user_id}")
        if cached_data:
            return eval(cached_data)  # In production, use proper serialization
        return None
    except Exception as e:
        print(f"Cache retrieval error: {e}")
        return None

# Usage
user_data = {"name": "John", "email": "john@example.com"}
cache_user_data("123", user_data)
cached_user = get_cached_user("123")
print(f"Cached user: {cached_user}")
```

## Error Handling Examples

### Graceful Error Handling

```python
from honeyhive.tracer import trace, HoneyHiveOTelTracer
from honeyhive.models.errors.sdkerror import SDKError

# Initialize tracer
tracer = HoneyHiveOTelTracer(
    api_key="your-api-key",
    project="error-handling-app",
    source="production"
)

@trace
def robust_function(data: dict) -> dict:
    """Function with robust error handling"""
    try:
        # Add custom metadata
        from honeyhive.tracer import enrich_span
        enrich_span(
            config={"operation": "robust_function"},
            metadata={"input_size": len(str(data))}
        )
        
        # Process data
        result = process_data(data)
        
        # Add success metadata
        enrich_span(
            config={"status": "success"},
            metadata={"result_size": len(str(result))}
        )
        
        return result
        
    except Exception as e:
        # Add error metadata
        from honeyhive.tracer import enrich_span
        enrich_span(
            config={"status": "error"},
            metadata={"error_type": type(e).__name__, "error_message": str(e)}
        )
        
        # Re-raise or handle as needed
        raise

def handle_tracer_errors():
    """Example of handling tracer-specific errors"""
    try:
        # This will raise SDKError for invalid project
        tracer = HoneyHiveOTelTracer(project="")
    except SDKError as e:
        print(f"Tracer configuration error: {e}")
        # Handle configuration error
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle unexpected error
```

### Fallback Behavior

```python
from honeyhive.tracer import trace, HoneyHiveOTelTracer

@trace
def function_with_fallback(data: dict) -> dict:
    """Function that continues operation even with errors"""
    try:
        # Primary operation
        result = primary_operation(data)
        return result
    except Exception as e:
        # Fallback operation
        print(f"Primary operation failed: {e}, using fallback")
        result = fallback_operation(data)
        return result

def tracer_fallback_example():
    """Example of tracer fallback behavior"""
    try:
        # Try to initialize with invalid API key
        tracer = HoneyHiveOTelTracer(
            api_key="invalid-key",
            project="test-project"
        )
        
        # Tracer will log error but continue initialization
        print("Tracer initialized with fallback behavior")
        
    except Exception as e:
        print(f"Tracer failed completely: {e}")
```

---

*These examples demonstrate the current capabilities of the HoneyHive tracer module. For detailed API information, see the [api_reference.md](api_reference.md) file.*

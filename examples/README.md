# HoneyHive SDK Examples

This directory contains practical examples demonstrating how to use the HoneyHive SDK for observability and tracing in various scenarios.

## Quick Start

1. **Install the SDK**:
   ```bash
   pip install -e .
   ```

2. **Set up environment variables**:
   ```bash
   export HH_API_KEY="your-honeyhive-api-key"
   export HH_PROJECT="your-project-name"
   export HH_SOURCE="production"
   ```

3. **Run the examples**:
   ```bash
   python examples/simple_agent_integration.py
   python examples/agent_google_ai_integration.py
   ```

## Available Examples

### 1. Dynamic Trace Decorator (`dynamic_trace_demo.py`)

A demonstration of the new unified trace decorator that automatically handles both synchronous and asynchronous functions:

**Key Features:**
- Single decorator for both sync and async functions
- Automatic detection of function type
- Comprehensive tracing with all existing features
- Backward compatibility with existing `@trace` and `@atrace` decorators

**Usage:**
```bash
python examples/dynamic_trace_demo.py
```

**Example:**
```python
from honeyhive.tracer.decorators import dynamic_trace

@dynamic_trace(event_type="demo", event_name="my_function")
def sync_function():
    return "sync result"

@dynamic_trace(event_type="demo", event_name="my_async_function")
async def async_function():
    return "async result"
```

### 2. Simple Agent Integration (`simple_agent_integration.py`)

A basic example showing:
- HoneyHive tracer initialization
- Session management
- Event logging
- Basic tracing and observability

**Key Features:**
- Simple mock LLM responses
- Question-answer interaction
- Automatic event logging to HoneyHive
- Session tracking

**Usage:**
```bash
python examples/simple_agent_integration.py
```

### 2. Advanced Agent Integration (`agent_google_ai_integration.py`)

A comprehensive example demonstrating:
- Advanced agent framework with tools
- Multi-step execution planning
- Comprehensive tracing and observability
- Tool usage tracking
- Performance monitoring

**Key Features:**
- Tool-based architecture (search, calculator, weather, database)
- Action planning and execution
- Step-by-step tracing
- Rich metadata collection
- Error handling and logging

**Usage:**
```bash
python examples/agent_google_ai_integration.py
```

## What Gets Traced

### Agent Operations
- **Session Management**: Session start/end with metadata
- **Request Processing**: User input, planning, execution
- **Tool Usage**: Tool selection, parameters, results
- **Performance Metrics**: Duration, step counts, success rates

### Events Logged
- **Agent Steps**: Each tool execution step
- **Final Responses**: Completed request results
- **Errors**: Processing failures with context
- **Session Events**: Start, end, and metadata

### Tracing Data
- **Spans**: Request processing, tool execution, response generation
- **Attributes**: User input, tool parameters, results, metadata
- **Context**: Session ID, project, source, timestamps

## Dashboard Features

When you run these examples, you'll see in your HoneyHive dashboard:

### Traces
- **Request Flow**: Complete request processing pipeline
- **Tool Execution**: Individual tool usage and performance
- **Error Paths**: Failed operations with full context

### Metrics
- **Performance**: Response times, throughput
- **Usage**: Tool popularity, success rates
- **Errors**: Failure patterns, error types

### Events
- **Agent Activity**: All agent operations and decisions
- **Tool Usage**: Tool selection and execution results
- **Session Data**: User interaction patterns

## Advanced Patterns

### Custom Tool Integration
```python
@dataclass
class CustomTool:
    name: str
    description: str
    parameters: Dict[str, Any]
    
    def execute(self, **kwargs) -> str:
        # Your tool logic here
        return "Tool result"
```

### Custom Event Logging
```python
def log_custom_event(self, event_type: str, data: Dict[str, Any]):
    event_data = {
        "project": self.project,
        "event_type": event_type,
        "event_name": "custom_event",
        "source": self.source,
        "config": {"custom": True},
        "inputs": data,
        "outputs": {"status": "success"},
        "metadata": {"timestamp": time.time()}
    }
    
    self.client.events.create_event(event_data)
```

### Session Enrichment
```python
from honeyhive.tracer import enrich_session

enrich_session(
    session_id=self.session_id,
    metadata={
        "user_id": "user123",
        "preferences": {"language": "en"},
        "context": "customer_support"
    }
)
```

## Configuration

### Environment Variables
- `HH_API_KEY`: Your HoneyHive API key
- `HH_PROJECT`: Project name for organizing data
- `HH_SOURCE`: Source environment (e.g., "production", "staging")

### SDK Configuration
```python
from honeyhive.utils.config import get_config

config = get_config()
print(f"Project: {config.project}")
print(f"Source: {config.source}")
print(f"API URL: {config.api_url}")
```

## Monitoring and Debugging

### Real-time Monitoring
- **Live Traces**: See requests as they happen
- **Performance Alerts**: Get notified of slow operations
- **Error Tracking**: Monitor failure rates and patterns

### Debugging
- **Request Replay**: Reconstruct failed requests
- **Context Inspection**: View all related spans and events
- **Performance Analysis**: Identify bottlenecks and optimizations

### Best Practices
1. **Use Descriptive Names**: Clear span and event names
2. **Include Context**: Add relevant metadata to all operations
3. **Handle Errors**: Log errors with full context
4. **Monitor Performance**: Track duration and success rates
5. **Organize Data**: Use consistent project and source naming

## Troubleshooting

### Common Issues
1. **Missing API Key**: Ensure `HH_API_KEY` is set
2. **Network Errors**: Check API endpoint accessibility
3. **Import Errors**: Verify SDK installation
4. **Permission Issues**: Check API key permissions

### Debug Mode
Enable debug logging:
```bash
export HH_DEBUG_MODE=true
```

### Testing
Run the setup script to verify everything works:
```bash
chmod +x examples/setup.sh
./examples/setup.sh
```

## Next Steps

1. **Explore the Dashboard**: Check your HoneyHive dashboard for traces and events
2. **Customize Examples**: Modify the examples for your use case
3. **Add Your Tools**: Integrate your own tools and services
4. **Scale Up**: Apply patterns to production applications

For more information, check the main SDK documentation and API reference.

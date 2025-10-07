# Observability Integration Guide

**Instructions for the Cursor Agent: How to add observability tracing to the Agent OS MCP server when a user requests it.**

---

## Overview

By default, the Agent OS MCP server has **no-op observability hooks**. Users can add their preferred observability platform:
- HoneyHive (AI-specific observability)
- OpenTelemetry (universal observability)
- DataDog, New Relic, etc.

This document shows how to integrate each platform.

---

## Integration Pattern

The MCP server has observability hooks in `agent_os_rag.py`:

```python
# Hooks (no-op by default)
OBSERVABILITY_ENABLED = False
tracer = None

def _init_tracer():
    """Initialize observability tracer."""
    pass

def trace(*args, **kwargs):
    """Trace decorator."""
    def decorator(func):
        return func
    return decorator

def enrich_span(data):
    """Enrich span with metadata."""
    pass

def tool_trace(func):
    """Tool-specific trace helper."""
    return func
```

**To add observability:** Replace these no-op implementations with your platform's SDK.

---

## Option 1: HoneyHive Integration

**When to use:** User says "Add HoneyHive tracing" or "I want to dogfood HoneyHive"

### Step 1: Add HoneyHive to requirements.txt

```diff
# .agent-os/mcp_server/requirements.txt

lancedb~=0.25.0
sentence-transformers>=2.0.0
mcp>=1.0.0
watchdog>=3.0.0
+ honeyhive>=0.1.0  # AI observability
```

### Step 2: Replace observability hooks in agent_os_rag.py

```python
# Replace the no-op hooks with:

# HoneyHive tracing - singleton pattern
OBSERVABILITY_ENABLED = False
tracer = None
_tracer_initialized = False

try:
    from honeyhive import HoneyHiveTracer, trace, enrich_span
    from honeyhive.models import EventType
    OBSERVABILITY_ENABLED = os.getenv("HONEYHIVE_ENABLED", "false").lower() == "true"
except ImportError:
    OBSERVABILITY_ENABLED = False


def _init_tracer():
    """Initialize HoneyHive tracer (singleton pattern)."""
    global tracer, _tracer_initialized, OBSERVABILITY_ENABLED
    
    if _tracer_initialized:
        return  # Already initialized
    
    _tracer_initialized = True
    
    if not OBSERVABILITY_ENABLED:
        return
    
    # Initialize tracer with environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HONEYHIVE_PROJECT") or os.getenv("HH_PROJECT")
    
    if api_key and project:
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            source="agent-os-mcp-server",
            verbose=True
        )
        logger.info(f"🍯 HoneyHive tracing enabled (project: {project})")
    else:
        logger.warning(
            "HoneyHive enabled but missing HH_API_KEY or HONEYHIVE_PROJECT, "
            "tracing disabled"
        )
        OBSERVABILITY_ENABLED = False

# No-op decorators if HoneyHive not enabled or available
if not OBSERVABILITY_ENABLED:
    def trace(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def enrich_span(data):
        pass


def tool_trace(func):
    """Helper to apply trace decorator with tracer instance for tools."""
    if OBSERVABILITY_ENABLED and tracer:
        return trace(tracer=tracer, event_type=EventType.tool)(func)
    return func
```

### Step 3: Configure environment variables

Update `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "python",
      "args": ["${workspaceFolder}/.agent-os/mcp_server/agent_os_rag.py"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.agent-os",
        "HONEYHIVE_ENABLED": "true",
        "HH_API_KEY": "${env:HH_API_KEY}",
        "HONEYHIVE_PROJECT": "${env:HH_PROJECT}"
      }
    }
  }
}
```

### Step 4: Test HoneyHive tracing

```bash
# Set environment variables
export HH_API_KEY="your-api-key"
export HH_PROJECT="your-project-name"

# Restart Cursor
# Use MCP tools
# Check HoneyHive dashboard for traces
```

---

## Option 2: OpenTelemetry Integration

**When to use:** User says "Add OpenTelemetry" or "I want OTEL tracing"

### Step 1: Add OpenTelemetry to requirements.txt

```diff
# .agent-os/mcp_server/requirements.txt

lancedb~=0.25.0
sentence-transformers>=2.0.0
mcp>=1.0.0
watchdog>=3.0.0
+ opentelemetry-api>=1.20.0
+ opentelemetry-sdk>=1.20.0
+ opentelemetry-exporter-otlp>=1.20.0
```

### Step 2: Replace observability hooks in agent_os_rag.py

```python
# Replace the no-op hooks with:

from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

OBSERVABILITY_ENABLED = False
tracer = None


def _init_tracer():
    """Initialize OpenTelemetry tracer."""
    global tracer, OBSERVABILITY_ENABLED
    
    if os.getenv("OTEL_ENABLED", "false").lower() != "true":
        return
    
    # Set up OpenTelemetry
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    ))
    provider.add_span_processor(processor)
    otel_trace.set_tracer_provider(provider)
    
    tracer = otel_trace.get_tracer("agent-os-mcp-server")
    OBSERVABILITY_ENABLED = True
    logger.info("OpenTelemetry tracing enabled")


def trace(*args, **kwargs):
    """OpenTelemetry trace decorator."""
    def decorator(func):
        if not OBSERVABILITY_ENABLED:
            return func
        
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(func.__name__):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def enrich_span(data):
    """Enrich current span with attributes."""
    if not OBSERVABILITY_ENABLED:
        return
    
    span = otel_trace.get_current_span()
    for key, value in data.items():
        span.set_attribute(key, str(value))


def tool_trace(func):
    """Tool-specific trace helper."""
    return trace()(func)
```

### Step 3: Configure environment variables

Update `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "python",
      "args": ["${workspaceFolder}/.agent-os/mcp_server/agent_os_rag.py"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.agent-os",
        "OTEL_ENABLED": "true",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317"
      }
    }
  }
}
```

---

## Option 3: No Observability (Default)

**When to use:** User doesn't request observability

**No changes needed!** The MCP server works perfectly with no-op hooks.

---

## Testing Observability

### Verify Tracing is Working

1. **Check logs:** Look for initialization message
   ```
   HoneyHive tracing enabled (project: your-project)
   # or
   OpenTelemetry tracing enabled
   ```

2. **Use MCP tool:** Query standards
   ```
   "What are the concurrency best practices?"
   ```

3. **Check your platform:**
   - HoneyHive: Check dashboard for traces
   - OpenTelemetry: Check your OTEL backend (Jaeger, etc.)

### Troubleshooting

**No traces appearing:**
- Check environment variables are set correctly
- Check API keys are valid
- Check OBSERVABILITY_ENABLED is true
- Check logs for error messages

**Import errors:**
- Run: `pip install -r .agent-os/mcp_server/requirements.txt`
- Verify package versions

---

## When User Requests Observability

### User says: "Add HoneyHive tracing"

You (Cursor agent) should:
1. Follow "Option 1: HoneyHive Integration" above
2. Update `requirements.txt`
3. Update `agent_os_rag.py` with HoneyHive code
4. Update `.cursor/mcp.json` with env vars
5. Explain how to set HH_API_KEY and HH_PROJECT

### User says: "Add OpenTelemetry"

You (Cursor agent) should:
1. Follow "Option 2: OpenTelemetry Integration" above
2. Update `requirements.txt`
3. Update `agent_os_rag.py` with OTEL code
4. Update `.cursor/mcp.json` with env vars
5. Explain how to set OTEL endpoint

### User says: "I don't need tracing"

You (Cursor agent) should:
- Say: "Perfect! Agent OS MCP server works great without tracing. The hooks are no-ops by default."

---

## Best Practices

1. **Environment variables over hardcoding:** Always use env vars for API keys
2. **Graceful degradation:** If observability fails to initialize, MCP server should still work
3. **No-op by default:** Never require observability to use Agent OS
4. **Document clearly:** Update README if adding observability

---

**End of Observability Integration Guide**

This ensures Agent OS MCP server remains platform-neutral while supporting any observability platform users want to add.

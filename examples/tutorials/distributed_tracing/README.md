# Distributed Tracing Tutorial Example

This directory contains the complete working code for the **End-to-End Distributed Tracing** tutorial.

## What This Demonstrates

A three-service microservices architecture with distributed tracing:

```
Client → API Gateway → User Service → LLM Service
[------------ Single Unified Trace ------------]
```

## Prerequisites

```bash
pip install honeyhive[openinference-openai] flask requests
```

Set up your environment variables:

```bash
export HH_API_KEY="your-honeyhive-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

## Running the Example

**Terminal 1** - Start LLM Service:
```bash
python llm_service.py
```

**Terminal 2** - Start User Service:
```bash
python user_service.py
```

**Terminal 3** - Start API Gateway:
```bash
python api_gateway.py
```

**Terminal 4** - Test the distributed trace:
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "query": "Explain distributed tracing in one sentence"}'
```

## What You'll See

In your HoneyHive dashboard (https://app.honeyhive.ai), you'll see a single unified trace showing:

1. **API Gateway** (root span) - Entry point
2. **User Service** - Validation and routing
   - User validation sub-span
3. **LLM Service** - AI response generation
   - OpenAI API call sub-span

All with the same trace ID, showing the complete request journey.

## Key Concepts

- **Context Injection**: `inject_context_into_carrier()` adds trace context to HTTP headers
- **Context Extraction**: `extract_context_from_carrier()` extracts context from headers
- **Context Attachment**: `context.attach()` makes spans children of parent trace
- **Unified Tracing**: All services share the same trace ID

## Files

- `api_gateway.py` - Entry point service (port 5000)
- `user_service.py` - Middle tier service (port 5001)
- `llm_service.py` - LLM generation service (port 5002)
- `test_distributed_trace.sh` - Automated test script

## Tutorial Link

For the full step-by-step tutorial, see: [End-to-End Distributed Tracing](../../../docs/tutorials/06-distributed-tracing.rst)


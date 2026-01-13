"""
FastAPI Multi-Session Tracing Example
=====================================

This example demonstrates the recommended pattern for tracing multiple
concurrent requests in a FastAPI server with HoneyHive.

Key Pattern:
- Initialize tracer ONCE at app startup (shared across all requests)
- Use create_session() or acreate_session() in middleware per request
- Session IDs are stored in OpenTelemetry baggage (ContextVar-based)
- Each request is automatically isolated to its own session

Installation:
    pip install honeyhive fastapi uvicorn

Usage:
    # Set your API key
    export HH_API_KEY="your-api-key"
    export HH_PROJECT="your-project"
    
    # Run the server
    uvicorn fastapi_multi_session_example:app --reload
    
    # Test with concurrent requests
    curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" \
         -H "X-User-ID: user-123" -d '{"message": "Hello!"}'
"""

import os
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from honeyhive import HoneyHiveTracer, trace

# =============================================================================
# TRACER INITIALIZATION (ONCE AT APP STARTUP)
# =============================================================================
# The tracer is initialized ONCE and shared across all requests.
# Session isolation is achieved through OpenTelemetry baggage (ContextVar),
# NOT by creating multiple tracer instances.

tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT", "fastapi-example"),
    source=os.getenv("HH_SOURCE", "development"),
)

app = FastAPI(
    title="HoneyHive Multi-Session Example",
    description="Demonstrates per-request session isolation with a global tracer",
)


# =============================================================================
# SESSION MIDDLEWARE
# =============================================================================
# This middleware creates a new session for each request.
# The session_id is stored in OpenTelemetry baggage, which is:
# - ContextVar-based (automatically request-scoped)
# - Propagated to all spans within the request
# - Safe for concurrent requests (no race conditions)


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    """Create isolated session for each request.
    
    acreate_session() creates a session via the HoneyHive API and stores
    the session_id in OpenTelemetry baggage. This enables:
    
    1. Request-scoped isolation (each request has its own session)
    2. No race conditions (session_id is NOT stored on tracer instance)
    3. Automatic span association (span processor reads from baggage)
    """
    # Extract user info from headers (example)
    user_id = request.headers.get("X-User-ID")
    
    # Create session via API (async version for async middleware)
    # If you have an existing session_id, you can pass it directly:
    #   await tracer.acreate_session(session_id=existing_session_id)
    session_id = await tracer.acreate_session(
        session_name=f"api-{request.method}-{request.url.path}",
        inputs={
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
        },
        user_properties={
            "user_id": user_id,
        } if user_id else None,
    )
    
    # Process the request
    response = await call_next(request)
    
    # Enrich session with response data
    # enrich_session reads session_id from baggage automatically
    tracer.enrich_session(
        outputs={"status_code": response.status_code},
        metadata={"completed": True},
    )
    
    # Optionally return session_id to client for debugging/linking
    if session_id:
        response.headers["X-Session-ID"] = session_id
    
    return response


# =============================================================================
# REQUEST MODELS
# =============================================================================


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


# =============================================================================
# ENDPOINTS (Traced)
# =============================================================================
# All endpoints use @trace decorator with explicit tracer reference.
# Spans are automatically associated with the session from middleware.


@app.post("/chat", response_model=ChatResponse)
@trace(event_type="chain", tracer=tracer)
async def chat_endpoint(request: Request, body: ChatRequest) -> ChatResponse:
    """Chat endpoint with automatic session association.
    
    The @trace decorator creates a span that automatically picks up
    the session_id from baggage (set by middleware).
    """
    # Enrich span with input data
    tracer.enrich_span(
        inputs={"message": body.message, "context": body.context},
        metadata={"message_length": len(body.message)},
    )
    
    # Process the message (traced as nested span)
    response = await process_message(body.message, body.context)
    
    # Enrich span with output
    tracer.enrich_span(outputs={"response": response})
    
    # Get session_id from request state (set by middleware)
    # Note: In production, you might want to read this from baggage
    session_id = request.headers.get("X-Session-ID")
    
    return ChatResponse(response=response, session_id=session_id)


@trace(event_type="tool", tracer=tracer)
async def process_message(message: str, context: Optional[str] = None) -> str:
    """Process message - span automatically uses parent's session context.
    
    Nested functions decorated with @trace automatically inherit the
    session context from the parent span.
    """
    tracer.enrich_span(
        inputs={"message": message, "context": context},
        metadata={"step": "message_processing"},
    )
    
    # Simulate LLM call (in real app, this would call OpenAI, Anthropic, etc.)
    response = await generate_response(message)
    
    tracer.enrich_span(outputs={"response": response})
    
    return response


@trace(event_type="model", tracer=tracer)
async def generate_response(message: str) -> str:
    """Simulate LLM response generation.
    
    In a real application, this would call an LLM provider.
    The span is automatically associated with the correct session.
    """
    tracer.enrich_span(
        inputs={"prompt": message},
        metadata={"model": "simulated"},
    )
    
    # Simulate LLM response
    response = f"Response to: {message}"
    
    tracer.enrich_span(
        outputs={"completion": response},
        metadata={"tokens": len(response.split())},
    )
    
    return response


# =============================================================================
# BRING-YOUR-OWN SESSION ID EXAMPLE
# =============================================================================


@app.post("/chat/with-session/{session_id}")
@trace(event_type="chain", tracer=tracer)
async def chat_with_existing_session(
    request: Request, session_id: str, body: ChatRequest
) -> ChatResponse:
    """Chat endpoint that uses an existing session ID.
    
    Use this pattern when you want to link multiple requests to
    the same session (e.g., multi-turn conversations).
    """
    # Set the provided session_id in baggage (no API call)
    tracer.create_session(session_id=session_id)
    
    # Now all spans will use this session_id
    tracer.enrich_span(inputs={"message": body.message})
    
    response = await process_message(body.message, body.context)
    
    return ChatResponse(response=response, session_id=session_id)


# =============================================================================
# HEALTH CHECK
# =============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint (not traced)."""
    return {"status": "healthy"}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("Starting FastAPI server with HoneyHive tracing...")
    print(f"Project: {os.getenv('HH_PROJECT', 'fastapi-example')}")
    print(f"Source: {os.getenv('HH_SOURCE', 'development')}")
    print()
    print("Test with:")
    print('  curl -X POST http://localhost:8000/chat \\')
    print('       -H "Content-Type: application/json" \\')
    print('       -H "X-User-ID: user-123" \\')
    print("       -d '{\"message\": \"Hello!\"}'")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

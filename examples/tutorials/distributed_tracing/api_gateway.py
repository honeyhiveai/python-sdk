"""API Gateway - Entry point for distributed tracing tutorial.

This service initiates the distributed trace and propagates context to downstream services.
"""

from flask import Flask, request, jsonify
from honeyhive import HoneyHiveTracer, trace
from honeyhive.tracer.processing.context import inject_context_into_carrier
from honeyhive.models import EventType
import requests
import os

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="distributed-tracing-tutorial",
    source="api-gateway",
)

app = Flask(__name__)


@app.route("/api/query", methods=["POST"])
@trace(tracer=tracer, event_type=EventType.session)
def handle_query():
    """API Gateway - initiates distributed trace."""

    data = request.get_json()

    tracer.enrich_span(
        {
            "service": "api-gateway",
            "endpoint": "/api/query",
            "user_id": data.get("user_id"),
            "client_ip": request.remote_addr,
        }
    )

    # Inject context into headers for downstream service
    headers = {}
    inject_context_into_carrier(headers, tracer)

    tracer.enrich_span({"propagated_headers": list(headers.keys())})

    # Call user service with trace context
    response = requests.post(
        "http://localhost:5001/process",
        json=data,
        headers=headers,  # Trace context propagates here
        timeout=30,
    )

    tracer.enrich_span(
        {
            "user_service_status": response.status_code,
            "response_size": len(response.content),
        }
    )

    return jsonify(response.json())


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "api-gateway"})


if __name__ == "__main__":
    print("🌐 API Gateway starting on port 5000...")
    print("Environment: HH_API_KEY =", "✓ Set" if os.getenv("HH_API_KEY") else "✗ Missing")
    app.run(port=5000, debug=True, use_reloader=False)


"""User Service - Middle tier service for distributed tracing tutorial.

This service validates users and calls the LLM service, propagating trace context.
"""

from flask import Flask, request, jsonify
from honeyhive import HoneyHiveTracer, trace
from honeyhive.tracer.processing.context import (
    extract_context_from_carrier,
    inject_context_into_carrier,
)
from honeyhive.models import EventType
from opentelemetry import context
import requests
import os

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="distributed-tracing-tutorial",
    source="user-service",
)

app = Flask(__name__)


@app.route("/process", methods=["POST"])
def process():
    """Process user request with distributed tracing."""

    # Extract context from incoming request
    incoming_context = extract_context_from_carrier(dict(request.headers), tracer)

    if incoming_context:
        token = context.attach(incoming_context)

    @trace(tracer=tracer, event_type=EventType.chain)
    def process_user_request(user_id: str, query: str) -> dict:
        """Validate user and call LLM service."""

        tracer.enrich_span(
            {"service": "user-service", "user_id": user_id, "operation": "process_request"}
        )

        # Step 1: Validate user
        is_valid = validate_user(user_id)

        if not is_valid:
            tracer.enrich_span({"validation": "failed"})
            return {"error": "Invalid user"}

        tracer.enrich_span({"validation": "passed"})

        # Step 2: Inject context for downstream service
        headers = {}
        inject_context_into_carrier(headers, tracer)

        # Step 3: Call LLM service with propagated context
        try:
            response = requests.post(
                "http://localhost:5002/generate",
                json={"user_id": user_id, "prompt": query},
                headers=headers,  # Trace context in headers
                timeout=30,
            )

            tracer.enrich_span({"downstream_status": response.status_code})

            return response.json()
        except requests.exceptions.RequestException as e:
            tracer.enrich_span({"error": str(e), "downstream_status": "failed"})
            return {"error": f"Failed to call LLM service: {e}"}

    @trace(tracer=tracer, event_type=EventType.tool)
    def validate_user(user_id: str) -> bool:
        """Validate user - appears as child span."""

        tracer.enrich_span({"operation": "validate_user", "user_id": user_id})

        # Simulate validation logic
        valid = user_id.startswith("user_")
        tracer.enrich_span({"is_valid": valid})

        return valid

    # Execute
    data = request.get_json()
    result = process_user_request(data["user_id"], data["query"])

    if incoming_context:
        context.detach(token)

    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "user-service"})


if __name__ == "__main__":
    print("👤 User Service starting on port 5001...")
    print("Environment: HH_API_KEY =", "✓ Set" if os.getenv("HH_API_KEY") else "✗ Missing")
    app.run(port=5001, debug=True, use_reloader=False)


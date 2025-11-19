"""LLM Service - Downstream service for distributed tracing tutorial.

This service generates LLM responses and continues the distributed trace.
"""

from flask import Flask, request, jsonify
from honeyhive import HoneyHiveTracer, trace
from honeyhive.tracer.processing.context import extract_context_from_carrier
from honeyhive.models import EventType
from opentelemetry import context
from openinference.instrumentation.openai import OpenAIInstrumentor
import openai
import os

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="distributed-tracing-tutorial",
    source="llm-service",
)

# Initialize OpenAI instrumentor
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)

app = Flask(__name__)


@app.route("/generate", methods=["POST"])
def generate():
    """Generate LLM response with distributed trace context."""

    # Step 1: Extract trace context from incoming headers
    incoming_context = extract_context_from_carrier(dict(request.headers), tracer)

    # Step 2: Attach context so our spans are children of parent trace
    if incoming_context:
        token = context.attach(incoming_context)

    # Step 3: Create traced operation
    @trace(tracer=tracer, event_type=EventType.model)
    def generate_response(user_id: str, prompt: str) -> str:
        """Generate LLM response - automatically part of distributed trace."""

        tracer.enrich_span(
            {"service": "llm-service", "user_id": user_id, "prompt_length": len(prompt)}
        )

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content
        tracer.enrich_span({"response_length": len(result)})

        return result

    # Execute traced function
    data = request.get_json()
    try:
        result = generate_response(data["user_id"], data["prompt"])
        response = {"response": result}
    except Exception as e:
        response = {"error": str(e)}

    # Detach context
    if incoming_context:
        context.detach(token)

    return jsonify(response)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "llm-service"})


if __name__ == "__main__":
    print("🔥 LLM Service starting on port 5002...")
    print("Environment: HH_API_KEY =", "✓ Set" if os.getenv("HH_API_KEY") else "✗ Missing")
    print("Environment: OPENAI_API_KEY =", "✓ Set" if os.getenv("OPENAI_API_KEY") else "✗ Missing")
    app.run(port=5002, debug=True, use_reloader=False)


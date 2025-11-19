"""Google ADK Agent Server - Server running a Google ADK agent for distributed tracing.

This server runs a Google ADK agent and accepts requests with distributed trace context.
"""

from flask import Flask, request, jsonify
from honeyhive import HoneyHiveTracer, trace
from honeyhive.tracer.processing.context import with_distributed_trace_context
from honeyhive.models import EventType
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os

# Initialize HoneyHive tracer
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project=os.getenv("HH_PROJECT", "sdk"),
    source="google-adk-agent-server",
    verbose=True
)

# Initialize Google ADK instrumentor
instrumentor = GoogleADKInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)

app = Flask(__name__)
session_service = InMemorySessionService()
app_name = "distributed_agent_demo"

#@trace(tracer=tracer, event_type="chain")
async def run_agent(user_id: str, query: str, agent_name: str = "research_agent") -> str:
    """Run Google ADK agent - automatically part of distributed trace."""
        
    # Create agent
    agent = LlmAgent(
        model="gemini-2.0-flash-exp",
        name=agent_name,
        description="A research agent that gathers comprehensive information on topics" if agent_name == "research_agent" else "An analysis agent that provides insights and conclusions",
        instruction="""You are a research assistant. When given a topic, provide 
        key facts, statistics, and important information in 2-3 clear sentences. 
        Focus on accuracy and relevance.""" if agent_name == "research_agent" else """You are an analytical assistant. Review the information 
        provided and give key insights, implications, and conclusions in 2-3 sentences.""",
        output_key="research_findings" if agent_name == "research_agent" else None
    )
    
    # Create runner and execute
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
    session_id = tracer.session_id if hasattr(tracer, 'session_id') and tracer.session_id else f"{app_name}_{user_id}"
    
    try:
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    except Exception:
        pass  # Session might already exist
    
    user_content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response = ""
    
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
    
    return final_response or ""
            
@app.route("/agent/invoke", methods=["POST"])
async def invoke_agent():
    """Invoke Google ADK agent with distributed trace context."""
    
    # Use context manager for distributed tracing - it automatically:
    # 1. Extracts client's trace context from headers
    # 2. Parses session_id/project/source from baggage
    # 3. Attaches the context (so all spans link to client's trace)
    # 4. Detaches on exit
    with with_distributed_trace_context(dict(request.headers), tracer):
        try:
            data = request.get_json()
            result = await run_agent(
                data.get("user_id", "default_user"),
                data.get("query", ""),
                data.get("agent_name", "research_agent")
            )
            return jsonify({"response": result, "agent": data.get("agent_name", "research_agent")})
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "google-adk-agent-server"})


if __name__ == "__main__":
    print("🤖 Google ADK Agent Server starting on port 5003...")
    app.run(port=5003, debug=True, use_reloader=False)

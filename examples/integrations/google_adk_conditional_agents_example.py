#!/usr/bin/env python3
"""Google ADK Conditional Agents Example with Distributed Tracing

Demonstrates:
- Mixed invocation: Agent 1 (remote/distributed), Agent 2 (local)  
- Baggage propagation across service boundaries
- Google ADK instrumentation with HoneyHive tracing

Requirements: pip install honeyhive google-adk openinference-instrumentation-google-adk requests

Environment:
- HH_API_KEY, HH_PROJECT, GOOGLE_API_KEY (required)
- AGENT_SERVER_URL (optional, default: http://localhost:5003)
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Any
import requests

from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.genai import types

# HoneyHive imports
from honeyhive import HoneyHiveTracer, trace
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# Distributed Tracing imports
from honeyhive.tracer.processing.context import enrich_span_context, inject_context_into_carrier

agent_server_url = os.getenv("AGENT_SERVER_URL", "http://localhost:5003")

def init_honeyhive_telemetry() -> HoneyHiveTracer:
    """Initialize HoneyHive tracer and Google ADK instrumentor."""
    # Initialize tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT"),
        session_name=Path(__file__).stem,
        source="google_adk_conditional_agents"
    )
    # Initialize instrumentor
    adk_instrumentor = GoogleADKInstrumentor()
    adk_instrumentor.instrument(tracer_provider=tracer.provider)
    return tracer

tracer = init_honeyhive_telemetry()

async def main():
    """Main entry point."""
    try:
        # Setup
        session_service = InMemorySessionService()
        app_name = "conditional_agents_demo"
        user_id = "demo_user"

        # Execute two user calls
        await user_call(session_service, app_name, user_id, "Explain the benefits of renewable energy")
        await user_call(session_service, app_name, user_id, "What are the main challenges?")
        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


@trace(event_type="chain", event_name="user_call")
async def user_call(
    session_service: Any,
    app_name: str,
    user_id: str,
    user_query: str
) -> str:
    """User entry point - demonstrates session enrichment."""
    result = await call_principal(session_service, app_name, user_id, user_query, agent_server_url)
    return result


@trace(event_type="chain", event_name="call_principal")
async def call_principal(
    session_service: Any,
    app_name: str,
    user_id: str,
    query: str,
    agent_server_url: Optional[str] = None
) -> str:
    """Principal orchestrator - calls Agent 1 (remote) then Agent 2 (local)."""
    # Agent 1: Research (remote)
    agent_1_result = await call_agent(session_service, app_name, user_id, query, True, agent_server_url)
    
    # Agent 2: Analysis (local) - uses Agent 1's output
    agent_2_result = await call_agent(session_service, app_name, user_id, agent_1_result, False, agent_server_url)
    
    return f"Research: {agent_1_result}\n\nAnalysis: {agent_2_result}"


async def call_agent(
    session_service: Any,
    app_name: str,
    user_id: str,
    query: str,
    use_research_agent: bool = True,
    agent_server_url: Optional[str] = None
) -> str:
    """Conditional agent execution - creates explicit spans for each path."""
    
    # Agent 1: Remote invocation (distributed tracing)
    if use_research_agent:
        with enrich_span_context(event_name="call_agent_1", inputs={"query": query}):
            headers = {}
            inject_context_into_carrier(headers, tracer)
            
            response = requests.post(
                f"{agent_server_url}/agent/invoke",
                json={"user_id": user_id, "query": query, "agent_name": "research_agent"},
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            result = response.json().get("response", "")
            tracer.enrich_span(outputs={"response": result}, metadata={"mode": "remote"})
            return result
    
    # Agent 2: Local invocation (same process)
    else:
        with enrich_span_context(event_name="call_agent_2", inputs={"research": query}):
            agent = LlmAgent(
                model="gemini-2.0-flash-exp",
                name="analysis_agent",
                description="Analysis agent",
                instruction=f"Analyze: {query}\n\nProvide 2-3 sentence analysis."
            )
            
            runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
            session_id = tracer.session_id if hasattr(tracer, 'session_id') and tracer.session_id else f"{app_name}_{user_id}"
            
            try:
                await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
            except Exception:
                pass
            
            user_content = types.Content(role='user', parts=[types.Part(text=f"Analyze: {query[:500]}")])
            result = ""
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
                if event.is_final_response() and event.content and event.content.parts:
                    result = event.content.parts[0].text or ""
            
            tracer.enrich_span(outputs={"response": result}, metadata={"mode": "local"})
            return result


if __name__ == "__main__":
    asyncio.run(main())
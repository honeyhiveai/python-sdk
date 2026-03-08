"""
Super-simple LangGraph + HoneyHive end-to-end smoke test.

Runs a tiny tool-calling agent, flushes traces to HoneyHive prod,
then queries the API to verify the session and its events landed.

Requirements:
    pip install honeyhive langgraph langchain-openai openinference-instrumentation-langchain

Environment variables:
    HH_API_KEY      – HoneyHive bearer token for the "LangGraph" project
    HH_PROJECT      – should be "LangGraph"
    OPENAI_API_KEY  – OpenAI key (gpt-4o-mini is used)
"""

import operator
import os
import sys
import time
from typing import Annotated, Literal, TypedDict

from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from openinference.instrumentation.langchain import LangChainInstrumentor

from honeyhive import HoneyHiveTracer

# ── Configuration ────────────────────────────────────────────────────────────

API_KEY = os.environ["HH_API_KEY"]
PROJECT = os.environ.get("HH_PROJECT", "LangGraph")

# ── 1. Initialise HoneyHive tracer ──────────────────────────────────────────

tracer = HoneyHiveTracer.init(
    api_key=API_KEY,
    project=PROJECT,
    session_name="langgraph-simple-smoke-test",
    # server_url defaults to https://api.honeyhive.ai
)
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

print(f"[setup] HoneyHive tracer initialised – session_id={tracer.session_id}")

# ── 2. Define a minimal tool-calling agent ───────────────────────────────────

model = ChatOpenAI(model="gpt-4o-mini")


@tool
def add(a: float, b: float) -> str:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number
    """
    return str(a + b)


@tool
def multiply(a: float, b: float) -> str:
    """Multiply two numbers together.

    Args:
        a: First number
        b: Second number
    """
    return str(a * b)


tools = [add, multiply]
tools_by_name = {t.name: t for t in tools}
model_with_tools = model.bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


def llm_node(state: AgentState) -> dict:
    """Call the LLM, which may request tool use."""
    response = model_with_tools.invoke(
        [SystemMessage(content="You are a calculator assistant. Use tools.")]
        + state["messages"]
    )
    return {"messages": [response]}


def tool_node(state: AgentState) -> dict:
    """Execute any tool calls the LLM requested."""
    results = []
    for tc in state["messages"][-1].tool_calls:
        result = tools_by_name[tc["name"]].invoke(tc["args"])
        results.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    return {"messages": results}


def should_continue(state: AgentState) -> Literal["tool_node", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "tool_node"
    return END


agent = (
    StateGraph(AgentState)
    .add_node("llm_node", llm_node)
    .add_node("tool_node", tool_node)
    .add_edge(START, "llm_node")
    .add_conditional_edges("llm_node", should_continue, ["tool_node", END])
    .add_edge("tool_node", "llm_node")
    .compile()
)

# ── 3. Run the agent ────────────────────────────────────────────────────────

print("\n[run] Asking: What is 7 + 3, then multiply the result by 4?")
result = agent.invoke(
    {"messages": [HumanMessage(content="What is 7 + 3, then multiply the result by 4?")]}
)
final_answer = result["messages"][-1].content
print(f"[run] Final answer: {final_answer}")

# ── 4. Flush traces and validate ────────────────────────────────────────────

print("\n[validate] Flushing traces...")
tracer.flush(timeout_millis=15000)

# Give the backend a moment to ingest
POLL_DELAY = 5
POLL_RETRIES = 6
print(f"[validate] Waiting {POLL_DELAY}s for backend ingestion...")
time.sleep(POLL_DELAY)

# Use the HoneyHive API client to fetch the session and its events
from honeyhive import HoneyHive  # noqa: E402 – deferred import to keep setup clear

client = HoneyHive(api_key=API_KEY)

session_id = tracer.session_id
assert session_id, "Tracer did not produce a session_id!"

# Retry-poll for the session (traces may take a few seconds to land)
session = None
for attempt in range(1, POLL_RETRIES + 1):
    try:
        session = client.sessions.get(session_id)
        break
    except Exception as exc:
        print(f"[validate] Attempt {attempt}/{POLL_RETRIES} – session not ready: {exc}")
        if attempt < POLL_RETRIES:
            time.sleep(POLL_DELAY)

if session is None:
    print("[FAIL] Could not retrieve session after retries.", file=sys.stderr)
    sys.exit(1)

print(f"[validate] Session retrieved: id={session_id}")

# Fetch events (spans) for the session
events_resp = None
for attempt in range(1, POLL_RETRIES + 1):
    try:
        events_resp = client.events.get_by_session_id(session_id)
        if events_resp and events_resp.events:
            break
    except Exception as exc:
        print(f"[validate] Events attempt {attempt}/{POLL_RETRIES}: {exc}")
    if attempt < POLL_RETRIES:
        time.sleep(POLL_DELAY)

if not events_resp or not events_resp.events:
    print("[FAIL] No events found for session.", file=sys.stderr)
    sys.exit(1)

num_events = len(events_resp.events)
print(f"[validate] Found {num_events} event(s) for session {session_id}")

# Basic sanity: we expect at least 2 events (LLM call + tool call)
if num_events < 2:
    print(f"[WARN] Expected >= 2 events but got {num_events}. Traces may still be arriving.")

# Print event summary
for i, ev in enumerate(events_resp.events):
    ev_dict = ev if isinstance(ev, dict) else (ev.dict() if hasattr(ev, "dict") else vars(ev))
    name = ev_dict.get("event_name", ev_dict.get("name", "unknown"))
    ev_type = ev_dict.get("event_type", "?")
    print(f"  [{i+1}] {name} (type={ev_type})")

print("\n[PASS] LangGraph traces validated successfully on prod!")

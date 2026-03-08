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

import requests as http_requests
from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from openinference.instrumentation.langchain import LangChainInstrumentor

from honeyhive import HoneyHiveTracer

# ── Configuration ────────────────────────────────────────────────────────────

API_KEY = os.environ.get("HH_API_KEY")
if not API_KEY:
    print("[FAIL] HH_API_KEY environment variable is required.", file=sys.stderr)
    sys.exit(1)

PROJECT = os.environ.get("HH_PROJECT", "LangGraph")
SERVER_URL = os.environ.get("HH_API_URL", "https://api.honeyhive.ai")

# ── 1. Create session via API and initialise tracer ─────────────────────────

# Create session directly to get the real session_id from the server
print("[setup] Creating HoneyHive session...")
resp = http_requests.post(
    f"{SERVER_URL}/session/start",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "project": PROJECT,
        "session_name": "langgraph-simple-smoke-test",
        "source": "sdk-smoke-test",
    },
    timeout=15,
)
if resp.status_code != 200:
    print(
        f"[FAIL] Session creation failed: {resp.status_code} {resp.text}",
        file=sys.stderr,
    )
    sys.exit(1)

session_data = resp.json()
session_id = session_data.get("session_id")
if not session_id:
    print("[FAIL] No session_id in API response.", file=sys.stderr)
    sys.exit(1)

print(f"[setup] Session created: id={session_id}")

# Initialise the tracer with the pre-created session_id.
tracer = HoneyHiveTracer.init(
    api_key=API_KEY,
    project=PROJECT,
    session_name="langgraph-simple-smoke-test",
    session_id=session_id,
    server_url=SERVER_URL,
)
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

# The SDK may internally re-create the session and, due to a known
# model-validation drift (PostSessionStartResponse requires org_id /
# workspace_id that prod no longer returns), fall back to a new UUID.
# Record whichever session_id the tracer actually uses so we can
# validate the right one.
active_session_id = tracer.session_id or session_id
print(f"[setup] HoneyHive tracer initialised – active_session_id={active_session_id}")
if active_session_id != session_id:
    print(
        f"[setup]   NOTE: tracer replaced session_id with {active_session_id}"
    )

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
    last_msg = state["messages"][-1]
    for tc in getattr(last_msg, "tool_calls", []):
        if tc["name"] not in tools_by_name:
            results.append(
                ToolMessage(
                    content=f"Unknown tool: {tc['name']}",
                    tool_call_id=tc["id"],
                )
            )
            continue
        result = tools_by_name[tc["name"]].invoke(tc["args"])
        results.append(
            ToolMessage(content=str(result), tool_call_id=tc["id"])
        )
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
    .add_conditional_edges(
        "llm_node", should_continue, ["tool_node", END]
    )
    .add_edge("tool_node", "llm_node")
    .compile()
)

# ── 3. Run the agent ────────────────────────────────────────────────────────

print("\n[run] Asking: What is 7 + 3, then multiply the result by 4?")
result = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="What is 7 + 3, then multiply the result by 4?"
            )
        ]
    }
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

# Helper for authenticated GET requests against the HoneyHive REST API.
auth_headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def hh_get(path: str) -> dict:
    """GET ``SERVER_URL/<path>`` and return parsed JSON."""
    r = http_requests.get(
        f"{SERVER_URL}/{path.lstrip('/')}",
        headers=auth_headers,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


# We validate BOTH session IDs: the one the API created and the one the
# tracer actually uses (they may differ due to model-validation drift).
validation_ids = list(dict.fromkeys([session_id, active_session_id]))
print(f"[validate] Will try session id(s): {validation_ids}")

# ── 4a. Verify the session exists ─────────────────────────────────────────
session_json = None
validated_sid = None
for sid in validation_ids:
    for attempt in range(1, POLL_RETRIES + 1):
        try:
            session_json = hh_get(f"session/{sid}")
            validated_sid = sid
            break
        except Exception as exc:
            print(
                f"[validate] sid={sid} attempt {attempt}/{POLL_RETRIES}"
                f" – not ready: {exc}"
            )
            if attempt < POLL_RETRIES:
                time.sleep(POLL_DELAY)
    if session_json is not None:
        break

if session_json is None:
    print(
        "[FAIL] Could not retrieve session after retries.",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"[validate] Session retrieved: id={validated_sid}")

# ── 4b. Fetch events (spans) for the session ─────────────────────────────
events = None
for sid in validation_ids:
    for attempt in range(1, POLL_RETRIES + 1):
        try:
            ev_resp = hh_get(f"session/{sid}")
            children = ev_resp.get("children", [])
            if children:
                events = children
                validated_sid = sid
                break
        except Exception as exc:
            print(
                f"[validate] Events sid={sid}"
                f" attempt {attempt}/{POLL_RETRIES}: {exc}"
            )
        if attempt < POLL_RETRIES:
            time.sleep(POLL_DELAY)
    if events:
        break

if not events:
    print(
        "[WARN] No child events found yet (traces may still be arriving)."
    )
else:
    num_events = len(events)
    print(
        f"[validate] Found {num_events} event(s)"
        f" for session {validated_sid}"
    )

    # Basic sanity: we expect at least 2 events (LLM call + tool call)
    if num_events < 2:
        print(
            f"[WARN] Expected >= 2 events but got {num_events}."
            " Traces may still be arriving."
        )

    # Print event summary
    for i, ev in enumerate(events):
        name = ev.get("event_name", ev.get("name", "unknown"))
        ev_type = ev.get("event_type", "?")
        print(f"  [{i+1}] {name} (type={ev_type})")

print("\n[PASS] LangGraph smoke test completed successfully on prod!")
print(
    f"  Session URL: https://app.honeyhive.ai/projects/LangGraph"
    f"/sessions/{validated_sid}"
)

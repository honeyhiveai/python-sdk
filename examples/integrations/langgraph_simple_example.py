"""
LangGraph + HoneyHive demo: single-trace and experiment in one script.

Part 1 -- Runs a tool-calling LangGraph agent once and validates the trace.
Part 2 -- Runs the same agent over a small dataset via ``honeyhive.evaluate``
          and prints the experiment report.

Requirements:
    pip install honeyhive langchain langgraph langchain-openai

Environment variables:
    HH_API_KEY      -- HoneyHive bearer token
    HH_PROJECT      -- project name (default: "LangGraph Demo")
    OPENAI_API_KEY  -- OpenAI key (gpt-4o-mini is used)
"""

from __future__ import annotations

import operator
import os
import sys
import time
from typing import Annotated, Literal, TypedDict

import requests as http_requests
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from honeyhive import HoneyHiveTracer, evaluate

# -- Configuration ------------------------------------------------------------

API_KEY = os.environ.get("HH_API_KEY")
if not API_KEY:
    print(
        "[FAIL] HH_API_KEY environment variable is required.",
        file=sys.stderr,
    )
    sys.exit(1)

PROJECT = os.environ.get("HH_PROJECT", "LangGraph Demo")
SERVER_URL = os.environ.get("HH_API_URL", "https://api.honeyhive.ai")

# -- Agent definition ----------------------------------------------------------

llm = ChatOpenAI(model="gpt-4o-mini")


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
llm_with_tools = llm.bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


def llm_node(state: AgentState) -> dict:
    """Call the LLM, which may request tool use."""
    response = llm_with_tools.invoke(
        [SystemMessage(content="You are a calculator assistant. Use tools.")]
        + state["messages"]
    )
    return {"messages": [response]}


def tool_node(state: AgentState) -> dict:
    """Execute any tool calls the LLM requested."""
    results: list[ToolMessage] = []
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
        out = tools_by_name[tc["name"]].invoke(tc["args"])
        results.append(
            ToolMessage(content=str(out), tool_call_id=tc["id"])
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


def run_agent(question: str) -> str:
    """Run the agent on a question and return the final text answer."""
    result = agent.invoke(
        {"messages": [HumanMessage(content=question)]}
    )
    return result["messages"][-1].content


# =============================================================================
# PART 1 -- Single trace
# =============================================================================

print("=" * 60)
print("PART 1: Single traced agent run")
print("=" * 60)

tracer = HoneyHiveTracer.init(
    api_key=API_KEY,
    project=PROJECT,
    session_name="langgraph-single-trace",
    server_url=SERVER_URL,
)

session_id = tracer.session_id
if not session_id:
    print("[FAIL] Tracer did not produce a session_id!", file=sys.stderr)
    sys.exit(1)
print(f"[trace] session_id = {session_id}")

question = "What is 7 + 3, then multiply the result by 4?"
print(f"[trace] Question: {question}")
answer = run_agent(question)
print(f"[trace] Answer:   {answer}")

tracer.flush()
print("[trace] Traces flushed.")

# Quick validation via REST API
POLL_DELAY = 5
POLL_RETRIES = 6
time.sleep(POLL_DELAY)

auth_headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

session_json = None
for attempt in range(1, POLL_RETRIES + 1):
    try:
        r = http_requests.get(
            f"{SERVER_URL}/session/{session_id}",
            headers=auth_headers,
            timeout=15,
        )
        r.raise_for_status()
        session_json = r.json()
        break
    except Exception as exc:
        print(f"[trace] poll {attempt}/{POLL_RETRIES}: {exc}")
        if attempt < POLL_RETRIES:
            time.sleep(POLL_DELAY)

if session_json is None:
    print("[FAIL] Could not retrieve session.", file=sys.stderr)
    sys.exit(1)

children = session_json.get("children", [])
print(f"[trace] Session retrieved -- {len(children)} event(s)")
for i, ev in enumerate(children):
    name = ev.get("event_name", ev.get("name", "?"))
    print(f"  [{i+1}] {name} (type={ev.get('event_type', '?')})")

print(
    f"[trace] URL: https://app.honeyhive.ai/projects/"
    f"{PROJECT}/sessions/{session_id}"
)

# =============================================================================
# PART 2 -- Experiment (evaluate)
# =============================================================================

print("\n" + "=" * 60)
print("PART 2: Experiment run")
print("=" * 60)

# Inline dataset -- each row has inputs + expected ground_truth
dataset = [
    {
        "inputs": {"question": "What is 2 + 3?"},
        "ground_truth": {"expected": "5"},
    },
    {
        "inputs": {"question": "Multiply 6 by 7."},
        "ground_truth": {"expected": "42"},
    },
    {
        "inputs": {"question": "Add 10 and 20, then multiply by 2."},
        "ground_truth": {"expected": "60"},
    },
]


def task_fn(inputs: dict, ground_truth: dict) -> dict:
    """Evaluation task: run the agent and return its answer."""
    q = inputs["question"]
    ans = run_agent(q)
    return {"answer": ans}


def correctness(outputs: dict, inputs: dict, ground_truth: dict) -> int:
    """1 if the expected number appears in the answer, else 0."""
    expected = ground_truth.get("expected", "")
    return 1 if expected in outputs.get("answer", "") else 0


eval_result = evaluate(
    function=task_fn,
    dataset=dataset,
    evaluators=[correctness],
    api_key=API_KEY,
    project=PROJECT,
    name="langgraph-math-experiment",
    server_url=SERVER_URL,
)

print(f"\n[experiment] run_id      = {eval_result.run_id}")
print(f"[experiment] status      = {eval_result.status}")
print(f"[experiment] dataset_id  = {eval_result.dataset_id}")
print(f"[experiment] sessions    = {len(eval_result.session_ids)}")
if eval_result.stats:
    for metric, values in eval_result.stats.items():
        print(f"[experiment] {metric}: {values}")

print("\n" + "=" * 60)
print("[PASS] LangGraph Demo completed successfully.")
print("=" * 60)

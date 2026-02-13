"""
HoneyHive + Strands Agents integration example.

Demonstrates two patterns:
1) Agent with a tool
2) Multi-agent orchestration (agents-as-tools)

Requirements:
    pip install honeyhive strands-agents

Environment variables:
    HH_API_KEY, HH_PROJECT, ANTHROPIC_API_KEY
"""

import os
from contextlib import contextmanager

from honeyhive import HoneyHiveTracer

# --- HoneyHive setup (initialize BEFORE importing Strands) ---

HoneyHiveTracer.init(
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    session_name="strands-agents-example",
)

from strands import Agent, tool  # noqa: E402
from strands.models.anthropic import AnthropicModel  # noqa: E402


def get_model():
    return AnthropicModel(
        client_args={"api_key": os.environ["ANTHROPIC_API_KEY"]},
        model_id=os.getenv("STRANDS_ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=1024,
    )


@contextmanager
def semconv_opt_in(value: str | None):
    """Temporarily set OTEL semconv mode for Strands spans."""
    key = "OTEL_SEMCONV_STABILITY_OPT_IN"
    previous = os.environ.get(key)
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = previous


# --- Pattern 1: Agent with a tool ---

@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    return str(eval(expression, {"__builtins__": {}}, {}))


def run_agent_with_tool(label: str):
    agent = Agent(
        model=get_model(),
        tools=[calculator],
        system_prompt="You are a helpful assistant. Use tools when useful.",
    )
    print(label, agent("What is 25 * 4? Use the calculator tool."))


# Default Strands behavior (GenAI semconv v1.36.0-compatible emission)
with semconv_opt_in(None):
    run_agent_with_tool("Agent with tool (default semconv):")

# Opt in to latest experimental GenAI semconv emission (v1.37.0+)
with semconv_opt_in("gen_ai_latest_experimental"):
    run_agent_with_tool("Agent with tool (latest semconv opt-in):")


# --- Pattern 2: Multi-agent orchestration ---

@tool
def research_agent(query: str) -> str:
    """Route factual questions to a research specialist."""
    specialist = Agent(model=get_model(), system_prompt="You are a research specialist.")
    return str(specialist(query))


@tool
def math_agent(problem: str) -> str:
    """Route math problems to a math specialist."""
    specialist = Agent(
        model=get_model(),
        system_prompt="You are a math specialist. Solve step-by-step.",
    )
    return str(specialist(problem))


orchestrator = Agent(
    model=get_model(),
    tools=[research_agent, math_agent],
    system_prompt=(
        "Route queries to the correct specialist:\n"
        "- Factual questions -> research_agent\n"
        "- Math problems -> math_agent"
    ),
)
print("Multi-agent orchestrator:", orchestrator("What is the square root of 144?"))

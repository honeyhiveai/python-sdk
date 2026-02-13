"""
LangChain + HoneyHive integration example.

Patterns:
  1) Single agent with tools
  2) Multi-agent with subagents (agent-as-tool)

Requirements:
    pip install honeyhive langchain langchain-openai openinference-instrumentation-langchain

Environment variables:
    HH_API_KEY, HH_PROJECT, OPENAI_API_KEY
"""

import os
from honeyhive import HoneyHiveTracer
from langchain.agents import create_agent
from langchain.tools import tool
from openinference.instrumentation.langchain import LangChainInstrumentor

# --- HoneyHive setup (add these 3 lines to any LangChain app) ---

tracer = HoneyHiveTracer.init(
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    session_name="langchain-example",
)
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

# --- Tools ---

@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    return str(eval(expression, {"__builtins__": {}}, {}))

@tool
def policy_lookup(topic: str) -> str:
    """Look up company policy on a topic."""
    policies = {
        "soc2": "SOC 2 covers security, availability, processing integrity, confidentiality, and privacy.",
        "retention": "Default retention is 30 days unless compliance requires longer.",
    }
    return policies.get(topic.lower(), "No policy found.")

# --- Pattern 1: Single agent with tools ---

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[calculator, policy_lookup],
    system_prompt="You are a support assistant. Use tools when needed.",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is 17 * 3 + 5? Also summarize our SOC2 policy."}]}
)
print(result["messages"][-1].content)

# --- Pattern 2: Multi-agent with subagents ---

math_agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[calculator],
    system_prompt="You are a math specialist. Use calculator for all arithmetic.",
)

policy_agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[policy_lookup],
    system_prompt="You are a compliance specialist. Use policy_lookup for questions.",
)

@tool("math_expert", description="Solve math and arithmetic problems")
def call_math_agent(query: str) -> str:
    result = math_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

@tool("policy_expert", description="Answer questions about company policies")
def call_policy_agent(query: str) -> str:
    result = policy_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

supervisor = create_agent(
    model="openai:gpt-4o-mini",
    tools=[call_math_agent, call_policy_agent],
    system_prompt="You coordinate specialist agents. Delegate tasks to the right expert.",
)

result = supervisor.invoke(
    {"messages": [{"role": "user", "content": "What is 24 * 7? And what's our retention policy?"}]}
)
print(result["messages"][-1].content)

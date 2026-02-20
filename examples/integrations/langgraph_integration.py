"""
LangGraph + HoneyHive integration example.

Patterns:
  1) Agent with tool calling loop (canonical LangGraph pattern)
  2) Routing workflow with structured output + conditional edges

Requirements:
    pip install honeyhive langgraph langchain-openai openinference-instrumentation-langchain

Environment variables:
    HH_API_KEY, HH_PROJECT, OPENAI_API_KEY
"""

import operator
import os
from typing import Annotated, Literal, TypedDict

from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from openinference.instrumentation.langchain import LangChainInstrumentor
from pydantic import BaseModel, Field

from honeyhive import HoneyHiveTracer

# --- HoneyHive setup (add these 3 lines to any LangGraph app) ---

tracer = HoneyHiveTracer.init(
    api_key=os.environ["HH_API_KEY"],
    project=os.environ["HH_PROJECT"],
    session_name="langgraph-example",
)
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

# --- Tools ---

model = ChatOpenAI(model="gpt-4o-mini")


@tool
def calculator(a: float, b: float, operation: str) -> str:
    """Perform arithmetic on two numbers.

    Args:
        a: First number
        b: Second number
        operation: One of 'add', 'subtract', 'multiply', 'divide'
    """
    ops = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y else "err",
    }
    fn = ops.get(operation)
    return str(fn(a, b)) if fn else f"Unknown operation: {operation}"


@tool
def knowledge_base(topic: str) -> str:
    """Look up information on a topic.

    Args:
        topic: The topic to look up
    """
    topics = {
        "renewable energy": "Solar and wind generate 30% of global electricity. Costs dropped 90% since 2010.",
        "machine learning": "ML models learn patterns from data. Key types: supervised, unsupervised, reinforcement.",
    }
    for k, v in topics.items():
        if k in topic.lower():
            return v
    return f"No match for '{topic}'."


# --- Pattern 1: Agent with tool calling loop ---
# The LLM decides which tools to call via bind_tools.
# A loop runs until no more tool calls remain.

tools = [calculator, knowledge_base]
tools_by_name = {t.name: t for t in tools}
model_with_tools = model.bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


def llm_call(state: AgentState):
    """LLM decides whether to call a tool or respond."""
    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant. Use tools when needed."
                    )
                ]
                + state["messages"]
            )
        ]
    }


def tool_node(state: AgentState):
    """Execute tool calls from the LLM response."""
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
    .add_node("llm_call", llm_call)
    .add_node("tool_node", tool_node)
    .add_edge(START, "llm_call")
    .add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    .add_edge("tool_node", "llm_call")
    .compile()
)

result = agent.invoke({"messages": [HumanMessage(content="What is 256 divided by 8?")]})
print(result["messages"][-1].content)

result = agent.invoke({"messages": [HumanMessage(content="Look up renewable energy")]})
print(result["messages"][-1].content)


# --- Pattern 2: Routing workflow with structured output ---
# Classify the question, then route to a specialized handler node.


class Route(BaseModel):
    category: Literal["math", "knowledge", "general"] = Field(
        description="The category of the question"
    )


class RouterState(TypedDict):
    question: str
    category: str
    answer: str


router_llm = model.with_structured_output(Route)


def classify(state: RouterState):
    result = router_llm.invoke(
        [
            SystemMessage(content="Classify as 'math', 'knowledge', or 'general'."),
            HumanMessage(content=state["question"]),
        ]
    )
    return {"category": result.category}


def handle_math(state: RouterState):
    response = model.invoke(f"Solve this math problem: {state['question']}")
    return {"answer": response.content}


def handle_knowledge(state: RouterState):
    # Use tool directly for lookup, then summarize
    result = knowledge_base.invoke(state["question"])
    response = model.invoke(
        f"Question: {state['question']}\nFacts: {result}\nBrief answer."
    )
    return {"answer": response.content}


def handle_general(state: RouterState):
    response = model.invoke(f"Answer concisely: {state['question']}")
    return {"answer": response.content}


router = (
    StateGraph(RouterState)
    .add_node("classify", classify)
    .add_node("math", handle_math)
    .add_node("knowledge", handle_knowledge)
    .add_node("general", handle_general)
    .add_edge(START, "classify")
    .add_conditional_edges(
        "classify",
        lambda state: state["category"],
        {"math": "math", "knowledge": "knowledge", "general": "general"},
    )
    .add_edge("math", END)
    .add_edge("knowledge", END)
    .add_edge("general", END)
    .compile()
)

result = router.invoke(
    {"question": "What is 42 times 15?", "category": "", "answer": ""}
)
print(f"Route: {result['category']} | {result['answer']}")

result = router.invoke(
    {"question": "Tell me about machine learning", "category": "", "answer": ""}
)
print(f"Route: {result['category']} | {result['answer']}")

#!/usr/bin/env python3
"""
LangGraph Integration Example with HoneyHive

This example demonstrates how to integrate LangGraph with HoneyHive using the
OpenInference LangChain instrumentor for comprehensive graph observability and tracing.

Requirements:
    pip install honeyhive langgraph langchain-openai openinference-instrumentation-langchain

Environment Variables:
    HH_API_KEY: Your HoneyHive API key
    HH_PROJECT: Your HoneyHive project name
    OPENAI_API_KEY: Your OpenAI API key
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, TypedDict


async def main():
    """Main example demonstrating LangGraph integration with HoneyHive."""

    # Check required environment variables
    hh_api_key = os.getenv("HH_API_KEY")
    hh_project = os.getenv("HH_PROJECT")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not all([hh_api_key, hh_project, openai_api_key]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY: Your HoneyHive API key")
        print("   - HH_PROJECT: Your HoneyHive project name")
        print("   - OPENAI_API_KEY: Your OpenAI API key")
        print("\nSet these environment variables and try again.")
        return False

    try:
        # Import required packages
        from langchain_openai import ChatOpenAI
        from langgraph.graph import END, START, StateGraph
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from honeyhive import HoneyHiveTracer
        from honeyhive.tracer.instrumentation.decorators import trace

        print("🚀 LangGraph + HoneyHive Integration Example")
        print("=" * 50)

        # 1. Initialize the LangChain instrumentor
        print("🔧 Setting up LangChain instrumentor...")
        langchain_instrumentor = LangChainInstrumentor()
        print("✓ LangChain instrumentor initialized")

        # 2. Initialize HoneyHive tracer
        print("🔧 Setting up HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=hh_api_key,
            project=hh_project,
            session_name=Path(__file__).stem,  # Use filename as session name
            source="langgraph_example"
        )
        print("✓ HoneyHive tracer initialized")

        # Instrument LangChain with tracer provider
        langchain_instrumentor.instrument(tracer_provider=tracer.provider)
        print("✓ HoneyHive tracer initialized with LangChain instrumentor")

        # 3. Initialize LangChain model
        print("✓ OpenAI API key configured from environment")
        model = ChatOpenAI(model="gpt-4o-mini")

        # 4. Test basic graph workflow
        print("\n📊 Testing basic graph workflow...")
        result1 = await test_basic_graph(tracer, model)
        print(f"✓ Basic graph completed: {result1[:100]}...")

        # 5. Test conditional graph workflow
        print("\n🔀 Testing conditional graph workflow...")
        result2 = await test_conditional_graph(tracer, model)
        print(f"✓ Conditional graph completed: {result2[:100]}...")

        # 6. Test multi-step agent graph
        print("\n🤖 Testing multi-step agent graph...")
        result3 = await test_agent_graph(tracer, model)
        print(f"✓ Agent graph completed: {result3[:100]}...")

        # 7. Clean up instrumentor
        print("\n🧹 Cleaning up...")
        langchain_instrumentor.uninstrument()
        print("✓ Instrumentor cleaned up")

        print("\n🎉 LangGraph integration example completed successfully!")
        print(f"📊 Check your HoneyHive project '{hh_project}' for trace data")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install honeyhive langgraph langchain-openai openinference-instrumentation-langchain")
        return False

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_basic_graph(tracer: "HoneyHiveTracer", model: "ChatOpenAI") -> str:
    """Test basic LangGraph workflow with sequential nodes."""

    from langchain_openai import ChatOpenAI
    from langgraph.graph import END, START, StateGraph
    from honeyhive.tracer.instrumentation.decorators import trace

    # Define state schema
    class GraphState(TypedDict):
        message: str
        response: str

    # Define node functions with @trace decorator
    @trace(event_type="tool", event_name="say_hello_node", tracer=tracer)
    def say_hello(state: GraphState) -> GraphState:
        """First node: generates a greeting."""
        response = model.invoke("Say hello in a friendly way")
        return {"message": "hello", "response": response.content}

    @trace(event_type="tool", event_name="say_goodbye_node", tracer=tracer)
    def say_goodbye(state: GraphState) -> GraphState:
        """Second node: generates a farewell."""
        print(f"Previous response: {state.get('response', 'N/A')}")
        response = model.invoke("Say goodbye in a friendly way")
        return {"message": "goodbye", "response": response.content}

    # Create the state graph
    workflow = (
        StateGraph(GraphState)
        .add_node("sayHello", say_hello)
        .add_node("sayGoodbye", say_goodbye)
        .add_edge(START, "sayHello")
        .add_edge("sayHello", "sayGoodbye")
        .add_edge("sayGoodbye", END)
    )

    graph = workflow.compile()

    # Execute the graph - all operations will be logged to HoneyHive
    result = await graph.ainvoke({"message": "", "response": ""})
    
    return result.get("response", "No response")


async def test_conditional_graph(tracer: "HoneyHiveTracer", model: "ChatOpenAI") -> str:
    """Test LangGraph with conditional routing based on state."""

    from langchain_openai import ChatOpenAI
    from langgraph.graph import END, START, StateGraph
    from honeyhive.tracer.instrumentation.decorators import trace

    # Define state schema
    class ConditionalState(TypedDict):
        question: str
        category: str
        response: str

    # Node 1: Classify the question
    @trace(event_type="tool", event_name="classify_question_node", tracer=tracer)
    def classify_question(state: ConditionalState) -> ConditionalState:
        """Classify the type of question."""
        question = state["question"]
        response = model.invoke(
            f"Classify this question as either 'technical' or 'general': {question}\n"
            "Respond with only one word: technical or general"
        )
        category = response.content.strip().lower()
        return {"question": question, "category": category, "response": ""}

    # Node 2: Handle technical questions
    @trace(event_type="tool", event_name="handle_technical_node", tracer=tracer)
    def handle_technical(state: ConditionalState) -> ConditionalState:
        """Handle technical questions with detailed response."""
        question = state["question"]
        response = model.invoke(
            f"Provide a technical, detailed answer to: {question}"
        )
        return {"question": question, "category": state["category"], "response": response.content}

    # Node 3: Handle general questions
    @trace(event_type="tool", event_name="handle_general_node", tracer=tracer)
    def handle_general(state: ConditionalState) -> ConditionalState:
        """Handle general questions with simple response."""
        question = state["question"]
        response = model.invoke(
            f"Provide a brief, friendly answer to: {question}"
        )
        return {"question": question, "category": state["category"], "response": response.content}

    # Routing function
    def route_question(state: ConditionalState) -> str:
        """Route to appropriate handler based on category."""
        category = state["category"]
        if "technical" in category:
            return "handleTechnical"
        else:
            return "handleGeneral"

    # Create the conditional graph
    workflow = (
        StateGraph(ConditionalState)
        .add_node("classify", classify_question)
        .add_node("handleTechnical", handle_technical)
        .add_node("handleGeneral", handle_general)
        .add_edge(START, "classify")
        .add_conditional_edges("classify", route_question)
        .add_edge("handleTechnical", END)
        .add_edge("handleGeneral", END)
    )

    graph = workflow.compile()

    # Test with a technical question
    result = await graph.ainvoke({
        "question": "How does machine learning work?",
        "category": "",
        "response": ""
    })
    
    return result.get("response", "No response")


async def test_agent_graph(tracer: "HoneyHiveTracer", model: "ChatOpenAI") -> str:
    """Test multi-step agent graph with tools and decision making."""

    from langchain_openai import ChatOpenAI
    from langgraph.graph import END, START, StateGraph
    from honeyhive.tracer.instrumentation.decorators import trace

    # Define state schema
    class AgentState(TypedDict):
        input: str
        plan: str
        research: str
        answer: str
        iterations: int

    # Node 1: Create a plan
    @trace(event_type="tool", event_name="create_plan_node", tracer=tracer)
    def create_plan(state: AgentState) -> AgentState:
        """Create a plan for answering the question."""
        user_input = state["input"]
        response = model.invoke(
            f"Create a brief plan (2-3 steps) for answering this question: {user_input}"
        )
        return {
            "input": user_input,
            "plan": response.content,
            "research": "",
            "answer": "",
            "iterations": state.get("iterations", 0)
        }

    # Node 2: Gather information
    @trace(event_type="tool", event_name="research_node", tracer=tracer)
    def research(state: AgentState) -> AgentState:
        """Gather information based on the plan."""
        plan = state["plan"]
        response = model.invoke(
            f"Based on this plan: {plan}\n\n"
            "Provide key information and facts that would help answer the question. "
            "Keep it concise (3-4 sentences)."
        )
        return {
            "input": state["input"],
            "plan": plan,
            "research": response.content,
            "answer": "",
            "iterations": state.get("iterations", 0) + 1
        }

    # Node 3: Synthesize answer
    @trace(event_type="tool", event_name="synthesize_answer_node", tracer=tracer)
    def synthesize_answer(state: AgentState) -> AgentState:
        """Synthesize final answer from research."""
        user_input = state["input"]
        research = state["research"]
        response = model.invoke(
            f"Question: {user_input}\n\n"
            f"Research: {research}\n\n"
            "Provide a clear, concise answer to the question based on the research."
        )
        return {
            "input": user_input,
            "plan": state["plan"],
            "research": research,
            "answer": response.content,
            "iterations": state.get("iterations", 0)
        }

    # Node 4: Evaluate if answer is sufficient
    @trace(event_type="tool", event_name="evaluate_answer_node", tracer=tracer)
    def evaluate_answer(state: AgentState) -> AgentState:
        """Evaluate if the answer is sufficient."""
        # For this example, we'll just mark it as complete
        # In a real scenario, you might use the LLM to evaluate
        return state

    # Routing function
    def should_continue(state: AgentState) -> str:
        """Decide whether to continue or end."""
        iterations = state.get("iterations", 0)
        # Limit to 1 iteration for this example
        if iterations >= 1:
            return "synthesize"
        else:
            return "research"

    # Create the agent graph
    workflow = (
        StateGraph(AgentState)
        .add_node("plan", create_plan)
        .add_node("research", research)
        .add_node("synthesize", synthesize_answer)
        .add_node("evaluate", evaluate_answer)
        .add_edge(START, "plan")
        .add_edge("plan", "research")
        .add_edge("research", "synthesize")
        .add_edge("synthesize", "evaluate")
        .add_edge("evaluate", END)
    )

    graph = workflow.compile()

    # Execute the agent graph
    result = await graph.ainvoke({
        "input": "What are the benefits of renewable energy?",
        "plan": "",
        "research": "",
        "answer": "",
        "iterations": 0
    })
    
    return result.get("answer", "No answer generated")


if __name__ == "__main__":
    """Run the LangGraph integration example."""
    success = asyncio.run(main())

    if success:
        print("\n✅ Example completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Example failed!")
        sys.exit(1)


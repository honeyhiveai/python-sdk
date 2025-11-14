"""
Stage 2: Test @atrace with actual LangGraph workflow execution
This tests if the error occurs during LangGraph's state management
"""
import asyncio
from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from honeyhive import atrace, trace, HoneyHiveTracer

# Simulate LangGraph state (like customer's AgentState)
class AgentState(TypedDict):
    """Custom state that extends MessagesState with additional fields."""
    messages: list
    query_count: int
    requires_approval: bool
    current_step: str


# Test nodes with @atrace (like customer's code)
@atrace
async def analyze_query_node(state: AgentState) -> AgentState:
    """Node 1: Analyze the user's query."""
    print(f"  → analyze_query_node called with state: {state.get('current_step')}")
    
    # Check if requires approval
    requires_approval = state.get("query_count", 0) > 5
    
    return {
        "current_step": "execute",
        "requires_approval": requires_approval,
        "query_count": state.get("query_count", 0)
    }


@atrace
async def execution_node(state: AgentState) -> AgentState:
    """Node 2: Execute the query."""
    print(f"  → execution_node called with state: {state.get('current_step')}")
    
    return {
        "messages": state.get("messages", []) + ["Result: Success"],
        "query_count": state.get("query_count", 0) + 1,
        "current_step": "complete"
    }


# Conditional routing (sync function with @atrace - known issue)
@atrace
def should_approve_atrace(state: AgentState) -> Literal["approve", "execute"]:
    """Conditional routing with @atrace (customer's issue)."""
    print(f"  → should_approve_atrace called with state: {state.get('current_step')}")
    if state.get("requires_approval", False):
        return "approve"
    return "execute"


# Conditional routing (sync function with @trace - correct usage)
@trace
def should_approve_trace(state: AgentState) -> Literal["approve", "execute"]:
    """Conditional routing with @trace (correct usage)."""
    print(f"  → should_approve_trace called with state: {state.get('current_step')}")
    if state.get("requires_approval", False):
        return "approve"
    return "execute"


async def approval_node(state: AgentState) -> AgentState:
    """Node 3: Approval required."""
    print(f"  → approval_node called with state: {state.get('current_step')}")
    return {
        "messages": state.get("messages", []) + ["Approval required"],
        "current_step": "complete"
    }


async def test_with_atrace_routing():
    """Test LangGraph with @atrace on sync routing function."""
    print("\n" + "="*80)
    print("TEST 1: LangGraph with @atrace on sync routing function")
    print("="*80)
    
    try:
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", analyze_query_node)
        workflow.add_node("execute", execution_node)
        workflow.add_node("approve", approval_node)
        
        # Add edges
        workflow.add_edge(START, "analyze")
        
        # Add conditional edge with @atrace on sync function
        workflow.add_conditional_edges(
            "analyze",
            should_approve_atrace,  # ← This is the problem: @atrace on sync
            {
                "execute": "execute",
                "approve": "approve"
            }
        )
        
        workflow.add_edge("execute", END)
        workflow.add_edge("approve", END)
        
        # Compile
        graph = workflow.compile()
        
        # Run
        initial_state = {
            "messages": ["Test query"],
            "query_count": 0,
            "requires_approval": False,
            "current_step": "analyze"
        }
        
        result = await graph.ainvoke(initial_state)
        print(f"✅ SUCCESS: {result}")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def test_with_trace_routing():
    """Test LangGraph with @trace on sync routing function (correct)."""
    print("\n" + "="*80)
    print("TEST 2: LangGraph with @trace on sync routing function (CORRECT)")
    print("="*80)
    
    try:
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", analyze_query_node)
        workflow.add_node("execute", execution_node)
        workflow.add_node("approve", approval_node)
        
        # Add edges
        workflow.add_edge(START, "analyze")
        
        # Add conditional edge with @trace on sync function
        workflow.add_conditional_edges(
            "analyze",
            should_approve_trace,  # ← Correct: @trace auto-detects sync
            {
                "execute": "execute",
                "approve": "approve"
            }
        )
        
        workflow.add_edge("execute", END)
        workflow.add_edge("approve", END)
        
        # Compile
        graph = workflow.compile()
        
        # Run
        initial_state = {
            "messages": ["Test query"],
            "query_count": 0,
            "requires_approval": False,
            "current_step": "analyze"
        }
        
        result = await graph.ainvoke(initial_state)
        print(f"✅ SUCCESS: {result}")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def test_with_tracer():
    """Test with actual HoneyHive tracer initialized."""
    print("\n" + "="*80)
    print("TEST 3: LangGraph with @atrace and HoneyHive tracer initialized")
    print("="*80)
    
    try:
        # Initialize tracer (will use test mode if no API key)
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="langgraph-test",
            source="test",
            test_mode=True
        )
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes  
        workflow.add_node("analyze", analyze_query_node)
        workflow.add_node("execute", execution_node)
        workflow.add_node("approve", approval_node)
        
        # Add edges
        workflow.add_edge(START, "analyze")
        workflow.add_conditional_edges(
            "analyze",
            should_approve_trace,  # Use correct @trace
            {
                "execute": "execute",
                "approve": "approve"
            }
        )
        workflow.add_edge("execute", END)
        workflow.add_edge("approve", END)
        
        # Compile
        graph = workflow.compile()
        
        # Run
        initial_state = {
            "messages": ["Test query"],
            "query_count": 0,
            "requires_approval": False,
            "current_step": "analyze"
        }
        
        result = await graph.ainvoke(initial_state)
        print(f"✅ SUCCESS: {result}")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all Stage 2 tests."""
    print("="*80)
    print("Stage 2: LangGraph Workflow Execution Tests")
    print("="*80)
    
    # Test 1: @atrace on sync routing (customer's usage)
    await test_with_atrace_routing()
    
    # Test 2: @trace on sync routing (correct usage)
    await test_with_trace_routing()
    
    # Test 3: With HoneyHive tracer initialized
    await test_with_tracer()


if __name__ == "__main__":
    asyncio.run(main())


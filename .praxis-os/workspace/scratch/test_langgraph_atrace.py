"""
Minimal reproduction test for @atrace with LangGraph
Testing to understand the exact error
"""
import asyncio
from typing import Literal, TypedDict
from honeyhive import atrace

# Simulate LangGraph state
class AgentState(TypedDict):
    """Simulated LangGraph state"""
    messages: list
    query_count: int
    requires_approval: bool
    current_step: str


# Test 1: Basic @atrace on async function
@atrace
async def simple_async_node(state: AgentState) -> AgentState:
    """Simple async node without any complexity"""
    return {
        "messages": state.get("messages", []),
        "query_count": state.get("query_count", 0) + 1,
        "requires_approval": False,
        "current_step": "complete"
    }


# Test 2: @atrace on sync function (known issue)
@atrace
def simple_sync_node(state: AgentState) -> Literal["approve", "execute"]:
    """Sync function decorated with @atrace"""
    if state.get("requires_approval", False):
        return "approve"
    return "execute"


# Test 3: @atrace with explicit parameters
@atrace(event_type="tool", event_name="explicit_node")
async def explicit_async_node(state: AgentState) -> AgentState:
    """Async node with explicit atrace parameters"""
    return {
        "messages": state.get("messages", []),
        "query_count": state.get("query_count", 0) + 1,
        "requires_approval": False,
        "current_step": "complete"
    }


async def test_scenarios():
    """Run test scenarios"""
    
    # Test state
    test_state = {
        "messages": ["test message"],
        "query_count": 0,
        "requires_approval": False,
        "current_step": "analyze"
    }
    
    print("="*80)
    print("Testing @atrace with LangGraph-style state objects")
    print("="*80)
    
    # Test 1
    print("\n[Test 1] Simple async node with @atrace")
    try:
        result = await simple_async_node(test_state)
        print(f"✅ SUCCESS: {result}")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
    
    # Test 2
    print("\n[Test 2] Sync function with @atrace (should fail or warn)")
    try:
        result = simple_sync_node(test_state)
        print(f"✅ SUCCESS: {result}")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
    
    # Test 3
    print("\n[Test 3] Async node with explicit @atrace parameters")
    try:
        result = await explicit_async_node(test_state)
        print(f"✅ SUCCESS: {result}")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_scenarios())


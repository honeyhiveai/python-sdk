# Reproduction Plan: @atrace with LangGraph Error

## What We CAN Reproduce (95%)

### ✅ Core Components We Have
1. **HoneyHive SDK** - We have the source code
2. **LangGraph** - Public library, can install
3. **LangChain** - Public library, can install
4. **Chinook Database** - Public sample SQLite database
5. **Customer's Code** - They provided the full script

### ✅ What We Can Test WITHOUT Any External Credentials

**Minimal Reproduction (No External Services)**:
```python
# Test JUST the decorator with LangGraph state objects
from typing import TypedDict, Literal
from honeyhive import atrace

class AgentState(TypedDict):
    messages: list
    query_count: int
    requires_approval: bool
    current_step: str

@atrace
async def test_node(state: AgentState) -> AgentState:
    return {"messages": [], "query_count": 0}

@atrace
def test_sync(state: AgentState) -> Literal["a", "b"]:
    return "a"

# Run this and see if we get the error
```

This requires **ZERO credentials** and will tell us if:
- The error is in our decorator validation
- The error is specific to LangGraph's TypedDict
- The error occurs at decoration time or execution time

### ⚠️ What Requires Credentials (But Optional)

**Full LangGraph + OpenAI Test**:
- **OpenAI API Key** - Only needed if we want to actually invoke the LLM
- **Alternative**: We can mock the OpenAI calls or use a fake LLM

**Database**:
- **Chinook.db** - Publicly available, no credentials needed
- Download from: https://github.com/lerocha/chinook-database/

## Reproduction Strategy (Staged Approach)

### Stage 1: Isolated Decorator Test (0 credentials)
**Goal**: Reproduce the Pydantic validation error in isolation

```bash
# No external dependencies needed
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
source venv/bin/activate

# Run our minimal test
python .praxis-os/workspace/scratch/test_langgraph_atrace.py
```

**Expected**: This should either:
- ✅ Work fine → Error is elsewhere
- ❌ Show the error → We found the root cause

### Stage 2: LangGraph Integration (0 credentials)
**Goal**: Test with actual LangGraph state management

**Dependencies to install**:
```bash
pip install langgraph langchain-core
```

**Test**: Create a minimal LangGraph workflow with our decorator
- No OpenAI needed
- No database needed
- Just test state passing through nodes

### Stage 3: Full Stack (Optional, requires OpenAI key)
**Goal**: Exact reproduction of customer's scenario

**Dependencies**:
```bash
pip install \
  langgraph \
  langchain \
  langchain-core \
  langchain-community \
  langchain-openai
```

**Credentials Needed**:
- OpenAI API key (set as `OPENAI_API_KEY` env var)
- OR: Mock it with `langchain-fake-llm` (no credentials)

**Database**:
```bash
# Download Chinook database (public, no credentials)
wget https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite
mv Chinook_Sqlite.sqlite Chinook.db
```

## Recommended Approach: Start with Stage 1

### Why Start Minimal?
1. **Fastest to debug** - No external dependencies
2. **Isolates the issue** - Is it our code or LangGraph?
3. **No credentials needed** - Can start immediately
4. **Clear signal** - Either validates or fails

### Test Script (Already Created)
Location: `.praxis-os/workspace/scratch/test_langgraph_atrace.py`

This tests:
- ✅ @atrace on async function with TypedDict state
- ✅ @atrace on sync function (known issue)
- ✅ @atrace with explicit parameters

## Expected Outcomes

### If Stage 1 Passes
→ Error is in LangGraph's internal state management
→ Move to Stage 2

### If Stage 1 Fails
→ Error is in our decorator/validation
→ We can fix it immediately
→ No credentials needed

### If Stage 2 Fails (but Stage 1 passes)
→ Error is in LangGraph integration
→ May need to inspect LangGraph's state internals
→ Still no credentials needed

### If All Pass
→ Error requires the full stack (OpenAI + database)
→ Then we need OpenAI key
→ Or we ask customer for full stack trace

## Credentials Summary

| Stage | Credentials Needed | Can Proceed Without? |
|-------|-------------------|---------------------|
| **Stage 1** | None | ✅ Yes (recommended start) |
| **Stage 2** | None | ✅ Yes |
| **Stage 3** | OpenAI API key | ⚠️ Can mock with fake LLM |
| **Database** | None (public) | ✅ Yes |

## Action Plan

1. **Immediate** (0 minutes setup):
   ```bash
   cd /Users/josh/src/github.com/honeyhiveai/python-sdk
   source venv/bin/activate
   python .praxis-os/workspace/scratch/test_langgraph_atrace.py
   ```

2. **If Stage 1 passes** (5 minutes setup):
   ```bash
   pip install langgraph langchain-core
   # Create Stage 2 test (LangGraph workflow)
   ```

3. **If Stages 1-2 pass** (10 minutes setup):
   ```bash
   # Install full stack
   # Download Chinook.db
   # Either: Set OPENAI_API_KEY or use mock LLM
   ```

4. **If all pass**:
   → Ask customer for full stack trace
   → Ask customer to try `@trace` instead of `@atrace`
   → Ask customer for LangGraph/LangChain versions

## What We Should Do First

**Recommendation**: Run Stage 1 immediately. I already created the test script.

Would you like me to:
1. Run the Stage 1 test now? (requires running Python)
2. Create the Stage 2 test (LangGraph integration)?
3. Set up the full Stage 3 environment?
4. Create a script the customer can run to give us more diagnostic info?


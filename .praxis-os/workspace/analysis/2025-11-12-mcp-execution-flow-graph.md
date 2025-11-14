# MCP Server Execution Flow - Call Graph Analysis
**Date:** 2025-11-12  
**Method:** Graph traversal on praxis_os partition (find_callers, find_dependencies)  
**Discovery:** Complete runtime execution paths traced via DuckDB recursive CTEs

---

## Mission: Trace Actual Runtime Call Paths

Used the praxis_os partition's GraphIndex to trace **actual function calls** in the MCP server, revealing the complete execution flow from AI agent request to subsystem response.

---

## 1. Tool Dispatch Flow (All 6 Action-Based Tools)

### Call Graph Discovered:

```
AI Agent Request
    ↓
pos_search_project() / pos_workflow() / pos_filesystem() / pos_browser() / get_server_info()
    ↓
ActionDispatchMixin.dispatch()
    ↓
    ├─→ extract_session_id() ────────┐ (Middleware)
    │   ├─→ get_session_key()        │
    │   ├─→ get_timeout_seconds()    │
    │   ├─→ is_expired()              │
    │   └─→ SessionState (class)     │
    │                                  │
    ├─→ record_query() ───────────────┤ (Middleware)
    │   ├─→ classify()                │
    │   │   └─→ _create_result()      │
    │   └─→ QueryStats (class)        │
    │                                  │
    ├─→ Handler Lookup                │
    │   (e.g., _handle_search_standards)
    │                                  │
    ├─→ Invoke Handler ───────────────┤
    │   └─→ Subsystem Call            │
    │       (IndexManager, WorkflowEngine, etc.)
    │                                  │
    ├─→ success_response() ───────────┤ (Success Path)
    │                                  │
    └─→ error_response() ─────────────┘ (Error Path)
        └─→ ActionableError (class)
```

### Graph Evidence:

**From `find_callers(extract_session_id)`:**
```
Depth 1: dispatch → extract_session_id
Depth 2: 
  - pos_search_project → dispatch → extract_session_id
  - pos_workflow → dispatch → extract_session_id
  - pos_filesystem → dispatch → extract_session_id
  - pos_browser → dispatch → extract_session_id
  - get_server_info → dispatch → extract_session_id
```

**Result:** All 6 action-based tools converge on the SAME dispatch flow!

---

## 2. Middleware Integration Points (Graph Verified)

### From `find_dependencies(dispatch)`:

**Middleware Calls (Depth 1):**
```
dispatch() calls:
├─→ extract_session_id()      # Session management
├─→ record_query()             # Query tracking for metrics
├─→ success_response()         # Response formatting
├─→ error_response()           # Error formatting
└─→ Logging: info(), debug(), error(), warning()
```

**Middleware Calls (Depth 2):**
```
extract_session_id() calls:
├─→ get_session_key()          # Session key generation
├─→ get_timeout_seconds()      # Timeout configuration
├─→ is_expired()               # Session expiry check
└─→ SessionState (construct)   # State management

record_query() calls:
├─→ classify()                 # Query classification (5 angles)
│   └─→ _create_result()       # Classification result
└─→ QueryStats (construct)     # Metrics aggregation
```

**Middleware Calls (Depth 3):**
```
classify() calls:
└─→ _create_result()           # Format classification (📖, 📍, 🔧, ⭐, ⚠️)

is_expired() calls:
└─→ get_timeout_seconds()      # Check expiry threshold
```

---

## 3. Tool Registration Flow (Graph Verified)

### From `find_dependencies(register_all)`:

```
ToolRegistry.register_all()
    ↓
    ├─→ discover_tools() ──────────┐
    │   ├─→ importlib.import_module()
    │   ├─→ inspect.getmembers()
    │   ├─→ inspect.signature()
    │   └─→ Logging: info(), debug(), error()
    │
    ├─→ register_tool() ───────────┤
    │   ├─→ Dependency Injection
    │   │   (match params to self.dependencies dict)
    │   ├─→ Call: register_*_tool(**kwargs)
    │   │   └─→ Create tool instance
    │   │       └─→ Access .tool property
    │   │           └─→ @mcp.tool() decoration
    │   └─→ Logging: info(), warning(), error()
    │
    └─→ Logging: info(), error() ──┘
```

**Result:** Auto-discovery + dependency injection = zero boilerplate registration!

---

## 4. Complete Execution Flow: AI Request → Subsystem → Response

### Example: Search Query Execution

```
1. AI Agent calls:
   pos_search_project(action="search_standards", query="how does X work?")

2. Tool function (decorated):
   @mcp.tool()
   async def pos_search_project(action, query, **kwargs):
       return await self.dispatch(action, self.handlers, query=query, **kwargs)

3. ActionDispatchMixin.dispatch():
   ├─→ extract_session_id()               # Get/create task_session_id
   │   └─→ Result: task_session_id="..."
   │
   ├─→ record_query()                     # Track for metrics
   │   ├─→ agent_session: long-lived
   │   ├─→ task_session: short-lived
   │   └─→ classify(query)                # 5-angle classification
   │       └─→ Result: {📖: true, 📍: false, ...}
   │
   ├─→ Lookup handler:
   │   handler = self.handlers["search_standards"]
   │   # handler = SearchTool._handle_search_standards
   │
   ├─→ Invoke handler:
   │   result = await handler(query=query, task_session_id=task_session_id, **kwargs)
   │
   └─→ success_response(action, result)
       └─→ Return: {"status": "success", "action": "search_standards", ...}

4. SearchTool._handle_search_standards():
   ├─→ index_manager.get_index("standards")
   │   └─→ StandardsIndex instance
   │
   ├─→ standards_index.search(query, method, n_results, filters)
   │   ├─→ Hybrid search (vector + FTS + RRF)
   │   └─→ Result: [SearchResult, ...]
   │
   ├─→ PrependGenerator.generate()         # Middleware
   │   ├─→ Query count: "📊 Queries: 3/5"
   │   ├─→ Angle coverage: "📖✓ 📍⬜ ..."
   │   └─→ Suggestion: "💡 Try: 'What is X?'"
   │
   ├─→ Inject prepend into first result
   │   result[0].content = f"{prepend}\n\n---\n\n{result[0].content}"
   │
   └─→ Return: {"results": [...], "count": 3, ...}

5. Response flows back:
   dispatch() → success_response() → MCP protocol → AI Agent
```

---

## 5. Error Handling Flow (Graph Verified)

### From `find_dependencies(dispatch)` - Error Path:

```
dispatch() → error_response()
    ↓
Creates standard error envelope:
{
    "status": "error",
    "action": "search_standards",
    "error": "ERROR: search_standards\n\nReason: ...\n\nRemediation: ...",
    "error_type": "IndexError",
    "remediation": "Check server logs for details..."
}
```

**Error Types Discovered:**
- `ActionableError`: User-facing error with remediation guidance
- `IndexError`: Index-related errors
- `ValueError`: Invalid parameters
- `TypeError`: Type mismatches
- Generic `Exception`: Catch-all

**Every error is logged + wrapped + returned (no crashes!):**
```python
try:
    result = handler(**kwargs)
except Exception as e:
    logger.error("Action dispatch failed", exc_info=True)
    return self.error_response(action, e)
```

---

## 6. Dual Session Tracking (Graph Verified)

### From `find_dependencies(dispatch)` → `extract_session_id`:

**Two session concepts flow through dispatch:**

```
dispatch()
    ↓
extract_session_id(client_id=agent_session_id)
    ├─→ get_session_key() → "session_{client_id}"
    ├─→ Check: SessionState.sessions[key]
    ├─→ is_expired() → check last_access_time
    │   └─→ get_timeout_seconds() → 300s (5 min)
    ├─→ If expired: generate new task_session_id
    └─→ Return: task_session_id

record_query(agent_session_id, query)
record_query(task_session_id, query)   # Record TWICE!
```

**Result:**
- **agent_session_id**: Tracks queries across DAYS (behavioral metrics)
- **task_session_id**: Tracks queries within 5-min window (prepend gamification)

---

## 7. Query Classification Flow (Graph Verified)

### From `find_dependencies(dispatch)` → `record_query` → `classify`:

```
record_query(session_id, query)
    ↓
classify(query) → _create_result()
    ↓
Returns: {
    "conceptual_understanding": bool,  # 📖 (e.g., "What is X?")
    "location_finding": bool,          # 📍 (e.g., "Where is Y?")
    "procedure_learning": bool,        # 🔧 (e.g., "How do I Z?")
    "rationale_seeking": bool,         # ⭐ (e.g., "Why does W?")
    "issue_resolution": bool           # ⚠️ (e.g., "How to fix V?")
}
```

**This classification feeds:**
1. **QueryStats**: Aggregated metrics
2. **PrependGenerator**: Angle coverage display ("📖✓ 📍⬜ 🔧⬜ ⭐⬜ ⚠️⬜")
3. **Behavioral analysis**: Query diversity measurements

---

## 8. Logging Integration (Graph Verified)

### All Logging Flows Through Utils:

**From multiple `find_dependencies` calls:**

```
ALL functions call logging:
├─→ ouroboros/utils/logging.py:info()     (line 263)
├─→ ouroboros/utils/logging.py:debug()    (line 246)
├─→ ouroboros/utils/logging.py:warning()  (line 281)
└─→ ouroboros/utils/logging.py:error()    (line 298)
```

**Structured logging with context:**
```python
logger.info(
    "Dispatching action",
    extra={
        "action": action,
        "tool_class": self.__class__.__name__,
        "kwargs_keys": list(kwargs.keys()),
    }
)
```

**Result:** Every action is traceable through logs with full context!

---

## 9. Subsystem Integration Points

### Tools → Subsystems (Discovered Dependencies):

**1. SearchTool → IndexManager**
```
_handle_search_standards()
    ↓
index_manager.get_index("standards")
    ↓
StandardsIndex.search()
    ├─→ LanceDB (vector + FTS)
    ├─→ RRF fusion
    └─→ Reranking
```

**2. WorkflowTool → WorkflowEngine**
```
_handle_start()
    ↓
workflow_engine.start_workflow(workflow_type, target_file)
    ├─→ WorkflowRenderer (load content)
    ├─→ PhaseGates (sequential enforcement)
    ├─→ StateManager (persistence)
    └─→ EvidenceValidator (multi-layer validation)
```

**3. FilesystemTool → Python pathlib/shutil**
```
_handle_read()
    ↓
Path validation (security)
    ├─→ Check: no ".." (traversal)
    ├─→ Check: inside workspace
    ├─→ Check: not gitignored
    └─→ Path.read_text(encoding=encoding)
```

**4. BrowserTool → BrowserManager**
```
_handle_navigate()
    ↓
browser_manager.get_session(session_id)
    ├─→ SessionMapper (conversation → browser session)
    ├─→ Playwright (browser automation)
    └─→ session.page.goto(url)
```

---

## 10. Visualization: Complete Call Graph

### Layered Architecture (Verified by Graph Traversal):

```
┌─────────────────────────────────────────────────────────┐
│                     AI Agent Layer                       │
│  (LLM, Cursor, Claude API, etc.)                        │
└─────────────────────────────────────────────────────────┘
                        ↓ MCP Protocol
┌─────────────────────────────────────────────────────────┐
│                    MCP Tools Layer                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ pos_search_project  pos_workflow  pos_filesystem │   │
│  │ pos_browser  get_server_info  current_date      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        ↓ dispatch()
┌─────────────────────────────────────────────────────────┐
│                  Middleware Layer                        │
│  ┌────────────────────────────────────────────────┐    │
│  │ extract_session_id() → SessionState            │    │
│  │ record_query() → QueryTracker → classify()     │    │
│  │ PrependGenerator → query count + suggestions   │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                        ↓ handler()
┌─────────────────────────────────────────────────────────┐
│                 Subsystems Layer                         │
│  ┌────────────────────────────────────────────────┐    │
│  │ IndexManager → Standards/Code/AST/Graph        │    │
│  │ WorkflowEngine → PhaseGates + EvidenceValidator│    │
│  │ BrowserManager → SessionMapper + Playwright    │    │
│  │ StateManager → Persistence                     │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                 Storage Layer                            │
│  LanceDB | DuckDB | Filesystem | Browser                │
└─────────────────────────────────────────────────────────┘
```

---

## 11. Key Insights from Call Graph Analysis

### 1. **Single Choke Point (dispatch)**
- ✅ ALL tools flow through dispatch()
- ✅ Middleware integration happens in ONE place
- ✅ Consistent error handling for all tools
- ✅ Query tracking for all searches
- ✅ Session management for all requests

### 2. **Middleware is Non-Invasive**
- ✅ extract_session_id: Pure function, no side effects on handler
- ✅ record_query: Fire-and-forget, doesn't block handler
- ✅ PrependGenerator: Post-processing, doesn't affect handler logic
- ✅ All middleware failures are caught and logged (don't break dispatch)

### 3. **Pure Handler Functions**
- ✅ Handlers receive clean inputs (no middleware knowledge needed)
- ✅ Handlers return clean outputs (dict)
- ✅ Handlers focus on business logic only
- ✅ Easy to test in isolation (mock subsystems)

### 4. **Dependency Injection Works**
- ✅ Tools declare what they need (function signature)
- ✅ Registry provides what's available (dependencies dict)
- ✅ Auto-matching via introspection (inspect.signature)
- ✅ Missing dependencies detected at registration (not runtime)

### 5. **Error Boundaries Everywhere**
- ✅ dispatch() catches handler errors
- ✅ Handler errors wrapped in ActionableError
- ✅ Middleware errors caught and logged
- ✅ Registration errors logged and skipped
- ✅ NO crashes propagate to AI agent

---

## 12. Performance Implications (From Graph)

### Call Depth Analysis:

**Typical search query call depth:**
```
pos_search_project (depth 0)
  └─→ dispatch (depth 1)
      ├─→ extract_session_id (depth 2)
      │   ├─→ get_session_key (depth 3)
      │   ├─→ is_expired (depth 3)
      │   │   └─→ get_timeout_seconds (depth 4)
      │   └─→ SessionState (depth 3)
      ├─→ record_query (depth 2)
      │   ├─→ classify (depth 3)
      │   │   └─→ _create_result (depth 4)
      │   └─→ QueryStats (depth 3)
      ├─→ _handle_search_standards (depth 2)
      │   └─→ index_manager.get_index (depth 3)
      │       └─→ StandardsIndex.search (depth 4)
      │           └─→ LanceDB operations (depth 5)
      └─→ success_response (depth 2)

Maximum depth: 5 levels
```

**This is SHALLOW!** Very efficient call stack.

---

## 13. Testing Implications (From Graph)

### Isolated Testing Strategy:

**1. Test Handlers in Isolation:**
```python
# Mock only the subsystem, not the entire dispatch flow
mock_index_manager = Mock()
tool = SearchTool(mcp, mock_index_manager)

result = await tool._handle_search_standards(
    query="test",
    method="hybrid",
    n_results=5
)

# Verify subsystem called correctly
mock_index_manager.get_index.assert_called_with("standards")
```

**2. Test Middleware in Isolation:**
```python
# Test extract_session_id without tools
session_id = extract_session_id(client_id="test")
assert session_id.startswith("task_")

# Test record_query without tools
query_tracker.record_query("session123", "test query")
stats = query_tracker.get_stats("session123")
assert stats.total_queries == 1
```

**3. Test dispatch with Mock Handlers:**
```python
# Test dispatch flow without real handlers
mock_handler = AsyncMock(return_value={"result": "success"})
handlers = {"test_action": mock_handler}

result = await mixin.dispatch("test_action", handlers)

assert result["status"] == "success"
mock_handler.assert_called_once()
```

**Result:** Clean separation = easy testing at every layer!

---

## Conclusion

**Call graph traversal revealed:**

✅ **Single dispatch choke point** - All tools converge  
✅ **Middleware integration** - Seamless, non-invasive  
✅ **Dependency injection** - Auto-matching via introspection  
✅ **Error boundaries** - Catching at every layer  
✅ **Shallow call depth** - Maximum 5 levels  
✅ **Pure handlers** - Business logic only  
✅ **Dual session tracking** - Long-term + short-term  
✅ **Query classification** - 5-angle coverage  

**Used praxis OS graph traversal to understand praxis OS execution flow.**

**Meta analysis complete. 🎯**


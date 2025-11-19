# MCP Tools Architecture Patterns
**Date:** 2025-11-12  
**Method:** Call graph traversal + code reading of praxis_os partition  
**Discovery:** Unified action-dispatch pattern across all MCP tools

---

## Mission: Understand MCP Tool Implementation Patterns

Used the newly indexed `praxis_os` partition to analyze how MCP tools are architected. Discovered a **beautiful, consistent pattern** across all 7 tools with automatic discovery, dependency injection, and action-based dispatch.

---

## 1. The Core Pattern: ActionDispatchMixin

### Location: `ouroboros/tools/base.py`

**The Foundation:**
```python
class ActionDispatchMixin:
    """
    Mixin providing common action-based dispatch behavior for MCP tools.
    
    Provides:
    - Action validation against allowed set
    - Handler lookup and invocation
    - Error handling with standard envelopes
    - Success/error response formatting
    - Logging integration
    - Query tracking integration
    """
    
    def __init__(self, mcp: FastMCP, query_tracker: Optional[Any] = None):
        self.mcp = mcp
        self.query_tracker = query_tracker
```

**The Dispatch Magic:**
```python
async def dispatch(
    self,
    action: str,
    handlers: Dict[str, Callable],
    query: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Dispatch action to appropriate handler with error wrapping.
    
    Flow:
    1. Extract session IDs (agent_session + task_session)
    2. Record query in QueryTracker (behavioral metrics)
    3. Validate handler exists
    4. Invoke handler (async-aware)
    5. Wrap result in success envelope
    6. On error: catch, log, return error envelope
    """
```

**Key Features:**
- ✅ **Dual Session Tracking**: agent_session (long-lived) + task_session (per-request)
- ✅ **QueryTracker Integration**: Behavioral metrics for all searches
- ✅ **Standard Response Envelopes**: Success vs error formatting
- ✅ **Error Wrapping**: Catches all exceptions, returns structured errors
- ✅ **Logging**: Structured logging with context
- ✅ **Async-aware**: Detects and awaits coroutines

---

## 2. Tool Implementation Pattern

### Every Tool Follows This Structure:

**Step 1: Inherit from ActionDispatchMixin**
```python
class SearchTool(ActionDispatchMixin):
    def __init__(self, mcp, index_manager, query_tracker=None):
        super().__init__(mcp, query_tracker)
        self.index_manager = index_manager  # Tool-specific dependency
```

**Step 2: Define Handler Mapping**
```python
        # Map actions to handler methods
        self.handlers = {
            "search_standards": self._handle_search_standards,
            "search_code": self._handle_search_code,
            "search_ast": self._handle_search_ast,
            "find_callers": self._handle_find_callers,
            "find_dependencies": self._handle_find_dependencies,
            "find_call_paths": self._handle_find_call_paths,
        }
```

**Step 3: Expose via @property + @mcp.tool()**
```python
    @property
    def tool(self):
        @self.mcp.tool()
        async def pos_search_project(
            action: Literal[
                "search_standards",
                "search_code",
                "search_ast",
                "find_callers",
                "find_dependencies",
                "find_call_paths"
            ],
            query: str,
            **kwargs
        ) -> Dict[str, Any]:
            """Docstring becomes MCP tool description"""
            return await self.dispatch(action, self.handlers, query=query, **kwargs)
        
        return pos_search_project
```

**Step 4: Implement Pure Business Logic Handlers**
```python
    async def _handle_search_standards(
        self,
        query: str,
        method: str = "hybrid",
        n_results: int = 5,
        filters: Optional[Dict] = None,
        task_session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Pure business logic - no boilerplate!
        
        Just:
        1. Call subsystem (IndexManager)
        2. Format results
        3. Return dict
        
        ActionDispatchMixin handles:
        - Error catching
        - Response wrapping
        - Logging
        - Query tracking
        """
        # Get standards index
        standards_index = self.index_manager.get_index("standards")
        
        # Search
        results = standards_index.search(
            query=query,
            method=method,
            n_results=n_results,
            filters=filters
        )
        
        # Format and return
        return {
            "results": [r.to_dict() for r in results],
            "count": len(results),
            # ...
        }
```

---

## 3. All 7 MCP Tools Follow This Pattern

### Tool Inventory:

**1. pos_search_project** (`pos_search_project.py`)
- **Class:** `SearchTool`
- **Dependency:** `index_manager`, `query_tracker`
- **Actions (6):** search_standards, search_code, search_ast, find_callers, find_dependencies, find_call_paths
- **Pattern:** ✅ Full compliance

**2. pos_workflow** (`pos_workflow.py`)
- **Class:** `WorkflowTool`
- **Dependency:** `workflow_engine`
- **Actions (14):** list_workflows, start, get_phase, get_task, complete_phase, get_state, list_sessions, get_session, delete_session, pause, resume, retry_phase, rollback, get_errors
- **Pattern:** ✅ Full compliance

**3. pos_filesystem** (`pos_filesystem.py`)
- **Class:** `FilesystemTool`
- **Dependency:** `workspace_root`
- **Actions (12):** read, write, append, delete, move, copy, list, exists, stat, glob, mkdir, rmdir
- **Pattern:** ✅ Full compliance
- **Security:** Path validation, gitignore respect, safe defaults

**4. pos_browser** (`pos_browser.py`)
- **Class:** `BrowserTool`
- **Dependency:** `browser_manager`, `session_mapper`
- **Actions (24):** navigate, screenshot, console, query, evaluate, click, type, fill, select, wait, emulate_media, viewport, get_cookies, set_cookies, run_test, intercept_network, new_tab, switch_tab, close_tab, list_tabs, upload_file, download_file, get_local_storage, close
- **Pattern:** ✅ Full compliance

**5. get_server_info** (`get_server_info.py`)
- **Class:** `ServerInfoTool`
- **Dependency:** `server_runtime_info`, `index_manager`, `query_tracker`
- **Actions (4):** status, health, behavioral_metrics, version
- **Pattern:** ✅ Full compliance

**6. current_date** (`current_date.py`)
- **Simple Tool:** No actions (single function)
- **Pattern:** ✅ Partial (simpler, no dispatch needed)

**7. (Future tools drop in here...)**

---

## 4. Tool Registry: Auto-Discovery & Dependency Injection

### Location: `ouroboros/tools/registry.py`

**The Magic:**
```python
class ToolRegistry:
    """
    Auto-discovers and registers MCP tools from tools/ directory.
    
    Architecture:
    1. Scan tools/ for *.py files
    2. Import each module
    3. Find register_*_tool() functions
    4. Call with dependency injection
    5. Track success/failure
    """
    
    def __init__(self, tools_dir, mcp_server, dependencies):
        self.tools_dir = tools_dir
        self.mcp_server = mcp_server
        self.dependencies = dependencies  # {"index_manager": ..., "workflow_engine": ...}
```

**Discovery Process:**
```python
def discover_tools(self) -> List[Dict[str, Any]]:
    """Scan tools/ directory for register_*_tool functions."""
    discovered = []
    
    for tool_file in self.tools_dir.glob("*.py"):
        if tool_file.name in ("__init__.py", "registry.py"):
            continue
        
        # Import module
        module = importlib.import_module(f"ouroboros.tools.{tool_file.stem}")
        
        # Find registration functions
        for name, obj in inspect.getmembers(module):
            if name.startswith("register_") and name.endswith("_tool"):
                sig = inspect.signature(obj)
                params = list(sig.parameters.keys())
                
                discovered.append({
                    "function_name": name,
                    "function": obj,
                    "parameters": params,  # For dependency injection
                })
    
    return discovered
```

**Registration with Dependency Injection:**
```python
def register_tool(self, tool_info):
    """Register tool by calling its register_*_tool() function."""
    func = tool_info["function"]
    params = tool_info["parameters"]
    
    # Build arguments via dependency injection
    kwargs = {"mcp": self.mcp_server}
    
    for param in params:
        if param == "mcp":
            continue
        elif param in self.dependencies:
            kwargs[param] = self.dependencies[param]  # Inject!
        else:
            # Missing dependency - skip or use default
            logger.warning(f"Missing dependency: {param}")
            return 0
    
    # Call registration function
    count = func(**kwargs)
    logger.info(f"✅ Registered {tool_info['function_name']} ({count} tool(s))")
    
    return count
```

**All Tools Auto-Register:**
```python
def register_all(self):
    """Discover and register all tools."""
    discovered = self.discover_tools()
    
    for tool_info in discovered:
        self.register_tool(tool_info)  # Dependency injection happens here
    
    logger.info(f"📊 Tool Registration Summary: {len(discovered)} discovered")
```

---

## 5. Tool Registration Functions

### Pattern: Every Tool Exports `register_*_tool(mcp, dependencies)`

**Example 1: Search Tool**
```python
# ouroboros/tools/pos_search_project.py

def register_search_tool(
    mcp: Any,
    index_manager: Any,
    query_tracker: Optional[Any] = None
) -> int:
    """
    Register pos_search_project tool with FastMCP.
    
    Args:
        mcp: FastMCP server instance (required)
        index_manager: IndexManager instance (required)
        query_tracker: QueryTracker instance (optional)
    
    Returns:
        Number of tools registered (1)
    """
    tool_instance = SearchTool(mcp, index_manager, query_tracker)
    
    # Register tool (via @property decorator)
    _ = tool_instance.tool
    
    return 1  # 1 tool registered
```

**Example 2: Workflow Tool**
```python
# ouroboros/tools/pos_workflow.py

def register_workflow_tool(mcp: Any, workflow_engine: Any) -> int:
    """Register pos_workflow tool."""
    tool_instance = WorkflowTool(mcp, workflow_engine)
    _ = tool_instance.tool
    return 1
```

**Example 3: Filesystem Tool**
```python
# ouroboros/tools/pos_filesystem.py

def register_filesystem_tool(mcp: Any, workspace_root: Path) -> int:
    """Register pos_filesystem tool."""
    tool_instance = FilesystemTool(mcp, workspace_root)
    _ = tool_instance.tool
    return 1
```

**Example 4: Browser Tool**
```python
# ouroboros/tools/pos_browser.py

def register_browser_tool(
    mcp: Any,
    browser_manager: Any,
    session_mapper: Any
) -> int:
    """Register pos_browser tool."""
    tool_instance = BrowserTool(mcp, browser_manager, session_mapper)
    _ = tool_instance.tool
    return 1
```

**Example 5: Server Info Tool**
```python
# ouroboros/tools/get_server_info.py

def register_server_info_tool(
    mcp: Any,
    server_runtime_info: Any,
    index_manager: Any,
    query_tracker: Optional[Any] = None
) -> int:
    """Register get_server_info tool."""
    tool_instance = ServerInfoTool(mcp, server_runtime_info, index_manager, query_tracker)
    _ = tool_instance.tool
    return 1
```

**Example 6: Current Date Tool (Simpler)**
```python
# ouroboros/tools/current_date.py

def register_current_date_tool(mcp: Any) -> int:
    """Register current_date tool (no dependencies)."""
    
    @mcp.tool()
    async def current_date() -> Dict[str, Any]:
        """Get current date/time for preventing AI date errors."""
        from datetime import datetime
        now = datetime.now()
        
        return {
            "iso_date": now.strftime("%Y-%m-%d"),
            "iso_datetime": now.isoformat(),
            # ...
        }
    
    return 1
```

---

## 6. Architecture Flow: How It All Works Together

### Server Startup Sequence:

```
1. Server.__init__()
   ├── Initialize subsystems (IndexManager, WorkflowEngine, BrowserManager)
   ├── Create dependency dict
   └── Initialize ToolRegistry

2. ToolRegistry.register_all()
   ├── Scan tools/ directory
   ├── Import: pos_search_project.py
   │   └── Find: register_search_tool()
   ├── Import: pos_workflow.py
   │   └── Find: register_workflow_tool()
   ├── Import: pos_filesystem.py
   │   └── Find: register_filesystem_tool()
   ├── Import: pos_browser.py
   │   └── Find: register_browser_tool()
   ├── Import: get_server_info.py
   │   └── Find: register_server_info_tool()
   └── Import: current_date.py
       └── Find: register_current_date_tool()

3. For each register_*_tool():
   ├── Inspect function signature
   ├── Build kwargs via dependency injection
   │   ├── mcp: self.mcp_server
   │   ├── index_manager: self.dependencies["index_manager"]
   │   ├── workflow_engine: self.dependencies["workflow_engine"]
   │   ├── browser_manager: self.dependencies["browser_manager"]
   │   └── ... (match params to dependencies)
   ├── Call: register_search_tool(mcp, index_manager, query_tracker)
   │   ├── Create: SearchTool(mcp, index_manager, query_tracker)
   │   ├── Access: tool_instance.tool (triggers @mcp.tool() decoration)
   │   └── Return: 1
   └── Log: "✅ Registered register_search_tool (1 tool(s))"

4. Server Ready
   ├── All tools registered
   ├── All tools have @mcp.tool() decorations
   └── MCP protocol ready to dispatch
```

### AI Agent Call Flow:

```
1. AI Agent calls: pos_search_project(action="search_standards", query="...")

2. MCP Server routes to: SearchTool.tool() (the decorated function)

3. Tool function calls: self.dispatch(action, self.handlers, query=query, **kwargs)

4. ActionDispatchMixin.dispatch():
   ├── Extract session IDs (agent_session, task_session)
   ├── Record query in QueryTracker
   ├── Validate action in handlers dict
   ├── Lookup handler: self.handlers["search_standards"]
   ├── Invoke: _handle_search_standards(query=query, **kwargs)
   │   ├── Call: index_manager.get_index("standards")
   │   ├── Call: standards_index.search(query, method, n_results)
   │   └── Return: {"results": [...], "count": ...}
   ├── Wrap in success envelope: {"status": "success", "action": "search_standards", ...}
   └── Return to AI agent

5. On Error:
   ├── Catch exception in dispatch()
   ├── Log structured error
   ├── Wrap in error envelope: {"status": "error", "action": "...", "error": "...", "error_type": "..."}
   └── Return to AI agent (no crash!)
```

---

## 7. Key Architecture Benefits

### 1. **DRY (Don't Repeat Yourself)**
- ✅ Dispatch logic in ONE place (ActionDispatchMixin)
- ✅ Error handling in ONE place
- ✅ Response formatting in ONE place
- ✅ Query tracking in ONE place
- ✅ Logging in ONE place

**Without Mixin (hypothetical):**
```python
# Every tool would have 50+ lines of:
# - Action validation
# - Handler lookup
# - Error try/catch
# - Response wrapping
# - Logging
# - Query tracking
# TIMES 7 TOOLS = 350+ lines of duplication!
```

**With Mixin:**
```python
# ActionDispatchMixin: ~150 lines
# Each tool: ~5 lines of dispatch call
# 7 tools: 150 + (7 * 5) = 185 lines total
# Savings: 165 lines (47% reduction)
```

### 2. **Testability**
```python
# Mock subsystems easily
mock_index_manager = Mock()
tool = SearchTool(mcp, mock_index_manager)

# Test handler directly (no MCP protocol)
result = await tool._handle_search_standards("test query")
assert result["count"] > 0

# Verify subsystem calls
mock_index_manager.get_index.assert_called_with("standards")
```

### 3. **Maintainability**
- **Change dispatch behavior once** → affects all tools
- **Add query tracking** → one line in mixin
- **Change error format** → one method in mixin
- **Add new tool** → drop file in tools/, export register function

### 4. **Consistency**
- **All tools have same response format**
- **All tools have same error format**
- **All tools have same logging structure**
- **All tools integrate with QueryTracker**

### 5. **Extensibility**
```python
# Add new tool: Just drop a file!

# ouroboros/tools/pos_my_new_tool.py
class MyNewTool(ActionDispatchMixin):
    def __init__(self, mcp, my_subsystem):
        super().__init__(mcp)
        self.my_subsystem = my_subsystem
        self.handlers = {
            "do_thing": self._handle_do_thing,
        }
    
    @property
    def tool(self):
        @self.mcp.tool()
        async def pos_my_new_tool(action, **kwargs):
            return await self.dispatch(action, self.handlers, **kwargs)
        return pos_my_new_tool
    
    async def _handle_do_thing(self, **kwargs):
        return {"result": "done"}

def register_my_new_tool(mcp, my_subsystem):
    tool = MyNewTool(mcp, my_subsystem)
    _ = tool.tool
    return 1

# That's it! ToolRegistry auto-discovers and registers.
# No changes to server.py needed!
```

### 6. **Dependency Injection**
```python
# Registry inspects function signatures
# Matches params to available dependencies
# Calls with correct arguments

# Tools don't know HOW they get dependencies
# They just declare WHAT they need

# Want to swap IndexManager implementation?
# Just change server.py dependency dict
# All tools use new implementation (no tool changes needed)
```

---

## 8. Design Patterns Identified

### 1. **Mixin Pattern** (ActionDispatchMixin)
- **Purpose:** Share behavior across multiple classes
- **Benefit:** No inheritance hierarchy needed

### 2. **Template Method Pattern** (dispatch method)
- **Purpose:** Define algorithm skeleton, let subclasses fill in details
- **Benefit:** Consistent flow, customizable steps

### 3. **Strategy Pattern** (handlers dict)
- **Purpose:** Define family of algorithms, make them interchangeable
- **Benefit:** Easy to add/remove actions

### 4. **Facade Pattern** (Tool classes)
- **Purpose:** Unified interface to subsystems
- **Benefit:** AI agents don't know about IndexManager, WorkflowEngine, etc.

### 5. **Registry Pattern** (ToolRegistry)
- **Purpose:** Auto-discover and register components
- **Benefit:** Pluggable architecture

### 6. **Dependency Injection Pattern** (register functions)
- **Purpose:** Inversion of control for dependencies
- **Benefit:** Loose coupling, easy testing

### 7. **Factory Pattern** (register_*_tool functions)
- **Purpose:** Encapsulate object creation
- **Benefit:** Tools don't instantiate themselves

---

## 9. Query Tracking Integration

### Dual Session Concept:

**From ActionDispatchMixin.dispatch() (lines 159-188):**

```python
# Two session concepts:
# 1. agent_session_id: Long-lived (entire conversation)
#    - For behavioral metrics
#    - Tracks all queries across days/weeks
#    - Used for: "How diverse are queries?"
#
# 2. task_session_id: Short-lived (per user request with timeout)
#    - For prepend gamification
#    - Resets after timeout (5 minutes)
#    - Used for: "📊 Queries: 3/5 | Unique: 2"

agent_session_id = session_id or "default_session"
task_session_id = extract_session_id(client_id=agent_session_id)

# Record in QueryTracker under BOTH sessions
self.query_tracker.record_query(agent_session_id, query)
self.query_tracker.record_query(task_session_id, query)
```

**This enables:**
- **Long-term metrics:** Query diversity over weeks
- **Short-term feedback:** "You're at 3/5 queries, try different angles"
- **Behavioral reinforcement:** Encourages thorough querying

---

## 10. Middleware Integration Points

### PrependGenerator:

**From pos_search_project.py (lines 163-172):**
```python
# Generate prepend message for first result
prepend = None
if self.prepend_generator and task_session_id:
    prepend = self.prepend_generator.generate(
        task_session_id,
        query,
        results,
        "search_standards"
    )

# Inject prepend into first result
if prepend and results:
    results[0].content = f"{prepend}\n\n---\n\n{results[0].content}"
```

**Result:**
```
📊 Queries: 3/5 | Unique: 2 | Angles: 📖✓ 📍⬜ 🔧⬜ ⭐⬜ ⚠️⬜
💡 Try: 'What is lazy-load mode indexes?'

---

[Actual search result content...]
```

**This is the gamification layer!**

---

## 11. Comparison to Alternative Architectures

### ❌ Alternative 1: Flat Functions (No Classes)
```python
# What it would look like:
@mcp.tool()
async def pos_search_project(action, query, **kwargs):
    if action == "search_standards":
        # 50 lines of error handling, validation, query tracking...
        results = index_manager.get_index("standards").search(...)
        # 20 lines of response formatting...
        return {"status": "success", ...}
    elif action == "search_code":
        # Another 70 lines...
    # Repeat for 6 actions...
    # Total: 400+ lines per tool
```

**Problems:**
- ❌ Massive functions (400+ lines)
- ❌ Duplicated error handling (7 tools × 6 actions = 42 times)
- ❌ Hard to test (mocking is painful)
- ❌ Hard to change (modify 42 places for new behavior)

### ❌ Alternative 2: Manual Registration
```python
# server.py would have:
search_tool = SearchTool(mcp, index_manager)
workflow_tool = WorkflowTool(mcp, workflow_engine)
filesystem_tool = FilesystemTool(mcp, workspace_root)
browser_tool = BrowserTool(mcp, browser_manager, session_mapper)
# ... manual for every tool
```

**Problems:**
- ❌ Adding tool requires editing server.py
- ❌ Can't discover tools dynamically
- ❌ Tight coupling between server and tools

### ✅ Chosen Architecture: Mixin + Registry
```python
# Tools are self-contained
# Registry auto-discovers
# Dependencies injected
# Clean separation
```

**Benefits:**
- ✅ DRY (no duplication)
- ✅ Testable (mock dependencies)
- ✅ Maintainable (change once)
- ✅ Extensible (drop in files)
- ✅ Consistent (same patterns)

---

## 12. Key Takeaways

### For Building New Tools:

1. **Inherit from ActionDispatchMixin**
2. **Define self.handlers dict** (action → method)
3. **Implement @property def tool()** with @mcp.tool() decorator
4. **Implement pure business logic handlers** (no boilerplate)
5. **Export register_*_tool(mcp, dependencies)** function
6. **Drop file in tools/** (auto-discovered!)

### For Understanding Existing Tools:

1. **Look at handlers dict** → see all actions
2. **Read _handle_* methods** → understand business logic
3. **Ignore dispatch boilerplate** → it's in the mixin
4. **Check register function** → see dependencies

### For Modifying Behavior:

1. **All tools?** → Modify ActionDispatchMixin
2. **One tool?** → Modify its _handle_* methods
3. **New action?** → Add to handlers dict + implement _handle_* method

---

## 13. Architecture Documentation Quality

### What Makes This Architecture Good:

1. **Self-Documenting Code**
   - Class names describe purpose (SearchTool, WorkflowTool)
   - Method names describe actions (_handle_search_standards)
   - Registration functions are explicit

2. **Comprehensive Docstrings**
   - Every module has architecture overview
   - Every class has usage examples
   - Every method has parameter descriptions
   - Traceability references (FR-XXX)

3. **Consistent Patterns**
   - Same structure across all tools
   - Same error handling
   - Same response format
   - Easy to learn one, understand all

4. **Separation of Concerns**
   - Tools: Dispatch + validation
   - Handlers: Business logic
   - Subsystems: Implementation
   - Registry: Discovery

5. **Testability by Design**
   - Dependency injection
   - Pure functions (handlers)
   - Mockable subsystems
   - No global state

---

## Conclusion

The MCP tools architecture is a **masterclass in software design**:

✅ **DRY** - Dispatch logic in one place  
✅ **SOLID** - Single responsibility, open/closed, dependency inversion  
✅ **Testable** - Pure handlers, dependency injection  
✅ **Maintainable** - Change once, affect all  
✅ **Extensible** - Drop in new files, auto-discovered  
✅ **Consistent** - Same patterns everywhere  

**This is production-grade architecture.**

The ActionDispatchMixin + ToolRegistry combination creates a **pluggable, self-documenting, maintainable system** that's a joy to extend and debug.

**Used praxis OS (graph traversal + code intelligence) to understand praxis OS.**

Meta complete. 🎯


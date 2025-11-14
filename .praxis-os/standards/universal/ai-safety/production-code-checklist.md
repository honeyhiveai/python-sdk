# Production Code Checklist - prAxIs OS Framework

**CRITICAL: ALL code written by AI must meet these standards - NO EXCEPTIONS**

**Date**: October 6, 2025  
**Status**: Active  
**Scope**: Every code change in prAxIs OS Framework  
**Context**: We are building a framework that guides other projects - our code must exemplify the standards we teach

---

## 🚨 The 5-Second Rule - Production Code Quick Reference (TL;DR)

**Keywords for search**: production code checklist, code quality standards, AI code review, before writing code, quality checklist, configuration management, concurrency analysis, failure modes, resource lifecycle, test coverage, code review checklist, production-ready code

**Before writing ANY code, answer these 5 questions:**

1. **Configuration?** → Single source of truth (RAGConfig dataclass with defaults)
2. **Shared state?** → Concurrency analysis (threading.RLock, never assume thread-safety)
3. **How does this fail?** → Graceful degradation (try/except with logging + fallback)
4. **Resources?** → Lifecycle management (context managers, explicit cleanup)
5. **Tests?** → Unit + integration coverage (happy path + failure modes)

**When to query this standard:**
- Before starting new feature → `pos_search_project(content_type="standards", query="production code checklist")`
- During code review → `pos_search_project(content_type="standards", query="code quality requirements")`
- When adding dependencies → `pos_search_project(content_type="standards", query="dependency version management")`
- When handling failures → `pos_search_project(content_type="standards", query="graceful degradation patterns")`
- When managing state → `pos_search_project(content_type="standards", query="concurrency thread safety")`

**Remember: We teach quality standards - we must exemplify them.**

**For complete checklist with examples, continue reading below.**

---

## Questions This Answers

- "What should I check before committing code?"
- "How do I ensure my code is production-ready?"
- "What are the quality standards for AI-written code?"
- "How do I handle configuration in prAxIs OS?"
- "When do I need concurrency analysis?"
- "How should I handle failures gracefully?"
- "What documentation is required for production code?"
- "What testing is required before committing?"

---

## 🎯 Core Principle

**"AI has no excuse for shortcuts - especially when building a quality framework."**

**We are prAxIs OS - we dogfood our own standards.**

If we ship bugs, we undermine the entire framework. Every line must be production-grade because:
- AI doesn't get tired
- AI doesn't have time pressure
- Quality checks add seconds, debugging takes hours
- **We teach quality - we must demonstrate quality**

---

## 📋 Universal Checks (Tier 1 - MANDATORY FOR ALL CODE)

### 1. How to Manage Configuration (Framework-Specific)

**Question**: Does this code read or modify configuration?

**Configuration sources in prAxIs OS:**
- `config.json` - User-editable configuration
- Environment variables
- Dataclass defaults (in `models.py`)
- Hardcoded constants (should be avoided)

**If YES → Configuration standards REQUIRED:**
- [ ] Is there a single source of truth for defaults?
- [ ] Are defaults clearly documented?
- [ ] Can users override via config.json?
- [ ] Are paths resolved correctly (relative to project root)?
- [ ] Is missing config handled gracefully?

**Required Pattern:**
```python
@dataclass
class RAGConfig:
    """RAG configuration with sane defaults."""
    standards_path: str = ".praxis-os/standards"  # Clear default
    
    @classmethod
    def from_config_file(cls, base_path: Path) -> "RAGConfig":
        """Load from config.json with fallback to defaults."""
        config_path = base_path / "config.json"
        
        if not config_path.exists():
            logger.info("No config.json, using defaults")
            return cls()  # All defaults
        
        try:
            with open(config_path) as f:
                data = json.load(f)
            
            rag_section = data.get("rag", {})
            return cls(
                standards_path=rag_section.get("standards_path", cls.standards_path),
                # ...
            )
        except Exception as e:
            logger.warning(f"Config load failed: {e}, using defaults")
            return cls()
```

**Anti-Pattern (FORBIDDEN):**
```python
# Bad: Multiple places define defaults
def _load_config():
    defaults = {"path": "universal/standards"}  # ❌ Hard to find
    
# Bad: Scattered path construction  
self.path = base / "standards"  # ❌ Not from config
```

### 2. How to Analyze Shared State and Concurrency

**Question**: Does this code access shared state?

**Shared state in prAxIs OS:**
- Vector index (LanceDB table)
- Workflow state (JSON files)
- File watcher rebuild state
- RAG engine loaded index
- Configuration cache

**If YES → Concurrency analysis REQUIRED:**
- [ ] What happens if 2+ operations access this simultaneously?
- [ ] Does the library handle locking internally? (Research - NEVER assume)
- [ ] Do I need external locking? (threading.Lock, RLock)
- [ ] How do I test concurrent access?

**Example (RAG Index Hot Reload):**
```python
# CONCURRENCY: Thread-safe via RLock for read/write coordination
# Validated with: test_concurrent_search_during_reload.py
class RAGEngine:
    def __init__(self):
        self._lock = threading.RLock()  # Reentrant for nested calls
        self._rebuilding = threading.Event()
    
    def search(self, query: str) -> List[Dict]:
        """Thread-safe search with rebuild coordination."""
        if self._rebuilding.is_set():
            self._rebuilding.wait(timeout=30)
        with self._lock:  # Read lock
            return self._vector_search(query)
    
    def reload_index(self) -> None:
        """Thread-safe index reload (blocks all searches)."""
        with self._lock:  # Write lock (blocks all reads)
            self._rebuilding.set()
            try:
                # Rebuild logic
                pass
            finally:
                self._rebuilding.clear()
```

### 3. How to Manage Dependencies and Versions

**Question**: Does this code add/modify dependencies?

**If YES → Version justification REQUIRED:**
- [ ] Why this version or range?
- [ ] What changed between versions that matters?
- [ ] Stability/maturity level?
- [ ] Known issues in this version?

**Version Standards:**
- `package~=1.2.0` - PREFERRED (patch-level: 1.2.x)
- `package>=1.2.0,<2.0.0` - When breaking changes expected
- `package==1.2.0` - RARE (critical stability only)
- `package>=1.2.0` - **FORBIDDEN** (non-deterministic)

**Documentation:**
```python
# mcp_server/requirements.txt
lancedb~=0.17.0  # Latest stable with improved concurrency, avoid 0.16.x race conditions
watchdog~=6.0.0   # Stable file watching, fixes macOS symlink issues in 5.x
```

### 4. How to Analyze and Handle Failure Modes

**Question**: How does this code fail gracefully?

**EVERY code block must answer:**
- [ ] What if external service is down? (LLM API, file system)
- [ ] What if network times out?
- [ ] What if input is malformed?
- [ ] What if resources exhausted?
- [ ] What's the degradation path?

**Required Pattern:**
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    # Graceful degradation
    result = fallback_strategy()
```

**Anti-Pattern (FORBIDDEN):**
```python
try:
    result = risky_operation()
except:  # ❌ Bare except
    pass  # ❌ Silent failure
```

### 5. How to Manage Resource Lifecycle

**Question**: Does this manage resources?

**Resources in prAxIs OS:**
- File handles (config.json, workflow files)
- Vector database connections
- File watcher observers
- Background threads (debounce threads)

**If YES → Lifecycle management REQUIRED:**
- [ ] How acquired? (open, connect, Observer())
- [ ] How released? (close, stop, join)
- [ ] What during reload/restart?
- [ ] What if cleanup fails?
- [ ] Memory leak potential?

**Required Pattern:**
```python
# Good: Context manager
with open(config_path) as f:
    data = json.load(f)

# Or explicit cleanup
observer = None
try:
    observer = Observer()
    observer.start()
    # ...
finally:
    if observer:
        observer.stop()
        observer.join(timeout=5)
```

### 6. How to Document Code Properly

**Question**: Can another developer (or AI) understand this code?

**EVERY code element must have Sphinx-style docstrings:**
- [ ] All public functions documented
- [ ] All classes documented
- [ ] All modules documented
- [ ] All parameters described with types
- [ ] Return values documented
- [ ] Exceptions documented
- [ ] Usage examples for complex code

**Required Format: Sphinx-Style Docstrings**

**Functions:**
```python
def get_task(session_id: str, phase: int, task_number: int) -> Dict[str, Any]:
    """
    Get full content for a specific task (horizontal scaling).
    
    Retrieves complete task content including execution steps and commands.
    Follows meta-workflow principle: work on one task at a time.
    
    :param session_id: Workflow session identifier (from start_workflow)
    :param phase: Phase number (0-8)
    :param task_number: Task number within the phase (1-10)
    :return: Dictionary with task content, execution steps, and validation criteria
    :raises ValueError: If session_id invalid or task not found
    :raises KeyError: If phase/task_number out of range
    
    Example:
        >>> response = start_workflow("test_generation_v3", "test.py")
        >>> session_id = response["session_id"]
        >>> task = get_task(session_id, phase=1, task_number=1)
        >>> print(task["execution_steps"])
    """
```

**Classes:**
```python
class ServerFactory:
    """
    Factory for creating MCP server with dependency injection.
    
    This factory coordinates the creation and wiring of all MCP server
    components, ensuring proper dependency injection and configuration
    propagation throughout the system.
    
    :param config: Validated ServerConfig with all settings
    :type config: ServerConfig
    
    Attributes:
        config (ServerConfig): Server configuration
        paths (Dict[str, Path]): Resolved filesystem paths
    
    Example:
        >>> config = ConfigLoader.load(base_path)
        >>> factory = ServerFactory(config)
        >>> server = factory.create_server()
        >>> server.run()
    """
    
    def __init__(self, config: ServerConfig):
        """
        Initialize factory with validated configuration.
        
        :param config: Validated ServerConfig
        :raises ValueError: If config validation failed
        """
```

**Modules:**
```python
"""
Configuration management for prAxIs OS MCP Server.

This module provides configuration loading, validation, and management
for the MCP server. It implements a single source of truth for all
configuration with graceful fallback to sensible defaults.

Classes:
    ConfigLoader: Load configuration from config.json
    ConfigValidator: Validate configuration paths and settings

Example:
    >>> from mcp_server.config import ConfigLoader, ConfigValidator
    >>> config = ConfigLoader.load(Path(".praxis-os"))
    >>> errors = ConfigValidator.validate(config)
    >>> if errors:
    ...     raise ValueError(f"Invalid config: {errors}")
"""
```

**Why Sphinx Style:**
- ✅ Machine-parseable (generates API docs)
- ✅ IDE support (autocomplete, tooltips)
- ✅ Standard format (familiar to Python developers)
- ✅ Compatible with type hints

**Anti-Pattern (FORBIDDEN):**
```python
# Bad: No docstring
def process_data(x, y):
    return x + y

# Bad: Vague docstring
def process_data(x, y):
    """Process data."""
    return x + y

# Bad: Missing parameter/return docs
def process_data(x, y):
    """Process data and return result."""
    return x + y
```

### 7. How to Ensure Adequate Test Coverage

**Question**: How do I validate this works?

**EVERY code change must have:**
- [ ] Unit test for happy path
- [ ] Unit test for failure modes
- [ ] Integration test if touching external systems
- [ ] Concurrent test if touching shared state

**Minimum:**
```python
def test_happy_path():
    result = my_function(valid_input)
    assert result == expected_output

def test_failure_mode():
    with pytest.raises(SpecificException):
        my_function(invalid_input)
```

---

## 🏗️ Framework-Specific Checks (Tier 2)

### 7. How to Validate Dogfooding (Installation Logic)

**Question**: Does this code handle installation/file-copying logic?

**prAxIs OS dogfoods itself - validate consumer experience:**
- [ ] Does this work with real copied files (not symlinks)?
- [ ] Does this handle both source (`universal/`) and installed (`.praxis-os/`)?
- [ ] Are paths resolved relative to correct base?
- [ ] Does file watcher watch installed files, not source?

**Testing:**
```bash
# Test dogfooding workflow
echo "test" >> universal/standards/test.md
cp -r universal/standards .praxis-os/standards/universal
# Verify MCP finds new content
```

### 8. How to Design MCP Tool Interfaces

**Question**: Does this code implement or modify MCP tools?

**If YES → MCP standards REQUIRED:**
- [ ] Is the tool discoverable via MCP protocol?
- [ ] Are parameters clearly documented with examples?
- [ ] Are return values well-structured and documented?
- [ ] Are errors returned as structured data (not exceptions to LLM)?
- [ ] Is there usage documentation in `universal/usage/`?

**Required Pattern:**
```python
@server.tool()
def my_tool(
    param1: str,
    param2: int = 10
) -> Dict[str, Any]:
    """
    Tool description for AI agents.
    
    :param param1: Clear parameter description
    :param param2: Optional parameter with default
    :return: Structured response dict
    """
    try:
        result = perform_operation(param1, param2)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "fallback": "Use cached result"
        }
```

### 9. How to Maintain RAG Index Consistency

**Question**: Does this code modify or rebuild the RAG index?

**If YES → Index consistency REQUIRED:**
- [ ] Is file watcher notified of changes?
- [ ] Is incremental update used (not full rebuild)?
- [ ] Are concurrent searches blocked during rebuild?
- [ ] Is the index validated after rebuild?
- [ ] Are errors logged with context?

**Required Pattern:**
```python
def reload_index(self) -> None:
    """Reload index with concurrency safety."""
    with self._lock:  # Block all searches
        self._rebuilding.set()
        try:
            # Clean up old connections
            if hasattr(self, 'table'):
                del self.table
            
            # Reload
            self.table = self.db.open_table("praxis_os_index")
            logger.info("✅ Index reloaded successfully")
        except Exception as e:
            logger.error(f"❌ Index reload failed: {e}")
            # Keep using old index if reload fails
        finally:
            self._rebuilding.clear()
```

### 10. How to Manage Workflow State

**Question**: Does this code manage workflow state?

**If YES → State persistence REQUIRED:**
- [ ] Is state saved after each phase transition?
- [ ] Can state be recovered after crash?
- [ ] Are state files validated on load?
- [ ] Is concurrent state access handled?
- [ ] Are state files cleaned up after workflow completion?

---

## ✅ Commit Message Requirements

```
type(scope): brief description

**Tier 1 Checks:**
- Configuration: [RAGConfig with clear defaults | No config changes]
- Concurrency: [Thread-safe via RLock | No shared state]
- Dependencies: [No changes | Added package~=X.Y.Z because reason]
- Failure Modes: [Graceful degradation via fallback | N/A]
- Resources: [Context manager for cleanup | N/A]
- Tests: [test_happy_path + test_failure]

**Tier 2 Checks (Framework-Specific):**
- Dogfooding: [Tested with real copies | N/A]
- MCP Interface: [Documented in universal/usage/ | N/A]
- RAG Index: [Incremental update with locking | N/A]
- Workflow State: [Persisted after transition | N/A]
```

---

## 🚨 Anti-Patterns (FORBIDDEN)

### **1. Configuration Scattered Across Files**
```python
# Bad: Defaults in multiple places
# file1.py
defaults = {"path": "standards"}
# file2.py  
self.path = base / "standards"
```
**Fix:** Single RAGConfig dataclass with all defaults.

### **2. Assuming Thread-Safety**
```python
# Bad: "LanceDB probably handles this"
self.table = db.open_table("index")  # ❌ No locking
```
**Fix:** Research library docs, add external locking when needed.

### **3. Hardcoded Paths**
```python
# Bad: Hardcoded instead of from config
self.standards_path = base_path / "standards"
```
**Fix:** Load from RAGConfig with defaults.

### **4. Silent Failures**
```python
# Bad: File watcher fails silently
try:
    self._schedule_rebuild()
except:
    pass  # ❌ User has no idea rebuild failed
```
**Fix:** Log errors, notify user, use fallback.

---

## 📚 Cross-References and Related Standards

### Related Architecture Standards

Query when implementing production code:

```python
# For concurrency patterns
pos_search_project(content_type="standards", query="thread safety concurrency patterns")

# For graceful degradation  
pos_search_project(content_type="standards", query="failure modes graceful degradation")

# For system architecture
pos_search_project(content_type="standards", query="dependency injection architecture patterns")

# For testing strategy
pos_search_project(content_type="standards", query="test pyramid unit integration")
```

**Related Standards:**
- [Concurrency Patterns](../concurrency/) - Thread-safety, locking strategies
- [Failure Modes](../failure-modes/) - Graceful degradation patterns
- [SOLID Principles](../architecture/solid-principles.md) - Class design for maintainability
- [Test Pyramid](../testing/test-pyramid.md) - Testing strategy and ratios
- [Operating Model](../../usage/operating-model.md) - Human vs AI roles

### When to Query This Checklist

```python
# Before starting implementation
pos_search_project(content_type="standards", query="production code checklist")

# During code review
pos_search_project(content_type="standards", query="code quality standards AI")

# When debugging quality issues
pos_search_project(content_type="standards", query="common code quality mistakes")

# When onboarding to prAxIs OS
pos_search_project(content_type="standards", query="prAxIs OS code standards")
```

---

## 🎯 The 5-Second Rule (Framework Edition)

**Before writing ANY code:**

1. **Configuration?** → Single source of truth
2. **Shared state?** → Concurrency analysis
3. **How does this fail?** → Graceful degradation
4. **Resources?** → Lifecycle management
5. **Tests?** → Unit + integration coverage

**Remember: We teach quality standards - we must exemplify them.**

**This is not optional. This is the baseline for prAxIs OS Framework code.**

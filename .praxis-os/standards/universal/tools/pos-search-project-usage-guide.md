# pos_search_project Usage Guide

**Keywords for search**: pos_search_project, code search, semantic search, AST search, call graph, find callers, find dependencies, call paths, structural search, tree-sitter, CodeBERT embeddings, how to search code, how to find function callers, how to trace dependencies, graph traversal, code intelligence, symbol search, node type search, multi-repo search, partition filtering, cross-repository search, search multiple repos, search across repositories

**This standard defines how to use the `pos_search_project` tool for comprehensive code intelligence, semantic search, and call graph analysis.**

---

## 🚨 TL;DR - pos_search_project Quick Reference

**Core Principle:** `pos_search_project` provides unified access to semantic search, structural code analysis (AST), and call graph traversal. Choose the right action for your task.

**6 Actions Available:**

1. **search_standards** - Natural language search across standards documentation (hybrid: vector + FTS + RRF)
2. **search_code** - Semantic code search using CodeBERT embeddings (meaning-based)
3. **search_ast** - Structural code search by AST node type (syntax-based, uses tree-sitter)
4. **find_callers** - Who calls this function? (reverse lookup, graph traversal)
5. **find_dependencies** - What does this function call? (forward lookup, graph traversal)
6. **find_call_paths** - How does function A reach function B? (path finding, recursive CTEs)

**When to Use What (Quick Reference):**

| Need | Tool | Example |
|------|------|---------|
| Understand concept/pattern | `pos_search_project` | `search_code("error handling")` |
| Find exact symbol | `grep` | `grep "def my_function"` |
| Read full file | `read_file` | `read_file("src/module.py")` |
| Learn system | `pos_search_project` | `search_standards("how does X work")` |
| Verify existence | `grep` | `grep "import MyClass"` |
| Implement changes | `read_file` | After discovery with pos_search_project |

**Action-Specific Reference:**

| Task | Action | Example Query |
|------|--------|---------------|
| Find documentation | `search_standards` | "how to create standards" |
| Find code by meaning | `search_code` | "error handling patterns" |
| Find code by structure | `search_ast` | "if_statement" or "class_definition" |
| Find who calls X | `find_callers` | "route_action" |
| Find what X calls | `find_dependencies` | "build_index" |
| Trace call chain | `find_call_paths` | from="main" to="database_query" |

**When in Doubt:**
```
1. Start with pos_search_project (discovery → build understanding)
2. Use grep to verify exact details (verification → confirm specifics)
3. Use read_file for final implementation (implementation → make changes)
```

**Common Mistakes:**
- ❌ Using natural language for AST search ("find all functions" instead of "function_definition")
- ❌ Using `search_code` when you need exact structure (use `search_ast` for syntax patterns)
- ❌ Searching for undefined symbols in call graph (returns empty, not an error)
- ❌ Using `search_standards` for code (use `search_code` instead)
- ❌ Using grep for semantic queries (use `search_code` instead)
- ❌ Using pos_search_project for exact matches (use `grep` instead - it's faster)
- ❌ Reading entire files before discovery (use pos_search_project first to narrow scope)

**Quick Test:**
```python
# Does it work?
pos_search_project(action="search_ast", query="function_definition", n_results=3)
# Should return 3 function definitions with file paths and line numbers
```

---

## 🎯 Questions This Answers

- How do I search for code by meaning vs by structure?
- What's the difference between semantic search and AST search?
- How do I find who calls a specific function?
- How do I trace function dependencies?
- How do I find call paths between two functions?
- What query patterns work best for each action?
- When should I use search_code vs search_ast?
- How do I search for specific code constructs (loops, error handlers, etc.)?
- What are tree-sitter node types and how do I use them?
- How do I interpret call graph results?
- **When should I use pos_search_project vs grep vs read_file?**
- **What's the cognitive load difference between code index and manual grep?**
- **How do I build understanding systematically with multiple queries?**
- **How do I search across multiple repositories simultaneously?**
- **What are partitions and how do I use partition filters?**
- **How do I compare implementations across different projects?**
- **When do I need to specify a partition filter?**
- **How do I trace bugs across multiple repositories?**

---

## 🔀 When to Use: pos_search_project vs grep vs read_file

**Core Insight:** These tools are **complementary**, not competitive. Each excels in different scenarios.

### Use pos_search_project when:

**Building Understanding (Reasoning Phase)**
- ✅ Finding concepts/patterns → `search_code("error handling patterns")`
- ✅ Understanding "how does X work?" → `search_standards("workflow execution")`
- ✅ Tracing relationships → `find_callers("process_data")`
- ✅ Discovering architecture → `find_call_paths("main", "database")`
- ✅ Finding structural patterns → `search_ast("try_statement")`
- ✅ Cross-file exploration → Call graph traversal

**Why better than grep:**
- Semantic understanding (finds meaning, not just text)
- Relationship mapping (who calls, what calls, how connected)
- Structured results (JSON with metadata, scores, context)
- Cross-file synthesis (builds complete picture)

**Cognitive load:** Low - System builds understanding for you

**Time investment:** 2-5 minutes for comprehensive understanding

---

### Use grep when:

**Finding Exact Matches (Verification Phase)**
- ✅ You know the exact symbol → `grep "def my_function"`
- ✅ Quick existence check → `grep "import MyClass"`
- ✅ String literal search → `grep "error_message"`
- ✅ Fast verification → "Does this exist anywhere?"

**Why better than pos_search_project:**
- Instant results (no embedding computation)
- Exact text matching (no semantic interpretation)
- Simple output (just file:line:match)
- Regex support (complex patterns)

**Cognitive load:** Medium - You manually synthesize results

**Time investment:** Seconds for single queries, minutes for manual chaining

---

### Use read_file when:

**Reading Full Context (Implementation Phase)**
- ✅ You know the exact file path → `read_file("src/module.py")`
- ✅ Need full file context → Understanding complete file structure
- ✅ Implementing in specific file → Need to see all surrounding code
- ✅ Deep dive on single file → After discovery narrows to one file

**Why better than pos_search_project:**
- Complete file context (no chunking)
- Linear reading (natural flow)
- Direct access (no search needed)
- See everything (imports, structure, comments)

**Cognitive load:** High - You process entire file

**Time investment:** 5-20 minutes per file depending on size

---

## 🧠 The Cognitive Load Difference

### Manual Workflow: grep + read_file (20+ minutes)

```bash
# High cognitive load, fragmented understanding:

# Step 1: Find the function (noisy results)
grep "route_action" -r .
# → 47 matches across 12 files (mostly irrelevant)

# Step 2: Find definition (manual filtering)
grep "def route_action" -r .
# → Found in index_manager.py

# Step 3: Read implementation (large file)
read_file("ouroboros/subsystems/rag/index_manager.py")
# → 800 lines, find the relevant 50 lines manually

# Step 4: Find all callers (manual)
grep "route_action(" -r .
# → 6 matches, now read each caller file

read_file("ouroboros/tools/pos_search_project.py")
# → Another 500 lines, find relevant calls

# Step 5: Understand what it calls (manual)
# Read through function, identify called functions
grep "ActionableError" -r .
grep "search" -r .
# → Repeat for each dependency...

# Mental model: Fragmented, incomplete, many irrelevant details
# Risk: Miss connections, incorrect understanding
```

**Total:** 20-30 minutes, high cognitive load, fragmented understanding

---

### Code Index Workflow: pos_search_project (2-5 minutes)

```python
# Low cognitive load, systematic understanding:

# Step 1: Understand what it is (30 seconds)
search_code("route_action dispatch pattern")
# → Returns: index_manager.py, relevant code chunk, context

# Step 2: Find all callers (30 seconds)
find_callers("route_action", max_depth=2)
# → Returns: 6 callers with file paths, line numbers, call chains
# → Structured data: {caller_name, caller_file, caller_line, depth, path}

# Step 3: Find all dependencies (30 seconds)
find_dependencies("route_action", max_depth=2)
# → Returns: All called functions/classes
# → Structured data: {dep_name, dep_file, dep_line, relationship}

# Step 4: Trace execution flow (30 seconds)
find_call_paths("_handle_search_code", "route_action")
# → Returns: Complete call paths
# → ["_handle_search_code", "route_action"]

# Mental model: Complete, accurate, structured
# Risk: None - all relationships mapped
```

**Total:** 2-5 minutes, low cognitive load, complete understanding

**Reduction:** 75-85% time savings, 90% cognitive load reduction

---

## 🎯 The Hybrid Workflow (Recommended)

**Phase 1: Discovery (Use pos_search_project)**
```python
# Goal: Build comprehensive understanding

# Understand the domain
search_standards("how does feature X work")

# Find the implementation
search_code("feature X implementation patterns")

# Map the architecture
find_callers("core_function")
find_dependencies("core_function")
find_call_paths("entry_point", "core_function")
```

**Outcome:** Complete mental model of the system

---

**Phase 2: Verification (Use grep)**
```bash
# Goal: Verify specific details quickly

# Confirm exact symbol
grep "def exact_function_name"

# Check imports
grep "from module import"

# Verify string literals
grep "specific_error_message"
```

**Outcome:** Confirmed exact details

---

**Phase 3: Implementation (Use read_file)**
```python
# Goal: Deep dive on specific files

# Read target file fully
read_file("path/to/target.py")

# Read test file
read_file("tests/test_target.py")

# Read config
read_file("config.yaml")
```

**Outcome:** Full context for changes

---

## 📊 Performance & Context Trade-offs

| Tool | Speed | Accuracy | Context | Cognitive Load | Best For |
|------|-------|----------|---------|----------------|----------|
| **search_standards** | Medium (100-500ms) | High (semantic) | Targeted chunks | Low | Learning system |
| **search_code** | Medium (200-800ms) | High (semantic) | Relevant code | Low | Finding patterns |
| **search_ast** | Fast (50-200ms) | Perfect (exact) | Structural | Low | Syntax queries |
| **find_callers** | Fast (50-300ms) | Perfect (graph) | Relationship map | Very Low | Impact analysis |
| **find_dependencies** | Fast (50-300ms) | Perfect (graph) | Relationship map | Very Low | Tracing calls |
| **find_call_paths** | Medium (100-500ms) | Perfect (graph) | Full paths | Very Low | Flow understanding |
| **grep** | Very Fast (<50ms) | Perfect (exact) | Match only | Medium | Exact matches |
| **read_file** | Very Fast (<50ms) | N/A | Full file | High | Complete context |

**Key Insights:**
- **Semantic search** = Slower but finds concepts (not just text)
- **Graph traversal** = Fast + structured + complete relationships
- **Grep** = Fastest but requires manual synthesis
- **Read file** = Instant but highest cognitive load

---

## 🔬 Reasoning Workflows: Building Systematic Understanding

These workflows show how to use multiple queries to build comprehensive understanding, not just find things.

### Workflow 1: Understanding a New Subsystem

**Goal:** Build complete mental model of unfamiliar code

```python
# Phase 1: High-level discovery (2 minutes)
search_standards("subsystem name overview architecture")
# → Understand: Purpose, design, key concepts

search_code("subsystem initialization entry point")
# → Understand: Where it starts, how it's invoked

# Phase 2: Architectural mapping (2 minutes)
search_ast("class_definition")  # Filter by subsystem path
# → Understand: Main classes, structure

find_dependencies("MainSubsystemClass.__init__")
# → Understand: What it depends on

find_callers("MainSubsystemClass.primary_method")
# → Understand: Who uses it, integration points

# Phase 3: Data flow tracing (2 minutes)
find_call_paths("entry_point", "core_operation")
# → Understand: Execution flow, call chains

search_code("error handling patterns")  # In subsystem
# → Understand: Error handling strategy

# Phase 4: Pattern discovery (1 minute)
search_ast("try_statement")  # In subsystem
# → Understand: Where errors are caught

search_code("configuration validation")
# → Understand: How it's configured

# SYNTHESIS (30 seconds):
# - Entry points: [list]
# - Core classes: [list]
# - Key dependencies: [list]
# - Integration points: [list]
# - Error handling: [strategy]
# - Configuration: [approach]

# Mental model: COMPLETE ✅
# Time: 7-8 minutes
# Cognitive load: Low (system did the work)
```

**Compare to grep+read:** Would take 45-60 minutes with high cognitive load

---

### Workflow 2: Tracing a Bug

**Goal:** Understand how bad data flows through system

```python
# Phase 1: Find the error location (1 minute)
search_code("error message text from logs")
# → Understand: Where error is raised

find_callers("function_that_errors")
# → Understand: Who calls the failing function

# Phase 2: Trace data flow (2 minutes)
find_call_paths("data_entry_point", "function_that_errors")
# → Understand: How data reaches the error

find_dependencies("each_function_in_path")
# → Understand: What each function does to the data

# Phase 3: Find validation points (1 minute)
search_code("validation data checking")  # In the call path
# → Understand: Where data should be validated

search_ast("if_statement")  # In relevant functions
# → Understand: What checks exist

# Phase 4: Find similar patterns (1 minute)
search_code("similar validation patterns")
# → Understand: How other code handles this

# SYNTHESIS:
# - Data enters at: [point]
# - Flows through: [path]
# - Validation missing at: [location]
# - Fix: Add validation at step X
# - Verify: No other code paths have same issue

# Mental model: ROOT CAUSE IDENTIFIED ✅
# Time: 5 minutes
# Cognitive load: Low
```

**Compare to grep+read:** Would take 30-45 minutes, might miss related issues

---

### Workflow 3: Refactoring Impact Analysis

**Goal:** Safely rename/modify a function

```python
# Phase 1: Map current usage (2 minutes)
find_callers("target_function", max_depth=3)
# → Understand: All direct and indirect callers

find_dependencies("target_function", max_depth=2)
# → Understand: What it relies on

# Phase 2: Check for string references (1 minute)
search_code("target_function string literal config")
# → Understand: Non-code references (config, logs, docs)

# Phase 3: Find similar patterns (1 minute)
search_code("similar function pattern usage")
# → Understand: Consistency requirements

# Phase 4: Verify test coverage (1 minute)
search_code("test target_function")
# → Understand: What tests exist

find_callers("target_function")  # Filter by test files
# → Understand: How it's tested

# SYNTHESIS:
# - Direct callers: [list with files/lines]
# - Indirect callers: [list]
# - String references: [locations]
# - Tests affected: [list]
# - Safe to rename: YES/NO
# - If YES: [list of files to update]

# Mental model: COMPLETE IMPACT MAP ✅
# Time: 5 minutes
# Cognitive load: Low
# Risk: Minimal (all usages identified)
```

**Compare to grep+read:** Would take 20-30 minutes, higher risk of missing usages

---

### Workflow 4: Architecture Discovery

**Goal:** Understand system design from code

```python
# Phase 1: Find entry points (2 minutes)
search_code("main entry point initialization")
search_ast("function_definition")  # In __main__.py or main module
# → Understand: How system starts

# Phase 2: Map major components (3 minutes)
find_dependencies("main", max_depth=2)
# → Understand: Top-level component initialization

search_ast("class_definition")
# → Understand: Major classes (review names)

# Phase 3: Understand data flow (3 minutes)
find_call_paths("entry", "data_processing")
find_call_paths("data_processing", "output")
# → Understand: Data pipeline

# Phase 4: Identify patterns (2 minutes)
search_code("factory pattern")
search_code("singleton pattern")
search_code("dependency injection")
# → Understand: Design patterns in use

# Phase 5: Map error handling (2 minutes)
search_ast("try_statement")
search_code("error handling strategy")
# → Understand: Error management approach

# SYNTHESIS:
# - Architecture: [3-tier/MVC/microservices/etc]
# - Entry points: [list]
# - Major components: [list with responsibilities]
# - Data flow: [diagram in mind]
# - Design patterns: [list]
# - Error strategy: [approach]

# Mental model: COMPLETE ARCHITECTURE ✅
# Time: 12 minutes
# Cognitive load: Medium (synthesis required)
```

**Compare to grep+read:** Would take 2-3 hours, incomplete understanding

---

## 🎓 Synthesis Guidance: Building Mental Models

After running queries, how do you know you have "enough" understanding?

### Synthesis Checklist

**After running exploration queries, ask yourself:**

- [ ] **Can I draw the call graph from memory?**
  - If NO → Run more `find_callers`/`find_dependencies` queries

- [ ] **Do I understand why each component exists?**
  - If NO → Run `search_standards` for design rationale

- [ ] **Can I predict what happens if I change X?**
  - If NO → Run `find_callers` to see impact

- [ ] **Have I found unexpected patterns or inconsistencies?**
  - If NO → Run `search_code` for similar patterns across codebase

- [ ] **Can I explain this to someone else clearly?**
  - If NO → Run `find_call_paths` to trace full flows

- [ ] **Do I know where to make the change?**
  - If NO → Run `search_ast` to find all instances of pattern

**If YES to all:** Understanding is complete ✅

**If NO to any:** Query more specific areas 🔍

---

### Progressive Refinement Strategy

**Start broad → narrow based on results → verify understanding**

```python
# Round 1: Broad discovery
search_code("general concept")
# → Result: Found 5 relevant files

# Round 2: Narrow to specific file
search_code("specific implementation details")  # Filter by file from Round 1
# → Result: Found 2 key functions

# Round 3: Map relationships
find_callers("key_function_from_round_2")
find_dependencies("key_function_from_round_2")
# → Result: Complete relationship map

# Round 4: Verify understanding
find_call_paths("entry", "key_function")
# → Result: Confirmed execution flow

# Round 5: Check for edge cases
search_ast("try_statement")  # In the files you care about
# → Result: Found error handling approach

# SYNTHESIS: Understanding complete ✅
```

---

### Breadth-First vs Depth-First Exploration

**Breadth-First (Recommended for new codebases):**
```python
# Get high-level view of everything first
search_standards("system overview")
search_code("main components initialization")
find_dependencies("main", max_depth=1)  # Only immediate deps

# Then drill into each component
search_code("component A details")
find_callers("component_a_method")

search_code("component B details")
find_callers("component_b_method")

# Mental model: Balanced, complete overview
```

**Depth-First (Recommended for specific bugs/features):**
```python
# Follow one path completely
search_code("specific feature entry point")
find_call_paths("entry", "deep_function")
find_dependencies("deep_function", max_depth=5)

# Then explore related areas
search_code("similar patterns to deep_function")
find_callers("related_function")

# Mental model: Deep understanding of one path
```

---

## 🎯 Updated Decision Tree

```
START: What do you want to accomplish?

├─ Building Understanding? (Discovery Phase)
│  ├─ Learn system/feature? → search_standards("how does X work")
│  ├─ Find similar code? → search_code("pattern description")
│  ├─ Understand relationships? → find_callers + find_dependencies
│  └─ Trace execution flow? → find_call_paths
│
├─ Finding Exact Match? (Verification Phase)
│  ├─ Know exact symbol? → grep "exact_text"
│  ├─ Check existence? → grep "import|def|class Name"
│  └─ Find string literal? → grep "error message"
│
├─ Reading Full Context? (Implementation Phase)
│  ├─ Know exact file? → read_file("path/file.py")
│  ├─ Need complete structure? → read_file (after discovery)
│  └─ Implementing changes? → read_file target + tests
│
└─ Systematic Exploration? (Reasoning Phase)
   ├─ New subsystem? → Use "Workflow 1" above
   ├─ Tracing bug? → Use "Workflow 2" above
   ├─ Refactoring? → Use "Workflow 3" above
   └─ Understanding architecture? → Use "Workflow 4" above
```

---

## 📚 The Six Actions Explained

### Action 1: search_standards - Documentation Search

**What it does:** Searches standards documentation using hybrid search (vector similarity + full-text + reciprocal rank fusion + reranking).

**When to use:**
- Finding "how to" documentation
- Learning project patterns
- Understanding workflows
- Discovering tool usage

**Parameters:**
- `query` (str): Natural language question or keywords
- `n_results` (int): Max results (default: 5)
- `filters` (dict): Optional filters (domain, phase, tags)

**Examples:**

```python
# Find documentation
pos_search_project(
    action="search_standards",
    query="how to create standards",
    n_results=5
)

# Find specific domain
pos_search_project(
    action="search_standards",
    query="testing patterns",
    n_results=3,
    filters={"domain": "development"}
)

# Find workflow guidance
pos_search_project(
    action="search_standards",
    query="spec execution workflow phases",
    n_results=5
)
```

**Returns:**
```json
{
  "status": "success",
  "action": "search_standards",
  "results": [
    {
      "content": "# Standards Creation Process\n...",
      "file_path": "standards/universal/ai-assistant/standards-creation-process.md",
      "relevance_score": 0.85,
      "section": "TL;DR",
      "metadata": {"domain": "universal", "phase": 0}
    }
  ],
  "count": 5
}
```

---

### Action 2: search_code - Semantic Code Search

**What it does:** Searches code by meaning using CodeBERT embeddings. Finds semantically similar code even with different variable names or syntax.

**When to use:**
- Finding code that does something conceptually
- Discovering similar implementations
- Finding examples of patterns
- Understanding "how X works here"

**Parameters:**
- `query` (str): Natural language description or concept
- `n_results` (int): Max results (default: 5)
- `filters` (dict): Optional filters (language, file_path)

**Examples:**

```python
# Find error handling code
pos_search_project(
    action="search_code",
    query="error handling exception catching",
    n_results=5
)

# Find graph traversal logic
pos_search_project(
    action="search_code",
    query="recursive graph traversal DFS BFS",
    n_results=3
)

# Find database queries
pos_search_project(
    action="search_code",
    query="DuckDB SQL query execution",
    n_results=5,
    filters={"language": "python"}
)

# Find initialization patterns
pos_search_project(
    action="search_code",
    query="initialize schema create tables indexes",
    n_results=3
)
```

**Returns:**
```json
{
  "status": "success",
  "action": "search_code",
  "results": [
    {
      "content": "def _extract_relationships(...):\n    \"\"\"Extract call graph relationships...\"\"\"\n    ...",
      "file_path": "ouroboros/subsystems/rag/code/graph/ast.py",
      "relevance_score": 0.78,
      "line_range": [280, 367],
      "metadata": {"language": "python"}
    }
  ],
  "count": 5
}
```

**Pro Tips:**
- Use technical terms (not "do something" but "execute query")
- Combine concepts ("authentication + JWT + validation")
- Include library names ("tree-sitter parser" or "LanceDB connection")

---

### Action 3: search_ast - Structural Code Search

**What it does:** Searches code by syntax structure using tree-sitter AST (Abstract Syntax Tree). Finds code by what it IS, not what it DOES.

**When to use:**
- Finding specific language constructs
- Locating all functions/classes/loops
- Finding error handlers (try/except)
- Discovering conditionals or imports
- Syntax-level code analysis

**Parameters:**
- `query` (str): Tree-sitter node type or pattern
- `n_results` (int): Max results (default: 5)
- `filters` (dict): Optional filters (language, file_path, node_type)

**Critical: Use Tree-sitter Node Types**

AST search requires **exact tree-sitter node type names**, not natural language.

**Python Node Types:**

| Construct | Node Type | Query |
|-----------|-----------|-------|
| Functions | `function_definition` | `"function_definition"` |
| Async functions | `async_function_definition` | `"async_function_definition"` |
| Classes | `class_definition` | `"class_definition"` |
| If statements | `if_statement` | `"if_statement"` |
| For loops | `for_statement` | `"for_statement"` |
| While loops | `while_statement` | `"while_statement"` |
| Try/except | `try_statement` | `"try_statement"` |
| Imports | `import_statement`, `import_from_statement` | `"import_from_statement"` |
| With blocks | `with_statement` | `"with_statement"` |
| Lambda | `lambda` | `"lambda"` |

**Examples:**

```python
# Find all function definitions
pos_search_project(
    action="search_ast",
    query="function_definition",
    n_results=10
)

# Find all class definitions
pos_search_project(
    action="search_ast",
    query="class_definition",
    n_results=5
)

# Find error handling blocks
pos_search_project(
    action="search_ast",
    query="try_statement",
    n_results=10
)

# Find conditionals
pos_search_project(
    action="search_ast",
    query="if_statement",
    n_results=10
)

# Find async functions only
pos_search_project(
    action="search_ast",
    query="async_function_definition",
    n_results=5
)

# Find with context managers
pos_search_project(
    action="search_ast",
    query="with_statement",
    n_results=5
)
```

**Returns:**
```json
{
  "status": "success",
  "action": "search_ast",
  "results": [
    {
      "file_path": "ouroboros/__main__.py",
      "language": "python",
      "node_type": "function_definition",
      "symbol_name": null,
      "start_line": 37,
      "end_line": 94,
      "content": "function_definition  (lines 37-94)"
    }
  ],
  "count": 10
}
```

**Common Mistakes:**

❌ **DON'T use natural language:**
```python
# Wrong
search_ast(query="find all functions")
search_ast(query="error handlers")
search_ast(query="loops")
```

✅ **DO use node types:**
```python
# Correct
search_ast(query="function_definition")
search_ast(query="try_statement")
search_ast(query="for_statement")
```

---

### Action 4: find_callers - Reverse Lookup

**What it does:** Finds all functions that call a given symbol. Uses recursive graph traversal to find direct and indirect callers.

**When to use:**
- Understanding function impact ("who uses this?")
- Tracing code dependencies backwards
- Refactoring impact analysis
- Understanding call hierarchy

**Parameters:**
- `query` (str): Symbol name (function or class name)
- `max_depth` (int): Maximum traversal depth (default: 10)

**Examples:**

```python
# Find who calls route_action
pos_search_project(
    action="find_callers",
    query="route_action",
    max_depth=2
)

# Find who calls build method
pos_search_project(
    action="find_callers",
    query="build",
    max_depth=3
)

# Find who calls a specific class
pos_search_project(
    action="find_callers",
    query="GraphIndex",
    max_depth=2
)
```

**Returns:**
```json
{
  "status": "success",
  "action": "find_callers",
  "results": [
    {
      "caller_id": 160,
      "caller_name": "_handle_search_standards",
      "caller_type": "function",
      "caller_file": "ouroboros/tools/pos_search_project.py",
      "caller_line": 169,
      "target_id": 357,
      "target_name": "route_action",
      "depth": 1,
      "path": "_handle_search_standards"
    },
    {
      "caller_id": 161,
      "caller_name": "_handle_search_code",
      "caller_type": "function",
      "caller_file": "ouroboros/tools/pos_search_project.py",
      "caller_line": 178,
      "target_id": 357,
      "target_name": "route_action",
      "depth": 1,
      "path": "_handle_search_code"
    }
  ],
  "count": 6
}
```

**Understanding Results:**
- `depth=1`: Direct caller
- `depth=2`: Caller of caller (indirect)
- `path`: Call chain showing how we reached this caller

---

### Action 5: find_dependencies - Forward Lookup

**What it does:** Finds all functions that a given symbol calls. Uses recursive graph traversal to find direct and indirect dependencies.

**When to use:**
- Understanding what a function does internally
- Tracing code dependencies forward
- Impact analysis for changes
- Understanding call chains

**Parameters:**
- `query` (str): Symbol name (function or class name)
- `max_depth` (int): Maximum traversal depth (default: 10)

**Examples:**

```python
# Find what route_action calls
pos_search_project(
    action="find_dependencies",
    query="route_action",
    max_depth=2
)

# Find what build calls
pos_search_project(
    action="find_dependencies",
    query="build",
    max_depth=3
)

# Find dependencies of initialization
pos_search_project(
    action="find_dependencies",
    query="__init__",
    max_depth=1
)
```

**Returns:**
```json
{
  "status": "success",
  "action": "find_dependencies",
  "results": [
    {
      "dep_id": 257,
      "dep_name": "ActionableError",
      "dep_type": "class",
      "dep_file": "ouroboros/utils/errors.py",
      "dep_line": 39,
      "source_id": 357,
      "source_name": "route_action",
      "depth": 1,
      "path": "ActionableError"
    },
    {
      "dep_id": 260,
      "dep_name": "IndexError",
      "dep_type": "class",
      "dep_file": "ouroboros/utils/errors.py",
      "dep_line": 237,
      "source_id": 357,
      "source_name": "route_action",
      "depth": 1,
      "path": "IndexError"
    }
  ],
  "count": 8
}
```

**Understanding Results:**
- `depth=1`: Direct dependency (calls directly)
- `depth=2`: Transitive dependency (calls something that calls this)
- `path`: Call chain showing dependency flow

---

### Action 6: find_call_paths - Path Finding

**What it does:** Finds all call paths from one symbol to another. Shows how function A can reach function B through intermediate calls.

**When to use:**
- Understanding execution flow
- Tracing how code reaches a specific function
- Debugging call chains
- Understanding system architecture

**Parameters:**
- `query` (str): Starting symbol name
- `to_symbol` (str): Target symbol name
- `max_depth` (int): Maximum path length (default: 10)

**Examples:**

```python
# Find how _handle_search_code reaches route_action
pos_search_project(
    action="find_call_paths",
    query="_handle_search_code",
    to_symbol="route_action",
    max_depth=3
)

# Find how main reaches database operations
pos_search_project(
    action="find_call_paths",
    query="main",
    to_symbol="execute",
    max_depth=5
)

# Find initialization path
pos_search_project(
    action="find_call_paths",
    query="create_server",
    to_symbol="ensure_all_indexes_healthy",
    max_depth=3
)
```

**Returns:**
```json
{
  "status": "success",
  "action": "find_call_paths",
  "results": [
    ["_handle_search_code", "route_action"],
    ["_handle_search_code", "index_manager.route_action", "route_action"]
  ],
  "count": 2
}
```

**Understanding Results:**
- Each result is an array representing one path
- Paths show intermediate function calls
- Multiple paths indicate different routes to same destination

---

## 🚀 Multi-Repo Code Intelligence - Searching Across Repositories

**New Feature:** pos_search_project now supports **multi-repo search** - search across multiple local repositories simultaneously using a partition-based architecture.

### What Are Partitions?

**Partitions** = Independent code repositories indexed separately but searchable together.

**Example Setup:**
```
praxis-os/               # Partition 1: "praxis-os"
├── .praxis-os/
│   └── ouroboros/      # Framework code
│
python-sdk/              # Partition 2: "python-sdk"
└── src/
    └── honeyhive/      # SDK code
```

**Both repositories** are indexed and searchable through a single unified interface.

---

### How to Search Across Repositories

**Pattern 1: Search ALL Partitions (Default)**

```python
# Searches BOTH praxis-os AND python-sdk
pos_search_project(
    action="search_code",
    query="tracer initialization setup",
    n_results=10
)
# Returns: Results from BOTH repositories, ranked by relevance
```

**When to use:** Discovery phase - finding concepts across entire codebase.

---

**Pattern 2: Search SPECIFIC Partition**

```python
# Search ONLY the python-sdk partition
pos_search_project(
    action="search_code",
    query="HoneyHiveTracer initialization",
    n_results=5,
    filters={"partition": "python-sdk"}
)
# Returns: Results ONLY from python-sdk repository
```

**When to use:** Focused search - you know which repo has the code.

---

### Multi-Repo Search for All Actions

**All 6 actions** support multi-repo search with partition filtering:

#### 1. Standards Search (Single Repo Only)
```python
# Standards are always in praxis-os (no multi-repo)
pos_search_project(
    action="search_standards",
    query="dogfooding model development"
)
```

#### 2. Semantic Code Search (Multi-Repo)
```python
# Search all repos
pos_search_project(
    action="search_code",
    query="async HTTP client requests",
    n_results=10
)

# Search specific repo
pos_search_project(
    action="search_code",
    query="async HTTP client requests",
    n_results=10,
    filters={"partition": "python-sdk"}
)
```

#### 3. AST Search (Multi-Repo)
```python
# Find all async functions in python-sdk
pos_search_project(
    action="search_ast",
    query="async_function_definition",
    n_results=10,
    filters={"partition": "python-sdk"}
)

# Find all classes across all repos
pos_search_project(
    action="search_ast",
    query="class_definition",
    n_results=20
)
```

#### 4. Find Callers (Single Partition)
```python
# MUST specify partition for call graph operations
pos_search_project(
    action="find_callers",
    query="HoneyHiveTracer.__init__",
    max_depth=2,
    filters={"partition": "python-sdk"}
)
```

**⚠️ Important:** Call graph actions (`find_callers`, `find_dependencies`, `find_call_paths`) **require partition specification** because call graphs don't cross repository boundaries.

#### 5. Find Dependencies (Single Partition)
```python
# Find what HoneyHiveTracer.__init__ calls
pos_search_project(
    action="find_dependencies",
    query="HoneyHiveTracer.__init__",
    max_depth=2,
    filters={"partition": "python-sdk"}
)
```

#### 6. Find Call Paths (Single Partition)
```python
# Trace initialization path in python-sdk
pos_search_project(
    action="find_call_paths",
    query="HoneyHiveTracer.__init__",
    to_symbol="configure",
    max_depth=5,
    filters={"partition": "python-sdk"}
)
```

---

### Multi-Repo Workflow Patterns

#### Pattern 1: Cross-Repo Discovery

**Goal:** Find similar implementations across multiple projects.

```python
# Phase 1: Search all repos for concept
pos_search_project(
    action="search_code",
    query="rate limiting throttling requests",
    n_results=10
)
# → Returns: Results from praxis-os AND python-sdk

# Phase 2: Compare implementations
# Review results, note differences in approach

# Phase 3: Deep dive on specific implementation
pos_search_project(
    action="search_ast",
    query="function_definition",
    n_results=10,
    filters={"partition": "python-sdk"}
)
# → Find specific functions in python-sdk
```

**Use Case:** Understanding how different projects solve the same problem.

---

#### Pattern 2: SDK Integration Analysis

**Goal:** Understand how SDK integrates with framework.

```python
# Step 1: Find SDK's public API
pos_search_project(
    action="search_ast",
    query="class_definition",
    n_results=10,
    filters={"partition": "python-sdk"}
)
# → Identify: HoneyHiveTracer, Client, Configuration, etc.

# Step 2: Find tracer initialization
pos_search_project(
    action="search_code",
    query="HoneyHiveTracer initialization setup",
    n_results=5,
    filters={"partition": "python-sdk"}
)
# → Understand: How tracer is set up

# Step 3: Map tracer dependencies
pos_search_project(
    action="find_dependencies",
    query="HoneyHiveTracer.__init__",
    max_depth=2,
    filters={"partition": "python-sdk"}
)
# → Understand: What tracer depends on

# Step 4: Find who uses tracer
pos_search_project(
    action="find_callers",
    query="HoneyHiveTracer.__init__",
    max_depth=2,
    filters={"partition": "python-sdk"}
)
# → Understand: How tracer is instantiated

# Step 5: Search framework for integration patterns
pos_search_project(
    action="search_code",
    query="SDK integration tracer setup patterns",
    n_results=5,
    filters={"partition": "praxis-os"}
)
# → Understand: How framework integrates SDKs
```

**Use Case:** Learning SDK architecture and integration points.

---

#### Pattern 3: Bug Tracing Across Repos

**Goal:** Trace a bug from SDK to framework (or vice versa).

```python
# Step 1: Find error in SDK
pos_search_project(
    action="search_code",
    query="error message text from logs",
    n_results=5,
    filters={"partition": "python-sdk"}
)
# → Found: Where error originates

# Step 2: Map SDK call stack
pos_search_project(
    action="find_callers",
    query="function_that_errors",
    max_depth=3,
    filters={"partition": "python-sdk"}
)
# → Understand: SDK-internal call chain

# Step 3: Search framework for SDK usage
pos_search_project(
    action="search_code",
    query="python-sdk HoneyHive integration",
    n_results=10,
    filters={"partition": "praxis-os"}
)
# → Understand: How framework calls SDK

# Step 4: Trace framework side
pos_search_project(
    action="find_call_paths",
    query="sdk_entry_point",
    to_symbol="function_that_errors",
    max_depth=5,
    filters={"partition": "praxis-os"}
)
# → Understand: Full execution path
```

**Use Case:** Debugging issues that span multiple repositories.

---

#### Pattern 4: Architecture Comparison

**Goal:** Compare architectural patterns between projects.

```python
# Find error handling in praxis-os
pos_search_project(
    action="search_ast",
    query="try_statement",
    n_results=20,
    filters={"partition": "praxis-os"}
)
# → Found: 127 try statements in praxis-os

# Find error handling in python-sdk
pos_search_project(
    action="search_ast",
    query="try_statement",
    n_results=20,
    filters={"partition": "python-sdk"}
)
# → Found: 43 try statements in python-sdk

# Compare error patterns semantically
pos_search_project(
    action="search_code",
    query="exception handling error recovery retry",
    n_results=10
)
# → Returns: Both repos, compare approaches
```

**Use Case:** Learning different architectural approaches, identifying best practices.

---

### Multi-Repo Best Practices

#### ✅ DO:

1. **Start broad, then narrow**
   ```python
   # First: Search all repos
   search_code("authentication patterns")
   
   # Then: Focus on specific repo
   search_code("authentication patterns", filters={"partition": "python-sdk"})
   ```

2. **Use partition filters for call graph operations**
   ```python
   # ALWAYS specify partition for call graphs
   find_callers("symbol_name", filters={"partition": "python-sdk"})
   ```

3. **Search semantically across repos for discovery**
   ```python
   # Good: Find concepts everywhere
   search_code("rate limiting implementation")
   ```

4. **Use AST search to compare structures**
   ```python
   # Compare: How many classes in each repo?
   search_ast("class_definition", filters={"partition": "praxis-os"})
   search_ast("class_definition", filters={"partition": "python-sdk"})
   ```

#### ❌ DON'T:

1. **Don't forget partition filter for call graphs**
   ```python
   # ❌ Wrong: Will fail without partition
   find_callers("HoneyHiveTracer.__init__")
   
   # ✅ Correct: Specify partition
   find_callers("HoneyHiveTracer.__init__", filters={"partition": "python-sdk"})
   ```

2. **Don't assume results are from one repo**
   ```python
   # Be aware: Results may mix repos
   search_code("HTTP client")
   # → Check result metadata to see which partition it's from
   ```

3. **Don't search across repos for repo-specific symbols**
   ```python
   # ❌ Inefficient: Searching all repos for SDK-specific class
   search_code("HoneyHiveTracer initialization")
   
   # ✅ Better: Target the right repo
   search_code("HoneyHiveTracer initialization", filters={"partition": "python-sdk"})
   ```

---

### Understanding Multi-Repo Results

**Result Metadata Includes Partition Information:**

```json
{
  "status": "success",
  "action": "search_code",
  "results": [
    {
      "content": "class HoneyHiveTracer:\n    def __init__(...)...",
      "file_path": "src/honeyhive/tracer.py",
      "relevance_score": 0.82,
      "metadata": {
        "language": "python",
        "partition": "python-sdk",      // <-- Partition metadata
        "repo_name": "python-sdk"       // <-- Repository name
      }
    },
    {
      "content": "class Tracer:\n    def __init__(...)...",
      "file_path": "ouroboros/observability/tracer.py",
      "relevance_score": 0.75,
      "metadata": {
        "language": "python",
        "partition": "praxis-os",       // <-- Different partition
        "repo_name": "praxis-os"
      }
    }
  ]
}
```

**Use `_partition` or `partition` in metadata to identify source repository.**

---

### Multi-Repo Configuration

**Partition configuration is defined in `.praxis-os/config/mcp.yaml`:**

```yaml
indexes:
  code:
    enabled: true
    partitions:
      praxis-os:                        # Partition name
        path: .                         # Relative to config file
        domains:
          code:
            include_paths: [ouroboros/, scripts/]
            
      python-sdk:                       # Another partition
        path: ../../python-sdk          # Relative to config file
        domains:
          code:
            include_paths: [src/]       # Index only src/ directory
            metadata:
              project: python-sdk
              type: library
```

**Key Points:**
- Each partition has a unique name (`praxis-os`, `python-sdk`)
- `path` is relative to the config file location
- `include_paths` specifies which directories to index (e.g., `src/` only, not `venv/`)
- Metadata is optional but useful for filtering

---

### When to Use Multi-Repo Search

#### ✅ Use Multi-Repo When:

- **Learning across projects** - "How do different projects handle authentication?"
- **Finding patterns** - "Where is rate limiting implemented?"
- **Cross-repo discovery** - "What repos have async HTTP clients?"
- **Architecture comparison** - "Compare error handling across SDKs"
- **Integration understanding** - "How does SDK integrate with framework?"

#### ✅ Use Single-Repo (Partition Filter) When:

- **Focused implementation** - "How does `python-sdk` handle retries?"
- **Call graph analysis** - "Who calls this SDK function?"
- **Repo-specific features** - "Find all tracer implementations in SDK"
- **Performance** - Faster to search one repo when you know where it is

---

### Multi-Repo Search Performance

| Operation | Single Repo | Multi-Repo (2 partitions) | Multi-Repo (5 partitions) |
|-----------|-------------|---------------------------|---------------------------|
| `search_code` | 200-400ms | 400-800ms | 1-2s |
| `search_ast` | 50-150ms | 100-300ms | 250-750ms |
| `find_callers` | 50-200ms | N/A (single partition only) | N/A |
| `find_dependencies` | 50-200ms | N/A (single partition only) | N/A |
| `find_call_paths` | 100-400ms | N/A (single partition only) | N/A |

**Key Insights:**
- Multi-repo semantic search scales linearly with partition count
- AST search is fast even across multiple repos
- Call graph operations are always single-partition (fast)

---

### Multi-Repo Query Examples

```python
# Example 1: Find async patterns across all repos
pos_search_project(
    action="search_code",
    query="async await asyncio patterns",
    n_results=15
)
# → Returns: Async code from ALL repos, ranked by relevance

# Example 2: Find all classes in python-sdk
pos_search_project(
    action="search_ast",
    query="class_definition",
    n_results=20,
    filters={"partition": "python-sdk"}
)
# → Returns: All classes ONLY in python-sdk

# Example 3: Trace SDK initialization
pos_search_project(
    action="find_dependencies",
    query="HoneyHiveTracer.__init__",
    max_depth=3,
    filters={"partition": "python-sdk"}
)
# → Returns: What __init__ calls (SDK-internal only)

# Example 4: Compare error handling
search_code("exception handling retry backoff", n_results=10)
# → Returns: Error handling from BOTH repos

# Example 5: Find SDK usage in framework
pos_search_project(
    action="search_code",
    query="HoneyHiveTracer integration setup usage",
    n_results=5,
    filters={"partition": "praxis-os"}
)
# → Returns: How praxis-os uses the SDK
```

---

### Multi-Repo Troubleshooting

**Problem:** "No results when searching specific repo"

```python
# Check if partition exists
pos_search_project(
    action="search_code",
    query="test",  # Generic query
    n_results=1,
    filters={"partition": "python-sdk"}
)
# If returns 0 results, partition might not be indexed
```

**Problem:** "Call graph search fails"

```python
# ❌ Error: "Partition not specified"
find_callers("my_function")

# ✅ Fix: Add partition filter
find_callers("my_function", filters={"partition": "praxis-os"})
```

**Problem:** "Results from wrong repo"

```python
# Always check result metadata
result = search_code("my_function")
print(result["results"][0]["metadata"]["partition"])  # Which repo?
```

---

## 🎯 Decision Tree: Which Action to Use?

```
START: What do you want to find?

├─ Documentation / Standards?
│  └─ Use: search_standards
│     └─ Query: Natural language ("how to create standards")
│
├─ Code by what it DOES (meaning)?
│  └─ Use: search_code
│     └─ Query: Conceptual description ("error handling patterns")
│
├─ Code by what it IS (structure)?
│  └─ Use: search_ast
│     └─ Query: Node type ("function_definition", "try_statement")
│
├─ Who calls this function?
│  └─ Use: find_callers
│     └─ Query: Symbol name ("route_action")
│
├─ What does this function call?
│  └─ Use: find_dependencies
│     └─ Query: Symbol name ("build")
│
└─ How does A reach B?
   └─ Use: find_call_paths
      └─ Query: from="A", to_symbol="B"
```

---

## 💡 Best Practices

### 1. Semantic Search (search_code)

**✅ Good Queries:**
- Use technical terms: "tree-sitter parser initialization"
- Combine concepts: "DuckDB recursive CTE graph traversal"
- Include library names: "LanceDB connection management"
- Be specific: "two-pass extraction symbol relationships"

**❌ Bad Queries:**
- Too vague: "code"
- Too generic: "function"
- Non-technical: "the thing that does stuff"

### 2. AST Search (search_ast)

**✅ Good Queries:**
- Exact node types: `"function_definition"`
- Language constructs: `"try_statement"`, `"if_statement"`
- Async variants: `"async_function_definition"`

**❌ Bad Queries:**
- Natural language: "find all functions"
- Generic terms: "conditionals"
- Multiple patterns: "functions and classes" (search twice instead)

### 3. Call Graph (find_callers, find_dependencies, find_call_paths)

**✅ Good Queries:**
- Exact symbol names: `"route_action"`, `"GraphIndex"`
- Public methods: `"build"`, `"search"`, `"health_check"`
- Well-known functions: `"create_server"`, `"main"`

**❌ Bad Queries:**
- Partial names: `"route"` (use full name)
- Generic names: `"get"` (too many results)
- Private methods without context: `"_helper"` (many matches)

### 4. Iterate and Refine

Start broad, then narrow:

```python
# Step 1: Find general area
search_code(query="graph traversal implementation")

# Step 2: Find specific structure
search_ast(query="function_definition")  # in the files you found

# Step 3: Understand dependencies
find_dependencies(query="traverse_graph")  # function you identified

# Step 4: Trace impact
find_callers(query="traverse_graph")
```

---

## ⚠️ Common Mistakes and Anti-Patterns

### Mistake 1: Using Natural Language for AST Search

**❌ Wrong:**
```python
search_ast(query="find all error handlers")
```

**✅ Correct:**
```python
search_ast(query="try_statement")
```

**Why:** AST search requires exact tree-sitter node type names.

---

### Mistake 2: Using search_code When You Want Exact Structure

**❌ Wrong:**
```python
search_code(query="all class definitions in the codebase")
```

**✅ Correct:**
```python
search_ast(query="class_definition")
```

**Why:** Semantic search finds meaning; AST search finds syntax.

---

### Mistake 3: Searching for Undefined Symbols

**❌ Wrong:**
```python
find_callers(query="my_new_function")  # Function doesn't exist yet
# Returns: {"results": [], "count": 0}
```

**✅ Correct:**
First verify symbol exists:
```python
search_code(query="my_new_function")  # Check if it exists
# Then use find_callers if found
```

---

### Mistake 4: Not Using Filters

**❌ Wrong:**
```python
search_code(query="test")  # Returns tests + code with "test" in name
```

**✅ Correct:**
```python
search_code(query="authentication logic", filters={"language": "python"})
```

---

### Mistake 5: Setting max_depth Too Low

**❌ Wrong:**
```python
find_call_paths(query="main", to_symbol="database_query", max_depth=1)
# Returns: [] because path is longer than 1
```

**✅ Correct:**
```python
find_call_paths(query="main", to_symbol="database_query", max_depth=5)
```

---

## 📊 Real-World Examples

### Example 1: Understanding How a Feature Works

**Goal:** Understand how AST extraction works in the code index.

```python
# Step 1: Find the relevant code
search_code(
    query="AST extraction tree-sitter parsing",
    n_results=5
)
# → Found: ast.py with extraction logic

# Step 2: Find who uses this
find_callers(query="_extract_ast_nodes", max_depth=2)
# → Found: GraphIndex calls it during build

# Step 3: Find what it depends on
find_dependencies(query="_extract_ast_nodes", max_depth=2)
# → Found: tree-sitter Parser, language detection

# Step 4: Find the full call path
find_call_paths(
    query="build",
    to_symbol="_extract_ast_nodes",
    max_depth=5
)
# → Path: build → _extract_all_data → _extract_ast_nodes
```

---

### Example 2: Refactoring Impact Analysis

**Goal:** Rename `route_action` and find all affected code.

```python
# Step 1: Find all callers
find_callers(query="route_action", max_depth=3)
# → Found: 6 callers in pos_search_project.py

# Step 2: Find all dependencies (what it calls)
find_dependencies(query="route_action", max_depth=2)
# → Found: ActionableError, IndexError, search methods

# Step 3: Search for string references (not in call graph)
search_code(query="route_action string literal")
# → Check for config/logging references
```

**Conclusion:** Safe to rename - all usages identified.

---

### Example 3: Finding All Error Handling

**Goal:** Audit error handling patterns in the codebase.

```python
# Step 1: Find all try/except blocks
search_ast(query="try_statement", n_results=50)
# → Found: 222 try statements

# Step 2: Find error handler functions semantically
search_code(query="exception handling error catching", n_results=10)
# → Found: Error handling utilities

# Step 3: Find all ActionableError usage
search_code(query="ActionableError raise exception")
# → Found: 35 instances
```

---

### Example 4: Tracing Server Startup

**Goal:** Understand server initialization flow.

```python
# Step 1: Find entry point
search_ast(query="function_definition")
# Filter results for "main" or "create_server"

# Step 2: Trace initialization
find_dependencies(query="create_server", max_depth=3)
# → Found: IndexManager init, ensure_all_indexes_healthy, etc.

# Step 3: Find specific path to index building
find_call_paths(
    query="create_server",
    to_symbol="ensure_all_indexes_healthy",
    max_depth=5
)
# → Path: create_server → IndexManager.__init__ → ensure_all_indexes_healthy
```

---

## 🧪 Testing Your Queries

### Test 1: Verify Action Works

```python
# Should return results
pos_search_project(action="search_ast", query="function_definition", n_results=3)
```

**Expected:** 3 function definitions with file paths and line numbers.

---

### Test 2: Verify Semantic Search

```python
# Should find conceptually related code
pos_search_project(action="search_code", query="graph traversal recursive", n_results=3)
```

**Expected:** Code about graph traversal (even if it doesn't use those exact words).

---

### Test 3: Verify Call Graph

```python
# Should find callers
pos_search_project(action="find_callers", query="route_action", max_depth=2)
```

**Expected:** List of functions that call `route_action`.

---

## 🔗 Related Standards

**Query workflow for code search:**

1. **Understanding search types** → This document
2. **RAG query patterns** → `pos_search(content_type="standards", query="query construction patterns")`
3. **Tree-sitter node types** → `pos_search(content_type="standards", query="tree-sitter AST node types")`
4. **Code intelligence** → `pos_search(content_type="standards", query="code analysis call graph")`

**By Category:**

**Code Search:**
- This document → `pos_search(content_type="standards", query="pos_search_project usage")`
- Query patterns → `pos_search(content_type="standards", query="query construction patterns")`

**Tool Usage:**
- MCP tool discovery → `pos_search(content_type="standards", query="MCP tool discovery")`
- RAG content authoring → `pos_search(content_type="standards", query="RAG content authoring")`

---

## 📝 Quick Cheat Sheet

| Task | Action | Query Format | Example |
|------|--------|--------------|---------|
| **Find docs** | `search_standards` | Natural language | "how to create standards" |
| **Find code meaning** | `search_code` | Conceptual description | "error handling patterns" |
| **Find code structure** | `search_ast` | Node type | "function_definition" |
| **Find callers** | `find_callers` | Symbol name | "route_action" |
| **Find dependencies** | `find_dependencies` | Symbol name | "build" |
| **Find paths** | `find_call_paths` | from + to symbols | "main" → "execute" |

---

## 🎓 Learning Path

1. **Start with search_standards** to learn the system
2. **Use search_code** to find examples
3. **Use search_ast** to find exact patterns
4. **Use find_callers** to understand impact
5. **Use find_dependencies** to trace execution
6. **Use find_call_paths** for complex analysis

**Practice:** Try all 6 actions with the same concept to see how they differ:
- `search_standards`: "graph traversal"
- `search_code`: "graph traversal DFS BFS"
- `search_ast`: "for_statement"
- `find_callers`: "traverse"
- `find_dependencies`: "traverse"
- `find_call_paths`: "main" → "traverse"

---

**END OF STANDARD**


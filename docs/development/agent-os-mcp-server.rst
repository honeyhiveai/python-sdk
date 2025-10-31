Agent OS MCP/RAG Server
=======================

.. note::
   **🤖 AI-Assisted Development Infrastructure**
   
   This is the infrastructure that powers AI-assisted development on the HoneyHive Python SDK. It's also a demonstration of dogfooding—using HoneyHive's own tracing to observe AI development workflows.

Overview
--------

The Agent OS MCP/RAG server is a Model Context Protocol (MCP) server that provides AI coding assistants (like Cursor) with intelligent access to our development standards, workflows, and architectural patterns.

**What Problem Does This Solve?**

Traditional AI coding assistants face three major challenges:

1. **Context Overload**: Reading entire 50KB standard files when they only need 5KB
2. **Workflow Violations**: Skipping critical phases (e.g., jumping to coding without planning)
3. **No Observability**: Can't trace what standards AI is actually using or how decisions are made

**Our Solution:**

- **90% Context Reduction**: RAG engine with semantic search (50KB → 5KB)
- **Phase Gating**: Workflow engine prevents AI from skipping steps
- **Full Observability**: HoneyHive tracing on all AI development operations

What is Agent OS?
-----------------

`Agent OS <https://buildermethods.com/agent-os>`_ is a spec-driven development methodology created by **Brian Casel (Builder Methods)**. It provides a structured approach to AI-assisted software development through three layers of context stored as markdown files:

**Layer 1: Standards (``~/.agent-os/standards/``)**
   Your tech stack, code style, and best practices that apply across all projects.

**Layer 2: Product (``.agent-os/product/``)**
   Mission, roadmap, architecture decisions, and product-specific context.

**Layer 3: Specs (``.agent-os/specs/YYYY-MM-DD-feature-name/``)**
   Individual feature specifications with requirements, technical design, and task breakdowns.

**Traditional Agent OS Approach:**

AI coding assistants (like Cursor, Claude Code) directly read these markdown files using tools like ``codebase_search``, ``read_file``, and ``grep`` to understand your development standards and execute workflows like:

- ``plan-product`` - Analyze product and create roadmap
- ``create-spec`` - Generate feature specifications  
- ``execute-tasks`` - Implement features following specs

**Learn More**: https://buildermethods.com/agent-os

Our Evolution: From Builder Methods to MCP/RAG
----------------------------------------------

Phase 1: Builder Methods Agent OS (Markdown Foundation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We started with `Agent OS <https://buildermethods.com/agent-os>`_ as created by Brian Casel, implementing the traditional approach:

**What We Adopted:**

- ✅ Three-layer context architecture (Standards, Product, Specs)
- ✅ Markdown-based documentation system
- ✅ Spec-driven development methodology
- ✅ Command-based workflows (``plan-product``, ``create-spec``, ``execute-tasks``)

**How It Worked:**

AI coding assistants directly read markdown files:

.. code-block:: text

   User: "What are our git safety rules?"
   
   AI: Uses codebase_search(".agent-os/standards/")
       Reads entire git-safety-rules.md (2,500 lines)
       Extracts relevant sections manually

**This foundation was excellent**, providing structure and consistency. However, as our codebase and standards grew, we discovered scaling challenges.

Phase 2: HoneyHive LLM Workflow Engineering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We extended Agent OS with our own **LLM Workflow Engineering methodology** (documented in ``.agent-os/standards/ai-assistant/LLM-WORKFLOW-ENGINEERING-METHODOLOGY.md``):

**Our Innovations:**

🔧 **Command Language Interface**
   Binding commands like ``🛑 EXECUTE-NOW``, ``📊 QUANTIFY-RESULTS``, ``🎯 NEXT-MANDATORY`` that create non-negotiable obligations for AI execution.

🏗️ **Three-Tier Architecture**
   - **Tier 1: Side-Loaded (≤100 lines)**: Automatic injection for systematic execution
   - **Tier 2: Active Read (200-500 lines)**: On-demand comprehensive context
   - **Tier 3: Output (Unlimited)**: Generated deliverables

🚨 **11 Automated Pre-Commit Hooks**
   Quality gates enforcing: formatting, linting, tests, documentation compliance, no-mock policy, etc.

📋 **Phase Gating with Evidence Requirements**
   Each workflow phase requires quantified evidence before progression (e.g., "test file created", "coverage ≥90%").

🎯 **Quality Targets**
   100% test pass rate + 90%+ coverage + 10.0/10 Pylint + 0 MyPy errors (non-negotiable).

**Example Workflow (V3 Test Generation):**

.. code-block:: markdown

   # Phase 1: Analysis
   🛑 EXECUTE-NOW: grep -n "^def\|^class" target_file.py
   📊 COUNT-AND-DOCUMENT: Functions and classes with signatures
   🎯 NEXT-MANDATORY: phases/2/dependency-analysis.md
   
   # Evidence Required:
   - Function count: <number>
   - Class count: <number>
   - Complexity assessment: <high/medium/low>

**Results:**

- ✅ 22% → 80%+ success rate (3.6x improvement)
- ✅ Systematic quality enforcement via automation
- ✅ Evidence-based validation preventing vague claims

**But New Challenges Emerged:**

❌ **Context Waste**
   AI reads 50KB files when only 5KB needed for current task.

❌ **No Programmatic Enforcement**
   Phase gating relies on AI compliance, can be skipped.

❌ **Zero Observability**
   No way to trace which standards AI consulted or how decisions were made.

❌ **Manual Discovery**
   AI must search for relevant standards each time.

Phase 3: MCP/RAG Innovation (This Implementation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We evolved our LLM Workflow Engineering approach by building an **MCP server with RAG**, transforming standards access from file-based to API-based:

**Builder Methods Foundation + Our Innovations + MCP/RAG = Complete Solution**

✅ **90% Context Reduction via RAG**
   Semantic search returns only relevant chunks (5KB vs 50KB), preserving Builder Methods' three-layer structure.

   .. code-block:: text
   
      User: "What are our git safety rules?"
      
      AI: Uses mcp_agent-os-rag_search_standards(
            query="git safety rules forbidden operations",
            n_results=5
          )
          
      Returns: 3 relevant chunks (840 tokens) instead of entire file (12,000 tokens)

✅ **Architectural Phase Gating**
   Workflow engine **programmatically enforces** our phase-gating methodology, making it impossible to skip steps.

   .. code-block:: python
   
      # Cannot advance to Phase 2 without Phase 1 evidence
      result = workflow_engine.complete_phase(
          session_id="abc-123",
          phase=1,
          evidence={
              "test_file_created": True,
              "framework_decision": "pytest"
          }
      )
      
      # Returns Phase 2 requirements ONLY if evidence validates

✅ **Full Observability (Dogfooding HoneyHive)**
   Every RAG query and workflow operation traced, demonstrating our own product in action.

✅ **Intelligent Filtering**
   Search by phase number, tags, or semantic meaning from Builder Methods' structured markdown.

✅ **Hot Reload**
   File watcher automatically rebuilds index when standards change.

**The Complete Evolution:**

.. list-table::
   :header-rows: 1
   :widths: 20 25 25 30

   * - Aspect
     - Builder Methods Agent OS
     - + LLM Workflow Engineering
     - + MCP/RAG Server
   * - **Foundation**
     - 3-layer context (Standards/Product/Specs)
     - Command language + Phase gating
     - Programmatic API access
   * - **Standards Access**
     - Direct file reading
     - Same (file-based)
     - Semantic search (90% reduction)
   * - **Workflow Enforcement**
     - Manual AI compliance
     - Evidence-based validation
     - Architectural phase gating
   * - **Context Efficiency**
     - Read entire files
     - Tier-based sizing
     - RAG chunk retrieval
   * - **Observability**
     - None
     - Manual tracking
     - Full HoneyHive tracing
   * - **Quality Gates**
     - None
     - 11 pre-commit hooks
     - Same (inherited)
   * - **AI Interface**
     - Tool calls (search, read)
     - Command language
     - MCP tools (5 tools)

**Credit Where Due:**

- **Builder Methods (Brian Casel)**: Three-layer architecture, spec-driven methodology, markdown standards
- **HoneyHive Engineering**: LLM Workflow Engineering, command language, phase gating, quality automation
- **This Implementation**: MCP/RAG server combining both approaches with programmatic enforcement and observability

Architecture
------------

The MCP server consists of four core components:

RAG Engine (``rag_engine.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Semantic search over Agent OS standards with metadata filtering.

**Technology**:

- **LanceDB**: Vector database (migrated from ChromaDB for better filtering)
- **sentence-transformers**: Local embeddings (``all-MiniLM-L6-v2`` model)
- **Grep Fallback**: When vector search unavailable, falls back to grep

**Key Features**:

- 90%+ retrieval accuracy on standard queries
- <100ms average latency
- Metadata filtering (phase, tags, file path)
- LRU cache with configurable TTL (5-minute default)
- Automatic index rebuilding

**Example Query**:

.. code-block:: python

   from mcp_servers.rag_engine import RAGEngine
   
   engine = RAGEngine(index_path, standards_path)
   
   # Search with semantic meaning
   result = engine.search(
       query="git safety rules forbidden operations",
       n_results=5,
       filters={"phase": 8}  # Only Phase 8 content
   )

Workflow Engine (``workflow_engine.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Phase-gated workflow execution with checkpoint validation.

**Workflows Supported**:

- ``test_generation_v3``: 8-phase TDD test generation workflow
- ``production_code_v2``: Production code generation with quality gates

**Phase Gating**:

.. code-block:: text

   Phase 1 → Evidence → Phase 2 → Evidence → Phase 3 → ...
   
   Cannot advance to Phase N+1 without completing Phase N evidence requirements.

**Checkpoint Validation**:

Each phase defines required evidence (e.g., "test file must exist", "coverage must be 90%+"). The workflow engine validates evidence before allowing progression.

**Example**:

.. code-block:: python

   from mcp_servers.workflow_engine import WorkflowEngine
   
   engine = WorkflowEngine(state_manager, rag_engine)
   
   # Start workflow
   state = engine.start_workflow(
       workflow_type="test_generation_v3",
       target_file="tests/unit/test_new_feature.py"
   )
   
   # Complete phase with evidence
   result = engine.complete_phase(
       session_id=state.session_id,
       phase=1,
       evidence={
           "test_file_created": True,
           "framework_decision": "pytest with fixtures"
       }
   )

State Manager (``state_manager.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Workflow state persistence and session lifecycle management.

**Features**:

- JSON-based state persistence in ``.agent-os/workflow_sessions/``
- Session expiration (30-day default)
- Automatic garbage collection of expired sessions
- State validation and integrity checking

Chunker (``chunker.py``)
~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Markdown document chunking for RAG indexing.

**Chunking Strategy**:

- **Size**: 100-500 tokens per chunk (optimal for semantic search)
- **Structure**: Respects markdown headers (keeps sections together)
- **Metadata**: Extracts phase numbers, tags, and section titles
- **Overlap**: Maintains context continuity between chunks

Getting Started
---------------

Prerequisites
~~~~~~~~~~~~~

1. **Cursor IDE** with MCP support
2. **Python 3.11+** with ``python-sdk`` virtual environment
3. **Agent OS standards** in ``.agent-os/standards/``

Building the RAG Index
~~~~~~~~~~~~~~~~~~~~~~

Before using the MCP server, build the vector index:

.. code-block:: bash

   cd /Users/josh/src/github.com/honeyhiveai/python-sdk
   
   # Activate project venv
   source python-sdk/bin/activate
   
   # Install MCP server dependencies
   pip install -r .agent-os/mcp_servers/requirements.txt
   
   # Build the index
   python .agent-os/scripts/build_rag_index.py

**Output**:

.. code-block:: text

   🏗️  Building RAG index from Agent OS standards...
   📁 Standards path: .agent-os/standards
   💾 Index path: .agent-os/rag_index
   
   📄 Processing 47 markdown files...
   ✅ Created 342 chunks
   🎯 90.2% retrieval accuracy on test queries
   ⚡ Average query time: 87ms
   
   ✅ Index built successfully!

Enabling in Cursor
~~~~~~~~~~~~~~~~~~

The MCP server is already configured in ``.cursor/mcp.json``:

.. code-block:: json

   {
     "mcpServers": {
       "agent-os-rag": {
         "command": "/Users/josh/src/github.com/honeyhiveai/python-sdk/python-sdk/bin/python",
         "args": [
           "/Users/josh/src/github.com/honeyhiveai/python-sdk/.agent-os/run_mcp_server.py"
         ],
         "env": {
           "HONEYHIVE_ENABLED": "true"
         },
         "autoApprove": [
           "search_standards",
           "get_current_phase",
           "get_workflow_state"
         ]
       }
     }
   }

**To Enable**:

1. Open Cursor Settings → MCP
2. Locate ``agent-os-rag`` server
3. Enable the server
4. Reload Cursor window

Using the MCP Tools
-------------------

The MCP server provides 5 tools for AI assistants:

1. search_standards
~~~~~~~~~~~~~~~~~~~

Semantic search over Agent OS standards with filtering.

**Example**:

.. code-block:: text

   User: "What are our git safety rules?"
   
   AI uses: mcp_agent-os-rag_search_standards(
     query="git safety rules forbidden operations",
     n_results=5
   )
   
   Returns: Relevant chunks from git-safety-rules.md

**Filters**:

- ``phase``: Filter by workflow phase number (1-8)
- ``tags``: Filter by metadata tags

2. start_workflow
~~~~~~~~~~~~~~~~~

Initialize a phase-gated workflow session.

**Example**:

.. code-block:: text

   User: "Generate tests for config/dsl/compiler.py"
   
   AI uses: mcp_agent-os-rag_start_workflow(
     workflow_type="test_generation_v3",
     target_file="tests/unit/config/dsl/test_compiler.py"
   )
   
   Returns: Phase 1 requirements and session ID

3. get_current_phase
~~~~~~~~~~~~~~~~~~~~

Retrieve current phase requirements and artifacts from previous phases.

4. complete_phase
~~~~~~~~~~~~~~~~~

Submit evidence and attempt to advance to next phase.

**Example**:

.. code-block:: text

   AI uses: mcp_agent-os-rag_complete_phase(
     session_id="abc-123",
     phase=1,
     evidence={
       "test_file_created": True,
       "framework_decision": "pytest"
     }
   )
   
   Returns: Phase 2 requirements if evidence validates

5. get_workflow_state
~~~~~~~~~~~~~~~~~~~~~

Query complete workflow state for debugging/resume capability.

Development
-----------

Running MCP Server Tests
~~~~~~~~~~~~~~~~~~~~~~~~

MCP server tests have **separate dependencies** from the main SDK and are excluded from the main test suite:

.. code-block:: bash

   # Activate venv with MCP dependencies
   source python-sdk/bin/activate
   pip install -r .agent-os/mcp_servers/requirements.txt
   
   # Run MCP server tests only
   pytest tests/unit/mcp_servers/ -v

**Test Coverage**:

- 28 comprehensive unit tests
- 10.0/10 Pylint score
- Full type annotations (MyPy clean)
- Tests for all 4 core components

Why Separate Tests?
~~~~~~~~~~~~~~~~~~~

The MCP server is an **independent component** with its own dependency tree:

**MCP Dependencies** (not in main SDK):

- ``lancedb>=0.3.0`` - Vector database
- ``sentence-transformers>=2.0.0`` - Local embeddings
- ``watchdog>=3.0.0`` - File watching
- ``mcp>=1.0.0`` - Model Context Protocol

**Rationale**:

- ✅ **No dependency bloat** in main SDK
- ✅ **Faster main SDK tests** (no vector DB initialization)
- ✅ **Clear separation** between SDK and tooling
- ✅ **Independent versioning** for MCP components

Adding New Tools
~~~~~~~~~~~~~~~~

To add a new MCP tool:

1. **Define the tool function** in ``agent_os_rag.py``
2. **Add @trace decorator** for observability
3. **Register with MCP server** in ``create_server()``
4. **Add to autoApprove** in ``.cursor/mcp.json`` (if safe)
5. **Write tests** in ``tests/unit/mcp_servers/``

**Example**:

.. code-block:: python

   @tool_trace
   @server.call_tool()
   async def new_tool(query: str) -> Sequence[types.TextContent]:
       """New tool description."""
       # Enrich span with input
       enrich_span({"query": query})
       
       # Tool logic here
       result = do_something(query)
       
       # Enrich span with output
       enrich_span({"result": result})
       
       return [types.TextContent(type="text", text=result)]

Hot Reload
~~~~~~~~~~

The MCP server includes a file watcher that automatically rebuilds the RAG index when standards change:

.. code-block:: python

   from watchdog.observers import Observer
   from watchdog.events import FileSystemEventHandler
   
   class AgentOSFileWatcher(FileSystemEventHandler):
       def on_modified(self, event):
           if event.src_path.endswith('.md'):
               # Debounce and rebuild index
               self._schedule_rebuild()

**In Development**:

- Edit any ``.agent-os/standards/*.md`` file
- Index automatically rebuilds in background
- New content available in ~2-3 seconds

Observability (Dogfooding HoneyHive)
------------------------------------

Every MCP tool operation is traced with HoneyHive instrumentation, demonstrating dogfooding of our own product.

Instrumentation Pattern
~~~~~~~~~~~~~~~~~~~~~~~

All tools use the ``@trace`` decorator with span enrichment:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   
   # Initialize tracer once
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project="your-project-here",
       source="agent-os-mcp-server",
       verbose=True
   )
   
   # Wrap tool with tracing
   @trace(tracer=tracer, event_type=EventType.tool)
   async def search_standards(query: str, n_results: int):
       # Enrich span with inputs
       enrich_span({
           "query": query,
           "n_results": n_results,
           "filters": filters
       })
       
       # Execute RAG search
       result = rag_engine.search(query, n_results, filters)
       
       # Enrich span with outputs
       enrich_span({
           "chunks_returned": len(result.chunks),
           "retrieval_method": result.retrieval_method,
           "query_time_ms": result.query_time_ms
       })
       
       return result

Viewing Traces
~~~~~~~~~~~~~~

1. Navigate to HoneyHive dashboard
2. Select project: **your-project-here**
3. Filter by source: **agent-os-mcp-server**

**Trace Attributes**:

- ``query``: Semantic search query
- ``n_results``: Number of chunks requested
- ``filters``: Metadata filters applied
- ``chunks_returned``: Actual chunks returned
- ``retrieval_method``: "vector" or "grep_fallback"
- ``query_time_ms``: RAG query latency
- ``session_id``: Workflow session ID (for workflow tools)
- ``phase``: Current phase number

Span Enrichment Examples
~~~~~~~~~~~~~~~~~~~~~~~~

**Search Tool**:

.. code-block:: json

   {
     "query": "git safety rules forbidden operations",
     "n_results": 5,
     "filters": null,
     "chunks_returned": 3,
     "retrieval_method": "vector",
     "query_time_ms": 87,
     "total_tokens": 840
   }

**Workflow Tool**:

.. code-block:: json

   {
     "session_id": "abc-123-def-456",
     "workflow_type": "test_generation_v3",
     "target_file": "tests/unit/test_feature.py",
     "current_phase": 2,
     "phase_content_tokens": 1200
   }

Troubleshooting
---------------

Import Errors
~~~~~~~~~~~~~

**Problem**: ``ModuleNotFoundError: No module named 'lancedb'``

**Solution**: Install MCP server dependencies:

.. code-block:: bash

   pip install -r .agent-os/mcp_servers/requirements.txt

**Why**: MCP server has separate dependencies from main SDK.

Index Rebuild Issues
~~~~~~~~~~~~~~~~~~~~

**Problem**: RAG index not updating after standards changes.

**Solutions**:

1. **Manual Rebuild**:

   .. code-block:: bash
   
      python .agent-os/scripts/build_rag_index.py

2. **Check File Watcher**: Look for errors in MCP server logs (Cursor DevTools).

3. **Clear Index**:

   .. code-block:: bash
   
      rm -rf .agent-os/rag_index
      python .agent-os/scripts/build_rag_index.py

Credential Loading
~~~~~~~~~~~~~~~~~~

**Problem**: HoneyHive traces not appearing in dashboard.

**Cause**: MCP server not loading credentials from ``.env``.

**Solution**: Verify ``.env`` has correct format:

.. code-block:: bash

   export HH_API_KEY="your-key-here"
   export HH_PROJECT="your-project-here"

**How Credentials Load**:

1. ``.cursor/mcp.json`` → Launches ``run_mcp_server.py``
2. ``run_mcp_server.py`` → Parses ``.env`` and loads into ``os.environ``
3. ``agent_os_rag.py`` → Reads from ``os.getenv()``

**Debug**:

Check MCP server logs in Cursor DevTools for:

.. code-block:: text

   DEBUG: HH_API_KEY=SET
   DEBUG: HONEYHIVE_PROJECT=your-project-here
   🍯 HoneyHive tracing enabled for dogfooding

No Traces Appearing
~~~~~~~~~~~~~~~~~~~

**Problem**: MCP server running but no traces in HoneyHive.

**Checklist**:

1. ✅ ``HONEYHIVE_ENABLED="true"`` in ``.cursor/mcp.json`` env
2. ✅ Valid ``HH_API_KEY`` and ``HH_PROJECT`` in ``.env``
3. ✅ Tracer initialized successfully (check logs)
4. ✅ Using correct project in HoneyHive dashboard

**Debugging**:

Enable verbose logging in ``agent_os_rag.py``:

.. code-block:: python

   tracer = HoneyHiveTracer.init(
       verbose=True  # Already enabled
   )

See Also
--------

**Agent OS Resources**:

- `Agent OS Documentation <https://buildermethods.com/agent-os>`_ - Official Agent OS guide by Builder Methods
- `Builder Methods YouTube <https://www.youtube.com/@buildermethods>`_ - AI-assisted development tutorials

**Related SDK Documentation**:

- :doc:`/development/testing/setup-and-commands` - Test infrastructure overview
- :doc:`/development/workflow-optimization` - AI-assisted development workflows
- :doc:`/how-to/advanced-tracing/custom-spans` - HoneyHive instrumentation patterns

**Internal References**:

- ``.agent-os/specs/2025-10-03-agent-os-mcp-rag-evolution/`` - Complete specification
- ``.agent-os/standards/ai-assistant/import-verification-rules.md`` - Import verification standard
- ``.cursorrules`` - AI assistant compliance rules


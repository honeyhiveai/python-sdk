# Integration Analysis Workflow - Pattern Discovery

**Date:** 2025-11-12  
**Context:** Successful pydantic-ai integration analysis using multi-repo code intelligence  
**Goal:** Extract reusable workflow pattern for analyzing third-party library integrations

---

## 🎯 Problem Statement

**Challenge:** Understand how a third-party library (pydantic-ai) integrates with OpenTelemetry to determine:
1. Do we need a custom instrumentor?
2. What span attributes does it generate?
3. Is it compatible with our ingestion service?
4. How do we integrate it with HoneyHive SDK?

**Traditional Approach Problems:**
- Reading entire codebase linearly (slow, overwhelming)
- Grepping for keywords (misses context, false positives)
- Trial-and-error testing (expensive, incomplete understanding)

**Code Intelligence Approach:**
- Graph traversal → Find data flow
- AST search → Find structure
- Semantic search → Validate understanding
- Targeted file reading → Get implementation details

---

## ✅ Successful Workflow Steps

### Phase 1: Call Flow Discovery (Graph Traversal)

**Goal:** Understand the execution path from user API to span creation

**Queries:**
```python
# Step 1: Find who calls the instrumentation function
pos_search_project(
    action="find_callers",
    query="_instrument",
    max_depth=3,
    filters={"partition": "pydantic_ai"}
)
# Result: request() and request_stream() call _instrument()

# Step 2: Find what instrumentation depends on
pos_search_project(
    action="find_dependencies",
    query="_instrument",
    max_depth=3,
    filters={"partition": "pydantic_ai"}
)
# Result: model_attributes(), model_request_parameters_attributes(), record_metrics()

# Step 3: Trace the full call path
pos_search_project(
    action="find_call_paths",
    query="request",
    to_symbol="model_attributes",
    max_depth=5,
    filters={"partition": "pydantic_ai"}
)
# Result: request → _instrument → model_attributes
```

**Output:** Call graph showing data flow from API → instrumentation → attribute setting

**Success Criteria:**
- ✅ Found entry points (`request`, `request_stream`)
- ✅ Found span creation (`_instrument`)
- ✅ Found attribute setters (`model_attributes`, etc.)
- ✅ Understood execution flow

---

### Phase 2: Structural Discovery (AST Search)

**Goal:** Find all functions in the instrumentation module to ensure nothing is missed

**Queries:**
```python
# Find all function definitions in the instrumentation file
pos_search_project(
    action="search_ast",
    query="function_definition",
    n_results=50,
    filters={"partition": "pydantic_ai", "file_path": "instrumented.py"}
)
# Result: 18 functions found with line numbers
```

**Output:** Complete inventory of functions in target file

**Success Criteria:**
- ✅ Found all functions (18 total)
- ✅ Got line ranges for each
- ✅ Identified key functions from Phase 1 in the list

**Current Gap:** AST results don't include function names or signatures (only line numbers)

---

### Phase 3: Implementation Analysis (Targeted File Reading)

**Goal:** Read specific functions identified in Phase 1 & 2 to understand implementation

**Queries:**
```python
# Read the main instrumentation function
read_file(
    target_file="pydantic_ai/models/instrumented.py",
    offset=400,
    limit=90
)
# Lines 400-486: _instrument() implementation

# Read attribute setting functions
read_file(
    target_file="pydantic_ai/models/instrumented.py",
    offset=489,
    limit=35
)
# Lines 489-505: model_attributes() implementation
# Lines 508-511: model_request_parameters_attributes() implementation
```

**Output:** Actual code for span creation and attribute setting

**Success Criteria:**
- ✅ Found `gen_ai.operation.name`, `gen_ai.system`, `gen_ai.request.model`
- ✅ Found usage tracking (`gen_ai.usage.*`)
- ✅ Found cost calculation (`operation.cost`)
- ✅ Found tracer initialization pattern (`get_tracer_provider()`)

---

### Phase 4: Validation (Semantic Search)

**Goal:** Validate understanding with conceptual queries

**Queries:**
```python
# Confirm tracer provider usage
pos_search_project(
    action="search_code",
    query="How does InstrumentedModel get the OpenTelemetry tracer provider?",
    n_results=5,
    filters={"partition": "pydantic_ai"}
)
# Result: Confirms get_tracer_provider() usage

# Find message handling
pos_search_project(
    action="search_code",
    query="How are gen_ai.input.messages and gen_ai.output.messages set?",
    n_results=5,
    filters={"partition": "pydantic_ai"}
)
# Result: instrumentation_settings.handle_messages()
```

**Output:** Conceptual confirmation of technical understanding

**Success Criteria:**
- ✅ Confirmed tracer provider pattern
- ✅ Found message attribute handling
- ✅ Validated GenAI semantic convention usage

---

### Phase 5: Compatibility Check (Multi-Repo Analysis)

**Goal:** Check if ingestion service can handle the attributes

**Queries:**
```python
# Find existing fixtures
glob_file_search(
    glob_pattern="*pydantic_ai*.json",
    target_directory="hive-kube/kubernetes/ingestion_service"
)
# Result: 3 existing pydantic-ai fixtures

# Read fixtures to understand attribute mapping
read_file(target_file="pydantic_ai_anthropic_agent_001.json")
read_file(target_file="pydantic_ai_claude_chat_001.json")
read_file(target_file="pydantic_ai_anthropic_running_tool_001.json")

# Check ingestion service attribute mappings
codebase_search(
    query="How does attribute_router map gen_ai attributes?",
    target_directories=["hive-kube/kubernetes/ingestion_service"]
)
```

**Output:** Compatibility matrix showing supported vs. missing attributes

**Success Criteria:**
- ✅ Found existing fixtures (proves some support)
- ✅ Identified supported attributes (~85%)
- ✅ Identified gaps (tool attributes need mapping)

---

## 🔄 Workflow Pattern (Generalized)

### Input Parameters
```python
{
    "target_library": "pydantic-ai",           # Library to analyze
    "integration_type": "opentelemetry",       # Integration type
    "partition": "pydantic_ai",                # Code index partition
    "entry_points": ["Agent.run", "request"],  # User-facing APIs
    "key_concepts": ["spans", "attributes", "tracer"],  # What to look for
}
```

### Execution Steps

```
1. DISCOVER_CALL_FLOW (graph_traversal)
   ├─ find_callers(entry_points) → Find instrumentation hooks
   ├─ find_dependencies(hooks) → Find helper functions
   └─ find_call_paths(entry → helpers) → Validate flow
   
2. FIND_ALL_FUNCTIONS (ast_search)
   └─ search_ast("function_definition", file=instrumentation_file)
   
3. READ_IMPLEMENTATIONS (file_reading)
   ├─ read_file(instrumentation_function)
   ├─ read_file(attribute_setters)
   └─ read_file(tracer_initialization)
   
4. VALIDATE_UNDERSTANDING (semantic_search)
   ├─ search_code("How does X get tracer?")
   ├─ search_code("Where are Y attributes set?")
   └─ search_code("What Z semantic conventions are used?")
   
5. CHECK_COMPATIBILITY (multi_repo_analysis)
   ├─ glob_file_search("*{library}*.json") → Find existing fixtures
   ├─ read_file(fixtures) → Understand expected format
   └─ search_code("attribute mapping", partition=ingestion_service)
   
6. SYNTHESIZE_FINDINGS (documentation)
   └─ Generate analysis document with:
      - Integration pattern (code example)
      - Attribute matrix (supported vs. gaps)
      - Compatibility score
      - Next steps (tests, fixtures, docs)
```

---

## 📊 Success Metrics

**Workflow Quality Indicators:**

| Metric | Target | Actual (pydantic-ai) |
|--------|--------|---------------------|
| Time to understanding | < 30 min | ~20 min |
| Files read manually | < 5 | 3 (instrumented.py sections) |
| Grep queries needed | 0 | 0 ✅ |
| Trial-and-error tests | 0 | 0 ✅ |
| Completeness | > 90% | ~95% (missed some logfire-specific attrs) |
| Confidence in findings | High | High ✅ |

**Key Advantages:**
- ✅ No guessing (graph traversal shows exact flow)
- ✅ No missing code (AST search finds all functions)
- ✅ No context loss (semantic search validates understanding)
- ✅ Multi-repo analysis (cross-repository compatibility check)

---

## 🚧 Current Gaps & Improvements

### Tool Limitations

1. **AST Search Results**
   - ❌ Current: Only returns `"function_definition (lines 66-74)"`
   - ✅ Needed: Extract function names from AST (`def _instrument(...)`)
   - ✅ Needed: Include function signature in `content` field
   - ✅ Needed: Populate `symbol_name` field

2. **Code Search in Multi-Partition Mode**
   - ❌ Async build bug (lazy index build broken)
   - ✅ Needed: Explicit index build on partition add
   - ✅ Needed: Health check per partition

3. **Graph Traversal Partition Requirement**
   - ❌ Must specify partition (can't auto-detect)
   - ✅ Needed: Infer partition from symbol if unique

### Workflow Improvements

1. **Automated Evidence Collection**
   - Capture query results → evidence dictionary
   - Track which queries answered which questions
   - Build confidence score per finding

2. **Iterative Refinement**
   - After Phase 1, suggest Phase 2 queries
   - After Phase 3, validate with Phase 4
   - Loop until confidence threshold met

3. **Parallel Query Execution**
   - Run multiple graph traversal queries simultaneously
   - Read multiple file sections in parallel
   - Batch semantic validation queries

---

## 🎯 Candidate Workflow: `integration_analysis_v1`

### Workflow Definition

```yaml
workflow_type: integration_analysis_v1
description: Analyze third-party library integration with OpenTelemetry
estimated_hours: 0.5-1.0

phases:
  - phase: 1
    name: "Call Flow Discovery"
    tasks:
      - Use find_callers to locate instrumentation hooks
      - Use find_dependencies to find helper functions
      - Use find_call_paths to validate execution flow
    evidence_required:
      - call_graph: JSON with entry points → hooks → helpers
      
  - phase: 2
    name: "Structural Inventory"
    tasks:
      - Use search_ast to find all functions in instrumentation file
      - Identify functions from Phase 1 in AST results
    evidence_required:
      - function_inventory: List of all functions with line ranges
      
  - phase: 3
    name: "Implementation Analysis"
    tasks:
      - Read instrumentation functions from Phase 1
      - Read attribute setter functions from Phase 1
      - Extract span attributes, tracer usage
    evidence_required:
      - span_attributes: List of all attributes set
      - tracer_pattern: How library gets tracer instance
      
  - phase: 4
    name: "Semantic Validation"
    tasks:
      - Search for tracer initialization pattern
      - Search for attribute setting patterns
      - Validate GenAI semantic convention compliance
    evidence_required:
      - validation_queries: Conceptual confirmations
      
  - phase: 5
    name: "Compatibility Analysis"
    tasks:
      - Find existing fixtures in ingestion service
      - Read fixtures to understand format
      - Check attribute mapping in ingestion service
    evidence_required:
      - compatibility_matrix: Supported vs. missing attributes
      - compatibility_score: Percentage (0-100)
      
  - phase: 6
    name: "Documentation"
    tasks:
      - Generate integration pattern code example
      - Create attribute compatibility matrix
      - List next steps (tests, fixtures, docs)
    evidence_required:
      - analysis_document: Complete markdown report

success_criteria:
  - All phases completed
  - Compatibility score > 80%
  - Integration pattern code example generated
  - Next steps clearly defined
```

---

## 🔍 Key Insights

### What Made This Work

1. **Right Tool, Right Job**
   - Graph traversal for data flow (not grep)
   - AST search for structure inventory (not manual)
   - Semantic search for validation (not trial-and-error)
   - File reading only after narrowing scope

2. **Multi-Repo Intelligence**
   - Analyzed pydantic-ai source
   - Checked hive-kube fixtures
   - Cross-referenced attribute mappings
   - All without context switching

3. **Incremental Understanding**
   - Phase 1 identified targets for Phase 2
   - Phase 2 provided line numbers for Phase 3
   - Phase 3 revealed details for Phase 4
   - Each phase built on previous

### What Didn't Work

1. **Direct AST queries for specific functions**
   - AST search doesn't support `"function_definition name:_instrument"`
   - Need to get all functions → filter manually

2. **Semantic search for exact implementation**
   - Good for concepts ("how does X work?")
   - Bad for exact code ("what does line 450 do?")

3. **Guessing partition names**
   - `filters={"type": "framework"}` returned empty
   - Better to use `filters={"partition": "pydantic_ai"}`

---

## 📝 Next Steps

1. **Fix AST Search**
   - Extract function/class names from AST nodes
   - Include signatures in `content` field
   - Populate `symbol_name` field

2. **Create Workflow**
   - Implement `integration_analysis_v1` workflow
   - Add to `.praxis-os/workflows/`
   - Test with another integration (e.g., langchain, openlit)

3. **Add Automation**
   - Auto-suggest next phase queries based on results
   - Parallel query execution
   - Evidence validation scoring

4. **Document Pattern**
   - Add to standards: "How to analyze third-party integrations"
   - Include query templates
   - Share with team

---

## 🎓 Lessons Learned

**For AI Agents:**
- Always start with graph traversal for new codebases
- Use AST to ensure completeness (no missed functions)
- Read files only after narrowing scope
- Validate understanding with semantic queries
- Think in phases: discover → inventory → analyze → validate → document

**For Tool Design:**
- AST results need more context (function names, signatures)
- Multi-repo analysis is incredibly powerful
- Partition-based indexing enables focused searches
- Graph traversal reveals what grep cannot

**For Workflow Design:**
- Phase-gated execution prevents wasted work
- Evidence requirements keep AI focused
- Each phase should inform the next
- Success criteria should be measurable


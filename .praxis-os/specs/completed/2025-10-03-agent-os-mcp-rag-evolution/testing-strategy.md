# Testing Strategy
# Agent OS MCP/RAG Evolution

**Document Version:** 1.0  
**Date:** October 3, 2025  
**Status:** Draft - Specification Phase

---

## PURPOSE

This document defines the **comprehensive testing strategy** for validating the Agent OS MCP/RAG implementation, ensuring quality preservation and success criteria achievement.

---

## TESTING PYRAMID

```
                    ┌─────────────────────┐
                    │   End-to-End Tests  │  5 tests
                    │  (Full workflows)   │  (5%)
                    └─────────────────────┘
                 ┌──────────────────────────┐
                 │   Integration Tests      │  15 tests
                 │   (Component interaction)│  (15%)
                 └──────────────────────────┘
            ┌──────────────────────────────────┐
            │      Unit Tests                  │  80 tests
            │  (Individual functions/classes)  │  (80%)
            └──────────────────────────────────┘
```

---

## UNIT TESTING

### Coverage Target

- **Line Coverage:** 90%+
- **Branch Coverage:** 85%+
- **Files:** All `.praxis-os/mcp_servers/*.py`

### Test Files

```
tests/unit/mcp_servers/
├── test_chunker.py              # 15 tests
├── test_models.py               # 10 tests
├── test_state_manager.py        # 12 tests
├── test_workflow_engine.py      # 20 tests
├── test_rag_engine.py          # 18 tests
└── test_agent_os_rag.py        # 5 tests
                        TOTAL:    80 tests
```

### Chunker Tests

```python
# tests/unit/mcp_servers/test_chunker.py

def test_token_counting_accuracy():
    """Test token counting within 20% accuracy."""
    text = "This is a test sentence. " * 50
    tokens = count_tokens(text)
    expected = len(text) // 4  # Rough estimate
    assert abs(tokens - expected) / expected < 0.20

def test_parse_markdown_headers():
    """Test header parsing with nested structure."""
    content = """
## Phase 1
Content

### Subheader
Sub content

## Phase 2
More content
"""
    sections = parse_markdown_headers(content)
    assert len(sections) == 3
    assert sections[0]['header'] == "Phase 1"
    assert sections[0]['level'] == 2
    assert sections[1]['level'] == 3

def test_chunk_small_section():
    """Test chunking section under MAX_TOKENS."""
    chunker = AgentOSChunker()
    section = {
        'header': 'Test Header',
        'content': 'Small content ' * 20,  # ~100 tokens
        'level': 2
    }
    chunks = chunker._chunk_section(section, Path("test.md"))
    assert len(chunks) == 1
    assert chunks[0].tokens < 500

def test_chunk_large_section():
    """Test chunking section over MAX_TOKENS."""
    chunker = AgentOSChunker()
    section = {
        'header': 'Large Header',
        'content': 'Large content. ' * 200,  # ~600 tokens
        'level': 2
    }
    chunks = chunker._chunk_section(section, Path("test.md"))
    assert len(chunks) >= 2
    assert all(c.tokens <= 500 for c in chunks)

def test_metadata_extraction_phase():
    """Test phase number extraction from content."""
    content = "## Phase 1: Method Verification\nRequirements..."
    chunk = DocumentChunk(content=content, ...)
    metadata = chunker._extract_metadata(content, Path("test.md"))
    assert metadata.phase == 1

def test_metadata_extraction_critical():
    """Test critical marker detection."""
    content = "MANDATORY: Complete all steps before proceeding."
    metadata = chunker._extract_metadata(content, Path("test.md"))
    assert metadata.is_critical is True

def test_metadata_extraction_tags():
    """Test tag extraction from content."""
    content = "Use mocking for external dependencies. AST analysis required."
    metadata = chunker._extract_metadata(content, Path("test.md"))
    assert "mocking" in metadata.tags
    assert "ast" in metadata.tags

def test_chunk_id_stability():
    """Test chunk IDs are stable across runs."""
    chunk1 = chunker._create_chunk(section, Path("test.md"))
    chunk2 = chunker._create_chunk(section, Path("test.md"))
    assert chunk1.chunk_id == chunk2.chunk_id

def test_chunk_real_file():
    """Test chunking actual Agent OS file."""
    chunker = AgentOSChunker()
    test_file = Path(".praxis-os/standards/ai-assistant/compliance-checking.md")
    chunks = chunker.chunk_file(test_file)
    
    assert len(chunks) > 0
    assert all(100 <= c.tokens <= 500 for c in chunks)
    assert all(c.chunk_id for c in chunks)
    assert all(c.metadata for c in chunks)

# ... 6 more tests covering edge cases
```

### Workflow Engine Tests

```python
# tests/unit/mcp_servers/test_workflow_engine.py

def test_start_workflow():
    """Test workflow initialization."""
    engine = WorkflowEngine(state_manager, rag_engine)
    result = engine.start_workflow("test_generation_v3", "test.py")
    
    assert result["session_id"]
    assert result["current_phase"] == 1
    assert result["total_phases"] == 8
    assert result["phase_content"]

def test_phase_gating_prevents_skip():
    """Test cannot skip phases."""
    session_id = engine.start_workflow("test_generation_v3", "test.py")["session_id"]
    
    # Try to access Phase 3 (current is 1)
    result = engine.get_phase_content(session_id, requested_phase=3)
    
    assert "error" in result
    assert result["error"] == "phase_sequence_violation"
    assert result["current_phase_content"]

def test_checkpoint_validation_complete_evidence():
    """Test checkpoint passes with complete evidence."""
    evidence = {
        "function_count": 21,
        "method_count": 15,
        "branch_count": 36,
        "ast_command_output": "def compile()...",
        "functions_list": ["compile", "parse"]
    }
    
    passed, missing = engine.validate_checkpoint(phase=1, evidence=evidence)
    
    assert passed is True
    assert missing == []

def test_checkpoint_validation_missing_evidence():
    """Test checkpoint fails with incomplete evidence."""
    evidence = {
        "function_count": 21
        # Missing other fields
    }
    
    passed, missing = engine.validate_checkpoint(phase=1, evidence=evidence)
    
    assert passed is False
    assert len(missing) > 0

def test_complete_phase_advances():
    """Test completing phase advances to next."""
    session_id = engine.start_workflow("test_generation_v3", "test.py")["session_id"]
    
    # Complete Phase 1
    result = engine.complete_phase(session_id, phase=1, evidence={...})
    
    assert result["checkpoint_passed"] is True
    assert result["next_phase"] == 2
    assert result["next_phase_content"]

def test_artifacts_available_in_next_phase():
    """Test artifacts from Phase 1 available in Phase 2."""
    session_id = engine.start_workflow("test_generation_v3", "test.py")["session_id"]
    
    # Complete Phase 1 with artifacts
    engine.complete_phase(session_id, phase=1, evidence={
        "functions_list": ["compile", "parse"]
    })
    
    # Get Phase 2 content
    result = engine.get_phase_content(session_id, requested_phase=2)
    
    assert "artifacts_from_previous" in result
    assert 1 in result["artifacts_from_previous"]
    assert "functions_list" in result["artifacts_from_previous"][1]

def test_state_persistence_across_restarts():
    """Test state persists and can be resumed."""
    session_id = engine.start_workflow("test_generation_v3", "test.py")["session_id"]
    engine.complete_phase(session_id, phase=1, evidence={...})
    
    # Simulate restart
    new_engine = WorkflowEngine(state_manager, rag_engine)
    state = new_engine.get_workflow_state(session_id)
    
    assert state["current_phase"] == 2
    assert 1 in state["completed_phases"]

# ... 12 more tests covering all scenarios
```

### RAG Engine Tests

```python
# tests/unit/mcp_servers/test_rag_engine.py

def test_vector_search_basic():
    """Test basic vector search."""
    result = rag_engine.search("Phase 1 requirements", n_results=5)
    
    assert len(result.chunks) == 5
    assert result.retrieval_method == "vector"
    assert all(score > 0.5 for score in result.relevance_scores)

def test_vector_search_with_phase_filter():
    """Test vector search with phase filtering."""
    result = rag_engine.search(
        "method verification",
        filter_phase=1,
        n_results=5
    )
    
    assert all(chunk.metadata.phase == 1 for chunk in result.chunks)

def test_vector_search_with_tag_filter():
    """Test vector search with tag filtering."""
    result = rag_engine.search(
        "external dependencies",
        filter_tags=["mocking"],
        n_results=5
    )
    
    assert all("mocking" in chunk.metadata.tags for chunk in result.chunks)

def test_fallback_to_grep():
    """Test fallback to grep when vector search fails."""
    # Simulate vector search failure
    rag_engine._chromadb_client = None
    
    result = rag_engine.search("Phase 1", n_results=5)
    
    assert result.retrieval_method == "grep"
    assert len(result.chunks) > 0

def test_query_latency():
    """Test query latency meets performance target."""
    import time
    
    start = time.time()
    result = rag_engine.search("method verification", n_results=5)
    elapsed_ms = (time.time() - start) * 1000
    
    assert elapsed_ms < 100  # p95 target

def test_caching():
    """Test query result caching."""
    # First query
    result1 = rag_engine.search("Phase 1", n_results=5)
    
    # Second identical query should be faster
    import time
    start = time.time()
    result2 = rag_engine.search("Phase 1", n_results=5)
    elapsed_ms = (time.time() - start) * 1000
    
    assert elapsed_ms < 10  # Should be cached
    assert result1.chunks[0].chunk_id == result2.chunks[0].chunk_id

# ... 12 more tests
```

---

## INTEGRATION TESTING

### Integration Test Scenarios

```python
# tests/integration/test_mcp_end_to_end.py

def test_honeyhive_tracing_integration():
    """Test HoneyHive tracing for dogfooding."""
    # Setup HoneyHive environment
    os.environ["HONEYHIVE_ENABLED"] = "true"
    os.environ["HONEYHIVE_PROJECT"] = "agent-os-mcp-rag-test"
    
    # Start MCP server with tracing
    mcp_server = AgentOSMCPServer()
    
    # Execute traced operation
    result = mcp_server.pos_search_project(action="search_standards", query=
        query="Phase 1 requirements",
        n_results=5
    )
    
    # Verify operation succeeded
    assert "results" in result
    
    # Verify trace was created (check HoneyHive)
    # NOTE: In real implementation, would query HoneyHive API
    # to verify trace exists with correct metadata
    
    # Verify trace metadata
    # assert trace has: query, n_results, chunks_returned, query_time_ms

def test_complete_workflow_integration():
    """Test complete 8-phase workflow."""
    # Start workflow
    result = mcp_server.start_workflow("test_generation_v3", "test.py")
    session_id = result["session_id"]
    
    # Complete all 8 phases
    for phase in range(1, 9):
        # Get phase content
        content = mcp_server.get_current_phase(session_id)
        assert content["current_phase"] == phase
        
        # Complete phase checkpoint
        evidence = generate_phase_evidence(phase)
        result = mcp_server.complete_phase(session_id, phase, evidence)
        
        if phase < 8:
            assert result["next_phase_unlocked"] is True
        else:
            assert result["workflow_complete"] is True

def test_cursor_mcp_integration():
    """Test MCP server works from Cursor."""
    # Simulate Cursor launching MCP server
    server_process = subprocess.Popen([
        "python", ".praxis-os/mcp_servers/agent_os_rag.py"
    ])
    
    time.sleep(2)  # Allow startup
    
    # Test tool calls
    result = call_mcp_tool("search_standards", {
        "query": "Phase 1 requirements",
        "n_results": 5
    })
    
    assert "results" in result
    assert len(result["results"]) == 5
    
    server_process.terminate()

def test_rag_workflow_integration():
    """Test RAG engine integrated with workflow engine."""
    # RAG should provide phase-specific content
    session_id = workflow_engine.start_workflow("test_generation_v3", "test.py")["session_id"]
    
    phase_content = workflow_engine.get_phase_content(session_id, requested_phase=1)
    
    # Verify content is Phase 1 specific
    assert "Phase 1" in phase_content["content"]
    assert "Method Verification" in phase_content["content"]

def test_state_persistence_integration():
    """Test state persists correctly between sessions."""
    # Create session and complete Phase 1
    session_id = workflow_engine.start_workflow("test_generation_v3", "test.py")["session_id"]
    workflow_engine.complete_phase(session_id, 1, evidence={...})
    
    # Simulate Cursor restart
    del workflow_engine
    new_workflow_engine = WorkflowEngine(...)
    
    # Resume session
    state = new_workflow_engine.get_workflow_state(session_id)
    assert state["current_phase"] == 2
    assert 1 in state["completed_phases"]

# ... 11 more integration tests
```

---

## END-TO-END TESTING

### E2E Test Scenarios

```python
# tests/e2e/test_full_workflows.py

def test_e2e_test_generation_workflow():
    """
    End-to-end test: Complete test generation workflow.
    
    This test validates the entire system working together:
    - Cursor launches MCP server
    - AI queries for Phase 1 content
    - AI completes each phase with evidence
    - AI generates tests using workflow guidance
    - Tests pass with 10.0/10 Pylint, 95%+ coverage
    """
    # Setup
    target_file = "config/dsl/compiler.py"
    
    # Start workflow
    session_id = start_workflow_via_cursor(
        workflow_type="test_generation_v3",
        target_file=target_file
    )
    
    # Simulate AI completing workflow
    for phase in range(1, 9):
        # AI queries for phase content
        content = query_mcp_tool("get_current_phase", {"session_id": session_id})
        
        # AI executes phase (simulated)
        evidence = execute_phase_commands(content)
        
        # AI submits checkpoint
        result = query_mcp_tool("complete_phase", {
            "session_id": session_id,
            "phase": phase,
            "evidence": evidence
        })
        
        assert result["checkpoint_passed"] is True
    
    # Generate tests using workflow artifacts
    # (This would be done by AI in real scenario)
    
    # Validate outcomes
    test_file = f"tests/unit/config/test_dsl_compiler.py"
    assert Path(test_file).exists()
    
    # Run quality checks
    pylint_score = run_pylint(test_file)
    coverage = run_coverage(test_file)
    
    assert pylint_score >= 10.0
    assert coverage >= 95.0

def test_e2e_context_reduction():
    """
    End-to-end test: Context reduction measurement.
    
    Compare context consumption before/after MCP/RAG.
    """
    # Baseline: Current approach (full files in context)
    baseline_tokens = measure_baseline_context_consumption()
    
    # New approach: MCP/RAG (only relevant chunks)
    rag_tokens = measure_rag_context_consumption()
    
    # Calculate reduction
    reduction = (baseline_tokens - rag_tokens) / baseline_tokens
    
    assert reduction >= 0.85  # 85%+ reduction target

def test_e2e_quality_preservation():
    """
    End-to-end test: Quality outcomes preserved.
    
    Validate same quality outcomes with MCP/RAG vs baseline.
    """
    target_file = "config/dsl/compiler.py"
    
    # Generate tests using MCP/RAG
    test_file = generate_tests_with_mcp_rag(target_file)
    
    # Measure quality
    quality_metrics = {
        "pylint_score": run_pylint(test_file),
        "coverage_line": run_coverage_line(test_file),
        "coverage_branch": run_coverage_branch(test_file),
        "mypy_errors": run_mypy(test_file)
    }
    
    # Compare to baseline (from AI Perspective doc)
    baseline = {
        "pylint_score": 10.0,
        "coverage_line": 95.94,
        "coverage_branch": 92.0,
        "mypy_errors": 0
    }
    
    # Allow ±2% variance
    assert abs(quality_metrics["pylint_score"] - baseline["pylint_score"]) < 0.1
    assert abs(quality_metrics["coverage_line"] - baseline["coverage_line"]) < 2.0
    assert quality_metrics["mypy_errors"] == baseline["mypy_errors"]

# ... 2 more E2E tests
```

---

## VALIDATION TESTING

### RAG Accuracy Validation

```python
# .praxis-os/scripts/validate_rag.py

# Test query set (50 queries with expected results)
TEST_QUERIES = [
    {
        "query": "Phase 1 method verification requirements",
        "expected_phase": 1,
        "expected_keywords": ["function", "method", "AST", "grep"],
        "min_relevance": 0.85
    },
    {
        "query": "How to determine mocking boundaries",
        "expected_tags": ["mocking"],
        "expected_keywords": ["boundary", "external", "dependency"],
        "min_relevance": 0.80
    },
    {
        "query": "Quality targets for test generation",
        "expected_keywords": ["Pylint", "10.0", "coverage", "95%"],
        "min_relevance": 0.85
    },
    # ... 47 more queries
]

def validate_rag_accuracy():
    """Validate RAG retrieval accuracy."""
    rag_engine = RAGEngine(...)
    
    results = []
    for test in TEST_QUERIES:
        result = rag_engine.search(test["query"], n_results=5)
        
        # Check if expected keywords in top result
        top_chunk = result.chunks[0]
        keywords_found = all(
            kw.lower() in top_chunk.content.lower()
            for kw in test["expected_keywords"]
        )
        
        # Check relevance score
        relevance_ok = result.relevance_scores[0] >= test["min_relevance"]
        
        # Check phase if specified
        phase_ok = True
        if "expected_phase" in test:
            phase_ok = top_chunk.metadata.phase == test["expected_phase"]
        
        success = keywords_found and relevance_ok and phase_ok
        results.append(success)
        
        if not success:
            print(f"FAIL: {test['query']}")
            print(f"  Expected: {test['expected_keywords']}")
            print(f"  Got: {top_chunk.content[:200]}...")
    
    accuracy = sum(results) / len(results)
    print(f"\n{'='*50}")
    print(f"RAG Accuracy: {accuracy:.1%}")
    print(f"Target: 90%+")
    print(f"Status: {'✅ PASS' if accuracy >= 0.90 else '❌ FAIL'}")
    
    assert accuracy >= 0.90, f"Accuracy {accuracy:.1%} below 90% target"
```

### Performance Benchmarking

```python
# .praxis-os/scripts/benchmark_rag.py

def benchmark_query_latency():
    """Benchmark query latency."""
    rag_engine = RAGEngine(...)
    
    queries = [
        "Phase 1 requirements",
        "Mocking strategies",
        "Coverage targets",
        # ... 100 total queries
    ]
    
    latencies = []
    for query in queries:
        start = time.time()
        result = rag_engine.search(query, n_results=5)
        elapsed_ms = (time.time() - start) * 1000
        latencies.append(elapsed_ms)
    
    # Calculate percentiles
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)
    
    print(f"Query Latency:")
    print(f"  p50: {p50:.1f}ms (target: 30ms)")
    print(f"  p95: {p95:.1f}ms (target: 100ms)")
    print(f"  p99: {p99:.1f}ms (target: 200ms)")
    
    assert p95 < 100, f"p95 latency {p95:.1f}ms exceeds 100ms target"

def benchmark_index_build():
    """Benchmark index build time."""
    start = time.time()
    builder = IndexBuilder(...)
    builder.build_index()
    elapsed = time.time() - start
    
    print(f"Index Build Time: {elapsed:.1f}s (target: <60s)")
    assert elapsed < 60, f"Build time {elapsed:.1f}s exceeds 60s target"
```

---

## REGRESSION TESTING

### Quality Regression Suite

```python
# tests/regression/test_quality_regression.py

def test_no_regression_in_pylint_scores():
    """Ensure Pylint scores don't regress."""
    # Baseline scores from pre-MCP/RAG
    baseline_scores = load_baseline_scores()
    
    # Current scores
    current_scores = run_all_pylint_checks()
    
    for file, baseline in baseline_scores.items():
        current = current_scores[file]
        assert current >= baseline - 0.1, \
            f"{file}: Pylint regressed from {baseline} to {current}"

def test_no_regression_in_coverage():
    """Ensure coverage doesn't regress."""
    baseline_coverage = load_baseline_coverage()
    current_coverage = run_all_coverage_checks()
    
    for file, baseline in baseline_coverage.items():
        current = current_coverage[file]
        assert current >= baseline - 2.0, \
            f"{file}: Coverage regressed from {baseline}% to {current}%"
```

---

## TEST EXECUTION

### Running Tests

```bash
# Unit tests
pytest tests/unit/mcp_servers/ -v --cov=.praxis-os/mcp_servers --cov-report=html

# Integration tests
pytest tests/integration/ -v

# End-to-end tests (slower)
pytest tests/e2e/ -v -s

# Validation
python .praxis-os/scripts/validate_rag.py

# Benchmarking
python .praxis-os/scripts/benchmark_rag.py

# All tests
pytest tests/ -v --cov=.praxis-os/mcp_servers
```

---

## SUCCESS CRITERIA

**Testing succeeds when:**

✅ 90%+ unit test line coverage  
✅ 85%+ unit test branch coverage  
✅ All 80 unit tests pass  
✅ All 15 integration tests pass  
✅ All 5 E2E tests pass  
✅ RAG accuracy >= 90%  
✅ Query latency p95 < 100ms  
✅ Quality metrics match baseline ±2%  
✅ No regressions detected

---

**Document Status:** Complete - Ready for Review  
**All Specification Documents Complete:** 9/9  
**Purpose:** Comprehensive testing validation strategy  
**Coverage:** Unit, Integration, E2E, Validation, Regression


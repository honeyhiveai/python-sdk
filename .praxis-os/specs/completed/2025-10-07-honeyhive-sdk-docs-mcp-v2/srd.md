# Software Requirements Document
# HoneyHive SDK Documentation MCP Server v2

**Project:** HoneyHive SDK Documentation MCP Server (v2 - Production-Hardened)  
**Date:** 2025-10-07  
**Priority:** Critical  
**Category:** AI Development Platform Enhancement  
**Version:** 2.0 (Incorporates Agent OS MCP Lessons Learned)

---

## 1. Introduction

### 1.1 Purpose

This document defines the requirements for the HoneyHive SDK Documentation MCP Server v2—a production-hardened, project-specific Model Context Protocol server that provides AI assistants with semantic search and structured access to the complete HoneyHive SDK knowledge corpus.

**Key Enhancement Over V1:** This version incorporates critical lessons learned from the Agent OS MCP corruption bug (October 2025), ensuring concurrency safety, proper dependency management, and systematic failure mode analysis.

### 1.2 Scope

This feature will provide:
- Semantic search over 5 knowledge sources (local docs, Mintlify, source code, examples, OTEL)
- Real-time knowledge updates via hot reload
- Production-grade reliability with concurrency safety
- Graceful degradation and comprehensive error handling
- Full HoneyHive tracing for dogfooding and observability

### 1.3 Document Evolution

This specification builds upon:
- **Original Spec:** `.praxis-os/specs/2025-10-04-honeyhive-sdk-docs-mcp/`
- **Critical Gaps:** Identified in `VALIDATION.md` (6 major issues)
- **Improvements:** Detailed in `SPEC_IMPROVEMENTS_ANALYSIS.md`
- **Learnings:** From Agent OS MCP concurrency bug fix (October 2025)

---

## 2. Business Goals

### Goal 1: Transform AI into Expert SDK Developer

**Objective:** Elevate AI assistants from "helpful but hallucination-prone" to "expert SDK developers with perfect memory and instant recall" by providing semantic access to the complete HoneyHive SDK knowledge corpus.

**Success Metrics:**
- Import path hallucination: 30% error rate → <1% error rate
- Parameter name accuracy: 60% correct → >99% correct  
- Context efficiency: 4,000 tokens average → <500 tokens average (87.5% reduction)
- Knowledge freshness: Months lag → <10 seconds lag

**Business Impact:**
- Developers freed from fact-checking AI outputs (role inversion correction)
- Faster development velocity (no manual doc lookup)
- Reduced frustration (fewer hallucination bugs)
- Confidence in AI-generated code (provenance and citations)

### Goal 2: Production-Grade Reliability

**Objective:** Deliver a production-ready MCP server that never crashes, handles concurrent access safely, and degrades gracefully under failure conditions.

**Success Metrics:**
- Zero file corruption incidents (vs. Agent OS MCP bug)
- Zero race condition crashes
- 100% graceful degradation on external dependency failures
- <5 minute recovery time on index corruption

**Business Impact:**
- Developer trust in AI infrastructure
- No disruption to development workflow
- Systematic quality vs. ad-hoc development
- Foundation for future MCP servers

### Goal 3: Dogfooding Value

**Objective:** Use HoneyHive SDK's own tracing capabilities to observe and optimize the MCP server, validating product-market fit for AI infrastructure observability.

**Success Metrics:**
- 100% of MCP tool calls traced
- Query pattern analysis reveals retrieval improvements
- Latency insights drive performance optimization
- Case study: "We use our product to build our product"

**Business Impact:**
- Internal validation of HoneyHive for AI workloads
- Product improvement feedback loop
- Marketing case study (dogfooding narrative)
- Proof of concept for future customers

---

## 3. User Stories

### As an AI Assistant Developer

**Story 1:** Import Path Verification
```
As an AI assistant,
When a user asks "How do I import the trace decorator?",
I need to retrieve the exact import path from source code,
So that I generate code that runs without ImportError.

Acceptance Criteria:
- Search source code index for "trace decorator"
- Return: from honeyhive import trace
- Cite source: src/honeyhive/__init__.py
- Accuracy: 100% (zero hallucination)
```

**Story 2:** API Reference Lookup
```
As an AI assistant,
When a user asks "What parameters does HoneyHiveTracer.init accept?",
I need to retrieve the exact function signature with types,
So that I generate code with correct parameter names.

Acceptance Criteria:
- Tool: get_api_reference("HoneyHiveTracer.init")
- Return: Full signature (16 parameters + types + defaults)
- Cite source: docs/reference/api/tracer.rst + src/honeyhive/tracer/core/tracer.py
- Accuracy: >99%
```

**Story 3:** Example-Based Learning
```
As an AI assistant,
When a user asks "Show me Anthropic streaming integration",
I need to find working code examples,
So that I provide copy-paste-ready code.

Acceptance Criteria:
- Tool: search_examples(query="anthropic streaming")
- Return: examples/integrations/anthropic.py (full file)
- Context: Includes imports, error handling, best practices
- Accuracy: Code runs without modification
```

### As a Developer Using AI Assistant

**Story 4:** Real-Time Knowledge
```
As a developer,
When I add a new method to the tracer,
I need the AI to be aware within 10 seconds,
So that I can immediately ask AI about my new code.

Acceptance Criteria:
- Watchdog detects file change
- Incremental index update completes
- AI query returns new method signature
- Latency: <10 seconds from file save
```

**Story 5:** Concurrent Development
```
As a developer,
When the index is rebuilding (hot reload),
I need my AI queries to still work,
So that I don't experience workflow disruption.

Acceptance Criteria:
- Query during rebuild: Wait up to 30s for completion
- Query returns results or graceful error
- No file corruption
- No "file not found" crashes
```

---

## 4. Functional Requirements

### FR-1: Semantic Search

**Requirement:** Provide semantic search over 5 knowledge sources with metadata filtering and intelligent ranking.

**Knowledge Sources:**
1. Local SDK Docs (Sphinx RST/HTML) - 70 RST + 79 HTML files
2. HoneyHive Mintlify Docs (MDX/markdown) - Public platform documentation
3. Python Source Code (src/honeyhive/) - 74 files, ~28K lines
4. Examples Directory (examples/) - ~20 working integration examples
5. OpenTelemetry Docs - Curated subset (tracing, Python SDK, OTLP)

**Capabilities:**
- Semantic vector search (sentence-transformers embeddings)
- Metadata filtering (source, doc_type, provider, language)
- 5-factor ranking (semantic similarity + doc type + source + recency + query boosts)
- Keyword search fallback (grep) on semantic search failure

### FR-2: MCP Tools

**Requirement:** Provide 4 MCP tools for structured knowledge access.

**Tool 1: search_docs**
- Parameters: query (str), filters (dict), top_k (int)
- Returns: List of SearchResult with content, source, metadata
- Use case: General semantic search

**Tool 2: get_api_reference**
- Parameters: symbol_name (str), include_examples (bool)
- Returns: APIReference with signature, parameters, docstring, source
- Use case: Function/class signature lookup

**Tool 3: get_integration_guide**
- Parameters: provider (str)
- Returns: IntegrationGuide with setup, code examples, best practices
- Use case: Provider-specific integration patterns

**Tool 4: search_examples**
- Parameters: query (str), provider (str, optional)
- Returns: List of ExampleFile with full code, imports, description
- Use case: Find working code examples

### FR-3: Hot Reload

**Requirement:** Automatically detect file changes and update index incrementally.

**Capabilities:**
- Watchdog monitors: docs/, src/honeyhive/, examples/
- Debounce changes (5s window to batch multiple saves)
- Incremental updates (LanceDB upserts)
- Concurrency-safe rebuild (lock + event signal)
- Target latency: <10 seconds from file save to index availability

### FR-4: Periodic Sync

**Requirement:** Sync external knowledge sources on a schedule.

**Sources:**
- Mintlify Docs: Git pull daily
- OTEL Docs: HTTP fetch weekly

### FR-5: Modular Architecture (🆕 V2.1 - agent-os-enhanced pattern)

**Requirement:** MCP server must be organized into domain-specific modules following production-grade patterns.

**Architecture Modules:**
- `models/` - Type-safe dataclasses (config.py, docs.py, sources.py)
- `config/` - Configuration management (loader.py, validator.py)
- `monitoring/` - File watching for hot reload (watcher.py)
- `server/` - Server factory and tool registration (factory.py, tools/)
- `core/` - Business logic (rag_engine.py, parsers/)

**Acceptance Criteria:**
- [ ] All files <200 lines (maintainability)
- [ ] Clear module boundaries (domain-driven design)
- [ ] Dependency injection throughout (ServerFactory pattern)
- [ ] No hardcoded paths or scattered configuration
- [ ] Module execution via `python -m honeyhive_sdk_docs`

**Rationale:** Following agent-os-enhanced modular refactor for sustainability and standards compliance.

### FR-6: Tool Scalability & Performance Monitoring (🆕 V2.1)

**Requirement:** Support selective tool loading with performance monitoring to avoid LLM degradation.

**Research Basis:** Microsoft Research shows LLM performance degrades by up to 85% with >20 tools.

**Implementation:**
- Tools organized by category (search_tools, reference_tools)
- Selective loading via config (enabled_tool_groups)
- Tool count monitoring and warning at startup
- Performance threshold: 20 tools max

**Acceptance Criteria:**
- [ ] Tools can be enabled/disabled via `config.json`
- [ ] Tool count logged at server startup
- [ ] Warning issued if tool count >20
- [ ] Future sub-agent tools can be added without code changes

**Configuration:**
```json
{
  "docs_mcp": {
    "enabled_tool_groups": ["search", "reference"],
    "max_tools_warning": 20
  }
}
```

**Capabilities:**
- Background thread for sync
- Failure tolerance (use cached version on error)
- Last-sync timestamp tracking

### FR-5: Concurrency Safety (CRITICAL)

**Requirement:** Handle concurrent queries and index rebuilds without corruption.

**Mechanisms** (from Agent OS MCP lessons learned):
- `threading.RLock()` protects index access
- `threading.Event()` signals rebuild state
- Query waits (up to 30s) during rebuild
- Clean connection cleanup before rebuild
- Explicit `del self.table; del self.db` before reconnect

**Rationale:** LanceDB 0.25.x does NOT handle concurrent read+write internally. Without locking, queries during rebuild cause "file not found" errors and index corruption.

### FR-6: Graceful Degradation

**Requirement:** Never crash—always provide best-effort results or helpful errors.

**Degradation Paths:**
- Semantic search fails → Keyword search fallback (grep)
- Mintlify clone fails → Use cached version + log warning
- OTEL fetch fails → Skip, use local docs only
- Index corrupted → Auto-rebuild from source
- Embedding model fails → Fall back to keyword search

### FR-7: HoneyHive Tracing

**Requirement:** Trace all MCP tool calls with HoneyHive SDK for observability and dogfooding.

**Span Enrichment:**
- Query text
- Number of results returned
- Sources searched
- Latency breakdown (embedding time, search time, ranking time)
- Session metadata: mcp_server=honeyhive-sdk-docs-v2

**Purpose:** Validate HoneyHive SDK for AI infrastructure, analyze query patterns, optimize retrieval accuracy.

---

## 5. Non-Functional Requirements

### NFR-1: Performance

**Search Latency:**
- Target: <100ms P50, <250ms P99
- Timeout: 5 seconds (graceful error after)

**Index Build Time:**
- Full rebuild: <5 minutes (all sources)
- Incremental update: <10 seconds (single file change)
- Hot reload debounce: 5 seconds (batch changes)

**Index Size:**
- Target: <500MB (compressed embeddings)
- Per-source estimates:
  - Local docs: ~50MB
  - Mintlify: ~100MB
  - Source code: ~75MB
  - Examples: ~10MB
  - OTEL: ~100MB

### NFR-2: Reliability

**Availability:**
- Target: 99.9% uptime (development environment)
- Zero crashes from race conditions
- Zero index corruption incidents

**Error Handling:**
- All parsers wrapped in try-except
- Log errors, continue processing
- Validate embeddings before storage
- Never propagate parser exceptions to MCP layer

### NFR-3: Maintainability

**Code Quality:**
- Pylint: 10.0/10 score (non-negotiable)
- MyPy: 0 errors (strict type checking)
- Docstrings: 100% coverage (Sphinx format)
- Unit tests: >80% coverage

**Documentation:**
- README.md: Setup, usage, troubleshooting
- Architecture diagrams: Mermaid format
- Inline comments: Explain non-obvious logic (especially concurrency)

### NFR-4: Security

**Credential Handling:**
- No API keys in code (use .env file)
- GitHub token for Mintlify (optional, read-only)
- Never commit .env or credentials

**Input Validation:**
- Sanitize query inputs (prevent injection)
- Validate file paths (prevent directory traversal)
- Rate limiting: TBD (if exposed beyond local use)

### NFR-5: Observability

**Logging:**
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log rotation: 100MB max per file

**Metrics:**
- Query count per source
- Average latency per source
- Index rebuild frequency
- Cache hit rate (if caching implemented)

### NFR-6: Configuration Management (🆕 V2.1 - agent-os-enhanced pattern)

**Requirement:** Configuration via JSON file with type-safe dataclass models, NOT environment variables.

**Rationale:** Following agent-os-enhanced modular refactor:
- **Single source of truth** (not scattered .env vars)
- **Type-safe** with dataclass validation
- **Graceful fallback** to defaults
- **Testable** (can mock ServerConfig)
- **Portable** across environments

**Pattern** (see Section 8 for full implementation):
```python
# .praxis-os/config.json (user editable)
{
  "docs_mcp": {
    "index_path": ".mcp_cache/docs_index",
    "embedding_provider": "local",
    "hot_reload_enabled": true,
    "knowledge_sources": {
      "local_docs": "docs/",
      "source_code": "src/honeyhive/"
    }
  },
  "honeyhive_tracing": {
    "enabled": true,
    "project": "mcp-servers"
  }
}

# models/config.py (type-safe dataclass)
@dataclass
class DocsConfig:
    """Docs MCP configuration with validated defaults."""
    index_path: str = ".mcp_cache/docs_index"
    embedding_provider: str = "local"
    hot_reload_enabled: bool = True
    # ... (see implementation.md for full model)
```

### NFR-7: Modular Architecture & Maintainability (🆕 V2.1)

**Requirement:** All files must be <200 lines with clear module boundaries and single responsibility.

**Rationale:** Following Agent OS production code standards and agent-os-enhanced pattern:
- Files >200 lines become unmaintainable
- Modular structure enables testing and extensibility
- Domain-driven design improves code discoverability

**File Size Limits:**
- Core modules: <200 lines each
- Tool modules: <150 lines each
- Configuration modules: <100 lines each

**Module Boundaries:**
- `models/` - Data models only, no business logic
- `config/` - Configuration loading/validation only
- `server/` - Server creation and tool registration only
- `core/` - Business logic only (RAG, parsers, etc.)

### NFR-8: Dependency Management (CRITICAL)

**Requirement:** Pin all dependencies with explicit version ranges and justifications.

**Rationale:** Loose version specs (`lancedb>=0.3.0`) allow non-deterministic builds, leading to bugs. Agent OS MCP bug was caused by version drift.

**Specifications** (see Section 8 for full list):
```python
lancedb~=0.25.0          # 0.24.x had race condition bugs, 0.25.x adds safety
sentence-transformers~=2.2.0  # 2.2.x added M1/M2 optimization
fastmcp>=1.0.0           # FastMCP framework (same as agent-os-enhanced)
watchdog~=3.0.0          # Stable, follows SemVer
# ... (see Section 8.1 for complete list with justifications)
```

---

## 6. Out-of-Scope Items

**Explicitly excluded from this version:**

❌ **Provider-Specific Docs (OpenAI, Anthropic, etc.)**
- Rationale: Abstracted via instrumentors/non-framework integrations
- Alternative: Users reference provider docs directly if needed

❌ **GitHub Issues/Discussions**
- Rationale: Historical context, not reference documentation
- Future: May add if pattern emerges

❌ **CHANGELOG/README Indexing**
- Rationale: Better suited for Agent OS standards MCP
- These are project-agnostic (not SDK API-specific)

❌ **Test Files as Examples**
- Rationale: Tests are for validation, not user guidance
- Examples directory provides better user-facing patterns

❌ **Workflow Integration (Phase 1)**
- Rationale: Focus on RAG search first, add workflows in future iteration
- See SPEC_IMPROVEMENTS_ANALYSIS.md for workflow design (deferred)

---

## 7. Success Criteria

### 7.1 Quantitative Metrics

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| **Import Path Hallucination** | 30% error rate | <1% error rate | 100 test queries, validate accuracy |
| **Parameter Accuracy** | 60% correct | >99% correct | Validate against actual API signatures |
| **Context Efficiency** | 4,000 tokens avg | <500 tokens avg | Token count in MCP search results |
| **Search Latency (P50)** | N/A | <100ms | Benchmark 100 queries |
| **Search Latency (P99)** | N/A | <250ms | Benchmark 100 queries |
| **Full Index Build** | N/A | <5 minutes | Time all sources indexing |
| **Incremental Update** | N/A | <10 seconds | Single file change → index ready |
| **Real-Time Knowledge** | Months lag | <10 seconds | File save → query returns new content |
| **Concurrent Access Safety** | Crashes | Zero crashes | 50 queries during rebuild, zero errors |

### 7.2 Qualitative Outcomes

**AI Behavior Changes:**
- ✅ AI prefixes answers: "According to docs/reference/api/tracer.rst..."
- ✅ AI provides exact code snippets from examples
- ✅ AI corrects user misconceptions with doc citations
- ✅ AI asks clarifying questions when multiple approaches exist

**Developer Experience:**
- ✅ Zero time copy-pasting docs into prompts
- ✅ Confidence in AI-generated code (provenance)
- ✅ Faster iteration (no manual doc lookup)
- ✅ Reduced frustration (fewer hallucination bugs)
- ✅ No workflow disruption during index rebuilds

**Human Orchestration Quality:**
- ✅ Human focuses on: Architecture, requirements, validation
- ✅ Human freed from: Fact-checking imports, parameter names, doc lookup
- ✅ Paradigm shift: From "verify everything" to "trust and spot-check"

### 7.3 Production Code Checklist Evidence

**Requirement:** Systematic application of CS fundamentals per Agent OS production code checklist.

**Evidence Required** (see Section 11 in specs.md):
- [ ] Shared state concurrency analysis complete
- [ ] Dependency version pinning with justifications
- [ ] Failure mode analysis for all external dependencies
- [ ] Resource lifecycle management documented
- [ ] Concurrent access tests written and passing

---

## 8. Risks & Mitigations

### Risk 1: Race Conditions in Hot Reload

**Risk:** Query thread reads index while rebuild thread modifies → file corruption  
**Likelihood:** High (without mitigation)  
**Impact:** Critical (index corruption, crashes)

**Mitigation:**
- threading.RLock() for index access
- threading.Event() for rebuild state
- Query waits (up to 30s) during rebuild
- Clean connection cleanup (del self.table, del self.db)
- Concurrent access tests (50 queries during rebuild)

**Status:** ✅ Addressed in V2 (learned from Agent OS MCP bug)

### Risk 2: Version Drift in Dependencies

**Risk:** Loose version specs allow breaking changes  
**Likelihood:** Medium  
**Impact:** High (non-deterministic builds, subtle bugs)

**Mitigation:**
- Pin all dependencies with `~=` (lock to minor version)
- Justify every version choice
- Document why versions are pinned
- Test on clean environment

**Status:** ✅ Addressed in V2 (see Section 8.1 in implementation.md)

### Risk 3: Mintlify Repo Access

**Risk:** HoneyHive docs repo may be private  
**Likelihood:** Low  
**Impact:** Medium

**Mitigation:**
- Use read-only GitHub token
- Fallback: Scrape public Mintlify site
- Graceful degradation: Use local docs only

**Status:** ⚠️ Investigate during Phase 3

### Risk 4: Index Size Explosion

**Risk:** Full OTEL docs = 500MB+ embeddings  
**Likelihood:** Medium  
**Impact:** Low

**Mitigation:**
- Curate OTEL subset (tracing only)
- Use compressed embeddings
- Monitor index size, prune if needed

**Status:** ⚠️ Monitor during Phase 3

### Risk 5: Embedding Model Bias

**Risk:** sentence-transformers may not understand code syntax  
**Likelihood:** Medium  
**Impact:** Medium

**Mitigation:**
- Hybrid search (embedding + keyword)
- Test retrieval accuracy
- Keyword search fallback on low confidence

**Status:** ⚠️ Test during Phase 4

### Risk 6: Duplicate Content

**Risk:** Source docstrings = Sphinx autodoc = duplicate chunks  
**Likelihood:** High  
**Impact:** Low

**Mitigation:**
- Content-based deduplication (hash)
- Prioritize source ranking (mintlify > local_docs > source_code)

**Status:** ⚠️ Implement during Phase 3

---

## 9. Dependencies

### 9.1 External Dependencies

**Critical:**
- LanceDB ~=0.25.0 (vector database)
- sentence-transformers ~=2.2.0 (local embeddings)
- watchdog ~=3.0.0 (file watching)
- fastmcp >=1.0.0 (FastMCP server framework - same as agent-os-enhanced)

**Required:**
- beautifulsoup4 ~=4.12.0 (HTML parsing)
- markdown >=3.4.0,<4.0.0 (Markdown parsing)
- gitpython ~=3.1.0 (Git operations)
- requests ~=2.31.0 (HTTP fetching)

**Internal:**
- honeyhive >=0.1.0 (tracing dogfooding - optional, via env var check)

### 9.2 Internal Dependencies

- **Configuration**: `.praxis-os/config.json` (single source of truth)
- **Cursor Integration**: `.cursor/mcp.json` with `${workspaceFolder}` variables
- **Module Execution**: Python `-m honeyhive_sdk_docs` pattern
- **Virtual Environment**: Project-specific venv in `.mcp_servers/honeyhive_sdk_docs_v2/venv/`

### 9.3 Development Dependencies

- pytest (unit testing)
- pylint + mypy (code quality)
- black + isort (formatting)
- pytest-cov (coverage reporting)

---

## 10. Timeline Estimate

**Specification Phase:** 1 day (this document + supporting analysis)

**Implementation Phase:** 3-5 days (systematic AI authorship)
- Phase 1 (Foundation): 1 day
- Phase 2 (Local Sources): 1 day
- Phase 3 (External Sources): 1 day
- Phase 4 (MCP Tools & Search): 0.5 day
- Phase 5 (Quality & Operations): 0.5 day

**Total:** ~5 days (following Agent OS MCP reference, enhanced with V2 improvements)

---

## 11. Approval & Next Steps

### Approval Gate

**🛑 CRITICAL:** Implementation cannot begin until:
1. ✅ This SRD reviewed and approved
2. ✅ specs.md (architecture) reviewed and approved
3. ✅ tasks.md (implementation plan) reviewed and approved
4. ✅ Success criteria confirmed measurable
5. ✅ Timeline and resource allocation approved

### Next Steps

1. ⏭️ Author specs.md (architecture & design)
2. ⏭️ Author tasks.md (implementation breakdown)
3. ⏭️ Author implementation.md (technical details)
4. ⏭️ Author README.md (executive summary)
5. ⏭️ Begin Phase 1 implementation upon approval

---

## 12. Document Metadata

**Authorship:** 100% AI-authored via human orchestration  
**Review Status:** Awaiting human approval  
**Version:** 2.0 (Production-Hardened with Agent OS MCP Lessons)  
**Related Documents:**
- Original V1 Spec: `.praxis-os/specs/2025-10-04-honeyhive-sdk-docs-mcp/`
- Critical Gaps Analysis: `supporting-docs/VALIDATION.md`
- Improvements Analysis: `supporting-docs/SPEC_IMPROVEMENTS_ANALYSIS.md`

**Key Improvements Over V1:**
1. ✅ Concurrency safety strategy (threading.RLock + Event)
2. ✅ Version pinning with justifications
3. ✅ Connection cleanup strategy
4. ✅ Concurrent access testing requirements
5. ✅ Failure mode analysis
6. ✅ Production code checklist application


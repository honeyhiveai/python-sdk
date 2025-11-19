# RAG Architecture Design
# Agent OS MCP/RAG Evolution

**Document Version:** 1.0  
**Date:** October 3, 2025  
**Status:** Draft - Specification Phase

---

## PURPOSE

This document details the **RAG (Retrieval-Augmented Generation) architecture** for Agent OS, including vector store design, chunking strategy, and retrieval mechanisms.

---

## ARCHITECTURE OVERVIEW

```
Query: "Phase 1 method verification requirements"
    │
    ▼
┌─────────────────────────────────────────────────┐
│ RAG Engine                                      │
│ ┌─────────────────────────────────────────────┐ │
│ │ 1. Query Understanding                      │ │
│ │    - Detect phase number (1)               │ │
│ │    - Identify intent (requirements)        │ │
│ │    - Extract filters (phase=1)             │ │
│ └─────────────────────────────────────────────┘ │
│           │                                      │
│           ▼                                      │
│ ┌─────────────────────────────────────────────┐ │
│ │ 2. Embedding Generation                     │ │
│ │    - OpenAI text-embedding-3-small         │ │
│ │    - 1536-dimensional vector               │ │
│ └─────────────────────────────────────────────┘ │
│           │                                      │
│           ▼                                      │
│ ┌─────────────────────────────────────────────┐ │
│ │ 3. Vector Search (ChromaDB)                │ │
│ │    - Cosine similarity search              │ │
│ │    - Metadata filtering (phase=1)          │ │
│ │    - Top-K retrieval (K=5)                 │ │
│ └─────────────────────────────────────────────┘ │
│           │                                      │
│           ▼                                      │
│ ┌─────────────────────────────────────────────┐ │
│ │ 4. Result Ranking                          │ │
│ │    - Relevance scoring                     │ │
│ │    - Critical content boosting             │ │
│ │    - Deduplication                         │ │
│ └─────────────────────────────────────────────┘ │
│           │                                      │
│           ▼                                      │
│ ┌─────────────────────────────────────────────┐ │
│ │ 5. Response Assembly                       │ │
│ │    - Combine chunks                        │ │
│ │    - Add source citations                  │ │
│ │    - Return structured result              │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
    │
    ▼
Result: {
  chunks: [relevant phase 1 content...],
  total_tokens: 1500,
  retrieval_method: "vector",
  relevance_scores: [0.95, 0.93, 0.89]
}
```

---

## CHUNKING STRATEGY

### Principles

1. **Preserve Semantic Boundaries:** Never split mid-paragraph or mid-code block
2. **Maintain Context:** Include parent headers in metadata
3. **Optimal Size:** 100-500 tokens per chunk (balance specificity vs context)
4. **Stable IDs:** MD5 hash for consistent chunk identification

### Chunking Algorithm

```python
def chunk_document(filepath: Path) -> List[DocumentChunk]:
    """
    Chunk document preserving semantic boundaries.
    
    Steps:
    1. Parse by ## headers (primary sections)
    2. For each section:
       a. If < 500 tokens → single chunk
       b. If > 500 tokens:
          i.  Try splitting on ### sub-headers
          ii. If still large, split on paragraphs
          iii. If still large, split on sentences (preserve code blocks)
    3. Attach metadata to each chunk
    4. Generate stable chunk ID (MD5)
    """
```

### Example Chunking Result

**Input:** `TEST_GENERATION_MANDATORY_FRAMEWORK.md` (15,000 tokens)

**Output:** ~40 chunks

| Chunk ID | Section | Tokens | Metadata |
|----------|---------|--------|----------|
| abc123... | Phase 1 - Header + Overview | 450 | phase=1, is_critical=True |
| def456... | Phase 1 - Commands | 320 | phase=1, tags=[ast] |
| ghi789... | Phase 1 - Checkpoint | 380 | phase=1, is_critical=True |
| jkl012... | Phase 2 - Header + Overview | 420 | phase=2, tags=[logging] |
| ... | ... | ... | ... |

---

## VECTOR STORE DESIGN

### ChromaDB Configuration

```python
# Using SQLite backend for local persistence
client = chromadb.PersistentClient(
    path=".praxis-os/.cache/vector_index",
    settings=Settings(
        anonymized_telemetry=False,  # No external calls
        allow_reset=True             # For rebuilds
    )
)

# Collection configuration
collection = client.get_or_create_collection(
    name="agent_os_standards",
    metadata={
        "description": "Agent OS Standards and Frameworks",
        "hnsw:space": "cosine",        # Cosine similarity
        "hnsw:construction_ef": 100,   # Index build quality
        "hnsw:search_ef": 50           # Query quality
    }
)
```

### Metadata Schema

```python
chunk_metadata = {
    # File information
    "file_path": str,              # Source file
    "section_header": str,         # Header this chunk belongs to
    
    # Content classification
    "framework_type": str,         # "test_v3", "production_v2", etc.
    "phase": int,                  # Phase number (1-8, or -1 if not phase-specific)
    "category": str,               # "requirement", "example", "reference"
    "tags": str,                   # Comma-separated: "mocking,ast,coverage"
    
    # Retrieval hints
    "is_critical": bool,           # Contains MANDATORY/CRITICAL markers
    "tokens": int,                 # Token count
    
    # Versioning
    "chunk_id": str,               # MD5 hash (stored as ID, not metadata)
    "indexed_at": str              # ISO timestamp
}
```

---

## EMBEDDING STRATEGY

### Primary: OpenAI Embeddings

```python
def generate_embedding_openai(text: str) -> List[float]:
    """
    Generate embedding using OpenAI.
    
    Model: text-embedding-3-small
    Dimensions: 1536
    Cost: ~$0.00002 per 1K tokens
    
    For 198 files → ~200K tokens → $0.004 per index build
    """
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

### Fallback: Local Embeddings (Future)

```python
def generate_embedding_local(text: str) -> List[float]:
    """
    Generate embedding using local model.
    
    Model: sentence-transformers/all-MiniLM-L6-v2
    Dimensions: 384
    Cost: Free, but slower
    
    Not implemented in Phase 1, reserved for Phase 2+ enhancement.
    """
```

---

## RETRIEVAL MECHANISMS

### Primary: Vector Search

```python
def vector_search(
    query: str,
    n_results: int = 5,
    filters: Optional[Dict] = None
) -> SearchResult:
    """
    Semantic search using vector similarity.
    
    Steps:
    1. Generate query embedding
    2. Search ChromaDB with cosine similarity
    3. Apply metadata filters
    4. Return top N results with scores
    """
    # Generate query embedding
    query_embedding = generate_embedding(query)
    
    # Build metadata filter
    where_filter = build_where_filter(filters)
    
    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results * 2,  # Get 2x, then filter/rank
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )
    
    # Post-process
    chunks = post_process_results(results)
    
    return SearchResult(
        chunks=chunks[:n_results],
        total_tokens=sum(c.tokens for c in chunks[:n_results]),
        retrieval_method="vector",
        relevance_scores=[1 - d for d in results["distances"][0]],
        query_time_ms=measure_time()
    )

def build_where_filter(filters: Dict) -> Dict:
    """Build ChromaDB where clause from filters."""
    where = {}
    
    if filters.get("phase"):
        where["phase"] = filters["phase"]
    
    if filters.get("framework_type"):
        where["framework_type"] = filters["framework_type"]
    
    if filters.get("is_critical"):
        where["is_critical"] = True
    
    return where
```

### Fallback: Grep Search

```python
def grep_fallback(query: str, n_results: int = 5) -> SearchResult:
    """
    Fallback to grep if vector search fails.
    
    Uses ripgrep for fast text search with context.
    """
    import subprocess
    
    # Run ripgrep
    result = subprocess.run(
        ["rg", query, ".praxis-os/standards", "-C", "3"],
        capture_output=True,
        text=True
    )
    
    # Parse results into chunks
    chunks = parse_grep_results(result.stdout)
    
    return SearchResult(
        chunks=chunks[:n_results],
        total_tokens=sum(count_tokens(c.content) for c in chunks[:n_results]),
        retrieval_method="grep",
        relevance_scores=[1.0] * len(chunks),  # No scoring in grep
        query_time_ms=measure_time()
    )
```

---

## RESULT RANKING

### Ranking Algorithm

```python
def rank_results(results: List[DocumentChunk]) -> List[DocumentChunk]:
    """
    Rank results with critical content boosting.
    
    Scoring:
    - Base score: Vector similarity (0-1)
    - Critical boost: +0.2 if is_critical=True
    - Phase match boost: +0.1 if exact phase match
    - Recency boost: +0.05 if recently indexed
    """
    scored_results = []
    
    for chunk, similarity in results:
        score = similarity
        
        # Critical content boost
        if chunk.metadata.is_critical:
            score += 0.2
        
        # Phase match boost (if filtering by phase)
        if chunk.metadata.phase == filter_phase:
            score += 0.1
        
        scored_results.append((chunk, score))
    
    # Sort by score descending
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    return [chunk for chunk, score in scored_results]
```

---

## INDEX BUILD PROCESS

### Initial Build

```bash
# First time setup
python .praxis-os/scripts/build_rag_index.py

Steps:
1. Find all .md files in .praxis-os/standards/ (198 files)
2. Chunk each file (40 chunks/file → 7,920 chunks)
3. Generate embeddings (OpenAI, ~60 seconds)
4. Insert into ChromaDB (batches of 100)
5. Save metadata.json with hash of source files
6. Complete in < 60 seconds
```

### Incremental Updates

```python
def rebuild_if_needed():
    """Check if index is stale and rebuild."""
    metadata_file = Path(".praxis-os/.cache/vector_index/metadata.json")
    
    if not metadata_file.exists():
        # No index exists
        build_index()
        return
    
    # Load metadata
    metadata = json.loads(metadata_file.read_text())
    
    # Hash current standards
    current_hash = hash_directory(Path(".praxis-os/standards"))
    
    if current_hash != metadata["standards_hash"]:
        # Standards changed, rebuild
        print("Standards changed, rebuilding index...")
        build_index()
    else:
        print("Index up to date")
```

---

## PERFORMANCE OPTIMIZATION

### Caching Strategy

```python
class CachedRAGEngine:
    """RAG engine with LRU caching."""
    
    def __init__(self):
        self.query_cache = LRUCache(maxsize=100)  # Cache 100 recent queries
    
    def search(self, query: str, **kwargs) -> SearchResult:
        """Search with caching."""
        cache_key = (query, frozenset(kwargs.items()))
        
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Perform search
        result = self._search_impl(query, **kwargs)
        
        # Cache result
        self.query_cache[cache_key] = result
        
        return result
```

### Query Optimization

```python
optimization_strategies = {
    "pre_filter": "Apply metadata filters before vector search",
    "approximate_nn": "Use HNSW approximate nearest neighbor (ChromaDB default)",
    "batch_queries": "If multiple queries, batch embeddings API calls",
    "lazy_loading": "Don't load full index into memory, query on-disk",
    "result_limit": "Limit n_results to reasonable size (5-20)"
}
```

---

## MONITORING & OBSERVABILITY

### HoneyHive Instrumentation (Dogfooding)

**All RAG operations traced with HoneyHive:**

```python
from honeyhive import HoneyHiveTracer, trace, enrich_span
from honeyhive.models import EventType

class RAGEngine:
    """RAG engine with HoneyHive tracing."""
    
    def __init__(self, tracer: HoneyHiveTracer):
        self.tracer = tracer
        # ... other initialization
    
    @trace(tracer=lambda self: self.tracer, event_type=EventType.tool)
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> SearchResult:
        """
        Search with tracing for dogfooding.
        
        Using @trace decorator (recommended HoneyHive pattern):
        - Automatic input/output capture
        - Better error handling
        - Cleaner code vs manual context managers
        - Automatic context propagation
        """
        # Enrich span with additional metadata
        enrich_span({
            "rag.filters": filters,
            "rag.component": "rag_engine",
            "rag.n_results": n_results
        })
        
        # Core implementation
        result = self._search_impl(query, n_results, filters)
        
        # Enrich with result metadata
        enrich_span({
            "rag.chunks_returned": len(result.chunks),
            "rag.total_tokens": result.total_tokens,
            "rag.retrieval_method": result.retrieval_method,
            "rag.query_time_ms": result.query_time_ms,
            "rag.cache_hit": result.cache_hit
        })
        
        return result
```

**Why decorator pattern over context manager:**
- **Recommended by HoneyHive docs** - Decorator is the idiomatic approach
- **Cleaner code** - No nested indentation, more readable
- **Automatic capture** - Inputs/outputs captured automatically
- **Error handling** - Built-in exception capture and span status setting
- **Consistent with project** - Matches patterns in examples/ and docs/

**Dogfooding Benefits:**
- Validates HoneyHive works for AI agent workflows
- Provides insights into real AI query patterns
- Observes RAG performance in production
- Demonstrates product value to internal teams

### Query Metrics

```python
@dataclass
class QueryMetrics:
    """Metrics for each query (logged to HoneyHive)."""
    query: str
    n_results: int
    retrieval_method: str  # "vector" or "grep"
    query_time_ms: float
    chunks_returned: int
    total_tokens: int
    cache_hit: bool
    filters_applied: Dict
    timestamp: datetime
    honeyhive_trace_id: str  # For correlation
```

### Index Metrics

```python
@dataclass
class IndexMetrics:
    """Metrics for index state (logged to HoneyHive)."""
    total_chunks: int
    total_files: int
    index_size_mb: float
    last_build_time: datetime
    standards_hash: str
    embedding_provider: str
    honeyhive_session: str  # For tracing
```

---

## TESTING STRATEGY

### RAG Accuracy Testing

```python
# Define test query set
test_queries = [
    {
        "query": "Phase 1 method verification requirements",
        "expected_phase": 1,
        "expected_keywords": ["function", "method", "AST", "grep"],
        "min_relevance": 0.85
    },
    {
        "query": "How to determine mocking boundaries",
        "expected_tags": ["mocking"],
        "expected_keywords": ["boundary", "external", "stub"],
        "min_relevance": 0.80
    },
    # ... 50 total test queries
]

def test_retrieval_accuracy():
    """Test retrieval accuracy against expected results."""
    correct = 0
    total = len(test_queries)
    
    for test in test_queries:
        result = rag_engine.search(test["query"])
        
        # Check if expected content retrieved
        if all(kw in result.chunks[0].content for kw in test["expected_keywords"]):
            correct += 1
    
    accuracy = correct / total
    assert accuracy >= 0.90, f"Accuracy {accuracy:.2%} below 90% target"
```

---

## SUCCESS CRITERIA

**RAG system succeeds when:**

✅ 90%+ retrieval accuracy on test query set  
✅ < 100ms p95 query latency  
✅ < 60 seconds initial index build  
✅ Graceful fallback to grep on failures  
✅ Automatic index rebuild on content changes  
✅ < 100MB memory overhead

---

**Document Status:** Complete - Ready for Review  
**Next Document:** testing-strategy.md (Final document)  
**Purpose:** RAG architecture and vector store design  
**Key Innovation:** Semantic retrieval with workflow-aware filtering


# Agent OS RAG + MCP Architecture
**Date:** 2025-10-03  
**Status:** Proposed  
**Priority:** High  
**Category:** Agent OS Enhancement

## Executive Summary

Transform Agent OS from "RAG-lite" (keyword-triggered full-file reads) to proper RAG (semantic search with chunked retrieval) using MCP as the infrastructure layer.

## Problem Statement

### Current State: RAG-lite
```
User Query → Keyword Match → Read Full File (50KB) → Extract Relevant (2KB) → Use
Efficiency: ~4%
Context Cost: 50KB per query
```

**Limitations:**
- No semantic understanding (keyword-only triggers)
- Inefficient (load entire files for small answers)
- Not scalable (198 files = potential 10MB+ context)
- Static routing (can't adapt to novel queries)
- No ranking (can't prioritize most relevant content)

### Desired State: Proper RAG
```
User Query → Semantic Search → Retrieve Chunks (2KB) → Rank → Use
Efficiency: ~100%
Context Cost: 2KB per query
```

---

## Solution Overview

### Three-Layer RAG Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Cursor AI Assistant (Consumer)               │
│  - Generates semantic queries                           │
│  - Calls MCP tools for retrieval                        │
│  - Uses retrieved chunks in responses                   │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol
┌────────────────────▼────────────────────────────────────┐
│  Layer 2: MCP Server (Interface)                        │
│  - Exposes RAG tools via MCP protocol                   │
│  - Handles query routing and tool execution             │
│  - Provides structured responses                        │
└────────────────────┬────────────────────────────────────┘
                     │ Internal API
┌────────────────────▼────────────────────────────────────┐
│  Layer 3: RAG Engine (Intelligence)                     │
│  - Vector embeddings (OpenAI/local)                     │
│  - Semantic search over Agent OS content                │
│  - Chunk ranking and relevance scoring                  │
│  - Cache frequently accessed content                    │
└─────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Data Layer: Agent OS Knowledge Base                    │
│  - 198 markdown files in .praxis-os/                     │
│  - Indexed and chunked                                  │
│  - Metadata: tags, categories, update dates             │
└─────────────────────────────────────────────────────────┘
```

---

## Technical Architecture

### Component 1: Document Preprocessing

**Chunking Strategy:**
```python
from typing import List, Dict
import hashlib

class AgentOSChunker:
    """Intelligent chunking for Agent OS documentation."""
    
    def chunk_document(self, filepath: str) -> List[Dict]:
        """
        Chunk markdown files with context preservation.
        
        Strategy:
        - Split on ## headers (natural semantic boundaries)
        - Keep chunks 300-500 tokens
        - Preserve parent headers for context
        - Add metadata (file path, section, tags)
        """
        content = read_file(filepath)
        sections = self._split_on_headers(content)
        
        chunks = []
        for section in sections:
            if len(section.tokens) > 500:
                # Further split large sections
                sub_chunks = self._split_by_paragraphs(section, target=400)
                chunks.extend(sub_chunks)
            else:
                chunks.append(section)
        
        # Add metadata to each chunk
        for chunk in chunks:
            chunk.metadata = {
                "file": filepath,
                "section": chunk.header,
                "tags": self._extract_tags(chunk),
                "category": self._infer_category(filepath),
                "hash": hashlib.md5(chunk.content.encode()).hexdigest()
            }
        
        return chunks
    
    def _extract_tags(self, chunk) -> List[str]:
        """Extract semantic tags from chunk."""
        tags = []
        
        # Detect mandatory/critical content
        if "MANDATORY" in chunk.content or "CRITICAL" in chunk.content:
            tags.append("critical")
        
        # Detect topic
        if "test" in chunk.content.lower():
            tags.append("testing")
        if "git" in chunk.content.lower():
            tags.append("git")
        if "quality" in chunk.content.lower():
            tags.append("quality")
            
        return tags
```

---

### Component 2: Vector Store

**Embedding Strategy:**
```python
from typing import List
import chromadb
from openai import OpenAI

class AgentOSVectorStore:
    """Vector store for semantic search over Agent OS."""
    
    def __init__(self, persist_directory: str = ".praxis-os/.cache/chroma"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="agent_os_standards",
            metadata={"description": "Agent OS standards and frameworks"}
        )
        self.openai = OpenAI()
    
    def index_chunks(self, chunks: List[Dict]):
        """Index chunked documents with embeddings."""
        for chunk in chunks:
            # Generate embedding
            embedding = self.openai.embeddings.create(
                input=chunk["content"],
                model="text-embedding-3-small"  # 1536 dimensions, cheap
            ).data[0].embedding
            
            # Store in vector DB
            self.collection.add(
                ids=[chunk["metadata"]["hash"]],
                embeddings=[embedding],
                documents=[chunk["content"]],
                metadatas=[chunk["metadata"]]
            )
    
    def semantic_search(
        self,
        query: str,
        n_results: int = 5,
        filter_tags: List[str] = None
    ) -> List[Dict]:
        """Semantic search with optional tag filtering."""
        # Generate query embedding
        query_embedding = self.openai.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        ).data[0].embedding
        
        # Build filter
        where_filter = {}
        if filter_tags:
            where_filter["tags"] = {"$in": filter_tags}
        
        # Query vector store
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter if where_filter else None
        )
        
        return self._format_results(results)
```

---

### Component 3: MCP Server

**MCP Tool Implementation:**
```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio

class AgentOSMCPServer:
    """MCP server exposing Agent OS as RAG tools."""
    
    def __init__(self):
        self.server = Server("agent-os-rag")
        self.vector_store = AgentOSVectorStore()
        self.register_tools()
    
    def register_tools(self):
        """Register MCP tools for Agent OS access."""
        
        @self.server.tool()
        async def pos_search_project(action="search_standards", query=
            query: str,
            n_results: int = 5,
            category: str = None
        ) -> dict:
            """
            Semantic search over Agent OS standards.
            
            Args:
                query: Natural language question or topic
                n_results: Number of relevant chunks to return
                category: Optional filter (testing, git, quality, etc.)
            
            Returns:
                {
                    "results": [
                        {
                            "content": "chunk text...",
                            "file": ".praxis-os/standards/...",
                            "section": "header name",
                            "relevance_score": 0.95
                        }
                    ],
                    "total_tokens": 2500
                }
            """
            filter_tags = [category] if category else None
            results = self.vector_store.semantic_search(
                query=query,
                n_results=n_results,
                filter_tags=filter_tags
            )
            
            return {
                "results": results,
                "total_tokens": sum(r["tokens"] for r in results)
            }
        
        @self.server.tool()
        async def validate_operation(
            operation_type: str,
            details: dict
        ) -> dict:
            """
            Validate operation against Agent OS rules.
            
            Args:
                operation_type: git, file_write, test_generation, etc.
                details: Operation-specific parameters
            
            Returns:
                {
                    "allowed": bool,
                    "violations": [...],
                    "guidance": "...",
                    "relevant_standards": [...]
                }
            """
            # Search for relevant rules
            query = f"{operation_type} rules and requirements"
            rules = self.vector_store.semantic_search(query, n_results=3)
            
            # Apply validation logic
            result = self._validate_against_rules(operation_type, details, rules)
            
            return result
        
        @self.server.tool()
        async def get_framework(
            framework_type: str,
            detail_level: str = "summary"
        ) -> dict:
            """
            Retrieve specific framework content.
            
            Args:
                framework_type: test_v2, production_v2, etc.
                detail_level: summary, full, checklist
            
            Returns:
                Framework content optimized for detail level
            """
            if detail_level == "summary":
                # Return condensed overview
                query = f"{framework_type} framework core requirements"
                chunks = self.vector_store.semantic_search(query, n_results=3)
            elif detail_level == "full":
                # Return complete framework
                file_map = {
                    "test_v2": ".praxis-os/standards/ai-assistant/code-generation/tests/v2/framework-core.md",
                    "production_v2": ".praxis-os/standards/ai-assistant/code-generation/production/v2/framework-core.md"
                }
                content = read_file(file_map[framework_type])
                return {"content": content, "type": "full"}
            
            return {"chunks": chunks, "type": detail_level}
        
        @self.server.tool()
        async def get_quality_targets(
            context: str = "general"
        ) -> dict:
            """
            Get quality targets for current context.
            
            Args:
                context: test, production, documentation, etc.
            
            Returns:
                {
                    "targets": {
                        "coverage": "90%+",
                        "pylint": "10.0/10",
                        ...
                    },
                    "rationale": "...",
                    "enforcement": "..."
                }
            """
            query = f"{context} quality targets and requirements"
            results = self.vector_store.semantic_search(query, n_results=2)
            
            return self._parse_quality_targets(results)
```

---

### Component 4: Cursor Integration

**Updated .cursorrules (lightweight):**
```yaml
# .cursorrules (~5KB instead of current ~10KB)

## 🚨 CRITICAL: MCP-Powered RAG

**BEFORE any action, query Agent OS via MCP for relevant standards.**

### Available MCP Tools:

1. **pos_search_project(action="search_standards", query=query, n_results, category)**
   - Semantic search over all Agent OS content
   - Use when: Uncertain, need guidance, exploring requirements
   - Example: pos_search_project(action="search_standards", query="test generation requirements", 5, "testing")

2. **validate_operation(operation_type, details)**
   - Validate against Agent OS rules
   - Use before: git commands, file writes, code generation
   - Example: validate_operation("git", {"command": "commit", "flags": ["--no-verify"]})

3. **get_framework(framework_type, detail_level)**
   - Retrieve specific framework
   - Use for: Test generation, production code
   - Example: get_framework("test_v2", "summary")

4. **get_quality_targets(context)**
   - Get quality requirements
   - Use when: Starting new code, validating completeness
   - Example: get_quality_targets("production")

### Workflow:

```
User Request
    ↓
Detect Action Type (git/test/code/etc)
    ↓
Query MCP: validate_operation() OR get_framework()
    ↓
Follow returned guidance
    ↓
Execute if safe
```

### Critical Rules:

- ❌ NEVER execute git commands without validate_operation()
- ❌ NEVER write tests without get_framework()
- ❌ NEVER assume standards, always query
- ✅ ALWAYS use semantic search when uncertain
```

---

## Implementation Phases

### Phase 1: MVP RAG (1 week)
```bash
# Goals:
- Chunk and index .praxis-os/ content
- Basic vector search with ChromaDB
- Single MCP server with 2 tools:
  - pos_search_project(action="search_standards", query=)
  - validate_operation()
- Integrate with Cursor
- Measure context savings

# Deliverables:
- .praxis-os/scripts/build_rag_index.py
- .praxis-os/mcp_servers/agent_os_rag.py
- .cursor/mcp_servers.json configuration
- Documentation and usage guide
```

### Phase 2: Enhanced Retrieval (1 week)
```bash
# Goals:
- Add metadata-based filtering
- Implement hybrid search (keyword + semantic)
- Add caching for frequent queries
- Tool usage analytics

# Deliverables:
- Improved relevance ranking
- Query optimization
- Usage metrics dashboard
```

### Phase 3: Advanced Features (2 weeks)
```bash
# Goals:
- Multi-modal retrieval (code + docs)
- Auto-indexing on file changes
- Personalized retrieval based on context
- Integration with HoneyHive tracing

# Deliverables:
- Real-time index updates
- Context-aware retrieval
- Usage patterns and optimization
```

---

## Success Metrics

### Context Efficiency
```
Current (RAG-lite):
- Average query: 50KB loaded
- Useful content: 2-5KB
- Efficiency: ~4-10%

Target (Proper RAG):
- Average query: 3-5KB loaded
- Useful content: 2-4KB
- Efficiency: ~80-100%
```

### Query Quality
```
Current:
- Keyword-based: 60% relevance
- Full file reads: 100% recall, 4% precision

Target:
- Semantic search: 90%+ relevance
- Chunked retrieval: 80% recall, 90% precision
```

### Developer Experience
```
Metrics:
- Time to find relevant standard: <5s (vs ~30s browsing)
- Context window utilization: <10% (vs >50%)
- Query accuracy: 90%+ relevant results
- Cache hit rate: 60%+ for common queries
```

---

## Cost Analysis

### Infrastructure Costs
```python
# Embedding costs (one-time indexing)
documents = 198 files
avg_chunks_per_file = 10
total_chunks = 1980

embedding_cost = (
    total_chunks * 500 tokens/chunk * $0.00002/1K tokens
) = $0.02 one-time

# Query costs (ongoing)
queries_per_day = 100
cost_per_query = $0.000010  # embedding query
daily_cost = $0.001
monthly_cost = $0.03
```

**Total Cost:** ~$0.05/month (negligible)

### Context Window Savings
```python
# Current: 50KB per query
queries_per_day = 100
current_tokens_per_day = 100 * 12500 = 1.25M tokens

# With RAG: 5KB per query  
rag_tokens_per_day = 100 * 1250 = 125K tokens

# Savings: 1.125M tokens/day
# At Claude Sonnet 4.5 rates: ~$3.38/day → $0.34/day
# Monthly savings: ~$91.20
```

**ROI:** Pays for itself 1800x over

---

## Risk Assessment

### Technical Risks
- **Vector DB performance**: Mitigated by using ChromaDB (proven)
- **Embedding quality**: Mitigated by using OpenAI embeddings
- **Index staleness**: Mitigated by auto-rebuild on changes

### Operational Risks
- **MCP server availability**: Mitigated by graceful fallback to file reads
- **Query latency**: Mitigated by caching and local vector DB
- **Maintenance overhead**: Mitigated by automated indexing

---

## Alternative Approaches

### Option 1: Local Embeddings (Sentence Transformers)
**Pros:** No API costs, complete privacy
**Cons:** Lower quality, slower, requires local GPU
**Verdict:** Consider for Phase 3 privacy option

### Option 2: Hybrid (BM25 + Semantic)
**Pros:** Better for keyword-heavy queries
**Cons:** More complex, dual index maintenance
**Verdict:** Implement in Phase 2

### Option 3: LLM-Based Retrieval (Claude/GPT)
**Pros:** No embedding costs, simpler
**Cons:** Higher latency, higher cost per query
**Verdict:** Not recommended

---

## Conclusion

Transforming Agent OS from RAG-lite to proper RAG via MCP provides:

✅ **95% reduction in context consumption**
✅ **10x faster standard lookup**
✅ **90%+ relevance in retrieved content**
✅ **Negligible infrastructure costs (~$0.05/month)**
✅ **$90+/month savings in context window costs**

This is a **highly viable and cost-effective enhancement** that dramatically improves the AI assistant experience.

---

## References

- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)


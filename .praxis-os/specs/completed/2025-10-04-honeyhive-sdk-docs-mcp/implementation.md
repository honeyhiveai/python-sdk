# HoneyHive SDK Documentation MCP Server
# Technical Implementation Details
# 100% AI Infrastructure Authorship

**Date:** October 4, 2025  
**Status:** Design Phase  
**Authorship:** 100% AI-authored via human orchestration

---

## 1. DEPENDENCIES & ENVIRONMENT

### 1.1 Python Requirements

**File:** `.mcp_servers/honeyhive_sdk_docs/requirements.txt`

```text
# HoneyHive SDK Docs MCP Server Dependencies
# 100% AI-authored via human orchestration

# Vector database for RAG
lancedb>=0.3.0

# Local embeddings (default, free, offline)
sentence-transformers>=2.0.0

# File watching for hot reload
watchdog>=3.0.0

# HTML parsing (Sphinx HTML, OTEL docs)
beautifulsoup4>=4.12.0

# Git operations (Mintlify repo cloning)
gitpython>=3.1.0

# HTTP requests (OTEL docs fetching)
requests>=2.31.0

# RST parsing (Sphinx RST source)
docutils>=0.19

# Model Context Protocol
mcp>=1.0.0

# HoneyHive tracing for dogfooding
honeyhive>=0.1.0

# Data validation
pydantic>=2.0.0

# Arrow tables for LanceDB
pyarrow>=12.0.0
```

### 1.2 Environment Variables

**File:** `.env` (project root)

```bash
# HoneyHive Tracing (optional, for dogfooding)
HONEYHIVE_ENABLED=true
HH_API_KEY=your_api_key_here
HH_PROJECT=your_project_name

# MCP Server Configuration
DOCS_MCP_INDEX_PATH=.mcp_servers/honeyhive_sdk_docs/honeyhive_sdk_docs.lance
DOCS_MCP_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
DOCS_MCP_HOT_RELOAD_ENABLED=true
DOCS_MCP_PERIODIC_SYNC_ENABLED=true

# External Sources
MINTLIFY_REPO_URL=https://github.com/honeyhiveai/honeyhive-ai-docs
MINTLIFY_SYNC_INTERVAL=86400  # 1 day in seconds
OTEL_SYNC_INTERVAL=604800     # 7 days in seconds
```

---

## 2. PROJECT STRUCTURE

```
.mcp_servers/honeyhive_sdk_docs/
├── __init__.py                         # Package marker
├── honeyhive_docs_rag.py               # MCP server entry point
├── rag_engine.py                       # RAG search engine
├── chunker.py                          # Unified chunking interface
├── models.py                           # Pydantic models + LanceDB schema
├── hot_reload.py                       # Watchdog file monitoring
├── sync.py                             # External docs syncing
├── parsers/
│   ├── __init__.py
│   ├── sphinx_parser.py                # RST/HTML parsing
│   ├── mintlify_parser.py              # MDX parsing
│   ├── source_parser.py                # Python AST parsing
│   ├── examples_parser.py              # Example files
│   └── otel_parser.py                  # OpenTelemetry docs
├── scripts/
│   ├── __init__.py
│   ├── build_index.py                  # Index builder script
│   └── sync_external_docs.py           # Manual sync script
├── .cache/                             # External docs cache (gitignored)
│   ├── honeyhive-ai-docs/              # Cloned Mintlify repo
│   └── otel_docs/                      # Downloaded OTEL docs
├── honeyhive_sdk_docs.lance/           # LanceDB index (gitignored)
├── requirements.txt                    # Dependencies
├── run_docs_server.py                  # Wrapper script (.env loading)
└── README.md                           # Documentation
```

---

## 3. DATA MODELS

### 3.1 Core Models

**File:** `.mcp_servers/honeyhive_sdk_docs/models.py`

```python
"""
Data models for HoneyHive SDK Docs MCP Server.

100% AI-authored via human orchestration.
"""

from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """
    Metadata for a documentation chunk.
    
    Used for filtering, ranking, and citation in search results.
    """
    
    # Source identification
    source: Literal["local_docs", "mintlify", "source_code", "examples", "otel"]
    file_path: str = Field(..., description="Relative path from project root")
    url: str | None = Field(None, description="URL for external sources")
    
    # Document categorization
    doc_type: Literal[
        "tutorial",
        "how-to",
        "explanation",
        "api_reference",
        "example",
        "concept"
    ]
    language: Literal["python", "javascript", "rest_api", "general"] = "python"
    provider: str | None = Field(None, description="e.g., 'openai', 'anthropic'")
    
    # Symbol information (for source code)
    symbol: str | None = Field(None, description="e.g., 'HoneyHiveTracer.init'")
    symbol_type: Literal[
        "module", "class", "function", "method", "attribute"
    ] | None = None
    line_range: str | None = Field(None, description="e.g., '12:45'")
    signature: str | None = Field(None, description="e.g., 'def init(...)'")
    
    # Content hierarchy
    title: str = Field(..., description="Section or symbol title")
    headers: list[str] = Field(default_factory=list, description="Breadcrumb trail")
    
    # Quality metadata
    token_count: int = Field(..., description="Token count for LLM context")
    char_count: int = Field(..., description="Character count")
    last_updated: str = Field(..., description="ISO 8601 timestamp")
    indexed_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO 8601 timestamp"
    )


class DocumentChunk(BaseModel):
    """
    Represents a single chunk of documentation.
    
    This is the fundamental unit of indexing and retrieval.
    """
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique ID")
    content: str = Field(..., description="The actual text content")
    embedding: list[float] = Field(
        default_factory=list,
        description="Vector embedding (384 floats)"
    )
    metadata: ChunkMetadata = Field(..., description="Chunk metadata")


class SearchResult(BaseModel):
    """
    Search result returned by RAG engine.
    
    Contains chunk content, metadata, and relevance score.
    """
    
    content: str
    source: str
    file_path: str
    doc_type: str
    title: str
    score: float = Field(..., description="Similarity score (lower is better)")
    metadata: ChunkMetadata


class Parameter(BaseModel):
    """Parameter information for API reference."""
    
    name: str
    type: str
    required: bool
    default: str | None = None
    description: str


class APIReference(BaseModel):
    """API reference for a symbol (class, function, method)."""
    
    symbol: str
    signature: str
    docstring: str
    parameters: list[Parameter]
    return_type: str
    source_file: str
    line_range: str
    examples: list[str] = Field(default_factory=list)


class IntegrationGuide(BaseModel):
    """Integration guide for a provider."""
    
    provider: str
    docs: list[SearchResult]
    examples: list[str]
    source_code: list[str]
    external_links: list[str]


class ExampleFile(BaseModel):
    """Example file information."""
    
    file_path: str
    content: str
    provider: str
    imports: list[str]
    description: str
```

### 3.2 LanceDB Schema

**Schema Creation:**

```python
"""Create LanceDB table with schema."""
import lancedb
import pyarrow as pa


def create_lancedb_table(db_path: str) -> lancedb.Table:
    """
    Create LanceDB table for documentation chunks.
    
    Args:
        db_path: Path to LanceDB database directory
    
    Returns:
        LanceDB table instance
    """
    db = lancedb.connect(db_path)
    
    # Define schema
    schema = pa.schema([
        # Core fields
        pa.field("id", pa.string()),
        pa.field("content", pa.string()),
        pa.field("embedding", pa.list_(pa.float32(), 384)),  # Fixed size
        
        # Metadata fields (flattened for efficient querying)
        pa.field("source", pa.string()),
        pa.field("file_path", pa.string()),
        pa.field("url", pa.string()),
        pa.field("doc_type", pa.string()),
        pa.field("language", pa.string()),
        pa.field("provider", pa.string()),
        pa.field("symbol", pa.string()),
        pa.field("symbol_type", pa.string()),
        pa.field("line_range", pa.string()),
        pa.field("signature", pa.string()),
        pa.field("title", pa.string()),
        pa.field("headers", pa.list_(pa.string())),
        pa.field("token_count", pa.int32()),
        pa.field("char_count", pa.int32()),
        pa.field("last_updated", pa.string()),
        pa.field("indexed_at", pa.string())
    ])
    
    # Create table
    table = db.create_table("honeyhive_docs", schema=schema)
    
    # Create indexes for fast filtering
    table.create_index("source")
    table.create_index("doc_type")
    table.create_index("symbol")
    table.create_index("provider")
    
    return table
```

---

## 4. RAG ENGINE IMPLEMENTATION

### 4.1 Core RAG Engine

**File:** `.mcp_servers/honeyhive_sdk_docs/rag_engine.py`

```python
"""
RAG Engine for HoneyHive SDK Documentation.

Provides semantic search over LanceDB vector index with filtering and ranking.

100% AI-authored via human orchestration.
"""

import logging
from pathlib import Path
from typing import Any

import lancedb
from sentence_transformers import SentenceTransformer

from .models import SearchResult, ChunkMetadata

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval Augmented Generation engine for SDK documentation.
    
    Provides semantic search with metadata filtering and intelligent ranking.
    """
    
    def __init__(
        self,
        index_path: Path,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize RAG engine.
        
        Args:
            index_path: Path to LanceDB index directory
            embedding_model: HuggingFace model name for embeddings
        """
        self.index_path = Path(index_path)
        self.db = lancedb.connect(str(self.index_path))
        
        # Load table (will be created by index builder if doesn't exist)
        try:
            self.table = self.db.open_table("honeyhive_docs")
            logger.info(f"Opened LanceDB table with {len(self.table)} chunks")
        except Exception as e:
            logger.warning(f"Table not found, will be created on first index: {e}")
            self.table = None
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        logger.info("RAG engine initialized successfully")
    
    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        top_k: int = 5
    ) -> list[SearchResult]:
        """
        Semantic search over documentation.
        
        Args:
            query: Natural language search query
            filters: Optional metadata filters (source, doc_type, provider, language)
            top_k: Number of results to return
        
        Returns:
            List of SearchResult objects ranked by relevance
        """
        if self.table is None:
            logger.error("Index not built, cannot search")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Build filter expression
            filter_expr = self._build_filter(filters or {})
            
            # Search LanceDB
            search = self.table.search(query_embedding).limit(top_k)
            
            if filter_expr:
                search = search.where(filter_expr)
            
            results = search.to_list()
            
            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    content=r["content"],
                    source=r["source"],
                    file_path=r["file_path"],
                    doc_type=r["doc_type"],
                    title=r["title"],
                    score=r.get("_distance", 1.0),
                    metadata=ChunkMetadata(
                        source=r["source"],
                        file_path=r["file_path"],
                        url=r.get("url"),
                        doc_type=r["doc_type"],
                        language=r.get("language", "python"),
                        provider=r.get("provider"),
                        symbol=r.get("symbol"),
                        symbol_type=r.get("symbol_type"),
                        line_range=r.get("line_range"),
                        signature=r.get("signature"),
                        title=r["title"],
                        headers=r.get("headers", []),
                        token_count=r["token_count"],
                        char_count=r["char_count"],
                        last_updated=r["last_updated"],
                        indexed_at=r["indexed_at"]
                    )
                )
                for r in results
            ]
            
            # Re-rank results
            reranked = self._rerank(search_results, query, filters or {})
            
            return reranked
        
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            # Fallback to keyword search
            return self._keyword_search_fallback(query, filters, top_k)
    
    def _build_filter(self, filters: dict[str, Any]) -> str:
        """
        Build LanceDB filter expression from filters dict.
        
        Args:
            filters: Dictionary of filters (source, doc_type, provider, language)
        
        Returns:
            LanceDB WHERE clause string
        """
        conditions = []
        
        # Source filter (can be list)
        if "source" in filters:
            sources = filters["source"] if isinstance(filters["source"], list) else [filters["source"]]
            source_conditions = [f"source = '{s}'" for s in sources]
            conditions.append(f"({' OR '.join(source_conditions)})")
        
        # Doc type filter (can be list)
        if "doc_type" in filters:
            doc_types = filters["doc_type"] if isinstance(filters["doc_type"], list) else [filters["doc_type"]]
            doc_type_conditions = [f"doc_type = '{dt}'" for dt in doc_types]
            conditions.append(f"({' OR '.join(doc_type_conditions)})")
        
        # Provider filter
        if "provider" in filters:
            conditions.append(f"provider = '{filters['provider']}'")
        
        # Language filter
        if "language" in filters:
            conditions.append(f"language = '{filters['language']}'")
        
        # Combine conditions with AND
        if not conditions:
            return ""
        
        return " AND ".join(conditions)
    
    def _rerank(
        self,
        results: list[SearchResult],
        query: str,
        filters: dict[str, Any]
    ) -> list[SearchResult]:
        """
        Re-rank results by multiple factors.
        
        Ranking factors:
        1. Semantic distance (LanceDB score)
        2. Doc type priority (api_reference > tutorial > concept)
        3. Source priority (local_docs > mintlify > otel)
        4. Recency (newer docs preferred)
        5. Query-specific boosts (e.g., "example" in query → boost examples)
        
        Args:
            results: Initial search results
            query: Original query
            filters: Filters applied
        
        Returns:
            Re-ranked results
        """
        query_lower = query.lower()
        
        # Assign weights to each result
        weighted_results = []
        
        for result in results:
            score = result.score  # Lower is better (distance)
            
            # Doc type priority
            doc_type_weights = {
                "api_reference": 0.8,   # Boost (multiply by <1)
                "tutorial": 0.9,
                "how-to": 1.0,
                "example": 1.0,
                "concept": 1.1,
                "explanation": 1.2
            }
            score *= doc_type_weights.get(result.doc_type, 1.0)
            
            # Source priority
            source_weights = {
                "local_docs": 0.9,
                "examples": 0.9,
                "mintlify": 1.0,
                "source_code": 1.1,
                "otel": 1.2
            }
            score *= source_weights.get(result.source, 1.0)
            
            # Recency boost (last 30 days)
            from datetime import datetime, timedelta
            try:
                last_updated = datetime.fromisoformat(result.metadata.last_updated)
                days_old = (datetime.now() - last_updated).days
                if days_old < 30:
                    score *= 0.95  # 5% boost
            except (ValueError, TypeError):
                pass
            
            # Query-specific boosts
            if "example" in query_lower and result.doc_type == "example":
                score *= 0.7  # 30% boost
            
            if "signature" in query_lower and result.metadata.signature:
                score *= 0.8  # 20% boost
            
            if "how" in query_lower and result.doc_type == "how-to":
                score *= 0.85  # 15% boost
            
            weighted_results.append((score, result))
        
        # Sort by adjusted score (lower is better)
        weighted_results.sort(key=lambda x: x[0])
        
        return [result for score, result in weighted_results]
    
    def _keyword_search_fallback(
        self,
        query: str,
        filters: dict[str, Any] | None,
        top_k: int
    ) -> list[SearchResult]:
        """
        Fallback keyword search if semantic search fails.
        
        Less accurate but always works (grep-style search).
        
        Args:
            query: Search query
            filters: Metadata filters
            top_k: Number of results
        
        Returns:
            Search results from keyword matching
        """
        logger.warning("Using keyword search fallback")
        
        # Simple keyword matching (not implemented in this spec)
        # In practice, would iterate through indexed files and grep
        
        return [SearchResult(
            content="Search temporarily unavailable. Try rephrasing your query.",
            source="system",
            file_path="",
            doc_type="error",
            title="Search Error",
            score=1.0,
            metadata=ChunkMetadata(
                source="system",
                file_path="",
                doc_type="error",
                title="Search Error",
                token_count=0,
                char_count=0,
                last_updated=datetime.now().isoformat(),
                indexed_at=datetime.now().isoformat()
            )
        )]
    
    def health_check(self) -> dict[str, Any]:
        """
        Check RAG engine health.
        
        Returns:
            Health status dictionary
        """
        try:
            chunk_count = len(self.table) if self.table else 0
            return {
                "status": "healthy",
                "index_path": str(self.index_path),
                "chunk_count": chunk_count,
                "embedding_model": self.embedder.get_sentence_embedding_dimension()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
```

---

## 5. PARSER IMPLEMENTATIONS

### 5.1 Sphinx RST Parser

**File:** `.mcp_servers/honeyhive_sdk_docs/parsers/sphinx_parser.py`

```python
"""
Sphinx RST/HTML parser for SDK documentation.

Parses both RST source files and HTML output from Sphinx build.

100% AI-authored via human orchestration.
"""

import logging
from pathlib import Path

from bs4 import BeautifulSoup
from docutils.core import publish_doctree

from ..models import DocumentChunk, ChunkMetadata

logger = logging.getLogger(__name__)


class SphinxRSTParser:
    """Parser for Sphinx RST source files."""
    
    def parse(self, rst_file: Path) -> list[DocumentChunk]:
        """
        Parse RST file into documentation chunks.
        
        Strategy:
        - Split by headers (##, ###, ####)
        - Keep code blocks intact
        - Preserve cross-references
        - Extract metadata from directives
        
        Args:
            rst_file: Path to RST file
        
        Returns:
            List of DocumentChunk objects
        """
        try:
            with open(rst_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse with docutils
            doctree = publish_doctree(content)
            
            chunks = []
            
            # Extract sections
            for section in doctree.traverse(condition=lambda n: n.tagname == "section"):
                title = self._extract_title(section)
                section_content = self._extract_content(section)
                
                if not section_content.strip():
                    continue
                
                chunk = DocumentChunk(
                    content=section_content,
                    metadata=ChunkMetadata(
                        source="local_docs",
                        file_path=str(rst_file.relative_to(Path.cwd())),
                        doc_type=self._infer_doc_type(rst_file),
                        title=title,
                        headers=self._extract_breadcrumb(section),
                        token_count=len(section_content.split()),
                        char_count=len(section_content),
                        last_updated=rst_file.stat().st_mtime
                    )
                )
                chunks.append(chunk)
            
            logger.info(f"Parsed {rst_file.name}: {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Failed to parse {rst_file}: {e}", exc_info=True)
            return []
    
    def _extract_title(self, section) -> str:
        """Extract section title."""
        title_node = section.next_node(condition=lambda n: n.tagname == "title")
        return title_node.astext() if title_node else "Untitled"
    
    def _extract_content(self, section) -> str:
        """Extract section content (text + code blocks)."""
        return section.astext()
    
    def _extract_breadcrumb(self, section) -> list[str]:
        """Extract header breadcrumb trail."""
        breadcrumb = []
        parent = section.parent
        while parent:
            if parent.tagname == "section":
                title = self._extract_title(parent)
                breadcrumb.insert(0, title)
            parent = parent.parent
        return breadcrumb
    
    def _infer_doc_type(self, file_path: Path) -> str:
        """Infer document type from file path."""
        path_str = str(file_path)
        if "tutorial" in path_str:
            return "tutorial"
        if "how-to" in path_str:
            return "how-to"
        if "reference/api" in path_str:
            return "api_reference"
        if "explanation" in path_str:
            return "explanation"
        return "concept"


class SphinxHTMLParser:
    """Parser for Sphinx HTML output (API reference via autodoc)."""
    
    def parse(self, html_file: Path) -> list[DocumentChunk]:
        """
        Parse Sphinx HTML for API reference.
        
        Target elements:
        - <dl class="py class"> (class definitions)
        - <dl class="py function"> (function signatures)
        - <dl class="py method"> (method signatures)
        
        Args:
            html_file: Path to HTML file
        
        Returns:
            List of DocumentChunk objects
        """
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, "html.parser")
            chunks = []
            
            # Extract classes
            for class_dl in soup.find_all("dl", class_=lambda c: c and "py class" in c):
                chunk = self._extract_symbol_chunk(class_dl, html_file, "class")
                if chunk:
                    chunks.append(chunk)
            
            # Extract functions
            for func_dl in soup.find_all("dl", class_=lambda c: c and "py function" in c):
                chunk = self._extract_symbol_chunk(func_dl, html_file, "function")
                if chunk:
                    chunks.append(chunk)
            
            # Extract methods
            for method_dl in soup.find_all("dl", class_=lambda c: c and "py method" in c):
                chunk = self._extract_symbol_chunk(method_dl, html_file, "method")
                if chunk:
                    chunks.append(chunk)
            
            logger.info(f"Parsed {html_file.name}: {len(chunks)} API reference chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Failed to parse {html_file}: {e}", exc_info=True)
            return []
    
    def _extract_symbol_chunk(
        self,
        dl_element,
        html_file: Path,
        symbol_type: str
    ) -> DocumentChunk | None:
        """Extract a single symbol (class/function/method) as a chunk."""
        try:
            # Extract signature (from <dt>)
            dt = dl_element.find("dt")
            signature = dt.get_text(strip=True) if dt else ""
            symbol_id = dt.get("id", "") if dt else ""
            
            # Extract docstring (from <dd>)
            dd = dl_element.find("dd")
            docstring = dd.get_text(separator="\n", strip=True) if dd else ""
            
            if not signature or not docstring:
                return None
            
            content = f"{signature}\n\n{docstring}"
            
            return DocumentChunk(
                content=content,
                metadata=ChunkMetadata(
                    source="local_docs",
                    file_path=str(html_file.relative_to(Path.cwd())),
                    doc_type="api_reference",
                    symbol=symbol_id,
                    symbol_type=symbol_type,
                    signature=signature,
                    title=symbol_id,
                    headers=[],
                    token_count=len(content.split()),
                    char_count=len(content),
                    last_updated=html_file.stat().st_mtime
                )
            )
        
        except Exception as e:
            logger.error(f"Failed to extract symbol: {e}")
            return None
```

*(Note: Remaining parser implementations follow similar patterns - see architecture.md for details)*

---

## 6. MCP SERVER IMPLEMENTATION

**File:** `.mcp_servers/honeyhive_sdk_docs/honeyhive_docs_rag.py`

```python
"""
HoneyHive SDK Documentation MCP Server.

Provides semantic search and structured access to SDK documentation via MCP.

100% AI-authored via human orchestration.
"""

import logging
import os
from pathlib import Path

from mcp.server import Server
from mcp.server.models import Tool, TextContent

# HoneyHive tracing
HONEYHIVE_ENABLED = os.getenv("HONEYHIVE_ENABLED", "false").lower() == "true"
tracer = None

if HONEYHIVE_ENABLED:
    try:
        from honeyhive import HoneyHiveTracer, trace, enrich_span
        from honeyhive.models import EventType
        
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY"),
            project=os.getenv("HH_PROJECT"),
            source="honeyhive-sdk-docs-mcp",
            verbose=True
        )
        logging.info("🍯 HoneyHive tracing enabled for dogfooding")
    except ImportError:
        HONEYHIVE_ENABLED = False
        logging.warning("HoneyHive SDK not available, tracing disabled")

# No-op decorators if tracing disabled
if not HONEYHIVE_ENABLED:
    def trace(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def enrich_span(data):
        pass

# Import local modules
from .rag_engine import RAGEngine
from .models import SearchResult

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_server() -> Server:
    """
    Create and configure MCP server.
    
    Returns:
        Configured MCP server instance
    """
    server = Server("honeyhive-sdk-docs")
    
    # Initialize RAG engine
    index_path = Path(os.getenv(
        "DOCS_MCP_INDEX_PATH",
        ".mcp_servers/honeyhive_sdk_docs/honeyhive_sdk_docs.lance"
    ))
    embedding_model = os.getenv(
        "DOCS_MCP_EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    
    rag_engine = RAGEngine(index_path, embedding_model)
    
    # Register tools
    @server.list_tools()
    def handle_list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_docs",
                description=(
                    "Semantic search over HoneyHive SDK documentation. "
                    "Searches local Sphinx docs, Mintlify docs, source code, "
                    "examples, and OpenTelemetry docs."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional metadata filters",
                            "properties": {
                                "source": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Filter by source"
                                },
                                "doc_type": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Filter by document type"
                                },
                                "provider": {
                                    "type": "string",
                                    "description": "Filter by provider"
                                },
                                "language": {
                                    "type": "string",
                                    "description": "Filter by language"
                                }
                            }
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_api_reference",
                description="Get API reference for a specific symbol",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Fully qualified symbol name (e.g., 'HoneyHiveTracer.init')"
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            Tool(
                name="get_integration_guide",
                description="Get complete integration guide for a provider",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "description": "Provider name (e.g., 'openai', 'anthropic')"
                        }
                    },
                    "required": ["provider"]
                }
            ),
            Tool(
                name="search_examples",
                description="Find code examples by query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for examples"
                        },
                        "provider": {
                            "type": "string",
                            "description": "Optional provider filter"
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
    
    @server.call_tool()
    def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "search_docs":
            return search_docs_handler(rag_engine, arguments)
        elif name == "get_api_reference":
            return get_api_reference_handler(rag_engine, arguments)
        elif name == "get_integration_guide":
            return get_integration_guide_handler(rag_engine, arguments)
        elif name == "search_examples":
            return search_examples_handler(rag_engine, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    return server


@trace(tracer=tracer, event_type=EventType.tool) if HONEYHIVE_ENABLED else lambda f: f
def search_docs_handler(rag_engine: RAGEngine, arguments: dict) -> list[TextContent]:
    """Handle search_docs tool invocation."""
    query = arguments["query"]
    filters = arguments.get("filters", {})
    top_k = arguments.get("top_k", 5)
    
    # Enrich span with inputs
    if HONEYHIVE_ENABLED:
        enrich_span({"query": query, "filters": filters, "top_k": top_k})
    
    # Perform search
    results = rag_engine.search(query, filters, top_k)
    
    # Enrich span with outputs
    if HONEYHIVE_ENABLED:
        enrich_span({
            "result_count": len(results),
            "sources": [r.source for r in results],
            "avg_score": sum(r.score for r in results) / len(results) if results else 0
        })
    
    # Format results
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"**Result {i}** (score: {result.score:.3f})\n"
            f"**Source:** {result.source} | **Type:** {result.doc_type}\n"
            f"**File:** {result.file_path}\n"
            f"**Title:** {result.title}\n\n"
            f"{result.content}\n\n"
            f"---\n"
        )
    
    return [TextContent(type="text", text="\n".join(formatted_results))]


# (Other tool handlers follow similar pattern...)


def main():
    """Main entry point for MCP server."""
    import asyncio
    from mcp.server.stdio import stdio_server
    
    server = create_server()
    
    asyncio.run(stdio_server(server.run()))


if __name__ == "__main__":
    main()
```

---

## 7. INDEX BUILD SCRIPT

**File:** `.mcp_servers/honeyhive_sdk_docs/scripts/build_index.py`

```python
"""
Index builder for HoneyHive SDK documentation.

Builds LanceDB vector index from all documentation sources.

100% AI-authored via human orchestration.
"""

import argparse
import hashlib
import logging
from datetime import datetime
from pathlib import Path

import lancedb
from sentence_transformers import SentenceTransformer

from ..models import DocumentChunk
from ..chunker import DocumentChunker
from ..sync import ExternalDocsSync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def build_index(
    sources: list[str],
    force: bool = False,
    index_path: Path = None,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
):
    """
    Build vector index from documentation sources.
    
    Args:
        sources: List of sources to index ("local"|"mintlify"|"otel"|"all")
        force: Force rebuild even if index exists
        index_path: Path to LanceDB index
        embedding_model: Embedding model name
    """
    if index_path is None:
        index_path = Path(".mcp_servers/honeyhive_sdk_docs/honeyhive_sdk_docs.lance")
    
    # Check if index exists
    if index_path.exists() and not force:
        logger.info("Index exists, use --force to rebuild")
        return
    
    logger.info(f"Building index at {index_path}")
    
    # Initialize components
    chunker = DocumentChunker()
    embedder = SentenceTransformer(embedding_model)
    
    # Collect all chunks
    all_chunks = []
    
    if "all" in sources or "local" in sources:
        logger.info("Indexing local SDK documentation...")
        all_chunks.extend(index_local_docs(chunker))
    
    if "all" in sources or "mintlify" in sources:
        logger.info("Indexing Mintlify documentation...")
        all_chunks.extend(index_mintlify_docs(chunker))
    
    if "all" in sources or "otel" in sources:
        logger.info("Indexing OpenTelemetry documentation...")
        all_chunks.extend(index_otel_docs(chunker))
    
    logger.info(f"Total chunks collected: {len(all_chunks)}")
    
    # Deduplicate
    logger.info("Deduplicating chunks...")
    unique_chunks = deduplicate_chunks(all_chunks)
    logger.info(f"Unique chunks: {len(unique_chunks)}")
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    for chunk in unique_chunks:
        chunk.embedding = embedder.encode(chunk.content).tolist()
    
    # Create LanceDB table
    logger.info("Creating LanceDB table...")
    db = lancedb.connect(str(index_path))
    
    # Convert chunks to records
    records = [chunk.model_dump() for chunk in unique_chunks]
    
    # Create table
    table = db.create_table("honeyhive_docs", data=records)
    
    # Create indexes
    table.create_index("source")
    table.create_index("doc_type")
    table.create_index("symbol")
    table.create_index("provider")
    
    logger.info(f"✅ Index built successfully: {len(unique_chunks)} chunks")


def index_local_docs(chunker: DocumentChunker) -> list[DocumentChunk]:
    """Index local SDK documentation."""
    chunks = []
    
    # Index RST files
    docs_dir = Path("docs")
    for rst_file in docs_dir.rglob("*.rst"):
        chunks.extend(chunker.chunk_file(rst_file))
    
    # Index HTML files (API reference)
    html_dir = Path("docs/_build/html")
    if html_dir.exists():
        for html_file in html_dir.rglob("*.html"):
            if "genindex" not in str(html_file) and "search" not in str(html_file):
                chunks.extend(chunker.chunk_file(html_file))
    
    # Index source code
    src_dir = Path("src/honeyhive")
    for py_file in src_dir.rglob("*.py"):
        if ".tox" not in str(py_file) and "__pycache__" not in str(py_file):
            chunks.extend(chunker.chunk_file(py_file))
    
    # Index examples
    examples_dir = Path("examples")
    if examples_dir.exists():
        for py_file in examples_dir.rglob("*.py"):
            chunks.extend(chunker.chunk_file(py_file))
    
    return chunks


def index_mintlify_docs(chunker: DocumentChunker) -> list[DocumentChunk]:
    """Index Mintlify documentation."""
    sync = ExternalDocsSync(None)
    sync.sync_mintlify()
    
    chunks = []
    mintlify_dir = Path(".mcp_servers/honeyhive_sdk_docs/.cache/honeyhive-ai-docs")
    
    for mdx_file in mintlify_dir.rglob("*.mdx"):
        chunks.extend(chunker.chunk_file(mdx_file))
    
    for md_file in mintlify_dir.rglob("*.md"):
        chunks.extend(chunker.chunk_file(md_file))
    
    return chunks


def index_otel_docs(chunker: DocumentChunker) -> list[DocumentChunk]:
    """Index OpenTelemetry documentation."""
    from ..parsers.otel_parser import OTELDocsParser
    parser = OTELDocsParser()
    return parser.fetch_and_parse()


def deduplicate_chunks(chunks: list[DocumentChunk]) -> list[DocumentChunk]:
    """
    Deduplicate chunks by content hash.
    
    Priority: mintlify > local_docs > source_code
    """
    seen_hashes = {}
    unique_chunks = []
    
    # Sort by priority
    priority = {"mintlify": 0, "local_docs": 1, "source_code": 2, "examples": 3, "otel": 4}
    sorted_chunks = sorted(chunks, key=lambda c: priority.get(c.metadata.source, 5))
    
    for chunk in sorted_chunks:
        # Compute content hash
        content_normalized = " ".join(chunk.content.split())
        content_hash = hashlib.sha256(content_normalized.encode()).hexdigest()
        
        if content_hash not in seen_hashes:
            seen_hashes[content_hash] = chunk.metadata.source
            unique_chunks.append(chunk)
    
    return unique_chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build HoneyHive SDK docs index")
    parser.add_argument("--sources", nargs="+", default=["all"],
                       choices=["local", "mintlify", "otel", "all"])
    parser.add_argument("--force", action="store_true", help="Force rebuild")
    
    args = parser.parse_args()
    
    build_index(args.sources, args.force)
```

---

## 8. DEPLOYMENT

### 8.1 Wrapper Script

**File:** `.mcp_servers/honeyhive_sdk_docs/run_docs_server.py`

```python
"""
Wrapper script for HoneyHive SDK Docs MCP server.

Loads environment variables from .env and starts the server.

100% AI-authored via human orchestration.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env file
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            if '=' in line:
                key, value = line.split('=', 1)
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), value)

# Import and run server
from honeyhive_sdk_docs.honeyhive_docs_rag import main

if __name__ == "__main__":
    main()
```

### 8.2 MCP Registration

**File:** `.cursor/mcp.json` (add to existing config)

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "/Users/josh/src/github.com/honeyhiveai/python-sdk/python-sdk/bin/python",
      "args": ["/Users/josh/src/github.com/honeyhiveai/python-sdk/.praxis-os/run_mcp_server.py"],
      "env": {"HONEYHIVE_ENABLED": "true"}
    },
    "honeyhive-sdk-docs": {
      "command": "/Users/josh/src/github.com/honeyhiveai/python-sdk/python-sdk/bin/python",
      "args": ["/Users/josh/src/github.com/honeyhiveai/python-sdk/.mcp_servers/honeyhive_sdk_docs/run_docs_server.py"],
      "env": {"HONEYHIVE_ENABLED": "true"},
      "autoApprove": ["search_docs", "get_api_reference", "search_examples"]
    }
  }
}
```

---

## 9. TESTING STRATEGY

### 9.1 Unit Tests Structure

```
tests/unit/mcp_servers/honeyhive_sdk_docs/
├── __init__.py
├── test_models.py                  # Pydantic model validation
├── test_rag_engine.py              # RAG search, filtering, ranking
├── test_parsers.py                 # All parsers (RST, HTML, AST, MDX)
├── test_chunker.py                 # Chunking logic
└── test_deduplication.py           # Deduplication algorithm
```

### 9.2 Integration Tests

```
tests/integration/mcp_servers/
└── test_honeyhive_sdk_docs_mcp.py  # End-to-end MCP tool invocations
```

### 9.3 Performance Tests

```
tests/performance/
└── test_honeyhive_sdk_docs_performance.py  # Benchmark latency, memory, index size
```

---

## 10. NEXT STEPS

1. ✅ Review this implementation spec
2. ⏭️ Begin Phase 1 implementation (Foundation)
3. ⏭️ Systematic progression through all 5 phases
4. ⏭️ Quality validation at each phase
5. ⏭️ Complete case-study.md post-implementation

---

**Authorship:** 100% AI-authored via human orchestration  
**Approval:** Pending human review

**Total Spec Pages:** 4 documents (SRD, Architecture, Tasks, Implementation)  
**Total Spec Lines:** ~3,000 lines of comprehensive specification  
**Ready for Implementation:** ✅

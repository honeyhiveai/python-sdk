"""
RAG and document chunking models.

Data structures for RAG search results, document chunks, and metadata.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ChunkMetadata:
    """Metadata for better retrieval."""

    framework_type: str  # "test_v3", "production_v2", etc.
    phase: Optional[int]  # If phase-specific
    category: str  # "requirement", "example", "reference"
    tags: List[str]  # ["mocking", "ast", "coverage", ...]
    is_critical: bool  # Contains MANDATORY/CRITICAL markers
    parent_headers: List[str]  # Breadcrumb of headers


@dataclass
class DocumentChunk:
    """Represents a chunk of Agent OS documentation."""

    chunk_id: str  # MD5 hash of content
    file_path: str  # Source file path
    section_header: str  # Header this chunk belongs to
    content: str  # The actual text content
    tokens: int  # Token count
    metadata: ChunkMetadata  # Additional metadata


@dataclass
class SearchResult:
    """Results from RAG search."""

    chunks: List[Dict[str, Any]]  # Retrieved chunks with content and metadata
    total_tokens: int  # Total tokens in all chunks
    retrieval_method: str  # "vector", "grep_fallback", or "cached"
    query_time_ms: float  # Query latency in milliseconds
    relevance_scores: List[float]  # Relevance scores for each chunk
    cache_hit: bool = False  # Whether result was cached


@dataclass
class QueryMetrics:
    """Metrics for observability."""

    query: str
    n_results: int
    filters: Optional[Dict] = None
    retrieval_method: str = "vector"
    query_time_ms: float = 0.0
    chunks_returned: int = 0
    total_tokens: int = 0
    cache_hit: bool = False
    honeyhive_trace_id: Optional[str] = None


__all__ = [
    "ChunkMetadata",
    "DocumentChunk",
    "SearchResult",
    "QueryMetrics",
]

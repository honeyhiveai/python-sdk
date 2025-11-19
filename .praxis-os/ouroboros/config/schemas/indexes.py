"""
Configuration schemas for RAG indexes.

Provides Pydantic v2 models for all index configurations:
    - IndexesConfig: Root container for all indexes
    - StandardsIndexConfig: Vector + FTS + reranking for standards
    - CodeIndexConfig: LanceDB + DuckDB for code semantic + graph
    - ASTIndexConfig: Tree-sitter structural search
    - VectorConfig: Vector search configuration
    - FTSConfig: Full-text search configuration
    - RerankingConfig: Cross-encoder reranking
    - GraphConfig: Call graph traversal configuration
    - FileWatcherConfig: File monitoring for incremental updates

All configurations use fail-fast validation with clear error messages.
Cross-field validation ensures semantic constraints (e.g., chunk_overlap < chunk_size).

Example Usage:
    >>> from ouroboros.config.schemas.indexes import IndexesConfig
    >>> 
    >>> config = IndexesConfig(
    ...     standards=StandardsIndexConfig(
    ...         source_paths=["standards/"],
    ...         vector=VectorConfig(chunk_size=500),
    ...         fts=FTSConfig(enabled=True),
    ...     ),
    ...     code=CodeIndexConfig(...),
    ...     ast=ASTIndexConfig(...)
    ... )

See Also:
    - base.BaseConfig: Base configuration model
    - Pydantic v2 validators: https://docs.pydantic.dev/latest/concepts/validators/
"""

import logging
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator, model_validator

from ouroboros.config.schemas.base import BaseConfig

logger = logging.getLogger(__name__)


class VectorConfig(BaseConfig):
    """
    Vector search configuration using sentence transformers.

    Configures embedding model, chunking strategy, and index type for
    semantic/meaning-based search. Used by both StandardsIndex and CodeIndex.

    Key Settings:
        - model: Sentence transformer model (e.g., "all-MiniLM-L6-v2")
        - chunk_size: Text chunk size in tokens (100-2000)
        - chunk_overlap: Overlap between chunks (0-500, must be < chunk_size)
        - dimension: Embedding dimension (128-4096, model-specific)
        - index_type: Vector index algorithm (HNSW, IVF_PQ, FLAT)

    Chunking Strategy:
        Larger chunks = more context, but less precision
        Smaller chunks = more precision, but less context
        Overlap = prevent concept splitting at boundaries

    Recommended Settings:
        - Standards (docs): chunk_size=800, overlap=100
        - Code (semantic): chunk_size=200, overlap=20

    Example:
        >>> from ouroboros.config.schemas.indexes import VectorConfig
        >>> 
        >>> # Standards config (larger chunks)
        >>> config = VectorConfig(
        ...     model="sentence-transformers/all-MiniLM-L6-v2",
        ...     chunk_size=800,
        ...     chunk_overlap=100,
        ...     dimension=384
        ... )
        >>> 
        >>> # Code config (smaller chunks)
        >>> code_config = VectorConfig(
        ...     model="microsoft/codebert-base",
        ...     chunk_size=200,
        ...     chunk_overlap=20,
        ...     dimension=768
        ... )

    Validation Rules:
        - chunk_size: 100-2000 tokens
        - chunk_overlap: 0-500 tokens, must be < chunk_size
        - dimension: 128-4096 (model-dependent)
        - index_type: Must be HNSW, IVF_PQ, or FLAT
    """

    model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model identifier (HuggingFace model name)",
        min_length=1,
    )

    chunk_size: int = Field(
        default=800,
        ge=100,
        le=2000,
        description="Text chunk size in tokens (100-2000)",
    )

    chunk_overlap: int = Field(
        default=100,
        ge=0,
        le=500,
        description="Overlap between chunks in tokens (0-500)",
    )

    dimension: int = Field(
        default=384,
        ge=128,
        le=4096,
        description="Embedding vector dimension (model-specific)",
    )

    index_type: str = Field(
        default="HNSW",
        pattern=r"^(HNSW|IVF_PQ|FLAT)$",
        description="Vector index algorithm (HNSW=fast, IVF_PQ=compressed, FLAT=exact)",
    )

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap_lt_chunk_size(cls, v: int, info) -> int:
        """
        Ensure chunk_overlap is less than chunk_size.

        Prevents configuration error where overlap >= size (invalid chunking).

        Args:
            v: chunk_overlap value
            info: Validation info containing other field values

        Returns:
            int: Validated chunk_overlap

        Raises:
            ValueError: If chunk_overlap >= chunk_size

        Example:
            >>> # Valid: overlap < size
            >>> VectorConfig(chunk_size=800, chunk_overlap=100)  # ✅
            >>> 
            >>> # Invalid: overlap >= size
            >>> VectorConfig(chunk_size=800, chunk_overlap=800)  # ❌ ValueError
        """
        chunk_size = info.data.get("chunk_size", 800)
        if v >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({v}) must be < chunk_size ({chunk_size})\n"
                f"Remediation: Set chunk_overlap to < {chunk_size} (recommended: {chunk_size // 8})"
            )
        return v


class FTSConfig(BaseConfig):
    """
    Full-text search (FTS) configuration for keyword matching.

    Configures BM25-based keyword search using LanceDB's native FTS.
    Complements vector search by matching exact terms and phrases.

    Key Settings:
        - enabled: Enable FTS index
        - use_tantivy: Use Tantivy backend (faster, more features)
        - tokenizer: Tokenization strategy

    Tokenizer Options:
        - default: Standard tokenization with stemming
        - standard: Unicode-aware tokenization
        - whitespace: Split on whitespace only
        - simple: Lowercase + split on non-alphanumeric

    Example:
        >>> from ouroboros.config.schemas.indexes import FTSConfig
        >>> 
        >>> # Enable FTS with default tokenizer
        >>> config = FTSConfig(enabled=True, tokenizer="default")
        >>> 
        >>> # Disable FTS (vector-only)
        >>> config = FTSConfig(enabled=False)

    Performance:
        - FTS adds ~10-20ms per query
        - Index size: ~5-10% of corpus size
        - Rebuild time: ~1-2 seconds per 1000 documents
    """

    enabled: bool = Field(
        default=True,
        description="Enable FTS index (keyword matching)",
    )

    use_tantivy: bool = Field(
        default=False,
        description="Use Tantivy backend (faster, more features, requires Rust)",
    )

    tokenizer: str = Field(
        default="default",
        pattern=r"^(default|standard|whitespace|simple)$",
        description="FTS tokenizer (default=stemming, standard=unicode, whitespace=split, simple=lowercase)",
    )


class RerankingConfig(BaseConfig):
    """
    Cross-encoder reranking configuration for result refinement.

    After initial hybrid search (vector + FTS), rerank top-K results using
    a cross-encoder model for improved precision. Adds ~20-50ms per query
    but significantly improves relevance.

    Key Settings:
        - enabled: Enable reranking
        - model: Cross-encoder model (e.g., "ms-marco-MiniLM-L-6-v2")
        - top_k: Rerank top K candidates (5-100)

    When to Enable:
        - Precision matters more than latency
        - Hybrid search returns too many false positives
        - Willing to accept +20-50ms query latency

    Example:
        >>> from ouroboros.config.schemas.indexes import RerankingConfig
        >>> 
        >>> # Enable reranking
        >>> config = RerankingConfig(
        ...     enabled=True,
        ...     model="cross-encoder/ms-marco-MiniLM-L-6-v2",
        ...     top_k=20
        ... )
        >>> 
        >>> # Disable reranking (faster queries)
        >>> config = RerankingConfig(enabled=False)

    Performance Impact:
        - Latency: +20-50ms per query (depends on top_k)
        - Precision improvement: +10-30% (dataset-dependent)
        - Memory: +100-200MB (model loading)
    """

    enabled: bool = Field(
        default=False,
        description="Enable cross-encoder reranking",
    )

    model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Cross-encoder model identifier (HuggingFace model name)",
        min_length=1,
    )

    top_k: int = Field(
        default=20,
        ge=5,
        le=100,
        description="Rerank top K candidates (5-100)",
    )


class ScalarIndexConfig(BaseConfig):
    """
    Configuration for a single scalar index on a metadata column.
    
    Scalar indexes enable fast filtering on metadata fields (e.g., domain, phase, role).
    LanceDB supports two index types:
        - BTREE: For high cardinality columns (many unique values)
        - BITMAP: For low cardinality columns (few unique values, < 1000)
    
    Key Settings:
        - column: Column name to index
        - index_type: BTREE or BITMAP
    
    Example:
        >>> from ouroboros.config.schemas.indexes import ScalarIndexConfig
        >>> 
        >>> # High cardinality (domains: workflow, rag, browser, etc.)
        >>> domain_idx = ScalarIndexConfig(column="domain", index_type="BTREE")
        >>> 
        >>> # Low cardinality (phases: 0-8)
        >>> phase_idx = ScalarIndexConfig(column="phase", index_type="BITMAP")
    
    Performance:
        - BTREE: O(log n) lookups, handles millions of unique values
        - BITMAP: O(1) lookups, best for < 1000 unique values
    """
    
    column: str = Field(
        ...,
        min_length=1,
        description="Column name to index (must exist in data schema)",
    )
    
    index_type: str = Field(
        ...,
        pattern=r"^(BTREE|BITMAP|btree|bitmap)$",
        description="Index type: BTREE (high cardinality) or BITMAP (low cardinality)",
    )


class MetadataFilteringConfig(BaseConfig):
    """
    Metadata filtering configuration for pre/post-filtering search results.
    
    Enables filtering search results by metadata fields (e.g., domain, phase, role).
    Requires scalar indexes on filtered columns for performance.
    
    Key Settings:
        - enabled: Enable metadata filtering
        - scalar_indexes: List of scalar indexes to create
        - auto_generate: Auto-detect columns and generate indexes
        - llm_enhance: Use LLM to extract additional metadata
    
    Example:
        >>> from ouroboros.config.schemas.indexes import (
        ...     MetadataFilteringConfig, ScalarIndexConfig
        ... )
        >>> 
        >>> config = MetadataFilteringConfig(
        ...     enabled=True,
        ...     scalar_indexes=[
        ...         ScalarIndexConfig(column="domain", index_type="BTREE"),
        ...         ScalarIndexConfig(column="phase", index_type="BITMAP"),
        ...         ScalarIndexConfig(column="role", index_type="BITMAP"),
        ...     ],
        ...     auto_generate=False,
        ...     llm_enhance=False
        ... )
    
    Filtering Usage:
        >>> # Filter by phase
        >>> results = search_standards(
        ...     query="workflow execution",
        ...     filters={"phase": 3}
        ... )
        >>> 
        >>> # Filter by multiple criteria
        >>> results = search_standards(
        ...     query="error handling",
        ...     filters={"domain": "workflow", "role": "agent"}
        ... )
    """
    
    enabled: bool = Field(
        default=False,
        description="Enable metadata filtering",
    )
    
    scalar_indexes: list["ScalarIndexConfig"] = Field(
        default_factory=list,
        description="Scalar indexes to create for filtering",
    )
    
    auto_generate: bool = Field(
        default=False,
        description="Auto-detect columns and generate scalar indexes",
    )
    
    llm_enhance: bool = Field(
        default=False,
        description="Use LLM to extract additional metadata from content",
    )


class GraphConfig(BaseConfig):
    """
    Graph traversal configuration for call graph analysis.

    Configures DuckDB recursive CTEs for call graph queries:
        - find_callers: Who calls this function?
        - find_dependencies: What does this function call?
        - find_call_paths: Show call chain from A to B

    Key Settings:
        - enabled: Enable graph traversal index
        - max_depth: Maximum recursion depth (1-100)
        - relationship_types: Relationship types to track

    Relationship Types:
        - calls: Function/method calls
        - imports: Module imports
        - inherits: Class inheritance

    Example:
        >>> from ouroboros.config.schemas.indexes import GraphConfig
        >>> 
        >>> config = GraphConfig(
        ...     enabled=True,
        ...     max_depth=10,
        ...     relationship_types=["calls", "imports", "inherits"]
        ... )

    Performance:
        - Shallow graphs (depth 1-3): <10ms
        - Medium graphs (depth 4-7): 10-50ms
        - Deep graphs (depth 8-10): 50-200ms

    Security:
        max_depth prevents infinite recursion in circular call graphs.
    """

    enabled: bool = Field(
        default=True,
        description="Enable graph traversal index (DuckDB call graph)",
    )

    max_depth: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max recursion depth for CTE queries (prevents infinite loops)",
    )

    relationship_types: list[str] = Field(
        default=["calls", "imports", "inherits"],
        description="Relationship types to track in graph",
        min_length=1,
    )


class FileWatcherConfig(BaseConfig):
    """
    File watcher configuration for incremental index updates.

    Monitors configured paths for file changes and triggers incremental
    re-indexing. Debouncing prevents rebuild storms during rapid changes.

    Key Settings:
        - enabled: Enable file watching
        - debounce_ms: Debounce delay in milliseconds
        - watch_patterns: File patterns to watch

    Debouncing Strategy:
        - Standards (markdown): 2000ms (docs change less frequently)
        - Code (Python/TS): 3000ms (code changes in bursts)

    Example:
        >>> from ouroboros.config.schemas.indexes import FileWatcherConfig
        >>> 
        >>> config = FileWatcherConfig(
        ...     enabled=True,
        ...     debounce_ms=2000,
        ...     watch_patterns=["*.md", "*.py", "*.ts"]
        ... )

    Performance:
        - Monitoring overhead: <1% CPU
        - Update latency: debounce_ms + rebuild time
        - Rebuild time: <5s for incremental updates
    """

    enabled: bool = Field(
        default=True,
        description="Enable file watching for incremental updates",
    )

    debounce_ms: int = Field(
        default=500,
        ge=100,
        le=5000,
        description="Debounce delay in milliseconds (prevents rebuild storms)",
    )

    watch_patterns: list[str] = Field(
        default=["*.md", "*.py", "*.go", "*.rs", "*.ts", "*.tsx"],
        description="File patterns to watch (glob patterns)",
        min_length=1,
    )


class StandardsIndexConfig(BaseConfig):
    """
    Configuration for standards index (documentation/markdown files).

    Implements hybrid search (vector + FTS + RRF) with optional reranking
    for searching project standards, docs, and knowledge base.

    Key Settings:
        - source_paths: Directories to index (relative to .praxis-os/)
        - vector: Vector search configuration
        - fts: Full-text search configuration
        - reranking: Optional cross-encoder reranking

    Search Strategy:
        1. Vector search: Semantic/meaning-based matching
        2. FTS: Keyword/exact term matching
        3. RRF: Reciprocal Rank Fusion (merge results)
        4. Rerank: Optional cross-encoder refinement

    Example:
        >>> from ouroboros.config.schemas.indexes import (
        ...     StandardsIndexConfig, VectorConfig, FTSConfig
        ... )
        >>> 
        >>> config = StandardsIndexConfig(
        ...     source_paths=["standards/", "docs/"],
        ...     vector=VectorConfig(chunk_size=800, chunk_overlap=100),
        ...     fts=FTSConfig(enabled=True),
        ...     reranking=None  # Disable reranking
        ... )

    Validation Rules:
        - source_paths: At least one path required
        - reranking: Optional (None = disabled)
    """

    source_paths: list[str] = Field(
        ...,
        min_length=1,
        description="Directories to index (relative to .praxis-os/)",
    )

    vector: VectorConfig = Field(
        ...,
        description="Vector search configuration",
    )

    fts: FTSConfig = Field(
        ...,
        description="Full-text search configuration",
    )

    reranking: Optional[RerankingConfig] = Field(
        default=None,
        description="Optional cross-encoder reranking (None = disabled)",
    )

    metadata_filtering: MetadataFilteringConfig = Field(
        default_factory=lambda: MetadataFilteringConfig(enabled=False),
        description="Metadata filtering configuration for pre/post-filtering",
    )



class ChunkingConfig(BaseConfig):
    """
    AST-aware chunking configuration for a language.

    Defines how code should be chunked at AST boundaries and how import
    statements should be penalized in search ranking.

    Key Settings:
        - import_nodes: AST node types for import/export statements
        - definition_nodes: AST node types for function/class definitions
        - split_boundary_nodes: AST node types for control flow boundaries
        - import_penalty: Score multiplier for import-heavy chunks (0.0-1.0)

    Chunking Strategy:
        1. Parse code with Tree-sitter into AST
        2. Identify chunks at definition boundaries (functions, classes)
        3. Group consecutive imports into single chunks
        4. Apply penalty to chunks with high import ratio

    Example:
        >>> from ouroboros.config.schemas.indexes import ChunkingConfig
        >>> 
        >>> # Python chunking config
        >>> config = ChunkingConfig(
        ...     import_nodes=["import_statement", "import_from_statement"],
        ...     definition_nodes=["function_definition", "class_definition"],
        ...     split_boundary_nodes=["if_statement", "for_statement"],
        ...     import_penalty=0.3
        ... )

    Validation Rules:
        - import_nodes: At least one node type required
        - definition_nodes: At least one node type required
        - split_boundary_nodes: Can be empty (no control flow chunking)
        - import_penalty: Float between 0.0 and 1.0
    """

    import_nodes: list[str] = Field(
        ...,
        min_length=1,
        description="AST node types for imports/exports (e.g., ['import_statement', 'export_statement'])",
    )

    definition_nodes: list[str] = Field(
        ...,
        min_length=1,
        description="AST node types for definitions (e.g., ['function_definition', 'class_definition'])",
    )

    split_boundary_nodes: list[str] = Field(
        default_factory=list,
        description="AST node types for control flow splits (e.g., ['if_statement', 'for_statement'])",
    )

    import_penalty: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Score multiplier for import-heavy chunks (0.0=filter out, 1.0=no penalty)",
    )


class LanguageConfig(BaseConfig):
    """
    Language-specific configuration for AST chunking.

    Defines all AST node types and chunking behavior for a programming language.
    Enables adding new languages via config without code changes.

    Key Settings:
        - chunking: AST-aware chunking configuration

    Config-Driven Design:
        - Add support for new languages by adding YAML entry
        - No code changes required per language
        - All logic driven by Tree-sitter node types

    Example:
        >>> from ouroboros.config.schemas.indexes import (
        ...     LanguageConfig, ChunkingConfig
        ... )
        >>> 
        >>> # Python language config
        >>> config = LanguageConfig(
        ...     chunking=ChunkingConfig(
        ...         import_nodes=["import_statement", "import_from_statement"],
        ...         definition_nodes=["function_definition", "async_function_definition", "class_definition"],
        ...         split_boundary_nodes=["if_statement", "for_statement", "while_statement"],
        ...         import_penalty=0.3
        ...     )
        ... )

    Usage in mcp.yaml:
        indexes:
          code:
            language_configs:
              python:
                chunking:
                  import_nodes: ["import_statement", "import_from_statement"]
                  definition_nodes: ["function_definition", "class_definition"]
                  split_boundary_nodes: ["if_statement", "for_statement"]
                  import_penalty: 0.3
              typescript:
                chunking:
                  import_nodes: ["import_statement", "export_statement"]
                  definition_nodes: ["function_declaration", "class_declaration"]
                  split_boundary_nodes: ["if_statement", "for_statement"]
                  import_penalty: 0.3
    """

    chunking: ChunkingConfig = Field(
        ...,
        description="AST-aware chunking configuration",
    )


class DomainConfig(BaseConfig):
    """
    Configuration for a domain within a partition (e.g., code, tests, docs).

    Defines what content to index within a repository using include/exclude patterns.
    Leverages existing .gitignore support with additional exclusion flexibility.

    Key Settings:
        - include_paths: Directories to index within the repo
        - exclude_patterns: Additional exclusion patterns (gitignore format)
        - metadata: Arbitrary key-value pairs for query filtering

    Metadata Field (NEW - AI-Friendly Querying):
        Optional dict of string key-value pairs that get attached to all chunks
        from this domain. Makes it easy for AI to filter searches without parsing
        file paths or guessing repo structure.

        Common metadata patterns:
            - framework: "openai", "anthropic", "langchain"
            - type: "instrumentor", "core", "tests"
            - provider: "openlit", "traceloop", "arize"
            - language: "python", "typescript", "go"
            - Custom: any domain-specific tags

    Exclusion Strategy (3-tier system):
        1. Language-specific defaults (node_modules/, target/, etc.)
        2. .gitignore patterns (automatically respected)
        3. exclude_patterns (config override for additional exclusions)

    Example:
        >>> from ouroboros.config.schemas.indexes import DomainConfig
        >>> 
        >>> # Index source code directories
        >>> code_domain = DomainConfig(
        ...     include_paths=["ouroboros/", "scripts/"],
        ...     exclude_patterns=None,
        ...     metadata=None
        ... )
        >>> 
        >>> # Index instrumentor with rich metadata for filtering
        >>> openai_instrumentor = DomainConfig(
        ...     include_paths=["instrumentation/openai/"],
        ...     exclude_patterns=None,
        ...     metadata={
        ...         "framework": "openai",
        ...         "type": "instrumentor",
        ...         "provider": "openlit"
        ...     }
        ... )
        >>> 
        >>> # Index tests with custom exclusions
        >>> tests_domain = DomainConfig(
        ...     include_paths=["tests/"],
        ...     exclude_patterns=["tests/__pycache__/"],
        ...     metadata={"type": "tests"}
        ... )

    Usage in mcp.yaml:
        partitions:
          praxis-os:
            path: ../
            domains:
              code:
                include_paths: [ouroboros/, scripts/]
                exclude_patterns: null
                metadata: null
              tests:
                include_paths: [tests/]
                exclude_patterns: null
                metadata:
                  type: tests
          
          openlit:
            path: ../deps/openlit
            domains:
              openai-instrumentor:
                include_paths: [instrumentation/openai/]
                exclude_patterns: null
                metadata:
                  framework: openai
                  type: instrumentor
                  provider: openlit
    """

    include_paths: list[str] = Field(
        ...,
        min_length=1,
        description="Directories to index within the repository (e.g., ['src/', 'lib/'])",
    )

    exclude_patterns: Optional[list[str]] = Field(
        default=None,
        description="Additional exclusion patterns in gitignore format (e.g., ['*.log', 'tmp/'])",
    )

    metadata: Optional[dict[str, str]] = Field(
        default=None,
        description="Arbitrary metadata for query filtering (e.g., {'framework': 'openai', 'type': 'instrumentor'})",
    )


class PartitionConfig(BaseConfig):
    """
    Configuration for a single repository partition.

    One partition = one repository with multiple domains (code, tests, docs).
    Each domain defines what directories to index with include/exclude patterns.

    Design Philosophy:
        - Simple 1:1 mapping (partition name = repo name)
        - Domain-agnostic (works for any project type)
        - Flexible indexing (different patterns per domain)
        - Leverages existing .gitignore support

    Key Settings:
        - path: Repository location (relative to .praxis-os/)
        - domains: Dict of domain configs (code, tests, docs, etc.)

    Example:
        >>> from ouroboros.config.schemas.indexes import PartitionConfig, DomainConfig
        >>> 
        >>> # Single repo with code and tests domains
        >>> praxis_partition = PartitionConfig(
        ...     path="../",
        ...     domains={
        ...         "code": DomainConfig(
        ...             include_paths=["ouroboros/", "scripts/"],
        ...             exclude_patterns=None
        ...         ),
        ...         "tests": DomainConfig(
        ...             include_paths=["tests/"],
        ...             exclude_patterns=None
        ...         )
        ...     }
        ... )

    Usage in mcp.yaml:
        partitions:
          praxis-os:              # Partition name = repo name
            path: ../             # Repo location
            domains:              # Explicit domains field
              code:               # Domain: source code
                include_paths: [ouroboros/, scripts/]
                exclude_patterns: null
              tests:              # Domain: tests
                include_paths: [tests/]
                exclude_patterns: null
          
          python-sdk:             # Another repo
            path: ../python-sdk
            domains:
              code:
                include_paths: [src/]
                exclude_patterns: null

    Domain Names:
        - Common: code, tests, docs, examples
        - Custom: Any string works (e.g., "frontend", "backend", "api")
        - Flexible: Define domains that match your project structure

    Validation Rules:
        - path must be a non-empty string
        - domains must have at least one entry
        - domain names must be valid Python identifiers (no spaces/special chars)
    """

    path: str = Field(
        ...,
        min_length=1,
        description="Repository path relative to .praxis-os/ (e.g., '../', '../python-sdk/')",
    )

    domains: dict[str, DomainConfig] = Field(
        ...,
        min_length=1,
        description="Domain configurations (e.g., {'code': DomainConfig(...), 'tests': DomainConfig(...)})",
    )

    @field_validator("domains")
    @classmethod
    def validate_domain_names(cls, v: dict[str, DomainConfig]) -> dict[str, DomainConfig]:
        """
        Ensure domain names are valid identifiers.

        Domain names should be simple, descriptive strings that work as
        Python identifiers (used in code and queries).

        Args:
            v: domains dict

        Returns:
            dict[str, DomainConfig]: Validated domains

        Raises:
            ValueError: If domain name contains invalid characters

        Example:
            >>> # Valid domain names
            >>> domains = {"code": DomainConfig(...), "tests": DomainConfig(...)}  # ✅
            >>> 
            >>> # Invalid: spaces and special chars
            >>> domains = {"my code": DomainConfig(...)}  # ❌
            >>> domains = {"code-v2": DomainConfig(...)}  # ❌
        """
        for domain_name in v.keys():
            if not domain_name.isidentifier():
                raise ValueError(
                    f"Invalid domain name '{domain_name}': must be a valid Python identifier\n"
                    f"Domain names should be simple strings like: code, tests, docs, examples\n"
                    f"Avoid spaces, hyphens, and special characters\n"
                    f"Remediation: Use '{domain_name.replace('-', '_').replace(' ', '_')}' instead"
                )
        
        return v


class CodeIndexConfig(BaseConfig):
    """
    Configuration for code index (LanceDB semantic + DuckDB graph).

    Dual-index system for code search:
        - LanceDB: Semantic code search (vector + FTS + hybrid)
        - DuckDB: Call graph traversal (recursive CTEs)

    Key Settings:
        - source_paths: Code directories to index
        - languages: Programming languages to support
        - vector: Vector search config (CodeBERT)
        - fts: Full-text search config
        - duckdb_path: DuckDB database path
        - graph: Graph traversal config
        - language_configs: Language-specific AST chunking configs (optional)
        - chunking_strategy: "ast" (AST-aware) or "line" (line-based fallback)
        - partitions: Multi-repo partitioning configuration (NEW)

    Supported Languages:
        - Python, TypeScript, JavaScript, Go, Rust
        - Config-driven: Add via YAML, no code changes

    AST-Aware Chunking (NEW):
        - chunking_strategy="ast": Use Tree-sitter to chunk at function/class boundaries
        - Applies import_penalty to de-prioritize import-heavy chunks
        - Graceful fallback to line-based chunking if AST parsing fails
        - Config-driven via language_configs (no hardcoded logic)

    Example:
        >>> from ouroboros.config.schemas.indexes import (
        ...     CodeIndexConfig, VectorConfig, FTSConfig, GraphConfig,
        ...     LanguageConfig, ChunkingConfig
        ... )
        >>> 
        >>> config = CodeIndexConfig(
        ...     source_paths=["src/", "lib/"],
        ...     languages=["python", "typescript"],
        ...     vector=VectorConfig(
        ...         model="microsoft/codebert-base",
        ...         chunk_size=200,
        ...         dimension=768
        ...     ),
        ...     fts=FTSConfig(enabled=True),
        ...     duckdb_path=Path(".praxis-os/code.duckdb"),
        ...     graph=GraphConfig(max_depth=10),
        ...     chunking_strategy="ast",
        ...     language_configs={
        ...         "python": LanguageConfig(
        ...             chunking=ChunkingConfig(
        ...                 import_nodes=["import_statement", "import_from_statement"],
        ...                 definition_nodes=["function_definition", "class_definition"],
        ...                 split_boundary_nodes=["if_statement", "for_statement"],
        ...                 import_penalty=0.3
        ...             )
        ...         )
        ...     }
        ... )

    Validation Rules:
        - source_paths: At least one path required
        - languages: At least one language required
        - chunking_strategy: Must be "ast" or "line"
    """

    source_paths: list[str] = Field(
        ...,
        min_length=1,
        description="Code directories to index (e.g., ['src/', 'lib/'])",
    )

    languages: list[str] = Field(
        ...,
        min_length=1,
        description="Programming languages to support (e.g., ['python', 'typescript'])",
    )

    vector: VectorConfig = Field(
        ...,
        description="Vector search configuration (recommend CodeBERT)",
    )

    fts: FTSConfig = Field(
        ...,
        description="Full-text search configuration",
    )

    duckdb_path: Path = Field(
        default=Path(".praxis-os/code.duckdb"),
        description="DuckDB database path for call graph",
    )

    graph: GraphConfig = Field(
        ...,
        description="Graph traversal configuration",
    )

    respect_gitignore: bool = Field(
        default=True,
        description="Respect .gitignore patterns when indexing files (recommended: True)",
    )

    exclude_patterns: Optional[list[str]] = Field(
        default=None,
        description="Additional exclusion patterns in gitignore format (merged with .gitignore if present)",
    )

    chunking_strategy: str = Field(
        default="ast",
        pattern=r"^(ast|line)$",
        description="Chunking strategy: 'ast' (AST-aware, recommended) or 'line' (line-based fallback)",
    )

    language_configs: Optional[dict[str, LanguageConfig]] = Field(
        default=None,
        description="Language-specific AST chunking configs (e.g., {'python': LanguageConfig(...)})",
    )

    partitions: Optional[dict[str, PartitionConfig]] = Field(
        default=None,
        description="Multi-repo partitions (e.g., {'primary': PartitionConfig(...), 'instrumentors': PartitionConfig(...)})",
    )



class ASTIndexConfig(BaseConfig):
    """
    Configuration for AST index (Tree-sitter structural search).

    Parses source code into Abstract Syntax Trees for structural queries:
        - Find all async functions
        - Find all classes with specific methods
        - Find all error handling blocks

    Key Settings:
        - enabled: Enable AST structural search index
        - source_paths: Code directories to parse
        - languages: Languages to support (Tree-sitter parsers)
        - auto_install_parsers: Auto-install missing parsers
        - venv_path: Isolated venv for parser installation

    Auto-Install Behavior:
        If enabled, server will `pip install tree-sitter-{language}` for
        any missing parser on startup. Requires internet access.

    Example:
        >>> from ouroboros.config.schemas.indexes import ASTIndexConfig
        >>> 
        >>> config = ASTIndexConfig(
        ...     enabled=True,
        ...     source_paths=["src/", "lib/"],
        ...     languages=["python", "typescript", "rust"],
        ...     auto_install_parsers=True,
        ...     venv_path=Path(".praxis-os/venv")
        ... )

    Validation Rules:
        - source_paths: At least one path required
        - languages: At least one language required

    Security:
        Parser installation uses isolated venv (no system pollution).
    """

    enabled: bool = Field(
        default=True,
        description="Enable AST structural search index (Tree-sitter)",
    )

    source_paths: list[str] = Field(
        ...,
        min_length=1,
        description="Code directories to parse (e.g., ['src/', 'lib/'])",
    )

    languages: list[str] = Field(
        ...,
        min_length=1,
        description="Languages to support (e.g., ['python', 'typescript'])",
    )

    auto_install_parsers: bool = Field(
        default=True,
        description="Auto-install missing Tree-sitter parsers (requires internet)",
    )

    venv_path: Path = Field(
        default=Path(".praxis-os/venv"),
        description="Isolated venv for parser installation",
    )



class IndexBuildConfig(BaseConfig):
    """Configuration for resilient index building.
    
    Provides configurable thresholds, retry policies, and TTLs for robust
    index building with graceful degradation and auto-repair.
    
    Key Settings:
        - disk_space_threshold_gb: Minimum free disk space required (GB)
        - max_retries: Maximum retry attempts for transient failures
        - retry_backoff_base: Exponential backoff base (seconds)
        - transient_error_keywords: Keywords to identify transient errors
        - *_error_ttl_hours: TTL for different error types
        - report_progress_per_component: Enable component-level progress
        - telemetry_enabled: Enable telemetry event emission
    
    Error TTL Strategy:
        - Config errors: No TTL (persist until restart) - requires code/config fix
        - Transient errors: 24h TTL - external issues may resolve
        - Resource errors: 1h TTL - disk/memory issues should be fixed quickly
    
    Validation Warnings:
        Logs warnings for potentially unsafe config overrides:
        - Disk space threshold <1GB (may cause mid-build failures)
        - Max retries >5 (may delay failure detection)
        - Max retries =0 (disables retry for transient failures)
        - Transient TTL <1h (may cause frequent rebuild attempts)
        - Resource TTL >24h (resource issues should be fixed quickly)
        - Backoff base >5.0 (may cause excessive delays)
    
    Example:
        >>> from ouroboros.config.schemas.indexes import IndexBuildConfig
        >>> 
        >>> # Production config (safe defaults)
        >>> config = IndexBuildConfig(
        ...     disk_space_threshold_gb=2.0,
        ...     max_retries=3,
        ...     retry_backoff_base=2.0,
        ...     transient_error_ttl_hours=24.0,
        ...     resource_error_ttl_hours=1.0,
        ...     report_progress_per_component=True,
        ...     telemetry_enabled=False
        ... )
        >>> 
        >>> # Development config (aggressive retries)
        >>> dev_config = IndexBuildConfig(
        ...     disk_space_threshold_gb=0.5,  # ⚠️ Warning logged
        ...     max_retries=5,  # ⚠️ Warning logged
        ...     transient_error_ttl_hours=1.0,  # ⚠️ Warning logged
        ... )
    
    Traceability:
        FR-029: IndexBuildConfig Schema
        FR-030: Config Validation Warnings
    """
    
    disk_space_threshold_gb: float = Field(
        default=2.0,
        ge=0.1,
        description="Minimum free disk space required to build (GB)"
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Max retries for transient failures"
    )
    
    retry_backoff_base: float = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="Exponential backoff base (seconds)"
    )
    
    transient_error_keywords: List[str] = Field(
        default_factory=lambda: [
            "timeout",
            "connection",
            "network",
            "temporary",
            "unavailable",
            "model download",
        ],
        description="Keywords to identify transient errors"
    )
    
    config_error_ttl_hours: Optional[float] = Field(
        default=None,
        description="TTL for config errors (None = until restart)"
    )
    
    transient_error_ttl_hours: float = Field(
        default=24.0,
        ge=0.1,
        description="TTL for transient errors (hours)"
    )
    
    resource_error_ttl_hours: float = Field(
        default=1.0,
        ge=0.1,
        description="TTL for resource errors (hours)"
    )
    
    report_progress_per_component: bool = Field(
        default=True,
        description="Report progress at component level"
    )
    
    telemetry_enabled: bool = Field(
        default=False,
        description="Enable telemetry event emission"
    )
    
    @model_validator(mode="after")
    def validate_config(self) -> "IndexBuildConfig":
        """Validate config and log warnings for unsafe overrides.
        
        Warnings logged for:
            - Disk space threshold <1GB
            - Max retries >5 or =0
            - TTLs too short (<1h for transient)
            - Backoff base too high (>5.0)
        
        Returns:
            Self (for method chaining)
        """
        # Warn if disk space threshold is too low
        if self.disk_space_threshold_gb < 1.0:
            logger.warning(
                "⚠️  Low disk_space_threshold_gb (%.1fGB). "
                "Recommended: 2GB+ to prevent mid-build failures. "
                "Current setting may cause frequent build failures.",
                self.disk_space_threshold_gb
            )
        
        # Warn if max_retries is too high
        if self.max_retries > 5:
            logger.warning(
                "⚠️  High max_retries (%d). "
                "May delay failure detection and mask persistent issues. "
                "Recommended: 3 retries for transient failures.",
                self.max_retries
            )
        
        # Warn if max_retries is disabled
        if self.max_retries == 0:
            logger.warning(
                "⚠️  Retries disabled (max_retries=0). "
                "Transient failures (network timeouts, model downloads) will fail immediately. "
                "Recommended: 3 retries."
            )
        
        # Warn if TTLs are too short
        if self.transient_error_ttl_hours < 1.0:
            logger.warning(
                "⚠️  Short transient_error_ttl_hours (%.1fh). "
                "May cause frequent rebuild attempts for persistent issues. "
                "Recommended: 24h to allow time for external issues to resolve.",
                self.transient_error_ttl_hours
            )
        
        # Warn if resource error TTL is too long
        if self.resource_error_ttl_hours > 24.0:
            logger.warning(
                "⚠️  Long resource_error_ttl_hours (%.1fh). "
                "Resource issues (disk space, memory) should be resolved quickly. "
                "Recommended: 1h to encourage prompt resolution.",
                self.resource_error_ttl_hours
            )
        
        # Warn if backoff base is too high
        if self.retry_backoff_base > 5.0:
            logger.warning(
                "⚠️  High retry_backoff_base (%.1fs). "
                "May cause excessive delays between retries. "
                "Recommended: 2.0s for balanced retry timing.",
                self.retry_backoff_base
            )
        
        return self


class IndexesConfig(BaseConfig):
    """
    Root configuration for all RAG indexes.

    Composes StandardsIndex, CodeIndex, and ASTIndex configurations with
    shared settings for caching and file watching.

    Key Settings:
        - standards: Standards index configuration
        - code: Code index configuration
        - ast: AST index configuration
        - cache_path: Base cache path for all indexes
        - file_watcher: File monitoring configuration
        - build: Resilient index building configuration

    Cache Structure:
        .praxis-os/.cache/indexes/
        ├── standards/        # Standards vector index (LanceDB)
        ├── code/             # Code vector index (LanceDB) + graph (DuckDB)
        └── ast/              # AST index (SQLite)

    Example:
        >>> from ouroboros.config.schemas.indexes import (
        ...     IndexesConfig, StandardsIndexConfig, CodeIndexConfig, ASTIndexConfig
        ... )
        >>> 
        >>> config = IndexesConfig(
        ...     standards=StandardsIndexConfig(...),
        ...     code=CodeIndexConfig(...),
        ...     ast=ASTIndexConfig(...),
        ...     cache_path=Path(".cache/indexes"),  # Relative to base_path
        ...     file_watcher=FileWatcherConfig(enabled=True),
        ...     build=IndexBuildConfig()  # Use defaults
        ... )

    Validation:
        All nested configs are validated on creation (fail-fast).
    """

    standards: StandardsIndexConfig = Field(
        ...,
        description="Standards index configuration",
    )

    code: CodeIndexConfig = Field(
        ...,
        description="Code index configuration",
    )

    ast: ASTIndexConfig = Field(
        ...,
        description="AST index configuration",
    )

    cache_path: Path = Field(
        default=Path(".cache/indexes"),
        description="Base cache path for all indexes (relative to base_path)",
    )

    file_watcher: FileWatcherConfig = Field(
        ...,
        description="File watcher configuration",
    )
    
    build: IndexBuildConfig = Field(
        default_factory=IndexBuildConfig,
        description="Resilient index building configuration",
    )


__all__ = [
    "VectorConfig",
    "FTSConfig",
    "RerankingConfig",
    "GraphConfig",
    "FileWatcherConfig",
    "ChunkingConfig",
    "LanguageConfig",
    "DomainConfig",
    "PartitionConfig",
    "StandardsIndexConfig",
    "CodeIndexConfig",
    "ASTIndexConfig",
    "IndexBuildConfig",
    "IndexesConfig",
    "MetadataFilteringConfig",
]


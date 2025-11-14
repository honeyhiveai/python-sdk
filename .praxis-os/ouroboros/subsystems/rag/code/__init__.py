"""Code index submodule - semantic + graph search for code.

This submodule provides dual-database search capabilities for code:
1. Semantic search (LanceDB): Vector-based similarity search for code snippets
2. Graph search (DuckDB): AST traversal and call graph analysis

Architecture:
    - container.py: CodeIndex (implements BaseIndex, orchestrates semantic + graph)
    - semantic.py: SemanticIndex (internal LanceDB implementation)
    - graph.py: GraphIndex (internal DuckDB implementation for AST + call graph)

The container pattern provides:
    - Uniform interface (BaseIndex) for IndexManager
    - Internal orchestration of semantic and graph indexes
    - Lock management for build/update operations
    - Composite search (semantic + graph results)

Usage:
    >>> from ouroboros.subsystems.rag.code import CodeIndex
    >>> 
    >>> index = CodeIndex(config, base_path)
    >>> index.build(source_paths)
    >>> # Semantic search
    >>> results = index.search("how to parse json", n_results=5)
    >>> # Graph traversal
    >>> callers = index.find_callers("process_data", max_depth=3)

Exports:
    CodeIndex: Main interface for code search (from container.py)

Traceability:
    - FR-001: Uniform container entry point pattern
    - FR-002: Dual database orchestration (semantic + graph)
    - FR-007: Internal implementation hidden from IndexManager
    - Implementation Pattern 3: Complex submodule (dual databases)
"""

from ouroboros.subsystems.rag.code.container import CodeIndex

__all__ = ["CodeIndex"]


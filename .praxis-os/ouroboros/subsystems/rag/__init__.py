"""RAG (Retrieval-Augmented Generation) Subsystem for Ouroboros.

This subsystem provides multi-index search capabilities:
- Standards: Vector + FTS + RRF hybrid search
- Code: Semantic search (LanceDB) + Graph traversal (DuckDB)
- AST: Structural code search (Tree-sitter)

Mission: Enable AI agents to discover project-specific knowledge through
semantic search, preventing reliance on training data.
"""

from ouroboros.subsystems.rag.index_manager import IndexManager

__all__ = ["IndexManager"]


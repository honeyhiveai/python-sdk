"""Shared utility modules for RAG subsystem.

Provides reusable components for:
- LanceDB connection management and embedding models
- DuckDB connection pooling and query execution
- Corruption detection and auto-repair

These utilities eliminate code duplication across index implementations
and provide consistent error handling with ActionableError.

Modules:
    lancedb_helpers: LanceDBConnection, EmbeddingModelLoader
    duckdb_helpers: DuckDBConnection with thread-safe pooling
    corruption_detector: Pattern matching for corruption errors

Usage:
    >>> from ouroboros.subsystems.rag.utils.lancedb_helpers import LanceDBConnection
    >>> conn = LanceDBConnection(Path("/path/to/db"))
    >>> db = conn.connect()
"""

from ouroboros.subsystems.rag.utils.corruption_detector import is_corruption_error
from ouroboros.subsystems.rag.utils.duckdb_helpers import DuckDBConnection
from ouroboros.subsystems.rag.utils.lancedb_helpers import (
    EmbeddingModelLoader,
    LanceDBConnection,
)

__all__ = [
    "LanceDBConnection",
    "EmbeddingModelLoader",
    "DuckDBConnection",
    "is_corruption_error",
]


"""LanceDB connection management and embedding model loading utilities.

Provides reusable components for LanceDB operations across all indexes:
- Lazy connection initialization
- Table opening with error handling
- Singleton embedding model caching

These utilities eliminate duplication and provide consistent error handling
with ActionableError messages.

Classes:
    LanceDBConnection: Manages LanceDB connection lifecycle
    EmbeddingModelLoader: Singleton model loader with caching

Usage:
    >>> from ouroboros.subsystems.rag.utils.lancedb_helpers import (
    ...     LanceDBConnection,
    ...     EmbeddingModelLoader
    ... )
    >>> 
    >>> # Connection management
    >>> conn = LanceDBConnection(Path("/path/to/db"))
    >>> db = conn.connect()  # Lazy init
    >>> table = conn.open_table("my_table")
    >>> 
    >>> # Model loading (cached)
    >>> model = EmbeddingModelLoader.load("all-MiniLM-L6-v2")
    >>> embeddings = model.encode(["text1", "text2"])

Traceability:
    - FR-006: Shared utilities eliminate duplication
    - Implementation Pattern 4: Shared utility modules
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


def safe_encode(model: Any, texts: Union[str, List[str]], **kwargs) -> Any:
    """Safely encode text using sentence-transformers with threading backend.
    
    Forces joblib to use threading backend to avoid Python 3.13 semaphore leaks.
    
    Args:
        model: SentenceTransformer model instance
        texts: Single text or list of texts to encode
        **kwargs: Additional arguments to pass to model.encode()
    
    Returns:
        Embeddings array
    """
    try:
        import joblib
        # Force threading backend for this encode call
        with joblib.parallel_backend('threading'):
            return model.encode(texts, **kwargs)
    except ImportError:
        # Fallback if joblib not available (shouldn't happen)
        return model.encode(texts, **kwargs)


class LanceDBConnection:
    """Manages LanceDB connection with lazy initialization and error handling.

    Provides a reusable connection manager that:
    - Initializes database connection only when needed (lazy init)
    - Creates database directory if missing
    - Handles import errors with actionable fix guidance
    - Provides consistent error messages across indexes

    The connection is cached after first use, so subsequent calls to connect()
    return the same database instance.

    Attributes:
        db_path: Path to LanceDB database directory
        _db: Cached database connection (None until first connect())

    Example:
        >>> conn = LanceDBConnection(Path("/tmp/lance"))
        >>> db = conn.connect()  # Creates dir, connects
        >>> db2 = conn.connect()  # Returns cached connection
        >>> assert db is db2  # Same instance
    """

    def __init__(self, db_path: Path) -> None:
        """Initialize connection manager.

        Args:
            db_path: Path to LanceDB database directory (created if missing)

        Note:
            Connection is not established until connect() is called.
            This allows construction without side effects.
        """
        self.db_path = db_path
        self._db: Optional[Any] = None

    def connect(self) -> Any:
        """Get or create LanceDB connection (lazy initialization).

        Creates database directory if it doesn't exist. Connection is cached
        after first call.

        Returns:
            LanceDB database object (lancedb.db.DBConnection)

        Raises:
            ActionableError: If lancedb not installed or connection fails
                - ImportError: Package not installed
                - PermissionError: Directory not writable
                - Other errors: Generic connection failure

        Example:
            >>> conn = LanceDBConnection(Path("/tmp/lance"))
            >>> db = conn.connect()
            >>> # Use db for operations
        """
        if self._db is None:
            try:
                import lancedb

                # Create directory if missing
                self.db_path.mkdir(parents=True, exist_ok=True)

                # Connect to database
                self._db = lancedb.connect(str(self.db_path))
                logger.info("✅ Connected to LanceDB at %s", self.db_path)

            except ImportError as e:
                raise ActionableError(
                    what_failed="LanceDB import",
                    why_failed="lancedb package not installed",
                    how_to_fix="Install via: pip install 'lancedb>=0.13.0'",
                ) from e
            except PermissionError as e:
                raise ActionableError(
                    what_failed="Create LanceDB directory",
                    why_failed=f"Permission denied: {self.db_path}",
                    how_to_fix=f"Ensure {self.db_path.parent} is writable or use different path",
                ) from e
            except Exception as e:
                raise ActionableError(
                    what_failed="LanceDB connection",
                    why_failed=str(e),
                    how_to_fix=f"Check that {self.db_path.parent} is writable and accessible",
                ) from e

        return self._db

    def open_table(self, table_name: str) -> Any:
        """Open LanceDB table with error handling.

        Args:
            table_name: Name of table to open

        Returns:
            LanceDB table object (lancedb.table.Table)

        Raises:
            ActionableError: If table doesn't exist or cannot be opened
                - FileNotFoundError: Table not found (needs build)
                - Other errors: Corruption or integrity issues

        Example:
            >>> conn = LanceDBConnection(Path("/tmp/lance"))
            >>> table = conn.open_table("standards")
            >>> results = table.search("query").limit(5).to_list()
        """
        try:
            db = self.connect()
            table = db.open_table(table_name)
            logger.info("✅ Opened table: %s", table_name)
            return table

        except FileNotFoundError as e:
            raise ActionableError(
                what_failed=f"Open LanceDB table '{table_name}'",
                why_failed="Table does not exist",
                how_to_fix="Run build first: index.build(source_paths)",
            ) from e
        except Exception as e:
            # Could be corruption, permission issues, etc.
            error_str = str(e).lower()
            if "corrupt" in error_str or "invalid" in error_str:
                raise ActionableError(
                    what_failed=f"Open LanceDB table '{table_name}'",
                    why_failed=f"Table may be corrupted: {e}",
                    how_to_fix="Rebuild index with force=True: index.build(source_paths, force=True)",
                ) from e
            else:
                raise ActionableError(
                    what_failed=f"Open LanceDB table '{table_name}'",
                    why_failed=str(e),
                    how_to_fix="Check database integrity, permissions, or rebuild",
                ) from e

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "connected" if self._db is not None else "not connected"
        return f"LanceDBConnection(path='{self.db_path}', status={status})"


class EmbeddingModelLoader:
    """Singleton embedding model loader with class-level cache.

    Loads sentence-transformer embedding models with caching to prevent
    redundant loading. Uses class-level cache so models are shared across
    all index instances.

    This is critical for performance - loading models is expensive (seconds),
    but encoding is fast (milliseconds). Cache ensures we load once per model.

    Attributes:
        _model_cache: Class-level dict mapping model_name -> model instance

    Example:
        >>> # First load (slow: ~2-5s)
        >>> model1 = EmbeddingModelLoader.load("all-MiniLM-L6-v2")
        >>> 
        >>> # Second load (instant: cached)
        >>> model2 = EmbeddingModelLoader.load("all-MiniLM-L6-v2")
        >>> assert model1 is model2  # Same instance
        >>> 
        >>> # Encode text
        >>> embeddings = model1.encode(["hello", "world"])
    """

    _model_cache: Dict[str, Any] = {}

    @classmethod
    def load(cls, model_name: str) -> Any:
        """Load or retrieve cached embedding model.

        Args:
            model_name: HuggingFace model identifier
                Examples: "all-MiniLM-L6-v2", "all-mpnet-base-v2"

        Returns:
            SentenceTransformer model instance (cached)

        Raises:
            ActionableError: If sentence-transformers not installed or load fails
                - ImportError: Package not installed
                - OSError: Network error (model download)
                - Other errors: Model loading failure

        Example:
            >>> model = EmbeddingModelLoader.load("all-MiniLM-L6-v2")
            >>> embeddings = model.encode(["text1", "text2"])
            >>> print(embeddings.shape)  # (2, 384)
        """
        if model_name not in cls._model_cache:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info("Loading embedding model: %s", model_name)
                model = SentenceTransformer(model_name)
                cls._model_cache[model_name] = model
                logger.info("✅ Model loaded: %s", model_name)

            except ImportError as e:
                raise ActionableError(
                    what_failed="SentenceTransformer import",
                    why_failed="sentence-transformers package not installed",
                    how_to_fix="Install via: pip install sentence-transformers",
                ) from e
            except OSError as e:
                # Network errors during download
                raise ActionableError(
                    what_failed=f"Download embedding model '{model_name}'",
                    why_failed=f"Network error or model not found: {e}",
                    how_to_fix=(
                        "Options:\n"
                        "1. Check internet connection\n"
                        "2. Verify model name is correct (see: huggingface.co/models)\n"
                        "3. Use local model cache if available"
                    ),
                ) from e
            except Exception as e:
                raise ActionableError(
                    what_failed=f"Load embedding model '{model_name}'",
                    why_failed=str(e),
                    how_to_fix="Check model name is valid or use different model",
                ) from e

        return cls._model_cache[model_name]

    @classmethod
    def clear_cache(cls) -> None:
        """Clear model cache (useful for testing or memory management).

        Example:
            >>> EmbeddingModelLoader.load("all-MiniLM-L6-v2")
            >>> EmbeddingModelLoader.clear_cache()
            >>> # Next load will re-download/load model
        """
        cls._model_cache.clear()
        logger.info("Embedding model cache cleared")

    @classmethod
    def cached_models(cls) -> list[str]:
        """Get list of currently cached model names.

        Returns:
            List of model names in cache

        Example:
            >>> EmbeddingModelLoader.load("all-MiniLM-L6-v2")
            >>> EmbeddingModelLoader.load("all-mpnet-base-v2")
            >>> print(EmbeddingModelLoader.cached_models())
            ['all-MiniLM-L6-v2', 'all-mpnet-base-v2']
        """
        return list(cls._model_cache.keys())


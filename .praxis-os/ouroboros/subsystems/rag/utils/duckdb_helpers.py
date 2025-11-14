"""DuckDB connection management with thread-safe pooling.

Provides reusable DuckDB connection manager with:
- Lazy initialization
- Thread-safe connection handling
- Parameter binding for safe queries
- Consistent error handling

Classes:
    DuckDBConnection: Thread-safe DuckDB connection manager

Usage:
    >>> from ouroboros.subsystems.rag.utils.duckdb_helpers import DuckDBConnection
    >>> 
    >>> conn = DuckDBConnection(Path("/path/to/db.duckdb"))
    >>> 
    >>> # Execute query with parameter binding
    >>> results = conn.execute(
    ...     "SELECT * FROM symbols WHERE name = ?",
    ...     params=("my_function",)
    ... )
    >>> 
    >>> # Execute without parameters
    >>> results = conn.execute("SELECT COUNT(*) FROM symbols")

Traceability:
    - FR-006: Shared utilities eliminate duplication
    - FR-004: DuckDB replaces SQLite for graph operations
    - Implementation Pattern 4: Shared utility modules
"""

import logging
import threading
from pathlib import Path
from typing import Any, List, Optional, Tuple

from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class DuckDBConnection:
    """Thread-safe DuckDB connection manager with lazy initialization.

    Manages DuckDB connection lifecycle with thread-local storage to ensure
    thread safety. Each thread gets its own connection to prevent concurrent
    access issues.

    DuckDB Connection Model:
        - In-memory mode: Fast, no persistence (:memory:)
        - File mode: Persistent, thread-safe with separate connections per thread
        - Read-only mode: Multiple readers, single writer

    Attributes:
        db_path: Path to DuckDB database file (or ":memory:")
        _local: ThreadLocal storage for per-thread connections
        _lock: RLock for thread-safe connection creation

    Thread Safety:
        - Uses threading.local() for per-thread connections
        - RLock protects connection creation
        - Each thread gets independent connection
        - Safe for concurrent reads and writes

    Example:
        >>> conn = DuckDBConnection(Path("/tmp/graph.duckdb"))
        >>> 
        >>> # Thread 1
        >>> results1 = conn.execute("SELECT * FROM symbols")
        >>> 
        >>> # Thread 2 (separate connection)
        >>> results2 = conn.execute("SELECT * FROM relationships")
    """

    def __init__(self, db_path: Path) -> None:
        """Initialize connection manager.

        Args:
            db_path: Path to DuckDB database file
                - File path: Persistent database
                - ":memory:": In-memory database (fast, ephemeral)

        Note:
            Connection not established until first execute() call.
            This allows construction without side effects.
        """
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.RLock()

    def get_connection(self) -> Any:
        """Get or create thread-local DuckDB connection.

        Returns:
            DuckDB connection object for current thread

        Raises:
            ActionableError: If duckdb not installed or connection fails

        Thread Safety:
            Uses threading.local() so each thread gets own connection.
            Multiple threads can safely call this simultaneously.
        """
        # Check if current thread has a connection
        if not hasattr(self._local, "connection"):
            with self._lock:
                # Double-check after acquiring lock
                if not hasattr(self._local, "connection"):
                    try:
                        import duckdb

                        # Create database directory if file-based
                        if str(self.db_path) != ":memory:":
                            self.db_path.parent.mkdir(parents=True, exist_ok=True)

                        # Connect to database
                        self._local.connection = duckdb.connect(str(self.db_path))
                        
                        # Enable checkpoint on shutdown for clean single-file state
                        self._local.connection.execute("PRAGMA enable_checkpoint_on_shutdown")
                        
                        logger.debug(
                            "✅ DuckDB connection created for thread %s: %s",
                            threading.current_thread().name,
                            self.db_path,
                        )

                    except ImportError as e:
                        raise ActionableError(
                            what_failed="DuckDB import",
                            why_failed="duckdb package not installed",
                            how_to_fix="Install via: pip install 'duckdb>=0.9.0'",
                        ) from e
                    except PermissionError as e:
                        raise ActionableError(
                            what_failed="Create DuckDB database",
                            why_failed=f"Permission denied: {self.db_path}",
                            how_to_fix=f"Ensure {self.db_path.parent} is writable or use :memory: mode",
                        ) from e
                    except Exception as e:
                        raise ActionableError(
                            what_failed="DuckDB connection",
                            why_failed=str(e),
                            how_to_fix=(
                                "Options:\n"
                                "1. Check path is writable\n"
                                "2. Check disk space available\n"
                                "3. Use :memory: mode for testing"
                            ),
                        ) from e

        return self._local.connection

    def execute(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None,
    ) -> List[Tuple[Any, ...]]:
        """Execute SQL query with optional parameter binding.

        Args:
            query: SQL query string (use ? for parameter placeholders)
            params: Optional tuple of parameters to bind

        Returns:
            List of result tuples (rows)

        Raises:
            ActionableError: If query execution fails
                - Syntax errors
                - Table not found
                - Column not found
                - Other SQL errors

        Example:
            >>> # Query with parameters (safe from SQL injection)
            >>> results = conn.execute(
            ...     "SELECT * FROM symbols WHERE name = ?",
            ...     params=("my_function",)
            ... )
            >>> 
            >>> # Query without parameters
            >>> results = conn.execute("SELECT COUNT(*) FROM symbols")
            >>> 
            >>> # Multiple parameters
            >>> results = conn.execute(
            ...     "SELECT * FROM symbols WHERE name = ? AND type = ?",
            ...     params=("my_function", "function")
            ... )

        Thread Safety:
            Safe to call from multiple threads. Each thread uses its own
            connection via _get_connection().
        """
        try:
            conn = self.get_connection()

            # Execute with or without parameters
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)

            # Fetch all results
            results = cursor.fetchall()
            logger.debug("Query executed: %d rows returned", len(results))
            return results  # type: ignore[no-any-return]

        except Exception as e:
            error_str = str(e).lower()

            # Provide specific guidance based on error type
            if "syntax error" in error_str:
                raise ActionableError(
                    what_failed="Execute DuckDB query",
                    why_failed=f"SQL syntax error: {e}",
                    how_to_fix="Check SQL syntax and parameter placeholders (?)",
                ) from e
            elif "table" in error_str and "does not exist" in error_str:
                raise ActionableError(
                    what_failed="Execute DuckDB query",
                    why_failed=f"Table not found: {e}",
                    how_to_fix="Create table first or check table name spelling",
                ) from e
            elif "column" in error_str and "does not exist" in error_str:
                raise ActionableError(
                    what_failed="Execute DuckDB query",
                    why_failed=f"Column not found: {e}",
                    how_to_fix="Check column name spelling or table schema",
                ) from e
            else:
                raise ActionableError(
                    what_failed="Execute DuckDB query",
                    why_failed=str(e),
                    how_to_fix="Check query syntax, table/column names, and data types",
                ) from e

    def close(self) -> None:
        """Close thread-local connection if exists.

        Safe to call multiple times. Only closes connection for current thread.

        Example:
            >>> conn = DuckDBConnection(Path("/tmp/db.duckdb"))
            >>> conn.execute("SELECT 1")
            >>> conn.close()  # Close current thread's connection
        """
        if hasattr(self._local, "connection"):
            try:
                self._local.connection.close()
                logger.debug("DuckDB connection closed for thread %s", threading.current_thread().name)
            except Exception as e:
                logger.warning("Error closing DuckDB connection: %s", e)
            finally:
                delattr(self._local, "connection")

    def __repr__(self) -> str:
        """String representation for debugging."""
        has_conn = hasattr(self._local, "connection")
        status = "connected" if has_conn else "not connected"
        thread = threading.current_thread().name
        return f"DuckDBConnection(path='{self.db_path}', thread='{thread}', status={status})"

    def __del__(self) -> None:
        """Cleanup: Close connection on deletion."""
        try:
            self.close()
        except Exception:
            pass  # Ignore errors during cleanup


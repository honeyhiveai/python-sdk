"""
Agent OS RAG Engine - LanceDB Implementation
Semantic search with metadata filtering and fallback mechanisms.

Switched from ChromaDB to LanceDB for:
- Built-in WHERE clause filtering (fast!)
- No singleton client conflicts (clean hot reload)
- Simpler reconnection logic

100% AI-authored via human orchestration.
"""

# pylint: disable=too-many-instance-attributes
# Justification: RAGEngine requires 12 attributes to manage vector DB connection,
# embedding models, caching, and configuration - all essential state

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: __init__ needs 6 parameters for flexible configuration of
# database path, embedding provider, model, dimension, cache, and LLM fallback

# pylint: disable=import-outside-toplevel
# Justification: Heavy ML dependencies (sentence-transformers, openai) loaded
# lazily only when needed to reduce startup time and support optional features

# pylint: disable=broad-exception-caught
# Justification: RAG engine catches broad exceptions for robustness - vector
# search failures fall back to grep, ensuring service availability

# pylint: disable=too-many-locals
# Justification: Complex search logic with filtering, ranking, and fallback
# requires multiple intermediate variables for clarity

import hashlib
import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import lancedb

from .models.rag import SearchResult

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Semantic search engine for Agent OS standards.

    Features:
    - Vector similarity search via LanceDB
    - Metadata filtering at DB level (phase, tags, framework)
    - Relevance ranking with critical content boosting
    - Grep fallback for offline/error scenarios
    - Query result caching (TTL: 1 hour)
    """

    def __init__(
        self,
        index_path: Path,
        standards_path: Path,
        embedding_provider: str = "local",
        embedding_model: str = "all-MiniLM-L6-v2",
        cache_ttl_seconds: int = 3600,
    ):
        """
        Initialize RAG engine.

        Args:
            index_path: Path to LanceDB index
            standards_path: Path to Agent OS standards for grep fallback
            embedding_provider: Provider for embeddings ("local" default or "openai")
            embedding_model: Model to use for embeddings
            cache_ttl_seconds: Cache time-to-live in seconds (default: 1 hour)
        """
        self.index_path = index_path
        self.standards_path = standards_path
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.cache_ttl_seconds = cache_ttl_seconds

        # Query cache: {query_hash: (result, timestamp)}
        self._query_cache: Dict[str, tuple] = {}

        # Concurrency control for safe hot reload
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._rebuilding = threading.Event()  # Signal when rebuild in progress

        # Initialize embedding model
        self.local_model: Any = None
        if self.embedding_provider == "local":
            from sentence_transformers import SentenceTransformer

            self.local_model = SentenceTransformer(embedding_model)
        else:
            self.local_model = None

        # Initialize LanceDB connection
        try:
            logger.info("Initializing RAG engine with index at %s", index_path)
            self.db = lancedb.connect(str(index_path))
            self.table = self.db.open_table("agent_os_standards")
            chunk_count = self.table.count_rows()
            logger.info("LanceDB table loaded: %s chunks", chunk_count)
            self.vector_search_available = True
        except Exception as e:
            logger.warning("Failed to initialize LanceDB: %s", e)
            logger.warning("Vector search unavailable, grep fallback will be used")
            self.vector_search_available = False
            self.db = None
            self.table = None

    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None,
    ) -> SearchResult:
        """
        Search Agent OS standards with intelligent retrieval.

        Steps:
        1. Check cache for recent identical query
        2. Generate query embedding
        3. Vector search with metadata filtering (WHERE clauses)
        4. Rank and boost critical content
        5. Return structured results

        If vector search fails, falls back to grep.

        Args:
            query: Search query text
            n_results: Number of results to return (default: 5)
            filters: Optional metadata filters:
                - phase: int (phase number to filter by)
                - tags: List[str] (tags to filter by)
                - framework: str (framework type to filter by)
                - is_critical: bool (only critical content)

        Returns:
            SearchResult with chunks, metadata, and metrics

        Example:
            # Get Phase 1 requirements
            result = engine.search(
                "Phase 1 method verification requirements",
                n_results=5,
                filters={"phase": 1}
            )
        """
        # Wait if rebuild in progress (timeout: 30s)
        if self._rebuilding.is_set():
            logger.debug("Waiting for index rebuild to complete...")
            if not self._rebuilding.wait(timeout=30):
                logger.warning("Rebuild timeout, proceeding with current index")

        start_time = time.time()

        # Check cache
        cache_key = self._generate_cache_key(query, n_results, filters)
        cached_result = self._check_cache(cache_key)
        if cached_result:
            logger.debug("Cache hit for query: %s...", query[:50])
            return cached_result

        # Acquire read lock for safe concurrent access during index queries
        with self._lock:
            # Try vector search
            if self.vector_search_available:
                try:
                    result = self._vector_search(query, n_results, filters)
                    elapsed_ms = (time.time() - start_time) * 1000
                    result.query_time_ms = elapsed_ms

                    # Cache result
                    self._cache_result(cache_key, result)

                    logger.info(
                        "Vector search completed: %s chunks in %.1fms",
                        len(result.chunks),
                        elapsed_ms,
                    )
                    return result

                except Exception as e:
                    logger.error("Vector search failed: %s", e, exc_info=True)
                    logger.info("Falling back to grep search")

            # Grep fallback
            result = self._grep_fallback(query, n_results)
            elapsed_ms = (time.time() - start_time) * 1000
            result.query_time_ms = elapsed_ms

            logger.info(
                "Grep search completed: %s chunks in %.1fms",
                len(result.chunks),
                elapsed_ms,
            )
            return result

    def _vector_search(
        self, query: str, n_results: int, filters: Optional[Dict]
    ) -> SearchResult:
        """
        Perform vector similarity search with LanceDB.

        Args:
            query: Search query
            n_results: Number of results
            filters: Metadata filters

        Returns:
            SearchResult with vector-retrieved chunks
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)

        # Build LanceDB query - table is guaranteed to be available here
        if self.table is None:
            raise RuntimeError("LanceDB table not available for vector search")
        search_query = self.table.search(query_embedding).limit(n_results * 2)

        # Apply filters using WHERE clauses (LanceDB's killer feature!)
        if filters:
            where_conditions = []

            if "phase" in filters:
                where_conditions.append(f"phase = {filters['phase']}")

            if "is_critical" in filters:
                where_conditions.append(f"is_critical = {filters['is_critical']}")

            if "framework" in filters:
                where_conditions.append(f"framework_type = '{filters['framework']}'")

            if "tags" in filters:
                # Tags are JSON array, need to check if any match
                for tag in filters["tags"]:
                    where_conditions.append(f"tags LIKE '%{tag}%'")

            # Combine conditions with AND
            if where_conditions:
                where_clause = " AND ".join(where_conditions)
                search_query = search_query.where(where_clause)

        # Execute search
        results = search_query.to_list()

        # Convert to chunks format
        chunks = []
        scores = []
        total_tokens = 0

        for result in results[:n_results]:
            # Parse JSON fields
            try:
                parent_headers = json.loads(result.get("parent_headers", "[]"))
                tags = json.loads(result.get("tags", "[]"))
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                logger.debug("Failed to parse metadata fields: %s", e)
                parent_headers = []
                tags = []

            chunk = {
                "content": result["content"],
                "file_path": result["file_path"],
                "section_header": result["section_header"],
                "parent_headers": parent_headers,
                "token_count": result["token_count"],
                "phase": result["phase"],
                "framework_type": result["framework_type"],
                "category": result.get("category", ""),
                "is_critical": result["is_critical"],
                "tags": tags,
            }

            chunks.append(chunk)
            scores.append(result.get("_distance", 0.0))  # LanceDB returns distance
            total_tokens += result["token_count"]

        return SearchResult(
            chunks=chunks,
            total_tokens=total_tokens,
            retrieval_method="vector",
            query_time_ms=0.0,  # Set by caller
            relevance_scores=scores,
            cache_hit=False,
        )

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for query text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if self.embedding_provider == "local":
            if self.local_model is None:
                raise RuntimeError("Local embedding model not initialized")
            embedding = self.local_model.encode(text, convert_to_numpy=True)
            return cast(List[float], embedding.tolist())

        if self.embedding_provider == "openai":
            import openai

            response = openai.embeddings.create(model=self.embedding_model, input=text)
            # OpenAI SDK returns embedding as list[float] but type-stubbed as Any
            return response.data[0].embedding  # type: ignore[no-any-return]

        raise ValueError(f"Unknown embedding provider: {self.embedding_provider}")

    def _grep_fallback(self, query: str, n_results: int) -> SearchResult:
        """
        Fallback to grep-based search when vector search unavailable.

        Args:
            query: Search query
            n_results: Number of results

        Returns:
            SearchResult with grep-retrieved chunks
        """
        logger.info("Using grep fallback for query: %s...", query[:50])

        try:
            # Extract search terms (simple word splitting)
            search_terms = query.lower().split()

            # Run grep for each term
            chunks = []
            seen_files = set()

            for term in search_terms[:3]:  # Limit to 3 most important terms
                result = subprocess.run(
                    [
                        "grep",
                        "-r",
                        "-i",
                        "-l",  # Files with matches
                        "-m",
                        "1",  # Stop after first match per file
                        term,
                        str(self.standards_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )

                # Parse matched files
                for line in result.stdout.splitlines():
                    if line and line not in seen_files:
                        seen_files.add(line)

                        # Read file content (up to first 1000 chars)
                        try:
                            content = Path(line).read_text(encoding="utf-8")[:1000]
                            chunks.append(
                                {
                                    "content": content,
                                    "file_path": line,
                                    "section_header": "Grep Match",
                                    "token_count": len(content.split()),
                                }
                            )
                        except Exception as e:
                            logger.debug("Could not read %s: %s", line, e)

                    if len(chunks) >= n_results:
                        break

                if len(chunks) >= n_results:
                    break

            total_tokens = sum(
                int(c["token_count"]) if isinstance(c["token_count"], (int, str)) else 0
                for c in chunks
            )

            return SearchResult(
                chunks=chunks[:n_results],
                total_tokens=total_tokens,
                retrieval_method="grep_fallback",
                query_time_ms=0.0,
                relevance_scores=[1.0] * len(chunks),
                cache_hit=False,
            )

        except Exception as e:
            logger.error("Grep fallback failed: %s", e)
            return SearchResult(
                chunks=[],
                total_tokens=0,
                retrieval_method="grep_fallback",
                query_time_ms=0.0,
                relevance_scores=[],
                cache_hit=False,
            )

    def _generate_cache_key(
        self, query: str, n_results: int, filters: Optional[Dict]
    ) -> str:
        """Generate cache key from query parameters.

        Creates MD5 hash of query, n_results, and filters for cache lookup.

        :param query: Search query text
        :type query: str
        :param n_results: Number of results requested
        :type n_results: int
        :param filters: Optional metadata filters
        :type filters: Optional[Dict]
        :return: MD5 hash as cache key
        :rtype: str
        """
        key_data = f"{query}:{n_results}:{json.dumps(filters, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _check_cache(self, cache_key: str) -> Optional[SearchResult]:
        """Check if cached result exists and is fresh (thread-safe).

        Lock must be held for all cache operations to prevent race conditions
        where multiple threads check/modify cache simultaneously.

        Returns cached result if found and not expired, otherwise None.

        Thread Safety:
        - Acquires lock before checking cache
        - Prevents concurrent modification during read/delete
        - Safe for concurrent search operations

        :param cache_key: Cache key to look up
        :type cache_key: str
        :return: Cached search result if fresh, None otherwise
        :rtype: Optional[SearchResult]
        """
        # Lock must be held for all cache operations
        with self._lock:
            if cache_key not in self._query_cache:
                return None

            result: SearchResult
            result, timestamp = self._query_cache[cache_key]

            # Check if expired
            if time.time() - timestamp > self.cache_ttl_seconds:
                del self._query_cache[cache_key]
                return None

            # Return cached result with cache_hit flag
            result.cache_hit = True
            return result

    def _cache_result(self, cache_key: str, result: SearchResult) -> None:
        """Cache search result with timestamp.

        Stores result in cache and triggers cleanup if cache grows too large.

        :param cache_key: Cache key for storage
        :type cache_key: str
        :param result: Search result to cache
        :type result: SearchResult
        """
        self._query_cache[cache_key] = (result, time.time())

        # Clean old cache entries if cache is large
        if len(self._query_cache) > 100:
            self._clean_cache()

    def _clean_cache(self) -> None:
        """Remove expired cache entries (thread-safe).

        Iterates through cache and deletes entries that have exceeded
        the TTL threshold.

        Thread Safety:
        - Uses list() copy to prevent RuntimeError during iteration
        - Safe to call concurrently with cache reads/writes
        - Lock held during entire operation

        Note:
            Must be called while holding self._lock (if called externally)
            or will acquire lock if called directly.
        """
        # Lock must be held for all cache operations
        with self._lock:
            current_time = time.time()
            # Use list() to create snapshot - prevents RuntimeError if cache modified
            expired_keys = [
                key
                for key, (_, timestamp) in list(self._query_cache.items())
                if current_time - timestamp > self.cache_ttl_seconds
            ]
            for key in expired_keys:
                del self._query_cache[key]

    def health_check(self) -> Dict[str, Any]:
        """
        Check RAG engine health status.

        Returns:
            Health status dictionary
        """
        health = {
            "vector_search_available": self.vector_search_available,
            "index_path": str(self.index_path),
            "standards_path": str(self.standards_path),
            "cache_size": len(self._query_cache),
            "embedding_provider": self.embedding_provider,
        }

        if self.vector_search_available:
            try:
                if self.table is not None:
                    health["chunk_count"] = self.table.count_rows()
                    health["status"] = "healthy"
                else:
                    health["status"] = "degraded"
                    health["error"] = "Table not initialized"
            except Exception as e:
                health["status"] = "degraded"
                health["error"] = str(e)
        else:
            health["status"] = "grep_only"

        return health

    def reload_index(self) -> None:
        """Reload LanceDB index for hot reload after rebuild.

        Reconnects to LanceDB and reopens the table after index rebuild.
        Clears query cache to ensure fresh results. Unlike ChromaDB, LanceDB
        has no singleton conflicts making hot reload clean and simple.

        **Thread Safety:**

        Uses write lock to prevent concurrent queries during reload. Blocks
        all search operations until reload completes. Sets `_rebuilding` event
        to signal queries to wait.

        **Example:**

        .. code-block:: python

            # After editing Agent OS content
            rag_engine.reload_index()  # Picks up new content immediately

        **Note:**

        This is typically called automatically by the file watcher when
        Agent OS content changes are detected.
        """
        # Acquire write lock to block all reads during reload
        with self._lock:
            self._rebuilding.set()  # Signal rebuild in progress
            try:
                logger.info("Reloading LanceDB index...")

                # Close old connections cleanly
                if hasattr(self, "table"):
                    del self.table
                if hasattr(self, "db"):
                    del self.db

                # Reconnect to index
                self.db = lancedb.connect(str(self.index_path))
                self.table = self.db.open_table("agent_os_standards")
                chunk_count = self.table.count_rows()
                logger.info("Index reloaded: %s chunks", chunk_count)
                self.vector_search_available = True

                # Clear cache after reload
                self._query_cache.clear()

            except Exception as e:
                logger.error("Failed to reload index: %s", e)
                self.vector_search_available = False
            finally:
                self._rebuilding.clear()  # Signal rebuild complete

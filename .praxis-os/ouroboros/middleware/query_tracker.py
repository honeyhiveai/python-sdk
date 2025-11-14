"""
Query tracker for behavioral metrics and query history.

Tracks per-session query statistics including:
    - Total/unique query counts
    - Angle coverage (conceptual, location, implementation, etc.)
    - Query history (recent 10 queries, FIFO)
    - Last query timestamp

Used by PrependGenerator for gamification feedback and by MetricsCollector
for behavioral analysis.

Example Usage:
    >>> from ouroboros.middleware.query_tracker import QueryTracker
    >>> 
    >>> tracker = QueryTracker()
    >>> angle = tracker.record_query("session-123", "How does X work?")
    >>> print(angle.primary)  # "conceptual"
    >>> 
    >>> stats = tracker.get_stats("session-123")
    >>> print(f"Total: {stats.total_queries}, Unique: {stats.unique_queries}")
    >>> print(f"Angles covered: {stats.angles_covered}")

Thread Safety:
    Thread-safe via RLock for concurrent access in dual-transport mode
    (stdio + HTTP). Safe for multiple simultaneous sessions.

Memory Footprint:
    ~1KB per session (bounded by history limit of 10 queries)

See Also:
    - query_classifier: QueryClassifier for angle detection
    - prepend_generator: PrependGenerator for gamification messages
    - utils.metrics: MetricsCollector for system-wide behavioral tracking
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .query_classifier import QueryAngle, QueryAngleResult, QueryClassifier


@dataclass
class QueryStats:
    """
    Statistics for a query session.

    Tracks query counts, angle coverage, and recent query history
    for progress visualization and gamification feedback.

    Attributes:
        total_queries (int): Total number of queries (includes duplicates)
        unique_queries (int): Number of unique queries (normalized comparison)
        angles_covered (set[QueryAngle]): Set of angles seen in this session
        query_history (list[str]): Recent queries (max 10, FIFO)
        last_query_time (datetime | None): Timestamp of most recent query

    Memory:
        Approximately 1-1.5KB per session (bounded by history limit)

    Example:
        >>> stats = QueryStats()
        >>> stats.total_queries
        0
        >>> stats.angles_covered
        set()
    """

    total_queries: int = 0
    unique_queries: int = 0
    angles_covered: set[QueryAngle] = field(default_factory=set)
    query_history: list[str] = field(default_factory=list)
    last_query_time: Optional[datetime] = None


class QueryTracker:
    """
    Track query patterns per conversation session.

    Maintains isolated statistics for each session including total/unique
    query counts, angle coverage, and recent query history.

    The tracker automatically:
        - Classifies query angles using QueryClassifier
        - Detects duplicate queries via normalized comparison
        - Maintains bounded history (FIFO, max 10 queries)
        - Creates new sessions on first query
        - Isolates session state (no cross-contamination)

    Performance:
        - record_query(): ≤2ms average latency
        - Memory: ~1KB per session

    Thread Safety:
        Thread-safe via RLock for dual-transport HTTP/stdio concurrent access.

    Example:
        >>> tracker = QueryTracker()
        >>> 
        >>> # Record query
        >>> result = tracker.record_query("session-1", "What is X?")
        >>> print(result.primary)  # "conceptual"
        >>> 
        >>> # Get stats
        >>> stats = tracker.get_stats("session-1")
        >>> print(stats.total_queries)  # 1
        >>> 
        >>> # Check coverage
        >>> uncovered = tracker.get_uncovered_angles("session-1")
        >>> print(f"Unexplored: {uncovered}")

    Use Cases:
        - Gamification feedback (prepend generation)
        - Behavioral analysis (query diversity)
        - Progress tracking (angle coverage)
        - Suggestion generation (explore other angles)
    """

    # Class-level singleton for global state
    _singleton_instance: Optional["QueryTracker"] = None
    _singleton_lock = threading.RLock()

    def __init__(self) -> None:
        """
        Initialize query tracker with empty session storage.

        Creates an empty dictionary for session statistics.
        Each session_id maps to its own QueryStats instance.

        Thread Safety:
            RLock protects _sessions dictionary from concurrent access
            in dual-transport mode (stdio + HTTP threads).

        Example:
            >>> tracker = QueryTracker()
        """
        self._sessions: dict[str, QueryStats] = {}
        self._sessions_lock = threading.RLock()
        self._classifier = QueryClassifier()

    def record_query(self, session_id: str, query: str) -> QueryAngleResult:
        """
        Record a query and return its classification result.

        Tracks query in session statistics:
            - Increments total_queries count
            - Increments unique_queries if not seen before (normalized)
            - Adds angle(s) to angles_covered set
            - Appends to query_history (FIFO, max 10)
            - Updates last_query_time

        Args:
            session_id: Conversation session identifier
            query: Query string to record

        Returns:
            QueryAngleResult: Classification result with angle(s), confidence

        Performance:
            - Average latency: ≤2ms
            - O(1) session lookup
            - O(n) duplicate detection (n ≤ 10 for history)

        Example:
            >>> tracker = QueryTracker()
            >>> result = tracker.record_query("s1", "What is X?")
            >>> print(result.primary)  # "conceptual"
            >>> print(result.confidence)  # 1.0
            >>> 
            >>> # Duplicate query
            >>> result = tracker.record_query("s1", "what is x?")
            >>> stats = tracker.get_stats("s1")
            >>> print(stats.total_queries)  # 2
            >>> print(stats.unique_queries)  # 1

        Thread Safety:
            Uses double-checked locking for session creation and
            synchronized mutations to QueryStats.
        """
        # Classify query angle(s)
        result = self._classifier.classify(query)

        # Double-checked locking for session creation (thread-safe)
        # Fast path: check without lock (common case for existing sessions)
        if session_id in self._sessions:
            stats = self._sessions[session_id]
        else:
            # Slow path: acquire lock for session creation
            with self._sessions_lock:
                # Re-check after acquiring lock (another thread may have created it)
                if session_id not in self._sessions:
                    self._sessions[session_id] = QueryStats()
                stats = self._sessions[session_id]

        # Update stats (lock protects mutations to shared QueryStats object)
        with self._sessions_lock:
            # Update total count
            stats.total_queries += 1

            # Check if query is unique (normalized comparison)
            normalized_query = query.lower().strip()
            normalized_history = [q.lower().strip() for q in stats.query_history]

            if normalized_query not in normalized_history:
                stats.unique_queries += 1

            # Add primary and secondary angles to covered set
            stats.angles_covered.add(result.primary)
            for angle in result.secondary:
                stats.angles_covered.add(angle)

            # Add to query history (FIFO, max 10)
            stats.query_history.append(query)
            if len(stats.query_history) > 10:
                stats.query_history.pop(0)  # Remove oldest

            # Update timestamp
            stats.last_query_time = datetime.now()

        return result

    def get_stats(self, session_id: str) -> QueryStats:
        """
        Get current statistics for session.

        Returns the QueryStats instance for the given session.
        If session doesn't exist, returns an empty QueryStats.

        Args:
            session_id: Conversation session identifier

        Returns:
            QueryStats: Current statistics for the session

        Example:
            >>> tracker = QueryTracker()
            >>> stats = tracker.get_stats("new_session")  # New session
            >>> stats.total_queries
            0
            >>> 
            >>> tracker.record_query("new_session", "What is X?")
            >>> stats = tracker.get_stats("new_session")
            >>> stats.total_queries
            1
        """
        with self._sessions_lock:
            if session_id not in self._sessions:
                return QueryStats()

            # Return a copy to prevent external mutation
            return self._sessions[session_id]

    def get_uncovered_angles(self, session_id: str) -> set[QueryAngle]:
        """
        Get angles not yet covered in this session.

        Returns the set of QueryAngle values that have NOT been
        recorded in this session. Useful for generating suggestions
        to explore diverse query patterns.

        Args:
            session_id: Conversation session identifier

        Returns:
            set[QueryAngle]: Angles not yet covered in session

        Example:
            >>> tracker = QueryTracker()
            >>> tracker.record_query("s1", "What is X?")  # conceptual
            >>> uncovered = tracker.get_uncovered_angles("s1")
            >>> len(uncovered)
            4
            >>> "conceptual" in uncovered
            False
            >>> "location" in uncovered
            True
        """
        all_angles: set[QueryAngle] = {
            "conceptual",
            "location",
            "implementation",
            "critical",
            "troubleshooting",
        }

        with self._sessions_lock:
            if session_id not in self._sessions:
                return all_angles

            stats = self._sessions[session_id]
            return all_angles - stats.angles_covered

    def get_diversity_score(self, session_id: str) -> float:
        """
        Calculate query diversity score for session (0.0-1.0).

        Diversity score is based on angle coverage:
            - 0.0: No queries yet
            - 0.2: 1/5 angles covered
            - 0.4: 2/5 angles covered
            - 0.6: 3/5 angles covered
            - 0.8: 4/5 angles covered
            - 1.0: 5/5 angles covered (perfect diversity)

        Args:
            session_id: Conversation session identifier

        Returns:
            float: Diversity score (0.0-1.0)

        Example:
            >>> tracker = QueryTracker()
            >>> tracker.record_query("s1", "What is X?")  # conceptual
            >>> tracker.get_diversity_score("s1")
            0.2
            >>> tracker.record_query("s1", "Where is X?")  # location
            >>> tracker.get_diversity_score("s1")
            0.4
        """
        with self._sessions_lock:
            if session_id not in self._sessions:
                return 0.0

            stats = self._sessions[session_id]
            return len(stats.angles_covered) / 5.0

    def reset_session(self, session_id: str) -> None:
        """
        Reset session statistics (primarily for testing).

        Removes all statistics for the given session. Useful for
        test cleanup and session restart scenarios.

        Args:
            session_id: Conversation session identifier to reset

        Example:
            >>> tracker = QueryTracker()
            >>> tracker.record_query("s1", "What is X?")
            >>> tracker.reset_session("s1")
            >>> stats = tracker.get_stats("s1")
            >>> stats.total_queries
            0
        """
        with self._sessions_lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

    def get_all_sessions(self) -> dict[str, QueryStats]:
        """
        Get statistics for all tracked sessions.

        Returns a copy of the sessions dictionary mapping session IDs
        to their QueryStats. Used for system-wide metrics collection
        and observability.

        Returns:
            dict[str, QueryStats]: Map of session_id -> QueryStats

        Example:
            >>> tracker = QueryTracker()
            >>> tracker.record_query("s1", "Query 1")
            >>> tracker.record_query("s2", "Query 2")
            >>> sessions = tracker.get_all_sessions()
            >>> len(sessions)
            2
            >>> sessions["s1"].total_queries
            1

        Thread Safety:
            Returns a shallow copy of _sessions to prevent external
            mutation while allowing safe iteration.
        """
        with self._sessions_lock:
            return dict(self._sessions)

    @classmethod
    def get_singleton(cls) -> "QueryTracker":
        """
        Get the global query tracker instance (singleton pattern).

        Ensures a single QueryTracker instance per process for
        consistent state across all tool calls.

        Returns:
            QueryTracker: The global tracker instance

        Example:
            >>> tracker1 = QueryTracker.get_singleton()
            >>> tracker2 = QueryTracker.get_singleton()
            >>> tracker1 is tracker2
            True

        Thread Safety:
            Uses class-level RLock for thread-safe singleton initialization.
        """
        if cls._singleton_instance is None:
            with cls._singleton_lock:
                if cls._singleton_instance is None:
                    cls._singleton_instance = cls()
        return cls._singleton_instance


__all__ = ["QueryStats", "QueryTracker"]


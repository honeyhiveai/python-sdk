"""
Behavioral metrics collection and tracking.

Provides metrics tracking for Ouroboros behavioral engineering mission:
    - Query diversity (unique queries per session)
    - Query trends (categories over time)
    - Latency tracking (operation performance)
    - Tool usage patterns
    - Workflow adherence (gate passage rates)

Metrics are mission-critical for Ouroboros, enabling behavioral analysis
and reinforcement learning for AI agents.

Example Usage:
    >>> from ouroboros.utils.metrics import MetricsCollector
    >>> 
    >>> metrics = MetricsCollector()
    >>> 
    >>> # Track query
    >>> metrics.track_query("How does X work?", session_id="abc123")
    >>> 
    >>> # Get query diversity
    >>> diversity = metrics.get_query_diversity("abc123")
    >>> print(f"Diversity: {diversity:.2f}")  # 0.00-1.00
    >>> 
    >>> # Track latency
    >>> with metrics.track_latency("search_standards"):
    ...     # Perform operation
    ...     pass
    >>> 
    >>> # Get metrics summary
    >>> summary = metrics.get_summary()

See Also:
    - logging: StructuredLogger for behavioral event logging
    - config.schemas.logging: LoggingConfig with behavioral_metrics_enabled
"""

import time
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator


class MetricsCollector:
    """
    Behavioral metrics collector for AI agent tracking.

    Tracks behavioral metrics for Ouroboros's mission:
        - Query diversity: Unique queries / total queries
        - Query trends: Query categories over time
        - Latency: Operation performance tracking
        - Tool usage: Tool call frequencies
        - Workflow adherence: Gate passage rates

    Metrics are stored in-memory and can be:
        - Logged via StructuredLogger.behavioral()
        - Exported for analysis
        - Reset per session

    Example:
        >>> metrics = MetricsCollector()
        >>> 
        >>> # Track queries
        >>> metrics.track_query("How does X work?", session_id="abc123")
        >>> metrics.track_query("What is Y?", session_id="abc123")
        >>> metrics.track_query("How does X work?", session_id="abc123")  # duplicate
        >>> 
        >>> # Get diversity (2 unique / 3 total = 0.67)
        >>> diversity = metrics.get_query_diversity("abc123")
        >>> assert 0.6 < diversity < 0.7
        >>> 
        >>> # Track latency
        >>> with metrics.track_latency("search_standards"):
        ...     time.sleep(0.1)  # Simulate work
        >>> 
        >>> # Get latency stats
        >>> stats = metrics.get_latency_stats("search_standards")
        >>> assert stats["count"] == 1
        >>> assert stats["avg_ms"] >= 100

    Attributes:
        queries (dict): Query tracking per session
        latencies (dict): Latency tracking per operation
        tool_usage (dict): Tool call counts
        workflow_gates (dict): Gate passage tracking
    """

    def __init__(self) -> None:
        """
        Initialize metrics collector.

        Creates empty data structures for:
            - Query tracking (session → query list)
            - Latency tracking (operation → latency list)
            - Tool usage (tool → call count)
            - Workflow gates (session → gates passed)

        Example:
            >>> metrics = MetricsCollector()
            >>> assert metrics.queries == {}
            >>> assert metrics.latencies == {}
        """
        # Query tracking: {session_id: [query1, query2, ...]}
        self.queries: dict[str, list[str]] = defaultdict(list)

        # Latency tracking: {operation: [latency_ms1, latency_ms2, ...]}
        self.latencies: dict[str, list[float]] = defaultdict(list)

        # Tool usage: {tool_name: call_count}
        self.tool_usage: dict[str, int] = defaultdict(int)

        # Workflow gates: {session_id: {phase: passed}}
        self.workflow_gates: dict[str, dict[int, bool]] = defaultdict(dict)

    def track_query(self, query: str, session_id: str) -> None:
        """
        Track query for behavioral diversity analysis.

        Records query for session to calculate:
            - Query diversity (unique / total)
            - Query trends over time
            - Behavioral drift detection

        Args:
            query: Query text
            session_id: AI agent session identifier

        Example:
            >>> metrics = MetricsCollector()
            >>> metrics.track_query("How does X work?", session_id="abc123")
            >>> metrics.track_query("What is Y?", session_id="abc123")
            >>> 
            >>> # Check tracking
            >>> assert len(metrics.queries["abc123"]) == 2

        Use Cases:
            - Query diversity calculation
            - Trend analysis (improving vs regressing)
            - Behavioral drift detection (stuck in loops)
        """
        self.queries[session_id].append(query)

    def get_query_diversity(self, session_id: str) -> float:
        """
        Calculate query diversity for session.

        Diversity = unique_queries / total_queries
            - 1.0: All queries unique (perfect)
            - 0.5: Half queries unique (moderate)
            - 0.0: All queries duplicates (poor)

        Args:
            session_id: AI agent session identifier

        Returns:
            float: Query diversity (0.0-1.0)

        Example:
            >>> metrics = MetricsCollector()
            >>> metrics.track_query("Query A", session_id="s1")
            >>> metrics.track_query("Query B", session_id="s1")
            >>> metrics.track_query("Query A", session_id="s1")  # duplicate
            >>> 
            >>> diversity = metrics.get_query_diversity("s1")
            >>> assert diversity == 2/3  # 2 unique, 3 total

        Interpretation:
            - >0.8: Excellent diversity (exploring broadly)
            - 0.5-0.8: Good diversity (normal behavior)
            - 0.3-0.5: Low diversity (repetitive behavior)
            - <0.3: Poor diversity (stuck in loop)

        Use Cases:
            - Behavioral health monitoring
            - Gamification (prepend generation)
            - Learning trend analysis
        """
        session_queries = self.queries.get(session_id, [])
        if not session_queries:
            return 1.0  # No queries yet, perfect diversity

        unique_count = len(set(session_queries))
        total_count = len(session_queries)
        return unique_count / total_count

    def get_query_count(self, session_id: str) -> dict[str, int | float]:
        """
        Get query counts for session.

        Returns:
            dict: Query counts with keys:
                - unique: Number of unique queries
                - total: Total number of queries
                - diversity: Query diversity (0.0-1.0)

        Example:
            >>> metrics = MetricsCollector()
            >>> metrics.track_query("A", session_id="s1")
            >>> metrics.track_query("B", session_id="s1")
            >>> metrics.track_query("A", session_id="s1")
            >>> 
            >>> counts = metrics.get_query_count("s1")
            >>> assert counts["unique"] == 2
            >>> assert counts["total"] == 3
            >>> assert counts["diversity"] == 2/3
        """
        session_queries = self.queries.get(session_id, [])
        unique_count = len(set(session_queries))
        total_count = len(session_queries)
        diversity = unique_count / total_count if total_count > 0 else 1.0

        return {
            "unique": unique_count,
            "total": total_count,
            "diversity": diversity,
        }

    @contextmanager
    def track_latency(self, operation: str) -> Generator[None, None, None]:
        """
        Context manager for latency tracking.

        Measures operation duration and records latency in milliseconds.
        Use as context manager with `with` statement.

        Args:
            operation: Operation name (e.g., "search_standards", "workflow_gate")

        Yields:
            None

        Example:
            >>> metrics = MetricsCollector()
            >>> 
            >>> with metrics.track_latency("search_standards"):
            ...     time.sleep(0.1)  # Simulate 100ms operation
            >>> 
            >>> stats = metrics.get_latency_stats("search_standards")
            >>> assert stats["count"] == 1
            >>> assert stats["avg_ms"] >= 100

        Use Cases:
            - Performance monitoring
            - Latency regression detection
            - Operation profiling
            - SLA tracking
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000  # Convert to milliseconds
            self.latencies[operation].append(latency_ms)

    def get_latency_stats(self, operation: str) -> dict[str, float]:
        """
        Get latency statistics for operation.

        Returns:
            dict: Latency stats with keys:
                - count: Number of measurements
                - avg_ms: Average latency in milliseconds
                - min_ms: Minimum latency
                - max_ms: Maximum latency
                - total_ms: Total latency

        Example:
            >>> metrics = MetricsCollector()
            >>> with metrics.track_latency("op"):
            ...     time.sleep(0.1)
            >>> 
            >>> stats = metrics.get_latency_stats("op")
            >>> assert stats["count"] == 1
            >>> assert stats["avg_ms"] >= 100
            >>> assert stats["min_ms"] >= 100
            >>> assert stats["max_ms"] >= 100

        Use Cases:
            - Performance dashboards
            - Latency trend analysis
            - Operation optimization
            - Bottleneck identification
        """
        operation_latencies = self.latencies.get(operation, [])
        if not operation_latencies:
            return {
                "count": 0,
                "avg_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "total_ms": 0.0,
            }

        return {
            "count": len(operation_latencies),
            "avg_ms": sum(operation_latencies) / len(operation_latencies),
            "min_ms": min(operation_latencies),
            "max_ms": max(operation_latencies),
            "total_ms": sum(operation_latencies),
        }

    def track_tool_usage(self, tool_name: str) -> None:
        """
        Track tool usage frequency.

        Increments call count for tool to analyze:
            - Tool usage patterns
            - Query-first adherence
            - Behavioral drift

        Args:
            tool_name: Tool name (e.g., "pos_search_project", "pos_workflow")

        Example:
            >>> metrics = MetricsCollector()
            >>> metrics.track_tool_usage("pos_search_project")
            >>> metrics.track_tool_usage("pos_search_project")
            >>> metrics.track_tool_usage("pos_workflow")
            >>> 
            >>> assert metrics.tool_usage["pos_search_project"] == 2
            >>> assert metrics.tool_usage["pos_workflow"] == 1

        Use Cases:
            - Tool usage frequency analysis
            - Query-first behavior verification
            - Behavioral pattern detection
        """
        self.tool_usage[tool_name] += 1

    def track_workflow_gate(
        self, session_id: str, phase: int, passed: bool
    ) -> None:
        """
        Track workflow gate passage.

        Records whether AI agent passed workflow gate validation to analyze:
            - Workflow adherence rates
            - Gate failure patterns
            - Evidence quality trends

        Args:
            session_id: AI agent session identifier
            phase: Workflow phase number
            passed: Whether gate validation passed

        Example:
            >>> metrics = MetricsCollector()
            >>> metrics.track_workflow_gate("s1", phase=1, passed=True)
            >>> metrics.track_workflow_gate("s1", phase=2, passed=False)
            >>> 
            >>> gates = metrics.workflow_gates["s1"]
            >>> assert gates[1] is True
            >>> assert gates[2] is False

        Use Cases:
            - Workflow adherence monitoring
            - Gate failure analysis
            - Evidence quality tracking
        """
        self.workflow_gates[session_id][phase] = passed

    def get_workflow_adherence(self, session_id: str) -> dict[str, Any]:
        """
        Get workflow adherence metrics for session.

        Returns:
            dict: Adherence metrics with keys:
                - gates_attempted: Number of gates attempted
                - gates_passed: Number of gates passed
                - adherence_rate: Pass rate (0.0-1.0)
                - failed_phases: List of failed phase numbers

        Example:
            >>> metrics = MetricsCollector()
            >>> metrics.track_workflow_gate("s1", 1, True)
            >>> metrics.track_workflow_gate("s1", 2, True)
            >>> metrics.track_workflow_gate("s1", 3, False)
            >>> 
            >>> adherence = metrics.get_workflow_adherence("s1")
            >>> assert adherence["gates_attempted"] == 3
            >>> assert adherence["gates_passed"] == 2
            >>> assert adherence["adherence_rate"] == 2/3
            >>> assert adherence["failed_phases"] == [3]
        """
        gates = self.workflow_gates.get(session_id, {})
        if not gates:
            return {
                "gates_attempted": 0,
                "gates_passed": 0,
                "adherence_rate": 1.0,
                "failed_phases": [],
            }

        gates_attempted = len(gates)
        gates_passed = sum(1 for passed in gates.values() if passed)
        adherence_rate = gates_passed / gates_attempted
        failed_phases = [phase for phase, passed in gates.items() if not passed]

        return {
            "gates_attempted": gates_attempted,
            "gates_passed": gates_passed,
            "adherence_rate": adherence_rate,
            "failed_phases": failed_phases,
        }

    def get_summary(self) -> dict[str, Any]:
        """
        Get complete metrics summary.

        Returns:
            dict: Complete metrics with keys:
                - timestamp: Current timestamp (ISO 8601)
                - query_metrics: Query diversity and counts
                - latency_metrics: Latency stats per operation
                - tool_usage: Tool call frequencies
                - workflow_metrics: Workflow adherence rates

        Example:
            >>> metrics = MetricsCollector()
            >>> metrics.track_query("A", session_id="s1")
            >>> metrics.track_tool_usage("pos_search_project")
            >>> 
            >>> summary = metrics.get_summary()
            >>> assert "timestamp" in summary
            >>> assert "query_metrics" in summary
            >>> assert "tool_usage" in summary

        Use Cases:
            - Metrics dashboards
            - Behavioral analysis
            - Performance reports
            - Trend visualization
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query_metrics": {
                session_id: self.get_query_count(session_id)
                for session_id in self.queries
            },
            "latency_metrics": {
                operation: self.get_latency_stats(operation)
                for operation in self.latencies
            },
            "tool_usage": dict(self.tool_usage),
            "workflow_metrics": {
                session_id: self.get_workflow_adherence(session_id)
                for session_id in self.workflow_gates
            },
        }

    def reset_session(self, session_id: str) -> None:
        """
        Reset metrics for specific session.

        Clears:
            - Query history
            - Workflow gates

        Preserves:
            - Latency metrics (global)
            - Tool usage (global)

        Args:
            session_id: Session to reset

        Example:
            >>> metrics = MetricsCollector()
            >>> metrics.track_query("A", session_id="s1")
            >>> metrics.track_query("B", session_id="s1")
            >>> 
            >>> metrics.reset_session("s1")
            >>> assert len(metrics.queries.get("s1", [])) == 0

        Use Cases:
            - Session cleanup
            - Fresh start for new workflow
            - Testing reset
        """
        if session_id in self.queries:
            del self.queries[session_id]
        if session_id in self.workflow_gates:
            del self.workflow_gates[session_id]


__all__ = ["MetricsCollector"]


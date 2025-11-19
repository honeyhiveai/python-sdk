"""
Session ID extraction with dynamic countdown timer for task boundaries.

Provides session management for query gamification (PrependGenerator):
- First query: 20s timeout → session_0
- Next query within timeout: (timeout-1)s → same session
- Query after timeout expires: reset to 20s → new session

This creates natural boundaries between user requests while allowing
rapid queries within a single task to stay in the same session.

Architecture:
    - Short-lived sessions for prepend gamification (task boundaries)
    - Distinct from QueryTracker's long-lived agent sessions
    - Uses dynamic countdown timer (20s → 19s → 18s... floor at 5s)

Example Usage:
    >>> from ouroboros.middleware.session_id_extractor import extract_session_id
    >>> 
    >>> # Query 1 at 0:00
    >>> session_1 = extract_session_id(client_id="agent_123")
    >>> # Returns: "agent_123_s0", timeout: 20s
    >>> 
    >>> # Query 2 at 0:15 (within timeout)
    >>> session_2 = extract_session_id(client_id="agent_123")
    >>> # Returns: "agent_123_s0", timeout: 19s
    >>> 
    >>> # Query 3 at 0:45 (after timeout)
    >>> session_3 = extract_session_id(client_id="agent_123")
    >>> # Returns: "agent_123_s1", timeout: 20s (new session)

Thread Safety:
    Thread-safe via RLock for concurrent access in dual-transport mode.

Traceability:
    Spec: specs/completed/2025-10-21-query-gamification-system/specs.md
    Addendum: SESSION-TRACKING-ADDENDUM.md
"""

import logging
import os
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Track session timing state per client.
    
    Attributes:
        client_id: Client identifier (from MCP context or fallback)
        session_number: Sequential session number for this client
        last_query_time: Unix timestamp of last query
        queries_in_session: Count of queries in current session
    """
    client_id: str
    session_number: int
    last_query_time: float
    queries_in_session: int
    
    def get_session_key(self) -> str:
        """Get the session identifier string.
        
        Returns:
            Session ID: "{client_id}_s{session_number}"
        """
        return f"{self.client_id}_s{self.session_number}"
    
    def get_timeout_seconds(self) -> float:
        """Calculate timeout for next query based on queries so far.
        
        Formula: Start at 20s, decrease by 1s per query, floor at 5s
        
        Examples:
            - Query 1: 20s timeout
            - Query 2: 19s timeout
            - Query 3: 18s timeout
            - Query 16+: 5s timeout (floor)
            
        Returns:
            Timeout in seconds for next query
        """
        return max(5.0, 20.0 - self.queries_in_session)
    
    def is_expired(self, current_time: float) -> bool:
        """Check if session timeout has expired.
        
        Args:
            current_time: Current Unix timestamp
            
        Returns:
            True if time since last query exceeds timeout
        """
        timeout = self.get_timeout_seconds()
        time_since_last = current_time - self.last_query_time
        return time_since_last > timeout


# Global state tracking (in-memory, per-process)
_session_states: Dict[str, SessionState] = {}
_session_lock = threading.RLock()


def extract_session_id(client_id: Optional[str] = None) -> str:
    """Extract session ID using dynamic countdown timer.
    
    Strategy:
        1. First query from client → 20s timer, session_0
        2. Next query within timeout → same session, (timeout-1)s timer
        3. Query after timeout expires → new session, reset to 20s timer
    
    Args:
        client_id: Client identifier (from MCP context or fallback to PID)
        
    Returns:
        Session identifier string: "{client_id}_s{session_number}"
        
    Example:
        Query 1 at 0:00 → "client_abc_s0" (20s timeout)
        Query 2 at 0:15 → "client_abc_s0" (19s timeout)
        Query 3 at 0:50 → "client_abc_s1" (timer expired, new session)
        
    Thread Safety:
        Uses RLock for thread-safe session state management.
    """
    # Fallback to PID if no client_id provided
    if not client_id:
        client_id = f"pid_{os.getpid()}"
    
    current_time = time.time()
    
    with _session_lock:
        # Check if client has existing state
        if client_id in _session_states:
            state = _session_states[client_id]
            
            # Check if session expired
            if state.is_expired(current_time):
                # Start new session
                state.session_number += 1
                state.queries_in_session = 0
                logger.debug(
                    "Session expired for %s, starting session_%d",
                    client_id, state.session_number
                )
        else:
            # First query from this client
            state = SessionState(
                client_id=client_id,
                session_number=0,
                last_query_time=current_time,
                queries_in_session=0
            )
            _session_states[client_id] = state
            logger.debug("Created new session state for %s", client_id)
        
        # Update state
        state.last_query_time = current_time
        state.queries_in_session += 1
        
        session_id = state.get_session_key()
        timeout = state.get_timeout_seconds()
        
        logger.debug(
            "Session: %s, queries: %d, next timeout: %.1fs",
            session_id, state.queries_in_session, timeout
        )
        
        return session_id


def cleanup_stale_sessions(max_age_seconds: float = 300) -> int:
    """Clean up sessions idle for longer than max_age_seconds.
    
    Removes session states that haven't been accessed recently to prevent
    memory leaks from abandoned clients.
    
    Args:
        max_age_seconds: Maximum age for idle sessions (default: 5 minutes)
        
    Returns:
        Number of sessions removed
        
    Example:
        >>> # Clean up sessions idle for >5 minutes
        >>> removed = cleanup_stale_sessions(300)
        >>> print(f"Cleaned up {removed} stale sessions")
    """
    current_time = time.time()
    removed_count = 0
    
    with _session_lock:
        stale_clients = []
        
        for client_id, state in _session_states.items():
            age = current_time - state.last_query_time
            if age > max_age_seconds:
                stale_clients.append(client_id)
        
        for client_id in stale_clients:
            del _session_states[client_id]
            removed_count += 1
        
        if removed_count > 0:
            logger.info("Cleaned up %d stale session(s)", removed_count)
    
    return removed_count


def get_session_stats() -> Dict[str, dict]:
    """Get statistics about active sessions (for debugging/monitoring).
    
    Returns:
        Dictionary mapping client_id to session statistics
        
    Example:
        >>> stats = get_session_stats()
        >>> print(f"Active clients: {len(stats)}")
        >>> for client_id, info in stats.items():
        ...     print(f"{client_id}: {info['queries_in_session']} queries")
    """
    current_time = time.time()
    stats = {}
    
    with _session_lock:
        for client_id, state in _session_states.items():
            age = current_time - state.last_query_time
            stats[client_id] = {
                "session_number": state.session_number,
                "queries_in_session": state.queries_in_session,
                "age_seconds": age,
                "next_timeout_seconds": state.get_timeout_seconds(),
                "is_expired": state.is_expired(current_time)
            }
    
    return stats


def reset_all_sessions() -> None:
    """Reset all session states (primarily for testing).
    
    Clears all session tracking state. Use with caution - this will
    reset session numbers and query counts for all clients.
    
    Example:
        >>> # In tests
        >>> reset_all_sessions()
        >>> # All clients start fresh
    """
    with _session_lock:
        _session_states.clear()
    logger.debug("Reset all session states")


__all__ = [
    "extract_session_id",
    "cleanup_stale_sessions",
    "get_session_stats",
    "reset_all_sessions",
]


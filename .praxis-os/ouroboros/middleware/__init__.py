"""
Behavioral engineering middleware for Ouroboros.

Provides middleware components that wrap all tool calls for behavioral tracking:
    - Query Classifier: Angle detection (conceptual, location, implementation, etc.)
    - Query Tracker: Query history and diversity tracking
    - Prepend Generator: Gamification messages for query-first reinforcement

These middleware components are mission-critical for Ouroboros's behavioral
engineering goals, wrapping tool calls to track and reinforce desired behaviors.

Example Usage:
    >>> from ouroboros.middleware.query_classifier import QueryClassifier
    >>> from ouroboros.middleware.query_tracker import QueryTracker
    >>> from ouroboros.middleware.prepend_generator import PrependGenerator
    >>> 
    >>> # Classify query
    >>> classifier = QueryClassifier()
    >>> angles = classifier.classify("How does X work?")
    >>> print(angles.primary)  # "conceptual"
    >>> 
    >>> # Track query
    >>> tracker = QueryTracker()
    >>> tracker.log_query("How does X work?", session_id="abc123")
    >>> 
    >>> # Generate prepend
    >>> generator = PrependGenerator(tracker)
    >>> prepend = generator.generate(query="How?", session_id="abc123")

See Also:
    - query_classifier: Angle detection for search queries
    - query_tracker: Query history and behavioral metrics
    - prepend_generator: Gamification for query-first reinforcement
    
Note: SessionMapper moved to foundation layer (foundation.session_mapper)
"""

__all__ = []


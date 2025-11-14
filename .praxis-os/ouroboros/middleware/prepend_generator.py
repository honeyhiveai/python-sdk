"""
Prepend generator for query gamification messages.

Generates dynamic feedback messages based on query statistics to encourage
diverse exploration and provide progress visualization:
    - Query counts (total/unique)
    - Angle coverage indicators (📖📍🔧⭐⚠️)
    - Suggestions for unexplored angles
    - Completion messages for diverse sessions

Used to reinforce query-first behavior through positive feedback.

Example Usage:
    >>> from ouroboros.middleware.prepend_generator import PrependGenerator
    >>> from ouroboros.middleware.query_tracker import QueryTracker
    >>> 
    >>> tracker = QueryTracker()
    >>> tracker.record_query("s1", "What is X?")
    >>> 
    >>> generator = PrependGenerator(tracker)
    >>> prepend = generator.generate(session_id="s1", current_query="What is X?")
    >>> print(prepend)
    # 📊 Queries: 1/5 | Unique: 1 | Angles: 📖✓ 📍⬜ 🔧⬜ ⭐⬜ ⚠️⬜
    # 💡 Try: 'Where is X implemented?'
    # ---

Token Budget:
    ≤120 tokens maximum, ~85 average per prepend

Performance:
    ≤10ms average latency

See Also:
    - query_tracker: QueryTracker for session statistics
    - query_classifier: QueryClassifier for angle detection
"""

import re
import threading
from typing import Optional

from .query_classifier import QueryAngle, QueryAngleResult, QueryClassifier
from .query_tracker import QueryStats, QueryTracker


class PrependGenerator:
    """
    Generate gamification prepends based on query statistics.

    Creates dynamic feedback messages with:
        - Progress counter (query counts)
        - Angle coverage visualization (emoji indicators)
        - Suggestions for unexplored angles
        - Completion message (≥5 queries + ≥4 angles)

    Token Budget:
        - Early session (1-2 queries): ~60 tokens
        - Mid session (3-4 queries): ~65 tokens
        - Complete session (5+ queries, ≥4 angles): ~70 tokens
        - Maximum: 120 tokens

    Performance:
        - Latency: ≤10ms average
        - Memory: Minimal (stateless except tracker reference)

    Example:
        >>> from ouroboros.middleware.query_tracker import QueryTracker
        >>> 
        >>> tracker = QueryTracker()
        >>> generator = PrependGenerator(tracker)
        >>> 
        >>> # First query
        >>> tracker.record_query("s1", "What is X?")
        >>> prepend = generator.generate("s1", "What is X?")
        >>> assert "Queries: 1/5" in prepend
        >>> assert "📖✓" in prepend
        >>> 
        >>> # Complete session
        >>> for i in range(4):
        ...     tracker.record_query("s1", f"query {i}")
        >>> prepend = generator.generate("s1", "final query")
        >>> assert "Keep exploring" in prepend

    Use Cases:
        - Reinforce query-first behavior
        - Encourage diverse query patterns
        - Visualize progress and coverage
        - Provide actionable next steps
    """

    def __init__(self, tracker: QueryTracker) -> None:
        """
        Initialize prepend generator.

        Args:
            tracker: QueryTracker instance for session statistics

        Example:
            >>> tracker = QueryTracker()
            >>> generator = PrependGenerator(tracker)
        """
        self.tracker = tracker
        self.classifier = QueryClassifier()
        
        # Track suggestion history per session for rotation
        # Format: {session_id: [suggestion1, suggestion2, ...]} (max 5, FIFO)
        self._suggestion_history: dict[str, list[str]] = {}
        self._suggestion_lock = threading.RLock()

    def generate(
        self,
        session_id: str,
        current_query: str,
    ) -> str:
        """
        Generate prepend message for current query.

        Creates a formatted message with:
            - Progress line (query counts, angle indicators)
            - Feedback line (suggestion or completion message)
            - Visual separator

        Args:
            session_id: Conversation session identifier
            current_query: Query that just executed (for topic extraction)

        Returns:
            str: Formatted prepend string (3-4 lines)

        Example:
            >>> tracker = QueryTracker()
            >>> generator = PrependGenerator(tracker)
            >>> tracker.record_query("s1", "What is X?")
            >>> prepend = generator.generate("s1", "What is X?")
            >>> print(prepend)
            # 📊 Queries: 1/5 | Unique: 1 | Angles: 📖✓ 📍⬜ 🔧⬜ ⭐⬜ ⚠️⬜
            # 💡 Try: 'Where is X implemented?'
            # ---

        Message Format:
            Line 1: Progress line with counts and angle indicators
            Line 2: Feedback line (suggestion or completion)
            Line 3: Empty line
            Line 4: Visual separator
            Line 5: Empty line

        Token Budget:
            ~60-120 tokens depending on session state
        """
        # Get current session statistics
        stats = self.tracker.get_stats(session_id)

        # Generate progress line with angle coverage
        angle_indicators = self._generate_angle_indicators(stats.angles_covered)
        progress_line = (
            f"📊 Queries: {stats.total_queries}/5 | "
            f"Unique: {stats.unique_queries} | "
            f"Angles: {angle_indicators}"
        )

        # Generate suggestion or completion message
        if stats.total_queries >= 5 and len(stats.angles_covered) >= 4:
            # Completion message
            feedback_line = "🎉 Keep exploring! Query liberally to deepen your knowledge."
        else:
            # Generate suggestion with rotation (angle-based or pattern-based)
            uncovered_angles = self.tracker.get_uncovered_angles(session_id)
            topic = self._extract_topic(current_query)
            suggestion = self._generate_suggestion_with_rotation(
                session_id, uncovered_angles, topic, current_query
            )
            feedback_line = f"💡 Try: {suggestion}"

        # Separator
        separator = "---"

        # Combine all lines
        prepend = f"{progress_line}\n{feedback_line}\n\n{separator}\n\n"

        return prepend

    def _generate_angle_indicators(self, angles_covered: set[QueryAngle]) -> str:
        """
        Generate angle coverage indicators with emojis.

        Creates visual representation of angle coverage using
        emojis with checkmarks (✓) for covered angles and
        empty boxes (⬜) for uncovered angles.

        Args:
            angles_covered: Set of angles covered in session

        Returns:
            str: Formatted indicator string

        Example:
            >>> generator = PrependGenerator(QueryTracker())
            >>> indicators = generator._generate_angle_indicators({"conceptual", "location"})
            >>> assert "📖✓" in indicators
            >>> assert "📍✓" in indicators
            >>> assert "🔧⬜" in indicators

        Angle Order:
            1. 📖 Conceptual
            2. 📍 Location
            3. 🔧 Implementation
            4. ⭐ Critical
            5. ⚠️ Troubleshooting
        """
        # Deterministic angle order
        angle_order: tuple[QueryAngle, ...] = (
            "conceptual",
            "location",
            "implementation",
            "critical",
            "troubleshooting",
        )

        indicators = []
        for angle in angle_order:
            emoji = self.classifier.get_angle_emoji(angle)
            status = "✓" if angle in angles_covered else "⬜"
            indicators.append(f"{emoji}{status}")

        return " ".join(indicators)

    def _extract_topic(self, query: str) -> str:
        """
        Extract topic from query by removing common words.

        Strips common query words (what, how, where, is, are, etc.)
        to extract the core topic for suggestion generation.

        **Security**: Sanitizes HTML tags to prevent XSS injection.

        Args:
            query: Query string

        Returns:
            str: Extracted topic or "[concept]" if extraction fails

        Example:
            >>> generator = PrependGenerator(QueryTracker())
            >>> generator._extract_topic("What is checkpoint validation?")
            'checkpoint validation'
            >>> generator._extract_topic("How to use workflows?")
            'use workflows'
            >>> generator._extract_topic("Where is the parser?")
            'parser'

        Security:
            HTML tags are stripped to prevent XSS injection in suggestions.
        """
        if not query or not isinstance(query, str):
            return "[concept]"

        # SECURITY: Remove HTML tags to prevent XSS
        sanitized_query = re.sub(r"<[^>]+>", "", query)

        # Common words to remove (query patterns + stop words)
        common_words = {
            # Question words
            "what", "is", "are", "how", "where", "which", "when", "why", "who",
            # Articles and determiners
            "the", "a", "an", "this", "that", "these", "those",
            # Prepositions
            "to", "in", "of", "on", "at", "by", "for", "with", "from", "as",
            # Auxiliary verbs
            "do", "does", "did", "can", "could", "should", "will", "would",
            # Pronouns
            "i", "you", "he", "she", "it", "we", "they",
            # Action verbs (query patterns)
            "work", "works", "working", "implemented", "implementation", "implement",
            "use", "using", "used", "create", "created", "creating",
            "find", "finding", "found", "get", "getting", "got",
            "explain", "explaining", "explained", "describe", "describing",
            "show", "showing", "shown", "tell", "telling", "told",
        }

        # Split, filter, and rejoin
        words = sanitized_query.lower().split()
        
        # Strip punctuation and filter out common words
        filtered_words = []
        for w in words:
            cleaned = w.strip("?.,;:!")
            if cleaned and cleaned not in common_words:
                filtered_words.append(cleaned)

        if not filtered_words:
            return "[concept]"

        # Take first 2-3 words as topic (prefer nouns/concepts, not action verbs)
        # Stop early if we hit an action verb (shouldn't happen after filtering, but safety check)
        topic_words = []
        for word in filtered_words[:3]:
            if word in common_words:  # Double-check (shouldn't happen)
                continue
            topic_words.append(word)
            if len(topic_words) >= 3:
                break
        
        if not topic_words:
            return "[concept]"
        
        topic = " ".join(topic_words)
        return topic if topic else "[concept]"

    def _generate_suggestion_with_rotation(
        self,
        session_id: str,
        uncovered_angles: set[QueryAngle],
        topic: str,
        current_query: str,
    ) -> str:
        """
        Generate suggestion with rotation between angle-based and pattern-based.

        Rotates between:
        1. Angle-based suggestions (explore uncovered angles)
        2. Pattern-based variations (rephrase current query)

        Tracks suggestion history to avoid immediate repetition.

        Args:
            session_id: Session identifier for history tracking
            uncovered_angles: Set of angles not yet covered
            topic: Extracted topic from current query
            current_query: Current query for pattern variations

        Returns:
            str: Rotated suggestion string (quoted)

        Rotation Strategy:
            - Query count % 2 == 0: Angle-based suggestion
            - Query count % 2 == 1: Pattern-based variation
            - Avoids showing same suggestion twice in a row
        """
        stats = self.tracker.get_stats(session_id)
        
        # Get recent suggestions for this session
        recent_suggestions = self._get_recent_suggestions(session_id)
        
        # Rotate between angle-based and pattern-based
        # Use query count to determine rotation (even = angle, odd = pattern)
        use_pattern = stats.total_queries % 2 == 1
        
        if use_pattern:
            # Generate pattern-based variation
            suggestion = self._generate_pattern_variation(current_query, topic, recent_suggestions)
        else:
            # Generate angle-based suggestion
            suggestion = self._generate_angle_suggestion(uncovered_angles, topic, recent_suggestions)
        
        # Track this suggestion
        self._track_suggestion(session_id, suggestion)
        
        return suggestion
    
    def _generate_angle_suggestion(
        self,
        uncovered_angles: set[QueryAngle],
        topic: str,
        recent_suggestions: list[str],
    ) -> str:
        """
        Generate angle-based suggestion, rotating through uncovered angles.

        Args:
            uncovered_angles: Set of angles not yet covered
            topic: Extracted topic from current query
            recent_suggestions: Recently shown suggestions to avoid

        Returns:
            str: Angle-based suggestion string (quoted)
        """
        if not uncovered_angles:
            # All angles covered, suggest general exploration
            return "'Explore more advanced topics'"

        # Deterministic angle priority for consistent suggestions
        angle_priority: tuple[QueryAngle, ...] = (
            "conceptual",
            "location",
            "implementation",
            "critical",
            "troubleshooting",
        )

        # Find uncovered angles in priority order
        available_angles = [angle for angle in angle_priority if angle in uncovered_angles]
        
        if not available_angles:
            return "'Explore more advanced topics'"

        # Rotate through available angles based on how many we've shown
        # Use modulo to cycle through angles
        angle_index = len(recent_suggestions) % len(available_angles)
        selected_angle = available_angles[angle_index]

        # Generate suggestion using angle-specific template
        templates = {
            "conceptual": f"'What is {topic}?'",
            "location": f"'Where is {topic} implemented?'",
            "implementation": f"'How to use {topic}?'",
            "critical": f"'{topic} best practices'",
            "troubleshooting": f"'Common {topic} mistakes to avoid'",
        }

        suggestion_text = templates.get(selected_angle, f"'{topic}'")
        return suggestion_text
    
    def _generate_pattern_variation(
        self,
        current_query: str,
        topic: str,
        recent_suggestions: list[str],
    ) -> str:
        """
        Generate pattern-based variation of current query.

        Creates semantic variations using pattern templates:
        - Question → Statement: "How does X work?" → "Explain X"
        - Question type change: "How does X?" → "What is X?"
        - Statement form: "X overview", "X details", "X explanation"

        Args:
            current_query: Current query string
            topic: Extracted topic from current query
            recent_suggestions: Recently shown suggestions to avoid

        Returns:
            str: Pattern-based variation (quoted)
        """
        query_lower = current_query.lower().strip()
        
        # Pattern templates for variations
        # Each template is a tuple: (pattern_match, variations_list)
        pattern_templates = [
            # "How does X work?" → variations
            (
                lambda q: any(phrase in q for phrase in ["how does", "how do", "how is", "how are"]),
                [
                    f"'What is {topic}?'",
                    f"'Explain {topic}'",
                    f"'{topic} overview'",
                    f"'Describe {topic}'",
                ]
            ),
            # "What is X?" → variations
            (
                lambda q: any(phrase in q for phrase in ["what is", "what are", "what does"]),
                [
                    f"'How does {topic} work?'",
                    f"'Explain {topic}'",
                    f"'{topic} details'",
                    f"'Describe {topic}'",
                ]
            ),
            # "Where is X?" → variations
            (
                lambda q: "where" in q,
                [
                    f"'What is {topic}?'",
                    f"'How is {topic} implemented?'",
                    f"'{topic} location'",
                    f"'Find {topic}'",
                ]
            ),
            # "How to X?" → variations
            (
                lambda q: any(phrase in q for phrase in ["how to", "how do i", "how can i"]),
                [
                    f"'What is {topic}?'",
                    f"'{topic} usage'",
                    f"'{topic} example'",
                    f"'Using {topic}'",
                ]
            ),
            # Default: general variations
            (
                lambda q: True,  # Always matches (fallback)
                [
                    f"'What is {topic}?'",
                    f"'How does {topic} work?'",
                    f"'Explain {topic}'",
                    f"'{topic} overview'",
                    f"'Describe {topic}'",
                ]
            ),
        ]
        
        # Find matching pattern
        matching_pattern = None
        for pattern_check, variations in pattern_templates:
            if pattern_check(query_lower):
                matching_pattern = variations
                break
        
        if not matching_pattern:
            # Fallback
            matching_pattern = [f"'{topic}'"]
        
        # Rotate through variations, avoiding recent suggestions
        # Find first variation not in recent suggestions
        for variation in matching_pattern:
            if variation not in recent_suggestions:
                return variation
        
        # All variations shown recently, return first one anyway (with rotation)
        rotation_index = len(recent_suggestions) % len(matching_pattern)
        return matching_pattern[rotation_index]
    
    def _get_recent_suggestions(self, session_id: str) -> list[str]:
        """
        Get recently shown suggestions for session.

        Args:
            session_id: Session identifier

        Returns:
            list[str]: Recent suggestions (max 5, FIFO)
        """
        with self._suggestion_lock:
            return self._suggestion_history.get(session_id, [])
    
    def _track_suggestion(self, session_id: str, suggestion: str) -> None:
        """
        Track suggestion in session history for rotation.

        Maintains FIFO queue of recent suggestions (max 5) to avoid
        immediate repetition.

        Args:
            session_id: Session identifier
            suggestion: Suggestion string to track
        """
        with self._suggestion_lock:
            if session_id not in self._suggestion_history:
                self._suggestion_history[session_id] = []
            
            history = self._suggestion_history[session_id]
            
            # Add if not already in recent history
            if suggestion not in history:
                history.append(suggestion)
            
            # Maintain max 5 suggestions (FIFO)
            if len(history) > 5:
                history.pop(0)


__all__ = ["PrependGenerator"]


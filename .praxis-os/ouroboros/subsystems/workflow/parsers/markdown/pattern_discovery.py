"""
Pattern discovery for dynamic parsing.

Discovers document patterns before parsing to enable adaptive scoring.
Instead of hardcoding rules, analyzes document structure to determine:
- What level headers are phases?
- What pattern do phase headers follow?
- What are metadata section patterns?

Target: ~150 lines
"""

from collections import Counter
from typing import Dict, List, Optional, Set

from mistletoe import Document
from mistletoe.block_token import Heading

from . import traversal


class DocumentPatterns:
    """Discovered patterns from document analysis."""
    
    def __init__(self):
        self.phase_header_level: Optional[int] = None
        self.phase_pattern: Optional[str] = None  # Regex pattern
        self.metadata_keywords: Set[str] = set()
        self.phase_header_examples: List[str] = []
        self.metadata_header_examples: List[str] = []
    
    def __repr__(self) -> str:
        return (
            f"DocumentPatterns("
            f"phase_level={self.phase_header_level}, "
            f"phase_count={len(self.phase_header_examples)}, "
            f"metadata_count={len(self.metadata_header_examples)}"
            f")"
        )


def discover_patterns(doc: Document) -> DocumentPatterns:
    """
    Discover document patterns by analyzing structure.
    
    Strategy:
    1. Find all headers, analyze their patterns
    2. Identify phase headers by strong positive signals
    3. Identify metadata sections by negative signals
    4. Build adaptive scoring rules from discovered patterns
    
    Args:
        doc: Parsed markdown document
        
    Returns:
        DocumentPatterns with discovered patterns
    """
    patterns = DocumentPatterns()
    
    # Step 1: Collect all headers with context
    all_headers = traversal.find_headers(doc)
    if not all_headers:
        return patterns
    
    # Step 2: Identify strong phase candidates (high confidence)
    phase_candidates = _identify_phase_candidates(all_headers)
    
    if phase_candidates:
        # Discover pattern from actual phase headers
        patterns.phase_header_level = _discover_phase_level(phase_candidates)
        patterns.phase_pattern = _discover_phase_pattern(phase_candidates)
        patterns.phase_header_examples = [
            traversal.get_text_content(h).strip() 
            for h in phase_candidates[:5]  # Keep a few examples
        ]
    
    # Step 3: Identify metadata sections (negative signals)
    metadata_headers = _identify_metadata_sections(all_headers, phase_candidates)
    patterns.metadata_header_examples = [
        traversal.get_text_content(h).lower().strip()
        for h in metadata_headers[:10]
    ]
    
    # Step 4: Extract metadata keywords from examples
    patterns.metadata_keywords = _extract_metadata_keywords(
        patterns.metadata_header_examples
    )
    
    return patterns


def _identify_phase_candidates(headers: List[Heading]) -> List[Heading]:
    """
    Identify strong phase header candidates using strict positive signals.
    
    Strong signals:
    - Level 2 header (##)
    - Matches "Phase N:" pattern exactly
    - Has a descriptive name after colon
    
    Returns:
        List of headers that are very likely phases
    """
    candidates = []
    
    for header in headers:
        text = traversal.get_text_content(header).strip()
        text_lower = text.lower()
        
        # Strong positive signal: Level 2 + "Phase N:" pattern
        if header.level == 2:
            import re
            if re.match(r"^phase\s+\d+\s*:", text_lower):
                # Has descriptive name after colon
                if ":" in text and len(text.split(":", 1)[1].strip()) > 3:
                    candidates.append(header)
    
    return candidates


def _discover_phase_level(phase_candidates: List[Heading]) -> Optional[int]:
    """
    Discover what header level phases use.
    
    Returns most common level, or None if no candidates.
    """
    if not phase_candidates:
        return None
    
    level_counts = Counter(h.level for h in phase_candidates)
    most_common = level_counts.most_common(1)
    if not most_common:
        return None
    return int(most_common[0][0])


def _discover_phase_pattern(phase_candidates: List[Heading]) -> Optional[str]:
    """
    Discover the regex pattern phase headers follow.
    
    Analyzes actual phase headers to build pattern.
    Returns regex pattern or None.
    """
    if not phase_candidates:
        return None
    
    # Analyze patterns in phase headers
    patterns_seen = []
    for header in phase_candidates[:10]:  # Analyze first 10
        text = traversal.get_text_content(header).strip().lower()
        
        # Most common pattern: "Phase N: Name"
        import re
        if re.match(r"^phase\s+\d+\s*:", text):
            patterns_seen.append(r"^phase\s+\d+\s*:")
        elif re.match(r"^phase\s+\d+", text):
            patterns_seen.append(r"^phase\s+\d+")
    
    if patterns_seen:
        # Return most common pattern
        pattern_counts = Counter(patterns_seen)
        return pattern_counts.most_common(1)[0][0]
    
    return None


def _identify_metadata_sections(
    all_headers: List[Heading], 
    phase_candidates: List[Heading]
) -> List[Heading]:
    """
    Identify metadata section headers (negative signals).
    
    Metadata sections:
    - Contain keywords like "Tasks", "Acceptance Criteria", "Dependencies"
    - Are subsections (level 3+) of phases
    - Appear after main phase headers
    
    Args:
        all_headers: All headers in document
        phase_candidates: Headers identified as phases
        
    Returns:
        List of headers that are metadata sections
    """
    metadata = []
    phase_set = set(phase_candidates)
    
    # Keywords that indicate metadata sections
    # Note: "phase" is excluded because it appears in both phase headers and metadata headers
    metadata_keywords = {
        "tasks", "task", "acceptance", "criteria", "validation", "gate",
        "dependencies", "dependency", "execution", "order", "estimated",
        "duration", "risk", "mitigation", "success", "detailed",
        "breakdown"
    }
    
    for header in all_headers:
        if header in phase_set:
            continue  # Skip actual phases
        
        text = traversal.get_text_content(header).lower()
        words = set(text.split())
        
        # Check if contains metadata keywords
        if words & metadata_keywords:
            metadata.append(header)
    
    return metadata


def _extract_metadata_keywords(metadata_examples: List[str]) -> Set[str]:
    """
    Extract common keywords from metadata section examples.
    
    Returns set of keywords that indicate metadata sections.
    """
    keywords = set()
    
    common_words = {
        "tasks", "task", "acceptance", "criteria", "validation", "gate",
        "dependencies", "dependency", "execution", "order", "estimated",
        "duration", "risk", "mitigation", "success", "detailed", "breakdown",
        "time", "estimates", "overall", "level"
        # Note: "phase" is NOT included because it appears in both phase headers
        # and metadata headers. We use pattern matching instead.
    }
    
    for example in metadata_examples:
        words = set(example.lower().split())
        # Add words that appear in metadata but not typically in phase names
        metadata_words = words & common_words
        keywords.update(metadata_words)
    
    return keywords


__all__ = [
    "DocumentPatterns",
    "discover_patterns",
]

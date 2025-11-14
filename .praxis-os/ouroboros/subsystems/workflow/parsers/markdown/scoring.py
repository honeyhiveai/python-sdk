"""
Semantic scoring for markdown structure identification.

Implements defensive parsing with semantic scoring to identify phases and tasks
even when format varies. Uses discovered patterns from document analysis for
adaptive scoring rather than rigid pattern matching.

Target: ~200 lines
"""

import re
from typing import Dict, List, Optional, Tuple

from mistletoe.block_token import Heading

from .pattern_discovery import DocumentPatterns


def score_phase_header(
    header: Heading, 
    patterns: Optional[DocumentPatterns] = None
) -> float:
    """
    Calculate confidence score that a header represents a phase.

    Uses discovered patterns from document analysis for adaptive scoring:
    - Matches discovered phase pattern = high score
    - Matches discovered phase level = bonus
    - Contains discovered metadata keywords = penalty
    - Falls back to heuristics if no patterns available

    Args:
        header: Heading node to score
        patterns: Discovered document patterns (optional, uses heuristics if None)

    Returns:
        Confidence score (0.0-1.0, higher = more likely a phase)

    Examples:
        >>> score_phase_header(heading("## Phase 1: Setup"), patterns)
        0.95
        >>> score_phase_header(heading("### Task 1.1"), patterns)
        0.0
    """
    score = 0.0
    
    # Extract header text
    from .traversal import get_text_content
    text = get_text_content(header).strip()
    text_lower = text.lower()
    
    # Use discovered patterns if available
    if patterns:
        score = _score_with_patterns(header, text, text_lower, patterns)
    else:
        # Fallback to heuristic scoring
        score = _score_with_heuristics(header, text, text_lower)
    
    return min(max(score, 0.0), 1.0)


def _score_with_patterns(
    header: Heading,
    text: str,
    text_lower: str,
    patterns: DocumentPatterns
) -> float:
    """
    Score header using discovered patterns (dynamic approach).
    
    Strategy:
    1. Strong positive: Matches discovered phase pattern + level
    2. Moderate positive: Matches level but not pattern
    3. Strong negative: Contains metadata keywords
    4. Moderate negative: Wrong level
    
    Returns:
        Confidence score
    """
    score = 0.0
    
    # Positive signals from discovered patterns
    if patterns.phase_pattern:
        if re.match(patterns.phase_pattern, text_lower):
            score += 0.6  # Strong match to discovered pattern
        elif "phase" in text_lower and re.search(r"\d+", text):
            score += 0.2  # Weak match (has phase + number)
    
    if patterns.phase_header_level:
        if header.level == patterns.phase_header_level:
            score += 0.3  # Matches discovered level
        elif header.level > patterns.phase_header_level:
            score -= 0.4  # Too deep (subsection)
    
    # Negative signals from discovered metadata keywords
    # Only penalize if header matches metadata patterns, not just because it contains "phase"
    if patterns.metadata_keywords:
        text_words = set(text_lower.split())
        matched_keywords = text_words & patterns.metadata_keywords
        
        # Don't penalize if it's a phase header pattern (would be caught by positive signals)
        # Only penalize if it looks like metadata (contains "tasks", "acceptance", etc.)
        is_metadata_pattern = any(kw in text_lower for kw in ["tasks", "acceptance", "validation", "gate", "dependencies", "execution", "order"])
        
        if matched_keywords and is_metadata_pattern:
            # Strong penalty if matches multiple metadata keywords AND looks like metadata
            score -= len(matched_keywords) * 0.3
            # Extra penalty for common metadata patterns
            if any(kw in text_lower for kw in ["tasks", "acceptance", "validation", "gate"]):
                score -= 0.5
    
    # Additional negative signals (common metadata patterns)
    if re.search(r"phase\s+\d+\s+tasks", text_lower):
        score -= 1.0  # "Phase N Tasks" is definitely not a phase header
    
    if re.search(r"phase\s+\d+\s+(acceptance|validation|gate)", text_lower):
        score -= 1.0  # Metadata sections
    
    if re.search(r"phase\s+\d+\s*[→→-]", text_lower):
        score -= 1.0  # Dependency notation
    
    if "execution order" in text_lower:
        score -= 0.8
    
    # Too short to be a phase header
    if len(text) < 8:
        score -= 0.3
    
    return score


def _score_with_heuristics(header: Heading, text: str, text_lower: str) -> float:
    """
    Score header using static heuristics (fallback when no patterns available).
    
    Returns:
        Confidence score
    """
    score = 0.0
    
    # Level-based scoring
    if header.level == 2:
        score += 0.5
    elif header.level == 1:
        score += 0.3
    elif header.level >= 3:
        score -= 0.5
    
    # Pattern matching
    if re.match(r"^phase\s+\d+\s*:", text_lower):
        score += 0.5
    elif "phase" in text_lower:
        score += 0.2
    
    # Negative signals
    if re.search(r"phase\s+\d+\s+tasks", text_lower):
        score -= 1.0
    
    if re.search(r"phase\s+\d+\s+(acceptance|validation|gate)", text_lower):
        score -= 1.0
    
    if re.search(r"phase\s+\d+\s*[→→-]", text_lower):
        score -= 1.0
    
    if any(kw in text_lower for kw in ["validation gate", "acceptance criteria", 
                                       "execution order", "dependencies"]):
        score -= 0.7
    
    if len(text) < 8:
        score -= 0.3
    
    return score


def classify_header(
    header: Heading, 
    threshold: float = 0.5,
    patterns: Optional[DocumentPatterns] = None
) -> str:
    """
    Classify header as phase, section, or other.

    Args:
        header: Heading node
        threshold: Confidence threshold for phase classification
        patterns: Discovered document patterns (optional)

    Returns:
        Classification string: "phase", "section", or "other"

    Examples:
        >>> classify_header(heading("## Phase 2: Build"), patterns=patterns)
        "phase"
        >>> classify_header(heading("### Validation Gate"), patterns=patterns)
        "section"
    """
    score = score_phase_header(header, patterns)
    
    if score >= threshold:
        return "phase"
    elif score >= 0.2:
        return "section"
    else:
        return "other"


def extract_phase_number_defensively(text: str) -> int:
    """
    Extract phase number using multiple strategies.

    Tries multiple patterns to find phase number:
    1. "Phase N" pattern (most common)
    2. Leading number before colon
    3. First number in text
    4. Falls back to 0

    Args:
        text: Header or content text

    Returns:
        Phase number (0 if not found)

    Examples:
        >>> extract_phase_number_defensively("## Phase 2: Implementation")
        2
        >>> extract_phase_number_defensively("## 3: Build")
        3
        >>> extract_phase_number_defensively("Some text with 5 in it")
        5
    """
    # Strategy 1: "Phase N" pattern
    match = re.search(r"[Pp]hase\s+(\d+)", text)
    if match:
        return int(match.group(1))

    # Strategy 2: Leading number before colon
    match = re.search(r"^##?\s*(\d+)\s*:", text)
    if match:
        return int(match.group(1))

    # Strategy 3: Any number in first part
    match = re.search(r"(\d+)", text)
    if match:
        return int(match.group(1))

    # Strategy 4: Fallback
    return 0


def score_task_indicator(text: str) -> float:
    """
    Calculate confidence that text represents a task.

    Looks for task indicators:
    - "Task N.N" pattern
    - Checkbox list item
    - Numbered format (N.N:)
    - Bold or emphasized text

    Args:
        text: Text to score

    Returns:
        Confidence score (0.0-1.0)

    Examples:
        >>> score_task_indicator("- [ ] **Task 1.1:** Create module")
        0.9
        >>> score_task_indicator("Some random paragraph")
        0.0
    """
    score = 0.0
    text_lower = text.lower()

    # Strong indicators
    if re.search(r"task\s+\d+\.\d+", text_lower):
        score += 0.6
    
    # Numbered format (N.N:)
    if re.search(r"\b\d+\.\d+\s*:", text):
        score += 0.4

    # Checkbox (common in tasks)
    if text.strip().startswith("- [ ]") or text.strip().startswith("- [x]"):
        score += 0.3

    # Bold markers (tasks often start with bold)
    if "**" in text[:50]:  # Check first 50 chars
        score += 0.2

    return min(score, 1.0)


def extract_task_id_defensively(text: str) -> str:
    """
    Extract task ID using multiple strategies.

    Tries multiple patterns:
    1. "Task N.N" format
    2. "N.N:" format
    3. Any N.N in first line

    Args:
        text: Task text

    Returns:
        Task ID string (e.g., "1.1") or empty string

    Examples:
        >>> extract_task_id_defensively("Task 1.2: Do something")
        "1.2"
        >>> extract_task_id_defensively("1.3: Another task")
        "1.3"
    """
    # Strategy 1: "Task N.N" pattern
    match = re.search(r"[Tt]ask\s+(\d+\.\d+)", text)
    if match:
        return match.group(1)

    # Strategy 2: "N.N:" pattern
    match = re.search(r"(\d+\.\d+)\s*:", text)
    if match:
        return match.group(1)

    # Strategy 3: Any N.N pattern in first 100 chars
    match = re.search(r"\b(\d+\.\d+)\b", text[:100])
    if match:
        return match.group(1)

    return ""


def group_headers_by_confidence(
    headers: List[Heading], 
    threshold: float = 0.5,
    patterns: Optional[DocumentPatterns] = None
) -> Dict[str, List[Heading]]:
    """
    Group headers by classification confidence.

    Args:
        headers: List of Heading nodes
        threshold: Phase classification threshold
        patterns: Discovered document patterns (optional)

    Returns:
        Dictionary mapping classification to headers

    Examples:
        >>> groups = group_headers_by_confidence(all_headers, patterns=patterns)
        >>> len(groups["phase"])  # How many phase headers
        3
    """
    groups: Dict[str, List[Heading]] = {
        "phase": [],
        "section": [],
        "other": [],
    }

    for header in headers:
        classification = classify_header(header, threshold, patterns)
        groups[classification].append(header)

    return groups


__all__ = [
    "score_phase_header",
    "classify_header",
    "extract_phase_number_defensively",
    "score_task_indicator",
    "extract_task_id_defensively",
    "group_headers_by_confidence",
]

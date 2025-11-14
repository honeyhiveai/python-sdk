"""
Text processing utilities.

Pure functions for cleaning text, extracting numbers, normalizing whitespace,
and extracting metadata from markdown text.

Target: ~100 lines
"""

import re
from typing import List, Optional


def extract_first_number(text: str) -> Optional[int]:
    """
    Extract first number from text string.

    Args:
        text: Input text that may contain numbers

    Returns:
        First number found as int, or None if no numbers found

    Examples:
        >>> extract_first_number("Phase 2: Implementation")
        2
        >>> extract_first_number("Task 3.1")
        3
        >>> extract_first_number("No numbers here")
        None
    """
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())
    return None


def extract_metadata(text: str, labels: List[str]) -> Optional[str]:
    """
    Extract metadata value from text with given labels.

    Searches for "Label: value" or "**Label:** value" patterns.

    Args:
        text: Text to search in
        labels: List of label strings to search for

    Returns:
        Extracted value string or None if no match

    Examples:
        >>> extract_metadata("**Duration:** 2 hours", ["Duration", "Time"])
        "2 hours"
        >>> extract_metadata("Objective: Build feature", ["Objective"])
        "Build feature"
    """
    for label in labels:
        # Try bold label first: **Label:**
        pattern = rf"\*\*{re.escape(label)}\*\*\s*:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try plain label: Label:
        pattern = rf"{re.escape(label)}\s*:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def clean_text(text: str) -> str:
    """
    Remove extra whitespace and normalize separators.

    Pure function: Same input always produces same output.
    No side effects: Doesn't modify global state or input.

    Args:
        text: Input text to clean

    Returns:
        Cleaned text with normalized whitespace

    Examples:
        >>> clean_text("  hello   world  ")
        "hello world"
        >>> clean_text("line1\\n\\nline2")
        "line1 line2"
    """
    return " ".join(text.split())


def normalize_task_id(text: str) -> Optional[str]:
    """
    Extract and normalize task ID from text.

    Handles formats like:
    - "Task 1.1"
    - "1.1:"
    - "Task 1.1:"

    Args:
        text: Text containing task ID

    Returns:
        Normalized task ID (e.g., "1.1") or None

    Examples:
        >>> normalize_task_id("Task 1.1: Do something")
        "1.1"
        >>> normalize_task_id("2.3: Build feature")
        "2.3"
    """
    # Match patterns like "1.1" or "Task 1.1"
    pattern = r"(?:Task\s+)?(\d+\.\d+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


__all__ = [
    "extract_first_number",
    "extract_metadata",
    "clean_text",
    "normalize_task_id",
]

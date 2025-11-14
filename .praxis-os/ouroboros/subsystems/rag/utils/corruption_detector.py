"""Corruption detection utilities for LanceDB indexes.

Provides pattern matching functions to detect index corruption errors
and trigger auto-repair workflows.

Functions:
    is_corruption_error: Detect if an exception indicates index corruption

Usage:
    >>> try:
    ...     table = db.open_table("my_table")
    ... except Exception as e:
    ...     if is_corruption_error(e):
    ...         # Trigger auto-repair
    ...         rebuild_index()

Traceability:
    - FR-005: Auto-repair triggers on corruption detection
    - FR-010: Health checks use corruption detection
    - NFR-R1: Reliability (0 corruption incidents per month)
"""

import logging
from typing import Union

logger = logging.getLogger(__name__)

# Known corruption error patterns from LanceDB
CORRUPTION_PATTERNS = [
    # Manifest corruption
    "invalid manifest",
    "manifest not found",
    "manifest error",
    "corrupt manifest",
    # Table corruption
    "lance error",
    "corrupted table",
    "invalid table",
    # File corruption
    "corrupted file",
    "invalid file format",
    "unable to read",
    # Fragment corruption
    "invalid fragment",
    "fragment not found",
    # Schema corruption
    "schema mismatch",
    "invalid schema",
    # Data corruption
    "data file corrupted",
    "index corrupted",
]


def is_corruption_error(error: Union[Exception, str]) -> bool:
    """Detect if error indicates LanceDB index corruption.

    Checks error message against known corruption patterns. Used to trigger
    auto-repair workflows when corruption is detected.

    Args:
        error: Exception object or error message string to check

    Returns:
        True if error indicates corruption, False otherwise

    Detection Strategy:
        - Converts error to lowercase string
        - Checks against CORRUPTION_PATTERNS list
        - Pattern matching is case-insensitive
        - Partial matches count (e.g., "contains pattern")

    Example:
        >>> # Exception handling with corruption detection
        >>> try:
        ...     table = db.open_table("my_table")
        ... except Exception as e:
        ...     if is_corruption_error(e):
        ...         logger.warning("Corruption detected, triggering rebuild")
        ...         rebuild_index(force=True)
        ...     else:
        ...         raise
        >>> 
        >>> # Direct string checking
        >>> error_msg = "lance error: Invalid manifest"
        >>> if is_corruption_error(error_msg):
        ...     print("Corruption detected")

    Known Patterns:
        - "invalid manifest": Manifest file corruption
        - "lance error": Generic LanceDB error (often corruption)
        - "corrupted table": Table data corruption
        - "schema mismatch": Schema version mismatch
        - "fragment not found": Missing data fragment
        - See CORRUPTION_PATTERNS for full list

    Notes:
        - False positives are acceptable (triggers unnecessary rebuild)
        - False negatives are dangerous (leaves corrupt index)
        - Therefore, pattern list is intentionally broad
        - Rebuild is safe operation (idempotent)
    """
    # Convert error to string (handle Exception objects)
    if isinstance(error, Exception):
        error_str = str(error).lower()
    else:
        error_str = str(error).lower()

    # Check against all known patterns
    for pattern in CORRUPTION_PATTERNS:
        if pattern in error_str:
            logger.debug("Corruption pattern detected: '%s' in error: %s", pattern, error_str[:100])
            return True

    logger.debug("No corruption pattern detected in error: %s", error_str[:100])
    return False


def add_corruption_pattern(pattern: str) -> None:
    """Add custom corruption pattern to detection list.

    Useful for handling new corruption error types discovered in production.

    Args:
        pattern: Lowercase error pattern to add (e.g., "new lance error")

    Example:
        >>> # Add new pattern discovered in production
        >>> add_corruption_pattern("lance: vector index corrupted")
        >>> 
        >>> # Now detectable
        >>> error = "Error: lance: vector index corrupted"
        >>> assert is_corruption_error(error) is True

    Notes:
        - Pattern is added to global CORRUPTION_PATTERNS list
        - Pattern should be lowercase
        - Pattern persists for process lifetime only
        - For permanent additions, update CORRUPTION_PATTERNS constant
    """
    pattern_lower = pattern.lower()
    if pattern_lower not in CORRUPTION_PATTERNS:
        CORRUPTION_PATTERNS.append(pattern_lower)
        logger.info("Added corruption pattern: %s", pattern_lower)
    else:
        logger.debug("Corruption pattern already exists: %s", pattern_lower)


def get_corruption_patterns() -> list[str]:
    """Get list of all registered corruption patterns.

    Returns:
        List of lowercase corruption pattern strings

    Example:
        >>> patterns = get_corruption_patterns()
        >>> print(f"Monitoring {len(patterns)} corruption patterns")
        >>> for pattern in patterns:
        ...     print(f"  - {pattern}")
    """
    return CORRUPTION_PATTERNS.copy()


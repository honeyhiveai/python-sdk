"""
Dependency resolution utilities.

Functions for parsing, normalizing, and validating task dependencies.
Pure functions with no side effects.

Target: ~100 lines
"""

import re
from typing import List


def parse_dependency_references(dep_text: str) -> List[str]:
    """
    Parse dependency references from text.

    Extracts task IDs in formats like:
    - "1.1, 1.2"
    - "Task 1.1, Task 2.3"
    - "Depends on 1.1 and 1.2"

    Args:
        dep_text: Text containing dependency references

    Returns:
        List of task IDs (e.g., ["1.1", "2.3"])

    Examples:
        >>> parse_dependency_references("Task 1.1, Task 1.2")
        ["1.1", "1.2"]
        >>> parse_dependency_references("Depends on 1.1 and 2.3")
        ["1.1", "2.3"]
        >>> parse_dependency_references("None")
        []
    """
    if not dep_text or dep_text.lower() in ("none", "n/a", "-"):
        return []

    # Extract task IDs using regex: digits.digits pattern
    task_ids = re.findall(r"\b(\d+\.\d+)\b", dep_text)
    
    if task_ids:
        return task_ids
    
    # Fallback: split by comma if no task IDs found
    parts = [p.strip() for p in dep_text.split(",")]
    return [p for p in parts if p]


def normalize_dependency_format(dep_id: str, phase_shift: int = 0) -> str:
    """
    Normalize dependency to phase.task format with optional shift.

    Args:
        dep_id: Dependency ID (e.g., "1.1", "Task 1.1")
        phase_shift: Amount to shift phase number (for Phase 0 detection)

    Returns:
        Normalized dependency ID with shift applied

    Examples:
        >>> normalize_dependency_format("1.1", shift=0)
        "1.1"
        >>> normalize_dependency_format("0.1", shift=1)
        "1.1"
        >>> normalize_dependency_format("Task 2.3", shift=1)
        "3.3"
    """
    # Extract phase.task numbers
    match = re.search(r"(\d+)\.(\d+)", dep_id)
    if match:
        phase_num = int(match.group(1))
        task_num = int(match.group(2))
        
        # Apply shift
        shifted_phase = phase_num + phase_shift
        
        return f"{shifted_phase}.{task_num}"
    
    return dep_id


def validate_dependency_reference(dep_id: str, available_tasks: List[str]) -> bool:
    """
    Check if dependency reference is valid.

    Args:
        dep_id: Dependency ID to validate
        available_tasks: List of valid task IDs

    Returns:
        True if dependency exists, False otherwise

    Examples:
        >>> validate_dependency_reference("1.1", ["1.1", "1.2", "2.1"])
        True
        >>> validate_dependency_reference("3.1", ["1.1", "1.2"])
        False
    """
    return dep_id in available_tasks


def detect_circular_dependencies(
    task_id: str, dependencies: List[str], dep_map: dict
) -> List[str]:
    """
    Detect circular dependency chains.

    Args:
        task_id: Task to check
        dependencies: Direct dependencies of task
        dep_map: Mapping of task_id -> dependencies for all tasks

    Returns:
        List representing circular chain, or empty list if none

    Examples:
        >>> dep_map = {"1.1": ["1.2"], "1.2": ["1.3"], "1.3": ["1.1"]}
        >>> detect_circular_dependencies("1.1", ["1.2"], dep_map)
        ["1.1", "1.2", "1.3", "1.1"]
    """
    visited = set()
    path: List[str] = []

    def dfs(current: str) -> List[str]:
        if current in visited:
            # Found cycle - build the cycle path
            cycle_start = path.index(current)
            return path[cycle_start:] + [current]
        
        visited.add(current)
        path.append(current)
        
        for dep in dep_map.get(current, []):
            cycle = dfs(dep)
            if cycle:
                return cycle
        
        path.pop()
        return []

    return dfs(task_id)


__all__ = [
    "parse_dependency_references",
    "normalize_dependency_format",
    "validate_dependency_reference",
    "detect_circular_dependencies",
]

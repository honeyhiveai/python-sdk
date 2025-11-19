"""
Validation utilities.

Functions for validating phase sequences, detecting gaps, and checking
structural integrity of parsed workflow data.

Target: ~100 lines
"""

from typing import List, Optional, Tuple


def validate_phase_sequence(phase_numbers: List[int]) -> Tuple[bool, Optional[str]]:
    """
    Validate that phases are sequential with no gaps or duplicates.

    Args:
        phase_numbers: List of phase numbers

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_phase_sequence([0, 1, 2, 3])
        (True, None)
        >>> validate_phase_sequence([1, 2, 3, 4])
        (True, None)
        >>> validate_phase_sequence([1, 3, 4])
        (False, "Phase sequence has gaps: missing phase 2")
        >>> validate_phase_sequence([0, 0, 1, 2])
        (False, "Phase sequence has duplicates: [0]")
    """
    if not phase_numbers:
        return False, "No phases provided"

    # Check for duplicates
    if len(phase_numbers) != len(set(phase_numbers)):
        from collections import Counter
        counts = Counter(phase_numbers)
        duplicates = [num for num, count in counts.items() if count > 1]
        return (
            False,
            f"Phase sequence has duplicates: {sorted(duplicates)}",
        )

    sorted_phases = sorted(phase_numbers)
    min_phase = sorted_phases[0]
    max_phase = sorted_phases[-1]

    # Check that phases start at 0 or 1
    if min_phase not in (0, 1):
        return (
            False,
            f"Phases must start at 0 or 1, found {min_phase}",
        )

    # Check for gaps
    expected = list(range(min_phase, max_phase + 1))
    if sorted_phases != expected:
        missing = set(expected) - set(sorted_phases)
        return (
            False,
            f"Phase sequence has gaps: missing phases {sorted(missing)}",
        )

    return True, None


def detect_phase_shift_requirement(phase_numbers: List[int]) -> int:
    """
    Detect if Phase 0 exists and return shift amount.

    For spec_execution_v1 workflow harness:
    - If Phase 0 exists: return +1 (Phase 0 becomes workflow Phase 1)
    - If starts at Phase 1: return 0 (no shift)

    Args:
        phase_numbers: List of phase numbers

    Returns:
        Shift amount (0 or 1)

    Examples:
        >>> detect_phase_shift_requirement([0, 1, 2])
        1
        >>> detect_phase_shift_requirement([1, 2, 3])
        0
    """
    if not phase_numbers:
        return 0

    min_phase = min(phase_numbers)
    return 1 if min_phase == 0 else 0


def validate_task_count(phase_name: str, task_count: int, min_tasks: int = 1) -> Tuple[bool, Optional[str]]:
    """
    Validate that phase has sufficient tasks.

    Args:
        phase_name: Name of phase being validated
        task_count: Number of tasks in phase
        min_tasks: Minimum required tasks (default: 1)

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_task_count("Phase 1", 3)
        (True, None)
        >>> validate_task_count("Phase 2", 0)
        (False, "Phase 2 has no tasks")
    """
    if task_count < min_tasks:
        return (
            False,
            f"{phase_name} has insufficient tasks (found {task_count}, need {min_tasks})",
        )
    return True, None


def validate_task_ids_sequential(task_ids: List[str], phase_number: int) -> Tuple[bool, Optional[str]]:
    """
    Validate that task IDs are sequential within phase.

    Args:
        task_ids: List of task IDs (e.g., ["1.1", "1.2", "1.3"])
        phase_number: Expected phase number

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_task_ids_sequential(["1.1", "1.2", "1.3"], 1)
        (True, None)
        >>> validate_task_ids_sequential(["1.1", "1.3"], 1)
        (False, "Task IDs in phase 1 are not sequential")
    """
    if not task_ids:
        return True, None

    # Extract task numbers
    task_numbers = []
    for task_id in task_ids:
        parts = task_id.split(".")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            phase = int(parts[0])
            task_num = int(parts[1])
            
            if phase != phase_number:
                return (
                    False,
                    f"Task {task_id} has wrong phase number (expected {phase_number})",
                )
            
            task_numbers.append(task_num)

    # Check sequential (allowing any starting number)
    if task_numbers:
        sorted_nums = sorted(task_numbers)
        expected = list(range(sorted_nums[0], sorted_nums[-1] + 1))
        if sorted_nums != expected:
            return (
                False,
                f"Task IDs in phase {phase_number} are not sequential",
            )

    return True, None


__all__ = [
    "validate_phase_sequence",
    "detect_phase_shift_requirement",
    "validate_task_count",
    "validate_task_ids_sequential",
]

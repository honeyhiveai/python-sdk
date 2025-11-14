"""
Markdown content extraction utilities.

Functions for extracting metadata, task information, acceptance criteria,
and validation gates from markdown structures.

Target: ~150 lines
"""

import re
from typing import Dict, List, Optional


def extract_acceptance_criteria(text: str) -> List[str]:
    """
    Extract acceptance criteria from task text.

    Looks for "Acceptance Criteria:" section and extracts checklist items.

    Args:
        text: Task text containing acceptance criteria

    Returns:
        List of acceptance criteria strings

    Examples:
        >>> text = "**Acceptance Criteria:**\\n- [ ] Must compile\\n- [ ] Tests pass"
        >>> extract_acceptance_criteria(text)
        ["Must compile", "Tests pass"]
    """
    criteria = []

    # Look for "Acceptance Criteria:" section
    pattern = r"(?:Acceptance Criteria|Success Criteria|Validation|Requirements?):\s*\n((?:\s*-\s*\[[ x]\].+\n?)+)"
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

    if match:
        criteria_text = match.group(1)
        # Extract checkbox items
        for line in criteria_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("- [ ]") or stripped.startswith("- [x]"):
                item = stripped[5:].strip()
                if item:
                    criteria.append(item)

    return criteria


def extract_phase_info(header_text: str, content_text: str) -> Optional[Dict[str, str]]:
    """
    Extract phase information from header and content.

    Parses phase number, name, objective, and estimated duration.

    Args:
        header_text: Header text (e.g., "## Phase 2: Implementation")
        content_text: Content following header

    Returns:
        Dictionary with phase info or None if invalid

    Examples:
        >>> info = extract_phase_info("## Phase 2: Implementation", "**Objective:** Build feature")
        >>> info["phase_number"]
        "2"
        >>> info["phase_name"]
        "Implementation"
    """
    # Extract phase number from header
    phase_match = re.search(r"Phase\s+(\d+)", header_text, re.IGNORECASE)
    if not phase_match:
        return None

    phase_number = phase_match.group(1)

    # Extract phase name (text after "Phase N:")
    name_match = re.search(r"Phase\s+\d+\s*[:\-]\s*(.+?)(?:\n|$)", header_text, re.IGNORECASE)
    phase_name = name_match.group(1).strip() if name_match else f"Phase {phase_number}"

    # Extract objective
    objective_match = re.search(
        r"\*\*Objective\*\*\s*:\s*(.+?)(?:\n\n|\n\*\*|$)",
        content_text,
        re.IGNORECASE | re.DOTALL
    )
    objective = objective_match.group(1).strip() if objective_match else ""

    # Extract estimated duration
    duration_match = re.search(
        r"\*\*(?:Estimated\s+)?Duration\*\*\s*:\s*(.+?)(?:\n|$)",
        content_text,
        re.IGNORECASE
    )
    estimated_duration = duration_match.group(1).strip() if duration_match else "Variable"

    return {
        "phase_number": phase_number,
        "phase_name": phase_name,
        "objective": objective,
        "estimated_duration": estimated_duration,
    }


def extract_task_info(text: str) -> Optional[Dict[str, str]]:
    """
    Extract task information from task text.

    Parses task ID, name, description, and estimated time.

    Args:
        text: Task text

    Returns:
        Dictionary with task info or None if invalid

    Examples:
        >>> info = extract_task_info("Task 1.1: Create module\\n**Estimated:** 2h")
        >>> info["task_id"]
        "1.1"
        >>> info["task_name"]
        "Create module"
    """
    # Extract task ID (e.g., "1.1", "2.3")
    task_id_match = re.search(r"(?:Task\s+)?(\d+\.\d+)", text, re.IGNORECASE)
    if not task_id_match:
        return None

    task_id = task_id_match.group(1)

    # Extract task name (text after "Task 1.1:")
    name_match = re.search(
        r"(?:Task\s+)?\d+\.\d+\s*[:\-]\s*(.+?)(?:\n|$)",
        text,
        re.IGNORECASE
    )
    task_name = name_match.group(1).strip() if name_match else f"Task {task_id}"

    # Extract description (first paragraph after task header)
    desc_match = re.search(
        r"(?:Task\s+\d+\.\d+.+?\n)(.+?)(?:\n\n|\*\*|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    description = desc_match.group(1).strip() if desc_match else ""

    # Extract estimated time
    time_match = re.search(
        r"\*\*(?:Estimated\s+)?(?:Time|Duration)\*\*\s*:\s*(.+?)(?:\n|$)",
        text,
        re.IGNORECASE
    )
    estimated_time = time_match.group(1).strip() if time_match else "Variable"

    return {
        "task_id": task_id,
        "task_name": task_name,
        "description": description,
        "estimated_time": estimated_time,
    }


def extract_validation_gate(content: str) -> List[str]:
    """
    Extract validation gate criteria from content.

    Looks for "Validation Gate:" section and extracts checklist items.

    Args:
        content: Content containing validation gate

    Returns:
        List of validation criteria strings

    Examples:
        >>> content = "## Validation Gate\\n- [ ] All tests pass\\n- [ ] Code reviewed"
        >>> extract_validation_gate(content)
        ["All tests pass", "Code reviewed"]
    """
    criteria = []

    # Look for validation gate section
    pattern = r"##?\s*Validation\s+Gate.+?\n((?:\s*-\s*\[[ x]\].+\n?)+)"
    match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)

    if match:
        criteria_text = match.group(1)
        # Extract checkbox items
        for line in criteria_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("- [ ]") or stripped.startswith("- [x]"):
                item = stripped[5:].strip()
                if item:
                    criteria.append(item)

    return criteria


__all__ = [
    "extract_acceptance_criteria",
    "extract_phase_info",
    "extract_task_info",
    "extract_validation_gate",
]

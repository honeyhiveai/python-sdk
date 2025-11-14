"""
Workflow task management guidance injection.

Adds explicit guidance fields to workflow responses to prevent AI assistants
from using external task management tools (like todo_write) when a workflow
is active, which would create duplicate/conflicting task tracking.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Guidance fields injected into all workflow tool responses
WORKFLOW_GUIDANCE_FIELDS = {
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": (
        "This workflow manages ALL tasks. DO NOT use todo_write or "
        "external task lists. The workflow IS your task tracker."
    ),
    "execution_model": "Complete task → Submit evidence → Advance phase",
}


def add_workflow_guidance(
    response: Dict[str, Any], breadcrumb: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Inject task management guidance and optional breadcrumb navigation into workflow response.

    This function adds explicit guidance fields to inform AI assistants that the workflow
    system manages task state and external task tools (like todo_write) should not be used.
    It also supports optional breadcrumb navigation to guide AI agents to the next action.

    **Merging Order (Python 3.7+ dict insertion order):**
    1. Static guidance fields (WORKFLOW_GUIDANCE_FIELDS) - prepended for visibility
    2. Response content - middle section with workflow data
    3. Breadcrumb fields (if provided) - appended at end for recency bias

    **Recency Bias Positioning Strategy:**
    Breadcrumb fields are positioned LAST in the response dictionary to exploit AI models'
    recency bias (attention to recent tokens). This makes the suggested next action the
    most salient information, increasing probability of correct sequential execution.

    Args:
        response: Base response dict from workflow engine
        breadcrumb: Optional action-specific navigation guidance.
            Structure: {"⚡_NEXT_ACTION": "get_task(phase=1, task_number=2)", ...}
            Common fields:
                - ⚡_NEXT_ACTION: Literal call syntax for next workflow action
                - 🎯_CURRENT_POSITION: Position indicator (e.g., "Task 2/5")
                - 📊_PHASE_INFO: Phase-level context (e.g., "Phase 1 has 3 tasks")
                - ✅_PHASE_COMPLETE: Completion status
                - 🎉_WORKFLOW_COMPLETE: Final workflow completion message

    Returns:
        Response dict with injected guidance + breadcrumb fields.
        Field order: guidance → response → breadcrumb (if provided)

    Example:
        >>> # Basic usage (backward compatible)
        >>> base = {"session_id": "123", "phase": 1}
        >>> wrapped = add_workflow_guidance(base)
        >>> "⚠️_WORKFLOW_EXECUTION_MODE" in wrapped
        True

        >>> # With breadcrumb navigation
        >>> breadcrumb = {"⚡_NEXT_ACTION": "get_task(phase=1, task_number=1)"}
        >>> wrapped = add_workflow_guidance(base, breadcrumb=breadcrumb)
        >>> list(wrapped.keys())[-1]  # Breadcrumb positioned last
        '⚡_NEXT_ACTION'

    Note:
        - Gracefully handles non-dict inputs (returns unchanged)
        - Never raises exceptions (fail-safe design)
        - Original response fields preserved (non-invasive)
        - Backward compatible: breadcrumb=None behaves identically to old version
    """
    # Input validation: only process dict responses
    if not isinstance(response, dict):
        logger.debug(
            "Skipping guidance injection for non-dict response: %s",
            type(response).__name__,
        )
        return response

    try:
        # Merge in order: static guidance → response → breadcrumb (if provided)
        # Python 3.7+ guarantees dict insertion order, so breadcrumb appears last
        guided = {**WORKFLOW_GUIDANCE_FIELDS, **response}
        
        # Append breadcrumb at end for recency bias positioning
        if breadcrumb:
            guided.update(breadcrumb)
        
        return guided
    except Exception as e:
        # Fail-safe: return original response if injection fails
        logger.warning(
            "Failed to inject workflow guidance: %s. Returning original response.", e
        )
        return response


__all__ = [
    "WORKFLOW_GUIDANCE_FIELDS",
    "add_workflow_guidance",
]


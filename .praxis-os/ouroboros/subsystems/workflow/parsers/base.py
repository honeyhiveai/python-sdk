"""
Base classes for parsers.

Provides abstract interface and error handling for all parser implementations.

Extracted from task_parser.py to enable modular parser architecture.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ouroboros.subsystems.workflow.models import DynamicPhase
from ouroboros.utils.errors import ActionableError


class ParseError(ActionableError):
    """Raised when source parsing fails."""

    def __init__(self, message: str):
        """Create parse error with default guidance."""
        super().__init__(
            what_failed="Source parsing",
            why_failed=message,
            how_to_fix="Check source file format and structure. See documentation for expected format.",
        )


class SourceParser(ABC):
    """
    Abstract parser for dynamic workflow sources.

    Subclasses implement parsing for specific source formats
    (e.g., tasks.md files, YAML workflow definitions, etc.).
    """

    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse source into structured phase/task data.

        Args:
            source_path: Path to source file or directory

        Returns:
            List of DynamicPhase objects with populated tasks

        Raises:
            ParseError: If source is invalid or cannot be parsed
        """


__all__ = [
    "ParseError",
    "SourceParser",
]

"""
Parser submodule for workflow sources.

Provides abstract interfaces and concrete implementations for parsing
external sources (tasks.md, YAML definitions) into structured workflow data.

This is a modular refactor of the monolithic task_parser.py to improve
extensibility, maintainability, and prevent technical debt accumulation.
"""

from .base import ParseError, SourceParser
from .markdown import SpecTasksParser
from .yaml import WorkflowDefinitionParser

__all__ = [
    "ParseError",
    "SourceParser",
    "SpecTasksParser",
    "WorkflowDefinitionParser",
]


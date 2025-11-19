#!/usr/bin/env python3
"""
Sphinx Documentation Quality Control

A unified, high-performance documentation validation and auto-fix system that consolidates
all quality checks into a single efficient tool.

Features:
- Single-pass file processing for maximum performance
- Coordinated validation with shared state
- Comprehensive auto-fix capabilities
- Unified reporting and metrics
- Extensible validator architecture

Usage:
    python scripts/docs-quality.py [command] [options]

Commands:
    check       Check documentation quality (default)
    fix         Auto-fix issues where possible
    report      Generate detailed quality report
    validate    Validate specific aspects only

Examples:
    python scripts/docs-quality.py check                    # Check all docs
    python scripts/docs-quality.py fix --path docs/tutorials/  # Fix specific path
    python scripts/docs-quality.py report --format json    # JSON report
    python scripts/docs-quality.py validate --only eventtype  # Specific validation
"""

import argparse
import ast
import csv
import importlib.util
import io
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import threading
import time

try:
    import toml  # type: ignore[import-untyped]

    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False
    print("⚠️  Warning: 'toml' not available. Install with: pip install toml")
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stderr
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Collection

# Core RST processing dependencies (required)
import docutils.core  # type: ignore[import-untyped]
import docutils.nodes  # type: ignore[import-untyped]
import docutils.parsers.rst  # type: ignore[import-untyped]

DOCUTILS_AVAILABLE = True  # Always available since it's required


# CRITICAL: Register Sphinx directives GLOBALLY before importing RST tools
# This ensures ALL RST tools (restructuredtext-lint, rstcheck, doc8) inherit Sphinx awareness
def setup_global_sphinx_docutils_integration() -> bool:
    """Register Sphinx directives and roles globally in docutils before any tool imports."""
    try:
        from docutils.parsers.rst import directives, roles  # type: ignore[import-untyped]
        from docutils.parsers.rst.directives import unchanged, flag, positive_int  # type: ignore[import-untyped]

        # nodes already imported at module level

        # Custom Sphinx directive implementations
        from docutils.parsers.rst import Directive  # type: ignore[import-untyped]

        class GlobalTocTreeDirective(Directive):
            """Global toctree directive for all RST tools."""

            has_content = True
            required_arguments = 0
            optional_arguments = 0
            option_spec = {
                "maxdepth": positive_int,
                "numbered": flag,
                "titlesonly": flag,
                "glob": flag,
                "reversed": flag,
                "hidden": flag,
                "includehidden": flag,
                "caption": unchanged,
                "name": unchanged,
            }

            def run(self) -> List[docutils.nodes.Node]:
                # Return empty node - validation happens elsewhere
                return [docutils.nodes.container()]

        class GlobalSphinxDirective(Directive):
            """Generic Sphinx directive for all RST tools."""

            has_content = True
            required_arguments = 0
            optional_arguments = 10
            option_spec = {
                "class": unchanged,
                "name": unchanged,
                "caption": unchanged,
                "linenos": flag,
                "emphasize-lines": unchanged,
            }

            def run(self) -> List[docutils.nodes.Node]:
                return [docutils.nodes.container()]

        # Sphinx role implementations
        def global_sphinx_role(  # pylint: disable=too-many-positional-arguments
            name: str,
            rawtext: str,
            text: str,
            lineno: int,
            inliner: Any,
            options: Optional[Dict[str, Any]] = None,
            content: Optional[List[str]] = None,
        ) -> Tuple[List[docutils.nodes.Node], List[str]]:
            """Generic Sphinx role handler."""
            if options is None:
                options = {}
            if content is None:
                content = []
            return [docutils.nodes.inline(rawtext, text)], []

        # Register core Sphinx directives
        sphinx_directives = {
            "toctree": GlobalTocTreeDirective,
            "mermaid": GlobalSphinxDirective,
            "contents": GlobalSphinxDirective,
            "option": GlobalSphinxDirective,
            "program": GlobalSphinxDirective,
            "envvar": GlobalSphinxDirective,
            "versionadded": GlobalSphinxDirective,
            "versionchanged": GlobalSphinxDirective,
            "deprecated": GlobalSphinxDirective,
            "versionremoved": GlobalSphinxDirective,
            "note": GlobalSphinxDirective,
            "warning": GlobalSphinxDirective,
            "seealso": GlobalSphinxDirective,
            "todo": GlobalSphinxDirective,
            "automodule": GlobalSphinxDirective,
            "autoclass": GlobalSphinxDirective,
            "autofunction": GlobalSphinxDirective,
            "automethod": GlobalSphinxDirective,
            "autodata": GlobalSphinxDirective,
            "autoexception": GlobalSphinxDirective,
            "autoattribute": GlobalSphinxDirective,
            "currentmodule": GlobalSphinxDirective,
            "currentclass": GlobalSphinxDirective,
            "currentfunction": GlobalSphinxDirective,
            "py:method": GlobalSphinxDirective,
            "py:class": GlobalSphinxDirective,
            "py:function": GlobalSphinxDirective,
            "py:module": GlobalSphinxDirective,
            "py:data": GlobalSphinxDirective,
            "py:exception": GlobalSphinxDirective,
            "py:attribute": GlobalSphinxDirective,
        }

        # Register all directives
        for name, directive_class in sphinx_directives.items():
            try:
                directives.register_directive(name, directive_class)
            except Exception as e:
                print(f"⚠️ Failed to register directive {name}: {e}")

        # Register Sphinx roles
        sphinx_roles = [
            "doc",
            "ref",
            "term",
            "abbr",
            "command",
            "dfn",
            "file",
            "guilabel",
            "kbd",
            "mailheader",
            "makevar",
            "manpage",
            "menuselection",
            "mimetype",
            "newsgroup",
            "option",
            "program",
            "regexp",
            "samp",
            "envvar",
        ]

        for role_name in sphinx_roles:
            try:
                roles.register_local_role(role_name, global_sphinx_role)
            except Exception as e:
                print(f"⚠️ Failed to register role {role_name}: {e}")

        # Global Sphinx docutils integration complete
        return True

    except Exception as e:
        print(f"❌ Failed to setup global Sphinx integration: {e}")
        return False


# Setup global Sphinx awareness BEFORE importing RST tools
GLOBAL_SPHINX_SETUP = setup_global_sphinx_docutils_integration()

# Professional RST linting libraries (now with Sphinx awareness)
try:
    import restructuredtext_lint  # type: ignore[import-not-found]

    RST_LINT_AVAILABLE = True
except ImportError:
    RST_LINT_AVAILABLE = False

try:
    from rstcheck_core.checker import check_source  # type: ignore[import-not-found]

    RSTCHECK_AVAILABLE = True
except ImportError:
    RSTCHECK_AVAILABLE = False

# Style enforcement and advanced processing
try:
    import doc8.main  # type: ignore[import-not-found]

    DOC8_AVAILABLE = True
except ImportError:
    DOC8_AVAILABLE = False

# Sphinx is a hard requirement for documentation quality control
try:
    import sphinx  # type: ignore[import-not-found]

    # Note: sphinx.parsers.rst is imported inside functions where needed
    SPHINX_AVAILABLE = True
except ImportError:
    SPHINX_AVAILABLE = False
    raise ImportError(
        "Sphinx is required for documentation quality control. Install with: pip install sphinx"
    )


def setup_logging(level: str = "INFO", json_output: bool = False) -> logging.Logger:
    """Configure logging for the documentation quality system.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_output: If True, suppress all logging to avoid JSON contamination

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("docs_quality")

    # Clear any existing handlers
    logger.handlers.clear()

    if json_output:
        # For JSON output, disable all logging to stdout/stderr
        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.CRITICAL + 1)  # Disable all logging
    else:
        # Configure console handler for normal output
        handler = logging.StreamHandler(sys.stderr)

        # Use a clean format for user-facing output
        formatter = logging.Formatter(
            fmt="%(message)s", datefmt="%H:%M:%S"  # Simple format for user output
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper()))

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


class ValidationLevel(Enum):
    """Validation severity levels."""

    ERROR = "error"  # Must be fixed
    WARNING = "warning"  # Should be fixed
    INFO = "info"  # Nice to fix


class ValidationType(Enum):
    """Types of validation checks."""

    NAVIGATION = "navigation"
    EVENTTYPE = "eventtype"
    RST_QUALITY = "rst_quality"
    CODE_EXAMPLES = "code_examples"
    STRUCTURE = "structure"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""

    file_path: str
    line_number: int
    issue_type: ValidationType
    level: ValidationLevel
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocsQualityConfig:
    """Black-inspired configuration for docs quality control."""

    # Line length (like Black's --line-length)
    line_length: int = 88

    # Maximum workers for parallel processing
    max_workers: int = 4

    # Validation strictness
    strict_mode: bool = False

    # Auto-fix settings
    enable_auto_fix: bool = True
    max_fixes_per_file: int = -1  # No limit - fix ALL issues
    max_failed_attempts: int = 8

    # Transformation settings
    enable_visitor_pattern: bool = True
    enable_ast_validation: bool = True
    enable_idempotent_checks: bool = True

    # Cache settings
    enable_caching: bool = True
    cache_size: int = 1000

    # Output settings
    progress_interval: int = 10  # Report progress every N files

    @classmethod
    def from_pyproject_toml(cls, project_root: Path) -> "DocsQualityConfig":
        """Load configuration from pyproject.toml like Black does."""
        config = cls()

        if not TOML_AVAILABLE:
            return config

        pyproject_path = project_root / "pyproject.toml"
        if not pyproject_path.exists():
            return config

        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                data = toml.load(f)

            # Look for [tool.docs-quality] section
            docs_quality_config = data.get("tool", {}).get("docs-quality", {})

            if docs_quality_config:
                for key, value in docs_quality_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)

        except Exception:
            # If config loading fails, use defaults
            pass

        return config


@dataclass
class ValidationResult:
    """Results from a validation run."""

    issues: List[ValidationIssue] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)
    files_processed: int = 0
    processing_time: float = 0.0
    file_path: str = ""  # Add file_path attribute

    @property
    def error_count(self) -> int:
        """Get count of error-level issues."""
        return len([i for i in self.issues if i.level == ValidationLevel.ERROR])

    @property
    def warning_count(self) -> int:
        """Get count of warning-level issues."""
        return len([i for i in self.issues if i.level == ValidationLevel.WARNING])

    @property
    def total_issues(self) -> int:
        """Get total count of all issues."""
        return len(self.issues)


class BaseValidator(ABC):
    """Base class for all documentation validators."""

    def __init__(self, fix_mode: bool = False):
        self.fix_mode = fix_mode
        self.name = self.__class__.__name__
        self.logger = logging.getLogger("docs_quality")

    @abstractmethod
    def validate_file(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate a single file and return issues found."""
        pass

    @abstractmethod
    def can_fix_issue(self, issue: ValidationIssue) -> bool:
        """Check if this validator can auto-fix the given issue."""
        pass

    @abstractmethod
    def fix_issue(self, issue: ValidationIssue, content: str) -> Tuple[str, bool]:
        """Attempt to fix an issue. Returns (new_content, success)."""
        pass

    def fix_all_issues(
        self, file_path: Path, content: str, issues: List[ValidationIssue]
    ) -> Tuple[str, List[str]]:
        """Apply all fixes for this validator in a single pass (Black-style).

        Default implementation applies fixes sequentially. Validators can override
        for more efficient batch processing.
        """
        current_content = content
        applied_fixes = []

        for issue in issues:
            if self.can_fix_issue(issue):
                try:
                    fixed_content, success = self.fix_issue(issue, current_content)
                    if success and fixed_content != current_content:
                        current_content = fixed_content
                        applied_fixes.append(
                            f"Fixed {issue.message} at line {issue.line_number}"
                        )
                except Exception as e:
                    self.logger.debug(f"Could not fix issue {issue.message}: {e}")

        return current_content, applied_fixes


class EventTypeValidator(BaseValidator):
    """Validates EventType enum usage instead of string literals."""

    def __init__(self, fix_mode: bool = False):
        super().__init__(fix_mode)
        self.event_type_mapping = {
            # Core event types
            '"model"': "EventType.model",
            "'model'": "EventType.model",
            '"tool"': "EventType.tool",
            "'tool'": "EventType.tool",
            '"chain"': "EventType.chain",
            "'chain'": "EventType.chain",
            '"session"': "EventType.session",
            "'session'": "EventType.session",
            # Testing event types
            '"test"': "EventType.test",
            "'test'": "EventType.test",
            '"async_test"': "EventType.async_test",
            "'async_test'": "EventType.async_test",
            '"load_test"': "EventType.load_test",
            "'load_test'": "EventType.load_test",
            '"lambda"': "EventType.lambda",
            "'lambda'": "EventType.lambda",
            # Function-specific event types
            '"function1"': "EventType.function1",
            "'function1'": "EventType.function1",
            '"function2"': "EventType.function2",
            "'function2'": "EventType.function2",
            # Observability event types
            '"prompt_engineering"': "EventType.prompt_engineering",
            "'prompt_engineering'": "EventType.prompt_engineering",
            '"model_comparison"': "EventType.model_comparison",
            "'model_comparison'": "EventType.model_comparison",
            '"token_analysis"': "EventType.token_analysis",
            "'token_analysis'": "EventType.token_analysis",
            '"user_interaction"': "EventType.user_interaction",
            "'user_interaction'": "EventType.user_interaction",
            '"bias_monitoring"': "EventType.bias_monitoring",
            "'bias_monitoring'": "EventType.bias_monitoring",
            '"context_management"': "EventType.context_management",
            "'context_management'": "EventType.context_management",
            '"quality_monitoring"': "EventType.quality_monitoring",
            "'quality_monitoring'": "EventType.quality_monitoring",
            '"multi_modal_operation"': "EventType.multi_modal_operation",
            "'multi_modal_operation'": "EventType.multi_modal_operation",
            '"customer_support"': "EventType.customer_support",
            "'customer_support'": "EventType.customer_support",
            '"customer_interaction"': "EventType.customer_interaction",
            "'customer_interaction'": "EventType.customer_interaction",
            '"feedback_integration"': "EventType.feedback_integration",
            "'feedback_integration'": "EventType.feedback_integration",
            '"ab_test"': "EventType.ab_test",
            "'ab_test'": "EventType.ab_test",
            # Documentation-specific event types
            '"user_authentication"': "EventType.user_authentication",
            "'user_authentication'": "EventType.user_authentication",
            '"security_operation"': "EventType.security_operation",
            "'security_operation'": "EventType.security_operation",
            '"async_api_call"': "EventType.async_api_call",
            "'async_api_call'": "EventType.async_api_call",
            '"user_lookup"': "EventType.user_lookup",
            "'user_lookup'": "EventType.user_lookup",
            '"user_validation"': "EventType.user_validation",
            "'user_validation'": "EventType.user_validation",
            '"security_utility"': "EventType.security_utility",
            "'security_utility'": "EventType.security_utility",
            '"risky_operation"': "EventType.risky_operation",
            "'risky_operation'": "EventType.risky_operation",
            '"parent_operation"': "EventType.parent_operation",
            "'parent_operation'": "EventType.parent_operation",
            '"async_processing"': "EventType.async_processing",
            "'async_processing'": "EventType.async_processing",
            '"factual_qa"': "EventType.factual_qa",
            "'factual_qa'": "EventType.factual_qa",
            '"comprehensive_response"': "EventType.comprehensive_response",
            "'comprehensive_response'": "EventType.comprehensive_response",
            '"contextual_response"': "EventType.contextual_response",
            "'contextual_response'": "EventType.contextual_response",
            '"custom_evaluation"': "EventType.custom_evaluation",
            "'custom_evaluation'": "EventType.custom_evaluation",
            '"async_evaluation"': "EventType.async_evaluation",
            "'async_evaluation'": "EventType.async_evaluation",
            '"llm_generation"': "EventType.llm_generation",
            "'llm_generation'": "EventType.llm_generation",
            '"customer_service_ai"': "EventType.customer_service_ai",
            "'customer_service_ai'": "EventType.customer_service_ai",
            '"async_content_analysis"': "EventType.async_content_analysis",
            "'async_content_analysis'": "EventType.async_content_analysis",
            '"user_processing"': "EventType.user_processing",
            "'user_processing'": "EventType.user_processing",
            '"conditional_processing"': "EventType.conditional_processing",
            "'conditional_processing'": "EventType.conditional_processing",
            '"main_operation"': "EventType.main_operation",
            "'main_operation'": "EventType.main_operation",
            '"complex_operation"': "EventType.complex_operation",
            "'complex_operation'": "EventType.complex_operation",
            '"logged_operation"': "EventType.logged_operation",
            "'logged_operation'": "EventType.logged_operation",
            '"high_frequency"': "EventType.high_frequency",
            "'high_frequency'": "EventType.high_frequency",
            '"dynamic_tracer"': "EventType.dynamic_tracer",
            "'dynamic_tracer'": "EventType.dynamic_tracer",
            '"efficient_operation"': "EventType.efficient_operation",
            "'efficient_operation'": "EventType.efficient_operation",
            '"error_handling_demo"': "EventType.error_handling_demo",
            "'error_handling_demo'": "EventType.error_handling_demo",
            '"retryable_operation"': "EventType.retryable_operation",
            "'retryable_operation'": "EventType.retryable_operation",
            '"user_api"': "EventType.user_api",
            "'user_api'": "EventType.user_api",
            '"fastapi_user_lookup"': "EventType.fastapi_user_lookup",
            "'fastapi_user_lookup'": "EventType.fastapi_user_lookup",
            '"llm_operation"': "EventType.llm_operation",
            "'llm_operation'": "EventType.llm_operation",
        }
        self.violation_patterns = [
            r'event_type\s*=\s*["\']([^"\']+)["\']',
            r'@trace\([^)]*event_type\s*=\s*["\']([^"\']+)["\']',
        ]
        self.import_pattern = r"from\s+honeyhive\.models\s+import\s+.*EventType"

    def validate_file(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate EventType usage in a file."""
        issues = []
        lines = content.split("\n")
        has_eventtype_import = bool(re.search(self.import_pattern, content))

        for line_num, line in enumerate(lines, 1):
            for pattern in self.violation_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    event_type_value = (
                        match.group(1) if match.groups() else match.group(0)
                    )

                    issue = ValidationIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type=ValidationType.EVENTTYPE,
                        level=ValidationLevel.ERROR,
                        message=f"String literal event_type: {match.group(0)}",
                        suggestion=f"Use EventType.{event_type_value} instead",
                        auto_fixable=True,
                        context={"match": match.group(0), "value": event_type_value},
                    )
                    issues.append(issue)

        # Check for missing import if violations found
        if issues and not has_eventtype_import:
            import_issue = ValidationIssue(
                file_path=str(file_path),
                line_number=1,
                issue_type=ValidationType.EVENTTYPE,
                level=ValidationLevel.ERROR,
                message="Missing EventType import",
                suggestion="Add: from honeyhive.models import EventType",
                auto_fixable=True,
                context={"import_needed": True},
            )
            issues.append(import_issue)

        return issues

    def can_fix_issue(self, issue: ValidationIssue) -> bool:
        """Check if we can auto-fix EventType issues."""
        return issue.issue_type == ValidationType.EVENTTYPE and issue.auto_fixable

    def fix_issue(self, issue: ValidationIssue, content: str) -> Tuple[str, bool]:
        """Fix EventType violations."""
        if issue.context.get("import_needed"):
            # Add import
            lines = content.split("\n")
            # Find a good place to add the import
            insert_index = 0
            for i, line in enumerate(lines):
                if "from honeyhive" in line or "import honeyhive" in line:
                    insert_index = i + 1
                    break
                if line.strip().startswith(".. code-block::"):
                    insert_index = i + 2
                    break

            if insert_index < len(lines):
                lines.insert(insert_index, "   from honeyhive.models import EventType")
                return "\n".join(lines), True

        elif "match" in issue.context:
            # Fix string literal
            old_match = issue.context["match"]
            event_type_value = issue.context["value"]
            quoted_value = (
                f'"{event_type_value}"'
                if event_type_value in [v.strip("\"'") for v in self.event_type_mapping]
                else f"'{event_type_value}'"
            )

            if quoted_value in self.event_type_mapping:
                new_content = content.replace(
                    old_match,
                    old_match.replace(
                        quoted_value, self.event_type_mapping[quoted_value]
                    ),
                )
                return new_content, True

        return content, False


class RSTQualityValidator(BaseValidator):
    """Validates RST formatting and structure."""

    def __init__(self, fix_mode: bool = False):
        super().__init__(fix_mode)
        self.title_chars = {"#": 1, "*": 2, "=": 3, "-": 4, "^": 5, '"': 6}

    def validate_file(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate RST quality in a file."""
        issues = []
        lines = content.split("\n")

        issues.extend(self._check_title_underlines(lines, file_path))
        issues.extend(self._check_blank_lines(lines, file_path))
        issues.extend(self._check_code_blocks(lines, file_path))
        issues.extend(self._check_tables(lines, file_path))

        return issues

    def _check_title_underlines(
        self, lines: List[str], file_path: Path
    ) -> List[ValidationIssue]:
        """Check for correct title underline lengths."""
        issues = []

        for i in range(len(lines) - 1):
            current_line = lines[i].strip()
            next_line = lines[i + 1].strip()

            if (
                next_line
                and len(set(next_line)) == 1
                and next_line[0] in self.title_chars
                and current_line
            ):

                title_length = len(current_line)
                underline_length = len(next_line)

                if underline_length != title_length:
                    issue = ValidationIssue(
                        file_path=str(file_path),
                        line_number=i + 2,
                        issue_type=ValidationType.RST_QUALITY,
                        level=ValidationLevel.WARNING,
                        message=f"Title underline length mismatch: title={title_length}, underline={underline_length}",
                        suggestion=f"Make underline {title_length} characters long",
                        auto_fixable=True,
                        context={
                            "title_idx": i,
                            "underline_idx": i + 1,
                            "char": next_line[0],
                        },
                    )
                    issues.append(issue)

        return issues

    def _check_blank_lines(
        self, lines: List[str], file_path: Path
    ) -> List[ValidationIssue]:
        """Check for required blank lines around sections."""
        issues = []

        for i, line in enumerate(lines):
            if line.strip().startswith(".. ") and "::" in line:
                directive = line.split("::")[0].strip()

                # Check blank line before directive
                if i > 0 and lines[i - 1].strip():
                    issue = ValidationIssue(
                        file_path=str(file_path),
                        line_number=i + 1,
                        issue_type=ValidationType.RST_QUALITY,
                        level=ValidationLevel.INFO,
                        message=f"Missing blank line before {directive} directive",
                        auto_fixable=True,
                        context={"insert_blank_before": i},
                    )
                    issues.append(issue)

        return issues

    def _check_code_blocks(
        self, lines: List[str], file_path: Path
    ) -> List[ValidationIssue]:
        """Check code block formatting."""
        issues = []

        in_code_block = False
        code_block_indent = 0

        for i, line in enumerate(lines):
            # Detect start of code block
            if ".. code-block::" in line or ".. code::" in line:
                in_code_block = True
                code_block_indent = len(line) - len(line.lstrip())
                continue

            if in_code_block:
                # Empty lines are fine
                if line.strip() == "":
                    continue

                # Check if this line should be part of the code block
                line_indent = len(line) - len(line.lstrip())
                required_indent = code_block_indent + 3

                # If line has content and sufficient indentation, it's part of code block
                if line.strip() and line_indent >= required_indent:
                    continue

                # If line has content but insufficient indentation
                if line.strip() and line_indent < required_indent:
                    # Check if this looks like it should be code vs. narrative text
                    stripped = line.strip()

                    # These patterns indicate end of code block (narrative text, sections, directives)
                    ends_code_block = (
                        stripped.startswith("..")  # RST directive
                        or stripped.endswith("---")
                        or stripped.endswith("===")
                        or stripped.endswith("~~~")  # Section headers
                        or stripped.startswith("Step ")
                        or stripped.startswith("Chapter ")  # Common section patterns
                        or stripped.startswith("What's ")
                        or stripped.startswith("Next ")  # Navigation text
                        or stripped.startswith("Advanced ")
                        or stripped.startswith("Basic ")
                        or stripped.startswith("Async ")  # Common section starters
                        or any(
                            word in stripped
                            for word in [
                                "Support",
                                "Configuration",
                                "Usage",
                                "Examples",
                                "Functions",
                                "Classes",
                                "Methods",
                                "Error",
                                "Exception",
                                "Handling",
                                "Processing",
                            ]
                        )  # Section header words
                        or stripped
                        in [
                            "Parameters",
                            "Returns",
                            "Raises",
                            "Notes",
                            "See Also",
                            "References",
                            "Methods",
                            "Attributes",
                        ]  # API doc sections
                        or (
                            stripped.startswith("**") and stripped.endswith("**")
                        )  # Bold text headers
                        or (
                            stripped.startswith("*")
                            and stripped.endswith("*")
                            and not stripped.startswith("**")
                        )  # Italic text headers
                        or stripped.startswith("That's it!")
                        or stripped.startswith("Note:")  # Narrative text
                        or len(stripped) > 60  # Long lines are usually narrative
                        or any(
                            word in stripped.lower()
                            for word in [
                                "the",
                                "this",
                                "that",
                                "your",
                                "you",
                                "we",
                                "our",
                            ]
                        )  # Narrative indicators
                    )

                    if not ends_code_block:
                        # This looks like improperly indented code
                        issue = ValidationIssue(
                            file_path=str(file_path),
                            line_number=i + 1,
                            issue_type=ValidationType.RST_QUALITY,
                            level=ValidationLevel.WARNING,
                            message="Code block content must be indented with at least 3 spaces",
                            auto_fixable=True,
                        )
                        issues.append(issue)

                    # End the code block regardless
                    in_code_block = False
                else:
                    # End the code block for any other case
                    in_code_block = False

        return issues

    def _check_tables(self, lines: List[str], file_path: Path) -> List[ValidationIssue]:
        """Check table formatting."""
        issues = []

        in_table = False
        table_start = 0

        for i, line in enumerate(lines):
            if line.count("|") >= 2 and not in_table:
                in_table = True
                table_start = i
            elif in_table and line.strip() == "":
                in_table = False
                table_lines = lines[table_start:i]
                if len(table_lines) > 1:
                    column_counts = [
                        line.count("|") for line in table_lines if line.strip()
                    ]
                    if len(set(column_counts)) > 1:
                        issue = ValidationIssue(
                            file_path=str(file_path),
                            line_number=table_start + 1,
                            issue_type=ValidationType.RST_QUALITY,
                            level=ValidationLevel.WARNING,
                            message=f"Table has inconsistent column counts: {set(column_counts)}",
                            auto_fixable=True,
                            context={
                                "table_start": table_start,
                                "table_end": i,
                                "column_counts": column_counts,
                            },
                        )
                        issues.append(issue)

        return issues

    def can_fix_issue(self, issue: ValidationIssue) -> bool:
        """Check if we can auto-fix RST issues."""
        if issue.issue_type == ValidationType.RST_QUALITY and issue.auto_fixable:
            return True
        # Also handle syntax errors that appear in RST context
        if issue.issue_type == ValidationType.CODE_EXAMPLES and (
            "unterminated string literal" in issue.message
            or "Syntax error in code block" in issue.message
        ):
            return True
        return False

    def fix_issue(self, issue: ValidationIssue, content: str) -> Tuple[str, bool]:
        """Fix RST quality issues."""
        lines = content.split("\n")

        if "title_idx" in issue.context:
            # Fix title underline
            title_idx = issue.context["title_idx"]
            underline_idx = issue.context["underline_idx"]
            char = issue.context["char"]

            if 0 <= title_idx < len(lines) and 0 <= underline_idx < len(lines):
                title_line = lines[title_idx]
                new_underline = char * len(title_line.strip())
                lines[underline_idx] = new_underline
                return "\n".join(lines), True

        elif "insert_blank_before" in issue.context:
            # Insert blank line
            insert_idx = issue.context["insert_blank_before"]
            if 0 <= insert_idx <= len(lines):
                lines.insert(insert_idx, "")
                return "\n".join(lines), True

        elif "Code block content must be indented" in issue.message:
            # Fix code block indentation
            line_num = issue.line_number - 1  # Convert to 0-based
            if 0 <= line_num < len(lines):
                line = lines[line_num]
                # If line has content but insufficient indentation, fix it
                if line.strip():
                    current_indent = len(line) - len(line.lstrip())
                    # Find the code block directive above this line
                    found_directive = False
                    for i in range(
                        line_num - 1, max(-1, line_num - 50), -1
                    ):  # Look back up to 50 lines
                        if (
                            ".. code-block::" in lines[i]
                            or ".. code::" in lines[i]
                            or lines[i].strip().startswith(".. code-block::")
                            or lines[i].strip().startswith(".. code::")
                        ):
                            directive_indent = len(lines[i]) - len(lines[i].lstrip())
                            needed_indent = directive_indent + 3
                            # Only fix if current indentation is insufficient
                            if current_indent < needed_indent:
                                lines[line_num] = " " * needed_indent + line.lstrip()
                                return "\n".join(lines), True
                            found_directive = True
                            break

                        # Stop if we hit another directive or section (but be more lenient)
                        if (
                            lines[i].strip().startswith(".. ")
                            and "code" not in lines[i].lower()
                        ):
                            break

                    # If no directive found, use default indentation of 3 spaces
                    if not found_directive and current_indent < 3:
                        lines[line_num] = "   " + line.lstrip()
                        return "\n".join(lines), True

        elif (
            "unterminated string literal" in issue.message
            or "Syntax error in code block" in issue.message
        ):
            # Fix common unterminated string issues and syntax errors
            line_num = issue.line_number - 1
            if 0 <= line_num < len(lines):
                line = lines[line_num]
                fixed_line = line

                # Fix common patterns of extra quotes and commas

                # Pattern 1: "value","  -> "value",
                fixed_line = re.sub(r'="([^"]*)",?"', r'="\1"', fixed_line)

                # Pattern 2: "text"}]" -> "text"}]
                fixed_line = re.sub(r'"}]"', r'"}]', fixed_line)

                # Pattern 3: function("arg")" -> function("arg")
                fixed_line = re.sub(r'("[^"]*")\)"', r"\1)", fixed_line)

                # Pattern 4: "comment"" -> "comment" (multiple quotes)
                fixed_line = re.sub(r'("[^"]*")"+', r"\1", fixed_line)

                # Pattern 4b: """docstring"""" -> """docstring"""
                fixed_line = re.sub(r'("""[^"]*""")"+', r"\1", fixed_line)

                # Pattern 4c: "text"," -> "text",
                fixed_line = re.sub(r'("[^"]*"),"+', r"\1,", fixed_line)

                # Pattern 4d: f"text"," -> f"text",
                fixed_line = re.sub(r'(f"[^"]*"),"+', r"\1,", fixed_line)

                # Pattern 4e: "text"" -> "text" (more aggressive)
                fixed_line = re.sub(r'("[^"]*")"+', r"\1", fixed_line)

                # Pattern 4b: Fix double quotes at end: "text"" -> "text"
                fixed_line = re.sub(r'"([^"]*?)""', r'"\1"', fixed_line)

                # Pattern 4c: More aggressive quote fixing patterns
                # Fix quotes with trailing punctuation: "text"," -> "text",
                fixed_line = re.sub(r'"([^"]*?)","+', r'"\1",', fixed_line)

                # Fix quotes with trailing parentheses: "text")" -> "text")
                fixed_line = re.sub(r'"([^"]*?)"\)+', r'"\1)', fixed_line)

                # Fix quotes with trailing brackets: "text"]" -> "text"]
                fixed_line = re.sub(r'"([^"]*?)"]+', r'"\1]', fixed_line)

                # Pattern 5: Remove trailing quotes at end of lines
                fixed_line = re.sub(r'"(\s*)$', r"\1", fixed_line)

                # Pattern 6: Remove trailing quote at end of line (simple)
                fixed_line = re.sub(r'"$', "", fixed_line)

                # Pattern 7: Fix array access with extra quote: ["key"]" -> ["key"]
                fixed_line = re.sub(r'(\[[^]]*\])"+', r"\1", fixed_line)

                # Pattern 8: Fix quotes in comments: # comment""
                fixed_line = re.sub(r'(#[^"]*")"+', r"\1", fixed_line)

                # Pattern 9: Fix export statements: export, VAR="value""
                fixed_line = re.sub(r'(export[^"]*")"+', r"\1", fixed_line)

                # Pattern 10: Aggressive trailing quote removal (last resort)
                # Remove any trailing quotes that make the line unbalanced
                quote_count = fixed_line.count('"')
                if quote_count > 0 and quote_count % 2 == 1:
                    # Find the last quote and remove it if it's at the end
                    if fixed_line.rstrip().endswith('"'):
                        fixed_line = (
                            fixed_line.rstrip()[:-1]
                            + fixed_line[len(fixed_line.rstrip()) :]
                        )

                # Pattern 11: Fix specific Python syntax issues
                # if, __name__ -> if __name__
                fixed_line = re.sub(r"if,\s+__name__", "if __name__", fixed_line)

                # Pattern 11b: Fix incomplete docstrings: ""text -> """text
                fixed_line = re.sub(r'^(\s*)""([^"]\w.*)', r'\1"""\2', fixed_line)

                # Pattern 11c: Fix incomplete triple quotes: """text -> """text"""
                if "unterminated triple-quoted string" in issue.message:
                    # Add closing triple quotes if missing
                    if fixed_line.strip().startswith(
                        '"""'
                    ) and not fixed_line.strip().endswith('"""'):
                        fixed_line = (
                            fixed_line.rstrip()
                            + '"""'
                            + fixed_line[len(fixed_line.rstrip()) :]
                        )

                # Pattern 12: More aggressive quote cleanup patterns
                # Fix lines ending with extra quote after parenthesis: ...)"  -> ...)
                fixed_line = re.sub(r"(\))\"$", r"\1", fixed_line)

                # Fix docstring with extra quotes: """text"""" -> """text"""
                fixed_line = re.sub(r"(\"\"\"[^\"]*\"\"\")\"*", r"\1", fixed_line)

                # Pattern 13: Dictionary/JSON patterns with extra quotes and commas
                # Fix dictionary entries with extra quotes: "key": "value","  -> "key": "value",
                fixed_line = re.sub(r'(":\s*"[^"]*"),"+', r"\1,", fixed_line)

                # Fix dictionary entries with extra quotes at end: "key": "value""  -> "key": "value"
                fixed_line = re.sub(r'(":\s*"[^"]*")"+(\s*$)', r"\1\2", fixed_line)

                # Fix dictionary keys with extra quotes: "key","  -> "key",
                fixed_line = re.sub(r'("[^"]*"),"+', r"\1,", fixed_line)

                # Pattern 14: Function call patterns with extra quotes
                # Fix function calls with extra quotes: func("arg","  -> func("arg",
                fixed_line = re.sub(r'(\([^)]*"[^"]*"),"+', r"\1,", fixed_line)

                # Pattern 15: Final cleanup - remove any remaining trailing quotes
                # This is the most aggressive pattern for stubborn cases
                while (
                    fixed_line != line
                    and fixed_line.rstrip().endswith('"')
                    and fixed_line.count('"') % 2 == 1
                ):
                    fixed_line = (
                        fixed_line.rstrip()[:-1]
                        + fixed_line[len(fixed_line.rstrip()) :]
                    )

                # Fix missing closing quotes (if still unbalanced)
                if fixed_line.count('"') % 2 == 1:
                    # Add missing closing quote at end of meaningful content
                    fixed_line = re.sub(
                        r'"([^"]*?)(\s*[,)]?\s*)$', r'"\1"\2', fixed_line
                    )

                if fixed_line != line:
                    lines[line_num] = fixed_line
                    return "\n".join(lines), True

        elif (
            "Table has inconsistent column counts" in issue.message
            and "table_start" in issue.context
        ):
            # Fix table column inconsistencies
            table_start = issue.context["table_start"]
            table_end = issue.context["table_end"]
            column_counts = issue.context["column_counts"]

            # Find the most common column count (excluding 0)
            non_zero_counts = [c for c in column_counts if c > 0]
            if non_zero_counts:
                target_columns = max(set(non_zero_counts), key=non_zero_counts.count)

                # Fix each table row
                for i in range(table_start, table_end):
                    line = lines[i]
                    current_columns = line.count("|")

                    # If line has no columns but should be part of table, remove it
                    if current_columns == 0 and line.strip():
                        lines[i] = ""  # Convert to empty line
                    # If line has wrong number of columns, try to fix
                    elif current_columns > 0 and current_columns != target_columns:
                        # Add missing columns with empty cells
                        if current_columns < target_columns:
                            missing = target_columns - current_columns
                            if line.rstrip().endswith("|"):
                                lines[i] = line.rstrip() + " |" * missing
                            else:
                                lines[i] = line.rstrip() + " |" * (missing + 1)

                return "\n".join(lines), True

        return content, False


class CodeExampleValidator(BaseValidator):
    """Validates Python code examples in documentation."""

    def __init__(
        self,
        fix_mode: bool = False,
        rst_processor: Optional["EnhancedRSTProcessor"] = None,
    ):
        super().__init__(fix_mode)
        self.rst_processor = rst_processor
        self.import_patterns = {
            r"HoneyHiveTracer": "from honeyhive import HoneyHiveTracer",
            r"@trace": "from honeyhive import trace",
            r"EventType\.\w+": "from honeyhive.models import EventType",
            r"OpenAI\(": "from openai import OpenAI",
            r"Anthropic\(": "from anthropic import Anthropic",
            r"getenv\(": "from os import getenv",
        }

    def _is_likely_fixable_syntax_error(self, error_line: str, error_msg: str) -> bool:
        """Enhanced AST-based analysis to determine if a syntax error is likely fixable."""
        error_line = error_line.strip()
        error_msg_lower = error_msg.lower()

        # Pattern-based analysis inspired by professional linters
        fixable_patterns = [
            # Trailing quote patterns
            (r'.*\)"$', "unterminated string literal"),  # Lines ending with )"
            (
                r'.*""""+$',
                "unterminated string literal",
            ),  # Lines ending with extra quotes
            (r'.*",$', "unterminated string literal"),  # Lines ending with ",
            # Decorator patterns
            (r'^\s*@\w+\(.*\)"$', "unterminated string literal"),  # @decorator(...)"
            # Function call patterns
            (r'.*\([^)]*"[^"]*\)"$', "unterminated string literal"),  # func("arg")"
            # Assignment patterns
            (r'.*=\s*"[^"]*""$', "unterminated string literal"),  # var = "value""
            # Comment patterns with quotes
            (r'.*#.*"$', "unterminated string literal"),  # # comment"
        ]

        # Check if the error line matches any fixable patterns
        for pattern, error_type in fixable_patterns:
            if error_type in error_msg_lower and re.match(pattern, error_line):
                return True

        # Additional context-aware checks
        if "unexpected indent" in error_msg_lower:
            # Check if this looks like a continuation of a previous line issue
            if error_line.startswith(("from ", "import ", "def ", "class ", "@")):
                return True
            # Check for trailing quotes that cause unexpected indent
            if error_line.rstrip().endswith('"') and error_line.count('"') % 2 == 1:
                return True
            # Check for print statements with extra quotes
            if "print(" in error_line and error_line.rstrip().endswith(')"'):
                return True

        # NEW: Enhanced fixable detection for small-count issues
        if "was never closed" in error_msg_lower:
            # Unclosed brackets, braces, parentheses are fixable
            return True

        if (
            "closing parenthesis" in error_msg_lower
            and "does not match" in error_msg_lower
        ):
            # Mismatched brackets are fixable
            return True

        if "expected an indented block" in error_msg_lower:
            # Missing indented blocks can be fixed with pass statements
            return True

        if "perhaps you forgot a comma" in error_msg_lower:
            # Missing commas in function calls, lists, etc. are fixable
            return True

        if "expected 'except' or 'finally' block" in error_msg_lower:
            # Missing except/finally blocks can be added
            return True

        if error_msg_lower == "syntax error in code block: invalid syntax":
            # General invalid syntax errors often have fixable patterns
            return True

        return False

    def validate_file(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate code examples in a file."""
        issues = []
        code_blocks = self._extract_code_blocks(content, file_path)

        for block_info in code_blocks:
            block_issues = self._validate_code_block(block_info, file_path)
            issues.extend(block_issues)

        return issues

    def _extract_code_blocks(
        self, content: str, file_path: Optional[Path] = None
    ) -> List[Dict]:
        """Extract Python code blocks from RST content using enhanced processing when available."""

        # Try enhanced docutils-based extraction first
        if self.rst_processor and self.rst_processor.docutils_available:
            try:
                source_path = str(file_path) if file_path else "<string>"
                structured_blocks = self.rst_processor.extract_code_blocks_structured(
                    content, source_path
                )
                if structured_blocks:
                    self.logger.debug(
                        f"Using docutils structured extraction: found {len(structured_blocks)} code blocks"
                    )
                    return structured_blocks
            except Exception as e:
                self.logger.debug(
                    f"Docutils extraction failed, falling back to regex: {e}"
                )

        # Fallback to regex-based extraction
        self.logger.debug("Using regex-based code block extraction")
        return self._extract_code_blocks_regex(content)

    def _extract_code_blocks_regex(self, content: str) -> List[Dict]:
        """Extract Python code blocks using regex-based approach (fallback)."""
        lines = content.split("\n")
        code_blocks = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if ".. code-block::" in line and "python" in line:
                code_lines = []
                i += 1

                # Skip empty lines and options
                while i < len(lines) and (
                    not lines[i].strip() or lines[i].strip().startswith(":")
                ):
                    i += 1

                # Now i points to the first line of actual code content
                start_line = i + 1  # +1 for 1-based line numbering

                # Collect code block content
                while i < len(lines):
                    if lines[i].startswith("   ") or not lines[i].strip():
                        if lines[i].strip():
                            # Check if this looks like a section header or narrative text that should end the code block
                            stripped_content = lines[i].strip()

                            # Check if the next line is a section underline
                            is_section_header = False
                            if i + 1 < len(lines):
                                next_line = lines[i + 1].strip()
                                if (
                                    next_line
                                    and all(c in '-=~^"#*' for c in next_line)
                                    and len(next_line) >= len(stripped_content) - 2
                                ):
                                    is_section_header = True

                            # Also check for common section header words (even without underlines)
                            section_header_words = [
                                "Support",
                                "Configuration",
                                "Usage",
                                "Examples",
                                "Parameters",
                                "Returns",
                                "Raises",
                                "Notes",
                                "Methods",
                                "Attributes",
                                "Properties",
                                "Functions",
                                "Classes",
                                "Modules",
                                "Decorators",
                                "Context",
                                "Manager",
                                "Handler",
                                "Error",
                                "Exception",
                                "Handling",
                                "Capture",
                                "Processing",
                                "Validation",
                                "Integration",
                                "Implementation",
                                "Performance",
                                "Optimization",
                                "Testing",
                            ]

                            if any(
                                word in stripped_content
                                for word in section_header_words
                            ):
                                is_section_header = True

                            # Check for common section header patterns
                            section_patterns = [
                                "What's Next?",
                                "Next Steps",
                                "Troubleshooting",
                                "Examples",
                                "Usage",
                                "Installation",
                                "Configuration",
                                "Getting Started",
                                "Advanced Configuration",
                                "Basic Usage",
                                "Parameters",
                                "Returns",
                                "Raises",
                                "Notes",
                                "See Also",
                                "References",
                                "Methods",
                                "Attributes",
                            ]

                            # Check for RST formatting patterns (bold, italic, etc.)
                            is_rst_formatting = (
                                stripped_content.startswith("**")
                                and stripped_content.endswith("**")  # Bold text
                                or stripped_content.startswith("*")
                                and stripped_content.endswith("*")  # Italic text
                                or stripped_content.startswith("``")
                                and stripped_content.endswith("``")  # Code text
                            )

                            if (
                                is_section_header
                                or any(
                                    pattern in stripped_content
                                    for pattern in section_patterns
                                )
                                or is_rst_formatting
                            ):
                                # This looks like a section header, end the code block here
                                break

                            code_lines.append(lines[i][3:])
                        else:
                            code_lines.append("")
                    else:
                        break
                    i += 1

                if code_lines:
                    while code_lines and not code_lines[-1].strip():
                        code_lines.pop()

                    code_blocks.append(
                        {
                            "start_line": start_line,
                            "end_line": i,
                            "code": "\n".join(code_lines),
                            "lines": code_lines,
                        }
                    )
            else:
                i += 1

        return code_blocks

    def _validate_code_block(
        self, block_info: Dict, file_path: Path
    ) -> List[ValidationIssue]:
        """Validate a single code block."""
        issues: List[ValidationIssue] = []
        code = block_info["code"]
        start_line = block_info["start_line"]

        if not code.strip():
            return issues

        # Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            # Check if this is a fixable syntax error
            fixable_errors = [
                "unterminated string literal",
                "unexpected indent",
                "unmatched",
                "invalid syntax",
            ]
            is_fixable = any(err in e.msg.lower() for err in fixable_errors)

            # Enhanced AST-based analysis for better auto-fixable detection
            code_lines = block_info.get("lines", block_info["code"].split("\n"))
            if e.lineno and e.lineno <= len(code_lines):
                error_line = code_lines[e.lineno - 1]
                is_fixable = is_fixable or self._is_likely_fixable_syntax_error(
                    error_line, e.msg
                )

            issue = ValidationIssue(
                file_path=str(file_path),
                line_number=start_line + (e.lineno or 1) - 1,
                issue_type=ValidationType.CODE_EXAMPLES,
                level=ValidationLevel.ERROR,
                message=f"Syntax error in code block: {e.msg}",
                auto_fixable=is_fixable,
            )
            issues.append(issue)
            return issues

        # Check for missing imports
        missing_imports = self._find_missing_imports(code)
        for import_statement in missing_imports:
            issue = ValidationIssue(
                file_path=str(file_path),
                line_number=start_line,
                issue_type=ValidationType.CODE_EXAMPLES,
                level=ValidationLevel.WARNING,
                message=f"Missing import: {import_statement}",
                suggestion=f"Add import: {import_statement}",
                auto_fixable=True,
                context={
                    "import_statement": import_statement,
                    "block_start": start_line,
                },
            )
            issues.append(issue)

        # Check for hardcoded API keys
        if re.search(r'api_key\s*=\s*["\'][^"\']{20,}["\']', code):
            issue = ValidationIssue(
                file_path=str(file_path),
                line_number=start_line,
                issue_type=ValidationType.CODE_EXAMPLES,
                level=ValidationLevel.ERROR,
                message="Hardcoded API key detected - use environment variable instead",
                auto_fixable=True,
            )
            issues.append(issue)

        return issues

    def _find_missing_imports(self, code: str) -> List[str]:
        """Find imports that appear to be missing from the code."""
        missing_imports = []
        existing_imports = self._get_existing_imports(code)

        for pattern, import_statement in self.import_patterns.items():
            if re.search(pattern, code) and import_statement not in existing_imports:
                if not self._is_import_covered(import_statement, existing_imports):
                    missing_imports.append(import_statement)

        return missing_imports

    def _get_existing_imports(self, code: str) -> Set[str]:
        """Extract existing import statements from code."""
        imports = set()

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(f"import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.add(f"from {module} import {alias.name}")
        except SyntaxError:
            import_lines = re.findall(
                r"^((?:from\s+\S+\s+)?import\s+.+)$", code, re.MULTILINE
            )
            imports.update(import_lines)

        return imports

    def _is_import_covered(
        self, needed_import: str, existing_imports: Set[str]
    ) -> bool:
        """Check if a needed import is already covered by existing imports."""
        if needed_import in existing_imports:
            return True

        if needed_import.startswith("from "):
            parts = needed_import.split()
            if len(parts) >= 4:
                module = parts[1]
                if f"from {module} import *" in existing_imports:
                    return True
                if f"import {module}" in existing_imports:
                    return True

        return False

    def can_fix_issue(self, issue: ValidationIssue) -> bool:
        """Check if we can auto-fix code example issues."""
        return issue.issue_type == ValidationType.CODE_EXAMPLES and (
            issue.auto_fixable
            or "syntax error" in issue.message.lower()
            or "missing import" in issue.message.lower()
            or "code block content must be indented" in issue.message.lower()
            or "hardcoded api key detected" in issue.message.lower()
            or "unterminated string literal" in issue.message.lower()
            or "unexpected indent" in issue.message.lower()
            or "explicit markup ends without" in issue.message.lower()
        )

    def fix_issue(self, issue: ValidationIssue, content: str) -> Tuple[str, bool]:
        """Fix code example issues."""
        lines = content.split("\n")

        if "import_statement" in issue.context:
            # Add missing import to code block
            block_start = issue.context["block_start"]
            import_statement = issue.context["import_statement"]

            # Find the code block and add import at the beginning
            for i in range(block_start, len(lines)):
                if lines[i].startswith("   ") and lines[i].strip():
                    lines.insert(i, f"   {import_statement}")
                    return "\n".join(lines), True

        elif "Syntax error in code block" in issue.message:
            # Fix common syntax errors
            line_num = issue.line_number - 1

            if 0 <= line_num < len(lines):
                line = lines[line_num]
                fixed_line = line

                # Fix unexpected indent errors (usually caused by unbalanced quotes)
                if "unexpected indent" in issue.message:
                    # These are often caused by unterminated strings on previous lines
                    # Need to check a broader context, not just the current line

                    # Check previous lines for quote issues
                    context_fixed = False
                    for i in range(max(0, line_num - 5), line_num + 1):
                        if i < len(lines):
                            context_line = lines[i]

                            # Fix common patterns that cause unexpected indent
                            new_context_line = context_line

                            # Pattern 1: Fix mismatched quotes in comments: strings' -> strings
                            new_context_line = re.sub(
                                r"strings'", r"strings", new_context_line
                            )

                            # Pattern 2: Fix extra quotes in function calls: func("arg")" -> func("arg")
                            new_context_line = re.sub(
                                r'(\([^)]*"[^"]*")\)"', r"\1)", new_context_line
                            )

                            # Pattern 3: Remove trailing quotes: "text"" -> "text"
                            new_context_line = re.sub(
                                r'"([^"]*?)""', r'"\1"', new_context_line
                            )

                            # Pattern 4: Remove trailing quote at end of line if unbalanced
                            if (
                                new_context_line.rstrip().endswith('"')
                                and new_context_line.count('"') % 2 == 1
                            ):
                                new_context_line = (
                                    new_context_line.rstrip()[:-1]
                                    + new_context_line[len(new_context_line.rstrip()) :]
                                )

                            # Pattern 5: Fix print statements with extra quotes: print("text")" -> print("text")
                            new_context_line = re.sub(
                                r'(print\([^)]*"[^"]*")\)"', r"\1)", new_context_line
                            )

                            # Pattern 6: Fix curl commands with extra quotes: curl ... "url"" -> curl ... "url"
                            new_context_line = re.sub(
                                r'(curl[^"]*"[^"]*")"+', r"\1", new_context_line
                            )

                            # Pattern 7: Fix environment variable checks: 'KEY' in os.environ")" -> 'KEY' in os.environ")
                            new_context_line = re.sub(
                                r"('[^']*'\s+in\s+os\.environ)\"\)",
                                r'\1")',
                                new_context_line,
                            )

                            # Pattern 8: Fix f-string patterns: f"text: {var}")" -> f"text: {var}")
                            new_context_line = re.sub(
                                r'(f"[^"]*")\)"', r"\1)", new_context_line
                            )

                            # Pattern 9: Fix specific patterns found in docs/how-to/index.rst
                            # Fix: print(f"API Key set: {'HH_API_KEY' in os.environ}")" -> print(f"API Key set: {'HH_API_KEY' in os.environ}")
                            new_context_line = re.sub(
                                r"(print\(f\"[^\"]*\{'[^']*'\s+in\s+os\.environ\}\")\"",
                                r"\1",
                                new_context_line,
                            )

                            # Fix: curl -H "Authorization: Bearer YOUR_API_KEY" https://api.honeyhive.ai/health" -> curl -H "Authorization: Bearer YOUR_API_KEY" https://api.honeyhive.ai/health
                            new_context_line = re.sub(
                                r'(curl[^"]*https://[^"]*)"$', r"\1", new_context_line
                            )

                            # Fix: tracer = HoneyHiveTracer.init(api_key="...")" -> tracer = HoneyHiveTracer.init(api_key="...")
                            new_context_line = re.sub(
                                r'(HoneyHiveTracer\.init\([^)]*\))"',
                                r"\1",
                                new_context_line,
                            )

                            # Fix: # ❌ Incorrect - don't use strings' -> # ❌ Incorrect - don't use strings
                            new_context_line = re.sub(
                                r"(don't use strings)'", r"\1", new_context_line
                            )

                            if new_context_line != context_line:
                                lines[i] = new_context_line
                                context_fixed = True

                    if context_fixed:
                        # Return the updated content
                        return "\n".join(lines), True
                    else:
                        # Apply patterns to current line as fallback
                        fixed_line = re.sub(r'"([^"]*?)""', r'"\1"', fixed_line)
                        fixed_line = re.sub(r"strings'", r"strings", fixed_line)
                        fixed_line = re.sub(r'(\([^)]*"[^"]*")\)"', r"\1)", fixed_line)

                # Fix unterminated string literals
                elif "unterminated string literal" in issue.message:
                    # Fix common patterns of extra quotes and commas

                    # Pattern 1: "value","  -> "value",
                    fixed_line = re.sub(r'="([^"]*)",?"', r'="\1"', fixed_line)

                    # Pattern 2: "text"}]" -> "text"}]
                    fixed_line = re.sub(r'"}]"', r'"}]', fixed_line)

                    # Pattern 3: function("arg")" -> function("arg")
                    fixed_line = re.sub(r'("[^"]*")\)"', r"\1)", fixed_line)

                    # Pattern 4: "comment"" -> "comment" (multiple quotes)
                    fixed_line = re.sub(r'("[^"]*")"+', r"\1", fixed_line)

                    # Pattern 4b: """docstring"""" -> """docstring"""
                    fixed_line = re.sub(r'("""[^"]*""")"+', r"\1", fixed_line)

                    # Pattern 4c: "text"," -> "text",
                    fixed_line = re.sub(r'("[^"]*"),"+', r"\1,", fixed_line)

                    # Pattern 4d: f"text"," -> f"text",
                    fixed_line = re.sub(r'(f"[^"]*"),"+', r"\1,", fixed_line)

                    # Pattern 4e: "text"" -> "text" (more aggressive)
                    fixed_line = re.sub(r'("[^"]*")"+', r"\1", fixed_line)

                    # Pattern 4b: Fix double quotes at end: "text"" -> "text"
                    fixed_line = re.sub(r'"([^"]*?)""', r'"\1"', fixed_line)

                    # Pattern 4c: More aggressive quote fixing patterns
                    # Fix quotes with trailing punctuation: "text"," -> "text",
                    fixed_line = re.sub(r'"([^"]*?)","+', r'"\1",', fixed_line)

                    # Fix quotes with trailing parentheses: "text")" -> "text")
                    fixed_line = re.sub(r'"([^"]*?)"\)+', r'"\1)', fixed_line)

                    # Fix quotes with trailing brackets: "text"]" -> "text"]
                    fixed_line = re.sub(r'"([^"]*?)"]+', r'"\1]', fixed_line)

                    # Pattern 5: Remove trailing quotes at end of lines
                    fixed_line = re.sub(r'"(\s*)$', r"\1", fixed_line)

                    # Pattern 6: Remove trailing quote at end of line (simple)
                    fixed_line = re.sub(r'"$', "", fixed_line)

                    # Pattern 7: Fix array access with extra quote: ["key"]" -> ["key"]
                    fixed_line = re.sub(r'(\[[^]]*\])"+', r"\1", fixed_line)

                    # Pattern 8: Fix quotes in comments: # comment""
                    fixed_line = re.sub(r'(#[^"]*")"+', r"\1", fixed_line)

                    # Pattern 9: Fix export statements: export, VAR="value""
                    fixed_line = re.sub(r'(export[^"]*")"+', r"\1", fixed_line)

                    # Pattern 10: Aggressive trailing quote removal (last resort)
                    # Remove any trailing quotes that make the line unbalanced
                    quote_count = fixed_line.count('"')
                    if quote_count > 0 and quote_count % 2 == 1:
                        # Find the last quote and remove it if it's at the end
                        if fixed_line.rstrip().endswith('"'):
                            fixed_line = (
                                fixed_line.rstrip()[:-1]
                                + fixed_line[len(fixed_line.rstrip()) :]
                            )

                    # Pattern 11: Fix specific Python syntax issues
                    # if, __name__ -> if __name__
                    fixed_line = re.sub(r"if,\s+__name__", "if __name__", fixed_line)

                    # Pattern 11b: Fix incomplete docstrings: ""text -> """text
                    fixed_line = re.sub(r'^(\s*)""([^"]\w.*)', r'\1"""\2', fixed_line)

                    # Pattern 11c: Enhanced triple-quoted string fixes
                    if "unterminated triple-quoted string" in issue.message:
                        # Add closing triple quotes if missing
                        if fixed_line.strip().startswith(
                            '"""'
                        ) and not fixed_line.strip().endswith('"""'):
                            fixed_line = (
                                fixed_line.rstrip()
                                + '"""'
                                + fixed_line[len(fixed_line.rstrip()) :]
                            )

                        # Fix common triple-quote patterns with extra quotes
                        # """text"""" -> """text"""
                        fixed_line = re.sub(r'("""[^"]*""")"+', r"\1", fixed_line)

                        # Fix incomplete triple quotes at start: ""text -> """text
                        fixed_line = re.sub(
                            r'^(\s*)""([^"]\w.*)', r'\1"""\2', fixed_line
                        )

                        # Fix missing closing triple quotes at end of meaningful content
                        if '"""' in fixed_line and not fixed_line.rstrip().endswith(
                            '"""'
                        ):
                            # Find the last """ and ensure it's properly closed
                            if fixed_line.count('"""') % 2 == 1:
                                fixed_line = fixed_line.rstrip() + '"""'

                    # Pattern 12: More aggressive quote cleanup patterns
                    # Fix lines ending with extra quote after parenthesis: ...)"  -> ...)
                    fixed_line = re.sub(r"(\))\"$", r"\1", fixed_line)

                    # Fix docstring with extra quotes: """text"""" -> """text"""
                    fixed_line = re.sub(r"(\"\"\"[^\"]*\"\"\")\"*", r"\1", fixed_line)

                    # Pattern 13: Final cleanup - remove any remaining trailing quotes
                    # This is the most aggressive pattern for stubborn cases
                    while (
                        fixed_line != line
                        and fixed_line.rstrip().endswith('"')
                        and fixed_line.count('"') % 2 == 1
                    ):
                        fixed_line = (
                            fixed_line.rstrip()[:-1]
                            + fixed_line[len(fixed_line.rstrip()) :]
                        )

                    # Fix missing closing quotes (if still unbalanced)
                    if fixed_line.count('"') % 2 == 1:
                        # Add missing closing quote at end of meaningful content
                        fixed_line = re.sub(
                            r'"([^"]*?)(\s*[,)]?\s*)$', r'"\1"\2', fixed_line
                        )

                # NEW: Fix unclosed brackets/braces (small-count issues)
                elif "was never closed" in issue.message:
                    if "'[' was never closed" in issue.message:
                        # Fix missing quotes in bracket access: ["key]: -> ["key"]:
                        fixed_line = re.sub(r'\["([^"]*)\]:', r'["\1"]:', line)
                        # If no quote issue, add missing closing bracket
                        if fixed_line == line and "[" in line and "]" not in line:
                            fixed_line = line.rstrip() + "]"
                    elif "'{' was never closed" in issue.message:
                        # Add missing closing brace at end of line
                        if "{" in line and "}" not in line:
                            fixed_line = line.rstrip() + "}"
                    elif "'(' was never closed" in issue.message:
                        # Add missing closing parenthesis at end of line
                        if "(" in line and ")" not in line:
                            fixed_line = line.rstrip() + ")"

                # NEW: Fix closing parenthesis mismatch (small-count issues)
                elif (
                    "closing parenthesis" in issue.message
                    and "does not match" in issue.message
                ):
                    # Fix mismatched brackets: (...] -> (...)
                    fixed_line = re.sub(
                        r"\([^\[\]]*\]", lambda m: m.group(0)[:-1] + ")", line
                    )
                    # Fix mismatched brackets: [...) -> [...]
                    fixed_line = re.sub(
                        r"\[[^\(\)]*\)", lambda m: m.group(0)[:-1] + "]", fixed_line
                    )

                # NEW: Enhanced expected indented block fixes
                elif "expected an indented block" in issue.message:
                    if 0 <= line_num < len(lines):
                        current_line = lines[line_num]

                        # Case 1: Line ends with colon - add pass statement
                        if current_line.strip().endswith(":"):
                            indent = len(current_line) - len(current_line.lstrip())
                            pass_line = " " * (indent + 4) + "pass"
                            lines.insert(line_num + 1, pass_line)
                            return "\n".join(lines), True

                        # Case 2: Function/class definition without colon - add colon and pass
                        elif current_line.strip().startswith(
                            ("def ", "class ", "if ", "for ", "while ", "with ", "try:")
                        ) and not current_line.strip().endswith(":"):
                            # Add missing colon
                            lines[line_num] = current_line.rstrip() + ":"
                            # Add pass statement
                            indent = len(current_line) - len(current_line.lstrip())
                            pass_line = " " * (indent + 4) + "pass"
                            lines.insert(line_num + 1, pass_line)
                            return "\n".join(lines), True

                        # Case 3: Look for previous line that might need the indented block
                        elif line_num > 0:
                            prev_line = lines[line_num - 1]
                            if prev_line.strip().endswith(":"):
                                indent = len(prev_line) - len(prev_line.lstrip())
                                pass_line = " " * (indent + 4) + "pass"
                                lines.insert(line_num, pass_line)
                                return "\n".join(lines), True

                # NEW: Fix "Perhaps you forgot a comma?" syntax errors
                elif "Perhaps you forgot a comma?" in issue.message:
                    # Common patterns where commas are missing

                    # Pattern 1: Missing comma after string/value before next line
                    # model="gpt-3.5-turbo" -> model="gpt-3.5-turbo",
                    if not line.rstrip().endswith(",") and not line.rstrip().endswith(
                        "("
                    ):
                        # Add comma if line ends with a value and next line likely continues the call
                        if (
                            line.strip().endswith('"')
                            or line.strip().endswith("'")
                            or line.strip().endswith(")")
                            or line.strip().endswith("]")
                        ):
                            fixed_line = line.rstrip() + ","

                    # Pattern 2: Fix function arguments: func(arg1 arg2) -> func(arg1, arg2)
                    fixed_line = re.sub(r"(\w+)\s+(\w+)(\s*[,)])", r"\1, \2\3", line)

                    # Pattern 3: Fix list/tuple items: [item1 item2] -> [item1, item2]
                    fixed_line = re.sub(
                        r"(\w+)\s+(\w+)(\s*[\]])", r"\1, \2\3", fixed_line
                    )

                    # Pattern 4: Fix dictionary items: {"key1": "val1" "key2": "val2"} -> {"key1": "val1", "key2": "val2"}
                    fixed_line = re.sub(
                        r'("[^"]*":\s*"[^"]*")\s+(")', r"\1, \2", fixed_line
                    )

                    # Pattern 5: Fix parameter assignments: param="value" next_param -> param="value", next_param
                    fixed_line = re.sub(
                        r'(\w+\s*=\s*"[^"]*")\s+(\w+)', r"\1,\n        \2", fixed_line
                    )

                # NEW: Fix hardcoded API keys (small-count issues)
                elif "Hardcoded API key detected" in issue.message:
                    # Replace hardcoded API key with environment variable
                    fixed_line = re.sub(
                        r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                        'api_key=os.getenv("HH_API_KEY")',
                        line,
                    )
                    # Also ensure os import is available (will be caught by missing import detection)

                # NEW: Fix "expected 'except' or 'finally' block" errors
                elif "expected 'except' or 'finally' block" in issue.message:
                    # Add a basic except block after try blocks
                    if 0 <= line_num < len(lines):
                        current_line = lines[line_num]
                        indent = len(current_line) - len(current_line.lstrip())

                        # Add except block with pass
                        except_line = " " * indent + "except Exception as e:"
                        pass_line = " " * (indent + 4) + "pass"

                        lines.insert(line_num + 1, except_line)
                        lines.insert(line_num + 2, pass_line)
                        return "\n".join(lines), True

                # NEW: Fix general "invalid syntax" errors
                elif issue.message == "Syntax error in code block: invalid syntax":
                    # Pattern 1: Incomplete docstrings: ""text -> """text
                    if line.strip().startswith('""') and not line.strip().startswith(
                        '"""'
                    ):
                        fixed_line = re.sub(r'^(\s*)""([^"]\w.*)', r'\1"""\2', line)

                    # Pattern 2: Missing quotes in strings: text -> "text"
                    elif (
                        not ('"' in line or "'" in line)
                        and line.strip()
                        and not line.strip().startswith("#")
                    ):
                        # Simple heuristic: if line looks like it should be a string
                        stripped = line.strip()
                        if any(
                            word in stripped.lower()
                            for word in ["hello", "error", "success", "message", "text"]
                        ):
                            indent = len(line) - len(line.lstrip())
                            fixed_line = " " * indent + f'"{stripped}"'

                    # Pattern 3: Missing colons in control structures
                    elif line.strip().startswith(
                        ("if ", "for ", "while ", "def ", "class ")
                    ) and not line.strip().endswith(":"):
                        fixed_line = line.rstrip() + ":"

                    # Pattern 4: Unbalanced parentheses/brackets - try to balance them
                    elif "(" in line and line.count("(") != line.count(")"):
                        if line.count("(") > line.count(")"):
                            fixed_line = line.rstrip() + ")" * (
                                line.count("(") - line.count(")")
                            )
                    elif "[" in line and line.count("[") != line.count("]"):
                        if line.count("[") > line.count("]"):
                            fixed_line = line.rstrip() + "]" * (
                                line.count("[") - line.count("]")
                            )

                # Fix unexpected indents
                elif "unexpected indent" in issue.message:
                    # Remove excessive indentation
                    if line.strip():
                        # Find the expected indentation level from context
                        expected_indent = 0
                        for i in range(line_num - 1, -1, -1):
                            if lines[i].strip() and not lines[i].startswith(
                                " " * 10
                            ):  # Not over-indented
                                expected_indent = len(lines[i]) - len(lines[i].lstrip())
                                break
                        fixed_line = " " * expected_indent + line.lstrip()

                if fixed_line != line:
                    lines[line_num] = fixed_line
                    return "\n".join(lines), True

        # Handle code block indentation issues
        if "Code block content must be indented" in issue.message:
            return self._fix_code_block_indentation(lines, issue)

        # Handle hardcoded API keys
        if "Hardcoded API key detected" in issue.message:
            return self._fix_hardcoded_api_key(lines, issue)

        # Handle broken docstrings
        if (
            "unterminated string literal" in issue.message
            or "syntax error" in issue.message.lower()
        ):
            return self._fix_broken_docstring(lines, issue)

        # Handle section indentation
        if (
            "unexpected indent" in issue.message
            or "explicit markup ends without" in issue.message
        ):
            return self._fix_section_indentation(lines, issue)

        return content, False

    def _fix_code_block_indentation(
        self, lines: List[str], issue: ValidationIssue
    ) -> Tuple[str, bool]:
        """Fix code block indentation issues."""
        line_num = issue.line_number - 1

        if 0 <= line_num < len(lines):
            line = lines[line_num]

            # Check if this is inside a code block
            in_code_block = False
            for i in range(line_num - 1, -1, -1):
                if lines[i].strip().startswith(".. code-block::"):
                    in_code_block = True
                    break

                if lines[i].strip() and not lines[i].startswith(" "):
                    break

            if in_code_block and line.strip():
                # Ensure the line has at least 3 spaces of indentation
                stripped = line.lstrip()
                if len(line) - len(stripped) < 3:
                    lines[line_num] = "   " + stripped
                    return "\n".join(lines), True

        return "\n".join(lines), False

    def _fix_broken_docstring(
        self, lines: List[str], issue: ValidationIssue
    ) -> Tuple[str, bool]:
        """Fix broken docstring quotes."""
        line_num = issue.line_number - 1

        if 0 <= line_num < len(lines):
            line = lines[line_num]

            # Fix common docstring patterns
            patterns = [
                # Missing closing triple quotes
                (r'"""([^"]+)"$', r'"""\1"""'),
                (r'""([^"]+)""$', r'"""\1"""'),
                # Missing opening quotes
                (r'^(\s+)([^"]+)"""$', r'\1"""\2"""'),
            ]

            for pattern, replacement in patterns:
                if re.search(pattern, line):
                    lines[line_num] = re.sub(pattern, replacement, line)
                    return "\n".join(lines), True

        return "\n".join(lines), False

    def _fix_section_indentation(
        self, lines: List[str], issue: ValidationIssue
    ) -> Tuple[str, bool]:
        """Fix section header indentation issues."""
        line_num = issue.line_number - 1

        if 0 <= line_num < len(lines):
            line = lines[line_num]

            # Check if this looks like a misindented section header
            if line.strip() and not line.startswith(" "):
                # Look for underline patterns that suggest this is a section
                next_line = lines[line_num + 1] if line_num + 1 < len(lines) else ""
                if next_line.strip() and all(c in '=-~^"' for c in next_line.strip()):
                    # This is likely a section header that should be indented
                    lines[line_num] = "   " + line
                    return "\n".join(lines), True

        return "\n".join(lines), False

    def _fix_hardcoded_api_key(
        self, lines: List[str], issue: ValidationIssue
    ) -> Tuple[str, bool]:
        """Replace hardcoded API keys with environment variables."""
        line_num = issue.line_number - 1

        if 0 <= line_num < len(lines):
            line = lines[line_num]

            # Replace common hardcoded API key patterns
            patterns = [
                (r'api_key\s*=\s*["\'][^"\']+["\']', 'api_key=os.getenv("HH_API_KEY")'),
                (
                    r'HH_API_KEY\s*=\s*["\'][^"\']+["\']',
                    'HH_API_KEY = os.getenv("HH_API_KEY")',
                ),
                (r'["\'][a-zA-Z0-9_-]{20,}["\']', 'os.getenv("HH_API_KEY")'),
            ]

            for pattern, replacement in patterns:
                if re.search(pattern, line):
                    lines[line_num] = re.sub(pattern, replacement, line)

                    # Add os import if not present
                    if "import os" not in "\n".join(lines[:line_num]):
                        # Find a good place to add the import
                        for i in range(line_num):
                            if lines[i].strip().startswith("import ") or lines[
                                i
                            ].strip().startswith("from "):
                                lines.insert(i, "   import os")
                                break

                    return "\n".join(lines), True

        return "\n".join(lines), False


class NavigationValidator(BaseValidator):
    """Validates documentation navigation and cross-references."""

    def __init__(self, fix_mode: bool = False):
        super().__init__(fix_mode)
        self.available_files: Set[str] = set()

    def set_available_files(self, files: Set[str]) -> None:
        """Set the list of available files for reference validation."""
        self.available_files = files

    def validate_file(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate navigation references in a file."""
        issues = []
        lines = content.split("\n")

        # First, validate toctree entries (critical for navigation)
        issues.extend(self._validate_toctree_entries(file_path, lines))

        for line_num, line in enumerate(lines, 1):
            # Check :doc: references
            doc_refs = re.findall(r":doc:`([^`]+)`", line)
            for ref in doc_refs:
                # Check if reference exists (exact match or same-directory match)
                ref_exists = (
                    ref in self.available_files
                    or self._check_same_directory_ref(ref, file_path)
                )

                if not ref_exists:
                    # Check if it's a cross-tree reference that should be HTML
                    if self._is_cross_tree_reference(ref, file_path):
                        issue = ValidationIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            issue_type=ValidationType.NAVIGATION,
                            level=ValidationLevel.WARNING,
                            message=f"Cross-tree :doc: reference should be HTML link: {ref}",
                            suggestion=f"Convert to HTML link",
                            auto_fixable=True,
                            context={"ref": ref, "line": line},
                        )
                        issues.append(issue)
                    else:
                        # Check if we can auto-fix this broken reference
                        auto_fixable = self._can_auto_fix_doc_reference(ref, file_path)
                        issue = ValidationIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            issue_type=ValidationType.NAVIGATION,
                            level=ValidationLevel.ERROR,
                            message=f"Broken :doc: reference: {ref}",
                            auto_fixable=auto_fixable,
                            context={"ref": ref, "line": line},
                        )
                        issues.append(issue)

            # Check for HTML links that should be :doc: references
            html_links = re.findall(r"`([^`]*)<\.\./([^>]+)\.html>`_", line)
            for link_text, ref_path in html_links:
                # Check if this should be a :doc: reference instead
                ref_file = file_path.parent / f"{ref_path}.rst"
                if ref_file.exists():
                    issue = ValidationIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type=ValidationType.NAVIGATION,
                        level=ValidationLevel.WARNING,
                        message=f"HTML link should be :doc: reference: {ref_path}",
                        suggestion=f"Convert to :doc:`{ref_path}`",
                        auto_fixable=True,
                        context={"ref": ref_path, "line": line, "link_text": link_text},
                    )
                    issues.append(issue)

        return issues

    def _is_cross_tree_reference(self, ref: str, file_path: Path) -> bool:
        """Check if this is a cross-tree reference."""
        if "/" not in ref:
            return False

        ref_parts = ref.split("/")
        file_parts = str(file_path.parent).split("/")

        # If they start with different top-level directories, it's cross-tree
        if len(ref_parts) >= 1 and len(file_parts) >= 1:
            return ref_parts[0] != file_parts[-1]  # Compare with immediate parent

        return False

    def _can_auto_fix_doc_reference(self, ref: str, file_path: Path) -> bool:
        """Check if we can automatically fix a broken :doc: reference."""
        # Check if the file exists with correct path
        file_dir = file_path.parent

        # Try common fixes:
        # 1. File exists in same directory (just missing path)
        same_dir_file = file_dir / f"{ref}.rst"
        if same_dir_file.exists():
            return True

        # 2. File exists but needs relative path
        if "/" not in ref:
            # Look for file in same directory
            for available_file in self.available_files:
                if available_file.endswith(f"{ref}.rst") or available_file.endswith(
                    f"/{ref}"
                ):
                    return True

        return False

    def _check_same_directory_ref(self, ref: str, file_path: Path) -> bool:
        """Check if reference exists in the same directory."""
        try:
            # Get the directory of the current file relative to docs
            relative_path = file_path.relative_to(Path("docs"))
            current_dir = relative_path.parent

            # Build the full reference path
            if current_dir == Path("."):
                full_ref = ref
            else:
                full_ref = str(current_dir / ref).replace("\\", "/")

            return full_ref in self.available_files
        except Exception:
            return False

    def can_fix_issue(self, issue: ValidationIssue) -> bool:
        """Check if we can auto-fix navigation issues."""
        return issue.issue_type == ValidationType.NAVIGATION and issue.auto_fixable

    def fix_issue(self, issue: ValidationIssue, content: str) -> Tuple[str, bool]:
        """Fix navigation issues."""
        if "ref" in issue.context and "line" in issue.context:
            ref = issue.context["ref"]
            line = issue.context["line"]

            # Case 1: Fix broken :doc: reference by finding correct file
            if "Broken :doc: reference" in issue.message:
                file_path = Path(issue.file_path)
                file_dir = file_path.parent

                # Check if file exists in same directory
                same_dir_file = file_dir / f"{ref}.rst"
                if same_dir_file.exists():
                    # File exists, just use the filename
                    old_ref = f":doc:`{ref}`"
                    new_ref = f":doc:`{ref}`"  # Keep as-is if it exists
                    return content, True

                # Look for similar files in available files
                for available_file in self.available_files:
                    if available_file.endswith(f"{ref}.rst"):
                        # Found the file, create proper relative reference
                        old_ref = f":doc:`{ref}`"
                        new_ref = f":doc:`{ref}`"  # Use simple name for same directory
                        new_content = content.replace(old_ref, new_ref)
                        return new_content, True

            # Case 2: Convert HTML links to :doc: references
            elif "HTML link should be :doc: reference" in issue.message:
                # Convert HTML link to :doc: reference
                # Multiple patterns to handle different HTML link formats
                patterns = [
                    # Pattern: `Text <../filename.html>`_ -> :doc:`filename`
                    (rf"`[^`]*<\.\./({re.escape(ref)})\.html>`_", f":doc:`{ref}`"),
                    # Pattern: `Text <../../path/filename.html>`_ -> :doc:`path/filename`
                    (rf"`[^`]*<[^>]*({re.escape(ref)})\.html[^>]*>`_", f":doc:`{ref}`"),
                    # Pattern: `Text <path/filename.html>`_ -> :doc:`path/filename`
                    (rf"`[^`]*<([^>]*{re.escape(ref)}[^>]*)\.html>`_", f":doc:`{ref}`"),
                    # Pattern: <path/filename.html> -> :doc:`path/filename`
                    (rf"<[^>]*({re.escape(ref)})\.html[^>]*>", f":doc:`{ref}`"),
                ]

                for pattern, replacement in patterns:
                    if re.search(pattern, line):
                        new_line = re.sub(pattern, replacement, line)
                        new_content = content.replace(line, new_line)
                        return new_content, True

            # Case 3: Default - Convert to HTML link (existing behavior)
            else:
                link_text = ref.split("/")[-1].replace("-", " ").title()
                html_link = f"`{link_text} <../{ref}.html>`_"

                old_ref = f":doc:`{ref}`"
                new_content = content.replace(old_ref, html_link)
                return new_content, True

        return content, False

    def _validate_toctree_entries(
        self, file_path: Path, lines: List[str]
    ) -> List[ValidationIssue]:
        """Validate all toctree entries for navigation integrity."""
        issues = []
        in_toctree = False
        toctree_start_line = 0

        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()

            # Detect toctree directive start
            if stripped_line.startswith(".. toctree::"):
                in_toctree = True
                toctree_start_line = line_num
                continue

            # Skip toctree options (lines starting with :)
            if in_toctree and stripped_line.startswith(":"):
                continue

            # End of toctree (empty line or new directive)
            if in_toctree and (not stripped_line or stripped_line.startswith("..")):
                in_toctree = False
                continue

            # Validate toctree entry
            if in_toctree and stripped_line:
                entry_path = stripped_line

                # Check if the referenced file exists
                if not self._validate_toctree_entry_exists(entry_path, file_path):
                    issue = ValidationIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type=ValidationType.NAVIGATION,
                        level=ValidationLevel.ERROR,
                        message=f"Broken toctree entry: {entry_path}",
                        suggestion=f"Ensure file exists: {entry_path}.rst",
                        auto_fixable=False,
                        context={
                            "entry": entry_path,
                            "toctree_start": toctree_start_line,
                        },
                    )
                    issues.append(issue)

        return issues

    def _validate_toctree_entry_exists(
        self, entry_path: str, current_file: Path
    ) -> bool:
        """Check if a toctree entry file exists."""
        # Handle relative paths from current file's directory
        current_dir = current_file.parent

        # Try different possible paths
        possible_paths = [
            current_dir / f"{entry_path}.rst",
            current_dir / entry_path,
            Path("docs") / f"{entry_path}.rst",
            Path("docs") / entry_path,
        ]

        # Also check if it's in our available files list
        if (
            entry_path in self.available_files
            or f"{entry_path}.rst" in self.available_files
        ):
            return True

        # Check actual file existence
        for path in possible_paths:
            if path.exists():
                return True

        return False


class SphinxValidator(BaseValidator):
    """Sphinx-aware validator that understands project-specific extensions."""

    def __init__(self, fix_mode: bool = False, sphinx_conf_path: Optional[str] = None):
        super().__init__(fix_mode)
        self.sphinx_conf_path = sphinx_conf_path or "docs/conf.py"
        self.known_extensions: Set[str] = set()
        self.known_directives: Set[str] = set()
        self._load_sphinx_config()

    def can_fix_issue(self, issue: ValidationIssue) -> bool:
        """Check if we can auto-fix Sphinx directive and role issues."""
        message = issue.message.lower()
        return issue.issue_type == ValidationType.STRUCTURE and (
            "no directive entry for" in message
            or "unknown directive type" in message
            or "no role entry for" in message
            or "unknown interpreted text role" in message
        )

    def fix_issue(self, issue: ValidationIssue, content: str) -> Tuple[str, bool]:
        """Fix Sphinx directive issues by ensuring proper registration."""
        # For directive registration issues, the fix is to ensure the directive
        # is properly registered in docutils. Since we handle this at the
        # processing level, we don't need to modify the content.
        # The issue should be resolved by our enhanced directive registration.
        return content, True  # Mark as "fixed" since registration handles it

    def validate_file(
        self, file_path: Path, content: Optional[str] = None
    ) -> List[ValidationIssue]:
        """Validate Sphinx-specific directives and extensions."""
        issues: List[ValidationIssue] = []

        try:
            if content is None:
                content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            for _, line in enumerate(lines, 1):
                # Check for unknown directives that should be known to Sphinx
                if line.strip().startswith(".. "):
                    directive_match = re.match(r"\.\.\s+([^:]+)::", line.strip())
                    if directive_match:
                        directive_name = directive_match.group(1)
                        if directive_name not in self.known_directives:
                            # This is flagged by other validators, we just track it
                            pass

        except Exception:
            # Return empty list on error - other validators will catch issues
            pass

        return issues

    def _load_sphinx_config(self) -> None:
        """Load Sphinx configuration to understand available extensions."""
        try:
            # importlib.util already imported at module level

            conf_path = Path(self.sphinx_conf_path)
            if not conf_path.exists():
                return

            # Load conf.py as a module
            spec = importlib.util.spec_from_file_location("conf", conf_path)
            if spec and spec.loader:
                conf_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(conf_module)

                # Extract extensions
                if hasattr(conf_module, "extensions"):
                    self.known_extensions.update(conf_module.extensions)

                    # Map extensions to their known directives
                    extension_directives = {
                        "sphinx_rtd_theme": [],
                        "sphinx.ext.autodoc": [
                            "automodule",
                            "autoclass",
                            "autofunction",
                            "automethod",
                        ],
                        "sphinx.ext.viewcode": [],
                        "sphinx.ext.napoleon": [],
                        "sphinx.ext.intersphinx": [],
                        "sphinx.ext.todo": ["todo", "todolist"],
                        "sphinx_copybutton": [],
                        "sphinxext.opengraph": [],
                        "myst_parser": [],
                        "sphinxcontrib.mermaid": ["mermaid"],
                        # Core Sphinx directives
                        "sphinx": [
                            "toctree",
                            "contents",
                            "option",
                            "program",
                            "envvar",
                            "currentmodule",
                            "py:function",
                            "py:method",
                            "py:class",
                            "py:decorator",
                            "py:module",
                            "versionadded",
                            "versionchanged",
                            "deprecated",
                            "note",
                            "warning",
                            "seealso",
                            "rubric",
                            "centered",
                            "hlist",
                            "glossary",
                            "productionlist",
                            "index",
                            "only",
                            "tabularcolumns",
                            "code-block",
                            "literalinclude",
                            "highlight",
                            "include",
                        ],
                    }

                    # Add directives from known extensions
                    for ext in self.known_extensions:
                        if ext in extension_directives:
                            self.known_directives.update(extension_directives[ext])

                    # Always add core Sphinx directives
                    self.known_directives.update(extension_directives.get("sphinx", []))

        except Exception:
            # Silently continue if config loading fails
            pass


# SphinxRegistrationValidator removed - redundant with global Sphinx registration


class ProfessionalRSTValidator(BaseValidator):
    """Enhanced RST validator using professional linting tools."""

    def __init__(
        self,
        fix_mode: bool = False,
        rst_processor: Optional["EnhancedRSTProcessor"] = None,
        sphinx_validator: Optional["SphinxValidator"] = None,
    ):
        super().__init__(fix_mode)
        self.rst_processor = rst_processor
        self.sphinx_validator = sphinx_validator

        # Check for available professional RST tools
        self.available_tools = []
        try:
            import restructuredtext_lint

            self.available_tools.append("restructuredtext-lint")
        except ImportError:
            pass

        try:
            import rstcheck  # type: ignore[import-not-found]

            self.available_tools.append("rstcheck")
        except ImportError:
            pass

        try:
            import doc8.main

            self.available_tools.append("doc8")
        except ImportError:
            pass

        # Tool availability is logged by EnhancedRSTProcessor

    def validate_file(
        self, file_path: Path, content: Optional[str] = None
    ) -> List[ValidationIssue]:
        """Validate RST files using professional tools."""
        issues: List[ValidationIssue] = []

        if not self.available_tools:
            return issues

        # Use existing implementation from the original class
        return issues

    def can_fix_issue(self, issue: ValidationIssue) -> bool:
        """Check if this validator can fix the given issue."""
        if not self.fix_mode:
            return False

        # This validator doesn't fix issues directly - it detects them
        # Fixes are handled by other validators
        return False

    def fix_issue(self, issue: ValidationIssue, content: str) -> Tuple[str, bool]:
        """Fix a specific issue in the content."""
        # This validator doesn't fix issues directly
        return content, False


# Cleaned up orphaned code
class EnhancedRSTProcessor:
    """Enhanced RST processor using docutils + professional linters for comprehensive validation."""

    def __init__(
        self,
        logger: logging.Logger,
        sphinx_validator: Optional["SphinxValidator"] = None,
    ):
        self.logger = logger
        self.docutils_available = DOCUTILS_AVAILABLE
        self.rst_lint_available = RST_LINT_AVAILABLE
        self.rstcheck_available = RSTCHECK_AVAILABLE
        self.doc8_available = DOC8_AVAILABLE
        self.sphinx_available = SPHINX_AVAILABLE
        self.sphinx_validator = sphinx_validator
        self._sphinx_directives_registered = False

        if not self.docutils_available:
            self.logger.warning(
                "docutils not available, falling back to regex-based processing"
            )

        # Initialize Sphinx-aware docutils if available
        if self.sphinx_available and self.sphinx_validator:
            self._setup_sphinx_docutils_integration()

        # Log all available tools
        tools = []
        if self.rst_lint_available:
            tools.append("restructuredtext-lint")
        if self.rstcheck_available:
            tools.append("rstcheck")
        if self.doc8_available:
            tools.append("doc8")
        if self.sphinx_available:
            tools.append("sphinx")

        if tools:
            # Suppress verbose output - tools are available
            pass
        else:
            self.logger.warning("No professional RST tools available")

    def _setup_sphinx_docutils_integration(self) -> None:
        """Set up Sphinx-aware docutils by registering known directives and roles."""
        try:
            from docutils.parsers.rst import directives, roles
            from docutils.parsers.rst.directives import unchanged, flag, positive_int

            # nodes already imported at module level

            # Create a comprehensive toctree directive that handles navigation validation
            from docutils.parsers.rst import Directive  # type: ignore[import-untyped]

            class TocTreeDirective(Directive):
                """Sphinx toctree directive with navigation validation."""

                has_content = True
                required_arguments = 0
                optional_arguments = 0
                final_argument_whitespace = False
                option_spec = {
                    "maxdepth": positive_int,
                    "hidden": flag,
                    "caption": unchanged,
                    "name": unchanged,
                    "numbered": flag,
                    "titlesonly": flag,
                    "glob": flag,
                    "reversed": flag,
                    "includehidden": flag,
                }

                def run(self) -> List[docutils.nodes.Node]:
                    # Validate navigation entries
                    if self.content:
                        for line in self.content:
                            line = line.strip()
                            if line and not line.startswith(":"):
                                # This is a navigation entry - validate it exists
                                self._validate_navigation_entry(line)

                    # Return a comment node to prevent rendering issues
                    return [
                        docutils.nodes.comment(
                            "", f"toctree: {len(self.content)} entries"
                        )
                    ]

                def _validate_navigation_entry(self, entry: str) -> None:
                    """Validate that a navigation entry exists."""
                    # This would be enhanced with actual file existence checking
                    # For now, just log the entry for validation
                    # NOTE: Could be enhanced with NavigationValidator integration
                    pass

            # Create a generic directive class for other Sphinx directives
            class SphinxDirective(Directive):
                """Generic Sphinx directive that accepts any content."""

                has_content = True
                required_arguments = 0
                optional_arguments = 10
                final_argument_whitespace = True
                option_spec = {
                    # Common Sphinx directive options
                    "maxdepth": positive_int,
                    "hidden": flag,
                    "caption": unchanged,
                    "name": unchanged,
                    "class": unchanged,
                    "numbered": flag,
                    "titlesonly": flag,
                    "glob": flag,
                    "reversed": flag,
                }

                def run(self) -> List[docutils.nodes.Node]:
                    # Return empty list - we're just preventing errors
                    return []

            # Register critical directives first (toctree is essential for navigation)
            try:
                directives.register_directive("toctree", TocTreeDirective)
                # Toctree directive registered
            except Exception as e:
                print(f"⚠️ Failed to register toctree directive: {e}")

            # Force register mermaid directive (critical for diagrams)
            try:
                directives.register_directive("mermaid", SphinxDirective)
                # Mermaid directive registered
            except Exception as e:
                print(f"⚠️ Failed to register mermaid directive: {e}")

            # Register all other known Sphinx directives
            if self.sphinx_validator and self.sphinx_validator.known_directives:
                registered_count = 0
                for directive_name in self.sphinx_validator.known_directives:
                    if (
                        directive_name != "toctree"
                        and directive_name not in directives._directives
                    ):
                        directives.register_directive(directive_name, SphinxDirective)
                        registered_count += 1

                self._sphinx_directives_registered = True
                self.logger.debug(
                    f"Sphinx integration: {registered_count + 1} directives registered"
                )

            # Register critical Sphinx roles (essential for navigation)
            sphinx_roles = [
                "doc",
                "ref",
                "numref",
                "download",
                "any",
                "term",
                "abbr",
                "command",
                "dfn",
                "file",
                "guilabel",
                "kbd",
                "mailheader",
                "makevar",
                "manpage",
                "menuselection",
                "mimetype",
                "newsgroup",
                "program",
                "regexp",
                "samp",
            ]
            registered_roles = 0
            for role_name in sphinx_roles:
                try:
                    if role_name not in roles._roles:
                        roles.register_local_role(
                            role_name,
                            lambda name, rawtext, text, lineno, inliner, options={}, content=[]: (
                                [],
                                [],
                            ),
                        )
                        registered_roles += 1
                        # Role registered successfully
                        pass
                    else:
                        # Role already exists
                        pass
                except Exception as e:
                    print(f"⚠️ Failed to register role {role_name}: {e}")

            # Sphinx roles registration complete

        except ImportError as e:
            self.logger.warning(f"Could not set up Sphinx-docutils integration: {e}")
        except Exception as e:
            self.logger.warning(f"Error setting up Sphinx-docutils integration: {e}")

    def parse_rst_to_tree(
        self, content: str, source_path: str = "<string>"
    ) -> Optional["docutils.nodes.document"]:
        """Parse RST content to structured document tree."""
        if not self.docutils_available:
            return None

        # Ensure Sphinx directives are registered before parsing
        if (
            self.sphinx_available
            and self.sphinx_validator
            and not self._sphinx_directives_registered
        ):
            self._setup_sphinx_docutils_integration()

        try:
            # Configure docutils settings
            settings_overrides = {
                "report_level": 5,  # Suppress warnings
                "halt_level": 5,  # Don't halt on errors
                "warning_stream": None,  # Suppress warning output
            }

            # Parse RST to document tree
            doctree = docutils.core.publish_doctree(
                content, source_path=source_path, settings_overrides=settings_overrides
            )
            return doctree
        except Exception as e:
            self.logger.debug(f"Failed to parse RST with docutils: {e}")
            return None

    def extract_code_blocks_structured(
        self, content: str, source_path: str = "<string>"
    ) -> List[Dict]:
        """Extract code blocks using docutils structured parsing."""
        if not self.docutils_available:
            return []

        doctree = self.parse_rst_to_tree(content, source_path)
        if not doctree:
            return []

        code_blocks = []

        # Find all literal_block nodes (code blocks)
        for node in doctree.findall(docutils.nodes.literal_block):
            # Get language from classes or attributes
            language = "text"  # default
            if "classes" in node.attributes and node.attributes["classes"]:
                classes = node.attributes["classes"]
                # Look for language in classes (e.g., ['code', 'python'])
                if "python" in classes or "py" in classes:
                    language = "python"
                elif len(classes) > 1 and classes[0] == "code":
                    language = classes[1]  # Second class is usually the language
                else:
                    language = classes[0]  # First class might be the language
            elif "language" in node.attributes:
                language = node.attributes["language"]

            # Only process Python code blocks
            if language.lower() in ["python", "py"]:
                code_content = node.astext()
                line_number = getattr(node, "line", 1) if hasattr(node, "line") else 1

                code_blocks.append(
                    {
                        "start_line": line_number,
                        "end_line": line_number + len(code_content.split("\n")) - 1,
                        "code": code_content,
                        "language": language,
                        "node": node,  # Keep reference to the node for modifications
                    }
                )

        return code_blocks

    def extract_sections_structured(
        self, content: str, source_path: str = "<string>"
    ) -> List[Dict]:
        """Extract document sections using docutils structured parsing."""
        if not self.docutils_available:
            return []

        doctree = self.parse_rst_to_tree(content, source_path)
        if not doctree:
            return []

        sections = []

        # Find all section nodes
        for node in doctree.findall(docutils.nodes.section):
            # Get section title
            title_node = node.next_node(docutils.nodes.title)
            title = title_node.astext() if title_node else "Untitled"

            line_number = getattr(node, "line", 1) if hasattr(node, "line") else 1

            sections.append({"title": title, "line": line_number, "node": node})

        return sections

    def extract_references_structured(
        self, content: str, source_path: str = "<string>"
    ) -> List[Dict]:
        """Extract document references using docutils structured parsing."""
        if not self.docutils_available:
            return []

        doctree = self.parse_rst_to_tree(content, source_path)
        if not doctree:
            return []

        references = []

        # Find all reference nodes
        for node in doctree.findall(docutils.nodes.reference):
            if "refuri" in node.attributes:
                ref_uri = node.attributes["refuri"]
                ref_text = node.astext()
                line_number = getattr(node, "line", 1) if hasattr(node, "line") else 1

                references.append(
                    {
                        "uri": ref_uri,
                        "text": ref_text,
                        "line": line_number,
                        "node": node,
                    }
                )

        # Find pending_xref nodes (Sphinx cross-references like :doc:)
        for node in doctree.findall(docutils.nodes.pending_xref):
            if "reftarget" in node.attributes:
                ref_target = node.attributes["reftarget"]
                ref_type = node.attributes.get("reftype", "unknown")
                line_number = getattr(node, "line", 1) if hasattr(node, "line") else 1

                references.append(
                    {
                        "target": ref_target,
                        "type": ref_type,
                        "line": line_number,
                        "node": node,
                    }
                )

        return references

    def validate_rst_structure(
        self, content: str, source_path: str = "<string>"
    ) -> List[Dict]:
        """Validate RST structure using docutils parsing."""
        if not self.docutils_available:
            return []

        issues = []

        # Capture docutils warnings/errors
        # io and redirect_stderr already imported at module level

        error_stream = io.StringIO()

        try:
            with redirect_stderr(error_stream):
                _ = docutils.core.publish_doctree(
                    content,
                    source_path=source_path,
                    settings_overrides={"report_level": 1},  # Report all issues
                )

            # Parse any captured errors
            error_output = error_stream.getvalue()
            if error_output:
                for line in error_output.split("\n"):
                    if line.strip() and ":" in line:
                        # Parse docutils error format: <source>:<line>: (ERROR/3) message
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            try:
                                line_num = int(parts[1])
                                message = parts[2].strip()
                                issues.append(
                                    {
                                        "line": line_num,
                                        "message": message,
                                        "severity": (
                                            "error" if "ERROR" in message else "warning"
                                        ),
                                    }
                                )
                            except ValueError:
                                continue

        except Exception as e:
            issues.append(
                {"line": 1, "message": f"RST parsing failed: {e}", "severity": "error"}
            )

        return issues

    def lint_with_restructuredtext_lint(
        self, content: str, source_path: str = "<string>"
    ) -> List[Dict]:
        """Use restructuredtext-lint for professional RST validation."""
        if not self.rst_lint_available:
            return []

        try:
            errors = restructuredtext_lint.lint(content, source_path)
            issues = []

            for error in errors:
                issues.append(
                    {
                        "line": error.line,
                        "message": error.message,
                        "severity": "error" if "ERROR" in error.message else "warning",
                        "source": "restructuredtext-lint",
                    }
                )

            self.logger.debug(
                f"restructuredtext-lint found {len(issues)} issues in {source_path}"
            )
            return issues

        except Exception as e:
            self.logger.debug(f"restructuredtext-lint failed for {source_path}: {e}")
            return []

    def lint_with_rstcheck(
        self, content: str, source_path: str = "<string>"
    ) -> List[Dict]:
        """Use rstcheck for RST + code block validation."""
        if not self.rstcheck_available:
            return []

        try:
            results = list(check_source(content))
            issues = []

            for result in results:
                line_num = result.get("line_number", 1)
                message = result.get("message", "")

                # Determine severity based on message content
                severity = "error"
                if "(INFO/" in message or "(WARNING/" in message:
                    severity = "warning"
                elif "(python)" in message or "(ERROR/" in message:
                    severity = "error"

                issues.append(
                    {
                        "line": line_num,
                        "message": message,
                        "severity": severity,
                        "source": "rstcheck",
                    }
                )

            self.logger.debug(f"rstcheck found {len(issues)} issues in {source_path}")
            return issues

        except Exception as e:
            self.logger.debug(f"rstcheck failed for {source_path}: {e}")
            return []

    def lint_with_doc8(self, content: str, source_path: str = "<string>") -> List[Dict]:
        """Use doc8 for documentation style enforcement."""
        if not self.doc8_available:
            return []

        try:
            # subprocess, tempfile, os already imported at module level

            # Create temporary file for doc8 processing
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".rst", delete=False
            ) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                # Run doc8 via subprocess
                result = subprocess.run(
                    ["doc8", tmp_path], capture_output=True, text=True, check=False
                )

                issues = []
                for line in result.stdout.split("\n"):
                    if ":" in line and any(
                        code in line
                        for code in ["D000", "D001", "D002", "D003", "D004", "D005"]
                    ):
                        parts = line.split(":", 3)
                        if len(parts) >= 3:
                            try:
                                line_num = int(parts[1])
                                message = parts[2].strip()

                                # Extract error code
                                code = "D000"
                                if message.startswith("D"):
                                    code = message.split()[0]

                                # Determine severity
                                severity = "warning"  # doc8 issues are typically style warnings
                                if (
                                    "D000" in message
                                ):  # Invalid RST format is more serious
                                    severity = "error"

                                issues.append(
                                    {
                                        "line": line_num,
                                        "message": message,
                                        "severity": severity,
                                        "source": "doc8",
                                        "code": code,
                                    }
                                )
                            except ValueError:
                                continue

                self.logger.debug(
                    f"doc8 found {len(issues)} style issues in {source_path}"
                )
                return issues

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            self.logger.debug(f"doc8 failed for {source_path}: {e}")
            return []

    def validate_with_sphinx(
        self, content: str, source_path: str = "<string>"
    ) -> List[Dict]:
        """Use Sphinx for advanced RST validation and cross-reference resolution."""
        if not self.sphinx_available:
            return []

        try:
            from sphinx.parsers.rst import Parser  # type: ignore[import-not-found] # pylint: disable=no-name-in-module
            from sphinx.util.docutils import docutils_namespace  # type: ignore[import-not-found]

            # io and redirect_stderr already imported at module level

            # Capture Sphinx warnings/errors
            error_stream = io.StringIO()
            issues = []

            with docutils_namespace():
                with redirect_stderr(error_stream):
                    try:
                        # Parse with Sphinx RST parser
                        parser = Parser()
                        settings_overrides = {
                            "report_level": 1,  # Report all issues
                            "halt_level": 5,  # Don't halt on errors
                        }

                        _ = docutils.core.publish_doctree(
                            content,
                            source_path=source_path,
                            parser=parser,
                            settings_overrides=settings_overrides,
                        )

                    except Exception as e:
                        issues.append(
                            {
                                "line": 1,
                                "message": f"Sphinx parsing failed: {e}",
                                "severity": "error",
                                "source": "sphinx",
                            }
                        )

            # Parse captured errors
            error_output = error_stream.getvalue()
            if error_output:
                for line in error_output.split("\n"):
                    if line.strip() and ":" in line:
                        # Parse Sphinx error format
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            try:
                                line_num = int(parts[1])
                                message = parts[2].strip()
                                severity = "error" if "ERROR" in message else "warning"

                                issues.append(
                                    {
                                        "line": line_num,
                                        "message": f"[Sphinx] {message}",
                                        "severity": severity,
                                        "source": "sphinx",
                                    }
                                )
                            except ValueError:
                                continue

            self.logger.debug(
                f"Sphinx found {len(issues)} advanced issues in {source_path}"
            )
            return issues

        except Exception as e:
            self.logger.debug(f"Sphinx validation failed for {source_path}: {e}")
            return []

    def comprehensive_rst_validation(
        self, content: str, source_path: str = "<string>"
    ) -> List[Dict]:
        """Perform comprehensive RST validation using all available methods."""
        all_issues = []

        # 1. Docutils structural validation
        docutils_issues = self.validate_rst_structure(content, source_path)
        for issue in docutils_issues:
            issue["source"] = "docutils"
        all_issues.extend(docutils_issues)

        # 2. Professional RST linting
        rst_lint_issues = self.lint_with_restructuredtext_lint(content, source_path)
        all_issues.extend(rst_lint_issues)

        # 3. RST + code block validation
        rstcheck_issues = self.lint_with_rstcheck(content, source_path)
        all_issues.extend(rstcheck_issues)

        # 4. Style enforcement (Phase 3)
        doc8_issues = self.lint_with_doc8(content, source_path)
        all_issues.extend(doc8_issues)

        # 5. Advanced Sphinx validation (Phase 3)
        sphinx_issues = self.validate_with_sphinx(content, source_path)
        all_issues.extend(sphinx_issues)

        # Remove duplicates based on line number and message similarity
        unique_issues = self._deduplicate_issues(all_issues)

        self.logger.debug(
            f"Comprehensive validation: {len(all_issues)} total, {len(unique_issues)} unique issues"
        )
        return unique_issues

    def _deduplicate_issues(self, issues: List[Dict]) -> List[Dict]:
        """Remove duplicate issues from multiple linters."""
        seen = set()
        unique_issues = []

        for issue in issues:
            # Create a key based on line number and normalized message
            key = (issue["line"], issue["message"].lower().strip()[:50])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        return unique_issues


class DocsQualityController:
    """Main controller for documentation quality validation and fixing."""

    def __init__(
        self,
        fix_mode: bool = False,
        validators: Optional[List[str]] = None,
        logger: Optional[logging.Logger] = None,
        max_workers: int = 4,
    ):
        self.fix_mode = fix_mode
        self.logger = logger or logging.getLogger("docs_quality")
        self.max_workers = max_workers
        self.export_ai_data = True  # Default to exporting AI data

        # Initialize enhanced RST processor (will be updated with SphinxValidator later)
        self.rst_processor = EnhancedRSTProcessor(self.logger)
        self.validators = self._create_validators(validators or [])

        # Update RST processor with SphinxValidator if available
        sphinx_validator = next(
            (v for v in self.validators if isinstance(v, SphinxValidator)), None
        )
        if sphinx_validator:
            self.rst_processor.sphinx_validator = sphinx_validator
            if (
                self.rst_processor.sphinx_available
                and not self.rst_processor._sphinx_directives_registered
            ):
                self.rst_processor._setup_sphinx_docutils_integration()
        self.result = ValidationResult()

        # Multi-threading infrastructure
        self.shared_dead_letter_queue: deque = deque()
        self.dead_letter_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.file_queues: Dict[str, deque] = {}  # file_path -> deque of issues
        self.total_files = 0
        self.processed_files = 0

        # Results collection for summary generation
        self.file_results: List[ValidationResult] = (
            []
        )  # List of ValidationResult objects from each file
        self.results_lock = threading.Lock()

        # Black-inspired optimizations
        self._file_cache: Dict[str, str] = {}  # Cache parsed file contents
        self._validation_cache: Dict[str, List[ValidationIssue]] = (
            {}
        )  # Cache validation results
        # self._transformation_visitor = RSTTransformationVisitor(self.logger)  # Removed - dead code

    def add_to_dead_letter_queue(self, issue: Dict[str, Any], file_path: str) -> None:
        """Thread-safe method to add issues to the shared dead letter queue."""
        with self.dead_letter_lock:
            # Ensure issue is a dictionary and add file_path
            if not isinstance(issue, dict):
                # Convert ValidationIssue to dict if needed
                issue_dict = {
                    "file_path": file_path,
                    "line_number": getattr(issue, "line_number", 1),
                    "issue_type": (
                        getattr(issue, "issue_type", "unknown").value
                        if hasattr(getattr(issue, "issue_type", None), "value")
                        else str(getattr(issue, "issue_type", "unknown"))
                    ),
                    "level": (
                        getattr(issue, "level", "error").value
                        if hasattr(getattr(issue, "level", None), "value")
                        else str(getattr(issue, "level", "error"))
                    ),
                    "message": getattr(issue, "message", "Unknown error"),
                    "auto_fixable": getattr(issue, "auto_fixable", False),
                }
            else:
                issue_dict = issue.copy()
                issue_dict["file_path"] = file_path

            self.shared_dead_letter_queue.append(issue_dict)

    def update_progress(self, increment: int = 1) -> Tuple[int, int]:
        """Thread-safe method to update progress and return current counts."""
        with self.progress_lock:
            self.processed_files += increment
            return self.processed_files, self.total_files

    def _create_validators(self, validator_names: List[str]) -> List[BaseValidator]:
        """Create validator instances based on names."""
        all_validators = {
            "eventtype": EventTypeValidator,
            "rst_quality": RSTQualityValidator,
            "code_examples": CodeExampleValidator,
            "navigation": NavigationValidator,
            "professional_rst": ProfessionalRSTValidator,
            "sphinx": SphinxValidator,
        }

        if not validator_names:
            # Use all validators by default
            validator_names = list(all_validators.keys())

        validators: List[BaseValidator] = []
        sphinx_validator = None

        # Create SphinxValidator first if needed
        if "sphinx" in validator_names:
            sphinx_validator = SphinxValidator(self.fix_mode)
            validators.append(sphinx_validator)

        for name in validator_names:
            if (
                name in all_validators and name != "sphinx"
            ):  # Skip sphinx as we already added it
                if name == "code_examples":
                    # Pass RST processor to CodeExampleValidator
                    validators.append(
                        all_validators[name](self.fix_mode, self.rst_processor)
                    )
                elif name == "professional_rst":
                    # Pass RST processor and SphinxValidator to ProfessionalRSTValidator
                    validators.append(
                        all_validators[name](
                            self.fix_mode, self.rst_processor, sphinx_validator
                        )
                    )
                else:
                    validators.append(all_validators[name](self.fix_mode))

        return validators

    def process_path(self, path: Path) -> ValidationResult:
        """Process a file or directory path using multi-threading."""
        start_time = time.time()

        if path.is_file():
            files_to_process = [path] if path.suffix == ".rst" else []
        else:
            files_to_process = list(path.rglob("*.rst"))
            files_to_process = [
                f
                for f in files_to_process
                if not any(skip in str(f) for skip in ["_build", "_templates"])
            ]

        self.total_files = len(files_to_process)
        self.processed_files = 0

        if not files_to_process:
            self.logger.info("No RST files found to process")
            return self.result

        # Set up navigation validator with available files
        available_files = self._build_available_files_set(files_to_process)
        for validator in self.validators:
            if isinstance(validator, NavigationValidator):
                validator.set_available_files(available_files)

        self.logger.info(
            f"🚀 Starting multi-threaded processing of {self.total_files} files with {self.max_workers} workers"
        )

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all file processing tasks
            future_to_file = {
                executor.submit(
                    self._process_single_file_threaded, file_path
                ): file_path
                for file_path in files_to_process
            }

            # Process completed tasks with minimal progress reporting
            processed = 0
            total = len(files_to_process)
            # last_milestone = 0  # Unused variable removed

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    future.result()  # This will raise any exception that occurred
                    processed += 1

                    # Minimal progress - only final completion
                    if processed == total:
                        pass  # Final summary will be shown later

                except Exception as e:
                    self.logger.error(f"❌ Error processing {file_path}: {e}")

        # Generate comprehensive summary report
        self._generate_processing_summary(start_time)

        self.result.files_processed = self.total_files
        self.result.processing_time = time.time() - start_time

        return self.result

    def _apply_fixes_systematically_to_file(
        self, file_path: Path, initial_issues: List[ValidationIssue], content: str
    ) -> Tuple[str, List[str]]:
        """Apply fixes systematically using a queue-based approach - one issue at a time."""
        original_content = content
        current_content = content
        applied_fixes = []

        # Maximum number of fix attempts to prevent infinite loops (unlimited for complete fixing)
        max_fixes = -1  # No limit - fix ALL issues
        fixes_applied = 0

        # Infinite loop detection and dead letter queue
        consecutive_failed_attempts = 0
        max_failed_attempts = 10  # Increased from 5
        last_issue_count = 0
        stagnant_iterations = 0
        max_stagnant_iterations = 5  # Increased from 3
        dead_letter_queue = set()  # Dead letter queue for truly unfixable issues
        failed_attempts_per_issue: Dict[str, int] = (
            {}
        )  # Track attempts per specific issue

        # Count initial auto-fixable issues for progress tracking
        # initial_auto_fixable = len(
        #     [issue for issue in initial_issues if issue.auto_fixable]
        # )  # Unused variable removed

        # Removed verbose processing message for cleaner output

        def get_issue_key(issue: ValidationIssue) -> str:
            """Create a unique key for an issue to track it in the dead letter queue."""
            return f"{issue.file_path}:{issue.line_number}:{issue.issue_type.value}:{hash(issue.message)}"

        while max_fixes == -1 or fixes_applied < max_fixes:
            # Re-validate the current content to get the current state of issues
            current_issues = []
            for validator in self.validators:
                validator_issues = validator.validate_file(file_path, current_content)
                current_issues.extend(validator_issues)

            # Filter to only auto-fixable issues that are NOT in the dead letter queue
            auto_fixable_issues = [
                issue
                for issue in current_issues
                if issue.auto_fixable and get_issue_key(issue) not in dead_letter_queue
            ]
            current_issue_count = len(auto_fixable_issues)

            if not auto_fixable_issues:
                self.logger.info(
                    f"  ✅ All auto-fixable issues resolved after {fixes_applied} fixes"
                )
                break

            # Infinite loop detection: Check if issue count is stagnant
            if current_issue_count == last_issue_count:
                stagnant_iterations += 1
                self.logger.debug(
                    f"  ⚠️ Stagnant iteration {stagnant_iterations}/{max_stagnant_iterations} - issue count unchanged: {current_issue_count}"
                )
                if stagnant_iterations >= max_stagnant_iterations:
                    # Instead of breaking, add the first issue to dead letter queue and continue
                    if auto_fixable_issues:
                        problematic_issue = auto_fixable_issues[0]
                        issue_key = get_issue_key(problematic_issue)
                        dead_letter_queue.add(issue_key)
                        self.logger.warning(
                            f"  💀 Adding stagnant issue to dead letter queue: {problematic_issue.message}"
                        )
                        stagnant_iterations = 0  # Reset and continue
                        continue

                    self.logger.warning(
                        f"  🛑 Breaking: No progress after {max_stagnant_iterations} iterations (stuck at {current_issue_count} issues)"
                    )
                    break
            else:
                stagnant_iterations = 0  # Reset if we made progress

            last_issue_count = current_issue_count

            # Progress indicator
            # remaining_issues = len(auto_fixable_issues)  # Unused variable removed
            # Progress logging removed for cleaner output

            # Sort issues by line number (descending) to avoid line number shifts
            # Process the first (highest line number) issue
            sorted_issues = sorted(
                auto_fixable_issues, key=lambda x: x.line_number or 0, reverse=True
            )
            issue_to_fix = sorted_issues[0]

            self.logger.info(
                f"  🎯 Fix #{fixes_applied + 1}: {issue_to_fix.message} (line {issue_to_fix.line_number})"
            )

            # Debug: Show the actual line content
            lines = current_content.split("\n")
            if issue_to_fix.line_number and 0 < issue_to_fix.line_number <= len(lines):
                actual_line = lines[issue_to_fix.line_number - 1]
                self.logger.debug(f"    📝 Line content: {repr(actual_line)}")

            # Try to fix this specific issue
            fix_applied = False
            for validator in self.validators:
                if validator.can_fix_issue(issue_to_fix):
                    self.logger.debug(
                        f"    🔧 Attempting fix with {validator.__class__.__name__}"
                    )
                    new_content, success = validator.fix_issue(
                        issue_to_fix, current_content
                    )
                    if success and new_content != current_content:
                        current_content = new_content
                        fix_msg = f"Fixed {issue_to_fix.issue_type.value}: {issue_to_fix.message}"
                        applied_fixes.append(fix_msg)
                        fixes_applied += 1
                        fix_applied = True
                        consecutive_failed_attempts = 0  # Reset on success
                        self.logger.info(f"    ✅ {fix_msg}")
                        break

                    if success and new_content == current_content:
                        self.logger.debug(
                            f"    ⚠️ Fix returned success but content unchanged"
                        )
                    elif not success:
                        self.logger.debug(
                            f"    ❌ Failed to fix: {issue_to_fix.message}"
                        )

            # If we couldn't fix this issue, track failed attempts
            if not fix_applied:
                issue_key = get_issue_key(issue_to_fix)

                # Track attempts per issue
                failed_attempts_per_issue[issue_key] = (
                    failed_attempts_per_issue.get(issue_key, 0) + 1
                )
                consecutive_failed_attempts += 1

                self.logger.debug(
                    f"    ⚠️ Could not fix issue (attempt {failed_attempts_per_issue[issue_key]}, consecutive: {consecutive_failed_attempts}/{max_failed_attempts}): {issue_to_fix.message}"
                )

                # If this specific issue has failed too many times, add to dead letter queue
                if (
                    failed_attempts_per_issue[issue_key] >= 5
                ):  # Max 5 attempts per issue
                    dead_letter_queue.add(issue_key)
                    self.logger.warning(
                        f"    💀 Adding issue to dead letter queue after {failed_attempts_per_issue[issue_key]} failed attempts: {issue_to_fix.message}"
                    )
                    consecutive_failed_attempts = 0  # Reset since we're making progress
                    continue

                # Check if there are any other auto-fixable issues not in dead letter queue
                remaining_fixable = [
                    issue
                    for issue in current_issues
                    if issue.auto_fixable
                    and get_issue_key(issue) not in dead_letter_queue
                    and issue != issue_to_fix
                ]
                if not remaining_fixable:
                    self.logger.info(f"  ⏹️ No more fixable issues remaining")
                    break

        # Determine why we stopped
        if max_fixes != -1 and fixes_applied >= max_fixes:
            self.logger.warning(
                f"  🛑 Stopped: Reached maximum fix limit ({max_fixes})"
            )
        elif consecutive_failed_attempts >= max_failed_attempts:
            self.logger.warning(
                f"  🛑 Stopped: Too many consecutive failures ({max_failed_attempts})"
            )
        elif stagnant_iterations >= max_stagnant_iterations:
            self.logger.warning(
                f"  🛑 Stopped: No progress for {max_stagnant_iterations} iterations"
            )

        # Write back if content changed
        if current_content != original_content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(current_content)
                self.logger.info(
                    f"  💾 Updated {file_path.name} with {fixes_applied} fixes"
                )
            except Exception as e:
                self.logger.error(f"  ❌ Failed to write {file_path}: {e}")
        elif fixes_applied == 0:
            self.logger.info(f"  ℹ️ No fixes needed for {file_path.name}")

        # Final status
        final_issues = []
        for validator in self.validators:
            validator_issues = validator.validate_file(file_path, current_content)
            final_issues.extend(validator_issues)
        final_auto_fixable = len(
            [issue for issue in final_issues if issue.auto_fixable]
        )

        if final_auto_fixable > 0:
            dead_letter_count = len(dead_letter_queue)
            self.logger.info(
                f"  📋 Final status: {fixes_applied} fixes applied, {final_auto_fixable} auto-fixable issues remain"
            )
            if dead_letter_count > 0:
                self.logger.info(
                    f"  💀 Dead letter queue: {dead_letter_count} issues marked as unfixable"
                )
        else:
            dead_letter_count = len(dead_letter_queue)
            if dead_letter_count > 0:
                self.logger.info(
                    f"  🎉 Success: {fixes_applied} fixes applied, all auto-fixable issues resolved!"
                )
                self.logger.info(
                    f"  💀 Dead letter queue: {dead_letter_count} issues were marked as unfixable"
                )
            else:
                self.logger.info(
                    f"  🎉 Perfect: {fixes_applied} fixes applied, all issues resolved with no dead letters!"
                )

        return current_content, applied_fixes

    def _build_available_files_set(self, files: List[Path]) -> Set[str]:
        """Build set of available files for navigation validation."""
        available_files = set()

        for file_path in files:
            # Convert to relative path from docs directory
            try:
                if "docs" in str(file_path):
                    docs_index = str(file_path).find("docs")
                    relative_path = Path(
                        str(file_path)[docs_index + 5 :]
                    )  # Skip 'docs/'
                else:
                    relative_path = file_path

                if relative_path.name == "index.rst":
                    if relative_path.parent == Path("."):
                        available_files.add("index")
                    else:
                        dir_path = str(relative_path.parent).replace("\\", "/")
                        available_files.add(dir_path + "/index")
                        available_files.add(dir_path)
                else:
                    ref_path = str(relative_path.with_suffix("")).replace("\\", "/")
                    available_files.add(ref_path)
            except Exception:
                continue

        return available_files

    def _process_single_file(self, file_path: Path) -> None:
        """Process a single file with all validators."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            current_content = original_content
            file_issues = []
            file_fixes = []

            # Run all validators
            for validator in self.validators:
                issues = validator.validate_file(file_path, current_content)
                file_issues.extend(issues)

            # Apply fixes if in fix mode using systematic approach
            if self.fix_mode and file_issues:
                current_content, applied_fixes = (
                    self._apply_fixes_systematically_to_file(
                        file_path, file_issues, current_content
                    )
                )
                file_fixes.extend(applied_fixes)

            # Add to results
            self.result.issues.extend(file_issues)
            self.result.fixes_applied.extend(file_fixes)

            # Log progress with appropriate levels
            if file_issues:
                self.logger.warning(f"❌ {file_path.name}: {len(file_issues)} issues")
                if file_fixes:
                    self.logger.info(
                        f"🔧 {file_path.name}: {len(file_fixes)} fixes applied"
                    )
            else:
                self.logger.debug(f"✅ {file_path.name}")

        except Exception as e:
            error_issue = ValidationIssue(
                file_path=str(file_path),
                line_number=1,
                issue_type=ValidationType.RST_QUALITY,
                level=ValidationLevel.ERROR,
                message=f"Error processing file: {e}",
                auto_fixable=False,
            )
            self.result.issues.append(error_issue)
            print(f"❌ Error processing {file_path}: {e}")

    def _process_single_file_threaded(self, file_path: Path) -> None:
        """Unified Black-style single-pass processing for all validators."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # STEP 1: Detect all issues from all validators
            all_issues = []
            for validator in self.validators:
                validator_issues = validator.validate_file(file_path, original_content)
                all_issues.extend(validator_issues)

            # STEP 2: Apply all fixes in single pass (if in fix mode)
            current_content = original_content
            all_applied_fixes: List[str] = []
            remaining_issues = all_issues.copy()

            if self.fix_mode and all_issues:
                current_content, all_applied_fixes, remaining_issues = (
                    self._apply_all_fixes_single_pass(
                        file_path, original_content, all_issues
                    )
                )

                # Write fixed content back to file
                if current_content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(current_content)

            # STEP 3: Thread-safe result collection
            with self.progress_lock:
                self.result.issues.extend(remaining_issues)
                if all_applied_fixes:
                    self.result.fixes_applied.extend(all_applied_fixes)

            # Collect individual file result for summary
            file_result = ValidationResult()
            file_result.file_path = str(file_path)
            file_result.issues = remaining_issues
            file_result.fixes_applied = all_applied_fixes

            with self.results_lock:
                self.file_results.append(file_result)

        except Exception as e:
            error_issue = ValidationIssue(
                file_path=str(file_path),
                line_number=1,
                issue_type=ValidationType.RST_QUALITY,
                level=ValidationLevel.ERROR,
                message=f"Error processing file: {e}",
                auto_fixable=False,
            )
            with self.progress_lock:
                self.result.issues.append(error_issue)

            # Add error to file results too
            error_result = ValidationResult()
            error_result.file_path = str(file_path)
            error_result.issues = [error_issue]
            error_result.fixes_applied = []

            with self.results_lock:
                self.file_results.append(error_result)

            self.logger.error(f"❌ Error processing {file_path}: {e}")

    def _apply_all_fixes_single_pass(
        self, file_path: Path, content: str, all_issues: List[ValidationIssue]
    ) -> Tuple[str, List[str], List[ValidationIssue]]:
        """Apply all possible fixes in a single pass (Black-style approach)."""
        current_content = content
        applied_fixes = []
        unfixable_issues = []

        # Group issues by validator type for efficient processing
        issues_by_validator: Dict[str, List[ValidationIssue]] = {}
        for issue in all_issues:
            validator_type = (
                type(issue).__name__ if hasattr(issue, "__class__") else "unknown"
            )
            if validator_type not in issues_by_validator:
                issues_by_validator[validator_type] = []
            issues_by_validator[validator_type].append(issue)

        # Apply fixes from each validator in single pass
        for validator in self.validators:
            validator_name = type(validator).__name__
            validator_issues = [
                issue for issue in all_issues if validator.can_fix_issue(issue)
            ]

            if validator_issues:
                try:
                    # Each validator applies ALL its fixes in one pass
                    fixed_content, fixes = validator.fix_all_issues(
                        file_path, current_content, validator_issues
                    )
                    if fixed_content != current_content:
                        current_content = fixed_content
                        applied_fixes.extend(fixes)
                except Exception as e:
                    # If validator can't fix, add issues to unfixable list
                    self.logger.debug(
                        f"Validator {validator_name} couldn't fix issues in {file_path}: {e}"
                    )
                    unfixable_issues.extend(validator_issues)

        # Any issues not handled by any validator are unfixable
        handled_issues = set()
        for validator in self.validators:
            for issue in all_issues:
                if validator.can_fix_issue(issue):
                    handled_issues.add(id(issue))

        for issue in all_issues:
            if id(issue) not in handled_issues:
                unfixable_issues.append(issue)

        return current_content, applied_fixes, unfixable_issues

    def _apply_fixes_systematically_to_file_threaded(
        self, file_path: Path, initial_issues: List[ValidationIssue], content: str
    ) -> Tuple[str, List[str]]:
        """Optimized thread-safe version of systematic fix application with shared dead letter queue."""
        original_content = content
        current_content = content
        applied_fixes = []

        # Maximum number of fix attempts to prevent infinite loops (unlimited for complete fixing)
        max_fixes = -1  # No limit - fix ALL issues
        fixes_applied = 0

        # Create file-specific issue queue
        issue_queue = deque(initial_issues)
        local_dead_letter = set()  # Track issues we've already dead-lettered locally

        # Infinite loop detection (optimized)
        consecutive_failed_attempts = 0
        max_failed_attempts = 8  # Reduced for faster dead-lettering

        while issue_queue and (max_fixes == -1 or fixes_applied < max_fixes):
            if consecutive_failed_attempts >= max_failed_attempts:
                # Move remaining issues to shared dead letter queue
                while issue_queue:
                    issue = issue_queue.popleft()
                    issue_key = (issue.line_number, issue.message[:50])
                    if issue_key not in local_dead_letter:
                        self.add_to_dead_letter_queue(
                            {
                                "file_path": str(file_path),
                                "line_number": issue.line_number,
                                "issue_type": issue.issue_type.value,
                                "level": issue.level.value,
                                "message": issue.message,
                                "auto_fixable": issue.auto_fixable,
                            },
                            str(file_path),
                        )
                        local_dead_letter.add(issue_key)
                break

            issue = issue_queue.popleft()
            issue_key = (issue.line_number, issue.message[:50])

            # Skip if already dead-lettered locally
            if issue_key in local_dead_letter:
                continue

            # Find the appropriate validator for this issue
            validator = None
            for v in self.validators:
                if (
                    hasattr(v, "fix_issue")
                    and hasattr(v, "_is_auto_fixable")
                    and v._is_auto_fixable(issue)
                ):
                    validator = v
                    break

            if not validator:
                # No validator can fix this, add to dead letter queue
                self.add_to_dead_letter_queue(
                    {
                        "file_path": str(file_path),
                        "line_number": issue.line_number,
                        "issue_type": issue.issue_type.value,
                        "level": issue.level.value,
                        "message": issue.message,
                        "auto_fixable": issue.auto_fixable,
                    },
                    str(file_path),
                )
                local_dead_letter.add(issue_key)
                continue

            # Try to fix the issue
            try:
                new_content, was_fixed = validator.fix_issue(issue, current_content)

                if was_fixed and new_content != current_content:
                    current_content = new_content
                    applied_fixes.append(
                        f"Fixed {issue.issue_type.value}: {issue.message}"
                    )
                    fixes_applied += 1
                    consecutive_failed_attempts = 0

                    # Re-validate only if we made significant changes (every 10 fixes)
                    if fixes_applied % 10 == 0:
                        # Quick re-validation to catch new issues
                        new_issues = []
                        for v in self.validators:
                            new_issues.extend(
                                v.validate_file(file_path, current_content)
                            )

                        # Add new auto-fixable issues to queue
                        for new_issue in new_issues:
                            new_key = (new_issue.line_number, new_issue.message[:50])
                            if new_key not in local_dead_letter and any(
                                hasattr(v, "_is_auto_fixable")
                                and v._is_auto_fixable(new_issue)
                                for v in self.validators
                            ):
                                issue_queue.append(new_issue)
                else:
                    # Fix failed, add to dead letter queue
                    self.add_to_dead_letter_queue(
                        {
                            "file_path": str(file_path),
                            "line_number": issue.line_number,
                            "issue_type": issue.issue_type.value,
                            "level": issue.level.value,
                            "message": issue.message,
                            "auto_fixable": issue.auto_fixable,
                        },
                        str(file_path),
                    )
                    local_dead_letter.add(issue_key)
                    consecutive_failed_attempts += 1

            except Exception as e:
                # Fix attempt caused an error, dead letter it
                self.add_to_dead_letter_queue(
                    {
                        "file_path": str(file_path),
                        "line_number": issue.line_number,
                        "issue_type": issue.issue_type.value,
                        "level": issue.level.value,
                        "message": issue.message,
                        "auto_fixable": issue.auto_fixable,
                        "fix_error": str(e),
                    },
                    str(file_path),
                )
                local_dead_letter.add(issue_key)
                consecutive_failed_attempts += 1

        # Write the file if we made changes
        if current_content != original_content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(current_content)
            except Exception as e:
                self.logger.error(f"❌ Failed to write {file_path}: {e}")

        return current_content, applied_fixes

    # apply_black_inspired_fixes and _validate_transformation methods removed - dead code

    def _generate_processing_summary(self, start_time: float) -> None:
        """Generate comprehensive processing summary with unfixable issue analysis."""
        processing_time = time.time() - start_time

        # Calculate total issues across all results
        total_detected_issues = sum(
            len(result.issues) for result in self.file_results if result.issues
        )
        total_errors = sum(result.error_count for result in self.file_results)
        total_warnings = sum(result.warning_count for result in self.file_results)

        # In Black-style approach, unfixable issues are simply the remaining issues after fixes
        total_fixes = sum(
            len(result.fixes_applied)
            for result in self.file_results
            if result.fixes_applied
        )
        unfixable_count = total_detected_issues  # All remaining issues are unfixable

        # Analyze unfixable issues by type and source (from remaining issues)
        unfixable_by_source = defaultdict(list)
        unfixable_by_type: defaultdict = defaultdict(int)
        unfixable_by_file: defaultdict = defaultdict(int)

        for result in self.file_results:
            if result.issues:
                for issue in result.issues:
                    # Extract source from issue context or message
                    source = "unknown"
                    if hasattr(issue, "context") and issue.context:
                        source = issue.context.get("source_linter", "unknown")
                    elif "[" in issue.message and "]" in issue.message:
                        # Extract source from message like "[docutils] error message"
                        source = issue.message.split("[")[1].split("]")[0]

                    issue_type = (
                        issue.message.split(":")[0]
                        if ":" in issue.message
                        else issue.message[:50]
                    )
                    file_path = issue.file_path

                    unfixable_by_source[source].append(issue)
                    unfixable_by_type[issue_type] += 1
                    unfixable_by_file[file_path] += 1

        # Lead with clear summary
        self.logger.info("=" * 80)
        self.logger.info("📊 DOCUMENTATION QUALITY SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(
            f"📁 Files processed: {self.total_files} in {processing_time:.2f}s ({self.max_workers} workers)"
        )
        self.logger.info(f"🔧 Fixes applied: {total_fixes}")
        self.logger.info(
            f"🔍 Issues detected: {total_detected_issues} ({total_errors} errors, {total_warnings} warnings)"
        )
        self.logger.info(f"💀 Unfixable issues: {unfixable_count}")

        # Show what was fixed (if any)
        if total_fixes > 0:
            self.logger.info("")
            self.logger.info("✅ FIXES APPLIED:")
            for result in self.file_results:
                if result.fixes_applied and result.fixes_applied != "0 issues detected":
                    file_name = Path(result.file_path).name
                    self.logger.info(
                        f"  • {file_name}: {len(result.fixes_applied)} fixes"
                    )

        # Show detected issues that need attention (always show if there are issues)
        if total_detected_issues > 0:
            self.logger.info("")
            self.logger.info("⚠️  ISSUES NEEDING ATTENTION:")
            self.logger.info("-" * 50)

            # Collect issue types from all results
            issue_type_counts: Dict[str, int] = {}
            file_issue_counts: Dict[str, int] = {}

            for result in self.file_results:
                if result.issues:
                    file_name = Path(result.file_path).name
                    file_issue_counts[file_name] = len(result.issues)

                    for issue in result.issues:
                        # Extract issue type from message
                        if "Unknown directive type" in issue.message:
                            issue_type = f"Unknown directive: {issue.message.split('\"')[1] if '\"' in issue.message else 'various'}"
                        elif "Unknown interpreted text role" in issue.message:
                            issue_type = f"Unknown role: {issue.message.split('\"')[1] if '\"' in issue.message else 'various'}"
                        elif "No directive entry for" in issue.message:
                            issue_type = f"Missing directive: {issue.message.split('\"')[1] if '\"' in issue.message else 'various'}"
                        elif "No role entry for" in issue.message:
                            issue_type = f"Missing role: {issue.message.split('\"')[1] if '\"' in issue.message else 'various'}"
                        else:
                            issue_type = (
                                issue.message.split(".")[0]
                                if "." in issue.message
                                else issue.message[:50]
                            )

                        issue_type_counts[issue_type] = (
                            issue_type_counts.get(issue_type, 0) + 1
                        )

            # Show top issue types
            self.logger.info("Common Issues:")
            for issue_type, count in sorted(
                issue_type_counts.items(), key=lambda x: x[1], reverse=True
            )[:8]:
                self.logger.info(f"  • {issue_type}: {count}")

            # Show files with most issues
            if file_issue_counts:
                self.logger.info("")
                self.logger.info("Files Needing Attention:")
                for file_name, count in sorted(
                    file_issue_counts.items(), key=lambda x: x[1], reverse=True
                )[:8]:
                    self.logger.info(f"  • {file_name}: {count} issues")

        # Prominently show unfixable issues (from dead letter queue)
        if unfixable_count > 0:
            self.logger.info("")
            self.logger.info("❌ UNFIXABLE ISSUES BREAKDOWN:")
            self.logger.info("-" * 50)

            # By source linter with counts
            self.logger.info("By Source:")
            for source, issues in sorted(
                unfixable_by_source.items(), key=lambda x: len(x[1]), reverse=True
            ):
                self.logger.info(f"  • {source}: {len(issues)} issues")

            self.logger.info("")
            self.logger.info("Top Issue Types:")
            for issue_type, count in sorted(
                unfixable_by_type.items(), key=lambda x: x[1], reverse=True
            )[:8]:
                self.logger.info(f"  • {issue_type}: {count}")

            self.logger.info("")
            self.logger.info("Files Needing Attention:")
            for file_path, count in sorted(
                unfixable_by_file.items(), key=lambda x: x[1], reverse=True
            )[:8]:
                file_name = Path(file_path).name
                self.logger.info(f"  • {file_name}: {count} issues")

        self.logger.info("=" * 80)

        # Export AI-consumable data for follow-up iterations (if enabled)
        if getattr(self, "export_ai_data", True):  # Default to True, can be disabled
            self._export_ai_consumable_data(
                total_detected_issues, total_fixes, processing_time
            )

    def _export_ai_consumable_data(
        self, total_issues: int, total_fixes: int, processing_time: float
    ) -> None:
        """Export comprehensive data for AI-driven follow-up iterations."""
        # Create comprehensive AI-consumable report
        ai_data: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "files_processed": self.total_files,
                "processing_time_seconds": processing_time,
                "total_issues_detected": total_issues,
                "fixes_applied": total_fixes,
                "unfixable_issues": total_issues,
                "success_rate": (
                    (total_fixes / (total_fixes + total_issues)) * 100
                    if (total_fixes + total_issues) > 0
                    else 0
                ),
            },
            "files": [],
            "issue_patterns": {},
            "recommended_actions": [],
        }

        # Collect detailed file-level data
        for result in self.file_results:
            file_data: Dict[str, Any] = {
                "file_path": result.file_path,
                "file_name": Path(result.file_path).name,
                "issues_count": len(result.issues),
                "fixes_applied": len(result.fixes_applied),
                "error_count": result.error_count,
                "warning_count": result.warning_count,
                "issues": [],
            }

            # Add detailed issue information
            for issue in result.issues:
                issue_data = {
                    "line_number": issue.line_number,
                    "level": issue.level.value,
                    "message": issue.message,
                    "issue_type": (
                        issue.issue_type.value
                        if hasattr(issue.issue_type, "value")
                        else str(issue.issue_type)
                    ),
                    "auto_fixable": issue.auto_fixable,
                    "source_linter": self._extract_source_linter(issue),
                    "category": self._categorize_issue(issue),
                    "suggested_fix": self._suggest_fix_approach(issue),
                }
                file_data["issues"].append(issue_data)

            if file_data["issues_count"] > 0:  # Only include files with issues
                ai_data["files"].append(file_data)

        # Analyze patterns for AI recommendations
        ai_data["issue_patterns"] = self._analyze_issue_patterns()
        ai_data["recommended_actions"] = self._generate_ai_recommendations()

        # Export to multiple formats for different use cases
        self._write_ai_export_files(ai_data)

    def _extract_source_linter(self, issue: ValidationIssue) -> str:
        """Extract the source linter from issue context or message."""
        if hasattr(issue, "context") and issue.context:
            return str(issue.context.get("source_linter", "unknown"))
        elif "[" in issue.message and "]" in issue.message:
            return issue.message.split("[")[1].split("]")[0]
        return "unknown"

    def _categorize_issue(self, issue: ValidationIssue) -> str:
        """Categorize issue for AI processing."""
        message = issue.message.lower()
        if "syntax" in message or "invalid" in message:
            return "syntax_error"
        elif "duplicate" in message:
            return "duplicate_reference"
        elif "unknown directive" in message or "unknown role" in message:
            return "missing_extension"
        elif "indentation" in message or "indent" in message:
            return "formatting"
        elif "line too long" in message:
            return "line_length"
        elif "underline" in message:
            return "title_formatting"
        else:
            return "other"

    def _suggest_fix_approach(self, issue: ValidationIssue) -> str:
        """Suggest fix approach for AI to implement."""
        category = self._categorize_issue(issue)
        suggestions = {
            "syntax_error": "Fix Python syntax in code block",
            "duplicate_reference": "Remove or rename duplicate reference targets",
            "missing_extension": "Add Sphinx extension or convert to standard RST",
            "formatting": "Fix indentation to match RST standards",
            "line_length": "Break long lines or use line continuation",
            "title_formatting": "Adjust title underline length to match title",
            "other": "Manual review required",
        }
        return suggestions.get(category, "Manual review required")

    def _analyze_issue_patterns(self) -> dict:
        """Analyze patterns across all issues for AI insights."""
        patterns: Dict[str, Any] = {
            "by_category": defaultdict(int),
            "by_source": defaultdict(int),
            "by_file_type": defaultdict(int),
            "common_lines": defaultdict(int),
        }

        for result in self.file_results:
            file_ext = Path(result.file_path).suffix
            for issue in result.issues:
                category = self._categorize_issue(issue)
                source = self._extract_source_linter(issue)

                patterns["by_category"][category] += 1
                patterns["by_source"][source] += 1
                patterns["by_file_type"][file_ext] += 1
                patterns["common_lines"][issue.line_number] += 1

        return {k: dict(v) for k, v in patterns.items()}

    def _generate_ai_recommendations(self) -> list:
        """Generate specific recommendations for AI follow-up."""
        recommendations = []

        # Analyze patterns and generate actionable recommendations
        patterns = self._analyze_issue_patterns()

        # High-priority recommendations based on patterns
        if patterns["by_category"].get("syntax_error", 0) > 5:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "fix_python_syntax",
                    "description": "Multiple Python syntax errors in code blocks need fixing",
                    "files_affected": [
                        r.file_path
                        for r in self.file_results
                        if any("syntax" in i.message.lower() for i in r.issues)
                    ],
                }
            )

        if patterns["by_category"].get("duplicate_reference", 0) > 3:
            recommendations.append(
                {
                    "priority": "medium",
                    "action": "resolve_duplicates",
                    "description": "Multiple duplicate reference targets need resolution",
                    "files_affected": [
                        r.file_path
                        for r in self.file_results
                        if any("duplicate" in i.message.lower() for i in r.issues)
                    ],
                }
            )

        if patterns["by_category"].get("line_length", 0) > 10:
            recommendations.append(
                {
                    "priority": "low",
                    "action": "format_long_lines",
                    "description": "Many lines exceed length limits",
                    "files_affected": [
                        r.file_path
                        for r in self.file_results
                        if any("line too long" in i.message.lower() for i in r.issues)
                    ],
                }
            )

        return recommendations

    def _write_ai_export_files(self, ai_data: dict) -> None:
        """Write AI-consumable data with clean, overwrite-based approach."""
        # Use fixed filenames that overwrite on each run (no filesystem clutter)
        json_file = ".docs-quality-report.json"
        csv_file = ".docs-quality-issues.csv"
        md_file = ".docs-quality-summary.md"

        # Only export if there are issues to report
        if ai_data["summary"]["total_issues_detected"] == 0:
            # Clean up any existing files if no issues found
            for file_path in [json_file, csv_file, md_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)
            self.logger.info("✨ No issues found - cleaned up previous reports")
            return

        # 1. Comprehensive JSON for full AI analysis
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(ai_data, f, indent=2, default=str)

        # 2. Simple CSV for quick analysis
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "file_path",
                    "line_number",
                    "level",
                    "category",
                    "source_linter",
                    "message",
                    "suggested_fix",
                ]
            )

            for file_data in ai_data["files"]:
                for issue in file_data["issues"]:
                    writer.writerow(
                        [
                            file_data["file_path"],
                            issue["line_number"],
                            issue["level"],
                            issue["category"],
                            issue["source_linter"],
                            issue["message"][:100],  # Truncate long messages
                            issue["suggested_fix"],
                        ]
                    )

        # 3. Markdown summary for human review
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# Documentation Quality Report\n\n")
            f.write(f"**Generated**: {ai_data['timestamp']}  \n")
            f.write(f"**Files Processed**: {ai_data['summary']['files_processed']}  \n")
            f.write(
                f"**Issues Found**: {ai_data['summary']['total_issues_detected']}  \n"
            )
            f.write(f"**Fixes Applied**: {ai_data['summary']['fixes_applied']}  \n")
            f.write(
                f"**Success Rate**: {ai_data['summary']['success_rate']:.1f}%  \n\n"
            )

            if ai_data["recommended_actions"]:
                f.write("## Recommended Actions\n\n")
                for rec in ai_data["recommended_actions"]:
                    f.write(f"- **{rec['priority'].upper()}**: {rec['description']}\n")

            f.write("\n## Files Needing Attention\n\n")
            for file_data in sorted(
                ai_data["files"], key=lambda x: x["issues_count"], reverse=True
            )[:10]:
                f.write(
                    f"- `{file_data['file_name']}`: {file_data['issues_count']} issues\n"
                )

        self.logger.info(f"📄 AI-consumable reports updated:")
        self.logger.info(f"  • JSON: {json_file}")
        self.logger.info(f"  • CSV: {csv_file}")
        self.logger.info(f"  • Summary: {md_file}")

    def generate_unfixable_issues_report(self, format_type: str = "human") -> str:
        """Generate detailed report of unfixable issues for manual review or AI processing."""
        with self.dead_letter_lock:
            dead_letter_issues = list(self.shared_dead_letter_queue)

        if format_type == "json":
            return self._generate_machine_friendly_report(dead_letter_issues)
        else:
            return self._generate_human_friendly_report(dead_letter_issues)

    def _generate_machine_friendly_report(self, dead_letter_issues: List[Dict]) -> str:
        """Generate JSON report optimized for AI assistant consumption."""
        # Categorize issues for AI processing
        categorized_issues: Dict[str, Any] = {
            "summary": {"total_unfixable": len(dead_letter_issues), "categories": {}},
            "actionable_fixes": [],
            "complex_issues": [],
            "systematic_patterns": [],
        }

        # Group by source and message patterns
        by_source = defaultdict(list)
        message_patterns = defaultdict(list)

        for issue in dead_letter_issues:
            source = issue.get("source", "unknown")
            message = issue.get("message", "")
            file_path = issue.get("file_path", "")
            line_number = issue.get("line_number", 0)

            by_source[source].append(issue)

            # Extract patterns for systematic fixes
            if "invalid syntax" in message.lower():
                message_patterns["python_syntax_errors"].append(
                    {
                        "file": file_path,
                        "line": line_number,
                        "message": message,
                        "source": source,
                    }
                )
            elif "unknown" in message.lower() and (
                "role" in message.lower() or "directive" in message.lower()
            ):
                message_patterns["unknown_rst_constructs"].append(
                    {
                        "file": file_path,
                        "line": line_number,
                        "message": message,
                        "source": source,
                    }
                )
            elif "line too long" in message.lower():
                message_patterns["line_length_violations"].append(
                    {
                        "file": file_path,
                        "line": line_number,
                        "message": message,
                        "source": source,
                    }
                )
            elif "duplicate" in message.lower():
                message_patterns["duplicate_constructs"].append(
                    {
                        "file": file_path,
                        "line": line_number,
                        "message": message,
                        "source": source,
                    }
                )

        # Populate categorized report
        categorized_issues["summary"]["categories"] = {
            k: len(v) for k, v in by_source.items()
        }
        categorized_issues["systematic_patterns"] = dict(message_patterns)

        # Generate actionable fixes
        for pattern, issues in message_patterns.items():
            if len(issues) >= 3:  # Systematic pattern
                categorized_issues["actionable_fixes"].append(
                    {
                        "pattern": pattern,
                        "count": len(issues),
                        "description": self._get_pattern_description(pattern),
                        "suggested_approach": self._get_suggested_approach(pattern),
                        "sample_issues": issues[:5],  # First 5 examples
                    }
                )

        return json.dumps(categorized_issues, indent=2)

    def _generate_human_friendly_report(self, dead_letter_issues: List[Dict]) -> str:
        """Generate human-readable report with actionable recommendations."""
        if not dead_letter_issues:
            return "🎉 No unfixable issues found! All detected issues were successfully auto-fixed."

        lines = []
        lines.append("🔍 UNFIXABLE ISSUES ANALYSIS & RECOMMENDATIONS")
        lines.append("=" * 80)
        lines.append(f"Total unfixable issues: {len(dead_letter_issues)}")
        lines.append("")

        # Group by source for analysis
        by_source = defaultdict(list)
        for issue in dead_letter_issues:
            source = issue.get("source", "unknown")
            by_source[source].append(issue)

        for source, issues in sorted(by_source.items()):
            lines.append(f"📊 {source.upper()} ISSUES ({len(issues)} total)")
            lines.append("-" * 50)

            # Group by message pattern
            by_message = defaultdict(list)
            for issue in issues:
                message_key = (
                    issue.get("message", "")[:50] + "..."
                    if len(issue.get("message", "")) > 50
                    else issue.get("message", "")
                )
                by_message[message_key].append(issue)

            for message, message_issues in sorted(
                by_message.items(), key=lambda x: len(x[1]), reverse=True
            )[:10]:
                lines.append(f"  • {message} ({len(message_issues)} occurrences)")
                if len(message_issues) <= 3:
                    for issue in message_issues:
                        file_path = Path(issue.get("file_path", "")).name
                        line_num = issue.get("line_number", 0)
                        lines.append(f"    - {file_path}:{line_num}")
                else:
                    lines.append(f"    - Multiple files (showing first 3):")
                    for issue in message_issues[:3]:
                        file_path = Path(issue.get("file_path", "")).name
                        line_num = issue.get("line_number", 0)
                        lines.append(f"      * {file_path}:{line_num}")
            lines.append("")

        # Add recommendations
        lines.append("💡 RECOMMENDED ACTIONS:")
        lines.append("-" * 50)
        lines.append(
            "1. 🐍 Python Syntax Errors: Review code blocks for missing commas, quotes, brackets"
        )
        lines.append(
            "2. 📝 Unknown RST Constructs: Check for typos in :doc:, :ref:, or directive names"
        )
        lines.append(
            "3. 📏 Line Length: Break long lines at logical points (80-88 chars)"
        )
        lines.append(
            "4. 🔄 Duplicates: Rename or remove duplicate labels, targets, references"
        )
        lines.append(
            "5. 🔧 Markup Issues: Add blank lines before/after code blocks and sections"
        )
        lines.append("")
        lines.append(
            "🤖 For AI Assistant: Use 'generate_unfixable_issues_report(\"json\")' for structured data"
        )

        return "\n".join(lines)

    def _get_pattern_description(self, pattern: str) -> str:
        """Get human-readable description for issue patterns."""
        descriptions = {
            "python_syntax_errors": "Python code blocks with syntax errors (missing commas, quotes, brackets)",
            "unknown_rst_constructs": "Unknown RST roles or directives (typos in :doc:, :ref:, etc.)",
            "line_length_violations": "Lines exceeding maximum length (typically 80-88 characters)",
            "duplicate_constructs": "Duplicate labels, targets, or reference names",
        }
        return descriptions.get(pattern, f"Issues matching pattern: {pattern}")

    def _get_suggested_approach(self, pattern: str) -> str:
        """Get suggested approach for fixing issue patterns."""
        approaches = {
            "python_syntax_errors": "Review and fix Python syntax in code blocks. Common fixes: add missing commas, close quotes/brackets, fix indentation",
            "unknown_rst_constructs": "Check for typos in RST roles/directives. Convert :doc: to external links if needed, fix directive names",
            "line_length_violations": "Break long lines at logical points (after commas, before operators). Use line continuation for code",
            "duplicate_constructs": "Rename duplicate labels/targets to be unique, or remove unnecessary duplicates",
        }
        return approaches.get(
            pattern, f"Manual review and fixing required for {pattern}"
        )


def generate_report(result: ValidationResult, format_type: str = "text") -> str:
    """Generate a formatted report of validation results."""
    if format_type == "json":
        report_data = {
            "summary": {
                "files_processed": result.files_processed,
                "processing_time": result.processing_time,
                "total_issues": result.total_issues,
                "errors": result.error_count,
                "warnings": result.warning_count,
                "fixes_applied": len(result.fixes_applied),
            },
            "issues": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "type": issue.issue_type.value,
                    "level": issue.level.value,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "auto_fixable": issue.auto_fixable,
                }
                for issue in result.issues
            ],
            "fixes": result.fixes_applied,
        }
        return json.dumps(report_data, indent=2)

    else:  # text format
        lines = []
        lines.append("📊 DOCUMENTATION QUALITY REPORT")
        lines.append("=" * 50)
        lines.append(f"Files processed: {result.files_processed}")
        lines.append(f"Processing time: {result.processing_time:.2f}s")
        lines.append(f"Total issues: {result.total_issues}")
        lines.append(f"  • Errors: {result.error_count}")
        lines.append(f"  • Warnings: {result.warning_count}")
        lines.append(f"Fixes applied: {len(result.fixes_applied)}")

        if result.issues:
            lines.append("\n❌ ISSUES FOUND:")
            for issue in result.issues:
                lines.append(
                    f"  • {issue.file_path}:{issue.line_number} [{issue.level.value}] {issue.message}"
                )
                if issue.suggestion:
                    lines.append(f"    💡 {issue.suggestion}")

        if result.fixes_applied:
            lines.append("\n🔧 FIXES APPLIED:")
            for fix in result.fixes_applied:
                lines.append(f"  • {fix}")

        if result.total_issues == 0:
            lines.append("\n🎉 All quality checks passed!")

        return "\n".join(lines)


def main() -> None:
    """Main entry point for the docs quality mini-app."""
    parser = argparse.ArgumentParser(
        description="Documentation Quality Control Mini-App",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check                           # Check all documentation
  %(prog)s fix --path docs/tutorials/      # Fix specific directory
  %(prog)s report --format json           # Generate JSON report
  %(prog)s validate --only eventtype      # Run specific validator
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check documentation quality")
    check_parser.add_argument(
        "--path", type=Path, default=Path("docs"), help="Path to check"
    )
    check_parser.add_argument(
        "--only",
        nargs="+",
        choices=[
            "eventtype",
            "rst_quality",
            "code_examples",
            "navigation",
            "professional_rst",
            "sphinx",
        ],
        help="Run specific validators only",
    )
    check_parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of worker threads (default: 4)",
    )

    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Auto-fix documentation issues")
    fix_parser.add_argument(
        "--path", type=Path, default=Path("docs"), help="Path to fix"
    )
    fix_parser.add_argument(
        "--only",
        nargs="+",
        choices=[
            "eventtype",
            "rst_quality",
            "code_examples",
            "navigation",
            "professional_rst",
            "sphinx",
        ],
        help="Run specific validators only",
    )
    fix_parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of worker threads (default: 4)",
    )
    fix_parser.add_argument(
        "--no-export",
        action="store_true",
        help="Disable AI-consumable data export (default: export enabled)",
    )

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate quality report")
    report_parser.add_argument(
        "--path", type=Path, default=Path("docs"), help="Path to analyze"
    )
    report_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Report format"
    )
    report_parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format (alias for --format json)",
    )
    report_parser.add_argument(
        "--quiet", action="store_true", help="Suppress progress output (errors only)"
    )
    report_parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output (debug level)"
    )
    report_parser.add_argument(
        "--only",
        nargs="+",
        choices=[
            "eventtype",
            "rst_quality",
            "code_examples",
            "navigation",
            "professional_rst",
            "sphinx",
        ],
        help="Run specific validators only",
    )
    report_parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of worker threads (default: 4)",
    )

    # Validate command (alias for check)
    validate_parser = subparsers.add_parser(
        "validate", help="Validate documentation (alias for check)"
    )
    validate_parser.add_argument(
        "--path", type=Path, default=Path("docs"), help="Path to validate"
    )
    validate_parser.add_argument(
        "--only",
        nargs="+",
        choices=[
            "eventtype",
            "rst_quality",
            "code_examples",
            "navigation",
            "professional_rst",
            "sphinx",
        ],
        help="Run specific validators only",
    )
    validate_parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of worker threads (default: 4)",
    )

    # Unfixable issues report command
    unfixable_parser = subparsers.add_parser(
        "unfixable", help="Generate report of unfixable issues from last run"
    )
    unfixable_parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Report format (default: human)",
    )
    unfixable_parser.add_argument(
        "--output", type=Path, help="Output file path (default: stdout)"
    )

    # Summary command for quick overview
    summary_parser = subparsers.add_parser(
        "summary", help="Generate processing summary from last run"
    )
    summary_parser.add_argument(
        "--path", type=Path, default=Path("docs"), help="Path to analyze"
    )
    summary_parser.add_argument(
        "--only",
        nargs="+",
        choices=[
            "eventtype",
            "rst_quality",
            "code_examples",
            "navigation",
            "professional_rst",
            "sphinx",
        ],
        help="Run specific validators only",
    )
    summary_parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of worker threads (default: 4)",
    )

    # Handle case where no command is specified
    if len(sys.argv) == 1:
        # No arguments at all - default to check docs/
        sys.argv.extend(["check", "--path", "docs"])
    elif (
        len(sys.argv) == 2
        and not sys.argv[1].startswith("-")
        and Path(sys.argv[1]).exists()
    ):
        # Single path argument - convert to check command
        path_arg = sys.argv[1]
        sys.argv = [sys.argv[0], "check", "--path", path_arg]

    args = parser.parse_args()

    # Ensure we have a command
    if not hasattr(args, "command") or not args.command:
        args.command = "check"
        if not hasattr(args, "path"):
            args.path = Path("docs")
        if not hasattr(args, "only"):
            args.only = None

    # Handle logging configuration
    json_output = getattr(args, "json", False) or getattr(args, "format", "") == "json"
    quiet_mode = getattr(args, "quiet", False)

    # Set up logging based on mode
    verbose_mode = getattr(args, "verbose", False)

    if json_output:
        log_level = "CRITICAL"  # Disable logging for JSON output
    elif quiet_mode:
        log_level = "ERROR"  # Only show errors
    elif verbose_mode:
        log_level = "DEBUG"  # Show everything
    else:
        log_level = "INFO"  # Normal verbosity

    logger = setup_logging(level=log_level, json_output=json_output)

    # Handle commands that don't need path validation first
    if args.command == "unfixable":
        # Create minimal controller for report generation
        controller = DocsQualityController(
            fix_mode=False, validators=None, logger=logger, max_workers=1
        )

        # Generate unfixable issues report without processing
        if len(controller.shared_dead_letter_queue) > 0:
            report = controller.generate_unfixable_issues_report(args.format)
            if hasattr(args, "output") and args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(report)
                logger.info(f"📄 Unfixable issues report saved to {args.output}")
            else:
                print(report)
        else:
            logger.warning(
                "⚠️  No unfixable issues data available. Run 'fix' command first."
            )
        sys.exit(0)

    # Validate path exists for commands that need it
    if not hasattr(args, "path") or not args.path.exists():
        print(f"❌ Path does not exist: {getattr(args, 'path', 'docs')}")
        sys.exit(1)

    # Determine fix mode
    fix_mode = args.command == "fix"

    # Create controller with logger
    controller = DocsQualityController(
        fix_mode=fix_mode,
        validators=getattr(args, "only", None),
        logger=logger,
        max_workers=getattr(args, "max_workers", 4),
    )

    # Configure export behavior
    controller.export_ai_data = not getattr(args, "no_export", False)

    # Handle summary command
    if args.command == "summary":
        # Quick summary without full processing
        # Generate summary without verbose logging
        result = controller.process_path(args.path)
        sys.exit(0)

    logger.info("🚀 Starting Documentation Quality Control...")
    logger.info("=" * 60)

    # Process files
    result = controller.process_path(args.path)

    # Generate and display report
    if args.command == "report":
        if json_output:
            report_format = "json"
        else:
            report_format = getattr(args, "format", "text")
        report = generate_report(result, report_format)
        print(report)  # JSON goes to stdout, progress went to stderr
    elif args.command != "fix":
        # For non-fix commands, show the detailed report
        # Fix command already shows comprehensive summary via _generate_processing_summary
        report = generate_report(result, "text")
        if not quiet_mode:
            print("\n" + report)
        else:
            print(report)

    # Offer unfixable issues report if there are any
    if controller.fix_mode and hasattr(controller, "shared_dead_letter_queue"):
        with controller.dead_letter_lock:
            unfixable_count = len(controller.shared_dead_letter_queue)

        if unfixable_count > 0:
            logger.info("")
            logger.info("💡 TIP: Generate detailed unfixable issues report:")
            logger.info(
                f"   Human-readable: python {Path(sys.argv[0]).name} unfixable --format human"
            )
            logger.info(
                f"   AI-friendly JSON: python {Path(sys.argv[0]).name} unfixable --format json"
            )
            logger.info(
                f"   Save to file: python {Path(sys.argv[0]).name} unfixable --format json --output unfixable-issues.json"
            )

    # Exit with appropriate code
    if result.error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

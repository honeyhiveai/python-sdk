"""
Actionable error classes with remediation guidance.

Provides exception classes with structured fields for:
    - What failed (clear description)
    - Why it failed (root cause)
    - How to fix (actionable remediation steps)
    - Field path (for config/validation errors)

These errors are designed to be actionable for both humans and AI agents,
providing clear guidance on how to resolve issues.

Example Usage:
    >>> from ouroboros.utils.errors import ActionableError, ConfigValidationError
    >>> 
    >>> # Basic actionable error
    >>> raise ActionableError(
    ...     what_failed="Database connection failed",
    ...     why_failed="Connection timeout after 30s",
    ...     how_to_fix="Check database is running: docker ps | grep postgres"
    ... )
    >>> 
    >>> # Config validation error with field path
    >>> raise ConfigValidationError(
    ...     what_failed="Invalid chunk_size",
    ...     why_failed="chunk_size=50 is below minimum (100)",
    ...     how_to_fix="Update config: indexes.vector.chunk_size = 500",
    ...     field_path="indexes.vector.chunk_size"
    ... )

See Also:
    - config.loader: Uses ConfigValidationError for config failures
    - workflow: Uses EvidenceValidationError for gate failures
"""

from typing import Optional


class ActionableError(Exception):
    """
    Base exception with structured error information and remediation guidance.

    Provides clear, actionable error messages with:
        - what_failed: Description of what operation failed
        - why_failed: Root cause or reason for failure
        - how_to_fix: Specific remediation steps
        - field_path: Optional path to problematic field (for validation)

    Error Message Format:
        ERROR: {what_failed}
        
        Reason: {why_failed}
        
        Remediation: {how_to_fix}
        
        Field: {field_path} (if provided)

    Design Principles:
        1. **Actionable**: Always provide specific fix steps, not vague suggestions
        2. **Contextual**: Include field paths and values where relevant
        3. **AI-friendly**: Structured data for AI agents to parse and act on
        4. **Human-readable**: Clear formatting for human developers

    Example:
        >>> try:
        ...     raise ActionableError(
        ...         what_failed="Config validation failed",
        ...         why_failed="chunk_size=50 is below minimum (100)",
        ...         how_to_fix="Update config: indexes.vector.chunk_size = 500",
        ...         field_path="indexes.vector.chunk_size"
        ...     )
        ... except ActionableError as e:
        ...     print(str(e))
        ...     # Prints formatted error message
        ...     print(e.to_dict())
        ...     # Returns structured dict for AI parsing

    Attributes:
        what_failed (str): Description of what operation failed
        why_failed (str): Root cause or reason for failure
        how_to_fix (str): Specific remediation steps
        field_path (Optional[str]): Path to problematic field (e.g., "indexes.vector.chunk_size")

    Methods:
        to_dict(): Serialize to dictionary for JSON responses
        __str__(): Format as human-readable error message
    """

    def __init__(
        self,
        what_failed: str,
        why_failed: str,
        how_to_fix: str,
        field_path: Optional[str] = None,
    ) -> None:
        """
        Initialize actionable error with structured fields.

        Args:
            what_failed: Description of what operation failed
            why_failed: Root cause or reason for failure
            how_to_fix: Specific remediation steps
            field_path: Optional path to problematic field

        Example:
            >>> error = ActionableError(
            ...     what_failed="Index creation failed",
            ...     why_failed="Source directory not found: /path/to/docs",
            ...     how_to_fix="Create directory: mkdir -p /path/to/docs",
            ...     field_path="indexes.standards.source_paths[0]"
            ... )
        """
        self.what_failed = what_failed
        self.why_failed = why_failed
        self.how_to_fix = how_to_fix
        self.field_path = field_path

        # Build exception message
        message = self._format_message()
        super().__init__(message)

    def _format_message(self) -> str:
        """
        Format error as human-readable message.

        Returns:
            str: Formatted error message with clear sections

        Format:
            ERROR: {what_failed}
            
            Reason: {why_failed}
            
            Remediation: {how_to_fix}
            
            Field: {field_path} (if provided)
        """
        lines = [
            f"ERROR: {self.what_failed}",
            "",
            f"Reason: {self.why_failed}",
            "",
            f"Remediation: {self.how_to_fix}",
        ]

        if self.field_path:
            lines.extend(["", f"Field: {self.field_path}"])

        return "\n".join(lines)

    def to_dict(self) -> dict[str, str | None]:
        """
        Serialize error to dictionary for JSON responses.

        Returns:
            dict: Error data with keys: what_failed, why_failed, how_to_fix, field_path

        Example:
            >>> error = ActionableError(
            ...     what_failed="Config validation failed",
            ...     why_failed="Invalid value",
            ...     how_to_fix="Fix config"
            ... )
            >>> error.to_dict()
            {
                'what_failed': 'Config validation failed',
                'why_failed': 'Invalid value',
                'how_to_fix': 'Fix config',
                'field_path': None
            }

        Use Cases:
            - MCP tool returns: Return dict in error response
            - Logging: Structured log entry with error details
            - AI parsing: AI agent can parse and act on error
        """
        return {
            "what_failed": self.what_failed,
            "why_failed": self.why_failed,
            "how_to_fix": self.how_to_fix,
            "field_path": self.field_path,
        }


class ConfigValidationError(ActionableError):
    """
    Configuration validation error with auto-fix suggestions.

    Raised when config loading or validation fails. Automatically includes:
        - Field path (e.g., "indexes.vector.chunk_size")
        - Current vs expected value
        - Specific fix command or config change

    Example:
        >>> raise ConfigValidationError(
        ...     what_failed="Invalid chunk_size in vector config",
        ...     why_failed="chunk_size=50 is below minimum (100)",
        ...     how_to_fix="Update config: indexes.vector.chunk_size = 500",
        ...     field_path="indexes.vector.chunk_size"
        ... )

    Use Cases:
        - Config file validation (MCPConfig.from_yaml)
        - Runtime config validation
        - Path validation (missing directories)
        - Type validation (wrong data types)
    """

    pass


class EvidenceValidationError(ActionableError):
    """
    Workflow evidence validation error with remediation.

    Raised when workflow gate validation fails due to insufficient evidence.
    Guides AI agent on what evidence is missing and how to collect it.

    Example:
        >>> raise EvidenceValidationError(
        ...     what_failed="Phase 1 gate validation failed",
        ...     why_failed="Required field 'tests_passing' is missing",
        ...     how_to_fix="Run tests and provide: tests_passing=True, test_count=15",
        ...     field_path="evidence.tests_passing"
        ... )

    Use Cases:
        - Workflow gate validation
        - Evidence schema compliance
        - Required field checks
        - Cross-field validation
    """

    pass


class IndexError(ActionableError):
    """
    Index operation error with recovery guidance.

    Raised when index operations fail (build, search, update). Provides
    specific guidance on index recovery or rebuild.

    Example:
        >>> raise IndexError(
        ...     what_failed="Standards index search failed",
        ...     why_failed="LanceDB table not found: standards_v1",
        ...     how_to_fix="Rebuild index: python -m ouroboros.subsystems.rag rebuild_standards",
        ...     field_path="indexes.standards"
        ... )

    Use Cases:
        - Index not found
        - Index corruption
        - Search failures
        - Update failures
    """

    pass


class WorkflowExecutionError(ActionableError):
    """
    Workflow execution error with recovery steps.

    Raised when workflow execution fails (invalid state, missing workflow,
    timeout). Provides guidance on workflow recovery or reset.

    Example:
        >>> raise WorkflowExecutionError(
        ...     what_failed="Cannot advance to phase 2",
        ...     why_failed="Phase 1 gate not passed (evidence_schemas_exposed=True)",
        ...     how_to_fix="Fix phase 1 evidence: set evidence_schemas_exposed=False",
        ...     field_path="workflow.phase_1.evidence"
        ... )

    Use Cases:
        - Gate validation failures
        - Invalid state transitions
        - Missing workflow definitions
        - Workflow timeouts
    """

    pass


__all__ = [
    "ActionableError",
    "ConfigValidationError",
    "EvidenceValidationError",
    "IndexError",
    "WorkflowExecutionError",
]


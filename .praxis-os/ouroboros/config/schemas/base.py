"""
Base configuration models and shared validation for Ouroboros.

Provides foundational Pydantic v2 models, enums, and validation utilities
that all other configuration schemas inherit from. Implements fail-fast
validation with actionable error messages.

Key Components:
    - EnvType: Environment enum (development, production, test)
    - BaseConfig: Base Pydantic model with shared validation
    - Path resolution utilities for .praxis-os/ relative paths

Design Principles:
    1. Fail-Fast: Invalid values crash immediately at startup
    2. Clear Errors: Error messages include field paths and remediation
    3. Type-Safe: All fields fully typed for IDE support
    4. Immutable: frozen=True prevents runtime mutation
    5. Validated: Cross-field and constraint validation

Example Usage:
    >>> from ouroboros.config.schemas.base import BaseConfig, EnvType
    >>> from pydantic import Field
    >>> 
    >>> class MyConfig(BaseConfig):
    ...     name: str = Field(description="Service name", min_length=1)
    ...     port: int = Field(ge=1024, le=65535, default=8080)
    ...     env: EnvType = Field(default=EnvType.DEVELOPMENT)
    >>> 
    >>> # Valid config
    >>> config = MyConfig(name="my-service", port=3000)
    >>> 
    >>> # Invalid config (fails fast with clear error)
    >>> try:
    ...     bad_config = MyConfig(name="", port=80)  # name empty, port < 1024
    ... except ValidationError as e:
    ...     print(e)  # Shows field paths and constraints violated

See Also:
    - Pydantic v2 docs: https://docs.pydantic.dev/latest/
    - Field constraints: https://docs.pydantic.dev/latest/concepts/fields/
    - Custom validators: https://docs.pydantic.dev/latest/concepts/validators/
"""

from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EnvType(str, Enum):
    """
    Environment type for server configuration.

    Determines behavior for different deployment environments:
        - DEVELOPMENT: Local development, verbose logging, debug enabled
        - PRODUCTION: Production deployment, optimized, security hardened
        - TEST: Test environment, isolated state, deterministic behavior

    Used to:
        - Configure logging levels (DEBUG in dev, INFO in prod)
        - Enable/disable debug features
        - Set validation strictness
        - Configure performance optimizations

    Example:
        >>> from ouroboros.config.schemas.base import EnvType
        >>> env = EnvType.DEVELOPMENT
        >>> print(env.value)  # "development"
        >>> is_prod = (env == EnvType.PRODUCTION)  # False
    """

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class BaseConfig(BaseModel):
    """
    Base configuration model with shared validation and settings.

    All Ouroboros configuration schemas inherit from this base class to ensure
    consistent validation behavior, error handling, and immutability.

    Features:
        - Fail-fast validation (invalid config crashes at startup)
        - Immutable after creation (frozen=True prevents mutation)
        - Unknown fields forbidden (extra="forbid" catches typos)
        - Clear error messages (field paths with constraints)
        - Type-safe access (dot-notation, IDE autocomplete)

    Configuration Options (via ConfigDict):
        - frozen: True - Immutable after creation
        - extra: "forbid" - Reject unknown fields (catches typos)
        - validate_assignment: True - Validate on attribute assignment
        - arbitrary_types_allowed: False - Strict type checking
        - str_strip_whitespace: True - Auto-trim string fields
        - validate_default: True - Validate default values

    Path Resolution:
        All relative paths are resolved relative to .praxis-os/ directory:
            - "standards/" → ".praxis-os/standards/"
            - "config/mcp.yaml" → ".praxis-os/config/mcp.yaml"

    Error Handling:
        Validation errors include:
            - Field path (e.g., "indexes.standards.vector.model")
            - Constraint violated (e.g., "must be >= 100")
            - Actual value provided
            - Expected type/format

    Example:
        >>> from ouroboros.config.schemas.base import BaseConfig
        >>> from pydantic import Field
        >>> 
        >>> class ServiceConfig(BaseConfig):
        ...     name: str = Field(description="Service name", min_length=1)
        ...     port: int = Field(ge=1024, le=65535, default=8080)
        >>> 
        >>> # Valid
        >>> config = ServiceConfig(name="api", port=3000)
        >>> 
        >>> # Invalid (fails fast)
        >>> try:
        ...     bad = ServiceConfig(name="", port=99999)
        ... except ValidationError as e:
        ...     # Error shows: "name: String should have at least 1 characters"
        ...     # Error shows: "port: Input should be less than or equal to 65535"
        ...     pass

    Immutability Example:
        >>> config = ServiceConfig(name="api", port=3000)
        >>> config.port = 4000  # Raises ValidationError: frozen instance

    Unknown Field Example:
        >>> try:
        ...     bad = ServiceConfig(name="api", invalid_field="value")
        ... except ValidationError as e:
        ...     # Error: "Extra inputs are not permitted"
        ...     pass

    See Also:
        - Pydantic ConfigDict: https://docs.pydantic.dev/latest/api/config/
        - Field constraints: https://docs.pydantic.dev/latest/concepts/fields/
    """

    # Pydantic v2 configuration
    model_config = ConfigDict(
        frozen=True,  # Immutable after creation (prevents runtime mutation)
        extra="forbid",  # Reject unknown fields (catches typos in YAML)
        validate_assignment=True,  # Validate on attribute assignment
        arbitrary_types_allowed=False,  # Strict type checking
        str_strip_whitespace=True,  # Auto-trim whitespace from strings
        validate_default=True,  # Validate default values
    )

    # Base path for resolving relative paths (class variable)
    _base_path: ClassVar[Path] = Path(".praxis-os")

    @classmethod
    def resolve_path(cls, path: str | Path) -> Path:
        """
        Resolve a path relative to .praxis-os/ directory.

        Converts relative paths to absolute paths based on .praxis-os/
        base directory. Prevents path traversal attacks and ensures
        all paths are canonical.

        Args:
            path: Relative path string or Path object
                  Examples: "standards/", "config/mcp.yaml"

        Returns:
            Path: Absolute resolved path
                  Example: Path("/project/.praxis-os/standards/")

        Raises:
            ValueError: If path contains path traversal (../)
            ValueError: If path is absolute (must be relative)

        Security:
            - Rejects path traversal attempts (../)
            - Rejects absolute paths
            - Canonicalizes path (resolves symlinks)

        Example:
            >>> from ouroboros.config.schemas.base import BaseConfig
            >>> 
            >>> # Relative path resolution
            >>> path = BaseConfig.resolve_path("standards/")
            >>> print(path)  # /project/.praxis-os/standards/
            >>> 
            >>> # Path traversal rejected
            >>> try:
            ...     bad_path = BaseConfig.resolve_path("../secrets/")
            ... except ValueError as e:
            ...     print(e)  # "Path traversal not allowed: ../secrets/"
            >>> 
            >>> # Absolute path rejected
            >>> try:
            ...     bad_path = BaseConfig.resolve_path("/etc/passwd")
            ... except ValueError as e:
            ...     print(e)  # "Absolute paths not allowed: /etc/passwd"

        See Also:
            - pathlib.Path: https://docs.python.org/3/library/pathlib.html
            - Path security: OWASP Path Traversal Prevention
        """
        path_obj = Path(path)

        # Security: Reject absolute paths
        if path_obj.is_absolute():
            raise ValueError(
                f"Absolute paths not allowed: {path}\n"
                f"Remediation: Use relative paths (e.g., 'standards/' instead of '{path}')"
            )

        # Security: Reject path traversal
        if ".." in path_obj.parts:
            raise ValueError(
                f"Path traversal not allowed: {path}\n"
                f"Remediation: Remove '../' from path. All paths are relative to .praxis-os/"
            )

        # Resolve relative to .praxis-os/
        resolved = (cls._base_path / path_obj).resolve()

        return resolved

    @field_validator("*", mode="before")
    @classmethod
    def strip_strings(cls, value: Any) -> Any:
        """
        Strip whitespace from all string fields.

        Applied to all string fields automatically before validation.
        Prevents common user errors like trailing spaces in YAML.

        Args:
            value: Field value (any type)

        Returns:
            Any: Stripped string if value is str, otherwise unchanged

        Example:
            >>> class MyConfig(BaseConfig):
            ...     name: str
            >>> 
            >>> config = MyConfig(name="  test  ")
            >>> print(config.name)  # "test" (whitespace stripped)
        """
        if isinstance(value, str):
            return value.strip()
        return value


__all__ = [
    "EnvType",
    "BaseConfig",
]


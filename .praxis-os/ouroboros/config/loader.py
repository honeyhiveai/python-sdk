"""
Configuration loading utilities for Ouroboros MCP server.

Provides high-level functions for loading and validating configuration with:
    - Automatic path resolution
    - Clear error messages with remediation
    - Optional path validation
    - Environment-specific config overrides

The loader wraps MCPConfig.from_yaml() with additional error handling and
convenience features for production use.

Example Usage:
    >>> from ouroboros.config.loader import load_config, find_config_file
    >>> 
    >>> # Simple load
    >>> config = load_config()
    >>> 
    >>> # Custom path
    >>> config = load_config(Path("custom/config.yaml"))
    >>> 
    >>> # Skip path validation (testing)
    >>> config = load_config(validate_paths=False)

See Also:
    - schemas.mcp.MCPConfig: Root configuration model
    - schemas.base.BaseConfig: Base configuration class
"""

import sys
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from ouroboros.config.schemas.mcp import MCPConfig


def find_config_file(start_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Find mcp.yaml config file by searching upward from start_dir.

    Searches for .praxis-os/config/mcp.yaml starting from start_dir and
    walking up the directory tree until found or filesystem root reached.

    This allows running Ouroboros from any subdirectory of the project.

    Args:
        start_dir: Directory to start search from (default: cwd)

    Returns:
        Path to mcp.yaml if found, None otherwise

    Example:
        >>> from ouroboros.config.loader import find_config_file
        >>> 
        >>> # Find from current directory
        >>> config_path = find_config_file()
        >>> if config_path:
        ...     print(f"Found config: {config_path}")
        ... else:
        ...     print("Config not found")
        >>> 
        >>> # Find from specific directory
        >>> config_path = find_config_file(Path("/path/to/project/subdir"))

    Search Strategy:
        1. Check start_dir/.praxis-os/config/mcp.yaml
        2. Check parent/.praxis-os/config/mcp.yaml
        3. Repeat until found or root reached
        4. Return None if not found

    Use Cases:
        - Running MCP server from project subdirectory
        - Running tests from tests/ directory
        - Running scripts from scripts/ directory
        - Monorepo with multiple projects
    """
    current = (start_dir or Path.cwd()).resolve()

    # Walk up directory tree
    for parent in [current] + list(current.parents):
        config_path = parent / ".praxis-os" / "config" / "mcp.yaml"
        if config_path.exists():
            return config_path

    return None


def load_config(
    config_path: Optional[Path] = None,
    validate_paths: bool = True,
    auto_find: bool = True,
) -> MCPConfig:
    """
    Load and validate MCP configuration with enhanced error handling.

    High-level config loading function that wraps MCPConfig.from_yaml()
    with additional features:
        - Automatic config file discovery
        - Path existence validation
        - Clear error messages with remediation
        - Graceful error handling

    Args:
        config_path: Path to mcp.yaml (default: auto-discover)
        validate_paths: Validate paths exist (default: True)
        auto_find: Auto-discover config if path not provided (default: True)

    Returns:
        MCPConfig: Validated configuration instance

    Raises:
        FileNotFoundError: If config file not found
        ValidationError: If config validation fails
        ValueError: If config has invalid values
        SystemExit: If validation fails and no recovery possible

    Example:
        >>> from ouroboros.config.loader import load_config
        >>> 
        >>> # Simple load (auto-discover)
        >>> try:
        ...     config = load_config()
        ... except SystemExit:
        ...     print("Config load failed, exiting")
        >>> 
        >>> # Custom path
        >>> config = load_config(Path(".praxis-os/config/mcp.yaml"))
        >>> 
        >>> # Skip path validation (testing)
        >>> config = load_config(validate_paths=False)
        >>> 
        >>> # Explicit path, no auto-find
        >>> config = load_config(
        ...     config_path=Path("config.yaml"),
        ...     auto_find=False
        ... )

    Error Handling:
        All errors include:
            - Problem description
            - Current vs expected state
            - Remediation steps
            - Reference documentation

        Examples:
            - Missing file → FileNotFoundError with config location
            - Invalid YAML → ValueError with line number
            - Validation error → ValidationError with field path
            - Missing paths → ValueError with list of missing paths

    Auto-Discovery:
        If config_path is None and auto_find=True:
            1. Search upward from cwd for .praxis-os/config/mcp.yaml
            2. If found, load from that path
            3. If not found, raise FileNotFoundError

    Path Validation:
        If validate_paths=True (default):
            1. Load and validate config schema
            2. Check all configured paths exist
            3. Report missing paths with remediation
            4. Raise ValueError if any paths missing

        If validate_paths=False:
            Skip path existence checks (useful for testing)

    Production Usage:
        ```python
        from ouroboros.config.loader import load_config
        import sys
        
        try:
            config = load_config()
        except Exception as e:
            print(f"FATAL: Config load failed: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Config loaded successfully, start server
        ```

    Testing Usage:
        ```python
        from ouroboros.config.loader import load_config
        
        # Load test config without path validation
        config = load_config(
            config_path=Path("tests/fixtures/test_config.yaml"),
            validate_paths=False
        )
        ```
    """
    # Resolve config path
    if config_path is None:
        if auto_find:
            config_path = find_config_file()
            if config_path is None:
                print(
                    "ERROR: Could not find mcp.yaml config file\n"
                    "Searched upward from current directory for .praxis-os/config/mcp.yaml\n"
                    "Remediation:\n"
                    "  1. Create .praxis-os/config/mcp.yaml in your project root\n"
                    "  2. Or run from a directory within your praxis-os project\n"
                    "  3. Or specify explicit path: load_config(Path('path/to/config.yaml'))",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            # Default path if no auto-find
            config_path = Path(".praxis-os/config/mcp.yaml")

    # Load and validate config
    try:
        config = MCPConfig.from_yaml(config_path)
    except FileNotFoundError as e:
        print(
            f"ERROR: Config file not found: {config_path}\n"
            f"Remediation:\n"
            f"  1. Create config file at {config_path}\n"
            f"  2. Or specify different path: load_config(Path('your/config.yaml'))\n"
            f"  3. See .praxis-os/config/mcp.yaml.example for template",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValidationError as e:
        print(
            f"ERROR: Config validation failed for {config_path}\n"
            f"\n{e}\n"
            f"\nRemediation:\n"
            f"  1. Fix validation errors in {config_path}\n"
            f"  2. Check field names, types, and constraints\n"
            f"  3. See error messages above for specific issues",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError as e:
        print(
            f"ERROR: Invalid config values in {config_path}\n"
            f"{e}\n"
            f"\nRemediation:\n"
            f"  1. Fix invalid values in {config_path}\n"
            f"  2. Check YAML syntax and data types",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate paths exist
    if validate_paths:
        path_errors = config.validate_paths()
        if path_errors:
            print(
                f"ERROR: Config path validation failed\n"
                f"\nMissing or invalid paths:\n",
                file=sys.stderr,
            )
            for error in path_errors:
                print(f"  - {error}", file=sys.stderr)
            print(
                f"\nRemediation:\n"
                f"  1. Create missing directories\n"
                f"  2. Or update paths in {config_path}\n"
                f"  3. Or skip path validation: load_config(validate_paths=False)",
                file=sys.stderr,
            )
            sys.exit(1)

    return config


__all__ = ["find_config_file", "load_config"]


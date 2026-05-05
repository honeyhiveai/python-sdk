"""Git information and telemetry utilities.

This module provides dynamic git information collection and telemetry
management using flexible, environment-aware logic patterns.
"""

import os
import subprocess
import sys
from typing import Any, Dict, Optional

# Import shared logging utility
from ...utils.logger import safe_log


def is_telemetry_enabled(tracer_instance: Any = None) -> bool:
    """Dynamically check if telemetry collection is enabled.

    Uses dynamic environment variable analysis to determine telemetry status
    with intelligent default handling and flexible configuration patterns.

    Returns:
        True if telemetry is enabled, False otherwise

    Example:
        >>> if is_telemetry_enabled():
        ...     git_info = get_git_information()
        ... else:
        ...     print("Telemetry disabled")
    """
    # Dynamic telemetry setting detection
    telemetry_setting = _get_telemetry_setting_dynamically(tracer_instance)

    # Dynamic boolean conversion with multiple patterns
    return _convert_to_boolean_dynamically(
        telemetry_setting, default=True, tracer_instance=tracer_instance
    )


def _get_telemetry_setting_dynamically(tracer_instance: Any = None) -> str:
    """Dynamically get telemetry setting from environment.

    Returns:
        Telemetry setting string
    """
    # Dynamic environment variable patterns
    env_var_patterns = [
        "HONEYHIVE_TELEMETRY",
        "HH_TELEMETRY",
        "TELEMETRY_ENABLED",
    ]

    # Check each pattern dynamically
    for env_var in env_var_patterns:
        value = os.getenv(env_var)
        if value is not None:
            safe_log(
                tracer_instance,
                "debug",
                "Found telemetry setting",
                honeyhive_data={
                    "env_var": env_var,
                    "value": value,
                },
            )
            return value.lower()

    # Default when no setting found
    return "true"


def _convert_to_boolean_dynamically(
    value: str, default: bool = True, tracer_instance: Any = None
) -> bool:
    """Dynamically convert string value to boolean.

    Args:
        value: String value to convert
        default: Default value if conversion fails

    Returns:
        Boolean representation
    """
    # Dynamic false patterns
    false_patterns = ["false", "0", "f", "no", "n", "off", "disabled"]

    # Dynamic true patterns
    true_patterns = ["true", "1", "t", "yes", "y", "on", "enabled"]

    value_lower = value.lower().strip()

    if value_lower in false_patterns:
        return False
    if value_lower in true_patterns:
        return True
    # Dynamic default handling
    safe_log(
        tracer_instance,
        "debug",
        "Unknown telemetry value, using default",
        honeyhive_data={
            "value": value,
            "default": default,
        },
    )
    return default


def get_git_information(
    verbose: bool = False, tracer_instance: Any = None
) -> Dict[str, Any]:
    """Dynamically collect git information for session metadata.

    Uses dynamic git command execution and intelligent error handling
    to gather comprehensive repository information while respecting
    telemetry settings and environment constraints.

    Args:
        verbose: Whether to enable verbose logging

    Returns:
        Dictionary containing git information or error details

    Example:
        >>> git_info = get_git_information(verbose=True)
        >>> if "error" not in git_info:
        ...     print(f"Commit: {git_info['commit_hash']}")
        ...     print(f"Branch: {git_info['branch']}")
    """
    try:
        # Dynamic telemetry check
        if not is_telemetry_enabled(tracer_instance):
            if verbose:
                safe_log(
                    tracer_instance,
                    "debug",
                    "Telemetry disabled. Skipping git information collection.",
                )
            return {"error": "Telemetry disabled"}

        # Dynamic git repository validation
        if not _is_git_repository_dynamically():
            if verbose:
                safe_log(
                    tracer_instance,
                    "debug",
                    "Not a git repository. Skipping git information collection.",
                )
            return {"error": "Not a git repository"}

        # Dynamic git information collection
        git_info = _collect_git_information_dynamically(verbose)

        if verbose:
            _log_git_collection_success_dynamically(git_info)

        return git_info

    except subprocess.CalledProcessError as e:
        return _handle_git_command_error_dynamically(e, verbose)
    except FileNotFoundError:
        return _handle_git_not_found_error_dynamically(verbose)
    except Exception as e:
        return _handle_unexpected_git_error_dynamically(e, verbose)


def _is_git_repository_dynamically() -> bool:
    """Dynamically check if current directory is a git repository.

    Returns:
        True if git repository, False otherwise
    """
    try:
        cwd = os.getcwd()
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def _collect_git_information_dynamically(verbose: bool) -> Dict[str, Any]:
    """Dynamically collect all git information.

    Args:
        verbose: Whether to enable verbose logging

    Returns:
        Dictionary with git information
    """
    cwd = os.getcwd()
    git_info: Dict[str, Any] = {}

    # Dynamic information collection pipeline
    collection_steps = [
        ("commit_hash", lambda: _get_git_commit_hash_dynamically(cwd)),
        ("branch", lambda: _get_git_branch_dynamically(cwd)),
        ("repo_url", lambda: _get_git_repo_url_dynamically(cwd)),
        ("uncommitted_changes", lambda: _has_uncommitted_changes_dynamically(cwd)),
        ("relative_path", lambda: _get_main_module_relative_path_dynamically(cwd)),
    ]

    # Execute collection steps dynamically
    for key, collector in collection_steps:
        try:
            git_info[key] = collector()
        except Exception as e:
            if verbose:
                safe_log(
                    None,  # Internal helper function - use fallback logging
                    "warning",
                    f"Failed to collect {key}",
                    honeyhive_data={
                        "key": key,
                        "error": str(e),
                    },
                )
            git_info[key] = None

    # Dynamic commit link generation
    if git_info.get("repo_url") and git_info.get("commit_hash"):
        git_info["commit_link"] = _generate_commit_link_dynamically(
            git_info["repo_url"], git_info["commit_hash"]
        )

    return git_info


def _get_git_commit_hash_dynamically(cwd: str) -> Optional[str]:
    """Dynamically get the current git commit hash.

    Args:
        cwd: Current working directory

    Returns:
        Full commit hash
    """
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _get_git_branch_dynamically(cwd: str) -> Optional[str]:
    """Dynamically get the current git branch name.

    Args:
        cwd: Current working directory

    Returns:
        Branch name
    """
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _get_git_repo_url_dynamically(cwd: str) -> Optional[str]:
    """Dynamically get the git repository URL.

    Args:
        cwd: Current working directory

    Returns:
        Repository URL without .git suffix
    """
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().rstrip(".git")


def _generate_commit_link_dynamically(repo_url: str, commit_hash: str) -> str:
    """Dynamically generate a direct link to the commit.

    Uses dynamic provider detection to generate appropriate commit links
    for different git hosting services.

    Args:
        repo_url: Repository URL
        commit_hash: Commit hash

    Returns:
        Direct link to commit or repository URL
    """
    # Dynamic provider detection patterns
    provider_patterns = [
        ("github.com", lambda url, hash: f"{url}/commit/{hash}"),
        ("gitlab.com", lambda url, hash: f"{url}/-/commit/{hash}"),
        ("bitbucket.org", lambda url, hash: f"{url}/commits/{hash}"),
    ]

    # Apply dynamic pattern matching
    for provider, link_generator in provider_patterns:
        if provider in repo_url:
            try:
                return link_generator(repo_url, commit_hash)
            except Exception:
                # Fallback to repo URL if link generation fails
                break

    # Default fallback
    return repo_url


def _has_uncommitted_changes_dynamically(cwd: str) -> bool:
    """Dynamically check if there are uncommitted changes in the repository.

    Args:
        cwd: Current working directory

    Returns:
        True if there are uncommitted changes, False otherwise
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return bool(result.stdout.strip())


def _get_main_module_relative_path_dynamically(cwd: str) -> Optional[str]:
    """Dynamically get the relative path of the main module from repository root.

    Args:
        cwd: Current working directory

    Returns:
        Relative path of main module or None if not available
    """
    try:
        # Dynamic repository root detection
        repo_root = _get_repository_root_dynamically(cwd)
        if not repo_root:
            return None

        # Dynamic main module path detection
        main_module_path = _get_main_module_path_dynamically()
        if not main_module_path:
            return None

        # Dynamic relative path calculation
        return os.path.relpath(main_module_path, repo_root)

    except Exception:
        return None


def _get_repository_root_dynamically(cwd: str) -> Optional[str]:
    """Dynamically get git repository root.

    Args:
        cwd: Current working directory

    Returns:
        Repository root path or None
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def _get_main_module_path_dynamically() -> Optional[str]:
    """Dynamically get main module absolute path.

    Returns:
        Main module path or None
    """
    try:
        main_module = sys.modules.get("__main__")
        if main_module and hasattr(main_module, "__file__") and main_module.__file__:
            return os.path.abspath(main_module.__file__)
        return None
    except Exception:
        return None


def _log_git_collection_success_dynamically(git_info: Dict[str, Any]) -> None:
    """Dynamically log successful git information collection.

    Args:
        git_info: Collected git information
    """
    # Dynamic logging data preparation
    log_data = {}

    if git_info.get("commit_hash"):
        log_data["commit_hash"] = git_info["commit_hash"][:8]  # Short hash

    if git_info.get("branch"):
        log_data["branch"] = git_info["branch"]

    if "uncommitted_changes" in git_info:
        log_data["has_changes"] = git_info["uncommitted_changes"]

    safe_log(
        None,  # Internal helper function - use fallback logging
        "debug",
        "Git information collected successfully",
        honeyhive_data=log_data,
    )


def _handle_git_command_error_dynamically(
    error: subprocess.CalledProcessError, verbose: bool
) -> Dict[str, str]:
    """Dynamically handle git command errors.

    Args:
        error: CalledProcessError from git command
        verbose: Whether to log verbosely

    Returns:
        Error information dictionary
    """
    error_msg = "Failed to retrieve Git info. Is this a valid repo?"

    if verbose:
        safe_log(
            None,  # Internal helper function - use fallback logging
            "warning",
            error_msg,
            honeyhive_data={
                "return_code": error.returncode,
                "command": " ".join(error.cmd) if error.cmd else "unknown",
            },
        )

    return {"error": error_msg}


def _handle_git_not_found_error_dynamically(verbose: bool) -> Dict[str, str]:
    """Dynamically handle git not found errors.

    Args:
        verbose: Whether to log verbosely

    Returns:
        Error information dictionary
    """
    error_msg = "Git is not installed or not in PATH."

    if verbose:
        safe_log(
            None, "warning", error_msg
        )  # Internal helper function - use fallback logging

    return {"error": error_msg}


def _handle_unexpected_git_error_dynamically(
    error: Exception, verbose: bool
) -> Dict[str, str]:
    """Dynamically handle unexpected git errors.

    Args:
        error: Unexpected exception
        verbose: Whether to log verbosely

    Returns:
        Error information dictionary
    """
    error_msg = f"Error getting git info: {error}"

    if verbose:
        safe_log(
            None,  # Internal helper function - use fallback logging
            "error",
            "Unexpected error collecting git info",
            honeyhive_data={
                "error": str(error),
                "error_type": type(error).__name__,
            },
        )

    return {"error": error_msg}

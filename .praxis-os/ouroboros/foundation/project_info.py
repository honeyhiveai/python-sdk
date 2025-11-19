"""
Project information discovery for MCP server dual-transport.

This module provides dynamic discovery of project metadata without any
hardcoded values, supporting both git and non-git projects.

Traceability:
    FR-026: Dual-Transport Support
    NFR-O1: Structured Logging (project metadata)
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ProjectInfoDiscovery:
    """
    Discovers project information dynamically at runtime.

    All information is discovered via:
    - Git commands (subprocess with timeout)
    - Filesystem operations
    - NO hardcoded values or machine-specific paths

    Provides graceful fallbacks for non-git projects and git command failures.

    Example:
        >>> from pathlib import Path
        >>> discovery = ProjectInfoDiscovery(Path(".praxis-os"))
        >>> info = discovery.get_project_info()
        >>> print(f"Project: {info['name']}")
        >>> print(f"Root: {info['root']}")
    """

    def __init__(self, base_path: Path):
        """
        Initialize project info discovery.

        Args:
            base_path: Path to .praxis-os directory
        """
        self.base_path = base_path
        self.project_root = base_path.parent  # Discovered from filesystem

    def get_project_info(self) -> Dict:
        """
        Get comprehensive project information (dynamic discovery).

        Discovers:
        - Project name (from git remote or directory name)
        - Project root path (from filesystem)
        - Git repository info (if available, None otherwise)
        - prAxIs OS path

        ALL values discovered at runtime - no hardcoded values.

        Returns:
            Project information dictionary:
            {
                "name": str,               # Project name (dynamic)
                "root": str,               # Absolute path to project root
                "praxis_os_path": str,      # Absolute path to .praxis-os
                "git": dict | None         # Git info or None if not git repo
            }

        Example:
            >>> info = discovery.get_project_info()
            >>> if info["git"]:
            ...     print(f"Branch: {info['git']['branch']}")
        """
        return {
            "name": self._get_project_name(),
            "root": str(self.project_root),
            "praxis_os_path": str(self.base_path),
            "git": self._get_git_info(),
        }

    def _get_project_name(self) -> str:
        """
        Get project name dynamically.

        Priority:
        1. Git repository name (extracted from remote URL)
        2. Directory name (fallback for non-git projects)

        Examples:
            git@github.com:user/praxis-os-enhanced.git → "praxis-os-enhanced"
            https://github.com/user/my-project.git → "my-project"
            /home/user/my-project/ → "my-project"

        Returns:
            Project name (NEVER hardcoded)
        """
        git_name = self._get_git_repo_name()
        if git_name:
            return git_name

        # Fallback to directory name
        return self.project_root.name

    def _get_git_repo_name(self) -> Optional[str]:
        """
        Extract repository name from git remote URL.

        Supports multiple URL formats:
        - SSH: git@github.com:user/repo.git
        - HTTPS: https://github.com/user/repo.git
        - HTTPS no .git: https://github.com/user/repo

        Returns:
            Repository name or None if not a git repo

        Example:
            >>> name = discovery._get_git_repo_name()
            >>> print(name)  # e.g., "praxis-os-enhanced"
        """
        remote = self._get_git_remote()
        if not remote:
            return None

        # Extract name from various URL formats
        # git@github.com:user/repo.git → repo
        # https://github.com/user/repo.git → repo
        match = re.search(r"/([^/]+?)(?:\.git)?$", remote)
        if match:
            return match.group(1)

        return None

    def _get_git_info(self) -> Optional[Dict]:
        """
        Get git repository information dynamically.

        Runs git commands to discover:
        - remote: Git remote URL (origin)
        - branch: Current branch name
        - commit: Full commit hash (40 chars)
        - commit_short: Short commit hash (7 chars)
        - status: "clean" or "dirty" based on working tree

        Returns None gracefully for non-git repositories or if any
        git command fails (timeout, error, etc.).

        Returns:
            Git information dict or None:
            {
                "remote": str,
                "branch": str,
                "commit": str,
                "commit_short": str,
                "status": "clean" | "dirty"
            }

        Example:
            >>> git_info = discovery._get_git_info()
            >>> if git_info:
            ...     print(f"On {git_info['branch']} at {git_info['commit_short']}")
        """
        if not self._is_git_repo():
            return None

        # Gather all git information
        remote = self._get_git_remote()
        branch = self._get_git_branch()
        commit = self._get_git_commit()
        status = self._get_git_status()

        # If any critical field is None, return None
        if not all([remote, branch, commit]):
            return None

        return {
            "remote": remote,
            "branch": branch,
            "commit": commit,
            "commit_short": commit[:7] if commit else None,
            "status": status if status else "unknown",
        }

    def _is_git_repo(self) -> bool:
        """
        Check if project is a git repository.

        Returns:
            True if .git directory exists, False otherwise
        """
        return (self.project_root / ".git").exists()

    def _get_git_remote(self) -> Optional[str]:
        """
        Get git remote URL (origin).

        Returns:
            Remote URL or None if failed
        """
        return self._run_git_command(["remote", "get-url", "origin"])

    def _get_git_branch(self) -> Optional[str]:
        """
        Get current git branch name.

        Returns:
            Branch name or None if failed
        """
        return self._run_git_command(["branch", "--show-current"])

    def _get_git_commit(self) -> Optional[str]:
        """
        Get current git commit hash (full).

        Returns:
            Commit hash (40 chars) or None if failed
        """
        return self._run_git_command(["rev-parse", "HEAD"])

    def _get_git_status(self) -> Optional[str]:
        """
        Get git working tree status.

        Returns:
            "clean" if no changes, "dirty" if changes, None if failed
        """
        output = self._run_git_command(["status", "--porcelain"])
        if output is None:
            return None

        # Empty output means clean, any output means dirty
        return "clean" if not output.strip() else "dirty"

    def _run_git_command(self, args: list) -> Optional[str]:
        """
        Run git command with timeout and error handling.

        Provides robust execution with:
        - 5 second timeout (prevents hanging)
        - Graceful error handling (returns None on failure)
        - Working directory set to project root
        - Captures stdout as text

        Args:
            args: Git command arguments (e.g., ["status", "--porcelain"])

        Returns:
            Command output (stripped) or None on any failure

        Example:
            >>> output = discovery._run_git_command(["status", "--porcelain"])
            >>> if output is not None:
            ...     print("Git command succeeded")
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
                timeout=5,  # Prevent hanging
            )
            return result.stdout.strip()
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            OSError,
            FileNotFoundError,
        ) as e:
            # Graceful degradation - log but return None
            logger.debug("Git command failed: %s, error: %s", args, e)
            return None


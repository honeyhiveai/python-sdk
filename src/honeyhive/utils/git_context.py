"""Git context collection for experiment metadata.

Collects git repository information (commit, branch, remote URL, etc.)
from the current working directory to stamp on experiment run metadata.
"""

import subprocess
from typing import Any, Dict, Optional

from honeyhive.utils.logger import get_logger

logger = get_logger("honeyhive.utils.git_context")


def _run_git_command(args: list, cwd: Optional[str] = None) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=cwd,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def get_git_context(cwd: Optional[str] = None) -> Dict[str, Any]:
    """Collect git context from the current working directory.

    Returns a dictionary with git metadata suitable for stamping on
    experiment run metadata. Returns an empty dict if not in a git repo
    or git is unavailable.

    Args:
        cwd: Working directory to run git commands in. Defaults to the
            current process working directory.

    Returns:
        Dictionary with git context fields:
            - commit_hash: Full SHA of HEAD commit
            - commit_hash_short: Short SHA of HEAD commit
            - branch: Current branch name
            - commit_message: Subject line of HEAD commit
            - author_name: Author name of HEAD commit
            - author_email: Author email of HEAD commit
            - remote_url: URL of the 'origin' remote
            - is_dirty: Whether the working tree has uncommitted changes
    """
    rev_parse = _run_git_command(["rev-parse", "--is-inside-work-tree"], cwd=cwd)
    if rev_parse != "true":
        return {}

    context: Dict[str, Any] = {}

    commit_hash = _run_git_command(["rev-parse", "HEAD"], cwd=cwd)
    if commit_hash:
        context["commit_hash"] = commit_hash

    commit_hash_short = _run_git_command(["rev-parse", "--short", "HEAD"], cwd=cwd)
    if commit_hash_short:
        context["commit_hash_short"] = commit_hash_short

    branch = _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if branch:
        context["branch"] = branch

    commit_message = _run_git_command(["log", "-1", "--format=%s"], cwd=cwd)
    if commit_message:
        context["commit_message"] = commit_message

    author_name = _run_git_command(["log", "-1", "--format=%an"], cwd=cwd)
    if author_name:
        context["author_name"] = author_name

    author_email = _run_git_command(["log", "-1", "--format=%ae"], cwd=cwd)
    if author_email:
        context["author_email"] = author_email

    remote_url = _run_git_command(["remote", "get-url", "origin"], cwd=cwd)
    if remote_url:
        context["remote_url"] = remote_url

    status_output = _run_git_command(["status", "--porcelain"], cwd=cwd)
    if status_output is not None:
        context["is_dirty"] = len(status_output) > 0

    return context

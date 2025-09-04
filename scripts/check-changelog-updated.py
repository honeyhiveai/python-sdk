#!/usr/bin/env python3
"""
CHANGELOG Update Checker

Ensures that CHANGELOG.md is updated when code changes are made.
This prevents code changes from being committed without proper documentation.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import NoReturn


def get_staged_files() -> list:
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []


def has_significant_changes(staged_files: list) -> bool:
    """Check if there are staged changes that require CHANGELOG updates."""
    significant_patterns = [
        "src/",  # Source code changes
        "scripts/",  # Tooling changes
        ".github/workflows/",  # CI/CD changes
        "pyproject.toml",  # Dependency/config changes
        "tox.ini",  # Build config changes
        "docs/",  # Documentation changes (significant)
        ".agent-os/",  # Agent OS documentation changes
        "examples/",  # Example changes
    ]

    exclude_patterns = [
        "__pycache__",
        ".pyc",
        ".pytest_cache",
        "_build/",  # Sphinx build artifacts
        ".tox/",  # Tox artifacts
    ]

    significant_files = []
    for file_path in staged_files:
        # Check if it's a significant file
        if any(file_path.startswith(pattern) for pattern in significant_patterns):
            # But exclude build artifacts and cache files
            if not any(exclude in file_path for exclude in exclude_patterns):
                significant_files.append(file_path)

    # Consider it significant if we have multiple files or any non-trivial changes
    return len(significant_files) > 0


def is_changelog_updated(staged_files: list) -> bool:
    """Check if CHANGELOG.md is being updated in this commit."""
    return "CHANGELOG.md" in staged_files


def get_changelog_last_modified() -> datetime:
    """Get the last modification date of CHANGELOG.md."""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        return datetime.min

    return datetime.fromtimestamp(changelog_path.stat().st_mtime)


def is_recent_update(last_modified: datetime, hours: int = 24) -> bool:
    """Check if CHANGELOG was updated recently (within specified hours)."""
    time_diff = datetime.now() - last_modified
    return time_diff.total_seconds() < (hours * 3600)


def check_commit_message_has_docs_intent() -> bool:
    """Check if commit message indicates documentation intent."""
    try:
        # Get the commit message being prepared
        result = subprocess.run(
            ["git", "log", "--format=%B", "-n", "1", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        commit_msg = result.stdout.lower()

        # Keywords that indicate documentation intent
        doc_keywords = [
            "docs:",
            "doc:",
            "documentation",
            "changelog",
            "readme",
            "update docs",
            "fix: docs",
            "feat: docs",
            "chore: docs",
        ]

        return any(keyword in commit_msg for keyword in doc_keywords)
    except subprocess.CalledProcessError:
        return False


def main() -> NoReturn:
    """Main validation function."""
    print("📝 CHANGELOG Update Check")
    print("=" * 30)

    staged_files = get_staged_files()

    if not staged_files:
        print("✅ No staged files to check")
        sys.exit(0)

    has_significant = has_significant_changes(staged_files)
    changelog_updated = is_changelog_updated(staged_files)

    print(f"📁 Staged files: {len(staged_files)}")
    print(f"🔧 Significant changes detected: {'Yes' if has_significant else 'No'}")
    print(f"📝 CHANGELOG.md updated: {'Yes' if changelog_updated else 'No'}")

    # If no significant changes, allow commit
    if not has_significant:
        print("✅ No significant changes requiring CHANGELOG update")
        sys.exit(0)

    # If CHANGELOG is being updated, allow commit
    if changelog_updated:
        print("✅ CHANGELOG.md is being updated")
        sys.exit(0)

    # Check if CHANGELOG was recently updated (within 24 hours)
    last_modified = get_changelog_last_modified()
    if is_recent_update(last_modified, hours=24):
        print(
            f"✅ CHANGELOG.md was recently updated ({last_modified.strftime('%Y-%m-%d %H:%M')})"
        )
        sys.exit(0)

    # Check if this is explicitly a documentation commit
    if check_commit_message_has_docs_intent():
        print("✅ Documentation-focused commit detected")
        sys.exit(0)

    # Fail the check
    print("\n❌ CHANGELOG.md update required!")
    print("\nSignificant changes detected but CHANGELOG.md not updated.")
    print("\nTo fix this:")
    print("1. Update CHANGELOG.md with your changes")
    print("2. Stage the CHANGELOG.md file: git add CHANGELOG.md")
    print("3. Re-run your commit")
    print("\nOr use a documentation commit message (docs:, fix: docs, etc.)")
    print("Or bypass in emergencies: git commit --no-verify")

    sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Mandatory Documentation Update Checker

Ensures that all commits include appropriate documentation updates.
This prevents commits from being made without proper documentation maintenance.
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta
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


def get_commit_message() -> str:
    """Get the commit message being prepared."""
    # Check for commit message file (used by git commit -m)
    commit_msg_file = Path(".git/COMMIT_EDITMSG")
    if commit_msg_file.exists():
        return commit_msg_file.read_text().strip()

    # If no commit message file, this might be an amend or merge
    return ""


def is_emergency_commit(commit_msg: str) -> bool:
    """Check if this is marked as an emergency commit."""
    emergency_keywords = [
        "emergency",
        "hotfix",
        "urgent",
        "critical",
        "security:",
        "sec:",
        "fix: critical",
    ]
    return any(keyword in commit_msg.lower() for keyword in emergency_keywords)


def is_docs_only_commit(staged_files: list) -> bool:
    """Check if this commit only contains documentation changes."""
    doc_patterns = [
        "docs/",
        "README.md",
        "CHANGELOG.md",
        ".agent-os/",
        ".cursorrules",
        "*.md",
        "*.rst",
    ]

    non_doc_files = []
    for file_path in staged_files:
        if not any(
            file_path.startswith(pattern.rstrip("*"))
            or file_path.endswith(pattern.lstrip("*"))
            or pattern in file_path
            for pattern in doc_patterns
        ):
            non_doc_files.append(file_path)

    return len(non_doc_files) == 0


def has_new_features(staged_files: list) -> bool:
    """Check if staged changes include new features."""
    feature_indicators = [
        "src/honeyhive/",  # New SDK features
        ".github/workflows/",  # New CI/CD features
        "scripts/",  # New tooling
    ]

    for file_path in staged_files:
        if any(file_path.startswith(pattern) for pattern in feature_indicators):
            return True

    return False


def check_required_docs_updated(staged_files: list) -> tuple:
    """Check which required docs are being updated."""
    required_docs = {
        "CHANGELOG.md": False,
        "README.md": False,
        "docs/FEATURE_LIST.rst": False,
        ".agent-os/product/features.md": False,
    }

    for file_path in staged_files:
        if file_path in required_docs:
            required_docs[file_path] = True

    updated = [doc for doc, updated in required_docs.items() if updated]
    missing = [doc for doc, updated in required_docs.items() if not updated]

    return updated, missing


def check_ai_assistant_compliance() -> bool:
    """Check if this commit comes from an AI assistant that should update docs."""
    # Check environment variables that might indicate AI assistant usage
    ai_indicators = [
        "CURSOR_SESSION",
        "COPILOT_SESSION",
        "AI_ASSISTANT",
        "CLAUDE_SESSION",
    ]

    for indicator in ai_indicators:
        if os.environ.get(indicator):
            return True

    # Check commit message patterns
    commit_msg = get_commit_message()
    ai_patterns = [
        "feat:",
        "fix:",
        "docs:",
        "refactor:",  # Conventional commits often from AI
        "implement",
        "add support for",
        "enhance",  # Common AI patterns
    ]

    return any(pattern in commit_msg.lower() for pattern in ai_patterns)


def main() -> NoReturn:
    """Main validation function."""
    print("📋 Mandatory Documentation Update Check")
    print("=" * 45)

    staged_files = get_staged_files()
    commit_msg = get_commit_message()

    if not staged_files:
        print("✅ No staged files to check")
        sys.exit(0)

    print(f"📁 Staged files: {len(staged_files)}")

    # Allow docs-only commits
    if is_docs_only_commit(staged_files):
        print("✅ Documentation-only commit")
        sys.exit(0)

    # Allow emergency commits
    if is_emergency_commit(commit_msg):
        print("🚨 Emergency commit detected - bypassing docs requirement")
        sys.exit(0)

    # Check if new features are being added
    has_features = has_new_features(staged_files)
    updated_docs, missing_docs = check_required_docs_updated(staged_files)

    print(f"🆕 New features detected: {'Yes' if has_features else 'No'}")
    print(f"📝 Updated docs: {updated_docs if updated_docs else 'None'}")

    # Strict enforcement for feature commits
    if has_features:
        required_for_features = ["CHANGELOG.md", "docs/FEATURE_LIST.rst"]
        missing_required = [doc for doc in required_for_features if doc in missing_docs]

        if missing_required:
            print(f"\n❌ New features require documentation updates!")
            print(f"   Missing: {missing_required}")
            print("\nTo fix:")
            print("1. Update CHANGELOG.md with your changes")
            print("2. Update docs/FEATURE_LIST.rst if adding new features")
            print("3. Stage updated docs: git add CHANGELOG.md docs/FEATURE_LIST.rst")
            print("4. Re-run your commit")
            sys.exit(1)

    # General enforcement - at least CHANGELOG for significant changes
    if len(staged_files) > 3 and "CHANGELOG.md" not in updated_docs:
        # Check if this looks like an AI assistant commit
        if check_ai_assistant_compliance():
            print(f"\n⚠️  AI Assistant Compliance Warning!")
            print(
                f"   Large changeset ({len(staged_files)} files) without CHANGELOG update"
            )
            print(f"   AI assistants should update documentation before committing")
            print("\nTo fix:")
            print("1. Update CHANGELOG.md with your changes")
            print("2. Stage it: git add CHANGELOG.md")
            print("3. Re-commit")
            sys.exit(1)

    print("✅ Documentation requirements satisfied")
    sys.exit(0)


if __name__ == "__main__":
    main()

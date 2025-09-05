#!/usr/bin/env python3
"""
Documentation Compliance Checker

Comprehensive validation for documentation updates in high-frequency development.
Ensures proper documentation maintenance without compromising content quality.
"""

import subprocess
import sys
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
    commit_msg_file = Path(".git/COMMIT_EDITMSG")
    if commit_msg_file.exists():
        return commit_msg_file.read_text().strip()
    return ""


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
        if any(file_path.startswith(pattern) for pattern in significant_patterns):
            if not any(exclude in file_path for exclude in exclude_patterns):
                significant_files.append(file_path)

    return len(significant_files) > 0


def has_new_features(staged_files: list) -> bool:
    """Check if new features are being added that require reference docs."""
    feature_indicators = [
        "src/honeyhive/",  # Core SDK changes
        "examples/",  # New examples
    ]
    
    return any(
        file_path.startswith(pattern) 
        for file_path in staged_files 
        for pattern in feature_indicators
    )


def is_changelog_updated(staged_files: list) -> bool:
    """Check if CHANGELOG.md is being updated."""
    return "CHANGELOG.md" in staged_files


def is_docs_changelog_updated(staged_files: list) -> bool:
    """Check if docs/changelog.rst is being updated."""
    return "docs/changelog.rst" in staged_files


def is_reference_docs_updated(staged_files: list) -> bool:
    """Check if reference documentation is being updated."""
    reference_files = [
        "docs/reference/index.rst",
        ".agent-os/product/features.md"
    ]
    return any(ref_file in staged_files for ref_file in reference_files)


def is_docs_only_commit(staged_files: list) -> bool:
    """Check if this is a documentation-only commit."""
    doc_patterns = ["docs/", "README.md", ".agent-os/"]
    non_doc_patterns = ["src/", "tests/", "examples/", "scripts/"]
    
    has_docs = any(file_path.startswith(pattern) for file_path in staged_files for pattern in doc_patterns)
    has_non_docs = any(file_path.startswith(pattern) for file_path in staged_files for pattern in non_doc_patterns)
    
    return has_docs and not has_non_docs


def is_emergency_commit(commit_msg: str) -> bool:
    """Check if this is marked as an emergency commit."""
    emergency_keywords = [
        "emergency", "hotfix", "urgent", "critical", "security:", "sec:"
    ]
    return any(keyword in commit_msg.lower() for keyword in emergency_keywords)


def check_commit_message_has_docs_intent() -> bool:
    """Check if commit message indicates documentation intent."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%B", "-n", "1", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        commit_msg = result.stdout.lower()

        doc_keywords = [
            "docs:", "doc:", "documentation", "changelog", "readme",
            "update docs", "fix: docs", "feat: docs", "chore: docs",
        ]

        return any(keyword in commit_msg for keyword in doc_keywords)
    except subprocess.CalledProcessError:
        return False


def main() -> NoReturn:
    """Main validation function."""
    print("📚 Documentation Compliance Check")
    print("=" * 40)

    staged_files = get_staged_files()
    commit_msg = get_commit_message()

    if not staged_files:
        print("✅ No staged files to check")
        sys.exit(0)

    # Analyze the commit
    has_significant = has_significant_changes(staged_files)
    has_features = has_new_features(staged_files)
    changelog_updated = is_changelog_updated(staged_files)
    docs_changelog_updated = is_docs_changelog_updated(staged_files)
    reference_updated = is_reference_docs_updated(staged_files)
    is_docs_only = is_docs_only_commit(staged_files)
    is_emergency = is_emergency_commit(commit_msg)

    print(f"📁 Staged files: {len(staged_files)}")
    print(f"🔧 Significant changes: {'Yes' if has_significant else 'No'}")
    print(f"✨ New features: {'Yes' if has_features else 'No'}")
    print(f"📝 CHANGELOG.md updated: {'Yes' if changelog_updated else 'No'}")
    print(f"📚 docs/changelog.rst updated: {'Yes' if docs_changelog_updated else 'No'}")
    print(f"📖 Reference docs updated: {'Yes' if reference_updated else 'No'}")
    print(f"📄 Docs-only commit: {'Yes' if is_docs_only else 'No'}")
    print("⚡ High-frequency development mode: Strict enforcement enabled")

    # Emergency bypass
    if is_emergency:
        print("🚨 Emergency commit detected - bypassing documentation requirements")
        sys.exit(0)

    # Docs-only commits have relaxed requirements
    if is_docs_only:
        if len(staged_files) > 5 and not changelog_updated:
            print("\n⚠️  Large documentation change detected")
            print("Consider updating CHANGELOG.md for significant documentation changes")
        print("✅ Documentation-only commit")
        sys.exit(0)

    # No significant changes - allow commit
    if not has_significant:
        print("✅ No significant changes requiring documentation updates")
        sys.exit(0)

    # CRITICAL: If CHANGELOG.md is updated, docs/changelog.rst MUST be updated
    if changelog_updated and not docs_changelog_updated:
        print("\n❌ Documentation changelog sync required!")
        print("\nCHANGELOG.md is being updated but docs/changelog.rst is not.")
        print("\n📋 IMPORTANT: Keep content styles different:")
        print("  • CHANGELOG.md: Detailed technical changes")
        print("  • docs/changelog.rst: High-level user-facing highlights")
        print("\nTo fix this:")
        print("1. Update docs/changelog.rst with curated, user-friendly highlights")
        print("2. Stage the file: git add docs/changelog.rst")
        print("3. Re-run your commit")
        print("\n💡 The docs changelog should be lightweight and curated!")
        sys.exit(1)

    # New features require reference documentation
    if has_features and not reference_updated:
        print("\n❌ Reference documentation update required!")
        print("\nNew features detected but reference docs not updated.")
        print("\nTo fix this:")
        print("1. Update docs/reference/index.rst with new features")
        print("2. Update .agent-os/product/features.md if applicable")
        print("3. Stage updated docs: git add docs/reference/index.rst")
        print("4. Re-run your commit")
        sys.exit(1)

    # Significant changes require CHANGELOG
    if has_significant and not changelog_updated:
        # Check if this is explicitly a documentation commit
        if check_commit_message_has_docs_intent():
            print("✅ Documentation-focused commit detected")
            sys.exit(0)

        print("\n❌ CHANGELOG.md update required!")
        print("\nSignificant changes detected but CHANGELOG.md not updated.")
        print("\nTo fix this:")
        print("1. Update CHANGELOG.md with your changes")
        print("2. Update docs/changelog.rst with curated highlights")
        print("3. Stage both files: git add CHANGELOG.md docs/changelog.rst")
        print("4. Re-run your commit")
        print("\nOr use a documentation commit message (docs:, fix: docs, etc.)")
        print("Or bypass in emergencies: git commit --no-verify")
        sys.exit(1)

    # All checks passed
    if changelog_updated and docs_changelog_updated:
        print("✅ Both CHANGELOG.md and docs/changelog.rst are being updated")
    
    print("✅ All documentation compliance requirements satisfied")
    sys.exit(0)


if __name__ == "__main__":
    main()

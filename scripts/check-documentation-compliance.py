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


def get_change_statistics(staged_files: list) -> dict:
    """
    Analyze git diff statistics to understand the nature of changes.
    
    Returns dictionary with:
    - total_additions: Total lines added
    - total_deletions: Total lines deleted  
    - net_change: additions - deletions (positive = growth, negative = reduction)
    - is_mostly_deletions: True if >70% of changes are deletions
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--numstat"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        total_additions = 0
        total_deletions = 0
        
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                added = parts[0]
                deleted = parts[1]
                # Skip binary files (marked with '-')
                if added != "-" and deleted != "-":
                    total_additions += int(added)
                    total_deletions += int(deleted)
        
        total_changes = total_additions + total_deletions
        deletion_ratio = total_deletions / total_changes if total_changes > 0 else 0
        
        return {
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "net_change": total_additions - total_deletions,
            "is_mostly_deletions": deletion_ratio > 0.7,
        }
    except subprocess.CalledProcessError:
        return {
            "total_additions": 0,
            "total_deletions": 0,
            "net_change": 0,
            "is_mostly_deletions": False,
        }


def has_significant_changes(staged_files: list) -> bool:
    """Check if there are staged changes that require CHANGELOG updates."""
    significant_patterns = [
        "src/",  # Source code changes
        "scripts/",  # Tooling changes
        ".github/workflows/",  # CI/CD changes
        "pyproject.toml",  # Dependency/config changes
        "tox.ini",  # Build config changes
        "docs/",  # Documentation changes (significant)
        ".praxis-os/",  # praxis OS documentation changes
        "examples/",  # Example changes
    ]

    exclude_patterns = [
        "__pycache__",
        ".pyc",
        ".pytest_cache",
        "_build/",  # Sphinx build artifacts
        ".tox/",  # Tox artifacts
        ".praxis-os/specs/",  # Spec proposals - CHANGELOG required on implementation, not proposal
    ]

    significant_files = []
    for file_path in staged_files:
        if any(file_path.startswith(pattern) for pattern in significant_patterns):
            if not any(exclude in file_path for exclude in exclude_patterns):
                significant_files.append(file_path)

    return len(significant_files) > 0


def detect_change_type(staged_files: list, change_stats: dict) -> str:
    """
    Detect the type of change based on files modified and change statistics.
    
    Returns:
    - "feature": New functionality being added (requires reference docs)
    - "refactor": Code cleanup/restructuring (changelog only)
    - "fix": Bug fix (changelog only)
    - "test": Test-only changes (minimal docs)
    - "docs": Documentation changes (minimal requirements)
    - "other": Other changes (full requirements)
    """
    # Pure test changes
    if all(f.startswith("tests/") for f in staged_files):
        return "test"
    
    # Pure documentation changes
    doc_patterns = ["docs/", "README.md", ".praxis-os/"]
    if all(any(f.startswith(p) for p in doc_patterns) for f in staged_files):
        return "docs"
    
    # Mostly deletions with minimal additions suggests refactoring/cleanup
    if change_stats["is_mostly_deletions"] and change_stats["net_change"] < -100:
        return "refactor"
    
    # Check for new public API additions
    api_files = [
        "src/honeyhive/__init__.py",
        "src/honeyhive/api/",
        "src/honeyhive/tracer/__init__.py",
    ]
    has_api_changes = any(f.startswith(tuple(api_files)) for f in staged_files)
    
    # Check for new examples (usually indicates new features)
    has_new_examples = any(f.startswith("examples/") for f in staged_files)
    
    # If adding new public APIs or examples with significant additions, likely a feature
    if (has_api_changes or has_new_examples) and change_stats["net_change"] > 100:
        return "feature"
    
    # Internal processing/utility changes (not public API)
    internal_patterns = [
        "src/honeyhive/tracer/processing/",
        "src/honeyhive/tracer/utils/",
        "src/honeyhive/utils/",
        "scripts/",
    ]
    if any(f.startswith(tuple(internal_patterns)) for f in staged_files):
        # If mostly internal changes without API changes, treat as refactor
        if not has_api_changes:
            return "refactor"
    
    # Default: treat as potentially user-facing change
    return "other"


def has_new_features(staged_files: list, change_type: str) -> bool:
    """
    Check if new features are being added that require reference docs.
    
    Based on detected change type:
    - feature: Requires reference docs
    - refactor/fix/test/docs: No reference docs needed
    """
    return change_type == "feature"


def is_changelog_updated(staged_files: list) -> bool:
    """Check if CHANGELOG.md is being updated."""
    return "CHANGELOG.md" in staged_files


def is_docs_changelog_updated(staged_files: list) -> bool:
    """Check if docs/changelog.rst is being updated."""
    return "docs/changelog.rst" in staged_files


def is_reference_docs_updated(staged_files: list) -> bool:
    """Check if reference documentation is being updated."""
    reference_files = ["docs/reference/index.rst", ".praxis-os/workspace/product/features.md"]
    return any(ref_file in staged_files for ref_file in reference_files)


def is_docs_only_commit(staged_files: list) -> bool:
    """Check if this is a documentation-only commit."""
    doc_patterns = ["docs/", "README.md", ".praxis-os/"]
    non_doc_patterns = ["src/", "tests/", "examples/", "scripts/"]

    has_docs = any(
        file_path.startswith(pattern)
        for file_path in staged_files
        for pattern in doc_patterns
    )
    has_non_docs = any(
        file_path.startswith(pattern)
        for file_path in staged_files
        for pattern in non_doc_patterns
    )

    return has_docs and not has_non_docs


def is_emergency_commit(commit_msg: str) -> bool:
    """Check if this is marked as an emergency commit."""
    emergency_keywords = [
        "emergency",
        "hotfix",
        "urgent",
        "critical",
        "security:",
        "sec:",
    ]
    return any(keyword in commit_msg.lower() for keyword in emergency_keywords)


def check_commit_message_has_docs_intent() -> bool:
    """Check if commit message indicates documentation intent."""
    # During pre-commit hooks, there is no commit message yet
    # This function should not be used to bypass CHANGELOG requirements
    # during pre-commit validation, only during post-commit analysis

    # For now, always return False during pre-commit to enforce CHANGELOG updates
    # This ensures significant changes always require proper documentation
    return False


def main() -> NoReturn:
    """
    Main validation function.

    Validation order (by priority):
    1. PRIMARY: CHANGELOG.md updates for significant changes
    2. SECONDARY: docs/changelog.rst sync when CHANGELOG.md is updated
    3. TERTIARY: Reference docs updates for new features (after changelog)

    This order ensures changelog entries are complete before derived documentation.
    
    Change type detection (file and diff-based):
    - feature: New public APIs/examples -> full docs required
    - refactor: Code cleanup, mostly deletions -> changelog only
    - fix: Bug fixes -> changelog only
    - test/docs: Minimal requirements
    """
    print("📚 Documentation Compliance Check")
    print("=" * 40)

    staged_files = get_staged_files()
    commit_msg = get_commit_message()

    if not staged_files:
        print("✅ No staged files to check")
        sys.exit(0)

    # Analyze the changes
    change_stats = get_change_statistics(staged_files)
    change_type = detect_change_type(staged_files, change_stats)
    has_significant = has_significant_changes(staged_files)
    has_features = has_new_features(staged_files, change_type)
    changelog_updated = is_changelog_updated(staged_files)
    docs_changelog_updated = is_docs_changelog_updated(staged_files)
    reference_updated = is_reference_docs_updated(staged_files)
    is_docs_only = is_docs_only_commit(staged_files)
    is_emergency = is_emergency_commit(commit_msg)

    print(f"📁 Staged files: {len(staged_files)}")
    print(f"📊 Change statistics: +{change_stats['total_additions']} -{change_stats['total_deletions']} (net: {change_stats['net_change']:+d})")
    print(f"🔍 Detected change type: {change_type}")
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

    # Docs-only commits: still require CHANGELOG for significant changes
    if is_docs_only:
        if has_significant and not changelog_updated:
            print(
                "\n❌ CHANGELOG.md update required for significant documentation changes!"
            )
            print(
                "\nEven documentation-only commits require CHANGELOG updates when they:"
            )
            print("- Affect user-facing behavior or examples")
            print("- Change API documentation or reference materials")
            print("- Include major template or generation system changes")
            print("\nTo fix this:")
            print("1. Update CHANGELOG.md with your documentation changes")
            print("2. Stage the file: git add CHANGELOG.md")
            print("3. Re-run your commit")
            sys.exit(1)
        elif len(staged_files) > 5 and not changelog_updated:
            print("\n⚠️  Large documentation change detected")
            print(
                "Consider updating CHANGELOG.md for significant documentation changes"
            )
        print("✅ Documentation-only commit")
        sys.exit(0)

    # No significant changes - allow commit
    if not has_significant:
        print("✅ No significant changes requiring documentation updates")
        sys.exit(0)

    # PRIMARY CHECK: Significant changes require CHANGELOG first
    if has_significant and not changelog_updated:
        # Check if this is explicitly a documentation commit
        if check_commit_message_has_docs_intent():
            print("✅ Documentation-focused commit detected")
            sys.exit(0)

        print("\n❌ CHANGELOG.md update required!")
        print("\nSignificant changes detected but CHANGELOG.md not updated.")
        print(
            "\nCHANGELOG updates are required FIRST since reference docs are derived from changelog entries."
        )
        print("\nTo fix this:")
        print("1. Update CHANGELOG.md with your changes")
        print("2. Update docs/changelog.rst with curated highlights")
        print("3. Stage both files: git add CHANGELOG.md docs/changelog.rst")
        print("4. Re-run your commit")
        print("\nOr use a documentation commit message (docs:, fix: docs, etc.)")
        sys.exit(1)

    # SECONDARY CHECK: If CHANGELOG.md is updated, docs/changelog.rst MUST be updated
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

    # TERTIARY CHECK: New features require reference documentation (after CHANGELOG)
    if has_features and not reference_updated:
        print("\n❌ Reference documentation update required!")
        print("\nNew features detected (new public APIs or examples) but reference docs not updated.")
        print(
            "\nReference docs should be updated AFTER changelog entries are complete."
        )
        print("\nTo fix this:")
        print("1. Update docs/reference/index.rst with new features")
        print("2. Update .praxis-os/workspace/product/features.md if applicable")
        print("3. Stage updated docs: git add docs/reference/index.rst")
        print("4. Re-run your commit")
        print(f"\n💡 NOTE: Detected change type is '{change_type}'")
        print("   If this is internal refactoring, the detection may need adjustment.")
        sys.exit(1)

    # All checks passed
    if changelog_updated and docs_changelog_updated:
        print("✅ Both CHANGELOG.md and docs/changelog.rst are being updated")

    print("✅ All documentation compliance requirements satisfied")
    sys.exit(0)


if __name__ == "__main__":
    main()

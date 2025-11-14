#!/usr/bin/env python3
"""
Safe Upgrade Tool for prAxIs OS

Safely upgrades local .praxis-os/ directory from praxis-os-enhanced source
with conflict detection and interactive prompts.

This tool compares checksums between the source manifest and local files,
automatically updating unchanged files while prompting for conflicts.

Usage:
    python scripts/safe-upgrade.py --source /path/to/praxis-os-enhanced --target .praxis-os

Examples:
    # Preview changes (dry-run)
    python scripts/safe-upgrade.py --source ../praxis-os-enhanced --dry-run

    # Execute upgrade
    python scripts/safe-upgrade.py --source ../praxis-os-enhanced --target .praxis-os
"""

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class FileState(Enum):
    """File state classification for upgrade decisions."""

    NEW = "new"  # In manifest, not local
    UNCHANGED = "unchanged"  # Both exist, no changes
    AUTO_UPDATE = "auto_update"  # Local unchanged, upstream changed
    LOCAL_ONLY = "local_only"  # Local changed, upstream unchanged
    CONFLICT = "conflict"  # Both changed
    ERROR = "error"  # Processing error


@dataclass
class UpgradeReport:
    """
    Report of upgrade operations performed.

    Tracks all files processed, actions taken, and timing information
    for the upgrade session.

    Attributes:
        added: List of file paths that were added
        updated: List of file paths that were auto-updated
        skipped: List of file paths that were skipped (unchanged)
        local_only: List of files with local-only changes preserved
        conflicts: List of files requiring manual decision
        errors: List of files that had processing errors
        start_time: When the upgrade started
        end_time: When the upgrade completed (None if not finished)
        backup_path: Path to backup directory (None if dry-run)
        dry_run: Whether this was a dry-run (no actual changes)
    """

    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    local_only: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    backup_path: Optional[str] = None
    dry_run: bool = False


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Load and validate manifest from JSON file.

    Args:
        manifest_path: Path to the manifest JSON file

    Returns:
        Manifest dictionary with version, generated, generator_version, and files

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        ValueError: If manifest is invalid (malformed JSON or missing fields)

    Examples:
        >>> from pathlib import Path
        >>> manifest = load_manifest(Path("universal/.universal-manifest.json"))
        >>> "version" in manifest
        True
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest: {e}") from e

    # Validate required fields
    required_fields = ["version", "generated", "generator_version", "files"]
    for field in required_fields:
        if field not in manifest:
            raise ValueError(f"Manifest missing required field: {field}")

    # Validate files structure
    if not isinstance(manifest["files"], dict):
        raise ValueError("Manifest 'files' field must be a dictionary")

    # Validate file entries
    for rel_path, metadata in manifest["files"].items():
        if not isinstance(metadata, dict):
            raise ValueError(f"Invalid metadata for file: {rel_path}")

        required_metadata = ["checksum", "size", "last_updated"]
        for field in required_metadata:
            if field not in metadata:
                raise ValueError(f"File '{rel_path}' missing field: {field}")

        # Validate checksum format
        checksum = metadata["checksum"]
        if not checksum.startswith("sha256:") or len(checksum) != 71:
            raise ValueError(f"File '{rel_path}' has malformed checksum: {checksum}")

    return manifest


def calculate_checksum(file_path: Path) -> str:
    """
    Calculate SHA-256 checksum of a file.

    Args:
        file_path: Path to the file

    Returns:
        Hexadecimal checksum string

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}") from e


def classify_file(
    rel_path: str, manifest: Dict[str, Any], local_dir: Path, source_dir: Path
) -> FileState:
    """
    Classify file state based on checksums.

    Compares local file, source file, and manifest checksums to determine
    the appropriate action for the file.

    Args:
        rel_path: Relative path of the file
        manifest: Source manifest dictionary
        local_dir: Local .praxis-os directory
        source_dir: Source universal directory

    Returns:
        FileState enum indicating the classification

    Examples:
        >>> from pathlib import Path
        >>> # File exists in manifest but not locally
        >>> classify_file("new.md", manifest, Path(".praxis-os"), Path("universal"))
        FileState.NEW
    """
    local_file = local_dir / rel_path
    source_file = source_dir / rel_path

    # Get manifest checksum
    if rel_path not in manifest["files"]:
        # This shouldn't happen in normal operation
        return FileState.ERROR

    manifest_checksum = manifest["files"][rel_path]["checksum"]

    # Calculate source checksum
    try:
        source_checksum = f"sha256:{calculate_checksum(source_file)}"
    except Exception:
        return FileState.ERROR

    # Case 1: File doesn't exist locally
    if not local_file.exists():
        return FileState.NEW

    # Calculate local checksum
    try:
        local_checksum = f"sha256:{calculate_checksum(local_file)}"
    except Exception:
        return FileState.ERROR

    # Case 2: Local matches manifest (user hasn't modified it)
    if local_checksum == manifest_checksum:
        if source_checksum == manifest_checksum:
            return FileState.UNCHANGED
        else:
            return FileState.AUTO_UPDATE

    # Case 3: Local changed (user customized it)
    else:
        if source_checksum == manifest_checksum:
            return FileState.LOCAL_ONLY
        else:
            return FileState.CONFLICT


def log_message(message: str, log_file: Optional[Path] = None):
    """
    Log message to console and optionally to file.

    Args:
        message: Message to log
        log_file: Optional path to log file
    """
    # Print to console
    print(message)

    # Write to log file if provided
    if log_file:
        try:
            timestamp = datetime.now().isoformat()
            with open(log_file, "a") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception:
            # Don't fail if logging fails
            pass


def create_backup(target_dir: Path) -> Path:
    """
    Create timestamped backup of target directory.

    Args:
        target_dir: Directory to backup

    Returns:
        Path to backup directory

    Raises:
        IOError: If backup fails
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = target_dir.parent / f"{target_dir.name}.backup.{timestamp}"

    print(f"📦 Creating backup: {backup_path}")

    try:
        shutil.copytree(target_dir, backup_path, symlinks=True)
        print(f"✅ Backup created successfully")
        return backup_path
    except Exception as e:
        raise IOError(f"Failed to create backup: {e}") from e


def show_diff(local_file: Path, source_file: Path, max_lines: int = 50):
    """
    Show diff between local and source files.

    Args:
        local_file: Local file path
        source_file: Source file path
        max_lines: Maximum lines of diff to show
    """
    import difflib

    try:
        with open(local_file, "r") as f:
            local_lines = f.readlines()
        with open(source_file, "r") as f:
            source_lines = f.readlines()
    except UnicodeDecodeError:
        print("   [Binary file - cannot show diff]")
        return

    differ = difflib.Differ()
    diff = list(differ.compare(local_lines, source_lines))

    print(f"\n   === DIFF (- = local, + = universal) ===")
    lines_shown = 0
    for line in diff:
        if lines_shown >= max_lines:
            print(f"\n   ... ({len(diff) - max_lines} more lines)")
            break
        if line.startswith(("- ", "+ ")):
            print(f"   {line}", end="")
            lines_shown += 1
    print(f"   === END DIFF ===\n")


def handle_conflict(rel_path: str, source_file: Path, local_file: Path) -> str:
    """
    Handle conflict with interactive prompt.

    Args:
        rel_path: Relative file path
        source_file: Source file path
        local_file: Local file path

    Returns:
        Action taken ("kept_local", "replaced", "skipped")
    """
    print(f"\n⚠️  CONFLICT: {rel_path}")
    print(f"   Both local and universal versions have changed.")
    print(f"\n   Local:     {local_file.stat().st_size:,} bytes")
    print(f"   Universal: {source_file.stat().st_size:,} bytes")

    while True:
        print(f"\n   [K] Keep local (preserve your changes)")
        print(f"   [R] Replace with universal (lose local changes)")
        print(f"   [D] Show diff")
        print(f"   [S] Skip (decide later)")

        choice = input(f"   Choice: ").strip().upper()

        if choice == "K":
            print(f"   ✅ Kept local version")
            return "kept_local"
        elif choice == "R":
            confirm = input(f"   ⚠️  Overwrite local changes? [y/N]: ").strip().lower()
            if confirm == "y":
                shutil.copy2(source_file, local_file)
                print(f"   ✅ Replaced with universal")
                return "replaced"
        elif choice == "D":
            show_diff(local_file, source_file)
        elif choice == "S":
            print(f"   ⏭️  Skipped")
            return "skipped"
        else:
            print(f"   Invalid choice. Please choose K, R, D, or S.")


def process_new_file(rel_path: str, source_file: Path, local_file: Path) -> bool:
    """
    Prompt user to add new file.

    Args:
        rel_path: Relative file path
        source_file: Source file path
        local_file: Destination path

    Returns:
        True if file was added, False if skipped
    """
    size_kb = source_file.stat().st_size / 1024
    print(f"\n➕ New file: {rel_path} ({size_kb:.1f} KB)")

    choice = input(f"   Add this file? [Y/n]: ").strip().lower()
    if choice in ["", "y", "yes"]:
        local_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, local_file)
        print(f"   ✅ Added")
        return True
    else:
        print(f"   ⏭️  Skipped")
        return False


def print_summary(report: UpgradeReport):
    """
    Print upgrade summary report.

    Args:
        report: UpgradeReport with all statistics
    """
    report.end_time = datetime.now()
    elapsed = (report.end_time - report.start_time).total_seconds()

    print(f"\n{'='*60}")
    print(f"📊 UPGRADE SUMMARY")
    print(f"{'='*60}")
    print(f"Files added:      {len(report.added)}")
    print(f"Files updated:    {len(report.updated)}")
    print(f"Files unchanged:  {len(report.skipped)}")
    print(f"Local-only:       {len(report.local_only)}")
    print(f"Conflicts:        {len(report.conflicts)}")
    print(f"Errors:           {len(report.errors)}")
    print(f"\nElapsed time:     {elapsed:.1f}s")

    if report.backup_path:
        print(f"\nBackup created:   {report.backup_path}")
        print(f"\n💡 To rollback:")
        print(f"   rm -rf .praxis-os")
        print(f"   mv {report.backup_path} .praxis-os")

    if report.conflicts:
        print(f"\n⚠️  Unresolved conflicts:")
        for path in report.conflicts:
            print(f"   - {path}")

    print(f"{'='*60}")


def main() -> int:
    """
    Main entry point for safe upgrade tool.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Safe prAxIs OS upgrade tool with conflict detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes (dry-run)
  %(prog)s --source /path/to/praxis-os-enhanced --dry-run
  
  # Execute upgrade with custom target
  %(prog)s --source /path/to/praxis-os-enhanced --target .praxis-os
  
  # Non-interactive mode (auto-confirm)
  %(prog)s --source /path/to/praxis-os-enhanced --yes
        """,
    )

    parser.add_argument(
        "--source",
        required=True,
        help="Path to praxis-os-enhanced repository",
        metavar="DIR",
    )

    parser.add_argument(
        "--target",
        default=".praxis-os",
        help="Path to local .praxis-os directory (default: .praxis-os)",
        metavar="DIR",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying them"
    )

    parser.add_argument(
        "--yes",
        action="store_true",
        help="Auto-confirm all prompts (dangerous - use with caution)",
    )

    args = parser.parse_args()

    # Convert to Path objects
    source_dir = Path(args.source) / "universal"
    target_dir = Path(args.target)

    # Validate source directory
    if not source_dir.exists():
        print(f"❌ ERROR: Source directory not found: {source_dir}", file=sys.stderr)
        print(
            f"\n   Make sure the path points to the praxis-os-enhanced repository.",
            file=sys.stderr,
        )
        print(f"   Expected universal/ subdirectory in: {args.source}", file=sys.stderr)
        return 1

    if not source_dir.is_dir():
        print(
            f"❌ ERROR: Source path is not a directory: {source_dir}", file=sys.stderr
        )
        return 1

    # Validate manifest exists
    manifest_path = source_dir / ".universal-manifest.json"
    if not manifest_path.exists():
        print(f"❌ ERROR: Manifest not found: {manifest_path}", file=sys.stderr)
        print(f"\n   The source repository may be too old or corrupt.", file=sys.stderr)
        print(f"   ", file=sys.stderr)
        print(f"   To fix:", file=sys.stderr)
        print(
            f"   1. Ensure you're using praxis-os-enhanced v1.3.0 or later",
            file=sys.stderr,
        )
        print(
            f"   2. Run: cd {args.source} && python scripts/generate-manifest.py --version 1.3.0",
            file=sys.stderr,
        )
        return 1

    # Initialize logging
    log_file = target_dir / "UPGRADE_LOG.txt" if not args.dry_run else None

    # Header
    print(f"🚀 prAxIs OS Safe Upgrade Tool")
    print(f"{'='*60}")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print(
        f"Mode: {'DRY RUN (preview only)' if args.dry_run else 'LIVE (will make changes)'}"
    )
    print(f"{'='*60}")
    print()

    # Load and validate manifest
    try:
        log_message("📖 Loading manifest...", log_file)
        manifest = load_manifest(manifest_path)
        log_message(
            f"✅ Manifest loaded: {len(manifest['files'])} files tracked", log_file
        )
        log_message(f"   Version: {manifest['version']}", log_file)
        print()
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        return 1

    # Initialize report
    report = UpgradeReport(dry_run=args.dry_run)

    # Classify all files
    log_message("🔍 Analyzing files...", log_file)
    classifications = {}

    for rel_path in manifest["files"].keys():
        state = classify_file(rel_path, manifest, target_dir, source_dir)
        classifications[rel_path] = state

        # Track in report
        if state == FileState.NEW:
            report.added.append(rel_path)
        elif state == FileState.UNCHANGED:
            report.skipped.append(rel_path)
        elif state == FileState.AUTO_UPDATE:
            report.updated.append(rel_path)
        elif state == FileState.LOCAL_ONLY:
            report.local_only.append(rel_path)
        elif state == FileState.CONFLICT:
            report.conflicts.append(rel_path)
        elif state == FileState.ERROR:
            report.errors.append(rel_path)

    print()

    # Display summary
    log_message("📊 Analysis Summary:", log_file)
    log_message(f"   New files: {len(report.added)}", log_file)
    log_message(f"   Auto-update: {len(report.updated)}", log_file)
    log_message(f"   Unchanged: {len(report.skipped)}", log_file)
    log_message(f"   Local-only changes: {len(report.local_only)}", log_file)
    log_message(f"   Conflicts: {len(report.conflicts)}", log_file)
    log_message(f"   Errors: {len(report.errors)}", log_file)
    print()

    # Show details for each category
    if report.added:
        log_message("➕ New files to add:", log_file)
        for path in report.added[:10]:  # Show first 10
            log_message(f"   + {path}", log_file)
        if len(report.added) > 10:
            log_message(f"   ... and {len(report.added) - 10} more", log_file)
        print()

    if report.updated:
        log_message("🔄 Files to auto-update:", log_file)
        for path in report.updated[:10]:  # Show first 10
            log_message(f"   ↑ {path}", log_file)
        if len(report.updated) > 10:
            log_message(f"   ... and {len(report.updated) - 10} more", log_file)
        print()

    if report.local_only:
        log_message("📝 Files with local-only changes (will be preserved):", log_file)
        for path in report.local_only[:10]:
            log_message(f"   ✏️  {path}", log_file)
        if len(report.local_only) > 10:
            log_message(f"   ... and {len(report.local_only) - 10} more", log_file)
        print()

    if report.conflicts:
        log_message("⚠️  Conflicts requiring attention:", log_file)
        for path in report.conflicts:
            log_message(f"   ⚠️  {path}", log_file)
        print()

    if report.errors:
        log_message("❌ Files with errors:", log_file)
        for path in report.errors:
            log_message(f"   ❌ {path}", log_file)
        print()

    # Dry-run mode: show what would happen
    if args.dry_run:
        log_message("✅ DRY RUN COMPLETE", log_file)
        log_message("   No changes were made to the filesystem.", log_file)
        log_message("   Remove --dry-run to execute the upgrade.", log_file)
        return 0

    # Live mode: Execute upgrade
    print()
    log_message("🚀 LIVE UPGRADE MODE", log_file)

    # Create backup
    try:
        if target_dir.exists():
            backup_path = create_backup(target_dir)
            report.backup_path = str(backup_path)
        print()
    except IOError as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        return 1

    # Process files by state
    log_message("📝 Processing files...", log_file)
    print()

    # Process NEW files
    for rel_path in report.added:
        source_file = source_dir / rel_path
        local_file = target_dir / rel_path

        if process_new_file(rel_path, source_file, local_file):
            log_message(f"Added: {rel_path}", log_file)

    # Process AUTO_UPDATE files
    if report.updated:
        print(f"\n🔄 Auto-updating {len(report.updated)} files...")
        for rel_path in report.updated:
            source_file = source_dir / rel_path
            local_file = target_dir / rel_path

            try:
                local_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, local_file)
                log_message(f"Updated: {rel_path}", log_file)
                print(f"   ✓ {rel_path}")
            except Exception as e:
                log_message(f"Error updating {rel_path}: {e}", log_file)
                print(f"   ❌ {rel_path}: {e}")

    # Process CONFLICTS
    conflicts_resolved = []
    for rel_path in report.conflicts:
        source_file = source_dir / rel_path
        local_file = target_dir / rel_path

        action = handle_conflict(rel_path, source_file, local_file)
        log_message(f"Conflict {rel_path}: {action}", log_file)
        if action != "skipped":
            conflicts_resolved.append(rel_path)

    # Update report with resolved conflicts
    for path in conflicts_resolved:
        report.conflicts.remove(path)

    # Print summary
    print_summary(report)

    # Success
    log_message("✅ UPGRADE COMPLETE", log_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())

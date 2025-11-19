#!/usr/bin/env python3
"""
Manifest Generator for prAxIs OS

Scans universal/ directory and generates .universal-manifest.json
with checksums and metadata for all skeleton files.

This tool is run during the release process to create a manifest of all
universal files with their SHA-256 checksums, enabling safe upgrades in
consuming projects.

Usage:
    python scripts/generate-manifest.py --version 1.3.0

Examples:
    # Generate manifest for release 1.3.0
    python scripts/generate-manifest.py --version 1.3.0
    
    # Custom paths
    python scripts/generate-manifest.py --version 1.3.0 \\
        --universal-dir /path/to/universal \\
        --output /path/to/manifest.json
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict

# Constants
SUPPORTED_EXTENSIONS = {".md", ".json"}
GENERATOR_VERSION = "1.0.0"


def calculate_checksum(file_path: Path) -> str:
    """
    Calculate SHA-256 checksum of a file.

    Reads the file in 8KB chunks for memory efficiency, allowing large files
    to be processed without loading the entire content into memory.

    Args:
        file_path: Path to the file to checksum

    Returns:
        Hexadecimal string representation of the SHA-256 checksum

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file isn't readable
        IOError: If there's an error reading the file

    Examples:
        >>> from pathlib import Path
        >>> path = Path("test.txt")
        >>> checksum = calculate_checksum(path)
        >>> len(checksum)
        64
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    try:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in 8KB chunks for memory efficiency
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except PermissionError as e:
        raise PermissionError(f"Permission denied reading file: {file_path}") from e
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}") from e


def get_last_modified_date(file_path: Path, repo_root: Path) -> str:
    """
    Get the last modified date of a file, preferring git commit date over filesystem mtime.

    Attempts to retrieve the last commit date for the file from git history.
    If git is not available or the file is not tracked, falls back to the
    filesystem modification time.

    Args:
        file_path: Path to the file
        repo_root: Path to the git repository root

    Returns:
        ISO date string in YYYY-MM-DD format

    Raises:
        ValueError: If file_path doesn't exist

    Examples:
        >>> from pathlib import Path
        >>> date = get_last_modified_date(Path("README.md"), Path("."))
        >>> len(date)
        10
        >>> date.count("-")
        2
    """
    if not file_path.exists():
        raise ValueError(f"File does not exist: {file_path}")

    # Try to get date from git
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", str(file_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,  # 5-second timeout as specified
        )

        git_datetime = result.stdout.strip()
        if git_datetime:
            # Git date format: "YYYY-MM-DD HH:MM:SS +ZZZZ"
            # Extract just the date part (first 10 characters)
            return git_datetime.split()[0]

    except subprocess.TimeoutExpired:
        # Git command took too long, fall back to filesystem
        pass
    except subprocess.CalledProcessError:
        # Git command failed (file not tracked, not a git repo, etc.)
        pass
    except FileNotFoundError:
        # Git not installed
        pass
    except Exception:
        # Any other error, fall back gracefully
        pass

    # Fallback to filesystem mtime
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime).date().isoformat()


def scan_directory(universal_dir: Path, repo_root: Path) -> Dict[str, Dict[str, Any]]:
    """
    Recursively scan directory for supported files and collect metadata.

    Scans the universal/ directory for .md and .json files, calculating
    checksums and collecting metadata for each file. Hidden files and
    unsupported file types are skipped.

    Args:
        universal_dir: Path to the universal/ directory to scan
        repo_root: Path to the git repository root

    Returns:
        Dictionary mapping relative file paths to metadata dictionaries.
        Each metadata dict contains: checksum, size, last_updated

    Raises:
        ValueError: If universal_dir doesn't exist or isn't a directory

    Examples:
        >>> from pathlib import Path
        >>> files = scan_directory(Path("universal"), Path("."))
        >>> all("checksum" in meta for meta in files.values())
        True
    """
    if not universal_dir.exists():
        raise ValueError(f"Directory does not exist: {universal_dir}")

    if not universal_dir.is_dir():
        raise ValueError(f"Path is not a directory: {universal_dir}")

    files = {}
    file_count = 0

    # Recursively find all files
    for file_path in sorted(universal_dir.rglob("*")):
        # Skip directories
        if not file_path.is_file():
            continue

        # Skip unsupported extensions
        if file_path.suffix not in SUPPORTED_EXTENSIONS:
            continue

        # Skip hidden files (starting with .)
        # Exception: allow .universal-manifest.json during validation
        if (
            file_path.name.startswith(".")
            and file_path.name != ".universal-manifest.json"
        ):
            continue

        # Skip hidden directories in path
        if any(part.startswith(".") for part in file_path.parts):
            continue

        # Calculate relative path from universal_dir
        try:
            rel_path = str(file_path.relative_to(universal_dir))
        except ValueError:
            # File is not relative to universal_dir, skip it
            continue

        # Skip the manifest itself if we're generating a new one
        if rel_path == ".universal-manifest.json":
            continue

        # Collect metadata
        try:
            checksum = calculate_checksum(file_path)
            size = file_path.stat().st_size
            last_updated = get_last_modified_date(file_path, repo_root)

            files[rel_path] = {
                "checksum": f"sha256:{checksum}",
                "size": size,
                "last_updated": last_updated,
            }

            file_count += 1
            print(f"  ✓ {rel_path}")

        except Exception as e:
            # Log error but continue with other files
            print(f"  ⚠️  Error processing {rel_path}: {e}", file=sys.stderr)
            continue

    print(f"\n✅ Scanned {file_count} files")
    return files


def generate_manifest(
    universal_dir: Path, version: str, repo_root: Path
) -> Dict[str, Any]:
    """
    Generate complete manifest for universal directory.

    Creates a manifest dictionary containing version information, generation
    timestamp, and metadata for all tracked files in the universal directory.

    Args:
        universal_dir: Path to the universal/ directory
        version: prAxIs OS version string (e.g., "1.3.0")
        repo_root: Path to the git repository root

    Returns:
        Complete manifest dictionary with structure:
        {
            "version": str,
            "generated": str (ISO datetime),
            "generator_version": str,
            "files": {relative_path: metadata, ...}
        }

    Raises:
        ValueError: If universal_dir is invalid

    Examples:
        >>> from pathlib import Path
        >>> manifest = generate_manifest(Path("universal"), "1.3.0", Path("."))
        >>> "version" in manifest
        True
        >>> "files" in manifest
        True
    """
    print(f"Scanning {universal_dir}...")
    files = scan_directory(universal_dir, repo_root)

    manifest = {
        "version": version,
        "generated": datetime.now(UTC).isoformat(),
        "generator_version": GENERATOR_VERSION,
        "files": files,
    }

    return manifest


def validate_manifest(manifest: Dict[str, Any]) -> bool:
    """
    Validate manifest structure and content.

    Checks that the manifest contains all required fields and that
    all values are properly formatted.

    Args:
        manifest: Manifest dictionary to validate

    Returns:
        True if validation passes

    Raises:
        ValueError: If validation fails, with detailed error message

    Examples:
        >>> manifest = {"version": "1.3.0", "generated": "2025-10-07T12:00:00Z",
        ...             "generator_version": "1.0.0", "files": {}}
        >>> validate_manifest(manifest)
        True
    """
    # Check required top-level fields
    required_fields = ["version", "generated", "generator_version", "files"]
    for field in required_fields:
        if field not in manifest:
            raise ValueError(f"Manifest missing required field: {field}")

    # Validate version format (simple check)
    if not isinstance(manifest["version"], str) or not manifest["version"]:
        raise ValueError("Manifest version must be a non-empty string")

    # Validate generated timestamp format (should be ISO datetime)
    if not isinstance(manifest["generated"], str):
        raise ValueError("Manifest generated field must be a string")

    # Validate generator version
    if not isinstance(manifest["generator_version"], str):
        raise ValueError("Manifest generator_version must be a string")

    # Validate files dictionary
    if not isinstance(manifest["files"], dict):
        raise ValueError("Manifest files field must be a dictionary")

    # Validate each file entry
    for rel_path, metadata in manifest["files"].items():
        if not isinstance(metadata, dict):
            raise ValueError(f"File metadata for '{rel_path}' must be a dictionary")

        # Check required metadata fields
        required_metadata_fields = ["checksum", "size", "last_updated"]
        for field in required_metadata_fields:
            if field not in metadata:
                raise ValueError(f"File '{rel_path}' missing required field: {field}")

        # Validate checksum format
        checksum = metadata["checksum"]
        if not isinstance(checksum, str) or not checksum.startswith("sha256:"):
            raise ValueError(
                f"File '{rel_path}' has invalid checksum format: {checksum}"
            )

        # Validate checksum length (sha256: + 64 hex chars = 71 total)
        if len(checksum) != 71:
            raise ValueError(
                f"File '{rel_path}' has invalid checksum length: {len(checksum)}"
            )

        # Validate size
        if not isinstance(metadata["size"], int) or metadata["size"] < 0:
            raise ValueError(f"File '{rel_path}' has invalid size: {metadata['size']}")

        # Validate last_updated format (YYYY-MM-DD)
        last_updated = metadata["last_updated"]
        if not isinstance(last_updated, str) or len(last_updated) != 10:
            raise ValueError(
                f"File '{rel_path}' has invalid date format: {last_updated}"
            )

    return True


def main() -> int:
    """
    Main entry point for manifest generator.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate manifest for prAxIs OS universal files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate manifest for release 1.3.0
  %(prog)s --version 1.3.0
  
  # Custom paths
  %(prog)s --version 1.3.0 --universal-dir /path/to/universal
        """,
    )

    parser.add_argument(
        "--version",
        required=True,
        help="prAxIs OS version (e.g., 1.3.0)",
        metavar="VERSION",
    )

    parser.add_argument(
        "--universal-dir",
        default="universal",
        help="Path to universal directory (default: universal)",
        metavar="DIR",
    )

    parser.add_argument(
        "--output",
        default="universal/.universal-manifest.json",
        help="Output path for manifest (default: universal/.universal-manifest.json)",
        metavar="FILE",
    )

    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to git repository root (default: current directory)",
        metavar="DIR",
    )

    args = parser.parse_args()

    # Convert to Path objects
    universal_dir = Path(args.universal_dir)
    output_path = Path(args.output)
    repo_root = Path(args.repo_root)

    # Validate paths
    if not universal_dir.exists():
        print(
            f"❌ ERROR: Universal directory not found: {universal_dir}", file=sys.stderr
        )
        print(
            f"\n   Make sure you're running from the praxis-os root directory.",
            file=sys.stderr,
        )
        return 1

    if not universal_dir.is_dir():
        print(
            f"❌ ERROR: Universal path is not a directory: {universal_dir}",
            file=sys.stderr,
        )
        return 1

    # Generate manifest
    print(f"🚀 prAxIs OS Manifest Generator v{GENERATOR_VERSION}")
    print(f"   Version: {args.version}")
    print(f"   Universal directory: {universal_dir}")
    print(f"   Output: {output_path}")
    print()

    try:
        manifest = generate_manifest(universal_dir, args.version, repo_root)

        # Validate manifest
        print("\n🔍 Validating manifest...")
        validate_manifest(manifest)
        print("✅ Manifest validation passed")

        # Write output
        print(f"\n📝 Writing manifest to {output_path}...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Summary
        file_count = len(manifest["files"])
        print(f"\n✅ Manifest generated successfully")
        print(f"   Files tracked: {file_count}")
        print(f"   Output: {output_path}")
        print(f"   Version: {manifest['version']}")
        print(f"   Generated: {manifest['generated']}")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

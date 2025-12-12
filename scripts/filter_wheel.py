#!/usr/bin/env python3
"""
Filter wheel contents by excluding specified directories.

This script removes specified directories from a wheel file, allowing us to
create v0.x and v1.x packages from the same source by excluding _v1/ or _v0/.

Usage:
    python scripts/filter_wheel.py dist/*.whl --exclude "_v1"
    python scripts/filter_wheel.py dist/*.whl --exclude "_v0"
"""

import argparse
import hashlib
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


def compute_record_hash(filepath: Path) -> tuple[str, int]:
    """Compute the hash and size for a file in RECORD format."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        content = f.read()
        sha256.update(content)
    # Format: sha256=base64_digest
    import base64

    digest = base64.urlsafe_b64encode(sha256.digest()).rstrip(b"=").decode("ascii")
    return f"sha256={digest}", len(content)


def filter_wheel(wheel_path: str, exclude_pattern: str) -> None:
    """
    Remove files matching exclude pattern from a wheel.

    Args:
        wheel_path: Path to the wheel file
        exclude_pattern: Directory name to exclude (e.g., "_v1" or "_v0")
    """
    wheel_path = Path(wheel_path)
    if not wheel_path.exists():
        print(f"❌ Wheel not found: {wheel_path}")
        sys.exit(1)

    print(f"  Processing: {wheel_path.name}")
    print(f"  Excluding: {exclude_pattern}/")

    # Create temp directory for extraction
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Extract wheel
        with zipfile.ZipFile(wheel_path, "r") as zf:
            zf.extractall(tmpdir)

        # Find and remove excluded directories
        removed_count = 0
        for item in tmpdir.rglob(f"*/{exclude_pattern}"):
            if item.is_dir():
                print(f"  Removing: {item.relative_to(tmpdir)}")
                shutil.rmtree(item)
                removed_count += 1

        # Also check top-level (shouldn't happen but be safe)
        for item in tmpdir.glob(exclude_pattern):
            if item.is_dir():
                print(f"  Removing: {item.relative_to(tmpdir)}")
                shutil.rmtree(item)
                removed_count += 1

        if removed_count == 0:
            print(f"  ⚠️  No directories matching '{exclude_pattern}' found")
            return

        # Update RECORD file
        record_files = list(tmpdir.rglob("*.dist-info/RECORD"))
        if record_files:
            record_file = record_files[0]
            dist_info_dir = record_file.parent

            # Read existing RECORD and filter out excluded entries
            new_record_lines = []
            with open(record_file, "r") as f:
                for line in f:
                    # Skip lines for excluded files
                    if f"/{exclude_pattern}/" not in line and not line.startswith(
                        f"{exclude_pattern}/"
                    ):
                        new_record_lines.append(line)

            # Write updated RECORD (without recalculating hashes for remaining files)
            with open(record_file, "w") as f:
                f.writelines(new_record_lines)

        # Repack wheel
        wheel_path.unlink()  # Remove original
        with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in tmpdir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(tmpdir)
                    zf.write(file_path, arcname)

    print(f"  ✅ Removed {removed_count} director{'y' if removed_count == 1 else 'ies'}")


def main():
    parser = argparse.ArgumentParser(description="Filter wheel contents")
    parser.add_argument("wheel", help="Path to wheel file")
    parser.add_argument(
        "--exclude", required=True, help="Directory name to exclude (e.g., _v1)"
    )

    args = parser.parse_args()
    filter_wheel(args.wheel, args.exclude)


if __name__ == "__main__":
    main()

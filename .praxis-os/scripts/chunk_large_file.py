#!/usr/bin/env python3
"""
Chunk Large File Script

Splits a large file into manageable chunks that can be read individually.
Useful for analyzing session exports or other large text files that exceed context limits.

Usage:
    python scripts/chunk_large_file.py <input_file> [lines_per_chunk]

Example:
    python scripts/chunk_large_file.py other-sessions/cline_task_oct-11-2025_1-16-57-pm.md 1000
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple


def chunk_file(input_path: str, lines_per_chunk: int = 1000) -> List[str]:
    """
    Split a large file into smaller chunks.

    :param input_path: Path to the input file
    :param lines_per_chunk: Number of lines per chunk
    :return: List of created chunk file paths
    :raises FileNotFoundError: If input file doesn't exist
    :raises ValueError: If lines_per_chunk is invalid
    """
    if lines_per_chunk < 1:
        raise ValueError("lines_per_chunk must be at least 1")

    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Create output directory
    output_dir = input_file.parent / f"{input_file.stem}_chunks"
    output_dir.mkdir(exist_ok=True)

    chunk_files = []
    chunk_index = []
    chunk_num = 0
    current_chunk = []
    total_lines = 0

    print(f"Reading: {input_path}")
    print(f"Output directory: {output_dir}")
    print(f"Lines per chunk: {lines_per_chunk}")
    print()

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                current_chunk.append(line)
                total_lines += 1

                if len(current_chunk) >= lines_per_chunk:
                    # Write chunk
                    chunk_path = output_dir / f"chunk_{chunk_num:03d}.md"
                    with open(chunk_path, "w", encoding="utf-8") as chunk_f:
                        chunk_f.writelines(current_chunk)

                    # Record info
                    start_line = line_num - len(current_chunk) + 1
                    end_line = line_num
                    chunk_files.append(str(chunk_path))
                    chunk_index.append(
                        {
                            "chunk": chunk_num,
                            "file": chunk_path.name,
                            "lines": f"{start_line}-{end_line}",
                            "size": len(current_chunk),
                        }
                    )

                    print(
                        f"✓ Created {chunk_path.name}: lines {start_line}-{end_line} ({len(current_chunk)} lines)"
                    )

                    # Reset
                    current_chunk = []
                    chunk_num += 1

            # Write final chunk if any lines remain
            if current_chunk:
                chunk_path = output_dir / f"chunk_{chunk_num:03d}.md"
                with open(chunk_path, "w", encoding="utf-8") as chunk_f:
                    chunk_f.writelines(current_chunk)

                start_line = total_lines - len(current_chunk) + 1
                end_line = total_lines
                chunk_files.append(str(chunk_path))
                chunk_index.append(
                    {
                        "chunk": chunk_num,
                        "file": chunk_path.name,
                        "lines": f"{start_line}-{end_line}",
                        "size": len(current_chunk),
                    }
                )

                print(
                    f"✓ Created {chunk_path.name}: lines {start_line}-{end_line} ({len(current_chunk)} lines)"
                )

    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        raise

    # Create index file
    index_path = output_dir / "INDEX.md"
    with open(index_path, "w", encoding="utf-8") as idx_f:
        idx_f.write(f"# Chunk Index\n\n")
        idx_f.write(f"**Source File:** `{input_path}`\n")
        idx_f.write(f"**Total Lines:** {total_lines:,}\n")
        idx_f.write(f"**Total Chunks:** {len(chunk_index)}\n")
        idx_f.write(f"**Lines per Chunk:** {lines_per_chunk}\n\n")
        idx_f.write("## Chunks\n\n")
        idx_f.write("| Chunk | File | Line Range | Lines |\n")
        idx_f.write("|-------|------|------------|-------|\n")

        for info in chunk_index:
            idx_f.write(
                f"| {info['chunk']} | {info['file']} | {info['lines']} | {info['size']} |\n"
            )

        idx_f.write("\n## Usage\n\n")
        idx_f.write("Read chunks individually with:\n")
        idx_f.write("```\n")
        idx_f.write(f"read_file {output_dir}/chunk_XXX.md\n")
        idx_f.write("```\n")

    print()
    print(f"✓ Created index: {index_path}")
    print()
    print(f"Summary:")
    print(f"  Total lines: {total_lines:,}")
    print(f"  Chunks created: {len(chunk_index)}")
    print(f"  Output directory: {output_dir}")
    print()
    print(f"Next steps:")
    print(f"  1. Read the index: read_file {index_path}")
    print(f"  2. Read specific chunks: read_file {output_dir}/chunk_000.md")

    return chunk_files


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: python scripts/chunk_large_file.py <input_file> [lines_per_chunk]"
        )
        print()
        print("Example:")
        print(
            "  python scripts/chunk_large_file.py other-sessions/cline_task_oct-11-2025_1-16-57-pm.md 1000"
        )
        sys.exit(1)

    input_path = sys.argv[1]
    lines_per_chunk = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    try:
        chunk_file(input_path, lines_per_chunk)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

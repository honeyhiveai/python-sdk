#!/usr/bin/env python3
"""
Generate v1 Client from OpenAPI Specification

This script generates the v1 API client from the OpenAPI specification
using openapi-python-client. The generated code is placed in src/honeyhive/_v1/
and will be excluded from v0.x builds.

Usage:
    python scripts/generate_v1_client.py

The generated client includes:
    - src/honeyhive/_v1/client/     - HTTP client classes
    - src/honeyhive/_v1/models/     - Pydantic models
    - src/honeyhive/_v1/api/        - API endpoint methods
    - src/honeyhive/_v1/types/      - Type definitions
"""

import shutil
import subprocess
import sys
from pathlib import Path

# Get the repo root directory
REPO_ROOT = Path(__file__).parent.parent
OPENAPI_SPEC = REPO_ROOT / "openapi" / "v1.yaml"
OUTPUT_DIR = REPO_ROOT / "src" / "honeyhive" / "_v1"
TEMP_OUTPUT = REPO_ROOT / ".generated_v1_temp"


def run_generator() -> bool:
    """
    Run openapi-python-client to generate the v1 client.

    Returns True if successful, False otherwise.
    """
    print("🚀 Generating v1 Client (openapi-python-client)")
    print("=" * 50)
    print(f"📖 OpenAPI Spec: {OPENAPI_SPEC}")
    print(f"📝 Output Dir: {OUTPUT_DIR}")
    print()

    if not OPENAPI_SPEC.exists():
        print(f"❌ OpenAPI spec not found: {OPENAPI_SPEC}")
        return False

    # Clean up any previous temp output
    if TEMP_OUTPUT.exists():
        shutil.rmtree(TEMP_OUTPUT)

    # Run openapi-python-client
    # Use --meta none to skip pyproject.toml generation (we integrate into existing package)
    # Output to temp directory first, then move the inner package
    cmd = [
        "openapi-python-client",
        "generate",
        "--path",
        str(OPENAPI_SPEC),
        "--output-path",
        str(TEMP_OUTPUT),
        "--meta",
        "none",
        "--overwrite",
    ]

    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Generation failed!")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        return False

    # Show any warnings
    if result.stderr:
        print(f"⚠️  Warnings:\n{result.stderr}")

    print("✅ openapi-python-client generation successful!")
    print()

    return True


def move_generated_code() -> bool:
    """
    Move generated code from temp directory to _v1/.

    With --meta none, openapi-python-client puts files directly in output:
        .generated_v1_temp/
        ├── __init__.py
        ├── client.py
        ├── models/
        ├── api/
        └── types.py

    We move the entire temp directory contents to src/honeyhive/_v1/
    """
    print("📦 Moving generated code to _v1/...")

    if not TEMP_OUTPUT.exists():
        print(f"❌ Temp output directory not found: {TEMP_OUTPUT}")
        return False

    # With --meta none, generated files are directly in temp output
    # Check for __init__.py to confirm this is the package root
    if (TEMP_OUTPUT / "__init__.py").exists():
        generated_pkg = TEMP_OUTPUT
    else:
        # Fall back: look for a subdirectory containing __init__.py
        subdirs = [
            d
            for d in TEMP_OUTPUT.iterdir()
            if d.is_dir() and (d / "__init__.py").exists()
        ]
        if not subdirs:
            print(f"❌ Could not find generated package in {TEMP_OUTPUT}")
            return False
        generated_pkg = subdirs[0]

    print(f"  Generated package root: {generated_pkg}")

    # Clean existing _v1 directory
    if OUTPUT_DIR.exists():
        print(f"  Removing existing {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)

    # Copy generated package to _v1, ignoring cache directories
    def ignore_patterns(directory, files):
        return [f for f in files if f.startswith(".") or f == "__pycache__"]

    shutil.copytree(str(generated_pkg), str(OUTPUT_DIR), ignore=ignore_patterns)

    # Clean up temp directory
    shutil.rmtree(TEMP_OUTPUT)

    # Add module docstring to __init__.py
    init_file = OUTPUT_DIR / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        if not content.startswith('"""'):
            new_content = (
                '"""v1 API client implementation.\n\nThis module is auto-generated and excluded from v0.x builds.\n"""\n\n'
                + content
            )
            init_file.write_text(new_content)

    print("✅ Code moved successfully!")
    return True


def list_generated_files() -> None:
    """List the generated files."""
    print()
    print("📁 Generated Files:")

    if not OUTPUT_DIR.exists():
        print("  (none)")
        return

    for path in sorted(OUTPUT_DIR.rglob("*.py")):
        relative = path.relative_to(REPO_ROOT)
        print(f"  • {relative}")


def main() -> int:
    """Main entry point."""
    if not run_generator():
        return 1

    if not move_generated_code():
        return 1

    list_generated_files()

    print()
    print("🎉 v1 client generation complete!")
    print()
    print("Next steps:")
    print("  1. Run 'make format' to format generated code")
    print("  2. Run 'make lint' to check for issues")
    print("  3. Test the generated client")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Generate Python SDK Client from OpenAPI Specification

This script generates a complete Pydantic-based API client from the OpenAPI
specification using openapi-python-generator. The generated code includes:
- Pydantic v2 models for all schemas
- Sync and async service functions for all endpoints
- API configuration with Bearer auth support

Usage:
    python scripts/generate_client.py [--spec PATH] [--minimal]

Options:
    --spec PATH    Path to OpenAPI spec (default: openapi/v1.yaml)
    --minimal      Use minimal spec for testing (openapi/v1_minimal.yaml)

The generated client is written to:
    src/honeyhive/_generated/
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Get the repo root directory
REPO_ROOT = Path(__file__).parent.parent
DEFAULT_SPEC = REPO_ROOT / "openapi" / "v1.yaml"
MINIMAL_SPEC = REPO_ROOT / "openapi" / "v1_minimal.yaml"
OUTPUT_DIR = REPO_ROOT / "src" / "honeyhive" / "_generated"
TEMP_DIR = REPO_ROOT / ".generated_temp"


def clean_output_dir(output_dir: Path) -> None:
    """Remove existing generated code."""
    if output_dir.exists():
        print(f"🧹 Cleaning existing generated code: {output_dir}")
        shutil.rmtree(output_dir)


def clean_temp_dir(temp_dir: Path) -> None:
    """Remove temporary generation directory."""
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def run_generator(spec_path: Path, temp_dir: Path) -> bool:
    """
    Run openapi-python-generator to create the client.

    Returns True if successful, False otherwise.
    """
    cmd = [
        "openapi-python-generator",
        str(spec_path),
        str(temp_dir),
        "--library",
        "httpx",
        "--pydantic-version",
        "v2",
        "--formatter",
        "black",
    ]

    print(f"Running: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Generator failed with return code {e.returncode}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def move_generated_code(temp_dir: Path, output_dir: Path) -> bool:
    """
    Move generated code from temp directory to final location.

    The generator outputs directly to the temp directory with:
    - __init__.py, api_config.py
    - models/ subdirectory
    - services/ subdirectory

    Returns True if successful, False otherwise.
    """
    # Verify temp directory has expected content
    if not (temp_dir / "api_config.py").exists():
        print(f"❌ Expected api_config.py not found in {temp_dir}")
        return False

    # Move entire temp directory to output location
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(temp_dir), str(output_dir))
    print(f"📦 Moved generated code to {output_dir.relative_to(REPO_ROOT)}")

    return True


def post_process(output_dir: Path) -> bool:
    """
    Apply any post-processing customizations to the generated code.

    Returns True if successful, False otherwise.
    """
    print("🔧 Applying post-processing customizations...")

    # Ensure __init__.py exists at the package root
    init_file = output_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Auto-generated HoneyHive API client."""\n')
        print("  ✓ Created __init__.py")

    # Fix serialization to exclude None values
    # The API rejects null values, so we must use model_dump(exclude_none=True)
    services_dir = output_dir / "services"
    if services_dir.exists():
        fixed_count = 0
        for service_file in services_dir.glob("*.py"):
            content = service_file.read_text()
            if "data.dict()" in content:
                content = content.replace(
                    "data.dict()", "data.model_dump(exclude_none=True)"
                )
                service_file.write_text(content)
                fixed_count += 1
        if fixed_count > 0:
            print(f"  ✓ Fixed serialization in {fixed_count} service files")

    print("  ✓ Post-processing complete")
    return True


def main() -> int:
    """Generate client from OpenAPI specification."""
    parser = argparse.ArgumentParser(
        description="Generate Python SDK client from OpenAPI spec"
    )
    parser.add_argument(
        "--spec",
        type=Path,
        help=f"Path to OpenAPI spec (default: {DEFAULT_SPEC.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Use minimal spec for testing",
    )
    args = parser.parse_args()

    # Determine which spec to use
    if args.spec:
        spec_path = args.spec
    elif args.minimal:
        spec_path = MINIMAL_SPEC
    else:
        spec_path = DEFAULT_SPEC

    print("🚀 Generating SDK Client (openapi-python-generator)")
    print("=" * 55)
    print()

    # Validate that the OpenAPI spec exists
    if not spec_path.exists():
        print(f"❌ OpenAPI spec not found: {spec_path}")
        return 1

    print(f"📖 OpenAPI Spec: {spec_path.relative_to(REPO_ROOT)}")
    print(f"📝 Output Dir:   {OUTPUT_DIR.relative_to(REPO_ROOT)}")
    print()

    # Clean up any previous temp directory
    clean_temp_dir(TEMP_DIR)

    # Run the generator
    if not run_generator(spec_path, TEMP_DIR):
        clean_temp_dir(TEMP_DIR)
        return 1

    # Clean existing generated code
    clean_output_dir(OUTPUT_DIR)

    # Move generated code to final location (this also removes TEMP_DIR)
    if not move_generated_code(TEMP_DIR, OUTPUT_DIR):
        clean_temp_dir(TEMP_DIR)
        return 1

    # Apply post-processing
    if not post_process(OUTPUT_DIR):
        return 1

    print()
    print("✅ SDK generation successful!")
    print()
    print("📁 Generated Files:")

    # List generated files
    for path in sorted(OUTPUT_DIR.rglob("*.py")):
        print(f"  • {path.relative_to(REPO_ROOT)}")

    print()
    print("💡 Next Steps:")
    print("  1. Review the generated code for correctness")
    print("  2. Update the ergonomic wrapper (client_v1.py) if needed")
    print("  3. Run tests: direnv exec . tox -e py311")
    print("  4. Format code: make format")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

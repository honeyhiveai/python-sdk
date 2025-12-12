#!/usr/bin/env python3
"""
Generate v0 Models and Client from OpenAPI Specification

This script regenerates the Pydantic models from the OpenAPI specification
using datamodel-codegen. This is the lightweight, hand-written API client
approach where models are auto-generated but the client code is maintained
manually.

Usage:
    python scripts/generate_v0_models.py

The generated models are written to:
    src/honeyhive/models/generated.py
"""

import subprocess
import sys
from pathlib import Path

# Get the repo root directory
REPO_ROOT = Path(__file__).parent.parent
OPENAPI_SPEC = REPO_ROOT / "openapi.yaml"
OUTPUT_FILE = REPO_ROOT / "src" / "honeyhive" / "models" / "generated.py"


def main():
    """Generate models from OpenAPI specification."""
    print("🚀 Generating v0 Models (datamodel-codegen)")
    print("=" * 50)

    # Validate that the OpenAPI spec exists
    if not OPENAPI_SPEC.exists():
        print(f"❌ OpenAPI spec not found: {OPENAPI_SPEC}")
        return 1

    print(f"📖 OpenAPI Spec: {OPENAPI_SPEC}")
    print(f"📝 Output File: {OUTPUT_FILE}")
    print()

    # Run datamodel-codegen
    cmd = [
        "datamodel-codegen",
        "--input",
        str(OPENAPI_SPEC),
        "--output",
        str(OUTPUT_FILE),
        "--target-python-version",
        "3.11",
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--use-annotated",
    ]

    print(f"Running: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print()
            print("✅ Model generation successful!")
            print()
            print("📁 Generated Files:")
            print(f"  • {OUTPUT_FILE.relative_to(REPO_ROOT)}")
            print()
            print("💡 Next Steps:")
            print("  1. Review the generated models for correctness")
            print("  2. Run tests to ensure compatibility: make test")
            print("  3. Commit the changes: git add src/honeyhive/models/generated.py && git commit -m 'feat(models): regenerate from updated OpenAPI spec'")
            print()
            return 0
        else:
            print(f"❌ Model generation failed with return code {result.returncode}")
            return 1

    except FileNotFoundError:
        print("❌ datamodel-codegen not found!")
        print()
        print("Please install the datamodel-code-generator package:")
        print("  pip install 'datamodel-code-generator>=0.20.0'")
        print()
        print("Or install the SDK with dev dependencies:")
        print("  pip install -e '.[dev]'")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running datamodel-codegen: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

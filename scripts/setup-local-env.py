#!/usr/bin/env python3
"""
Setup Local Environment for HoneyHive Python SDK Development

This script helps developers set up their local .env file for development
and testing, following Agent OS standards.
"""

import os
import sys
from pathlib import Path


def main():
    """Set up local environment for development."""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    example_file = project_root / "env.integration.example"

    print("🔧 HoneyHive Python SDK - Local Environment Setup")
    print("=" * 60)

    # Check if .env already exists
    if env_file.exists():
        print(f"✅ .env file already exists: {env_file}")

        # Ask if user wants to overwrite
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response not in ["y", "yes"]:
            print("Keeping existing .env file.")
            return

    # Check if example file exists
    if not example_file.exists():
        print(f"❌ Example file not found: {example_file}")
        print("Cannot create .env file without example template.")
        sys.exit(1)

    # Copy example to .env
    try:
        with open(example_file, "r") as f:
            content = f.read()

        with open(env_file, "w") as f:
            f.write(content)

        print(f"✅ Created .env file: {env_file}")
        print()
        print("📝 Next steps:")
        print(f"1. Edit {env_file} with your real credentials")
        print("2. Required: Set HH_API_KEY=your_honeyhive_api_key")
        print("3. Optional: Set LLM provider keys for instrumentor tests")
        print("4. Never commit .env files to git (they're in .gitignore)")
        print()
        print("🚀 You can now run integration tests with:")
        print("   tox -e integration")

    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

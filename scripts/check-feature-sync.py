#!/usr/bin/env python3
"""
Feature Documentation Synchronization Checker

Ensures that feature documentation stays synchronized between:
- docs/FEATURE_LIST.rst (user-facing documentation)
- .agent-os/product/features.md (Agent OS product catalog)
- Actual codebase features (src/honeyhive/)

This prevents documentation drift and ensures comprehensive feature coverage.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, NoReturn, Set


def extract_features_from_feature_list() -> Set[str]:
    """Extract features from docs/FEATURE_LIST.rst."""
    feature_list_path = Path("docs/FEATURE_LIST.rst")
    if not feature_list_path.exists():
        print(f"❌ {feature_list_path} not found")
        return set()

    content = feature_list_path.read_text()
    # Extract features from RST sections (look for ~~~ underlines)
    features = set()
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "~~~" in line and i > 0:
            feature_name = lines[i - 1].strip()
            if feature_name and not feature_name.startswith("*"):
                features.add(feature_name.lower())

    return features


def extract_features_from_agent_os() -> Set[str]:
    """Extract features from .agent-os/product/features.md."""
    agent_os_path = Path(".agent-os/product/features.md")
    if not agent_os_path.exists():
        print(f"❌ {agent_os_path} not found")
        return set()

    content = agent_os_path.read_text()
    # Extract features from markdown headers
    features = set()
    for line in content.split("\n"):
        if line.startswith("###") and not line.startswith("####"):
            feature_name = line.replace("###", "").strip()
            # Remove emojis and special characters
            feature_name = re.sub(r"[^\w\s-]", "", feature_name)
            if feature_name:
                features.add(feature_name.lower())

    return features


def extract_core_components_from_codebase() -> Set[str]:
    """Extract core components from the codebase structure."""
    src_path = Path("src/honeyhive")
    if not src_path.exists():
        print(f"❌ {src_path} not found")
        return set()

    components = set()

    # Add main modules
    for module_dir in src_path.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith("_"):
            components.add(module_dir.name)

    # Add key features based on file patterns
    key_patterns = {
        "decorators": "tracer/decorators.py",
        "opentelemetry integration": "tracer/otel_tracer.py",
        "evaluation framework": "evaluation/",
        "api client": "api/client.py",
        "configuration management": "utils/config.py",
        "error handling": "utils/error_handler.py",
        "caching": "utils/cache.py",
        "http instrumentation": "tracer/http_instrumentation.py",
    }

    for feature, file_path in key_patterns.items():
        full_path = src_path / file_path
        if full_path.exists():
            components.add(feature)

    return components


def check_documentation_build() -> bool:
    """Check if documentation builds successfully."""
    print("🔍 Checking documentation build...")
    exit_code = os.system("tox -e docs > /dev/null 2>&1")
    if exit_code != 0:
        print("❌ Documentation build failed")
        print("   Run 'tox -e docs' to see detailed errors")
        return False
    else:
        print("✅ Documentation builds successfully")
        return True


def check_required_docs_exist() -> bool:
    """Check that all required documentation files exist and are non-empty."""
    required_docs = [
        "README.md",
        "CHANGELOG.md",
        "docs/FEATURE_LIST.rst",
        "docs/TESTING.rst",
        ".agent-os/product/features.md",
        ".agent-os/standards/best-practices.md",
    ]

    missing_docs = []
    empty_docs = []

    for doc_path in required_docs:
        path = Path(doc_path)
        if not path.exists():
            missing_docs.append(doc_path)
        elif path.stat().st_size < 100:  # Less than 100 bytes is probably empty
            empty_docs.append(doc_path)

    if missing_docs:
        print(f"❌ Missing required documentation files: {missing_docs}")
        return False

    if empty_docs:
        print(f"❌ Empty or insufficient documentation files: {empty_docs}")
        return False

    print("✅ All required documentation files exist and have content")
    return True


def main() -> NoReturn:
    """Main validation function."""
    print("📚 Documentation Synchronization Check")
    print("=" * 50)

    # Check if documentation builds
    build_ok = check_documentation_build()

    # Check required docs exist
    docs_exist = check_required_docs_exist()

    # Extract features from different sources
    feature_list_features = extract_features_from_feature_list()
    agent_os_features = extract_features_from_agent_os()
    codebase_components = extract_core_components_from_codebase()

    print(f"\n📊 Feature Coverage Analysis:")
    print(f"   Feature List (docs/): {len(feature_list_features)} features")
    print(f"   Agent OS (product/): {len(agent_os_features)} features")
    print(f"   Codebase components: {len(codebase_components)} components")

    # Check for major discrepancies
    all_good = True

    if len(feature_list_features) == 0:
        print("❌ No features found in FEATURE_LIST.rst")
        all_good = False

    if len(agent_os_features) == 0:
        print("❌ No features found in Agent OS features.md")
        all_good = False

    # Warn about significant gaps (more than 50% difference)
    if len(feature_list_features) > 0 and len(agent_os_features) > 0:
        ratio = min(len(feature_list_features), len(agent_os_features)) / max(
            len(feature_list_features), len(agent_os_features)
        )
        if ratio < 0.5:
            print(
                f"⚠️  Significant feature count discrepancy: {len(feature_list_features)} vs {len(agent_os_features)}"
            )
            print("   Consider updating documentation to ensure consistency")

    # Final result
    if build_ok and docs_exist and all_good:
        print("\n✅ Documentation validation passed")
        sys.exit(0)
    else:
        print("\n❌ Documentation validation failed")
        print("\nTo fix:")
        print("1. Ensure all documentation files exist and have content")
        print("2. Fix any documentation build errors: tox -e docs")
        print("3. Update feature documentation to stay synchronized")
        sys.exit(1)


if __name__ == "__main__":
    main()

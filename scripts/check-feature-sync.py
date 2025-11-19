#!/usr/bin/env python3
"""
Feature Documentation Synchronization Checker

Ensures that feature documentation stays synchronized between:
- docs/reference/index.rst (modern API reference documentation)
- .praxis-os/workspace/product/features.md (praxis OS product catalog)
- Actual codebase features (src/honeyhive/)

This prevents documentation drift and ensures comprehensive feature coverage.

Note: docs/FEATURE_LIST.rst and docs/TESTING.rst are legacy files maintained
for backward compatibility only. New feature documentation should be added
to the Divio-structured documentation in docs/reference/, docs/tutorials/,
docs/how-to/, and docs/explanation/.
"""

import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import List, NoReturn, Set


def extract_features_from_reference_docs() -> Set[str]:
    """Extract features from docs/reference/index.rst (modern documentation)."""
    reference_path = Path("docs/reference/index.rst")
    if not reference_path.exists():
        print(f"❌ {reference_path} not found")
        return set()

    content = reference_path.read_text()
    features = set()

    # Extract features from RST sections and bullet points
    lines = content.split("\n")
    for i, line in enumerate(lines):
        # Look for section headers with underlines
        if "~~~" in line and i > 0:
            feature_name = lines[i - 1].strip()
            if feature_name and not feature_name.startswith("*"):
                features.add(feature_name.lower())

        # Look for bullet points with ** bold features
        if line.strip().startswith("- **") and "**:" in line:
            feature_match = re.search(r"\*\*(.*?)\*\*", line)
            if feature_match:
                features.add(feature_match.group(1).lower())

    return features


def extract_features_from_praxis_os() -> Set[str]:
    """Extract features from .praxis-os/workspace/product/features.md."""
    praxis_os_path = Path(".praxis-os/workspace/product/features.md")
    if not praxis_os_path.exists():
        print(f"❌ {praxis_os_path} not found")
        return set()

    content = praxis_os_path.read_text()
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
    """Check if documentation builds successfully with enhanced error reporting."""
    print("🔍 Checking documentation build...")
    
    # Check for existing build artifacts that might cause conflicts
    build_dir = Path("docs/_build")
    if build_dir.exists():
        print(f"   Found existing build directory: {build_dir}")
        try:
            # Try to clean up existing build
            import shutil
            shutil.rmtree(build_dir)
            print("   Cleaned up existing build directory")
        except Exception as e:
            print(f"   Warning: Could not clean build directory: {e}")
    
    # Use subprocess for better error handling and output capture
    start_time = time.time()
    try:
        print("   Running: tox -e docs")
        result = subprocess.run(
            ["tox", "-e", "docs"],
            capture_output=True,
            text=True,
            timeout=180,  # 3 minute timeout
            cwd=os.getcwd()
        )
        elapsed_time = time.time() - start_time
        print(f"   Build completed in {elapsed_time:.2f} seconds")
        
        if result.returncode == 0:
            print("✅ Documentation builds successfully")
            return True
        else:
            print("❌ Documentation build failed")
            print(f"   Exit code: {result.returncode}")
            print(f"   Working directory: {os.getcwd()}")
            print(f"   Command: tox -e docs")
            
            # Enhanced error reporting
            if result.stdout:
                print(f"   STDOUT (last 1000 chars):")
                print(f"   {result.stdout[-1000:]}")
            
            if result.stderr:
                print(f"   STDERR (last 1000 chars):")
                print(f"   {result.stderr[-1000:]}")
            
            # Check for common error patterns
            combined_output = (result.stdout or "") + (result.stderr or "")
            if "Directory not empty" in combined_output:
                print("   🔍 Detected 'Directory not empty' error - likely build artifact conflict")
            if "Theme error" in combined_output:
                print("   🔍 Detected 'Theme error' - likely Sphinx configuration issue")
            if "OSError" in combined_output:
                print("   🔍 Detected OSError - likely file system or permission issue")
            
            print("   Run 'tox -e docs' manually to see full detailed errors")
            return False
            
    except subprocess.TimeoutExpired as e:
        elapsed_time = time.time() - start_time
        print(f"❌ Documentation build timed out after {elapsed_time:.2f} seconds")
        print("   This may indicate a hanging process or resource contention")
        print("   Run 'tox -e docs' manually to see detailed errors")
        return False
        
    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        print("   Ensure tox is installed and available in PATH")
        print(f"   Current PATH: {os.environ.get('PATH', 'Not set')}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error during documentation build: {e}")
        print(f"   Exception type: {type(e).__name__}")
        print(f"   Traceback:")
        traceback.print_exc()
        return False


def check_required_docs_exist() -> bool:
    """Check that all required documentation files exist and are non-empty."""
    required_docs = [
        "README.md",
        "CHANGELOG.md",
        "docs/reference/index.rst",
        "docs/tutorials/index.rst",
        "docs/how-to/index.rst",
        "docs/explanation/index.rst",
        ".praxis-os/workspace/product/features.md",
        ".praxis-os/standards/universal/best-practices.md",
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
    """Main validation function with enhanced diagnostics."""
    start_time = time.time()
    print("📚 Documentation Synchronization Check")
    print("=" * 50)
    print(f"🕐 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"🔧 Process ID: {os.getpid()}")
    
    # Environment diagnostics
    print(f"🌍 Environment variables:")
    for key in ['VIRTUAL_ENV', 'PATH', 'PYTHONPATH', 'TOX_ENV_NAME']:
        value = os.environ.get(key, 'Not set')
        print(f"   {key}: {value[:100]}{'...' if len(value) > 100 else ''}")
    
    try:
        # Check if documentation builds
        print(f"\n🔨 Step 1: Documentation Build Check")
        build_ok = check_documentation_build()

        # Check required docs exist
        print(f"\n📋 Step 2: Required Documentation Check")
        docs_exist = check_required_docs_exist()

        # Extract features from different sources
        print(f"\n🔍 Step 3: Feature Extraction")
        reference_docs_features = extract_features_from_reference_docs()
        praxis_os_features = extract_features_from_praxis_os()
        codebase_components = extract_core_components_from_codebase()

        print(f"\n📊 Feature Coverage Analysis:")
        print(
            f"   Reference Docs (docs/reference/): {len(reference_docs_features)} features"
        )
        print(f"   praxis OS (product/): {len(praxis_os_features)} features")
        print(f"   Codebase components: {len(codebase_components)} components")

        # Check for major discrepancies
        all_good = True

        if len(reference_docs_features) == 0:
            print("❌ No features found in docs/reference/index.rst")
            all_good = False

        if len(praxis_os_features) == 0:
            print("❌ No features found in praxis OS features.md")
            all_good = False

        # Warn about significant gaps (more than 50% difference)
        if len(reference_docs_features) > 0 and len(praxis_os_features) > 0:
            ratio = min(len(reference_docs_features), len(praxis_os_features)) / max(
                len(reference_docs_features), len(praxis_os_features)
            )
            if ratio < 0.5:
                print(
                    f"⚠️  Significant feature count discrepancy: {len(reference_docs_features)} vs {len(praxis_os_features)}"
                )
                print("   Consider updating documentation to ensure consistency")

        # Final result
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Total execution time: {elapsed_time:.2f} seconds")
        
        if build_ok and docs_exist and all_good:
            print("\n✅ Documentation validation passed")
            sys.exit(0)
        else:
            print("\n❌ Documentation validation failed")
            print(f"\n🔍 Failure Summary:")
            print(f"   Build OK: {build_ok}")
            print(f"   Docs Exist: {docs_exist}")
            print(f"   Feature Analysis OK: {all_good}")
            print("\nTo fix:")
            print("1. Ensure all documentation files exist and have content")
            print("2. Fix any documentation build errors: tox -e docs")
            print("3. Update feature documentation to stay synchronized")
            sys.exit(1)
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n💥 Unexpected error in main execution after {elapsed_time:.2f} seconds:")
        print(f"   Exception: {e}")
        print(f"   Type: {type(e).__name__}")
        print(f"   Traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

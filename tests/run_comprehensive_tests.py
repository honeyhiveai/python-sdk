#!/usr/bin/env python3
"""
Comprehensive test runner for HoneyHive SDK.

This script runs all tests in the correct order to ensure proper test isolation
and comprehensive coverage of all SDK functionality.
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ {description} completed successfully in {duration:.2f}s")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"❌ {description} failed after {duration:.2f}s")
        print(f"Exit code: {e.returncode}")
        
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        
        return False


def run_pytest_tests(test_path, description):
    """Run pytest tests for a specific path."""
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ]
    
    return run_command(cmd, description)


def run_tox_tests(env=None, description=""):
    """Run tests using tox."""
    cmd = ["tox"]
    if env:
        cmd.extend(["-e", env])
    
    return run_command(cmd, description=f"Tox tests{f' ({env})' if env else ''}")


def main():
    """Main test runner."""
    print("🚀 Starting Comprehensive HoneyHive SDK Test Suite")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run from the project root.")
        sys.exit(1)
    
    # Check if tox is available
    try:
        import tox
        print("✅ Tox is available")
    except ImportError:
        print("❌ Tox is not available. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "tox"], check=True)
    
    # Run tests in order of dependency
    test_results = []
    
    # 1. Run unit tests
    print("\n📋 Phase 1: Unit Tests")
    print("=" * 50)
    
    unit_tests = [
        ("Unit Tests - Utils", run_pytest_tests("tests/unit/test_utils.py", "Unit tests for utilities")),
        ("Unit Tests - Client", run_pytest_tests("tests/unit/test_client.py", "Unit tests for client")),
        ("Unit Tests - Tracer", run_pytest_tests("tests/unit/test_tracer.py", "Unit tests for tracer")),
        ("Unit Tests - API", run_pytest_tests("tests/unit/test_api.py", "Unit tests for API")),
        ("Unit Tests - Evaluation", run_pytest_tests("tests/unit/test_evaluation.py", "Unit tests for evaluation")),
        ("Unit Tests - HTTP Instrumentation", run_pytest_tests("tests/unit/test_http_instrumentation.py", "Unit tests for HTTP instrumentation")),
        ("Unit Tests - Advanced Features", run_pytest_tests("tests/unit/test_advanced_features.py", "Unit tests for advanced features")),
        ("Unit Tests - CLI", run_pytest_tests("tests/unit/test_cli.py", "Unit tests for CLI")),
        ("Unit Tests - Traceloop Compatibility", run_pytest_tests("tests/unit/test_traceloop_compatibility.py", "Unit tests for traceloop compatibility")),
    ]
    
    # Add unit test results
    for test_name, result in unit_tests:
        test_results.append((test_name, result))
    
    # 2. Run tox tests for all Python versions
    print("\n📋 Phase 2: Multi-Python Tests (Tox)")
    test_results.append((
        "Tox - Python 3.11",
        run_tox_tests("py311", "Python 3.11 compatibility")
    ))
    
    test_results.append((
        "Tox - Python 3.12",
        run_tox_tests("py312", "Python 3.12 compatibility")
    ))
    
    test_results.append((
        "Tox - Python 3.13",
        run_tox_tests("py313", "Python 3.13 compatibility")
    ))
    
    # 3. Run comprehensive tox test
    print("\n📋 Phase 3: Comprehensive Tox Test")
    test_results.append((
        "Tox - All Environments",
        run_tox_tests("", "All tox environments")
    ))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! The SDK is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

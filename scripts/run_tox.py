#!/usr/bin/env python3
"""
Helper script to run tox tests for HoneyHive Python SDK.
This script provides convenient commands to run tests across different Python versions.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, capture_output=capture_output, text=True)
    if capture_output and result.stdout:
        print(result.stdout)
    if capture_output and result.stderr:
        print(result.stderr)
    return result


def check_tox_installed():
    """Check if tox is installed."""
    try:
        result = run_command([sys.executable, "-m", "tox", "--version"], check=False)
        return result.returncode == 0
    except Exception:
        return False


def install_tox():
    """Install tox if not already installed."""
    print("Installing tox...")
    run_command([sys.executable, "-m", "pip", "install", "tox>=4.0"])


def list_environments():
    """List available tox environments."""
    print("Available tox environments:")
    run_command([sys.executable, "-m", "tox", "-l"])


def run_tests(env=None, args=None):
    """Run tests with tox."""
    cmd = [sys.executable, "-m", "tox"]
    
    if env:
        cmd.extend(["-e", env])
    
    if args:
        cmd.extend(["--"] + args)
    
    print(f"Running tests with command: {' '.join(cmd)}")
    run_command(cmd)


def run_lint():
    """Run linting checks."""
    print("Running linting checks...")
    run_command([sys.executable, "-m", "tox", "-e", "lint"])


def run_format_check():
    """Run code formatting checks."""
    print("Running code formatting checks...")
    run_command([sys.executable, "-m", "tox", "-e", "format"])


def run_docs():
    """Build documentation."""
    print("Building documentation...")
    run_command([sys.executable, "-m", "tox", "-e", "docs"])


def main():
    parser = argparse.ArgumentParser(description="HoneyHive Python SDK Tox Test Runner")
    parser.add_argument("command", choices=["test", "lint", "format", "docs", "list", "install"], 
                       help="Command to run")
    parser.add_argument("-e", "--env", help="Specific environment to run (e.g., py39, py310)")
    parser.add_argument("--args", nargs="*", help="Additional arguments to pass to pytest")
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    if args.command == "install":
        if not check_tox_installed():
            install_tox()
        else:
            print("tox is already installed.")
        return
    
    if not check_tox_installed():
        print("tox is not installed. Installing...")
        install_tox()
    
    if args.command == "list":
        list_environments()
    elif args.command == "test":
        run_tests(args.env, args.args)
    elif args.command == "lint":
        run_lint()
    elif args.command == "format":
        run_format_check()
    elif args.command == "docs":
        run_docs()


if __name__ == "__main__":
    main()

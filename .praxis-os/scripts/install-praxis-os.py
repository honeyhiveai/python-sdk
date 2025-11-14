#!/usr/bin/env python3
"""
prAxIs OS - Fast Installation Script

Handles mechanical file operations (clone, copy, validate).
LLM handles intelligent tasks (language detection, standards generation, venv, RAG).

Usage:
    python install-praxis-os.py [target_directory]

    If target_directory not provided, uses current directory.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict

# Configuration
REPO_URL = "https://github.com/honeyhiveai/praxis-os.git"
MIN_PYTHON = (3, 9)
MIN_DISK_MB = 200  # Minimal base install (RAG indexes grow over time)


def main():
    """Main installation flow"""
    print("=" * 60)
    print("prAxIs OS Installer v1.0.0")
    print("=" * 60)
    print()

    # Parse target directory
    target = parse_target()
    print(f"Target directory: {target}")
    print()

    # Check prerequisites
    print("Step 1/8: Checking prerequisites")
    check_prerequisites(target)
    print()

    # Clone repository
    print("Step 2/8: Cloning repository")
    temp_dir = clone_repository()
    print()

    # Create directory structure
    print("Step 3/8: Creating directory structure")
    create_directories(target)
    print()

    # Copy files
    print("Step 4/8: Copying files")
    stats = copy_files(temp_dir, target)
    print()

    # Create venv and install dependencies
    print("Step 5/8: Creating virtual environment")
    create_venv_and_install(target)
    print()

    # Configure .gitignore
    print("Step 6/8: Configuring .gitignore")
    configure_gitignore(target)
    print()

    # Create rebuild flag for RAG index
    print("Step 7/8: Scheduling RAG index build")
    create_rebuild_flag(target)
    print()

    # Validate installation
    print("Step 8/8: Validating installation")
    validate_installation(target, stats)
    print()

    # Cleanup
    cleanup(temp_dir)

    # Print success and next steps
    print_success(target, stats)


def parse_target() -> Path:
    """
    Get target directory from args or use current directory.

    Returns:
        Path: Resolved target directory
    """
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = Path.cwd()

    return target.resolve()


def check_prerequisites(target: Path):
    """
    Check git, Python version, and disk space.

    Args:
        target: Target installation directory

    Raises:
        SystemExit: If prerequisites not met
    """
    # Check git
    try:
        result = subprocess.run(
            ["git", "--version"], capture_output=True, check=True, text=True
        )
        git_version = result.stdout.strip()
        print(f"✓ Git detected: {git_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Git not found")
        print("  Install git: https://git-scm.com/downloads")
        sys.exit(1)

    # Check Python version
    if sys.version_info < MIN_PYTHON:
        print(f"✗ Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required")
        print(f"  Current: Python {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print(
        f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected"
    )

    # Check disk space
    stat = shutil.disk_usage(target)
    free_mb = stat.free // (1024 * 1024)
    if free_mb < MIN_DISK_MB:
        print(f"✗ Insufficient disk space: {free_mb}MB < {MIN_DISK_MB}MB")
        sys.exit(1)
    print(f"✓ {free_mb}MB disk space available")


def clone_repository() -> Path:
    """
    Clone repository to temporary directory.

    Returns:
        Path: Temporary directory with cloned repo

    Raises:
        SystemExit: If clone fails
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="praxis-os-install-"))

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, str(temp_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✓ Cloned to {temp_dir}")
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f"✗ Clone failed: {e.stderr}")
        print("  Check internet connection and GitHub access")
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)


def create_directories(target: Path):
    """
    Create .praxis-os directory structure.

    Args:
        target: Target installation directory
    """
    base = target / ".praxis-os"

    # Core directories that need to exist
    directories = [
        # Standards (universal from framework, development for project)
        base / "standards" / "development",
        # Workflows (no universal/ prefix - flattened)
        base / "workflows",
        # MCP Server
        base / "ouroboros",
        # Specs (organized by status)
        base / "specs" / "approved",
        base / "specs" / "completed",
        base / "specs" / "review",
        # Workspace (temporary files)
        base / "workspace" / "design",
        base / "workspace" / "analysis",
        base / "workspace" / "scratch",
        # Cache (RAG index will be stored here)
        base / ".cache" / "vector_index",
        # Scripts directory
        base / "scripts",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    print(f"✓ Created directory structure at {base}")


def validate_directory_copy(src_dir: Path, dest_dir: Path, name: str):
    """
    Validate that all files were copied from source to destination.

    Counts source files with ignore patterns applied (matching shutil.copytree behavior).
    Counts destination files directly (no ignore patterns needed).

    Args:
        src_dir: Source directory
        dest_dir: Destination directory
        name: Human-readable name for error messages

    Raises:
        SystemExit: If file counts don't match
    """
    # Count source with ignore patterns (matches what copytree will copy)
    src_count = count_files(src_dir, respect_ignore_patterns=True)
    # Count destination normally (already filtered by copytree)
    dest_count = count_files(dest_dir, respect_ignore_patterns=False)

    if src_count != dest_count:
        print(f"\n✗ File count mismatch in {name}/")
        print(f"  Expected: {src_count} files")
        print(f"  Found:    {dest_count} files")
        print(f"  Missing:  {src_count - dest_count} files")
        sys.exit(1)


def copy_files(source: Path, target: Path) -> Dict[str, int]:
    """
    Copy files from source to target using simple recursive copies.

    Behavior:
      - universal/workflows → .praxis-os/workflows (flatten)
      - universal/standards → .praxis-os/standards/universal (keep namespace)
      - dist/ouroboros → .praxis-os/ouroboros (direct copy)
      - scripts → .praxis-os/scripts (RAG index builder, etc.)

    After each copy, validates that source and destination file counts match.

    Args:
        source: Source directory (cloned repo)
        target: Target directory (installation location)

    Returns:
        Dict with file counts per category

    Raises:
        SystemExit: If copy or validation fails
    """
    base = target / ".praxis-os"
    stats = {}

    # Patterns to ignore during copy
    ignore_patterns = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        ".pytest_cache",
        ".mypy_cache",
        ".praxis-os",
        ".cursor",  # Don't copy nested artifacts from ouroboros
    )

    try:
        # 1. Workflows (flatten - no universal/ prefix in consumer installs)
        print("  Copying workflows...", end=" ", flush=True)
        src_workflows = source / "universal" / "workflows"
        dest_workflows = base / "workflows"
        shutil.copytree(
            src_workflows, dest_workflows, dirs_exist_ok=True, ignore=ignore_patterns
        )
        validate_directory_copy(src_workflows, dest_workflows, "workflows")
        stats["workflows"] = count_files(dest_workflows)
        print(f"✓ {stats['workflows']} files")

        # 2. Standards (keep universal/ namespace to distinguish from development/)
        print("  Copying standards...", end=" ", flush=True)
        src_standards = source / "universal" / "standards"
        dest_standards = base / "standards" / "universal"
        shutil.copytree(
            src_standards, dest_standards, dirs_exist_ok=True, ignore=ignore_patterns
        )
        validate_directory_copy(src_standards, dest_standards, "standards")
        stats["standards"] = count_files(dest_standards)
        print(f"✓ {stats['standards']} files")

        # 3. MCP Server (entire Python package)
        print("  Copying MCP server...", end=" ", flush=True)
        src_mcp = source / "dist" / "ouroboros"
        dest_mcp = base / "ouroboros"
        shutil.copytree(src_mcp, dest_mcp, dirs_exist_ok=True, ignore=ignore_patterns)
        validate_directory_copy(src_mcp, dest_mcp, "ouroboros")
        stats["ouroboros"] = count_files(dest_mcp)
        print(f"✓ {stats['ouroboros']} files")

        # 4. Scripts (RAG index builder and other utilities)
        print("  Copying scripts...", end=" ", flush=True)
        src_scripts = source / "scripts"
        dest_scripts = base / "scripts"
        shutil.copytree(
            src_scripts, dest_scripts, dirs_exist_ok=True, ignore=ignore_patterns
        )
        validate_directory_copy(src_scripts, dest_scripts, "scripts")
        stats["scripts"] = count_files(dest_scripts)
        print(f"✓ {stats['scripts']} files")

        stats["total"] = sum(stats.values())
        return stats

    except Exception as e:
        print(f"\n✗ Copy failed: {e}")
        sys.exit(1)


def count_files(directory: Path, respect_ignore_patterns: bool = False) -> int:
    """
    Recursively count files in directory.

    Args:
        directory: Directory to count files in
        respect_ignore_patterns: If True, exclude files matching standard ignore patterns

    Returns:
        Number of files (not directories)
    """
    # Patterns to exclude (matching copy_files ignore patterns)
    ignore_names = {
        "__pycache__",
        ".DS_Store",
        ".pytest_cache",
        ".mypy_cache",
        ".praxis-os",
        ".cursor",
    }
    ignore_extensions = {".pyc"}

    count = 0
    for item in directory.rglob("*"):
        if not item.is_file():
            continue

        # Apply ignore patterns if requested
        if respect_ignore_patterns:
            # Skip if any parent directory matches ignore_names
            if any(part in ignore_names for part in item.parts):
                continue
            # Skip if file extension matches
            if item.suffix in ignore_extensions:
                continue

        count += 1

    return count


def validate_installation(target: Path, stats: Dict[str, int]):
    """
    Validate installation structure exists.

    File count validation is done during copy via validate_directory_copy().
    This function just ensures the directory structure was created correctly.

    Args:
        target: Target installation directory
        stats: File count statistics from copy

    Raises:
        SystemExit: If validation fails
    """
    base = target / ".praxis-os"

    # Check that all expected directories exist
    required_dirs = [
        base / "workflows",
        base / "standards" / "universal",
        base / "standards" / "development",
        base / "ouroboros",
        base / "scripts",
        base / "specs" / "approved",
        base / "specs" / "completed",
        base / "specs" / "review",
        base / "workspace" / "design",
        base / "workspace" / "analysis",
        base / "workspace" / "scratch",
        base / ".cache" / "vector_index",
        base / "venv",
    ]

    for directory in required_dirs:
        if not directory.exists():
            print(f"✗ Missing directory: {directory}")
            sys.exit(1)

    print("✓ Directory structure validated")
    print(f"✓ File integrity validated (exact counts)")
    print(f"✓ Total: {stats['total']} files copied")


def create_venv_and_install(target: Path):
    """
    Create Python virtual environment and install MCP server dependencies.

    Args:
        target: Target installation directory

    Raises:
        SystemExit: If venv creation or pip install fails
    """
    base = target / ".praxis-os"
    venv_path = base / "venv"

    # Create virtual environment
    print("  Creating Python virtual environment...", end=" ", flush=True)
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✓")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ venv creation failed: {e.stderr}")
        sys.exit(1)

    # Determine pip path based on platform
    if os.name == "nt":  # Windows
        pip_path = venv_path / "Scripts" / "pip"
    else:  # Unix-like (Linux, macOS)
        pip_path = venv_path / "bin" / "pip"

    # Install dependencies
    print("  Installing MCP server dependencies...", end=" ", flush=True)
    try:
        subprocess.run(
            [
                str(pip_path),
                "install",
                "--quiet",
                "-r",
                str(base / "ouroboros" / "requirements.txt"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✓")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ pip install failed: {e.stderr}")
        sys.exit(1)


def configure_gitignore(target: Path):
    """
    Configure .gitignore to prevent committing ephemeral prAxIs OS files.

    Appends prAxIs OS patterns to existing .gitignore (or creates new file).
    Never overwrites existing patterns.

    Args:
        target: Target installation directory
    """
    gitignore_path = target / ".gitignore"

    # Patterns to add
    praxis_os_patterns = [
        "",
        "# prAxIs OS - Ephemeral Files",
        ".praxis-os/.cache/",
        ".praxis-os/venv/",
        ".praxis-os/.mcp_server_state.json",
        "",
    ]

    # Read existing .gitignore if it exists
    existing_content = ""
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            existing_content = f.read()

    # Check if already configured
    if ".praxis-os/.cache/" in existing_content:
        print("✓ .gitignore already configured for prAxIs OS")
        return

    # Append prAxIs OS patterns
    with open(gitignore_path, "a") as f:
        for pattern in praxis_os_patterns:
            f.write(pattern + "\n")

    # Print clear message about what was added
    print("✓ .gitignore configured")
    print()
    print("  Added patterns to .gitignore:")
    print("    • .praxis-os/.cache/          (RAG index, ~50MB)")
    print("    • .praxis-os/venv/            (Python dependencies, ~250MB)")
    print("    • .praxis-os/.mcp_server_state.json  (MCP runtime state)")
    print()
    print("  These files are ephemeral and should not be committed.")


def create_rebuild_flag(target: Path):
    """
    Create .rebuild_index flag to trigger RAG index build on MCP startup.

    This flag tells the MCP watcher to build the RAG index when the server starts.
    The watcher will use incremental indexing to efficiently handle new files
    created during installation (e.g., development standards generated by LLM).

    Args:
        target: Target installation directory
    """
    flag_path = target / ".praxis-os" / "standards" / ".rebuild_index"
    flag_path.touch()

    print("✓ RAG index build scheduled")
    print()
    print("  Created: .praxis-os/standards/.rebuild_index")
    print("  When MCP server starts:")
    print("    • Watcher detects flag")
    print("    • Builds index (universal + development standards)")
    print("    • Removes flag after completion")
    print("    • Subsequent changes auto-rebuild incrementally")


def cleanup(temp_dir: Path):
    """
    Remove temporary directory.

    Args:
        temp_dir: Temporary directory to remove
    """
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"✓ Cleaned up temporary directory")
    except Exception as e:
        print(f"⚠ Could not remove temp directory: {e}")
        print(f"  Manual cleanup: rm -rf {temp_dir}")


def print_success(target: Path, stats: Dict[str, int]):
    """
    Print success message and next steps for LLM.

    Args:
        target: Target installation directory
        stats: File count statistics
    """
    print()
    print("=" * 60)
    print("✅ MECHANICAL INSTALLATION COMPLETE")
    print("=" * 60)
    print()
    print(f"Installed to: {target}/.praxis-os")
    print()
    print("Files copied:")
    print(f"  • Standards: {stats['standards']} files")
    print(f"  • Workflows: {stats['workflows']} files")
    print(f"  • MCP Server: {stats['ouroboros']} files")
    print(f"  • Helper Scripts: {stats['scripts']} scripts")
    print(f"  • Total: {stats['total']} files")
    print()
    print("Environment:")
    print(f"  • Virtual environment: .praxis-os/venv/")
    print(f"  • Dependencies: Installed from requirements.txt")
    print(f"  • .gitignore: Configured (ephemeral files excluded)")
    print(f"  • RAG index: Scheduled (.rebuild_index flag created)")
    print()
    print("=" * 60)
    print("NEXT STEPS (for LLM):")
    print("=" * 60)
    print()
    print("1. Detect project language")
    print("   → Scan for language-specific files")
    print("   → Identify framework (FastAPI, Express, etc.)")
    print()
    print("2. Generate language-specific standards")
    print("   → Create standards in .praxis-os/standards/development/")
    print("   → Follow language-specific patterns")
    print()
    print("3. Configure your AI agent")
    print("   → See: docs/content/how-to-guides/agent-integrations/")
    print("   → Primary agents: cursor/, cline/vscode.md, claude-code/terminal.md")
    print("   → Secondary agents: cline/cursor.md, claude-code/cursor.md")
    print("   → Choose based on your IDE and workflow")
    print()
    print("4. Start MCP server")
    print("   → Restart editor to load MCP config")
    print("   → MCP server auto-starts")
    print("   → Watcher detects .rebuild_index flag")
    print("   → RAG index builds automatically (all standards)")
    print()
    print("5. Validate installation")
    print("   → Test search_standards() tool")
    print("   → Test workflow tools")
    print("   → Confirm connectivity")
    print()
    print("Estimated time: 5-10 minutes (depends on agent)")
    print()
    print("=" * 60)
    print("AGENT INTEGRATION GUIDES:")
    print("=" * 60)
    print()
    print("Choose your agent configuration:")
    print()
    print("📘 PRIMARY AGENTS (Control MCP Server):")
    print("  • Cursor → docs/.../agent-integrations/cursor/")
    print("  • Cline in VS Code → docs/.../agent-integrations/cline/vscode.md")
    print("  • Claude Code (CLI) → docs/.../agent-integrations/claude-code/terminal.md")
    print(
        "  • Claude Code (VS Code) → docs/.../agent-integrations/claude-code/vscode.md"
    )
    print()
    print("🔗 SECONDARY AGENTS (Connect via HTTP):")
    print("  • Cline in Cursor → docs/.../agent-integrations/cline/cursor.md")
    print(
        "  • Claude Code in Cursor → docs/.../agent-integrations/claude-code/cursor.md"
    )
    print()
    print("💡 Installation Pattern:")
    print('   "Install prAxIs OS from github.com/honeyhiveai/praxis-os for <AGENT>"')
    print()
    print("Examples:")
    print('  • "...for Cursor" → Primary Cursor setup')
    print('  • "...for Cline in VS Code" → Primary Cline')
    print('  • "...for Cline in Cursor" → Secondary Cline (needs Cursor primary)')
    print('  • "...for Claude Code" → Terminal CLI mode')
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

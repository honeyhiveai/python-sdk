"""
Dependency management for prAxIs OS installation.

Phase 7, Task 7.3: AI-friendly functions to update requirements.txt
with Tree-sitter parser packages based on detected languages.
"""

from pathlib import Path
from typing import List, Set

# Import from language detection
from language_detection import get_treesitter_package_names


def update_requirements_with_treesitter(
    requirements_path: Path, languages: List[str], dry_run: bool = False
) -> dict:
    """
    Update requirements.txt with Tree-sitter packages for detected languages.

    Phase 7, Task 7.3: Core dependency installation for LLM-driven setup.

    Reads existing requirements.txt, adds Tree-sitter base package and
    language-specific parser packages, deduplicates, and writes back.

    Preserves existing requirements and comments. Never removes packages.

    :param requirements_path: Path to requirements.txt file
    :param languages: List of detected language names (e.g., ["python", "typescript"])
    :param dry_run: If True, return changes without writing file
    :return: Dict with "added", "existing", "written" lists

    :raises FileNotFoundError: If requirements.txt doesn't exist
    :raises RuntimeError: If file write fails

    Example:
        >>> result = update_requirements_with_treesitter(
        ...     Path(".praxis-os/mcp_server/requirements.txt"),
        ...     ["python", "typescript"]
        ... )
        >>> result["added"]
        ['tree-sitter>=0.21.0', 'tree-sitter-python>=0.21.0', 'tree-sitter-typescript>=0.21.0']

    AI Usage Tip:
        Call this during installation after config generation to ensure
        Tree-sitter parsers are installed for detected languages.
    """
    if not requirements_path.exists():
        raise FileNotFoundError(
            f"Requirements file not found: {requirements_path}. "
            "Cannot update dependencies without existing requirements.txt."
        )

    # Read existing requirements
    existing_reqs = _read_requirements(requirements_path)

    # Get Tree-sitter packages for languages
    treesitter_packages = get_treesitter_package_names(languages)

    # Always include base tree-sitter package
    all_packages = ["tree-sitter>=0.21.0"] + treesitter_packages

    # Determine what's new
    added = []
    existing = []

    for package in all_packages:
        package_name = package.split(">=")[0].split("==")[0]  # Extract name only

        # Check if already in requirements (any version)
        if any(package_name in req for req in existing_reqs):
            existing.append(package)
        else:
            added.append(package)

    # Build result
    result = {
        "added": added,
        "existing": existing,
        "written": False,
    }

    # If dry run, just return what would be added
    if dry_run:
        return result

    # Write updated requirements
    if added:
        _write_requirements(requirements_path, existing_reqs, added)
        result["written"] = True

    return result


def _read_requirements(requirements_path: Path) -> List[str]:
    """
    Read existing requirements from requirements.txt.

    Returns list of all lines (including comments and blank lines)
    to preserve file structure.

    :param requirements_path: Path to requirements.txt
    :return: List of lines from file
    """
    with open(requirements_path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f.readlines()]


def _write_requirements(
    requirements_path: Path, existing_lines: List[str], new_packages: List[str]
) -> None:
    """
    Write updated requirements.txt with new packages appended.

    Preserves all existing content and appends new packages at the end
    with a clear comment section.

    :param requirements_path: Path to requirements.txt
    :param existing_lines: Existing lines from file
    :param new_packages: New packages to append
    :raises RuntimeError: If write fails
    """
    try:
        with open(requirements_path, "w", encoding="utf-8") as f:
            # Write existing content
            for line in existing_lines:
                f.write(line + "\n")

            # Add Tree-sitter section if we're adding packages
            if new_packages:
                f.write("\n")
                f.write("# Tree-sitter parsers (auto-added by prAxIs OS installer)\n")
                for package in new_packages:
                    f.write(package + "\n")

    except Exception as e:
        raise RuntimeError(
            f"Failed to write requirements to {requirements_path}: {e}"
        ) from e


def verify_treesitter_installed(venv_path: Path, languages: List[str]) -> dict:
    """
    Verify that Tree-sitter packages are installed in the venv.

    Phase 7, Task 7.3: Post-installation verification.

    Checks if Tree-sitter base package and language-specific parsers
    are available in the virtual environment.

    :param venv_path: Path to virtual environment (e.g., .praxis-os/venv)
    :param languages: List of language names to verify
    :return: Dict with "missing" and "installed" lists

    Example:
        >>> result = verify_treesitter_installed(
        ...     Path(".praxis-os/venv"),
        ...     ["python", "typescript"]
        ... )
        >>> result["installed"]
        ['tree-sitter', 'tree-sitter-python', 'tree-sitter-typescript']
        >>> result["missing"]
        []

    AI Usage Tip:
        Call this after pip install to verify installation succeeded.
        If missing is non-empty, retry installation or report error to user.
    """
    import importlib.util
    import sys

    # Determine site-packages path
    if sys.platform == "win32":
        site_packages = venv_path / "Lib" / "site-packages"
    else:
        # Unix-like: find python version dynamically
        python_dirs = list((venv_path / "lib").glob("python*"))
        if not python_dirs:
            return {
                "installed": [],
                "missing": ["Could not find site-packages in venv"],
            }
        site_packages = python_dirs[0] / "site-packages"

    if not site_packages.exists():
        return {"installed": [], "missing": ["Virtual environment not initialized"]}

    # Add site-packages to path temporarily
    sys.path.insert(0, str(site_packages))

    installed = []
    missing = []

    try:
        # Check base tree-sitter
        if importlib.util.find_spec("tree_sitter") is not None:
            installed.append("tree-sitter")
        else:
            missing.append("tree-sitter")

        # Check language-specific parsers
        package_map = {
            "python": "tree_sitter_python",
            "javascript": "tree_sitter_javascript",
            "typescript": "tree_sitter_typescript",
            "go": "tree_sitter_go",
            "rust": "tree_sitter_rust",
        }

        for lang in languages:
            if lang in package_map:
                module_name = package_map[lang]
                if importlib.util.find_spec(module_name) is not None:
                    installed.append(f"tree-sitter-{lang}")
                else:
                    missing.append(f"tree-sitter-{lang}")

    finally:
        # Remove site-packages from path
        sys.path.remove(str(site_packages))

    return {
        "installed": installed,
        "missing": missing,
    }


def format_dependency_report(result: dict, languages: List[str]) -> str:
    """
    Format human-readable dependency installation report.

    Phase 7, Task 7.3: AI-friendly output formatting.

    :param result: Result dict from update_requirements_with_treesitter()
    :param languages: List of detected languages
    :return: Formatted report string

    Example:
        >>> result = {"added": ["tree-sitter>=0.21.0", "tree-sitter-python>=0.21.0"], "existing": [], "written": True}
        >>> print(format_dependency_report(result, ["python"]))
        Tree-sitter Dependencies:
        ========================

        Added to requirements.txt:
          + tree-sitter>=0.21.0
          + tree-sitter-python>=0.21.0

        Total: 2 packages added for 1 language(s)
    """
    lines = [
        "Tree-sitter Dependencies:",
        "=" * 50,
        "",
    ]

    if result["added"]:
        lines.append("Added to requirements.txt:")
        for package in result["added"]:
            lines.append(f"  + {package}")
    else:
        lines.append("All required packages already installed!")

    if result["existing"]:
        lines.append("")
        lines.append("Already in requirements.txt:")
        for package in result["existing"]:
            lines.append(f"  ✓ {package}")

    lines.append("")
    total = len(result["added"]) + len(result["existing"])
    lines.append(f"Total: {total} package(s) for {len(languages)} language(s)")

    return "\n".join(lines)


__all__ = [
    "update_requirements_with_treesitter",
    "verify_treesitter_installed",
    "format_dependency_report",
]

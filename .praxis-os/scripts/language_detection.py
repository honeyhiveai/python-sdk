"""
Language detection for prAxIs OS installation.

Phase 7, Task 7.1: Helper functions for LLM-driven project language detection.

This module provides AI-friendly functions to detect programming languages
in a project and generate appropriate configuration for code indexing.
"""

from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping of file extensions to language names
LANGUAGE_EXTENSIONS: Dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
}

# File patterns to exclude from language detection
EXCLUDE_PATTERNS = [
    "node_modules",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "target",  # Rust/Java
    ".praxis-os",
    ".cache",
]


def detect_project_languages(project_path: Path, min_files: int = 3) -> List[str]:
    """
    Detect programming languages in a project by scanning file extensions.

    Phase 7, Task 7.1: AI-friendly language detection for installation.

    Scans the project directory tree for source files, counts by language,
    and returns languages sorted by file count (most common first).

    Only includes languages with at least min_files to avoid false positives
    from single config files.

    :param project_path: Root directory of the project to scan
    :param min_files: Minimum number of files required to include a language
    :return: List of language names, sorted by file count descending

    :raises ValueError: If project_path doesn't exist
    :raises RuntimeError: If scan fails

    Example:
        >>> languages = detect_project_languages(Path("."))
        >>> languages
        ['python', 'typescript', 'javascript']
        >>> # prAxIs OS project has mostly Python, some TS/JS for examples

    AI Usage Tip:
        Call this function during installation to determine which languages
        to enable in index_config.yaml and which Tree-sitter packages to install.
    """
    if not project_path.exists():
        raise ValueError(f"Project path does not exist: {project_path}")

    if not project_path.is_dir():
        raise ValueError(f"Project path is not a directory: {project_path}")

    # Count files by language
    language_counts = count_language_files(project_path)

    # Filter languages with at least min_files
    languages = [lang for lang, count in language_counts if count >= min_files]

    return languages


def count_language_files(project_path: Path) -> List[Tuple[str, int]]:
    """
    Count source files by programming language.

    Phase 7, Task 7.1: Core language detection logic.

    Recursively scans project directory, excludes common non-source directories,
    and counts files by language based on file extension.

    :param project_path: Root directory to scan
    :return: List of (language, count) tuples, sorted by count descending

    Example:
        >>> counts = count_language_files(Path("."))
        >>> counts
        [('python', 156), ('typescript', 12), ('javascript', 8)]
    """
    counter: Counter = Counter()

    try:
        for file_path in project_path.rglob("*"):
            # Skip directories
            if not file_path.is_file():
                continue

            # Skip excluded paths
            if _is_excluded(file_path, project_path):
                continue

            # Check extension
            ext = file_path.suffix.lower()
            if ext in LANGUAGE_EXTENSIONS:
                language = LANGUAGE_EXTENSIONS[ext]
                counter[language] += 1

    except Exception as e:
        raise RuntimeError(f"Failed to scan project directory: {e}") from e

    # Return sorted by count descending
    return counter.most_common()


def _is_excluded(file_path: Path, project_root: Path) -> bool:
    """
    Check if file path should be excluded from language detection.

    Excludes common non-source directories like node_modules, __pycache__, etc.

    :param file_path: File path to check
    :param project_root: Project root directory
    :return: True if should be excluded, False otherwise
    """
    # Get relative path from project root
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        # File is outside project root, exclude it
        return True

    # Check each path component against exclude patterns
    for part in rel_path.parts:
        if part in EXCLUDE_PATTERNS:
            return True

    return False


def get_language_file_patterns(languages: List[str]) -> List[str]:
    """
    Get file patterns for a list of programming languages.

    Phase 7, Task 7.2: Helper for config generation.

    Converts language names to file extension patterns suitable for
    index_config.yaml file_patterns section.

    :param languages: List of language names (e.g., ["python", "typescript"])
    :return: List of file patterns (e.g., ["*.py", "*.ts", "*.tsx"])

    Example:
        >>> get_language_file_patterns(["python", "typescript"])
        ['*.py', '*.ts', '*.tsx']

    AI Usage Tip:
        Use this when generating index_config.yaml to populate the
        code.file_patterns section.
    """
    patterns = []

    # Reverse lookup: language -> extensions
    for ext, lang in LANGUAGE_EXTENSIONS.items():
        if lang in languages:
            patterns.append(f"*{ext}")

    return sorted(patterns)


def get_treesitter_package_names(languages: List[str]) -> List[str]:
    """
    Get Tree-sitter package names for programming languages.

    Phase 7, Task 7.3: Helper for dependency installation.

    Converts language names to PyPI package names for Tree-sitter parsers.

    :param languages: List of language names (e.g., ["python", "typescript"])
    :return: List of package names (e.g., ["tree-sitter-python>=0.21.0"])

    Example:
        >>> get_treesitter_package_names(["python", "typescript"])
        ['tree-sitter-python>=0.21.0', 'tree-sitter-typescript>=0.21.0']

    AI Usage Tip:
        Use this when updating requirements.txt during installation to
        add the correct Tree-sitter parser packages.

    Note:
        Not all languages have Tree-sitter parsers available on PyPI.
        This function only returns packages for languages with known parsers.
    """
    # Known Tree-sitter packages on PyPI
    known_packages = {
        "python": "tree-sitter-python",
        "javascript": "tree-sitter-javascript",
        "typescript": "tree-sitter-typescript",
        "go": "tree-sitter-go",
        "rust": "tree-sitter-rust",
        "java": "tree-sitter-java",
        "c": "tree-sitter-c",
        "cpp": "tree-sitter-cpp",
    }

    packages = []
    for lang in languages:
        if lang in known_packages:
            # Use >=0.21.0 for compatibility with tree-sitter 0.25.x API
            packages.append(f"{known_packages[lang]}>=0.21.0")

    return packages


def format_language_report(
    language_counts: List[Tuple[str, int]], detected_languages: List[str]
) -> str:
    """
    Format a human-readable report of detected languages.

    Phase 7, Task 7.1: AI-friendly output formatting.

    :param language_counts: All language counts from count_language_files()
    :param detected_languages: Filtered languages from detect_project_languages()
    :return: Formatted report string

    Example:
        >>> counts = [('python', 156), ('typescript', 12)]
        >>> detected = ['python', 'typescript']
        >>> print(format_language_report(counts, detected))
        Language Detection Results:
        ===========================

        Detected languages (>=3 files):
          ✓ python (156 files)
          ✓ typescript (12 files)

        Total: 2 languages detected
    """
    lines = [
        "Language Detection Results:",
        "=" * 50,
        "",
        f"Detected languages (>=3 files):",
    ]

    for lang in detected_languages:
        # Find count for this language
        count = next((c for l, c in language_counts if l == lang), 0)
        lines.append(f"  ✓ {lang} ({count} files)")

    lines.append("")
    lines.append(f"Total: {len(detected_languages)} language(s) detected")

    return "\n".join(lines)


__all__ = [
    "detect_project_languages",
    "count_language_files",
    "get_language_file_patterns",
    "get_treesitter_package_names",
    "format_language_report",
]

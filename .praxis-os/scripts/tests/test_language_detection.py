"""
Unit tests for language detection module.

Phase 7, Task 7.1: Validates language detection, file counting, and helper functions.
"""

# Import language detection module
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from language_detection import (
    count_language_files,
    detect_project_languages,
    format_language_report,
    get_language_file_patterns,
    get_treesitter_package_names,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create Python files
        (project_path / "main.py").touch()
        (project_path / "utils.py").touch()
        (project_path / "config.py").touch()
        (project_path / "test.py").touch()

        # Create TypeScript files
        (project_path / "app.ts").touch()
        (project_path / "component.tsx").touch()

        # Create JavaScript files
        (project_path / "script.js").touch()
        (project_path / "index.jsx").touch()

        # Create files to be excluded
        (project_path / "node_modules").mkdir()
        (project_path / "node_modules" / "lib.js").touch()
        (project_path / "__pycache__").mkdir()
        (project_path / "__pycache__" / "cache.pyc").touch()

        yield project_path


class TestLanguageDetection:
    """Test suite for detect_project_languages()."""

    def test_detects_languages_above_threshold(self, temp_project):
        """Should detect languages with at least min_files."""
        languages = detect_project_languages(temp_project, min_files=3)

        # Python has 4 files, should be detected
        assert "python" in languages

    def test_filters_languages_below_threshold(self, temp_project):
        """Should not detect languages below min_files threshold."""
        languages = detect_project_languages(temp_project, min_files=3)

        # TypeScript has 2 files, should not be detected with min_files=3
        assert "typescript" not in languages

    def test_sorts_by_file_count_descending(self, temp_project):
        """Should return languages sorted by file count (most first)."""
        languages = detect_project_languages(temp_project, min_files=2)

        # Python (4) should come before TypeScript (2) and JavaScript (2)
        assert languages[0] == "python"

    def test_raises_on_nonexistent_path(self):
        """Should raise ValueError for nonexistent path."""
        with pytest.raises(ValueError, match="does not exist"):
            detect_project_languages(Path("/nonexistent/path"))

    def test_raises_on_file_not_directory(self, tmp_path):
        """Should raise ValueError when path is a file."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with pytest.raises(ValueError, match="not a directory"):
            detect_project_languages(test_file)


class TestCountLanguageFiles:
    """Test suite for count_language_files()."""

    def test_counts_all_languages(self, temp_project):
        """Should count files for all detected languages."""
        counts = count_language_files(temp_project)
        count_dict = dict(counts)

        assert count_dict["python"] == 4
        assert count_dict["typescript"] == 2  # .ts + .tsx
        assert count_dict["javascript"] == 2  # .js + .jsx

    def test_returns_sorted_by_count(self, temp_project):
        """Should return languages sorted by count descending."""
        counts = count_language_files(temp_project)

        # First should be highest count
        assert counts[0][0] == "python"
        assert counts[0][1] == 4

    def test_excludes_node_modules(self, temp_project):
        """Should exclude files in node_modules."""
        counts = count_language_files(temp_project)
        count_dict = dict(counts)

        # node_modules/lib.js should not be counted
        # So JavaScript count should be 2, not 3
        assert count_dict.get("javascript", 0) == 2

    def test_excludes_pycache(self, temp_project):
        """Should exclude files in __pycache__."""
        counts = count_language_files(temp_project)

        # __pycache__/cache.pyc should not be counted
        # All counts should be from real source files only
        total_files = sum(count for _, count in counts)
        assert total_files == 8  # 4 py + 2 ts + 2 js

    def test_handles_empty_directory(self, tmp_path):
        """Should return empty list for empty directory."""
        counts = count_language_files(tmp_path)
        assert counts == []


class TestGetLanguageFilePatterns:
    """Test suite for get_language_file_patterns()."""

    def test_returns_patterns_for_python(self):
        """Should return correct patterns for Python."""
        patterns = get_language_file_patterns(["python"])
        assert "*.py" in patterns

    def test_returns_patterns_for_typescript(self):
        """Should return correct patterns for TypeScript."""
        patterns = get_language_file_patterns(["typescript"])
        assert "*.ts" in patterns
        assert "*.tsx" in patterns

    def test_returns_patterns_for_javascript(self):
        """Should return correct patterns for JavaScript."""
        patterns = get_language_file_patterns(["javascript"])
        assert "*.js" in patterns
        assert "*.jsx" in patterns

    def test_returns_patterns_for_multiple_languages(self):
        """Should return combined patterns for multiple languages."""
        patterns = get_language_file_patterns(["python", "typescript", "javascript"])

        assert "*.py" in patterns
        assert "*.ts" in patterns
        assert "*.tsx" in patterns
        assert "*.js" in patterns
        assert "*.jsx" in patterns

    def test_returns_sorted_patterns(self):
        """Should return patterns sorted alphabetically."""
        patterns = get_language_file_patterns(["typescript", "python"])

        # Should be sorted
        assert patterns == sorted(patterns)


class TestGetTreesitterPackageNames:
    """Test suite for get_treesitter_package_names()."""

    def test_returns_package_for_python(self):
        """Should return tree-sitter-python package."""
        packages = get_treesitter_package_names(["python"])
        assert "tree-sitter-python>=0.21.0" in packages

    def test_returns_package_for_typescript(self):
        """Should return tree-sitter-typescript package."""
        packages = get_treesitter_package_names(["typescript"])
        assert "tree-sitter-typescript>=0.21.0" in packages

    def test_returns_packages_for_multiple_languages(self):
        """Should return multiple packages for multiple languages."""
        packages = get_treesitter_package_names(["python", "typescript", "javascript"])

        assert len(packages) == 3
        assert "tree-sitter-python>=0.21.0" in packages
        assert "tree-sitter-typescript>=0.21.0" in packages
        assert "tree-sitter-javascript>=0.21.0" in packages

    def test_skips_unsupported_languages(self):
        """Should skip languages without known Tree-sitter packages."""
        packages = get_treesitter_package_names(["python", "unknown_language"])

        # Should only include Python, skip unknown
        assert len(packages) == 1
        assert "tree-sitter-python>=0.21.0" in packages

    def test_returns_empty_for_no_languages(self):
        """Should return empty list for no languages."""
        packages = get_treesitter_package_names([])
        assert packages == []


class TestFormatLanguageReport:
    """Test suite for format_language_report()."""

    def test_formats_single_language(self):
        """Should format report for single language."""
        counts = [("python", 156)]
        detected = ["python"]
        report = format_language_report(counts, detected)

        assert "python" in report
        assert "156 files" in report
        assert "Total: 1 language" in report

    def test_formats_multiple_languages(self):
        """Should format report for multiple languages."""
        counts = [("python", 156), ("typescript", 12), ("javascript", 8)]
        detected = ["python", "typescript", "javascript"]
        report = format_language_report(counts, detected)

        assert "python (156 files)" in report
        assert "typescript (12 files)" in report
        assert "javascript (8 files)" in report
        assert "Total: 3 language" in report

    def test_shows_checkmarks(self):
        """Should show checkmarks for detected languages."""
        counts = [("python", 156)]
        detected = ["python"]
        report = format_language_report(counts, detected)

        assert "✓" in report


class TestExclusionLogic:
    """Test suite for _is_excluded() logic."""

    def test_excludes_standard_directories(self, temp_project):
        """Should exclude node_modules, __pycache__, .git, venv."""
        # Create standard excluded directories
        (temp_project / ".git").mkdir()
        (temp_project / ".git" / "config").touch()
        (temp_project / "venv").mkdir()
        (temp_project / "venv" / "lib.py").touch()

        counts = count_language_files(temp_project)
        count_dict = dict(counts)

        # Should not count files in excluded directories
        # Original 4 Python files should remain
        assert count_dict.get("python", 0) == 4

    def test_excludes_praxis_os_directory(self, temp_project):
        """Should exclude .praxis-os directory."""
        (temp_project / ".praxis-os").mkdir()
        (temp_project / ".praxis-os" / "config.py").touch()

        counts = count_language_files(temp_project)
        count_dict = dict(counts)

        # Should not count .praxis-os/config.py
        assert count_dict.get("python", 0) == 4  # Original 4 only

    def test_excludes_dist_and_build(self, temp_project):
        """Should exclude dist and build directories."""
        (temp_project / "dist").mkdir()
        (temp_project / "dist" / "bundle.js").touch()
        (temp_project / "build").mkdir()
        (temp_project / "build" / "output.py").touch()

        counts = count_language_files(temp_project)
        count_dict = dict(counts)

        # Should not count files in dist/build
        assert count_dict.get("python", 0) == 4  # Original 4 only
        assert count_dict.get("javascript", 0) == 2  # Original 2 only


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

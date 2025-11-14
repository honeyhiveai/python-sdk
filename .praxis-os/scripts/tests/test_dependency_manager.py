"""
Unit tests for dependency manager module.

Phase 7, Task 7.3: Validates Tree-sitter dependency installation helpers.
"""

# Import dependency manager module
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from dependency_manager import (
    format_dependency_report,
    update_requirements_with_treesitter,
)


@pytest.fixture
def temp_requirements():
    """Create temporary requirements.txt with sample content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        req_path = Path(tmpdir) / "requirements.txt"

        # Write sample requirements
        with open(req_path, "w") as f:
            f.write("# Sample requirements\n")
            f.write("fastapi>=0.100.0\n")
            f.write("pydantic>=2.0.0\n")
            f.write("\n")
            f.write("# MCP dependencies\n")
            f.write("mcp>=0.1.0\n")

        yield req_path


class TestUpdateRequirementsWithTreesitter:
    """Test suite for update_requirements_with_treesitter()."""

    def test_adds_treesitter_packages_for_python(self, temp_requirements):
        """Should add tree-sitter and tree-sitter-python."""
        result = update_requirements_with_treesitter(temp_requirements, ["python"])

        assert "tree-sitter>=0.21.0" in result["added"]
        assert "tree-sitter-python>=0.21.0" in result["added"]
        assert result["written"] is True

    def test_adds_packages_for_multiple_languages(self, temp_requirements):
        """Should add packages for all detected languages."""
        result = update_requirements_with_treesitter(
            temp_requirements, ["python", "typescript", "javascript"]
        )

        # Should have base + 3 language packages
        assert len(result["added"]) == 4
        assert "tree-sitter>=0.21.0" in result["added"]
        assert "tree-sitter-python>=0.21.0" in result["added"]
        assert "tree-sitter-typescript>=0.21.0" in result["added"]
        assert "tree-sitter-javascript>=0.21.0" in result["added"]

    def test_preserves_existing_requirements(self, temp_requirements):
        """Should preserve all existing requirements."""
        update_requirements_with_treesitter(temp_requirements, ["python"])

        # Read back and verify existing packages still there
        with open(temp_requirements, "r") as f:
            content = f.read()

        assert "fastapi>=0.100.0" in content
        assert "pydantic>=2.0.0" in content
        assert "mcp>=0.1.0" in content

    def test_appends_to_end_of_file(self, temp_requirements):
        """Should append new packages to end of file."""
        update_requirements_with_treesitter(temp_requirements, ["python"])

        with open(temp_requirements, "r") as f:
            lines = f.readlines()

        # Tree-sitter packages should be after existing packages
        treesitter_line_idx = next(
            i for i, line in enumerate(lines) if "tree-sitter" in line.lower()
        )

        # Should be near the end (after all original packages)
        assert treesitter_line_idx > 4  # After the 5 original lines

    def test_does_not_duplicate_existing_packages(self, temp_requirements):
        """Should not add packages that are already in requirements."""
        # Add tree-sitter manually first
        with open(temp_requirements, "a") as f:
            f.write("\ntree-sitter>=0.21.0\n")

        result = update_requirements_with_treesitter(temp_requirements, ["python"])

        # tree-sitter should be in existing, not added
        assert "tree-sitter>=0.21.0" in result["existing"]
        assert "tree-sitter>=0.21.0" not in result["added"]

        # But tree-sitter-python should still be added
        assert "tree-sitter-python>=0.21.0" in result["added"]

    def test_dry_run_does_not_write(self, temp_requirements):
        """Should not write file when dry_run=True."""
        # Get original content
        with open(temp_requirements, "r") as f:
            original = f.read()

        result = update_requirements_with_treesitter(
            temp_requirements, ["python"], dry_run=True
        )

        # Should report what would be added
        assert len(result["added"]) > 0
        assert result["written"] is False

        # File should be unchanged
        with open(temp_requirements, "r") as f:
            current = f.read()

        assert current == original

    def test_raises_on_missing_file(self):
        """Should raise FileNotFoundError for nonexistent file."""
        with pytest.raises(FileNotFoundError, match="Requirements file not found"):
            update_requirements_with_treesitter(
                Path("/nonexistent/requirements.txt"), ["python"]
            )

    def test_handles_empty_languages_list(self, temp_requirements):
        """Should handle empty languages list (just add base tree-sitter)."""
        result = update_requirements_with_treesitter(temp_requirements, [])

        # Should add base tree-sitter only
        assert result["added"] == ["tree-sitter>=0.21.0"]

    def test_skips_languages_without_parsers(self, temp_requirements):
        """Should skip languages that don't have Tree-sitter packages."""
        result = update_requirements_with_treesitter(
            temp_requirements, ["python", "unknown_language"]
        )

        # Should add base + python only, skip unknown
        assert len(result["added"]) == 2
        assert "tree-sitter>=0.21.0" in result["added"]
        assert "tree-sitter-python>=0.21.0" in result["added"]


class TestFormatDependencyReport:
    """Test suite for format_dependency_report()."""

    def test_formats_added_packages(self):
        """Should format report for added packages."""
        result = {
            "added": ["tree-sitter>=0.21.0", "tree-sitter-python>=0.21.0"],
            "existing": [],
            "written": True,
        }

        report = format_dependency_report(result, ["python"])

        assert "tree-sitter>=0.21.0" in report
        assert "tree-sitter-python>=0.21.0" in report
        assert "2 package" in report
        assert "1 language" in report

    def test_formats_existing_packages(self):
        """Should format report for existing packages."""
        result = {
            "added": [],
            "existing": ["tree-sitter>=0.21.0"],
            "written": False,
        }

        report = format_dependency_report(result, ["python"])

        assert "Already" in report
        assert "tree-sitter>=0.21.0" in report

    def test_formats_mixed_added_and_existing(self):
        """Should format report with both added and existing."""
        result = {
            "added": ["tree-sitter-python>=0.21.0"],
            "existing": ["tree-sitter>=0.21.0"],
            "written": True,
        }

        report = format_dependency_report(result, ["python"])

        assert "Added" in report
        assert "Already" in report
        assert "tree-sitter-python>=0.21.0" in report
        assert "tree-sitter>=0.21.0" in report

    def test_shows_plus_signs_for_added(self):
        """Should show + prefix for added packages."""
        result = {
            "added": ["tree-sitter>=0.21.0"],
            "existing": [],
            "written": True,
        }

        report = format_dependency_report(result, ["python"])

        assert "+ tree-sitter" in report

    def test_shows_checkmarks_for_existing(self):
        """Should show ✓ prefix for existing packages."""
        result = {
            "added": [],
            "existing": ["tree-sitter>=0.21.0"],
            "written": False,
        }

        report = format_dependency_report(result, ["python"])

        assert "✓" in report


class TestEndToEnd:
    """Test suite for end-to-end dependency installation workflow."""

    def test_full_workflow(self, temp_requirements):
        """Should complete full workflow: update -> verify -> report."""
        # Step 1: Update requirements
        result = update_requirements_with_treesitter(
            temp_requirements, ["python", "typescript"]
        )

        # Step 2: Verify written
        assert result["written"] is True
        assert len(result["added"]) > 0

        # Step 3: Read back to verify
        with open(temp_requirements, "r") as f:
            content = f.read()

        assert "tree-sitter>=0.21.0" in content
        assert "tree-sitter-python>=0.21.0" in content
        assert "tree-sitter-typescript>=0.21.0" in content

        # Step 4: Format report
        report = format_dependency_report(result, ["python", "typescript"])
        assert "python" in report or "2 language" in report

    def test_idempotent_updates(self, temp_requirements):
        """Should be idempotent - running twice doesn't duplicate."""
        # First update
        result1 = update_requirements_with_treesitter(temp_requirements, ["python"])
        assert len(result1["added"]) > 0

        # Second update (should find existing)
        result2 = update_requirements_with_treesitter(temp_requirements, ["python"])
        assert len(result2["added"]) == 0
        assert len(result2["existing"]) > 0
        assert result2["written"] is False  # Nothing new to write


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

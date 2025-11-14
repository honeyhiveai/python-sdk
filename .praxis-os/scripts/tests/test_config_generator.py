"""
Unit tests for configuration generator module.

Phase 7, Task 7.2: Validates config generation, validation, and file writing.
"""

# Import config generator module
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_generator import (
    format_config_summary,
    generate_index_config,
    validate_config,
    write_config_file,
)


class TestGenerateIndexConfig:
    """Test suite for generate_index_config()."""

    def test_generates_valid_config_for_python(self, tmp_path):
        """Should generate valid config for Python project."""
        config = generate_index_config(["python"], tmp_path)

        assert "indexes" in config
        assert "retrieval" in config
        assert "monitoring" in config

    def test_includes_vector_search(self, tmp_path):
        """Should always include vector search for standards."""
        config = generate_index_config(["python"], tmp_path)

        assert config["indexes"]["vector"]["enabled"] is True
        assert "model" in config["indexes"]["vector"]

    def test_includes_fts_search(self, tmp_path):
        """Should always include FTS for standards."""
        config = generate_index_config(["python"], tmp_path)

        assert config["indexes"]["fts"]["enabled"] is True

    def test_includes_metadata_filtering(self, tmp_path):
        """Should always include metadata filtering."""
        config = generate_index_config(["python"], tmp_path)

        assert config["indexes"]["metadata"]["enabled"] is True
        assert "scalar_indexes" in config["indexes"]["metadata"]

    def test_includes_code_search_when_enabled(self, tmp_path):
        """Should include code search for detected languages."""
        config = generate_index_config(["python", "typescript"], tmp_path)

        assert "code" in config["indexes"]
        assert config["indexes"]["code"]["enabled"] is True
        assert config["indexes"]["code"]["languages"] == ["python", "typescript"]

    def test_excludes_code_search_when_disabled(self, tmp_path):
        """Should exclude code search when disabled."""
        config = generate_index_config(["python"], tmp_path, enable_code_search=False)

        assert "code" not in config["indexes"]

    def test_raises_on_empty_languages_with_code_search(self, tmp_path):
        """Should raise ValueError when enabling code search without languages."""
        with pytest.raises(ValueError, match="Cannot enable code search"):
            generate_index_config([], tmp_path, enable_code_search=True)

    def test_allows_empty_languages_without_code_search(self, tmp_path):
        """Should allow empty languages when code search disabled."""
        config = generate_index_config([], tmp_path, enable_code_search=False)

        # Should still have vector/fts/metadata
        assert "vector" in config["indexes"]
        assert "code" not in config["indexes"]


class TestCodeConfig:
    """Test suite for code search configuration generation."""

    def test_sets_correct_languages(self, tmp_path):
        """Should set languages list from detected languages."""
        config = generate_index_config(["python", "typescript"], tmp_path)

        assert config["indexes"]["code"]["languages"] == ["python", "typescript"]

    def test_sets_correct_file_patterns(self, tmp_path):
        """Should set file patterns based on languages."""
        config = generate_index_config(["python", "typescript"], tmp_path)

        patterns = config["indexes"]["code"]["file_patterns"]
        assert "*.py" in patterns
        assert "*.ts" in patterns
        assert "*.tsx" in patterns

    def test_includes_exclude_patterns(self, tmp_path):
        """Should include standard exclude patterns."""
        config = generate_index_config(["python"], tmp_path)

        excludes = config["indexes"]["code"]["exclude_patterns"]
        assert "**/tests/**" in excludes
        assert "**/node_modules/**" in excludes or "*/node_modules/*" in excludes
        assert "**/__pycache__/**" in excludes or "*/__pycache__/*" in excludes
        assert "**/venv/**" in excludes or "*/venv/*" in excludes

    def test_sets_source_paths(self, tmp_path):
        """Should set default source paths."""
        config = generate_index_config(["python"], tmp_path)

        assert "source_paths" in config["indexes"]["code"]
        assert isinstance(config["indexes"]["code"]["source_paths"], list)


class TestMonitoringConfig:
    """Test suite for monitoring configuration generation."""

    def test_enables_file_watcher(self, tmp_path):
        """Should enable file watcher by default."""
        config = generate_index_config(["python"], tmp_path)

        assert config["monitoring"]["file_watcher"]["enabled"] is True

    def test_includes_standards_watcher(self, tmp_path):
        """Should always include standards watcher."""
        config = generate_index_config(["python"], tmp_path)

        watched = config["monitoring"]["file_watcher"]["watched_content"]
        assert "standards" in watched
        assert watched["standards"]["patterns"] == ["*.md", "*.json"]

    def test_includes_code_watcher_when_enabled(self, tmp_path):
        """Should include code watcher when code search enabled."""
        config = generate_index_config(["python"], tmp_path, enable_code_search=True)

        watched = config["monitoring"]["file_watcher"]["watched_content"]
        assert "code" in watched

    def test_excludes_code_watcher_when_disabled(self, tmp_path):
        """Should exclude code watcher when code search disabled."""
        config = generate_index_config(["python"], tmp_path, enable_code_search=False)

        watched = config["monitoring"]["file_watcher"]["watched_content"]
        assert "code" not in watched

    def test_sets_different_debounce_times(self, tmp_path):
        """Should set different debounce times for standards vs code."""
        config = generate_index_config(["python"], tmp_path)

        watched = config["monitoring"]["file_watcher"]["watched_content"]
        assert watched["standards"]["debounce_seconds"] == 5
        assert watched["code"]["debounce_seconds"] == 10


class TestWriteConfigFile:
    """Test suite for write_config_file()."""

    def test_writes_valid_yaml(self, tmp_path):
        """Should write valid YAML file."""
        config = generate_index_config(["python"], tmp_path)
        output_path = tmp_path / "test_config.yaml"

        write_config_file(config, output_path)

        # Should be valid YAML
        with open(output_path, "r") as f:
            loaded = yaml.safe_load(f)

        assert loaded == config

    def test_creates_parent_directories(self, tmp_path):
        """Should create parent directories if needed."""
        config = generate_index_config(["python"], tmp_path)
        output_path = tmp_path / "nested" / "dir" / "config.yaml"

        write_config_file(config, output_path)

        assert output_path.exists()

    def test_preserves_structure(self, tmp_path):
        """Should preserve nested dictionary structure."""
        config = generate_index_config(["python", "typescript"], tmp_path)
        output_path = tmp_path / "config.yaml"

        write_config_file(config, output_path)

        # Reload and verify structure
        with open(output_path, "r") as f:
            loaded = yaml.safe_load(f)

        assert loaded["indexes"]["code"]["languages"] == ["python", "typescript"]


class TestValidateConfig:
    """Test suite for validate_config()."""

    def test_validates_complete_config(self, tmp_path):
        """Should validate complete, correct config."""
        config = generate_index_config(["python"], tmp_path)

        assert validate_config(config) is True

    def test_raises_on_missing_indexes(self):
        """Should raise ValueError when indexes section missing."""
        config = {"retrieval": {}, "monitoring": {}}

        with pytest.raises(ValueError, match="Missing required section: indexes"):
            validate_config(config)

    def test_raises_on_missing_retrieval(self):
        """Should raise ValueError when retrieval section missing."""
        config = {"indexes": {}, "monitoring": {}}

        with pytest.raises(ValueError, match="Missing required section: retrieval"):
            validate_config(config)

    def test_raises_on_missing_monitoring(self):
        """Should raise ValueError when monitoring section missing."""
        config = {"indexes": {}, "retrieval": {}}

        with pytest.raises(ValueError, match="Missing required section: monitoring"):
            validate_config(config)

    def test_raises_on_missing_vector_index(self):
        """Should raise ValueError when vector index missing."""
        config = {
            "indexes": {"fts": {}, "metadata": {}},
            "retrieval": {},
            "monitoring": {"file_watcher": {}},
        }

        with pytest.raises(ValueError, match="Missing required index: vector"):
            validate_config(config)

    def test_raises_on_disabled_vector(self):
        """Should raise ValueError when vector search disabled."""
        config = {
            "indexes": {
                "vector": {"enabled": False},
                "fts": {},
                "metadata": {},
            },
            "retrieval": {},
            "monitoring": {"file_watcher": {}},
        }

        with pytest.raises(ValueError, match="Vector search must be enabled"):
            validate_config(config)


class TestFormatConfigSummary:
    """Test suite for format_config_summary()."""

    def test_formats_single_language(self, tmp_path):
        """Should format summary for single language."""
        config = generate_index_config(["python"], tmp_path)
        summary = format_config_summary(config, ["python"])

        assert "python" in summary
        assert "1 languages" in summary

    def test_formats_multiple_languages(self, tmp_path):
        """Should format summary for multiple languages."""
        config = generate_index_config(["python", "typescript"], tmp_path)
        summary = format_config_summary(config, ["python", "typescript"])

        assert "python" in summary
        assert "typescript" in summary
        assert "2 languages" in summary

    def test_shows_indexes(self, tmp_path):
        """Should show all enabled indexes."""
        config = generate_index_config(["python"], tmp_path)
        summary = format_config_summary(config, ["python"])

        assert "Vector search" in summary
        assert "Full-text search" in summary
        assert "Metadata filtering" in summary
        assert "Code search" in summary

    def test_shows_file_watcher(self, tmp_path):
        """Should show file watcher configuration."""
        config = generate_index_config(["python"], tmp_path)
        summary = format_config_summary(config, ["python"])

        assert "File Watcher" in summary
        assert "Standards" in summary
        assert "5s debounce" in summary
        assert "10s debounce" in summary

    def test_shows_checkmarks(self, tmp_path):
        """Should show checkmarks for enabled features."""
        config = generate_index_config(["python"], tmp_path)
        summary = format_config_summary(config, ["python"])

        assert "✓" in summary


class TestEndToEnd:
    """Test suite for end-to-end config generation workflow."""

    def test_full_workflow(self, tmp_path):
        """Should complete full workflow: generate -> validate -> write."""
        # Generate config
        config = generate_index_config(["python", "typescript"], tmp_path)

        # Validate
        assert validate_config(config)

        # Write
        output_path = tmp_path / "config.yaml"
        write_config_file(config, output_path)

        # Verify file exists and is valid
        assert output_path.exists()
        with open(output_path, "r") as f:
            loaded = yaml.safe_load(f)

        # Should match original
        assert loaded["indexes"]["code"]["languages"] == ["python", "typescript"]

    def test_ai_agent_usage(self, tmp_path):
        """Should demonstrate AI agent usage pattern."""
        # Step 1: Detect languages (from Task 7.1)
        detected_languages = ["python", "typescript"]

        # Step 2: Generate config (Task 7.2)
        config = generate_index_config(detected_languages, tmp_path)

        # Step 3: Validate
        validate_config(config)

        # Step 4: Write
        output_path = tmp_path / ".praxis-os" / "config" / "index_config.yaml"
        write_config_file(config, output_path)

        # Step 5: Format summary for user
        summary = format_config_summary(config, detected_languages)

        # All steps should complete successfully
        assert output_path.exists()
        assert "python" in summary
        assert "typescript" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Configuration generator for prAxIs OS installation.

Phase 7, Task 7.2: AI-friendly functions to generate index_config.yaml
based on detected project languages.
"""

from pathlib import Path
from typing import List

import yaml

# Import from language detection
from language_detection import get_language_file_patterns


def generate_index_config(
    languages: List[str], project_root: Path, enable_code_search: bool = True
) -> dict:
    """
    Generate index_config.yaml content based on detected languages.

    Phase 7, Task 7.2: Core config generation for LLM-driven installation.

    Creates complete configuration dictionary with:
    - Vector search for standards (always enabled)
    - FTS for standards (always enabled)
    - Metadata filtering (always enabled)
    - Code search with detected languages (if enabled)
    - File watcher with appropriate patterns

    :param languages: List of detected language names (e.g., ["python", "typescript"])
    :param project_root: Project root directory (for determining source paths)
    :param enable_code_search: Whether to enable code indexing (default: True)
    :return: Configuration dictionary ready for yaml.dump()

    :raises ValueError: If languages list is empty and code search is enabled

    Example:
        >>> config = generate_index_config(["python", "typescript"], Path("."))
        >>> config["indexes"]["code"]["languages"]
        ['python', 'typescript']
        >>> config["indexes"]["code"]["file_patterns"]
        ['*.py', '*.ts', '*.tsx']

    AI Usage Tip:
        Call this during installation after detect_project_languages() to
        generate appropriate configuration. Then write to .praxis-os/config/index_config.yaml.
    """
    if enable_code_search and not languages:
        raise ValueError(
            "Cannot enable code search without detected languages. "
            "Either disable code search or provide languages list."
        )

    # Build configuration dictionary
    config = {
        "indexes": {
            "vector": _generate_vector_config(),
            "fts": _generate_fts_config(),
            "metadata": _generate_metadata_config(),
        },
        "retrieval": _generate_retrieval_config(),
        "monitoring": _generate_monitoring_config(languages, enable_code_search),
    }

    # Add code search if enabled
    if enable_code_search:
        config["indexes"]["code"] = _generate_code_config(languages)

    return config


def _generate_vector_config() -> dict:
    """
    Generate vector search configuration section.

    Always enabled for standards, using BGE-small model for local embedding.
    """
    return {
        "enabled": True,
        "model": "BAAI/bge-small-en-v1.5",
        "source_paths": ["standards/"],
        "file_patterns": ["*.md"],
        "chunk_size": 500,
        "chunk_overlap": 50,
    }


def _generate_fts_config() -> dict:
    """
    Generate FTS (Full-Text Search) configuration section.

    Always enabled for standards, using LanceDB native BM25.
    """
    return {
        "enabled": True,
        "source_paths": ["standards/"],
        "with_position": False,
        "stem": True,
        "remove_stop_words": True,
        "ascii_folding": True,
        "max_token_length": 40,
    }


def _generate_metadata_config() -> dict:
    """
    Generate metadata filtering configuration section.

    Always enabled with scalar indexes for domain, phase, role, audience.
    """
    return {
        "enabled": True,
        "scalar_indexes": [
            {"column": "domain", "index_type": "btree"},
            {"column": "phase", "index_type": "bitmap"},
            {"column": "role", "index_type": "bitmap"},
            {"column": "audience", "index_type": "btree"},
        ],
        "auto_generate": True,
        "llm_enhance": False,
    }


def _generate_code_config(languages: List[str]) -> dict:
    """
    Generate code search configuration section.

    :param languages: Detected languages to enable
    :return: Code configuration dict
    """
    file_patterns = get_language_file_patterns(languages)

    return {
        "enabled": True,
        "source_paths": ["mcp_server/"],  # Default to our own code during dogfooding
        "languages": languages,
        "file_patterns": file_patterns,
        "exclude_patterns": [
            "**/tests/**",
            "*/node_modules/*",
            "*/__pycache__/*",
            "*/venv/*",
            "*/dist/*",
            "*/build/*",
        ],
    }


def _generate_retrieval_config() -> dict:
    """
    Generate retrieval strategy configuration section.

    Enables hybrid search with RRF fusion and cross-encoder re-ranking.
    """
    return {
        "fusion_strategy": "reciprocal_rank",
        "rerank": {
            "enabled": True,
            "model": "cross-encoder/ms-marco-MiniLM-L-12-v2",
        },
    }


def _generate_monitoring_config(languages: List[str], enable_code_watch: bool) -> dict:
    """
    Generate monitoring and file watcher configuration section.

    :param languages: Detected languages for code watching
    :param enable_code_watch: Whether to enable code file watching
    :return: Monitoring configuration dict
    """
    config = {
        "track_query_performance": True,
        "log_level": "INFO",
        "file_watcher": {
            "enabled": True,
            "watched_content": {
                "standards": {
                    "paths": ["standards/"],
                    "patterns": ["*.md", "*.json"],
                    "exclude": [],
                    "debounce_seconds": 5,
                },
            },
        },
    }

    # Add code watching if enabled
    if enable_code_watch:
        file_patterns = get_language_file_patterns(languages)
        config["file_watcher"]["watched_content"]["code"] = {
            "enabled": True,
            "paths": ["../src", "../lib", "../app"],
            "patterns": file_patterns,
            "exclude": [
                "**/node_modules/**",
                "**/venv/**",
                "**/.venv/**",
                "**/dist/**",
                "**/build/**",
                "**/__pycache__/**",
                "**/*.pyc",
                "**/.git/**",
                "**/htmlcov/**",
                "**/coverage/**",
            ],
            "debounce_seconds": 10,
        }

    return config


def write_config_file(config: dict, output_path: Path) -> None:
    """
    Write configuration dictionary to YAML file.

    Phase 7, Task 7.2: Write generated config to disk.

    Creates parent directories if needed. Preserves YAML formatting
    with proper indentation and flow style for readability.

    :param config: Configuration dictionary from generate_index_config()
    :param output_path: Path to write config file (e.g., .praxis-os/config/index_config.yaml)

    :raises IOError: If file write fails
    :raises RuntimeError: If YAML serialization fails

    Example:
        >>> config = generate_index_config(["python"], Path("."))
        >>> write_config_file(config, Path(".praxis-os/config/index_config.yaml"))
        >>> # File written with proper YAML formatting

    AI Usage Tip:
        Call this after generate_index_config() during installation to
        persist the configuration to disk.
    """
    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            # Write with nice formatting
            yaml.dump(
                config,
                f,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                width=80,
            )
    except Exception as e:
        raise RuntimeError(f"Failed to write config to {output_path}: {e}") from e


def validate_config(config: dict) -> bool:
    """
    Validate generated configuration has required sections.

    Phase 7, Task 7.2: Sanity check before writing config.

    Checks that configuration dictionary has all required top-level
    sections and key fields.

    :param config: Configuration dictionary to validate
    :return: True if valid
    :raises ValueError: If configuration is invalid with specific error message

    Example:
        >>> config = generate_index_config(["python"], Path("."))
        >>> validate_config(config)
        True
        >>> # Missing required section raises ValueError
    """
    required_sections = ["indexes", "retrieval", "monitoring"]

    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section: {section}")

    # Validate indexes section
    if "vector" not in config["indexes"]:
        raise ValueError("Missing required index: vector")
    if "fts" not in config["indexes"]:
        raise ValueError("Missing required index: fts")
    if "metadata" not in config["indexes"]:
        raise ValueError("Missing required index: metadata")

    # Validate vector config
    vector = config["indexes"]["vector"]
    if not vector.get("enabled"):
        raise ValueError("Vector search must be enabled")
    if "model" not in vector:
        raise ValueError("Vector config missing model")

    # Validate monitoring has file_watcher
    if "file_watcher" not in config["monitoring"]:
        raise ValueError("Monitoring config missing file_watcher")

    return True


def format_config_summary(config: dict, languages: List[str]) -> str:
    """
    Format human-readable summary of generated configuration.

    Phase 7, Task 7.2: AI-friendly output for installation feedback.

    :param config: Generated configuration dictionary
    :param languages: Detected languages list
    :return: Formatted summary string

    Example:
        >>> config = generate_index_config(["python", "typescript"], Path("."))
        >>> print(format_config_summary(config, ["python", "typescript"]))
        Configuration Generated:
        =======================

        Indexes:
          ✓ Vector search (BGE-small-en-v1.5)
          ✓ Full-text search (BM25)
          ✓ Metadata filtering (4 scalar indexes)
          ✓ Code search (2 languages: python, typescript)

        File Watcher:
          ✓ Standards (*.md, *.json) - 5s debounce
          ✓ Code (*.py, *.ts, *.tsx) - 10s debounce
    """
    lines = [
        "Configuration Generated:",
        "=" * 50,
        "",
        "Indexes:",
    ]

    # Vector
    vector = config["indexes"]["vector"]
    lines.append(f"  ✓ Vector search ({vector['model']})")

    # FTS
    lines.append("  ✓ Full-text search (BM25)")

    # Metadata
    metadata = config["indexes"]["metadata"]
    num_indexes = len(metadata["scalar_indexes"])
    lines.append(f"  ✓ Metadata filtering ({num_indexes} scalar indexes)")

    # Code (if enabled)
    if "code" in config["indexes"]:
        code = config["indexes"]["code"]
        lang_str = ", ".join(code["languages"])
        lines.append(
            f"  ✓ Code search ({len(code['languages'])} languages: {lang_str})"
        )

    lines.append("")
    lines.append("File Watcher:")

    # Standards watcher
    standards = config["monitoring"]["file_watcher"]["watched_content"]["standards"]
    patterns = ", ".join(standards["patterns"])
    lines.append(
        f"  ✓ Standards ({patterns}) - {standards['debounce_seconds']}s debounce"
    )

    # Code watcher (if enabled)
    if "code" in config["monitoring"]["file_watcher"]["watched_content"]:
        code_watch = config["monitoring"]["file_watcher"]["watched_content"]["code"]
        patterns = ", ".join(code_watch["patterns"][:3])  # First 3 patterns
        if len(code_watch["patterns"]) > 3:
            patterns += ", ..."
        lines.append(
            f"  ✓ Code ({patterns}) - {code_watch['debounce_seconds']}s debounce"
        )

    return "\n".join(lines)


__all__ = [
    "generate_index_config",
    "write_config_file",
    "validate_config",
    "format_config_summary",
]

# pylint: disable=protected-access,redefined-outer-name,too-many-public-methods
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, and pytest fixtures are used as parameters.
"""
Unit tests for config.dsl.validation.signature_collisions module.

Tests signature collision detection across provider configuration files including:
- Signature extraction from YAML files
- Collision detection across multiple providers
- Confidence-based resolution
- CLI entry point behavior
"""

from pathlib import Path
from typing import List, Tuple, FrozenSet
from unittest.mock import Mock, patch, mock_open

import yaml

from config.dsl.validation.signature_collisions import (
    extract_signatures,
    check_collisions,
    check_signature_collisions,
    main,
)


class TestExtractSignatures:
    """Test extract_signatures() function."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_valid_yaml_with_signatures(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test extraction from valid YAML with signatures."""
        mock_yaml_load.return_value = {
            "provider": "openai",
            "patterns": {
                "chat_completion": {
                    "signature_fields": ["gen_ai.request.model", "gen_ai.system"],
                    "confidence_weight": 0.9,
                },
                "embedding": {
                    "signature_fields": ["gen_ai.request.model"],
                    "confidence_weight": 0.8,
                },
            },
        }
        filepath: Path = Path("openai/structure_patterns.yaml")

        signatures: List[Tuple[FrozenSet[str], str, float]] = extract_signatures(
            filepath
        )

        assert len(signatures) == 2
        # Check first signature
        assert signatures[0][0] == frozenset(["gen_ai.request.model", "gen_ai.system"])
        assert signatures[0][1] == "openai:chat_completion"
        assert signatures[0][2] == 0.9
        # Check second signature
        assert signatures[1][0] == frozenset(["gen_ai.request.model"])
        assert signatures[1][1] == "openai:embedding"
        assert signatures[1][2] == 0.8

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_missing_patterns_key(self, mock_yaml_load: Mock, _mock_file: Mock) -> None:
        """Test handling when patterns key is missing."""
        mock_yaml_load.return_value = {"provider": "openai", "version": "4.0"}
        filepath: Path = Path("openai/structure_patterns.yaml")

        signatures: List[Tuple[FrozenSet[str], str, float]] = extract_signatures(
            filepath
        )

        assert not signatures

    def test_file_not_found(self) -> None:
        """Test handling of non-existent file."""
        filepath: Path = Path("nonexistent/structure_patterns.yaml")

        signatures: List[Tuple[FrozenSet[str], str, float]] = extract_signatures(
            filepath
        )

        assert not signatures

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_yaml_parsing_error(self, mock_yaml_load: Mock, _mock_file: Mock) -> None:
        """Test handling of YAML parsing errors."""
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")
        filepath: Path = Path("openai/structure_patterns.yaml")

        signatures: List[Tuple[FrozenSet[str], str, float]] = extract_signatures(
            filepath
        )

        assert not signatures

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_empty_patterns(self, mock_yaml_load: Mock, _mock_file: Mock) -> None:
        """Test extraction from YAML with empty patterns."""
        mock_yaml_load.return_value = {"provider": "openai", "patterns": {}}
        filepath: Path = Path("openai/structure_patterns.yaml")

        signatures: List[Tuple[FrozenSet[str], str, float]] = extract_signatures(
            filepath
        )

        assert not signatures

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_missing_confidence_weight_uses_default(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test that missing confidence_weight uses default value."""
        mock_yaml_load.return_value = {
            "provider": "anthropic",
            "patterns": {
                "chat": {"signature_fields": ["gen_ai.request.model"]}
                # No confidence_weight specified
            },
        }
        filepath: Path = Path("anthropic/structure_patterns.yaml")

        signatures: List[Tuple[FrozenSet[str], str, float]] = extract_signatures(
            filepath
        )

        assert len(signatures) == 1
        assert signatures[0][2] == 0.9  # Default confidence

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_non_dict_data(self, mock_yaml_load: Mock, _mock_file: Mock) -> None:
        """Test handling when YAML root is not a dictionary."""
        mock_yaml_load.return_value = ["list", "not", "dict"]
        filepath: Path = Path("invalid/structure_patterns.yaml")

        signatures: List[Tuple[FrozenSet[str], str, float]] = extract_signatures(
            filepath
        )

        assert not signatures


class TestCheckCollisions:
    """Test check_collisions() function."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_no_collisions_unique_signatures(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test when all signatures are unique across providers."""
        mock_yaml_load.side_effect = [
            {
                "provider": "openai",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model", "gen_ai.system"],
                        "confidence_weight": 0.9,
                    }
                },
            },
            {
                "provider": "anthropic",
                "patterns": {
                    "chat": {
                        "signature_fields": [
                            "gen_ai.request.model",
                            "anthropic.version",
                        ],
                        "confidence_weight": 0.9,
                    }
                },
            },
        ]

        yaml_files: List[Path] = [
            Path("openai/structure_patterns.yaml"),
            Path("anthropic/structure_patterns.yaml"),
        ]

        has_collisions, messages = check_collisions(yaml_files)

        assert not has_collisions
        assert not messages

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_collision_between_two_providers(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test detection of collision between two providers."""
        mock_yaml_load.side_effect = [
            {
                "provider": "openai",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.9,
                    }
                },
            },
            {
                "provider": "anthropic",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.8,
                    }
                },
            },
        ]

        yaml_files: List[Path] = [
            Path("openai/structure_patterns.yaml"),
            Path("anthropic/structure_patterns.yaml"),
        ]

        has_collisions, messages = check_collisions(yaml_files)

        assert has_collisions
        assert len(messages) > 0
        # Verify collision message contains both providers
        full_message: str = "\n".join(messages)
        assert "openai" in full_message
        assert "anthropic" in full_message
        assert "Signature Collision" in full_message

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_same_provider_no_collision(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test that multiple patterns from same provider don't trigger collision."""
        mock_yaml_load.return_value = {
            "provider": "openai",
            "patterns": {
                "chat_v1": {
                    "signature_fields": ["gen_ai.request.model"],
                    "confidence_weight": 0.9,
                },
                "chat_v2": {
                    "signature_fields": ["gen_ai.request.model"],
                    "confidence_weight": 0.8,
                },
            },
        }

        yaml_files: List[Path] = [Path("openai/structure_patterns.yaml")]

        has_collisions, messages = check_collisions(yaml_files)

        assert not has_collisions
        assert not messages

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_multiple_collisions(self, mock_yaml_load: Mock, _mock_file: Mock) -> None:
        """Test detection of multiple different collisions."""
        mock_yaml_load.side_effect = [
            {
                "provider": "openai",
                "patterns": {
                    "chat": {
                        "signature_fields": ["field1"],
                        "confidence_weight": 0.9,
                    },
                    "embed": {
                        "signature_fields": ["field2"],
                        "confidence_weight": 0.9,
                    },
                },
            },
            {
                "provider": "anthropic",
                "patterns": {
                    "chat": {
                        "signature_fields": ["field1"],
                        "confidence_weight": 0.8,
                    },
                    "embed": {
                        "signature_fields": ["field2"],
                        "confidence_weight": 0.8,
                    },
                },
            },
        ]

        yaml_files: List[Path] = [
            Path("openai/structure_patterns.yaml"),
            Path("anthropic/structure_patterns.yaml"),
        ]

        has_collisions, messages = check_collisions(yaml_files)

        assert has_collisions
        # Should have messages for both collisions
        assert len(messages) >= 2

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_small_confidence_difference_warning(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test warning when confidence difference is too small."""
        mock_yaml_load.side_effect = [
            {
                "provider": "openai",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.90,
                    }
                },
            },
            {
                "provider": "anthropic",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.88,  # Difference of 0.02 < 0.05
                    }
                },
            },
        ]

        yaml_files: List[Path] = [
            Path("openai/structure_patterns.yaml"),
            Path("anthropic/structure_patterns.yaml"),
        ]

        has_collisions, messages = check_collisions(yaml_files)

        assert has_collisions
        full_message: str = "\n".join(messages)
        assert "WARNING" in full_message
        assert "Confidence difference is very small" in full_message

    def test_empty_file_list(self) -> None:
        """Test handling of empty file list."""
        yaml_files: List[Path] = []

        has_collisions, messages = check_collisions(yaml_files)

        assert not has_collisions
        assert not messages

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_collision_with_multiple_providers(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test collision detection with more than 2 providers."""
        mock_yaml_load.side_effect = [
            {
                "provider": "openai",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.9,
                    }
                },
            },
            {
                "provider": "anthropic",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.85,
                    }
                },
            },
            {
                "provider": "cohere",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.8,
                    }
                },
            },
        ]

        yaml_files: List[Path] = [
            Path("openai/structure_patterns.yaml"),
            Path("anthropic/structure_patterns.yaml"),
            Path("cohere/structure_patterns.yaml"),
        ]

        has_collisions, messages = check_collisions(yaml_files)

        assert has_collisions
        full_message: str = "\n".join(messages)
        assert "3 patterns" in full_message
        assert "3 providers" in full_message


class TestCheckSignatureCollisions:
    """Test check_signature_collisions() function."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_valid_structure_patterns_files(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test processing valid structure_patterns files."""
        mock_yaml_load.side_effect = [
            {
                "provider": "openai",
                "patterns": {
                    "chat": {
                        "signature_fields": ["field1"],
                        "confidence_weight": 0.9,
                    }
                },
            },
            {
                "provider": "anthropic",
                "patterns": {
                    "chat": {
                        "signature_fields": ["field2"],
                        "confidence_weight": 0.9,
                    }
                },
            },
        ]

        yaml_files: List[Path] = [
            Path("openai/structure_patterns.yaml"),
            Path("anthropic/structure_patterns.yaml"),
        ]

        has_collisions, messages, providers_checked = check_signature_collisions(
            yaml_files
        )

        assert not has_collisions
        assert not messages
        assert providers_checked == 2

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_mixed_file_types_filters_correctly(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test that only structure_patterns files are processed."""
        mock_yaml_load.return_value = {
            "provider": "openai",
            "patterns": {
                "chat": {
                    "signature_fields": ["field1"],
                    "confidence_weight": 0.9,
                }
            },
        }

        yaml_files: List[Path] = [
            Path("openai/structure_patterns.yaml"),
            Path("openai/navigation_rules.yaml"),
            Path("openai/field_mappings.yaml"),
        ]

        (
            has_collisions,
            _messages,
            providers_checked,
        ) = check_signature_collisions(yaml_files)

        assert not has_collisions
        assert providers_checked == 1  # Only structure_patterns counted
        assert mock_yaml_load.call_count == 1  # Only one file loaded

    def test_no_structure_patterns_files(self) -> None:
        """Test handling when no structure_patterns files provided."""
        yaml_files: List[Path] = [
            Path("openai/navigation_rules.yaml"),
            Path("openai/field_mappings.yaml"),
        ]

        has_collisions, messages, providers_checked = check_signature_collisions(
            yaml_files
        )

        assert not has_collisions
        assert not messages  #  Verify no collision messages
        assert providers_checked == 0

    def test_empty_file_list(self) -> None:
        """Test handling of empty file list."""
        yaml_files: List[Path] = []

        has_collisions, messages, providers_checked = check_signature_collisions(
            yaml_files
        )

        assert not has_collisions
        assert not messages  # Verify no collision messages
        assert providers_checked == 0

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_collisions_detected_and_propagated(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test that collisions are detected and propagated correctly."""
        mock_yaml_load.side_effect = [
            {
                "provider": "openai",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.9,
                    }
                },
            },
            {
                "provider": "anthropic",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.8,
                    }
                },
            },
        ]

        yaml_files: List[Path] = [
            Path("openai/structure_patterns.yaml"),
            Path("anthropic/structure_patterns.yaml"),
        ]

        has_collisions, messages, providers_checked = check_signature_collisions(
            yaml_files
        )

        assert has_collisions
        assert len(messages) > 0
        assert providers_checked == 2


class TestMain:
    """Test main() CLI entry point."""

    def test_no_arguments_shows_usage(self) -> None:
        """Test that running with no arguments shows usage and exits 1."""
        with patch("sys.argv", ["script_name"]):
            exit_code: int = main()

            assert exit_code == 1

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_successful_validation_exits_zero(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test successful validation returns exit code 0."""
        mock_yaml_load.side_effect = [
            {
                "provider": "openai",
                "patterns": {
                    "chat": {
                        "signature_fields": ["field1"],
                        "confidence_weight": 0.9,
                    }
                },
            },
            {
                "provider": "anthropic",
                "patterns": {
                    "chat": {
                        "signature_fields": ["field2"],
                        "confidence_weight": 0.9,
                    }
                },
            },
        ]

        with patch(
            "sys.argv",
            [
                "script",
                "openai/structure_patterns.yaml",
                "anthropic/structure_patterns.yaml",
            ],
        ):
            exit_code: int = main()

            assert exit_code == 0

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_collisions_detected_exits_one(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test collision detection returns exit code 1."""
        mock_yaml_load.side_effect = [
            {
                "provider": "openai",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.9,
                    }
                },
            },
            {
                "provider": "anthropic",
                "patterns": {
                    "chat": {
                        "signature_fields": ["gen_ai.request.model"],
                        "confidence_weight": 0.8,
                    }
                },
            },
        ]

        with patch(
            "sys.argv",
            [
                "script",
                "openai/structure_patterns.yaml",
                "anthropic/structure_patterns.yaml",
            ],
        ):
            exit_code: int = main()

            assert exit_code == 1

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_multiple_files_processed(
        self, mock_yaml_load: Mock, _mock_file: Mock
    ) -> None:
        """Test that multiple files are processed correctly."""
        mock_yaml_load.return_value = {
            "provider": "test",
            "patterns": {
                "chat": {
                    "signature_fields": ["field1", "field2"],
                    "confidence_weight": 0.9,
                }
            },
        }

        with patch(
            "sys.argv",
            [
                "script",
                "provider1/structure_patterns.yaml",
                "provider2/structure_patterns.yaml",
                "provider3/structure_patterns.yaml",
            ],
        ):
            exit_code: int = main()

            assert exit_code == 0
            assert mock_yaml_load.call_count == 3

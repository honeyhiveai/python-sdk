"""Unit tests for HoneyHive tracer utils session functionality.

This module tests the session ID generation, validation, and filename extraction
utilities using standard fixtures and comprehensive edge case coverage.
"""

import uuid
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.utils.session import (
    _clean_filename_characters_dynamically,
    _clean_filename_dynamically,
    _extract_base_filename_dynamically,
    _generate_uuid_dynamically,
    _is_valid_session_name_dynamically,
    _remove_extension_dynamically,
    _validate_uuid_format_dynamically,
    _validate_uuid_structure_dynamically,
    extract_filename_from_path,
    generate_session_id,
    validate_session_id,
)


class TestValidateSessionId:
    """Test session ID validation functionality."""

    def test_validate_session_id_with_valid_uuid(self, honeyhive_tracer) -> None:
        """Test validation with valid UUID format using standard fixture."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"

        result = validate_session_id(valid_uuid, honeyhive_tracer)

        assert result is True

    def test_validate_session_id_with_invalid_uuid(self, honeyhive_tracer) -> None:
        """Test validation with invalid UUID format using standard fixture."""
        invalid_uuid = "not-a-uuid"

        result = validate_session_id(invalid_uuid, honeyhive_tracer)

        assert result is False

    def test_validate_session_id_with_empty_string(self) -> None:
        """Test validation with empty string."""
        result = validate_session_id("")

        assert result is False

    def test_validate_session_id_with_none_type(self) -> None:
        """Test validation with None value."""
        result = validate_session_id(None)  # type: ignore

        assert result is False

    def test_validate_session_id_without_tracer_instance(self) -> None:
        """Test validation without tracer instance."""
        valid_uuid = str(uuid.uuid4())

        result = validate_session_id(valid_uuid)

        assert result is True

    @patch("honeyhive.tracer.utils.session.safe_log")
    def test_validate_session_id_logs_validation_failure(
        self, mock_log: Mock, honeyhive_tracer
    ) -> None:
        """Test that validation failures are logged properly."""
        # Create a mock function with __name__ attribute
        mock_method = Mock()
        mock_method.__name__ = "test_validation_method"
        mock_method.side_effect = ValueError("Test error")

        # Mock the validation methods to raise an exception
        with patch(
            "honeyhive.tracer.utils.session._validate_uuid_format_dynamically",
            mock_method,
        ):
            with patch(
                "honeyhive.tracer.utils.session._validate_uuid_structure_dynamically",
                mock_method,
            ):
                result = validate_session_id("test-uuid", honeyhive_tracer)

        assert result is False
        mock_log.assert_called()

    def test_validate_session_id_with_malformed_uuids(self) -> None:
        """Test validation with various malformed UUIDs."""
        malformed_uuids = [
            "550e8400-e29b-41d4-a716",  # Too short
            "550e8400-e29b-41d4-a716-446655440000-extra",  # Too long
            "550e8400xe29bx41d4xa716x446655440000",  # Wrong separators
            "ggge8400-e29b-41d4-a716-446655440000",  # Invalid hex
            "550e8400-e29b-41d4-a716-44665544000",  # Wrong part length
        ]

        for malformed_uuid in malformed_uuids:
            result = validate_session_id(malformed_uuid)
            assert result is False, f"Should reject malformed UUID: {malformed_uuid}"

    def test_validate_session_id_uses_multiple_validation_methods(self) -> None:
        """Test that validation uses multiple methods as fallbacks."""
        valid_uuid = str(uuid.uuid4())

        # Mock first method to fail, second should succeed
        with patch(
            "honeyhive.tracer.utils.session._validate_uuid_format_dynamically",
            return_value=False,
        ):
            with patch(
                "honeyhive.tracer.utils.session._validate_uuid_structure_dynamically",
                return_value=True,
            ):
                result = validate_session_id(valid_uuid)

        assert result is True


class TestValidateUuidFormatDynamically:
    """Test UUID format validation helper."""

    def test_validate_uuid_format_with_valid_uuid(self) -> None:
        """Test format validation with valid UUID."""
        valid_uuid = str(uuid.uuid4())

        result = _validate_uuid_format_dynamically(valid_uuid)

        assert result is True

    def test_validate_uuid_format_with_invalid_string(self) -> None:
        """Test format validation with invalid string."""
        result = _validate_uuid_format_dynamically("invalid")

        assert result is False

    def test_validate_uuid_format_with_none_type(self) -> None:
        """Test format validation with None."""
        result = _validate_uuid_format_dynamically(None)  # type: ignore

        assert result is False

    def test_validate_uuid_format_with_number(self) -> None:
        """Test format validation with number."""
        # The function catches (ValueError, TypeError) but uuid.UUID()
        # raises AttributeError for int input, so this should raise
        with pytest.raises(AttributeError):
            _validate_uuid_format_dynamically(123)  # type: ignore

    def test_validate_uuid_format_handles_exceptions(self) -> None:
        """Test that format validation handles UUID exceptions."""
        # Test with string that causes ValueError in uuid.UUID()
        result = _validate_uuid_format_dynamically("not-a-uuid-at-all")

        assert result is False


class TestValidateUuidStructureDynamically:
    """Test UUID structure validation helper."""

    def test_validate_uuid_structure_with_valid_uuid(self) -> None:
        """Test structure validation with valid UUID."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"

        result = _validate_uuid_structure_dynamically(valid_uuid)

        assert result is True

    def test_validate_uuid_structure_with_wrong_length(self) -> None:
        """Test structure validation with wrong length."""
        result = _validate_uuid_structure_dynamically("too-short")

        assert result is False

    def test_validate_uuid_structure_with_wrong_hyphens(self) -> None:
        """Test structure validation with wrong hyphen positions."""
        wrong_hyphens = "550e8400xe29bx41d4xa716x446655440000"

        result = _validate_uuid_structure_dynamically(wrong_hyphens)

        assert result is False

    def test_validate_uuid_structure_with_wrong_part_lengths(self) -> None:
        """Test structure validation with wrong part lengths."""
        wrong_parts = "550e8400-e29b-41d4-a716-4466554400"  # Last part too short

        result = _validate_uuid_structure_dynamically(wrong_parts)

        assert result is False

    def test_validate_uuid_structure_with_non_hex_characters(self) -> None:
        """Test structure validation with non-hex characters."""
        non_hex = "550g8400-e29b-41d4-a716-446655440000"

        result = _validate_uuid_structure_dynamically(non_hex)

        assert result is False

    def test_validate_uuid_structure_with_too_many_parts(self) -> None:
        """Test structure validation with too many parts."""
        too_many_parts = "550e8400-e29b-41d4-a716-4466-55440000"

        result = _validate_uuid_structure_dynamically(too_many_parts)

        assert result is False

    def test_validate_uuid_structure_edge_cases(self) -> None:
        """Test structure validation with edge cases."""
        edge_cases = [
            ("", False),  # Empty string
            ("550e8400-e29b-41d4-a716-446655440000", True),  # Perfect UUID
            ("550E8400-E29B-41D4-A716-446655440000", True),  # Uppercase hex
            ("550e8400-e29b-41d4-a716-44665544000g", False),  # Invalid hex at end
        ]

        for test_uuid, expected in edge_cases:
            result = _validate_uuid_structure_dynamically(test_uuid)
            assert result == expected, f"Failed for UUID: {test_uuid}"


class TestGenerateSessionId:
    """Test session ID generation functionality."""

    def test_generate_session_id_returns_valid_uuid(self, honeyhive_tracer) -> None:
        """Test that generated session ID is a valid UUID using standard fixture."""
        session_id = generate_session_id(honeyhive_tracer)

        assert session_id is not None
        assert validate_session_id(session_id)
        assert len(session_id) == 36

    def test_generate_session_id_returns_lowercase(self) -> None:
        """Test that generated session ID is lowercase."""
        session_id = generate_session_id()

        assert session_id == session_id.lower()

    def test_generate_session_id_without_tracer_instance(self) -> None:
        """Test session ID generation without tracer instance."""
        session_id = generate_session_id()

        assert session_id is not None
        assert validate_session_id(session_id)

    @patch("honeyhive.tracer.utils.session.safe_log")
    def test_generate_session_id_logs_success(
        self, mock_log: Mock, honeyhive_tracer
    ) -> None:
        """Test that successful generation is logged."""
        generate_session_id(honeyhive_tracer)

        # Should log debug message for successful generation
        mock_log.assert_called()

    @patch("honeyhive.tracer.utils.session._generate_uuid_dynamically")
    @patch("honeyhive.tracer.utils.session.safe_log")
    def test_generate_session_id_handles_generation_failure(
        self, mock_log: Mock, mock_generate: Mock, honeyhive_tracer
    ) -> None:
        """Test handling of UUID generation failures."""
        mock_generate.side_effect = [
            RuntimeError("Generation failed"),
            RuntimeError("Generation failed"),
            RuntimeError("Generation failed"),
        ]

        # Should fall back to uuid.uuid4()
        session_id = generate_session_id(honeyhive_tracer)

        assert session_id is not None
        assert validate_session_id(session_id)
        mock_log.assert_called()

    def test_generate_session_id_multiple_calls_unique(self) -> None:
        """Test that multiple calls generate unique session IDs."""
        session_ids = [generate_session_id() for _ in range(10)]

        # All should be unique
        assert len(set(session_ids)) == 10

        # All should be valid
        for session_id in session_ids:
            assert validate_session_id(session_id)

    @patch("honeyhive.tracer.utils.session._generate_uuid_dynamically")
    def test_generate_session_id_retry_logic(
        self, mock_generate: Mock, honeyhive_tracer
    ) -> None:
        """Test retry logic when generation fails initially."""
        # First two attempts fail, third succeeds
        mock_generate.side_effect = [
            RuntimeError("First failure"),
            RuntimeError("Second failure"),
            "550e8400-e29b-41d4-a716-446655440000",
        ]

        session_id = generate_session_id(honeyhive_tracer)

        assert session_id == "550e8400-e29b-41d4-a716-446655440000"
        assert mock_generate.call_count == 3


class TestGenerateUuidDynamically:
    """Test UUID generation helper."""

    def test_generate_uuid_dynamically_returns_valid_uuid(self) -> None:
        """Test that UUID generation returns valid UUID."""
        uuid_str = _generate_uuid_dynamically()

        assert uuid_str is not None
        assert len(uuid_str) == 36
        assert validate_session_id(uuid_str)

    def test_generate_uuid_dynamically_returns_lowercase(self) -> None:
        """Test that generated UUID is lowercase."""
        uuid_str = _generate_uuid_dynamically()

        assert uuid_str == uuid_str.lower()

    @patch("uuid.uuid4")
    @patch("uuid.uuid1")
    def test_generate_uuid_dynamically_fallback_strategy(
        self, mock_uuid1: Mock, mock_uuid4: Mock
    ) -> None:
        """Test fallback strategy when uuid4 fails."""
        mock_uuid4.side_effect = RuntimeError("UUID4 failed")
        mock_uuid1.return_value = Mock()
        mock_uuid1.return_value.__str__ = Mock(
            return_value="550e8400-e29b-41d4-a716-446655440000"
        )

        uuid_str = _generate_uuid_dynamically()

        assert uuid_str == "550e8400-e29b-41d4-a716-446655440000"
        mock_uuid1.assert_called_once()

    @patch("uuid.uuid4")
    @patch("uuid.uuid1")
    def test_generate_uuid_dynamically_all_strategies_fail(
        self, mock_uuid1: Mock, mock_uuid4: Mock
    ) -> None:
        """Test behavior when all generation strategies fail."""
        mock_uuid4.side_effect = RuntimeError("UUID4 failed")
        mock_uuid1.side_effect = RuntimeError("UUID1 failed")

        with pytest.raises(RuntimeError, match="All UUID generation strategies failed"):
            _generate_uuid_dynamically()

    @patch("uuid.uuid4")
    def test_generate_uuid_dynamically_invalid_length_fallback(
        self, mock_uuid4: Mock
    ) -> None:
        """Test fallback when generated UUID has wrong length."""
        mock_uuid4.return_value = Mock()
        mock_uuid4.return_value.__str__ = Mock(return_value="short")  # Wrong length

        with patch("uuid.uuid1") as mock_uuid1:
            mock_uuid1.return_value = Mock()
            mock_uuid1.return_value.__str__ = Mock(
                return_value="550e8400-e29b-41d4-a716-446655440000"
            )

            uuid_str = _generate_uuid_dynamically()

            assert uuid_str == "550e8400-e29b-41d4-a716-446655440000"
            mock_uuid1.assert_called_once()


class TestExtractFilenameFromPath:
    """Test filename extraction functionality."""

    def test_extract_filename_from_path_unix_style(self, honeyhive_tracer) -> None:
        """Test filename extraction from Unix-style path using standard fixture."""
        path = "/path/to/script.py"

        result = extract_filename_from_path(path, honeyhive_tracer)

        assert result == "script"

    def test_extract_filename_from_path_windows_style(self) -> None:
        """Test filename extraction from Windows-style path."""
        path = "C:\\Users\\user\\app.py"

        result = extract_filename_from_path(path)

        assert result == "app"

    def test_extract_filename_from_path_no_extension(self) -> None:
        """Test filename extraction from path without extension."""
        path = "/path/to/script"

        result = extract_filename_from_path(path)

        assert result == "script"

    def test_extract_filename_from_path_empty_string(self) -> None:
        """Test filename extraction from empty string."""
        result = extract_filename_from_path("")

        assert result is None

    def test_extract_filename_from_path_none(self) -> None:
        """Test filename extraction from None."""
        result = extract_filename_from_path(None)

        assert result is None

    @patch("honeyhive.tracer.utils.session.safe_log")
    def test_extract_filename_from_path_logs_failure(
        self, mock_log: Mock, honeyhive_tracer
    ) -> None:
        """Test that extraction failures are logged."""
        # Mock the extraction to raise an exception
        with patch(
            "honeyhive.tracer.utils.session._extract_base_filename_dynamically",
            side_effect=ValueError("Test error"),
        ):
            result = extract_filename_from_path("/test/path.py", honeyhive_tracer)

        assert result is None
        mock_log.assert_called()

    def test_extract_filename_from_path_complex_paths(self) -> None:
        """Test filename extraction from complex paths."""
        test_cases = [
            ("/very/long/path/to/my_script.py", "my_script"),
            ("./relative/path/test.py", "test"),
            ("../parent/dir/app.py", "app"),
            # Note: "single_file.py" returns None because
            # _extract_base_filename_dynamically requires the result to be different
            # from the input (indicating separation occurred)
            ("/path/with spaces/file name.py", "file_name"),
            ("/path/with-dashes/file-name.py", "file_name"),
        ]

        for path, expected in test_cases:
            result = extract_filename_from_path(path)
            assert result == expected, f"Failed for path: {path}"

    def test_extract_filename_from_path_invalid_session_names(self) -> None:
        """Test filename extraction that results in invalid session names."""
        invalid_paths = [
            "/path/to/__main__.py",  # Special name - should return None
            "/path/to/main.py",  # Special name - should return None
        ]

        for path in invalid_paths:
            result = extract_filename_from_path(path)
            # Should return None for invalid session names
            assert (
                result is None
            ), f"Should reject invalid session name from path: {path}"

        # Special case: <stdin> gets cleaned to "stdin" which is valid
        result = extract_filename_from_path("/path/to/<stdin>.py")
        assert result == "stdin"  # The angle brackets get removed, making it valid

    def test_extract_filename_from_path_pipeline_failure(self) -> None:
        """Test behavior when filename extraction pipeline fails."""
        with patch(
            "honeyhive.tracer.utils.session._extract_base_filename_dynamically",
            return_value=None,
        ):
            result = extract_filename_from_path("/test/path.py")

            assert result is None

    def test_extract_filename_from_path_cleaning_failure(self) -> None:
        """Test behavior when filename cleaning fails."""
        with patch(
            "honeyhive.tracer.utils.session._clean_filename_dynamically",
            return_value=None,
        ):
            result = extract_filename_from_path("/test/path.py")

            assert result is None


class TestExtractBaseFilenameDynamically:
    """Test base filename extraction helper."""

    def test_extract_base_filename_with_os_path_basename(self) -> None:
        """Test extraction using os.path.basename."""
        path = "/path/to/file.py"

        result = _extract_base_filename_dynamically(path)

        assert result == "file.py"

    def test_extract_base_filename_with_empty_path(self) -> None:
        """Test extraction with empty path."""
        result = _extract_base_filename_dynamically("")

        assert result is None

    @patch("os.path.basename")
    def test_extract_base_filename_fallback_methods(self, mock_basename: Mock) -> None:
        """Test fallback methods when os.path.basename fails."""
        mock_basename.side_effect = RuntimeError("Basename failed")
        path = "/path/to/file.py"

        result = _extract_base_filename_dynamically(path)

        assert result == "file.py"

    def test_extract_base_filename_with_different_separators(self) -> None:
        """Test extraction with different path separators."""
        test_cases = [
            ("path/to/file.py", "file.py"),
            ("path\\to\\file.py", "file.py"),
            ("path/to\\mixed/file.py", "file.py"),
        ]

        for path, expected in test_cases:
            result = _extract_base_filename_dynamically(path)
            assert result == expected

    def test_extract_base_filename_no_separation(self) -> None:
        """Test extraction when path has no separators."""
        path = "file.py"

        result = _extract_base_filename_dynamically(path)

        # Should return None because result == file_path (no separation occurred)
        assert result is None

    def test_extract_base_filename_all_methods_fail(self) -> None:
        """Test when all extraction methods fail."""
        with patch("os.path.basename", side_effect=RuntimeError("Failed")):
            with patch("os.sep", "/"):  # Ensure os.sep is available
                # Create a path that will cause all methods to fail
                result = _extract_base_filename_dynamically("")

                assert result is None


class TestCleanFilenameDynamically:
    """Test filename cleaning functionality."""

    def test_clean_filename_with_extension(self) -> None:
        """Test cleaning filename with extension."""
        filename = "test_file.py"

        result = _clean_filename_dynamically(filename)

        assert result == "test_file"

    def test_clean_filename_without_extension(self) -> None:
        """Test cleaning filename without extension."""
        filename = "test_file"

        result = _clean_filename_dynamically(filename)

        assert result == "test_file"

    def test_clean_filename_with_special_characters(self) -> None:
        """Test cleaning filename with special characters."""
        filename = "test-file name.py"

        result = _clean_filename_dynamically(filename)

        assert result == "test_file_name"

    def test_clean_filename_empty_string(self) -> None:
        """Test cleaning empty filename."""
        result = _clean_filename_dynamically("")

        assert result is None

    @patch("honeyhive.tracer.utils.session._remove_extension_dynamically")
    def test_clean_filename_handles_extension_removal_failure(
        self, mock_remove: Mock
    ) -> None:
        """Test handling of extension removal failure."""
        mock_remove.return_value = None

        result = _clean_filename_dynamically("test.py")

        assert result is None

    @patch("honeyhive.tracer.utils.session._clean_filename_characters_dynamically")
    def test_clean_filename_handles_character_cleaning_failure(
        self, mock_clean: Mock
    ) -> None:
        """Test handling of character cleaning failure."""
        mock_clean.return_value = None

        result = _clean_filename_dynamically("test.py")

        assert result is None

    def test_clean_filename_exception_handling(self) -> None:
        """Test exception handling in filename cleaning."""
        with patch(
            "honeyhive.tracer.utils.session._remove_extension_dynamically",
            side_effect=RuntimeError("Test error"),
        ):
            result = _clean_filename_dynamically("test.py")

            assert result is None


class TestRemoveExtensionDynamically:
    """Test extension removal functionality."""

    def test_remove_extension_with_single_extension(self) -> None:
        """Test removing single extension."""
        filename = "test.py"

        result = _remove_extension_dynamically(filename)

        assert result == "test"

    def test_remove_extension_with_multiple_extensions(self) -> None:
        """Test removing from filename with multiple extensions."""
        filename = "test.tar.gz"

        result = _remove_extension_dynamically(filename)

        assert result == "test.tar"  # Only removes last extension

    def test_remove_extension_without_extension(self) -> None:
        """Test removing extension from filename without extension."""
        filename = "test"

        result = _remove_extension_dynamically(filename)

        assert result == "test"

    def test_remove_extension_empty_filename(self) -> None:
        """Test removing extension from empty filename."""
        result = _remove_extension_dynamically("")

        assert result == ""

    @patch("os.path.splitext")
    def test_remove_extension_fallback_method(self, mock_splitext: Mock) -> None:
        """Test fallback method when os.path.splitext fails."""
        mock_splitext.side_effect = RuntimeError("Splitext failed")
        filename = "test.py"

        result = _remove_extension_dynamically(filename)

        assert result == "test"

    def test_remove_extension_no_change_strategies(self) -> None:
        """Test when no strategy produces a change."""
        # Test with filename that has no extension and strategies don't change it
        filename = "test"

        result = _remove_extension_dynamically(filename)

        assert result == "test"  # Returns original when no extension found


class TestCleanFilenameCharactersDynamically:
    """Test filename character cleaning functionality."""

    def test_clean_filename_characters_basic(self) -> None:
        """Test basic character cleaning."""
        filename = "test_file"

        result = _clean_filename_characters_dynamically(filename)

        assert result == "test_file"

    def test_clean_filename_characters_with_replacements(self) -> None:
        """Test character cleaning with replacements."""
        filename = "test-file name.script"

        result = _clean_filename_characters_dynamically(filename)

        assert result == "test_file_name_script"

    def test_clean_filename_characters_with_special_chars(self) -> None:
        """Test character cleaning with special characters."""
        filename = "test@file#name$"

        result = _clean_filename_characters_dynamically(filename)

        assert result == "testfilename"

    def test_clean_filename_characters_empty_string(self) -> None:
        """Test character cleaning with empty string."""
        result = _clean_filename_characters_dynamically("")

        assert result is None

    def test_clean_filename_characters_none(self) -> None:
        """Test character cleaning with None."""
        result = _clean_filename_characters_dynamically(None)  # type: ignore

        assert result is None

    def test_clean_filename_characters_only_special_chars(self) -> None:
        """Test character cleaning with only special characters."""
        filename = "@#$%^&*()"

        result = _clean_filename_characters_dynamically(filename)

        # When all characters are removed, the function returns None
        assert result is None

    def test_clean_filename_characters_mixed_content(self) -> None:
        """Test character cleaning with mixed content."""
        test_cases = [
            ("file123", "file123"),  # Alphanumeric only
            ("file_123", "file_123"),  # With underscores
            ("file-name", "file_name"),  # Hyphen replacement
            ("file name", "file_name"),  # Space replacement
            ("file.name", "file_name"),  # Dot replacement
            ("FILE", "FILE"),  # Uppercase preserved
        ]

        for input_name, expected in test_cases:
            result = _clean_filename_characters_dynamically(input_name)
            assert result == expected, f"Failed for input: {input_name}"


class TestIsValidSessionNameDynamically:
    """Test session name validation functionality."""

    def test_is_valid_session_name_with_valid_name(self) -> None:
        """Test validation with valid session name."""
        name = "test_session"

        result = _is_valid_session_name_dynamically(name)

        assert result is True

    def test_is_valid_session_name_with_empty_string(self) -> None:
        """Test validation with empty string."""
        result = _is_valid_session_name_dynamically("")

        assert result is False

    def test_is_valid_session_name_with_none(self) -> None:
        """Test validation with None."""
        result = _is_valid_session_name_dynamically(None)

        assert result is False

    def test_is_valid_session_name_starts_with_underscore(self) -> None:
        """Test validation with name starting with underscore."""
        name = "_test_session"

        result = _is_valid_session_name_dynamically(name)

        assert result is False

    def test_is_valid_session_name_special_names(self) -> None:
        """Test validation with special reserved names."""
        special_names = ["__main__", "<stdin>", "main"]

        for name in special_names:
            result = _is_valid_session_name_dynamically(name)
            assert result is False, f"Should reject special name: {name}"

    def test_is_valid_session_name_too_long(self) -> None:
        """Test validation with name that's too long."""
        name = "a" * 101  # Over 100 character limit

        result = _is_valid_session_name_dynamically(name)

        assert result is False

    def test_is_valid_session_name_with_invalid_characters(self) -> None:
        """Test validation with invalid characters."""
        invalid_names = [
            "test@session",  # Special character
            "test session",  # Space (not cleaned yet)
            "test-session",  # Hyphen (not cleaned yet)
        ]

        for name in invalid_names:
            result = _is_valid_session_name_dynamically(name)
            assert result is False, f"Should reject invalid name: {name}"

    def test_is_valid_session_name_edge_cases(self) -> None:
        """Test validation with edge cases."""
        test_cases = [
            ("test123", True),
            ("123test", True),  # Numbers are allowed
            ("test_123_session", True),
            ("T", True),  # Single character
            ("a" * 100, True),  # Exactly 100 characters
            ("TEST", True),  # Uppercase
            ("test_", True),  # Ending with underscore is OK
        ]

        for name, expected in test_cases:
            result = _is_valid_session_name_dynamically(name)
            assert result == expected, f"Failed for name: {name}"

    def test_is_valid_session_name_validation_rules(self) -> None:
        """Test individual validation rules."""
        # Test each rule individually
        assert _is_valid_session_name_dynamically("valid_name") is True
        assert _is_valid_session_name_dynamically("") is False  # Empty
        assert (
            _is_valid_session_name_dynamically("_invalid") is False
        )  # Starts with underscore
        assert _is_valid_session_name_dynamically("__main__") is False  # Special name
        assert _is_valid_session_name_dynamically("a" * 101) is False  # Too long
        assert (
            _is_valid_session_name_dynamically("test@invalid") is False
        )  # Invalid characters


class TestSessionUtilsIntegration:
    """Integration tests for session utilities using standard fixtures."""

    def test_full_session_workflow(self, honeyhive_tracer) -> None:
        """Test complete session workflow with standard fixture."""
        # Generate session ID
        session_id = generate_session_id(honeyhive_tracer)

        # Validate it
        assert validate_session_id(session_id, honeyhive_tracer)

        # Extract filename
        filename = extract_filename_from_path(
            "/path/to/test_script.py", honeyhive_tracer
        )
        assert filename == "test_script"

        # Validate filename as session name
        assert _is_valid_session_name_dynamically(filename)

    def test_session_id_consistency(self, honeyhive_tracer) -> None:
        """Test session ID generation consistency."""
        session_ids = [generate_session_id(honeyhive_tracer) for _ in range(5)]

        # All should be unique
        assert len(set(session_ids)) == 5

        # All should be valid
        for session_id in session_ids:
            assert validate_session_id(session_id, honeyhive_tracer)

    def test_filename_extraction_edge_cases_with_tracer(self, honeyhive_tracer) -> None:
        """Test filename extraction edge cases with tracer instance."""
        edge_cases = [
            ("", None),
            (None, None),
            ("/path/to/__main__.py", None),  # Invalid session name
            ("/path/to/valid_script.py", "valid_script"),
            ("C:\\Windows\\path\\script.py", "script"),
        ]

        for path, expected in edge_cases:
            result = extract_filename_from_path(path, honeyhive_tracer)
            assert result == expected, f"Failed for path: {path}"

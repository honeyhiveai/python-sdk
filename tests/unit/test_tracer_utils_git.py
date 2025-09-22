"""Unit tests for HoneyHive tracer utils git functionality.

This module tests the git information collection utilities including telemetry
settings, repository detection, and git command execution using standard fixtures
and comprehensive edge case coverage following Agent OS testing standards.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Comprehensive git testing requires extensive test coverage

import subprocess
from typing import Any
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.utils.git import (
    _collect_git_information_dynamically,
    _convert_to_boolean_dynamically,
    _generate_commit_link_dynamically,
    _get_git_branch_dynamically,
    _get_git_commit_hash_dynamically,
    _get_git_repo_url_dynamically,
    _get_main_module_path_dynamically,
    _get_main_module_relative_path_dynamically,
    _get_repository_root_dynamically,
    _get_telemetry_setting_dynamically,
    _handle_git_command_error_dynamically,
    _handle_git_not_found_error_dynamically,
    _handle_unexpected_git_error_dynamically,
    _has_uncommitted_changes_dynamically,
    _is_git_repository_dynamically,
    _log_git_collection_success_dynamically,
    get_git_information,
    is_telemetry_enabled,
)


class TestIsTelemetryEnabled:
    """Test telemetry enablement checking functionality."""

    @patch("honeyhive.tracer.utils.git._get_telemetry_setting_dynamically")
    @patch("honeyhive.tracer.utils.git._convert_to_boolean_dynamically")
    def test_is_telemetry_enabled_calls_helper_functions(
        self, mock_convert: Any, mock_get_setting: Any, honeyhive_tracer: Any
    ) -> None:
        """Test that telemetry check calls helper functions properly."""
        mock_get_setting.return_value = "true"
        mock_convert.return_value = True

        result = is_telemetry_enabled(honeyhive_tracer)

        assert result is True
        mock_get_setting.assert_called_once_with(honeyhive_tracer)
        mock_convert.assert_called_once_with(
            "true", default=True, tracer_instance=honeyhive_tracer
        )

    @patch("honeyhive.tracer.utils.git._get_telemetry_setting_dynamically")
    @patch("honeyhive.tracer.utils.git._convert_to_boolean_dynamically")
    def test_is_telemetry_enabled_with_false_setting(
        self, mock_convert: Any, mock_get_setting: Any, honeyhive_tracer: Any
    ) -> None:
        """Test telemetry check with false setting."""
        mock_get_setting.return_value = "false"
        mock_convert.return_value = False

        result = is_telemetry_enabled(honeyhive_tracer)

        assert result is False

    def test_is_telemetry_enabled_without_tracer_instance(self) -> None:
        """Test telemetry check without tracer instance."""
        with patch(
            "honeyhive.tracer.utils.git._get_telemetry_setting_dynamically"
        ) as mock_get_setting:
            with patch(
                "honeyhive.tracer.utils.git._convert_to_boolean_dynamically"
            ) as mock_convert:
                mock_get_setting.return_value = "true"
                mock_convert.return_value = True

                result = is_telemetry_enabled()

                assert result is True
                mock_get_setting.assert_called_once_with(None)


class TestGetTelemetrySettingDynamically:
    """Test telemetry setting retrieval functionality."""

    @patch("os.getenv")
    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_get_telemetry_setting_honeyhive_telemetry(
        self, mock_log: Any, mock_getenv: Any, honeyhive_tracer: Any
    ) -> None:
        """Test telemetry setting retrieval with HONEYHIVE_TELEMETRY."""
        mock_getenv.side_effect = lambda key: (
            "TRUE" if key == "HONEYHIVE_TELEMETRY" else None
        )

        result = _get_telemetry_setting_dynamically(honeyhive_tracer)

        assert result == "true"
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert args[2] == "Found telemetry setting"
        assert kwargs["honeyhive_data"]["env_var"] == "HONEYHIVE_TELEMETRY"
        assert kwargs["honeyhive_data"]["value"] == "TRUE"

    @patch("os.getenv")
    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_get_telemetry_setting_hh_telemetry(
        self, mock_log: Any, mock_getenv: Any, honeyhive_tracer: Any
    ) -> None:
        """Test telemetry setting retrieval with HH_TELEMETRY."""
        mock_getenv.side_effect = lambda key: "false" if key == "HH_TELEMETRY" else None

        result = _get_telemetry_setting_dynamically(honeyhive_tracer)

        assert result == "false"
        mock_log.assert_called_once()
        _, kwargs = mock_log.call_args
        assert kwargs["honeyhive_data"]["env_var"] == "HH_TELEMETRY"

    @patch("os.getenv")
    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_get_telemetry_setting_telemetry_enabled(
        self, mock_log: Any, mock_getenv: Any, honeyhive_tracer: Any
    ) -> None:
        """Test telemetry setting retrieval with TELEMETRY_ENABLED."""
        mock_getenv.side_effect = lambda key: (
            "0" if key == "TELEMETRY_ENABLED" else None
        )

        result = _get_telemetry_setting_dynamically(honeyhive_tracer)

        assert result == "0"
        mock_log.assert_called_once()
        _, kwargs = mock_log.call_args
        assert kwargs["honeyhive_data"]["env_var"] == "TELEMETRY_ENABLED"

    @patch("os.getenv")
    def test_get_telemetry_setting_no_env_vars(
        self, mock_getenv: Any, honeyhive_tracer: Any
    ) -> None:
        """Test telemetry setting retrieval with no environment variables set."""
        mock_getenv.return_value = None

        result = _get_telemetry_setting_dynamically(honeyhive_tracer)

        assert result == "true"

    @patch("os.getenv")
    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_get_telemetry_setting_priority_order(
        self, mock_log: Any, mock_getenv: Any, honeyhive_tracer: Any
    ) -> None:
        """Test that environment variables are checked in priority order."""

        # Set multiple env vars, should pick the first one found
        def mock_getenv_side_effect(key: Any) -> Any:
            if key == "HONEYHIVE_TELEMETRY":
                return "first"
            if key == "HH_TELEMETRY":
                return "second"
            if key == "TELEMETRY_ENABLED":
                return "third"
            return None

        mock_getenv.side_effect = mock_getenv_side_effect

        result = _get_telemetry_setting_dynamically(honeyhive_tracer)

        assert result == "first"
        mock_log.assert_called_once()
        _, kwargs = mock_log.call_args
        assert kwargs["honeyhive_data"]["env_var"] == "HONEYHIVE_TELEMETRY"


class TestConvertToBooleanDynamically:
    """Test boolean conversion functionality."""

    def test_convert_to_boolean_false_patterns(self, honeyhive_tracer: Any) -> None:
        """Test boolean conversion with false patterns."""
        false_values = ["false", "0", "f", "no", "n", "off", "disabled"]

        for value in false_values:
            result = _convert_to_boolean_dynamically(
                value, tracer_instance=honeyhive_tracer
            )
            assert result is False, f"Failed for value: {value}"

            # Test case insensitive
            result = _convert_to_boolean_dynamically(
                value.upper(), tracer_instance=honeyhive_tracer
            )
            assert result is False, f"Failed for uppercase value: {value.upper()}"

    def test_convert_to_boolean_true_patterns(self, honeyhive_tracer: Any) -> None:
        """Test boolean conversion with true patterns."""
        true_values = ["true", "1", "t", "yes", "y", "on", "enabled"]

        for value in true_values:
            result = _convert_to_boolean_dynamically(
                value, tracer_instance=honeyhive_tracer
            )
            assert result is True, f"Failed for value: {value}"

            # Test case insensitive
            result = _convert_to_boolean_dynamically(
                value.upper(), tracer_instance=honeyhive_tracer
            )
            assert result is True, f"Failed for uppercase value: {value.upper()}"

    def test_convert_to_boolean_with_whitespace(self, honeyhive_tracer: Any) -> None:
        """Test boolean conversion with whitespace."""
        result = _convert_to_boolean_dynamically(
            "  true  ", tracer_instance=honeyhive_tracer
        )
        assert result is True

        result = _convert_to_boolean_dynamically(
            "  false  ", tracer_instance=honeyhive_tracer
        )
        assert result is False

    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_convert_to_boolean_unknown_value_default_true(
        self, mock_log: Any, honeyhive_tracer: Any
    ) -> None:
        """Test boolean conversion with unknown value and default True."""
        result = _convert_to_boolean_dynamically(
            "unknown", default=True, tracer_instance=honeyhive_tracer
        )

        assert result is True
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert args[2] == "Unknown telemetry value, using default"
        assert kwargs["honeyhive_data"]["value"] == "unknown"
        assert kwargs["honeyhive_data"]["default"] is True

    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_convert_to_boolean_unknown_value_default_false(
        self, mock_log: Any, honeyhive_tracer: Any
    ) -> None:
        """Test boolean conversion with unknown value and default False."""
        result = _convert_to_boolean_dynamically(
            "unknown", default=False, tracer_instance=honeyhive_tracer
        )

        assert result is False
        mock_log.assert_called_once()
        _, kwargs = mock_log.call_args
        assert kwargs["honeyhive_data"]["default"] is False


class TestGetGitInformation:
    """Test main git information collection functionality."""

    @patch("honeyhive.tracer.utils.git.is_telemetry_enabled")
    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_get_git_information_telemetry_disabled(
        self, mock_log: Any, mock_telemetry: Any, honeyhive_tracer: Any
    ) -> None:
        """Test git information collection when telemetry is disabled."""
        mock_telemetry.return_value = False

        result = get_git_information(verbose=True, tracer_instance=honeyhive_tracer)

        assert result == {"error": "Telemetry disabled"}
        mock_log.assert_called_once_with(
            honeyhive_tracer,
            "debug",
            "Telemetry disabled. Skipping git information collection.",
        )

    @patch("honeyhive.tracer.utils.git.is_telemetry_enabled")
    def test_get_git_information_telemetry_disabled_not_verbose(
        self, mock_telemetry: Any, honeyhive_tracer: Any
    ) -> None:
        """Test git information collection when telemetry is disabled and not
        verbose."""
        mock_telemetry.return_value = False

        result = get_git_information(verbose=False, tracer_instance=honeyhive_tracer)

        assert result == {"error": "Telemetry disabled"}

    @patch("honeyhive.tracer.utils.git.is_telemetry_enabled")
    @patch("honeyhive.tracer.utils.git._is_git_repository_dynamically")
    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_get_git_information_not_git_repo(
        self,
        mock_log: Any,
        mock_is_git: Any,
        mock_telemetry: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test git information collection when not in git repository."""
        mock_telemetry.return_value = True
        mock_is_git.return_value = False

        result = get_git_information(verbose=True, tracer_instance=honeyhive_tracer)

        assert result == {"error": "Not a git repository"}
        mock_log.assert_called_once_with(
            honeyhive_tracer,
            "debug",
            "Not a git repository. Skipping git information collection.",
        )

    @patch("honeyhive.tracer.utils.git.is_telemetry_enabled")
    @patch("honeyhive.tracer.utils.git._is_git_repository_dynamically")
    @patch("honeyhive.tracer.utils.git._collect_git_information_dynamically")
    @patch("honeyhive.tracer.utils.git._log_git_collection_success_dynamically")
    def test_get_git_information_success(  # pylint: disable=R0917 # too-many-positional-arguments
        self,
        mock_log_success: Any,
        mock_collect: Any,
        mock_is_git: Any,
        mock_telemetry: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test successful git information collection."""
        mock_telemetry.return_value = True
        mock_is_git.return_value = True
        expected_git_info = {
            "commit_hash": "abc123",
            "branch": "main",
            "repo_url": "https://github.com/user/repo.git",
        }
        mock_collect.return_value = expected_git_info

        result = get_git_information(verbose=True, tracer_instance=honeyhive_tracer)

        assert result == expected_git_info
        mock_collect.assert_called_once_with(True)
        mock_log_success.assert_called_once_with(expected_git_info)

    @patch("honeyhive.tracer.utils.git.is_telemetry_enabled")
    @patch("honeyhive.tracer.utils.git._is_git_repository_dynamically")
    @patch("honeyhive.tracer.utils.git._collect_git_information_dynamically")
    def test_get_git_information_success_not_verbose(
        self,
        mock_collect: Any,
        mock_is_git: Any,
        mock_telemetry: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test successful git information collection without verbose logging."""
        mock_telemetry.return_value = True
        mock_is_git.return_value = True
        expected_git_info = {"commit_hash": "abc123"}
        mock_collect.return_value = expected_git_info

        result = get_git_information(verbose=False, tracer_instance=honeyhive_tracer)

        assert result == expected_git_info
        mock_collect.assert_called_once_with(False)

    @patch("honeyhive.tracer.utils.git.is_telemetry_enabled")
    @patch("honeyhive.tracer.utils.git._is_git_repository_dynamically")
    @patch("honeyhive.tracer.utils.git._collect_git_information_dynamically")
    @patch("honeyhive.tracer.utils.git._handle_git_command_error_dynamically")
    def test_get_git_information_subprocess_error(  # pylint: disable=R0917 # too-many-positional-arguments
        self,
        mock_handle_error: Any,
        mock_collect: Any,
        mock_is_git: Any,
        mock_telemetry: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test git information collection with subprocess error."""
        mock_telemetry.return_value = True
        mock_is_git.return_value = True
        error = subprocess.CalledProcessError(1, "git")
        mock_collect.side_effect = error
        expected_error_result = {"error": "Git command failed"}
        mock_handle_error.return_value = expected_error_result

        result = get_git_information(verbose=True, tracer_instance=honeyhive_tracer)

        assert result == expected_error_result
        mock_handle_error.assert_called_once_with(error, True)

    @patch("honeyhive.tracer.utils.git.is_telemetry_enabled")
    @patch("honeyhive.tracer.utils.git._is_git_repository_dynamically")
    @patch("honeyhive.tracer.utils.git._collect_git_information_dynamically")
    @patch("honeyhive.tracer.utils.git._handle_git_not_found_error_dynamically")
    def test_get_git_information_file_not_found(  # pylint: disable=R0917 # too-many-positional-arguments
        self,
        mock_handle_error: Any,
        mock_collect: Any,
        mock_is_git: Any,
        mock_telemetry: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test git information collection with FileNotFoundError."""
        mock_telemetry.return_value = True
        mock_is_git.return_value = True
        mock_collect.side_effect = FileNotFoundError("git not found")
        expected_error_result = {"error": "Git not found"}
        mock_handle_error.return_value = expected_error_result

        result = get_git_information(verbose=True, tracer_instance=honeyhive_tracer)

        assert result == expected_error_result
        mock_handle_error.assert_called_once_with(True)

    @patch("honeyhive.tracer.utils.git.is_telemetry_enabled")
    @patch("honeyhive.tracer.utils.git._is_git_repository_dynamically")
    @patch("honeyhive.tracer.utils.git._collect_git_information_dynamically")
    @patch("honeyhive.tracer.utils.git._handle_unexpected_git_error_dynamically")
    def test_get_git_information_unexpected_error(  # pylint: disable=R0917 # too-many-positional-arguments
        self,
        mock_handle_error: Any,
        mock_collect: Any,
        mock_is_git: Any,
        mock_telemetry: Any,
        honeyhive_tracer: Any,
    ) -> None:
        """Test git information collection with unexpected error."""
        mock_telemetry.return_value = True
        mock_is_git.return_value = True
        error = ValueError("Unexpected error")
        mock_collect.side_effect = error
        expected_error_result = {"error": "Unexpected error"}
        mock_handle_error.return_value = expected_error_result

        result = get_git_information(verbose=True, tracer_instance=honeyhive_tracer)

        assert result == expected_error_result
        mock_handle_error.assert_called_once_with(error, True)


class TestIsGitRepositoryDynamically:
    """Test git repository detection functionality."""

    @patch("os.getcwd")
    @patch("subprocess.run")
    def test_is_git_repository_true(self, mock_run: Any, mock_getcwd: Any) -> None:
        """Test git repository detection when in git repository."""
        mock_getcwd.return_value = "/path/to/repo"
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _is_git_repository_dynamically()

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd="/path/to/repo",
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("os.getcwd")
    @patch("subprocess.run")
    def test_is_git_repository_false(self, mock_run: Any, mock_getcwd: Any) -> None:
        """Test git repository detection when not in git repository."""
        mock_getcwd.return_value = "/path/to/non-repo"
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = _is_git_repository_dynamically()

        assert result is False

    @patch("os.getcwd")
    @patch("subprocess.run")
    def test_is_git_repository_exception(self, mock_run: Any, mock_getcwd: Any) -> None:
        """Test git repository detection with exception."""
        mock_getcwd.return_value = "/path/to/repo"
        mock_run.side_effect = Exception("Command failed")

        result = _is_git_repository_dynamically()

        assert result is False


class TestCollectGitInformationDynamically:
    """Test git information collection functionality."""

    @patch("os.getcwd")
    @patch("honeyhive.tracer.utils.git._get_git_commit_hash_dynamically")
    @patch("honeyhive.tracer.utils.git._get_git_branch_dynamically")
    @patch("honeyhive.tracer.utils.git._get_git_repo_url_dynamically")
    @patch("honeyhive.tracer.utils.git._has_uncommitted_changes_dynamically")
    @patch("honeyhive.tracer.utils.git._get_main_module_relative_path_dynamically")
    def test_collect_git_information_all_success(  # pylint: disable=R0917 # too-many-positional-arguments
        self,
        mock_path: Any,
        mock_changes: Any,
        mock_url: Any,
        mock_branch: Any,
        mock_commit: Any,
        mock_getcwd: Any,
    ) -> None:
        """Test git information collection when all steps succeed."""
        mock_getcwd.return_value = "/repo"
        mock_commit.return_value = "abc123"
        mock_branch.return_value = "main"
        mock_url.return_value = "https://github.com/user/repo.git"
        mock_changes.return_value = True
        mock_path.return_value = "src/main.py"

        result = _collect_git_information_dynamically(verbose=True)

        expected = {
            "commit_hash": "abc123",
            "branch": "main",
            "repo_url": "https://github.com/user/repo.git",
            "uncommitted_changes": True,
            "relative_path": "src/main.py",
            "commit_link": "https://github.com/user/repo.git/commit/abc123",
        }
        assert result == expected

    @patch("os.getcwd")
    @patch("honeyhive.tracer.utils.git._get_git_commit_hash_dynamically")
    @patch("honeyhive.tracer.utils.git._get_git_branch_dynamically")
    @patch("honeyhive.tracer.utils.git._get_git_repo_url_dynamically")
    @patch("honeyhive.tracer.utils.git._has_uncommitted_changes_dynamically")
    @patch("honeyhive.tracer.utils.git._get_main_module_relative_path_dynamically")
    def test_collect_git_information_partial_success(  # pylint: disable=R0917 # too-many-positional-arguments
        self,
        mock_path: Any,
        mock_changes: Any,
        mock_url: Any,
        mock_branch: Any,
        mock_commit: Any,
        mock_getcwd: Any,
    ) -> None:
        """Test git information collection when some steps fail."""
        mock_getcwd.return_value = "/repo"
        mock_commit.return_value = "abc123"
        mock_branch.return_value = None  # Failed to get branch
        mock_url.return_value = "https://github.com/user/repo.git"
        mock_changes.return_value = False
        mock_path.return_value = None  # Failed to get path

        result = _collect_git_information_dynamically(verbose=False)

        expected = {
            "commit_hash": "abc123",
            "branch": None,
            "repo_url": "https://github.com/user/repo.git",
            "uncommitted_changes": False,
            "relative_path": None,
            "commit_link": "https://github.com/user/repo.git/commit/abc123",
        }
        assert result == expected

    @patch("os.getcwd")
    @patch("honeyhive.tracer.utils.git._get_git_commit_hash_dynamically")
    def test_collect_git_information_exception_handling(
        self, mock_commit: Any, mock_getcwd: Any
    ) -> None:
        """Test git information collection with exception in collector."""
        mock_getcwd.return_value = "/repo"
        mock_commit.side_effect = Exception("Git command failed")

        # Should not raise exception, just skip the failed collector
        result = _collect_git_information_dynamically(verbose=True)

        # Should return empty dict or dict without commit_hash
        assert isinstance(result, dict)
        # The function sets keys to None when there's an exception
        assert result["commit_hash"] is None


class TestGetGitCommitHashDynamically:
    """Test git commit hash retrieval functionality."""

    @patch("subprocess.run")
    def test_get_git_commit_hash_success(self, mock_run: Any) -> None:
        """Test successful git commit hash retrieval."""
        mock_result = Mock()
        mock_result.stdout = "abc123def456\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _get_git_commit_hash_dynamically("/repo")

        assert result == "abc123def456"
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "HEAD"],
            cwd="/repo",
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_get_git_commit_hash_failure(self, mock_run: Any) -> None:
        """Test git commit hash retrieval failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        # The function doesn't catch exceptions, so it will raise
        with pytest.raises(subprocess.CalledProcessError):
            _get_git_commit_hash_dynamically("/repo")

    @patch("subprocess.run")
    def test_get_git_commit_hash_exception(self, mock_run: Any) -> None:
        """Test git commit hash retrieval with exception."""
        mock_run.side_effect = Exception("Command failed")

        # The function doesn't catch exceptions, so it will raise
        with pytest.raises(Exception):
            _get_git_commit_hash_dynamically("/repo")


class TestGetGitBranchDynamically:
    """Test git branch retrieval functionality."""

    @patch("subprocess.run")
    def test_get_git_branch_success(self, mock_run: Any) -> None:
        """Test successful git branch retrieval."""
        mock_result = Mock()
        mock_result.stdout = "main\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _get_git_branch_dynamically("/repo")

        assert result == "main"
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd="/repo",
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_get_git_branch_failure(self, mock_run: Any) -> None:
        """Test git branch retrieval failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        # The function doesn't catch exceptions, so it will raise
        with pytest.raises(subprocess.CalledProcessError):
            _get_git_branch_dynamically("/repo")

    @patch("subprocess.run")
    def test_get_git_branch_exception(self, mock_run: Any) -> None:
        """Test git branch retrieval with exception."""
        mock_run.side_effect = Exception("Command failed")

        # The function doesn't catch exceptions, so it will raise
        with pytest.raises(Exception):
            _get_git_branch_dynamically("/repo")


class TestGetGitRepoUrlDynamically:
    """Test git repository URL retrieval functionality."""

    @patch("subprocess.run")
    def test_get_git_repo_url_success(self, mock_run: Any) -> None:
        """Test successful git repository URL retrieval."""
        mock_result = Mock()
        mock_result.stdout = "https://github.com/user/repo.git\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _get_git_repo_url_dynamically("/repo")

        # The function strips .git suffix
        assert result == "https://github.com/user/repo"
        mock_run.assert_called_once_with(
            ["git", "config", "--get", "remote.origin.url"],
            cwd="/repo",
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_get_git_repo_url_failure(self, mock_run: Any) -> None:
        """Test git repository URL retrieval failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        # The function doesn't handle exceptions - it lets them propagate
        with pytest.raises(subprocess.CalledProcessError):
            _get_git_repo_url_dynamically("/repo")

    @patch("subprocess.run")
    def test_get_git_repo_url_exception(self, mock_run: Any) -> None:
        """Test git repository URL retrieval with exception."""
        mock_run.side_effect = Exception("Command failed")

        # The function doesn't handle exceptions - it lets them propagate
        with pytest.raises(Exception):
            _get_git_repo_url_dynamically("/repo")


class TestGenerateCommitLinkDynamically:
    """Test commit link generation functionality."""

    def test_generate_commit_link_github(self) -> None:
        """Test commit link generation for GitHub repository."""
        repo_url = "https://github.com/user/repo.git"
        commit_hash = "abc123def456"

        result = _generate_commit_link_dynamically(repo_url, commit_hash)

        expected = "https://github.com/user/repo.git/commit/abc123def456"
        assert result == expected

    def test_generate_commit_link_github_no_git_suffix(self) -> None:
        """Test commit link generation for GitHub repository without .git suffix."""
        repo_url = "https://github.com/user/repo"
        commit_hash = "abc123def456"

        result = _generate_commit_link_dynamically(repo_url, commit_hash)

        expected = "https://github.com/user/repo/commit/abc123def456"
        assert result == expected

    def test_generate_commit_link_gitlab(self) -> None:
        """Test commit link generation for GitLab repository."""
        repo_url = "https://gitlab.com/user/repo.git"
        commit_hash = "abc123def456"

        result = _generate_commit_link_dynamically(repo_url, commit_hash)

        expected = "https://gitlab.com/user/repo.git/-/commit/abc123def456"
        assert result == expected

    def test_generate_commit_link_bitbucket(self) -> None:
        """Test commit link generation for Bitbucket repository."""
        repo_url = "https://bitbucket.org/user/repo.git"
        commit_hash = "abc123def456"

        result = _generate_commit_link_dynamically(repo_url, commit_hash)

        expected = "https://bitbucket.org/user/repo.git/commits/abc123def456"
        assert result == expected

    def test_generate_commit_link_unknown_provider(self) -> None:
        """Test commit link generation for unknown git provider."""
        repo_url = "https://custom-git.com/user/repo.git"
        commit_hash = "abc123def456"

        result = _generate_commit_link_dynamically(repo_url, commit_hash)

        # Should return the original repo URL for unknown providers
        expected = "https://custom-git.com/user/repo.git"
        assert result == expected


class TestHasUncommittedChangesDynamically:
    """Test uncommitted changes detection functionality."""

    @patch("subprocess.run")
    def test_has_uncommitted_changes_true(self, mock_run: Any) -> None:
        """Test uncommitted changes detection when changes exist."""
        mock_result = Mock()
        mock_result.stdout = " M modified_file.py\n?? new_file.py\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _has_uncommitted_changes_dynamically("/repo")

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "status", "--porcelain"],
            cwd="/repo",
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_has_uncommitted_changes_false(self, mock_run: Any) -> None:
        """Test uncommitted changes detection when no changes exist."""
        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _has_uncommitted_changes_dynamically("/repo")

        assert result is False

    @patch("subprocess.run")
    def test_has_uncommitted_changes_failure(self, mock_run: Any) -> None:
        """Test uncommitted changes detection failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        # The function doesn't handle exceptions - it lets them propagate
        with pytest.raises(subprocess.CalledProcessError):
            _has_uncommitted_changes_dynamically("/repo")

    @patch("subprocess.run")
    def test_has_uncommitted_changes_exception(self, mock_run: Any) -> None:
        """Test uncommitted changes detection with exception."""
        mock_run.side_effect = Exception("Command failed")

        # The function doesn't handle exceptions - it lets them propagate
        with pytest.raises(Exception):
            _has_uncommitted_changes_dynamically("/repo")


class TestGetMainModuleRelativePathDynamically:
    """Test main module relative path retrieval functionality."""

    @patch("honeyhive.tracer.utils.git._get_repository_root_dynamically")
    @patch("honeyhive.tracer.utils.git._get_main_module_path_dynamically")
    def test_get_main_module_relative_path_success(
        self, mock_main_path: Any, mock_repo_root: Any
    ) -> None:
        """Test successful main module relative path retrieval."""
        mock_repo_root.return_value = "/repo"
        mock_main_path.return_value = "/repo/src/main.py"

        result = _get_main_module_relative_path_dynamically("/repo")

        assert result == "src/main.py"

    @patch("honeyhive.tracer.utils.git._get_repository_root_dynamically")
    @patch("honeyhive.tracer.utils.git._get_main_module_path_dynamically")
    def test_get_main_module_relative_path_no_repo_root(
        self, mock_main_path: Any, mock_repo_root: Any
    ) -> None:
        """Test main module relative path retrieval when repo root not found."""
        mock_repo_root.return_value = None
        mock_main_path.return_value = "/repo/src/main.py"

        result = _get_main_module_relative_path_dynamically("/repo")

        assert result is None

    @patch("honeyhive.tracer.utils.git._get_repository_root_dynamically")
    @patch("honeyhive.tracer.utils.git._get_main_module_path_dynamically")
    def test_get_main_module_relative_path_no_main_path(
        self, mock_main_path: Any, mock_repo_root: Any
    ) -> None:
        """Test main module relative path retrieval when main path not found."""
        mock_repo_root.return_value = "/repo"
        mock_main_path.return_value = None

        result = _get_main_module_relative_path_dynamically("/repo")

        assert result is None

    @patch("honeyhive.tracer.utils.git._get_repository_root_dynamically")
    @patch("honeyhive.tracer.utils.git._get_main_module_path_dynamically")
    def test_get_main_module_relative_path_not_in_repo(
        self, mock_main_path: Any, mock_repo_root: Any
    ) -> None:
        """Test main module relative path retrieval when main path not in repo."""
        mock_repo_root.return_value = "/repo"
        mock_main_path.return_value = "/other/path/main.py"

        result = _get_main_module_relative_path_dynamically("/repo")

        # The function returns the relative path even if it's outside the repo
        assert result == "../other/path/main.py"

    @patch("honeyhive.tracer.utils.git._get_repository_root_dynamically")
    @patch("honeyhive.tracer.utils.git._get_main_module_path_dynamically")
    def test_get_main_module_relative_path_exception(
        self, mock_main_path: Any, mock_repo_root: Any
    ) -> None:
        """Test main module relative path retrieval with exception."""
        mock_repo_root.return_value = "/repo"
        mock_main_path.side_effect = Exception("Path error")

        result = _get_main_module_relative_path_dynamically("/repo")

        assert result is None


class TestGetRepositoryRootDynamically:
    """Test repository root retrieval functionality."""

    @patch("subprocess.run")
    def test_get_repository_root_success(self, mock_run: Any) -> None:
        """Test successful repository root retrieval."""
        mock_result = Mock()
        mock_result.stdout = "/path/to/repo\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _get_repository_root_dynamically("/repo")

        assert result == "/path/to/repo"
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--show-toplevel"],
            cwd="/repo",
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_get_repository_root_failure(self, mock_run: Any) -> None:
        """Test repository root retrieval failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        result = _get_repository_root_dynamically("/repo")

        assert result is None

    @patch("subprocess.run")
    def test_get_repository_root_exception(self, mock_run: Any) -> None:
        """Test repository root retrieval with exception."""
        mock_run.side_effect = Exception("Command failed")

        result = _get_repository_root_dynamically("/repo")

        assert result is None


class TestGetMainModulePathDynamically:
    """Test main module path retrieval functionality."""

    def test_get_main_module_path_with_main_module(self) -> None:
        """Test main module path retrieval when __main__ module exists."""
        mock_main_module = Mock()
        mock_main_module.__file__ = "/path/to/main.py"

        with patch.dict("sys.modules", {"__main__": mock_main_module}):
            result = _get_main_module_path_dynamically()

        assert result == "/path/to/main.py"

    def test_get_main_module_path_no_main_module(self) -> None:
        """Test main module path retrieval when __main__ module doesn't exist."""
        with patch.dict("sys.modules", {}, clear=True):
            result = _get_main_module_path_dynamically()

        assert result is None

    def test_get_main_module_path_no_file_attribute(self) -> None:
        """Test main module path retrieval when __main__ module has no __file__."""
        mock_main_module = Mock()
        del mock_main_module.__file__  # Remove __file__ attribute

        with patch.dict("sys.modules", {"__main__": mock_main_module}):
            result = _get_main_module_path_dynamically()

        assert result is None

    def test_get_main_module_path_none_file_attribute(self) -> None:
        """Test main module path retrieval when __main__ module __file__ is None."""
        mock_main_module = Mock()
        mock_main_module.__file__ = None

        with patch.dict("sys.modules", {"__main__": mock_main_module}):
            result = _get_main_module_path_dynamically()

        assert result is None


class TestLogGitCollectionSuccessDynamically:
    """Test git collection success logging functionality."""

    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_log_git_collection_success_with_data(self, mock_log: Any) -> None:
        """Test git collection success logging with data."""
        git_info = {
            "commit_hash": "abc123",
            "branch": "main",
            "repo_url": "https://github.com/user/repo.git",
            "uncommitted_changes": True,
        }

        _log_git_collection_success_dynamically(git_info)

        mock_log.assert_called_once_with(
            None,
            "debug",
            "Git information collected successfully",
            honeyhive_data={
                "commit_hash": "abc123",  # Short hash (first 8 chars)
                "branch": "main",
                "has_changes": True,  # Renamed from uncommitted_changes
            },
        )

    @patch("honeyhive.tracer.utils.git.safe_log")
    def test_log_git_collection_success_empty_data(self, mock_log: Any) -> None:
        """Test git collection success logging with empty data."""
        git_info: dict[str, Any] = {}

        _log_git_collection_success_dynamically(git_info)

        mock_log.assert_called_once_with(
            None,
            "debug",
            "Git information collected successfully",
            honeyhive_data={},  # Empty dict when no git info available
        )


class TestHandleGitCommandErrorDynamically:
    """Test git command error handling functionality."""

    def test_handle_git_command_error_verbose(self) -> None:
        """Test git command error handling with verbose logging."""
        error = subprocess.CalledProcessError(1, ["git", "rev-parse", "HEAD"])
        error.stderr = "fatal: not a git repository"

        result = _handle_git_command_error_dynamically(error, verbose=True)

        expected = {"error": "Failed to retrieve Git info. Is this a valid repo?"}
        assert result == expected

    def test_handle_git_command_error_not_verbose(self) -> None:
        """Test git command error handling without verbose logging."""
        error = subprocess.CalledProcessError(1, ["git", "rev-parse", "HEAD"])
        error.stderr = "fatal: not a git repository"

        result = _handle_git_command_error_dynamically(error, verbose=False)

        expected = {"error": "Failed to retrieve Git info. Is this a valid repo?"}
        assert result == expected

    def test_handle_git_command_error_no_stderr(self) -> None:
        """Test git command error handling when stderr is None."""
        error = subprocess.CalledProcessError(1, ["git", "rev-parse", "HEAD"])
        error.stderr = None

        result = _handle_git_command_error_dynamically(error, verbose=True)

        expected = {"error": "Failed to retrieve Git info. Is this a valid repo?"}
        assert result == expected


class TestHandleGitNotFoundErrorDynamically:
    """Test git not found error handling functionality."""

    def test_handle_git_not_found_error_verbose(self) -> None:
        """Test git not found error handling with verbose logging."""
        result = _handle_git_not_found_error_dynamically(verbose=True)

        expected = {"error": "Git is not installed or not in PATH."}
        assert result == expected

    def test_handle_git_not_found_error_not_verbose(self) -> None:
        """Test git not found error handling without verbose logging."""
        result = _handle_git_not_found_error_dynamically(verbose=False)

        expected = {"error": "Git is not installed or not in PATH."}
        assert result == expected


class TestHandleUnexpectedGitErrorDynamically:
    """Test unexpected git error handling functionality."""

    def test_handle_unexpected_git_error_verbose(self) -> None:
        """Test unexpected git error handling with verbose logging."""
        error = ValueError("Unexpected error message")

        result = _handle_unexpected_git_error_dynamically(error, verbose=True)

        expected = {"error": "Error getting git info: Unexpected error message"}
        assert result == expected

    def test_handle_unexpected_git_error_not_verbose(self) -> None:
        """Test unexpected git error handling without verbose logging."""
        error = ValueError("Unexpected error message")

        result = _handle_unexpected_git_error_dynamically(error, verbose=False)

        expected = {"error": "Error getting git info: Unexpected error message"}
        assert result == expected

    def test_handle_unexpected_git_error_no_message(self) -> None:
        """Test unexpected git error handling when exception has no message."""
        error = ValueError()

        result = _handle_unexpected_git_error_dynamically(error, verbose=True)

        expected = {"error": "Error getting git info: "}
        assert result == expected

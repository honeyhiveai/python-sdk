"""
Unit tests for DevelopmentAwareBundleLoader.

Tests cover bundle loading, environment detection, lazy compilation,
transform helpers, and accessor methods with complete mock isolation.
"""

# pylint: disable=protected-access,too-many-lines,redefined-outer-name,too-many-public-methods,line-too-long,too-many-positional-arguments,too-many-locals,unused-argument
# Justification:
# - protected-access: Testing internal methods for complete coverage
# - too-many-lines: Comprehensive test coverage requires large file (78 tests)
# - redefined-outer-name: Standard pytest fixture usage pattern
# - too-many-public-methods: Complete coverage requires many test methods
# - line-too-long: Black formatter may create long lines for readability
# - too-many-positional-arguments: Multiple fixtures and mocks required
# - too-many-locals: Complex test scenarios require multiple local variables
# - unused-argument: Mock fixtures that are only used via @patch decoration

import os
import pickle
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import Mock, mock_open, patch

import pytest

from honeyhive.tracer.processing.semantic_conventions.bundle_loader import (
    DevelopmentAwareBundleLoader,
)
from honeyhive.tracer.processing.semantic_conventions.bundle_types import (
    CompiledProviderBundle,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_tracer_instance() -> Mock:
    """Create a mock tracer instance for safe_log calls."""
    tracer: Mock = Mock()
    tracer.project_name = "test-project"
    tracer.session_id = "test-session"
    return tracer


@pytest.fixture
def mock_bundle_path(tmp_path: Path) -> Path:
    """Create a temporary bundle path."""
    bundle_path: Path = tmp_path / "compiled_providers.pkl"
    return bundle_path


@pytest.fixture
def mock_source_path(tmp_path: Path) -> Path:
    """Create a temporary source path."""
    source_path: Path = tmp_path / "config" / "dsl"
    source_path.mkdir(parents=True, exist_ok=True)
    return source_path


@pytest.fixture
def sample_bundle() -> CompiledProviderBundle:
    """Create a sample compiled provider bundle."""
    bundle: CompiledProviderBundle = CompiledProviderBundle(
        provider_signatures={
            "openai": [frozenset(["gen_ai.system", "gen_ai.request.model"])],
            "anthropic": [frozenset(["gen_ai.system", "llm.provider"])],
        },
        field_mappings={
            "openai": {"model": "gen_ai.request.model"},
            "anthropic": {"model": "gen_ai.request.model"},
        },
        transform_registry={},
        validation_rules={},
        signature_to_provider={
            frozenset(["gen_ai.system", "gen_ai.request.model"]): ("openai", 1.0),
            frozenset(["gen_ai.system", "llm.provider"]): ("anthropic", 1.0),
        },
        extraction_functions={
            "openai": "def extract_openai_data(attributes):\n    return {'provider': 'openai'}",
            "anthropic": "def extract_anthropic_data(attributes):\n    return {'provider': 'anthropic'}",
        },
        build_metadata={
            "build_time": "2025-01-01T00:00:00Z",
            "version": "4.0.0",
            "provider_count": 2,
        },
    )
    return bundle


# =============================================================================
# TEST CLASS: INITIALIZATION
# =============================================================================


class TestDevelopmentAwareBundleLoaderInit:
    """Test initialization of DevelopmentAwareBundleLoader."""

    def test_init_with_tracer_instance(
        self, mock_bundle_path: Path, mock_source_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test initialization with tracer instance."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        assert loader.bundle_path == mock_bundle_path
        assert loader.source_path == mock_source_path
        assert loader.tracer_instance == mock_tracer_instance
        assert (
            loader.bundle_metadata_path
            == mock_bundle_path.parent / "bundle_metadata.json"
        )
        assert loader._cached_bundle is None
        assert not loader._cached_functions

    def test_init_without_tracer_instance(
        self, mock_bundle_path: Path, mock_source_path: Path
    ) -> None:
        """Test initialization without tracer instance (production mode)."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
        )

        assert loader.bundle_path == mock_bundle_path
        assert loader.source_path == mock_source_path
        assert loader.tracer_instance is None
        assert loader._cached_bundle is None
        assert not loader._cached_functions

    def test_init_without_source_path(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test initialization without source path (production only mode)."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        assert loader.bundle_path == mock_bundle_path
        assert loader.source_path is None
        assert loader.tracer_instance == mock_tracer_instance


# =============================================================================
# TEST CLASS: BUNDLE LOADING
# =============================================================================


class TestBundleLoading:
    """Test bundle loading workflows."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._is_development_environment"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._load_development_bundle"
    )
    def test_load_provider_bundle_development_mode(
        self,
        mock_load_dev: Mock,
        mock_is_dev: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test load_provider_bundle in development mode."""
        mock_is_dev.return_value = True
        mock_load_dev.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader.load_provider_bundle()

        assert result == sample_bundle
        mock_is_dev.assert_called_once()
        mock_load_dev.assert_called_once()

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._is_development_environment"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._load_production_bundle"
    )
    def test_load_provider_bundle_production_mode(
        self,
        mock_load_prod: Mock,
        mock_is_dev: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test load_provider_bundle in production mode."""
        mock_is_dev.return_value = False
        mock_load_prod.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader.load_provider_bundle()

        assert result == sample_bundle
        mock_is_dev.assert_called_once()
        mock_load_prod.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    def test_load_production_bundle_not_cached(
        self,
        mock_pickle_load: Mock,
        mock_file_open: Mock,
        mock_exists: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test _load_production_bundle when bundle is not cached."""
        mock_exists.return_value = True
        mock_pickle_load.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader._load_production_bundle()

        assert result == sample_bundle
        assert loader._cached_bundle == sample_bundle
        mock_file_open.assert_called_once_with(mock_bundle_path, "rb")
        mock_pickle_load.assert_called_once()

    def test_load_production_bundle_cached(
        self,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test _load_production_bundle when bundle is already cached."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader._cached_bundle = sample_bundle  # type: ignore[assignment]

        result: Dict[str, Any] = loader._load_production_bundle()

        assert result == sample_bundle

    @patch("pathlib.Path.exists")
    def test_load_production_bundle_file_not_found(
        self, mock_exists: Mock, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _load_production_bundle raises FileNotFoundError when bundle missing."""
        mock_exists.return_value = False

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        with pytest.raises(FileNotFoundError) as exc_info:
            loader._load_production_bundle()

        assert "Compiled bundle not found" in str(exc_info.value)

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    def test_load_production_bundle_pickle_error(
        self,
        mock_pickle_load: Mock,
        mock_file_open: Mock,
        mock_exists: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _load_production_bundle raises exception on pickle load error."""
        mock_exists.return_value = True
        mock_pickle_load.side_effect = pickle.UnpicklingError("Invalid pickle data")

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        with pytest.raises(pickle.UnpicklingError):
            loader._load_production_bundle()

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._needs_recompilation"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._load_bundle_with_debug_info"
    )
    def test_load_development_bundle_no_recompilation_needed(
        self,
        mock_load_debug: Mock,
        mock_needs_recompile: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test _load_development_bundle when recompilation not needed."""
        mock_needs_recompile.return_value = False
        mock_load_debug.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader._load_development_bundle()

        assert result == sample_bundle
        mock_needs_recompile.assert_called_once()
        mock_load_debug.assert_called_once()

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._needs_recompilation"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._recompile_bundle"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._load_bundle_with_debug_info"
    )
    def test_load_development_bundle_with_recompilation(
        self,
        mock_load_debug: Mock,
        mock_recompile: Mock,
        mock_needs_recompile: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test _load_development_bundle when recompilation needed."""
        mock_needs_recompile.return_value = True
        mock_load_debug.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader._load_development_bundle()

        assert result == sample_bundle
        assert loader._cached_bundle is None  # Cache cleared before reload
        mock_needs_recompile.assert_called_once()
        mock_recompile.assert_called_once()
        mock_load_debug.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._load_bundle_metadata"
    )
    def test_load_bundle_with_debug_info_success(
        self,
        mock_load_metadata: Mock,
        mock_pickle_load: Mock,
        mock_file_open: Mock,
        mock_exists: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test _load_bundle_with_debug_info successfully loads with metadata."""
        mock_exists.return_value = True
        mock_pickle_load.return_value = sample_bundle
        metadata: Dict[str, Any] = {"version": "4.0.0", "provider_count": 2}
        mock_load_metadata.return_value = metadata

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader._load_bundle_with_debug_info()

        assert result == sample_bundle
        assert loader._cached_bundle == sample_bundle
        mock_load_metadata.assert_called_once()

    @patch("pathlib.Path.exists")
    def test_load_bundle_with_debug_info_file_not_found(
        self,
        mock_exists: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _load_bundle_with_debug_info raises FileNotFoundError."""
        mock_exists.return_value = False

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        with pytest.raises(FileNotFoundError) as exc_info:
            loader._load_bundle_with_debug_info()

        assert "Compiled bundle not found" in str(exc_info.value)


# =============================================================================
# TEST CLASS: ENVIRONMENT DETECTION
# =============================================================================


class TestEnvironmentDetection:
    """Test development environment detection logic."""

    def test_is_development_environment_source_path_exists(
        self, mock_bundle_path: Path, mock_source_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _is_development_environment returns True when source path exists."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        # source_path.exists() returns True by default (from fixture)
        result: bool = loader._is_development_environment()

        assert result is True

    @patch("os.environ.get")
    def test_is_development_environment_env_flag_set(
        self, mock_env_get: Mock, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _is_development_environment returns True when HONEYHIVE_DEV_MODE=true."""
        mock_env_get.side_effect = lambda key, default=None: (
            "true" if key == "HONEYHIVE_DEV_MODE" else "false"
        )

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=None,
            tracer_instance=mock_tracer_instance,
        )

        result: bool = loader._is_development_environment()

        assert result is True

    @patch("sys.modules", {"pytest": Mock()})
    def test_is_development_environment_pytest_detected(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _is_development_environment returns True when pytest is in sys.modules."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=None,
            tracer_instance=mock_tracer_instance,
        )

        result: bool = loader._is_development_environment()

        assert result is True

    @patch("sys.modules", {})
    @patch("os.environ.get")
    def test_is_development_environment_git_repository(
        self,
        mock_env_get: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _is_development_environment returns True when .git exists."""
        mock_env_get.side_effect = lambda key, default=None: (
            "false" if key == "CI" else None
        )

        # Patch .exists() to return True for .git path only
        with patch.object(Path, "exists", return_value=True):
            loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
                bundle_path=mock_bundle_path,
                source_path=None,
                tracer_instance=mock_tracer_instance,
            )

            result: bool = loader._is_development_environment()

        assert result is True

    @patch("sys.modules", {})
    @patch("os.environ.get")
    def test_is_development_environment_production_mode(
        self,
        mock_env_get: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _is_development_environment returns False in production."""
        mock_env_get.side_effect = lambda key, default=None: (
            "true" if key == "CI" else None
        )

        with patch.object(Path, "exists", return_value=False):
            loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
                bundle_path=mock_bundle_path,
                source_path=None,
                tracer_instance=mock_tracer_instance,
            )

            result: bool = loader._is_development_environment()

        assert result is False


# =============================================================================
# TEST CLASS: RECOMPILATION LOGIC
# =============================================================================


class TestRecompilation:
    """Test bundle recompilation logic."""

    @patch("pathlib.Path.exists")
    def test_needs_recompilation_bundle_missing(
        self,
        mock_exists: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _needs_recompilation returns True when bundle doesn't exist."""
        mock_exists.return_value = False

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        result: bool = loader._needs_recompilation()

        assert result is True

    @patch("pathlib.Path.exists")
    def test_needs_recompilation_source_path_none(
        self, mock_exists: Mock, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _needs_recompilation returns False when source_path is None."""
        mock_exists.return_value = True

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=None,
            tracer_instance=mock_tracer_instance,
        )

        result: bool = loader._needs_recompilation()

        assert result is False

    def test_needs_recompilation_source_path_missing(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock, tmp_path: Path
    ) -> None:
        """Test _needs_recompilation returns False when source_path doesn't exist."""
        nonexistent_source: Path = tmp_path / "nonexistent"

        # Create the bundle file so it exists
        mock_bundle_path.touch()

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=nonexistent_source,
            tracer_instance=mock_tracer_instance,
        )

        result: bool = loader._needs_recompilation()

        assert result is False

    def test_needs_recompilation_newer_source_file(
        self, mock_bundle_path: Path, mock_source_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _needs_recompilation returns True when source file is newer."""
        # Create bundle file
        mock_bundle_path.touch()
        bundle_mtime: float = mock_bundle_path.stat().st_mtime

        # Create YAML file with newer timestamp
        yaml_file: Path = mock_source_path / "providers.yaml"
        yaml_file.write_text("test: data")
        # Manually set newer mtime
        os.utime(yaml_file, (bundle_mtime + 100, bundle_mtime + 100))

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        result: bool = loader._needs_recompilation()

        assert result is True

    def test_needs_recompilation_older_source_files(
        self, mock_bundle_path: Path, mock_source_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _needs_recompilation returns False when all source files are older."""
        # Create YAML file first
        yaml_file: Path = mock_source_path / "providers.yaml"
        yaml_file.write_text("test: data")

        # Create bundle file with newer timestamp
        time.sleep(0.01)  # Ensure bundle is newer
        mock_bundle_path.touch()

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        result: bool = loader._needs_recompilation()

        assert result is False

    @patch("subprocess.run")
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._find_compile_script"
    )
    @patch("sys.executable", "/usr/bin/python3")
    def test_recompile_bundle_success(
        self,
        mock_find_script: Mock,
        mock_subprocess_run: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _recompile_bundle successfully recompiles bundle."""
        compile_script: Path = Path("/project/scripts/compile_providers.py")
        mock_find_script.return_value = compile_script
        mock_subprocess_run.return_value = Mock(
            returncode=0, stdout="Success", stderr=""
        )

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        loader._recompile_bundle()

        mock_subprocess_run.assert_called_once_with(
            [
                "/usr/bin/python3",
                str(compile_script),
                "--source-dir",
                str(mock_source_path),
                "--output-dir",
                str(mock_bundle_path.parent),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._find_compile_script"
    )
    def test_recompile_bundle_script_not_found(
        self,
        mock_find_script: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _recompile_bundle raises RuntimeError when script not found."""
        mock_find_script.return_value = None

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        with pytest.raises(RuntimeError) as exc_info:
            loader._recompile_bundle()

        assert "Could not find compile_providers.py script" in str(exc_info.value)

    @patch("subprocess.run")
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._find_compile_script"
    )
    def test_recompile_bundle_subprocess_error(
        self,
        mock_find_script: Mock,
        mock_subprocess_run: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _recompile_bundle raises RuntimeError on subprocess error."""
        compile_script: Path = Path("/project/scripts/compile_providers.py")
        mock_find_script.return_value = compile_script
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            1, "compile", stderr="Compilation failed"
        )

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        with pytest.raises(RuntimeError) as exc_info:
            loader._recompile_bundle()

        assert "Failed to recompile provider bundle" in str(exc_info.value)

    @patch("subprocess.run")
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._find_compile_script"
    )
    def test_recompile_bundle_unexpected_error(
        self,
        mock_find_script: Mock,
        mock_subprocess_run: Mock,
        mock_bundle_path: Path,
        mock_source_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _recompile_bundle raises exception on unexpected error."""
        compile_script: Path = Path("/project/scripts/compile_providers.py")
        mock_find_script.return_value = compile_script
        mock_subprocess_run.side_effect = OSError("Disk full")

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            source_path=mock_source_path,
            tracer_instance=mock_tracer_instance,
        )

        with pytest.raises(OSError):
            loader._recompile_bundle()

    def test_find_compile_script_in_scripts_directory(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock, tmp_path: Path
    ) -> None:
        """Test _find_compile_script finds script in scripts directory."""
        # Create scripts directory with compile script
        scripts_dir: Path = tmp_path / "scripts"
        scripts_dir.mkdir()
        compile_script: Path = scripts_dir / "compile_providers.py"
        compile_script.write_text("# compile script")

        # Mock Path.cwd() to return tmp_path
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
                bundle_path=mock_bundle_path,
                tracer_instance=mock_tracer_instance,
            )

            result: Optional[Path] = loader._find_compile_script()

            assert result == compile_script

    def test_find_compile_script_not_found(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock, tmp_path: Path
    ) -> None:
        """Test _find_compile_script returns None when script not found."""
        # Use a directory with no scripts
        empty_dir: Path = tmp_path / "empty"
        empty_dir.mkdir()

        with patch("pathlib.Path.cwd", return_value=empty_dir):
            with patch.object(Path, "exists", return_value=False):
                loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
                    bundle_path=mock_bundle_path,
                    tracer_instance=mock_tracer_instance,
                )

                result: Optional[Path] = loader._find_compile_script()

                assert result is None


# =============================================================================
# TEST CLASS: EXTRACTION FUNCTIONS
# =============================================================================


class TestExtractionFunctions:
    """Test extraction function compilation and lazy loading."""

    @patch("builtins.compile")
    @patch("builtins.exec")
    def test_compile_single_function_success(
        self,
        mock_exec: Mock,
        mock_compile: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test _compile_single_function successfully compiles a function."""
        mock_compile.return_value = compile(
            "def extract_openai_data(attributes): pass", "<string>", "exec"
        )

        def exec_side_effect(
            code: Any, globals_dict: Dict[str, Any], locals_dict: Dict[str, Any]
        ) -> None:
            locals_dict["extract_openai_data"] = lambda attributes: {
                "provider": "openai"
            }

        mock_exec.side_effect = exec_side_effect

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader._cached_bundle = sample_bundle  # type: ignore[assignment]

        loader._compile_single_function("openai")

        assert "openai" in loader._cached_functions
        assert callable(loader._cached_functions["openai"])

    def test_compile_single_function_no_cached_bundle(
        self,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _compile_single_function loads bundle if not cached."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        # Mock load_provider_bundle to prevent actual loading
        with patch.object(loader, "load_provider_bundle") as mock_load:
            loader._compile_single_function("openai")

            mock_load.assert_called_once()

    @patch("builtins.compile")
    def test_compile_single_function_no_extraction_functions_attr(
        self,
        mock_compile: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _compile_single_function handles bundle without extraction_functions."""
        # Create bundle without extraction_functions attribute
        bundle_without_functions: Mock = Mock(spec=["provider_signatures"])
        bundle_without_functions.provider_signatures = {"openai": []}

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader._cached_bundle = bundle_without_functions  # type: ignore[assignment]

        loader._compile_single_function("openai")

        # Should not attempt compilation
        mock_compile.assert_not_called()
        assert "openai" not in loader._cached_functions

    @patch("builtins.compile")
    def test_compile_single_function_provider_not_found(
        self,
        mock_compile: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test _compile_single_function handles missing provider gracefully."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader._cached_bundle = sample_bundle  # type: ignore[assignment]

        loader._compile_single_function("nonexistent")

        # Should not attempt compilation
        mock_compile.assert_not_called()
        assert "nonexistent" not in loader._cached_functions

    @patch("builtins.compile")
    @patch("builtins.exec")
    def test_compile_single_function_compilation_error(
        self,
        mock_exec: Mock,
        mock_compile: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test _compile_single_function creates fallback on compilation error."""
        mock_compile.side_effect = SyntaxError("Invalid syntax")

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader._cached_bundle = sample_bundle  # type: ignore[assignment]

        loader._compile_single_function("openai")

        # Should create fallback function
        assert "openai" in loader._cached_functions
        assert callable(loader._cached_functions["openai"])

    @patch("builtins.compile")
    @patch("builtins.exec")
    def test_compile_single_function_missing_function_name(
        self,
        mock_exec: Mock,
        mock_compile: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test _compile_single_function creates fallback when function name not found."""
        mock_compile.return_value = compile(
            "def wrong_name(attributes): pass", "<string>", "exec"
        )

        def exec_side_effect(
            code: Any, globals_dict: Dict[str, Any], locals_dict: Dict[str, Any]
        ) -> None:
            locals_dict["wrong_name"] = lambda attributes: {"provider": "openai"}

        mock_exec.side_effect = exec_side_effect

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader._cached_bundle = sample_bundle  # type: ignore[assignment]

        loader._compile_single_function("openai")

        # Should create fallback function
        assert "openai" in loader._cached_functions

    def test_create_fallback_function(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _create_fallback_function creates valid fallback."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        fallback: Callable = loader._create_fallback_function("test_provider")

        assert callable(fallback)

        # Test fallback function execution
        test_attributes: Dict[str, Any] = {"llm.model_name": "gpt-4"}
        result: Dict[str, Any] = fallback(test_attributes)

        assert result["metadata"]["provider"] == "test_provider"
        assert result["metadata"]["extraction_method"] == "fallback"
        assert result["config"]["model"] == "gpt-4"

    def test_create_fallback_function_missing_model_name(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _create_fallback_function handles missing model_name."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        fallback: Callable = loader._create_fallback_function("test_provider")

        test_attributes: Dict[str, Any] = {}
        result: Dict[str, Any] = fallback(test_attributes)

        assert result["config"]["model"] == "unknown"

    def test_get_extraction_function_cached(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test get_extraction_function returns cached function."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        # Pre-cache a function
        cached_func: Callable = lambda x: {"cached": True}
        loader._cached_functions["openai"] = cached_func

        result: Optional[Callable] = loader.get_extraction_function("openai")

        assert result == cached_func

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._compile_single_function"
    )
    def test_get_extraction_function_lazy_compilation(
        self,
        mock_compile: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test get_extraction_function triggers lazy compilation."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        # Set up _compile_single_function to add to cache
        compiled_func: Callable = lambda x: {"compiled": True}

        def compile_side_effect(provider_name: str) -> None:
            loader._cached_functions[provider_name] = compiled_func

        mock_compile.side_effect = compile_side_effect

        result: Optional[Callable] = loader.get_extraction_function("openai")

        mock_compile.assert_called_once_with("openai")
        assert result == compiled_func

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader._compile_single_function"
    )
    def test_get_extraction_function_compilation_failed(
        self,
        mock_compile: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test get_extraction_function returns None when compilation fails."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        # Don't add to cached_functions to simulate compilation failure

        result: Optional[Callable] = loader.get_extraction_function("openai")

        mock_compile.assert_called_once_with("openai")
        assert result is None


# =============================================================================
# TEST CLASS: ACCESSOR METHODS
# =============================================================================


class TestAccessorMethods:
    """Test public accessor methods."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader.load_provider_bundle"
    )
    def test_get_provider_signatures(
        self,
        mock_load_bundle: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test get_provider_signatures returns provider signatures."""
        mock_load_bundle.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader.get_provider_signatures()

        assert result == sample_bundle.provider_signatures
        mock_load_bundle.assert_called_once()

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader.load_provider_bundle"
    )
    def test_get_provider_signatures_missing_attribute(
        self,
        mock_load_bundle: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test get_provider_signatures returns empty dict when attribute missing."""
        bundle_without_sigs: Mock = Mock(spec=[])
        mock_load_bundle.return_value = bundle_without_sigs

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader.get_provider_signatures()

        assert not result

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader.load_provider_bundle"
    )
    def test_get_field_mappings(
        self,
        mock_load_bundle: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test get_field_mappings returns field mappings."""
        mock_load_bundle.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader.get_field_mappings()

        assert result == sample_bundle.field_mappings

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader.load_provider_bundle"
    )
    def test_get_transform_registry(
        self,
        mock_load_bundle: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test get_transform_registry returns transform registry."""
        mock_load_bundle.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader.get_transform_registry()

        assert result == sample_bundle.transform_registry

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader.load_provider_bundle"
    )
    def test_get_validation_rules(
        self,
        mock_load_bundle: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test get_validation_rules returns validation rules."""
        mock_load_bundle.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader.get_validation_rules()

        assert result == sample_bundle.validation_rules

    def test_get_build_metadata_cached_bundle(
        self,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test get_build_metadata uses cached bundle (optimized path)."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader._cached_bundle = sample_bundle  # type: ignore[assignment]

        result: Dict[str, Any] = loader.get_build_metadata()

        assert result == sample_bundle.build_metadata

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader.load_provider_bundle"
    )
    def test_get_build_metadata_no_cached_bundle(
        self,
        mock_load_bundle: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
        sample_bundle: CompiledProviderBundle,
    ) -> None:
        """Test get_build_metadata loads bundle when not cached."""
        mock_load_bundle.return_value = sample_bundle

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader.get_build_metadata()

        assert result == sample_bundle.build_metadata
        mock_load_bundle.assert_called_once()

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.bundle_loader.DevelopmentAwareBundleLoader.load_provider_bundle"
    )
    def test_get_build_metadata_missing_attribute(
        self,
        mock_load_bundle: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test get_build_metadata returns empty dict when attribute missing."""
        bundle_without_metadata: Mock = Mock(spec=[])
        mock_load_bundle.return_value = bundle_without_metadata

        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader._cached_bundle = None  # Force load

        result: Dict[str, Any] = loader.get_build_metadata()

        assert not result

    @patch("builtins.open", new_callable=mock_open, read_data='{"version": "4.0.0"}')
    def test_load_bundle_metadata_success(
        self,
        mock_file_open: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _load_bundle_metadata successfully loads metadata."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader.bundle_metadata_path.touch()  # Create metadata file

        result: Dict[str, Any] = loader._load_bundle_metadata()

        assert result == {"version": "4.0.0"}

    def test_load_bundle_metadata_file_not_found(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _load_bundle_metadata returns empty dict when file missing."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Dict[str, Any] = loader._load_bundle_metadata()

        assert not result

    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    def test_load_bundle_metadata_json_error(
        self,
        mock_file_open: Mock,
        mock_bundle_path: Path,
        mock_tracer_instance: Mock,
    ) -> None:
        """Test _load_bundle_metadata returns empty dict on JSON error."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )
        loader.bundle_metadata_path.touch()

        result: Dict[str, Any] = loader._load_bundle_metadata()

        assert not result


# =============================================================================
# TEST CLASS: TRANSFORM HELPERS
# =============================================================================


class TestTransformHelpers:
    """Test transform helper methods."""

    def test_flatten_array_not_list(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _flatten_array returns value as-is when not a list."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Any = loader._flatten_array("not a list")

        assert result == "not a list"

    def test_flatten_array_flat_list(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _flatten_array handles already flat list."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Any = loader._flatten_array([1, 2, 3])

        assert result == [1, 2, 3]

    def test_flatten_array_nested_list(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _flatten_array flattens nested list."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Any = loader._flatten_array([1, [2, 3], 4])

        assert result == [1, 2, 3, 4]

    def test_flatten_array_deeply_nested(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _flatten_array flattens deeply nested list."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Any = loader._flatten_array([1, [2, [3, [4]]], 5])

        assert result == [1, 2, 3, 4, 5]

    def test_merge_objects_not_list_or_dict(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _merge_objects returns value as-is when not list or dict."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Any = loader._merge_objects("not a list")

        assert result == "not a list"

    def test_merge_objects_dict_input(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _merge_objects returns dict as-is."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        input_dict: Dict[str, Any] = {"key": "value"}
        result: Any = loader._merge_objects(input_dict)

        assert result == input_dict

    def test_merge_objects_list_of_dicts(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _merge_objects merges list of dicts."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        input_list: List[Dict[str, Any]] = [{"a": 1}, {"b": 2}, {"c": 3}]
        result: Any = loader._merge_objects(input_list)

        assert result == {"a": 1, "b": 2, "c": 3}

    def test_merge_objects_mixed_types_in_list(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _merge_objects handles mixed types in list."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        input_list: List[Any] = [{"a": 1}, "not a dict", {"b": 2}]
        result: Any = loader._merge_objects(input_list)

        assert result == {"a": 1, "b": 2}

    def test_apply_transform_extract_user_message_content(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _apply_transform with extract_user_message_content implementation."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {}
        parameters: Dict[str, Any] = {}

        with patch.object(
            loader, "_extract_user_message_content", return_value="user content"
        ) as mock_extract:
            result: Any = loader._apply_transform(
                "extract_user_message_content", attributes, parameters
            )

            assert result == "user content"
            mock_extract.assert_called_once_with(attributes, parameters)

    def test_apply_transform_extract_assistant_message_content(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _apply_transform with extract_assistant_message_content implementation."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {}
        parameters: Dict[str, Any] = {}

        with patch.object(
            loader,
            "_extract_assistant_message_content",
            return_value="assistant content",
        ):
            result: Any = loader._apply_transform(
                "extract_assistant_message_content", attributes, parameters
            )

            assert result == "assistant content"

    def test_apply_transform_sum_fields(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _apply_transform with sum_fields implementation."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {}
        parameters: Dict[str, Any] = {}

        with patch.object(loader, "_sum_fields", return_value=42):
            result: Any = loader._apply_transform("sum_fields", attributes, parameters)

            assert result == 42

    def test_apply_transform_detect_instrumentor_framework(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _apply_transform with detect_instrumentor_framework implementation."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {}
        parameters: Dict[str, Any] = {}

        with patch.object(
            loader, "_detect_instrumentor_framework", return_value="openai"
        ):
            result: Any = loader._apply_transform(
                "detect_instrumentor_framework", attributes, parameters
            )

            assert result == "openai"

    def test_apply_transform_unknown_implementation(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _apply_transform returns None for unknown implementation."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        result: Any = loader._apply_transform("unknown_transform", {}, {})

        assert result is None

    def test_extract_user_message_content_single_message(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _extract_user_message_content with single user message."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {
            "llm.input_messages": [{"role": "user", "content": "Hello"}]
        }
        parameters: Dict[str, Any] = {}

        result: str = loader._extract_user_message_content(attributes, parameters)

        assert result == "Hello"

    def test_extract_user_message_content_multiple_messages(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _extract_user_message_content with multiple user messages."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {
            "llm.input_messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
                {"role": "user", "content": "How are you?"},
            ]
        }
        parameters: Dict[str, Any] = {}

        result: str = loader._extract_user_message_content(attributes, parameters)

        assert result == "Hello\n\nHow are you?"

    def test_extract_user_message_content_no_match(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _extract_user_message_content with no matching messages."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {
            "llm.input_messages": [{"role": "assistant", "content": "Hello"}]
        }
        parameters: Dict[str, Any] = {}

        result: str = loader._extract_user_message_content(attributes, parameters)

        assert result == ""

    def test_extract_user_message_content_empty_messages(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _extract_user_message_content with empty messages list."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {}
        parameters: Dict[str, Any] = {}

        result: str = loader._extract_user_message_content(attributes, parameters)

        assert result == ""

    def test_extract_assistant_message_content_single_message(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _extract_assistant_message_content with single assistant message."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {
            "llm.output_messages": [{"role": "assistant", "content": "Hello"}]
        }
        parameters: Dict[str, Any] = {}

        result: str = loader._extract_assistant_message_content(attributes, parameters)

        assert result == "Hello"

    def test_extract_assistant_message_content_multiple_messages(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _extract_assistant_message_content with multiple assistant messages."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {
            "llm.output_messages": [
                {"role": "assistant", "content": "Hello"},
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "How can I help?"},
            ]
        }
        parameters: Dict[str, Any] = {}

        result: str = loader._extract_assistant_message_content(attributes, parameters)

        assert result == "Hello\nHow can I help?"

    def test_extract_assistant_message_content_no_match(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _extract_assistant_message_content with no matching messages."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {
            "llm.output_messages": [{"role": "user", "content": "Hello"}]
        }
        parameters: Dict[str, Any] = {}

        result: str = loader._extract_assistant_message_content(attributes, parameters)

        assert result == ""

    def test_extract_assistant_message_content_empty_messages(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _extract_assistant_message_content with empty messages list."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {}
        parameters: Dict[str, Any] = {}

        result: str = loader._extract_assistant_message_content(attributes, parameters)

        assert result == ""

    def test_sum_fields_with_values(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _sum_fields with numeric values."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {"field1": 10, "field2": 20, "field3": 30}
        parameters: Dict[str, Any] = {"source_fields": ["field1", "field2", "field3"]}

        result: int = loader._sum_fields(attributes, parameters)

        assert result == 60

    def test_sum_fields_no_values(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _sum_fields with no matching fields."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {}
        parameters: Dict[str, Any] = {
            "source_fields": ["field1", "field2"],
            "fallback_value": 100,
        }

        result: int = loader._sum_fields(attributes, parameters)

        assert result == 100

    def test_sum_fields_fallback_used(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _sum_fields uses fallback when sum is zero."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {"field1": 0, "field2": 0}
        parameters: Dict[str, Any] = {
            "source_fields": ["field1", "field2"],
            "fallback_value": 50,
        }

        result: int = loader._sum_fields(attributes, parameters)

        assert result == 50

    def test_detect_instrumentor_framework_match_found(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _detect_instrumentor_framework finds matching instrumentor."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {
            "gen_ai.system": "openai",
            "gen_ai.request.model": "gpt-4",
            "llm.usage.total_tokens": 100,
        }
        parameters: Dict[str, Any] = {
            "attribute_patterns": {
                "openai": ["gen_ai.system", "gen_ai.request.model"],
                "anthropic": ["gen_ai.system", "llm.provider"],
            }
        }

        result: str = loader._detect_instrumentor_framework(attributes, parameters)

        assert result == "openai"

    def test_detect_instrumentor_framework_no_match(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _detect_instrumentor_framework returns unknown when no match."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {"some_field": "value"}
        parameters: Dict[str, Any] = {
            "attribute_patterns": {"openai": ["gen_ai.system", "gen_ai.request.model"]}
        }

        result: str = loader._detect_instrumentor_framework(attributes, parameters)

        assert result == "unknown"

    def test_detect_instrumentor_framework_empty_patterns(
        self, mock_bundle_path: Path, mock_tracer_instance: Mock
    ) -> None:
        """Test _detect_instrumentor_framework handles empty patterns."""
        loader: DevelopmentAwareBundleLoader = DevelopmentAwareBundleLoader(
            bundle_path=mock_bundle_path,
            tracer_instance=mock_tracer_instance,
        )

        attributes: Dict[str, Any] = {"gen_ai.system": "openai"}
        parameters: Dict[str, Any] = {"attribute_patterns": {}}

        result: str = loader._detect_instrumentor_framework(attributes, parameters)

        assert result == "unknown"

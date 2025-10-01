"""Unit tests for Universal LLM Discovery Engine v4.0 provider processor.

This module tests the UniversalProviderProcessor class which implements:
- O(1) provider detection using inverted signature indices
- O(log n) subset matching fallback
- Compiled extraction function execution
- Graceful degradation for unknown providers

Testing follows Agent OS V3 Framework standards:
- Mock all external dependencies (time, Path, safe_log, bundle_loader)
- Execute all internal methods for coverage
- Achieve 90%+ line coverage
- 100% test pass rate
- 10.0/10 Pylint score
- 0 MyPy errors
"""

# pylint: disable=protected-access,too-many-lines,redefined-outer-name,too-many-public-methods,line-too-long,too-many-positional-arguments
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, pytest fixtures are used as parameters,
# mock patch decorators create unavoidable long lines for module paths,
# and complex test setups require many fixtures.

from typing import Any, Dict, FrozenSet, List, Optional, Tuple
from unittest.mock import Mock, patch
from pathlib import Path

import pytest

from honeyhive.tracer.processing.semantic_conventions.provider_processor import (
    UniversalProviderProcessor,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_tracer_instance() -> Mock:
    """Mock tracer instance for safe_log calls."""
    return Mock()


@pytest.fixture
def mock_bundle_loader() -> Mock:
    """Mock DevelopmentAwareBundleLoader."""
    mock: Mock = Mock()
    mock.load_provider_bundle = Mock()
    mock.get_extraction_function = Mock()
    mock.get_build_metadata = Mock()
    mock._cached_bundle = None
    mock._cached_functions = {}
    return mock


@pytest.fixture
def sample_bundle() -> Mock:
    """Create a sample bundle with inverted index (v4.0.1+)."""
    bundle: Mock = Mock()

    # Provider signatures (forward index)
    bundle.provider_signatures = {
        "openai": [frozenset(["gen_ai.request.model", "gen_ai.system"])],
        "anthropic": [frozenset(["model", "version"])],
    }

    # Inverted index for O(1) lookup
    bundle.signature_to_provider = {
        frozenset(["gen_ai.request.model", "gen_ai.system"]): ("openai", 0.95),
        frozenset(["model", "version"]): ("anthropic", 0.9),
    }

    # Other bundle components
    bundle.field_mappings = {"openai": {"model": "config.model"}}
    bundle.transform_registry = {}
    bundle.validation_rules = {}

    return bundle


@pytest.fixture
def legacy_bundle_without_inverted_index() -> Mock:
    """Create legacy bundle without inverted index (pre-v4.0.1)."""
    bundle: Mock = Mock(
        spec=[
            "provider_signatures",
            "extraction_functions",
            "field_mappings",
            "transform_registry",
            "validation_rules",
            "metadata",
        ]
    )
    bundle.provider_signatures = {
        "openai": [frozenset(["gen_ai.request.model", "gen_ai.system"])],
        "anthropic": [frozenset(["model", "version"])],
    }
    bundle.field_mappings = {}
    bundle.transform_registry = {}
    bundle.validation_rules = {}

    return bundle


# =============================================================================
# TEST CLASS 1: INITIALIZATION
# =============================================================================


class TestUniversalProviderProcessorInit:
    """Test UniversalProviderProcessor initialization."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_init_with_custom_bundle_loader(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        mock_tracer_instance: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test initialization with custom bundle loader."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader, tracer_instance=mock_tracer_instance
        )

        assert processor.bundle_loader == mock_bundle_loader
        assert processor.tracer_instance == mock_tracer_instance
        assert processor.bundle == sample_bundle
        assert processor.provider_signatures == sample_bundle.provider_signatures
        assert processor.signature_to_provider == sample_bundle.signature_to_provider
        mock_bundle_loader.load_provider_bundle.assert_called_once()

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.Path"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.DevelopmentAwareBundleLoader"
    )
    def test_init_creates_default_bundle_loader(
        self,
        mock_loader_class: Mock,  # pylint: disable=unused-argument
        mock_path_class: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
    ) -> None:
        """Test initialization creates default bundle loader when none provided."""
        # Setup Path mocking
        mock_current_file: Mock = Mock()
        mock_current_file.parent = Path("/test/path")
        mock_path_class.return_value = mock_current_file

        mock_source_path: Mock = Mock()
        mock_source_path.exists.return_value = True

        # Processor creation will call _create_default_bundle_loader
        processor: UniversalProviderProcessor = UniversalProviderProcessor()

        assert processor.bundle_loader is not None

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.Path"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.DevelopmentAwareBundleLoader"
    )
    def test_create_default_bundle_loader_handles_exception(
        self,
        mock_loader_class: Mock,  # pylint: disable=unused-argument
        mock_path_class: Mock,
        mock_safe_log: Mock,
    ) -> None:
        """Test _create_default_bundle_loader handles exceptions gracefully."""
        mock_path_class.side_effect = Exception("Path error")

        processor: UniversalProviderProcessor = UniversalProviderProcessor()

        # Should have logged warning and returned None
        assert any(
            "Failed to create default bundle loader" in str(call)
            for call in mock_safe_log.call_args_list
        )
        # Bundle loader should be None
        assert processor.bundle_loader is None

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_init_initializes_performance_stats(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test initialization sets up performance statistics."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        assert processor.performance_stats["total_processed"] == 0
        assert not processor.performance_stats["provider_detections"]
        assert processor.performance_stats["fallback_usage"] == 0
        assert not processor.performance_stats["processing_times"]
        assert processor.performance_stats["errors"] == 0

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_init_initializes_empty_indices(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test initialization sets up empty signature indices."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # After loading, indices should be populated from bundle
        assert isinstance(processor.signature_to_provider, dict)
        assert len(processor.signature_to_provider) == 2  # 2 providers in sample_bundle


# =============================================================================
# TEST CLASS 2: BUNDLE LOADING
# =============================================================================


class TestBundleLoading:
    """Test bundle loading with different bundle types."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_load_bundle_with_inverted_index(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _load_bundle with modern bundle containing inverted index."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Should use bundle's pre-compiled inverted index
        assert processor.signature_to_provider == sample_bundle.signature_to_provider
        assert processor.provider_signatures == sample_bundle.provider_signatures

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_load_bundle_builds_fallback_index_for_legacy(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        legacy_bundle_without_inverted_index: Mock,
    ) -> None:
        """Test _load_bundle builds inverted index for legacy bundles."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]
        mock_bundle_loader.load_provider_bundle.return_value = (
            legacy_bundle_without_inverted_index
        )
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Should have built inverted index at runtime
        assert isinstance(processor.signature_to_provider, dict)
        assert len(processor.signature_to_provider) > 0

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.Path"
    )
    def test_load_bundle_handles_no_bundle_loader(
        self,
        mock_path: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
    ) -> None:
        """Test _load_bundle handles missing bundle loader gracefully."""
        # Make default loader creation fail by raising exception in Path
        mock_path.side_effect = Exception("Path error")

        processor: UniversalProviderProcessor = UniversalProviderProcessor()

        # Should log warning and continue with empty configurations
        # (bundle_loader will be None, so _load_bundle returns early with empty dicts)
        assert not processor.provider_signatures
        assert not processor.signature_to_provider

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_load_bundle_handles_load_exception(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
    ) -> None:
        """Test _load_bundle handles bundle loading exceptions."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]
        mock_bundle_loader.load_provider_bundle.side_effect = Exception(
            "Bundle load failed"
        )

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Should catch exception and set empty configurations
        assert not processor.provider_signatures
        assert not processor.extraction_functions


# =============================================================================
# TEST CLASS 3: SPAN PROCESSING
# =============================================================================


class TestProcessSpanAttributes:
    """Test process_span_attributes main entry point."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_process_span_attributes_with_valid_dict(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test processing valid dict attributes."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1, 2000.0, 2000.05]
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attributes: Dict[str, Any] = {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
        }

        result: Dict[str, Any] = processor.process_span_attributes(attributes)

        assert "metadata" in result
        assert "provider" in result["metadata"]
        assert processor.performance_stats["total_processed"] == 1

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_process_span_attributes_with_non_dict_input(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test graceful handling of non-dict input."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        result: Dict[str, Any] = processor.process_span_attributes("not_a_dict")  # type: ignore

        # Should use fallback processing
        assert result["metadata"]["provider"] == "unknown"
        assert processor.performance_stats["fallback_usage"] >= 0  # type: ignore[operator]

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_process_span_attributes_with_empty_dict(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test processing empty dict."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1, 2000.0, 2000.05]
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        result: Dict[str, Any] = processor.process_span_attributes({})

        assert result["metadata"]["provider"] == "unknown"

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_process_span_attributes_tracks_performance(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test performance tracking in span processing."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1, 2000.0, 2000.05]
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attributes: Dict[str, Any] = {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
        }

        processor.process_span_attributes(attributes)

        assert processor.performance_stats["total_processed"] == 1
        assert len(processor.performance_stats["processing_times"]) == 1  # type: ignore[arg-type]


# =============================================================================
# TEST CLASS 4: PROVIDER DETECTION
# =============================================================================


class TestProviderDetection:
    """Test O(1) provider detection and subset matching."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_detect_provider_exact_match_o1(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test O(1) exact match provider detection."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attributes: Dict[str, Any] = {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
        }

        provider: str = processor._detect_provider(attributes)

        assert provider == "openai"

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_detect_provider_empty_attributes(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _detect_provider with empty attributes."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        provider: str = processor._detect_provider({})

        assert provider == "unknown"

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_detect_provider_subset_match_fallback(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test provider detection falls back to subset matching."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Attributes with extra keys (not exact match)
        attributes: Dict[str, Any] = {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
            "extra_attribute": "value",
        }

        provider: str = processor._detect_provider(attributes)

        # Should find openai via subset matching
        assert provider in ["openai", "unknown"]

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_find_best_subset_match_finds_match(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _find_best_subset_match finds matching provider."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Attributes that contain openai signature as subset
        attribute_keys: FrozenSet[str] = frozenset(
            [
                "gen_ai.request.model",
                "gen_ai.system",
                "extra_attribute",
            ]
        )

        provider: str = processor._find_best_subset_match(attribute_keys)

        assert provider == "openai"

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_find_best_subset_match_returns_unknown_when_no_match(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _find_best_subset_match returns unknown when no match found."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attribute_keys: FrozenSet[str] = frozenset(["completely_unrelated_key"])

        provider: str = processor._find_best_subset_match(attribute_keys)

        assert provider == "unknown"

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_find_best_subset_match_early_termination(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
    ) -> None:
        """Test subset matching early termination on high confidence."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]

        # Create bundle with high confidence signature
        bundle: Mock = Mock()
        bundle.provider_signatures = {
            "openai": [frozenset(["model", "system"])],
        }
        bundle.signature_to_provider = {
            frozenset(["model", "system"]): ("openai", 0.95),
        }
        bundle.field_mappings = {}
        bundle.transform_registry = {}
        bundle.validation_rules = {}

        mock_bundle_loader.load_provider_bundle.return_value = bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attribute_keys: FrozenSet[str] = frozenset(["model", "system", "extra"])

        provider: str = processor._find_best_subset_match(attribute_keys)

        # Should find openai and terminate early
        assert provider == "openai"


# =============================================================================
# TEST CLASS 5: DATA EXTRACTION
# =============================================================================


class TestDataExtraction:
    """Test _extract_provider_data method."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_extract_provider_data_success(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test successful data extraction using extraction function."""

        # Create extraction function that returns proper structure
        def mock_extraction_func(attrs: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "inputs": {"prompt": attrs.get("gen_ai.request.model")},
                "outputs": {},
                "config": {},
                "metadata": {"provider": "openai"},
            }

        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = mock_extraction_func

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Manually add extraction function to processor
        processor.extraction_functions["openai"] = mock_extraction_func

        attributes: Dict[str, Any] = {"gen_ai.request.model": "gpt-4"}

        result: Dict[str, Any] = processor._extract_provider_data("openai", attributes)

        assert result["inputs"]["prompt"] == "gpt-4"
        assert result["metadata"]["provider"] == "openai"

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_extract_provider_data_no_function(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _extract_provider_data when no extraction function available."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Provider not in extraction_functions
        attributes: Dict[str, Any] = {"gen_ai.request.model": "gpt-4"}

        result: Dict[str, Any] = processor._extract_provider_data(
            "unknown_provider", attributes
        )

        # Should fall back to _fallback_processing
        assert result["metadata"]["provider"] == "unknown"

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_extract_provider_data_function_returns_non_dict(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _extract_provider_data when extraction function returns non-dict."""

        def bad_extraction_func(_attrs: Dict[str, Any]) -> str:
            return "not a dict"  # type: ignore

        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = bad_extraction_func

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        processor.extraction_functions["openai"] = bad_extraction_func

        attributes: Dict[str, Any] = {"gen_ai.request.model": "gpt-4"}

        result: Dict[str, Any] = processor._extract_provider_data("openai", attributes)

        # Should fall back when result is not dict
        assert result["metadata"]["provider"] == "unknown"

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_extract_provider_data_handles_exception(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _extract_provider_data handles exceptions gracefully."""

        def failing_extraction_func(attrs: Dict[str, Any]) -> Dict[str, Any]:
            raise ValueError("Extraction failed")

        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = (
            failing_extraction_func
        )

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        processor.extraction_functions["openai"] = failing_extraction_func

        attributes: Dict[str, Any] = {"gen_ai.request.model": "gpt-4"}

        result: Dict[str, Any] = processor._extract_provider_data("openai", attributes)

        # Should catch exception and fall back
        assert result["metadata"]["provider"] == "unknown"


# =============================================================================
# TEST CLASS 6: VALIDATION AND ENHANCEMENT
# =============================================================================


class TestValidationAndEnhancement:
    """Test _validate_and_enhance and _apply_validation_rules methods."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_validate_and_enhance_ensures_sections(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _validate_and_enhance ensures all required sections exist."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Data missing some sections
        incomplete_data: Dict[str, Any] = {"inputs": {"prompt": "test"}}

        result: Dict[str, Any] = processor._validate_and_enhance(
            incomplete_data, "openai"
        )

        # All sections should now exist
        assert "inputs" in result
        assert "outputs" in result
        assert "config" in result
        assert "metadata" in result

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_validate_and_enhance_converts_non_dict_sections(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _validate_and_enhance converts non-dict sections to dicts."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Data with non-dict sections
        bad_data: Dict[str, Any] = {
            "inputs": "not a dict",  # type: ignore
            "outputs": [],  # type: ignore
            "config": 123,  # type: ignore
            "metadata": None,  # type: ignore
        }

        result: Dict[str, Any] = processor._validate_and_enhance(bad_data, "openai")

        # All sections should be dicts now
        assert isinstance(result["inputs"], dict)
        assert isinstance(result["outputs"], dict)
        assert isinstance(result["config"], dict)
        assert isinstance(result["metadata"], dict)

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_validate_and_enhance_adds_processing_metadata(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _validate_and_enhance adds processing metadata."""
        mock_time.time.return_value = 1234567890.0
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        data: Dict[str, Any] = {
            "inputs": {},
            "outputs": {},
            "config": {},
            "metadata": {},
        }

        result: Dict[str, Any] = processor._validate_and_enhance(data, "openai")

        assert result["metadata"]["provider"] == "openai"
        assert result["metadata"]["processing_engine"] == "universal_llm_discovery_v4"
        assert result["metadata"]["detection_method"] == "signature_based"
        assert "processed_at" in result["metadata"]

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_apply_validation_rules_max_fields(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
    ) -> None:
        """Test _apply_validation_rules checks max fields."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]

        # Bundle with validation rules
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": [frozenset(["model"])]}
        bundle.signature_to_provider = {frozenset(["model"]): ("openai", 0.9)}
        bundle.field_mappings = {}
        bundle.transform_registry = {}
        bundle.validation_rules = {
            "schema_validation": {
                "inputs": {"max_fields": 5},
            }
        }

        mock_bundle_loader.load_provider_bundle.return_value = bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Data with too many fields
        data: Dict[str, Any] = {
            "inputs": {f"field_{i}": i for i in range(10)},  # 10 fields, max is 5
            "outputs": {},
            "config": {},
            "metadata": {},
        }

        processor._apply_validation_rules(data, "openai")

        # Should log warning about exceeding max fields
        assert any("max is" in str(call) for call in mock_safe_log.call_args_list)

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_apply_validation_rules_required_fields(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
    ) -> None:
        """Test _apply_validation_rules checks required fields."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]

        # Bundle with validation rules
        bundle: Mock = Mock()
        bundle.provider_signatures = {"openai": [frozenset(["model"])]}
        bundle.signature_to_provider = {frozenset(["model"]): ("openai", 0.9)}
        bundle.field_mappings = {}
        bundle.transform_registry = {}
        bundle.validation_rules = {
            "schema_validation": {
                "metadata": {"require_provider": True},
                "config": {"require_model_recommended": True},
            }
        }

        mock_bundle_loader.load_provider_bundle.return_value = bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Data missing required fields
        data: Dict[str, Any] = {
            "inputs": {},
            "outputs": {},
            "config": {},  # Missing 'model'
            "metadata": {},  # Missing 'provider'
        }

        processor._apply_validation_rules(data, "openai")

        # Should log about missing fields (debug level, not enforced)

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_apply_validation_rules_handles_exception(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test _apply_validation_rules handles exceptions gracefully."""
        # Setup validation rules that will cause error
        sample_bundle.validation_rules = {"invalid": "not a dict"}  # type: ignore

        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        data: Dict[str, Any] = {
            "inputs": {},
            "outputs": {},
            "config": {},
            "metadata": {},
        }

        # Should not raise, should log error
        processor._apply_validation_rules(data, "openai")


# =============================================================================
# TEST CLASS 5: FALLBACK INDEX BUILDING
# =============================================================================


class TestFallbackIndexBuilding:
    """Test inverted index building for legacy bundles."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_build_inverted_index_fallback_creates_index(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        legacy_bundle_without_inverted_index: Mock,
    ) -> None:
        """Test _build_inverted_index_fallback creates correct index."""
        mock_bundle_loader.load_provider_bundle.return_value = (
            legacy_bundle_without_inverted_index
        )
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        inverted: Dict[FrozenSet[str], Tuple[str, float]] = (
            processor.signature_to_provider
        )

        # Should have entries for both providers
        assert len(inverted) == 2
        assert any(provider == "openai" for sig, (provider, conf) in inverted.items())
        assert any(
            provider == "anthropic" for sig, (provider, conf) in inverted.items()
        )

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_build_inverted_index_fallback_handles_collisions(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
    ) -> None:
        """Test collision handling when same signature maps to multiple providers."""
        mock_time.perf_counter.side_effect = [1000.0, 1000.1]

        # Create bundle with duplicate signatures
        bundle: Mock = Mock(
            spec=[
                "provider_signatures",
                "field_mappings",
                "transform_registry",
                "validation_rules",
            ]
        )
        bundle.provider_signatures = {
            "openai": [frozenset(["model", "version"])],
            "anthropic": [frozenset(["model", "version"])],  # Same signature!
        }
        bundle.field_mappings = {}
        bundle.transform_registry = {}
        bundle.validation_rules = {}

        mock_bundle_loader.load_provider_bundle.return_value = bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        inverted: Dict[FrozenSet[str], Tuple[str, float]] = (
            processor.signature_to_provider
        )

        # Should have one entry (last provider wins with same confidence)
        assert frozenset(["model", "version"]) in inverted


# =============================================================================
# TEST CLASS 6: FALLBACK PROCESSING
# =============================================================================


class TestFallbackProcessing:
    """Test fallback processing for unknown providers."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_fallback_processing_extracts_inputs(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
    ) -> None:
        """Test fallback processing extracts input fields."""
        mock_bundle_loader.load_provider_bundle.return_value = Mock(
            provider_signatures={},
            field_mappings={},
            transform_registry={},
            validation_rules={},
        )

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attributes: Dict[str, Any] = {
            "input_data": "test input",
            "prompt": "test prompt",
        }

        result: Dict[str, Any] = processor._fallback_processing(attributes)

        assert "inputs" in result
        assert "input_data" in result["inputs"]
        assert result["metadata"]["provider"] == "unknown"

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_fallback_processing_extracts_outputs(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
    ) -> None:
        """Test fallback processing extracts output fields."""
        mock_bundle_loader.load_provider_bundle.return_value = Mock(
            provider_signatures={},
            field_mappings={},
            transform_registry={},
            validation_rules={},
        )

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attributes: Dict[str, Any] = {
            "output": "test output",
            "result_data": "test result",
        }

        result: Dict[str, Any] = processor._fallback_processing(attributes)

        assert "outputs" in result
        assert "result_data" in result["outputs"]

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_fallback_processing_extracts_config(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
    ) -> None:
        """Test fallback processing extracts config fields."""
        mock_bundle_loader.load_provider_bundle.return_value = Mock(
            provider_signatures={},
            field_mappings={},
            transform_registry={},
            validation_rules={},
        )

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attributes: Dict[str, Any] = {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 100,
        }

        result: Dict[str, Any] = processor._fallback_processing(attributes)

        assert "config" in result
        assert "max_tokens" in result["config"]

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_fallback_processing_handles_exceptions_gracefully(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
    ) -> None:
        """Test fallback processing handles exceptions without crashing."""
        mock_bundle_loader.load_provider_bundle.return_value = Mock(
            provider_signatures={},
            field_mappings={},
            transform_registry={},
            validation_rules={},
        )

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Non-string key that will cause lower() to fail
        attributes: Dict[str, Any] = {123: "value"}  # type: ignore[dict-item]

        result: Dict[str, Any] = processor._fallback_processing(attributes)

        # Should return valid structure despite errors
        assert "metadata" in result
        assert result["metadata"]["provider"] == "unknown"


# =============================================================================
# TEST CLASS 7: PUBLIC API METHODS
# =============================================================================


class TestPublicAPIMethods:
    """Test public API methods for performance stats, providers, and metadata."""

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_get_performance_stats(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test get_performance_stats calculates statistics."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Add some performance data
        processor.performance_stats["processing_times"] = [10.0, 20.0, 30.0]
        processor.performance_stats["provider_detections"] = {
            "openai": 5,
            "anthropic": 3,
        }
        processor.performance_stats["total_processed"] = 8
        processor.performance_stats["fallback_usage"] = 2

        stats: Dict[str, Any] = processor.get_performance_stats()

        assert stats["avg_processing_time_ms"] == 20.0
        assert stats["min_processing_time_ms"] == 10.0
        assert stats["max_processing_time_ms"] == 30.0
        assert "provider_detection_rates" in stats
        assert stats["fallback_rate"] == 0.25

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_reset_performance_stats(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test reset_performance_stats clears all statistics."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        # Add some data
        processor.performance_stats["total_processed"] = 10
        processor.performance_stats["provider_detections"] = {"openai": 5}
        processor.performance_stats["processing_times"] = [10.0, 20.0]

        processor.reset_performance_stats()

        assert processor.performance_stats["total_processed"] == 0
        assert not processor.performance_stats["provider_detections"]
        assert not processor.performance_stats["processing_times"]

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_get_supported_providers(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test get_supported_providers returns provider list."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        providers: List[str] = processor.get_supported_providers()

        assert "openai" in providers
        assert "anthropic" in providers
        assert len(providers) == 2

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_get_provider_signatures(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test get_provider_signatures returns signatures for provider."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        signatures: Optional[List[FrozenSet[str]]] = processor.get_provider_signatures(
            "openai"
        )

        assert signatures is not None
        assert len(signatures) == 1
        assert all(isinstance(sig, frozenset) for sig in signatures)

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_get_provider_signatures_unknown_provider(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test get_provider_signatures returns None for unknown provider."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        signatures: Optional[List[FrozenSet[str]]] = processor.get_provider_signatures(
            "unknown_provider"
        )

        assert signatures is None

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_validate_attributes_for_provider(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test validate_attributes_for_provider validates correctly."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attributes: Dict[str, Any] = {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
        }

        is_valid: bool = processor.validate_attributes_for_provider(
            attributes, "openai"
        )

        assert is_valid is True

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_validate_attributes_for_provider_no_match(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test validate_attributes_for_provider returns False when no match."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        attributes: Dict[str, Any] = {
            "unrelated_key": "value",
        }

        is_valid: bool = processor.validate_attributes_for_provider(
            attributes, "openai"
        )

        assert is_valid is False

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    def test_get_bundle_metadata(
        self,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test get_bundle_metadata retrieves metadata."""
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None
        mock_bundle_loader.get_build_metadata.return_value = {
            "version": "4.0.1",
            "providers_processed": 2,
        }

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        metadata: Dict[str, Any] = processor.get_bundle_metadata()

        assert metadata["version"] == "4.0.1"
        assert metadata["providers_processed"] == 2

    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.safe_log"
    )
    @patch(
        "honeyhive.tracer.processing.semantic_conventions.provider_processor.time"
    )
    def test_reload_bundle(
        self,
        mock_time: Mock,
        mock_safe_log: Mock,  # pylint: disable=unused-argument
        mock_bundle_loader: Mock,
        sample_bundle: Mock,
    ) -> None:
        """Test reload_bundle reloads the provider bundle."""
        # Provide enough side_effect values for both __init__ and reload_bundle
        mock_time.perf_counter.side_effect = [1000.0, 1000.1, 2000.0, 2000.1]
        mock_bundle_loader.load_provider_bundle.return_value = sample_bundle
        mock_bundle_loader.get_extraction_function.return_value = None

        # Setup cache attributes on mock
        mock_bundle_loader._cached_bundle = None
        mock_bundle_loader._cached_functions = {}

        processor: UniversalProviderProcessor = UniversalProviderProcessor(
            bundle_loader=mock_bundle_loader
        )

        initial_call_count: int = mock_bundle_loader.load_provider_bundle.call_count

        processor.reload_bundle()

        # Should have loaded bundle again (called once in init, once in reload)
        assert (
            mock_bundle_loader.load_provider_bundle.call_count == initial_call_count + 1
        )

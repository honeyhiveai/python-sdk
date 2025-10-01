# pylint: disable=protected-access,redefined-outer-name,too-many-public-methods
# Justification: Testing requires access to protected methods, comprehensive
# coverage requires extensive test cases, and pytest fixtures are used as parameters.
"""
Unit tests for config.dsl.validation.performance_benchmarks module.

Tests performance benchmark validation including:
- Bundle loading benchmarks
- Exact match detection benchmarks
- Subset match detection benchmarks
- Metadata access benchmarks
- Regression detection workflow
- CLI entry point behavior
"""

from pathlib import Path
from unittest.mock import Mock, patch

from config.dsl.validation.performance_benchmarks import (
    benchmark_bundle_loading,
    benchmark_exact_match_detection,
    benchmark_subset_match_detection,
    benchmark_metadata_access,
    run_performance_checks,
    check_performance_regression,
    main,
)


class TestBenchmarkBundleLoading:
    """Test benchmark_bundle_loading() function."""

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    @patch("config.dsl.validation.performance_benchmarks.DevelopmentAwareBundleLoader")
    @patch("pathlib.Path.exists")
    def test_pass_within_baseline(
        self,
        mock_exists: Mock,
        _mock_loader_class: Mock,
        mock_perf_counter: Mock,
        mock_mean: Mock,
    ) -> None:
        """Test benchmark passing when within baseline."""
        mock_exists.return_value = True
        mock_perf_counter.side_effect = [
            1.0,
            1.003,
            2.0,
            2.003,
            3.0,
            3.003,
            4.0,
            4.003,
            5.0,
            5.003,
        ]
        mock_mean.return_value = 3.0  # Within 5ms baseline

        avg_time, status = benchmark_bundle_loading(Path("test.pkl"))

        assert avg_time == 3.0
        assert "PASS" in status
        assert "3.00ms" in status

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    @patch("config.dsl.validation.performance_benchmarks.DevelopmentAwareBundleLoader")
    @patch("pathlib.Path.exists")
    def test_warn_above_baseline_within_threshold(
        self,
        mock_exists: Mock,
        _mock_loader_class: Mock,
        mock_perf_counter: Mock,
        mock_mean: Mock,
    ) -> None:
        """Test benchmark warning when above baseline but within threshold."""
        mock_exists.return_value = True
        mock_perf_counter.side_effect = [
            1.0,
            1.005,
            2.0,
            2.005,
            3.0,
            3.005,
            4.0,
            4.005,
            5.0,
            5.005,
        ]
        mock_mean.return_value = 5.5  # Above 5ms but within 20% threshold

        avg_time, status = benchmark_bundle_loading(Path("test.pkl"))

        assert avg_time == 5.5
        assert "WARN" in status

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    @patch("config.dsl.validation.performance_benchmarks.DevelopmentAwareBundleLoader")
    @patch("pathlib.Path.exists")
    def test_fail_exceeds_threshold(
        self,
        mock_exists: Mock,
        _mock_loader_class: Mock,
        mock_perf_counter: Mock,
        mock_mean: Mock,
    ) -> None:
        """Test benchmark failure when exceeding threshold."""
        mock_exists.return_value = True
        mock_perf_counter.side_effect = [
            1.0,
            1.01,
            2.0,
            2.01,
            3.0,
            3.01,
            4.0,
            4.01,
            5.0,
            5.01,
        ]
        mock_mean.return_value = 10.0  # Exceeds 5ms * 1.20 threshold

        avg_time, status = benchmark_bundle_loading(Path("test.pkl"))

        assert avg_time == 10.0
        assert "FAIL" in status

    def test_bundle_file_not_found(self) -> None:
        """Test handling when bundle file not found."""
        with patch("pathlib.Path.exists", return_value=False):
            avg_time, status = benchmark_bundle_loading(Path("nonexistent.pkl"))

            assert avg_time == 0.0
            assert "not found" in status

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    @patch("config.dsl.validation.performance_benchmarks.DevelopmentAwareBundleLoader")
    @patch("pathlib.Path.exists")
    def test_custom_bundle_path(
        self,
        mock_exists: Mock,
        _mock_loader_class: Mock,
        mock_perf_counter: Mock,
        mock_mean: Mock,
    ) -> None:
        """Test benchmark with custom bundle path."""
        mock_exists.return_value = True
        mock_perf_counter.side_effect = [
            1.0,
            1.002,
            2.0,
            2.002,
            3.0,
            3.002,
            4.0,
            4.002,
            5.0,
            5.002,
        ]
        mock_mean.return_value = 2.5

        custom_path: Path = Path("/custom/path/bundle.pkl")
        avg_time, status = benchmark_bundle_loading(custom_path)

        assert avg_time == 2.5
        assert "PASS" in status


class TestBenchmarkExactMatchDetection:
    """Test benchmark_exact_match_detection() function."""

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_pass_within_baseline(
        self, mock_perf_counter: Mock, mock_mean: Mock
    ) -> None:
        """Test exact match benchmark passing."""
        # Warm-up calls (5) + actual benchmark calls (100)
        mock_perf_counter.side_effect = [1.0] * 210  # 105 pairs
        mock_mean.return_value = 0.05  # Within 0.1ms baseline

        mock_processor: Mock = Mock()
        mock_processor._detect_provider.return_value = "openai"

        avg_time, status = benchmark_exact_match_detection(mock_processor)

        assert avg_time == 0.05
        assert "PASS" in status

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_warn_above_baseline_within_threshold(
        self, mock_perf_counter: Mock, mock_mean: Mock
    ) -> None:
        """Test exact match benchmark warning."""
        mock_perf_counter.side_effect = [1.0] * 210
        mock_mean.return_value = 0.11  # Above 0.1ms but within threshold

        mock_processor: Mock = Mock()
        mock_processor._detect_provider.return_value = "openai"

        avg_time, status = benchmark_exact_match_detection(mock_processor)

        assert avg_time == 0.11
        assert "WARN" in status

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_fail_exceeds_threshold(
        self, mock_perf_counter: Mock, mock_mean: Mock
    ) -> None:
        """Test exact match benchmark failure."""
        mock_perf_counter.side_effect = [1.0] * 210
        mock_mean.return_value = 0.20  # Exceeds threshold

        mock_processor: Mock = Mock()
        mock_processor._detect_provider.return_value = "openai"

        avg_time, status = benchmark_exact_match_detection(mock_processor)

        assert avg_time == 0.20
        assert "FAIL" in status

    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_detection_failure_wrong_provider(self, _mock_perf_counter: Mock) -> None:
        """Test benchmark failure when detection returns wrong provider."""
        mock_processor: Mock = Mock()
        mock_processor._detect_provider.return_value = "anthropic"  # Wrong provider

        avg_time, status = benchmark_exact_match_detection(mock_processor)

        assert avg_time == 0.0
        assert "FAIL" in status
        assert "anthropic" in status


class TestBenchmarkSubsetMatchDetection:
    """Test benchmark_subset_match_detection() function."""

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_pass_within_baseline(
        self, mock_perf_counter: Mock, mock_mean: Mock
    ) -> None:
        """Test subset match benchmark passing."""
        mock_perf_counter.side_effect = [1.0] * 210
        mock_mean.return_value = 0.10  # Within 0.15ms baseline

        mock_processor: Mock = Mock()
        mock_processor._detect_provider.return_value = "openai"

        avg_time, status = benchmark_subset_match_detection(mock_processor)

        assert avg_time == 0.10
        assert "PASS" in status

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_warn_above_baseline_within_threshold(
        self, mock_perf_counter: Mock, mock_mean: Mock
    ) -> None:
        """Test subset match benchmark warning."""
        mock_perf_counter.side_effect = [1.0] * 210
        mock_mean.return_value = 0.16  # Above 0.15ms but within threshold

        mock_processor: Mock = Mock()
        mock_processor._detect_provider.return_value = "unknown"

        avg_time, status = benchmark_subset_match_detection(mock_processor)

        assert avg_time == 0.16
        assert "WARN" in status

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_fail_exceeds_threshold(
        self, mock_perf_counter: Mock, mock_mean: Mock
    ) -> None:
        """Test subset match benchmark failure."""
        mock_perf_counter.side_effect = [1.0] * 210
        mock_mean.return_value = 0.25  # Exceeds threshold

        mock_processor: Mock = Mock()
        mock_processor._detect_provider.return_value = "openai"

        avg_time, status = benchmark_subset_match_detection(mock_processor)

        assert avg_time == 0.25
        assert "FAIL" in status

    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_detection_failure_unexpected_provider(
        self, _mock_perf_counter: Mock
    ) -> None:
        """Test benchmark failure when unexpected provider detected."""
        mock_processor: Mock = Mock()
        mock_processor._detect_provider.return_value = "cohere"  # Unexpected

        avg_time, status = benchmark_subset_match_detection(mock_processor)

        assert avg_time == 0.0
        assert "FAIL" in status
        assert "cohere" in status


class TestBenchmarkMetadataAccess:
    """Test benchmark_metadata_access() function."""

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_pass_within_baseline(
        self, mock_perf_counter: Mock, mock_mean: Mock
    ) -> None:
        """Test metadata access benchmark passing."""
        mock_perf_counter.side_effect = [1.0] * 202  # 101 pairs
        mock_mean.return_value = 0.005  # Within 0.01ms baseline

        mock_loader: Mock = Mock()
        mock_loader.get_build_metadata.return_value = {"version": "1.0"}

        avg_time, status = benchmark_metadata_access(mock_loader)

        assert avg_time == 0.005
        assert "PASS" in status

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_warn_above_baseline_within_threshold(
        self, mock_perf_counter: Mock, mock_mean: Mock
    ) -> None:
        """Test metadata access benchmark warning."""
        mock_perf_counter.side_effect = [1.0] * 202
        mock_mean.return_value = 0.011  # Above 0.01ms but within threshold

        mock_loader: Mock = Mock()
        mock_loader.get_build_metadata.return_value = {"version": "1.0"}

        avg_time, status = benchmark_metadata_access(mock_loader)

        assert avg_time == 0.011
        assert "WARN" in status

    @patch("config.dsl.validation.performance_benchmarks.statistics.mean")
    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_fail_exceeds_threshold(
        self, mock_perf_counter: Mock, mock_mean: Mock
    ) -> None:
        """Test metadata access benchmark failure."""
        mock_perf_counter.side_effect = [1.0] * 202
        mock_mean.return_value = 0.020  # Exceeds threshold

        mock_loader: Mock = Mock()
        mock_loader.get_build_metadata.return_value = {"version": "1.0"}

        avg_time, status = benchmark_metadata_access(mock_loader)

        assert avg_time == 0.020
        assert "FAIL" in status

    @patch("config.dsl.validation.performance_benchmarks.time.perf_counter")
    def test_metadata_empty_failure(self, _mock_perf_counter: Mock) -> None:
        """Test benchmark failure when metadata is empty."""
        mock_loader: Mock = Mock()
        mock_loader.get_build_metadata.return_value = {}

        avg_time, status = benchmark_metadata_access(mock_loader)

        assert avg_time == 0.0
        assert "FAIL" in status
        assert "empty" in status


class TestRunPerformanceChecks:
    """Test run_performance_checks() function."""

    @patch("config.dsl.validation.performance_benchmarks.benchmark_metadata_access")
    @patch(
        "config.dsl.validation.performance_benchmarks.benchmark_subset_match_detection"
    )
    @patch(
        "config.dsl.validation.performance_benchmarks.benchmark_exact_match_detection"
    )
    @patch("config.dsl.validation.performance_benchmarks.benchmark_bundle_loading")
    @patch("config.dsl.validation.performance_benchmarks.UniversalProviderProcessor")
    @patch("config.dsl.validation.performance_benchmarks.DevelopmentAwareBundleLoader")
    def test_all_benchmarks_pass(
        self,
        _mock_loader_class: Mock,
        _mock_processor_class: Mock,
        mock_bundle_benchmark: Mock,
        mock_exact_benchmark: Mock,
        mock_subset_benchmark: Mock,
        mock_metadata_benchmark: Mock,
    ) -> None:
        """Test when all benchmarks pass."""
        mock_bundle_benchmark.return_value = (3.0, "✅ PASS")
        mock_exact_benchmark.return_value = (0.05, "✅ PASS")
        mock_subset_benchmark.return_value = (0.10, "✅ PASS")
        mock_metadata_benchmark.return_value = (0.005, "✅ PASS")

        all_passed, results = run_performance_checks(Path("test.pkl"))

        assert all_passed
        assert "bundle_loading" in results
        assert results["bundle_loading"]["time_ms"] == 3.0
        assert "exact_match" in results
        assert "subset_match" in results
        assert "metadata_access" in results

    @patch("config.dsl.validation.performance_benchmarks.benchmark_metadata_access")
    @patch(
        "config.dsl.validation.performance_benchmarks.benchmark_subset_match_detection"
    )
    @patch(
        "config.dsl.validation.performance_benchmarks.benchmark_exact_match_detection"
    )
    @patch("config.dsl.validation.performance_benchmarks.benchmark_bundle_loading")
    @patch("config.dsl.validation.performance_benchmarks.UniversalProviderProcessor")
    @patch("config.dsl.validation.performance_benchmarks.DevelopmentAwareBundleLoader")
    def test_some_benchmarks_fail(
        self,
        _mock_loader_class: Mock,
        _mock_processor_class: Mock,
        mock_bundle_benchmark: Mock,
        mock_exact_benchmark: Mock,
        mock_subset_benchmark: Mock,
        mock_metadata_benchmark: Mock,
    ) -> None:
        """Test when some benchmarks fail."""
        mock_bundle_benchmark.return_value = (10.0, "❌ FAIL")
        mock_exact_benchmark.return_value = (0.05, "✅ PASS")
        mock_subset_benchmark.return_value = (0.30, "❌ FAIL")
        mock_metadata_benchmark.return_value = (0.005, "✅ PASS")

        all_passed, results = run_performance_checks(Path("test.pkl"))

        assert not all_passed
        assert "FAIL" in results["bundle_loading"]["status"]
        assert "FAIL" in results["subset_match"]["status"]

    @patch("config.dsl.validation.performance_benchmarks.benchmark_bundle_loading")
    def test_exception_in_bundle_loading(self, mock_bundle_benchmark: Mock) -> None:
        """Test handling of exception in bundle loading."""
        mock_bundle_benchmark.side_effect = RuntimeError("Load error")

        all_passed, results = run_performance_checks(Path("test.pkl"))

        assert not all_passed
        assert "error" in results["bundle_loading"]
        assert "Load error" in results["bundle_loading"]["error"]

    @patch(
        "config.dsl.validation.performance_benchmarks.benchmark_exact_match_detection"
    )
    @patch("config.dsl.validation.performance_benchmarks.benchmark_bundle_loading")
    @patch("config.dsl.validation.performance_benchmarks.UniversalProviderProcessor")
    @patch("config.dsl.validation.performance_benchmarks.DevelopmentAwareBundleLoader")
    def test_exception_in_exact_match(
        self,
        _mock_loader_class: Mock,
        _mock_processor_class: Mock,
        mock_bundle_benchmark: Mock,
        mock_exact_benchmark: Mock,
    ) -> None:
        """Test handling of exception in exact match detection."""
        mock_bundle_benchmark.return_value = (3.0, "✅ PASS")
        mock_exact_benchmark.side_effect = RuntimeError("Detection error")

        all_passed, results = run_performance_checks(Path("test.pkl"))

        assert not all_passed
        assert "error" in results["exact_match"]

    @patch(
        "config.dsl.validation.performance_benchmarks.benchmark_subset_match_detection"
    )
    @patch(
        "config.dsl.validation.performance_benchmarks.benchmark_exact_match_detection"
    )
    @patch("config.dsl.validation.performance_benchmarks.benchmark_bundle_loading")
    @patch("config.dsl.validation.performance_benchmarks.UniversalProviderProcessor")
    @patch("config.dsl.validation.performance_benchmarks.DevelopmentAwareBundleLoader")
    def test_exception_in_subset_match(
        self,
        _mock_loader_class: Mock,
        _mock_processor_class: Mock,
        mock_bundle_benchmark: Mock,
        mock_exact_benchmark: Mock,
        mock_subset_benchmark: Mock,
    ) -> None:
        """Test handling of exception in subset match detection."""
        mock_bundle_benchmark.return_value = (3.0, "✅ PASS")
        mock_exact_benchmark.return_value = (0.05, "✅ PASS")
        mock_subset_benchmark.side_effect = RuntimeError("Subset error")

        all_passed, results = run_performance_checks(Path("test.pkl"))

        assert not all_passed
        assert "error" in results["subset_match"]

    @patch("config.dsl.validation.performance_benchmarks.benchmark_metadata_access")
    @patch(
        "config.dsl.validation.performance_benchmarks.benchmark_subset_match_detection"
    )
    @patch(
        "config.dsl.validation.performance_benchmarks.benchmark_exact_match_detection"
    )
    @patch("config.dsl.validation.performance_benchmarks.benchmark_bundle_loading")
    @patch("config.dsl.validation.performance_benchmarks.UniversalProviderProcessor")
    @patch("config.dsl.validation.performance_benchmarks.DevelopmentAwareBundleLoader")
    def test_custom_bundle_path(  # pylint: disable=too-many-positional-arguments
        self,
        _mock_loader_class: Mock,
        _mock_processor_class: Mock,
        mock_bundle_benchmark: Mock,
        mock_exact_benchmark: Mock,
        mock_subset_benchmark: Mock,
        mock_metadata_benchmark: Mock,
    ) -> None:
        """Test performance checks with custom bundle path."""
        mock_bundle_benchmark.return_value = (3.0, "✅ PASS")
        mock_exact_benchmark.return_value = (0.05, "✅ PASS")
        mock_subset_benchmark.return_value = (0.10, "✅ PASS")
        mock_metadata_benchmark.return_value = (0.005, "✅ PASS")

        custom_path: Path = Path("/custom/bundle.pkl")
        all_passed, _results = run_performance_checks(custom_path)

        assert all_passed
        # Verify custom path was used
        mock_bundle_benchmark.assert_called_once_with(custom_path)


class TestCheckPerformanceRegression:
    """Test check_performance_regression() function (alias)."""

    @patch("config.dsl.validation.performance_benchmarks.run_performance_checks")
    def test_successful_check_alias(self, mock_run_checks: Mock) -> None:
        """Test alias function works correctly on success."""
        mock_run_checks.return_value = (True, {"test": "data"})

        all_passed, results = check_performance_regression(Path("test.pkl"))

        assert all_passed
        assert results == {"test": "data"}
        mock_run_checks.assert_called_once_with(Path("test.pkl"))

    @patch("config.dsl.validation.performance_benchmarks.run_performance_checks")
    def test_failed_check_alias_propagates(self, mock_run_checks: Mock) -> None:
        """Test alias function propagates failures correctly."""
        mock_run_checks.return_value = (False, {"error": "failed"})

        all_passed, results = check_performance_regression()

        assert not all_passed
        assert results == {"error": "failed"}


class TestMain:
    """Test main() CLI entry point."""

    @patch("config.dsl.validation.performance_benchmarks.run_performance_checks")
    def test_all_checks_pass_exit_zero(self, mock_run_checks: Mock) -> None:
        """Test successful checks return exit code 0."""
        mock_run_checks.return_value = (
            True,
            {
                "bundle_loading": {"time_ms": 3.0, "status": "✅ PASS"},
                "exact_match": {"time_ms": 0.05, "status": "✅ PASS"},
                "subset_match": {"time_ms": 0.10, "status": "✅ PASS"},
                "metadata_access": {"time_ms": 0.005, "status": "✅ PASS"},
            },
        )

        exit_code: int = main()

        assert exit_code == 0

    @patch("config.dsl.validation.performance_benchmarks.run_performance_checks")
    def test_some_checks_fail_exit_one(self, mock_run_checks: Mock) -> None:
        """Test failed checks return exit code 1."""
        mock_run_checks.return_value = (
            False,
            {
                "bundle_loading": {"time_ms": 10.0, "status": "❌ FAIL"},
                "exact_match": {"time_ms": 0.05, "status": "✅ PASS"},
                "subset_match": {"time_ms": 0.30, "status": "❌ FAIL"},
                "metadata_access": {"time_ms": 0.005, "status": "✅ PASS"},
            },
        )

        exit_code: int = main()

        assert exit_code == 1

    @patch("config.dsl.validation.performance_benchmarks.run_performance_checks")
    def test_results_display_correctly(self, mock_run_checks: Mock) -> None:
        """Test that results are displayed in CLI output."""
        mock_run_checks.return_value = (
            False,
            {
                "bundle_loading": {"error": "Test error"},
                "exact_match": {"time_ms": 0.05, "status": "✅ PASS"},
                "subset_match": {"time_ms": 0.10, "status": "✅ PASS"},
                "metadata_access": {"time_ms": 0.005, "status": "✅ PASS"},
            },
        )

        exit_code: int = main()

        assert exit_code == 1

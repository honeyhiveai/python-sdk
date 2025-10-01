"""
Unit tests for load testing module.

Tests the LoadTestRunner class for QPS and concurrency testing.
"""

import pytest
from unittest.mock import Mock, patch
from ..testing.load_testing import LoadTestRunner, LoadTestConfig, LoadTestResult
from ..core.config import BenchmarkConfig
from ..scenarios.prompt_generator import PromptGenerator
from ..providers.base_provider import ProviderResponse


class TestLoadTestConfig:
    """Test cases for LoadTestConfig dataclass."""
    
    def test_default_initialization(self):
        """Test LoadTestConfig default initialization."""
        config = LoadTestConfig(name="Test Load")
        
        assert config.name == "Test Load"
        assert config.qps_levels == [1.0, 2.0, 5.0, 10.0, 20.0]
        assert config.concurrency_levels == [1, 2, 4, 8, 16]
        assert config.duration_seconds == 60
        assert config.warmup_seconds == 10
        assert config.ramp_up_seconds == 5
        assert config.cooldown_seconds == 5
    
    def test_custom_initialization(self):
        """Test LoadTestConfig with custom values."""
        config = LoadTestConfig(
            name="Custom Test",
            qps_levels=[1.0, 5.0, 10.0],
            concurrency_levels=[2, 4, 8],
            duration_seconds=30,
            warmup_seconds=5
        )
        
        assert config.name == "Custom Test"
        assert config.qps_levels == [1.0, 5.0, 10.0]
        assert config.concurrency_levels == [2, 4, 8]
        assert config.duration_seconds == 30
        assert config.warmup_seconds == 5


class TestLoadTestResult:
    """Test cases for LoadTestResult dataclass."""
    
    def test_initialization(self):
        """Test LoadTestResult initialization."""
        result = LoadTestResult(
            test_name="Test Result",
            target_qps=5.0,
            concurrency=4,
            actual_qps=4.8,
            latencies=[100.0, 110.0, 120.0, 130.0, 140.0],
            success_rate=95.0,
            memory_stats={"peak_memory_mb": 150.0},
            saturation_detected=False,
            error_rate=5.0
        )
        
        assert result.test_name == "Test Result"
        assert result.target_qps == 5.0
        assert result.actual_qps == 4.8
        assert result.success_rate == 95.0
        assert result.saturation_detected is False
    
    def test_get_latency_percentiles(self):
        """Test latency percentile calculation."""
        latencies = [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0]
        result = LoadTestResult(
            test_name="Percentile Test",
            target_qps=5.0,
            concurrency=4,
            actual_qps=4.8,
            latencies=latencies,
            success_rate=100.0,
            memory_stats={},
            saturation_detected=False,
            error_rate=0.0
        )
        
        percentiles = result.get_latency_percentiles()
        
        assert "p50" in percentiles
        assert "p95" in percentiles
        assert "p99" in percentiles
        assert percentiles["p50"] == 150.0  # Median of 10 values (index 5)
        assert percentiles["p95"] == 190.0  # 95th percentile (index 9)
        assert percentiles["p99"] == 190.0  # 99th percentile (index 9)
    
    def test_get_latency_percentiles_empty(self):
        """Test latency percentiles with empty latencies."""
        result = LoadTestResult(
            test_name="Empty Test",
            target_qps=5.0,
            concurrency=4,
            actual_qps=0.0,
            latencies=[],
            success_rate=0.0,
            memory_stats={},
            saturation_detected=True,
            error_rate=100.0
        )
        
        percentiles = result.get_latency_percentiles()
        
        assert percentiles["p50"] == 0.0
        assert percentiles["p95"] == 0.0
        assert percentiles["p99"] == 0.0
    
    def test_get_summary(self):
        """Test summary generation."""
        result = LoadTestResult(
            test_name="Summary Test",
            target_qps=10.0,
            concurrency=8,
            actual_qps=9.5,
            latencies=[100.0, 200.0, 300.0],
            success_rate=98.5,
            memory_stats={"peak_memory_mb": 200.0},
            saturation_detected=False,
            error_rate=1.5
        )
        
        summary = result.get_summary()
        
        assert summary["Test"] == "Summary Test"
        assert summary["Target QPS"] == "10.0"
        assert summary["Actual QPS"] == "9.5"
        assert summary["Concurrency"] == 8
        assert summary["Success Rate"] == "98.5%"
        assert summary["Error Rate"] == "1.5%"
        assert summary["Saturated"] == "No"


class TestLoadTestRunner:
    """Test cases for LoadTestRunner class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = BenchmarkConfig(operations=10, warmup_operations=0)
        self.prompt_generator = PromptGenerator(seed=42)
        self.runner = LoadTestRunner(self.config, self.prompt_generator)
    
    def test_initialization(self):
        """Test LoadTestRunner initialization."""
        assert self.runner.config == self.config
        assert self.runner.prompt_generator == self.prompt_generator
        assert self.runner.memory_profiler is not None
    
    def test_detect_saturation_qps(self):
        """Test QPS saturation detection."""
        # QPS saturation: can't achieve target QPS
        is_saturated = self.runner._detect_saturation(
            target_qps=10.0,
            actual_qps=7.0,  # Less than 80% of target
            latencies=[1000.0, 1100.0, 1200.0],
            error_rate=2.0
        )
        assert is_saturated is True
        
        # No saturation
        is_saturated = self.runner._detect_saturation(
            target_qps=10.0,
            actual_qps=9.5,  # Close to target
            latencies=[1000.0, 1100.0, 1200.0],
            error_rate=1.0
        )
        assert is_saturated is False
    
    def test_detect_saturation_latency(self):
        """Test latency saturation detection."""
        # Latency saturation: P95 too high
        high_latencies = [1000.0] * 94 + [35000.0] * 6  # P95 > 30 seconds
        is_saturated = self.runner._detect_saturation(
            target_qps=5.0,
            actual_qps=4.8,
            latencies=high_latencies,
            error_rate=1.0
        )
        assert is_saturated is True
    
    def test_detect_saturation_error_rate(self):
        """Test error rate saturation detection."""
        # Error saturation: too many errors
        is_saturated = self.runner._detect_saturation(
            target_qps=5.0,
            actual_qps=4.8,
            latencies=[1000.0, 1100.0, 1200.0],
            error_rate=15.0  # More than 10%
        )
        assert is_saturated is True
    
    def test_find_max_stable_qps(self):
        """Test finding maximum stable QPS."""
        results = [
            LoadTestResult("Test", 1.0, 1, 1.0, [], 100.0, {}, False, 0.0),
            LoadTestResult("Test", 5.0, 2, 5.0, [], 98.0, {}, False, 2.0),
            LoadTestResult("Test", 10.0, 4, 9.0, [], 95.0, {}, True, 5.0),  # Saturated
            LoadTestResult("Test", 20.0, 8, 15.0, [], 90.0, {}, True, 10.0),  # Saturated
        ]
        
        max_stable = self.runner._find_max_stable_qps(results)
        assert max_stable == 5.0  # Last non-saturated with >95% success rate
    
    def test_find_max_stable_qps_none(self):
        """Test finding max stable QPS when none are stable."""
        results = [
            LoadTestResult("Test", 1.0, 1, 1.0, [], 90.0, {}, True, 10.0),  # Low success rate
            LoadTestResult("Test", 5.0, 2, 4.0, [], 85.0, {}, True, 15.0),  # Saturated
        ]
        
        max_stable = self.runner._find_max_stable_qps(results)
        assert max_stable is None
    
    def test_analyze_performance_curve(self):
        """Test performance curve analysis."""
        results = [
            LoadTestResult("Test", 1.0, 1, 1.0, [100.0], 100.0, {}, False, 0.0),
            LoadTestResult("Test", 5.0, 2, 5.0, [120.0], 100.0, {}, False, 0.0),
            LoadTestResult("Test", 10.0, 4, 10.0, [200.0], 95.0, {}, False, 5.0),  # 50% latency increase
            LoadTestResult("Test", 20.0, 8, 18.0, [400.0], 90.0, {}, True, 10.0),
        ]
        
        analysis = self.runner._analyze_performance_curve(results)
        
        assert "qps_range" in analysis
        assert "latency_range" in analysis
        assert "inflection_qps" in analysis
        assert "degradation_pattern" in analysis
        assert "stable_region" in analysis
        
        # Should detect inflection at 5.0 QPS (where latency jumped from 100 to 120, then 200)
        assert analysis["inflection_qps"] == 5.0
        assert analysis["degradation_pattern"] == "exponential"
    
    def test_analyze_concurrency_impact(self):
        """Test concurrency impact analysis."""
        results = [
            LoadTestResult("Test", 5.0, 1, 5.0, [200.0], 100.0, {}, False, 0.0),
            LoadTestResult("Test", 5.0, 2, 5.0, [150.0], 100.0, {}, False, 0.0),  # Best latency
            LoadTestResult("Test", 5.0, 4, 5.0, [160.0], 100.0, {}, False, 0.0),
            LoadTestResult("Test", 5.0, 8, 5.0, [180.0], 100.0, {}, False, 0.0),
        ]
        
        analysis = self.runner._analyze_concurrency_impact(results)
        
        assert "optimal_concurrency" in analysis
        assert "latency_improvement" in analysis
        assert "diminishing_returns_threshold" in analysis
        assert "concurrency_efficiency" in analysis
        
        # Should identify concurrency=2 as optimal (lowest latency)
        assert analysis["optimal_concurrency"] == 2
        assert analysis["latency_improvement"] == 50.0  # 200 - 150
    
    def test_find_diminishing_returns(self):
        """Test finding diminishing returns threshold."""
        results = [
            LoadTestResult("Test", 5.0, 1, 5.0, [200.0], 100.0, {}, False, 0.0),
            LoadTestResult("Test", 5.0, 2, 5.0, [150.0], 100.0, {}, False, 0.0),  # 50ms improvement
            LoadTestResult("Test", 5.0, 4, 5.0, [140.0], 100.0, {}, False, 0.0),  # 10ms improvement (< 50% of previous)
            LoadTestResult("Test", 5.0, 8, 5.0, [138.0], 100.0, {}, False, 0.0),  # 2ms improvement
        ]
        
        threshold = self.runner._find_diminishing_returns(results)
        assert threshold == 2  # Where improvement dropped significantly (from 50ms to 10ms improvement)
    
    def test_analyze_burst_impact(self):
        """Test burst impact analysis."""
        baseline = LoadTestResult("Baseline", 2.0, 2, 2.0, [100.0], 100.0, {"peak_memory_mb": 100.0}, False, 0.0)
        burst = LoadTestResult("Burst", 50.0, 16, 45.0, [500.0], 85.0, {"peak_memory_mb": 200.0}, True, 15.0)
        recovery = LoadTestResult("Recovery", 2.0, 2, 2.0, [110.0], 100.0, {"peak_memory_mb": 105.0}, False, 0.0)
        
        analysis = self.runner._analyze_burst_impact(baseline, burst, recovery)
        
        assert "burst_latency_impact" in analysis
        assert "recovery_time_estimate" in analysis
        assert "burst_success_rate" in analysis
        assert "system_resilience" in analysis
        assert "memory_spike" in analysis
        
        assert analysis["burst_latency_impact"] == 400.0  # 500 - 100
        assert analysis["burst_success_rate"] == 85.0
        assert analysis["system_resilience"] == "medium"  # 70-90% success rate
        assert analysis["memory_spike"] == 100.0  # 200 - 100
    
    @patch('time.perf_counter')
    @patch('time.sleep')
    def test_run_load_test_phase_sequential(self, mock_sleep, mock_time):
        """Test running a single load test phase in sequential mode."""
        # Mock time progression - provide many values for the while loop
        mock_time.side_effect = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
        
        # Mock provider factory
        mock_provider = Mock()
        mock_provider.make_call.return_value = ProviderResponse(
            provider_name="test",
            operation_id=1,
            success=True,
            latency_ms=100.0,
            tokens_used=50,
            response_text="Test response",
            response_length=13,
            model_used="test-model",
            error_message=None
        )
        
        def provider_factory():
            return mock_provider
        
        load_config = LoadTestConfig(
            name="Test Phase",
            duration_seconds=1,
            warmup_seconds=0
        )
        
        with patch.object(self.runner.memory_profiler, 'reset'), \
             patch.object(self.runner.memory_profiler, 'start_monitoring'), \
             patch.object(self.runner.memory_profiler, 'stop_monitoring') as mock_stop:
            
            mock_stop.return_value = {"peak_memory_mb": 100.0}
            
            result = self.runner._run_load_test_phase(
                provider_factory=provider_factory,
                target_qps=2.0,
                concurrency=1,
                load_config=load_config
            )
        
        assert isinstance(result, LoadTestResult)
        assert result.test_name == "Test Phase"
        assert result.target_qps == 2.0
        assert result.concurrency == 1
        assert len(result.latencies) > 0
        
        # Verify provider setup
        mock_provider.initialize_client.assert_called_once()
        mock_provider.initialize_instrumentor.assert_called_once()
        mock_provider.cleanup_instrumentor.assert_called_once()

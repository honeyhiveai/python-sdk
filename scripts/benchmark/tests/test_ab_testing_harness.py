"""
Unit tests for A/B testing harness module.

Tests the ABTestingHarness class for traced vs untraced workload comparison.
"""

import pytest
from unittest.mock import Mock, patch
from ..testing.ab_testing_harness import ABTestingHarness, ABTestResult
from ..core.config import BenchmarkConfig
from ..scenarios.prompt_generator import PromptGenerator
from ..providers.base_provider import ProviderResponse


class TestABTestResult:
    """Test cases for ABTestResult dataclass."""
    
    def test_initialization(self):
        """Test ABTestResult initialization."""
        result = ABTestResult(
            test_name="Test A/B",
            traced_latencies=[100.0, 110.0, 120.0],
            untraced_latencies=[90.0, 95.0, 100.0],
            traced_memory={"peak_memory_mb": 150.0},
            untraced_memory={"peak_memory_mb": 100.0},
            overhead_percent=15.0,
            statistical_significance=0.01,
            confidence_interval=(10.0, 20.0),
            sample_size=50
        )
        
        assert result.test_name == "Test A/B"
        assert result.overhead_percent == 15.0
        assert result.sample_size == 50
    
    def test_is_statistically_significant(self):
        """Test statistical significance check."""
        # Significant result
        significant_result = ABTestResult(
            test_name="Significant",
            traced_latencies=[100.0],
            untraced_latencies=[90.0],
            traced_memory={},
            untraced_memory={},
            overhead_percent=10.0,
            statistical_significance=0.01,  # p < 0.05
            confidence_interval=(5.0, 15.0),
            sample_size=50
        )
        assert significant_result.is_statistically_significant() is True
        
        # Non-significant result
        non_significant_result = ABTestResult(
            test_name="Non-significant",
            traced_latencies=[100.0],
            untraced_latencies=[95.0],
            traced_memory={},
            untraced_memory={},
            overhead_percent=5.0,
            statistical_significance=0.10,  # p > 0.05
            confidence_interval=(0.0, 10.0),
            sample_size=50
        )
        assert non_significant_result.is_statistically_significant() is False
    
    def test_get_summary(self):
        """Test summary generation."""
        result = ABTestResult(
            test_name="Summary Test",
            traced_latencies=[100.0, 110.0],
            untraced_latencies=[90.0, 95.0],
            traced_memory={"overhead_percent": 20.0},
            untraced_memory={},
            overhead_percent=15.0,
            statistical_significance=0.01,
            confidence_interval=(10.0, 20.0),
            sample_size=25
        )
        
        summary = result.get_summary()
        
        assert summary["Test Name"] == "Summary Test"
        assert summary["Sample Size"] == "25 per group"
        assert "15.00%" in summary["Overhead"]
        assert summary["Significant"] == "Yes"


class TestABTestingHarness:
    """Test cases for ABTestingHarness class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = BenchmarkConfig(operations=5, warmup_operations=0)
        self.prompt_generator = PromptGenerator(seed=42)
        self.harness = ABTestingHarness(self.config, self.prompt_generator)
    
    def test_initialization(self):
        """Test ABTestingHarness initialization."""
        assert self.harness.config == self.config
        assert self.harness.prompt_generator == self.prompt_generator
        assert self.harness.memory_profiler is not None
    
    def test_generate_test_prompts(self):
        """Test test prompt generation."""
        prompts = self.harness._generate_test_prompts(sample_size=3, seed=42)
        
        assert len(prompts) == 3
        assert all(isinstance(prompt, str) for prompt, scenario in prompts)
        assert all(scenario is not None for prompt, scenario in prompts)
        
        # Test deterministic generation
        prompts2 = self.harness._generate_test_prompts(sample_size=3, seed=42)
        assert prompts == prompts2
    
    @patch('time.perf_counter')
    def test_run_workload_traced(self, mock_time):
        """Test running traced workload."""
        # Mock time progression
        mock_time.side_effect = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        
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
        
        # Generate test prompts
        prompts = [("test prompt", None)]
        
        with patch.object(self.harness.memory_profiler, 'start_monitoring'), \
             patch.object(self.harness.memory_profiler, 'stop_monitoring') as mock_stop, \
             patch.object(self.harness.memory_profiler, 'sample_memory'):
            
            mock_stop.return_value = {"peak_memory_mb": 100.0}
            
            result = self.harness._run_workload(
                provider_factory=provider_factory,
                prompts=prompts,
                enable_tracing=True,
                group_name="traced_test"
            )
        
        assert result["group_name"] == "traced_test"
        assert len(result["latencies"]) == 1
        assert len(result["responses"]) == 1
        assert result["success_count"] == 1
        
        # Verify provider was set up correctly for tracing
        mock_provider.initialize_client.assert_called_once()
        mock_provider.initialize_instrumentor.assert_called_once()
        mock_provider.cleanup_instrumentor.assert_called_once()
    
    @patch('time.perf_counter')
    def test_run_workload_untraced(self, mock_time):
        """Test running untraced workload."""
        # Mock time progression
        mock_time.side_effect = [0.0, 0.1, 0.2, 0.3]
        
        # Mock provider factory
        mock_provider = Mock()
        mock_provider.make_call.return_value = ProviderResponse(
            provider_name="test",
            operation_id=1,
            success=True,
            latency_ms=90.0,
            tokens_used=45,
            response_text="Test response",
            response_length=13,
            model_used="test-model",
            error_message=None
        )
        
        def provider_factory():
            return mock_provider
        
        # Generate test prompts
        prompts = [("test prompt", None)]
        
        with patch.object(self.harness.memory_profiler, 'start_monitoring'), \
             patch.object(self.harness.memory_profiler, 'stop_monitoring') as mock_stop, \
             patch.object(self.harness.memory_profiler, 'sample_memory'):
            
            mock_stop.return_value = {"peak_memory_mb": 80.0}
            
            result = self.harness._run_workload(
                provider_factory=provider_factory,
                prompts=prompts,
                enable_tracing=False,
                group_name="untraced_test"
            )
        
        assert result["group_name"] == "untraced_test"
        assert len(result["latencies"]) == 1
        assert len(result["responses"]) == 1
        assert result["success_count"] == 1
        
        # Verify provider was set up without tracing
        mock_provider.initialize_client.assert_called_once()
        mock_provider.initialize_instrumentor.assert_not_called()
        mock_provider.cleanup_instrumentor.assert_not_called()
    
    def test_calculate_ab_metrics(self):
        """Test A/B metrics calculation."""
        traced_results = {
            "latencies": [110.0, 115.0, 120.0],
            "responses": [Mock(success=True)] * 3,
            "memory_stats": {"peak_memory_mb": 150.0}
        }
        
        untraced_results = {
            "latencies": [100.0, 105.0, 110.0],
            "responses": [Mock(success=True)] * 3,
            "memory_stats": {"peak_memory_mb": 120.0}
        }
        
        result = self.harness._calculate_ab_metrics(
            test_name="Test Calculation",
            traced_results=traced_results,
            untraced_results=untraced_results,
            sample_size=3
        )
        
        assert isinstance(result, ABTestResult)
        assert result.test_name == "Test Calculation"
        assert result.sample_size == 3
        assert len(result.traced_latencies) == 3
        assert len(result.untraced_latencies) == 3
        
        # Check overhead calculation
        traced_avg = sum(traced_results["latencies"]) / len(traced_results["latencies"])
        untraced_avg = sum(untraced_results["latencies"]) / len(untraced_results["latencies"])
        expected_overhead = ((traced_avg - untraced_avg) / untraced_avg) * 100
        
        assert abs(result.overhead_percent - expected_overhead) < 0.1
    
    def test_concurrent_workload_execution(self):
        """Test concurrent workload execution."""
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
        
        # Generate test prompts
        prompts = [("test prompt 1", None), ("test prompt 2", None)]
        
        with patch.object(self.harness.memory_profiler, 'start_monitoring'), \
             patch.object(self.harness.memory_profiler, 'stop_monitoring') as mock_stop, \
             patch.object(self.harness.memory_profiler, 'sample_memory'), \
             patch('time.perf_counter', side_effect=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5]):
            
            mock_stop.return_value = {"peak_memory_mb": 100.0}
            
            result = self.harness._run_concurrent_workload(
                provider_factory=provider_factory,
                prompts=prompts,
                enable_tracing=True,
                concurrency=2,
                group_name="concurrent_test"
            )
        
        assert result["group_name"] == "concurrent_test"
        assert len(result["responses"]) == 2
        assert result["success_count"] == 2

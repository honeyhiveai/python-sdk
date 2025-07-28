"""
Test to verify that the multi-threaded evaluation fixes resolve the
TracerWrapper concurrency issues for 100+ datapoints.
"""
import os  
import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from honeyhive.evaluation import Evaluation


def test_concurrent_evaluation_robustness():
    """Test that concurrent evaluation handles TracerWrapper failures gracefully"""
    
    with patch('honeyhive.evaluation.HoneyHive') as mock_hh, \
         patch('honeyhive.evaluation.HoneyHiveTracer') as mock_tracer_class:
        
        # Mock dataset setup
        mock_dataset_response = Mock()
        mock_dataset_response.object.testcases = [
            Mock(datapoints=[f'dp{i}' for i in range(50)])  # 50 datapoints for concurrent test
        ]
        mock_hh.return_value.datasets.get_datasets.return_value = mock_dataset_response
        
        # Mock batch datapoint fetch
        mock_datapoints = []
        for i in range(50):
            mock_dp = Mock()
            mock_dp.id = f'dp{i}'
            mock_dp.inputs = {'input': f'test{i}'}
            mock_dp.ground_truth = {'expected': f'result{i}'}
            mock_datapoints.append(mock_dp)
        
        mock_batch_response = Mock()
        mock_batch_response.object.datapoints = mock_datapoints
        mock_hh.return_value.datapoints.get_datapoints.return_value = mock_batch_response
        
        # Mock run creation
        mock_run_response = Mock()
        mock_run_response.create_run_response.run_id = 'test_run_id'
        mock_hh.return_value.experiments.create_run.return_value = mock_run_response
        mock_hh.return_value.experiments.update_run.return_value = Mock()
        
        # Mock tracer that fails sometimes (simulating TracerWrapper issues)
        failed_tracers = 0
        def mock_tracer_init(*args, **kwargs):
            nonlocal failed_tracers
            if failed_tracers < 5:  # First 5 tracers fail
                failed_tracers += 1
                raise Exception("'TracerWrapper' object has no attribute '_TracerWrapper__spans_processor'")
            
            mock_tracer = Mock()
            mock_tracer.session_id = f'session_{failed_tracers}'
            return mock_tracer
        
        mock_tracer_class.side_effect = mock_tracer_init
        
        def test_function(inputs, ground_truths):
            # Simulate some work
            time.sleep(0.01)
            return f"processed: {inputs.get('input', 'unknown')}"
        
        # Create evaluation with concurrency enabled
        eval_instance = Evaluation(
            api_key="test_key",
            project="test_project",
            name="test_evaluation", 
            function=test_function,
            dataset_id="test_dataset_id",
            max_workers=5,  # Use multiple workers to trigger concurrency
            run_concurrently=True,
            verbose=True
        )
        
        # Mock the flush method
        with patch('honeyhive.evaluation.HoneyHiveTracer.flush') as mock_flush:
            # Run the evaluation
            eval_instance.run()
            
            # Verify that flush was called (should have timeout fix)
            assert mock_flush.called
            
            # Verify that evaluation completed despite tracer failures
            assert len(eval_instance.eval_result.data['input']) == 50
            assert len(eval_instance.eval_result.data['output']) == 50
            
            # Verify that some evaluations succeeded even with tracer failures
            successful_outputs = [o for o in eval_instance.eval_result.data['output'] if o is not None]
            assert len(successful_outputs) >= 45  # At least 45/50 should succeed
            
            # Verify that failed tracers didn't crash the evaluation
            print(f"Successfully completed evaluation with {5} tracer failures")


def test_otel_timeout_configuration():
    """Test that OTEL timeout is properly configured"""
    
    with patch('honeyhive.evaluation.HoneyHive') as mock_hh, \
         patch.dict('os.environ', {}, clear=False) as mock_env:
        
        # Mock minimal setup to trigger timeout configuration
        mock_dataset_response = Mock() 
        mock_dataset_response.object.testcases = [Mock(datapoints=['dp1'])]
        mock_hh.return_value.datasets.get_datasets.return_value = mock_dataset_response
        
        mock_batch_response = Mock()
        mock_batch_response.object.datapoints = [Mock(id='dp1', inputs={}, ground_truth={})]
        mock_hh.return_value.datapoints.get_datapoints.return_value = mock_batch_response
        
        def test_function(inputs, ground_truths):
            return "test_output"
        
        # Create evaluation instance
        eval_instance = Evaluation(
            api_key="test_key",
            project="test_project",
            name="test_evaluation",
            function=test_function,
            dataset_id="test_dataset_id"
        )
        
        # Verify OTEL timeout was set
        assert os.environ.get("OTEL_EXPORTER_OTLP_TIMEOUT") == "30000"
        print("OTEL timeout properly configured to 30 seconds")


def test_flush_lock_timeout():
    """Test that flush lock uses timeout instead of non-blocking"""
    
    with patch('honeyhive.tracer.HoneyHiveTracer._flush_lock') as mock_lock, \
         patch('honeyhive.tracer.HoneyHiveTracer._is_traceloop_initialized', True), \
         patch('honeyhive.tracer.TracerWrapper') as mock_wrapper:
        
        # Mock lock.acquire to return True (successful acquisition)
        mock_lock.acquire.return_value = True
        
        from honeyhive.tracer import HoneyHiveTracer
        
        # Call flush
        HoneyHiveTracer.flush()
        
        # Verify that acquire was called with blocking=True and timeout=10.0
        mock_lock.acquire.assert_called_once_with(blocking=True, timeout=10.0)
        mock_lock.release.assert_called_once()
        
        print("Flush lock properly uses blocking with timeout")


def test_large_dataset_concurrent_evaluation():
    """Test concurrent evaluation with 100+ datapoints"""
    
    with patch('honeyhive.evaluation.HoneyHive') as mock_hh, \
         patch('honeyhive.evaluation.HoneyHiveTracer') as mock_tracer_class:
        
        # Create 150 datapoints
        num_datapoints = 150
        datapoint_ids = [f'dp{i}' for i in range(num_datapoints)]
        
        mock_dataset_response = Mock()
        mock_dataset_response.object.testcases = [Mock(datapoints=datapoint_ids)]
        mock_hh.return_value.datasets.get_datasets.return_value = mock_dataset_response
        
        # Mock batch fetch
        mock_datapoints = []
        for i in range(num_datapoints):
            mock_dp = Mock()
            mock_dp.id = f'dp{i}'
            mock_dp.inputs = {'input': f'test{i}'}
            mock_dp.ground_truth = {'expected': f'result{i}'}
            mock_datapoints.append(mock_dp)
        
        mock_batch_response = Mock()
        mock_batch_response.object.datapoints = mock_datapoints
        mock_hh.return_value.datapoints.get_datapoints.return_value = mock_batch_response
        
        # Mock run creation
        mock_run_response = Mock()
        mock_run_response.create_run_response.run_id = 'test_run_id'
        mock_hh.return_value.experiments.create_run.return_value = mock_run_response
        mock_hh.return_value.experiments.update_run.return_value = Mock()
        
        # Mock tracer to succeed (testing the happy path)
        mock_tracer_class.return_value.session_id = 'test_session'
        
        def test_function(inputs, ground_truths):
            return f"processed: {inputs.get('input', 'unknown')}"
        
        # Test with reduced concurrency (max_workers=3) for stability
        eval_instance = Evaluation(
            api_key="test_key",
            project="test_project",
            name="large_dataset_test",
            function=test_function,
            dataset_id="test_dataset_id",
            max_workers=3,  # Limited concurrency for stability
            run_concurrently=True
        )
        
        with patch('honeyhive.evaluation.HoneyHiveTracer.flush'):
            start_time = time.time()
            eval_instance.run()
            end_time = time.time()
            
            # Verify all datapoints were processed
            assert len(eval_instance.eval_result.data['input']) == num_datapoints
            assert len(eval_instance.eval_result.data['output']) == num_datapoints
            
            # Verify reasonable performance (should be much faster with batch fetching)
            duration = end_time - start_time
            print(f"Processed {num_datapoints} datapoints in {duration:.2f} seconds")
            
            # With batch fetching, this should complete relatively quickly even with 150 datapoints
            assert duration < 60, f"Evaluation took too long: {duration:.2f}s"


if __name__ == "__main__":
    test_concurrent_evaluation_robustness()
    test_otel_timeout_configuration()
    test_flush_lock_timeout()
    test_large_dataset_concurrent_evaluation()
    print("All multi-threaded evaluation tests passed!")
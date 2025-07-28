"""
Tests for evaluation edge cases and error handling scenarios.
"""
import pytest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from honeyhive.evaluation import Evaluation, evaluate, evaluator
from honeyhive.evaluation.evaluators import EvalSettings


class TestEvaluationEdgeCases:
    """Test edge cases in evaluation functionality."""
    
    def test_evaluation_with_empty_dataset(self):
        """Test evaluation with empty dataset."""
        def test_function(inputs, ground_truths):
            return "test"
        
        # Empty dataset triggers "No valid dataset" error due to line 124: if not self.dataset
        with pytest.raises(Exception, match="No valid 'dataset_id' or 'dataset' found"):
            with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
                eval_instance = Evaluation(
                    api_key="test_key",
                    project="test_project",
                    function=test_function,
                    dataset=[],  # Empty dataset fails validation
                    run_concurrently=False
                )
            
    def test_evaluation_with_large_worker_count(self):
        """Test evaluation with more workers than datapoints."""
        def test_function(inputs, ground_truths):
            return f"result_{inputs.get('id', '0')}"
        
        dataset = [
            {"inputs": {"id": "1"}, "ground_truths": {"expected": "result_1"}},
            {"inputs": {"id": "2"}, "ground_truths": {"expected": "result_2"}}
        ]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                max_workers=10,  # More workers than datapoints
                run_concurrently=True
            )
            
            eval_instance.run()
            
            # Should complete successfully
            assert len(eval_instance.eval_result.data['output']) == 2
            
    def test_evaluation_with_malformed_datapoint(self):
        """Test evaluation with malformed datapoint structure."""
        def test_function(inputs, ground_truths):
            return inputs.get('query', 'default')
        
        dataset = [
            {"inputs": {"query": "test1"}, "ground_truths": {"expected": "result1"}},
            {"not_inputs": "malformed"},  # Malformed datapoint
            {"inputs": {"query": "test3"}, "ground_truths": {"expected": "result3"}}
        ]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                run_concurrently=False
            )
            
            eval_instance.run()
            
            # Should handle malformed datapoint gracefully
            assert len(eval_instance.eval_result.data['output']) == 3
            assert eval_instance.eval_result.data['output'][1] == 'default'  # Used default for malformed
            
    def test_evaluation_with_failing_evaluator(self):
        """Test evaluation with evaluator that raises exceptions."""
        def test_function(inputs, ground_truths):
            return "test output"
        
        def failing_evaluator(outputs, inputs, ground_truths):
            raise ValueError("Evaluator failed!")
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                evaluators=[failing_evaluator],
                run_concurrently=False
            )
            
            eval_instance.run()
            
            # Should complete with None result for failing evaluator
            assert eval_instance.eval_result.data['metrics'][0]['failing_evaluator'] is None
            
    def test_evaluation_with_none_output(self):
        """Test evaluation when function returns None."""
        def none_function(inputs, ground_truths):
            return None
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=none_function,
                dataset=dataset,
                run_concurrently=False
            )
            
            eval_instance.run()
            
            # Should handle None output gracefully
            assert eval_instance.eval_result.data['output'][0] is None
            
    def test_evaluation_tracer_initialization_failure(self):
        """Test evaluation when tracer initialization fails."""
        def test_function(inputs, ground_truths):
            return "test output"
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            # Mock tracer initialization to fail
            with patch('honeyhive.evaluation.HoneyHiveTracer', side_effect=Exception("Tracer failed")):
                eval_instance = Evaluation(
                    api_key="test_key",
                    project="test_project",
                    function=test_function,
                    dataset=dataset,
                    run_concurrently=False,
                    verbose=True
                )
                
                eval_instance.run()
                
                # Should continue evaluation without tracing
                assert eval_instance.eval_result.data['output'][0] == "test output"
                
    def test_evaluation_with_duplicate_evaluator_names(self):
        """Test evaluation with evaluators having duplicate names."""
        def test_function(inputs, ground_truths):
            return "test"
        
        def evaluator1(outputs, inputs, ground_truths):
            return 1
        
        def evaluator2(outputs, inputs, ground_truths):
            return 2
        
        # Give them the same name
        evaluator1.__name__ = "duplicate_name"
        evaluator2.__name__ = "duplicate_name"
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                evaluators=[evaluator1, evaluator2],
                run_concurrently=False
            )
            
            # Should raise error for duplicate names
            with pytest.raises(ValueError, match="Evaluator duplicate_name is defined multiple times"):
                eval_instance.run()
                
    def test_evaluation_run_update_failure(self):
        """Test evaluation when run update fails."""
        def test_function(inputs, ground_truths):
            return "test output"
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            # Make update_run fail
            mock_hh.return_value.experiments.update_run.side_effect = Exception("Update failed")
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                run_concurrently=False,
                print_results=False  # Avoid print output in tests
            )
            
            # Should complete despite update failure
            eval_instance.run()
            assert eval_instance.eval_result.data['output'][0] == "test output"
            
    def test_evaluation_with_custom_metadata(self):
        """Test evaluation with custom metadata."""
        def test_function(inputs, ground_truths):
            return "test"
        
        custom_metadata = {
            "experiment_version": "v1.2.3",
            "model_name": "test-model",
            "temperature": 0.7
        }
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                metadata=custom_metadata,
                run_concurrently=False
            )
            
            # Check that custom metadata is included
            assert eval_instance.metadata["experiment_version"] == "v1.2.3"
            assert eval_instance.metadata["model_name"] == "test-model"
            assert eval_instance.metadata["temperature"] == 0.7
            
    def test_evaluation_with_external_dataset_params(self):
        """Test evaluation with external dataset parameters."""
        def test_function(inputs, ground_truths):
            return "test"
        
        external_dataset = {
            "id": "external_dataset_123",
            "name": "Custom Dataset",
            "data": [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        }
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=external_dataset,
                run_concurrently=False
            )
            
            # Check that dataset name is added to metadata
            assert eval_instance.metadata["dataset_name"] == "Custom Dataset"
            assert eval_instance.dataset_id == "EXT-external_dataset_123"
            
    def test_evaluation_keyboard_interrupt_handling(self):
        """Test evaluation handling of keyboard interrupt."""
        def slow_function(inputs, ground_truths):
            time.sleep(0.1)  # Simulate slow function
            return "test"
        
        dataset = [
            {"inputs": {"query": f"test{i}"}, "ground_truths": {"expected": f"result{i}"}}
            for i in range(5)
        ]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=slow_function,
                dataset=dataset,
                run_concurrently=True,
                max_workers=2
            )
            
            # Mock a keyboard interrupt during execution
            with patch('honeyhive.evaluation.ThreadPoolExecutor') as mock_executor:
                mock_executor.return_value.__enter__.return_value.submit.side_effect = KeyboardInterrupt()
                
                with pytest.raises(KeyboardInterrupt):
                    eval_instance.run()


class TestEvaluationNetworkFailures:
    """Test evaluation behavior under network failure conditions."""
    
    def test_evaluation_dataset_fetch_failure(self):
        """Test evaluation when dataset fetch fails."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            # Mock dataset fetch to fail
            mock_hh.return_value.datasets.get_datasets.side_effect = Exception("Network error")
            
            with pytest.raises(RuntimeError, match="No dataset found with id"):
                Evaluation(
                    api_key="test_key",
                    project="test_project",
                    function=test_function,
                    dataset_id="nonexistent_dataset"
                )
                
    def test_evaluation_empty_dataset_from_api(self):
        """Test evaluation when API returns empty dataset."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            # Mock empty dataset response
            mock_dataset_response = Mock()
            mock_dataset_response.object.testcases = []
            mock_hh.return_value.datasets.get_datasets.return_value = mock_dataset_response
            
            with pytest.raises(RuntimeError, match="No valid testcases found"):
                Evaluation(
                    api_key="test_key",
                    project="test_project",
                    function=test_function,
                    dataset_id="empty_dataset"
                )
                
    def test_evaluation_datapoint_fetch_error(self):
        """Test evaluation when individual datapoint fetch fails."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            # Mock dataset response
            mock_dataset_response = Mock()
            mock_dataset_response.object.testcases = [Mock(datapoints=['dp1'])]
            mock_hh.return_value.datasets.get_datasets.return_value = mock_dataset_response
            
            # Mock batch fetch to fail
            mock_hh.return_value.datapoints.get_datapoints.side_effect = Exception("Batch failed")
            # Mock individual fetch to also fail
            mock_hh.return_value.datapoints.get_datapoint.side_effect = Exception("Individual failed")
            
            # Mock run methods
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset_id="test_dataset",
                run_concurrently=False
            )
            
            eval_instance.run()
            
            # Should handle failed datapoint fetch gracefully
            assert eval_instance.eval_result.data['input'][0] == {}
            assert eval_instance.eval_result.data['ground_truth'][0] == {}


class TestEvaluationConcurrencyIssues:
    """Test evaluation under various concurrency scenarios."""
    
    def test_evaluation_tracer_wrapper_concurrency_issue(self):
        """Test handling of TracerWrapper concurrency issues."""
        def test_function(inputs, ground_truths):
            return "test"
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh, \
             patch('honeyhive.evaluation.HoneyHiveTracer') as mock_tracer:
            
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            # Mock TracerWrapper concurrency issue
            mock_tracer.side_effect = Exception("TracerWrapper concurrency issue")
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                run_concurrently=False,
                verbose=True
            )
            
            eval_instance.run()
            
            # Should complete evaluation despite tracer issues
            assert eval_instance.eval_result.data['output'][0] == "test"
            
    def test_evaluation_future_timeout(self):
        """Test evaluation with future timeout in concurrent execution."""
        def slow_function(inputs, ground_truths):
            time.sleep(1)  # Simulate very slow function
            return "slow result"
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=slow_function,
                dataset=dataset,
                run_concurrently=True,
                max_workers=1
            )
            
            # Mock future.result to timeout
            with patch('concurrent.futures.Future.result', side_effect=TimeoutError("Timeout")):
                eval_instance.run()
                
                # Should handle timeout gracefully
                assert len(eval_instance.eval_result.data['output']) == 1


if __name__ == "__main__":
    pytest.main([__file__])
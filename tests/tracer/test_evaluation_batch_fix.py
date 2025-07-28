"""
Test to verify that the evaluation SDK can handle 100+ datapoints 
by using batch fetching instead of individual API calls.
"""
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from honeyhive.evaluation import Evaluation, evaluate
from honeyhive.models import components, operations


def test_batch_datapoint_fetching():
    """Test that datapoints are fetched in batch instead of individually"""
    
    # Mock the HoneyHive SDK and its methods
    with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
        # Mock the get_datasets response
        mock_dataset_response = Mock()
        mock_dataset_response.object.testcases = [
            Mock(datapoints=['dp1', 'dp2', 'dp3'])
        ]
        mock_hh.return_value.datasets.get_datasets.return_value = mock_dataset_response
        
        # Mock the batch get_datapoints response
        mock_datapoint1 = Mock()
        mock_datapoint1.id = 'dp1'
        mock_datapoint1.inputs = {'input': 'test1'}
        mock_datapoint1.ground_truth = {'expected': 'result1'}
        
        mock_datapoint2 = Mock()
        mock_datapoint2.id = 'dp2' 
        mock_datapoint2.inputs = {'input': 'test2'}
        mock_datapoint2.ground_truth = {'expected': 'result2'}
        
        mock_datapoint3 = Mock()
        mock_datapoint3.id = 'dp3'
        mock_datapoint3.inputs = {'input': 'test3'}
        mock_datapoint3.ground_truth = {'expected': 'result3'}
        
        mock_batch_response = Mock()
        mock_batch_response.object.datapoints = [
            mock_datapoint1, mock_datapoint2, mock_datapoint3
        ]
        mock_hh.return_value.datapoints.get_datapoints.return_value = mock_batch_response
        
        # Mock the experiments create_run response
        mock_run_response = Mock()
        mock_run_response.create_run_response.run_id = 'test_run_id'  
        mock_hh.return_value.experiments.create_run.return_value = mock_run_response
        
        # Mock the update_run method
        mock_hh.return_value.experiments.update_run.return_value = Mock()
        
        # Create a simple test function
        def test_function(inputs, ground_truths):
            return f"processed: {inputs.get('input', 'unknown')}"
        
        # Create evaluation instance with HoneyHive dataset
        eval_instance = Evaluation(
            api_key="test_key",
            project="test_project", 
            name="test_evaluation",
            function=test_function,
            dataset_id="test_dataset_id",
            verbose=True
        )
        
        # Verify that batch fetch was called
        mock_hh.return_value.datapoints.get_datapoints.assert_called_once_with(
            project="test_project",
            datapoint_ids=['dp1', 'dp2', 'dp3']
        )
        
        # Verify datapoints are cached
        assert 'dp1' in eval_instance.datapoint_cache
        assert 'dp2' in eval_instance.datapoint_cache  
        assert 'dp3' in eval_instance.datapoint_cache
        
        # Verify cached data is correct
        assert eval_instance.datapoint_cache['dp1'].inputs == {'input': 'test1'}
        assert eval_instance.datapoint_cache['dp1'].ground_truth == {'expected': 'result1'}
        
        # Test that _get_inputs_and_ground_truth uses cache
        inputs, ground_truth = eval_instance._get_inputs_and_ground_truth(0)
        assert inputs == {'input': 'test1'}
        assert ground_truth == {'expected': 'result1'}
        
        inputs, ground_truth = eval_instance._get_inputs_and_ground_truth(1)
        assert inputs == {'input': 'test2'}
        assert ground_truth == {'expected': 'result2'}


def test_fallback_to_individual_fetch_on_batch_failure():
    """Test that individual fetch is used as fallback when batch fetch fails"""
    
    with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
        # Mock the get_datasets response
        mock_dataset_response = Mock()
        mock_dataset_response.object.testcases = [
            Mock(datapoints=['dp1', 'dp2'])
        ]
        mock_hh.return_value.datasets.get_datasets.return_value = mock_dataset_response
        
        # Mock batch fetch to fail
        mock_hh.return_value.datapoints.get_datapoints.side_effect = Exception("Batch fetch failed")
        
        # Mock individual fetch to succeed
        mock_individual_response = Mock()
        mock_individual_response.object.datapoint = [Mock(
            inputs={'input': 'test1'},
            ground_truth={'expected': 'result1'}
        )]
        mock_hh.return_value.datapoints.get_datapoint.return_value = mock_individual_response
        
        # Mock the experiments methods
        mock_run_response = Mock()
        mock_run_response.create_run_response.run_id = 'test_run_id'
        mock_hh.return_value.experiments.create_run.return_value = mock_run_response
        mock_hh.return_value.experiments.update_run.return_value = Mock()
        
        def test_function(inputs, ground_truths):
            return f"processed: {inputs.get('input', 'unknown')}"
        
        # Create evaluation instance
        eval_instance = Evaluation(
            api_key="test_key",
            project="test_project",
            name="test_evaluation", 
            function=test_function,
            dataset_id="test_dataset_id"
        )
        
        # Verify batch fetch was attempted
        mock_hh.return_value.datapoints.get_datapoints.assert_called_once()
        
        # Verify cache is empty due to batch fetch failure
        assert len(eval_instance.datapoint_cache) == 0
        
        # Test that individual fetch is used as fallback
        inputs, ground_truth = eval_instance._get_inputs_and_ground_truth(0)
        assert inputs == {'input': 'test1'}
        assert ground_truth == {'expected': 'result1'}
        
        # Verify individual fetch was called
        mock_hh.return_value.datapoints.get_datapoint.assert_called_once_with(id='dp1')


def test_large_dataset_handling():
    """Test that the solution works with large datasets (100+ datapoints)"""
    
    with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
        # Create 150 mock datapoints
        num_datapoints = 150
        datapoint_ids = [f'dp{i}' for i in range(num_datapoints)]
        
        mock_dataset_response = Mock()
        mock_dataset_response.object.testcases = [
            Mock(datapoints=datapoint_ids)
        ]
        mock_hh.return_value.datasets.get_datasets.return_value = mock_dataset_response
        
        # Create mock datapoints for batch response
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
        
        # Mock experiments methods
        mock_run_response = Mock()
        mock_run_response.create_run_response.run_id = 'test_run_id'
        mock_hh.return_value.experiments.create_run.return_value = mock_run_response
        mock_hh.return_value.experiments.update_run.return_value = Mock()
        
        def test_function(inputs, ground_truths):
            return f"processed: {inputs.get('input', 'unknown')}"
        
        # Create evaluation instance
        eval_instance = Evaluation(
            api_key="test_key",
            project="test_project",
            name="test_evaluation",
            function=test_function,
            dataset_id="test_dataset_id",
            verbose=True
        )
        
        # Verify batch fetch was called with all datapoint IDs
        mock_hh.return_value.datapoints.get_datapoints.assert_called_once_with(
            project="test_project",
            datapoint_ids=datapoint_ids
        )
        
        # Verify all datapoints are cached
        assert len(eval_instance.datapoint_cache) == num_datapoints
        
        # Test random access to cached datapoints
        inputs, ground_truth = eval_instance._get_inputs_and_ground_truth(99)
        assert inputs == {'input': 'test99'}
        assert ground_truth == {'expected': 'result99'}
        
        inputs, ground_truth = eval_instance._get_inputs_and_ground_truth(149)
        assert inputs == {'input': 'test149'}
        assert ground_truth == {'expected': 'result149'}


if __name__ == "__main__":
    test_batch_datapoint_fetching()
    test_fallback_to_individual_fetch_on_batch_failure()
    test_large_dataset_handling()
    print("All tests passed!")
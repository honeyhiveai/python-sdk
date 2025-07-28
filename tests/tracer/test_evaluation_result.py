"""
Tests for EvaluationResult class and related functionality.
"""
import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from honeyhive.evaluation import EvaluationResult, Evaluation


class TestEvaluationResult:
    """Test EvaluationResult class functionality."""
    
    def test_evaluation_result_creation(self):
        """Test creating an EvaluationResult."""
        result = EvaluationResult(
            run_id="test_run_123",
            stats={"duration_s": 45.2, "total_tests": 10},
            dataset_id="dataset_456",
            session_ids=["session_1", "session_2"],
            status="completed",
            suite="test_suite",
            data={
                "input": [{"query": "test1"}, {"query": "test2"}],
                "output": ["response1", "response2"],
                "metrics": [{"accuracy": 0.8}, {"accuracy": 0.9}],
                "metadata": [{}, {}],
                "ground_truth": [{"expected": "resp1"}, {"expected": "resp2"}]
            }
        )
        
        assert result.run_id == "test_run_123"
        assert result.stats["duration_s"] == 45.2
        assert result.dataset_id == "dataset_456"
        assert len(result.session_ids) == 2
        assert result.status == "completed"
        assert result.suite == "test_suite"
        assert len(result.data["input"]) == 2
        
    def test_evaluation_result_to_json(self):
        """Test EvaluationResult.to_json() method."""
        data = {
            "input": [{"query": "test"}],
            "output": ["response"],
            "metrics": [{"score": 0.8}],
            "metadata": [{"meta": "data"}],
            "ground_truth": [{"expected": "resp"}]
        }
        
        result = EvaluationResult(
            run_id="test_run",
            stats={"duration_s": 10.0},
            dataset_id="dataset_123",
            session_ids=["session_1"],
            status="completed",
            suite="test_suite",
            data=data
        )
        
        # Test that to_json creates a file
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                result.to_json()
                
                # Check if file was created
                expected_file = "test_suite.json"
                assert os.path.exists(expected_file)
                
                # Check file contents
                with open(expected_file, 'r') as f:
                    saved_data = json.load(f)
                
                assert saved_data == data
                
            finally:
                os.chdir(original_cwd)


class TestEvaluationClass:
    """Test the main Evaluation class functionality."""
    
    def test_evaluation_initialization_with_dataset(self):
        """Test Evaluation initialization with dataset."""
        def test_function(inputs, ground_truths):
            return f"processed: {inputs.get('query', '')}"
        
        dataset = [
            {"inputs": {"query": "test1"}, "ground_truths": {"expected": "result1"}},
            {"inputs": {"query": "test2"}, "ground_truths": {"expected": "result2"}}
        ]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            eval_instance = Evaluation(
                api_key="test_api_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                name="test_evaluation"
            )
            
            assert eval_instance.function == test_function
            assert eval_instance.dataset == dataset
            assert eval_instance.name == "test_evaluation"
            assert eval_instance.project == "test_project"
            assert not eval_instance.use_hh_dataset
            
    def test_evaluation_initialization_with_dataset_id(self):
        """Test Evaluation initialization with dataset_id."""
        def test_function(inputs, ground_truths):
            return "test output"
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            # Mock the dataset response
            mock_dataset_response = Mock()
            mock_dataset_response.object.testcases = [
                Mock(datapoints=['dp1', 'dp2'])
            ]
            mock_hh.return_value.datasets.get_datasets.return_value = mock_dataset_response
            
            # Mock batch datapoint fetch
            mock_batch_response = Mock()
            mock_batch_response.object.datapoints = [
                Mock(id='dp1', inputs={'query': 'test1'}, ground_truth={'expected': 'result1'}),
                Mock(id='dp2', inputs={'query': 'test2'}, ground_truth={'expected': 'result2'})
            ]
            mock_hh.return_value.datapoints.get_datapoints.return_value = mock_batch_response
            
            eval_instance = Evaluation(
                api_key="test_api_key",
                project="test_project",
                function=test_function,
                dataset_id="test_dataset_id",
                name="test_evaluation"
            )
            
            assert eval_instance.dataset_id == "test_dataset_id"
            assert eval_instance.use_hh_dataset
            assert len(eval_instance.datapoint_cache) == 2
            
    def test_evaluation_requires_function(self):
        """Test that Evaluation requires a function."""
        with pytest.raises(Exception, match="Please provide a function to evaluate"):
            Evaluation(
                api_key="test_api_key",
                project="test_project",
                dataset=[{"inputs": {}, "ground_truths": {}}]
            )
            
    def test_evaluation_requires_dataset_or_dataset_id(self):
        """Test that Evaluation requires either dataset or dataset_id."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with pytest.raises(Exception, match="No valid 'dataset_id' or 'dataset' found"):
            Evaluation(
                api_key="test_api_key",
                project="test_project",
                function=test_function
            )
            
    def test_evaluation_cannot_have_both_dataset_and_dataset_id(self):
        """Test that Evaluation cannot have both dataset and dataset_id."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with pytest.raises(Exception, match="Both 'dataset_id' and 'dataset' were provided"):
            Evaluation(
                api_key="test_api_key",
                project="test_project",
                function=test_function,
                dataset=[{"inputs": {}, "ground_truths": {}}],
                dataset_id="test_dataset_id"
            )
            
    def test_evaluation_validation_requirements(self):
        """Test validation of API key and project requirements."""
        def test_function(inputs, ground_truths):
            return "test"
        
        # Test missing API key
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KeyError, match="HH_API_KEY"):
                Evaluation(
                    project="test_project",
                    function=test_function,
                    dataset=[{"inputs": {}, "ground_truths": {}}]
                )
        
        # Test missing project  
        with patch.dict(os.environ, {"HH_API_KEY": "test_key"}, clear=True):
            with pytest.raises(KeyError, match="HH_PROJECT"):
                Evaluation(
                    api_key="test_key",
                    function=test_function,
                    dataset=[{"inputs": {}, "ground_truths": {}}]
                )
                
    def test_evaluation_dataset_validation(self):
        """Test dataset format validation."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with patch('honeyhive.evaluation.HoneyHive'):
            # Non-list, non-dict datasets become None and trigger the "No valid dataset" error
            with pytest.raises(Exception, match="No valid 'dataset_id' or 'dataset' found"):
                eval_instance = Evaluation(
                    api_key="test_key",
                    project="test_project",
                    function=test_function,
                    dataset="not a list"  # Becomes None, triggers "no valid dataset" error
                )
            
            # Test dataset with non-dict items - this triggers the validation logic
            with pytest.raises(Exception, match="All items in dataset must be dictionaries"):
                eval_instance = Evaluation(
                    api_key="test_key",
                    project="test_project",
                    function=test_function,
                    dataset=["not", "dicts"]  # List with non-dict items should fail validation
                )
                
    def test_evaluation_generate_hash(self):
        """Test dataset hash generation."""
        hash1 = Evaluation.generate_hash("test_data_1")
        hash2 = Evaluation.generate_hash("test_data_2")
        hash3 = Evaluation.generate_hash("test_data_1")
        
        # Same input should generate same hash
        assert hash1 == hash3
        # Different inputs should generate different hashes
        assert hash1 != hash2
        # Should have EXT- prefix
        assert hash1.startswith("EXT-")
        assert len(hash1) == 28  # "EXT-" + 24 char hash
        
    def test_evaluation_add_ext_prefix(self):
        """Test EXT- prefix addition."""
        # Test adding prefix to string without prefix
        result1 = Evaluation._add_ext_prefix("test_id")
        assert result1 == "EXT-test_id"
        
        # Test not adding prefix when already present
        result2 = Evaluation._add_ext_prefix("EXT-test_id")
        assert result2 == "EXT-test_id"
        
        # Test with non-string input
        result3 = Evaluation._add_ext_prefix(123)
        assert result3 == "EXT-123"
        
    def test_evaluation_get_inputs_and_ground_truth_custom_dataset(self):
        """Test getting inputs and ground truth from custom dataset."""
        def test_function(inputs, ground_truths):
            return "test"
        
        dataset = [
            {"inputs": {"query": "test1"}, "ground_truths": {"expected": "result1"}},
            {"inputs": {"query": "test2"}, "ground_truths": {"expected": "result2"}}
        ]
        
        with patch('honeyhive.evaluation.HoneyHive'):
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset
            )
            
            inputs, ground_truth = eval_instance._get_inputs_and_ground_truth(0)
            assert inputs == {"query": "test1"}
            assert ground_truth == {"expected": "result1"}
            
            inputs, ground_truth = eval_instance._get_inputs_and_ground_truth(1)
            assert inputs == {"query": "test2"}
            assert ground_truth == {"expected": "result2"}
            
    def test_evaluation_run_single_datapoint(self):
        """Test running evaluation on a single datapoint."""
        def test_function(inputs, ground_truths):
            return f"processed: {inputs.get('query', 'unknown')}"
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            # Mock run creation
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                run_concurrently=False  # Test sequential execution
            )
            
            # Test running on single datapoint
            result = eval_instance.run_each(0)
            
            assert result['input'] == {"query": "test"}
            assert result['ground_truth'] == {"expected": "result"}
            assert result['output'] == "processed: test"
            assert result['metrics'] == {}
            assert result['metadata'] == {}
            
    def test_evaluation_with_evaluators(self):
        """Test evaluation with custom evaluators."""
        def test_function(inputs, ground_truths):
            return inputs.get('query', 'default')
        
        def test_evaluator(outputs, inputs, ground_truths):
            return len(outputs) if outputs else 0
        
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
                evaluators=[test_evaluator],
                run_concurrently=False
            )
            
            result = eval_instance.run_each(0)
            
            assert result['output'] == "test"
            assert 'test_evaluator' in result['metrics']
            assert result['metrics']['test_evaluator'] == 4  # len("test")
            
    def test_evaluation_async_function_error(self):
        """Test that async functions raise appropriate error."""
        async def async_function(inputs, ground_truths):
            return "async result"
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=async_function,
                dataset=dataset,
                run_concurrently=False
            )
            
            # Should detect async function and raise error
            result = eval_instance.run_each(0)
            assert result['output'] is None  # Function failed
            
    @patch('honeyhive.evaluation.HoneyHiveTracer')
    def test_evaluation_git_metadata_integration(self, mock_tracer):
        """Test that git metadata is properly integrated."""
        def test_function(inputs, ground_truths):
            return "test"
        
        # Mock git info
        mock_git_info = {
            "branch": "main",
            "commit": "abc123",
            "repo": "test-repo"
        }
        mock_tracer._get_git_info.return_value = mock_git_info
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive'):
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=dataset,
                verbose=True
            )
            
            # Check that git info was added to metadata
            assert "git" in eval_instance.metadata
            assert eval_instance.metadata["git"] == mock_git_info


if __name__ == "__main__":
    pytest.main([__file__])
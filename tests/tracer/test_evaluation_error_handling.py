"""
Tests for comprehensive error handling in the evaluation harness.
"""
import pytest
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock
from honeyhive.evaluation import Evaluation, evaluate, evaluator, EvaluationResult
from honeyhive.evaluation.evaluators import EvalSettings, EvalResult


class TestEvaluationFunctionErrors:
    """Test error handling for evaluation function failures."""
    
    def test_function_raises_exception(self):
        """Test evaluation when the main function raises an exception."""
        def failing_function(inputs, ground_truths):
            raise ValueError("Function failed!")
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=failing_function,
                dataset=dataset,
                run_concurrently=False,
                print_results=False
            )
            
            eval_instance.run()
            
            # Should handle exception gracefully
            assert eval_instance.eval_result.data['output'][0] is None
            
    def test_function_returns_invalid_type(self):
        """Test evaluation when function returns unexpected type."""
        def invalid_return_function(inputs, ground_truths):
            return {"not": "serializable", "object": object()}
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=invalid_return_function,
                dataset=dataset,
                run_concurrently=False,
                print_results=False
            )
            
            eval_instance.run()
            
            # Should handle the complex return type
            assert eval_instance.eval_result.data['output'][0] is not None
            
    def test_function_infinite_loop_timeout(self):
        """Test evaluation with function that takes too long."""
        def slow_function(inputs, ground_truths):
            import time
            time.sleep(2)  # Simulate very slow function
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
            
            # Mock timeout in concurrent execution
            with patch('concurrent.futures.Future.result') as mock_result:
                mock_result.side_effect = [Exception("Timeout")]
                
                eval_instance.run()
                
                # Should handle timeout gracefully
                assert len(eval_instance.eval_result.data['output']) == 1
                
    def test_function_memory_error(self):
        """Test evaluation when function causes memory error."""
        def memory_intensive_function(inputs, ground_truths):
            # Simulate memory error
            raise MemoryError("Out of memory!")
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=memory_intensive_function,
                dataset=dataset,
                run_concurrently=False,
                print_results=False
            )
            
            eval_instance.run()
            
            # Should handle memory error gracefully
            assert eval_instance.eval_result.data['output'][0] is None


class TestEvaluatorErrors:
    """Test error handling for evaluator-specific errors."""
    
    def test_evaluator_syntax_error(self):
        """Test evaluator with syntax error in expression."""
        @evaluator(transform="value +")  # Invalid syntax
        def syntax_error_eval(outputs, inputs, ground_truth):
            return 10
        
        with pytest.raises(SyntaxError):
            syntax_error_eval("output", {}, {})
            
    def test_evaluator_division_by_zero(self):
        """Test evaluator with division by zero."""
        @evaluator(transform="value / 0")
        def division_error_eval(outputs, inputs, ground_truth):
            return 10
        
        with pytest.raises(ZeroDivisionError):
            division_error_eval("output", {}, {})
            
    def test_evaluator_undefined_variable(self):
        """Test evaluator referencing undefined variable."""
        @evaluator(transform="value * undefined_var")
        def undefined_var_eval(outputs, inputs, ground_truth):
            return 10
        
        with pytest.raises(NameError):
            undefined_var_eval("output", {}, {})
            
    def test_evaluator_type_error(self):
        """Test evaluator with type error."""
        @evaluator(transform="value + 'string'")  # Can't add int and string
        def type_error_eval(outputs, inputs, ground_truth):
            return 10
        
        with pytest.raises(TypeError):
            type_error_eval("output", {}, {})
            
    def test_evaluator_recursive_call(self):
        """Test evaluator that calls itself recursively."""
        @evaluator(transform="recursive_eval(value, {}, {})")
        def recursive_eval(outputs, inputs, ground_truth):
            return 10
        
        # Should cause maximum recursion depth exceeded
        with pytest.raises(RecursionError):
            recursive_eval("output", {}, {})
            
    def test_evaluator_invalid_aggregate_function(self):
        """Test evaluator with invalid aggregate function."""
        @evaluator(repeat=3, aggregate="nonexistent_function(values)")
        def invalid_aggregate_eval(outputs, inputs, ground_truth):
            return 10
        
        with pytest.raises(NameError):
            invalid_aggregate_eval("output", {}, {})
            
    def test_evaluator_checker_exception(self):
        """Test evaluator where checker expression raises exception."""
        @evaluator(checker="1 / 0 < value", asserts=True)
        def checker_error_eval(outputs, inputs, ground_truth):
            return 10
        
        with pytest.raises(ZeroDivisionError):
            checker_error_eval("output", {}, {})


class TestAsyncEvaluatorErrors:
    """Test async evaluator error handling."""
    
    @pytest.mark.asyncio
    async def test_async_evaluator_exception(self):
        """Test async evaluator that raises exception."""
        @evaluator  # Note: using @evaluator for async function should cause error
        async def async_with_sync_decorator(outputs, inputs, ground_truth):
            return 10
        
        # Should raise assertion error about using wrong decorator
        with pytest.raises(AssertionError, match="please use @aevaluator"):
            async_with_sync_decorator("output", {}, {})
            
    def test_sync_evaluator_with_async_function(self):
        """Test sync evaluator decorator on async function."""
        @evaluator
        async def incorrectly_decorated_async(outputs, inputs, ground_truth):
            return 10
        
        # Should raise assertion error
        with pytest.raises(AssertionError):
            incorrectly_decorated_async("output", {}, {})


class TestNetworkAndAPIErrors:
    """Test network and API-related error handling."""
    
    def test_api_key_invalid(self):
        """Test evaluation with invalid API key."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            # Mock API error for invalid key
            mock_hh.return_value.experiments.create_run.side_effect = Exception("Invalid API key")
            
            eval_instance = Evaluation(
                api_key="invalid_key",
                project="test_project",
                function=test_function,
                dataset=[{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}],
                run_concurrently=False
            )
            
            # Should raise exception during run creation
            with pytest.raises(Exception, match="Invalid API key"):
                eval_instance.run()
                
    def test_project_not_found(self):
        """Test evaluation with non-existent project."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_hh.return_value.experiments.create_run.side_effect = Exception("Project not found")
            
            eval_instance = Evaluation(
                api_key="valid_key",
                project="nonexistent_project",
                function=test_function,
                dataset=[{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}],
                run_concurrently=False
            )
            
            with pytest.raises(Exception, match="Project not found"):
                eval_instance.run()
                
    def test_network_timeout_during_run_creation(self):
        """Test network timeout during run creation."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_hh.return_value.experiments.create_run.side_effect = TimeoutError("Network timeout")
            
            eval_instance = Evaluation(
                api_key="valid_key",
                project="test_project",
                function=test_function,
                dataset=[{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}],
                run_concurrently=False
            )
            
            with pytest.raises(TimeoutError):
                eval_instance.run()
                
    def test_rate_limit_error(self):
        """Test API rate limit handling."""
        def test_function(inputs, ground_truths):
            return "test"
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_hh.return_value.experiments.create_run.side_effect = Exception("Rate limit exceeded")
            
            eval_instance = Evaluation(
                api_key="valid_key",
                project="test_project",
                function=test_function,
                dataset=[{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}],
                run_concurrently=False
            )
            
            with pytest.raises(Exception, match="Rate limit exceeded"):
                eval_instance.run()


class TestDatasetErrors:
    """Test dataset-related error handling."""
    
    def test_corrupted_dataset_structure(self):
        """Test evaluation with corrupted dataset structure."""
        def test_function(inputs, ground_truths):
            return "test"
        
        # Create dataset with mixed valid/invalid structures
        corrupted_dataset = [
            {"inputs": {"query": "valid"}, "ground_truths": {"expected": "result"}},
            "not_a_dict",
            {"inputs": None, "ground_truths": "invalid_structure"},
            42,
            {"missing_inputs": True}
        ]
        
        with pytest.raises(Exception, match="All items in dataset must be dictionaries"):
            Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=corrupted_dataset
            )
            
    def test_dataset_with_circular_references(self):
        """Test dataset with circular references."""
        def test_function(inputs, ground_truths):
            return "test"
        
        # Create circular reference
        circular_dict = {"inputs": {"query": "test"}}
        circular_dict["self_ref"] = circular_dict
        
        with patch('honeyhive.evaluation.HoneyHive'):
            # Should handle circular reference in hash generation
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=test_function,
                dataset=[circular_dict]
            )
            # The circular reference will cause JSON serialization to fail in generate_hash
            # This tests that the error is handled appropriately
            
    def test_dataset_too_large_for_memory(self):
        """Test handling very large datasets."""
        def test_function(inputs, ground_truths):
            return "test"
        
        # Create a large dataset (simulate memory pressure)
        with patch('honeyhive.evaluation.json.dumps') as mock_dumps:
            mock_dumps.side_effect = MemoryError("Dataset too large")
            
            with patch('honeyhive.evaluation.HoneyHive'):
                with pytest.raises(MemoryError):
                    Evaluation(
                        api_key="test_key",
                        project="test_project",
                        function=test_function,
                        dataset=[{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
                    )


class TestConcurrencyErrors:
    """Test concurrency-related error handling."""
    
    def test_thread_pool_exhaustion(self):
        """Test behavior when thread pool is exhausted."""
        def slow_function(inputs, ground_truths):
            import time
            time.sleep(0.1)
            return "slow result"
        
        dataset = [
            {"inputs": {"query": f"test{i}"}, "ground_truths": {"expected": f"result{i}"}}
            for i in range(20)  # Many datapoints
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
                max_workers=2  # Very limited workers
            )
            
            # Should complete despite resource constraints
            eval_instance.run()
            assert len(eval_instance.eval_result.data['output']) == 20
            
    def test_context_variable_isolation_failure(self):
        """Test failure in context variable isolation."""
        def context_dependent_function(inputs, ground_truths):
            import contextvars
            # Try to access context that might not exist
            try:
                ctx_var = contextvars.ContextVar('test_var')
                return ctx_var.get()
            except LookupError:
                return "no_context"
        
        dataset = [{"inputs": {"query": "test"}, "ground_truths": {"expected": "result"}}]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=context_dependent_function,
                dataset=dataset,
                run_concurrently=True
            )
            
            eval_instance.run()
            # Should handle context isolation gracefully
            assert eval_instance.eval_result.data['output'][0] == "no_context"


class TestResourceExhaustionErrors:
    """Test resource exhaustion scenarios."""
    
    def test_disk_space_exhaustion(self):
        """Test behavior when disk space is exhausted."""
        def test_function(inputs, ground_truths):
            return "test"
        
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
                print_results=False
            )
            
            # Mock disk space error during result export
            with patch.object(EvaluationResult, 'to_json', side_effect=OSError("No space left on device")):
                eval_instance.run()
                
                # Should complete evaluation despite export failure
                assert eval_instance.eval_result.data['output'][0] == "test"
                
    def test_memory_pressure_during_evaluation(self):
        """Test behavior under memory pressure."""
        def memory_intensive_function(inputs, ground_truths):
            # Simulate memory allocation
            large_data = "x" * 1000  # Not actually large, but simulates the concept
            return f"processed: {large_data[:10]}"
        
        dataset = [
            {"inputs": {"query": f"test{i}"}, "ground_truths": {"expected": f"result{i}"}}
            for i in range(10)
        ]
        
        with patch('honeyhive.evaluation.HoneyHive') as mock_hh:
            mock_run_response = Mock()
            mock_run_response.create_run_response.run_id = 'test_run_id'
            mock_hh.return_value.experiments.create_run.return_value = mock_run_response
            mock_hh.return_value.experiments.update_run.return_value = Mock()
            
            eval_instance = Evaluation(
                api_key="test_key",
                project="test_project",
                function=memory_intensive_function,
                dataset=dataset,
                run_concurrently=True,
                max_workers=1  # Limit concurrency to reduce memory pressure
            )
            
            eval_instance.run()
            # Should complete successfully
            assert len(eval_instance.eval_result.data['output']) == 10


class TestSystemErrors:
    """Test system-level error handling."""
    
    def test_signal_interruption(self):
        """Test handling of system signals during evaluation."""
        def test_function(inputs, ground_truths):
            return "test"
        
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
                run_concurrently=False
            )
            
            # Mock system interrupt during execution
            with patch.object(eval_instance, 'run_each', side_effect=KeyboardInterrupt()):
                with pytest.raises(KeyboardInterrupt):
                    eval_instance.run()
                    
    def test_permission_denied_errors(self):
        """Test handling of permission denied errors."""
        def test_function(inputs, ground_truths):
            # Simulate permission error
            raise PermissionError("Access denied")
        
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
                run_concurrently=False,
                print_results=False
            )
            
            eval_instance.run()
            # Should handle permission error gracefully
            assert eval_instance.eval_result.data['output'][0] is None


if __name__ == "__main__":
    pytest.main([__file__])
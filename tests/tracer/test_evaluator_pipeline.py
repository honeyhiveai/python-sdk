"""
Tests for evaluator pipeline operations (transform, aggregate, checker, repeat).
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from honeyhive.evaluation.evaluators import evaluator, aevaluator, EvalSettings, EvalResult


class TestEvaluatorTransformation:
    """Test evaluator transformation functionality."""
    
    def test_simple_transform(self):
        """Test simple transformation operation."""
        @evaluator(transform="value * 2")
        def double_eval(outputs, inputs, ground_truth):
            return 5
        
        result = double_eval("output", {}, {})
        assert result == 10  # 5 * 2
        
    def test_complex_transform(self):
        """Test complex transformation with multiple operations."""
        @evaluator(transform="(value + 10) * 0.5")
        def complex_transform_eval(outputs, inputs, ground_truth):
            return 20
        
        result = complex_transform_eval("output", {}, {})
        assert result == 15.0  # (20 + 10) * 0.5
        
    def test_transform_with_result_access(self):
        """Test transformation that accesses the result object."""
        @evaluator(transform="value + len(result.metadata)")
        def metadata_transform_eval(outputs, inputs, ground_truth):
            return 10
        
        result = metadata_transform_eval("output", {}, {})
        # Should access the result's metadata length
        assert isinstance(result, (int, float))
        
    def test_no_transform(self):
        """Test evaluator without transformation."""
        @evaluator
        def no_transform_eval(outputs, inputs, ground_truth):
            return 42
        
        result = no_transform_eval("output", {}, {})
        assert result == 42  # No transformation applied
        
    def test_transform_error_handling(self):
        """Test transformation with invalid expression."""
        @evaluator(transform="invalid_function(value)")
        def invalid_transform_eval(outputs, inputs, ground_truth):
            return 10
        
        # Should raise error for invalid transform
        with pytest.raises(NameError):
            invalid_transform_eval("output", {}, {})


class TestEvaluatorAggregation:
    """Test evaluator aggregation functionality."""
    
    def test_mean_aggregation(self):
        """Test mean aggregation."""
        @evaluator(repeat=3, aggregate="mean(values)")
        def mean_eval(outputs, inputs, ground_truth):
            return 10  # Will be called 3 times
        
        result = mean_eval("output", {}, {})
        assert result == 10.0  # mean([10, 10, 10])
        
    def test_sum_aggregation(self):
        """Test sum aggregation."""
        call_count = 0
        
        @evaluator(repeat=3, aggregate="sum(values)")
        def sum_eval(outputs, inputs, ground_truth):
            nonlocal call_count
            call_count += 1
            return call_count
        
        result = sum_eval("output", {}, {})
        assert result == 6  # sum([1, 2, 3])
        
    def test_max_aggregation(self):
        """Test max aggregation."""
        values = [1, 5, 3]
        call_index = 0
        
        @evaluator(repeat=3, aggregate="max(values)")
        def max_eval(outputs, inputs, ground_truth):
            nonlocal call_index
            result = values[call_index]
            call_index += 1
            return result
        
        result = max_eval("output", {}, {})
        assert result == 5  # max([1, 5, 3])
        
    def test_min_aggregation(self):
        """Test min aggregation."""
        values = [7, 2, 9]
        call_index = 0
        
        @evaluator(repeat=3, aggregate="min(values)")
        def min_eval(outputs, inputs, ground_truth):
            nonlocal call_index
            result = values[call_index]
            call_index += 1
            return result
        
        result = min_eval("output", {}, {})
        assert result == 2  # min([7, 2, 9])
        
    def test_custom_aggregation_with_builtin(self):
        """Test custom aggregation using built-in evaluators."""
        @evaluator(repeat=4, aggregate="median(values)")
        def median_eval(outputs, inputs, ground_truth):
            return len(outputs)  # Return length of output
        
        result = median_eval("test", {}, {})
        assert result == 4  # median([4, 4, 4, 4]) using built-in median
        
    def test_no_aggregation_with_repeat(self):
        """Test repeat without aggregation returns tuple."""
        @evaluator(repeat=2)
        def no_aggregate_eval(outputs, inputs, ground_truth):
            return 42
        
        result = no_aggregate_eval("output", {}, {})
        # Without aggregation, should return the transformed result directly
        assert result == 42
        
    def test_aggregation_error_handling(self):
        """Test aggregation with invalid expression."""
        @evaluator(repeat=2, aggregate="invalid_function(values)")
        def invalid_aggregate_eval(outputs, inputs, ground_truth):
            return 10
        
        with pytest.raises(NameError):
            invalid_aggregate_eval("output", {}, {})


class TestEvaluatorChecker:
    """Test evaluator checker functionality."""
    
    def test_simple_checker_pass(self):
        """Test simple checker that passes."""
        @evaluator(checker="value > 5")
        def pass_checker_eval(outputs, inputs, ground_truth):
            return 10
        
        result = pass_checker_eval("output", {}, {})
        assert result == 10
        
    def test_simple_checker_fail(self):
        """Test simple checker that fails."""
        @evaluator(checker="value > 15")
        def fail_checker_eval(outputs, inputs, ground_truth):
            return 10
        
        result = fail_checker_eval("output", {}, {})
        assert result == 10  # Checker doesn't affect return value unless asserts=True
        
    def test_checker_with_target(self):
        """Test checker with target value."""
        @evaluator(checker="value >= target", target=8)
        def target_checker_eval(outputs, inputs, ground_truth):
            return 10
        
        result = target_checker_eval("output", {}, {})
        assert result == 10
        
    def test_checker_with_assertions_pass(self):
        """Test checker with assertions that pass."""
        @evaluator(checker="value >= target", target=5, asserts=True)
        def assert_pass_eval(outputs, inputs, ground_truth):
            return 10
        
        result = assert_pass_eval("output", {}, {})
        assert result == 10
        
    def test_checker_with_assertions_fail(self):
        """Test checker with assertions that fail."""
        @evaluator(checker="value >= target", target=15, asserts=True)
        def assert_fail_eval(outputs, inputs, ground_truth):
            return 10
        
        with pytest.raises(AssertionError):
            assert_fail_eval("output", {}, {})
            
    def test_assertions_without_checker(self):
        """Test assertions without explicit checker."""
        @evaluator(asserts=True)
        def simple_assert_eval(outputs, inputs, ground_truth):
            return True  # Truthy value should pass
        
        result = simple_assert_eval("output", {}, {})
        assert result == True
        
    def test_assertions_without_checker_fail(self):
        """Test assertions without explicit checker that fail."""
        @evaluator(asserts=True)
        def simple_assert_fail_eval(outputs, inputs, ground_truth):
            return False  # Falsy value should fail
        
        with pytest.raises(AssertionError):
            simple_assert_fail_eval("output", {}, {})
            
    def test_complex_checker_expression(self):
        """Test complex checker expression."""
        @evaluator(checker="0.5 <= value <= 1.0")
        def range_checker_eval(outputs, inputs, ground_truth):
            return 0.8
        
        result = range_checker_eval("output", {}, {})
        assert result == 0.8
        
    def test_checker_with_result_access(self):
        """Test checker that accesses the result object."""
        @evaluator(checker="len(result.metadata) == 0")
        def result_checker_eval(outputs, inputs, ground_truth):
            return 1.0
        
        result = result_checker_eval("output", {}, {})
        assert result == 1.0


class TestEvaluatorRepeat:
    """Test evaluator repeat functionality."""
    
    def test_basic_repeat(self):
        """Test basic repeat functionality."""
        call_count = 0
        
        @evaluator(repeat=3)
        def repeat_eval(outputs, inputs, ground_truth):
            nonlocal call_count
            call_count += 1
            return call_count
        
        result = repeat_eval("output", {}, {})
        # Without aggregation, returns the last result
        assert call_count == 3
        
    def test_repeat_with_random_values(self):
        """Test repeat with different values each time."""
        import random
        
        @evaluator(repeat=5, aggregate="mean(values)")
        def random_eval(outputs, inputs, ground_truth):
            return random.uniform(0, 1)
        
        # Mock random to return predictable sequence
        with patch('random.uniform', side_effect=[0.1, 0.2, 0.3, 0.4, 0.5]):
            result = random_eval("output", {}, {})
            assert result == 0.3  # mean([0.1, 0.2, 0.3, 0.4, 0.5])
            
    def test_repeat_zero(self):
        """Test with repeat=0 or no repeat."""
        @evaluator  # No repeat specified
        def no_repeat_eval(outputs, inputs, ground_truth):
            return 42
        
        result = no_repeat_eval("output", {}, {})
        assert result == 42
        
    def test_repeat_one(self):
        """Test with repeat=1."""
        @evaluator(repeat=1)
        def repeat_one_eval(outputs, inputs, ground_truth):
            return 100
        
        result = repeat_one_eval("output", {}, {})
        assert result == 100
        
    def test_large_repeat_count(self):
        """Test with large repeat count."""
        @evaluator(repeat=100, aggregate="len(values)")
        def large_repeat_eval(outputs, inputs, ground_truth):
            return 1
        
        result = large_repeat_eval("output", {}, {})
        assert result == 100  # len([1, 1, 1, ...]) = 100


class TestComplexPipelines:
    """Test complex evaluator pipelines with multiple operations."""
    
    def test_full_pipeline(self):
        """Test evaluator with all pipeline operations."""
        call_count = 0
        
        @evaluator(
            repeat=3,
            transform="value * 10",
            aggregate="mean(values)", 
            checker="value >= target",
            target=50,
            asserts=True
        )
        def full_pipeline_eval(outputs, inputs, ground_truth):
            nonlocal call_count
            call_count += 1
            return call_count + 4  # Returns 5, 6, 7
        
        result = full_pipeline_eval("output", {}, {})
        # (5+6+7)/3 * 10 = 6 * 10 = 60, which should pass target >= 50
        assert result == 60.0
        
    def test_pipeline_with_failing_checker(self):
        """Test pipeline where checker fails."""
        @evaluator(
            repeat=2,
            transform="value * 0.1",
            aggregate="mean(values)",
            checker="value >= target",
            target=10,
            asserts=True
        )
        def failing_pipeline_eval(outputs, inputs, ground_truth):
            return 50  # 50 * 0.1 = 5, mean([5, 5]) = 5, but target is 10
        
        with pytest.raises(AssertionError):
            failing_pipeline_eval("output", {}, {})
            
    def test_pipeline_order_dependency(self):
        """Test that pipeline operations execute in correct order."""
        @evaluator(
            repeat=2,
            transform="value + 1",  # First: add 1 to each repeat result
            aggregate="sum(values)",  # Then: sum the transformed values
            checker="value == target",  # Finally: check the aggregated result
            target=12,  # 2 calls returning 5 each: (5+1) + (5+1) = 12
            asserts=True
        )
        def order_test_eval(outputs, inputs, ground_truth):
            return 5
        
        result = order_test_eval("output", {}, {})
        assert result == 12
        
    def test_nested_evaluator_calls(self):
        """Test pipeline with nested evaluator calls in expressions."""
        @evaluator
        def helper_eval(outputs, inputs, ground_truth):
            return len(outputs)
        
        @evaluator(transform="helper_eval(value, {}, {}) * 2")
        def nested_eval(outputs, inputs, ground_truth):
            return "test"  # len("test") = 4, so 4 * 2 = 8
        
        result = nested_eval("output", {}, {})
        assert result == 8
        
    def test_pipeline_with_conditional_logic(self):
        """Test pipeline with conditional expressions."""
        @evaluator(
            repeat=3,
            aggregate="max(values) if len(values) > 2 else sum(values)"
        )
        def conditional_eval(outputs, inputs, ground_truth):
            return len(outputs)
        
        result = conditional_eval("output", {}, {})
        # 3 calls with "output" (len=6), condition is true, so max([6,6,6]) = 6
        assert result == 6


class TestAsyncEvaluatorPipelines:
    """Test async evaluator pipeline operations."""
    
    @pytest.mark.asyncio
    async def test_async_evaluator_basic_pipeline(self):
        """Test basic async evaluator pipeline."""
        @aevaluator(transform="value * 2")
        async def async_transform_eval(outputs, inputs, ground_truth):
            await asyncio.sleep(0.001)
            return 15
        
        result = await async_transform_eval("output", {}, {})
        assert result == 30  # 15 * 2
        
    @pytest.mark.asyncio 
    async def test_async_evaluator_with_repeat_and_aggregate(self):
        """Test async evaluator with repeat and aggregation."""
        call_count = 0
        
        @aevaluator(repeat=3, aggregate="sum(values)")
        async def async_repeat_eval(outputs, inputs, ground_truth):
            nonlocal call_count
            await asyncio.sleep(0.001)
            call_count += 1
            return call_count
        
        result = await async_repeat_eval("output", {}, {})
        assert result == 6  # sum([1, 2, 3])
        
    @pytest.mark.asyncio
    async def test_async_evaluator_complex_pipeline(self):
        """Test complex async evaluator pipeline."""
        @aevaluator(
            repeat=2,
            transform="value + 5",
            aggregate="mean(values)",
            checker="value >= target",
            target=10
        )
        async def async_complex_eval(outputs, inputs, ground_truth):
            await asyncio.sleep(0.001)
            return 7  # (7+5) + (7+5) = 24, mean = 12, passes target >= 10
        
        result = await async_complex_eval("output", {}, {})
        assert result == 12.0


class TestEvaluatorSettings:
    """Test evaluator settings and configuration in pipelines."""
    
    def test_weight_setting(self):
        """Test weight setting in evaluator."""
        @evaluator(weight=2.5)
        def weighted_eval(outputs, inputs, ground_truth):
            return 0.8
        
        settings = weighted_eval.settings
        assert settings.weight == 2.5
        
    def test_pipeline_settings_inheritance(self):
        """Test that pipeline settings are properly inherited."""
        @evaluator(
            repeat=3,
            transform="value * 2", 
            aggregate="mean(values)",
            weight=1.5,
            asserts=True
        )
        def settings_eval(outputs, inputs, ground_truth):
            return 10
        
        settings = settings_eval.settings
        assert settings.repeat == 3
        assert settings.transform == "value * 2"
        assert settings.aggregate == "mean(values)"
        assert settings.weight == 1.5
        assert settings.asserts == True
        
    def test_runtime_settings_override(self):
        """Test overriding settings at runtime."""
        @evaluator(weight=1.0)
        def override_eval(outputs, inputs, ground_truth):
            return 0.9
        
        # Test calling with runtime settings
        result = override_eval("output", {}, {}, weight=2.0)
        assert result == 0.9  # Settings override doesn't affect return value directly


if __name__ == "__main__":
    pytest.main([__file__])
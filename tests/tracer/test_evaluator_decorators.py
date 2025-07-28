"""
Tests for evaluator and aevaluator decorators.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from honeyhive.evaluation.evaluators import evaluator, aevaluator, EvalSettings, EvalResult


class TestEvaluatorDecorator:
    """Test the @evaluator decorator functionality."""
    
    def test_basic_evaluator_decoration(self):
        """Test that @evaluator properly decorates a function."""
        @evaluator
        def test_eval(outputs, inputs, ground_truth):
            return 0.8
        
        assert isinstance(test_eval, evaluator)
        assert test_eval.name == "test_eval"
        assert test_eval in evaluator.all_evaluators.values()
        
    def test_evaluator_with_settings(self):
        """Test evaluator with custom settings."""
        @evaluator(weight=2.0, asserts=True)
        def weighted_eval(outputs, inputs, ground_truth):
            return 0.9
        
        settings = weighted_eval.settings
        assert settings.weight == 2.0
        assert settings.asserts == True
        
    def test_evaluator_call(self):
        """Test calling an evaluator."""
        @evaluator
        def simple_eval(outputs, inputs, ground_truth):
            return len(outputs) if outputs else 0
        
        result = simple_eval("test output", {"input": "test"}, {"expected": "test"})
        assert result == 11  # len("test output")
        
    def test_evaluator_registration(self):
        """Test that evaluators are registered correctly."""
        @evaluator
        def registered_eval(outputs, inputs, ground_truth):
            return 1.0
        
        # Should be accessible via class indexing
        retrieved = evaluator["registered_eval"]
        assert retrieved is registered_eval
        
    def test_evaluator_with_transform(self):
        """Test evaluator with transform setting."""
        @evaluator(transform="value * 2")
        def transform_eval(outputs, inputs, ground_truth):
            return 0.5
        
        result = transform_eval("output", {}, {})
        assert result == 1.0  # 0.5 * 2
        
    def test_evaluator_with_repeat(self):
        """Test evaluator with repeat setting."""
        call_count = 0
        
        @evaluator(repeat=3, aggregate="mean(values)")
        def repeat_eval(outputs, inputs, ground_truth):
            nonlocal call_count
            call_count += 1
            return call_count
        
        result = repeat_eval("output", {}, {})
        assert result == 2.0  # mean([1, 2, 3]) = 2.0
        
    def test_evaluator_with_checker_and_target(self):
        """Test evaluator with checker and target."""
        @evaluator(checker="value >= target", target=0.8)
        def checked_eval(outputs, inputs, ground_truth):
            return 0.9
        
        result = checked_eval("output", {}, {})
        # With checker, the result is the boolean result of the check
        assert result == True
        
    def test_evaluator_assertion_failure(self):
        """Test evaluator assertion failure."""
        @evaluator(checker="value >= target", target=0.8, asserts=True)
        def failing_eval(outputs, inputs, ground_truth):
            return 0.5
        
        with pytest.raises(AssertionError):
            failing_eval("output", {}, {})


class TestAsyncEvaluator:
    """Test the @aevaluator decorator functionality."""
    
    def test_basic_aevaluator_decoration(self):
        """Test that @aevaluator properly decorates an async function."""
        @aevaluator
        async def async_eval(outputs, inputs, ground_truth):
            return 0.8
        
        assert isinstance(async_eval, aevaluator)
        assert async_eval.name == "async_eval"
        
    @pytest.mark.asyncio(scope="function")
    async def test_aevaluator_call(self):
        """Test calling an async evaluator."""
        @aevaluator
        async def async_simple_eval(outputs, inputs, ground_truth):
            await asyncio.sleep(0.001)  # Simulate async work
            return len(outputs) if outputs else 0
        
        result = await async_simple_eval("test", {}, {})
        assert result == 4


class TestEvaluatorSettings:
    """Test evaluator settings and configuration."""
    
    def test_eval_settings_creation(self):
        """Test EvalSettings creation and defaults."""
        settings = EvalSettings(name="test")
        assert settings.name == "test"
        assert settings.weight is None
        assert settings.asserts is None
        
    def test_eval_settings_update(self):
        """Test updating EvalSettings."""
        settings = EvalSettings(name="test")
        settings.update({"weight": 2.0, "asserts": True})
        
        assert settings.weight == 2.0
        assert settings.asserts == True
        
    def test_eval_settings_invalid_field(self):
        """Test updating with invalid field raises error."""
        settings = EvalSettings(name="test")
        
        with pytest.raises(ValueError, match="Invalid field name"):
            settings.update({"invalid_field": "value"})
            
    def test_extract_eval_settings_and_kwargs(self):
        """Test extracting eval settings from mixed kwargs."""
        mixed_kwargs = {
            "weight": 2.0,
            "asserts": True,
            "custom_param": "value",
            "another_param": 123
        }
        
        eval_settings, eval_kwargs = EvalSettings.extract_eval_settings_and_kwargs(mixed_kwargs)
        
        assert eval_settings == {"weight": 2.0, "asserts": True}
        assert eval_kwargs == {"custom_param": "value", "another_param": 123}


class TestEvalResult:
    """Test EvalResult functionality."""
    
    def test_eval_result_creation(self):
        """Test creating an EvalResult."""
        result = EvalResult(score=0.8, test_meta="test_value")
        
        assert result.score == 0.8
        assert result.metadata["test_meta"] == "test_value"
        
    def test_eval_result_to_dict(self):
        """Test converting EvalResult to dictionary."""
        result = EvalResult(score=0.9, custom_field="custom_value")
        result_dict = result.to_dict()
        
        expected = {
            "score": 0.9,
            "metadata": {"custom_field": "custom_value"}
        }
        assert result_dict == expected
        
    def test_eval_result_copy(self):
        """Test copying an EvalResult."""
        original = EvalResult(score=0.7, meta_field="meta_value")
        copy = original.copy()
        
        assert copy.score == original.score
        assert copy.metadata == original.metadata
        assert copy is not original


class TestEvaluatorWrapping:
    """Test evaluator wrapping functionality."""
    
    def test_parse_wraps_string(self):
        """Test parsing wrap settings with string."""
        wraps_name, wraps_kwargs = evaluator.parse_wraps("base_evaluator")
        
        assert wraps_name == "base_evaluator"
        assert wraps_kwargs == {}
        
    def test_parse_wraps_dict(self):
        """Test parsing wrap settings with dictionary."""
        wraps_config = {"base_evaluator": {"weight": 2.0, "custom_param": "value"}}
        wraps_name, wraps_kwargs = evaluator.parse_wraps(wraps_config)
        
        assert wraps_name == "base_evaluator"
        assert wraps_kwargs == {"weight": 2.0, "custom_param": "value"}
        
    def test_parse_wraps_none(self):
        """Test parsing wrap settings with None."""
        wraps_name, wraps_kwargs = evaluator.parse_wraps(None)
        
        assert wraps_name is None
        assert wraps_kwargs == {}
        
    def test_parse_wraps_invalid(self):
        """Test parsing wrap settings with invalid input."""
        with pytest.raises(ValueError, match="Invalid wraps type"):
            evaluator.parse_wraps(123)


class TestBuiltinEvaluators:
    """Test built-in evaluators like mean, median, mode."""
    
    def test_mean_evaluator(self):
        """Test the built-in mean evaluator."""
        mean_eval = evaluator["mean"]
        # Built-in evaluators expect scores as first argument only
        result = mean_eval([1, 2, 3, 4, 5])
        assert result == 3.0
        
    def test_median_evaluator(self):
        """Test the built-in median evaluator."""
        median_eval = evaluator["median"]
        # Built-in evaluators expect scores as first argument only
        result = median_eval([1, 2, 3, 4, 5])
        assert result == 3
        
    def test_mode_evaluator(self):
        """Test the built-in mode evaluator."""
        mode_eval = evaluator["mode"]
        # Built-in evaluators expect scores as first argument only
        result = mode_eval([1, 2, 2, 3, 2])
        assert result == 2


class TestEvaluatorPipeline:
    """Test complex evaluator pipeline operations."""
    
    def test_complex_pipeline(self):
        """Test evaluator with multiple pipeline operations."""
        @evaluator(
            repeat=3,
            transform="value * 10",
            aggregate="mean(values)",
            checker="value >= target",
            target=80.0
        )
        def complex_eval(outputs, inputs, ground_truth):
            return 9.0  # Will become 90 after transform
        
        result = complex_eval("output", {}, {})
        # With checker, the result is the boolean result of the check
        assert result == True  # 90.0 >= 80.0
        
    def test_pipeline_with_custom_aggregate(self):
        """Test pipeline with custom aggregation function."""
        @evaluator(repeat=2, aggregate="max(values)")
        def max_aggregate_eval(outputs, inputs, ground_truth):
            import random
            return random.choice([0.7, 0.9])
        
        # Mock random to ensure deterministic behavior
        with patch('random.choice', side_effect=[0.7, 0.9]):
            result = max_aggregate_eval("output", {}, {})
            assert result == 0.9


if __name__ == "__main__":
    pytest.main([__file__])
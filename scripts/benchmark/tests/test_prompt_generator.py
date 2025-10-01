"""
Unit tests for prompt generator module.

Tests the PromptGenerator class for deterministic prompt generation.
"""

import pytest
from ..scenarios.prompt_generator import PromptGenerator


class TestPromptGenerator:
    """Test cases for PromptGenerator class."""
    
    def test_initialization_default_seed(self):
        """Test PromptGenerator initialization with default seed."""
        generator = PromptGenerator()
        assert generator.base_seed == 12345
        assert generator.templates is not None
    
    def test_initialization_custom_seed(self):
        """Test PromptGenerator initialization with custom seed."""
        generator = PromptGenerator(seed=123)
        assert generator.base_seed == 123
        assert generator.templates is not None
    
    def test_deterministic_generation(self):
        """Test that prompt generation is deterministic with same seed."""
        generator1 = PromptGenerator(seed=42)
        generator2 = PromptGenerator(seed=42)
        
        # Generate prompts with same operation_id
        prompt1, scenario1 = generator1.generate_prompt(1001, "mixed")
        prompt2, scenario2 = generator2.generate_prompt(1001, "mixed")
        
        # Should be identical
        assert prompt1 == prompt2
        assert scenario1 == scenario2
    
    def test_different_seeds_different_prompts(self):
        """Test that different seeds produce different prompts."""
        generator1 = PromptGenerator(seed=42)
        generator2 = PromptGenerator(seed=123)
        
        # Generate multiple prompts to increase probability of difference
        results1 = []
        results2 = []
        for i in range(10):
            prompt1, scenario1 = generator1.generate_prompt(1000 + i, "mixed")
            prompt2, scenario2 = generator2.generate_prompt(1000 + i, "mixed")
            results1.append(prompt1)
            results2.append(prompt2)
        
        # At least some should be different (very high probability)
        assert results1 != results2
    
    def test_different_operation_ids_different_prompts(self):
        """Test that different operation IDs produce different prompts."""
        generator = PromptGenerator(seed=42)
        
        prompt1, scenario1 = generator.generate_prompt(1001, "mixed")
        prompt2, scenario2 = generator.generate_prompt(1002, "mixed")
        
        # Should be different
        assert (prompt1, scenario1) != (prompt2, scenario2)
    
    def test_span_size_modes(self):
        """Test prompt generation for different span size modes."""
        generator = PromptGenerator(seed=42)
        
        valid_modes = ["small", "medium", "large", "mixed"]
        
        for mode in valid_modes:
            prompt, scenario = generator.generate_prompt(1001, mode)
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert scenario is not None
    
    def test_invalid_span_size_mode(self):
        """Test that invalid span size mode logs warning but works."""
        generator = PromptGenerator(seed=42)
        
        # Should work but log a warning
        prompt, scenario = generator.generate_prompt(1001, "invalid")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert scenario is not None
    
    def test_prompt_structure(self):
        """Test that generated prompts have expected structure."""
        generator = PromptGenerator(seed=42)
        
        prompt, scenario = generator.generate_prompt(1001, "medium")
        
        # Should be a non-empty string
        assert isinstance(prompt, str)
        assert len(prompt) > 10  # Should be substantial
        
        # Should contain some conversational elements
        # (This is a basic check - actual content will vary)
        assert len(prompt.split()) > 5  # At least 5 words
        
        # Scenario should be valid
        assert scenario is not None
    
    def test_reproducibility_across_calls(self):
        """Test that the same generator produces consistent results."""
        generator = PromptGenerator(seed=42)
        
        # Generate the same prompt multiple times
        results = []
        for _ in range(5):
            # Reset generator to same state
            generator = PromptGenerator(seed=42)
            result = generator.generate_prompt(1001, "medium")
            results.append(result)
        
        # All results should be identical
        assert all(result == results[0] for result in results)
    
    def test_operation_id_range(self):
        """Test prompt generation with various operation ID ranges."""
        generator = PromptGenerator(seed=42)
        
        # Test different operation ID ranges
        operation_ids = [1, 100, 1000, 9999, 10000]
        
        prompts = []
        for op_id in operation_ids:
            prompt, scenario = generator.generate_prompt(op_id, "medium")
            prompts.append(prompt)
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert scenario is not None
        
        # All prompts should be different (compare just the strings)
        assert len(set(prompts)) == len(prompts)
    
    def test_span_size_consistency(self):
        """Test that span size modes produce appropriately sized content."""
        generator = PromptGenerator(seed=42)
        
        # Generate prompts for different sizes
        small_prompt, small_scenario = generator.generate_prompt(1001, "small")
        medium_prompt, medium_scenario = generator.generate_prompt(1002, "medium") 
        large_prompt, large_scenario = generator.generate_prompt(1003, "large")
        
        # Basic length checks (these are rough estimates)
        small_words = len(small_prompt.split())
        medium_words = len(medium_prompt.split())
        large_words = len(large_prompt.split())
        
        # Small should be shorter than large (medium can vary)
        # (This is probabilistic but should generally hold)
        assert small_words < large_words
        
        # All should have reasonable minimum length
        assert small_words >= 5
        assert medium_words >= 5
        assert large_words >= 10
        
        # Scenarios should match expected sizes
        assert small_scenario is not None
        assert medium_scenario is not None
        assert large_scenario is not None
    
    def test_mixed_mode_variety(self):
        """Test that mixed mode produces variety in prompt sizes."""
        generator = PromptGenerator(seed=42)
        
        # Generate multiple mixed prompts
        prompts = []
        scenario_descriptions = []
        for i in range(20):
            prompt, scenario = generator.generate_prompt(1000 + i, "mixed")
            prompts.append(prompt)
            scenario_descriptions.append(scenario.description)
        
        # Check that we get variety in lengths
        lengths = [len(prompt.split()) for prompt in prompts]
        
        # Should have some variation in lengths
        assert min(lengths) < max(lengths)
        assert len(set(lengths)) > 1  # At least 2 different lengths
        
        # Should have variety in scenario descriptions (hashable)
        assert len(set(scenario_descriptions)) > 1  # At least 2 different scenarios
